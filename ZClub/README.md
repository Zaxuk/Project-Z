# ZClub 积分系统

<p align="center">
  <img src="https://img.shields.io/badge/Spring%20Boot-2.7.15-green" alt="Spring Boot">
  <img src="https://img.shields.io/badge/Vue-3.3.0-brightgreen" alt="Vue">
  <img src="https://img.shields.io/badge/Java-8-orange" alt="Java">
  <img src="https://img.shields.io/badge/Node-16+-blue" alt="Node">
</p>

ZClub 是一个面向家庭的积分管理系统，旨在通过积分机制激励孩子完成学习任务、家务劳动等活动。孩子可以通过完成任务赚取积分（称为 Z 币），并使用积分兑换游戏时间、零花钱、零食等奖励。

## 功能特性

- **多角色支持**：管理员、普通家长、孩子三种角色
- **任务管理**：支持学习任务、家务任务、行为任务、临时任务
- **积分系统**：完成任务赚取积分，兑换奖励消耗积分
- **奖励商城**：自定义奖励和系统默认奖励
- **审批流程**：家长审批孩子完成的任务
- **实时通知**：任务状态变更和积分变动通知

## 技术栈

### 后端
- **框架**：Spring Boot 2.7.15
- **安全**：Spring Security + JWT
- **数据库**：H2（开发）/ MySQL（生产）
- **持久层**：Spring Data JPA
- **缓存**：Redis
- **构建工具**：Maven

### 前端
- **框架**：Vue 3.3
- **构建工具**：Vite 4.3
- **UI 组件库**：Element Plus 2.3
- **状态管理**：Vuex 4.1
- **HTTP 客户端**：Axios
- **样式**：Tailwind CSS 3.3

### 测试
- **E2E 测试**：Playwright

## 项目结构

```
ZClub/
├── docs/                       # 文档中心
│   ├── spec/                   # 需求规格说明书
│   ├── design/                 # 设计文档
│   ├── adr/                    # 架构决策记录
│   ├── api/                    # API 文档
│   ├── changelog.md            # 变更日志
│   └── current_status.md       # 系统现状快照
│
├── src/                        # 后端源代码
│   └── main/java/com/zclub/
│       ├── modules/            # 业务领域模块
│       │   ├── auth/           # 认证模块
│       │   ├── task/           # 任务模块
│       │   ├── reward/         # 奖励模块
│       │   ├── point/          # 积分模块
│       │   ├── notification/   # 通知模块
│       │   └── family/         # 家庭模块
│       ├── libs/               # 通用工具库
│       ├── jobs/               # 异步任务
│       ├── config/             # 全局配置
│       └── security/           # 安全配置
│
├── web/                        # 前端应用
│   ├── src/
│   │   ├── components/         # UI 组件
│   │   ├── store/              # Vuex 状态管理
│   │   └── utils/              # 工具函数
│   └── index.html
│
├── tests/                      # 测试
│   ├── e2e/                    # Playwright E2E 测试
│   ├── integration/            # 集成测试
│   └── mocks/                  # Mock 数据
│
├── scripts/                    # 运维脚本
└── AGENTS.md                   # 项目基本法
```

## 快速开始

### 环境要求

- Java 8+
- Maven 3.6+
- Node.js 16+
- npm 8+

### 后端启动

```bash
# 克隆项目
git clone <repository-url>
cd ZClub

# 编译并运行
mvn spring-boot:run
```

后端服务将在 http://localhost:8081 启动

### 前端启动

```bash
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 http://localhost:3000 启动

### 运行 E2E 测试

```bash
cd web

# 运行 Playwright 测试
npx playwright test

# 查看测试报告
npx playwright show-report
```

## API 文档

API 文档遵循 OpenAPI 规范，详见 [docs/api/openapi.yaml](docs/api/openapi.yaml)。

主要 API 端点：

| 端点 | 说明 |
|------|------|
| `POST /api/auth/register` | 用户注册 |
| `POST /api/auth/login` | 用户登录 |
| `GET /api/auth/verify` | 验证 Token |
| `GET /api/tasks` | 获取任务列表 |
| `POST /api/tasks` | 创建任务 |
| `GET /api/rewards` | 获取奖励列表 |
| `POST /api/rewards/{id}/redeem` | 兑换奖励 |
| `GET /api/points` | 获取积分余额 |
| `GET /api/points/history` | 获取积分历史 |
| `GET /api/notifications` | 获取通知列表 |

## 数据库配置

### 开发环境（H2）

开发环境默认使用 H2 内存数据库，无需额外配置。

### 生产环境（MySQL）

修改 `src/main/resources/application.yml`：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/zclub?useSSL=false&serverTimezone=UTC
    username: your_username
    password: your_password
    driver-class-name: com.mysql.cj.jdbc.Driver
  jpa:
    hibernate:
      ddl-auto: update
    database-platform: org.hibernate.dialect.MySQL8Dialect
```

## 项目规范

本项目遵循《项目基本法》（[AGENTS.md](AGENTS.md)）中定义的规范：

- **目录结构**：按业务领域模块拆分
- **代码规范**：遵循阿里巴巴 Java 开发手册
- **API 规范**：统一的响应格式
- **数据库规范**：snake_case 命名，UTC 时间存储
- **文档规范**：变更必须同步更新文档

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 变更日志

详见 [docs/changelog.md](docs/changelog.md)

## 许可证

[MIT](LICENSE)

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。
