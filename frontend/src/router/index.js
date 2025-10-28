import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginPage.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterPage.vue'),
    meta: { requiresAuth: false, title: '注册' }
  },
  {
    path: '/',
    name: 'Home',
  },

  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/views/ProjectsPage.vue'),
    meta: { requiresAuth: true, title: '项目管理' }
  },
  {
    path: '/projects/:projectId',
    name: 'ProjectDetail',
    component: () => import('@/views/ProjectsPage.vue'),
    meta: { requiresAuth: true, title: '项目详情' }
  },
  {
    path: '/api-test',
    name: 'ApiTest',
    component: () => import('@/views/ApiTest.vue'),
    meta: { requiresAuth: true, title: 'API测试' }
  },
  {
    path: '/api-test/:projectId?',
    name: 'ApiTestWithProject',
    component: () => import('@/views/ApiTest.vue'),
    meta: { requiresAuth: true, title: 'API测试' }
  },
  {
    path: '/ui-test',
    name: 'UiTest',
    component: () => import('@/views/UiTest.vue'),
    meta: { requiresAuth: true, title: 'UI测试' }
  },
  {
    path: '/performance',
    name: 'Performance',
    component: () => import('@/views/PerformancePage.vue'),
    meta: { requiresAuth: true, title: '性能测试' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfilePage.vue'),
    meta: { requiresAuth: true, title: '个人资料' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 测试平台`
  }

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && userStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router