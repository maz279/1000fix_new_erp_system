# BN-007 — Bengali Formatting Rules (P04-M08-T04)

> `PID-03`: a native date picker may differ, but **the value written must be
> identical**. Formatting is a presentation concern; the stored value never
> changes with the locale.

Owner: Localisation Lead (`L11`). Applies to every runtime — Odoo Web (R1),
the six Next.js portals (R2), QWeb reports (R3), Flutter apps (R4) and the
dashboards (R5 partial). The web implementation lives in
`libs/ts/i18n` (BN-005); Odoo-side formatting rides the same tables below.

## 1. Numerals

| Context | `bn` locale | `en` locale |
|---|---|---|
| Quantities, amounts, counters | Bengali numerals `০১২৩৪৫৬৭৮৯` | ASCII digits |
| Identifiers (order refs, S/N, IMEI, tracking IDs) | **ASCII digits always** — identifiers are matched, never read | ASCII |
| Phone numbers | ASCII digits (diallable strings) | ASCII |

Rule: identifiers stay ASCII so that a customer reading an SMS can type the
tracking ID exactly; quantities switch scripts because they are read, not typed.

## 2. Currency (BDT)

- Symbol: `৳` (U+09F3), placed **before** the amount with a thin space: `৳ ১,৫০০`.
- Grouping: lakh-crory grouping (`##,##,###`) — `১,৫০,০০০`, never `150,000`.
- Decimals: amounts show 2 decimals (`৳ ১,৫০০.০০`); the decimal separator is `.`
  (Bangladeshi practice), NOT the South-Asian `।`.
- The **stored value** is always a decimal in BDT; the locale only renders it.
- Mushak 6.3 VAT figures use the same grouping (Phase 6 report rules inherit this file).

## 3. Dates

| Format | Pattern | Example (bn) |
|---|---|---|
| Full date | `d MMMM, y` | `২ অক্টোবর, ২০২৬` |
| Short date | `d/M/y` | `২/১০/২০২৬` |
| Datetime | `d MMMM, y h:mm a` | `২ অক্টোবর, ২০২৬ ৩:৪৫ PM` |

- Month names: জানুয়ারি, ফেব্রুয়ারি, মার্চ, এপ্রিল, মে, জুন, জুলাই, আগস্ট, সেপ্টেম্বর, অক্টোবর, নভেম্বর, ডিসেম্বর.
- AM/PM: `AM`/`PM` remain Latin (common Bangladeshi practice; পূর্বাহ্ণ/অপরাহ্ণ is not used in operational UIs).
- Timezone: Asia/Dhaka (UTC+6, no DST) — the only display zone (`QH-04` companion).
- Stored values are UTC ISO-8601; rendering converts.

## 4. Addresses

Bangladeshi order — **division → district → upazila/thana → union/ward → street, house** —
the inverse of Western order. The `fix.bd.address` model (M30) stores the parts;
rendering joins them with commas in this order, postcode (`####`) last:
`বাড়ি ১২, রোড ৫, ধানমন্ডি, ঢাকা ১২০৯`.

## 5. Names

- `name_bn` is authoritative in the `bn` locale; `name` (Latin) in `en`.
- A party without `name_bn` falls back to Latin — never machine-translated.
- Honorific: `জনাব`/`মিসেস` are used only in message templates (NT set), never in data views.

## 6. Pluralisation (BN-005)

Bengali has six noun classes; operational copy needs the two common forms:

| Count | Form | Example |
|---|---|---|
| exactly 1 | singular | `১টি ডিভাইস` |
| other (0, 2+) | plural/measure | `৩টি ডিভাইস` |

CLDR plural rules for `bn`: `one` (n=0..1 with i=0 and v=0.. fractions use
"other") / `other`. The i18n library implements exactly these two keys —
never more.

## 7. Layout under expansion (UX-007)

Bengali runs typically **15–30% longer** than English and conjunct stacks
increase line height:

- Line height: the `typography.lineHeight.loose` token for body copy; never `tight`.
- No truncation on status wording (MD-027 labels) — wrap instead.
- Buttons re-flow, never ellipsize.
- The expansion test (P04-M08-T09) renders the W1 screens in both locales and
  fails on overflow/clipping.

## 8. Conformance

- Static: `tooling/fitness/check_translations.py` (FF-25) — bn_BD.po 100%.
- Runtime: doctor check 10 — Bengali conjunct rendering vs the committed
  reference image (`docs/guides/reference/bengali-conjunct-reference.png`,
  TR-07). The reference renders through the QWeb report path so a font or
  shaping regression is caught before a Mushak 6.3 invoice goes out.
