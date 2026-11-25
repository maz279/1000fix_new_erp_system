"use client";

/**
 * Vendor portal auth gate — Odoo session sign-in (see lib/auth.ts).
 *
 * - AuthProvider asks /web/session/get_session_info on load; with no uid the
 *   gate sends the user to /login (the proxy already redirects when the
 *   session cookie is absent).
 * - A data call that fails with Odoo SessionExpired (lib/api.ts fires
 *   SESSION_EXPIRED_EVENT) returns the user to the sign-in screen.
 * - External portal for Odoo portal users linked to a supplier profile.
 *   Staff accounts are not refused here; the Odoo controllers resolve the
 *   vendor from the session's commercial partner (staff get the support view).
 * - English UI with Bengali subtitles (this app has no language dictionary);
 *   portal names and the session-expired notice come from the generated
 *   copy registry (uiCopy). Labelled inputs, managed focus, role="alert"
 *   errors. Tokens only (CFM-01). No prefilled or demo credentials.
 */
import { createContext, useCallback, useContext, useEffect, useId, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { tokens, uiCopy } from "../lib/imports";
import {
  AuthError,
  SESSION_EXPIRED_EVENT,
  getSessionInfo,
  login,
  logout,
  signInConfigError,
  type UserSession,
} from "../lib/auth";

/** P06/P10 are staff consoles; P05/P07/P08/P12 serve external portal users. */
const STAFF_ONLY = false as boolean;
const PORTAL_KEY = "nav.portal.p05";
/** Public before sign-in: the vendor landing page and the login page. */
const PUBLIC_ROUTES = new Set(["/", "/login"]);

/** Return path supplied by the proxy / login link. Same-site only. */
export function nextPath(): string {
  if (typeof window === "undefined") return "/dashboard";
  const raw = new URLSearchParams(window.location.search).get("next") || "/dashboard";
  if (!raw.startsWith("/") || raw.startsWith("//") || PUBLIC_ROUTES.has(raw)) return "/dashboard";
  return raw;
}

type Status = "checking" | "signed-out" | "signed-in" | "check-failed";

interface AuthContextValue {
  status: Status;
  user: UserSession | null;
  /** Why the user was sent back to sign-in (session expiry), if any. */
  notice: string | null;
  checkError: string | null;
  /** True right after an interactive sign-in (the gate moves focus to the page). */
  justSignedIn: boolean;
  signIn: (loginName: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  recheck: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<Status>("checking");
  const [user, setUser] = useState<UserSession | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [checkError, setCheckError] = useState<string | null>(null);
  const [justSignedIn, setJustSignedIn] = useState(false);

  const check = useCallback(async () => {
    setStatus("checking");
    setCheckError(null);
    try {
      const session = await getSessionInfo();
      setUser(session);
      setStatus(session ? "signed-in" : "signed-out");
    } catch (e) {
      setUser(null);
      setCheckError((e as Error).message);
      setStatus("check-failed");
    }
  }, []);

  useEffect(() => {
    void check();
  }, [check]);

  useEffect(() => {
    const onExpired = () => {
      setUser(null);
      setJustSignedIn(false);
      setNotice(`${uiCopy("common.session.expired", "en")} / ${uiCopy("common.session.expired", "bn")}`);
      setStatus("signed-out");
    };
    window.addEventListener(SESSION_EXPIRED_EVENT, onExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, onExpired);
  }, []);

  const signIn = useCallback(async (loginName: string, password: string) => {
    const session = await login(loginName, password);
    setUser(session);
    setNotice(null);
    setJustSignedIn(true);
    setStatus("signed-in");
  }, []);

  const signOut = useCallback(async () => {
    await logout();
    setUser(null);
    setNotice(null);
    setJustSignedIn(false);
    setStatus("signed-out");
  }, []);

  return (
    <AuthContext.Provider
      value={{ status, user, notice, checkError, justSignedIn, signIn, signOut, recheck: () => void check() }}
    >
      {children}
    </AuthContext.Provider>
  );
}

const panel: React.CSSProperties = {
  maxWidth: 440,
  margin: "48px auto",
  padding: 28,
  background: tokens["color.surface.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  boxShadow: tokens["shadow.md"],
};

const bnLine: React.CSSProperties = {
  display: "block",
  fontSize: tokens["typography.size.100"],
  color: tokens["color.text.secondary"],
  fontWeight: Number(tokens["typography.weight.normal"]),
};

const fieldLabel: React.CSSProperties = {
  display: "block",
  marginBottom: 4,
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
  color: tokens["color.text.primary"],
};

const input: React.CSSProperties = {
  width: "100%",
  boxSizing: "border-box",
  padding: "10px 12px",
  fontSize: tokens["typography.size.200"],
  color: tokens["color.text.primary"],
  background: tokens["color.surface.canvas"],
  border: `1px solid ${tokens["color.border.strong"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
};

const primaryBtn: React.CSSProperties = {
  minHeight: 44,
  padding: "10px 20px",
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.semibold"]),
  color: tokens["color.text.inverse"],
  background: tokens["color.primary.base"],
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
};

const secondaryBtn: React.CSSProperties = {
  padding: "4px 10px",
  fontSize: tokens["typography.size.100"],
  color: tokens["color.text.secondary"],
  background: tokens["color.surface.canvas"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
};

const alertBox: React.CSSProperties = {
  margin: "0 0 16px",
  padding: "10px 12px",
  fontSize: tokens["typography.size.200"],
  color: tokens["color.status.error"],
  background: tokens["color.status.error-bg"],
  border: `1px solid ${tokens["color.status.error-border"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
};

const BN_ERRORS: Record<string, string> = {
  credentials: "ভুল ব্যবহারকারী নাম/ইমেইল বা পাসওয়ার্ড।",
  rate_limited: "অনেকবার চেষ্টা করা হয়েছে। এক মিনিট পরে আবার চেষ্টা করুন।",
  network: "সাইন-ইন সার্ভারে পৌঁছানো যাচ্ছে না।",
  config: "এই সার্ভারে সাইন-ইন কনফিগার করা হয়নি।",
};

/** Signed-in user's name + sign-out, for the nav bar. Renders nothing when signed out. */
export function AuthStatus() {
  const { status, user, signOut } = useAuth();
  const [busy, setBusy] = useState(false);
  if (status !== "signed-in" || !user) return null;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <span
        title={user.username ? `${user.name} (${user.username})` : user.name}
        style={{
          fontSize: tokens["typography.size.100"],
          color: tokens["color.text.primary"],
          background: tokens["color.surface.secondary"],
          padding: "2px 10px",
          borderRadius: tokens["dimension.border.radius-pill"],
          maxWidth: 200,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
      >
        <span style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", clip: "rect(0 0 0 0)" }}>
          Signed in as{" "}
        </span>
        {user.name}
      </span>
      <button
        type="button"
        disabled={busy}
        onClick={() => {
          setBusy(true);
          void signOut().finally(() => setBusy(false));
        }}
        style={secondaryBtn}
      >
        {uiCopy("common.nav.chrome.signout", "en")}{" "}
        <span lang="bn">({uiCopy("common.nav.chrome.signout", "bn")})</span>
      </button>
    </div>
  );
}

/** Renders the page only for a signed-in (and, on staff consoles, internal) user. */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const { status, user, checkError, justSignedIn, recheck } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const contentRef = useRef<HTMLDivElement>(null);
  const isPublic = PUBLIC_ROUTES.has(pathname || "/");

  useEffect(() => {
    if (status === "signed-in" && justSignedIn) contentRef.current?.focus();
  }, [status, justSignedIn]);

  useEffect(() => {
    if (isPublic || status !== "signed-out") return;
    router.replace(`/login?next=${encodeURIComponent(pathname || "/dashboard")}`);
  }, [isPublic, status, pathname, router]);

  if (isPublic) return <>{children}</>;

  if (status === "checking") {
    return (
      <main style={panel}>
        <p role="status" aria-live="polite" style={{ margin: 0, color: tokens["color.text.secondary"] }}>
          Checking your session…
          <span lang="bn" style={bnLine}>আপনার সেশন যাচাই করা হচ্ছে…</span>
        </p>
        <noscript>This portal needs JavaScript to sign in.</noscript>
      </main>
    );
  }

  if (status === "check-failed") {
    return (
      <main style={panel}>
        <div role="alert" style={alertBox}>
          Could not check your session: {checkError}
          <span lang="bn" style={bnLine}>আপনার সেশন যাচাই করা যায়নি।</span>
        </div>
        <button type="button" onClick={recheck} style={primaryBtn}>
          Try again <span lang="bn">(আবার চেষ্টা করুন)</span>
        </button>
      </main>
    );
  }

  if (status === "signed-out" || !user) {
    return (
      <main style={panel}>
        <p role="status" style={{ margin: 0, color: tokens["color.text.secondary"] }}>
          Redirecting to sign in…
          <span lang="bn" style={bnLine}>সাইন ইন পাতায় নিয়ে যাচ্ছে…</span>
        </p>
      </main>
    );
  }

  if (STAFF_ONLY && !user.isInternal) return <StaffOnly user={user} />;

  return (
    <div ref={contentRef} tabIndex={-1} style={{ outline: "none" }}>
      {children}
    </div>
  );
}

function StaffOnly({ user }: { user: UserSession }) {
  const { signOut } = useAuth();
  const headingRef = useRef<HTMLHeadingElement>(null);
  useEffect(() => headingRef.current?.focus(), []);
  return (
    <main style={panel}>
      <h1 ref={headingRef} tabIndex={-1} style={{ margin: "0 0 8px", fontSize: tokens["typography.size.400"], color: tokens["color.text.primary"], outline: "none" }}>
        This portal is for 1000FiX staff
        <span lang="bn" style={bnLine}>এই পোর্টালটি ১০০০FiX কর্মীদের জন্য</span>
      </h1>
      <p role="alert" style={{ margin: "0 0 16px", color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
        You are signed in as {user.name}, which is not a staff account.
        <span lang="bn" style={bnLine}>আপনার অ্যাকাউন্টটি কর্মী অ্যাকাউন্ট নয়।</span>
      </p>
      <button type="button" onClick={() => void signOut()} style={primaryBtn}>
        {uiCopy("common.nav.chrome.signout", "en")} <span lang="bn">({uiCopy("common.nav.chrome.signout", "bn")})</span>
      </button>
    </main>
  );
}

export function SignInScreen() {
  const { signIn, notice, status, user } = useAuth();
  const router = useRouter();
  const usernameId = useId();
  const passwordId = useId();
  const errorId = useId();
  const usernameRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);

  // Never prefilled: the portal ships no default or demo credentials.
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<{ kind: string; message: string; bn: string | null } | null>(null);
  const configError = signInConfigError();

  useEffect(() => {
    usernameRef.current?.focus();
  }, []);

  useEffect(() => {
    if (status === "signed-in" && user) router.replace(nextPath());
  }, [status, user, router]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await signIn(username, password);
    } catch (err) {
      const kind = err instanceof AuthError ? err.kind : "server";
      setError({ kind, message: (err as Error).message || "Sign-in failed.", bn: BN_ERRORS[kind] ?? null });
      setPassword("");
      setBusy(false);
      (kind === "credentials" ? passwordRef : usernameRef).current?.focus();
    }
  };

  const credentialsInvalid = error?.kind === "credentials";

  return (
    <main style={panel} aria-labelledby={`${usernameId}-title`}>
      <h1
        id={`${usernameId}-title`}
        style={{ margin: "0 0 4px", fontSize: tokens["typography.size.400"], fontWeight: Number(tokens["typography.weight.bold"]), color: tokens["color.text.primary"] }}
      >
        Sign in — {uiCopy(PORTAL_KEY, "en")}
        <span lang="bn" style={bnLine}>সাইন ইন — {uiCopy(PORTAL_KEY, "bn")}</span>
      </h1>
      <p style={{ margin: "8px 0 20px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
        For 1000FiX suppliers. Sign in with the vendor account issued to you.
        <span lang="bn" style={bnLine}>১০০০FiX সরবরাহকারীদের জন্য। আপনার দেওয়া ভেন্ডর অ্যাকাউন্ট দিয়ে সাইন ইন করুন।</span>
      </p>

      {notice && (
        <p
          role="status"
          style={{
            margin: "0 0 16px",
            padding: "10px 12px",
            fontSize: tokens["typography.size.200"],
            color: tokens["color.status.warning-bold"],
            background: tokens["color.status.warning-bg"],
            border: `1px solid ${tokens["color.status.warning-border"]}`,
            borderRadius: tokens["dimension.border.radius-sm"],
          }}
        >
          {notice}
        </p>
      )}

      {configError && (
        <p role="alert" style={alertBox}>
          {configError}
          <span lang="bn" style={bnLine}>{BN_ERRORS.config}</span>
        </p>
      )}

      {error && (
        <p id={errorId} role="alert" style={alertBox}>
          {error.message}
          {error.bn && <span lang="bn" style={bnLine}>{error.bn}</span>}
        </p>
      )}

      <form onSubmit={onSubmit}>
        <div style={{ marginBottom: 14 }}>
          <label htmlFor={usernameId} style={fieldLabel}>
            Username or email <span lang="bn" style={{ color: tokens["color.text.secondary"] }}>(ব্যবহারকারী নাম বা ইমেইল)</span>
          </label>
          <input
            ref={usernameRef}
            id={usernameId}
            name="username"
            type="text"
            autoComplete="username"
            autoCapitalize="none"
            spellCheck={false}
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            aria-invalid={credentialsInvalid || undefined}
            aria-describedby={error ? errorId : undefined}
            style={input}
          />
        </div>
        <div style={{ marginBottom: 20 }}>
          <label htmlFor={passwordId} style={fieldLabel}>
            Password <span lang="bn" style={{ color: tokens["color.text.secondary"] }}>(পাসওয়ার্ড)</span>
          </label>
          <input
            ref={passwordRef}
            id={passwordId}
            name="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            aria-invalid={credentialsInvalid || undefined}
            aria-describedby={error ? errorId : undefined}
            style={input}
          />
        </div>
        <button
          type="submit"
          disabled={busy || configError !== null}
          aria-busy={busy || undefined}
          style={{
            ...primaryBtn,
            width: "100%",
            cursor: busy ? "wait" : configError ? "not-allowed" : "pointer",
            opacity: busy || configError ? 0.7 : 1,
          }}
        >
          {busy ? "Signing in…" : "Sign in"}{" "}
          <span lang="bn">({busy ? "সাইন ইন হচ্ছে…" : "সাইন ইন"})</span>
        </button>
      </form>
    </main>
  );
}
