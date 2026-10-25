"use client";

/**
 * Dedicated sign-in page — ported from the frozen prototype login.html
 * (Front_end/css/landing.css § login): split-screen brand panel (deep-teal
 * gradient + sunset glow, Sora display type, 823/346/12 facts) with the
 * form card on the right; OTP presented as the prototype's 6-box TOTP row;
 * demo persona one-click; SSO row (federation is P04-side, shown disabled).
 * Auth is same-origin through /api/odoo (lib/auth.ts).
 */
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "../../components/language";
import { useAuth } from "../../components/auth-modal";
import { login, sendOtp, loginWithOtp } from "../../lib/auth";

export default function LoginPage() {
  const { t, locale } = useLanguage();
  const { user, refreshUser } = useAuth();
  const router = useRouter();

  const [tab, setTab] = useState<"otp" | "password">("otp");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // OTP state
  const [phone, setPhone] = useState("01711223344");
  const [otpSent, setOtpSent] = useState(false);
  const [digits, setDigits] = useState(["", "", "", "", "", ""]);
  const [devCode, setDevCode] = useState<string | null>(null);
  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Password state
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin");

  const bn = locale === "bn";

  useEffect(() => {
    if (user) router.replace("/");
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
      router.replace("/");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const handlePassword = async (u = username, p = password) => {
    setBusy(true);
    setError(null);
    try {
      await login(u, p);
      await refreshUser();
      router.replace("/");
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
            <strong style={{ fontSize: 15 }}>1000 FiX ERP</strong>
            <div style={{ fontSize: 10, opacity: 0.7, letterSpacing: "0.08em" }}>SERVICE OPERATIONS PLATFORM</div>
          </div>
        </div>
        <h1>
          {bn ? <>এক প্ল্যাটফর্ম, <br />প্রতিটি সার্ভিস মুহূর্ত।</> : <>One platform, <br />every service moment.</>}
        </h1>
        <p className="lb-sub">
          {bn
            ? "হটলাইন ১৬৭৪৩ থেকে ওয়ার্কশপ বেঞ্চ পর্যন্ত — ৬৭ মডিউল, ১২ পোর্টাল, প্রতিটি গ্রাহক ও ডিভাইসের একটি গোল্ডেন রেকর্ড।"
            : "Hotline 16743 to workshop bench — 67 modules, 12 portals, one golden record per customer and device."}
        </p>
        <div className="lb-facts">
          <div><b>823</b><span>{bn ? "স্ক্রিন" : "screens"}</span></div>
          <div><b>346</b><span>{bn ? "রিপোর্ট" : "reports"}</span></div>
          <div><b>12</b><span>{bn ? "পোর্টাল" : "portals"}</span></div>
        </div>
        <div className="lb-foot">
          ISO 9001:2015 · 51+ {bn ? "সেন্টার" : "centres"} · 8 {bn ? "বিভাগ" : "divisions"} · © 2026
        </div>
      </aside>

      <section className="login-form-wrap">
        <div className="login-card">
          <h2>{bn ? "সাইন ইন" : "Sign in"}</h2>
          <p className="login-sub">
            {bn
              ? "আপনার ১০০০ FiX ক্রেডেনশিয়াল ব্যবহার করুন — OTP বা পাসওয়ার্ড।"
              : "Use your 1000 FiX credentials — OTP or password."}
          </p>

          <div className="demo-box">
            <span aria-hidden>👤</span>
            <span className="persona">
              <b>{bn ? "ডেমো অ্যাডমিন" : "Demo admin"}</b>
              {bn ? "এক ক্লিকে প্রবেশ (admin/admin)" : "One-click sign in (admin/admin)"}
            </span>
            <button className="btn btn-hero" disabled={busy} onClick={() => handlePassword("admin", "admin")}>
              {bn ? "ডেমো হিসেবে সাইন ইন ▸" : "Sign in as demo ▸"}
            </button>
          </div>

          <div className="tabs" role="tablist">
            <button role="tab" aria-selected={tab === "otp"} className={`tab-btn${tab === "otp" ? " active" : ""}`} onClick={() => { setTab("otp"); setError(null); }}>
              📱 {bn ? "মোবাইল ওটিপি" : "Mobile OTP"}
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
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder={t.authPhonePlaceholder}
                    style={{ marginBottom: 10 }}
                  />
                  <small className="muted" style={{ marginBottom: 12 }}>
                    {bn ? "বাংলাদেশের ১১-সংখ্যার যেকোনো সক্রিয় মোবাইল নম্বর।" : "Any active 11-digit Bangladesh mobile number."}
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
                <input id="login-user" type="text" required value={username} onChange={(e) => setUsername(e.target.value)} />
              </div>
              <div className="field">
                <label htmlFor="login-pass">{bn ? "পাসওয়ার্ড" : "Password"}</label>
                <input id="login-pass" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
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

          <div className="sso-row">
            <button className="btn" disabled title={bn ? "করপোরেট ফেডারেশন (P04/M29)" : "Corporate federation (P04/M29)"}>
              Microsoft SSO
            </button>
            <button className="btn" disabled title={bn ? "করপোরেট ফেডারেশন (P04/M29)" : "Corporate federation (P04/M29)"}>
              Google SSO
            </button>
          </div>

          <p className="login-foot">
            <Link href="/">{bn ? "← পোর্টালে ফিরুন" : "← Back to portal"}</Link>
            {" · "}
            {bn ? "শর্তাবলি · PDPA ২০২৬ গোপনীয়তা নীতি" : "Terms · PDPA 2026 privacy notice"}
          </p>
        </div>
      </section>
    </main>
  );
}
