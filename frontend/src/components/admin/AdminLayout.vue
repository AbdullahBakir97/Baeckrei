<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Sidebar -->
    <div class="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="flex items-center justify-center h-16 bg-indigo-600">
          <router-link to="/" class="text-xl font-bold text-white">
            Beackrei Admin
          </router-link>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 px-2 py-4 space-y-1">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center px-4 py-2 text-sm font-medium rounded-md"
            :class="[
              $route.path.startsWith(item.path)
                ? 'bg-indigo-100 text-indigo-700'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            ]"
          >
            <component
              :is="item.icon"
              class="mr-3 h-5 w-5"
              :class="[
                $route.path.startsWith(item.path)
                  ? 'text-indigo-500'
                  : 'text-gray-400'
              ]"
            />
            {{ item.name }}
          </router-link>
        </nav>
      </div>
    </div>

    <!-- Main Content -->
    <div class="pl-64">
      <!-- Top Bar -->
      <div class="bg-white shadow-sm">
        <div class="flex justify-between items-center px-8 h-16">
          <h1 class="text-2xl font-semibold text-gray-900">
            {{ currentPageTitle }}
          </h1>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-500">
              Welcome, {{ authStore.user?.first_name || 'Admin' }}
            </span>
            <button
              @click="handleLogout"
              class="text-sm text-gray-600 hover:text-indigo-600"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>

      <!-- Page Content -->
      <main class="p-8">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()
const { isAdmin } = storeToRefs(authStore)

const navItems = [
  {
    name: 'Dashboard',
    path: '/admin',
    icon: 'HomeIcon',
  },
  {
    name: 'Products',
    path: '/admin/products',
    icon: 'ShoppingBagIcon',
  },
  {
    name: 'Categories',
    path: '/admin/categories',
    icon: 'FolderIcon',
  },
  {
    name: 'Orders',
    path: '/admin/orders',
    icon: 'ShoppingCartIcon',
  },
  {
    name: 'Users',
    path: '/admin/users',
    icon: 'UsersIcon',
  },
]

onMounted(() => {
  if (!isAdmin.value) {
    router.push({ name: 'products' })
  }
})

const currentPageTitle = computed(() => {
  const currentPath = router.currentRoute.value.path
  const currentItem = navItems.find(item => currentPath.startsWith(item.path))
  return currentItem?.name || 'Dashboard'
})

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
</script>
