import { createI18n } from 'vue-i18n'
import de from './de'
import en from './en'

export const LOCALES = [
  { code: 'de', label: 'Deutsch', short: 'DE', intl: 'de-DE' },
  { code: 'en', label: 'English', short: 'EN', intl: 'en-GB' }
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
  fallbackLocale: 'de',
  messages: { de, en },
  missingWarn: false,
  fallbackWarn: false
})

export const currentLocale = () => i18n.global.locale.value
export const intlLocale = () => LOCALES.find(l => l.code === currentLocale())?.intl || 'de-DE'
export const t = (...args) => i18n.global.t(...args)

export function setLocale(code) {
  if (!LOCALES.some(l => l.code === code)) return
  i18n.global.locale.value = code
  document.documentElement.lang = code
  try { localStorage.setItem(STORAGE_KEY, code) } catch { /* ignore */ }
}

document.documentElement.lang = currentLocale()
