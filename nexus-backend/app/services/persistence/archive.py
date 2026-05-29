import logging
import json
import os
from pathlib import Path
from typing import Dict, Any

from app.services.normalizer.canonical_models import CanonicalMarketSnapshot

logger = logging.getLogger(__name__)

# Data Lake Mock paths
ARCHIVE_DIR = Path("data/archive")
RAW_DIR = ARCHIVE_DIR / "raw"
CANONICAL_DIR = ARCHIVE_DIR / "canonical"

class ImmutableSnapshotArchive:
    """
    Layer A: Immutable Snapshot Archive.
    Stores the raw payload and the strongly-typed CanonicalMarketSnapshot.
    Never mutated. Provides perfect deterministic replay.
    """
    
    def __init__(self):
        os.makedirs(RAW_DIR, exist_ok=True)
        os.makedirs(CANONICAL_DIR, exist_ok=True)
        
    def archive_raw_payload(self, snapshot_id: str, raw_payload: Dict[str, Any]):
        """Persists the raw HTML/text payload immediately after acquisition."""
        filepath = RAW_DIR / f"{snapshot_id}_raw.json"
        
        # In a real enterprise system, raw_html might be dumped to S3/GCS.
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(raw_payload, f, ensure_ascii=False)
            
        logger.info(f"Archived RAW payload: {snapshot_id}")

    def archive_canonical_snapshot(self, snapshot: CanonicalMarketSnapshot):
        """Persists the canonical, strongly-typed snapshot."""
        filepath = CANONICAL_DIR / f"{snapshot.snapshot_id}_canonical.json"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(snapshot.model_dump_json(indent=2))
            
        logger.info(f"Archived CANONICAL snapshot: {snapshot.snapshot_id}")

archive_layer = ImmutableSnapshotArchive()
