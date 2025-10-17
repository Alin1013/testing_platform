<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>登录</h2>
      </template>
      <el-form :model="form" :rules="rules" ref="loginFormRef">
        <!-- 用户名输入框 -->
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 密码输入框 -->
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 全局错误提示 -->
        <el-form-item v-if="globalError" class="error-tip">
          <el-alert
            type="error"
            :title="globalErrorTitle"
            :description="globalError"
            show-icon
            :closable="true"
            @close="handleCloseError"
            center
            effect="dark"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleLogin"
            :loading="loading"
            size="large"
            style="width: 100%"
          >
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
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref()
const loading = ref(false)

// 错误状态管理
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

// 手动关闭错误提示
const handleCloseError = () => {
  globalError.value = ''
  globalErrorTitle.value = '登录失败'
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  // 验证表单
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  handleCloseError() // 开始新的登录尝试时清除旧错误

  try {
    await userStore.login(form)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    console.error('登录错误详情:', error)

    // 提取错误信息
    let errorMsg = '登录失败，请稍后重试'

    // 处理不同类型的错误
    if (error.response) {
      // 服务器返回错误
      errorMsg = error.response.data?.detail || error.response.data?.message || '登录失败'
    } else if (error.request) {
      // 网络错误
      errorMsg = '网络连接失败，请检查网络连接'
    } else {
      // 其他错误
      errorMsg = error.message || '登录失败'
    }

    // 根据错误信息类型设置不同的提示
    if (errorMsg.includes('不存在') ||
        errorMsg.toLowerCase().includes('not found') ||
        errorMsg.toLowerCase().includes('incorrect') ||
        errorMsg.includes('用户')) {
      globalErrorTitle.value = '用户名不存在'
      globalError.value = '当前用户名不存在，请检查输入或前往注册'
    } else if (errorMsg.includes('密码') ||
               errorMsg.toLowerCase().includes('password')) {
      globalErrorTitle.value = '密码错误'
      globalError.value = '密码输入错误，请重新输入'
      form.password = '' // 清空密码框
    } else if (errorMsg.includes('禁用') ||
               errorMsg.toLowerCase().includes('inactive')) {
      globalErrorTitle.value = '账号异常'
      globalError.value = '您的账号已被禁用，请联系管理员'
    } else if (errorMsg.includes('网络') ||
               errorMsg.includes('连接') ||
               errorMsg.toLowerCase().includes('network')) {
      globalErrorTitle.value = '网络错误'
      globalError.value = '网络连接失败，请检查网络连接后重试'
    } else {
      globalErrorTitle.value = '登录失败'
      globalError.value = errorMsg
    }

    // 确保错误提示显示
    await nextTick()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #e3e6ef 0%, #e3e6ef 100%);
}

.login-card {
  width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.register-link {
  text-align: center;
  margin-top: 20px;
}

/* 错误提示样式优化 */
.error-tip {
  margin-bottom: 16px;
}

/* 确保错误提示样式正确 */
:deep(.el-alert) {
  border: 1px solid #f56c6c;
  border-radius: 4px;
}

:deep(.el-alert__title) {
  font-weight: bold;
  color: #f56c6c;
}

:deep(.el-alert__description) {
  color: #f56c6c;
  margin-top: 4px;
}
</style>