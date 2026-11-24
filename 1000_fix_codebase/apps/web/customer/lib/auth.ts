/**
 * Customer Authentication & Session Management (W4 / P-11 contract).
 *
 * BROWSER CALLS ARE SAME-ORIGIN: every auth endpoint goes through the
 * Next bridge /api/odoo/* → Odoo (allow-listed in app/api/odoo), so the
 * Odoo session cookie is first-party (localhost:3000), no Kong dependency
 * in dev, and no cross-origin cookie loss.
 *
 * CUSTOMERS ONLY (2026-11-24): this is the customer portal. A staff/admin
 * Odoo login is refused here — staff use the operations portal (P03) — so a
 * portal session can never carry ERP back-office authority into this app.
 * The rule is enforced right after Odoo answers, where `is_internal_user`
 * is authoritative; the session is destroyed before the error is raised.
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

type JsonRpcAnswer = {
  result?: Record<string, unknown>;
  error?: { message?: string; data?: { message?: string } };
};

async function jsonRpc(path: string, params: Record<string, unknown>): Promise<JsonRpcAnswer | null> {
  const res = await fetch(`${base()}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ jsonrpc: "2.0", method: "call", id: Date.now(), params }),
  });
  const text = await res.text();
  // Odoo answers most business errors with HTTP 200 + {error}. The customer
  // bridge answers its own refusals (staff login, disallowed path) with a
  // non-2xx + the same JSON-RPC error shape — surface that message too.
  let parsed: JsonRpcAnswer | null = null;
  try {
    parsed = JSON.parse(text) as JsonRpcAnswer;
  } catch {
    parsed = null;
  }
  if (parsed?.error) return parsed;
  if (!res.ok) {
    throw new Error(`${path} → HTTP ${res.status}${text ? ` (${text.slice(0, 120)})` : ""}`);
  }
  return parsed;
}

/** Drops the server-side Odoo session. Swallows network failures on purpose. */
async function destroySession(): Promise<void> {
  try {
    await jsonRpc("/web/session/destroy", {});
  } catch {
    /* a refused login must not fail on cleanup */
  }
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
  const result = data?.result as {
    uid?: number;
    name?: string;
    username?: string;
    partner_id?: number;
    is_portal?: boolean;
    is_internal_user?: boolean;
  } | undefined;
  if (!result?.uid) {
    throw new Error("Invalid username or password");
  }
  // Customer portal boundary: an internal (staff/back-office) account is not
  // a customer account. Destroy the just-created session before refusing so
  // nothing staff-authorised lingers behind the sign-in screen.
  const internal = result.is_internal_user === true;
  if (internal || result.is_portal === false) {
    await destroySession();
    throw new Error(
      "This is the customer portal. Staff and administrator accounts must sign in through the operations portal."
    );
  }
  const session: UserSession = {
    uid: result.uid,
    name: result.name || loginName,
    username: result.username || loginName,
    partnerId: result.partner_id || result.uid,
    isPortal: true,
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
    isPortal: true,
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
    const result = data?.result as {
      uid?: number;
      username?: string;
      name?: string;
      partner_id?: number;
      is_portal?: boolean;
      is_internal_user?: boolean;
    } | undefined;
    if (!result?.uid) return { user: null, backendReachable: true };
    // A public/anonymous session carries a false-y username — signed out.
    const identified = result.username || result.name;
    if (!identified) return { user: null, backendReachable: true };
    // Internal staff sessions are not customer sessions; the customer portal
    // treats them as signed out (defence in depth after the login guard).
    if (result.is_internal_user === true) return { user: null, backendReachable: true };
    return {
      user: {
        uid: result.uid,
        name: identified,
        username: result.username || "",
        partnerId: result.partner_id || result.uid,
        isPortal: true,
      },
      backendReachable: true,
    };
  } catch {
    return { user: null, backendReachable: false };
  }
}

/**
 * Staff-session probe for the P02 technician workbench. Unlike
 * `getSessionInfo` (which deliberately hides internal sessions from the
 * customer portal), this reports whether the current cookie is an internal
 * user — the technician page is staff-only and must never render for a
 * customer. Odoo remains the authority; the relay still refuses a portal
 * session on every API call.
 */
export async function getStaffSession(): Promise<{ authenticated: boolean; internal: boolean }> {
  try {
    const data = await jsonRpc("/web/session/get_session_info", {});
    if (data?.error) return { authenticated: false, internal: false };
    const result = data?.result as { uid?: number; username?: string; is_internal_user?: boolean } | undefined;
    return {
      authenticated: Boolean(result?.uid && (result.username || result.is_internal_user)),
      internal: result?.is_internal_user === true,
    };
  } catch {
    return { authenticated: false, internal: false };
  }
}

export async function logout(): Promise<void> {
  await destroySession();

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
