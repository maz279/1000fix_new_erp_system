"use client";

/**
 * Seller scorecard — measured performance by period (M12).
 * Acceptance 30% · on-time 30% · reviews 25% · dispute rate −15%; the tier
 * bands and the composite are computed in the backend, never here.
 */
import { useEffect, useState } from "react";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  PageHeader,
  Panel,
  StatCard,
  downloadCsv,
  linkButtonStyle,
  pageStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface ScoreRow {
  period: string;
  acceptance_rate: number;
  on_time_rate: number;
  review_rating: number;
  dispute_rate: number;
  composite: number;
  orders_awarded?: number;
}

const pct = (v: number) => `${Math.round(v * 100)}%`;

export default function ScorecardPage() {
  const [rows, setRows] = useState<ScoreRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ scorecard?: ScoreRow[]; error?: { message: string } }>("/seller/scorecard")
      .then((d) => {
        if (d.error) setError(d.error.message);
        else setRows(d.scorecard ?? []);
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <Loading label="Loading your scorecard…" />;
  if (error) return <LoadError what="scorecard" message={error} />;

  const latest = rows[0] ?? null;
  const exportCsv = () =>
    downloadCsv(
      `1000fix-scorecard-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Period", "Acceptance", "On-time", "Review rating", "Dispute rate", "Composite"],
      rows.map((r) => [
        r.period,
        pct(r.acceptance_rate),
        pct(r.on_time_rate),
        r.review_rating.toFixed(1),
        pct(r.dispute_rate),
        r.composite.toFixed(2),
      ])
    );

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Scorecard"
        subtitle="Acceptance, on-time delivery, customer reviews and dispute rate by period — the measured inputs to your tier."
        actions={
          <button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>
            ⬇ Export CSV
          </button>
        }
      />

      {latest ? (
        <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 12, marginBottom: 16 }}>
          <StatCard label="Latest period" value={latest.period} tone="primary" />
          <StatCard label="Composite" value={latest.composite.toFixed(2)} note="0–1 scale" tone="success" />
          <StatCard label="Acceptance" value={pct(latest.acceptance_rate)} />
          <StatCard label="On-time" value={pct(latest.on_time_rate)} />
          <StatCard label="Review rating" value={`${latest.review_rating.toFixed(1)} / 5`} />
          <StatCard label="Dispute rate" value={pct(latest.dispute_rate)} tone={latest.dispute_rate > 0.02 ? "warning" : "success"} />
        </section>
      ) : (
        <Panel>
          <div style={{ padding: 18, fontSize: 12.5, color: tokens["color.text.secondary"] }}>
            No scorecard periods recorded yet. Scores appear after a measured period (action_measure).
          </div>
        </Panel>
      )}

      <Panel title="History">
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Period</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Acceptance</th>
                <th style={{ ...thStyle, textAlign: "right" }}>On-time</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Reviews</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Disputes</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Composite</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.period}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{r.period}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{pct(r.acceptance_rate)}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{pct(r.on_time_rate)}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{r.review_rating.toFixed(1)}/5</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{pct(r.dispute_rate)}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>{r.composite.toFixed(2)}</td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 24 }}>
                    No periods recorded.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <p style={{ marginTop: 12, fontSize: 11.5, color: tokens["color.text.secondary"] }}>
        Composite = acceptance × 0.30 + on-time × 0.30 + (review ÷ 5) × 0.25 − dispute rate × 0.15.
        Tier bands and the score are backend-computed.
      </p>
    </main>
  );
}
