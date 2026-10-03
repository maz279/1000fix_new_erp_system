---
id: RF-005
title: Content-to-Portal Coverage Map
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead with Content Design Lead and Localisation Lead
reviewers: [CTO, Content Design Lead, Localisation Lead, QA Lead, Legal & Compliance, Support Lead, all Portal Owners]
approver: Programme Content Lead
content_class: E
purpose: >
  The go-live gate for each of the twelve portals, expressed as content. A portal cannot launch at
  90% of its content: a customer meeting an untranslated error message, a technician meeting an
  English offline-sync warning, or a seller meeting an unwritten payout dispute page is a launch
  failure regardless of build quality. This map states, per portal, the content it requires, what
  exists, what is missing, and whether the Bengali obligation that `PS-03` makes non-negotiable is
  met. It also corrects the Master Index §5 coverage table, which undercounts portal content by a
  factor of nearly four and has been read as a count for the life of the register.
traces_to: [04-00, 05-01, 05-04, 05-06, 06-01, 06-02, PS-01, PS-02, PS-03, PS-04, PS-06, PS-08, PS-09, CP-04, RF-001, RF-003, RF-004, RF-007, RF-012, CG-010]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md §2 suite table — audience, population, technology and wave per portal; §3 PS-01…PS-12; per-portal capability sets and KPI targets
    verified: 2026-08-18
    class: P1
  - source: Extraction of traces_to front matter across all 429 written content files for Pnn targets, run 2026-08-18 — produced the per-portal content lists in §4.4
    verified: 2026-08-18
    class: P1
  - source: Extraction of distinct FR- identifiers and AC- rows per portal file, run 2026-08-18 — 376 distinct FR-POR-family requirements and 260 acceptance criteria across the 12 P*.md files
    verified: 2026-08-18
    class: P1
  - source: project_content/1000FiX_ERP_Content_Master_Index.md §5 Cross-Reference Content Coverage by Portal — the table this file supersedes as a coverage statement
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md §3.2 — 266 of 452 files bilingual; per-category splits used in §4.5
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-012_Category_11_BN_Content_Audit.md finding BN-01 — the common.* namespace of 154 shared strings has no registered Bengali owner; P02 Bengali completeness counted at 44%
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2026-11-18
---

# RF-005 — Content-to-Portal Coverage Map

> **The rule this file exists to enforce.** *A portal cannot go live with 90% of its content.*
> Content is not a percentage-complete deliverable at a portal launch: the missing 10% is
> precisely the part a user meets on the day something goes wrong.

---

## 1. Purpose

Twelve portals serve eleven distinct audiences across five front-end frameworks, in two
languages, with populations ranging from twenty auditors to a quarter of a million customers a
month. Each has a documented adoption target in `04-00`, and each of those targets is met or
missed principally on content.

Three things make a portal-level map necessary rather than merely useful:

1. **The launch unit is the portal, not the module.** `M20` ships across `P01`, `P03`, `P04` and
   `P10`. A gate that clears `M20` says nothing about whether `P04` has a corporate invoice
   dispute page.
2. **The Bengali obligation is portal-scoped and non-negotiable on two of them.** `PS-03` requires
   Bengali throughout with Bengali default on customer and field surfaces. `P02`'s own
   non-negotiable requirement #3 is a *complete* Bengali interface **including error messages**.
   That is a per-portal completeness test, and it currently fails.
3. **Master Index §5 is being read as a coverage count and is not one.** It lists 109
   portal-content links. Enumeration finds **418**. §4.3 explains the difference and why the
   undercount matters.

---

## 2. Scope

**In scope** — all twelve portals; the content each requires by type; enumerated coverage;
Bengali completeness; the launch-gate checklist per portal; the correction to Master Index §5.

**Out of scope**

| Excluded | Owner |
|---|---|
| Module content readiness | `RF-004` |
| Requirement denominator and traceability model | `RF-003` |
| Portal functional design | `04-00` and the twelve `P*` specifications |
| Bengali wording itself | `BN-003`, `BN-009`–`BN-013` |
| Which content is bilingual | `CG-010` §3.2 |

> **Filing caveat.** All twelve portal specifications are on disk in
> `03_Modules/K_Platform_and_Technology/`, not in `04_Portals_and_Applications/`. This is audit
> finding **AF-01**, open, awaiting a CTO decision. `AUDIT-001` records that until it is resolved
> *"`RF-005` cannot be maintained mechanically"*. It is maintained here by **identifier**, not by
> path, which removes the dependency — see §6.

---

## 3. Audience

| Reader | Uses this map to |
|---|---|
| **A portal owner** | See their launch-gate content position in one row |
| **The CTO at a go-live decision** | Take a content verdict per portal with named blockers |
| **The Localisation Lead** | See Bengali completeness per portal against `PS-03` |
| **The Support Lead** | Anticipate contact volume from portals launching with help gaps |
| **The Programme Content Lead** | Direct authoring capacity at the portal launching next |

---

## 4. Content

### 4.1 The twelve portals

From `04-00` §2, with requirement and acceptance-criteria counts enumerated 2026-08-18.

| Portal | Audience | Population | Technology | Wave | Reqs | AC |
|---|---|---|---|:--:|---:|---:|
| `P01` Customer Self-Service | Individual customers | 250,000+/month | Next.js 15 + React Native | W2 | 40 | 23 |
| `P02` Technician Mobile | Field & workshop technicians | 200–400 | Flutter | W2 | 46 | 24 |
| `P03` Admin Operations | Back-office & branch staff | 150–250 | Odoo Web (OWL 2) | W1 | 34 | 23 |
| `P04` Corporate B2B | Corporate & government clients | 500–2,000 | Next.js 15 | W4 | 34 | 19 |
| `P05` Vendor & Supplier | Parts vendors, couriers, sub-contractors | 200–500 | Odoo Portal + Next.js | W3 | 26 | 19 |
| `P06` Analytics & Executive | Management | 25–60 | Metabase + Grafana | W4 | 24 | 23 |
| `P07` Marketplace Seller | External engineers & shops | 500–2,000 | Next.js 15 + React Native | W7 | 34 | 21 |
| `P08` Brand Partner | 17+ brand partners | 50–150 | Next.js 15 | W4 | 30 | 20 |
| `P09` Logistics & Rider | Riders, coordinators, couriers | 50–200 | Flutter | W3 | 31 | 23 |
| `P10` Contact Centre Console | Agents & supervisors | 30–80 | Next.js 15 | W4 | 28 | 22 |
| `P11` Field Auditor & Quality | Auditors, branch managers | 20–60 | Flutter | W5 | 27 | 22 |
| `P12` Partner & Referral | Alliance partners, referrers | 100–500 | Next.js 15 | W7 | 25 | 21 |
| | | | | | **376** distinct | **260** |

---

### 4.2 The required content set per portal type

Derived from the register, not asserted. A portal's verdict is measured against this.

| Content type | External customer-facing (`P01`, `P07`) | Field mobile (`P02`, `P09`, `P11`) | Internal desktop (`P03`, `P10`) | B2B / partner (`P04`, `P05`, `P08`, `P12`) | Analytics (`P06`) |
|---|:--:|:--:|:--:|:--:|:--:|
| `UI` portal copy pack | ● | ● | ● | ● | ● |
| `UI` cross-cutting libraries (`UI-001`–`UI-010`) | ● | ● | ● | ● | ● |
| `BN` Bengali string bundle | ● **default** | ● **default** | ● | ◐ | ◐ |
| `NT` notification set | ● | ● | ◐ | ● | ◐ |
| `HC` help set | ● | ● | ● | ● | ● |
| `LG` binding terms | ● | ◐ | ◐ | ● | ◐ |
| `TR` training pack | ○ | ● | ● | ○ | ○ |
| `EO` onboarding kit | ○ | ○ | ○ | ● | ○ |
| `DT` documents the portal issues | ● | ● | ● | ● | ○ |
| `TS` test scripts incl. accessibility | ● | ● | ● | ● | ● |
| `OP` support and status content | ● | ● | ● | ● | ◐ |
| `KB` offline knowledge pack | ○ | ● | ○ | ○ | ○ |

**●** required · **◐** required where the audience or `CG-010` §3.2 calls for it · **○** not required

---

### 4.3 Correction — Master Index §5 undercounts portal content by 3.8×

**What Master Index §5 states.** A table headed *"Cross-Reference: Content Coverage by Portal"*
with a **"Total direct"** column, summing to **109** across twelve portals — from 5 (`P06`) to 27
(`P03`).

**What enumeration finds.** Counting every content file that declares a portal in `traces_to:`:

| Portal | Master Index §5 | Enumerated 2026-08-18 | Difference |
|---|---:|---:|---:|
| `P01` | 11 | **42** | +31 |
| `P02` | 8 | **55** | +47 |
| `P03` | 27 | **67** | +40 |
| `P04` | 9 | **40** | +31 |
| `P05` | 8 | **25** | +17 |
| `P06` | 5 | **23** | +18 |
| `P07` | 9 | **27** | +18 |
| `P08` | 7 | **34** | +27 |
| `P09` | 6 | **35** | +29 |
| `P10` | 6 | **26** | +20 |
| `P11` | 6 | **24** | +18 |
| `P12` | 7 | **20** | +13 |
| **Total** | **109** | **418** | **+309** |

**Why the two differ, and why it is not simply an error.** Master Index §5 counts only files whose
*primary* subject is that portal, and its own footnote says so: *"Cross-cutting content (`CG`,
`VB`, `MD`, `SP`, `DT`, `RP`, `TS`, `OP`, `RF`) serves all twelve and is not repeated per portal —
principle `CP-01`."* That is a defensible editorial choice for a **cross-reference**.

**It is not defensible for a coverage table**, and the column is headed "Total direct". Three
consequences have already followed:

1. **`P06` reads as the least-served portal at 5 files.** It has 23 — including all seven `RP`
   dashboard and semantic-layer files, without which the portal cannot be built at all.
2. **`P02` reads as thinner than `P03`** (8 against 27). Enumerated, `P02` has 55 — the second
   most-served portal in the register, as its non-negotiable requirements demand.
3. **The go-live gate cannot use it.** A gate needs to know that `P09` depends on `DT-028` proof of
   delivery and `KB-013` battery safety. §5 shows neither.

**Ruling `PC-01`.** Master Index §5 remains as a **cross-reference of portal-primary content** and
its column is renamed *"Portal-primary files"*. **This file is the coverage map**, and any gate,
paper or plan quoting portal content coverage cites `RF-005` §4.4. Carried to `RF-012` as finding
`RF-02` and to `RF-006` as decision `CD-03`.

---

### 4.4 The map

Content lists are enumerated from `traces_to:`. **Verdicts use the `RF-004` scheme**
(`READY` · `THIN` · `GAP` · `BLOCKED`), applied against §4.2.

#### `P01` — Customer Self-Service Portal & Mobile App · W2 · 42 files

| Type | Content | Status |
|---|---|---|
| `UI` | `UI-011` pack + `UI-001`–`UI-010` cross-cutting + `UI-037`–`UI-042` flows | Written |
| `BN` | `BN-009` Bengali bundle, `BN-001` strategy | Written; **not signed off in context** |
| `NT` | `NT-004` SMS, `NT-009` email, `NT-015` push, `NT-018` inbox, `NT-002` consent | Written |
| `HC` | `HC-003` help set, `HC-015` FAQ, `HC-016` tours, `HC-017`–`HC-020` AI + video | Written; AI set at W6 |
| `LG` | `LG-002` terms, `LG-008` privacy, `LG-011` cookies, `LG-013` warranty, `LG-014` refund, `LG-017`–`LG-019` | Written; **all await G5** |
| `DT` | `DT-032` warranty certificate, `DT-034` data destruction | Written |
| `TS` | `TS-011` portal scripts, `TS-014` performance, `TS-016` accessibility | Written; **`TS-016` has no reviewer** |
| `OP` | `OP-005` status page, `OP-011` app operations | Written |
| `CM` | `CM-006` go-live, `CM-013` customer migration, `CM-016` adoption | Written |

**Verdict: `THIN`.** Every required type is present. Two blockers: the Bengali bundle has no
in-context sign-off (`CM-R6` blocks approval), and eight `LG` files gate on G5 legal review that
has not started. **Booking-funnel conversion target > 72% and 88% online booking depend on copy
that cannot be approved.**

#### `P02` — Technician Mobile Application · W2 · 55 files

| Type | Content | Status |
|---|---|---|
| `UI` | `UI-012` pack, `UI-009` offline/sync copy | Written |
| `BN` | `BN-010` bundle, `BN-006` typography, `BN-017` voice | Written |
| `KB` | **All 16 `KB` files** + `KB-016` offline reference card set | Written **as specifications only** |
| `TR` | `TR-009` field technician pack (Bengali-native), `TR-022` job aids | Written |
| `HC` | `HC-004` help set + `HC-001`, `HC-002`, `HC-015`, `HC-016`, `HC-020` | Written |
| `NT` | `NT-005` SMS, `NT-016` push | Written |
| `DT` | `DT-003` job card, `DT-028` POD, `DT-044` labels | Written |
| `SP` | `SP-008` field visit, `SP-016` van stock, `SP-022` attendance, `SP-030` safety, `SP-033` triage | Written |
| `TS` | `TS-015` offline/field scripts, `TS-014` performance | Written; **field logistics unresourced** |

**Verdict: `BLOCKED`.** Three named blockers:

1. **`PS-03` / `P02` non-negotiable #3 fails.** The `common.*` namespace — **154 shared strings
   loading on every portal** — has no registered Bengali owner. `P02` Bengali completeness is
   counted at **44%** (`AUDIT-012` `BN-01`). `BN-019` must be registered.
2. **Every `KB` file specifies content that does not exist.** 160 articles, 22 tool guides and 48
   reference cards, estimated at **775–1,545 specialist hours, unresourced** (`AUDIT-008` `R-07`).
   `KB-016` is the *offline pack shipped inside the app* and it has nothing to package.
3. **`TS-015` cannot be executed** — no field logistics (`AUDIT-014`). The 24-hour offline,
   30-second sync and sub-12% battery non-negotiables are therefore unevidenced.

#### `P03` — Admin Operations Portal · W1 · 67 files

| Type | Content | Status |
|---|---|---|
| `UI` | `UI-013` pack + **`UI-023`–`UI-036` fourteen workspace packs** + `UI-041` bulk actions | Written |
| `BN` | `BN-011` bundle | Written |
| `TR` | `TR-007`, `TR-008`, `TR-010`–`TR-016`, `TR-021`–`TR-023` | Written |
| `HC` | `HC-005` help set, `HC-008`, `HC-016` | Written |
| `SP` | Thirteen SOPs across intake, workshop, inventory, cash, IT | Written |
| `KB` | Nine troubleshooting and reference files | Specifications only |
| `RP` | `RP-004` operational console dashboards | Written |
| `LG` | `LG-011`, `LG-020` acceptable use, `LG-022` quality policy | Written |
| `TS` | `TS-014`, `TS-016` | Written |
| `OP` | `OP-001` support model | Written |

**Verdict: `THIN`.** The most-covered portal, and appropriately so — fourteen workspaces, 150–250
users, a four-hour time-to-competence target. Blockers: `OP-001` support model is `P0` at W1 while
`M66` lands at **W6** (`AUDIT-017` `OP-06`), and **the 38 access profiles `UI-036` and `OP-015`
assume do not exist** (`OP-10`).

#### `P04` — Corporate B2B Portal · W4 · 40 files

**Verdict: `BLOCKED`.** `DT-031` maps **nine `MD-028` fields that do not exist**, and `MD-028` has
no clock start/stop event field at all (`AUDIT-013` `LG-01`). `P04` publishes an SLA with service
credits (`AC-10`) and commits to an invoice-dispute rate below 3%. **Service credits cannot be
computed from the content as written.** Secondary: `credit_note.issued` — the event `P04` `AC-10`
publishes — **does not exist in the `05-03` event inventory** (`AUDIT-016` `AP-01`).

#### `P05` — Vendor & Supplier Portal · W3 · 25 files

**Verdict: `THIN`.** All required types present: `UI-015`, `HC-007`, `EO-005`, `EO-006`,
`LG-006`, `NT-011`, `DT-022`/`DT-023`, `TR-013`, `CM-015`. Correctly English-only under `CG-010`
§3.2. Blocker: three W3 courier integrations carry **customer name, phone and address** and are
`Undetermined` in the Class B disclosure register (`AUDIT-016` `AP-08`) — a data-protection
blocker on a portal, not a content gap.

#### `P06` — Analytics & Executive Dashboard · W4 · 23 files

**Verdict: `GAP`.** Content coverage is adequate — `UI-016`, `HC-008`, and **all sixteen `RP`
files**. The gap is upstream and fatal to the portal's purpose:

- **250 KPI identifiers in use against 95 registered** (`AUDIT-015` `RP-01`)
- **44 of 95 KPI baselines are absent**, and `06-02` §6 states a KPI without a baseline cannot
  claim a benefit — roughly **BDT 396 lac of the 876 lac base case** rests on them (`RP-02`)
- **1,063 reports specified across 79 specifications**, never counted before (`RP-03`)

`P06` commits management to 100% of decisions on live data. A dashboard whose metrics are
ambiguous produces confidently wrong decisions faster than a spreadsheet.

#### `P07` — Marketplace Seller Portal & App · W7 · 27 files

**Verdict: `BLOCKED`.** `AUDIT-018` `EO-01`: a configurable payout hold, an unbounded dispute
block and an unbounded appeal are set against the Digital Commerce Operation Guidelines 2021
**ten-day settlement obligation** and **72-hour complaint obligation**, and the Consumer Rights
Protection Act 2009 §60 **30-day** consumer window. **No stage SLA exists anywhere, no 72-hour
path exists, and no compliance officer is named in any programme document.** Compounding:
decision `D-03` (principal or agent) is unmade, and `SP-024` names **`LG-018` — the e-waste
statement — as the Marketplace Seller Agreement in five places** (`EO-08`).

#### `P08` — Brand Partner Portal · W4 · 34 files

**Verdict: `THIN`.** Well covered: `UI-018`, `HC-010`, `EO-003`, `EO-004`, `LG-005`, `DT-033`,
`AP-007`, five `KB` files. Blockers: `MD-017`'s **"17+ brands" figure remains unverified**
(`00-07` H2-12) while `EO-004` per-brand claim rules depend on it; and
**`recall.execution_updated` — a product-safety event — does not exist** in the `05-03` inventory
(`AUDIT-016` `AP-01`), while `KB-010` requires recall notices to be acted on.

#### `P09` — Logistics & Rider Application · W3 · 35 files

**Verdict: `THIN`.** Strong: `UI-019`, `UI-009` offline, `BN-013`, `HC-011`, `TR-020`, `DT-027`,
`DT-028`, `DT-044`, `SP-009`, `KB-013`, `KB-016`, `NT-017`, `OP-011`. Blockers: shares the
`common.*` Bengali gap with `P02`; `TS-015` field scripts unexecutable. Custody-break target is
**zero** and POD completeness **100%** — both evidenced only by `DT-028`, whose scan-and-identity
rule `BRU-LOG-01` depends on labels (`DT-044`) that are written but unpinned to a release.

#### `P10` — Contact Centre Agent Console · W4 · 26 files

**Verdict: `THIN`.** `UI-020`, `HC-012`, `SP-034` scripts, `TR-017`, `NT-019` IVR, `BN-017`
Bengali voice, `OP-003` macros, `OP-004` incident templates. Blocker: `HC-017`/`HC-018` AI intent
and response libraries are scheduled **W6**, two waves after the console. Agents get AI assist at
W4 with no governed intent set — and the transcript-derived work that would build one **has no
confirmed lawful basis under PDPA 2026** (`AUDIT-010` `HC-01`).

#### `P11` — Field Auditor & Quality Application · W5 · 24 files

**Verdict: `THIN`.** `UI-021`, `HC-013`, `TR-016`, `DT-043` NCR/CAPA forms, `SP-029`, `SP-032`,
`KB-012`, `KB-013`, `LG-022`, `TS-015`. Blocker: **ISO 9001:2026 publishes 16 September 2026**
with transition to September 2029 (`RF-008` `ST-12`). Every clause citation in `DT-043`,
`SP-029`, `LG-022` and `TR-016` re-opens inside the programme window — and `P11` is the
application the certification body will inspect.

#### `P12` — Partner & Referral Portal · W7 · 20 files

**Verdict: `GAP`.** `UI-022`, `HC-014`, `EO-009`, `EO-012`, `LG-007`, `DT-040`, `BN-013`.
Blockers: **`05-05` carries no business rule for `M40`** — the module `P12` runs on
(`AUDIT-018` `EO-02`); and **`EO-014` exit content is registered up to twenty-two months after the
first exit it governs becomes possible** (`EO-03`). Partner commission accuracy target is **100%**
and disputes start with wording; `DT-040` is the only commission content and it is unapproved.

---

### 4.5 Bengali completeness — the `PS-03` gate

`CG-010` §3.2 registers 266 bilingual files of 452. Portal-facing completeness:

| Portal | Bengali requirement | Bundle | Counted completeness | Gate |
|---|---|---|---|:--:|
| `P01` | **Bengali default** (`PS-03`) | `BN-009` | Bundle written; **no in-context sign-off** | ❌ |
| `P02` | **Complete Bengali incl. error messages** — non-negotiable #3 | `BN-010` | **44%** (`AUDIT-012` `BN-01`) | ❌ |
| `P03` | Bengali available | `BN-011` | Bundle written; 47 KB, the largest | ⚠ |
| `P04`–`P06` | Bengali available | `BN-012` | Written | ⚠ |
| `P07`–`P12` | Bengali default on `P07`, `P09` | `BN-013` | Written | ⚠ |
| **All twelve** | `common.*` — **154 shared strings on every portal** | **none** | **No registered owner** | ❌ |

**The `common.*` finding is the single largest portal blocker in the register.** It is not one
portal's problem: 154 strings load on all twelve. `BN-019` must be registered, taking Category 11
to 19 files. Until then **no portal can claim `PS-03` conformance**, and two of them have made it
a non-negotiable.

Compounding: **289 Bengali strings have no English source row** (`AUDIT-012` `BN-18`) — the `UI`
packs are representative rather than complete, so the Bengali bundles are ahead of their sources
in places and behind in others.

---

### 4.6 Summary and launch verdicts

| Portal | Wave | Files | Verdict | Primary blocker |
|---|:--:|---:|:--:|---|
| `P01` Customer | W2 | 42 | `THIN` | Bengali sign-off; 8 `LG` files at G5 |
| `P02` Technician | W2 | 55 | **`BLOCKED`** | `common.*` Bengali 44%; `KB` corpus unwritten; `TS-015` unexecutable |
| `P03` Admin | W1 | 67 | `THIN` | `OP-001` needed W1, `M66` lands W6; 38 access profiles absent |
| `P04` Corporate | W4 | 40 | **`BLOCKED`** | `DT-031` maps nine non-existent `MD-028` fields |
| `P05` Vendor | W3 | 25 | `THIN` | Three courier integrations `Undetermined` under PDPA |
| `P06` Analytics | W4 | 23 | **`GAP`** | 196 unregistered KPIs; 44 baselines absent |
| `P07` Seller | W7 | 27 | **`BLOCKED`** | Statutory settlement/complaint obligations unmet; `D-03` unmade |
| `P08` Brand | W4 | 34 | `THIN` | "17+ brands" unverified; recall event missing |
| `P09` Rider | W3 | 35 | `THIN` | `common.*` Bengali; `TS-015` unexecutable |
| `P10` Contact Centre | W4 | 26 | `THIN` | AI content two waves late; no lawful basis for transcripts |
| `P11` Auditor | W5 | 24 | `THIN` | ISO 9001:2026 re-opens every clause citation |
| `P12` Partner | W7 | 20 | **`GAP`** | No `M40` business rules; exit content 22 months late |

| Verdict | Portals |
|---|---:|
| `READY` | **0** |
| `THIN` | 7 |
| `GAP` | 2 |
| `BLOCKED` | 3 |

**No portal is content-ready.** The two earliest — `P03` at W1 and `P01`/`P02` at W2 — are `THIN`,
`THIN` and `BLOCKED`.

---

### 4.7 The per-portal launch checklist

A portal passes the content gate when **every** line is evidenced. This is the operative
instrument of this file.

| # | Criterion | Evidence |
|---|---|---|
| `PG-01` | `UI` portal pack **approved** and pinned to the release (`CG-006` §3) | `pinned_to:` names a real build |
| `PG-02` | `UI-001`–`UI-010` cross-cutting libraries approved | `CG-008` DoD ticked |
| `PG-03` | Bengali bundle complete and **signed off in context** (`BN-018`) | Sign-off record; `CM-R6` |
| `PG-04` | `common.*` namespace Bengali-complete | `BN-019` |
| `PG-05` | Every user-visible error states cause and remedy in the user's language (`PS-09`, `BR-STD-04`) | `UI-004` + `BN` bundle diff = zero unpaired strings |
| `PG-06` | `HC` help set published and searchable | Help IA live |
| `PG-07` | `NT` templates approved; WhatsApp templates **pre-approved by Meta** | `NT-026` change log |
| `PG-08` | Binding terms approved by named counsel and acceptance capture live | `LG-001` ledger |
| `PG-09` | `TR` pack delivered to the operating population | `TR-002` completion record |
| `PG-10` | `EO` onboarding kit issued (external portals) | `EO-*` |
| `PG-11` | `TS-011` portal scripts and `TS-016` accessibility executed and signed | Test evidence |
| `PG-12` | `OP-003` macros and `OP-005` status content live | Support readiness |
| `PG-13` | `DT` documents the portal issues render correctly (G3) | Rendered output verified |
| `PG-14` | `IP-09` manual fallback documented for every `P0` integration the portal uses | `OP-014` |
| `PG-15` | Data leaving to any counterparty is registered field-by-field with a lawful ground | `AP-012` |

**On the enumeration date, no portal satisfies `PG-01`**, because no content file is `Approved`.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `04-00` and the twelve `P*` specifications | Portal definition, audience, wave, KPI targets |
| `CG-010` §3.2 | Which content is bilingual |
| `BN-018` | In-context linguistic sign-off, required by `PG-03` |
| `CG-007` | The gate model behind `PG-01`, `PG-08` |
| `RF-003`, `RF-004` | Traceability model and verdict scheme |
| Category audits | Every blocker named in §4.4 |

| Depended on by | Why |
|---|---|
| Portal go-live decisions | `PG-01`–`PG-15` |
| `RF-007` | Receives the gaps as backlog |
| `RF-011` | Receives the launch risks |
| `CM-005`, `CM-006` | Wave launch and go-live kits |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary**, and 60 days before any portal go-live |
| Regeneration rule | §4.3 and §4.4 counts **regenerated by extraction from `traces_to:`** (`CP-11`, `CM-R2`) |
| **`AF-01` independence** | This map is maintained **by identifier (`Pnn`)**, never by filesystem path. It therefore does **not** depend on the resolution of `AF-01`, correcting `AUDIT-001`'s assessment that it could not be maintained mechanically until the portal files move |
| Trigger for out-of-cycle review | A portal wave change; a Bengali sign-off completed; a blocker closed; a new portal |
| Owner | Programme Content Lead |
| Escalation | A portal within 60 days of go-live at `BLOCKED` goes to the Steering Committee |

---

## Approval Record

| Gate | Required for Class E | Reviewer | Status |
|---|:--:|---|---|
| G1 Editorial | ● | Content Design | Not started |
| G2 Factual | ● | Content Design Lead with each Portal Owner | Not started |
| G3–G6 | ○ | — | Not required |
| Final approver | — | Programme Content Lead | **Unappointed** |

---

## Open Items

| # | Item | Owner | Blocks |
|---|---|---|---|
| `RF-005-OI-01` | **`common.*` — 154 shared strings on all twelve portals have no Bengali owner.** `BN-019` unregistered | Localisation Lead | `PS-03` on every portal; `P02` non-negotiable #3 |
| `RF-005-OI-02` | **No portal is content-ready; three are `BLOCKED`** | Portal owners | Every go-live |
| `RF-005-OI-03` | **`PC-01` — Master Index §5 column not yet renamed** | Programme Content Lead | Continued misreading |
| `RF-005-OI-04` | **`DT-031` maps nine non-existent `MD-028` fields** | Service Ops with Legal | `P04` service credits |
| `RF-005-OI-05` | **`P07` statutory settlement and complaint obligations unmet; no compliance officer named** | CEO with Legal | Marketplace launch |
| `RF-005-OI-06` | **`KB` corpus unwritten — 775–1,545 specialist hours unresourced** | Knowledge Manager | `P02`, `P03`, `P11` |
| `RF-005-OI-07` | **`TS-015`, `TS-016` unexecutable — no field logistics, no accessibility reviewer** | QA Lead | `PG-11` on five portals |
| `RF-005-OI-08` | **No Programme Content Lead appointed** | CEO | Final approval |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; register table and maintenance procedure added per `CG-009` §3
- [x] All **twelve** portals mapped, none omitted
- [x] Counts produced by extraction with a stated enumeration instant (`CP-11`, `RG-06`)
- [x] Master Index §5 discrepancy reported and reconciled, not silently replaced (`PC-01`)
- [x] Required-content-set definition stated before verdicts applied (§4.2)
- [x] Bengali completeness assessed against `PS-03` and the `P02` non-negotiable (§4.5)
- [x] Operative launch checklist `PG-01`–`PG-15` provided
- [x] Maintenance made independent of `AF-01`
- [x] All internal links resolve
- [x] Bengali counterpart — n/a (`bilingual: no`, `CG-010` §3.2)
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] **`RF-005-OI-01` `common.*` Bengali owner registered** — outstanding
- [ ] **Named approver recorded** — outstanding, `RF-005-OI-08`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
