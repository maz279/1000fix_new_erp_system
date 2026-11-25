"use client";

/**
 * P08 public landing page — the brand partner's front door.
 *
 * Explains the partner surface (claim decisions, evidence gate, remittance
 * advice and reconciliation, brand isolation) and hands the visitor to the
 * dedicated sign-in. No claim data is shown before the session is verified.
 */
import Link from "next/link";
import { tokens } from "../lib/imports";
import { useAuth } from "../components/auth-gate";
import { linkButtonStyle, pageStyle, primaryLinkStyle } from "../components/ui";

const FEATURES = [
  {
    href: "/claims",
    icon: "📑",
    en: "Warranty claim decisions",
    bn: "ওয়ারেন্টি দাবির সিদ্ধান্ত",
    descEn: "The submitted queue for your brand: evidence completeness, amount, state and approve/reject with a reason.",
    descBn: "আপনার ব্র্যান্ডের সাবমিটেড কিউ: এভিডেন্স সম্পূর্ণতা, পরিমাণ, অবস্থা এবং কারণসহ অনুমোদন/প্রত্যাখ্যান।",
  },
  {
    href: "/reconciliation",
    icon: "💳",
    en: "Remittance & reconciliation",
    bn: "রেমিট্যান্স ও রিকনসিলিয়েশন",
    descEn: "Approved vs received, your remittance advice, and mismatches flagged — never auto-adjusted.",
    descBn: "অনুমোদিত বনাম প্রাপ্ত, আপনার রেমিট্যান্স অ্যাডভাইস এবং মিসম্যাচ ফ্ল্যাগ — কখনও স্বয়ংক্রিয় সমন্বয় নয়।",
  },
  {
    href: "/dashboard",
    icon: "📊",
    en: "Brand claim posture",
    bn: "ব্র্যান্ড দাবির অবস্থা",
    descEn: "Claimed, approved, remitted and outstanding totals with the state mix and mismatch count.",
    descBn: "দাবিকৃত, অনুমোদিত, রেমিটেড ও বাকি টোটাল, স্টেট মিক্স ও মিসম্যাচ সংখ্যাসহ।",
  },
  {
    href: "/account",
    icon: "🔐",
    en: "Brand access",
    bn: "ব্র্যান্ড অ্যাক্সেস",
    descEn: "The brands linked to your account — every call is scoped by the server, never a raw brand id.",
    descBn: "আপনার অ্যাকাউন্টে সংযুক্ত ব্র্যান্ড — প্রতিটি কল সার্ভারে সীমাবদ্ধ, কখনও কাঁচা ব্র্যান্ড আইডি নয়।",
  },
];

export default function BrandLandingPage() {
  const { status, user } = useAuth();
  const signedIn = status === "signed-in" && Boolean(user);

  return (
    <main style={pageStyle}>
      <section
        aria-labelledby="brand-hero-title"
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
            1000 FiX · BRAND PARTNER PORTAL (P08)
          </p>
          <h1
            id="brand-hero-title"
            style={{ margin: "8px 0 10px", fontSize: tokens["typography.size.600"], lineHeight: 1.18, color: "#fff" }}
          >
            Warranty claims,<br />settled transparently.
          </h1>
          <p style={{ margin: 0, maxWidth: "74ch", fontSize: 14, lineHeight: 1.65, opacity: 0.9 }}>
            Decide your brand's warranty claims with the evidence in front of you, record remittance
            advice, and reconcile every approved amount against money received — scoped to your brand only.
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
              {signedIn ? "Open my dashboard" : "Brand partner sign in"}
            </Link>
            <Link
              href="/claims"
              style={{
                ...linkButtonStyle,
                background: "transparent",
                color: "#fff",
                borderColor: "rgba(255,255,255,0.45)",
                padding: "10px 18px",
                fontSize: 14,
              }}
            >
              View the claim queue →
            </Link>
          </div>
          <p style={{ margin: "14px 0 0", fontSize: 11.5, opacity: 0.8, lineHeight: 1.55 }}>
            New partner? Contact the warranty desk on 16743 to link your brand to your account.
            No demo or shared credential exists.
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }} aria-label="Portal facts">
          {[
            { value: "P08", en: "Brand partner", bn: "ব্র্যান্ড পার্টনার" },
            { value: "2-way", en: "Claim decisions", bn: "দাবি সিদ্ধান্ত" },
            { value: "Flagged", en: "Mismatches", bn: "মিসম্যাচ" },
            { value: "Scoped", en: "Per brand", bn: "প্রতি ব্র্যান্ড" },
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

      <section style={{ marginTop: 28 }} aria-labelledby="brand-features-title">
        <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
          <h2 id="brand-features-title" style={{ margin: 0, fontSize: tokens["typography.size.400"], color: tokens["color.text.primary"] }}>
            What your brand account provides
          </h2>
          <p style={{ margin: 0, fontSize: 12, color: tokens["color.text.secondary"] }}>
            Every call is scoped by the server to the brands linked to your user — never another brand's claims.
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
            Warranty desk
          </h2>
          <p style={{ margin: 0, maxWidth: "75ch", fontSize: 12.5, lineHeight: 1.55, color: tokens["color.text.secondary"] }}>
            For access, claim evidence or remittance queries call 16743. Decisions and remittance
            advice are recorded against your brand user with an audit trail.
          </p>
        </div>
        <a href="tel:16743" style={{ ...primaryLinkStyle, textDecoration: "none" }}>☎ 16743</a>
      </section>

      <p style={{ marginTop: 18, paddingTop: 12, borderTop: `1px solid ${tokens["color.border.default"]}`, fontSize: 10.5, color: tokens["color.text.secondary"], textAlign: "center" }}>
        1000 FiX Services Ltd. · ISO 9001:2015 · P08 Brand Partner · monetary values are backend-computed
        BN-007 strings, never portal calculations
      </p>
    </main>
  );
}
