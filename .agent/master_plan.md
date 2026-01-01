# PIC Hub Master Development Plan

## 1. System Vision
A private, self-evolving intelligence center on Mac that leverages diverse AI models (Local, API, Web) to manage massive local data while maintaining absolute privacy and safety.

## 2. Technical Pillars
- **The Hub**: Python-based native orchestrator (`uv` managed).
- **The Hands**: MCP-driven resource access.
- **The Shield**: Mandatory heterogeneous AI code auditing.
- **The Memory**: Structured Vector DB + Human-readable Journal.
- **The Face**: macOS floating "Smart Orbit" UI.

## 3. Development Phases

### Phase 1: Minimum Viable Loop (MVL)
- [ ] Core Dispatcher skeleton.
- [ ] Local File System MCP.
- [ ] Simple Analysis Skill (using only local logic).
- [ ] Basic CLI Trigger.

### Phase 2: The Security Wall
- [ ] Audit Middleware implementation.
- [ ] Restricted Subprocess Execution Environment.
- [ ] Logic/Data separation protocol (Metadata-to-Cloud).

### Phase 3: Browser & UI
- [ ] Playwright-based Subagent with Persistent Profiles.
- [ ] Web-AI as a Provider wrapper.
- [ ] Smart Orbit (Native Mac Wrapper) for monitoring/override.

### Phase 4: Self-Evolution
- [ ] ChromaDB/SQLite memory integration.
- [ ] Skill extraction & Sandbox testing workflow.
- [ ] Evolutionary Pruning logic (Explicit Human confirmation).

### Phase 5: Seamless Remote Access
- [ ] Gateway layer with Tunneling (Cloudflare Tunnel/Tailscale).
- [ ] Mobile-optimized mini-dashboard (PWA).
- [ ] iOS Shortcuts & Remote Push notification for Audits.

---

## 4. Operational Workflow (The Switch)

### Master/Framework Discussions
- Goal: Update the "Laws" of the system.
- Action: Direct modification of `.agent/blueprint.md`.
- Validation: AI must check for regression in existing rules.

### Feature/Skill Sprints
- Goal: Build "Apps" on the framework.
- Action: Isolated development in `skills/` or `mcp-servers/`.
- Validation: Pre-flight Sandbox testing mandatory before merge.

---
*Maintained by PIC Hub Orchestrator*
