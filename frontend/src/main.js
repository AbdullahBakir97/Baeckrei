import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import { FontAwesomeIcon } from './plugins/fontawesome'
import VueGlow from '@aksharahegde/vue-glow'
import './style.css'
import App from './App.vue'
import axios from './plugins/axios'

// Initialize Pinia
const pinia = createPinia()

// Create Vue app
const app = createApp(App)

// Use plugins
app.use(pinia)
app.use(router)
app.use(VueGlow)

// Register global components
app.component('font-awesome-icon', FontAwesomeIcon)

// Restore auth token if it exists
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// Mount app
app.mount('#app')
