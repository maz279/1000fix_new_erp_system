"use client";

/**
 * Seller onboarding & KYC — the compliance state of the seller account.
 *
 * There is no online KYC submission/verification service in this deployment,
 * so the page shows the live status, the document checklist and how to reach
 * compliance; it does not pretend to accept documents it cannot store.
 */
import { useEffect, useState } from "react";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  Badge,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  linkButtonStyle,
  pageStyle,
} from "../../components/ui";

interface SellerKyc {
  name?: string;
  kyc_status: string;
  kyc_ref: string;
  tier?: string;
  seller_type?: string;
  kyc_submitted?: string;
  kyc_verified?: string;
  rating?: number;
  total_jobs?: number;
}

const DOCS = [
  ["Trade licence", "Current trade licence from the city corporation / RJSC (INT-035)."],
  ["BIN-13", "Business Identification Number (VAT registration)."],
  ["e-TIN", "12-digit e-TIN certificate from NBR."],
  ["NID", "National ID of the owner / authorised representative."],
  ["Bank statement", "Recent statement showing the business name and account."],
];

export default function SellerOnboardingPage() {
  const [seller, setSeller] = useState<SellerKyc | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ seller?: SellerKyc; error?: { message: string } }>("/seller/dashboard")
      .then((d) => {
        if (d.error) setError(d.error.message);
        else setSeller(d.seller ?? null);
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <Loading label="Loading your KYC status…" />;
  if (error) return <LoadError what="KYC status" message={error} />;

  const status = seller?.kyc_status ?? "unverified";
  const verified = status === "verified";
  const steps = [
    { en: "Seller account created", done: Boolean(seller) },
    { en: "KYC documents submitted", done: Boolean(seller?.kyc_submitted) || verified },
    { en: "Compliance review", done: status === "in_review" || verified },
    { en: "KYC verified — quoting enabled", done: verified },
  ];

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Onboarding & KYC"
        subtitle="L6 merchant KYC — trade licence, BIN-13, e-TIN and NID verification. Quoting is gated on a verified, CFO-approved seller record."
        actions={<a href="tel:16743" style={{ ...linkButtonStyle, textDecoration: "none" }}>☎ Seller desk 16743</a>}
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="KYC status" value={status} tone={verified ? "success" : "warning"} />
        <StatCard label="Reference" value={seller?.kyc_ref || "pending"} />
        <StatCard label="Tier" value={seller?.tier || "unrated"} tone="primary" />
        <StatCard label="Rating" value={seller?.rating != null ? `${seller.rating.toFixed(1)} / 5` : "—"} />
        <StatCard label="Total jobs" value={seller?.total_jobs ?? 0} />
      </section>

      <div
        role="note"
        style={{
          marginBottom: 16,
          padding: "10px 14px",
          borderRadius: tokens["dimension.border.radius-sm"],
          background: verified ? tokens["color.status.success-bg"] : tokens["color.status.warning-bg"],
          color: verified ? tokens["color.status.success"] : tokens["color.status.warning"],
          border: `1px solid ${verified ? tokens["color.status.success"] : tokens["color.status.warning"]}`,
          fontSize: 12.5,
          lineHeight: 1.55,
        }}
      >
        {verified
          ? "Your KYC is verified. Quoting is enabled subject to the open-job and CFO-approval gates."
          : `Your KYC is ${status}. Online document submission is not available in this deployment — compliance completes verification with you directly. Contact the seller desk on 16743.`}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: 16 }}>
        <Panel title="Onboarding progress">
          <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            {steps.map((s) => (
              <div key={s.en} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 12.5 }}>
                <Badge tone={s.done ? "success" : "neutral"}>{s.done ? "✓" : "·"}</Badge>
                <span>{s.en}</span>
              </div>
            ))}
            <div style={{ marginTop: 6, fontSize: 11.5, color: tokens["color.text.secondary"] }}>
              {seller?.kyc_submitted ? `Submitted ${seller.kyc_submitted}. ` : ""}
              {seller?.kyc_verified ? `Verified ${seller.kyc_verified}. ` : ""}
            </div>
          </div>
        </Panel>

        <Panel title="Documents compliance collects">
          <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 8 }}>
            {DOCS.map(([name, desc]) => (
              <div key={name} style={{ display: "flex", gap: 10, fontSize: 12.5 }}>
                <StateBadge state={verified ? "verified" : "pending"} label={verified ? "On file" : "Required"} />
                <div>
                  <b>{name}</b>
                  <div style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>{desc}</div>
                </div>
              </div>
            ))}
            <p style={{ margin: "8px 0 0", fontSize: 11.5, color: tokens["color.text.secondary"] }}>
              Documents are handled by 1000 FiX compliance under PDPA residency controls. Do not send
              documents by email; the seller desk will provide a secure channel.
            </p>
          </div>
        </Panel>
      </div>
    </main>
  );
}
