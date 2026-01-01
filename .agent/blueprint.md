# Project JANUS 架构蓝图 (Blueprint) v0.1

## 1. 项目概述 (Overview)
Project JANUS 是一个模块化的 AI 系统框架，优先考虑数据隐私、可扩展性和智能体间协作 (A2A)。

## 2. 系统分层 (Layers)
### A. 编排层 (The Hub Core)
- **角色**：意图识别、路由分发、子代理监督。
- **组件**：调度器 (`Dispatcher`)、审计中间件 (`AuditMiddleware`)、上下文管理器 (`ContextManager`)。
- **逻辑**：使用最强模型进行规划；使用最高效模型进行执行。
- **扩展**：`GatewayLayer` (Phase 5) 负责加密远程隧道与手机推送同步。

### B. 能力层 (Agent Skills)
- **角色**：封装的专家逻辑。
- **标准**：遵循 ADK 启发的 `AgentCard` 架构（包含 ID、名称、描述、示例、元数据）。
- **存储**：`skills/active/`。

### C. 资源层 (MCP & Execution)
- **角色**：对物理工具和数据的访问。
- **协议**：模型上下文协议 (MCP)。
- **安全**：针对未验证代码在沙箱环境中执行。

## 3. 核心协议 (Key Protocols)
### 审计协议 (Audit Protocol - 宁慢必审)
1. **生成**：逻辑 Agent 生成代码。
2. **拦截**：Hub 中间件拦截其请求并送往审计 Agent。
3. **验证**：静态分析 + 基于 LLM 的意图校验。
4. **结果**：通过 (PASS) / 驳回修改 (REJECT) / 提请人工裁决 (ESCALATE)。

### 进化修剪协议 (Pruning Protocol)
- 只有在以下条件达成时，新技能才替换旧技能：
  1. 沙箱验证通过。
  2. 生成性能与重合度报告。
  3. 用户通过 UI 界面显式同意。

## 4. 交互形态 (Interaction)
- **悬浮球 (Smart Orbit)**：Mac 原生 UI 元素。
- **状态**：静默 (Dormant)、思考 (Reasoning)、执行 (Action)、告警 (Alert)。
- **手动接管**：双击即可由隐藏后台推送到前台接管浏览器子代理。

## 5. 记忆系统 (Memory System)
- **Shadow Layer (影子层)**：向量数据库，用于技能映射和偏好检索。
- **Mirror Layer (镜像层)**：Markdown 格式的维护日志，用于决策追踪和冲突解决。

## 6. 技术术语映射 (Terminology Mapping)
*For future AI developers: Maintain these terms in English within code and metadata.*
- **HubCore**: The central orchestration engine (调度中枢).
- **AgentSkill**: Encapsulated business logic or expert capability (代理技能).
- **MCP Server**: Model Context Protocol driver for physical resources (资源连接驱动).
- **AuditMiddleware**: The safety interceptor between generation and execution (审计中间件).
- **Pruning**: The act of reducing complexity by deprecating skills (进化修剪).
