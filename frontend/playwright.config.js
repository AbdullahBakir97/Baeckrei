import { defineConfig, devices } from '@playwright/test'

// End-to-end tests against the production setup: the built storefront
// (npm run build) served by Django with DEBUG off, on a fresh database with
// the demo bakery (see e2e/serve.sh).
//   npm run build && npm run test:e2e
const PORT = process.env.E2E_PORT || 8765

export default defineConfig({
  testDir: 'e2e',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: `http://localhost:${PORT}`,
    locale: 'en-GB',
    timezoneId: 'Europe/Berlin',
    contextOptions: { reducedMotion: 'reduce' },
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    ...devices['Desktop Chrome']
  },
  webServer: {
    command: `sh e2e/serve.sh ${PORT}`,
    url: `http://localhost:${PORT}/api/products/`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    stdout: 'ignore',
    stderr: 'pipe'
  }
})
