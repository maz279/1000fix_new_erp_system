"use client";

/* P05 invoices — submission feeding the three-way match. G3-06: a
 * BLOCKED invoice is visible WITH its block reason, never warned about;
 * the match engine lives server-side (AS-09). */
import { useCallback, useEffect, useState } from "react";
import { tokens, Pill, SectionHead, DataTable, Loading, LoadError, Stat } from "../../lib/imports";
import type { Column } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface Invoice {
  id: number; invoice_ref: string; po_ref: string; date: string;
  subtotal_bdt: string; tds_bdt: string; payable_bdt: string;
  match_state: string; match_detail: string;
}
interface PO { id: number; ref: string; lines: { id: number; product_id: number; product: string; ordered: number; unit_price_bdt: string }[] }

const inputStyle: React.CSSProperties = {
  padding: 10,
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
  width: "100%",
};
const btn: React.CSSProperties = {
  padding: "8px 16px",
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
  background: tokens["color.primary.base"],
  color: tokens["color.text.inverse"],
};

export default function VendorInvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [pos, setPOs] = useState<PO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [poId, setPoId] = useState<number | null>(null);
  const [invoiceRef, setInvoiceRef] = useState("");

  const reload = useCallback(async () => {
    const [inv, po] = await Promise.all([
      callOdoo<{ invoices: Invoice[] }>("/vendor/invoices"),
      callOdoo<{ purchase_orders: PO[] }>("/vendor/purchase-orders"),
    ]);
    setInvoices(inv.invoices || []);
    setPOs(po.purchase_orders || []);
  }, []);

  useEffect(() => {
    reload()
      .then(() => setLoading(false))
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, [reload]);

  const selectedPO = pos.find((p) => p.id === poId);

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!selectedPO) return;
    const form = new FormData(e.currentTarget);
    const lines = selectedPO.lines.map((l) => ({
      product_id: l.product_id,
      description: l.product,
      quantity: Number(form.get(`qty-${l.id}`) || 0),
      unit_price: Number(String(l.unit_price_bdt).replace(/,/g, "")),
    })).filter((l) => l.quantity > 0);
    if (lines.length === 0) { setNotice("Enter at least one quantity"); return; }
    const d = await callOdoo<{ invoice?: { match_state: string; match_detail: string }; error?: { message: string } }>(
      "/vendor/invoices", {
        invoice_ref: form.get("ref"),
        po_id: selectedPO.id,
        lines,
      });
    setNotice(d.error
      ? d.error.message
      : `Submitted — match: ${d.invoice?.match_state} (${d.invoice?.match_detail})`);
    if (!d.error) reload();
  }

  if (loading) return <Loading />;
  if (error) return <LoadError what="invoices" message={error} />;

  const blocked = invoices.filter((i) => i.match_state === "blocked").length;
  const columns: Column<Invoice>[] = [
    { header: "Invoice Ref", cell: (i) => i.invoice_ref },
    { header: "PO", cell: (i) => i.po_ref || "—" },
    { header: "Date", cell: (i) => i.date },
    { header: "Subtotal (BDT)", cell: (i) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{i.subtotal_bdt}</span> },
    { header: "TDS (BDT)", cell: (i) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{i.tds_bdt}</span> },
    { header: "Payable (BDT)", cell: (i) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{i.payable_bdt}</span> },
    {
      header: "3-way match",
      cell: (i) => (
        <span title={i.match_detail}>
          <Pill state={i.match_state} />
        </span>
      ),
    },
  ];

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="Invoices"
        note="Submission runs the three-way match (PO / receipt / invoice). A blocked invoice shows its block reason — visible, never warned (G3-06)."
      />
      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Stat label="Invoices" value={invoices.length} />
        <Stat label="Blocked" value={blocked} tone="primary" />
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

      <section style={{
        padding: 20, marginBottom: 24,
        border: `1px solid ${tokens["color.border.default"]}`,
        borderRadius: tokens["dimension.border.radius-md"],
        background: tokens["color.surface.primary"],
      }}>
        <strong>Submit an invoice</strong>
        <form onSubmit={submit} style={{ marginTop: 12, display: "grid", gap: 12, maxWidth: 560 }}>
          <label style={{ color: tokens["color.text.secondary"] }}>
            Invoice ref (your paper)
            <input name="ref" required value={invoiceRef}
              onChange={(e) => setInvoiceRef(e.target.value)} style={inputStyle} />
          </label>
          <label style={{ color: tokens["color.text.secondary"] }}>
            Against PO
            <select value={poId ?? ""} onChange={(e) => setPoId(Number(e.target.value))} style={inputStyle}>
              <option value="">— select PO —</option>
              {pos.map((p) => <option key={p.id} value={p.id}>{p.ref}</option>)}
            </select>
          </label>
          {selectedPO?.lines.map((l) => (
            <label key={l.id} style={{ color: tokens["color.text.secondary"] }}>
              {l.product} — PO price ৳ {l.unit_price_bdt}
              <input name={`qty-${l.id}`} type="number" min={0} step="0.01" defaultValue={0} style={inputStyle} />
            </label>
          ))}
          <button type="submit" disabled={!selectedPO} style={{ ...btn, opacity: selectedPO ? 1 : 0.5 }}>
            Submit for match
          </button>
        </form>
      </section>

      <DataTable rows={invoices} columns={columns} />
      {invoices.some((i) => i.match_state === "blocked") && (
        <section style={{ marginTop: 16 }}>
          <strong style={{ color: tokens["color.status.error"] }}>Block reasons (G3-06)</strong>
          <ul style={{ marginTop: 8, paddingLeft: 20, fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>
            {invoices.filter((i) => i.match_state === "blocked").map((i) => (
              <li key={i.id}><strong>{i.invoice_ref}</strong>: {i.match_detail}</li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
