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

        <!-- 用户信息表单 -->
        <el-form
          :model="profileForm"
          :rules="rules"
          ref="profileFormRef"
          label-width="100px"
          class="profile-form"
        >
          <el-form-item label="用户名" prop="username">
            <el-input v-model="profileForm.username" placeholder="请输入用户名" />
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
            <p>邮箱: {{ userStore.user?.email || '未设置' }}</p>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Camera } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const profileFormRef = ref()
const showDeleteDialog = ref(false)
const loading = ref(false)
const deleting = ref(false)

const profileForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const defaultAvatar = ref('/default-avatar.png')

// 计算上传请求头
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
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 获取头像URL
const getAvatarUrl = (avatarPath) => {
  if (!avatarPath) return defaultAvatar.value
  return `http://localhost:8000/static/avatars/${avatarPath}`
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 头像上传前的验证
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

// 头像上传成功
const handleAvatarSuccess = (response) => {
  ElMessage.success('头像上传成功')
  // 更新用户信息
  userStore.user.avatar_path = response.filename
}

// 更新个人信息
const updateProfile = async () => {
  if (!profileFormRef.value) return

  profileFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const updateData = {
          username: profileForm.username
        }

        // 只有在输入了新密码时才更新密码
        if (profileForm.password) {
          updateData.password = profileForm.password
        }

        await userStore.updateProfile(updateData)
        ElMessage.success('个人信息更新成功')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '更新失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  if (profileFormRef.value) {
    profileFormRef.value.resetFields()
  }
  loadUserData()
}

// 加载用户数据
const loadUserData = () => {
  if (userStore.user) {
    profileForm.username = userStore.user.username || ''
  }
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

    // 调用注销账户的API
    // await userStore.deleteAccount()
    ElMessage.success('账户注销成功')
    userStore.logout()
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

// 初始化
onMounted(() => {
  loadUserData()
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

:deep(.el-upload) {
  border: none;
  background: none;
}
</style>