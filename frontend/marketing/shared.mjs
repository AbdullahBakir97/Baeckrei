// Shared pieces for the print and social designs: fonts, colours, frames for
// screenshots, prices, QR codes and the page skeleton.
import { dirname, join } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import QRCode from 'qrcode'
import shop from './data/shop.mjs'
import copy from './data/copy.mjs'

export const HERE = dirname(fileURLToPath(import.meta.url))
export const FRONTEND = join(HERE, '..')
const NODE_MODULES = join(FRONTEND, 'node_modules')
const url = (path) => pathToFileURL(path).href

export { shop }

/** A product photo from frontend/src/assets/bakery. */
export const photo = (name) => url(join(FRONTEND, 'src/assets/bakery', name))

/** A screenshot from marketing/assets/screens/<lang> (each edition shows the site in its own language). */
export const screen = (lang, name) => url(join(HERE, 'assets/screens', lang, `${name}.jpg`))

/** Copy text by dotted path, with {placeholders} filled in. */
export function text(lang, path, params = {}) {
  const value = path.split('.').reduce((node, key) => node?.[key], copy[lang])
  if (typeof value !== 'string') return value
  return value.replace(/\{(\w+)\}/g, (_, key) => params[key] ?? `{${key}}`)
}

export const esc = (value) => String(value ?? '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

/** "2,40 €" in German, "2.40 €" (kept left-to-right) in Arabic. */
export function price(value, lang) {
  if (lang === 'ar') return `<bdi dir="ltr" class="num">${Number(value).toFixed(2)} €</bdi>`
  return `<span class="num">${new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value)}</span>`
}

export const host = () => shop.website.replace(/^https?:\/\//, '').replace(/\/$/, '')
export const shopUrl = (path = '/products') => shop.website.replace(/\/$/, '') + path

/** Inline SVG QR code. */
export async function qr(target, { dark = '#1d1712', light = '#00000000' } = {}) {
  return QRCode.toString(target, { type: 'svg', margin: 0, errorCorrectionLevel: 'M', color: { dark, light } })
}

export const hoursList = (lang) => shop.hours[lang]
  .map(([days, time]) => `<div class="hours-row"><span>${esc(days)}</span><bdi dir="ltr" class="num">${esc(time)}</bdi></div>`)
  .join('')

export const addressLines = (lang) => [
  `${esc(shop.name)} · ${esc(shop.street)}`,
  esc(shop.city),
  esc(shop.transit[lang])
].filter(Boolean)

export const logo = (extra = '') => `<span class="logo ${extra}"><em>${esc(shop.name.charAt(0))}</em>${esc(shop.name.slice(1))}</span>`

// ---- screenshot frames ----------------------------------------------------
export const browser = (src, path = '') => `
  <figure class="frame-browser">
    <div class="frame-bar"><i></i><i></i><i></i><span dir="ltr">${esc(host())}${esc(path)}</span></div>
    <img src="${src}" alt="">
  </figure>`

export const phone = (src) => `<figure class="frame-phone"><img src="${src}" alt=""></figure>`

export const tv = (src) => `<figure class="frame-tv"><img src="${src}" alt=""><span class="frame-tv-foot"></span></figure>`

// ---- page skeleton --------------------------------------------------------
const FONT_CSS = [
  '@fontsource/instrument-serif/400.css',
  '@fontsource/instrument-serif/400-italic.css',
  '@fontsource-variable/manrope/index.css',
  '@fontsource/el-messiri/400.css',
  '@fontsource/el-messiri/600.css',
  '@fontsource/el-messiri/700.css',
  '@fontsource/ibm-plex-sans-arabic/400.css',
  '@fontsource/ibm-plex-sans-arabic/500.css',
  '@fontsource/ibm-plex-sans-arabic/600.css',
  '@fontsource/ibm-plex-sans-arabic/700.css'
].map(file => `<link rel="stylesheet" href="${url(join(NODE_MODULES, file))}">`).join('\n')

export const BASE_CSS = `
  :root {
    --paper: #f7f0e5;
    --paper-2: #efe4d3;
    --ink: #1d1712;
    --ink-2: #4f4339;
    --muted: #85766a;
    --line: rgba(29, 23, 18, 0.14);
    --crust: #b6722c;
    --crust-light: #e6a15a;
    --gold: #f2c48d;
    --ember: #c4532f;
    --oven: #14110e;
    --oven-2: #201a15;
    --cream: #f4ece1;
    --cream-muted: #b9ab98;
    --green: #4f7d43;
    --display: 'Instrument Serif', Georgia, serif;
    --sans: 'Manrope Variable', 'Manrope', system-ui, sans-serif;
  }
  [lang="ar"] {
    --display: 'El Messiri', 'Instrument Serif', serif;
    --sans: 'IBM Plex Sans Arabic', 'Manrope Variable', system-ui, sans-serif;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { background: #777; }
  body {
    font-family: var(--sans);
    color: var(--ink);
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    text-rendering: geometricPrecision;
  }
  img { display: block; }
  .sheet {
    position: relative;
    overflow: hidden;
    break-after: page;
    background: var(--paper);
  }
  .sheet:last-child { break-after: auto; }
  .paper {
    background:
      radial-gradient(70% 45% at 85% 0%, rgba(230, 161, 90, 0.18), transparent 70%),
      radial-gradient(60% 40% at 0% 100%, rgba(196, 83, 47, 0.07), transparent 70%),
      var(--paper);
  }
  .dark {
    color: var(--cream);
    background:
      radial-gradient(60% 50% at 70% 35%, rgba(230, 161, 90, 0.22), transparent 70%),
      radial-gradient(60% 50% at 0% 100%, rgba(196, 83, 47, 0.14), transparent 70%),
      var(--oven);
  }
  .logo { font-family: 'Instrument Serif', Georgia, serif; font-weight: 400; line-height: 1; letter-spacing: -0.01em; white-space: nowrap; }
  .logo em { font-style: normal; color: var(--crust); }
  .dark .logo em { color: var(--crust-light); }
  .display { font-family: var(--display); font-weight: 400; line-height: 1.02; letter-spacing: -0.01em; }
  [lang="ar"] .display { font-weight: 600; line-height: 1.3; letter-spacing: 0; }
  .eyebrow { font-size: var(--eyebrow, 7.5pt); font-weight: 700; letter-spacing: 0.22em; text-transform: uppercase; color: var(--crust); }
  [lang="ar"] .eyebrow { letter-spacing: 0; font-size: calc(var(--eyebrow, 7.5pt) * 1.2); }
  .dark .eyebrow { color: var(--crust-light); }
  .num { font-variant-numeric: tabular-nums; white-space: nowrap; }
  .muted { color: var(--muted); }
  .dark .muted { color: var(--cream-muted); }
  .cutout { position: absolute; object-fit: contain; filter: drop-shadow(0 4mm 5mm rgba(40, 22, 8, 0.35)); }
  .dark .cutout { filter: drop-shadow(0 5mm 7mm rgba(0, 0, 0, 0.6)); }
  .qr svg { display: block; width: 100%; height: 100%; }
  .qr-card { background: var(--cream); border-radius: 3mm; padding: 2.4mm; }
  .hours-row { display: flex; justify-content: space-between; gap: 4mm; }

  /* Screenshot frames */
  .frame-browser { border-radius: 2.2mm; overflow: hidden; background: #0e0c0a; box-shadow: 0 2.5mm 6mm rgba(29, 23, 18, 0.25); border: 0.25mm solid rgba(29, 23, 18, 0.25); }
  .frame-bar { display: flex; align-items: center; gap: 1.1mm; height: 5mm; padding: 0 2mm; background: #2a231c; }
  .frame-bar i { width: 1.5mm; height: 1.5mm; border-radius: 50%; background: #5b4e42; }
  .frame-bar span { flex: 1; margin: 0 4mm; padding: 0.5mm 2mm; border-radius: 9mm; background: #14110e; color: #b9ab98; font: 500 5.5pt var(--sans); text-align: center; }
  .frame-browser img { width: 100%; }
  .frame-phone { position: relative; border-radius: 6mm; padding: 1.6mm; background: #0b0908; box-shadow: 0 3mm 7mm rgba(29, 23, 18, 0.35), inset 0 0 0 0.35mm #3a3029; }
  .frame-phone::before { content: ''; position: absolute; top: 2.6mm; left: 50%; width: 9mm; height: 2.2mm; margin-left: -4.5mm; border-radius: 2mm; background: #0b0908; z-index: 1; }
  .frame-phone img { width: 100%; border-radius: 4.6mm; }
  .frame-tv { position: relative; padding: 1.6mm; border-radius: 1.8mm; background: #0b0908; box-shadow: 0 3mm 7mm rgba(29, 23, 18, 0.35); }
  .frame-tv img { width: 100%; border-radius: 0.6mm; }
  .frame-tv-foot { position: absolute; left: 50%; bottom: -5mm; width: 26mm; height: 5mm; margin-left: -13mm; background: linear-gradient(#2a231c, #14110e); clip-path: polygon(30% 0, 70% 0, 100% 100%, 0 100%); }
`

/** A complete HTML document of pages that are `width` × `height` (CSS units). */
export function documentHtml({ lang, title, width, height, css = '', pages }) {
  return `<!doctype html>
<html lang="${lang}" dir="${lang === 'ar' ? 'rtl' : 'ltr'}">
<head>
<meta charset="utf-8">
<title>${esc(title)}</title>
${FONT_CSS}
<style>
  @page { size: ${width} ${height}; margin: 0; }
  ${BASE_CSS}
  .sheet { width: ${width}; height: ${height}; }
  ${css}
</style>
</head>
<body>
${pages.join('\n')}
</body>
</html>`
}
