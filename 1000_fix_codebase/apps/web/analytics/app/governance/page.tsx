"use client";

/**
 * Data governance — catalogue completeness, source-to-target lineage,
 * data-quality rules and residency compliance.
 *
 * These endpoints serve FROZEN audit artefacts verbatim (A11 E5). The page
 * labels that plainly on every panel and never implies a live measurement;
 * live governance reads are the M62 packs.
 */
import { useEffect, useState } from "react";
import { Loading, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { describeError, type DescribedError } from "../../lib/errors";
import {
  Badge,
  PageHeader,
  Panel,
  StatCard,
  linkButtonStyle,
  pageStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface FrozenBase {
  is_frozen_artifact?: boolean;
  artifact?: string;
  as_of?: string | null;
  note?: string;
  error?: { code?: string; message?: string };
}

interface Catalogue extends FrozenBase {
  total_entities_catalogued?: number;
  target_entity_count?: number;
  completeness_pct?: number;
  owner_module_coverage_pct?: number;
  named_steward_coverage_pct?: number;
  classification_coverage_pct?: number;
  retention_policy_coverage_pct?: number;
  status?: string;
  domain_breakdown?: Record<string, number>;
  classification_breakdown?: Record<string, number>;
}

interface LineageFeed {
  lineage_id?: string;
  feed_name?: string;
  source_entity?: string;
  target_entity?: string;
  transformation?: string;
  grain?: string;
}
interface Lineage extends FrozenBase {
  total_warehouse_feeds?: number;
  lineage_coverage_pct?: number;
  status?: string;
  feeds?: LineageFeed[];
}

interface DqRule {
  rule_id?: string;
  name?: string;
  entity?: string;
  rule_type?: string;
  threshold_pct?: number;
  last_result_pct?: number;
  state?: string;
  alert_dispatched?: boolean;
}
interface DqAlert {
  rule_id?: string;
  entity?: string;
  measured_result?: number;
  threshold?: number;
  severity?: string;
}
interface Dq extends FrozenBase {
  rules_evaluated?: number;
  passing_rules_count?: number;
  failing_rules_count?: number;
  seeded_failure_tested?: boolean;
  status?: string;
  rules?: DqRule[];
  alerts?: DqAlert[];
}

interface Residency extends FrozenBase {
  scanned_files_count?: number;
  forbidden_tokens_checked?: string[];
  violations_count?: number;
  status?: string;
  audit_finding?: string;
}

type Tab = "catalogue" | "lineage" | "dq" | "residency";

function FrozenNote({ data }: { data: FrozenBase | null }) {
  if (!data) return null;
  return (
    <div
      role="note"
      style={{
        marginBottom: 14,
        padding: "9px 12px",
        borderRadius: tokens["dimension.border.radius-sm"],
        background: tokens["color.status.warning-bg"],
        color: tokens["color.status.warning"],
        border: `1px solid ${tokens["color.status.warning-border"]}`,
        fontSize: 11.5,
        lineHeight: 1.55,
      }}
    >
      <b>Frozen audit artefact — not a live measurement.</b>{" "}
      {data.artifact ? `Source: ${data.artifact}. ` : ""}
      {data.as_of ? `As of ${String(data.as_of).slice(0, 19)}. ` : ""}
      {data.note ?? "Live governance reads are the M62 packs."}
    </div>
  );
}

function MetricGrid({ items }: { items: [string, string | number | undefined | null][] }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 10 }}>
      {items.map(([label, value]) => (
        <div
          key={label}
          style={{
            padding: "9px 11px",
            background: tokens["color.surface.secondary"],
            borderRadius: tokens["dimension.border.radius-sm"],
          }}
        >
          <div style={{ fontSize: 10, textTransform: "uppercase", letterSpacing: "0.04em", color: tokens["color.text.secondary"] }}>
            {label}
          </div>
          <div style={{ fontSize: 16, fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
            {value == null ? "—" : String(value)}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function GovernancePage() {
  const [tab, setTab] = useState<Tab>("catalogue");
  const [catalogue, setCatalogue] = useState<Catalogue | null>(null);
  const [lineage, setLineage] = useState<Lineage | null>(null);
  const [dq, setDq] = useState<Dq | null>(null);
  const [residency, setResidency] = useState<Residency | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<DescribedError | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([
      callOdoo<Catalogue>("/analytics/governance/catalogue"),
      callOdoo<Lineage>("/analytics/governance/lineage"),
      callOdoo<Dq>("/analytics/governance/dq"),
      callOdoo<Residency>("/analytics/governance/residency"),
    ])
      .then(([c, l, q, r]) => {
        if (!active) return;
        setCatalogue(c);
        setLineage(l);
        setDq(q);
        setResidency(r);
        setLoading(false);
      })
      .catch((e: unknown) => {
        if (!active) return;
        setError(describeError(e));
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <main style={pageStyle}>
        <PageHeader title="Data governance" subtitle="Loading the governance evidence…" />
        <Loading label="Loading governance artefacts…" />
      </main>
    );
  }
  if (error) {
    return (
      <main style={pageStyle}>
        <PageHeader title="Data governance" />
        <div role="alert" style={{ color: tokens["color.status.error"], fontSize: 13 }}>
          Failed to load governance evidence: {error.message}
        </div>
      </main>
    );
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: "catalogue", label: "Catalogue" },
    { key: "lineage", label: "Lineage" },
    { key: "dq", label: "Data quality" },
    { key: "residency", label: "Residency" },
  ];

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Data governance"
        subtitle="Catalogue completeness, source-to-target lineage, data-quality rules and residency compliance for the warehouse estate."
        actions={
          <button
            type="button"
            onClick={() => window.location.reload()}
            style={{ ...linkButtonStyle, cursor: "pointer" }}
          >
            ↻ Reload evidence
          </button>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard
          label="Catalogue completeness"
          value={`${catalogue?.completeness_pct ?? "—"}%`}
          note={`${catalogue?.total_entities_catalogued ?? "—"} of ${catalogue?.target_entity_count ?? "—"} entities`}
          tone="warning"
        />
        <StatCard
          label="Lineage coverage"
          value={`${lineage?.lineage_coverage_pct ?? "—"}%`}
          note={`${lineage?.total_warehouse_feeds ?? "—"} warehouse feeds`}
          tone="success"
        />
        <StatCard
          label="DQ rules passing"
          value={`${dq?.passing_rules_count ?? "—"} / ${dq?.rules_evaluated ?? "—"}`}
          note={`${dq?.failing_rules_count ?? "—"} failing`}
          tone={Number(dq?.failing_rules_count ?? 0) > 0 ? "warning" : "success"}
        />
        <StatCard
          label="Residency violations"
          value={residency?.violations_count ?? "—"}
          note={`${residency?.scanned_files_count ?? "—"} files scanned`}
          tone={Number(residency?.violations_count ?? 0) > 0 ? "error" : "success"}
        />
      </section>

      <div role="tablist" aria-label="Governance views" style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 14 }}>
        {tabs.map((t) => (
          <button
            key={t.key}
            role="tab"
            aria-selected={tab === t.key}
            onClick={() => setTab(t.key)}
            style={{
              minHeight: 40,
              padding: "7px 14px",
              cursor: "pointer",
              borderRadius: tokens["dimension.border.radius-sm"],
              border: tab === t.key ? `2px solid ${tokens["color.primary.base"]}` : `1px solid ${tokens["color.border.default"]}`,
              background: tab === t.key ? tokens["color.primary.base"] : tokens["color.surface.primary"],
              color: tab === t.key ? tokens["color.text.inverse"] : tokens["color.text.primary"],
              fontSize: tokens["typography.size.200"],
              fontWeight: 500,
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "catalogue" && (
        <Panel title="Data catalogue">
          <div style={{ padding: 14 }}>
            <FrozenNote data={catalogue} />
            <MetricGrid
              items={[
                ["Catalogued entities", catalogue?.total_entities_catalogued],
                ["Target entity count", catalogue?.target_entity_count],
                ["Completeness", catalogue?.completeness_pct != null ? `${catalogue.completeness_pct}%` : undefined],
                ["Owner-module coverage", catalogue?.owner_module_coverage_pct != null ? `${catalogue.owner_module_coverage_pct}%` : undefined],
                ["Named-steward coverage", catalogue?.named_steward_coverage_pct != null ? `${catalogue.named_steward_coverage_pct}%` : undefined],
                ["Classification coverage", catalogue?.classification_coverage_pct != null ? `${catalogue.classification_coverage_pct}%` : undefined],
                ["Retention policy coverage", catalogue?.retention_policy_coverage_pct != null ? `${catalogue.retention_policy_coverage_pct}%` : undefined],
                ["Status", catalogue?.status],
              ]}
            />
            {catalogue?.domain_breakdown && (
              <div style={{ marginTop: 14 }}>
                <h3 style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.04em", color: tokens["color.text.secondary"], margin: "0 0 8px" }}>
                  Catalogue by domain
                </h3>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {Object.entries(catalogue.domain_breakdown).map(([domain, count]) => (
                    <span key={domain} style={{ padding: "6px 10px", border: `1px solid ${tokens["color.border.default"]}`, borderRadius: tokens["dimension.border.radius-sm"], fontSize: 12 }}>
                      {domain} <b>{count}</b>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Panel>
      )}

      {tab === "lineage" && (
        <Panel title="Source-to-target lineage">
          <div style={{ padding: 14 }}>
            <FrozenNote data={lineage} />
            <MetricGrid
              items={[
                ["Warehouse feeds", lineage?.total_warehouse_feeds],
                ["Coverage", lineage?.lineage_coverage_pct != null ? `${lineage.lineage_coverage_pct}%` : undefined],
                ["Status", lineage?.status],
              ]}
            />
            <div style={{ overflowX: "auto", marginTop: 14, border: `1px solid ${tokens["color.border.default"]}`, borderRadius: tokens["dimension.border.radius-sm"] }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: tokens["color.surface.secondary"] }}>
                    <th style={thStyle}>Feed</th>
                    <th style={thStyle}>Source</th>
                    <th style={thStyle}>Target</th>
                    <th style={thStyle}>Grain</th>
                    <th style={thStyle}>Transformation</th>
                  </tr>
                </thead>
                <tbody>
                  {(lineage?.feeds ?? []).map((f, i) => (
                    <tr key={f.lineage_id ?? `${f.feed_name}-${i}`}>
                      <td style={{ ...tdStyle, fontWeight: 500 }}>{f.feed_name ?? "—"}</td>
                      <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11 }}>{f.source_entity ?? "—"}</td>
                      <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11 }}>{f.target_entity ?? "—"}</td>
                      <td style={tdStyle}>{f.grain ?? "—"}</td>
                      <td style={{ ...tdStyle, fontSize: 11.5 }}>{f.transformation ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Panel>
      )}

      {tab === "dq" && (
        <Panel title="Data quality monitoring">
          <div style={{ padding: 14 }}>
            <FrozenNote data={dq} />
            <MetricGrid
              items={[
                ["Rules evaluated", dq?.rules_evaluated],
                ["Passing", dq?.passing_rules_count],
                ["Failing", dq?.failing_rules_count],
                ["Seeded failure tested", dq?.seeded_failure_tested ? "Yes" : "No"],
                ["Status", dq?.status],
              ]}
            />
            <div style={{ overflowX: "auto", marginTop: 14, border: `1px solid ${tokens["color.border.default"]}`, borderRadius: tokens["dimension.border.radius-sm"] }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: tokens["color.surface.secondary"] }}>
                    <th style={thStyle}>Rule</th>
                    <th style={thStyle}>Name</th>
                    <th style={thStyle}>Entity</th>
                    <th style={thStyle}>Type</th>
                    <th style={{ ...thStyle, textAlign: "right" }}>Threshold</th>
                    <th style={{ ...thStyle, textAlign: "right" }}>Last result</th>
                    <th style={thStyle}>State</th>
                  </tr>
                </thead>
                <tbody>
                  {(dq?.rules ?? []).map((r) => (
                    <tr key={r.rule_id}>
                      <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11 }}>{r.rule_id}</td>
                      <td style={{ ...tdStyle, fontWeight: 500 }}>{r.name}</td>
                      <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11 }}>{r.entity}</td>
                      <td style={tdStyle}>{r.rule_type}</td>
                      <td style={{ ...tdStyle, textAlign: "right" }}>{r.threshold_pct ?? "—"}%</td>
                      <td style={{ ...tdStyle, textAlign: "right" }}>{r.last_result_pct ?? "—"}%</td>
                      <td style={tdStyle}>
                        <Badge tone={r.state === "passing" ? "success" : "error"}>{r.state ?? "—"}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {(dq?.alerts ?? []).length > 0 && (
              <div style={{ marginTop: 12, fontSize: 11.5, color: tokens["color.text.secondary"] }}>
                Seeded failure alert: {dq?.alerts?.[0]?.rule_id} · {dq?.alerts?.[0]?.entity} · measured{" "}
                {dq?.alerts?.[0]?.measured_result}% vs threshold {dq?.alerts?.[0]?.threshold}% ·{" "}
                <Badge tone="error">{dq?.alerts?.[0]?.severity ?? "ALERT"}</Badge>
              </div>
            )}
          </div>
        </Panel>
      )}

      {tab === "residency" && (
        <Panel title="Residency compliance scan">
          <div style={{ padding: 14 }}>
            <FrozenNote data={residency} />
            <MetricGrid
              items={[
                ["Files scanned", residency?.scanned_files_count],
                ["Forbidden tokens checked", residency?.forbidden_tokens_checked?.length],
                ["Violations", residency?.violations_count],
                ["Status", residency?.status],
                ["Finding", residency?.audit_finding],
              ]}
            />
            {residency?.forbidden_tokens_checked && (
              <div style={{ marginTop: 14 }}>
                <h3 style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.04em", color: tokens["color.text.secondary"], margin: "0 0 8px" }}>
                  Tokens checked for
                </h3>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {residency.forbidden_tokens_checked.map((token) => (
                    <span key={token} style={{ padding: "3px 8px", border: `1px solid ${tokens["color.border.default"]}`, borderRadius: tokens["dimension.border.radius-pill"], fontSize: 11, fontFamily: "monospace" }}>
                      {token}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Panel>
      )}
    </main>
  );
}
