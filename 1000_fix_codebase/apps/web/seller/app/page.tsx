"use client";

/* P07 seller dashboard — onboarding state (KYC), rating, jobs count.
 * The KYC gate is stated here: an unverified seller sees WHY quoting is
 * blocked (the server refuses the quote — never a client-side warn). */
import { useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Loading, LoadError, Stat } from "../lib/imports";
import { callOdoo } from "../lib/api";

interface Seller {
  id: number; name: string; kyc_status: string; kyc_ref: string;
  rating: number; total_jobs: number;
}

export default function SellerDashboard() {
  const [seller, setSeller] = useState<Seller | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ seller?: Seller; error?: { message: string } }>("/seller/dashboard")
      .then((d) => {
        if (d.error) setError(d.error.message);
        else setSeller(d.seller || null);
        setLoading(false);
      })
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return <Loading />;
  if (error) return <LoadError what="seller profile" message={error} />;

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title={seller?.name || "Seller"}
        note="Marketplace seller home — onboarding, standing and headline numbers (M12)"
      />
      {seller && (
        <>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <Stat label="KYC" value={<Pill state={seller.kyc_status} />} />
            <Stat label="Rating" value={`${seller.rating.toFixed(1)} / 5`} tone="primary" />
            <Stat label="Total jobs" value={seller.total_jobs} />
          </div>
          {seller.kyc_status !== "verified" && (
            <p role="status" style={{
              marginTop: 16, padding: "10px 14px",
              borderRadius: tokens["dimension.border.radius-sm"],
              background: tokens["color.status.warning-bg"],
              color: tokens["color.status.warning"],
              fontSize: tokens["typography.size.200"],
            }}>
              KYC {seller.kyc_status} — quoting opens once verification completes
              (server-enforced; ref {seller.kyc_ref || "pending"}).
            </p>
          )}
        </>
      )}
    </main>
  );
}
