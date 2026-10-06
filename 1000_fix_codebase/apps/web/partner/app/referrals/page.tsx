"use client";

/* P12 referrals — submission (attribution lands on the referred party)
 * and tracking (submitted → converted → commissioned). The model gates
 * duplicate/self referrals server-side (AS-09). */
import { useCallback, useEffect, useState } from "react";
import { tokens, Pill, SectionHead, DataTable, Loading, LoadError, Stat } from "../../lib/imports";
import type { Column } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface Referral {
  id: number; name: string; referred: string; state: string;
  commission_bdt: string;
}

const inputStyle: React.CSSProperties = {
  padding: 8,
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
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

export default function ReferralsPage() {
  const [rows, setRows] = useState<Referral[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const reload = useCallback(async () => {
    const d = await callOdoo<{ referrals?: Referral[]; error?: { message: string } }>("/partner/referrals");
    if (d.error) setError(d.error.message);
    else setRows(d.referrals || []);
  }, []);

  useEffect(() => {
    reload().then(() => setLoading(false)).catch((e: Error) => setError(e.message));
  }, [reload]);

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const d = await callOdoo<{ referral?: { id: number; state: string }; error?: { message: string } }>(
      "/partner/referrals", {
        referred_partner_id: Number(form.get("referred_partner_id")),
        referred_name: String(form.get("referred_name")),
      });
    setNotice(d.error ? d.error.message : `Referral submitted (${d.referral?.state})`);
    (e.target as HTMLFormElement).reset();
    if (!d.error) reload();
  }

  if (loading) return <Loading />;
  if (error) return <LoadError what="referrals" message={error} />;

  const commissioned = rows.filter((r) => r.state === "commissioned").length;
  const columns: Column<Referral>[] = [
    { header: "Referral", cell: (r) => r.name },
    { header: "Referred party", cell: (r) => r.referred },
    { header: "State", cell: (r) => <Pill state={r.state} /> },
    { header: "Commission (BDT)", cell: (r) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{r.commission_bdt}</span> },
  ];

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="Referrals"
        note="Attribution lands on the referred party — convert → commission runs its server-side course (M53)"
      />
      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Stat label="Referrals" value={rows.length} />
        <Stat label="Commissioned" value={commissioned} tone="primary" />
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

      <section style={{
        padding: 20, marginBottom: 24, maxWidth: 560,
        border: `1px solid ${tokens["color.border.default"]}`,
        borderRadius: tokens["dimension.border.radius-md"],
        background: tokens["color.surface.primary"],
      }}>
        <strong>Submit a referral</strong>
        <form onSubmit={submit} style={{ marginTop: 12, display: "flex", gap: 8, flexWrap: "wrap" }}>
          <input name="referred_partner_id" type="number" required
            placeholder="Referred party ID" style={inputStyle} aria-label="Referred party ID" />
          <input name="referred_name" required
            placeholder="Label (e.g. company / person)" style={{ ...inputStyle, width: 220 }} aria-label="Referral label" />
          <button type="submit" style={btn}>Submit</button>
        </form>
      </section>

      <DataTable rows={rows} columns={columns} />
    </main>
  );
}
