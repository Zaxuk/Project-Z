# ZClub 积分系统数据库设计

## 1. 数据库表结构

### 1.1 用户表 (users)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 用户ID |
| `name` | `VARCHAR(255)` | `NOT NULL` | 用户名 |
| `email` | `VARCHAR(255)` | `UNIQUE` | 邮箱（仅家长用户） |
| `phone` | `VARCHAR(20)` | `UNIQUE` | 手机号码（预留，支持短信验证码登录） |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | 密码哈希 |
| `role` | `VARCHAR(50)` | `NOT NULL` | 角色（admin/parent/child） |
| `parent_id` | `UUID` | `REFERENCES users(id)` | 家长ID（仅孩子用户） |
| `family_id` | `UUID` | `REFERENCES families(id)` | 家庭ID |
| `age` | `INTEGER` | | 年龄（仅孩子用户） |
| `status` | `VARCHAR(50)` | `DEFAULT 'active'` | 状态（active/inactive） |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新时间 |

### 1.2 家庭表 (families)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 家庭ID |
| `name` | `VARCHAR(255)` | `NOT NULL` | 家庭名称 |
| `created_by` | `UUID` | `REFERENCES users(id)` | 创建者ID |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新时间 |

### 1.3 任务表 (tasks)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 任务ID |
| `name` | `VARCHAR(255)` | `NOT NULL` | 任务名称 |
| `description` | `TEXT` | | 任务描述 |
| `points` | `INTEGER` | `NOT NULL` | 积分奖励 |
| `status` | `VARCHAR(50)` | `NOT NULL` | 状态（pending_approval/approved/completed） |
| `type` | `VARCHAR(50)` | `NOT NULL` | 任务类型（study/chore/behavior/temporary） |
| `creator_id` | `UUID` | `NOT NULL` | 创建者ID |
| `family_id` | `UUID` | `NOT NULL` | 家庭ID |
| `due_date` | `TIMESTAMP` | | 截止时间 |
| `recurrence` | `VARCHAR(255)` | | 重复规则（如 daily/weekly/monthly，仅非临时任务） |
| `recurrence_status` | `VARCHAR(50)` | `DEFAULT 'non_recurring'` | 重复状态（non_recurring/recurring） |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新时间 |

### 1.4 任务完成记录表 (task_completions)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 完成记录ID |
| `task_id` | `UUID` | `NOT NULL` | 任务ID |
| `user_id` | `UUID` | `NOT NULL` | 完成任务的用户ID（孩子） |
| `status` | `VARCHAR(50)` | `NOT NULL` | 状态（pending_approval/completed） |
| `approval_level_id` | `UUID` | | 审批等级ID |
| `points_earned` | `INTEGER` | `NOT NULL` | 实际获得的积分 |
| `completed_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 完成时间 |
| `approved_at` | `TIMESTAMP` | | 审批时间 |
| `approved_by` | `UUID` | `REFERENCES users(id)` | 审批者ID |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新时间 |

### 1.5 积分余额表 (point_balances)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 余额ID |
| `user_id` | `UUID` | `UNIQUE` | 用户ID |
| `balance` | `INTEGER` | `NOT NULL DEFAULT 0` | 当前积分余额 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新时间 |

### 1.6 积分记录表 (point_records)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 记录ID |
| `user_id` | `UUID` | `NOT NULL` | 用户ID |
| `type` | `VARCHAR(50)` | `NOT NULL` | 类型（earned/spent） |
| `amount` | `INTEGER` | `NOT NULL` | 积分数量 |
| `related_id` | `UUID` | | 相关对象ID（任务完成记录或奖励兑换记录） |
| `related_type` | `VARCHAR(50)` | | 相关类型（task_completion/reward_redemption） |
| `description` | `TEXT` | | 描述 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |

### 1.7 奖励表 (rewards)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 奖励ID |
| `name` | `VARCHAR(255)` | `NOT NULL` | 奖励名称 |
| `description` | `TEXT` | | 奖励描述 |
| `points_required` | `INTEGER` | `NOT NULL` | 所需积分 |
| `stock` | `INTEGER` | `DEFAULT NULL` | 库存数量（NULL表示无限制） |
| `status` | `VARCHAR(50)` | `DEFAULT 'active'` | 状态（active/inactive） |
| `family_id` | `UUID` | `NOT NULL` | 家庭ID |
| `created_by` | `UUID` | `REFERENCES users(id)` | 创建者ID |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新时间 |

### 1.8 系统默认奖励表 (default_rewards)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 奖励ID |
| `name` | `VARCHAR(255)` | `NOT NULL` | 奖励名称 |
| `description` | `TEXT` | | 奖励描述 |
| `points_required` | `INTEGER` | `NOT NULL` | 所需积分 |
| `status` | `VARCHAR(50)` | `DEFAULT 'active'` | 状态（active/inactive） |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新时间 |

### 1.9 奖励兑换表 (reward_redemptions)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 兑换ID |
| `user_id` | `UUID` | `NOT NULL` | 用户ID |
| `reward_id` | `UUID` | `NOT NULL` | 奖励ID |
| `status` | `VARCHAR(50)` | `NOT NULL` | 状态（completed） |
| `redeemed_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 兑换时间 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新时间 |

### 1.10 通知表 (notifications)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 通知ID |
| `user_id` | `UUID` | `NOT NULL` | 接收用户ID |
| `type` | `VARCHAR(50)` | `NOT NULL` | 通知类型（task_completed/point_earned/reward_redeemed等） |
| `title` | `VARCHAR(255)` | `NOT NULL` | 通知标题 |
| `message` | `TEXT` | `NOT NULL` | 通知内容 |
| `read_status` | `VARCHAR(50)` | `DEFAULT 'unread'` | 阅读状态（unread/read） |
| `related_id` | `UUID` | | 相关对象ID |
| `related_type` | `VARCHAR(50)` | | 相关类型 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |

### 1.11 任务审批等级表 (task_approval_levels)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 等级ID |
| `name` | `VARCHAR(50)` | `NOT NULL` | 等级名称（如 A、B、C、D） |
| `multiplier` | `DECIMAL(3,2)` | `NOT NULL` | 积分倍率（如 1.2、1.0、0.8、0.6） |
| `order` | `INTEGER` | `NOT NULL` | 等级顺序 |
| `status` | `VARCHAR(50)` | `DEFAULT 'active'` | 状态（active/inactive） |
| `family_id` | `UUID` | `NOT NULL` | 家庭ID |
| `created_by` | `UUID` | `REFERENCES users(id)` | 创建者ID |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新时间 |

### 1.12 系统设置表 (system_settings)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 设置ID |
| `key` | `VARCHAR(255)` | `UNIQUE` | 设置键 |
| `value` | `TEXT` | `NOT NULL` | 设置值 |
| `description` | `TEXT` | | 设置描述 |
| `family_id` | `UUID` | `NOT NULL` | 家庭ID |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新时间 |

## 2. 索引设计

### 2.1 用户表索引
- `idx_users_parent_id`：`parent_id` 字段索引，加速查询孩子用户
- `idx_users_email`：`email` 字段唯一索引，加速登录验证
- `idx_users_phone`：`phone` 字段唯一索引，加速登录验证
- `idx_users_family_id`：`family_id` 字段索引，加速查询家庭成员
- `idx_users_role`：`role` 字段索引，加速查询特定角色用户
- `idx_users_status`：`status` 字段索引，加速查询特定状态用户

### 2.2 家庭表索引
- `idx_families_created_by`：`created_by` 字段索引，加速查询创建的家庭
- `idx_families_name`：`name` 字段索引，加速查询家庭名称

### 2.3 任务表索引
- `idx_tasks_creator_id`：`creator_id` 字段索引，加速查询创建的任务
- `idx_tasks_family_id`：`family_id` 字段索引，加速查询家庭任务
- `idx_tasks_status`：`status` 字段索引，加速查询任务状态
- `idx_tasks_type`：`type` 字段索引，加速查询任务类型
- `idx_tasks_due_date`：`due_date` 字段索引，加速查询到期任务
- `idx_tasks_recurrence_status`：`recurrence_status` 字段索引，加速查询重复任务

### 2.4 任务完成记录表索引
- `idx_task_completions_task_id`：`task_id` 字段索引，加速查询任务完成记录
- `idx_task_completions_user_id`：`user_id` 字段索引，加速查询用户完成记录
- `idx_task_completions_status`：`status` 字段索引，加速查询完成状态

### 2.5 积分余额表索引
- `idx_point_balances_user_id`：`user_id` 字段唯一索引，加速查询用户积分余额

### 2.6 积分记录表索引
- `idx_point_records_user_id`：`user_id` 字段索引，加速查询用户积分记录
- `idx_point_records_created_at`：`created_at` 字段索引，加速查询时间范围内的积分记录
- `idx_point_records_type`：`type` 字段索引，加速查询积分记录类型

### 2.7 奖励表索引
- `idx_rewards_family_id`：`family_id` 字段索引，加速查询家庭奖励
- `idx_rewards_created_by`：`created_by` 字段索引，加速查询创建的奖励
- `idx_rewards_status`：`status` 字段索引，加速查询活跃奖励

### 2.8 系统默认奖励表索引
- `idx_default_rewards_status`：`status` 字段索引，加速查询活跃默认奖励

### 2.9 奖励兑换表索引
- `idx_reward_redemptions_user_id`：`user_id` 字段索引，加速查询用户兑换记录
- `idx_reward_redemptions_reward_id`：`reward_id` 字段索引，加速查询奖励兑换记录
- `idx_reward_redemptions_status`：`status` 字段索引，加速查询兑换状态

### 2.10 通知表索引
- `idx_notifications_user_id`：`user_id` 字段索引，加速查询用户通知
- `idx_notifications_read_status`：`read_status` 字段索引，加速查询未读通知
- `idx_notifications_type`：`type` 字段索引，加速查询通知类型

### 2.11 任务审批等级表索引
- `idx_task_approval_levels_family_id`：`family_id` 字段索引，加速查询家庭审批等级
- `idx_task_approval_levels_order`：`order` 字段索引，加速查询等级顺序
- `idx_task_approval_levels_status`：`status` 字段索引，加速查询活跃审批等级

### 2.12 系统设置表索引
- `idx_system_settings_family_id`：`family_id` 字段索引，加速查询家庭设置
- `idx_system_settings_key`：`key` 字段索引，加速查询设置键

## 3. 数据关系

### 3.1 一对一关系
- 用户与积分余额：`point_balances.user_id` → `users.id`（一个用户对应一个积分余额）

### 3.2 一对多关系
- 家庭可以有多个用户（家长和孩子）：`users.family_id` → `families.id`
- 家长用户（parent）可以有多个孩子用户（child）：`users.parent_id` → `users.id`
- 家长用户可以创建多个任务：`tasks.creator_id` → `users.id`
- 家庭可以有多个任务：`tasks.family_id` → `families.id`
- 任务可以有多个完成记录：`task_completions.task_id` → `tasks.id`
- 孩子用户可以完成多个任务：`task_completions.user_id` → `users.id`
- 用户可以有多个积分记录：`point_records.user_id` → `users.id`
- 家庭可以有多个奖励：`rewards.family_id` → `families.id`
- 家长用户可以创建多个奖励：`rewards.created_by` → `users.id`
- 系统默认奖励：全局可用，不需要与特定家庭关联
- 孩子用户可以提交多个奖励兑换申请：`reward_redemptions.user_id` → `users.id`
- 奖励可以被多个用户兑换：`reward_redemptions.reward_id` → `rewards.id`
- 用户可以接收多个通知：`notifications.user_id` → `users.id`
- 家庭可以有多个审批等级：`task_approval_levels.family_id` → `families.id`
- 家庭可以有多个系统设置：`system_settings.family_id` → `families.id`
- 用户可以创建多个家庭：`families.created_by` → `users.id`

### 3.3 多对多关系
- 无

## 4. 数据完整性

### 4.1 约束
- **主键约束**：所有表的 `id` 字段为主键
- **外键约束**：确保引用关系的完整性
- **非空约束**：关键字段设置为非空
- **唯一约束**：邮箱、积分余额用户ID等字段设置为唯一
- **检查约束**：积分数量必须为正数，年龄必须为合理范围，积分倍率必须为正数等

### 4.2 触发器
- `update_timestamp`：自动更新 `updated_at` 字段
- `check_point_balance`：确保积分余额不为负数
- `update_task_status`：自动更新过期任务状态
- `update_reward_stock`：自动更新奖励库存

### 4.3 默认数据
- **默认任务审批等级**：A（1.2）、B（1.0）、C（0.8）、D（0.6）
- **默认奖励**：游戏时间、零花钱、零食等
- **默认系统设置**：临时任务积分奖励最大值（如 100）

## 5. 数据备份与恢复

### 5.1 备份策略
- 每日全量备份
- 每小时增量备份
- 备份存储在安全位置

### 5.2 恢复策略
- 定期测试备份恢复
- 制定灾难恢复计划
- 确保数据可快速恢复

## 6. 数据迁移

### 6.1 迁移工具
- 使用数据库迁移工具（如 Flyway、Liquibase 或 ORM 自带迁移工具）
- 版本控制迁移脚本

### 6.2 迁移流程
- 开发环境测试迁移
- 预生产环境验证
- 生产环境执行
- 回滚方案准备

## 7. 性能优化

### 7.1 查询优化
- 合理使用索引
- 避免全表扫描
- 优化复杂查询

### 7.2 存储优化
- 定期清理过期数据
- 归档历史数据
- 优化数据存储结构

### 7.3 缓存策略
- 缓存热点数据
- 使用 Redis 缓存积分余额等频繁访问数据
- 缓存任务和奖励列表
- 缓存任务审批等级和系统设置

## 8. 安全性

### 8.1 数据加密
- 密码使用加盐哈希存储
- 敏感数据加密存储
- 传输加密（HTTPS）

### 8.2 访问控制
- 基于角色的权限控制
- 最小权限原则
- 防止 SQL 注入和 XSS 攻击

### 8.3 审计日志
- 记录关键操作
- 监控异常行为
- 定期审计数据访问

## 9. 数据字典

### 9.1 任务状态 (tasks.status)
- `pending_approval`：待审批
- `approved`：已批准
- `completed`：已完成

### 9.2 任务类型 (tasks.type)
- `study`：学习任务
- `chore`：家务任务
- `behavior`：行为任务
- `temporary`：临时任务

### 9.3 任务完成状态 (task_completions.status)
- `pending_approval`：待审批
- `completed`：已完成

### 9.4 积分记录类型 (point_records.type)
- `earned`：赚取
- `spent`：消耗

### 9.5 奖励兑换状态 (reward_redemptions.status)
- `completed`：已完成

### 9.6 用户角色 (users.role)
- `admin`：管理员
- `parent`：普通家长
- `child`：孩子

### 9.7 用户状态 (users.status)
- `active`：活跃
- `inactive`：非活跃

### 9.8 奖励状态 (rewards.status)
- `active`：活跃
- `inactive`：非活跃

### 9.9 任务审批等级状态 (task_approval_levels.status)
- `active`：活跃
- `inactive`：非活跃

### 9.10 任务重复状态 (tasks.recurrence_status)
- `non_recurring`：非重复
- `recurring`：重复

### 9.11 通知阅读状态 (notifications.read_status)
- `unread`：未读
- `read`：已读

### 9.12 系统设置键 (system_settings.key)
- `temporary_task_max_points`：临时任务积分奖励最大值