import api from './index'

export const userAPI = {
  // 用户登录 - 增强错误处理
  async login(credentials) {
    try {
      const response = await api.post('/login', credentials)
      return response
    } catch (error) {
      // 统一错误格式，确保前端能正确解析
      if (error.response) {
        // 服务器返回错误状态码
        const serverError = new Error(error.response.data?.detail || '登录失败')
        serverError.response = error.response
        throw serverError
      } else if (error.request) {
        // 请求发送但无响应
        throw new Error('网络连接失败，请检查网络连接')
      } else {
        // 其他错误
        throw new Error(error.message || '登录失败')
      }
    }
  },

  // 用户注册 - 使用 FormData
  async register(userData) {
    try {
      // 创建 FormData 对象
      const formData = new FormData()
      formData.append('username', userData.username)
      formData.append('password', userData.password)

      // 如果有头像文件，添加到 FormData
      if (userData.avatar) {
        formData.append('avatar', userData.avatar)
      }

      const response = await api.post('/register', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response
    } catch (error) {
      if (error.response) {
        const serverError = new Error(error.response.data?.detail || '注册失败')
        serverError.response = error.response
        throw serverError
      } else if (error.request) {
        throw new Error('网络连接失败，请检查网络连接')
      } else {
        throw new Error(error.message || '注册失败')
      }
    }
  },

  // 获取当前用户信息
  async getCurrentUser() {
    try {
      const response = await api.get('/users/me')
      return response
    } catch (error) {
      if (error.response) {
        const serverError = new Error(error.response.data?.detail || '获取用户信息失败')
        serverError.response = error.response
        throw serverError
      } else if (error.request) {
        throw new Error('网络连接失败，请检查网络连接')
      } else {
        throw new Error(error.message || '获取用户信息失败')
      }
    }
  },

  // 更新用户信息
  async updateUser(userData) {
    try {
      const response = await api.put('/users/me', userData)
      return response
    } catch (error) {
      if (error.response) {
        const serverError = new Error(error.response.data?.detail || '更新用户信息失败')
        serverError.response = error.response
        throw serverError
      } else if (error.request) {
        throw new Error('网络连接失败，请检查网络连接')
      } else {
        throw new Error(error.message || '更新用户信息失败')
      }
    }
  },

  // 更新用户头像
  async updateAvatar(avatarFile) {
    try {
      const formData = new FormData()
      formData.append('file', avatarFile)

      const response = await api.post('/users/me/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response
    } catch (error) {
      if (error.response) {
        const serverError = new Error(error.response.data?.detail || '头像上传失败')
        serverError.response = error.response
        throw serverError
      } else if (error.request) {
        throw new Error('网络连接失败，请检查网络连接')
      } else {
        throw new Error(error.message || '头像上传失败')
      }
    }
  },

  // 删除账户
  async deleteAccount() {
    try {
      const response = await api.delete('/users/me')
      return response
    } catch (error) {
      if (error.response) {
        const serverError = new Error(error.response.data?.detail || '账户删除失败')
        serverError.response = error.response
        throw serverError
      } else if (error.request) {
        throw new Error('网络连接失败，请检查网络连接')
      } else {
        throw new Error(error.message || '账户删除失败')
      }
    }
  }
}

export default userAPI