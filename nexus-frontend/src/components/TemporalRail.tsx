"use client";

import { motion } from "framer-motion";
import { History } from "lucide-react";

interface Milestone {
  date: string;
  label: string;
  type: string;
}

import { useNavStore } from "@/state/navStore";

export function TemporalRail() {
  const { 
      timeline, 
      temporalTarget, 
      scrubbingDate, 
      setScrubbingDate, 
      commitTemporalTarget, 
      setSessionMode 
  } = useNavStore();

  const activeDate = scrubbingDate || temporalTarget || "PRESENT";
  return (
    <motion.div 
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[800px] nx-panel p-4 flex flex-col gap-4 z-50 overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-900/10 to-transparent pointer-events-none" />
      
      <div className="flex items-center justify-between z-10">
        <div className="flex items-center gap-2 text-cyan-500">
          <History className="w-4 h-4" />
          <span className="text-xs font-mono tracking-widest font-semibold uppercase">Historical Reconstruction Mode</span>
        </div>
        <button onClick={() => setSessionMode("LIVE")} className="nx-typography hover:text-zinc-300 transition-colors">
          Return to Present
        </button>
      </div>

      <div className="relative h-12 flex items-center z-10">
        {/* The Rail Line */}
        <div className="absolute left-4 right-4 h-[2px] bg-cyan-900/40" />
        
        {/* Milestones */}
        <div className="absolute inset-0 flex items-center justify-between px-4">
          {timeline.map((m, i) => {
            const isActive = activeDate === m.date;
            
            return (
              <div key={i} className="relative group flex flex-col items-center">
                <button 
                  onMouseEnter={() => setScrubbingDate(m.date)}
                  onMouseLeave={() => setScrubbingDate(null)}
                  onClick={() => commitTemporalTarget(m.date)}
                  className={`w-3 h-3 rounded-full transition-all duration-300 z-10 ${
                    isActive ? "bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.5)] scale-125" : "bg-cyan-900 hover:bg-cyan-700"
                  }`}
                />
                <div className={`absolute ${i % 2 === 0 ? 'top-6' : 'bottom-6'} w-24 text-center whitespace-normal text-[9px] font-mono transition-all duration-300 ${isActive ? 'text-cyan-300 z-20 font-bold drop-shadow-md' : 'text-zinc-500 group-hover:text-cyan-400 group-hover:z-20'}`}>
                  {m.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
