/**
 * masks — statutory input masks + display formatters (PP6, 03-DATA-STRATEGY §7/§8).
 *
 * §7: the four Bangladesh statutory identifiers, exactly as the estate
 * enforces them (audit-corrected 2026-10-05: digit-only + exact length;
 * NO invented checksums — the NBR publishes none for BIN/e-TIN).
 * §8: bn007 renders South Asian grouping for backend-computed money —
 * formatting only; the client never performs monetary arithmetic (AS-10).
 *
 * Binding rule: any R1/R2 input that captures one of these identifiers
 * applies the mask + validator here — no portal re-declares the pattern.
 */

/** 13-digit BIN (NBR VAT Act 2012) — the fix.mushak.register constraint. */
export const BIN_13 = /^\d{13}$/;
/** 10-digit Smart NID (Election Commission). */
export const NID_10 = /^\d{10}$/;
/** 17-digit Legacy NID — year-of-birth prefix + 13 digits. */
export const NID_17 = /^(19|20)\d{15}$/;
/** 12-digit e-TIN in the statutory XXXX-XXXX-XXXX hyphenated form. */
export const ETIN_12 = /^\d{4}-\d{4}-\d{4}$/;

export type StatutoryId = "bin" | "nid10" | "nid17" | "etin";

const PATTERNS: Record<StatutoryId, RegExp> = {
  bin: BIN_13, nid10: NID_10, nid17: NID_17, etin: ETIN_12,
};

/** Validate a statutory identifier against its §7 rule. */
export function isValidId(kind: StatutoryId, value: string): boolean {
  return PATTERNS[kind].test(value);
}

/**
 * Input mask for typing: keeps digits (and the e-TIN hyphens), drops the
 * rest, and inserts the hyphens as the e-TIN's groups complete. Pure
 * string shaping — no async, no locale state.
 */
export function maskId(kind: StatutoryId, value: string): string {
  const digits = value.replace(/\D/g, "");
  if (kind === "etin") {
    return [digits.slice(0, 4), digits.slice(4, 8), digits.slice(8, 12)]
      .filter(Boolean).join("-");
  }
  const max = kind === "bin" ? 13 : kind === "nid10" ? 10 : 17;
  return digits.slice(0, max);
}

/**
 * bn007 — display formatter for backend-computed BDT strings/numbers
 * (§8): South Asian grouping `1,23,45,678.00`. The value's magnitude is
 * the backend's; this function groups digits only.
 */
export function bn007(value: string | number): string {
  const n = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(n)) return "0.00";
  const neg = n < 0 ? "-" : "";
  const abs = Math.abs(n);
  const whole = Math.trunc(abs);
  const frac = (abs - whole).toFixed(2).slice(1); // ".xx"
  const s = String(whole);
  if (s.length <= 3) return neg + s + frac;
  const last3 = s.slice(-3);
  let rest = s.slice(0, -3);
  const parts: string[] = [];
  while (rest.length > 2) {
    parts.unshift(rest.slice(-2));
    rest = rest.slice(0, -2);
  }
  if (rest) parts.unshift(rest);
  return neg + parts.join(",") + "," + last3 + frac;
}
