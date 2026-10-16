"use client";

/**
 * Customer Authentication Modal & Context.
 * Enables direct sign-in against Odoo via the Kong gateway.
 * Supports:
 *   1. 11-digit Bangladesh Phone + SMS OTP verification (/customer/auth/otp/send & verify)
 *      for 250K+/mo retail customers.
 *   2. Odoo username/password credential entry and one-click demo personas.
 * Fully accessible: aria-modal, role="dialog", Escape key listener, focus styles.
 * Tokens only (CFM-01) — no hand-authored colors.
 */
import { createContext, useContext, useEffect, useState, useId } from "react";
import { tokens } from "../lib/imports";
import { login, logout, sendOtp, loginWithOtp, getCurrentUser, UserSession } from "../lib/auth";
import { useLanguage } from "./language";

interface AuthContextValue {
  user: UserSession | null;
  openLoginModal: () => void;
  closeLoginModal: () => void;
  logoutUser: () => Promise<void>;
  loginWithCredentials: (u: string, p: string) => Promise<void>;
  loginUserWithOtp: (phone: string, otp: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  openLoginModal: () => {},
  closeLoginModal: () => {},
  logoutUser: async () => {},
  loginWithCredentials: async () => {},
  loginUserWithOtp: async () => {},
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
    const session = await login(u, p);
    setUser(session);
    setIsModalOpen(false);
  };

  const loginUserWithOtp = async (phone: string, otp: string) => {
    const session = await loginWithOtp(phone, otp);
    setUser(session);
    setIsModalOpen(false);
  };

  const logoutUser = async () => {
    await logout();
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
        loginUserWithOtp,
      }}
    >
      {children}
      {isModalOpen && (
        <AuthModal
          onClose={closeLoginModal}
          onLoginCredentials={loginWithCredentials}
          onLoginOtp={loginUserWithOtp}
        />
      )}
    </AuthContext.Provider>
  );
}

interface AuthModalProps {
  onClose: () => void;
  onLoginCredentials: (u: string, p: string) => Promise<void>;
  onLoginOtp: (phone: string, otp: string) => Promise<void>;
}

function AuthModal({ onClose, onLoginCredentials, onLoginOtp }: AuthModalProps) {
  const { t, locale } = useLanguage();
  const [activeTab, setActiveTab] = useState<"otp" | "credentials">("otp");

  // Phone OTP State
  const [phone, setPhone] = useState("01711223344");
  const [otpSent, setOtpSent] = useState(false);
  const [otpCode, setOtpCode] = useState("");
  const [maskedPhone, setMaskedPhone] = useState("");
  const [devCode, setDevCode] = useState<string | null>(null);

  // Credentials State
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin");

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const phoneId = useId();
  const otpId = useId();
  const usernameId = useId();
  const passwordId = useId();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await sendOtp(phone);
      setOtpSent(true);
      setMaskedPhone(res.masked_phone || phone);
      if (res.dev_code) {
        setDevCode(res.dev_code);
        setOtpCode(res.dev_code); // Auto-fill dev code for convenience
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onLoginOtp(phone, otpCode);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const handleCredentialSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onLoginCredentials(username, password);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const handlePersonaLogin = async (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setBusy(true);
    setError(null);
    try {
      await onLoginCredentials(u, p);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="auth-modal-title"
      style={{
        position: "fixed",
        inset: 0,
        display: "grid",
        placeItems: "center",
        background: "rgba(0, 0, 0, 0.5)",
        backdropFilter: "blur(4px)",
        zIndex: 1000,
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 460,
          background: tokens["color.surface.primary"],
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-md"],
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.2)",
          padding: 24,
          margin: 16,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2
            id="auth-modal-title"
            style={{
              margin: 0,
              fontSize: tokens["typography.size.400"],
              fontWeight: Number(tokens["typography.weight.bold"]),
              color: tokens["color.primary.base"],
            }}
          >
            {locale === "bn" ? "১০০০FiX কাস্টমার পোর্টাল লগইন" : "1000FiX Customer Sign In"}
          </h2>
          <button
            onClick={onClose}
            aria-label={locale === "bn" ? "বন্ধ করুন" : "Close"}
            style={{
              background: "transparent",
              border: "none",
              color: tokens["color.text.secondary"],
              fontSize: tokens["typography.size.400"],
              cursor: "pointer",
              padding: 4,
            }}
          >
            ✕
          </button>
        </div>

        {/* Tab Selection */}
        <div
          role="tablist"
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 6,
            marginTop: 16,
            marginBottom: 16,
            background: tokens["color.surface.secondary"],
            padding: 4,
            borderRadius: tokens["dimension.border.radius-sm"],
          }}
        >
          <button
            role="tab"
            aria-selected={activeTab === "otp"}
            type="button"
            onClick={() => { setActiveTab("otp"); setError(null); }}
            style={{
              padding: "8px 12px",
              background: activeTab === "otp" ? tokens["color.surface.primary"] : "transparent",
              color: activeTab === "otp" ? tokens["color.primary.base"] : tokens["color.text.secondary"],
              border: activeTab === "otp" ? `1px solid ${tokens["color.border.default"]}` : "none",
              borderRadius: tokens["dimension.border.radius-sm"],
              fontWeight: activeTab === "otp" ? 600 : 400,
              cursor: "pointer",
              fontSize: tokens["typography.size.100"],
            }}
          >
            📱 {t.authOtpTab}
          </button>
          <button
            role="tab"
            aria-selected={activeTab === "credentials"}
            type="button"
            onClick={() => { setActiveTab("credentials"); setError(null); }}
            style={{
              padding: "8px 12px",
              background: activeTab === "credentials" ? tokens["color.surface.primary"] : "transparent",
              color: activeTab === "credentials" ? tokens["color.primary.base"] : tokens["color.text.secondary"],
              border: activeTab === "credentials" ? `1px solid ${tokens["color.border.default"]}` : "none",
              borderRadius: tokens["dimension.border.radius-sm"],
              fontWeight: activeTab === "credentials" ? 600 : 400,
              cursor: "pointer",
              fontSize: tokens["typography.size.100"],
            }}
          >
            🔑 {t.authCredsTab}
          </button>
        </div>

        {/* TAB 1: PHONE OTP AUTHENTICATION */}
        {activeTab === "otp" && (
          <div>
            {!otpSent ? (
              <form onSubmit={handleSendOtp} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                <div>
                  <label
                    htmlFor={phoneId}
                    style={{
                      display: "block",
                      marginBottom: 6,
                      fontSize: tokens["typography.size.200"],
                      color: tokens["color.text.primary"],
                      fontWeight: Number(tokens["typography.weight.medium"]),
                    }}
                  >
                    {t.authPhoneLabel}
                  </label>
                  <input
                    id={phoneId}
                    type="tel"
                    required
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder={t.authPhonePlaceholder}
                    style={{
                      width: "100%",
                      boxSizing: "border-box",
                      padding: "10px 12px",
                      background: tokens["color.surface.canvas"],
                      color: tokens["color.text.primary"],
                      border: `1px solid ${tokens["color.border.default"]}`,
                      borderRadius: tokens["dimension.border.radius-sm"],
                      fontSize: tokens["typography.size.200"],
                    }}
                  />
                  <small style={{ color: tokens["color.text.secondary"], display: "block", marginTop: 4 }}>
                    {locale === "bn"
                      ? "বাংলাদেশের ১১-সংখ্যার যেকোনো সক্রিয় মোবাইল নম্বর প্রদান করুন।"
                      : "Enter an active 11-digit Bangladesh phone number."}
                  </small>
                </div>

                <button
                  type="submit"
                  disabled={busy}
                  style={{
                    padding: "10px 16px",
                    background: tokens["color.primary.base"],
                    color: tokens["color.text.inverse"],
                    border: "none",
                    borderRadius: tokens["dimension.border.radius-sm"],
                    cursor: "pointer",
                    fontSize: tokens["typography.size.200"],
                    fontWeight: Number(tokens["typography.weight.medium"]),
                  }}
                >
                  {busy ? (locale === "bn" ? "ওটিপি পাঠানো হচ্ছে…" : "Sending OTP…") : t.authSendOtpBtn}
                </button>
              </form>
            ) : (
              <form onSubmit={handleVerifyOtp} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                <div
                  style={{
                    padding: "10px 12px",
                    background: tokens["color.status.info-bg"],
                    color: tokens["color.status.info"],
                    borderRadius: tokens["dimension.border.radius-sm"],
                    fontSize: tokens["typography.size.100"],
                  }}
                >
                  {t.authOtpSentNotice(maskedPhone)}
                  {devCode && (
                    <div style={{ marginTop: 4, fontWeight: 600 }}>
                      [Dev Test OTP: {devCode}]
                    </div>
                  )}
                </div>

                <div>
                  <label
                    htmlFor={otpId}
                    style={{
                      display: "block",
                      marginBottom: 6,
                      fontSize: tokens["typography.size.200"],
                      color: tokens["color.text.primary"],
                      fontWeight: Number(tokens["typography.weight.medium"]),
                    }}
                  >
                    {t.authOtpCodeLabel}
                  </label>
                  <input
                    id={otpId}
                    type="text"
                    required
                    maxLength={6}
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                    placeholder="123456"
                    style={{
                      width: "100%",
                      boxSizing: "border-box",
                      padding: "10px 12px",
                      background: tokens["color.surface.canvas"],
                      color: tokens["color.text.primary"],
                      border: `1px solid ${tokens["color.border.default"]}`,
                      borderRadius: tokens["dimension.border.radius-sm"],
                      fontSize: tokens["typography.size.300"],
                      letterSpacing: "4px",
                      textAlign: "center",
                      fontWeight: 600,
                    }}
                  />
                </div>

                <div style={{ display: "flex", gap: 8 }}>
                  <button
                    type="submit"
                    disabled={busy}
                    style={{
                      flex: 1,
                      padding: "10px 16px",
                      background: tokens["color.primary.base"],
                      color: tokens["color.text.inverse"],
                      border: "none",
                      borderRadius: tokens["dimension.border.radius-sm"],
                      cursor: "pointer",
                      fontSize: tokens["typography.size.200"],
                      fontWeight: Number(tokens["typography.weight.medium"]),
                    }}
                  >
                    {busy ? (locale === "bn" ? "যাচাই হচ্ছে…" : "Verifying…") : t.authVerifyOtpBtn}
                  </button>
                  <button
                    type="button"
                    onClick={() => { setOtpSent(false); setError(null); }}
                    style={{
                      padding: "10px 14px",
                      background: tokens["color.surface.canvas"],
                      color: tokens["color.text.secondary"],
                      border: `1px solid ${tokens["color.border.default"]}`,
                      borderRadius: tokens["dimension.border.radius-sm"],
                      cursor: "pointer",
                      fontSize: tokens["typography.size.100"],
                    }}
                  >
                    {locale === "bn" ? "পরিবর্তন" : "Change"}
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        {/* TAB 2: CREDENTIALS & DEMO PERSONAS */}
        {activeTab === "credentials" && (
          <div>
            <p
              style={{
                margin: "0 0 12px",
                color: tokens["color.text.secondary"],
                fontSize: tokens["typography.size.100"],
              }}
            >
              {locale === "bn"
                ? "ওডু ইআরপি অ্যাকাউন্ট বা এক-ক্লিক ডেমো পারসোনা:"
                : "Sign in with your Odoo ERP account or select a one-click persona:"}
            </p>

            {/* One-click Persona Buttons */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 16 }}>
              <button
                type="button"
                disabled={busy}
                onClick={() => handlePersonaLogin("admin", "admin")}
                style={{
                  padding: "8px 10px",
                  background: tokens["color.surface.secondary"],
                  color: tokens["color.text.primary"],
                  border: `1px solid ${tokens["color.border.default"]}`,
                  borderRadius: tokens["dimension.border.radius-sm"],
                  fontSize: tokens["typography.size.100"],
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                <strong>Mitchell Admin</strong>
                <div style={{ fontSize: "11px", color: tokens["color.text.secondary"] }}>
                  {locale === "bn" ? "অ্যাডমিন পারসোনা" : "Admin Persona"}
                </div>
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => handlePersonaLogin("portal", "portal")}
                style={{
                  padding: "8px 10px",
                  background: tokens["color.surface.secondary"],
                  color: tokens["color.text.primary"],
                  border: `1px solid ${tokens["color.border.default"]}`,
                  borderRadius: tokens["dimension.border.radius-sm"],
                  fontSize: tokens["typography.size.100"],
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                <strong>Joel Willis</strong>
                <div style={{ fontSize: "11px", color: tokens["color.text.secondary"] }}>
                  {locale === "bn" ? "পোর্টাল কাস্টমার" : "Portal Customer"}
                </div>
              </button>
            </div>

            <form onSubmit={handleCredentialSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div>
                <label
                  htmlFor={usernameId}
                  style={{
                    display: "block",
                    marginBottom: 4,
                    fontSize: tokens["typography.size.200"],
                    color: tokens["color.text.primary"],
                  }}
                >
                  {locale === "bn" ? "ব্যবহারকারী নাম / ইমেইল" : "Username / Email"}
                </label>
                <input
                  id={usernameId}
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  style={{
                    width: "100%",
                    boxSizing: "border-box",
                    padding: "8px 10px",
                    background: tokens["color.surface.canvas"],
                    color: tokens["color.text.primary"],
                    border: `1px solid ${tokens["color.border.default"]}`,
                    borderRadius: tokens["dimension.border.radius-sm"],
                    fontSize: tokens["typography.size.200"],
                  }}
                />
              </div>

              <div>
                <label
                  htmlFor={passwordId}
                  style={{
                    display: "block",
                    marginBottom: 4,
                    fontSize: tokens["typography.size.200"],
                    color: tokens["color.text.primary"],
                  }}
                >
                  {locale === "bn" ? "পাসওয়ার্ড" : "Password"}
                </label>
                <input
                  id={passwordId}
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{
                    width: "100%",
                    boxSizing: "border-box",
                    padding: "8px 10px",
                    background: tokens["color.surface.canvas"],
                    color: tokens["color.text.primary"],
                    border: `1px solid ${tokens["color.border.default"]}`,
                    borderRadius: tokens["dimension.border.radius-sm"],
                    fontSize: tokens["typography.size.200"],
                  }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 4 }}>
                <button
                  type="button"
                  onClick={onClose}
                  style={{
                    padding: "8px 16px",
                    background: "transparent",
                    color: tokens["color.text.secondary"],
                    border: `1px solid ${tokens["color.border.default"]}`,
                    borderRadius: tokens["dimension.border.radius-sm"],
                    cursor: "pointer",
                    fontSize: tokens["typography.size.200"],
                  }}
                >
                  {locale === "bn" ? "বাতিল" : "Cancel"}
                </button>
                <button
                  type="submit"
                  disabled={busy}
                  style={{
                    padding: "8px 20px",
                    background: tokens["color.primary.base"],
                    color: tokens["color.text.inverse"],
                    border: "none",
                    borderRadius: tokens["dimension.border.radius-sm"],
                    cursor: "pointer",
                    fontSize: tokens["typography.size.200"],
                    fontWeight: Number(tokens["typography.weight.medium"]),
                  }}
                >
                  {busy
                    ? locale === "bn"
                      ? "যাচাই হচ্ছে…"
                      : "Signing In…"
                    : locale === "bn"
                    ? "লগইন করুন"
                    : "Sign In"}
                </button>
              </div>
            </form>
          </div>
        )}

        {error && (
          <p
            role="alert"
            style={{
              marginTop: 12,
              padding: "8px 12px",
              background: tokens["color.status.error-bg"],
              color: tokens["color.status.error"],
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: tokens["typography.size.200"],
            }}
          >
            {error}
          </p>
        )}
      </div>
    </div>
  );
}

/** Nav bar authentication controls (shows login button or user indicator + sign out) */
export function AuthControls() {
  const { user, openLoginModal, logoutUser } = useAuth();
  const { t } = useLanguage();

  if (!user) {
    return (
      <button
        onClick={openLoginModal}
        style={{
          padding: "4px 12px",
          background: tokens["color.primary.base"],
          color: tokens["color.text.inverse"],
          border: "none",
          borderRadius: tokens["dimension.border.radius-sm"],
          cursor: "pointer",
          fontSize: tokens["typography.size.200"],
          fontWeight: Number(tokens["typography.weight.semibold"]),
        }}
      >
        {t.signIn}
      </button>
    );
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <span
        title={user.name}
        style={{
          fontSize: tokens["typography.size.100"],
          background: tokens["color.surface.secondary"],
          color: tokens["color.text.primary"],
          padding: "2px 8px",
          borderRadius: tokens["dimension.border.radius-pill"],
          fontWeight: 600,
          maxWidth: 140,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
      >
        👤 {user.name}
      </span>
      <button
        onClick={logoutUser}
        style={{
          padding: "4px 8px",
          background: tokens["color.surface.canvas"],
          color: tokens["color.text.secondary"],
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-sm"],
          cursor: "pointer",
          fontSize: tokens["typography.size.100"],
        }}
      >
        {t.signOut}
      </button>
    </div>
  );
}
