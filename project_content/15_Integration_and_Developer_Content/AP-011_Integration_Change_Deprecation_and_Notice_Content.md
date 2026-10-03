---
id: AP-011
title: Integration Change, Deprecation and Notice Content
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
author: Platform Engineering with Content Design
reviewers: [CTO, Solution Architect, Content Design Lead, Security Lead, Legal Counsel, Commercial Director, Account Management Lead, Support Lead]
approver: Content Design Lead with CTO
content_class: D
purpose: >
  What counts as a breaking change to a 1000FiX API or event, and the content that must reach every
  affected consumer before it happens — deprecation notices, migration guides, changelog entries,
  machine-readable headers, dual-publish periods and the escalation when a consumer will not move.
  `IP-08` requires versioned, documented external contracts and `05-03` §3.4 promises six months'
  notice before a version is removed. A promise of notice with no notice content is a promise
  nobody can keep, and the failure is asymmetric: the consumer discovers the change when their
  integration stops working, which for a payment rail or a brand's claim feed is a business
  interruption 1000FiX caused.
traces_to: [M28, M28 FR-IPF-013, M28 FR-IPF-014, M28 FR-IPF-025, M28 §8.2, M28 AUT-IPF-08, M28 AUT-IPF-09, M28 BRU-IPF-05, M28 BRU-IPF-06, M28 Q-08, 05-03, 05-03 IP-08, 05-03 §3.4, 05-03 §4.3, 05-03 API-02, CG-006, AP-001, AP-002, AP-003, AP-004, AP-005, AP-006, AP-007, AP-008, AP-009, AP-010, AP-012, LG-003, LG-005, LG-006, LG-007, OP-006, NT-013, RF-006]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §3.4 "both sides support at least two API versions concurrently; six months' notice before removing a version"; §5.2 API-02; §4.3 additive-only within a schema_version, breaking changes require a new version and a dual-publish period; §1 IP-08
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_Integration_API_and_Event_Platform.md §5.2 FR-IPF-013 and FR-IPF-014; §8.2 the API version lifecycle DESIGNED → PUBLISHED → DEPRECATED → SUNSET → RETIRED with removal blocked while a consumer still calls; §9 BRU-IPF-05, BRU-IPF-06; §11 AUT-IPF-08, AUT-IPF-09; §18 Q-08 escalation path when a consumer refuses to migrate
    verified: 2026-08-18
    class: P1
  - source: RFC 9745 The Deprecation HTTP Response Header Field (2025) — a structured-field date indicating when deprecation takes effect; used with RFC 8594 Sunset, whose timestamp must not be earlier than the Deprecation date, and a Link header pointing to migration documentation. https://www.rfc-editor.org/info/rfc9745/ · https://www.ietf.org/rfc/rfc9745.pdf
    verified: 2026-08-18
    class: P2
  - source: project_content/00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md §5 — `AP` content is pinned to API version, not to a wave
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Integration Change, Deprecation and Notice Content

| Item | Value |
|---|---|
| Change classes | 4 (§4.1) |
| Breaking-change definitions | 14 for REST, 8 for events (§4.1) |
| Version lifecycle states | 5 (`M28` §8.2) |
| Notice period | **6 months** before removal (`05-03` §3.4, `API-02`) |
| Notice templates | 6 (§4.4) |
| Notice channels | 5 (§4.3) |
| Machine-readable headers | 3 — `Deprecation`, `Sunset`, `Link` (§4.5) |
| Emergency exception | 1 route, security only (§4.8) |
| Wave | W4 registered · **first consumed W3** — open item `O-01` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order; §4 subdivided by volume. The **endpoint reference table**
> required by `CG-009` §3 is §4.10 — the version and deprecation register endpoints. The **error
> catalogue table** required by `CG-009` §3 is §4.11 — the version-related errors, referencing
> `AP-006` codes (`CP-01`).

---

## 1. Purpose

`IP-08` requires every external contract to be versioned and documented. `API-02` requires path
versioning, at least two concurrent versions, and six months' deprecation notice. `05-03` §3.4
repeats it for the portal contract. `FR-IPF-014` emits machine-readable headers, notifies
registered consumers, enforces the notice period and **blocks removal while a consumer is still
calling**.

**The mechanism is fully specified. The content is not specified at all.** `FR-IPF-014` says
"notify registered consumers"; nothing says what the notification contains, when the notifications
are sent, through which channel, in whose voice, or what a migration guide must include.

The asymmetry is what makes this matter. When a version is removed without adequate notice,
**1000FiX experiences a clean deprecation and the partner experiences an outage.** For a brand's
claim feed that means claims stop flowing against a 72-hour submission target (`G4-01`); for a
courier it means consignment status stops updating mid-delivery; for a payment rail it means
customers cannot pay. In each case the interruption is ours and the consequence lands on them.

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| A breaking-change definition | Teams ship a "small change" that breaks six consumers. §4.1's fourteen REST cases are all things engineers have genuinely believed were non-breaking |
| Notice content | `FR-IPF-014` "notifies" with an empty template. A notice that does not say what to change is a warning, not a migration |
| A notice schedule | One email six months out, and nothing after. Consumers plan around the last reminder, not the first |
| Migration guide structure | Each migration is documented differently and the partner re-learns the format each time |
| Dual-publish content | `05-03` §4.3 requires dual publishing for breaking event changes; nothing tells a consumer that both versions are live, which is authoritative, or when the old one stops |
| The sunset-blocked path | `M28` Q-08 is open: what happens when a consumer refuses to migrate and blocks a sunset. Without a path, the version lives forever or someone removes it unilaterally |
| An emergency route | A security-driven breaking change has no path except breaking the six-month promise, which then breaks it for everything |

---

## 2. Scope

**In scope.** Change classification; breaking-change definitions for REST and events; the version
lifecycle and its content obligations; notice channels and schedule; six notice templates;
machine-readable signalling; event schema change and dual publishing; the sunset-blocked
escalation; the emergency exception; the changelog standard; the register reference; and
version-related errors.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| The versioning **mechanism** — routing, header emission, registry state | `M28` `FR-IPF-013`, `FR-IPF-014` | This file is the content the mechanism carries |
| Release notes for **internal users** across the estate | `OP-006` | Different audience, different cadence. `OP-006` covers nine waves of change for staff; this covers external contracts |
| Content lifecycle and versioning for the content set itself | `CG-006` | `CG-006` §5 pins `AP` content to API version — which is a rule this file operates under, not one it sets |
| Schema compatibility enforcement | `M28` `FR-IPF-025`, CI | The gate that stops a breaking change reaching production without a new version |
| Contractual notice obligations to partners | `LG-003`, `LG-005`, `LG-006`, `LG-007` | **Referenced, not restated — and see `O-02`, because none of them may carry an API notice clause** |
| Notification delivery infrastructure | `M27` | §4.3 names channels; `M27` delivers |
| Partner-facing announcement of a **new** capability | Commercial and `EO` kits | This file covers change and removal, not launch |
| Sandbox refresh notice | `AP-010` `RS-4` | Uses this file's channel and cadence |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Module developers across all 67 modules** | §4.1 — deciding whether a change they are about to make is breaking. Primary audience by volume |
| **Platform Engineering** | The notice schedule and the register |
| **Content Design** | The six templates and the changelog voice |
| **Account Managers** | The escalation at §4.7, which becomes a commercial conversation |
| **External consumers** | The output — notices, migration guides, changelog. They read the notice, not this file |
| **Support** | Understanding what a consumer has already been told before they call |
| **Legal** | §4.7's escalation and the `O-02` contractual gap |

---

## 4. Content

### 4.1 What counts as a change

Four classes. The class determines everything that follows.

| Class | Definition | Version impact | Notice |
|---|---|---|---|
| **C1 — Additive** | New optional field, new endpoint, new optional parameter, new enum value **where the schema declares the enum open** | None | Changelog entry only |
| **C2 — Behavioural** | Same contract, different behaviour — a validation tightened, a default changed, a limit reduced, an error newly emitted | None to the schema; **material to the consumer** | **Changelog + direct notice.** The most under-notified class |
| **C3 — Breaking** | Anything in the lists below | New version required | **Full deprecation cycle** — §4.3 |
| **C4 — Emergency** | A breaking change required to close a security or legal exposure | New version, expedited | §4.8 |

**Breaking for REST — fourteen cases.** Every one of these has been argued as non-breaking by
somebody, somewhere.

| # | Change | Why it breaks |
|---:|---|---|
| B-01 | Removing an endpoint | — |
| B-02 | Removing a field from a response | A consumer reading it gets nothing |
| B-03 | Renaming a field | Equivalent to removing one |
| B-04 | Changing a field's type — string to integer, scalar to object | Parse failure |
| B-05 | Making an optional request field required | Existing callers fail validation |
| B-06 | Adding a **new required** request field | Same |
| B-07 | Tightening validation — a shorter length, a narrower pattern, a smaller range | Previously valid requests now fail |
| B-08 | Removing an enum value, **or adding one to a closed enum** | The consumer's switch statement has no branch |
| B-09 | Changing the HTTP status for an existing outcome | Consumers branch on status even when told not to |
| B-10 | Changing an `AP-006` **code** for an existing condition | `EP-01` — the code is the contract |
| B-11 | Changing an error's **retry classification** | `AP-006` `CG-06`; the consumer's handler is built on it |
| B-12 | Changing the **default** for an omitted parameter | Silent behaviour change with no signal at all — the worst of the fourteen |
| B-13 | Changing pagination semantics — cursor format, page-size maximum, end-of-collection signal | Page loops break or silently truncate |
| B-14 | **Reducing a rate limit** | An integration sized to the published limit starts failing (`AP-005` §6) |

**Breaking for events — eight cases.** `05-03` §4.3: additive changes only within a
`schema_version`; a breaking change requires a new version **and a dual-publish period**.

| # | Change | Why it breaks |
|---:|---|---|
| E-01 | Removing a payload field | — |
| E-02 | Renaming a payload field | — |
| E-03 | Changing a payload field's type | — |
| E-04 | Changing the **meaning** of an event without changing its shape | `AP-003` `NM-07`. The schema registry cannot detect it and CI will pass |
| E-05 | Changing the **emission condition** — when the event fires | Consumers act on a fact that is now a different fact |
| E-06 | Renaming the event type | `NM-04` |
| E-07 | Splitting one event into two, or merging two into one | Consumers receive nothing, or receive twice |
| E-08 | Changing the **aggregate** an event is partitioned on | Destroys the per-aggregate ordering guarantee consumers depend on (`T-03`) |

> **`E-04` and `E-05` are the two the machinery cannot catch.** `FR-IPF-025` enforces schema
> compatibility; a description change and an emission-condition change both pass. They are caught
> only by `AP-003`'s change control — the producing module's owner plus Enterprise Architecture
> plus a `RF-006` entry — and that is why `AP-003` `NM-07` exists.

### 4.2 The version lifecycle and what content each state owes

`M28` §8.2 gives the states. This adds the content obligation at each.

| State | Meaning | Content owed | Who receives it |
|---|---|---|---|
| **DESIGNED** | Specification registered and linted | None external | — |
| **PUBLISHED** | Live, documented, consumers registered | Changelog entry; reference pages generated (`AP-001` PT-04, PT-05) | Public |
| **DEPRECATED** | Successor released; the six-month clock has started | **Deprecation notice** (T1) · **migration guide** (T3) · changelog entry · `Deprecation`, `Sunset` and `Link` headers on every response · register row | Every registered consumer of that version, directly |
| **SUNSET** | Notice period elapsed; removal authorised **only if no traffic** | **Final notice** (T4) at 30 days, 7 days and 24 hours | Every consumer still calling |
| **RETIRED** | Routes removed; specification archived | **Retirement notice** (T5); changelog entry; reference pages moved to the archive, **not deleted** | Public |
| *(blocked)* | Sunset reached **with live traffic** | **Blocked-sunset escalation** (T6) — §4.7 | The consumer's named owner, their account manager, and internally |

**Two rules that follow from `BRU-IPF-05`.**

| # | Rule |
|---|---|
| **VL-1** | **A version is never removed while a registered consumer is calling it.** `AUT-IPF-09` blocks removal and escalates. This is a hard rule, not a courtesy |
| **VL-2** | **Deprecated documentation is never hidden before sunset** (`AP-001` `NAV-07`). Hiding the docs while the endpoint lives strands the consumer we are trying to move |

### 4.3 Notice channels and schedule

**Five channels**, each with a different job.

| # | Channel | Reaches | Job |
|---|---|---|---|
| **CH-1** | **Direct notification to every registered consumer's `owner_user_id`** | The named human on the consumer registration | The notice of record. Everything else is reinforcement |
| **CH-2** | **Machine-readable headers** on every response of the deprecated version | The integration itself | The only channel that reaches a system nobody is watching (§4.5) |
| **CH-3** | **Developer portal changelog and deprecation register** | Anyone who looks | The durable, linkable record (`AP-001` §7) |
| **CH-4** | **In-portal banner** for consumers with a portal presence | The partner's operational staff | Reaches people who are not the integration's owner |
| **CH-5** | **Account manager briefing** for contracted partners — brands, corporate clients, payment rails | The commercial relationship | The channel that actually moves a partner who has not responded to CH-1 |

**The schedule.** `05-03` §3.4 gives six months. Six months with one notice at the start produces
migration in month six or not at all.

| Point | Channels | Content |
|---|---|---|
| **T−6 months** — deprecation announced | CH-1, CH-2, CH-3, CH-4 | Deprecation notice (T1) + migration guide (T3) |
| **T−3 months** | CH-1, CH-3 | Reminder (T2), **stating whether that consumer is still calling the old version** |
| **T−1 month** | CH-1, CH-4, **CH-5 for contracted partners still calling** | Reminder (T2) with the consumer's own current traffic figure |
| **T−30 days** | CH-1, CH-2, CH-4 | Final notice (T4) |
| **T−7 days** | CH-1, CH-4, CH-5 | Final notice (T4) |
| **T−24 hours** | CH-1, CH-4 | Final notice (T4) |
| **T = sunset, no traffic** | CH-3 | Retirement notice (T5) |
| **T = sunset, traffic present** | CH-1, CH-5, internal | **Blocked-sunset escalation (T6)** — §4.7 |

> **The T−3 and T−1 reminders are consumer-specific and that is the design.** A generic reminder is
> filed; a reminder that says *"your integration made 4,182 calls to `v1` last week"* is acted on.
> `FR-IPF-017` provides per-consumer usage, so the figure is available.

### 4.4 The six notice templates

Voice per `CG-003`: plain, specific, no apology theatre, no "we are excited to announce". A
deprecation notice is an operational instruction.

---

**T1 — Deprecation notice** · CH-1, CH-3

| Element | Content |
|---|---|
| Subject | `{API name} {version} is deprecated — action required by {sunset date}` |
| Opening | What is deprecated, and the one-line reason |
| What changes | The specific difference, listed against §4.1's breaking cases |
| **What you must do** | The action, in order, with the migration guide linked |
| **By when** | The sunset date, in full, with the notice period stated |
| What happens if you do not | *Your integration will stop working on {date}. We will not remove the version while you are still calling it, but we will escalate to your account manager and agree a dated plan* — **the honest statement of `VL-1`** |
| Your current usage | Calls to this version in the last 7 days, for this consumer |
| Who to ask | A named route, not a generic mailbox |

**Required and frequently omitted:** the *reason*. A consumer who understands why a version is
going will plan for it; one who does not will assume it is arbitrary and defer.

---

**T2 — Reminder** · CH-1, CH-3, CH-5 at T−1 month

Shorter. Must carry: days remaining · **this consumer's current call volume on the old version** ·
the migration guide link · one sentence on what happens at sunset. If the consumer has already
migrated — zero calls — **send nothing.** Reminders to consumers who have complied train them to
ignore reminders.

---

**T3 — Migration guide** · CH-3, linked from every notice

| Section | Content |
|---|---|
| 1. What changed | The change list, by §4.1 case |
| 2. Who is affected | Which endpoints, which events, which consumer classes. **A consumer must be able to tell in 30 seconds whether this affects them** |
| 3. Before and after | The request and response, or the event payload, **side by side** |
| 4. Step-by-step migration | Numbered, with the smallest safe increment first |
| 5. How to test | The sandbox path (`AP-010`), including which forced-error triggers apply |
| 6. Rollback | Both versions are live during the notice period. **Say so** — it is the fact that makes migrating early safe |
| 7. Timeline | Deprecation date, sunset date, notice points |
| 8. Getting help | Named route |

**Section 3 is not optional.** A migration guide without a before-and-after is a change log with
headings.

---

**T4 — Final notice** · CH-1, CH-2, CH-4

Blunt. Days remaining · this consumer's calls in the last 24 hours · the exact date and time of
removal · the one action. No new information — a final notice that introduces new detail is a
notice that arrived too late.

---

**T5 — Retirement notice** · CH-3

Recorded rather than sent. What was retired, when, what replaced it, where the archived
specification lives. This is the record a future integrator finds when they wonder why `v1`
returns `404`.

---

**T6 — Blocked-sunset escalation** · CH-1, CH-5, internal

| Element | Content |
|---|---|
| To | The consumer's `owner_user_id`, their account manager, the API owner, the CTO |
| States | The sunset date has passed; the version remains live under `VL-1`; this consumer's traffic |
| Asks for | **A dated migration plan with a named owner on the consumer's side** |
| Offers | Technical assistance, a sandbox walkthrough, and a review of any genuine blocker |
| Does not | Threaten removal. `VL-1` means we will not, and a threat we will not carry out damages the next notice |

§4.7 covers what happens next.

---

### 4.5 Machine-readable signalling

The only channel that reaches an unattended integration.

| Header | Standard | Value | Emitted from |
|---|---|---|---|
| `Deprecation` | **RFC 9745** | A structured-field date — the moment deprecation took effect | Deprecation announcement onward |
| `Sunset` | **RFC 8594** | An HTTP-date — when the endpoint stops working. **Must not be earlier than `Deprecation`** | Deprecation announcement onward |
| `Link` | RFC 8288 | `rel="deprecation"` → the migration guide; `rel="successor-version"` → the replacement | Deprecation announcement onward |

| # | Rule |
|---|---|
| **MH-1** | All three are emitted on **every response** from the deprecated version, not on a sample |
| **MH-2** | `Sunset` ≥ `Deprecation`, always. RFC 9745 requires it |
| **MH-3** | The `Link` target is the **migration guide**, not the changelog. A consumer following the header needs the instruction, not the announcement |
| **MH-4** | Headers are emitted **in addition to** CH-1, never instead. A header nobody logs is a notice nobody received |
| **MH-5** | After retirement, the route returns **`410 Gone`** with a `Link` to the successor — not `404`. `410` tells a machine the resource existed and is deliberately gone |
| **MH-6** | Consumers are told, in `AP-002`'s concept pages, to **log and alert on `Deprecation` and `Sunset`**. A partner who does this receives every notice automatically |

### 4.6 Event schema change and dual publishing

`05-03` §4.3 and `BRU-IPF-06`: additive within a `schema_version`; breaking changes need a new
version **and a dual-publish period**.

```
   v1 published ──────────────────────────────────────────────────────┐
                                                                       │ dual-publish window
   v2 registered ──► v2 published ─────────────────────────────────────┤ both live
                                                                       │ fix_event_schema.dual_publish_until
   consumers migrate subscription from v1 to v2 ────────────────────►  │
                                                                       │
   v1 has no subscribers ──► v1 stops publishing ──────────────────────┘
```

| # | Rule | Content obligation |
|---|---|---|
| **DP-1** | Both versions are published to the bus for the whole window | The notice states **both are authoritative and identical in meaning** — otherwise a consumer receiving both assumes a duplicate |
| **DP-2** | `dual_publish_until` is stored on the schema registration and is **published**, not internal | The register row (§4.10) shows it |
| **DP-3** | A consumer subscribes to **one** version, not both. Receiving both is a subscription error, not a platform behaviour | Stated in T3 §2 |
| **DP-4** | The window is **not** the same as the six-month API notice. **Its length is unspecified anywhere in the repository** — `O-03` | — |
| **DP-5** | v1 stops publishing when no subscriber remains, subject to `VL-1`'s equivalent for events | T6 applies |
| **DP-6** | An `E-04` or `E-05` change — meaning or emission condition, with an unchanged schema — **still requires a notice**, even though it needs no new version technically | `AP-003` `NM-07`. This is the change class most likely to ship silently |

### 4.7 When a consumer will not migrate — `M28` Q-08

`M28` Q-08 is open and addressed to the CTO at W3: *"What is the escalation path when a consumer
refuses to migrate off a deprecated API version and blocks a sunset?"* This file cannot close it,
but it can set out the shape, because `VL-1` guarantees the situation will occur.

**The constraint that makes this hard:** `BRU-IPF-05` is a **hard rule** — a version cannot be
removed while a registered consumer is calling it. So the platform has no unilateral remedy, and
the resolution is necessarily commercial.

| Stage | Trigger | Action | Owner |
|---:|---|---|---|
| 1 | Sunset date reached with traffic | T6 issued; the version stays live | Platform |
| 2 | +2 weeks, no dated plan | Account manager raises it as a **service issue on the relationship**, not a technical request | Account Management |
| 3 | +6 weeks, no dated plan | **Commercial review.** Is the consumer contractually obliged to maintain a supported version? `O-02` says probably not, today | Commercial + Legal |
| 4 | +3 months | Options, in order of preference: extended support **with a stated end date**; a compatibility shim with a stated cost; a rate-limit reduction on the deprecated version making migration the easier path; contractual escalation | CTO + Commercial |
| 5 | Last resort | **Removal by decision**, recorded in `RF-006`, with the consumer given a final dated notice | CTO, with Steering Committee visibility |

| # | Position |
|---|---|
| **ES-1** | Stage 5 exists so that stages 1–4 are not open-ended. A rule with no terminal state is a rule that is eventually broken silently |
| **ES-2** | A rate-limit reduction (stage 4) is itself a **B-14 breaking change** and needs its own notice. Using one breaking change to force another is legitimate only with the full cycle |
| **ES-3** | **Two deprecated versions blocked simultaneously is an architecture problem, not a partner problem.** `API-02` requires supporting two concurrent versions; three live versions means the platform is carrying a version nobody agreed to carry |

### 4.8 The emergency exception

A breaking change required to close a security or legal exposure cannot wait six months. Exactly
one route exists, deliberately narrow.

| # | Rule |
|---|---|
| **EM-1** | Invoked only for: a security vulnerability in the contract itself, a regulatory or statutory requirement with a shorter deadline, or a data-disclosure error where the contract exposes something it must not |
| **EM-2** | **Requires CTO and Security Lead approval, and a `RF-006` entry stating the exposure.** Commercial convenience is never a ground |
| **EM-3** | The notice period is the **shortest that closes the exposure**, and is stated with its reason |
| **EM-4** | Every affected consumer is contacted through **CH-1 and CH-5 simultaneously** — a named human, not only a notification |
| **EM-5** | Where the exposure permits, the change is made **additively first** — a new safe field alongside the old, old one removed later on the normal cycle |
| **EM-6** | Where it does not, the change ships and **the notice explains the exposure to the degree that disclosure permits** |
| **EM-7** | An emergency change is reviewed afterwards: could the original contract have avoided it? The answer goes to `AP-002`'s review, because most such exposures are design defects that a documentation standard could have caught |

### 4.9 Changelog standard

The changelog is the durable record and `AP-001` §7 is its home.

| # | Rule |
|---|---|
| **CL-1** | One entry per change that affects a public contract. C1 additive changes get an entry too — a consumer wondering when a field appeared needs the answer |
| **CL-2** | Entries are **dated, versioned and classified** by §4.1 class |
| **CL-3** | Reverse chronological, filterable by API family and by version |
| **CL-4** | Each entry states: what changed · which versions · the class · the action required, or "none" |
| **CL-5** | A C3 entry links to its migration guide; a C4 entry links to its `RF-006` record |
| **CL-6** | The changelog is **public** (`AP-001` T-Pub). A prospective partner assessing integration risk is entitled to see the change history |
| **CL-7** | Entries are **never edited after publication**. A correction is a new entry referencing the old one — the same discipline `AP-003` `EV-02` applies to events |
| **CL-8** | Written in `CG-003` voice. Not "we've improved…" — "`GET /api/v1/service-orders` now returns `promised_at`. Optional; no action required." |

### 4.10 Register and endpoint reference

The endpoint reference table required by `CG-009` §3.

| Endpoint / surface | Method | Purpose | Owner | Tier |
|---|:--:|---|:--:|:--:|
| `/api/v1/platform/apis` | GET | The API registry with versions, status, deprecation and sunset dates, and consumer counts | `M28` | T-Auth |
| Deprecation register page | — | Generated from `fix_api_registry` — every deprecated version, its sunset date and its migration guide (`AP-001` PT-13) | `M28` | **T-Pub** |
| Changelog | — | Authored entries (`AP-001` PT-12) | Platform + module owners | **T-Pub** |
| `/api/v1/platform/events/schemas` | GET | Event schema versions, compatibility and `dual_publish_until` | `M28` | T-Auth |
| `/api/v1/platform/consumers` | GET | A consumer's own registrations, including which versions they call | `M28` | T-Auth, own only |

**The deprecation register is public and the consumer list is not.** A partner may see *that*
`v1` sunsets on a date; they may not see *who else* calls it. That is `EA-02` applied to
documentation.

### 4.11 Version-related errors

Codes are `AP-006`'s (`CP-01`).

| Situation | Code | HTTP | Remedy |
|---|---|:--:|---|
| Calling a version that never existed | `request.version_unsupported` | `400` | Use a supported version; see the register |
| Calling a **retired** version | `request.version_unsupported` with a `Link` to the successor | **`410`** | Migrate. `MH-5` — `410`, not `404` |
| Calling a **deprecated** version | *(no error)* — succeeds, with `Deprecation`, `Sunset` and `Link` headers | `2xx` | Migrate before the sunset date |
| Sending a field removed in this version | `request.unknown_field` | `400` | The field belongs to an earlier version |
| Sending a field required only in a later version | `validation.required_missing` | `400` | Check the version you are calling |
| Subscribing to a retired event `schema_version` | `422 state.transition_invalid` *(nearest existing code — see `O-06`)* | `422` | Subscribe to the current version |
| Receiving both versions during dual publish | *(not an error)* | — | A subscription error on the consumer's side (`DP-3`) |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M28` `FR-IPF-013`, `FR-IPF-014` | Version support, headers, notification, removal blocking |
| `M28` `FR-IPF-025` | Schema compatibility and the dual-publish record |
| `M28` `FR-IPF-017` | Per-consumer usage — the figure that makes the T−3 and T−1 reminders effective |
| `M28` §8.2 | The lifecycle states §4.2 adds content to |
| `05-03` §3.4, `API-02` | The six-month promise |
| `05-03` §4.3 | Additive-only and the dual-publish requirement |
| `AP-001` §7 | Where the changelog and register are published |
| `AP-002` | The reference pages a version change regenerates; `AR-26` requires the deprecation annotation |
| `AP-003` `NM-04`…`NM-08` | Event naming and versioning rules; `NM-07` is the `E-04`/`E-05` control |
| `AP-005` | Rate-limit reductions are `B-14` breaking changes |
| `AP-006` `CG-01`, `CG-04`, `CG-06` | Code permanence, meaning changes and retry reclassification are all breaking |
| `AP-010` `RS-4` | Sandbox refresh notice uses this cadence |
| `LG-003`, `LG-005`, `LG-006`, `LG-007` | Partner terms — **and `O-02`** |
| `M27` | Notification delivery for CH-1 |
| `CG-006` §5 | `AP` content pins to API version |
| `RF-006` | Emergency changes and stage-5 removals are recorded decisions |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave, and after every deprecation cycle completes |
| Trigger for out-of-cycle review | Resolution of `M28` Q-08 · the first blocked sunset · the first emergency change · a change to `API-02`'s notice period · a partner reporting they received no notice |
| Owner | Platform Engineering Lead, with Content Design Lead accountable for the six templates |
| Change control | **Shortening the notice period requires CTO and Commercial Director approval and a review of every partner agreement** — it is a change to a published promise. Template wording changes need the Content Design Lead. Both need a `RF-006` entry |
| Version pinning | Pinned to **API version** (`CG-006` §5) |
| Post-cycle review | After each completed deprecation: how many consumers migrated by T−3, T−1 and sunset; how many needed CH-5; whether any blocked. **The migration curve is the measure of whether the notice content works** |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Registered W4; first consumed W3.** `05-03` §8 puts ten integrations into W3, `AP-002` and `AP-006` are W3, and `API-02`'s two-concurrent-version obligation applies from the second version of anything — which arrives well before W4. Eleventh consecutive category with this defect | Programme Content Lead with Platform Engineering Lead | **W3** |
| **O-02** | **No partner agreement is known to carry an API notice clause.** `05-03` §3.4 promises six months' notice; `LG-003`, `LG-005`, `LG-006` and `LG-007` are the agreements that would bind it, and none is cited anywhere as containing it. **A promise made in an architecture document and not in a contract is not enforceable in either direction** — 1000FiX cannot require a partner to migrate, and a partner cannot hold us to the notice. This is §4.7 stage 3's whole difficulty | Legal Counsel with Commercial Director | **W3 — before the first external contract is signed** |
| **O-03** | **The dual-publish window length is unspecified.** `05-03` §4.3 requires the period; `fix_event_schema.dual_publish_until` stores it; nothing states how long it should be, or whether it is per change or standard | Solution Architect | **W1 — the first event version change could occur in W2** |
| **O-04** | **`M28` Q-08 is unresolved.** §4.7 proposes a five-stage escalation ending in a recorded removal decision. It is a proposal; `BRU-IPF-05` gives the platform no unilateral remedy, so without an agreed path the terminal state is a version carried indefinitely | CTO with Commercial Director | **W3** |
| **O-05** | **No notice-delivery owner is named.** CH-1 requires notifications to every registered consumer's `owner_user_id` at six scheduled points. `M27` delivers; nobody is named as the function that composes, schedules and confirms. `AP-001` `O-08` records the same gap for the changelog | Platform Engineering Lead with Support Lead | W3 |
| **O-06** | **No error code exists for a retired event schema version.** §4.11 uses `state.transition_invalid` as the nearest fit, which breaches `AP-006` `CG-03`. Events are not REST and the subscription surface needs its own condition | Platform Engineering Lead | W4 |
| **O-07** | **`API-02` requires two concurrent versions and `05-03` §3.4 requires six months' notice; neither states the maximum number of live versions.** `ES-3` argues three is an architecture failure. Without a stated ceiling, a blocked sunset plus a normal release cadence produces four | Solution Architect | W4 |
| **O-08** | **`OP-006` release notes and this file's changelog have no declared boundary.** `OP-006` covers release-note structure and per-wave note sets for internal audiences; `CL-1`…`CL-8` cover the external contract changelog. A change to a public API is both, and today both files could claim it | Programme Content Lead with Support Lead | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] Four change classes, with the behavioural class identified as the most under-notified
- [x] **Fourteen REST and eight event breaking cases enumerated, including the two the schema registry cannot detect**
- [x] Version lifecycle mapped to the content each state owes and who receives it
- [x] Five channels with the job each does, including the one that reaches an unattended integration
- [x] **Eight-point notice schedule, with consumer-specific usage figures in the reminders**
- [x] Six notice templates authored, each with its required elements and the element most often omitted
- [x] Machine-readable signalling specified against RFC 9745 and RFC 8594, including `410` not `404` after retirement
- [x] Dual-publish contract with the six rules a consumer needs
- [x] **`M28` Q-08 given a five-stage shape ending in a terminal state, with the reason a terminal state is necessary**
- [x] Emergency exception defined narrowly, with the additive-first preference and the post-hoc review
- [x] Eight changelog rules including the never-edit discipline
- [x] Version-related errors referencing `AP-006`, with the one missing code recorded as a gap
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` registered after first consumption — outstanding**
- [ ] **`O-02` the six-month promise is in no contract — outstanding; it is unenforceable in both directions**
- [ ] **`O-03` dual-publish window length unspecified — outstanding**
- [ ] **`O-04` `M28` Q-08 unresolved — outstanding; no terminal state for a blocked sunset**
- [ ] Named approvers recorded — **pending Content Design Lead and CTO**
- [ ] Bengali counterpart — n/a; developer audience, English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
