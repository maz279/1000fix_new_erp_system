"use client";

/**
 * Model monitoring — Bengali speech-to-text productionisation evidence.
 *
 * The evidence is fixture-level: the page states the evaluation scope and the
 * fact that no backend is deployed / production WER is unmeasured, rather than
 * presenting fixture numbers as production accuracy.
 */
import { useEffect, useState, type CSSProperties } from "react";
import { Loading, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { describeError, type DescribedError } from "../../lib/errors";
import { Badge, PageHeader, Panel, StatCard, pageStyle, tdStyle, thStyle } from "../../components/ui";

interface FixtureBatch {
  batch_id?: string;
  timestamp?: string;
  samples?: number;
  average_wer?: number;
  substitutions?: number;
  insertions?: number;
  deletions?: number;
  accuracy_class?: string;
}
interface DriftRun {
  baseline_wer?: number | null;
  current_wer?: number | null;
  threshold?: number;
  drift_detected?: boolean | null;
  status?: string;
  retraining_event?: {
    from_version?: string;
    to_version?: string;
    reason?: string;
    status?: string;
    note?: string;
  } | null;
}
interface Stt {
  model_name?: string;
  active_version?: string;
  stage?: string;
  model_registry?: {
    model_name?: string;
    active_version?: string;
    stage?: string;
    architecture?: string;
    backend_configured?: boolean;
    production_wer?: number | null;
    production_wer_note?: string;
  };
  evaluation_scope?: string;
  timestamp?: string;
  evaluation_summary?: {
    fixture_batches?: FixtureBatch[];
    fixture_baseline_wer_used_for_drift?: number;
    fixture_baseline_note?: string;
  };
  drift_monitoring?: { against_fixture_baseline?: DriftRun; without_any_baseline?: DriftRun };
  pdpa_compliance?: {
    legal_basis_gate_enforced?: boolean;
    dpia_reference?: string;
    retention_policy?: string;
  };
  checks?: Record<string, boolean>;
  status?: string;
  finding?: string;
  error?: string;
}

export default function ModelsPage() {
  const [data, setData] = useState<Stt | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<DescribedError | null>(null);

  useEffect(() => {
    callOdoo<Stt>("/analytics/stt/dashboard")
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((e: unknown) => {
        setError(describeError(e));
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <main style={pageStyle}>
        <PageHeader title="Model monitoring" subtitle="Loading the model evidence…" />
        <Loading label="Loading model monitoring…" />
      </main>
    );
  }
  if (error) {
    return (
      <main style={pageStyle}>
        <PageHeader title="Model monitoring" />
        <div role="alert" style={{ color: tokens["color.status.error"], fontSize: 13 }}>
          Failed to load model monitoring: {error.message}
        </div>
      </main>
    );
  }

  const registry = data?.model_registry ?? null;
  const drift = data?.drift_monitoring?.against_fixture_baseline;
  const batches = data?.evaluation_summary?.fixture_batches ?? [];
  const checks = Object.entries(data?.checks ?? {});
  const emptyCell: CSSProperties = {
    ...tdStyle,
    textAlign: "center",
    color: tokens["color.text.secondary"],
  };

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Model monitoring"
        subtitle="Bengali speech-to-text model registry, fixture evaluation, drift/retraining bookkeeping and PDPA controls."
        actions={<Badge tone={data?.status === "PASS" ? "success" : "warning"}>{data?.status ?? "STATUS —"}</Badge>}
      />

      <div
        role="note"
        style={{
          marginBottom: 16,
          padding: "10px 13px",
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.status.warning-bg"],
          color: tokens["color.status.warning"],
          border: `1px solid ${tokens["color.status.warning-border"]}`,
          fontSize: 12,
          lineHeight: 1.55,
        }}
      >
        <b>Evaluation scope:</b> {data?.evaluation_scope ?? "fixture-level evidence"}
        {data?.evaluation_scope?.trim().endsWith(".") ? "" : "."}
        {data?.timestamp ? ` Evidence as of ${String(data.timestamp).slice(0, 19)}.` : ""}{" "}
        Fixture WER is not production accuracy.
      </div>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Model" value={registry?.model_name ?? data?.model_name ?? "—"} note={registry?.architecture ?? ""} tone="primary" />
        <StatCard label="Active version" value={registry?.active_version ?? data?.active_version ?? "—"} note={registry?.stage ?? data?.stage ?? ""} />
        <StatCard
          label="Production WER"
          value={registry?.production_wer == null ? "Unmeasured" : `${registry.production_wer}`}
          note={registry?.backend_configured ? "backend configured" : "no backend deployed"}
          tone={registry?.production_wer == null ? "warning" : "success"}
        />
        <StatCard
          label="Drift (fixture baseline)"
          value={drift?.drift_detected == null ? "—" : drift.drift_detected ? "Detected" : "None"}
          note={`threshold ${drift?.threshold ?? "—"}`}
          tone={drift?.drift_detected ? "error" : "success"}
        />
        <StatCard label="Checks" value={`${checks.filter(([, ok]) => ok).length} / ${checks.length}`} note="evidence checks passing" tone="success" />
      </section>

      {registry?.production_wer_note && (
        <p style={{ margin: "0 0 16px", fontSize: 11.5, color: tokens["color.text.secondary"] }}>
          {registry.production_wer_note}
        </p>
      )}

      <Panel title="Fixture evaluation batches">
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Batch</th>
                <th style={thStyle}>Timestamp</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Samples</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Average WER</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Sub / Ins / Del</th>
                <th style={thStyle}>Classification</th>
              </tr>
            </thead>
            <tbody>
              {batches.map((b) => (
                <tr key={b.batch_id}>
                  <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11 }}>{b.batch_id ?? "—"}</td>
                  <td style={tdStyle}>{b.timestamp ? String(b.timestamp).slice(0, 19) : "—"}</td>
                  <td style={{ ...tdStyle, textAlign: "right" }}>{b.samples ?? "—"}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{b.average_wer ?? "—"}</td>
                  <td style={{ ...tdStyle, textAlign: "right" }}>{b.substitutions ?? "—"} / {b.insertions ?? "—"} / {b.deletions ?? "—"}</td>
                  <td style={tdStyle}>
                    <Badge tone={b.accuracy_class === "production-ready" ? "success" : "error"}>
                      {b.accuracy_class ?? "—"}
                    </Badge>
                  </td>
                </tr>
              ))}
              {batches.length === 0 && (
                <tr><td colSpan={6} style={emptyCell}>No fixture batches in the evidence.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(380px, 1fr))", gap: 16, marginTop: 16 }}>
        <Panel title="Drift & retraining">
          <div style={{ padding: 14, fontSize: 12.5, lineHeight: 1.8 }}>
            <div>Baseline WER: <b>{drift?.baseline_wer ?? "—"}</b></div>
            <div>Current WER: <b>{drift?.current_wer ?? "—"}</b></div>
            <div>Threshold: <b>{drift?.threshold ?? "—"}</b></div>
            <div>Status: <Badge tone={drift?.status === "RETRAINED" ? "warning" : "neutral"}>{drift?.status ?? "—"}</Badge></div>
            {drift?.retraining_event && (
              <div style={{ marginTop: 10, paddingTop: 10, borderTop: `1px solid ${tokens["color.border.default"]}` }}>
                <div><b>Retraining event</b> ({drift.retraining_event.status ?? "—"})</div>
                <div>{drift.retraining_event.from_version ?? "—"} → {drift.retraining_event.to_version ?? "—"}</div>
                <div style={{ color: tokens["color.text.secondary"] }}>{drift.retraining_event.reason ?? ""}</div>
                {drift.retraining_event.note && (
                  <div style={{ color: tokens["color.text.secondary"], fontSize: 11.5 }}>{drift.retraining_event.note}</div>
                )}
              </div>
            )}
            <div style={{ marginTop: 10, color: tokens["color.text.secondary"], fontSize: 11.5 }}>
              {data?.evaluation_summary?.fixture_baseline_note ?? ""}
            </div>
          </div>
        </Panel>

        <Panel title="PDPA & governance controls">
          <div style={{ padding: 14, fontSize: 12.5, lineHeight: 1.8 }}>
            <div>Legal-basis gate: <Badge tone={data?.pdpa_compliance?.legal_basis_gate_enforced ? "success" : "error"}>{data?.pdpa_compliance?.legal_basis_gate_enforced ? "Enforced" : "Off"}</Badge></div>
            <div>DPIA reference: <b>{data?.pdpa_compliance?.dpia_reference ?? "—"}</b></div>
            <div>Retention: {data?.pdpa_compliance?.retention_policy ?? "—"}</div>
            <div style={{ marginTop: 10 }}>
              {checks.map(([name, ok]) => (
                <div key={name} style={{ display: "flex", justifyContent: "space-between", gap: 10, fontSize: 12 }}>
                  <span>{name.replace(/_/g, " ")}</span>
                  <Badge tone={ok ? "success" : "error"}>{ok ? "PASS" : "FAIL"}</Badge>
                </div>
              ))}
            </div>
          </div>
        </Panel>
      </div>

      {data?.finding && (
        <p style={{ marginTop: 14, fontSize: 11.5, lineHeight: 1.6, color: tokens["color.text.secondary"] }}>
          <b>Finding:</b> {data.finding}
        </p>
      )}
    </main>
  );
}
