import logging
from typing import Dict, Any, Optional

from app.services.scraper.browser_pool import browser_pool
from app.services.scraper.governance import AcquisitionState

logger = logging.getLogger(__name__)

async def acquire_pricing_page(url: str, company_name: str) -> Dict[str, Any]:
    """
    Orchestrates the ingestion of a pricing target.
    Delegates network acquisition to the BrowserPool.
    Returns a raw snapshot payload ready for extraction.
    """
    logger.info(f"Initiating pricing acquisition for {company_name} at {url}")
    
    # 1. Network Acquisition via Kernel
    state, raw_html, raw_text, fetch_duration, runtime_version = await browser_pool.fetch_page(url=url)
    
    # 2. Package Raw Snapshot
    raw_payload = {
        "company": company_name,
        "target_url": url,
        "acquisition_state": state,
        "raw_html": raw_html,
        "raw_text": raw_text,
        "provenance": {
            "fetch_duration_ms": fetch_duration,
            "browser_runtime_version": runtime_version,
            "retry_count": 0 if state == AcquisitionState.ACQUISITION_COMPLETE else 1,
            "acquisition_node": "nexus-primary-mesh"
        }
    }
    
    if state != AcquisitionState.ACQUISITION_COMPLETE:
        logger.warning(f"Acquisition for {company_name} finished with state: {state}")
        
    return raw_payload
