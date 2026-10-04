import { reactive } from 'vue'
import axios from '@/plugins/axios'
import { intlLocale } from '@/i18n'

// Single source for the shop's public details (footer, contact, legal pages).
// The values here are the defaults; the bakery edits the real ones in the
// admin (Settings), and loadShopInfo() puts them in place when the site opens.
// Empty values are shown as "to be added" on the legal pages and hidden elsewhere.
export const business = reactive({
  name: 'Backlover',
  legalName: '', // e.g. "Backlover GmbH" or the owner's full name
  owner: '', // person responsible for the content (Impressum)
  street: 'Friedrichstraße',
  houseNumber: '',
  postalCode: '',
  city: 'Berlin',
  country: 'Deutschland',
  transit: 'U-Bahn Friedrichstraße',
  email: '',
  phone: '',
  vatId: '', // USt-IdNr., if any
  register: '', // Handelsregister entry, if any
  // Weekly hours from the server: [{ weekday: 0-6, ranges: [['07:00', '18:00']] }]
  weeklyHours: [],
  // Upcoming closing days: [{ start, end, label, label_en }]
  closures: [],
  closedToday: null,
  announcement: '',
  announcementEn: '',
  deliveryFee: null,
  // Grouped for display, e.g. [{ days: 'Mo – Fr', hours: '07:00–18:00' }]
  get openingHours() {
    return groupHours(this.weeklyHours, intlLocale())
  },
  // Pickup and delivery times are shown on the shop's clock, wherever the
  // visitor is (the bookable slots come from the backend's opening hours).
  timeZone: 'Europe/Berlin',
  // Optional Spline scene for the home page hero (see .env.example).
  splineScene: import.meta.env.VITE_SPLINE_SCENE || '',
  social: {
    instagram: '',
    facebook: '',
    twitter: ''
  }
})

function groupHours(days, locale) {
  if (!days?.length) return []
  const name = (d) => new Intl.DateTimeFormat(locale, { weekday: 'short' }).format(new Date(2024, 0, 1 + d))
  const text = (ranges) => ranges.map(([a, b]) => `${a}–${b}`).join(', ')
  const rows = []
  for (const day of [...days].sort((a, b) => a.weekday - b.weekday)) {
    if (!day.ranges.length) continue
    const last = rows[rows.length - 1]
    if (last && last.to === day.weekday - 1 && last.hours === text(day.ranges)) last.to = day.weekday
    else rows.push({ from: day.weekday, to: day.weekday, hours: text(day.ranges) })
  }
  return rows.map(r => ({ days: r.from === r.to ? name(r.from) : `${name(r.from)} – ${name(r.to)}`, hours: r.hours }))
}

// Fetch the details the bakery saved in the admin.
export async function loadShopInfo() {
  try {
    const { data } = await axios.get('/api/shop/info/')
    const values = {
      name: data.name, legalName: data.legal_name, owner: data.owner, street: data.street,
      houseNumber: data.house_number, postalCode: data.postal_code, city: data.city, country: data.country,
      transit: data.transit, email: data.email, phone: data.phone, vatId: data.vat_id, register: data.register,
      announcement: data.announcement, announcementEn: data.announcement_en
    }
    // Before the first save, keep the defaults above for anything still empty.
    for (const [key, value] of Object.entries(values)) {
      if (data.configured || value) business[key] = value || ''
    }
    for (const key of ['instagram', 'facebook', 'twitter']) {
      if (data.configured || data[key]) business.social[key] = data[key] || ''
    }
    business.weeklyHours = data.hours?.days || []
    business.closures = data.hours?.closures || []
    business.closedToday = data.hours?.closed_today || null
    business.deliveryFee = data.delivery_fee
  } catch { /* offline: keep the defaults */ }
}

export const streetLine = () =>
  [business.street, business.houseNumber].filter(Boolean).join(' ')

export const cityLine = () =>
  [business.postalCode, business.city].filter(Boolean).join(' ')
