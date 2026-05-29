"use client";
import React, { useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { graphStore } from '../state/graphStore';
import { useNavStore } from '../state/navStore';

interface Node {
  id: string;
  name: string;
  type: string;
  sector?: string;
  attributes?: any;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface Edge {
  id: string;
  source: string | Node;
  target: string | Node;
  relation: string;
  strength: number;
}

export default function KnowledgeGraph() {
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Use graphStore via manual subscription to trigger re-renders
  const [storeState, setStoreState] = useState(() => ({
      visibleNodes: graphStore.visibleNodes,
      graphState: graphStore.graphState,
      animationState: graphStore.animationState
  }));

  useEffect(() => {
      const unsubscribe = graphStore.subscribe(() => {
          setStoreState({
              visibleNodes: new Set(graphStore.visibleNodes),
              graphState: graphStore.graphState,
              animationState: graphStore.animationState
          });
      });
      return unsubscribe;
  }, []);

  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    if (!storeState.graphState || !storeState.graphState.nodes) return;
    
    // Copy nodes and assign random initial positions, but filter by visibleNodes
    const visibleNodesList = storeState.graphState.nodes.filter((n: any) => storeState.visibleNodes.has(n.id));
    
    const initialNodes = visibleNodesList.map((n: any) => ({
      ...n,
      // For entrance animation, start them far away and let them snap in
      x: storeState.animationState === 'ENTRANCE' ? Math.random() * 2000 - 1000 : Math.random() * 800 - 400,
      y: storeState.animationState === 'ENTRANCE' ? Math.random() * 2000 - 1000 : Math.random() * 600 - 300,
      vx: 0,
      vy: 0,
    }));
    
    const initialEdges = storeState.graphState.edges || [];
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setNodes(initialNodes);
    setEdges(initialEdges);
    
    if (storeState.animationState === 'ENTRANCE') {
        const timer = setTimeout(() => {
            graphStore.setAnimationState('IDLE');
        }, 2000);
        return () => clearTimeout(timer);
    } else if (storeState.animationState === 'SIMULATING') {
        // Persona divergence WOW moment: Jitter nodes significantly to show "re-weighting"
        setNodes(prev => prev.map(n => ({
            ...n,
            vx: (n.vx || 0) + (Math.random() * 200 - 100),
            vy: (n.vy || 0) + (Math.random() * 200 - 100),
        })));
    }
  }, [storeState.graphState, storeState.visibleNodes, storeState.animationState]);

  useEffect(() => {
    if (nodes.length === 0) return;
    
    if (storeState.animationState === 'REWINDING') {
        // Freeze physics entirely during historical temporal shifts
        return;
    }
    
    let animationFrameId: number;
    let currentNodes = [...nodes];
    
    let alpha = 0.5;
    let ticks = 0;
    const maxTicks = 250;
    
    const tick = () => {
      if (alpha < 0.015 || ticks > maxTicks) return;
      alpha *= 0.95;
      ticks++;
      
      // Very basic force layout
      
      // Repulsion
      for (let i = 0; i < currentNodes.length; i++) {
        for (let j = i + 1; j < currentNodes.length; j++) {
          const dx = (currentNodes[j].x || 0) - (currentNodes[i].x || 0);
          const dy = (currentNodes[j].y || 0) - (currentNodes[i].y || 0);
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = 12000 / (dist * dist);
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          
          currentNodes[i].vx = (currentNodes[i].vx || 0) - fx;
          currentNodes[i].vy = (currentNodes[i].vy || 0) - fy;
          currentNodes[j].vx = (currentNodes[j].vx || 0) + fx;
          currentNodes[j].vy = (currentNodes[j].vy || 0) + fy;
        }
      }
      
      // Attraction (edges)
      edges.forEach(edge => {
        const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id;
        const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id;
        
        const sourceNode = currentNodes.find(n => n.id === sourceId);
        const targetNode = currentNodes.find(n => n.id === targetId);
        
        if (sourceNode && targetNode) {
          const dx = (targetNode.x || 0) - (sourceNode.x || 0);
          const dy = (targetNode.y || 0) - (sourceNode.y || 0);
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = (dist - 100) * 0.02 * (edge.strength || 1);
          
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          
          sourceNode.vx = (sourceNode.vx || 0) + fx;
          sourceNode.vy = (sourceNode.vy || 0) + fy;
          targetNode.vx = (targetNode.vx || 0) - fx;
          targetNode.vy = (targetNode.vy || 0) - fy;
        }
      });
      
      // Center gravity
      currentNodes.forEach(node => {
        node.vx = (node.vx || 0) - (node.x || 0) * 0.01;
        node.vy = (node.vy || 0) - (node.y || 0) * 0.01;
        
        // Apply velocity and dampen
        node.x = (node.x || 0) + (node.vx || 0) * alpha;
        node.y = (node.y || 0) + (node.vy || 0) * alpha;
        node.vx = (node.vx || 0) * 0.9;
        node.vy = (node.vy || 0) * 0.9;
      });
      
      setNodes([...currentNodes]);
      animationFrameId = requestAnimationFrame(tick);
    };
    
    animationFrameId = requestAnimationFrame(tick);
    
    return () => cancelAnimationFrame(animationFrameId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [edges, nodes.length, storeState.animationState]); // Re-run if topology changes or animation state flips

  if (!storeState.graphState || !storeState.graphState.nodes || storeState.graphState.nodes.length === 0) {
    const isReplay = storeState.animationState === 'REWINDING';
    const message = isReplay ? "HISTORICAL SOURCE UNAVAILABLE" : "INTELLIGENCE DEGRADED: SOURCE UNAVAILABLE";
    
    return (
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-900/10 via-black to-black opacity-60 flex flex-col items-center justify-center">
        <div className="w-12 h-12 border border-red-900/50 rounded-full flex items-center justify-center mb-4 bg-red-900/10 shadow-[0_0_15px_rgba(220,38,38,0.15)]">
           <svg className="w-5 h-5 text-red-500/70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
           </svg>
        </div>
        <div className="text-zinc-500 font-mono tracking-[0.2em] text-xs uppercase">{message}</div>
        <div className="text-zinc-700 font-mono tracking-widest text-[9px] uppercase mt-2">Graph Reconstruction Halted</div>
      </div>
    );
  }

  return (
    <div className="absolute inset-0 overflow-hidden" ref={containerRef}>
      <svg width="100%" height="100%" viewBox="-400 -300 800 600" className="w-full h-full cursor-move">
        <defs>
          <radialGradient id="nodeGrad" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
            <stop offset="0%" stopColor="rgba(99, 102, 241, 0.8)" />
            <stop offset="100%" stopColor="rgba(99, 102, 241, 0)" />
          </radialGradient>
        </defs>
        
        {/* Draw edges */}
        {edges.map(edge => {
          const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id;
          const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id;
          
          // Ensure both nodes are visible before drawing edge
          if (!storeState.visibleNodes.has(sourceId) || !storeState.visibleNodes.has(targetId)) return null;

          const sourceNode = nodes.find(n => n.id === sourceId);
          const targetNode = nodes.find(n => n.id === targetId);
          
          if (!sourceNode || !targetNode) return null;
          
          const isSimulating = storeState.animationState === 'SIMULATING';
          const strokeColor = isSimulating ? 'rgba(245, 158, 11, 0.6)' : 'rgba(255,255,255,0.15)';
          const edgeWidth = isSimulating ? (edge.strength || 0.5) * 6 : (edge.strength || 0.5) * 3;
          
          return (
            <g key={edge.id} className={isSimulating ? 'transition-all duration-300' : ''}>
              <line 
                x1={sourceNode.x} y1={sourceNode.y} 
                x2={targetNode.x} y2={targetNode.y} 
                stroke={strokeColor} strokeWidth={edgeWidth}
              />
              <text 
                x={((sourceNode.x || 0) + (targetNode.x || 0)) / 2} 
                y={((sourceNode.y || 0) + (targetNode.y || 0)) / 2 - 5}
                fill="rgba(255,255,255,0.4)" fontSize="6" textAnchor="middle" className="font-mono uppercase"
              >
                {edge.relation}
              </text>
            </g>
          );
        })}
        
        {/* Draw nodes */}
        {nodes.map(node => {
          const isCompany = node.type === 'Company';
          const isSimulating = storeState.animationState === 'SIMULATING';
          const isRewinding = storeState.animationState === 'REWINDING';
          const size = isCompany ? 10 : 7;
          
          // Flash colors when simulating to indicate cognitive divergence
          const color = isSimulating ? (isCompany ? '#fbbf24' : '#f87171') : (isCompany ? '#818cf8' : '#34d399');
          const opacityClass = isRewinding ? 'opacity-50 grayscale transition-all duration-1000' : (isSimulating ? 'transition-all duration-300' : '');
          
          return (
            <g 
              key={node.id} 
              transform={`translate(${node.x || 0}, ${node.y || 0})`} 
              className={`${opacityClass} cursor-pointer group hover:opacity-100 transition-opacity`}
              onClick={() => useNavStore.getState().setActiveExplanationId(`node_${node.name}`)}
            >
              <circle r={size * 2.5} fill={isSimulating ? 'rgba(245, 158, 11, 0.4)' : 'url(#nodeGrad)'} opacity={isSimulating ? '0.6' : '0.3'} />
              <circle r={size} fill={color} stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
              <text 
                y={size + 12} 
                fill={isCompany ? "white" : "rgba(255,255,255,0.7)"} 
                fontSize={isCompany ? "7" : "5"} 
                textAnchor="middle" 
                className={`font-sans font-medium tracking-wide drop-shadow-md pointer-events-none ${isCompany ? '' : 'opacity-0 group-hover:opacity-100 transition-opacity duration-200'}`}
              >
                {isCompany ? node.name : node.name.replace(/^Signal_.*?_/, '').replace(/_/g, ' ')}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
