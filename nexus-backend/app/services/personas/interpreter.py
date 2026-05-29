import logging
from typing import Dict, Any, Optional

from app.services.personas.registry import registry as persona_registry
from app.schemas.intelligence import InterpretationResult, InterpretationProvenance

logger = logging.getLogger(__name__)

def interpret_trajectory(persona_id: str, objective_trajectory: Optional[Dict[str, Any]] = None) -> Optional[InterpretationResult]:
    """
    Applies a Persona Lens over the objective trajectory.
    Returns Canonical InterpretationResult.
    """
    if not objective_trajectory:
        return None
        
    snapshot = persona_registry.get_persona(persona_id)
    if not snapshot:
        # Graceful fallback to a neutral snapshot if persona missing
        weights = {"market_retreat": 1.0, "aggressive_expansion": 1.0, "pricing_compression": 1.0, "feature_escalation": 1.0, "volatility": 1.0}
        logger.warning(f"Persona {persona_id} not found in registry. Using fallback.")
    else:
        weights = snapshot.weights
    
    dominant_trend = objective_trajectory.get("dominant_trend", "Structural Realignment")
    
    # Map the dominant trend to the weight keys
    trend_key_map = {
        "Market Retreat": "market_retreat",
        "Aggressive Expansion": "aggressive_expansion",
        "Pricing Compression": "pricing_compression",
        "Feature Escalation": "feature_escalation"
    }
    
    key = trend_key_map.get(dominant_trend, "volatility")
    weight_applied = weights.get(key, 1.0)
    
    # Generate the Interpretive Projection
    if weight_applied > 1.2:
        strategic_framing = f"CRITICAL PRIORITY: {dominant_trend} detected. High impact on your objectives."
    elif weight_applied < 0.8:
        strategic_framing = f"LOW PRIORITY: {dominant_trend} detected. Minor impact on your objectives."
    else:
        strategic_framing = f"STANDARD PRIORITY: {dominant_trend} detected. Monitor closely."
        
    summary = f"[{persona_id.upper()} LENS]: {strategic_framing}"
    
    provenance = InterpretationProvenance(
        dominant_trend=dominant_trend,
        weight_applied=weight_applied,
        full_ontology_weights=weights
    )
    
    return InterpretationResult(
        persona_applied=persona_id.upper(),
        interpretive_summary=summary,
        interpretation_provenance=provenance
    )
