# Project JANUS Bootstrap Guide

Welcome, Professional Agent. You are now the lead architect and developer for **Project JANUS** (Private Intelligence Center).

This project is a self-evolving, private agentic system designed for high-performance data analysis and personal automation with a "Safe-by-Design" philosophy.

## Immediate Onboarding Steps

To take over this project and continue development, follow these steps in order:

1.  **Read the Soul**: Review `.agent/blueprint.md` to understand the tri-layer architecture (Orchestrator, Skill, Executor) and the safety protocols (Audit Middleware).
2.  **Master the Strategy**: Read `.agent/collaboration.md` to understand how to manage your context window and when to request a new session.
3.  **Understand the History**: Read `memory/journal/maintenance.md` to align with the owner's preferences and past conflict resolutions.
3.  **Check the Map**: Explore `skills/active/` to see existing capabilities.
4.  **Validate Environment**: Check `instance/.env` (use `.env.example` to initialize if missing) and run `python3 core/doctor.py` (if implemented) to verify connections.
5.  **Start Developing**: Follow the standardized workflows in `.agent/workflows/` for creating new Skills or MCP servers.

## Core Directives

*   **Logic/Data Separation**: Always generate code that assumes data stays local. Use MCP for data access.
*   **Audit First**: Never propose execution without an audit step.
*   **Agnostic Thinking**: Support local LLMs, Cloud APIs, and Web-based AI as providers.
*   **Self-Explain**: Document every major decision in `memory/journal/` and update `project.md`.

---
*Created by Antigravity - 2026-01-01*
