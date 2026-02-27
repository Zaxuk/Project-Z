import { createStore } from 'vuex'
import axios from 'axios'
import { setCookie, getCookie, deleteCookie } from '../utils/cookie'

// 从cookie获取token
const getTokenFromCookie = () => {
  return getCookie('token')
}

// 从localStorage获取用户数据（作为备份）
const getUserFromStorage = () => {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

export default createStore({
  state: {
    user: getUserFromStorage(),
    token: getTokenFromCookie(),
    tasks: [],
    rewards: [],
    defaultRewards: [],
    points: 0,
    pointRecords: [],
    notifications: []
  },
  mutations: {
    setUser(state, user) {
      state.user = user
      // 保存到localStorage
      if (user) {
        localStorage.setItem('user', JSON.stringify(user))
      } else {
        localStorage.removeItem('user')
      }
    },
    setToken(state, token) {
      state.token = token
      // 保存到cookie，7天过期
      if (token) {
        setCookie('token', token, 7)
      } else {
        deleteCookie('token')
      }
    },
    setTasks(state, tasks) {
      state.tasks = tasks
    },
    setRewards(state, rewards) {
      state.rewards = rewards
    },
    setDefaultRewards(state, rewards) {
      state.defaultRewards = rewards
    },
    setPoints(state, points) {
      state.points = points
    },
    setPointRecords(state, pointRecords) {
      state.pointRecords = pointRecords
    },
    setNotifications(state, notifications) {
      state.notifications = notifications
    }
  },
  actions: {
    async login({ commit }, credentials) {
      try {
        const response = await axios.post('/api/auth/login', credentials)
        const { user, token } = response.data
        
        // 保存用户信息和token
        commit('setUser', user)
        commit('setToken', token)
        
        // 设置axios默认请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        
        return user
      } catch (error) {
        throw error
      }
    },
    async register({ commit, dispatch }, userData) {
      try {
        const response = await axios.post('/api/auth/register', userData)
        const { user, token } = response.data
        
        // 保存用户信息和token
        commit('setUser', user)
        commit('setToken', token)
        
        // 设置axios默认请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        
        return response.data
      } catch (error) {
        throw error
      }
    },
    logout({ commit }) {
      commit('setUser', null)
      commit('setToken', null)
      
      // 清除axios请求头
      delete axios.defaults.headers.common['Authorization']
    },
    // 初始化登录状态（页面刷新时调用）
    initAuth({ commit, state }) {
      const token = state.token || getTokenFromCookie()
      const user = state.user || getUserFromStorage()
      
      if (token && user) {
        commit('setToken', token)
        commit('setUser', user)
        
        // 设置axios默认请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        
        return true
      }
      
      return false
    },
    async fetchTasks({ commit, state }) {
      if (!state.user) return
      try {
        const response = await axios.get(`/api/tasks/family/${state.user.familyId}`)
        commit('setTasks', response.data)
      } catch (error) {
        console.error('Failed to fetch tasks:', error)
      }
    },
    async fetchRewards({ commit, state }) {
      if (!state.user) return
      try {
        const response = await axios.get(`/api/rewards/family/${state.user.familyId}`)
        commit('setRewards', response.data)
      } catch (error) {
        console.error('Failed to fetch rewards:', error)
      }
    },
    async fetchDefaultRewards({ commit }) {
      try {
        const response = await axios.get('/api/rewards/default')
        commit('setDefaultRewards', response.data)
      } catch (error) {
        console.error('Failed to fetch default rewards:', error)
      }
    },
    async completeTask({ dispatch }, { taskId, userId }) {
      try {
        await axios.post(`/api/tasks/${taskId}/complete`, { userId })
        await dispatch('fetchTasks')
      } catch (error) {
        console.error('Failed to complete task:', error)
      }
    },
    async redeemReward({ dispatch }, { rewardId, userId }) {
      try {
        await axios.post(`/api/rewards/${rewardId}/redeem`, { userId })
        await dispatch('fetchRewards')
      } catch (error) {
        console.error('Failed to redeem reward:', error)
      }
    },
    async fetchNotifications({ commit, state }) {
      if (!state.user) return
      try {
        const response = await axios.get(`/api/notifications/${state.user.id}`)
        commit('setNotifications', response.data)
      } catch (error) {
        console.error('Failed to fetch notifications:', error)
      }
    },
    async markNotificationAsRead({ commit, state }, notificationId) {
      try {
        await axios.put(`/api/notifications/${notificationId}/read`)
        const notifications = state.notifications.map(n => 
          n.id === notificationId ? { ...n, readStatus: 'read' } : n
        )
        commit('setNotifications', notifications)
      } catch (error) {
        console.error('Failed to mark notification as read:', error)
      }
    },
    async fetchPoints({ commit, state }) {
      if (!state.user) return
      try {
        const balanceResponse = await axios.get(`/api/points/balance/${state.user.id}`)
        commit('setPoints', balanceResponse.data.balance)
        
        const recordsResponse = await axios.get(`/api/points/records/${state.user.id}`)
        commit('setPointRecords', recordsResponse.data)
      } catch (error) {
        console.error('Failed to fetch points:', error)
      }
    }
  },
  getters: {
    isLoggedIn: state => state.user !== null && state.token !== null,
    isAdmin: state => state.user && state.user.role === 'admin',
    isParent: state => state.user && (state.user.role === 'admin' || state.user.role === 'parent'),
    isChild: state => state.user && state.user.role === 'child',
    getToken: state => state.token
  }
})
