/**
 * Server-only technician relay (R01 re-audit 2026-10-22; session gate added
 * in the security fix of 2026-10-23) — used ONLY by
 * app/api/technician/[...path]/route.ts.
 *
 * Odoo's /technician/* routes are auth="bearer". This module attaches the
 * technician's Odoo API key from the server-only env var
 * FIX_TECHNICIAN_API_KEY; the key never reaches browser JS (`server-only`
 * makes any client import a build error, and the variable has no
 * NEXT_PUBLIC_ prefix so Next never inlines it).
 *
 * Trust model (2026-10-23):
 * 1. `verifyOdooSession` — the caller must hold a live Odoo session of an
 *    INTERNAL user: its `session_id` cookie is sent server-side to Odoo
 *    /web/session/get_session_info and the relay refuses (401/403) unless
 *    Odoo answers with a uid and `is_internal_user: true`.
 * 2. `relayTechnicianCall` forwards that same `session_id` cookie together
 *    with the bearer key. Odoo's ir.http._auth_method_bearer then raises
 *    AccessDenied ("Session user does not match the used apikey") unless the
 *    session user IS the key's user, so only the technician who owns
 *    FIX_TECHNICIAN_API_KEY can act through this relay; any other signed-in
 *    user is refused by Odoo itself (mapped to 403 `session_user_mismatch`).
 *
 * Residual gap: the key is still ONE technician's key per deployment. Per-
 * user identity for every technician needs a backend change (per-technician
 * API keys / Keycloak OIDC tokens, PP3, or a session-authenticated variant of
 * the /technician/* routes); Odoo's bearer auth only accepts a bare session
 * for browser navigations (Sec-Fetch-* headers), which a relay must not forge.
 *
 * Transport goes through libs/ts/api-client (P-11/FF-39 — no raw fetch),
 * to the API gateway at FIX_API_BASE (the client's documented server env;
 * loopback Kong by default). Imported directly, not via lib/imports.ts: the
 * barrel re-exports client UI components a route handler must not bundle.
 */
import "server-only";

import { ApiClient, ApiError } from "../../../../libs/ts/api-client/src/index";
import type { TechnicianPath } from "./technician";

export interface RelayError {
  code: string;
  message: string;
}

export type RelayOutcome =
  | { status: number; result: unknown }
  | { status: number; error: RelayError };

/** Odoo JSON-RPC envelope (the `data` block is never passed to the browser: it carries a traceback). */
interface OdooEnvelope {
  jsonrpc?: string;
  result?: unknown;
  error?: {
    code?: number;
    message?: string;
    data?: { name?: string; message?: string };
  };
}

/** libs/ts/api-client's loopback default (Kong, local compose stack). */
const DEFAULT_GATEWAY = "http://127.0.0.1:8000";

const AUTH_REJECTED: RelayError = {
  code: "technician_auth_rejected",
  message:
    "Odoo rejected the technician credentials of this portal (FIX_TECHNICIAN_API_KEY is invalid, revoked or expired)",
};

const SESSION_MISMATCH: RelayError = {
  code: "session_user_mismatch",
  message:
    "Your Odoo account is not the technician this portal is configured for (FIX_TECHNICIAN_API_KEY belongs to another user)",
};

const UNAUTHENTICATED: RelayError = {
  code: "unauthenticated",
  message: "Sign in with your Odoo technician account first",
};

/** Odoo's session cookie: urlsafe-base64 sid (84 chars in Odoo 19). Anything else is not forwarded. */
const SESSION_ID_RE = /^[A-Za-z0-9_-]{16,256}$/;

function failure(status: number, code: string, message: string): RelayOutcome {
  return { status, error: { code, message } };
}

function gatewayBase(): string {
  // An empty FIX_API_BASE (copied .env.example) must not yield a relative URL.
  return process.env.FIX_API_BASE?.trim() || DEFAULT_GATEWAY;
}

function odooHeaders(sessionId: string): Record<string, string> {
  const database = process.env.FIX_ODOO_DB?.trim();
  return {
    // Only Odoo's own session cookie is forwarded, never the browser's whole Cookie header.
    cookie: `session_id=${sessionId}`,
    // The relay must not trigger Odoo's soft session rotation: the new sid
    // would be set on the relay's response, never on the browser.
    "x-odoo-skip-session-rotation-interval": "1",
    ...(database ? { "x-odoo-database": database } : {}),
  };
}

export function isWellFormedSessionId(value: string | undefined): value is string {
  return typeof value === "string" && SESSION_ID_RE.test(value);
}

export type SessionCheck =
  | { ok: true; uid: number; sessionId: string }
  | { ok: false; status: number; error: RelayError };

interface OdooSessionInfo {
  uid?: unknown;
  is_internal_user?: unknown;
}

function sessionRefused(status: number, error: RelayError): SessionCheck {
  return { ok: false, status, error };
}

/**
 * Ask Odoo (server-side, same gateway as the relay) who owns `sessionId`.
 * Succeeds only for a live session of an internal (employee) user.
 */
export async function verifyOdooSession(sessionId: string | undefined): Promise<SessionCheck> {
  if (!isWellFormedSessionId(sessionId)) return sessionRefused(401, UNAUTHENTICATED);

  const client = new ApiClient({ baseUrl: gatewayBase(), maxRetries: 0 });
  let envelope: OdooEnvelope;
  try {
    envelope = await client.post<OdooEnvelope>(
      "/web/session/get_session_info",
      { jsonrpc: "2.0", method: "call", id: Date.now(), params: {} },
      { cache: "no-store", redirect: "error", headers: odooHeaders(sessionId) },
    );
  } catch (err) {
    if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
      return sessionRefused(401, UNAUTHENTICATED);
    }
    return sessionRefused(502, {
      code: "session_check_failed",
      message: "Could not verify your Odoo session with the API gateway",
    });
  }
  if (typeof envelope !== "object" || envelope === null || envelope.jsonrpc !== "2.0") {
    return sessionRefused(502, {
      code: "session_check_failed",
      message: "The API gateway returned a malformed session response",
    });
  }
  // Any error (code 100 SessionExpiredException, AccessDenied, ...) means "no usable session".
  if (envelope.error) return sessionRefused(401, UNAUTHENTICATED);

  const info = (envelope.result ?? {}) as OdooSessionInfo;
  const uid = info.uid;
  if (typeof uid !== "number" || !Number.isInteger(uid) || uid <= 0) {
    return sessionRefused(401, UNAUTHENTICATED);
  }
  if (info.is_internal_user !== true) {
    return sessionRefused(403, {
      code: "not_internal_user",
      message: "Technician access requires an internal (employee) Odoo account",
    });
  }
  return { ok: true, uid, sessionId };
}

function mapOdooError(error: NonNullable<OdooEnvelope["error"]>): RelayOutcome {
  const name = error.data?.name ?? "";
  // The forwarded session belongs to another user than the key's user.
  if (name.endsWith(".AccessDenied") && /does not match/i.test(error.data?.message ?? "")) {
    return { status: 403, error: SESSION_MISMATCH };
  }
  // _auth_method_bearer raises Unauthorized (bad/missing key) or AccessDenied;
  // code 100 is SessionExpiredException (resolved to the public user).
  if (name.endsWith(".Unauthorized") || name.endsWith(".AccessDenied") || error.code === 100) {
    return { status: 502, error: AUTH_REJECTED };
  }
  if (error.code === 404) {
    return failure(502, "upstream_not_found", "The technician API is not available on the Odoo server");
  }
  // odoo.exceptions.* (UserError, ValidationError, ...) carry user-facing text;
  // anything else may leak internals, so it is reported generically.
  const message =
    name.startsWith("odoo.exceptions.") && error.data?.message
      ? error.data.message
      : "Odoo could not process the technician request";
  return failure(502, "upstream_error", message);
}

/**
 * Forward one JSON-RPC call to Odoo as the technician who owns the server key.
 * `sessionId` MUST already have passed `verifyOdooSession`; it is forwarded so
 * that Odoo refuses the call unless the session user is the key's user.
 */
export async function relayTechnicianCall(
  path: TechnicianPath,
  params: Record<string, unknown>,
  id: string | number,
  sessionId: string,
): Promise<RelayOutcome> {
  if (!isWellFormedSessionId(sessionId)) {
    return { status: 401, error: UNAUTHENTICATED };
  }
  const apiKey = process.env.FIX_TECHNICIAN_API_KEY?.trim();
  if (!apiKey) {
    return failure(
      503,
      "technician_auth_not_configured",
      "Technician access is not configured on this server (FIX_TECHNICIAN_API_KEY is not set)",
    );
  }

  const client = new ApiClient({
    baseUrl: gatewayBase(),
    tokenGetter: () => apiKey,
    // Never replay a write (clock-in, part consumption) on a transport error.
    maxRetries: 0,
  });

  let envelope: OdooEnvelope;
  try {
    envelope = await client.post<OdooEnvelope>(
      path,
      { jsonrpc: "2.0", method: "call", id, params },
      {
        // Only the verified session_id is forwarded: Odoo refuses (AccessDenied)
        // a session whose user differs from the key's user, and does not save
        // the session on bearer calls. Nothing is cached, no redirect is
        // followed with the key attached.
        cache: "no-store",
        redirect: "error",
        headers: odooHeaders(sessionId),
      },
    );
  } catch (err) {
    if (err instanceof ApiError) {
      if (err.status === 401 || err.status === 403) return { status: 502, error: AUTH_REJECTED };
      if (err.status === 0) {
        return failure(502, "upstream_unreachable", "The API gateway (FIX_API_BASE) is unreachable");
      }
      return failure(502, "upstream_error", `The API gateway answered HTTP ${err.status}`);
    }
    return failure(502, "upstream_error", "The API gateway returned an unreadable response");
  }

  if (typeof envelope !== "object" || envelope === null || envelope.jsonrpc !== "2.0") {
    return failure(502, "upstream_error", "The API gateway returned a malformed JSON-RPC response");
  }
  if (envelope.error) return mapOdooError(envelope.error);
  // Odoo omits `result` when the controller returned None.
  return { status: 200, result: envelope.result ?? null };
}
