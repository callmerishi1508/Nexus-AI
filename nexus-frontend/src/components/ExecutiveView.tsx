import React from 'react';
import { FileText, RefreshCw, Activity, Network } from 'lucide-react';
import { ROLE_NAVIGATION_MAP } from '@/config/navigationConfig';
import { useNavStore } from '@/state/navStore';
import KnowledgeGraph from '@/components/KnowledgeGraph';

export function ExecutiveView(props: any) {
  const { activeTab, setActiveTab, activeRole, masterMode } = useNavStore();
  const { synthesisBrief, isSynthesizing, fetchSynthesisBrief, graphState, activeExplanationId, setActiveExplanationId, temporalTarget } = props;

  return (
    <>
      <div className="flex justify-between items-center mb-6 bg-white/[0.01] border border-white/5 p-4 rounded-xl shadow-sm shrink-0">
        <div className="flex gap-4">
          {ROLE_NAVIGATION_MAP[activeRole]?.modeViews[masterMode]?.map((view: any) => (
            <button 
              key={view.id}
              onClick={() => setActiveTab(view.id)}
              className={`px-4 py-2 rounded-md text-xs font-semibold tracking-wide transition-colors ${activeTab === view.id ? 'bg-white/10 text-white shadow-sm' : 'text-zinc-400 hover:text-white hover:bg-white/5'}`}
            >
              {view.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
            <input 
              type="text"
              placeholder="Enter Sector (e.g. AI Technology)"
              className="bg-white/5 border border-white/10 rounded-md px-3 py-1.5 text-sm font-medium text-zinc-300 outline-none hover:bg-white/10 focus:border-cyan-500/50 transition-colors w-56"
              value={props.activeSector}
              onChange={(e) => {
                  props.setActiveSector(e.target.value);
              }}
              onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                      useNavStore.getState().setActiveSector(e.currentTarget.value);
                      props.handleExpandSector(e.currentTarget.value);
                  }
              }}
            />
            <button 
              onClick={(e) => {
                  const val = (e.currentTarget.previousElementSibling as HTMLInputElement).value;
                  props.setActiveSector(val);
                  useNavStore.getState().setActiveSector(val);
                  props.handleExpandSector(val);
              }}
              disabled={props.isExpandingSector}
              className="bg-cyan-950/40 hover:bg-cyan-900/60 border border-cyan-800 text-cyan-400 px-3 py-1.5 rounded-md text-xs uppercase tracking-widest font-mono transition-all flex items-center gap-2"
            >
              {props.isExpandingSector ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Network className="w-4 h-4" />}
              Synthesize
            </button>
        </div>
      </div>

      {activeTab === "strategic_memory" ? (
        <div className="flex-1 flex flex-col min-h-0 relative border border-zinc-800 bg-zinc-950 rounded-lg p-0 overflow-hidden">
          <KnowledgeGraph />
        </div>
      ) : activeTab === "strategic_synthesis" ? (
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
                      <div className="text-zinc-300 leading-relaxed font-light text-lg space-y-6 whitespace-pre-wrap">
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
      ) : (
        <div className="flex-1 flex items-center justify-center font-mono text-sm text-zinc-600 tracking-widest uppercase border border-white/5 rounded-xl bg-white/[0.01]">
          {activeTab} Mode Initializing...
        </div>
      )}
    </>
  );
}
