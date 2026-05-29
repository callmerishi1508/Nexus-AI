import logging
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from app.services.graph.builder import build_ephemeral_graph
from app.services.graph.sector_intelligence import inject_sector_emergence
from app.services.graph.queries import trace_signal_provenance, get_sector_emergence
from app.services.persistence.derivatives import DERIVATIVE_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_mock_derivative(company: str, snapshot_id: str, classification: str, signals: list):
    """Generates a mock derivative file simulating an event output."""
    filepath = DERIVATIVE_DIR / f"{snapshot_id}_event.json"
    os.makedirs(DERIVATIVE_DIR, exist_ok=True)
    
    with open(filepath, "w") as f:
        json.dump({
            "company": company,
            "timestamp": datetime.now(timezone.utc).timestamp(),
            "impact": {
                "classification": classification,
                "primary_signals": [s["type"] for s in signals]
            },
            "signals": signals
        }, f)

def main():
    logger.info("--- 1. MOCKING GRAPH DERIVATIVES ---")
    # Simulate 3 different companies encountering PRICING_COMPRESSION independently
    generate_mock_derivative("Company Alpha", "snap_alpha_1", "PRICING_COMPRESSION", [
        {"type": "PRICING_COMPRESSION", "confidence": 0.9, "severity": 2}
    ])
    generate_mock_derivative("Company Beta", "snap_beta_1", "PRICING_COMPRESSION", [
        {"type": "PRICING_COMPRESSION", "confidence": 0.88, "severity": 2}
    ])
    generate_mock_derivative("Company Gamma", "snap_gamma_1", "PRICING_COMPRESSION", [
        {"type": "PRICING_COMPRESSION", "confidence": 0.95, "severity": 2}
    ])
    
    # Simulate a company with a low-confidence signal that should be filtered out
    generate_mock_derivative("Company Delta", "snap_delta_1", "STABLE", [
        {"type": "FEATURE_ADDED", "confidence": 0.4, "severity": 1} # Should be dropped (0.4 < 0.7)
    ])
    
    logger.info("\n--- 2. BUILDING DETERMINISTIC GRAPH ---")
    graph = build_ephemeral_graph()
    
    logger.info("\n--- 3. DETECTING SECTOR EMERGENCE ---")
    inject_sector_emergence(graph)
    
    logger.info("\n--- 4. QUERYING GRAPH ---")
    sector_signals = get_sector_emergence(graph)
    logger.info(f"Sector Emergence Detected: {sector_signals}")
    
    # Trace provenance of the first signal from Company Alpha
    prov = trace_signal_provenance(graph, "sig_snap_alpha_1_0")
    if prov:
        logger.info(f"Provenance Trace for sig_snap_alpha_1_0 -> Snapshot: {prov['origin_snapshot_id']}")
    else:
        logger.warning("Provenance trace failed.")
        
    logger.info("\n--- 5. DISPOSING GRAPH ---")
    graph.clear()
    logger.info("Lifecycle complete.")

if __name__ == "__main__":
    main()
