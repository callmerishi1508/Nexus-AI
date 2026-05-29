import json
import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import GovernanceReview
from app.services.graph.query import export_graph_state
from app.services.inference_router import inference_router
from app.config.settings import settings

logger = logging.getLogger(__name__)

class StrategicSynthesisEngine:
    def __init__(self):
        self.MIN_EVIDENCE_COUNT = settings.INTEGRITY_MIN_EVIDENCE_COUNT
        self.MIN_CONVERGENCE_SCORE = settings.INTEGRITY_MIN_CONVERGENCE_SCORE

    def _assess_evidence_sufficiency(self, graph_state: Dict[str, Any]) -> bool:
        edges = graph_state.get("edges", [])
        
        # We need at least MIN_EVIDENCE_COUNT edges
        if len(edges) < self.MIN_EVIDENCE_COUNT:
            return False
            
        # We need at least one high-confidence convergence event
        has_strong_convergence = False
        for edge in edges:
            if edge.get("confidence", 0) >= self.MIN_CONVERGENCE_SCORE:
                has_strong_convergence = True
                break
                
        return has_strong_convergence

    def _get_deterministic_fallback(self, graph_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Template-based deterministic synthesis recovery.
        Used if LLM inference fails, ensuring continuity and explainability.
        """
        nodes = graph_state.get("nodes", [])
        edges = graph_state.get("edges", [])
        
        sectors = [n["name"] for n in nodes if n.get("type") == "Sector"]
        companies = [n["name"] for n in nodes if n.get("type") == "Company"]
        trends = [n["name"] for n in nodes if n.get("type") == "SectorTrend"]
        
        sector_str = sectors[0] if sectors else "Multiple Sectors"
        evidence_ids = [n["id"] for n in nodes] + [f"edge_{e['source']}_{e['target']}" for e in edges]
        
        narrative = f"Detected sustained convergence across {len(companies)} monitored entities within the {sector_str}. "
        if trends:
            narrative += f"Primary catalyst identified as: {', '.join(trends)}. "
        narrative += "Strategic trajectory indicates increasing market alignment."

        return {
            "strategic_narrative": narrative,
            "synthesis_confidence": 75,
            "evidence_count": len(edges),
            "temporal_support": "MEDIUM",
            "contradictions_detected": [],
            "reasoning_scope": "SECTOR_LEVEL",
            "evidence_anchors": evidence_ids[:5],
            "provider": "DETERMINISTIC_RECOVERY"
        }

    async def generate_brief(self, db: AsyncSession, tenant_id: str, timestamp: Any = None) -> Dict[str, Any]:
        # Gather escalating intelligence for this specific tenant
        reviews = await db.execute(
            select(GovernanceReview)
            .where(GovernanceReview.status == "ESCALATED")
            .where(GovernanceReview.tenant_id == tenant_id)
            .order_by(GovernanceReview.priority_score.desc())
        )
        graph_state = await export_graph_state(db, tenant_id, timestamp)
        
        if not self._assess_evidence_sufficiency(graph_state):
            logger.warning(
                f"[CONSTITUTION] Synthesis blocked:\n"
                f"reason=INSUFFICIENT_EVIDENCE_DENSITY\n"
                f"edge_count={len(graph_state.get('edges', []))}\n"
                f"required_threshold={self.MIN_EVIDENCE_COUNT}"
            )
            return {
                "strategic_narrative": "Insufficient strategic evidence for synthesis.",
                "synthesis_confidence": 0,
                "evidence_count": len(graph_state.get("edges", [])),
                "temporal_support": "WEAK",
                "contradictions_detected": [],
                "reasoning_scope": "NONE",
                "evidence_anchors": [],
                "provider": "SYSTEM"
            }

        prompt = f"""
        You are a Strategic Market Intelligence Analyst.
        Your task is to synthesize the provided intelligence graph state into a concise, executive-level strategic narrative.
        
        CRITICAL RULES:
        1. Synthesize ONLY from the provided evidence. DO NOT invent facts, news, or trends.
        2. Identify the reasoning scope (e.g. SECTOR_LEVEL, MARKET_LEVEL).
        3. Anchor your claims by returning the node IDs or edge references in 'evidence_anchors'.
        4. Detect contradictions (e.g. one entity doing pricing expansion, another doing pricing contraction).
        
        EVIDENCE (Graph State JSON):
        {json.dumps(graph_state, indent=2)}
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "strategic_narrative": "<2-3 paragraph executive summary>",
            "synthesis_confidence": <0-100 integer>,
            "evidence_count": <integer>,
            "temporal_support": "<STRONG|MEDIUM|WEAK>",
            "contradictions_detected": ["<list of contradictions>", ...],
            "reasoning_scope": "<SECTOR_LEVEL|TARGET_LEVEL|MARKET_LEVEL>",
            "evidence_anchors": ["<node_id or edge_id>", ...]
        }}
        """

        try:
            # Evidence-Constrained LLM Inference
            result = await inference_router.route_inference(
                prompt=prompt,
                system_prompt="You are an evidence-constrained intelligence synthesizer. Output strictly in JSON format as requested.",
                structured_schema={
                    "type": "object",
                    "properties": {
                        "strategic_narrative": {"type": "string"},
                        "synthesis_confidence": {"type": "integer"},
                        "evidence_count": {"type": "integer"},
                        "temporal_support": {"type": "string"},
                        "contradictions_detected": {"type": "array", "items": {"type": "string"}},
                        "reasoning_scope": {"type": "string"},
                        "evidence_anchors": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["strategic_narrative", "synthesis_confidence", "evidence_count", "temporal_support", "contradictions_detected", "reasoning_scope", "evidence_anchors"]
                }
            )
            
            raw_content = result["content"].replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw_content)
            parsed["provider"] = result["provider"]
            
            # Calculate Intelligence Priority Weighting
            priority_score = int(parsed.get("synthesis_confidence", 0)) * 0.5 + int(parsed.get("evidence_count", 0)) * 10
            
            # Form Governance Review Item
            review_item = GovernanceReview(
                status="REVIEW_REQUIRED",
                brief_data=json.dumps(parsed),
                priority_score=priority_score,
                review_reason=f"System generated {parsed.get('reasoning_scope', 'UNKNOWN')} synthesis.",
                risk_level="MEDIUM",
                evidence_anchors=json.dumps(parsed.get("evidence_anchors", []))
            )
            
            db.add(review_item)
            await db.commit()
            
            return parsed
            
        except Exception as e:
            logger.error(f"Synthesis inference failed: {e}")
            logger.warning(
                f"[CONSTITUTION] Synthesis fallback activated:\n"
                f"reason=INFERENCE_FAILURE\n"
                f"error={str(e)}"
            )
            fallback = self._get_deterministic_fallback(graph_state)
            
            # Persist fallback
            review_item = GovernanceReview(
                status="REVIEW_REQUIRED",
                brief_data=json.dumps(fallback),
                priority_score=fallback.get("synthesis_confidence", 0) * 0.5,
                review_reason="Deterministic fallback synthesis.",
                risk_level="LOW",
                evidence_anchors=json.dumps(fallback.get("evidence_anchors", []))
            )
            db.add(review_item)
            await db.commit()
            
            return fallback

synthesis_engine = StrategicSynthesisEngine()
