export class GraphStore {
    private listeners: Set<() => void> = new Set();
    
    public visibleNodes: Set<string> = new Set();
    public activeSector: string | null = null;
    public graphState: any = null;
    public animationState: 'IDLE' | 'ENTRANCE' | 'SIMULATING' | 'REWINDING' = 'IDLE';

    subscribe(listener: () => void) {
        this.listeners.add(listener);
        return () => {
            this.listeners.delete(listener);
        };
    }

    private notify() {
        this.listeners.forEach(l => l());
    }

    setGraphState(state: any) {
        this.graphState = state;
        
        // Default: all nodes in the active sector are visible
        if (state && state.nodes) {
            this.visibleNodes = new Set(
                state.nodes
                    .filter((n: any) => !this.activeSector || n.sector === this.activeSector)
                    .map((n: any) => n.id)
            );
        } else {
            this.visibleNodes.clear();
        }
        
        this.animationState = 'ENTRANCE';
        this.notify();
    }

    setActiveSector(sector: string | null) {
        this.activeSector = sector;
        if (this.graphState) {
            this.setGraphState(this.graphState); // recompute visible
        }
    }

    toggleNodeVisibility(nodeId: string) {
        if (this.visibleNodes.has(nodeId)) {
            this.visibleNodes.delete(nodeId);
        } else {
            this.visibleNodes.add(nodeId);
        }
        this.notify();
    }

    setAnimationState(state: 'IDLE' | 'ENTRANCE' | 'SIMULATING' | 'REWINDING') {
        this.animationState = state;
        this.notify();
    }
}

// Singleton instance
export const graphStore = new GraphStore();
