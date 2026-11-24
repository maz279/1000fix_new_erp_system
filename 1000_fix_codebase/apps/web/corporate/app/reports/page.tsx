"use client";

/**
 * Spend & service reports — the account's six-month spend, request volume,
 * estate distribution and AR aging. Aggregation and BN-007 formatting happen
 * in Odoo; the page draws bars from the backend's numeric chart values and
 * displays the formatted strings.
 */
import { useEffect, useMemo, useState } from "react";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { RequireAuth } from "../../components/require-auth";
import {
  PageHeader,
  Panel,
  StatCard,
  downloadCsv,
  linkButtonStyle,
  pageStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface SpendRow {
  key: string;
  label: string;
  count: number;
  amount_bdt: string;
  amount: number;
}
interface StateRow {
  state: string;
  count: number;
}
interface SiteRow {
  site: string;
  count: number;
}
interface AgingRow {
  bucket: string;
  count: number;
  amount_bdt: string;
  amount: number;
}
interface Summary {
  spend: SpendRow[];
  orders_by_state: StateRow[];
  estate_by_site: SiteRow[];
  aging: AgingRow[];
  totals: {
    spend_bdt: string;
    outstanding_bdt: string;
    assets: number;
    open_requests: number;
    active_contracts: number;
  };
}

function Bar({ ratio, color }: { ratio: number; color: string }) {
  return (
    <div style={{ height: 8, background: tokens["color.surface.secondary"], borderRadius: 4, overflow: "hidden" }}>
      <div
        style={{
          width: `${Math.max(2, Math.min(100, Math.round(ratio * 100)))}%`,
          height: "100%",
          background: color,
          borderRadius: 4,
        }}
      />
    </div>
  );
}

function ReportsContent() {
  const { locale } = useLanguage();
  const bn = locale === "bn";
  const [data, setData] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    callOdoo<Summary>("/corporate/reports/summary")
      .then((d) => {
        if (!active) return;
        setData(d);
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

  const maxima = useMemo(
    () => ({
      spend: Math.max(1, ...(data?.spend.map((s) => s.amount) ?? [1])),
      orders: Math.max(1, ...(data?.orders_by_state.map((s) => s.count) ?? [1])),
      site: Math.max(1, ...(data?.estate_by_site.map((s) => s.count) ?? [1])),
    }),
    [data]
  );

  if (loading) return <Loading label={bn ? "রিপোর্ট তৈরি হচ্ছে…" : "Building reports…"} />;
  if (error || !data) return <LoadError what={bn ? "রিপোর্ট" : "Reports"} message={error || "No data"} />;

  const exportSpend = () =>
    downloadCsv(
      `1000fix-spend-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Month", "Invoices", "Spend (BDT)"],
      data.spend.map((s) => [s.label, String(s.count), s.amount_bdt])
    );

  return (
    <main style={pageStyle}>
      <PageHeader
        title={bn ? "ব্যয় ও সার্ভিস রিপোর্ট" : "Spend & service reports"}
        subtitle={
          bn
            ? "গত ছয় মাসের ব্যয়, অনুরোধের পরিমাণ, সাইট বণ্টন এবং প্রাপ্য হিসাবের এজিং — সব ব্যাকএন্ডে গণনা করা।"
            : "Six-month spend, request volume, site distribution and receivables aging — aggregated in the backend."
        }
        actions={
          <button type="button" onClick={exportSpend} style={{ ...linkButtonStyle, cursor: "pointer" }}>
            ⬇ {bn ? "ব্যয় CSV" : "Spend CSV"}
          </button>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label={bn ? "মোট ব্যয় (৬ মাস)" : "Spend (6 months)"} value={`৳ ${data.totals.spend_bdt}`} tone="primary" />
        <StatCard label={bn ? "বাকি" : "Outstanding"} value={`৳ ${data.totals.outstanding_bdt}`} tone="warning" />
        <StatCard label={bn ? "ডিভাইস" : "Assets"} value={data.totals.assets} />
        <StatCard label={bn ? "খোলা অনুরোধ" : "Open requests"} value={data.totals.open_requests} tone="warning" />
        <StatCard label={bn ? "সক্রিয় চুক্তি" : "Active contracts"} value={data.totals.active_contracts} tone="success" />
      </section>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))", gap: 16 }}>
        <Panel title={bn ? "মাসিক ব্যয়" : "Monthly spend"}>
          <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
            {data.spend.map((s) => (
              <div key={s.key}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                  <span>{s.label} <span style={{ color: tokens["color.text.secondary"] }}>({s.count})</span></span>
                  <b style={{ fontVariantNumeric: "tabular-nums" }}>৳ {s.amount_bdt}</b>
                </div>
                <Bar ratio={s.amount / maxima.spend} color={tokens["color.primary.base"]} />
              </div>
            ))}
          </div>
        </Panel>

        <Panel title={bn ? "অনুরোধের অবস্থা" : "Requests by state"}>
          <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            {data.orders_by_state.map((s) => (
              <div key={s.state}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                  <span style={{ textTransform: "capitalize" }}>{s.state.replace(/_/g, " ")}</span>
                  <b>{s.count}</b>
                </div>
                <Bar ratio={s.count / maxima.orders} color={tokens["color.status.info"]} />
              </div>
            ))}
            {data.orders_by_state.length === 0 && (
              <p style={{ margin: 0, fontSize: 12, color: tokens["color.text.secondary"] }}>
                {bn ? "কোনো সার্ভিস অনুরোধ নেই।" : "No service requests yet."}
              </p>
            )}
          </div>
        </Panel>

        <Panel title={bn ? "সাইট অনুযায়ী ডিভাইস" : "Estate by site"}>
          <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            {data.estate_by_site.map((s) => (
              <div key={s.site}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                  <span>{s.site}</span>
                  <b>{s.count}</b>
                </div>
                <Bar ratio={s.count / maxima.site} color={tokens["color.status.success"]} />
              </div>
            ))}
            {data.estate_by_site.length === 0 && (
              <p style={{ margin: 0, fontSize: 12, color: tokens["color.text.secondary"] }}>
                {bn ? "কোনো ডিভাইস নেই।" : "No devices registered."}
              </p>
            )}
          </div>
        </Panel>

        <Panel title={bn ? "প্রাপ্য এজিং" : "Receivables aging"}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>{bn ? "বাকেট" : "Bucket"}</th>
                <th style={{ ...thStyle, textAlign: "right" }}>{bn ? "ইনভয়েস" : "Invoices"}</th>
                <th style={{ ...thStyle, textAlign: "right" }}>{bn ? "বাকি" : "Outstanding"}</th>
              </tr>
            </thead>
            <tbody>
              {data.aging.map((a) => (
                <tr key={a.bucket}>
                  <td style={tdStyle}>{a.bucket}</td>
                  <td style={{ ...tdStyle, textAlign: "right" }}>{a.count}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {a.amount_bdt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      </div>
    </main>
  );
}

export default function ReportsPage() {
  return (
    <RequireAuth>
      <ReportsContent />
    </RequireAuth>
  );
}
