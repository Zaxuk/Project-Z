
# Manifesto.md

## 本项目基本法 (V1.0)

### 1. 核心原则 (Core Principles)

* **文档即真理 (Documentation is Source of Truth)**：代码只是文档的可执行版本。当代码逻辑与设计文档（Markdown/Mermaid）冲突时，以文档为准。任何逻辑变更必须先修改文档，再修改代码。
* **上下文优先 (Context First)**：在编写任何具体功能前，必须确保充分理解业务上下文（如：实体状态流转逻辑）。不要猜测，有歧义时必须向人类开发者提问。
* **防御性编程 (Defensive Coding)**：鉴于本项目可能依赖第三方 API，必须假设第三方服务是不稳定的、数据格式可能变更的、响应是延迟的。

---
### 2. 项目目录结构说明
├── .cursorrules               # [核心] 给 AI 的系统级指令（包含技术栈、编码风格等）
├── Technical_Manifesto.md     # [核心] 项目“基本法”，即本文件
├── README.md                  # 项目入口，包含环境搭建和快速启动指南
├── docker-compose.yml         # 本地开发环境（DB, Redis, Mock Server）
├── .env.example               # 环境变量模板
│
├── docs/                      # 文档中心 - AI 的知识源
│   ├── spec/                  # 需求规格说明书
│   │   ├── functional.md      # 功能需求
│   │   └── non_functional.md  # 性能与监控需求
│   ├── design/                # 设计文档
│   │   ├── architecture.md    # 整体架构图 (Mermaid)
│   │   ├── database_schema.md # 数据库设计
│   │   └── sequence_diagrams/ # 关键业务流程时序图
│   ├── adr/                   # 架构决策记录 (Architecture Decision Records)
│   ├── current_status.md      # [核心] 系统现状快照 (定期更新)
│   ├── changelog.md           # 每次对话中更改的内容记录
│   └── api/                   # 对外 API 文档 (OpenAPI/Swagger)
│
├── src/                       # [躯干] 源代码
│   ├── config/                # 全局配置 (Env loader, Constants)
│   │
│   ├── database/              # 数据库层
│   │   ├── migrations/        # SQL 迁移文件
│   │   ├── schema.prisma      # (或 models.py) 数据模型定义
│   │   └── seeds/             # 初始测试数据
│   │
│   ├── libs/                  # 通用工具库
│   │   ├── logger.ts          # 结构化日志封装 (Manifesto 要求)
│   │   └── api_client.ts      # 基础 HTTP 请求封装 (含重试/熔断机制)
│   │
│   ├── modules/               # [核心] 业务领域模块 (按功能拆分，而非按层拆分)
│   │   ├── tracking/          # 核心域：新增业务领域时，创建同级别文件夹
│   │   │   ├── services/      # 业务逻辑
│   │   │   ├── controllers/   # API 路由处理
│   │   │   ├── types.ts       # 领域模型定义
│   │   │   └── tests/         # 模块单元测试
│   │   │
│   │   ├── integration/       # 防腐层：第三方集成
│   │   │   ├── shipping_api/  # 船期聚合 API 的适配器 (Adapter)
│   │   │   └── erp_system/    # 外部 ERP 系统的适配器 (Adapter)
│   │   │
│   │   └── notification/      # 告警与通知模块
│   │
│   └── jobs/                  # 异步任务与队列 (Temporal / BullMQ / Celery)
│   │   ├── workers/           # 具体的消费者逻辑
│   │   └── triggers/          # 定时任务调度配置
│   │
├── web/                       # [门面] 前端应用 (前后端分离)
│   ├── components/            # UI 组件
│   └── pages/                 # 页面路由
│
├── tests/                     # [保障] 端到端测试与集成测试
│   ├── e2e/                   # Playwright/Cypress 脚本
│   ├── integration/           # 跨模块集成测试
│   └── mocks/                 # 第三方 API 的 Mock 数据 (JSON Files)
│
└── scripts/                   # 运维与维护脚本
    ├── setup.sh               # 一键初始化脚本
    └── verify_deployment.sh   # 部署后冒烟测试

---
### 3. 文档更新触发点 (Document Update Triggers)

**AI 必须在以下时刻主动要求或自动执行文档更新：**

* **[触发点 A] 业务逻辑变更**：
* 当修改了核心流程（如：从“轮询”改为“Webhook”），必须先在 `docs/design/sequence_diagram/` 下新建更新后的 Mermaid 时序图,并把原来的时序图文件名标记为已过时。

* **[触发点 B] 数据结构变更**：
* 当新增表或字段时，必须同步更新 `docs/design/database_schema.md` 。
* 如果涉及对外API契约变更，必须同步更新 docs/design/api/ 下的OpenAPI 定义。

* **[触发点 C] 引入新依赖**：
* 当引入新的库或外部服务时，必须更新 `/README.md` 中的“环境配置”部分。

* **[触发点 D] 需求规格说明书**：
每次对话后和ABC触发点触发后，如有必要，同步更新docs/spec下的需求规格说明书

* **[触发点 E] 技术架构文档**：
每次对话后和ABCD触发点触发后，如有必要，同步更新docs/design/architecture.md

* **[触发点 F] 完成里程碑**：
* 每完成一个大 Feature（如“完成订阅功能”），AI 需协助更新 `docs/changelog.md` 和 `docs/current_status.md`（当前系统快照）。

---

### 4. 数据库设计与命名规范 (Database Standards)

* **通用规则**：所有数据库对象使用 `snake_case`（蛇形命名法）。
* **表命名**：
* 使用**复数**形式（例如：`shipment_orders`, `container_milestones`）。
* 联结表使用两个表名连接（例如：`users_roles`）。


* **字段命名**：
* 主键统一为 `id` (UUIDv4 或 BigInt，视具体技术栈定)。
* 外键命名为 `target_table_singular_id`（例如：`shipment_order_id`）。
* 布尔值字段必须加前缀 `is_` 或 `has_`（例如：`is_active`, `has_arrived`）。
* 时间字段统一以 `_at` 结尾（例如：`created_at`, `updated_at`, `eta_at`），存储格式必须为 **UTC ISO-8601**。


* **索引策略**：所有外键字段、用于查询过滤的高频字段（如 `container_no`, `bill_of_lading_no`）必须建立索引。

---

### 5. API 错误处理与交互机制 (Error Handling & Integration)

本项目核心涉及三方 API 调用，需严格遵循以下健壮性设计：

#### 5.1 内部响应标准

所有内部 API 必须返回统一的 JSON 结构：

```json
{
  "success": boolean,
  "data": any | null,
  "error": {
    "code": "ERROR_CODE_UPPERCASE",
    "message": "用户可读的错误描述",
    "details": "调试用详细信息（仅在非生产环境返回）"
  },
  "timestamp": "ISO-8601 String"
}

```

#### 5.2 第三方 API 集成策略 (Anti-Fragile Pattern)

* **隔离层 (Anti-Corruption Layer)**：严禁将第三方 API 的原始数据结构直接透传给前端或外部系统。必须在 Service 层转换为我们自己的领域模型（Domain Model）。
* **重试机制 (Retry Policy)**：
* 对于网络波动（HTTP 502/503/504）或速率限制（HTTP 429），必须实施**指数退避 (Exponential Backoff)** 重试策略。
* 最大重试次数默认为 3 次。


* **死信处理 (Dead Letter)**：
* 当重试耗尽或遇到不可恢复错误（如 HTTP 400/401/404）时，必须将任务标记为 `FAILED`，并将原始请求与错误响应记录到 `integration_logs` 表中，同时触发告警。


---

### 6. 代码与测试规范 (Code & Testing)

* **注释即文档**：复杂的业务逻辑必须包含清晰的注释，解释“为什么”这样做，而不仅仅是“做了什么”。
* **自动化测试要求**：
* **Unit Test**：对于所有数据转换函数（Transform Logic），必须生成覆盖边缘案例（如空值、非法格式）的测试用例。
* 单元测试覆盖率 > 80%
* **Integration Test**：对于核心流程（DB -> API -> DB），必须编写 Mock 测试，严禁在测试中真实调用外部付费 API。

* 集成测试覆盖关键流程
* E2E 测试覆盖用户旅程

* **日志规范**：
* 使用结构化日志（JSON Logs）。
* 关键节点（API 请求发出前、收到响应后、任务创建时）必须打 Log，且包含 `trace_id` 以便全链路追踪。

---

### 7. AI 协作指令 (Instructions for AI Agent)

* **拒绝模糊**：如果用户的指令模糊（例如“优化一下性能”），请先列出可能的优化方向（数据库索引？缓存？并发？），让用户选择后再执行。
* **自我审查**：在生成代码后，请自问：“这段代码是否符合 `manifesto.md` 中的错误处理规范？”如果不符合，请自动修正。
* **小步提交**：不要一次性生成 500 行以上的代码。采用“分析 -> 方案确认 -> 实现 -> 验证”的循环。

---
