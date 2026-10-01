<template>
  <footer class="footer">
    <div class="section">
      <!-- Newsletter -->
      <div class="footer-news">
        <div>
          <p v-reveal class="eyebrow">{{ $t('footer.newsletter') }}</p>
          <h2 v-split class="display-title text-5xl sm:text-6xl mt-4 max-w-xl">
            {{ $t('footer.newsletterTitle') }}
          </h2>
        </div>
        <div v-reveal="{ delay: 0.15 }" class="w-full max-w-md">
          <p v-if="newsletterMessage" class="mb-3 text-sm" :class="newsletterOk ? 'text-green-300' : 'text-red-300'" role="status">
            {{ newsletterMessage }}
          </p>
          <form v-if="!newsletterOk" class="footer-form" @submit.prevent="subscribeNewsletter">
            <label for="newsletter-email" class="sr-only">{{ $t('footer.emailLabel') }}</label>
            <input id="newsletter-email" v-model.trim="email" type="email" :placeholder="$t('footer.emailPlaceholder')" required autocomplete="email" />
            <button type="submit" class="btn-amber !py-3 !px-6" :disabled="subscribing">
              {{ subscribing ? $t('footer.sending') : $t('footer.subscribe') }}
            </button>
          </form>
          <p class="mt-3 text-xs text-cream-faint">
            {{ $t('footer.newsletterNote') }}
            <router-link to="/privacy" class="underline hover:text-cream">{{ $t('footer.privacyPolicy') }}</router-link>.
          </p>
        </div>
      </div>

      <!-- Links -->
      <div class="footer-cols">
        <div>
          <h3 class="footer-head">{{ $t('footer.shop') }}</h3>
          <ul>
            <li><router-link to="/products">{{ $t('common.allProducts') }}</router-link></li>
            <li v-for="category in categories" :key="category.slug">
              <router-link :to="{ name: 'category', params: { category: category.slug } }">{{ categoryName(category) }}</router-link>
            </li>
            <li><router-link :to="{ name: 'seasonal' }">{{ $t('common.seasonal') }}</router-link></li>
          </ul>
        </div>
        <div>
          <h3 class="footer-head">{{ $t('footer.explore') }}</h3>
          <ul>
            <li v-for="link in exploreLinks" :key="link.to"><router-link :to="link.to">{{ $t(link.label) }}</router-link></li>
          </ul>
        </div>
        <div>
          <h3 class="footer-head">{{ $t('footer.visit') }}</h3>
          <address class="not-italic space-y-2 text-cream-muted">
            <p>{{ business.name }}<br>{{ storeAddress }}</p>
            <p v-if="business.transit" class="flex items-center gap-2">
              <font-awesome-icon icon="train-subway" class="text-crust" /> {{ business.transit }}
            </p>
            <p v-if="business.phone">{{ business.phone }}</p>
            <p v-if="business.email">{{ business.email }}</p>
          </address>
          <dl v-if="business.openingHours.length" class="mt-4 grid grid-cols-2 gap-y-1 text-sm text-cream-muted">
            <template v-for="row in business.openingHours" :key="row.days">
              <dt>{{ row.days }}</dt><dd class="tabular-nums">{{ row.hours }}</dd>
            </template>
          </dl>
        </div>
        <div>
          <h3 class="footer-head">{{ $t('footer.account') }}</h3>
          <ul>
            <li><router-link to="/cart">{{ $t('footer.cart') }}</router-link></li>
            <li><router-link to="/wishlist">{{ $t('nav.wishlist') }}</router-link></li>
            <li><router-link to="/orders">{{ $t('nav.orders') }}</router-link></li>
            <li><router-link to="/profile">{{ $t('nav.profile') }}</router-link></li>
          </ul>
          <div v-if="socialLinks.length" class="mt-6 flex gap-3">
            <a v-for="link in socialLinks" :key="link.icon" :href="link.url" class="footer-social"
               target="_blank" rel="noopener" :aria-label="link.label">
              <font-awesome-icon :icon="['fab', link.icon]" />
            </a>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="footer-bottom">
        <p>© {{ year }} {{ business.name }} · {{ $t('footer.madeIn', { city: business.city }) }}</p>
        <nav class="flex flex-wrap gap-x-6 gap-y-2" :aria-label="$t('footer.legal')">
          <router-link to="/impressum">{{ $t('footer.impressum') }}</router-link>
          <router-link to="/privacy">{{ $t('footer.privacy') }}</router-link>
          <router-link to="/terms">{{ $t('footer.terms') }}</router-link>
          <router-link to="/cookie-policy">{{ $t('footer.cookies') }}</router-link>
        </nav>
      </div>
    </div>

    <!-- Oversized wordmark rising out of the bottom edge -->
    <div class="footer-mark" aria-hidden="true">
      <span v-parallax="-0.25">{{ business.name }}</span>
    </div>
  </footer>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { useProductStore } from '@/stores/productStore'
import { business, streetLine, cityLine } from '@/config/business'
import { categoryName } from '@/i18n/catalog'

const { t } = useI18n()
const email = ref('')
const productStore = useProductStore()
const storeAddress = [streetLine(), cityLine()].filter(Boolean).join(', ')
const year = new Date().getFullYear()

// Only show social icons that have a real URL in src/config/business.js.
const socialLinks = [
  { icon: 'instagram', label: 'Instagram', url: business.social.instagram },
  { icon: 'facebook', label: 'Facebook', url: business.social.facebook },
  { icon: 'twitter', label: 'Twitter', url: business.social.twitter }
].filter(link => link.url)

const exploreLinks = [
  { label: 'nav.homeLink', to: '/' },
  { label: 'nav.about', to: '/about' },
  { label: 'nav.journal', to: '/blog' },
  { label: 'nav.contact', to: '/contact' },
  { label: 'footer.compare', to: '/compare' }
]

const categories = computed(() => productStore.categories.filter(c => c.is_active !== false))

onMounted(() => {
  if (!productStore.categories.length) productStore.fetchCategories()
})

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
    newsletterMessage.value = t('footer.subscribed')
    email.value = ''
  } catch (err) {
    newsletterMessage.value = err.response?.status === 400 ? t('footer.invalidEmail') : t('footer.tryLater')
  } finally {
    subscribing.value = false
  }
}
</script>

<style scoped>
.footer {
  position: relative;
  z-index: 1;
  margin-top: 8rem;
  overflow: hidden;
  border-top: 1px solid rgba(244, 236, 225, 0.07);
  background:
    radial-gradient(60% 50% at 50% 100%, rgba(210, 96, 63, 0.12), transparent 70%),
    #0e0c0a;
}

.footer-news {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 2.5rem;
  padding: 6rem 0 4.5rem;
  border-bottom: 1px solid rgba(244, 236, 225, 0.07);
}

.footer-form {
  display: flex;
  gap: 0.4rem;
  padding: 0.35rem;
  border-radius: 9999px;
  background: rgba(244, 236, 225, 0.05);
  border: 1px solid rgba(244, 236, 225, 0.12);
}

.footer-form input {
  flex: 1;
  min-width: 0;
  padding: 0 1rem;
  border: 0;
  background: transparent;
  color: #f4ece1;
  outline: none;
}

.footer-form input::placeholder {
  color: #7d7061;
}

.footer-cols {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 2.5rem;
  padding: 4rem 0;
  font-size: 0.95rem;
}

@media (min-width: 768px) {
  .footer-cols {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.footer-head {
  margin-bottom: 1.1rem;
  font-family: 'Manrope Variable', system-ui, sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #7d7061;
}

.footer-cols ul {
  display: grid;
  gap: 0.6rem;
}

.footer-cols a {
  color: #d9cfc2;
  background: linear-gradient(currentColor, currentColor) no-repeat 0 100% / 0 1px;
  transition: color 0.3s, background-size 0.5s var(--ease-out-expo);
}

.footer-cols a:hover {
  background-size: 100% 1px;
}

.footer-cols a:hover {
  color: #f2c48d;
}

.footer-social {
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  border: 1px solid rgba(244, 236, 225, 0.14);
}

.footer-bottom {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.75rem 0;
  border-top: 1px solid rgba(244, 236, 225, 0.07);
  font-size: 0.85rem;
  color: #7d7061;
}

.footer-bottom a {
  color: #b9ab98;
}

.footer-bottom a:hover {
  color: #f4ece1;
}

.footer-mark {
  display: flex;
  justify-content: center;
  height: clamp(5rem, 16vw, 15rem);
  overflow: hidden;
  pointer-events: none;
  user-select: none;
}

.footer-mark span {
  display: block;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: clamp(7rem, 25vw, 24rem);
  line-height: 0.9;
  letter-spacing: -0.04em;
  background: linear-gradient(180deg, rgba(230, 161, 90, 0.35), rgba(230, 161, 90, 0));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
</style>
