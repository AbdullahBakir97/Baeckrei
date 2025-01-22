import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import { useAuthStore } from './stores/authStore'
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

// Restore auth token if it exists
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// Mount app
app.mount('#app')
