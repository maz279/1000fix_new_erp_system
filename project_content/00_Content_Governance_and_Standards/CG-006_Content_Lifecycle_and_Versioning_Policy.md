---
id: CG-006
title: Content Lifecycle and Versioning Policy
project: 1000FiX ERP System v2.0
content_type: Policy
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead
reviewers: [Enterprise Architecture, Legal & Compliance, Platform Engineering, Localisation Lead]
approver: Programme Content Lead
purpose: >
  Defines the states a content file moves through, how versions are numbered, and how content is
  pinned to the software release or statutory year it belongs to. A UI copy pack not pinned to a
  release ships wording the build does not contain. A tax template not pinned to a Finance Act
  year becomes illegal silently — and nobody notices, because nothing changed.
traces_to: [CP-08, CP-10, CG-002, CG-007, CG-008, 06-01, LG-009, ISO 9001:2015 clause 7.5]
priority: P0
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: ISO 9001:2015 clause 7.5.2 (creating and updating) and 7.5.3 (control of documented information)
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 Implementation Roadmap — wave structure W1–W9
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 DM-06 soft delete
    verified: 2026-08-15
supersedes: none
review_due: 2027-02-15
---

# CG-006 — Content Lifecycle and Versioning Policy

> The company is ISO 9001:2015 certified, and that certification is its stated market
> differentiator. Clause 7.5 requires that documented information carry identification, format,
> review and approval, and that changes be controlled and versions managed. **This policy is how
> 452 content files satisfy clause 7.5 without a document-management ceremony that nobody
> follows.**

---

## 1. States

Every content file has exactly one status at any moment, declared in its front matter.

```
   ┌─────────┐   author     ┌────────┐   reviewers   ┌──────────┐   approver   ┌──────────┐
   │ Planned │─────────────►│ Draft  │──────────────►│  Review  │─────────────►│ Approved │
   └─────────┘              └────────┘               └──────────┘              └──────────┘
        │                        ▲                        │                          │
        │                        └────────────────────────┘                          │ publish
        │                             changes required                               ▼
        │                                                                     ┌──────────────┐
        │                                                                     │  Published   │
        │                                                                     └──────────────┘
        │                                                                            │
        │                                                                            │ replaced
        │                                                                            │ or retired
        ▼                                                                            ▼
   ┌───────────┐                                                              ┌──────────────┐
   │ Withdrawn │◄─────────────────────────────────────────────────────────────│  Superseded  │
   └───────────┘                        never written                         └──────────────┘
```

| Status | Meaning | May be used? | Who moves it here |
|---|---|:--:|---|
| **Planned** | Registered in the Content Master Index; no file yet | No | Programme Content Lead |
| **Reserved** | ID allocated to a bulk block or a vendor, authoring not started | No | Programme Content Lead |
| **Draft** | Being written. Incomplete, unreviewed, possibly wrong | No | Author |
| **Review** | Complete and submitted; in the review gates of `CG-007` | No | Author |
| **Approved** | Passed all gates and the `CG-008` Definition of Done. Correct, but not yet in the build | **Yes, as a specification** | Approver per content class |
| **Published** | Live in the build, the LMS, the print engine or the portal | **Yes, as the operative content** | Publisher |
| **Superseded** | Replaced by a newer version. Retained for traceability | No — reference only | Programme Content Lead |
| **Withdrawn** | Retired without replacement. The ID never returns | No | Programme Content Lead |

### 1.1 State rules

| # | Rule |
|---|---|
| **LC-01** | Status is declared in front matter and nowhere else. A file whose body claims a different status than its front matter is defective. |
| **LC-02** | Only the roles named above may change a status. An author cannot move their own file to `Approved` (`CO-04`). |
| **LC-03** | `Draft` and `Approved` cannot coexist with a `DRAFT_` file-name prefix in the wrong direction — see `CG-005` §4.2. |
| **LC-04** | A file may move backwards from `Review` to `Draft` freely. Moving backwards from `Approved` requires a new version, not a status change. |
| **LC-05** | `Approved` content that has not been published within one wave is re-reviewed for currency before publication. |
| **LC-06** | Only `Published` content may be cited as operative by another file, a training course, a test script or a legal position. |
| **LC-07** | `Superseded` content moves to `_ARCHIVE/` with a `SUPERSEDED_` prefix and a header note naming its replacement. It is never deleted (`CP-10`, `CM-R5`). |
| **LC-08** | For a bilingual file, **the pair moves together**. The English file cannot reach `Approved` while its Bengali counterpart is in `Draft` (`CM-R6`, `BN-018`). |

---

## 2. Version numbering

```
MAJOR . MINOR
```

Two parts only. A third part invites arguments about what a patch is.

| Part | Increment when | Effect |
|---|---|---|
| **MAJOR** | The meaning changes: a rule changes, a term changes, a statutory position changes, scope is added or removed, or the file is restructured | Re-review and re-approval required. Bengali counterpart re-translated. All citing files reviewed |
| **MINOR** | The meaning does not change: typo, formatting, a broken link, an added example, a clarified sentence | Approver informed, not re-consulted. Bengali counterpart updated where the wording changed |

| Version | Meaning |
|---|---|
| `0.1` … `0.n` | Pre-approval drafts. Any `0.x` file is `Draft` or `Review` |
| `1.0` | First approved issue |
| `1.1`, `1.2` | Non-substantive changes to the approved issue |
| `2.0` | Substantive change requiring re-approval |

### 2.1 What counts as MAJOR — the test

If a reader who acted correctly on the previous version could now act incorrectly, **it is
MAJOR**. Examples:

| Change | Version |
|---|---|
| A VAT rate changes in `MD-037` | MAJOR |
| An approval threshold changes from BDT 25,000 to BDT 30,000 in `SP-004` | MAJOR |
| An error message is reworded to state a different remedy in `UI-004` | MAJOR |
| A banned term is added to `CG-004` | MAJOR |
| A typo is corrected in a heading | MINOR |
| A screenshot is refreshed after a cosmetic UI change | MINOR |
| An example is added that illustrates the existing rule | MINOR |
| A dead link is repaired | MINOR |

**When in doubt, it is MAJOR.** The cost of an unnecessary re-approval is an hour. The cost of
a substantive change escaping review is whatever the content controls.

---

## 3. Pinning content to software releases

This is the failure the policy exists to prevent: **content and build drifting apart.**

A UI copy pack describes strings that exist in a specific build. If the pack is approved against
build 4 and the portal ships build 6, the help articles quote labels that are no longer on
screen, the training shows a flow that has changed, and the test scripts fail for the wrong
reason.

### 3.1 The pin

Content that describes the system carries a `pinned_to:` key in its front matter:

```yaml
pinned_to:
  surface: P01              # portal or application
  release: 2.4.0            # the release this content describes
  wave: W2
  verified_against_build: 2026-08-14
```

### 3.2 Which content must be pinned

| Category | Pinned? | Pin to |
|---|:--:|---|
| `UI` UI copy | **Yes** | Portal release |
| `HC` Help centre | **Yes** | Portal release |
| `TR` Training course packs | **Yes** | Portal release |
| `NT` Notification templates | **Yes** | Platform release (template engine) |
| `DT` Document templates | **Yes** | Print-engine release **and** statutory year (§4) |
| `TS` Test scripts | **Yes** | Release under test |
| `AP` API and developer content | **Yes** | API version |
| `OP` Runbooks | **Yes** | Platform release |
| `SP` SOPs | Partial | Pinned where the SOP names screens or system steps |
| `MD` Master data | No — but see §3.4 | Effective date, not release |
| `BN` Bengali bundles | Inherits the pin of the English source | — |
| `CG`, `VB`, `LG`, `RF`, `CM`, `DM`, `MM`, `KB`, `EO`, `RP` | No | — |

### 3.3 Pin rules

| # | Rule |
|---|---|
| **PN-01** | Pinned content is re-verified against the build before each release that changes its surface. Verification is a check, not a rewrite; most releases will pass unchanged |
| **PN-02** | A release that changes a user-visible string **cannot ship** until the affected `UI` pack is updated and the affected `HC`, `TR` and `TS` content is either updated or explicitly assessed as unaffected |
| **PN-03** | The assessment in PN-02 is recorded — "assessed, no change required" is a valid outcome that must be written down |
| **PN-04** | Content whose pin is more than one release behind is flagged **stale** and may not be cited as current |
| **PN-05** | The release notes (`OP-006`) list every content file changed by the release. This is how the two sets stay synchronised |

### 3.4 Master data — effective dating, not release pinning

Master data does not follow the build; it follows the business calendar. `MD` files therefore
carry **effective dates** rather than release pins:

```yaml
effective_from: 2026-07-01
effective_to: null            # null = current
supersedes_version: 1.3
```

Price lists, rate cards, tax codes, SLA definitions, warranty terms and payroll elements are all
effective-dated. **A transaction is evaluated against the version effective on its own date,
never against the current version.** This is a system requirement as much as a content one; it
is stated here because the content must be authored to support it.

---

## 4. Pinning statutory content to its instrument

The most dangerous version failure in this programme is the one where **nothing changes**.

A Mushak 6.3 template that was correct in the 2026 Finance Act year remains on disk, unchanged,
approved, published — and becomes non-compliant the moment the instrument changes. No edit
occurs, no review triggers, no test fails. The company continues issuing invoices that are no
longer valid.

### 4.1 The statutory pin

Class A content (`CG-002` §4) carries:

```yaml
statutory_pin:
  instrument: "Value Added Tax and Supplementary Duty Act 2012, as amended"
  provision: "Mushak 6.3 form, NBR prescribed format"
  fiscal_year: "2026-27"
  verified: 2026-08-15
  verified_by: "Tax Manager + external adviser"
  next_verification: 2027-06-01      # before the next Finance Act takes effect
```

### 4.2 Statutory review triggers

| Trigger | Action | Timebox |
|---|---|---|
| **Annual Finance Act** | Every Class A tax file is re-verified against the enacted Act, not against press reporting | Before the Act takes effect |
| A regulator issues a new or amended form | The affected `DT` file goes to `Review` immediately | 5 working days |
| A statutory rate, threshold or deadline changes | `MD-037`, `MD-043` and every citing document re-verified | 10 working days |
| A data-protection or residency obligation changes | `LG-008`, `LG-009`, `LG-012` re-verified | 10 working days |
| An ISO standard is revised | `LG-021`, `LG-022`, `DT-043`, `SP-029` re-verified | Before the next surveillance audit |
| **No trigger fires for 12 months** | The file is re-verified anyway. Silence is not evidence of currency | Annual |

> **The last row is the important one.** `AUDIT-001` finding `AF-04` and `00-07` finding H2-13 —
> statutory figures resting on press reporting rather than the enacted instrument — both arose
> because nothing forced a re-check. A calendar trigger with no external event is the only
> defence against silent staleness.

### 4.3 Retention

Superseded statutory content is retained for the longer of:

- the statutory retention period for the records it produced — **VAT records must be preserved
  for at least five years** — or
- the period set in `LG-009` Data Retention and Deletion Schedule.

A Mushak template retired in 2027 must remain retrievable while any invoice it produced is
within its retention window, because the template is the evidence of how that invoice was
constructed.

---

## 5. Review cycles

Every file carries a `review_due:` date. A file past its review date is **non-current** and may
not be cited as evidence (`CO-07`).

| Content class | Cycle | Additional triggers |
|---|---|---|
| **A** Statutory | Annual, plus every instrument change | §4.2 |
| **B** Legal / contractual | Annual, plus on any dispute, regulatory change or product change | Counterparty change |
| **C** Operational-critical | Per wave, plus on any process or system change | Incident, audit finding, KPI degradation |
| **D** User-facing | Per release affecting the surface | Support-volume spike, help-deflection drop (`CG-014`) |
| **E** Internal governance | Every two waves | Audit finding, governance change |

### 5.1 Ownership of currency

| Item | Who |
|---|---|
| Setting the review date | Author, at approval |
| Tracking review dates | Programme Content Lead, via `RF-010` |
| Performing the review | Content Steward for the category |
| Recording the outcome | Content Steward — including "reviewed, no change required" |

**"Reviewed, no change required" is a recorded outcome, not silence.** A file with no review
record is indistinguishable from a file nobody looked at.

---

## 6. Change control

### 6.1 Procedure

| Step | Action | Who |
|---|---|---|
| 1 | Raise the change: what, why, MAJOR or MINOR | Requester |
| 2 | Assess impact: which files, string keys, templates, courses and tests cite this content | Content Steward |
| 3 | For MAJOR: route to the review gates of `CG-007` for the content's class | Content Lead |
| 4 | For MINOR: approver is informed; no gate | Content Steward |
| 5 | Update the file, increment the version, update the revision history table | Author |
| 6 | Update the Bengali counterpart where wording changed | Localisation |
| 7 | Move the previous version to `_ARCHIVE/` if MAJOR | Content Lead |
| 8 | Publish, and list the change in the release notes (`OP-006`) | Publisher |
| 9 | Log the decision in `RF-006` | Content Lead |

### 6.2 The impact list

**A MAJOR change without an impact list is refused.** The list is produced by searching the
repository, not by recalling which files might be affected. This is the same discipline as rule
`RG-06` — count, do not consult.

```bash
# Files citing a content ID
grep -rl "CG-004" --include="*.md" .

# Files citing a specific term about to change
grep -rn "service order" --include="*.md" . | wc -l

# String keys affected by a UI copy change
grep -rn "p01.booking.confirm" --include="*.md" 03_UI_Copy_and_Microcopy/
```

### 6.3 Freeze windows

| Window | What is frozen | Why |
|---|---|---|
| Wave gate minus 4 weeks to go-live | MAJOR changes to any `P0` content for that wave | Training, translation and testing are already committed against the current version |
| Cutover freeze (`DM-014`) | All `MD` master data | Data loaded during cutover must match the specification it was validated against |
| Hypercare (`OP-002`) | MAJOR changes, except defect fixes | Users are learning; moving the content moves the target |
| Statutory filing period | Class A tax content, except to correct a defect | An in-flight filing must complete against one version |

A change inside a freeze window requires Content Lead approval and is logged as an exception in
`RF-006`.

---

## 7. Archiving

| Rule | Detail |
|---|---|
| **AR-01** | Superseded content moves to `_ARCHIVE/` with a `SUPERSEDED_` prefix |
| **AR-02** | The archived file gets a header note: what replaced it, when, why, and by whose decision |
| **AR-03** | The original file name and ID are preserved inside the archived name: `SUPERSEDED_MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register_v1.0.md` |
| **AR-04** | Archived content is never edited. If it was wrong, that is part of the record |
| **AR-05** | Content is **archived, never deleted** — mirroring `05-02` DM-06, which requires business records to be archived rather than hard-deleted |
| **AR-06** | Retention follows `LG-009`; statutory content follows §4.3 |

---

## 8. What this policy makes possible

| Question a reader will ask | How the policy answers it |
|---|---|
| "Is this content current?" | Status + version + review date + pin, all in front matter |
| "Which version was in force when this invoice was issued?" | Effective dating (§3.4) and archived versions (§7) |
| "Did anyone approve this?" | Approver in front matter; evidence in `LG-001` for Class A/B |
| "What changed and why?" | Revision history table in every file; decision in `RF-006` |
| "What else does this change affect?" | The impact list (§6.2) |
| "Is the Bengali version the same version?" | `LC-08` — the pair moves together |
| "Does this match what the system actually does?" | The pin (§3), verified per release |
| "Is this still legal?" | The statutory pin (§4), verified annually and on every instrument change |

These eight questions are, in substance, what an ISO 9001 surveillance auditor asks about
documented information. The policy is designed so that the answer to each is a field in the
file, not a search through email.

---

## 9. Related documents

| Document | Relationship |
|---|---|
| [`CG-002_Content_Operating_Model_and_RACI.md`](CG-002_Content_Operating_Model_and_RACI.md) | Who may move a status; content classes |
| [`CG-007_Review_Approval_and_Signoff_Workflow.md`](CG-007_Review_Approval_and_Signoff_Workflow.md) | The gates between `Review` and `Approved` |
| [`CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | What `Approved` requires |
| [`CG-005_Content_ID_and_Naming_Convention.md`](CG-005_Content_ID_and_Naming_Convention.md) | `SUPERSEDED_` and `DRAFT_` prefixes; retirement |
| [`CG-012_Content_Sourcing_and_Evidence_Rules.md`](CG-012_Content_Sourcing_and_Evidence_Rules.md) | Verification dates that drive §4.2 |
| `LG-001` Legal Content Register and Sign-off Log | Which version a user accepted, and when |
| `LG-009` Data Retention and Deletion Schedule | Archive retention periods |
| `OP-006` Release Notes Standard | Where content changes reach users |
| `RF-006` Content Decision Log | Every change decision |
| `06-01` Implementation Roadmap | The wave boundaries that drive freeze windows |

---

## 10. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Eight states, two-part versioning with a MAJOR test, release pinning, statutory pinning with an annual no-trigger review, effective dating for master data, change control with mandatory impact lists, four freeze windows | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] States, transitions and permitted actors defined
- [x] Version scheme defined with a decidable MAJOR/MINOR test
- [x] Release pinning specified per category
- [x] Statutory pinning includes an annual trigger that fires when nothing changes
- [x] Retention reconciles to `LG-009` and the five-year VAT record requirement
- [x] Change control requires a searched impact list, not a recalled one
- [x] All internal links resolve
- [x] Bengali counterpart — n/a
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
