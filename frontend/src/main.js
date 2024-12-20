import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import { FontAwesomeIcon } from './plugins/fontawesome'
import './style.css'
import App from './App.vue'

// Initialize Pinia
const pinia = createPinia()

// Create Vue app
const app = createApp(App)

// Use plugins
app.use(pinia)
app.use(router)

// Register global components
app.component('font-awesome-icon', FontAwesomeIcon)

// Mount app
app.mount('#app')
