<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>登录</h2>
      </template>
      <el-form :model="form" :rules="rules" ref="loginFormRef">
        <!-- 用户名输入框 -->
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large" @input="clearGlobalError">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <!-- 密码输入框 -->
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password @input="clearGlobalError">
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <!-- 全局错误提示：手动关闭 -->
        <el-form-item v-if="globalError" class="error-tip">
          <el-alert
            type="error"
            :title="globalErrorTitle"
            :description="globalError"
            show-icon
            :closable="true"
            @close="handleCloseError"
            size="small"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" size="large" style="width: 100%">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="register-link">
        <span>没有账号？</span>
        <el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref()
const loading = ref(false)
// 存储全局登录错误信息
const globalError = ref('')
const globalErrorTitle = ref('登录失败')

const form = reactive({
  username: '',
  password: ''
})

const rules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少 8 个字符', trigger: 'blur' }
  ]
})

// 清除错误提示
const clearGlobalError = () => {
  globalError.value = ''
}

// 手动关闭错误提示
const handleCloseError = () => {
  globalError.value = ''
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  // 每次登录前清空上一次的错误提示
  clearGlobalError()

  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(form)
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        // 根据后端返回的错误信息，区分不同场景
        const errorMsg = error.response?.data?.detail || error.message || '登录失败，请稍后重试'

        // 场景1：用户名不存在
        if (errorMsg.includes('不存在') || errorMsg.includes('not found') || errorMsg.includes('incorrect')) {
          globalErrorTitle.value = '用户名不存在'
          globalError.value = '当前用户名不存在，请检查输入或前往注册'
        }
        // 场景2：密码错误
        else if (errorMsg.includes('密码') || errorMsg.includes('password')) {
          globalErrorTitle.value = '密码错误'
          globalError.value = '密码输入错误，请重新输入'
          // 密码错误时自动清空密码框
          form.password = ''
        }
        // 场景3：网络错误
        else if (errorMsg.includes('network') || errorMsg.includes('Network')) {
          globalErrorTitle.value = '网络错误'
          globalError.value = '网络连接失败，请检查网络连接'
        }
        // 场景4：其他错误
        else {
          globalErrorTitle.value = '登录失败'
          globalError.value = errorMsg
        }
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
}
.register-link {
  text-align: center;
  margin-top: 20px;
}
/* 错误提示样式优化 */
.error-tip {
  margin-bottom: 0;
  padding-bottom: 0;
}
/* 调整Alert组件间距 */
:deep(.el-alert) {
  margin-bottom: 8px;
}
/* 确保错误提示不会自动消失，手动关闭 */
:deep(.el-alert) {
  opacity: 1 !important;
}
</style>