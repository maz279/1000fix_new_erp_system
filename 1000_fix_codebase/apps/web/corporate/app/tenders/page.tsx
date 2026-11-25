"use client";

/**
 * Tenders & quotations — the procuring tenders where this account is the
 * client, plus the quotations 1000 FiX has issued to it (M36 read).
 * Internal bid preparation (draft / no-bid) is never exposed.
 */
import { useEffect, useState } from "react";
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

interface Tender {
  id: number;
  reference: string;
  name: string;
  client_name: string;
  due_date: string;
  state: string;
  tender_type: string;
  estimated_value_bdt: string;
  awarded_value_bdt: string;
  award_ref: string;
  days_to_due: number | null;
}

interface Quotation {
  id: number;
  name: string;
  quote_type: string;
  state: string;
  version: number;
  value_bdt: string;
  valid_until: string;
  sent_at: string;
}

const TYPE_LABEL: Record<string, { en: string; bn: string }> = {
  public_egp: { en: "Public tender (e-GP)", bn: "পাবলিক টেন্ডার (ই-জিপি)" },
  private_rfq: { en: "Private RFQ", bn: "প্রাইভেট আরএফকিউ" },
  private_rfp: { en: "Private RFP", bn: "প্রাইভেট আরএফপি" },
};
const QUOTE_LABEL: Record<string, { en: string; bn: string }> = {
  service: { en: "Service order", bn: "সার্ভিস অর্ডার" },
  contract: { en: "Contract", bn: "চুক্তি" },
  subscription: { en: "Subscription", bn: "সাবস্ক্রিপশন" },
  project: { en: "Goods & works", bn: "গুডস ও ওয়ার্কস" },
};

function TendersContent() {
  const { locale } = useLanguage();
  const bn = locale === "bn";
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [quotations, setQuotations] = useState<Quotation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    callOdoo<{ tenders: Tender[]; quotations: Quotation[] }>("/corporate/tenders")
      .then((d) => {
        if (!active) return;
        setTenders(d.tenders || []);
        setQuotations(d.quotations || []);
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

  if (loading) return <Loading label={bn ? "টেন্ডার লোড হচ্ছে…" : "Loading tenders…"} />;
  if (error) return <LoadError what={bn ? "টেন্ডার" : "Tenders"} message={error} />;

  const openTenders = tenders.filter((t) => t.state === "submitted").length;
  const pendingQuotes = quotations.filter((q) => ["sent", "approved"].includes(q.state)).length;
  const acceptedQuotes = quotations.filter((q) => q.state === "accepted").length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title={bn ? "টেন্ডার ও কোটেশন" : "Tenders & quotations"}
        subtitle={
          bn
            ? "আপনার প্রসিউরিং টেন্ডার এবং ১০০০ FiX-এর ইস্যু করা কোটেশন ও চুক্তি-প্রস্তাব।"
            : "Your procuring tenders and the quotations/contract proposals 1000 FiX has issued to you."
        }
        actions={
          <>
            <a href="tel:16743" style={{ ...linkButtonStyle, textDecoration: "none" }}>
              ☎ {bn ? "টেন্ডার ডেস্ক" : "Tender desk"}
            </a>
            <a href="mailto:tenders@1000fix.com" style={{ ...linkButtonStyle, textDecoration: "none" }}>
              ✉ tenders@1000fix.com
            </a>
          </>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label={bn ? "খোলা টেন্ডার" : "Open tenders"} value={openTenders} tone="primary" />
        <StatCard label={bn ? "অপেক্ষমাণ কোটেশন" : "Pending quotations"} value={pendingQuotes} tone="warning" />
        <StatCard label={bn ? "গৃহীত কোটেশন" : "Accepted quotations"} value={acceptedQuotes} tone="success" />
        <StatCard label={bn ? "মোট" : "Total records"} value={tenders.length + quotations.length} />
      </section>

      <Panel title={bn ? "টেন্ডার" : "Tenders"}>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>{bn ? "রেফারেন্স" : "Reference"}</th>
                <th style={thStyle}>{bn ? "শিরোনাম" : "Title"}</th>
                <th style={thStyle}>{bn ? "ধরন" : "Type"}</th>
                <th style={thStyle}>{bn ? "জমার শেষ তারিখ" : "Due"}</th>
                <th style={{ ...thStyle, textAlign: "right" }}>{bn ? "আনুমানিক মূল্য" : "Estimated value"}</th>
                <th style={thStyle}>{bn ? "ফলাফল" : "Outcome"}</th>
                <th style={thStyle}>{bn ? "অবস্থা" : "Status"}</th>
              </tr>
            </thead>
            <tbody>
              {tenders.map((t) => (
                <tr key={t.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{t.reference}</td>
                  <td style={tdStyle}>
                    <div>{t.name}</div>
                    <div style={{ fontSize: 11, color: tokens["color.text.secondary"] }}>{t.client_name}</div>
                  </td>
                  <td style={tdStyle}>{TYPE_LABEL[t.tender_type] ? (bn ? TYPE_LABEL[t.tender_type].bn : TYPE_LABEL[t.tender_type].en) : t.tender_type}</td>
                  <td style={tdStyle}>
                    {t.due_date}
                    {t.days_to_due !== null && (
                      <div style={{ fontSize: 10.5, color: t.days_to_due < 0 ? tokens["color.status.error"] : tokens["color.text.secondary"] }}>
                        {t.days_to_due < 0
                          ? `${Math.abs(t.days_to_due)} ${bn ? "দিন আগে" : "days ago"}`
                          : `${t.days_to_due} ${bn ? "দিন বাকি" : "days left"}`}
                      </div>
                    )}
                  </td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {t.estimated_value_bdt}</td>
                  <td style={tdStyle}>
                    {t.state === "won" ? (
                      <span style={{ fontSize: 11.5 }}>
                        {bn ? "জয়" : "Won"}{t.award_ref ? ` · ${t.award_ref}` : ""}
                        {t.awarded_value_bdt ? <div>৳ {t.awarded_value_bdt}</div> : null}
                      </span>
                    ) : t.state === "lost" ? (bn ? "হারা" : "Lost") : "—"}
                  </td>
                  <td style={tdStyle}><StatePill state={t.state} /></td>
                </tr>
              ))}
              {tenders.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 26 }}>
                    {bn
                      ? "আপনার নামে কোনো সাবমিটেড টেন্ডার নেই। নতুন টেন্ডারের জন্য টেন্ডার ডেস্কে যোগাযোগ করুন।"
                      : "No submitted tenders under your account. Contact the tender desk to register a new procurement."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <div style={{ marginTop: 16 }}>
        <Panel title={bn ? "কোটেশন ও প্রস্তাব" : "Quotations & proposals"}>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: tokens["color.surface.secondary"] }}>
                  <th style={thStyle}>{bn ? "কোটেশন" : "Quotation"}</th>
                  <th style={thStyle}>{bn ? "ধরন" : "Type"}</th>
                  <th style={thStyle}>{bn ? "সংস্করণ" : "Version"}</th>
                  <th style={{ ...thStyle, textAlign: "right" }}>{bn ? "মূল্য" : "Value"}</th>
                  <th style={thStyle}>{bn ? "বৈধতা" : "Valid until"}</th>
                  <th style={thStyle}>{bn ? "অবস্থা" : "Status"}</th>
                </tr>
              </thead>
              <tbody>
                {quotations.map((q) => (
                  <tr key={q.id}>
                    <td style={{ ...tdStyle, fontWeight: 600 }}>{q.name}</td>
                    <td style={tdStyle}>{QUOTE_LABEL[q.quote_type] ? (bn ? QUOTE_LABEL[q.quote_type].bn : QUOTE_LABEL[q.quote_type].en) : q.quote_type}</td>
                    <td style={tdStyle}>v{q.version}</td>
                    <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {q.value_bdt}</td>
                    <td style={tdStyle}>{q.valid_until || "—"}</td>
                    <td style={tdStyle}><StatePill state={q.state} /></td>
                  </tr>
                ))}
                {quotations.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 26 }}>
                      {bn
                        ? "এখনও কোনো কোটেশন ইস্যু হয়নি। আপনার অ্যাকাউন্ট ম্যানেজার কোটেশন তৈরি করলে এখানে দেখা যাবে।"
                        : "No quotations issued yet. They appear here once your account manager issues one."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </main>
  );
}

export default function TendersPage() {
  return (
    <RequireAuth>
      <TendersContent />
    </RequireAuth>
  );
}
