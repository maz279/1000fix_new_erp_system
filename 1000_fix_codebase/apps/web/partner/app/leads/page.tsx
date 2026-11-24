"use client";

/**
 * Leads — the partner's actual lead pipeline from /partner/referrals.
 *
 * The backend DOES accept partner leads (customer name/phone + recorded
 * consent) and returns them with their state, loss reason and attribution
 * expiry. This page surfaces that pipeline; submission happens on
 * /referrals, where the consent is captured.
 */
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { tokens, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  Badge,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  downloadCsv,
  fmtDate,
  linkButtonStyle,
  pageStyle,
  primaryLinkStyle,
  selectStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Lead {
  lead: string;
  referred: string;
  state: string;
  loss_reason: string;
  service_interest: string;
  attributed_at: string;
  attribution_expires_on: string;
  converted_at: string;
  referral: string;
  commission_bdt: string;
}

function protection(lead: Lead): { text: string; tone: "success" | "warning" | "error" | "neutral" } {
  if (["converted", "lost"].includes(lead.state)) return { text: "closed", tone: "neutral" };
  if (!lead.attribution_expires_on) return { text: "no window", tone: "neutral" };
  const expires = Date.parse(`${lead.attribution_expires_on}T23:59:59Z`);
  if (Number.isNaN(expires)) return { text: lead.attribution_expires_on, tone: "neutral" };
  const days = Math.ceil((expires - Date.now()) / 86_400_000);
  if (days < 0) return { text: `lapsed ${Math.abs(days)}d ago`, tone: "error" };
  if (days <= 7) return { text: `until ${fmtDate(lead.attribution_expires_on)} (${days}d)`, tone: "warning" };
  return { text: `until ${fmtDate(lead.attribution_expires_on)}`, tone: "success" };
}

export default function PartnerLeadsPage() {
  const [rows, setRows] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noProfile, setNoProfile] = useState(false);
  const [stateFilter, setStateFilter] = useState("all");
  const [query, setQuery] = useState("");

  useEffect(() => {
    callOdoo<{ leads?: Lead[]; error?: { code: string; message: string } }>("/partner/referrals")
      .then((d) => {
        if (d.error) {
          if (d.error.code === "no_partner_profile") setNoProfile(true);
          else setError(d.error.message);
        } else setRows(d.leads ?? []);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows
      .filter((l) => (stateFilter === "all" ? true : l.state === stateFilter))
      .filter((l) => (!q ? true : `${l.referred} ${l.service_interest} ${l.lead}`.toLowerCase().includes(q)));
  }, [rows, stateFilter, query]);

  const exportCsv = () =>
    downloadCsv(
      `1000fix-partner-leads-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Lead", "Customer", "Service interest", "State", "Loss reason", "Protected until", "Referral", "Commission (BDT)"],
      visible.map((l) => [
        l.lead,
        l.referred,
        l.service_interest,
        l.state,
        l.loss_reason,
        l.attribution_expires_on,
        l.referral,
        l.commission_bdt,
      ])
    );

  if (loading) return <Loading label="Loading your lead pipeline…" />;
  if (noProfile) {
    return (
      <main style={pageStyle}>
        <PageHeader title="No partner profile is linked" subtitle="Leads are only available to an onboarded partner account." />
        <Panel><div style={{ padding: 16, fontSize: 13, color: tokens["color.text.secondary"] }}>
          Contact the partner desk on <strong>16743</strong> to complete onboarding/KYC.
        </div></Panel>
      </main>
    );
  }
  if (error && rows.length === 0) return <LoadError what="leads" message={error} />;

  const submitted = rows.filter((l) => l.state === "submitted").length;
  const qualified = rows.filter((l) => l.state === "qualified").length;
  const converted = rows.filter((l) => l.state === "converted").length;
  const lost = rows.filter((l) => l.state === "lost").length;
  const winRate = converted + lost > 0 ? Math.round((converted / (converted + lost)) * 100) : null;

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Leads"
        subtitle="Every customer you referred, its pipeline state, why it was lost if it was, and how long the attribution protection runs."
        actions={
          <>
            <Link href="/referrals" style={{ ...primaryLinkStyle, textDecoration: "none" }}>+ Submit a lead</Link>
            <button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>⬇ Export CSV</button>
          </>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Leads" value={rows.length} tone="primary" />
        <StatCard label="Submitted" value={submitted} tone="warning" />
        <StatCard label="Qualified" value={qualified} tone="primary" />
        <StatCard label="Converted" value={converted} tone="success" />
        <StatCard label="Lost" value={lost} tone={lost ? "error" : "neutral"} />
        <StatCard label="Win rate" value={winRate == null ? "—" : `${winRate}%`} note="converted ÷ closed" />
      </section>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", marginBottom: 12 }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search customer, interest or lead no…"
          aria-label="Search leads"
          style={{ ...selectStyle, flex: "1 1 280px", maxWidth: 420 }}
        />
        <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} aria-label="Lead state" style={selectStyle}>
          <option value="all">All states</option>
          <option value="submitted">Submitted</option>
          <option value="qualified">Qualified</option>
          <option value="converted">Converted</option>
          <option value="lost">Lost</option>
        </select>
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>{visible.length} of {rows.length} leads</span>
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Lead</th>
                <th style={thStyle}>Customer</th>
                <th style={thStyle}>Service interest</th>
                <th style={thStyle}>State</th>
                <th style={thStyle}>Protection</th>
                <th style={thStyle}>Referral</th>
                <th style={thStyle}>Loss reason</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((l) => {
                const p = protection(l);
                return (
                  <tr key={l.lead}>
                    <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11.5 }}>{l.lead}</td>
                    <td style={{ ...tdStyle, fontWeight: 600 }}>{l.referred}</td>
                    <td style={tdStyle}>{l.service_interest || "—"}</td>
                    <td style={tdStyle}><StateBadge state={l.state} /></td>
                    <td style={tdStyle}><Badge tone={p.tone}>{p.text}</Badge></td>
                    <td style={tdStyle}>{l.referral || "—"}</td>
                    <td style={{ ...tdStyle, color: l.loss_reason ? tokens["color.status.error"] : tokens["color.text.secondary"] }}>
                      {l.loss_reason || "—"}
                    </td>
                  </tr>
                );
              })}
              {visible.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 24 }}>
                    {rows.length === 0 ? "No leads submitted yet — start on the Referrals page." : "No leads match this filter."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <p style={{ marginTop: 12, fontSize: 11, color: tokens["color.text.secondary"] }}>
        Attribution is lead-level: the window starts when the lead is submitted, and conversion/commission
        are recorded by 1000 FiX against that lead. Click and link tracking are not offered.
      </p>
    </main>
  );
}
