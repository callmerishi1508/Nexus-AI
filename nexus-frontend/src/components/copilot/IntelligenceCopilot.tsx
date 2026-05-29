import React, { useState, useRef, useEffect } from 'react';
import { useNavStore } from '@/state/navStore';
import { Terminal, Send, Cpu, Loader2, Filter } from 'lucide-react';
import { nexusFetch } from '@/lib/api';
import { graphStore } from '@/state/graphStore';

interface Message {
    id: string;
    role: 'user' | 'agent';
    content: string;
    evidence?: string[];
    confidence?: number;
    directive?: string;
    persona: string;
}

export function IntelligenceCopilot() {
    const { activePersona, activeTenant, sessionMode, temporalTarget } = useNavStore();
    const [messages, setMessages] = useState<Message[]>([{
        id: 'init',
        role: 'agent',
        content: `NEXUS Copilot initialized. Active Lens: ${activePersona}. Awaiting strategic inquiry...`,
        persona: 'SYSTEM'
    }]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const [graphState, setGraphState] = useState(() => ({
        nodes: graphStore.graphState?.nodes || [],
        visibleNodes: graphStore.visibleNodes
    }));
    const [showFilters, setShowFilters] = useState(false);

    useEffect(() => {
        const unsubscribe = graphStore.subscribe(() => {
            setGraphState({
                nodes: graphStore.graphState?.nodes || [],
                visibleNodes: new Set(graphStore.visibleNodes)
            });
        });
        return unsubscribe;
    }, []);

    const handleSend = async () => {
        if (!input.trim() || isTyping) return;
        
        const query = input;
        setInput('');
        
        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: query,
            persona: 'USER'
        };
        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        try {
            const res = await nexusFetch('http://127.0.0.1:8000/api/copilot/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    persona: activePersona,
                    sector: activeSector,
                    timestamp: sessionMode === 'REPLAY' ? temporalTarget : null
                })
            });
            const data = await res.json();
            
            const agentMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'agent',
                content: data.answer || "Error: Failed to process response.",
                confidence: data.confidence_score,
                evidence: data.evidence_anchors,
                directive: data.strategic_directive,
                persona: activePersona
            };
            setMessages(prev => [...prev, agentMsg]);
        } catch (error) {
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                role: 'agent',
                content: "Inference Error: Unable to reach Copilot endpoint.",
                persona: 'SYSTEM'
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="w-full border-l border-zinc-800/80 bg-zinc-950 flex flex-col h-full shrink-0 z-30 shadow-2xl relative">
            {/* Header */}
            <div className="h-14 border-b border-zinc-800/80 px-4 flex items-center justify-between bg-zinc-900/40">
                <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-cyan-500" />
                    <span className="text-xs font-mono font-semibold text-zinc-300 uppercase tracking-widest">Intelligence Terminal</span>
                </div>
                <select 
                    value={activePersona} 
                    onChange={e => {
                        useNavStore.getState().setActivePersona(e.target.value as any);
                        setMessages([{
                            id: Date.now().toString(),
                            role: 'agent',
                            content: `Lens shifted to ${e.target.value}. Recalibrating strategic context...`,
                            persona: 'SYSTEM'
                        }]);
                    }}
                    className="bg-indigo-950/30 border border-indigo-500/30 rounded px-2 py-1 text-[10px] font-mono font-medium text-indigo-400 outline-none hover:bg-indigo-900/40 transition-colors uppercase tracking-widest cursor-pointer"
                >
                    <option className="bg-zinc-900" value="CHIEF_EXECUTIVE_OFFICER">CHIEF EXECUTIVE OFFICER</option>
                    <option className="bg-zinc-900" value="CHIEF_TECHNOLOGY_OFFICER">CHIEF TECHNOLOGY OFFICER</option>
                    <option className="bg-zinc-900" value="CHIEF_FINANCIAL_OFFICER">CHIEF FINANCIAL OFFICER</option>
                    <option className="bg-zinc-900" value="VENTURE_CAPITALIST">VENTURE CAPITALIST</option>
                    <option className="bg-zinc-900" value="ENTERPRISE_ARCHITECT">ENTERPRISE ARCHITECT</option>
                    <option className="bg-zinc-900" value="QUANTITATIVE_ANALYST">QUANTITATIVE ANALYST</option>
                    <option className="bg-zinc-900" value="PRODUCT_STRATEGIST">PRODUCT STRATEGIST</option>
                    <option className="bg-zinc-900" value="THREAT_INTELLIGENCE">THREAT INTELLIGENCE</option>
                    <option className="bg-zinc-900" value="HEAD_OF_ENGINEERING">HEAD OF ENGINEERING</option>
                    <option className="bg-zinc-900" value="MARKET_RESEARCHER">MARKET RESEARCHER</option>
                    <option className="bg-zinc-900" value="REGULATORY_COMPLIANCE">REGULATORY COMPLIANCE</option>
                </select>
                <button 
                    onClick={() => setShowFilters(!showFilters)}
                    className={`ml-2 p-1.5 rounded transition-colors ${showFilters ? 'bg-cyan-900/50 text-cyan-400' : 'text-zinc-500 hover:bg-zinc-800'}`}
                >
                    <Filter className="w-3.5 h-3.5" />
                </button>
            </div>

            {/* Filter Panel */}
            {showFilters && (
                <div className="bg-zinc-900/80 border-b border-zinc-800/80 p-3 flex flex-col gap-2 max-h-48 overflow-y-auto">
                    <span className="text-[9px] uppercase tracking-widest text-cyan-500/70 mb-1 font-mono">Topology Filters</span>
                    {graphState.nodes.filter((n: any) => n.type === 'Company').map((node: any) => (
                        <label key={node.id} className="flex items-center gap-2 text-xs font-mono text-zinc-300 cursor-pointer hover:text-white">
                            <input 
                                type="checkbox" 
                                checked={graphState.visibleNodes.has(node.id)}
                                onChange={() => graphStore.toggleNodeVisibility(node.id)}
                                className="accent-cyan-600 bg-zinc-800 border-zinc-700"
                            />
                            {node.name}
                        </label>
                    ))}
                </div>
            )}

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar" ref={scrollRef}>
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                        <div className={`text-[9px] font-mono uppercase tracking-widest mb-1 ${msg.role === 'user' ? 'text-zinc-500' : 'text-cyan-600/70'}`}>
                            {msg.role === 'user' ? 'Operator' : msg.persona + ' Agent'}
                        </div>
                        <div className={`max-w-[90%] p-3 text-xs leading-relaxed font-mono ${msg.role === 'user' ? 'bg-zinc-800 text-zinc-200 rounded-l rounded-br' : 'bg-cyan-950/20 text-cyan-100/90 border border-cyan-900/50 rounded-r rounded-bl'}`}>
                            {msg.content}
                            
                            {msg.role === 'agent' && msg.persona !== 'SYSTEM' && (
                                <div className="mt-3 pt-3 border-t border-cyan-900/50 flex flex-col gap-2">
                                    <div className="flex justify-between items-center text-[10px]">
                                        <span className="text-zinc-500">Confidence</span>
                                        <span className={msg.confidence && msg.confidence > 80 ? 'text-emerald-400' : 'text-amber-400'}>{msg.confidence}%</span>
                                    </div>
                                    {msg.directive && (
                                        <div className="bg-cyan-900/30 p-2 rounded border border-cyan-800/50">
                                            <span className="text-[9px] uppercase tracking-widest text-cyan-500 block mb-1">Strategic Directive</span>
                                            {msg.directive}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {isTyping && (
                    <div className="flex items-center gap-2 text-[10px] font-mono text-cyan-600 uppercase tracking-widest">
                        <Loader2 className="w-3 h-3 animate-spin" /> Ingesting Graph Topology...
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-zinc-800/80 bg-zinc-900/20">
                <div className="relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder={`Query the ${activePersona} Agent...`}
                        className="w-full bg-black border border-zinc-800 rounded px-4 py-3 text-xs font-mono text-zinc-300 placeholder:text-zinc-600 focus:outline-none focus:border-cyan-500/50 transition-colors pr-10"
                    />
                    <button 
                        onClick={handleSend}
                        className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-zinc-500 hover:text-cyan-400 transition-colors"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
                <div className="mt-2 text-[9px] text-zinc-600 font-mono text-center tracking-widest uppercase">
                    Bounded by Current Deterministic Replay State
                </div>
            </div>
        </div>
    );
}
