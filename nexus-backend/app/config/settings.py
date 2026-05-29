from pydantic_settings import BaseSettings
from typing import Literal, Optional

class Settings(BaseSettings):
    # Bright Data Infrastructure
    BRIGHT_DATA_SCRAPING_BROWSER_URL: Optional[str] = None
    
    # Base Intervals
    SCHEDULER_BASE_INTERVAL_SEC: int = 300
    SCHEDULER_MIN_INTERVAL_SEC: int = 30
    
    # Decay Engine Thresholds
    DECAY_BASE_RATE: float = 0.05
    DECAY_PRUNE_THRESHOLD: float = 0.1
    
    # Trust & Integrity
    INTEGRITY_MAX_EVIDENCE_DENSITY: int = 5
    INTEGRITY_MAX_LINEAGE_DEPTH: int = 3
    INTEGRITY_DRIFT_THRESHOLD: int = 40  # Semantic drift confidence threshold
    INTEGRITY_MIN_EVIDENCE_COUNT: int = 3 # Minimum evidence for synthesis
    INTEGRITY_MIN_CONVERGENCE_SCORE: int = 70
    
    # Simulation Eligibility
    SIMULATION_MINIMUM_SNAPSHOTS: int = 3
    SIMULATION_MINIMUM_LINEAGE: int = 2
    
    # System Epochs
    CONSTITUTION_VERSION: str = "1.0.0"
    SCHEMA_EPOCH: str = "EPOCH_3"
    GOVERNANCE_EPOCH: str = "EPOCH_3"
    
    # Enforcements
    STRICT_SCHEMA_MODE: str = "SOFT"
    
    # Executional Boundaries
    MAX_PARALLEL_SANDBOXES: int = 3
    MAX_PENDING_SIMULATIONS: int = 10
    MAX_GRAPH_MUTATIONS: int = 50
    MAX_CONCURRENT_INFERENCE: int = 2
    
    # Standardized Institutional Vocabulary (Constants)
    STATE_ACTIVE: str = "ACTIVE"
    STATE_STABLE: str = "STABLE"
    STATE_ESCALATING: str = "ESCALATING"
    STATE_DEGRADED: str = "DEGRADED"
    STATE_GOVERNANCE_FROZEN: str = "GOVERNANCE_FROZEN"
    STATE_REPLAY: str = "REPLAY"
    STATE_SIMULATION: str = "SIMULATION"

    # Current System State
    SYSTEM_STATE: str = "ACTIVE"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
