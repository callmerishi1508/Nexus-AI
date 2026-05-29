import asyncio
import logging
import json
from datetime import datetime
from app.services.connector.pricing import acquire_pricing_page
from app.services.normalizer.pipeline import normalize_snapshot
from app.services.diff.pricing_diff import diff_pricing
from app.services.scoring.ontology import evaluate_ontology
from app.services.persistence.archive import archive_layer
from app.services.persistence.derivatives import derivative_store
from app.services.normalizer.canonical_models import CanonicalMarketSnapshot, Metadata, Taxonomy, AcquisitionProvenance, AcquisitionState
from app.config.versions import EXTRACTOR_VERSION, NORMALIZER_VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    target_url = "https://example.com/pricing"
    company_name = "Notion (Test Target)"
    
    # 1. Acquire
    logger.info("--- PHASE 1: ACQUISITION ---")
    raw_payload = await acquire_pricing_page(target_url, company_name)
    
    # Create Mock Historical Snapshot (representing older pricing)
    historical_snapshot = CanonicalMarketSnapshot(
        snapshot_id="snap_hist_001",
        lineage_chain_id="chain_001",
        company=company_name,
        timestamp=datetime.utcnow(),
        extractor_version=EXTRACTOR_VERSION,
        normalizer_version=NORMALIZER_VERSION,
        ontology_version="v1.0.0",
        acquisition_state=AcquisitionState.ACQUISITION_COMPLETE,
        pricing=[
            {"name": "Pro", "price": 10.0, "currency": "USD", "billing_cycle": "monthly", "features": []}, # Older, cheaper price
            {"name": "Enterprise", "price": 499.0, "currency": "USD", "billing_cycle": "monthly", "features": []}
        ],
        metadata=Metadata(source_url=target_url, user_agent="test", provenance=AcquisitionProvenance(acquisition_runtime="test", browser_runtime_version="test", fetch_duration_ms=0, retry_count=0, acquisition_node="test")),
        taxonomy=Taxonomy(sector="Test", vertical="Test")
    )
    
    # 2. Normalize
    logger.info("\n--- PHASE 2: NORMALIZATION ---")
    current_snapshot = await normalize_snapshot(
        raw_payload=raw_payload,
        parent_snapshot_id=historical_snapshot.snapshot_id,
        lineage_chain_id=historical_snapshot.lineage_chain_id,
        historical_html="<html><body><div>Older Layout</div></body></html>"
    )
    
    # 3. Archive
    logger.info("\n--- PHASE 3: PERSISTENCE ---")
    archive_layer.archive_raw_payload(current_snapshot.snapshot_id, raw_payload)
    archive_layer.archive_canonical_snapshot(current_snapshot)
    
    # 4. Diff & Score
    logger.info("\n--- PHASE 4: DIFF & ONTOLOGY ---")
    signals = diff_pricing(current_snapshot, historical_snapshot)
    logger.info(f"Diff Signals: {json.dumps(signals, indent=2)}")
    
    impact = evaluate_ontology(signals)
    logger.info(f"Ontology Impact: {json.dumps(impact, indent=2)}")
    
    # 5. Store Derivative
    derivative_store.store_event(current_snapshot.snapshot_id, {
        "signals": signals,
        "impact": impact
    })
    
    # 6. Cleanup
    from app.services.scraper.browser_pool import browser_pool
    await browser_pool.close()
    
    logger.info("\nVERIFICATION COMPLETE.")

if __name__ == "__main__":
    asyncio.run(main())
