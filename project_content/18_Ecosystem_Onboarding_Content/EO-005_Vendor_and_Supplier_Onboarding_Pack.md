---
id: EO-005
title: Vendor and Supplier Onboarding Pack
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Procurement
author: Procurement Manager with Finance and Content Design
reviewers: [Supply Chain Director, Chief Financial Officer, Quality Manager, Legal Counsel, Finance Manager, Master Data Owner, Content Design Lead]
approver: Content Design Lead with Procurement Manager
content_class: D
purpose: >
  The pack issued to a prospective or existing supplier to get them registered, qualified,
  activated and transacting through the P05 portal: what documents are required, what
  qualification actually assesses, what activation per category means, and how RFQ, purchase
  order, delivery, invoice and payment work once they are on it. The portal targets more than 90%
  of purchase orders acknowledged and more than 85% of invoices submitted through it, against a
  base of suppliers who currently transact by phone and email. A supplier who is not actively
  onboarded stays on email, and a supplier on email cannot be blocked by the activation gate that
  every purchase order depends on.
traces_to: [P05, M42, M16, M15, M41, M20, M52, M03, M18, M24, M29, M51, 04-00 P05, 05-04 §8 EA-01, EA-02, EA-06, FR-SRM2-001, FR-SRM2-002, FR-SRM2-004, FR-SRM2-005, FR-SRM2-007, FR-SRM2-008, FR-SRM2-009, FR-SRM2-010, FR-SRM2-011, FR-SRM2-013, FR-SRM2-014, FR-SRM2-015, FR-SRM2-016, FR-SRM2-017, FR-SRM2-018, FR-SRM2-019, FR-SRM2-020, FR-SRM2-021, FR-SRM2-022, FR-SRM2-023, FR-SRM2-026, BRU-SRM2-01, BRU-SRM2-02, BRU-SRM2-03, BRU-SRM2-04, BRU-SRM2-05, BRU-SRM2-06, BRU-SRM2-07, BRU-SRM2-12, BRU-SRM2-14, BRU-SRM2-16, BRU-SRM2-17, BRU-SRM2-20, KPI-048, KPI-049, G3-06, MD-016, MD-037, MD-038, MD-022, MD-047, LG-006, LG-023, SP-017, SP-018, SP-026, DT-022, DT-023, DT-024, DT-025, UI-015, UI-040, HC-007, NT-011, EO-006, EO-011, EO-014, CM-015, AP-005, AP-011]
priority: P2
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P05 capability set (onboarding, sourcing, orders, delivery, invoicing, returns, performance, logistics partners, recycling partners); users "parts vendors, courier partners, sub-contractors, recycling partners", 200–500; KPIs "POs acknowledged through the portal > 90%", "invoices submitted through the portal > 85%", "vendor phone/email queries −60%", "RFQ response rate > 75%"; Wave W3
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M42_Supplier_Relationship_and_Performance.md §5.1–§5.4 FR-SRM2-001…026 including the FR-SRM2-010 activation gate exposed as a synchronous decision API M16 must call before any purchase order; §9 BRU-SRM2-01…20 including BRU-SRM2-02 fail-closed, BRU-SRM2-03 qualification per category and per legal entity, BRU-SRM2-07 bank-detail second-person approval, BRU-SRM2-16 permanent blocking authority
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md §2 record structure — vendor_category enum, trade_licence_no, bin, tin, is_vat_registered, vds_applicable, vds_rate_code, bank_account_name, bank_routing_no, payment_term_code, approval_state gating payability, portal_enabled; §4 VND-01…VND-07
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md §wave allocation — W3 Months 9–13, W4 Months 14–18 with M42 listed at W4
    verified: 2026-08-18
    class: P1
  - source: National Board of Revenue (Bangladesh) — the 13-digit e-BIN issued through the VAT online portal is the only valid Business Identification Number format; a valid TIN is a precondition of BIN application; VAT withholding entities include limited companies and entities exceeding BDT 100 million turnover, which must deduct VAT at source when paying vendors
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# Vendor and Supplier Onboarding Pack

| Item | Value |
|---|---|
| Audience | Parts vendors, service providers, courier and logistics partners, sub-contractors, recycling partners |
| Population | **200–500** portal users (`04-00` P05) |
| Portal | `P05` Vendor & Supplier Portal |
| Language | **English only** (`CG-010` §3.2 — "vendors and suppliers: No") |
| Issued by | Procurement, at first contact and at re-qualification |
| Wave | W3 · Months 9–13 (`06-01` §3) — **but see `O-01`; `M42` is W4** |
| KPIs served | `KPI-048` on-time delivery · `KPI-049` three-way match exceptions · the four `04-00` P05 portal targets |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The three `EO` additions appear as §4.1 (**journey** — registration to
> activation to first order), §4.3 (**checklist** — the document set by supplier class) and §4.8
> (**first 90 days**). Template 15 `TPL_Onboarding_Kit.md` does not exist.

---

## 1. Purpose

`M42` `FR-SRM2-010` builds a gate that every purchase order in the company passes through:

> The activation status per supplier per category is held authoritatively by `M42` and **exposed
> as a synchronous decision API that `M16` must call before creating any purchase order** —
> and `BRU-SRM2-02` makes it **fail closed**: if the service is unavailable, purchase orders are
> blocked, not permitted.

That gate is the strongest control in the procurement chain and it has one weakness: **a supplier
who never completed qualification is not blocked by it — they are absent from it.** Spend then
routes around the portal by the oldest mechanism available, which is a phone call to a supplier
someone already knows.

`04-00` sets the four targets this pack exists to move — 90% of purchase orders acknowledged
through the portal, 85% of invoices submitted through it, RFQ response above 75%, and a 60%
reduction in phone and email queries. All four are **supplier behaviours**, not system behaviours.

Three failures follow from onboarding without a pack:

| Absent | Consequence |
|---|---|
| A stated document set per supplier class | A courier partner is asked for the parts-vendor document set, concludes the process is bureaucratic, and stays on email |
| A stated meaning for "qualified" and "activated **per category**" | A supplier believes approval is global, quotes for a category they are not qualified in, and the order is blocked at `BRU-SRM2-01` |
| A stated explanation of bank-detail change control | The second-person approval requirement reads as distrust rather than as the anti-fraud control it is — and suppliers route bank changes through a relationship contact instead |

**What this pack is not.** It is not the portal terms or the Supplier Code of Conduct (`LG-006`),
not the scorecard explanation (`EO-006`), not the screen copy (`UI-015`, `UI-040`), not the help
set (`HC-007`), and not the internal procure-to-pay procedure (`SP-017`).

---

## 2. Scope

**In scope.** Supplier classification; registration through `P05`; the document set per supplier
class; qualification — what is assessed and by whom; **activation per category and per legal
entity**; provisional and conditional activation; document expiry and its automatic consequences;
bank-detail change control; integrity screening, conflict of interest and the Code of Conduct;
the agreed price list and price-change governance; the transaction cycle as the supplier
experiences it (RFQ → PO → delivery → invoice → payment → returns); the additional terms for
courier and recycling partners; and the first 90 days on the portal.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Portal terms of use and the Supplier Code of Conduct text | `LG-006` |
| **The performance scorecard, its metrics and how to improve a score** | **`EO-006`** |
| The vendor master record and its fields | `MD-016`; tax codes `MD-037`; payment terms and banks `MD-038` |
| The internal procure-to-pay procedure | `SP-017`; receipt and put-away `SP-018` |
| Screen copy | `UI-015`, `UI-040` |
| Help articles | `HC-007` |
| Vendor notifications | `NT-011` |
| RFQ, PO, GRN and RTV documents | `DT-022`, `DT-023`, `DT-024`, `DT-025` |
| Price and rate-card change communication | **`EO-011`** |
| Anti-bribery, ethics and whistleblowing policy | `LG-023` |
| E-waste disposal routes and certificates | `MD-047`, `SP-026` |
| Suspension, blocking, exit and reinstatement | **`EO-014`** |
| **Moving an *existing* supplier off email and phone onto `P05`** | **`CM-015`** Vendor and Seller Transition Pack — a one-off change event per wave |
| A supplier's own system integrating to ours | `AP-005`, `AP-011` — and `AP-007`/`AP-008` for the brand and corporate variants |

> **The `CM-015` boundary.** `CM-015` owns the **transition** of a named existing supplier, once,
> during a wave. This pack owns **qualification and activation** — which every supplier passes
> through, transitioned or new, because `BRU-SRM2-01` gates the purchase order and not the email
> habit. A `CM-015` transition therefore consumes §4.1 stages 3, 6 and 8 of this pack rather than
> replacing them.

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Prospective supplier's owner or commercial lead** | Deciding whether to register, and what it will take |
| **Supplier's finance contact** | Invoicing, matching, payment schedule, VDS and remittance |
| **Supplier's logistics or dispatch contact** | PO acknowledgement, ASN, delivery and rejection response |
| **Courier / logistics partner** | Consignment bookings, POD upload, settlement claims |
| **Recycling partner** | Batch transfers, disposal certificates, material recovery reporting |
| **1000FiX Procurement Officer** | The pack they issue, and the questions they will be asked |
| **Category owner / Quality Manager** | What the supplier has been told qualification assesses |
| **Finance Manager (`R26`)** | The payment and VDS commitments made to suppliers |

---

## 4. Content

### 4.1 The onboarding journey

| # | Stage | Supplier does | 1000FiX does | Exit condition |
|---|---|---|---|---|
| **1** | **Classify** | Identifies which class they are (§4.2) | Confirms the class and the resulting document set | Class agreed — it determines everything after |
| **2** | **Register** | Self-registers through `P05` with identity, categories, capabilities and documents (`FR-SRM2-007`) | Acknowledges; lists anything missing | Application complete |
| **3** | **Qualify** | Completes the category- and tier-specific questionnaire with evidence (`FR-SRM2-008`) | Risk-tiers the supplier (`FR-SRM2-004`); routes to category owner, Quality Manager and Procurement Manager as the tier requires (`FR-SRM2-009`) | Questionnaire scored |
| **4** | **Screen** | Declares related parties, conflicts of interest and accepts the Code (`FR-SRM2-019`, `FR-SRM2-020`) | Sanctions, conflict-of-interest and related-party screening | No unresolved match (`BRU-SRM2-17`) |
| **5** | **Verify banking** | Supplies bank details in the **legal entity's own name** | Verifies; `VND-02` requires CFO approval on a name mismatch | Account verified |
| **6** | **Activate** | — | Activation **per category, per legal entity** (`BRU-SRM2-03`), recorded with validity dates | `approval_state` = `approved`; `M16` may now raise a PO (`BRU-SRM2-01`) |
| **7** | **Agree terms** | Signs or accepts the framework agreement and price list | Records agreement term, scope, service levels, penalties, notice and renewal (`FR-SRM2-021`, `FR-SRM2-022`) | Prices published as the authority for call-off |
| **8** | **Enable portal** | Named users complete access setup; accepts `LG-006` | Provisions `P05` under `PS-01`; `MD-016` `portal_enabled` set | Supplier can see **only their own records** (`EA-01`, `EA-02`, `EA-06`, `BRU-SRM2-20`) |
| **9** | **Transact** | Responds to RFQs; acknowledges POs; submits invoices | §4.6 | First PO acknowledged and first invoice matched in the portal |

> **Stage 6 is the whole point.** Everything before it is preparation for a single boolean that
> the purchase-order path calls synchronously on every order.

### 4.2 Supplier classes, and why the class comes first

`MD-016` `vendor_category` and `M42` `FR-SRM2-002` between them define twelve classifications.
The pack is issued in five editions, because asking a courier for a parts-authorisation document
is how an onboarding stalls at stage 2.

| Edition | Covers | Distinctive requirement |
|---|---|---|
| **A — Parts and consumables** | OEM, authorised distributor, local distributor, local trader, importer | **Genuine-OEM evidence** where the supplier is to be qualified for OEM parts (`FR-SRM2-015`, `BRU-SRM2-05`) |
| **B — Services and sub-contract** | Service providers, sub-contractors, facilities, IT | Capability and capacity evidence; insurance where the work carries risk |
| **C — Logistics** | Courier partners, freight forwarders, C&F agents, cargo insurers | Consignment booking, POD upload and settlement-claim capability |
| **D — Recycling** | Recycling and disposal partners | Environmental authorisation; disposal certification capability (`SP-026`, `MD-047`) |
| **E — Brand partner as supplier** | Brands supplying consignment parts | Consignment terms (`FR-SRM2-024`); the **relationship** is `EO-003`, the **supply** is here |

> **Edition E exists because a brand partner appears in both ecosystems.** `M42` `FR-SRM2-002`
> lists `brand partner` as a supplier classification, and `EO-003` onboards the same organisation
> as a warranty counterparty. The pack states which relationship a given conversation is about,
> because the two have different documents, different systems and different 1000FiX owners.

### 4.3 The document checklist

**Universal — every class**

| # | Item | Why | Blocking |
|---|---|---|---|
| 1 | **Trade licence**, current | Lawful trade; `MD-016` `trade_licence_no` | **Yes** — an expired licence blocks new purchase orders (`VND-05`) |
| 2 | **e-TIN** | Income-tax identity; withholding treatment | **Yes** |
| 3 | **13-digit e-BIN** where VAT-registered | Input-VAT claim; `MD-016` `bin`, `is_vat_registered`. **9- and 11-digit BINs are not valid** | Conditional |
| 4 | **VDS position** | Whether 1000FiX must deduct VAT at source, and at what rate (`MD-016` `vds_applicable`, `vds_rate_code` → `MD-037`) | **Yes** (`VND-04`) |
| 5 | **Bank account in the legal entity's name**, with BEFTN routing | Payment destination. `VND-02` — a name mismatch requires CFO approval | **Yes** |
| 6 | **Named contacts** — commercial, delivery, finance, escalation | Portal scope is per user | **Yes** |
| 7 | **Related-party and conflict-of-interest declaration** | `FR-SRM2-019`; a match must be declared and approved before activation (`BRU-SRM2-17`) | **Yes** |
| 8 | **Anti-bribery declaration** and acceptance of the Supplier Code of Conduct | `FR-SRM2-019`, `FR-SRM2-020`, `LG-006` §5, `LG-023` | **Yes** |
| 9 | **Category declaration** — what they are asking to be qualified for | Activation is per category (`BRU-SRM2-03`) | **Yes** |
| 10 | Acceptance of `LG-006` portal terms | Portal access | **Yes** |

**By edition**

| Edition | Additional items |
|---|---|
| **A — Parts** | Genuine-OEM authorisation or authorised-distribution evidence **with an expiry date** (`FR-SRM2-015`) · product certifications · counterfeit-control declaration · lead times and MOQs · warranty terms on supplied parts |
| **B — Services** | Capability and capacity evidence · insurance certificate where risk requires it · relevant technical certifications · sub-contractor policy |
| **C — Logistics** | Fleet and coverage declaration · goods-in-transit insurance · driver and vehicle compliance · POD capability · cargo-handling certifications |
| **D — Recycling** | Environmental authorisation for the material streams handled · disposal site and route evidence (`MD-047`) · certificate-issuing capability (`SP-026`) · downstream chain evidence |
| **E — Brand as supplier** | Consignment terms — parts in scope, holding locations, valuation basis, settlement trigger and cadence, return rights, reconciliation frequency, liability for loss or damage (`FR-SRM2-024`) |

> **Document expiry is not administrative.** `FR-SRM2-017` warns ahead of expiry and applies the
> status consequence on lapse; `BRU-SRM2-04` **automatically suspends the supplier for the
> affected categories**. The pack states this at stage 2, not at the first suspension, because a
> supplier suspended mid-order for a lapsed licence assumes a system error.

### 4.4 What qualification actually assesses

Suppliers assume qualification is a document check. It is not, and saying so improves the quality
of what arrives.

| Assessed | By | Depth set by |
|---|---|---|
| Legal existence and tax standing | Procurement | All tiers |
| **Category competence** — can they supply *this* category | Category owner | Risk tier (`FR-SRM2-004`) |
| Quality system and defect handling | Quality Manager | Risk tier |
| Capacity against our expected volume | Category owner | Risk tier |
| Financial stability and continuity risk | Procurement / Finance | Risk tier |
| Counterfeit exposure for parts categories | Quality Manager | **Always, for parts** |
| Integrity — sanctions, conflict of interest, related party | Procurement with CFO | **Always** |
| Environmental and labour standards | Quality / Procurement | Code of Conduct; `LG-006` §5.2–§5.3 |

**Three outcomes, and the middle one is the most common.**

| Outcome | What it means | Time-boxed? |
|---|---|---|
| **Approved** | Activated for the named categories, with a validity period (`FR-SRM2-011`) | Yes — re-qualification on expiry |
| **Conditional / provisional** | Activated with named conditions | **Yes, and it blocks automatically at expiry with no grace period** (`FR-SRM2-013`, `BRU-SRM2-12`) |
| **Not approved** | With the reason, and what would change it | Re-application permitted |

### 4.5 Bank-detail change control — stated plainly, once

The single most-questioned control in supplier onboarding, and the one most worth explaining
rather than merely imposing.

| What happens | Rule |
|---|---|
| A bank-detail change requires **documented verification and second-person approval** | `FR-SRM2-018`, `BRU-SRM2-07` |
| The change and its approver are retained **immutably**, with a security event raised | `BRU-SRM2-07` |
| The change **resets `approval_state` to `verified` and requires re-approval** | `VND-03` |
| Two suppliers sharing a bank account number raises a warning | `VND-07` — *"a duplicate or a fraud signal"* |
| A change requested by email or phone is **not actioned** | `VO-06` |

> **Why we say this to suppliers rather than only enforcing it.** Supplier-bank-detail fraud
> works by impersonating the supplier to us. A supplier who knows we will never action a change
> from an email is a supplier who will tell us when they receive one purporting to be from us.

### 4.6 The transaction cycle

| Step | Supplier does | 1000FiX does | Where | Target |
|---|---|---|---|---|
| **RFQ** | Responds with price, lead time and validity | Issues the RFQ to qualified suppliers in the category | `P05`, `DT-022` | **Response rate > 75%** |
| **PO** | **Acknowledges or queries; confirms the delivery date** | Raises the PO only against an active supplier for that category (`BRU-SRM2-01`) | `P05`, `DT-023` | **> 90% acknowledged in the portal** |
| **ASN** | Submits advance shipping notice | Prepares receipt | `P05` | — |
| **Delivery** | Delivers against the PO | Receipt and inspection (`SP-018`); outcome published to the portal | `DT-024` | — |
| **Rejection** | Responds to a rejection | Records the reason and the quality event | `P05` | Feeds `EO-006` |
| **Invoice** | Submits the invoice against the PO | **Three-way match**; unmatched invoices are blocked (`G3-06`) | `P05` | **> 85% submitted in the portal**; `KPI-049` match-exception rate |
| **Payment** | Sees the schedule and remittance advice | Pays per `payment_term_code`, net of VDS where applicable | `P05` | — |
| **Return** | Receives the RTV notice; issues a credit note | Raises the RTV | `DT-025` | — |
| **Price change** | Submits and justifies a proposed increase | **Approves before it takes effect; `M16` cannot order at an unapproved price** (`FR-SRM2-023`, `BRU-SRM2-14`) | `P05` | Zero unapproved increases reaching a PO |

**Additional terms by edition.**

- **Logistics (C):** consignment bookings, status updates, POD upload and settlement claims
  (`04-00` P05); `LG-006` §4.8 carries the terms.
- **Recycling (D):** batch transfers, disposal certificates and material-recovery reporting;
  `LG-006` §4.7 carries the terms; `SP-026` the procedure. **A disposal certificate is a
  compliance artefact, not a delivery note** — `G8-04` requires the e-waste chain fully certified
  with zero uncertified disposals.

### 4.7 What a supplier can see — and cannot

| Can see | Cannot see |
|---|---|
| Their own RFQs, POs, receipts, inspection outcomes, invoices, payments, returns | Any other supplier's records, prices or volumes |
| Their own agreed price list and its validity dates | 1000FiX cost, margin, or another supplier's pricing |
| Their own scorecard, its metrics and the underlying data (`FR-SRM2-029`, `EO-006`) | Any other supplier's scorecard or the ranking |
| Their own documents and expiry dates | Internal risk tier commentary and category strategy |

`EA-01`, `EA-02`, `EA-06` and `BRU-SRM2-20` enforce it; `LG-006` §4.9 states it.

### 4.8 The first 90 days

| Days | Supplier milestone | 1000FiX milestone | Test |
|---|---|---|---|
| **0–30** | Registered, qualified, activated for at least one category; portal users signed in | Activation recorded per category with validity dates; documents loaded with expiry dates | Can `M16` raise a PO for this supplier and category? |
| **31–60** | First RFQ response and first PO acknowledged **in the portal** | First receipt and inspection outcome published | Portal acknowledgement, not email |
| **61–90** | First invoice submitted in the portal and three-way matched | First payment with remittance advice visible | **`KPI-049` match exception rate for this supplier**; a supplier whose first three invoices all fail matching has an unresolved PO or price problem, not an invoicing problem |
| **91+** | First scorecard published (`EO-006`) | First performance review at the segment cadence (`BRU-SRM2-18`) | Steady state |

**The 90-day test is not "are they registered" but "has an order completed end to end in the
portal".** A supplier registered and never transacted through is indistinguishable, in the KPI, from
a supplier who never registered.

### 4.9 Rules

| # | Rule |
|---|---|
| **VO-01** | The pack is issued **by edition** (§4.2). A supplier is never given a document list that does not apply to them |
| **VO-02** | Qualification and activation are described as **per category and per legal entity, never global** (`BRU-SRM2-03`). This is the single most common supplier misunderstanding |
| **VO-03** | Document expiry is described with its **automatic** consequence (`BRU-SRM2-04`), at stage 2 |
| **VO-04** | Conditional activation is described as **time-boxed with no grace period** (`BRU-SRM2-12`) |
| **VO-05** | The activation gate is described as **fail-closed** (`BRU-SRM2-02`): if the check cannot run, no order is raised. Suppliers are told, so an outage is not read as a cancelled order |
| **VO-06** | Bank-detail changes are **only** actioned through the portal with second-person approval. The pack states that an emailed or telephoned change will not be actioned, whoever appears to send it |
| **VO-07** | No price, rate or commercial term is stated here. The agreed price list (`FR-SRM2-022`) is the authority; `EO-011` governs change communication |
| **VO-08** | The pack never promises volume. `FR-SRM2-021` frameworks may carry committed volume; a pack that implies one where the agreement does not is a commercial exposure |
| **VO-09** | Genuine-OEM qualification requires **current documentary evidence with an expiry date** (`BRU-SRM2-05`), and the pack says a supplier cannot be qualified for OEM parts without it |
| **VO-10** | The data-boundary table (§4.7) appears in every edition |
| **VO-11** | Anti-bribery and the Code of Conduct are presented as **conditions of qualification**, not as an appendix (`FR-SRM2-020`, `LG-006` §5) |
| **VO-12** | Permanent blocking for a confirmed sanctions match or confirmed counterfeit supply is stated, including that it **cannot be reversed below CFO or CEO authority** (`BRU-SRM2-16`) |
| **VO-13** | Nothing in the pack varies `LG-006`. Variation requests route to Legal |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`MD-016`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) | Every field the registration collects; `VND-01`…`VND-07` |
| [`MD-037`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md), [`MD-038`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md) | VDS rates, payment terms, bank master |
| `M42` §5.1–§5.4 | Classification, risk tiering, qualification, the activation gate, documents, bank control, agreements and price governance |
| `M16`, [`SP-017`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-017_SOP_Procurement_to_Payment.md) | The procure-to-pay cycle §4.6 describes from the supplier's side |
| [`SP-018`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md) | Receipt, inspection and put-away — where a delivery outcome is created |
| [`SP-026`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-026_SOP_EWaste_Collection_and_Disposal.md), [`MD-047`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-047_EWaste_Material_and_Disposal_Route_Register.md) | Recycling-partner obligations |
| [`LG-006`](../10_Legal_Policy_and_Compliance/LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md) | Portal terms and the Supplier Code of Conduct accepted at stages 4 and 8 |
| [`LG-023`](../10_Legal_Policy_and_Compliance/LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md) | Anti-bribery, ethics and whistleblowing |
| [`EO-006`](EO-006_Supplier_Performance_Scorecard_Explanation.md) | The scorecard published at day 91 |
| [`EO-011`](EO-011_Rate_Card_and_Pricing_Communication_Pack.md) | Price and rate-card change communication |
| [`EO-014`](EO-014_Ecosystem_Offboarding_and_Exit_Content.md) | Suspension, blocking, exit and reinstatement |
| [`UI-015`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-015_P05_Vendor_and_Supplier_Portal_UI_Copy_Pack.md), [`UI-040`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-040_Registration_and_Onboarding_Flow_Copy.md), [`HC-007`](../09_Help_Centre_and_Self_Service/09A_Help_Sets_By_Portal/HC-007_Help_Set_P05_Vendor_and_Supplier_Portal.md), `NT-011` | Screens, flow copy, help and notifications |
| [`DT-022`](../05_Document_and_Print_Templates/05C_Supply_Chain_and_Logistics/DT-022_Request_for_Quotation.md)…[`DT-025`](../05_Document_and_Print_Templates/05C_Supply_Chain_and_Logistics/DT-025_Return_to_Vendor_and_Debit_Advice.md) | RFQ, PO, GRN, RTV |

> **Rule-citation attribution.** **BRU-SRM2-\***  → `M42` §9 — these are **module-scoped** rule families and **`05-05` carries none of them**. Stated per `AUDIT-015` R-11, which asked that the convention be recorded once rather than rediscovered by each extraction.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually, and at every re-qualification cycle |
| Trigger for out-of-cycle review | A change to `MD-016` required fields or `VND-*` rules; a change to VDS or e-BIN requirements; a `P05` release changing the registration or invoice flow; a change to `LG-006`; a confirmed counterfeit or sanctions event; a new supplier class |
| Owner | Procurement Manager, with Finance for §4.5 and §4.6 and Quality for §4.4 |
| Change control | Any change to the document set or to what a supplier is told about payment requires Procurement Manager and Finance Manager sign-off |
| Effectiveness measure | The four `04-00` P05 targets, plus the share of registered suppliers that complete an end-to-end portal transaction within 90 days (§4.8) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This pack is registered W3 and `M42` — the module that owns qualification, activation and the scorecard — is W4.** `02-02` §wave places `M42` at W4 (Months 14–18); `04-00` places `P05` at W3 (Months 9–13); `06-01` §3's Wave 3 detail lists *"Procurement: requisition, PO, receipt, three-way match, vendor portal"* and **does not list `M42` in any wave's module set**. §4.1 stages 3, 4, 6 and 7 and the whole of §4.4 therefore describe capability that arrives a wave after the pack is issued. **`EO-006` inherits the same defect one level worse** — it explains a scorecard whose module is W4 | Programme Content Lead with Supply Chain Director and Enterprise Architecture | **W3 — register sequencing decision** |
| **O-02** | **`06-01` §3 and `02-02` §wave disagree on module content for Waves 3 and 4.** `02-02` lists `M42` at W4 and `M40` at W7; `06-01` §3's per-wave module lists omit both. This is a specification defect outside Category 18, and **it is the reason `O-01` cannot be resolved by reading either document alone** | Enterprise Architecture with Programme Manager | **W3** |
| **O-03** | **The four `04-00` P05 targets have no registered KPI identifier.** PO acknowledgement > 90%, portal invoicing > 85%, query reduction −60% and RFQ response > 75% exist only in the portal specification. `06-02` §2.6 registers `KPI-048` (assigned to `M16`, with `M42` §15 recording the conflict) and `KPI-049`. **`M42` §15 already flags that fourteen of its own metrics are unregistered and require `KPI-0nn` allocation — "an audit action"**. **This is an instance of `AUDIT-015` RP-01, not a new finding**: that audit counted **250 KPI identifiers in use against 95 registered in `06-02`**, with 196 unregistered, and recommended widening the register per `RP-001` §4.3 (R-01). The portal targets below are part of the 196. | BI Lead with Enterprise Architecture | **W3 — before the Gate 3 pack** |
| **O-04** | **The five pack editions do not exist as artefacts.** §4.2 specifies them; this file specifies the content of all five and **is not itself five documents.** Producing and maintaining five editions across 200–500 suppliers is unresourced, and `CG-002` records no Procurement content author | Procurement Manager with Programme Content Lead | **W3** |
| **O-05** | **Brand-supplier consignment terms have no owning content file.** Edition E requires the `FR-SRM2-024` consignment term set and no `MD`, `LG` or `EO` file holds it; `MD-017` carries only a boolean. **This is the same gap `EO-003` `O-04` records from the warranty side** — one gap, two files, no owner | Supply Chain Director | **W3 for the supply side; W4 for the warranty side** |
| **O-06** | **VDS applicability is a supplier-specific determination this pack asks the supplier to self-declare.** `MD-016` `vds_applicable` gates `vds_rate_code` (`VND-04`) and 1000FiX carries the statutory consequence of deducting wrongly or failing to deduct. The source here is authoritative secondary (`class: P2`); **`CG-012` `EV-01` would require a primary instrument if this were Class A content, and the VDS position is Class A in substance even though the pack is not** | CFO / Tax Manager with external verification (`CG-007` G6) | **W3 — before the first supplier payment** |
| **O-07** | **Insurance requirements are named but not specified.** Editions B and C require insurance "where risk requires it" and "goods-in-transit insurance" with no limits, no named perils and no evidence standard. `LG-006` §5.8–§5.11 sets liability caps; **an uninsured logistics partner carrying customer devices is a custody exposure `M03` chain-of-custody controls do not cover** | Risk with Legal Counsel and Procurement Manager | **W3 — before the first courier partner is activated** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the three `EO` additions placed and the template gap noted
- [x] **The activation gate identified as the control the whole pack serves, including its fail-closed behaviour**
- [x] Nine-stage journey with an exit condition at each stage
- [x] Five supplier editions defined, with the brand-as-supplier overlap against `EO-003` stated
- [x] Universal and per-edition document checklists, each item traced to its rule or field
- [x] Qualification described as an assessment, not a document check, with three named outcomes
- [x] **Bank-detail change control explained rather than merely imposed, with the reason a supplier benefits from knowing it**
- [x] Transaction cycle stated from the supplier's side with the four `04-00` targets attached
- [x] Data-boundary table stated with the `EA-*` and `BRU-SRM2-20` enforcement named
- [x] First-90-days test framed as an end-to-end portal transaction rather than registration
- [x] Thirteen rules, including the prohibition on implying volume
- [x] All internal links resolve
- [x] Seven open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` pack is W3 and `M42` is W4 — outstanding; §4.4 describes capability that does not yet exist**
- [ ] **`O-03` the four targets this pack moves have no registered KPI — outstanding**
- [ ] **`O-04` five editions unproduced and unresourced — outstanding**
- [ ] **`O-06` VDS determination unverified against a primary instrument — outstanding; `CG-007` G6 required in substance**
- [ ] **`O-07` insurance requirements unspecified — outstanding; blocks courier activation**
- [ ] Named approver recorded — **pending Content Design Lead with Procurement Manager**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
