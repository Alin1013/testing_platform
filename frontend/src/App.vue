<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <el-header v-if="showHeader" class="app-header">
      <div class="header-content">
        <div class="logo-section">
          <h1 class="logo">测试平台</h1>
        </div>

        <div class="nav-section">
          <h2>项目管理</h2>
        </div>

        <div class="user-section">
          <el-dropdown @command="handleUserCommand" v-if="userStore.isAuthenticated">
            <span class="user-info">
              <el-avatar :size="32" :src="getAvatarUrl(userStore.user?.avatar_path)" class="user-avatar" />
              <span class="username">{{ userStore.user?.username }}</span>
              <el-icon><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <div v-else class="login-register">
            <el-button type="text" @click="$router.push('/login')">登录</el-button>
            <el-button type="primary" @click="$router.push('/register')">注册</el-button>
          </div>
        </div>
      </div>
    </el-header>

    <!-- 主内容区域 -->
    <el-main class="app-main">
      <router-view />
    </el-main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from './stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowDown,
  User,
  SwitchButton
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeIndex = ref('/')

// 计算是否显示顶部导航栏
const showHeader = computed(() => {
  return !['/login', '/register'].includes(route.path)
})

// 获取头像URL
const getAvatarUrl = (avatarPath) => {
  if (!avatarPath) return '/default-avatar.png'
  return `http://localhost:8000/static/avatars/${avatarPath}`
}

// 监听路由变化，更新激活的菜单项
const updateActiveMenu = () => {
  activeIndex.value = route.path
}

// 处理菜单选择
const handleSelect = (index) => {
  activeIndex.value = index
}

// 处理用户命令
const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 处理退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }).catch(() => {
    // 用户取消操作
  })
}

// 初始化
onMounted(() => {
  updateActiveMenu()

  // 监听路由变化
  router.afterEach(() => {
    updateActiveMenu()
  })
})
</script>

<style scoped>
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.app-header {
  padding: 0;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  height: 60px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo-section {
  display: flex;
  align-items: center;
}

.logo {
  color: #409eff;
  font-size: 20px;
  margin: 0;
  font-weight: 600;
}

.nav-section {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-menu {
  border-bottom: none;
}

.user-section {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.user-avatar {
  margin-right: 8px;
}

.username {
  margin-right: 5px;
  font-size: 14px;
}

.login-register {
  display: flex;
  align-items: center;
  gap: 10px;
}

.app-main {
  flex: 1;
  padding: 0;
  background-color: #f5f7fa;
  overflow: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 10px;
  }

  .logo {
    font-size: 16px;
  }

  .username {
    display: none;
  }
}
</style>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
}

/* Element Plus 组件样式调整 */
.el-menu--horizontal > .el-menu-item {
  height: 60px;
  line-height: 60px;
}

.el-dropdown-menu__item {
  display: flex;
  align-items: center;
}

.el-dropdown-menu__item .el-icon {
  margin-right: 8px;
}
</style>