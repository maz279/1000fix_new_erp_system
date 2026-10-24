/**
 * Same-origin technician relay: POST /api/technician/<path> -> Odoo
 * /technician/<path> with the server-only bearer key (lib/technician-relay.ts),
 * ONLY for a caller holding a live Odoo session of an internal user whose
 * account is the key's own user (security fix 2026-10-23).
 *
 * The browser's ApiClient (lib/api.ts callOdooAsTechnician) posts a JSON-RPC
 * envelope here and receives one back, so the page keeps the single
 * api-client surface (P-11). Guards:
 * - exact path allow-list (lib/technician.ts) — the relay is not an open proxy;
 * - same-origin only: Sec-Fetch-Site (when sent) must be same-origin and the
 *   Origin header is REQUIRED (every route here is state-changing POST;
 *   browsers always send Origin on POST) and must match this host; the body
 *   must be application/json (a cross-site form post cannot send it without a
 *   CORS preflight, which this route never answers);
 * - authenticated: the caller's Odoo `session_id` cookie is verified
 *   server-side against Odoo /web/session/get_session_info (401 unless it
 *   resolves to a uid, 403 unless that user is internal) BEFORE the shared key
 *   is attached; the cookie is then forwarded with the key so Odoo itself
 *   refuses a session user other than the key's user (403);
 * - bounded body; caller-supplied employee_id/technician_id are forwarded as
 *   sent and refused by Odoo (`forbidden`) unless they name the key's own
 *   technician — Odoo stays the authority on identity.
 */
import { NextResponse, type NextRequest } from "next/server";
import { isTechnicianPath } from "../../../../lib/technician";
import {
  relayTechnicianCall,
  verifyOdooSession,
  type RelayError,
} from "../../../../lib/technician-relay";

export const dynamic = "force-dynamic";

/** Offline journals are batched; anything larger than this is not a legitimate sync. */
const MAX_BODY_CHARS = 1_000_000;

type JsonRpcId = string | number | null;

function reply(
  status: number,
  id: JsonRpcId,
  payload: { result: unknown } | { error: RelayError },
): NextResponse {
  return NextResponse.json(
    { jsonrpc: "2.0", id, ...payload },
    { status, headers: { "cache-control": "no-store" } },
  );
}

function refuse(status: number, code: string, message: string, id: JsonRpcId = null): NextResponse {
  return reply(status, id, { error: { code, message } });
}

/** Odoo's session cookie name (odoo/http.py). */
const ODOO_SESSION_COOKIE = "session_id";

/**
 * Same-origin check for a state-changing request. A missing Origin is refused:
 * browsers send it on every POST, so only a non-browser client omits it, and
 * that client must not be able to drive the relay.
 */
function isSameOrigin(request: NextRequest): boolean {
  const fetchSite = request.headers.get("sec-fetch-site");
  if (fetchSite && fetchSite !== "same-origin") return false;
  const origin = request.headers.get("origin");
  if (!origin) return false;
  const forwardedHost = request.headers.get("x-forwarded-host")?.split(",")[0]?.trim();
  const host = forwardedHost || request.headers.get("host");
  if (!host) return false;
  try {
    return new URL(origin).host === host;
  } catch {
    return false;
  }
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
): Promise<NextResponse> {
  if (!isSameOrigin(request)) {
    return refuse(403, "cross_origin", "The technician relay only accepts same-origin requests");
  }
  const contentType = request.headers.get("content-type") ?? "";
  if (!contentType.toLowerCase().startsWith("application/json")) {
    return refuse(415, "unsupported_media_type", "Content-Type must be application/json");
  }

  const { path } = await context.params;
  const odooPath = `/technician/${path.join("/")}`;
  if (!isTechnicianPath(odooPath)) {
    return refuse(404, "unknown_route", "Unknown technician route");
  }

  // Authenticate the caller BEFORE the shared key is ever attached.
  const sessionId = request.cookies.get(ODOO_SESSION_COOKIE)?.value;
  const session = await verifyOdooSession(sessionId);
  if (!session.ok) {
    return refuse(session.status, session.error.code, session.error.message);
  }

  const raw = await request.text();
  if (raw.length > MAX_BODY_CHARS) {
    return refuse(413, "payload_too_large", "Request body is too large");
  }
  let envelope: unknown;
  try {
    envelope = JSON.parse(raw);
  } catch {
    return refuse(400, "invalid_json", "Request body is not valid JSON");
  }
  if (!isPlainObject(envelope)) {
    return refuse(400, "invalid_request", "Expected a JSON-RPC request object");
  }
  const id: JsonRpcId =
    typeof envelope.id === "number" || typeof envelope.id === "string" ? envelope.id : null;
  const params = envelope.params ?? {};
  if (!isPlainObject(params)) {
    return refuse(400, "invalid_params", "params must be an object", id);
  }

  const outcome = await relayTechnicianCall(odooPath, params, id ?? Date.now(), session.sessionId);
  return "error" in outcome
    ? reply(outcome.status, id, { error: outcome.error })
    : reply(outcome.status, id, { result: outcome.result });
}
