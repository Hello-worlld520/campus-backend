import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import HomeView from '../views/HomeView.vue' 

const routes = [
  {
    path: '/',
    name: 'login',
    component: LoginView,
    meta: {
      title: '登录 - SENTINEL'
    }
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView,
    meta: {
      title: '首页 - SENTINEL',
      requiresAuth: true
    }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: {
      title: '监控大屏 - SENTINEL',
      requiresAuth: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes
})

router.beforeEach((to, from) => {
  const isLoggedIn =
    localStorage.getItem('sentinel_logged_in') === '1' ||
    sessionStorage.getItem('sentinel_logged_in') === '1'

  if (to.path === '/') {
    return true 
  }

  if (to.meta.requiresAuth && !isLoggedIn) {
    return '/'
  }

  return true
})

router.afterEach((to) => {
  if (to.meta?.title) {
    document.title = to.meta.title
  }
})

export default router