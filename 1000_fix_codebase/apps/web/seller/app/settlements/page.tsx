"use client";

/* P07 settlements — the seller's commission statement lines + net total
 * from the commission ledger (served by cd_settlement_ext — the model's
 * owning module; FL-03). Payout state ships with every line: a held
 * payout is visible with its state, never explained away. Money arrives
 * as BN-007 strings (AS-10). */
import { useEffect, useState } from "react";
import { tokens, Pill, SectionHead, DataTable, Loading, LoadError, Stat } from "../../lib/imports";
import type { Column } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface SettlementLine {
  ref: string; source_ref: string;
  gross_bdt: string; commission_bdt: string; tds_bdt: string; net_bdt: string;
  state: string;
}

export default function SettlementsPage() {
  const [lines, setLines] = useState<SettlementLine[]>([]);
  const [netTotal, setNetTotal] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ settlements?: { lines: SettlementLine[]; net_total_bdt: string }; error?: { message: string } }>(
      "/seller/settlements")
      .then((d) => {
        if (d.error) setError(d.error.message);
        else {
          setLines(d.settlements?.lines || []);
          setNetTotal(d.settlements?.net_total_bdt || "0.00");
        }
        setLoading(false);
      })
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return <Loading />;
  if (error) return <LoadError what="settlements" message={error} />;

  const columns: Column<SettlementLine>[] = [
    { header: "Ref", cell: (l) => l.ref },
    { header: "Source", cell: (l) => l.source_ref || "—" },
    { header: "Gross (BDT)", cell: (l) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{l.gross_bdt}</span> },
    { header: "Commission (BDT)", cell: (l) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{l.commission_bdt}</span> },
    { header: "TDS (BDT)", cell: (l) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{l.tds_bdt}</span> },
    { header: "Net (BDT)", cell: (l) => <strong style={{ fontVariantNumeric: "tabular-nums" }}>{l.net_bdt}</strong> },
    { header: "Payout", cell: (l) => <Pill state={l.state} /> },
  ];

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="Settlement Statements"
        note="Commission ledger lines with gross/commission/TDS/net and payout state — backend-computed (M53)"
      />
      <div style={{ marginBottom: 16 }}>
        <Stat label="Net total (BDT)" value={netTotal} tone="primary" />
      </div>
      {lines.length === 0
        ? <p style={{ color: tokens["color.text.secondary"] }}>No settlement lines yet.</p>
        : <DataTable rows={lines} columns={columns} keyOf={(l) => l.ref} />}
    </main>
  );
}
