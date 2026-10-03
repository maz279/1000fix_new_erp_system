/**
 * fix-i18n — BN-005 key loading and pluralisation for the web estate
 * (P04-M08-T03, BE-004 §4, UX-007).
 *
 * ONE implementation across the six Next.js portals. Bengali (`bn`) is the
 * first-class locale (PS-03); English is the fallback, never the reverse.
 *
 * Formatting (BN-007) lives here too so every runtime formats identically:
 * Bengali numerals, ৳-before-amount, lakh-crory grouping, Asia/Dhaka dates.
 * Stored values never change with the locale (PID-03) — formatting is
 * presentation only.
 */

export type Locale = "bn" | "en";

/** CLDR plural rules for Bengali: `one` for exactly 1, `other` otherwise. */
export function pluralRule(count: number): "one" | "other" {
  return count === 1 ? "one" : "other";
}

export type Messages = Record<string, string>;

/** Key lookup with dot-path nesting and {variable} interpolation. */
export function translate(
  messages: Messages,
  key: string,
  variables: Record<string, string | number> = {},
  fallbackMessages: Messages = {},
): string {
  const raw = messages[key] ?? fallbackMessages[key] ?? key;
  return raw.replace(/\{(\w+)\}/g, (_match, name: string) =>
    Object.prototype.hasOwnProperty.call(variables, name)
      ? String(variables[name])
      : `{${name}}`,
  );
}

/** Plural-aware translate: picks `${key}.${pluralRule(count)}`. */
export function translatePlural(
  messages: Messages,
  key: string,
  count: number,
  variables: Record<string, string | number> = {},
  fallbackMessages: Messages = {},
): string {
  const subkey = `${key}.${pluralRule(count)}`;
  const resolved = messages[subkey] ?? fallbackMessages[subkey] ?? subkey;
  return translate({ [subkey]: resolved }, subkey, { ...variables, count });
}

// ---------------------------------------------------------------- BN-007 ---

const BN_DIGITS = ["০", "১", "২", "৩", "৪", "৫", "৬", "৭", "৮", "৯"];

export function toBengaliDigits(input: string): string {
  return input.replace(/\d/g, (d) => BN_DIGITS[Number(d)]);
}

/** Lakh-crory grouping: 1,50,000 — NOT western 150,000. */
export function groupSouthAsian(digits: string, separator: string): string {
  if (digits.length <= 3) return digits;
  const head = digits.slice(0, -3).replace(/\B(?=(\d{2})+(?!\d))/g, separator);
  return head + separator + digits.slice(-3);
}

export function formatNumber(
  value: number,
  locale: Locale,
  options: { decimals?: number } = {},
): string {
  const decimals = options.decimals ?? 0;
  const [intPart, decPart] = Math.abs(value).toFixed(decimals).split(".");
  const sign = value < 0 ? "-" : "";
  let out = sign + groupSouthAsian(intPart, ",");
  if (decPart) out += "." + decPart;
  return locale === "bn" ? toBengaliDigits(out) : out;
}

/** ৳ before the amount with a thin space: ৳ ১,৫০০.০০ */
export function formatCurrencyBDT(value: number, locale: Locale): string {
  const amount = formatNumber(value, locale, { decimals: 2 });
  return locale === "bn" ? `৳\u2009${amount}` : `BDT\u2009${amount}`;
}

const BN_MONTHS = [
  "জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন",
  "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর",
];

/** Asia/Dhaka rendering (UTC+6, no DST — QH-04 companion). Stored values are UTC. */
export function formatDate(
  iso: string,
  locale: Locale,
  style: "full" | "short" | "datetime" = "full",
): string {
  const date = new Date(iso);
  const dhaka = new Date(date.getTime() + 6 * 3600 * 1000);
  const d = dhaka.getUTCDate();
  const m = dhaka.getUTCMonth();
  const y = dhaka.getUTCFullYear();
  if (locale === "en") {
    const month = new Date(Date.UTC(y, m, d)).toLocaleString("en", { month: "short", timeZone: "UTC" });
    if (style === "short") return `${d}/${m + 1}/${y}`;
    if (style === "datetime") return `${d} ${month} ${y} ${dhaka.getUTCHours()}:${String(dhaka.getUTCMinutes()).padStart(2, "0")}`;
    return `${d} ${month} ${y}`;
  }
  if (style === "short") return toBengaliDigits(`${d}/${m + 1}/${y}`);
  if (style === "datetime") {
    const hh = dhaka.getUTCHours();
    const ampm = hh < 12 ? "AM" : "PM";
    const h12 = hh % 12 === 0 ? 12 : hh % 12;
    return toBengaliDigits(`${d} ${BN_MONTHS[m]}, ${y} ${h12}:${String(dhaka.getUTCMinutes()).padStart(2, "0")} ${ampm}`);
  }
  return `${toBengaliDigits(String(d))} ${BN_MONTHS[m]}, ${toBengaliDigits(String(y))}`;
}
