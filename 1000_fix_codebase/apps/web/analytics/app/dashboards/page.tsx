"use client";

/**
 * P06 dashboards — executive and operational views over backend-computed
 * KPIs (no data copy, no portal arithmetic).
 *
 * Adds the executive-dashboard essentials: period selection with a previous
 * comparison, a server generation timestamp, curated tabs, drill-down tables
 * and a governed CSV export. Superset remains an optional embed; the native
 * KPI view is always available.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Loading, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { describeError, type DescribedError } from "../../lib/errors";
import {
  Badge,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  downloadCsv,
  linkButtonStyle,
  pageStyle,
  primaryLinkStyle,
  selectStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Dashboard {
  id: string;
  area: string;
  title_en: string;
  title_bn: string;
  audience: string;
  embed_available: boolean;
  embed_url: string | null;
}

interface Kpis {
  dashboard: string;
  orders_by_state: Record<string, number>;
  orders_total: number;
  breakdown?: { name: string; open: number }[];
  claims_by_state?: Record<string, number>;
  people_metrics?: Record<string, string | number>;
  period?: { date_from: string | null; date_to: string | null; days: number | null };
  orders_previous?: number | null;
  orders_delta_pct?: number | null;
  generated_at?: string;
  source?: string;
}

type PeriodKey = "7" | "30" | "90" | "365" | "all";
const PERIODS: { key: PeriodKey; en: string; bn: string; days: number | null }[] = [
  { key: "7", en: "Last 7 days", bn: "শেষ ৭ দিন", days: 7 },
  { key: "30", en: "Last 30 days", bn: "শেষ ৩০ দিন", days: 30 },
  { key: "90", en: "Last 90 days", bn: "শেষ ৯০ দিন", days: 90 },
  { key: "365", en: "Last 12 months", bn: "শেষ ১২ মাস", days: 365 },
  { key: "all", en: "All time", bn: "সব সময়", days: null },
];

function ymd(d: Date): string {
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${m}-${day}`;
}

function periodParams(key: PeriodKey): Record<string, unknown> {
  const spec = PERIODS.find((p) => p.key === key) ?? PERIODS[1];
  if (!spec.days) return { include_meta: 1 };
  const to = new Date();
  const from = new Date();
  from.setDate(to.getDate() - (spec.days - 1));
  return { date_from: ymd(from), date_to: ymd(to), include_meta: 1 };
}

function allowedEmbedOrigin(): string | null {
  const raw = process.env.NEXT_PUBLIC_SUPERSET_URL?.trim();
  if (!raw) return null;
  try {
    return new URL(raw).origin;
  } catch {
    return null;
  }
}

function frameableEmbed(d: Dashboard): string | null {
  if (!d.embed_available || !d.embed_url) return null;
  const origin = allowedEmbedOrigin();
  if (!origin) return null;
  try {
    return new URL(d.embed_url).origin === origin ? d.embed_url : null;
  } catch {
    return null;
  }
}

const OPEN_EXCLUDED = new Set(["delivered", "closed", "cancelled"]);

function pretty(v: string): string {
  return v.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function DashboardsPage() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [registryLoading, setRegistryLoading] = useState(true);
  const [registryError, setRegistryError] = useState<DescribedError | null>(null);
  const [active, setActive] = useState<string | null>(null);
  const [period, setPeriod] = useState<PeriodKey>("30");
  const [query, setQuery] = useState("");
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<DescribedError | null>(null);

  useEffect(() => {
    callOdoo<{ dashboards?: Dashboard[] } | undefined>("/analytics/dashboards")
      .then((d) => {
        const list = d?.dashboards ?? [];
        setDashboards(list);
        setActive(list[0]?.id ?? null);
      })
      .catch((e: unknown) => setRegistryError(describeError(e)))
      .finally(() => setRegistryLoading(false));
  }, []);

  const loadKpis = useCallback(
    async (id: string, p: PeriodKey) => {
      setLoading(true);
      setError(null);
      try {
        const d = await callOdoo<{ kpis?: Kpis; error?: { message: string } } | undefined>(
          "/analytics/kpis",
          { dashboard: id, ...periodParams(p) }
        );
        if (d?.error) {
          setKpis(null);
          setError({ sessionExpired: false, message: d.error.message });
        } else {
          setKpis(d?.kpis ?? null);
        }
      } catch (e: unknown) {
        setKpis(null);
        setError(describeError(e));
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    if (active) void loadKpis(active, period);
  }, [active, period, loadKpis]);

  const filteredDashboards = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return dashboards;
    return dashboards.filter(
      (d) =>
        d.title_en.toLowerCase().includes(q) ||
        d.title_bn.includes(query.trim()) ||
        d.audience.toLowerCase().includes(q) ||
        d.id.toLowerCase().includes(q)
    );
  }, [dashboards, query]);

  const current = dashboards.find((d) => d.id === active) ?? null;
  const embedUrl = current ? frameableEmbed(current) : null;
  const embedBlocked = Boolean(current?.embed_available && current.embed_url && !embedUrl);

  const openCount = kpis
    ? Object.entries(kpis.orders_by_state)
        .filter(([state]) => !OPEN_EXCLUDED.has(state))
        .reduce((sum, [, count]) => sum + count, 0)
    : 0;
  const delta = kpis?.orders_delta_pct ?? null;
  const generated = kpis?.generated_at
    ? new Date(`${kpis.generated_at.replace(" ", "T")}Z`) // Odoo sends naive UTC
    : null;
  const fresh = generated ? Date.now() - generated.getTime() < 60 * 60 * 1000 : null;

  const exportCsv = () => {
    if (!current || !kpis) return;
    const rows: string[][] = [
      ["meta", "dashboard", current.title_en],
      ["meta", "audience", current.audience],
      ["meta", "period_from", kpis.period?.date_from ?? "all"],
      ["meta", "period_to", kpis.period?.date_to ?? "all"],
      ["meta", "orders_total", String(kpis.orders_total)],
      ["meta", "orders_previous", kpis.orders_previous == null ? "" : String(kpis.orders_previous)],
      ["meta", "orders_delta_pct", delta == null ? "" : String(delta)],
      ["meta", "generated_at", kpis.generated_at ?? ""],
      ["section", "key", "value"],
      ...Object.entries(kpis.orders_by_state).map(([s, c]) => ["orders_by_state", s, String(c)]),
      ...Object.entries(kpis.claims_by_state ?? {}).map(([s, c]) => ["claims_by_state", s, String(c)]),
      ...(kpis.breakdown ?? []).map((b) => ["breakdown", b.name, String(b.open)]),
    ];
    downloadCsv(`1000fix-${current.id}-${ymd(new Date())}.csv`, ["metric", "key", "value"], rows);
  };

  if (registryLoading) {
    return (
      <main style={pageStyle}>
        <PageHeader title="Analytics dashboards" subtitle="Loading the dashboard registry…" />
        <Loading label="Loading dashboard registry…" />
      </main>
    );
  }

  if (registryError) {
    return (
      <main style={pageStyle}>
        <PageHeader title="Analytics dashboards" />
        <div role="alert" style={{ color: tokens["color.status.error"] }}>
          Failed to load the dashboard registry: {registryError.message}
        </div>
      </main>
    );
  }

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Analytics dashboards"
        subtitle={
          current
            ? `${current.title_en} — backend read_group aggregations, scoped to the selected period. Staff-only.`
            : "Backend-computed KPIs for 1000 FiX staff."
        }
        actions={
          <>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value as PeriodKey)}
              aria-label="Reporting period"
              style={selectStyle}
            >
              {PERIODS.map((p) => (
                <option key={p.key} value={p.key}>{p.en}</option>
              ))}
            </select>
            <button type="button" onClick={() => active && void loadKpis(active, period)} style={linkButtonStyle}>
              ↻ Refresh
            </button>
            <button type="button" onClick={exportCsv} disabled={!kpis} style={{ ...linkButtonStyle, opacity: kpis ? 1 : 0.5 }}>
              ⬇ Export CSV
            </button>
            <Link href="/kpi-register" style={{ ...primaryLinkStyle, textDecoration: "none" }}>
              KPI definitions
            </Link>
          </>
        }
      />

      <section aria-label="KPI summary" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard
          label="Total service orders"
          value={kpis ? kpis.orders_total.toLocaleString() : "…"}
          note={kpis?.period?.days ? `last ${kpis.period.days} days` : "all time"}
          tone="primary"
        />
        <StatCard
          label="Previous period"
          value={kpis?.orders_previous == null ? "—" : kpis.orders_previous.toLocaleString()}
          note="same-length comparison window"
        />
        <StatCard
          label="Change vs previous"
          value={delta == null ? "—" : `${delta > 0 ? "+" : ""}${delta}%`}
          tone={delta == null ? "neutral" : delta > 0 ? "success" : delta < 0 ? "error" : "neutral"}
          note={delta == null ? "no previous data" : "period-over-period"}
        />
        <StatCard
          label="Open requests"
          value={kpis ? openCount.toLocaleString() : "…"}
          note="excludes delivered / closed / cancelled"
          tone="warning"
        />
        <StatCard
          label="Data freshness"
          value={fresh == null ? "…" : fresh ? "Fresh" : "Stale"}
          note={generated ? `generated ${generated.toLocaleString()}` : kpis?.source ?? ""}
          tone={fresh == null ? "neutral" : fresh ? "success" : "warning"}
        />
      </section>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", marginBottom: 12 }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Filter dashboards by name or audience…"
          aria-label="Filter dashboards"
          style={{ ...selectStyle, flex: "1 1 260px", maxWidth: 380 }}
        />
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
          {filteredDashboards.length} of {dashboards.length} dashboards
        </span>
      </div>

      <nav aria-label="Analytics dashboard views" style={{ marginBottom: 18 }}>
        <div role="tablist" aria-label="Dashboard categories" style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {filteredDashboards.map((d) => {
            const selected = active === d.id;
            return (
              <button
                key={d.id}
                id={`tab-${d.id}`}
                role="tab"
                aria-selected={selected}
                aria-controls={`tabpanel-${d.id}`}
                tabIndex={selected ? 0 : -1}
                onClick={() => setActive(d.id)}
                style={{
                  minHeight: 44,
                  padding: "8px 14px",
                  cursor: "pointer",
                  border: selected ? `2px solid ${tokens["color.primary.base"]}` : `1px solid ${tokens["color.border.default"]}`,
                  borderRadius: tokens["dimension.border.radius-sm"],
                  background: selected ? tokens["color.primary.base"] : tokens["color.surface.primary"],
                  color: selected ? tokens["color.text.inverse"] : tokens["color.text.primary"],
                  fontSize: tokens["typography.size.200"],
                  fontWeight: 500,
                }}
              >
                {d.title_en}
                <span style={{ fontSize: 10, opacity: 0.8, marginLeft: 6, textTransform: "uppercase" }}>
                  {d.audience}
                </span>
              </button>
            );
          })}
          {filteredDashboards.length === 0 && (
            <span style={{ fontSize: 12, color: tokens["color.text.secondary"] }}>
              No dashboards match this filter.
            </span>
          )}
        </div>
      </nav>

      {current && (
        <section id={`tabpanel-${current.id}`} role="tabpanel" aria-labelledby={`tab-${current.id}`}>
          {embedUrl ? (
            <Panel title={`${current.title_en} — Superset embed`} padding={0}>
              <iframe
                src={embedUrl}
                title={`${current.title_en} Superset Dashboard`}
                style={{ width: "100%", height: 640, border: "none", display: "block" }}
                sandbox="allow-scripts allow-same-origin allow-forms"
              />
            </Panel>
          ) : (
            <Panel
              title={`${current.title_en} — native KPIs`}
              actions={
                <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
                  {kpis?.source ?? "live ORM read_group"} ·{" "}
                  {kpis?.generated_at ? `as of ${kpis.generated_at.slice(0, 16)}` : "as of —"}
                </span>
              }
              padding={16}
            >
              {embedBlocked && (
                <p
                  role="note"
                  style={{
                    margin: "0 0 14px",
                    padding: "9px 12px",
                    borderRadius: tokens["dimension.border.radius-sm"],
                    background: tokens["color.status.warning-bg"],
                    color: tokens["color.status.warning"],
                    fontSize: 12,
                  }}
                >
                  A BI embed is configured for this dashboard, but its origin is not allowed by this
                  portal (NEXT_PUBLIC_SUPERSET_URL is unset or points elsewhere). Showing the native KPI view.
                </p>
              )}

              {loading ? (
                <Loading label="Loading KPIs…" />
              ) : error ? (
                <div role="alert" style={{ color: tokens["color.status.error"], fontSize: 12.5 }}>
                  {error.sessionExpired
                    ? "Your session has expired — sign in again to view KPIs."
                    : `Failed to load KPIs: ${error.message}`}
                </div>
              ) : kpis ? (
                <>
                  <h3 style={{ margin: "0 0 10px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"], textTransform: "uppercase", letterSpacing: "0.04em" }}>
                    Service orders by state
                  </h3>
                  {Object.keys(kpis.orders_by_state).length === 0 ? (
                    <p style={{ margin: "0 0 16px", fontSize: 12.5, color: tokens["color.text.secondary"] }}>
                      No service orders in this period.
                    </p>
                  ) : (
                    <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 18 }}>
                      {Object.entries(kpis.orders_by_state)
                        .sort((a, b) => b[1] - a[1])
                        .map(([state, count]) => (
                          <div
                            key={state}
                            style={{
                              minWidth: 130,
                              padding: "10px 12px",
                              background: tokens["color.surface.secondary"],
                              border: `1px solid ${tokens["color.border.default"]}`,
                              borderRadius: tokens["dimension.border.radius-sm"],
                            }}
                          >
                            <StateBadge state={state} />
                            <div style={{ fontSize: 20, fontWeight: 700, marginTop: 6, fontVariantNumeric: "tabular-nums" }}>
                              {count.toLocaleString()}
                            </div>
                          </div>
                        ))}
                    </div>
                  )}

                  {kpis.claims_by_state && (
                    <div style={{ marginTop: 6 }}>
                      <h3 style={{ margin: "0 0 10px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"], textTransform: "uppercase", letterSpacing: "0.04em" }}>
                        Warranty claims by state
                      </h3>
                      {Object.keys(kpis.claims_by_state).length === 0 ? (
                        <p style={{ margin: 0, fontSize: 12.5, color: tokens["color.text.secondary"] }}>
                          No warranty claims in this period.
                        </p>
                      ) : (
                        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                          {Object.entries(kpis.claims_by_state).map(([state, count]) => (
                            <div key={state} style={{ padding: "8px 12px", border: `1px solid ${tokens["color.border.default"]}`, borderRadius: tokens["dimension.border.radius-sm"] }}>
                              <StateBadge state={state} /> <b style={{ marginLeft: 6 }}>{count.toLocaleString()}</b>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {kpis.people_metrics && (
                    <div style={{ marginTop: 18 }}>
                      <h3 style={{ margin: "0 0 10px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"], textTransform: "uppercase", letterSpacing: "0.04em" }}>
                        People &amp; HR governance
                      </h3>
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 10 }}>
                        {Object.entries(kpis.people_metrics).map(([k, v]) => (
                          <StatCard
                            key={k}
                            label={pretty(k)}
                            value={String(v)}
                            tone={
                              String(v).toUpperCase() === "BREACH"
                                ? "error"
                                : String(v).toUpperCase() === "COMPLIANT"
                                  ? "success"
                                  : "neutral"
                            }
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {kpis.breakdown && (
                    <div style={{ marginTop: 18 }}>
                      <h3 style={{ margin: "0 0 10px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"], textTransform: "uppercase", letterSpacing: "0.04em" }}>
                        Service orders by {current.id === "branch" ? "branch" : "technician"}
                      </h3>
                      {kpis.breakdown.length === 0 ? (
                        <p style={{ margin: 0, fontSize: 12.5, color: tokens["color.text.secondary"] }}>
                          No service orders in this period.
                        </p>
                      ) : (
                        <div style={{ overflowX: "auto", border: `1px solid ${tokens["color.border.default"]}`, borderRadius: tokens["dimension.border.radius-sm"] }}>
                          <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                              <tr style={{ background: tokens["color.surface.secondary"] }}>
                                <th style={thStyle}>{current.id === "branch" ? "Branch" : "Technician"}</th>
                                <th style={{ ...thStyle, textAlign: "right" }}>Service orders</th>
                                <th style={thStyle}>Share</th>
                              </tr>
                            </thead>
                            <tbody>
                              {kpis.breakdown
                                .slice()
                                .sort((a, b) => b.open - a.open)
                                .map((b) => {
                                  const total = kpis.breakdown?.reduce((s, x) => s + x.open, 0) || 1;
                                  return (
                                    <tr key={b.name}>
                                      <td style={{ ...tdStyle, fontWeight: 500 }}>{b.name}</td>
                                      <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{b.open.toLocaleString()}</td>
                                      <td style={tdStyle}>
                                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                          <div style={{ flex: 1, height: 7, background: tokens["color.surface.secondary"], borderRadius: 4 }}>
                                            <div style={{ width: `${Math.max(2, Math.round((b.open / total) * 100))}%`, height: "100%", background: tokens["color.primary.base"], borderRadius: 4 }} />
                                          </div>
                                          <span style={{ fontSize: 11, color: tokens["color.text.secondary"], width: 38, textAlign: "right" }}>
                                            {Math.round((b.open / total) * 100)}%
                                          </span>
                                        </div>
                                      </td>
                                    </tr>
                                  );
                                })}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  )}

                  {current.id === "finance" && (
                    <p style={{ marginTop: 16, fontSize: 11.5, color: tokens["color.text.secondary"] }}>
                      Ledger, VAT and receivables figures ride the Superset finance embed when configured; the
                      native view serves order-linked signals only.
                    </p>
                  )}

                  <p style={{ marginTop: 16, marginBottom: 0, fontSize: 11, color: tokens["color.text.secondary"] }}>
                    Definitions and owners: <Link href="/kpi-register" style={{ color: tokens["color.primary.base"] }}>KPI register</Link>.
                    The portal renders backend aggregates; it never recomputes a metric.
                  </p>
                </>
              ) : null}
            </Panel>
          )}
        </section>
      )}

      {dashboards.length === 0 && (
        <Panel>
          <div style={{ padding: 18, fontSize: 12.5, color: tokens["color.text.secondary"] }}>
            No dashboards are registered for this deployment.
          </div>
        </Panel>
      )}

      <p style={{ marginTop: 14, fontSize: 11, color: tokens["color.text.secondary"] }}>
        <Badge tone="info">Staff only</Badge>{" "}
        KPIs are company-wide aggregates for internal decision support. Customer and partner portal
        accounts cannot read them (enforced at the bridge and the API).
      </p>
    </main>
  );
}
