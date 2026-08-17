"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth";
import SubmissionForm from "@/components/SubmissionForm";
import SubmissionList from "@/components/SubmissionList";
import ReportViewer from "@/components/ReportViewer";
import AuthScene from "@/components/AuthScene";

export default function Home() {
  const { token, email, setAuth, clearAuth } = useAuth();
  const [selectedSubmission, setSelectedSubmission] = useState<number | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  if (!token) {
    return <AuthScene onAuth={setAuth} />;
  }

  const handleSubmitted = () => setRefreshKey((k) => k + 1);

  return (
    <main className="min-h-screen p-8 max-w-6xl mx-auto">
      <header className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">CodeSentinel</h1>
          <p className="text-gray-500">AI Code Review & Evaluation</p>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">{email}</span>
          <button
            onClick={clearAuth}
            className="text-sm text-red-500 hover:text-red-700"
          >
            Logout
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <SubmissionForm token={token} onSubmitted={handleSubmitted} />
          <SubmissionList
            token={token}
            key={refreshKey}
            onSelect={setSelectedSubmission}
            selectedId={selectedSubmission}
          />
        </div>
        <div>
          {selectedSubmission ? (
            <ReportViewer submissionId={selectedSubmission} token={token} />
          ) : (
            <div className="border rounded-lg p-8 text-center text-gray-400">
              Select a submission to view its report
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
