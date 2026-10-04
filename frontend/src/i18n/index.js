import { createI18n } from 'vue-i18n'
import de from './de'
import en from './en'
import ar from './ar'

export const LOCALES = [
  { code: 'de', label: 'Deutsch', short: 'DE', intl: 'de-DE' },
  { code: 'en', label: 'English', short: 'EN', intl: 'en-GB' },
  // Arabic with Western digits, like prices on the shop's printed menu.
  { code: 'ar', label: 'العربية', short: 'ع', intl: 'ar-u-nu-latn', dir: 'rtl' }
]
const STORAGE_KEY = 'locale'

// German first (the shop is in Berlin); English if the visitor chose it or
// their browser prefers it.
function initialLocale() {
  // Links can pick the language explicitly, e.g. ?lang=en.
  const requested = new URLSearchParams(window.location.search).get('lang')
  if (LOCALES.some(l => l.code === requested)) {
    try { localStorage.setItem(STORAGE_KEY, requested) } catch { /* ignore */ }
    return requested
  }
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (LOCALES.some(l => l.code === saved)) return saved
  } catch { /* storage unavailable */ }
  const browser = (navigator.languages || [navigator.language || 'de'])
    .map(lang => lang.slice(0, 2).toLowerCase())
    .find(code => LOCALES.some(l => l.code === code))
  return browser || 'de'
}

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: initialLocale(),
  // A missing Arabic text shows in English, a missing English one in German.
  fallbackLocale: { ar: ['en', 'de'], en: ['de'], default: ['de'] },
  messages: { de, en, ar },
  missingWarn: false,
  fallbackWarn: false
})

export const currentLocale = () => i18n.global.locale.value
export const intlLocale = () => LOCALES.find(l => l.code === currentLocale())?.intl || 'de-DE'
export const t = (...args) => i18n.global.t(...args)

export const isRtl = () => LOCALES.find(l => l.code === currentLocale())?.dir === 'rtl'

// The page's language and reading direction follow the chosen language.
function applyToDocument(code) {
  document.documentElement.lang = code
  document.documentElement.dir = LOCALES.find(l => l.code === code)?.dir || 'ltr'
}

export function setLocale(code) {
  if (!LOCALES.some(l => l.code === code)) return
  i18n.global.locale.value = code
  applyToDocument(code)
  try { localStorage.setItem(STORAGE_KEY, code) } catch { /* ignore */ }
  // Scroll effects measured for the old text direction measure again.
  requestAnimationFrame(() => window.dispatchEvent(new Event('resize')))
}

applyToDocument(currentLocale())
