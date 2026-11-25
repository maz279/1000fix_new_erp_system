---
id: DT-030
title: Contract and AMC Agreement Template Set
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with Account Management
author: Legal & Compliance with Account Management and Content Design
reviewers: [Legal Counsel, Finance, Commercial, Service Operations, Localisation Lead]
approver: Legal Counsel with Chief Commercial Officer
content_class: B
purpose: >
  AMC, RAMC, MSP and enterprise agreement templates with their schedules and controlled variable
  clauses. Contracts are generated at volume by account managers; a template set with controlled
  variables is what prevents unreviewed bespoke terms entering the estate one deal at a time.
traces_to: [M08, M39, M05, P04, DT-001, DT-020, DT-031, DT-032, DT-037, LG-015, MD-015, MD-028, MD-032, MD-033, MD-040, BRU-CTR-01, BRU-CTR-02, BRU-CTR-03, BRU-CTR-05, BRU-CTR-06, BRU-CTR-07]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: DT-030_Contract_and_AMC_Agreement_Template_Set_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-CTR-01 — a contract cannot be activated without at least one covered asset or seat, defined entitlements, a billing frequency and approval
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-CTR-06 — RAMC package price is derived from the number and type of registered appliances, never a flat fee
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-CTR-07 — healthcare equipment contracts require calibration scheduling as a mandatory contract element
    verified: 2026-08-15
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-032 Contract and AMC Template Catalogue — the catalogue this document set implements
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-030 — Contract and AMC Agreement Template Set

> ⚠ **Class B — legal.** Every template in this set, and every permitted variable value, is
> approved by Legal Counsel. **An account manager may select from the approved set; they may not
> write a clause.**
>
> The failure this prevents is specific and common: a large deal closes on a Thursday, a clause is
> agreed on a call, and three years later the company is honouring an obligation nobody reviewed.
> §5.1 is the control that stops it.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Contract template set with schedules |
| Owning module | `M08` Contract Lifecycle Management |
| Statutory | No — **legally binding**; every clause is Legal's |
| Recipient(s) | Customer signatory, account manager, finance, service operations, legal file |
| Languages | **Bilingual — separate pages with a precedence clause** (`VB-004` BL-07) |
| Output formats | A4 portrait · PDF for e-signature (`M24`) · portal (`P04`) |
| Numbering mask | `MD-040` — `CTR-{entity}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; **contract term plus the limitation period** |

### 1.1 The set

| Template | Product | Typical customer | Key characteristic |
|---|---|---|---|
| **AMC** | Annual Maintenance Contract | Business and institutional | Asset-based entitlements, scheduled preventive visits |
| **RAMC** | Residential AMC | Consumer households | **Price derived from registered appliances (`BRU-CTR-06`)**, never a flat fee |
| **MSP** | Managed Service Provider agreement | Corporate IT estates (`M05`) | Seat- or device-based, remote support, SLA-led |
| **Enterprise** | Master service agreement | Large corporate, multi-site | Framework plus per-service schedules and delegated authority |
| **Healthcare equipment** | Specialist AMC | Hospitals, diagnostic centres | **Calibration scheduling mandatory (`BRU-CTR-07`)** |
| **Government / institutional** | Public-sector variant | Government bodies | Tender-linked terms, prescribed conditions where required |

### 1.2 The schedule structure

Every contract is a **framework plus schedules**. The framework is fixed; the schedules carry the
deal.

| Schedule | Contents | Governed by |
|---|---|---|
| **A — Covered assets or seats** | Asset list, sites, seat count | `BRU-CTR-01` — at least one required |
| **B — Entitlements** | What is included, how many, what is excluded | `BRU-CTR-04` |
| **C — Service levels** | Response and resolution commitments | **`DT-031`, and it must match `MD-028` exactly** |
| **D — Commercials** | Price, billing frequency, escalation, payment terms | `MD-029`, `MD-038` |
| **E — Contacts and authority** | Named contacts, approval delegation | `MD-015` |
| **F — Special conditions** | The **only** place bespoke terms may appear | §5.1 |

---

## 2. Statutory Requirements

Not statutory. Five legal constraints:

| Constraint | Source | Effect |
|---|---|---|
| Enforceability of each clause | Contract Act — **pending G6** | A clause that cannot be enforced is worse than absent |
| Consumer protection in RAMC | Consumer Rights Protection Act 2009 — **pending G6** | Consumer contracts carry protections that cannot be contracted away |
| Data protection where the contract covers data-bearing assets | `LG-008`, `05-06` NFR-086 | Processing terms are required where we handle customer data |
| Bilingual precedence | `CG-010` §4.1 — **pending Legal** | Which language governs in a dispute must be stated |
| Stamp duty | Stamp Act 1899 — **pending G6** | Applicability to service agreements and the current schedule |

### 2.1 G6 questions for Legal Counsel

| # | Question |
|---|---|
| **CT1** | Is our standard liability cap, exclusion set and indemnity enforceable as drafted? |
| **CT2** | Which consumer protections cannot be excluded in an RAMC? |
| **CT3** | Does stamp duty apply to these agreements, at what value, and who bears it? |
| **CT4** | Is an electronic signature sufficient for each contract type and value band? |
| **CT5** | What language precedence clause is appropriate, and is a Bengali version mandatory for consumer contracts? |
| **CT6** | What notice provisions are required for suspension and termination, and do they differ for consumers? |
| **CT7** | What processing terms are required where the contract covers data-bearing devices? |

---

## 3. Layout

| Zone | Content | Bilingual |
|---|---|---|
| Header | Contract reference, type, parties, effective and expiry dates | Title stacked |
| Party block | Both parties with legal name, registration, address and signatory | **Separate pages** per language |
| Body | Framework clauses, numbered and stable across the set | Separate pages |
| Totals | Not in the framework. Commercials are Schedule D | — |
| Statutory block | **Signature page** with precedence clause and stamp position | Both languages present |
| Signature | Both parties, with witness where required | — |
| Footer | Contract reference, `page n of m`, version of the template used | English |

| # | Rule |
|---|---|
| **L-30-a** | **Clause numbering is stable across the whole set.** Clause 12 means the same thing in an AMC and an MSP. Amendments, disputes and training all depend on it |
| **L-30-b** | Bengali and English are **complete separate versions**, each internally complete, with a precedence clause (`VB-004` BL-07) |
| **L-30-c** | The **template version used** prints in the footer. Years later, knowing which version a customer signed is the first question asked |
| **L-30-d** | Schedules are separately paginated and separately signed or initialled |
| **L-30-e** | Schedule F (special conditions) prints **even when empty**, stating "None". A missing schedule invites the claim that one existed |

---

## 4. Field Mapping

### 4.1 Framework variables

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Contract reference | চুক্তি সূত্র | `MD-040` sequence | Monospace | ✔ |
| Contract type | চুক্তির ধরন | `MD-032.template_code` | Label | ✔ |
| **Template version** | টেমপ্লেট সংস্করণ | `MD-032.version` | `v{n}.{n}` | ✔ |
| Customer legal name | গ্রাহকের আইনি নাম | `MD-015.account_legal_name` | Text | ✔ |
| Registration / BIN / TIN | নিবন্ধন / বিআইএন | `MD-015` | Monospace | ✔ where applicable |
| Registered address | নিবন্ধিত ঠিকানা | `MD-015` | Text | ✔ |
| Customer signatory | স্বাক্ষরকারী | `MD-015.authorised_signatory` | Name + designation | ✔ |
| Our entity and signatory | আমাদের প্রতিষ্ঠান | `MD-002`, `employee` | Text | ✔ |
| Effective date | কার্যকর তারিখ | `contract.effective_from` | `DD/MM/YYYY` | ✔ |
| Expiry date | মেয়াদ শেষ | `contract.expires_on` | `DD/MM/YYYY` | ✔ |
| Renewal basis | নবায়নের ভিত্তি | `contract.renewal_type` | Enum: auto / on notice / none | ✔ |
| Notice period | নোটিশের মেয়াদ | `contract.notice_days` | Days | ✔ |
| Governing law and jurisdiction | প্রযোজ্য আইন | Fixed | Text | ✔ |
| Language precedence | ভাষার প্রাধান্য | Per **G6 CT5** | Text | ✔ |

### 4.2 Schedules

| Schedule | Key fields | Source |
|---|---|---|
| **A** | Asset ID, serial, model, site, department, cover start | `M17`, `MD-015`, `MD-021` |
| **A (seats)** | Seat count, named users where applicable | `M05` |
| **B** | Entitlement type, quantity, period, carry-over, exclusions | `MD-032` |
| **C** | Priority, response, resolution, hours of cover, exclusions | **`MD-028` and `DT-031`** |
| **D** | Price, billing frequency, escalation %, payment terms, advance | `MD-029`, `MD-033`, `MD-038` |
| **E** | Named contacts, approval limits, escalation contacts | `MD-015` |
| **F** | Special conditions, each with its approval reference | §5.1 |

| # | Rule |
|---|---|
| **FM-30-a** | **Schedule C must match `MD-028` exactly.** A response time in a contract that differs from the SLA register is a liability the system cannot measure or honour. This is audit check **F3** |
| **FM-30-b** | RAMC pricing derives from the registered appliance list in Schedule A (`BRU-CTR-06`). A flat-fee RAMC cannot be issued |
| **FM-30-c** | A contract cannot be activated without at least one Schedule A entry, defined Schedule B entitlements, a Schedule D billing frequency and approval (`BRU-CTR-01`) |
| **FM-30-d** | Healthcare equipment contracts require calibration scheduling in Schedule B (`BRU-CTR-07`) |
| **FM-30-e** | Every Schedule F condition carries its **own approval reference**. A special condition with no approval cannot print |
| **FM-30-f** | Entitlement carry-over, expiry and over-consumption treatment are stated in Schedule B, because `BRU-CTR-04` requires over-consumption to be visible and that requires a defined baseline |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-CTR-01` | Activation preconditions — asset/seat, entitlements, billing frequency, approval |
| `BRU-CTR-02` | Out-of-scope service billed separately; the contract must define scope precisely enough to make "out of scope" determinable |
| `BRU-CTR-03` | On expiry, future scheduled work is cancelled and the customer notified — the contract states this |
| `BRU-CTR-04` | Over-consumption blocked or billed per configuration, never invisible |
| `BRU-CTR-05` | Suspension for non-payment follows the defined notice sequence (`DT-018`) |
| `BRU-CTR-06` | RAMC price from registered appliances |
| `BRU-CTR-07` | Healthcare calibration scheduling mandatory |
| `BRU-CTR-08` | Service credits calculated automatically; manual credits require CFO approval |
| `BRU-DMS-03` | A signed contract is not modified; a change is an amendment with a new signature |

### 5.1 Variable control — the mechanism

| Tier | What it is | Who may set it | Approval |
|:--:|---|---|---|
| **Fixed** | Framework clauses | Nobody. Changing them is a template revision | Legal Counsel, as a set |
| **Selectable** | Values from an approved list — cover hours, priority tiers, notice periods | Account manager | None; the list **is** the approval |
| **Bounded** | Numeric within an approved range — price, escalation %, payment days | Account manager within range; outside range escalates | Commercial approval outside range |
| **Special (Schedule F)** | Genuinely bespoke terms | **Nobody without Legal review** | **Legal Counsel per condition, referenced on the document** |

| # | Rule |
|---|---|
| **VC-01** | An account manager can produce a compliant contract without contacting Legal **for the overwhelming majority of deals**. That is the point — a control that blocks everything is a control that gets bypassed |
| **VC-02** | Schedule F is the pressure valve, and it is deliberately expensive: Legal review, a recorded approval, and a reference printed on the document |
| **VC-03** | Schedule F conditions are **reviewed quarterly**. A condition appearing repeatedly should become a selectable option or a template revision |
| **VC-04** | The template version is pinned at signature. A later template revision does not alter a signed contract (`CG-006`) |
| **VC-05** | Contracts signed on a superseded template remain valid and are tracked, so that a term change can be assessed against the population that actually holds it |

---

## 6. Variants

Beyond the six templates in §1.1:

| Variant | When used | Difference |
|---|---|---|
| **Amendment** | Change to a live contract | References the original; states only what changes; signed by both |
| **Renewal** | Term extension | New reference, references the prior contract, restates schedules |
| **Novation** | Customer entity changes | Three-party signature; Legal review mandatory |
| **Trial / pilot** | Time-boxed evaluation | Fixed end date, no auto-renewal, simplified entitlements |
| **Group framework** | Multi-entity customer | Framework with entity-level participation agreements (`MD-015` hierarchy) |
| **Tender-linked** | Public procurement | Prescribed conditions where the tender mandates them; those override our framework and Legal confirms each |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-030-S1` | Corporate AMC, 3 sites, 240 assets | Base framework plus schedules A–F |
| `DT-030-S2` | RAMC, 6 registered appliances | `BRU-CTR-06` derived pricing |
| `DT-030-S3` | Healthcare equipment AMC | `BRU-CTR-07` calibration schedule |
| `DT-030-S4` | Contract with two Schedule F conditions | `VC-02` approval references printed |
| `DT-030-S5` | Bengali and English separate versions | `L-30-b` precedence clause |
| `DT-030-S6` | Amendment to a live contract | Amendment variant |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Legal & Compliance with Account Management | 2026-08-15 | Draft issue |
| Reviewer — Finance | *pending* | | |
| Reviewer — Service Operations (Schedule C) | *pending* | | |
| Reviewer — Commercial | *pending* | | |
| **Legal Counsel — the set approved as a set** | *pending* | | **Required; per-template approval is not sufficient** |
| Approver — Legal Counsel with CCO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `CTR-{entity}-{yy}-{seq:06d}`; amendments suffix `/A{n}` |
| Gap policy | `gaps_recorded`; an unsigned draft consumes no number until issue |
| Archive format | **PDF/A-3 at execution**, with the e-signature evidence from `M24` |
| Retention | `LG-009`; **contract term plus the limitation period** |
| Re-render | **Prohibited.** The signed instrument is the instrument |
| Reprint | Watermarked **COPY**, logged |
| Template versioning | Every template version is retained while any contract on it remains live (`VC-05`) |
| Signature evidence | Signer identity, timestamp and document hash retained (`M24`, `SG-02`) |
| Stamp | Where **G6 CT3** requires stamp duty, the stamped original is the archived instrument |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-031_SLA_Schedule_and_Service_Credit_Annex.md`](DT-031_SLA_Schedule_and_Service_Credit_Annex.md) | **Schedule C; must match `MD-028` exactly** |
| [`DT-032_Warranty_Certificate_and_Extension_Document.md`](DT-032_Warranty_Certificate_and_Extension_Document.md) | Where cover is a purchased warranty rather than a contract |
| [`DT-037_Rental_Agreement_and_Asset_Handover_Record.md`](DT-037_Rental_Agreement_and_Asset_Handover_Record.md) | The rental counterpart |
| [`../05B_Finance_and_Statutory/DT-020_Consolidated_Corporate_Invoice.md`](../05B_Finance_and_Statutory/DT-020_Consolidated_Corporate_Invoice.md) | Billing under the contract |
| [`../05B_Finance_and_Statutory/DT-018_Dunning_and_Collection_Letter_Series.md`](../05B_Finance_and_Statutory/DT-018_Dunning_and_Collection_Letter_Series.md) | Suspension notice sequence |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | The SLA source of truth |
| [`../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-032_Contract_and_AMC_Template_Catalogue.md`](../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-032_Contract_and_AMC_Template_Catalogue.md) | The catalogue this implements |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md) | Sites, departments, signatories, delegation |
| `LG-015` AMC, SLA Master Terms and Service Credit Rules | The clause library this set draws on |
| [`SP-015_SOP_Contract_and_AMC_Lifecycle.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-015_SOP_Contract_and_AMC_Lifecycle.md) | How a contract is produced and activated |
| `TR-018` Course Pack — Account and Contract Manager | Where variable control is taught |
| [`NT-010_Email_Template_Library_Corporate_and_B2B.md`](../../04_Notification_and_Messaging/04C_Email/NT-010_Email_Template_Library_Corporate_and_B2B.md) | Renewal and expiry notices |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Six-template set, six-schedule framework, four-tier variable control with Schedule F as a deliberately expensive pressure valve, stable clause numbering, template-version pinning | Legal Counsel with CCO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Variable control defined as a four-tier mechanism, not a policy statement
- [x] Schedule C bound to `MD-028` with the audit check named (`FM-30-a`)
- [x] Stable clause numbering across the set (`L-30-a`)
- [x] Template versioning and pinning specified
- [x] All internal links resolve
- [ ] **Legal Counsel approval of the set** — **outstanding; blocks `Approved`**
- [ ] G6 CT1–CT7 answered, particularly CT3 stamp duty and CT5 language precedence — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Schedule C reconciled line-by-line with `MD-028` and `DT-031` (check **F3**) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
