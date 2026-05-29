import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Search, Filter, Cpu, Target, ExternalLink, ShieldAlert } from 'lucide-react';
import { useNavStore } from '@/state/navStore';
import { LiveIngestionWidget } from './LiveIngestionWidget';

interface IntelData {
  company: string;
  productName: string;
  trajectory: any;
  rawSignals: number;
  timestamp: string;
  sourceUrl: string;
  confidenceScore: number;
  impactScore: number;
  classification: 'EXCELLENT' | 'STABLE' | 'UNDERPERFORMING' | 'BANKRUPT';
  personaInterpretation?: any;
  degradedState: string;
  traceId: string;
}

export const MarketIntelWorkspace: React.FC<{ activeSector: string }> = ({ activeSector }) => {
  const { activeTenant, activePersona, isTransitioning, setActiveExplanationId } = useNavStore();
  const [intel, setIntel] = useState<IntelData[]>([]);
  const [loading, setLoading] = useState(true);
  const [systemAlert, setSystemAlert] = useState<{message: string, type: string} | null>(null);

  const fetchIntel = useCallback(async () => {
    setLoading(true);
    try {
      // 1. Fetch all targets
      const targetsRes = await fetch("http://127.0.0.1:8000/api/system/targets", {
        headers: { 'X-Nexus-Tenant': activeTenant }
      });
      if (!targetsRes.ok) throw new Error("Failed to fetch targets");
      
      const targetsData = await targetsRes.json();
      const sectorCompanies = targetsData.sector_targets?.[activeSector] || [];
      
      if (sectorCompanies.length === 0) {
        setIntel([]);
        setLoading(false);
        return;
      }

      // 2. Fetch intelligence for each company
      const results = await Promise.all(sectorCompanies.map(async (company: string) => {
        try {
          const url = activePersona && activePersona !== 'SYSTEM' 
            ? `http://127.0.0.1:8000/api/intelligence/interpret/${activePersona}/${encodeURIComponent(company)}`
            : `http://127.0.0.1:8000/api/intelligence/company/${encodeURIComponent(company)}`;
            
          const res = await fetch(url, { headers: { 'X-Nexus-Tenant': activeTenant } });
          if (!res.ok) return null;
          return await res.json();
        } catch (e) {
          return null;
        }
      }));

      const validResults = results.filter(Boolean);

      // Map to UI format
      const mappedIntel: IntelData[] = validResults.map(res => ({
        company: res.company,
        productName: "Intelligence Trajectory",
        trajectory: res.trajectory_compression,
        rawSignals: res.raw_signal_count || 0,
        timestamp: new Date().toISOString(),
        sourceUrl: "#",
        confidenceScore: res.degraded_state === "OK" ? 85 : 0,
        impactScore: res.degraded_state === "OK" ? 90 : 0,
        classification: 'STABLE',
        personaInterpretation: res.persona_interpretation,
        degradedState: res.degraded_state,
        traceId: res.trace_id
      }));

      setIntel(mappedIntel);
    } catch (e) {
      console.error(e);
      setSystemAlert({ message: "Failed to load intelligence", type: "error" });
    } finally {
      setLoading(false);
    }
  }, [activeSector, activePersona, activeTenant]);

  useEffect(() => {
    fetchIntel();
  }, [fetchIntel]);

  return (
    <div className="flex-1 p-6 overflow-y-auto w-full relative">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold font-mono tracking-widest text-zinc-100 uppercase">
            Market Intelligence: {activeSector}
          </h2>
          <div className="text-xs text-zinc-500 font-mono tracking-widest uppercase mt-1">
            Real-time Competitive State Tracking
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchIntel} className="p-2 border border-white/10 rounded hover:bg-white/5 transition-colors">
            <Activity className="w-4 h-4 text-cyan-400" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2].map(i => (
            <div key={i} className="border border-white/5 bg-black/20 rounded-lg p-6 flex flex-col gap-4 animate-pulse">
              <div className="h-6 w-1/3 bg-white/5 rounded"></div>
              <div className="grid grid-cols-2 gap-4 mt-2">
                <div className="h-16 bg-white/5 rounded"></div>
                <div className="h-16 bg-white/5 rounded"></div>
              </div>
              <div className="h-20 bg-white/5 rounded mt-4"></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {intel.length === 0 ? (
            <div className="col-span-1 md:col-span-2 flex flex-col items-center justify-center p-16 border border-dashed border-zinc-800 rounded-lg bg-zinc-900/20">
              <ShieldAlert className="w-8 h-8 text-zinc-600 mb-4" />
              <div className="text-zinc-400 font-mono text-sm tracking-widest uppercase mb-1">No Verified Targets</div>
              <div className="text-zinc-600 font-mono text-[10px] tracking-widest uppercase text-center max-w-sm">
                No verified intelligence targets exist in the current domain for {activeSector}. Switch to Executive mode to synthesize this sector.
              </div>
            </div>
          ) : (
            intel.map((data, idx) => (
              <div 
                key={data.company}
                onClick={() => setActiveExplanationId(`intel_${data.company}`)}
                className={`bg-black/40 border border-white/10 rounded-lg p-6 flex flex-col gap-4 relative overflow-hidden cursor-pointer hover:border-indigo-500/50 transition-colors ${isTransitioning ? 'opacity-70 grayscale' : ''}`}
              >
                {data.degradedState !== "OK" && (
                  <div className="absolute inset-0 bg-red-900/10 pointer-events-none"></div>
                )}
                
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-lg text-indigo-300">{data.company}</h3>
                    <div className="text-xs text-zinc-500 uppercase tracking-widest mt-1">{data.productName}</div>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-[10px] bg-white/5 px-2 py-1 rounded font-mono text-zinc-400">
                      {data.rawSignals} SIGNALS
                    </span>
                  </div>
                </div>

                {data.degradedState !== "OK" && (
                  <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded flex items-center gap-2 text-amber-400 text-xs font-mono tracking-wide">
                    <ShieldAlert className="w-4 h-4 shrink-0" />
                    <div>Degraded Intelligence State: {data.degradedState}.</div>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4 mt-2">
                  <div className="bg-white/5 border border-white/5 rounded p-3">
                    <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest mb-1">Confidence Score</div>
                    <div className="text-2xl font-bold text-zinc-200">{data.confidenceScore}<span className="text-sm text-zinc-500">/100</span></div>
                  </div>
                  <div className="bg-white/5 border border-white/5 rounded p-3">
                    <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest mb-1">Impact Score</div>
                    <div className="text-2xl font-bold text-zinc-200">{data.impactScore}<span className="text-sm text-zinc-500">/100</span></div>
                  </div>
                </div>

                <div className="space-y-4 mt-2">
                  <div>
                    <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest mb-2 border-b border-white/5 pb-1">Temporal Trajectory Compression</div>
                    {data.trajectory ? (
                      <div className="bg-indigo-950/30 border border-indigo-500/20 p-3 rounded text-sm text-indigo-200">
                        <div className="font-semibold mb-1">{data.trajectory.summary}</div>
                        <div className="text-xs opacity-70">Dominant Trend: {data.trajectory.dominant_trend}</div>
                      </div>
                    ) : (
                      <div className="text-xs text-zinc-500 italic">No compressed trajectory available.</div>
                    )}
                  </div>
                  
                  {data.personaInterpretation && (
                    <div>
                      <div className="text-[10px] font-mono text-amber-500 uppercase tracking-widest mb-2 border-b border-white/5 pb-1">Cognitive Persona Lens: {activePersona}</div>
                      <div className="bg-amber-950/30 border border-amber-500/20 p-3 rounded text-sm text-amber-200/90">
                        {data.personaInterpretation.insight}
                      </div>
                    </div>
                  )}

                  <div className="flex justify-between items-center text-[10px] font-mono text-zinc-600 uppercase">
                    <div>Trace: {data.traceId.substring(0, 12)}...</div>
                    <div className="flex items-center gap-1 hover:text-indigo-400 transition-colors">
                      Source <ExternalLink className="w-3 h-3" />
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      <div className="mt-8">
        <LiveIngestionWidget onIngestComplete={fetchIntel} />
      </div>
    </div>
  );
};