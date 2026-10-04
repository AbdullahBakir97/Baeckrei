import { test as base, expect } from '@playwright/test'
import account from './account.cjs'

// Every page: skip the first-visit intro and fail the test on page errors.
export const test = base.extend({
  page: async ({ page }, use) => {
    const errors = []
    // Frames without storage (e.g. a preview while it starts) skip this.
    await page.addInitScript(() => { try { localStorage.setItem('intro-seen', '1') } catch { /* no storage here */ } })
    page.on('pageerror', (error) => errors.push(String(error)))
    await use(page)
    expect(errors, 'uncaught errors on the page').toEqual([])
  }
})

export { expect, account }

export async function signIn(page) {
  await page.goto('/login')
  const form = page.locator('form').filter({ has: page.getByRole('button', { name: 'Sign in' }) })
  await form.getByLabel('Email address').fill(account.email)
  await form.getByLabel('Password', { exact: true }).fill(account.password)
  await form.getByRole('button', { name: 'Sign in' }).click()
  await expect(page).not.toHaveURL(/\/login/)
}

export async function signInAsOwner(page) {
  await page.goto('/login')
  const form = page.locator('form').filter({ has: page.getByRole('button', { name: 'Sign in' }) })
  await form.getByLabel('Email address').fill(account.admin.email)
  await form.getByLabel('Password', { exact: true }).fill(account.admin.password)
  await form.getByRole('button', { name: 'Sign in' }).click()
  await expect(page).toHaveURL(/\/admin/)
}

/** Open a product from the shop by clicking its name. */
export async function openProduct(page, name) {
  await page.goto('/products')
  await page.locator('.pcard-title').getByRole('link', { name, exact: true }).click()
  await expect(page.getByRole('heading', { name, level: 1 })).toBeVisible()
}
