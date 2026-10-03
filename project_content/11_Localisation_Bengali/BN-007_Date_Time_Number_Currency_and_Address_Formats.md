---
id: BN-007
title: Date, Time, Number, Currency and Address Formats
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Platform Engineering, Finance and Service Operations
reviewers: [Platform Engineering, Finance Controller, Tax Manager, Service Operations, MDM Lead, Design System, QA Lead]
approver: Content Design Lead with Localisation Lead and Finance Controller
content_class: C
purpose: >
  Fixes the bn-BD and en presentation of every number, amount, date, time, duration, phone
  number, address and identifier the system displays, prints, speaks or exports, and closes the
  numeral-glyph question that CG-010 §12 item 3 and VB-009 NU-03 leave open. Locale defaults
  cannot be trusted here: CLDR sets Bengali digits as the default numbering system for bn, puts
  the currency symbol after the amount, supplies AM and PM in Latin, and has no weekend data for
  Bangladesh at all — so a system that relies on the locale renders money in Bengali digits with
  a trailing symbol and computes SLA due dates against a Saturday-Sunday weekend that Bangladesh
  does not observe.
traces_to: [05-06 §9, 05-06 DM-08, CG-010 BC-06, CG-010 BC-07, CG-010 §12 item 3, VB-009 §5, VB-009 NU-03, VB-009 NU-04, VB-009 NU-05, BN-006 §7, MD-006, MD-007, MD-028, MD-041, LG-015, DT-010, DT-016]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: Unicode CLDR cldr-numbers-full bn/numbers.json — "defaultNumberingSystem":"beng"; decimal standard pattern "#,##,##0.###"; currency standard pattern "#,##,##0.00¤"; group separator ","; decimal separator "."
    verified: 2026-08-17
    class: P1
  - source: Unicode CLDR cldr-numbers-full bn/currencies.json — BDT displayName "বাংলাদেশী টাকা", symbol "৳", symbol-alt-narrow "৳"
    verified: 2026-08-17
    class: P1
  - source: Unicode CLDR cldr-dates-full bn/ca-gregorian.json — months wide জানুয়ারি…ডিসেম্বর; days wide রবিবার…শনিবার; dateFormats full "EEEE, d MMMM, y", long "d MMMM, y", medium "d MMM, y", short "d/M/yy"; timeFormats short "h:mm a"; dayPeriods format wide am "AM", pm "PM", morning1 "ভোরবেলায়", afternoon1 "দুপুরবেলায়", evening1 "সন্ধ্যাবেলায়", night1 "রাত্রিবেলায়"
    verified: 2026-08-17
    class: P1
  - source: Unicode CLDR supplemental weekData.json — firstDay "BD":"sun"; BD is absent from weekendStart and weekendEnd, inheriting the "001" default of sat–sun
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 — lakh/crore grouping 12,34,567 in the Bengali locale; BDT (৳) primary with two decimal places; DD/MM/YYYY with Bengali month names in the Bengali locale; 12-hour with Bengali AM/PM equivalents, stored UTC displayed Asia/Dhaka; Gregorian calendar with Bangladesh public holidays including moon-dependent dates; fiscal year July–June; address Division → District → Upazila/Thana → Union/Ward → Postcode; phone +880 with operator validation; National ID 10-digit and 17-digit
    verified: 2026-08-17
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-009 §5.1 proposed numeral policy by content type, NU-01…NU-05
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-007 — Date, Time, Number, Currency and Address Formats

> **The locale is not the standard. The locale is the starting point that must be corrected.**
>
> Four CLDR defaults for Bengali are wrong for this system, and each one is wrong in a way that
> costs money rather than looking untidy:
>
> | CLDR default for `bn` / `BD` | What the system needs | Cost of not overriding |
> |---|---|---|
> | `defaultNumberingSystem` = **`beng`** | Arabic digits for money, identifiers and data | An amount transcribed into a bank form from Bengali digits |
> | Currency pattern **`#,##,##0.00¤`** — symbol last | Symbol first, both locales | Two amount formats on one invoice |
> | Day periods **`"AM"` / `"PM"`** in Latin | Bengali time expression (`05-06` §9) | An untranslated string on every timestamp |
> | **No weekend data for `BD`** — inherits sat–sun | **Friday–Saturday** | **SLA due dates computed against the wrong working week, and service credits are a contractual liability** |

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | Presentation and parsing of numbers, money, dates, times, durations, phone numbers, addresses, names and identifiers in both locales, across screen, print, message, voice and export |
| **What it does not govern** | Which glyphs the font draws (`BN-006` §7); which words are used (`BN-003`); which items never change form (`BN-004`); the business calendar's contents (`MD-041`) |
| **What breaks without it** | Money transcribed wrongly, SLA breaches computed against the wrong week, an invoice with two amount formats, a phone number that fails operator validation, and an address that cannot be delivered to |

---

## 2. The locale baseline and the overrides

**Every override below is deliberate, sourced and configured explicitly in code.** Nothing relies
on a locale default (`BN-006` `NU-07`).

| Aspect | CLDR `bn` default | **1000FiX standard** | Override? | Authority |
|---|---|---|:--:|---|
| Numbering system | `beng` | **`latn` by default; `beng` only in the §3.2 contexts** | **Yes** | §3 |
| Decimal grouping | `#,##,##0.###` | Unchanged — lakh/crore | No | `05-06` §9 |
| Group / decimal separator | `,` / `.` | Unchanged | No | `05-06` §9 |
| Currency symbol | `৳` | Unchanged | No | CLDR + `05-06` §9 |
| Currency pattern | `#,##,##0.00¤` (suffix) | **`¤ #,##,##0.00` (prefix, NBSP)** | **Yes** | §4 |
| Currency decimals | 2 | Unchanged | No | `05-06` §9 |
| Short date | `d/M/yy` | **`dd/MM/yyyy`** | **Yes** | `05-06` §9 |
| Month names | জানুয়ারি … ডিসেম্বর | Unchanged | No | CLDR + `05-06` §9 |
| Day names | রবিবার … শনিবার | Unchanged | No | CLDR |
| Day period am/pm | `"AM"` / `"PM"` | **Bengali expression — §6** | **Yes** | `05-06` §9 |
| First day of week | `sun` (BD) | Unchanged — **Sunday** | No | CLDR `weekData` |
| **Weekend** | **absent for BD; inherits sat–sun** | **Friday and Saturday** | **Yes — critical** | §7 |
| Time zone | — | Store UTC, display **Asia/Dhaka** (UTC+6, no DST) | — | `05-02` DM-08 |
| Calendar | Gregorian | Unchanged. **Bangla Sôn is not used for transactions** | No | §5.4 |
| Fiscal year | — | **July–June** | — | `05-06` §9 |

| # | Rule |
|---|---|
| **FM-01** | **Every one of the five overrides is configured in one place** — a shared locale configuration consumed by all five frameworks and by the reporting layer. Per-surface configuration guarantees divergence |
| **FM-02** | **Nothing is formatted by hand.** Content authors write ICU placeholders; the formatter produces the string (`BN-005` `KP-09`) |
| **FM-03** | A format defect found in production is fixed **in the shared configuration**, never in the string |

---

## 3. Numerals — the decision

**This closes `CG-010` §12 item 3 and `VB-009` `NU-03`.**

### 3.1 The decision

| # | Decision |
|---|---|
| **NM-A** | **Arabic digits (0–9) are the system default in both locales.** The ICU numbering system is set explicitly to `latn`, overriding the CLDR `beng` default |
| **NM-B** | **Bengali digits (০–৯) are used only in the contexts listed in §3.2**, and only by explicit opt-in at the point of rendering |
| **NM-C** | **Never mix numeral systems within one value, one column, one document, one message or one screen region** (`BN-006` `NU-01`…`NU-03`) |
| **NM-D** | **Identifiers are Arabic digits always**, in every context including Bengali prose (`BN-004` `DN-04`) |
| **NM-E** | **Bengali digits are accepted as input everywhere** and normalised to Arabic on write (`BN-006` `IM-06`). The decision constrains output, never the user's keyboard |

### 3.2 Where Bengali digits are used

| Context | Numerals | Reason |
|---|:--:|---|
| Help, training and knowledge **prose** | **Bengali** | Read as language, not transcribed. Bengali digits are natural in Bengali sentences |
| Dates **written out in Bengali prose** | **Bengali**, with Bengali month names | `05-06` §9 permits it; §5.3 |
| Marketing and campaign copy on Bengali surfaces | **Bengali** | Continuity with the corporate website |
| IVR **spoken** output | n/a — spoken | `BN-017` `VP-07` |
| **Everything else** | **Arabic** | |

### 3.3 Where Bengali digits are prohibited

| Context | Reason |
|---|---|
| **Money, anywhere** | Transcription into bank, gateway and government systems (`BN-004` §7) |
| **Statutory documents and filings** | Transcribed by a third party into a state system |
| **Identifiers** — reference, IMEI, serial, part number, BIN, TIN, NID, phone, postcode, account | Read and typed character by character (`NM-D`) |
| **Quantities, prices and totals in tables** | Column scanning; also `BN-006` `NU-06` legibility at the floor |
| **Dates and times in data fields, logs, exports and APIs** | Machine-parsed |
| **Barcode and QR payloads** | `BN-004` §7 |
| **Thermal and label output** | 203 dpi with no anti-aliasing; ০ and ৩ converge (`BN-006` §4) |
| **Anything a contact-centre agent reads aloud from a screen** | The agent transcribes what the customer says back |

### 3.4 The consequence for existing content

| Where | Current | Required |
|---|---|---|
| `NT-004` §2.2 variables table — `{amount}` example `৳ ৩,২০০.০০` | Bengali digits in money | **`৳ 3,200.00`** — §3.3 |
| `VB-009` §5.1 "Money, anywhere — Arabic" | Consistent with `NM-A` | Confirmed; `VB-009` `NU-03`'s deferral to this file is now discharged |
| `MD-027` sample rows | No numerals | Unaffected |

> Raised as `AUDIT-012` **BN-09**. The correction belongs to `NT-004`'s owner under `CG-007` §7
> re-approval triggers, not to Localisation (`BN-003` `GL-10`).

---

## 4. Numbers and currency

### 4.1 Numbers

| Item | Bengali locale | English locale |
|---|---|---|
| Grouping | **Lakh/crore — `#,##,##0`** | Lakh/crore — the company operates in Bangladesh and one grouping across both locales prevents mis-reading between them |
| Example | 12,34,567 | 12,34,567 |
| Decimal separator | `.` | `.` |
| Negative | `-1,234.00` | `-1,234.00` |
| Percentage | `12.5%` — no space | `12.5%` |
| Range | `10–20` — en dash, no spaces | `10–20` |
| Ordinals | See `BN-005` `PL-08` — five categories | Four categories |
| Large numbers in prose | **লাখ** and **কোটি**, not "million" | lakh and crore, expanded on first use for non-Bangladeshi readers |

| # | Rule |
|---|---|
| **FM-04** | **Lakh/crore grouping applies in both locales** (`05-06` §9 sets it for the Bengali locale; this file extends it to English). Two groupings for one figure on one programme is how a 12,34,567 becomes a 1,234,567 in a board pack |
| **FM-05** | **Never write a number as a literal in content.** `12,34,567` typed into a string will not regroup, will not localise and will not update (`FM-02`) |
| **FM-06** | Quantities are **tabular figures** in scanned columns (`BN-006` `FR-08`, `NU-05`) |

### 4.2 Currency

| Item | Standard |
|---|---|
| Code | **`BDT`** — Tier 1 (`BN-004`) |
| Symbol | **`৳`** (U+09F3) |
| **Position** | **Prefix, both locales**, followed by a non-breaking space: `৳ 3,200.00` |
| Decimals | **Always two**, including whole amounts: `৳ 3,200.00`, never `৳ 3200` |
| Grouping | Lakh/crore |
| Negative | `-৳ 3,200.00` |
| Zero | `৳ 0.00` |
| Foreign currency | ISO code prefix: `USD 1,200.00` (CLDR `bn` renders USD as `US$`; **overridden to the code** to avoid ambiguity on a multi-currency document) |
| Which symbol where | **`৳` on both Bengali and English surfaces.** `VB-009` `NU-05` proposed `৳` in Bengali and `BDT` in English; this file supersedes that with a single symbol, and `BDT` used only where a code is required |

| # | Rule |
|---|---|
| **FM-07** | **The symbol precedes the amount and is separated by a non-breaking space.** This overrides the CLDR `bn` suffix pattern (§2). A line break between `৳` and its amount is a defect |
| **FM-08** | **An amount is never rendered without its currency indicator** on a document, a message or a total. A bare number in a money column is ambiguous the moment a second currency exists |
| **FM-09** | **Two decimals always.** Truncating them on a receipt to save width is a reconciliation defect |
| **FM-10** | **`VB-009` `NU-05` is superseded by `FM-07`.** Recorded as `AUDIT-012` **BN-10**, with the correction routed to `VB-009`'s owner |

### 4.3 Amount in words

Required on money receipts, cheques and any instrument where a figure may be altered
(`DT-016`, `DT-010`).

| # | Rule |
|---|---|
| **AW-01** | Bengali amount-in-words uses **লাখ / কোটি** structure, ends with **টাকা মাত্র**, and states paisa explicitly or states its absence |
| **AW-02** | Example: `৳ 3,200.50` → **তিন হাজার দুইশত টাকা পঞ্চাশ পয়সা মাত্র** |
| **AW-03** | Amount-in-words uses **Bengali words with Arabic digits nowhere in the phrase** — it is prose, not a number |
| **AW-04** | The English amount-in-words is the parallel: **Three thousand two hundred taka and fifty paisa only** |
| **AW-05** | Amount-in-words is **generated, never typed**, and is verified against the figure at render. A mismatch is a build failure |
| **AW-06** | Where a document is bilingual, **both** amount-in-words forms appear, and both are generated from the same figure |

---

## 5. Dates

### 5.1 Formats

| Context | Bengali locale | English locale |
|---|---|---|
| Data, forms, tables, exports | **`dd/MM/yyyy`** — 17/08/2026 | `dd/MM/yyyy` |
| Medium, in prose | **১৭ আগস্ট, ২০২৬** | 17 Aug 2026 |
| Long, on documents | **১৭ আগস্ট, ২০২৬** | 17 August 2026 |
| Full, with weekday | **সোমবার, ১৭ আগস্ট, ২০২৬** | Monday, 17 August 2026 |
| Month names | জানুয়ারি, ফেব্রুয়ারি, মার্চ, এপ্রিল, মে, জুন, জুলাই, আগস্ট, সেপ্টেম্বর, অক্টোবর, নভেম্বর, ডিসেম্বর | January … December |
| Day names | রবিবার, সোমবার, মঙ্গলবার, বুধবার, বৃহস্পতিবার, শুক্রবার, শনিবার | Sunday … Saturday |
| Machine interchange | **ISO 8601 `YYYY-MM-DD`** | ISO 8601 |

| # | Rule |
|---|---|
| **FM-11** | **`dd/MM/yyyy` with a four-digit year and zero padding**, overriding CLDR's `d/M/yy` (§2). A two-digit year on a warranty expiry or a contract end date is not acceptable |
| **FM-12** | **Never `MM/DD/YYYY`.** Any surface, export or integration producing US order is a defect, and 03/04/2026 is silently wrong rather than visibly wrong |
| **FM-13** | Dates in **prose** in Bengali content use Bengali digits and Bengali month names (§3.2) |
| **FM-14** | Dates in **data** use Arabic digits in both locales (§3.3) |
| **FM-15** | Machine interchange — APIs, exports, file names, logs — is **ISO 8601 in UTC**, never a localised form (`AP-004`) |
| **FM-16** | A date range uses an en dash with spaces in prose and none in tables: `১৭–২১ আগস্ট` |

### 5.2 Relative dates

| Concept | Bengali | English |
|---|---|---|
| Today | আজ | Today |
| Tomorrow | আগামীকাল | Tomorrow |
| Yesterday | গতকাল | Yesterday |
| In n days | `{n} দিনে` | in {n} days |
| n days ago | `{n} দিন আগে` | {n} days ago |

| # | Rule |
|---|---|
| **FM-17** | Relative dates are used **only within ±7 days** and only where the absolute date is also available. "৩ দিন আগে" on a warranty record is not a date |
| **FM-18** | Relative dates are **never used on a legal, statutory or financial document** |
| **FM-19** | Relative dates are computed in **Asia/Dhaka**, not in the browser's zone. A technician in Sylhet and a server in Singapore must agree on what "আজ" means |

### 5.3 Calendar

| Item | Standard |
|---|---|
| Calendar | **Gregorian**, in all transactional and statutory contexts |
| **Bangla Sôn (বঙ্গাব্দ)** | **Not used for transactions.** It may be named in campaign content for Pohela Boishakh, where the date itself comes from `MD-041` |
| Public holidays | From **`MD-041`**, including moon-dependent Eid dates carried as provisional until confirmed (`NT-019` `IV-05`) |
| Fiscal year | **July–June** (`05-06` §9) |
| First day of week | **Sunday** — CLDR `BD`, unchanged |

---

## 6. Time

| Item | Bengali locale | English locale |
|---|---|---|
| Storage | **UTC, always** (`05-02` DM-08) | UTC |
| Display zone | **Asia/Dhaka, UTC+6, no DST** | Asia/Dhaka |
| Prose and appointments | **12-hour with a Bengali day-period word** — সকাল ১০:৩০, বিকাল ৪:০০, রাত ৯:১৫ | 10:30 am, 4:00 pm |
| Tables, logs, technical surfaces | **24-hour — 16:00** | 24-hour — 16:00 |
| Seconds | Only where operationally required | Same |
| Machine interchange | **ISO 8601 with offset** — `2026-08-17T16:00:00+06:00` | Same |

**Day-period words**, used in place of AM and PM:

| Range | Bengali |
|---|---|
| 04:00–05:59 | ভোর |
| 06:00–11:59 | সকাল |
| 12:00–14:59 | দুপুর |
| 15:00–17:59 | বিকাল |
| 18:00–19:59 | সন্ধ্যা |
| 20:00–03:59 | রাত |

| # | Rule |
|---|---|
| **FM-20** | **`"AM"` and `"PM"` are never displayed on a Bengali surface.** CLDR supplies them in Latin for `bn`; `05-06` §9 requires Bengali equivalents; §6 is the override that satisfies it |
| **FM-21** | **Dense operational surfaces use 24-hour**, which removes the day-period question entirely and is unambiguous on a dispatch board, a log and a shift roster |
| **FM-22** | The day-period word is **derived from the time**, never authored into a string. `সকাল {time}` in a bundle is a defect — the value may be an afternoon |
| **FM-23** | **All time arithmetic is performed in UTC** and converted for display only. SLA elapsed time, shift duration and offline-queue ordering are computed in UTC (`05-02` DM-08, `PS-08`) |
| **FM-24** | Bangladesh observes **no daylight saving**. Code must not assume a fixed offset for other zones a multi-entity deployment may add (`M65`) |

### 6.1 Durations

| Concept | Bengali | English |
|---|---|---|
| Minutes | `{n} মিনিট` | {n} min |
| Hours | `{n} ঘণ্টা` | {n} hr |
| Hours and minutes | `২ ঘণ্টা ৩০ মিনিট` | 2 hr 30 min |
| Days | `{n} দিন` | {n} days |
| Working days | `{n} কার্যদিবস` | {n} working days |

| # | Rule |
|---|---|
| **FM-25** | **A duration is never expressed as a decimal of an hour** in customer content. "২.৫ ঘণ্টা" is a spreadsheet value, not a promise |
| **FM-26** | **কার্যদিবস (working day) is never a synonym for দিন (day).** The difference is §7, and it is the difference between meeting an SLA and paying a service credit |

---

## 7. Working days, business hours and the weekend

**This section exists because the locale gets Bangladesh wrong.**

| # | Rule |
|---|---|
| **BD-01** | **The Bangladesh weekend is Friday and Saturday.** CLDR carries no `weekendStart`/`weekendEnd` entry for `BD` and therefore inherits the `001` world default of Saturday–Sunday, which is **wrong** |
| **BD-02** | **The weekend is configured explicitly and never taken from the locale.** A system that inherits the default treats Friday as a working day and Sunday as a holiday — inverting the working week |
| **BD-03** | The working week is **Sunday to Thursday** for offices; branch and field operating patterns vary by site and come from **`MD-003`**, not from a global assumption |
| **BD-04** | **Business-day arithmetic — SLA response and resolution, payment terms, dunning, notice periods, retention — uses the `MD-041` business calendar**, which carries the weekend, public holidays and moon-dependent dates |
| **BD-05** | **SLA pause rules are `MD-028`'s**, and `MD-028` is the sole authority. This file supplies the calendar; it does not define the pause |
| **BD-06** | **A due date computed against the wrong weekend is a financial defect, not a display defect.** SLA breaches trigger service credits, which are a quantified contractual liability (`LG-015`, `DT-031`) |
| **BD-07** | Moon-dependent holidays are **provisional until confirmed** and every dependent computation is re-evaluated on confirmation (`MD-041`, `NT-019` `IV-05`) |
| **BD-08** | Quiet hours for notifications are **08:00–21:00 Asia/Dhaka** (`NT-003`), computed in the display zone, not in UTC |

> **Verification.** `TS-014` and the `MD-028` acceptance tests must include a case that falls
> across a Friday and a case that falls across a Sunday. A test suite written in a Saturday–Sunday
> assumption passes against the defect.

---

## 8. Phone, address, name and identifier formats

### 8.1 Phone

| Item | Standard |
|---|---|
| Storage | **E.164 — `+8801XXXXXXXXX`** |
| Display, Bangladesh | `01XXX-XXXXXX` |
| Display, international | `+880 1XXX-XXXXXX` |
| Digits | **Arabic always** (`NM-D`) |
| Validation | Bangladesh mobile operator prefixes (`05-06` §9) |
| Landline | Area code preserved; `+880` in storage |

| # | Rule |
|---|---|
| **FM-27** | **Bengali digits are accepted as input and normalised** (`NM-E`). A customer typing ০১৭ on a Bengali keyboard is not rejected |
| **FM-28** | A phone number is **never grouped with a thousands separator** (`BN-004` `DN-05`) |

### 8.2 Address

Composition per `05-06` §9 and `MD-006`; validation rules per `MD-007`.

```
Bengali                                  English
{recipient}                              {recipient}
{house/holding}, {road/area}             {house/holding}, {road/area}
{union_or_ward}, {upazila_or_thana}      {union_or_ward}, {upazila_or_thana}
{district} — {postcode}                  {district} — {postcode}
{division} বিভাগ                          {division} Division
বাংলাদেশ                                  Bangladesh
```

| # | Rule |
|---|---|
| **FM-29** | Order is **narrowest to broadest**, in both languages |
| **FM-30** | **Place names come from `MD-006`** in the matching script (`BN-004` `TL-08`) |
| **FM-31** | **Postcode is Arabic digits**, both languages (`NM-D`) |
| **FM-32** | Informal elements — a landmark, a market name, "beside the mosque" — are **preserved as entered** and never normalised away. Field service fails on bad addresses more often than on bad diagnosis (`MD-007`) |
| **FM-33** | An address printed for a **courier** follows the courier's required format and script (`BN-004` §7, `DT-027`) |
| **FM-34** | GPS coordinates are **decimal degrees, Arabic digits, six decimal places**, never localised |

### 8.3 Names

| # | Rule |
|---|---|
| **FM-35** | Names are stored in **both scripts** where both are known (`BN-004` `TL-02`) |
| **FM-36** | **No forename/surname split is imposed.** Bangladeshi naming does not reliably decompose that way; the record holds a full name plus optional parts (`MD-013`) |
| **FM-37** | Honorifics are stored separately and are **not** part of the name (`BN-004` `TL-06`) |
| **FM-38** | Sorting is by **ICU `bn-BD` collation** on the script being displayed (`BN-006` `EN-07`) |

### 8.4 Identifiers

| Identifier | Format |
|---|---|
| **NID** | 10-digit **or** 17-digit, validated (`05-06` §9). Arabic digits. No grouping |
| **BIN** | As issued. Latin and Arabic digits |
| **TIN** | As issued. Sensitive under `05-06` NFR-086 — masked in list views, revealed on authorised action |
| Service order reference | `SR-YYYY-NNNNNN` (`CG-005`) |
| IMEI | 15 digits, no grouping |
| Postcode | 4 digits |

| # | Rule |
|---|---|
| **FM-39** | **No identifier is ever grouped, spaced or reformatted for display** (`BN-004` `DN-05`) |
| **FM-40** | An identifier displayed for **reading aloud** may be visually chunked in the UI **without changing the stored or copied value** — and the chunking is identical in both languages |

---

## 9. Where formats are consumed

| Surface | Consideration |
|---|---|
| Screen | ICU formatters from the shared configuration (`FM-01`) |
| **Print and PDF** | Same configuration. **Thermal output uses Arabic digits regardless** (`BN-006` §4) |
| **SMS** | Bengali digits cost the same as Arabic in UCS-2, but a longer formatted amount can cross a segment boundary (`BN-014` §3) |
| **IVR** | Digits read individually with a pause; amounts read as a spoken figure (`BN-017` `VP-07`) |
| **Email** | Same configuration; no client-side locale detection |
| **Reports and exports** | ISO 8601 dates and unformatted numeric values in the data; formatting applied at presentation only (`RP-014`) |
| **APIs** | ISO 8601, decimal points, no grouping, no symbol (`AP-004`) |
| **Barcode / QR** | Raw values only (`BN-004` §7) |

---

## 10. Enforcement

| Check | Mechanism | When |
|---|---|---|
| A hard-coded date, number or amount in a string | Automated pattern scan | Every commit |
| Bengali digits in an identifier, money or data field | Automated | Every commit |
| A locale-default numbering system left unset | **Configuration test** | Every build |
| Currency symbol rendered as a suffix | Automated snapshot test | Every build |
| `"AM"` or `"PM"` in a Bengali bundle or render | Automated | Every commit |
| **Weekend configured as Friday–Saturday** | **Configuration test with a Friday and a Sunday case** | **Every build** |
| Business-day arithmetic against `MD-041` | Unit tests (`TS-014`) | Every build |
| Amount-in-words matches the figure | Render-time assertion (`AW-05`) | Every render |
| Date rendered as `MM/DD/YYYY` anywhere | Automated | Every commit |
| Export encoding and date form | File-header and sample check | Every export release |

---

## 11. Open decisions

| # | Decision | Owner | Needed by | Blocks |
|---|---|---|---|---|
| 1 | **Ratify §3 — the numeral decision.** Closes `CG-010` §12 item 3, `VB-009` `NU-03`, `BN-006` §10 item 2, `UI-001` §9 item 4 | Localisation Lead with Design, ratified by Content Lead | **Before W1** | Every bundle, every document, every message |
| 2 | **Confirm `FM-07`** — currency symbol prefix, overriding CLDR and superseding `VB-009` `NU-05` | Finance Controller with Localisation Lead | Before the first `DT` release | `DT-010`…`DT-020`, `BN-015` |
| 3 | **Confirm `BD-01`** — the Friday–Saturday weekend, and that `MD-041` carries it | **Service Operations with Finance** | **Before W1 SLA configuration** | `MD-028`, `MD-041`, `LG-015`, `DT-031` |
| 4 | Does any statutory form require **Bengali digits** in a field we would render in Arabic (§3.3)? | Tax Manager | Before the first statutory filing | `DT-010`…`DT-014`, `BN-015` |
| 5 | Is lakh/crore grouping acceptable in the **English** locale for international brand partners reading `P08` (`FM-04`)? | Commercial with Finance | Before W4 | `P08`, `RP` executive reporting |

---

## 12. Dependencies

| Depends on | Why |
|---|---|
| `05-06` §9 | The locale standards this implements and, in four places, overrides |
| `05-02` DM-08 | UTC storage, Asia/Dhaka display |
| `BN-006` §7 | Numeral glyph rendering consequences |
| `MD-041` Business calendar | Holidays and the weekend `BD-04` depends on |
| `MD-028` SLA definitions | The pause rules `BD-05` defers to |
| `MD-006`, `MD-007` | Place names and address validation |
| `MD-013` | Name and phone storage |
| `LG-015`, `DT-031` | Why `BD-06` is a financial rule |

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | Numeral glyph rendering; §7 CLDR default |
| [`BN-005_i18n_Key_Placeholder_and_Pluralisation_Rules.md`](BN-005_i18n_Key_Placeholder_and_Pluralisation_Rules.md) | The ICU formatters `FM-02` requires |
| [`BN-004_Do_Not_Translate_and_Transliteration_Register.md`](BN-004_Do_Not_Translate_and_Transliteration_Register.md) | Identifier and export rules |
| [`BN-015_Bengali_Document_and_Print_Template_Pack.md`](BN-015_Bengali_Document_and_Print_Template_Pack.md) | Where amount-in-words and statutory formats are applied |
| [`../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) | §5 proposal; `NU-05` superseded by `FM-07` |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | The SLA definitions §7 serves |
| [`../04_Notification_and_Messaging/04A_SMS_and_OTP/NT-004_SMS_Template_Library_Customer.md`](../04_Notification_and_Messaging/04A_SMS_and_OTP/NT-004_SMS_Template_Library_Customer.md) | §3.4 correction |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. **The numeral question closed** — Arabic default with a declared Bengali-digit context list, overriding the CLDR `beng` default; five locale overrides identified against the CLDR source with the cost of each stated; currency symbol fixed as a prefix, superseding `VB-009` `NU-05`; Bengali day-period words replacing the Latin AM/PM CLDR supplies for `bn`; amount-in-words rules; **the Bangladesh weekend override, with CLDR's absent `BD` weekend data identified as a service-credit exposure**; phone, address, name and identifier formats; ten automated checks; five open decisions | Content Design Lead with Localisation Lead and Finance Controller (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] **The numeral decision `CG-010` §12 item 3 defers here is made**, with the prohibited contexts listed and the reason for each
- [x] **Every locale default that must be overridden is identified against the CLDR source, dated, and costed**
- [x] **The Bangladesh weekend defect is identified, with its financial consequence traced to `LG-015` service credits**
- [x] Currency, date, time, duration, phone, address, name and identifier formats stated for both locales
- [x] Amount-in-words specified as generated and verified, not typed
- [x] Existing content that contradicts this standard is identified and routed to its owner (§3.4, `FM-10`)
- [x] Machine-interchange formats separated from presentation formats throughout
- [x] Every rule that can be a build or configuration test is one
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; internal standard, English-only by `CG-010` §3.2
- [ ] **§3 numeral decision ratified** — outstanding; §11 item 1, `W1` blocker for every bundle
- [ ] **`BD-01` weekend confirmed and `MD-041` verified to carry it** — outstanding; §11 item 3, `W1` blocker for SLA configuration
- [ ] **`FM-07` currency prefix confirmed by Finance** — outstanding; §11 item 2
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
