from enum import Enum
from typing import Dict, Any

class PersonaLens(str, Enum):
    CEO = "CEO"
    CTO = "CTO"
    TRADER = "TRADER"
    PM = "PM"
    GM = "GM"
    AGM = "AGM"
    EMPLOYEE = "EMPLOYEE"
    STOCK_BROKER = "STOCK_BROKER"
    INVESTMENT_BANKER = "INVESTMENT_BANKER"
    AI_RESEARCHER = "AI_RESEARCHER"
    AI_SCIENTIST = "AI_SCIENTIST"

# Cognitive Interpretation Configurations
PERSONA_CONFIGS = {
    PersonaLens.CEO: {
        "emphasis": ["market expansion", "revenue", "strategic moat"],
        "graph_weighting": "market_cap",
        "narrative_framing": "strategic_business_value"
    },
    PersonaLens.CTO: {
        "emphasis": ["architecture", "technical risk", "velocity"],
        "graph_weighting": "technical_debt",
        "narrative_framing": "technical_execution"
    },
    PersonaLens.TRADER: {
        "emphasis": ["volatility", "catalysts", "momentum"],
        "graph_weighting": "momentum",
        "narrative_framing": "price_action_catalysts"
    },
    PersonaLens.STOCK_BROKER: {
        "emphasis": ["volatility", "catalysts", "momentum"],
        "graph_weighting": "momentum",
        "narrative_framing": "price_action_catalysts"
    },
    PersonaLens.INVESTMENT_BANKER: {
        "emphasis": ["M&A opportunities", "financial health", "market consolidation"],
        "graph_weighting": "enterprise_value",
        "narrative_framing": "deal_flow_potential"
    },
    PersonaLens.PM: {
        "emphasis": ["feature adoption", "user friction", "roadmap execution"],
        "graph_weighting": "feature_density",
        "narrative_framing": "product_strategy"
    },
    PersonaLens.AI_SCIENTIST: {
        "emphasis": ["model architecture", "data moats", "compute efficiency"],
        "graph_weighting": "ai_capability",
        "narrative_framing": "technical_innovation"
    }
}

def apply_cognitive_lens(base_insights: Dict[str, Any], persona: PersonaLens) -> Dict[str, Any]:
    """
    Reframes base insights according to the selected persona lens.
    """
    config = PERSONA_CONFIGS.get(persona, PERSONA_CONFIGS[PersonaLens.CEO])
    
    reframed_insights = base_insights.copy()
    reframed_insights["cognitive_lens_applied"] = persona.value
    reframed_insights["emphasis_areas"] = config["emphasis"]
    
    # In a full implementation, the actual narrative would be dynamically generated or rewritten
    # based on these emphasis areas via the Scoring/Prediction layers.
    return reframed_insights
