"use client";

/* P08 reconciliation — the brand's remittance view (T08): approved and
 * remitted claims with FLAGGED mismatches (never auto-adjusted), plus
 * remittance recording against a claim. Money arrives as BN-007 strings. */
import { useCallback, useEffect, useState } from "react";
import { tokens, Pill, SectionHead, DataTable, Loading, LoadError, Stat } from "../../lib/imports";
import type { Column } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface ReconRow {
  claim_no: string; state: string;
  expected_bdt: string; received_bdt: string; mismatch: boolean;
  variance_bdt?: string;
}

const inputStyle: React.CSSProperties = {
  padding: 8,
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
  width: 140,
};
const btn: React.CSSProperties = {
  padding: "8px 16px",
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
  background: tokens["color.primary.base"],
  color: tokens["color.text.inverse"],
};

export default function ReconciliationPage() {
  const [rows, setRows] = useState<ReconRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const brandId = (() => {
    if (typeof window === "undefined") return null;
    const saved = window.sessionStorage.getItem("fix_brand_id");
    return saved ? Number(saved) : null;
  })();

  const reload = useCallback(async (bid: number) => {
    const d = await callOdoo<{ reconciliation?: ReconRow[]; error?: { message: string } }>(
      "/brand/reconciliation", { brand_id: bid });
    if (d.error) setError(d.error.message);
    else setRows(d.reconciliation || []);
  }, []);

  useEffect(() => {
    if (brandId == null) { setLoading(false); setError("No brand selected — open Claims first"); return; }
    reload(brandId).then(() => setLoading(false)).catch((e: Error) => setError(e.message));
  }, [brandId, reload]);

  async function recordRemittance(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (brandId == null) return;
    const form = new FormData(e.currentTarget);
    const d = await callOdoo<{ remittance?: { claim_no: string; mismatch: boolean }; error?: { message: string } }>(
      "/brand/reconciliation", {
        brand_id: brandId,
        claim_id: Number(form.get("claim_id")),
        amount: Number(form.get("amount")),
        bank_ref: String(form.get("bank_ref")),
      });
    setNotice(d.error
      ? d.error.message
      : `${d.remittance?.claim_no} recorded${d.remittance?.mismatch ? " — MISMATCH FLAGGED (expected ≠ received)" : ""}`);
    if (!d.error) reload(brandId);
  }

  if (loading) return <Loading />;
  if (error) return <LoadError what="reconciliation" message={error} />;

  const mismatches = rows.filter((r) => r.mismatch).length;
  const columns: Column<ReconRow>[] = [
    { header: "Claim", cell: (r) => r.claim_no },
    { header: "State", cell: (r) => <Pill state={r.state} /> },
    { header: "Expected (BDT)", cell: (r) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{r.expected_bdt}</span> },
    { header: "Received (BDT)", cell: (r) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{r.received_bdt}</span> },
    {
      header: "Variance (BDT)",
      cell: (r) => <span style={{ fontVariantNumeric: "tabular-nums", color: r.mismatch ? tokens["color.chart.5"] : "inherit" }}>{r.variance_bdt || "0.00"}</span>,
    },
    {
      header: "Match",
      cell: (r) => r.mismatch
        ? <Pill state="mismatch" label="flagged" />
        : (r.state === "remitted" ? <Pill state="matched" label="ok" /> : "—"),
    },
  ];

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="Remittance Reconciliation"
        note="T08: a mismatch is FLAGGED, never auto-adjusted — the flag stands until a human clears it"
      />
      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Stat label="Approved / remitted" value={rows.length} />
        <Stat label="Flagged mismatches" value={mismatches} tone="primary" />
      </div>
      {notice && (
        <p role="status" style={{
          padding: "10px 14px", marginBottom: 16,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.status.info-bg"],
          color: tokens["color.status.info"],
          fontSize: tokens["typography.size.200"],
        }}>{notice}</p>
      )}
      <DataTable rows={rows} columns={columns} keyOf={(r) => r.claim_no} />

      <section style={{
        marginTop: 24, padding: 20, maxWidth: 560,
        border: `1px solid ${tokens["color.border.default"]}`,
        borderRadius: tokens["dimension.border.radius-md"],
        background: tokens["color.surface.primary"],
      }}>
        <strong>Record a remittance</strong>
        <form onSubmit={recordRemittance} style={{ marginTop: 12, display: "flex", gap: 8, flexWrap: "wrap" }}>
          <input name="claim_id" type="number" required placeholder="Claim ID" style={inputStyle} aria-label="Claim ID" />
          <input name="amount" type="number" step="0.01" required placeholder="Amount ৳" style={inputStyle} aria-label="Remitted amount" />
          <input name="bank_ref" required placeholder="Bank ref" style={{ ...inputStyle, width: 180 }} aria-label="Bank reference" />
          <button type="submit" style={btn}>Record</button>
        </form>
      </section>
    </main>
  );
}
