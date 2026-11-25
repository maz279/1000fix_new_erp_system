"use client";

/**
 * Disputes — every dispute against the seller's jobs with its reason, amount
 * and 48-hour resolution standing. The route is read-only: there is no
 * seller-initiated dispute service, so the page says so instead of pretending.
 */
import { useEffect, useMemo, useState } from "react";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  Badge,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  downloadCsv,
  linkButtonStyle,
  pageStyle,
  selectStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface DisputeItem {
  id: string;
  order_ref: string;
  dispute_reason: string;
  disputed_amount_bdt: string;
  state: string;
  sla_breached: boolean;
  sla_deadline: string;
  description: string;
}

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
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    callOdoo<{ disputes?: DisputeItem[]; error?: { message: string } }>("/seller/disputes")
      .then((d) => {
        if (d.error) setError(d.error.message);
        else setDisputes(d.disputes ?? []);
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  const filtered = useMemo(
    () =>
      disputes.filter((d) =>
        filter === "all" ? true : filter === "open" ? OPEN_STATES.has(d.state) : d.state === filter
      ),
    [disputes, filter]
  );

  const exportCsv = () =>
    downloadCsv(
      `1000fix-seller-disputes-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Dispute", "Order", "Reason", "Amount (BDT)", "SLA deadline", "SLA breached", "State"],
      disputes.map((d) => [
        d.id,
        d.order_ref,
        REASON_LABELS[d.dispute_reason] ?? d.dispute_reason,
        d.disputed_amount_bdt,
        d.sla_deadline,
        d.sla_breached ? "Yes" : "No",
        d.state,
      ])
    );

  if (loading) return <Loading label="Loading disputes…" />;
  if (error) return <LoadError what="disputes" message={error} />;

  const open = disputes.filter((d) => OPEN_STATES.has(d.state)).length;
  const breached = disputes.filter((d) => d.sla_breached).length;
  const resolved = disputes.filter((d) => d.state === "resolved").length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Dispute management (48h SLA)"
        subtitle="BRU-BIL-03: disputes raised against your marketplace jobs, with their 48-hour resolution standing."
        actions={
          <button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>
            ⬇ Export CSV
          </button>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Open disputes" value={open} tone="warning" />
        <StatCard label="SLA breached" value={breached} tone={breached ? "error" : "success"} />
        <StatCard label="Resolved" value={resolved} tone="success" />
        <StatCard label="Total" value={disputes.length} />
      </section>

      <p
        role="note"
        style={{
          padding: "10px 14px",
          marginBottom: 16,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.surface.secondary"],
          color: tokens["color.text.secondary"],
          fontSize: 12,
          border: `1px solid ${tokens["color.border.default"]}`,
        }}
      >
        Filing a new dispute from the seller portal is not yet available — there is no backend
        service for seller-raised disputes. Contact seller support (16743) to raise one.
      </p>

      <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 12 }}>
        <select value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Dispute state" style={selectStyle}>
          <option value="all">All states</option>
          <option value="open">Open</option>
          <option value="raised">Raised</option>
          <option value="investigating">Investigating</option>
          <option value="arbitration">Arbitration</option>
          <option value="escalated">Escalated</option>
          <option value="resolved">Resolved</option>
        </select>
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
          {filtered.length} of {disputes.length}
        </span>
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Dispute</th>
                <th style={thStyle}>Order</th>
                <th style={thStyle}>Reason</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Amount</th>
                <th style={thStyle}>48h SLA</th>
                <th style={thStyle}>State</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((d) => (
                <tr key={d.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{d.id}</td>
                  <td style={tdStyle}>{d.order_ref || "—"}</td>
                  <td style={tdStyle}>
                    {REASON_LABELS[d.dispute_reason] ?? d.dispute_reason}
                    {d.description && (
                      <div style={{ fontSize: 11, color: tokens["color.text.secondary"] }}>{d.description}</div>
                    )}
                  </td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {d.disputed_amount_bdt}</td>
                  <td style={tdStyle}>
                    <Badge tone={d.sla_breached ? "error" : "success"}>{d.sla_breached ? "Breached" : "Within SLA"}</Badge>
                    {d.sla_deadline && (
                      <div style={{ fontSize: 10.5, color: tokens["color.text.secondary"], marginTop: 2 }}>
                        by {d.sla_deadline.slice(0, 16)}
                      </div>
                    )}
                  </td>
                  <td style={tdStyle}><StateBadge state={d.state} /></td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 26 }}>
                    No disputes in this filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>
    </main>
  );
}
