import { api } from '@/lib/api';

describe('api.request transport', () => {
  afterEach(() => {
    delete (global as any).fetch;
  });

  it('returns data on ok response', async () => {
    (global as any).fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ status: 'ok', data: { id: 1 } }),
    });
    const r = await api.login('a@b.com', 'password123');
    expect(r).toEqual({ id: 1 });
  });

  it('throws on error envelope', async () => {
    (global as any).fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ status: 'error', error_type: 'invalid_credentials', message: 'bad' }),
    });
    await expect(api.login('a@b.com', 'x')).rejects.toThrow('bad');
  });

  it('exportReport resolves raw text', async () => {
    (global as any).fetch = jest.fn().mockResolvedValue({
      text: async () => 'jsonl-line',
    });
    const text = await api.exportReport(1, 'jsonl', 'tok');
    expect(text).toBe('jsonl-line');
  });
});
