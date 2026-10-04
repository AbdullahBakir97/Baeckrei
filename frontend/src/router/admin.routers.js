const ProductManagement = () => import('@/components/admin/products/ProductManagement.vue')
const AdminLayout = () => import('@/components/admin/AdminLayout.vue')

// Studio pages: journal, inbox, newsletter, ingredients, settings, menu screens.
const STUDIO = {
  JournalList: () => import('@/components/admin/studio/JournalList.vue'),
  JournalEditor: () => import('@/components/admin/studio/JournalEditor.vue'),
  MessagesInbox: () => import('@/components/admin/studio/MessagesInbox.vue'),
  NewsletterManager: () => import('@/components/admin/studio/NewsletterManager.vue'),
  IngredientManager: () => import('@/components/admin/studio/IngredientManager.vue'),
  ShopSettings: () => import('@/components/admin/studio/ShopSettings.vue'),
  ScreenList: () => import('@/components/admin/studio/ScreenList.vue'),
  ScreenEditor: () => import('@/components/admin/studio/ScreenEditor.vue')
}

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
          title: 'Dashboard',
          requiresAuth: true,
          requiresAdmin: true 
        }
      },
      {
        path: 'products',
        name: 'admin-products',
        component: ProductManagement,
        meta: { 
          title: 'Products',
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
        path: 'categories',
        name: 'admin-categories',
        component: () => import('@/components/admin/categories/CategoryManagement.vue'),
        meta: {
          title: 'Categories',
          requiresAuth: true,
          requiresAdmin: true
        }
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/components/admin/users/UserManagement.vue'),
        meta: {
          title: 'Users',
          requiresAuth: true,
          requiresAdmin: true
        }
      },
      ...[
        ['journal', 'admin-journal', 'JournalList'],
        ['journal/new', 'admin-journal-new', 'JournalEditor'],
        ['journal/:id', 'admin-journal-edit', 'JournalEditor'],
        ['messages', 'admin-messages', 'MessagesInbox'],
        ['newsletter', 'admin-newsletter', 'NewsletterManager'],
        ['ingredients', 'admin-ingredients', 'IngredientManager'],
        ['settings', 'admin-settings', 'ShopSettings'],
        ['screens', 'admin-screens', 'ScreenList'],
        ['screens/:id', 'admin-screen-edit', 'ScreenEditor']
      ].map(([path, name, component]) => ({
        path,
        name,
        component: STUDIO[component],
        meta: { requiresAuth: true, requiresAdmin: true }
      })),
      {
        path: 'orders',
        name: 'admin-orders',  // Fixed naming convention
        component: () => import('@/components/admin/orders/OrderManagement.vue'),
        meta: { 
          title: 'Orders',
          requiresAuth: true,
          requiresAdmin: true 
        }
      }
    ]
  }