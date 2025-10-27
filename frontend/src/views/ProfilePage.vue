<template>
  <div class="profile-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>个人信息</h2>
        </div>
      </template>

      <div class="profile-content">
        <!-- 头像上传 -->
        <div class="avatar-section">
          <el-upload
            class="avatar-uploader"
            action="/api/v1/users/me/avatar"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
          >
            <el-avatar
              v-if="userStore.user?.avatar_path"
              :size="100"
              :src="getAvatarUrl(userStore.user.avatar_path)"
            />
            <el-avatar v-else :size="100" :src="defaultAvatar">
              <span class="avatar-text">{{ userStore.user?.username?.charAt(0) || 'U' }}</span>
            </el-avatar>
            <div class="avatar-hover">
              <el-icon><Camera /></el-icon>
              <span>更换头像</span>
            </div>
          </el-upload>
        </div>

        <!-- 用户信息表单（用户名只读） -->
        <el-form
          :model="profileForm"
          :rules="rules"
          ref="profileFormRef"
          label-width="100px"
          class="profile-form"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="profileForm.username"
              placeholder="用户名"
              readonly
              disabled
            />
          </el-form-item>

          <el-form-item label="新密码" prop="password">
            <el-input
              v-model="profileForm.password"
              type="password"
              placeholder="请输入新密码（留空则不修改）"
              show-password
            />
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="profileForm.confirmPassword"
              type="password"
              placeholder="请确认新密码"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="updateProfile" :loading="loading">
              更新信息
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 账户操作 -->
        <el-card class="account-actions" header="账户操作">
          <div class="actions-content">
            <p>注册时间: {{ formatDate(userStore.user?.created_at) }}</p>
            <el-button type="danger" @click="showDeleteDialog = true">
              注销账户
            </el-button>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 注销账户确认对话框 -->
    <el-dialog
      v-model="showDeleteDialog"
      title="确认注销账户"
      width="400px"
      center
    >
      <span>确定要注销账户吗？此操作不可逆，所有数据将被删除。</span>
      <template #footer>
        <el-button @click="showDeleteDialog = false">取消</el-button>
        <el-button type="danger" @click="deleteAccount" :loading="deleting">
          确认注销
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user' // 关联优化后的userStore
import { ElMessage, ElMessageBox } from 'element-plus'
import { Camera } from '@element-plus/icons-vue'

// 初始化依赖
const router = useRouter()
const userStore = useUserStore()
const profileFormRef = ref()
const showDeleteDialog = ref(false)
const loading = ref(false)
const deleting = ref(false)

// 表单数据（用户名仅用于展示）
const profileForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

// 默认头像路径（根据项目实际路径调整）
const defaultAvatar = ref('/src/assets/default-avatar.png')

// 上传请求头（携带token）
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${userStore.token}`
}))

// 表单验证规则
const validatePassword = (rule, value, callback) => {
  if (value && value !== '') {
    if (value.length < 8) {
      callback(new Error('密码长度至少8位'))
    } else if (!/[a-zA-Z]/.test(value)) {
      callback(new Error('密码必须包含英文字母'))
    } else if (value !== profileForm.confirmPassword) {
      callback(new Error('两次输入密码不一致'))
    } else {
      callback()
    }
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (profileForm.password && value !== profileForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '用户名不可为空', trigger: 'blur' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 工具函数：获取头像完整URL
const getAvatarUrl = (avatarPath) => {
  if (!avatarPath) return defaultAvatar.value
  return `http://localhost:8000/static/avatars/${avatarPath}`
}

// 工具函数：格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  // 尝试解析日期，处理不同格式
  const date = new Date(dateString)
  if (isNaN(date.getTime())) {  // 检查日期是否有效
    return '格式错误'
  }
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 头像上传前验证
const beforeAvatarUpload = (file) => {
  const isJPGOrPNG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPGOrPNG) {
    ElMessage.error('头像只能是 JPG 或 PNG 格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

// 头像上传成功回调
const handleAvatarSuccess = () => {
  ElMessage.success('头像上传成功')
  // 无需手动更新userInfo：userStore.updateAvatar已同步本地存储
}

// 更新个人信息（仅更新密码，不包含用户名）
const updateProfile = async () => {
  if (!profileFormRef.value) return

  profileFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const updateData = {}
        // 仅当输入新密码时才传递password字段
        if (profileForm.password) {
          updateData.password = profileForm.password
        }

        await userStore.updateProfile(updateData)
        ElMessage.success('个人信息更新成功')
        // 重置密码输入框
        profileForm.password = ''
        profileForm.confirmPassword = ''
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '更新失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// 重置表单（保持用户名与userStore一致）
const resetForm = () => {
  if (profileFormRef.value) {
    profileFormRef.value.resetFields()
  }
  profileForm.username = userStore.user?.username || ''
  profileForm.password = ''
  profileForm.confirmPassword = ''
}

// 注销账户
const deleteAccount = async () => {
  deleting.value = true
  try {
    await ElMessageBox.confirm(
      '此操作将永久删除您的账户和所有数据，确定要继续吗？',
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await userStore.deleteAccount()
    ElMessage.success('账户注销成功')
    router.push('/login')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('注销账户失败')
    }
  } finally {
    deleting.value = false
    showDeleteDialog.value = false
  }
}

// 监听userStore.user变化，实时同步用户名
watch(
  () => userStore.user,
  (newUser) => {
    if (newUser) {
      profileForm.username = newUser.username || ''
    }
  },
  { immediate: true }
)

// 页面初始化：加载用户信息（防止本地存储无数据时空白）
onMounted(async () => {
  if (!userStore.user) {
    try {
      await userStore.fetchCurrentUser()
    } catch (error) {
      ElMessage.error('加载用户信息失败，请重新登录')
      router.push('/login')
    }
  }
  // 调试代码
  console.log('用户信息:', userStore.user)
  console.log('注册时间:', userStore.user?.created_at)
  profileForm.username = userStore.user?.username || ''
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.avatar-uploader {
  position: relative;
  cursor: pointer;
}

.avatar-uploader:hover .avatar-hover {
  opacity: 1;
}

.avatar-hover {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-text {
  font-size: 24px;
  font-weight: bold;
}

.profile-form {
  margin-top: 20px;
}

.account-actions {
  margin-top: 20px;
}

.actions-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.actions-content p {
  margin: 0;
  color: #666;
}

/* 优化只读输入框样式 */
:deep(.el-input.is-disabled .el-input__inner) {
  background-color: #f5f7fa;
  color: #303133;
  cursor: not-allowed;
}

:deep(.el-upload) {
  border: none;
  background: none;
}
</style>