import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path:'/',
      name:'home',
      component: ()=> import('@/views/HomeView.vue')
    },
    {
      path:'/login',
      name:'login',
      component: ()=> import('@/views/LoginView.vue')
    },
    {
      path:'/register-company',
      name:'register-company',
      component: ()=> import('@/views/CompanyRegisterView.vue')
    },
    {
      path:'/register-student',
      name:'register-student',
      component: ()=> import('@/views/StudentRegisterView.vue')
    },
    {
      path: '/admin',
      component: () => import('@/views/admin/DashboardView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/companies',
      component: () => import('@/views/admin/CompaniesView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/students',
      component: () => import('@/views/admin/StudentsView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/placement-drives',
      component: () => import('@/views/admin/DrivesView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/applications',
      component: () => import('@/views/admin/ApplicationsView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/company',
      component: () => import('@/views/company/DashboardView.vue'),
      meta: { requiresAuth: true, role: 'company' }
    },
    {
    path: '/company/placement-drives',
    component: () => import('@/views/company/DrivesView.vue'),
    meta: {
      requiresAuth: true,
      role: 'company'
    }
    },
    {
      path: '/company/placement-drives/new',
      component: () => import('@/views/company/CreateDriveView.vue'),
      meta: {
        requiresAuth: true,
        role: 'company'
      }
    },
    {
      path: '/company/placement-drives/:id',
      component: () => import('@/views/company/DriveDetailsView.vue'),
      meta: {
        requiresAuth: true,
        role: 'company'
      }
    },
    {
      path: '/company/offers/new/:application_id',
      component: () => import('@/views/company/OfferFormView.vue'),
      meta: {
        requiresAuth: true,
        role: 'company'
      }
    },
    {
      path: '/company/offers/:offer_id',
      component: () => import('@/views/company/OfferDetailsView.vue'),
      meta: {
        requiresAuth: true,
        role: 'company'
      }
    },
    {
      path: '/student',
      component: () => import('@/views/student/DashboardView.vue'),
      meta: { requiresAuth: true, role: 'student' }
    },
    {
      path: '/student/profile',
      component: () => import('@/views/student/ProfileView.vue'),
      meta: { requiresAuth: true, role: 'student' }
    },
    {
      path: '/student/placement-drives',
      component: () => import('@/views/student/JobsView.vue'),
      meta: { requiresAuth: true, role: 'student' }
    },
    {
      path: '/student/applications/:id',
      component: () => import('@/views/student/ApplicationDetailsView.vue'),
      meta: { requiresAuth: true, role: 'student' }
    },
    {
      path: '/student/placement-drives/:id',
      component: () => import('@/views/student/ApplyView.vue'),
      meta: { requiresAuth: true, role: 'student' }
    },
    
  ],
})

router.beforeEach((to,from) => {
  const auth = useAuthStore()

  const isAuthenticated = auth.isAuthenticated
  const roles = auth.userRoles

  if (to.meta.requiresAuth && !isAuthenticated) {
    return '/login'
  }

  if (to.meta.role && !roles.includes(to.meta.role)) {
    let redirectPath = '/'

    // Determine the correct home base for their role
    if (roles.includes('admin')) redirectPath = '/admin'
    else if (roles.includes('student')) redirectPath = '/student'
    else if (roles.includes('company')) redirectPath = '/company'

    // Only redirect if they are not already trying to go to that exact path
    if (to.path !== redirectPath) {
      return redirectPath
    }
  }
})

export default router
