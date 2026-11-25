"use client";

/**
 * Contracts & SLA — the corporate client's active agreements, coverage,
 * renewal horizon and service targets (M08 read; partner-scoped backend).
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
  linkButtonStyle,
  pageStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Sla {
  code: string;
  name: string;
  response_hours: number | null;
  resolution_hours: number | null;
}

interface Contract {
  id: number;
  code: string;
  name: string;
  family: string;
  date_start: string;
  date_end: string;
  state: string;
  annual_value_bdt: string;
  billing_frequency: string;
  covered_count: number;
  days_to_expiry: number | null;
  slas: Sla[];
}

const FAMILY: Record<string, { en: string; bn: string }> = {
  amc: { en: "AMC", bn: "এএমসি" },
  ramc: { en: "RAMC", bn: "র‍্যামক" },
  managed: { en: "Managed services", bn: "ম্যানেজড সার্ভিস" },
  rental: { en: "Rental", bn: "রেন্টাল" },
  marketplace: { en: "Marketplace", bn: "মার্কেটপ্লেস" },
};

function ContractsContent() {
  const { locale } = useLanguage();
  const bn = locale === "bn";
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [summary, setSummary] = useState({ active: 0, expiring_90: 0, annual_value_bdt: "0.00" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");

  useEffect(() => {
    let active = true;
    callOdoo<{
      contracts: Contract[];
      summary: { active: number; expiring_90: number; annual_value_bdt: string };
    }>("/corporate/contracts")
      .then((d) => {
        if (!active) return;
        setContracts(d.contracts || []);
        setSummary(d.summary || { active: 0, expiring_90: 0, annual_value_bdt: "0.00" });
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
      contracts.filter((c) => {
        const q = query.trim().toLowerCase();
        const matchesQuery = !q || c.code.toLowerCase().includes(q) || c.name.toLowerCase().includes(q);
        const matchesState = filter === "all" || c.state === filter;
        return matchesQuery && matchesState;
      }),
    [contracts, query, filter]
  );

  if (loading) return <Loading label={bn ? "চুক্তি লোড হচ্ছে…" : "Loading contracts…"} />;
  if (error) return <LoadError what={bn ? "চুক্তি" : "Contracts"} message={error} />;

  return (
    <main style={pageStyle}>
      <PageHeader
        title={bn ? "চুক্তি ও এসএলএ" : "Contracts & SLA"}
        subtitle={
          bn
            ? "আপনার এএমসি ও ম্যানেজড সার্ভিস চুক্তি, কভারেজ, নবায়ন সময়সীমা এবং প্রতিশ্রুত রেসপন্স/রেজোলিউশন লক্ষ্য।"
            : "Your AMC and managed-service agreements, coverage, renewal horizon and committed response/resolution targets."
        }
        actions={
          <>
            <Link href="/estate" style={{ ...linkButtonStyle, textDecoration: "none" }}>
              {bn ? "কভার করা ডিভাইস" : "Covered devices"}
            </Link>
            <Link href="/service-requests" style={{ ...linkButtonStyle, textDecoration: "none" }}>
              {bn ? "সার্ভিস রিকোয়েস্ট" : "Raise a request"}
            </Link>
          </>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label={bn ? "সক্রিয় চুক্তি" : "Active contracts"} value={summary.active} tone="primary" />
        <StatCard label={bn ? "৯০ দিনে শেষ" : "Expiring in 90 days"} value={summary.expiring_90} tone={summary.expiring_90 ? "warning" : "neutral"} />
        <StatCard label={bn ? "বার্ষিক চুক্তিমূল্য" : "Annual contract value"} value={`৳ ${summary.annual_value_bdt}`} tone="success" />
      </section>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", marginBottom: 12 }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={bn ? "চুক্তি নং বা নাম খুঁজুন…" : "Search contract no. or title…"}
          style={{
            flex: "1 1 280px",
            maxWidth: 420,
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
          { key: "active", en: "Active", bn: "সক্রিয়" },
          { key: "expiring", en: "Expiring", bn: "শেষ হচ্ছে" },
          { key: "expired", en: "Expired", bn: "মেয়াদোত্তীর্ণ" },
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
                <th style={thStyle}>{bn ? "চুক্তি" : "Contract"}</th>
                <th style={thStyle}>{bn ? "পরিবার" : "Family"}</th>
                <th style={thStyle}>{bn ? "মেয়াদ" : "Term"}</th>
                <th style={{ ...thStyle, textAlign: "right" }}>{bn ? "বার্ষিক মূল্য" : "Annual value"}</th>
                <th style={thStyle}>{bn ? "বিলিং" : "Billing"}</th>
                <th style={thStyle}>{bn ? "কভারেজ" : "Coverage"}</th>
                <th style={thStyle}>{bn ? "এসএলএ" : "SLA"}</th>
                <th style={thStyle}>{bn ? "অবস্থা" : "Status"}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => (
                <tr key={c.id}>
                  <td style={tdStyle}>
                    <div style={{ fontWeight: 600 }}>{c.code}</div>
                    <div style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>{c.name}</div>
                  </td>
                  <td style={tdStyle}>{FAMILY[c.family] ? (bn ? FAMILY[c.family].bn : FAMILY[c.family].en) : c.family}</td>
                  <td style={tdStyle}>
                    <div>{c.date_start}</div>
                    <div style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
                      → {c.date_end}
                      {c.days_to_expiry !== null && c.days_to_expiry <= 90 && c.days_to_expiry >= 0
                        ? ` · ${c.days_to_expiry} ${bn ? "দিন বাকি" : "days left"}`
                        : ""}
                    </div>
                  </td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {c.annual_value_bdt}</td>
                  <td style={tdStyle}>{c.billing_frequency}</td>
                  <td style={tdStyle}>{c.covered_count} {bn ? "ডিভাইস" : "devices"}</td>
                  <td style={tdStyle}>
                    {c.slas.length === 0 && "—"}
                    {c.slas.map((s) => (
                      <div key={s.code} style={{ fontSize: 11.5 }}>
                        <span style={{ fontWeight: 600 }}>{s.code}</span>
                        {": "}
                        {s.response_hours ?? "—"}h / {s.resolution_hours ?? "—"}h
                      </div>
                    ))}
                  </td>
                  <td style={tdStyle}><StatePill state={c.state} /></td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 28 }}>
                    {bn
                      ? "কোনো চুক্তি পাওয়া যায়নি। আপনার অ্যাকাউন্ট ম্যানেজারের সাথে যোগাযোগ করুন।"
                      : "No contracts found. Contact your account manager to set up an AMC or managed-service agreement."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <p style={{ marginTop: 12, fontSize: 11.5, color: tokens["color.text.secondary"] }}>
        {bn
          ? "এসএলএ লক্ষ্য চুক্তির সাথে সংযুক্ত পলিসি থেকে আসে; বাস্তব সার্ভিস অর্ডারের ডেডলাইন সার্ভিস রিকোয়েস্ট পাতায় দেখা যায়।"
          : "SLA targets come from the policies attached to each contract; live service-order deadlines appear on the service requests page."}
      </p>
    </main>
  );
}

export default function ContractsPage() {
  return (
    <RequireAuth>
      <ContractsContent />
    </RequireAuth>
  );
}
