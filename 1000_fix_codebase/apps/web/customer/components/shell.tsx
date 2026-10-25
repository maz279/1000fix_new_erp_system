"use client";

/**
 * P01 app wrapper around the shared Service-Teal Fluent shell (libs/ts/ui
 * shell.tsx). Supplies the bilingual chrome copy from the app dictionary,
 * the portal sections, and mounts the existing app controls (language /
 * theme / auth) into the command bar's right slot.
 */
import { useEffect, useState } from "react";
import type { ShellCopy, ShellSection } from "../lib/imports";
import { Shell } from "../lib/imports";
import { useLanguage, LanguageToggle } from "./language";
import { ThemeToggles } from "./theme";
import { AuthControls } from "./auth-modal";

const SECTIONS: ShellSection[] = [
  { href: "/booking", en: "Booking", bn: "বুকিং", icon: "📅" },
  { href: "/tracking", en: "Tracking", bn: "ট্র্যাকিং", icon: "📍" },
  { href: "/estimates", en: "Estimates", bn: "অনুমান", icon: "🧾" },
  { href: "/devices", en: "Devices", bn: "ডিভাইস", icon: "📱" },
  { href: "/consent", en: "Consent", bn: "সম্মতি", icon: "🔐" },
  { href: "/technician", en: "Technician (P02)", bn: "টেকনিশিয়ান (P02)", icon: "🛠️" },
  { href: "/welcome", en: "Platform", bn: "✦ প্ল্যাটফর্ম", icon: "✦" },
];

const COPY: Record<"bn" | "en", ShellCopy> = {
  bn: {
    searchPlaceholder: "মডিউল, স্ক্রিন, রিপোর্ট খুঁজুন… (Alt+Q)",
    portalZone: "কাস্টমার পোর্টাল",
    erpZone: "ERP এরিয়া (P03)",
    systemZone: "সিস্টেম",
    home: "হোম",
    recents: "সাম্প্রতিক",
    online: "ব্যাকএন্ড সংযুক্ত",
    offline: "ব্যাকএন্ড বিচ্ছিন্ন",
    company: "1000 FiX Services Ltd.",
    opsLabel: "অপারেশনস P03",
    portalsLabel: "১২ পোর্টাল",
    tellmePages: "পোর্টাল পাতা",
    tellmeModules: "মডিউল",
    tellmeScreens: "স্ক্রিন",
    tellmeEmpty: "কিছু পাওয়া যায়নি — মডিউল আইডি (যেমন M01) বা নাম লিখুন",
    closeTab: "ট্যাব বন্ধ",
  },
  en: {
    searchPlaceholder: "Search modules, screens, reports… (Alt+Q)",
    portalZone: "CUSTOMER PORTAL",
    erpZone: "ERP AREAS (P03)",
    systemZone: "SYSTEM",
    home: "Home",
    recents: "Recents",
    online: "Backend online",
    offline: "Backend offline",
    company: "1000 FiX Services Ltd.",
    opsLabel: "Operations P03",
    portalsLabel: "12 Portals",
    tellmePages: "Portal pages",
    tellmeModules: "Modules",
    tellmeScreens: "Screens",
    tellmeEmpty: "No matches — try a module id (e.g. M01) or a name",
    closeTab: "Close tab",
  },
};

export function CustomerShell({ children }: { children: React.ReactNode }) {
  const { locale, t } = useLanguage();
  // Cross-portal links must share the browsing HOSTNAME (session cookies
  // are per-hostname, port-agnostic). Resolved after mount: SSR renders
  // the loopback fallback, the effect swaps in the browsing hostname.
  const [hostName, setHostName] = useState<string | null>(null);
  useEffect(() => {
    setHostName(window.location.hostname);
  }, []);
  const corporateHref = `http://${hostName ?? "127.0.0.1"}:3001/`;
  return (
    <Shell
      brandWord={t.portalTitle}
      brandSub="P01 · Customer Portal"
      locale={locale}
      sections={SECTIONS}
      copy={COPY[locale]}
      rightSlot={
        <>
          <a
            className="tb-company"
            href={corporateHref}
            target="_blank"
            rel="noreferrer"
            title="P04 Corporate"
          >
            {t.navCorporate}
          </a>
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
