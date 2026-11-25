"use client";

/**
 * Public staff landing for the P10 agent console.
 *
 * The queue itself lives behind /queue; this page explains what the
 * workspace does and sends staff to the dedicated /login. It exposes no
 * ERP data and names no credential.
 */
import { tokens } from "../lib/imports";
import { useAuth } from "../components/auth-gate";
import { Badge, linkButtonStyle, pageStyle, primaryLinkStyle } from "../components/ui";

const FEATURES: { icon: string; title: string; bn: string; body: string }[] = [
  {
    icon: "🎧",
    title: "One omnichannel queue",
    bn: "একটাই সর্বচ্যানেল কিউ",
    body: "Voice 16743, WhatsApp, web chat, email and in-app contacts in one oldest-first queue with channel and state filters.",
  },
  {
    icon: "🤖",
    title: "AI → human handoff with context",
    bn: "কনটেক্সটসহ এআই থেকে মানুষের কাছে",
    body: "Claim an AI-handled conversation and keep the full transcript, NLU intent and customer 360 in front of you.",
  },
  {
    icon: "📋",
    title: "Customer 360 beside the transcript",
    bn: "ট্রান্সক্রিপ্টের পাশে কাস্টমার ৩৬০",
    body: "Open service orders, registered devices and warranty status for the caller, without hopping screens.",
  },
  {
    icon: "⏱",
    title: "SLA pulse on every row",
    bn: "প্রতিটি সারিতে এসএলএ",
    body: "First-response due time and breach state from the SLA engine, so the next contact is chosen by risk, not arrival order.",
  },
  {
    icon: "✍️",
    title: "Reply and mandatory wrap-up",
    bn: "রিপ্লাই ও বাধ্যতামূলক র‍্যাপ-আপ",
    body: "Record the agent reply on the transcript, then close through the disposition + substantive notes + FCR gate.",
  },
  {
    icon: "🔐",
    title: "Staff-only, transcript as record",
    bn: "শুধু কর্মীদের জন্য, ট্রান্সক্রিপ্টই রেকর্ড",
    body: "Internal users only, enforced at the data layer. Every turn, disposition and close is kept on the conversation record.",
  },
];

export default function LandingPage() {
  const { status, user } = useAuth();
  const signedInStaff = status === "signed-in" && user?.isInternal;

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
            1000 FiX · Contact Centre Console (P10)
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
            Every conversation,
            <br />
            one agent workspace.
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
            The internal console for hotline <strong>16743</strong>: claim contacts from the AI lane,
            answer with the customer&apos;s orders and devices in view, and close through the mandatory
            wrap-up gate. Signed in staff only — no demo or shared credential exists.
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            <a
              href={signedInStaff ? "/queue" : "/login"}
              style={{ ...primaryLinkStyle, minHeight: 44, padding: "12px 22px", textDecoration: "none" }}
            >
              {signedInStaff ? "Open the queue →" : "Staff sign in →"}
            </a>
            <a href="tel:16743" style={{ ...linkButtonStyle, minHeight: 44, padding: "12px 18px", textDecoration: "none" }}>
              ☎ Hotline 16743
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
            Console posture
          </div>
          {[
            ["Channels", "5 in one queue"],
            ["Handoff", "AI ↔ human, full context"],
            ["Wrap-up", "disposition + notes + FCR"],
            ["Access", "1000FiX staff only"],
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
              <span style={{ fontWeight: 600, color: tokens["color.text.primary"] }}>{v}</span>
            </div>
          ))}
        </div>
      </section>

      <section aria-label="What the console provides" style={{ padding: "34px 0 12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
          <h2 style={{ margin: 0, fontSize: tokens["typography.size.400"], color: tokens["color.text.primary"] }}>
            What the workspace provides
          </h2>
          <Badge tone="neutral">P10</Badge>
        </div>
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
        Internal system — access is logged against your 1000FiX ERP account. For access problems contact the
        service desk; for customer escalations use hotline 16743.
      </p>
    </main>
  );
}
