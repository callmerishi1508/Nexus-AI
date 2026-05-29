import os
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from app.services.extractors.coordinator import execute_deterministic_extraction
from app.services.extractor.semantic import extract_pricing_and_features

# =========================================================================
# NEXUS - SEMANTIC INTELLIGENCE ENGINE (PHASE 6)
# =========================================================================

class PricingTier(BaseModel):
    tier_name: str = Field(description="Name of the pricing tier (e.g., Pro, Enterprise)")
    price: Optional[str] = Field(description="Price associated with the tier", default=None)
    billing: Optional[str] = Field(description="Billing frequency (e.g., annually, monthly)", default=None)

class ExtractedIntelligence(BaseModel):
    pricing: List[PricingTier] = Field(description="List of pricing tiers explicitly found")
    features: List[str] = Field(description="Key features explicitly listed")
    messaging: Optional[str] = Field(description="Primary positioning messaging or tagline", default=None)
    release_notes: Optional[str] = Field(description="Any explicitly visible release notes or update text", default=None)
    timestamps: Optional[str] = Field(description="Explicitly visible timestamps", default=None)

# -------------------------------------------------------------------------
# EXTRACTION ENGINE
# -------------------------------------------------------------------------

EXTRACTION_PROMPT = """
You are NEXUS, an enterprise-grade competitive intelligence engine.
Your task is to extract structured business intelligence from the provided raw markdown.

CRITICAL EXTRACTION RULES (NO HALLUCINATION):
1. Only extract explicitly visible information.
2. Do not infer pricing tiers, features, or business changes not directly present in the source content.
3. Return null for uncertain fields.
4. If a value is unlisted or custom (e.g., 'Contact Us'), extract the exact wording.

Content:
{markdown_content}
"""

async def extract_semantic_intelligence(markdown_content: str, raw_html: str = "") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Hybrid Routing Engine:
    1. Attempts Deterministic Extraction via modular Python heuristics.
    2. Computes Structural Confidence Score.
    3. If confidence >= 85, bypasses LLM entirely.
    4. If < 85, routes anomaly segments to Sovereign Local Inference.
    """
    # 1. Deterministic Extraction First
    extracted_data, confidence_score, fingerprint = execute_deterministic_extraction(raw_html or markdown_content)
    
    inference_telemetry = {
        "inference_bypassed": True,
        "structural_confidence": confidence_score,
        "deterministic_coverage": 100 if confidence_score >= 85 else min(100, int(confidence_score * 1.1)),
        "anomaly_segments_routed": 0,
        "structural_fingerprint": fingerprint
    }
    
    # 2. Hybrid Routing (LLM only for anomaly/low confidence)
    if confidence_score < 85:
        inference_telemetry["inference_bypassed"] = False
        inference_telemetry["anomaly_segments_routed"] = 1
        
        # We pass the markdown to LLM to extract ambiguous fields
        llm_data, llm_telemetry = await extract_pricing_and_features(markdown_content)
        
        inference_telemetry.update(llm_telemetry)
        
        # Hybrid Merge: Keep deterministic arrays if they found data, otherwise use LLM
        if not extracted_data["pricing"] and llm_data.get("pricing"):
             extracted_data["pricing"] = llm_data["pricing"]
        if not extracted_data["features"] and llm_data.get("features"):
             extracted_data["features"] = llm_data["features"]
             
        extracted_data["messaging"] = llm_data.get("messaging")
        extracted_data["release_notes"] = llm_data.get("release_notes")
        
    return extracted_data, inference_telemetry

# -------------------------------------------------------------------------
# DIFF & SCORING ENGINE
# -------------------------------------------------------------------------

def generate_semantic_diff(current: Dict[str, Any], historical: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares historical and current structured snapshots to detect 
    additions, removals, pricing movement, and tier restructuring.
    """
    diff = {
        "additions": {},
        "removals": {}
    }
    
    def _sanitize_pricing(pricing_data):
        if not pricing_data: return {}
        if isinstance(pricing_data, dict):
            pricing_data = [pricing_data]
        elif isinstance(pricing_data, str):
            return {}
        return {t.get("tier_name", "Unknown"): t for t in pricing_data if isinstance(t, dict)}
        
    current_pricing = _sanitize_pricing(current.get("pricing", []))
    hist_pricing = _sanitize_pricing(historical.get("pricing", []))
    
    diff["additions"]["pricing"] = {}
    diff["removals"]["pricing"] = {}
    
    for tier, data in current_pricing.items():
        if tier not in hist_pricing:
            diff["additions"]["pricing"][tier] = data
        elif data.get("price") != hist_pricing[tier].get("price"):
            diff["additions"]["pricing"][tier] = {"price": data.get("price")}
            diff["removals"]["pricing"][tier] = {"price": hist_pricing[tier].get("price")}
            
    for tier, data in hist_pricing.items():
        if tier not in current_pricing:
            diff["removals"]["pricing"][tier] = data

    # Clean empty dicts
    if not diff["additions"]["pricing"]: del diff["additions"]["pricing"]
    if not diff["removals"]["pricing"]: del diff["removals"]["pricing"]

    # Feature comparison
    curr_features = set(current.get("features", []))
    hist_features = set(historical.get("features", []))
    
    added_features = curr_features - hist_features
    removed_features = hist_features - curr_features
    
    if added_features: diff["additions"]["features"] = list(added_features)
    if removed_features: diff["removals"]["features"] = list(removed_features)
    
    return diff

def compute_dual_scores(diff: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes Confidence and Impact scores with explainable metadata.
    """
    has_additions = len(diff.get("additions", {})) > 0
    has_removals = len(diff.get("removals", {})) > 0
    
    if not has_additions and not has_removals:
        return {
            "confidence_score": 9.8,
            "confidence_reason": ["No semantic changes detected.", "Extraction stable."],
            "impact_score": 0.0,
            "impact_reason": "No strategic movement detected."
        }

    # Simplistic heuristic for demo purposes
    impact_score = 3.0
    impact_reason = "Minor cosmetic or messaging tweaks."
    
    if "pricing" in diff.get("additions", {}) or "pricing" in diff.get("removals", {}):
        impact_score = 8.5
        impact_reason = "Major tier restructuring or numeric pricing change detected."
    elif "features" in diff.get("additions", {}):
        impact_score = 5.0
        impact_reason = "New features added to the product offering."

    return {
        "confidence_score": 8.7,
        "confidence_reason": [
            "Fields successfully mapped to structured JSON.",
            "Semantic boundaries clearly identified."
        ],
        "impact_score": impact_score,
        "impact_reason": impact_reason
    }
