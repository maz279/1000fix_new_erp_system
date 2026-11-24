"use client";

/**
 * Supplier profile & compliance — the master data the buyer holds for this
 * vendor: standing, contacts, bank (masked), the latest approved
 * qualification score and every compliance document with its expiry.
 * Read-only: master-data changes and document renewals go through
 * procurement (the vendor-editable surface is deliberately narrow).
 */
import { useEffect, useState } from "react";
import { tokens, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  Badge,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  daysUntil,
  fmtDate,
  pageStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Profile {
  id: number;
  name: string;
  code: string;
  status: string;
  segment: string;
  category: string;
  residency: string;
  classification: string;
  risk_tier: string;
  onboarded_on: string;
  payment_block: boolean;
  buyer: string;
  bank: { masked: string; bank: string };
  contacts: { name: string; role: string; phone: string; email: string }[];
  latest_score: { score: number; approved_on: string; stage: string } | null;
}

interface Doc {
  id: number;
  name: string;
  doc_type: string;
  number: string;
  valid_from: string;
  valid_to: string;
  state: string;
  is_valid: boolean;
  days_to_expiry: number | null;
}

const DOC_LABEL: Record<string, string> = {
  trade_licence: "Trade licence",
  tin: "TIN certificate",
  vat: "VAT registration",
  incorporation: "Certificate of incorporation",
  tax_residency: "Tax residency",
  iso: "ISO certificate",
  insurance: "Insurance",
  bank: "Bank details",
  contract: "Signed contract",
  other: "Other",
};

const SEGMENT: Record<string, string> = {
  strategic: "Strategic",
  preferred: "Preferred",
  transactional: "Transactional",
  probationary: "Probationary",
};

function expiryBadge(doc: Doc): { text: string; tone: "success" | "warning" | "error" | "neutral" } {
  if (doc.state === "expired") return { text: "expired", tone: "error" };
  if (doc.state === "pending") return { text: "pending verification", tone: "warning" };
  const days = doc.days_to_expiry ?? daysUntil(doc.valid_to);
  if (days == null) return { text: "no end date", tone: "neutral" };
  if (days < 0) return { text: `expired ${Math.abs(days)}d ago`, tone: "error" };
  if (days <= 30) return { text: `${days} days left`, tone: "warning" };
  return { text: `${days} days left`, tone: "success" };
}

export default function VendorProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [docs, setDocs] = useState<Doc[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noProfile, setNoProfile] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const p = await callOdoo<{ supplier?: Profile; error?: { code: string; message: string } }>(
          "/vendor/portal/profile"
        );
        if (p.error) {
          if (p.error.code === "no_supplier_profile") setNoProfile(true);
          else setError(p.error.message);
          return;
        }
        setProfile(p.supplier ?? null);
        const d = await callOdoo<{ documents?: Doc[]; error?: { message: string } }>("/vendor/portal/documents");
        if (d.error) setError(d.error.message);
        else setDocs(d.documents ?? []);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <Loading label="Loading supplier profile…" />;
  if (noProfile) {
    return (
      <main style={pageStyle}>
        <PageHeader title="No supplier profile is linked" subtitle="Master data is shown only to the linked vendor account." />
        <Panel><div style={{ padding: 16, fontSize: 13, color: tokens["color.text.secondary"] }}>
          Contact the supplier desk on <strong>16743</strong> to complete onboarding.
        </div></Panel>
      </main>
    );
  }
  if (error || !profile) return <LoadError what="supplier profile" message={error || "No profile returned."} />;

  const expired = docs.filter((d) => d.state === "expired" || (d.days_to_expiry != null && d.days_to_expiry < 0));
  const soon = docs.filter(
    (d) => d.state !== "expired" && d.days_to_expiry != null && d.days_to_expiry >= 0 && d.days_to_expiry <= 30
  );

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Profile & compliance"
        subtitle={`${profile.name} · ${profile.code}. This is the master data 1000 FiX holds for you; renewals and changes are handled by procurement.`}
      />

      {profile.payment_block && (
        <div role="alert" style={{ marginBottom: 14, padding: "10px 14px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.error-bg"], color: tokens["color.status.error"], fontSize: 12.5 }}>
          <strong>Payments are blocked on this supplier account.</strong> Contact the supplier desk on 16743 before
          submitting further invoices.
        </div>
      )}

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Standing" value={profile.status} tone={profile.status === "active" ? "success" : "warning"} />
        <StatCard label="Segment" value={SEGMENT[profile.segment] ?? profile.segment} />
        <StatCard
          label="Qualification score"
          value={profile.latest_score ? `${profile.latest_score.score}%` : "—"}
          tone={profile.latest_score && profile.latest_score.score >= 85 ? "success" : "warning"}
          note={profile.latest_score ? `approved ${fmtDate(profile.latest_score.approved_on)}` : "no approved audit"}
        />
        <StatCard label="Documents" value={docs.length} note={`${expired.length} expired · ${soon.length} expiring`} tone={expired.length ? "error" : soon.length ? "warning" : "success"} />
      </section>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) minmax(300px, 1fr)", gap: 16, alignItems: "start" }}>
        <Panel title="Supplier master">
          <div style={{ padding: 16, display: "grid", gap: 9, fontSize: 12.5 }}>
            <Row label="Legal name" value={profile.name} />
            <Row label="Supplier code" value={profile.code} />
            <Row label="Status" value={<StateBadge state={profile.status} />} />
            <Row label="Segment" value={SEGMENT[profile.segment] ?? profile.segment} />
            <Row label="Spend category" value={profile.category || "—"} />
            <Row label="Residency" value={profile.residency === "resident" ? "Bangladesh-registered" : "Foreign"} />
            <Row label="Classification" value={(profile.classification || "—").replace(/_/g, " ")} />
            <Row label="Risk tier" value={profile.risk_tier || "—"} />
            <Row label="Onboarded" value={fmtDate(profile.onboarded_on)} />
            <Row label="Buyer" value={profile.buyer || "—"} />
            <Row label="Bank (masked)" value={profile.bank?.masked ? `${profile.bank.masked}${profile.bank.bank ? ` · ${profile.bank.bank}` : ""}` : "not on record"} />
            <Row label="Payment block" value={profile.payment_block ? <Badge tone="error">blocked</Badge> : <Badge tone="success">clear</Badge>} />
          </div>
        </Panel>

        <Panel title="Contacts">
          <div style={{ padding: 16, display: "grid", gap: 10 }}>
            {profile.contacts.length === 0 ? (
              <p style={{ margin: 0, fontSize: 12.5, color: tokens["color.text.secondary"] }}>No active contacts on record.</p>
            ) : (
              profile.contacts.map((c) => (
                <div key={`${c.name}-${c.role}`} style={{ padding: 10, borderRadius: tokens["dimension.border.radius-sm"], border: `1px solid ${tokens["color.border.default"]}`, background: tokens["color.surface.canvas"] }}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                    <strong style={{ fontSize: 12.5 }}>{c.name}</strong>
                    <Badge tone="neutral">{c.role}</Badge>
                  </div>
                  <div style={{ fontSize: 11.5, color: tokens["color.text.secondary"], marginTop: 4 }}>
                    {c.phone || "no phone"} · {c.email || "no email"}
                  </div>
                </div>
              ))
            )}
          </div>
        </Panel>
      </div>

      <div style={{ marginTop: 16 }}>
        <Panel title="Compliance documents">
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: tokens["color.surface.secondary"] }}>
                  <th style={thStyle}>Document</th>
                  <th style={thStyle}>Number</th>
                  <th style={thStyle}>Valid from</th>
                  <th style={thStyle}>Valid to</th>
                  <th style={thStyle}>State</th>
                  <th style={thStyle}>Expiry</th>
                </tr>
              </thead>
              <tbody>
                {docs.map((d) => {
                  const badge = expiryBadge(d);
                  return (
                    <tr key={d.id}>
                      <td style={{ ...tdStyle, fontWeight: 600 }}>{DOC_LABEL[d.doc_type] ?? d.doc_type}</td>
                      <td style={tdStyle}>{d.number || "—"}</td>
                      <td style={tdStyle}>{fmtDate(d.valid_from)}</td>
                      <td style={tdStyle}>{fmtDate(d.valid_to)}</td>
                      <td style={tdStyle}><StateBadge state={d.state} /></td>
                      <td style={tdStyle}><Badge tone={badge.tone}>{badge.text}</Badge></td>
                    </tr>
                  );
                })}
                {docs.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 24 }}>
                      No compliance documents on record.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <p style={{ margin: 0, padding: "10px 16px", fontSize: 11.5, color: tokens["color.text.secondary"] }}>
            Renewals are sent to procurement; this portal does not accept document uploads yet, and bank-detail
            changes always need a separate verified proposal (never a portal edit).
          </p>
        </Panel>
      </div>
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
