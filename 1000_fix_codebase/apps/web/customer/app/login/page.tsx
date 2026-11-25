"use client";

/**
 * Customer sign-in — the only way into the P01 portal.
 *
 * Two customer-friendly paths, both Odoo-backed:
 * - Mobile OTP: verifies the phone and signs into the customer's OWN portal
 *   account (created on first use by the backend).
 * - Password: for customers who already have portal credentials.
 *
 * Staff/administrator accounts are refused here (lib/auth.ts) — the customer
 * portal is not the operations portal. There is no demo/shared login.
 */
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "../../components/language";
import { useAuth } from "../../components/auth-modal";
import { login, sendOtp, loginWithOtp } from "../../lib/auth";

/** Return path supplied by the route guard / proxy (/login?next=/invoices). */
function nextPath(): string {
  if (typeof window === "undefined") return "/dashboard";
  const raw = new URLSearchParams(window.location.search).get("next") || "/dashboard";
  // Only same-site paths — never an absolute URL from the query string.
  if (!raw.startsWith("/") || raw.startsWith("//")) return "/dashboard";
  return raw;
}

export default function LoginPage() {
  const { t, locale } = useLanguage();
  const { user, refreshUser } = useAuth();
  const router = useRouter();

  const [tab, setTab] = useState<"otp" | "password">("otp");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // OTP state
  const [phone, setPhone] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [digits, setDigits] = useState(["", "", "", "", "", ""]);
  const [devCode, setDevCode] = useState<string | null>(null);
  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Password state
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const bn = locale === "bn";

  useEffect(() => {
    if (user) router.replace(nextPath());
  }, [user, router]);

  const setDigit = (i: number, v: string) => {
    const clean = v.replace(/\D/g, "");
    if (clean.length > 1) {
      // paste: distribute
      const next = [...digits];
      clean.slice(0, 6 - i).split("").forEach((d, k) => (next[i + k] = d));
      setDigits(next);
      otpRefs.current[Math.min(i + clean.length, 5)]?.focus();
      return;
    }
    const next = [...digits];
    next[i] = clean;
    setDigits(next);
    if (clean && i < 5) otpRefs.current[i + 1]?.focus();
  };

  const onDigitKey = (i: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !digits[i] && i > 0) otpRefs.current[i - 1]?.focus();
  };

  const handleSendOtp = async () => {
    setBusy(true);
    setError(null);
    try {
      const res = await sendOtp(phone);
      setOtpSent(true);
      setDevCode(res.dev_code ?? null);
      if (res.dev_code) setDigits(res.dev_code.split(""));
      setNotice(t.authOtpSentNotice(res.masked_phone));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const handleVerifyOtp = async () => {
    const code = digits.join("");
    if (code.length !== 6) {
      setError(bn ? "৬-সংখ্যার কোড দিন" : "Enter the 6-digit code");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await loginWithOtp(phone, code);
      await refreshUser();
      router.replace(nextPath());
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const handlePassword = async () => {
    setBusy(true);
    setError(null);
    try {
      await login(username, password);
      await refreshUser();
      router.replace(nextPath());
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="login-split" data-testid="login-page">
      <aside className="login-brand">
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span className="tb-logo" style={{ width: 40, height: 40, fontSize: 20, borderRadius: 10 }} aria-hidden>F</span>
          <div>
            <strong style={{ fontSize: 15 }}>1000 FiX</strong>
            <div style={{ fontSize: 10, opacity: 0.7, letterSpacing: "0.08em" }}>CUSTOMER PORTAL</div>
          </div>
        </div>
        <h1>
          {bn ? <>আপনার সার্ভিস, <br />আপনার হাতে।</> : <>Your service, <br />in your hands.</>}
        </h1>
        <p className="lb-sub">
          {bn
            ? "আপনার মেরামত, অনুমান, ইনভয়েস, ডিভাইস ওয়ারেন্টি ও গোপনীয়তা পছন্দ — সব এক অ্যাকাউন্টে। শুধুমাত্র আপনার নিজের রেকর্ড।"
            : "Your repairs, estimates, invoices, device warranties and privacy choices — all in one account. Only your own records."}
        </p>
        <div className="lb-facts">
          <div><b>16743</b><span>{bn ? "হটলাইন" : "Hotline"}</span></div>
          <div><b>ISO 9001</b><span>{bn ? "সার্টিফায়েড" : "Certified"}</span></div>
          <div><b>51+</b><span>{bn ? "সেন্টার" : "Centres"}</span></div>
        </div>
        <div className="lb-foot">
          {bn ? "৫১+ সেন্টার · ৮ বিভাগ · © ২০২৬" : "51+ centres · 8 divisions · © 2026"}
        </div>
      </aside>

      <section className="login-form-wrap">
        <div className="login-card">
          <h2>{bn ? "সাইন ইন" : "Sign in"}</h2>
          <p className="login-sub">
            {bn
              ? "আপনার মোবাইল নম্বর দিয়ে OTP নিন — অথবা পোর্টাল পাসওয়ার্ড ব্যবহার করুন।"
              : "Use a one-time code sent to your mobile, or your existing portal password."}
          </p>

          <div className="tabs" role="tablist">
            <button role="tab" aria-selected={tab === "otp"} className={`tab-btn${tab === "otp" ? " active" : ""}`} onClick={() => { setTab("otp"); setError(null); }}>
              📱 {bn ? "মোবাইল OTP" : "Mobile OTP"}
            </button>
            <button role="tab" aria-selected={tab === "password"} className={`tab-btn${tab === "password" ? " active" : ""}`} onClick={() => { setTab("password"); setError(null); }}>
              🔑 {bn ? "পাসওয়ার্ড" : "Password"}
            </button>
          </div>

          {tab === "otp" && (
            <div>
              {!otpSent ? (
                <form
                  className="field"
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendOtp();
                  }}
                >
                  <label htmlFor="login-phone">{t.authPhoneLabel}</label>
                  <input
                    id="login-phone"
                    type="tel"
                    required
                    autoComplete="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder={t.authPhonePlaceholder}
                    style={{ marginBottom: 10 }}
                  />
                  <small className="muted" style={{ marginBottom: 12 }}>
                    {bn ? "বাংলাদেশের ১১-সংখ্যার সক্রিয় মোবাইল নম্বর (01XXXXXXXXX)।" : "Any active 11-digit Bangladesh mobile number (01XXXXXXXXX)."}
                  </small>
                  <button className="btn btn-primary" type="submit" disabled={busy}>
                    {busy ? (bn ? "পাঠানো হচ্ছে…" : "Sending…") : t.authSendOtpBtn}
                  </button>
                </form>
              ) : (
                <div>
                  {notice && (
                    <p className="st info" style={{ display: "block", padding: "6px 10px", marginBottom: 4 }}>
                      {notice}
                      {devCode && <span className="mono" style={{ marginLeft: 8 }}>[dev: {devCode}]</span>}
                    </p>
                  )}
                  <div className="fx-otp" data-testid="otp-row">
                    {digits.map((d, i) => (
                      <input
                        key={i}
                        ref={(el) => {
                          otpRefs.current[i] = el;
                        }}
                        inputMode="numeric"
                        autoComplete={i === 0 ? "one-time-code" : "off"}
                        maxLength={6}
                        value={d}
                        onChange={(e) => setDigit(i, e.target.value)}
                        onKeyDown={(e) => onDigitKey(i, e)}
                        aria-label={`OTP ${i + 1}`}
                      />
                    ))}
                  </div>
                  <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
                    <button className="btn btn-primary" style={{ flex: 1, justifyContent: "center" }} disabled={busy} onClick={handleVerifyOtp}>
                      {busy ? (bn ? "যাচাই হচ্ছে…" : "Verifying…") : t.authVerifyOtpBtn}
                    </button>
                    <button className="btn" onClick={() => { setOtpSent(false); setDigits(["", "", "", "", "", ""]); setNotice(null); }}>
                      {bn ? "পরিবর্তন" : "Change"}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {tab === "password" && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handlePassword();
              }}
              style={{ display: "flex", flexDirection: "column", gap: 12 }}
            >
              <div className="field">
                <label htmlFor="login-user">{bn ? "ব্যবহারকারী নাম / ইমেইল" : "Username / Email"}</label>
                <input id="login-user" type="text" required autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} />
              </div>
              <div className="field">
                <label htmlFor="login-pass">{bn ? "পাসওয়ার্ড" : "Password"}</label>
                <input id="login-pass" type="password" required autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
              </div>
              <button className="btn btn-primary" type="submit" disabled={busy} style={{ justifyContent: "center" }}>
                {busy ? (bn ? "যাচাই হচ্ছে…" : "Signing in…") : bn ? "সাইন ইন ✓" : "Sign in ✓"}
              </button>
            </form>
          )}

          {error && (
            <p className="st err" role="alert" style={{ display: "block", padding: "6px 10px", marginTop: 12 }}>
              {error}
            </p>
          )}

          <p className="login-foot">
            <Link href="/">{bn ? "← পোর্টালে ফিরুন" : "← Back to the portal"}</Link>
            {" · "}
            <Link href="/support">{bn ? "সহায়তা" : "Help"}</Link>
          </p>
          <p className="login-foot" style={{ marginTop: 8 }}>
            {bn
              ? "এই পোর্টালটি গ্রাহকদের জন্য। কর্মী/অ্যাডমিন অ্যাকাউন্ট অপারেশনস পোর্টাল (P03) দিয়ে সাইন ইন করুন।"
              : "This portal is for customers. Staff and administrator accounts sign in through the operations portal (P03)."}
          </p>
        </div>
      </section>
    </main>
  );
}
