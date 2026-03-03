---
name: "zentao-helper"
description: "禅道自动化助手，支持通过自然语言指令完成禅道日常操作，包括查询需求和任务、任务拆解和分配等功能。当用户需要与禅道项目管理工具交互时调用，如查询任务、分配任务、拆解任务等场景。首次使用需要登录禅道。"
---

# ZenTao Helper Skill

## Description
禅道自动化助手，支持通过自然语言指令完成禅道日常操作。提供安全的交互式认证，自动管理会话，无需存储密码。

## Capabilities

### 信息收集
- 查询指派给我的需求列表
- 查询指派给我的任务列表
- 支持按状态、优先级过滤

### 自动化操作
- 任务拆解：将一个任务拆解为多个子任务
- 任务分配：将任务分配给指定用户

### 自然语言支持
- 支持中英文混合指令
- 智能解析任务ID、用户名等实体
- 支持从自然语言中提取子任务名称

## Usage

### 基础用法
直接使用自然语言描述您的需求：

```bash
# 查看需求
查看我的需求
显示需求列表

# 查看任务
查看我的任务
显示任务列表

# 任务拆解
拆解任务#123
拆解任务#123为前端开发和后端开发

# 任务分配
把任务#456分配给张三
指派任务#789给wangxiaoming

# 帮助
帮助
能做什么
```

### 认证流程
首次使用时会自动触发交互式登录：
```
需要登录禅道...
用户名: [输入您的用户名]
密码: [输入您的密码，不会显示]
```

登录成功后，会话信息将加密存储在本地，后续使用无需重复登录。

## Configuration

### 配置文件位置
`.trae/skills/zentao-helper/config/settings.yaml`

### 配置项说明
```yaml
zentao:
  base_url: "http://zentao.diansan.com/"  # 禅道服务器地址
  timeout: 30                              # 请求超时时间（秒）
  retry_times: 3                           # 重试次数
  retry_backoff: 1                         # 重试退避因子（秒）

logging:
  level: "INFO"                            # 日志级别
  format: "json"                           # 日志格式
```

## Security

- 密码仅在内存中存在，不写入任何文件
- 会话信息使用系统 keyring 加密存储（Windows 凭据管理器）
- 支持会话过期自动检测和重新登录
- 所有 API 调用使用 HTTPS（如禅道服务器支持）

## Extension Points

### 添加新的意图
在 `src/nlp/intent_classifier.py` 的 `INTENTS` 字典中添加新的意图和关键词：

```python
INTENTS = {
    'query_stories': ['需求', 'story', '需求列表', '我的需求', '显示需求'],
    'query_tasks': ['任务', 'task', '任务列表', '我的任务', '显示任务', '查看任务'],
    'split_task': ['拆解', '分解', 'split', '拆分', '拆成'],
    'assign_task': ['分配', '指派', 'assign', '给'],
    # 添加新意图
    'your_new_intent': ['关键词1', '关键词2'],
}
```

### 添加新的处理器
1. 在 `src/automators/` 目录下创建新的处理器类
2. 继承 `BaseAutomator` 基类
3. 在 `skill.py` 中初始化并调用

## Architecture

```
skill.py              # Skill 主入口，实现 execute() 方法
├── src/
│   ├── nlp/          # 自然语言处理
│   │   ├── command_parser.py      # 命令解析器
│   │   ├── intent_classifier.py   # 意图分类器
│   │   └── entity_extractor.py    # 实体提取器
│   ├── auth/         # 认证模块
│   │   └── session_manager.py     # 会话管理器
│   ├── zentao/       # 禅道 API
│   │   ├── api_client.py          # API 客户端
│   │   └── models.py              # 数据模型
│   ├── collectors/   # 信息收集器
│   │   ├── story_collector.py     # 需求收集器
│   │   └── task_collector.py      # 任务收集器
│   ├── automators/   # 自动化操作器
│   │   ├── task_splitter.py       # 任务拆解器
│   │   └── task_assigner.py       # 任务分配器
│   └── utils/        # 工具模块
│       ├── logger.py              # 结构化日志
│       ├── response.py            # 统一响应
│       └── config_loader.py       # 配置加载
└── config/
    └── settings.yaml              # 配置文件
```

## Troubleshooting

### 登录失败
- 检查用户名和密码是否正确
- 检查网络连接是否正常
- 检查 `config/settings.yaml` 中的 `base_url` 配置是否正确

### 会话过期
- 系统会自动检测会话过期并提示重新登录
- 也可以手动删除 `.session.enc` 文件强制重新登录

### API 调用失败
- 检查禅道服务器是否可访问
- 查看日志文件获取详细错误信息
- 检查网络代理设置
