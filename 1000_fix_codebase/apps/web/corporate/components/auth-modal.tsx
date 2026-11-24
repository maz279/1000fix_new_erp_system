"use client";

/**
 * Corporate Authentication Context.
 *
 * Sign-in lives on the dedicated /login page; `openLoginModal()` navigates
 * there (the name is kept for existing callers). Session truth is the Odoo
 * cookie checked through the same-origin /api/odoo bridge — the Odoo session
 * is the only credential and internal (staff) sessions are treated as signed
 * out. The sessionStorage profile is display-only.
 */
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getCurrentUser,
  getSessionInfo,
  loginWithOdoo,
  logoutOdoo,
  type UserSession,
} from "../lib/auth";

interface AuthContextValue {
  user: UserSession | null;
  backendReachable: boolean | null;
  /** false until the first Odoo session check has completed. */
  authReady: boolean;
  openLoginModal: () => void;
  closeLoginModal: () => void;
  logoutUser: () => Promise<void>;
  loginWithCredentials: (u: string, p: string) => Promise<void>;
  refreshUser: () => Promise<UserSession | null>;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  backendReachable: null,
  authReady: false,
  openLoginModal: () => {},
  closeLoginModal: () => {},
  logoutUser: async () => {},
  loginWithCredentials: async () => {},
  refreshUser: async () => null,
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserSession | null>(null);
  const [backendReachable, setBackendReachable] = useState<boolean | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const router = useRouter();

  const refreshUser = useCallback(async () => {
    const { user: live, backendReachable: up } = await getSessionInfo();
    setBackendReachable(up);
    if (live) {
      setUser(live);
      window.sessionStorage.setItem("fix_corporate_user", JSON.stringify(live));
    } else {
      setUser(null);
      window.sessionStorage.removeItem("fix_corporate_user");
      window.sessionStorage.removeItem("fix_token");
    }
    setAuthReady(true);
    return live;
  }, []);

  useEffect(() => {
    const cached = getCurrentUser();
    if (cached) setUser(cached);
    refreshUser();
  }, [refreshUser]);

  const openLoginModal = useCallback(() => router.push("/login"), [router]);
  const closeLoginModal = useCallback(() => router.push("/"), [router]);

  const loginWithCredentials = useCallback(async (u: string, p: string) => {
    const session = await loginWithOdoo(u, p);
    setUser(session);
  }, []);

  const logoutUser = useCallback(async () => {
    await logoutOdoo();
    setUser(null);
    router.push("/");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        user,
        backendReachable,
        authReady,
        openLoginModal,
        closeLoginModal,
        logoutUser,
        loginWithCredentials,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
