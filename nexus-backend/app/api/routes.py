import uuid
from fastapi import APIRouter, Header, Request
from typing import Dict, Any, List, Optional

from app.services.query.orchestrator import orchestrate_sector_query, orchestrate_company_query
from app.services.personas.interpreter import interpret_trajectory
from app.schemas.intelligence import TrajectoryProjection

router = APIRouter()

@router.get("/sector", response_model=List[Dict[str, Any]])
async def get_sector_intelligence(request: Request):
    """
    Returns active macro-market trends (e.g. SECTOR_PRICING_COMPRESSION).
    """
    trace_id = request.headers.get("X-Trace-Id", uuid.uuid4().hex)
    return await orchestrate_sector_query(trace_id=trace_id)

@router.get("/company/{company_name}", response_model=TrajectoryProjection)
async def get_company_intelligence(
    company_name: str,
    request: Request,
    x_nexus_tenant: Optional[str] = Header(default="tenant_public")
):
    """
    Returns the temporal cognition path and compressed trajectory for a specific entity.
    """
    decoded_name = company_name.replace("%20", " ")
    trace_id = request.headers.get("X-Trace-Id", uuid.uuid4().hex)
    
    return await orchestrate_company_query(
        company_name=decoded_name,
        workspace=x_nexus_tenant,
        persona_id="SYSTEM",
        session_id="LIVE",
        trace_id=trace_id
    )

@router.get("/interpret/{persona_id}/{company_name}", response_model=TrajectoryProjection)
async def interpret_company_intelligence(
    persona_id: str, 
    company_name: str,
    request: Request,
    x_nexus_tenant: Optional[str] = Header(default="tenant_public")
):
    """
    Applies the mathematical persona weights over the objective graph trajectory.
    Returns the canonical TrajectoryProjection contract.
    """
    decoded_name = company_name.replace("%20", " ")
    trace_id = request.headers.get("X-Trace-Id", uuid.uuid4().hex)
    
    # We query the orchestrator, passing the persona for caching keys
    projection = await orchestrate_company_query(
        company_name=decoded_name,
        workspace=x_nexus_tenant,
        persona_id=persona_id,
        session_id="LIVE",
        trace_id=trace_id
    )
    
    # Generate subjective interpretation
    # We pass the trajectory dict since interpret_trajectory expects dict or Model
    trajectory_dict = projection.trajectory_compression.dict() if projection.trajectory_compression else None
    interpretation = interpret_trajectory(persona_id, trajectory_dict)
    
    projection.persona_interpretation = interpretation
    return projection
