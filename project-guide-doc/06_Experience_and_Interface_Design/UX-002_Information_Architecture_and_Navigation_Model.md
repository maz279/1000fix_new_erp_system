---
id: UX-002
title: Information Architecture & Navigation Model
category: 06 — Experience & Interface Design
code: UX
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of Product Design
approver: Design Authority (constituted under GV-002)
standards_basis: >
  ISO 9241-210:2019 (human-centred design) · WCAG 2.2 Level AA SC 2.4.5, 2.4.8, 3.2.3, 3.2.6 ·
  RFC 3986 (URI syntax) · RFC 9309 · IETF BCP 47 (language tags) · ISO 9241-112:2017
traces_to: >
  PGD-000 UX-002 · NFR-077 (≤ 4 clicks) · NFR-035 (search ≤ 600 ms incl. Bengali) ·
  URD §19.2 · 04-00 §P03 design requirements · UI-002 · 05-04 (role matrix) ·
  M29 (identity), M30 (platform administration)
depends_on: UX-001 (C-49…C-60 navigation components) · RQ-008 (stories that define entry points) · AR-001 §6 (surface set)
verified_on: 2026-08-18
priority: P1
needed_by: W1
enumeration_timestamp: 2026-08-18 14:45 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# UX-002 — Information Architecture & Navigation Model

### Category 06 · Code `UX` · ISO 9241-210:2019 · WCAG 2.2 AA

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 06 as `UX-002`.
> 2. **`PG-03` Count, do not consult.** Counts here were taken from the filesystem at
>    **2026-08-18 14:45 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-18`.

---

## 1. Purpose

`UI-002` registers **what the navigation is called**. This document specifies **what the navigation
is** — the structure those labels sit in, the addresses those structures resolve to, and the rules
that keep thirteen surfaces navigable by people who move between them.

It exists because `NFR-077` promises *"any record reachable in ≤ 4 clicks from any starting point"*
and `URD` §19.2 promises a maximum of seven top-level items, one-click workspace access, breadcrumbs
on every drill-down, recent items, saved views and correct browser-back behaviour — **and none of
these is achievable by a developer who has been given a label register and no structure.**

It unblocks the route table every front-end needs before its first screen (`BE-004`), the deep-link
targets every notification must carry (`NT-001` and `M27`), the permission-aware menu that `M29`
must feed, and the screen addressing scheme `UX-003` assigns identifiers within.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The information architecture of all thirteen surfaces — the primary structure of each |
| 2 | The navigation model: global chrome, primary navigation, workspace switching, drill-down, return |
| 3 | The **click-budget model** that makes `NFR-077` measurable rather than aspirational |
| 4 | The URL and route scheme, including deep links, public links and app links |
| 5 | The search model — global, scoped, bilingual, and its relationship to navigation |
| 6 | Permission-aware navigation and the non-disclosure rule |
| 7 | Cross-surface navigation — moving between portals without losing context |
| 8 | Wayfinding: breadcrumbs, recent items, saved views, back behaviour, help placement |
| 9 | Navigation change control — a label change is a coordinated edit across four content categories |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Navigation **labels** | `UI-002`, `BN-009`…`BN-013` | Content. This document cites them; it never invents one |
| The navigation **components** | `UX-001` `C-49`…`C-60` | A component is not a structure |
| Which screens exist | `UX-003` | An IA says where a screen sits; the inventory says which screens there are |
| Transition and motion between views | `UX-004` | Behaviour, not structure |
| Role and permission definitions | `05-04`, `SC-004` | This document consumes the role matrix; it does not define it |
| Help-content structure | `HC-001` | The help centre has its own IA; §9.6 states the join |
| Developer-portal IA | `AP-001` | A separate audience and a separate estate |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Front-end and mobile engineers | The route table, the deep-link scheme, the back-behaviour contract |
| Designers | The structure a screen sits in before it is designed |
| `M27` / notification engineering | The deep-link target for every notification type |
| Identity engineering (`M29`) | The menu-visibility contract |
| Training and help authors | The navigation paths every article must describe |
| QA | The click-budget assertions and the non-disclosure tests |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure |
|---|---|---|---|
| **ISO 9241-210:2019** | §5.4 (understanding context of use), §5.5 (user requirements) | The IA is derived per audience from the counted role and persona sets, not from the module structure. §4.1 states the derivation | None |
| **WCAG 2.2 AA** | SC 2.4.5 Multiple Ways · SC 2.4.8 Location · SC 3.2.3 Consistent Navigation · **SC 3.2.6 Consistent Help** | §9.1 (breadcrumbs), §9.6 (help in one position on all thirteen surfaces), §8 (search as the second way) | SC 2.4.8 is AAA and is adopted anyway — breadcrumbs are already an `URD` §19.2 commitment |
| **RFC 3986** | §3 | The route grammar in §7.1 | None |
| **IETF BCP 47** | — | Locale segment `bn-BD` / `en-BD` in routes; `Content-Language` on every response | None |
| ISO 9241-112:2017 | §5.2 organising information | Grouping, ordering and labelling rules in §4.3 | None |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `UI-002` §3 | The label register: global chrome (7 items), the `P03` workspace switcher (14 items), `P01` primary navigation |
| `04-00` §P03 | Fourteen workspaces, one-click access, ≤ 4 clicks to any record, 1366×768 hardware |
| `04-00` §P01…§P12 | Capability areas per surface — **counted: 14, 13, 14 workspaces, 11, 9, 6, 11, 9, 7, 9, 7, 6** |
| `URD` §19.2 | Ten navigation and findability commitments |
| `URD` §3, §4 | **36 personas · 46 roles** — the audiences an IA must serve |
| `05-04` | Role, permission and access matrix — the input to permission-aware navigation |
| `RQ-008` | User stories: the tasks each entry point must open onto |
| `NT-001` | Notification event/channel matrix — every notification needs a deep-link target |

### 2.3 Findings this document addresses

| Finding | Source | How this document addresses it |
|---|---|---|
| Register row `UX-002` ◐ | `PGD-000` | `UI-002` is a label register, not a structure. This document supplies the structure |
| **New — `UXA-04`** | This category | `UI-002` §1 declares i18n namespace `common.nav.*` but its own §3 uses `ws.nav.switcher.*` and `p01.nav.primary.*`. Three namespaces, one declared. §10.2 rules the namespace allocation |
| **New — `UXA-05`** | This category | **Eleven demand-side files require deep linking; none states an address scheme.** `NT-015`/`016`/`017` each commit that *"every push opens the exact record"*; `NT-018` `IB-05`, `NT-022`, `OP-004`, `TPL_Notification_Template`, `P03` §12, `P06` §T-08 and `M10` `FR-LOY-033` all depend on one. **The requirement is stated eleven times and specified zero times.** §7 supplies the scheme |
| `RQA-17` residual | `PGD-AUDIT-004` | Entry points per objective are named in §4.2, so an objective with no surface becomes visible |

---

# 3. The Governing Constraint

## 3.1 Thirteen surfaces, forty-six roles, one mental model

Counted at 2026-08-18 14:45 (+06):

| Count | What |
|---:|---|
| **12** | Portals and applications, `P01`…`P12` |
| **13** | **Distinct navigable surfaces** — `P01` has two (web and app) with different IA constraints |
| **14** | `P03` role-scoped workspaces |
| **46** | Roles (`URD` §4) |
| **36** | Personas (`URD` §3) |
| **67** | Modules whose objects must be reachable |
| **371** | Module functional areas — the grouping level navigation resolves to |

> **The design problem is not "how do we navigate one system". It is "how does a branch manager who
> uses `P03` Branch Console daily, opens `P06` weekly and answers a `P10` escalation monthly not
> have to relearn navigation three times."** A person holds one mental model, not thirteen.

## 3.2 The four navigation laws

| # | Law | Consequence if broken |
|---|---|---|
| `NVR-01` | **The same thing is in the same place on every surface.** Global chrome, search, help, account, notifications and language occupy fixed positions across all thirteen | Retraining cost per surface; WCAG SC 3.2.3 and SC 3.2.6 failures |
| `NVR-02` | **Navigation is a noun; action is a verb.** Menu items name objects; buttons name actions. One exception is registered: `P01` "Book a service", which is the primary action of the surface (`UI-002` §3) | Users cannot predict whether a click navigates or commits |
| `NVR-03` | **Structure follows the task, not the module.** A workspace opens on the work its role does, not on a list of the modules that back it | The `P03` workspace becomes a module menu, which is the Odoo default and the thing `04-00` §P03 explicitly rejects |
| `NVR-04` | **Never reveal what the user may not see.** A hidden item is hidden completely — not greyed, not counted, not returned by search | Information disclosure; breaches `URD` §19.4 and `05-04` |

---

# 4. Information Architecture Method

## 4.1 How the structure was derived

Three passes, in this order. The order matters: deriving from modules first produces a module menu.

| Pass | Input | Output |
|:--:|---|---|
| **1 — Audience** | 46 roles, 36 personas, the capability tables of `04-00` | Which surface each role uses, and for what |
| **2 — Task** | `RQ-008` user stories, the 15 critical journeys, the 28 SOPs | The tasks each surface must open onto, ranked by frequency |
| **3 — Object** | 371 module functional areas, 1,335 entities | The objects those tasks act on, grouped to the level navigation resolves to |

> **Frequency, not completeness, orders a menu.** A dispatcher's first item is the live queue,
> which they open two hundred times a day; "Reports" is last, because they open it weekly. Ordering
> by module number — the default when pass 3 runs first — puts them in the wrong order permanently.

## 4.2 Surface-to-audience map

| Surface | Primary audience | Volume | Top-level items | Default landing |
|---|---|---|---:|---|
| `P01` web | Individual customers | 250,000+/mo | **5** | Home — active services + book |
| `P01` app | Individual customers | — | **5** (tab bar) | Home |
| `P02` | Field & workshop technicians | 200–400 | **4** (tab bar) | **Today** — the job queue |
| `P03` | Back-office, branch, functional staff | 150–250 | **Workspace switcher (14)** | The user's default workspace |
| `P04` | Corporate & government clients | 500–2,000 | **6** | Estate dashboard |
| `P05` | Vendors, couriers, sub-contractors | 200–500 | **6** | Open orders |
| `P06` | Executives, directors, managers | 25–60 | **5** | Role-scoped executive board |
| `P07` | Marketplace sellers | 500–2,000 | **6** | Available work |
| `P08` | Brand partners | 50–150 | **5** | Claim pipeline |
| `P09` rider | Riders | 50–200 | **3** (tab bar) | **Today's manifest** |
| `P09` coordinator | Logistics coordinators | — | in `P03` | Consignment board |
| `P10` | Contact centre agents & supervisors | 30–80 | **4** | Unified queue |
| `P11` | Quality auditors, branch managers | 20–60 | **4** (tab bar) | Assigned audits |
| `P12` | Alliance partners, referrers | 100–500 | **5** | Referral dashboard |

> **Every count is ≤ 7** (`URD` §19.2). The field applications are ≤ 4 because a tab bar wider than
> four targets breaks one-handed thumb reach at `size.target.field` (`UX-006` §5.3).

## 4.3 Grouping and labelling rules

| # | Rule | Basis |
|---|---|---|
| `NVR-05` | A top-level item is a **noun the audience already uses**, taken from `UI-002` and `CG-004`. Never an internal term (`T-06`) | `UI-002` §2 |
| `NVR-06` | **Maximum two levels of menu.** A third level is a page, not a menu. Deeper menus defeat the click budget and are unusable on touch | `NFR-077` |
| `NVR-07` | Menu items are ordered by **task frequency**, measured or estimated, and the estimate is recorded so it can be corrected | §4.1 |
| `NVR-08` | An item that fewer than 5% of a surface's users can see does not belong in primary navigation. It belongs in search and in a settings area | `NVR-04` |
| `NVR-09` | **No menu item is a synonym of another.** "Devices" and "Assets" may not both appear; `CG-004` fixes which | `CG-004` §5 |
| `NVR-10` | Every top-level item resolves to a real landing screen. **No item exists only to open a submenu** | `NFR-077` |

---

# 5. The Click Budget — making `NFR-077` measurable

## 5.1 The problem with "≤ 4 clicks"

`NFR-077` is currently verified by "navigation audit / inspection" (`RQ-006` §4.4). **An inspection
of what, against which starting points, to which records?** Without a definition, the requirement
is unfalsifiable — which `RQA-02`'s sibling problem shows is the normal fate of an unmeasured
requirement.

## 5.2 The definition

> **`NVR-11`.** A **click** is any discrete user action that changes the primary content region:
> a link or button press, a menu selection, a tab change, a search submission, a row selection.
> Typing into a field is not a click. Scrolling is not a click. **Opening a disclosure that does not
> change the primary region is not a click.**
>
> A **record** is any instance of the 1,335 catalogued entities that the user has permission to view.
>
> A **starting point** is any of the surface's top-level landing screens, plus global search.

## 5.3 The budget table

| Path class | Budget | Rationale |
|---|:--:|---|
| Global search → record | **2** | Type, select result. **This is the guaranteed path and the reason SC 2.4.5 is met** |
| Landing → list → record | **2** | The common path |
| Landing → workspace → list → record | **3** | `P03` cross-workspace |
| Landing → list → filter → record | **3** | Where the list is long |
| Landing → record → related record | **3** | Following an association |
| **Any record from any starting point** | **≤ 4** | `NFR-077` |
| Primary action of the surface | **1** | `P01` "Book a service", `P02` "Start job", `P10` "Answer" |
| Role workspace from home | **1** | `04-00` §P03 |
| Help | **1** | WCAG SC 3.2.6 |

## 5.4 How it is verified

| # | Method | When |
|---|---|---|
| `NVR-12` | A **route-graph assertion** — the route table (§7) is compiled into a directed graph and the shortest path from every landing screen to every record route is computed. Any path > 4 fails the build | Every build, every surface |
| `NVR-13` | The graph is computed **per role**, using `05-04`, because a path that exists for an administrator may not exist for a branch agent | Every build |
| `NVR-14` | Global search is excluded from the graph when computing worst-case, then included to demonstrate the 2-click guarantee. **Both numbers are published** | Every build |

> **`NVR-13` is the one that will find defects.** The four-click promise is almost always true for a
> user who can see everything, and almost always false for a user who cannot. Testing only the
> administrator path is how this requirement passes an audit and fails in a branch.

---

# 6. Surface Architectures

## 6.1 Global chrome — identical on all thirteen surfaces

Positions are fixed. Labels are `UI-002` `common.nav.chrome.*`.

| Position | Element | Behaviour | Criterion |
|---|---|---|---|
| Top-left | Logo (28 px operational, 40 px `P01`/`P07`/`P12`) | Returns to the surface's landing screen | `VB-003` LG-01 |
| Top-left, after logo | Breadcrumb | Present on every drill-down | SC 2.4.8 |
| Top-centre | Global search | Present on **every** screen | SC 2.4.5 |
| Top-right | Notifications · Help · Language · Account | Fixed order, all thirteen surfaces | **SC 3.2.6**, SC 3.2.3 |
| — | Total chrome height | **≤ 96 px** | `VB-003` D-02, `LAY-02` |

| # | Rule |
|---|---|
| `NVR-15` | Chrome **declares its height** to the scroll container so a focused element is never obscured — WCAG 2.2 SC 2.4.11 (`UX-001` `FOC-04`) |
| `NVR-16` | The language control always shows the **other** language, never the current one (`UI-002` §3) |
| `NVR-17` | On `bp.xs`, chrome collapses to logo + search + account; notifications and help move into the account menu. **Help stays reachable in one action** (SC 3.2.6) |
| `NVR-18` | Field applications (`P02`, `P09`, `P11`) replace the chrome with a **sync status bar** (`C-62`) plus search and account. The sync bar is never collapsed or hidden (`AR-010` §6.2) |

## 6.2 `P03` — the fourteen workspaces

The largest and most consequential IA in the estate: one surface, 46 roles, 67 modules, 371
functional areas.

| # | Workspace | Role (`04-00` §P03) | Opens on | Frequency |
|---:|---|---|---|---|
| 1 | Service intake | Service centre agent | Queue · quick intake · customer search | Continuous |
| 2 | Dispatch console | Dispatch manager | Live map · unassigned queue · technician load · SLA risk | Continuous |
| 3 | Branch console | Branch manager | Today's numbers · WIP ageing · cash · staff · uncollected devices | Hourly |
| 4 | Workshop console | Workshop supervisor | Bench board · WIP by state · parts holds | Continuous |
| 5 | Inventory console | Inventory manager | Network stock · alerts · transfers · counts | Hourly |
| 6 | Procurement console | Procurement officer | Requisitions · POs · receipts · vendor performance | Daily |
| 7 | Finance console | Finance officer / manager | Invoices · receipts · reconciliation · ageing · close checklist | Continuous |
| 8 | HR console | HR officer / manager | Attendance exceptions · leave · payroll run · incentives | Daily |
| 9 | Quality console | Quality manager | NCRs · CAPAs · complaints · audits · checklists | Daily |
| 10 | Contract console | Account manager | Contract base · renewals · entitlements · profitability | Daily |
| 11 | Warranty console | Warranty officer | Claim pipeline · ageing · rejections · reconciliation | Daily |
| 12 | Marketplace console | Marketplace operations | Seller approvals · disputes · scores · payouts | Daily |
| 13 | Managed services console | MSP operations | Estate health · alerts · tickets · SLA · patch compliance | Continuous |
| 14 | System console | IT administrator | Users · roles · configuration · jobs · integrations · health | Weekly |

### 6.2.1 Workspace rules

| # | Rule | Basis |
|---|---|---|
| `NVR-19` | **A workspace opens on work, not on a menu.** Its landing screen is the board, queue or list its role acts on — never a dashboard of links | `04-00` §P03, `NVR-03` |
| `NVR-20` | Every workspace is **one click from anywhere** via `C-50` `WorkspaceSwitcher` | `04-00` §P03 |
| `NVR-21` | A user is granted **one default workspace** and may be granted others. The default is a user setting, seeded from the role | `05-04` |
| `NVR-22` | Workspaces the user cannot enter **do not appear in the switcher** (`NVR-04`) |
| `NVR-23` | Each workspace has **≤ 7** second-level sections. Counted against the module functional areas it surfaces; where a workspace exceeds 7, sections are grouped, not added | `URD` §19.2 |
| `NVR-24` | An object appears in **exactly one workspace as its home**, and may be *reachable* from others. Two homes for one object is the ambiguity `AR-005` exists to prevent | `AR-005` |

> **`NVR-24` is where the 371 functional areas are allocated.** The allocation table is
> `UX-003` §5.3, because it is the same act as assigning screens to surfaces. It is recorded once,
> there, rather than twice.

## 6.3 `P01` — customer, web and app

| Level | Web | App (tab bar) |
|---|---|---|
| 1 | Home · Book a service · My services · My devices · More | Home · Book · Services · Shop · Account |
| 2 (under More) | Contracts · Warranty · Shop · Loyalty · Trade-in · Recycling · Support | — |

| # | Rule |
|---|---|
| `NVR-25` | **"Book a service" is one click from every screen** on both surfaces. It is the surface's primary action and its conversion is the primary design KPI (> 72%) |
| `NVR-26` | The **public tracking path requires no login and no navigation** — a single addressable URL (§7.4). It is often the first 1000FiX interface a person ever sees |
| `NVR-27` | The web and app IA **differ in shape, not in content**. Every capability reachable on one is reachable on the other |
| `NVR-28` | Bengali is the default; the language control never resets navigation state (`UX-007` §6.2) |

## 6.4 `P02`, `P09`, `P11` — the field applications

| Surface | Tabs | Landing |
|---|---|---|
| `P02` | **Today · Job · Parts · Me** | Today — the optimised job queue |
| `P09` | **Manifest · Scan · Me** | Manifest |
| `P11` | **Audits · Capture · Findings · Me** | Assigned audits |

| # | Rule | Basis |
|---|---|---|
| `NVR-29` | **≤ 4 tabs.** More breaks thumb reach at `size.target.field` | `UX-006` §5.3 |
| `NVR-30` | **Every tab works offline.** A tab that requires a connection is a design defect, not a limitation | `P02` non-negotiable #7 |
| `NVR-31` | The **job context is never more than one action away** from any screen inside a job. A technician standing at a customer's device does not navigate | `URD` §20 |
| `NVR-32` | Navigation state survives app kill, battery death and reboot, and restores to the same screen with the same unsaved input | `AR-010` §4.1 |
| `NVR-33` | `P09` has **three** tabs because a rider operates in a helmet, in rain, on a motorcycle. This is the tightest budget in the estate and is not negotiable for feature reasons | `VB-007` §4, `A-03` |

## 6.5 The remaining external surfaces

| Surface | Top-level structure |
|---|---|
| `P04` | Estate · Requests · Contracts · Billing · Reports · Support |
| `P05` | Orders · Deliveries · Invoices · Performance · Catalogue · Profile |
| `P06` | Executive · Branches · Functions · Live · Explore |
| `P07` | Work · Listings · Earnings · Performance · Growth · Profile |
| `P08` | Claims · Parts · Rate cards · Performance · Quality |
| `P10` | Queue · Conversation · Customer · Quality |
| `P12` | Referrals · Rewards · Materials · Performance · Profile |

| # | Rule |
|---|---|
| `NVR-34` | Each is derived by pass 1–3 of §4.1 from its `04-00` capability table. The mapping is recorded in `UX-003` §5.2 so the derivation is auditable |
| `NVR-35` | `P10` has four items because an agent is **in a conversation**; navigation competes with a live customer. Everything else reaches through the conversation context (`04-00` §P10 — *agent screen switches per contact < 3*) |

---

# 7. Addressing — Routes and Deep Links

> **`UXA-05`: the estate requires deep linking eleven times and specifies it zero times.**
> Counted at 2026-08-18 21:40 (+06) across the 621 demand-side files, eleven require it —
> `NT-015`, `NT-016`, `NT-017` (*"every push opens the exact record"*), `NT-018` `IB-05`,
> `NT-022`, `OP-004`, `TPL_Notification_Template`, `P03` §12 (*"deep links into any `P03` record"*),
> `P06` §T-08 drill-through, `M10` `FR-LOY-033` referral links, and the content master index.
> **Not one states an address.** Every tracking SMS, claim email and push message implies a
> destination that no document defines. This section supplies the scheme.
>
> *(This finding was overstated at first issue as "no deep-link scheme exists anywhere". Eleven
> files discuss deep links; what none supplies is a scheme. Corrected during the Category 06
> audit — `UXA-20`.)*

## 7.1 Route grammar

```
https://<surface-host>/<locale>/<section>/<object>/<id>[/<sub>][?<query>]

<locale>   bn | en                       BCP 47 short form; full tag in Content-Language
<section>  a top-level navigation item   stable, never renamed without a redirect
<object>   the entity family             plural, kebab-case, from CG-004
<id>       the business reference        SR-2026-114882 — never a database key
<sub>      a tab or panel within record  optional
```

| # | Rule | Basis |
|---|---|---|
| `NVR-36` | **The URL carries the business reference, never the database primary key.** A key is not stable across migration (`MG-003`) and leaks record volume | RFC 3986; `SC-002` |
| `NVR-37` | Every route is **addressable, bookmarkable and shareable** subject to permission. A state reachable only by clicking through is not a screen, it is a modal |
| `NVR-38` | The locale segment is **always present**. A locale-less URL redirects to the user's preference, or to `bn` for `P01`, `P02`, `P09`, `P12` | `UX-007` §3 |
| `NVR-39` | A renamed section **keeps a permanent redirect**. Help articles, training decks, SMS messages and printed QR codes all carry URLs | `CG-006` |
| `NVR-40` | Query parameters carry **view state** — filter, sort, page, saved view. They never carry identity or authorisation |

### 7.1.1 Worked examples

| Purpose | Route |
|---|---|
| Customer's service order | `p01.1000fix.com/bn/services/service-orders/SR-2026-114882` |
| Its estimate tab | `p01.1000fix.com/bn/services/service-orders/SR-2026-114882/estimate` |
| Dispatch console, SLA-risk view | `erp.1000fix.com/en/dispatch?view=sla-risk&branch=BR-014` |
| Brand partner claim | `p08.1000fix.com/en/claims/warranty-claims/WC-2026-00871` |
| Seller payout statement | `p07.1000fix.com/bn/earnings/statements/2026-07` |
| **Public tracking, no login** | `track.1000fix.com/SR-2026-114882?t=<opaque-token>` |

## 7.2 Deep links from notifications

**Every notification type carries exactly one canonical destination.** The table below is the
contract `M27` implements and `NT-001` populates.

| Notification class | Destination | Surface | Auth |
|---|---|---|---|
| Booking confirmed | Service order detail | `P01` | Session or magic link |
| Technician on the way | **Public tracking** | `track` | Token |
| Estimate ready for approval | Estimate tab of the order | `P01` | Session (step-up for approval) |
| Payment due / receipt | Invoice detail | `P01`, `P04` | Session |
| Job assigned | Job detail | `P02` | Session |
| Sync failed, action needed | Sync queue detail | `P02`, `P09`, `P11` | Local |
| Consignment ready for collection | Manifest entry | `P09` | Session |
| Claim decision | Claim detail | `P08` | Session |
| PO issued | PO detail | `P05` | Session |
| SLA breach imminent | Filtered dispatch view | `P03` | Session |
| Contract renewal due | Contract detail | `P04`, `P03` | Session |
| Seller payout released | Payout statement | `P07` | Session |
| Dispute raised | Dispute detail | `P07`, `P03` | Session |
| Survey / NPS invitation | Survey screen | `P01` | Token |

| # | Rule |
|---|---|
| `NVR-41` | **A notification with no destination is not shippable.** `NT-026` message governance adds a mandatory `destination` field, and `M27` rejects a template without one |
| `NVR-42` | A deep link to a screen the recipient cannot see resolves to a **plain "you do not have access" screen that does not confirm the record exists** (`NVR-04`, `URD` §19.4) |
| `NVR-43` | An unauthenticated deep link **preserves the destination through sign-in** and lands there afterwards. Dropping the user on a home screen after login is the most common and most damaging navigation defect in notification flows |
| `NVR-44` | Token-authenticated links (`track`, survey) are **single-purpose, expiring and revocable**, and expose only the fields `LG-008` permits |

## 7.3 Mobile app links

| Scheme | Use |
|---|---|
| `https://` App Links (Android) / Universal Links (iOS) | **Primary.** A notification link opens the app if installed, the web surface if not |
| `fix1000://` custom scheme | Fallback only; never published in content |

| # | Rule |
|---|---|
| `NVR-45` | Custom schemes never appear in an SMS, email or printed document. They cannot be verified and they fail silently |
| `NVR-46` | App links resolve **offline** to the locally held record where one exists, and to a queued-fetch state where it does not (`UX-006` §4.5) |

## 7.4 Public and unauthenticated surfaces

| Surface | Route | Content |
|---|---|---|
| Public tracking | `track.1000fix.com/<ref>?t=` | Status, ETA, technician first name and photo, branch contact. **No price, no address history, no other orders** |
| Seller / vendor registration | `p07.1000fix.com/<locale>/register` | `UI-040` |
| Legal and policy | `1000fix.com/<locale>/legal/<doc>` | `LG-002`…`LG-024` |
| Status page | `status.1000fix.com` | Full brand (`VB-003` §4) |

---

# 8. Search — the second way

WCAG SC 2.4.5 requires **more than one way** to reach a page. Navigation is one; search is the
other, and on a system with 1,335 entities it is the primary one for anyone who is not doing a
routine task.

| # | Rule | Basis |
|---|---|---|
| `NVR-47` | Global search is on **every screen of every surface** | `URD` §19.2 |
| `NVR-48` | It accepts **Bengali and English simultaneously** in one query, with no mode switch | `URD` §19.2, `NFR-035` |
| `NVR-49` | Results return in **≤ 600 ms p95 including Bengali content** | `NFR-035` |
| `NVR-50` | Results are **permission-filtered before ranking**. A user never learns a record exists from a result count | `NVR-04` |
| `NVR-51` | An identifier typed in full (`SR-2026-114882`, an IMEI, a part number) navigates **directly** — one result, no result page. This is the 2-click guarantee of §5.3 |
| `NVR-52` | Results are **grouped by object type** with the type named, and each result shows enough to disambiguate — customer name plus device plus date, not just a reference |
| `NVR-53` | The search placeholder **states its scope** (`VB-006` SF-01): "Search service orders, customers, devices" — not "Search" |
| `NVR-54` | Scoped search inside a list filters that list and does not navigate away |
| `NVR-55` | **Zero results is a designed state** with a suggested next action (`UI-006` §3.2), never an empty page |
| `NVR-56` | Recent searches and the **last 5 records viewed** are offered on focus (`URD` §19.2) |

---

# 9. Wayfinding

## 9.1 Breadcrumbs

| # | Rule |
|---|---|
| `NVR-57` | Present on every drill-down screen, showing the **navigational** path, not the click history (SC 2.4.8) |
| `NVR-58` | The current page is the last crumb and is not a link |
| `NVR-59` | Crumbs truncate from the **middle**, never from the end; the end is where the user is |
| `NVR-60` | On `bp.xs`, the breadcrumb collapses to a single "back to <parent>" control |

## 9.2 Back behaviour

| # | Rule | Basis |
|---|---|---|
| `NVR-61` | Browser and hardware back **always work and never lose form state** | `URD` §19.2 |
| `NVR-62` | Back from a modal closes the modal; it does not leave the screen |
| `NVR-63` | Back from a wizard step returns to the previous step **with input preserved** |
| `NVR-64` | Leaving a screen with unsaved changes prompts once, naming what will be lost |
| `NVR-65` | On `R4`, back at the root of a tab returns to the first tab; back at the first tab prompts before exit — never exits silently with queued work (`UX-006` §4.4) |

## 9.3 Recent items and saved views

| # | Rule |
|---|---|
| `NVR-66` | **Last 5 records** accessible from navigation on every surface (`URD` §19.2) |
| `NVR-67` | Users can save, name and share list views and filter sets; a shared view is permission-checked **on open**, per viewer, not on share |
| `NVR-68` | A saved view is addressable (§7.1 query parameters) so it can be pasted into a message |

## 9.4 Permission-aware navigation

| # | Rule | Basis |
|---|---|---|
| `NVR-69` | An item the user may not access is **absent**, not disabled | `NVR-04` |
| `NVR-70` | Counts and badges never include records the user may not see |
| `NVR-71` | A direct URL to a forbidden record returns the same response as a non-existent one | `URD` §19.4 |
| `NVR-72` | The menu is computed **server-side from `M29` scopes**, never assembled client-side from a role name. A client-assembled menu is an information disclosure by construction | `SC-004` |
| `NVR-73` | Menu composition is tested per role for all 46 roles (`NVR-13`) |

## 9.5 Cross-surface navigation

| # | Rule |
|---|---|
| `NVR-74` | A link from one surface to another carries the **object reference**, and the target surface resolves it to its own route. Cross-surface links never carry the source surface's route |
| `NVR-75` | Where a user holds identities on two surfaces, single sign-on carries the session (`M29`); where they do not, the link lands on a sign-in that preserves the destination (`NVR-43`) |
| `NVR-76` | `P10` agents jump to any relevant ERP screen **and return with the conversation intact** (`04-00` §P10). The conversation is the persistent context; the ERP screen is transient |

## 9.6 Help — WCAG 2.2 SC 3.2.6

| # | Rule |
|---|---|
| `NVR-77` | The help control is in the **same relative position on all thirteen surfaces** — top-right of global chrome (§6.1). This is a Level A criterion new in WCAG 2.2 and it is trivially met by construction and trivially broken by one surface deviating |
| `NVR-78` | Help opens the `HC-001` set **scoped to the current surface and screen**, not a generic home |
| `NVR-79` | Human contact is reachable from help in **one further action** on every surface — the criterion covers contact details, not only documentation |

---

# 10. Governance

## 10.1 A label change is not a label change

`UI-002` records that every help article and training slide cites navigation labels verbatim in
bold (`CG-003` X-03). Counted at 2026-08-18 14:45 (+06), the estate holds **16 help files, 2
training framework files and 18 test-and-acceptance files** that cite navigation.

| # | Rule |
|---|---|
| `NVR-80` | Changing a navigation label is a **coordinated edit** across `UI-002`, `BN-009`…`BN-013`, the `HC` set, the `TR` set and the `TS` set, raised as one change under `CG-006` |
| `NVR-81` | Changing a **route** additionally requires a permanent redirect (`NVR-39`) and a sweep of `NT-*` templates for embedded links |
| `NVR-82` | Adding a top-level item requires removing one, or a Design Authority decision that the surface may exceed its budget. **The budget is the design; exceptions erode it silently** |

## 10.2 Namespace ruling *(closes `UXA-04`)*

`UI-002` §1 declares the namespace `common.nav.*`; its §3 then uses `common.nav.chrome.*`,
`ws.nav.switcher.*` and `p01.nav.primary.*`. Three namespaces where one was declared.

> **Ruling.** The declaration is too narrow, not the usage. Navigation strings occupy three
> namespaces by design, and the rule is:
>
> | Namespace | Contains |
> |---|---|
> | `common.nav.*` | Chrome present on every surface |
> | `ws.nav.*` | `P03` workspace switching and workspace-internal sections |
> | `<surface>.nav.*` | That surface's primary navigation — `p01.nav.*`, `p04.nav.*`, … |
>
> `UI-002` §1 is corrected to declare all three. Raised as a content change under `CG-006`;
> recorded here because this document is where the structure that needs three namespaces is defined.

## 10.3 Ownership

| Element | Owner | Approver |
|---|---|---|
| Surface IA | Head of Product Design | Design Authority |
| Labels | Content Design Lead (`UI-002`) | Content Design Lead |
| Route table | Chief Architect | Design Authority |
| Deep-link contract | `M27` product owner | Design Authority + Chief Architect |
| Permission-aware menu | Identity engineering (`M29`) | Security Architect |

---

# 11. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `UX-002-D-01` | How to make `NFR-077` verifiable | (a) manual navigation audit; (b) **route-graph shortest-path assertion, per role** | **(b)** | An inspection with no defined starting points or targets cannot fail. A graph assertion can | The route table becomes a build input, not documentation |
| `UX-002-D-02` | Business reference or database key in URLs | (a) key; (b) **business reference** | **(b)** | Keys are unstable across migration and leak volume | Every entity needs a stable public reference — raised to `DA-002` |
| `UX-002-D-03` | `P03` structure | (a) module menu (Odoo default); (b) **14 task-scoped workspaces** | **(b)** | `04-00` §P03 requires it; a module menu puts a dispatcher four levels from the queue | 371 functional areas must be allocated to 14 workspaces — `UX-003` §5.3 |
| `UX-002-D-04` | Field-app tab count | (a) 5 for feature parity; (b) **≤ 4, 3 for `P09`** | **(b)** | Thumb reach at `size.target.field`; a rider in a helmet | Some capabilities move inside the job context rather than onto a tab |
| `UX-002-D-05` | Namespace count for navigation | (a) force everything into `common.nav.*`; (b) **three declared namespaces** | **(b)** | Workspace and surface navigation are genuinely different scopes | `UI-002` §1 correction raised under `CG-006` |
| `UX-002-D-06` | Forbidden-record response | (a) 403 "no access"; (b) **identical to not-found** | **(b)** | A distinguishable 403 confirms existence | Slightly worse diagnostics for legitimate users; `NVR-42` copy compensates |

---

# 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Which of the 14 workspaces is each of the 46 roles defaulted to? `05-04` maps permissions, not defaults | Head of Product Design + HR | W1 | `NVR-21` |
| `Q-02` | Does `P09`'s coordinator view live inside `P03` as a fifteenth workspace, or as a separate surface? `04-00` §P09 says "coordinator view (web)"; the Technology Stack says Odoo Web | Chief Architect | **W3** | §4.2, workspace count |
| `Q-03` | Is there one host per surface or one host with path prefixes? §7.1 assumes per-surface hosts; this is a `PE-001` decision with cookie-scope and CSP consequences | Chief Architect | **W1** | Route table, session design |
| `Q-04` | What is the public tracking token's lifetime and revocation rule? | Security Architect + `LG-008` owner | W2 | `NVR-44` |
| `Q-05` | Do all 1,335 entities need a stable public reference, or only the ~120 that appear in a URL? | Data Architect (`DA-002`) | W1 | `UX-002-D-02` |
| `Q-06` | Search ranking authority — is relevance tuned per surface or globally? | BI Lead | W2 | `NVR-52` |

---

# 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every one of the thirteen surfaces has a stated top-level structure with a counted item budget ≤ 7 | §4.2, §6 |
| `AC-02` | `NFR-077` has a definition, a budget table and an automated verification method | §5 |
| `AC-03` | A route grammar exists and resolves for every surface | §7.1 |
| `AC-04` | Every notification class has a named deep-link destination | §7.2 |
| `AC-05` | Permission-aware navigation is specified so that no menu, count or search result can disclose a record | §9.4 |
| `AC-06` | WCAG 2.2 SC 2.4.5, 2.4.8, 3.2.3 and **3.2.6** are each satisfied by a named rule | §6.1, §8, §9.1, §9.6 |
| `AC-07` | The `UI-002` namespace defect is ruled and the correction raised | §10.2 |

**Definition of done.** Complete when every criterion is met, `Q-02` and `Q-03` are decided, the
route table is committed as a build input, and `PGD-000`'s `UX-002` row is updated with a fresh
enumeration timestamp.

---

# 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-006` `NFR-077`, `NFR-035` | The requirements this realises |
| Upstream | `UX-001` `C-49`…`C-60` | The components that render this structure |
| Upstream | `05-04` | Role matrix feeding `NVR-72` |
| Downstream | **`UX-003`** | Screens are assigned to the sections defined here; §5.3 allocates the 371 functional areas |
| Downstream | **`UX-004`** | Transitions between the states defined here |
| Downstream | **`UX-006`** | Field-app tab model and offline navigation |
| Downstream | `IN-002` | Search and menu endpoints |
| Downstream | `NT-001`, `M27` | Deep-link destination contract |
| Downstream | `CH-*` training, `HC-*` help | Navigation paths cited in content |
| Lateral | `UI-002` | Labels; namespace correction §10.2 |
| Lateral | `HC-001` | Help-centre IA joins at §9.6 |

---

# 15. References

**Within this repository**
`../PGD-000_…` · `./_CATEGORY_OVERVIEW.md` · `./UX-001`, `./UX-003`, `./UX-004`, `./UX-006`, `./UX-007` ·
`../01_Requirements_Engineering/RQ-006`, `RQ-008` · `../02_Architecture_and_Design/AR-001`, `AR-005`

**Workspace**
`../../1000fix_ERP_Module/04_Portals_and_Applications/04-00` §P01–§P12 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04`, `05-06` ·
`../../project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-002` ·
`../../project_content/09_Help_Centre_and_Self_Service/HC-001` ·
`../../project_content/04_Notification_and_Messaging/NT-001`, `NT-026` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_URD.md` §3, §4, §19

**External standards and sources**

| Source | Verified |
|---|---|
| ISO 9241-210:2019 — Ergonomics of human-system interaction — Human-centred design for interactive systems | 2026-08-18 |
| W3C — WCAG 2.2, SC 2.4.5, 2.4.8, 3.2.3, **3.2.6 Consistent Help (new in 2.2, Level A)** | 2026-08-18 |
| IETF RFC 3986 — Uniform Resource Identifier (URI): Generic Syntax | 2026-08-18 |
| IETF BCP 47 — Tags for Identifying Languages | 2026-08-18 |
| ISO 9241-112:2017 — Principles for the presentation of information | 2026-08-18 |

---

# 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Head of Product Design | Initial issue. Converts `UI-002`'s label register into a structure: thirteen surface architectures, a **click-budget model that makes `NFR-077` machine-verifiable per role**, a route grammar, and **the first deep-link scheme in the estate** (`UXA-05`). Rules the `UI-002` namespace defect (`UXA-04`) | *(pending — `PGD-A1-09`)* |

---

*`UX-002` · Category 06 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
