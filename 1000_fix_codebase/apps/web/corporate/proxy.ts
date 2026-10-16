// PP7-M03 — per-request nonce Content-Security-Policy (D17).
//
// Next 16 pattern: the proxy (formerly middleware) generates a nonce per
// request and sets BOTH (a) the CSP on the *request* headers — Next reads
// it and stamps the nonce onto its own bootstrap/inline scripts — and
// (b) the CSP on the *response*. `strict-dynamic` lets the nonce-bearing
// bootstrap load the rest of the chunk graph without listing every file.
//
// Policy notes:
// - style-src keeps 'unsafe-inline' (framework-injected styles; no nonce
//   plumbing exists for styles in Next 16 — documented, not silent).
// - connect-src: 'self' plus the local API gateway origins by default —
//   the PP5 apps' client components call Kong at 127.0.0.1:8000 (cross-
//   origin on dev ports; customer alone uses its same-origin /api/odoo
//   rewrite). Production sets CSP_CONNECT_SRC="" when everything flows
//   same-origin behind the gateway.
// - frame-ancestors: overridable per portal via FRAME_ANCESTORS env —
//   P06 (analytics) sets its Superset/Grafana embed origins there.
// - upgrade-insecure-requests is deliberately NOT set on these http dev
//   serves; it is enabled at the TLS-terminating edge (Kong) in deployment.
import { NextRequest, NextResponse } from "next/server";

const FRAME_ANCESTORS = process.env.FRAME_ANCESTORS?.trim() || "'self'";
const CONNECT_SRC = [
  "'self'",
  process.env.CSP_CONNECT_SRC?.trim() ?? "http://127.0.0.1:8000 http://localhost:8000",
].filter(Boolean).join(" ");

export function proxy(request: NextRequest) {
  const nonce = crypto.randomUUID().replace(/-/g, "");

  const csp = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "font-src 'self' data:",
    `connect-src ${CONNECT_SRC}`,
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
  // Skip Next internals and the API rewrite (proxied responses pass through).
  matcher: ["/((?!_next/static|_next/image|api/odoo|favicon.ico).*)"],
};
