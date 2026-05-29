import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import TargetRegistry, AsyncSessionLocal
from app.services.registry import TargetRegistryService

logger = logging.getLogger(__name__)

class GovernanceDaemon:
    def __init__(self):
        self.is_running = False
        self._task = None

    async def _sweep_pending_targets(self):
        """Sweeps the system for GOVERNANCE_PENDING targets and auto-arbitrates them."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(TargetRegistry).where(TargetRegistry.onboarding_state == "GOVERNANCE_PENDING")
            )
            pending_targets = result.scalars().all()
            
            for target in pending_targets:
                logger.info(f"[GOVERNANCE DAEMON] Arbitrating pending target: {target.company_name} ({target.id})")
                
                # Auto-approve for the hackathon "Universal" requirement
                target.onboarding_state = "ACTIVE"
                target.scheduler_assignment_state = "ASSIGNED"
                
                # In a real system, we'd trigger a background task to scrape it right now.
                # Here, we update the state so the frontend Target Registration completes.
                
            if pending_targets:
                await db.commit()
                logger.info(f"[GOVERNANCE DAEMON] Arbitrated {len(pending_targets)} targets to ACTIVE.")

    async def run(self):
        self.is_running = True
        logger.info("[GOVERNANCE DAEMON] Autonomous Agent started.")
        while self.is_running:
            try:
                await self._sweep_pending_targets()
            except Exception as e:
                logger.error(f"[GOVERNANCE DAEMON] Error during sweep: {e}")
            await asyncio.sleep(5) # Poll every 5 seconds

    def start(self):
        if not self.is_running:
            self._task = asyncio.create_task(self.run())
            
    def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()

governance_daemon = GovernanceDaemon()
