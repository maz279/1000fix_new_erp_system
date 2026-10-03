---
id: LG-005
title: Brand Partner Portal Terms
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance
author: Legal & Compliance with Commercial and Warranty Operations
reviewers: [Legal Counsel, Chief Data Officer, Finance Director, Quality Manager, Commercial Director, CTO delegate]
approver: Legal Counsel
content_class: B
purpose: >
  The terms on which an authorised brand partner accesses P08 — what data they receive, what they
  may do with it, the confidentiality boundary, evidence handling, audit rights and the limits of
  their access. Brand partners receive customer and technician personal data through the claims
  and evidence flow; if the boundary is not contractual it is not a boundary, and the company
  remains answerable for a disclosure it authorised without limits.
traces_to: [P08, M09, M15, M17, M23, M25, LG-001, LG-008, LG-009, LG-012, LG-021, DT-032, DT-033, MD-011, MD-017, SP-014, EA-05, EA-08, EA-09, EA-10, BRU-WTY-04, BRU-WTY-05, BRU-WTY-08, BRU-WTY-10, BRU-WTY-18, BRU-WTY-19, BRU-PCM-20, BRU-QMS-15, BRU-QMS-17, NFR-098]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 P08 capability set — claim decisioning with full evidence packs, evidence viewing including photographs and technician certification, reconciliation, consignment parts, rate cards, service performance on their brand, quality concerns and partner audits with evidence access, technician certification status, bulletins and recall notifications; KPIs including claim decision under 10 days
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §8 EA-05 — a brand partner sees only claims and service data relating to their own brand; EA-08, EA-09, EA-10
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M09 §9 BRU-WTY-05 claim valued at the brand rate-card version in force on the service date; BRU-WTY-08 brand partner sees only their own brand; BRU-WTY-10 certification gating; BRU-WTY-18 consignment reporting; BRU-WTY-19 defective-part return
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M23 §9 BRU-QMS-15 — evidence released to an external auditor requires a release approval and is logged; BRU-QMS-17 — suppliers and sellers audited against the same standards
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md §7 CR-05 — the "17+ brands" figure underpins an M22 control and is unverified
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# LG-005 — Brand Partner Portal Terms

| Item | Value |
|---|---|
| Document class | **Terms** — portal access terms, subordinate to the executed brand agreement |
| Counterparty | An authorised brand partner (manufacturer or its regional entity) and its named users |
| Governing law | **Bangladesh** — *subject to `BP1`, because several brand agreements are governed by foreign law* |
| Effective date | On publication, or on execution as an annex to the brand agreement |
| Acceptance capture method | **`AC-2` e-signature**, or execution as an annex to the brand agreement, recorded in `LG-001` with `entity_bound_id` |
| Version accepted by users | Recorded in `LG-001` — per named user **and** per brand entity |
| External counsel review | **Required** — the governing-law interaction and the §6.2 processor position |
| Bengali version | **Not required** (`CG-010` §3.2, §3.3 — brand partners are international and contract in English) |

> ⚠ **Class B. The exposure here is disclosure, not money.**
>
> `P08` gives a brand partner **photographs of a customer's device, a technician's diagnosis, the
> named technician's certification status, and service performance data** — and, through the
> partner-audit capability, access to evidence at branch level. Every one of those is personal data
> about someone who is not a party to this agreement.
>
> **§4.3 and §6 are the whole document. The rest is administration.**
>
> **Conformance note.** All ten template sections retained in order; gate questions and open items
> are §1.2 and §1.3 (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with Commercial | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — Finance Director (claims) with Quality Manager (audits) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — Legal Counsel | *pending* | | |

### 1.2 Questions for Legal Counsel (G5)

| # | Question | Why it matters |
|---|---|---|
| **BP1** | Where an executed brand agreement is governed by foreign law, do these Bangladesh-law portal terms operate as an annex under that law, or must they be re-issued per brand? | Seventeen-plus brands, potentially several governing laws, one portal |
| **BP2** | Is the brand partner a **controller in its own right** for claim data it receives, or the Company's processor? | It determines who answers a data-subject request about a claim, and whether §6.2 is a flow-down or a joint arrangement |
| **BP3** | May technician **names and certification status** be disclosed to a brand partner, and on what basis? `BRU-WTY-10` makes certification a claim condition, so the brand has a reason to see it — but the technician is an employee, not a party | Employee personal data disclosed to a commercial counterparty |
| **BP4** | May **customer device photographs** be disclosed where they may incidentally show the customer's data, home or premises? | `DT-033` evidence packs are photographic by design |
| **BP5** | What is the lawful basis for a brand partner conducting an **on-site audit** with evidence access at a branch (`BRU-QMS-15`)? | An external party inspecting records containing third-party personal data |
| **BP6** | Is the §5.4 cap appropriate where a brand's rate-card version determines claim value (`BRU-WTY-05`) and a version dispute could be large? | Claim valuation disputes are the predictable commercial dispute here |
| **BP7** | Are the **recall notification** obligations in §4.7 sufficient, and does receiving a recall notice create a duty on the Company toward the end customer? | A recall the Company knows about and does not act on is a safety exposure |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | `BP1`–`BP7` unanswered | **Yes — blocks `Approved`** | Legal Counsel |
| **O-02** | **The executed brand agreements are the rank-1 instrument and have not been reviewed against these terms.** `MD-017` holds the brand register; `CG-012` §7 names the executed agreements as the primary source | **Yes** | Commercial with Legal |
| **O-03** | **`CG-013` `CR-05`: the "17+ brands" figure is unverified** and underpins an `M22` certification control. This document is written for that population without knowing its size | No — does not change a term | Commercial |
| **O-04** | The claim submission window varies by brand (`BRU-WTY-08`). §4.4.5 refers to "the brand's stated window"; **no register holds those windows per brand** | Yes — blocks §4.4.5 | Warranty Operations |
| **O-05** | Whether a brand partner's own assessment of the Company (`BRU-PCM-20`, recorded verbatim and not editable by the account owner) is disclosable to that partner through `P08` | No | Commercial |

---

## 2. Scope and Parties

| Party | Identity |
|---|---|
| **The Company** | 1000FiX Services Limited, an authorised service provider |
| **The Brand Partner** | The manufacturer or authorised entity named in an executed brand agreement, listed in `MD-017` |
| **Portal User** | A named individual the Brand Partner authorises to use `P08` |

**Precedence:**

| Rank | Instrument | Governs |
|---|---|---|
| **1** | The **executed brand agreement** | Authorisation, rate cards, claim rules, reimbursement, consignment, term, commercial liability |
| **2** | **These terms** | Portal access, user conduct, confidentiality of what the portal exposes, evidence handling, audit conduct |
| **3** | `LG-008` / `LG-009` / `LG-012` | Personal data — **prevail over 1 and 2** |

| # | Clause |
|---|---|
| **2.1** | A Portal User accepts these terms on their own behalf and as agent of the Brand Partner |
| **2.2** | These terms **do not vary the brand agreement**, do not create an authorisation, and do not alter a rate card |
| **2.3** | Where the brand agreement is silent on portal use, evidence handling or data, these terms fill the gap |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Claim** | A warranty reimbursement claim submitted by the Company to the Brand Partner (`M09`) |
| **Evidence pack** | The photographs, diagnosis, parts record, technician certification and purchase proof supporting a claim (`DT-033`) |
| **Rate card** | The Brand Partner's published labour rates, parts pricing and claim rules, versioned in the portal |
| **Consignment parts** | Parts the Brand Partner supplies that remain its property until consumed (`BRU-WTY-04`) |
| **Brand-scoped data** | Data relating to the Brand Partner's own brand only. **The Brand Partner sees nothing else** (`EA-05`, `BRU-WTY-08`) |
| **Partner audit** | An audit the Brand Partner conducts of the Company's performance on its brand, under §4.6 |
| **Governing text** | This English text |

---

## 4. Terms

### 4.1 Access

| # | Clause |
|---|---|
| **4.1.1** | Access is granted for the term of the brand agreement, by named individual, through Company single sign-on (`PS-01`) |
| **4.1.2** | **Shared accounts are not permitted.** Every claim decision is attributed to a named decision-maker |
| **4.1.3** | The Brand Partner notifies the Company promptly when a Portal User leaves |
| **4.1.4** | Sessions time out after 30 minutes of inactivity (`EA-08`); **multi-factor authentication is mandatory for any action with financial consequence** (`EA-09`) — a claim decision is such an action |
| **4.1.5** | **Every external access to customer personal data is logged and reportable** (`EA-10`). The Company may produce that log to a regulator or a data subject |

### 4.2 Brand scoping — the hard boundary

| # | Clause |
|---|---|
| **4.2.1** | **The Brand Partner sees only claims and service data relating to its own brand** (`EA-05`, `BRU-WTY-08`). This is enforced by the platform, not by undertaking |
| **4.2.2** | The Brand Partner never sees another brand's data, the Company's cost or margin, internal notes, or any other party's data (`EA-01`, `EA-02`) |
| **4.2.3** | The Brand Partner must not attempt to infer another brand's volumes, pricing or performance from what it can see, and must not aggregate Company data with third-party data for that purpose |

### 4.3 Data the Brand Partner receives, and what it may do with it

> **`CL-01`. This is the clause the document exists for.** The list is explicit because a general
> "data received through the portal" formula would leave the customer and the technician unnamed,
> and they are the people whose data is being disclosed.

| Data | Why the Brand Partner receives it | Permitted use |
|---|---|---|
| **Device serial or IMEI, model, fault, diagnosis** | To decide the claim | Claim decisioning; warranty administration; **failure-pattern analysis on its own brand** |
| **Photographs of the device before and after repair** | Evidence required by the claim rules (`BRU-WTY-01`) | Claim decisioning only. **`BP4`** |
| **Parts replaced and consignment consumption** | Reimbursement and replenishment (`BRU-WTY-18`) | Claim and inventory administration |
| **Named technician and certification status** | `BRU-WTY-10` makes certification a claim condition | **Verification of claim eligibility only.** Not performance management of the individual. **`BP3`** |
| **Purchase proof supplied by the customer** | Warranty entitlement | Claim decisioning only |
| **Customer name and contact, where the brand's rules require it** | Warranty registration and validation | **Claim decisioning only.** Not marketing, not profiling, not transfer to a third party |
| **Aggregate service performance on the brand** — volume, turnaround, first-time fix, rework, CSAT, failure patterns by model | The brand's legitimate interest in service quality | Quality management and engineering |

| # | Clause |
|---|---|
| **4.3.1** | The Brand Partner uses portal data **only for the purposes in the table** and for no other purpose |
| **4.3.2** | The Brand Partner must not use portal data to contact a customer directly, unless the brand agreement expressly provides for it and the customer's consent basis covers it |
| **4.3.3** | The Brand Partner must not disclose portal data to a third party, including an affiliate, except to a processor bound by equivalent obligations and disclosed to the Company (`NFR-098`) |
| **4.3.4** | The Brand Partner must not export portal data in bulk beyond what the portal provides, and must not use automated extraction (`EA-11`, `EA-12`) |
| **4.3.5** | The Brand Partner **must not use portal data as training data for a model** without the Company's written agreement and a confirmed lawful basis |

### 4.4 Claims

| # | Clause |
|---|---|
| **4.4.1** | The Company submits claims with the complete evidence set the brand's rules require. **A claim without the complete set is blocked by the Company's own system, not merely flagged** (`BRU-WTY-09`, `BRU-ARB-19`) |
| **4.4.2** | The Brand Partner decides claims within the period in the brand agreement. **The Company's service target is a decision within 10 days** (`P08` KPI); where the agreement is silent, 10 business days applies |
| **4.4.3** | A rejection must state a reason. **A rejection without a reason cannot be reconciled and is treated as undecided** |
| **4.4.4** | A claim is valued at the **rate-card version in force on the service completion date** (`BRU-WTY-05`), and claims are raised in the agreed currency at the rate prevailing on that date (`BRU-ARB-20`) |
| **4.4.5** | Where the brand's rules impose a submission window, the Company submits within it; **the window must be stated in the portal to be enforceable against the Company** — `O-04` |
| **4.4.6** | Where the brand requires the defective part to be returned, reimbursement is conditional on evidenced return (`BRU-WTY-19`) |
| **4.4.7** | A rate-card change applies **prospectively from its published effective date** and does not re-value a decided or submitted claim |

### 4.5 Consignment parts

Consignment parts remain the Brand Partner's property until consumed. **Brand-supplied warranty
parts cannot be consumed on non-warranty jobs** (`BRU-WTY-04`). Consumption is reported in the same
cycle as the claim (`BRU-WTY-18`). Defective returns follow the brand agreement.

### 4.6 Quality concerns and partner audits

| # | Clause |
|---|---|
| **4.6.1** | The Brand Partner may raise a quality concern in the portal and receive the Company's CAPA response (`M23`) |
| **4.6.2** | The Brand Partner may conduct partner audits at the frequency and scope the brand agreement provides, on reasonable notice, during business hours |
| **4.6.3** | **Evidence released to an external auditor requires a release approval and is logged** (`BRU-QMS-15`). An auditor may inspect what is released; they may not copy, photograph or remove records containing third-party personal data without approval |
| **4.6.4** | Audit findings are recorded, and the Company's response is recorded with them. **Sellers and suppliers are audited against the same standards as owned operations** (`BRU-QMS-17`) |
| **4.6.5** | The lawful basis for audit access to records containing personal data is **`BP5`** and must be settled before the first audit |

### 4.7 Bulletins, technical notices and recalls

The Brand Partner may issue bulletins, technical notices and **recall notifications** through the
portal. The Company acknowledges receipt, distributes them into `KB` technical content, and acts on
a recall per the brand agreement. **A recall notification is not discharged by publication in the
portal alone** — it requires acknowledgement, and §4.7 is subject to `BP7`.

### 4.8 Confidentiality

Each party keeps the other's confidential information confidential and uses it only for the
relationship. **The Company's operational, cost and pricing data is confidential to the Company;
the Brand Partner's rate cards, claim rules and technical notices are confidential to the Brand
Partner; and the customer's and technician's personal data is confidential to neither party's
commercial advantage.**

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | Each party is liable for loss it causes by breach of these terms |
| **5.2** | **The Brand Partner is liable for its own use of portal data**, including use outside §4.3, disclosure outside §4.3.3, and any regulatory consequence arising from it |
| **5.3** | The Company is not liable for a claim decision the Brand Partner makes, or for a commercial outcome of the brand agreement |
| **5.4** | **Cap.** Aggregate liability under these portal terms is limited to the reimbursement value of claims in the twelve months preceding the claim, **or to the cap in the brand agreement where it has one, whichever the brand agreement makes applicable** — provisional pending `BP6` |
| **5.5** | Nothing limits liability that cannot lawfully be limited, or a statutory data-protection liability |
| **5.6** | **A commercial claim-valuation dispute is not a portal-terms dispute.** It follows the brand agreement |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| # | Clause |
|---|---|
| **6.1** | The Company discloses personal data to the Brand Partner **only as §4.3 permits**, and only where the disclosure has a recorded lawful basis in the record of processing activities (`BRU-GRC-16`, `FR-GRC-033`) |
| **6.2** | The Brand Partner's role — controller in its own right or the Company's processor — is **`BP2`**. **Until it is settled, the Brand Partner is treated as the Company's processor and equivalent obligations flow down by this clause** (`NFR-098`, `BRU-GRC-18`) |
| **6.3** | The Brand Partner implements technical and organisational measures proportionate to the risk (`NFR-097`), and on request evidences them. The Company's own controls are in `LG-021` |
| **6.4** | **Cross-border transfer.** Where the Brand Partner is outside Bangladesh, disclosure through the portal is a cross-border transfer and requires a **registered basis and safeguards before it occurs** (`BRU-GRC-18`, `BRU-SEC-14`, `NFR-086b`). **`LG-012` §4.5 governs, and no brand may be onboarded to `P08` until its transfer is registered** |
| **6.5** | **Residency-restricted identifiers are never disclosed through `P08`** — National ID, passport number, TIN, biometric templates and recovered customer data (`05-06` §6.4, `BRU-CPM-06`, `BRU-SEC-13`). Where a brand's claim rules ask for one, the answer is no, and §4.4.1 evidence is provided by another means |
| **6.6** | A breach affecting portal data must be reported to the Company **immediately**; the Company holds the notification duty to the **National Data Management Authority** (`NFR-094`) |
| **6.7** | On termination, the Brand Partner returns or destroys portal data except where it must retain it for its own statutory or warranty purposes, and certifies which it has done |
| **6.8** | Data-subject requests received by the Brand Partner about a Company customer are forwarded to the Company within 5 business days and handled under `LG-010` |

> **`CL-02`. §6.4 is a gate, not an aspiration.** `BRU-SEC-14` blocks cross-border transfer of a
> residency-classified field until an Authority notification record and a documented safeguard
> exist. `P08` is a portal for international counterparties. **Onboarding a brand to `P08` without
> its transfer registered is a hard-rule breach at the platform level, and this clause is where
> the commercial side is told so.**

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **Brand agreement ends** | Portal access ends. **In-flight claims are decided or the agreement's run-off applies.** Consignment stock is reconciled and returned |
| **Authorisation lapses** | Work requiring that authorisation cannot be performed (`BRU-PCM-08`), and escalation must already have fired at the declared intervals (`BRU-PCM-07`) |
| **Breach of §4.3 or §6** | Access may be suspended immediately, with notice; escalated as a data incident |
| **Portal User leaves** | Access revoked; decisions already made remain the Brand Partner's |
| **In every case** | §4.8 confidentiality, §6.7 return-or-destroy, and the Company's record retention (`LG-009`) survive. Claim records are retained because they evidence transactions and tax positions |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Operational** | Warranty Operations, then the Finance Director, per `SP-005` |
| **2 — Commercial** | The brand agreement's escalation, if it has one |
| **3 — Data incident** | Handled as an incident, not a dispute, under `LG-021` and `M60` `FR-GRC-036` |
| **4 — Formal** | **The brand agreement's dispute clause governs.** Where it is silent, arbitration in Dhaka under the Arbitration Act 2001, subject to `BP1` |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft for G5 | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to §4.3 permitted use, §6 data protection or §5 liability is MAJOR: notice and re-acceptance |
| **9.2** | These terms are never changed to accommodate a single brand's request. **A brand-specific variation is an annex to that brand agreement**, recorded in `LG-001` against the brand |
| **9.3** | A change to a rate card is the Brand Partner's act, not a change to these terms, and is versioned in the portal (§4.4.4) |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-001_Legal_Content_Register_and_Signoff_Log.md`](LG-001_Legal_Content_Register_and_Signoff_Log.md) | Version and acceptance record per brand entity | `LR-09` |
| [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | **§6.4 gate** | Which transfers are registered; what may never leave |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) · [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | §6 | Check **F6** |
| [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) | §6.3 the Company's own controls; §8 step 3 | Supplier-security and incident policy |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-033_Warranty_Claim_Evidence_Pack.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-033_Warranty_Claim_Evidence_Pack.md) | **What is actually disclosed under §4.3** | Pack contents versus permitted use |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-032_Warranty_Certificate_and_Extension_Document.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-032_Warranty_Certificate_and_Extension_Document.md) | The customer-facing warranty | `LG-013` governs its terms |
| [`../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) | The brand population and their agreements (`O-02`, `O-03`) | Brand identity and authorisation status |
| [`../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Certification status disclosed under §4.3 (`BP3`) | Which certifications exist |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md) | Operates §4.4 | Submission windows, rejection handling |
| `HC-010` Help Set `P08` · `EO-*` brand onboarding | Explain these terms | No help may state a permitted use §4.3 does not |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **Disclosed data enumerated item by item with its permitted use** (§4.3), rather than described generically (`CL-01`)
- [x] Brand scoping stated as platform-enforced, not undertaking-based (`EA-05`, `BRU-WTY-08`)
- [x] **Cross-border transfer stated as a hard gate before onboarding** (§6.4, `CL-02`)
- [x] Residency-restricted identifiers explicitly excluded from disclosure (§6.5)
- [x] Audit evidence release tied to `BRU-QMS-15` approval and logging
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] **`BP1`–`BP7` answered at G5** — outstanding, blocks `Approved`
- [ ] **Executed brand agreements reviewed against these terms** — outstanding, `O-02`
- [ ] **Per-brand claim submission windows registered** — outstanding, `O-04`
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
