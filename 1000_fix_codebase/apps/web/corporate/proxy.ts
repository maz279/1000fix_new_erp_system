// PP7-M03 — per-request nonce Content-Security-Policy (D17) + the P04
// customer-account access boundary (2026-11-24).
//
// Next 16 pattern: the proxy (formerly middleware) generates a nonce per
// request and sets BOTH the CSP on the *request* headers — Next reads it and
// stamps the nonce onto its own bootstrap scripts — and the CSP on the
// *response*. `strict-dynamic` lets the nonce-bearing bootstrap load the rest
// of the chunk graph.
//
// CORPORATE PORTAL BOUNDARY:
// - The portal talks to Odoo only through the same-origin /api/odoo
//   allow-list (app/api/odoo). There is no Kong dependency and no direct
//   browser access to the ERP; frame-src is 'none'.
// - Corporate-account routes require a signed-in session. Odoo remains
//   authoritative on every /corporate/* call (auth="user", commercial-partner
//   fenced), so this gate is the first hop, not the security boundary.
import { NextRequest, NextResponse } from "next/server";

const FRAME_ANCESTORS = process.env.FRAME_ANCESTORS?.trim() || "'self'";
const CONNECT_SRC = [
  "'self'",
  process.env.CSP_CONNECT_SRC?.trim() ?? "",
].filter(Boolean).join(" ");

/** Odoo's session cookie (odoo/http.py). */
const ODOO_SESSION_COOKIE = "session_id";

/**
 * Corporate-account routes. Public: the landing page (/), sign-in (/login),
 * and the health bridge.
 */
const PROTECTED_PREFIXES = [
  "/dashboard",
  "/estate",
  "/contracts",
  "/invoices",
  "/service-requests",
  "/tenders",
  "/reports",
  "/account",
];

function isProtected(pathname: string): boolean {
  return PROTECTED_PREFIXES.some(
    (p) => pathname === p || pathname.startsWith(`${p}/`)
  );
}

export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  if (isProtected(pathname) && !request.cookies.get(ODOO_SESSION_COOKIE)?.value) {
    const login = new URL("/login", request.url);
    login.searchParams.set("next", `${pathname}${search}`);
    return NextResponse.redirect(login);
  }

  const nonce = crypto.randomUUID().replace(/-/g, "");

  const csp = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "font-src 'self' data:",
    `connect-src ${CONNECT_SRC}`,
    "frame-src 'none'",
    `frame-ancestors ${FRAME_ANCESTORS}`,
    "base-uri 'self'",
    "form-action 'self'",
    "object-src 'none'",
  ].join("; ");

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);
  requestHeaders.set("content-security-policy", csp);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("content-security-policy", csp);
  return response;
}

export const config = {
  // Skip Next internals and the same-origin bridges (they do their own checks).
  matcher: ["/((?!_next/static|_next/image|api/|favicon.ico).*)"],
};
