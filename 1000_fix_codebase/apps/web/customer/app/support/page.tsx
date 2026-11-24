"use client";

/**
 * P01 help & support — the public customer help surface.
 *
 * Static guidance only (hotline, hours, how service works, common questions).
 * It carries no ERP data and needs no session; anything that reads a
 * customer's records links to the protected pages instead.
 */
import Link from "next/link";
import { SectionHead, tokens } from "../../lib/imports";
import { useLanguage } from "../../components/language";

interface Faq {
  qEn: string;
  qBn: string;
  aEn: string;
  aBn: string;
}

const FAQS: Faq[] = [
  {
    qEn: "How do I know the repair status?",
    qBn: "মেরামতের অবস্থা কীভাবে জানব?",
    aEn: "Open Track service and enter your order reference, or use the tracking link sent by SMS. Signed-in customers also see every booking on the dashboard.",
    aBn: "‘ট্র্যাকিং’ পাতায় অর্ডার রেফারেন্স দিন, অথবা SMS-এ পাঠানো ট্র্যাকিং লিংক ব্যবহার করুন। সাইন-ইন করা গ্রাহকরা ড্যাশবোর্ডে সব বুকিং দেখতে পান।",
  },
  {
    qEn: "How do I approve an estimate?",
    qBn: "অনুমান কীভাবে অনুমোদন করব?",
    aEn: "Estimates awaiting your decision appear under Estimates & approvals. Approving records the reference OTP / e-signature / signed form required by our process.",
    aBn: "আপনার সিদ্ধান্তের অপেক্ষায় থাকা অনুমান ‘অনুমান ও অনুমোদন’ পাতায় দেখা যায়। অনুমোদনের সময় প্রয়োজনীয় OTP / ই-সাইন / স্বাক্ষরিত ফর্মের রেফারেন্স সংরক্ষিত হয়।",
  },
  {
    qEn: "Where is my invoice?",
    qBn: "আমার ইনভয়েস কোথায়?",
    aEn: "Issued invoices are listed under Invoices & payments with paid and outstanding amounts. Pay at any 1000 FiX service centre.",
    aBn: "ইস্যু করা ইনভয়েস ‘ইনভয়েস ও পেমেন্ট’ পাতায় পরিশোধিত ও বাকি টাকাসহ দেখা যায়। যেকোনো 1000 FiX সেন্টারে পরিশোধ করুন।",
  },
  {
    qEn: "How do I add or transfer a device?",
    qBn: "ডিভাইস কীভাবে যোগ বা হস্তান্তর করব?",
    aEn: "Register a device under My devices & warranty with its serial number or IMEI. Ownership transfer is available on the same page and is recorded in the device history.",
    aBn: "‘আমার ডিভাইস ও ওয়ারেন্টি’ পাতায় সিরিয়াল নম্বর বা IMEI দিয়ে ডিভাইস নিবন্ধন করুন। একই পাতায় মালিকানা হস্তান্তর করা যায় এবং তা ডিভাইস হিস্ট্রিতে সংরক্ষিত হয়।",
  },
  {
    qEn: "How do I stop marketing messages?",
    qBn: "মার্কেটিং বার্তা কীভাবে বন্ধ করব?",
    aEn: "Open Privacy & consent and withdraw the channels you no longer want. Withdrawal is recorded with its date, as required by PDPA 2026.",
    aBn: "‘গোপনীয়তা ও সম্মতি’ পাতায় যে চ্যানেল আর চান না তা প্রত্যাহার করুন। PDPA ২০২৬ অনুযায়ী তারিখসহ প্রত্যাহার সংরক্ষিত হয়।",
  },
];

export default function SupportPage() {
  const { locale } = useLanguage();
  const bn = locale === "bn";

  return (
    <main>
      <SectionHead
        title={bn ? "সহায়তা" : "Help & support"}
        note={bn ? "হটলাইন ২৪/৭ · সাধারণ প্রশ্নের উত্তর · শাখা নির্দেশনা" : "Hotline 24/7 · answers to common questions · branch guidance"}
      />

      <div className="grid-2" style={{ marginTop: 18 }}>
        <div className="fx-card">
          <h3>☎ {bn ? "হটলাইন" : "Hotline"}</h3>
          <p style={{ margin: "6px 0 10px", fontSize: tokens["typography.size.400"], fontWeight: 700 }}>
            <a href="tel:16743" style={{ color: tokens["color.primary.base"], textDecoration: "none" }}>16743</a>
          </p>
          <p className="muted" style={{ margin: 0, fontSize: tokens["typography.size.200"] }}>
            {bn
              ? "সপ্তাহে ৭ দিন, ২৪ ঘণ্টা। বুকিং, ট্র্যাকিং, ইনভয়েস ও ওয়ারেন্টি সংক্রান্ত যেকোনো প্রশ্নে কল করুন।"
              : "7 days a week, 24 hours. Call for anything about bookings, tracking, invoices or warranties."}
          </p>
        </div>
        <div className="fx-card">
          <h3>🏢 {bn ? "সার্ভিস সেন্টার" : "Service centres"}</h3>
          <p className="muted" style={{ margin: "6px 0 10px", fontSize: tokens["typography.size.200"] }}>
            {bn
              ? "৫১+ সেন্টার, ৮ বিভাগ। বুকিং করার সময় আপনার নিকটতম শাখা বেছে নিন — ওয়াক-ইন, পিকআপ ও অনসাইট সার্ভিস উপলব্ধ।"
              : "51+ centres across 8 divisions. Choose your nearest branch while booking — walk-in, pickup and onsite service are available."}
          </p>
          <Link className="btn btn-primary" href="/booking">{bn ? "সার্ভিস বুক করুন" : "Book a service"}</Link>
        </div>
      </div>

      <div className="fx-card" style={{ marginTop: 16 }}>
        <h3>{bn ? "সাধারণ প্রশ্ন" : "Common questions"}</h3>
        <div style={{ marginTop: 10, display: "grid", gap: 8 }}>
          {FAQS.map((f, i) => (
            <details key={i} style={{ border: `1px solid ${tokens["color.border.default"]}`, borderRadius: tokens["dimension.border.radius-sm"], padding: "10px 12px" }}>
              <summary style={{ cursor: "pointer", fontWeight: 600 }}>{bn ? f.qBn : f.qEn}</summary>
              <p className="muted" style={{ margin: "8px 0 0", fontSize: tokens["typography.size.200"] }}>
                {bn ? f.aBn : f.aEn}
              </p>
            </details>
          ))}
        </div>
      </div>

      <p className="footer-note">
        {bn ? "জরুরি নিরাপত্তা বা গোপনীয়তা ইস্যু?" : "Urgent security or privacy issue?"}{" "}
        <a href="tel:16743">16743</a>
        {" · "}
        {bn ? "অথবা" : "or"}{" "}
        <Link href="/consent">{bn ? "গোপনীয়তা ও সম্মতি" : "Privacy & consent"}</Link>
      </p>
    </main>
  );
}
