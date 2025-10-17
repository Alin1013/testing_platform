<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>登录</h2>
      </template>
      <el-form :model="form" :rules="rules" ref="loginFormRef">
        <!-- 用户名输入框：新增错误提示关联 -->
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <!-- 密码输入框：新增错误提示关联 -->
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <!-- 全局错误提示：专门显示账号密码匹配类错误 -->
        <el-form-item v-if="globalError" class="error-tip">
          <el-alert
            type="error"
            title="登录失败"
            :description="globalError"
            show-icon
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
import { ElMessage, ElAlert } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref()
const loading = ref(false)
// 新增：存储全局登录错误信息（如用户名不存在、密码错误）
const globalError = ref('')

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

const handleLogin = async () => {
  if (!loginFormRef.value) return
  // 每次登录前清空上一次的错误提示
  globalError.value = ''

  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(form)
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        // 核心：根据后端返回的错误信息，区分不同场景
        const errorMsg = error.response?.data?.detail || '登录失败，请稍后重试'

        // 场景1：用户名不存在（需后端返回包含“不存在”的提示，如“用户不存在”）
        if (errorMsg.includes('不存在')) {
          globalError.value = '当前用户名不存在，请检查输入或前往注册'
        }
        // 场景2：密码错误（需后端返回包含“密码”的提示，如“密码错误”）
        else if (errorMsg.includes('密码')) {
          globalError.value = '密码输入错误，请重新输入'
          // 可选：密码错误时自动清空密码框，提升安全性
          form.password = ''
        }
        // 场景3：其他错误（如网络异常、服务器问题）
        else {
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
/* 新增：错误提示样式优化，与输入框对齐 */
.error-tip {
  margin-bottom: 0;
  padding-bottom: 0;
}
/* 调整Alert组件间距，避免过于拥挤 */
:deep(.el-alert) {
  margin-bottom: 8px;
}
</style>