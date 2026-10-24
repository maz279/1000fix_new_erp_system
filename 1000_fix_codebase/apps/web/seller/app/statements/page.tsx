"use client";

/* P07 Statements — NBR §52 withholding view.
 * The only backend source is the commission ledger at /seller/settlements
 * (cd_settlement_ext): per-line gross / commission / TDS / net and payout
 * state, all backend-computed BN-007 strings (AS-10). Monthly certified
 * statements, VDS figures, disbursal rails and downloadable §52
 * certificates have NO backend service yet, so they are stated as
 * unavailable instead of shown. WCAG 2.2 AA compliant. */
import { useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Stat, DataTable, Loading, LoadError } from "../../lib/imports";
import type { Column } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface SettlementLine {
  ref: string;
  source_ref: string;
  gross_bdt: string;
  commission_bdt: string;
  tds_bdt: string;
  net_bdt: string;
  state: string;
}

interface SettlementsResponse {
  settlements?: { lines: SettlementLine[]; net_total_bdt: string };
  error?: { message: string };
}

export default function SellerStatementsPage() {
  const [lines, setLines] = useState<SettlementLine[]>([]);
  const [netTotal, setNetTotal] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<SettlementsResponse | undefined>("/seller/settlements")
      .then((d) => {
        if (!d) setError("The server returned an empty response.");
        else if (d.error) setError(d.error.message);
        else {
          setLines(d.settlements?.lines ?? []);
          setNetTotal(d.settlements?.net_total_bdt ?? "0.00");
        }
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;
  if (error) return <LoadError what="statement lines" message={error} />;

  const columns: Column<SettlementLine>[] = [
    { header: "Ledger Ref", cell: (r) => <strong>{r.ref}</strong> },
    { header: "Source", cell: (r) => r.source_ref || "—" },
    {
      header: "Gross (BDT)",
      cell: (r) => <span style={{ fontVariantNumeric: "tabular-nums" }}>৳ {r.gross_bdt}</span>,
    },
    {
      header: "Commission (BDT)",
      cell: (r) => <span style={{ fontVariantNumeric: "tabular-nums" }}>৳ {r.commission_bdt}</span>,
    },
    {
      header: "TDS Withheld (§52)",
      cell: (r) => <span style={{ fontVariantNumeric: "tabular-nums" }}>৳ {r.tds_bdt}</span>,
    },
    {
      header: "Net (BDT)",
      cell: (r) => (
        <strong style={{ fontVariantNumeric: "tabular-nums", color: tokens["color.primary.base"] }}>
          ৳ {r.net_bdt}
        </strong>
      ),
    },
    { header: "Payout", cell: (r) => <Pill state={r.state} /> },
  ];

  return (
    <main style={{ padding: 32, maxWidth: 1100, margin: "0 auto" }}>
      <SectionHead
        title="Settlement Statements &amp; NBR §52 Withholding (স্টেটমেন্ট ও কর প্রত্যয়ন)"
        note="Withholding (TDS) per commission-ledger line — backend-computed from the settlement ledger (M53)"
      />

      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <Stat label="Net total (BDT)" value={`৳ ${netTotal}`} tone="primary" />
        <Stat label="Ledger lines" value={lines.length} />
      </div>

      <p
        role="note"
        style={{
          padding: "10px 14px",
          marginBottom: 20,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.surface.secondary"],
          color: tokens["color.text.secondary"],
          fontSize: tokens["typography.size.200"],
          border: `1px solid ${tokens["color.border.default"]}`,
        }}
      >
        Certified monthly statements, VDS figures and downloadable NBR §52 withholding certificates are
        not yet available — there is no backend service for them. The lines below are the live
        commission-ledger entries.
      </p>

      {lines.length === 0 ? (
        <p style={{ color: tokens["color.text.secondary"] }}>No settlement lines yet.</p>
      ) : (
        <DataTable rows={lines} columns={columns} keyOf={(r) => r.ref} />
      )}
    </main>
  );
}
