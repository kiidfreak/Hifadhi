# Hifadhi V2: Global AI Hiring OS Architecture

## 1. Core Philosophy
Hifadhi V2 is not a CRUD application. It is an **Agentic Operating System**. 
- **Old Way:** User clicks "Screen" -> System runs a function -> Returns result.
- **New Way:** User sets a Goal ("Hire a Senior Dev") -> Orchestrator spawns Agents -> Agents plan, execute, collaborate, and report back.

## 2. System Components

### A. The Orchestrator (The "Boss")
- Receives high-level goals from the user.
- Decomposes goals into sub-tasks.
- Assigns tasks to specialized agents.
- Manages the global state and memory.

### B. Specialized Agents (The "Team")
1.  **🕵️ Sourcing Agent:** Scans databases, LinkedIn (simulated), and job boards.
2.  **🧠 Screening Agent:** Analyzes resumes against JDs, checks compliance (GDPR/EEOC).
3.  **🗣️ Interview Agent:** Schedules calls, generates questions, conducts AI video/text interviews.
4.  **⚖️ Compliance Agent:** Audits every decision for bias and legal risks.
5.  **💰 Economics Agent (PayLink):** Handles payments for tests, bounties, and contractor payouts.

### C. The Event Bus (The "Nervous System")
Agents communicate via an event bus (e.g., `AgentEvent`).
- `CANDIDATE_FOUND` -> triggers Screening Agent
- `SCREENING_PASSED` -> triggers Interview Agent
- `INTERVIEW_PASSED` -> triggers Compliance Check

## 3. Data Architecture (Multi-Tenant)
- **Organization ID:** All data partitioned by `org_id`.
- **Audit Logs:** Immutable logs of *why* an agent made a decision (critical for global compliance).

## 4. Integration Layer
- **ATS Connectors:** Webhooks/APIs for Greenhouse, Lever, etc.
- **Communication:** Slack/Teams/Email integration for agent notifications.

## 5. Implementation Roadmap (Phase 1)
1.  **`agent_engine.py`:** Implement the base `Agent` and `Orchestrator`.
2.  **`tools/`:** Migrate existing tools (database, email) into the new agent tool format.
3.  **`dashboard_v6.html`:** A "Mission Control" UI that visualizes agent thoughts and active workflows.

---
**Status:** Drafted
**Version:** 2.0.0
