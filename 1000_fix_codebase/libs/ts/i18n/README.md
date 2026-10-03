# fix-i18n — BN-005 key loading, pluralisation and BN-007 formatting

P04-M08-T03/T04. One implementation across the six Next.js portals
(BE-004 §4). Bengali first (PS-03); English is the fallback, never the
reverse.

- `translate()` — dot-path keys with `{variable}` interpolation
- `translatePlural()` — CLDR `bn` plurals (`one` for exactly 1, `other` otherwise)
- `formatNumber()` — Bengali numerals + **lakh-crory grouping** (`১,৫০,০০০`)
- `formatCurrencyBDT()` — `৳` before the amount, thin space, 2 decimals
- `formatDate()` — Asia/Dhaka (UTC+6, no DST); stored values stay UTC ISO (PID-03)

The full formatting rules live in `docs/localisation/bn-007-formatting.md`.
Identifiers (tracking IDs, S/N, IMEI) are never script-converted — they stay
ASCII in both locales so a customer can type what they read.
