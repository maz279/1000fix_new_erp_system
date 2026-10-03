---
id: EO-001
title: Marketplace Seller Onboarding Kit
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Marketplace Operations
author: Marketplace Operations with Content Design and Localisation
reviewers: [Chief Commercial Officer, Legal Counsel, Chief Financial Officer, Quality Manager, Data Protection Officer, Localisation Lead, Content Design Lead]
approver: Content Design Lead with Marketplace Operations
content_class: D
purpose: >
  The kit a prospective marketplace seller is given to get from "interested" to "first job
  completed and paid". Registration walkthrough, the document set for each seller type,
  what verification actually means and how long it takes, and the first listing and first
  job. Onboarding completion is targeted above 60% of started registrations against a 500-seller
  goal; a registration abandoned at the document-upload step is a seller the marketplace never
  acquires, and drop-off in a nine-stage flow with a T5 document set is a content failure before
  it is a product failure.
traces_to: [P07, M12, M22, M24, M29, M53, 04-00 P07, 05-04 §4 T5, 05-04 §6 SOD-06, 05-04 §8 EA-04, 05-05 §8 BRU-ECM-01, BRU-ECM-07, BRU-ECM-08, BRU-MKP-01, BRU-MKP-09, BRU-MKP-19, BRU-MKP-21, FR-MKP-001, FR-MKP-002, FR-MKP-003, FR-MKP-004, FR-MKP-006, FR-MKP-007, FR-MKP-008, FR-MKP-009, FR-MKP-011, FR-MKP-012, FR-MKP-014, FR-MKP-017, FR-MKP-030, FR-MKP-039, FR-MKP-040, FR-MKP-041, KPI-079, KPI-C12-04, G7-01, MD-011, MD-018, MD-029, MD-038, LG-004, LG-008, SP-024, UI-017, UI-040, HC-009, TR-019, DT-039, NT-012, BN-013, EO-002, EO-011, EO-013, EO-014, CM-015, RP-005]
priority: P1
wave: W7
bilingual: yes
bn_counterpart: EO-001_Marketplace_Seller_Onboarding_Kit_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P07 capability set and the four governance requirements; "seller onboarding completion rate > 60% of started registrations"; 500 approved sellers by end of W8; PS-03, PS-07, PS-09
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md §5.1 FR-MKP-001…016, §8.1 seller lifecycle and transition guards, §9 BRU-MKP-01/09/19/21, §13 field-level restrictions, §16.4 migration rule — "no existing sub-contractor is migrated as an Approved seller"
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §8 BRU-ECM-01, BRU-ECM-07, BRU-ECM-08
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §2.9 KPI-079 500 approved active sellers by W8; §4 Gate 7 G7-01 "200+ approved sellers transacting"
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md §2 required_documents enumeration, §4 SLC-01…SLC-06
    verified: 2026-08-18
    class: P1
  - source: National Board of Revenue (Bangladesh) — the 13-digit e-BIN is the only valid Business Identification Number format; issued through the VAT online portal (vat.gov.bd); a valid TIN is a precondition of applying for a BIN; 9-digit and 11-digit BINs are legally invalid on VAT documents
    verified: 2026-08-18
    class: P2
  - source: Digital Commerce Operation Guidelines 2021 (Ministry of Commerce, Bangladesh) — a marketplace must settle payment to the business owner within ten days after deducting charges and commission; complaints against the platform to be resolved within 72 hours; a compliance officer must be appointed to coordinate with the Directorate of National Consumer Rights Protection
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# Marketplace Seller Onboarding Kit

| Item | Value |
|---|---|
| Audience | Prospective and newly approved marketplace sellers — freelance engineers and shops |
| Population | **500–2,000** (`04-00` P07); **500 approved active** at the `KPI-079` target |
| Portal | `P07` Marketplace Seller Portal & App |
| Language | **Bengali-first**, English toggle (`PS-03`; `M12` design position 5) |
| Issued by | Marketplace Operations (`R24`) |
| Wave | W7 · Months 27–30 (`06-01` §3) |
| Governing procedure | `SP-024` — this kit is its seller-facing counterpart, not a second copy of it |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3),
> all six sections retained in order. The three `CG-009` additions required of every `EO` file —
> **onboarding journey table** (§4.1), **document checklist** (§4.2) and **first-90-days section**
> (§4.7) — are placed inside §4 rather than appended, so §5 and §6 keep their template positions.

---

## 1. Purpose

`04-00` sets one number for P07 that this file exists to move: **seller onboarding completion
above 60% of started registrations**. Everything else about the marketplace is downstream of it.
`KPI-079` wants 500 approved active sellers and `G7-01` will not pass Wave 7 below 200
transacting — and at a 60% completion rate, 500 approved sellers requires roughly **833 started
registrations**; at 30% it requires 1,667.

The seller is not an e-commerce merchant. `M12`'s design position 5 states the constraint
plainly: sellers are *"independent engineers, not e-commerce merchants"*, working in Bengali on a
mid-range Android phone. They are being asked to hand over a National ID, a trade licence, a bank
account and a signed agreement to a company they have not transacted with, before earning
anything.

Three things follow, and they are what this kit is for:

| Absent | Consequence |
|---|---|
| A stated document set per seller type | The seller discovers requirement seven at stage seven, having gathered six. `M12` `FR-MKP-002` makes the flow resumable; it cannot make it predictable |
| A stated meaning and duration for "verification" | Silence after submission is read as rejection. `BRU-ECM-01` makes verification a hard precondition to transacting, so the wait is real and must be named |
| First-listing and first-job guidance | An approved seller who never lists is indistinguishable from one who never registered. `KPI-C12-05` monthly active rate above 70% starts here |

**What this kit is not.** It is not the agreement (`LG-004`), not the screen copy (`UI-017`,
`UI-040`), not the help articles (`HC-009`), not the internal procedure (`SP-024`) and not the
standards handbook (`EO-002`). It is the **issued artefact** — the thing a Marketplace Operations
officer sends, and a seller reads before and during registration.

---

## 2. Scope

**In scope.** The seller-facing onboarding narrative from first contact to first payout: the nine
journey stages; the document and evidence checklist for both seller types; what verification
checks and how long each check takes; the approval outcomes and what each means; agreement
signature; onboarding training; the first listing; the first bid, award and job; the first
statement; and the provisional-to-approved graduation.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| The seller agreement and the policy handbook it incorporates | `LG-004` |
| Standards, scorecard mechanics, thresholds and sanctions | **`EO-002`** — this kit introduces them; `EO-002` states them |
| In-product registration, OTP and document-upload copy | `UI-040` (cross-audience flow), `UI-017` (P07 pack) |
| Help articles, search and troubleshooting | `HC-009` |
| The internal verification, approval and governance procedure | `SP-024` |
| Category qualification requirements and thresholds as data | `MD-018`; certifications `MD-011` |
| Commission rates, fees and bands | `MD-029`; communicated under `EO-011` |
| The payout statement itself | `DT-039` |
| Seller-facing training content and assessment | `TR-019` |
| Notification wording at each stage | `NT-012` |
| Dispute intake, evidence and appeal | **`EO-013`** |
| Offboarding, final settlement and reinstatement | **`EO-014`** |
| **Moving an *existing* sub-contractor or informal counterparty onto `P07`** | **`CM-015`** Vendor and Seller Transition Pack — a one-off change event per wave |
| External-portal dashboard scoping for the seller's own data | `RP-005` |

> **The `CM-015` boundary, stated because both files are about a seller arriving.** `CM-015` owns
> the **transition** — a named existing counterparty moved from email and phone onto the portal,
> once, during a wave. This kit owns **onboarding** — the repeatable admission of any seller,
> before and after that wave, forever. `M12` §16.4 makes the distinction operative rather than
> editorial: **no existing sub-contractor is migrated as an approved seller**, so a `CM-015`
> transition still routes its subject through every stage of §4.1 (`SO-12`).

> **`CP-01` note.** Where this kit states a rule that `LG-004`, `MD-018` or `EO-002` owns, it
> states it **by reference with the owning identifier inline**, never by restatement. A seller
> reading a number here and a different number in the agreement is the failure mode `CP-01`
> exists to prevent, and in a marketplace it is a contractual failure, not an editorial one.

---

## 3. Audience

| Reader | Uses it for | Reads it |
|---|---|---|
| **Prospective freelance engineer** | Deciding whether to start, and what to gather first | Bengali, on a phone, before registering |
| **Prospective shop or business owner** | The business document set, and who signs | Bengali or English, often with an accountant |
| **Newly approved seller** | The first listing, the first bid, the first job, the first statement | Bengali, in the first 30 days |
| **Marketplace Operations officer (`R24`)** | The artefact they issue and the questions they will be asked | English |
| **Contact Centre agent (`R34`)** | Answering seller enquiries without inventing an answer | English + Bengali |
| **Seller acquisition / Marketing (`R23`)** | What can be promised in acquisition material | English |
| **Legal Counsel** | Confirming the kit does not create obligations `LG-004` does not carry | English |

---

## 4. Content

### 4.1 The onboarding journey

Nine stages. **Stages 1–6 are the completion funnel** the 60% target measures; stages 7–9 are
what converts an approved seller into an active one.

| # | Stage | What the seller does | What 1000FiX does | Elapsed target | What stops it |
|---|---|---|---|---|---|
| **1** | **Decide** | Reads this kit; checks the categories they can serve and the areas they cover | Publishes category, area and earning information | — | Categories they want are not open (`MD-018`) |
| **2** | **Register** | Creates an account; verifies phone by OTP and email (`FR-MKP-003`) | Issues OTP; preserves progress across sessions (`FR-MKP-002`) | Same day | Phone number already registered to another seller |
| **3** | **Declare** | Seller type, categories, skills, device brands, service areas, working hours, daily capacity (`FR-MKP-007`) | Validates against `MD-018` and `MD-011` | Same day | A category needing a certification they do not hold (`BRU-ECM-07`) |
| **4** | **Submit documents** | Uploads the §4.2 set for their seller type | Acknowledges receipt; lists anything missing | Same day | **The highest-drop-off stage.** See §4.3 |
| **5** | **Verify payout** | Enters the payout destination — bank, bKash or Nagad (`FR-MKP-006`) | Penny-verification or equivalent check | 1–2 working days | Account name does not match the verified entity (`SP-024` step 3 — **refused**) |
| **6** | **Await decision** | Nothing. This is the stage that must not feel silent | Verification (§4.3), then approval routing (`FR-MKP-011`) | **Target 5 working days**, `O-05` | Document expiry, illegibility, or a verification service outage |
| **7** | **Accept** | Reads and digitally signs the agreement (`LG-004`, `FR-MKP-009`, via `M24`) | Presents the current version and records the signature | Same day | Seller declines a term — **there is no per-seller negotiation** (`SP-024` §4) |
| **8** | **Learn** | Completes platform standards training and acknowledges it (`FR-MKP-012`, `TR-019`) | Assigns the course; blocks first award until complete | 1–3 days | Training not available in Bengali (`O-06`) |
| **9** | **Trade** | First listing, first bid, first job, first statement | Provisional limits applied; closer monitoring | Within 14 days of approval | No broadcast reaches them — a supply/demand problem, not an onboarding one |

**The status the seller is in at every point.** `M12` §8.1 owns the lifecycle; this is the
seller-readable rendering of it, and the words below are the words `UI-017` and `NT-012` must use.

| Lifecycle state | Told to the seller as | Can they earn? |
|---|---|---|
| `REGISTERED` | "Application started" | No |
| `PENDING REVIEW` | "We are checking your documents" | No |
| `REJECTED` | "We cannot approve this application" — with the reason and the reapplication date | No |
| `PROVISIONAL` | "Approved — starter limits apply" | **Yes**, within limits (§4.7) |
| `APPROVED` | "Full seller" | Yes |
| `RESTRICTED` | "Some categories are paused" | Partly — `EO-002` |
| `PROBATION` | "Improvement plan in place" | Yes, monitored — `EO-002` |
| `SUSPENDED` | "You cannot take jobs right now" | No — `EO-002` |
| `EXPIRED` | "A document has run out" | No, until renewed (`BRU-ECM-08`) |
| `OFFBOARDING` / `REMOVED` | Covered by `EO-014` | No |

### 4.2 Document and evidence checklist

Derived from `MD-018` `required_documents`, `M12` `FR-MKP-003`/`004`/`005`/`006` and
`SP-024` §5.1. **Everything in this table is tier `T5` restricted data** (`05-04` §4,
`BRU-MKP-19`): allow-list access, step-up authentication, every access logged. The seller is
told that, because it is the single most common reason a seller hesitates at stage 4.

#### Freelance engineer

| # | Item | Why it is asked | Accepted form | Blocking? |
|---|---|---|---|---|
| 1 | **National ID (NID)** | Identity verification (`FR-MKP-003`) | Photograph of both sides, legible, unexpired | **Yes** |
| 2 | **Live photograph** | Matched to the NID; also the public profile photo (`FR-MKP-015`) | In-app capture | **Yes** |
| 3 | **Mobile number** | OTP-verified; the primary channel for job broadcast | One number, one seller | **Yes** |
| 4 | **Email address** | Statements, agreement copy, formal notice | Verified by link | **Yes** |
| 5 | **e-TIN** *(where the seller holds one)* | Withholding treatment on earnings (`FR-MKP-074`) | e-TIN certificate | Conditional — `O-02` |
| 6 | **Payout destination** | Bank account, bKash or Nagad, **in the seller's own name** | Statement header or account screenshot + penny verification | **Yes** |
| 7 | **Service-area declaration** | Broadcast matching (`FR-MKP-028`) | Selected from `MD-006` geography | **Yes** |
| 8 | **Category certifications** | Only where `MD-018` requires them (`BRU-ECM-07`) | Certificate resolving in `MD-011` | Conditional |
| 9 | **References** | Verification depth (`FR-MKP-005`) | Two contactable references | No — affects standing, not admission |
| 10 | **Work samples** | Verification depth; also listing quality | 3–10 photographs of completed work | No |

#### Shop or business

Items 1–10 above **for the signing individual**, plus:

| # | Item | Why it is asked | Accepted form | Blocking? |
|---|---|---|---|---|
| 11 | **Trade licence** | Business existence and lawful trade | Current licence, unexpired, matching the trading name | **Yes** |
| 12 | **e-TIN** | Business tax identity | e-TIN certificate | **Yes** |
| 13 | **13-digit e-BIN** *(where VAT-registered)* | VAT treatment of commission and earnings | **13-digit** BIN issued through the NBR VAT online portal. **9- and 11-digit BINs are not accepted** — they are no longer valid on VAT documents | Conditional on VAT registration |
| 14 | **Business bank account** | Payout destination in the business's name | Account in the licensed trading entity's name | **Yes** |
| 15 | **Premises evidence** | Address verification; also customer-facing shop information | Photograph of the premises with signage | No |
| 16 | **Authority to sign** | The individual signing binds the business (`LG-004` §2) | Named on the licence, or a written authority | **Yes** |

> **The e-BIN rule matters more than its position in the table suggests.** A TIN must exist
> *before* a BIN can be applied for, so a seller who has neither cannot obtain a BIN in the
> registration window. **The kit must therefore not present the e-BIN as a same-day item.** Where
> the principal/agent determination (`M12` Q-01) lands on 1000FiX as agent, the commission is the
> VAT-bearing supply and the seller's own BIN status changes what the seller must issue — which is
> why `O-01` treats that determination as blocking for this kit, not only for the settlement build.

#### What we do not ask for, and say so

`LG-008` and PDPA 2026 minimisation make the omissions worth stating explicitly, because sellers
are asked for these by other platforms and assume we want them too:

- No NID of family members, no photograph of the seller's home, no social-media accounts.
- **No security deposit is collected at registration.** Whether one is required at all is `M12`
  Q-03, undecided — `O-03`.
- No exclusivity. A seller may work for anyone; `LG-004` §4.3 governs conduct on *our* jobs only.

### 4.3 What verification means, and how long each check takes

Stage 6 is where an unmanaged expectation becomes an abandoned application. The kit states the
mechanism, not a reassurance.

| Check | What is actually checked | Owner | Working days | If it fails |
|---|---|---|---|---|
| Identity | NID against the issuing service; photograph against the NID (`INT-MKP-01`) | `R24` | 1–2 | Re-upload once; a second failure ends the application with a stated reapplication window |
| Business existence | Trade licence, TIN and BIN validity (`INT-MKP-02`) | `R24` | 1–3 | Correctable; the application waits rather than closing |
| Payout ownership | **That the account belongs to the verified entity** | `R24` → `R26` | 1–2 | **Refused, not corrected** (`SP-024` §6). This is the standard payout-fraud pattern |
| Category qualification | Assessment against `MD-018`; certification against `MD-011` | `R24` with `M22` | 1–3 | The category is withheld; the rest of the application proceeds |
| Brand-authorised categories | Whether the category needs a certification 1000FiX holds and the seller does not | `R24` | 1 | **Category refused.** `BRU-MKP-09` — warranty work under a brand authorisation is never broadcast to the marketplace, by any route |
| Approval decision | `FR-MKP-011` routing, with recorded reason | `R24` | 1 | See outcomes below |

**Approval outcomes, and what each one means to the seller.**

| Outcome | What it means | What happens next |
|---|---|---|
| **Provisional** | Approved with limits — the normal outcome for a new seller | §4.7 graduation |
| **Approved** | Full standing | Rare at first application; reached by graduation |
| **Rejected** | Application refused with a recorded reason (`FR-MKP-011`) | A stated reapplication window, and what would need to change |
| **Held** | Something is missing or unreadable | Named item, one action, no re-submission of the whole application |

> **Two people, never one.** Approving a seller and approving that seller's payout is a hard
> segregation (`SOD-06`, `BRU-MKP-03`). Sellers are told this, because it is the answer to
> "can my Operations contact just release my money?" — and the answer is no, by design.

### 4.4 The first listing

A listing is the seller's shopfront and the first thing they control.

| Step | What good looks like | Rule |
|---|---|---|
| Choose the category | Only categories the seller is qualified in appear | `BRU-ECM-07` hard block |
| Title and description | Bengali first; plain; states scope and what is excluded | `UI-017`, `VB-002` |
| Set the price | **The seller sets it.** 1000FiX does not price seller listings | `M12` §3.2 — M11 prices only our own fees |
| Declare availability and area | Drives matching and, later, acceptance rate | `FR-MKP-016` |
| Product listings | Seller-owned parts only; condition and warranty declared | `FR-MKP-018`, `FR-MKP-019` |
| Submit for moderation | Automated screening first; only exceptions reach a human | `FR-MKP-020` |

**Three ways a first listing fails moderation**, stated because they account for most rejections:

1. **A prohibited or unauthorised item** — counterfeit or non-genuine parts, or a category needing
   an authorisation the seller lacks (`FR-MKP-021`). A counterfeit finding is not a moderation
   outcome; it suspends the listing and the seller pending investigation (`BRU-MKP-11`).
2. **A price materially outside the category norm** — flagged for review, not corrected.
   1000FiX does not set the price; it asks whether the seller meant it (`FR-MKP-024`).
3. **Contact details in the listing text** — the platform masks contact exchange
   (`FR-MKP-046`, `T-10`), and putting a phone number in a description is the first
   disintermediation signal (`FR-MKP-064`).

### 4.5 The first job

| Step | What happens | What the seller must know |
|---|---|---|
| **Broadcast** | An eligible job is published to matching sellers within a declared window (`FR-MKP-028`) | Ranking is computed from declared, auditable factors and is reconstructible (`BRU-MKP-22`). It is not arbitrary and it is not for sale — **paid boost never overrides a quality restriction** (`BRU-MKP-12`) |
| **Bid** | Price, ETA and scope; revisable inside the window (`FR-MKP-030`) | A bid is an offer. Non-acceptance after award is recorded against the score (`AUT-MKP-07`) |
| **Award** | By customer choice, rule or operator decision, basis recorded (`FR-MKP-032`) | The acceptance window is short and lapsing re-awards automatically (`FR-MKP-033`) |
| **Customer data** | Name, contact and address are released **on award only**, and revoked a defined period after completion (`FR-MKP-038`, `EA-04`) | Retaining or re-using customer contact details after that window is a data-protection breach, not a policy preference (`SP-024` §8) |
| **Execute** | Job workspace with checklist, evidence capture and time recording, offline-tolerant (`FR-MKP-039`) | — |
| **Evidence** | **The same before/after photographs, diagnostic record and QC checklist as a 1000FiX technician's job. Completion is blocked without them** (`FR-MKP-040`, `BRU-ECM-03`) | This is the single most important sentence in the kit. See §4.6 |
| **Sign-off** | Customer verification, signature or OTP (`FR-MKP-041`) | No sign-off, no completion, no earning |
| **Escalate** | Seller or customer can escalate live to 1000FiX, with takeover (`FR-MKP-044`) | Escalating is not a failure; not escalating is |

### 4.6 Why the standard is the same as ours

Stated once, in the kit, in the seller's own interest — because a seller who believes marketplace
standards are lighter will discover otherwise at their first blocked completion.

> **`04-00` P07 governance requirement 2, and `BRU-ECM-03`: quality and evidence standards for
> marketplace jobs are identical to owned jobs.** The customer books 1000FiX. They do not
> experience a marketplace; they experience a repair. `M12`'s category risk register rates
> marketplace quality failure as **Critical**, because 1000FiX's business rests on 17+
> manufacturer authorisations that a brand can withdraw.

What that means concretely for a seller: the evidence pack is not paperwork, it is the seller's
own defence in a dispute (`EO-013`); a job completed without it cannot be paid; and 1000FiX
remedies the customer first and recovers from the seller second (`BRU-MKP-20`) — which is
generous in the moment and is why recovery exists at all.

### 4.7 The first 90 days

Provisional standing is not probation. It is the period in which the platform learns whether the
seller's declared capability is real, and the seller learns whether the platform pays.

| Days | Seller milestone | Platform milestone | Measured by |
|---|---|---|---|
| **0–7** | Agreement signed, training complete, profile and first listing live | Access provisioned; provisional limits applied (`AUT-MKP-03`) | Listing live within 7 days |
| **8–30** | First bid, first award, first completed job with full evidence, first review | First statement issued (`DT-039`); hold period explained before it is experienced | **Evidence compliance 100%** — `KPI-C12-09` admits no lower number at W9 |
| **31–60** | Sustained acceptance and on-time rates; second and third categories if qualified | Score components become visible to the seller (`FR-MKP-056`) | Acceptance and on-time rates |
| **61–90** | **Graduation review** | Provisional → Approved on the `M12` §8.1 guard: minimum completed jobs, minimum rating, full evidence compliance, no upheld disputes | Standing change with notice |

**Provisional limits.** `M12` §8.1 defines provisional standing as "limited job value, closer
monitoring", and `MD-018` holds `max_open_jobs` per category. **The actual values are
unconfigured** — `O-04`. The kit states the *mechanism* and marks the numbers as "set at
launch", which is honest and is also the only thing it can do before configuration.

**The first payout is the moment the relationship is decided.** `DT-039` carries the statement;
this kit sets the expectation around it: the hold period from `MD-018` `payout_hold_days`, the
absolute block while any dispute is open (`SLC-04`, `BRU-BIL-03`), and the payout schedule for
the seller's tier. **`O-01` records that a configurable hold may not be lawful** against the
ten-day settlement obligation in the Digital Commerce Operation Guidelines 2021.

### 4.8 Rules

| # | Rule |
|---|---|
| **SO-01** | The kit states the document set **per seller type, in full, before stage 2**. A requirement revealed mid-flow is a defect against the 60% target |
| **SO-02** | Every blocking item is marked blocking. A seller must be able to tell what stops the application from what merely improves it |
| **SO-03** | The three preconditions to transacting — documents verified, agreement signed, administrator approved — are stated together, in that order, wherever approval is described (`BRU-ECM-01`) |
| **SO-04** | Evidence parity with owned jobs is stated **once as a headline and never softened**. No formulation such as "wherever practical" is permitted (`BRU-ECM-03`) |
| **SO-05** | The kit never states a commission rate, fee or threshold value. It names the owning register — `MD-029` for rates, `MD-018` for thresholds — and `EO-011` for how changes are communicated |
| **SO-06** | Payout destination ownership failure is described as **refusal**, not as an error to correct (`SP-024` §6) |
| **SO-07** | Personal and business documents are described as restricted-tier data with logged access, in the seller's own words (`BRU-MKP-19`, `05-04` §4) |
| **SO-08** | Customer data is described as **granted on award and revoked after completion**, with the consequence of retention stated (`EA-04`) |
| **SO-09** | The kit never promises a job volume, an income, or a broadcast frequency. Supply-side promises the demand side cannot honour are the fastest route to seller churn |
| **SO-10** | Every lifecycle state has one seller-facing name, used identically in `UI-017`, `NT-012` and `HC-009` (§4.1 table) |
| **SO-11** | Rejection is always accompanied by a reason and a reapplication window (`FR-MKP-011`) |
| **SO-12** | No existing sub-contractor is presented as pre-approved. **Every seller completes KYC, signature and training through the platform** (`M12` §16.4 migration rule) |
| **SO-13** | Bengali is the source language for seller-facing delivery of this kit; the English is the governing text for meaning (`CG-010` §4). Machine translation is prohibited (`CP-05`) |
| **SO-14** | The kit is issued at the agreement version in force; a material agreement change requires re-acceptance (`FR-MKP-009`) and a kit re-issue |
| **SO-15** | Where a figure is unconfigured, the kit says "set at launch" and names the register that will hold it. It never estimates |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`LG-004`](../10_Legal_Policy_and_Compliance/LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md) | The agreement signed at stage 7; every obligation this kit describes must resolve there |
| [`EO-002`](EO-002_Seller_Standards_Scoring_and_Sanctions_Handbook.md) | Standards, scorecard and sanctions — introduced here, owned there |
| [`MD-018`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md) | Required documents, category thresholds, `max_open_jobs`, `payout_hold_days` |
| [`MD-011`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Certifications gating categories |
| [`MD-029`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md) | Commission bands and fees |
| [`MD-038`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md) | Payment methods and the payout destinations accepted |
| `M12` §5.1, §8.1 | The registration features and the lifecycle this kit renders |
| [`SP-024`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-024_SOP_Marketplace_Seller_Onboarding_and_Governance.md) | The internal procedure; §7 authority limits must reconcile with what the kit promises |
| [`UI-017`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-017_P07_Marketplace_Seller_Portal_UI_Copy_Pack.md), [`UI-040`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-040_Registration_and_Onboarding_Flow_Copy.md) | The in-product copy the kit must not contradict |
| [`HC-009`](../09_Help_Centre_and_Self_Service/09A_Help_Sets_By_Portal/HC-009_Help_Set_P07_Marketplace_Seller_Portal.md) | Help articles for everything the kit introduces |
| [`TR-019`](../08_Training_and_Enablement/08B_Course_Packs/TR-019_Course_Pack_Marketplace_and_Seller_Operations.md) | The training completed at stage 8 |
| [`NT-012`](../04_Notification_and_Messaging/04C_Email/NT-012_Email_Template_Library_Seller_and_Partner.md) | Stage-change notifications |
| [`DT-039`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-039_Marketplace_Seller_Payout_Statement.md) | The first statement |
| [`BN-013`](../11_Localisation_Bengali/BN-013_Bengali_String_Bundle_P07_to_P12.md) | The Bengali string set for P07 surfaces |
| [`EO-011`](EO-011_Rate_Card_and_Pricing_Communication_Pack.md), [`EO-013`](EO-013_Ecosystem_Dispute_Resolution_Content.md), [`EO-014`](EO-014_Ecosystem_Offboarding_and_Exit_Content.md) | Price change, dispute and exit — the three things a seller will need that this kit does not own |

> **Rule-citation attribution.** **BRU-MKP-\*** → `M12` §9 — this is a **module-scoped** rule family and **`05-05` carries none of it**. The family this file cites that **does** resolve in `05-05` is `BRU-ECM-*`. Stated per `AUDIT-015` R-11, which asked that the convention be recorded once rather than rediscovered by each extraction.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly during W7–W8 while the funnel is being tuned; annually thereafter |
| Trigger for out-of-cycle review | A material change to `LG-004`; a change to `MD-018` required documents or thresholds; the principal/agent determination landing; a completion-rate drop of more than 5 points in a month; a change to the NBR e-BIN or e-TIN requirement; a `P07` release that changes the registration flow |
| Owner | Marketplace Operations, with Content Design for the funnel and Localisation for the Bengali |
| Change control | Any change that alters what a seller is asked to provide, or what they are told about money, requires CCO sign-off and a re-issue — not a silent edit |
| Effectiveness measure | Completion rate by stage (`KPI-C12-04`), and the drop-off share at stage 4 specifically |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **A configurable payout hold may conflict with a statutory settlement deadline.** The Digital Commerce Operation Guidelines 2021 require a marketplace to settle payment to the business owner **within ten days** after deducting charges and commission. `M12` `FR-MKP-071` and `MD-018` `payout_hold_days` model an open-ended, configurable hold, and `SLC-04`/`BRU-BIL-03` block payout entirely while a dispute is open — **with no stated maximum**. Either the guidelines do not apply to a service marketplace of this shape, or the hold and dispute-block design needs a lawful ceiling. **This kit cannot state a hold period until it is resolved.** The source here is authoritative secondary (`class: P2`); `CG-012` `EV-01` would require a primary instrument if this file were Class A, and the exposure is the same one audit `00-07` H2-13 recorded for tax figures resting on press reporting | **Legal Counsel with CFO**, external adviser | **W6 — before the first seller is told a hold period** |
| **O-02** | **The principal/agent determination is undecided** (`M12` Q-01, `BRU-MKP-15`, risk `RSK-022`). It determines whether commission or gross value is the VAT-bearing supply, what the seller must issue, whether the seller's own e-BIN is required, and what withholding applies to earnings (`FR-MKP-074`). **§4.2 items 5 and 13 and the whole of §4.7's payout expectation are provisional until it lands** | CFO / CEO with external counsel | **W6 — blocking, three months before build** |
| **O-03** | **Whether a security deposit is required is undecided** (`M12` Q-03). §4.2 currently tells sellers no deposit is collected. If that changes it changes the acquisition proposition materially, and the kit will have said the opposite to every seller onboarded before the change | CFO / CCO | W7 build |
| **O-04** | **Provisional limits, graduation criteria and `max_open_jobs` are unconfigured.** `MD-018` §6 states the thresholds are "initial estimates" with "no precedent — the marketplace does not exist yet" and must be recalibrated after the first quarter. §4.7 therefore describes a mechanism with no numbers | CCO with Marketplace Operations | **W7 — before first approval** |
| **O-05** | **No decision service level is set for stage 6.** §4.1 states a five-working-day target derived from the sum of §4.3's individual checks; **no programme document commits to it.** `KPI-C40-12` sets partner onboarding cycle time at under 10 days for `M40`, and `M12` has no equivalent. A funnel target of 60% with an uncommitted decision time is not a managed funnel | Marketplace Operations with CCO | **W7 — before launch** |
| **O-06** | **Bengali authoring and translation for this kit is unresourced.** `CP-05` prohibits machine translation on field-facing content, `SO-13` makes Bengali the delivery language, and `TR-019`'s Bengali standing is the same open question. `CG-002` records that no Localisation Lead is appointed | Localisation Lead *(unappointed)* with Programme Content Lead | **W7 minus 6 weeks** (`CG-002` §7 escalation trigger) |
| **O-07** | **`SP-024` cites the wrong identifiers for two of this kit's dependencies.** It names `LG-018` as the Marketplace Seller Agreement in five places — `LG-018` is E-Waste, EPR and Environmental Compliance; the agreement is **`LG-004`** — and names **`EO-006`** as the "Marketplace Seller Onboarding Pack", which is the Supplier Performance Scorecard Explanation; this file is **`EO-001`**. Both must be corrected in `SP-024`, not mirrored here | Programme Content Lead with Business Process Lead | **W1 — before `SP-024` is trained** |
| **O-08** | **Background-check scope is undecided** (`M12` Q-06): whether verification beyond NID is required for sellers entering customers' homes, and where liability sits if it is not done. §4.2 asks for NID, references and work samples and **no background check**, which is a position this file has taken by default rather than by decision | Legal / CCO | **W7 — blocking** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the three `CG-009` `EO` additions placed inside §4 and the placement justified
- [x] Nine-stage journey table with elapsed targets and the specific blocker at each stage
- [x] Document checklist split by seller type, every item marked blocking or not, with the reason it is asked
- [x] **The 13-digit e-BIN stated correctly, with the TIN precedence that makes it not a same-day item**
- [x] Verification described as a set of named checks with durations and failure behaviour, not as a reassurance
- [x] Every lifecycle state given one seller-facing name for `UI-017`, `NT-012` and `HC-009` to share
- [x] **Evidence parity stated as a headline and not softened anywhere in the file** (`SO-04`)
- [x] First-90-days section with the graduation guard taken from `M12` §8.1
- [x] Fifteen rules stated, including the prohibition on quoting rates, thresholds or income
- [x] `CP-01` boundaries stated against `LG-004`, `EO-002`, `UI-017`, `UI-040`, `HC-009`, `SP-024`, `DT-039`, `TR-019`, `MD-018`
- [x] All internal links resolve
- [x] Eight open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` statutory settlement deadline unresolved — outstanding; the kit cannot state a hold period**
- [ ] **`O-02` principal/agent determination undecided — outstanding; §4.2 and §4.7 provisional**
- [ ] **`O-04` provisional limits unconfigured — outstanding; §4.7 has a mechanism and no numbers**
- [ ] **`O-05` no decision service level committed — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Named approver recorded — **pending Content Design Lead with Marketplace Operations**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
