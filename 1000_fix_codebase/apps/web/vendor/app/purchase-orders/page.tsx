"use client";

/**
 * Purchase orders — the vendor's own POs. Acknowledging is the RFQ
 * response: the vendor confirms the delivery date it commits to. Goods
 * receipts are a WAREHOUSE act (the backend refuses a vendor's delivery
 * confirmation), so this page shows received/accepted progress read-only.
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

interface POLine {
  id: number;
  product: string;
  ordered: number;
  received: number;
  unit_price_bdt: string;
}

interface PO {
  id: number;
  ref: string;
  state: string;
  date_order: string;
  acknowledged_at: string | null;
  vendor_confirmed_date: string;
  promised_date: string;
  received_on: string;
  sent_at: string;
  lines: POLine[];
  total_bdt: string;
}

interface Notice {
  kind: "success" | "error";
  text: string;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function PurchaseOrdersPage() {
  const [pos, setPOs] = useState<PO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noProfile, setNoProfile] = useState(false);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [ackFor, setAckFor] = useState<PO | null>(null);
  const [ackDate, setAckDate] = useState("");
  const [busy, setBusy] = useState(false);
  const [stateFilter, setStateFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState<number | null>(null);

  const reload = useCallback(async () => {
    const d = await callOdoo<{ purchase_orders?: PO[]; error?: { code: string; message: string } }>(
      "/vendor/purchase-orders"
    );
    if (d.error) {
      if (d.error.code === "no_supplier_profile") setNoProfile(true);
      else setError(d.error.message);
      return;
    }
    setPOs(d.purchase_orders ?? []);
    setError(null);
  }, []);

  useEffect(() => {
    reload()
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [reload]);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return pos
      .filter((p) => (stateFilter === "all" ? true : p.state === stateFilter))
      .filter((p) => (!q ? true : `${p.ref} ${p.lines.map((l) => l.product).join(" ")}`.toLowerCase().includes(q)));
  }, [pos, stateFilter, query]);

  const openAck = (po: PO) => {
    setAckFor(po);
    setAckDate(po.vendor_confirmed_date || todayIso());
    setNotice(null);
  };

  async function acknowledge(e: React.FormEvent) {
    e.preventDefault();
    if (!ackFor) return;
    setBusy(true);
    setNotice(null);
    try {
      const d = await callOdoo<{ purchase_order?: { state: string }; error?: { message: string } }>(
        "/vendor/purchase-orders",
        { po_id: ackFor.id, action: "acknowledge", delivery_date: ackDate }
      );
      if (d.error) throw new Error(d.error.message);
      setNotice({ kind: "success", text: `${ackFor.ref}: acknowledged for ${ackDate}.` });
      setAckFor(null);
      await reload();
    } catch (err) {
      setNotice({ kind: "error", text: (err as Error).message });
    } finally {
      setBusy(false);
    }
  }

  const exportCsv = () =>
    downloadCsv(
      `1000fix-vendor-purchase-orders-${new Date().toISOString().slice(0, 10)}.csv`,
      ["PO", "State", "Ordered", "Confirmed delivery", "Received on", "Total (BDT)", "Acknowledged"],
      visible.map((p) => [
        p.ref,
        p.state,
        p.date_order,
        p.vendor_confirmed_date,
        p.received_on,
        p.total_bdt,
        p.acknowledged_at ?? "",
      ])
    );

  if (loading) return <Loading label="Loading your purchase orders…" />;
  if (noProfile) {
    return (
      <main style={pageStyle}>
        <PageHeader title="No supplier profile is linked" subtitle="Purchase orders are only available to an active supplier account." />
        <Panel><div style={{ padding: 16, fontSize: 13, color: tokens["color.text.secondary"] }}>
          Contact the supplier desk on <strong>16743</strong> to complete onboarding.
        </div></Panel>
      </main>
    );
  }
  if (error && pos.length === 0) return <LoadError what="purchase orders" message={error} />;

  const awaiting = pos.filter((p) => p.state === "sent").length;
  const partial = pos.filter((p) => p.state === "partially_received").length;
  const received = pos.filter((p) => ["received", "closed"].includes(p.state)).length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Purchase orders"
        subtitle="Acknowledge the POs issued to you with the delivery date you commit to. Received and accepted quantities are booked by the 1000 FiX warehouse."
        actions={<button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>⬇ Export CSV</button>}
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Purchase orders" value={pos.length} tone="primary" />
        <StatCard label="Awaiting your ack" value={awaiting} tone={awaiting ? "warning" : "success"} />
        <StatCard label="Partially received" value={partial} tone={partial ? "warning" : "neutral"} />
        <StatCard label="Fully received" value={received} tone="success" />
      </section>

      {notice && (
        <div role={notice.kind === "error" ? "alert" : "status"} style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: notice.kind === "error" ? tokens["color.status.error-bg"] : tokens["color.status.success-bg"], color: notice.kind === "error" ? tokens["color.status.error"] : tokens["color.status.success"], fontSize: 12.5 }}>
          {notice.text}
        </div>
      )}

      {ackFor && (
        <Panel title={`Acknowledge ${ackFor.ref}`}>
          <form onSubmit={acknowledge} style={{ padding: 16, display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
            <div>
              <label htmlFor="ack-date" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>
                Delivery date you confirm (YYYY-MM-DD)
              </label>
              <input
                id="ack-date"
                type="date"
                required
                min={todayIso()}
                value={ackDate}
                onChange={(e) => setAckDate(e.target.value)}
                style={{ ...inputStyle, width: 200 }}
              />
            </div>
            <button type="submit" disabled={busy || !ackDate} style={{ ...primaryLinkStyle, border: "none", cursor: busy ? "wait" : "pointer", opacity: busy ? 0.7 : 1 }}>
              {busy ? "Recording…" : "Acknowledge"}
            </button>
            <button type="button" style={linkButtonStyle} disabled={busy} onClick={() => setAckFor(null)}>
              Cancel
            </button>
            <p style={{ margin: 0, flex: "1 1 260px", fontSize: 11.5, color: tokens["color.text.secondary"] }}>
              On-time delivery is measured against this date. Acknowledge only when the date is firm.
            </p>
          </form>
        </Panel>
      )}

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", margin: "16px 0 12px" }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search PO ref or product…"
          aria-label="Search purchase orders"
          style={{ ...selectStyle, flex: "1 1 280px", maxWidth: 420 }}
        />
        <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} aria-label="PO state" style={selectStyle}>
          <option value="all">All states</option>
          <option value="sent">Sent</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="partially_received">Partially received</option>
          <option value="received">Received</option>
          <option value="closed">Closed</option>
        </select>
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>{visible.length} of {pos.length} POs</span>
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>PO</th>
                <th style={thStyle}>Ordered</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Total (BDT)</th>
                <th style={thStyle}>State</th>
                <th style={thStyle}>Your delivery date</th>
                <th style={thStyle}>Lines</th>
                <th style={thStyle}>Action</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((p) => {
                const accepted = p.lines.reduce(
                  (sum, l) => sum + Math.min(l.received, l.ordered),
                  0
                );
                const ordered = p.lines.reduce((sum, l) => sum + l.ordered, 0);
                return (
                  <tr key={p.id}>
                    <td style={{ ...tdStyle, fontWeight: 600 }}>{p.ref}</td>
                    <td style={tdStyle}>{fmtDate(p.date_order)}</td>
                    <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {p.total_bdt}</td>
                    <td style={tdStyle}><StateBadge state={p.state} /></td>
                    <td style={tdStyle}>{fmtDate(p.vendor_confirmed_date)}</td>
                    <td style={tdStyle}>
                      <button
                        type="button"
                        onClick={() => setExpanded(expanded === p.id ? null : p.id)}
                        style={{ ...linkButtonStyle, padding: "4px 10px" }}
                        aria-expanded={expanded === p.id}
                      >
                        {p.lines.length} line{p.lines.length === 1 ? "" : "s"} · {accepted}/{ordered} received
                      </button>
                    </td>
                    <td style={tdStyle}>
                      {p.state === "sent" ? (
                        <button type="button" onClick={() => openAck(p)} style={{ ...primaryLinkStyle, padding: "5px 12px", border: "none", cursor: "pointer" }}>
                          Acknowledge
                        </button>
                      ) : (
                        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
                          {p.state === "acknowledged" || p.state === "partially_received"
                            ? "receipt by warehouse"
                            : p.received_on
                              ? `received ${fmtDate(p.received_on)}`
                              : "—"}
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
              {visible.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 24 }}>
                    {pos.length === 0 ? "No purchase orders issued yet." : "No POs match this filter."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      {expanded != null && (() => {
        const po = pos.find((p) => p.id === expanded);
        if (!po) return null;
        return (
          <div style={{ marginTop: 16 }}>
            <Panel title={`${po.ref} — lines`}>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ background: tokens["color.surface.secondary"] }}>
                      <th style={thStyle}>Product</th>
                      <th style={{ ...thStyle, textAlign: "right" }}>Ordered</th>
                      <th style={{ ...thStyle, textAlign: "right" }}>Received</th>
                      <th style={{ ...thStyle, textAlign: "right" }}>Unit price</th>
                      <th style={thStyle}>Progress</th>
                    </tr>
                  </thead>
                  <tbody>
                    {po.lines.map((l) => {
                      const pct = l.ordered > 0 ? Math.min(100, Math.round((l.received / l.ordered) * 100)) : 0;
                      return (
                        <tr key={l.id}>
                          <td style={{ ...tdStyle, fontWeight: 600 }}>{l.product}</td>
                          <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{l.ordered}</td>
                          <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{l.received}</td>
                          <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {l.unit_price_bdt}</td>
                          <td style={tdStyle}>
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                              <div style={{ flex: 1, height: 8, minWidth: 90, borderRadius: 4, background: tokens["color.surface.secondary"], overflow: "hidden" }}>
                                <div style={{ width: `${pct}%`, height: "100%", background: tokens["color.status.success"], opacity: 0.8 }} />
                              </div>
                              <span style={{ fontSize: 11, color: tokens["color.text.secondary"], width: 34, textAlign: "right" }}>{pct}%</span>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <p style={{ margin: 0, padding: "10px 16px", fontSize: 11.5, color: tokens["color.text.secondary"] }}>
                Received quantities are the warehouse&apos;s posted goods receipts. Only inspected/accepted goods
                count toward the three-way match; the vendor never self-certifies delivery.
              </p>
            </Panel>
          </div>
        );
      })()}

      <p style={{ marginTop: 12, fontSize: 11, color: tokens["color.text.secondary"] }}>
        <Badge tone="neutral">Receipts are warehouse-recorded</Badge>{" "}
        Acknowledge only a PO issued to you; foreign or draft POs are not visible.
      </p>
    </main>
  );
}
