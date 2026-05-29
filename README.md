NEXUS-AI

Overview

NEXUS is not an AI wrapper.

NEXUS is an institutional operating system that bridges chaotic real-world event streams with deterministic strategic execution.

It consumes unstructured market events and transforms them into bounded, replayable, and governed cognitive projections.

By wrapping sovereign AI inference in deterministic evidence pipelines, verifiable state graphs, and strict Role-Based Access Control (RBAC), NEXUS prevents the operational entropy common in probabilistic LLM systems.

NEXUS does not predict the future.
It simulates bounded strategic trajectories constrained by replayable evidence.

---

Key Features

Deterministic Extraction

Transforms unstructured payloads into validated structured state using strict JSON schema enforcement.

Strategic Memory Graph

Stores knowledge in a localized temporal graph for deterministic replayability.

Institutional Governance

Detects contradictions and evidence saturation.

When inconsistencies occur, NEXUS enters:

"GOVERNANCE_FROZEN"

to preserve institutional truth.

Bounded Simulation

Runs counterfactual strategic projections with confidence decay over extended horizons.

Graceful Degradation

If sovereign inference fails, NEXUS falls back to deterministic regex extraction while maintaining system continuity.

---

Architecture Roles

SYSTEM_ADMIN

Full topology access, heartbeat visibility, and chaos event control.

EXECUTIVE

Strategic dashboard with filtered institutional signal.

ANALYST

Simulation access with governance restrictions.

---

Prerequisites

- Node.js v20+
- Python 3.11+
- SQLite3

---

Quick Start

Windows

Run full stack:

.\launch_nexus.ps1

---

launch_nexus.ps1

Write-Host "Starting NEXUS Backend..."

Set-Location nexus-backend

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

Start-Process powershell -ArgumentList `
"-NoExit", `
"-Command", `
"uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Set-Location ..\nexus-frontend

npm install

npm run dev

---

Backend Manual Boot

cd nexus-backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload

---

Frontend Manual Boot

cd nexus-frontend
npm install
npm run dev

---

Project Structure

NEXUS-AI/
├── nexus-backend/
│   ├── app/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── chaos/
│   │   ├── db/
│   │   ├── events/
│   │   ├── services/
│   │   └── simulation/
│   └── tests/

├── nexus-frontend/
│   ├── app/
│   ├── components/
│   └── public/

├── launch_nexus.ps1
├── launch_nexus_minimal.ps1
└── emergency_recovery.md

---

License

MIT License

Built for precision.
Built for resilience.
Built for institutional execution.

