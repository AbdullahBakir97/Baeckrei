import { createApp, watch } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import { useAuthStore } from './stores/authStore'
import { useCartStore } from './stores/cartStore'
import axios from './plugins/axios'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import './plugins/fontawesome'
import VueGlow from '@aksharahegde/vue-glow'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(VueGlow)

// Register global components
app.component('font-awesome-icon', FontAwesomeIcon)

// Initialize auth state before mounting the app
const authStore = useAuthStore()
await authStore.initializeAuth()

// Initialize cart state after auth
const cartStore = useCartStore()
if (authStore.isAuthenticated) {
  await cartStore.fetchCart()
}

// Restore auth token if it exists
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// Watch for auth state changes and refresh cart accordingly

watch(
  () => authStore.isAuthenticated,
  async (isAuthenticated) => {
    if (isAuthenticated) {
      // User just logged in, refresh cart
      await cartStore.fetchCart()
    } else {
      // User logged out, clear cart
      cartStore.items = []
      cartStore.subtotal = '0.00'
      cartStore.tax = '0.00'
      cartStore.total = '0.00'
      cartStore.total_items = 0
    }
  }
)

// Mount app
app.mount('#app')
