---
id: FIX-ERP2-AUDIT-013
title: Category 10 LG — Legal, Policy and Compliance Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 24 Category 10 LG files, their citations into the module repository and the content register, cross-register integrity, gates F3 and F6, and the resolution of inbound findings carried from AUDIT-010 and AUDIT-012
mandate: Audit required on completion of Category 10 authoring (rule CM-R9)
extends: AUDIT-001 … AUDIT-012
enumeration_date: 2026-08-18
method: Filesystem enumeration and identifier extraction only (RG-06, CP-11). No figure in this report is projected, and none is taken from what a document says about itself.
---

# Category 10 `LG` — Legal, Policy and Compliance Content Audit

### 24 files · 352 of 452 registered content files now written

---

## 1. Method and result

Checks **A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F7** and **G1–G5** of
`AUDIT_Checklist_Recurring.md`, answered by running the extraction, never by reading a document's own
claim about itself (`RG-06`, `CP-11`). **Enumeration date 2026-08-18.**

Nine category-specific extractions were run:

| Extraction | What was compared |
|---|---|
| **X1** | Every content identifier cited, against the 452 register rows |
| **X2** | Every `BRU-` identifier, against the full module repository |
| **X3** | Every `FR-`, `NFR-`, `SOD-`, `EA-` and `PS-` identifier, against the module repository |
| **X4** | Every governance rule identifier (`CP-`, `CM-R`, `T-A/B/C`, `EV-`, `PR-`, `WV-`, `SO-`, `RG-`), against `00_Content_Governance_and_Standards/` and the register |
| **X5** | Register filenames against disk, both directions |
| **X6** | Front-matter key count per file, against the 24-key `TPL_Content_File_Front_Matter.md` contract |
| **X7** | Template section spine per file, against `TPL_Legal_Document.md` |
| **X8** | **Gate F3** — `LG-015` §4.3 and §4.6 against `MD-028` §2 and §9, and against `DT-031` §4.1 and §4.2 |
| **X9** | **Gate F6** — `LG-008` purposes against `LG-009` retention rows, bidirectionally; and the residency field list across `LG-008`, `LG-012` and `05-06` §6.4 |

**Fourteen findings — 1 critical, 4 high, 6 medium, 3 low.** Three were remediated during the audit;
eleven are open, and **nine of those are owned outside the content function.**

| Severity | Count | Fixed | Open |
|---|---:|---:|---:|
| Critical | 1 | 0 | 1 |
| High | 4 | 1 | 3 |
| Medium | 6 | 2 | 4 |
| Low | 3 | 0 | 3 |

> **The headline is not a content defect.** All twenty-four files are written, every identifier
> resolves and every gate that can be run passes — **except F3, which fails between two documents
> that were both already written and approved as drafts before this category started.** Finding
> **LG-01** is upstream of Category 10 and was found only because `LG-015` had to reproduce
> `MD-028`'s field names in order to comply with the rule that binds them.

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | 24 of 24 ✅ |
| **A2** Total written | **352 of 452**, enumerated 2026-08-18 ✅ |
| **A5** Files on disk with no register entry | Zero ✅ |
| **A6** Register entries with no file | Zero for Category 10 ✅ |
| **B1** ID uniqueness | 24 unique, front matter and filename agree in all 24 ✅ |
| **B2** Contiguity `LG-001`…`LG-024` | No gaps ✅ |
| **B4** File name matches ID | 24 of 24 ✅ |
| **C1/C2** `purpose:` and `traces_to:` present | 24 of 24 ✅ |
| **D1** Internal links resolve | **380 relative links, zero broken** ✅ *(two were broken and were fixed — finding LG-12)* |
| **D2** Files in their declared folder | 24 flat in `10_Legal_Policy_and_Compliance/`, matching Master Index §3.2, which declares no `LG` subfolders ✅ |
| **D3** No spaces or ampersands in any path | Zero ✅ |
| **E7 / X7** Template conformance | **23 files carry all ten `TPL_Legal_Document.md` sections in order plus the DoD; `LG-001` carries all six generic sections plus the DoD** ✅ |
| **F1 / X6** Front matter complete | **All 24 required keys present in all 24 files** ✅ |
| **X1** Content-ID citations | **158 distinct identifiers cited; 157 registered.** The one exception is `TR-025`, declared — see §3 note ✅ |
| **X2** `BRU-` citations | **266 distinct identifiers, all 266 resolve** ✅ *(272 before remediation — finding LG-05)* |
| **X3** `FR-`/`NFR-`/`SOD-`/`EA-`/`PS-` citations | **48 `FR-`, 24 `NFR-`, and every `SOD-`, `EA-` and `PS-` identifier resolve** ✅ |
| **X4** Governance rule citations | **53 distinct rule identifiers, all resolve** in the `CG` set, the register or the checklist ✅ |
| **X5** Register filenames vs disk | **Byte-identical, both directions, 24 of 24** ✅ |
| **X9** Gate **F6** | **Reconciles on all seven axes** — see §2.2 ✅ |

> **On `TR-025`.** `LG-020` §4.12 and `LG-022` §4.9.5 cite `TR-025` — the Layer 1 statutory induction
> curriculum — as the vehicle for policy attestation and for the ISO 9001 clause 5.2.2 *understanding*
> evidence. **`TR-025` is not in the register.** That is not an invented identifier: `AUDIT-009`
> finding **TR-01** already established that `TR-025` must be registered, taking Category 08 to 25
> files and the register to 453. Both citations name it in plain text and **neither hyperlinks it**,
> which is what `CG-012` `EX-03` requires of a planned document. **Category 10 has now given
> `AUDIT-009` TR-01 two more consumers.**

### 2.1 Cross-register reconciliation — gate F7

**All seven dimensions reconcile exactly.**

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---|---:|:--:|
| File count | Master Index §4 | 24 | 24 | ✅ |
| Contiguity | `CP-02` | `LG-001`…`LG-024` | No gaps | ✅ |
| Content class A / B | `CG-002` §4.1 | **6 / 18** | **6 / 18** | ✅ |
| Bilingual / English-only | `CG-010` §3.2 | **16 / 8** | **16 / 8** | ✅ |
| Template 10 / template 1 | `CG-009` §3, §3.1 | **23 / 1** | **23 / 1** | ✅ |
| Priority `P0`/`P1`/`P2`/`P3` | Master Index §1 | **7 / 10 / 7 / 0** | **7 / 10 / 7 / 0** | ✅ |
| Wave per file | Master Index §4 rows | W1 4 · W2 11 · W3 3 · W4 3 · W5 1 · W7 2 | All 24 match | ✅ |

**Class A (6):** `LG-008`, `LG-009`, `LG-012`, `LG-018`, `LG-019`, `LG-024`.
**English-only (8):** `LG-001`, `LG-003`, `LG-004`, `LG-005`, `LG-006`, `LG-007`, `LG-021`, `LG-024`.
**Template 1 (1):** `LG-001` — matching `CG-009` §3's note that *"`LG-001` uses template 1 — it is a
register"*.

> **`CG-002` §4.1 and `CG-010` §3.2 state these splits as category totals and never enumerate them
> per file.** The allocations above were therefore **derived**, with the reasoning recorded in
> `LG-001` §4.2 and §4.3 so they are re-examinable rather than re-invented. **This is finding LG-11**,
> reported rather than silently absorbed.

### 2.2 Gate F6 — the data-protection reconciliation

Check F6 reads *"Legal documents do not contradict each other on data protection — **manual review**
of `LG-008`, `LG-009`, `LG-012`"*. **Manual review of three long documents finds nothing reliably**,
so the three files were built to make the check mechanical, and it was then run mechanically.

| Axis | Method | Result |
|---|---|---|
| Purpose → retention | `LG-008` §4.2 declares purposes `P-01`…`P-20`; `LG-009` §4.2 declares rows `RC-01`…`RC-23`, each naming its purpose | **All 20 purposes have a retention row** ✅ |
| Retention → purpose | Reverse extraction | **All 23 rows are referenced back from `LG-008`** ✅ *(fixed during the audit — see LG-07)* |
| Residency field list | `LG-012` §4.3 against `05-06` §6.4 | **Identical — 7 field rows across 6 entities, character for character on the entity names** ✅ |
| Residency field list | `LG-008` §4.2 residency column against `LG-012` §4.3 | Consistent ✅ |
| Erasure overrides | `LG-009` §4.5 is the single source; `LG-010` `RF-03` quotes it verbatim under rule `RF-R4` | One override set, one wording ✅ |
| Rights timelines | `LG-008` §4.4, `LG-010` §4.4 | **30 days for rectification in both, traced to `BRU-CPM-10`** ✅ |
| Third-party tags as transfers | `LG-011` §4.3 third-party rows against `LG-012` §4.6 | **Rule `F6-06` written to bind them; the register itself is empty — finding LG-03** ⚠ |

---

## 3. Findings

### LG-01 — Gate F3 fails today, between two documents that were already written

**Severity: CRITICAL · Status: OPEN · Owner: Enterprise Architecture with Legal Counsel**

**What was found.** Check **F3** requires SLA definitions to be **identical** across `MD-028`,
`DT-031` and `LG-015`, *"zero divergence — these carry financial liability"*. `MD-028` validation rule
`SLA-03` enforces one half of it as a **hard block**: an SLA band cannot be activated if its
`credit_calculation` diverges from `LG-015`'s wording.

Authoring `LG-015` required reproducing `MD-028`'s field names. Extraction **X8** compared them:

| `DT-031` §4.1/§4.2 maps to `MD-028` | Exists in `MD-028` §2? |
|---|---|
| `MD-028.priority_code` | **No** — the field is `sla_band_code` |
| `MD-028.priority_name_en` / `_bn` | **No** — the fields are `band_name_en` / `band_name_bn` |
| `MD-028.definition` | **No such field** |
| `MD-028.response_target` | **No** — the field is `response_target_min` |
| `MD-028.resolution_target` | **No** — the field is `resolution_target_min` |
| `MD-028.coverage_window` | **No** — the fields are `clock_runs` and `business_calendar_code` |
| `MD-028.measurement_basis` | **No such field** |
| `MD-028.clock_start_event` | **No such field** |
| `MD-028.clock_stop_event` | **No such field** |

**Nine field references, none of which exist.**

**Why it is Critical.** `AUDIT_Checklist_Recurring.md` defines Critical as *"work done against the
wrong artefact, or a required artefact assumed present when absent."* Both apply:

1. **`DT-031` `FM-31-a` states that every value in its commitments table is "read from `MD-028`, not
   entered"** — and it names nine fields the register cannot supply. A build to `DT-031` would be a
   build against a schema that does not exist.
2. **Two of the missing fields are substantive, not cosmetic.** `MD-028` has **no clock start or stop
   event field at all**, and `DT-031` §1.1 names *when the clock starts and stops* as one of the four
   ambiguities *"every SLA dispute the company will ever have"* is about. **The register the system
   measures against cannot express the commitment the contract makes.**
3. `MD-028` has **no `definition` field**, while `DT-031` prints a per-band definition and `L-31-b`
   requires values *"copied, not paraphrased"*. A definition that exists only on the printed annex is
   a definition with no controlled source.

**How it happened.** `DT-031`'s own Definition of Done leaves the item **"Check F3 run against
`MD-028` and `LG-015` — zero divergence"** unticked and marked *"outstanding; blocks `Approved`"*.
**The gate was correctly identified as outstanding and was never run, because the third document did
not exist.** Category 10 is the first point at which it could be run.

**Remediation instruction.** Three changes, and none is a wording edit:

1. **Correct `DT-031` §4.1 and §4.2 to `MD-028`'s actual field names.**
2. **Extend `MD-028` §2 with `definition`, `clock_start_event` and `clock_stop_event` columns.**
   `LG-015` §4.4 defines the events; `MD-028` must be able to hold them.
3. **Re-run F3 across all three** before any of them reaches `Approved`.

Recorded as `LG-015` `O-02`, `O-03`, `O-04`.

---

### LG-02 — Six unwaivable G6 gates, no external adviser commissioned, and W1/W2 files in scope

**Severity: HIGH · Status: OPEN · Owner: Legal Counsel with the Programme Director**

**What was found.** Extraction of `content_class` gives **6 Class A files**, and `CG-007` §2.1 makes
**G6 statutory verification mandatory** for every one. `CG-007` `WV-02` is unambiguous: **"G5 and G6
can never be waived. There is no authority in this programme to publish unreviewed legal or statutory
content."**

The gate load, counted from `LG-001` §4.7:

| Gate | Count | Service level | Driver |
|---|---:|---|---|
| G1 Editorial | 24 | 3 working days | Content Design |
| G2 Factual | 24 | 5 working days | Domain owners |
| **G3 Technical** | **2** | 5 working days | `LG-015`, `LG-019` — both system-pinned |
| **G4 Linguistic** | **16** | 5 days **after English approval** | Independent reviewer, in context |
| **G5 Legal** | **24** | **10 working days each** | **Legal Counsel** |
| **G6 Statutory** | **6** | **15 working days, driven by external adviser availability** | **Four different specialisms** |

**And G6 needs four specialisms, not one:** an external **tax** adviser (`LG-009`), a **data
protection** adviser (`LG-008`, `LG-009`, `LG-012`), an **environmental** adviser (`LG-018`), and an
external **legal** adviser (`LG-019`, `LG-024`).

**Why it matters.** `LG-013` and `LG-022` are **`W1`**. Six files carrying G6 are **`W2`**.
`CG-007` §3.6 states plainly that statutory content *"is scheduled with this lead time; it is not
requested at a wave gate."* **`CG-013` `CR-01` already records legal review capacity as the binding
constraint on 75 Class A and B files across the register — 24 of them are here.**

**Remediation instruction.** Commission the four external reviews at **W0**, not at the W1 and W2
gates. Recorded as `LG-001` `O-03`.

---

### LG-03 — Four upstream decisions block the category, and one of them blocks 20+ retention rows elsewhere

**Severity: HIGH · Status: OPEN · Owner: Steering Committee**

**What was found.** Four decisions sit outside the content function and each blocks a file from
reaching `Approved`:

| Decision | Blocks | Recorded where | Status |
|---|---|---|---|
| **`D-13` split-residency legal opinion** (`05-06` `DEP-31`) | `LG-008`, `LG-012`, and **every consent string** | `CG-013` `CR-08` states it: *"`LG-008`, `LG-012` and every consent string may be wrong"* | **Outstanding. `05-06` requires it before the Wave 1 architecture is fixed** |
| **`D-03` marketplace principal-or-agent** (`RSK-022`) | `LG-004` §4.5, §4.6, §5.2; `LG-014` `EN-09`; `DT-039` | `BRU-MKP-15` and `BRU-TAX-17` both refuse to build until it is documented | **Outstanding** |
| **E-waste regulated-entity question** (`LG-018` `EW1`) | `LG-018` §4.2 in full; `LG-024` `OB-16`…`OB-21`; `LG-006` §4.7.8 | `LG-018` `O-02` | **Outstanding — and may already be overdue** |
| **The limitation period** (`LG-009` `RT8`) | **More than twenty `DT` retention rows**, `LG-009` §4.2 and §4.3, `DT-031` §9 | `LG-009` `O-02` | **Outstanding** |

**The fourth is the one to act on first, and it is the cheapest.** Extraction across
`05_Document_and_Print_Templates/` found the phrase *"plus the limitation period"* in more than twenty
retention rows and in `DT-031` §9. **No document in the repository states the number.** Until it is
stated, `M24` `FR-DMS-035` cannot compute a disposal date for the contract, warranty, custody,
complaint or dispute record classes — **which is most of the estate's legally significant records.**

**Why it matters.** These are not Category 10 questions. `LG-004` is drafted with §4.5 as two explicit
alternatives rather than a term, precisely because `BRU-MKP-15` prohibits building on an
undocumented determination. **That is the right authoring behaviour and it does not make the file
usable.**

**Remediation instruction.** Table all four at the next Steering Committee as one paper. **The
limitation period is a single question to Legal Counsel with a repository-wide effect and should not
wait for the other three.**

---

### LG-04 — Wave-sequencing inversion, now the fifth consecutive category

**Severity: HIGH · Status: OPEN · Owner: Programme Content Lead**

**What was found.** Extraction of `wave:` against the citation graph found **six inversions inside
Category 10**, where a file is forward-referenced by a file that ships earlier:

| Governing file | Wave | Forward-referenced by | Wave |
|---|:--:|---|:--:|
| **`LG-018`** E-waste and environmental | **W5** | `LG-017` §4.7.4 | **W2** |
| **`LG-018`** | **W5** | `LG-009` `DC-14` | **W2** |
| **`LG-018`** | **W5** | `LG-006` §4.7.8 | **W3** |
| **`LG-021`** ISMS | **W2** | `LG-020` §4.2, §4.5 | **W1** |
| **`LG-023`** Ethics and whistleblowing | **W3** | `LG-020` `AU-16`, `AU-18` | **W1** |
| **`LG-024`** Obligation register | **W3** | `LG-018` §4.2.8 — **a W3 file waiting on a W5 file, which is waiting on it** | **W5** |

The last row is a **circular** dependency across three waves: `LG-018` needs `LG-024` to hold the
environmental obligations, and `LG-024` needs `LG-018`'s `EW1` answer to write them.

**This is the fifth consecutive category with the same defect shape.** `AUDIT-008` found it three
times in `KB`; `AUDIT-009` twice in `TR`; `AUDIT-010` twice in `HC` plus a dependency variant;
`AUDIT-012` found *"two further wave inversions"* in `BN`. **`AUDIT-010` §7 already concluded that
"the register was sequenced by when a file's subject matures rather than by when its consumers need
it, and the remaining twelve categories will inherit the same defect unless the sequencing basis is
corrected once."** Two of those twelve have since been authored and both inherited it.

**Remediation instruction.** **Do not fix this category's six inversions individually.** Correct the
sequencing basis once, register-wide, as `AUDIT-010` R-02 and `AUDIT-012` already asked. Recorded as
`LG-018` `O-04`, `LG-020` `O-03`, `LG-006` `O-02`, `LG-017` `O-07`, `LG-024` `O-04`.

---

### LG-05 — Eight invalid business-rule identifiers, caught by extraction

**Severity: HIGH · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Extraction **X2** returned **272 distinct `BRU-` identifiers** cited across the
category. Comparing them against every `BRU-` identifier in the module repository, **seven did not
exist**, appearing eight times across six files:

`BRU-GRC-25` · `BRU-GRC-26` · `BRU-GRC-27` · `BRU-GRC-34` · `BRU-GRC-36` · `BRU-GRC-43` ·
`BRU-GRC-44`

**`M60` §9 contains `BRU-GRC-01`…`BRU-GRC-22` and no more.** The seven are **`FR-GRC-*` feature
identifiers carried across with a `BRU-` prefix** — `FR-GRC-025` obligation calendar, `-026` change
monitoring, `-027` licence register, `-034` cross-border transfer register, `-036` breach register,
`-043` continuity governance, `-044` whistleblowing case management.

**Why it is High and not Medium.** A `BRU-` identifier is a **hard business rule with a named owner
and an enforcement point**; an `FR-` identifier is a **feature**. Citing a feature as a rule asserts
that the platform blocks something it merely provides for. In a legal document that distinction is the
difference between *"the system prevents this"* and *"the system supports this"* — and `LG-021` §4.14
maps policies to enforcing rules, so a mis-typed prefix would have propagated into a control map shown
to an auditor.

**How it happened.** `M60` is the only module in the repository where the `FR-` and `BRU-` families
share the same three-letter code (`GRC`) **and** overlap numerically, so `FR-GRC-036` and a
hypothetical `BRU-GRC-36` are visually indistinguishable in a citation. `AUDIT-010` recorded the
mirror-image trap for `BRU-CAI-*`, which exists in `M32` §9 but not in `05-05`.

**Remediation — applied.** All eight corrected to `FR-GRC-0nn`, or removed where the correct `FR-`
identifier was already cited alongside. **X2 re-run: 266 distinct identifiers, all 266 resolve.**

**Recommendation.** A citation check comparing `BRU-`/`FR-` prefixes against the owning register
belongs in the automated `CG-013` §8 commit scan, alongside the existing escalation-marker and
word-trigger scans.

---

### LG-06 — `MD-031` cannot carry the warranty exclusions the rule requires it to carry

**Severity: MEDIUM · Status: OPEN · Owner: Master Data Owner with Legal Counsel**

**What was found.** `MD-031` §2 marks the `exclusions` column *"Must match `LG-013` verbatim"*, and
validation rule `WTY-02` makes a divergence a **hard block on activation**. `LG-013` §4.6 was
therefore written as a numbered, quotable list `EX-01`…`EX-18` rather than as prose.

Extracting `MD-031` §9's sample rows found two defects:

| Defect | Detail |
|---|---|
| **Missing mandatory columns** | The sample CSV header carries `warranty_type_code, warranty_class, name_en, name_bn, brand_code, duration_months, starts_from, covers, claim_window_days, transferable, is_sellable, effective_from, active`. **`device_families` and `exclusions` are absent**, and §2 marks both **required (✔)**. `item_code` is also absent |
| **A period expressed in the wrong unit** | The 30-day repair warranty is registered as `duration_months = 1`. **Thirty days and one month are not the same period**, and the difference decides a claim made on day 31 of a 31-day month |

**Why it matters.** The first is the more serious: **a load built from that sample cannot satisfy
`WTY-02`, because the column that would carry `LG-013`'s text is not in it.** The control would pass
vacuously, or the load would fail, depending on implementation — and both outcomes look like a data
problem rather than a legal one.

**Remediation instruction.** Correct `MD-031` §9 to include `device_families`, `exclusions` and
`item_code`; express the standard repair warranty in **days**, or add a `duration_days` column.
Recorded as `LG-013` `O-04`, `O-05`.

---

### LG-07 — Completion figures were stale in three places, and the F7 sweep found two of them

**Severity: MEDIUM · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Filesystem enumeration on 2026-08-18 gives **352** written content files.
At the start of this audit:

| Location | Said | Enumerated |
|---|---|---|
| Master Index §1 | **351 of 452**, *"10 `LG` at 23 of 24 … a floor, not a ceiling"* | 352 |
| Master Index §12 | **351 of 452** | 352 |
| README "Current position" | **345 of 452** | 352 |
| README Category 10 row | *"In progress — 19 of 24"* | 24 of 24 |

**Three different figures — 345, 351 and 352 — in two files.** All three were honest counts taken at
different instants while Categories 10 and 13 were being authored concurrently, and each was correctly
dated. **The defect is not the counting; it is that a derived figure was restated in three places and
only one was refreshed.**

**Why it is reported and not silently fixed.** This is the third audit to find the same shape.
`AUDIT-005` changed a bilingual total from 268 to 266 and found the old figure **restated in eleven
further places across four files**, which is why check **F7 includes a repository-wide sweep**.
`AUDIT-012` `BN-23` found the *"Categories 07–99 — Not started"* line surviving while later categories
were complete. **The mechanism keeps working and the discipline keeps lapsing under concurrency.**

**Remediation — applied.** F7 sweep run with `grep` for `351` and `of 452` across the whole
repository. All three figures regenerated to **352 of 452**, each carrying the 2026-08-18 enumeration
date and an explicit note that it supersedes the earlier floors. Category 10 status rows added to both
files. `AUDIT-013` registered in Master Index §3.2 **before this report was written** — see LG-13.

**Also fixed under F6.** `LG-008` `P-10` expressed its retention reference as a range,
`` `RC-10`…`RC-13` ``, which an extraction reads as two identifiers rather than four. The F6 reverse
check therefore reported `RC-11` and `RC-12` as unreferenced. **Enumerated rather than ranged**, so the
gate is now genuinely mechanical in both directions.

---

### LG-08 — `05-06` has three identifier defects, one of them a live collision

**Severity: MEDIUM · Status: OPEN · Owner: CTO with Enterprise Architecture**

**What was found.** Category 10 cites 24 distinct `NFR-` identifiers, all of which resolve.
**Three of them resolve to two different requirements each.**

| Identifier | `05-06` §6.3 says | `05-06` §7 says |
|---|---|---|
| **`NFR-090`** | *Process personal data only on consent or a stated legitimate ground* — `M33`, **P0** | *Unit test coverage ≥ 80% on custom code; 100% on financial calculations* — P0 |
| **`NFR-091`** | *Consent must be clear, explicit, specific and freely given* — `M33`, **P0** | *Every module ships with an operational runbook* — P0 |
| **`NFR-092`** | *Issue a transparency notice before or during processing* — `M33`, **P0** | *Distributed tracing across all services with a single correlation id* — P1 |

**Two further defects in the same document:**

- Its own title line reads **`# NFR-001 … NFR-092`** while the document contains **`NFR-101`**.
- The table **"Fields currently classified as residency-restricted"** in §6.4 has two stray rows
  appended after its seven field rows: `NFR-088` records retention and `NFR-089` SOC 2 / ISO 27001
  readiness. **They are three-column rows in a three-column table, so they render as fields**, and a
  reader could take "SOC 2 / ISO 27001 readiness" for a residency-restricted data field.

**Why it matters.** `NFR-092` is the transparency-notice obligation and is the single most-cited
requirement in `LG-008`, `LG-010` and `LG-011`. A collision means **`traces_to: [NFR-092]` is
ambiguous across the whole repository**, and `CG-007` G3 requires every cited `NFR-` to exist *in its
owning register* — which it does, twice.

**How it happened.** `05-06` revision 2.1 added §6.3 (ten new PDPA requirements) and §6.4 (four
residency requirements) as **audit corrections C-04 and C-05**, numbering upward from `NFR-086`
without checking that `NFR-090`–`NFR-092` were already in use in §7. **The correction that fixed a
statutory-currency defect introduced an identifier defect.**

**Remediation instruction.** Renumber the §6.3 PDPA requirements — they are the newer set — to
`NFR-102`+, or renumber §7. Correct the title range. Move the two stray rows out of the residency
table. **`CP-02` applies to `NFR-` identifiers as much as to content IDs, and every content file
citing them must be re-pointed in the same change.**

---

### LG-09 — `05-06` §6.4 does not reflect the amending Ordinance's residency effect

**Severity: MEDIUM · Status: OPEN · Owner: CTO with the Chief Data Officer**

**What was found.** `05-06` §6.1 records the **Personal Data Protection (Amendment) Ordinance 2026
(Ordinance No. 23 of 2026, 5 February 2026)** as amending the Ordinance before it was repealed on
enactment of the Act — **verified 2026-08-12.** §6.4's `NFR-086` split-residency architecture makes no
reference to what the amendment changed.

Research for `LG-012` found published analysis that the amendment introduced a **data-localisation
requirement obliging at least one synchronised real-time copy to be held within Bangladesh** for data
categorised as restricted, or processed by **critical information infrastructure as defined in the
Cyber Security Ordinance 2025**.

**A synchronised in-country copy is a different obligation from split residency.** `NFR-086` holds
sensitive fields in Bangladesh and the remainder in a regional store, joined by a resident key. A
synchronised-copy requirement, if it applies, requires a **complete** in-country replica of the
affected data — which is an architecture change, not a policy change.

**Why it is Medium and not High.** Whether it applies turns on whether the company is critical
information infrastructure, which nobody has determined (see LG-10). **The finding is that the
specification does not currently pose the question**, so nobody would discover it before the Wave 1
architecture is fixed.

**Remediation instruction.** Add the amendment's residency effect to `05-06` §6.4 as an open
requirement pending the `D-13` opinion, and fold it into that opinion's scope. Recorded as `LG-012`
`RD2`, `O-03`.

---

### LG-10 — One unanswered question is asked in three files, with three different consequences

**Severity: MEDIUM · Status: OPEN · Owner: CTO with Legal Counsel**

**What was found.** Three files independently ask whether the company is **critical information
infrastructure** under the Cyber Security Ordinance 2025:

| File | Question | If yes |
|---|---|---|
| `LG-012` | `RD3` | The amending Ordinance's **synchronised in-country copy** requirement may apply (LG-09) |
| `LG-021` | `CS1` | A **distinct incident-reporting regime** applies, and `IS-10` §4.10.2's four notification clocks become five |
| `LG-024` | `RG7` | A **registration or reporting obligation** enters the register as `OB-32` |

**One question, three consequences, three owners, and each file records it as blocking.**

**Why it is reported rather than merged.** Three files asking the same question independently is
**evidence the question is real** rather than an authoring artefact — the same reasoning `AUDIT-010`
`HC-01` applied when three Category 09 files each recorded the transcript-basis question. But three
open items also means three chances for it to be closed inconsistently.

**Remediation instruction.** Consolidate to **one** determination, recorded in `LG-024` §4.3 `OB-32`,
with `LG-012` and `LG-021` citing it. Recorded as `LG-024` `O-09`, `LG-021` `O-02`.

---

### LG-11 — Two governance splits existed only as totals, and had to be derived

**Severity: MEDIUM · Status: FIXED (declared) · Owner: Programme Content Lead**

**What was found.** Gate **F7** requires a category's content-class and bilingual allocations to
reconcile against `CG-002` §4.1 and `CG-010` §3.2. Both state Category 10 as a **total** and neither
enumerates:

- `CG-002` §4.1: `LG` → **6 Class A, 18 Class B**. No file named.
- `CG-010` §3.2: `LG` → **16 bilingual, 8 English-only**, with a one-line rationale: *"Consumer- and
  employee-facing terms, privacy, warranty, refund, data. Vendor, seller, brand and internal policy
  sets remain English."* No file named.

**A total with no allocation cannot be reconciled — it can only be matched by arithmetic.** Any
allocation summing to 6 and 16 would pass F7 while being substantively wrong.

**How it was contained.** Both allocations were **derived with reasoning recorded** in `LG-001` §4.2
and §4.3, including the deciding test for each Class A file and the two allocations most likely to be
challenged (`LG-013` warranty as Class B, `LG-022` ISO 9001 as Class B). `LR-01` and `LR-02` fix them
so they are not re-derived per file. **F7 now passes against a stated allocation rather than an
arithmetic coincidence.**

**One substantive conflict surfaced in the derivation.** `CG-010` §3.2 puts **`LG-004`** — the
marketplace seller agreement — in the **English-only** set, while `CG-010` §3.3's audience rule marks
**marketplace sellers bilingual**. 500–2,000 sellers are predominantly Bengali-first freelance
engineers and small shops, and `BRU-MKP-17` gives them a **right of appeal** against earnings recovery
that they must be able to read. **The two sections of `CG-010` disagree, and the file most affected is
the one where the consequence is a contractual right.** Recorded as `LG-001` `O-01` and `LG-004`
`O-02`; the same tension applies to the recycling-partner and courier variants of `LG-006`
(`LG-006` `O-03`).

**Remediation instruction.** Enumerate both splits per file in `CG-002` §4.1 and `CG-010` §3.2 for the
remaining categories, and **reconcile `CG-010` §3.2 against §3.3 explicitly for `LG-004` and
`LG-006`**.

---

### LG-12 — Two broken links, from a register title that does not match the file

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Extraction **D1** found **2 broken links out of 379**, both to
`VB-002_Tone_of_Voice_and_Writing_Principles.md`. **`VB-002` is
`VB-002_Persona_and_Portal_Tone_Matrix.md`**; the voice and tone guide is `VB-001`.

**Remediation — applied.** `LG-011` §10 re-pointed to `VB-002`'s actual filename with a corrected
description. `LG-018` §10 re-pointed to `VB-001` and `CG-003`, which are the files that actually hold
the tone guidance and the banned-absolutes rules `CX-2` relies on; its `traces_to:` updated to match.
**D1 re-run: 380 links, zero broken.**

**Why it is reported.** The two links were written from the *subject* rather than from the register.
`AUDIT-012` recorded the register-versus-filesystem allocation problem for audit IDs; this is the same
habit applied to a content file, and it is the reason `CG-012` `EX-01` exists.

---

### LG-13 — Audit ID allocation is still not register-first, and this report nearly repeated the collision

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** `AUDIT-012` `BN-24` recorded a **HIGH** finding: that audit was issued as
`AUDIT-011`, discovered that the register had concurrently allocated `AUDIT-011` to Category 12 `DM`,
and renumbered itself — updating 36 references across 18 files. Its **Recommendation R-10** was that
*"`AUDIT-nnn` identifiers are allocated in the Master Index **before** the audit is written."*

**At the start of this audit the `_AUDIT/` folder contained `AUDIT-012` and no `AUDIT-011`**, while
the Master Index §3.2 tree listed `AUDIT-011_Category_12_DM_Content_Audit.md`. Allocating from the
filesystem would have produced `AUDIT-011` for Category 10 — **the identical collision `BN-24`
described, one category later.**

**Remediation — applied.** `AUDIT-013_Category_10_LG_Content_Audit.md` was **added to the Master Index
§3.2 tree before this report was written**, following `AUDIT-012` R-10 and `CM-R1`. The register
governs.

**Why it is Low as a finding and not as a risk.** It was caught, and the cost was nil. But
**`AUDIT-012` R-10 asked for a reservation step and no reservation step exists** — the collision was
avoided by reading the register carefully, which is exactly what `BN-24` says both workstreams
reasonably failed to do.

---

### LG-14 — `UI-042`'s two questions are answered, and one of its answers changes customer-facing copy

**Severity: LOW · Status: OPEN (change requests raised) · Owner: Content Design Lead with the CDO**

**What was found.** `UI-042` §9 asks two questions and marks the first as blocking G6:

| `UI-042` question | Answer, from `LG-008` §4.7 |
|---|---|
| *"Is the residency wording confirmed by Legal and the DPO?"* | **Partly.** *"It is stored in Bangladesh and is not shared"* is correct for National ID and bank details. **It is wrong for TIN**, which appears on statutory outputs and is disclosed to the NBR through filings (`LG-008` `P-03`, `P-16`; `LG-024` `OB-02`). **Change request raised** on `flow.consent.purpose.tin` |
| *"Is the statutory retention period for invoices confirmed at five years?"* | **The statutory minimum is five years; the company's own standard is seven** (`BRU-TAX-24`). `flow.dsr.erase_limits` interpolates `{years}`; **the bound value must be 7**, or the customer is told a shorter period than the company applies. **Change request raised** |

**A third defect was found in the same file.** `UI-042` §9's table has **two data rows above its
header row**, so the two questions it asks of `LG-008` render outside the table structure.

**Why the second answer matters.** It is a **customer-facing misstatement in the making**. The
5-versus-7-year divergence is real, both figures are correct against their own definition, and
`LG-009` §4.4 reconciles them — but a string that tells a customer "invoices for 5 years" while the
company retains for 7 is a transparency defect, not a rounding difference.

**Remediation instruction.** Apply both `UI-042` change requests; correct the §9 table structure.
Recorded as `LG-008` `O-07` (resolved) and in `LG-009` `RS-13`.

---

## 4. Inbound findings resolved

| Finding | Source | Resolution |
|---|---|---|
| **`BN-22`** — *"Category 10 `LG` is unwritten, but `BN-013` and `BN-015` cite `LG-001`, `LG-004`, `LG-007`, `LG-013` and `LG-015` as operative. Category 10 `LG` contains zero files."* `BN-015` is Class B and its precedence clause is drafted *"once in `LG-001`"* — a document that did not exist | `AUDIT-012` | **CLOSED.** All five cited files now exist. **`LG-001` §4.3 also supplies what `BN-015` was waiting for**: rule `LR-03` settles that **English governs in a dispute** for every bilingual `LG` file — closing `CG-010` §12 open question 2, which was registered against `LG-002`, `LG-013` and `LG-015`. `LR-04` preserves the Bengali version's operative effect where a Bengali-reading counterparty relied on it, and `LR-05` routes an unfaithful translation to `CG-013` `T-C06` before either version is approved |
| **`HC-01`** — customer conversation data scheduled to be mined at W2 before the legal basis for it is confirmed; three Category 09 files depend on it | `AUDIT-010` (CRITICAL) | **NOT closed — it is a legal question — but it now has an owning artefact and a gate.** `LG-008` §4.2 registers it as purpose **`P-14`**, marks it **provisional and non-operative**, and `PI-03` states that `HC-015` and `HC-017` cannot mine transcripts until it is answered. The question is `LG-008` `PN5`, addressed to the external data-protection adviser at G6, and `LG-009` `RC-17` gives the derived corpora a retention row conditioned on the same answer |
| **`UI-042` §9 open questions 1 and 2** — residency wording and invoice retention period, the first marked blocking G6 | `UI-042` category work | **Answered in `LG-008` §4.7.1 and §4.7.2**, with two change requests raised against `UI-042` — see finding LG-14 |
| **`CG-010` §12 open question 2** — *"Does English govern in a dispute for bilingual legal documents?"*, registered against `LG-002`, `LG-013`, `LG-015` | `CG-010` | **Resolved in `LG-001` `LR-03`–`LR-05`**, with the limits of a governing-language clause stated rather than assumed |
| **`AUDIT-009` `TR-01`** — the Layer 1 statutory induction curriculum has no owning file; `TR-025` must be registered | `AUDIT-009` | **Not closed; reinforced.** `LG-020` §4.12 and `LG-022` §4.9.5 now depend on `TR-025` as the attestation and understanding-evidence vehicle. **Two more consumers for a file that does not exist** |

---

## 5. Remediation applied during this audit

| # | Change | File |
|---|---|---|
| 1 | **Eight invalid `BRU-GRC-*` identifiers corrected to `FR-GRC-0nn` or removed** (LG-05) | `LG-003`, `LG-008`, `LG-012`, `LG-021`, `LG-023`, `LG-024` |
| 2 | **Two broken links re-pointed**; `LG-018` `traces_to:` corrected from `VB-002` to `VB-001`, `CG-003` (LG-12) | `LG-011`, `LG-018` |
| 3 | **`LG-008` `P-10` retention reference enumerated instead of ranged**, so the F6 reverse check is mechanical (LG-07) | `LG-008` |
| 4 | **Master Index §1 completion figure regenerated: 351 → 352 of 452**, with the superseded floor explained | Master Index §1 |
| 5 | **Master Index §12 completion figure regenerated: 351 → 352** (F7 sweep) | Master Index §12 |
| 6 | **README completion figure regenerated: 345 → 352** (F7 sweep) | README |
| 7 | **Master Index §12 Category 10 status row added** | Master Index §12 |
| 8 | **README Category 10 row updated** from *"In progress — 19 of 24"* to complete, with the blocking findings named | README |
| 9 | **`AUDIT-013` registered in Master Index §3.2 before this report was written** (LG-13) | Master Index §3.2 |
| 10 | **`AUDIT-012` and `AUDIT-013` added to the README audit list** | README |

---

## 6. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Run gate F3 across `MD-028`, `DT-031` and `LG-015`, and correct all three.** Extend `MD-028` with `definition`, `clock_start_event` and `clock_stop_event` columns (LG-01) | **Enterprise Architecture with Legal** | **Before any of the three reaches `Approved`** |
| **R-02** | **Commission four external G6 reviews at W0** — tax, data protection, environmental, legal. `WV-02` makes them unwaivable and `W1`/`W2` files are in scope (LG-02) | **Legal Counsel with Programme Director** | **W0** |
| **R-03** | **Table the four blocking decisions as one Steering paper** — `D-13`, `D-03`, e-waste `EW1`, and the limitation period (LG-03) | **Steering Committee** | Next meeting |
| **R-04** | **State the limitation period.** One question to Legal Counsel; **more than twenty `DT` retention rows and every contract, warranty and dispute disposal date depend on it** (LG-03) | **Legal Counsel** | **Immediately — it is the cheapest of the four** |
| **R-05** | **Correct the register-wide sequencing basis once**, rather than this category's six inversions individually. **Fifth consecutive request** — `AUDIT-008`, `AUDIT-009`, `AUDIT-010` R-02, `AUDIT-012` (LG-04) | **Programme Content Lead** | **W1** |
| **R-06** | **Renumber the `05-06` §6.3 PDPA requirements away from `NFR-090`–`NFR-092`**, correct the title range, and move the two stray rows out of the §6.4 residency table (LG-08) | **CTO** | **W1 — before `traces_to:` propagates further** |
| **R-07** | **Add the amending Ordinance's residency effect to `05-06` §6.4** and fold it into the `D-13` opinion's scope (LG-09) | **CTO with CDO** | **W1** |
| **R-08** | **Determine the critical-information-infrastructure question once**, recorded in `LG-024` `OB-32`, with `LG-012` and `LG-021` citing it (LG-10) | **CTO with Legal Counsel** | **W2** |
| **R-09** | **Correct `MD-031` §9** — add `device_families`, `exclusions` and `item_code`; express the repair warranty in days (LG-06) | **Master Data Owner** | **W1** |
| **R-10** | **Enumerate the content-class and bilingual splits per file in `CG-002` §4.1 and `CG-010` §3.2** for the remaining categories, and reconcile `CG-010` §3.2 against §3.3 for `LG-004` and `LG-006` (LG-11) | **Programme Content Lead with Legal** | **W1** |
| **R-11** | **Apply the two `UI-042` change requests** — the TIN residency wording and the `{years}` value of 7 — and fix its §9 table (LG-14) | **Content Design Lead with CDO** | **W2** |
| **R-12** | **Add a `BRU-`/`FR-` prefix check to the automated `CG-013` §8 commit scan** (LG-05) | Content Design | W2 |
| **R-13** | **Create an `AUDIT-nnn` reservation step**, as `AUDIT-012` R-10 asked. **The collision it recorded was avoided here by care, not by control** (LG-13) | **Programme Content Lead** | **Before the next audit** |
| **R-14** | **Name one accessibility reviewer for all content categories.** `AUDIT-010` R-09 asked, having noted it was the third request. Category 10 makes it the fourth | **Content Design Lead** | **W1** |
| **R-15** | **Add a specification variant to `_templates/`, or amend `CG-009` §3 once.** `AUDIT-008` R-05, `AUDIT-009` R-09 and `AUDIT-010` R-10 each asked; `LG-021` is a fourth category adapting a single-instrument template to a suite of thirteen policies | Content Design | **W2** |

---

## 7. Closure

Category 10 is **complete as specified**: 24 of 24 files written, all seven F7 dimensions reconciling,
**380 internal links resolving, 158 content identifiers, 266 `BRU-` rules, 48 `FR-`, 24 `NFR-` and 53
governance rule identifiers all resolving to their owning register**, template conformance at 24 of
24, and front matter complete at 24 of 24.

**Four observations belong in front of the Steering Committee.**

**First, F3 fails, and it failed before this category existed.** Finding **LG-01** is not a Category 10
defect. `DT-031` and `MD-028` have contradicted each other since both were written, and `DT-031`'s own
Definition of Done recorded the gate as un-run **because the third document did not exist to run it
against**. Two of the nine divergences are substantive: `MD-028` cannot express a clock start or stop
event, and `DT-031` §1.1 names clock start and stop as one of the four things *"every SLA dispute the
company will ever have"* is about. **The register the platform measures against cannot hold the
commitment the contract makes.** This is what F3 was written to catch, and it took the third document
to catch it.

**Second, this category cannot be approved by the content function under any circumstances.** Twenty
four files require G5. Six require G6, which `WV-02` makes **unwaivable** — *"there is no authority in
this programme to publish unreviewed legal or statutory content"* — and which needs **four different
external specialisms**. `LG-013` and `LG-022` are `W1`. **Every other category has ended with content
that could in principle be signed internally; this one ends with twenty-four files whose approval sits
entirely outside the programme.**

**Third, four decisions outside the content function block the category, and one of them blocks the
repository.** The split-residency opinion (`D-13`), the marketplace principal-or-agent determination
(`D-03`) and the e-waste regulated-entity question each block a specific file. **The limitation period
blocks more than twenty `DT` retention rows**, because *"plus the limitation period"* appears
throughout Category 05 and **no document states the number.** Until it is stated, `M24` cannot compute
a disposal date for the contract, warranty, custody, complaint or dispute record classes. It is one
question to Legal Counsel with the widest effect of the four and the lowest cost.

**Fourth, the wave-sequencing defect is now five for five, and two of the five were authored after it
was diagnosed.** `AUDIT-010` §7 concluded that *"the remaining twelve categories will inherit the same
defect unless the sequencing basis is corrected once."* `AUDIT-012` found two inversions in `BN`; this
audit finds six in `LG`, including a **circular** dependency where `LG-018` at `W5` and `LG-024` at
`W3` each wait on the other. **The diagnosis was correct and the register has not been corrected.**

| Rule | Status |
|---|---|
| `CM-R1` register-first | ✅ All 24 registered before authoring; zero divergence both directions. **`AUDIT-013` registered before this report was written** (LG-13) |
| `CM-R7` statutory or legal file needs a named sign-off | ⚠ **Zero of 24 signed.** Correctly recorded as pending in all 24 approval records; **check E2 cannot pass until R-02 is actioned** |
| `CM-R9` audit on category completion | ✅ This report |
| `CP-11` counted, not estimated | ✅ Every figure enumerated 2026-08-18 |
| `RG-06` never read what a document says about itself | ✅ Every check by extraction; **LG-01, LG-05, LG-06, LG-08 and LG-12 were found only this way** |
| Proposed `RG-08` — a count must be produced by the command that counts it (`AUDIT-012` R-1) | ✅ **Held. Every count in §2 is a command output** |
| Gate **F3** SLA identity | 🔴 **FAILS — finding LG-01. Blocking on `MD-028`, `DT-031` and `LG-015`** |
| Gate **F6** data-protection consistency | ✅ **Seven axes, zero divergence** — and made mechanical rather than left to manual review |
| Gate **F7** category-completion reconciliation | ✅ **Seven dimensions, zero divergence**, against a derived allocation rather than an arithmetic match (LG-11) |
| Check **G1** — findings open across three consecutive audits | ⚠ **Three recommendations have now been made four or five times: R-05 sequencing (5th), R-14 accessibility reviewer (4th), R-15 template variant (4th)** |

> **Index note.** This report and `AUDIT-001` through `AUDIT-012` must be indexed in `RF-012` when
> Category 99 `RF` is authored. **`AUDIT-011` is register-allocated to Category 12 `DM` and is not yet
> written to disk.**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
