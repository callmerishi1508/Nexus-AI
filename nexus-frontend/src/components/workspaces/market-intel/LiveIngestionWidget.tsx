import React, { useState } from 'react';
import { DownloadCloud, ExternalLink, ShieldCheck, AlertTriangle, Loader2 } from 'lucide-react';
import { useNavStore } from '@/state/navStore';

const DEMO_TARGETS = [
    { name: "Notion Pricing", url: "https://www.notion.so/pricing", competitor: "Notion", type: "PRICING" },
    { name: "Monday Pricing", url: "https://monday.com/pricing", competitor: "Monday.com", type: "PRICING" },
    { name: "Airtable Pricing", url: "https://airtable.com/pricing", competitor: "Airtable", type: "PRICING" },
    { name: "OpenAI Pricing", url: "https://openai.com/pricing", competitor: "OpenAI", type: "PRICING" }
];

export function LiveIngestionWidget({ onIngestComplete }: { onIngestComplete?: () => void }) {
    const [mode, setMode] = useState<'DEMO' | 'ADVANCED'>('DEMO');
    const [url, setUrl] = useState('');
    const [competitor, setCompetitor] = useState('');
    const [status, setStatus] = useState<'IDLE' | 'INGESTING' | 'SUCCESS' | 'REJECTED' | 'ERROR'>('IDLE');
    const [message, setMessage] = useState('');
    
    const { activeTenant } = useNavStore();

    const handleIngest = async (targetUrl: string, targetComp: string, type: string = "PRICING") => {
        if (!targetUrl || !targetComp) return;
        
        setStatus('INGESTING');
        setMessage(`Connecting to Bright Data mesh for ${targetComp}...`);
        
        try {
            const res = await fetch('http://127.0.0.1:8000/api/ingestion/live', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-Nexus-Tenant': activeTenant
                },
                body: JSON.stringify({
                    url: targetUrl,
                    competitor: targetComp,
                    signal_type: type
                })
            });
            const data = await res.json();
            
            if (res.ok && data.status === 'MATERIALIZED') {
                setStatus('SUCCESS');
                setMessage(`Acquisition successful. Confidence: ${(data.confidence * 100).toFixed(1)}%. Graph updated.`);
                if (onIngestComplete) onIngestComplete();
            } else if (res.ok && data.status === 'REJECTED') {
                setStatus('REJECTED');
                setMessage(data.message || 'Signal rejected by governance.');
            } else {
                throw new Error(data.detail || 'Unknown error');
            }
        } catch (e: any) {
            setStatus('ERROR');
            setMessage(`Acquisition failed: ${e.message}`);
        }
    };

    return (
        <div className="bg-black/30 border border-indigo-500/20 rounded-xl p-6 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 bg-indigo-500 h-full"></div>
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h3 className="text-lg font-bold text-zinc-200 flex items-center gap-2">
                        <DownloadCloud className="w-5 h-5 text-indigo-400" />
                        Live Intelligence Acquisition
                    </h3>
                    <div className="text-xs text-zinc-500 font-mono mt-1 uppercase tracking-widest">
                        Acquire raw signals & materialise to graph
                    </div>
                </div>
                <div className="flex gap-2 bg-black/40 border border-white/5 rounded-lg p-1">
                    <button 
                        onClick={() => setMode('DEMO')}
                        className={`px-3 py-1 rounded text-xs font-mono transition-colors ${mode === 'DEMO' ? 'bg-indigo-500/20 text-indigo-300' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        FAST PRESETS
                    </button>
                    <button 
                        onClick={() => setMode('ADVANCED')}
                        className={`px-3 py-1 rounded text-xs font-mono transition-colors ${mode === 'ADVANCED' ? 'bg-indigo-500/20 text-indigo-300' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        CUSTOM URL
                    </button>
                </div>
            </div>

            {mode === 'DEMO' ? (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                    {DEMO_TARGETS.map(t => (
                        <button
                            key={t.name}
                            onClick={() => handleIngest(t.url, t.competitor, t.type)}
                            disabled={status === 'INGESTING'}
                            className="bg-white/5 hover:bg-indigo-500/10 border border-white/5 hover:border-indigo-500/30 p-3 rounded-lg text-left transition-all disabled:opacity-50"
                        >
                            <div className="font-semibold text-zinc-300 text-sm">{t.competitor}</div>
                            <div className="text-[10px] text-zinc-500 font-mono mt-1 line-clamp-1">{t.url}</div>
                        </button>
                    ))}
                </div>
            ) : (
                <div className="flex gap-4">
                    <input 
                        type="text" 
                        placeholder="Target Company Name" 
                        value={competitor}
                        onChange={e => setCompetitor(e.target.value)}
                        className="bg-black/50 border border-white/10 rounded-lg px-4 py-2 text-sm text-zinc-200 outline-none w-1/4 focus:border-indigo-500/50"
                    />
                    <input 
                        type="url" 
                        placeholder="https://..." 
                        value={url}
                        onChange={e => setUrl(e.target.value)}
                        className="bg-black/50 border border-white/10 rounded-lg px-4 py-2 text-sm text-zinc-200 outline-none flex-1 focus:border-indigo-500/50"
                    />
                    <button
                        onClick={() => handleIngest(url, competitor)}
                        disabled={status === 'INGESTING' || !url || !competitor}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50 flex items-center gap-2"
                    >
                        {status === 'INGESTING' ? <Loader2 className="w-4 h-4 animate-spin" /> : <DownloadCloud className="w-4 h-4" />}
                        Acquire
                    </button>
                </div>
            )}

            {status !== 'IDLE' && (
                <div className={`mt-4 p-3 rounded border text-sm font-mono flex items-start gap-3 ${
                    status === 'INGESTING' ? 'bg-blue-900/10 border-blue-500/20 text-blue-400' :
                    status === 'SUCCESS' ? 'bg-emerald-900/10 border-emerald-500/20 text-emerald-400' :
                    status === 'REJECTED' ? 'bg-amber-900/10 border-amber-500/20 text-amber-400' :
                    'bg-red-900/10 border-red-500/20 text-red-400'
                }`}>
                    {status === 'SUCCESS' && <ShieldCheck className="w-4 h-4 mt-0.5" />}
                    {(status === 'ERROR' || status === 'REJECTED') && <AlertTriangle className="w-4 h-4 mt-0.5" />}
                    {status === 'INGESTING' && <Loader2 className="w-4 h-4 mt-0.5 animate-spin" />}
                    <div>
                        <div className="font-semibold uppercase tracking-widest text-xs mb-1">Status: {status}</div>
                        <div className="opacity-90">{message}</div>
                    </div>
                </div>
            )}
        </div>
    );
}