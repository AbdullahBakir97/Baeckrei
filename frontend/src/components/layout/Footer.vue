<template>
  <footer class="bg-gray-800 text-white">
    <!-- Main Footer -->
    <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- Company Info -->
        <div class="space-y-4">
          <h3 class="text-lg font-semibold">Beackrei</h3>
          <p class="text-gray-400 text-sm">
            Your trusted source for quality baked goods and confectionery products.
          </p>
          <div class="flex space-x-4">
            <a href="#" class="text-gray-400 hover:text-white">
              <i class="fab fa-facebook"></i>
            </a>
            <a href="#" class="text-gray-400 hover:text-white">
              <i class="fab fa-twitter"></i>
            </a>
            <a href="#" class="text-gray-400 hover:text-white">
              <i class="fab fa-instagram"></i>
            </a>
            <a href="#" class="text-gray-400 hover:text-white">
              <i class="fab fa-linkedin"></i>
            </a>
          </div>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="text-lg font-semibold mb-4">Quick Links</h3>
          <ul class="space-y-2">
            <li v-for="link in quickLinks" :key="link.path">
              <router-link
                :to="link.path"
                class="text-gray-400 hover:text-white transition-colors"
              >
                {{ link.name }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Categories -->
        <div>
          <h3 class="text-lg font-semibold mb-4">Categories</h3>
          <ul class="space-y-2">
            <li v-for="category in categories" :key="category.path">
              <router-link
                :to="category.path"
                class="text-gray-400 hover:text-white transition-colors"
              >
                {{ category.name }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Newsletter -->
        <div>
          <h3 class="text-lg font-semibold mb-4">Newsletter</h3>
          <p class="text-gray-400 text-sm mb-4">
            Subscribe to our newsletter for updates and special offers.
          </p>
          <form @submit.prevent="handleSubscribe" class="space-y-2">
            <input
              type="email"
              v-model="email"
              placeholder="Enter your email"
              class="w-full px-4 py-2 rounded bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              type="submit"
              class="w-full px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
            >
              Subscribe
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Bottom Footer -->
    <div class="border-t border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <!-- Copyright -->
          <div class="text-gray-400 text-sm">
            © {{ currentYear }} Beackrei. All rights reserved.
          </div>

          <!-- Legal Links -->
          <div class="flex space-x-6">
            <router-link
              v-for="link in legalLinks"
              :key="link.path"
              :to="link.path"
              class="text-gray-400 hover:text-white text-sm transition-colors"
            >
              {{ link.name }}
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, computed } from 'vue'

// State
const email = ref('')

// Computed
const currentYear = computed(() => new Date().getFullYear())

// Links Data
const quickLinks = [
  { name: 'Home', path: '/' },
  { name: 'Products', path: '/products' },
  { name: 'About Us', path: '/about' },
  { name: 'Contact', path: '/contact' },
  { name: 'Blog', path: '/blog' }
]

const categories = [
  { name: 'Breads', path: '/categories/breads' },
  { name: 'Pastries', path: '/categories/pastries' },
  { name: 'Cakes', path: '/categories/cakes' },
  { name: 'Cookies', path: '/categories/cookies' },
  { name: 'Seasonal', path: '/categories/seasonal' }
]

const legalLinks = [
  { name: 'Privacy Policy', path: '/privacy' },
  { name: 'Terms of Service', path: '/terms' },
  { name: 'Cookie Policy', path: '/cookies' }
]

// Methods
const handleSubscribe = () => {
  if (!email.value) return
  
  // TODO: Implement newsletter subscription
  console.log('Subscribe:', email.value)
  email.value = ''
}
</script>

<style scoped>
/* Add any custom styles here */
.fab {
  @apply text-xl;
}

/* Transitions */
.transition-colors {
  transition: all 0.2s ease-in-out;
}
</style>
