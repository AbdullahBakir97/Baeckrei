<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">My Profile</h1>
    <div class="max-w-2xl mx-auto">
      <div v-if="!isAuthenticated" class="bg-white rounded-lg shadow p-6">
        <p class="text-center text-gray-600">
          Please log in to view your profile.
        </p>
      </div>
      
      <div v-else class="bg-white rounded-lg shadow p-6 space-y-6">
        <div class="flex items-center justify-between border-b pb-4">
          <div>
            <h2 class="text-xl font-semibold">{{ user?.email }}</h2>
            <p class="text-gray-600">Member since {{ formatDate(user?.date_joined) }}</p>
          </div>
          <span v-if="isAdmin" class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
            Admin
          </span>
        </div>

        <!-- Admin Quick Links -->
        <div v-if="isAdmin" class="space-y-4">
          <h3 class="text-lg font-semibold">Admin Quick Links</h3>
          <div class="grid grid-cols-2 gap-4">
            <router-link 
              :to="{ name: 'admin-dashboard' }"
              class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <HomeIcon class="w-6 h-6 text-gray-600 mr-3" />
              <span>Dashboard</span>
            </router-link>
            
            <router-link 
              :to="{ name: 'admin-products' }"
              class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ShoppingBagIcon class="w-6 h-6 text-gray-600 mr-3" />
              <span>Products</span>
            </router-link>
            
            <router-link 
              :to="{ name: 'admin-orders' }"
              class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ShoppingCartIcon class="w-6 h-6 text-gray-600 mr-3" />
              <span>Orders</span>
            </router-link>
          </div>
        </div>

        <!-- User Actions -->
        <div class="space-y-4">
          <h3 class="text-lg font-semibold">Account Actions</h3>
          <div class="flex space-x-4">
            <button 
              @click="handleLogout" 
              class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              Logout
            </button>
            <button 
              class="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
            >
              Edit Profile
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { 
  HomeIcon, 
  ShoppingBagIcon, 
  ShoppingCartIcon, 
  UsersIcon 
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isAdmin = computed(() => authStore.isAdmin)
const user = computed(() => authStore.user)

const adminLinks = [
  {
    name: 'Dashboard',
    path: '/admin',
    icon: HomeIcon
  },
  {
    name: 'Products',
    path: '/admin/products',
    icon: ShoppingBagIcon
  },
  {
    name: 'Orders',
    path: '/admin/orders',
    icon: ShoppingCartIcon
  },
  {
    name: 'Users',
    path: '/admin/users',
    icon: UsersIcon
  }
]

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const handleLogout = async () => {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>