import { create } from 'zustand';
import { Role, MasterMode, ROLE_NAVIGATION_MAP } from '../config/navigationConfig';
import { graphStore } from './graphStore';

export type SessionMode = "LIVE" | "REPLAY" | "SANDBOX" | "CHAOS";
export type Tenant = "tenant_public" | "tenant_sandbox" | "tenant_demo";
export type Persona = "SYSTEM" | "CHIEF_EXECUTIVE_OFFICER" | "CHIEF_TECHNOLOGY_OFFICER" | "CHIEF_FINANCIAL_OFFICER" | "VENTURE_CAPITALIST" | "ENTERPRISE_ARCHITECT" | "QUANTITATIVE_ANALYST" | "PRODUCT_STRATEGIST" | "THREAT_INTELLIGENCE" | "HEAD_OF_ENGINEERING" | "MARKET_RESEARCHER" | "REGULATORY_COMPLIANCE";

export interface Milestone {
  date: string;
  label: string;
  type: string;
}

interface NavState {
  // Global Identifiers
  activeRole: Role;
  activeTenant: Tenant;
  activePersona: Persona;
  activeSector: string;
  
  // Navigation State
  masterMode: MasterMode;
  activeTab: string; // canonical route id
  activeExplanationId: string | null;
  executiveScreenshotMode: boolean;
  
  // Temporal & Replay State
  sessionMode: SessionMode;
  temporalTarget: string | null;
  scrubbingDate: string | null; // For lightweight preview staging
  timeline: Milestone[];
  replayCache: Record<string, any>; // In-memory LRU approximation
  replayAbortController: AbortController | null;
  
  // Orchestration Locks
  isTransitioning: boolean;
  transitionMessage: string;
  hasEntered: boolean;

  // Actions / Setters
  setActiveRole: (role: Role) => void;
  setActiveTenant: (tenant: Tenant) => void;
  setActivePersona: (persona: Persona) => void;
  setActiveSector: (sector: string) => void;
  setMasterMode: (mode: MasterMode) => void;
  setActiveTab: (tabId: string) => void;
  setSessionMode: (mode: SessionMode) => void;
  setActiveExplanationId: (id: string | null) => void;
  toggleScreenshotMode: () => void;
  setHasEntered: (entered: boolean) => void;
  
  // Replay Lifecycle Actions
  setScrubbingDate: (date: string | null) => void;
  commitTemporalTarget: (date: string) => void;
  setReplayCache: (key: string, data: any) => void;
  getReplayAbortSignal: () => AbortSignal;
  cancelInFlightReplay: () => void;
  
  // Internal Lock helper
  _startTransition: (msg: string) => void;
  _endTransition: () => void;

  // Derived Selectors (convenience functions mapped from config)
  getAllowedModes: () => MasterMode[];
  getAllowedTabs: () => { id: string, label: string }[];
  isReplayActive: () => boolean;
}

export const useNavStore = create<NavState>((set, get) => ({
  activeRole: "EXECUTIVE",
  activeTenant: "tenant_public",
  activePersona: "CHIEF_EXECUTIVE_OFFICER",
  activeSector: "Productivity SaaS",
  
  masterMode: "INTELLIGENCE",
  activeTab: "strategic_memory",
  activeExplanationId: null,
  executiveScreenshotMode: false,
  
  sessionMode: "LIVE",
  temporalTarget: null,
  scrubbingDate: null,
  timeline: [
    { date: "2023-11-01", label: "Sector Emergence", type: "event" },
    { date: "2024-01-15", label: "Competitor Bankruptcy", type: "event" },
    { date: "2024-03-20", label: "Product Alpha Launch", type: "event" },
    { date: "2024-05-10", label: "Strategic Drift", type: "event" },
    { date: "PRESENT", label: "Current Topology", type: "event" }
  ],
  replayCache: {},
  replayAbortController: null,
  
  isTransitioning: false,
  transitionMessage: "",
  hasEntered: false,

  _startTransition: (msg) => set({ isTransitioning: true, transitionMessage: msg }),
  _endTransition: () => set({ isTransitioning: false, transitionMessage: "" }),

  // ---------------------------------------------------------
  // INVALIDATION RULES ENFORCEMENT
  // ---------------------------------------------------------
  
  setActiveRole: (role) => {
    const { _startTransition, _endTransition } = get();
    _startTransition("Authenticating Cognitive Profile...");
    
    // Invalidation Rule 1: Role changes validate modes and routes
    const config = ROLE_NAVIGATION_MAP[role];
    const newMode = config.allowedModes.includes(get().masterMode) ? get().masterMode : config.defaultMode;
    const allowedTabs = config.modeViews[newMode]?.map(v => v.id) || [];
    const newTab = allowedTabs.includes(get().activeTab) ? get().activeTab : (config.defaultViews[newMode] || "");

    // Clear underlying intelligence state heavily
    graphStore.setGraphState({nodes: [], edges: []});

    setTimeout(() => {
        set({ activeRole: role, masterMode: newMode, activeTab: newTab });
        _endTransition();
    }, 400);
  },

  setActiveTenant: (tenant) => {
    const { _startTransition, _endTransition } = get();
    // Invalidation Rule 2: Workspace changes invalidate graph cache
    _startTransition("Flushing Cognitive State & Connecting to Isolated Domain...");
    
    graphStore.setGraphState({nodes: [], edges: []});
    
    setTimeout(() => {
        set({ activeTenant: tenant });
        _endTransition();
    }, 600);
  },

  setActivePersona: (persona) => {
    const { _startTransition, _endTransition } = get();
    // Invalidation Rule 3: Persona changes trigger recomputation & graph morph
    _startTransition("Reweighting Cognitive Lens...");
    
    set({ activePersona: persona });
    // Tell GraphStore to run a morph animation
    graphStore.setAnimationState('SIMULATING');
    
    setTimeout(() => {
        graphStore.setAnimationState('IDLE');
        _endTransition();
    }, 800);
  },

  setActiveSector: (sector) => {
      set({ activeSector: sector });
      graphStore.setActiveSector(sector); // Sync graph visibility immediately
  },

  setMasterMode: (mode) => {
      const config = ROLE_NAVIGATION_MAP[get().activeRole];
      if (!config.allowedModes.includes(mode)) return; // Prevent unauthorized
      const newTab = config.defaultViews[mode] || "";
      set({ masterMode: mode, activeTab: newTab });
  },

  setActiveTab: (tabId) => {
      const allowed = get().getAllowedTabs().map(t => t.id);
      if (allowed.includes(tabId)) {
          set({ activeTab: tabId });
      }
  },

  setActiveExplanationId: (id) => {
      set({ activeExplanationId: id });
  },

  toggleScreenshotMode: () => {
      set(state => ({ executiveScreenshotMode: !state.executiveScreenshotMode }));
  },

  setHasEntered: (entered) => {
      set({ hasEntered: entered });
  },

  setSessionMode: (mode) => {
    const { _startTransition, _endTransition, cancelInFlightReplay } = get();
    // Invalidation Rule 4: Session changes reset replay state
    _startTransition(mode === "REPLAY" ? "Synchronizing Historical Topology..." : "Resynchronizing Live Stream...");
    
    cancelInFlightReplay(); // Stop any pending replay frames
    set({ sessionMode: mode, temporalTarget: null, scrubbingDate: null });
    
    setTimeout(() => {
        _endTransition();
    }, 500);
  },

  // ---------------------------------------------------------
  // REPLAY STAGING LIFECYCLE
  // ---------------------------------------------------------
  setScrubbingDate: (date) => {
      // Very lightweight state update for drag preview
      set({ scrubbingDate: date });
  },

  commitTemporalTarget: (date) => {
      const { _startTransition, _endTransition, cancelInFlightReplay, replayCache, activeTenant, activePersona } = get();
      
      // 1. Cancel stale fetches
      cancelInFlightReplay();

      // 2. Commit the target
      set({ temporalTarget: date, scrubbingDate: null });

      const cacheKey = `${activeTenant}:${activePersona}:${date}`;
      const isCached = !!replayCache[cacheKey];

      // 3. UX Lock
      _startTransition(isCached ? "Restoring Memory Snapshot..." : "Reconstructing Historical Topology...");
      
      // 4. Graph Visual Freeze
      graphStore.setAnimationState('REWINDING');

      // (The actual fetch is triggered in page.tsx by watching temporalTarget)
  },

  setReplayCache: (key, data) => {
      set(state => {
          const newCache = { ...state.replayCache, [key]: data };
          // Naive LRU: Keep last 20 frames
          const keys = Object.keys(newCache);
          if (keys.length > 20) {
              delete newCache[keys[0]]; // Remove oldest
          }
          return { replayCache: newCache };
      });
  },

  getReplayAbortSignal: () => {
      const controller = new AbortController();
      set({ replayAbortController: controller });
      return controller.signal;
  },

  cancelInFlightReplay: () => {
      const { replayAbortController } = get();
      if (replayAbortController) {
          replayAbortController.abort();
          set({ replayAbortController: null });
      }
  },

  // ---------------------------------------------------------
  // DERIVED SELECTORS
  // ---------------------------------------------------------
  getAllowedModes: () => {
      const role = get().activeRole;
      return ROLE_NAVIGATION_MAP[role].allowedModes;
  },
  
  getAllowedTabs: () => {
      const role = get().activeRole;
      const mode = get().masterMode;
      return ROLE_NAVIGATION_MAP[role].modeViews[mode] || [];
  },
  
  isReplayActive: () => get().sessionMode === "REPLAY"

}));
