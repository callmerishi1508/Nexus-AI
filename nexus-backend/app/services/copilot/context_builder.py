import json
from typing import Dict, Any, List

class CopilotContextBuilder:
    """
    Compresses raw graph topology and timeline trajectory into a bounded context 
    window for the Copilot LLM. This prevents the LLM from processing thousands of 
    raw nodes and forces it to operate on strategic, deterministic intelligence.
    """
    
    def build_graph_summary(self, graph_state: Dict[str, Any]) -> str:
        nodes = graph_state.get("nodes", [])
        edges = graph_state.get("edges", [])
        
        companies = [n["name"] for n in nodes if n["type"] == "Company"]
        features = [n["name"] for n in nodes if n["type"] == "Feature"]
        pricing = [n["name"] for n in nodes if n["type"] == "PricingModel"]
        
        summary = (
            f"Active Competitors Monitored: {', '.join(companies) if companies else 'None'}\n"
            f"Feature Developments: {', '.join(features) if features else 'None'}\n"
            f"Pricing Shifts: {', '.join(pricing) if pricing else 'None'}\n"
        )
        return summary

    def build_sector_emergence_summary(self, graph_state: Dict[str, Any]) -> str:
        nodes = graph_state.get("nodes", [])
        trends = [n["name"] for n in nodes if n["type"] == "SectorTrend"]
        
        if not trends:
            return "No distinct sector macro-trends identified."
            
        return f"Sector Trends Detected: {', '.join(trends)}"

    def build_trajectory_summary(self, edges: List[Dict[str, Any]], nodes: List[Dict[str, Any]]) -> str:
        if not edges:
            return "No historical timeline trajectory found."
            
        # Just grab the top 3 strongest signals
        sorted_edges = sorted(edges, key=lambda x: x.get("strength", 0), reverse=True)
        top_edges = sorted_edges[:3]
        
        trajectory = []
        node_map = {n['id']: n['name'] for n in nodes}
        for e in top_edges:
            source_name = node_map.get(e['source'], e['source'])
            target_name = node_map.get(e['target'], e['target'])
            trajectory.append(f"Strongest Signal: {source_name} {e['relation']} {target_name} (Confidence: {e.get('confidence', 1.0)})")
            
        return "\n".join(trajectory)

    def build_context(self, graph_state: Dict[str, Any], persona: str, timeline: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Builds the final deterministic context object injected into the LLM prompt.
        """
        return {
            "persona": persona,
            "graph_summary": self.build_graph_summary(graph_state),
            "sector_emergence": self.build_sector_emergence_summary(graph_state),
            "trajectory_summary": self.build_trajectory_summary(graph_state.get("edges", []), graph_state.get("nodes", [])),
            "raw_evidence_count": len(graph_state.get("edges", []))
        }

context_builder = CopilotContextBuilder()
