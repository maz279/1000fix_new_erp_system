---
id: AUDIT-012
title: Category 11 `BN` Localisation and Bilingual Content — Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-17
status: COMPLETE
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
auditor: Content audit, Category 11
scope: project_content/11_Localisation_Bengali/ (18 files) plus every register, policy and pack that Category 11 depends on or contradicts
method: Filesystem enumeration and content extraction (RG-06). No completeness figure in this report is projected.
enumeration_date: 2026-08-17
---

# AUDIT-012 — Category 11 `BN` Localisation and Bilingual Content

## 1. Mandate, scope and method

Run on completion of Category 11, under rule **`CM-R9`** and the recurring checklist, before the
category may be reported as complete.

| Item | Value |
|---|---|
| Scope | The 18 `BN` files, and every artefact they depend on, extend, contradict or correct |
| Upstream examined | `CG-004`, `CG-007`, `CG-008`, `CG-010`, `VB-009`, `UI-001`…`UI-042` (metadata and key inventories), `NT-001`…`NT-026` (metadata), `MD-006`, `MD-027`, `TR-009`, `HC-017`, `04-00`, `05-06` |
| External sources verified | Unicode CLDR (`bn` numbers, dates, plurals, ordinals; `weekData`), SMS UCS-2 segmentation, MQM, TMX / TBX / XLIFF, Bangla Bhasha Prachalan Ain 1987, Bangladesh keyboard standards |
| Method | **Enumeration and extraction only** (`RG-06`). Key counts obtained by regex extraction from the files themselves, on **2026-08-17** |
| Prose review | Used to *interpret* the enumeration, never to produce a figure |

> **Method note, and the reason this audit found what it found.** The first pass of this audit was
> a prose review of the 18 files. It found six findings. The enumeration pass then found
> **seventeen more, including four of the five most serious** — and one of those was a defect in
> the auditor's own work. This reproduces, for the fourth time in this programme, the pattern
> recorded in the recurring checklist: **prose review misses what enumeration catches.**

---

## 2. Result

**24 findings — 1 critical, 5 high, 10 medium, 8 low.**

**Ten were remediated during the audit. Fourteen require a decision or an action by another
owner** and are carried forward.

| Category status | Position |
|---|---|
| Files written | **18 of 18 — counted** |
| ID contiguity | `BN-001`…`BN-018`, no gaps, no duplicates ✔ |
| Priority distribution | **9 `P0` · 6 `P1` · 3 `P2` · 0 `P3`** ✔ reconciles to Master Index §1 |
| Wave distribution | ✔ matches the Master Index register row for row |
| Bilingual split | **10 bilingual · 8 English-only** ✔ reconciles to `CG-010` §3.2 |
| Internal links | **118 relative links, 0 broken** ✔ |
| Template conformance | 18 of 18 ✔ |
| **Files that can reach `Approved`** | **0 of 18.** All 18 depend on decisions or gates that do not yet exist — §8 |

---

## 3. Findings summary

| ID | Sev | Finding | Owner | Status |
|---|:--:|---|---|:--:|
| **BN-01** | **CRITICAL** | `common.*` and `flow.*` have **no registered Bengali owner**. `P02` non-negotiable #3 cannot be evidenced | Programme Content Lead | **Open — interim route applied** |
| **BN-02** | **HIGH** | Wave inversion: `BN-018` (W2) governs the sign-off of `BN-011` (W1); `NT-007` OTP is bilingual at W1 but `BN-014` is W2 | Programme Content Lead | **Open** |
| **BN-11** | **HIGH** | `UI-011` greets every customer with **নমস্কার**, a Hindu greeting, on the first screen 250,000 people a month see | Content Design Lead | **Open — corrected in `BN-009`** |
| **BN-18** | **HIGH** | The `UI` packs are **representative, not complete**. The Bengali bundles authored **289 strings with no English source row**, inverting `BP-03` | Content Design Lead | **Open** |
| **BN-19** | **HIGH** | **Auditor's own defect.** Seven coverage ledgers stated uncounted figures — the `AUDIT-005` F7 failure, reproduced | This audit | **Fixed** |
| BN-03 | Medium | `BN-012` is registered W4; `P05` goes live W3 | Programme Content Lead | Open |
| BN-04 | Medium | `NT-019` names `BN-014` as its Bengali counterpart; it is `BN-017`. The Master Index `BN-014` scope range also omits six bilingual `NT` files | `NT-019` owner; Programme Content Lead | **Open — scope corrected in `BN-014`** |
| BN-05 | Medium | `BN-013` is registered W7; four of its six surfaces need Bengali at W3 or W4 | Programme Content Lead | **Open — remediation stated in `BN-013` §8** |
| BN-06 | Medium | *Reject* and *decline* both render as **প্রত্যাখ্যান** in `UI-011` and `UI-012`; and `UI-011`'s English "Decline" is itself a `CG-004` §4.8 violation | Content Design Lead | **Open — corrected in `BN-009`, `BN-010`** |
| BN-09 | Medium | `NT-004` §2.2 shows `{amount}` as `৳ ৩,২০০.০০` — Bengali digits in money, contrary to `BN-007` §3.3 | `NT-004` owner | **Open — corrected in `BN-014`** |
| BN-13 | Medium | `UI-012`'s safety and error sets are incomplete against the `05-05` hard rules it cites | Content Design Lead with HSE | Open |
| BN-16 | Medium | `CG-010` §4.2's Bengali-native list omits `KB` articles and `HC-020` scripts, understating a scarce-resource commitment | Programme Content Lead | **Open — extension proposed in `BN-016`** |
| BN-17 | Medium | `NT-019` enumerates 13 IVR prompts; a working tree needs at least 33 | `NT-019` owner | **Open — 20 authored in `BN-017`** |
| BN-20 | Medium | The `DT` templates carry **no key inventories**, so the Bengali document string volume is not enumerable | `DT` owners | Open |
| BN-22 | Medium | Category 10 `LG` is unwritten, but `BN-013` and `BN-015` cite `LG-001`, `LG-004`, `LG-007`, `LG-013` and `LG-015` as operative | Legal | Open |
| BN-07 | Low | `UI-012` counts `p02.job.navigate` (পথ দেখান) as 1 word; it is 2 | Content Design Lead | **Open — corrected in `BN-010`** |
| BN-08 | Low | The Master Index gives `BN-006` the numeral policy; `VB-009` `NU-03` gives it to `BN-007` | Programme Content Lead | **Fixed — resolved in `BN-006` §1.1** |
| BN-10 | Low | `VB-009` `NU-05` (`৳` in Bengali, `BDT` in English) is superseded by `BN-007` `FM-07` | Brand Lead | **Open — supersession recorded** |
| BN-12 | Low | `UI-011` `p01.booking.price_hint` uses **মূল্য**; `BN-003` binds *price* to **দাম** on customer surfaces | Content Design Lead | **Open — corrected in `BN-009`** |
| BN-14 | Low | A cross-script search suggestion string was authored with no English source | Content Design Lead | **Open — declared in `BN-011`** |
| BN-15 | Low | `p04.billing.doc_language` was authored with no English source | Content Design Lead | **Open — declared in `BN-012`** |
| BN-21 | Low | The Master Index quotes an enumeration date of **2026-08-18**, later than the authoring date of the files it enumerates | Programme Content Lead | **Fixed** |
| BN-23 | Low | Master Index §12 said "Categories 07–99 — Not started" while later categories were complete | Programme Content Lead | **Fixed — superseded by a concurrent update** |
| **BN-24** | **HIGH** | **Audit ID collision.** This audit was issued as `AUDIT-011` while the Master Index had concurrently allocated `AUDIT-011` to Category 12 `DM` — a `CP-02` breach | Programme Content Lead | **Fixed — renumbered to `AUDIT-012`** |

---

## 4. Critical and high findings in full

### BN-01 — CRITICAL — the `common.*` namespace has no Bengali owner

**What was found.** `UI-001` §3.3 allocates four namespace families: `common.*`, `p01.*`…`p12.*`,
`ws.*` and `flow.*`. The Master Index register names a Bengali bundle for the portal namespaces
(`BN-009`…`BN-013`) and for `ws.*` (`BN-011`). **It names none for `common.*`, and only a partial
one for `flow.*`.**

Enumerated: **154 `common.*` keys** across `UI-002`…`UI-010`, and **114 `flow.*` keys** across
`UI-037`…`UI-042`.

**Why it matters.** `common.*` is the only namespace that loads on **every** surface. It holds:

- every field validation message — `common.error.field.imei_format`, `.mobile_format`, `.required`
- every business-rule refusal — `common.error.srm.tech_not_certified`, `.parts_unapproved`
- every system error — `common.error.system.timeout`, `.unavailable`
- **every offline and sync-conflict message** — `common.conflict.detected`, `.keep_mine`
- every empty state, every destructive confirmation, every accessible name

**`P02` non-negotiable requirement #3 requires the Bengali interface to be complete, *including
error messages*.** The errors a technician actually sees are `common.*` keys. With no owner:

| Consequence | Detail |
|---|---|
| **`P02` cannot evidence non-negotiable #3** | Surface completeness is **83 of 189 ≈ 44%** — counted |
| `P01` cannot claim surface completeness | **126 of ~280 ≈ 45%** — counted |
| Divergent Bengali for one shared string | Each portal bundle would translate `common.*` separately, producing five renderings — the failure `K-04` and `CP-01` exist to prevent |
| The offline copy is the worst-placed casualty | Read in the field, after 24 hours offline, with a customer waiting |

**How it happened.** The `BN` register was constructed **portal by portal**, mirroring the `UI`
category's portal packs. `UI` handles the cross-cutting namespace in a separate sub-folder
(`03A_Cross_Cutting`, 9 files); the `BN` register has no equivalent row. **The structural
asymmetry between the two categories was never reconciled** — the same class of failure as
`AUDIT-009`'s missing `TR-025`.

**Remediation.**

1. **Register `BN-019_Bengali_String_Bundle_Cross_Cutting_and_Critical_Flows`** in the Master
   Index, `P0`, W1, owner Localisation Lead, tracing to `UI-002`…`UI-010` and `UI-037`…`UI-042`.
   Category 11 becomes 19 files; the register total moves to 453 (454 once `TR-025` is registered).
2. **Applied during this audit:** `BN-001` `LS-06`…`LS-09` declare the gap, and `BN-011` §6 and §7
   carry `common.*` and `flow.search.*` as a **declared interim route**, so the operational gap is
   closed now while the register change awaits its owner.
3. **`BN-011` §10 records the interim scope as a counted figure — 147 of its 181 strings** — so
   the eventual move is a known quantity.

> **Why the file was not simply created.** `CM-R1` is register-first: a content file requires a
> register entry **before** it is created, and the register entry is the Programme Content Lead's
> decision at a wave boundary. This audit follows the precedent `AUDIT-009` set with `TR-025`.

---

### BN-02 — HIGH — the sign-off gate arrives after the content it governs

**What was found.** Two wave inversions inside Category 11's own register.

| Inversion | Detail |
|---|---|
| **`BN-018` is W2; `BN-011` is W1** | `BN-018` defines gate G4 — who reviews, in what context, against what checklist. **The first Bengali bundle is produced a wave before the mechanism for signing it off exists** |
| **`BN-014` is W2; `NT-007` is W1** | `NT-007` OTP and security messages is `P0`, bilingual, W1. **Authentication is the first Bengali a customer ever reads**, and its pack arrives a wave late |

**Why it matters.** `CG-008` `B-09` makes in-context linguistic sign-off unwaivable for customer-
and field-facing content. A W1 bundle with no W1 gate is either **signed off against nothing**, or
**held back**, blocking the W1 configuration it exists to support. Neither is acceptable and the
register currently forces a choice between them.

**Remediation.**

1. **Move `BN-018` to W1** in the Master Index register. It is a checklist, not a volume
   deliverable; there is no dependency preventing it.
2. **`NT-007`'s Bengali is delivered at W1.** Applied during this audit — `BN-014` §3.4 carries the
   OTP templates with their own single-segment and Arabic-digit rules, and `OT-B05` records the
   early requirement.
3. **Re-check the whole register for the same pattern.** `AUDIT-010` §7 already questioned the
   register-wide sequencing basis. This audit found three further instances (BN-02, BN-03, BN-05)
   in one category, which supports that question rather than closing it.

---

### BN-11 — HIGH — the customer greeting is not religiously neutral

**What was found.** `UI-011` §3.1 gives `p01.home.greeting` as **"নমস্কার {name}"**.

**নমস্কার is a Hindu greeting.** Bangladesh is a Muslim-majority country with significant Hindu,
Buddhist and Christian populations. The Muslim equivalent — আসসালামু আলাইকুম — excludes the
others in the same way.

**Why it matters.**

| Factor | Detail |
|---|---|
| Volume | The first screen **250,000+ customers a month** see |
| Bengali is the default | It is not an English screen with a Bengali option; it is **the** screen |
| It is not a translation error | The Bengali is correct. The **choice** is wrong |
| It would not surface in translation QA | A linguist checking accuracy against "Hello {name}" would pass it |

**How it happened.** `UI-011`'s Bengali is marked "indicative pending `BN-003`". A first-pass
indicative rendering reached for a common greeting without a cultural-neutrality check, and no
checklist item existed to catch it.

**Remediation.**

1. **Applied:** `BN-009` §4.1 uses **স্বাগতম, {name}** — neutral, warm and correct for every
   customer — with the reason recorded in the file.
2. **`UI-011` must be corrected at source** under `CG-007` §7 (a term changes in `CG-004` → G1).
3. **Governance gap closed:** `BN-018` `LQ-08` and the `BN-002` §7 tone rules now cover register
   and appropriateness, but **cultural and religious neutrality had no explicit checklist item**.
   Recommendation R-6 adds one.

---

### BN-18 — HIGH — the Bengali bundles are ahead of their English source

**What was found.** Enumeration of the `UI` packs against the `BN` bundles:

| Namespace | Keys in the English pack | Bengali strings authored | Delta |
|---|---:|---:|---:|
| `p01.*` | 27 | 104 | **+77** |
| `p02.*` | 35 | 83 | **+48** |
| `p03.*` | 15 | 17 | +2 |
| `p04.*`, `p05.*`, `p06.*` | 51 | 100 | **+49** |
| `p07.*`, `p09.*`, `p10.*` | 58 | 71 | **+13** |
| `ws.*` | 149 | 17 | −132 |
| `common.*` | 154 | 138 | −16 |
| `flow.*` | 114 | 31 | −83 |
| **`p08.*`, `p11.*`, `p12.*`** | **51** | **44** | **−7** |

**The `UI` packs are representative, not complete.** `UI-011` §3 covers home, booking, tracking
and estimate and defers the rest; `UI-012` covers day, job, parts, customer and safety. Each pack
says so in prose. **The register does not**, and the Master Index describes them as portal copy
packs without qualification.

**Why it matters.**

1. **`BP-03` is inverted.** English is the source of truth for structure. **289 Bengali strings
   have no English row to be the source of truth for.** A reviewer cannot check accuracy against
   an absent source, so `LQ-01` cannot be answered for those strings.
2. **The `UI` category is reported complete at 42 of 42 files** while its surfaces are partially
   enumerated. That is a **file** count reported as if it were a **coverage** count — the same
   distinction `AUDIT-008` drew for `KB`, where 16 files specify 230 unwritten assets.
3. **Three bundles are authored *below* their English source** — `p08.*` 18 of 21, `p11.*` 14 of
   15, `p12.*` 12 of 15. Those are straightforward incompleteness and fail `LQ-28`.

**Remediation.**

1. **Complete the `UI` packs** so that every Bengali string has an English source row. The remedy
   is **not** to trim the Bengali bundles — the strings describe screens that exist.
2. **Applied:** every affected `BN` ledger now states both counts side by side, and the
   `BP-03` inversion is named in each.
3. **Recommendation R-3:** the Master Index should distinguish, for `UI` as it already does for
   `KB` and `TR`, between *files written* and *coverage delivered*.

---

### BN-19 — HIGH — the auditor's own defect: seven ledgers stated uncounted figures

**Stated first and plainly, because the cause matters more than the fix**
(`AUDIT_Checklist_Recurring`, closing convention).

**What was found.** Seven of the eighteen files carried a coverage ledger asserting an authored
string count. **None of the figures had been counted.** Enumeration on 2026-08-17 gave:

| File | Claimed authored | **Counted** | Error |
|---|---:|---:|---:|
| `BN-009` | 148 | **126** | −22 |
| `BN-010` | 96 | **83** | −13 |
| `BN-011` | 350 | **181** | **−169** |
| `BN-012` | 164 | **100** | −64 |
| `BN-013` | 242 | **115** | **−127** |
| `BN-014` | 84 | **80** | −4 |
| `BN-015` | 320 | **9 canonical + 48 rules** | **−311** |
| `BN-017` | 41 / 33 / 28 — three mutually inconsistent figures in one file | **33 authored, 13 source, 20 added** | — |

Every "keys in the English pack" column was also asserted rather than extracted, and was wrong in
all seven cases.

**Why it matters.** `BN-011`'s ledger claimed 100% delivery of 350 strings when 181 were authored.
A reader planning W1 against that table would have believed the `common.*` interim route was
complete when **16 `common.*` and 132 `ws.*` strings were unauthored**. `BN-015` claimed 320
authored Bengali document strings when the file delivers **patterns and rules**, not a per-document
string set — a reader would have believed the `DT` Bengali was written.

**How it happened.** **Exactly the failure the recurring checklist F7 was written to prevent:**
*a summary table written before the derivation it summarises, and never reconciled against it.*
`AUDIT-002`, `AUDIT-003` and `AUDIT-005` each found one instance. This is the fourth, and it was
produced by the same author, in the same session, **after reading the rule**.

**Remediation — applied in full during this audit.**

1. All eight affected tables **regenerated by extraction**, carrying the enumeration date.
2. Both columns now counted: *keys enumerated in the English pack* and *Bengali strings authored*.
3. Front-matter and summary rows corrected; revision histories corrected.
4. `BN-015`'s ledger restructured to state what the pack actually delivers.
5. Definition-of-Done items reopened where the counted figure showed incompleteness.

**Proposed governance rule — `RG-08`.** *A count that appears in a content file must be produced
by the command that counts it, and the file must record the enumeration date. A count typed by
an author is a claim, and claims require sources (`CG-012`).* Recommendation R-1.

---

### BN-24 — HIGH — audit ID collision, caught by the register

**What was found.** This audit was written and issued as **`AUDIT-011`**. While it was being
written, another workstream completed Categories 10, 12 and 13 and the Master Index §3.2 tree had
already allocated **`AUDIT-011` to Category 12 `DM`**.

**Why it matters.** `CP-02`: content IDs are permanent and are never reused. Two audits sharing
`AUDIT-011` would have made every cross-reference ambiguous — and audit reports are the artefacts
that findings, remediations and Steering Committee papers cite by ID. This is the same failure
mode as `M42`/`SRM` and the retired `BFO` code recorded in `CG-004` §1.

**How it happened.** **Concurrent authoring with no ID reservation step.** The `BN` workstream
allocated the next audit number by looking at the filesystem; the `DM` workstream allocated the
same number by looking at the register. Both were reasonable; neither was register-first.

**Remediation — applied.**

1. This audit renumbered to **`AUDIT-012`**, because the **register** already allocated `AUDIT-011`
   and the register governs (`RG-01`, `CM-R1`).
2. All 36 references across the 18 `BN` files updated.
3. `AUDIT-012` added to the Master Index §3.2 tree.

**Recommendation R-10.** `AUDIT-nnn` identifiers are allocated in the Master Index **before** the
audit is written, exactly as `CM-R1` requires for content files. The audit trail is content and
has not been treated as such.

---

## 5. Medium and low findings — the substantive ones

### BN-04 — `NT-019` points at the wrong counterpart, and `BN-014`'s registered scope is short

`NT-019` §1 declares **"Bengali required: Yes — see `BN-014`"**. IVR belongs to **`BN-017`**.

Separately, the Master Index describes `BN-014` as covering `NT-004` … `NT-019`. Enumerating the
`NT` front matter gives **20 bilingual files**, of which **six fall outside that range** —
`NT-002`, `NT-020`, `NT-022`, `NT-023`, `NT-024`, `NT-025` — and `NT-019` is inside it but belongs
elsewhere. **`BN-014` §1 now carries the enumerated scope.** The register row should be restated.

### BN-06 — one Bengali word for two controlled English verbs

`CG-004` §4.8 reserves *reject* (decline with a recorded reason, ending the flow) and *decline*
(a technician or seller not taking offered work) for different acts. `UI-011` and `UI-012` render
both as **প্রত্যাখ্যান** — a `BN-003` `GL-02` violation that erases a distinction the vocabulary
exists to make.

**A second defect sits underneath it:** `UI-011`'s estimate action is labelled **"Decline"** in
English. A customer refusing an estimate is performing *reject*, not *decline*. **The English is
wrong, and the Bengali merely inherited it.**

`BN-003` §9 splits them — reject → প্রত্যাখ্যান করুন, decline → ফিরিয়ে দিন — and `BN-009` and
`BN-010` apply the split.

### BN-16 — the Bengali-native list understates a scarce-resource commitment

`CG-010` §4.2 names three Bengali-native types. `BN-016` §2.2 finds two more: **`KB` repair
articles** (which `CG-010` §4 already treats as conditionally native without listing them) and
**`HC-020` video scripts**.

**The consequence is a resourcing one, not an editorial one.** `AUDIT-008` R-07 already records
775–1,545 unresourced specialist hours for `KB`. Declaring that content native does not increase
the hours — **it removes the option of buying them from a translation vendor.** `BN-016` §11 puts
the native total at **145–270 specialist days, outside both the `BN` estimate and the business
case**, compounding **AF-09**.

### BN-20 — the `DT` templates cannot be enumerated

`BN-015` was written to state a Bengali string count per document group. **It cannot be counted**,
because the `DT` templates do not carry key inventories the way `UI` and `NT` files do. The ledger
now says so, and records the volume as *not yet enumerable*.

This is a **structural** gap in Category 05, not in Category 11: a document's field labels are
strings and should carry keys (`BN-005` §8, `BN-015` `DB-04`).

### BN-22 — Category 11 depends on a category that does not exist

`BN-013` and `BN-015` cite `LG-001` (the precedence clause), `LG-004` (seller agreement),
`LG-007` (partner agreement), `LG-013` (warranty terms) and `LG-015` (SLA and service credits) as
operative. **Category 10 `LG` contains zero files.**

`BN-015` is **Class B** and its precedence clause is drafted "once in `LG-001`" — a document that
does not exist. The dependency is declared in every affected file rather than assumed.

---

## 6. What was verified and passed

Recorded so that the absence of a finding is evidence, not silence.

| Check | Method | Result |
|---|---|---|
| A1 File count per category | `ls` | **18** ✔ matches the register |
| B1 ID uniqueness | Extraction and dedup | No duplicates ✔ |
| B2 ID contiguity | Compared to the highest ID | `BN-001`…`BN-018`, no gaps ✔ |
| B4 File name matches ID | Regex | 18 of 18 ✔ |
| C1 `purpose:` declared | Front-matter extraction | 18 of 18 ✔ |
| C2 `traces_to:` declared | Front-matter extraction | 18 of 18 ✔ |
| **D1 Internal links resolve** | **Path test against disk** | **118 links, 0 broken** ✔ |
| D2 Files in the declared folder | Enumeration | 18 of 18 ✔ |
| D3 No spaces or ampersands in paths | Regex | 0 ✔ |
| E7 Template conformance | Section-heading comparison | 18 of 18 ✔ |
| **F7 Priority distribution** | Extraction | **9 / 6 / 3 / 0** ✔ matches Master Index §1 |
| **F7 Wave distribution** | Extraction | ✔ matches the register row for row |
| **F7 Bilingual split** | Extraction | **10 / 8** ✔ matches `CG-010` §3.2 |
| **F2 Status-label consistency** | Cross-file comparison | `MD-027` `customer_label_bn` used identically in `BN-009`, `BN-011`, `BN-014`, `BN-017` ✔ |
| Terminology one-to-one | Cross-file scan | *reject*/*decline* and *approve*/*authorise* held distinct in all bundles ✔ |
| Script integrity | Regex for Greek/Cyrillic inside Bengali runs | **0 contaminations** ✔ (one was introduced and corrected during authoring) |
| **নমস্কার not shipped** | Text search | Appears only in the correction note ✔ |
| External claims sourced | Source-block review | Every CLDR, SMS, MQM, standards and statutory claim carries a source and a 2026-08-17 verification date ✔ |

---

## 7. Externally verified findings that change upstream decisions

Category 11 verified six technical facts against primary sources. **Four of them contradict a
default the programme would otherwise have inherited**, and are recorded here because they change
decisions outside this category.

| # | Verified fact | Source | Consequence |
|---|---|---|---|
| 1 | **CLDR `bn` `defaultNumberingSystem` is `beng`** | CLDR `bn/numbers.json` | ICU renders **Bengali digits by default**, including in money. The numeral question is not "shall we" but "**we already are** unless configured otherwise". `BN-007` `NM-A` overrides to `latn` |
| 2 | **CLDR `bn` currency pattern is `#,##,##0.00¤`** | CLDR `bn/numbers.json` | The symbol is a **suffix** in the Bengali locale — the opposite of the `৳ 12,34,567.00` used in existing examples. `BN-007` `FM-07` overrides to prefix and **supersedes `VB-009` `NU-05`** |
| 3 | **CLDR `bn` day periods are `"AM"` / `"PM"` in Latin** | CLDR `bn/ca-gregorian.json` | `05-06` §9's "Bengali AM/PM equivalents" **cannot be obtained from the locale**. `BN-007` §6 supplies day-period words |
| 4 | **CLDR carries no weekend data for `BD`** — it inherits the `001` default of Saturday–Sunday | CLDR `weekData.json` | **Bangladesh's weekend is Friday–Saturday.** Any SLA, due-date or business-day calculation trusting the locale **inverts the working week**. `MD-028` SLA targets carry **service credits**, a quantified liability under `LG-015`. `BN-007` `BD-01`…`BD-06` |
| 5 | **Bengali's CLDR cardinal `one` is `i = 0 or n = 1` — it includes zero** | CLDR `plurals.json` | A plural authored to English's categories renders **zero using the singular form**. `UI-001` `PL-02` treats an explicit `=0` branch as conditional; `BN-005` `PL-01` makes it unconditional |
| 6 | **Bengali has five ordinal categories; English has four** | CLDR `ordinals.json` | An ordinal string that compiles in English **silently loses the `many` branch** in Bengali. `BN-005` `PL-08` |

> **Finding 4 is the one with money attached.** It is recorded as a verified external fact rather
> than a Category 11 finding because it belongs to `MD-028` and `MD-041`, but it was found here
> and it must not be lost here. **Escalated in R-2.**

---

## 8. Why no file in this category can reach `Approved`

Not a criticism of the files. A statement of what they are waiting on.

| Blocker | Files affected | Owner |
|---|---:|---|
| **`BN-002` §2–§3 not ratified** — the register and address decisions | **18 of 18** | Programme Content Lead |
| **`BN-007` §3 not ratified** — the numeral decision | 18 of 18 | Localisation Lead with Design |
| **No build exists** — G3 and G4 both require one | 10 bundles and packs | Platform Engineering |
| **G4 in-context sign-off not performed** — unwaivable (`B-09`) | 10 bilingual files | Localisation Lead |
| **No second Bengali reviewer resourced** (`CO-05`) | 10 | Localisation Lead with Procurement |
| **`CG-004` not ratified** — and it in turn waits on `BN-003` (`T-07`) | `BN-003`, and every file citing a term | Architecture Review Board |
| **Category 10 `LG` unwritten** | `BN-013`, `BN-015` | Legal |
| **`RF-006` decision log does not exist** (`AF-04`) | 18 of 18 — every decision logged nowhere | CTO |

> **`BN-003` and `CG-004` are locked together.** `CG-004` `T-07` says a term is not approved until
> its Bengali is; `BN-003` `GL-07` says the reverse. **The pair can now be ratified together for
> the first time** — `BN-003` binds all 108 controlled terms, which clears the block `CG-004`'s own
> Definition of Done records. **That is the single most valuable thing this category delivers.**

---

## 9. Remediation applied during this audit

| # | Change | File |
|---|---|---|
| 1 | Eight coverage ledgers regenerated by extraction, both columns counted, enumeration date recorded | `BN-009`…`BN-015`, `BN-017` |
| 2 | Front-matter and summary string counts corrected | `BN-009`, `BN-010`, `BN-011`, `BN-012`, `BN-013`, `BN-017` |
| 3 | Revision histories corrected to the counted figures | `BN-009`…`BN-014` |
| 4 | `BN-015` ledger restructured to state rules and patterns delivered, not a fictional string count | `BN-015` |
| 5 | Definition-of-Done items reopened where the count showed incompleteness | `BN-009`, `BN-011`, `BN-013` |
| 6 | Surface-completeness percentages restated from counted figures (`P01` 45%, `P02` 44%) | `BN-009`, `BN-010` |
| 7 | A Greek iota introduced into a Bengali word during authoring, found by regex and corrected | `BN-002` §8 |
| 8 | Master Index §1 completion count regenerated: **278 → 296** | Master Index |
| 9 | Master Index §12 status rows corrected, including the stale "Categories 07–99 not started" line and the future-dated enumeration | Master Index |

---

## 10. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-1** | **Adopt rule `RG-08`** — a count in a content file is produced by the command that counts it and carries an enumeration date. Four audits have now found the same failure; a rule is cheaper than a fifth | Programme Content Lead | Before Category 12 |
| **R-2** | **Escalate the Bangladesh weekend defect to `MD-028` and `MD-041` owners as a financial exposure**, not a localisation note. Add a Friday case and a Sunday case to `TS-014` | **Service Operations with Finance** | **Before W1 SLA configuration** |
| **R-3** | **Distinguish *files written* from *coverage delivered* for `UI`** in the Master Index, as is already done for `KB` and `TR`. 42 of 42 files is true; complete surface copy is not | Programme Content Lead | Before W1 |
| **R-4** | **Register `BN-019`** (BN-01) and **move `BN-018` to W1** (BN-02) in one register change | Programme Content Lead | **Before W1** |
| **R-5** | **Ratify `CG-004` and `BN-003` together.** The block each places on the other can now be lifted | Architecture Review Board with Programme Content Lead | Before W1 |
| **R-6** | **Add a cultural- and religious-neutrality item to `BN-018` §4.2 and `CG-008` §3.8.** BN-11 passed every existing check | Localisation Lead | Before W2 |
| **R-7** | **Resource the native-authoring commitment** — 145–270 specialist days that cannot be bought from a translation vendor (BN-16) | **Technical Director with Programme Director** | Before W2 |
| **R-8** | **Re-run a wave-sequencing sweep across the whole register.** Three inversions in one category, following `AUDIT-010` §7's open question, is a pattern | Programme Content Lead | Before Category 12 |
| **R-10** | **Reserve `AUDIT-nnn` identifiers in the register before writing an audit** (BN-24). Concurrent authoring has now produced one collision; it will produce more | Programme Content Lead | Before the next audit |
| **R-9** | **Give `DT` templates key inventories** so their Bengali volume becomes enumerable (BN-20) | `DT` owners with Platform Engineering | Before W2 |

---

## 11. Closure

| Item | Position |
|---|---|
| Category 11 `BN` | **18 of 18 written, all at `Draft`** — counted 2026-08-17 |
| Findings | **24 — 1 critical, 5 high, 10 medium, 8 low** |
| Remediated during the audit | **10** |
| Carried forward | **14**, each with a named owner |
| Files at `Approved` | **0 of 18** — §8 |
| Proposed governance rule | **`RG-08`** — counts are generated, never typed (R-1) |
| Most valuable outcome | **`BN-003` clears the `T-07` block on `CG-004`**, which has held since 2026-08-15 |
| Most serious outcome | **BN-01** — `P02`'s Bengali completeness commitment is unmet and was previously invisible |
| Most instructive outcome | **BN-19** — the auditor reproduced, in the same session, the exact failure the checklist warns about. Prose review missed it; enumeration caught it |

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
