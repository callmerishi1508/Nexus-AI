import asyncio
from fastapi import APIRouter, Depends
from app.auth.roles import require_role, Role
from app.config.settings import settings
import app.api.simulation as simulation_api

router = APIRouter(prefix="/api/system", tags=["System"])

@router.get("/state")
async def get_system_state(role: Role = Depends(require_role(Role.SYSTEM_ADMIN))):
    """
    Exposes infrastructure observability and resource budgets.
    Requires SYSTEM_ADMIN role.
    """
    return {
        "status": "success",
        "system_state": settings.SYSTEM_STATE,
        "resource_budgets": {
            "max_parallel_sandboxes": settings.MAX_PARALLEL_SANDBOXES,
            "max_pending_simulations": settings.MAX_PENDING_SIMULATIONS,
            "max_graph_mutations": settings.MAX_GRAPH_MUTATIONS,
            "max_concurrent_inference": settings.MAX_CONCURRENT_INFERENCE
        },
        "current_usage": {
            "active_sandboxes": simulation_api.active_sandboxes,
            "queued_sandboxes": simulation_api.queued_sandboxes,
            "active_inference_slots": len(asyncio.all_tasks())
        },
        "epochs": {
            "constitution": settings.CONSTITUTION_VERSION,
            "schema": settings.SCHEMA_EPOCH,
            "governance": settings.GOVERNANCE_EPOCH
        }
    }

from pydantic import BaseModel
from app.services.registry import TargetRegistryService
from app.services.watcher import watcher_service
from fastapi import Request

class TargetCreate(BaseModel):
    company: str
    url: str
    sector: str

@router.get("/targets")
async def get_targets():
    sectors = await TargetRegistryService.get_all_active_targets()
    # Group by sector for frontend
    grouped = {}
    for comp, meta in sectors.items():
        s = meta.get("sector", "Unknown")
        if s not in grouped:
            grouped[s] = []
        grouped[s].append(comp)
    return {"sector_targets": grouped}
    
@router.get("/targets/all")
async def get_all_targets_raw():
    targets = await TargetRegistryService.get_all_targets_raw()
    return {"targets": [
        {
            "id": t.id,
            "company_name": t.company_name,
            "url": t.url,
            "sector": t.sector,
            "onboarding_state": t.onboarding_state,
            "validation_state": t.validation_state,
            "scheduler_assignment_state": t.scheduler_assignment_state,
            "validation_report": t.validation_report,
            "created_at": t.created_at.isoformat() if t.created_at else None
        } for t in targets
    ]}

@router.post("/targets")
async def create_target(target: TargetCreate, request: Request):
    new_target = await TargetRegistryService.submit_target(target.company, target.url, target.sector)
    return {"status": "success", "company": new_target.company_name, "id": new_target.id}

@router.post("/targets/{target_id}/approve")
async def approve_target(target_id: str, role: Role = Depends(require_role(Role.GOVERNANCE))):
    await TargetRegistryService.approve_target(target_id, "GOVERNANCE_ADMIN")
    return {"status": "success"}
    
@router.post("/targets/{target_id}/activate")
async def activate_target(target_id: str, role: Role = Depends(require_role(Role.SYSTEM_ADMIN))):
    await TargetRegistryService.activate_target(target_id)
    return {"status": "success"}
