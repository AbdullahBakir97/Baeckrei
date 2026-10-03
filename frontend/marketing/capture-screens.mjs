// Screenshots of every customer page of the shop, in German and English, for
// the customer guide (marketing/build.mjs). Run against a shop with some
// products and a customer account that has placed an order:
//
//   node marketing/capture-screens.mjs --base http://localhost:5173 \
//     --email kunde@example.com --password '...'
//
// Writes marketing/assets/screens/<de|en>/<page>.jpg (desktop) and
// marketing/assets/screens/<de|en>/mobile-<page>.jpg.
import { chromium } from '@playwright/test'
import { mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean)
  .map(pair => pair.trim().split(/\s+/)).map(([k, ...v]) => [k, v.join(' ')]))
const BASE = (args.base || 'http://localhost:5173').replace(/\/$/, '')
const EMAIL = args.email
const PASSWORD = args.password
const ONLY = args.only ? args.only.split(',') : null
const OUT = join(dirname(fileURLToPath(import.meta.url)), 'assets', 'screens')
const LANGS = (args.langs || 'de,en').split(',')

const wait = (page, ms) => page.waitForTimeout(ms)

async function settle(page, ms = 1800) {
  await page.waitForLoadState('networkidle').catch(() => {})
  await wait(page, ms)
}

async function shot(page, lang, name, { mobile = false } = {}) {
  if (ONLY && !ONLY.includes(name)) return
  const file = join(OUT, lang, `${mobile ? 'mobile-' : ''}${name}.jpg`)
  mkdirSync(dirname(file), { recursive: true })
  await page.screenshot({ path: file, type: 'jpeg', quality: 82 })
  console.log(lang, mobile ? 'mobile' : 'desktop', name)
}

async function open(page, path, ms) {
  await page.goto(BASE + path)
  await settle(page, ms)
}

async function signIn(page) {
  await open(page, '/login', 800)
  const form = page.locator('form').filter({ has: page.locator('button[type=submit]') }).first()
  await form.locator('input[type=email]').fill(EMAIL)
  await form.locator('input[type=password]').fill(PASSWORD)
  await form.locator('button[type=submit]').click()
  await page.waitForURL(url => !url.pathname.startsWith('/login'), { timeout: 15000 })
  await settle(page, 1000)
}

async function firstProductPath(page) {
  await open(page, '/products', 1500)
  return page.locator('.pcard-title a').first().getAttribute('href')
}

async function desktop(browser, lang) {
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.25, locale: lang === 'de' ? 'de-DE' : 'en-GB',
    timezoneId: 'Europe/Berlin', reducedMotion: 'reduce'
  })
  await ctx.addInitScript((l) => { localStorage.setItem('locale', l); localStorage.setItem('intro-seen', '1') }, lang)
  const page = await ctx.newPage()

  // Public pages
  await open(page, '/', 3500); await shot(page, lang, 'home')
  await open(page, '/products', 2500); await shot(page, lang, 'shop')
  await open(page, '/seasonal', 2000); await shot(page, lang, 'seasonal')
  await open(page, '/categories/pastries', 2000); await shot(page, lang, 'category')
  const productPath = await firstProductPath(page)
  await open(page, productPath, 6000); await shot(page, lang, 'product')
  // Save to wishlist and compare, then add to the cart.
  await page.locator('.pd-actions button').nth(0).click().catch(() => {})
  await page.locator('.pd-actions button').nth(1).click().catch(() => {})
  const second = await (async () => {
    await open(page, '/products', 1200)
    return page.locator('.pcard-title a').nth(1).getAttribute('href')
  })()
  await open(page, second, 2500)
  await page.locator('.pd-actions button').nth(1).click().catch(() => {})
  await page.getByRole('button', { name: /Warenkorb|Add to cart/ }).first().click().catch(() => {})
  await wait(page, 1500)
  await open(page, '/blog', 2000); await shot(page, lang, 'journal')
  const post = await page.locator('a[href^="/blog/"]').first().getAttribute('href').catch(() => null)
  if (post) { await open(page, post, 2000); await shot(page, lang, 'journal-post') }
  await open(page, '/about', 2500); await shot(page, lang, 'about')
  await open(page, '/contact', 2000); await shot(page, lang, 'contact')
  await open(page, '/wishlist', 2000); await shot(page, lang, 'wishlist')
  await open(page, '/compare', 2000); await shot(page, lang, 'compare')
  await open(page, '/cart', 2000); await shot(page, lang, 'cart')
  await open(page, '/impressum', 1500); await shot(page, lang, 'impressum')
  await open(page, '/privacy', 1500); await shot(page, lang, 'privacy')
  await open(page, '/terms', 1500); await shot(page, lang, 'terms')
  await open(page, '/cookie-policy', 1500); await shot(page, lang, 'cookies')
  await open(page, '/this-page-does-not-exist', 1500); await shot(page, lang, 'not-found')
  await open(page, '/register', 1500); await shot(page, lang, 'register')
  await open(page, '/forgot-password', 1500); await shot(page, lang, 'forgot-password')
  await open(page, '/login', 1500); await shot(page, lang, 'login')

  // Customer pages
  await signIn(page)
  await open(page, '/checkout', 2500); await shot(page, lang, 'checkout')
  await page.locator('.slot-days .slot-chip').nth(1).click().catch(() => {})
  await page.locator('.slot-times .slot-chip:not([disabled])').nth(3).click().catch(() => {})
  await page.mouse.wheel(0, 500); await wait(page, 800); await shot(page, lang, 'checkout-time')
  await open(page, '/orders', 2000); await shot(page, lang, 'orders')
  const order = await page.locator('a[href^="/orders/"]').first().getAttribute('href').catch(() => null)
  if (order) { await open(page, `${order}?placed=1`, 2500); await shot(page, lang, 'order') }
  await open(page, '/profile', 2000); await shot(page, lang, 'profile')
  await open(page, '/settings', 2000); await shot(page, lang, 'settings')
  await ctx.close()

  // The in-shop screen
  const tv = await browser.newContext({ viewport: { width: 1920, height: 1080 }, timezoneId: 'Europe/Berlin' })
  const board = await tv.newPage()
  await board.goto(`${BASE}/menu-board?lang=${lang}`); await wait(board, 4000)
  await shot(board, lang, 'menu-board')
  await tv.close()
}

async function mobile(browser, lang) {
  const ctx = await browser.newContext({
    viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true,
    locale: lang === 'de' ? 'de-DE' : 'en-GB', timezoneId: 'Europe/Berlin', reducedMotion: 'reduce'
  })
  await ctx.addInitScript((l) => { localStorage.setItem('locale', l); localStorage.setItem('intro-seen', '1') }, lang)
  const page = await ctx.newPage()
  await open(page, '/', 3000); await shot(page, lang, 'home', { mobile: true })
  await open(page, '/products', 2500); await shot(page, lang, 'shop', { mobile: true })
  const productPath = await page.locator('.pcard-title a').first().getAttribute('href')
  await open(page, productPath, 5000); await shot(page, lang, 'product', { mobile: true })
  await page.locator('.nav-burger').tap(); await wait(page, 1500); await shot(page, lang, 'menu', { mobile: true })
  await ctx.close()
}

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] })
for (const lang of LANGS) {
  await desktop(browser, lang)
  await mobile(browser, lang)
}
await browser.close()
