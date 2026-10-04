// Small helpers shared by the Studio pages.
export function errorsFrom(err) {
  const data = err?.response?.data
  const fields = {}
  let message = ''
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    for (const [key, value] of Object.entries(data)) {
      const text = Array.isArray(value) ? value[0] : (typeof value === 'object' ? Object.values(value).flat()[0] : value)
      if (key === 'detail' || key === 'non_field_errors') message = String(text)
      else fields[key] = String(text)
    }
  } else if (Array.isArray(data)) {
    message = String(data[0])
  }
  return { fields, message }
}

export const listOf = (data) => (Array.isArray(data) ? data : data?.results || [])

// <input type="datetime-local"> works in local time without a zone.
export function toLocalInput(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}
export const fromLocalInput = (value) => (value ? new Date(value).toISOString() : null)

export function formatDate(iso, locale, withTime = true) {
  if (!iso) return ''
  return new Intl.DateTimeFormat(locale, withTime
    ? { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }
    : { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(iso))
}

export const paragraphs = (text) => String(text || '').split(/\n\s*\n/).map(p => p.trim()).filter(Boolean)
