"use client";

/* P12 Partner Attribution — the partner's identity from /partner/profile.
 * Referral-link tracking (ref/UTM parameters, click attribution) and the
 * per-channel funnel have NO backend service: the booking flow does not
 * read a partner ref and no click/channel data is recorded. The page says
 * so instead of generating links nothing consumes or showing sample
 * funnels. WCAG 2.2 AA compliant. */
import { useEffect, useState } from "react";
import { tokens, SectionHead, Stat, Pill, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface Partner {
  id: number;
  name: string;
  partner_type: string;
  territory: string;
  commission_rate: number;
  state: string;
}

const panel: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 24,
  marginBottom: 24,
};

export default function PartnerAttributionPage() {
  const [partner, setPartner] = useState<Partner | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ partner?: Partner; error?: { message: string } } | undefined>("/partner/profile")
      .then((d) => {
        if (!d) setError("The server returned an empty response.");
        else if (d.error) setError(d.error.message);
        else setPartner(d.partner ?? null);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;
  if (error) return <LoadError what="partner profile" message={error} />;

  return (
    <main style={{ padding: 32, maxWidth: 1050, margin: "0 auto" }}>
      <SectionHead
        title="Partner Attribution &amp; Funnel (অ্যাট্রিবিউশন ও ট্র্যাকিং)"
        note="Your partner identity and referral attribution"
      />

      {partner && (
        <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
          <Stat label="Partner" value={partner.name} tone="primary" />
          <Stat label="Partner ID" value={`#${partner.id}`} />
          <Stat label="Type" value={partner.partner_type} />
          <Stat label="State" value={<Pill state={partner.state} />} />
        </div>
      )}

      <section style={panel} aria-label="Attributed booking links">
        <h2
          style={{
            fontSize: tokens["typography.size.300"],
            fontWeight: Number(tokens["typography.weight.semibold"]),
            marginTop: 0,
            marginBottom: 8,
          }}
        >
          Attributed Booking Links — not yet available
        </h2>
        <p style={{ margin: 0, color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
          There is no backend service that records bookings or clicks from partner referral links, so links
          cannot be generated here — a booking made through one would not be credited to you. Submit each
          introduction on the{" "}
          <a href="/referrals" style={{ color: tokens["color.primary.base"] }}>Referrals</a> page to be
          credited.
        </p>
      </section>

      <section style={panel} aria-label="Attribution channels performance">
        <h2
          style={{
            fontSize: tokens["typography.size.300"],
            fontWeight: Number(tokens["typography.weight.semibold"]),
            marginTop: 0,
            marginBottom: 8,
          }}
        >
          Channel Attribution Breakdown — not yet available
        </h2>
        <p style={{ margin: 0, color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
          Click, conversion and per-channel commission data are not collected by the backend yet. Your
          backend-computed earnings are on the{" "}
          <a href="/commissions" style={{ color: tokens["color.primary.base"] }}>Commissions</a> statement.
        </p>
      </section>
    </main>
  );
}
