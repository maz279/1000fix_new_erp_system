"use client";

/* P12 partner profile — the partner's standing (type, territory, rate,
 * state) with the referral/commission headlines. */
import { useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Loading, LoadError, Stat } from "../lib/imports";
import { callOdoo } from "../lib/api";

interface Partner {
  id: number; name: string; partner_type: string; territory: string;
  commission_rate: number; state: string;
}

export default function PartnerHome() {
  const [partner, setPartner] = useState<Partner | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ partner?: Partner; error?: { message: string } }>("/partner/profile")
      .then((d) => {
        if (d.error) setError(d.error.message);
        else setPartner(d.partner || null);
        setLoading(false);
      })
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return <Loading />;
  if (error) return <LoadError what="partner profile" message={error} />;

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title={partner?.name || "Partner"}
        note="Your standing in the referral programme — type, territory and commission rate (M53)"
      />
      {partner && (
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <Stat label="Type" value={partner.partner_type} />
          <Stat label="Territory" value={partner.territory || "—"} />
          <Stat label="Commission rate" value={`${(partner.commission_rate * 100).toFixed(1)}%`} tone="primary" />
          <Stat label="State" value={<Pill state={partner.state} />} />
        </div>
      )}
      <p style={{ marginTop: 24, color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
        Submit referrals from the <a href="/referrals" style={{ color: tokens["color.primary.base"] }}>Referrals</a> page;
        earned commissions accumulate on the <a href="/commissions" style={{ color: tokens["color.primary.base"] }}>Commissions</a> statement.
      </p>
    </main>
  );
}
