"use client";

/**
 * Invoices — submission into the three-way match and the statement of what
 * happened to each bill. The server judges (PO / receipt / invoice); this
 * page never computes or overrides the match. A blocked invoice is shown
 * WITH its exact block reason (G3-06).
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import { tokens, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  Badge,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  downloadCsv,
  fmtDate,
  inputStyle,
  linkButtonStyle,
  pageStyle,
  primaryLinkStyle,
  selectStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Invoice {
  id: number;
  invoice_ref: string;
  po_ref: string;
  date: string;
  due_date: string;
  subtotal_bdt: string;
  tds_bdt: string;
  payable_bdt: string;
  match_state: string;
  approval_state: string;
  payment_state: string;
  match_detail: string;
}

interface POLine {
  id: number;
  product_id: number;
  product: string;
  ordered: number;
  received: number;
  unit_price_bdt: string;
}

interface PO {
  id: number;
  ref: string;
  state: string;
  lines: POLine[];
}

export default function VendorInvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [pos, setPOs] = useState<PO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noProfile, setNoProfile] = useState(false);
  const [notice, setNotice] = useState<{ kind: "success" | "error"; text: string } | null>(null);
  const [poId, setPoId] = useState<number | null>(null);
  const [stateFilter, setStateFilter] = useState("all");
  const [busy, setBusy] = useState(false);
  const [showForm, setShowForm] = useState(false);

  const reload = useCallback(async () => {
    const [inv, po] = await Promise.all([
      callOdoo<{ invoices?: Invoice[]; error?: { code: string; message: string } }>("/vendor/invoices"),
      callOdoo<{ purchase_orders?: PO[]; error?: { code: string; message: string } }>("/vendor/purchase-orders"),
    ]);
    const denied = inv.error ?? po.error;
    if (denied) {
      if (denied.code === "no_supplier_profile") setNoProfile(true);
      else setError(denied.message);
      return;
    }
    setInvoices(inv.invoices ?? []);
    setPOs(po.purchase_orders ?? []);
    setError(null);
  }, []);

  useEffect(() => {
    reload()
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [reload]);

  const selectedPO = pos.find((p) => p.id === poId);
  const visible = useMemo(
    () => (stateFilter === "all" ? invoices : invoices.filter((i) => i.match_state === stateFilter)),
    [invoices, stateFilter]
  );

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!selectedPO) return;
    const form = new FormData(e.currentTarget);
    const lines = selectedPO.lines
      .map((l) => ({
        product_id: l.product_id,
        description: l.product,
        quantity: Number(form.get(`qty-${l.id}`) || 0),
        unit_price: Number(form.get(`price-${l.id}`) || 0),
      }))
      .filter((l) => l.quantity > 0);
    if (lines.length === 0) {
      setNotice({ kind: "error", text: "Enter at least one quantity." });
      return;
    }
    setBusy(true);
    setNotice(null);
    try {
      const d = await callOdoo<{
        invoice?: { match_state: string; match_detail: string; replayed?: boolean };
        error?: { message: string };
      }>("/vendor/invoices", {
        invoice_ref: String(form.get("ref") || "").trim(),
        po_id: selectedPO.id,
        invoice_date: String(form.get("invoice_date") || "") || undefined,
        lines,
      });
      if (d.error) throw new Error(d.error.message);
      setNotice({
        kind: d.invoice?.match_state === "blocked" ? "error" : "success",
        text: `${d.invoice?.replayed ? "Already lodged — " : "Submitted — "}match: ${d.invoice?.match_state} (${d.invoice?.match_detail})`,
      });
      (e.target as HTMLFormElement).reset();
      setPoId(null);
      await reload();
    } catch (err) {
      setNotice({ kind: "error", text: (err as Error).message });
    } finally {
      setBusy(false);
    }
  }

  const exportCsv = () =>
    downloadCsv(
      `1000fix-vendor-invoices-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Invoice", "PO", "Date", "Due", "Subtotal (BDT)", "TDS (BDT)", "Payable (BDT)", "Match", "Approval", "Payment", "Block reason"],
      visible.map((i) => [
        i.invoice_ref,
        i.po_ref,
        i.date,
        i.due_date,
        i.subtotal_bdt,
        i.tds_bdt,
        i.payable_bdt,
        i.match_state,
        i.approval_state,
        i.payment_state,
        i.match_detail,
      ])
    );

  if (loading) return <Loading label="Loading your invoices…" />;
  if (noProfile) {
    return (
      <main style={pageStyle}>
        <PageHeader title="No supplier profile is linked" subtitle="Invoices are only available to an active supplier account." />
        <Panel><div style={{ padding: 16, fontSize: 13, color: tokens["color.text.secondary"] }}>
          Contact the supplier desk on <strong>16743</strong> to complete onboarding.
        </div></Panel>
      </main>
    );
  }
  if (error && invoices.length === 0) return <LoadError what="invoices" message={error} />;

  const blocked = invoices.filter((i) => i.match_state === "blocked").length;
  const matched = invoices.filter((i) => i.match_state === "matched").length;
  const unpaid = invoices.filter((i) => i.payment_state !== "paid").length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Invoices"
        subtitle="Submit your paper against a PO. The server runs the three-way match (PO / goods receipt / invoice) and records approval and payment; a blocked invoice shows why."
        actions={
          <>
            <button type="button" onClick={() => setShowForm((v) => !v)} style={{ ...primaryLinkStyle, border: "none", cursor: "pointer" }}>
              {showForm ? "Hide form" : "+ Submit an invoice"}
            </button>
            <button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>⬇ Export CSV</button>
          </>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Invoices" value={invoices.length} tone="primary" />
        <StatCard label="Matched" value={matched} tone="success" />
        <StatCard label="Blocked" value={blocked} tone={blocked ? "error" : "success"} />
        <StatCard label="Unpaid" value={unpaid} tone={unpaid ? "warning" : "success"} note="approval / payment in AP" />
      </section>

      {notice && (
        <div role={notice.kind === "error" ? "alert" : "status"} style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: notice.kind === "error" ? tokens["color.status.error-bg"] : tokens["color.status.success-bg"], color: notice.kind === "error" ? tokens["color.status.error"] : tokens["color.status.success"], fontSize: 12.5 }}>
          {notice.text}
        </div>
      )}

      {showForm && (
        <Panel title="Submit an invoice against a PO">
          <form onSubmit={submit} style={{ padding: 16, display: "grid", gap: 12 }}>
            <p style={{ margin: 0, fontSize: 12, color: tokens["color.text.secondary"] }}>
              Price the lines as your paper shows them. The match compares them with the approved PO price and
              the accepted receipt quantity; a difference blocks the invoice and the reason is shown below.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
              <label style={{ display: "grid", gap: 4, fontSize: 12, fontWeight: 600 }}>
                Invoice ref (your paper)
                <input name="ref" required maxLength={64} style={inputStyle} placeholder="e.g. DSP-INV-2026-020" />
              </label>
              <label style={{ display: "grid", gap: 4, fontSize: 12, fontWeight: 600 }}>
                Against PO
                <select
                  value={poId ?? ""}
                  onChange={(e) => setPoId(e.target.value ? Number(e.target.value) : null)}
                  required
                  style={selectStyle}
                >
                  <option value="">— select PO —</option>
                  {pos.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.ref} ({p.state})
                    </option>
                  ))}
                </select>
              </label>
              <label style={{ display: "grid", gap: 4, fontSize: 12, fontWeight: 600 }}>
                Invoice date (optional)
                <input name="invoice_date" type="date" style={inputStyle} />
              </label>
            </div>

            {selectedPO && (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ background: tokens["color.surface.secondary"] }}>
                      <th style={thStyle}>Product</th>
                      <th style={{ ...thStyle, textAlign: "right" }}>Ordered</th>
                      <th style={{ ...thStyle, textAlign: "right" }}>Received</th>
                      <th style={{ ...thStyle, textAlign: "right" }}>PO price</th>
                      <th style={{ ...thStyle, textAlign: "right" }}>Invoice qty</th>
                      <th style={{ ...thStyle, textAlign: "right" }}>Invoice unit price</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedPO.lines.map((l) => (
                      <tr key={l.id}>
                        <td style={{ ...tdStyle, fontWeight: 600 }}>{l.product}</td>
                        <td style={{ ...tdStyle, textAlign: "right" }}>{l.ordered}</td>
                        <td style={{ ...tdStyle, textAlign: "right" }}>{l.received}</td>
                        <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {l.unit_price_bdt}</td>
                        <td style={tdStyle}>
                          <input
                            name={`qty-${l.id}`}
                            type="number"
                            min={0}
                            step="0.01"
                            defaultValue={0}
                            aria-label={`Invoice quantity for ${l.product}`}
                            style={{ ...inputStyle, width: 110, textAlign: "right" }}
                          />
                        </td>
                        <td style={tdStyle}>
                          <input
                            name={`price-${l.id}`}
                            type="number"
                            min={0}
                            step="0.01"
                            defaultValue={l.unit_price_bdt.replace(/,/g, "")}
                            aria-label={`Invoice unit price for ${l.product}`}
                            style={{ ...inputStyle, width: 130, textAlign: "right" }}
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div>
              <button type="submit" disabled={busy || !selectedPO} style={{ ...primaryLinkStyle, border: "none", cursor: busy ? "wait" : "pointer", opacity: busy || !selectedPO ? 0.6 : 1 }}>
                {busy ? "Submitting…" : "Submit for match"}
              </button>
            </div>
          </form>
        </Panel>
      )}

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", margin: "16px 0 12px" }}>
        <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} aria-label="Match state" style={selectStyle}>
          <option value="all">All match states</option>
          <option value="matched">Matched</option>
          <option value="blocked">Blocked</option>
          <option value="unmatched">Unmatched</option>
          <option value="not_required">Not required</option>
        </select>
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>{visible.length} of {invoices.length} invoices</span>
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Invoice</th>
                <th style={thStyle}>PO</th>
                <th style={thStyle}>Date</th>
                <th style={thStyle}>Due</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Subtotal</th>
                <th style={{ ...thStyle, textAlign: "right" }}>TDS</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Payable</th>
                <th style={thStyle}>Match</th>
                <th style={thStyle}>Approval</th>
                <th style={thStyle}>Payment</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((i) => (
                <tr key={i.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{i.invoice_ref}</td>
                  <td style={tdStyle}>{i.po_ref || "—"}</td>
                  <td style={tdStyle}>{fmtDate(i.date)}</td>
                  <td style={tdStyle}>{fmtDate(i.due_date)}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {i.subtotal_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {i.tds_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums", fontWeight: 700 }}>৳ {i.payable_bdt}</td>
                  <td style={tdStyle}><StateBadge state={i.match_state} /></td>
                  <td style={tdStyle}><StateBadge state={i.approval_state} /></td>
                  <td style={tdStyle}><StateBadge state={i.payment_state} /></td>
                </tr>
              ))}
              {visible.length === 0 && (
                <tr>
                  <td colSpan={10} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 24 }}>
                    {invoices.length === 0 ? "No invoices submitted yet." : "No invoices in this match state."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      {invoices.some((i) => i.match_state === "blocked") && (
        <div style={{ marginTop: 16 }}>
          <Panel title="Blocked invoices — exact reasons">
            <ul style={{ margin: 0, padding: "14px 18px 14px 34px", display: "grid", gap: 8, fontSize: 12.5 }}>
              {invoices.filter((i) => i.match_state === "blocked").map((i) => (
                <li key={i.id}>
                  <strong>{i.invoice_ref}</strong> ({i.po_ref || "no PO"}): {i.match_detail || "No detail recorded."}
                </li>
              ))}
            </ul>
          </Panel>
        </div>
      )}

      <p style={{ marginTop: 12, fontSize: 11, color: tokens["color.text.secondary"] }}>
        <Badge tone="neutral">Match is server-side</Badge>{" "}
        Approval and payment are AP decisions; the portal reports them. A duplicate submission of the same
        PO + reference returns the bill already lodged instead of creating a second one.
      </p>
    </main>
  );
}
