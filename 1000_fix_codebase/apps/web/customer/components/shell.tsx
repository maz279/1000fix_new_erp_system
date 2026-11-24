"use client";

/**
 * P01 app wrapper around the shared Service-Teal Fluent shell.
 *
 * The customer portal exposes CUSTOMER-ACCOUNT functions only: my service
 * requests, booking, live tracking, estimates and approvals, invoices,
 * registered devices and warranty, privacy consent and help. The ERP areas
 * and the embedded operations workspace are not part of this portal (they
 * live in P03 for staff), so the shell payload carries no module tree.
 *
 * Supplies the bilingual chrome copy from the app dictionary, the portal
 * sections, and mounts the app controls (language / theme / auth) into the
 * command bar's right slot.
 */
import type { ShellCopy, ShellSection } from "../lib/imports";
import { Shell } from "../lib/imports";
import { useLanguage, LanguageToggle } from "./language";
import { ThemeToggles } from "./theme";
import { AuthControls } from "./auth-modal";

/** Customer-account navigation — every destination is scoped to the
 * signed-in customer's own records. */
const SECTIONS: ShellSection[] = [
  { href: "/dashboard", en: "My dashboard", bn: "আমার ড্যাশবোর্ড", icon: "🏠" },
  { href: "/booking", en: "Book a service", bn: "সার্ভিস বুকিং", icon: "📅" },
  { href: "/tracking", en: "Track service", bn: "ট্র্যাকিং", icon: "📍" },
  { href: "/estimates", en: "Estimates & approvals", bn: "অনুমান ও অনুমোদন", icon: "🧾" },
  { href: "/invoices", en: "Invoices & payments", bn: "ইনভয়েস ও পেমেন্ট", icon: "💳" },
  { href: "/devices", en: "My devices & warranty", bn: "আমার ডিভাইস ও ওয়ারেন্টি", icon: "📱" },
  { href: "/consent", en: "Privacy & consent", bn: "গোপনীয়তা ও সম্মতি", icon: "🔐" },
  { href: "/support", en: "Help & support", bn: "সহায়তা", icon: "🎧" },
];

const COPY: Record<"bn" | "en", ShellCopy> = {
  bn: {
    searchPlaceholder: "পোর্টাল পাতা খুঁজুন… (Alt+Q)",
    portalZone: "কাস্টমার অ্যাকাউন্ট",
    erpZone: "",
    systemZone: "",
    home: "হোম",
    recents: "সাম্প্রতিক",
    online: "সার্ভিস সংযুক্ত",
    offline: "সার্ভিস বিচ্ছিন্ন",
    company: "1000 FiX Services Ltd.",
    opsLabel: "",
    portalsLabel: "",
    tellmePages: "পোর্টাল পাতা",
    tellmeModules: "",
    tellmeScreens: "",
    tellmeEmpty: "কিছু পাওয়া যায়নি — পাতার নাম লিখুন",
    closeTab: "ট্যাব বন্ধ",
  },
  en: {
    searchPlaceholder: "Search portal pages… (Alt+Q)",
    portalZone: "Customer account",
    erpZone: "",
    systemZone: "",
    home: "Home",
    recents: "Recents",
    online: "Service online",
    offline: "Service offline",
    company: "1000 FiX Services Ltd.",
    opsLabel: "",
    portalsLabel: "",
    tellmePages: "Portal pages",
    tellmeModules: "",
    tellmeScreens: "",
    tellmeEmpty: "No matches — try a page name",
    closeTab: "Close tab",
  },
};

export function CustomerShell({ children }: { children: React.ReactNode }) {
  const { locale, t } = useLanguage();
  return (
    <Shell
      brandWord={t.portalTitle}
      brandSub="P01 · Customer Portal"
      locale={locale}
      sections={SECTIONS}
      copy={COPY[locale]}
      rightSlot={
        <>
          <LanguageToggle />
          <ThemeToggles />
          <AuthControls />
        </>
      }
    >
      {children}
    </Shell>
  );
}
