from typing import List, Dict, Any
from sqlalchemy import select, update
from app.db.models import TargetRegistry, AsyncSessionLocal
import httpx
from datetime import datetime
import asyncio

# =========================================================================
# EPOCH 4: TARGET METADATA REGISTRY & LIFECYCLE
# =========================================================================

class TargetValidationEngine:
    @staticmethod
    async def validate_target(url: str) -> Dict[str, Any]:
        """Validates reachable domain, formats, and mock accessibility."""
        report = {
            "format_valid": url.startswith("http"),
            "reachable": False,
            "robots_safe": True, # Mock
            "notes": "Passed initial format validation."
        }
        
        if not report["format_valid"]:
            report["notes"] = "Invalid URL format."
            return report
            
        try:
            # Quick lightweight reachability check
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(url)
                if res.status_code < 400:
                    report["reachable"] = True
                    report["notes"] = "Domain reachable."
                else:
                    report["notes"] = f"Domain returned {res.status_code}"
        except Exception as e:
            report["notes"] = f"Unreachable: {str(e)}"
            
        return report

class TargetRegistryService:
    
    @staticmethod
    async def get_all_active_targets() -> Dict[str, Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(TargetRegistry).where(TargetRegistry.onboarding_state == "ACTIVE")
            )
            targets = result.scalars().all()
            return {
                t.company_name: {
                    "sector": t.sector,
                    "company": t.company_name,
                    "url": t.url,
                    "polling_interval": t.polling_interval
                } for t in targets
            }
            
    @staticmethod
    async def get_all_targets_raw() -> List[TargetRegistry]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(TargetRegistry))
            return result.scalars().all()
            
    @staticmethod
    async def submit_target(company: str, url: str, sector: str) -> TargetRegistry:
        async with AsyncSessionLocal() as session:
            normalized = company.strip().lower()
            
            # Check for dupes
            existing = await session.execute(
                select(TargetRegistry).where(TargetRegistry.normalized_name == normalized)
            )
            if existing.scalar_one_or_none():
                raise ValueError("Target already exists in registry.")
                
            new_target = TargetRegistry(
                company_name=company.strip(),
                normalized_name=normalized,
                url=url.strip(),
                sector=sector,
                onboarding_state="SUBMITTED",
                validation_state="PENDING",
                scheduler_assignment_state="UNASSIGNED",
                target_epoch="EPOCH_4"
            )
            session.add(new_target)
            await session.commit()
            await session.refresh(new_target)
            
            # Kick off async validation
            asyncio.create_task(TargetRegistryService._run_validation(new_target.id, url))
            return new_target

    @staticmethod
    async def _run_validation(target_id: str, url: str):
        report = await TargetValidationEngine.validate_target(url)
        async with AsyncSessionLocal() as session:
            target = await session.get(TargetRegistry, target_id)
            if target:
                target.validation_report = report
                if report["reachable"] and report["format_valid"]:
                    target.validation_state = "PASSED"
                    target.onboarding_state = "GOVERNANCE_PENDING"
                else:
                    target.validation_state = "FAILED"
                    target.onboarding_state = "REJECTED"
                await session.commit()

    @staticmethod
    async def approve_target(target_id: str, owner: str):
        async with AsyncSessionLocal() as session:
            target = await session.get(TargetRegistry, target_id)
            if target and target.onboarding_state == "GOVERNANCE_PENDING":
                target.onboarding_state = "APPROVED"
                target.governance_owner = owner
                target.approved_at = datetime.utcnow()
                await session.commit()
                
    @staticmethod
    async def activate_target(target_id: str):
        async with AsyncSessionLocal() as session:
            target = await session.get(TargetRegistry, target_id)
            if target and target.onboarding_state == "APPROVED":
                target.onboarding_state = "ACTIVE"
                target.active = 1
                await session.commit()
                
    @staticmethod
    async def set_assignment_state(company: str, state: str):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(TargetRegistry).where(TargetRegistry.company_name == company)
            )
            target = result.scalar_one_or_none()
            if target:
                target.scheduler_assignment_state = state
                await session.commit()
