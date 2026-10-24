"use client";

/* P07 Disputes — the seller's dispute history and 48h SLA standing
 * (BRU-BIL-03) from /seller/disputes. That route is read-only: the
 * backend exposes no dispute-creation service for sellers, so the portal
 * does not pretend to file one. Amounts are backend BN-007 strings (AS-10).
 * WCAG 2.2 AA compliant. */
import { useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Stat, DataTable, Loading, LoadError } from "../../lib/imports";
import type { Column } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface DisputeItem {
  id: string;
  order_ref: string;
  dispute_reason: string;
  disputed_amount_bdt: string;
  state: string;
  sla_breached: boolean;
  description: string;
}

// fix.marketplace.dispute.dispute_reason labels (cd_marketplace)
const REASON_LABELS: Record<string, string> = {
  quality: "Substandard Repair Quality",
  delay: "Delay Exceeding SLA",
  pricing: "Unauthorized Additional Charges",
  damage: "Device Damage",
  unresponsive: "Seller Unresponsive",
};

const OPEN_STATES = new Set(["raised", "investigating", "arbitration", "escalated"]);

export default function SellerDisputesPage() {
  const [disputes, setDisputes] = useState<DisputeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ disputes?: DisputeItem[]; error?: { message: string } } | undefined>("/seller/disputes")
      .then((d) => {
        if (!d) setError("The server returned an empty response.");
        else if (d.error) setError(d.error.message);
        else setDisputes(d.disputes ?? []);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;
  if (error) return <LoadError what="disputes" message={error} />;

  const columns: Column<DisputeItem>[] = [
    { header: "Dispute Ref", cell: (d) => <strong>{d.id}</strong> },
    { header: "Order", cell: (d) => d.order_ref || "—" },
    { header: "Reason", cell: (d) => REASON_LABELS[d.dispute_reason] ?? d.dispute_reason },
    {
      header: "Disputed Amount",
      cell: (d) => <span style={{ fontVariantNumeric: "tabular-nums" }}>৳ {d.disputed_amount_bdt}</span>,
    },
    {
      header: "48h SLA",
      cell: (d) => (
        <span
          style={{
            color: d.sla_breached ? tokens["color.status.error"] : tokens["color.text.secondary"],
            fontWeight: Number(tokens["typography.weight.semibold"]),
          }}
        >
          {d.sla_breached ? "Breached" : "Within SLA"}
        </span>
      ),
    },
    { header: "Status", cell: (d) => <Pill state={d.state} /> },
  ];

  return (
    <main style={{ padding: 32, maxWidth: 1050, margin: "0 auto" }}>
      <SectionHead
        title="Dispute Management &amp; 48h SLA (বিরোধ নিষ্পত্তি)"
        note="BRU-BIL-03: disputes raised against your marketplace orders, with their 48-hour resolution SLA standing"
      />

      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <Stat label="Open Disputes" value={disputes.filter((d) => OPEN_STATES.has(d.state)).length} tone="primary" />
        <Stat label="SLA Breached" value={disputes.filter((d) => d.sla_breached).length} />
        <Stat label="Total" value={disputes.length} />
      </div>

      <p
        role="note"
        style={{
          padding: "10px 14px",
          marginBottom: 20,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.surface.secondary"],
          color: tokens["color.text.secondary"],
          fontSize: tokens["typography.size.200"],
          border: `1px solid ${tokens["color.border.default"]}`,
        }}
      >
        Filing a new dispute from the seller portal is not yet available — there is no backend service
        for seller-raised disputes. Contact 1000FiX seller support (hotline 16743) to raise one.
      </p>

      {disputes.length === 0 ? (
        <p style={{ color: tokens["color.text.secondary"] }}>No disputes on record.</p>
      ) : (
        <DataTable rows={disputes} columns={columns} keyOf={(d) => d.id} />
      )}
    </main>
  );
}
