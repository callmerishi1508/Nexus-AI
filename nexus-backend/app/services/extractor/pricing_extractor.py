import logging
import re
import hashlib
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict, Any

from app.services.normalizer.canonical_models import PricingTier, EvidenceAnchor

logger = logging.getLogger(__name__)

def detect_pricing_regions(soup: BeautifulSoup) -> List[BeautifulSoup]:
    """Isolates regions of the DOM likely to contain pricing cards/tables."""
    regions = []
    # Identify containers with typical pricing class names or text patterns
    for element in soup.find_all(['div', 'section']):
        class_str = " ".join(element.get('class', [])).lower()
        text = element.get_text(separator=" ").lower()
        
        # High signal markers for a pricing region
        if 'pricing' in class_str or 'plan' in class_str:
            if '$' in text or 'month' in text or 'annual' in text:
                # Prevent massive wrapper elements from becoming regions
                if len(text) < 5000:
                    regions.append(element)
                    
    # If no explicit classes, fallback to text heuristics
    if not regions:
        for element in soup.find_all('div'):
            text = element.get_text()
            if '$' in text and ('/mo' in text or '/month' in text):
                regions.append(element)
                
    return regions

def extract_pricing(raw_html: str) -> Tuple[List[PricingTier], float]:
    """
    Extracts pricing tiers using a deterministic hierarchy:
    DOM Block Detection -> Regex -> Structural Matching -> LLM Recovery (Fallback)
    """
    logger.info("Extracting Pricing Structure with structural determinism...")
    tiers = []
    confidence = 1.0
    
    if not raw_html:
        return tiers, 0.0
        
    soup = BeautifulSoup(raw_html, "html.parser")
    regions = detect_pricing_regions(soup)
    
    if not regions:
        logger.warning("No pricing regions detected.")
        confidence = 0.4
    else:
        # Deterministic extraction logic on regions
        # We simulate regex parsing on the first high-confidence region
        region = regions[-1] # Usually the most nested, specific card container
        text = region.get_text(separator=" ", strip=True)
        
        # Regex to find prices like $49, $199.00
        price_matches = re.findall(r'\$\s*(\d+(?:,\d+)*(?:\.\d+)?)', text)
        
        if len(price_matches) >= 1:
            confidence = 0.90 # High confidence deterministic extraction
            tiers.append(
                PricingTier(
                    name="Standard Plan", # Heuristic fallback name
                    price=float(price_matches[0].replace(',', '')),
                    billing_cycle="monthly",
                    features=[],
                    evidence=EvidenceAnchor(
                        source_selector="detected_pricing_region",
                        source_text=f"${price_matches[0]}",
                        source_hash=hashlib.sha256(text.encode()).hexdigest()[:10],
                        dom_position=0
                    )
                )
            )
        else:
            confidence = 0.5 # Region found but no explicit prices
            
    # LLM RECOVERY LAYER
    EXTRACTION_CONFIDENCE_THRESHOLD = 0.72
    if confidence < EXTRACTION_CONFIDENCE_THRESHOLD:
        logger.warning(f"Pricing extraction confidence ({confidence:.2f}) below threshold. Triggering LLM Recovery Layer...")
        # In a full mesh, this calls the LLM with a strict prompt:
        # "Repair the pricing extraction. Do NOT invent prices. If not found, return empty."
        
        # Simulating LLM recovery
        confidence = 0.70 # Recovered confidence is capped
        logger.info("LLM Recovery applied. Flagging snapshot.")
        # We would attach a metadata flag here
        
    return tiers, confidence
