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

const PRINT = [
  { key: 'menu', file: 'speisekarte-a4.pdf', make: menuDocument },
  { key: 'flyer', file: 'flyer-a5.pdf', make: flyerDocument },
  { key: 'postcard', file: 'postkarte-a6.pdf', make: postcardDocument },
  { key: 'poster', file: 'plakat-a3.pdf', make: posterDocument },
  { key: 'guide', file: 'kundeninfo-a4.pdf', make: guideDocument },
  { key: 'handbook', file: 'handbuch-a4.pdf', make: handbookDocument }
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

const browser = await chromium.launch()
for (const lang of LANGS) {
  mkdirSync(join(DIST, lang), { recursive: true })
  mkdirSync(join(DIST, 'previews', lang), { recursive: true })
  mkdirSync(join(BUILD, lang), { recursive: true })

  for (const doc of PRINT) {
    if (ONLY && !ONLY.includes(doc.key)) continue
    const html = await doc.make(lang)
    const source = join(BUILD, lang, `${doc.key}.html`)
    writeFileSync(source, html)
    const page = await browser.newPage({ deviceScaleFactor: 1 })
    await page.goto(pathToFileURL(source).href)
    await ready(page)
    await page.pdf({ path: join(DIST, lang, doc.file), printBackground: true, preferCSSPageSize: true })
    // Previews of each page at screen resolution.
    const sheets = page.locator('.sheet')
    const count = await sheets.count()
    for (let i = 0; i < count; i++) {
      await sheets.nth(i).screenshot({ path: join(DIST, 'previews', lang, `${doc.key}-${i + 1}.jpg`), type: 'jpeg', quality: 80 })
    }
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
