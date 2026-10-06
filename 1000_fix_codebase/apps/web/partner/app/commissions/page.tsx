"use client";

/* P12 commissions — the statement built from the referral ledger with
 * the earned total. Backend-computed BN-007 strings (AS-10). */
import { useEffect, useState } from "react";
import { tokens, Pill, SectionHead, DataTable, Loading, LoadError, Stat } from "../../lib/imports";
import type { Column } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface CommissionLine {
  referral: string; referred: string; state: string; commission_bdt: string;
}

export default function CommissionsPage() {
  const [lines, setLines] = useState<CommissionLine[]>([]);
  const [total, setTotal] = useState("0.00");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ commissions?: { lines: CommissionLine[]; earned_total_bdt: string }; error?: { message: string } }>(
      "/partner/commissions")
      .then((d) => {
        if (d.error) setError(d.error.message);
        else {
          setLines(d.commissions?.lines || []);
          setTotal(d.commissions?.earned_total_bdt || "0.00");
        }
        setLoading(false);
      })
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return <Loading />;
  if (error) return <LoadError what="commissions" message={error} />;

  const columns: Column<CommissionLine>[] = [
    { header: "Referral", cell: (l) => l.referral },
    { header: "Referred party", cell: (l) => l.referred },
    { header: "State", cell: (l) => <Pill state={l.state} /> },
    { header: "Commission (BDT)", cell: (l) => <strong style={{ fontVariantNumeric: "tabular-nums" }}>{l.commission_bdt}</strong> },
  ];

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="Commission Statement"
        note="Earned commissions from the referral ledger — backend-computed (M53)"
      />
      <div style={{ marginBottom: 16 }}>
        <Stat label="Earned total (BDT)" value={total} tone="primary" />
      </div>
      {lines.length === 0
        ? <p style={{ color: tokens["color.text.secondary"] }}>No earned commissions yet — submit and convert referrals first.</p>
        : <DataTable rows={lines} columns={columns} keyOf={(l) => l.referral} />}
    </main>
  );
}
