"use client";

/**
 * Consolidated invoices & account statement.
 *
 * Backend-filtered to customer-facing documents (issued/paid/credited) and
 * partner-fenced. Every amount is a BN-007-formatted string from the server;
 * the page renders, filters and exports — it never re-computes money.
 */
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { RequireAuth } from "../../components/require-auth";
import {
  PageHeader,
  Panel,
  StatePill,
  StatCard,
  downloadCsv,
  linkButtonStyle,
  pageStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Invoice {
  id: number;
  invoice_no: string;
  customer: string;
  invoice_date: string;
  date_due: string;
  state: string;
  gross_bdt: string;
  vat_bdt: string;
  net_bdt: string;
  paid_bdt: string;
  balance_bdt: string;
  days_overdue: number;
  aging: string;
}

interface Totals {
  outstanding_bdt: string;
  overdue_bdt: string;
  paid_bdt: string;
  count: number;
  overdue_count: number;
}

interface AgingRow {
  bucket: string;
  count: number;
  amount_bdt: string;
}

const EMPTY_TOTALS: Totals = {
  outstanding_bdt: "0.00",
  overdue_bdt: "0.00",
  paid_bdt: "0.00",
  count: 0,
  overdue_count: 0,
};

function InvoicesContent() {
  const { locale } = useLanguage();
  const bn = locale === "bn";
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [totals, setTotals] = useState<Totals>(EMPTY_TOTALS);
  const [aging, setAging] = useState<AgingRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");

  useEffect(() => {
    let active = true;
    callOdoo<{ invoices: Invoice[]; totals: Totals; aging: AgingRow[] }>(
      "/corporate/invoices/consolidated"
    )
      .then((d) => {
        if (!active) return;
        setInvoices(d.invoices || []);
        setTotals(d.totals || EMPTY_TOTALS);
        setAging(d.aging || []);
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

  const filtered = useMemo(
    () =>
      invoices.filter((inv) => {
        const q = query.trim().toLowerCase();
        const matchesQuery = !q || inv.invoice_no.toLowerCase().includes(q);
        const matchesFilter =
          filter === "all" ||
          (filter === "overdue" && inv.days_overdue > 0) ||
          inv.state === filter;
        return matchesQuery && matchesFilter;
      }),
    [invoices, query, filter]
  );

  const exportStatement = () => {
    downloadCsv(
      `1000fix-statement-${new Date().toISOString().slice(0, 10)}.csv`,
      [
        "Invoice",
        "Invoice date",
        "Due date",
        "State",
        "Total (BDT)",
        "Paid (BDT)",
        "Balance (BDT)",
        "Days overdue",
        "Aging",
      ],
      invoices.map((i) => [
        i.invoice_no,
        i.invoice_date,
        i.date_due,
        i.state,
        i.net_bdt,
        i.paid_bdt,
        i.balance_bdt,
        String(i.days_overdue),
        i.aging,
      ])
    );
  };

  if (loading) return <Loading label={bn ? "ইনভয়েস লোড হচ্ছে…" : "Loading invoices…"} />;
  if (error) return <LoadError what={bn ? "ইনভয়েস" : "Invoices"} message={error} />;

  return (
    <main style={pageStyle}>
      <PageHeader
        title={bn ? "ইনভয়েস ও স্টেটমেন্ট" : "Invoices & statements"}
        subtitle={
          bn
            ? "কনসোলিডেটেড বি২বি বিলিং, বাকি ব্যালেন্স, এজিং এবং সিএসভি স্টেটমেন্ট — ইস্যু করা, পরিশোধিত ও ক্রেডিট করা ডকুমেন্ট।"
            : "Consolidated B2B billing, outstanding balance, aging and a CSV statement — issued, paid and credited documents only."
        }
        actions={
          <>
            <button type="button" onClick={exportStatement} style={{ ...linkButtonStyle, cursor: "pointer" }}>
              ⬇ {bn ? "স্টেটমেন্ট CSV" : "Statement CSV"}
            </button>
            <Link href="/contracts" style={{ ...linkButtonStyle, textDecoration: "none" }}>
              {bn ? "চুক্তি" : "Contracts"}
            </Link>
          </>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label={bn ? "বাকি" : "Outstanding"} value={`৳ ${totals.outstanding_bdt}`} note={`${totals.count} ${bn ? "ইনভয়েস" : "invoices"}`} tone="warning" />
        <StatCard label={bn ? "মেয়াদোত্তীর্ণ" : "Overdue"} value={`৳ ${totals.overdue_bdt}`} note={`${totals.overdue_count} ${bn ? "ইনভয়েস" : "invoices"}`} tone={totals.overdue_count ? "error" : "neutral"} />
        <StatCard label={bn ? "পরিশোধিত" : "Paid"} value={`৳ ${totals.paid_bdt}`} tone="success" />
      </section>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 10, marginBottom: 16 }}>
        {aging.map((a) => (
          <div
            key={a.bucket}
            style={{
              padding: "10px 12px",
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-sm"],
            }}
          >
            <div style={{ fontSize: 11, color: tokens["color.text.secondary"], textTransform: "uppercase", letterSpacing: "0.04em" }}>
              {a.bucket}
            </div>
            <div style={{ fontSize: 14, fontWeight: 700, color: tokens["color.text.primary"], fontVariantNumeric: "tabular-nums" }}>৳ {a.amount_bdt}</div>
            <div style={{ fontSize: 10.5, color: tokens["color.text.secondary"] }}>{a.count} {bn ? "ইনভয়েস" : "invoices"}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", marginBottom: 12 }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={bn ? "ইনভয়েস নম্বর খুঁজুন…" : "Search invoice no.…"}
          style={{
            flex: "1 1 260px",
            maxWidth: 380,
            padding: "8px 12px",
            border: `1px solid ${tokens["color.border.default"]}`,
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.surface.primary"],
            color: tokens["color.text.primary"],
            fontSize: tokens["typography.size.200"],
          }}
        />
        {[
          { key: "all", en: "All", bn: "সব" },
          { key: "issued", en: "Issued", bn: "ইস্যু" },
          { key: "overdue", en: "Overdue", bn: "মেয়াদোত্তীর্ণ" },
          { key: "paid", en: "Paid", bn: "পরিশোধিত" },
        ].map((f) => (
          <button
            key={f.key}
            type="button"
            aria-pressed={filter === f.key}
            onClick={() => setFilter(f.key)}
            style={{
              padding: "6px 12px",
              fontSize: tokens["typography.size.200"],
              borderRadius: tokens["dimension.border.radius-sm"],
              border: `1px solid ${filter === f.key ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
              background: filter === f.key ? tokens["color.primary.base"] : tokens["color.surface.primary"],
              color: filter === f.key ? tokens["color.text.inverse"] : tokens["color.text.secondary"],
              cursor: "pointer",
            }}
          >
            {bn ? f.bn : f.en}
          </button>
        ))}
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>{bn ? "ইনভয়েস" : "Invoice"}</th>
                <th style={thStyle}>{bn ? "তারিখ" : "Date"}</th>
                <th style={thStyle}>{bn ? "ডিউ" : "Due"}</th>
                <th style={{ ...thStyle, textAlign: "right" }}>{bn ? "মোট" : "Total"}</th>
                <th style={{ ...thStyle, textAlign: "right" }}>{bn ? "পরিশোধিত" : "Paid"}</th>
                <th style={{ ...thStyle, textAlign: "right" }}>{bn ? "বাকি" : "Balance"}</th>
                <th style={thStyle}>{bn ? "বিলম্ব" : "Overdue"}</th>
                <th style={thStyle}>{bn ? "অবস্থা" : "Status"}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((inv) => (
                <tr key={inv.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{inv.invoice_no}</td>
                  <td style={tdStyle}>{inv.invoice_date}</td>
                  <td style={tdStyle}>{inv.date_due || "—"}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {inv.net_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {inv.paid_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>৳ {inv.balance_bdt}</td>
                  <td style={tdStyle}>{inv.days_overdue > 0 ? `${inv.days_overdue} ${bn ? "দিন" : "days"}` : "—"}</td>
                  <td style={tdStyle}><StatePill state={inv.state} /></td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 28 }}>
                    {bn ? "এই ফিল্টারে কোনো ইনভয়েস নেই।" : "No invoices in this filter."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <p style={{ marginTop: 12, fontSize: 11.5, color: tokens["color.text.secondary"] }}>
        {bn
          ? "পেমেন্ট: যেকোনো 1000 FiX সেন্টারে নগদ/কার্ড/মোবাইল ব্যাংকিং, অথবা আপনার চুক্তির পেমেন্ট টার্ম অনুযায়ী ব্যাংক ট্রান্সফার। প্রশ্নে ১৬৭৪৩।"
          : "Payment: cash/card/mobile banking at any 1000 FiX centre, or bank transfer per your contract payment terms. Questions: 16743."}
      </p>
    </main>
  );
}

export default function InvoicesPage() {
  return (
    <RequireAuth>
      <InvoicesContent />
    </RequireAuth>
  );
}
