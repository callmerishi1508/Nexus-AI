import logging
import re
import hashlib
from typing import List, Dict, Any, Tuple

from app.services.diff.thresholds import SignalSeverity

logger = logging.getLogger(__name__)

def canonicalize_feature(feature_text: str) -> Tuple[str, str]:
    """
    Normalizes a feature string for deterministic comparison.
    Strips whitespace, casing, punctuation, and common stopwords.
    Returns: (canonical_text, hash)
    """
    # 1. Lowercase and basic strip
    text = feature_text.lower().strip()
    
    # 2. Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # 3. Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # 4. Remove common meaningless stopwords (SaaS specific)
    stopwords = {"and", "the", "with", "for", "a", "an", "up", "to", "included"}
    words = text.split()
    canonical_words = [w for w in words if w not in stopwords]
    canonical_text = " ".join(canonical_words)
    
    # 5. Generate deterministic hash
    feature_hash = hashlib.sha256(canonical_text.encode()).hexdigest()[:12]
    
    return canonical_text, feature_hash

def calculate_jaccard(str1: str, str2: str) -> float:
    """Calculates Jaccard similarity between two strings based on word overlap."""
    set1 = set(str1.split())
    set2 = set(str2.split())
    
    if not set1 or not set2:
        return 0.0
        
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

def diff_features(historical_features: List[str], current_features: List[str]) -> List[Dict[str, Any]]:
    """
    Generates deterministic signals for feature changes.
    Does NOT use embeddings to preserve stability.
    """
    signals = []
    
    hist_canonical = {canonicalize_feature(f)[1]: f for f in historical_features}
    curr_canonical = {canonicalize_feature(f)[1]: f for f in current_features}
    
    hist_hashes = set(hist_canonical.keys())
    curr_hashes = set(curr_canonical.keys())
    
    # 1. Exact Removals
    removed_hashes = hist_hashes - curr_hashes
    
    # 2. Exact Additions
    added_hashes = curr_hashes - hist_hashes
    
    # 3. Fuzzy Matching (Did an addition actually just modify a removal?)
    true_removals = []
    for r_hash in removed_hashes:
        r_text, _ = canonicalize_feature(hist_canonical[r_hash])
        was_modified = False
        
        for a_hash in list(added_hashes):
            a_text, _ = canonicalize_feature(curr_canonical[a_hash])
            
            similarity = calculate_jaccard(r_text, a_text)
            if similarity > 0.6: # High semantic overlap
                signals.append({
                    "type": "FEATURE_MODIFIED",
                    "old_feature": hist_canonical[r_hash],
                    "new_feature": curr_canonical[a_hash],
                    "similarity": similarity,
                    "severity": SignalSeverity.LOW_SIGNAL
                })
                added_hashes.remove(a_hash)
                was_modified = True
                break
                
        if not was_modified:
            true_removals.append(r_hash)
            
    # Process final Additions and Removals
    for a_hash in added_hashes:
        signals.append({
            "type": "FEATURE_ADDED",
            "feature": curr_canonical[a_hash],
            "severity": SignalSeverity.MATERIAL
        })
        
    for r_hash in true_removals:
        signals.append({
            "type": "FEATURE_REMOVED",
            "feature": hist_canonical[r_hash],
            "severity": SignalSeverity.ESCALATE # Removing features is usually a massive signal
        })
        
    if signals:
        logger.info(f"Generated {len(signals)} semantic feature signals.")
        
    return signals
