/**
 * Same-origin Odoo bridge for the corporate portal.
 *
 * Replaces the Kong (:8000) dependency: the browser posts JSON-RPC to
 * /api/odoo/<path>, this route forwards it to the server-configured Odoo
 * origin and relays the session cookie back. The origin is never taken from
 * the request (no SSRF), the path is allow-listed (session endpoints +
 * /corporate/* only), the method is POST, the body is JSON and bounded, and
 * redirects are not followed.
 *
 * CORPORATE CLIENTS ONLY: a successful internal (staff/admin) Odoo login is
 * refused here and the upstream session destroyed — the corporate portal is
 * not a back-office entry point. Internal sessions are also refused on every
 * /corporate/* call (defence in depth for a staff cookie created elsewhere on
 * this hostname).
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
const ALLOWED_PREFIX = "corporate/";
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
    return replyError(404, "not_allowed", "This endpoint is not part of the corporate portal API");
  }
  const upstream = upstreamConfig();
  if (!upstream) {
    return replyError(503, "bridge_misconfigured", "The corporate API bridge is not configured");
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
    if (auth?.internal) {
      await destroyUpstreamSession(
        upstream.base,
        cookieFromSetCookies(upstreamRes.headers.getSetCookie()),
        request
      );
      return replyError(
        403,
        "corporate_clients_only",
        "This portal is for corporate clients. Staff and administrator accounts use the operations portal."
      );
    }
  }

  if (odooPath.startsWith(ALLOWED_PREFIX) && cookie) {
    const internal = await sessionIsInternal(upstream.base, cookie);
    if (internal) {
      return replyError(
        403,
        "corporate_clients_only",
        "This portal is for corporate clients. Staff sessions have no access here."
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
      result?: { uid?: number; is_internal_user?: boolean; is_portal?: boolean };
    };
    const result = data.result;
    if (!result?.uid) return null;
    return { internal: result.is_internal_user === true || result.is_portal === false };
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

export function GET(): NextResponse {
  return replyError(405, "method_not_allowed", "Use POST for Odoo JSON-RPC");
}
