"use client";

/* P06 dashboards — the registry with the embedded-BI seam (R05-M04-T01).
 * The portal layer holds NO data: the dashboard registry comes from
 * /analytics/dashboards and every number comes from /analytics/kpis
 * (backend read_group over service orders / warranty claims / HR).
 * Nothing is substituted when a call fails — the error is shown.
 * A Superset embed renders only when the backend returns an embed URL AND
 * the deployment allows that origin via NEXT_PUBLIC_SUPERSET_URL (which
 * proxy.ts also adds to the CSP frame-src).
 */
import { useCallback, useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Loading, Stat } from "../lib/imports";
import { callOdoo } from "../lib/api";
import { describeError, type DescribedError } from "../lib/errors";

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
}

/** The Superset origin this deployment allows in frame-src, or null. */
function allowedEmbedOrigin(): string | null {
  const raw = process.env.NEXT_PUBLIC_SUPERSET_URL?.trim();
  if (!raw) return null;
  try {
    return new URL(raw).origin;
  } catch {
    return null;
  }
}

/** The embed URL when it may be framed under the CSP, else null. */
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

const card: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 24,
  boxShadow: "0 1px 3px rgba(0, 0, 0, 0.05)",
};

const tabBtn = (active: boolean): React.CSSProperties => ({
  minHeight: 48,
  padding: "10px 20px",
  cursor: "pointer",
  border: active ? `2px solid ${tokens["color.primary.base"]}` : `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
  background: active ? tokens["color.primary.base"] : tokens["color.surface.primary"],
  color: active ? tokens["color.text.inverse"] : tokens["color.text.primary"],
  transition: "all 0.15s ease-in-out",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
});

const subHead: React.CSSProperties = {
  fontSize: tokens["typography.size.200"],
  color: tokens["color.text.secondary"],
  marginBottom: 12,
  textTransform: "uppercase",
  letterSpacing: "0.5px",
};

const countTile: React.CSSProperties = {
  padding: "12px 18px",
  borderRadius: tokens["dimension.border.radius-sm"],
  background: tokens["color.surface.secondary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  minWidth: 140,
};

function ErrorPanel({ err, what }: { err: DescribedError; what: string }) {
  if (err.sessionExpired) {
    return (
      <div role="alert" style={{ ...card, color: tokens["color.status.warning"] }}>
        <strong>Your session has expired or you are not signed in.</strong>{" "}
        Returning you to the sign-in screen — sign in again to view {what}.
      </div>
    );
  }
  return (
    <div role="alert" style={{ ...card, color: tokens["color.status.error"] }}>
      Failed to load {what}: {err.message}
    </div>
  );
}

function CountTiles({ counts, prefix }: { counts: Record<string, number>; prefix?: string }) {
  return (
    <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
      {Object.entries(counts).map(([state, count]) => (
        <div key={state} style={countTile}>
          <div
            style={{
              fontSize: tokens["typography.size.100"],
              color: tokens["color.text.secondary"],
              textTransform: "capitalize",
            }}
          >
            {prefix}
            {state.replace(/_/g, " ")}
          </div>
          <div
            style={{
              fontSize: tokens["typography.size.400"],
              fontWeight: Number(tokens["typography.weight.bold"]),
              color: tokens["color.text.primary"],
              marginTop: 4,
            }}
          >
            {count.toLocaleString()}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function DashboardsPage() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [registryLoading, setRegistryLoading] = useState(true);
  const [registryError, setRegistryError] = useState<DescribedError | null>(null);
  const [active, setActive] = useState<string | null>(null);
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

  const loadKpis = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    setKpis(null);
    try {
      const d = await callOdoo<{ kpis?: Kpis; error?: { message: string } } | undefined>(
        "/analytics/kpis",
        { dashboard: id }
      );
      if (d?.error) {
        setError({ sessionExpired: false, message: d.error.message });
      } else if (d?.kpis) {
        setKpis(d.kpis);
      } else {
        setError({ sessionExpired: false, message: "The server returned no KPI data." });
      }
    } catch (e: unknown) {
      setError(describeError(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (active) loadKpis(active);
  }, [active, loadKpis]);

  const header = (
    <header style={{ marginBottom: 24 }}>
      <SectionHead
        title="Executive BI & Analytics Portal (P06 / M25)"
        note="Backend-computed KPIs from the analytics API; embedded Superset dashboards where the deployment configures them"
      />
    </header>
  );

  if (registryLoading) {
    return (
      <main style={{ padding: "32px 40px", maxWidth: 1400, margin: "0 auto" }}>
        {header}
        <Loading label="Loading dashboard registry…" />
      </main>
    );
  }

  if (registryError) {
    return (
      <main style={{ padding: "32px 40px", maxWidth: 1400, margin: "0 auto" }}>
        {header}
        <ErrorPanel err={registryError} what="the dashboard registry" />
      </main>
    );
  }

  const current = dashboards.find((d) => d.id === active) ?? null;
  const embedUrl = current ? frameableEmbed(current) : null;
  const embedBlocked = Boolean(current?.embed_available && current.embed_url && !embedUrl);

  return (
    <main style={{ padding: "32px 40px", maxWidth: 1400, margin: "0 auto" }}>
      {header}

      {dashboards.length === 0 && (
        <div style={{ ...card, color: tokens["color.text.secondary"] }}>
          No dashboards are registered for this deployment.
        </div>
      )}

      {/* Tab Navigation conforming to WCAG 2.2 AA */}
      {dashboards.length > 0 && (
        <nav aria-label="Analytics Dashboard Views" style={{ marginBottom: 24 }}>
          <div
            role="tablist"
            aria-label="Dashboard Categories"
            style={{
              display: "flex",
              gap: 12,
              flexWrap: "wrap",
              padding: 4,
              background: tokens["color.surface.secondary"],
              borderRadius: tokens["dimension.border.radius-md"],
            }}
          >
            {dashboards.map((d) => {
              const isSelected = active === d.id;
              return (
                <button
                  key={d.id}
                  id={`tab-${d.id}`}
                  role="tab"
                  aria-selected={isSelected}
                  aria-controls={`tabpanel-${d.id}`}
                  tabIndex={isSelected ? 0 : -1}
                  style={tabBtn(isSelected)}
                  onClick={() => setActive(d.id)}
                >
                  <span>{d.title_en}</span>
                  <span
                    style={{
                      fontSize: tokens["typography.size.100"],
                      opacity: 0.85,
                      marginLeft: 6,
                    }}
                  >
                    ({d.title_bn})
                  </span>
                </button>
              );
            })}
          </div>
        </nav>
      )}

      {/* Dashboard Viewport */}
      {current && (
        <section
          id={`tabpanel-${current.id}`}
          role="tabpanel"
          aria-labelledby={`tab-${current.id}`}
        >
          {embedUrl ? (
            <div
              style={{
                ...card,
                height: 640,
                display: "flex",
                flexDirection: "column",
              }}
            >
              <h2 style={{ fontSize: tokens["typography.size.400"], margin: "0 0 12px" }}>
                {current.title_en} — Apache Superset Embed
              </h2>
              <iframe
                src={embedUrl}
                title={`${current.title_en} Superset Dashboard`}
                style={{
                  width: "100%",
                  height: "100%",
                  border: "none",
                  borderRadius: tokens["dimension.border.radius-sm"],
                }}
                sandbox="allow-scripts allow-same-origin allow-forms"
              />
            </div>
          ) : (
            <div style={card}>
              {embedBlocked && (
                <p
                  role="note"
                  style={{
                    margin: "0 0 16px",
                    padding: "10px 14px",
                    borderRadius: tokens["dimension.border.radius-sm"],
                    background: tokens["color.status.warning-bg"],
                    color: tokens["color.status.warning"],
                    fontSize: tokens["typography.size.200"],
                  }}
                >
                  A BI embed is configured for this dashboard, but its origin is not allowed by this
                  portal (NEXT_PUBLIC_SUPERSET_URL is unset or points elsewhere). Showing the native
                  KPI view instead.
                </p>
              )}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 16,
                  borderBottom: `1px solid ${tokens["color.border.default"]}`,
                  paddingBottom: 12,
                  gap: 16,
                  flexWrap: "wrap",
                }}
              >
                <div>
                  <h2 style={{ fontSize: tokens["typography.size.300"], margin: 0 }}>
                    {current.title_en} — Backend Aggregations
                  </h2>
                  <p
                    style={{
                      fontSize: tokens["typography.size.200"],
                      color: tokens["color.text.secondary"],
                      margin: "4px 0 0",
                    }}
                  >
                    Source: /analytics/kpis (server-side read_group; nothing is computed in the portal)
                  </p>
                </div>
                {kpis && <Stat label="Total Service Orders" value={kpis.orders_total.toLocaleString()} tone="primary" />}
              </div>

              {loading ? (
                <Loading label="Loading KPIs…" />
              ) : error ? (
                <ErrorPanel err={error} what="KPIs" />
              ) : kpis ? (
                <>
                  <h3 style={subHead}>Service Orders by State</h3>
                  {Object.keys(kpis.orders_by_state).length === 0 ? (
                    <p style={{ color: tokens["color.text.secondary"], marginBottom: 20 }}>
                      No service orders recorded yet.
                    </p>
                  ) : (
                    <CountTiles counts={kpis.orders_by_state} />
                  )}

                  {kpis.claims_by_state && (
                    <div style={{ marginTop: 20 }}>
                      <h3 style={subHead}>Warranty Claims by State</h3>
                      {Object.keys(kpis.claims_by_state).length === 0 ? (
                        <p style={{ color: tokens["color.text.secondary"] }}>No warranty claims recorded yet.</p>
                      ) : (
                        <CountTiles counts={kpis.claims_by_state} prefix="Claim: " />
                      )}
                    </div>
                  )}

                  {kpis.people_metrics && (
                    <div style={{ marginTop: 20 }}>
                      <h3 style={subHead}>People &amp; HR Governance</h3>
                      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                        {Object.entries(kpis.people_metrics).map(([k, v]) => (
                          <Stat key={k} label={k.replace(/_/g, " ")} value={String(v)} />
                        ))}
                      </div>
                    </div>
                  )}

                  {kpis.breakdown && (
                    <div style={{ marginTop: 24 }}>
                      <h3
                        style={{
                          fontSize: tokens["typography.size.300"],
                          marginBottom: 12,
                          color: tokens["color.text.primary"],
                        }}
                      >
                        Service Orders by {current.id === "branch" ? "Branch" : "Technician"}
                      </h3>
                      {kpis.breakdown.length === 0 ? (
                        <p style={{ color: tokens["color.text.secondary"] }}>No service orders recorded yet.</p>
                      ) : (
                        <div
                          style={{
                            overflowX: "auto",
                            borderRadius: tokens["dimension.border.radius-sm"],
                            border: `1px solid ${tokens["color.border.default"]}`,
                          }}
                        >
                          <table
                            style={{
                              width: "100%",
                              borderCollapse: "collapse",
                              fontSize: tokens["typography.size.200"],
                              textAlign: "left",
                            }}
                          >
                            <thead>
                              <tr
                                style={{
                                  background: tokens["color.surface.secondary"],
                                  borderBottom: `1px solid ${tokens["color.border.default"]}`,
                                }}
                              >
                                <th scope="col" style={{ padding: "12px 16px" }}>
                                  {current.id === "branch" ? "Branch" : "Technician"}
                                </th>
                                <th scope="col" style={{ padding: "12px 16px" }}>Service Orders</th>
                              </tr>
                            </thead>
                            <tbody>
                              {kpis.breakdown.map((b, i) => (
                                <tr
                                  key={`${b.name}-${i}`}
                                  style={{
                                    borderBottom: `1px solid ${tokens["color.border.default"]}`,
                                    background:
                                      i % 2 === 0
                                        ? tokens["color.surface.primary"]
                                        : tokens["color.surface.secondary"],
                                  }}
                                >
                                  <td style={{ padding: "12px 16px", fontWeight: 500 }}>{b.name}</td>
                                  <td style={{ padding: "12px 16px" }}>
                                    <Pill state="open" label={`${b.open.toLocaleString()} orders`} />
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  )}

                  {current.id === "finance" && (
                    <p style={{ marginTop: 20, color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
                      Ledger, VAT and receivables figures are not served by the native KPI API; they are
                      available only through the Superset finance embed when one is configured.
                    </p>
                  )}
                </>
              ) : null}
            </div>
          )}
        </section>
      )}
    </main>
  );
}
