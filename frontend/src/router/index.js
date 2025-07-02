import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/login'
      },
      {
        path: 'login',
        name: 'login',
        component: () => import('@/pages/Login.vue')
      },
      {
        path: 'registro',
        name: 'registro',
        component: () => import('@/pages/Registro.vue')
      }
    ]
  },
  {
    path: '/dashboard',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/pages/Dashboard.vue')
      },
      {
        path: '/lancamentos',
        name: 'lancamentos',
        component: () => import('@/pages/Lancamentos.vue')
      },
      {
        path: '/categorias',
        name: 'categorias',
        component: () => import('@/pages/Categorias.vue')
      },
      {
        path: '/metas',
        name: 'metas',
        component: () => import('@/pages/Metas.vue')
      },
      {
        path: '/contas',
        name: 'contas',
        component: () => import('@/pages/Contas.vue')
      },
      {
        path: '/profile',
        name: 'profile',
        component: () => import('@/pages/Profile.vue')
      },
      // Páginas Administrativas
      {
        path: '/admin/chatbot',
        name: 'chatbot-admin',
        component: () => import('@/pages/admin/ChatbotAdmin.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/admin/importar-dados',
        name: 'importar-dados',
        component: () => import('@/pages/admin/ImportarDados.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/admin/backup',
        name: 'backup',
        component: () => import('@/pages/admin/Backup.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/admin/api-docs',
        name: 'api-docs',
        component: () => import('@/pages/admin/ApiDocs.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/admin/logs',
        name: 'logs-sistema',
        component: () => import('@/pages/admin/LogsSistema.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      }
    ]
  },
  {
    path: '/:catchAll(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Proteção de rotas com inicialização da store
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Aguardar inicialização da store se necessário
  if (!authStore.user && localStorage.getItem('token')) {
    await authStore.initAuth()
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (requiresAdmin && (!authStore.user || !authStore.user.is_superuser)) {
    next('/dashboard')
  } else if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/registro')) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
