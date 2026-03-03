# ZTools - 日常办公自动化工具集

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

ZTools 是一个基于 Trae Skill 架构的日常办公自动化工具集，旨在通过自然语言指令简化日常工作流程。

## 功能特性

### 禅道自动化助手 (zentao-helper)

通过自然语言与禅道项目管理工具交互，支持：

- **信息收集**
  - 查询指派给我的需求列表（支持过滤和关键字搜索）
  - 查询指派给我的任务列表（支持状态过滤）
  - 智能显示需求/任务状态和优先级

- **自动化操作**
  - 任务拆解：交互式输入需求等级、优先级、上线时间等信息
  - 任务分配：将任务分配给指定用户
  - 自动更新需求标题格式

- **自然语言支持**
  - 支持中英文混合指令
  - 智能解析任务ID、用户名等实体
  - 支持从自然语言中提取子任务名称

## 快速开始

### 环境要求

- Python 3.13+
- Windows 10/11
- Trae IDE

### 安装

1. 克隆仓库
```bash
git clone https://github.com/Zaxuk/Project-Z.git
cd "Project Z/ZTools"
```

2. 安装依赖
```bash
cd .trae/skills/zentao-helper
pip install -r requirements.txt
```

3. 配置禅道服务器
编辑 `.trae/skills/zentao-helper/config/settings.yaml`：
```yaml
zentao:
  base_url: "http://zentao.diansan.com/"
  timeout: 30
  retry_times: 3
```

### 使用

在 Trae IDE 中直接使用自然语言指令：

```
# 查看需求
查看我的需求
显示需求列表

# 查看任务
查看我的任务
显示任务列表

# 任务拆解
拆解任务#123为前端开发和后端开发

# 任务分配
把任务#456分配给张三
```

首次使用时会提示登录禅道，会话信息将加密存储在本地。

## 项目结构

```
ZTools/
├── .trae/
│   └── skills/
│       └── zentao-helper/         # 禅道自动化 Skill
│           ├── skill.py            # Skill 主入口
│           ├── SKILL.md            # Skill 文档
│           ├── requirements.txt    # Python 依赖
│           ├── config/
│           │   └── settings.yaml   # 配置文件
│           └── src/                # 源代码
│               ├── auth/           # 认证模块
│               ├── zentao/         # 禅道 API
│               ├── nlp/            # 自然语言处理
│               ├── collectors/     # 信息收集器
│               ├── automators/     # 自动化操作器
│               └── utils/          # 工具模块
├── docs/                           # 项目文档
│   ├── spec/                       # 需求规格
│   ├── design/                     # 设计文档
│   ├── changelog.md                # 变更日志
│   └── current_status.md           # 系统现状
├── scripts/                        # 运维脚本
├── .cursorrules                    # AI 编码规范
├── AGENTS.md                       # 项目基本法
└── README.md                       # 本文件
```

## 架构设计

ZTools 采用 **Skill-based Architecture**（基于技能的架构）：

- **Skill 层**：每个 Skill 是一个独立的自动化工具，通过 Trae IDE 调用
- **NLP 层**：意图分类、实体提取、命令解析
- **认证层**：安全的交互式登录，会话加密存储
- **API 层**：统一的 API 客户端，包含重试机制
- **业务层**：信息收集器和自动化操作器

详细架构说明请查看 [docs/design/architecture.md](docs/design/architecture.md)

## 配置说明

### 禅道配置

编辑 `.trae/skills/zentao-helper/config/settings.yaml`：

```yaml
zentao:
  base_url: "http://zentao.diansan.com/"  # 禅道服务器地址
  timeout: 30                              # 请求超时时间
  retry_times: 3                           # 重试次数
  
  story_query:
    products: ["都江堰系统"]                # 查询的产品列表
    keywords: ["特2"]                       # 标题关键字过滤
  
  task_creation:
    default_assigned_to: ""                 # 默认任务执行人
    grade_hours:                            # 需求等级对应的任务时长
      "A-": 1
      "A": 2
      "A+": 4
      "A++": 8
      "B": null
```

## 开发指南

### 添加新的 Skill

1. 在 `.trae/skills/` 目录下创建新的 Skill 目录
2. 按照 Trae Skill 规范创建 `skill.py` 和 `SKILL.md`
3. 在 `skill.py` 中实现 `execute()` 方法

### 扩展现有 Skill

1. 在 `src/nlp/intent_classifier.py` 添加新意图
2. 在 `src/automators/` 创建新处理器
3. 在 `skill.py` 中添加处理逻辑

详细开发指南请查看 [AGENTS.md](AGENTS.md)

## 文档

- [项目基本法](AGENTS.md) - 开发规范和原则
- [功能需求](docs/spec/functional.md) - 功能规格说明
- [技术架构](docs/design/architecture.md) - 架构设计文档
- [变更日志](docs/changelog.md) - 版本更新记录
- [系统现状](docs/current_status.md) - 当前开发状态

## 安全说明

- 密码仅在内存中存在，不写入任何文件
- 会话信息使用系统 keyring 加密存储（Windows 凭据管理器）
- 支持会话过期自动检测和重新登录

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。
