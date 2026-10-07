/**
 * Corporate API singleton — the only HTTP surface for this app (P-11).
 *
 * Wraps the typed api-client (libs/ts/api-client) which handles:
 * - Base URL from env only (never user-provided; loopback default is for
 *   the local compose stack — production MUST set FIX_API_BASE)
 * - Bearer token injection (the Keycloak OIDC flow sets the getter)
 * - callOdoo: JSON-RPC envelope construction — apps never build it
 *
 * No page or component in this app calls fetch() directly — FF-39.
 */
import { ApiClient } from "./imports";

let _client: ApiClient | null = null;

function getClient(): ApiClient {
  if (!_client) {
    _client = new ApiClient({
      baseUrl: process.env.NEXT_PUBLIC_FIX_API_BASE || "http://127.0.0.1:8000",
      tokenGetter: () => {
        if (typeof window !== "undefined") {
          return window.sessionStorage.getItem("fix_token");
        }
        return null;
      },
    });
  }
  return _client;
}

/**
 * Calls an Odoo JSON-RPC endpoint. Delegates to the ApiClient's
 * callOdoo method — no raw fetch anywhere in this file.
 */
export async function callOdoo<T>(path: string, params: Record<string, unknown> = {}): Promise<T> {
  return getClient().callOdoo<T>(path, params);
}

/** Export the client for auth flows that need a custom endpoint. */
export { getClient as getApiClient };
