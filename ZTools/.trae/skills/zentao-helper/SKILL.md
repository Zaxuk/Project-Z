---
name: "zentao-helper"
description: "禅道自动化助手，支持通过自然语言指令完成禅道日常操作。包括查询需求和任务、任务拆解和分配等功能。首次使用需要登录禅道。"
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
直接调用 Skill 并用自然语言描述您的需求：

```bash
# 查看需求
/iflow zentao-helper 查看我的需求
/iflow zentao-helper 显示需求列表

# 查看任务
/iflow zentao-helper 查看我的任务
/iflow zentao-helper 显示任务列表

# 任务拆解
/iflow zentao-helper 拆解任务#123
/iflow zentao-helper 拆解任务#123为前端开发和后端开发

# 任务分配
/iflow zentao-helper 把任务#456分配给张三
/iflow zentao-helper 指派任务#789给wangxiaoming

# 帮助
/iflow zentao-helper 帮助
/iflow zentao-helper 能做什么
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
    'create_bug': ['创建bug', 'new bug', '提bug'],
}
```

### 添加新的实体提取器
在 `src/nlp/entity_extractor.py` 中添加新的实体提取方法。

### 添加新的自动化操作
在 `src/automators/` 下创建新的类，继承 `BaseAutomator`，并在 `skill.py` 中注册。

### 集成 LLM API（预留扩展）
修改 `src/nlp/` 目录下的类，将关键词匹配替换为 LLM API 调用：

```python
# 未来可以这样扩展
class IntentClassifier:
    def classify(self, text):
        # 使用 LLM API 进行意图识别
        response = self.llm_client.chat([
            {"role": "system", "content": "你是意图分类器..."},
            {"role": "user", "content": text}
        ])
        return response.intent
```

## Error Handling

所有操作都返回统一的响应结构：
```json
{
  "success": boolean,
  "data": any | null,
  "error": {
    "code": "ERROR_CODE",
    "message": "用户可读的错误描述",
    "details": "调试用详细信息"
  },
  "timestamp": "ISO-8601 String"
}
```

常见错误码：
- `SESSION_EXPIRED`: 会话过期，需要重新登录
- `LOGIN_FAILED`: 登录失败，请检查用户名密码
- `TASK_NOT_FOUND`: 任务不存在或无权访问
- `USER_NOT_FOUND`: 用户不存在
- `API_ERROR`: 禅道 API 调用失败
- `UNKNOWN_INTENT`: 无法理解您的指令
- `MISSING_PARAMETER`: 缺少必要参数（如任务ID）

## Troubleshooting

### 登录失败
- 检查用户名密码是否正确
- 检查 `config/settings.yaml` 中的禅道服务器地址是否正确
- 确认网络连接正常

### 会话过期
- 重新调用 Skill，会自动提示重新登录
- 如果频繁过期，检查禅道服务器的会话超时设置

### 无法理解指令
- 尝试使用更明确的表达方式
- 查看帮助信息了解支持的指令格式
- 参考 Usage 部分的示例

## Requirements

- Python 3.10+
- requests
- pyyaml
- cryptography
- keyring

## License

内部使用，版权所有。