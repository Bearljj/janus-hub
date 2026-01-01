# PIC Hub Architecture Blueprint v0.1

## 1. Overview
PIC Hub is a modular AI system framework. It prioritizes data privacy, scalability, and AI-to-AI (A2A) collaboration.

## 2. Layers
### A. Orchestration Layer (The Hub Core)
- **Role**: Intent resolution, routing, and sub-agent supervision.
- **Components**: `Dispatcher`, `AuditMiddleware`, `ContextManager`.
- **Logic**: Use the most capable model available for planning; use the most efficient model for execution.
- **Extension**: `GatewayLayer` for encrypted remote tunneling and mobile push synchronization (Phase 5).

### B. Capability Layer (Agent Skills)
- **Role**: Encapsulated expert logic.
- **Standard**: Follows ADK-inspired `AgentCard` schema (ID, Name, Description, Examples, Metadata).
- **Storage**: `skills/active/`.

### C. Resource Layer (MCP & Execution)
- **Role**: Physical access to tools and data.
- **Protocol**: Model Context Protocol (MCP).
- **Safety**: sandboxed execution for unverified code.

## 3. Key Protocols
### The Audit Protocol (寧慢必審)
1. **Generation**: LogicAgent produces code.
2. **Interception**: Hub intercepts and sends to AuditAgent.
3. **Verification**: Static analysis + LLM-based intent check.
4. **Result**: `PASS` (Proceed) / `REJECT` (Fix & Loop) / `ESCALATE` (Ask User).

### The Pruning Protocol (进化修剪)
- New Skill replaces Old Skill only after:
  1. Sandbox validation passes.
  2. Performance/Overlap report generated.
  3. Explicit User approval received via UI.

## 4. Interaction (Smart Orbit)
- **Floating Ball**: A native Mac UI element.
- **States**: Dormant, Reasoning, Action, Alert.
- **Manual Override**: Double-click to reveal hidden browser sub-agent.

## 5. Memory System
- **Vector DB**: Fast semantic retrieval for Skill mapping and User preferences.
- **Journal**: Markdown-based human-readable logs for decision tracking and conflict resolution.

---
*Archived in .agent/blueprint.md*
