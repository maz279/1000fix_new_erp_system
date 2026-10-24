/**
 * POST /api/auth/callback — server-side OIDC code-for-token exchange
 * (security fix 2026-10-23).
 *
 * The /auth/callback page (the registered redirect_uri) posts the `code` and
 * `state` it received from Keycloak here. This handler:
 * - accepts same-origin JSON only (Origin REQUIRED and matching this host;
 *   Sec-Fetch-Site, when sent, must be same-origin);
 * - verifies `state` against the httpOnly cookie in constant time and uses the
 *   httpOnly PKCE verifier — both cookies are single-use and cleared on every
 *   outcome;
 * - exchanges the code with the non-public OIDC_CLIENT_SECRET (if set);
 * - returns only { access_token, expires_in, token_type } (no refresh / id
 *   token) with cache-control: no-store.
 */
import { NextResponse, type NextRequest } from "next/server";
import {
  OidcConfigError,
  STATE_COOKIE,
  TokenExchangeError,
  VERIFIER_COOKIE,
  exchangeAuthorizationCode,
  isHttpsRequest,
  oidcConfig,
  stateMatches,
  transactionCookieOptions,
} from "../oidc-auth";

export const dynamic = "force-dynamic";

/** Authorization codes / state values are short; anything larger is not a callback. */
const MAX_BODY_CHARS = 8_192;

function isSameOrigin(request: NextRequest): boolean {
  const fetchSite = request.headers.get("sec-fetch-site");
  if (fetchSite && fetchSite !== "same-origin") return false;
  const origin = request.headers.get("origin");
  if (!origin) return false;
  const forwardedHost = request.headers.get("x-forwarded-host")?.split(",")[0]?.trim();
  const host = forwardedHost || request.headers.get("host");
  if (!host) return false;
  try {
    return new URL(origin).host === host;
  } catch {
    return false;
  }
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  const secure = isHttpsRequest(request.url, request.headers.get("x-forwarded-proto"));

  const respond = (status: number, body: unknown): NextResponse => {
    const response = NextResponse.json(body, { status, headers: { "cache-control": "no-store" } });
    // Single-use transaction: clear state + verifier whatever the outcome.
    const expired = transactionCookieOptions(secure, 0);
    response.cookies.set(STATE_COOKIE, "", expired);
    response.cookies.set(VERIFIER_COOKIE, "", expired);
    return response;
  };
  const refuse = (status: number, code: string, message: string): NextResponse =>
    respond(status, { error: { code, message } });

  if (!isSameOrigin(request)) {
    return refuse(403, "cross_origin", "The sign-in callback only accepts same-origin requests");
  }
  if (!(request.headers.get("content-type") ?? "").toLowerCase().startsWith("application/json")) {
    return refuse(415, "unsupported_media_type", "Content-Type must be application/json");
  }

  const raw = await request.text();
  if (raw.length > MAX_BODY_CHARS) {
    return refuse(413, "payload_too_large", "Request body is too large");
  }
  let payload: unknown;
  try {
    payload = JSON.parse(raw);
  } catch {
    return refuse(400, "invalid_json", "Request body is not valid JSON");
  }
  const { code, state } = (payload ?? {}) as { code?: unknown; state?: unknown };
  if (typeof code !== "string" || !code || typeof state !== "string" || !state) {
    return refuse(400, "invalid_request", "code and state are required");
  }

  const expectedState = request.cookies.get(STATE_COOKIE)?.value;
  const verifier = request.cookies.get(VERIFIER_COOKIE)?.value;
  if (!verifier || !stateMatches(expectedState, state)) {
    return refuse(400, "invalid_state", "The sign-in attempt expired or did not start here — please sign in again");
  }

  let config;
  try {
    config = oidcConfig();
  } catch (err) {
    const message = err instanceof OidcConfigError ? err.message : "Single sign-on is not configured";
    return refuse(503, "oidc_not_configured", message);
  }

  try {
    const grant = await exchangeAuthorizationCode(config, code, verifier);
    return respond(200, grant);
  } catch (err) {
    const message = err instanceof TokenExchangeError ? err.message : "The sign-in could not be completed";
    return refuse(502, "token_exchange_failed", message);
  }
}
