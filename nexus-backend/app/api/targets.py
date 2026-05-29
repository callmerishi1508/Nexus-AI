from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from app.db.models import get_db, TargetRegistry
from app.api.dependencies import get_tenant

router = APIRouter(tags=["Governance Targets"])

async def simulate_validation_lifecycle(target_id: str, db: AsyncSession):
    # Simulated validation engine
    await asyncio.sleep(2)
    target = await db.get(TargetRegistry, target_id)
    if not target: return
    
    target.onboarding_state = "VALIDATING"
    await db.commit()
    
    await asyncio.sleep(4)
    target.onboarding_state = "GOVERNANCE_PENDING"
    target.validation_report = {
        "reachability": "Verified",
        "taxonomy_alignment": 92.5,
        "integrity_precheck": "Passed"
    }
    target.integrity_score = 100.0
    await db.commit()

async def simulate_reconciliation_lifecycle(target_id: str, db: AsyncSession):
    # Simulated scheduler reconciliation
    await asyncio.sleep(2.5)
    target = await db.get(TargetRegistry, target_id)
    if not target: return
    
    target.onboarding_state = "ACTIVE"
    target.scheduler_assignment_state = "ASSIGNED"
    target.active = 1
    await db.commit()

@router.post("/register")
async def register_target(payload: Dict[str, Any], background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant)):
    company_name = payload.get("company_name")
    url = payload.get("url")
    sector = payload.get("sector")
    
    if not company_name or not url:
        raise HTTPException(status_code=400, detail="Missing required fields")
        
    target = TargetRegistry(
        company_name=company_name,
        normalized_name=company_name.lower().replace(" ", "_"),
        url=url,
        sector=sector,
        onboarding_state="SUBMITTED",
        validation_state="PENDING",
        scheduler_assignment_state="UNASSIGNED",
        tenant_id=tenant_id
    )
    
    db.add(target)
    await db.commit()
    await db.refresh(target)
    
    background_tasks.add_task(simulate_validation_lifecycle, target.id, db)
    
    return {"status": "success", "target_id": target.id, "state": "SUBMITTED"}

@router.get("/")
async def list_targets(db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant)):
    result = await db.execute(select(TargetRegistry).where(TargetRegistry.tenant_id == tenant_id).order_by(TargetRegistry.created_at.desc()))
    targets = result.scalars().all()
    
    return [{
        "id": t.id,
        "company_name": t.company_name,
        "url": t.url,
        "sector": t.sector,
        "onboarding_state": t.onboarding_state,
        "validation_report": t.validation_report,
        "integrity_score": t.integrity_score,
        "intelligence_readiness": int(t.integrity_score) if t.integrity_score else 50,
        "ingestion_lineage": f"SUBMITTED_BY_ANALYST_{t.id[:4]}",
        "scheduler_assignment_state": t.scheduler_assignment_state
    } for t in targets]

@router.post("/{target_id}/approve")
async def approve_target(target_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant)):
    target = await db.get(TargetRegistry, target_id)
    if not target or target.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Target not found in this cognitive domain")
        
    if target.onboarding_state != "GOVERNANCE_PENDING":
        raise HTTPException(status_code=400, detail="Target must be in GOVERNANCE_PENDING state")
        
    target.onboarding_state = "RECONCILING"
    target.approved_at = datetime.utcnow()
    target.governance_owner = "EXECUTIVE_AUTH"
    await db.commit()
    
    background_tasks.add_task(simulate_reconciliation_lifecycle, target.id, db)
    
    return {"status": "success", "state": "RECONCILING"}
