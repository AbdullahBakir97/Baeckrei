import { test, expect, signInAsOwner } from './fixtures'

// The bakery runs everything from its own admin ("Studio").

test('the owner sets a shop notice and a closing day', async ({ page, request }) => {
  await signInAsOwner(page)
  await page.goto('/admin/settings')
  await page.getByLabel('Show the notice').check({ force: true })
  await page.locator('#set-ann').fill('Heute frische Brezeln!')
  await page.locator('#set-ann-en').fill('Fresh pretzels today!')
  await page.getByRole('button', { name: 'Save changes' }).click()
  await expect(page.getByText(/Last saved/)).toBeVisible()

  const next = new Date(Date.now() + 3 * 864e5).toISOString().slice(0, 10)
  await page.locator('#cl-start').fill(next)
  await page.locator('#cl-label').fill('Inventory')
  await page.getByRole('button', { name: 'Add', exact: true }).click()
  await expect(page.getByText('Inventory')).toBeVisible()

  const info = await (await request.get('/api/shop/info/')).json()
  expect(info.announcement_en).toBe('Fresh pretzels today!')
  expect(info.hours.closures[0].label).toBe('Inventory')

  await page.goto('/products')
  await expect(page.getByRole('status').getByText('Fresh pretzels today!')).toBeVisible()
})

test('the owner writes and publishes a journal post', async ({ page }) => {
  await signInAsOwner(page)
  await page.goto('/admin/journal/new')
  await page.getByLabel('Title').fill('Our sourdough turns ten')
  await page.getByLabel(/^Text/).fill('Ten years ago we fed it for the first time.\n\nIt still bakes every loaf.')
  await page.getByText('Publish', { exact: true }).click()
  await page.getByRole('button', { name: 'Publish' }).last().click()
  await expect(page.getByText('Published and visible in the shop.')).toBeVisible()

  await page.goto('/blog')
  await expect(page.getByText('Our sourdough turns ten').first()).toBeVisible()
})

test('the owner answers a contact message from the inbox', async ({ page, request }) => {
  const sent = await request.post('/api/content/contact/', {
    data: { name: 'Mia Example', email: 'mia@example.com', subject: 'Birthday cake', message: 'Can I order a cake for Saturday?' }
  })
  expect(sent.ok()).toBeTruthy()
  await signInAsOwner(page)
  await page.goto('/admin/messages')
  await page.getByRole('button', { name: /Mia Example/ }).click()
  await expect(page.getByText('Can I order a cake for Saturday?').last()).toBeVisible()
  await page.getByLabel('Reply', { exact: true }).fill('Hello Mia,\n\nof course – see you on Saturday!')
  await page.getByRole('button', { name: 'Send reply' }).click()
  await expect(page.getByText('Reply sent to mia@example.com.')).toBeVisible()
  await expect(page.getByText(/Answered by/)).toBeVisible()
})

test('the owner sends a newsletter', async ({ page, request }) => {
  await request.post('/api/content/newsletter/', { data: { email: 'fan@example.com' } })
  await signInAsOwner(page)
  await page.goto('/admin/newsletter')
  await page.getByRole('button', { name: 'New newsletter' }).click()
  await page.getByLabel('Subject').fill('New this autumn')
  await page.getByLabel(/^Text/).fill('Pumpkin bread is back.')
  await page.getByRole('button', { name: /^Send to \d+/ }).click()
  await page.getByRole('button', { name: 'Send now' }).click()
  await expect(page.getByText(/Sent to \d+ subscribers/).first()).toBeVisible()
})

test('the owner adds the EU allergens and an ingredient', async ({ page }) => {
  await signInAsOwner(page)
  await page.goto('/admin/ingredients')
  await page.getByRole('button', { name: /Add the 14 main EU allergens/ }).click()
  await expect(page.locator('.allergen-list')).toContainText('Sesame')
  await page.getByRole('button', { name: 'Add ingredient' }).click()
  await page.getByLabel('Name', { exact: true }).fill('Sesame seeds')
  await page.locator('.pick').filter({ hasText: 'Sesame' }).click()
  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await expect(page.getByRole('cell', { name: 'Sesame seeds' })).toBeVisible()
})

test('the owner designs a menu screen and a TV opens it with its code', async ({ page, context }) => {
  await signInAsOwner(page)
  await page.goto('/admin/screens')
  await page.getByRole('button', { name: 'Create the first screen' }).click()
  await expect(page).toHaveURL(/\/admin\/screens\/\d+/)
  await page.getByRole('button', { name: /Photo tiles/ }).click()
  await page.getByRole('button', { name: /Paper \(light\)/ }).click()
  await page.getByRole('tab', { name: 'Content' }).click()
  await page.locator('#sc-tick').fill('Fresh pretzels every morning')
  await page.getByRole('button', { name: 'Save & go live' }).click()
  await expect(page.getByText('All saved and live')).toBeVisible()
  const code = (await page.locator('.st-chip', { hasText: 'Code' }).textContent()).replace(/\D/g, '')

  const tv = await context.newPage()
  await tv.setViewportSize({ width: 1920, height: 1080 })
  await tv.goto('/tv')
  await tv.getByLabel('Screen code').fill(code)
  await expect(tv).toHaveURL(/\/menu-board\/counter/)
  await expect(tv.locator('.board-ticker')).toContainText('Fresh pretzels every morning')
  await expect(tv.locator('.grid-card').first()).toBeVisible()

  // The TV remembers its screen.
  await tv.goto('/tv')
  await expect(tv.getByText(/This device shows “Counter”/)).toBeVisible()
})
