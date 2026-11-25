"use client";

/**
 * Corporate overview — the signed-in client's operating picture.
 *
 * Live data only (no fixtures): estate, contracts/SLA, invoices/aging and
 * service requests, all fenced to the session's commercial partner by the
 * backend. Mounted behind RequireAuth.
 */
import { useEffect, useState } from "react";
import Link from "next/link";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { useAuth } from "../../components/auth-modal";
import { RequireAuth } from "../../components/require-auth";
import {
  PageHeader,
  Panel,
  StatePill,
  StatCard,
  linkButtonStyle,
  primaryLinkStyle,
  pageStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Device {
  id: number;
  warranty_status: string;
}

interface Invoice {
  id: number;
  invoice_no: string;
  invoice_date: string;
  date_due: string;
  state: string;
  balance_bdt: string;
  net_bdt: string;
  days_overdue: number;
}

interface ServiceOrder {
  id: number;
  name: string;
  state: string;
  device: string;
  site: string;
  priority: string;
  service_type: string;
  opened_at: string;
}

interface ContractSummary {
  active: number;
  expiring_90: number;
  annual_value_bdt: string;
}

function DashboardContent() {
  const { locale } = useLanguage();
  const { user } = useAuth();
  const bn = locale === "bn";

  const [devices, setDevices] = useState<Device[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [invoiceTotals, setInvoiceTotals] = useState({
    outstanding_bdt: "0.00",
    overdue_bdt: "0.00",
    overdue_count: 0,
    count: 0,
  });
  const [orders, setOrders] = useState<ServiceOrder[]>([]);
  const [contracts, setContracts] = useState<ContractSummary>({
    active: 0,
    expiring_90: 0,
    annual_value_bdt: "0.00",
  });
  const [tenderCount, setTenderCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([
      callOdoo<{ devices: Device[]; total: number }>("/corporate/estate"),
      callOdoo<{
        invoices: Invoice[];
        total: number;
        totals: { outstanding_bdt: string; overdue_bdt: string; overdue_count: number; count: number };
      }>("/corporate/invoices/consolidated"),
      callOdoo<{ orders: ServiceOrder[]; total: number }>("/corporate/service-requests"),
      callOdoo<{ summary: ContractSummary }>("/corporate/contracts"),
      callOdoo<{ total: number }>("/corporate/tenders"),
    ])
      .then(([estate, inv, req, contractRes, tenderRes]) => {
        if (!active) return;
        setDevices(estate.devices || []);
        setInvoices(inv.invoices || []);
        setInvoiceTotals({
          outstanding_bdt: inv.totals?.outstanding_bdt ?? "0.00",
          overdue_bdt: inv.totals?.overdue_bdt ?? "0.00",
          overdue_count: inv.totals?.overdue_count ?? 0,
          count: inv.totals?.count ?? 0,
        });
        setOrders(req.orders || []);
        setContracts(
          contractRes.summary || { active: 0, expiring_90: 0, annual_value_bdt: "0.00" }
        );
        setTenderCount(tenderRes.total || 0);
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

  if (loading) return <Loading label={bn ? "ওভারভিউ লোড হচ্ছে…" : "Loading your overview…"} />;
  if (error) return <LoadError what={bn ? "ডেটা" : "Portal data"} message={error} />;

  const inWarranty = devices.filter((d) =>
    ["in_warranty", "extended"].includes(d.warranty_status)
  ).length;
  const openOrders = orders.filter(
    (o) => !["delivered", "closed", "cancelled"].includes(o.state)
  ).length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title={bn ? "কর্পোরেট সার্ভিস ওভারভিউ" : "Corporate service overview"}
        subtitle={
          user?.name
            ? bn
              ? `${user.name} — আপনার অ্যাকাউন্টের ডিভাইস, চুক্তি, বিলিং ও সার্ভিস অনুরোধের সারসংক্ষেপ।`
              : `${user.name} — your account's estate, contracts, billing and service requests at a glance.`
            : undefined
        }
        actions={
          <>
            <Link href="/service-requests" style={{ ...primaryLinkStyle, textDecoration: "none" }}>
              + {bn ? "সার্ভিস রিকোয়েস্ট" : "Service request"}
            </Link>
            <Link href="/estate" style={{ ...linkButtonStyle, textDecoration: "none" }}>
              {bn ? "ডিভাইস বহর" : "Fleet estate"}
            </Link>
          </>
        }
      />

      <section aria-label={bn ? "মূল সূচক" : "Key indicators"} style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
        <StatCard label={bn ? "ডিভাইস" : "Fleet assets"} value={devices.length} note={bn ? "নিবন্ধিত" : "Registered"} tone="primary" />
        <StatCard label={bn ? "সক্রিয় ওয়ারেন্টি" : "Active warranties"} value={inWarranty} note={bn ? "ইন/এক্সটেন্ডেড" : "In / extended"} tone="success" />
        <StatCard label={bn ? "খোলা অনুরোধ" : "Open requests"} value={openOrders} note={bn ? "সার্ভিস চলমান" : "In the service workflow"} tone="warning" />
        <StatCard label={bn ? "বাকি ব্যালেন্স" : "Outstanding balance"} value={`৳ ${invoiceTotals.outstanding_bdt}`} note={`${invoiceTotals.count} ${bn ? "ইনভয়েস" : "invoices"}`} tone="warning" />
        <StatCard label={bn ? "মেয়াদোত্তীর্ণ" : "Overdue"} value={`৳ ${invoiceTotals.overdue_bdt}`} note={`${invoiceTotals.overdue_count} ${bn ? "ইনভয়েস" : "invoices"}`} tone={invoiceTotals.overdue_count ? "error" : "neutral"} />
        <StatCard label={bn ? "সক্রিয় চুক্তি" : "Active contracts"} value={contracts.active} note={bn ? `বার্ষিক ৳ ${contracts.annual_value_bdt}` : `৳ ${contracts.annual_value_bdt} / year`} tone="primary" />
      </section>

      <section
        style={{
          marginTop: 16,
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 10,
        }}
        aria-label={bn ? "দ্রুত লিংক" : "Quick links"}
      >
        {[
          { href: "/contracts", en: "Contracts & SLA", bn: "চুক্তি ও এসএলএ", note: `${contracts.expiring_90} ${bn ? "৯০ দিনে শেষ" : "expiring ≤90d"}` },
          { href: "/invoices", en: "Invoices & statements", bn: "ইনভয়েস ও স্টেটমেন্ট", note: bn ? "এজিং ও সিএসভি" : "Aging & CSV statement" },
          { href: "/tenders", en: "Tenders & quotes", bn: "টেন্ডার ও কোটেশন", note: `${tenderCount} ${bn ? "রেকর্ড" : "records"}` },
          { href: "/reports", en: "Spend & reports", bn: "ব্যয় ও রিপোর্ট", note: bn ? "৬ মাসের ব্যয়" : "6-month spend" },
          { href: "/account", en: "Account", bn: "অ্যাকাউন্ট", note: bn ? "কোম্পানি ও যোগাযোগ" : "Company & contacts" },
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
            <strong>{bn ? q.bn : q.en}</strong>
            <span style={{ color: tokens["color.text.secondary"], fontSize: 11 }}>{q.note}</span>
          </Link>
        ))}
      </section>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(460px, 1fr))", gap: 16, marginTop: 18 }}>
        <Panel
          title={bn ? "সাম্প্রতিক সার্ভিস অনুরোধ" : "Recent service requests"}
          actions={<Link href="/service-requests" style={{ fontSize: 12, color: tokens["color.primary.base"], textDecoration: "none", fontWeight: 600 }}>{bn ? "সব দেখুন" : "View all"}</Link>}
        >
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>{bn ? "রেফারেন্স" : "Reference"}</th>
                <th style={thStyle}>{bn ? "ডিভাইস / সাইট" : "Device / site"}</th>
                <th style={thStyle}>{bn ? "প্রায়োরিটি" : "Priority"}</th>
                <th style={thStyle}>{bn ? "অবস্থা" : "Status"}</th>
              </tr>
            </thead>
            <tbody>
              {orders.slice(0, 5).map((o) => (
                <tr key={o.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{o.name}</td>
                  <td style={tdStyle}>{o.device || "—"}{o.site ? ` · ${o.site}` : ""}</td>
                  <td style={tdStyle}><StatePill state={o.priority} /></td>
                  <td style={tdStyle}><StatePill state={o.state} /></td>
                </tr>
              ))}
              {orders.length === 0 && (
                <tr><td colSpan={4} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"] }}>{bn ? "কোনো অনুরোধ নেই।" : "No service requests yet."}</td></tr>
              )}
            </tbody>
          </table>
        </Panel>

        <Panel
          title={bn ? "সাম্প্রতিক ইনভয়েস" : "Recent invoices"}
          actions={<Link href="/invoices" style={{ fontSize: 12, color: tokens["color.primary.base"], textDecoration: "none", fontWeight: 600 }}>{bn ? "সব দেখুন" : "View all"}</Link>}
        >
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>{bn ? "ইনভয়েস" : "Invoice"}</th>
                <th style={thStyle}>{bn ? "তারিখ" : "Date"}</th>
                <th style={{ ...thStyle, textAlign: "right" }}>{bn ? "বাকি" : "Balance"}</th>
                <th style={thStyle}>{bn ? "অবস্থা" : "Status"}</th>
              </tr>
            </thead>
            <tbody>
              {invoices.slice(0, 5).map((inv) => (
                <tr key={inv.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{inv.invoice_no}</td>
                  <td style={tdStyle}>{inv.invoice_date}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {inv.balance_bdt}</td>
                  <td style={tdStyle}><StatePill state={inv.state} /></td>
                </tr>
              ))}
              {invoices.length === 0 && (
                <tr><td colSpan={4} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"] }}>{bn ? "কোনো ইনভয়েস নেই।" : "No issued invoices yet."}</td></tr>
              )}
            </tbody>
          </table>
        </Panel>
      </div>
    </main>
  );
}

export default function CorporateDashboardPage() {
  return (
    <RequireAuth>
      <DashboardContent />
    </RequireAuth>
  );
}
