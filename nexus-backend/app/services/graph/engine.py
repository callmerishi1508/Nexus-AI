import logging
from enum import Enum
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class NodeType(str, Enum):
    COMPANY = "COMPANY"
    SIGNAL = "SIGNAL"
    ONTOLOGY_STATE = "ONTOLOGY_STATE"
    SECTOR_SIGNAL = "SECTOR_SIGNAL"
    SNAPSHOT = "SNAPSHOT"

class EdgeType(str, Enum):
    GENERATED_FROM = "GENERATED_FROM"    # Signal <- Snapshot
    PRECEDES = "PRECEDES"                # Signal -> Signal
    CORROBORATES = "CORROBORATES"        # Signal -> Signal
    CONTRIBUTES_TO = "CONTRIBUTES_TO"    # Signal -> Ontology
    EMERGES_INTO = "EMERGES_INTO"        # Ontology -> Sector Signal

class SignalClass(str, Enum):
    PRICING = "PRICING"
    FEATURE = "FEATURE"
    RELEASE = "RELEASE"
    HIRING = "HIRING"
    MARKET_POSITION = "MARKET_POSITION"
    ENTERPRISE_SIGNAL = "ENTERPRISE_SIGNAL"

class Node:
    def __init__(self, node_id: str, node_type: NodeType, attributes: Dict[str, Any]):
        self.node_id = node_id
        self.node_type = node_type
        self.attributes = attributes
        
    def __repr__(self):
        return f"Node({self.node_type.name}, {self.node_id})"

class Edge:
    def __init__(self, source_id: str, target_id: str, edge_type: EdgeType, attributes: Dict[str, Any] = None):
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type
        self.attributes = attributes or {}
        
    def __repr__(self):
        return f"Edge({self.source_id} -[{self.edge_type.name}]-> {self.target_id})"

class EphemeralSignalGraph:
    """
    In-memory graph topology rebuilt deterministically on query.
    Never persists. Operates only on valid materialized signals.
    """
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        
    def add_node(self, node: Node):
        if node.node_id not in self.nodes:
            self.nodes[node.node_id] = node
            
    def add_edge(self, edge: Edge):
        self.edges.append(edge)
        
    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)
        
    def get_edges_from(self, source_id: str) -> List[Edge]:
        return [e for e in self.edges if e.source_id == source_id]
        
    def get_edges_to(self, target_id: str) -> List[Edge]:
        return [e for e in self.edges if e.target_id == target_id]
        
    def clear(self):
        """Disposes the graph to ensure determinism and prevent mutation."""
        self.nodes.clear()
        self.edges.clear()
        logger.info("Ephemeral Signal Graph disposed.")
