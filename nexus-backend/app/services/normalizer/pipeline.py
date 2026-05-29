import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from app.services.normalizer.canonical_models import (
    CanonicalMarketSnapshot,
    Metadata,
    AcquisitionProvenance,
    Taxonomy
)
from app.services.scraper.dom_stability import calculate_dom_stability
from app.services.extractor.pricing_extractor import extract_pricing

logger = logging.getLogger(__name__)

async def normalize_snapshot(
    raw_payload: Dict[str, Any], 
    parent_snapshot_id: Optional[str] = None,
    lineage_chain_id: Optional[str] = None,
    historical_html: Optional[str] = None
) -> CanonicalMarketSnapshot:
    """
    Transforms a raw acquisition payload into the immutable CanonicalMarketSnapshot.
    Executes DOM stability checks and field-level semantic extraction.
    """
    logger.info(f"Normalizing snapshot for {raw_payload.get('company')}")
    
    # 1. Calculate Stability
    dom_stability = calculate_dom_stability(raw_payload.get('raw_html', ''), historical_html)
    
    # 2. Extract Fields & Confidences
    pricing, pricing_confidence = extract_pricing(raw_payload.get('raw_html', ''))
    
    # Generate Lineage
    snap_id = f"snap_{uuid.uuid4().hex[:12]}"
    chain_id = lineage_chain_id or f"chain_{uuid.uuid4().hex[:12]}"
    
    # 3. Assemble Canonical Schema
    snapshot = CanonicalMarketSnapshot(
        snapshot_id=snap_id,
        parent_snapshot_id=parent_snapshot_id,
        lineage_chain_id=chain_id,
        company=raw_payload.get('company', 'Unknown'),
        timestamp=datetime.utcnow(),
        acquisition_state=raw_payload.get('acquisition_state'),
        dom_stability_score=dom_stability,
        pricing_confidence=pricing_confidence,
        pricing=pricing,
        metadata=Metadata(
            source_url=raw_payload.get('target_url', ''),
            user_agent="nexus-acquisition-kernel/v1.0",
            provenance=AcquisitionProvenance(
                acquisition_runtime="playwright-chromium",
                browser_runtime_version=raw_payload.get('provenance', {}).get('browser_runtime_version', 'unknown'),
                fetch_duration_ms=raw_payload.get('provenance', {}).get('fetch_duration_ms', 0),
                retry_count=raw_payload.get('provenance', {}).get('retry_count', 0),
                acquisition_node=raw_payload.get('provenance', {}).get('acquisition_node', 'local')
            )
        ),
        taxonomy=Taxonomy(
            sector="Enterprise SaaS",
            vertical="General",
            target_audience=[]
        )
    )
    
    logger.info(f"Canonical Market Snapshot {snap_id} successfully materialized.")
    return snapshot
