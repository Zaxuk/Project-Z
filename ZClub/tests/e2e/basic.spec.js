const { test, expect } = require('@playwright/test');

test.describe('ZClub 基础功能测试', () => {
  
  test('首页可以正常访问并显示标题', async ({ page }) => {
    await page.goto('/');
    
    // 验证页面标题
    await expect(page.locator('h1')).toContainText('ZClub 积分系统');
    
    // 验证未登录状态显示
    await expect(page.locator('text=请先登录')).toBeVisible();
  });

  test('登录对话框可以正常打开和关闭', async ({ page }) => {
    await page.goto('/');
    
    // 点击登录按钮
    await page.click('text=登录');
    
    // 验证登录对话框显示
    await expect(page.locator('.el-dialog__title')).toContainText('登录');
    await expect(page.locator('text=邮箱')).toBeVisible();
    await expect(page.locator('text=密码')).toBeVisible();
    
    // 点击取消关闭对话框
    await page.click('text=取消');
    
    // 验证对话框已关闭
    await expect(page.locator('.el-dialog__title')).not.toBeVisible();
  });

  test('注册对话框可以正常打开和关闭', async ({ page }) => {
    await page.goto('/');
    
    // 点击注册按钮
    await page.click('text=注册');
    
    // 验证注册对话框显示
    await expect(page.locator('.el-dialog__title')).toContainText('注册');
    await expect(page.locator('text=姓名')).toBeVisible();
    await expect(page.locator('text=邮箱')).toBeVisible();
    await expect(page.locator('text=密码')).toBeVisible();
    
    // 点击取消关闭对话框
    await page.click('text=取消');
    
    // 验证对话框已关闭
    await expect(page.locator('.el-dialog__title')).not.toBeVisible();
  });

});
