const { test, expect } = require('@playwright/test');

test.describe('ZClub 认证功能测试', () => {
  
  test('登录表单验证 - 空字段', async ({ page }) => {
    await page.goto('/');
    
    // 打开登录对话框
    await page.click('text=登录');
    
    // 直接点击登录按钮（不填写任何字段）
    await page.click('.el-dialog__footer button:has-text("登录")');
    
    // 验证对话框仍然打开（因为没有填写字段）
    await expect(page.locator('.el-dialog__title')).toContainText('登录');
  });

  test('登录表单可以填写', async ({ page }) => {
    await page.goto('/');
    
    // 打开登录对话框
    await page.click('text=登录');
    
    // 填写登录表单
    await page.fill('.el-dialog input[placeholder*="邮箱"]', 'test@example.com');
    await page.fill('.el-dialog input[type="password"]', 'password123');
    
    // 验证输入的值
    await expect(page.locator('.el-dialog input[placeholder*="邮箱"]')).toHaveValue('test@example.com');
    await expect(page.locator('.el-dialog input[type="password"]')).toHaveValue('password123');
  });

  test('注册表单可以填写', async ({ page }) => {
    await page.goto('/');
    
    // 打开注册对话框
    await page.click('text=注册');
    
    // 填写注册表单
    await page.fill('.el-dialog input[placeholder*="姓名"]', '测试用户');
    await page.fill('.el-dialog input[placeholder*="邮箱"]', 'newuser@example.com');
    await page.fill('.el-dialog input[type="password"]', 'newpassword123');
    
    // 验证输入的值
    await expect(page.locator('.el-dialog input[placeholder*="姓名"]')).toHaveValue('测试用户');
    await expect(page.locator('.el-dialog input[placeholder*="邮箱"]')).toHaveValue('newuser@example.com');
    await expect(page.locator('.el-dialog input[type="password"]')).toHaveValue('newpassword123');
  });

});
