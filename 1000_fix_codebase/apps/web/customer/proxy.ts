// PP7-M03 — per-request nonce Content-Security-Policy (D17).
//
// Next 16 pattern: the proxy (formerly middleware) generates a nonce per
// request and sets BOTH (a) the CSP on the *request* headers — Next reads
// it and stamps the nonce onto its own bootstrap/inline scripts — and
// (b) the CSP on the *response*. `strict-dynamic` lets the nonce-bearing
// bootstrap load the rest of the chunk graph without listing every file.
//
// Customer-portal access boundary (2026-11-24):
// - This portal is the CUSTOMER's self-service surface. The ERP backend is
//   not embedded and not framed: frame-src is 'none' and the only call
//   surface is the same-origin /api/odoo allowlist (app/api/odoo).
// - Customer-account routes require a signed-in Odoo session. Authentication
//   is still authoritative in Odoo (every customer API route is auth="user"
//   and partner-scoped); this gate is the first hop so an unauthenticated
//   visitor lands on the public landing/sign-in page instead of a dashboard
//   shell.
//
// Policy notes:
// - style-src keeps 'unsafe-inline' (framework-injected styles; no nonce
//   plumbing exists for styles in Next 16 — documented, not silent).
// - connect-src: 'self' plus the local API gateway origins by default —
//   the PP5 apps' client components call Kong at 127.0.0.1:8000 (cross-
//   origin on dev ports; customer alone uses its same-origin /api/odoo
//   rewrite). Production sets CSP_CONNECT_SRC="" when everything flows
//   same-origin behind the gateway.
// - upgrade-insecure-requests is deliberately NOT set on these http dev
//   serves; it is enabled at the TLS-terminating edge (Kong) in deployment.
import { NextRequest, NextResponse } from "next/server";

const FRAME_ANCESTORS = process.env.FRAME_ANCESTORS?.trim() || "'self'";
const CONNECT_SRC = [
  "'self'",
  process.env.CSP_CONNECT_SRC?.trim() ?? "http://127.0.0.1:8000 http://localhost:8000",
].filter(Boolean).join(" ");

/** Odoo's session cookie (odoo/http.py). Presence is the first-hop gate;
 * Odoo still validates the session on every customer API call. */
const ODOO_SESSION_COOKIE = "session_id";

/**
 * Routes that require a signed-in customer. The public surface is the
 * landing page (/), sign-in (/login), live tracking token links (/tracking)
 * and help (/support).
 */
const PROTECTED_PREFIXES = [
  "/dashboard",
  "/booking",
  "/devices",
  "/estimates",
  "/invoices",
  "/consent",
  "/account",
  "/technician", // P02 staff surface — never customer-visible
  "/workspace", // legacy ERP pane; redirects to the dashboard
];

function isProtected(pathname: string): boolean {
  return PROTECTED_PREFIXES.some(
    (p) => pathname === p || pathname.startsWith(`${p}/`)
  );
}

export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  // Customer-account pages need a session cookie before they render. A
  // missing cookie is a signed-out visitor: send them to sign-in and bring
  // them back to the page they asked for after authentication.
  if (isProtected(pathname) && !request.cookies.get(ODOO_SESSION_COOKIE)?.value) {
    const login = new URL("/login", request.url);
    login.searchParams.set("next", `${pathname}${search}`);
    return NextResponse.redirect(login);
  }

  const nonce = crypto.randomUUID().replace(/-/g, "");

  // Dev-only: React's development bundle requires eval() for its debug
  // introspection (the production bundle never uses it — the runtime warning
  // says exactly that). `next dev` keeps the strict policy waived here;
  // `next build && next start` sets NODE_ENV=production and stays hardened.
  const devEval = process.env.NODE_ENV === "production" ? "" : " 'unsafe-eval'";

  const csp = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${devEval}`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "font-src 'self' data:",
    `connect-src ${CONNECT_SRC}`,
    // The ERP is never framed by the customer portal.
    "frame-src 'none'",
    `frame-ancestors ${FRAME_ANCESTORS}`,
    "base-uri 'self'",
    "form-action 'self'",
    "object-src 'none'",
  ].join("; ");

  const requestHeaders = new Headers(request.headers);
  // Next reads the CSP (incl. nonce) from the request headers and applies
  // it to its generated <script> tags automatically.
  requestHeaders.set("x-nonce", nonce);
  requestHeaders.set("content-security-policy", csp);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("content-security-policy", csp);
  return response;
}

export const config = {
  // Skip Next internals and the same-origin Odoo bridge (the bridge route
  // performs its own path allowlist and forwards the session cookie).
  matcher: ["/((?!_next/static|_next/image|api/|favicon.ico).*)"],
};
