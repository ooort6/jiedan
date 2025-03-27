import { defineStore } from 'pinia'
import { login, logout, getUserInfo } from '@/api/user'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userId: '',
    username: '',
    nickname: '',
    avatar: '',
    roles: [],
    permissions: []
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.roles.includes('ROLE_ADMIN')
  },

  actions: {
    // 设置Token
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
    },

    // 清除Token
    clearToken() {
      this.token = ''
      localStorage.removeItem('token')
    },

    // 保存用户信息
    setUserInfo(userInfo) {
      this.userId = userInfo.userId
      this.username = userInfo.username
      this.nickname = userInfo.nickname
      this.avatar = userInfo.avatar
      this.roles = userInfo.roles
      this.permissions = userInfo.permissions
    },

    // 清除用户信息
    clearUserInfo() {
      this.userId = ''
      this.username = ''
      this.nickname = ''
      this.avatar = ''
      this.roles = []
      this.permissions = []
    },

    // 登录
    async login(loginData) {
      try {
        const response = await login(loginData)
        if (response.code === 200) {
          this.setToken(response.data.token)
          this.setUserInfo(response.data)
          return Promise.resolve(response.data)
        } else {
          return Promise.reject(response.message || '登录失败')
        }
      } catch (error) {
        return Promise.reject(error)
      }
    },

    // 登出
    async logout() {
      try {
        await logout()
        this.clearToken()
        this.clearUserInfo()
        return Promise.resolve()
      } catch (error) {
        return Promise.reject(error)
      }
    },

    // 获取用户信息
    async getUserInfo() {
      try {
        const response = await getUserInfo()
        if (response.code === 200) {
          const data = response.data
          this.setUserInfo({
            userId: data.id,
            username: data.username,
            nickname: data.nickname,
            avatar: data.avatar,
            roles: data.roles || [],
            permissions: data.permissions || []
          })
          return Promise.resolve(data)
        } else {
          return Promise.reject(response.message || '获取用户信息失败')
        }
      } catch (error) {
        return Promise.reject(error)
      }
    },

    // 重置状态
    resetState() {
      this.clearToken()
      this.clearUserInfo()
    }
  }
}) 