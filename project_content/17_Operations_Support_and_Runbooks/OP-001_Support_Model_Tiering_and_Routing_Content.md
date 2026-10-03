---
id: OP-001
title: Support Model, Tiering and Routing Content
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Support Lead
author: Support Lead with Platform Engineering and Contact Centre
reviewers: [Chief Technology Officer, Operations Director, Contact Centre Supervisor, Internal IT, Account Management, Marketplace Ops, Procurement, Localisation Lead]
approver: Support Lead
content_class: C
purpose: >
  Names the one route to help for every population that uses the system — 800+ internal users
  and eleven external audiences — and the tier, queue, owner and response commitment behind each
  route. Without it, help is whoever answers first: the branch manager's mobile, a WhatsApp
  group, or the developer who built the screen. That model does not survive 51+ branches, and it
  leaves no record from which OP-016 can find a recurring cause.
traces_to: [M66, M05, M27, P03, P10, 05-04, 05-06 NFR-006, NFR-045, SP-005, SP-031, OP-013, OP-014, HC-015, MD-028]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md §3.1 items 1–8, §5 FR-ITS-008, FR-ITS-009, §11 Q-02, §11 Q-03
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md §1 — priority P2, delivery wave W6 (Months 23–26)
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-006 uptime 09:00–22:00 BST, NFR-045 24×7 uptime ≥ 99.7%, NFR-003 800+ concurrent internal users
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/02_Architecture/02-05 §6 — cloud telephony/CPaaS serving hotline 16743
    verified: 2026-08-20
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md — service priority and severity scales, escalation_at_pct
    verified: 2026-08-20
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md §4 — escalation destinations and out-of-hours cover
    verified: 2026-08-20
    class: P1
  - source: ITSM tiered support and escalation practice, as recorded in M66 §4 benchmarking of ServiceNow ITSM
    verified: 2026-08-20
    class: P3
supersedes: none
review_due: 2027-02-20
---

# OP-001 — Support Model, Tiering and Routing

> **Every user of this system must be able to answer one question without asking anyone: *where
> do I go when it does not work?*** This file is the answer, written once, for every population.
>
> English only. The audience is the support function and the queue owners ([`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2). The
> *user-facing* expression of this model — what a customer, technician or seller is actually told
> — lives in [`OP-003`](OP-003_Service_Desk_Macro_and_Canned_Response_Library.md) (macros), [`HC-015`](../09_Help_Centre_and_Self_Service/HC-015_FAQ_Bank_by_Audience.md) (contact routes) and [`UI-005`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-005_System_Permission_and_Session_Message_Library.md) (system messages), all of
> which are bilingual.

---

## 1. Purpose

`M66` states the position plainly: internal IT support today "runs on WhatsApp while clients get
a portal", and nothing about it is recorded — "not the problem, not the fix, not how long it
took, and not the fact that the same fault has occurred eleven times this month"
(`M66` §2, §11 risk register).

This file exists because that model has four consequences the programme cannot absorb:

| Consequence | Why it stops something |
|---|---|
| **No stated route** | A branch coordinator in Sylhet with a failed invoice print at 19:40 has no defined destination. They call whoever they know. The person they know may be on leave, may be a developer with production access they should not use, or may be nobody |
| **No record** | [`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md) can only find a recurring cause if incidents exist as records. Eleven occurrences of the same fault in a WhatsApp thread are eleven separate irritations |
| **No tier** | Every question reaches an engineer. At 800+ internal users (`NFR-003`) that consumes the engineering capacity the delivery waves depend on |
| **No commitment** | Without a stated response commitment, every requester escalates immediately, because escalation is the only lever they have |

**What stops without this file:** wave W1 cannot pass gate `G1-12` ("Runbooks and training materials
delivered", `06-02` §4), because a runbook set with no support model has no consumer; [`CM-007`](../16_Change_Management_and_Comms/CM-007_Hypercare_Communication_Pack.md)
(hypercare communication) has nothing to point at; [`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) has no boundary telling it which
events reach the on-call rota; and `HC-015` cannot publish contact routes it does not have.

---

## 2. Scope

**In scope:** the support tier model; the populations served; routing by audience, channel and
issue type; response and restoration commitments; hours of cover and the out-of-hours boundary;
the interim operating model for waves W1–W5 before `M66` exists; the queue register; and the
measurement set for support performance.

**Out of scope:**

| Situation | Owned by |
|---|---|
| Technical severity definitions (`Sev1`–`Sev4`) and the on-call rota | `OP-013` |
| Escalation destinations for operational, commercial, safety and legal paths | [`SP-005`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) |
| The internal service desk *procedure* — how a ticket is worked, changed and closed | [`SP-031`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) |
| Customer service SLA bands, priority and severity for **service orders** | [`MD-028`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) |
| Contractual SLAs and service credits for corporate clients | `M08`, [`LG-003`](../10_Legal_Policy_and_Compliance/LG-003_Portal_Terms_of_Use_Corporate.md) |
| Client-facing managed-services support (a paid product, not internal support) | `M05`, [`SP-011`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md) |
| The words used in a reply | `OP-003` |
| Where a customer is told to go for help | `HC-015`, `UI-005` |
| Access requests and their approval routing | [`OP-015`](OP-015_Access_Request_and_Joiner_Mover_Leaver_Content.md) |
| Incident and outage communication | [`OP-004`](OP-004_Incident_Communication_Template_Set.md), [`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md) |

> **`CP-01` boundary note.** `MD-028` owns *service* priority and severity — the scale that
> governs a customer's repair job. `OP-013` owns *platform incident* severity — the scale that
> governs the system itself. They are different scales measuring different things and must never
> be merged; §4.6 states the mapping between them, which is the only relationship they have.

---

## 3. Audience

| Reader | Uses this file to |
|---|---|
| Support Lead | Operate the model and staff it |
| Service desk analysts (T1) | Know what they resolve and what they pass on |
| Branch managers, coordinators, technicians | Know where to go, and what to expect back |
| Contact Centre supervisor (`P10`) | Separate customer service contacts from system-fault contacts |
| Platform Engineering | Know what reaches them, and in what state |
| Account Management, Marketplace Ops, Procurement | Know the route for their external population |
| Programme Office | Resource hypercare ([`OP-002`](OP-002_Hypercare_Plan_and_Exit_Criteria.md)) against a defined model |
| Internal Audit / Quality | Evidence that support is a controlled process (`ISO 9001:2015` cl. 8.5.1) |

---

## 4. Content

### 4.1 The populations served

`M66` §2 puts the internal population at "500–1,000 people across 51+ branches"; `NFR-003`
requires 800+ concurrent internal users. The register's phrase for the external side is "eleven
external audiences". That phrase is not enumerated anywhere upstream, so it is enumerated here
and this enumeration becomes the definitive one.

| # | Population | Est. size | Portal / channel | Language of support | Owning function |
|---:|---|---|---|---|---|
| — | **Internal — all staff** | 500–1,000 | `P03`, `P02`, `P09`, `P11`, branch desktops | Bengali and English | Support Lead |
| 1 | Consumer customers | 250,000+/month | `P01`, hotline **16743**, WhatsApp | **Bengali first** | Contact Centre (`P10`) |
| 2 | Corporate client **end users** | 500–2,000 | `P04` | English and Bengali | Account Management |
| 3 | Corporate client **administrators** | 50–200 | `P04` admin surfaces | English | Account Management |
| 4 | Marketplace sellers | 500–2,000 | `P07` | **Bengali first** | Marketplace Ops |
| 5 | Marketplace seller technicians | 1,000–4,000 | `P07` app surfaces | **Bengali first** | Marketplace Ops |
| 6 | Brand partners | 17+ | `P08` | English | Commercial / Warranty |
| 7 | Vendors and suppliers | 200–600 | `P05` | English | Procurement |
| 8 | Referral and alliance partners | 50–300 | `P12` | Bengali and English | Partnerships |
| 9 | Franchise and channel partners | 0–30 (from W8) | `P12` | Bengali and English | Commercial |
| 10 | Courier partners (`INT-024`…`INT-026`) | 3–6 organisations | `P09` integration surfaces | English | Logistics |
| 11 | Regulators, auditors and external verifiers | occasional | Named contact, no portal | English | Compliance / Legal |

> **Derivation declared ([`CG-012`](../00_Content_Governance_and_Standards/CG-012_Content_Sourcing_and_Evidence_Rules.md) §2).** Rows 1–11 are derived from the six external-facing portals
> in `04-00` plus the two non-portal counterparty groups that raise system-affecting contacts
> (couriers via integration, regulators via statutory request). The register's "eleven external
> audiences" is not enumerated upstream; if the Steering Committee's intended eleven differs, this
> table changes and `HC-015` follows it. Logged as open item **OP-001-OI-01**.

### 4.2 The tier model

Five tiers. The rule that makes tiering work is that **a tier only escalates when it has
exhausted its own scope**, and every escalation carries the diagnosis already done.

| Tier | Name | Who | Scope | Resolves | Escalates to |
|:--:|---|---|---|---|---|
| **T0** | Self-service | The user | Help centre, in-app guidance, known-error notices, status page | Password self-reset, "how do I", known issues with a published workaround | T1 |
| **T1** | Service desk | Service desk analysts; Contact Centre agents for customer contacts | First contact for every population. Triage, classify, record, resolve from the macro and known-error library | ≥ 60% of contacts at first touch (target) | T2 |
| **T2** | Application / domain specialist | Branch super-users, functional leads, `R33` IT Administrator | Configuration, master data, permissions, "the system did something unexpected in *this* process" | Process and configuration faults, data corrections within [`SP-004`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) authority | T3 |
| **T3** | Platform engineering | Platform Squad, on-call rota (`OP-013`) | Defects, integration failures, performance, infrastructure, anything requiring code or infrastructure change | Platform incidents; raises change records under `SP-031` | T4 |
| **T4** | Vendor / external | Gateway, telco, courier, hosting, KYC and e-signature vendors; `L6` suppliers | Faults inside a third party | Vendor-side resolution, tracked by T3 | — |

**Tier rules**

| # | Rule |
|---|---|
| **TR-01** | **Nothing skips T1.** Every contact is recorded at T1 first, including one raised by a director. The record exists before the fix does |
| **TR-02** | A tier that escalates records **what it ruled out**. An escalation with no diagnosis is returned once, with the reason |
| **TR-03** | **T3 is paged, not queued, only for `Sev1` and `Sev2`** (`OP-013` §4.1). Everything else reaches T3 as a queued ticket |
| **TR-04** | T2 and T3 never change production configuration outside an approved change record (`SP-031` §5, `BRU-ADM-02`) — including during an incident, where the emergency-change path applies |
| **TR-05** | **Ownership does not transfer with escalation.** T1 retains the requester relationship and the update obligation until closure |
| **TR-06** | A contact that arrives at the wrong tier is **routed, not rejected**. Rejection is how populations learn to bypass the model |
| **TR-07** | Any tier may **declare** an incident (`OP-013` §4.5). Declaration authority is deliberately wide; de-escalation authority is not |
| **TR-08** | External populations never reach T3 directly. Their route ends at their owning function (§4.1), which raises the ticket |

### 4.3 Routing — audience × contact type

The routing table is the operational core of this file. It is implemented as queue configuration
in `M66` from W6, and as the interim queues in §4.9 before that.

| Audience | Contact type | Channel | Lands in queue | Tier | Owning function |
|---|---|---|---|:--:|---|
| Internal — any staff | System fault, error, "it is broken" | Service desk portal · `it@` mailbox · hotline extension | `Q-IT-INCIDENT` | T1 | Support Lead |
| Internal — any staff | Access request, new user, permission change | Service desk portal request form (`OP-015`) | `Q-IT-ACCESS` | T1 → approver | Security + HR |
| Internal — any staff | Equipment, device, printer, scanner | Service desk portal | `Q-IT-ASSET` | T1 | Internal IT |
| Internal — any staff | "How do I…" | Help centre first; then service desk | `Q-IT-HOWTO` | T0 → T1 | Support Lead |
| Internal — branch/front desk | Master data wrong (branch, price, part, customer) | Service desk portal | `Q-DATA` | T2 | MDM (`M64`) |
| Internal — finance | Invoice, tax, posting, reconciliation defect | Service desk portal | `Q-FIN-APP` | T2 | Finance Systems |
| Internal — technician (`P02`) | App fault, sync failure, GPS, offline | In-app "report a problem" | `Q-MOBILE` | T1 | Support Lead |
| Internal — dispatcher | Dispatch board, routing, assignment fault | Service desk portal, flagged operational | `Q-DISPATCH` | T2 | Service Operations |
| Consumer customer | Service complaint, job query | Hotline 16743, `P01`, WhatsApp | Contact Centre (`P10`) queues | T1 | Contact Centre |
| Consumer customer | **Portal or app fault** | Same channels, agent reclassifies | `Q-EXT-PORTAL` | T1 → T3 | Support Lead |
| Corporate user / admin | Any | `P04` support form → Account Manager | `Q-CORP` | T1 | Account Management |
| Marketplace seller | Onboarding, payout, listing, app fault | `P07` support form | `Q-SELLER` | T1 | Marketplace Ops |
| Brand partner | Claim, portal, integration | `P08` support form or named contact | `Q-BRAND` | T1 | Warranty / Commercial |
| Vendor / supplier | PO, invoice, portal | `P05` support form | `Q-VENDOR` | T1 | Procurement |
| Referral / franchise partner | Attribution, payout, access | `P12` support form | `Q-PARTNER` | T1 | Partnerships |
| Courier partner | Integration failure, consignment sync | Named technical contact → T3 ticket | `Q-INTEG` | T3 | Platform Engineering |
| Regulator / auditor | Statutory request, evidence | Named contact only — never a queue | — | — | Compliance / Legal ([`LG-024`](../10_Legal_Policy_and_Compliance/LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md)) |
| Any | **Suspected security or data incident** | Any channel, immediately | `Q-SEC` **and** page `OP-013` | T3 | Security (`M29`) |
| Any | **Safety incident** | [`SP-030`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) path, not this model | — | — | HSE |

> **Two routes bypass tiering by design.** A suspected security or data-protection incident goes
> to `Q-SEC` *and* pages the on-call simultaneously — the notification duty in `NFR-094` runs on a
> statutory clock that a queue wait would consume (`OP-016` §6). A safety incident leaves the
> support model entirely and follows `SP-030`; support's only duty is to route it there within
> the same contact.

### 4.4 Channel register

| Channel | Populations | Hours | Recorded automatically | Notes |
|---|---|---|:--:|---|
| Service desk portal (`P03` → `M66` from W6) | Internal | 24×7 intake | ✔ | The primary intake. All others exist to feed it |
| `it@1000fix…` mailbox | Internal | 24×7 intake | ✔ (parsed to ticket, `INT-013`) | Retained because email works when the portal does not |
| Hotline **16743** | Consumers, and internal by extension | Per Contact Centre roster | ✔ from W4 (`INT-015`) | Before W4, logged manually by the agent |
| In-app "report a problem" | `P01`, `P02`, `P07`, `P09`, `P11` | 24×7 intake | ✔ | Carries device, version, connectivity and last-sync context automatically — the single highest-value channel for mobile faults |
| Portal support forms | All external portals | 24×7 intake | ✔ | Per-audience forms, routed per §4.3 |
| WhatsApp (`INT-012`) | Consumers | Per Contact Centre roster | ✔ | Customer service only. **Not a support channel for internal staff** |
| On-call page (`OP-013`) | System-generated ([`NT-021`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md)) and T1/T2 escalation | 24×7 | ✔ | Never a user-facing channel |
| Branch WhatsApp groups | — | — | ✘ | **Withdrawn at W1 for support use.** Retained for operational coordination only. See [`CM-005`](../16_Change_Management_and_Comms/CM-005_Wave_Launch_Communication_Kit.md) |

> **`CH-01`.** A channel that does not produce a record is not a support channel. The withdrawal of
> WhatsApp groups as a support route is the single behavioural change this file requires, and it
> will fail unless the portal route is faster than the group. That is a design constraint on `M66`,
> not an instruction to users.

### 4.5 Response commitments

These are **internal support commitments**, distinct from contractual customer SLAs (`M08`,
`LG-003`) and from service-order SLA bands (`MD-028`). They are stated per platform-incident
severity (`OP-013` §4.1) for faults, and per request class for requests.

**Faults (incidents)**

| Severity (`OP-013`) | Acknowledge | First substantive update | Update cadence | Restoration target | Cover |
|:--:|---|---|---|---|---|
| **Sev1** | 15 min | 30 min | 30 min, and on every change of state | ≤ 2 h (`NFR-007` RTO where failover applies) | 24×7 |
| **Sev2** | 30 min in hours · 60 min out of hours | 2 h | 2 h | ≤ 8 working hours | 24×7 page, business-hours work unless customer-affecting |
| **Sev3** | 4 working hours | 1 working day | Daily | ≤ 5 working days | Business hours |
| **Sev4** | 1 working day | On triage | On change | Next planned release | Business hours |

**Requests**

| Request class | Target | Notes |
|---|---|---|
| Password / MFA reset (self-service failed) | 30 min in hours | [`OP-009`](OP-009_Runbook_Identity_and_Access.md) §6 governs the identity-proofing step |
| Standard access profile grant (`OP-015`) | 1 working day **after approval** | The approval wait is not counted; approval latency is reported separately |
| Non-standard access | 3 working days after approval | Requires `SP-004` authority |
| Device / equipment | 5 working days | Subject to stock (`M66` §3.1 item 14) |
| Report or data extract | 3 working days | Standing requests move to [`RP-013`](../14_Reporting_Analytics_and_KPI/RP-013_Scheduled_Report_and_Subscription_Catalogue.md) |
| Master data correction | 1 working day | Within `SP-004` authority; otherwise routed to approval |

**Business hours** for support are **09:00–22:00 BST, seven days**, matching the uptime window in
`NFR-006`. Out-of-hours cover is the on-call rota only (`OP-013`), and it exists for `Sev1` and
`Sev2` — not for requests.

> **Stated openly:** the restoration targets above are **support commitments, not contractual
> ones**, and they have not been agreed with the business. `M66` §11 Q-03 records the same gap
> ("an SLA IT sets alone is a target, not an agreement"). Ratification is open item
> **OP-001-OI-02**.

### 4.6 The only relationship between the two severity scales

A platform incident can breach service SLAs without being a service incident, and vice versa.
The mapping below is the *only* sanctioned relationship; nothing else may be inferred.

| Platform event (`OP-013`) | Effect on service SLA (`MD-028`) | Who decides |
|---|---|---|
| `Sev1` affecting job creation, dispatch or the technician app | SLA clocks for affected jobs are **paused for the outage duration**, applied in bulk, evidenced by the incident record | Operations Director on the incident record |
| `Sev1`/`Sev2` affecting invoicing or payment only | No SLA pause — service delivery continues; finance catches up under [`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md) | Finance Controller |
| `Sev3` with a working fallback | No effect | — |
| Any severity | **Never** silently adjusts a customer's SLA band | — |

> This is the mechanism `MD-028`'s `pause_conditions` field exists to carry. A pause with no
> incident record behind it is an unevidenced SLA adjustment and will be found by `M23` audit.

### 4.7 Staffing model

`M66` §11 Q-02 records the open question directly: *"How many IT staff are there, and what is the
intended tier structure? A tiered model with escalation paths requires enough people to have
tiers."* This file cannot answer it, but it can state what the model requires so the answer can be
costed.

| Tier | Requirement at W1 (pilot, ~150 users) | At W4 (~500 users) | At W8 (800+ users, all portals) |
|---|---|---|---|
| T1 service desk | 2 FTE, 09:00–22:00 shifted | 4 FTE | 6–8 FTE |
| T2 specialists | Named part-time role in each domain (finance, ops, data) — ~1.5 FTE total | 3 FTE | 4–5 FTE |
| T3 platform | Delivery engineers on rota (no separate ops team) | 2 dedicated + rota | 3–4 dedicated |
| Champion network ([`CM-008`](../16_Change_Management_and_Comms/CM-008_Champion_and_Super_User_Network_Kit.md)) | 1 per pilot branch | 1 per branch | 1 per branch, 51+ |

> **Consequence if unfunded.** With no T1, every contact reaches T2 or T3 and the tier model
> degrades into the WhatsApp model with a ticket system attached. The register's `P0` on this file
> is a statement that the *model* is blocking; the *staffing* to run it is outside content's
> control and is escalated as open item **OP-001-OI-03**.

### 4.8 Known-error and deflection loop

Support content is not a by-product of support; it is the mechanism that stops the second
occurrence reaching a human.

| Step | Action | Produces | Lands in |
|---:|---|---|---|
| 1 | T1 resolves a contact using an unwritten answer | A candidate macro | `OP-003` backlog |
| 2 | The same contact recurs 3× in 30 days | A known error with a published workaround | `OP-005` (if customer-visible), `HC` set, `KB` article |
| 3 | The known error has a permanent fix | A problem record | `SP-031` §8 problem management |
| 4 | Deflection is measured | First-contact and self-service resolution rate | [`CG-014`](../00_Content_Governance_and_Standards/CG-014_Content_Metrics_and_Effectiveness_Measurement.md), `M66` FR-ITS-030 |

**Rule `DF-01`:** any contact type reaching T1 more than **20 times in a month** must have a macro
(`OP-003`) and a help article (`HC`) within one further month, or the Support Lead records why not.

### 4.9 The interim model, waves W1–W5

**This is the most important operational fact in this file.** `OP-001` is `P0` at **W1**. The
module it traces to, `M66`, is `P2` at **W6** (`M66` §1, verified 2026-08-20). The support model
therefore has to run for roughly twenty months with no ITSM platform behind it.

| Capability | W6+ (target, `M66`) | **W1–W5 interim** | Consequence of the interim |
|---|---|---|---|
| Ticket intake | Employee self-service portal | OCA `helpdesk` queue in `P03` (already deployed for `M01`/`M05`) + `it@` mailbox parsing | Adequate. This is the same substrate `M66` will later build on (`M66` §12) |
| Queues per §4.3 | Configured service catalogue | `helpdesk` teams named exactly as the `Q-*` codes above | Reporting is by team, not by service |
| SLA clock | `M66` SLA engine, calendar-aware | `helpdesk` SLA policies, **without** holiday-calendar awareness | SLA attainment over public holidays will be wrong. Do not report it as a KPI before W6 |
| Escalation on breach | `FR-ITS-008` automatic | Manual, by the T1 supervisor, from a daily breach-risk view | Depends on a person. Names a single point of failure — mitigate with the daily review in §4.11 |
| Known errors | `M66` known-error database | `KB` articles tagged `known-error` | Workable; discoverability is weaker |
| CMDB | `M66` CMDB | None. [`OP-007`](OP-007_Runbook_Core_ERP_Platform.md)…[`OP-011`](OP-011_Runbook_Portal_and_Mobile_App_Operations.md) runbooks are the substitute | Impact assessment during an incident is manual |
| Asset register | `M66` IT asset management | Spreadsheet register held by Internal IT | **Accepted risk**: the `100% of company IT assets tracked` KPI cannot be evidenced before W6 |
| Change process | `M66` change management | `SP-031` executed manually with a change register | Works, but audit evidence is weaker |

> **Register consequence.** The Master Index shows `OP-001` tracing to `M66` with no note that the
> traced module lands five waves later. That is a register defect, not an authoring defect, and it
> is raised as a finding in the Category 17 audit. The correct trace for W1–W5 is **`M01` + OCA
> `helpdesk` in `P03`**; `M66` becomes the trace from W6.

### 4.10 What support is not permitted to do

| Prohibition | Why | Reference |
|---|---|---|
| Change production configuration without a change record | Untraceable production state; audit failure | `SP-031` §5, `BRU-ADM-02` |
| Grant access outside `OP-015` because the requester is senior or urgent | The most common insider-risk finding | `SP-004` A-85/A-86 |
| Read or export customer personal data to "check" an issue | Purpose limitation; `05-06` §6.3 `NFR-090` | [`LG-010`](../10_Legal_Policy_and_Compliance/LG-010_Data_Subject_Request_Handling_Content.md), `M29` |
| Resolve a ticket the requester has not confirmed, to protect an SLA figure | Corrupts the measure and the trust in it | `CG-014` |
| Share a screenshot containing personal data in a support channel | Alert and channel audiences are wider than record audiences | `NT-021` AL-03 |
| Tell a customer an outage is over before `OP-005` says so | Two sources of truth during an incident | `OP-004` §3 |

### 4.11 Measurement

| Measure | Definition | Target | Source | Cadence |
|---|---|---|---|---|
| First-contact resolution (T1) | Closed by T1 with no reassignment ÷ all T1 contacts | ≥ 60% | Ticket system | Weekly |
| Internal tickets within SLA | Per `M66` FR-ITS-009 | **> 92%** | `M66` (from W6) | Monthly |
| Escalation accuracy | Escalations accepted by the receiving tier ÷ all escalations | ≥ 90% | Ticket system | Monthly |
| Route compliance | Contacts arriving via a recorded channel ÷ estimated total contacts | ≥ 85% by W4 | Ticket system + spot survey | Quarterly |
| Deflection | Self-service resolutions ÷ (self-service + T1 contacts) | ≥ 30% by W6 | `HC`, `M66` | Monthly |
| Reopen rate | Reopened within 7 days ÷ closed | < 5% | Ticket system | Monthly |
| Breach-risk review completed | Daily during W1–W5 interim | 100% | Support Lead log | Daily |

`KPI` linkage: `M66` §9 carries "internal IT tickets resolved within SLA > 92%" as the category
KPI; nothing in `06-02` carries a support-model KPI, so the remaining measures above are content
-owned and reported through `CG-014`.

### 4.12 Open decisions

| # | Decision required | Owner | Needed by | Consequence if unresolved |
|---|---|---|---|---|
| **OP-001-OI-01** | Confirm or correct the enumeration of the eleven external audiences (§4.1) | Programme Office | W1 | `HC-015` publishes contact routes for a population set that may be wrong |
| **OP-001-OI-02** | Ratify the response commitments in §4.5 with the business (`M66` Q-03) | CTO + Operations Director | W1 | Targets are IT's opinion; escalation has no agreed trigger |
| **OP-001-OI-03** | Fund the T1 staffing in §4.7 | CTO + CFO | W1 | The tier model collapses into direct-to-engineer support |
| **OP-001-OI-04** | Confirm the withdrawal of branch WhatsApp groups as a support route, and who enforces it | Operations Director | W1 | The recorded channel competes with an unrecorded one and loses |
| **OP-001-OI-05** | Confirm whether Contact Centre agents (`P10`) act as T1 for internal contacts out of hours, or only for customers | Contact Centre Supervisor + Support Lead | W2 | Out-of-hours internal contacts have no destination below the on-call rota |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M66` Internal IT Service Management | The platform this model runs on from W6; the interim substitute is §4.9 |
| `M01` / OCA `helpdesk` in `P03` | The W1–W5 interim ticket substrate |
| [`MD-009`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md) Role and Job Title Master | Queue ownership and tier membership are expressed as roles |
| `MD-028` Priority, Severity and SLA Definition Register | The service-side scale this file maps to in §4.6 |
| `SP-005` Escalation Matrix | Named escalation destinations beyond the support tiers |
| `SP-031` SOP IT Service Desk and Change Management | How a ticket is actually worked |
| `OP-013` On-Call, Escalation and Handover | Severity definitions, the rota and paging |
| `OP-003` Macro and Canned Response Library | The words T1 uses |
| `OP-015` Access Request and JML | The request path for the largest single request class |
| `HC-015` | The customer-facing statement of these routes |
| `CM-007` Hypercare Communication Pack | Reuses this model's routes during hypercare |
| `05-06` NFR-006, NFR-045, NFR-003 | Hours of cover and population size |

**Depended on by:** `OP-002` (hypercare staffs against these tiers) · `OP-003` · `OP-004` ·
`OP-013` · `OP-016` · `CM-007` · [`TR-023`](../08_Training_and_Enablement/08B_Course_Packs/TR-023_Train_the_Trainer_and_Super_User_Kit.md) · `HC-015` · [`EO-001`](../18_Ecosystem_Onboarding_Content/EO-001_Marketplace_Seller_Onboarding_Kit.md)…[`EO-014`](../18_Ecosystem_Onboarding_Content/EO-014_Ecosystem_Offboarding_and_Exit_Content.md) (each external kit states
its support route from §4.3).

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly during W1–W6; six-monthly thereafter |
| Trigger for out-of-cycle review | Any new portal going live · any new external population · `M66` go-live at W6 · any change to hours of cover · two consecutive months below 85% route compliance · any `Sev1` where routing failed |
| Owner | Support Lead |
| Change route | [`CG-006`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) minor version for queue and target changes; major version for tier-model change, which requires re-approval by the CTO |
| Retirement | Superseded only by a successor support model; never withdrawn without one |

---

## Open Items

1. **OP-001-OI-01** — external audience enumeration unconfirmed (§4.1).
2. **OP-001-OI-02** — response commitments not agreed with the business (§4.5).
3. **OP-001-OI-03** — T1 staffing unfunded (§4.7).
4. **OP-001-OI-04** — WhatsApp withdrawal not yet mandated (§4.4).
5. **OP-001-OI-05** — out-of-hours internal T1 cover undecided (§4.12).
6. **Register defect** — the Master Index traces `OP-001` (`P0`, W1) to `M66` (`P2`, W6) with no
   lead-time note. Raised in the Category 17 audit.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present; `Open Items` added, justified by five unresolved decisions
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md); Bengali terms — n/a, English-only file
- [x] All internal links resolve
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — n/a; not user-facing. The user-facing expression is `HC-015`
- [x] Bengali counterpart — n/a; English-only by `CG-010` §3.2
- [ ] Named approver recorded — Support Lead not yet appointed (`AUDIT-001` R-07)
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — five open decisions and one register defect pending

**Gates required (Class C):** G1 Editorial ●, G2 Factual ●, G3 Technical ●. G4 not applicable.

---

*`OP-001` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
