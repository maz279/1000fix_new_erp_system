// PP7-M03 — per-request nonce CSP (D17) + the P10 staff-console boundary.
//
// Staff sign in with an Odoo session; every /contact/portal/* call refuses
// non-internal users at the Odoo controller (the UI check is not the only
// gate). The browser talks to Odoo only through the same-origin /api/odoo
// bridge, so connect-src is 'self'. Pages that need a session redirect to
// /login before React mounts; the client gate still verifies the staff flag.
import { NextRequest, NextResponse } from "next/server";

const FRAME_ANCESTORS = process.env.FRAME_ANCESTORS?.trim() || "'self'";
const ODOO_SESSION_COOKIE = "session_id";
const PROTECTED_PREFIXES = ["/queue", "/conversation"];

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
  // Skip Next internals and the API bridge (proxied responses pass through).
  matcher: ["/((?!_next/static|_next/image|api/|favicon.ico).*)"],
};
