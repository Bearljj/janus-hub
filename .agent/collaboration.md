# AI 协作与进化策略 (Collaboration Strategy)

本文件定义了用户与 AI 在 Project JANUS 生态中如何协作，以克服上下文窗口限制并保持系统完整性。

## 1. 唯一真理来源 (Source of Truth)
**文件系统是唯一的真理。**
- 会话记录是挥发性的。所有重大的架构决定、安全规则和技能规约必须持久化在 `.agent/` 目录中。
- 绝不假设未来的 AI 能读取过去会话的聊天记录。

## 2. 会话管理协议 (Session Management Protocol)

### A. 主会话 (Master Session - Command Center)
- **角色 (Role)**: 架构师与法官 (Architect & Judiciary).
- **职责**: 定义 Hub 内核、管理蓝图、解决冲突、全局安全审计。
- **状态维护**: 当会话过长时，必须将当前状态总结到 `project.md` 中，并开启新的“干净”主会话。

### B. 专项会话 (Specialist Sessions - Feeder Chats)
- **角色 (Role)**: 开发员与调试员 (Developer & Debugger).
- **范围**: 严格专注于单一 MCP Server 或单一 Agent Skill。
- **工作流 (Workflow)**:
  1. 通过 `BOOTSTRAP.md` 初始化认知。
  2. 实现逻辑代码。
  3. 在沙箱 (Sandbox) 中验证。
  4. 提交成果至 `/skills` 或 `/mcp-servers`。

## 3. 运行模式切换 (Operational Modes)

### 模式 A: 蓝图讨论 (Blueprint Mode)
- **场景**：修改核心法律、安全策略或通信协议。
- **规则**：AI 必须挂起所有开发任务，以修改 `.agent/blueprint.md` 为首要动作。

### 模式 B: 功能冲刺 (Sprint Mode)
- **场景**：编写具体代码。
- **规则**：AI 遵循蓝图约束，仅在 `project.md` 和相应子目录内活动。

## 4. 文档语言与结构规约 (Document Language & Structuring Protocol)

为平衡人类阅读体验与 AI 推理效率，所有系统文档必须遵循以下标准：

- **中英双语混合 (Bilingual Hybrid)**：
  - 使用 **中文** 进行叙述、意图说明和用户偏好描述（高感性度、高语境容量）。
  - 在核心技术术语、协议、状态名后必须保留 **英文锚点**（例如：审计中间件 `AuditMiddleware`）。
- **抗熵增结构 (Anti-Entropy Structure)**：
  - 禁止单纯在文档末尾追加内容。新信息必须**集成 (Integrate)** 进既有的逻辑章节中。
  - 术语使用必须参考 `.agent/blueprint.md` 中的 **Terminology Mapping**。
- **可机器读取 (Machine Readable)**：
  - 核心配置项、Schema 定义和流程逻辑应使用列表、表格或伪代码等结构化形式呈现。

## 5. 冲突解决
若“过去的知识”与“新的指令”产生逻辑矛盾：
- **优先级**：用户最新的显式指令 > 当前维护日志 > 旧技能元数据。
- **行动**：暂停并手动通过仪表盘或终端触发“用户显式确认”。

---
*Maintained by Janus Hub Orchestrator*
