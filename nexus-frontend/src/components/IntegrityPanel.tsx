import { Shield } from "lucide-react";

interface IntegrityPanelProps {
  reviewQueue: any[];
}

export function IntegrityPanel({ reviewQueue }: IntegrityPanelProps) {
  return (
    <div className="flex-1 overflow-y-auto mt-4 px-8">
      <h2 className="text-xs font-mono text-zinc-500 uppercase tracking-[0.2em] mb-12 border-b border-zinc-800/50 pb-4">
         Institutional Trust Observability
      </h2>
      
      <div className="flex gap-24">
        {/* Platform Guarantees Doctrine */}
        <div className="w-80 border-r border-zinc-800/30 pr-16 shrink-0">
           <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-12">Platform Guarantees</h3>
           <div className="space-y-6">
               <div className="flex items-start gap-6 text-[10px] font-mono text-zinc-400">
                   <span className="text-zinc-700 mt-0.5">--</span> Replay Integrity
               </div>
               <div className="flex items-start gap-6 text-[10px] font-mono text-zinc-400">
                   <span className="text-zinc-700 mt-0.5">--</span> Governance Enforcement
               </div>
               <div className="flex items-start gap-6 text-[10px] font-mono text-zinc-400">
                   <span className="text-zinc-700 mt-0.5">--</span> Simulation Isolation
               </div>
               <div className="flex items-start gap-6 text-[10px] font-mono text-zinc-400">
                   <span className="text-zinc-700 mt-0.5">--</span> Graceful Degradation
               </div>
               <div className="flex items-start gap-6 text-[10px] font-mono text-zinc-400">
                   <span className="text-zinc-700 mt-0.5">--</span> Evidence-Constrained Cognition
               </div>
           </div>
        </div>

        <div className="flex-1 grid grid-cols-3 gap-y-24 gap-x-12">
           {/* Integrity Score */}
           <div className="flex flex-col items-start">
              <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-3">Integrity Score</h3>
              <div className="text-4xl font-light text-zinc-300">92.4</div>
              <div className="text-[9px] font-mono text-zinc-600 mt-3 tracking-widest uppercase">Weighted Degradation</div>
           </div>
           
           {/* Replay Confidence */}
           <div className="flex flex-col items-start">
              <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-3">Replay Confidence</h3>
              <div className="text-4xl font-light text-zinc-300">99.5%</div>
              <div className="text-[9px] font-mono text-zinc-600 mt-3 tracking-widest uppercase">Deterministic Rate</div>
           </div>
           
           {/* Contradiction Pressure */}
           <div className="flex flex-col items-start">
              <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-3">Contradiction Pressure</h3>
              <div className="text-4xl font-light text-zinc-300">1.2</div>
              <div className="text-[9px] font-mono text-zinc-600 mt-3 tracking-widest uppercase">Instability Index</div>
           </div>
           
           {/* Governance Saturation */}
           <div className="flex flex-col items-start border-t border-zinc-800/30 pt-12">
              <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-3">Governance Saturation</h3>
              <div className="text-4xl font-light text-zinc-300">{reviewQueue.length}</div>
              <div className="text-[9px] font-mono text-zinc-600 mt-3 tracking-widest uppercase">Awaiting Adjudication</div>
           </div>
           
           {/* Lineage Depth */}
           <div className="flex flex-col items-start border-t border-zinc-800/30 pt-12">
              <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-3">Avg Lineage Depth</h3>
              <div className="text-4xl font-light text-zinc-300">4.2</div>
              <div className="text-[9px] font-mono text-zinc-600 mt-3 tracking-widest uppercase">Snapshot Generations</div>
           </div>
           
           {/* Evidence Density */}
           <div className="flex flex-col items-start border-t border-zinc-800/30 pt-12">
              <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-3">Evidence Density</h3>
              <div className="text-4xl font-light text-zinc-300">3.8</div>
              <div className="text-[9px] font-mono text-zinc-600 mt-3 tracking-widest uppercase">Anchors Per Synthesis</div>
           </div>
        </div>
      </div>
    </div>
  );
}
