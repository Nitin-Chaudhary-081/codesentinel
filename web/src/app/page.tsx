"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import SubmissionForm from "@/components/SubmissionForm";
import SubmissionList from "@/components/SubmissionList";
import ReportViewer from "@/components/ReportViewer";

export default function Home() {
  const { token, email, setAuth, clearAuth } = useAuth();
  const [selectedSubmission, setSelectedSubmission] = useState<number | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  if (!token) {
    return <AuthForm onAuth={setAuth} />;
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

function AuthForm({ onAuth }: { onAuth: (token: string, email: string) => void }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      if (isLogin) {
        const { access_token } = await api.login(email, password);
        onAuth(access_token, email);
      } else {
        await api.register(email, password);
        const { access_token } = await api.login(email, password);
        onAuth(access_token, email);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-8">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-2">CodeSentinel</h1>
        <p className="text-gray-500 text-center mb-8">AI Code Review Platform</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full border rounded-lg px-4 py-2"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full border rounded-lg px-4 py-2"
          />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit"
            className="w-full bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700"
          >
            {isLogin ? "Login" : "Register"}
          </button>
          <button
            type="button"
            onClick={() => setIsLogin(!isLogin)}
            className="w-full text-sm text-gray-500 hover:text-gray-700"
          >
            {isLogin ? "Need an account? Register" : "Have an account? Login"}
          </button>
        </form>
      </div>
    </main>
  );
}
