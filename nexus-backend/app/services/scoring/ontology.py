import logging
import hashlib
from typing import List, Dict, Any

from app.services.diff.thresholds import SignalSeverity
from app.config.versions import ONTOLOGY_VERSION
from app.services.scoring.signals import MaterializedSignal

logger = logging.getLogger(__name__)

class MarketOntologyState:
    UNDERPERFORMING = "UNDERPERFORMING"
    AGGRESSIVE_EXPANSION = "AGGRESSIVE_EXPANSION"
    PRICING_COMPRESSION = "PRICING_COMPRESSION"
    FEATURE_ESCALATION = "FEATURE_ESCALATION"
    MARKET_RETREAT = "MARKET_RETREAT"
    STABLE = "STABLE"

def evaluate_ontology(temporal_window: List[MaterializedSignal]) -> Dict[str, Any]:
    """
    Derives structural market reality from a Temporal Context Window (e.g. last 5 materialized signals).
    Signals are weighted by their temporal decay factor.
    """
    logger.info(f"Evaluating Market Ontology impacts from {len(temporal_window)} materialized signals...")
    
    if not temporal_window:
        return {
            "classification": MarketOntologyState.STABLE,
            "ontology_version": ONTOLOGY_VERSION,
            "interpretation_hash": None,
            "signal_count": 0,
            "primary_signals": []
        }
    
    # Calculate deterministic hash for ontology drift protection (based on signal types & severities)
    signal_hash_input = "".join([f"{s.signal_type}_{s.severity.name}" for s in sorted(temporal_window, key=lambda x: x.signal_type)])
    interpretation_hash = hashlib.sha256(f"{ONTOLOGY_VERSION}_{signal_hash_input}".encode()).hexdigest()[:12]
    
    # Calculate decayed presence of structural signals
    tier_removal_weight = sum([s.decay_factor for s in temporal_window if s.signal_type == "TIER_REMOVED"])
    compression_weight = sum([s.decay_factor for s in temporal_window if s.signal_type == "PRICING_COMPRESSION"])
    increase_weight = sum([s.decay_factor for s in temporal_window if s.signal_type == "PRICING_INCREASE"])
    feature_removal_weight = sum([s.decay_factor for s in temporal_window if s.signal_type == "FEATURE_REMOVED"])
    
    classification = MarketOntologyState.STABLE
    
    # Ontology Convergence Logic (Factoring in temporal decay)
    if (tier_removal_weight > 0.5 or feature_removal_weight > 0.5) and compression_weight > 0.5:
        classification = MarketOntologyState.MARKET_RETREAT
    elif compression_weight > 0.8:
        classification = MarketOntologyState.PRICING_COMPRESSION
    elif increase_weight > 0.8:
        classification = MarketOntologyState.AGGRESSIVE_EXPANSION
        
    return {
        "classification": classification,
        "ontology_version": ONTOLOGY_VERSION,
        "interpretation_hash": interpretation_hash,
        "signal_count": len(temporal_window),
        "primary_signals": [s.signal_type for s in temporal_window if s.severity >= SignalSeverity.MATERIAL]
    }
