---
id: BN-005
title: i18n Key, Placeholder and Pluralisation Rules
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Platform Engineering and Content Design
reviewers: [Platform Engineering, Mobile Engineering, Content Design Lead, Design System, QA Lead, all portal owners]
approver: Content Design Lead with Localisation Lead
content_class: D
purpose: >
  The localisation-owned counterpart of UI-001. It states the placeholder, plural, ordinal,
  gender and context-note rules that make a string translatable into Bengali, and the build
  behaviours that stop an untranslated string reaching a user. Concatenated strings cannot be
  assembled in Bengali word order, and the prohibition must reach developers before the first
  sprint, not at the first translation batch. Bengali's CLDR plural category "one" includes
  zero, so a plural authored to English's categories renders the singular form for an empty
  list — a defect that is invisible in English testing and visible on every empty screen in
  Bengali.
traces_to: [UI-001, UI-001 P-01, UI-001 P-03, UI-001 PL-01, UI-001 §9, CG-003 S-05, CG-010 BC-03, BN-001 LR-07, BN-002 SC-01, BN-006, BN-007, 05-06 NFR-016, 05-06 §9, PS-08]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: Unicode CLDR supplemental plurals.json — locale bn cardinal rules, "pluralRule-count-one":"i = 0 or n = 1 @integer 0, 1 @decimal 0.0~1.0, 0.00~0.04"; locale en, "pluralRule-count-one":"i = 1 and v = 0 @integer 1"
    verified: 2026-08-17
    class: P1
  - source: Unicode CLDR supplemental ordinals.json — locale bn ordinal rules, five categories: one "n = 1,5,7,8,9,10", two "n = 2,3", few "n = 4", many "n = 6", other
    verified: 2026-08-17
    class: P1
  - source: Unicode CLDR cldr-numbers-full bn/numbers.json — defaultNumberingSystem "beng"; decimal pattern "#,##,##0.###"; currency pattern "#,##,##0.00¤"
    verified: 2026-08-17
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-001 §3.1 key format, §3.2 K-01…K-07, §4.1 P-01…P-05, §4.2 PL-01…PL-03, §9 open questions 1–4
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 — UTF-8 throughout, ICU bn-BD collation; §5 NFR-016 full Bengali and English support in interfaces, notifications, reports and data entry
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-08 — offline-capable with queued sync for P02, P09, P11; §P02 non-negotiable #1, 24 hours offline with no data loss
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-005 — i18n Key, Placeholder and Pluralisation Rules

> **`UI-001` decides the key scheme. This file decides what makes a string survive contact with
> Bengali.** They are ratified together and must not diverge (`CP-01`). Where they do, `UI-001`
> governs key structure and naming; this file governs message format, plural behaviour,
> translator context and build enforcement.
>
> **The rule this file exists for:** a string that is assembled from fragments in English cannot
> be reassembled in Bengali, because Bengali puts the verb last (`BN-002` `SC-01`). By the time a
> translator sees the fragments, the damage is in the code and costs a sprint to undo. This must
> reach developers **before the first sprint**, which is why it is `P0` at `W1`.

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | ICU message format, placeholders, plurals, ordinals, selects, context notes, bundle structure, offline bundling, and the build checks that enforce all of it |
| **What it does not govern** | Key naming and namespace allocation (`UI-001` §3); which Bengali word is used (`BN-003`); how a number is formatted once ICU has it (`BN-007`); typography (`BN-006`) |
| **What breaks without it** | Concatenated sentences that cannot be translated, plurals that show the singular form for zero, ordinals missing two categories, a technician's phone falling back to English mid-shift, and translators guessing at context |

---

## 2. What `UI-001` already fixes

Not repeated here. Cited so this file can build on it.

| From `UI-001` | Rule |
|---|---|
| `K-01` | Keys are semantic, never the source text |
| `K-02` | Lower snake_case; no Bengali script in a key |
| `K-05` | A key is permanent; changing the English does not change the key |
| `K-07` | No key is defined in code; keys are declared in the pack, then implemented |
| `P-01` | Named placeholders only; positional placeholders are prohibited |
| `P-03` | No concatenation across a translatable boundary |
| `PL-01` | Every count-bearing string uses ICU plural |

---

## 3. Message format

### 3.1 ICU MessageFormat is mandatory

| # | Rule |
|---|---|
| **KP-01** | **ICU MessageFormat is the message format for every surface**, across all five frameworks — Odoo OWL, Next.js, React Native, Flutter and any reporting layer that renders a user-visible string |
| **KP-02** | Where a framework has no native ICU support, an **adapter is built**. The message format is not downgraded to the framework's capability. `UI-001` §9 item 1 records this as open for Odoo OWL and it is a `W1` blocker |
| **KP-03** | One bundle format across all frameworks (`UI-001` §9 item 2). A per-framework format multiplies the translation pipeline by five |
| **KP-04** | Bundles are **UTF-8, NFC-normalised** (`05-06` §9, `BN-006` `EN-02`). A bundle in NFD looks identical and fails every string comparison |

### 3.2 Placeholders

```
{customer_name} approved the estimate on {approved_at, date, medium}
{amount, number, ::currency/BDT}
{count, plural, =0 {…} one {…} other {…}}
```

| # | Rule |
|---|---|
| **KP-05** | **No concatenation across a translatable boundary.** `"You have " + n + " items"` is prohibited. Author the whole sentence, per plural form (`UI-001` `P-03`, `CG-003` S-05, `BN-002` `SC-05`) |
| **KP-06** | **A placeholder may appear anywhere in the Bengali, in any order.** The translator moves it; the developer must not assume position. This is the practical consequence of `P-01` |
| **KP-07** | **Every placeholder is documented** with: name, source field, data type, an example value, whether it may be empty, and its maximum realistic length (`UI-001` `P-02`, `BN-002` §9) |
| **KP-08** | **A placeholder that carries a full clause is a concatenation in disguise.** `{reason}` inside "This is taking longer. {reason} We will update you." is permitted only because `{reason}` resolves to a **translated, whole sentence** from `MD-026`. A `{reason}` holding an English fragment is a defect |
| **KP-09** | Dates, numbers, currency and percentages use **ICU formatters**, never pre-formatted strings. The locale decides the form (`BN-007`) |
| **KP-10** | A placeholder that could contain user input is **escaped at render**, and the pack states so |
| **KP-11** | **Bengali may need a placeholder the English does not** — most often a classifier or postposition attached to a value. Where it does, the Bengali string is authored with the particle inline, never by adding a second placeholder |
| **KP-12** | **Never place a placeholder immediately adjacent to a Bengali case-marking suffix without a plan.** `{mobile}-এ` works because the hyphen separates the Latin value from the Bengali suffix; `{device}র` does not, because the correct suffix depends on the word ending. Where the suffix varies, restructure the sentence |

> **`KP-12` is the most common Bengali placeholder defect and it does not exist in English.**
> Bengali attaches postpositional suffixes to nouns — এ, তে, র, ের, কে — and which one is correct
> depends on the final sound of the word the placeholder resolves to. `NT-004` handles this
> correctly by writing `{mobile}-এ রসিদ পাঠানো হয়েছে`, using the hyphen to detach the suffix from
> a Latin-script value. For a Bengali-script value the sentence must be restructured instead.

### 3.3 Selects

| # | Rule |
|---|---|
| **KP-13** | `{gender, select, …}` is **not used**. Bengali marks no grammatical gender on verbs or adjectives (`BN-002` `SC-09`), and the English surfaces do not require it |
| **KP-14** | `{select}` **is** used for genuine variant text — delivery mode, contract type, channel. Every branch is authored; there is no implicit fallthrough |
| **KP-15** | A `select` **must** declare an `other` branch, and `other` must be a complete sentence, not a placeholder for a case someone forgot |

---

## 4. Plurals — the Bengali difference

### 4.1 Cardinal categories

Both languages use two CLDR categories. **The categories are not the same categories.**

| | English `one` | Bengali `one` |
|---|---|---|
| CLDR rule | `i = 1 and v = 0` | **`i = 0 or n = 1`** |
| Integers matched | 1 | **0, 1** |
| Decimals matched | — | 0.0–1.0, 0.00–0.04 |

**Zero is `one` in Bengali and `other` in English.**

```json
"common.parts.count": {
  "en": "{n, plural, =0 {No parts} one {# part} other {# parts}}",
  "bn": "{n, plural, =0 {কোনো পার্টস নেই} one {#টি পার্টস} other {#টি পার্টস}}"
}
```

| # | Rule |
|---|---|
| **PL-01** | **Every count-bearing string authors an explicit `=0` branch**, in both languages. `UI-001` `PL-02` makes this conditional on the wording differing; **in Bengali it is unconditional**, because without it zero renders through the `one` branch |
| **PL-02** | Both `one` and `other` are declared explicitly in both languages. Neither relies on a runtime default |
| **PL-03** | Bengali nouns do not inflect for number. `one` and `other` frequently carry **identical text**, and that is correct, not a copy-paste error. A reviewer must not "fix" it (`BN-018` `LQ-08`) |
| **PL-04** | The `#` token renders the number through the locale's number formatter (`BN-007`). Never substitute a bare `{n}` beside a hand-written numeral |
| **PL-05** | Never build a plural by appending "(s)" or "গুলো" mechanically (`UI-001` `PL-03`) |
| **PL-06** | The Bengali classifier — টি, টা, জন, খানা — is part of the authored string and is chosen per noun. **জন for people, টি for things.** "৩টি টেকনিশিয়ান" is wrong; "৩ জন টেকনিশিয়ান" is right |
| **PL-07** | A count string that will exceed one line in Bengali at the target size is a **design conversation**, not a copy problem (`UI-001` §8) |

> **Why `PL-01` is a `P0` rule and not a nicety.** Every empty state in the system is a zero
> count. `UI-006` is an entire pack of them. On the English build, zero falls into `other` and
> reads "0 parts", which is odd but harmless. On the Bengali build, zero falls into `one` and
> reads as the singular. The defect appears **only in Bengali**, **only on empty screens**, and
> those are the first screens every user sees at go-live.

### 4.2 Ordinal categories

| Language | Ordinal categories |
|---|---|
| English | `one` (1st), `two` (2nd), `few` (3rd), `other` |
| **Bengali** | **`one`** (1, 5, 7, 8, 9, 10) · **`two`** (2, 3) · **`few`** (4) · **`many`** (6) · `other` |

**Bengali has five ordinal categories. English has four.**

| # | Rule |
|---|---|
| **PL-08** | An ordinal string uses `{n, selectordinal, …}` and **declares all five Bengali categories**. A string authored to English's four silently loses the `many` branch |
| **PL-09** | Where an ordinal is not essential, **use a cardinal instead**. "Step {n} of {total}" is safer than "the {n}th step" and reads better in both languages |
| **PL-10** | Queue position, step numbers and rankings — `ivr.position`, booking step indicators, league tables (`RP-011`) — are the surfaces where ordinals actually occur. Each is checked at `BN-018` |

---

## 5. Context notes

A translator with a string and no context produces a defect that costs more to find than to
prevent. `BN-002` §9 states the obligation; this section states the format.

Every key in every pack carries:

| Field | Content | Example |
|---|---|---|
| `context` | What the string is and where it appears | "Primary button on the technician job screen, lower third, one-handed reach" |
| `slot` | The component and its budget | "Button, 20 characters Bengali rendered" |
| `audience` | Who reads it | "Field technician, outdoors, in motion" |
| `tone` | The `VB-002` row | "Direct, ≤ 12 words" |
| `placeholders` | Per `KP-07` | `{part}` — `fix.part.display_name`, string, "কম্প্রেসর", never empty, max 40 |
| `screenshot` | Required for any constrained slot | `p02-job-parts.png` |
| `do_not_translate` | Tier 1 items present in the string | `IMEI` |

| # | Rule |
|---|---|
| **CX-01** | A string extracted **without** a context note fails the build. It is not sent for translation and then queried (`BN-002` `TX-01`) |
| **CX-02** | Context notes are authored by the **content author**, not generated from the key. A key is a location; a context note is a meaning |
| **CX-03** | Context notes travel through the whole pipeline — pack, extraction, XLIFF, TM, review tool (`BN-008` `TM-05`) |
| **CX-04** | Where two keys hold the **same English** but different meanings, each context note states the difference explicitly. This is the only defence against `GL-02` collisions in Bengali |
| **CX-05** | A **screenshot** is required for every string in a button, chip, badge, tab, table header or notification preview — the slots where truncation happens |

---

## 6. Bundle structure and loading

| # | Rule |
|---|---|
| **BU-01** | One bundle per namespace per locale: `p02.bn.json`, `p02.en.json`, `common.bn.json` (`UI-001` `K-06`) |
| **BU-02** | Namespaces load on demand. A portal never loads another portal's namespace |
| **BU-03** | **`common.*` loads on every surface.** It is the only namespace that does. This is why it needs a single owning Bengali bundle (`BN-001` §4) |
| **BU-04** | **`P02`, `P09` and `P11` bundle strings at build time, not at runtime.** A technician offline for 24 hours cannot fetch a language pack (`PS-08`, `P02` non-negotiable #1). `UI-001` §9 item 3 records this as open; the offline requirement decides it |
| **BU-05** | The **font is bundled with the strings** on those three surfaces (`VB-009` `TF-02`). A bundled Bengali string with no bundled Bengali font renders as tofu |
| **BU-06** | Bundle files are **UTF-8 without BOM**; export files for Excel are UTF-8 **with** BOM (`BN-004` §7). These are different rules for different destinations and both are load-bearing |
| **BU-07** | A locale bundle declares its `lang` tag: **`bn-BD`**, not `bn`, not `bn-IN` (`05-06` §9). `bn-IN` selects Indian conventions and different default formats |

---

## 7. Build enforcement

**The rules above are only real if the build refuses to ship a violation.**

| # | Check | Behaviour |
|---|---|---|
| **BE-01** | A key present in `en` and missing in `bn` | **Build failure.** Never a runtime fallback to English (`BN-001` `LR-07`) |
| **BE-02** | A key present in `bn` and missing in `en` | Build failure — an orphan translation means the English was retired without retiring the Bengali |
| **BE-03** | An unresolved placeholder at render | **Build failure, never a runtime message** (`UI-001` §5) |
| **BE-04** | Placeholder sets differ between `en` and `bn` for the same key | Build failure. A dropped placeholder is a silent information loss |
| **BE-05** | A count-bearing string without an explicit `=0` branch | Build failure (`PL-01`) |
| **BE-06** | An ordinal string without all five Bengali categories | Build failure (`PL-08`) |
| **BE-07** | A key containing Bengali script, uppercase or a hyphen | Build failure (`UI-001` `K-02`) |
| **BE-08** | A string literal in source code rather than in a bundle | Build failure (`UI-001` `K-07`) |
| **BE-09** | Bundle not NFC-normalised | Build failure (`KP-04`) |
| **BE-10** | A string with no context note | Build failure (`CX-01`) |
| **BE-11** | A Tier 1 item transliterated in the Bengali bundle | Build failure (`BN-004` `EN-01`) |
| **BE-12** | A Bengali string exceeding its declared slot budget | **Warning at build, failure at the wave gate.** The remedy is a design change, not truncation (`UI-001` §8) |
| **BE-13** | `bn` bundle string identical to the `en` string, where the English contains no Tier 1 item | Warning — usually an untranslated string that was copied forward |
| **BE-14** | Two keys with different English mapped to identical Bengali | Warning at build; **checked at `BN-018` `LQ-11`** |

| # | Rule |
|---|---|
| **BE-15** | **`BE-01` has no waiver.** "Ship English for now and translate later" is how a surface reaches 97% and stays there. `PS-03` and `P02` non-negotiable #3 admit no partial state |
| **BE-16** | Warnings are reported per commit and **must be zero at the wave gate** (`BN-001` §9) |

---

## 8. Reports, documents and messages

Strings outside the UI are still strings, and they break in the same ways.

| Surface | Rule |
|---|---|
| **Notifications** | Same key scheme, same ICU format, same plural rules. A template ID like `sms.cust.booked` is a key (`NT-004`) |
| **SMS** | Placeholder values change the **segment count** in Bengali. A template that fits in two segments with a 6-character `{branch}` may need three with a 20-character one. Segment count is measured at the **realistic maximum**, not the example (`BN-014` §3) |
| **Documents** | Field labels are keys. A `DT` template's Bengali labels come from a bundle, not from the layout file (`BN-015` `DB-04`) |
| **Reports** | Column headers, filter labels, aggregate labels and null placeholders are all strings (`RP-002`). **A report that shows "N/A" in an otherwise Bengali table has an untranslated string** |
| **IVR** | Prompt text is a key; the **recording** is the artefact. Changing the string requires re-recording (`BN-017` `VP-09`) |
| **Emails** | Subject, preview text, alt text and the plain-text part are all strings (`NT-009`, `VB-005`) |
| **PDF metadata** | Title, author and subject are user-visible in a viewer's tab and in file listings (`CG-010` §5) |
| **Errors from integrations** | A gateway's English error is **mapped to our own message key**, never surfaced raw (`UI-004`, `NT-021`) |

---

## 9. Open questions

Inherited from `UI-001` §9, with the localisation position stated. **All four are `W1` blockers.**

| # | Question | Localisation position | Owner |
|---|---|---|---|
| 1 | Does Odoo OWL support ICU MessageFormat natively, or is an adapter needed? | **An adapter is built** (`KP-02`). The plural and ordinal rules in §4 cannot be expressed without ICU, and `P03` carries the largest string volume in the system | Platform Engineering |
| 2 | One extraction pipeline across five frameworks, or per framework with a shared bundle format? | **Shared bundle format is mandatory** (`KP-03`); a shared pipeline is preferred. Five pipelines means five places for `BE-01` to be implemented differently | Platform Engineering |
| 3 | Do Flutter surfaces bundle strings at build or fetch at runtime? | **Bundle at build** (`BU-04`). The 24-hour offline requirement decides it; this is not an open question in practice | Mobile Engineering |
| 4 | Do Bengali numerals in placeholders follow the `BN-007` decision? | **Yes, without exception.** The ICU number formatter is configured from `BN-007` §3 and no string overrides it | Localisation Lead |

---

## 10. Dependencies

| Depends on | Why |
|---|---|
| `UI-001` | Key scheme and namespace allocation; ratified together |
| `BN-002` | `SC-01` word order, `SC-05` concatenation, §9 translator inputs |
| `BN-003` | The terms the strings must use |
| `BN-004` | Tier 1 items inside strings (`BE-11`) |
| `BN-006` | NFC normalisation, font bundling |
| `BN-007` | What the ICU formatters are configured to produce |
| `BN-008` | Where context notes and TM segments live |
| `BN-018` | The human checks `BE-14` defers to |
| `05-06` §9, `PS-08` | Encoding, collation and offline constraints |

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-001_UI_String_Architecture_and_i18n_Key_Standard.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-001_UI_String_Architecture_and_i18n_Key_Standard.md) | The counterpart; ratified together |
| [`BN-001_Localisation_Strategy_and_Language_Coverage_Matrix.md`](BN-001_Localisation_Strategy_and_Language_Coverage_Matrix.md) | `LR-07`, the `common.*` ownership question `BU-03` depends on |
| [`BN-007_Date_Time_Number_Currency_and_Address_Formats.md`](BN-007_Date_Time_Number_Currency_and_Address_Formats.md) | What `KP-09` formatters produce |
| [`BN-014_Bengali_Notification_and_SMS_Pack.md`](BN-014_Bengali_Notification_and_SMS_Pack.md) | Segment-count consequence of placeholders |
| [`BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md`](BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md) | `LQ-08`, `LQ-11` |
| [`../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md`](../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md) | S-05, the concatenation prohibition in English authoring |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. ICU mandated across five frameworks with an adapter rather than a downgrade; fifteen placeholder rules including the Bengali postposition-suffix rule; **the CLDR finding that Bengali's `one` category includes zero**, making an explicit `=0` branch unconditional; **the five-category Bengali ordinal finding**; seven-field context-note format; offline bundling rules; sixteen build-enforcement checks with `BE-01` declared unwaivable; the four `UI-001` open questions answered from the localisation side | Content Design Lead with Localisation Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Does not repeat `UI-001`; cites it and builds on it (`CP-01`)
- [x] **Bengali plural behaviour verified against the CLDR source, not assumed** — the zero-in-`one` finding is sourced and dated
- [x] **Bengali ordinal categories verified against the CLDR source** — five, not four
- [x] Placeholder rules cover the Bengali-specific postposition problem, which has no English analogue
- [x] Context-note format specified field by field, with the build check that enforces it
- [x] Offline bundling stated as a decided consequence of `PS-08`, not left open
- [x] Every rule that can be a build check is one, and the unwaivable check is named
- [x] Non-UI string surfaces covered — notifications, documents, reports, IVR, email, PDF metadata, integration errors
- [x] All four `UI-001` §9 open questions answered from the localisation side
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; internal standard, English-only by `CG-010` §3.2
- [ ] **Odoo OWL ICU adapter confirmed** — outstanding; §9 item 1, `W1` blocker
- [ ] **Shared bundle format confirmed** — outstanding; §9 item 2, `W1` blocker
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
