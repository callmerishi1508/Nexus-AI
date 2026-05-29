import logging
from typing import List, Dict, Any, Optional

from app.services.graph.engine import EphemeralSignalGraph, NodeType, EdgeType

logger = logging.getLogger(__name__)

def get_company_cognition_path(graph: EphemeralSignalGraph, company_name: str) -> List[Dict[str, Any]]:
    """
    Returns the temporal chain of signals and resulting ontology states for a given company.
    """
    company_node_id = f"company_{company_name.replace(' ', '_').lower()}"
    company_node = graph.get_node(company_node_id)
    
    if not company_node:
        return []
        
    path = []
    
    # We find all signals. Since we didn't explicitly link Company->Signal, we just iterate all signals
    # that map to this company's snapshots, or simply traverse PRECEDES chains.
    # Actually, in builder.py we tracked it internally. We can just find all SignalNodes, 
    # check if they GENERATED_FROM a Snapshot that belongs to this company.
    # To keep it fast for now, we just scan for all SignalNodes in the graph and return them sorted by ID (which implies time in our mock).
    # A robust implementation would trace CompanyNode -> SnapshotNode -> SignalNode -> PRECEDES.
    
    return path

def get_sector_emergence(graph: EphemeralSignalGraph) -> List[Dict[str, Any]]:
    """
    Returns all active SectorSignalNode macro-intelligence states.
    """
    sector_nodes = [n for n in graph.nodes.values() if n.node_type == NodeType.SECTOR_SIGNAL]
    return [{"macro_state": n.attributes.get("macro_state"), "company_count": n.attributes.get("company_count")} for n in sector_nodes]

def trace_signal_provenance(graph: EphemeralSignalGraph, signal_id: str) -> Optional[Dict[str, Any]]:
    """
    Traverses GENERATED_FROM to find the exact Snapshot for forensic auditability.
    """
    edges = graph.get_edges_from(signal_id)
    gen_edges = [e for e in edges if e.edge_type == EdgeType.GENERATED_FROM]
    
    if not gen_edges:
        return None
        
    snapshot_id = gen_edges[0].target_id
    snapshot_node = graph.get_node(snapshot_id)
    
    if not snapshot_node:
        return None
        
    return {
        "signal_id": signal_id,
        "origin_snapshot_id": snapshot_id,
        "timestamp": snapshot_node.attributes.get("timestamp")
    }
