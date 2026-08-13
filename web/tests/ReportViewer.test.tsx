import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ReportViewer from '@/components/ReportViewer';

jest.mock('@/lib/api', () => ({
  LANGUAGES: [],
  api: {
    getSubmission: jest.fn(),
    runEvaluation: jest.fn(),
    exportReport: jest.fn(),
  },
}));

import { api } from '@/lib/api';

const sub = {
  id: 1,
  user_id: 1,
  code: 'x',
  language: 'python',
  context: null,
  status: 'pending',
  created_at: '',
  updated_at: '',
};
const scores = {
  complexity: 8,
  naming: 9,
  error_handling: 5,
  duplication: 9,
  security: 8,
  maintainability: 7,
};
const evalOk = {
  id: 1,
  submission_id: 1,
  scores,
  feedback: { issues: [], suggestions: [], highlights: [] },
  overall_score: 7,
  created_at: '',
  language: 'python',
  analysis_status: 'ok',
  syntax_valid: true,
  message: 'ok',
};

beforeEach(() => {
  jest.clearAllMocks();
  (global as any).URL = (global as any).URL || {};
  (global as any).URL.createObjectURL = jest.fn(() => 'blob:x');
  (global as any).URL.revokeObjectURL = jest.fn();
  if (!(global as any).Blob) {
    (global as any).Blob = class {
      constructor(_p: unknown) {}
    };
  }
});

describe('ReportViewer', () => {
  it('renders scores after evaluation', async () => {
    (api.getSubmission as jest.Mock).mockResolvedValue(sub);
    (api.runEvaluation as jest.Mock).mockResolvedValue(evalOk);

    render(<ReportViewer submissionId={1} token="t" />);
    await waitFor(() => expect(screen.getByText('Run Evaluation')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: 'Run Evaluation' }));

    await waitFor(() => expect(screen.getByText('7/10')).toBeInTheDocument());
  });

  it('shows typed error for invalid code', async () => {
    (api.getSubmission as jest.Mock).mockResolvedValue(sub);
    const err = Object.assign(new Error('err'), {
      apiError: {
        error_type: 'syntax_error',
        message: 'Syntax error',
        details: { line: 1 },
        data: { language: 'python', analysis_status: 'syntax_error' },
      },
    });
    (api.runEvaluation as jest.Mock).mockRejectedValue(err);

    render(<ReportViewer submissionId={1} token="t" />);
    await waitFor(() => expect(screen.getByText('Run Evaluation')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: 'Run Evaluation' }));

    await waitFor(() => expect(screen.getByText('Syntax Error')).toBeInTheDocument());
  });

  it('exports JSONL on button click', async () => {
    (api.getSubmission as jest.Mock).mockResolvedValue(sub);
    (api.runEvaluation as jest.Mock).mockResolvedValue(evalOk);
    (api.exportReport as jest.Mock).mockResolvedValue('jsonl-content');

    render(<ReportViewer submissionId={1} token="t" />);
    await waitFor(() => expect(screen.getByText('Run Evaluation')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: 'Run Evaluation' }));
    await waitFor(() => expect(screen.getByText('7/10')).toBeInTheDocument());

    fireEvent.click(screen.getByRole('button', { name: 'Export JSONL' }));
    await waitFor(() => expect(api.exportReport).toHaveBeenCalledWith(1, 'jsonl', 't'));
  });
});
