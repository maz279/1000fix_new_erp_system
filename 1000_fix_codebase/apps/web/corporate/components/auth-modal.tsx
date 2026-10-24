"use client";

/**
 * Corporate Authentication Modal & Context.
 * Enables direct sign-in against Odoo via the Kong gateway (/web/session/authenticate).
 * Credential entry only: no prefilled, demo or one-click persona credentials
 * (removed in the security fix of 2026-10-23).
 * Fully accessible: aria-modal, role="dialog", Escape key listener, focus styles.
 * Tokens only (CFM-01) — no hand-authored colors.
 */
import { createContext, useContext, useEffect, useState, useId } from "react";
import { tokens } from "../lib/imports";
import { loginWithOdoo, logoutOdoo, getCurrentUser, UserSession } from "../lib/auth";
import { useLanguage } from "./language";

interface AuthContextValue {
  user: UserSession | null;
  openLoginModal: () => void;
  closeLoginModal: () => void;
  logoutUser: () => Promise<void>;
  loginWithCredentials: (u: string, p: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  openLoginModal: () => {},
  closeLoginModal: () => {},
  logoutUser: async () => {},
  loginWithCredentials: async () => {},
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserSession | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const existing = getCurrentUser();
    if (existing) setUser(existing);
  }, []);

  const openLoginModal = () => setIsModalOpen(true);
  const closeLoginModal = () => setIsModalOpen(false);

  const loginWithCredentials = async (u: string, p: string) => {
    const session = await loginWithOdoo(u, p);
    setUser(session);
    setIsModalOpen(false);
  };

  const logoutUser = async () => {
    await logoutOdoo();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        openLoginModal,
        closeLoginModal,
        logoutUser,
        loginWithCredentials,
      }}
    >
      {children}
      {isModalOpen && <AuthModal onClose={closeLoginModal} />}
    </AuthContext.Provider>
  );
}

export function AuthModal({ onClose }: { onClose: () => void }) {
  const { loginWithCredentials } = useAuth();
  const { t } = useLanguage();
  const usernameId = useId();
  const passwordId = useId();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await loginWithCredentials(username, password);
    } catch (err) {
      setError((err as Error).message || "Authentication failed");
      setLoading(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="corporate-auth-title"
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0, 0, 0, 0.6)",
        backdropFilter: "blur(4px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
        padding: 16,
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        style={{
          background: tokens["color.surface.primary"],
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-md"],
          maxWidth: 520,
          width: "100%",
          padding: 28,
          boxShadow: tokens["shadow.lg"],
          position: "relative",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
          <div>
            <h2
              id="corporate-auth-title"
              style={{
                margin: "0 0 6px",
                fontSize: tokens["typography.size.400"],
                fontWeight: Number(tokens["typography.weight.bold"]),
                color: tokens["color.text.primary"],
              }}
            >
              {t.authModalTitle}
            </h2>
            <p
              style={{
                margin: 0,
                fontSize: tokens["typography.size.200"],
                color: tokens["color.text.secondary"],
                lineHeight: tokens["typography.lineHeight.normal"],
              }}
            >
              {t.authModalSubtitle}
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label={t.closeButton}
            style={{
              background: "transparent",
              border: "none",
              color: tokens["color.text.secondary"],
              fontSize: 20,
              cursor: "pointer",
              padding: "4px 8px",
              lineHeight: 1,
            }}
          >
            ✕
          </button>
        </div>

        {error && (
          <div
            role="alert"
            style={{
              padding: 10,
              marginBottom: 16,
              background: tokens["color.status.error-bg"],
              color: tokens["color.status.error"],
              border: `1px solid ${tokens["color.status.error"]}`,
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: tokens["typography.size.200"],
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {/* Credentials Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 14 }}>
            <label
              htmlFor={usernameId}
              style={{
                display: "block",
                fontSize: tokens["typography.size.200"],
                fontWeight: Number(tokens["typography.weight.medium"]),
                color: tokens["color.text.primary"],
                marginBottom: 4,
              }}
            >
              {t.usernameLabel}
            </label>
            <input
              id={usernameId}
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "8px 12px",
                fontSize: tokens["typography.size.200"],
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-sm"],
                background: tokens["color.surface.canvas"],
                color: tokens["color.text.primary"],
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label
              htmlFor={passwordId}
              style={{
                display: "block",
                fontSize: tokens["typography.size.200"],
                fontWeight: Number(tokens["typography.weight.medium"]),
                color: tokens["color.text.primary"],
                marginBottom: 4,
              }}
            >
              {t.passwordLabel}
            </label>
            <input
              id={passwordId}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "8px 12px",
                fontSize: tokens["typography.size.200"],
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-sm"],
                background: tokens["color.surface.canvas"],
                color: tokens["color.text.primary"],
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ display: "flex", gap: 12, justifyContent: "flex-end" }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: "8px 16px",
                fontSize: tokens["typography.size.200"],
                color: tokens["color.text.secondary"],
                background: "transparent",
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-sm"],
                cursor: "pointer",
              }}
            >
              {t.cancelButton}
            </button>
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: "8px 20px",
                fontSize: tokens["typography.size.200"],
                fontWeight: Number(tokens["typography.weight.semibold"]),
                color: tokens["color.text.inverse"],
                background: tokens["color.primary.base"],
                border: "none",
                borderRadius: tokens["dimension.border.radius-sm"],
                cursor: loading ? "wait" : "pointer",
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? t.loggingIn : t.loginButton}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
