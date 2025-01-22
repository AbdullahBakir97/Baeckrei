import ProductManagement from '@/components/admin/products/ProductManagement.vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'

export const adminRoutes = {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',  // This makes it the default admin route
        name: 'admin-dashboard',
        component: () => import('@/components/admin/dashboard/AdminDashboard.vue'),
        meta: { 
          title: 'Admin Dashboard',
          requiresAuth: true,
          requiresAdmin: true 
        }
      },
      {
        path: 'products',
        name: 'admin-products',
        component: ProductManagement,
        meta: { 
          title: 'Product Management',
          requiresAuth: true,
          requiresAdmin: true 
        }
      },
      {
        path: 'products/:id',
        name: 'admin-product-detail',
        component: () => import('@/components/admin/products/ProductDetail.vue'),
        meta: { 
          title: 'Product Detail',
          requiresAuth: true,
          requiresAdmin: true 
        }
      },
      {
        path: 'orders',
        name: 'admin-orders',  // Fixed naming convention
        component: () => import('@/components/admin/orders/OrderManagement.vue'),
        meta: { 
          title: 'Order Management',
          requiresAuth: true,
          requiresAdmin: true 
        }
      }
    ]
  }