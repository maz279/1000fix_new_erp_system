---
id: EO-009
title: Referral and Alliance Partner Kit
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Partnerships
author: Partnerships with Content Design and Localisation
reviewers: [Chief Commercial Officer, Chief Financial Officer, Legal Counsel, Data Protection Officer, Marketing Manager, Head of Sales, Localisation Lead, Content Design Lead]
approver: Content Design Lead with Partnerships
content_class: D
purpose: >
  The kit issued to a referral or alliance partner covering enrolment, how referral links and
  codes work, how a lead is submitted with the customer's consent, exactly how attribution is
  decided and when it lapses, and how commission is earned, stated and paid. Referral-attributed
  customers are targeted above 12% of new customers with more than 200 active partners; partners
  only refer volume into a scheme whose attribution they trust, and attribution is the one
  mechanic that cannot be explained after the first disputed commission.
traces_to: [P12, M40, M07, M10, M11, M20, M33, M53, M35, M24, M29, 04-00 P12, 05-04 §8 EA-01, EA-02, EA-11, FR-PCM-005, FR-PCM-006, FR-PCM-007, FR-PCM-008, FR-PCM-009, FR-PCM-010, FR-PCM-022, FR-PCM-023, FR-PCM-024, FR-PCM-025, FR-PCM-026, FR-PCM-027, FR-PCM-028, FR-PCM-029, FR-PCM-030, FR-PCM-031, FR-PCM-032, FR-PCM-041, FR-PCM-042, BRU-PCM-01, BRU-PCM-04, BRU-PCM-05, BRU-PCM-06, BRU-PCM-09, BRU-PCM-10, BRU-PCM-12, BRU-PCM-13, BRU-PCM-14, BRU-PCM-15, BRU-PCM-19, KPI-035, KPI-C40-01, KPI-C40-02, KPI-C40-03, KPI-C40-04, KPI-C40-10, KPI-C40-12, MD-013, MD-029, MD-034, MD-038, LG-007, LG-008, DT-040, UI-022, UI-040, HC-014, NT-012, EO-011, EO-012, EO-013, EO-014, CM-002, CM-015, AP-001]
priority: P2
wave: W7
bilingual: yes
bn_counterpart: EO-009_Referral_and_Alliance_Partner_Kit_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P12 Partner & Referral Portal capability set (onboarding, referral, benefits, earnings, co-marketing, reseller, performance); users "alliance partners, referral partners, corporate resellers" 100–500; KPIs "active referral partners > 200 by end of W8", "referral-attributed new customers > 12% of new customers", "partner commission accuracy 100%", "partner portal adoption > 75% of approved partners"; Wave W7
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md §5.3 FR-PCM-022…032 referral links and codes, lead submission with customer consent captured, attribution model with a defined window, lead-to-opportunity handoff preserving attribution, lead status visibility, deal registration with conflict detection, protection period, channel conflict rules, alliance scheme definition, member eligibility validation, volume commitment tracking; §6 T-02 attribution durability, T-03 window enforcement, T-07 referral link integrity, T-12 consent on partner-submitted leads
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md §9 BRU-PCM-04 attribution written at lead creation and immutable through to revenue, BRU-PCM-05 a lead converting outside its window attributes to no partner, BRU-PCM-06 recorded customer consent required before the record is created, BRU-PCM-09 conflicts decided never auto-approved, BRU-PCM-14 a partner sees only their own records, BRU-PCM-15 outstanding commission settled before Exited, BRU-PCM-19 alliance benefits applied by M11; §18 Q-03, Q-04, Q-07, Q-09
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §2.4 KPI-035 referral-attributed new customers 0% baseline, 6% at W4, 12% at W8 — source column "M10"
    verified: 2026-08-18
    class: P1
  - source: project_content/10_Legal_Policy_and_Compliance/LG-007_Referral_and_Alliance_Partner_Agreement.md §4.2 attribution as the operative clause; §4.6 consent and personal data in a Lead; §4.8 conflicts, deal registration and channel precedence, marked pending its own open items
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Referral and Alliance Partner Kit

| Item | Value |
|---|---|
| Audience | Referral partners, alliance partners (insurers, telcos, banks, benefit schemes, retailers), corporate resellers |
| Population | **100–500** portal users; **> 200 active partners** targeted by end of W8 |
| Portal | `P12` Partner & Referral Portal |
| Language | **Bilingual** — individual referrers and small-business partners read Bengali |
| Issued by | Partnerships, at enrolment |
| Wave | W7 · Months 27–30 |
| Target this kit serves | **Referral-attributed new customers > 12%** (`KPI-035`, `KPI-C40-02`) |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The three `EO` additions appear as §4.1 (**journey** — enrolment to first
> payout), §4.3 (**checklist** — enrolment documents and what a valid lead must contain) and §4.8
> (**first 90 days**). Template 15 `TPL_Onboarding_Kit.md` does not exist.

---

## 1. Purpose

A referral programme has one currency and it is not money. It is **belief in the attribution**.

`M40`'s design position says why: a partner sends a customer to 1000FiX and then loses sight of
them. Everything after that moment — whether the customer converted, whether the conversion was
credited, and whether the commission is right — happens inside our systems, where the partner
cannot look. `KPI-C40-02` wants referral-attributed customers above 12% of all new customers, and
no partner sends their second referral into a scheme whose first referral disappeared.

`M40` builds the mechanism for that belief and this kit is what makes it legible:

| Mechanism | Rule | What the partner needs to be told |
|---|---|---|
| Attribution is written **at lead creation** and is immutable through opportunity, quotation, order and revenue | `BRU-PCM-04`, `T-02` | Their credit is fixed the moment the lead exists — not recomputed later from inference |
| A lead converting **outside its window** attributes to **no partner** | `BRU-PCM-05`, `T-03` | Not to a different partner, and not to direct sales. The window is real and it is symmetric |
| A partner-submitted lead **cannot be created without recorded customer consent** | `BRU-PCM-06`, `T-12` | The partner has an obligation before the referral, not after |
| Conflicts are **decided, never auto-approved** | `BRU-PCM-09` | A registered deal is a decision they can see the basis of |
| Every partner sees **only their own records** | `BRU-PCM-14`, `EA-01`, `EA-11` | Their pipeline is not visible to another partner |

**What this kit is not.** It is not the partner agreement (`LG-007`), not the co-marketing asset
guide (**`EO-012`**), not the screen copy (`UI-022`, `UI-040`), not the help set (`HC-014`), not
the commission statement (`DT-040`), and not the customer-to-customer referral mechanic, which is
loyalty and belongs to `M10`.

---

## 2. Scope

**In scope.** Partner types and which mechanics apply to each; enrolment, qualification and
approval; the agreement and portal provisioning; referral links and codes — how they work, how
they are protected, and how they are revoked; lead submission, including the consent obligation;
the attribution model, its window, and the four ways attribution is lost; lead status visibility;
deal registration, conflict detection and the protection period; channel precedence; alliance
scheme mechanics and member eligibility; commission earning, statement and payout; the reseller
variant; performance and tiering; and the first 90 days.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| The partner agreement, its liability and termination terms | `LG-007` |
| Approved marks, materials, co-branded campaigns and the approval route | **`EO-012`** |
| Marketplace seller onboarding — **a seller is not a partner** | **`EO-001`**; `BRU-PCM-02` |
| Franchise model, territory, royalties and standards | **`EO-010`** |
| Customer-to-customer referral and loyalty rewards | `M10`; `MD-034` |
| Commission **rates** and benefit schedules | `MD-029`; `M11` applies alliance benefits (`BRU-PCM-19`); change communication **`EO-011`** |
| Commission **calculation and payout execution** | `M53` / `M52`; `M40` defines the programme |
| The commission statement document | `DT-040` |
| Campaign execution | `M35` |
| Screens, flow copy, help, notifications | `UI-022`, `UI-040`, `HC-014`, `NT-012` |
| Disputes about a partner's commission or standing | **`EO-013`** |
| Exit, final settlement of commission and link revocation | **`EO-014`** |

---

## 3. Audience

| Reader | Uses it for | Language |
|---|---|---|
| **Individual referral partner** | Enrolment, link mechanics, what earns commission | **Bengali** |
| **Small-business referral partner** | The same, plus tax and payout details | **Bengali** |
| **Alliance partner scheme manager** (insurer, telco, bank, retailer) | Scheme definition, member eligibility, volume commitments | English |
| **Corporate reseller** | Allocation, ordering, settlement | Either |
| **Partner finance contact** | Commission statement, payout schedule, deductions | Either |
| **1000FiX Partnerships lead** | The kit they issue and the mechanics they must not misstate | English |
| **1000FiX Sales / account manager** | Channel precedence, so a partner-introduced customer is not re-claimed as direct | English |

---

## 4. Content

### 4.1 The enrolment journey

| # | Stage | Partner does | 1000FiX does | Target | Exit condition |
|---|---|---|---|---|---|
| **1** | **Apply** | Applies through `P12` or by introduction, in a staged, resumable, bilingual flow (`FR-PCM-005`) | Acknowledges | Day 1 | Application complete |
| **2** | **Qualify** | Supplies the §4.3 documents | Qualifies against the programme's entry criteria; records the reason for the decision (`FR-PCM-006`) | Day 2–5 | Qualified or refused with a reason |
| **3** | **Agree** | Signs the partner agreement (`LG-007`) through `M24` | Links it; **transacting is blocked until it is executed** (`FR-PCM-008`, `BRU-PCM-01`) | Day 5–7 | Agreement executed |
| **4** | **Onboard** | Completes the programme checklist — contacts, banking, tax registration, training | Drives the checklist (`FR-PCM-007`) | Day 7–9 | Checklist complete |
| **5** | **Enable** | Named contacts complete portal access | Provisions `P12` on approval; **revokes automatically on exit, expiry or suspension within one hour** (`T-11`, `BRU-PCM-13`) | Day 9–10 | Partner signed in |
| **6** | **Equip** | Generates referral links and codes | Issues them, signed and revocable (`FR-PCM-022`, `T-07`) | Day 10 | First link live |
| **7** | **Refer** | Submits the first lead, **with consent** (`FR-PCM-023`) | Attributes it at creation (`BRU-PCM-04`) | — | Lead visible to the partner with a status |
| **8** | **Convert** | Watches the status (`FR-PCM-026`) | Converts to an `M07` opportunity, preserving attribution (`FR-PCM-025`) | — | Conversion or loss, with a reason |
| **9** | **Earn** | Reviews the statement | Issues the commission statement (`DT-040`); pays per the programme schedule | — | First payout reconciled by the partner |

**`KPI-C40-12` targets a partner onboarding cycle under 10 days**, falling from 21. Stages 1–6 are
that cycle; the kit is what makes ten days achievable without a person chasing each stage.

### 4.2 Partner types — and which mechanics apply

`M40` types are the register's; this is what each type actually does.

| Type | Brings | Mechanics that apply | Mechanics that do not |
|---|---|---|---|
| **Referral partner** | Individual leads for commission | Links and codes, lead submission, attribution, commission | Deal registration, scheme eligibility, allocation |
| **Alliance partner** | A member base — policyholders, subscribers, cardholders, employees | Scheme definition, member eligibility, benefit schedule, volume commitments | Individual attribution per lead, usually |
| **Corporate reseller** | Onward sale of refurbished stock or services | Allocation, reseller pricing, ordering, settlement | Referral commission on the same transaction |
| **Alliance + referral** | Both | Both, with a stated precedence between them | — |

> **A marketplace seller is not a partner** (`BRU-PCM-02`), and `M40` Q-09 asks whether a person
> may be both. Until that is answered, the kit states the rule and flags the case — `O-05`.

### 4.3 The enrolment checklist

#### Documents

| # | Item | Individual partner | Business / alliance partner | Why |
|---|---|:--:|:--:|---|
| 1 | Identity — NID | **Yes** | For the signatory | Party identity (`MD-013`) |
| 2 | Trade licence | — | **Yes** | Business existence |
| 3 | e-TIN | Where held | **Yes** | Withholding on commission |
| 4 | 13-digit e-BIN | — | Where VAT-registered | Tax treatment of commission |
| 5 | Payout destination — bank, bKash or Nagad, **in the partner's own name** | **Yes** | **Yes** | Commission payment (`MD-038`) |
| 6 | Named contacts — commercial, finance, escalation | Self | **Yes** | `FR-PCM-009` |
| 7 | Authority to sign | — | **Yes** | Binds the entity |
| 8 | Programme training and policy acknowledgement | **Yes** | **Yes** | `FR-PCM-041` gates programme benefits on it |
| 9 | Alliance scheme definition — member base, eligibility rules, validation method | — | Alliance only | `FR-PCM-030` |
| 10 | Volume commitment, where the programme carries one | — | Where applicable | `FR-PCM-032` |

#### What a valid lead must contain

**This is the checklist that decides whether a partner gets paid**, and it is short by design.

| # | Element | Required | Why |
|---|---|:--:|---|
| 1 | Customer name and contact | **Yes** | The lead is a person |
| 2 | **Recorded customer consent to the referral** | **Yes — the record cannot be created without it** | `BRU-PCM-06`, `T-12`, PDPA 2026; `LG-007` §4.6 |
| 3 | What the customer needs | **Yes** | Routing and qualification |
| 4 | Location or preferred branch | **Yes** | Coverage |
| 5 | The partner's link, code or portal submission | **Yes** | The attribution key |
| 6 | Any scheme membership reference | Alliance only | `FR-PCM-031` eligibility validation |

> **Consent is the partner's obligation and the kit is blunt about it.** A partner who submits a
> customer's details without that customer's knowledge has created a personal-data breach in our
> system, using our form. §4.4 states what consent must cover and what the partner must be able to
> show.

### 4.4 Consent — what the partner must obtain

| Requirement | What it means |
|---|---|
| **Before submission** | Consent is obtained from the customer *before* the lead is created, not sought afterwards |
| **Specific** | The customer knows their details are being passed **to 1000FiX**, for a **service enquiry**, by **that partner** |
| **Recorded** | The partner can show when and how it was given |
| **Withdrawable** | The customer may withdraw; the partner tells us, and the lead is handled under `LG-008` |
| **Not bundled** | Consent to a partner's own terms is not consent to a referral |

**What we do with it.** The consent record is captured with the lead (`FR-PCM-023`), the customer
is contacted by 1000FiX, and the customer's own privacy rights from that point are governed by
`LG-008` and `M33`. **A partner does not receive the customer's subsequent transaction history** —
they see the lead's status (`FR-PCM-026`), not the customer's account.

### 4.5 Attribution — the operative mechanic

Written plainly, once, because `LG-007` §4.2 calls attribution *"the operative clause"* and every
commission dispute is an attribution dispute.

| Rule | Statement |
|---|---|
| **When it is decided** | **At lead creation.** Not at conversion, not at invoice (`BRU-PCM-04`) |
| **How durable it is** | Carried immutably through opportunity, quotation, order and revenue. **Commission is never recomputed from inference** (`T-02`) |
| **The window** | A defined attribution window, evaluated **deterministically at conversion** (`T-03`) |
| **Outside the window** | Attributes to **no partner** — not to another partner, not to direct (`BRU-PCM-05`) |
| **Model** | First touch, last touch, or partner-declared with validation — **undecided**, `M40` Q-04, `O-01` |

**The four ways a partner loses attribution**, stated so a partner can avoid three of them:

| # | Cause | Avoidable by the partner? |
|---|---|---|
| 1 | The lead converted **outside the window** | Partly — submit at the point of interest, not later |
| 2 | The customer was **already in our pipeline** when the lead arrived | Yes — register the deal first where the programme allows (`FR-PCM-027`) |
| 3 | **No consent recorded**, so the lead was never created | **Yes, entirely** |
| 4 | The link or code was **not used**, and the customer arrived unattributed | **Yes** — the code is the key; a verbal referral leaves no key |

**Deal registration is the defence against cause 2.** A partner registers an opportunity, conflict
detection runs against open pipeline, other registrations and territory rules in under two seconds
(`T-04`), and **the conflict is decided rather than auto-approved** (`BRU-PCM-09`). An approved
registration carries a **time-boxed protection period** (`FR-PCM-028`). `KPI-C40-10` targets 98%
of registrations decided within SLA.

**Channel precedence** (`FR-PCM-029`, `BRU-PCM-10`) resolves the case where a partner introduces a
customer already in the direct pipeline. **The precedence rule is undecided** — `M40` Q-07 —
recorded as `O-02`.

### 4.6 Referral links and codes

| Property | Statement | Rule |
|---|---|---|
| Unique per partner and per campaign | A partner can tell which activity produced which lead | `FR-PCM-022` |
| **Signed and non-guessable** | Another party cannot fabricate a link that attributes to them | `T-07` |
| **Revocable** | A compromised or misused link is revoked without ending the relationship | `T-07` |
| Rate-limited | Automated abuse is resisted | `T-07` |
| Bound to the programme version in force | Terms cannot change retrospectively under a live link | `BRU-PCM-12`, `T-10` |

**What a partner must not do with a link**, drawn from `LG-007` §4.3 and stated in the kit because
it is where partner programmes go wrong: no paid search on 1000FiX brand terms, no unsolicited
messaging, no impersonation of 1000FiX, no placement on sites the partner does not control, and no
use of 1000FiX marks outside **`EO-012`**.

### 4.7 Commission, statements and payout

| Element | Where it lives |
|---|---|
| Commission model and rates | `MD-029`; the programme design is `M40`, the rate is a pricing decision (`BRU-PCM-03`) |
| Calculation and payout execution | `M53` / `M52` |
| **Statement** | **`DT-040`** — commission by referral, period, deductions and net |
| Payout schedule | The programme tier's schedule |
| Tax | Withholding on commission per the partner's tax status; **`O-04`** |
| Accuracy | **`KPI-C40-04` targets 100%.** `KPI-082`'s equivalent on the marketplace side is the same number for the same reason |

**Settlement on exit.** `BRU-PCM-15` requires outstanding commission to be settled **before** a
relationship reaches `Exited`. The kit states it at enrolment, not at exit — see `EO-014`.

### 4.8 The first 90 days

| Days | Partner milestone | 1000FiX milestone | Test |
|---|---|---|---|
| **0–30** | Enrolled, agreement signed, portal access live, first link generated, **first lead submitted with consent** | Onboarding cycle under 10 days (`KPI-C40-12`); lead attributed at creation | Does the partner see their lead, with a status? |
| **31–60** | Steady lead flow; first deal registration where applicable | First conversion attributed through to revenue; status visibility working end to end (`FR-PCM-026`) | **Can the partner reconcile a conversion to a lead they submitted?** |
| **61–90** | First commission statement reviewed | First payout, on schedule, matching the statement | **Statement reconciles to zero variance.** `KPI-C40-04` is 100% and the first statement is where a partner decides whether to believe it |
| **91+** | Volume, tiering, co-marketing (`EO-012`) | Performance reporting; tier movement with notice (`FR-PCM-004`) | Partner counts toward `KPI-C40-01`'s 200 |

**The 90-day test is the statement, not the lead volume.** A partner who has sent thirty leads and
cannot reconcile their first statement will send no more. `KPI-C40-03`'s 75% portal-adoption
target is achieved by partners who look at the portal because it tells them something true.

### 4.9 Rules

| # | Rule |
|---|---|
| **RL-01** | Attribution is explained **before** the first lead, in the terms of §4.5, in both languages |
| **RL-02** | The four ways attribution is lost are stated with whether the partner can prevent each |
| **RL-03** | **The kit never states an attribution window or a commission rate** while `M40` Q-03 and Q-04 are open. It states the mechanism and marks the value as set at programme launch (`O-01`) |
| **RL-04** | Consent is presented as a **precondition to the lead existing**, not as a term in an appendix (`BRU-PCM-06`) |
| **RL-05** | The kit states what a partner does **not** receive — the customer's account, history or subsequent transactions |
| **RL-06** | A partner sees only their own records; never another partner's, never 1000FiX cost or margin (`BRU-PCM-14`, `EA-01`, `EA-02`, `EA-11`) |
| **RL-07** | Link misuse prohibitions are stated positively and specifically, with `EO-012` named for marks and materials |
| **RL-08** | **A marketplace seller is not a partner** (`BRU-PCM-02`); the kit says so, and flags the dual-role case as undecided |
| **RL-09** | Programme terms are versioned and effective-dated; a partner is bound to the version in force at their agreement date (`BRU-PCM-12`) |
| **RL-10** | Portal access is described as revoked **within one hour** of exit, suspension or expiry (`BRU-PCM-13`) |
| **RL-11** | Outstanding commission settled before `Exited` is stated at enrolment (`BRU-PCM-15`) |
| **RL-12** | Alliance benefits are described as applied by the pricing engine, **never as an ad-hoc discount** (`BRU-PCM-19`) |
| **RL-13** | Bengali is the delivery language for individual and small-business partners (`CG-010` §3.3); machine translation is prohibited (`CP-05`) |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`LG-007`](../10_Legal_Policy_and_Compliance/LG-007_Referral_and_Alliance_Partner_Agreement.md) | The agreement signed at stage 3; §4.2 attribution and §4.6 consent are its operative clauses |
| `M40` §5.3 | Links, leads, attribution, registration, precedence and schemes |
| `M07` | Where an attributed lead becomes an opportunity |
| `M33`, [`LG-008`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md) | Customer party identity and the privacy position after the lead is created |
| `M11`, [`MD-029`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md) | Commission rates and alliance benefit application |
| `M53`, `M52`, [`DT-040`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-040_Partner_Commission_Statement.md) | Calculation, payment and the statement |
| [`MD-013`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md), [`MD-038`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md) | Party master and payout destinations |
| `M10`, [`MD-034`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-034_Loyalty_Tier_Point_and_Benefit_Register.md) | The customer-referral mechanic this kit is **not** about |
| [`UI-022`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-022_P12_Partner_and_Referral_Portal_UI_Copy_Pack.md), [`UI-040`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-040_Registration_and_Onboarding_Flow_Copy.md), [`HC-014`](../09_Help_Centre_and_Self_Service/09A_Help_Sets_By_Portal/HC-014_Help_Set_P12_Partner_and_Referral_Portal.md), `NT-012` | Screens, flow copy, help and notifications |
| [`EO-011`](EO-011_Rate_Card_and_Pricing_Communication_Pack.md), [`EO-012`](EO-012_Co_Marketing_and_Co_Branding_Asset_Guide.md), [`EO-013`](EO-013_Ecosystem_Dispute_Resolution_Content.md), `EO-014` | Rate change communication, marks and materials, disputes, exit |

> **Rule-citation attribution.** **BRU-PCM-\***  → `M40` §9 — these are **module-scoped** rule families and **`05-05` carries none of them**. Stated per `AUDIT-015` R-11, which asked that the convention be recorded once rather than rediscovered by each extraction.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly during W7–W8; annually thereafter |
| Trigger for out-of-cycle review | The attribution model or window being decided or changed; a commission model change; a channel-precedence decision; a change to `LG-007`; a `P12` release changing lead submission; a dispute revealing an unexplained attribution rule; a PDPA 2026 guidance change on third-party consent |
| Owner | Partnerships, with Legal for §4.4 and Finance for §4.7 |
| Change control | **An attribution or commission change applies to leads created after the effective date only.** `BRU-PCM-04` makes attribution immutable and `BRU-PCM-12` binds a partner to the version at their agreement date; a retrospective change would breach both |
| Effectiveness measure | Commission disputes per hundred statements, and the share of partners submitting a second lead within 30 days of their first |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The two numbers this kit exists to explain are both undecided.** `M40` Q-04 — *"what is the attribution window and model — first touch, last touch, or partner-declared with validation?"* — and Q-03 — the commission model, *"and is it viable against the marketplace take rate?"* **§4.5 and §4.7 therefore describe mechanisms with no values**, and `RL-03` forbids estimating them. A referral kit that cannot state the window or the rate can enrol a partner and cannot motivate one | CCO / CFO | **W7 build — both are named `W7 build` in `M40` §18** |
| **O-02** | **Channel precedence is undecided** (`M40` Q-07): what applies when a referral partner introduces a customer already in the direct pipeline. §4.5 cause 2 is the second-commonest attribution loss and the kit can only describe deal registration as the defence. **`LG-007` §4.8 is itself marked *pending* `O-04`, `O-05`** — so the agreement and the kit are blocked on the same decision | CCO | **W7 build** |
| **O-03** | **`KPI-035` is assigned to `M10`, and this kit's target belongs to `M40`.** `06-02` §2.4 registers *"referral-attributed new customers"* at 6% (W4) and 12% (W8) with the source column reading **`M10`** — the loyalty module, which owns **customer-to-customer** referral. `M40` `KPI-C40-02` claims the same 12% for **partner** referral, and `04-00` P12 claims it again. **Three claims on one number, measuring two different mechanics.** Either two identifiers are needed or the 12% is being double-counted between loyalty and partnerships | Enterprise Architecture with BI Lead and CCO | **W4 — `KPI-035` has a W4 milestone and `M40` is W7** |
| **O-04** | **Withholding treatment on commission is unstated.** §4.7 names it and cannot specify it. Commission paid to an individual referrer, to a VAT-registered business and to an alliance partner attract different treatments, and 1000FiX carries the deduction obligation. **`EO-005` `O-06` records the same class of gap for supplier VDS** — one tax determination, two ecosystems, no owner | CFO / Tax Manager with external verification (`CG-007` G6) | **W7 — before the first commission payment** |
| **O-05** | **The dual-role case is undecided** (`M40` Q-09): where a marketplace seller is also a referral partner, whether both roles are permitted and how conflict of interest is managed. §4.2 states `BRU-PCM-02` and flags the case. **A seller who refers a customer to a job they then bid on is a structural conflict**, and neither `M12` nor `M40` resolves it | CCO | **W7 build** |
| **O-06** | **Alliance member-eligibility validation may require partner APIs that do not exist** (`M40` Q-06: *"do alliance partners require API-based member eligibility validation, and will they expose one?"*). §4.3 item 9 and `FR-PCM-031` assume a validation method; for an insurer or telco that is an integration, not a document. **No alliance partner has been asked** | CCO / CTO | **W7 build** |
| **O-07** | **Bengali is required and unresourced.** §3 marks the two largest partner populations as Bengali readers. `CG-010` §3.2's `EO` rationale — *"seller, rider and corporate-user-facing kits"* — **does not mention partners at all**, so this file's bilingual status rests on the §3.3 audience rule rather than on the category allocation. Recorded here and in the category audit | Localisation Lead *(unappointed)* with Partnerships | **W7 minus 6 weeks** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the three `EO` additions placed and the template gap noted
- [x] **Attribution identified as the programme's currency, with the five mechanisms that make it believable**
- [x] Nine-stage enrolment journey against the `KPI-C40-12` ten-day cycle
- [x] Partner types distinguished by which mechanics apply and which do not
- [x] Enrolment document checklist and a separate **valid-lead** checklist
- [x] **Consent stated as a precondition to the lead existing, with what the partner must be able to show**
- [x] Attribution stated as five rules plus the **four ways it is lost**, with preventability marked for each
- [x] Deal registration positioned as the defence against the pipeline-conflict loss
- [x] Referral-link properties and the specific prohibitions on link use
- [x] Commission, statement, payout and the exit-settlement rule stated at enrolment
- [x] First-90-days test set at the **first statement**, not at lead volume
- [x] Thirteen rules, including the prohibition on estimating the window or the rate
- [x] All internal links resolve
- [x] Seven open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` attribution window and commission model both undecided — outstanding; the kit's two operative numbers are absent**
- [ ] **`O-02` channel precedence undecided — outstanding; `LG-007` §4.8 blocked on the same decision**
- [ ] **`O-03` `KPI-035` assigned to `M10` while `M40` and `P12` claim the same 12% — outstanding; possible double count**
- [ ] **`O-04` commission withholding treatment unstated — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Named approver recorded — **pending Content Design Lead with Partnerships**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
