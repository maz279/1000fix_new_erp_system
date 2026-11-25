"use client";

/**
 * Public landing for the P05 vendor & supplier portal.
 *
 * Explains the vendor workspace (PO acknowledgement, invoice submission into
 * the three-way match, status/payment visibility, compliance documents and
 * score) and sends vendors to /login. It exposes no vendor data.
 */
import { tokens, uiCopy } from "../lib/imports";
import { useAuth } from "../components/auth-gate";
import { linkButtonStyle, pageStyle, primaryLinkStyle } from "../components/ui";

const FEATURES: { icon: string; title: string; bn: string; body: string }[] = [
  {
    icon: "📦",
    title: "Acknowledge purchase orders",
    bn: "পারচেজ অর্ডার স্বীকৃতি দিন",
    body: "See every PO issued to you, confirm the delivery date you commit to, and watch the received quantities the warehouse books against it.",
  },
  {
    icon: "🧾",
    title: "Submit invoices against a PO",
    bn: "পিও-এর বিপরীতে ইনভয়েস জমা দিন",
    body: "Submit your paper line by line. The server runs the three-way match (PO / goods receipt / invoice) and shows the outcome — including the exact block reason.",
  },
  {
    icon: "💳",
    title: "Invoice status, approval and payment",
    bn: "ইনভয়েস স্ট্যাটাস, অনুমোদন ও পেমেন্ট",
    body: "Each invoice carries its match, approval and payment state plus the due date, so you can plan cash without calling the AP desk.",
  },
  {
    icon: "🏅",
    title: "Your performance score",
    bn: "আপনার পারফরম্যান্স স্কোর",
    body: "The qualification score the buyer uses, the supplier standing and the payment-block state are visible to you — the same numbers, not a different story.",
  },
  {
    icon: "📄",
    title: "Compliance documents and expiry",
    bn: "কমপ্লায়েন্স ডকুমেন্ট ও মেয়াদ",
    body: "Trade licence, TIN, VAT and other documents with their validity dates, so a renewal is planned before it lapses.",
  },
  {
    icon: "🔐",
    title: "Fenced to your vendor account",
    bn: "আপনার ভেন্ডর অ্যাকাউন্টে সীমাবদ্ধ",
    body: "Every query is scoped by the server to your commercial partner. Another supplier's orders, invoices and documents are never returned.",
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
            1000 FiX · Vendor &amp; Supplier Portal (P05)
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
            Supply 1000 FiX,
            <br />
            without the guesswork.
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
            Acknowledge purchase orders, submit invoices that run the three-way match, and see exactly
            where each invoice stands — match, approval and payment. Your compliance documents and
            performance score are in the same place. Sign in with the vendor account issued to you.
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            <a
              href={signedIn ? "/dashboard" : "/login"}
              style={{ ...primaryLinkStyle, minHeight: 44, padding: "12px 22px", textDecoration: "none" }}
            >
              {signedIn ? "Open your dashboard →" : "Vendor sign in →"}
            </a>
            <a href="tel:16743" style={{ ...linkButtonStyle, minHeight: 44, padding: "12px 18px", textDecoration: "none" }}>
              ☎ Supplier desk 16743
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
            How settlement works
          </div>
          {[
            ["1", "You acknowledge the PO + delivery date"],
            ["2", "Warehouse books the receipt (not you)"],
            ["3", "You submit the invoice against the PO"],
            ["4", "The server matches PO / receipt / invoice"],
            ["5", "AP approves and pays to terms"],
          ].map(([n, text]) => (
            <div
              key={n}
              style={{
                display: "flex",
                gap: 10,
                padding: "8px 0",
                borderTop: `1px solid ${tokens["color.border.default"]}`,
                fontSize: tokens["typography.size.200"],
              }}
            >
              <span
                style={{
                  width: 20,
                  height: 20,
                  borderRadius: "50%",
                  background: tokens["color.surface.secondary"],
                  color: tokens["color.text.primary"],
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 11,
                  fontWeight: 700,
                  flexShrink: 0,
                }}
              >
                {n}
              </span>
              <span style={{ color: tokens["color.text.secondary"] }}>{text}</span>
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
        Goods receipts are recorded by the 1000 FiX warehouse, never self-certified in the portal — that is
        what keeps the three-way match honest. {uiCopy("nav.portal.p05", "bn")}
      </p>
    </main>
  );
}
