import { expect, test } from '@playwright/test'

test('opens the scaffold home page', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'LearnFlow' })).toBeVisible()
  await expect(page.getByText('个人学习工作台')).toBeVisible()
})
