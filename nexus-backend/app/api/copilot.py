from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import get_db
from app.services.graph.query import export_graph_state
from app.services.copilot.context_builder import context_builder
from app.services.inference_router import inference_router
from app.api.dependencies import get_tenant
import json

router = APIRouter()

class CopilotQueryRequest(BaseModel):
    query: str
    persona: str
    sector: str
    timestamp: Optional[str] = None
    
class CopilotExplainRequest(BaseModel):
    node_id: str
    persona: str
    timestamp: Optional[str] = None

@router.post("/ask")
async def ask_copilot(req: CopilotQueryRequest, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant)):
    target_dt = None
    if req.timestamp:
        from dateutil.parser import parse
        target_dt = parse(req.timestamp)
        
    graph_state = await export_graph_state(db, tenant_id, target_dt)
    
    # Compress Graph State into Bounded Context
    context = context_builder.build_context(graph_state, req.persona)
    
    system_prompt = f"""
You are the {req.persona} Agent embedded within the NEXUS Institutional Cognitive Engine.
Your role is to act as an Institutional Copilot answering strategic queries.

CRITICAL RULES:
1. Use the provided CONTEXT as your primary source of truth, but you may augment it with your own general knowledge to provide a comprehensive answer.
2. Embody the {req.persona} persona (e.g., if CEO, focus on high-level market impact; if Trader, focus on volatility and pricing).
3. The user is currently viewing the {req.sector} sector. Your response MUST focus primarily on intelligence related to the {req.sector} sector. Ignore graph context unrelated to {req.sector}.

--- CONTEXT ---
Graph Summary: {context['graph_summary']}
Sector Emergence: {context['sector_emergence']}
Trajectory Summary: {context['trajectory_summary']}
Raw Evidence Count: {context['raw_evidence_count']}
"""
    
    result = await inference_router.route_inference(
        prompt=req.query,
        system_prompt=system_prompt,
        structured_schema={
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "confidence_score": {"type": "integer"},
                "evidence_anchors": {"type": "array", "items": {"type": "string"}},
                "strategic_directive": {"type": "string"}
            },
            "required": ["answer", "confidence_score", "evidence_anchors", "strategic_directive"]
        }
    )
    
    raw_content = result["content"].replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(raw_content)
    except Exception:
        # Fallback if json parsing fails
        parsed = {
            "answer": "Failed to parse deterministic JSON from inference.",
            "confidence_score": 0,
            "evidence_anchors": [],
            "strategic_directive": "Re-run query."
        }
    
    parsed["provider"] = result["provider"]
    return parsed


@router.post("/explain")
async def explain_node(req: CopilotExplainRequest, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant)):
    target_dt = None
    if req.timestamp:
        from dateutil.parser import parse
        target_dt = parse(req.timestamp)
        
    graph_state = await export_graph_state(db, tenant_id, target_dt)
    
    # Try to find the specific node
    target_node = None
    for n in graph_state.get("nodes", []):
        if n["name"] == req.node_id or str(n["id"]) == req.node_id:
            target_node = n
            break
            
    if not target_node:
        return {
            "answer": f"Node '{req.node_id}' could not be located in the current temporal graph.",
            "confidence_score": 0,
            "evidence_anchors": [],
            "strategic_directive": ""
        }
        
    context = context_builder.build_context(graph_state, req.persona)
    
    system_prompt = f"""
You are the NEXUS Institutional Copilot. The user has clicked on a Graph Node: '{target_node['name']}' (Type: {target_node['type']}).
Explain WHY this node exists in the current temporal graph.

CRITICAL RULES:
1. Explain its origin using the provided CONTEXT.
2. Be concise and authoritative. 

--- TARGET NODE ---
{json.dumps(target_node, indent=2)}

--- CONTEXT ---
Graph Summary: {context['graph_summary']}
Trajectory Summary: {context['trajectory_summary']}
"""

    result = await inference_router.route_inference(
        prompt=f"Explain the provenance and significance of node {target_node['name']}.",
        system_prompt=system_prompt,
        structured_schema={
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "confidence_score": {"type": "integer"},
                "evidence_anchors": {"type": "array", "items": {"type": "string"}},
                "strategic_directive": {"type": "string"}
            },
            "required": ["answer", "confidence_score", "evidence_anchors", "strategic_directive"]
        }
    )
    
    raw_content = result["content"].replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(raw_content)
    except Exception:
        parsed = {
            "answer": "Failed to parse deterministic JSON from inference.",
            "confidence_score": 0,
            "evidence_anchors": [],
            "strategic_directive": "Re-run query."
        }
    
    parsed["provider"] = result["provider"]
    return parsed
