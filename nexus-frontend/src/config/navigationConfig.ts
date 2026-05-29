export type Role = "SYSTEM_ADMIN" | "EXECUTIVE" | "GOVERNANCE" | "ANALYST" | "OBSERVER";
export type MasterMode = "OPERATIONS" | "INTELLIGENCE" | "SIMULATION";

export interface ViewDefinition {
  id: string;
  label: string;
  icon?: string;
  description?: string;
}

export interface NavigationConfig {
  allowedModes: MasterMode[];
  defaultMode: MasterMode;
  modeViews: Record<MasterMode, ViewDefinition[]>;
  defaultViews: Record<MasterMode, string>;
}

export interface RoleLayoutPreset {
  sidebar: boolean;
  density: "sparse" | "dense" | "comfortable";
  telemetry: boolean;
  graphOpacity: number;
  narrativePriority: boolean;
}

export const ROLE_LAYOUT_PRESETS: Record<Role, RoleLayoutPreset> = {
  EXECUTIVE: {
    sidebar: false,
    density: "sparse",
    telemetry: false,
    graphOpacity: 0.2,
    narrativePriority: true
  },
  SYSTEM_ADMIN: {
    sidebar: true,
    density: "dense",
    telemetry: true,
    graphOpacity: 0.9,
    narrativePriority: false
  },
  ANALYST: {
    sidebar: true,
    density: "dense",
    telemetry: true,
    graphOpacity: 0.8,
    narrativePriority: false
  },
  GOVERNANCE: {
    sidebar: true,
    density: "comfortable",
    telemetry: true,
    graphOpacity: 0.5,
    narrativePriority: true
  },
  OBSERVER: {
    sidebar: true,
    density: "comfortable",
    telemetry: false,
    graphOpacity: 0.6,
    narrativePriority: false
  }
};

export const VIEW_REGISTRY: Record<string, ViewDefinition> = {
  "topology": { id: "topology", label: "Topology", icon: "Network" },
  "logical_nodes": { id: "logical_nodes", label: "Logical Nodes", icon: "Server" },
  "integrity": { id: "integrity", label: "Integrity", icon: "Shield" },
  
  "strategic_memory": { id: "strategic_memory", label: "Knowledge Graph", icon: "Network" },
  "strategic_synthesis": { id: "strategic_synthesis", label: "Synthesis Briefs", icon: "FileText" },
  "governance": { id: "governance", label: "Institutional Arbitration", icon: "Shield" },
  "entity_registration": { id: "entity_registration", label: "Entity Registration", icon: "Activity" },

  "scenario_sandbox": { id: "scenario_sandbox", label: "Scenario Sandbox", icon: "Zap" }
};

export const ROLE_NAVIGATION_MAP: Record<Role, NavigationConfig> = {
  SYSTEM_ADMIN: {
    allowedModes: ["OPERATIONS", "INTELLIGENCE", "SIMULATION"],
    defaultMode: "OPERATIONS",
    modeViews: {
      OPERATIONS: [VIEW_REGISTRY["topology"], VIEW_REGISTRY["logical_nodes"], VIEW_REGISTRY["integrity"]],
      INTELLIGENCE: [VIEW_REGISTRY["strategic_memory"], VIEW_REGISTRY["strategic_synthesis"], VIEW_REGISTRY["governance"]],
      SIMULATION: [VIEW_REGISTRY["scenario_sandbox"]]
    },
    defaultViews: {
      OPERATIONS: "topology",
      INTELLIGENCE: "strategic_memory",
      SIMULATION: "scenario_sandbox"
    }
  },
  EXECUTIVE: {
    allowedModes: ["INTELLIGENCE", "SIMULATION"],
    defaultMode: "INTELLIGENCE",
    modeViews: {
      OPERATIONS: [],
      INTELLIGENCE: [VIEW_REGISTRY["strategic_memory"], VIEW_REGISTRY["strategic_synthesis"], VIEW_REGISTRY["governance"]],
      SIMULATION: [VIEW_REGISTRY["scenario_sandbox"]]
    },
    defaultViews: {
      OPERATIONS: "",
      INTELLIGENCE: "strategic_memory",
      SIMULATION: "scenario_sandbox"
    }
  },
  GOVERNANCE: {
    allowedModes: ["INTELLIGENCE"],
    defaultMode: "INTELLIGENCE",
    modeViews: {
      OPERATIONS: [],
      INTELLIGENCE: [VIEW_REGISTRY["strategic_memory"], VIEW_REGISTRY["strategic_synthesis"], VIEW_REGISTRY["governance"]],
      SIMULATION: []
    },
    defaultViews: {
      OPERATIONS: "",
      INTELLIGENCE: "governance",
      SIMULATION: ""
    }
  },
  ANALYST: {
    allowedModes: ["INTELLIGENCE", "SIMULATION"],
    defaultMode: "INTELLIGENCE",
    modeViews: {
      OPERATIONS: [],
      INTELLIGENCE: [VIEW_REGISTRY["strategic_memory"], VIEW_REGISTRY["strategic_synthesis"], VIEW_REGISTRY["entity_registration"]],
      SIMULATION: [VIEW_REGISTRY["scenario_sandbox"]]
    },
    defaultViews: {
      OPERATIONS: "",
      INTELLIGENCE: "strategic_memory",
      SIMULATION: "scenario_sandbox"
    }
  },
  OBSERVER: {
    allowedModes: ["OPERATIONS"],
    defaultMode: "OPERATIONS",
    modeViews: {
      OPERATIONS: [VIEW_REGISTRY["topology"]],
      INTELLIGENCE: [],
      SIMULATION: []
    },
    defaultViews: {
      OPERATIONS: "topology",
      INTELLIGENCE: "",
      SIMULATION: ""
    }
  }
};

export const getCanonicalViewName = (viewId: string): string => {
  return VIEW_REGISTRY[viewId]?.label || viewId;
};
