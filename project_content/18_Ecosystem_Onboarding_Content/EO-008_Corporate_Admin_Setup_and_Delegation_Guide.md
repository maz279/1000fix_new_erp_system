---
id: EO-008
title: Corporate Admin Setup and Delegation Guide
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Account Management
author: Account Management with Content Design and the Master Data Owner
reviewers: [Chief Commercial Officer, Chief Financial Officer, Operations Director, Data Protection Officer, Master Data Owner, Security Lead, Localisation Lead, Content Design Lead]
approver: Content Design Lead with Account Management
content_class: D
purpose: >
  The guide a corporate client's own portal administrator uses to configure users, sites,
  departments, roles, scopes and multi-level approval chains — and to keep them working as people
  join, move and leave. Corporate administrators configure their own delegation chains; a chain
  with no reachable approver stops every request behind it, and the client experiences a
  configuration error they made as a 1000FiX outage. Approval deadlock is the single most common
  support escalation in self-administered B2B portals, and every one of its causes is preventable
  at configuration time.
traces_to: [P04, M08, M29, M07, M20, 04-00 P04, 04-00 PS-01, 04-00 PS-12, 05-04 §8 EA-01, EA-02, MD-015, MD-015 §2.1, MD-006, MD-007, MD-013, MD-021, MD-028, MD-036, LG-003, LG-008, LG-020, SP-004, SP-005, DT-020, UI-014, UI-040, HC-006, NT-010, OP-015, EO-007, EO-011, EO-014, CM-014, AP-008]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: EO-008_Corporate_Admin_Setup_and_Delegation_Guide_BN.md
sources:
  - source: project_content/02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md §2 node structure and maximum depth 5; §2.1 approval chain — level 1 requesting user, level 2 line manager, level 3 site or department head, level 4 1000FiX account manager only where the contract requires counter-approval; "chains are defined per node and inherit downward unless overridden"; §4 CAH-01 depth and cycles, CAH-02 at least one billing node, CAH-03 billing node needs cycle and address, CAH-04 site node needs an address, CAH-05 an approval chain must terminate — a chain with no final approver is rejected, CAH-06 a node may not be archived while it has open service orders or unbilled charges, CAH-07 changing a billing node mid-cycle requires Finance approval
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P04 Account capability "multi-user access under one corporate account · role assignment · multi-level approval chains (user → line manager → 1000FiX admin) · multiple sites and departments"; Service capability "approve estimates within delegated authority"; PS-01 single sign-on through M29, PS-12 session, idle timeout and MFA policy inherited from M29
    verified: 2026-08-18
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md — the internal delegation-of-authority model this guide mirrors for the client side, including the treatment of absent approvers and escalation on timebox
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 4 G4-05 "10+ corporate clients transacting on the B2B portal"
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Corporate Admin Setup and Delegation Guide

| Item | Value |
|---|---|
| Audience | The **client's own** portal administrator — not a 1000FiX role |
| Population | One to three administrators per corporate client; 500–2,000 client users under them |
| Portal | `P04` Corporate B2B Portal |
| Language | **Bilingual** — administrators at site level frequently work in Bengali |
| Wave | W4 · Months 14–18 |
| Handed over from | **`EO-007` stage 6.** This guide begins where the onboarding kit stops |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The three `EO` additions are applied to a configuration task rather than
> to an admission: §4.1 is the **journey** an administrator follows to build a working
> configuration, §4.5 is the **checklist** — a pre-flight deadlock test — and §4.7 is the
> **first 90 days** of keeping it working. Declared; template 15 does not exist.

---

## 1. Purpose

The Master Index states the consequence exactly: *"corporate admins configure their own delegation
chains; errors here produce approval deadlocks the company gets blamed for."*

That sentence contains the whole design problem. **The client makes the error and 1000FiX
experiences the escalation.** A department head goes on leave without a delegate, forty repair
estimates queue behind them, and the call that follows is not "our approval chain is
misconfigured" — it is "your portal is broken".

`MD-015` prevents exactly one deadlock at the data layer: `CAH-05` rejects a chain with no final
approver. **Every other deadlock is structurally valid and operationally fatal**, and none of them
is caught by a validation rule:

| Configuration | Valid? | Deadlocks? |
|---|:--:|:--:|
| A chain terminating in one person, on leave, with no delegate | ✔ | **Yes** |
| A chain whose final approver's authority is below the amounts routed to them | ✔ | **Yes** |
| A site with no chain, inheriting one from a parent whose approver has no visibility of that site | ✔ | **Yes, silently** |
| A chain terminating in a person who has left the client organisation | ✔ | **Yes** |
| Two administrators each assuming the other maintains the chains | ✔ | **Yes, eventually** |

This guide exists to make those five configurations visible to an administrator **before** they
are saved, and to give them a routine that catches the sixth one nobody predicted.

---

## 2. Scope

**In scope.** The configuration sequence; users, roles and scope; sites and departments as an
administrator maintains them (not as they are first built); approval chains — levels, authority
limits, inheritance and override; the deadlock pre-flight test; delegation and absence cover;
joiner, mover and leaver handling on the client side; what an administrator can and cannot change;
change control on the four decisions `EO-007` §4.2 marks as expensive; the quarterly review
routine; and what to do when a request is already stuck.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| The initial account build, estate upload and welcome material | **`EO-007`** |
| The hierarchy **as a data standard** and its validation rules | `MD-015` |
| Contract scope, coverage, SLA band and pricing | The contract; `LG-015`; `MD-028`, `MD-029` |
| Portal terms of use | `LG-003` |
| 1000FiX's **own** internal approval matrix and delegation of authority | `SP-004`; escalation `SP-005` |
| 1000FiX's internal joiner-mover-leaver process | `OP-015` |
| Identity, session, idle-timeout and MFA policy | `M29`; `PS-01`, `PS-12`; `LG-020` |
| Screen copy and in-product help | `UI-014`, `UI-040`, `HC-006` |
| Notifications | `NT-010` |
| The consolidated invoice | `DT-020` |
| Account closure, user deprovisioning at exit and data return | **`EO-014`** |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Client portal administrator** | The whole guide. This is the only `EO` file whose primary reader is not being onboarded but being trained to operate |
| **Client site administrator** | §4.2 scope, §4.6 joiner-mover-leaver for their own site |
| **Client finance owner** | §4.4 authority limits, and why a limit change is a change to what the portal will let their people commit to |
| **Client IT / security contact** | §4.2 access model, `PS-01` single sign-on and `PS-12` session policy |
| **1000FiX Account Manager (`R22`)** | The configuration they hand over, and the diagnosis they run when a client reports a "portal problem" |
| **1000FiX Support (`R34`, `M66`)** | §4.8's stuck-request diagnosis, so the first response is a diagnosis rather than an escalation |

---

## 4. Content

### 4.1 The configuration journey

| # | Step | What the administrator does | Validation that will stop them |
|---|---|---|---|
| **1** | **Confirm the structure** | Reviews the hierarchy built at `EO-007` stage 2 | Depth ≤ 5, no cycles (`CAH-01`) |
| **2** | **Create sites and departments** | Adds nodes as the organisation actually operates | A `site` node without an address is rejected (`CAH-04`) |
| **3** | **Add users** | One record per person, with an individual identity | **Shared logins are not permitted** — `CA-03` |
| **4** | **Assign roles and scope** | Role plus the node it applies at | A user with no scope sees nothing |
| **5** | **Set authority limits** | The value each approver may commit | An amount above every limit in the chain has nowhere to go — §4.4 |
| **6** | **Build approval chains** | Per node, level by level | **A chain with no final approver is rejected** (`CAH-05`) |
| **7** | **Set inheritance and overrides** | Decide which nodes inherit and which override | Inheritance is silent — §4.4 |
| **8** | **Name delegates** | A deputy for every approver | **Not enforced by any rule** — this is the deadlock — §4.5 |
| **9** | **Run the pre-flight test** | §4.5, before going live | — |
| **10** | **Test with a real request** | One low-value request through the full chain | The only proof that the configuration works |

> **Step 10 is not optional and is the step most often skipped.** A configuration that has never
> carried a request is a hypothesis.

### 4.2 Users, roles and scope

| Concept | Rule |
|---|---|
| **Identity** | One person, one login. `PS-01` single sign-on through `M29`; session, idle timeout and MFA policy are inherited (`PS-12`) and are **not** administrator-configurable |
| **Role** | What a person may do (`EO-007` §4.4) |
| **Scope** | Where they may do it — a node, and everything beneath it |
| **Boundary** | A user sees only their organisation, and only their scope within it (`EA-01`, `EA-02`) |
| **Multiple scopes** | A person responsible for three sites is scoped at the common parent, or given three scopes — **not given a higher scope for convenience** |

**The scope mistake that matters.** Scoping a requester at company level "so they can raise
anything" also shows them every site's estate, costs and invoices. `LG-003` and `LG-008` make
that the client's own data-protection decision, not ours, and the guide says so — administrators
routinely widen scope to solve a permissions complaint and create a privacy problem instead.

### 4.3 Sites and departments in life

The build is `EO-007`; the maintenance is here.

| Event | What the administrator does | Constraint |
|---|---|---|
| New site opens | Create the node with an address; assign a chain or confirm inheritance | `CAH-04` |
| Site closes | Move or close open requests, then archive | **A node cannot be archived while it has open service orders or unbilled charges** (`CAH-06`) |
| Department renamed | Rename the node; the client's cost centre code is separate and changes independently | `cost_centre_ref` prints on `DT-020` |
| Reorganisation | Re-parent nodes | Depth ≤ 5 and no cycles (`CAH-01`); **re-check every inherited chain afterwards** |
| Billing node moves | **Request through the account manager** | Mid-cycle changes require 1000FiX Finance approval (`CAH-07`) — this one is not self-service |

### 4.4 Approval chains

`MD-015` §2.1 defines four levels. Levels 1–3 belong to the client; level 4 belongs to 1000FiX and
exists **only where the contract requires our counter-approval**.

| Level | Who | Set by | Notes |
|---|---|---|---|
| 1 | Requesting user | Client | Not an approval — the origin |
| 2 | Line manager | Client | The commonest single point of failure |
| 3 | Site or department head | Client | Usually the terminal level |
| 4 | **1000FiX account manager** | **1000FiX** | Only where the contract requires it. **An administrator cannot add or remove level 4** |

**Three properties an administrator must understand, because none of them is visible on the
screen:**

| Property | What it means | Why it bites |
|---|---|---|
| **Chains are defined per node** | A chain belongs to a site or department, not to a person | Moving a person does not move the chain |
| **Chains inherit downward unless overridden** | A node with no chain uses its parent's | **A new site silently inherits a chain whose approver has never heard of it** |
| **A chain must terminate** | `CAH-05` rejects one that does not | It does **not** check that the terminal approver's authority limit is high enough for what will reach them |

**Authority limits and the gap `CAH-05` does not close.**

| Situation | Result |
|---|---|
| Amount within level 2's limit | Approved at level 2 |
| Amount above level 2, within level 3 | Escalates to level 3 |
| **Amount above every limit in the chain** | **The request has nowhere to go.** `CAH-05` is satisfied — the chain terminates — and the request still cannot be approved |

> **This is the deadlock that is legal at the data layer.** The pre-flight test in §4.5 catches it;
> nothing else does. `SP-004` handles the equivalent internally by requiring every authority
> schedule to have an unlimited terminal approver, and the client-side model has no such rule.

### 4.5 The pre-flight deadlock test

**Run before going live, and after any reorganisation.** Eight questions; any "no" is a deadlock
waiting for a date.

| # | Question | If no |
|---|---|---|
| 1 | Does every node have a chain, by definition or inheritance? | The request stops at submission |
| 2 | Does every chain terminate in a named person? (`CAH-05`) | Rejected at save — the only one the system catches |
| 3 | **Does the terminal approver's limit exceed the largest amount that can reach them?** | Deadlock at the first large estimate |
| 4 | **Does every approver have a named delegate?** | Deadlock the first time someone takes leave |
| 5 | Is any single person the sole approver for more than one node? | A single absence stops several sites |
| 6 | Does every approver have **visibility** of the nodes whose requests reach them? | They receive requests for a site they cannot see and cannot assess |
| 7 | Is any approver also the requester in their own chain? | Self-approval, which is the client's control failure and our audit finding |
| 8 | Has a real request travelled the full chain? (§4.1 step 10) | The configuration is untested |

**Question 4 is the one that fails in practice.** Nothing in `MD-015` requires a delegate, so an
administrator who does not read this guide will never be prompted for one — recorded as `O-01`.

### 4.6 Joiners, movers and leavers on the client side

The client's own version of `OP-015`. It is short because it is only ever neglected, never
difficult.

| Event | Same day | Within a week |
|---|---|---|
| **Joiner** | Create the user with role and scope | Add to any chain they belong in; name their delegate |
| **Mover** | Change scope and role | **Re-check every chain they appeared in** — as approver and as delegate |
| **Leaver** | **Deactivate the login** | **Replace them in every chain and delegation.** A leaver who is a terminal approver is a deadlock with a delay fuse |
| **Long absence** | Activate the delegate | Confirm the delegate's authority limit covers what will arrive |

> **The leaver case is the one that reaches 1000FiX as an incident.** Deactivation is remembered
> because it is a security instinct; chain replacement is forgotten because it is invisible until
> the next request. **Do both, in that order, in the same session.**

### 4.7 The first 90 days of running the configuration

| Days | What the administrator does | What it prevents |
|---|---|---|
| **0–30** | Pre-flight test passed; one real request through every distinct chain; delegates named | The first-month deadlock, which is the one that defines the client's opinion of the portal |
| **31–60** | First reorganisation or new joiner handled; **re-run questions 1, 3, 4 and 6** | The silent-inheritance deadlock |
| **61–90** | **First quarterly review** — every chain, every limit, every delegate, every leaver | Drift, which is the cause of every deadlock after month three |
| **Thereafter** | Quarterly, and after any reorganisation | — |

**A configuration decays even when nobody changes it**, because the organisation around it moves.
Three months is the interval at which a client's chains and their staff list have measurably
diverged.

### 4.8 When a request is already stuck

Given to administrators and to 1000FiX support, so both diagnose the same way.

| Symptom | Likely cause | Fix |
|---|---|---|
| Request submitted, no approver notified | Node has no chain and no inheritable parent chain | Assign a chain (§4.4) |
| Approver notified, cannot act | Amount exceeds their authority limit and there is no higher level | Raise the limit, or extend the chain (§4.4) |
| Approver notified, does not act | Absence with no delegate | Activate or create a delegate (§4.6) |
| Approver acts, request still queued | A later level is unreachable — a leaver, or a limit gap | Question 3 and question 4 |
| Approver cannot see the request's detail | Scope does not cover the requesting node | Question 6 |
| Everything looks correct and nothing moves | Chain inherited from a parent that was re-parented | Question 1, after a reorganisation |
| Only one site is affected | Overridden chain at that node | Compare against a working sibling node |

> **Route to the account manager only after this table is exhausted.** Seven of the eight causes
> are client-side configuration, and an escalation that arrives with the answers to §4.5's
> questions is resolved in minutes rather than days.

### 4.9 Rules

| # | Rule |
|---|---|
| **CA-01** | The guide is handed over at `EO-007` stage 6 and never duplicates it (`CP-01`) |
| **CA-02** | Every deadlock cause in §4.4 and §4.5 is stated as a **configuration** cause, with the client's own action to fix it — this is the guide's entire purpose |
| **CA-03** | **One person, one login.** Shared administrator logins are stated as unacceptable, with the reason: an approval recorded against a shared account is not an approval anyone can be held to |
| **CA-04** | The guide never asks an administrator to change something they cannot change — session policy, MFA, level 4, billing nodes mid-cycle. Those are named as routed, with the route |
| **CA-05** | Inheritance is described as **silent**, in those words. It is the property administrators discover by outage |
| **CA-06** | The authority-limit gap that `CAH-05` does not close is stated explicitly (§4.4), because a validation rule that passes teaches administrators that the configuration is sound |
| **CA-07** | Delegation is presented as **mandatory practice** even though no rule enforces it (`O-01`) |
| **CA-08** | The leaver sequence is stated as **deactivate, then replace in chains, in the same session** |
| **CA-09** | Scope-widening is described with its privacy consequence, and identified as the client's decision under `LG-003` and `LG-008` |
| **CA-10** | The §4.8 diagnosis table is issued to both the client and 1000FiX support, in the same words |
| **CA-11** | Bengali is required for §4.2, §4.3, §4.6 and §4.8 — the sections a site administrator uses (`CG-010` §3.3) |
| **CA-12** | The guide states no price, limit value or SLA figure. Authority limits are the client's own numbers, set by the client |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`EO-007`](EO-007_Corporate_Client_Onboarding_and_Welcome_Kit.md) | The build this guide takes over; §4.2's four expensive decisions are set there |
| [`MD-015`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md) §2, §2.1, §4 | Node model, four-level chain, inheritance, and `CAH-01`…`CAH-07` |
| `M29`; `PS-01`, `PS-12`; [`LG-020`](../10_Legal_Policy_and_Compliance/LG-020_Acceptable_Use_and_Internal_Access_Policy.md) | Identity, single sign-on, session and MFA policy the administrator cannot change |
| [`LG-003`](../10_Legal_Policy_and_Compliance/LG-003_Portal_Terms_of_Use_Corporate.md), [`LG-008`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md) | Portal terms and the privacy position behind §4.2's scope warning |
| [`SP-004`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) | The internal delegation model this guide mirrors — **and the source of the unlimited-terminal-approver idea `MD-015` lacks** |
| [`SP-005`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) | Internal escalation, where a client deadlock becomes a 1000FiX escalation |
| [`OP-015`](../17_Operations_Support_and_Runbooks/OP-015_Access_Request_and_Joiner_Mover_Leaver_Content.md) | The internal joiner-mover-leaver model §4.6 is the client-side analogue of. **Written** — the read-across in `O-07` has not been done |
| [`AP-008`](../15_Integration_and_Developer_Content/AP-008_Partner_Integration_Guide_Corporate.md) | Partner Integration Guide — Corporate. Where a client integrates their own ITSM or identity platform, federated sign-on changes §4.2's identity model |
| [`CM-014`](../16_Change_Management_and_Comms/CM-014_Corporate_Client_Transition_Pack.md) | Corporate Client Transition Pack — owns moving an **existing** client onto `P04`; this guide owns the administrator's configuration in either case. §2 boundary |
| [`UI-014`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-014_P04_Corporate_B2B_Portal_UI_Copy_Pack.md), [`UI-040`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-040_Registration_and_Onboarding_Flow_Copy.md), [`HC-006`](../09_Help_Centre_and_Self_Service/09A_Help_Sets_By_Portal/HC-006_Help_Set_P04_Corporate_B2B_Portal.md), `NT-010` | Screens, flow copy, help and approval notifications |
| [`DT-020`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-020_Consolidated_Corporate_Invoice.md) | Where the client's cost centre appears, and why renaming a department is not renaming a cost centre |
| [`EO-011`](EO-011_Rate_Card_and_Pricing_Communication_Pack.md), [`EO-014`](EO-014_Ecosystem_Offboarding_and_Exit_Content.md) | Price change communication; user deprovisioning and account closure at exit |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually, and after any `P04` release that changes the approval or user-administration screens |
| Trigger for out-of-cycle review | A change to `MD-015` §2.1 or the `CAH-*` rules; a delegation feature added to `P04`; a deadlock cause appearing that §4.8 does not list; a change to `M29` session or MFA policy; a support-volume spike attributable to approval deadlock |
| Owner | Account Management, with the Master Data Owner for §4.4 and Security for §4.2 |
| Change control | A new deadlock cause is added to §4.5 and §4.8 **in the same revision** — the pre-flight test and the diagnosis table must never diverge |
| Effectiveness measure | Approval-deadlock support contacts per client per quarter, and the share resolved by the client using §4.8 without escalation |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Nothing requires a delegate, and delegate absence is the commonest deadlock.** `MD-015` §2.1 defines chains and `CAH-05` requires termination; **no rule, field or validation requires a delegate for an approver.** §4.5 question 4 and `CA-07` make it mandatory practice, which is a content control over a data gap — the weakest kind. **A `delegate_user_id` on the approval-chain level, with a validation, would close it at the data layer** and is a `MD-015` change, not a Category 18 one | Master Data Owner with Account Management | **W4 — before the first client configures a chain** |
| **O-02** | **`CAH-05` guarantees termination and not reachability.** A chain can terminate in an approver whose authority limit is below the amounts routed to them, and the configuration saves cleanly. `SP-004` solves the equivalent internally by requiring an unlimited terminal approver; **`MD-015` has no analogue.** §4.4 and §4.5 question 3 are the only defence and both depend on the administrator reading this guide | Master Data Owner with CFO | **W4** |
| **O-03** | **`P04` has no stated absence or out-of-office mechanism.** `04-00` P04's account capabilities list multi-level approval chains and no delegation, holiday or auto-escalation feature. §4.6 therefore instructs an administrator to *"activate the delegate"* — **a capability that may not exist.** Either `P04` provides it, or §4.6 must instruct a manual chain edit for every absence, which will not be done | Account Management with the `M08` owner and Solution Architect | **W4 — before the first client goes live** |
| **O-04** | **No timebox or auto-escalation exists on a client-side approval.** `SP-005` timeboxes internal escalations and `CO-02` in `CG-002` states *"silence is not agreement"*. A client request can sit at level 2 indefinitely with no notification to anyone, and **the SLA consequence of that delay is unallocated** — it is the client's delay, on 1000FiX's clock, and `KPI-030` counts SLA attainment | Service Operations with Legal Counsel | **W4 — before the first SLA statement** |
| **O-05** | **Self-approval is not blocked.** §4.5 question 7 asks the administrator to check it; nothing prevents an approver from being the requester in their own chain. `SP-006` maintains a segregation-of-duties register for 1000FiX and **there is no equivalent constraint on the client side**, even though the approval commits 1000FiX to work and the client to payment | Master Data Owner with CFO | **W4** |
| **O-06** | **Bengali is required and unresourced**, and the split is different from `EO-007`'s. §4.2, §4.3, §4.6 and §4.8 are site-administrator content and Bengali; §4.4 is structural and may remain English. **`CG-010` §3.3's "Partly" verdict for corporate users has not been resolved into a section-level rule for either file** | Localisation Lead *(unappointed)* with Account Management | **W4 minus 6 weeks** |
| **O-07** | **`OP-015` exists and §4.6 has not been read across against it.** Category 17 `OP` holds **15 of 16** files on disk, authored 2026-08-18, and **the register records the category as unstarted** — see `AUDIT-015` EO-01. `OP-015` carries the internal joiner-mover-leaver model, its standard access profiles and its approval routing; §4.6 was written as the client-side analogue of an intent rather than of a published standard. **The two must be reconciled, and the direction matters**: where `OP-015` sets a same-day deactivation obligation internally, a client-side guide that is weaker is a stated double standard. `OP-001` support routing — also written — owns the escalation §4.8 hands off to | Account Management with Security and Support Lead | **W4** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the three `EO` additions applied to a configuration task and the adaptation declared
- [x] **The five structurally valid, operationally fatal configurations named in §1**
- [x] Ten-step configuration journey with the validation that stops the administrator at each step
- [x] Users, roles and scope stated, with the scope-widening privacy consequence
- [x] Site and department maintenance covered, including the archive constraint and the non-self-service billing-node move
- [x] Four-level chain explained, with the three invisible properties: per node, silent inheritance, termination without reachability
- [x] **The authority-limit gap `CAH-05` does not close, stated explicitly**
- [x] Eight-question pre-flight deadlock test, with the one question no rule enforces identified
- [x] Client-side joiner-mover-leaver, with the leaver sequence stated in order
- [x] First-90-days routine built around configuration decay rather than configuration error
- [x] **Stuck-request diagnosis table issued to both the client and 1000FiX support in identical words**
- [x] Twelve rules
- [x] All internal links resolve
- [x] Six open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` no delegate requirement at the data layer — outstanding; the commonest deadlock has only a content control**
- [ ] **`O-03` `P04` may have no absence mechanism — outstanding; §4.6 may instruct an unavailable action**
- [ ] **`O-04` no timebox or auto-escalation on client approvals — outstanding; SLA consequence unallocated**
- [ ] **`O-05` self-approval not blocked — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Named approver recorded — **pending Content Design Lead with Account Management**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
