import { i18n } from './index'

const { t, te, locale } = i18n.global

// Products and categories are written in German; an English version is
// optional (`name_en`, `description_en`) and used for English and Arabic
// (there is no Arabic version of the catalogue; English reads better there).
export function localized(item, field) {
  if (!item) return ''
  if (locale.value !== 'de' && item[`${field}_en`]) return item[`${field}_en`]
  return item[field] || ''
}

// The categories created with the shop still carry their original English
// names; while a name is unchanged it is shown in the visitor's language.
function seeded(item, field, key) {
  if (!te(key, 'en')) return null
  return item[field] === t(key, {}, { locale: 'en' }) ? t(key) : null
}

export function categoryName(category) {
  if (!category) return ''
  if (locale.value !== 'de' && category.name_en) return category.name_en
  return seeded(category, 'name', `categories.${category.slug}`) || category.name || ''
}

export function categoryDescription(category) {
  if (!category) return ''
  if (locale.value !== 'de' && category.description_en) return category.description_en
  return seeded(category, 'description', `categories.descriptions.${category.slug}`) || category.description || ''
}
