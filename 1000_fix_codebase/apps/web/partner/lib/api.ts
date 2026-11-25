/**
 * Partner API singleton — the only HTTP surface for this app (P-11).
 * No page or component calls fetch() directly — FF-39.
 *
 * Auth (2026-10-23): no tokenGetter — the Odoo session cookie (sent by
 * callOdoo's credentials: "include") is the only credential; the former
 * sessionStorage "fix_token" bearer was never issued by anything. A call
 * that fails with Odoo SessionExpired notifies the auth gate, which returns
 * the user to the sign-in screen; every other error is rethrown unchanged.
 *
 * 2026-11-24: the client talks to the same-origin /api/odoo bridge, not Kong.
 * The bridge allow-list is the partner surface (session + partner/profile,
 * partner/referrals, partner/commissions); nothing else in Odoo is reachable.
 */
import { ApiClient } from "./imports";
import { isSessionExpiredError, notifySessionExpired } from "./auth";

let _client: ApiClient | null = null;

function getClient(): ApiClient {
  if (!_client) {
    _client = new ApiClient({ baseUrl: "/api/odoo" });
  }
  return _client;
}

export async function callOdoo<T>(path: string, params: Record<string, unknown> = {}): Promise<T> {
  try {
    return await getClient().callOdoo<T>(path, params);
  } catch (e) {
    if (isSessionExpiredError(e)) notifySessionExpired();
    throw e;
  }
}

export { getClient as getApiClient };
