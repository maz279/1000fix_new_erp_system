---
id: RF-002
title: Source Document and Evidence Index
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead with Enterprise Architecture and Legal & Compliance
reviewers: [CTO, Legal & Compliance, Finance, Localisation Lead, QA Lead, Business Process Lead, Data Migration Lead]
approver: Programme Content Lead
content_class: E
purpose: >
  The register of every source the 452-file content set draws on — where it lives, who owns it,
  what class of evidence it is, and when its currency was last checked. `CG-012` requires every
  factual, statutory, pricing or capability claim to name a primary source with a verification
  date; `CM-R8` makes that a maintenance rule. Both are unenforceable without one place where a
  source is registered once and cited by identifier. Without this file, 1,642 source declarations
  across 430 files are 1,516 independent assertions that nobody can re-verify, and a repealed
  statute or a superseded specification propagates silently — which is exactly what `RSK-035`
  records having already happened twice in this programme.
traces_to: [99-04, CG-012, CM-R8, CG-006, CG-013, DoD-17, RSK-035, 00-07, RF-001, RF-006, RF-008, RF-012]
priority: P1
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-012_Content_Sourcing_and_Evidence_Rules.md — the evidence rules this file operationalises; source classes and the primary-source obligation
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md §DoD-17 — "Regulatory citations verified current, with a verified-on date", added following audit finding C-04
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md RSK-035 — "the specification cited a statute repealed twice, and a withdrawn NIST revision, because no currency-review control existed"
    verified: 2026-08-18
    class: P1
  - source: Extraction of every `sources:` block across project_content/ — 1,642 declarations, 1,516 distinct, across 430 files; run 2026-08-18
    verified: 2026-08-18
    class: P1
  - source: Filesystem enumeration of f:/sofrware_project_5/1000 fix/ — primary-doc/ (4 files), old-primary-doc/ (6 files), 1000fix_ERP_Module/ (123 files), 1000_fix_corporate_website/ content set, and the eight root-level programme documents; run 2026-08-18
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2026-11-18
---

# RF-002 — Source Document and Evidence Index

---

## 1. Purpose

`CG-012` states the rule: **every factual, statutory, pricing or capability claim names a primary
source with a verification date.** The content set complies at the level of the individual file —
1,642 `source:` declarations exist and every one of them carries a `verified:` date.

What does not exist is the other half of the control. A rule that each file names its own source
produces **1,516 distinct source strings**, written by many hands, with no shared identifier, no
owner, no currency date at the source level, and no way to answer the only question that matters
when a statute changes: *which files must now be re-opened?*

This file supplies that half. It registers each source once, gives it an identifier, names its
owner and its currency status, and makes the reverse lookup possible.

**The failure this prevents has already happened here twice.** `RSK-035` records that the
specification "cited a statute repealed twice, and a withdrawn NIST revision, because no
currency-review control existed". `00-07` finding **H2-13** records tax figures resting on press
reporting rather than enacted law. `DoD-17` was added to the module Definition of Done in
response. `RF-002` and `RF-008` are the content-side counterpart of `DoD-17`: this file says where
the source is, `RF-008` says whether it is still current.

**It also reports a defect found in writing it.** Sixty-eight files carry verification dates
**after the date of writing** — see §4.7. A verification date in the future is not a verification.

---

## 2. Scope

**In scope**

- Every document, dataset, statute, standard, specification or system the content set cites as
  evidence for a claim
- The classification of each into evidence classes `P1`–`P4`
- Ownership, location, version and currency status per source
- The reverse index: source → consuming content files
- The evidence rules for source types that cannot be filed (an interview, a system observation)

**Out of scope**

| Excluded | Owner |
|---|---|
| Whether an external standard or statute is **current** | `RF-008` — this file registers it, `RF-008` verifies it |
| The rule requiring a source at all | `CG-012` |
| The rule requiring a named legal sign-off | `CG-007`, `LG-001` |
| Retention of the evidence itself as a record | `M24`, `LG-009` |
| Content-to-requirement traceability | `RF-003` |

---

## 3. Audience

| Reader | Uses this file to |
|---|---|
| **An author** | Find whether a source is already registered before citing it a 1,517th way |
| **A reviewer at gate G2** | Check that a cited source is registered, classed and current |
| **The Compliance function** | Answer "the Finance Act changed — what re-opens?" in one lookup |
| **An external auditor** | See the evidence base of a statutory claim without asking the author |
| **The Programme Content Lead** | Detect a claim resting on a class `P3` source that should rest on `P1` |

---

## 4. Content

### 4.1 Evidence classes

Extended from `CG-012`. Class is a property of the **source**, not of the claim.

| Class | Definition | Admissible for | Count in use |
|:--:|---|---|---:|
| **P1** | Primary — the enacted instrument, the signed contract, the owning specification, the system of record, or a filesystem enumeration | Any claim, including statutory | **1,431** |
| **P2** | Authoritative secondary — a regulator's published guidance, a standards body's own summary, an OEM's technical bulletin | Operational claims; **statutory claims only with a P1 corroboration** | **117** |
| **P3** | Reputable commentary — professional-services analysis, established trade press, academic review | Context and orientation only. **Never the sole basis for a statutory, tax, pricing or capability claim** | **46** |
| **P4** | Uncorroborated — internal recollection, an undated web page, a vendor sales claim | **Not admissible.** Present only as an explicit gap marker | 0 declared |

> **Read the P3 count carefully.** Forty-six is small, and every one of them is disclosed. The
> risk is not the declared `P3`; it is the undeclared. `00-07` **H2-13** found tax figures whose
> author believed they were citing law and was citing press reporting. That is a `P3` presented as
> `P1`, and no count catches it. Only gate G6 external verification does — which is why
> `WV-02` makes G6 unwaivable for the six Class A statutory files.

---

### 4.2 Source families

Fifteen families. `SRC-` identifiers are permanent and never reused (`CP-02` applied to sources).

| ID | Family | Location | Owner | Class | Files citing it |
|---|---|---|---|:--:|---:|
| `SRC-01` | **ERP module specifications** — `M01`–`M67` | `1000fix_ERP_Module/03_Modules/` | CTO / Enterprise Architecture | P1 | 428 |
| `SRC-02` | **Portal specifications** — `P01`–`P12` | `1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/` *(misfiled — `AF-01`)* | CTO | P1 | 300+ |
| `SRC-03` | **Cross-cutting specifications** — `05-01`…`05-06` | `1000fix_ERP_Module/05_Cross_Cutting_Specifications/` | Enterprise Architecture | P1 | 400+ |
| `SRC-04` | **Architecture** — `02-01`, `02-02`, `02-05` | `1000fix_ERP_Module/02_Architecture/` | CTO | P1 | 180+ |
| `SRC-05` | **Governance and charter** — `00-01`…`00-07` | `1000fix_ERP_Module/00_Governance_and_Charter/` | Programme Director | P1 | 120+ |
| `SRC-06` | **Delivery** — `06-01`, `06-02` | `1000fix_ERP_Module/06_Delivery_and_Implementation/` | Programme Office | P1 | 200+ |
| `SRC-07` | **Primary business documents** — BRD, RFP, URD, Technology Stack Specification | `primary-doc/` | Programme Director | P1 | 60+ |
| `SRC-08` | **Superseded primary documents** — the March 2026 BRD/RFP/URD/Stack set and two strategy papers | `old-primary-doc/` | Programme Director | **P4** | 0 — *see §4.5* |
| `SRC-09` | **Company profile and corporate collateral** | `1000FiX_Services_Company_Profile.md`, `1000FiX-Company profile.pptx` | Marketing | P2 | 20+ |
| `SRC-10` | **Corporate website content set** — 427 registered files | `1000_fix_corporate_website/.../project_content/` | Digital Strategy | P1 *for website facts*, P3 *for ERP facts* | 25 |
| `SRC-11` | **The content set itself** — `CG`…`RF` | `project_content/` | Programme Content Lead | P1 | all |
| `SRC-12` | **Bangladesh statutes and statutory instruments** | External — see `RF-008` | Legal & Compliance | P1/P2 | 90+ |
| `SRC-13` | **International standards** — ISO, IEC, W3C, IETF, Unicode, OMG | External — see `RF-008` | Quality / Platform / Localisation | P1 | 120+ |
| `SRC-14` | **Vendor and platform documentation** — Odoo, bKash, Nagad, SSLCOMMERZ, Meta/WhatsApp, Google Play, Apple, Metabase | External | Platform Engineering | P2 | 45+ |
| `SRC-15` | **Executed commercial instruments** — brand authorisations, supplier contracts, BIN/TIN certificates | Held in `M24` | Legal & Commercial | P1 | 18 |

**Two families deserve a warning label.**

`SRC-10` — **the corporate website content set is P1 about itself and P3 about the ERP.** Twenty-five
ERP content files cite website files (`CB-001` brand guidelines, `BN-001`/`BN-002` Bengali
guidelines, `VP-002` RAMC, `B2B-020` AMC comparison). For brand colour values and Bengali
translation guidance that is a legitimate `P1` — the website set owns those. For product
definitions, pricing and terms it is `P3`, because Master Index §11 makes the **ERP side
authoritative** on all four defined interfaces. An ERP file that takes an AMC package definition
from `B2B-020` rather than from `MD-032` has taken it from the wrong side of the interface.

`SRC-08` — **`old-primary-doc/` is class `P4` and must never be cited.** It holds a complete
March 2026 BRD, RFP, URD and Technology Stack Specification, superseded by the August 2026 set in
`primary-doc/`. The two sets have **identical file names**. `1000FiX_ERP_System_Comprehensive_BRD.md`
exists in both, at 110 KB and 336 KB respectively. A `traces_to:` or `source:` line naming the
file without its directory is ambiguous, and resolves to the wrong document exactly half the time.
Extraction found **zero** current citations to `old-primary-doc/` — the risk is prospective, and
the mitigation is `EV-04` below.

---

### 4.3 Registered external sources

The authoritative register of external instruments, with currency status, is **`RF-008`**. This
section registers only *where the programme's copy lives and who holds it*, because that is the
question this file answers and `RF-008` does not.

| Source | Held by | Programme copy | Cited by |
|---|---|---|---|
| Value Added Tax and Supplementary Duty Act 2012; VAT and SD Rules 2016 | Finance / Tax | **None held** — cited from published text | `MD-037`, `DT-010`–`DT-015`, `LG-009`, `M51` |
| Income Tax Act 2023 and the applicable Finance Act | Finance / Tax | **None held** | `MD-043`, `DT-041`, `SP-021` |
| Personal Data Protection Act 2026 (Act 63 of 2026) | Legal | **None held** | `LG-008`–`LG-012`, `AP-012`, `HC-019`, `UI-042` |
| Bangladesh Labour Act 2006 with Labour Rules 2015 | HR | **None held** | `MD-042`, `MD-043`, `DT-041`, `DT-042`, `SP-021`–`SP-023` |
| Consumer Rights Protection Act 2009 | Legal | **None held** | `LG-013`, `LG-014`, `EO-013`, `SP-028` |
| Digital Commerce Operation Guidelines 2021 | Legal / Marketplace | **None held** | `LG-004`, `EO-001`, `EO-002`, `EO-013`, `DT-039` |
| Hazardous Waste (E-waste) Management Rules 2021 | Sustainability | **None held** | `MD-047`, `LG-018`, `DT-035`, `SP-026` |
| Cyber Security Ordinance 2025 | Security | **None held** | `LG-021`, `LG-020` |
| ISO 9001:2015 | Quality | **Held** — certification pack | 40+ files across `SP`, `DT`, `TR`, `LG`, `KB` |
| ISO/IEC 27001:2022 | Security | Not held | `LG-021` |
| W3C WCAG 2.1 | Content Design | Public | `CG-011`, `UI-010`, `TS-016`, `RP-007` |
| Unicode CLDR (`bn`) | Localisation | Public, versioned | `BN-006`, `BN-007` |
| RFC 9457, RFC 9745, Standard Webhooks, AsyncAPI 3.0 | Platform | Public | `AP-002`, `AP-004`, `AP-006`, `AP-011` |
| NIST SP 800-88 Rev.1 | Data Services | Public | `DT-034`, `SP-012`, `LG-017` |
| IEC 61340-5-1 / ANSI-ESD S20.20; IEC 61010-1; UN Manual of Tests and Criteria 38.3 | HSE / Technical | Not held | `KB-012`, `KB-013`, `MD-046` |
| OMG BPMN 2.0.2 | Business Process | Public | `SP-003` |

> **"None held" is the finding, not the formatting.** Nine statutory instruments on which
> forty-one Class A and B files depend exist in this programme only as citations. There is no
> controlled copy, no version stamp, no diff when the instrument changes. `RF-008` `ST-16`
> carries the remediation; `M24` is the system that should hold them.

---

### 4.4 Sources that are not documents

`CG-012` admits four evidence types that cannot be filed as a document. Each needs a stated
evidence form, or the claim resting on it is unverifiable.

| Type | Example in this content set | Required evidence form |
|---|---|---|
| **Filesystem enumeration** | Every count in `RF-001`, `RF-003`, `RF-004`, `RF-012` | The command or extraction, plus the **enumeration instant**. `RG-06` forbids projection; proposed `RG-08` requires the instant |
| **SME interview** | `SP-002` as-is process baseline; `KB-004`–`KB-007` repair guidance | Dated note naming the interviewee and their role, retained in `M24`. **Currently not produced** — `EV-05` |
| **System observation** | `DM-002` legacy source profiles; `RP-015` KPI baselines | Extract with a date, a row count and the query. **All 48 legacy sources are unprofiled** — `AUDIT-011` |
| **Absence of a document** | "`06-03_Data_Migration_Strategy.md` does not exist" | A dated directory listing. This is a legitimate `P1` claim and the strongest evidence type in the set, because it is trivially reproducible |

---

### 4.5 The reverse index — what re-opens when a source changes

This is the section the file exists for. When an instrument changes, these are the files that must
be re-opened. Counts are of **registered** files, enumerated 2026-08-18.

| Trigger event | Files re-opened | Gate that must be re-run |
|---|---:|---|
| **Finance Act / VAT rate or Mushak form change** | `MD-037`, `DT-010`–`DT-016`, `DT-019`, `DT-020`, `LG-009`, `RP-009`, `TS-009`, `SP-020` — **17** | G6 statutory, unwaivable (`WV-02`) |
| **Income tax slab or payroll statutory change** | `MD-043`, `DT-041`, `SP-021`, `TR-015`, `TS-010`, `DM-009` — **6** | G6 |
| **PDPA 2026 rules, guidance or NDMA determination** | `LG-008`–`LG-012`, `UI-042`, `NT-002`, `HC-019`, `AP-012`, `TS-017`, `MD-012`, `MD-013` — **12** | G5 + G6 |
| **Labour Act / Rules amendment** | `MD-042`, `MD-043`, `DT-041`, `DT-042`, `SP-021`–`SP-023`, `TR-015`, `LG-020` — **9** | G5 |
| **E-waste rules or EPR target change** | `MD-047`, `LG-018`, `DT-035`, `SP-026`, `EO-014` — **5** | G6 |
| **Digital Commerce Guidelines amendment** | `LG-004`, `EO-001`, `EO-002`, `EO-013`, `DT-039`, `SP-024` — **6** | G5 |
| **ISO 9001 revision** | `LG-022`, `DT-043`, `SP-029`, `SP-032`, `TR-016`, `MD-046`, `KB-012`, `KB-015`, and 30+ files citing a clause — **38** | G2 + G5. **This trigger fires in September 2026** — `RF-008` `ST-12` |
| **WCAG version change** | `CG-011`, `UI-010`, `TS-016`, `RP-007`, `MM-002` — **5** | G1 + G3 |
| **Module specification `Mnn` change** | See `RF-004` §4.3 per-module content lists | G2 + G3 |
| **Portal specification `Pnn` change** | See `RF-005` §4.3 per-portal content lists | G2 + G3 |
| **`05-05` business-rule change** | Any file citing the affected `BRU-` identifier — `RF-003` §4.5 | G2 |
| **Superseded document promoted to current** | Every file citing `SRC-08` — currently **zero**; keep it there | — |

---

### 4.6 Rules

| # | Rule |
|---|---|
| **EV-01** | A source is registered here **once**, with an `SRC-` identifier. A file cites the identifier and the specific section, not a re-description of the source |
| **EV-02** | Every source declaration carries a `class:` (`P1`–`P4`) and a `verified:` date. A declaration with no class defaults to **`P4` — inadmissible**, not to `P1` |
| **EV-03** | A statutory, tax, pricing or capability claim resting solely on a `P2` or `P3` source is **marked as unverified in the file itself** until G6 corroborates it. It is not quietly upgraded |
| **EV-04** | **`old-primary-doc/` is never cited.** Where a primary document is cited, the path includes `primary-doc/`. A bare file name is a defect because the two directories share file names |
| **EV-05** | An SME interview used as evidence produces a dated note naming the interviewee, retained in `M24`. "The workshop manager said" is not a source |
| **EV-06** | A `verified:` date is the date the source **was read**, not the date the file was written and **never a future date**. See §4.7 |
| **EV-07** | Where the website content set (`SRC-10`) and the ERP content set disagree on a fact within the four Master Index §11 interfaces, **the ERP side governs** and the website citation is removed, not reconciled |
| **EV-08** | A currency-review sweep runs at every wave boundary against `RF-008`. Sources whose currency has lapsed are flagged in the consuming files, not only in the register |

---

### 4.7 Finding `EV-F1` — sixty-eight files carry a verification date in the future

**What was found.** Extraction of all 1,642 `verified:` values on **2026-08-18**:

| `verified:` date | Declarations | Status |
|---|---:|---|
| 2026-08-12 | 15 | Past — valid |
| 2026-08-15 | 619 | Past — valid |
| 2026-08-16 | 80 | Past — valid |
| 2026-08-17 | 182 | Past — valid |
| 2026-08-18 | 415 | Today — valid |
| **2026-08-19** | **69** | **Future** |
| **2026-08-20** | **262** | **Future** |

**331 declarations across 68 files** carry a date that has not occurred. The affected categories
are complete and contiguous:

| Category | Files | Also affected |
|---|---:|---|
| 13 `TS` Test & Acceptance | 18 | `AUDIT-014` states enumeration date **2026-08-19** |
| 14 `RP` Reporting & KPI | 16 | |
| 16 `CM` Change & Communications | 18 | |
| 17 `OP` Operations & Runbooks | 16 | `AUDIT-017` and `README.md` state enumeration **2026-08-20** |

**Why it matters.** `CG-012` and `CM-R8` make the verification date the control. `DoD-17` makes it
a Definition of Done item. A future date defeats both: it cannot be a record of a source having
been read, and it silently extends the currency window — a citation "verified 2026-08-20" survives
an annual review two days longer than one verified today. More seriously, it makes the whole
`verified:` field unreliable as an audit artefact, because a reader who finds one impossible date
must treat all 1,642 as unaudited.

**How it happened.** Not carelessness. The Master Index itself records **"352 at 2026-08-19"** as a
superseded completeness figure and `README.md` records Category 17 as *"enumerated 2026-08-20"*.
The dates are internally consistent with each other and inconsistent only with the calendar. The
most probable cause is a working clock or a sequencing convention that advanced a nominal date per
authoring session rather than reading the system date. Seventeen prior audit reports did not catch
it because **no check in `AUDIT_Checklist_Recurring.md` compares a `verified:` date to the present
day.** Check `E4` compares verification dates to *the currency policy* — a window — and a future
date passes a window test.

**Remediation.**

1. Correct the 331 declarations in the 68 files to the date the source was actually read. Where
   that is unknown, set the date of the file's own `date:` front matter and mark the source
   `class:` unchanged but add `recheck: required`.
2. Correct the enumeration dates in `AUDIT-014` and `AUDIT-017`, and the two derived statements in
   `README.md` and Master Index §1 and §12.
3. **Add check `A7` to `AUDIT_Checklist_Recurring.md`:** *no `verified:`, `enumeration_date:` or
   `date:` value may be later than the audit's own run date.* Proposed as governance rule
   **`RG-09`** in `RF-012` §4.7.

**Status.** Open. Owner: Programme Content Lead. Carried to `RF-012` as finding `RF-01` and to
`RF-006` as decision `CD-02`.

---

### 4.8 Source coverage statistics

Enumerated **2026-08-18**. A floor, not a ceiling — Category 19 `MM` was in flight (`RF-001` §4.9).

| Metric | Value |
|---|---:|
| Files carrying a `sources:` block | **430** |
| Total source declarations | **1,642** |
| Distinct source strings | **1,516** |
| Declarations per file (mean) | 3.8 |
| Class `P1` | 1,431 (87%) |
| Class `P2` | 117 (7%) |
| Class `P3` | 46 (3%) |
| Declarations with **no** `class:` | 48 (3%) — default to `P4` under `EV-02`, must be classed |
| Distinct **external** sources (non-repository) | **229** |
| Declarations with a **future** `verified:` date | **331 in 68 files** — finding `EV-F1` |
| Statutory instruments with a **controlled programme copy** | **1 of 10** (ISO 9001:2015 only) |

**The 1,516 distinct strings are the argument for this file.** The same instrument is cited under
as many as eight different strings — the VAT and Supplementary Duty Act 2012 appears as *"Value
Added Tax and Supplementary Duty Act 2012"*, *"Bangladesh Value Added Tax and Supplementary Duty
Act 2012"*, *"The Value Added Tax and Supplementary Duty Act 2012 and its schedules"*, *"VAT and
Supplementary Duty Act 2012 and its rules"*, and four more. No search finds all of them. `EV-01`
exists to collapse that to one `SRC-` citation.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `CG-012` | The evidence rule this file operationalises |
| `CG-013` | Escalation triggers when a source is found inadequate |
| `RF-008` | Currency of every external source registered here |
| `M24` | The system that must hold controlled copies (`RF-008` `ST-16`) |
| `LG-009` | Retention of the evidence as a record |

| Depended on by | Why |
|---|---|
| Every content file at gate **G2** | G2 checks that the source is registered, classed and current |
| `RF-008` | Uses §4.5 as its impact map |
| `RF-012` | Receives finding `EV-F1` |
| `AUDIT_Checklist_Recurring.md` checks `E3`, `E4` and proposed `A7` | Answered from this file |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary**, and immediately on any `RF-008` currency change |
| Trigger for out-of-cycle review | A statute amended or repealed; a specification superseded; a new source family; a `P3` source found underpinning a statutory claim |
| Enumeration rule | §4.8 regenerated by extraction, never edited (`CP-11`) |
| Owner | Programme Content Lead |
| Escalation | A statutory claim found resting on `P3` alone goes to Legal & Compliance the same day (`CG-013`) |

---

## Approval Record

| Gate | Required for Class E | Reviewer | Status |
|---|:--:|---|---|
| G1 Editorial | ● | Content Design | Not started |
| G2 Factual | ● | Programme Content Lead with Legal & Compliance | Not started |
| G3–G6 | ○ | — | Not required |
| Final approver | — | Programme Content Lead | **Unappointed** |

---

## Open Items

| # | Item | Owner | Blocks |
|---|---|---|---|
| `RF-002-OI-01` | **`EV-F1` — 331 future-dated verifications in 68 files** | Programme Content Lead | The credibility of every `verified:` value in the set |
| `RF-002-OI-02` | **Check `A7` / rule `RG-09` not yet added** to `AUDIT_Checklist_Recurring.md` | Programme Content Lead | Recurrence |
| `RF-002-OI-03` | **48 declarations carry no `class:`** and default to `P4` under `EV-02` | Category owners | G2 on those files |
| `RF-002-OI-04` | **Nine statutory instruments have no controlled programme copy** | Legal & Compliance with `M24` | G6 evidence for 41 Class A/B files |
| `RF-002-OI-05` | **SME-interview evidence notes (`EV-05`) are not being produced** | Business Process Lead, Knowledge Manager | `SP-002`, `KB-004`–`KB-007` at G2 |
| `RF-002-OI-06` | **All 48 legacy sources unprofiled** (`AUDIT-011`) — system-observation evidence unavailable | Data Migration Lead | Every `DM` load |
| `RF-002-OI-07` | **No Programme Content Lead appointed** | CEO | Final approval |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; register table and maintenance procedure added per `CG-009` §3
- [x] Fifteen source families registered with owner, location and class
- [x] Evidence classes `P1`–`P4` defined and counted from extraction
- [x] Reverse index (§4.5) present — the file's primary function
- [x] Eight rules `EV-01`…`EV-08` stated
- [x] Finding `EV-F1` reported with cause, not silently corrected (`AUDIT_Checklist_Recurring` convention)
- [x] Statistics carry an enumeration instant (`CP-11`, `RG-06`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a (`bilingual: no`, `CG-010` §3.2)
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] **`EV-F1` remediated across 68 files** — outstanding, `RF-002-OI-01`
- [ ] **Named approver recorded** — outstanding, `RF-002-OI-07`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
