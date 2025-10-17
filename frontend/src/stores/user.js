import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userAPI } from '../api/user'

export const useUserStore = defineStore('user', () => {
  // 从localStorage恢复状态：token + userInfo（解决刷新丢失）
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(
    localStorage.getItem('userInfo') ? JSON.parse(localStorage.getItem('userInfo')) : null
  )
  const isAuthenticated = ref(!!token.value)

  // 登录：成功后持久化 token 和 userInfo
  const login = async (credentials) => {
    try {
      const response = await userAPI.login(credentials)
      token.value = response.data.access_token
      user.value = response.data.user
      isAuthenticated.value = true
      // 持久化到本地存储
      localStorage.setItem('token', token.value)
      localStorage.setItem('userInfo', JSON.stringify(user.value))
      return response
    } catch (error) {
      // 重新抛出错误，让组件能够捕获并显示
      throw error
    }
  }

  // 退出：清空状态并删除本地存储
  const logout = () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  // 注册：保持原有逻辑
  const register = async (userData) => {
    try {
      const response = await userAPI.register(userData)
      return response
    } catch (error) {
      throw error
    }
  }

  // 更新个人信息：同步更新本地存储的 userInfo
  const updateProfile = async (profileData) => {
    try {
      const response = await userAPI.updateUser(profileData)
      if (user.value) {
        user.value = { ...user.value, ...response.data }
        // 同步更新本地存储
        localStorage.setItem('userInfo', JSON.stringify(user.value))
      }
      return response
    } catch (error) {
      throw error
    }
  }

  // 更新头像：同步更新 userInfo 中的头像路径
  const updateAvatar = async (avatarFile) => {
    try {
      const response = await userAPI.updateAvatar(avatarFile)
      if (user.value) {
        user.value.avatar_path = response.data.filename
        // 同步更新本地存储
        localStorage.setItem('userInfo', JSON.stringify(user.value))
      }
      return response
    } catch (error) {
      throw error
    }
  }

  // 获取当前用户信息：用于页面初始化加载
  const fetchCurrentUser = async () => {
    try {
      const response = await userAPI.getCurrentUser()
      user.value = response.data
      // 持久化到本地存储（防止未登录时调用导致状态丢失）
      localStorage.setItem('userInfo', JSON.stringify(user.value))
      return response
    } catch (error) {
      throw error
    }
  }

  // 注销账户：调用后退出登录
  const deleteAccount = async () => {
    try {
      const response = await userAPI.deleteAccount()
      logout() // 自动触发本地存储清空
      return response
    } catch (error) {
      throw error
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    register,
    updateProfile,
    updateAvatar,
    fetchCurrentUser,
    deleteAccount
  }
})