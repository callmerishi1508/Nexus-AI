import copy
from typing import Dict, Optional
from pydantic import BaseModel, Field

class PersonaSnapshot(BaseModel):
    """
    Immutable representation of a persona's cognitive lens.
    Versioned to preserve replay fidelity.
    """
    persona_id: str
    version: str = "1.0.0"
    description: str
    weights: Dict[str, float]

    class Config:
        frozen = True  # Ensures immutability

class PersonaRegistry:
    """
    Dynamic Persona Registry.
    Loads and serves versioned persona snapshots.
    """
    def __init__(self):
        # In a real enterprise system, these would load from DB/Config
        self._personas: Dict[str, PersonaSnapshot] = {
            "CEO": PersonaSnapshot(
                persona_id="CEO",
                description="Strategic Moat & Value Preservation",
                weights={
                    "market_retreat": 1.5,
                    "aggressive_expansion": 1.5,
                    "pricing_compression": 1.2,
                    "feature_escalation": 0.8,
                    "volatility": 0.5,
                    "opportunity": 0.8
                }
            ),
            "TRADER": PersonaSnapshot(
                persona_id="TRADER",
                description="Momentum & Volatility Exploitation",
                weights={
                    "market_retreat": 0.5,
                    "aggressive_expansion": 1.2,
                    "pricing_compression": 1.5,
                    "feature_escalation": 0.5,
                    "volatility": 1.8,
                    "opportunity": 1.5
                }
            ),
            "CTO": PersonaSnapshot(
                persona_id="CTO",
                description="Technical Velocity & Feature Moat",
                weights={
                    "market_retreat": 0.8,
                    "aggressive_expansion": 0.8,
                    "pricing_compression": 0.5,
                    "feature_escalation": 1.8,
                    "volatility": 0.5,
                    "opportunity": 0.5
                }
            ),
            "PM": PersonaSnapshot(
                persona_id="PM",
                description="Product Expansion & User Acquisition",
                weights={
                    "market_retreat": 1.0,
                    "aggressive_expansion": 1.0,
                    "pricing_compression": 1.0,
                    "feature_escalation": 1.5,
                    "volatility": 0.5,
                    "opportunity": 1.0
                }
            )
        }
        
    def get_persona(self, persona_id: str) -> Optional[PersonaSnapshot]:
        """Returns the immutable persona snapshot."""
        return self._personas.get(persona_id.upper())

    def register_persona(self, snapshot: PersonaSnapshot):
        """Register a new persona snapshot dynamically."""
        self._personas[snapshot.persona_id.upper()] = snapshot

# Global Registry Instance
registry = PersonaRegistry()
