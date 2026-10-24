/**
 * Customer API singleton — the only HTTP surface for this app (P-11).
 * Wraps the typed api-client (JSON-RPC envelope inside the lib); no page
 * or component in this app calls fetch() directly — FF-39.
 */
import { ApiClient, ApiError } from "./imports";
import type { TechnicianPath } from "./technician";

let _client: ApiClient | null = null;
let _technicianClient: ApiClient | null = null;

function getClient(): ApiClient {
  if (!_client) {
    _client = new ApiClient({
      baseUrl: typeof window !== "undefined" ? "/api/odoo" : (process.env.NEXT_PUBLIC_FIX_API_BASE || "http://127.0.0.1:8069"),
      // No tokenGetter: the Odoo session cookie (sent by callOdoo's
      // credentials: "include") is the only credential — no fake bearer.
    });
  }
  return _client;
}

export async function callOdoo<T>(path: string, params: Record<string, unknown> = {}): Promise<T> {
  return getClient().callOdoo<T>(path, params);
}

/**
 * P02 technician calls (R01 re-audit 2026-10-22). Odoo's /technician/* is
 * auth="bearer", so the browser does NOT call it directly and holds no key:
 * the call goes to the same-origin relay app/api/technician/[...path]
 * ("/api" + "/technician/..."), which attaches the server-only
 * FIX_TECHNICIAN_API_KEY. The technician is the key's user — never pass
 * employee_id / technician_id.
 *
 * Odoo reports business and identity refusals as a RESULT of the form
 * {"error": {code, message}} (forbidden, no_employee, no_open_shift, ...);
 * they are thrown here as ApiError so every caller handles them.
 */
export async function callOdooAsTechnician<T>(
  path: TechnicianPath,
  params: Record<string, unknown> = {},
): Promise<T> {
  if (!_technicianClient) {
    // No tokenGetter: the relay authenticates the caller by the Odoo session cookie.
    _technicianClient = new ApiClient({ baseUrl: "/api", maxRetries: 0 });
  }
  const result = await _technicianClient.callOdoo<unknown>(path, params);
  const refusal =
    typeof result === "object" && result !== null
      ? (result as { error?: { code?: string; message?: string } }).error
      : undefined;
  if (refusal) {
    throw new ApiError(200, refusal.code ?? "technician_error", refusal.message ?? "Technician request refused");
  }
  return result as T;
}

export { getClient as getApiClient };
