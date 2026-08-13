import { Page } from '@playwright/test';

/** Page Object for the login/register screen. */
export class AuthPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/');
  }

  async register(email: string, password: string) {
    const toggle = this.page.getByText(/Need an account\? Register/);
    if (await toggle.isVisible().catch(() => false)) await toggle.click();
    await this.page.getByPlaceholder('Email').fill(email);
    await this.page.getByPlaceholder('Password').fill(password);
    await this.page.getByRole('button', { name: 'Register' }).click();
  }

  async login(email: string, password: string) {
    await this.page.getByPlaceholder('Email').fill(email);
    await this.page.getByPlaceholder('Password').fill(password);
    await this.page.getByRole('button', { name: 'Login' }).click();
  }

  async expectDashboard() {
    await this.page.getByText('Submit Code').waitFor();
  }
}

/** Page Object for the post-login dashboard (submit / history / report). */
export class DashboardPage {
  constructor(private page: Page) {}

  async submitCode(code: string, language: string) {
    await this.page.locator('textarea').fill(code);
    await this.page.locator('select').selectOption(language);
    await this.page.getByRole('button', { name: 'Submit for Review' }).click();
  }

  async selectFirstSubmission() {
    await this.page.getByText(/^#\d+ —/).first().waitFor();
    await this.page.getByText(/^#\d+ —/).first().click();
  }

  async runEvaluation() {
    await this.page.getByRole('button', { name: 'Run Evaluation' }).click();
    await this.page
      .getByText('Syntax OK')
      .or(this.page.getByText('Syntax Error'))
      .or(this.page.getByText('Type Error'))
      .first()
      .waitFor();
  }

  async exportJsonl(): Promise<string> {
    const [download] = await Promise.all([
      this.page.waitForEvent('download'),
      this.page.getByRole('button', { name: 'Export JSONL' }).click(),
    ]);
    const suggested = download.suggestedFilename();
    const fs = await import('fs/promises');
    const content = await fs.readFile(await download.path(), 'utf-8');
    return content;
  }
}
