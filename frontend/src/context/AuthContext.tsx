import { ReactNode, createContext, useContext, useEffect, useState } from "react";

import { apiRequest } from "../api/client";
import type { AuthResponse, User } from "../types";

interface AuthContextValue {
  token: string | null;
  user: User | null;
  loading: boolean;
  login: (payload: { email: string; password: string }) => Promise<void>;
  register: (payload: { full_name: string; email: string; password: string }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_KEY = "kbc-lms-token";
const USER_KEY = "kbc-lms-user";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) {
      return;
    }
    apiRequest<User>("/auth/me", { token })
      .then((nextUser) => {
        setUser(nextUser);
        localStorage.setItem(USER_KEY, JSON.stringify(nextUser));
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        setToken(null);
        setUser(null);
      });
  }, [token]);

  async function handleAuth(path: string, body: unknown) {
    setLoading(true);
    try {
      const response = await apiRequest<AuthResponse>(path, {
        method: "POST",
        body,
      });
      setToken(response.access_token);
      setUser(response.user);
      localStorage.setItem(TOKEN_KEY, response.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(response.user));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        loading,
        login: (payload) => handleAuth("/auth/login", payload),
        register: (payload) => handleAuth("/auth/register", payload),
        logout: () => {
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(USER_KEY);
          setToken(null);
          setUser(null);
        },
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
