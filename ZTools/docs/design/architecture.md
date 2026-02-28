# 技术架构文档

## 1. 系统架构概览

ZTools 采用 **Skill-based Architecture**（基于技能的架构），通过 iFlow Skill 机制提供模块化的自动化工具。

```mermaid
graph TB
    subgraph "用户层"
        User[用户]
    end

    subgraph "iFlow CLI"
        IFlow[iFlow CLI]
    end

    subgraph "Skill 层"
        ZentaoHelper[禅道自动化助手]
    end

    subgraph "核心模块"
        NLP[NLP 模块]
        Auth[认证模块]
        API[API 客户端]
        Collectors[信息收集器]
        Automators[自动化操作器]
    end

    subgraph "外部服务"
        Zentao[禅道服务器]
    end

    User --> IFlow
    IFlow --> ZentaoHelper
    ZentaoHelper --> NLP
    ZentaoHelper --> Auth
    ZentaoHelper --> API
    ZentaoHelper --> Collectors
    ZentaoHelper --> Automators
    API --> Zentao

    style ZentaoHelper fill:#e1f5ff
    style NLP fill:#fff4e6
    style Auth fill:#ffe6e6
```

## 2. 技术栈

### 2.1 核心技术

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 语言 | Python | 3.13+ | 主要开发语言 |
| HTTP 客户端 | requests | 2.31+ | API 调用 |
| 配置管理 | PyYAML | 6.0+ | 配置文件解析 |
| 加密存储 | cryptography | 41.0+ | 会话加密 |
| 系统密钥环 | keyring | 24.0+ | 安全存储密钥 |

### 2.2 架构原则

1. **文档即真理**：代码只是文档的可执行版本
2. **上下文优先**：充分理解业务上下文后再编码
3. **防御性编程**：假设第三方服务不稳定
4. **防腐层设计**：统一转换外部 API 数据
5. **插件化扩展**：便于添加新功能

## 3. 模块设计

### 3.1 禅道自动化助手架构

```mermaid
graph TB
    subgraph "Skill 入口"
        SkillPy[skill.py<br/>Skill 主入口]
    end

    subgraph "NLP 层"
        CommandParser[CommandParser<br/>命令解析器]
        IntentClassifier[IntentClassifier<br/>意图分类器]
        EntityExtractor[EntityExtractor<br/>实体提取器]
    end

    subgraph "认证层"
        SessionManager[SessionManager<br/>会话管理器]
    end

    subgraph "API 层"
        ZentaoApiClient[ZentaoApiClient<br/>禅道 API 客户端]
        Models[Models<br/>数据模型]
    end

    subgraph "业务层"
        StoryCollector[StoryCollector<br/>需求收集器]
        TaskCollector[TaskCollector<br/>任务收集器]
        TaskSplitter[TaskSplitter<br/>任务拆解器]
        TaskAssigner[TaskAssigner<br/>任务分配器]
    end

    subgraph "工具层"
        Logger[Logger<br/>结构化日志]
        Response[ApiResponse<br/>统一响应]
        ConfigLoader[ConfigLoader<br/>配置加载]
    end

    SkillPy --> CommandParser
    CommandParser --> IntentClassifier
    CommandParser --> EntityExtractor

    SkillPy --> SessionManager
    SkillPy --> ZentaoApiClient
    SkillPy --> StoryCollector
    SkillPy --> TaskCollector
    SkillPy --> TaskSplitter
    SkillPy --> TaskAssigner

    SessionManager --> Logger
    ZentaoApiClient --> Models
    ZentaoApiClient --> Logger
    StoryCollector --> Logger
    TaskCollector --> Logger
    TaskSplitter --> Logger
    TaskAssigner --> Logger

    ZentaoApiClient --> Response
    StoryCollector --> Response
    TaskCollector --> Response
    TaskSplitter --> Response
    TaskAssigner --> Response

    SkillPy --> ConfigLoader
    SessionManager --> ConfigLoader
    ZentaoApiClient --> ConfigLoader

    style SkillPy fill:#e1f5ff
    style CommandParser fill:#fff4e6
    style SessionManager fill:#ffe6e6
    style ZentaoApiClient fill:#e8f5e9
```

### 3.2 核心模块说明

#### 3.2.1 NLP 模块
- **IntentClassifier**：基于关键词匹配的意图分类，预留 LLM API 扩展接口
- **EntityExtractor**：提取任务ID、用户名、子任务名称等实体
- **CommandParser**：组合意图和实体，生成结构化命令

#### 3.2.2 认证模块
- **SessionManager**：使用系统 keyring 加密存储会话，支持会话过期检测

#### 3.2.3 API 层
- **ZentaoApiClient**：统一的 API 调用接口，包含重试机制
- **Models**：定义领域模型（User, Story, Task），实现防腐层

#### 3.2.4 业务层
- **Collectors**：信息收集基类和具体实现（需求、任务）
- **Automators**：自动化操作基类和具体实现（任务拆解、分配）

#### 3.2.5 工具层
- **Logger**：符合 Manifesto 要求的结构化 JSON 日志
- **ApiResponse**：统一的 API 响应结构
- **ConfigLoader**：配置文件加载和管理

## 4. 数据流

### 4.1 查询需求流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Skill as Skill
    participant Parser as CommandParser
    participant Auth as SessionManager
    participant API as ZentaoApiClient
    participant Zentao as 禅道服务器

    User->>Skill: "查看我的需求"
    Skill->>Parser: 解析命令
    Parser-->>Skill: intent=query_stories
    Skill->>Auth: 检查会话
    Auth-->>Skill: 会话有效
    Skill->>API: get_my_stories()
    API->>Zentao: GET /api.php/v1/stories
    Zentao-->>API: 需求列表
    API-->>Skill: 格式化数据
    Skill-->>User: 显示需求列表
```

### 4.2 任务拆解流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Skill as Skill
    participant Parser as CommandParser
    participant Splitter as TaskSplitter
    participant API as ZentaoApiClient
    participant Zentao as 禅道服务器

    User->>Skill: "拆解任务#123为A和B"
    Skill->>Parser: 解析命令
    Parser-->>Skill: intent=split_task, task_id=123, subtasks=[A,B]
    Skill->>Splitter: execute()
    Splitter->>API: get_task(123)
    API-->>Splitter: 任务详情
    loop 每个子任务
        Splitter->>API: create_task(parent=123, name=...)
        API->>Zentao: POST /api.php/v1/tasks
        Zentao-->>API: 创建成功
    end
    Splitter-->>Skill: 拆解结果
    Skill-->>User: 显示拆解结果
```

## 5. 安全设计

### 5.1 认证流程
1. 首次使用：交互式输入用户名和密码
2. 密码仅在内存中存在，不写入文件
3. 登录成功后，获取 Token 和 Cookies
4. 加密存储会话信息到系统 keyring
5. 后续使用自动加载会话

### 5.2 加密机制
- 使用 Fernet 对称加密
- 加密密钥存储在系统 keyring（Windows 凭据管理器）
- 会话文件包含过期时间，自动检测

### 5.3 API 安全
- 所有 API 调用使用 HTTPS（如服务器支持）
- Token 在请求头中传递
- 自动重试网络错误（502/503/504）

## 6. 扩展性设计

### 6.1 添加新意图
在 `IntentClassifier.INTENTS` 中添加新的意图和关键词。

### 6.2 添加新实体
在 `EntityExtractor` 中添加新的实体提取方法。

### 6.3 添加新自动化操作
1. 继承 `BaseAutomator`
2. 实现 `execute()` 方法
3. 在 `skill.py` 中注册

### 6.4 集成 LLM API
预留 LLM 接口，配置文件中设置：
```yaml
nlp:
  llm:
    enabled: true
    provider: "openai"
    api_key: "your-api-key"
    model: "gpt-4"
```

## 7. 部署架构

```
ZTools/
├── .trae/
│   └── skills/
│       └── zentao-helper/     # 禅道自动化 Skill
│           ├── skill.py        # Skill 入口
│           ├── SKILL.md        # Skill 文档
│           ├── requirements.txt # 依赖
│           ├── config/         # 配置
│           └── src/            # 源代码
└── docs/                       # 项目文档
```

## 8. 技术债务

- [ ] 完善单元测试覆盖率（目标 >80%）
- [ ] 添加集成测试
- [ ] 完善 API 错误处理和重试策略
- [ ] 优化 NLP 意图识别准确率
- [ ] 添加性能监控和日志分析

## 9. 架构决策记录 (ADR)

| ADR ID | 决策内容 | 日期 |
|--------|----------|------|
| ADR-001 | 选择 Python 作为主要开发语言 | 2026-02-28 |
| ADR-002 | 使用关键词匹配实现 NLP，预留 LLM 扩展 | 2026-02-28 |
| ADR-003 | 使用系统 keyring 存储加密密钥 | 2026-02-28 |