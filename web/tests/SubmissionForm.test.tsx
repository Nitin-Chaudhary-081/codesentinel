import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SubmissionForm from '@/components/SubmissionForm';

jest.mock('@/lib/api', () => ({
  LANGUAGES: [
    { value: 'python', label: 'Python' },
    { value: 'typescript', label: 'TypeScript' },
  ],
  api: { createSubmission: jest.fn() },
}));

import { api } from '@/lib/api';

describe('SubmissionForm', () => {
  beforeEach(() => (api.createSubmission as jest.Mock).mockReset());

  it('submits code and notifies parent', async () => {
    (api.createSubmission as jest.Mock).mockResolvedValue({ id: 1 });
    const onSubmitted = jest.fn();
    render(<SubmissionForm token="t" onSubmitted={onSubmitted} />);

    fireEvent.change(screen.getByPlaceholderText('Paste your code here...'), {
      target: { value: 'print(1)' },
    });
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'python' } });
    fireEvent.click(screen.getByRole('button', { name: 'Submit for Review' }));

    await waitFor(() =>
      expect(api.createSubmission).toHaveBeenCalledWith('print(1)', 'python', null, 't'),
    );
    await waitFor(() => expect(onSubmitted).toHaveBeenCalled());
  });

  it('shows typed error on failure', async () => {
    const err = Object.assign(new Error('x'), {
      apiError: { error_type: 'unsupported_language', message: 'Unsupported' },
    });
    (api.createSubmission as jest.Mock).mockRejectedValue(err);
    render(<SubmissionForm token="t" onSubmitted={jest.fn()} />);

    fireEvent.change(screen.getByPlaceholderText('Paste your code here...'), {
      target: { value: 'x' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Submit for Review' }));

    await waitFor(() => expect(screen.getByText(/Unsupported language/)).toBeInTheDocument());
  });
});
