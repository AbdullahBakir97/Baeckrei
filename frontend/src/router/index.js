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
import { business } from '@/config/business'

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
    meta: { title: 'Category', requiresAuth: false }
  },
  {
    path: '/blog',
    name: 'blog',
    component: () => import('@/components/pages/Blog.vue'),
    meta: { title: 'Blog', requiresAuth: false }
  },
  // Old category paths from the footer; the categories now live under /categories/.
  ...['breads', 'pastries', 'cakes', 'cookies'].map(slug => ({
    path: `/${slug}`,
    redirect: { name: 'category', params: { category: slug } }
  })),
  {
    path: '/seasonal',
    name: 'seasonal',
    component: ProductList,
    meta: { title: 'Seasonal Specials', requiresAuth: false, seasonal: true }
  },
  {
    path: '/wishlist',
    name: 'wishlist',
    component: () => import('@/views/WishlistView.vue'),
    meta: { title: 'Wishlist' }
  },
  {
    path: '/compare',
    name: 'compare',
    component: () => import('@/views/CompareView.vue'),
    meta: { title: 'Compare Products' }
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/components/auth/ForgotPassword.vue'),
    meta: { title: 'Forgot Password' }
  },
  {
    path: '/reset-password/:uid/:token',
    name: 'reset-password',
    component: () => import('@/components/auth/ResetPassword.vue'),
    meta: { title: 'Reset Password' }
  },
  {
    path: '/blog/:slug',
    name: 'blog-post',
    component: () => import('@/components/pages/BlogPost.vue'),
    meta: { title: 'Blog' }
  },
  {
    path: '/newsletter/unsubscribe',
    name: 'newsletter-unsubscribe',
    component: () => import('@/components/pages/NewsletterUnsubscribe.vue'),
    meta: { title: 'Newsletter' }
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: () => import('@/components/pages/Privacy.vue'),
    meta: { title: 'Privacy Policy' }
  },
  {
    path: '/terms',
    name: 'terms',
    component: () => import('@/components/pages/Terms.vue'),
    meta: { title: 'Terms and Conditions' }
  },
  {
    path: '/cookie-policy',
    name: 'cookie-policy',
    component: () => import('@/components/pages/CookiePolicy.vue'),
    meta: { title: 'Cookie Policy' }
  },
  {
    path: '/impressum',
    name: 'impressum',
    component: () => import('@/components/pages/Impressum.vue'),
    meta: { title: 'Impressum' }
  },
  {
    path: '/cart',
    name: 'cart',
    component: () => import('@/views/CartView.vue'),
    meta: { requiresAuth: true, title: 'Shopping Cart' }
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: () => import('@/views/CheckoutView.vue'),
    meta: { requiresAuth: true, title: 'Checkout' }
  },
  {
    path: '/orders/:id(\\d+)',
    name: 'order-detail',
    component: () => import('@/views/OrderDetailView.vue'),
    meta: { requiresAuth: true, title: 'Order Details' }
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
    name: 'settings',
    component: Settings,
    meta: { requiresAuth: true, title: 'Settings' }
  },
  {
    path: '/login',
    name: 'login',
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
  // Must stay last: anything that matched no other route.
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/components/pages/NotFound.vue'),
    meta: { title: 'Page not found' }
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
    // Wait for the current user to load so role checks don't run against
    // an empty store (e.g. when an admin opens /admin directly).
    await authStore.initializeAuth()
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
    document.title = to.meta.title ? `${to.meta.title} - ${business.name}` : business.name
    
    next()
  } catch (error) {
    console.error('Navigation error:', error)
    next({ name: 'products' })
  } finally {
    document.body.classList.remove('page-loading')
  }
})

export default router
