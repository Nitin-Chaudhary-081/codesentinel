"use client";

import { useEffect, useState } from "react";
import { api, Submission } from "@/lib/api";

export default function SubmissionList({
  token,
  onSelect,
  selectedId,
}: {
  token: string;
  onSelect: (id: number) => void;
  selectedId: number | null;
}) {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listSubmissions(token)
      .then(setSubmissions)
      .catch(() => setSubmissions([]))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <p className="text-gray-500">Loading submissions...</p>;
  if (!submissions.length) return <p className="text-gray-500">No submissions yet.</p>;

  return (
    <div className="border rounded-lg p-4">
      <h2 className="text-xl font-semibold mb-4">History</h2>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {submissions.map((s) => (
          <button
            key={s.id}
            onClick={() => onSelect(s.id)}
            className={`w-full text-left p-3 rounded-lg border transition ${
              selectedId === s.id
                ? "border-blue-500 bg-blue-50"
                : "hover:bg-gray-50"
            }`}
          >
            <div className="flex justify-between items-center">
              <span className="font-mono text-sm">
                #{s.id} — <span className="font-semibold">{s.language}</span>
              </span>
              <StatusBadge status={s.status} language={s.language} />
            </div>
            <p className="text-xs text-gray-400 mt-1 truncate">
              {s.code.slice(0, 60)}...
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}

function StatusBadge({ status, language }: { status: string; language: string }) {
  const styles: Record<string, string> = {
    pending: "bg-yellow-100 text-yellow-800",
    processing: "bg-blue-100 text-blue-800",
    completed: "bg-green-100 text-green-800",
    failed: "bg-red-100 text-red-800",
  };
  const labels: Record<string, string> = {
    pending: "pending",
    processing: "processing",
    completed: "ok",
    failed: "failed",
  };
  const displayLabel = labels[status] || status;
  const compositeLabel = `${language}_${displayLabel}`;
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full ${styles[status] || "bg-gray-100"}`}>
      {compositeLabel}
    </span>
  );
}
