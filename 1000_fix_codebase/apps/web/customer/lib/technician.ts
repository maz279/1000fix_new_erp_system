/**
 * P02 technician API — shared, secret-free definitions (browser AND server).
 *
 * R01 re-audit 2026-10-22: Odoo's /technician/* routes are auth="bearer"
 * (an Odoo API key in `Authorization: Bearer`). The browser never calls
 * them directly and never holds that key: lib/api.ts `callOdooAsTechnician`
 * posts to the same-origin relay app/api/technician/[...path]/route.ts,
 * which verifies the caller's Odoo session and only then attaches the
 * server-only FIX_TECHNICIAN_API_KEY (lib/technician-relay.ts). The acting
 * technician is ALWAYS the employee linked to that key's user, and Odoo
 * refuses a session user other than that user — the page sends no
 * employee_id/technician_id.
 *
 * This module must stay free of secrets and of browser-only APIs at import
 * time: the relay imports it for the path allow-list.
 */

/** The only Odoo paths the relay forwards (exact match — no prefixes). */
export const TECHNICIAN_PATHS = [
  "/technician/auth/me",
  "/technician/queue",
  "/technician/attendance/clock_in",
  "/technician/attendance/clock_out",
  "/technician/job/status",
  "/technician/diagnostics/tree",
  "/technician/diagnostics/submit",
  "/technician/van-stock",
  "/technician/van-stock/consume",
  "/technician/sync",
] as const;

export type TechnicianPath = (typeof TECHNICIAN_PATHS)[number];

export function isTechnicianPath(path: string): path is TechnicianPath {
  return (TECHNICIAN_PATHS as readonly string[]).includes(path);
}

/**
 * Error codes meaning "this page cannot act as a technician" (as opposed to
 * a business error such as no_open_shift):
 * - unauthenticated / no_employee / forbidden — returned by Odoo's
 *   resolve_technician (technician_api.py);
 * - technician_auth_not_configured / technician_auth_rejected — returned by
 *   the relay when the server key is missing or refused by Odoo;
 * - unauthenticated / not_internal_user / session_user_mismatch — returned by
 *   the relay's Odoo session gate (no live session, a portal/public user, or
 *   a signed-in user who is not the key's technician).
 */
export const TECHNICIAN_AUTH_ERROR_CODES = [
  "unauthenticated",
  "no_employee",
  "forbidden",
  "technician_auth_not_configured",
  "technician_auth_rejected",
  "not_internal_user",
  "session_user_mismatch",
] as const;

export type TechnicianAuthErrorCode = (typeof TECHNICIAN_AUTH_ERROR_CODES)[number];

export function isTechnicianAuthError(code: string): code is TechnicianAuthErrorCode {
  return (TECHNICIAN_AUTH_ERROR_CODES as readonly string[]).includes(code);
}

/** Parameters that used to let the caller pick the technician (now refused by Odoo). */
const IMPERSONATION_PARAMS: readonly string[] = ["employee_id", "technician_id"];

/**
 * Drop employee_id / technician_id from a command payload. Offline journals
 * persisted before the R01 fix carry `employee_id: 6` (the removed demo
 * fallback), which Odoo now refuses with `forbidden`.
 */
export function withoutImpersonationParams(payload: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(payload).filter(([key]) => !IMPERSONATION_PARAMS.includes(key)),
  );
}

function canonicalize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    const sorted: Record<string, unknown> = {};
    for (const key of Object.keys(record).sort()) sorted[key] = canonicalize(record[key]);
    return sorted;
  }
  return value;
}

/**
 * SP-03 canonical JSON (docs/guides/offline-sync-protocol.md §6.2): compact,
 * object keys sorted at every level, non-ASCII emitted as-is — the same text
 * as Python's json.dumps(sort_keys=True, separators=(",", ":"),
 * ensure_ascii=False) for the ASCII keys and plain values the journal holds.
 */
export function canonicalJson(value: unknown): string {
  return JSON.stringify(canonicalize(value));
}

/**
 * SP-03 `batch_checksum`: lowercase hex SHA-256 of the UTF-8 canonical JSON
 * of `commands`. Must be computed over exactly the array that is sent.
 * Web Crypto is only exposed in secure contexts (HTTPS or localhost) — the
 * same requirement the PWA already has for service workers and GPS.
 */
export async function batchChecksum(commands: readonly unknown[]): Promise<string> {
  const subtle = globalThis.crypto?.subtle;
  if (!subtle) {
    throw new Error(
      "Offline sync needs a secure context (HTTPS or localhost) to compute the SP-03 batch checksum",
    );
  }
  const digest = await subtle.digest("SHA-256", new TextEncoder().encode(canonicalJson(commands)));
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}
