import logging
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.services.diff.thresholds import SignalSeverity

logger = logging.getLogger(__name__)

class MaterializedSignal(BaseModel):
    """
    The atom of institutional intelligence.
    Raw diffs are converted into Materialized Signals before ontology consumes them.
    """
    signal_type: str # e.g. PRICING_COMPRESSION, FEATURE_REMOVED
    severity: SignalSeverity
    confidence: float
    impact: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    originating_snapshot_id: str
    
    # Context payload for the specific event
    context: dict = {}
    
    @property
    def age_days(self) -> float:
        """Calculates the age of the signal in days."""
        delta = datetime.now(timezone.utc) - self.timestamp
        return max(0.0, delta.total_seconds() / 86400.0)
        
    @property
    def decay_factor(self) -> float:
        """
        Calculates Temporal Decay Mathematics.
        Older events lose influence to prevent them from poisoning current ontology states.
        
        < 1 day: 1.0 (100%)
        ~ 7 days: 0.80 (80%)
        ~ 30 days: 0.45 (45%)
        > 90 days: 0.15 (15% floor)
        """
        days = self.age_days
        
        if days <= 1:
            return 1.0
        elif days <= 7:
            # Linear decay from 1.0 to 0.8
            return 1.0 - ((days - 1) / 6.0) * 0.20
        elif days <= 30:
            # Linear decay from 0.8 to 0.45
            return 0.80 - ((days - 7) / 23.0) * 0.35
        elif days <= 90:
            # Linear decay from 0.45 to 0.15
            return 0.45 - ((days - 30) / 60.0) * 0.30
        else:
            return 0.15
