# NEXUS: Governed Cognitive Infrastructure
## Technical Whitepaper & Operational Guide

**Target Audience:** Hackathon Judging Panel (AI Researchers, CTOs, PMs, Enterprise Architects)
**Project Status:** Version 1.0.0 (Production Candidate)

---

## 1. Executive Summary: The Problem Space

Modern enterprise architecture is currently plagued by the fundamental unreliability of Large Language Models (LLMs). When deployed against dynamic, unstructured data streams (market intelligence, regulatory filings, competitor moves), raw LLMs exhibit fatal flaws:
- **Operational Entropy (Hallucinations):** Probabilistic token prediction generates plausible but structurally false assertions.
- **Context-Window Amnesia:** Rolling context windows rapidly lose deterministic relationships as temporal horizons expand.
- **Data Governance Failure:** Autonomous agents given free rein mutate internal state without verifiable chains of evidence.

**The Problem:** You cannot run an institution on probabilistic memory. 

**The NEXUS Solution:** NEXUS is an institutional operating system that bridges the gap between chaotic real-world event streams and deterministic strategic execution. It wraps sovereign AI inference in a strict shell of deterministic extraction, verifiable temporal graphs, and strict Role-Based Access Control (RBAC). *NEXUS does not predict the future; it simulates bounded strategic trajectories constrained by replayable evidence.*

---

## 2. Architectural Blueprint & Map

NEXUS operates on a strict multi-layered architecture designed for resilience and deterministic truth.

### Core Subsystems
1. **The Ingestion & Scraping Mesh (Browser Pool)**
   - Uses headless Puppeteer browsers managed via DOM stability checks to securely scrape unstructured HTML from market targets.
2. **Deterministic Extraction Pipeline (Semantic Engine)**
   - Unstructured data bypasses raw LLM generation. Instead, inference routers force the LLM into a strict JSON-schema compliance mode to extract verified entities (Companies, Sectors) and Signals (e.g., `MARKET_EXPANSION`, `PRICING_COMPRESSION`).
3. **Temporal Knowledge Graph (SQLite + Network Mesh)**
   - Extracted intelligence is mapped to a strictly relational graph. Rather than storing volatile vector embeddings, NEXUS anchors relationships structurally. This enables precise temporal replayability ("What did the market topology look like in January?").
4. **Governance Queue & Integrity Monitor**
   - Ingested data enters a queue. If the system detects logic contradictions or queue saturation, it triggers a `GOVERNANCE_FROZEN` lock, pausing mutations to preserve institutional truth.
5. **Role-Based Cognitive Viewports (RBAC)**
   - Institutional context is gated by role. A `SYSTEM_ADMIN` sees raw topological logs; a `CHIEF_EXECUTIVE_OFFICER` experiences a muted, high-level dashboard shielded from operational noise.

---

## 3. Comprehensive Feature Set

### 3.1. Interactive Temporal Knowledge Graph
- **Dynamic Node Rendering:** Visualizes relationships between `Company` entities and `Signal` nodes across sectors.
- **De-cluttered UX:** Smart visibility rules (recently implemented) hide massive Signal labels by default, revealing localized textual context smoothly via CSS hover groups, avoiding UI overlap.

### 3.2. Strategic Intelligence Copilot
- **Context-Aware Inference:** An embedded Chat UI that queries the graph. It dynamically injects the `activeSector` and `activePersona` into the System Prompt.
- **Bounded Responses:** The Copilot refuses to answer based on arbitrary LLM memory; it strictly cites the structural graph constraints provided to it in the background context pipeline.

### 3.3. Evidence Explainability Panel
- **Zero-Trust AI:** When the Copilot synthesizes a strategic insight, it generates `evidence_anchors`. The Explainability Panel visually maps these synthesized insights directly back to the raw, scraped source strings. 

### 3.4. Temporal Rail (Time Travel)
- **Live vs. Replay Modes:** Users can drag a timeline slider to morph the graph state to previous historical snapshots. The graph initiates an interactive `REWINDING` animation, allowing analysts to view the exact market state before major events occurred.

### 3.5. System Integrity Dashboard
- **Real-Time Heartbeat:** Monitors Database Sync (SQLite Write Latency), Scraper Thread stability, and overall System Entropy.

### 3.6. Chaos Engineering & Graceful Degradation
- **Failure Injection:** The system is built to survive its own intelligence. If the LLM goes offline (Inference Timeout), the system downgrades to a fallback `Deterministic Regex Extractor`. The mesh survives without its smartest node.

---

## 4. Development Log: What We Built So Far

Over the course of the hackathon, the following milestones were achieved and stabilized:
1. **Full-Stack Initialization:** Next.js 14 Frontend coupled with a FastAPI asynchronous backend.
2. **Database & Seeding:** Configured a scalable SQLite architecture seeded with deterministic demo data encompassing multiple sectors (Cyber Security, Fintech, AgTech, Productivity SaaS).
3. **Graph Morphing Engine:** Built the D3/SVG frontend capable of recalculating graph coordinates smoothly based on temporal shifts.
4. **Copilot Synchronization Fixes:** Resolved critical bugs where the Copilot queried across unbounded sectors. We tightly coupled the UI's `activeSector` state directly into the FastAPI request payload, strictly gating LLM inference to the active viewport.
5. **UI/UX Polishing:** Solved complex React state-rendering issues, fixed unbalanced HTML DOM structures that broke layouts, and implemented advanced CSS tailwind hover-states for a highly premium, executive-level aesthetic.
6. **Codebase Consolidation:** Cleared out residual nested Git repositories, ignored monolithic dependencies (like downloaded Chromium binaries), and successfully achieved a clean CI/CD push to the master branch.

---

## 5. Strategic Roadmap: Future Implementations

While NEXUS is production-ready for the demo, our roadmap includes:
1. **Live Autonomous Agents:** Transitioning the scraper from periodic fetching to autonomous, self-directed web surfing based on detected gaps in the Knowledge Graph.
2. **Multi-Modal Evidence:** Allowing the Explainability Panel to anchor insights not just to text, but to screenshots of competitor pricing pages captured at specific UNIX timestamps.
3. **Enterprise SSO & Audit Logs:** Implementing strict cryptographic signing for every graph mutation, satisfying extreme regulatory compliance (e.g., SOC2, FINRA).

---

## 6. Official User Guide: How to Operate NEXUS Effectively

*For Judges and Demonstrators evaluating the system.*

### Step 1: Navigating Viewports (Roles & Sectors)
1. At the top of the UI, use the **Persona Selector** to choose an identity (e.g., `Chief Executive Officer`, `Threat Intelligence`). 
2. Notice how the visual aesthetics and system feedback immediately adapt to your role.
3. Select an **Active Sector** (e.g., `Cyber Security`). The Knowledge Graph will instantaneously re-render to display only the competitors and signals relevant to that vertical.

### Step 2: Temporal Analysis (Time Travel)
1. Locate the **Temporal Rail** (Timeline) at the bottom or side of the screen.
2. Change the Session Mode from `LIVE` to `REPLAY`.
3. Scrub the timeline to a past date (e.g., "Competitor Bankruptcy"). 
4. Watch the Knowledge Graph elegantly regress to its historical state, demonstrating absolute deterministic memory retention.

### Step 3: Engaging the Intelligence Copilot
1. Open the **Command Center / Copilot** on the right pane.
2. Ask a high-level strategic query: *"Summarize the current pricing compression threats in this sector."*
3. The system will consult the **current graph topology** and provide a synthesis. 
4. **Crucial:** Look at the **Explainability Panel**. You will see exactly *why* the LLM made its assertion, anchored mathematically to raw evidence ingested by the scrapers.

### Step 4: Observing System Integrity
1. Check the top or left **Integrity Dashboard**. 
2. Observe the Database Sync status and active Scraper threads. This proves the application is a live, breathing infrastructure, not a mocked frontend prototype.

---

### Conclusion

NEXUS represents a paradigm shift in applied AI. We are not generating prose; we are compiling truth. Thank you for your review.
