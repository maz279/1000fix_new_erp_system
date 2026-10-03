---
id: CG-012
title: Content Sourcing and Evidence Rules
project: 1000FiX ERP System v2.0
content_type: Standard
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead
reviewers: [Enterprise Architecture, Legal & Compliance, Finance, Quality Manager]
approver: Programme Content Lead
purpose: >
  Requires every factual, statutory, pricing or capability claim in content to name a primary
  source with a verification date. The module repository has already recorded findings where
  claims rested on press reporting rather than enacted law, and where a control depended on an
  unverified figure. Content produced at 452-file scale multiplies both failure modes.
traces_to: [00-07 H2-12, 00-07 H2-13, 02-02 RG-05, 02-02 RG-06, AUDIT-001 AF-05, CG-006 §4, CG-007 G2, CG-007 G6, CG-008 U-28]
priority: P1
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-07 findings H2-12 (unverified "17+ brands" figure) and H2-13 (statutory tax figures on press reporting)
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/02_Architecture/02-02 §1 rules RG-05 and RG-06
    verified: 2026-08-15
  - source: project_content/_AUDIT/AUDIT-001 finding AF-05 (benchmark study claimed complete; folder empty)
    verified: 2026-08-15
supersedes: none
review_due: 2027-02-15
---

# CG-012 — Content Sourcing and Evidence Rules

> **Three recorded failures, three different shapes, one cause.**
>
> | Finding | What happened |
> |---|---|
> | `00-07` H2-13 | Statutory tax figures rested partly on **press reporting** rather than the enacted Finance Act |
> | `00-07` H2-12 | The "17+ brands" figure **underpins an `M22` control** and was recorded as unverified |
> | `AUDIT-001` AF-05 | `README.md` claimed the benchmark study and gap analysis were **"Complete"**; `01_Research_and_Benchmarking/` contains zero files |
>
> None was a lie. Each was a statement made in good faith that nobody could subsequently
> retrieve the basis for. **This standard makes the basis retrievable by construction.**

---

## 1. The rule

> **Every factual, statutory, pricing or capability claim in content names a source and the date
> that source was verified.**

Stated as `CM-R8` in the Content Master Index and `U-28`–`U-31` in `CG-008`. This file defines
what counts as a source, how currency is maintained, and what happens when a claim cannot be
sourced.

---

## 2. What needs a source

| Claim type | Example | Source needed |
|---|---|---|
| **Statutory** | "Mushak 9.1 is filed by the 15th of the following month" | **Always — primary only** |
| **Regulatory** | "Sensitive personal data must be Bangladesh-resident" | **Always — primary only** |
| **Contractual** | "Service credits are capped at 10% of the monthly charge" | **Always** — the executed agreement |
| **Pricing** | "On-site call-out outside Dhaka metro carries a zone surcharge" | **Always** — the approved rate card |
| **Capability** | "The technician application operates offline for 24 hours" | **Always** — the specification or a test result |
| **Quantitative** | "51+ service centres", "17+ brand partners", "250,000+ customers a month" | **Always** — the system of record or an owner's confirmation |
| **Repository** | "67 of 67 module specifications are written" | **Always — by enumeration** (`RG-06`) |
| **Comparative** | "Bangladesh's only ISO 9001:2015 certified IT service provider" | **Always** — the certificate and the basis of the exclusivity claim |
| **Technical** | "Odoo 19.0 was released on 18 September 2025" | **Always** — the vendor's own announcement |
| **Procedural** | "The dispatcher assigns the job from the dispatch board" | Only where non-obvious or contested |
| **Definitional** | "A service order is the record of a customer's request for service" | No — `CG-004` is the source |
| **Instructional** | "Select **Create service order**" | No — the pinned release is the source (`CG-006` §3) |

**Test:** if a reader could reasonably ask *"how do we know that?"* and the answer is not in the
file, a source is required.

---

## 3. Source classes

| Class | Definition | Examples | Acceptable for |
|:--:|---|---|---|
| **P1** | **Primary** — the instrument, record or system that constitutes the fact | Enacted Act; regulator's published form; executed contract; ISO certificate; the ERP itself; a filesystem enumeration; a signed board minute | Everything |
| **P2** | **Authoritative secondary** — an official body's own explanation of a P1 source | Regulator guidance note; vendor release announcement; standards body's published summary | Everything except Class A statutory content |
| **P3** | **Corroborating** — competent third-party analysis | Professional adviser's written opinion; audit report; recognised industry benchmark | Context and comparison only. **Never** the sole basis of a statutory, pricing or capability claim |
| **P4** | **Reported** — journalism, blogs, vendor marketing, conference talks | Newspaper report of a budget announcement; a consultancy blog post | **Never a source.** May flag that verification is needed |

### 3.1 Rules

| # | Rule |
|---|---|
| **EV-01** | **Class A statutory content requires P1.** No exception, no waiver (`CG-007` G6, `WV-02`) |
| **EV-02** | **P4 is never a source.** It may trigger a check against a P1 source; it may not substitute for one. This is the H2-13 failure |
| **EV-03** | Where only P4 exists — for example, a change announced but not yet enacted — the content states the position as **provisional**, names the P4 trigger, and records the date the P1 source is expected |
| **EV-04** | A P3 opinion is cited **as an opinion**, with the adviser named. "Our tax adviser advises that…" is a source; "It is understood that…" is not |
| **EV-05** | Quantitative claims about the business cite the system of record where one exists. Where none exists, the claim cites the accountable owner **by name and date**, and the absence of a system of record is itself recorded as a risk |
| **EV-06** | Repository claims are produced by **enumeration at the time of writing** (`RG-06`, `CP-11`) and carry the enumeration date |
| **EV-07** | A source that cannot be produced on request is not a source. "It's in an email somewhere" fails |

---

## 4. How sources are recorded

### 4.1 In front matter

```yaml
sources:
  - source: "Value Added Tax and Supplementary Duty Act 2012, as amended — Mushak 6.3 prescribed form"
    class: P1
    verified: 2026-08-15
    verified_by: "Tax Manager"
    location: "M24 document reference DOC-TAX-0042"
  - source: "1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §5 NFR-016"
    class: P1
    verified: 2026-08-15
```

| Field | Required | Purpose |
|---|:--:|---|
| `source` | Yes | Enough detail that another person can retrieve the same document |
| `class` | Yes for Class A and B content; recommended otherwise | P1–P3 (P4 is never a source) |
| `verified` | **Yes, always** | The date someone actually looked at it |
| `verified_by` | Yes for Class A and B | Who looked |
| `location` | Where the source is not publicly retrievable | Where the copy is held — usually an `M24` reference |

### 4.2 In the body

Where a specific claim needs a specific source, cite it inline against the claim, not only in
the front matter:

> Mushak 9.1 is filed by the 15th of the following month through the NBR VAT Online portal
> (`05-06` NFR-100, verified 2026-08-15).

| # | Rule |
|---|---|
| **CI-01** | Statutory, pricing and capability claims carry an inline citation, not only a front-matter entry |
| **CI-02** | The inline citation names the source and the verification date |
| **CI-03** | A table of claims carries a source column rather than repeating citations in prose |
| **CI-04** | Where a whole section derives from one source, cite it once at the section head |

---

## 5. Verification dates and currency

**A source verified once is not verified forever.** The verification date is the whole point:
it lets a reader judge whether the claim is still safe to rely on.

| Claim type | Re-verification interval | Additional triggers |
|---|---|---|
| Statutory and regulatory | **Annual**, plus on every instrument change | Finance Act; regulator notice; new form |
| Contractual | Annual, plus on renewal or amendment | Dispute; counterparty change |
| Pricing | **Every rate-card version** | Any approved price change |
| Capability | Every release affecting the surface | Failed test; incident |
| Quantitative business figures | **Quarterly** | Network change; partnership change |
| Repository counts | **Every wave boundary** | Any bulk authoring |
| Comparative and market claims | Annual | Competitor change; certification lapse |
| Technical and vendor | On vendor release | Deprecation notice |

### 5.1 The no-trigger rule

> **If nothing has triggered a re-verification in 12 months, re-verify anyway.**

This is the same rule as `CG-006` §4.2 and it exists for the same reason: the most dangerous
staleness produces no signal. A statutory claim verified in 2026 and never touched again looks
identical in 2029 to one verified last week — unless the date is there and someone reads it.

### 5.2 Stale sources

| Condition | Consequence |
|---|---|
| A source is past its re-verification interval | The claim is flagged **non-current**. The content may still be published, but the claim may not be cited as evidence elsewhere |
| A Class A source is past its interval | The file returns to `Review` and re-runs G6 (`CG-007` §7) |
| A source cannot be re-verified because it no longer exists | The claim is removed or restated with a new source. It is not left standing on a dead reference |

---

## 6. Claims that cannot be sourced

This is the most important section, because the failure mode is silence.

| Step | Action |
|---|---|
| 1 | **Do not write the claim.** A claim with no source is not a weaker claim; it is a liability |
| 2 | Ask the accountable owner whether a source exists that the author has not found |
| 3 | If a source exists but cannot be obtained in time, mark the claim **provisional**, state what is missing and who owns obtaining it, and set a date |
| 4 | If no source exists, record it as a **gap**, not as a fact |
| 5 | Log the gap in `RF-011` Content Risk Register with an owner |
| 6 | Where the unsourced claim underpins a system control, raise it to the Content Lead — this is the H2-12 shape and it is more serious than a documentation defect |

### 6.1 The provisional marking

```markdown
> ⚠ **Provisional — unverified.** The figure of 17+ brand partnerships is used here because it
> appears in the company profile and business plan. It has not been verified against the
> underlying agreements. `M22` certification controls depend on it. Owner: Commercial.
> Verification due: before W4. (`00-07` H2-12, `MD-017`.)
```

| # | Rule |
|---|---|
| **PR-01** | A provisional claim is visibly marked in the body, not only in the front matter |
| **PR-02** | The marking states what is unverified, who owns verification, and by when |
| **PR-03** | Provisional claims **may not be used for contractual commitment** — this is `RG-05` applied to content |
| **PR-04** | A provisional claim in a Class A file blocks approval. There is no provisional route for statutory content |
| **PR-05** | Open provisional claims are reported to the PMO monthly and reviewed at every wave audit |

### 6.2 The `AF-05` shape — claiming something exists

`AUDIT-001` finding AF-05 is a distinct failure: not an unsourced fact, but a **claim that a
document exists when it does not**. `README.md` stated the benchmark study and gap analysis were
"Complete"; the folder held zero files.

| # | Rule |
|---|---|
| **EX-01** | A claim that an artefact exists is verified by **checking that it exists**, at the moment of writing |
| **EX-02** | Status claims about other documents carry the date they were checked |
| **EX-03** | Never link to a planned document as though it were written. Planned documents are named in plain text, not as hyperlinks — this is the convention `README.md` already adopted after finding H-06 |

---

## 7. Sources this programme relies on

The recurring sources. `RF-002` holds the full index with locations; this is the working list.

| Domain | Primary sources | Class | Held where |
|---|---|:--:|---|
| VAT, Mushak forms, filing | Value Added Tax and Supplementary Duty Act and rules; NBR prescribed forms; NBR VAT Online portal | P1 | `M24`, Finance |
| Income tax, payroll deductions | Income Tax Act; the applicable Finance Act | P1 | `M24`, Finance |
| Data protection and residency | The Bangladesh personal-data statute cited in `05-06` §6 and NFR-086 | P1 | `M24`, Legal |
| Employment | Labour Act and rules | P1 | `M24`, HR |
| Environmental and e-waste | The applicable rules cited in `M18` | P1 | `M24`, Sustainability |
| Quality management | ISO 9001:2015 standard; the company's certificate | P1 | `M24`, Quality |
| Information security | ISO/IEC 27001 where cited | P2 | `M24`, Security |
| Accessibility | W3C WCAG 2.1 | P1 | Public |
| Company facts — network, headcount, volumes | The ERP once live; before that, the company profile and business plan **with owner confirmation** | P1 / P3 | `M24` |
| Brand partnerships | The executed brand agreements | P1 | `M24`, Commercial |
| Pricing | The approved rate card version (`MD-029`) | P1 | `MD-029` |
| System capability | The module and portal specifications; test results | P1 | `1000fix_ERP_Module/` |
| Repository state | Filesystem enumeration | P1 | The repository |
| Odoo and open-source components | Vendor release announcements and documentation | P2 | Public |

> **Note on company facts.** Figures such as "51+ service centres", "500+ employees" and
> "250,000+ customers a month" currently rest on the company profile and business plan — P3
> under §3. Until the ERP is the system of record for them, each use requires **owner
> confirmation with a date**, and `MD-003`, `MD-012` and `MD-017` are the files that will
> convert them to P1.

---

## 8. Evidence retention

| Source class | Retained where | For how long |
|---|---|---|
| Statutory instruments | `M24`, with version and date | Life of the content plus the statutory retention period (VAT: at least five years) |
| Contracts | `M24` | Per `LG-009` |
| Certificates | `M24` | Life of the certificate plus one cycle |
| Owner confirmations | `RF-006` decision log or `M24` | Life of the claim |
| Filesystem enumerations | The audit file that produced them | Life of the audit trail |
| Adviser opinions | `M24`, with scope and date | Life of the content |
| Public standards | Reference only; version recorded, copy not retained | — |

**A source that cannot be produced on request is not a source** (`EV-07`). Retention is what
makes production possible.

---

## 9. Verification

| Check | Method | When |
|---|---|---|
| Every file has at least one entry in `sources:` | Automated | Every commit |
| Every source entry has a `verified:` date | Automated | Every commit |
| No `verified:` date is in the future | Automated | Every commit |
| Class A files have `class: P1` on every statutory source | Automated | Every commit |
| Statutory claims carry inline citations | Manual, gate G2 / G6 | Per file |
| Sources are within their re-verification interval | Automated report | Monthly |
| Provisional claims have an owner and a date | Automated | Every commit |
| Provisional claims are tracked in `RF-011` | Wave audit | Every wave |
| Claims that an artefact exists are true | Wave audit, by enumeration | Every wave |
| Sampled evidence trace — pick a claim, retrieve the source | Wave audit, 10% sample plus 100% of Class A | Every wave |

**Targets** (from `_AUDIT/AUDIT_Checklist_Recurring.md` §E3):

| Measure | Target |
|---|---|
| Evidence defect rate on Class A and B files | **Zero** |
| Evidence defect rate on other classes, sampled | Under 5% |
| Claims resting on P4 sources | **Zero** |
| Provisional claims in Class A files | **Zero** |
| Sources past their re-verification interval at a wave gate | **Zero** for Class A and B |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| [`CG-006_Content_Lifecycle_and_Versioning_Policy.md`](CG-006_Content_Lifecycle_and_Versioning_Policy.md) | §4 statutory pinning and the annual no-trigger review |
| [`CG-007_Review_Approval_and_Signoff_Workflow.md`](CG-007_Review_Approval_and_Signoff_Workflow.md) | G2 factual and G6 statutory gates test this standard |
| [`CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | U-28 to U-31; blocking item B-04 |
| [`CG-013_Content_Risk_and_Legal_Escalation_Rules.md`](CG-013_Content_Risk_and_Legal_Escalation_Rules.md) | What to do when a claim cannot be sourced and it matters |
| `RF-002` Source Document and Evidence Index | The full index of sources and their locations |
| `RF-008` External Standards and Regulatory Reference Register | Standards with versions and verification dates |
| `RF-011` Content Risk Register | Where unsourceable claims are recorded as risk |
| `LG-001` Legal Content Register | Class A and B evidence |
| `M24` Document, Records & E-Signature | The system holding retained evidence |
| `02-02` RG-05, RG-06 | The provisional-figure and count-do-not-consult rules this extends |

---

## 11. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Four source classes with P4 excluded as a source, recording format, re-verification intervals with a no-trigger annual rule, the procedure for unsourceable claims including provisional marking, the `AF-05` artefact-existence rule, the programme's recurring source list with the company-facts caveat | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Every rule traced to a recorded audit finding
- [x] Source classes defined with P4 explicitly excluded (the H2-13 failure)
- [x] Recording format specified concretely enough to automate
- [x] Re-verification intervals set, including the no-trigger annual rule
- [x] The procedure for unsourceable claims prevents silence
- [x] The `AF-05` "claimed to exist" failure addressed separately from unsourced facts
- [x] Company-facts sources honestly classified as P3 pending the ERP becoming the system of record
- [x] All internal links resolve
- [x] Bengali counterpart — n/a
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
