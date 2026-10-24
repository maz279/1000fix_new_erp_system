"use client";

/* P04 Corporate Portal — Multi-Site Tender & Enterprise Fleet Admin (R05-M04-T04).
 * There is NO backend tender service: cd_corporate_portal exposes only
 * /corporate/estate, /corporate/invoices/consolidated and
 * /corporate/service-requests. Until a tender endpoint exists this page
 * states that plainly — no client register, no contract values, no
 * evidence badges — and points to the live estate and invoice screens.
 * WCAG 2.2 AA, design tokens only.
 */
import Link from "next/link";
import { tokens, SectionHead } from "../../lib/imports";

const linkStyle: React.CSSProperties = {
  color: tokens["color.primary.base"],
  fontWeight: 500,
};

export default function CorporateTenderPage() {
  return (
    <main style={{ padding: "32px 40px", maxWidth: 1400, margin: "0 auto" }}>
      <header style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
          <SectionHead
            title="Multi-Site Tenders (P04)"
            note="Enterprise tender and multi-site contract administration"
          />
          <Link
            href="/"
            style={{
              padding: "10px 18px",
              background: tokens["color.surface.secondary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-sm"],
              color: tokens["color.text.primary"],
              textDecoration: "none",
              fontSize: tokens["typography.size.200"],
              fontWeight: 500,
            }}
          >
            ← Back to Dashboard
          </Link>
        </div>
      </header>

      <section
        role="status"
        aria-label="Tender administration unavailable"
        style={{
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-md"],
          background: tokens["color.surface.primary"],
          padding: 24,
        }}
      >
        <h2 style={{ fontSize: tokens["typography.size.300"], margin: "0 0 8px" }}>
          Not yet available — no backend service
        </h2>
        <p style={{ margin: 0, color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"], lineHeight: 1.5 }}>
          Tender records, multi-site contract values and SLA tiers are not yet served by the 1000FiX
          backend, so nothing can be shown here. Your live equipment is on the{" "}
          <Link href="/estate" style={linkStyle}>Estate</Link> page and your billed work is on the{" "}
          <Link href="/invoices" style={linkStyle}>Invoices</Link> page.
        </p>
      </section>
    </main>
  );
}
