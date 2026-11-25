"use client";

/**
 * P04 public landing page — the corporate client's front door.
 *
 * Explains the account-scoped self-service surface (fleet estate, contracts &
 * SLA, invoices & statements, bulk service requests, tenders & quotations,
 * reports and the account record) and gives one way in: corporate sign-in.
 * The dashboard behind /dashboard is client-only (proxy + RequireAuth).
 */
import Link from "next/link";
import { tokens } from "../lib/imports";
import { useLanguage } from "../components/language";
import { useAuth } from "../components/auth-modal";
import { pageStyle, primaryLinkStyle, linkButtonStyle } from "../components/ui";

const FEATURES = [
  {
    icon: "🏢",
    href: "/estate",
    en: "Fleet estate by site",
    bn: "সাইট অনুযায়ী ডিভাইস বহর",
    enDesc: "Every asset, its site, serial and warranty state — one estate register.",
    bnDesc: "প্রতিটি অ্যাসেট, সাইট, সিরিয়াল ও ওয়ারেন্টি অবস্থা — এক রেজিস্টারে।",
  },
  {
    icon: "📄",
    href: "/contracts",
    en: "Contracts & SLA",
    bn: "চুক্তি ও এসএলএ",
    enDesc: "AMC/managed agreements, coverage, renewal dates and response targets.",
    bnDesc: "এএমসি/ম্যানেজড চুক্তি, কভারেজ, নবায়ন তারিখ ও রেসপন্স লক্ষ্য।",
  },
  {
    icon: "🧾",
    href: "/invoices",
    en: "Invoices & statements",
    bn: "ইনভয়েস ও স্টেটমেন্ট",
    enDesc: "Consolidated billing, outstanding balance, aging and CSV statements.",
    bnDesc: "কনসোলিডেটেড বিলিং, বাকি ব্যালেন্স, এজিং ও সিএসভি স্টেটমেন্ট।",
  },
  {
    icon: "📝",
    href: "/service-requests",
    en: "Bulk service requests",
    bn: "বাল্ক সার্ভিস রিকোয়েস্ট",
    enDesc: "Raise one request across many devices with priority and site routing.",
    bnDesc: "একাধিক ডিভাইসের জন্য প্রায়োরিটি ও সাইটসহ এক অনুরোধ।",
  },
  {
    icon: "⚖️",
    href: "/tenders",
    en: "Tenders & quotations",
    bn: "টেন্ডার ও কোটেশন",
    enDesc: "Your procuring tenders and the quotations 1000 FiX has issued.",
    bnDesc: "আপনার টেন্ডার ও ১০০০ FiX-এর ইস্যু করা কোটেশন।",
  },
  {
    icon: "📊",
    href: "/reports",
    en: "Spend & service reports",
    bn: "ব্যয় ও সার্ভিস রিপোর্ট",
    enDesc: "Six-month spend, request volume, site distribution and AR aging.",
    bnDesc: "ছয় মাসের ব্যয়, অনুরোধের পরিমাণ, সাইট বণ্টন ও এজিং।",
  },
  {
    icon: "🏦",
    href: "/account",
    en: "Account record",
    bn: "অ্যাকাউন্ট রেকর্ড",
    enDesc: "Company master data, billing identity, contacts and account manager.",
    bnDesc: "কোম্পানির মূল তথ্য, বিলিং পরিচয়, যোগাযোগ ও অ্যাকাউন্ট ম্যানেজার।",
  },
  {
    icon: "🎧",
    href: "/service-requests",
    en: "Dedicated enterprise desk",
    bn: "ডেডিকেটেড এন্টারপ্রাইজ ডেস্ক",
    enDesc: "Hotline 16743 and your named account manager for escalations.",
    bnDesc: "এস্কেলেশনের জন্য হটলাইন ১৬৭৪৩ ও আপনার নামযুক্ত অ্যাকাউন্ট ম্যানেজার।",
  },
];

const FACTS = [
  { value: "ISO 9001:2015", en: "Certified service", bn: "সার্টিফায়েড সার্ভিস" },
  { value: "51+", en: "Service centres", bn: "সার্ভিস সেন্টার" },
  { value: "8", en: "Divisions", bn: "বিভাগ" },
  { value: "24/7", en: "SLA support", bn: "এসএলএ সাপোর্ট" },
];

export default function CorporateLandingPage() {
  const { locale } = useLanguage();
  const { user } = useAuth();
  const bn = locale === "bn";

  return (
    <main style={pageStyle}>
      <section
        aria-labelledby="corp-hero-title"
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 1.55fr) minmax(240px, 0.75fr)",
          gap: 26,
          alignItems: "center",
          padding: "32px 28px",
          borderRadius: tokens["dimension.border.radius-lg"],
          background: `linear-gradient(150deg, ${tokens["color.primary.hover"]}, ${tokens["color.primary.base"]})`,
          color: tokens["color.text.inverse"],
        }}
      >
        <div>
          <p style={{ margin: 0, fontSize: 11, letterSpacing: "0.16em", textTransform: "uppercase", opacity: 0.8 }}>
            {bn ? "১০০০ FiX · কর্পোরেট বি২বি পোর্টাল" : "1000 FiX · CORPORATE B2B PORTAL"}
          </p>
          <h1
            id="corp-hero-title"
            style={{
              margin: "8px 0 10px",
              fontSize: tokens["typography.size.600"],
              lineHeight: 1.18,
              color: "#fff",
            }}
          >
            {bn ? (
              <>আপনার সার্ভিস অপারেশন, <br />এক জায়গায় নিয়ন্ত্রণে।</>
            ) : (
              <>Your service operations, <br />under control.</>
            )}
          </h1>
          <p style={{ margin: 0, maxWidth: "72ch", fontSize: 14, lineHeight: 1.65, opacity: 0.9 }}>
            {bn
              ? "একাধিক সাইটের ডিভাইস বহর, চুক্তি ও এসএলএ, কনসোলিডেটেড বিলিং, বাল্ক সার্ভিস রিকোয়েস্ট এবং টেন্ডার — সবকিছু আপনার কর্পোরেট অ্যাকাউন্টের মধ্যে।"
              : "Multi-site device estate, contracts and SLAs, consolidated billing, bulk service requests and tenders — all inside your own corporate account."}
          </p>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 20 }}>
            <Link
              href={user ? "/dashboard" : "/login"}
              style={{
                ...primaryLinkStyle,
                background: "#fff",
                color: tokens["color.primary.base"],
                padding: "10px 18px",
                fontSize: 14,
              }}
            >
              {user
                ? bn
                  ? "ওভারভিউ খুলুন"
                  : "Open the overview"
                : bn
                  ? "কর্পোরেট অ্যাকাউন্টে সাইন ইন"
                  : "Sign in to your corporate account"}
            </Link>
            <Link
              href="/service-requests"
              style={{
                ...linkButtonStyle,
                background: "transparent",
                color: "#fff",
                borderColor: "rgba(255,255,255,0.45)",
                padding: "10px 18px",
                fontSize: 14,
              }}
            >
              {bn ? "সার্ভিস রিকোয়েস্ট করুন →" : "Raise a service request →"}
            </Link>
          </div>
          <p style={{ margin: "14px 0 0", fontSize: 11.5, opacity: 0.8, lineHeight: 1.55 }}>
            {bn
              ? "নতুন ক্লায়েন্ট? আপনার অ্যাকাউন্ট ম্যানেজার বা ১৬৭৪৩ হটলাইনে যোগাযোগ করুন — অ্যাক্সেস ও চুক্তি সেটআপ করা হবে।"
              : "New client? Contact your account manager or hotline 16743 — access and contract setup are provisioned by 1000 FiX."}
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }} aria-label={bn ? "পোর্টাল তথ্য" : "Portal facts"}>
          {FACTS.map((f) => (
            <div
              key={f.value}
              style={{
                background: "rgba(255,255,255,0.1)",
                border: "1px solid rgba(255,255,255,0.18)",
                borderRadius: tokens["dimension.border.radius-md"],
                padding: "13px 14px",
              }}
            >
              <b style={{ display: "block", fontSize: 17, color: "#fff" }}>{f.value}</b>
              <span style={{ fontSize: 10.5, opacity: 0.8 }}>{bn ? f.bn : f.en}</span>
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginTop: 28 }} aria-labelledby="corp-features-title">
        <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
          <h2 id="corp-features-title" style={{ margin: 0, fontSize: tokens["typography.size.400"], color: tokens["color.text.primary"] }}>
            {bn ? "আপনি যা করতে পারবেন" : "What your account can do"}
          </h2>
          <p style={{ margin: 0, fontSize: 12, color: tokens["color.text.secondary"] }}>
            {bn
              ? "প্রতিটি স্ক্রিন আপনার নিজের কমার্শিয়াল অ্যাকাউন্টে সীমাবদ্ধ — অন্য ক্লায়েন্টের ডেটা বা ব্যাক-অফিস কখনও নয়।"
              : "Every screen is fenced to your own commercial account — never another client's data, never the back office."}
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 12 }}>
          {FEATURES.map((f) => (
            <Link
              key={`${f.href}-${f.en}`}
              href={f.href}
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 6,
                padding: 16,
                background: tokens["color.surface.primary"],
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-md"],
                color: tokens["color.text.primary"],
                textDecoration: "none",
              }}
            >
              <span style={{ fontSize: 20, lineHeight: 1 }} aria-hidden>{f.icon}</span>
              <strong style={{ fontSize: 13.5 }}>{bn ? f.bn : f.en}</strong>
              <span style={{ fontSize: 12, lineHeight: 1.55, color: tokens["color.text.secondary"] }}>
                {bn ? f.bnDesc : f.enDesc}
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section
        style={{
          marginTop: 28,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 18,
          flexWrap: "wrap",
          padding: "18px 20px",
          background: tokens["color.surface.primary"],
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-lg"],
        }}
      >
        <div>
          <h2 style={{ margin: "0 0 4px", fontSize: tokens["typography.size.400"], color: tokens["color.text.primary"] }}>
            {bn ? "সাহায্য দরকার?" : "Need a hand?"}
          </h2>
          <p style={{ margin: 0, maxWidth: "70ch", fontSize: 12.5, lineHeight: 1.55, color: tokens["color.text.secondary"] }}>
            {bn
              ? "আপনার ডেডিকেটেড এন্টারপ্রাইজ ডেস্ক ১৬৭৪৩-এ ২৪/৭ খোলা। চুক্তি, বিলিং বা অ্যাক্সেস সংক্রান্ত সবকিছুর জন্য কল করুন।"
              : "Your dedicated enterprise desk is open 24/7 on 16743 — contracts, billing, access and escalations."}
          </p>
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <a href="tel:16743" style={{ ...primaryLinkStyle, textDecoration: "none" }}>☎ 16743</a>
          <Link href="/account" style={{ ...linkButtonStyle, textDecoration: "none" }}>
            {bn ? "অ্যাকাউন্ট দেখুন" : "View account"}
          </Link>
        </div>
      </section>

      <p style={{ marginTop: 18, paddingTop: 12, borderTop: `1px solid ${tokens["color.border.default"]}`, fontSize: 10.5, color: tokens["color.text.secondary"], textAlign: "center" }}>
        {bn
          ? "১০০০ FiX Services Ltd. · ISO 9001:2015 · PDPA ২০২৬ · কর্মীদের জন্য অপারেশনস পোর্টাল (P03)"
          : "1000 FiX Services Ltd. · ISO 9001:2015 · PDPA 2026 · Staff use the operations portal (P03)"}
      </p>
    </main>
  );
}
