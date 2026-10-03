---
id: LG-007
title: Referral and Alliance Partner Agreement
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance
author: Legal & Compliance with Commercial and Partner Operations
reviewers: [Legal Counsel, CCO, CFO delegate, Chief Data Officer, Brand lead, Marketing Head]
approver: Legal Counsel with CCO
content_class: B
purpose: >
  The agreement governing referral partners, alliance partners and corporate resellers using P12 —
  what counts as a referral, how attribution is determined and when it expires, commission and
  settlement, what the partner may and may not say about 1000FiX, and how the relationship ends
  with commission settled. Attribution disputes are the normal failure mode of referral programmes,
  and the rules have to pre-date the first referral because attribution is written at lead creation
  and is immutable thereafter.
traces_to: [P12, M40, M10, M11, M12, M14, M20, M53, LG-001, LG-004, LG-006, LG-008, LG-009, LG-023, DT-040, SP-004, EA-01, EA-02, EA-08, EA-09, BRU-PCM-01, BRU-PCM-02, BRU-PCM-03, BRU-PCM-04, BRU-PCM-05, BRU-PCM-06, BRU-PCM-09, BRU-PCM-10, BRU-PCM-11, BRU-PCM-12, BRU-PCM-13, BRU-PCM-14, BRU-PCM-15, BRU-PCM-16, BRU-PCM-17, BRU-PCM-19, NFR-098]
priority: P2
wave: W7
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 P12 capability set — onboarding with agreement signature, referral links and codes with lead tracking to conversion, benefit schedule, commission and statements, co-marketing with approved materials, reseller stock allocation and settlement, performance and ranking; KPIs including partner portal adoption above 75%
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40 §9 BRU-PCM-01 … BRU-PCM-20 — agreement execution gating, sellers excluded, rate ownership split across M11 and M53, attribution immutability at lead creation, attribution window expiry to no partner, recorded customer consent before lead creation, deal registration conflict check, channel precedence, MDF approval separation, programme versioning, one-hour access revocation, partner data scoping, commission settled before exit, franchise territory and royalty rules
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §8 EA-01, EA-02, EA-08, EA-09 external party access rules
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md §2.1 T-A11 pricing and commission escalation, T-A13 comparative claims, T-A19 use of another organisation's brand
    verified: 2026-08-18
    class: P1
  - source: Personal Data Protection Act 2026 — consent as the basis for a third party submitting an individual's contact details as a lead. Instrument-level citation; clause-level content unverified in this file, pending G5
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-007 — Referral and Alliance Partner Agreement

| Item | Value |
|---|---|
| Document class | **Agreement** — bilateral, with three variants (referral, alliance, reseller) |
| Counterparty | A referral partner, alliance partner or corporate reseller approved for `P12` |
| Governing law | **Bangladesh** |
| Effective date | On execution — *pending approval* |
| Acceptance capture method | **`AC-2` e-signature at onboarding.** `BRU-PCM-01` makes execution the gate: no executed agreement, no transacting |
| Version accepted by users | Recorded in `LG-001`. **`BRU-PCM-12`: a partner is bound to the programme version in force at their agreement date** |
| External counsel review | **Required** — the §4.2 attribution regime and the §4.6 consent position |
| Bengali version | **Not required** (`CG-010` §3.2 — commercial counterparties contracting in English) |

> ⚠ **Class B. One clause carries most of the disputes this document will ever see.**
>
> `BRU-PCM-04`: *"Attribution is written at lead creation and is immutable through to revenue."*
> `BRU-PCM-05`: *"A lead converting outside its attribution window attributes to no partner."*
>
> **That is a design decision with commercial consequences a partner will contest.** A referral
> made in month one that converts in month eight pays nobody. §4.2 states that plainly, up front,
> because the alternative is stating it for the first time in a commission dispute.
>
> **Conformance note.** All ten template sections retained in order; gate questions and open items
> are §1.2 and §1.3 (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with Commercial | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — CCO with Partner Operations | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — Legal Counsel with CCO | *pending* | | |

### 1.2 Questions for Legal Counsel (G5)

| # | Question | Why it matters |
|---|---|---|
| **PA1** | Is a **fixed attribution window with no discretion** (`BRU-PCM-05`) enforceable, and does it need to be disclosed in a particular way to be relied on? | It is the single most likely dispute, and the answer determines whether §4.2.5 needs a hardship route |
| **PA2** | **Who is the controller** when a partner submits an individual's contact details as a lead? `BRU-PCM-06` requires recorded customer consent before the record is created — **whose consent record is it?** | If the partner is the controller at collection, the Company is receiving personal data on the partner's basis and must be able to rely on it |
| **PA3** | Is the §4.6.3 warranty from the partner — that it obtained valid consent — sufficient protection, or must the Company independently verify? | Independent verification of every lead's consent would make the referral model unworkable; no verification leaves the Company exposed |
| **PA4** | Is commission a **fee for a service** the partner supplies, and what is its VAT treatment and withholding position? | `T-A11` escalation; `BRU-TAX-07` withholding applies to applicable payments |
| **PA5** | Is a **franchise territory exclusivity** (`BRU-PCM-16`) enforceable as drafted in §4.9, and does the franchise variant need a separate instrument? | Franchise is regulated differently from referral in most systems; `M40` covers both |
| **PA6** | What limits apply to a partner's use of the 1000FiX name and marks (§4.7), and is the approval mechanism sufficient? | `T-A19`; a partner's unapproved claim becomes the Company's claim |
| **PA7** | May the Company **withhold commission** pending investigation of a suspected fraudulent or incentivised lead, and for how long? | §4.5.6 assumes yes |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | `PA1`–`PA7` unanswered | **Yes — blocks `Approved`** | Legal Counsel |
| **O-02** | **The attribution window length is not defined anywhere.** `BRU-PCM-05` operates on "its attribution window"; no register holds the value per programme | **Yes — blocks §4.2** | CCO |
| **O-03** | **Commission rates and the benefit schedule are held in `M11` and are not published.** §4.5 cannot state a rate; it states the mechanism | **Yes — blocks §4.5** | CCO with CFO |
| **O-04** | The **deal-registration protection period** (`BRU-PCM-09`) is undefined | Yes — blocks §4.8 | CCO |
| **O-05** | **Channel precedence rules are declared to exist (`BRU-PCM-10`) but are not written.** A partner referring a lead that the Company's own sales team already holds needs to know the outcome before it happens | **Yes — blocks §4.8.4** | CCO |
| **O-06** | `LG-004` and this file are both `W7`, and `BRU-PCM-02` separates sellers from partners. **A person could be both a marketplace seller and a referral partner**; no document says how the two agreements interact for that person | No | Legal Counsel |
| **O-07** | The reseller variant allocates refurbished stock (`M14`). **Consumer-protection responsibility for a refurbished device sold by a reseller is unallocated** | Yes — blocks the reseller variant | Legal Counsel with CCO |

---

## 2. Scope and Parties

| Party | Identity |
|---|---|
| **The Company** | 1000FiX Services Limited |
| **The Partner** | A referral partner, alliance partner or corporate reseller with an executed agreement and `P12` access |

**Three variants, one agreement:**

| Variant | What the Partner does | Additional clauses |
|---|---|---|
| **Referral** | Introduces potential customers by link, code or direct lead submission | §4.2–§4.6 |
| **Alliance** | Offers Company services as a benefit to its own members or customers | §4.2–§4.7, plus §4.7.5 benefit-scheme terms |
| **Reseller** | Takes allocation of refurbished stock and sells it on | §4.2–§4.7, plus §4.9 — **subject to `O-07`** |

| # | Clause |
|---|---|
| **2.1** | The Partner is an **independent contractor**. It is not the Company's agent, employee, joint venturer or franchisee, and has **no authority to bind the Company** |
| **2.2** | **A marketplace seller is not a Partner** and is never managed under this agreement (`BRU-PCM-02`). A person who is both holds two agreements — `O-06` |
| **2.3** | The Partner cannot transact until this agreement is executed and onboarding is complete (`BRU-PCM-01`) |
| **2.4** | Programme terms — rates, benefits, tiers — are **versioned, and the Partner is bound to the version in force at its agreement date** until it accepts a later one (`BRU-PCM-12`) |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Lead** | A potential customer the Partner introduces, recorded in the Company's system at creation |
| **Attribution** | The record of which Partner introduced a Lead. **Written at Lead creation and immutable through to revenue** (`BRU-PCM-04`) |
| **Attribution window** | The period from Lead creation within which a conversion attributes to the Partner. **A conversion outside it attributes to no Partner** (`BRU-PCM-05`) — `O-02` |
| **Conversion** | The Lead becoming a paying customer, on the definition in the programme terms |
| **Commission** | The amount payable on a qualifying conversion. **Programmes are defined in `M40`; rates are held in `M11`; computation and payment are in `M53`** (`BRU-PCM-03`) |
| **Deal registration** | Registration of a named opportunity, granted a protection period **only after a conflict check** (`BRU-PCM-09`) — `O-04` |
| **MDF** | Market development funds allocated for co-marketing. **Claims require evidence and approval by someone other than the allocator** (`BRU-PCM-11`) |
| **Approved materials** | Marketing assets the Company has published for Partner use in `P12` |
| **Governing text** | This English text |

---

## 4. Terms

### 4.1 Access and onboarding

| # | Clause |
|---|---|
| **4.1.1** | The Partner applies, submits documents, signs this agreement and is approved before any Lead is accepted (`BRU-PCM-01`) |
| **4.1.2** | Access is by named individual. **A Partner sees only its own records — never another Partner's, and never the Company's cost or margin** (`BRU-PCM-14`, `EA-01`, `EA-02`) |
| **4.1.3** | Sessions time out after 30 minutes (`EA-08`); MFA is mandatory for any action with financial consequence (`EA-09`) |
| **4.1.4** | **Portal access is revoked within one hour of exit, suspension or agreement expiry** (`BRU-PCM-13`) |

### 4.2 Attribution — the operative clause

| # | Clause |
|---|---|
| **4.2.1** | A Lead is attributed to the Partner whose link, code or submission created it. **Attribution is written at Lead creation and cannot be changed afterwards** (`BRU-PCM-04`) |
| **4.2.2** | Where a Lead already exists in the Company's records, **the existing record governs** and a later submission does not re-attribute it |
| **4.2.3** | Where two Partners introduce the same person, **the first Lead creation attributes**; the second is recorded and does not attribute |
| **4.2.4** | **A Lead that converts after its attribution window has expired attributes to no Partner and earns no commission** (`BRU-PCM-05`) |
| **4.2.5** | §4.2.4 has no discretionary exception. Where a Partner believes the outcome is unjust, the route is §8 escalation, not re-attribution — **subject to `PA1`** |
| **4.2.6** | The Partner can see the status of every Lead it created, including expiry, in `P12`. **The Partner is not told after the fact that a window closed; it can see the window running** |

> **`CL-01`. §4.2.1 and §4.2.4 together are why this document is `P2` and still worth writing
> carefully.** An immutable attribution record is what makes commission computable without
> argument. The cost of that certainty is that some genuine referrals earn nothing, and a partner
> who discovers that in month eight will not accept a system rule as an answer. **The rule is
> therefore stated as a term, visibly, before the first referral** — which is exactly the
> justification the register gives this file.

### 4.3 What the Partner may and may not do

| # | Clause |
|---|---|
| **4.3.1** | The Partner may promote Company services to its own audience using **approved materials** (§4.7) |
| **4.3.2** | The Partner must **not** make a claim about the Company's services, pricing, warranty, timescale or capability beyond the approved materials. **A comparative or superlative claim is prohibited unless the Company has published it** (`T-A13`) |
| **4.3.3** | The Partner must not represent itself as the Company, as an authorised service centre, or as able to accept a booking on the Company's behalf |
| **4.3.4** | The Partner must not bid on the Company's brand terms in paid search, or register a domain or account name that suggests it is the Company, without written approval |
| **4.3.5** | The Partner must not incentivise a person to become a Lead in a way that produces a Lead with no genuine interest |
| **4.3.6** | The Partner must not submit a Lead **without the individual's consent** (§4.6) |

### 4.4 Benefit schemes (alliance variant)

Where the Partner offers Company services as a member benefit, the benefit is applied by the
Company's pricing engine and **is never configured as an ad-hoc discount** (`BRU-PCM-19`). The
benefit schedule is published in `P12`; a change to it is a change to programme terms under §9.

### 4.5 Commission and settlement — **partly pending `O-03`**

| # | Clause |
|---|---|
| **4.5.1** | Commission is earned on a qualifying conversion, at the rate in the programme version binding on the Partner (`BRU-PCM-12`) |
| **4.5.2** | **Programme terms are defined in `M40`; rates are held in `M11`; commission is computed and paid by `M53`** (`BRU-PCM-03`). The Partner's statement is `DT-040` |
| **4.5.3** | **Franchise royalties, where applicable, are computed from Company-recorded revenue, never from the Partner's self-declaration** (`BRU-PCM-17`) |
| **4.5.4** | The Partner is responsible for its own tax on commission. Where the Company must withhold, it withholds at the determined rate and issues a certificate (`BRU-TAX-07`, `BRU-TAX-10`) — **subject to `PA4`** |
| **4.5.5** | **Partner commission accuracy is a stated Company target of 100%** (`P12` KPI). An error the Partner identifies is corrected, with the correction shown on the next statement |
| **4.5.6** | The Company may withhold commission on a Lead under investigation for §4.3.5 or fraud, **with notice of the investigation and its expected duration** — subject to `PA7` |
| **4.5.7** | **MDF claims require evidence and approval by someone other than the allocator** (`BRU-PCM-11`) |

### 4.6 Consent and personal data in a Lead

> **`CL-02`. This is the clause that makes the referral model lawful or unlawful.**
> `BRU-PCM-06`: *"A partner-submitted lead requires recorded customer consent before the record is
> created."* The rule sits in the module register with **Legal / CTO** as its owner, which is the
> repository's own signal that it is a legal question and not a build detail.

| # | Clause |
|---|---|
| **4.6.1** | The Partner must obtain the individual's **clear, explicit, specific and freely given consent** to their details being passed to the Company for the purpose of being contacted about its services (`NFR-091`) |
| **4.6.2** | **The Partner records that consent, including what the individual was told and when, and produces it on request.** A Lead without a recorded consent is not submitted |
| **4.6.3** | The Partner **warrants** that consent was obtained as §4.6.1 requires, and indemnifies the Company for a breach of that warranty (§5.4) — subject to `PA3` |
| **4.6.4** | The Company records the Lead's lawful basis before processing begins (`BRU-CPM-07`, `BRU-GRC-16`) and presents its own notice to the individual at first contact (`LG-008`) |
| **4.6.5** | The individual may withdraw consent at any time, directly with the Company, and withdrawal takes effect immediately across every channel (`BRU-CPM-09`). **Withdrawal does not remove an attribution already written** |
| **4.6.6** | The Partner must not retain, reuse or transfer the individual's details for its own purposes beyond what its own consent basis permits, and must not scrape or purchase lists for Lead submission |
| **4.6.7** | The controller position between the parties is **`PA2`**. Until settled, the Partner is treated as an independent controller at collection and as the Company's processor for nothing — **the Company relies on §4.6.3, which is why `PA3` matters** |

### 4.7 Brand, marks and co-marketing

| # | Clause |
|---|---|
| **4.7.1** | The Company grants a limited, revocable, non-exclusive, non-transferable licence to use its name and marks **solely as the approved materials provide** |
| **4.7.2** | Any use outside the approved materials requires prior written approval from the Brand lead with Legal (`T-A19`) |
| **4.7.3** | The Partner acquires no right in the Company's marks and must stop using them on termination |
| **4.7.4** | A co-branded campaign requires approval, and the Company may require correction or withdrawal of any material that misstates its services |
| **4.7.5** | The Partner grants the Company a reciprocal, equally limited licence to name it as a partner, where the Partner agrees |

### 4.8 Conflicts, deal registration and channel precedence — **pending `O-04`, `O-05`**

| # | Clause |
|---|---|
| **4.8.1** | A **deal registration** may be granted a protection period **only after a conflict check. Conflicts are decided, never auto-approved** (`BRU-PCM-09`) |
| **4.8.2** | The protection period and its effect are stated in the programme terms — `O-04` |
| **4.8.3** | Where the Company's own team, another Partner or the marketplace is already engaged with the same opportunity, the **channel precedence rules** determine the outcome (`BRU-PCM-10`) |
| **4.8.4** | **Channel precedence rules are declared and applied consistently; an ad-hoc exception requires CCO approval** (`BRU-PCM-10`) — `O-05` |
| **4.8.5** | The Partner is told the outcome of a conflict decision and its reason |

### 4.9 Reseller and franchise terms — **pending `O-07`, `PA5`**

| # | Clause |
|---|---|
| **4.9.1** | Stock allocation, pricing, order and settlement terms for refurbished devices are as published in `P12` and as `M14` grades them |
| **4.9.2** | **Refurbishment grading is the Company's statement of condition** (`DT-036`). The Partner must not represent a grade the Company did not assign |
| **4.9.3** | **Consumer-protection responsibility for a refurbished device sold on by the Partner to a consumer is `O-07`** and is not resolved by this draft |
| **4.9.4** | A franchise territory is exclusive as declared; **cross-territory activity requires documented agreement** (`BRU-PCM-16`) — subject to `PA5` |
| **4.9.5** | A relationship health score must decompose into its named contributing factors (`BRU-PCM-18`); the Partner may see that decomposition |

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | Each party is liable for loss it causes by breach of this agreement |
| **5.2** | The Company is **not** liable for: the number or value of Leads that convert; an attribution outcome properly determined under §4.2; a conflict decision under §4.8; loss of expected commission; or the Partner's own marketing costs |
| **5.3** | The Partner is liable for claims arising from its statements about the Company (§4.3.2), its use of the marks (§4.7), and its Lead-collection practices (§4.6) |
| **5.4** | **The Partner indemnifies the Company** against claims, penalties and regulatory action arising from a breach of §4.6.1, §4.6.2 or §4.6.6 — **this is the Company's principal protection under the referral model** and is provisional pending `PA3` |
| **5.5** | **Cap.** The Company's aggregate liability is limited to the commission paid to the Partner in the twelve months preceding the claim — provisional pending G5 |
| **5.6** | Nothing limits liability that cannot lawfully be limited, or a statutory data-protection liability |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| # | Clause |
|---|---|
| **6.1** | The Company processes the Partner's own business-contact, banking, performance and commission data as a controller, per `LG-008` |
| **6.2** | Lead personal data is governed by §4.6, and the controller position is `PA2` |
| **6.3** | Equivalent obligations flow down to any processor the Partner uses for Lead collection (`NFR-098`) |
| **6.4** | The Partner notifies the Company of a suspected breach **immediately**; the Company holds the duty to notify the **National Data Management Authority** (`NFR-094`) |
| **6.5** | **Residency-restricted identifiers are never collected in a Lead** — no National ID, no passport number, no TIN. A Lead is a name and a contact point, and asking for more is a breach of §4.6.6 |
| **6.6** | Where the Partner is outside Bangladesh, any transfer to it requires a **registered basis and safeguards before it occurs** (`BRU-SEC-14`), per `LG-012` §4.5 |
| **6.7** | Attribution, commission and statement records are retained per `LG-009` — **not less than the tax retention on the payments they evidence** |
| **6.8** | A Lead that never converts is retained only for the attribution window plus the period `LG-009` states, and is then deleted. **An unconverted Lead is not a marketing list** |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **Either party terminates on notice** | No new Leads. **Leads already created keep their attribution and their window** (`BRU-PCM-04`) |
| **Agreement expires** | Portal access revoked within one hour (`BRU-PCM-13`) |
| **Breach of §4.3, §4.6 or §4.7** | Immediate suspension, then termination unless remedied; commission on affected Leads withheld pending investigation (§4.5.6) |
| **Exit in the ordinary course** | **Outstanding commission is settled before the relationship reaches Exited** (`BRU-PCM-15`) |
| **In every case** | Mark use ceases (§4.7.3); §4.6 obligations and §5.4 indemnity survive; retention under `LG-009` survives; **conversions after termination within a live window are paid** unless termination was for a §4.6 or fraud breach |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Attribution or commission query** | Partner Operations, with the `P12` record as the evidence. **The record governs; recollection does not** |
| **2 — Escalation** | The CCO, per `SP-004` and `SP-005` |
| **3 — Mediation** | Good-faith discussion within 15 business days of written notice |
| **4 — Arbitration** | Arbitration in Dhaka under the Arbitration Act 2001, one arbitrator |
| **5 — Courts** | The courts of Dhaka, Bangladesh |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft for G5 | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to commission, the attribution window, the benefit schedule or §4.6 is MAJOR: notice, then re-acceptance |
| **9.2** | **Programme terms are versioned and a Partner remains bound to its own version** until it accepts a later one (`BRU-PCM-12`). **A rate reduction cannot be applied to an existing Partner without acceptance** |
| **9.3** | **A change to the attribution window does not shorten a window already running.** Leads created under the old window keep it |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-001_Legal_Content_Register_and_Signoff_Log.md`](LG-001_Legal_Content_Register_and_Signoff_Log.md) | Version and acceptance record | `AC-2` at onboarding |
| [`LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md`](LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md) | **Sellers are not Partners** (`BRU-PCM-02`); `O-06` where a person is both | The boundary between the two |
| [`LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md`](LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md) | §5 Code standards apply where the Partner also supplies | Ethical standards |
| [`LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md`](LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md) | Commission is a payment to an intermediary; **the anti-bribery position matters here** | Gift, hospitality and intermediary rules |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) · [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) · [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | §4.6 and §6 | Check **F6** |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-040_Partner_Commission_Statement.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-040_Partner_Commission_Statement.md) | Renders §4.5 | Commission basis and corrections |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-036_Refurbishment_Grading_and_Certification_Record.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-036_Refurbishment_Grading_and_Certification_Record.md) | §4.9.2 | What a grade means |
| [`../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) | MDF and exception approvals (§4.5.7, §4.8.4) | Approval authorities |
| `HC-014` Help Set `P12` · `EO-*` partner onboarding · `MM-*` approved materials | Explain and supply §4.7 materials | No material may make a claim §4.3.2 prohibits |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **Attribution stated as an immutable term with its harsh consequence disclosed up front** (§4.2, `CL-01`)
- [x] All 20 `BRU-PCM-*` rules reflected, including the seller/partner boundary and one-hour revocation
- [x] **Lead consent stated as the Partner's obligation with a warranty and indemnity** (§4.6, `CL-02`)
- [x] Three variants distinguished rather than merged into a generic partner formula
- [x] Brand and comparative-claim restrictions stated (`T-A13`, `T-A19`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] **`PA1`–`PA7` answered at G5** — outstanding, blocks `Approved`
- [ ] **Attribution window, commission rates, deal-registration period and channel precedence defined** — outstanding, `O-02`…`O-05`; four terms currently reference values that do not exist
- [ ] **Reseller consumer-protection responsibility allocated** — outstanding, `O-07`
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
