/**
 * Customer Authentication & Session Management (W4 / P-11 contract).
 *
 * BROWSER CALLS ARE SAME-ORIGIN: every auth endpoint goes through the
 * Next rewrite /api/odoo/* → Odoo, so the Odoo session cookie is
 * first-party (localhost:3000), no Kong dependency in dev, and no
 * cross-origin cookie loss. NEXT_PUBLIC_FIX_API_BASE still overrides the
 * base for production deployments behind the Kong gateway.
 *
 * The Odoo session cookie is the ONLY credential: this module mints no
 * bearer/"session" token of its own (security fix 2026-10-23). sessionStorage
 * keeps only the display profile (`fix_user`), which grants nothing.
 */
export interface UserSession {
  uid: number;
  name: string;
  username: string;
  partnerId: number;
  isPortal: boolean;
}

const BROWSER_BASE =
  typeof window !== "undefined" && !process.env.NEXT_PUBLIC_FIX_API_BASE
    ? "/api/odoo"
    : (process.env.NEXT_PUBLIC_FIX_API_BASE || "http://127.0.0.1:8069").replace(/\/+$/, "");

function base(): string {
  return BROWSER_BASE;
}

/** Pre-fix builds stored a fake `session_<uid>_<ts>` bearer here; it is purged on login/logout. */
const LEGACY_TOKEN_KEY = "fix_token";

/**
 * The Odoo database to sign in to. NEXT_PUBLIC_ODOO_DB (a database name is
 * not a secret) is inlined at build time; the local `fix_dev` fallback exists
 * only in development builds — a production build without it refuses to log in.
 */
export function odooDatabase(): string {
  const configured = process.env.NEXT_PUBLIC_ODOO_DB?.trim();
  if (configured) return configured;
  if (process.env.NODE_ENV !== "production") return "fix_dev";
  throw new Error("Sign-in is not configured on this server (NEXT_PUBLIC_ODOO_DB is not set)");
}

async function jsonRpc(
  path: string,
  params: Record<string, unknown>
): Promise<{ result?: Record<string, unknown>; error?: { message?: string; data?: { message?: string } } } | null> {
  const res = await fetch(`${base()}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ jsonrpc: "2.0", method: "call", id: Date.now(), params }),
  });
  if (!res.ok) {
    let detail = "";
    try {
      detail = (await res.text()).slice(0, 120);
    } catch {
      /* no body */
    }
    throw new Error(`${path} → HTTP ${res.status}${detail ? ` (${detail})` : ""}`);
  }
  return res.json();
}

export async function login(
  loginName: string,
  password: string,
  db: string = odooDatabase()
): Promise<UserSession> {
  const data = await jsonRpc("/web/session/authenticate", { db, login: loginName, password });
  if (data?.error) {
    throw new Error(data.error.data?.message || data.error.message || "Invalid login credentials");
  }
  const result = data?.result as { uid?: number; name?: string; username?: string; partner_id?: number; is_portal?: boolean } | undefined;
  if (!result?.uid) {
    throw new Error("Invalid username or password");
  }
  const session: UserSession = {
    uid: result.uid,
    name: result.name || loginName,
    username: result.username || loginName,
    partnerId: result.partner_id || result.uid,
    isPortal: Boolean(result.is_portal),
  };

  if (typeof window !== "undefined") {
    window.sessionStorage.setItem("fix_user", JSON.stringify(session));
    window.sessionStorage.removeItem(LEGACY_TOKEN_KEY);
  }

  return session;
}

export async function sendOtp(
  phone: string
): Promise<{ sent: boolean; message: string; masked_phone: string; dev_code?: string }> {
  const data = await jsonRpc("/customer/auth/otp/send", { phone });
  if (data?.error) {
    throw new Error(data.error.data?.message || data.error.message || "Failed to send OTP");
  }
  const result = data?.result as { error?: { message?: string }; sent?: boolean; message?: string; masked_phone?: string; dev_code?: string } | undefined;
  if (result?.error) {
    throw new Error(result.error.message || "Failed to send OTP");
  }
  return {
    sent: Boolean(result?.sent),
    message: result?.message || "",
    masked_phone: result?.masked_phone || phone,
    dev_code: result?.dev_code,
  };
}

export async function loginWithOtp(phone: string, otp: string): Promise<UserSession> {
  const data = await jsonRpc("/customer/auth/otp/verify", { phone, otp });
  if (data?.error) {
    throw new Error(data.error.data?.message || data.error.message || "OTP verification failed");
  }
  const result = data?.result as { error?: { message?: string }; user?: { uid: number; name?: string; phone?: string; partner_id?: number; is_portal?: boolean } } | undefined;
  if (result?.error) {
    throw new Error(result.error.message || "Invalid OTP code");
  }
  const user = result?.user;
  if (!user?.uid) {
    throw new Error("Invalid OTP code");
  }
  const session: UserSession = {
    uid: user.uid,
    name: user.name || `Customer (${phone.slice(-4)})`,
    username: user.phone || phone,
    partnerId: user.partner_id || user.uid,
    isPortal: Boolean(user.is_portal),
  };

  if (typeof window !== "undefined") {
    window.sessionStorage.setItem("fix_user", JSON.stringify(session));
    window.sessionStorage.removeItem(LEGACY_TOKEN_KEY);
  }

  return session;
}

/**
 * Session truth (not the sessionStorage cache): asks Odoo whether the
 * httpOnly session cookie still maps to a user. Returns null when the
 * backend is unreachable — callers distinguish offline from signed-out
 * via `backendReachable`.
 */
export async function getSessionInfo(): Promise<{ user: UserSession | null; backendReachable: boolean }> {
  try {
    const data = await jsonRpc("/web/session/get_session_info", {});
    if (data?.error) return { user: null, backendReachable: true };
    const result = data?.result as { uid?: number; username?: string; name?: string; partner_id?: number; is_portal?: boolean } | undefined;
    if (!result?.uid) return { user: null, backendReachable: true };
    // A public/anonymous session carries a false-y username — signed out.
    const identified = result.username || result.name;
    if (!identified) return { user: null, backendReachable: true };
    return {
      user: {
        uid: result.uid,
        name: identified,
        username: result.username || "",
        partnerId: result.partner_id || result.uid,
        isPortal: Boolean(result.is_portal),
      },
      backendReachable: true,
    };
  } catch {
    return { user: null, backendReachable: false };
  }
}

export async function logout(): Promise<void> {
  try {
    await jsonRpc("/web/session/destroy", {});
  } catch {
    /* ignore network failure on logout */
  }

  if (typeof window !== "undefined") {
    window.sessionStorage.removeItem("fix_user");
    window.sessionStorage.removeItem(LEGACY_TOKEN_KEY);
  }
}

export function getCurrentUser(): UserSession | null {
  if (typeof window === "undefined") return null;
  const raw = window.sessionStorage.getItem("fix_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as UserSession;
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  return getCurrentUser() !== null;
}
