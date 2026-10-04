// Builds the print and social designs into marketing/dist/<de|ar>/:
//   speisekarte-a4.pdf         menu, 2 pages, A4 + 3 mm bleed
//   flyer-a5.pdf               "order online" flyer, front + back, A5 + 3 mm bleed
//   postkarte-a6.pdf           breakfast postcard, front + back, A6 + 3 mm bleed
//   plakat-a3.pdf              window poster, A3 + 3 mm bleed
//   kundeninfo-a4.pdf          customer guide (A4, for screens and home printers)
//   handbuch-a4.pdf            owner handbook: running the shop and the admin (A4)
//   social-post.png / social-story.png   Instagram post (1080×1350) and story (1080×1920)
// plus small previews in marketing/dist/previews/.
//
//   npm run marketing             (both languages)
//   npm run marketing -- --lang ar --only guide
//
// Edit prices, hours and texts in marketing/data/ first. Screenshots for the
// guide come from `npm run marketing:screens`.
import { chromium } from '@playwright/test'
import { mkdirSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { HERE } from './shared.mjs'
import { menuDocument } from './docs/menu.mjs'
import { flyerDocument, postcardDocument, posterDocument, socialPostDocument, socialStoryDocument } from './docs/flyers.mjs'
import { guideDocument } from './docs/guide.mjs'
import { handbookDocument } from './docs/handbook.mjs'

const argv = process.argv.slice(2)
const option = (name) => { const i = argv.indexOf(`--${name}`); return i >= 0 ? argv[i + 1] : null }
const LANGS = (option('lang') || 'de,ar').split(',')
const ONLY = option('only') ? option('only').split(',') : null

// `dpi` is the resolution images are scaled down to: 300 for the print
// shop, less for the brochures that are read on screens.
const PRINT = [
  { key: 'menu', file: 'speisekarte-a4.pdf', make: menuDocument, dpi: 300 },
  { key: 'flyer', file: 'flyer-a5.pdf', make: flyerDocument, dpi: 300 },
  { key: 'postcard', file: 'postkarte-a6.pdf', make: postcardDocument, dpi: 300 },
  { key: 'poster', file: 'plakat-a3.pdf', make: posterDocument, dpi: 300 },
  { key: 'guide', file: 'kundeninfo-a4.pdf', make: guideDocument, dpi: 150 },
  { key: 'handbook', file: 'handbuch-a4.pdf', make: handbookDocument, dpi: 150 }
]
const SOCIAL = [
  { key: 'post', file: 'social-post.png', make: socialPostDocument, width: 1080, height: 1350 },
  { key: 'story', file: 'social-story.png', make: socialStoryDocument, width: 1080, height: 1920 }
]

const DIST = join(HERE, 'dist')
const BUILD = join(HERE, '.build')

async function ready(page) {
  await page.evaluate(async () => {
    await document.fonts.ready
    await Promise.all([...document.images].map(img => img.complete ? null : new Promise(r => { img.onload = img.onerror = r })))
  })
}

// PDF viewers redraw soft gradients with transparency on every scroll, which
// makes long documents stutter. Each gradient background is replaced by a
// picture of itself, so the PDF only holds plain images.
async function flattenGradients(page) {
  const count = await page.evaluate(() => {
    let n = 0
    for (const el of document.querySelectorAll('body *')) {
      const style = getComputedStyle(el)
      if (!style.backgroundImage.includes('gradient') || !el.offsetWidth) continue
      el.dataset.flat = n++
      // Same gradient at the same size (every page of a brochure): one picture.
      el.dataset.flatKey = [style.backgroundImage, style.backgroundColor, el.offsetWidth, el.offsetHeight].join('|')
      // A see-through background is kept as PNG, an opaque one as JPEG.
      el.dataset.flatAlpha = style.backgroundColor.startsWith('rgba') || style.backgroundColor === 'transparent' ? '1' : ''
    }
    return n
  })
  if (!count) return
  await page.addStyleTag({ content: `
    html.flat, html.flat body { background: transparent !important; }
    html.flat * { visibility: hidden !important; }
    html.flat .flat-target { visibility: visible !important; }
    html.flat .flat-target * { visibility: hidden !important; }` })
  const pictures = new Map()
  for (let i = 0; i < count; i++) {
    const el = page.locator(`[data-flat="${i}"]`)
    const { key, alpha } = await el.evaluate(node => ({ key: node.dataset.flatKey, alpha: Boolean(node.dataset.flatAlpha) }))
    if (!pictures.has(key)) {
      await el.evaluate(node => { document.documentElement.classList.add('flat'); node.classList.add('flat-target') })
      const shot = await el.screenshot({ type: alpha ? 'png' : 'jpeg', quality: alpha ? undefined : 85, omitBackground: alpha, animations: 'disabled' })
      await el.evaluate(node => { node.classList.remove('flat-target'); document.documentElement.classList.remove('flat') })
      pictures.set(key, `data:image/${alpha ? 'png' : 'jpeg'};base64,${shot.toString('base64')}`)
    }
    await el.evaluate((node, url) => {
      Object.assign(node.style, { backgroundImage: `url(${url})`, backgroundSize: '100% 100%', backgroundRepeat: 'no-repeat', backgroundPosition: '0 0', backgroundOrigin: 'border-box' })
    }, pictures.get(key))
  }
  await ready(page)
}

// Scale every picture down to what the page needs at `dpi`, so a photo
// shown 5 cm wide is not embedded at full screenshot size. Drop shadows are
// drawn into the picture too: as a CSS filter, Chromium stores each shadowed
// cut-out as a huge see-through image.
async function shrinkImages(page, dpi) {
  await page.evaluate(async (scale) => {
    const px = (value) => parseFloat(value) || 0
    for (const img of document.images) {
      const width = img.offsetWidth
      const height = img.offsetHeight
      if (!width || !img.naturalWidth || img.currentSrc.startsWith('data:')) continue
      const style = getComputedStyle(img)
      // e.g. "drop-shadow(rgba(40, 22, 8, 0.35) 0px 15px 19px)"
      const shadow = style.filter.match(/^drop-shadow\((rgba?\([^)]*\)) (-?[\d.]+)px (-?[\d.]+)px ([\d.]+)px\)$/)
      const fit = Math.min(width / img.naturalWidth, height / img.naturalHeight)
      const k = Math.min(scale, 1 / fit) // canvas pixels per CSS pixel, never above the original
      if (!shadow && img.naturalWidth <= img.naturalWidth * fit * scale * 1.15) continue

      const [, color, dx, dy, blur] = shadow || [, '', 0, 0, 0]
      const pad = shadow ? Math.ceil(px(blur) * 1.5 + Math.max(Math.abs(px(dx)), Math.abs(px(dy)))) : 0
      const canvas = document.createElement('canvas')
      canvas.width = Math.round((width + 2 * pad) * k)
      canvas.height = Math.round((height + 2 * pad) * k)
      const ctx = canvas.getContext('2d')
      ctx.imageSmoothingQuality = 'high'
      if (shadow) ctx.filter = `drop-shadow(${px(dx) * k}px ${px(dy) * k}px ${px(blur) * k}px ${color})`
      const drawnW = img.naturalWidth * fit
      const drawnH = img.naturalHeight * fit
      ctx.drawImage(img, (pad + (width - drawnW) / 2) * k, (pad + (height - drawnH) / 2) * k, drawnW * k, drawnH * k)

      const png = shadow || /\.png($|\?)/i.test(img.currentSrc)
      if (pad) {
        // Grow the box by the shadow on every side without moving its centre.
        Object.assign(img.style, {
          width: `${width + 2 * pad}px`, height: `${height + 2 * pad}px`, objectFit: 'fill', filter: 'none',
          marginTop: `${px(style.marginTop) - pad}px`, marginRight: `${px(style.marginRight) - pad}px`,
          marginBottom: `${px(style.marginBottom) - pad}px`, marginLeft: `${px(style.marginLeft) - pad}px`
        })
      }
      img.src = png ? canvas.toDataURL('image/png') : canvas.toDataURL('image/jpeg', scale > 2 ? 0.9 : 0.8)
    }
  }, dpi / 96)
  await ready(page)
}

// A blurred box shadow becomes a blurred image mask in the PDF, which viewers
// redraw slowly. A few sharp, faint layers look almost the same and stay
// plain shapes.
async function sharpenShadows(page) {
  await page.evaluate(() => {
    const split = (value) => value.split(/,(?![^(]*\))/).map(part => part.trim())
    for (const el of document.querySelectorAll('body *')) {
      const value = getComputedStyle(el).boxShadow
      if (!value || value === 'none') continue
      let changed = false
      const layers = split(value).flatMap(shadow => {
        // "rgba(29, 23, 18, 0.25) 0px 9.4px 22.7px 0px" (+ "inset")
        const match = shadow.match(/^rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?\) (-?[\d.]+)px (-?[\d.]+)px ([\d.]+)px (-?[\d.]+)px$/)
        if (!match || parseFloat(match[7]) === 0) return [shadow]
        changed = true
        const [, r, g, b, a = 1, x, y, blur, spread] = match.map((v, i) => (i ? parseFloat(v ?? 1) : v))
        return [[0.25, 0.45], [0.55, 0.3], [0.9, 0.18]].map(([step, alpha]) =>
          `rgba(${r}, ${g}, ${b}, ${(a * alpha).toFixed(3)}) ${x * step}px ${y * step}px 0px ${spread + blur * step * 0.3}px`)
      })
      if (changed) el.style.boxShadow = layers.join(', ')
    }
  })
}

// File access lets the page read the local pictures it scales down.
const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] })
for (const lang of LANGS) {
  mkdirSync(join(DIST, lang), { recursive: true })
  mkdirSync(join(DIST, 'previews', lang), { recursive: true })
  mkdirSync(join(BUILD, lang), { recursive: true })

  for (const doc of PRINT) {
    if (ONLY && !ONLY.includes(doc.key)) continue
    const html = await doc.make(lang)
    const source = join(BUILD, lang, `${doc.key}.html`)
    writeFileSync(source, html)
    const page = await browser.newPage({ deviceScaleFactor: 1.5 })
    await page.goto(pathToFileURL(source).href)
    await ready(page)
    // Previews show the design as written; the PDF gets the lighter version.
    const sheets = page.locator('.sheet')
    const count = await sheets.count()
    for (let i = 0; i < count; i++) {
      await sheets.nth(i).screenshot({ path: join(DIST, 'previews', lang, `${doc.key}-${i + 1}.jpg`), type: 'jpeg', quality: 80 })
    }
    await shrinkImages(page, doc.dpi)
    await sharpenShadows(page)
    await flattenGradients(page)
    await page.pdf({ path: join(DIST, lang, doc.file), printBackground: true, preferCSSPageSize: true })
    await page.close()
    console.log(`${lang} ${doc.file} (${count} pages)`)
  }

  for (const doc of SOCIAL) {
    if (ONLY && !ONLY.includes(doc.key)) continue
    const source = join(BUILD, lang, `${doc.key}.html`)
    writeFileSync(source, await doc.make(lang))
    const page = await browser.newPage({ viewport: { width: doc.width, height: doc.height } })
    await page.goto(pathToFileURL(source).href)
    await ready(page)
    await page.locator('.sheet').first().screenshot({ path: join(DIST, lang, doc.file) })
    await page.close()
    console.log(`${lang} ${doc.file}`)
  }
}
await browser.close()
