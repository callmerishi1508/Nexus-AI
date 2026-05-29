<div align="center">
  <img src="nexus-frontend/public/globe.svg" alt="Nexus Logo" width="80" height="80" />
  <h1>NEXUS</h1>
  <p><strong>Governed Cognitive Infrastructure for Strategic Intelligence</strong></p>

  [![Version](https://img.shields.io/badge/version-1.0.0-emerald.svg?style=for-the-badge)]()
  [![Build](https://img.shields.io/badge/build-passing-brightgreen.svg?style=for-the-badge)]()
  [![License](https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge)]()
</div>

<br />

**NEXUS** is not an "AI Wrapper." It is an institutional operating system that bridges the gap between chaotic real-world event streams and deterministic strategic execution. It consumes unstructured market events and reduces them into bounded, replayable, and governed cognitive projections.

By wrapping sovereign AI inference in a strict shell of deterministic evidence, verifiable graphs, and Role-Based Access Control (RBAC), NEXUS prevents the operational entropy typical of probabilistic LLM generation. 

*NEXUS does not predict the future. It simulates bounded strategic trajectories constrained by replayable evidence.*

---

## ⚡ Key Features

- **🧠 Deterministic Extraction**  
  Bypasses standard LLM hallucination for structured data. A strict JSON-schema pipeline enforces evidence extraction, ensuring unstructured payloads are converted into deterministic state.
- **🕸️ Strategic Memory Graph**  
  Knowledge is anchored structurally in a localized temporal graph. You cannot effectively replay a vector embedding; you *can* replay a graph. This bypasses context-window amnesia and enables perfectly deterministic replayability.
- **🛡️ Institutional Governance**  
  Monitors convergence anomalies and evidence-poor briefs. If saturation or contradictions occur, NEXUS immediately enters a `GOVERNANCE_FROZEN` state, intentionally halting mutation to preserve institutional truth.
- **🕹️ Bounded Simulation**  
  Sandboxes counterfactual strategic projections (e.g., "What if a competitor drops pricing by 15%?"). The simulation evaluates structural boundaries and mathematically decays confidence over stretched temporal horizons.
- **🪂 Graceful Degradation**  
  If the sovereign inference engine crashes, the Event Router catches the exception, updates the platform state to `DEGRADED`, and falls back to deterministic regex extraction. The mesh survives the loss of its smartest components.

---

## 🏗️ Architecture Philosophy

Most AI applications fail in production because they grant probabilistic systems uncontrolled mutation access to live infrastructure. NEXUS reverses this dynamic by enforcing **Cognitive Viewports**.

Roles do not just gate API endpoints; they gate situational awareness to prevent executive overload:
- **`SYSTEM_ADMIN`**: Full access to the raw topology, heartbeat pulses, and chaotic event feeds.
- **`EXECUTIVE`**: Experiences a sparse, muted strategic dashboard. Noise is constitutionally hidden.
- **`ANALYST`**: Can simulate bounded scenarios but cannot bypass governance approval.

---

## 🚀 Quick Start

### Prerequisites
- **Node.js**: v20 or higher
- **Python**: v3.11 or higher
- **SQLite3**: Pre-installed or available in PATH

### Boot Sequence

Launch the entire stack (Backend, Frontend, and Watcher services) using the unified boot script:

```powershell
# Windows
.\launch_nexus.ps1
```

*(For debugging or modular testing, you can boot the subsystems individually)*

<details>
<summary><b>Boot Subsystems Individually</b></summary>

**Backend (FastAPI)**
```bash
cd nexus-backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements-lock.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend (Next.js 14)**
```bash
cd nexus-frontend
npm install
npm run dev
```

</details>

---

## 💥 Chaos Engineering

NEXUS is engineered to survive infrastructure collapse. You can inject chaos into the mesh via the Operations Command Center to test its resilience:

- **Queue Saturation**: Floods the governance queue to trigger a `GOVERNANCE_FROZEN` state, proving the system blocks speculative simulations to protect data integrity.
- **Inference Timeout**: Forces the sovereign model offline to demonstrate the graceful fallback to the Deterministic Regex Extractor.

---

## 📂 Project Structure

```text
NEXUS-AI/
├── nexus-backend/               # Python/FastAPI Infrastructure
│   ├── app/
│   │   ├── api/                 # Endpoint routers (Simulation, Orchestrator, Auth)
│   │   ├── auth/                # RBAC and Viewport Governance
│   │   ├── chaos/               # Distributed Failure Injectors
│   │   ├── db/                  # SQLite Models & Engine
│   │   ├── events/              # Event Bus & Governance Queue
│   │   ├── services/            # Inference Routers & Watcher Mesh
│   │   └── simulation/          # Bounded Scenario Engine
│   └── tests/                   # Verification and Audit Scripts
│
├── nexus-frontend/              # Next.js 14 Dashboard
│   ├── app/                     # App Router, Layouts, and UI
│   ├── components/              # Topology Graphs and Integrity Panels
│   └── public/                  # Static Assets
│
├── launch_nexus.ps1             # Unified Boot Script
├── launch_nexus_minimal.ps1     # Nuclear Offline Survivability Boot
└── emergency_recovery.md        # Demo Continuation Doctrine
```

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

<div align="center">
  <sub>Built with precision for the Hackathon.</sub>
</div>
