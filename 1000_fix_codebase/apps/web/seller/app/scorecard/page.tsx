"use client";

/* P07 scorecard — the seller's performance history by period (M12).
 * Backend-computed rates (0–1 / 0–5); the portal renders only. */
import { useEffect, useState } from "react";
import { tokens, SectionHead, DataTable, Loading, LoadError } from "../../lib/imports";
import type { Column } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface ScoreRow {
  period: string;
  acceptance_rate: number;
  on_time_rate: number;
  review_rating: number;
  dispute_rate: number;
  composite: number;
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
        else setRows(d.scorecard || []);
        setLoading(false);
      })
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return <Loading />;
  if (error) return <LoadError what="scorecard" message={error} />;

  const columns: Column<ScoreRow>[] = [
    { header: "Period", cell: (r) => r.period },
    { header: "Acceptance", cell: (r) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{pct(r.acceptance_rate)}</span> },
    { header: "On-time", cell: (r) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{pct(r.on_time_rate)}</span> },
    { header: "Reviews", cell: (r) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{r.review_rating.toFixed(1)}/5</span> },
    { header: "Disputes", cell: (r) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{pct(r.dispute_rate)}</span> },
    {
      header: "Composite",
      cell: (r) => <strong style={{ color: tokens["color.primary.base"], fontVariantNumeric: "tabular-nums" }}>{r.composite.toFixed(2)}</strong>,
    },
  ];

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="Scorecard"
        note="Acceptance, on-time delivery, reviews and disputes by period — backend-computed (M12)"
      />
      {rows.length === 0
        ? <p style={{ color: tokens["color.text.secondary"] }}>No scorecard periods recorded yet.</p>
        : <DataTable rows={rows} columns={columns} keyOf={(r) => r.period} />}
    </main>
  );
}
