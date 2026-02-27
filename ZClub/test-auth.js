const axios = require('axios');

const API_URL = 'http://localhost:8081/api/auth';

async function testRegister() {
  console.log('=== 测试注册功能 ===');
  try {
    const response = await axios.post(`${API_URL}/register`, {
      name: '测试用户',
      email: 'test@example.com',
      password: '123456',
      role: 'admin'
    });
    console.log('注册成功:', response.data);
    return response.data;
  } catch (error) {
    console.error('注册失败:', error.message);
    throw error;
  }
}

async function testLogin() {
  console.log('\n=== 测试登录功能 ===');
  try {
    const response = await axios.post(`${API_URL}/login`, {
      email: 'test@example.com',
      password: '123456'
    });
    console.log('登录成功:', response.data);
    return response.data;
  } catch (error) {
    console.error('登录失败:', error.message);
    throw error;
  }
}

async function runTests() {
  try {
    await testRegister();
    await testLogin();
    console.log('\n✅ 所有测试通过！');
  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);
  }
}

runTests();
