import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.services.extractor.pricing_extractor import extract_pricing
from app.services.diff.feature_diff import diff_features
from app.services.scoring.signals import MaterializedSignal
from app.services.diff.thresholds import SignalSeverity
from app.services.scoring.ontology import evaluate_ontology
from app.services.scoring.confidence_graph import calculate_propagated_confidence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("--- 1. VERIFYING PRICING EXTRACTION ---")
    mock_html = """
    <html>
        <body>
            <div class="pricing-plan">
                <h3>Pro Plan</h3>
                <p>Only $199.00 / month</p>
            </div>
            <div class="pricing-card">
                <h3>Enterprise</h3>
                <p>Contact Sales</p>
            </div>
        </body>
    </html>
    """
    tiers, confidence = extract_pricing(mock_html)
    logger.info(f"Extraction Confidence: {confidence:.2f}")
    for tier in tiers:
        logger.info(f"Tier: {tier.name} - ${tier.price}")
        
    logger.info("\n--- 2. VERIFYING SEMANTIC FEATURE DIFFING ---")
    hist_features = ["Unlimited Storage", "SSO Integration", "24/7 Support"]
    curr_features = ["Unlimited Storage (10TB)", "24/7 Support", "Advanced Analytics"]
    
    signals = diff_features(hist_features, curr_features)
    for s in signals:
        if s["type"] == "FEATURE_MODIFIED":
            logger.info(f"{s['type']}: '{s['old_feature']}' -> '{s['new_feature']}' (Sim: {s['similarity']:.2f})")
        else:
            logger.info(f"{s['type']}: '{s['feature']}'")

    logger.info("\n--- 3. VERIFYING TEMPORAL EVENT CHAINS (WITH DECAY) ---")
    now = datetime.now(timezone.utc)
    
    # Create a temporal window of signals
    window = [
        # An old tier removal (should have decayed influence)
        MaterializedSignal(
            signal_type="TIER_REMOVED",
            severity=SignalSeverity.MATERIAL,
            confidence=0.9,
            impact=0.8,
            timestamp=now - timedelta(days=60), # 60 days old
            originating_snapshot_id="snap_1"
        ),
        # A recent pricing compression
        MaterializedSignal(
            signal_type="PRICING_COMPRESSION",
            severity=SignalSeverity.ESCALATE,
            confidence=0.95,
            impact=0.9,
            timestamp=now - timedelta(hours=12), # 12 hours old (100% influence)
            originating_snapshot_id="snap_2"
        )
    ]
    
    for sig in window:
        logger.info(f"Signal: {sig.signal_type}, Age: {sig.age_days:.1f} days, Decay Factor: {sig.decay_factor:.2f}")
        
    ontology = evaluate_ontology(window)
    logger.info(f"Ontology Convergence: {ontology['classification']}")
    
    logger.info("\n--- 4. VERIFYING CONFIDENCE PROPAGATION GRAPH ---")
    prop_conf = calculate_propagated_confidence(
        extraction_confidence=0.85,
        dom_stability=0.90,
        historical_consistency=0.95,
        corroboration_score=0.80
    )
    logger.info(f"Propagated Confidence: {prop_conf:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
