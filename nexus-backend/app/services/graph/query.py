from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import GraphNode, GraphEdge
from typing import Optional
from datetime import datetime

async def export_graph_state(session: AsyncSession, tenant_id: str, timestamp: Optional[datetime] = None):
    # Fetch all nodes
    node_query = select(GraphNode).where(GraphNode.tenant_id == tenant_id)
    if timestamp:
        node_query = node_query.where(GraphNode.created_at <= timestamp)
        
    nodes_result = await session.execute(node_query)
    nodes = nodes_result.scalars().all()
    
    # Fetch all edges
    edge_query = select(GraphEdge).where(GraphEdge.tenant_id == tenant_id)
    if timestamp:
        edge_query = edge_query.where(GraphEdge.created_at <= timestamp)
        
    edges_result = await session.execute(edge_query)
    edges = edges_result.scalars().all()
    
    return {
        "nodes": [
            {
                "id": n.id,
                "type": n.node_type,
                "name": n.name,
                "sector": n.sector,
                "attributes": n.attributes
            } for n in nodes
        ],
        "edges": [
            {
                "id": e.id,
                "source": e.source_id,
                "target": e.target_id,
                "relation": e.relationship_type,
                "strength": e.strength,
                "confidence": e.confidence,
                "last_updated": e.last_updated_at.isoformat() + "Z"
            } for e in edges
        ]
    }
