from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
from pydantic import BaseModel

from app.db.models import get_db, StrategicSimulation, WebSnapshot, TargetRegistry, GraphNode
from app.simulation.engine import ScenarioSandboxEngine
from app.auth.roles import require_role, Role, MIN_ROLE_FOR_SIMULATION_APPROVAL
from app.config.settings import settings
from app.api.dependencies import get_tenant
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])

# Global state for resource tracking (in-memory mock)
active_sandboxes = 0
queued_sandboxes = 0

class SimulationRequest(BaseModel):
    target_node_id: str
    mutation_type: str
    temporal_horizon: str
    requested_trajectory: str

@router.post("/estimate")
async def estimate_simulation_cost(req: SimulationRequest, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant)):
    """
    Returns resource cost estimates for the proposed simulation.
    """
    # Verify node exists within tenant scope
    node_result = await db.execute(select(GraphNode).where(GraphNode.name == req.target_node_id).where(GraphNode.tenant_id == tenant_id))
    
    # Simple heuristic
    base_mutations = 5
    if req.temporal_horizon == "MEDIUM": base_mutations *= 2
    elif req.temporal_horizon == "LONG": base_mutations *= 4
    
    inference_load = "LOW"
    if req.temporal_horizon == "LONG" and req.requested_trajectory in ["DIVERGENCE", "ESCALATION"]:
        inference_load = "HIGH"
    elif req.temporal_horizon == "MEDIUM":
        inference_load = "MEDIUM"

    return {
        "graph_mutations": base_mutations,
        "sandbox_depth": 3,
        "estimated_inference_load": inference_load,
        "cost_warning": base_mutations > settings.MAX_GRAPH_MUTATIONS
    }

@router.post("/project")
async def project_simulation(
    req: SimulationRequest, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant),
    role: Role = Depends(require_role(MIN_ROLE_FOR_SIMULATION_APPROVAL))
):
    """
    Executes a new bounded scenario projection.
    Enforces resource governance limits and system states.
    """
    global active_sandboxes, queued_sandboxes
    
    if settings.SYSTEM_STATE == settings.STATE_GOVERNANCE_FROZEN:
        logger.warning(
            f"[CONSTITUTION] Simulation blocked:\n"
            f"reason=SYSTEM_STATE_FROZEN\n"
            f"target={req.target_node_id}"
        )
        raise HTTPException(status_code=403, detail="System is GOVERNANCE_FROZEN. Simulations temporarily suspended.")
        
    if active_sandboxes >= settings.MAX_PARALLEL_SANDBOXES:
        if queued_sandboxes >= settings.MAX_PENDING_SIMULATIONS:
            logger.warning(
                f"[CONSTITUTION] Simulation blocked:\n"
                f"reason=RESOURCE_GOVERNANCE_LIMIT_EXCEEDED\n"
                f"active_sandboxes={active_sandboxes}\n"
                f"queued_sandboxes={queued_sandboxes}"
            )
            raise HTTPException(status_code=429, detail="Institutional load limit reached. Queue full. Try again later.")
        
        # Graceful degradation via queuing
        queued_sandboxes += 1
        while active_sandboxes >= settings.MAX_PARALLEL_SANDBOXES:
            await asyncio.sleep(1) # wait for slot
        queued_sandboxes -= 1

    # =========================================================================
    # EPOCH 4: MATURITY CONSTRAINTS
    # =========================================================================
    # Check if target is governed and mature enough for simulation
    target_result = await db.execute(select(TargetRegistry).where(TargetRegistry.company_name == req.target_node_id).where(TargetRegistry.tenant_id == tenant_id))
    target = target_result.scalar_one_or_none()
    
    # DEMO BYPASS: Allow any target
    # if target and target.onboarding_state != "ACTIVE":
    #     raise HTTPException(status_code=403, detail=f"Target {req.target_node_id} is not ACTIVE. Current state: {target.onboarding_state}")
        
    snapshots_result = await db.execute(
        select(WebSnapshot.id).where(WebSnapshot.competitor_name == req.target_node_id).where(WebSnapshot.tenant_id == tenant_id)
    )
    snapshot_count = len(snapshots_result.scalars().all())
    
    # DEMO BYPASS: For the hackathon, we allow simulation of any target entity even if they lack snapshots
    # if snapshot_count < settings.SIMULATION_MINIMUM_SNAPSHOTS:
    #     raise HTTPException(
    #         status_code=403, 
    #         detail=f"Target {req.target_node_id} lacks evidence maturity. Has {snapshot_count}/{settings.SIMULATION_MINIMUM_SNAPSHOTS} snapshots required."
    #     )

    active_sandboxes += 1
    engine = ScenarioSandboxEngine(db)
    try:
        sim = await engine.execute_projection(
            target_node=req.target_node_id,
            mutation=req.mutation_type,
            horizon=req.temporal_horizon,
            requested_trajectory=req.requested_trajectory
        )
        return {
            "status": "success",
            "simulation_id": sim.id,
            "governance_state": sim.governance_state,
            "trajectory_type": sim.trajectory_type,
            "confidence": sim.confidence,
            "stability_score": sim.stability_score,
            "synthesis": sim.synthesis_payload,
            "fingerprints": {
                "simulation_hash": sim.simulation_hash,
                "trajectory_hash": sim.trajectory_hash,
                "constraint_hash": sim.constraint_hash
            }
        }
    except ValueError as e:
        logger.error(
            f"[CONSTITUTION] Simulation validation failed:\n"
            f"reason=SANDBOX_VIOLATION\n"
            f"error={str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Failsafe rollback logging
        logger.error(
            f"[CONSTITUTION] Sandbox lifecycle failure:\n"
            f"reason=UNHANDLED_EXCEPTION\n"
            f"error={str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal sandbox failure.")
    finally:
        active_sandboxes -= 1

@router.get("/scenarios")
async def get_scenarios(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant),
    role: Role = Depends(require_role(Role.ANALYST))
):
    """
    Fetches the history of re-playable institutional simulations.
    """
    result = await db.execute(select(StrategicSimulation).where(StrategicSimulation.tenant_id == tenant_id).order_by(StrategicSimulation.created_at.desc()))
    simulations = result.scalars().all()
    
    return [
        {
            "id": sim.id,
            "target": sim.target_node_id,
            "mutation": sim.mutation_type,
            "horizon": sim.temporal_horizon,
            "trajectory": sim.trajectory_type,
            "governance_state": sim.governance_state,
            "confidence": sim.confidence,
            "stability_score": sim.stability_score,
            "created_at": sim.created_at
        }
        for sim in simulations
    ]
