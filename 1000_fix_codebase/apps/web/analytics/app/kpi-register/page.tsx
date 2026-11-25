"use client";

/**
 * The 95-KPI register — the single definitions source for every metric the
 * estate reports: family, owner, baseline, W4/W8 target, source dataset and
 * the calculation formula. Includes the BM-002 reconciliation (registered vs
 * specified vs produced) so coverage gaps are visible, not hidden.
 */
import { useEffect, useMemo, useState } from "react";
import { Loading, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { describeError, type DescribedError } from "../../lib/errors";
import {
  PageHeader,
  Panel,
  StatCard,
  downloadCsv,
  linkButtonStyle,
  pageStyle,
  selectStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface KpiDef {
  kpi: string;
  family: string;
  name: string;
  baseline: string;
  w4_target: string;
  w8_target: string;
  source: string;
  owner: string;
  formula: string;
}

interface Reconcile {
  registered_count?: number;
  distinct_in_specifications?: number;
  used_but_unregistered?: number;
  registered_but_unproduced?: number;
  both_registered_and_used?: number;
  unallocated_gap?: number;
  gap_range?: string;
  [key: string]: unknown;
}

interface RegisterResponse {
  total_registered?: number;
  returned_count?: number;
  reconciliation?: Reconcile;
  kpis?: KpiDef[];
  error?: { message?: string };
}

function pretty(v: string): string {
  return v.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function KpiRegisterPage() {
  const [rows, setRows] = useState<KpiDef[]>([]);
  const [reconciliation, setReconciliation] = useState<Reconcile>({});
  const [totalRegistered, setTotalRegistered] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<DescribedError | null>(null);
  const [query, setQuery] = useState("");
  const [family, setFamily] = useState("all");
  const [owner, setOwner] = useState("all");

  useEffect(() => {
    callOdoo<RegisterResponse>("/analytics/kpis/register")
      .then((d) => {
        if (d?.error) {
          setError({ sessionExpired: false, message: d.error.message ?? "Register unavailable" });
        } else {
          setRows(d?.kpis ?? []);
          setReconciliation(d?.reconciliation ?? {});
          setTotalRegistered(d?.total_registered ?? d?.kpis?.length ?? 0);
        }
        setLoading(false);
      })
      .catch((e: unknown) => {
        setError(describeError(e));
        setLoading(false);
      });
  }, []);

  const families = useMemo(
    () => Array.from(new Set(rows.map((r) => r.family))).sort(),
    [rows]
  );
  const owners = useMemo(
    () => Array.from(new Set(rows.map((r) => r.owner))).sort(),
    [rows]
  );

  const filtered = useMemo(
    () =>
      rows.filter((r) => {
        const q = query.trim().toLowerCase();
        const matchesQuery =
          !q ||
          r.kpi.toLowerCase().includes(q) ||
          r.name.toLowerCase().includes(q) ||
          r.formula.toLowerCase().includes(q) ||
          r.source.toLowerCase().includes(q);
        const matchesFamily = family === "all" || r.family === family;
        const matchesOwner = owner === "all" || r.owner === owner;
        return matchesQuery && matchesFamily && matchesOwner;
      }),
    [rows, query, family, owner]
  );

  const exportCsv = () =>
    downloadCsv(
      `1000fix-kpi-register-${new Date().toISOString().slice(0, 10)}.csv`,
      ["KPI", "Name", "Family", "Owner", "Baseline", "W4 target", "W8 target", "Source", "Formula"],
      rows.map((r) => [
        r.kpi,
        r.name,
        r.family,
        r.owner,
        r.baseline,
        r.w4_target,
        r.w8_target,
        r.source,
        r.formula,
      ])
    );

  if (loading) {
    return (
      <main style={pageStyle}>
        <PageHeader title="KPI register" subtitle="Loading the governed metric definitions…" />
        <Loading label="Loading the KPI register…" />
      </main>
    );
  }
  if (error) {
    return (
      <main style={pageStyle}>
        <PageHeader title="KPI register" />
        <div role="alert" style={{ color: tokens["color.status.error"], fontSize: 13 }}>
          Failed to load the KPI register: {error.message}
        </div>
      </main>
    );
  }

  return (
    <main style={pageStyle}>
      <PageHeader
        title="KPI register"
        subtitle={`${totalRegistered} governed KPIs — one definition, one owner and one formula per metric. The register is the source of truth; dashboard numbers are checked against it.`}
        actions={
          <button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>
            ⬇ Export CSV
          </button>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Registered KPIs" value={totalRegistered} tone="primary" />
        <StatCard label="Families" value={families.length} />
        <StatCard label="Owners (modules)" value={owners.length} />
        <StatCard
          label="Registered but not produced"
          value={reconciliation.registered_but_unproduced ?? "—"}
          tone={Number(reconciliation.registered_but_unproduced ?? 0) > 0 ? "warning" : "success"}
          note="BM-002 reconciliation"
        />
      </section>

      {reconciliation && Object.keys(reconciliation).length > 0 && (
        <Panel title="BM-002 reconciliation — the honest coverage picture">
          <div style={{ padding: 14, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: 10, fontSize: 12.5 }}>
            {[
              ["Registered", reconciliation.registered_count],
              ["Distinct in specifications", reconciliation.distinct_in_specifications],
              ["Used but unregistered", reconciliation.used_but_unregistered],
              ["Registered but not produced", reconciliation.registered_but_unproduced],
              ["Both registered and used", reconciliation.both_registered_and_used],
              ["Unallocated gap", reconciliation.unallocated_gap],
              ["Gap range", reconciliation.gap_range],
            ].map(([label, value]) => (
              <div key={String(label)} style={{ padding: "8px 10px", background: tokens["color.surface.secondary"], borderRadius: tokens["dimension.border.radius-sm"] }}>
                <div style={{ fontSize: 10, textTransform: "uppercase", letterSpacing: "0.04em", color: tokens["color.text.secondary"] }}>
                  {label}
                </div>
                <div style={{ fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>{value == null ? "—" : String(value)}</div>
              </div>
            ))}
          </div>
        </Panel>
      )}

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", margin: "16px 0 12px" }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search KPI id, name, source or formula…"
          aria-label="Search KPI register"
          style={{ ...selectStyle, flex: "1 1 280px", maxWidth: 420 }}
        />
        <select value={family} onChange={(e) => setFamily(e.target.value)} aria-label="Family" style={selectStyle}>
          <option value="all">All families ({families.length})</option>
          {families.map((f) => (
            <option key={f} value={f}>{pretty(f)}</option>
          ))}
        </select>
        <select value={owner} onChange={(e) => setOwner(e.target.value)} aria-label="Owner" style={selectStyle}>
          <option value="all">All owners ({owners.length})</option>
          {owners.map((o) => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
          {filtered.length} of {rows.length} shown
        </span>
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>KPI</th>
                <th style={thStyle}>Name</th>
                <th style={thStyle}>Family</th>
                <th style={thStyle}>Owner</th>
                <th style={thStyle}>Baseline</th>
                <th style={thStyle}>W4 target</th>
                <th style={thStyle}>W8 target</th>
                <th style={thStyle}>Source</th>
                <th style={thStyle}>Formula</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r) => (
                <tr key={r.kpi}>
                  <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11.5 }}>{r.kpi}</td>
                  <td style={{ ...tdStyle, fontWeight: 500 }}>{r.name}</td>
                  <td style={tdStyle}>{pretty(r.family)}</td>
                  <td style={tdStyle}>{r.owner}</td>
                  <td style={tdStyle}>{r.baseline}</td>
                  <td style={tdStyle}>{r.w4_target}</td>
                  <td style={tdStyle}>{r.w8_target}</td>
                  <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11 }}>{r.source}</td>
                  <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11, maxWidth: 340 }}>{r.formula}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={9} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 28 }}>
                    No KPIs match this filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>
    </main>
  );
}
