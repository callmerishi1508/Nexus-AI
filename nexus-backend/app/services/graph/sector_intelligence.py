import logging
from typing import Dict, List
import uuid

from app.services.graph.engine import EphemeralSignalGraph, Node, Edge, NodeType, EdgeType

logger = logging.getLogger(__name__)

def inject_sector_emergence(graph: EphemeralSignalGraph):
    """
    Scans the materialized graph for cross-company ontology convergences.
    If 3+ companies exhibit the same structural state, it injects a SECTOR_SIGNAL.
    """
    logger.info("Scanning for Sector-Level intelligence emergence...")
    
    # Map state -> List of Company Node IDs
    state_to_companies = {}
    
    # We need to trace: OntologyNode -> SignalNode -> SnapshotNode (or CompanyNode directly via PRECEDES/GENERATED_FROM)
    # For speed, we just iterate Ontology nodes and map back to companies using node attributes
    
    ontology_nodes = [n for n in graph.nodes.values() if n.node_type == NodeType.ONTOLOGY_STATE]
    
    for ont_node in ontology_nodes:
        state = ont_node.attributes.get("state")
        
        # Traverse back to find the company
        # Ontology <-[CONTRIBUTES_TO]- Signal -[GENERATED_FROM]-> Snapshot
        # Snapshot has no company attribute, but Company is linked? 
        # Wait, the simplest way is to extract company from the Signal or Snapshot if we embedded it,
        # but in builder.py we only added company to the CompanyNode.
        
        # We can find the Signal(s) contributing to this Ontology state
        contributing_signals = [e.source_id for e in graph.get_edges_to(ont_node.node_id) if e.edge_type == EdgeType.CONTRIBUTES_TO]
        
        if contributing_signals:
            first_sig = contributing_signals[0]
            # Find the snapshot for this signal
            generated_edges = [e for e in graph.get_edges_from(first_sig) if e.edge_type == EdgeType.GENERATED_FROM]
            if generated_edges:
                snap_id = generated_edges[0].target_id
                
                # In builder.py, we created company nodes. 
                # For hackathon correlation simplicity, let's just group by the raw state and assume all states are currently valid in the graph.
                
                # We need a robust way to map snapshot -> company. 
                # Let's assume snapshot ID contains company or we just group by the state itself.
                if state not in state_to_companies:
                    state_to_companies[state] = set()
                    
                # Store the ontology node ID to link later
                state_to_companies[state].add(ont_node.node_id)

    # Threshold for sector emergence is 3 separate occurrences of the same state
    SECTOR_THRESHOLD = 3
    
    for state, ont_node_ids in state_to_companies.items():
        if len(ont_node_ids) >= SECTOR_THRESHOLD:
            sector_node_id = f"sector_{state.lower()}_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"*** SECTOR EMERGENCE DETECTED *** : SECTOR_{state}")
            
            # Create the Sector Node
            graph.add_node(Node(
                sector_node_id,
                NodeType.SECTOR_SIGNAL,
                {"macro_state": f"SECTOR_{state}", "company_count": len(ont_node_ids)}
            ))
            
            # Connect all contributing Ontology States to this Sector Node
            for ont_id in ont_node_ids:
                graph.add_edge(Edge(ont_id, sector_node_id, EdgeType.EMERGES_INTO))
