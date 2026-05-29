import uuid
import datetime
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.fetcher import safe_fetch_pipeline
from app.services.parser import process_guarded_inference
from app.services.replay_snapshot import get_latest_snapshot, save_new_snapshot
from app.services.engine import extract_semantic_intelligence, generate_semantic_diff, compute_dual_scores
from app.services.event_router import event_router
from app.services.event_stream import event_bus
from app.services.registry import TargetRegistryService
from app.services.correlator import market_correlator
from app.config.settings import settings

from app.distributed.scheduler import cognitive_scheduler
from app.distributed.node_registry import node_registry

class ContinuousWatcher:
    def __init__(self):
        self.watch_cycle_count = 0

    async def _emit(self, state: str, competitor: str, message: str, extra: dict = None):
        payload = {
            "state": state,
            "competitor": competitor,
            "message": message,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        if extra:
            payload.update(extra)
        await event_bus.publish("watcher_feed", payload)

    async def watch_target(self, competitor: str, app_state):
        cycle_id = str(uuid.uuid4())[:8]
        self.watch_cycle_count += 1

        await self._emit(settings.STATE_ACTIVE, competitor, f"Initiating Cycle {self.watch_cycle_count}...", {
            "watch_cycle_id": cycle_id
        })

        # 1. Fetch
        browser = app_state.browser if hasattr(app_state, 'browser') else None
        target_dict = await TargetRegistryService.get_all_active_targets()
        target_metadata = target_dict.get(competitor, {})
        url = target_metadata.get("url", f"https://www.{competitor.lower()}.com/pricing")
        fetch_result = await safe_fetch_pipeline(competitor, url, browser)
        
        if fetch_result["mode"] == "FALLBACK":
            await self._emit(settings.STATE_DEGRADED, competitor, "Upstream degradation. Recovery pipeline active.")
            return

        content = fetch_result["markdown_content"]
        
        # 2. Validate DOM
        await self._emit(settings.STATE_ACTIVE, competitor, "DOM structural validation in progress.")
        historical_snapshot = await get_latest_snapshot(competitor)
        bypassed, current_hash, parser_telemetry = process_guarded_inference(content, historical_snapshot or {})
        
        hist_hash = historical_snapshot.get("dom_hash") if historical_snapshot else None
        
        if hist_hash and current_hash == hist_hash:
            # Heartbeat Event: No Delta
            await self._emit(settings.STATE_STABLE, competitor, "DOM Stability: 100%. No strategic delta detected.", {
                "watch_cycle_id": cycle_id,
                "dom_stability": 100
            })
            return

        # 3. Delta Detected -> Check Cooldown
        if event_router.is_in_cooldown(competitor, current_hash):
            await self._emit(settings.STATE_STABLE, competitor, "Signal previously escalated. Cooldown active.", {
                "watch_cycle_id": cycle_id,
                "cooldown_active": True
            })
            return

        # 4. Diffing (Selective Activation)
        await self._emit(settings.STATE_ACTIVE, competitor, "Structural delta detected. Activating deterministic semantic extraction.")
        raw_html = fetch_result.get("raw_html", "")
        current_extracted, inf_telemetry = await extract_semantic_intelligence(content, raw_html)
        
        # 4.5 Semantic Drift Detection
        if inf_telemetry.get("structural_confidence", 100) < settings.INTEGRITY_DRIFT_THRESHOLD:
             await self._emit(settings.STATE_DEGRADED, competitor, "SEMANTIC DRIFT DETECTED: Deterministic structure collapsed. Routing anomaly to AI.")

        hist_extracted = historical_snapshot.get("scraped_data", {}) if historical_snapshot else {}
        
        diff_data = generate_semantic_diff(current_extracted, hist_extracted)
        scores = compute_dual_scores(diff_data)
        
        # 5. Escalation Routing
        severity = event_router.evaluate_signal(scores)
        if event_router.should_escalate(scores):
            event_id = f"evt_{uuid.uuid4().hex[:8]}"
            event_router.register_escalation(competitor, current_hash)
            
            # Predict snapshot version
            snapshot_ver = (historical_snapshot.get("snapshot_version", 0) if historical_snapshot else 0) + 1
            
            # Emit Escalate event
            if "routing_event" in inf_telemetry:
                await self._emit(settings.STATE_DEGRADED, competitor, inf_telemetry["routing_event"])
                
            await self._emit(settings.STATE_ESCALATING, competitor, f"[{severity}] Signal escalation threshold breached.", {
                "event_id": event_id,
                "watch_cycle_id": cycle_id,
                "snapshot_version": snapshot_ver,
                "severity": severity,
                "scores": scores,
                "diff": diff_data,
                "escalation_threshold": "75%",
                "inference_telemetry": inf_telemetry,
                "target_metadata": target_metadata
            })
            
            # Send to Correlator
            await market_correlator.process_escalation(competitor, target_metadata, scores, diff_data)
            
            # Save lineage
            parent_id = historical_snapshot.get("id") if historical_snapshot else None
            await save_new_snapshot(
                competitor=competitor,
                url=url,
                dom_hash=current_hash,
                scraped_data=current_extracted,
                parent_id=parent_id,
                telemetry={"mode": "LIVE", "snapshot_status": "LIVE", "integrity_score": 98, "severity": severity, "event_id": event_id}
            )
        else:
            await self._emit(settings.STATE_STABLE, competitor, f"[{severity}] Delta below escalation threshold. Ignored.", {
                "watch_cycle_id": cycle_id
            })

    async def start(self, app_state):
        self.app_state = app_state
        # Schedule the reconciliation loop every 15 seconds
        cognitive_scheduler.scheduler.add_job(
            self.reconcile_scheduler,
            'interval',
            seconds=15,
            id="scheduler_reconciliation_loop"
        )
        # Schedule the decay engine sweep
        from app.memory.decay import decay_engine
        cognitive_scheduler.scheduler.add_job(
            decay_engine.run_decay_sweep,
            'interval',
            seconds=300, # 5 minutes
            id="memory_decay_sweep"
        )
        cognitive_scheduler.start()
        # Run first reconciliation immediately
        await self.reconcile_scheduler()

    async def reconcile_scheduler(self):
        targets = await TargetRegistryService.get_all_active_targets()
        
        # Register logical nodes per sector
        sectors = {}
        for target_name, metadata in targets.items():
            s = metadata.get("sector", "Unknown")
            if s not in sectors:
                sectors[s] = []
            sectors[s].append(target_name)
            
        for sector, tgts in sectors.items():
            node_registry.register_node(f"NODE_{sector.upper().replace(' ', '_')}", tgts)
            
        # Get active jobs
        active_jobs = [j.id for j in cognitive_scheduler.scheduler.get_jobs()]
        
        stagger_delay = 0
        for target_name, metadata in targets.items():
            job_id = f"watch_{target_name}"
            if job_id not in active_jobs:
                sector = metadata.get("sector", "Unknown")
                start_date = datetime.datetime.now() + datetime.timedelta(seconds=stagger_delay)
                cognitive_scheduler.scheduler.add_job(
                    self.watch_target, 
                    'interval', 
                    seconds=metadata.get("polling_interval", 300),
                    next_run_time=start_date,
                    args=[target_name, getattr(self, "app_state", None)],
                    id=job_id
                )
                stagger_delay += 15
                
                # Update DB state to ASSIGNED (Skipped on startup to prevent SQLite deadlock)
                # await TargetRegistryService.set_assignment_state(target_name, "ASSIGNED")

    def shutdown(self):
        cognitive_scheduler.shutdown()

watcher_service = ContinuousWatcher()
