"use client";

/**
 * Customer Authentication context + command-bar controls.
 * Sign-in lives on the dedicated /login page (prototype login.html port);
 * openLoginModal() is kept for existing callers and navigates there.
 * Session truth is the Odoo cookie checked via /web/session/get_session_info
 * (same-origin, lib/auth.ts) — the sessionStorage profile is display-only
 * and grants nothing; the legacy fake token is purged (security fix
 * 2026-10-23). Backend-down is distinguished from signed-out via
 * `backendReachable` so pages stop masking outages as "session expired".
 */
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  login,
  loginWithOtp,
  logout,
  getCurrentUser,
  getSessionInfo,
  UserSession,
} from "../lib/auth";
import { useLanguage } from "./language";

interface AuthContextValue {
  user: UserSession | null;
  /** null = unknown (checking), true/false = backend reachable or not */
  backendReachable: boolean | null;
  /** false until the first session check against Odoo has completed. */
  authReady: boolean;
  openLoginModal: () => void;
  closeLoginModal: () => void;
  logoutUser: () => Promise<void>;
  loginWithCredentials: (u: string, p: string) => Promise<void>;
  loginUserWithOtp: (phone: string, otp: string) => Promise<void>;
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
  loginUserWithOtp: async () => {},
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
      window.sessionStorage.setItem("fix_user", JSON.stringify(live));
    } else {
      // The display cache may only survive while the backend confirms it.
      setUser(null);
      window.sessionStorage.removeItem("fix_user");
      window.sessionStorage.removeItem("fix_token");
    }
    setAuthReady(true);
    return live;
  }, []);

  useEffect(() => {
    // Optimistic paint from the cache, then verify against Odoo.
    const cached = getCurrentUser();
    if (cached) setUser(cached);
    refreshUser();
  }, [refreshUser]);

  const openLoginModal = useCallback(() => router.push("/login"), [router]);
  const closeLoginModal = useCallback(() => router.push("/"), [router]);

  const loginWithCredentials = useCallback(async (u: string, p: string) => {
    const session = await login(u, p);
    setUser(session);
  }, []);

  const loginUserWithOtp = useCallback(async (phone: string, otp: string) => {
    const session = await loginWithOtp(phone, otp);
    setUser(session);
  }, []);

  const logoutUser = useCallback(async () => {
    await logout();
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
        loginUserWithOtp,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

/** Command bar controls: avatar + sign out when signed in, sign-in button otherwise. */
export function AuthControls() {
  const { user, openLoginModal, logoutUser } = useAuth();
  const { t } = useLanguage();
  const router = useRouter();

  if (!user) {
    return (
      <button className="btn btn-primary btn-sm" onClick={openLoginModal}>
        {t.signIn}
      </button>
    );
  }

  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      <button
        className="tb-avatar"
        title={user.name}
        aria-label={user.name}
        style={{ border: 0, cursor: "pointer" }}
        onClick={() => router.push("/dashboard")}
      >
        {user.name.slice(0, 1).toUpperCase()}
      </button>
      <span
        className="nav-label"
        style={{ fontSize: 12, color: "var(--fix-ink-2)", maxWidth: 120, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
      >
        {user.name}
      </span>
      <button className="tb-icon-btn" onClick={logoutUser} title={t.signOut} aria-label={t.signOut}>
        ⏻
      </button>
    </span>
  );
}
