/**
 * Same-origin Odoo bridge for the analytics portal (replaces the Kong :8000
 * dependency that made sign-in fail locally).
 *
 * - Upstream origin is SERVER-CONFIGURED (ODOO_INTERNAL_URL), never taken
 *   from the request; the path is allow-listed to the session endpoints and
 *   /analytics/* only.
 * - STAFF ONLY: this is the P06/P10 internal analytics estate. A successful
 *   non-internal (portal customer) sign-in is refused and destroyed, and a
 *   non-internal session is refused on every /analytics/* call — fail closed.
 * - POST only, JSON only, bounded body, no redirects, no open proxy.
 */
import { NextResponse, type NextRequest } from "next/server";

export const dynamic = "force-dynamic";

const MAX_BODY_CHARS = 1_000_000;
const UPSTREAM_TIMEOUT_MS = 30_000;

const ALLOWED_EXACT = new Set([
  "web/session/authenticate",
  "web/session/get_session_info",
  "web/session/destroy",
]);
const ALLOWED_PREFIX = "analytics/";
const DEFAULT_ALLOWED_HOSTS = ["127.0.0.1", "localhost", "::1", "odoo", "web"];

function upstreamConfig(): { base: URL } | null {
  const raw = (process.env.ODOO_INTERNAL_URL || "http://127.0.0.1:8069").trim();
  let base: URL;
  try {
    base = new URL(raw);
  } catch {
    return null;
  }
  if (base.protocol !== "http:" && base.protocol !== "https:") return null;
  if (base.username || base.password || base.search || base.hash) return null;
  if (base.pathname !== "/" && base.pathname !== "") return null;
  const configured = (process.env.ODOO_ALLOWED_HOSTS || "")
    .split(",")
    .map((h) => h.trim().toLowerCase())
    .filter(Boolean);
  const allowedHosts = configured.length > 0 ? configured : DEFAULT_ALLOWED_HOSTS;
  if (!allowedHosts.includes(base.hostname.toLowerCase())) return null;
  return { base };
}

function allowedPath(segments: string[]): string | null {
  if (segments.length === 0) return null;
  const joined = segments.join("/");
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
    return replyError(404, "not_allowed", "This endpoint is not part of the analytics portal API");
  }
  const upstream = upstreamConfig();
  if (!upstream) {
    return replyError(503, "bridge_misconfigured", "The analytics API bridge is not configured");
  }

  const contentType = request.headers.get("content-type") || "";
  if (!contentType.toLowerCase().startsWith("application/json")) {
    return replyError(415, "unsupported_media_type", "JSON requests only");
  }
  const body = await request.text();
  if (body.length > MAX_BODY_CHARS) {
    return replyError(413, "payload_too_large", "Request body is too large");
  }

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
    upstreamRes = await fetch(new URL(odooPath, upstream.base), {
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

  if (odooPath === "web/session/authenticate" && payloadText) {
    const auth = parseAuthResult(payloadText);
    if (auth && !auth.internal) {
      await destroyUpstreamSession(
        upstream.base,
        cookieFromSetCookies(upstreamRes.headers.getSetCookie()),
        request
      );
      return replyError(
        403,
        "staff_only",
        "The analytics portal is for 1000FiX staff accounts. Sign in with an internal staff account."
      );
    }
  }

  if (odooPath.startsWith(ALLOWED_PREFIX) && cookie) {
    const kind = await sessionKind(upstream.base, cookie);
    if (kind !== "internal") {
      return replyError(
        403,
        "staff_only",
        "The analytics portal is for 1000FiX staff accounts."
      );
    }
  }

  const response = new NextResponse(payload, { status: upstreamRes.status });
  response.headers.set(
    "content-type",
    upstreamRes.headers.get("content-type") || "application/json"
  );
  response.headers.set("cache-control", "no-store");
  for (const cookieValue of upstreamRes.headers.getSetCookie()) {
    response.headers.append("set-cookie", cookieValue);
  }
  return response;
}

function parseAuthResult(text: string): { internal: boolean } | null {
  try {
    const data = JSON.parse(text) as {
      result?: { uid?: number; is_internal_user?: boolean };
    };
    const result = data.result;
    if (!result?.uid) return null;
    return { internal: result.is_internal_user === true };
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

/** "internal" | "external" | "unknown" — fail closed in the caller. */
async function sessionKind(base: URL, cookie: string): Promise<string> {
  try {
    const res = await fetch(new URL("web/session/get_session_info", base), {
      method: "POST",
      headers: { "content-type": "application/json", cookie },
      body: JSON.stringify({ jsonrpc: "2.0", method: "call", id: 1, params: {} }),
      cache: "no-store",
      redirect: "manual",
      signal: AbortSignal.timeout(5_000),
    });
    if (!res.ok) return "unknown";
    const parsed = parseAuthResult(await res.text());
    if (!parsed) return "external";
    return parsed.internal ? "internal" : "external";
  } catch {
    return "unknown";
  }
}

export function GET(): NextResponse {
  return replyError(405, "method_not_allowed", "Use POST for Odoo JSON-RPC");
}
