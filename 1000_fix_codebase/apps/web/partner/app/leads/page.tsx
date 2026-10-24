"use client";

/* P12 Leads Pass-Through — Enterprise B2B lead submission.
 * There is NO backend service for partner B2B leads (cd_partner exposes
 * only /partner/profile, /partner/referrals and /partner/commissions), so
 * this page states that plainly: no sample rows, no locally-"submitted"
 * leads, and no client-side commission estimates (fees are backend-computed
 * on referrals only). WCAG 2.2 AA compliant. */
import { tokens, SectionHead } from "../../lib/imports";

export default function PartnerLeadsPage() {
  return (
    <main style={{ padding: 32, maxWidth: 1050, margin: "0 auto" }}>
      <SectionHead
        title="Enterprise B2B Leads (কর্পোরেট লিডস)"
        note="Pass-through enterprise corporate repair leads"
      />

      <section
        role="status"
        aria-label="Enterprise leads unavailable"
        style={{
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-md"],
          background: tokens["color.surface.primary"],
          padding: 24,
        }}
      >
        <h2
          style={{
            fontSize: tokens["typography.size.300"],
            fontWeight: Number(tokens["typography.weight.semibold"]),
            marginTop: 0,
            marginBottom: 8,
          }}
        >
          Not yet available — no backend service
        </h2>
        <p style={{ margin: 0, color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
          Enterprise lead submission and pipeline tracking are not yet supported by the 1000FiX backend, so
          leads cannot be submitted or tracked here. To be credited for an introduction, submit it as a
          referral on the{" "}
          <a href="/referrals" style={{ color: tokens["color.primary.base"] }}>Referrals</a> page; earned
          commissions appear on the{" "}
          <a href="/commissions" style={{ color: tokens["color.primary.base"] }}>Commissions</a> statement.
        </p>
      </section>
    </main>
  );
}
