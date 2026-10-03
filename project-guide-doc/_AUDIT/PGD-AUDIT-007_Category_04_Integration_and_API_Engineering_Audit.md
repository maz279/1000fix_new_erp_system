---
id: PGD-AUDIT-007
title: Category 04 — Integration & API Engineering Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Enterprise Architecture (self-audit — see §1.3 on independence)
scope: >
  The eight Category 04 IN documents, their fourteen executable artefacts, the identifier spaces
  they allocate, their citations into the four source repositories and into Categories 00–03 and 07,
  the PGD-000 register rows they change, and the concurrent-authoring condition observed throughout
  the audit window.
mandate: Audit required on completion of a category (rule PG-M7)
extends: PGD-AUDIT-001 … PGD-AUDIT-006
enumeration_timestamp: 2026-08-18 21:55 (+06)
method: >
  Filesystem enumeration and identifier extraction only. No figure in this report is projected, and
  none is taken from what a document says about itself — including this category's own files. Every
  count carries the instant it was taken, because the repository was under concurrent modification
  throughout the window (finding PGD-A7-01).
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# `PGD-AUDIT-007` — Category 04 `IN` Audit
### 8 documents · 14 executable artefacts · **enumerated 2026-08-18 21:55 (+06)**

---

## 1. Method and result

### 1.1 What was run

Seven extractions over the eight documents, the artefact tree and the wider repository:

| # | Extraction | What was compared |
|---|---|---|
| **X1** | Every relative markdown link, resolved against the filesystem | `PG-M9` |
| **X2** | Every `FF-nn` **definition** across all authored guiding categories | Identifier collision |
| **X3** | Every `IN-A-nn` finding identifier | Contiguity and uniqueness |
| **X4** | Every `` `IN-00n` `` cross-reference | Resolution to an issued document |
| **X5** | Every concrete workspace path cited in backticks | Existence on disk |
| **X6** | Mandatory template sections, per `TPL_Guiding_Document.md` | Structural conformance |
| **X7** | Every headline count re-derived from the source repositories | **The counts were re-run, not re-read** |

Plus a syntactic validation of all fourteen artefacts.

### 1.2 Result

**Eleven findings — 0 critical, 4 high, 5 medium, 2 low. Five were remediated during the audit;
six are open, and five of the six are owned outside this category.**

| Severity | Count | Fixed in audit | Open |
|---|---:|---:|---:|
| Critical | 0 | — | 0 |
| **High** | **4** | 1 | **3** |
| Medium | 5 | 3 | 2 |
| Low | 2 | 1 | 1 |
| **Total** | **11** | **5** | **6** |

> **This table was itself wrong on first writing, and the correction is `PGD-A7-05` recurring inside
> the report that raises it.** It originally read *"0 critical, 3 high, 5 medium, 3 low · six fixed,
> five open"* — composed while drafting rather than derived from the findings. Extraction over the
> eleven `**Severity: … · Status: …**` lines returns **4 high, 5 medium, 2 low · five fixed, six
> open**. It summed to eleven either way, which is precisely why it survived a reading.
>
> **`AUDIT-016` `AP-18` recorded the same defect inside the audit that verifies the gate designed to
> catch it. This is its third occurrence, and the second inside an audit report.** The instruction
> `AP-18` issued — *"derive every expected value from its source in the same pass that derives the
> actual, and never from the audit's own earlier prose"* — was followed for every other figure in
> this report and not for this one. Recorded rather than silently corrected.

### 1.3 On independence — stated, not glossed

> **This is a self-audit, and it is class `I0` under `GV-010`.** The auditor is the function that
> authored the material. `GV-010` records that **29 of 29 audit reports in this programme sit at
> `I0`** — the third line of assurance is empty.
>
> **Five of the eleven findings below are against this category's own work** (`PGD-A7-02`,
> `PGD-A7-04`, `PGD-A7-05`, `PGD-A7-11`, and the §1.2 severity-table correction), and all five were
> found by extraction rather than by reading. That is the only claim to rigour a self-audit can honestly make: **the checks were
> mechanical, and they were run before the documents were declared complete, not after.**
>
> Three of the five would not have been found by prose review at all — the severity table summed
> correctly while being wrong in three of its four rows.

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | **8 of 8** `IN-001`…`IN-008` ✅ |
| **A2** Identifier contiguity | `IN-001`…`IN-008`, no gaps, no duplicates ✅ |
| **A3** File name matches `id` front matter | 8 of 8, and each matches the `PGD-000` row link byte for byte ✅ |
| **A4** Files on disk with no register row | Zero ✅ |
| **B1** Front matter completeness | **All 19 template keys present in all 8**; `IN-002` and `IN-003` carry a 20th (`artefacts:`), which the template permits ✅ |
| **B2** `verified_on` present where a statute, standard or vendor version is cited | 8 of 8, all `2026-08-18` ✅ (`PG-M4`) |
| **B3** `owner` is a **role**, never a personal name | 8 of 8 ✅ |
| **X1** Relative links | **67 links, 0 broken** ✅ |
| **X3** `IN-A-nn` contiguity | `IN-A-01`…`IN-A-25`, **no gaps, no duplicates** ✅ *(after `PGD-A7-04`)* |
| **X4** `IN-00n` cross-references | Every reference resolves to an issued document ✅ |
| **X6** Template sections | 8 of 8 carry Purpose, Scope, Audience, Basis and Inputs, Standards conformance, Decisions, Open Questions, Acceptance Criteria, Traceability, References, Revision History ✅ *(after `PGD-A7-05`)* |
| **Artefact validity** | **7 YAML files parse · 2 JSON Schemas parse · CSV has 69 rows** ✅ |
| **`operationId` uniqueness** | **35 operations across 4 contracts, 0 duplicates, 0 null** ✅ (`FF-47` self-check) |
| **Decision identifier form** | **62 decisions, all in `<DOCUMENT-ID>-D-nn` form.** Zero bare `D-nn` ✅ (`DL-06`) |

### 2.1 What the category contains, counted

| Measure | Count |
|---|---:|
| Documents | **8** |
| Total lines · bytes | **6,650 · 434,284** |
| Executable artefacts | **14** — 7 YAML, 2 JSON, 1 CSV, 4 README/markdown |
| Decisions recorded (`<ID>-D-nn`) | **62** |
| Open questions | **59**, of which **8 are marked W0-blocking** |
| Acceptance criteria | **90** |
| Fitness functions defined | **63**, `FF-38`…`FF-100` |
| Findings raised against other artefacts | **25** (`IN-A-01`…`IN-A-25`) |
| OpenAPI operations issued | **35 of 1,187 — 2.9%** |
| Event schemas issued | **2 of 988** |
| ICDs issued | **14 of 47**, all at `Draft` |

---

## 3. Findings

### `PGD-A7-01` — Two identifier collisions with concurrently-authored categories

**Severity: HIGH · Status: FIXED IN AUDIT (by yielding) · Owner: CTO**

**What was found.** Category 04 was authored between **14:33 and 21:46 (+06)** on 2026-08-18.
During that window, four other categories were authored by independent sessions. Two identifier
collisions resulted:

| Space | Collision | Detected by | Resolution |
|---|---|---|---|
| **`FF-nn`** | `AR-012` was **re-issued as v1.1** allocating **`FF-36` and `FF-37`** to Category 03. Category 04 had allocated the same two to `IN-001` | **Extraction X2** — not by reading | Category 04 **yielded** and renumbered its entire block to `FF-38`…`FF-100`, across 8 documents and 6 artefacts |
| **`PGD-AUDIT-nnn`** | Category 06 took **`PGD-AUDIT-006`** | Directory enumeration at 21:52 | This report renumbered to **`PGD-AUDIT-007`** |

**How it happened.** `AR-012` §1 declares itself the register of fitness functions and was at
`FF-01`…`FF-35` when Category 04 began. Category 04 read that range, allocated from `FF-36`, and
`AR-012` v1.1 allocated from `FF-36` at the same time. **Neither author was wrong; there is no
allocating authority for the `FF-` space**, exactly as there is none for `D-nnn` before `GV-003`
existed.

**Why it is High.** `AUDIT_Checklist_Recurring.md` defines High as *"materially misleading."* Two
different checks called `FF-36` — one a data-dictionary citation check, one an API-contract
reconciliation check — is the `H-03` (48 colliding `CD` identifiers), `H2-04` (22 colliding KPI
identifiers) and `AP-02` (`NFR-090`…`092` meaning two things each) defect class, in a space that
gates the build.

**This is the fourth and fifth identifier collision in this repository.** The fix has been
recommended in `PGD-AUDIT-001`, `PGD-AUDIT-002`, `PGD-AUDIT-003` and `AUDIT-016`, and has never
been executed: **write `RR-002` (Identifier Convention Standard) and ratify `RG-08`.**

**Interim rule proposed.** Until `RR-002` exists, **`AR-012` is the sole allocating authority for
`FF-nn`**, and a category needing new fitness functions requests a block from it, exactly as
`GV-003` allocates `D-nnn`. Recorded for the Design Authority.

---

### `PGD-A7-02` — This category's own findings were allocated with gaps

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Enterprise Architecture (auditor's own work)**

**What was found.** Extraction X3 found the `IN-A-` space allocated as `IN-A-01`…`IN-A-31` with
**six gaps — 04, 07, 08, 09, 10 and 18** — and only 25 findings actually raised. The gaps arose
because identifiers were allocated as documents were drafted and some drafted findings were merged
or dropped without the numbers being reclaimed.

**Why it matters more than the tidiness.** A gapped identifier space is indistinguishable from a
space with **missing** entries. A reader encountering `IN-A-11` next to `IN-A-13` cannot tell
whether `IN-A-12` was withdrawn, is confidential, or was lost — and the estate has a live example
of exactly that ambiguity in `R39`–`R50` being unregistered.

**Remediation applied.** Renumbered contiguously in first-use order to `IN-A-01`…`IN-A-25` across
seven documents, **before any downstream document cited them**, and re-verified by extraction.
Twenty-two of the twenty-five identifiers changed.

---

### `PGD-A7-03` — The register was stale at the moment it was regenerated, and remains so

**Severity: HIGH · Status: OPEN · Owner: Programme Content Lead with CTO**

**What was found.** `PGD-000`'s totals were regenerated at 21:52 (+06) by counting all 140 category
rows (`PG-M10`). At that instant, enumeration of `project-guide-doc/` returned **119 files**, and:

| Category | Documents on disk | Register row at 21:55 | Audit |
|---|---:|---|---|
| 03 Data & Information Architecture | 9 | ✅ updated | `PGD-AUDIT-005` |
| **04 Integration & API Engineering** | **8** | ✅ **updated by this change** | **This report** |
| **05 Security, Privacy & Compliance** | **11** | ✘ **still 0 ✅ / 2 ◐ / 1 ⬜ / 8 ⛔** | — |
| **06 Experience & Interface Design** | **8** | ✘ **still 0 ✅ / 3 ◐ / 2 ⬜ / 3 ⛔** | **`PGD-AUDIT-006` ISSUED** |
| 07 Build Engineering & Dev Standards | 9 | ✅ updated | — |

**Nineteen authored documents are not reflected in the totals**, so the published **62 ✅ is a
floor**, and ◐/⬜/⛔ are ceilings.

**The starkest form yet.** **Category 06 has a published audit report while its register rows still
read ⛔ — "missing, blocking."** A document cannot simultaneously be absent and audited.

**Why it is High.** `PGD-000` §0.3 defines a status as *"an assertion about the filesystem"*, and
`PG-M2` forbids changing one without re-enumeration. The register is the artefact a Steering
Committee paper quotes. **A figure that is a floor must say so**, which is why this change adds an
explicit floor banner rather than silently publishing 62.

**This is the fifth occurrence** — after `PGD-A1-03`, `AUDIT-016` `AP-17`, `PGD-AUDIT-002` §8 and
`PGD-A3-18`. `AUDIT-016` `AP-17`'s remediation instruction was: *"a completion figure is taken only
when no category is in flight, and it carries its UTC instant."* **Proposed as `RG-08` and still
unratified after five occurrences.**

**Remediation instruction.** Ratify `RG-08`. Until then, every totals regeneration carries a floor
banner naming the categories in flight — which this change does, and which `AUDIT-015` did
correctly before it.

---

### `PGD-A7-04` — `IN-004` departed from the template's §2 and the departure was undeclared

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Enterprise Architecture (auditor's own work)**

**What was found.** Extraction X6 found `IN-004` missing `## 2. Basis and Inputs` and
`### 2.1 Standards conformance`. Its §2 was `The ICD Standard`; the template's three mandatory
sub-parts — standards conformance, source material, audit findings closed — were **absent as a
block**, though their content was distributed through §1 and §25.

**Why prose review missed it.** `IN-004` reads as complete: it names its standards in front matter,
cites its sources in §25, and closes findings throughout. **The structural check is what caught it**,
and the same check passed all seven other documents.

**Remediation applied.** §2 renamed `Basis and Inputs, and the ICD Standard`, with §2.1–§2.3
carrying the template's three sub-parts and §2.4–§2.6 the standard, **and the merge declared in a
template note rather than left implicit**. Existing section numbers were preserved so no
cross-reference in `IN-006` or `IN-008` broke; the two sub-section references that did move were
corrected and re-verified.

---

### `PGD-A7-05` — A stated operation count was written before it was derived

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Enterprise Architecture (auditor's own work)**

**What was found.** `IN-002` §9 and §11.1 stated **32 operations** across the four issued contracts,
composed from a per-contract table written while drafting. Parsing the artefacts returns **35** —
`service-delivery` has 16 not 14, and `platform` has 8 not 7.

**Why it matters, and why it is recorded rather than quietly corrected.** This is **`AUDIT-016`
`AP-18`'s defect exactly**: *"a summary table written before the derivation it summarises, and never
reconciled against it."* `AP-18` occurred **inside the audit that verifies gate F7**; this occurred
inside the document that establishes contract-generation discipline. `PG-M10` exists for it.

**It did not cancel.** Unlike `AP-18`'s two compensating errors, both components were low, so the
total was visibly wrong the moment it was derived. That is luck, not method.

**Remediation applied.** All five occurrences corrected to 35 / 2.9% / 1,152 remaining, **derived by
parsing the files**, and the derivation instant recorded in the text. Re-verified.

---

### `PGD-A7-06` — Three ICDs describe an interface with no signature mechanism, and two counterparties are misidentified in `05-03`

**Severity: HIGH · Status: OPEN · Owner: CTO with CFO, Treasury and Head of Tax**

**What was found.** Authoring `IN-004` against published counterparty documentation, verified
2026-08-18, produced three positions that contradict `05-03` §2:

| # | `05-03` says | Verified position | Consequence |
|---|---|---|---|
| 1 | `INT-038` NBR e-VAT — pattern **"File / API"** | **No publicly documented machine API** for Mushak-9.1 submission through IVAS at `vat.gov.bd`. The return is filed **through the portal, monthly, by the 15th** | `INT-038` is a `P5` batch integration whose transmission is a human. **The effort moves from integration to report-generation accuracy** |
| 2 | `INT-005` counterparty — **"Bank BEFTN"** | **BEFTN participants are banks.** 1000FiX is not one and cannot be. The counterparty is **its sponsoring bank**, and the file is that bank's implementation of the fixed-width national format | **`CD-100 cd_beftn` cannot be specified until the bank is named.** Two banks will not accept the same file |
| 3 | `INT-024`…`026` couriers — webhook status | **Signature support is inconsistent across the three; some offer none** | Where none exists, the inbound surface is authenticated by URL obscurity and network position alone |

**Why it is High.** *"Work done against the wrong artefact"* — a connector built against an API that
does not exist, or a file format from the wrong counterparty, is wasted build. Both are `P0` and
both land in W4–W5.

**Remediation instruction.** Head of Tax and CTO to confirm whether **any** IVAS submission API
exists, public or issued to registered filers (`IN-001` Q-06). CFO and Treasury to **name the
sponsoring bank and obtain its specification** (`IN-001` Q-07). Integration Architect to confirm
each courier's signature mechanism before the W3 ICDs go to `Agreed` (`IN-006` Q-02).

---

### `PGD-A7-07` — The PDPA instrument and its penalty basis are cited from a superseded position

**Severity: HIGH · Status: OPEN · Owner: Legal Counsel with CFO**

**What was found.** The estate cites **"PDPA 2026"** throughout, with a penalty exposure of
**BDT 25–50 lakh** (audit `C-04`, `AUDIT-016` `AP-02`, `AP-08`, `GV-005` `RSK-032`, `GV-008`'s risk
budget). Verification at **2026-08-18** against published sources finds:

| Element | Cited | Verified |
|---|---|---|
| Instrument | "PDPA 2026" | **Personal Data Protection Ordinance 2025**, gazetted 6 November 2025, **as amended by the Personal Data Protection (Amendment) Ordinance, 2026 — Ordinance No. 23 of 2026**, promulgated 5 February 2026 |
| Enforcement date | ~13 May 2027 | **Consistent** — enforcement mechanisms deferred ~18 months to on or about 13 May 2027 |
| **Penalty basis** | **BDT 25 lakh / 50 lakh ceiling** | **Turnover-proportional** — published analyses describe 1–2% of annual turnover generally, and **2–5% for a significant data fiduciary** |
| Localisation | Broad residency requirement | **Narrowed by the Amendment** to restricted data and Critical Information Infrastructure, requiring at least one synchronised real-time in-country copy |

**Why it is High and not Critical.** The enforcement date, the significant-data-fiduciary concept
and the cross-border notification obligation — the elements the estate's controls are actually built
on — are **unchanged**. What changes is the **exposure quantum** and the **localisation scope**.

**Why the quantum matters.** `GV-008` sizes a risk budget against a fixed BDT ceiling. At 250,000+
customers per month, **a turnover-proportional penalty is a materially different number**, and it is
the number a Board paper quotes.

**Why the localisation scope matters.** `NFR-086`'s split-residency architecture, `AR-001`'s Z4 zone
and CD-233 are designed against the unamended text. **If localisation is narrower than assumed, some
of that design may be over-engineered — and some data classes may have moved out of scope.** Either
way it is a design input that has changed.

**Remediation instruction.** Legal Counsel to obtain the consolidated Ordinance text and confirm the
penalty basis and localisation scope. **This is a repository-wide citation correction spanning
`05-06` §6, `LG-*`, `AP-012`, `GV-005`, `GV-008` and four audits — it is not Category 04's to make**,
and it is referred to `SC-003`, `SC-007` and `SC-008`, which are now authored.

---

### `PGD-A7-08` — Two categories' worth of effort sits in one register row each

**Severity: MEDIUM · Status: OPEN · Owner: Programme Director**

**What was found.** `IN-002` and `IN-003` were sized using `GV-007`'s method:

| Document | Low | Expected | High | Carried in `PGD-000` as |
|---|---:|---:|---:|---|
| `IN-002` — 1,187 operations, 11 contracts, generator, 100 path reconciliations | 109 PW | 194 PW | 356 PW | **one row** |
| `IN-003` — 988 schemas, 242 renames, 69 dispositions, ≥25 new events, registry | 84 PW | 163 PW | 319 PW | **one row** |
| **Combined** | **193 PW** | **357 PW** | **675 PW** | **two rows** |

`GV-007` sized the entire guiding-document stream at **264–528 PW for 127 documents** — an average
of ~3 PW each. **These two are 30–110× that average.**

**And `IN-003` `RE-08` is not documentation at all.** At least **25 events** — 8 owed by M12, 6 by
M27, 6 by M40 — appear in **no module's `§12.3` table**. They are module functionality nobody has
specified or costed, surfaced only by measuring the portal side.

**Why it is Medium and not High.** It **extends** open findings `PGD-A1-05` and `PGD-A3-15` rather
than raising a new class, and `GV-007` already records the guiding-document stream as unbudgeted.
It becomes High if a wave plan is published that assumes these two rows are ordinary documents.

**Remediation instruction.** `GV-007` to carry `IN-002` and `IN-003` as **named line items**, and
`GV-004` to schedule `RE-08` as **build scope**, not documentation.

---

### `PGD-A7-09` — Every claim of closure in this category is conditional, and the conditions are outside it

**Severity: MEDIUM · Status: OPEN · Owner: Design Authority, CTO, Security Lead, CFO, Legal Counsel**

**What was found.** The category closes or contributes to eight `AUDIT-016` findings. **Not one
closes on issue of a document.**

| Finding | This category delivered | Closes when |
|---|---|---|
| `AP-04` (high) — no signature scheme | A complete scheme + the three missing endpoints | **CTO and Security Lead ratify** |
| `AP-05` (high) — no scope vocabulary | 58 named scopes, ratified form | **Design Authority ratifies** |
| `AP-06` (high) — three commitments | Two reconciled by ruling | **CFO decides on a second card acquirer** |
| `AP-01` (critical) — unregistered events | The measurement, the triage, the CSV worklist | **`RE-02`/`RE-03`/`RE-04` execute** — with `AR-009` |
| `AP-08` (high) — disclosure register | Blocked ICDs; a blocking certification gate | **Legal determines the courier rows** |
| `AP-12` (medium) — seventh environment | `SANDBOX` specified | **`TS-001` §4.7 amended** — a Category 13 change |
| `AP-14` (medium) — no API notice clause | The clause, drafted | **Legal inserts it into four agreements** |
| `AP-03` — sequencing | This category sequenced one wave ahead | n/a — avoided, not closed |

**Eight open questions are marked W0-blocking**, meaning work cannot correctly start without them.

**Why this is recorded as a finding rather than a status note.** The estate's recurring failure mode
is **a document being read as a closure**. `PGD-A2-06` records an audit reporting a closed gap as
open; this is the mirror risk. **Issuing eight documents has closed nothing on its own**, and a
Steering Committee paper that reads "Category 04 authored, `AP-04` and `AP-05` closed" would be
wrong.

**Remediation instruction.** `GV-009`'s wave-gate assessment to treat the eight W0 questions as
**Gate 1 blockers**, and `GV-005` to carry the five unratified decisions as issues with owners.

---

### `PGD-A7-10` — `05-03` §4.2 and §5.1 are now contradicted by four documents and corrected in none

**Severity: LOW · Status: OPEN · Owner: Enterprise Architecture**

**What was found.** Four rulings across two categories now contradict the live text of `05-03`:

| `05-03` | Ruled by | Correction owed |
|---|---|---|
| §4.2 *"Event Inventory (Principal Events)"* — 64 events | `AR-009` `D-A9-01` — **partial, 6.5%** | Heading correction (`RM-06`, `RE-11`) |
| §5.1 twelve API families as **path prefixes** | `IN-001-D-01` — **policy groupings, not paths** | Family table correction (`RI-02`) |
| §7 monitoring windows read as failover triggers | `IN-001-D-02` — **breaker state drives failover** | Heading → *"Integration Monitoring and Alerting"* |
| §3.3 `technician.location_updated` as a webhook | `IN-006-D-08` — **throttled WebSocket** | Row superseded |
| §2.1, §2.6 counterparties for `INT-005`, `INT-038` | `IN-004-D-02`, `IN-004-D-03` | Counterparty correction |

**None has been applied to `05-03` itself.** Every correction is recorded in the ruling document and
scheduled (`RI-02`, `RE-11`), but the source file still says the superseded thing.

**Why it is Low.** The rulings are recorded, dated, owned and scheduled, and `GV-011` `CM-25` already
provides that where two artefacts disagree on a counted figure the more recent enumeration governs.
**It becomes Medium the first time an engineer builds from `05-03` §5.1 without reading `IN-001`.**

**Remediation instruction.** Apply the five corrections to `05-03` in one change, at W1, rather than
five times separately.

---

### `PGD-A7-11` — Abbreviated workspace citations do not resolve mechanically

**Severity: LOW · Status: FIXED IN AUDIT · Owner: Enterprise Architecture**

**What was found.** Extraction X5 flagged **12 of 22** concrete workspace paths as non-existent —
citations of the form `` `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03` `` without
the filename stem.

**Adjudication: this is the estate's convention, not a Category 04 defect.** `AR-009` §15, `AR-001`
§16 and every `GV` document cite the same way, and the reader-facing form `` `05-03` §4.2 `` is
clearer than a 60-character filename. **All twelve are backticked citations, not markdown links** —
`PG-M9` governs links, and X1 found **67 links, 0 broken**.

**Recorded rather than silently dismissed**, because the same extraction on a future category will
flag it again, and the next auditor should not re-adjudicate it. **Proposed convention:** a
citation intended to resolve mechanically uses the `_*.md` glob form; a citation intended for a
human uses the short stem. Both are legitimate; mixing them without a rule is what costs time.

**Remediation applied.** The convention was **adopted rather than merely proposed**: all twelve
citations were converted to the `_*.md` glob form across eight documents, and re-extraction now
returns **23 concrete workspace paths checked, 0 missing.** A convention that is proposed and not
applied is the `RG-08` failure mode in miniature.

---

## 4. Findings summary

| ID | Finding | Severity | Owner | Status |
|---|---|:--:|---|:--:|
| `PGD-A7-01` | Two identifier collisions with concurrent categories — `FF-36`/`FF-37`, `PGD-AUDIT-006` | **High** | CTO | **Fixed** (by yielding) |
| `PGD-A7-03` | Register stale at regeneration; 19 authored documents unreflected; **Category 06 audited while its rows read ⛔** | **High** | Content Lead + CTO | Open |
| `PGD-A7-06` | `INT-038` has no machine API; `INT-005`'s counterparty is the sponsoring bank; courier signatures inconsistent | **High** | CTO, CFO, Treasury, Head of Tax | Open |
| `PGD-A7-07` | PDPA instrument name, **penalty basis** and localisation scope cited from a superseded position | **High** | Legal Counsel + CFO | Open |
| `PGD-A7-02` | `IN-A-` space allocated with six gaps | Medium | Enterprise Architecture | **Fixed** |
| `PGD-A7-04` | `IN-004` template §2 departure, undeclared | Medium | Enterprise Architecture | **Fixed** |
| `PGD-A7-05` | Operation count stated before derivation — the `AP-18` class | Medium | Enterprise Architecture | **Fixed** |
| `PGD-A7-08` | `IN-002` + `IN-003` are 193–675 PW in two register rows; `RE-08` is uncosted build scope | Medium | Programme Director | Open |
| `PGD-A7-09` | Every closure claim is conditional on a ratification outside the category | Medium | Design Authority et al. | Open |
| `PGD-A7-10` | `05-03` contradicted by five rulings, corrected in none | Low | Enterprise Architecture | Open |
| `PGD-A7-11` | Abbreviated workspace citations do not resolve mechanically | Low | Enterprise Architecture | **Fixed** |

> **Four findings are against this category's own work** — `PGD-A7-02`, `-04`, `-05`, `-11` — and all
> four were fixed during the audit, as was this report's own severity table (§1.2). The convention inherited from `00-07` and
> `AUDIT-016` requires them to be stated anyway: **the cause matters more than the fix.**

---

## 5. Remediation applied during the audit

| # | Change | Files | Finding |
|---|---|---|---|
| 1 | `FF-36`…`FF-98` renumbered to `FF-38`…`FF-100` | 8 documents, 6 artefacts | `PGD-A7-01` |
| 2 | `AR-012` range corrected from `FF-01`…`FF-35` to `FF-01`…`FF-37` in every citation | 4 documents | `PGD-A7-01` |
| 3 | This report renumbered `PGD-AUDIT-006` → `PGD-AUDIT-007` | This file, `PGD-000`, `_CATEGORY_OVERVIEW` | `PGD-A7-01` |
| 4 | `IN-A-` renumbered contiguously — 22 of 25 identifiers changed | 7 documents | `PGD-A7-02` |
| 5 | `IN-004` §2 restructured; two moved sub-section references corrected in `IN-006` and `IN-008` | 3 documents | `PGD-A7-04` |
| 6 | Operation count corrected 32 → **35**, and 1,143 → **1,152 remaining**, in 5 places | `IN-002`, artefact README | `PGD-A7-05` |
| 7 | `PGD-000` totals **regenerated by counting all 140 rows**, with an explicit floor banner | `PGD-000` | `PGD-A7-03` |
| 8 | Twelve abbreviated workspace citations converted to the resolvable `_*.md` glob form | 8 documents | `PGD-A7-11` |

**All seven re-verified by re-running the extraction that found them.**

---

## 6. What Category 04 measured that nothing else had

Recorded because it is the category's principal contribution, and because it changes the size of a
known problem rather than finding a new one.

| # | Measurement | Prior position | Measured |
|---|---|---|---|
| 1 | **Portal-consumed API paths declared by no module** | Never measured | **100 of 140 — 71.4%** |
| 2 | **Portal-consumed events published by no module** | `AP-01`: **21**, from a three-file sample | **69 of 102 — 67.6%** |
| 3 | Module API operations | Never counted | **1,187** across 978 paths |
| 4 | Module paths under a declared API family | Assumed complete | **38 of 978 — 3.9%** |
| 5 | Convention-B event namespaces | `AR-009`: *"~245 across ~40"* | **242 across 37** — exact |
| 6 | CON-03 contract coverage | Assumed complete | **10 of 22 endpoints · 3 of 11 webhooks** |
| 7 | Contested API paths | Never checked | **6**, two modules each |
| 8 | Non-markdown files in the estate | Never counted | **0** — before this category |

> **Finding 2 is the one that matters.** `AP-01` was correct and its scale was set by its sample.
> The consumer-side gap is **69**, it contains all three of `AP-01`'s safety-critical events, and
> **`payment.received` — consumed by four portals and the CON-03 contract — is published by nobody.**
> `AR-009` found the same shape on the producer side at 45× its sample. **Two independent
> measurements, both 45–3× larger than the sampled finding, is a pattern about method, not about
> events:** the estate's summary tables are written before the specifications that consume them, and
> nobody runs the join.
>
> `IN-008`'s `CT-07` — a consumer's build fails when **no provider satisfies its pact** — is the
> control that makes running the join automatic. It would have caught every one of the 169 at
> authoring time.

---

## 7. Status assessment against `PGD-000` §0.3

| Test | Requirement | Category 04 |
|---|---|:--:|
| (a) | A named file exists at a stated path | ✅ 8 of 8, verified by enumeration |
| (b) | Complete front matter per `RR-003` | ✅ 8 of 8, all 19 template keys |
| (c) | ≥90% of the governing standard's section set | ✅ 8 of 8 *(after `PGD-A7-04`)* |
| (d) | **A named owner and an approval record** | **Owner ✅ · approval record ✘** |

**Test (d) fails, as it does for all 62 ✅ documents in this estate.** No constituted body can create
an approval record until `GV-001` `CC-01` completes (`PGD-A1-09`). The ✅ is therefore **qualified**,
in the same terms as Categories 00–03 and 07.

**Category 04 carries a second qualification the others do not.** Three of its eight documents await
a **named technical ratification** that is not a governance formality:

| Document | Awaiting | Consequence if not given |
|---|---|---|
| `IN-002` | The `IN-005` §5 scope vocabulary | `FF-54` blocks publication of every contract and issue of every credential |
| `IN-005` | Design Authority ratification of §5 | As above |
| `IN-006` | CTO + Security Lead ratification of §4 | The CON-03 portal accepts unverified POSTs from W1 |

**These are not "pending approval" in the `PGD-A1-09` sense.** They are decisions with a technical
consequence that arrives in Wave 1.

---

## 8. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Ratify the `IN-005` §5 scope vocabulary and the `IN-006` §4 signature scheme.** Two of the three unmade W1 decisions now have complete proposals; neither needs more analysis | Design Authority · CTO · Security Lead | **W0** |
| **R-02** | **Write `RR-002` and ratify `RG-08`.** Five identifier collisions and five stale-register occurrences, recommended five times, never executed | CTO | **W0** |
| **R-03** | Make **`AR-012` the sole allocating authority for `FF-nn`** until `RR-002` exists | Design Authority | **W0** |
| **R-04** | Decide the **second card acquirer** question, or restate `NFR-048` | CTO + CFO | **W3** |
| **R-05** | **Name the BEFTN sponsoring bank** and obtain its file specification | CFO + Treasury | **W5 − 4 months** |
| **R-06** | Confirm whether **any IVAS submission API** exists | Head of Tax + CTO | **W4 − 3 months** |
| **R-07** | **Determine the three courier `AP-012` rows** and sign processor contracts | Legal Counsel | **W3 − 3 months** |
| **R-08** | **Obtain the consolidated PDPA Ordinance text** and correct the penalty basis estate-wide | Legal Counsel + CFO | **W2** |
| **R-09** | Carry `IN-002` and `IN-003` as **named line items** in `GV-007`, and `RE-08` as build scope in `GV-004` | Programme Director | **W1** |
| **R-10** | Apply the five `05-03` corrections in **one change** | Enterprise Architecture | **W1** |
| **R-11** | **Update the `PGD-000` rows for Categories 05 and 06.** Category 06 is audited and still reads ⛔ | Programme Content Lead | **Immediately** |
| **R-12** | Commission a **class `I1` or better** review of at least one authored category. Thirty of thirty audits now sit at `I0` | CTO with `GV-010` | W2 |

---

## 9. The concurrent-authoring condition, recorded

Per `AUDIT-016` `AP-17`'s convention, the window is recorded to the minute:

| Instant (+06) | Event |
|---|---|
| **14:33** | Category 04 authoring begins. `project-guide-doc/` holds **59 files**; Categories 00–02 authored |
| 14:40 | Source-repository extraction taken — **978 paths, 1,187 operations, 988 events, 0 non-markdown files** |
| 14:49 | `IN-001` issued |
| 15:09 | `IN-002` and 7 artefacts issued |
| 17:25 | Portal-consumption extraction taken — **102 events, 69 unpublished** |
| 17:20–17:21 | **Category 03 registered by another session; `AR-012` re-issued v1.1 taking `FF-36`/`FF-37`; `PGD-AUDIT-005` issued** |
| 21:24–21:46 | `IN-003`…`IN-008` issued |
| 21:47 | Enumeration: **116 files.** Categories 05, 06, 07 found authored and unregistered |
| **21:52** | **`PGD-AUDIT-006` found taken by Category 06.** Register regenerated: **62 ✅** |
| **21:55** | Enumeration: **119 files.** Category 05 now **11** documents, up from 10 at 21:47 |

**The estate moved twice during the final eight minutes of this audit.** Every figure in this report
carries the instant it was taken, and the register's totals carry a floor banner, because a figure
that is correct for four minutes is not a figure a Steering Committee paper can quote — which is
`AUDIT-016` `AP-17`'s conclusion, reached independently for the sixth time.

---

## 10. Audit conclusion

**Category 04 is complete as a set of eight documents and fourteen artefacts, and it is honest about
being 2.9% of the contract surface, 0.2% of the event surface and 30% of the ICD surface.**

Its principal contribution is not the documents. It is the **measurement** — that 71.4% of the API
paths and 67.6% of the events the portal layer consumes are declared by no producing module — and
the recognition that this is the same defect `AP-01` and `AR-009` found, at a scale neither could see
from its sample.

**Its principal risk is that issuing the documents is mistaken for closing the findings.** Eight
questions are W0-blocking, five decisions await named ratifications, and two of the three unmade
Wave 1 platform decisions now have complete proposals sitting with the CTO, the Security Lead and
the Design Authority. **None of that is engineering work. All of it is a decision somebody has to
take.**

**Delivery-confidence rating for this category: Amber**, independence class **`I0`** (`GV-010`).

---

*`PGD-AUDIT-007` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
