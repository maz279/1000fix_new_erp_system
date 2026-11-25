---
id: CM-015
title: Vendor and Seller Transition Pack
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Procurement with Marketplace Operations
author: Change Lead with Procurement and Marketplace Operations
reviewers: [CCO, CFO, Procurement Manager, Marketplace Operations Officer, Logistics Coordinator, Legal & Compliance, Localisation Lead, Content Design Lead, Support Lead, Programme Content Lead]
approver: Content Design Lead, with the CCO approving commercial statements and Legal approving any term change
content_class: D
purpose: >
  Moves four external supply-side populations — parts vendors, courier partners, marketplace
  sellers and recycling partners — from email, phone and paper onto portal-based interaction,
  with a transition sequence per counterparty rather than a broadcast. Vendor portal adoption
  targets above 85% require active transition, not passive availability, and a supplier who
  discovers the change when their invoice is rejected becomes a payment dispute rather than a
  portal user.
traces_to: [P05, P07, P09, EO-001, EO-005, EO-009, CM-001, CM-002, CM-003, CM-016, NT-011, NT-012, LG-004, LG-006, LG-007, MD-042, 04-00, 06-01, M42, M12, M16]
priority: P2
wave: W3
bilingual: yes
bn_counterpart: CM-015_Vendor_and_Seller_Transition_Pack_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P05 — vendor portal capability set and KPIs: POs acknowledged through the portal above 90%, invoices above 85%, vendor phone and email queries down 60%, RFQ response above 75%
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P07 — marketplace seller portal, governance requirements and KPIs including onboarding completion above 60% of started registrations
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §1.2 RSK-010 — marketplace sellers fail to adopt; external audience with low switching cost, mitigated by simple onboarding, fast transparent payouts and clear scoring
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §3 Wave 3 and Wave 7 — vendor portal and rider app at W3; marketplace seller and partner portals at W7
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §6 D-03, D-09, D-10 and §3.2 DEP-29 — marketplace commercial model, guarantee position, seller insurance and liability caps, and the external tax and legal opinion, all open
    verified: 2026-08-20
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.3 — vendors and brand partners are English-audience; marketplace sellers are bilingual
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-015 — Vendor and Seller Transition Pack

> **Scope note.** This file owns **the transition of existing supply-side counterparties onto the
> portals**. It does not own onboarding a *new* one — that is Category 18 `EO`
> ([`EO-001`](../18_Ecosystem_Onboarding_Content/EO-001_Marketplace_Seller_Onboarding_Kit.md) sellers,
> [`EO-005`](../18_Ecosystem_Onboarding_Content/EO-005_Vendor_and_Supplier_Onboarding_Pack.md) vendors,
> [`EO-009`](../18_Ecosystem_Onboarding_Content/EO-009_Referral_and_Alliance_Partner_Kit.md) referral partners), all of which are
> written and at `Draft`. The distinction is real: an existing vendor already has a relationship, a
> payment history and a way of working; a new one has none of those and needs the opposite content.
> **Neither side's file yet states which one applies to a counterparty that pre-exists** (`O-01`).
>
> **Population note.** Four populations with three portals, two waves and different commercial
> exposures. §4.1 separates them, because a message written for all four is written for none.

---

## 1. Purpose

The register's justification is exact: *"Vendor portal adoption targets above 85% require active
transition, not passive availability."*

A vendor's incentive to change is weaker than the company's. They are paid either way; the portal
is the company's efficiency, not theirs, until they can see their own payment schedule in it. The
transition therefore has to be sold, per counterparty, by the person who already holds the
relationship.

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| Broadcast rather than per-counterparty transition | The large vendors move, the long tail does not, and the process runs twice for two years |
| No transition owner | Procurement assumes Marketing did it; nobody did |
| Portal announced before the counterparty is set up | A vendor logs in, cannot find their POs and does not return |
| No banking or document re-verification | Payment fails at the first cycle and the portal is blamed |
| Sellers transitioned with vendor content | 500–2,000 individual engineers receive procurement language they cannot act on |
| Term changes implied but not made | A commercial dispute created by a change communication |
| Bengali omitted for sellers | `RSK-010` — an external audience with low switching cost, addressed in a language many do not read |
| Cutover overlaps with a payment run | The first portal experience is a missed payment |

---

## 2. Scope

**In scope:** the four supply-side populations and their separation; the transition sequence per
counterparty; the pre-conditions before a counterparty is invited; the assets per population;
banking, document and identity re-verification communication; the dual-running window and its
end; the commercial-boundary rules; escalation; and rules `VT-01`…`VT-17`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Onboarding a **new** vendor, seller or partner | [`EO-001`](../18_Ecosystem_Onboarding_Content/EO-001_Marketplace_Seller_Onboarding_Kit.md), [`EO-005`](../18_Ecosystem_Onboarding_Content/EO-005_Vendor_and_Supplier_Onboarding_Pack.md), [`EO-009`](../18_Ecosystem_Onboarding_Content/EO-009_Referral_and_Alliance_Partner_Kit.md) |
| Seller standards, scoring and sanctions | [`EO-002`](../18_Ecosystem_Onboarding_Content/EO-002_Seller_Standards_Scoring_and_Sanctions_Handbook.md) |
| Supplier scorecard explanation | [`EO-006`](../18_Ecosystem_Onboarding_Content/EO-006_Supplier_Performance_Scorecard_Explanation.md) |
| Rate-card and pricing change communication | [`EO-011`](../18_Ecosystem_Onboarding_Content/EO-011_Rate_Card_and_Pricing_Communication_Pack.md) |
| Dispute intake and resolution | [`EO-013`](../18_Ecosystem_Onboarding_Content/EO-013_Ecosystem_Dispute_Resolution_Content.md); `LG-004` |
| Offboarding and exit | [`EO-014`](../18_Ecosystem_Onboarding_Content/EO-014_Ecosystem_Offboarding_and_Exit_Content.md) |
| Vendor, seller and partner agreements and terms | `LG-004` seller, `LG-006` vendor, `LG-007` partner |
| Transactional notifications to vendors and sellers | `NT-011`, `NT-012` |
| Portal UI copy | `UI-015` vendor, `UI-017` seller, `UI-019` rider |
| Commission, payout and settlement mechanics | `M12`, `M20` |
| Corporate client transition | [`CM-014_Corporate_Client_Transition_Pack.md`](CM-014_Corporate_Client_Transition_Pack.md) |
| Brand partner transition | [`EO-003`](../18_Ecosystem_Onboarding_Content/EO-003_Brand_Partner_Onboarding_Pack.md); brands are `P08` at W4 |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Procurement Officers (`R19`)** | Run the vendor transition, counterparty by counterparty |
| **Marketplace Operations (`R24`)** | Run the seller transition in cohorts |
| **Logistics Coordinators (`R15`)** | Transition courier partners onto `P09` and `P05` |
| **Finance (`R26`, `R27`)** | Know when invoice routes change and what the dual-running window is |
| **Change Lead** | Track transition coverage against the adoption targets |
| **Legal** | Confirm that nothing in the transition amends a term |
| **Support Lead** | Anticipate the enquiry load from an external population |

---

## 4. Content

### 4.1 Four populations, not one

**`VT-01`: each population is transitioned separately, on its own reason, by its own owner.**

| # | Population | Count | Portal | Wave | Owner | Their reason to move | Language |
|:--:|---|---|:--:|:--:|---|---|---|
| **V1** | **Parts vendors and suppliers** | 200–500 | `P05` | **W3** | Procurement Officer (`R19`) | *"See your PO status and your payment schedule without phoning."* | **EN** (`CG-010` §3.3) |
| **V2** | **Courier and logistics partners** | 10–40 firms | `P09` + `P05` | **W3** | Logistics Coordinator (`R15`) | *"Manifests, POD and settlement claims in one place."* | **EN + BN** — rider-facing surfaces reach Bengali-first staff |
| **V3** | **Marketplace sellers** | 500–2,000 | `P07` | **W7** | Marketplace Operations (`R24`) | *"Faster payouts and jobs matched to what you do."* | **BN-first** (`CG-010` §3.3) |
| **V4** | **Recycling and disposal partners** | 3–10 | `P05` | **W8** | Quality Manager | *"Batch transfers and certificate upload in one place."* | EN |

> **`VT-02` — V3 is not a transition in the same sense as V1.** Marketplace sellers largely do
> not exist yet as counterparties; W7 stands up the marketplace. Where a seller pre-exists as an
> informal sub-contractor, this file transitions them; where they do not, `EO-001` onboards them.
> **The boundary is whether a commercial relationship already exists.**

### 4.2 Per-counterparty sequence — V1 and V2

**`VT-03`: no counterparty is invited to the portal until their account is set up and populated.**
The first login must show them their own POs, their own invoices and their own payment schedule.
An empty portal is a portal they do not return to.

| # | Step | Owner | Offset | Requires reply |
|:--:|---|---|---|:--:|
| 1 | **Segment the vendor base** by spend, transaction volume and criticality | Procurement | W3 − 12 weeks | — |
| 2 | **Notify the top segment first**, by the relationship owner, by phone then in writing | Procurement Officer | W3 − 10 weeks | **Yes** |
| 3 | **Re-verify banking, tax and document data** with the counterparty | Procurement + Finance | W3 − 8 weeks | **Yes** |
| 4 | Account created and populated with open POs, open invoices and history | Procurement | W3 − 4 weeks | — |
| 5 | **Invitation with a named contact and a walkthrough offer** | Procurement Officer | W3 − 2 weeks | **Yes** |
| 6 | First transaction supported — one PO acknowledged with the officer on the phone | Procurement Officer | W3 | — |
| 7 | **Dual-running window** — email accepted alongside the portal | Procurement | W3 to W3 + 8 weeks | — |
| 8 | **Email route closed** for that counterparty | Procurement Manager | W3 + 8 weeks | **Yes — confirmation** |

> **`VT-04` — step 3 is the step that decides whether the first payment succeeds.** Banking and
> tax data carried across from a legacy system without re-verification produces a failed payment
> in the first cycle, and a failed payment is the only portal experience that vendor will
> remember.

> **`VT-05` — step 6 exists because a first successful transaction predicts adoption better than
> any communication.** One PO acknowledged with help, on the phone, converts more vendors than
> three reminders.

### 4.3 The dual-running window and its end

**`VT-06`: dual running is time-boxed per counterparty and its end is confirmed, not assumed.**

| Element | Rule |
|---|---|
| Length | **8 weeks per counterparty**, from their step 6 |
| What runs | Email and portal both accepted; **the portal is the record** |
| Extension | Once, by exception, with the Procurement Manager's approval and a stated reason |
| **Closure** | The email route is closed **for that counterparty**, confirmed in writing, with the date |
| **The trap** | A dual-running window with no end is a permanent second process. `04-00` §P05 targets 90% PO acknowledgement and 85% portal invoicing; those are not reachable while email works indefinitely |
| Exception population | Counterparties genuinely unable to use a portal — recorded, counted, and given a defined manual route rather than an unmanaged one |

> **`VT-07` — the exception population is counted and published.** An unbounded set of exceptions
> is how a 90% target quietly becomes 60%. Counting them makes the gap a decision rather than a
> drift.

### 4.4 The assets

| # | Asset | Population | Timing | Language |
|:--:|---|---|---|---|
| **A1** | **Relationship-owner call guide** — what to say, what to promise, what not to | V1, V2, V4 | Step 2 | EN |
| **A2** | **Written transition notice** — what changes, when, what is required of them | All | Step 2 | Per population |
| **A3** | **Data re-verification request** — banking, tax, documents, contacts | All | Step 3 | Per population |
| **A4** | **Portal invitation** — named contact, walkthrough offer, first-task guide | All | Step 5 | Per population |
| **A5** | **First-transaction walkthrough** — one PO, one invoice, one claim | All | Step 6 | Per population |
| **A6** | **Dual-running end notice** | All | Step 8 | Per population |
| **A7** | **Seller cohort pack** — registration, verification, first listing, first job, payout | **V3** | W7, per cohort | **BN-first** |
| **A8** | **Rider and courier field notice** — manifest, scanning, POD, cash reconciliation | **V2** | W3 | **BN-first** |

> **`VT-08` — A8 is Bengali-first even though V2's commercial contact is English.** The courier
> firm contracts in English; the rider scanning a consignment at a doorstep does not. A single
> "vendor" population can have two audiences with two language requirements, and `CG-010` §3.3
> resolves it by audience, not by contract.

### 4.5 Commercial boundaries

**`VT-09`: a transition communication never changes a commercial term.** Not payment terms, not
prices, not commission, not SLA, not liability.

| If the change is… | Then |
|---|---|
| Purely operational — the route by which a PO is acknowledged | This file communicates it |
| A change to payment **timing** | **A term change.** Legal and the CFO; `LG-006` amended; communicated as a contract variation |
| A change to commission or fees | **A term change.** `LG-004`; `EO-011` when it exists |
| A new obligation — for example mandatory portal invoicing | **A term change** once the alternative closes (`VT-06` step 8) |
| A change to evidence or documentation required | Check with Legal; frequently a term change |

> **`VT-10` — closing the email route is a term change and is treated as one.** For eight weeks
> it is an operational transition; on the day the alternative closes, the counterparty's method of
> invoicing has been changed by the company, and `LG-006` governs how that is done.

### 4.6 Marketplace sellers — the `RSK-010` case

`RSK-010` rates seller non-adoption Medium probability, High impact, with the mitigation *"simple
onboarding; fast, transparent payouts; clear scoring; seller advisory group."*

| Element | Position |
|---|---|
| **What sellers respond to** | Payout speed and job flow. Nothing else moves an audience with low switching cost |
| **What this file may promise** | Only what `04-00` §P07 and `M20` deliver — wallet, statements, payout schedule, scorecard visibility |
| **What it may not promise** | Job volume, earnings, or a commission rate — **`D-03` is open** and the commercial model is undecided |
| Cohorts | Sellers are transitioned in cohorts sized to onboarding support capacity, not in one wave |
| **Seller advisory group** | Named in the `RSK-010` mitigation; **no such group exists** (`O-04`) |
| Scoring | Explained before it applies, not when it first reduces visibility ([`EO-002`](../18_Ecosystem_Onboarding_Content/EO-002_Seller_Standards_Scoring_and_Sanctions_Handbook.md)) |
| Language | **Bengali-first**; individual engineers, not firms |

> **`VT-11` — no seller communication may state a commission rate, a guarantee position or a
> liability cap until `D-03`, `D-09` and `D-10` are decided.** All three are open, all three are
> `W7 minus 3 months`, and `RSK-022` rates the underlying tax and liability question Critical.

### 4.7 Escalation and support

| Situation | Route | Commitment |
|---|---|---|
| Counterparty cannot complete step 3 re-verification | Procurement Officer → Finance | 5 working days |
| Counterparty declines to move | **Relationship owner, then Procurement Manager** — recorded as an exception, not pursued by broadcast | Per cycle |
| Portal access or technical failure | Support desk, **external-counterparty route** — `OP-001` §4.1 populations 4–10 | `OP-001` §4.7, by severity |
| Payment failure attributed to the transition | **Finance, immediately** — with the manual payment fallback available | Same day |
| Seller disputes a payout or a score | [`EO-013`](../18_Ecosystem_Onboarding_Content/EO-013_Ecosystem_Dispute_Resolution_Content.md); `LG-004` | Per agreement |
| A commercial objection | Relationship owner → CCO | Next cycle |

### 4.8 Measurement

| Measure | Source | Target |
|---|---|---|
| Counterparties transitioned / in scope | Transition register | **100% of the in-scope base** |
| POs acknowledged in portal | `P05` instrumentation | **> 90%** (`04-00` §P05) |
| Invoices submitted in portal | `P05` | **> 85%** |
| RFQ response rate | `P05` | > 75% |
| Vendor phone and email queries | Support | **−60%** |
| **Exception population** | Transition register | **Counted and published** (`VT-07`) |
| Seller onboarding completion | `P07` | **> 60% of started registrations** |
| Seller monthly active | `P07` | > 70% of approved |
| **First-payment failures after transition** | Finance | **Zero tolerance; each investigated** |

### 4.9 Audience · channel · timing · message · call-to-action

| Audience | Channel | Timing | Message | Call to action |
|---|---|---|---|---|
| V1 top-segment vendors | **Phone by the procurement officer, then written** | W3 − 10 weeks | A2 transition notice | **Confirm your contact and nominate a portal user** |
| V1, V2, V4 | Written, EN | W3 − 8 weeks | A3 re-verification request | **Confirm banking, tax and documents** |
| V1, V2, V4 | Written + call | W3 − 2 weeks | A4 invitation with named contact | Log in; book the walkthrough |
| V1 | **Assisted call** | W3 | A5 first transaction | Acknowledge one PO with us on the line |
| V2 riders | **BN field notice + toolbox talk** | W3 | A8 manifest, POD, cash | Complete one manifest with support |
| V1, V2, V4 | Written | W3 + 8 weeks | A6 dual-running ends | **Confirm you are portal-only** |
| V3 sellers | **BN in-app + cohort session** | W7, per cohort | A7 seller pack | Complete verification; take one job |
| Procurement, Marketplace Ops | Transition register | Weekly | Coverage and exceptions | Chase the named counterparty |
| `S02` Steering | `CM-004` Section 5 | Monthly | Coverage vs target; exception count | Authorise or accept the gap |

### 4.10 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `VT-01` | Four populations, transitioned separately, each by its relationship owner | **H** |
| `VT-02` | The boundary with `EO` is whether a commercial relationship already exists | **H** |
| `VT-03` | No counterparty is invited before their account is populated with their own data | **H** |
| `VT-04` | Banking, tax and document data is re-verified with the counterparty before first payment | **H** |
| `VT-05` | Every counterparty's first transaction is assisted | **H** |
| `VT-06` | Dual running is time-boxed at 8 weeks per counterparty and its end is confirmed in writing | **H** |
| `VT-07` | The exception population is counted and published | **H** |
| `VT-08` | Language follows the audience, not the contract; rider-facing content is Bengali-first | **H** |
| `VT-09` | A transition communication never changes a commercial term | **H** |
| `VT-10` | Closing the alternative route is a term change and follows `LG-006` | **H** |
| `VT-11` | No seller communication states commission, guarantee or liability until `D-03`, `D-09`, `D-10` are decided | **H** |
| `VT-12` | Sellers are transitioned in cohorts sized to support capacity | **H** |
| `VT-13` | Scoring is explained before it applies, never when it first bites | **H** |
| `VT-14` | No transition step is scheduled to collide with a payment run | **H** |
| `VT-15` | A counterparty declining to move is recorded as an exception, not pursued by broadcast | **H** |
| `VT-16` | Every promise is limited to delivered `04-00` capability (`NR-08`) | **H** |
| `VT-17` | A first-payment failure after transition is investigated individually | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `04-00` §P05, §P07, §P09 | The capability and the targets |
| `00-04` §1.2 `RSK-010` | The seller adoption risk and its stated mitigations |
| `00-04` §6 `D-03`, `D-09`, `D-10` · §3.2 `DEP-29` | The open marketplace decisions `VT-11` blocks against |
| `LG-004`, `LG-006`, `LG-007` | The agreements a transition must not amend |
| [`EO-001`](../18_Ecosystem_Onboarding_Content/EO-001_Marketplace_Seller_Onboarding_Kit.md) · [`EO-002`](../18_Ecosystem_Onboarding_Content/EO-002_Seller_Standards_Scoring_and_Sanctions_Handbook.md) · [`EO-005`](../18_Ecosystem_Onboarding_Content/EO-005_Vendor_and_Supplier_Onboarding_Pack.md) · [`EO-006`](../18_Ecosystem_Onboarding_Content/EO-006_Supplier_Performance_Scorecard_Explanation.md) · [`EO-011`](../18_Ecosystem_Onboarding_Content/EO-011_Rate_Card_and_Pricing_Communication_Pack.md) · [`EO-013`](../18_Ecosystem_Onboarding_Content/EO-013_Ecosystem_Dispute_Resolution_Content.md) · [`EO-014`](../18_Ecosystem_Onboarding_Content/EO-014_Ecosystem_Offboarding_and_Exit_Content.md) | Onboarding, standards, scorecards, pricing, disputes and exit — **the content a transitioned counterparty is handed over to** |
| `NT-011`, `NT-012` | Transactional messages this pack must not duplicate |
| `M42`, `M16`, `M12`, `M20` | Vendor management, procurement, marketplace, settlement |
| `MD-042` | Vendor and supplier master |
| [`CM-016_Adoption_Campaign_Content.md`](CM-016_Adoption_Campaign_Content.md) | Where the campaign follows the transition |
| [`OP-001`](../17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) | §4.1 enumerates eleven external populations — vendors, sellers, seller technicians and couriers among them — with a support language per population |

| Depended on by |
|---|
| `P05` and `P07` adoption targets · `G7-01` 200+ sellers transacting · vendor payment continuity at W3 · `CM-016` supply-side campaigns · `CI-10` `R38` change statements |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per cohort or segment transitioned**, and at each wave gate |
| Trigger for out-of-cycle review | A term change · a `D-03`/`D-09`/`D-10` decision · a first-payment failure · an exception population above tolerance |
| Owner | Procurement for V1 and V4; Marketplace Operations for V3; Logistics for V2 |
| Change log | `RF-006`; any change touching a commercial statement requires Legal and CCO |
| Enforcement | `VT-01`…`VT-17`; the transition register reconciled weekly; exception count reported monthly |
| Improvement loop | **Adoption per segment against transition method is the finding worth having.** If assisted first transactions (`VT-05`) convert materially better than invitations alone, the method scales to the long tail; if they do not, the assumption behind the whole sequence is wrong |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **`VT-02`'s boundary is stated here and nowhere else.** All seven referenced `EO` files exist at `Draft`, and the rule that separates them from this pack — *whether a commercial relationship already exists* — appears only in this file. `EO-001` and `EO-005` describe registration journeys that a transitioning counterparty must **not** be sent through, and neither says so. A one-sided boundary is not a boundary | Programme Content Lead with Procurement and Marketplace Operations | **W3 minus 2 months** |
| **`O-02`** | **The vendor base has not been segmented and there is no transition register.** §4.2 step 1 and §4.8 both assume one; `MD-042` is the vendor master and no transition state is held anywhere. 200–500 counterparties tracked in a spreadsheet is the practice this programme exists to end | Procurement Manager | **W3 minus 12 weeks** |
| **`O-03`** | **Three marketplace decisions are open and `VT-11` blocks seller communication until they close.** `D-03` principal-vs-agent and commission structure, `D-09` whether 1000FiX guarantees marketplace work, `D-10` seller insurance and liability caps — all `W7 minus 3 months`, all feeding `RSK-022`, rated **Critical**. No seller can be told what they earn or what they are liable for | CEO, CFO and Legal | **W7 minus 3 months** |
| **`O-04`** | **The seller advisory group named in the `RSK-010` mitigation does not exist.** It is the mechanism by which sellers influence the platform they are asked to adopt, and it appears in the risk register as a mitigation and in no plan as an activity | CCO with Marketplace Operations | **W7 minus 6 months** |
| **`O-05`** | **The Bengali counterpart does not exist**, and V3 sellers plus V2 riders are Bengali-first. `RSK-010` describes an audience with low switching cost; addressing them in a second language is not a neutral choice | Localisation Lead | **W3 minus 6 weeks for V2; W7 minus 8 weeks for V3** |
| **`O-06`** | **`OP-001` §4.1 counts vendors at 200–600 and this file at 200–500.** The two enumerations of the same population differ, and `OP-001` declares its own *“the definitive one”*. `OP-001` also registers **seller technicians (1,000–4,000)** as a distinct supported population that this transition pack does not address at all — they are the people who will actually use `P07` on a job | Support Lead with Marketplace Operations | **W3 minus 4 weeks; W7 for seller technicians** |
| **`O-07`** | **The eight-week dual-running window is unpriced.** Running email and portal in parallel for 200–500 counterparties, staggered, means procurement and finance operate two intake processes for several months. It is the same unresourced-parallel-run problem `DM-014` `O-03` records internally | Procurement Manager with CFO | **W3 minus 2 months** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] **Four supply-side populations separated** with their own portal, wave, owner, reason and language
- [x] Boundary with Category 18 `EO` stated as existing-relationship versus new-relationship
- [x] Eight-step per-counterparty sequence with the reply-requiring steps identified
- [x] **Account populated before invitation, and first transaction assisted**
- [x] Dual-running time-boxed, its closure confirmed, and the exception population counted and published
- [x] **Commercial boundary stated**, including the finding that closing the email route is itself a term change
- [x] Seller case tied to `RSK-010`, with the three open decisions blocking any commercial statement
- [x] Language resolved by audience rather than by contract, making rider content Bengali-first
- [x] Nine measures including zero-tolerance first-payment failure
- [x] Seventeen governing rules with enforcement classes
- [x] All internal links resolve
- [ ] **`O-01` the `EO` boundary is stated on one side only**
- [ ] **`O-02` no vendor segmentation and no transition register**
- [ ] **`O-03` three marketplace decisions open; seller communication blocked**
- [ ] **`O-05` Bengali counterpart not written**
- [ ] **`O-06` population counts diverge from `OP-001` §4.1; seller technicians unaddressed**
- [ ] **`O-07` dual-running window unpriced**
- [ ] Named approver recorded — **pending Content Design Lead with the CCO and Legal**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
