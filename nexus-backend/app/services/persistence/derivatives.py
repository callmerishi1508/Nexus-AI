import logging
import json
import os
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

DERIVATIVE_DIR = Path("data/derivatives")

class DerivativeIntelligenceStore:
    """
    Layer B: Intelligence Derivatives.
    Stores Diffs, Scores, Ontology Classifications, and Predictions.
    Can be mutated, recomputed, and deleted without destroying raw truth.
    """
    
    def __init__(self):
        os.makedirs(DERIVATIVE_DIR, exist_ok=True)
        
    def store_event(self, snapshot_id: str, event_payload: Dict[str, Any]):
        """Persists a materialized market event or diff."""
        filepath = DERIVATIVE_DIR / f"{snapshot_id}_event.json"
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(event_payload, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Persisted DERIVATIVE intelligence for snapshot: {snapshot_id}")

derivative_store = DerivativeIntelligenceStore()
