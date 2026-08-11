"use client";

import { useEffect, useState, useCallback } from "react";
import { api, Evaluation, Submission } from "@/lib/api";

export default function ReportViewer({
  submissionId,
  token,
}: {
  submissionId: number;
  token: string;
}) {
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ type: string; message: string; details?: Record<string, unknown> } | null>(null);

  const loadSubmission = useCallback(() => {
    api.getSubmission(submissionId, token).then(setSubmission).catch(() => {});
  }, [submissionId, token]);

  useEffect(() => {
    loadSubmission();
  }, [loadSubmission]);

  const handleEvaluate = async () => {
    setLoading(true);
    setError(null);
    setEvaluation(null);
    try {
      const result = await api.runEvaluation(submissionId, token);
      setEvaluation(result);
    } catch (err) {
      const apiErr = (err as Error & { apiError?: { error_type: string; message: string; details?: Record<string, unknown>; data?: { error?: { error_type: string; message: string; details?: Record<string, unknown> } } } }).apiError;
      if (apiErr) {
        const innerError = apiErr.data?.error;
        setError({
          type: innerError?.error_type || apiErr.error_type,
          message: innerError?.message || apiErr.message,
          details: innerError?.details || apiErr.details,
        });
        if (apiErr.data?.language && apiErr.data?.analysis_status) {
          setEvaluation({
            id: 0,
            submission_id: submissionId,
            scores: null,
            feedback: null,
            overall_score: null,
            created_at: new Date().toISOString(),
            language: apiErr.data.language,
            analysis_status: apiErr.data.analysis_status as Evaluation["analysis_status"],
            syntax_valid: false,
            error: innerError,
          });
        }
      } else {
        setError({ type: "unknown", message: err instanceof Error ? err.message : "Evaluation failed" });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: string) => {
    try {
      const content = await api.exportReport(submissionId, format, token);
      const blob = new Blob([content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${submissionId}.${format === "jsonl" ? "jsonl" : "md"}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError({ type: "export_error", message: "Export failed" });
    }
  };

  return (
    <div className="border rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Report #{submissionId}</h2>

      {submission && (
        <div className="mb-4">
          <p className="text-sm text-gray-500">
            Language: {submission.language} | Status: {submission.status}
          </p>
        </div>
      )}

      {!evaluation && submission?.status !== "completed" && (
        <button
          onClick={handleEvaluate}
          disabled={loading}
          className="w-full bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 disabled:opacity-50 mb-4"
        >
          {loading ? "Evaluating..." : "Run Evaluation"}
        </button>
      )}

      {error && (
        <div className={`mb-4 p-3 rounded-lg ${
          error.type === "syntax_error" ? "bg-red-50 border border-red-200" :
          error.type === "type_error" ? "bg-orange-50 border border-orange-200" :
          error.type === "unsupported_language" ? "bg-yellow-50 border border-yellow-200" :
          "bg-red-50 border border-red-200"
        }`}>
          <p className="text-sm font-semibold text-red-700">
            {error.type === "syntax_error" ? "Syntax Error" :
             error.type === "type_error" ? "Type Error" :
             error.type === "unsupported_language" ? "Unsupported Language" :
             "Analysis Failed"}
          </p>
          <p className="text-sm text-red-600 mt-1">{error.message}</p>
          {error.details && typeof error.details === "object" && "line" in error.details && (
            <p className="text-xs text-red-500 mt-1">Line {String(error.details.line)}{"column" in error.details ? `, Column ${String(error.details.column)}` : ""}</p>
          )}
          {error.details && typeof error.details === "object" && "expected_type" in error.details && (
            <p className="text-xs text-red-500 mt-1">Expected: {String(error.details.expected_type)}, Got: {String(error.details.actual_type)}</p>
          )}
        </div>
      )}
      {evaluation?.syntax_valid && (
        <div className="mb-4 p-3 rounded-lg bg-green-50 border border-green-200">
          <p className="text-sm font-semibold text-green-700">Syntax OK</p>
          <p className="text-sm text-green-600 mt-1">{evaluation.message || "No syntax errors found"}</p>
        </div>
      )}

      {evaluation && evaluation.scores && (
        <>
          <ScoreRadar scores={evaluation.scores} overall={evaluation.overall_score} />
          <FeedbackSection feedback={evaluation.feedback} />
          <div className="flex gap-2 mt-4">
            <button
              onClick={() => handleExport("markdown")}
              className="flex-1 border rounded-lg px-3 py-2 text-sm hover:bg-gray-50"
            >
              Export Markdown
            </button>
            <button
              onClick={() => handleExport("jsonl")}
              className="flex-1 border rounded-lg px-3 py-2 text-sm hover:bg-gray-50"
            >
              Export JSONL
            </button>
          </div>
        </>
      )}
    </div>
  );
}

function ScoreRadar({ scores, overall }: { scores: Evaluation["scores"]; overall: number | null }) {
  return (
    <div className="mb-6">
      <div className="text-center mb-4">
        <span className="text-4xl font-bold">{overall ?? "—"}</span>
        <span className="text-gray-400 text-lg">/10</span>
      </div>
      <div className="space-y-2">
        {Object.entries(scores).map(([key, value]) => (
          <div key={key} className="flex items-center gap-3">
            <span className="text-sm w-32 capitalize">{key.replace("_", " ")}</span>
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${value * 10}%` }}
              />
            </div>
            <span className="text-sm w-8 text-right">{value}/10</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function FeedbackSection({ feedback }: { feedback: Evaluation["feedback"] }) {
  return (
    <div className="space-y-3">
      {feedback.issues?.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-red-600 mb-1">Issues</h3>
          <ul className="list-disc list-inside text-sm space-y-1">
            {feedback.issues.map((i, idx) => (
              <li key={idx} className="text-red-700">{i}</li>
            ))}
          </ul>
        </div>
      )}
      {feedback.suggestions?.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-yellow-600 mb-1">Suggestions</h3>
          <ul className="list-disc list-inside text-sm space-y-1">
            {feedback.suggestions.map((s, idx) => (
              <li key={idx} className="text-yellow-700">{s}</li>
            ))}
          </ul>
        </div>
      )}
      {feedback.highlights?.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-green-600 mb-1">Highlights</h3>
          <ul className="list-disc list-inside text-sm space-y-1">
            {feedback.highlights.map((h, idx) => (
              <li key={idx} className="text-green-700">{h}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
