---
id: AP-012
title: Data Sharing and Field-Level Disclosure Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Security Lead with Legal Counsel
author: Information Security with Legal and Platform Engineering
reviewers: [CTO, Legal Counsel, CFO, Solution Architect, Data Protection Officer (unappointed — O-06), Commercial Director, Account Management Lead, Treasury Lead, Marketplace Operations, Quality Manager]
approver: Legal Counsel
content_class: B
purpose: >
  The authoritative record of exactly which fields leave 1000FiX to each external counterparty, why
  each field is necessary, and the lawful ground under the Personal Data Protection Act 2026 that
  permits it. `IP-10` requires data leaving the company to be minimised and logged; minimisation is
  only auditable against a stated permitted set, and a lawful ground asserted per integration
  rather than per field is not a lawful ground. Without this register the company cannot answer the
  National Data Management Authority's basic question — what personal data do you disclose, to
  whom, and on what basis — and cannot demonstrate the technical and organisational measures
  `NFR-097` requires, against a penalty exposure of up to BDT 25 lakh, or BDT 50 lakh if 1000FiX is
  classified a significant data fiduciary.
traces_to: [05-03, 05-03 IP-10, 05-03 §2, 05-06 NFR-086, 05-06 NFR-086a, 05-06 NFR-086b, 05-06 NFR-086c, 05-06 NFR-090, 05-06 NFR-091, 05-06 NFR-092, 05-06 NFR-095, 05-06 NFR-097, 05-06 NFR-098, 05-06 NFR-099, 05-02 §10, 05-04 §5, 05-04 §8, M28 FR-IPF-044, M29, M60, LG-008, LG-009, LG-010, LG-012, LG-021, AP-001, AP-004, AP-005, AP-006, AP-007, AP-008, AP-009, AP-010, AP-011, TS-017, RF-008]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §1 IP-10 "data leaving the Company is minimised and logged — only the fields the counterparty needs"; §2 the 47-integration catalogue with direction and owning module
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §6.1 statutory currency table; §6.3 NFR-090…NFR-099 Personal Data Protection Act 2026 obligations; §6.4 NFR-086, NFR-086a/b/c split-residency architecture and the residency-classified field inventory; penalty exposure BDT 25 lakh / BDT 50 lakh, risk RSK-032
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md §10 data classification S0–S3 and the S3 field inventory; DM-14 sensitive-data field classification
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §5 field-level permissions; §8 EA-01…EA-12 external party access rules
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_Integration_API_and_Event_Platform.md §5.5 FR-IPF-044 data minimisation — "send only the fields the counterparty requires, and log what left the Company"; §14 the egress and data-minimisation log
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_Identity_Access_and_Information_Security.md §4 benchmark basis — PDPA 2026 localisation narrowed to restricted and CII data by Ordinance No. 23 of 2026; §18 Q-01 records that the residency-classified field list may now be broader than the statute requires
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Data Sharing and Field-Level Disclosure Register

| Item | Value |
|---|---|
| Counterparty classes registered | **12** (§4.3) |
| External integrations in scope | **47** (`05-03` §2) plus 6 external portal audiences |
| Counterparties with a **completed** field-level register | **9** (§4.5) |
| Counterparties **not yet specifiable** | **38** — the integration is not designed (§4.3, open item `O-01`) |
| Lawful grounds in the vocabulary | 5 (§4.4) |
| Residency-classified fields | 7 (`05-06` §6.4) |
| Absolute prohibitions | 12 (§4.7) |
| Content class | **B — Legal / contractual.** Approver: Legal Counsel (`CG-002` §5.2) |
| Wave | W3 |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order; §4 subdivided by volume. The **endpoint reference table**
> required by `CG-009` §3 is §4.10. The **error catalogue table** required by `CG-009` §3 is
> §4.11 — the `data.*` domain, referencing `AP-006` codes (`CP-01`).
>
> **This is the single Class B file in Category 15** (`CG-002` §4.1 allocates `AP` as 0 A · 1 B ·
> 0 C · 9 D · 2 E). Under `CM-R7` and `CG-007` it cannot reach `Approved` without a recorded
> named sign-off from Legal Counsel, and that sign-off is recorded in `LG-001`.

---

## 1. Purpose

`IP-10` is one line: *"Data leaving the Company is minimised and logged — only the fields the
counterparty needs."* `FR-IPF-044` implements it: *"Send only the fields the counterparty
requires, and log what left the Company."* `BRU-IPF-15` makes it a hard rule.

**A minimisation rule with no permitted set is unenforceable.** "Only the fields the counterparty
needs" requires somebody to have decided, per counterparty, which fields those are. Nobody has,
and the decision is not an engineering one — under the Personal Data Protection Act 2026 it is a
lawful-basis determination that Legal owns.

The statutory position, from `05-06` §6:

| Obligation | Requirement |
|---|---|
| `NFR-090` | Process personal data only on consent or a stated legitimate ground, **recorded per processing purpose** |
| `NFR-091` | Consent must be clear, explicit, specific and freely given, with a **heightened specific-consent standard for sensitive personal data** |
| `NFR-092` | Issue a transparency notice stating data categories, purposes, risks, retention, **third-party transfers** and the withdrawal procedure |
| `NFR-095` | Maintain processing records for **a minimum of five years** |
| `NFR-097` | Technical and organisational measures proportionate to risk |
| `NFR-098` | **A processor's processing is the controller's own.** Equivalent obligations flow to every processor and sub-processor **by contract** |
| `NFR-099` | Restrict large-scale transfer of Sensitive Personally Identifiable Data; **notify the Authority of cross-border transfers and disclose the safeguards** |

**Penalty exposure: up to BDT 25 lakh**, and **up to BDT 50 lakh** if 1000FiX is classified a
significant data fiduciary — registered as risk `RSK-032`. Enforcement mechanisms activate around
**13 May 2027, inside Wave 4**.

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| A permitted set per counterparty | `IP-10` and `BRU-IPF-15` cannot be enforced or tested. `TS-017` has nothing to assert against |
| A lawful ground per field | The company cannot answer the Authority's first question. `NFR-090` requires it recorded **per processing purpose**, not per system |
| A cross-border record | `NFR-086b` requires an Authority notification record and a documented safeguard **before the transfer executes**. Two payment rails and several AI services are cross-border by construction |
| A transparency-notice input | `NFR-092` requires the privacy notice to state third-party transfers. `LG-008` is the notice; **this register is where its transfer section comes from** |
| A processor-contract inventory | `NFR-098` flows obligations by contract to every processor. Without a list of processors there is no list of contracts to check |
| The disclosure boundary in machine-enforceable form | `AP-007` §4.9 and `AP-008` §4.9 state their boundaries in prose. Enforcement needs a field list per counterparty |

---

## 2. Scope

**In scope.** The disclosure principles; the register's row structure; the counterparty inventory
across all 47 integrations and 6 portal audiences; the lawful-ground vocabulary; completed
field-level registers for the nine counterparties that can be specified today; residency and
cross-border gating; twelve absolute prohibitions; egress logging and audit; the review procedure;
the egress endpoint reference; and the `data.*` error family.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| The privacy notice and consent copy | `LG-008` | This register is an **input** to it (`NFR-092`), not a substitute |
| Retention and deletion schedule | `LG-009` | Disclosure and retention are different obligations |
| Data-subject request handling | `LG-010` | `NFR-093`; the register tells a DSR handler where data went |
| The cross-border residency statement | `LG-012` | The **legal position**; this register is the **field-level implementation** of it |
| ISMS policy set | `LG-021` | Controls framework |
| Data classification S0–S3 and the residency field list | `05-02` §10, `05-06` §6.4 | Referenced, never redefined |
| Field-level permissions for **internal** roles | `05-04` §5 | Internal access; this register is external disclosure |
| Enforcement mechanism — masking, filtering, egress logging | `M28` `FR-IPF-044`, `M29` | The register states what; the platform enforces it |
| The DPIA | **Nobody — `O-03`** | Recorded, not assumed |
| Processor contract drafting | Legal, `M60`, `M42` vendor management | `NFR-098`; §4.9 names the requirement |
| Statutory currency of the citations | `RF-008` | Every statute cited here carries a verification date (`CG-012`) |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Legal Counsel** | The approver. This is a Class B file and its content is a legal position |
| **Security Lead** | The enforceable specification behind `IP-10` and `BRU-IPF-15` |
| **Data Protection Officer** | The processing record `NFR-090` and `NFR-095` require — **and the role is unappointed** (`NFR-096`, `O-06`) |
| **Platform Engineering** | The permitted field set per connector; `FR-IPF-044` is configured from this |
| **Account Management and Commercial** | What may be promised to a partner, and what may not |
| **External counterparties** | **Their own rows only**, as a generated extract (`AP-001` §4.8, tier T-Part) |
| **QA** | `TS-017` derives disclosure negative cases from §4.5 and §4.7 |
| **Auditors — internal, ISO 27001, and the Authority** | The evidence that minimisation is a control rather than an intention |

---

## 4. Content

### 4.1 Seven principles

| # | Principle | Basis |
|---|---|---|
| **DS-01** | **Nothing leaves without a row.** A field not on this register is not disclosed. The default is refusal, not permission | `IP-10`, `BRU-IPF-15` |
| **DS-02** | **A row is per field, per counterparty, per purpose** — not per integration. The same field to the same counterparty for a different purpose is a different row with its own ground | `NFR-090` — recorded **per processing purpose** |
| **DS-03** | **Necessity is argued, not assumed.** Every row states why the counterparty cannot perform its function without that field. "It was in the payload" is not a reason | `IP-10` minimisation |
| **DS-04** | **Identifiers before data.** Where a counterparty can resolve a reference through an authorised call, they receive the reference | `AP-003` `PD-02` |
| **DS-05** | **No residency-classified field leaves without the `NFR-086b` gate** — an Authority notification record and a documented safeguard, **before** the transfer executes | `NFR-086b`, `NFR-099` |
| **DS-06** | **Every egress is logged**, with counterparty, purpose, field set, record count and time | `IP-10`, `FR-IPF-044`, `NFR-095` |
| **DS-07** | **A processor's processing is ours.** Every counterparty acting as a processor carries equivalent obligations **by contract**, flowed down to sub-processors | `NFR-098` |

### 4.2 What a register row is

| Column | Content | Why |
|---|---|---|
| **Counterparty** | The named external party or class | — |
| **Integration** | `INT-nnn`, or the portal | Joins to `05-03` §2 |
| **Field** | The specific field, by its `05-02` name | Not "customer details" |
| **S-class** | S0–S3 (`05-02` §10) | Determines the control level |
| **Residency** | Whether the field is residency-classified (`05-06` §6.4) | Determines whether `DS-05` applies |
| **Purpose** | The single processing purpose | `NFR-090` |
| **Necessity** | Why the counterparty cannot function without it | `DS-03` |
| **Lawful ground** | From §4.4's vocabulary | `NFR-090`, `NFR-091` |
| **Direction** | Outbound, inbound or bidirectional | |
| **Retention at the counterparty** | How long they may hold it | `NFR-098` flow-down |
| **Cross-border** | Whether the transfer leaves Bangladesh | `NFR-086b`, `NFR-099` |
| **Status** | `Determined` · `Provisional` · **`Undetermined`** | Honesty about what has actually been decided |

**`Undetermined` is a real and common status and it is not a placeholder.** A row marked
`Undetermined` means the disclosure **must not occur** until it is determined (`DS-01`). Marking a
row `Provisional` to unblock a build is the specific misuse this column exists to prevent.

### 4.3 Counterparty inventory

Twelve classes across the 47 integrations and 6 external portal audiences.

| # | Class | Integrations | Personal data? | Register status |
|---:|---|---|:--:|---|
| **CP-1** | **Payment rails** | INT-001…009 (9) | ● | §4.5.1 — **3 complete, 6 undetermined** |
| **CP-2** | **Messaging and communications** | INT-010…018 (9) | ● | §4.5.2 — **3 complete, 6 undetermined** |
| **CP-3** | **Location, mapping, logistics** | INT-019…027 (9) | ● | §4.5.3 — **1 complete, 8 undetermined** |
| **CP-4** | Remote support and monitoring | INT-028…033 (6) | ● | **Undetermined** — client-estate data under `M05`; `LG-016` consent terms apply |
| **CP-5** | **Marketplace and trust** | INT-034…037 (4) | ● **sensitive** | §4.5.4 — **1 complete, 3 undetermined**. `INT-034` is the highest-risk row in the register |
| **CP-6** | **Government and compliance** | INT-038…042 (5) | ● | **Undetermined** — statutory disclosure; ground is `LG-3` (§4.4) but the field sets are unspecified |
| **CP-7** | **AI, data and enterprise** | INT-043…047 (5) | ● | §4.5.5 — **1 complete, 4 undetermined** |
| **CP-8** | **Brand partners** | `P08`, INT-P08-01…04 | ● restricted | §4.5.6 — **complete** |
| **CP-9** | **Corporate clients** | `P04`, INT-P04-01…04 | ● | §4.5.7 — **complete** |
| **CP-10** | Marketplace sellers | `P07` | ● | §4.5.8 — **complete for the awarded-job case** |
| **CP-11** | Referral and alliance partners | `P12` | ● | **Undetermined** — `M40` attribution model not settled |
| **CP-12** | Vendors and suppliers | `P05` | Minimal | §4.5.9 — **complete** |

> **Nine of fifty-three counterparties have a completed field-level register.** That is not a
> shortfall in this file; **it is the current state of the programme.** A field-level register can
> only be written after the integration's payload is designed, and 38 of the 47 integrations are
> scheduled from W4 onward. Recorded as `O-01`, with the operating rule that follows from `DS-01`:
> **an integration may not be promoted to production until its rows are `Determined`**, which
> makes this register a gate rather than a document.

### 4.4 The lawful-ground vocabulary

Five grounds. Every row names exactly one.

| # | Ground | When it applies | Evidence required |
|---|---|---|---|
| **LG-1** | **Contract performance** — processing necessary to deliver the service the data subject requested | The customer booked a repair; the courier needs the address to collect the device | The service order itself |
| **LG-2** | **Consent** — clear, explicit, specific, freely given (`NFR-091`) | Anything the customer could reasonably decline without losing the service | A consent record with purpose, timestamp and withdrawal route (`LG-008`) |
| **LG-2S** | **Specific consent for sensitive personal data** — the heightened standard | NID, biometric, criminal record, recovered data | As LG-2, at the heightened standard, **per purpose** |
| **LG-3** | **Legal obligation** — a statute or regulator requires the disclosure | NBR e-VAT (INT-038), BIN/TIN validation (INT-039), e-waste reporting (INT-040) | The instrument, cited with a verification date (`CG-012`, `RF-008`) |
| **LG-4** | **Legitimate ground** — a stated legitimate interest, balanced and recorded | Fraud prevention, service-quality analytics on non-identifying aggregates | A recorded balancing assessment. **Not a default** |

| # | Rule |
|---|---|
| **LR-1** | **`LG-4` is not the fallback.** A row that cannot state `LG-1`, `LG-2`, `LG-2S` or `LG-3` is `Undetermined`, not `LG-4` |
| **LR-2** | **`LG-2` requires a withdrawal path that actually works.** A consent that cannot be withdrawn is not freely given (`NFR-093`, `LG-010`) |
| **LR-3** | Consent withdrawn **stops the disclosure**, and the counterparty is told to delete under the `DS-07` flow-down |
| **LR-4** | `LG-1` does not cover marketing, analytics or model training. Those are `LG-2` or `LG-4` with a recorded assessment |
| **LR-5** | `LG-3` names the instrument. "Regulatory requirement" without a citation is `Undetermined` |

### 4.5 Field-level registers — the nine that can be specified

#### 4.5.1 Payment rails — CP-1

| Counterparty | Field | S | Res | Purpose | Necessity | Ground | Cross-border | Status |
|---|---|:--:|:--:|---|---|:--:|:--:|---|
| **bKash** (INT-001) | Amount, currency | S0 | — | Collect payment | The transaction | LG-1 | No | Determined |
| | Merchant + order reference | S0 | — | Reconciliation | Matching (`AP-009` §4.5) | LG-1 | No | Determined |
| | **Customer mobile number** | S2 | — | Wallet identity | **The wallet is the number.** Not minimisable | LG-1 | No | Determined |
| **Nagad** (INT-002) | Amount, currency, order reference | S0 | — | Collect payment | The transaction | LG-1 | No | Determined |
| | **Customer mobile number** | S2 | — | Wallet identity | As above | LG-1 | No | Determined |
| **SSLCOMMERZ** (INT-003) | Amount, currency, `tran_id` | S0 | — | Collect payment | The transaction | LG-1 | No | Determined |
| | **Customer name** | S2 | — | Card checkout | Acquirer requirement | LG-1 | No | Determined |
| | **Customer email, phone** | S2 | — | Checkout, receipt, dispute | Acquirer requirement | LG-1 | No | Determined |
| | **Customer address** | S2 | — | Card fraud screening | Acquirer requirement | LG-1 | No | Determined |
| INT-004 Rocket | — | — | — | — | — | — | — | **Undetermined — aggregator unnamed** (`AP-009` `O-02`) |
| **BEFTN** (INT-005) | **Beneficiary name, bank account** | S3 | — | Disbursement | The payment instruction | LG-1 (employment) | No | Determined |
| INT-007 payout rail | — | — | — | — | — | — | — | **Undetermined — rail unnamed** |
| INT-008 international | — | — | — | — | — | — | **Yes** | **Undetermined — `DS-05` gate applies** |
| INT-009 BNPL | — | — | — | — | — | — | Likely | **Undetermined** |

> **INT-003 is the largest personal-data egress of the nine.** Hosted checkout requires a customer
> profile — name, email, phone, address — and the necessity argument rests on the acquirer's own
> requirement rather than on ours. It should be re-examined against a lower-disclosure checkout
> option at the next review (`O-08`).

#### 4.5.2 Messaging — CP-2

| Counterparty | Field | S | Res | Purpose | Necessity | Ground | Status |
|---|---|:--:|:--:|---|---|:--:|---|
| **SMS gateways** (INT-010, -011) | Mobile number | S2 | — | Deliver a transactional message or OTP | The destination | LG-1 | Determined |
| | Message body | S1–S2 | — | The message | Content varies; **may carry an order reference and a name** | LG-1 | Determined |
| **WhatsApp Business Cloud** (INT-012) | Mobile number | S2 | — | Deliver | The destination | LG-1 | Determined |
| | Message body, template variables | S1–S2 | — | The message | Template-bound (`NT-008`) | LG-1 | Determined |
| | **Invoice document** where shared | S2 | — | Invoice sharing | Customer-requested | **LG-2** | Determined |
| **Email** (INT-013) | Address, subject, body, attachments | S1–S2 | — | Deliver | The destination | LG-1 | Determined |
| INT-014 push (FCM/APNs) | Device token, notification body | S1 | — | Deliver | The token is the destination | LG-1 | **Provisional — cross-border processor**, `NFR-098` flow-down unconfirmed |
| INT-015…018 | — | — | — | — | — | — | **Undetermined** — telephony recordings (S3), video, social, chat |

> **Call recordings (INT-015) are S3 and require `LG-2S`.** `05-04` §5 restricts
> `call_recording_url` to three internal roles. A telephony provider **holding** the recording is
> a processor with S3 data, which is `NFR-098`'s strongest case and is undetermined.

#### 4.5.3 Location and logistics — CP-3

| Counterparty | Field | S | Res | Purpose | Necessity | Ground | Status |
|---|---|:--:|:--:|---|---|:--:|---|
| **Google Maps** (INT-019) | Address string **or** coordinates | S2 | — | Geocoding, routing | Cannot geocode without it | LG-1 | **Provisional — cross-border processor**; `NFR-086b` assessment absent |
| INT-020, -021 OSRM/VROOM | Coordinates only | S1 | — | Distance, routing | Self-hosted — **no egress** | n/a | Determined — **no disclosure** |
| INT-023 Traccar | Technician position, device id | S2 | — | Live tracking | Self-hosted | n/a | Determined — no disclosure |
| **Couriers** (INT-024, -025, -026) | Recipient name | S2 | — | Delivery | Cannot deliver without it | LG-1 | **Undetermined — three providers, all W3** |
| | Recipient phone | S2 | — | Delivery contact | Courier operating requirement | LG-1 | **Undetermined** |
| | Recipient address | S2 | — | Delivery | The destination | LG-1 | **Undetermined** |
| | Consignment reference, weight, declared value | S0 | — | Handling | Operational | LG-1 | **Undetermined** |
| | **Device make/model** | S1 | — | — | **Not necessary. A courier delivers a package, not a device** | — | **Prohibited — §4.7 `PR-9`** |
| INT-027 freight | — | — | — | — | — | — | **Undetermined — cross-border, W9** |

> **`EA-07` already states the position: a courier partner sees only consignments assigned to
> them, with the minimum data needed to deliver.** The three W3 couriers are `Undetermined`, which
> under `DS-01` means **no consignment may be booked with them until their rows are determined.**
> That is a W3 blocker, not a W3 nicety (`O-02`).

#### 4.5.4 Identity verification — CP-5 · the highest-risk rows

| Counterparty | Field | S | Res | Purpose | Ground | Status |
|---|---|:--:|:--:|---|:--:|---|
| **NID verification** (INT-034) | **NID number** | **S3** | **● Residency-classified** | Verify seller and high-value customer identity | **LG-2S required** | **Undetermined — `DS-05` gate not satisfied** |
| | Name, date of birth | S2 | — | Matching | LG-2S | Undetermined |
| **Trade licence / registry** (INT-035) | Business registration number, entity name | S1 | — | Verify seller business registration | LG-1 | **Provisional** — corporate data, not personal, **unless a sole trader** |
| **IMEI blocklist** (INT-036) | IMEI | S1 | — | Screen trade-in devices | LG-1 | **Provisional** |
| INT-037 ad delivery | — | — | — | Serve and measure marketplace advertising | **LG-2 required** | **Undetermined — advertising is not `LG-1`** |

> **INT-034 is the single highest-risk row in this register and it is `Undetermined`.**
> It transmits a **national identifier**, which `05-06` §6.4 classifies residency-restricted and
> `NFR-099` names as Sensitive Personally Identifiable Data whose large-scale transfer is
> restricted. It therefore needs all three of: `LG-2S` specific consent; the `NFR-086b` gate —
> Authority notification and a documented safeguard **before** the transfer; and confirmation that
> the verification service is Bangladesh-resident. **None of the three exists**, and the
> integration is scheduled W7 for `P07` seller onboarding, where identity verification is the
> control the marketplace's trust model rests on. `O-04`.

#### 4.5.5 AI and data services — CP-7

| Counterparty | Field | S | Res | Purpose | Ground | Status |
|---|---|:--:|:--:|---|:--:|---|
| **Self-hosted LLM** (INT-043) | Prompt content — may contain any customer text | S1–S2 | Possible | Bengali assistant, summarisation | LG-1 | **Determined — self-hosted, no egress.** This is why self-hosting was chosen |
| **OCR** (INT-044) | Document images — invoices, IDs, delivery notes | **S1–S3** | **Possible** | Document extraction | Depends on the document | **Undetermined.** An OCR service processing an identity document receives residency-classified data |
| INT-045 speech-to-text | Call audio | **S3** | Possible | Transcription | **LG-2S** | **Undetermined — cross-border likely** |
| INT-046 corporate SSO | Employee identifiers from the **client's** directory | S2 | — | Federated authentication | LG-1 (client contract) | **Provisional** — inbound; the client is controller for their own users |
| INT-047 client ITSM | Ticket content, asset identifiers | S1 | — | Ticket exchange | LG-1 | **Undetermined** |

> **INT-044 OCR is the quiet risk.** It is `P2`, W3, and framed as a convenience — *"document
> extraction including Bengali"*. If it processes an NID, a passport or a trade licence, it is
> processing residency-classified data, and if the service is not Bangladesh-resident it breaches
> `NFR-086` without anybody deciding to. **The determination must be made before W3, not after.**

#### 4.5.6 Brand partners — CP-8 · **complete**

**Permitted** (`P08` `FR-POR-230`): device identity and serial · purchase proof · fault and
diagnostic detail · before/after photographs · parts with serials and provenance · labour · the
technician's certification for that brand · claim value and rate-card version.

| Field | S | Purpose | Necessity | Ground | Status |
|---|:--:|---|---|:--:|---|
| Device serial, make, model | S1 | Claim decision | Identifies the covered product | LG-1 | Determined |
| Purchase proof | S1 | Warranty eligibility | Establishes entitlement | LG-1 | Determined |
| Fault, diagnostic, repair detail | S1 | Claim decision | The substance of the claim | LG-1 | Determined |
| Photographs | S1 | Claim evidence | **Must not contain a person or an identifying document** — `MM-002` redaction standard | LG-1 | Determined |
| Parts, serials, provenance | S0 | Claim valuation | Consignment vs purchased | LG-1 | Determined |
| Technician certification status | S1 | Authorisation check | `BRU-SRM-09` | LG-1 | Determined |

**Prohibited to brands** — the eight in `AP-007` §4.9 (`P08` `T-03`, `EA-05`), enforced here.
**Photographs are the leak path**: an image of a repair bench can contain a customer's document,
another device's serial or a person. `MM-002` governs redaction and this register depends on it.

#### 4.5.7 Corporate clients — CP-9 · **complete**

| Field | S | Purpose | Ground | Status |
|---|:--:|---|:--:|---|
| Asset estate — serial, model, site, department | S1 | Estate management | LG-1 (client's own assets) | Determined |
| Service order detail for their own requests | S1 | Service delivery | LG-1 | Determined |
| **Requester name and contact — their own employee** | S2 | Service delivery | LG-1; **the client is controller for their own employees** | Determined |
| SLA measurement and credits | S0 | Contract performance | LG-1 | Determined |
| Invoice decomposition | S1 | Billing | LG-1 | Determined |
| Destruction and disposal certificates | S1 | Compliance evidence | LG-1 / LG-3 | Determined |
| **Technician name and photograph, for the visit only** | S2 | Visit identification and safety | LG-1 — **and this is a 1000FiX employee's personal data disclosed to a client** | **Determined, with a note**: the employment-side basis sits with HR (`M21`) and is assumed, not evidenced. `O-07` |

**Prohibited to corporate clients** — the six in `AP-008` §4.9, enforced by `P04` `AC-12`'s
automated payload inspection.

#### 4.5.8 Marketplace sellers — CP-10 · **complete for the awarded-job case**

`EA-04` is precise: *a marketplace seller sees the customer's name, contact and address only for a
job they have been awarded, and only until a defined period after completion.*

| Field | S | Purpose | Ground | Status |
|---|:--:|---|:--:|---|
| Customer name | S2 | Perform the awarded job | LG-1 | Determined |
| Customer contact number | S2 | Coordinate the visit | LG-1 | Determined |
| Customer address | S2 | Attend | LG-1 | Determined |
| Device and fault detail | S1 | Perform the job | LG-1 | Determined |
| **Time-boxed expiry after completion** | — | Minimisation | `EA-04` | **`Undetermined` — "a defined period" is not defined anywhere.** `O-05` |

> **The expiry period is the control, and it does not exist.** Without a number, `EA-04`'s
> minimisation is unenforceable and a seller retains customer contact details indefinitely — which
> is the marketplace's most obvious data-protection exposure and its most obvious channel for
> off-platform leakage.

#### 4.5.9 Vendors and suppliers — CP-12 · **complete**

| Field | S | Purpose | Ground | Status |
|---|:--:|---|:--:|---|
| Purchase order detail, parts, quantities, prices | S0 | Procurement | LG-1 | Determined |
| Delivery location — **a 1000FiX branch or warehouse** | S0 | Delivery | LG-1 | Determined |
| 1000FiX contact name and number | S1 | Coordination | LG-1 (employment) | Determined |
| **Customer data** | — | — | — | **Prohibited — `PR-4`.** A vendor has no customer relationship |

### 4.6 Residency and cross-border

`05-06` §6.4 classifies seven field types as residency-restricted:

| Field | Entity | Owning module |
|---|---|---|
| National ID number | `fix.identity.document` | `M33` |
| Passport number | `fix.identity.document` | `M33` |
| TIN | `fix.party`, `hr.employee` | `M33`, `M21` |
| Biometric attendance template | `fix.attendance.record` | `M55` |
| Recovered customer data and its index | `fix.recovered.inventory` | `M06` |
| Marketplace seller KYC documents | `fix.mp.seller.document` | `M12` |
| Criminal record checks | `fix.mp.seller.document` | `M12` |

**The gate (`NFR-086b`).** Any cross-border transfer of a residency-classified field requires an
**Authority notification record** and a **documented safeguard** *before the transfer executes*.

| # | Rule |
|---|---|
| **CB-1** | The gate is a **precondition**, not a report. A transfer executed before the record exists is a breach, not a paperwork gap |
| **CB-2** | `NFR-099` additionally restricts **large-scale** transfer of Sensitive Personally Identifiable Data. "Large-scale" is undefined in `05-06` and the register cannot define it — `O-04` |
| **CB-3** | Four counterparty classes are cross-border by construction: INT-008 international payments, INT-027 freight, INT-045 speech-to-text, and any non-resident OCR or cloud provider. **All four are `Undetermined`** |
| **CB-4** | `M29` §4 records that **Ordinance No. 23 of 2026 narrowed localisation to restricted and CII data**, and `M29` Q-01 asks whether `NFR-086`'s field list is now broader than the statute requires. **This register uses the `05-06` list as written**, because narrowing it is a legal determination and `DS-01` defaults to refusal |
| **CB-5** | The **split-residency legal opinion (`DEP-31`, decision `D-13`) is outstanding.** Several rows here cannot move beyond `Provisional` until it lands |

### 4.7 Absolute prohibitions

Never disclosed to any external counterparty, in any payload, by any path, in any mode.

| # | Never | Basis |
|---|---|---|
| **PR-1** | 1000FiX internal **cost, margin or vendor price** | `EA-02`, `05-04` §5 |
| **PR-2** | `internal_note` on any object | `05-04` §5 — *"never exposed to any external portal"* |
| **PR-3** | **Another counterparty's data**, including in an aggregate from which it can be isolated | `EA-02`, `EA-05` |
| **PR-4** | Customer personal data to a counterparty with no customer relationship — vendors, brands, ad services | `EA-02`, `P08` `T-03` |
| **PR-5** | Employee records beyond what a specific purpose requires — `salary`, `technician_incentive_detail`, `bank_account` except to the disbursement rail | `05-04` §5 |
| **PR-6** | **Recovered customer data or its index** (`M06`, T5, S3) to anyone, ever | `05-04` §4, `05-06` §6.4 |
| **PR-7** | Biometric templates | `05-06` §6.4, `NFR-099` |
| **PR-8** | Call recordings, except to the telephony processor that holds them under contract | `05-04` §5 |
| **PR-9** | Device make, model or fault detail to a **courier** | Not necessary to deliver a package; §4.5.3 |
| **PR-10** | A residency-classified field where the `NFR-086b` gate is unsatisfied | `NFR-086b`, `CB-1` |
| **PR-11** | Any field on a row whose status is `Undetermined` | `DS-01` |
| **PR-12** | Personal data for **model training** without a recorded ground and, where applicable, specific consent | `LR-4`; `INT-043` is self-hosted, which is why it is `Determined` |

**These twelve are the negative-test set** `TS-017` derives disclosure cases from. Each is
mechanically checkable against a payload.

### 4.8 Egress logging and audit

`IP-10` and `FR-IPF-044` require egress to be logged. `NFR-095` requires processing records for a
minimum of five years.

| # | Requirement |
|---|---|
| **EL-1** | Every outbound disclosure of personal data is logged: counterparty, integration, purpose, field set, record count, timestamp, correlation id |
| **EL-2** | The log records the **field set**, not the payload. Logging the payload creates a second copy of the personal data — which is itself processing (`OPS-04`) |
| **EL-3** | Retained **at least five years** (`NFR-095`) |
| **EL-4** | Reported monthly as the **egress and data-minimisation log** (`M28` §14) to CTO and Quality Manager |
| **EL-5** | A disclosure with no matching register row is an **exception** and is alerted, not absorbed |
| **EL-6** | The log is a **data-subject request input**: "who did you give my data to" is answered from it (`NFR-093`, `LG-010`) |
| **EL-7** | Bulk disclosure requires approval and step-up, and is logged with the requester and purpose (`EA-12`, `FR-SEC-041`) |

### 4.9 Review, DPIA and processor contracts

| # | Requirement | Status |
|---|---|---|
| **RV-1** | Every row reviewed **annually**, and on any change to the integration, the purpose or the statute | Cadence set here |
| **RV-2** | An integration may not be **promoted to production** until its rows are `Determined` (`AP-010` `P-02`) | **This is the register's enforcement mechanism** |
| **RV-3** | A **Data Protection Impact Assessment** is required for high-risk processing — INT-034 NID verification, INT-045 speech-to-text, INT-037 ad delivery, and the marketplace seller KYC set | **No DPIA exists or is scheduled** — `O-03` |
| **RV-4** | Every processor carries equivalent obligations by contract, flowed to sub-processors (`NFR-098`) | **No processor inventory or contract review exists** — `O-03` |
| **RV-5** | The register feeds the **transparency notice** third-party-transfer section (`NFR-092`, `LG-008`) | Dependency stated; `LG-008` must cite this register |
| **RV-6** | A **Chief Data Officer** must be appointed if 1000FiX is a significant data fiduciary (`NFR-096`) | **The classification has not been made and the role is unappointed** — `O-06` |

### 4.10 Endpoint reference

The endpoint reference table required by `CG-009` §3.

| Endpoint / surface | Method | Purpose | Owner | Tier |
|---|:--:|---|:--:|:--:|
| Egress and data-minimisation log | — | Monthly report: what data left, to whom, under which integration (`M28` §14) | `M28` | Internal |
| `/api/v1/platform/integrations` | GET | The 47-integration register with owner, pattern and fallback — **joins to this register** | `M28` | T-Int |
| Counterparty disclosure extract | — | **Generated** from this register, filtered to one counterparty (`AP-001` §4.8, §9) | Platform | **T-Part** |
| `/api/v1/platform/trace/{correlation_id}` | GET | End-to-end trace — **masks S3 and residency-classified fields** (`M28` §13) | `M28` | T-Int |

**The counterparty extract is generated, never re-authored.** A brand sees their own rows; a
courier sees theirs. Re-authoring per counterparty would produce the two-descriptions defect
`CP-01` forbids, and here it would produce two *legal* positions.

### 4.11 The `data.*` error family

Codes are `AP-006`'s §4.5 (`CP-01`). This states what each means as a **disclosure decision**.

| Code | HTTP | Disclosure meaning | Caller remedy |
|---|:--:|---|---|
| `data.disclosure_not_permitted` | `403` | The field is not on this counterparty's register | **None available to the caller.** `DS-01`; widening is a legal decision |
| `data.minimisation_refused` | `403` | More fields were requested than the purpose requires | Request only what the purpose needs (`DS-03`) |
| `data.consent_absent` | `403` | The `LG-2` or `LG-2S` ground is not satisfied for this subject | Consent is obtained through the customer's own channel, never through the counterparty |
| `data.residency_restricted` | `451` | A residency-classified field, and the `NFR-086b` gate is unsatisfied | None available. `PR-10` |
| `data.subject_request_pending` | `422` | An in-flight data-subject request affects the record | Retry after resolution (`LG-010`) |
| `data.retention_expired` | `422` | The record passed its retention period and was purged | Not recoverable (`LG-009`) |

**`451` is used deliberately for `data.residency_restricted`** — it is the status for a refusal on
legal grounds, and it distinguishes a statutory block from an authorisation failure, which matters
when a partner escalates.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-03` §2, IP-10 | The 47 integrations and the minimisation rule |
| `05-06` §6.3, §6.4 | The PDPA obligations and the residency-classified field list |
| `05-02` §10 | S0–S3 classification |
| `05-04` §5, §8 | Field-level restrictions and `EA-01`…`EA-12` |
| `M28` `FR-IPF-044` | The enforcement point. This register configures it |
| `M29` | Field-level encryption, access logging, residency enforcement at write time |
| `M60` | Governance, risk and compliance; breach notification (`NFR-094`) |
| **`LG-008`** | The transparency notice, whose third-party-transfer section comes from here (`RV-5`) |
| `LG-009`, `LG-010`, `LG-012` | Retention, data-subject requests, and the residency legal position |
| `AP-005` | Scope must never exceed disclosure |
| `AP-006` §4.5 | The `data.*` codes |
| `AP-007` §4.9, `AP-008` §4.9 | The prose boundaries this register makes enforceable |
| `AP-010` `P-02` | The promotion gate that makes `RV-2` real |
| `MM-002` | Screenshot and photograph redaction — the leak path in §4.5.6 |
| `TS-017` | Derives disclosure negative cases from §4.5 and §4.7 |
| `RF-008` | External standards and regulatory currency for the statutes cited |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Annually**, and on any change to an integration, a purpose or a statute (`RV-1`). Class B content is re-opened by a statutory change automatically (`CG-006` §5) |
| Trigger for out-of-cycle review | A new integration · a change to `NFR-086`'s field list · the `DEP-31` legal opinion landing · Authority guidance · a breach or near-miss · a data-subject request revealing an unregistered disclosure |
| Owner | **Security Lead with Legal Counsel.** Legal Counsel is the approver (`CG-002` §5.2) |
| Change control | **Every row change requires Legal Counsel approval and a `RF-006` entry.** Moving a row from `Undetermined` to `Determined` is a legal determination, not an engineering one. Adding a counterparty requires a DPIA screening (`RV-3`) |
| Sign-off record | Held in `LG-001` per `CM-R7` and `CG-007` |
| Version pinning | Pinned to **statutory currency**, not to API version — the exception to `CG-006` §5's `AP` rule, because this is Class B content |

---

## Approval Record

Required by `CM-R7` and `CG-007` for Class B content. **Not yet signed.**

| Role | Name | Date | Scope of sign-off |
|---|---|---|---|
| Legal Counsel *(approver)* | — | — | Lawful grounds, the `LG-1`…`LG-4` vocabulary, and every `Determined` row |
| Security Lead *(owner)* | — | — | Field sets, prohibitions, egress logging |
| CFO | — | — | Risk acceptance for `RSK-032` exposure |
| Data Protection Officer | **Unappointed** | — | `NFR-096` — see `O-06` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Nine of fifty-three counterparties have a determined register; thirty-eight cannot be specified yet** because their integrations are not designed. Under `DS-01` and `RV-2` that is workable **only if the promotion gate holds** — an integration reaching production with `Undetermined` rows silently defeats the whole control. The register must be maintained wave by wave, not authored once | Security Lead with Platform Engineering Lead | **Per wave, from W3** |
| **O-02** | **The three W3 courier integrations are `Undetermined` and carry customer name, phone and address.** Under `DS-01` no consignment may be booked with Pathao, RedX or Steadfast/Sundarban until their rows are determined and their processor contracts are in place (`NFR-098`). **This blocks W3 pick-and-drop**, and `G3-07` requires unbroken custody with zero exceptions in the same wave | Legal Counsel with `M03` owner | **W3 minus 3 months — blocking** |
| **O-03** | **No DPIA exists and no processor-contract inventory exists.** `RV-3` identifies at least four high-risk processing activities requiring assessment; `NFR-098` requires equivalent obligations flowed by contract to every processor and sub-processor. **Neither has an owner, a schedule or a budget** | Legal Counsel with `M60` owner | **W3 — and before 13 May 2027, when enforcement activates** |
| **O-04** | **INT-034 NID verification is the highest-risk row and satisfies none of its three preconditions** — `LG-2S` specific consent, the `NFR-086b` Authority notification and safeguard, and confirmation of a Bangladesh-resident service. `NFR-099`'s "large-scale" threshold is also undefined. The integration is W7 and is the control the marketplace trust model rests on | Legal Counsel with CTO | **W7 minus 6 months** |
| **O-05** | **`EA-04`'s "defined period" after which a marketplace seller loses access to customer contact details is not defined anywhere.** Without a number, the marketplace's most obvious data-protection control does not exist | Marketplace Operations with Legal Counsel | **W7 minus 3 months** |
| **O-06** | **No Data Protection Officer or Chief Data Officer is appointed, and the significant-data-fiduciary classification has not been made** (`NFR-096`). The classification determines the penalty ceiling — BDT 25 lakh or BDT 50 lakh — and the role is a reviewer of this file | CEO with Legal Counsel | **W3** |
| **O-07** | **Disclosure of 1000FiX employee personal data to clients and partners has no evidenced basis.** §4.5.7 discloses a technician's name and photograph to a corporate client; §4.5.6 discloses certification status to a brand. Both are recorded as `LG-1` on an assumed employment basis that HR has not evidenced | HR Manager with Legal Counsel | W4 |
| **O-08** | **INT-003's disclosure set should be re-examined.** Hosted checkout takes name, email, phone and address on the acquirer's requirement rather than ours — the largest personal-data egress of the nine rails, justified by someone else's product design. A lower-disclosure integration option should be assessed before W3 build | Treasury with Security Lead | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] **Class B treatment applied — Legal Counsel as approver, approval record block, `LG-001` sign-off route (`CM-R7`, `CG-007`)**
- [x] Seven principles, with refusal as the default
- [x] Row structure defined per field, per counterparty, **per purpose** — as `NFR-090` requires
- [x] **`Undetermined` established as a real status that blocks disclosure, not a placeholder**
- [x] All twelve counterparty classes inventoried across the 47 integrations and 6 portal audiences
- [x] Five lawful grounds with five rules, including the refusal to use legitimate interest as a fallback
- [x] Nine completed field-level registers with necessity argued per field
- [x] **The 38 unspecifiable counterparties counted and explained, not hidden (`CP-11`)**
- [x] Residency and cross-border gate stated as a precondition, with the Ordinance No. 23 narrowing recorded
- [x] Twelve absolute prohibitions, each mechanically checkable for `TS-017`
- [x] Egress logging specified, including the rule against logging the payload itself
- [x] DPIA, processor-contract and CDO obligations recorded as absent rather than assumed
- [x] `data.*` errors explained as disclosure decisions, referencing `AP-006`
- [x] Every statute cited with a verification date (`CG-012`, `CM-R8`)
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-02` three W3 couriers undetermined — outstanding; blocks W3 pick-and-drop under `DS-01`**
- [ ] **`O-03` no DPIA and no processor-contract inventory — outstanding; `NFR-098` is unmet**
- [ ] **`O-04` INT-034 NID verification satisfies none of its three preconditions — outstanding**
- [ ] **`O-06` no DPO appointed and no fiduciary classification made — outstanding**
- [ ] **Named approver recorded — pending Legal Counsel. `CM-R7`: this file cannot reach `Approved` without it**
- [ ] Bengali counterpart — n/a; developer and legal audience, English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
