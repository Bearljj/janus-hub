# Project JANUS (雅努斯)

> **构建属于你的数字大脑 —— 私有、代理化、且具有自我演进能力。**

Project JANUS 是一个独立的模块化 AI 框架，旨在协调多个专业智能体（Skills），并通过模型上下文协议（MCP）连接本地资源。

## 🌟 核心哲学 (Philosophy)
- **逻辑与执行分离 (Logic & Execution Separation)**：智能大脑在云端（或强力本地 LLM），执行手脚留在本地硬件。
- **审计先行 (Audit-First)**：永不信任，始终验证。所有 AI 生成的代码在运行前必须经过异构模型审计。
- **进取式修剪 (Evolutionary Pruning)**：系统自动建议并测试改进方案，通过显式“减法”逻辑保持系统的高性能天花板。

## 🚀 快速开始
1. **环境初始化**：
   ```bash
   cp .env.example .env
   # 填入你的 API Key 或本地 LLM 终端地址
   ```
2. **AI 开发引导**：如果你正使用 AI 助手开发本项目，请立即引导其阅读 `BOOTSTRAP.md`。
3. **运行 Hub**：(Phase 1 开发中)

## 📡 协作策略 (Collaboration)
为防止上下文窗口膨胀并保持高推理质量，我们采用 **“主/支线会话模型”**：
- **主会话 (Master Session)**：充当“架构师”，负责高层设计、安全策略和跨技能审计。
- **专项会话 (Specialist Sessions)**：充当“开发员”，专注于构建单一 MCP 服务或 Skill。

*详细指南请参阅 [`.agent/collaboration.md`](./.agent/collaboration.md)*

---
*Created by Harold Yao & Antigravity (2026-01-02)*
