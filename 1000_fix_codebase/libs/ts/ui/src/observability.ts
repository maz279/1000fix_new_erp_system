// PP7-M04 — the frontend observability seam (D18).
//
// A single, dependency-free instrumentation point every portal can adopt:
// when NEXT_PUBLIC_OTEL_ENDPOINT is set, a Web-Vitals + error beacon is
// POSTed there as OTLP-shaped JSON (the collector/Tempo path in the
// compose stack; Kong-fronted in deployment). Without the env the module
// is strictly inert — zero requests, zero bundle cost beyond this file.
//
// Deliberately NOT the full @opentelemetry/sdk-trace-web: the browser
// bundle budget (P01 < 400 KB) wins over SDK completeness; the seam's
// payload shape is OTLP-compatible so swapping in the full SDK at
// deployment is a drop-in change behind the same env flag.
export interface RumEvent {
  name: string;
  kind: "web-vital" | "error" | "navigation";
  value?: number;
  detail?: string;
  page: string;
  ts: string;
}

const ENDPOINT = (typeof process !== "undefined" &&
  process.env.NEXT_PUBLIC_OTEL_ENDPOINT) || "";

let installed = false;

function post(events: RumEvent[]): void {
  if (!ENDPOINT || typeof fetch !== "function") return;
  // OTLP/HTTP JSON resourceSpans-shaped envelope; fire-and-forget.
  const body = JSON.stringify({
    resourceSpans: [{
      resource: { attributes: [
        { key: "service.name", value: { stringValue: location.host } },
        { key: "fix.surface", value: { stringValue: "portal-rum" } },
      ] },
      scopeSpans: [{
        spans: events.map((e) => ({
          traceId: "", spanId: "",
          name: `${e.kind}:${e.name}`,
          kind: 1,
          startTimeUnixNano: String(Date.parse(e.ts) * 1e6),
          endTimeUnixNano: String((Date.parse(e.ts) + (e.value ?? 0)) * 1e6),
          attributes: [
            { key: "page", value: { stringValue: e.page } },
            ...(e.detail
              ? [{ key: "detail", value: { stringValue: e.detail.slice(0, 200) } }]
              : []),
          ],
        })),
      }],
    }],
  });
  try {
    void fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      keepalive: true,
    }).catch(() => undefined);
  } catch {
    /* beacon loss is never a user-facing error */
  }
}

/** Install the seam once per page load. Inert without the env flag. */
export function installRum(): void {
  if (installed || !ENDPOINT || typeof window === "undefined") return;
  installed = true;
  const page = location.pathname;
  const emit = (e: Omit<RumEvent, "page" | "ts">) =>
    post([{ ...e, page, ts: new Date().toISOString() }]);

  // Navigation timing (LCP proxy) + errors; Web Vitals via PerformanceObserver
  // where available — no third-party library.
  addEventListener("error", (ev) =>
    emit({ name: "js-error", kind: "error",
      detail: ev.message?.slice(0, 200) || "unknown" }));
  addEventListener("unhandledrejection", () =>
    emit({ name: "promise-rejection", kind: "error" }));
  try {
    const po = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        const vital = entry as PerformanceEntry & { renderTime?: number; loadTime?: number };
        const value = vital.renderTime ?? vital.loadTime ?? vital.startTime;
        emit({ name: vital.entryType === "largest-contentful-paint" ? "lcp" : vital.name,
          kind: "web-vital", value: Math.round(value) });
      }
    });
    po.observe({ type: "largest-contentful-paint", buffered: true } as PerformanceObserverInit);
  } catch {
    /* older engines: navigation timing still emitted below */
  }
  addEventListener("load", () => {
    const nav = performance.getEntriesByType("navigation")[0] as
      PerformanceNavigationTiming | undefined;
    if (nav) emit({ name: "tti", kind: "navigation", value: Math.round(nav.domContentLoadedEventEnd) });
  });
}
