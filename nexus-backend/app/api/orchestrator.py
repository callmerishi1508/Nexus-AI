from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.registry import TargetRegistryService
from app.services.graph.query import export_graph_state
from app.services.synthesis import synthesis_engine
from app.db.models import get_db
from app.services.fetcher import safe_fetch_pipeline
from app.services.parser import process_guarded_inference
from app.services.engine import extract_semantic_intelligence, generate_semantic_diff, compute_dual_scores
from app.services.pdf_generator import generate_executive_brief
from app.services.replay_snapshot import get_latest_snapshot, get_fallback_diff, save_new_snapshot, get_snapshot_lineage
from app.api.dependencies import get_tenant
from app.services.sector_generator import generate_and_seed_sector

# =========================================================================
# NEXUS - ORCHESTRATION LAYER (STAGE 3: PERSISTENT LINEAGE)
# =========================================================================

router = APIRouter()

@router.get("/graph/state")
async def get_graph_state(
    timestamp: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant)
):
    target_dt = None
    if timestamp:
        from dateutil.parser import parse
        target_dt = parse(timestamp)
    
    state = await export_graph_state(db, tenant_id, target_dt)
    return state

@router.get("/synthesis/brief")
async def get_strategic_brief(
    timestamp: Optional[str] = None,
    db: AsyncSession = Depends(get_db), 
    tenant_id: str = Depends(get_tenant)
):
    target_dt = None
    if timestamp:
        from dateutil.parser import parse
        target_dt = parse(timestamp)
        
    brief = await synthesis_engine.generate_brief(db, tenant_id, target_dt)
    return brief

class ExpandSectorRequest(BaseModel):
    sector: str

@router.post("/graph/expand_sector")
async def expand_sector(
    req: ExpandSectorRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant)
):
    try:
        result = await generate_and_seed_sector(req.sector, db, tenant_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph/sectors")
async def get_all_sectors(db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant)):
    from sqlalchemy import select, distinct
    from app.db.models import GraphNode
    query = select(distinct(GraphNode.sector)).where(GraphNode.tenant_id == tenant_id, GraphNode.sector != None)
    result = await db.execute(query)
    sectors = [row[0] for row in result.all()]
    return {"sectors": sectors}

@router.get("/temporal/timeline")
async def get_temporal_timeline(tenant_id: str = Depends(get_tenant)):
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    # Mocking semantic milestones based on seed data timestamps
    return {
        "milestones": [
            {"date": (now - timedelta(days=60)).isoformat() + "Z", "label": "Initial Knowledge Seeding", "type": "SEED"},
            {"date": (now - timedelta(days=30)).isoformat() + "Z", "label": "Pricing Convergence Detected", "type": "EVENT"},
            {"date": (now - timedelta(days=15)).isoformat() + "Z", "label": "AI Acceleration Event", "type": "EVENT"},
            {"date": (now - timedelta(days=5)).isoformat() + "Z", "label": "Governance Freeze Triggered", "type": "GOVERNANCE"},
            {"date": now.isoformat() + "Z", "label": "Present State", "type": "LIVE"}
        ]
    }

class DemoRequest(BaseModel):
    competitor: str
    url: str
    force_fallback: bool = False
    scenario: str = "pricing_change"  # For deterministic fallback

class DemoResponse(BaseModel):
    status: str
    mode: str
    telemetry: Dict[str, Any]
    diff: Dict[str, Any]
    scores: Dict[str, Any]
    pdf_url: Optional[str]
    timeline: Optional[List[Dict[str, Any]]] = None

@router.post("/run", response_model=DemoResponse)
async def run_demo_orchestration(req: DemoRequest, background_tasks: BackgroundTasks, request: Request, tenant_id: str = Depends(get_tenant)):
    """
    Centralized orchestration pipeline for the NEXUS frontend.
    Guarantees deterministic output and demo survivability via SQLite FALLBACK cascades.
    """
    telemetry = {}
    
    # 1. Fetch Phase (Proprietary Ingestion using Browser Pool)
    browser = request.app.state.browser
    fetch_result = await safe_fetch_pipeline(req.competitor, req.url, browser)
    mode = fetch_result["mode"]
    
    if "telemetry" in fetch_result:
        telemetry.update(fetch_result["telemetry"])
    
    if req.force_fallback:
        mode = "FALLBACK"
    
    # Historical Lineage Query (Database)
    historical_snapshot = await get_latest_snapshot(req.competitor)
    
    if mode == "FALLBACK":
        # RECOVERY ROUTING
        diff_data = get_fallback_diff(req.competitor)
        scores = {
            "confidence_score": diff_data.pop("confidence_score", 9.0),
            "confidence_reason": diff_data.pop("confidence_reason", []),
            "impact_score": diff_data.pop("impact_score", 0.0),
            "impact_reason": diff_data.pop("impact_reason", "")
        }
        governance = {
            "reviewer": "admin",
            "action": "APPROVED",
            "notes": "Emergency Baseline Recovered from SQLite."
        }
        telemetry = {
            "mode": "FALLBACK",
            "fetch_latency_ms": 0,
            "inference_bypassed": True,
            "tokens_saved": 4500,
            "cache_hit": True,
            "snapshot_status": "RECOVERED",
            "integrity_score": historical_snapshot.get("integrity_score", 100) if historical_snapshot else 50
        }
    else:
        # LIVE MODE
        content = fetch_result["markdown_content"]
        
        # Deterministic Extraction & Hash Validation
        bypassed, current_hash, parser_telemetry = process_guarded_inference(content, historical_snapshot or {})
        telemetry.update(parser_telemetry)
        telemetry["mode"] = "LIVE"
        
        # "No Delta Detected" Logic (MANDATORY Stage 3 Feature)
        hist_hash = historical_snapshot.get("dom_hash") if historical_snapshot else None
        
        if hist_hash and current_hash == hist_hash:
            # Prevent lineage pollution
            print("No meaningful structural delta detected. Bypassing snapshot persistence.")
            bypassed = True
            telemetry["message"] = "No meaningful structural delta detected"
        
        if bypassed:
            diff_data = {"additions": {}, "removals": {}}
            scores = compute_dual_scores(diff_data)
        else:
            # Semantic Diff Engine
            raw_html = fetch_result.get("raw_html", "")
            current_extracted, inf_telemetry = await extract_semantic_intelligence(content, raw_html)
            telemetry.update(inf_telemetry)
            hist_extracted = historical_snapshot.get("scraped_data", {}) if historical_snapshot else {}
            
            diff_data = generate_semantic_diff(current_extracted, hist_extracted)
            scores = compute_dual_scores(diff_data)
            
            telemetry["integrity_score"] = 98 # High integrity for live extraction
            telemetry["snapshot_status"] = "LIVE"
            
            # Snapshot Persistence
            parent_id = historical_snapshot.get("id") if historical_snapshot else None
            await save_new_snapshot(
                competitor=req.competitor,
                url=req.url,
                dom_hash=current_hash,
                scraped_data=current_extracted,
                parent_id=parent_id,
                telemetry=telemetry
            )
            
        governance = {"reviewer": "admin", "action": "PENDING"}

    # Timeline Intelligence Query
    timeline_history = await get_snapshot_lineage(req.competitor, limit=5)

    try:
        pdf_path = generate_executive_brief(req.competitor, diff_data, telemetry, governance)
        pdf_url = f"/api/demo/download?path={pdf_path}"
    except Exception as e:
        print(f"PDF Error: {e}")
        pdf_url = None

    return DemoResponse(
        status="success",
        mode=telemetry.get("mode", mode),
        telemetry=telemetry,
        diff=diff_data,
        scores=scores,
        pdf_url=pdf_url,
        timeline=timeline_history
    )
