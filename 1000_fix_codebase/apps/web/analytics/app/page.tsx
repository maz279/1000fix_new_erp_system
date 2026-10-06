"use client";

/* P06 dashboards — the registry with the embedded-BI seam. The portal
 * layer holds NO data: KPI numbers come from /analytics/kpis
 * (backend read_group), embeds render the deployment's configured BI
 * frames only (embed_url is null when unconfigured — the native KPI
 * view serves the area instead). No local data, no portal math. */
import { useCallback, useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Loading, LoadError, Stat } from "../lib/imports";
import { callOdoo } from "../lib/api";

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
}

const card: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 20,
};
const tabBtn = (active: boolean): React.CSSProperties => ({
  padding: "8px 16px",
  cursor: "pointer",
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
  background: active ? tokens["color.primary.base"] : tokens["color.surface.secondary"],
  color: active ? tokens["color.text.inverse"] : tokens["color.text.secondary"],
});

export default function DashboardsPage() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [active, setActive] = useState<string>("executive");
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ dashboards: Dashboard[] }>("/analytics/dashboards")
      .then((d) => { setDashboards(d.dashboards || []); setLoading(false); })
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, []);

  const loadKpis = useCallback(async (id: string) => {
    setKpis(null);
    const d = await callOdoo<{ kpis?: Kpis; error?: { message: string } }>(
      "/analytics/kpis", { dashboard: id });
    if (d.error) setError(d.error.message);
    else setKpis(d.kpis || null);
  }, []);

  useEffect(() => {
    if (dashboards.length) loadKpis(active);
  }, [active, dashboards.length, loadKpis]);

  if (loading) return <Loading />;
  if (error) return <LoadError what="dashboards" message={error} />;

  const current = dashboards.find((d) => d.id === active);

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="Dashboards"
        note="Backend-aggregated KPIs (read_group over live models) + the embedded-BI seam — the portal layer holds no data"
      />

      <div role="tablist" style={{ display: "flex", gap: 8, flexWrap: "wrap", margin: "16px 0" }}>
        {dashboards.map((d) => (
          <button key={d.id} role="tab" aria-selected={active === d.id}
            style={tabBtn(active === d.id)} onClick={() => setActive(d.id)}>
            {d.title_en}
          </button>
        ))}
      </div>

      {current?.embed_available && current.embed_url ? (
        <section style={{
          ...card,
          height: 560,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}>
          {/* The BI embed: the frame is deployment-configured (never a
              source literal); data crosses directly to the BI tool. */}
          <iframe
            src={current.embed_url}
            title={current.title_en}
            style={{ width: "100%", height: "100%", border: "none",
                     borderRadius: tokens["dimension.border.radius-sm"] }}
            sandbox="allow-scripts allow-same-origin"
          />
        </section>
      ) : (
        <section>
          <p style={{
            margin: "0 0 16px", fontSize: tokens["typography.size.200"],
            color: tokens["color.text.secondary"],
          }}>
            {current
              ? (current.embed_available
                  ? "Embedded BI frame unavailable — showing native KPIs."
                  : "No BI embed configured for this dashboard — native KPIs below (embeds arrive with the Superset/Grafana deployment config).")
              : ""}
          </p>
          {kpis ? (
            <>
              <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                <Stat label="Orders (all states)" value={kpis.orders_total} tone="primary" />
                {Object.entries(kpis.orders_by_state).slice(0, 6).map(([state, n]) => (
                  <Stat key={state} label={state} value={n} />
                ))}
              </div>
              {kpis.claims_by_state && (
                <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 12 }}>
                  {Object.entries(kpis.claims_by_state).map(([state, n]) => (
                    <Stat key={state} label={`claim: ${state}`} value={n} />
                  ))}
                </div>
              )}
              {kpis.breakdown && (
                <div style={{ marginTop: 16 }}>
                  <strong>Breakdown</strong>
                  <ul style={{ marginTop: 8, paddingLeft: 20, fontSize: tokens["typography.size.200"] }}>
                    {kpis.breakdown.map((b) => (
                      <li key={b.name}>
                        <Pill state="open" label={String(b.open)} /> {b.name}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <Loading label="Aggregating…" />
          )}
        </section>
      )}
    </main>
  );
}
