import { test, expect } from '@playwright/test';
import { AuthPage, DashboardPage } from './pages/auth.page';

const API = process.env.E2E_API_URL || 'http://127.0.0.1:8000';

test('visual capture + demo flow', async ({ page }, testInfo) => {
  const email = `demo_${Date.now()}@test.com`;
  const auth = new AuthPage(page);
  await auth.goto();
  await page.screenshot({ path: 'e2e/artifacts/01-landing.png', fullPage: true });

  await auth.register(email, 'password123');
  await auth.expectDashboard();
  await page.screenshot({ path: 'e2e/artifacts/02-dashboard-form.png', fullPage: true });

  const dash = new DashboardPage(page);
  // Submit Python code WITH a real bug (no error handling around file I/O)
  await dash.submitCode(
    'def read_config(path):\n    f = open(path)\n    return f.read()\n',
    'python',
  );
  await dash.selectFirstSubmission();
  await page.screenshot({ path: 'e2e/artifacts/03-history.png', fullPage: true });

  await dash.runEvaluation();
  await page.getByText('Syntax OK').waitFor();
  await page.screenshot({ path: 'e2e/artifacts/04-report.png', fullPage: true });

  // Sanity: report shows scores
  await expect(page.getByText(/\d+\/10/).first()).toBeVisible();

  // Save the OpenAPI/spec page and coverage as separate artifacts is done outside.
  console.log(`DEMO_VIDEO_DIR=${testInfo.outputDir}`);
});
