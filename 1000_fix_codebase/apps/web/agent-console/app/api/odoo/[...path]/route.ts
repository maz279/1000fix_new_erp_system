/**
 * Same-origin Odoo bridge for the agent console (replaces Kong :8000).
 *
 * - Upstream origin is SERVER-CONFIGURED (ODOO_INTERNAL_URL); the browser
 *   never supplies it. Path allow-list: session endpoints, the staff portal
 *   API (/contact/portal/*) and the two call-control reads the console uses
 *   (/contact/handoff, /contact/softphone). The rest of Odoo is not proxied.
 * - POST/JSON/bounded, no redirects, session cookie relayed both ways.
 * - Staff-only is enforced twice: the Odoo portal controller refuses
 *   non-internal users, and the console gate refuses them in the UI.
 */
import { NextResponse, type NextRequest } from "next/server";

export const dynamic = "force-dynamic";

const MAX_BODY_CHARS = 1_000_000;
const UPSTREAM_TIMEOUT_MS = 30_000;

const ALLOWED_EXACT = new Set([
  "web/session/authenticate",
  "web/session/get_session_info",
  "web/session/destroy",
  "contact/handoff",
  "contact/softphone",
]);
const ALLOWED_PREFIX = "contact/portal/";
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
    return replyError(404, "not_allowed", "This endpoint is not part of the agent console API");
  }
  const upstream = upstreamConfig();
  if (!upstream) {
    return replyError(503, "bridge_misconfigured", "The console API bridge is not configured");
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

export function GET(): NextResponse {
  return replyError(405, "method_not_allowed", "Use POST for Odoo JSON-RPC");
}
