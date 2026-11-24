/**
 * Seller portal sign-in & session (Odoo session via the Kong gateway).
 *
 * Same contract as the customer/corporate portals (security fix 2026-10-23):
 * - The browser authenticates against Odoo's /web/session/authenticate on
 *   the gateway origin with credentials: "include"; the Odoo session cookie
 *   is the ONLY credential. This module mints no bearer token and stores no
 *   profile — the gate asks /web/session/get_session_info on every load.
 * - The database name comes from NEXT_PUBLIC_ODOO_DB (not a secret, inlined
 *   at build time); the `fix_dev` fallback exists only outside production —
 *   a production build without it refuses to sign in.
 * - No default, demo or prefilled credentials anywhere.
 *
 * Exemption note (FF-39): like customer/corporate lib/auth.ts, this module
 * calls fetch() directly — authentication is not a business call.
 */
import { ApiError } from "./imports";

export interface UserSession {
  uid: number;
  name: string;
  username: string;
  partnerId: number;
  /** Odoo `is_internal_user`: true for 1000FiX staff, false for portal users. */
  isInternal: boolean;
}

export type AuthErrorKind = "credentials" | "config" | "network" | "rate_limited" | "server";

export class AuthError extends Error {
  constructor(public readonly kind: AuthErrorKind, message: string) {
    super(message);
    this.name = "AuthError";
  }
}

/** Fired on window when a data call reports an expired/missing Odoo session. */
export const SESSION_EXPIRED_EVENT = "fix:session-expired";

// Same-origin only. Auth calls go through the allow-listed /api/odoo bridge,
// which pins the Odoo origin server-side.
const API_BASE = "/api/odoo";

/**
 * sessionStorage keys purged on sign-in/out. `fix_token` is the fake bearer
 * the old lib/api.ts tokenGetter read (nothing legitimate ever set it here).
 */
const STALE_KEYS = ["fix_token"];

/**
 * The Odoo database to sign in to. NEXT_PUBLIC_ODOO_DB is inlined at build
 * time; `fix_dev` is the local fallback for non-production builds only.
 */
export function odooDatabase(): string {
  const configured = process.env.NEXT_PUBLIC_ODOO_DB?.trim();
  if (configured) return configured;
  if (process.env.NODE_ENV !== "production") return "fix_dev";
  throw new AuthError(
    "config",
    "Sign-in is not configured on this server (NEXT_PUBLIC_ODOO_DB is not set). Contact 1000FiX support.",
  );
}

/** The configuration problem that blocks sign-in, or null when sign-in can work. */
export function signInConfigError(): string | null {
  try {
    odooDatabase();
    return null;
  } catch (e) {
    return (e as Error).message;
  }
}

interface RpcErrorBody {
  code?: number | string;
  message?: string;
  data?: { name?: string; message?: string };
}

interface RpcEnvelope<T> {
  result?: T;
  error?: RpcErrorBody;
}

function isSessionExpiredBody(err: RpcErrorBody): boolean {
  return String(err.code) === "100" || err.data?.name === "odoo.http.SessionExpiredException";
}

async function rpc<T>(path: string, params: Record<string, unknown>): Promise<RpcEnvelope<T>> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      cache: "no-store",
      body: JSON.stringify({ jsonrpc: "2.0", method: "call", id: Date.now(), params }),
    });
  } catch (err) {
    throw new AuthError("network", `Cannot reach the 1000FiX sign-in server (${(err as Error).message}).`);
  }
  if (res.status === 429) {
    throw new AuthError("rate_limited", "Too many sign-in attempts. Wait a minute, then try again.");
  }
  if (!res.ok) {
    let message = `The sign-in server answered HTTP ${res.status}.`;
    try {
      const body = (await res.json()) as { error?: { message?: string } };
      if (body?.error?.message) message = body.error.message;
    } catch {
      /* non-JSON body: keep the status message */
    }
    throw new AuthError(res.status === 403 ? "credentials" : "server", message);
  }
  try {
    return (await res.json()) as RpcEnvelope<T>;
  } catch {
    throw new AuthError("server", "The sign-in server returned an unreadable response.");
  }
}

interface OdooSessionInfo {
  uid?: number | false | null;
  name?: string;
  username?: string;
  partner_id?: number;
  is_internal_user?: boolean;
}

function toSession(info: OdooSessionInfo | undefined): UserSession | null {
  if (!info || typeof info.uid !== "number" || info.uid <= 0) return null;
  return {
    uid: info.uid,
    name: info.name || info.username || `User #${info.uid}`,
    username: info.username || "",
    partnerId: typeof info.partner_id === "number" ? info.partner_id : 0,
    isInternal: info.is_internal_user === true,
  };
}

function purgeStaleKeys(): void {
  if (typeof window === "undefined") return;
  for (const key of STALE_KEYS) window.sessionStorage.removeItem(key);
}

/** The signed-in user of the current Odoo session, or null when there is none. */
export async function getSessionInfo(): Promise<UserSession | null> {
  const data = await rpc<OdooSessionInfo>("/web/session/get_session_info", {});
  if (data.error) {
    if (isSessionExpiredBody(data.error)) return null;
    throw new AuthError("server", data.error.data?.message || data.error.message || "Could not check your session.");
  }
  return toSession(data.result);
}

/** Username/email + password sign-in; sets the Odoo session cookie. */
export async function login(loginName: string, password: string): Promise<UserSession> {
  const db = odooDatabase();
  const data = await rpc<OdooSessionInfo>("/web/session/authenticate", {
    db,
    login: loginName.trim(),
    password,
  });
  if (data.error) {
    if (data.error.data?.name === "odoo.exceptions.AccessDenied") {
      throw new AuthError("credentials", "Wrong username/email or password.");
    }
    throw new AuthError("server", data.error.data?.message || data.error.message || "Sign-in failed.");
  }
  const session = toSession(data.result);
  if (!session) throw new AuthError("credentials", "Wrong username/email or password.");
  purgeStaleKeys();
  return session;
}

/** Ends the Odoo session (best effort) and clears local leftovers. */
export async function logout(): Promise<void> {
  try {
    await rpc("/web/session/destroy", {});
  } catch {
    /* network failure on sign-out: the local state is cleared regardless */
  }
  purgeStaleKeys();
}

/** True when a data call failed because the Odoo session is missing/expired. */
export function isSessionExpiredError(e: unknown): boolean {
  if (e instanceof ApiError) {
    return String(e.code) === "100" || /session expired/i.test(e.message);
  }
  return false;
}

/** Tell the auth gate the session is gone (it returns the user to sign-in). */
export function notifySessionExpired(): void {
  if (typeof window !== "undefined") window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
}
