import logging
from bs4 import BeautifulSoup
from typing import Optional

logger = logging.getLogger(__name__)

def calculate_dom_stability(current_html: str, historical_html: Optional[str]) -> float:
    """
    Calculates DOM Stability Score before passing to the Diff Engine.
    Prevents false intelligence events triggered by A/B tests or generic site redesigns.
    
    1.0 = Highly Stable
    0.0 = Completely Rewritten
    """
    if not historical_html:
        return 1.0 # First time seeing this target
        
    try:
        curr_soup = BeautifulSoup(current_html, "html.parser")
        hist_soup = BeautifulSoup(historical_html, "html.parser")
        
        # 1. Structural Entropy (div count parity)
        curr_divs = len(curr_soup.find_all("div"))
        hist_divs = len(hist_soup.find_all("div"))
        
        div_ratio = min(curr_divs, hist_divs) / max(curr_divs, hist_divs) if max(curr_divs, hist_divs) > 0 else 1.0
        
        # 2. Text Volume Parity
        curr_text = len(curr_soup.get_text(strip=True))
        hist_text = len(hist_soup.get_text(strip=True))
        text_ratio = min(curr_text, hist_text) / max(curr_text, hist_text) if max(curr_text, hist_text) > 0 else 1.0
        
        # In a full production scenario, this compares hashed CSS selectors for vital containers.
        stability = (div_ratio * 0.6) + (text_ratio * 0.4)
        
        logger.info(f"DOM Stability Score: {stability:.2f}")
        return float(stability)
        
    except Exception as e:
        logger.error(f"Failed to calculate DOM stability: {e}")
        return 0.5 # Degraded confidence
