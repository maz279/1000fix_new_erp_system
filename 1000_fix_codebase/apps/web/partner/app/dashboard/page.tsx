"use client";

/**
 * Partner dashboard — standing, KYC state, commission terms and the live
 * lead/referral/commission totals, all resolved from the signed-in user by
 * the server. No partner id is ever taken from the browser.
 */
import { useEffect, useState } from "react";
import Link from "next/link";
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
  primaryLinkStyle,
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
  email: string;
  phone: string;
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
  referred: string;
  service_interest: string;
  state: string;
  commission_bdt: string;
}

interface CommissionSummary {
  earned_total_bdt?: string;
  lines?: { state: string; commission_bdt: string }[];
}

const TYPE_LABEL: Record<string, string> = {
  referral: "Referral partner",
  reseller: "Reseller",
  franchise: "Franchise",
  alliance: "Strategic alliance",
};

export default function PartnerDashboardPage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [commission, setCommission] = useState<CommissionSummary>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noProfile, setNoProfile] = useState(false);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const p = await callOdoo<{ partner?: Profile; error?: { code: string; message: string } }>(
          "/partner/profile"
        );
        if (p.error) {
          if (p.error.code === "no_partner_profile") setNoProfile(true);
          else setError(p.error.message);
          return;
        }
        if (!active) return;
        setProfile(p.partner ?? null);
        const [r, c] = await Promise.all([
          callOdoo<{ referrals?: Referral[]; leads?: Lead[]; error?: { message: string } }>(
            "/partner/referrals"
          ),
          callOdoo<{ commissions?: CommissionSummary; error?: { message: string } }>(
            "/partner/commissions"
          ),
        ]);
        if (!active) return;
        if (r.error) setError(r.error.message);
        else {
          setReferrals(r.referrals ?? []);
          setLeads(r.leads ?? []);
        }
        if (!c.error) setCommission(c.commissions ?? {});
      } catch (e: unknown) {
        if (active) setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  if (loading) return <Loading label="Loading your partner standing…" />;
  if (noProfile) {
    return (
      <main style={pageStyle}>
        <PageHeader
          title="No partner profile is linked"
          subtitle="Your sign-in is valid, but it is not linked to a channel-partner profile. Partner onboarding and KYC are handled by 1000 FiX."
        />
        <Panel title="What to do">
          <div style={{ padding: 16, fontSize: 13, lineHeight: 1.6, color: tokens["color.text.secondary"] }}>
            <p style={{ margin: "0 0 10px" }}>
              Contact the partner desk on <strong>16743</strong> and quote the email on your account. Once
              onboarding is complete, the profile is linked and this dashboard fills in.
            </p>
            <p style={{ margin: 0 }}>
              Leads, referrals and commissions are only ever shown for the partner profile the server
              resolves from your session — never for an id typed into the browser.
            </p>
          </div>
        </Panel>
      </main>
    );
  }
  if (error || !profile) return <LoadError what="the partner dashboard" message={error || "No profile returned."} />;

  const submitted = leads.filter((l) => l.state === "submitted").length;
  const qualified = leads.filter((l) => l.state === "qualified").length;
  const converted = leads.filter((l) => l.state === "converted").length;
  const lost = leads.filter((l) => l.state === "lost").length;
  const commissioned = referrals.filter((r) => r.state === "commissioned").length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title={profile.name}
        subtitle={`${TYPE_LABEL[profile.partner_type] ?? profile.partner_type} · ${profile.territory || "no territory on record"}. Your standing, pipeline and commission at a glance.`}
        actions={
          <>
            <Link href="/referrals" style={{ ...primaryLinkStyle, textDecoration: "none" }}>
              + Submit a lead
            </Link>
            <Link href="/commissions" style={{ ...linkButtonStyle, textDecoration: "none" }}>
              Commission statement
            </Link>
          </>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Leads" value={leads.length} tone="primary" note={`${submitted} submitted · ${qualified} qualified`} />
        <StatCard label="Converted" value={converted} tone="success" note={`${lost} lost`} />
        <StatCard label="Referrals" value={referrals.length} note={`${commissioned} commissioned`} />
        <StatCard label="Commission rate" value={`${(profile.commission_rate * 100).toFixed(1)}%`} tone="primary" />
        <StatCard label="Earned commission" value={`৳ ${commission.earned_total_bdt ?? "0.00"}`} tone="success" />
      </section>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) minmax(280px, 1fr)", gap: 16, alignItems: "start" }}>
        <Panel title="Partner standing">
          <div style={{ padding: 16, display: "grid", gap: 10, fontSize: 13 }}>
            <Row label="Standing" value={<StateBadge state={profile.state} />} />
            <Row label="Partner type" value={TYPE_LABEL[profile.partner_type] ?? profile.partner_type} />
            <Row label="Territory" value={profile.territory || "—"} />
            <Row label="Commission rate" value={`${(profile.commission_rate * 100).toFixed(1)}%`} />
            <Row
              label="KYC"
              value={profile.kyc_verified ? <Badge tone="success">verified</Badge> : <Badge tone="warning">pending</Badge>}
            />
            <Row label="Partner email" value={profile.email || "—"} />
            <Row label="Partner phone" value={profile.phone || "—"} />
            <Row label="Partner ID" value={`#${profile.id}`} />
          </div>
        </Panel>

        <Panel title="Lead pipeline">
          <div style={{ padding: 16, display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 10 }}>
            {[
              ["Submitted", submitted, "warning"],
              ["Qualified", qualified, "info"],
              ["Converted", converted, "success"],
              ["Lost", lost, "error"],
            ].map(([label, value, tone]) => (
              <div
                key={String(label)}
                style={{
                  padding: 12,
                  borderRadius: tokens["dimension.border.radius-sm"],
                  border: `1px solid ${tokens["color.border.default"]}`,
                  background: tokens["color.surface.canvas"],
                }}
              >
                <div style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>{label}</div>
                <div style={{ fontSize: 22, fontWeight: 700, marginTop: 2 }}>{value}</div>
                <div style={{ marginTop: 6 }}>
                  <Badge tone={tone as "warning" | "info" | "success" | "error"}>{leads.length ? `${Math.round((Number(value) / leads.length) * 100)}%` : "0%"}</Badge>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 16, marginTop: 16 }}>
        <Panel
          title="Recent leads"
          actions={<Link href="/leads" style={{ fontSize: 12, color: tokens["color.primary.base"], textDecoration: "none", fontWeight: 600 }}>View all</Link>}
        >
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: tokens["color.surface.secondary"] }}>
                  <th style={thStyle}>Customer</th>
                  <th style={thStyle}>Interest</th>
                  <th style={thStyle}>State</th>
                  <th style={thStyle}>Protected until</th>
                </tr>
              </thead>
              <tbody>
                {leads.slice(0, 5).map((l) => (
                  <tr key={l.lead}>
                    <td style={{ ...tdStyle, fontWeight: 600 }}>{l.referred}</td>
                    <td style={tdStyle}>{l.service_interest || "—"}</td>
                    <td style={tdStyle}><StateBadge state={l.state} /></td>
                    <td style={tdStyle}>{["converted", "lost"].includes(l.state) ? "—" : fmtDate(l.attribution_expires_on)}</td>
                  </tr>
                ))}
                {leads.length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 22 }}>
                      No leads submitted yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel
          title="Recent referrals"
          actions={<Link href="/commissions" style={{ fontSize: 12, color: tokens["color.primary.base"], textDecoration: "none", fontWeight: 600 }}>Statement</Link>}
        >
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: tokens["color.surface.secondary"] }}>
                  <th style={thStyle}>Referral</th>
                  <th style={thStyle}>Customer</th>
                  <th style={thStyle}>State</th>
                  <th style={{ ...thStyle, textAlign: "right" }}>Commission</th>
                </tr>
              </thead>
              <tbody>
                {referrals.slice(0, 5).map((r) => (
                  <tr key={r.id}>
                    <td style={{ ...tdStyle, fontWeight: 600 }}>{r.name}</td>
                    <td style={tdStyle}>{r.referred || "—"}</td>
                    <td style={tdStyle}><StateBadge state={r.state} /></td>
                    <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {r.commission_bdt}</td>
                  </tr>
                ))}
                {referrals.length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 22 }}>
                      No referrals recorded yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>

      <p style={{ marginTop: 14, fontSize: 11, color: tokens["color.text.secondary"] }}>
        Commission is the frozen rate applied to approved referred revenue, computed by the backend. The
        earned total sums commissioned referrals only.
      </p>
    </main>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", borderTop: `1px solid ${tokens["color.border.default"]}`, paddingTop: 8 }}>
      <span style={{ color: tokens["color.text.secondary"] }}>{label}</span>
      <span style={{ fontWeight: 600, color: tokens["color.text.primary"], textAlign: "right" }}>{value}</span>
    </div>
  );
}
