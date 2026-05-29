from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import get_db
from app.api.dependencies import get_tenant
from app.services.fetcher import safe_fetch_pipeline
from app.services.engine import extract_semantic_intelligence, compute_dual_scores
from app.services.synthesis import synthesis_engine
from app.services.replay_snapshot import save_new_snapshot
from app.services.graph.query import export_graph_state

router = APIRouter()

class IngestionRequest(BaseModel):
    url: str
    competitor: str
    signal_type: str  # NEWS, PRODUCT, PRICING, RELEASE_NOTES
    
MIN_MATERIALIZATION_CONFIDENCE = 0.75

@router.post("/live")
async def ingest_live_signal(req: IngestionRequest, request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant)):
    """
    Live Market Acquisition Pipeline
    Fetches raw DOM, extracts intelligence, checks confidence threshold, and materializes to graph.
    """
    browser = request.app.state.browser
    fetch_result = await safe_fetch_pipeline(req.competitor, req.url, browser)
    
    if fetch_result["error"]:
        raise HTTPException(status_code=400, detail=f"Ingestion failed: {fetch_result['error']}")
        
    content = fetch_result["markdown_content"]
    raw_html = fetch_result.get("raw_html", "")
    
    current_extracted, telemetry = await extract_semantic_intelligence(content, raw_html)
    
    # Generate scores to determine materialization safety
    diff_data = {"additions": current_extracted, "removals": {}} # Synthetic diff for scoring
    scores = compute_dual_scores(diff_data)
    
    confidence = scores.get("confidence_score", 0) / 10.0 # scale 0 to 10 back to 0.0-1.0
    
    if confidence < MIN_MATERIALIZATION_CONFIDENCE:
        return {
            "status": "REJECTED",
            "message": f"Signal Spam Prevention: Confidence ({confidence}) below materialization threshold.",
            "data": current_extracted
        }
        
    # Proceed to Materialization
    import time
    telemetry["integrity_score"] = int(confidence * 100)
    await save_new_snapshot(
        competitor=req.competitor,
        url=req.url,
        dom_hash=str(hash(content)),
        scraped_data=current_extracted,
        parent_id=None,
        telemetry=telemetry
    )
    
    # Export updated graph to trigger UI refresh implicitly (if client polls or websockets)
    updated_graph = await export_graph_state(db, tenant_id)
    
    return {
        "status": "MATERIALIZED",
        "message": "Signal successfully processed into the Knowledge Graph.",
        "confidence": confidence,
        "nodes_added": len(updated_graph.get("nodes", []))
    }
