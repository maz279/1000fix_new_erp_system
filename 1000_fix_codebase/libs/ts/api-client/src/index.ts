/**
 * fix_api_client — the single HTTP surface for every R2 portal (PP1-M02).
 *
 * Rules (P-11 / AS-09 / DE-11):
 * - Portals talk to the API gateway (Kong), never directly to Odoo.
 * - The base URL comes from the environment. The loopback fallback exists for
 *   the local compose stack only; production MUST set FIX_API_BASE.
 * - No credentials live in code: the bearer token is supplied by the host app
 *   via a token getter (Keycloak OIDC in PP3).
 * - Money and business rules never pass through here — endpoints return
 *   backend-computed values (03-DATA-STRATEGY §8).
 */

export interface ApiClientOptions {
  baseUrl?: string;
  tokenGetter?: () => string | null | Promise<string | null>;
  fetchImpl?: typeof fetch;
  maxRetries?: number;
  retryDelayMs?: number;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const DEFAULT_MAX_RETRIES = 2;
const DEFAULT_RETRY_DELAY_MS = 250;

export class ApiClient {
  private readonly baseUrl: string;
  private readonly tokenGetter: ApiClientOptions["tokenGetter"];
  private readonly fetchImpl: typeof fetch;
  private readonly maxRetries: number;
  private readonly retryDelayMs: number;

  constructor(opts: ApiClientOptions = {}) {
    this.baseUrl = (opts.baseUrl ?? process.env.FIX_API_BASE ?? "http://127.0.0.1:8000").replace(/\/+$/, "");
    this.tokenGetter = opts.tokenGetter;
    this.fetchImpl = opts.fetchImpl ?? fetch;
    this.maxRetries = opts.maxRetries ?? DEFAULT_MAX_RETRIES;
    this.retryDelayMs = opts.retryDelayMs ?? DEFAULT_RETRY_DELAY_MS;
  }

  /** Typed GET. Retries transient failures (network + 502/503/504). */
  async get<T>(path: string, init?: RequestInit): Promise<T> {
    return this.request<T>("GET", path, init);
  }

  async post<T>(path: string, body: unknown, init?: RequestInit): Promise<T> {
    return this.request<T>("POST", path, {
      ...init,
      body: JSON.stringify(body),
      headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
    });
  }

  private async request<T>(method: string, path: string, init?: RequestInit): Promise<T> {
    let attempt = 0;
    // Bounded retry loop — no unbounded loops, no infinite backoff.
    for (;;) {
      const headers = new Headers(init?.headers);
      const token = this.tokenGetter ? await this.tokenGetter() : null;
      if (token) headers.set("authorization", `Bearer ${token}`);
      headers.set("accept-language", "en");
      let res: Response;
      try {
        res = await this.fetchImpl(`${this.baseUrl}${path}`, { ...init, method, headers });
      } catch (err) {
        if (attempt < this.maxRetries) {
          await this.delay(attempt);
          attempt += 1;
          continue;
        }
        throw new ApiError(0, "network", `request failed: ${(err as Error).message}`);
      }
      if (res.status >= 500 && res.status <= 504 && attempt < this.maxRetries) {
        await this.delay(attempt);
        attempt += 1;
        continue;
      }
      if (!res.ok) {
        let code = `http_${res.status}`;
        let message = res.statusText;
        try {
          const body = (await res.json()) as { error?: { code?: string; message?: string } };
          code = body.error?.code ?? code;
          message = body.error?.message ?? message;
        } catch {
          /* non-JSON error body — keep statusText */
        }
        throw new ApiError(res.status, code, message);
      }
      return (await res.json()) as T;
    }
  }

  private delay(attempt: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, this.retryDelayMs * 2 ** attempt));
  }
}
