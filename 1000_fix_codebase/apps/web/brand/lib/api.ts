/**
 * Brand API singleton — the only HTTP surface for this app (P-11).
 * No page or component calls fetch() directly — FF-39.
 */
import { ApiClient } from "./imports";

let _client: ApiClient | null = null;

function getClient(): ApiClient {
  if (!_client) {
    _client = new ApiClient({
      baseUrl: process.env.NEXT_PUBLIC_FIX_API_BASE || "http://127.0.0.1:8069",
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

export async function callOdoo<T>(path: string, params: Record<string, unknown> = {}): Promise<T> {
  return getClient().callOdoo<T>(path, params);
}

export { getClient as getApiClient };
