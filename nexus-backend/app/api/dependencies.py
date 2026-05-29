from fastapi import Header, HTTPException

def get_tenant(x_nexus_tenant: str = Header(default=None, alias="X-Nexus-Tenant")):
    if not x_nexus_tenant:
        raise HTTPException(status_code=401, detail="Tenant Isolation Violation: Missing X-Nexus-Tenant header.")
    return x_nexus_tenant
