"use client";

/**
 * Seller dashboard — standing, KYC state and the operating picture:
 * open jobs, my quotes, stock, payouts and disputes. Everything is scoped to
 * the signed-in seller by the backend (EA-05).
 */
import { useEffect, useState } from "react";
import Link from "next/link";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  Badge,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  linkButtonStyle,
  pageStyle,
  primaryLinkStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Seller {
  id: number;
  name: string;
  kyc_status: string;
  kyc_ref: string;
  rating: number;
  total_jobs: number;
}

interface Job {
  id: number;
  name: string;
  description: string;
  budget_bdt: string;
  state: string;
  my_quote: { id: number; price_bdt: string; eta_days: number; state: string } | null;
}

interface Quote {
  id: number;
  order_name: string;
  price_bdt: string;
  eta_days: number;
  state: string;
}

interface SettlementTotals {
  net_bdt?: string;
  paid_bdt?: string;
  pending_bdt?: string;
  gross_bdt?: string;
  commission_bdt?: string;
  tds_bdt?: string;
  lines?: number;
}

interface Dispute {
  id: string;
  state: string;
  sla_breached: boolean;
}

interface StockRow {
  id: number;
  sku: string;
  qty_on_hand: number;
  qty_reserved: number;
  qty_available: number;
}

export default function SellerDashboard() {
  const [seller, setSeller] = useState<Seller | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [totals, setTotals] = useState<SettlementTotals>({});
  const [disputes, setDisputes] = useState<Dispute[]>([]);
  const [stock, setStock] = useState<StockRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([
      callOdoo<{ seller?: Seller; error?: { message: string } }>("/seller/dashboard"),
      callOdoo<{ orders?: Job[] }>("/seller/orders").catch(() => ({ orders: [] })),
      callOdoo<{ quotes?: Quote[] }>("/seller/quotes").catch(() => ({ quotes: [] })),
      callOdoo<{ settlements?: { totals?: SettlementTotals } }>("/seller/settlements", {
        include_totals: 1,
      }).catch(
        () => ({ settlements: { totals: {} as SettlementTotals } })
      ),
      callOdoo<{ disputes?: Dispute[] }>("/seller/disputes").catch(() => ({ disputes: [] })),
      callOdoo<{ stock?: StockRow[] }>("/seller/stock").catch(() => ({ stock: [] })),
    ])
      .then(([d, o, q, s, dp, st]) => {
        if (!active) return;
        if (d.error || !d.seller) {
          setError(d.error?.message ?? "No seller profile for this account.");
        } else {
          setSeller(d.seller);
        }
        setJobs(o.orders ?? []);
        setQuotes(q.quotes ?? []);
        setTotals(s.settlements?.totals ?? {});
        setDisputes(dp.disputes ?? []);
        setStock(st.stock ?? []);
        setLoading(false);
      })
      .catch((e: Error) => {
        if (!active) return;
        setError(e.message);
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  if (loading) return <Loading label="Loading your seller dashboard…" />;
  if (error && !seller) return <LoadError what="seller profile" message={error} />;
  if (!seller) return <LoadError what="seller profile" message="No seller profile for this account." />;

  const openJobs = jobs.length;
  const submitted = quotes.filter((q) => q.state === "submitted").length;
  const selected = quotes.filter((q) => q.state === "selected").length;
  const openDisputes = disputes.filter((d) => ["raised", "investigating", "arbitration", "escalated"].includes(d.state)).length;
  const breached = disputes.filter((d) => d.sla_breached).length;
  const stockSkus = stock.length;
  const belowPar = stock.filter((s) => s.qty_available <= 2).length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title={seller.name}
        subtitle="Marketplace seller home — onboarding, standing and headline numbers (M12)."
        actions={
          <>
            <Link href="/jobs" style={{ ...primaryLinkStyle, textDecoration: "none" }}>
              Browse open jobs
            </Link>
            <Link href="/stock" style={{ ...linkButtonStyle, textDecoration: "none" }}>
              Stock &amp; listings
            </Link>
          </>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="KYC" value={seller.kyc_status} note={seller.kyc_ref || "reference pending"} tone={seller.kyc_status === "verified" ? "success" : "warning"} />
        <StatCard label="Rating" value={`${seller.rating.toFixed(1)} / 5`} note="customer reviews" tone="primary" />
        <StatCard label="Total jobs" value={seller.total_jobs} note="completed / awarded" />
        <StatCard label="Open jobs" value={openJobs} note="quotable now" tone="warning" />
        <StatCard label="Submitted quotes" value={submitted} note={`${selected} selected`} tone="primary" />
        <StatCard label="Net paid" value={`৳ ${totals.paid_bdt ?? "0.00"}`} note={`${totals.lines ?? 0} ledger lines`} tone="success" />
        <StatCard label="Pending payout" value={`৳ ${totals.pending_bdt ?? "0.00"}`} note="earned + accrued" tone="warning" />
        <StatCard label="Open disputes" value={openDisputes} note={breached ? `${breached} SLA breached` : "within 48h SLA"} tone={breached ? "error" : "neutral"} />
        <StatCard label="Stock SKUs" value={stockSkus} note={belowPar ? `${belowPar} at/below par` : "positions reported"} tone={belowPar ? "warning" : "success"} />
      </section>

      {seller.kyc_status !== "verified" && (
        <div
          role="status"
          style={{
            marginBottom: 16,
            padding: "10px 14px",
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.status.warning-bg"],
            color: tokens["color.status.warning"],
            border: `1px solid ${tokens["color.status.warning"]}`,
            fontSize: 12.5,
          }}
        >
          KYC {seller.kyc_status} — quoting opens once 1000 FiX compliance verifies your documents
          (server-enforced; reference {seller.kyc_ref || "pending"}).
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 10, marginBottom: 18 }}>
        {[
          { href: "/onboarding", en: "Onboarding & KYC", bn: "অনবোর্ডিং", note: seller.kyc_status },
          { href: "/quotes", en: "My quotes", bn: "আমার কোটেশন", note: `${quotes.length} total` },
          { href: "/statements", en: "Payouts & statements", bn: "পেমেন্ট", note: `net ৳ ${totals.net_bdt ?? "0.00"}` },
          { href: "/scorecard", en: "Scorecard", bn: "স্কোরকার্ড", note: "performance by period" },
          { href: "/disputes", en: "Disputes", bn: "বিরোধ", note: `${disputes.length} total` },
        ].map((q) => (
          <Link
            key={q.href}
            href={q.href}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: 8,
              padding: "12px 14px",
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              color: tokens["color.text.primary"],
              textDecoration: "none",
              fontSize: 12.5,
            }}
          >
            <strong>{q.en}</strong>
            <span style={{ color: tokens["color.text.secondary"], fontSize: 11 }}>{q.note}</span>
          </Link>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))", gap: 16 }}>
        <Panel
          title="Open jobs"
          actions={<Link href="/jobs" style={{ fontSize: 12, color: tokens["color.primary.base"], textDecoration: "none", fontWeight: 600 }}>View all</Link>}
        >
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Job</th>
                <th style={thStyle}>Budget</th>
                <th style={thStyle}>My quote</th>
              </tr>
            </thead>
            <tbody>
              {jobs.slice(0, 5).map((j) => (
                <tr key={j.id}>
                  <td style={tdStyle}>
                    <div style={{ fontWeight: 600 }}>{j.name}</div>
                    <div style={{ fontSize: 11, color: tokens["color.text.secondary"] }}>{j.description}</div>
                  </td>
                  <td style={tdStyle}>৳ {j.budget_bdt}</td>
                  <td style={tdStyle}>
                    {j.my_quote ? (
                      <span style={{ fontSize: 11.5 }}>৳ {j.my_quote.price_bdt} · <StateBadge state={j.my_quote.state} /></span>
                    ) : (
                      <Badge tone="neutral">Not quoted</Badge>
                    )}
                  </td>
                </tr>
              ))}
              {jobs.length === 0 && (
                <tr><td colSpan={3} style={{ ...tdStyle, color: tokens["color.text.secondary"] }}>No open jobs right now.</td></tr>
              )}
            </tbody>
          </table>
        </Panel>

        <Panel
          title="Recent quotes"
          actions={<Link href="/quotes" style={{ fontSize: 12, color: tokens["color.primary.base"], textDecoration: "none", fontWeight: 600 }}>View all</Link>}
        >
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Order</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Quoted</th>
                <th style={thStyle}>Status</th>
              </tr>
            </thead>
            <tbody>
              {quotes.slice(0, 5).map((q) => (
                <tr key={q.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{q.order_name || `Quote #${q.id}`}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {q.price_bdt}</td>
                  <td style={tdStyle}><StateBadge state={q.state} /></td>
                </tr>
              ))}
              {quotes.length === 0 && (
                <tr><td colSpan={3} style={{ ...tdStyle, color: tokens["color.text.secondary"] }}>No quotes submitted yet.</td></tr>
              )}
            </tbody>
          </table>
        </Panel>
      </div>
    </main>
  );
}
