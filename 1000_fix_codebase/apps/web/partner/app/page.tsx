"use client";

/**
 * Public landing for the P12 partner & referral portal.
 *
 * Explains the programme (consent-captured lead submission, lead-level
 * attribution, commission statement) and sends partners to /login. It
 * exposes no partner data and names no credential. Click/link attribution
 * is not offered because the backend does not record clicks.
 */
import { tokens, uiCopy } from "../lib/imports";
import { useAuth } from "../components/auth-gate";
import { linkButtonStyle, pageStyle, primaryLinkStyle } from "../components/ui";

const FEATURES: { icon: string; title: string; bn: string; body: string }[] = [
  {
    icon: "📝",
    title: "Submit a lead with consent",
    bn: "সম্মতিসহ লিড জমা দিন",
    body: "Name the customer, their phone and the service they need, and record how they agreed to be contacted (written, digital or recorded call).",
  },
  {
    icon: "🛡",
    title: "Lead-level protection",
    bn: "লিডভিত্তিক সুরক্ষা",
    body: "Every submission carries an attribution window. See the protection date and the lead's state — submitted, qualified, converted or lost with a reason.",
  },
  {
    icon: "📈",
    title: "Real pipeline, not vanity links",
    bn: "প্রকৃত পাইপলাইন",
    body: "The funnel is built from your actual leads and referrals: conversion rate, loss reasons and commission earned by service interest.",
  },
  {
    icon: "🧾",
    title: "Transparent commission statement",
    bn: "স্বচ্ছ কমিশন স্টেটমেন্ট",
    body: "Approved revenue, the frozen rate the commission was earned at, the earned amount and the referral's state — line by line.",
  },
  {
    icon: "🔐",
    title: "Scoped to your partner profile",
    bn: "আপনার পার্টনার প্রোফাইলে সীমাবদ্ধ",
    body: "The server resolves your partner profile from your sign-in; another partner's leads, referrals and commissions are never returned.",
  },
  {
    icon: "📞",
    title: "Human support",
    bn: "মানব সহায়তা",
    body: "Onboarding, KYC, disputed attribution and commission queries are handled by the partner desk on 16743.",
  },
];

export default function LandingPage() {
  const { status, user } = useAuth();
  const signedIn = status === "signed-in" && !!user;

  return (
    <main style={pageStyle}>
      <section
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 1.4fr) minmax(260px, 1fr)",
          gap: 32,
          alignItems: "center",
          padding: "28px 0 40px",
          borderBottom: `1px solid ${tokens["color.border.default"]}`,
        }}
      >
        <div>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "4px 10px",
              borderRadius: tokens["dimension.border.radius-pill"],
              background: tokens["color.status.info-bg"],
              color: tokens["color.status.info"],
              fontSize: tokens["typography.size.100"],
              fontWeight: 600,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              marginBottom: 16,
            }}
          >
            1000 FiX · Partner &amp; Referral Portal (P12)
          </div>
          <h1
            style={{
              margin: "0 0 14px",
              fontSize: "clamp(30px, 4vw, 46px)",
              lineHeight: 1.1,
              letterSpacing: "-0.02em",
              color: tokens["color.text.primary"],
            }}
          >
            Refer with confidence.
            <br />
            Get paid transparently.
          </h1>
          <p
            style={{
              margin: "0 0 22px",
              maxWidth: "62ch",
              fontSize: tokens["typography.size.300"],
              lineHeight: 1.6,
              color: tokens["color.text.secondary"],
            }}
          >
            Submit customer leads with recorded consent, follow each lead through the pipeline, and see the
            commission earned on the revenue you influenced. Every figure is backend-computed and scoped to
            your partner profile. Sign in with the partner account issued to you — no demo or shared
            credential exists.
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            <a
              href={signedIn ? "/dashboard" : "/login"}
              style={{ ...primaryLinkStyle, minHeight: 44, padding: "12px 22px", textDecoration: "none" }}
            >
              {signedIn ? "Open your dashboard →" : "Partner sign in →"}
            </a>
            <a href="tel:16743" style={{ ...linkButtonStyle, minHeight: 44, padding: "12px 18px", textDecoration: "none" }}>
              ☎ Partner desk 16743
            </a>
          </div>
        </div>

        <div
          style={{
            padding: 22,
            background: tokens["color.surface.primary"],
            border: `1px solid ${tokens["color.border.default"]}`,
            borderRadius: tokens["dimension.border.radius-md"],
          }}
        >
          <div style={{ fontSize: tokens["typography.size.200"], fontWeight: 700, marginBottom: 12 }}>
            Programme at a glance
          </div>
          {[
            ["Partner types", "Referral · reseller · franchise · alliance"],
            ["Attribution", "Per submitted lead, with consent"],
            ["Commission", "Frozen rate at earning"],
            ["Access", "Partner profile only"],
          ].map(([k, v]) => (
            <div
              key={k}
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 12,
                padding: "8px 0",
                borderTop: `1px solid ${tokens["color.border.default"]}`,
                fontSize: tokens["typography.size.200"],
              }}
            >
              <span style={{ color: tokens["color.text.secondary"] }}>{k}</span>
              <span style={{ fontWeight: 600, color: tokens["color.text.primary"], textAlign: "right" }}>{v}</span>
            </div>
          ))}
        </div>
      </section>

      <section aria-label="What the portal provides" style={{ padding: "34px 0 12px" }}>
        <h2 style={{ margin: "0 0 18px", fontSize: tokens["typography.size.400"], color: tokens["color.text.primary"] }}>
          What the portal provides
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 14 }}>
          {FEATURES.map((f) => (
            <article
              key={f.title}
              style={{
                padding: 18,
                background: tokens["color.surface.primary"],
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-md"],
              }}
            >
              <div style={{ fontSize: 22, marginBottom: 8 }} aria-hidden="true">{f.icon}</div>
              <h3 style={{ margin: "0 0 2px", fontSize: tokens["typography.size.300"], color: tokens["color.text.primary"] }}>
                {f.title}
              </h3>
              <div lang="bn" style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"], marginBottom: 8 }}>
                {f.bn}
              </div>
              <p style={{ margin: 0, fontSize: tokens["typography.size.200"], lineHeight: 1.55, color: tokens["color.text.secondary"] }}>
                {f.body}
              </p>
            </article>
          ))}
        </div>
      </section>

      <p style={{ marginTop: 28, fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
        This portal records lead-level attribution only. Co-branded links that track clicks are not offered —
        the platform does not record them, so a link would credit nothing. For programme terms contact the
        partner desk on 16743. {uiCopy("nav.portal.p12", "bn")}
      </p>
    </main>
  );
}
