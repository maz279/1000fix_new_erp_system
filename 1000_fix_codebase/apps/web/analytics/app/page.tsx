"use client";

/**
 * P06 public landing page — the analytics estate's front door.
 *
 * Staff-only: the page explains the decision surface (executive dashboards,
 * the 95-KPI register, data governance and model monitoring) and hands the
 * visitor to the dedicated staff sign-in. No metrics are shown before a
 * session is verified.
 */
import Link from "next/link";
import { tokens } from "../lib/imports";
import { useAuth } from "../components/auth-gate";
import { linkButtonStyle, pageStyle, primaryLinkStyle } from "../components/ui";

const FEATURES = [
  {
    href: "/dashboards",
    icon: "📊",
    en: "Executive & operational dashboards",
    bn: "এক্সিকিউটিভ ও অপারেশনাল ড্যাশবোর্ড",
    descEn: "Six curated views — executive, branch, technician, finance, warranty and people — with period comparison and CSV export.",
    descBn: "ছয়টি কিউরেটেড ভিউ — এক্সিকিউটিভ, ব্রাঞ্চ, টেকনিশিয়ান, ফাইন্যান্স, ওয়ারেন্টি ও কর্মী — পিরিয়ড তুলনা ও সিএসভি এক্সপোর্টসহ।",
  },
  {
    href: "/kpi-register",
    icon: "🎯",
    en: "The 95-KPI register",
    bn: "৯৫-কেপিআই রেজিস্টার",
    descEn: "Every KPI's family, owner, baseline, W4/W8 targets, source dataset and calculation formula — the single definitions source.",
    descBn: "প্রতিটি কেপিআই-এর পরিবার, মালিক, বেসলাইন, W4/W8 লক্ষ্য, সোর্স ডেটাসেট ও গণনার সূত্র — একক সংজ্ঞা উৎস।",
  },
  {
    href: "/governance",
    icon: "🛡️",
    en: "Data governance",
    bn: "ডেটা গভর্নেন্স",
    descEn: "Catalogue completeness, source-to-target lineage, data-quality rules and residency compliance — with frozen-artifact labels.",
    descBn: "ক্যাটালগ সম্পূর্ণতা, সোর্স-টু-টার্গেট লিনিয়েজ, ডেটা-কোয়ালিটি রুল ও রেসিডেন্সি কমপ্লায়েন্স — ফ্রোজেন আর্টিফ্যাক্ট লেবেলসহ।",
  },
  {
    href: "/models",
    icon: "🤖",
    en: "Model monitoring",
    bn: "মডেল মনিটরিং",
    descEn: "Bengali speech-to-text model version, evaluation WER, drift status and PDPA checks — with the evaluation scope stated.",
    descBn: "বাংলা স্পিচ-টু-টেক্সট মডেল সংস্করণ, WER, ড্রিফট স্ট্যাটাস ও PDPA চেক — মূল্যায়নের পরিধি স্পষ্ট করে।",
  },
];

export default function AnalyticsLandingPage() {
  const { status, user } = useAuth();
  const signedIn = status === "signed-in" && Boolean(user?.isInternal);

  return (
    <main style={pageStyle}>
      <section
        aria-labelledby="an-hero-title"
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
            1000 FiX · ANALYTICS &amp; EXECUTIVE (P06)
          </p>
          <h1
            id="an-hero-title"
            style={{ margin: "8px 0 10px", fontSize: tokens["typography.size.600"], lineHeight: 1.18, color: "#fff" }}
          >
            Decisions from one<br />trusted number.
          </h1>
          <p style={{ margin: 0, maxWidth: "74ch", fontSize: 14, lineHeight: 1.65, opacity: 0.9 }}>
            Executive and operational KPIs computed in the backend, a governed 95-KPI register,
            lineage and data-quality evidence, and model monitoring — for 1000 FiX staff only.
          </p>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 20 }}>
            <Link
              href={signedIn ? "/dashboards" : "/login"}
              style={{
                ...primaryLinkStyle,
                background: "#fff",
                color: tokens["color.primary.base"],
                padding: "10px 18px",
                fontSize: 14,
              }}
            >
              {signedIn ? "Open dashboards" : "Staff sign in"}
            </Link>
            <Link
              href="/kpi-register"
              style={{
                ...linkButtonStyle,
                background: "transparent",
                color: "#fff",
                borderColor: "rgba(255,255,255,0.45)",
                padding: "10px 18px",
                fontSize: 14,
              }}
            >
              Browse the KPI register →
            </Link>
          </div>
          <p style={{ margin: "14px 0 0", fontSize: 11.5, opacity: 0.8, lineHeight: 1.55 }}>
            Sign in with your 1000 FiX staff (internal) account. Customer and partner portal
            accounts are refused; no demo or shared credential exists.
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }} aria-label="Portal facts">
          {[
            { value: "95", en: "Registered KPIs", bn: "নিবন্ধিত কেপিআই" },
            { value: "6", en: "Dashboards", bn: "ড্যাশবোর্ড" },
            { value: "ISO 9001", en: "Certified", bn: "সার্টিফায়েড" },
            { value: "P06", en: "Staff-only", bn: "শুধু কর্মীদের জন্য" },
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

      <section style={{ marginTop: 28 }} aria-labelledby="an-features-title">
        <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
          <h2 id="an-features-title" style={{ margin: 0, fontSize: tokens["typography.size.400"], color: tokens["color.text.primary"] }}>
            What the estate provides
          </h2>
          <p style={{ margin: 0, fontSize: 12, color: tokens["color.text.secondary"] }}>
            Every number is backend-computed; the portal holds no data copy and does no arithmetic.
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
            Need access?
          </h2>
          <p style={{ margin: 0, maxWidth: "75ch", fontSize: 12.5, lineHeight: 1.55, color: tokens["color.text.secondary"] }}>
            Analytics access is provisioned per role. Ask your department head or the BI team;
            the enterprise desk is on 16743.
          </p>
        </div>
        <a href="tel:16743" style={{ ...primaryLinkStyle, textDecoration: "none" }}>☎ 16743</a>
      </section>

      <p style={{ marginTop: 18, paddingTop: 12, borderTop: `1px solid ${tokens["color.border.default"]}`, fontSize: 10.5, color: tokens["color.text.secondary"], textAlign: "center" }}>
        1000 FiX Services Ltd. · ISO 9001:2015 · P06 Analytics &amp; Executive · staff-only · financial values are
        backend aggregates, never portal calculations
      </p>
    </main>
  );
}
