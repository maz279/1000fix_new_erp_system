/**
 * uiCopy — read-side access to the GENERATED copy registry
 * (libs/ts/i18n/src/ui-copy.generated.json — 493 keys, 0 counterpart-pending).
 *
 * Mirrors the loader rules of libs/ts/i18n (CG-004: one key = one string per
 * locale; bn falls back to en, never machine-translated). Portals import this
 * through @api-client so they never hand-author user-facing strings.
 */
import raw from "../../i18n/src/ui-copy.generated.json";

interface UiCopyEntry {
  key: string;
  en: string;
  bn: string | null;
  bn_status: "inline" | "counterpart-pending";
}

type Locale = "en" | "bn";

const index = new Map<string, UiCopyEntry>();
for (const pack of Object.values((raw as { packs: Record<string, { copy: UiCopyEntry[] }> }).packs)) {
  for (const entry of pack.copy) index.set(entry.key, entry);
}

export function uiCopy(key: string, locale: Locale): string {
  const entry = index.get(key);
  if (!entry) return key; // never render an empty label — the key is the last resort
  if (locale === "bn" && entry.bn && entry.bn_status === "inline") return entry.bn;
  return entry.en;
}

export function copyStatus(): { total: number; counterpartPending: number } {
  let pending = 0;
  for (const entry of index.values()) if (entry.bn_status === "counterpart-pending") pending += 1;
  return { total: index.size, counterpartPending: pending };
}
