// Each file holds one area of the site with German and English side by side,
// so a new string is always added in both languages at once. The admin texts
// are loaded with the admin area (see AdminLayout.vue).
const modules = import.meta.glob(['./*.js', '!./admin.js', '!./index.js'], { eager: true })

export function pick(lang) {
  const out = {}
  for (const [path, mod] of Object.entries(modules)) {
    const name = path.replace('./', '').replace('.js', '')
    if (name === 'index') continue
    out[name] = mod.default[lang]
  }
  return out
}
