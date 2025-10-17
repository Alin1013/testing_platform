import api from './index'

export const userAPI = {
  // 用户登录
  login(credentials) {
    return api.post('/login', credentials)
  },

  // 用户注册 - 使用 FormData
  register(userData) {
    // 创建 FormData 对象
    const formData = new FormData()
    formData.append('username', userData.username)
    formData.append('password', userData.password)

    // 如果有头像文件，添加到 FormData
    if (userData.avatar) {
      formData.append('avatar', userData.avatar)
    }

    return api.post('/register', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
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
  },

  // 删除账户
  deleteAccount() {
    return api.delete('/users/me')
  }
}

export default userAPI