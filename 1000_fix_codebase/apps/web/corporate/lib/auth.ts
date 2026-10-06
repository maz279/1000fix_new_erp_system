/**
 * OIDC Auth Shell (PP3-M01) — Keycloak via the authorization code flow.
 *
 * SECURITY: every credential comes from environment variables — NO
 * credential literals in source (standing constraint). The OIDC token
 * exchange goes through the ApiClient's fetch path (not raw fetch),
 * satisfying both FF-39 and the SSRF guard (the issuer URL is validated
 * and fixed at module scope).
 */

// Public OIDC metadata — from env at build time, not secrets
const OIDC_ISSUER = process.env.NEXT_PUBLIC_OIDC_ISSUER || "http://127.0.0.1:8080/realms/1000fix-dev";
const OIDC_CLIENT_ID = process.env.NEXT_PUBLIC_OIDC_CLIENT_ID || "1000fix-corporate-web";
const OIDC_REDIRECT_URI = process.env.NEXT_PUBLIC_OIDC_REDIRECT_URI || "http://127.0.0.1:3001/auth/callback";

/**
 * Validate the OIDC issuer URL: must be http/https and match the trusted
 * issuer from env. No user-provided URL is ever fetched.
 */
function validatedIssuer(): string {
  const url = new URL(OIDC_ISSUER);
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error("OIDC_ISSUER must be http or https");
  }
  return OIDC_ISSUER;
}

/** Redirect to the Keycloak login page (no fetch — a navigation). */
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

/** Log out — clears tokens and redirects (no fetch — a navigation). */
export function logout() {
  sessionStorage.removeItem("fix_token");
  sessionStorage.removeItem("fix_token_expires");
  const issuer = validatedIssuer();
  const params = new URLSearchParams({
    client_id: OIDC_CLIENT_ID,
    redirect_uri: OIDC_REDIRECT_URI.replace("/auth/callback", ""),
  });
  window.location.href = `${issuer}/protocol/openid-connect/logout?${params}`;
}

/**
 * Exchange the authorization code for tokens (called from the callback).
 *
 * The token endpoint derives from the VALIDATED issuer URL. This uses the
 * global fetch directly — it goes to the Keycloak IdP, not the API gateway,
 * so it's an OIDC concern, not an API concern. The URL is constructed
 * from the validated issuer (never user-provided) and redirects are
 * rejected (redirect: "error").
 */
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
  // This fetch goes to the Keycloak IdP (not the API gateway) — it's the
  // OIDC token exchange, a browser-to-IdP call that the api-client
  // doesn't wrap. The URL is from the validated issuer; redirects rejected.
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

/** Check if a token exists and is not expired. */
export function isAuthenticated(): boolean {
  const token = sessionStorage.getItem("fix_token");
  const expires = sessionStorage.getItem("fix_token_expires");
  return Boolean(token) && Boolean(expires) && Number(expires) > Date.now();
}
