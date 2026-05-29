import logging
from typing import Dict, Any, List

from app.services.normalizer.canonical_models import CanonicalMarketSnapshot
from app.services.diff.thresholds import MaterializationThresholds, SignalSeverity

logger = logging.getLogger(__name__)

def diff_pricing(current: CanonicalMarketSnapshot, historical: CanonicalMarketSnapshot) -> List[Dict[str, Any]]:
    """
    Analyzes pricing changes. Emits signals only if they cross materialization thresholds.
    """
    signals = []
    
    # Fast path if completely missing in history
    if not historical.pricing and current.pricing:
        signals.append({
            "type": "NEW_PRICING_MODEL_DETECTED",
            "severity": SignalSeverity.MATERIAL
        })
        return signals

    hist_tiers = {t.name: t.price for t in historical.pricing}
    curr_tiers = {t.name: t.price for t in current.pricing}
    
    for name, old_price in hist_tiers.items():
        if name not in curr_tiers:
            signals.append({
                "type": "TIER_REMOVED",
                "tier_name": name,
                "severity": MaterializationThresholds.TIER_REMOVAL_SEVERITY
            })
            continue
            
        new_price = curr_tiers[name]
        if old_price > 0:
            change_percent = abs((new_price - old_price) / old_price) * 100
            
            if change_percent >= MaterializationThresholds.PRICING_CHANGE_MIN_PERCENT:
                direction = "INCREASE" if new_price > old_price else "COMPRESSION"
                severity = SignalSeverity.ESCALATE if change_percent > 15 else SignalSeverity.MATERIAL
                signals.append({
                    "type": f"PRICING_{direction}",
                    "tier_name": name,
                    "old_price": old_price,
                    "new_price": new_price,
                    "severity": severity
                })
            else:
                logger.debug(f"Pricing change for {name} ({change_percent:.1f}%) ignored (below threshold).")
                
    return signals
