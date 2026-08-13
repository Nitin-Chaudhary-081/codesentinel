import { test, expect } from '@playwright/test';
import { AuthPage, DashboardPage } from './pages/auth.page';

const API_BASE = process.env.E2E_API_URL || 'http://127.0.0.1:8000';

test.describe('CodeSentinel E2E', () => {
  test('TEST 1: register -> login -> submit Python -> see report', async ({ page }) => {
    const email = `e2e_${Date.now()}@test.com`;
    const auth = new AuthPage(page);
    await auth.goto();
    await auth.register(email, 'password123');
    await auth.expectDashboard();

    const dash = new DashboardPage(page);
    await dash.submitCode('def add(a, b):\n    return a + b\n', 'python');
    await dash.selectFirstSubmission();
    await dash.runEvaluation();
    await page.getByText('Syntax OK').waitFor();
    await expect(page.getByText(/\d+\/10/).first()).toBeVisible();
  });

  test('TEST 2: submit TypeScript -> download JSONL export', async ({ page }) => {
    const email = `e2e_ts_${Date.now()}@test.com`;
    const auth = new AuthPage(page);
    await auth.goto();
    await auth.register(email, 'password123');
    await auth.expectDashboard();

    const dash = new DashboardPage(page);
    await dash.submitCode(
      'function add(a: number, b: number): number {\n    return a + b;\n}\n',
      'typescript',
    );
    await dash.selectFirstSubmission();
    await dash.runEvaluation();
    await page.getByText('Syntax OK').waitFor();

    const content = await dash.exportJsonl();
    expect(content).toContain('"language": "typescript"');
    expect(content).toContain('"overall_score"');
  });

  test('TEST 3: unauthenticated user hits protected endpoint -> 401', async ({ request }) => {
    const resp = await request.get(`${API_BASE}/api/v1/submissions`);
    expect(resp.status()).toBe(401);
    const body = await resp.json();
    expect(body.error_type).toBe('unauthorized');
  });

  test('TEST 4: invalid input -> typed error, not crash', async ({ page }) => {
    const email = `e2e_bad_${Date.now()}@test.com`;
    const auth = new AuthPage(page);
    await auth.goto();
    await auth.register(email, 'password123');
    await auth.expectDashboard();

    const dash = new DashboardPage(page);
    await dash.submitCode('def f(:\n    broken', 'python');
    await dash.selectFirstSubmission();
    await dash.runEvaluation();
    await page.getByText('Syntax Error', { exact: true }).waitFor();
  });
});
