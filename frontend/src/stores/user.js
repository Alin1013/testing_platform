import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userAPI } from '../api/user'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const isAuthenticated = ref(!!token.value)

  const login = async (credentials) => {
    try {
      const response = await userAPI.login(credentials)
      token.value = response.data.access_token
      user.value = response.data.user
      isAuthenticated.value = true
      localStorage.setItem('token', token.value)
      return response
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
  }

  const register = async (userData) => {
    try {
      const response = await userAPI.register(userData)
      return response
    } catch (error) {
      throw error
    }
  }

  const updateProfile = async (profileData) => {
    try {
      const response = await userAPI.updateUser(profileData)
      if (user.value) {
        user.value = { ...user.value, ...response.data }
      }
      return response
    } catch (error) {
      throw error
    }
  }

  const updateAvatar = async (avatarFile) => {
    try {
      const response = await userAPI.updateAvatar(avatarFile)
      if (user.value) {
        user.value.avatar_path = response.data.filename
      }
      return response
    } catch (error) {
      throw error
    }
  }

  const fetchCurrentUser = async () => {
    try {
      const response = await userAPI.getCurrentUser()
      user.value = response.data
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
    fetchCurrentUser
  }
})