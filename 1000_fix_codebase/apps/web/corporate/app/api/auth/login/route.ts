/**
 * GET /api/auth/login — starts the Keycloak OIDC authorization-code flow
 * (security fix 2026-10-23): mints `state` + a PKCE (S256) verifier, keeps
 * both in httpOnly cookies scoped to /api/auth, and redirects to the IdP with
 * the state and the code challenge. The browser never sees the verifier.
 */
import { NextResponse, type NextRequest } from "next/server";
import {
  OidcConfigError,
  STATE_COOKIE,
  VERIFIER_COOKIE,
  authorizationUrl,
  isHttpsRequest,
  newTransaction,
  oidcConfig,
  transactionCookieOptions,
} from "../oidc-auth";

export const dynamic = "force-dynamic";

export function GET(request: NextRequest): NextResponse {
  let config;
  try {
    config = oidcConfig();
  } catch (err) {
    const message = err instanceof OidcConfigError ? err.message : "Single sign-on is not configured";
    return NextResponse.json(
      { error: { code: "oidc_not_configured", message } },
      { status: 503, headers: { "cache-control": "no-store" } },
    );
  }

  const { state, verifier, challenge } = newTransaction();
  const response = NextResponse.redirect(authorizationUrl(config, state, challenge), 302);
  response.headers.set("cache-control", "no-store");
  const options = transactionCookieOptions(isHttpsRequest(request.url, request.headers.get("x-forwarded-proto")));
  response.cookies.set(STATE_COOKIE, state, options);
  response.cookies.set(VERIFIER_COOKIE, verifier, options);
  return response;
}
