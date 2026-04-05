import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path:'/',
      name:'home',
      component: ()=> import('../views/HomwView.vue')
    },
    {
      path:'/login',
      name:'login',
      component: ()=> import('../views/LoginView.vue')
    },
    {
      path:'/register-company',
      name:'register-company',
      component: ()=> import('../views/CompanyRegisterView.vue')
    },
    {
      path:'/register-student',
      name:'register-studenty',
      component: ()=> import('../views/StudentRegisterView.vue')
    },
    {
      path: '/admin',
      component: () => import('@/views/admin/DashboardView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/student',
      component: () => import('@/views/student/DashboardView.vue'),
      meta: { requiresAuth: true, role: 'student' }
    },
  ],
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  const isAuthenticated = auth.isAuthenticated
  const roles = auth.getUserRoles()

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login')
  }

  if (to.meta.role && !roles.includes(to.meta.role)) {
    if (roles.includes('admin')) return next('/admin')
    if (roles.includes('student')) return next('/student')
    if (roles.includes('company')) return next('/company')
    return next('/') 
  }
  next()
})

export default router
