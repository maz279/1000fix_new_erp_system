/**
 * UI copy registry access — P04-M06-T09 (UI-001 i18n key standard).
 *
 * The registry is GENERATED (tooling/scripts/extract-ui-copy.py) from the
 * content library's W1 copy packs; nothing here authors a string.
 *
 * Rules enforced by the loader (matching the extractor):
 * - One key resolves to exactly one string per locale (CG-004).
 * - `counterpart-pending` keys return the English string in both locales and
 *   are counted — a portal never renders an empty label, and the pending
 *   count is visible to the release checklist. As of PP0 (2026-10-05) the
 *   registry carries 493 keys with 0 counterpart-pending (the 110 W1
 *   pendings closed at source; UI-900 added 199 inline prototype keys).
 * - Bengali fallback is Latin never machine-translated: bn falls back to en.
 */

import raw from "./ui-copy.generated.json";

export interface UiCopyEntry {
  key: string;
  en: string;
  bn: string | null;
  bn_status: "inline" | "counterpart-pending";
  max: number | null;
}

interface RegistryShape {
  total_keys: number;
  counterpart_pending: number;
  packs: Record<string, { source: string; wave: string; copy: UiCopyEntry[] }>;
}

const registry = raw as unknown as RegistryShape;

const byKey = new Map<string, UiCopyEntry>();
for (const pack of Object.values(registry.packs)) {
  for (const entry of pack.copy) {
    if (!byKey.has(entry.key)) {
      byKey.set(entry.key, entry);
    }
  }
}

export function uiCopy(key: string, locale: "bn" | "en"): string {
  const entry = byKey.get(key);
  if (!entry) {
    // A missing key renders visibly, never silently — CG-003: the interface
    // tells the truth about its own state.
    return key;
  }
  if (locale === "bn" && entry.bn) {
    return entry.bn;
  }
  return entry.en;
}

export function uiCopyStatus(): {
  totalKeys: number;
  inlineBilingual: number;
  counterpartPending: number;
} {
  let inline = 0;
  let pending = 0;
  for (const entry of byKey.values()) {
    if (entry.bn_status === "inline" && entry.bn) inline += 1;
    else pending += 1;
  }
  return { totalKeys: byKey.size, inlineBilingual: inline, counterpartPending: pending };
}
