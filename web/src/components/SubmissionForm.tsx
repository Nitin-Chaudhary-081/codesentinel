"use client";

import { useState } from "react";
import { api, LANGUAGES } from "@/lib/api";

export default function SubmissionForm({
  token,
  onSubmitted,
}: {
  token: string;
  onSubmitted: () => void;
}) {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [context, setContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.createSubmission(code, language, context || null, token);
      setCode("");
      setContext("");
      onSubmitted();
    } catch (err) {
      const apiErr = (err as Error & { apiError?: { error_type: string; message: string } }).apiError;
      if (apiErr?.error_type === "unsupported_language") {
        setError(`Unsupported language. Supported: Python, TypeScript, JavaScript, Go, Java, C++`);
      } else {
        setError(err instanceof Error ? err.message : "Submission failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border rounded-lg p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Submit Code</h2>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Language</label>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="w-full border rounded-lg px-3 py-2"
        >
          {LANGUAGES.map((l) => (
            <option key={l.value} value={l.value}>
              {l.label}
            </option>
          ))}
        </select>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Code</label>
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          required
          rows={10}
          className="w-full border rounded-lg px-3 py-2 font-mono text-sm"
          placeholder="Paste your code here..."
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Context (optional)</label>
        <input
          type="text"
          value={context}
          onChange={(e) => setContext(e.target.value)}
          className="w-full border rounded-lg px-3 py-2"
          placeholder="e.g., authentication middleware, sorting algorithm..."
        />
      </div>

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-green-600 text-white rounded-lg px-4 py-2 hover:bg-green-700 disabled:opacity-50"
      >
        {loading ? "Submitting..." : "Submit for Review"}
      </button>
    </form>
  );
}
