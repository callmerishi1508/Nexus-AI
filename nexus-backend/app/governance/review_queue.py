import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.db.models import get_db, GovernanceReview
from app.events.bus import distributed_bus
from app.api.dependencies import get_tenant
from app.auth.roles import require_role, Role, MIN_ROLE_FOR_GOVERNANCE_ADJUDICATION

router = APIRouter()

class ReviewAction(BaseModel):
    action: str  # ESCALATE, VERIFY, REJECT, ARCHIVE
    notes: Optional[str] = None
    priority_bump: Optional[float] = 0.0

@router.get("/queue")
async def get_review_queue(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant),
    role: Role = Depends(require_role(Role.ANALYST))
):
    """
    Fetches pending strategic synthesis items waiting for institutional governance.
    """
    result = await db.execute(
        select(GovernanceReview)
        .where(GovernanceReview.tenant_id == tenant_id)
        .where(GovernanceReview.status.in_(["REVIEW_REQUIRED", "ESCALATED"]))
        .order_by(GovernanceReview.priority_score.desc())
    )
    reviews = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "status": r.status,
            "priority_score": r.priority_score,
            "review_reason": r.review_reason,
            "risk_level": r.risk_level,
            "escalation_priority": r.escalation_priority,
            "brief_data": json.loads(r.brief_data) if r.brief_data else {},
            "evidence_anchors": json.loads(r.evidence_anchors) if r.evidence_anchors else [],
            "created_at": r.created_at
        }
        for r in reviews
    ]

@router.post("/{review_id}/adjudicate")
async def adjudicate_review(
    review_id: str, 
    action: ReviewAction, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant),
    role: Role = Depends(require_role(MIN_ROLE_FOR_GOVERNANCE_ADJUDICATION))
):
    """
    State machine transition for institutional governance.
    """
    result = await db.execute(select(GovernanceReview).where(GovernanceReview.id == review_id, GovernanceReview.tenant_id == tenant_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review item not found")
        
    old_status = review.status
    
    if action.action == "ESCALATE":
        review.status = "ESCALATED"
        review.escalation_priority = "HIGH"
    elif action.action == "VERIFY":
        review.status = "VERIFIED"
    elif action.action == "REJECT":
        review.status = "REJECTED"
    elif action.action == "ARCHIVE":
        review.status = "ARCHIVED"
    elif action.action == "PUBLISH":
        if review.status != "VERIFIED":
            raise HTTPException(status_code=400, detail="Must be VERIFIED before EXECUTIVE_BRIEFED")
        review.status = "EXECUTIVE_BRIEFED"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    review.reviewer_notes = action.notes
    if action.priority_bump:
        review.priority_score += action.priority_bump
        
    await db.commit()
    
    await distributed_bus.publish("events.governance", {
        "event_id": review_id,
        "action": action.action,
        "new_status": review.status,
        "old_status": old_status
    })
    
    return {"status": "success", "new_state": review.status}
