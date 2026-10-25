"use client";

/**
 * P01 public landing — the shared marketing shell (PP5): 12 portal
 * cards + 10 journey strips from the generated landing artefact,
 * bilingual with a Bengali default (DE-17).
 * Integrated with Customer Portal LanguageProvider for synchronized
 * language switching across the Fluent shell and LandingShell.
 */
import { LandingShell } from "../../lib/imports";
import { useLanguage } from "../../components/language";

export default function LandingPage() {
  const { locale, toggleLocale } = useLanguage();
  return <LandingShell portalId="P01" locale={locale} onToggleLocale={toggleLocale} />;
}
