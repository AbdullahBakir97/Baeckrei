<template>
  <nav class="nav-container">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <!-- Logo -->
          <div class="flex-shrink-0 flex items-center">
            <router-link to="/" class="brand-logo">
              <span class="text-2xl font-bold bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">B</span>
              <span class="text-xl font-semibold text-gray-200 ml-2">eackrei</span>
            </router-link>
          </div>

          <!-- Navigation Links -->
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <router-link
              v-for="link in navLinks"
              :key="link.to"
              :to="link.to"
              class="nav-link"
              :class="{ 'nav-link-active': $route.path === link.to }"
            >
              {{ link.text }}
            </router-link>
          </div>
        </div>

        <!-- Right side -->
        <div class="flex items-center space-x-4">
          <template v-if="authStore.isAuthenticated">
            <!-- Admin Dashboard Link -->
            <router-link
              v-if="authStore.isAdmin"
              to="/admin/dashboard"
              class="admin-link"
            >
              Admin Dashboard
            </router-link>

            <!-- Profile Dropdown -->
            <div class="relative">
              <button
                @click="showProfileMenu = !showProfileMenu"
                class="profile-button"
              >
                <span class="sr-only">Open user menu</span>
                <div class="profile-avatar">
                  {{ authStore.user?.username.charAt(0).toUpperCase() }}
                </div>
              </button>

              <!-- Profile Dropdown Menu -->
              <div
                v-if="showProfileMenu"
                class="profile-menu"
              >
                <router-link
                  to="/profile"
                  class="menu-item"
                >
                  Your Profile
                </router-link>
                <a
                  href="#"
                  @click.prevent="handleLogout"
                  class="menu-item"
                >
                  Sign out
                </a>
              </div>
            </div>
          </template>

          <template v-else>
            <router-link
              to="/login"
              class="auth-link"
            >
              Sign in
            </router-link>
            <router-link
              to="/register"
              class="signup-button"
            >
              Sign up
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()
const showProfileMenu = ref(false)

const navLinks = [
  { to: '/products', text: 'Products' },
  { to: '/cart', text: 'Cart' }
]

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
</script>

<style scoped>
.nav-container {
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
}

.brand-logo {
  @apply flex items-center px-3 py-2 rounded-lg transition-all duration-300;
  background: linear-gradient(
    135deg,
    rgba(245, 158, 11, 0.1),
    transparent
  );
}

.brand-logo:hover {
  background: linear-gradient(
    135deg,
    rgba(245, 158, 11, 0.2),
    transparent
  );
  box-shadow: 
    0 0 20px rgba(245, 158, 11, 0.1),
    0 0 40px rgba(245, 158, 11, 0.05);
}

.nav-link {
  @apply inline-flex items-center px-3 py-2 text-sm font-medium text-gray-300 
         border-b-2 border-transparent transition-all duration-300;
}

.nav-link:hover {
  @apply text-gray-100;
  border-color: rgba(245, 158, 11, 0.5);
  background: linear-gradient(
    to bottom,
    rgba(245, 158, 11, 0.1),
    transparent
  );
}

.nav-link-active {
  @apply text-amber-400 border-amber-500;
  background: linear-gradient(
    to bottom,
    rgba(245, 158, 11, 0.15),
    transparent
  );
}

.admin-link {
  @apply px-3 py-2 text-sm font-medium rounded-lg transition-all duration-300
         text-gray-300 hover:text-amber-400;
  background: linear-gradient(
    to right,
    rgba(245, 158, 11, 0.1),
    transparent
  );
}

.profile-button {
  @apply rounded-lg p-1 transition-all duration-300 
         focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 focus:ring-offset-gray-800;
}

.profile-avatar {
  @apply h-8 w-8 rounded-lg flex items-center justify-center text-white font-medium;
  background: linear-gradient(135deg, #F59E0B, #D97706);
}

.profile-menu {
  @apply absolute right-0 mt-2 w-48 rounded-lg shadow-lg py-1 z-50
         backdrop-blur-md bg-opacity-95;
  background: rgba(23, 23, 23, 0.95);
  border: 1px solid rgba(245, 158, 11, 0.2);
  transform-origin: top right;
  animation: menuFade 0.2s ease-out;
}

.menu-item {
  @apply block px-4 py-2 text-sm text-gray-300 hover:text-white transition-all duration-200;
}

.menu-item:hover {
  background: linear-gradient(
    90deg,
    rgba(245, 158, 11, 0.2),
    transparent
  );
}

.auth-link {
  @apply px-3 py-2 text-sm font-medium rounded-lg text-gray-300 
         hover:text-amber-400 transition-all duration-300;
}

.signup-button {
  @apply px-4 py-2 text-sm font-medium rounded-lg text-white 
         transition-all duration-300 transform hover:scale-105;
  background: linear-gradient(135deg, #F59E0B, #D97706);
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
}

.signup-button:hover {
  background: linear-gradient(135deg, #FBBF24, #F59E0B);
  box-shadow: 0 0 30px rgba(245, 158, 11, 0.3);
}

@keyframes menuFade {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
