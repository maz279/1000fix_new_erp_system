/**
 * Corporate Authentication & Session Management (W4 / P-11 contract).
 * Supports both:
 * 1. Direct Odoo session authentication via Kong gateway (/web/session/authenticate)
 *    with credentials: "include" for browser-preserved session cookies.
 * 2. Keycloak OIDC authorization code flow for enterprise SSO.
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

const API_BASE = (process.env.NEXT_PUBLIC_FIX_API_BASE || "http://127.0.0.1:8000").replace(/\/+$/, "");

// Public OIDC metadata — from env at build time
const OIDC_ISSUER = process.env.NEXT_PUBLIC_OIDC_ISSUER || "http://127.0.0.1:8080/realms/1000fix-dev";
const OIDC_CLIENT_ID = process.env.NEXT_PUBLIC_OIDC_CLIENT_ID || "1000fix-corporate-web";
const OIDC_REDIRECT_URI = process.env.NEXT_PUBLIC_OIDC_REDIRECT_URI || "http://127.0.0.1:3001/auth/callback";

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
  db: string = "fix_dev"
): Promise<UserSession> {
  const res = await fetch(`${API_BASE}/web/session/authenticate`, {
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

  if (!res.ok) {
    throw new Error(`Authentication server error: ${res.status}`);
  }

  const data = await res.json();
  if (data.error) {
    const msg = data.error.data?.message || data.error.message || "Invalid corporate credentials";
    throw new Error(msg);
  }

  const result = data.result;
  if (!result || !result.uid) {
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
    window.sessionStorage.setItem("fix_corporate_user", JSON.stringify(session));
    window.sessionStorage.setItem("fix_token", `session_${result.uid}_${Date.now()}`);
  }

  return session;
}

/** Direct session logout against Odoo via Kong gateway */
export async function logoutOdoo(): Promise<void> {
  try {
    await fetch(`${API_BASE}/web/session/destroy`, {
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
    window.sessionStorage.removeItem("fix_token");
    window.sessionStorage.removeItem("fix_token_expires");
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

/** Redirect to the Keycloak login page (OIDC SSO flow) */
export function login() {
  const issuer = validatedIssuer();
  const params = new URLSearchParams({
    client_id: OIDC_CLIENT_ID,
    redirect_uri: OIDC_REDIRECT_URI,
    response_type: "code",
    scope: "openid profile email",
  });
  window.location.href = `${issuer}/protocol/openid-connect/auth?${params}`;
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

/** Exchange authorization code for tokens (OIDC SSO callback) */
export async function exchangeCode(code: string): Promise<{
  access_token: string;
  expires_in: number;
}> {
  const issuer = validatedIssuer();
  const tokenUrl = `${issuer}/protocol/openid-connect/token`;
  if (!tokenUrl.startsWith(issuer)) {
    throw new Error("Token endpoint does not match the trusted issuer");
  }
  const body = new URLSearchParams({
    grant_type: "authorization_code",
    code,
    client_id: OIDC_CLIENT_ID,
    redirect_uri: OIDC_REDIRECT_URI,
  });
  const secret = process.env.NEXT_PUBLIC_OIDC_CLIENT_SECRET;
  if (secret) {
    body.set("client_secret", secret);
  }
  const res = await fetch(tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
    redirect: "error",
  });
  if (!res.ok) {
    throw new Error(`OIDC token exchange failed: ${res.status}`);
  }
  const data = await res.json();
  sessionStorage.setItem("fix_token", data.access_token);
  sessionStorage.setItem("fix_token_expires", String(Date.now() + data.expires_in * 1000));
  return data;
}
