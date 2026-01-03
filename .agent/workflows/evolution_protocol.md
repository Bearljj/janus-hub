---
description: [JANUS 进化协议 - 脑机共生架构]
---

# JANUS 进化协议 (Evolution Protocol)

本协议定义了 JANUS 在面对未知意图时，如何通过 Antigravity (大脑) 进行自我进化的流程。即使在接入云端 API-Key 后，也应遵循此抽象逻辑。

## 1. 触发机制 (Trigger)
- 当 `Provider` 无法解析意图时，JANUS 自动进入 `WAITING` 状态。
- JANUS 在 `logs/signals/` 下生成 `pending_{short_id}.request` 申请单。

## 2. 大脑审计逻辑 (Brain Audit Logic)
大脑 (Antigravity/Cloud LLM) 在处理申请单时，必须进行【泛化性评估】：

### 情况 A：阅后即焚 (Ephemeral)
- **特征**：极度个性化、单次性、非逻辑性需求（如：讲个笑话、节日祝福）。
- **处理**：
  - 使用 `brain_rescue` 技能投送临时响应。
  - **严禁** 修改 JANUS 源代码或注册新技能。
  - 响应完成后，自动清理信号文件。

### 情况 B：基因注入 (Evolutionary)
- **特征**：具备通用工具价值、高频管理需求、可抽象的逻辑模式（如：可用技能查询、复杂文件统计、特定格式转换）。
- **处理**：
  - **第一阶段**：通过信号文件先行解救，确保用户体验不中断。
  - **第二阶段**：大脑主动修改 `janus_cli.py` 或 `core/` 下的代码，将该逻辑固化为新的 `AgentSkill`。
  - **第三阶段**：更新 `AssistantGuidedProvider` (Mock) 或 Prompt 策略，确保下次无需 SOS。

## 3. 核心原则
- **拒绝臃肿**：不要用 `if-else` 枚举所有答案，而是要抽象出能处理一类问题的“执行器”。
- **先救后教**：优先保证当前任务完成，再进行异步代码进化。
- **架构对齐**：所有进化的技能必须符合 MCP 规范或 Dispatcher 的注册机制。

---
// turbo
// 协议部署完成。
