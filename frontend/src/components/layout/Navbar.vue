<template>
  <nav class="bg-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Logo and Brand -->
        <div class="flex items-center">
          <router-link to="/" class="flex-shrink-0 flex items-center">
            <span class="text-2xl font-bold text-blue-600">B</span>
            <span class="text-xl font-bold text-gray-800">eackrei</span>
          </router-link>
          <!-- Navigation Links -->
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <router-link
              v-for="link in navigationLinks"
              :key="link.path"
              :to="link.path"
              class="nav-link"
              :class="{ 'active': isActive(link.path) }"
            >
              {{ link.name }}
            </router-link>
          </div>
        </div>

        <!-- Right Side Menu -->
        <div class="flex items-center">
          <!-- Search -->
          <div class="relative mx-4">
            <input
              type="text"
              placeholder="Search products..."
              class="w-64 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              v-model="searchQuery"
              @input="handleSearch"
            >
            <span class="absolute right-3 top-2.5 text-gray-400">
              <i class="fas fa-search"></i>
            </span>
          </div>

          <!-- Cart Button -->
          <router-link
            to="/cart"
            class="p-2 text-gray-600 hover:text-blue-600 relative"
          >
            <span class="sr-only">Shopping cart</span>
            <svg
              class="h-6 w-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
            <span
              v-if="cartStore.itemCount > 0"
              class="absolute -top-1 -right-1 bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center"
            >
              {{ cartStore.itemCount }}
            </span>
          </router-link>

          <!-- User Menu -->
          <div class="ml-4 relative flex items-center space-x-4">
            <template v-if="!authStore.isAuthenticated">
              <router-link
                to="/login"
                class="text-sm font-medium text-gray-700 hover:text-blue-600"
              >
                Sign in
              </router-link>
              <router-link
                to="/register"
                class="text-sm font-medium bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Sign up
              </router-link>
            </template>
            <template v-else>
              <!-- Admin Link -->
              <router-link
                v-if="authStore.isAdmin"
                to="/admin"
                class="text-sm font-medium text-gray-700 hover:text-blue-600"
              >
                Admin Dashboard
              </router-link>

              <!-- User Dropdown -->
              <div class="relative">
                <button
                  @click="isUserMenuOpen = !isUserMenuOpen"
                  class="flex items-center space-x-1 text-sm font-medium text-gray-700 hover:text-blue-600 focus:outline-none"
                >
                  <span>{{ authStore.user?.first_name || 'User' }}</span>
                  <svg
                    class="h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </button>

                <!-- Dropdown Menu -->
                <div
                  v-if="isUserMenuOpen"
                  class="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5"
                >
                  <div
                    class="py-1"
                    role="menu"
                    aria-orientation="vertical"
                    aria-labelledby="user-menu"
                  >
                    <router-link
                      to="/profile"
                      class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      role="menuitem"
                      @click="isUserMenuOpen = false"
                    >
                      Your Profile
                    </router-link>
                    <router-link
                      to="/orders"
                      class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      role="menuitem"
                      @click="isUserMenuOpen = false"
                    >
                      Your Orders
                    </router-link>
                    <a
                      href="#"
                      class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      role="menuitem"
                      @click="handleLogout"
                    >
                      Sign out
                    </a>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useCartStore } from '@/stores/cartStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const cartStore = useCartStore()

const isUserMenuOpen = ref(false)
const searchQuery = ref('')

// Navigation links
const navigationLinks = [
  { name: 'Home', path: '/' },
  { name: 'Products', path: '/products' },
  { name: 'About', path: '/about' },
  { name: 'Contact', path: '/contact' }
]

// Check if route is active
const isActive = (path) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

// Handle search input
const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      path: '/products',
      query: { search: searchQuery.value.trim() }
    })
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    isUserMenuOpen.value = false
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
</script>

<style scoped>
.nav-link {
  @apply inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors;
}

.nav-link.active {
  @apply text-blue-600 border-b-2 border-blue-600;
}
</style>
