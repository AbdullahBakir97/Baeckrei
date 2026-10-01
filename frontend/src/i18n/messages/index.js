// Each file holds one area of the site with German and English side by side,
// so a new string is always added in both languages at once.
const modules = import.meta.glob('./*.js', { eager: true })

export function pick(lang) {
  const out = {}
  for (const [path, mod] of Object.entries(modules)) {
    const name = path.replace('./', '').replace('.js', '')
    if (name === 'index') continue
    out[name] = mod.default[lang]
  }
  return out
}
