from enum import Enum

class AcquisitionState(str, Enum):
    """
    Tracks the institutional status of a target during the acquisition mesh lifecycle.
    Prevents scraper instability from breaking the intelligence pipeline.
    """
    ACQUISITION_PENDING = "ACQUISITION_PENDING"       # Target registered, awaiting pool
    ACQUISITION_ACTIVE = "ACQUISITION_ACTIVE"         # Currently fetching/parsing
    ACQUISITION_DEGRADED = "ACQUISITION_DEGRADED"     # Partial timeouts, CSS broke, DOM entropy high
    ACQUISITION_BLOCKED = "ACQUISITION_BLOCKED"       # WAF, Captcha, IP Ban, or 403
    ACQUISITION_COMPLETE = "ACQUISITION_COMPLETE"     # Canonical extraction successful
