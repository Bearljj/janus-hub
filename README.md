# PIC Hub (Private Intelligence Center)

> **Build your own digital brain - Private, Agentic, and Self-Evolving.**

PIC Hub is an independent, modular AI framework designed to orchestrate multiple specialized agents (Skills) and connect them to local resources via the Model Context Protocol (MCP).

## 🌟 Core Philosophy: "The PIC Way"
- **Logic & Execution Separation**: Brains stay in the cloud (or strong local LLM), hands stay on local hardware.
- **Audit-First**: Never trust, always verify. Every piece of AI-generated code is audited before execution.
- **Evolutionary Pruning**: The system automatically suggests and tests improvements, keeping the performance ceiling high.

## 🚀 Getting Started
1. **Initialize Environment**:
   ```bash
   cp .env.example .env
   # Fill in your API keys or local LLM endpoints
   ```
2. **Onboard your AI**: If you are using an AI assistant to develop this, point it to `BOOTSTRAP.md` immediately.
3. **Run Hub**: (Coming Soon in Phase 1)

## 📡 Collaboration Strategy
To prevent context window bloat and maintain high reasoning quality, we use a **Master/Specialist Session** model:
- **Master Session**: (The Architect) High-level design, security policy, and cross-skill auditing.
- **Specialist Sessions**: (The Developers) Dedicated chats for building single MCP servers or Skills.

*Detailed guide available at [`.agent/collaboration.md`](./.agent/collaboration.md)*

---
*Created by Harold & Antigravity (2026-01-01)*
