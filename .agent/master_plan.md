# Project JANUS 开发路线图 (Master Plan)

## 1. 愿景 (System Vision)
在 Mac 上构建私有、自进化的智能中心。利用多样化的模型（本地、API、Web）管理海量数据，同时保持绝对的隐私和安全。

## 2. 核心支柱 (Technical Pillars)
- **中枢 (The Hub)**：基于 Python 的原生编排器（`uv` 管理）。
- **执行 (The Hands)**：MCP 驱动的资源访问。
- **守卫 (The Shield)**：强制性的异构 AI 代码审计。
- **记忆 (The Memory)**：结构化向量库 + 人类可读日志。
- **交互 (The Face)**：macOS 悬浮“Smart Orbit”交互界面。

## 3. 开发阶段 (Development Phases)

### Phase 1: 最小可用闭环 (MVL)
- [ ] 核心调度器 (Dispatcher) 骨架。
- [ ] 本地文件系统 MCP 连接器。
- [ ] 基础分析技能 (仅本地逻辑)。
- [ ] 基础 CLI 触发指令。

### Phase 2: 安全防御基石 (Security Wall)
- [ ] 审计中间件 (Audit Middleware) 实现。
- [ ] 受限子进程执行环境。
- [ ] 逻辑/数据分离协议 (Metadata-to-Cloud)。

### Phase 3: 浏览器与交互 (Browser & UI)
- [ ] 基于 Playwright 的持久化浏览器子代理。
- [ ] Web 端 AI 供给侧封装。
- [ ] Smart Orbit (Mac 原生包裹层) 监控与接管。

### Phase 4: 自进化与记忆 (Evolution & Memory)
- [ ] ChromaDB/SQLite 记忆库集成。
- [ ] 技能提取与沙箱测试流。
- [ ] 进化修剪逻辑（需用户显式确认）。

### Phase 5: 无缝远程访问 (Remote Access)
- [ ] 网关层与加密隧道 (Cloudflare Tunnel/Tailscale)。
- [ ] 移动端优化仪表盘 (PWA)。
- [ ] iOS 快捷指令集成与远程审计推送。

---

## 4. 运行模式切换 (Operational Workflow)

### 模式 A: 蓝图讨论 (框架设计)
- **目标**：更新系统的“法律”和核心规约。
- **动作**：直接修改 `.agent/blueprint.md`。不写具体代码，直到法则确立。

### 模式 B: 冲刺开发 (功能实现)
- **目标**：在框架下构建具体的技能或 MCP Server。
- **动作**：在子目录进行隔离开发，必须通过沙箱测试后方可合并。

---
*Last Updated: 2026-01-02*
