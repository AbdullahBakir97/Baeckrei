import { intlLocale } from '@/i18n'

// Prices follow the chosen language: "2,40 €" in German, "€2.40" in English.
// Reading the locale here makes templates re-render when it changes.
export const formatEuro = (value) =>
  new Intl.NumberFormat(intlLocale(), { style: 'currency', currency: 'EUR' }).format(Number(value || 0))

export const formatDate = (value, options = { day: 'numeric', month: 'long', year: 'numeric' }) =>
  value ? new Intl.DateTimeFormat(intlLocale(), options).format(new Date(value)) : ''

export const formatDateTime = (value) =>
  formatDate(value, { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
