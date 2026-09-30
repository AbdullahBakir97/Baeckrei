import { intlLocale } from '@/i18n'
import { business } from '@/config/business'

// Prices follow the chosen language: "2,40 €" in German, "€2.40" in English.
// Reading the locale here makes templates re-render when it changes.
export const formatEuro = (value) =>
  new Intl.NumberFormat(intlLocale(), { style: 'currency', currency: 'EUR' }).format(Number(value || 0))

// Dates and times are shown on the shop's clock (pickup times, opening
// hours), whatever time zone the visitor's device is in.
export const formatDate = (value, options = { day: 'numeric', month: 'long', year: 'numeric' }) =>
  value ? new Intl.DateTimeFormat(intlLocale(), { timeZone: business.timeZone, ...options }).format(new Date(value)) : ''

export const formatDateTime = (value) =>
  formatDate(value, { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
