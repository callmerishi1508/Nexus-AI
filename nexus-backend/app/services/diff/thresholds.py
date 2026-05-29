from enum import Enum

class SignalSeverity(int, Enum):
    NOISE = 0
    LOW_SIGNAL = 1
    MATERIAL = 2
    ESCALATE = 3
    CRITICAL_EVENT = 4

class MaterializationThresholds:
    """
    Prevents every minor diff from becoming an intelligence event.
    Compresses noise.
    """
    PRICING_CHANGE_MIN_PERCENT = 5.0  # e.g., 1% change is ignored, >5% is material
    FEATURE_REMOVAL_SEVERITY = SignalSeverity.ESCALATE
    TIER_REMOVAL_SEVERITY = SignalSeverity.MATERIAL
    HEADLINE_TWEAK_SEVERITY = SignalSeverity.NOISE
