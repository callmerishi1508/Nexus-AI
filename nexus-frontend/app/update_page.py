import re

with open(r"C:\Web Hackathon\nexus-frontend\app\page.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add state variable
content = content.replace(
    'const [graphState, setGraphState] = useState<{nodes: any[], edges: any[]}>({nodes: [], edges: []});',
    'const [graphState, setGraphState] = useState<{nodes: any[], edges: any[]}>({nodes: [], edges: []});\n  const [synthesisBrief, setSynthesisBrief] = useState<any>(null);\n  const [isSynthesizing, setIsSynthesizing] = useState(false);'
)

# 2. Add fetch function
fetch_func = """
  const fetchGraphState = async () => {
      try {
          const res = await fetch("http://localhost:8000/api/graph/state");
          const data = await res.json();
          setGraphState(data);
      } catch (e) {
          console.error("Failed to fetch graph state", e);
      }
  };

  const fetchSynthesisBrief = async () => {
      setIsSynthesizing(true);
      try {
          const res = await fetch("http://localhost:8000/api/synthesis/brief");
          const data = await res.json();
          setSynthesisBrief(data);
      } catch (e) {
          console.error("Failed to fetch synthesis", e);
      } finally {
          setIsSynthesizing(false);
      }
  };
"""
content = content.replace(
    '  const fetchGraphState = async () => {\n      try {\n          const res = await fetch("http://localhost:8000/api/graph/state");\n          const data = await res.json();\n          setGraphState(data);\n      } catch (e) {\n          console.error("Failed to fetch graph state", e);\n      }\n  };',
    fetch_func
)

# 3. Add to useEffect
useEffect_block = """  useEffect(() => {
      fetchGraphState();
      fetchSynthesisBrief();
      const interval = setInterval(() => {
          fetchGraphState();
      }, 15000);
      const synthInterval = setInterval(() => {
          fetchSynthesisBrief();
      }, 30000); // Poll synthesis every 30s
      return () => { clearInterval(interval); clearInterval(synthInterval); };
  }, []);"""
content = re.sub(
    r'  useEffect\(\(\) => \{\n      fetchGraphState\(\);\n      const interval = setInterval\(fetchGraphState, 15000\);\n      return \(\) => clearInterval\(interval\);\n  \}, \[\]\);',
    useEffect_block,
    content
)

# 4. Add Sidebar Tab
sidebar_tab = """        <div>
          <h3 className="text-[10px] font-bold text-zinc-500 tracking-widest mb-3 uppercase">Strategic Memory</h3>
          <button onClick={() => setActiveTab("Strategic Memory")} className={`w-full text-left px-3 py-2 rounded text-sm font-mono flex items-center gap-2 ${activeTab === "Strategic Memory" ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50'}`}>
            <Network className="w-4 h-4" /> Intelligence Graph
          </button>
          
          <button onClick={() => setActiveTab("Strategic Synthesis")} className={`w-full mt-2 text-left px-3 py-2 rounded text-sm font-mono flex items-center gap-2 ${activeTab === "Strategic Synthesis" ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50'}`}>
            <FileText className="w-4 h-4" /> Strategic Synthesis
          </button>
          
          <div className={`w-full text-left px-3 py-2 rounded text-sm font-mono flex items-center gap-2 text-zinc-500 pl-9`}>
            Convergence Clusters
          </div>
        </div>"""
content = re.sub(
    r'        <div>\n          <h3 className="text-\[10px\] font-bold text-zinc-500 tracking-widest mb-3 uppercase">Strategic Memory</h3>[\s\S]*?Convergence Clusters\n          </div>\n        </div>',
    sidebar_tab,
    content
)

# 5. Add UI Panel in Main Workspace
synthesis_ui = """
          {activeTab === "Strategic Synthesis" ? (
              <div className="flex-1 flex flex-col min-h-0 relative border border-zinc-800 bg-zinc-950 rounded-lg p-8 overflow-y-auto">
                 <div className="flex justify-between items-center mb-8 border-b border-zinc-800 pb-6">
                    <h2 className="text-xl font-light text-zinc-200 uppercase tracking-widest flex items-center gap-3">
                      <FileText className="w-5 h-5 text-purple-500" /> Executive Strategic Synthesis
                    </h2>
                    <div className="flex gap-4">
                        <span className="text-[10px] font-mono border border-zinc-700 bg-zinc-900 px-3 py-1 rounded text-zinc-400 uppercase tracking-widest">
                            Provider: {synthesisBrief?.provider || "STANDBY"}
                        </span>
                        <button onClick={fetchSynthesisBrief} className="bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs px-3 py-1 rounded border border-zinc-700 flex items-center gap-2 transition-colors">
                            <RefreshCw className={`w-3 h-3 ${isSynthesizing ? 'animate-spin text-purple-500' : ''}`} /> Refresh Brief
                        </button>
                    </div>
                 </div>
                 
                 {!synthesisBrief ? (
                    <div className="flex-1 flex items-center justify-center font-mono text-sm text-zinc-600 tracking-widest uppercase">
                        Awaiting Cognitive Synthesis...
                    </div>
                 ) : (
                    <div className="grid grid-cols-12 gap-8">
                        <div className="col-span-8">
                            <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-widest mb-6">Strategic Narrative</h3>
                            <div className="text-zinc-300 leading-relaxed font-light text-lg space-y-6">
                                {synthesisBrief.strategic_narrative}
                            </div>
                            
                            {synthesisBrief.contradictions_detected && synthesisBrief.contradictions_detected.length > 0 && (
                                <div className="mt-12 border border-rose-900/50 bg-rose-950/20 rounded p-6">
                                    <h3 className="text-sm font-semibold text-rose-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                                        <Activity className="w-4 h-4" /> Divergence Alerts
                                    </h3>
                                    <ul className="list-disc pl-5 space-y-2 text-rose-300 font-mono text-sm">
                                        {synthesisBrief.contradictions_detected.map((alert: string, idx: number) => (
                                            <li key={idx}>{alert}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                        
                        <div className="col-span-4 space-y-8">
                            <div>
                                <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4">Evidence Sufficiency</h3>
                                <div className="bg-zinc-900 border border-zinc-800 rounded p-4 space-y-4">
                                    <div className="flex justify-between items-end border-b border-zinc-800/50 pb-2">
                                        <span className="text-xs text-zinc-400">Synthesis Confidence</span>
                                        <span className={`text-base font-mono ${synthesisBrief.synthesis_confidence > 80 ? 'text-emerald-400' : 'text-amber-400'}`}>
                                            {synthesisBrief.synthesis_confidence}%
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-end border-b border-zinc-800/50 pb-2">
                                        <span className="text-xs text-zinc-400">Evidence Count</span>
                                        <span className="text-base font-mono text-zinc-300">{synthesisBrief.evidence_count}</span>
                                    </div>
                                    <div className="flex justify-between items-end border-b border-zinc-800/50 pb-2">
                                        <span className="text-xs text-zinc-400">Temporal Support</span>
                                        <span className="text-base font-mono text-zinc-300">{synthesisBrief.temporal_support}</span>
                                    </div>
                                    <div className="flex justify-between items-end">
                                        <span className="text-xs text-zinc-400">Reasoning Scope</span>
                                        <span className="text-xs font-mono bg-zinc-800 px-2 py-0.5 rounded text-zinc-300">{synthesisBrief.reasoning_scope}</span>
                                    </div>
                                </div>
                            </div>
                            
                            {synthesisBrief.evidence_anchors && synthesisBrief.evidence_anchors.length > 0 && (
                                <div>
                                    <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4">Evidence Anchors</h3>
                                    <div className="bg-zinc-900 border border-zinc-800 rounded p-4 font-mono text-[10px] text-zinc-400 space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                                        {synthesisBrief.evidence_anchors.map((anchor: string, idx: number) => (
                                            <div key={idx} className="bg-zinc-950 p-2 rounded border border-zinc-800 break-all">
                                                {anchor}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                 )}
              </div>
          ) : activeTab === "Command Center" ? ("""

content = content.replace(
    '        {activeTab === "Command Center" ? (',
    synthesis_ui
)

with open(r"C:\Web Hackathon\nexus-frontend\app\page.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("Page updated successfully!")
