import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Any

from app.services.graph.engine import EphemeralSignalGraph, Node, Edge, NodeType, EdgeType
from app.services.persistence.derivatives import DERIVATIVE_DIR

logger = logging.getLogger(__name__)

# Mandatory Insertion Thresholds to prevent "cognitive sludge"
MIN_GRAPH_CONFIDENCE = 0.70

def load_derivative_events() -> List[Dict[str, Any]]:
    """Loads all derivative events from disk."""
    events = []
    if not DERIVATIVE_DIR.exists():
        return events
        
    for filename in os.listdir(DERIVATIVE_DIR):
        if filename.endswith("_event.json"):
            filepath = DERIVATIVE_DIR / filename
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    event = json.load(f)
                    # We inject snapshot_id from the filename if needed
                    event["snapshot_id"] = filename.replace("_event.json", "")
                    events.append(event)
            except Exception as e:
                logger.error(f"Failed to load derivative {filename}: {e}")
                
    return events

def build_ephemeral_graph() -> EphemeralSignalGraph:
    """
    Deterministically rebuilds the intelligence topology from the derivative layer.
    Filters out noise before insertion. Links temporal edges.
    """
    graph = EphemeralSignalGraph()
    events = load_derivative_events()
    
    logger.info(f"Rebuilding Materialized Signal Graph from {len(events)} derivative events...")
    
    # We will map company -> list of signals to link PRECEDES edges chronologically later
    company_signals = {}
    
    for event in events:
        snapshot_id = event.get("snapshot_id")
        signals = event.get("signals", [])
        impact_payload = event.get("impact", {})
        
        # We need the company from the payload or mock it if missing
        # In a full system, company name is embedded in the event or retrieved from canonical archive
        # For hackathon, we assume 'company' is in the event metadata or we mock "Unknown Company"
        company_name = event.get("company", "Notion (Test Target)") 
        
        # 1. Ensure Company Node exists
        company_node_id = f"company_{company_name.replace(' ', '_').lower()}"
        graph.add_node(Node(company_node_id, NodeType.COMPANY, {"name": company_name}))
        
        # 2. Add Snapshot Node (Provenance Anchor)
        graph.add_node(Node(snapshot_id, NodeType.SNAPSHOT, {"timestamp": datetime.utcnow().isoformat()}))
        
        # 3. Add Ontology Node if one exists
        ontology_state = impact_payload.get("classification")
        ontology_node_id = None
        if ontology_state and ontology_state != "STABLE":
            ontology_node_id = f"ontology_{snapshot_id}_{ontology_state}"
            graph.add_node(Node(
                ontology_node_id, 
                NodeType.ONTOLOGY_STATE, 
                {"state": ontology_state, "interpretation_hash": impact_payload.get("interpretation_hash")}
            ))
        
        # 4. Filter & Insert Signals
        for idx, sig in enumerate(signals):
            sig_type = sig.get("type", "UNKNOWN")
            
            # Here we simulate the graph materialization thresholds (confidence normally comes from the signal)
            # In our current mock `verify_substrate.py`, confidence wasn't injected into the raw diff dict.
            # We assume a base confidence for structural diffs for the sake of the hackathon graph insertion.
            confidence = sig.get("confidence", 0.85)
            
            if confidence < MIN_GRAPH_CONFIDENCE:
                logger.debug(f"Signal {sig_type} dropped (Confidence {confidence} < {MIN_GRAPH_CONFIDENCE})")
                continue
                
            sig_id = f"sig_{snapshot_id}_{idx}"
            sig_node = Node(sig_id, NodeType.SIGNAL, {
                "type": sig_type,
                "confidence": confidence,
                "severity": sig.get("severity")
            })
            graph.add_node(sig_node)
            
            # Link Signal to Snapshot (Provenance)
            graph.add_edge(Edge(sig_id, snapshot_id, EdgeType.GENERATED_FROM))
            
            # Link Company to Signal (we invert logic, or we can just say Signal belongs to Company)
            # Actually, standard graph links Company -> Signal or Signal -> Company. 
            # Let's just track it in our temporal map to build PRECEDES.
            if company_node_id not in company_signals:
                company_signals[company_node_id] = []
            company_signals[company_node_id].append((sig_id, event.get("timestamp", datetime.utcnow().timestamp())))
            
            # Link Signal to Ontology
            if ontology_node_id and sig_type in impact_payload.get("primary_signals", []):
                graph.add_edge(Edge(sig_id, ontology_node_id, EdgeType.CONTRIBUTES_TO))

    # 5. Build Temporal PRECEDES edges per company
    for company_id, sig_list in company_signals.items():
        # Sort signals by timestamp
        sig_list.sort(key=lambda x: x[1])
        
        for i in range(len(sig_list) - 1):
            curr_sig = sig_list[i][0]
            next_sig = sig_list[i+1][0]
            graph.add_edge(Edge(curr_sig, next_sig, EdgeType.PRECEDES))
            
    logger.info(f"Graph Rebuild Complete. Nodes: {len(graph.nodes)} | Edges: {len(graph.edges)}")
    return graph
