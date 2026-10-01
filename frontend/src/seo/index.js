import { computed, toValue } from 'vue'
import { useHead } from '@unhead/vue'
import { business } from '@/config/business'

// Absolute URLs are needed for canonical links, share previews and
// structured data. Set VITE_SITE_URL in production (see .env.example).
export const SITE_URL = (import.meta.env.VITE_SITE_URL || window.location.origin).replace(/\/$/, '')
export const absoluteUrl = (path = '/') => (/^https?:\/\//.test(path) ? path : `${SITE_URL}${path.startsWith('/') ? '' : '/'}${path}`)
export const SHARE_IMAGE = '/og-image.jpg'

const clip = (text, length = 160) => {
  const clean = String(text || '').replace(/\s+/g, ' ').trim()
  return clean.length > length ? `${clean.slice(0, length - 1).trimEnd()}…` : clean
}

/**
 * Page title, description, share preview and structured data.
 * `meta` is a getter (or ref) returning { title, description, image, type, jsonLd, noindex }.
 * Later calls override earlier ones, so pages refine what App.vue sets.
 */
export function usePageMeta(meta) {
  const data = computed(() => toValue(meta) || {})
  useHead(() => {
    const { title, description, image, type, jsonLd, noindex, path } = data.value
    const tags = []
    if (description) {
      const text = clip(description)
      tags.push({ key: 'description', name: 'description', content: text })
      tags.push({ key: 'og:description', property: 'og:description', content: text })
      tags.push({ key: 'twitter:description', name: 'twitter:description', content: text })
    }
    if (title) {
      tags.push({ key: 'og:title', property: 'og:title', content: title })
      tags.push({ key: 'twitter:title', name: 'twitter:title', content: title })
    }
    if (image) {
      tags.push({ key: 'og:image', property: 'og:image', content: absoluteUrl(image) })
      tags.push({ key: 'twitter:image', name: 'twitter:image', content: absoluteUrl(image) })
    }
    if (type) tags.push({ key: 'og:type', property: 'og:type', content: type })
    if (path) tags.push({ key: 'og:url', property: 'og:url', content: absoluteUrl(path) })
    if (noindex !== undefined) tags.push({ key: 'robots', name: 'robots', content: noindex ? 'noindex, nofollow' : 'index, follow' })

    const head = { meta: tags }
    if (title) head.title = title
    if (path) head.link = [{ key: 'canonical', rel: 'canonical', href: absoluteUrl(path) }]
    if (jsonLd) {
      head.script = [].concat(jsonLd).map((item, index) => ({
        key: `ld-${item['@type']}-${index}`,
        type: 'application/ld+json',
        innerHTML: JSON.stringify({ '@context': 'https://schema.org', ...item })
      }))
    }
    return head
  })
}

// schema.org description of the shop, used for Google Maps / local results.
export function bakeryJsonLd() {
  const address = {
    '@type': 'PostalAddress',
    streetAddress: [business.street, business.houseNumber].filter(Boolean).join(' '),
    addressLocality: business.city,
    addressCountry: 'DE'
  }
  if (business.postalCode) address.postalCode = business.postalCode
  const data = {
    '@type': 'Bakery',
    '@id': `${SITE_URL}/#bakery`,
    name: business.name,
    url: SITE_URL,
    image: absoluteUrl(SHARE_IMAGE),
    address,
    servesCuisine: 'Bakery',
    priceRange: '€'
  }
  if (business.phone) data.telephone = business.phone
  if (business.email) data.email = business.email
  const sameAs = Object.values(business.social || {}).filter(Boolean)
  if (sameAs.length) data.sameAs = sameAs
  return data
}
