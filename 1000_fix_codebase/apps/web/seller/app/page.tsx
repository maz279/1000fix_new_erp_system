"use client";

/**
 * P07 public landing page — the marketplace seller's front door.
 *
 * Explains the seller self-service surface (KYC onboarding, job board and
 * quotes, stock and listings, payouts and statements, scorecard and 48h
 * disputes) and hands the visitor to the dedicated sign-in. No seller data is
 * shown before the session is verified.
 */
import Link from "next/link";
import { tokens } from "../lib/imports";
import { useAuth } from "../components/auth-gate";
import { linkButtonStyle, pageStyle, primaryLinkStyle } from "../components/ui";

const FEATURES = [
  {
    href: "/onboarding",
    icon: "🪪",
    en: "Onboarding & KYC",
    bn: "অনবোর্ডিং ও কেওয়াইসি",
    descEn: "Trade licence, BIN-13, e-TIN and NID verification status — quoting opens only after compliance verifies you.",
    descBn: "ট্রেড লাইসেন্স, বিআইএন-১৩, ই-টিআইএন ও এনআইডি যাচাই — কমপ্লায়েন্স অনুমোদনের পরেই কোটেশন চালু হয়।",
  },
  {
    href: "/jobs",
    icon: "📋",
    en: "Job board & quotes",
    bn: "জব বোর্ড ও কোটেশন",
    descEn: "See open repair jobs, quote with a price and ETA, and track your own quote — never another seller's.",
    descBn: "খোলা মেরামত জব দেখুন, মূল্য ও ইটিএ দিয়ে কোটেশন দিন, নিজের কোটেশন ট্র্যাক করুন — অন্য সেলারের নয়।",
  },
  {
    href: "/stock",
    icon: "📦",
    en: "Stock & listings",
    bn: "স্টক ও লিস্টিং",
    descEn: "Your active listings with on-hand, reserved and available stock — report a position in one step.",
    descBn: "আপনার সক্রিয় লিস্টিং, হাতে থাকা/রিজার্ভড/উপলব্ধ স্টক — এক ধাপে পজিশন রিপোর্ট করুন।",
  },
  {
    href: "/statements",
    icon: "💳",
    en: "Payouts & statements",
    bn: "পেমেন্ট ও স্টেটমেন্ট",
    descEn: "Gross, commission, §52 TDS and net per ledger line, with paid and pending totals — backend-computed.",
    descBn: "প্রতি লাইনে গ্রস, কমিশন, §৫২ টিডিএস ও নেট, পরিশোধিত ও অপেক্ষমাণ টোটালসহ — ব্যাকএন্ডে গণনা করা।",
  },
  {
    href: "/scorecard",
    icon: "⭐",
    en: "Scorecard",
    bn: "স্কোরকার্ড",
    descEn: "Acceptance, on-time delivery, ratings and disputes by period — the numbers that set your tier.",
    descBn: "পিরিয়ড অনুযায়ী অ্যাকসেপ্টেন্স, সময়মতো ডেলিভারি, রেটিং ও বিরোধ — যা আপনার টিয়ার নির্ধারণ করে।",
  },
  {
    href: "/disputes",
    icon: "⚖️",
    en: "Disputes & 48h SLA",
    bn: "বিরোধ ও ৪৮ ঘণ্টা এসএলএ",
    descEn: "Every dispute against your jobs with its reason, amount and 48-hour resolution standing.",
    descBn: "আপনার জবের বিরুদ্ধে প্রতিটি বিরোধ, কারণ, পরিমাণ ও ৪৮ ঘণ্টার সমাধান অবস্থা।",
  },
];

export default function SellerLandingPage() {
  const { status, user } = useAuth();
  const signedIn = status === "signed-in" && Boolean(user);

  return (
    <main style={pageStyle}>
      <section
        aria-labelledby="seller-hero-title"
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
            1000 FiX · MARKETPLACE SELLER PORTAL (P07)
          </p>
          <h1
            id="seller-hero-title"
            style={{ margin: "8px 0 10px", fontSize: tokens["typography.size.600"], lineHeight: 1.18, color: "#fff" }}
          >
            Grow your repair<br />business with 1000 FiX.
          </h1>
          <p style={{ margin: 0, maxWidth: "74ch", fontSize: 14, lineHeight: 1.65, opacity: 0.9 }}>
            KYC onboarding, open repair jobs, quotes with price and ETA, stock and listings,
            transparent settlement statements and 48-hour dispute tracking — in one seller account.
          </p>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 20 }}>
            <Link
              href={signedIn ? "/dashboard" : "/login"}
              style={{
                ...primaryLinkStyle,
                background: "#fff",
                color: tokens["color.primary.base"],
                padding: "10px 18px",
                fontSize: 14,
              }}
            >
              {signedIn ? "Open my dashboard" : "Seller sign in"}
            </Link>
            <Link
              href="/jobs"
              style={{
                ...linkButtonStyle,
                background: "transparent",
                color: "#fff",
                borderColor: "rgba(255,255,255,0.45)",
                padding: "10px 18px",
                fontSize: 14,
              }}
            >
              Browse open jobs →
            </Link>
          </div>
          <p style={{ margin: "14px 0 0", fontSize: 11.5, opacity: 0.8, lineHeight: 1.55 }}>
            New seller? Contact seller support on 16743 to start onboarding. No demo or shared
            credential exists; KYC is completed by 1000 FiX compliance.
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }} aria-label="Portal facts">
          {[
            { value: "48h", en: "Dispute SLA", bn: "বিরোধ এসএলএ" },
            { value: "§52", en: "TDS statements", bn: "টিডিএস স্টেটমেন্ট" },
            { value: "KYC", en: "Verified sellers", bn: "যাচাইকৃত সেলার" },
            { value: "P07", en: "Seller workspace", bn: "সেলার ওয়ার্কস্পেস" },
          ].map((f) => (
            <div
              key={f.value}
              style={{
                background: "rgba(255,255,255,0.1)",
                border: "1px solid rgba(255,255,255,0.18)",
                borderRadius: tokens["dimension.border.radius-md"],
                padding: "13px 14px",
              }}
            >
              <b style={{ display: "block", fontSize: 17, color: "#fff", whiteSpace: "nowrap" }}>{f.value}</b>
              <span style={{ fontSize: 10.5, opacity: 0.8 }}>{f.en}</span>
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginTop: 28 }} aria-labelledby="seller-features-title">
        <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
          <h2 id="seller-features-title" style={{ margin: 0, fontSize: tokens["typography.size.400"], color: tokens["color.text.primary"] }}>
            What your seller account provides
          </h2>
          <p style={{ margin: 0, fontSize: 12, color: tokens["color.text.secondary"] }}>
            Every screen is scoped to your own seller profile — never another seller's jobs, quotes or money.
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 12 }}>
          {FEATURES.map((f) => (
            <Link
              key={f.href}
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
              <span style={{ fontSize: 20 }} aria-hidden>{f.icon}</span>
              <strong style={{ fontSize: 13.5 }}>{f.en}</strong>
              <span lang="bn" style={{ fontSize: 11, color: tokens["color.text.secondary"] }}>{f.bn}</span>
              <span style={{ fontSize: 12, lineHeight: 1.55, color: tokens["color.text.secondary"] }}>{f.descEn}</span>
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
            Seller support
          </h2>
          <p style={{ margin: 0, maxWidth: "75ch", fontSize: 12.5, lineHeight: 1.55, color: tokens["color.text.secondary"] }}>
            Onboarding, KYC documents, payout queries or a dispute you cannot see: call the seller desk
            on 16743. The enterprise hotline is staffed 24/7.
          </p>
        </div>
        <a href="tel:16743" style={{ ...primaryLinkStyle, textDecoration: "none" }}>☎ 16743</a>
      </section>

      <p style={{ marginTop: 18, paddingTop: 12, borderTop: `1px solid ${tokens["color.border.default"]}`, fontSize: 10.5, color: tokens["color.text.secondary"], textAlign: "center" }}>
        1000 FiX Services Ltd. · ISO 9001:2015 · P07 Marketplace Seller · financial values are
        backend-computed BN-007 strings, never portal calculations
      </p>
    </main>
  );
}
