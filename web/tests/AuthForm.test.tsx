import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider } from '@/lib/auth';
import Home from '@/app/page';

jest.mock('@/lib/api', () => ({
  LANGUAGES: [],
  api: {
    register: jest.fn(),
    login: jest.fn(),
    createSubmission: jest.fn(),
    listSubmissions: jest.fn().mockResolvedValue([]),
    getSubmission: jest.fn(),
    runEvaluation: jest.fn(),
    exportReport: jest.fn(),
  },
}));

import { api } from '@/lib/api';

describe('AuthForm (page)', () => {
  beforeEach(() => jest.clearAllMocks());

  function pullCord() {
    fireEvent.click(screen.getByRole('button', { name: 'Turn lamp on' }));
  }

  it('registers then logs in and shows dashboard', async () => {
    (api.register as jest.Mock).mockResolvedValue({});
    (api.login as jest.Mock).mockResolvedValue({ access_token: 'tok' });

    render(
      <AuthProvider>
        <Home />
      </AuthProvider>,
    );

    pullCord();
    fireEvent.click(screen.getByText(/Need an account\? Register/));
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'a@b.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Register' }));

    await waitFor(() => expect(api.register).toHaveBeenCalled());
    await waitFor(() => expect(screen.getByText('Submit Code')).toBeInTheDocument());
  });

  it('hides login fields until the lamp cord is pulled', () => {
    render(
      <AuthProvider>
        <Home />
      </AuthProvider>,
    );

    expect(screen.queryByPlaceholderText('Email')).not.toBeInTheDocument();
    expect(screen.queryByPlaceholderText('Password')).not.toBeInTheDocument();
    expect(
      screen.getByText(/login menu stays hidden until you pull the lamp cord/),
    ).toBeInTheDocument();

    pullCord();
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Turn lamp off' }));
    expect(screen.queryByPlaceholderText('Email')).not.toBeInTheDocument();
  });

  it('shows error on failed login', async () => {
    const err = Object.assign(new Error('Invalid email or password'), {
      apiError: { error_type: 'invalid_credentials', message: 'Invalid email or password' },
    });
    (api.login as jest.Mock).mockRejectedValue(err);

    render(
      <AuthProvider>
        <Home />
      </AuthProvider>,
    );

    pullCord();
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'a@b.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Login' }));

    await waitFor(() =>
      expect(screen.getByText('Invalid email or password')).toBeInTheDocument(),
    );
  });
});
