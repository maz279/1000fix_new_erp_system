"use client";

/**
 * P01 public landing / sign-in page.
 *
 * This is the customer portal's front door: an unauthenticated visitor sees
 * what the portal gives them (their own service requests, estimates,
 * invoices, devices and privacy choices) and a single way in — sign in or
 * book with the hotline. The dashboard behind /dashboard is customer-only
 * and never rendered before the Odoo session is verified (RequireAuth).
 */
import Link from "next/link";
import { useLanguage } from "../components/language";
import { useAuth } from "../components/auth-modal";

interface Feature {
  icon: string;
  href: string;
  en: string;
  bn: string;
  descEn: string;
  descBn: string;
  auth: boolean;
}

const FEATURES: Feature[] = [
  {
    icon: "🏠",
    href: "/dashboard",
    en: "My service requests",
    bn: "আমার সার্ভিস অর্ডার",
    descEn: "Every repair, its current stage and the technician assigned to it.",
    descBn: "প্রতিটি মেরামত, এর বর্তমান ধাপ ও assigned টেকনিশিয়ান।",
    auth: true,
  },
  {
    icon: "📅",
    href: "/booking",
    en: "Book a service",
    bn: "সার্ভিস বুকিং",
    descEn: "Choose your device, fault, branch and a morning / afternoon / evening slot.",
    descBn: "ডিভাইস, ত্রুটি, শাখা ও সকাল/বিকাল/সন্ধ্যার সময় বেছে নিন।",
    auth: true,
  },
  {
    icon: "📍",
    href: "/tracking",
    en: "Track a repair",
    bn: "মেরামত ট্র্যাক করুন",
    descEn: "Follow intake, diagnosis, bench repair, QC and delivery — or use your SMS link.",
    descBn: "ইন্ট্যাক, ডায়াগনস্টিক, বেঞ্চ মেরামত, QC ও ডেলিভারি দেখুন — বা SMS লিংক ব্যবহার করুন।",
    auth: false,
  },
  {
    icon: "🧾",
    href: "/estimates",
    en: "Estimates & approvals",
    bn: "অনুমান ও অনুমোদন",
    descEn: "Review priced parts and labour, then approve or reject with a documented reference.",
    descBn: "যন্ত্রাংশ ও শ্রমের মূল্য দেখে ডকুমেন্টেড রেফারেন্সসহ অনুমোদন বা প্রত্যাখ্যান করুন।",
    auth: true,
  },
  {
    icon: "💳",
    href: "/invoices",
    en: "Invoices & payments",
    bn: "ইনভয়েস ও পেমেন্ট",
    descEn: "Every issued invoice, what is paid and what is still due.",
    descBn: "প্রতিটি ইস্যু করা ইনভয়েস, পরিশোধিত ও বাকি টাকা।",
    auth: true,
  },
  {
    icon: "📱",
    href: "/devices",
    en: "Devices & warranty",
    bn: "ডিভাইস ও ওয়ারেন্টি",
    descEn: "Your registered devices, warranty status, service history and ownership transfer.",
    descBn: "নিবন্ধিত ডিভাইস, ওয়ারেন্টি স্ট্যাটাস, সার্ভিস হিস্ট্রি ও মালিকানা হস্তান্তর।",
    auth: true,
  },
  {
    icon: "🔐",
    href: "/consent",
    en: "Privacy & consent",
    bn: "গোপনীয়তা ও সম্মতি",
    descEn: "See and change which channels 1000 FiX may use to contact you — PDPA 2026.",
    descBn: "১০০০ FiX কোন চ্যানেলে যোগাযোগ করতে পারবে তা দেখুন ও পরিবর্তন করুন — PDPA ২০২৬।",
    auth: true,
  },
  {
    icon: "🎧",
    href: "/support",
    en: "Help & support",
    bn: "সহায়তা",
    descEn: "Hotline, service hours, branch guidance and answers to common questions.",
    descBn: "হটলাইন, সার্ভিস সময়, শাখা নির্দেশনা ও সাধারণ প্রশ্নের উত্তর।",
    auth: false,
  },
];

const STEPS = [
  { n: "1", en: "Book or call 16743", bn: "বুক করুন বা ১৬৭৪৩-এ কল করুন" },
  { n: "2", en: "Drop off or request pickup", bn: "ড্রপ-অফ করুন বা পিকআপ চান" },
  { n: "3", en: "Approve the estimate", bn: "অনুমান অনুমোদন করুন" },
  { n: "4", en: "Track the repair live", bn: "লাইভ মেরামত ট্র্যাক করুন" },
  { n: "5", en: "Pay and collect", bn: "পেমেন্ট করে ডিভাইস নিন" },
];

export default function LandingPage() {
  const { locale } = useLanguage();
  const { user } = useAuth();
  const bn = locale === "bn";

  return (
    <main className="lp">
      <section className="hero-band lp-hero" aria-labelledby="lp-title">
        <div className="lp-hero-copy">
          <p className="lp-eyebrow">
            {bn ? "১০০০ FiX · কাস্টমার পোর্টাল" : "1000 FiX · CUSTOMER PORTAL"}
          </p>
          <h1 id="lp-title">
            {bn ? (
              <>আপনার সার্ভিস, <br />এক জায়গায়।</>
            ) : (
              <>Your service, <br />all in one place.</>
            )}
          </h1>
          <p className="lp-lede">
            {bn
              ? "মেরামত বুক করুন, লাইভ ফলো করুন, অনুমান অনুমোদন করুন, ইনভয়েস দেখুন এবং ডিভাইস-ওয়ারেন্টি পরিচালনা করুন — ২৪/৭।"
              : "Book a repair, follow it live, approve estimates, view invoices and manage your devices and warranties — 24/7."}
          </p>
          <div className="lp-actions">
            <Link className="btn btn-primary lp-btn-lg" href={user ? "/dashboard" : "/login"}>
              {user
                ? bn
                  ? `আমার ড্যাশবোর্ডে যান${user.name ? ` · ${user.name}` : ""}`
                  : `Open my dashboard${user.name ? ` · ${user.name}` : ""}`
                : bn
                  ? "আমার অ্যাকাউন্টে সাইন ইন করুন"
                  : "Sign in to my account"}
            </Link>
            <Link className="btn lp-btn-lg lp-btn-ghost" href="/tracking">
              {bn ? "মেরামত ট্র্যাক করুন →" : "Track a repair →"}
            </Link>
          </div>
          <p className="lp-note">
            {bn
              ? "নতুন গ্রাহক? ১৬৭৪৩ হটলাইনে বুক করুন, অথবা মোবাইল নম্বর দিয়ে OTP সাইন-ইন করুন — অ্যাকাউন্ট তৈরি হয়ে যাবে।"
              : "New customer? Book on hotline 16743, or sign in with your mobile number via OTP — your account is created on first use."}
          </p>
        </div>
        <div className="lp-hero-aside" aria-label={bn ? "পোর্টালের সুবিধা" : "Portal facts"}>
          <div className="lp-stat">
            <b>16743</b>
            <span>{bn ? "হটলাইন" : "Hotline"}</span>
          </div>
          <div className="lp-stat">
            <b>ISO 9001:2015</b>
            <span>{bn ? "সার্টিফায়েড সার্ভিস" : "Certified service"}</span>
          </div>
          <div className="lp-stat">
            <b>51+</b>
            <span>{bn ? "সার্ভিস সেন্টার" : "Service centres"}</span>
          </div>
          <div className="lp-stat">
            <b>8</b>
            <span>{bn ? "বিভাগ" : "Divisions"}</span>
          </div>
        </div>
      </section>

      <section className="lp-section" aria-labelledby="lp-features-title">
        <div className="lp-section-head">
          <h2 id="lp-features-title">{bn ? "আপনি যা করতে পারবেন" : "What you can do"}</h2>
          <p>
            {bn
              ? "সবকিছু আপনার নিজের অ্যাকাউন্টের মধ্যে সীমাবদ্ধ — অন্য গ্রাহকের ডেটা বা অভ্যন্তরীণ ERP কখনও নয়।"
              : "Everything is scoped to your own account — never another customer's data, never the internal ERP."}
          </p>
        </div>
        <div className="lp-grid">
          {FEATURES.map((f) => (
            <Link key={f.href} className="lp-card" href={f.href}>
              <span className="lp-card-icon" aria-hidden>{f.icon}</span>
              <strong>{bn ? f.bn : f.en}</strong>
              <span className="lp-card-desc">{bn ? f.descBn : f.descEn}</span>
              {f.auth && !user ? (
                <span className="lp-card-tag">{bn ? "সাইন-ইন প্রয়োজন" : "Sign-in required"}</span>
              ) : null}
            </Link>
          ))}
        </div>
      </section>

      <section className="lp-section" aria-labelledby="lp-steps-title">
        <div className="lp-section-head">
          <h2 id="lp-steps-title">{bn ? "সার্ভিস কীভাবে কাজ করে" : "How service works"}</h2>
        </div>
        <ol className="lp-steps">
          {STEPS.map((s) => (
            <li key={s.n}>
              <b>{s.n}</b>
              <span>{bn ? s.bn : s.en}</span>
            </li>
          ))}
        </ol>
      </section>

      <section className="lp-section lp-help" aria-labelledby="lp-help-title">
        <div>
          <h2 id="lp-help-title">{bn ? "সাহায্য দরকার?" : "Need a hand?"}</h2>
          <p>
            {bn
              ? "আমাদের হটলাইন ২৪/৭ খোলা। অথবা সহায়তা পাতায় সাধারণ প্রশ্নের উত্তর দেখুন।"
              : "Our hotline is open around the clock. Or see the answers to common questions on the support page."}
          </p>
        </div>
        <div className="lp-help-actions">
          <a className="btn btn-primary lp-btn-lg" href="tel:16743">☎ 16743</a>
          <Link className="btn lp-btn-lg lp-btn-ghost" href="/support">
            {bn ? "সহায়তা দেখুন" : "Visit help & support"}
          </Link>
        </div>
      </section>

      <p className="lp-foot">
        {bn
          ? "১০০০ FiX Services Ltd. · ISO 9001:2015 · PDPA ২০২৬ গোপনীয়তা নীতি · কর্মীদের জন্য: অপারেশনস পোর্টাল (P03)"
          : "1000 FiX Services Ltd. · ISO 9001:2015 · PDPA 2026 privacy notice · Staff: use the operations portal (P03)"}
      </p>
    </main>
  );
}
