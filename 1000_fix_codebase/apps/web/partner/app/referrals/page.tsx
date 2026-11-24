"use client";

/**
 * Referrals — submit a lead the way the backend actually accepts it:
 * customer name + phone (+ email/interest) and RECORDED consent, never a
 * party id. The server creates a fix.partner.lead with an attribution
 * window; the referral row and commission are the company's to establish.
 */
import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { tokens, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  Badge,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  downloadCsv,
  inputStyle,
  linkButtonStyle,
  pageStyle,
  primaryLinkStyle,
  selectStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Referral {
  id: number;
  name: string;
  referred: string;
  service_interest: string;
  state: string;
  commission_bdt: string;
}

const CONSENT_METHODS: [string, string][] = [
  ["digital", "Digital (OTP / click)"],
  ["written", "Written form"],
  ["recorded_call", "Recorded call"],
];

export default function ReferralsPage() {
  const [rows, setRows] = useState<Referral[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noProfile, setNoProfile] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [stateFilter, setStateFilter] = useState("all");

  const reload = useCallback(async () => {
    const d = await callOdoo<{ referrals?: Referral[]; leads?: { lead: string; referred: string }[]; error?: { code: string; message: string } }>(
      "/partner/referrals"
    );
    if (d.error) {
      if (d.error.code === "no_partner_profile") setNoProfile(true);
      else setError(d.error.message);
      return;
    }
    setRows(d.referrals ?? []);
    setError(null);
  }, []);

  useEffect(() => {
    reload()
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [reload]);

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    setBusy(true);
    setSubmitError(null);
    setNotice(null);
    try {
      const d = await callOdoo<{
        lead?: { name: string; state: string };
        error?: { message: string };
      }>("/partner/referrals", {
        referred_name: String(form.get("referred_name") || "").trim(),
        referred_phone: String(form.get("referred_phone") || "").trim(),
        referred_email: String(form.get("referred_email") || "").trim(),
        service_interest: String(form.get("service_interest") || "").trim(),
        consent_given: form.get("consent_given") === "on",
        consent_method: String(form.get("consent_method") || ""),
      });
      if (d.error) throw new Error(d.error.message);
      setNotice(`${d.lead?.name ?? "Lead"} submitted (${d.lead?.state ?? "submitted"}) — the protection window starts now.`);
      (e.target as HTMLFormElement).reset();
      await reload();
    } catch (err) {
      setSubmitError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const visible = useMemo(
    () => (stateFilter === "all" ? rows : rows.filter((r) => r.state === stateFilter)),
    [rows, stateFilter]
  );

  const exportCsv = () =>
    downloadCsv(
      `1000fix-partner-referrals-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Referral", "Customer", "Service interest", "State", "Commission (BDT)"],
      visible.map((r) => [r.name, r.referred, r.service_interest, r.state, r.commission_bdt])
    );

  if (loading) return <Loading label="Loading your referrals…" />;
  if (noProfile) {
    return (
      <main style={pageStyle}>
        <PageHeader title="No partner profile is linked" subtitle="Referrals are only available to an onboarded partner account." />
        <Panel><div style={{ padding: 16, fontSize: 13, color: tokens["color.text.secondary"] }}>
          Contact the partner desk on <strong>16743</strong> to complete onboarding/KYC. The portal never accepts
          a partner id from the browser.
        </div></Panel>
      </main>
    );
  }
  if (error && rows.length === 0) return <LoadError what="referrals" message={error} />;

  const commissioned = rows.filter((r) => r.state === "commissioned").length;
  const converted = rows.filter((r) => r.state === "converted").length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Referrals"
        subtitle="Submit a customer lead with recorded consent. A person — not a party id — is the referral: the company links the lead to the customer when it converts."
        actions={<button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>⬇ Export CSV</button>}
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Referrals" value={rows.length} tone="primary" />
        <StatCard label="Converted" value={converted} tone="success" />
        <StatCard label="Commissioned" value={commissioned} tone="success" />
      </section>

      {notice && (
        <div role="status" style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.success-bg"], color: tokens["color.status.success"], fontSize: 12.5 }}>
          {notice}
        </div>
      )}

      <Panel title="Submit a customer lead">
        <form onSubmit={submit} style={{ padding: 16, display: "grid", gap: 12 }}>
          <p style={{ margin: 0, fontSize: 12, color: tokens["color.text.secondary"] }}>
            Consent is mandatory (BRU-PCM-06). Record what the customer agreed to and how; a submission
            without both is refused by the server.
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
            <Field label="Customer name (required)">
              <input name="referred_name" required maxLength={120} style={inputStyle} placeholder="e.g. Tanvir Ahmed" />
            </Field>
            <Field label="Customer phone (required)">
              <input name="referred_phone" required maxLength={32} style={inputStyle} placeholder="+8801XXXXXXXXX" />
            </Field>
            <Field label="Customer email (optional)">
              <input name="referred_email" type="email" maxLength={120} style={inputStyle} placeholder="name@example.com" />
            </Field>
            <Field label="Service interest">
              <input name="service_interest" maxLength={120} style={inputStyle} placeholder="e.g. Corporate AMC — 40 laptops" />
            </Field>
            <Field label="Consent recorded how? (required)">
              <select name="consent_method" required defaultValue="digital" style={selectStyle}>
                {CONSENT_METHODS.map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </Field>
          </div>
          <label style={{ display: "inline-flex", alignItems: "center", gap: 8, fontSize: 12.5 }}>
            <input type="checkbox" name="consent_given" required />
            The customer agreed to be contacted by 1000 FiX about this service (consent recorded)
          </label>
          {submitError && (
            <p role="alert" style={{ margin: 0, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.error-bg"], color: tokens["color.status.error"], fontSize: 12.5 }}>
              {submitError}
            </p>
          )}
          <div>
            <button type="submit" disabled={busy} style={{ ...primaryLinkStyle, border: "none", cursor: busy ? "wait" : "pointer", opacity: busy ? 0.7 : 1 }}>
              {busy ? "Submitting…" : "Submit lead"}
            </button>
          </div>
        </form>
      </Panel>

      <div style={{ display: "flex", gap: 10, alignItems: "center", margin: "16px 0 12px", flexWrap: "wrap" }}>
        <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} aria-label="Referral state" style={selectStyle}>
          <option value="all">All states</option>
          <option value="submitted">Submitted</option>
          <option value="converted">Converted</option>
          <option value="commissioned">Commissioned</option>
        </select>
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>{visible.length} of {rows.length} referrals</span>
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Referral</th>
                <th style={thStyle}>Customer</th>
                <th style={thStyle}>Service interest</th>
                <th style={thStyle}>State</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Commission (BDT)</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((r) => (
                <tr key={r.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{r.name}</td>
                  <td style={tdStyle}>{r.referred || "—"}</td>
                  <td style={tdStyle}>{r.service_interest || "—"}</td>
                  <td style={tdStyle}><StateBadge state={r.state} /></td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {r.commission_bdt}</td>
                </tr>
              ))}
              {visible.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 24 }}>
                    No referrals in this view.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <p style={{ marginTop: 12, fontSize: 11, color: tokens["color.text.secondary"] }}>
        A submitted lead is protected for the attribution window and appears on the <a href="/leads" style={{ color: tokens["color.primary.base"] }}>Leads</a> page.
        Conversion and commissioning are company decisions; the commission rate is frozen when earned.
      </p>
      <Badge tone="neutral">Lead-level attribution only — no click tracking</Badge>
    </main>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label style={{ display: "grid", gap: 4, fontSize: 12, fontWeight: 600, color: tokens["color.text.primary"] }}>
      <span>{label}</span>
      {children}
    </label>
  );
}
