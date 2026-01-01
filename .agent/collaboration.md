# AI Collaboration & Evolution Strategy

This document defines how the User and AI Agents cooperate within the Project JANUS ecosystem to overcome context window limitations and maintain system integrity.

## 1. The Source of Truth
**The File System is the only Truth.**
- Conversation history is volatile. All key architectural decisions, security rules, and skill schemas MUST be persisted in `.agent/blueprint.md` or this document.
- Never assume a future AI can read the chat history of a past session.

## 2. Session Management (The Branching Model)

### A. The Master Session (Command Center)
- **Role**: Architect & Judiciary.
- **Tasks**: Defining the Hub core, managing `blueprint.md`, resolving conflicts, and high-level project management.
- **Context Management**: When this session gets too long, summarize the current state into `project.md` and start a new "Clean Master Session".

### B. Specialist Sessions (Feeder Chats)
- **Role**: Developer & Debugger.
- **Scope**: Narrowly focused on one MCP server or one Agent Skill.
- **Workflow**:
  1. Boot from `BOOTSTRAP.md`.
  2. Implement the logic.
  3. Validate in Sandbox.
  4. Merge results back to `/skills` or `/mcp-servers`.

## 3. Operational Modes (Executing the Switch)

### Mode A: Blueprinting (Framework Discussion)
- **Focus**: Updating the core laws, security, and protocols.
- **Rules**: AI must freeze development and update `.agent/blueprint.md` as the primary action. No code is written until the law is set.

### Mode B: Sprinting (Feature Development)
- **Focus**: Building specialized Skills or MCP servers.
- **Rules**: AI follows the "Constitution" in `blueprint.md`, performs sandbox testing, and only updates `project.md` and the relevant sub-directory.

## 4. Conflict Resolution
In case of logical contradictions between "Past Knowledge" and "New Instructions":
- **Priority**: Latest User Explicit Instruction > Current Journal > Old Skill Metadata.
- **Action**: Pause and trigger an "Explicit Human Confirmation" via the Dashboard/Terminal.

---
*Maintained by the Hub Orchestrator*
