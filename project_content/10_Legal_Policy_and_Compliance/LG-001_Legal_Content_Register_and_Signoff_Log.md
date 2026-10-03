---
id: LG-001
title: Legal Content Register and Sign-off Log
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance
author: Legal & Compliance with Programme Content Lead
reviewers: [Legal Counsel, Chief Data Officer, CFO, Quality Manager, CTO delegate, Programme Content Lead]
approver: Legal Counsel
content_class: B
purpose: >
  The register of every legally binding text the programme issues, and the log that proves which
  version of which text a named counterparty accepted, when, and by what mechanism. Without it the
  company holds twenty-four legal documents and no evidence of assent to any of them — and a term
  that cannot be proved accepted is a term that does not exist in a dispute.
traces_to: [CG-002, CG-006, CG-007, CG-008, CG-009, CG-010, CG-012, CG-013, M24, M60, FR-DMS-017, FR-DMS-025, FR-DMS-030, FR-DMS-033, FR-GRC-023, FR-GRC-029, BRU-DMS-03, BRU-DMS-09, BRU-DMS-10, BRU-GRC-14, LG-019, RF-006, RF-010]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md §2.1 gate matrix, §4.1 approval record schema, §4.2 evidence location, §4.3 rules SO-01…SO-07
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-002_Content_Operating_Model_and_RACI.md §4.1 — Category 10 carries 6 Class A and 18 Class B files; §5.1 and §5.2 RACI for those classes
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md §3.2 — Category 10 splits 16 bilingual and 8 English-only
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-009_Content_Template_Register.md §3 and §3.1 — template 10 Legal Document governs 23 LG files; LG-001 uses template 1
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M24_Document_Records_and_ESignature.md §5.2 FR-DMS-017 controlled-document workflow, §5.3 FR-DMS-030 completion certificate, FR-DMS-033 verification years later, §9 BRU-DMS-03/09/10
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60_Governance_Risk_and_Compliance.md §5.3 FR-GRC-029 policy library and FR-GRC-030 attestation; §9 BRU-GRC-14 retention defined in M60 and published to M24
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT_Checklist_Recurring.md checks E2, F6, F7 — named approver on every Category 10 file, no contradiction between LG-008/LG-009/LG-012, and blocking category-completion reconciliation
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# LG-001 — Legal Content Register and Sign-off Log

> **Read this before authoring or amending any other `LG` file.** It sets the class, the gates,
> the language, the approver and the acceptance-capture mechanism for all twenty-four.
>
> **It is also the answer to one question the company will eventually be asked in front of a
> third party:** *"Which version of your terms did this customer accept, and when?"* That question
> is not answered by a document. It is answered by a register with a row in it.

---

## 1. Purpose

Twenty-four legally binding or legally operative texts serve **eleven counterparty types** across
twelve portals. Each one has a version, an effective date, an approver, a jurisdiction and a
mechanism by which a counterparty is taken to have agreed to it.

**The document is not the asset. The evidence of assent is the asset.**

| Failure this file prevents | How it happens without a register |
|---|---|
| Terms in force that nobody approved | A draft is published because it was needed for a release |
| Terms accepted by a user, and no record of which version | Version 2.0 replaces 1.0 in place; the 250,000 users who accepted 1.0 leave no trace |
| Two files contradicting each other on data protection | `LG-008`, `LG-009` and `LG-012` drift because no one holds them together — audit check **F6** |
| A counterparty repudiating a term | The company can produce the document but not the acceptance |
| A statutory change re-opening the wrong set of files | No record of which file cites which instrument |
| A file reaching `Approved` on internal authority alone | Principle `CP-07`; rule `CM-R7` |

**Consequence of absence (`CP-03`).** Without this file, Category 10 is twenty-four unrelated
documents; `CG-007` §4.2 has nowhere to put Class A and B evidence; rule `SO-05` — *"`LG-001`
records which version each counterparty accepted and when"* — has no register to record it in;
and gate **F7** cannot be run on the category because its class, template and language splits
exist only as totals in three other files.

---

## 2. Scope

**In scope:** the register of all 24 `LG` files with class, gates, counterparty, jurisdiction,
language, wave and approver; the **derivation** of the content-class, template and bilingual
splits that gate F7 tests; the acceptance-capture taxonomy and what each mechanism proves; the
**version-acceptance ledger** record structure; effective-date, notice and re-acceptance rules;
the sign-off log; evidence retention; and rules `LR-01`…`LR-22`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The gates themselves, their service levels and waiver rules | [`../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md`](../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md) |
| Content classes and the RACI per class | [`../00_Content_Governance_and_Standards/CG-002_Content_Operating_Model_and_RACI.md`](../00_Content_Governance_and_Standards/CG-002_Content_Operating_Model_and_RACI.md) |
| Version numbering, statutory pinning, supersession | [`../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) |
| **The evidentiary basis of electronic acceptance** | [`LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md`](LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md) — stated once there, never per file (`SO-06`) |
| Retention periods for the evidence | [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) |
| The substance of any term | The `LG` file that owns it |
| Document storage, versioning, sealing, legal hold, disposal | `M24` — this file states the requirement; `M24` implements it |
| The obligation register and policy library | `M60` `FR-GRC-023`, `FR-GRC-029` |
| Content decisions taken while authoring | `RF-006` |
| Per-file owner and review date | `RF-010` |

> **`LG-001` is a register, not a repository.** It records *that* a version was approved and
> accepted, and where the evidence is. The evidence itself lives in `M24`.

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Legal Counsel** | Know which files are open, which are approved, and what is in force today |
| **Chief Data Officer** | Confirm `LG-008`, `LG-009`, `LG-012` and `LG-010` do not contradict (check **F6**) |
| **Programme Content Lead** | Run gate **F7** on Category 10 without re-deriving three splits |
| **Platform Engineering** | Build the version-acceptance ledger to §4.5, not to an invented shape |
| **Contact centre and branch staff** | Establish which terms applied to a specific transaction, during a dispute |
| **External counsel and auditors** | Trace a term from the register to its approval evidence |
| **Localisation Lead** | Plan 16 bilingual legal files with the English-governs rule settled |

---

## 4. Content

### 4.1 The register

Twenty-four files. `Pri` and `Wave` are copied from Master Index §4 and must not diverge (gate
**F7**). `Cls` is the content class from `CG-002` §4.1, derived in §4.2. `Lang` is from `CG-010`
§3.2, derived in §4.3. `Gates` are from `CG-007` §2.1 applied to the class.

| ID | Document | Counterparty | Cls | Gates | Lang | Pri | Wave | Approver | Acceptance capture |
|---|---|---|:--:|---|:--:|:--:|:--:|---|---|
| **LG-001** | Legal Content Register and Sign-off Log | — internal | B | G1 G2 G5 | EN | P0 | W1 | Legal Counsel | n/a — this is the record |
| **LG-002** | Portal Terms of Use — Customer | Individual customer (`P01`) | B | G1 G2 G4 G5 | **BN+EN** | P0 | W2 | Legal Counsel | **Click-wrap at registration** + re-acceptance on MAJOR change |
| **LG-003** | Portal Terms of Use — Corporate | Corporate portal user (`P04`) | B | G1 G2 G5 | EN | P1 | W4 | Legal Counsel | Click-wrap at first login, under the master contract |
| **LG-004** | Marketplace Seller Agreement and Policy Handbook | Marketplace seller (`P07`) | B | G1 G2 G5 | EN | P1 | W7 | Legal Counsel with CCO | **E-signature** — `BRU-MKP-01` gate |
| **LG-005** | Brand Partner Portal Terms | Brand partner (`P08`) | B | G1 G2 G5 | EN | P2 | W4 | Legal Counsel | E-signature or executed annex to the brand agreement |
| **LG-006** | Vendor Portal Terms and Supplier Code of Conduct | Supplier, courier, recycler (`P05`) | B | G1 G2 G5 | EN | P2 | W3 | Legal Counsel with Procurement Manager | E-signature at qualification — `BRU-SRM2-03` |
| **LG-007** | Referral and Alliance Partner Agreement | Referral / alliance partner (`P12`) | B | G1 G2 G5 | EN | P2 | W7 | Legal Counsel with CCO | E-signature at onboarding — `BRU-PCM-01` |
| **LG-008** | Privacy Notice and Consent Copy | Every data subject | **A** | G1 G2 **G4 G5 G6** | **BN+EN** | P0 | W2 | **Legal Counsel with CDO** | **Notice, not agreement** — presented; consent captured separately per purpose |
| **LG-009** | Data Retention and Deletion Schedule | — internal, regulator-facing | **A** | G1 G2 G4 G5 **G6** | **BN+EN** | P0 | W2 | **CFO with Legal Counsel** | n/a — published schedule (`BRU-GRC-14`) |
| **LG-010** | Data Subject Request Handling Content | Data subject | B | G1 G2 G4 G5 | **BN+EN** | P1 | W2 | Legal Counsel with CDO | n/a — response templates |
| **LG-011** | Cookie and Tracking Policy | Web visitor | B | G1 G2 G4 G5 | **BN+EN** | P2 | W2 | Legal Counsel with CDO | **Consent banner per category** |
| **LG-012** | Cross-Border Data Transfer and Residency Statement | Regulator, corporate client, brand partner | **A** | G1 G2 G4 G5 **G6** | **BN+EN** | P0 | W2 | **Legal Counsel with CTO** | n/a — published statement |
| **LG-013** | Service Terms, Warranty Terms and Exclusions | Every service customer | B | G1 G2 G4 G5 | **BN+EN** | P0 | W1 | Legal Counsel | **Signature at intake on `DT-002`**; reproduced on `DT-032` |
| **LG-014** | Refund, Cancellation and Compensation Policy | Customer | B | G1 G2 G4 G5 | **BN+EN** | P1 | W2 | Legal Counsel with CFO | Published policy; incorporated by reference into `LG-002` |
| **LG-015** | AMC / SLA Master Terms and Service Credit Rules | Contract customer | B | G1 G2 **G3** G4 G5 | **BN+EN** | P0 | W2 | **Legal Counsel with COO** | Executed contract — `DT-030` with `DT-031` as Schedule C |
| **LG-016** | Managed Services and Remote Access Consent Terms | Corporate client (`M05`) | B | G1 G2 G4 G5 | **BN+EN** | P1 | W4 | Legal Counsel with Corporate Services Head | **Per-session consent, logged** — `BRU-RMS-01`; standing consent by contract only |
| **LG-017** | Data Recovery and Secure Destruction Terms | Data-services customer (`M06`) | B | G1 G2 G4 G5 | **BN+EN** | P1 | W2 | Legal Counsel with Technical Services Head | Signature at case opening; destruction evidenced on `DT-034` |
| **LG-018** | E-Waste, EPR and Environmental Compliance Statements | Regulator, customer, corporate client | **A** | G1 G2 G4 G5 **G6** | **BN+EN** | P2 | W5 | **Legal Counsel with Quality Manager** | n/a — declarations and published claims |
| **LG-019** | E-Signature Legal Notice and Evidence Statement | Every signing counterparty | **A** | G1 G2 **G3** G4 G5 **G6** | **BN+EN** | P1 | W2 | **Legal Counsel with CTO** | n/a — it is the basis for all the others |
| **LG-020** | Acceptable Use and Internal Access Policy | Employee, contractor | B | G1 G2 G4 G5 | **BN+EN** | P1 | W1 | Legal Counsel with CTO | **Attestation at induction and annually** — `FR-GRC-030` |
| **LG-021** | ISMS Policy Set | Employee, auditor, enterprise client | B | G1 G2 G5 | EN | P1 | W2 | CTO with Legal Counsel | Attestation by named population |
| **LG-022** | Quality Policy and ISO 9001 Statement Set | Employee, certification body, client | B | G1 G2 G4 G5 | **BN+EN** | P1 | W1 | **CEO** with Quality Manager | Communicated and understood — ISO 9001:2015 clause 5.2.2 |
| **LG-023** | Anti-Bribery, Ethics and Whistleblowing Content | Employee, supplier, partner | B | G1 G2 G4 G5 | **BN+EN** | P2 | W3 | Legal Counsel with CEO | Attestation; supplier acceptance via `LG-006` |
| **LG-024** | Regulatory Disclosure and Statutory Notice Register | Regulators | **A** | G1 G2 G5 **G6** | EN | P2 | W3 | **CFO with Legal Counsel** | n/a — obligation register (`FR-GRC-023`) |

**Derived totals — regenerated from the rows above, not carried forward (`CP-11`, `CM-R2`):**

| Dimension | Expected by | Expected | This register | Result |
|---|---|---|---|:--:|
| File count | Master Index §4 | 24 | 24 | ✅ |
| Contiguity | `CP-02` | `LG-001`…`LG-024`, no gaps | No gaps | ✅ |
| Content class A / B | `CG-002` §4.1 | 6 / 18 | 6 / 18 | ✅ |
| Bilingual / English-only | `CG-010` §3.2 | 16 / 8 | 16 / 8 | ✅ |
| Template 10 / template 1 | `CG-009` §3, §3.1 | 23 / 1 | 23 / 1 | ✅ |
| Priority P0 / P1 / P2 / P3 | Master Index §1 | 7 / 10 / 7 / 0 | 7 / 10 / 7 / 0 | ✅ |
| Subfolder allocation | Master Index §3.2 | Flat — no `LG` subfolders | 24 flat | ✅ |

> **P0 (7):** `LG-001`, `LG-002`, `LG-008`, `LG-009`, `LG-012`, `LG-013`, `LG-015`.
> **P1 (10):** `LG-003`, `LG-004`, `LG-010`, `LG-016`, `LG-017`, `LG-019`, `LG-020`, `LG-021`,
> `LG-022`, `LG-014`. **P2 (7):** `LG-005`, `LG-006`, `LG-007`, `LG-011`, `LG-018`, `LG-023`,
> `LG-024`.

### 4.2 Content-class derivation — why these six are Class A

`CG-002` §4.1 states the totals and does not name the files. **`LR-01`: the allocation below is
the allocation. It is not re-derived per file.**

Class **A** under `CG-002` §5.1 means the content is *dictated by an enacted instrument or a
regulator's published form*, requires **G6 external verification**, and is approved by the CFO or
Legal Counsel. Class **B** means the content is *contractual* — the company chooses the wording,
and Legal Counsel confirms it is enforceable.

| File | Class | The deciding test |
|---|:--:|---|
| `LG-008` Privacy Notice | **A** | The mandatory notice content is set by statute (`05-06` NFR-092 restates it: categories, purposes, risks, retention, transfers, withdrawal procedure). The company does not choose what a transparency notice must contain |
| `LG-009` Retention Schedule | **A** | Each period is a statutory minimum or a statutory maximum. VAT record retention and the personal-data storage-limitation principle are both instrument-set |
| `LG-012` Residency Statement | **A** | The restriction on transferring sensitive personal identifiers is statutory (`05-06` NFR-099); the statement demonstrates conformance to it |
| `LG-018` E-Waste and EPR | **A** | Producer-responsibility duties, collection targets and disposal declarations are set by the e-waste rules made under the Environment Conservation Act 1995 |
| `LG-019` E-Signature Evidence | **A** | Validity of an electronic signature and admissibility of a digital record are statutory questions (ICT Act 2006; Evidence Act 1872 as amended 2022). The company cannot make its signatures valid by asserting that they are |
| `LG-024` Regulatory Disclosure Register | **A** | Every row is an obligation created by an instrument; the register's correctness is measured against those instruments |
| The other 18 | **B** | The company authors the term and Legal Counsel confirms enforceability. Statute constrains them; it does not write them |

**Two allocations that are deliberately Class B and are the ones most likely to be challenged:**

| File | Why not Class A |
|---|---|
| `LG-013` Warranty Terms | Consumer protection law **constrains** what may be excluded; it does not prescribe the warranty. The exclusions are ours to write and ours to defend. `T-A03` escalation and G5 apply; G6 does not, because there is no instrument to verify the text against. **If Legal Counsel concludes a consumer-protection instrument prescribes mandatory warranty content, this file reclassifies to A and the split becomes 7/17 — a register change, not a local edit** (`O-02`) |
| `LG-022` Quality Policy | ISO 9001:2015 is a **certification standard**, not an enacted instrument. It is audited, not enforced by a regulator. Class B with a certification-body review, which is stricter than G5 in practice but is not G6 |

### 4.3 Bilingual derivation — why these eight are English-only

`CG-010` §3.2 gives the split as **16 bilingual / 8 English-only** with a one-line rationale:
*"Consumer- and employee-facing terms, privacy, warranty, refund, data. Vendor, seller, brand and
internal policy sets remain English — those counterparties contract in English."* It does not
enumerate. **`LR-02`: this is the enumeration.**

| File | English-only | Reason |
|---|:--:|---|
| `LG-001` | ✔ | Internal register, worked by Legal and the content function |
| `LG-003` | ✔ | `CG-010` §3.3: corporate users — *"portal UI yes; contractual and technical documents English"* |
| `LG-004` | ✔ | Named in the §3.2 rationale as a seller set. **This is the uncomfortable one — see `O-01`** |
| `LG-005` | ✔ | 17+ brand partners, international, contract in English (`CG-010` §3.3: "No") |
| `LG-006` | ✔ | Vendors and suppliers contract in English (`CG-010` §3.3: "No") |
| `LG-007` | ✔ | Alliance and reseller partners are commercial counterparties contracting in English |
| `LG-021` | ✔ | Internal policy set; audited by certification bodies working in English |
| `LG-024` | ✔ | Internal obligation register; filings are made in the form the regulator prescribes |

The other sixteen are bilingual, and under rule `CM-R6` **none of them can reach `Approved` until
the Bengali counterpart passes in-context linguistic sign-off** under `BN-018`.

| # | Rule |
|---|---|
| **LR-03** | **English governs in a dispute** for every bilingual `LG` file, and the file says so in its own §3 Definitions. This closes `CG-010` §12 open question 2, which is registered against `LG-002`, `LG-013` and `LG-015` |
| **LR-04** | `LR-03` does not reduce the Bengali version's operative effect where a Bengali-reading counterparty relied on it. Where the two diverge in substance, that is a **content defect to be corrected**, not a conflict to be won on a governing-language clause (`T-C06`) |
| **LR-05** | A translation that cannot carry the English obligation faithfully escalates under `CG-013` `T-C06` before either version is approved |

> **`LR-03` is a legal drafting convention with a real limit.** A governing-language clause
> settles which text a court construes. It does not make a materially different Bengali version
> harmless — a counterparty who was shown Bengali and relied on it has an argument regardless.
> The clause protects against translation *ambiguity*; `LR-04` and `BN-018` are what protect
> against translation *error*.

### 4.4 Acceptance-capture taxonomy

Six mechanisms. Each proves something different, and the difference matters when the term is
challenged.

| # | Mechanism | Used for | What it proves | What it does not prove |
|---|---|---|---|---|
| **AC-1** | **Click-wrap** — affirmative tick or button, version recorded | `LG-002`, `LG-003`, `LG-011` | The user performed an act of assent to a specific version at a specific time from a specific device | That the user read it |
| **AC-2** | **E-signature** — `M24` envelope with a completion certificate (`FR-DMS-030`) | `LG-004`, `LG-005`, `LG-006`, `LG-007` | Signer identity to the assurance level used, integrity of the signed content, non-repudiation | More than the assurance level chosen supports (`LG-019` §4) |
| **AC-3** | **Wet signature on a printed form**, scanned and filed | `LG-013` at counter intake on `DT-002` | Physical assent at handover | Which version was printed, unless the version is on the page — **`LR-06` requires it** |
| **AC-4** | **Attestation** — named population acknowledges, tracked (`FR-GRC-030`) | `LG-020`, `LG-021`, `LG-022`, `LG-023` | The individual was given the policy and confirmed receipt | Comprehension. Where comprehension matters, `M22` assessment evidences it |
| **AC-5** | **Per-event consent, logged** | `LG-016` remote sessions (`BRU-RMS-01`), `LG-008` consent per purpose (`BRU-CPM-07`) | Consent for *this* event or purpose, with the notice version recorded (`BRU-CPM-08`) | Anything about a later event |
| **AC-6** | **Publication** — notice or statement made available, with a publication record | `LG-009`, `LG-012`, `LG-018`, `LG-024`, `LG-010` | That the company published it, from when, and in what version | Assent. **A notice is not a contract** |

| # | Rule |
|---|---|
| **LR-06** | Every acceptance mechanism records the **document version**. A recorded acceptance without a version is an acceptance of nothing (`SO-03`) |
| **LR-07** | Transactional necessity and marketing consent are **never bundled** into one act of acceptance (`UI-042` §3.1, `NT-002`) |
| **LR-08** | Acceptance of portal terms is **never** treated as consent for personal-data processing. They are separate legal acts captured separately, however adjacent they appear on screen |
| **LR-09** | Where a counterparty acts through a delegate — a corporate portal administrator, a shop's employee — the register records **both** the accepting individual and the entity bound (`LG-003` §2) |
| **LR-10** | An acceptance record is written by the platform, never edited by a human, and is subject to `BRU-SEC-11` insert-only audit |

### 4.5 The version-acceptance ledger

This is the record `SO-05` requires and the reason `LG-001` is `P0`/`W1` rather than a
documentation task. **`LR-11`: it is built before `LG-002` goes live at W2, not after.**

| Field | Type | Req | Notes |
|---|---|:--:|---|
| `acceptance_id` | uuid | ✔ | Immutable |
| `legal_content_id` | char(6) | ✔ | `LG-002`…`LG-024` |
| `document_version` | char(10) | ✔ | The `CG-006` version string, e.g. `1.0`, `2.1` |
| `document_hash` | char(64) | ✔ | SHA-256 of the exact rendered text accepted — **the defence against "that is not what it said"** |
| `language_presented` | enum | ✔ | `bn` / `en` — which version the counterparty actually saw |
| `party_id` | fk | ✔ | → `fix.party` (`M33`) |
| `entity_bound_id` | fk |  | Where the acceptor acts for an entity (`LR-09`) |
| `acceptor_user_id` | fk | ✔ | The identity that performed the act |
| `mechanism` | enum | ✔ | `AC-1`…`AC-6` per §4.4 |
| `accepted_at` | timestamptz | ✔ | Stored UTC, presented Asia/Dhaka (`05-02` DM-08) |
| `evidence_ref` | text | ✔ | `M24` document or envelope reference; completion certificate for `AC-2` |
| `ip_or_device` | text | ✔ | Per `FR-DMS-030`; redacted from logs per `BRU-SEC-24` |
| `notice_version_shown` | char(10) |  | **Mandatory where `mechanism = AC-5`** — `BRU-CPM-08` invalidates consent without it |
| `superseded_by` | fk |  | The later acceptance that replaced this one; **never a delete** |
| `withdrawn_at` | timestamptz |  | Consent withdrawal (`BRU-CPM-09`); the acceptance row itself is retained |

| # | Rule |
|---|---|
| **LR-12** | The ledger is **append-only**. Re-acceptance writes a new row and points `superseded_by`; it never overwrites |
| **LR-13** | `document_hash` is computed over the rendered text in the language presented. Two languages produce two hashes and, where both were shown, two rows |
| **LR-14** | The ledger is queryable by party and by date to answer *"what applied to this transaction"* in a single call. `FR-DMS-033` requires verification to work **years later**; so does this |
| **LR-15** | Withdrawal of consent does not delete the acceptance record. The record is the evidence that processing before withdrawal was lawful |
| **LR-16** | The ledger is retained per `LG-009` — **for the longer of the counterparty relationship plus the limitation period, or the statutory processing-record minimum** |

### 4.6 Effective dates, notice and re-acceptance

| Change type (`CG-006` §2) | Notice before effect | Re-acceptance | Files most affected |
|---|---|:--:|---|
| **PATCH** — typo, formatting, broken link | None | No | Any |
| **MINOR** — clarification that does not change an obligation | Published change note | No | Any |
| **MAJOR** — any change to an obligation, right, charge, exclusion, liability or data use | **Advance notice to every accepting counterparty** | **Yes** | `LG-002`, `LG-004`, `LG-013`, `LG-015` |
| **Statutory-driven** — the instrument changed | Immediate publication; notice with the change | Where the change alters what the counterparty agreed to | `LG-008`, `LG-009`, `LG-012`, `LG-018`, `LG-019`, `LG-024` |

| # | Rule |
|---|---|
| **LR-17** | **A MAJOR change to consumer-facing terms is not retrospective.** Work already commenced continues under the terms accepted for it. The register is what makes that determinable |
| **LR-18** | Notice periods are stated in the file's own §9 Change Control, not invented at the time of change |
| **LR-19** | Continued use is **not** treated as acceptance of a MAJOR change to `LG-002`. An affirmative act is required (`AC-1`) |
| **LR-20** | A statutory change fires `CG-007` §7 re-approval on **every** file citing the instrument — the register's citation column is how that set is found. Not memory |

### 4.7 Sign-off log

One row per file per version. Empty at issue; **`LR-21`: a blank row is not a defect, but a
blank row on a file at `status: Approved` is** (`SO-04`, check **E2**).

| File | Ver | G1 | G2 | G3 | G4 | G5 | G6 | Approver (named) | Date | Evidence ref |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|---|---|
| LG-001 | 1.0 | ☐ | ☐ | — | — | ☐ | — | *pending* | | |
| LG-002 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | — | *pending* | | |
| LG-003 | 1.0 | ☐ | ☐ | — | — | ☐ | — | *pending* | | |
| LG-004 | 1.0 | ☐ | ☐ | — | — | ☐ | — | *pending* | | |
| LG-005 | 1.0 | ☐ | ☐ | — | — | ☐ | — | *pending* | | |
| LG-006 | 1.0 | ☐ | ☐ | — | — | ☐ | — | *pending* | | |
| LG-007 | 1.0 | ☐ | ☐ | — | — | ☐ | — | *pending* | | |
| LG-008 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | ☐ | *pending* | | |
| LG-009 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | ☐ | *pending* | | |
| LG-010 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | — | *pending* | | |
| LG-011 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | — | *pending* | | |
| LG-012 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | ☐ | *pending* | | |
| LG-013 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | — | *pending* | | |
| LG-014 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | — | *pending* | | |
| LG-015 | 1.0 | ☐ | ☐ | ☐ | ☐ | ☐ | — | *pending* | | |
| LG-016 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | — | *pending* | | |
| LG-017 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | — | *pending* | | |
| LG-018 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | ☐ | *pending* | | |
| LG-019 | 1.0 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | *pending* | | |
| LG-020 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | — | *pending* | | |
| LG-021 | 1.0 | ☐ | ☐ | — | — | ☐ | — | *pending* | | |
| LG-022 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | — | *pending* | | |
| LG-023 | 1.0 | ☐ | ☐ | — | ☐ | ☐ | — | *pending* | | |
| LG-024 | 1.0 | ☐ | ☐ | — | — | ☐ | ☐ | *pending* | | |

**Gate load, counted from the rows above:** 24 × G1, 24 × G2, **2 × G3** (`LG-015`, `LG-019`),
**16 × G4**, **24 × G5**, **6 × G6**.

> **The G5 number is the programme's binding constraint, and it is already recorded as a risk.**
> `CG-013` `CR-01` states that Legal review capacity is the constraint on 75 Class A and B files
> across the whole register. Twenty-four of those are here, all requiring G5 at a 10-working-day
> service level, and six also requiring G6 at 15 working days driven by **external adviser
> availability**. `LG-013` and `LG-022` are `W1`. Six W2 files carry G6. **Legal and statutory
> review for Category 10 must be commissioned at W0, not requested at the W1 and W2 gates**
> (`O-03`).

### 4.8 Statutory citation index

Which files re-open when an instrument changes (`LR-20`). Instrument currency is held by
`05-06` §6.1, **verified 2026-08-12**; this table maps it to content.

| Instrument | Files that cite it | Currency owner |
|---|---|---|
| **Personal Data Protection Act 2026** (Law 63 of 2026) | `LG-008`, `LG-009`, `LG-010`, `LG-011`, `LG-012`, `LG-016`, `LG-017`, `LG-020`, `LG-021`, `LG-024`, `LG-005`, `LG-006` | CDO |
| Personal Data Protection (Amendment) Ordinance 2026 (No. 23 of 2026) | `LG-012`, `LG-009` | CDO |
| **Cyber Security Ordinance 2025** | `LG-012`, `LG-020`, `LG-021`, `LG-024` | CTO |
| **ICT Act 2006** | `LG-019`, `LG-002`, `LG-021` | Legal Counsel |
| Evidence Act 1872 (as amended 2022) | `LG-019` | Legal Counsel |
| **VAT and Supplementary Duty Act 2012** and rules | `LG-009`, `LG-014`, `LG-024` | CFO |
| **Income Tax Act 2023** and the applicable Finance Act | `LG-009`, `LG-024` | CFO |
| **Consumer Rights Protection Act 2009** | `LG-013`, `LG-014`, `LG-002`, `LG-015` | Legal Counsel |
| Digital Commerce Operation Guidelines 2021 | `LG-014`, `LG-002`, `LG-004` | Legal Counsel with CCO |
| **Bangladesh Labour Act 2006** and Labour Rules 2015 | `LG-020`, `LG-023`, `LG-009` | HR Director |
| **Environment Conservation Act 1995** and the e-waste rules 2021 | `LG-018`, `LG-024`, `LG-017` | Quality Manager |
| Contract Act 1872 · Limitation Act 1908 · Arbitration Act 2001 | `LG-002`…`LG-007`, `LG-013`…`LG-017` | Legal Counsel |
| Money Laundering Prevention Act 2012 · Anti-Corruption Commission Act 2004 | `LG-023`, `LG-006` | CFO |
| ISO 9001:2015 · ISO/IEC 27001:2022 | `LG-022`, `LG-021` | Quality Manager / CTO |

> **`LR-22`: this index is not a legal opinion and no file relies on it as a source.** It is a
> routing table for `CG-007` §7 re-approval. Every citation is verified in the citing file
> against a primary source at gate G6 or G5, per `CG-012` `EV-01`. Where a citation here is
> section-specific, the **section number is unverified in this file** and is verified in the file
> that relies on it.

### 4.9 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | **`LG-004` is English-only, and marketplace sellers are the counterparty class `CG-010` §3.3 marks bilingual.** 500–2,000 sellers — freelance engineers and small shops — are predominantly Bengali-first, and `BRU-MKP-17` gives them a right of appeal against earnings recovery. An English-only agreement is enforceable and may still be the wrong instrument to govern that population. **Reconcile `CG-010` §3.2 with §3.3 explicitly, either way** | **Yes — blocks `LG-004` G5** | Legal Counsel with Localisation Lead |
| **O-02** | Whether a consumer-protection instrument prescribes mandatory warranty content. If it does, `LG-013` becomes Class A and the split becomes 7/17 | **Yes — blocks `LG-013`** | Legal Counsel |
| **O-03** | G5 and G6 capacity is not commissioned. 24 × G5 and 6 × G6 with W1 and W2 files in scope (`CG-013` `CR-01`) | **Yes — blocks the W1 gate** | Legal Counsel with Programme Director |
| **O-04** | The split-residency legal opinion (`05-06` DEP-31 / D-13, `CG-013` `CR-08`) is outstanding and is upstream of `LG-008`, `LG-012` and every consent string | **Yes** | CTO with Legal Counsel |
| **O-05** | The marketplace principal-or-agent determination (`BRU-MKP-15`, `BRU-TAX-17`, D-03, `RSK-022`) is outstanding and is upstream of `LG-004` commission, payout and liability terms | **Yes — blocks `LG-004`** | CFO |
| **O-06** | The version-acceptance ledger (§4.5) is not in any module's feature register as specified. `M24` provides envelopes and completion certificates; **nothing owns the ledger that indexes them by party and version** | **Yes — blocks `LG-002` at W2** | CTO |
| **O-07** | No `RF-006` decision log exists yet (`CG-013` `CR-11`), so decisions taken in §4.2, §4.3 and `LR-03` are recorded here in the interim and must transfer on `RF-006` creation | No | Programme Content Lead |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md`](../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md) | The gates, the approval-record schema and rules `SO-01`…`SO-07` |
| [`../00_Content_Governance_and_Standards/CG-002_Content_Operating_Model_and_RACI.md`](../00_Content_Governance_and_Standards/CG-002_Content_Operating_Model_and_RACI.md) | Class definitions and the 6/18 split this file derives |
| [`../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | The 16/8 split this file derives, and open question 2 that `LR-03` closes |
| [`../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) | MAJOR/MINOR/PATCH definitions used in §4.6, and statutory pinning |
| [`../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md`](../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md) | The triggers that route content into G5 and G6, and `CR-01`, `CR-07`, `CR-08` |
| [`LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md`](LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md) | The evidentiary basis for `AC-1`, `AC-2` and `AC-5` |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | Retention of the ledger and the sign-off evidence |
| [`../../1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M24_Document_Records_and_ESignature.md`](../../1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M24_Document_Records_and_ESignature.md) | Controlled-document workflow, envelopes, completion certificates, sealing, verification |
| [`../../1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60_Governance_Risk_and_Compliance.md`](../../1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60_Governance_Risk_and_Compliance.md) | Policy library, attestation, obligation register, retention definition |
| [`../../1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33_Customer_and_Party_Master_Management.md`](../../1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33_Customer_and_Party_Master_Management.md) | `BRU-CPM-08` — consent invalid unless the notice version is recorded with it |
| `RF-006` Content Decision Log · `RF-010` Ownership Register · `RF-011` Content Risk Register | Where §4.2, §4.3, `LR-03` and `O-01`…`O-07` transfer when Category 99 is authored |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | At every wave boundary (`CM-R9`), and annually for Class A and B currency (`CG-007` §7) |
| Trigger for out-of-cycle review | Any statutory change in §4.8; any `LG` file version change; any new `LG` file; any acceptance-mechanism change; any audit finding naming a Category 10 file |
| Update procedure | (1) Amend the §4.1 row · (2) **regenerate the derived totals table**, never edit it in place (`CM-R2`, gate F7) · (3) grep the repository for every restatement of a changed figure (F7 sweep) · (4) update the §4.7 sign-off row · (5) log the decision in `RF-006` |
| Who may amend | Legal & Compliance. The class, gate and language columns may be amended **only** with a matching change to `CG-002`, `CG-007` or `CG-010` — a divergence here is a gate F7 failure, not a local correction |
| Owner | Legal Counsel |
| Enumeration rule | Every count in this file is produced by counting the §4.1 rows at the time of writing and carries the date in the front matter (`CP-11`, `EV-06`) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections plus DoD, none removed
- [x] Every factual claim carries a source and a verification date; section-level statutory claims are explicitly marked unverified in this file (`LR-22`)
- [x] All 24 registered files enumerated with class, gates, language, priority, wave, approver and acceptance mechanism
- [x] **Derived totals regenerated from the rows, not carried forward** — gate F7 reconciliation table present with all seven dimensions
- [x] Content-class and bilingual allocations **derived with reasoning**, so they are re-examinable rather than re-invented
- [x] Version-acceptance ledger specified to field level, including `document_hash` and `notice_version_shown`
- [x] Terminology matches `CG-004`
- [x] All internal links resolve
- [x] Bengali counterpart — n/a (`bilingual: no`, derived in §4.3)
- [ ] Named approver recorded — **pending Legal Counsel (`O-03`)**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decisions in §4.2, §4.3 and `LR-03` transferred to `RF-006` — **outstanding, `RF-006` does not exist (`O-07`)**
- [ ] **Version-acceptance ledger owned by a module (`O-06`)** — outstanding; blocks `LG-002` at W2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
