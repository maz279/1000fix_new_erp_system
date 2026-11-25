"use client";

/**
 * Stock & listings — the seller's positions by listing/SKU, with a one-step
 * report (on-hand / reserved). The backend stamps who reported it and when;
 * only the seller's own listings accept stock.
 */
import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  PageHeader,
  Panel,
  StatCard,
  downloadCsv,
  linkButtonStyle,
  pageStyle,
  primaryLinkStyle,
  selectStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface StockRow {
  id: number;
  listing_id: number;
  listing: string;
  sku: string;
  qty_on_hand: number;
  qty_reserved: number;
  qty_available: number;
  last_updated: string;
  source: string;
}

export default function SellerStockPage() {
  const [rows, setRows] = useState<StockRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<StockRow | null>(null);
  const [onHand, setOnHand] = useState("");
  const [reserved, setReserved] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const d = await callOdoo<{ stock?: StockRow[]; error?: { message: string } }>("/seller/stock");
    if (d.error) setError(d.error.message);
    else setRows(d.stock ?? []);
  }, []);

  useEffect(() => {
    load()
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [load]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter(
      (r) => r.listing.toLowerCase().includes(q) || r.sku.toLowerCase().includes(q)
    );
  }, [rows, query]);

  const startEdit = (row: StockRow) => {
    setSelected(row);
    setOnHand(String(row.qty_on_hand));
    setReserved(String(row.qty_reserved));
    setNotice(null);
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!selected) return;
    setBusy(true);
    setError(null);
    try {
      const d = await callOdoo<{ error?: { message: string } }>("/seller/stock", {
        listing_id: selected.listing_id,
        sku: selected.sku,
        qty_on_hand: Number(onHand),
        qty_reserved: Number(reserved),
      });
      if (d.error) throw new Error(d.error.message);
      setNotice(`Stock reported for ${selected.sku}.`);
      setSelected(null);
      await load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const exportCsv = () =>
    downloadCsv(
      `1000fix-seller-stock-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Listing", "SKU", "On hand", "Reserved", "Available", "Last updated", "Source"],
      rows.map((r) => [
        r.listing,
        r.sku,
        String(r.qty_on_hand),
        String(r.qty_reserved),
        String(r.qty_available),
        r.last_updated,
        r.source,
      ])
    );

  if (loading) return <Loading label="Loading your stock positions…" />;
  if (error && rows.length === 0) return <LoadError what="stock positions" message={error} />;

  const totalOnHand = rows.reduce((s, r) => s + r.qty_on_hand, 0);
  const totalReserved = rows.reduce((s, r) => s + r.qty_reserved, 0);
  const belowPar = rows.filter((r) => r.qty_available <= 2).length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Stock & listings"
        subtitle="Your active listings with on-hand, reserved and available stock. Reporting a position is stamped by the server."
        actions={
          <button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>
            ⬇ Export CSV
          </button>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Stock SKUs" value={rows.length} tone="primary" />
        <StatCard label="Units on hand" value={totalOnHand} />
        <StatCard label="Reserved" value={totalReserved} tone="warning" />
        <StatCard label="At / below par (≤2)" value={belowPar} tone={belowPar ? "error" : "success"} />
      </section>

      {notice && (
        <div role="status" style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.success-bg"], color: tokens["color.status.success"], fontSize: 12.5 }}>
          {notice}
        </div>
      )}
      {error && (
        <div role="alert" style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.error-bg"], color: tokens["color.status.error"], fontSize: 12.5 }}>
          {error}
        </div>
      )}

      {selected && (
        <Panel title={`Report stock — ${selected.listing} / ${selected.sku}`}>
          <form onSubmit={submit} style={{ padding: 16, display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
            <div>
              <label htmlFor="stock-onhand" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>On hand</label>
              <input id="stock-onhand" type="number" min={0} step="0.01" required value={onHand} onChange={(e) => setOnHand(e.target.value)} style={{ ...selectStyle, width: 130 }} />
            </div>
            <div>
              <label htmlFor="stock-reserved" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>Reserved</label>
              <input id="stock-reserved" type="number" min={0} step="0.01" required value={reserved} onChange={(e) => setReserved(e.target.value)} style={{ ...selectStyle, width: 130 }} />
            </div>
            <button type="submit" disabled={busy} style={{ ...primaryLinkStyle, border: "none", cursor: busy ? "wait" : "pointer", opacity: busy ? 0.7 : 1 }}>
              {busy ? "Reporting…" : "Report position"}
            </button>
            <button type="button" onClick={() => setSelected(null)} style={{ ...linkButtonStyle, cursor: "pointer" }}>
              Cancel
            </button>
          </form>
        </Panel>
      )}

      <div style={{ display: "flex", gap: 10, alignItems: "center", margin: "16px 0 12px" }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search listing or SKU…"
          aria-label="Search stock"
          style={{ ...selectStyle, flex: "1 1 260px", maxWidth: 380 }}
        />
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
          {filtered.length} of {rows.length} positions
        </span>
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Listing</th>
                <th style={thStyle}>SKU</th>
                <th style={{ ...thStyle, textAlign: "right" }}>On hand</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Reserved</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Available</th>
                <th style={thStyle}>Last updated</th>
                <th style={thStyle}>Source</th>
                <th style={thStyle}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r) => (
                <tr key={r.id}>
                  <td style={{ ...tdStyle, fontWeight: 500 }}>{r.listing}</td>
                  <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11.5 }}>{r.sku}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{r.qty_on_hand}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{r.qty_reserved}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums", color: r.qty_available <= 2 ? tokens["color.status.error"] : tokens["color.text.primary"], fontWeight: 600 }}>
                    {r.qty_available}
                  </td>
                  <td style={tdStyle}>{r.last_updated ? r.last_updated.slice(0, 16) : "—"}</td>
                  <td style={tdStyle}>{r.source}</td>
                  <td style={tdStyle}>
                    <button type="button" onClick={() => startEdit(r)} style={{ ...linkButtonStyle, padding: "4px 10px", cursor: "pointer" }}>
                      Report
                    </button>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 26 }}>
                    No stock positions yet. Positions appear once your listings are reported.
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
