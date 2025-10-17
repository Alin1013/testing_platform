import api from './index'

export const userAPI = {
  // 用户登录
  login(credentials) {
    return api.post('/login', credentials)
  },

  // 用户注册
  register(userData) {
    return api.post('/register', userData)
  },

  // 获取当前用户信息
  getCurrentUser() {
    return api.get('/users/me')
  },

  // 更新用户信息
  updateUser(userData) {
    return api.put('/users/me', userData)
  },

  // 更新用户头像
  updateAvatar(avatarFile) {
    const formData = new FormData()
    formData.append('file', avatarFile)
    return api.post('/users/me/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

export default userAPI