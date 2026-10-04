import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
// Fonts are bundled with the site (no requests to Google's font servers).
import '@fontsource/instrument-serif/400.css'
import '@fontsource/instrument-serif/400-italic.css'
import '@fontsource-variable/manrope/wght.css'
import './assets/arabic-fonts.css'
import './style.css'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import './plugins/fontawesome'
import { installMotion } from './motion/directives'
import { i18n } from './i18n'
import { createHead } from '@unhead/vue/client'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)
app.use(createHead())
installMotion(app)

// Register global components
app.component('font-awesome-icon', FontAwesomeIcon)

// The router guard waits for the auth state to load before resolving the
// first navigation, so the app can mount straight away.
app.mount('#app')
