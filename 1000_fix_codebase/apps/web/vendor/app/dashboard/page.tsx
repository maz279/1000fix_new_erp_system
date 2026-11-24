"use client";

/**
 * Vendor dashboard — the supplier's own standing, the work that needs
 * attention (POs to acknowledge, blocked invoices, expiring compliance) and
 * the live totals. Everything is resolved from the session's commercial
 * partner by the server; no vendor id is taken from the browser.
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
  daysUntil,
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
  latest_score: { score: number; approved_on: string; stage: string } | null;
}

interface Doc {
  id: number;
  name: string;
  doc_type: string;
  number: string;
  valid_to: string;
  state: string;
  days_to_expiry: number | null;
}

interface Summary {
  purchase_orders?: {
    open?: number;
    awaiting_ack?: number;
    oldest_open_days?: number;
    open_value_bdt?: string;
  };
  invoices?: {
    total?: number;
    blocked?: number;
    submitted_payable_bdt?: string;
  };
  compliance?: { documents?: number; expiring_30_days?: number; expired?: number };
  score?: number | null;
}

interface PO {
  id: number;
  ref: string;
  state: string;
  date_order: string;
  vendor_confirmed_date: string;
  total_bdt: string;
}

interface Invoice {
  id: number;
  invoice_ref: string;
  po_ref: string;
  date: string;
  due_date: string;
  payable_bdt: string;
  match_state: string;
  approval_state: string;
  payment_state: string;
}

const SEGMENT: Record<string, string> = {
  strategic: "Strategic",
  preferred: "Preferred",
  transactional: "Transactional",
  probationary: "Probationary",
};

export default function VendorDashboardPage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [summary, setSummary] = useState<Summary>({});
  const [docs, setDocs] = useState<Doc[]>([]);
  const [pos, setPOs] = useState<PO[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noProfile, setNoProfile] = useState(false);

  useEffect(() => {
    let active = true;
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
        if (!active) return;
        setProfile(p.supplier ?? null);
        const [s, d, po, inv] = await Promise.all([
          callOdoo<Summary>("/vendor/portal/summary"),
          callOdoo<{ documents?: Doc[] }>("/vendor/portal/documents"),
          callOdoo<{ purchase_orders?: PO[] }>("/vendor/purchase-orders"),
          callOdoo<{ invoices?: Invoice[] }>("/vendor/invoices"),
        ]);
        if (!active) return;
        setSummary(s);
        setDocs(d.documents ?? []);
        setPOs(po.purchase_orders ?? []);
        setInvoices(inv.invoices ?? []);
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

  if (loading) return <Loading label="Loading your supplier standing…" />;
  if (noProfile) {
    return (
      <main style={pageStyle}>
        <PageHeader
          title="No supplier profile is linked"
          subtitle="Your sign-in is valid, but no supplier master is linked to this account. Supplier onboarding and KYC are handled by 1000 FiX procurement."
        />
        <Panel title="What to do">
          <div style={{ padding: 16, fontSize: 13, lineHeight: 1.6, color: tokens["color.text.secondary"] }}>
            <p style={{ margin: "0 0 10px" }}>
              Contact the supplier desk on <strong>16743</strong> and quote the email on your account. Once
              onboarding is complete and the supplier is activated, the dashboard fills in.
            </p>
            <p style={{ margin: 0 }}>
              Purchase orders and invoices are only ever shown for the commercial partner the server resolves
              from your session.
            </p>
          </div>
        </Panel>
      </main>
    );
  }
  if (error || !profile) return <LoadError what="the vendor dashboard" message={error || "No supplier returned."} />;

  const po = summary.purchase_orders ?? {};
  const inv = summary.invoices ?? {};
  const comp = summary.compliance ?? {};
  const score = profile.latest_score?.score ?? summary.score ?? null;
  const expiringDocs = docs
    .filter((d) => d.state !== "expired" && d.days_to_expiry != null && d.days_to_expiry <= 30 && d.days_to_expiry >= 0)
    .sort((a, b) => (a.days_to_expiry ?? 999) - (b.days_to_expiry ?? 999));
  const expiredDocs = docs.filter((d) => d.state === "expired" || (d.days_to_expiry != null && d.days_to_expiry < 0));

  return (
    <main style={pageStyle}>
      <PageHeader
        title={profile.name}
        subtitle={`${profile.code} · ${SEGMENT[profile.segment] ?? profile.segment} supplier · ${profile.category || "no spend category"}. Your orders, invoices, compliance and score.`}
        actions={
          <>
            <Link href="/purchase-orders" style={{ ...primaryLinkStyle, textDecoration: "none" }}>
              Purchase orders
            </Link>
            <Link href="/invoices" style={{ ...linkButtonStyle, textDecoration: "none" }}>
              Submit / view invoices
            </Link>
          </>
        }
      />

      {profile.payment_block && (
        <div role="alert" style={{ marginBottom: 14, padding: "10px 14px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.error-bg"], color: tokens["color.status.error"], fontSize: 12.5 }}>
          <strong>Payments are blocked on this supplier account.</strong> New invoices will not be paid until the
          block is lifted by 1000 FiX finance. Contact the supplier desk on 16743.
        </div>
      )}

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Open POs" value={po.open ?? 0} tone="primary" note={`oldest ${po.oldest_open_days ?? 0} days`} />
        <StatCard label="Awaiting your ack" value={po.awaiting_ack ?? 0} tone={(po.awaiting_ack ?? 0) > 0 ? "warning" : "success"} />
        <StatCard label="Open PO value" value={`৳ ${po.open_value_bdt ?? "0.00"}`} />
        <StatCard label="Blocked invoices" value={inv.blocked ?? 0} tone={(inv.blocked ?? 0) > 0 ? "error" : "success"} />
        <StatCard label="Docs expiring (30d)" value={comp.expiring_30_days ?? 0} tone={(comp.expiring_30_days ?? 0) > 0 ? "warning" : "success"} note={`${comp.expired ?? 0} expired`} />
        <StatCard label="Qualification score" value={score == null ? "—" : `${score}%`} tone={score != null && score >= 85 ? "success" : "warning"} note={profile.latest_score ? `approved ${fmtDate(profile.latest_score.approved_on)}` : "no approved audit"} />
      </section>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1.1fr) minmax(280px, 1fr)", gap: 16, alignItems: "start" }}>
        <Panel title="Action needed">
          <div style={{ padding: 16, display: "grid", gap: 10 }}>
            {(po.awaiting_ack ?? 0) > 0 && (
              <ActionRow
                title={`${po.awaiting_ack} purchase order${po.awaiting_ack === 1 ? "" : "s"} awaiting your acknowledgement`}
                body="Confirm the delivery date you commit to. The buyer's on-time measurement uses your date."
                href="/purchase-orders"
                cta="Acknowledge"
              />
            )}
            {(inv.blocked ?? 0) > 0 && (
              <ActionRow
                title={`${inv.blocked} invoice${inv.blocked === 1 ? "" : "s"} blocked by the three-way match`}
                body="Open the invoice to read the exact block reason — receipt quantity, price or approval."
                href="/invoices"
                cta="See why"
                tone="error"
              />
            )}
            {expiredDocs.length > 0 && (
              <ActionRow
                title={`${expiredDocs.length} compliance document${expiredDocs.length === 1 ? "" : "s"} expired`}
                body={`${expiredDocs.map((d) => d.doc_type.replace(/_/g, " ")).join(", ")} — send the renewal to procurement.`}
                href="/profile"
                cta="View documents"
                tone="error"
              />
            )}
            {expiringDocs.length > 0 && (
              <ActionRow
                title={`${expiringDocs.length} document${expiringDocs.length === 1 ? "" : "s"} expiring within 30 days`}
                body={expiringDocs
                  .slice(0, 3)
                  .map((d) => `${d.doc_type.replace(/_/g, " ")} (${d.days_to_expiry}d)`)
                  .join(" · ")}
                href="/profile"
                cta="Review"
                tone="warning"
              />
            )}
            {!po.awaiting_ack && !inv.blocked && expiredDocs.length === 0 && expiringDocs.length === 0 && (
              <p style={{ margin: 0, fontSize: 12.5, color: tokens["color.text.secondary"] }}>
                Nothing needs your attention right now. New POs and invoice outcomes appear here.
              </p>
            )}
          </div>
        </Panel>

        <Panel title="Supplier standing">
          <div style={{ padding: 16, display: "grid", gap: 9, fontSize: 12.5 }}>
            <Row label="Status" value={<StateBadge state={profile.status} />} />
            <Row label="Segment" value={SEGMENT[profile.segment] ?? profile.segment} />
            <Row label="Residency" value={profile.residency === "resident" ? "Bangladesh-registered" : "Foreign"} />
            <Row label="Classification" value={(profile.classification || "—").replace(/_/g, " ")} />
            <Row label="Risk tier" value={profile.risk_tier || "—"} />
            <Row label="Onboarded" value={fmtDate(profile.onboarded_on)} />
            <Row label="Buyer" value={profile.buyer || "—"} />
            <Row label="Payment block" value={profile.payment_block ? <Badge tone="error">blocked</Badge> : <Badge tone="success">clear</Badge>} />
          </div>
        </Panel>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 16, marginTop: 16 }}>
        <Panel
          title="Recent purchase orders"
          actions={<Link href="/purchase-orders" style={{ fontSize: 12, color: tokens["color.primary.base"], textDecoration: "none", fontWeight: 600 }}>View all</Link>}
        >
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: tokens["color.surface.secondary"] }}>
                  <th style={thStyle}>PO</th>
                  <th style={thStyle}>Ordered</th>
                  <th style={thStyle}>Confirmed delivery</th>
                  <th style={{ ...thStyle, textAlign: "right" }}>Total</th>
                  <th style={thStyle}>State</th>
                </tr>
              </thead>
              <tbody>
                {pos.slice(0, 5).map((p) => (
                  <tr key={p.id}>
                    <td style={{ ...tdStyle, fontWeight: 600 }}>{p.ref}</td>
                    <td style={tdStyle}>{fmtDate(p.date_order)}</td>
                    <td style={tdStyle}>{fmtDate(p.vendor_confirmed_date)}</td>
                    <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {p.total_bdt}</td>
                    <td style={tdStyle}><StateBadge state={p.state} /></td>
                  </tr>
                ))}
                {pos.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 22 }}>
                      No purchase orders issued yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel
          title="Recent invoices"
          actions={<Link href="/invoices" style={{ fontSize: 12, color: tokens["color.primary.base"], textDecoration: "none", fontWeight: 600 }}>Statement</Link>}
        >
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: tokens["color.surface.secondary"] }}>
                  <th style={thStyle}>Invoice</th>
                  <th style={thStyle}>Due</th>
                  <th style={{ ...thStyle, textAlign: "right" }}>Payable</th>
                  <th style={thStyle}>Match</th>
                  <th style={thStyle}>Payment</th>
                </tr>
              </thead>
              <tbody>
                {invoices.slice(0, 5).map((i) => (
                  <tr key={i.id}>
                    <td style={{ ...tdStyle, fontWeight: 600 }}>{i.invoice_ref}</td>
                    <td style={tdStyle}>{fmtDate(i.due_date)}</td>
                    <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {i.payable_bdt}</td>
                    <td style={tdStyle}><StateBadge state={i.match_state} /></td>
                    <td style={tdStyle}><StateBadge state={i.payment_state} /></td>
                  </tr>
                ))}
                {invoices.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 22 }}>
                      No invoices submitted yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>

      <p style={{ marginTop: 14, fontSize: 11, color: tokens["color.text.secondary"] }}>
        The score is the latest approved qualification audit. Documents list the dates the supplier master
        holds; uploads/renewals are handled by procurement. Goods receipts are a warehouse record — the portal
        never lets a vendor certify its own delivery.
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

function ActionRow({
  title,
  body,
  href,
  cta,
  tone = "warning",
}: {
  title: string;
  body: string;
  href: string;
  cta: string;
  tone?: "warning" | "error";
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        gap: 12,
        alignItems: "center",
        padding: 12,
        borderRadius: tokens["dimension.border.radius-sm"],
        border: `1px solid ${tokens["color.border.default"]}`,
        background: tone === "error" ? tokens["color.status.error-bg"] : tokens["color.surface.canvas"],
      }}
    >
      <div>
        <div style={{ fontWeight: 600, fontSize: 12.5, color: tokens["color.text.primary"] }}>{title}</div>
        <div style={{ fontSize: 11.5, color: tokens["color.text.secondary"], marginTop: 2 }}>{body}</div>
      </div>
      <Link href={href} style={{ ...linkButtonStyle, textDecoration: "none", whiteSpace: "nowrap" }}>
        {cta}
      </Link>
    </div>
  );
}
