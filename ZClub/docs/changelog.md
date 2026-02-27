# 变更日志

## 2026-02-27

### 功能需求更新
- **奖励兑换流程**：移除审批环节，孩子可以直接兑换奖励
- **多家长协作**：普通家长只能创建临时任务，管理员可以创建所有类型的任务
- **任务管理**：任务创建后所有孩子都能看到，不需要分配
- **任务审批**：家长审批任务时需要打分，系统根据积分倍率计算最终积分

### 技术栈变更
- **后端**：从 Node.js + Express 改为 Java + Spring Boot
- **前端**：从 React 改为 Vue
- **数据库**：从 PostgreSQL 改为 MySQL
- **日志**：从 Winston 改为 Logback
- **UI 库**：从 Ant Design 改为 Element Plus

### 数据库设计更新
- **用户表**：添加 `phone` 字段，将 `is_active` 改为 `status`
- **任务表**：将 `is_recurring` 改为 `recurrence_status`
- **奖励表**：将 `is_default` 改为 `default_status`，后分离为 `default_rewards` 表
- **通知表**：将 `is_read` 改为 `read_status`
- **任务完成记录表**：移除拒绝相关字段，状态从 `pending_approval/approved/rejected` 改为 `pending_approval/completed`
- **奖励兑换表**：移除审批相关字段，状态从 `pending/approved/rejected` 改为 `completed`

### 架构设计更新
- **技术选型**：更新为 Java + Spring Boot + MySQL + Vue
- **奖励兑换流程**：移除审批环节，孩子直接兑换
- **任务完成流程**：添加打分和积分倍率计算步骤

### 文档更新
- 创建系统现状快照文档
- 创建变更日志文档
- 更新功能需求文档
- 更新非功能需求文档
- 更新架构设计文档
- 更新数据库设计文档
- 更新技术栈选择 ADR

### 功能更新
- **注册功能**：添加用户注册功能，默认注册为管理员角色
- **前端修复**：修复 tailwind.css 文件缺失问题

## 2026-02-26

### 功能需求更新
- **多家长支持**：添加管理员和普通家长角色
- **任务类型**：添加临时任务类型
- **任务审批等级**：添加 A/B/C/D 四个等级，对应不同积分倍率
- **奖励管理**：添加系统默认奖励

### 数据库设计更新
- 添加 `task_completions` 表
- 添加 `point_balances` 表
- 添加 `task_approval_levels` 表
- 添加 `system_settings` 表

### 架构设计更新
- 添加任务完成流程时序图
- 添加奖励兑换流程时序图

## 2026-02-25

### 初始创建
- 创建功能需求文档
- 创建非功能需求文档
- 创建架构设计文档
- 创建数据库设计文档
- 创建技术栈选择 ADR
- 创建 API 文档