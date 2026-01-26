import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './',
  timeout: 30 * 1000,
  retries: 0,
  use: {
    baseURL: process.env.SWA_BASE_URL || 'http://localhost:4280',
    trace: 'off',
    video: 'off',
    screenshot: 'off'
  },
  projects: [
    {
      name: 'Chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
});
