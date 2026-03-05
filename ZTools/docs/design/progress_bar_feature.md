# 进度条功能设计文档

**文档版本**: v1.0  
**创建日期**: 2026-03-04  
**关联需求**: 查询等耗时功能进度条显示

---

## 1. 需求背景

当前查询功能（如查询需求列表、任务列表）在执行时，用户无法感知进度，容易产生等待焦虑。本功能旨在为耗时操作提供可视化进度反馈。

## 2. 设计目标

- 为耗时操作（>1秒）提供进度条显示
- 保持代码简洁，不影响现有功能
- 支持多种进度显示模式（百分比、进度条、动画）
- 优雅处理异常情况

## 3. 功能范围

### 3.1 适用场景

| 功能模块 | 操作 | 预估耗时 | 是否需要进度条 |
|---------|------|---------|--------------|
| StoryCollector | collect() | 2-10秒 | ✅ 是 |
| TaskCollector | collect() | 2-10秒 | ✅ 是 |
| TaskSplitter | execute() | 5-15秒 | ✅ 是 |
| API Client | 单次请求 | <1秒 | ❌ 否 |

### 3.2 不适用场景

- 单次 API 调用（耗时 < 1秒）
- 交互式输入过程
- 简单的数据转换操作

## 4. 技术方案

### 4.1 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    ProgressBarManager                    │
│  (进度条管理器 - 单例模式)                                │
├─────────────────────────────────────────────────────────┤
│  + start(task_name: str, total: int = None)             │
│  + update(current: int, message: str = None)            │
│  + increment(step: int = 1, message: str = None)        │
│  + finish(message: str = None)                          │
│  + error(message: str)                                  │
└─────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
   ┌────────────────┐ ┌──────────┐ ┌────────────────┐
   │ ConsoleProgress │ │ TqdmProgress │ │ SimpleProgress │
   │ (控制台进度条)   │ │ (tqdm库)   │ │ (简单动画)     │
   └────────────────┘ └──────────┘ └────────────────┘
```

### 4.2 实现方式选择

方案A：使用 `tqdm` 库（推荐）
- 优点：功能完善，支持多种样式，社区活跃
- 缺点：需要额外依赖
- 适用：复杂进度显示需求

方案B：自实现简单进度条
- 优点：无额外依赖，代码可控
- 缺点：功能较简单
- 适用：简单进度显示需求

**建议采用方案B（自实现）**，理由：
1. 项目依赖应尽量精简
2. 进度条功能需求相对简单
3. 便于定制化显示样式

### 4.3 核心类设计

```python
# src/utils/progress_bar.py

class ProgressBar:
    """简单进度条实现"""
    
    def __init__(self, total: int = None, desc: str = "", unit: str = "项"):
        self.total = total
        self.desc = desc
        self.unit = unit
        self.current = 0
        self.start_time = None
        
    def start(self):
        """开始进度"""
        pass
        
    def update(self, n: int = 1):
        """更新进度"""
        pass
        
    def set_postfix(self, **kwargs):
        """设置后缀信息"""
        pass
        
    def close(self):
        """关闭进度条"""
        pass


class Spinner:
    """加载动画（用于不确定进度的场景）"""
    
    def __init__(self, desc: str = "加载中"):
        self.desc = desc
        self.running = False
        
    def start(self):
        """开始动画"""
        pass
        
    def stop(self):
        """停止动画"""
        pass
```

### 4.4 使用示例

```python
# 确定进度的场景（如分页查询）
from src.utils.progress_bar import ProgressBar

def collect_stories():
    stories = []
    total_pages = 10
    
    with ProgressBar(total=total_pages, desc="查询需求") as pbar:
        for page in range(1, total_pages + 1):
            result = api.get_stories(page=page)
            stories.extend(result)
            pbar.update(1)
            pbar.set_postfix(已获取=len(stories))
    
    return stories


# 不确定进度的场景（如批量处理）
from src.utils.progress_bar import Spinner

def process_tasks():
    spinner = Spinner(desc="正在处理任务")
    spinner.start()
    
    try:
        for task in tasks:
            process(task)
        spinner.stop(message="处理完成")
    except Exception as e:
        spinner.stop(message=f"处理失败: {e}")
        raise
```

## 5. 集成点

### 5.1 StoryCollector 集成

```python
# src/collectors/story_collector.py

def collect(self, status: str = None) -> ApiResponse:
    # 显示加载动画（不确定进度）
    spinner = Spinner("正在查询需求列表")
    spinner.start()
    
    try:
        # 第一步：获取总数量
        total = self._get_total_count()
        spinner.stop()
        
        # 第二步：分页获取（显示确定进度）
        with ProgressBar(total=total, desc="获取需求") as pbar:
            stories = self._fetch_all_pages(pbar)
        
        return ApiResponse.success_response({'stories': stories})
        
    except Exception as e:
        spinner.stop(message=f"查询失败: {e}")
        raise
```

### 5.2 TaskCollector 集成

与 StoryCollector 类似，在 `collect()` 方法中添加进度条。

### 5.3 TaskSplitter 集成

```python
# src/automators/task_splitter.py

def execute(self, story_id: str, **kwargs):
    steps = [
        ("获取需求信息", self._get_story),
        ("更新需求标题", self._update_title),
        ("评审需求", self._review_story),
        ("选择项目", self._select_project),
        ("创建任务", self._create_task),
    ]
    
    with ProgressBar(total=len(steps), desc="拆解需求") as pbar:
        for step_name, step_func in steps:
            pbar.set_postfix(当前步骤=step_name)
            step_func()
            pbar.update(1)
```

## 6. 界面样式

### 6.1 进度条样式

```
# 基础样式
查询需求:  50%|████████████████████                    | 5/10 [00:05<00:05, 1.0项/s]

# 带后缀信息
获取需求:  50%|████████████████████                    | 5/10 [00:05<00:05, 1.0项/s, 已获取=50]
```

### 6.2 加载动画样式

```
# 旋转动画
正在查询需求列表... /
正在查询需求列表... -
正在查询需求列表... \
正在查询需求列表... |

# 完成提示
✓ 查询完成，共获取 100 条需求
```

## 7. 异常处理

- 进度条在异常时应自动关闭
- 保留错误信息，不遮挡异常提示
- 支持手动取消操作（Ctrl+C）

## 8. 配置选项

```yaml
# config/settings.yaml

ui:
  progress_bar:
    enabled: true           # 是否启用进度条
    style: "simple"         # 样式: simple/bar/spinner
    show_speed: true        # 是否显示速度
    show_eta: true          # 是否显示预计剩余时间
    refresh_rate: 0.1       # 刷新频率（秒）
```

## 9. 测试计划

1. 单元测试：测试 ProgressBar 和 Spinner 的基本功能
2. 集成测试：在 StoryCollector 和 TaskCollector 中测试
3. 异常测试：验证异常时进度条正确关闭
4. 性能测试：确保进度条不影响整体性能

## 10. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|-----|------|------|---------|
| 进度条显示影响性能 | 低 | 中 | 控制刷新频率，使用简单实现 |
| 终端不支持特殊字符 | 中 | 低 | 提供纯文本回退方案 |
| 并发操作显示混乱 | 低 | 中 | 使用上下文管理器确保单实例 |

---

**待确认事项：**

1. 是否同意采用方案B（自实现进度条）？
2. 进度条样式是否有特殊要求？
3. 是否需要支持禁用进度条的配置选项？
4. 是否有其他需要添加进度条的功能点？

请确认后，我将开始实现。
