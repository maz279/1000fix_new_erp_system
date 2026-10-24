/**
 * Server-only Keycloak OIDC helpers for the corporate portal (security fix
 * 2026-10-23) — used ONLY by app/api/auth/login/route.ts and
 * app/api/auth/callback/route.ts.
 *
 * - Authorization-code flow with PKCE (S256) and a `state` value, both held in
 *   short-lived httpOnly cookies scoped to /api/auth (never readable by JS).
 * - The code-for-token exchange runs here, server-side, with the confidential
 *   client secret from the NON-public env var OIDC_CLIENT_SECRET (optional: a
 *   public client relies on PKCE alone). No NEXT_PUBLIC_* variable holds a
 *   secret; `server-only` turns any client import of this module into a build
 *   error.
 *
 * Exemption note (FF-39): like lib/auth.ts, this OIDC auth file calls fetch()
 * directly — the token request goes to the Keycloak IdP (form-encoded, not the
 * API gateway's JSON-RPC), to an issuer URL validated below, with
 * redirect: "error".
 */
import "server-only";

import { createHash, randomBytes, timingSafeEqual } from "node:crypto";

export interface OidcConfig {
  issuer: string;
  clientId: string;
  redirectUri: string;
  clientSecret: string | null;
}

export class OidcConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "OidcConfigError";
  }
}

/** Local compose-stack defaults — development builds only. */
const DEV_ISSUER = "http://127.0.0.1:8080/realms/1000fix-dev";
const DEV_REDIRECT_URI = "http://127.0.0.1:3001/auth/callback";
const DEFAULT_CLIENT_ID = "1000fix-corporate-web";

export const STATE_COOKIE = "fix_oidc_state";
export const VERIFIER_COOKIE = "fix_oidc_verifier";
/** Cookie path: the transaction cookies are only ever sent to /api/auth/*. */
export const OIDC_COOKIE_PATH = "/api/auth";
/** Seconds a login transaction (state + verifier) stays valid. */
export const OIDC_TX_MAX_AGE = 600;

function firstSet(...values: Array<string | undefined>): string | undefined {
  for (const value of values) {
    const trimmed = value?.trim();
    if (trimmed) return trimmed;
  }
  return undefined;
}

function httpUrl(value: string, name: string): string {
  let url: URL;
  try {
    url = new URL(value);
  } catch {
    throw new OidcConfigError(`${name} is not a valid URL`);
  }
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new OidcConfigError(`${name} must be http or https`);
  }
  return value.replace(/\/+$/, "");
}

/**
 * Server-side OIDC configuration. The non-secret values may come from the
 * server-only OIDC_* variables or (for backwards compatibility) from the
 * NEXT_PUBLIC_OIDC_* ones; the secret ONLY from OIDC_CLIENT_SECRET.
 */
export function oidcConfig(): OidcConfig {
  const isDev = process.env.NODE_ENV !== "production";
  const issuer = firstSet(process.env.OIDC_ISSUER, process.env.NEXT_PUBLIC_OIDC_ISSUER) ?? (isDev ? DEV_ISSUER : undefined);
  const redirectUri =
    firstSet(process.env.OIDC_REDIRECT_URI, process.env.NEXT_PUBLIC_OIDC_REDIRECT_URI) ??
    (isDev ? DEV_REDIRECT_URI : undefined);
  if (!issuer || !redirectUri) {
    throw new OidcConfigError("Single sign-on is not configured on this server (OIDC_ISSUER / OIDC_REDIRECT_URI)");
  }
  return {
    issuer: httpUrl(issuer, "OIDC_ISSUER"),
    redirectUri: httpUrl(redirectUri, "OIDC_REDIRECT_URI"),
    clientId: firstSet(process.env.OIDC_CLIENT_ID, process.env.NEXT_PUBLIC_OIDC_CLIENT_ID) ?? DEFAULT_CLIENT_ID,
    clientSecret: firstSet(process.env.OIDC_CLIENT_SECRET) ?? null,
  };
}

function base64Url(bytes: Buffer): string {
  return bytes.toString("base64url");
}

/** A fresh login transaction: random state + PKCE verifier and its S256 challenge. */
export function newTransaction(): { state: string; verifier: string; challenge: string } {
  const state = base64Url(randomBytes(32));
  const verifier = base64Url(randomBytes(32)); // 43 chars, within RFC 7636's 43..128
  const challenge = base64Url(createHash("sha256").update(verifier, "ascii").digest());
  return { state, verifier, challenge };
}

export function authorizationUrl(config: OidcConfig, state: string, challenge: string): string {
  const params = new URLSearchParams({
    client_id: config.clientId,
    redirect_uri: config.redirectUri,
    response_type: "code",
    scope: "openid profile email",
    state,
    code_challenge: challenge,
    code_challenge_method: "S256",
  });
  return `${config.issuer}/protocol/openid-connect/auth?${params}`;
}

/** Constant-time comparison of the returned `state` with the cookie value. */
export function stateMatches(expected: string | undefined, received: string): boolean {
  if (!expected) return false;
  const a = Buffer.from(expected, "utf8");
  const b = Buffer.from(received, "utf8");
  return a.length === b.length && timingSafeEqual(a, b);
}

/** Cookie attributes of the login-transaction cookies. */
export function transactionCookieOptions(secure: boolean, maxAge: number = OIDC_TX_MAX_AGE): {
  httpOnly: true;
  sameSite: "lax";
  secure: boolean;
  path: string;
  maxAge: number;
} {
  // SameSite=Lax: the callback is reached by a top-level navigation from the IdP.
  return { httpOnly: true, sameSite: "lax", secure, path: OIDC_COOKIE_PATH, maxAge };
}

/** True when the request reached the portal over TLS (directly or via the TLS-terminating gateway). */
export function isHttpsRequest(url: string, forwardedProto: string | null): boolean {
  const proto = forwardedProto?.split(",")[0]?.trim().toLowerCase();
  if (proto) return proto === "https";
  return url.startsWith("https:");
}

export interface TokenGrant {
  access_token: string;
  expires_in: number;
  token_type: string;
}

export class TokenExchangeError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "TokenExchangeError";
  }
}

/** Exchange an authorization code (+ PKCE verifier) for an access token, server-side. */
export async function exchangeAuthorizationCode(
  config: OidcConfig,
  code: string,
  verifier: string,
): Promise<TokenGrant> {
  const tokenUrl = `${config.issuer}/protocol/openid-connect/token`;
  const body = new URLSearchParams({
    grant_type: "authorization_code",
    code,
    client_id: config.clientId,
    redirect_uri: config.redirectUri,
    code_verifier: verifier,
  });
  if (config.clientSecret) body.set("client_secret", config.clientSecret);

  let res: Response;
  try {
    res = await fetch(tokenUrl, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded", accept: "application/json" },
      body,
      redirect: "error",
      cache: "no-store",
    });
  } catch {
    throw new TokenExchangeError("The identity provider is unreachable");
  }
  if (!res.ok) {
    throw new TokenExchangeError(`The identity provider refused the authorization code (HTTP ${res.status})`);
  }
  let data: unknown;
  try {
    data = await res.json();
  } catch {
    throw new TokenExchangeError("The identity provider returned an unreadable token response");
  }
  const grant = data as Partial<Record<keyof TokenGrant, unknown>> | null;
  if (
    !grant ||
    typeof grant.access_token !== "string" ||
    !grant.access_token ||
    typeof grant.expires_in !== "number" ||
    !Number.isFinite(grant.expires_in)
  ) {
    throw new TokenExchangeError("The identity provider returned a malformed token response");
  }
  return {
    access_token: grant.access_token,
    expires_in: grant.expires_in,
    token_type: typeof grant.token_type === "string" ? grant.token_type : "Bearer",
  };
}
