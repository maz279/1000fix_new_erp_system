"use client";

/* P05 purchase orders — RFQ response (acknowledge a sent PO), delivery
 * confirmation (line-level receipts), PO list. G3-06 note: the
 * three-way match runs on invoices (see /invoices). All data from
 * /vendor/purchase-orders (P-11); money arrives as BN-007 strings. */
import { useCallback, useEffect, useState } from "react";
import { tokens, Pill, SectionHead, DataTable, Loading, LoadError, Stat } from "../lib/imports";
import type { Column } from "../lib/imports";
import { callOdoo } from "../lib/api";

interface POLine {
  id: number; product: string; ordered: number; received: number;
  unit_price_bdt: string;
}
interface PO {
  id: number; ref: string; state: string; date_order: string;
  acknowledged_at: string | null; lines: POLine[]; total_bdt: string;
}

const btn: React.CSSProperties = {
  padding: "6px 14px",
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
  background: tokens["color.primary.base"],
  color: tokens["color.text.inverse"],
};
const ghostBtn: React.CSSProperties = {
  ...btn,
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.secondary"],
  border: `1px solid ${tokens["color.border.default"]}`,
};

export default function PurchaseOrdersPage() {
  const [pos, setPOs] = useState<PO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  const reload = useCallback(async () => {
    const d = await callOdoo<{ purchase_orders: PO[] }>("/vendor/purchase-orders");
    setPOs(d.purchase_orders || []);
  }, []);

  useEffect(() => {
    reload()
      .then(() => setLoading(false))
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, [reload]);

  async function acknowledge(po: PO) {
    const d = await callOdoo<{ purchase_order?: { state: string }; error?: { message: string } }>(
      "/vendor/purchase-orders", { po_id: po.id, action: "acknowledge" });
    setNotice(d.error ? d.error.message : `${po.ref}: acknowledged`);
    if (!d.error) reload();
  }

  async function deliver(po: PO) {
    // one delivery row per line, prefilled with the outstanding qty
    const receipts: Record<string, number> = {};
    for (const l of po.lines) {
      const outstanding = l.ordered - l.received;
      if (outstanding <= 0) continue;
      const v = window.prompt(
        `${l.product} — deliver how many? (outstanding ${outstanding})`,
        String(outstanding));
      if (v === null) return;
      receipts[String(l.id)] = Number(v);
    }
    if (Object.keys(receipts).length === 0) {
      setNotice("Nothing outstanding on this PO");
      return;
    }
    const d = await callOdoo<{ purchase_order?: { state: string }; error?: { message: string } }>(
      "/vendor/purchase-orders", { po_id: po.id, action: "deliver", receipts });
    setNotice(d.error ? d.error.message : `${po.ref}: ${d.purchase_order?.state}`);
    if (!d.error) reload();
  }

  if (loading) return <Loading />;
  if (error) return <LoadError what="purchase orders" message={error} />;

  const awaiting = pos.filter((p) => p.state === "sent").length;
  const columns: Column<PO>[] = [
    { header: "PO Ref", cell: (p) => p.ref },
    { header: "Ordered", cell: (p) => p.date_order.slice(0, 10) },
    { header: "Total (BDT)", cell: (p) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{p.total_bdt}</span> },
    { header: "State", cell: (p) => <Pill state={p.state} /> },
    {
      header: "Lines",
      cell: (p) => (
        <button style={ghostBtn} onClick={() => setExpanded(expanded === p.id ? null : p.id)}>
          {p.lines.length} line{p.lines.length === 1 ? "" : "s"} {expanded === p.id ? "▲" : "▼"}
        </button>
      ),
    },
    {
      header: "Action",
      cell: (p) => p.state === "sent" ? (
        <button style={btn} onClick={() => acknowledge(p)}>Acknowledge</button>
      ) : p.state === "acknowledged" || p.state === "partially_received" ? (
        <button style={ghostBtn} onClick={() => deliver(p)}>Confirm delivery</button>
      ) : "—",
    },
  ];

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="Purchase Orders"
        note="Acknowledge sent POs (RFQ response) and confirm deliveries — the received side of the three-way match"
      />
      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Stat label="POs" value={pos.length} />
        <Stat label="Awaiting ack" value={awaiting} tone="primary" />
      </div>
      {notice && (
        <p role="status" style={{
          padding: "10px 14px", marginBottom: 16,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.status.info-bg"],
          color: tokens["color.status.info"],
          fontSize: tokens["typography.size.200"],
        }}>{notice}</p>
      )}
      <DataTable rows={pos} columns={columns} />

      {expanded != null && (() => {
        const po = pos.find((p) => p.id === expanded);
        if (!po) return null;
        return (
          <section style={{
            marginTop: 16, padding: 20,
            border: `1px solid ${tokens["color.border.default"]}`,
            borderRadius: tokens["dimension.border.radius-md"],
            background: tokens["color.surface.primary"],
          }}>
            <strong>{po.ref} — lines</strong>
            <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 8 }}>
              <tbody>
                {po.lines.map((l) => (
                  <tr key={l.id} style={{ borderBottom: `1px solid ${tokens["color.border.default"]}` }}>
                    <td style={{ padding: "6px 12px" }}>{l.product}</td>
                    <td style={{ padding: "6px 12px", fontVariantNumeric: "tabular-nums" }}>
                      {l.received} / {l.ordered} received
                    </td>
                    <td style={{ padding: "6px 12px", fontVariantNumeric: "tabular-nums" }}>
                      ৳ {l.unit_price_bdt}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        );
      })()}
    </main>
  );
}
