import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import './plugins/fontawesome'
import VueGlow from '@aksharahegde/vue-glow'
import { installMotion } from './motion/directives'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(VueGlow)
installMotion(app)

// Register global components
app.component('font-awesome-icon', FontAwesomeIcon)

// The router guard waits for the auth state to load before resolving the
// first navigation, so the app can mount straight away.
app.mount('#app')
