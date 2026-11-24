"use client";

/**
 * Payouts & statements — the commission ledger with gross, commission, §52
 * TDS and net per line, plus paid/pending totals. All money is
 * backend-computed BN-007 text (AS-10); the portal renders and exports only.
 *
 * Certified monthly statements and downloadable §52 certificates have no
 * backend service yet, so they are stated as unavailable rather than faked.
 */
import { useEffect, useMemo, useState } from "react";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
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

interface SettlementLine {
  ref: string;
  source_ref: string;
  date: string;
  gross_bdt: string;
  commission_bdt: string;
  tds_bdt: string;
  net_bdt: string;
  state: string;
}

interface Totals {
  gross_bdt?: string;
  commission_bdt?: string;
  tds_bdt?: string;
  net_bdt?: string;
  paid_bdt?: string;
  pending_bdt?: string;
  lines?: number;
}

export default function SellerStatementsPage() {
  const [lines, setLines] = useState<SettlementLine[]>([]);
  const [totals, setTotals] = useState<Totals>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");

  useEffect(() => {
    callOdoo<{
      settlements?: { lines: SettlementLine[]; totals?: Totals };
      error?: { message: string };
    }>("/seller/settlements", { include_totals: 1 })
      .then((d) => {
        if (d.error) setError(d.error.message);
        else {
          setLines(d.settlements?.lines ?? []);
          setTotals(d.settlements?.totals ?? {});
        }
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  const filtered = useMemo(
    () =>
      lines.filter((r) => {
        const q = query.trim().toLowerCase();
        const matchesQuery =
          !q ||
          r.ref.toLowerCase().includes(q) ||
          (r.source_ref || "").toLowerCase().includes(q);
        const matchesState = filter === "all" || r.state === filter;
        return matchesQuery && matchesState;
      }),
    [lines, query, filter]
  );

  const exportCsv = () =>
    downloadCsv(
      `1000fix-seller-statement-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Ledger ref", "Date", "Source", "Gross (BDT)", "Commission (BDT)", "TDS §52 (BDT)", "Net (BDT)", "Payout state"],
      lines.map((r) => [
        r.ref,
        r.date,
        r.source_ref,
        r.gross_bdt,
        r.commission_bdt,
        r.tds_bdt,
        r.net_bdt,
        r.state,
      ])
    );

  if (loading) return <Loading label="Loading your settlement lines…" />;
  if (error) return <LoadError what="settlement statement" message={error} />;

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Payouts & statements"
        subtitle="Commission-ledger lines with gross, commission, §52 TDS and net, plus the paid and pending payout position."
        actions={
          <button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>
            ⬇ Statement CSV
          </button>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Gross" value={`৳ ${totals.gross_bdt ?? "0.00"}`} tone="primary" />
        <StatCard label="Commission" value={`৳ ${totals.commission_bdt ?? "0.00"}`} tone="warning" />
        <StatCard label="TDS withheld (§52)" value={`৳ ${totals.tds_bdt ?? "0.00"}`} tone="warning" />
        <StatCard label="Net earnings" value={`৳ ${totals.net_bdt ?? "0.00"}`} tone="success" />
        <StatCard label="Paid" value={`৳ ${totals.paid_bdt ?? "0.00"}`} tone="success" />
        <StatCard label="Pending payout" value={`৳ ${totals.pending_bdt ?? "0.00"}`} note="earned + accrued" tone="warning" />
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
        Certified monthly statements, VDS figures and downloadable NBR §52 withholding certificates
        are not yet available — there is no backend service for them. The lines below are the live
        commission-ledger entries.
      </p>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", marginBottom: 12 }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search ledger ref or source…"
          aria-label="Search statement lines"
          style={{ ...selectStyle, flex: "1 1 260px", maxWidth: 380 }}
        />
        <select value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Payout state" style={selectStyle}>
          <option value="all">All states</option>
          <option value="earned">Earned</option>
          <option value="accrued">Accrued</option>
          <option value="paid">Paid</option>
          <option value="forfeited">Forfeited</option>
          <option value="void">Void</option>
        </select>
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
          {filtered.length} of {lines.length} lines
        </span>
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Date</th>
                <th style={thStyle}>Ledger ref</th>
                <th style={thStyle}>Source</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Gross</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Commission</th>
                <th style={{ ...thStyle, textAlign: "right" }}>TDS §52</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Net</th>
                <th style={thStyle}>Payout</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r) => (
                <tr key={r.ref}>
                  <td style={tdStyle}>{r.date ? r.date.slice(0, 10) : "—"}</td>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{r.ref}</td>
                  <td style={tdStyle}>{r.source_ref || "—"}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {r.gross_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {r.commission_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {r.tds_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>৳ {r.net_bdt}</td>
                  <td style={tdStyle}><StateBadge state={r.state} /></td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 26 }}>
                    No settlement lines in this filter.
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
