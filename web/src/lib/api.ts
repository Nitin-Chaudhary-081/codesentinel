const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

export interface Submission {
  id: number;
  user_id: number;
  code: string;
  language: string;
  context: string | null;
  status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
  updated_at: string;
}

export interface ScoreBreakdown {
  complexity: number;
  naming: number;
  error_handling: number;
  duplication: number;
  security: number;
  maintainability: number;
}

export interface AnalysisError {
  error_type: "syntax_error" | "type_error" | "analysis_failed" | "unsupported_language";
  message: string;
  details?: {
    line?: number;
    column?: number;
    expected_type?: string;
    actual_type?: string;
    language?: string;
    supported?: string[];
  };
}

export interface Evaluation {
  id: number;
  submission_id: number;
  scores: ScoreBreakdown | null;
  feedback: { issues: string[]; suggestions: string[]; highlights: string[] } | null;
  overall_score: number | null;
  created_at: string;
  language: string;
  analysis_status: "ok" | "syntax_error" | "type_error" | "analysis_failed" | "unsupported_language";
  syntax_valid: boolean;
  message?: string;
  error?: AnalysisError;
}

export interface ApiError {
  status: "error";
  error_type: string;
  message: string;
  details?: Record<string, unknown>;
  data?: {
    language?: string;
    analysis_status?: string;
    error?: AnalysisError;
    scores?: ScoreBreakdown | null;
    suggestions?: string[] | null;
  };
}

export interface ApiResponse<T> {
  status: "ok" | "error";
  data?: T;
  error_type?: string;
  message?: string;
  details?: Record<string, unknown>;
}

export const LANGUAGES = [
  { value: "python", label: "Python" },
  { value: "typescript", label: "TypeScript" },
  { value: "go", label: "Go" },
  { value: "java", label: "Java" },
  { value: "javascript", label: "JavaScript" },
  { value: "cpp", label: "C++" },
];

async function request<T>(path: string, options?: RequestInit, token?: string): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(`${API_URL}${path}`, { ...options, headers });
  const json = await resp.json();

  if (json.status === "error") {
    const err: ApiError = json;
    const error = new Error(err.message) as Error & { apiError: ApiError };
    error.apiError = err;
    throw error;
  }

  if (!resp.ok) {
    throw new Error(json.message || `HTTP ${resp.status}`);
  }

  return json.data as T;
}

export const api = {
  register: (email: string, password: string) =>
    request<{ id: number; email: string }>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    request<{ access_token: string }>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  createSubmission: (code: string, language: string, context: string | null, token: string) =>
    request<Submission>("/api/v1/submissions", {
      method: "POST",
      body: JSON.stringify({ code, language, context }),
    }, token),

  listSubmissions: (token: string) =>
    request<Submission[]>("/api/v1/submissions", {}, token),

  getSubmission: (id: number, token: string) =>
    request<Submission>(`/api/v1/submissions/${id}`, {}, token),

  runEvaluation: (submissionId: number, token: string) =>
    request<Evaluation>(`/api/v1/evaluations/${submissionId}`, { method: "POST" }, token),

  getEvaluation: (submissionId: number, token: string) =>
    request<Evaluation>(`/api/v1/evaluations/${submissionId}`, {}, token),

  exportReport: (submissionId: number, format: string, token: string) =>
    fetch(`${API_URL}/api/v1/reports/${submissionId}/export?format=${format}`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then((r) => r.text()),
};
