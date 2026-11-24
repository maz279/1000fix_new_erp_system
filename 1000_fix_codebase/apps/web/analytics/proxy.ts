// PP7-M03 — per-request nonce CSP (D17) + the P06 analytics access boundary.
//
// Next 16 proxy (formerly middleware): a nonce per request is set on both the
// request headers (Next stamps it onto its scripts) and the response.
//
// ANALYTICS BOUNDARY:
// - Staff-only portal. Protected pages require an Odoo session cookie at this
//   first hop; Odoo remains authoritative (the bridge and the analytics API
//   both refuse non-internal users).
// - The browser talks to Odoo only through the same-origin /api/odoo bridge;
//   connect-src is 'self'. A Superset embed is allowed only when the
//   deployment sets NEXT_PUBLIC_SUPERSET_URL (same origin check as the page).
import { NextRequest, NextResponse } from "next/server";

const FRAME_ANCESTORS = process.env.FRAME_ANCESTORS?.trim() || "'self'";

function supersetOrigin(): string | null {
  const raw = process.env.NEXT_PUBLIC_SUPERSET_URL?.trim();
  if (!raw) return null;
  try {
    return new URL(raw).origin;
  } catch {
    return null;
  }
}
const SUPERSET_ORIGIN = supersetOrigin();

const ODOO_SESSION_COOKIE = "session_id";
const PROTECTED_PREFIXES = ["/dashboards", "/kpi-register", "/governance", "/models"];

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
    "connect-src 'self'",
    ...(SUPERSET_ORIGIN ? [`frame-src 'self' ${SUPERSET_ORIGIN}`] : ["frame-src 'none'"]),
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
  matcher: ["/((?!_next/static|_next/image|api/|favicon.ico).*)"],
};
