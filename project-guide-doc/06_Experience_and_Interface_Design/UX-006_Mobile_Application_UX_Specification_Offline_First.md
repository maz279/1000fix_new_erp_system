---
id: UX-006
title: Mobile Application UX Specification (Offline-First)
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
  WCAG 2.2 Level AA via W3C WCAG2ICT (Group Note, WCAG 2.2 edition, 11 December 2025) ·
  ISO 9241-210:2019 §5.4 context of use · ISO 9241-11:2018 (usability in context) ·
  ISO 9241-920:2009 (tactile and haptic interaction) · AR-010 command-journal model
traces_to: >
  PGD-000 UX-006 · AR-010 §6 (conflict disclosure — "the layout is UX-006's") · AR-010 Q-02 (blocking) ·
  P02 non-negotiables 1–7 · NFR-036, NFR-037, NFR-047, NFR-074, NFR-082 ·
  URD §20 (offline UX), §21.3 (situational accessibility) · UI-009 · UI-012, UI-019, UI-021 ·
  APP-01, APP-02, APP-03, APP-04
depends_on: AR-010 (the sync architecture this designs) · UX-001 (C-62, C-63, C-67 and field tokens) · UX-002 §6.4 (tab model) · UX-004 (interaction) · UX-005 (WCAG2ICT scope) · UX-007 (Bengali)
verified_on: 2026-08-18
priority: P0
needed_by: W2
enumeration_timestamp: 2026-08-18 14:45 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# UX-006 — Mobile Application UX Specification (Offline-First)

### Category 06 · Code `UX` · Realises `AR-010` §6 · Closes `AR-010` `Q-02`

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `UX-006` exists in `PGD-000` Category 06.
> 2. **`PG-03` Count, do not consult.** Counted at **2026-08-18 14:45 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-18`.

---

## 1. Purpose

`AR-010` §6.3 ends with a sentence that names this document as a blocker:

> *"**Content is `UI-009`'s** (written); **the states are this document's** (specified here); **the
> layout is `UX-006`'s** (not yet designed). All three must exist before APP-01 ships."*

and raises it formally as `AR-010` `Q-02`: *"`UX-006` (Mobile UX Specification) is ⛔ **not
written**. §6's states need a design before APP-01 ships in W2."*

**This document is that design.** It specifies how a technician, a rider and a field auditor
perceive and act on the sync state model `AR-010` defines, under the conditions they actually work
in — one hand, direct sunlight, gloves, rain, a helmet, a 3 GB Android device, a 3G connection that
comes and goes, and up to 24 hours with no connection at all.

It also closes a contradiction the estate has been carrying: `UI-009` offers the user a conflict
choice that `AR-010`'s server-authoritative matrix forbids (§8.3).

It unblocks APP-01 (`P02`, W2), APP-02 (`P09`, W3), APP-03 (`P11`, W5) and APP-04 (`P01` app, W6),
and the `AR-010` §10 offline test harness, which asserts behaviour that must first be specified.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The four Flutter applications — APP-01 `P02`, APP-02 `P09`, APP-03 `P11`, APP-04 `P01` app |
| 2 | The **field context of use** and the physical design consequences |
| 3 | The **sync state model as experienced** — the two-indicator rule, queue, last sync, failure |
| 4 | The offline capability matrix — what works offline, and how a user knows |
| 5 | Capture patterns: photograph, scan, voice, signature, measurement |
| 6 | **Conflict disclosure design** — the layout `AR-010` §6.3 requires |
| 7 | Battery and data discipline as user-visible behaviour |
| 8 | Safety and custody screens |
| 9 | Degraded-service behaviour: map, GPS, payment, notification |
| 10 | Session, device loss and the security asymmetry |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| The sync protocol, journal, conflict authority | `AR-010` | This document designs how it is perceived, not how it works |
| The copy | `UI-009`, `UI-012`, `UI-019`, `UI-021`, `BN-010` | Content. §8.3 raises one correction |
| Component definitions `C-62`, `C-63`, `C-67` | `UX-001` §8.7 | A component is not a screen |
| Screen enumeration | `UX-003` §5.4 — 36 bespoke screens across the three field apps | Inventory |
| Bengali metrics | `VB-009`, `UX-007` | This document applies the field floors |
| The `P01` **web** PWA degraded mode | `AR-001` §9.4, §10 here | Different problem: cached read, not offline write |
| Device management, MDM, enrolment | `PE-*`, `SC-004` | Infrastructure |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Mobile designers and engineers | The specification APP-01…APP-04 are built to |
| `AR-010` owner | The realisation that closes `Q-02` |
| QA | The behaviours the offline harness asserts |
| Field operations, dispatch, logistics | What their teams will see and be able to do |
| Accessibility reviewer | The WCAG2ICT surface set (`UX-005` §4.2) |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this conforms | Departure |
|---|---|---|---|
| **W3C WCAG 2.2 AA via WCAG2ICT** (Group Note, 2.2 edition, 11 Dec 2025) | 55 A+AA criteria as reinterpreted for non-web software | `UX-005` §4.3; every rule here that carries an accessibility consequence names its criterion | 2.4.5 Multiple Ways does not apply within a single application |
| **ISO 9241-210:2019** | §5.4 understand and specify the context of use | §3 is a context-of-use specification, not a persona summary. It is the input every other section derives from | None |
| **ISO 9241-11:2018** | Usability as effectiveness, efficiency and satisfaction **in a context** | The context is §3; the measures are `UX-008` §6 | None |
| ISO 9241-920:2009 | Tactile and haptic interaction | §7.2 haptic confirmation rules | Supporting guidance only |
| `AR-010` | §3–§11 | This document is its user-facing realisation and does not alter it | None. Where `UI-009` conflicts with `AR-010`, `AR-010` governs (§8.3) |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `AR-010` §5.3, §5.4, §6, §8, §9, §11 | The authority matrix, the four resolution outcomes, the two-state disclosure rule, evidence handling, ten failure modes, the security asymmetry |
| `04-00` §P02 | Seven non-negotiable requirements, including 24 h offline, 30 s sync, complete Bengali, mid-range Android 11 / 3 GB, ≤ 12% battery per 8-hour shift |
| `04-00` §P09, §P11 | Rider and auditor capability sets |
| `URD` §20 | The offline contract, what must always be visible, conflict discipline, data scope and battery |
| `URD` §21.3 | Situational accessibility — personas `A-02`, `A-03`, `A-04` |
| `UI-009` | Offline, sync and conflict copy — **and the contradiction at §3.3** |
| `UI-012`, `UI-019`, `UI-021` | `P02`, `P09`, `P11` copy packs |
| `VB-009` §3 | Field type floors: 17 px body, **19 px safety and custody** |
| `VB-003` §6 | Brand is **excluded** from the `P02` job flow and the `P09` rider app |
| `TS-015` | Offline and field-condition test scripts |

### 2.3 Findings this document addresses

| Finding | Source | How addressed |
|---|---|---|
| **`AR-010` `Q-02`** | `AR-010` §12 | **Closed.** §5–§8 are the design `AR-010` §6 requires |
| Register row `UX-006` ⛔ | `PGD-000` | Authored |
| `PGD-A3` residual — `UX-006` blocks APP-01 | `02` `_CATEGORY_OVERVIEW` §6 | Closed by issue |
| `UXA-10` | `UX-004` §5.8 | §8.3 rules the `UI-009` conflict-choice contradiction and specifies the replacement |
| `UXA-12` | `UX-005` §4.1 | The three apps are in accessibility scope; every rule here names its criterion |
| **New — `UXA-13`** | This category | `UI-009` `common.offline.limit_warning` warns at an unstated threshold and `AR-010` `F-09` says work continues past 24 h. §5.5 fixes the thresholds so copy and architecture agree |
| **New — `UXA-14`** | This category | **No specification anywhere states what a field user sees when the local store is full** (`AR-010` `F-04` blocks evidence capture). §7.6 |

---

# 3. Context of Use

**ISO 9241-210 §5.4 requires this before design, and the estate has never written it down.** Every
rule in this document derives from a row here.

## 3.1 The four applications

| App | Surface | Users | Wave | Offline | Reference device |
|---|---|---|:--:|---|---|
| **APP-01** | `P02` Technician | 200–400 field & workshop technicians | **W2** | **24 h full** | Mid-range Android 11, 3 GB RAM |
| **APP-02** | `P09` Rider | 50–200 riders and courier staff | W3 | **24 h full** | Same, often older |
| **APP-03** | `P11` Field auditor | 20–60 auditors and branch managers | W5 | **24 h full** | Same or better |
| **APP-04** | `P01` Customer app | Individual customers | W6 | **Cached read only** | Anything from 2 GB upward |

## 3.2 The physical context

| Dimension | Technician (`A-02`) | Rider (`A-03`) | Auditor |
|---|---|---|---|
| Hands free | **One, usually** | **Rarely both** | Often one (clipboard replaced) |
| Light | Direct sunlight to dark cupboard | Direct sunlight, headlights, dusk | Warehouse, workshop, branch |
| Weather | Rain, heat, humidity | **Rain, wind, in motion** | Indoor |
| Gloves | Often | **Usually** | Sometimes |
| Head protection | No | **Helmet** | No |
| Noise | Street, workshop | Traffic | Workshop |
| Posture | Crouched, standing, kneeling | Astride, standing at a door | Standing, walking |
| Session length | 8-hour shift | 8–10 hour shift | 4–6 hours |
| Connectivity | Urban 3G/4G; **basements, lifts, rural sites** | Street-level, moving between cells | Warehouse interiors |
| Time pressure | Customer present and waiting | **Customer at the door** | Moderate |
| Consequence of error | Wrong part, lost evidence, unbilled work | **Custody break** | Invalid audit |

## 3.3 The seven non-negotiables and their design consequence

`04-00` §P02 states seven. Each has a design consequence this document must satisfy — stated
explicitly, because a requirement without a design consequence is not implemented.

| # | Non-negotiable | Design consequence |
|---:|---|---|
| 1 | Full operation offline for 24 h, no data loss | §6 offline capability matrix; every screen has an offline state (`SIR-16`) |
| 2 | Sync within 30 s of reconnection, 100% integrity | §5.4 sync progress design; `NFR-037` |
| 3 | **Bengali UI, complete, including error messages** | `UX-007`; field type floors §4.2; **no English fallback string ever renders** |
| 4 | Mid-range Android 11, 3 GB RAM | §9.1 performance budget; no idle animation; no large in-memory lists |
| 5 | **Battery ≤ 12% per 8-hour shift excluding navigation** | §9 — battery is a design constraint, not an engineering one |
| 6 | Every state-changing action queued locally and idempotent | §5 the two-indicator rule; `AR-010` §3 |
| 7 | **No feature requires a connection a technician cannot complete offline** | §6.2 — a connection-required action is a design defect, verified feature-by-feature at Gate 2 |

---

# 4. Physical Design

## 4.1 Reach and target size

| # | Rule | Basis |
|---|---|---|
| `MOB-01` | **Every primary action sits in the bottom third of the screen**, thumb-reachable one-handed | `URD` §19.3, `A-02` |
| `MOB-02` | Destructive and irreversible actions sit **outside** the natural thumb arc — deliberately harder to reach | `IXN-08` |
| `MOB-03` | Target size is **`size.target.field` = 56 px** on `P02` and `P09`; 44 px on `P11` and APP-04; **never below the 24 px WCAG floor anywhere** | SC 2.5.8, `UX-001` §5.6 |
| `MOB-04` | Adjacent targets are separated by **≥ 12 px**. A gloved fingertip contact patch is ~20 mm; two 56 px targets touching are one target |
| `MOB-05` | **≤ 4 tabs**, 3 on `P09` | `UX-002` `NVR-29`, `NVR-33` |
| `MOB-06` | Every primary flow is completable **one-handed, in portrait**. Landscape is supported, never required | `URD` §19.3, SC 1.3.4 |
| `MOB-07` | No two-handed gesture, no pinch-to-act, no multi-finger action | SC 2.5.1, `IXN-17` |
| `MOB-08` | **No device-motion actuation** — no shake, no tilt. A rider triggers them accidentally | **SC 2.5.4**, `IXN-20` |

## 4.2 Legibility

| # | Rule | Basis |
|---|---|---|
| `MOB-09` | Body type is **`type.field.body`** — 17 px English, **17 px Bengali** (the Bengali floor for these surfaces) | `VB-009` §3 |
| `MOB-10` | **Safety and custody content is `type.field.safety` — 19 px, weight 600 — and is never compressed to fit.** Where it does not fit, the content is shortened or the screen is split; the type is not reduced | `VB-009` MS-04 |
| `MOB-11` | Weight is never below 400; thin weights vanish in sunlight and lose Bengali conjunct strokes | `VB-009` TF-07 |
| `MOB-12` | **`high-contrast` theme is the sunlight mode** and is one action from any screen — not buried in settings | `THM-02`, `URD` §21.3 |
| `MOB-13` | Contrast on field surfaces **exceeds** the 4.5:1 minimum; the `high-contrast` theme targets ≥ 7:1 | SC 1.4.3, `THM-02` |
| `MOB-14` | Brand colour does not appear in the `P02` job flow or anywhere in `P09` beyond a 24 px header mark | `VB-003` §6, LG-07 |
| `MOB-15` | Bengali is verified at rank 1 (Hind Siliguri, bundled) **and** rank 2 (Noto Sans Bengali, the Android default) on the reference device | `VB-009` MM-04, TF-02 |
| `MOB-16` | Platform text scaling to **200%** must not break any screen | SC 1.4.4, `ACD-04` |

## 4.3 Environmental

| # | Rule |
|---|---|
| `MOB-17` | Every confirmation is **visual + haptic**; audible where the platform allows. In traffic or a workshop, one channel is insufficient |
| `MOB-18` | Nothing depends on hearing (SC 1.4.2) or on colour (SC 1.4.1) |
| `MOB-19` | The app is usable with the screen at **minimum brightness** (battery preservation) and at maximum (sunlight) |
| `MOB-20` | No interaction requires precision below 56 px or a sustained press beyond 500 ms |
| `MOB-21` | **Screen wake is held during an active capture sequence** and released immediately after — a screen that sleeps mid-signature loses the signature |

---

# 5. The Sync State Model — as experienced

## 5.1 The two-indicator rule

`AR-010` §6.1 calls this *"the single most important UX decision in the offline design."* It is
therefore stated first and designed most carefully.

> **`MOB-22`.** **"Saved on this device" and "Sent to the office" are two visually distinct
> indicators. They are never merged, never abbreviated to one, and never rendered in the same
> shape or colour.**

| State | Meaning | Indicator | Token |
|---|---|---|---|
| **Saved on this device** | In the local journal. Survives app kill, battery death, reboot | **Filled circle with a downward tick**, `status-progress` | `sync.local.saved` |
| **Sent to the office** | Server has acknowledged | **Filled circle with an upward arrow**, `status-success` | `sync.remote.ack` |
| Sending | In flight | Same shape as *sent*, **outlined not filled**, `status-info` | `sync.remote.pending` |
| Not sent — retrying | Failed, will retry | *Sent* shape with a retry glyph, `status-warning` | `sync.remote.retry` |
| Not sent — needs help | Quarantined after 3 attempts (`AR-010` `F-06`) | *Sent* shape struck through, `status-error` | `sync.remote.blocked` |

| # | Rule | Basis |
|---|---|---|
| `MOB-23` | The two indicators use **different glyph shapes**, not two colours of the same glyph, so they survive greyscale, sunlight and colour-blind vision | SC 1.4.1, `VB-008` TS-02 |
| `MOB-24` | Each carries a **text label** in Bengali. Colour + glyph + label, always all three | `VB-008` §2 |
| `MOB-25` | The indicators appear **at the record level and in the persistent status bar** — a technician must be able to answer "is this job safe?" without navigating |
| `MOB-26` | **"Saved on this device" appears within 100 ms of the action.** The reassurance is the point; a delayed reassurance is not one | `IXN-04` |

> **Why this rule carries the whole design.** `AR-010` §6.1: *"A technician who cannot tell the
> difference has no way to know whether four hours of work is safe, and the rational response to
> that uncertainty is to write it on paper as well — which is the failure mode the whole programme
> is trying to end."*

## 5.2 The persistent status bar — `C-62`

Present on **every screen** of APP-01, APP-02 and APP-03. It replaces the global chrome
(`UX-002` `NVR-18`) and is never collapsed, hidden or scrolled away.

| Element | Always visible | Content | Basis |
|---|:--:|---|---|
| Connectivity | ● | Online / Offline, with the duration when offline | `URD` §20.2 |
| **Queue depth** | ● | Count of unsent items, **tappable to see what they are** | `URD` §20.2, `AR-010` §6.2 |
| **Last successful sync** | ● | Relative time — "12 minutes ago" | `AR-010` §6.2 |
| Sync in progress | when active | "Syncing 7 of 23" | `UI-009` `common.sync.progress` |
| Failure + action | when present | What failed and **what to do** | `NFR-078` |

| # | Rule |
|---|---|
| `MOB-27` | The bar occupies **≤ 44 px** and never pushes primary content below the fold |
| `MOB-28` | **Tapping the queue depth opens the queue detail** (§5.3). A count nobody can inspect is a number, not information |
| `MOB-29` | The bar is announced to assistive technology as a live region, `polite` (SC 4.1.3) |
| `MOB-30` | The bar **never shows a spinner alone**. Every state has a label |

## 5.3 The queue detail screen

One of the 16 bespoke `P02` screens (`UX-003` §5.4). It answers one question: **what of my work is
not yet at the office, and what should I do about it?**

| Section | Contents |
|---|---|
| Summary | *n* items waiting · oldest *t* · estimated sync time at current connection |
| **Per item** | What it was (job reference, action, timestamp), its state (§5.1), and — for blocked items — the reason and the next action |
| Blocked items | **First**, not buried. These are the ones that need a human |
| Evidence | Photographs and voice notes pending upload, with size and whether upload is deferred to Wi-Fi (`AR-010` §8) |
| Action | "Try now" — a manual sync attempt, always available |

| # | Rule |
|---|---|
| `MOB-31` | An item is described by **what the technician did**, never by a command name: "Recorded diagnosis on SR-2026-114882", not `record_diagnosis` |
| `MOB-32` | A blocked item states the reason in plain Bengali and offers an action — `UI-009` `common.sync.failed_help` gives a phone number, which is correct as a last resort and **must not be the first resort** |
| `MOB-33` | The queue is **never presented as an error state**. It is the normal condition of offline work |
| `MOB-34` | Evidence pending upload is shown separately from state commands, because `AR-010` §8 makes evidence deliberately non-urgent. **A technician must not think their job is unsent because a photograph is** |

## 5.4 Sync in progress

| Phase | Duration target | What the user sees |
|---|---|---|
| Reconnection detected | — | Bar changes to online; "Back online. Syncing *n* items" |
| Commands sending | **≤ 30 s after 24 h offline on 3G** (`NFR-037`) | Determinate progress, count-based |
| Commands acknowledged | — | Queue visibly empties, item by item |
| Conflicts resolved | — | §8 disclosure, **after** sync completes, batched |
| Evidence uploading | Deferred | Separate, low-priority, resumable indicator (`AR-010` §8) |

| # | Rule |
|---|---|
| `MOB-35` | **The queue empties visibly.** Watching the count fall is the confirmation; a single "done" message is weaker |
| `MOB-36` | Sync **never blocks the interface**. A technician continues working during sync |
| `MOB-37` | Conflicts are disclosed **after** the batch completes, together, not one interruption per conflict |
| `MOB-38` | Evidence upload progress is visible but **never presented as incomplete work** — the state is already at the office (`AR-010` §8) |

## 5.5 Duration thresholds — `UXA-13`

`UI-009` provides `common.offline.limit_warning` — *"{hours} hours offline. Sync soon to be safe"* —
without stating when it fires. `AR-010` `F-09` states that beyond 24 h *"work continues; sync time
is no longer guaranteed."* **Copy and architecture must agree on the numbers.**

> **Ruling.** The thresholds are:

| Offline duration | Behaviour | Copy |
|---|---|---|
| 0–4 h | Normal. Bar shows offline and queue depth | `common.offline.banner` |
| **4 h** | Bar shows elapsed hours and item count | `common.offline.banner_long` |
| **18 h** | **First warning** — sync recommended; the 24 h guarantee is approaching | `common.offline.limit_warning` |
| **24 h** | Guarantee reached. Warning escalates; **work continues, nothing is blocked** | needs new key — `Q-05` |
| **> 24 h** | Continues. Sync time no longer guaranteed; the user is told the queue is unusually large (`AR-010` `F-09`) | needs new key — `Q-05` |
| Storage pressure | §7.6 | needs new keys — `UXA-14` |

| # | Rule |
|---|---|
| `MOB-39` | **Nothing is ever blocked because of offline duration.** The 24 h figure is a sync-performance guarantee, not a permission window |
| `MOB-40` | The warning is informative and calm. A technician in a rural area for two days has done nothing wrong |

---

# 6. Offline Capability

## 6.1 The matrix

Applies `AR-010` §7.1's scope model to what a user can do.

| Capability | `P02` | `P09` | `P11` | APP-04 | Offline behaviour |
|---|:--:|:--:|:--:|:--:|---|
| View assigned work | ● | ● | ● | ● read | From the local store; scope is today + 2 days (`AR-010` §7.1) |
| Accept / decline a job | ● | ● | ● | — | Queued command |
| Navigate to a site | ◐ | ◐ | — | — | Cached map tiles for the assigned area; see §10.1 |
| Record diagnosis, notes | ● | — | ● | — | Client-authoritative (`AR-010` §5.3) |
| Consume a part | ● | — | — | — | Against van stock; **may be rejected on sync** (invariant I-31) — §8.4 |
| Capture evidence | ● | ● | ● | — | Local encrypted store; deferred upload |
| Present and approve an estimate | ● | — | — | — | Price snapshot; **server may have changed it** — §8.4 |
| Capture a signature | ● | ● | ● | — | Local |
| Collect payment | ◐ | ◐ | — | — | **Cash only offline.** Digital payment requires a connection — §10.3 |
| Complete a job / QC | ● | — | ● | — | Queued |
| Scan a barcode / IMEI | ● | ● | ● | — | Against local reference data; staleness shown (`SIR-17`) |
| Read knowledge / manuals | ● | — | ● | — | Bundled for assigned device models |
| Message dispatch | ◐ | ◐ | ◐ | — | Queued; **the user is told it has not been delivered** |
| Book a service | — | — | — | ○ | APP-04 is cached-read; booking requires a connection |
| Raise a safety alert | ● | ● | ● | — | **Queued and additionally attempted over SMS** — §11.2 |

● full · ◐ partial, with a stated limitation · ○ not available offline

| # | Rule |
|---|---|
| `MOB-41` | **A capability marked ● must never show a connection-required message.** That is non-negotiable #7 and it is verified feature-by-feature at Gate 2 |
| `MOB-42` | A capability marked ◐ or ○ **says so before the user starts**, not after they have entered data | `UI-009` `common.offline.blocked` |
| `MOB-43` | An unavailable action is **visible and explained**, never hidden. Hiding it makes the user think the feature does not exist | `VB-006` BT-05 |
| `MOB-44` | Messaging that is queued rather than delivered is shown as queued. A technician who believes dispatch has read their message and acts accordingly is a safety issue |

## 6.2 Stale reference data

| # | Rule | Basis |
|---|---|---|
| `MOB-45` | Any screen showing cached reference data — price list, part catalogue, stock, entitlement, fault codes — shows **its age** and a refresh affordance | `URD` §20.2, `SIR-17` |
| `MOB-46` | Age is shown in **relative, plain terms**: "Prices from this morning", not a timestamp |
| `MOB-47` | Where staleness could change a commercial outcome — a price shown to a customer — the screen says so **before** the number is presented, not in a footnote |
| `MOB-48` | Reference data older than **48 h** is marked prominently; older than **7 days**, the screen recommends syncing before quoting |

---

# 7. Capture Patterns

## 7.1 Photograph and video — `C-67`

| # | Rule | Basis |
|---|---|---|
| `MOB-49` | Every capture records **GPS, timestamp and the capturing user** automatically, and shows that it has | `04-00` §P02 |
| `MOB-50` | **Quality is validated at capture, not after upload.** Blur, darkness and framing are checked on device; a rejected photograph is retaken while the device is still in front of the technician | `URD` §20.4 |
| `MOB-51` | Compression happens on device to a declared quality floor; originals are retained until acknowledged | `AR-010` §8 |
| `MOB-52` | Required evidence sets — before/after, serial plate, damage — are shown as a **checklist with thumbnails**, so a missing item is visible before the job is closed |
| `MOB-53` | Capture works with **one hand and gloves**: a full-width shutter target in the bottom third, no pinch-to-zoom requirement | `MOB-01`, `MOB-07` |
| `MOB-54` | Evidence upload state is **separate** from job state and never blocks job completion | `AR-010` §8, `MOB-34` |

## 7.2 Scanning

| # | Rule | Basis |
|---|---|---|
| `MOB-55` | Scan-first, type-fallback, everywhere a scan is possible | `IXN-63` |
| `MOB-56` | The scanner is armed on entry to any scan-primary screen; **no tap to focus a field first** | `IXN-64` |
| `MOB-57` | Success gives **haptic + visual + audible** confirmation | `IXN-65`, ISO 9241-920 |
| `MOB-58` | A non-matching scan is a designed state: what was scanned, what was expected, manual entry offered | `IXN-66` |
| `MOB-59` | Multi-item verification against a manifest shows a **running tally with unscanned items always visible** — this is the rider's custody control | `IXN-67` |
| `MOB-60` | Scanning works against local reference data and shows staleness (`MOB-45`) | `IXN-68` |

## 7.3 Signature and OTP — custody

| # | Rule | Basis |
|---|---|---|
| `MOB-61` | The signature surface is **full-width, in the bottom half**, and holds screen wake (`MOB-21`) |
| `MOB-62` | What is being signed is stated **above** the signature area in `type.field.safety` (19 px) — the customer must be able to read it | `MOB-10` |
| `MOB-63` | Signature and OTP are captured **offline**, bound to the consignment and the timestamp | `AR-010` §5.3 |
| `MOB-64` | A custody handover is **not complete until both parties' identity is recorded**. The screen does not allow a partial handover to be marked complete | `04-00` §P09 |
| `MOB-65` | Custody screens carry no brand colour, no decoration and no secondary action. **One task, one screen** | `VB-003` §6 |

## 7.4 Voice

| # | Rule | Basis |
|---|---|---|
| `MOB-66` | Bengali voice-to-text wherever free text is captured; **the audio is retained in addition to any transcript** | `NFR-074`, `IXN-72` |
| `MOB-67` | Transcription is **reviewable and editable before commit** | `IXN-71` |
| `MOB-68` | Voice is never required (`IXN-74`) — customer privacy, noise, and a rider in a helmet |
| `MOB-69` | Where offline transcription is unavailable, the audio is captured and queued, and the screen says the transcript will follow | `Q-04` |

## 7.5 Measurement and checklist

| # | Rule |
|---|---|
| `MOB-70` | Checklist answers are client-authoritative (`AR-010` §5.3) and never lost to a conflict |
| `MOB-71` | A QC checklist enforces its blocking items **on device**, using the rules bundled with the job — the technician learns the block at the bench, not on sync |
| `MOB-72` | Numeric readings use a numeric keypad, `type.numeric`, and Arabic digits in both locales (`BN-007` §3.3) |

## 7.6 Storage pressure — `UXA-14`

`AR-010` `F-04` specifies the behaviour: *prune read cache → warn → block new evidence capture;
never prune the journal; escalate to supervisor.* **No document states what the user sees.**

| Stage | System behaviour (`AR-010` `F-04`) | What the user sees |
|---|---|---|
| Read cache pruned | Automatic | Nothing. Knowledge and manuals may need re-download; that is stated when opened |
| **Warning threshold** | Warn | Persistent banner: storage low, *n* evidence items pending, "Sync now to free space" |
| **Capture blocked** | New evidence capture blocked | **A screen, not a toast**: what is full, what is safe (the journal, always), what to do, and dispatch contact. Escalation to supervisor happens automatically and the user is told it has |
| Journal | **Never pruned** | The queue detail states explicitly that recorded work is safe |

| # | Rule |
|---|---|
| `MOB-73` | Blocked capture is the **worst moment in the application's life** — a technician standing at a device that needs photographing, unable to photograph it. The screen must be calm, must confirm that existing work is safe, and must offer the fallback (`Q-06`) |
| `MOB-74` | New copy keys are required for all three stages. Raised to `UI-009` under `CG-006` (`Q-05`) |

---

# 8. Conflict Disclosure

**This section is what `AR-010` §6.3 asks for.**

## 8.1 The principle

> `AR-010`: *"Any resolved conflict is shown to the user, with what changed and why. The system
> never silently picks a winner on something a technician entered by hand."*

## 8.2 The five elements

`AR-010` §6.3 requires five things be conveyed. This is their layout, in reading order:

| Order | Element | Rendering |
|---:|---|---|
| 1 | **What happened to their work** — first, before anything else | `type.field.safety` (19 px, weight 600): *"Your work has been saved to the job."* or the explicit rejection |
| 2 | **What changed** | The specific field or decision, with the old and new value side by side. Never "a conflict occurred" |
| 3 | **Who** | The actor's name where a person; the system where not |
| 4 | **When** | Timestamp in the technician's timezone, plus relative ("while you were offline") |
| 5 | **What to do next** | An action, or an explicit "nothing to do" |

| # | Rule |
|---|---|
| `MOB-75` | **Element 1 is first and largest.** The technician's question is "did I lose my work?" — every other element is secondary until that is answered |
| `MOB-76` | Element 2 shows **values**, not field names. "Assigned to: you → Mahbub", not "assignment changed" |
| `MOB-77` | Where nothing is required, the screen says so explicitly. A disclosure with no stated action reads as an unfinished task |
| `MOB-78` | Conflicts are **batched after sync** (`MOB-37`) and presented as a list with the same five elements per item |
| `MOB-79` | A disclosure is **dismissible but recoverable** — it remains in the job's history. A technician who dismisses it while riding must be able to find it later |

## 8.3 The ruling on `UI-009` — `UXA-10`

`UI-009` §3.3 provides `common.conflict.keep_mine` (*"Keep my version"*) and
`common.conflict.keep_theirs` (*"Keep {user}'s version"*). `AR-010` §5.3 makes assignment, pricing,
stock, state and entitlement **server-authoritative** and evidence, notes, timestamps and
measurements **client-retained**. **The system does not offer this choice.**

> **Ruling.** `AR-010` governs. The two keys are **withdrawn**.
>
> | `AR-010` outcome | What the user sees | Copy |
> |---|---|---|
> | **Applied** | Nothing. No conflict occurred | — |
> | **Applied with conflict** | The five-element disclosure. **Their data is preserved and attached** | `common.conflict.detected` + `common.conflict.both_kept`, reworded |
> | **Rejected** | What was rejected, the reason, and the offered alternative — e.g. a parts request when stock was consumed elsewhere | `common.sync.failed_help` is too blunt; needs a per-invariant key |
> | **Deferred** | Raised as a task for a supervisor. **This is the only case where a human decides, and it is not the technician** | `common.conflict.manual` — **already correct** |
>
> Raised as a content change under `CG-006`. `Q-05` tracks the replacement keys.

> **Why the choice must not be offered.** A technician shown "Keep my version" for an assignment the
> server has already reassigned would be given a choice the system will overrule. That is worse than
> no choice: it destroys trust in every subsequent message the application shows, including the ones
> that matter — and this application's entire value rests on the technician believing the sync
> indicator.

## 8.4 The two worked cases

**Case 1 — reassignment while offline** (`AR-010` §5.4).

> **Your work has been saved to the job.** *(19 px)*
>
> This job was reassigned to **Mahbub Rahman** at **10:55**, while you were offline.
> Your diagnosis, 6 photographs and time entries have been saved to the job and the office can see
> them.
>
> **Check with dispatch before travelling to your next stop.** → *Message dispatch*

**Case 2 — part consumed elsewhere** (`AR-010` §5.5, invariant I-31).

> **Your work has been saved. One item could not be applied.** *(19 px)*
>
> The part **SP-11402 · Display assembly** was used on another job at **14:12**.
> Your diagnosis, photographs and time are saved. The part consumption was not applied.
>
> **Request this part** → *(creates a parts request against this job)*

| # | Rule |
|---|---|
| `MOB-80` | Every rejection offers the **specific** next action, not a generic route to support |
| `MOB-81` | Both cases lead with the preserved work. Neither begins with the word "conflict" |

---

# 9. Battery and Data

`NFR-082`: **≤ 12% per 8-hour shift excluding navigation.** This is a design constraint. A design
that animates, polls and keeps GPS at full rate will breach it regardless of engineering quality.

## 9.1 Design rules

| # | Rule | Basis |
|---|---|---|
| `MOB-82` | **No animation runs while the screen is idle** | `IXN-99`, `MOT-03` |
| `MOB-83` | No decorative motion anywhere in the field applications |
| `MOB-84` | Location sampling is **adaptive** — high rate only during active navigation or an arrival check, low otherwise | `URD` §20.4 |
| `MOB-85` | Sync frequency is adaptive to connectivity quality and battery level; **the app never polls a dead network** |
| `MOB-86` | Evidence upload defers to **charging or Wi-Fi** where policy allows, and the user can override for an urgent item | `AR-010` §8 |
| `MOB-87` | Dark theme is the default on `P02` and `P09`, both for battery on OLED and for dusk legibility |
| `MOB-88` | No screen holds a wake lock except during an active capture sequence (`MOB-21`) |

## 9.2 Data cost is the user's cost

| # | Rule | Basis |
|---|---|---|
| `MOB-89` | **The technician's data allowance is a cost to them.** Uploads are compressed; non-critical uploads deferred | `URD` §20.4 |
| `MOB-90` | A settings screen shows data used this month by category, and offers Wi-Fi-only evidence upload |
| `MOB-91` | The app never downloads knowledge or map content on a metered connection without asking |

## 9.3 Made visible

| # | Rule |
|---|---|
| `MOB-92` | Battery and data behaviour are **visible in settings**, not silent. A technician who does not understand why the app used 400 MB will disable sync |
| `MOB-93` | Where the app defers an upload, it says why — "Waiting for Wi-Fi" — not merely "pending" |

---

# 10. Degraded Services

## 10.1 Map and navigation

| Condition | Behaviour |
|---|---|
| Map tiles unavailable | Cached tiles for the assigned area; beyond it, an address list with a phone-callable customer contact |
| Routing engine unavailable | Falls back to the self-hosted engine; then to a straight-line bearing and distance with the address |
| GPS unavailable | **Last known position with its timestamp**, clearly marked; manual status updates permitted | 
| Arrival detection unavailable | Manual "I have arrived" |

| # | Rule |
|---|---|
| `MOB-94` | A stale position is **never shown as current**. `URD` §20.5 requires the timestamp, and a rider's position is a custody-relevant fact |
| `MOB-95` | Navigation failure never blocks the job. The address and the phone number are always available |

## 10.2 Payment

| # | Rule |
|---|---|
| `MOB-96` | **Cash collection works fully offline** and is reconciled at end of shift |
| `MOB-97` | Digital payment requires a connection and **says so before the customer is asked to pay** — not after |
| `MOB-98` | Where digital payment is unavailable, the screen offers cash and a payment link to be sent on restoration (`URD` §20.5) |

## 10.3 Notification

| # | Rule |
|---|---|
| `MOB-99` | Push unavailable → in-app inbox on next sync. The fallback chain is `NT-001`'s; the app's obligation is to make the delay visible |
| `MOB-100` | A queued outbound message shows as queued, never as sent (`MOB-44`) |

## 10.4 APP-04 — the customer app boundary

APP-04 is **cached-read**, not offline-first (`AR-010` §1.1). Stating the boundary prevents a
capability being assumed.

| Capability | Offline |
|---|---|
| View existing services, devices, contracts, invoices | ● cached, with age shown |
| Track a service | ◐ last known status with its timestamp |
| Book a service | ○ **requires a connection** |
| Approve an estimate | ○ requires a connection |
| Pay | ○ requires a connection |

| # | Rule |
|---|---|
| `MOB-101` | APP-04 never queues a state change. A customer who believes they have booked and has not is a worse outcome than a clear "you need a connection" |

---

# 11. Session, Security and Safety

## 11.1 The security asymmetry

`AR-010` `SEC-07`: an offline session has a maximum life; beyond it the app requires
re-authentication to **submit** — but never to **view queued work or capture evidence**.

| # | Rule |
|---|---|
| `MOB-102` | An expired offline session **never blocks capture**. `AR-010`: *"A technician in a basement with an expired session must still be able to record what they did. Locking them out protects nothing — the work happens anyway, on paper — and loses the data"* |
| `MOB-103` | The expiry state is visible and explains exactly what is and is not available |
| `MOB-104` | Re-authentication accepts **biometric** where available and never requires a cognitive-function test | **SC 3.3.8** |
| `MOB-105` | Local data is encrypted and inert if extracted (`AR-010` `SEC-01`, `SEC-02`); the user is told the device is protected, once, at enrolment |

## 11.2 Safety

| # | Rule | Basis |
|---|---|---|
| `MOB-106` | The **panic / safety alert is reachable from every screen in two actions or fewer**, including offline and with an expired session | `04-00` §P02 |
| `MOB-107` | A safety alert is queued **and additionally attempted over SMS**, because it is the one message that must not wait for a data connection |
| `MOB-108` | Safety content renders at `type.field.safety` 19 px and is never truncated | `MOB-10` |
| `MOB-109` | The alert confirms **what was sent, to whom, and by which route** — a user who does not know whether help is coming will call anyway |

---

# 12. Verification

`AR-010` §10 defines the offline test harness. This section names the **user-facing** assertions it
must also carry, because a correct engine with an unusable disclosure still fails the field.

| # | Assertion | Method | Gate |
|---|---|---|---|
| `FV-01` | The two indicators are visually distinct in greyscale, in sunlight, and to a colour-blind user | Automated greyscale + manual field | Every mobile release |
| `FV-02` | "Saved on this device" appears within 100 ms of every state-changing action | Automated timing | Every build |
| `FV-03` | Queue depth, last sync and connectivity are visible on **every** screen | Automated screen sweep | Every build |
| `FV-04` | Every ● capability in §6.1 completes with the network off for 24 h | **`AR-010` harness** | Release blocker |
| `FV-05` | Every conflict outcome produces a disclosure carrying all five elements of §8.2 | Harness + manual | Release blocker |
| `FV-06` | **No `keep_mine` / `keep_theirs` choice is presented** | Automated string absence | Every build |
| `FV-07` | Battery ≤ 12% per 8-hour shift excluding navigation, on the reference device | Field measurement | Every mobile release |
| `FV-08` | All screens legible in direct sunlight with `high-contrast`, one-handed, with gloves | **Field testing in real conditions** | Every mobile release |
| `FV-09` | Bengali renders correctly at rank 1 and rank 2 on the reference device, at 100% and 200% scale | Device verification | Every mobile release |
| `FV-10` | Storage-full behaviour presents the §7.6 screen and never prunes the journal | Harness | Release blocker |
| `FV-11` | Safety alert reachable in ≤ 2 actions from every screen, offline, with an expired session | Automated + manual | Release blocker |
| `FV-12` | TalkBack in Bengali completes the `P02` job flow end to end | **Assisted-user test** | Per wave gate |

> **`FV-08` and `FV-12` cannot be automated and cannot be skipped.** `TS-015` covers the field
> condition scripts; `TS-016` covers assisted testing once `UX-005` `Q-01` is filled.

---

# 13. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `UX-006-D-01` | Sync-state disclosure | (a) one combined "synced" indicator; (b) **two distinct indicators** | **(b)** | `AR-010` §6.1 names this the single most important offline UX decision; a merged indicator recreates the paper-backup failure mode | Two glyphs, two labels, permanent screen cost of ≤ 44 px |
| `UX-006-D-02` | Conflict interaction (`UXA-10`) | (a) user chooses per `UI-009`; (b) **disclose the server-authoritative outcome** | **(b)** | Offering an overrulable choice destroys trust in the indicator the whole design rests on | Two `UI-009` keys withdrawn; replacements needed (`Q-05`) |
| `UX-006-D-03` | Offline duration limit | (a) block work past 24 h; (b) **never block; warn at 18 h** | **(b)** | 24 h is a sync-performance guarantee, not a permission window (`AR-010` `F-09`) | New copy keys for the > 24 h states |
| `UX-006-D-04` | Evidence versus state | (a) one queue; (b) **separate indicators** | **(b)** | `AR-010` §8 makes evidence deliberately non-urgent; merging them makes a synced job look unsynced | `C-62` carries two channels |
| `UX-006-D-05` | Default theme on `P02`/`P09` | (a) light; (b) **dark, with one-action high-contrast** | **(b)** | OLED battery against `NFR-082`, plus dusk legibility; sunlight is served by `high-contrast`, not by light theme | Every field screen designed in three themes |
| `UX-006-D-06` | APP-04 offline scope | (a) offline-first like APP-01; (b) **cached read** | **(b)** | A customer who believes they have booked and has not is worse than a clear connection message. `AR-010` §1.1 already scopes it this way | §10.4 boundary stated |
| `UX-006-D-07` | Expired session offline | (a) lock the app; (b) **capture permitted, submission blocked** | **(b)** | `AR-010` `SEC-07`. Locking loses the data and the work happens on paper anyway | Design must make the asymmetry legible (`MOB-103`) |

---

# 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Is the reference-device fleet — mid-range Android 11, 3 GB RAM — procured for design and QA? | Programme Manager | **W1** | `FV-07`, `FV-08`, `FV-09`, `PR-4` |
| `Q-02` | What is the actual measured battery draw of the specified location and sync behaviour? `NFR-082` has no instrument (`RQ-006` `Q-07`) | Mobile Lead | **W2** | `FV-07` |
| `Q-03` | How much map tile cache can be held within the storage budget, and for what radius? | Mobile Lead + `PE-*` | W2 | §10.1 |
| `Q-04` | Is Bengali voice-to-text available **offline** on the reference device? `NFR-074` requires it on mobile and `P02` runs 24 h offline | Mobile Lead | **W2** | §7.4, `MOB-69` |
| `Q-05` | Who writes the replacement `UI-009` keys — conflict outcomes, > 24 h offline, storage pressure? Approximately **9 new keys** | Content Design Lead | **W2** | `UXA-10`, `UXA-13`, `UXA-14` |
| `Q-06` | What is the fallback when evidence capture is blocked by storage? Camera roll with later import, or a hard stop? | Mobile Lead + Field Operations | W2 | `MOB-73` |
| `Q-07` | Does `P09`'s coordinator view need an offline mode? It is specified as web (`UX-002` `Q-02`) | Chief Architect | W3 | §6.1 scope |

---

# 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | **`AR-010` `Q-02` is closed** — §6's states have a design | §5, §8 |
| `AC-02` | A context-of-use specification exists per ISO 9241-210 §5.4 | §3 |
| `AC-03` | All seven `P02` non-negotiables have a named design consequence | §3.3 |
| `AC-04` | The two-indicator rule is specified to component and token level | §5.1, `C-62` |
| `AC-05` | An offline capability matrix exists per application and per capability | §6.1 |
| `AC-06` | Conflict disclosure carries all five `AR-010` §6.3 elements, with worked cases | §8.2, §8.4 |
| `AC-07` | The `UI-009` contradiction is ruled and the replacement specified | §8.3 |
| `AC-08` | Battery and data are treated as design constraints with named rules | §9 |
| `AC-09` | Every rule with an accessibility consequence names its WCAG 2.2 criterion | throughout |
| `AC-10` | Twelve user-facing verification assertions exist, with the non-automatable ones named | §12 |

**Definition of done.** Complete when every criterion is met, `Q-01` and `Q-05` are resolved, the
nine replacement copy keys exist, `AR-010` `Q-02` is formally closed in `AR-010`'s next revision,
and `PGD-000`'s `UX-006` row is updated with a fresh enumeration timestamp.

---

# 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`AR-010`** | The architecture this realises; `Q-02` closed |
| Upstream | `UX-001` `C-62`, `C-63`, `C-67`, `type.field.*`, `size.target.field` | Components and tokens |
| Upstream | `UX-002` §6.4 | Field tab model |
| Upstream | `UX-004` §5, §7 | Interaction and scanner contracts |
| Upstream | `UX-005` §4.2 | WCAG2ICT scope for the four apps |
| Upstream | `UX-007` | Bengali field floors and layout |
| Downstream | **APP-01, APP-02, APP-03, APP-04** | The build |
| Downstream | `TS-015`, `TS-016` | Field-condition and accessibility scripts |
| Downstream | `QA-003` | The `MV-*` assertions |
| Downstream | `CH-*` | Technician training describes these states |
| Lateral | `UI-009` | Copy; three corrections raised (§5.5, §7.6, §8.3) |
| Lateral | `UI-012`, `UI-019`, `UI-021` | Surface copy packs |

---

# 17. References

**Within this repository**
`../PGD-000_…` · `./_CATEGORY_OVERVIEW.md` · `./UX-001`…`./UX-005`, `./UX-007`, `./UX-008` ·
`../02_Architecture_and_Design/AR-010` · `../01_Requirements_Engineering/RQ-006`

**Workspace**
`../../1000fix_ERP_Module/04_Portals_and_Applications/04-00` §P02, §P09, §P11 ·
`../../project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-009` ·
`../../project_content/03_UI_Copy_and_Microcopy/03B_Portals/UI-012`, `UI-019`, `UI-021` ·
`../../project_content/01_Voice_Brand_and_Design_Content/VB-003` §6, `VB-009` §3 ·
`../../project_content/13_Test_and_Acceptance_Content/TS-015`, `TS-016` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_URD.md` §20, §21.3

**External standards and sources**

| Source | Verified |
|---|---|
| W3C — WCAG 2.2 (Recommendation) and **WCAG2ICT** (Group Note, WCAG 2.2 edition, 11 December 2025) | 2026-08-18 |
| ISO 9241-210:2019 §5.4 — understand and specify the context of use | 2026-08-18 |
| ISO 9241-11:2018 — usability: effectiveness, efficiency and satisfaction in a specified context of use | 2026-08-18 |
| ISO 9241-920:2009 — Guidance on tactile and haptic interaction | 2026-08-18 |

---

# 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Head of Product Design | Initial issue. **Closes `AR-010` `Q-02`**, the blocking dependency on APP-01. Specifies the two-indicator sync model, the persistent status bar, the offline capability matrix across four applications, and the five-element conflict disclosure with two worked cases. **Rules the `UI-009` conflict-choice contradiction** (`UXA-10`), fixes the offline duration thresholds copy and architecture disagreed on (`UXA-13`), and designs the storage-pressure states no document specified (`UXA-14`). Writes the estate's first ISO 9241-210 §5.4 context-of-use specification | *(pending — `PGD-A1-09`)* |

---

*`UX-006` · Category 06 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
