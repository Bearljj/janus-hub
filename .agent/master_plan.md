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

### Phase 5: 无缝移动感知 (Mobile Perception)
- [x] 时间意识与“午夜自省”仪式。
- [x] 感知总线与自律快速通道 (is_auto_run)。
- [ ] iOS 快捷指令集成与远程审计推送 (Discussed).
- [ ] 移动端状态监控 (Satellite Node).

### Phase 6: 生命化与协同演化 (Vitality & Collaborative Synergy)
- [ ] **交互生命化 (Interactive Vitality)**:
    - **听力与发送 (Voice First)**: 集成唤醒词识别 (KWS) 与快速 TTS/STT 闭环，实现“不见而知”的交互。
    - **晨间报告**: 每日初次唤醒时，由 AI 汇总前日记忆蒸馏、偏好沉淀与自修复结果。
    - **TUI 状态墙**: 基于 `rich` 库构建具备 TUI 质感的“生命体征墙”。
- [ ] **功能代谢 (Functional Metabolism)**:
    - 实现对冗余/臃肿技能的自动识别、解耦与重组。
- [ ] **多模型协同 (Brain Ensemble)**:
    - **异构审计**: 实现由 Claude 生成代码、GPT-4o 审计设计一致性、Gemini 归纳记忆的流水线。
    - **分布式智网**: 在多台设备（Mac/PC/Cloud）间实现记忆与意志的实时对齐。

---

## 4. 核心协议标准 (Core Protocols)

### 4.1 感知对齐协议 (Perception Alignment)
- **准则**: **指令-介质不相关性 (Medium Irrelevance)**。
- **要求**: 
    - 语音输入 (AudioSensor) 必须与文字输入在 `Intent` 层级实现语义对齐。
    - 识别过程 (STT) 需与感知监听解耦，确保系统可接入不同的识别引擎而不影响调度逻辑。
    - 所有感知信号（文本、语音、传感器信号）最终应被转化为统一的 `Intent` 对象分发给技能。

### 4.2 解耦发布协议 (Outbound Decoupling)
- **准则**: **意图与渠道分离 (Intent-Channel Separation)**。
- **架构**:
    - **发起端**: 技能通过 `context.emit("outbound", ...)` 发起发送请求，不关心具体渠道。
    - **路由端**: 由 `ReflexRule` 根据用户的 `Preference` 记忆，动态决定是通过通知、IM、邮件还是语音播报。
    - **渠道端**: 每一个发送渠道（如 Slack, MacOS Notify）作为独立基因管理。
- **发布协同 (Publication Ensemble)**:
    - **智能润色 (The Editor)**: 在正式发出前，由异构模型（如 GPT-4o）对主脑生成的回复进行语气润色，确保符合用户的 `Preference` 记忆（如：专业、简洁、或幽默）。
    - **裁判与防错 (The Referee)**: 检查回复内容是否包含敏感数据，或是否背离了当前的上下文语境。

---

## 5. 运行模式切换 (Operational Workflow)

### 模式 A: 蓝图讨论 (框架设计)
- **目标**：更新系统的“法律”和核心规约。
- **动作**：直接修改 `.agent/blueprint.md`。不写具体代码，直到法则确立。

### 模式 B: 冲刺开发 (功能实现)
- **目标**：在框架下构建具体的技能或 MCP Server。
- **动作**：在子目录进行隔离开发，必须通过沙箱测试后方可合并。

---
*Last Updated: 2026-01-03 10:11* (Design Lock Established)
