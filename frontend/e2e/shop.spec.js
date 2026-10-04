import { test, expect, account, openProduct, signIn } from './fixtures'

test('home page is served with its meta tags and renders', async ({ page, request }) => {
  const html = await (await request.get('/')).text()
  expect(html).toContain('<title>Backlover')
  expect(html).toContain('property="og:title"')

  await page.goto('/')
  await expect(page.locator('h1').first()).toBeVisible()
  await expect(page.getByRole('link', { name: 'Shop' }).first()).toBeVisible()
})

test('the language menu switches between English, German and Arabic', async ({ page }) => {
  await page.goto('/products')
  await page.getByRole('button', { name: 'Language: English' }).click()
  await page.getByRole('menuitemradio', { name: 'Deutsch' }).click()
  await expect(page.locator('html')).toHaveAttribute('lang', 'de')
  await expect(page.getByRole('link', { name: 'Über uns' }).first()).toBeVisible()
  await expect(page.getByText('Roggenbrot').first()).toBeVisible()

  await page.getByRole('button', { name: 'Sprache: Deutsch' }).click()
  await page.getByRole('menuitemradio', { name: 'العربية' }).click()
  await expect(page.locator('html')).toHaveAttribute('lang', 'ar')
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl')
  await expect(page.getByRole('link', { name: 'من نحن' }).first()).toBeVisible()
  // Arabic pages show the English product names; prices keep Western digits.
  await expect(page.getByText('Rye bread').first()).toBeVisible()

  // The choice is remembered on the next visit.
  await page.reload()
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl')
})

test('an Arabic link opens the site right to left', async ({ page, request }) => {
  const html = await (await request.get('/about?lang=ar')).text()
  expect(html).toContain('<html lang="ar" dir="rtl">')
  await page.goto('/about?lang=ar')
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl')
  await expect(page.getByRole('navigation', { name: 'التنقل الرئيسي' })).toBeVisible()
})

test('product pages have their own title for search engines', async ({ page, request }) => {
  await openProduct(page, 'Rye bread')
  const html = await (await request.get(page.url())).text()
  expect(html).toMatch(/<title>[^<]*Roggenbrot|<title>[^<]*Rye bread/)
})

test('a guest keeps their cart between pages', async ({ page }) => {
  await openProduct(page, 'Butter croissant')
  await page.getByRole('button', { name: /Add to cart/ }).click()
  await expect(page.locator('#nav-cart')).toContainText('1')

  await page.goto('/cart')
  await expect(page.getByText('Butter croissant').first()).toBeVisible()
  await page.reload()
  await expect(page.getByText('Butter croissant').first()).toBeVisible()
})

test('a guest signs in at checkout and keeps the cart', async ({ page }) => {
  await openProduct(page, 'Spelt wholemeal bread')
  await page.getByRole('button', { name: /Add to cart/ }).click()
  await page.goto('/cart')
  await page.getByRole('link', { name: /Checkout/ }).click()

  await expect(page).toHaveURL(/\/login\?redirect=/)
  const form = page.locator('form').filter({ has: page.getByRole('button', { name: 'Sign in' }) })
  await form.getByLabel('Email address').fill(account.email)
  await form.getByLabel('Password', { exact: true }).fill(account.password)
  await form.getByRole('button', { name: 'Sign in' }).click()

  await expect(page).toHaveURL(/\/checkout/)
  await expect(page.getByText('Spelt wholemeal bread').first()).toBeVisible()
})

test('a customer orders for pickup at a chosen time and pays in the shop', async ({ page }) => {
  await signIn(page)
  await openProduct(page, 'Cheesecake')
  await page.getByRole('button', { name: /Add to cart/ }).click()
  await expect(page.locator('#nav-cart')).toContainText('1')

  await page.goto('/checkout')
  // A pickup time is picked for the customer; choose a later one.
  const times = page.locator('.slot-times button:not([disabled])')
  await expect(times.first()).toBeVisible()
  await times.nth(2).click()
  const chosen = (await times.nth(2).textContent()).trim()
  await expect(page.getByText(`Pickup: `, { exact: false })).toContainText(chosen)

  await page.getByRole('button', { name: /Cash on pickup/ }).click()
  await page.getByRole('button', { name: /^Place order/ }).click()

  await expect(page).toHaveURL(/\/orders\/\d+\?placed=1/)
  await expect(page.getByText('Thank you! Your order has been placed.')).toBeVisible()
  await expect(page.getByText(new RegExp(`Requested for .*${chosen}`))).toBeVisible()
  await expect(page.locator('#nav-cart')).toContainText('0')
})

test('online payment is only offered once Stripe is set up', async ({ page }) => {
  await signIn(page)
  await openProduct(page, 'Cinnamon roll')
  await page.getByRole('button', { name: /Add to cart/ }).click()
  await page.goto('/checkout')
  const online = page.getByRole('button', { name: /Card online/ })
  await expect(online).toBeDisabled()
  await expect(online).toContainText('Coming soon')
})

test('the menu board shows the live menu full screen', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 })
  await page.goto('/menu-board')
  // No shop navigation on the screen; products and prices are listed.
  await expect(page.locator('nav.nav')).toHaveCount(0)
  await expect(page.locator('.menu-item').first()).toBeVisible()
  await expect(page.locator('.menu-item', { hasText: 'Roggenbrot' })).toContainText('4,20 €')
  await expect(page.locator('.board-open')).toBeVisible()
  await expect(page.locator('.board-qr img')).toBeVisible()
})
