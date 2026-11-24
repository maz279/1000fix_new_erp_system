"use client";

/**
 * Corporate client sign-in. One way in to the B2B portal: account
 * credentials checked against Odoo through the same-origin bridge. Staff and
 * administrator accounts are refused (server-side and here), and no demo or
 * shared credential is offered. SSO is a deployment option; it is not shown
 * as a dead button when the OIDC routes are not configured.
 */
import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { tokens } from "../../lib/imports";
import { useLanguage } from "../../components/language";
import { useAuth } from "../../components/auth-modal";

function nextPath(): string {
  if (typeof window === "undefined") return "/dashboard";
  const raw = new URLSearchParams(window.location.search).get("next") || "/dashboard";
  if (!raw.startsWith("/") || raw.startsWith("//")) return "/dashboard";
  return raw;
}

export default function CorporateLoginPage() {
  const { locale } = useLanguage();
  const { user, loginWithCredentials, refreshUser } = useAuth();
  const router = useRouter();
  const bn = locale === "bn";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) router.replace(nextPath());
  }, [user, router]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await loginWithCredentials(username, password);
      await refreshUser();
      router.replace(nextPath());
    } catch (err) {
      setError((err as Error).message || "Authentication failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main
      style={{
        display: "grid",
        gridTemplateColumns: "minmax(340px, 44%) 1fr",
        minHeight: "calc(100vh - 60px)",
      }}
    >
      <aside
        style={{
          padding: "48px 46px",
          color: tokens["color.text.inverse"],
          background: `linear-gradient(160deg, ${tokens["color.primary.hover"]}, ${tokens["color.primary.base"]})`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          gap: 14,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span
            aria-hidden
            style={{
              width: 38,
              height: 38,
              borderRadius: 10,
              background: "rgba(255,255,255,0.16)",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 700,
            }}
          >
            F
          </span>
          <div>
            <strong style={{ fontSize: 15 }}>1000 FiX</strong>
            <div style={{ fontSize: 10, opacity: 0.75, letterSpacing: "0.08em" }}>CORPORATE B2B PORTAL</div>
          </div>
        </div>
        <h1 style={{ margin: 0, fontSize: tokens["typography.size.500"], lineHeight: 1.22, color: "#fff" }}>
          {bn ? (
            <>আপনার কর্পোরেট সার্ভিস, <br />আপনার নিয়ন্ত্রণে।</>
          ) : (
            <>Your corporate service, <br />in your control.</>
          )}
        </h1>
        <p style={{ margin: 0, fontSize: 13, lineHeight: 1.65, opacity: 0.88, maxWidth: "44ch" }}>
          {bn
            ? "মাল্টি-সাইট ডিভাইস বহর, চুক্তি ও এসএলএ, কনসোলিডেটেড বিলিং, বাল্ক সার্ভিস রিকোয়েস্ট, টেন্ডার ও রিপোর্ট — শুধুমাত্র আপনার অ্যাকাউন্টের ডেটা।"
            : "Multi-site estate, contracts and SLAs, consolidated billing, bulk service requests, tenders and reports — only your account's data."}
        </p>
        <div style={{ display: "flex", gap: 24, marginTop: 12, flexWrap: "wrap" }}>
          <div><b style={{ display: "block", fontSize: 18, color: "#fff" }}>ISO 9001:2015</b><span style={{ fontSize: 10.5, opacity: 0.75 }}>{bn ? "সার্টিফায়েড" : "Certified"}</span></div>
          <div><b style={{ display: "block", fontSize: 18, color: "#fff" }}>51+</b><span style={{ fontSize: 10.5, opacity: 0.75 }}>{bn ? "সেন্টার" : "Centres"}</span></div>
          <div><b style={{ display: "block", fontSize: 18, color: "#fff" }}>24/7</b><span style={{ fontSize: 10.5, opacity: 0.75 }}>{bn ? "এসএলএ" : "SLA"}</span></div>
        </div>
      </aside>

      <section style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: 24, background: tokens["color.surface.canvas"] }}>
        <div style={{ width: "min(420px, 100%)" }}>
          <h2 style={{ margin: "0 0 6px", fontSize: tokens["typography.size.400"], color: tokens["color.text.primary"] }}>
            {bn ? "কর্পোরেট সাইন ইন" : "Corporate sign in"}
          </h2>
          <p style={{ margin: "0 0 18px", fontSize: 12.5, lineHeight: 1.55, color: tokens["color.text.secondary"] }}>
            {bn
              ? "আপনার কর্পোরেট অ্যাকাউন্টের ইমেইল ও পাসওয়ার্ড ব্যবহার করুন।"
              : "Use the email and password of your corporate portal account."}
          </p>

          <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div>
              <label htmlFor="corp-user" style={{ display: "block", marginBottom: 5, fontSize: 12, fontWeight: 600, color: tokens["color.text.primary"] }}>
                {bn ? "ইমেইল / ব্যবহারকারী নাম" : "Email / username"}
              </label>
              <input
                id="corp-user"
                type="text"
                autoComplete="username"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  padding: "9px 12px",
                  border: `1px solid ${tokens["color.border.default"]}`,
                  borderRadius: tokens["dimension.border.radius-sm"],
                  background: tokens["color.surface.primary"],
                  color: tokens["color.text.primary"],
                  fontSize: tokens["typography.size.200"],
                }}
              />
            </div>
            <div>
              <label htmlFor="corp-pass" style={{ display: "block", marginBottom: 5, fontSize: 12, fontWeight: 600, color: tokens["color.text.primary"] }}>
                {bn ? "পাসওয়ার্ড" : "Password"}
              </label>
              <input
                id="corp-pass"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  padding: "9px 12px",
                  border: `1px solid ${tokens["color.border.default"]}`,
                  borderRadius: tokens["dimension.border.radius-sm"],
                  background: tokens["color.surface.primary"],
                  color: tokens["color.text.primary"],
                  fontSize: tokens["typography.size.200"],
                }}
              />
            </div>
            <button
              type="submit"
              disabled={busy}
              style={{
                marginTop: 4,
                padding: "10px 16px",
                border: "none",
                borderRadius: tokens["dimension.border.radius-sm"],
                background: tokens["color.primary.base"],
                color: tokens["color.text.inverse"],
                fontSize: tokens["typography.size.200"],
                fontWeight: 600,
                cursor: busy ? "wait" : "pointer",
                opacity: busy ? 0.7 : 1,
              }}
            >
              {busy ? (bn ? "যাচাই হচ্ছে…" : "Signing in…") : bn ? "সাইন ইন" : "Sign in"}
            </button>
          </form>

          {error && (
            <div
              role="alert"
              style={{
                marginTop: 12,
                padding: "8px 10px",
                borderRadius: tokens["dimension.border.radius-sm"],
                background: tokens["color.status.error-bg"],
                color: tokens["color.status.error"],
                border: `1px solid ${tokens["color.status.error"]}`,
                fontSize: 12.5,
              }}
            >
              {error}
            </div>
          )}

          <p style={{ marginTop: 16, fontSize: 11.5, lineHeight: 1.6, color: tokens["color.text.secondary"] }}>
            {bn ? "অ্যাক্সেস দরকার?" : "Need access?"}{" "}
            {bn
              ? "আপনার অ্যাকাউন্ট ম্যানেজার অথবা হটলাইন ১৬৭৪৩-এ যোগাযোগ করুন।"
              : "Contact your account manager or hotline 16743."}
          </p>
          <p style={{ marginTop: 8, fontSize: 11, lineHeight: 1.6, color: tokens["color.text.secondary"] }}>
            {bn
              ? "এই পোর্টাল কর্পোরেট ক্লায়েন্টদের জন্য। কর্মী/অ্যাডমিন অ্যাকাউন্ট অপারেশনস পোর্টাল (P03) ব্যবহার করবে।"
              : "This portal is for corporate clients. Staff and administrator accounts use the operations portal (P03)."}
          </p>
          <p style={{ marginTop: 12, fontSize: 11.5 }}>
            <Link href="/" style={{ color: tokens["color.primary.base"], textDecoration: "none", fontWeight: 600 }}>
              {bn ? "← পোর্টালে ফিরুন" : "← Back to the portal"}
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
