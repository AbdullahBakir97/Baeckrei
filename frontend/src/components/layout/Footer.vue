<template>
  <footer class="footer-nav">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Logo and Description -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div class="col-span-1">
          <div class="brand-logo mb-4">
            <span class="text-2xl font-bold logo-text">{{ business.name.charAt(0) }}</span>
            <span class="text-xl font-semibold logo-text">{{ business.name.slice(1) }}</span>
          </div>
          <p class="text-gray-300 text-sm mb-4">
            Your trusted source for quality baked goods and confectionery products.
          </p>
          <address class="not-italic text-gray-300 text-sm mb-4 space-y-1">
            <p class="flex items-center gap-2"><font-awesome-icon icon="store" class="text-amber-500/80" /> {{ business.name }}, {{ storeAddress }}</p>
            <p v-if="business.transit" class="flex items-center gap-2"><font-awesome-icon icon="train-subway" class="text-amber-500/80" /> {{ business.transit }}</p>
          </address>
          <div v-if="socialLinks.length" class="flex space-x-4">
            <a v-for="link in socialLinks" :key="link.icon" :href="link.url" class="nav-link"
               target="_blank" rel="noopener" :aria-label="link.label">
              <font-awesome-icon :icon="['fab', link.icon]" size="lg" />
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
            <li v-for="category in categories" :key="category.slug">
              <router-link :to="{ name: 'category', params: { category: category.slug } }" class="nav-link">
                {{ category.name }}
              </router-link>
            </li>
            <li>
              <router-link :to="{ name: 'seasonal' }" class="nav-link">Seasonal</router-link>
            </li>
          </ul>
        </div>

        <!-- Newsletter -->
        <div class="col-span-1">
          <h3 class="text-gray-200 font-semibold text-lg mb-4">Newsletter</h3>
          <p class="text-gray-300 text-sm mb-4">
            Subscribe to our newsletter for updates and special offers.
          </p>
          <p v-if="newsletterMessage" class="text-sm" :class="newsletterOk ? 'text-green-300' : 'text-red-300'" role="status">
            {{ newsletterMessage }}
          </p>
          <form v-if="!newsletterOk" class="flex" @submit.prevent="subscribeNewsletter">
            <label for="newsletter-email" class="sr-only">Email address</label>
            <input
              id="newsletter-email"
              type="email"
              v-model.trim="email"
              placeholder="Enter your email"
              required
              class="search-input flex-1 min-w-0 rounded-r-none"
            >
            <button
              type="submit"
              :disabled="subscribing"
              class="px-4 py-2 bg-amber-500 text-white rounded-r-lg hover:bg-amber-600
                     transition duration-200 focus:outline-none focus:ring-2 focus:ring-amber-500 disabled:opacity-50"
            >
              Subscribe
            </button>
          </form>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="mt-12 pt-8 border-t border-gray-800">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <p class="text-gray-300 text-sm">
            © {{ new Date().getFullYear() }} {{ business.name }}. All rights reserved.
          </p>
          <nav class="flex flex-wrap justify-center gap-x-6 gap-y-2 mt-4 md:mt-0" aria-label="Legal">
            <router-link to="/impressum" class="nav-link text-sm">Impressum</router-link>
            <router-link to="/privacy" class="nav-link text-sm">Privacy Policy</router-link>
            <router-link to="/terms" class="nav-link text-sm">Terms</router-link>
            <router-link to="/cookie-policy" class="nav-link text-sm">Cookie Policy</router-link>
          </nav>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '@/plugins/axios'
import { useProductStore } from '@/stores/productStore'
import { business, streetLine, cityLine } from '@/config/business'

const email = ref('')
const productStore = useProductStore()
const storeAddress = [streetLine(), cityLine()].filter(Boolean).join(', ')

// Only show social icons that have a real URL in src/config/business.js.
const socialLinks = [
  { icon: 'instagram', label: 'Instagram', url: business.social.instagram },
  { icon: 'facebook', label: 'Facebook', url: business.social.facebook },
  { icon: 'twitter', label: 'Twitter', url: business.social.twitter }
].filter(link => link.url)

const categories = computed(() => productStore.categories.filter(c => c.is_active !== false))

onMounted(() => {
  if (!productStore.categories.length) productStore.fetchCategories()
})

const quickLinks = [
  { name: 'Home', path: '/' },
  { name: 'Products', path: '/products' },
  { name: 'About Us', path: '/about' },
  { name: 'Contact', path: '/contact' },
  { name: 'Blog', path: '/blog' }
]

const subscribing = ref(false)
const newsletterOk = ref(false)
const newsletterMessage = ref('')

const subscribeNewsletter = async () => {
  if (!email.value) return
  subscribing.value = true
  newsletterMessage.value = ''
  try {
    const response = await axios.post('/api/content/newsletter/', { email: email.value })
    newsletterOk.value = true
    newsletterMessage.value = response.data.message
    email.value = ''
  } catch (err) {
    newsletterMessage.value = err.response?.data?.email?.[0] || 'Please try again later.'
  } finally {
    subscribing.value = false
  }
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
  /* Decoration only; it covers the footer and must not block its form. */
  pointer-events: none;
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
  @apply flex items-baseline px-4 py-2 rounded-lg
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
