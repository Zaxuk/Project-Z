---
name: "playwright-e2e"
description: "使用 Playwright 进行前端端到端(E2E)测试。当用户需要测试 Vue/React 前端页面交互、表单提交、用户流程时调用此技能。"
---

# Playwright E2E 测试技能

## 概述

此技能用于为 Vue 3 + Vite 项目创建和运行端到端(E2E)测试，使用 Playwright 测试框架。

## 适用场景

- 测试页面路由导航
- 测试表单输入和提交
- 测试组件交互（点击、悬停等）
- 测试用户完整流程（登录 -> 操作 -> 退出）
- 测试 API 集成和数据展示
- 截图对比测试

## 前置要求

确保项目已安装 Playwright：

```bash
cd web
npm init playwright@latest
```

## 测试文件结构

```
web/
├── e2e/
│   ├── auth.spec.js          # 登录相关测试
│   ├── tasks.spec.js         # 任务模块测试
│   ├── rewards.spec.js       # 奖励模块测试
│   └── points.spec.js        # 积分模块测试
├── playwright.config.js      # Playwright 配置
└── package.json
```

## 常用测试模式

### 1. 基础页面访问测试

```javascript
const { test, expect } = require('@playwright/test');

test('首页可以正常访问', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page).toHaveTitle(/ZClub/);
});
```

### 2. 表单交互测试

```javascript
test('用户可以登录', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  
  // 填写表单
  await page.fill('[data-testid="username"]', 'testuser');
  await page.fill('[data-testid="password"]', 'password123');
  
  // 点击登录按钮
  await page.click('[data-testid="login-button"]');
  
  // 验证登录成功
  await expect(page.locator('[data-testid="user-profile"]')).toBeVisible();
});
```

### 3. API Mock 测试

```javascript
test('任务列表展示', async ({ page }) => {
  // Mock API 响应
  await page.route('**/api/tasks', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        data: [
          { id: 1, title: '测试任务', status: 'pending' }
        ]
      })
    });
  });
  
  await page.goto('http://localhost:3000/tasks');
  await expect(page.locator('.task-item')).toHaveCount(1);
});
```

## 运行测试

```bash
# 运行所有测试
npx playwright test

# 运行特定测试文件
npx playwright test e2e/auth.spec.js

#  headed 模式（可以看到浏览器）
npx playwright test --headed

# 调试模式
npx playwright test --debug

# 生成报告
npx playwright show-report
```

## 最佳实践

1. **使用 data-testid 属性**：在组件中添加 `data-testid` 便于测试定位元素
2. **每个测试独立**：测试之间不应有依赖关系
3. **使用 beforeEach**：在每个测试前重置状态
4. **截图记录**：失败时自动截图便于排查问题

## 项目特定配置

针对本项目的 Playwright 配置：

```javascript
// playwright.config.js
module.exports = {
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
    headless: true,
    viewport: { width: 1280, height: 720 },
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
};
```
