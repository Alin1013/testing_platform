<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <h2>注册</h2>
      </template>

      <el-form
        :model="form"
        :rules="rules"
        ref="registerFormRef"
        enctype="multipart/form-data"
      >
        <!-- 头像上传（已修复默认头像逻辑） -->
        <el-form-item label="头像" prop="avatar">
          <div class="avatar-upload-section">
            <el-upload
              class="avatar-uploader"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleAvatarChange"
              :before-upload="beforeAvatarUpload"
              accept=".jpg,.jpeg,.png,.gif"
            >
              <!-- 优先显示上传预览图，无预览图则显示默认头像 -->
              <el-avatar
                :size="100"
                :src="avatarPreview || defaultAvatarImg"
                class="avatar"
              />
              <!-- 上传提示（hover时显示） -->
              <div class="avatar-uploader-icon">
                <el-icon><Plus /></el-icon>
                <div class="el-upload__text">点击更换头像</div>
              </div>
            </el-upload>
            <div class="avatar-tips">
              <p>支持 JPG、JPEG、PNG、GIF 格式</p>
              <p>文件大小不超过 2MB</p>
            </div>
          </div>
        </el-form-item>

        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" size="large" show-password>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleRegister"
            :loading="loading"
            size="large"
            style="width: 100%"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-link">
        <span>已有账号？</span>
        <el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock, Plus } from '@element-plus/icons-vue'
// 引入默认头像
import defaultAvatarImg from '../../../backend/static/avatars/default-avatar.png'

const router = useRouter()
const userStore = useUserStore()
const registerFormRef = ref()
const loading = ref(false)
const avatarFile = ref(null)
const avatarPreview = ref('')

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

// 密码验证函数
const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请确认密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少 8 个字符', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!/[a-zA-Z]/.test(value)) {
          callback(new Error('密码必须包含英文字母'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePassword, trigger: 'blur' }
  ]
})

// 头像文件变化处理
const handleAvatarChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
  avatarFile.value = file.raw
}

// 头像上传前的验证
const beforeAvatarUpload = (file) => {
  const isJPGOrPNG = file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/gif'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPGOrPNG) {
    ElMessage.error('头像只能是 JPG、JPEG、PNG 或 GIF 格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return

  registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const formData = new FormData()
        formData.append('username', form.username)
        formData.append('password', form.password)

        if (avatarFile.value) {
          formData.append('avatar', avatarFile.value)
        }

        const response = await fetch('http://localhost:8000/api/v1/register', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || '注册失败')
        }

        const userData = await response.json()
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      } catch (error) {
        ElMessage.error(error.message || '注册失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 450px;
}

.login-link {
  text-align: center;
  margin-top: 20px;
}

.avatar-upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.avatar-uploader {
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  position: relative; /* 用于定位上传提示 */
  overflow: hidden;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

/* 2. 优化上传提示样式：默认隐藏，hover时显示 */
.avatar-uploader-icon {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8c939d;
  background-color: rgba(255, 255, 255, 0.6); /* 半透明背景，不遮挡头像 */
  opacity: 0;
  transition: opacity 0.3s; /* 平滑过渡 */
}

.avatar-uploader:hover .avatar-uploader-icon {
  opacity: 1; /* hover时显示提示 */
}

.avatar {
  width: 100px;
  height: 100px;
}

.avatar-tips {
  text-align: center;
  color: #909399;
  font-size: 12px;
}

.avatar-tips p {
  margin: 2px 0;
}

:deep(.el-upload) {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>