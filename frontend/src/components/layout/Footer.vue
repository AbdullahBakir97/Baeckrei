<template>
  <footer class="footer-nav">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Logo and Description -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div class="col-span-1">
          <div class="brand-logo mb-4">
            <span class="text-2xl font-bold logo-text">B</span>
            <span class="text-xl font-semibold logo-text ml-2">eackrei</span>
          </div>
          <p class="text-gray-300 text-sm mb-4">
            Your trusted source for quality baked goods and confectionery products.
          </p>
          <div class="flex space-x-4">
            <a href="#" class="nav-link">
              <font-awesome-icon :icon="['fab', 'facebook']" size="lg" />
            </a>
            <a href="#" class="nav-link">
              <font-awesome-icon :icon="['fab', 'twitter']" size="lg" />
            </a>
            <a href="#" class="nav-link">
              <font-awesome-icon :icon="['fab', 'instagram']" size="lg" />
            </a>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="col-span-1">
          <h3 class="text-gray-200 font-semibold text-lg mb-4">Quick Links</h3>
          <ul class="space-y-2">
            <li v-for="link in quickLinks" :key="link.path">
              <router-link :to="link.path" class="nav-link">
                {{ link.name }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Categories -->
        <div class="col-span-1">
          <h3 class="text-gray-200 font-semibold text-lg mb-4">Categories</h3>
          <ul class="space-y-2">
            <li v-for="category in categories" :key="category.path">
              <router-link :to="category.path" class="nav-link">
                {{ category.name }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Newsletter -->
        <div class="col-span-1">
          <h3 class="text-gray-200 font-semibold text-lg mb-4">Newsletter</h3>
          <p class="text-gray-300 text-sm mb-4">
            Subscribe to our newsletter for updates and special offers.
          </p>
          <div class="flex">
            <input 
              type="email" 
              v-model="email" 
              placeholder="Enter your email" 
              class="search-input flex-1 rounded-r-none"
            >
            <button 
              @click="subscribeNewsletter"
              class="px-4 py-2 bg-amber-500 text-white rounded-r-lg hover:bg-amber-600 
                     transition duration-200 focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              Subscribe
            </button>
          </div>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="mt-12 pt-8 border-t border-gray-800">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <p class="text-gray-300 text-sm">
            {{ new Date().getFullYear() }} Beackrei. All rights reserved.
          </p>
          <div class="flex space-x-6 mt-4 md:mt-0">
            <a href="#" class="nav-link text-sm">Privacy Policy</a>
            <a href="#" class="nav-link text-sm">Terms of Service</a>
            <a href="#" class="nav-link text-sm">Cookie Policy</a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref } from 'vue'

const email = ref('')

const quickLinks = [
  { name: 'Home', path: '/' },
  { name: 'Products', path: '/products' },
  { name: 'About Us', path: '/about' },
  { name: 'Contact', path: '/contact' },
  { name: 'Blog', path: '/blog' }
]

const categories = [
  { name: 'Breads', path: '/breads' },
  { name: 'Pastries', path: '/pastries' },
  { name: 'Cakes', path: '/cakes' },
  { name: 'Cookies', path: '/cookies' },
  { name: 'Seasonal', path: '/seasonal' }
]

const subscribeNewsletter = () => {
  console.log('Subscribing email:', email.value)
  email.value = ''
}
</script>

<style scoped>
.footer-nav {
  @apply relative;
  background: linear-gradient(
    to bottom,
    rgba(17, 17, 17, 0.95) 0%,
    rgba(17, 17, 17, 0.85) 100%
  );
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(245, 158, 11, 0.1);
  box-shadow: 
    0 -4px 6px -1px rgba(0, 0, 0, 0.1),
    0 -2px 4px -1px rgba(0, 0, 0, 0.06),
    0 0 20px rgba(245, 158, 11, 0.1);
  transform-style: preserve-3d;
  perspective: 1000px;
}

.footer-nav::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at bottom center,
    rgba(245, 158, 11, 0.15),
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.footer-nav:hover::before {
  opacity: 1;
}

.nav-link {
  @apply relative inline-flex items-center text-gray-300 transition-all duration-300;
  transform-style: preserve-3d;
}

.nav-link:hover {
  @apply text-white;
  transform: translateZ(10px);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(245, 158, 11, 0.8),
    transparent
  );
  transition: all 0.3s ease;
  transform: translateX(-50%);
}

.nav-link:hover::after {
  width: 100%;
}

.brand-logo {
  @apply flex items-center space-x-2 px-4 py-2 rounded-lg
         transition-all duration-300 w-fit;
  background: linear-gradient(
    135deg,
    rgba(245, 158, 11, 0.1),
    transparent
  );
  transform-style: preserve-3d;
}

.brand-logo:hover {
  transform: translateZ(10px);
  background: linear-gradient(
    135deg,
    rgba(245, 158, 11, 0.2),
    transparent
  );
  box-shadow: 
    0 0 20px rgba(245, 158, 11, 0.1),
    0 0 40px rgba(245, 158, 11, 0.05);
}

.logo-text {
  @apply font-bold text-transparent bg-clip-text;
  background-image: linear-gradient(
    135deg,
    #FCD34D,
    #F59E0B
  );
}

.search-input {
  @apply relative px-4 py-2 text-gray-100 
         transition-all duration-300;
  background: rgba(23, 23, 23, 0.7);
  border: 1px solid rgba(245, 158, 11, 0.2);
  backdrop-filter: blur(4px);
  transform-style: preserve-3d;
}

.search-input:focus {
  @apply outline-none;
  background: rgba(23, 23, 23, 0.9);
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 
    0 0 0 2px rgba(245, 158, 11, 0.1),
    0 0 20px rgba(245, 158, 11, 0.2);
  transform: translateZ(5px);
}
</style>
