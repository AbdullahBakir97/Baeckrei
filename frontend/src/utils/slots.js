import { business } from '@/config/business'
import { intlLocale, t } from '@/i18n'

// Pickup/delivery slots from the checkout options, grouped by day and
// labelled on the shop's clock.
const zone = { timeZone: business.timeZone }
const dayKey = (date) => new Intl.DateTimeFormat('en-CA', { ...zone, year: 'numeric', month: '2-digit', day: '2-digit' }).format(date)

export const slotTime = (iso) =>
  new Intl.DateTimeFormat(intlLocale(), { ...zone, hour: '2-digit', minute: '2-digit' }).format(new Date(iso))

export function slotDayLabel(key) {
  const today = dayKey(new Date())
  const tomorrow = dayKey(new Date(Date.now() + 864e5))
  if (key === today) return t('checkout.today')
  if (key === tomorrow) return t('checkout.tomorrow')
  // Noon avoids the date shifting across time zones.
  return new Intl.DateTimeFormat(intlLocale(), { ...zone, weekday: 'short', day: 'numeric', month: 'numeric' })
    .format(new Date(`${key}T12:00:00Z`))
}

export function groupSlots(slots = []) {
  const days = []
  for (const slot of slots) {
    const key = dayKey(new Date(slot.start))
    let day = days[days.length - 1]
    if (!day || day.key !== key) days.push(day = { key, slots: [] })
    day.slots.push(slot)
  }
  return days.filter(day => day.slots.some(slot => slot.available))
}

/** "Heute, 14:30" / "Fri 3/10, 08:00" */
export const slotLabel = (iso) => `${slotDayLabel(dayKey(new Date(iso)))}, ${slotTime(iso)}`
