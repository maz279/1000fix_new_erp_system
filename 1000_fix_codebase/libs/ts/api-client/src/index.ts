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
    // Bind at construction: a detached `fetch` reference throws
    // "Illegal invocation" in browsers (live-fired at the PP5 audit —
    // every portal's data call failed in a real browser because of it)
    this.fetchImpl = opts.fetchImpl ?? ((...args) => fetch(...args));
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

  /**
   * Odoo JSON-RPC call — wraps the standard JSON-RPC envelope so apps
   * never construct it themselves (PP3: the corporate portal's estate,
   * invoices and service-requests pages use this). Uses the client's
   * own fetchImpl (retry, auth, base URL) — the ONLY fetch path.
   */
  async callOdoo<T>(path: string, params: Record<string, unknown> = {}): Promise<T> {
    const headers = new Headers({ "Content-Type": "application/json" });
    const token = this.tokenGetter ? await this.tokenGetter() : null;
    if (token) headers.set("authorization", `Bearer ${token}`);
    headers.set("accept-language", "en");
    let res: Response;
    try {
      res = await this.fetchImpl(`${this.baseUrl}${path}`, {
        method: "POST",
        headers,
        body: JSON.stringify({ jsonrpc: "2.0", method: "call", id: Date.now(), params }),
        credentials: "include",
      });
    } catch (err) {
      throw new ApiError(0, "network", `request failed: ${(err as Error).message}`);
    }
    // A down upstream (or a plain-text proxy 500) must surface as a typed
    // ApiError, never as a JSON SyntaxError ("Unexpected token 'I'").
    let data: { error?: { code?: string; message?: string }; result?: unknown };
    try {
      data = (await res.json()) as typeof data;
    } catch {
      const text = await res.text().catch(() => "");
      throw new ApiError(
        res.status,
        res.ok ? "invalid_json" : `http_${res.status}`,
        `non-JSON response from ${path}: ${text.slice(0, 80) || res.statusText}`
      );
    }
    if (data.error) {
      throw new ApiError(res.status, data.error.code || "odoo_error",
                          data.error.message || "Odoo error");
    }
    return data.result as T;
  }
}
