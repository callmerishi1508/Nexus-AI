from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.config.versions import EXTRACTOR_VERSION, NORMALIZER_VERSION
from app.services.scraper.governance import AcquisitionState

class EvidenceAnchor(BaseModel):
    source_selector: str
    source_text: str
    source_hash: str
    dom_position: int

class PricingTier(BaseModel):
    name: str
    price: float
    currency: str = "USD"
    billing_cycle: str = "monthly"
    features: List[str] = []
    evidence: Optional[EvidenceAnchor] = None

class ReleaseNote(BaseModel):
    version: str
    date: str
    content: str
    type: str = "feature" # feature, bugfix, security
    evidence: Optional[EvidenceAnchor] = None

class Taxonomy(BaseModel):
    sector: str
    vertical: str
    target_audience: List[str] = []

class AcquisitionProvenance(BaseModel):
    acquisition_runtime: str
    browser_runtime_version: str
    fetch_duration_ms: int
    retry_count: int
    acquisition_node: str

class Metadata(BaseModel):
    source_url: str
    user_agent: str
    provenance: AcquisitionProvenance

class CanonicalMarketSnapshot(BaseModel):
    """
    The True Intelligence Source.
    Raw HTML is discarded after populating this model.
    All diffs and ontology impacts are calculated against this schema.
    """
    snapshot_id: str
    parent_snapshot_id: Optional[str] = None
    lineage_chain_id: str
    
    company: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Versioning for Replay Determinism
    extractor_version: str = EXTRACTOR_VERSION
    normalizer_version: str = NORMALIZER_VERSION
    ontology_version: str = "v1.0.0"
    ontology_interpretation_hash: Optional[str] = None
    
    # Governance & Stability
    acquisition_state: AcquisitionState = AcquisitionState.ACQUISITION_PENDING
    dom_stability_score: float = 1.0  # 1.0 = stable, 0.0 = completely changed
    extraction_confidence: float = 1.0 # 1.0 = precise selectors, 0.0 = fallback LLM guessing
    
    # Field-level Semantic Confidence
    pricing_confidence: float = 1.0
    feature_confidence: float = 1.0
    release_notes_confidence: float = 1.0
    metadata_confidence: float = 1.0
    
    # The Core Intelligence Payload
    pricing: List[PricingTier] = []
    features: List[str] = []
    release_notes: List[ReleaseNote] = []
    metadata: Metadata
    taxonomy: Taxonomy

