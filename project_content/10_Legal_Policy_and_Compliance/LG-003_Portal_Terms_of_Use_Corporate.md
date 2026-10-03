---
id: LG-003
title: Portal Terms of Use — Corporate
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance
author: Legal & Compliance with Account Management and Corporate Services
reviewers: [Legal Counsel, Chief Data Officer, CFO delegate, Corporate Services Head, Account Management, CTO delegate]
approver: Legal Counsel
content_class: B
purpose: >
  The terms on which a named individual uses the P04 corporate portal on behalf of a client
  organisation — delegated authority, approval limits, estate data accuracy, invoice dispute,
  confidentiality and account administration. Corporate portal users act under authority delegated
  by their employer, so the portal terms and the master service contract must interlock without
  contradiction; where they do not, an approval given in the portal binds nobody.
traces_to: [P04, M05, M07, M08, M17, M20, M25, LG-001, LG-002, LG-008, LG-009, LG-012, LG-015, LG-016, LG-019, DT-020, DT-030, DT-031, EA-01, EA-02, EA-03, EA-08, EA-09, EA-10, BRU-CTR-01, BRU-CTR-02, BRU-CTR-04, BRU-ARB-13, BRU-RMS-13]
priority: P1
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 P04 capability set — multi-user access under one corporate account, role assignment, multi-level approval chains (user → line manager → 1000FiX admin), estate management with bulk upload, contract entitlement view, SLA status and service credits, consolidated invoice approval and dispute, scoped reporting, compliance certificate download
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §8 external party access rules EA-01, EA-02, EA-03, EA-08, EA-09, EA-10, EA-12
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-CTR-02 out-of-scope work is billed separately and never silently absorbed; BRU-CTR-04 entitlement over-consumption is blocked or flagged, never invisible
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §7 approval authority matrix — repair estimate thresholds at BDT 5,000, 25,000 and 100,000
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md §3.3 — corporate client users are bilingual for portal UI, English for contractual and technical documents
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# LG-003 — Portal Terms of Use (Corporate)

| Item | Value |
|---|---|
| Document class | **Terms** — click-wrap, subordinate to an executed master contract |
| Counterparty | A named individual using `P04` on behalf of a Client organisation, **and the Client itself** |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending approval* |
| Acceptance capture method | **`AC-1` click-wrap at first login**, recorded per individual and per Client in the `LG-001` §4.5 ledger, with `entity_bound_id` populated (`LR-09`) |
| Version accepted by users | Recorded in `LG-001` — per individual **and** per Client entity |
| External counsel review | **Required** — the interlock with the master contract and the §4.3 authority position |
| Bengali version | **Not required** (`CG-010` §3.2, §3.3 — corporate contractual documents are English) |

> ⚠ **Class B. The risk in this document is not the wording; it is the seam.**
> A corporate user approves an estimate in `P04`. Did they have authority? Under whose delegation?
> Does the master contract say the same thing as the portal? **§4.3 exists because the answer must
> be the same in both places, and only one of them is drafted by the Client.**
>
> **Conformance note.** All ten template sections retained in order. Gate questions and open items
> appear as §1.2 and §1.3, not as added sections (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with Account Management | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — Corporate Services Head | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — Legal Counsel | *pending* | | |

### 1.2 Questions for Legal Counsel (G5)

| # | Question | Consequence of getting it wrong |
|---|---|---|
| **CO1** | Can the Company rely on a portal approval given by a Client's employee who lacked internal authority, and what must the Company do to be able to rely on it? | Unbilled work, or an unpaid invoice for work the Client says it never authorised |
| **CO2** | Does §4.3.4 — the Client is responsible for maintaining its own users' roles and limits — hold, or does the Company carry a duty to verify authority above a value threshold? | A general duty to verify would make the `P04` approval chain advisory only |
| **CO3** | Where the portal terms and an executed master contract conflict, does §2's precedence clause bind the Client's signatory? | Two documents, two answers, and the Client picks |
| **CO4** | Is the §5.3 exclusion of indirect and consequential loss enforceable between commercial parties in Bangladesh? | This is the Company's principal commercial exposure on managed services |
| **CO5** | Is arbitration under §8 the right route for a government client, or do public-procurement terms override? | `DT-031` §6 already flags that tender-prescribed service levels override ours |
| **CO6** | May the Company suspend portal access for non-payment while the underlying service contract continues? | §7.2 as drafted assumes yes |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | `CO1`–`CO6` unanswered | **Yes — blocks `Approved`** | Legal Counsel |
| **O-02** | `DT-030` is the master contract template set. **The interlock in §2 must be verified clause by clause against it**, not asserted | **Yes** | Legal Counsel with Account Management |
| **O-03** | Corporate estate data is uploaded in bulk by the Client. **No document states who owns the accuracy of an asset register the Client populated and the Company bills against** — §4.4 takes a position that needs G5 confirmation | **Yes** | Legal Counsel with CFO |
| **O-04** | `LG-016` managed-services and remote-access consent is `W4`, the same wave as this file. The two must be authored and reviewed together, because a Client administrator granting remote access through `P04` is exercising a right created there | No — sequencing | Legal Counsel |

---

## 2. Scope and Parties

| Party | Identity |
|---|---|
| **The Company** | 1000FiX Services Limited |
| **The Client** | The organisation that has an executed service contract, or an approved account, with the Company |
| **The User** | A named individual to whom the Client has granted `P04` access |

**Precedence — the clause this document exists for:**

| Rank | Instrument | Governs |
|---|---|---|
| **1** | The **executed master service contract** (`DT-030`) and its schedules, including the SLA annex (`DT-031`) | Commercial terms, scope, price, service levels, credits, term, liability as negotiated |
| **2** | `LG-015` AMC / SLA Master Terms | Where the executed contract adopts them by reference |
| **3** | **These terms** | Use of the portal, User conduct, account administration, data accuracy, and anything the contract is silent on |
| **4** | `LG-008` / `LG-009` / `LG-012` | Personal data — **these prevail over 1, 2 and 3** on data protection, because they state statutory positions the parties cannot contract around |

| # | Clause |
|---|---|
| **2.1** | A User accepts these terms **on their own behalf and as agent of the Client**. Acceptance binds the Client to the portal-use provisions |
| **2.2** | Where these terms conflict with the executed contract on a **commercial** matter, the contract prevails (rank 1) |
| **2.3** | Where these terms conflict with the executed contract on **personal data**, `LG-008`, `LG-009` and `LG-012` prevail (rank 4), and the conflict is escalated as a compliance defect (`CG-013` `T-C05`) |
| **2.4** | An individual consumer using `P01` is governed by `LG-002`, not this document. **A person may be both**, in different capacities, and the ledger records which capacity each acceptance was given in |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Estate** | The set of assets the Client has registered in the portal (`M17`) |
| **Entitlement** | The service volume, response level or coverage the contract grants, tracked in `M08` |
| **Delegated limit** | The maximum value a User may approve without a further approval step, set in the `P04` approval chain |
| **Approval chain** | User → Client line manager → Company administrator, as configured for the Client (`P04` capability set) |
| **Out-of-scope work** | Service outside the contract's scope, billed separately and never silently absorbed (`BRU-CTR-02`) |
| **Consolidated invoice** | The periodic invoice covering multiple sites, departments or assets (`DT-020`) |
| **Service credit** | The remedy for a measured service-level failure, calculated per `LG-015` and `DT-031` |
| **Governing text** | This English text. No Bengali version is issued (`CG-010` §3.2) |

---

## 4. Terms

### 4.1 Access and administration

| # | Clause |
|---|---|
| **4.1.1** | The Company grants the Client access to `P04` for the term of the contract, for the Client's internal business use |
| **4.1.2** | Access is by named individual through Company single sign-on (`PS-01`). **Shared or generic accounts are not permitted**, because they defeat the approval record in §4.3 |
| **4.1.3** | The Client nominates administrators who add, amend and remove Users and set their roles and limits |
| **4.1.4** | **The Client notifies the Company promptly when a User leaves.** Until notified, the Company acts on the access the Client configured |
| **4.1.5** | External sessions time out after 30 minutes of inactivity (`EA-08`). **Multi-factor authentication is mandatory for any action with financial consequence** (`EA-09`) |
| **4.1.6** | Bulk export is limited, rate-controlled and logged (`EA-12`). Automated or programmatic extraction outside a contracted API is not permitted |

### 4.2 What the User can and cannot see

| # | Clause |
|---|---|
| **4.2.1** | A User sees **only the Client's own data**, further scoped by their role in the Client organisation (`EA-03`, `BRU-RMS-13`) |
| **4.2.2** | A User never sees the Company's cost, margin or internal notes, or any other client's data (`EA-01`, `EA-02`) |
| **4.2.3** | **Every external access to customer personal data is logged and reportable** (`EA-10`). The Client may request the log for its own users |

### 4.3 Delegated authority — the operative clause

| # | Clause |
|---|---|
| **4.3.1** | An approval given in the portal by a User within their delegated limit is treated by the Company as the Client's authorisation, and the Company may proceed on it |
| **4.3.2** | The **Client** sets each User's delegated limit and approval chain. The Company configures what the Client instructs |
| **4.3.3** | Above the Client's configured limit, the portal requires the next approval in the chain before work proceeds. The Company's own thresholds for estimate approval — **BDT 5,000, BDT 25,000 and BDT 100,000** (`05-04` §7) — apply in addition, not instead |
| **4.3.4** | **The Client is responsible for keeping User roles and limits current.** The Company does not independently verify a User's internal authority — **subject to `CO2`** |
| **4.3.5** | Every approval is recorded with the approver, the timestamp, the value and the version of the terms in force (`LG-001` §4.5, `LG-019`) |

> **`CL-01`. §4.3.4 is where the money is.** If Legal Counsel answers `CO2` by imposing a
> verification duty on the Company above a threshold, §4.3.4 inverts and the `P04` approval chain
> becomes advisory. That is a build consequence, not a wording consequence, and it is why the
> question is asked at `W4` rather than after the first disputed invoice.

### 4.4 Estate data

| # | Clause |
|---|---|
| **4.4.1** | The Client uploads and maintains its asset estate. **The Client is responsible for its accuracy** |
| **4.4.2** | Coverage is validated against the contract before a request is accepted (`P04` capability set; `BRU-CTR-01`). **A request for an asset not on the estate, or not covered, is not refused silently** — the reason is shown |
| **4.4.3** | Where an asset is added after the contract date, coverage and price follow the contract's amendment terms, not the portal |
| **4.4.4** | Entitlement consumption is visible to the Client at all times. **Over-consumption is blocked or flagged for billing per the contract's configuration; it is never invisible** (`BRU-CTR-04`) |
| **4.4.5** | Where the estate is wrong and the Company has performed or billed on it in good faith, §4.4.1 governs — **subject to `O-03`** |

### 4.5 Service requests and out-of-scope work

Requests may be raised singly or in bulk. **Work outside the contract's scope is quoted and
approved separately before it proceeds, and is billed separately** (`BRU-CTR-02`). Out-of-scope
work is also outside the SLA (`DT-031` §5, `BRU-CTR-02`).

### 4.6 Service levels and credits

Service levels, the measurement method, the exclusions and the credit calculation are those in
`LG-015` and the contract's SLA annex (`DT-031`). **The Client sees the same measurement the
Company does** (`DT-031` `MI-06`). A credit is applied as a credit note or an invoice offset; it is
not paid in cash. **This document creates no service level and no credit.**

### 4.7 Invoicing, approval and dispute

| # | Clause |
|---|---|
| **4.7.1** | Consolidated invoices are issued on the contracted cycle with an itemised breakdown by site, department and asset (`DT-020`) |
| **4.7.2** | The Client may operate an internal invoice-approval workflow in the portal. **Internal approval is not a condition of the invoice becoming due** |
| **4.7.3** | A dispute must be raised within the period stated in the contract, identifying the disputed lines and the reason from the controlled taxonomy (`BRU-ARB-10`, `BRU-ARB-17`) |
| **4.7.4** | **Dunning is suppressed on the disputed amount only**, and the undisputed balance remains payable (`BRU-ARB-15`) |
| **4.7.5** | A dispute is closed with an outcome code; it cannot be closed as "resolved" without one (`BRU-ARB-17`) |
| **4.7.6** | Where the account exceeds its credit limit or its overdue threshold, it is placed on credit hold, which blocks new billable commitments until released by an authorised role (`BRU-ARB-13`). **The Client is notified when a hold is applied** |

### 4.8 Managed services and remote access

Where the contract includes managed services, remote access is governed by
[`LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md`](LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md).
**No remote connection is established without explicit, logged consent** (`BRU-RMS-01`), and
unattended access exists only where the contract grants it (`BRU-RMS-02`).

### 4.9 Confidentiality

Each party keeps the other's confidential information confidential, uses it only for the contract,
and returns or destroys it on termination. **The Company's service data about the Client's estate
is the Client's confidential information.** The Company's pricing, cost, margin, methods and
platform are the Company's.

### 4.10 Compliance evidence

The Client may download destruction certificates (`DT-034`), disposal certificates (`DT-035`) and
service evidence packs from the portal. **A certificate downloaded from the portal is the
Company's statement of what it did; it is not an audit opinion**, and the Client's own regulatory
duties remain the Client's.

### 4.11 Acceptable use

Users must not attempt unauthorised access, interfere with the platform, probe or test its
security without written permission, or use it to store or transmit unlawful material. **Security
testing requires prior written agreement**; unauthorised testing is treated as an incident.

---

## 5. Liability, Exclusions and Limits

> **This section applies only where the executed contract is silent.** Where the contract has a
> liability regime, the contract governs (§2.2). Provisional pending `CO4`.

| # | Clause |
|---|---|
| **5.1** | Each party is liable for loss it causes by breach of these terms, subject to §5.2–§5.5 |
| **5.2** | The Company is not liable for loss arising from: inaccurate estate data (§4.4.1); an approval given by a User the Client authorised in the portal (§4.3.1); the Client's failure to notify a leaver (§4.1.4); or the Client's own configuration of roles and limits |
| **5.3** | **Neither party is liable for indirect or consequential loss, loss of profit, loss of business, loss of goodwill or loss of anticipated saving** — provisional pending `CO4` |
| **5.4** | **Cap.** Aggregate liability under these terms is limited to the charges paid under the contract in the twelve months preceding the claim — provisional pending `CO4`, and superseded by any cap in the executed contract |
| **5.5** | Nothing limits liability that cannot lawfully be limited, including for fraud, for death or personal injury caused by negligence, or for a breach of a statutory data-protection duty |
| **5.6** | **Service credits under §4.6 are the remedy for a service-level failure to the extent `LG-015` provides.** Whether they are the *sole* remedy is `LG-015` `SL3`, not a question this document answers |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009` and `LG-012`. Contradiction is a compliance defect —
> check **F6**.

| # | Clause |
|---|---|
| **6.1** | Both parties process personal data relating to the Client's staff and the Company's staff. Each processes it for its own purposes and remains responsible for its own processing |
| **6.2** | Where the Company processes personal data **on the Client's instruction** — for example, personal data inside an estate upload, or data encountered during managed-services access — it does so under the contract, and **the Company's processing is treated as the Client's own** for statutory purposes (`NFR-098`) |
| **6.3** | The Company flows equivalent obligations to every processor and sub-processor it uses (`NFR-098`, `BRU-GRC-18`), and maintains a sub-processor register disclosed in `LG-012` §4.6 |
| **6.4** | Records of processing are maintained for a **minimum of five years** (`NFR-095`, `BRU-GRC-17`) |
| **6.5** | Certain identifiers, including National ID, passport number and TIN, are held in a **Bangladesh-resident** store and are not replicated outside Bangladesh (`NFR-086`, `BRU-CPM-06`). `LG-012` states what may and may not leave |
| **6.6** | A breach likely to cause significant damage is notified to the **National Data Management Authority** within the prescribed timeframe, and to the Client without undue delay (`NFR-094`, `FR-GRC-036`) |
| **6.7** | The Client's Users may exercise their own data-subject rights against the Company under `LG-010`, and the Company will inform the Client where a request affects the Client's records |
| **6.8** | Where the Client instructs processing the Company considers unlawful, the Company will say so in writing and may decline (`BRU-GRC-16`) |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **Contract ends or expires** | Portal access ends. **Future scheduled work orders are cancelled and the Client is notified** (`BRU-CTR-03`). Data is exportable for a stated period before closure |
| **Non-payment** | Contract suspension follows the notice sequence in the contract and cannot be applied without it (`BRU-CTR-05`). **Portal access suspension is subject to `CO6`** |
| **Breach of §4.11** | Access may be suspended immediately, with notice and a route to challenge |
| **User leaves the Client** | Access is revoked. Approvals the User already gave remain valid and remain the Client's |
| **In every case** | Invoices remain payable; confidentiality and §6 survive; statutory retention survives (`LG-009`); records under legal hold are not deleted (`BRU-SEC-23`) |
| **Offboarding of managed services** | Not complete until every agent is removed and every access revoked, evidenced (`BRU-RMS-11`) |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Account escalation** | The account manager, then the Corporate Services Head, per `SP-005` |
| **2 — Commercial escalation** | A meeting of authorised representatives within 15 business days of written notice |
| **3 — Arbitration** | Arbitration in Dhaka under the Arbitration Act 2001, one arbitrator, English language — **subject to `CO5`, and subject to any public-procurement route a government client must use** |
| **4 — Courts** | The courts of Dhaka retain jurisdiction for interim relief and for enforcement of an award |

Bangladesh law governs. **A billing dispute follows §4.7 first; §8 is not a route around it.**

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft for G5 | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A MAJOR change requires notice to the Client's nominated contact **and** to each User, with re-acceptance at next login |
| **9.2** | A change to these terms **never varies the executed contract**. Where a change would, it is a contract amendment and follows the contract's amendment clause |
| **9.3** | Every version and acceptance is recorded in `LG-001`, per individual and per Client entity (`LR-09`) |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-001_Legal_Content_Register_and_Signoff_Log.md`](LG-001_Legal_Content_Register_and_Signoff_Log.md) | Acceptance ledger with `entity_bound_id` | `LR-09` dual recording |
| [`LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md`](LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md) | Rank 2 in §2 | Service levels, credits, sole-remedy position |
| [`LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md`](LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md) | §4.8 | Consent capture, session recording |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) · [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) · [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | Rank 4 — prevail on data | §6 in full — check **F6** |
| [`LG-002_Portal_Terms_of_Use_Customer.md`](LG-002_Portal_Terms_of_Use_Customer.md) | The consumer equivalent | §2.4 capacity distinction |
| [`LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md`](LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md) | Evidentiary basis for §4.3.5 | Assurance level for approvals |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-030_Contract_and_AMC_Agreement_Template_Set.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-030_Contract_and_AMC_Agreement_Template_Set.md) | **Rank 1 — the interlock in §2 must be verified against it** (`O-02`) | Every commercial term |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md) | Schedule C of rank 1 | §4.6 |
| [`../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-020_Consolidated_Corporate_Invoice.md`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-020_Consolidated_Corporate_Invoice.md) | §4.7 | Dispute window, credit application |
| `HC-006` Help Set `P04` · `UI-014` `P04` UI copy · `EO-*` corporate onboarding | Explain these terms | No help text may state a term this does not |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **Four-rank precedence table** stated, including that data-protection files outrank the executed contract
- [x] The delegated-authority position stated as an operative clause with its inversion risk named (`CL-01`)
- [x] Liability clauses subordinated to the executed contract and marked provisional (`PR-01`)
- [x] External-party access rules `EA-01`…`EA-12` reflected rather than restated
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, derived in `LG-001` §4.3
- [ ] **`CO1`–`CO6` answered at G5** — outstanding, blocks `Approved`
- [ ] **§2 interlock verified clause by clause against `DT-030`** — outstanding, `O-02`
- [ ] **Estate-data accuracy position confirmed** — outstanding, `O-03`
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
