"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import LampToggle from "@/components/LampToggle";

const MOTES = [
  { left: "22%", bottom: "4%", size: 3, dur: 9, delay: 0, op: 0.7 },
  { left: "34%", bottom: "12%", size: 2, dur: 7.5, delay: 1.2, op: 0.5 },
  { left: "46%", bottom: "6%", size: 4, dur: 11, delay: 0.4, op: 0.6 },
  { left: "58%", bottom: "16%", size: 2, dur: 8, delay: 2.1, op: 0.5 },
  { left: "68%", bottom: "5%", size: 3, dur: 10, delay: 0.9, op: 0.65 },
  { left: "26%", bottom: "22%", size: 2, dur: 8.5, delay: 1.7, op: 0.45 },
  { left: "52%", bottom: "20%", size: 2.5, dur: 9.5, delay: 0.2, op: 0.55 },
  { left: "74%", bottom: "26%", size: 2, dur: 7.5, delay: 2.6, op: 0.4 },
];

export default function AuthScene({
  onAuth,
}: {
  onAuth: (token: string, email: string) => void;
}) {
  const [lampOn, setLampOn] = useState(false);
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
    <main className={`auth-scene relative min-h-screen overflow-hidden ${lampOn ? "scene-on" : "scene-off"}`}>
      <div className="scene-bg" aria-hidden />
      <div className="scene-vignette" aria-hidden />
      <div className="scene-topglow" aria-hidden />

      <div className="relative flex flex-col items-center px-6">
        <div className="pt-16 sm:pt-20">
          <LampToggle on={lampOn} onToggle={() => setLampOn((v) => !v)} />
        </div>

        <div className="relative w-full max-w-md mt-4">
          <div className="light-cone" aria-hidden />
          <div className="motes" aria-hidden>
            {MOTES.map((m, i) => (
              <span
                key={i}
                className="mote"
                style={{
                  left: m.left,
                  bottom: m.bottom,
                  width: m.size,
                  height: m.size,
                  opacity: m.op,
                  animationDuration: `${m.dur}s`,
                  animationDelay: `${m.delay}s`,
                }}
              />
            ))}
          </div>

          {!lampOn ? (
            <p className="hint relative z-10 mt-10 text-center text-sm text-slate-500/80">
              Pull the lamp cord to reveal the login menu
            </p>
          ) : (
            <form onSubmit={handleSubmit} className="glass-card relative z-10 space-y-4">
              <div className="text-center mb-2">
                <p className="field-in text-lg font-semibold tracking-tight text-slate-100" style={{ animationDelay: "0.18s" }}>
                  CodeSentinel
                </p>
                <p className="field-in text-sm text-slate-400/80" style={{ animationDelay: "0.24s" }}>
                  AI Code Review Platform
                </p>
              </div>

              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="field-in glass-input"
                style={{ animationDelay: "0.32s" }}
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                className="field-in glass-input"
                style={{ animationDelay: "0.4s" }}
              />

              {error && <p className="field-in text-red-400 text-sm" style={{ animationDelay: "0.44s" }}>{error}</p>}

              <button type="submit" className="field-in premium-btn" style={{ animationDelay: "0.5s" }}>
                {isLogin ? "Login" : "Register"}
              </button>
              <button
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                className="field-in w-full text-sm text-slate-400/80 hover:text-slate-200 transition-colors"
                style={{ animationDelay: "0.58s" }}
              >
                {isLogin ? "Need an account? Register" : "Have an account? Login"}
              </button>
            </form>
          )}
        </div>
      </div>
    </main>
  );
}
