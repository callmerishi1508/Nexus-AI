from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import uuid
import datetime

class EventMode(str, Enum):
    LIVE = "LIVE"
    REPLAY = "REPLAY"
    CHAOS = "CHAOS"
    SIMULATION = "SIMULATION"

class LifecycleState(str, Enum):
    INGESTED = "INGESTED"
    PARSED = "PARSED"
    CORRELATED = "CORRELATED"
    GRAPHED = "GRAPHED"
    SYNTHESIZED = "SYNTHESIZED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    VERIFIED = "VERIFIED"
    EXECUTIVE_BRIEFED = "EXECUTIVE_BRIEFED"
    ARCHIVED = "ARCHIVED"

class GovernanceState(str, Enum):
    PENDING = "PENDING"
    ESCALATED = "ESCALATED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"

class CanonicalIntelligenceEvent(BaseModel):
    """
    The Institutional Cognition Schema.
    Ensures coherence across graph, governance, synthesis, telemetry, and SSE feeds.
    """
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    correlation_id: Optional[str] = None
    sector: str
    target: str # E.g., Notion, ChatGPT
    
    # Priority & Trust Scoring
    priority_score: float = 0.0
    integrity_score: float = 0.0
    confidence: float = 0.0
    evidence_density: float = 0.0
    lineage_depth: int = 0
    replayability: float = 0.0
    
    # Evidentiary Support
    evidence_anchors: List[str] = Field(default_factory=list)
    source_nodes: List[str] = Field(default_factory=list)
    temporal_support: str = "CURRENT"
    reasoning_scope: str = "LOCAL"
    
    # State & Mode Tracking
    governance_state: str = GovernanceState.PENDING.value
    event_lifecycle_state: str = LifecycleState.INGESTED.value
    event_mode: str = EventMode.LIVE.value
    
    # Payload Context
    action: str # E.g., "DIFFING", "SYNTHESIZED"
    message: str # Human-readable log
    payload: dict = Field(default_factory=dict) # e.g. the diff, the extracted JSON, or the strategic_narrative
    
    constitution_version: str = "1.0.0"
    schema_epoch: str = "EPOCH_3"
    governance_epoch: str = "EPOCH_3"
    integrity_version: str = "v1"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")

# ---------------------------------------------------------
# Phase 17: Canonical Intelligence Models
# ---------------------------------------------------------

class DegradedState(str, Enum):
    OK = "OK"
    NO_DATA = "NO_DATA"
    PARTIAL_INTELLIGENCE = "PARTIAL_INTELLIGENCE"
    DEGRADED_PROJECTION = "DEGRADED_PROJECTION"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"

class StrategicSignal(BaseModel):
    """Primitive signal extracted from raw telemetry/diffs."""
    signal_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    trace_id: str
    type: str # e.g., "PRICING_COMPRESSION"
    confidence: float
    metadata: dict = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")

class TemporalCompression(BaseModel):
    """Compressed executive summary of a signal trajectory."""
    summary: str
    timeframe: str
    dominant_trend: str
    signal_count: int

class InterpretationProvenance(BaseModel):
    """Explains why a persona interpreted a signal a certain way."""
    dominant_trend: str
    weight_applied: float
    full_ontology_weights: dict

class InterpretationResult(BaseModel):
    """Subjective lens applied over objective truth."""
    persona_applied: str
    interpretive_summary: str
    interpretation_provenance: InterpretationProvenance

class TrajectoryProjection(BaseModel):
    """
    The Canonical Intelligence Object.
    Unified structure for frontend consumption.
    """
    company: str
    trace_id: str
    degraded_state: DegradedState = DegradedState.OK
    trajectory_compression: Optional[TemporalCompression] = None
    raw_signal_count: int = 0
    persona_interpretation: Optional[InterpretationResult] = None
    cached: bool = False

