"use client";

/**
 * Attribution & funnel — built ONLY from the partner's real leads and
 * referrals. Attribution here is lead-level (the customer the partner
 * named, with recorded consent), not click/link tracking: the platform
 * records no clicks, so no link or funnel-by-channel is fabricated.
 */
import { useEffect, useMemo, useState } from "react";
import { tokens, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  Badge,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  fmtDate,
  linkButtonStyle,
  pageStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Profile {
  id: number;
  name: string;
  partner_type: string;
  territory: string;
  commission_rate: number;
  state: string;
  kyc_verified: boolean;
}

interface Lead {
  lead: string;
  referred: string;
  state: string;
  loss_reason: string;
  service_interest: string;
  attribution_expires_on: string;
  referral: string;
  commission_bdt: string;
}

interface Referral {
  id: number;
  name: string;
  state: string;
  commission_bdt: string;
}

const STAGES: { key: string; label: string; tone: "warning" | "info" | "success" | "error" }[] = [
  { key: "submitted", label: "Submitted", tone: "warning" },
  { key: "qualified", label: "Qualified", tone: "info" },
  { key: "converted", label: "Converted", tone: "success" },
  { key: "lost", label: "Lost", tone: "error" },
];

export default function PartnerAttributionPage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noProfile, setNoProfile] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const p = await callOdoo<{ partner?: Profile; error?: { code: string; message: string } }>("/partner/profile");
        if (p.error) {
          if (p.error.code === "no_partner_profile") setNoProfile(true);
          else setError(p.error.message);
          return;
        }
        setProfile(p.partner ?? null);
        const r = await callOdoo<{ referrals?: Referral[]; leads?: Lead[]; error?: { message: string } }>(
          "/partner/referrals"
        );
        if (r.error) setError(r.error.message);
        else {
          setLeads(r.leads ?? []);
          setReferrals(r.referrals ?? []);
        }
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const lossReasons = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const l of leads) {
      if (l.state !== "lost") continue;
      const reason = l.loss_reason || "No reason recorded";
      counts[reason] = (counts[reason] ?? 0) + 1;
    }
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  }, [leads]);

  if (loading) return <Loading label="Building your funnel…" />;
  if (noProfile) {
    return (
      <main style={pageStyle}>
        <PageHeader title="No partner profile is linked" subtitle="The funnel is built from your own leads and referrals." />
        <Panel><div style={{ padding: 16, fontSize: 13, color: tokens["color.text.secondary"] }}>
          Contact the partner desk on <strong>16743</strong> to complete onboarding/KYC.
        </div></Panel>
      </main>
    );
  }
  if (error) return <LoadError what="the attribution funnel" message={error} />;

  const counts: Record<string, number> = {
    submitted: leads.filter((l) => l.state === "submitted").length,
    qualified: leads.filter((l) => l.state === "qualified").length,
    converted: leads.filter((l) => l.state === "converted").length,
    lost: leads.filter((l) => l.state === "lost").length,
  };
  const closed = counts.converted + counts.lost;
  const winRate = closed > 0 ? Math.round((counts.converted / closed) * 100) : null;
  const commissioned = referrals.filter((r) => r.state === "commissioned").length;
  const maxStage = Math.max(1, ...Object.values(counts));
  const protectedLeads = leads.filter(
    (l) => !["converted", "lost"].includes(l.state) && l.attribution_expires_on && Date.parse(`${l.attribution_expires_on}T23:59:59Z`) >= Date.now()
  ).length;
  const partnerCode = `P12-${String(profile?.id ?? 0).padStart(4, "0")}`;

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Attribution & funnel"
        subtitle="Lead-level attribution from your own submissions: who you referred, how far each lead progressed, why deals were lost and which ones became commissioned referrals."
        actions={<a href="/referrals" style={{ ...linkButtonStyle, textDecoration: "none" }}>+ Submit a lead</a>}
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Leads" value={leads.length} tone="primary" />
        <StatCard label="Protected now" value={protectedLeads} tone="success" note="unclosed leads inside the window" />
        <StatCard label="Win rate" value={winRate == null ? "—" : `${winRate}%`} note="converted ÷ closed" />
        <StatCard label="Commissioned referrals" value={commissioned} tone="success" />
        <StatCard label="Partner code" value={partnerCode} note="quote it to the partner desk" />
      </section>

      <Panel title="Lead funnel (current state)">
        <div style={{ padding: 16, display: "grid", gap: 12 }}>
          {STAGES.map((s) => {
            const value = counts[s.key] ?? 0;
            const pct = Math.round((value / maxStage) * 100);
            return (
              <div key={s.key} style={{ display: "grid", gridTemplateColumns: "120px minmax(0, 1fr) 48px", gap: 10, alignItems: "center" }}>
                <span style={{ fontSize: 12.5, color: tokens["color.text.secondary"] }}>{s.label}</span>
                <div style={{ height: 18, borderRadius: 9, background: tokens["color.surface.secondary"], overflow: "hidden" }}>
                  <div
                    style={{
                      width: `${Math.max(pct, value > 0 ? 4 : 0)}%`,
                      height: "100%",
                      background:
                        s.tone === "success"
                          ? tokens["color.status.success"]
                          : s.tone === "error"
                            ? tokens["color.status.error"]
                            : s.tone === "info"
                              ? tokens["color.status.info"]
                              : tokens["color.status.warning"],
                      opacity: 0.8,
                    }}
                  />
                </div>
                <strong style={{ textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{value}</strong>
              </div>
            );
          })}
          <p style={{ margin: 0, fontSize: 11.5, color: tokens["color.text.secondary"] }}>
            Bars show the number of leads currently in each state (not a historical cohort), so a lead that
            moved from submitted to converted appears once, in converted.
          </p>
        </div>
      </Panel>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 16, marginTop: 16 }}>
        <Panel title="Loss reasons">
          <div style={{ padding: 16 }}>
            {lossReasons.length === 0 ? (
              <p style={{ margin: 0, fontSize: 12.5, color: tokens["color.text.secondary"] }}>No lost leads recorded.</p>
            ) : (
              <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 8 }}>
                {lossReasons.map(([reason, count]) => (
                  <li key={reason} style={{ display: "flex", justifyContent: "space-between", gap: 10, fontSize: 12.5, borderTop: `1px solid ${tokens["color.border.default"]}`, paddingTop: 8 }}>
                    <span style={{ color: tokens["color.text.primary"] }}>{reason}</span>
                    <Badge tone="error">{count}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Panel>

        <Panel title="Protection status">
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: tokens["color.surface.secondary"] }}>
                  <th style={thStyle}>Customer</th>
                  <th style={thStyle}>State</th>
                  <th style={thStyle}>Protected until</th>
                </tr>
              </thead>
              <tbody>
                {leads.slice(0, 8).map((l) => {
                  const closed = ["converted", "lost"].includes(l.state);
                  const lapsed = !closed && l.attribution_expires_on && Date.parse(`${l.attribution_expires_on}T23:59:59Z`) < Date.now();
                  return (
                    <tr key={l.lead}>
                      <td style={{ ...tdStyle, fontWeight: 600 }}>{l.referred}</td>
                      <td style={tdStyle}><StateBadge state={l.state} /></td>
                      <td style={tdStyle}>
                        {closed ? (
                          <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>closed</span>
                        ) : lapsed ? (
                          <Badge tone="error">lapsed</Badge>
                        ) : (
                          <Badge tone="success">{fmtDate(l.attribution_expires_on)}</Badge>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {leads.length === 0 && (
                  <tr>
                    <td colSpan={3} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 22 }}>
                      No leads yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>

      <Panel title="Attribution model">
        <div style={{ padding: 16, display: "grid", gap: 8, fontSize: 12.5, lineHeight: 1.6, color: tokens["color.text.secondary"] }}>
          <p style={{ margin: 0 }}>
            <strong style={{ color: tokens["color.text.primary"] }}>What is recorded:</strong> a lead is the
            customer you named — name, phone and service interest — with the customer&apos;s consent and the
            method it was given. The attribution window starts at submission; conversion and commission are
            recorded by 1000 FiX against that lead.
          </p>
          <p style={{ margin: 0 }}>
            <strong style={{ color: tokens["color.text.primary"] }}>What is not recorded:</strong> clicks,
            link referrals, UTM parameters and per-channel funnels. Co-branded tracking links would credit
            nothing, so the portal does not generate them.
          </p>
          <p style={{ margin: 0 }}>
            <strong style={{ color: tokens["color.text.primary"] }}>Protection:</strong> an open lead stays in
            the attribution window until its expiry date. Use the Leads page for the full list and the
            partner desk (16743) for disputes.
          </p>
        </div>
      </Panel>
    </main>
  );
}
