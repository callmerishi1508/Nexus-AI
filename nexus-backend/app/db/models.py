from sqlalchemy import Column, String, Text, DateTime, MetaData, JSON, Integer, Float, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Index
import uuid
from datetime import datetime
import os

from dotenv import load_dotenv
load_dotenv()

# Stage 3: Deterministic SQLite Persistence
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nexus.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

class WebSnapshot(Base):
    __tablename__ = "web_snapshots"

    # Identity & Lineage Tracking
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, default="tenant_public", index=True)
    snapshot_version = Column(Integer, default=1, nullable=False)
    parent_snapshot_id = Column(String(36), nullable=True)
    
    # Target Information
    competitor_name = Column(String(100), nullable=False)
    source_url = Column(Text, nullable=False)
    
    # Forensic Metadata
    snapshot_status = Column(String(50), nullable=False, default="LIVE")
    integrity_score = Column(Float, nullable=True, default=0.0)
    lineage_depth = Column(Integer, default=0)
    fetch_source = Column(String(50), nullable=False, default="PLAYWRIGHT_CHROMIUM")
    browser_context_id = Column(String(50), nullable=True)
    parse_duration = Column(Integer, nullable=True) # in milliseconds
    recovery_origin = Column(String(50), nullable=True)
    
    # Replay Fingerprints
    replay_checksum = Column(String(64), nullable=True)
    replay_timestamp = Column(String(50), nullable=True)
    replay_graph_hash = Column(String(64), nullable=True)
    
    # System Epochs
    constitution_version = Column(String(20), default="1.0.0")
    schema_epoch = Column(String(20), default="EPOCH_3")
    governance_epoch = Column(String(20), default="EPOCH_3")
    
    # Intelligence Data
    scraped_data = Column(JSON, nullable=False)
    dom_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

# Required Index
Index('idx_competitor_created_at', WebSnapshot.competitor_name, WebSnapshot.created_at.desc())

# =========================================================================
# EPOCH 4: TARGET GOVERNANCE
# =========================================================================

class TargetRegistry(Base):
    __tablename__ = "target_registry"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, default="tenant_public", index=True)
    company_name = Column(String(100), nullable=False)
    normalized_name = Column(String(100), nullable=False, unique=True)
    url = Column(Text, nullable=False)
    sector = Column(String(100), nullable=False)
    
    # Lifecycle States: SUBMITTED, VALIDATING, GOVERNANCE_PENDING, APPROVED, ACTIVE, REJECTED
    onboarding_state = Column(String(50), default="SUBMITTED", nullable=False)
    validation_state = Column(String(50), default="PENDING", nullable=False)
    scheduler_assignment_state = Column(String(50), default="UNASSIGNED", nullable=False)
    
    # Validation Data
    validation_report = Column(JSON, nullable=True)
    
    # Timestamps & Governance
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    governance_owner = Column(String(100), nullable=True)
    
    # Epoch Consistency
    target_epoch = Column(String(20), default="EPOCH_4")
    
    # Scheduler Configuration
    polling_interval = Column(Integer, default=300)
    target_hash = Column(String(64), nullable=True)
    active = Column(Integer, default=0) # 0 or 1
    integrity_score = Column(Float, default=100.0)

# =========================================================================
# STAGE 8: INTELLIGENCE GRAPH INFRASTRUCTURE
# =========================================================================

class GraphNode(Base):
    __tablename__ = "graph_nodes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, default="tenant_public", index=True)
    node_type = Column(String(50), nullable=False) # Company, Feature, PricingModel, SectorTrend
    name = Column(String(100), nullable=False)
    sector = Column(String(100), nullable=True)
    attributes = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
Index('idx_graph_node_type', GraphNode.node_type)
Index('idx_graph_node_name', GraphNode.name)

class GraphEdge(Base):
    __tablename__ = "graph_edges"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, default="tenant_public", index=True)
    source_id = Column(String(36), ForeignKey('graph_nodes.id'), nullable=False)
    target_id = Column(String(36), ForeignKey('graph_nodes.id'), nullable=False)
    
    relationship_type = Column(String(50), nullable=False) # competing_with, mirrors_pricing, accelerating_AI
    
    # Weighted Intelligence
    strength = Column(Float, default=1.0) # 0.0 to 1.0, Decay engine affects this
    confidence = Column(Float, default=100.0) # 0.0 to 100.0
    evidence_density = Column(Float, default=1.0)
    replayability = Column(Float, default=100.0)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class GovernanceReview(Base):
    __tablename__ = "governance_reviews"
    
    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    tenant_id = Column(String(50), nullable=False, default="tenant_public", index=True)
    status = Column(String, default="REVIEW_REQUIRED", index=True) # REVIEW_REQUIRED, ESCALATED, VERIFIED, EXECUTIVE_BRIEFED, REJECTED, ARCHIVED
    brief_data = Column(String) # JSON payload of the synthesis
    priority_score = Column(Float, default=0.0) # Weighted intelligence priority
    
    # Governance Metadata
    review_reason = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)
    escalation_priority = Column(String, nullable=True)
    reviewer_notes = Column(String, nullable=True)
    evidence_anchors = Column(String) # JSON array of IDs
    
    # Integrity Tracking
    integrity_score = Column(Float, default=0.0)
    event_lifecycle_state = Column(String, default="SYNTHESIZED")
    lineage_depth = Column(Integer, default=0)
    replayability = Column(Float, default=0.0)
    
    # System Epochs
    constitution_version = Column(String(20), default="1.0.0")
    schema_epoch = Column(String(20), default="EPOCH_3")
    governance_epoch = Column(String(20), default="EPOCH_3")
    
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat() + "Z")

class PlatformSnapshot(Base):
    __tablename__ = "platform_snapshots"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, default="tenant_public", index=True)
    snapshot_type = Column(String(50), nullable=False) # e.g. "FULL_STATE"
    description = Column(String(200), nullable=True)
    
    # Payload of the entire state
    state_payload = Column(JSON, nullable=False)
    
    # System Epochs at time of snapshot
    constitution_version = Column(String(20), default="1.0.0")
    schema_epoch = Column(String(20), default="EPOCH_3")
    governance_epoch = Column(String(20), default="EPOCH_3")
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class StrategicSimulation(Base):
    __tablename__ = "strategic_simulations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, default="tenant_public", index=True)
    
    # Input assumptions
    target_node_id = Column(String(36), nullable=False)
    mutation_type = Column(String(100), nullable=False)
    temporal_horizon = Column(String(20), nullable=False) # SHORT, MEDIUM, LONG
    
    # Hashes & Replayability
    simulation_hash = Column(String(64), nullable=False)
    trajectory_hash = Column(String(64), nullable=False)
    constraint_hash = Column(String(64), nullable=False)
    projection_epoch = Column(String(20), default="EPOCH_3")
    
    # Core outputs
    trajectory_type = Column(String(50), nullable=False) # REINFORCEMENT, DIVERGENCE, etc.
    synthesis_payload = Column(JSON, nullable=False)
    
    # Integrity Metrics
    confidence = Column(Float, nullable=False)
    stability_score = Column(Float, nullable=False)
    contradiction_pressure = Column(Float, nullable=False)
    evidence_density = Column(Float, nullable=False)
    
    # Governance states
    governance_state = Column(String(50), default="SIMULATED", index=True)
    
    # System Epochs
    constitution_version = Column(String(20), default="1.0.0")
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
Index('idx_graph_edge_source', GraphEdge.source_id)
Index('idx_graph_edge_target', GraphEdge.target_id)
Index('idx_graph_edge_relation', GraphEdge.relationship_type)
Index('idx_sim_gov_state', StrategicSimulation.governance_state)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
