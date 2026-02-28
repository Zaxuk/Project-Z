# 变更日志

## 2026-02-28

### 项目目录结构重构
按照《项目基本法》(Manifesto.md) 要求，将代码从按技术层拆分重构为按业务领域模块拆分：

#### 目录结构变更
```
Before:
src/main/java/com/zclub/
├── controller/     # 所有Controller
├── service/        # 所有Service
├── repository/     # 所有Repository
├── model/          # 所有Entity
└── util/           # 工具类

After:
src/main/java/com/zclub/
├── modules/        # 业务领域模块
│   ├── auth/       # 认证模块
│   │   ├── controller/
│   │   ├── service/
│   │   ├── repository/
│   │   ├── entity/
│   │   └── tests/
│   ├── task/       # 任务模块
│   ├── reward/     # 奖励模块
│   ├── point/      # 积分模块
│   ├── notification/ # 通知模块
│   └── family/     # 家庭模块
├── libs/           # 通用工具库
├── jobs/           # 异步任务
│   ├── workers/
│   └── triggers/
├── config/         # 全局配置
└── security/       # 安全配置
```

#### 文件移动和包声明更新
- 移动 31 个 Java 文件到对应的业务模块
- 更新所有文件的 package 声明
- 更新所有 import 语句
- 删除旧的 controller/service/repository/model/util 目录

#### 新增目录
- `src/main/java/com/zclub/modules/*` - 6个业务领域模块
- `src/main/java/com/zclub/libs/` - 通用工具库
- `src/main/java/com/zclub/jobs/` - 异步任务
- `tests/integration/` - 集成测试
- `tests/mocks/` - Mock数据
- `scripts/` - 运维脚本

#### 测试目录调整
- 将 `web/e2e/` 移动到 `tests/e2e/`（符合基本法规范）
- 更新 `web/playwright.config.js` 中的 `testDir` 配置
- 删除 `web/playwright-report/`（生成文件不应提交）
- 创建 `.gitignore` 文件，忽略 playwright-report/ 等生成文件

#### 脚本文件整理
- 将根目录下的测试脚本移动到 `scripts/` 目录：
  - `test-auth.js` → `scripts/test-auth.js`
  - `test_api.bat` → `scripts/test_api.bat`
  - `test_api.ps1` → `scripts/test_api.ps1`
  - `test_api2.ps1` → `scripts/test_api2.ps1`

#### 文档完善
- 创建 `README.md`，包含：
  - 项目介绍和功能特性
  - 技术栈说明
  - 项目结构图解
  - 快速开始指南（后端、前端启动步骤）
  - E2E 测试运行说明
  - API 文档索引
  - 数据库配置说明
  - 项目规范引用

## 2026-02-27

### 认证与授权功能实现
- **JWT认证**：实现基于JWT的认证机制，支持token生成和验证
- **SecurityContext集成**：创建UserPrincipal类存储用户认证信息（userId, email, role, familyId）
- **登录状态持久化**：使用cookie存储token，支持浏览器重启后保持登录状态
- **认证过滤器**：实现JwtAuthenticationFilter，自动验证请求中的token

### 数据库切换
- **开发环境**：从MySQL切换到H2内存数据库，方便开发和调试
- **配置文件**：更新application.yml，添加H2数据库配置

### API修复与优化
- **注册功能**：修复注册时自动创建Family记录的逻辑
- **创建任务API**：移除前端传递familyId，改为从SecurityContext自动获取
- **错误处理**：当用户不存在时返回401错误，提示重新登录
- **CORS配置**：修复跨域问题，支持前端开发服务器访问

### 前端功能实现
- **Vuex状态管理**：实现用户状态管理，支持登录/注册/登出
- **Cookie工具**：创建cookie.js工具类，支持token的存储和读取
- **Axios拦截器**：自动添加Authorization请求头
- **登录对话框**：实现登录/注册对话框组件
- **任务组件**：实现任务列表和创建任务功能

### 文档更新
- 更新系统现状快照
- 更新变更日志

---

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