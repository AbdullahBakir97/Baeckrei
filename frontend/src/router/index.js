import { createRouter, createWebHistory } from 'vue-router'
import ProductList from '../components/products/ProductList.vue'
import ProductDetail from '../components/products/ProductDetail.vue'
import Cart from '../components/cart/Cart.vue'
import About from '../components/pages/About.vue'
import Contact from '../components/pages/Contact.vue'
import Profile from '../components/account/Profile.vue'
import Orders from '../components/account/Orders.vue'
import Settings from '../components/account/Settings.vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import ProductManagement from '@/components/admin/products/ProductManagement.vue'
import AdminDashboard from '@/components/admin/dashboard/AdminDashboard.vue'
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
    meta: { title: 'Products' }
  },
  {
    path: '/products/:id',
    name: 'product-detail',
    component: ProductDetail,
    meta: { title: 'Product Details' }
  },
  {
    path: '/categories/:category',
    name: 'category',
    component: ProductList,
    props: true,
    meta: { title: 'Category Products' }
  },
  {
    path: '/cart',
    name: 'cart',
    component: Cart,
    meta: { requiresAuth: true, title: 'Shopping Cart' }
  },
  {
    path: '/about',
    name: 'about',
    component: About,
    meta: { title: 'About Us' }
  },
  {
    path: '/contact',
    name: 'contact',
    component: Contact,
    meta: { title: 'Contact Us' }
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
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'admin-dashboard',
        component: AdminDashboard,
        meta: { title: 'Admin Dashboard' }
      },
      {
        path: 'products',
        name: 'product-management',
        component: ProductManagement,
        meta: { title: 'Product Management' }
      },
      {
        path: 'products/:id',
        name: 'admin-product-detail',
        component: () => import('@/components/admin/products/ProductDetail.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'orders',
        name: 'order-management',
        component: () => import('@/components/admin/orders/OrderManagement.vue'),
        meta: { title: 'Order Management' }
      }
    ]
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/components/auth/LoginForm.vue'),
    meta: { title: 'Login' }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/components/auth/RegisterForm.vue'),
    meta: { title: 'Register' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth state if not already done
  if (!authStore.initialized) {
    await authStore.initializeAuth()
  }
  
  // If logged in as admin and accessing login page, redirect to admin dashboard
  if (authStore.isAuthenticated && authStore.isAdmin && to.name === 'login') {
    next({ name: 'admin-dashboard' })
    return
  }

  // Check authentication requirements
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // Check admin requirements
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'products' })
    return
  }

  // Update document title
  document.title = to.meta.title ? `${to.meta.title} - Beackrei` : 'Beackrei'
  
  next()
})

export default router
