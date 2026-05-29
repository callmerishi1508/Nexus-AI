from enum import Enum
from fastapi import Header, HTTPException
from typing import List

class Role(str, Enum):
    OBSERVER = "OBSERVER"
    TRADER = "TRADER"
    ANALYST = "ANALYST"
    GOVERNANCE = "GOVERNANCE"
    EXECUTIVE = "EXECUTIVE"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"

# Pre-defined hierarchy for easy checks
ROLE_HIERARCHY = {
    Role.OBSERVER: 1,
    Role.TRADER: 2,
    Role.ANALYST: 3,
    Role.GOVERNANCE: 4,
    Role.EXECUTIVE: 5,
    Role.SYSTEM_ADMIN: 6
}

def require_role(min_role: Role):
    """
    Dependency that enforces institutional hierarchy.
    """
    def _check_role(x_nexus_role: str = Header(default="OBSERVER")):
        try:
            provided_role = Role(x_nexus_role.upper())
        except ValueError:
            raise HTTPException(status_code=403, detail="Invalid Institutional Role.")
            
        if ROLE_HIERARCHY[provided_role] < ROLE_HIERARCHY[min_role]:
            raise HTTPException(
                status_code=403, 
                detail=f"Restricted: Requires {min_role.value} clearance or higher."
            )
        return provided_role
    return _check_role

# Explicit escalation thresholds
MIN_ROLE_FOR_EXECUTIVE_BRIEF = Role.EXECUTIVE
MIN_ROLE_FOR_SIMULATION_APPROVAL = Role.ANALYST
MIN_ROLE_FOR_CHAOS_EXECUTION = Role.SYSTEM_ADMIN
MIN_ROLE_FOR_GOVERNANCE_ADJUDICATION = Role.GOVERNANCE
