/**
 * Same-origin Odoo bridge for the customer portal (replaces the former
 * next.config rewrite to :8069, which forwarded ANY path and therefore
 * exposed the whole ERP JSON surface to the browser).
 *
 * Security boundary:
 * - The upstream origin is SERVER-CONFIGURED (ODOO_INTERNAL_URL) and never
 *   taken from the request, so this route cannot be used as an SSRF proxy.
 *   The URL is validated on every request (http/https, no credentials,
 *   query or fragment, host on the explicit allow-list).
 * - The path is allow-listed: the Odoo session endpoints and the
 *   /customer/* self-service API ONLY. Staff/back-office endpoints
 *   (/web/dataset/call_kw, /web/action, /technician, ...) are refused here,
 *   so this bridge is not an open ERP proxy.
 * - The caller's httpOnly Odoo session cookie is forwarded to Odoo and the
 *   resulting Set-Cookie is relayed back. The cookie remains the only
 *   credential; the browser never holds a bearer token.
 * - POST only, JSON only, bounded body, no redirect following.
 */
import { NextResponse, type NextRequest } from "next/server";

export const dynamic = "force-dynamic";

const MAX_BODY_CHARS = 1_000_000;
const UPSTREAM_TIMEOUT_MS = 30_000;

/** Endpoints the customer portal itself needs. Everything else is refused. */
const ALLOWED_EXACT = new Set([
  "web/session/authenticate",
  "web/session/get_session_info",
  "web/session/destroy",
]);

/** The customer self-service API namespace (see cd_customer_portal). */
const ALLOWED_PREFIX = "customer/";

/** Hosts an upstream Odoo may resolve to. Deployment overrides via env. */
const DEFAULT_ALLOWED_HOSTS = ["127.0.0.1", "localhost", "::1", "odoo", "web"];

function upstreamConfig(): { base: URL; allowedHosts: string[] } | null {
  const raw = (process.env.ODOO_INTERNAL_URL || "http://127.0.0.1:8069").trim();
  let base: URL;
  try {
    base = new URL(raw);
  } catch {
    return null;
  }
  if (base.protocol !== "http:" && base.protocol !== "https:") return null;
  if (base.username || base.password || base.search || base.hash) return null;
  // The bridge appends allow-listed paths directly to the origin.
  if (base.pathname !== "/" && base.pathname !== "") return null;
  const configured = (process.env.ODOO_ALLOWED_HOSTS || "")
    .split(",")
    .map((h) => h.trim().toLowerCase())
    .filter(Boolean);
  const allowedHosts = configured.length > 0 ? configured : DEFAULT_ALLOWED_HOSTS;
  if (!allowedHosts.includes(base.hostname.toLowerCase())) return null;
  return { base, allowedHosts };
}

/** The requested Odoo path, or null when it is not on the customer allow-list. */
function allowedPath(segments: string[]): string | null {
  if (segments.length === 0) return null;
  const joined = segments.join("/");
  // No traversal, no backslashes, no empty segments, no query smuggling.
  if (
    joined.startsWith("/") ||
    joined.includes("..") ||
    joined.includes("\\") ||
    joined.includes("?") ||
    joined.includes("#") ||
    segments.some((s) => !s)
  ) {
    return null;
  }
  if (ALLOWED_EXACT.has(joined)) return joined;
  if (joined.startsWith(ALLOWED_PREFIX)) return joined;
  return null;
}

function replyError(status: number, code: string, message: string): NextResponse {
  return NextResponse.json(
    { jsonrpc: "2.0", id: null, error: { code, message } },
    { status, headers: { "cache-control": "no-store" } }
  );
}

export async function POST(
  request: NextRequest,
  ctx: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  const { path } = await ctx.params;
  const odooPath = allowedPath(path ?? []);
  if (!odooPath) {
    return replyError(404, "not_allowed", "This endpoint is not part of the customer portal API");
  }

  const upstream = upstreamConfig();
  if (!upstream) {
    return replyError(
      503,
      "bridge_misconfigured",
      "The customer API bridge is not configured on this server"
    );
  }

  const contentType = request.headers.get("content-type") || "";
  if (!contentType.toLowerCase().startsWith("application/json")) {
    return replyError(415, "unsupported_media_type", "JSON requests only");
  }

  const body = await request.text();
  if (body.length > MAX_BODY_CHARS) {
    return replyError(413, "payload_too_large", "Request body is too large");
  }

  const url = new URL(odooPath, upstream.base);
  const headers: Record<string, string> = {
    "content-type": "application/json",
    accept: "application/json",
  };
  const cookie = request.headers.get("cookie");
  if (cookie) headers.cookie = cookie;
  const language = request.headers.get("accept-language");
  if (language) headers["accept-language"] = language;

  let upstreamRes: Response;
  try {
    upstreamRes = await fetch(url, {
      method: "POST",
      headers,
      body,
      redirect: "manual",
      cache: "no-store",
      signal: AbortSignal.timeout(UPSTREAM_TIMEOUT_MS),
    });
  } catch {
    return replyError(502, "upstream_unreachable", "The service backend is unreachable");
  }

  const payload = await upstreamRes.arrayBuffer();
  const payloadText =
    (upstreamRes.headers.get("content-type") || "").includes("application/json")
      ? Buffer.from(payload).toString("utf8")
      : null;

  // CUSTOMERS ONLY, enforced server-side. A successful staff/admin login is
  // refused here (the browser-side guard alone would still let a scripted
  // client mint an internal session through this bridge). The upstream session
  // is destroyed best-effort and no cookie is relayed.
  if (odooPath === "web/session/authenticate" && payloadText) {
    const authResult = parseAuthResult(payloadText);
    if (authResult?.internal) {
      const setCookies = upstreamRes.headers.getSetCookie();
      await destroyUpstreamSession(upstream.base, cookieFromSetCookies(setCookies), request);
      return replyError(
        403,
        "customers_only",
        "This is the customer portal. Staff and administrator accounts must sign in through the operations portal."
      );
    }
  }

  // Defence in depth: an internal Odoo session (for example a staff cookie
  // created directly on :8069, which shares this hostname's cookie jar) is
  // never allowed to drive the customer API.
  if (odooPath.startsWith(ALLOWED_PREFIX) && cookie) {
    const internal = await sessionIsInternal(upstream.base, cookie);
    if (internal) {
      return replyError(
        403,
        "customers_only",
        "This is the customer portal. Staff and administrator sessions have no access here."
      );
    }
  }

  const response = new NextResponse(payload, { status: upstreamRes.status });
  response.headers.set(
    "content-type",
    upstreamRes.headers.get("content-type") || "application/json"
  );
  response.headers.set("cache-control", "no-store");
  // Relay Odoo's cookies to the browser (session, cids, tz). The upstream is
  // the trusted backend, and the browser keeps them first-party on the portal
  // origin — no cross-origin cookie loss.
  for (const cookieValue of upstreamRes.headers.getSetCookie()) {
    response.headers.append("set-cookie", cookieValue);
  }
  return response;
}

/** `{ internal: boolean }` from an authenticate/get_session_info result. */
function parseAuthResult(text: string): { internal: boolean } | null {
  try {
    const data = JSON.parse(text) as {
      result?: { uid?: number; is_internal_user?: boolean; is_portal?: boolean };
    };
    const result = data.result;
    if (!result?.uid) return null;
    return {
      internal: result.is_internal_user === true || result.is_portal === false,
    };
  } catch {
    return null;
  }
}

function cookieFromSetCookies(setCookies: string[]): string | null {
  for (const raw of setCookies) {
    const [pair] = raw.split(";");
    if (pair?.trim().toLowerCase().startsWith("session_id=")) return pair.trim();
  }
  return null;
}

/** Best-effort cleanup of the just-created upstream session. */
async function destroyUpstreamSession(
  base: URL,
  sessionCookie: string | null,
  request: NextRequest
): Promise<void> {
  const cookie = sessionCookie || request.headers.get("cookie");
  if (!cookie) return;
  try {
    await fetch(new URL("web/session/destroy", base), {
      method: "POST",
      headers: { "content-type": "application/json", cookie },
      body: JSON.stringify({ jsonrpc: "2.0", method: "call", id: 1, params: {} }),
      cache: "no-store",
      redirect: "manual",
      signal: AbortSignal.timeout(5_000),
    });
  } catch {
    /* cleanup is best-effort; no cookie was relayed */
  }
}

/**
 * Whether the presented Odoo session belongs to an internal (staff) user.
 * Returns false on any error so an unreachable/failed probe never silently
 * grants access — the customer route still authenticates the session itself.
 */
async function sessionIsInternal(base: URL, cookie: string): Promise<boolean> {
  try {
    const res = await fetch(new URL("web/session/get_session_info", base), {
      method: "POST",
      headers: { "content-type": "application/json", cookie },
      body: JSON.stringify({ jsonrpc: "2.0", method: "call", id: 1, params: {} }),
      cache: "no-store",
      redirect: "manual",
      signal: AbortSignal.timeout(5_000),
    });
    if (!res.ok) return false;
    const parsed = parseAuthResult(await res.text());
    return parsed?.internal === true;
  } catch {
    return false;
  }
}

/** The bridge is POST-only; answer other verbs explicitly (no catch-all proxy). */
export function GET(): NextResponse {
  return replyError(405, "method_not_allowed", "Use POST for Odoo JSON-RPC");
}
