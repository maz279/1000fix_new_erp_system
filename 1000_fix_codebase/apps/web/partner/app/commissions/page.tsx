"use client";

/**
 * Commission statement — the referral ledger as a partner-readable
 * statement: customer, service, referred date, approved revenue, the rate
 * frozen at earning, the earned commission and the referral state.
 * Money arrives as backend BN-007 strings and is never recomputed here.
 */
import { useEffect, useState } from "react";
import { tokens, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  downloadCsv,
  fmtDate,
  linkButtonStyle,
  pageStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface CommissionLine {
  referral: string;
  referred: string;
  service_interest: string;
  state: string;
  referred_on: string;
  base_amount_bdt: string;
  commission_rate: number;
  commission_bdt: string;
}

export default function CommissionsPage() {
  const [lines, setLines] = useState<CommissionLine[]>([]);
  const [total, setTotal] = useState("0.00");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noProfile, setNoProfile] = useState(false);

  useEffect(() => {
    callOdoo<{ commissions?: { lines: CommissionLine[]; earned_total_bdt: string }; error?: { code: string; message: string } }>(
      "/partner/commissions"
    )
      .then((d) => {
        if (d.error) {
          if (d.error.code === "no_partner_profile") setNoProfile(true);
          else setError(d.error.message);
        } else {
          setLines(d.commissions?.lines ?? []);
          setTotal(d.commissions?.earned_total_bdt ?? "0.00");
        }
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const exportCsv = () =>
    downloadCsv(
      `1000fix-partner-commissions-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Referral", "Customer", "Service interest", "Referred on", "Base revenue (BDT)", "Rate", "Commission (BDT)", "State"],
      lines.map((l) => [
        l.referral,
        l.referred,
        l.service_interest,
        l.referred_on,
        l.base_amount_bdt,
        `${(l.commission_rate * 100).toFixed(1)}%`,
        l.commission_bdt,
        l.state,
      ])
    );

  if (loading) return <Loading label="Loading your commission statement…" />;
  if (noProfile) {
    return (
      <main style={pageStyle}>
        <PageHeader title="No partner profile is linked" subtitle="The statement is built from your own referral ledger." />
        <Panel><div style={{ padding: 16, fontSize: 13, color: tokens["color.text.secondary"] }}>
          Contact the partner desk on <strong>16743</strong> to complete onboarding/KYC.
        </div></Panel>
      </main>
    );
  }
  if (error) return <LoadError what="commissions" message={error} />;

  const commissioned = lines.filter((l) => l.state === "commissioned").length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Commission statement"
        subtitle="Commission earned on referred revenue. The rate is the one frozen when the referral was earned; the amount is computed by the backend."
        actions={<button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>⬇ Export CSV</button>}
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Earned commission" value={`৳ ${total}`} tone="success" note="sum of commissioned referrals" />
        <StatCard label="Statement lines" value={lines.length} tone="primary" note={`${commissioned} commissioned`} />
      </section>

      <Panel title="Lines">
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Referral</th>
                <th style={thStyle}>Customer</th>
                <th style={thStyle}>Service interest</th>
                <th style={thStyle}>Referred on</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Base revenue</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Rate</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Commission</th>
                <th style={thStyle}>State</th>
              </tr>
            </thead>
            <tbody>
              {lines.map((l) => (
                <tr key={l.referral}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{l.referral}</td>
                  <td style={tdStyle}>{l.referred || "—"}</td>
                  <td style={tdStyle}>{l.service_interest || "—"}</td>
                  <td style={tdStyle}>{fmtDate(l.referred_on)}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {l.base_amount_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{(l.commission_rate * 100).toFixed(1)}%</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums", fontWeight: 700 }}>৳ {l.commission_bdt}</td>
                  <td style={tdStyle}><StateBadge state={l.state} /></td>
                </tr>
              ))}
              {lines.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 26 }}>
                    No earned commissions yet. Commission appears here when a referral is commissioned.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <p style={{ marginTop: 12, fontSize: 11, color: tokens["color.text.secondary"] }}>
        How it is calculated: commission = approved referred revenue × the rate frozen at earning. The referral
        row is the commission record; the customer name is the one you submitted on the lead. Payout timing
        and references are handled by the partner desk (16743).
      </p>
    </main>
  );
}
