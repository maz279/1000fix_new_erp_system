/**
 * Corporate Authentication & Session Management (W4 / P-11 contract).
 * Supports both:
 * 1. Direct Odoo session authentication via Kong gateway (/web/session/authenticate)
 *    with credentials: "include" for browser-preserved session cookies.
 * 2. Keycloak OIDC authorization code flow for enterprise SSO.
 *
 * Security fix 2026-10-23:
 * - Odoo sign-in mints no bearer token of its own: the Odoo session cookie is
 *   the credential (no more `session_<uid>_<ts>` in sessionStorage).
 * - The database name comes from NEXT_PUBLIC_ODOO_DB (not a secret); the
 *   `fix_dev` fallback exists only in development builds.
 * - OIDC: the browser only navigates to /api/auth/login (server: state + PKCE
 *   S256 in httpOnly cookies) and posts the returned code + state to
 *   /api/auth/callback (server: state check + code exchange with the
 *   non-public OIDC_CLIENT_SECRET). No client secret is ever read here.
 *
 * Exemption note (FF-39): auth.ts is permitted to call fetch() directly
 * to authenticate browser sessions without going through business logic layers.
 */

export interface UserSession {
  uid: number;
  name: string;
  username: string;
  partnerId: number;
  isPortal: boolean;
}

// Same-origin only. Auth calls below use the literal /api/odoo bridge path:
// the browser never learns or supplies the backend origin, and the bridge
// (app/api/odoo) pins it server-side with a path allow-list.

// Public OIDC metadata (used only for the SSO logout redirect) — from env at build time
const OIDC_ISSUER = process.env.NEXT_PUBLIC_OIDC_ISSUER || "http://127.0.0.1:8080/realms/1000fix-dev";
const OIDC_CLIENT_ID = process.env.NEXT_PUBLIC_OIDC_CLIENT_ID || "1000fix-corporate-web";
const OIDC_REDIRECT_URI = process.env.NEXT_PUBLIC_OIDC_REDIRECT_URI || "http://127.0.0.1:3001/auth/callback";

/** sessionStorage keys of the OIDC access token (read by lib/api.ts as the bearer). */
const TOKEN_KEY = "fix_token";
const TOKEN_EXPIRES_KEY = "fix_token_expires";

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

function validatedIssuer(): string {
  const url = new URL(OIDC_ISSUER);
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error("OIDC_ISSUER must be http or https");
  }
  return OIDC_ISSUER;
}

/** Direct session login against Odoo via Kong gateway */
export async function loginWithOdoo(
  loginName: string,
  password: string,
  db: string = odooDatabase()
): Promise<UserSession> {
  const res = await fetch("/api/odoo/web/session/authenticate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "call",
      id: Date.now(),
      params: { db, login: loginName, password },
    }),
  });

  let data: {
    error?: { message?: string; data?: { message?: string } };
    result?: {
      uid?: number;
      name?: string;
      username?: string;
      partner_id?: number;
      is_internal_user?: boolean;
      is_portal?: boolean;
    };
  } = {};
  try {
    data = await res.json();
  } catch {
    /* non-JSON body handled below */
  }
  if (data.error) {
    const msg = data.error.data?.message || data.error.message || "Invalid corporate credentials";
    throw new Error(msg);
  }
  if (!res.ok) {
    throw new Error(`Authentication server error: ${res.status}`);
  }

  const result = data.result;
  if (!result || !result.uid) {
    throw new Error("Invalid username or password");
  }
  // The bridge refuses internal logins; this is defence in depth so no
  // alternate path can turn the corporate portal into a back-office session.
  if (result.is_internal_user === true || result.is_portal === false) {
    await logoutOdoo();
    throw new Error(
      "This portal is for corporate clients. Staff and administrator accounts use the operations portal."
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
    window.sessionStorage.setItem("fix_corporate_user", JSON.stringify(session));
    // The Odoo session cookie is the credential; drop any stale bearer so
    // lib/api.ts does not send a token that is not this session's.
    window.sessionStorage.removeItem(TOKEN_KEY);
    window.sessionStorage.removeItem(TOKEN_EXPIRES_KEY);
  }

  return session;
}

/**
 * Session truth from Odoo (not the sessionStorage cache). Internal sessions
 * are reported as signed out — this portal is corporate-client only.
 */
export async function getSessionInfo(): Promise<{
  user: UserSession | null;
  backendReachable: boolean;
}> {
  try {
    const res = await fetch("/api/odoo/web/session/get_session_info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      cache: "no-store",
      body: JSON.stringify({ jsonrpc: "2.0", method: "call", id: Date.now(), params: {} }),
    });
    const data = (await res.json()) as {
      result?: {
        uid?: number;
        username?: string;
        name?: string;
        partner_id?: number;
        is_internal_user?: boolean;
      };
      error?: unknown;
    };
    if (data.error || !data.result?.uid) return { user: null, backendReachable: true };
    const r = data.result;
    const uid = r.uid;
    if (!uid) return { user: null, backendReachable: true };
    const identified = r.username || r.name;
    if (!identified || r.is_internal_user === true) return { user: null, backendReachable: true };
    return {
      user: {
        uid,
        name: identified,
        username: r.username || "",
        partnerId: r.partner_id || uid,
        isPortal: true,
      },
      backendReachable: true,
    };
  } catch {
    return { user: null, backendReachable: false };
  }
}

/** Direct session logout against Odoo through the same-origin bridge */
export async function logoutOdoo(): Promise<void> {
  try {
    await fetch("/api/odoo/web/session/destroy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        id: Date.now(),
        params: {},
      }),
    });
  } catch {
    /* ignore network failure on logout */
  }

  if (typeof window !== "undefined") {
    window.sessionStorage.removeItem("fix_corporate_user");
    window.sessionStorage.removeItem(TOKEN_KEY);
    window.sessionStorage.removeItem(TOKEN_EXPIRES_KEY);
  }
}

/** Get current authenticated user session */
export function getCurrentUser(): UserSession | null {
  if (typeof window === "undefined") return null;
  const raw = window.sessionStorage.getItem("fix_corporate_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as UserSession;
  } catch {
    return null;
  }
}

/** Check if user is authenticated */
export function isAuthenticated(): boolean {
  return getCurrentUser() !== null;
}

/**
 * Start the Keycloak OIDC SSO flow. The server route mints `state` and the
 * PKCE verifier (httpOnly cookies) and redirects to the IdP.
 */
export function login() {
  window.location.assign("/api/auth/login");
}

/** Log out from Keycloak SSO */
export function logout() {
  logoutOdoo();
  const issuer = validatedIssuer();
  const params = new URLSearchParams({
    client_id: OIDC_CLIENT_ID,
    redirect_uri: OIDC_REDIRECT_URI.replace("/auth/callback", ""),
  });
  window.location.href = `${issuer}/protocol/openid-connect/logout?${params}`;
}

/**
 * OIDC SSO callback: hand the authorization code and `state` to the server
 * route, which verifies the state against its httpOnly cookie and performs the
 * PKCE code-for-token exchange with the confidential client secret.
 */
export async function exchangeCode(code: string, state: string): Promise<{
  access_token: string;
  expires_in: number;
}> {
  const res = await fetch("/api/auth/callback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
    cache: "no-store",
    body: JSON.stringify({ code, state }),
  });
  let data: { access_token?: unknown; expires_in?: unknown; error?: { message?: string } } = {};
  try {
    data = await res.json();
  } catch {
    /* non-JSON body — reported below */
  }
  if (!res.ok || typeof data.access_token !== "string" || typeof data.expires_in !== "number") {
    throw new Error(data.error?.message || `OIDC sign-in failed: ${res.status}`);
  }
  sessionStorage.setItem(TOKEN_KEY, data.access_token);
  sessionStorage.setItem(TOKEN_EXPIRES_KEY, String(Date.now() + data.expires_in * 1000));
  return { access_token: data.access_token, expires_in: data.expires_in };
}
