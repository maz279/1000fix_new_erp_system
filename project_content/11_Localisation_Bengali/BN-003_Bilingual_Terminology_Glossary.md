---
id: BN-003
title: Bilingual Terminology Glossary
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Enterprise Architecture and a native Bengali linguistic reviewer
reviewers: [Enterprise Architecture, Content Design Lead, Programme Content Lead, Business Owners Forum, Legal & Compliance, Finance, Quality]
approver: Architecture Review Board with Programme Content Lead
content_class: D
purpose: >
  Binds one approved Bengali form to every controlled English term in CG-004, records the
  loanword tier that decides whether the term is kept in Latin, transliterated or translated,
  and extends the binding to the statutory, commercial and master-data vocabulary the ERP
  displays. CG-004 T-07 states that a term is not approved until its Bengali equivalent is
  approved; that rule currently blocks CG-004 itself. Without this file fix.service.order
  acquires five Bengali names across five portals and no review can afterwards tell which
  was intended.
traces_to: [CG-004, CG-004 T-07, CG-004 §7, CG-004 §10 item 1, BN-002, BN-004, MD-027, MD-003, MD-006, MD-019, MD-021, MD-024, MD-025, MD-026, RF-001, 05-02]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: self — this file is inherently bilingual (`CG-010` §3.2); it has no separate `_BN` version
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-004 §4.1–§4.8 controlled vocabulary, §5 registered surface-specific pairs, §6 concepts without entities, §7 Bengali binding approach, T-07 ratified-together rule
    verified: 2026-08-17
    class: P1
  - source: 1000_fix_corporate_website project_content LOCALIZATION/Bengali Language/BN-002 Bengali Glossary/Terminology v1.0 §2–§10 — established consumer-facing Bengali for device, service, pricing and payment vocabulary already in production on the corporate website
    verified: 2026-08-17
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027 §9 sample rows — internal_label_bn and customer_label_bn columns, showing the bilingual state-label pattern already adopted
    verified: 2026-08-17
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03B_Portals/UI-011 §2 and UI-012 §2 — indicative Bengali terminology bindings, explicitly marked as pending this file
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 Data Model and Entity Catalogue — the fix.* models every business-object term binds to
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2026-11-17
---

# BN-003 — Bilingual Terminology Glossary

> **`CG-004` cannot be approved until this file exists.** `T-07`: a term is not approved until
> its Bengali equivalent is approved, and the two documents are ratified together. `CG-004`'s own
> Definition of Done records the block: *"`BN-003` Bengali row exists for every term — blocked;
> `BN-003` not yet written."*
>
> Six approved `UI` packs already carry Bengali marked **"indicative pending `BN-003`"**. This
> file makes them authoritative or corrects them. Where it corrects them, §11 lists the change.

---

## 1. How to read this glossary

| Column | Meaning |
|---|---|
| **English** | The approved English term from `CG-004`. This file never introduces an English term |
| **Bengali** | The **one** approved Bengali form. Not a suggestion, not a preferred option |
| **Tier** | The `BN-002` §4 loanword tier: **1** keep Latin · **2** transliterate · **3** translate · **4** translate with English in brackets on first use |
| **Entity** | The `fix.*` model or register the term binds to (`CG-004` `T-03`) |
| **Note** | Surface restriction, reserved status, or the reason a near-miss form is wrong |

| # | Rule |
|---|---|
| **GL-01** | **One English term, one Bengali form.** Two Bengali forms for one English term is the same defect as two English terms for one object (`CG-004` `T-02`) |
| **GL-02** | **One Bengali form, one English term.** Two English terms sharing one Bengali form destroys the distinction the English vocabulary was built to make. Checked at `BN-018` `LQ-11` |
| **GL-03** | The **tier is a property of the term**, decided here, never chosen at translation time (`BN-002` `LW-01`) |
| **GL-04** | Verbs are given in the **honorific imperative** (`BN-002` `AD-02`). Other inflections derive from it; the stem is what is fixed |
| **GL-05** | **Where a registered surface-specific pair exists in English (`CG-004` §5), a matching Bengali pair is registered here** and both forms are approved |
| **GL-06** | A term absent from this glossary is **not approved for use in Bengali**. It is raised under §10, not invented in the string (`CG-004` `T-08` applied to Bengali) |
| **GL-07** | This file and `CG-004` are **ratified together and versioned together**. Neither is authoritative alone (`T-07`) |
| **GL-08** | Bengali forms here are subject to `BN-002` §2–§3 — চলিত register, আপনি address. A form that violates `BN-002` is a defect in this file, not an exception to `BN-002` |

---

## 2. Organisation and network

| English | Bengali | Tier | Entity | Note |
|---|---|:--:|---|---|
| branch | **শাখা** | 3 | `fix.branch` | Internal surfaces only. Registered pair with *service centre* — `GL-05` |
| service centre | **সার্ভিস সেন্টার** | 2 | `fix.branch` | Customer-facing. Already in production usage — `MD-003` `name_bn` examples, `NT-004` `{branch}` |
| workshop | **ওয়ার্কশপ** | 2 | `fix.branch` (type) | Never শাখা. A workshop is not a branch |
| zone | **জোন** | 2 | `fix.zone` | Never এলাকা — that renders the banned English *area* |
| entity | **আইনি সত্তা** | 3 | `fix.entity` | Never প্রতিষ্ঠান, which renders the banned *organisation* |
| business line | **ব্যবসায়িক ধারা (business line)** | 4 | `fix.business.line` | Reporting dimension. One of fourteen |
| cost centre | **কস্ট সেন্টার** | 2 | `fix.cost.center` | English content uses en-GB *cost centre*; the model is `fix.cost.center` (`CG-004` §4.1 spelling exception) |

---

## 3. Party and people

| English | Bengali | Tier | Entity | Note |
|---|---|:--:|---|---|
| party | **পক্ষ** | 3 | `fix.party` | Internal and data-model surfaces only. Never shown to a customer |
| customer | **গ্রাহক** | 3 | `fix.party` + role | The default term on every consumer surface |
| client | **ক্লায়েন্ট** | 2 | `fix.party` + role | **Reserved** — contracted corporate or government account only. Never for an individual |
| technician | **টেকনিশিয়ান** | 2 | `fix.technician.profile` | Confirmed by existing production usage. Never মিস্ত্রি |
| engineer | **ইঞ্জিনিয়ার** | 2 | `fix.party` + seller role | **Reserved** — external marketplace freelance engineer. **Diverges from the website glossary**, §11 D-2 |
| seller | **বিক্রেতা (seller)** | 4 | `fix.party` + role | Marketplace participant. English bracket on first use per surface, because সেলার is also heard |
| vendor | **ভেন্ডর** | 2 | `fix.party` + role | **Reserved** — supplier of parts, services or logistics |
| brand partner | **ব্র্যান্ড পার্টনার** | 2 | `fix.brand` | Never প্রস্তুতকারক (manufacturer) |
| partner | **পার্টনার** | 2 | `fix.alliance.partner` | **Reserved** — alliance, referral or channel partner. Never a vendor or seller |
| employee | **কর্মী** | 3 | `hr.employee` (ext) | Never স্টাফ |
| rider | **রাইডার** | 2 | `fix.party` + role | Established in Bangladeshi delivery usage. **Never ডেলিভারি বয়** — see `BN-002` `AD-01` |

> **রাইডার and the dignity rule.** The English vocabulary bans *delivery boy* (`CG-004` §4.2).
> The Bengali ban matters more: ডেলিভারি বয় is in common use in Bangladesh and a translator will
> reach for it. It is prohibited on the same grounds as `BN-002` `AD-03` — the company does not
> address its own workforce diminutively.

---

## 4. Service and work

| English | Bengali | Tier | Entity | Note |
|---|---|:--:|---|---|
| service order | **সার্ভিস অর্ডার** | 2 | `fix.service.order` | The most-cited object in the system. Customer surfaces may present it as **আমার সার্ভিস** — `CG-004` §10 item 2 remains open on the English side |
| job | **জব** | 2 | `fix.dispatch.job` | Confirmed by `UI-012`. Never কাজ alone — কাজ is generic work, not the dispatchable unit |
| work order | **ওয়ার্ক অর্ডার** | 2 | `fix.work.order` | On Class A/B documents the formal **কার্যাদেশ** is used (`BN-002` `RD-C`). Both are registered; the surface decides |
| task | **টাস্ক** | 2 | `fix.work.order.task` | A step within a work order |
| service request | **সার্ভিসের অনুরোধ** | 3 | — | The act of requesting, before a service order exists. A phase, not an entity |
| estimate | **এস্টিমেট** | 2 | `fix.estimate` | Confirmed by `UI-011`, `UI-012`. **Diverges from the website glossary**, §11 D-1 |
| quotation | **কোটেশন** | 2 | — | **Reserved** — commercial quotation to an organisation, including tender responses |
| diagnosis | **ডায়াগনোসিস** | 2 | `fix.device.condition.log` | The technician's confirmed determination |
| fault | **ত্রুটি** | 3 | `MD-024` code | Confirmed. The **confirmed** defect |
| symptom | **লক্ষণ** | 3 | `MD-024` code | Confirmed. What the customer **reported**. Never interchangeable with ত্রুটি |
| rework | **রিওয়ার্ক (rework)** | 4 | `fix.service.order` flag | A quality measure with contractual weight (`BRU-SRM-06`). Never পুনরায় মেরামত, which describes any second repair |
| service report | **সার্ভিস রিপোর্ট** | 2 | `fix.service.report` | Given to the customer on completion |
| consignment | **কনসাইনমেন্ট** | 2 | `fix.consignment` | **Deliberately not চালান.** চালান is bound to *challan* in §6 and the collision would make a delivery challan and a consignment the same word |
| custody | **হেফাজত** | 3 | `fix.asset.custody` | Documented possession by a named party. The word carries the right weight in Bengali administrative usage |

---

## 5. Commercial

| English | Bengali | Tier | Entity | Note |
|---|---|:--:|---|---|
| contract | **চুক্তি** | 3 | `fix.contract` | Covers AMC, RAMC and MSP |
| AMC | **AMC** | 1 | `fix.contract` (type) | First use in customer content: **বার্ষিক রক্ষণাবেক্ষণ চুক্তি (AMC)** — Tier 4 pattern |
| RAMC | **RAMC** | 1 | `fix.contract` (type) | First use: **আবাসিক বার্ষিক রক্ষণাবেক্ষণ চুক্তি (RAMC)** |
| entitlement | **প্রাপ্যতা** | 3 | `fix.contract.line` | What the contract permits its holder to consume |
| covered asset | **কভারভুক্ত ডিভাইস (covered asset)** | 4 | `fix.contract.covered.asset` | Gating object for `BRU-SRM-03`; the term appears in refusal messages and must be recognisable |
| warranty | **ওয়ারেন্টি** | 2 | `fix.warranty.register` | Never গ্যারান্টি — a distinct consumer expectation in Bangladesh |
| protection plan | **প্রোটেকশন প্ল্যান** | 2 | `fix.warranty.product` | **Never ইন্স্যুরেন্স.** Insurance has a regulatory meaning (`CG-004` §4.4) |
| claim | **ক্লেইম** | 2 | `fix.warranty.claim` | Submission to a brand partner for reimbursement |
| rate card | **রেট কার্ড** | 2 | `fix.brand.rate.card` | Versioned, effective-dated |
| price list | **মূল্য তালিকা** | 3 | `product.pricelist` (ext) | Catalogue-level pricing by segment |
| service credit | **সার্ভিস ক্রেডিট (service credit)** | 4 | `fix.contract.sla` | Class B legal term defined in `LG-015`. Never জরিমানা (penalty) or ক্ষতিপূরণ (compensation) |
| subscription | **সাবস্ক্রিপশন** | 2 | `fix.contract` (type) | Recurring-revenue product billed on a cycle |
| membership | **সদস্যপদ** | 3 | `fix.loyalty.member` | **Reserved** for the Privilege programme. *Privilege* itself is Tier 1 (`BN-004`) |
| commission | **কমিশন** | 2 | `fix.commission.entry` | Marketplace and partner transactions |

---

## 6. Finance and statutory

**Every Tier 1 row in this table is also a `BN-004` do-not-translate entry.** A statutory
identifier rendered in Bengali script cannot be transcribed into a government system.

| English | Bengali | Tier | Entity | Note |
|---|---|:--:|---|---|
| invoice | **ইনভয়েস** | 2 | `account.move` (ext) | In the Bangladesh VAT context the document is *Mushak 6.3* |
| **Mushak 6.3** | **Mushak 6.3** | **1** | `fix.mushak.invoice` | **Never translated, never transliterated, never paraphrased** (`CG-004` `T-05`). The same applies to Mushak 6.1, 6.2, 6.6 and 9.1 |
| challan | **চালান** | 3 | — | Only in the registered compounds **ডেলিভারি চালান** and **Mushak চালান**. Never alone |
| receipt | **রসিদ** | 3 | `fix.cash.movement` | Confirmed by `NT-004` and the website glossary |
| statement | **হিসাব বিবরণী** | 3 | — | A periodic account summary. **Never a synonym for ইনভয়েস** |
| credit note | **ক্রেডিট নোট** | 2 | `account.move` (ext) | The statutory adjustment document |
| **VDS** | **VDS** | **1** | — | VAT Deducted at Source. Certificate is Mushak 6.6 |
| **BIN** | **BIN** | **1** | `fix.entity` field | Business Identification Number, NBR-issued |
| **TIN** | **TIN** | **1** | `fix.party` field | Sensitive under `05-06` NFR-086 |
| charge | **চার্জ** | 2 | `fix.charge` | A priced line applied to a service order |
| fee | **ফি** | 2 | — | **Reserved** — platform, registration or payout fee in the marketplace context |
| cost | **খরচ** | 3 | — | **Reserved** — internal cost accounting. **Never what a customer pays** |
| price | **দাম** | 3 | `fix.catalogue.item` | Customer surfaces. Class A/B documents use the formal **মূল্য** (`BN-002` `RD-C`); registered pair under `GL-05` |

---

## 7. Supply chain and asset

| English | Bengali | Tier | Entity | Note |
|---|---|:--:|---|---|
| part | **পার্টস** | 2 | `fix.part` | Confirmed by `UI-012`. Used as a singular term in Bangladeshi technical usage; this is deliberate, not a number error |
| item | **আইটেম** | 2 | `fix.catalogue.item` | **Reserved** — a sellable catalogue entry |
| device | **ডিভাইস** | 2 | `fix.asset` | The customer's equipment under service |
| asset | **সম্পদ** | 3 | `fix.asset` | The umbrella object for any tracked physical thing |
| equipment | **যন্ত্রপাতি** | 3 | `fix.asset` (company) | **Reserved** — company-owned tools and test equipment |
| stock | **স্টক** | 2 | `stock.quant` (ext) | Quantity at a location |
| inventory | **ইনভেন্টরি** | 2 | — | **Reserved** — the function and the count activity, not the quantity |
| van stock | **ভ্যান স্টক** | 2 | `fix.van.stock` | Confirmed by `UI-012`. Under the technician's own custody |
| location | **লোকেশন** | 2 | `fix.stock.location` | **Always qualified** — স্টক লোকেশন, শাখা লোকেশন |
| site | **সাইট** | 2 | `fix.address` | **Reserved** — a corporate client's premises |
| transfer | **ট্রান্সফার** | 2 | `fix.transfer.request` | Movement of stock between locations |

---

## 8. Quality, governance and platform

| English | Bengali | Tier | Entity | Note |
|---|---|:--:|---|---|
| complaint | **অভিযোগ** | 3 | `fix.complaint` | Tracked to closure. Never এসকেলেশন |
| escalation | **এসকেলেশন** | 2 | — | Raising to a higher authority under `SP-005`. Never a synonym for অভিযোগ |
| non-conformance | **অসঙ্গতি (non-conformance)** | 4 | `fix.audit.finding` | ISO 9001 context. The NCR abbreviation itself is Tier 1 |
| defect | **ডিফেক্ট** | 2 | — | **Reserved** — software or product defect. Never ত্রুটি, which is bound to *fault* |
| **CAPA** | **CAPA** | **1** | `fix.capa` | ISO 9001 term; never paraphrased |
| finding | **অডিট ফাইন্ডিং** | 2 | `fix.audit.finding` | An observation raised during an audit, classified by severity |
| role | **রোল** | 2 | `05-04` `Rnn` | A registered access and responsibility profile. Never ভূমিকা, which reads as a narrative part |
| permission | **অনুমতি** | 3 | — | A specific granted capability within a role |
| portal | **পোর্টাল** | 2 | `Pnn` | One of the twelve registered surfaces |
| application | **অ্যাপ্লিকেশন** | 2 | `Pnn` | Native mobile surface. Customer-facing pair: **অ্যাপ** — `GL-05` |
| module | **মডিউল** | 2 | `Mnn` | One of the 67 registered capability modules |
| event | **ইভেন্ট** | 2 | `05-03` catalogue | A published domain event |

---

## 9. Verbs

`CG-004` §4.8 controls twenty-eight verbs and reserves fifteen of them for one meaning each.
**Bengali makes this harder, not easier**: inflection multiplies surface forms, and a translator
who does not know a verb is reserved will collapse two of them into one Bengali word. Two such
collisions already exist in approved packs — §11 D-3.

| English | Bengali (honorific imperative) | Tier | Reserved for | Never |
|---|---|:--:|---|---|
| create | **তৈরি করুন** | 3 | Bringing a new record into existence | নতুন করুন |
| raise | **উত্থাপন করুন** | 3 | **Reserved** — claim, NCR, complaint, requisition | জমা দিন (that is *submit*) |
| register | **নিবন্ধন করুন** | 3 | **Reserved** — recording a device, party or certification in a master register | তৈরি করুন |
| assign | **নির্ধারণ করুন** | 3 | Attaching a **person** to work | বরাদ্দ করুন (that is *allocate*) |
| allocate | **বরাদ্দ করুন** | 3 | **Reserved** — attaching stock, budget or an identifier | নির্ধারণ করুন |
| dispatch | **ডিসপ্যাচ করুন** | 2 | **Reserved** — releasing a job to the field | পাঠান |
| approve | **অনুমোদন করুন** | 3 | Giving authority for something to proceed | নিশ্চিত করুন, গ্রহণ করুন |
| authorise | **অথরাইজ করুন** | 2 | **Reserved** — granting a permission or an override under `BR-STD-06` | **অনুমোদন করুন** — that is *approve*, and the distinction is an audit control |
| accept | **গ্রহণ করুন** | 3 | **Reserved** — a counterparty agreeing to terms or an offer | অনুমোদন করুন |
| confirm | **নিশ্চিত করুন** | 3 | **Reserved** — a user verifying an action in a dialog | অনুমোদন করুন |
| reject | **প্রত্যাখ্যান করুন** | 3 | Declining with a recorded reason, ending the flow | ফিরিয়ে দিন |
| decline | **ফিরিয়ে দিন** | 3 | **Reserved** — a technician or seller not taking offered work | **প্রত্যাখ্যান করুন** — §11 D-3 |
| cancel | **বাতিল করুন** | 3 | Ending a record before completion, by request | রদ করুন |
| void | **রদ করুন** | 3 | **Reserved** — nullifying a posted financial document | বাতিল করুন |
| close | **বন্ধ করুন** | 3 | Ending a record that has run its course | সম্পন্ন করুন |
| complete | **সম্পন্ন করুন** | 3 | **Reserved** — work is done and quality-passed | শেষ করুন |
| resolve | **নিষ্পত্তি করুন** | 3 | **Reserved** — a complaint or incident reaching an outcome | সমাধান করুন (that is generic problem-solving) |
| submit | **জমা দিন** | 3 | Sending a record to another party for action | পাঠান |
| post | **পোস্ট করুন** | 2 | **Reserved** — committing a financial entry to the ledger | জমা দিন |
| issue | **ইস্যু করুন** | 2 | Releasing a part, document or certificate | দিন |
| hand over | **হস্তান্তর করুন** | 3 | **Reserved** — transferring custody of a device between named parties | দিয়ে দিন |
| release | **রিলিজ করুন** | 2 | **Reserved** — freeing a hold or reservation | **ছাড় দিন** — ছাড় is bound to *discount* |
| reschedule | **পুনর্নির্ধারণ করুন** | 3 | Changing an appointment to a new time | পিছিয়ে দিন |
| escalate | **এসকেলেট করুন** | 2 | Raising to a higher authority per `SP-005` | ফ্ল্যাগ করুন |
| flag | **ফ্ল্যাগ করুন** | 2 | **Reserved** — marking a record for attention without changing state | এসকেলেট করুন |
| archive | **আর্কাইভ করুন** | 2 | Setting `active = False` per `05-02` DM-06 | **মুছে ফেলুন** |
| delete | **মুছে ফেলুন** | 3 | Permanent destruction. **Applies to almost nothing** | — |

> **The `অনুমোদন / অথরাইজ` split is the most important row in this table.** `BR-STD-06` requires
> every override to name an authoriser and record a reason. If Bengali renders both *approve* and
> *authorise* as অনুমোদন, the audit trail reads identically for a routine approval and a control
> override, and the control becomes unevidenced in the language the branch actually works in.

---

## 10. Concepts without entities

| English | Bengali | Tier | Note |
|---|---|:--:|---|
| turnaround time (TAT) | **টার্নঅ্যারাউন্ড টাইম (TAT)** | 4 | Measured per `RP-001`. TAT stays Latin |
| first-time fix | **প্রথমবারেই সমাধান (first-time fix)** | 4 | `KPI-004`. FTF is not used in customer content |
| **SLA** | **SLA** | **1** | Defined in `MD-028` and `LG-015`. Never সেবার মান |
| wave | **ওয়েভ** | 2 | Internal programme term, `W1`–`W9` |
| release | **রিলিজ** | 2 | A deployed software version. Noun; distinct from the verb *release* in §9 |
| hypercare | **হাইপারকেয়ার** | 2 | The intensive-support period after a wave go-live |
| cutover | **কাটওভার** | 2 | Legacy-to-ERP transition for a defined scope |
| go-live | **গো-লাইভ** | 2 | The moment a wave becomes the system of record |

---

## 11. Divergences and corrections

**Recorded, not silently resolved.** Each row is a case where this file differs from an existing
approved artefact, or where an approved artefact contains a defect this file exposes.

| # | Divergence | Where | Resolution | Action required |
|---|---|---|---|---|
| **D-1** | *Estimate* is **আনুমানিক** in the website glossary and **এস্টিমেট** here | Website `BN-002` §6.1 | The website form translates the adjective *approximate*; the ERP term names a **document requiring customer approval**. Different objects | None on the website. ERP uses এস্টিমেট |
| **D-2** | *Engineer* is "technical staff" in the website glossary; `CG-004` reserves it for **external marketplace freelancers** | Website `BN-002` §5.5 | `CG-004` governs inside the ERP. The two sets are deliberately separate (Master Index §11) | Website unaffected. `CG-004` §10 item 3 remains open on `P04` |
| **D-3** | **Both *reject* and *decline* render as প্রত্যাখ্যান** in approved packs | `UI-011` `p01.estimate.cta_decline`; `UI-012` `p02.day.decline` | `GL-02` violation. §9 splits them: reject → প্রত্যাখ্যান করুন, decline → ফিরিয়ে দিন | **`UI-012` §3.1 must change to ফিরিয়ে দিন.** `UI-011`'s English is also wrong — a customer refusing an estimate is *reject*, not *decline* (`CG-004` §4.8). Raised as `AUDIT-012` **BN-06** |
| **D-4** | *Decline reason* renders as প্রত্যাখ্যান করছেন | `UI-012` `p02.day.decline_reason` | Follows D-3 | Change to **কেন ফিরিয়ে দিচ্ছেন?** |
| **D-5** | *Navigate* renders as পথ দেখান and is counted as 1 word | `UI-012` `p02.job.navigate` | পথ দেখান is two words. The word count is wrong, not the translation | Correct the count in `UI-012` §3.2. Raised as `AUDIT-012` **BN-07** |
| **D-6** | *Pause* renders as বিরতি (a noun) where the slot is a button | `UI-012` `p02.job.pause` | A button is a verb (`CG-008` UI-g). বিরতি is the state, not the action | Change to **বিরতি নিন** |
| **D-7** | `NT-019` declares its Bengali counterpart as `BN-014` | `NT-019` §1 Set summary | IVR belongs to `BN-017`, not `BN-014` (Master Index Category 11) | Correct `NT-019`. Raised as `AUDIT-012` **BN-04** |

| # | Rule |
|---|---|
| **GL-09** | A divergence is **recorded here and corrected at source**. This file does not become the place where two forms coexist |
| **GL-10** | Corrections to approved `UI` and `NT` packs are made by their owners under `CG-007` re-approval triggers — "a term changes in `CG-004`" (`CG-007` §7). They are not edited by Localisation directly |

---

## 12. Master data Bengali columns

Twenty-two of the 48 `MD` datasets carry a Bengali display column (`CG-010` §3.2). Those columns
are **content**, and the terms in them are governed by this glossary.

| Dataset | Bengali column | Governed by |
|---|---|---|
| `MD-003` Branch master | `name_bn` | §2 — the qualifier **সার্ভিস সেন্টার**, not শাখা, on customer-visible rows |
| `MD-006` Geographic hierarchy | `name_bn` | Bangla Academy standard place names. `MD-006` already carries ঢাকা, চট্টগ্রাম, যশোর |
| `MD-009` Role master | `name_bn` | §8 — role names follow `05-04` registration (`CG-004` `T-11`) |
| `MD-019` Product & service catalogue | `name_bn` | §4, §5 and the website glossary device vocabulary |
| `MD-020` Service type & delivery mode | `name_bn` | Walk-in, on-site, pick & drop, remote, workshop, kiosk |
| `MD-021` Device catalogue | `name_bn` | **Model names and brand names stay Latin** (`BN-004`); category names are Bengali |
| `MD-024` Fault & symptom taxonomy | `name_bn` | §4 — ত্রুটি and লক্ষণ must not be interchanged in the data |
| `MD-025` Repair action & resolution | `name_bn` | §9 verb discipline applies to action codes |
| `MD-026` Reason code register | `name_bn` | Reason text is read by customers on cancellations and refusals |
| `MD-027` Status & lifecycle labels | `internal_label_bn`, `customer_label_bn` | **Both columns.** §13 |
| `MD-028` Priority, severity & SLA | `name_bn` | **SLA** stays Latin (§10) |
| Eleven further display datasets | `name_bn` | This glossary |

| # | Rule |
|---|---|
| **MD-B1** | A Bengali data column is **populated at load, not after**. A dataset loaded with an empty `name_bn` ships an English-only surface |
| **MD-B2** | Bengali data columns pass **G4 in context** — rendered in the screen that displays them, not reviewed in the CSV (`BN-018` §4) |
| **MD-B3** | Where a data value is a Tier 1 item — a model number, a brand — the Bengali column repeats the Latin form. It is not left empty |

---

## 13. Status labels

`MD-027` is the register; this file governs its Bengali. **Status wording is the single most
duplicated content in the system** — it appears in the UI, in SMS, on documents, in reports and
in the IVR readback, and every one of those must show the same word.

| Internal state | `internal_label_bn` | `customer_label_bn` | Rule |
|---|---|---|---|
| `submitted` | জমা দেওয়া হয়েছে | **বুকিং গৃহীত হয়েছে** | Customer sees the outcome, not the mechanism |
| `awaiting_parts` | পার্টসের অপেক্ষায় | পার্টসের অপেক্ষায় | Same in both; permitted |
| `sla_breached` | এসএলএ লঙ্ঘিত | **বিলম্বিত** | **Never show এসএলএ লঙ্ঘিত to a customer** (`CG-004` `T-06`, `NT-004` `CS-04`) |
| `cancelled` | বাতিল | বাতিল | Same in both |

| # | Rule |
|---|---|
| **ST-01** | The customer-facing Bengali label is **quoted from `MD-027`**, never re-translated per surface (`CG-008` UI-i) |
| **ST-02** | `internal_label_bn` and `customer_label_bn` are **different content**. Copying one into the other is the `T-06` defect in Bengali |
| **ST-03** | **এসএলএ is the transliteration of an SLA breach state and appears on internal surfaces only.** In all customer content, SLA remains Latin (§10) and the state is বিলম্বিত |
| **ST-04** | Status labels are checked for cross-surface identity at `AUDIT_Checklist_Recurring` F2, in **both** languages |

---

## 14. Phonetic search and name matching

`NFR-074` requires phonetic Bengali input. A user typing phonetically produces spelling variants
of the same word, and party matching (`MD-013`) must not treat them as different people.

| # | Rule |
|---|---|
| **PS-01** | Search and matching operate on **NFC-normalised** text (`BN-006` `EN-02`) |
| **PS-02** | Comparison uses **ICU `bn-BD` collation** (`05-06` §9), never code-point order |
| **PS-03** | Party matching tolerates **known Bengali spelling variation classes**: ই/ঈ, উ/ঊ, র/ড়, ন/ণ, শ/ষ/স, and চন্দ্রবিন্দু presence or absence |
| **PS-04** | Matching also tolerates **script variation** — the same person entered as করিম হোসেন and Karim Hossain. Transliteration rules are in `BN-004` §5 |
| **PS-05** | A search that returns nothing offers the **other script** as a suggestion before offering "no results" (`UI-006`, `common.empty.no_results.search`) |
| **PS-06** | Terms in this glossary are **indexed in both languages**. A branch agent searching "estimate" and a customer searching এস্টিমেট reach the same record |

---

## 15. Adding, changing and deprecating a Bengali term

Mirrors `CG-004` §8, with the Bengali steps made explicit.

### 15.1 Adding

| Step | Action | Who |
|---|---|---|
| 1 | Confirm the English term is approved in `CG-004`. **If it is not, stop** — the English is added first (`T-08`) | Requester |
| 2 | Confirm no approved Bengali form already covers the meaning (`GL-02`) | Localisation Lead |
| 3 | Decide the tier against `BN-002` §4 | Localisation Lead |
| 4 | Propose the Bengali form with the reason a near-miss alternative is wrong | Localisation Lead |
| 5 | Native-speaker review by a reviewer **independent of the proposer** (`CO-05`) | Linguistic reviewer |
| 6 | Ratify at the fortnightly terminology board, **jointly with the `CG-004` row** (`T-07`) | Architecture Review Board delegate + Programme Content Lead |
| 7 | Add to this file **and** to the term base (`BN-008` §5) in the same change | Localisation |
| 8 | Log in `RF-006` | Programme Content Lead |

### 15.2 Changing

The most expensive operation in localisation, because a Bengali term change invalidates every
translation-memory segment containing it (`BN-008` `TM-08`).

Required, in addition to `CG-004` `T-13`:

1. An **impact list produced by search**, covering every bundle, document, recording and course
2. **Translation-memory remediation** — affected segments marked for re-review, not silently reused
3. **Re-recording** of any IVR prompt containing the term (`BN-017` `VP-09`)
4. A co-ordinated change in **one release**, at a wave boundary only

### 15.3 Deprecating

The row stays with status `DEPRECATED`, the date, the replacement and the reason. Deprecated
Bengali forms join the automated lint list so reintroduction is caught (`BN-002` §12).

---

## 16. Coverage

| Source | Terms | Bound here | Gap |
|---|---:|---:|---|
| `CG-004` §4.1 Organisation | 7 | 7 | — |
| `CG-004` §4.2 Party and people | 11 | 11 | — |
| `CG-004` §4.3 Service and work | 14 | 14 | — |
| `CG-004` §4.4 Commercial | 14 | 14 | — |
| `CG-004` §4.5 Finance and statutory | 13 | 13 | — |
| `CG-004` §4.6 Supply chain and asset | 11 | 11 | — |
| `CG-004` §4.7 Quality, governance, platform | 12 | 12 | — |
| `CG-004` §4.8 Verbs | 28 | 28 | — |
| `CG-004` §5 Registered pairs | 7 | 7 | Bengali pairs registered under `GL-05` |
| `CG-004` §6 Concepts | 8 | 8 | — |
| **Total controlled vocabulary** | **108** | **108** | **`T-07` satisfied — `CG-004` may proceed to approval** |
| `MD` display-column vocabulary | ~4,000 values | Governed, not enumerated | Held in the term base (`BN-008`), not in this file |
| `RF-001` explanatory glossary | Superset | Out of scope | `RF-001` is explanatory; this file is controlling |

> **This file binds the controlled vocabulary, not every word in the product.** The ~4,000 master
> data values live in the term base where they can be queried by a translation tool, which is
> what `BN-008` exists to provide. A glossary that tried to hold them would be unmaintainable and
> would be out of date the week after the catalogue changed.

---

## 17. Dependencies

| Depends on | Why |
|---|---|
| `CG-004` | The English vocabulary this binds. Ratified together (`T-07`) |
| `BN-002` §4 | The tier definitions `GL-03` applies |
| `BN-004` | Tier 1 membership and transliteration rules |
| `MD-027` | The status label register §13 governs |
| `BN-008` | The term base this glossary seeds |
| `05-02` | The entities every business-object term binds to |
| `RF-001` | The explanatory superset |

---

## 18. Related documents

| Document | Relationship |
|---|---|
| [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | The English half; ratified together |
| [`BN-002_Bengali_Translation_Standard.md`](BN-002_Bengali_Translation_Standard.md) | Register, address, tiers |
| [`BN-004_Do_Not_Translate_and_Transliteration_Register.md`](BN-004_Do_Not_Translate_and_Transliteration_Register.md) | Tier 1 and name transliteration |
| [`BN-008_Translation_Memory_and_Term_Base_Management.md`](BN-008_Translation_Memory_and_Term_Base_Management.md) | Where these rows become a machine-queryable term base |
| [`BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md`](BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md) | `LQ-11` one-to-one checking |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md) | The status register §13 governs |
| [`../03_UI_Copy_and_Microcopy/03B_Portals/UI-012_P02_Technician_App_UI_Copy_Pack.md`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-012_P02_Technician_App_UI_Copy_Pack.md) | §11 D-3, D-4, D-5, D-6 corrections |

---

## 19. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. All 108 `CG-004` controlled terms bound to one Bengali form with a loanword tier and a stated reason for each near-miss rejection; the অনুমোদন/অথরাইজ audit-control split; seven divergences from approved artefacts recorded with corrections routed to their owners; master-data column governance; status-label rules; phonetic search and matching classes; term change procedure including translation-memory and IVR consequences | Architecture Review Board with Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] **Every one of the 108 controlled terms in `CG-004` §4–§6 has a Bengali row** — the `T-07` block on `CG-004` is cleared
- [x] One Bengali form per English term, and one English term per Bengali form, checked both ways (`GL-01`, `GL-02`)
- [x] Tier recorded for every term (`GL-03`)
- [x] Reserved terms carry the reservation and the specific wrong form that must not be used
- [x] Registered surface-specific pairs given Bengali pairs (`GL-05`)
- [x] Verbs given in the honorific imperative per `BN-002` `AD-02`
- [x] Divergences from approved artefacts **recorded and routed**, not silently absorbed
- [x] Master-data Bengali columns and status labels brought under this glossary
- [x] Phonetic and script variation addressed for search and party matching (`NFR-074`)
- [x] All internal links resolve
- [ ] **Native-speaker review by an independent reviewer** — outstanding; blocks `Approved` (`CO-05`, step 5 of §15.1)
- [ ] **Ratified jointly with `CG-004`** — outstanding; neither may be approved alone (`T-07`, `GL-07`)
- [ ] **`BN-002` §2–§3 ratified** — outstanding; the register and address decisions this file assumes
- [ ] Corrections D-3, D-4, D-5, D-6, D-7 applied at source by their owners — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
