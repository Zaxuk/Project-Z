import { createStore } from 'vuex'
import axios from 'axios'

export default createStore({
  state: {
    user: null,
    tasks: [],
    rewards: [],
    defaultRewards: [],
    points: 0,
    notifications: []
  },
  mutations: {
    setUser(state, user) {
      state.user = user
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
    setNotifications(state, notifications) {
      state.notifications = notifications
    }
  },
  actions: {
    async login({ commit }, credentials) {
      try {
        const response = await axios.post('/api/auth/login', credentials)
        commit('setUser', response.data.user)
        return response.data.user
      } catch (error) {
        throw error
      }
    },
    async register({ commit }, userData) {
      try {
        const response = await axios.post('/api/auth/register', userData)
        return response.data
      } catch (error) {
        throw error
      }
    },
    logout({ commit }) {
      commit('setUser', null)
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
    }
  },
  getters: {
    isLoggedIn: state => state.user !== null,
    isAdmin: state => state.user && state.user.role === 'admin',
    isParent: state => state.user && (state.user.role === 'admin' || state.user.role === 'parent'),
    isChild: state => state.user && state.user.role === 'child'
  }
})