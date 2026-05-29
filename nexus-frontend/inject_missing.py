import re

with open('app/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# We want to insert the components right before </> and );\n          })()} at the end of the file.
# Let's locate })()}
idx = content.rfind('})()}')
if idx != -1:
    # Also find the </> right before it.
    idx2 = content.rfind('</>', 0, idx)
    if idx2 != -1:
        new_components = '''
          {activeTab === "topology" && (
            <div className="grid grid-cols-12 gap-6 flex-1 min-h-0 transition-all duration-500">
               <div className="col-span-9 glass-panel overflow-hidden relative">
                   <div className="absolute inset-0 bg-black/50" />
               </div>
               <div className="col-span-3 flex flex-col gap-6 overflow-y-auto">
                   <div className="glass-panel p-6">
                       <h3 className="text-xs font-bold text-zinc-500 tracking-widest uppercase mb-4 flex items-center gap-2"><Activity className="w-4 h-4 text-amber-500" /> Sector Health State</h3>
                       <div className="flex justify-between items-center mb-4">
                           <span className="text-sm font-medium text-zinc-400">Sector Stability</span>
                           <span className="text-xs font-bold bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded border border-emerald-500/20">NOMINAL</span>
                       </div>
                       <div className="flex justify-between items-center mb-4">
                           <span className="text-sm font-medium text-zinc-400">Convergence Pressure</span>
                           <span className="text-xs font-bold bg-white/5 text-zinc-500 px-2 py-1 rounded border border-white/5">LOW</span>
                       </div>
                       <div className="flex justify-between items-center">
                           <span className="text-sm font-medium text-zinc-400">Strategic Volatility</span>
                           <span className="text-xs font-bold text-zinc-300">STABLE</span>
                       </div>
                   </div>
                   <div className="glass-panel p-6 flex-1 min-h-0 overflow-y-auto custom-scrollbar">
                       <h3 className="text-xs font-bold text-zinc-500 tracking-widest uppercase mb-4 flex items-center gap-2"><Activity className="w-4 h-4 text-cyan-500" /> Operational Feed</h3>
                       <div className="flex flex-col gap-4 font-mono text-xs">
                           <div className="text-emerald-500/90 leading-relaxed">[12:43:29.117] [Monday]<br/>[DEGRADED] Upstream degradation. Recovery pipeline active.</div>
                           <div className="text-emerald-500/90 leading-relaxed">[12:43:29.085] [Monday]<br/>[ACTIVE] Initiating Cycle 91...</div>
                           <div className="text-emerald-500/90 leading-relaxed">[12:43:13.750] [Airtable]<br/>[DEGRADED] Upstream degradation. Recovery pipeline active.</div>
                       </div>
                   </div>
               </div>
            </div>
          )}

          {activeTab === "strategic_memory" && (
               <div className="flex-1 flex flex-col min-h-0 relative border border-[#1a2230] bg-[#0b0f14] p-8 overflow-hidden rounded-xl">
                    <h2 className="text-sm font-sans tracking-[0.2em] uppercase text-zinc-500 mb-6 flex items-center gap-3">
                      <Network className="w-5 h-5 text-blue-500" /> Strategic Knowledge Graph
                    </h2>
                    
                    <div className="flex-1 flex items-center justify-center relative min-h-0 overflow-hidden border border-white/5 bg-black/40 rounded-lg">
                        {isGraphLoading ? (
                           <div className="flex flex-col items-center justify-center gap-4">
                               <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
                               <span className="text-xs font-mono text-indigo-400 tracking-widest uppercase">Synthesizing Topology...</span>
                           </div>
                        ) : (
                           <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-900/10 via-black to-black opacity-60 flex items-center justify-center text-zinc-700 font-mono tracking-widest text-xs uppercase">No Nodes Mapped</div>
                        )}
                    </div>
                    
                    {sessionMode === "REPLAY" && (
                       <div className="mt-6 border border-white/10 bg-black/50 p-6 rounded-lg relative overflow-hidden">
                           <div className="flex justify-between items-center mb-4">
                               <span className="text-xs font-mono text-zinc-400 tracking-widest uppercase">Strategic Timeline Replay</span>
                               <span className="text-xs font-mono text-zinc-300">T - {30 - temporalDay} Days</span>
                           </div>
                           <input type="range" min="0" max="30" value={temporalDay} onChange={(e) => setTemporalDay(parseInt(e.target.value))} className="w-full accent-blue-500 h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer" />
                           <div className="flex justify-between px-1 mt-2">
                               <span className="text-[10px] font-mono text-zinc-600">-30D</span>
                               <span className="text-[10px] font-mono text-emerald-500">LIVE</span>
                           </div>
                       </div>
                    )}
               </div>
          )}

          {activeTab === "scenario_sandbox" && (
             <div className="flex-1 flex flex-col min-h-0 border border-blue-500/20 bg-[#0b0f14] p-8 overflow-hidden rounded-xl">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-sm font-semibold text-blue-400 uppercase tracking-widest flex items-center gap-2">
                      <Zap className="w-4 h-4" /> Scenario Sandbox
                    </h2>
                    <p className="text-[10px] font-mono text-zinc-500 mt-1 uppercase">Counterfactual Strategic Projection</p>
                    <p className="text-[9px] font-mono text-amber-500/80 mt-2 border border-amber-500/20 bg-amber-500/5 px-2 py-1 rounded inline-block">Bounded by historical evidence and institutional constraints.</p>
                  </div>
                  {simulationResult && (
                    <div className="text-right">
                      <div className="text-[10px] font-mono text-zinc-500">SIMULATION HASH</div>
                      <div className="text-[10px] font-mono text-blue-400">{str(simulationResult.get('fingerprints', {}).get('simulation_hash', ''))[:16]}...</div>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-6 flex-1 min-h-0">
                  <div className="col-span-1 flex flex-col gap-4 overflow-y-auto custom-scrollbar">
                    <div className="border border-zinc-800 bg-zinc-900/50 p-4 rounded-lg flex flex-col gap-3">
                      <h3 className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">Perturbation Variables</h3>
                      <div>
                          <label className="text-[9px] text-zinc-500 uppercase font-mono block mb-1">Target Node (Entity)</label>
                          <input type="text" value={simTarget} onChange={e => setSimTarget(e.target.value)} placeholder="e.g. Notion, OpenAI" className="w-full bg-black border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-zinc-300 focus:border-blue-500 outline-none" />
                      </div>
                      <div>
                          <label className="text-[9px] text-zinc-500 uppercase font-mono block mb-1">Vector Mutation</label>
                          <select value={simMutation} onChange={e => setSimMutation(e.target.value)} className="w-full bg-black border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-zinc-300 focus:border-blue-500 outline-none">
                              <option value="ACQUISITION">Acquisition</option>
                              <option value="BANKRUPTCY">Bankruptcy</option>
                              <option value="MERGER">Merger</option>
                              <option value="LEADERSHIP_CHANGE">Leadership Change</option>
                          </select>
                      </div>
                      <button onClick={runSimulation} disabled={isSimulating} className="mt-4 w-full bg-blue-600 hover:bg-blue-500 text-white font-mono text-[10px] py-2 rounded uppercase tracking-widest transition-colors flex justify-center items-center gap-2">
                          {isSimulating ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3" />}
                          {isSimulating ? "Simulating..." : "Execute Projection"}
                      </button>
                    </div>
                  </div>
                  
                  <div className="col-span-2 border border-zinc-800 bg-black rounded-lg p-6 flex flex-col min-h-0 overflow-y-auto custom-scrollbar">
                      {simulationResult ? (
                          <div className="flex-1 font-mono text-sm text-zinc-300 whitespace-pre-wrap">
                              <h4 className="text-blue-400 mb-4 tracking-widest uppercase border-b border-zinc-800 pb-2">Synthesis Results</h4>
                              <p className="leading-relaxed text-zinc-400">{(simulationResult as any).synthesis?.strategic_narrative}</p>
                          </div>
                      ) : (
                          <div className="flex-1 flex flex-col items-center justify-center text-zinc-600">
                              <Zap className="w-8 h-8 mb-4 opacity-50" />
                              <p className="text-xs uppercase tracking-widest">Awaiting Simulation Parameters</p>
                          </div>
                      )}
                  </div>
                </div>
             </div>
          )}
'''
        # Replace the simulationResult.get python code inside string with actual JS code!
        new_components = new_components.replace("str(simulationResult.get('fingerprints', {}).get('simulation_hash', ''))[:16]", "(simulationResult as any).fingerprints?.simulation_hash?.substring(0, 16)")
        content = content[:idx2] + new_components + content[idx2:]
        with open('app/page.tsx', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Success")
    else:
        print("Could not find </>")
else:
    print("Could not find })()}")
