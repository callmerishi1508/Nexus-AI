import logging

logger = logging.getLogger(__name__)

def calculate_propagated_confidence(
    extraction_confidence: float,
    dom_stability: float,
    historical_consistency: float = 1.0,
    corroboration_score: float = 1.0
) -> float:
    """
    Calculates localized propagated confidence.
    This is the mathematical foundation for institutional trust.
    
    Weights:
    - Extraction Confidence: 45%
    - DOM Stability: 25%
    - Historical Consistency: 15%
    - Corroboration Score: 15%
    """
    confidence = (
        (extraction_confidence * 0.45) +
        (dom_stability * 0.25) +
        (historical_consistency * 0.15) +
        (corroboration_score * 0.15)
    )
    
    # Cap at 1.0
    final_confidence = min(1.0, max(0.0, confidence))
    
    logger.info(f"Propagated Confidence: {final_confidence:.2f} "
                f"(Ext: {extraction_confidence:.2f}, DOM: {dom_stability:.2f}, "
                f"Hist: {historical_consistency:.2f}, Corr: {corroboration_score:.2f})")
                
    return final_confidence
