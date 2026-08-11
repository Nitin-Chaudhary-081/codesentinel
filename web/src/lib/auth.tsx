"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface AuthState {
  token: string | null;
  email: string | null;
  setAuth: (token: string, email: string) => void;
  clearAuth: () => void;
}

const AuthContext = createContext<AuthState>({
  token: null,
  email: null,
  setAuth: () => {},
  clearAuth: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);

  const setAuth = (t: string, e: string) => {
    setToken(t);
    setEmail(e);
    if (typeof window !== "undefined") {
      localStorage.setItem("codesentinel_token", t);
      localStorage.setItem("codesentinel_email", e);
    }
  };

  const clearAuth = () => {
    setToken(null);
    setEmail(null);
    if (typeof window !== "undefined") {
      localStorage.removeItem("codesentinel_token");
      localStorage.removeItem("codesentinel_email");
    }
  };

  return (
    <AuthContext.Provider value={{ token, email, setAuth, clearAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
