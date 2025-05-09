import { test, expect } from '@playwright/test';

test('handles session expiry and refresh', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  await page.waitForURL('/dashboard');

  await page.evaluate(() => {
    const cookies = document.cookie.split(';');
    const authToken = cookies.find(c => c.trim().startsWith('auth_token='));
    document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    const expiredDate = new Date();
    expiredDate.setMinutes(expiredDate.getMinutes() - 10);
    document.cookie = `auth_token=${authToken?.split('=')[1]}; expires=${expiredDate.toUTCString()}; path=/;`;
  });

  await page.waitForSelector('[data-testid="refresh-data"]:not([disabled])', { timeout: 5000 });
  await page.click('[data-testid="refresh-data"]');
  await page.waitForTimeout(200);
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('[data-testid="data-container"]')).toHaveText('Hello from the API!');
});
