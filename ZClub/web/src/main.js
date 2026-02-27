import { createApp } from 'vue'
import App from './App.vue'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/tailwind.css'
import axios from 'axios'

// 配置axios默认携带cookie
axios.defaults.withCredentials = true

const app = createApp(App)
app.use(store)
app.use(ElementPlus)

// 初始化登录状态（从cookie恢复）
store.dispatch('initAuth')

app.mount('#app')