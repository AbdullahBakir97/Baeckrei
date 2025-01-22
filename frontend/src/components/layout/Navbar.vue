<template>
  <nav class="bg-gray-900 shadow-lg border-b border-gray-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Logo and Brand -->
        <div class="flex items-center">
          <router-link to="/" class="flex-shrink-0 flex items-center brand-logo">
            <span class="text-2xl font-bold text-amber-400 logo-text">B</span>
            <span class="text-xl font-semibold text-gray-200 ml-2 logo-text">eackrei</span>
          </router-link>
          
          <!-- Navigation Links -->
          <div class="hidden md:flex ml-10 space-x-8">
            <router-link 
              v-for="link in navigationLinks" 
              :key="link.path" 
              :to="link.path"
              :class="[
                isActive(link.path) 
                  ? 'text-amber-400 border-amber-400' 
                  : 'text-gray-300 hover:text-gray-100 border-transparent',
                'px-3 py-2 text-sm font-medium border-b-2 nav-link'
              ]"
            >
              {{ link.name }}
            </router-link>
          </div>
        </div>

        <!-- Search and Cart -->
        <div class="flex items-center">
          <!-- Search -->
          <div class="relative mx-4">
            <input
              type="text"
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              placeholder="Search products..."
              class="w-64 px-4 py-2 rounded-lg bg-gray-800 text-gray-100 border border-gray-700 
                     focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent
                     placeholder-gray-400 search-input"
            />
            <button 
              @click="handleSearch"
              class="absolute right-0 top-0 mt-2 mr-3 text-gray-400 hover:text-gray-200 search-button"
            >
              <font-awesome-icon icon="fa-solid fa-search" />
            </button>
          </div>

          <!-- Cart -->
          <div 
            class="relative"
            @click="navigateToCart"
            @mouseenter="showCartDropdown = true"
            @mouseleave="showCartDropdown = false"
          >
            <div class="p-2 text-gray-400 hover:text-gray-200 flex items-center gap-2 cursor-pointer cart-icon">
              <div class="relative">
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
                  v-if="cartItemCount > 0"
                  class="absolute -top-1 -right-1 bg-amber-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center cart-count"
                >
                  {{ cartItemCount }}
                </span>
              </div>
              <span class="font-medium">{{ formatPrice(cartTotal) }} €</span>
            </div>

            <!-- Cart Dropdown -->
            <div v-show="showCartDropdown" class="absolute right-0 mt-2 w-80 bg-gray-800 rounded-lg shadow-xl z-50 glass-dropdown">
              <CartDropdown />
            </div>
          </div>

          <!-- User Menu -->
          <div class="ml-4 relative flex items-center space-x-4">
            <template v-if="!authStore.isAuthenticated">
              <router-link
                to="/login"
                class="text-sm font-medium text-gray-300 hover:text-gray-100"
              >
                Sign in
              </router-link>
              <router-link
                to="/register"
                class="text-sm font-medium text-gray-300 hover:text-gray-100"
              >
                Sign up
              </router-link>
            </template>
            <template v-else>
              <!-- Admin Link -->
              <router-link
                v-if="authStore.isAdmin"
                to="/admin"
                class="text-sm font-medium text-gray-300 hover:text-gray-100"
              >
                Admin Dashboard
              </router-link>

              <!-- User Dropdown -->
              <div class="relative">
                <button
                  @click="isUserMenuOpen = !isUserMenuOpen"
                  class="flex items-center space-x-1 text-sm font-medium text-gray-300 hover:text-gray-100 focus:outline-none user-menu-button"
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
                  class="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-gray-800 ring-1 ring-black ring-opacity-5 dropdown-menu"
                >
                  <div
                    class="py-1"
                    role="menu"
                    aria-orientation="vertical"
                    aria-labelledby="user-menu"
                  >
                    <router-link
                      to="/profile"
                      class="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 dropdown-item"
                      role="menuitem"
                      @click="isUserMenuOpen = false"
                    >
                      Your Profile
                    </router-link>
                    <router-link
                      to="/orders"
                      class="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 dropdown-item"
                      role="menuitem"
                      @click="isUserMenuOpen = false"
                    >
                      Your Orders
                    </router-link>
                    <a
                      href="#"
                      class="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 dropdown-item"
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
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCartStore } from '@/stores/cartStore'
import { useAuthStore } from '@/stores/authStore'
import { storeToRefs } from 'pinia'
import CartDropdown from '@/components/cart/CartDropdown.vue';

const router = useRouter()
const route = useRoute()
const cartStore = useCartStore()
const authStore = useAuthStore()
const { items } = storeToRefs(cartStore)

const showCartDropdown = ref(false)
const searchQuery = ref('')
const isUserMenuOpen = ref(false)

const displayedItems = computed(() => {
  return items.value?.slice(0, 3) || []
})

const cartItemCount = computed(() => {
  return items.value?.reduce((total, item) => total + item.quantity, 0) || 0
})

const cartTotal = computed(() => {
  return items.value?.reduce((total, item) => total + Number(item.total_price), 0) || 0
})

const formatPrice = (price) => {
  return Number(price || 0).toFixed(2)
}

// Navigation functions
const navigateToCart = () => {
  showCartDropdown.value = false
  router.push('/cart')
}

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

// Fetch cart data on component mount
onMounted(() => {
  cartStore.fetchCart()
})
</script>

<style scoped>
nav {
  @apply relative;
  background: linear-gradient(
    to bottom,
    rgba(17, 17, 17, 0.95) 0%,
    rgba(17, 17, 17, 0.85) 100%
  );
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(245, 158, 11, 0.1);
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06),
    0 0 20px rgba(245, 158, 11, 0.1);
  transform-style: preserve-3d;
  perspective: 1000px;
}

nav::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at top center,
    rgba(255, 215, 0, 0.15),
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

nav:hover::before {
  opacity: 1;
}

.router-link-active {
  @apply relative;
  transform-style: preserve-3d;
}

.router-link-active::before {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 215, 0, 0.8),
    transparent
  );
  transform: translateZ(20px);
  box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
}

.nav-link {
  @apply relative inline-flex items-center px-3 py-2 text-sm font-medium 
         transition-all duration-300;
  transform-style: preserve-3d;
}

.nav-link span {
  @apply text-gray-300 transition-all duration-300;
}

.nav-link:hover span,
.router-link-active span {
  @apply text-transparent bg-clip-text;
  background-image: linear-gradient(135deg, #FFD700, #FDB931, #B8860B);
}

.nav-link::after {
  content: '';
  @apply absolute bottom-0 left-1/2 w-0 h-0.5 transition-all duration-300 transform -translate-x-1/2;
  background: linear-gradient(90deg, #FFD700, #FDB931, #B8860B);
}

.nav-link:hover::after,
.router-link-active::after {
  @apply w-full;
}

.navbar {
  @apply flex items-center justify-between p-4 bg-gray-800 text-white;
}

.brand-logo .logo-text {
  @apply font-bold text-transparent bg-clip-text;
  background-image: linear-gradient(135deg, #FFD700, #FDB931, #B8860B);
}

.search-input:focus {
  @apply outline-none;
  background: rgba(23, 23, 23, 0.9);
  border-color: #FFD700;
  box-shadow: 
    0 0 0 2px rgba(255, 215, 0, 0.1),
    0 0 20px rgba(255, 215, 0, 0.2);
}

.dropdown-item {
  @apply block w-full px-4 py-2 text-sm text-gray-300 transition-all duration-200;
}

.dropdown-item:hover {
  @apply text-transparent bg-clip-text;
  background-image: linear-gradient(135deg, #FFD700, #FDB931, #B8860B);
  background-color: rgba(255, 215, 0, 0.1);
}

.cart-icon:hover {
  @apply text-transparent;
  background-image: linear-gradient(135deg, #FFD700, #FDB931, #B8860B);
  -webkit-background-clip: text;
}

.cart-count {
  background: linear-gradient(135deg, #FFD700, #FDB931, #B8860B);
  border: 2px solid rgba(17, 17, 17, 0.95);
  box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
}

.cart-icon .cart-count {
  @apply absolute -top-1 -right-1 bg-amber-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center;
}

.dropdown-menu {
  @apply absolute right-0 mt-2 w-80 bg-gray-800 rounded-lg shadow-xl z-50 glass-dropdown;
}

.user-menu-button:hover {
  @apply text-transparent;
  background-image: linear-gradient(135deg, #FFD700, #FDB931, #B8860B);
  -webkit-background-clip: text;
}

.search-button {
  @apply text-transparent;
  background-image: linear-gradient(135deg, #FFD700, #FDB931, #B8860B);
  -webkit-background-clip: text;
}

.search-button:hover {
  filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.5));
}

nav::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at top center,
    rgba(255, 215, 0, 0.15),
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

nav:hover::before {
  opacity: 1;
}
</style>
