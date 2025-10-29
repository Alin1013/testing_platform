import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/views/LoginPage.vue'
import ProjectsPage from '@/views/ProjectsPage.vue'
import ApiPage from '@/views/ApiTest.vue'
import UiTest from '@/views/UiTest.vue'
import PerformancePage from '@/views/PerformancePage.vue'
import ProfilePage from "@/views/ProfilePage.vue"
import RegisterPage from "@/views/RegisterPage.vue"

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresGuest: true } // 仅未登录用户可访问
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
    meta: { requiresGuest: true }
  },
  {
    path: '/profile',
    name: 'ProfilePage',
    component: ProfilePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: ProjectsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/:projectId/api-test',
    name: 'ApiTest',
    component: ApiPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/:projectId/ui-test',
    name: 'UiTest',
    component: UiTest,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/:projectId/performance-test',
    name: 'PerformanceTest',
    component: PerformancePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    redirect: '/projects'
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/projects' // 或者可以重定向到404页面
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 增强的路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const isAuthenticated = !!token

  // 检查路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      // 重定向到登录页，并保存目标路由以便登录后跳转
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  }
  // 检查路由是否需要未登录状态（如登录页、注册页）
  else if (to.matched.some(record => record.meta.requiresGuest)) {
    if (isAuthenticated) {
      // 已登录用户访问登录/注册页，重定向到项目页
      next('/projects')
    } else {
      next()
    }
  }
  // 其他路由直接放行
  else {
    next()
  }
})

// 可选的：响应式认证状态检查
router.afterEach((to) => {
  // 可以在这里添加页面访问统计等
  console.log(`Navigated to: ${to.name}`)
})

export default router