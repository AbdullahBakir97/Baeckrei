// Screenshots of every customer page of the shop, in German and English, for
// the customer guide (marketing/build.mjs). Run against a shop with some
// products and a customer account that has placed an order:
//
//   node marketing/capture-screens.mjs --base http://localhost:5173 \
//     --email kunde@example.com --password '...'
//
// Writes marketing/assets/screens/<de|en>/<page>.jpg (desktop) and
// marketing/assets/screens/<de|en>/mobile-<page>.jpg.
//
// With --admin-email and --admin-password (a superuser) it takes the admin
// pages for the owner handbook instead (admin-*.jpg), including Django's own
// admin at --api (default http://localhost:8000).
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
const ADMIN_EMAIL = args['admin-email']
const ADMIN_PASSWORD = args['admin-password']
const API = (args.api || 'http://localhost:8000').replace(/\/$/, '')
const DJANGO_ADMIN = args['django-admin'] || '/django-admin/'

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

async function signIn(page, email = EMAIL, password = PASSWORD) {
  await open(page, '/login', 800)
  await page.waitForSelector('input[type=password]')
  const form = page.locator('form').filter({ has: page.locator('button[type=submit]') }).first()
  await form.locator('input[type=email]').fill(email)
  await form.locator('input[type=password]').fill(password)
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

async function admin(browser, lang) {
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.25, locale: lang === 'de' ? 'de-DE' : 'en-GB',
    timezoneId: 'Europe/Berlin', reducedMotion: 'reduce'
  })
  await ctx.addInitScript((l) => { localStorage.setItem('locale', l); localStorage.setItem('intro-seen', '1') }, lang)
  const page = await ctx.newPage()
  const closeDialog = () => page.keyboard.press('Escape').then(() => wait(page, 500))
  await signIn(page, ADMIN_EMAIL, ADMIN_PASSWORD)

  await open(page, '/admin', 2500); await shot(page, lang, 'admin-dashboard')
  await open(page, '/admin/products', 2500); await shot(page, lang, 'admin-products')
  // The edit form of the first product
  await page.getByTitle(/^(Bearbeiten|Edit)$/).nth(1).click()
  await wait(page, 1200); await shot(page, lang, 'admin-product-form')
  await open(page, '/admin/products', 2000)
  await page.getByTitle(/^(Details anzeigen|View details)$/).nth(1).click()
  await settle(page, 2000); await shot(page, lang, 'admin-product-detail')
  await open(page, '/admin/categories', 2000); await shot(page, lang, 'admin-categories')
  await page.getByRole('button', { name: /Kategorie hinzufügen|Add category/ }).click()
  await wait(page, 1000); await shot(page, lang, 'admin-category-form')
  await closeDialog()
  await open(page, '/admin/orders', 2000); await shot(page, lang, 'admin-orders')
  await page.getByRole('button', { name: 'Details' }).first().click()
  await wait(page, 1500); await shot(page, lang, 'admin-order')
  await closeDialog()
  await open(page, '/admin/users', 2000); await shot(page, lang, 'admin-users')

  // A new order coming in: the next check of recent orders gets one more.
  let calls = 0
  await page.route('**/api/orders/orders/recent_orders/**', async (route) => {
    const response = await route.fetch()
    const data = await response.json()
    calls += 1
    if (calls > 1) data.unshift({ ...data[0], id: 'incoming', order_number: 'ORD-20261003-4F2A91C7' })
    await route.fulfill({ response, json: data })
  })
  await open(page, '/admin/orders', 2500)
  await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')))
  await wait(page, 1500); await shot(page, lang, 'admin-new-order')
  await page.unroute('**/api/orders/orders/recent_orders/**')

  // Django's admin for the journal, messages and newsletter
  await page.goto(`${API}${DJANGO_ADMIN}login/`)
  await page.fill('input[name=username]', ADMIN_EMAIL)
  await page.fill('input[name=password]', ADMIN_PASSWORD)
  await page.click('input[type=submit]')
  await settle(page, 800)
  for (const [name, path] of [['posts', 'content/post/'], ['post-form', 'content/post/add/'],
    ['messages', 'content/contactmessage/'], ['newsletter', 'content/newslettersubscriber/']]) {
    await page.goto(`${API}${DJANGO_ADMIN}${path}`); await settle(page, 600)
    await shot(page, lang, `admin-django-${name}`)
  }
  await ctx.close()

  // The admin on a phone
  const phoneCtx = await browser.newContext({
    viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true,
    locale: lang === 'de' ? 'de-DE' : 'en-GB', timezoneId: 'Europe/Berlin', reducedMotion: 'reduce'
  })
  await phoneCtx.addInitScript((l) => { localStorage.setItem('locale', l); localStorage.setItem('intro-seen', '1') }, lang)
  const phonePage = await phoneCtx.newPage()
  await signIn(phonePage, ADMIN_EMAIL, ADMIN_PASSWORD)
  await open(phonePage, '/admin', 2500); await shot(phonePage, lang, 'admin-dashboard', { mobile: true })
  await open(phonePage, '/admin/orders', 2500); await shot(phonePage, lang, 'admin-orders', { mobile: true })
  await phoneCtx.close()
}

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] })
for (const lang of LANGS) {
  if (ADMIN_EMAIL) {
    await admin(browser, lang)
  } else {
    await desktop(browser, lang)
    await mobile(browser, lang)
  }
}
await browser.close()
