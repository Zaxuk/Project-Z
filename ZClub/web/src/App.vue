<template>
  <div class="app">
    <el-container>
      <el-header>
        <h1>ZClub 积分系统</h1>
        <el-button v-if="!isLoggedIn" @click="showLoginDialog = true">登录</el-button>
        <el-button v-if="!isLoggedIn" @click="showRegisterDialog = true">注册</el-button>
        <el-button v-else @click="logout">退出</el-button>
      </el-header>
      <el-main>
        <el-dialog
          v-model="showLoginDialog"
          title="登录"
          width="400px"
        >
          <el-form :model="loginForm" label-width="80px">
            <el-form-item label="邮箱">
              <el-input v-model="loginForm.email" placeholder="请输入邮箱"></el-input>
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
            </el-form-item>
          </el-form>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="showLoginDialog = false">取消</el-button>
              <el-button type="primary" @click="login">登录</el-button>
            </span>
          </template>
        </el-dialog>

        <el-dialog
          v-model="showRegisterDialog"
          title="注册"
          width="400px"
        >
          <el-form :model="registerForm" label-width="80px">
            <el-form-item label="姓名">
              <el-input v-model="registerForm.name" placeholder="请输入姓名"></el-input>
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="registerForm.email" placeholder="请输入邮箱"></el-input>
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="registerForm.password" type="password" placeholder="请输入密码"></el-input>
            </el-form-item>
          </el-form>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="showRegisterDialog = false">取消</el-button>
              <el-button type="primary" @click="register">注册</el-button>
            </span>
          </template>
        </el-dialog>

        <div v-if="isLoggedIn">
          <el-menu :default-active="activeMenu" class="el-menu-demo" mode="horizontal" @select="handleMenuSelect">
            <el-menu-item index="tasks">任务</el-menu-item>
            <el-menu-item index="rewards">奖励</el-menu-item>
            <el-menu-item index="points">积分</el-menu-item>
            <el-menu-item index="notifications">通知</el-menu-item>
          </el-menu>
          <div class="content">
            <tasks v-if="activeMenu === 'tasks'" />
            <rewards v-if="activeMenu === 'rewards'" />
            <points v-if="activeMenu === 'points'" />
            <notifications v-if="activeMenu === 'notifications'" />
          </div>
        </div>
        <div v-else>
          <h2>请先登录</h2>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import Tasks from './components/Tasks.vue'
import Rewards from './components/Rewards.vue'
import Points from './components/Points.vue'
import Notifications from './components/Notifications.vue'

export default {
  name: 'App',
  components: {
    Tasks,
    Rewards,
    Points,
    Notifications
  },
  setup() {
    const store = useStore()
    const showLoginDialog = ref(false)
    const showRegisterDialog = ref(false)
    const activeMenu = ref('tasks')
    const loginForm = ref({
      email: '',
      password: ''
    })
    const registerForm = ref({
      name: '',
      email: '',
      password: ''
    })

    const isLoggedIn = computed(() => store.getters.isLoggedIn)
    
    // 页面加载时初始化登录状态
    onMounted(() => {
      store.dispatch('initAuth')
    })

    const login = async () => {
      try {
        await store.dispatch('login', loginForm.value)
        showLoginDialog.value = false
      } catch (error) {
        console.error('Login failed:', error)
      }
    }

    const register = async () => {
      try {
        // 默认设置为管理员角色
        const userData = {
          ...registerForm.value,
          role: 'admin'
        }
        await store.dispatch('register', userData)
        showRegisterDialog.value = false
      } catch (error) {
        console.error('Register failed:', error)
      }
    }

    const logout = () => {
      store.dispatch('logout')
    }

    const handleMenuSelect = (key) => {
      activeMenu.value = key
    }

    return {
      showLoginDialog,
      showRegisterDialog,
      activeMenu,
      loginForm,
      registerForm,
      isLoggedIn,
      login,
      register,
      logout,
      handleMenuSelect
    }
  }
}
</script>

<style>
.app {
  height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.el-header h1 {
  margin: 0;
}

.content {
  margin-top: 20px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}
</style>