import { createRouter, createWebHistory } from 'vue-router'
import ProductList from '../components/products/ProductList.vue'
import ProductDetail from '../components/products/ProductDetail.vue'
import About from '../components/pages/About.vue'
import Contact from '../components/pages/Contact.vue'
import Profile from '../components/account/Profile.vue'
import Orders from '../components/account/Orders.vue'
import Settings from '../components/account/Settings.vue'
import Login from '../components/auth/LoginForm.vue'
import { adminRoutes } from '@/router/admin.routers.js'
import { useAuthStore } from '@/stores/authStore'

const routes = [
  {
    path: '/',
    redirect: { name: 'products' }
  },
  {
    path: '/products',
    name: 'products',
    component: ProductList,
    meta: { title: 'Products', requiresAuth: false }
  },
  {
    path: '/products/:id',
    name: 'product-detail',
    component: ProductDetail,
    meta: { title: 'Product Details', requiresAuth: false }
  },
  {
    path: '/categories/:category',
    name: 'category',
    component: ProductList,
    props: true,
    meta: { title: 'Category Products', requiresAuth: false }
  },
  {
    path: '/blog',
    name: 'blog',
    component: () => import('@/components/pages/Blog.vue'),
    meta: { title: 'Blog', requiresAuth: false }
  },
  {
    path: '/breads',
    name: 'breads',
    component: ProductList,
    props: { category: 'breads' },
    meta: { title: 'Breads', requiresAuth: false }
  },
  {
    path: '/pastries',
    name: 'pastries',
    component: ProductList,
    props: { category: 'pastries' },
    meta: { title: 'Pastries', requiresAuth: false }
  },
  {
    path: '/cakes',
    name: 'cakes',
    component: ProductList,
    props: { category: 'cakes' },
    meta: { title: 'Cakes', requiresAuth: false }
  },
  {
    path: '/cookies',
    name: 'cookies',
    component: ProductList,
    props: { category: 'cookies' },
    meta: { title: 'Cookies', requiresAuth: false }
  },
  {
    path: '/seasonal',
    name: 'seasonal',
    component: ProductList,
    props: { category: 'seasonal' },
    meta: { title: 'Seasonal Products', requiresAuth: false }
  },
  {
    path: '/cart',
    name: 'cart',
    component: () => import('@/views/CartView.vue'),
    meta: { requiresAuth: true, title: 'Shopping Cart' }
  },
  {
    path: '/about',
    name: 'about',
    component: About,
    meta: { title: 'About Us', requiresAuth: false }
  },
  {
    path: '/contact',
    name: 'contact',
    component: Contact,
    meta: { title: 'Contact Us', requiresAuth: false }
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile,
    meta: { requiresAuth: true, title: 'Profile' }
  },
  {
    path: '/orders',
    name: 'orders',
    component: Orders,
    meta: { requiresAuth: true, title: 'Orders' }
  },
  {
    path: '/settings',
    component: Settings,
    meta: { requiresAuth: true, title: 'Settings' }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: 'Login' }
  },
  adminRoutes,
  {
    path: '/register',
    name: 'register',
    component: () => import('@/components/auth/RegisterForm.vue'),
    meta: { title: 'Register', requiresAuth: false }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0, behavior: 'smooth' }
  }
})

router.beforeEach(async (to, from, next) => {
  document.body.classList.add('page-loading')
  
  try {
    const authStore = useAuthStore()
    const isAuthenticated = authStore.isAuthenticated
    const isAdmin = authStore.isAdmin

    // First check admin routes
    if (to.meta.requiresAdmin) {
      if (!isAuthenticated) {
        next({ 
          name: 'login', 
          query: { redirect: to.fullPath },
          replace: true 
        })
        return
      }
      
      if (!isAdmin) {
        next({ 
          name: 'products',
          replace: true 
        })
        return
      }
    }

    // Then check general auth routes
    if (to.meta.requiresAuth && !isAuthenticated) {
      next({ 
        name: 'login', 
        query: { redirect: to.fullPath },
        replace: true 
      })
      return
    }

    // Handle authenticated user redirects
    if ((to.name === 'login' || to.name === 'register') && isAuthenticated) {
      next(isAdmin ? { name: 'admin-dashboard' } : { name: 'products' })
      return
    }

    // Update document title
    document.title = to.meta.title ? `${to.meta.title} - Beackrei` : 'Beackrei'
    
    next()
  } catch (error) {
    console.error('Navigation error:', error)
    next({ name: 'products' })
  } finally {
    document.body.classList.remove('page-loading')
  }
})

export default router
