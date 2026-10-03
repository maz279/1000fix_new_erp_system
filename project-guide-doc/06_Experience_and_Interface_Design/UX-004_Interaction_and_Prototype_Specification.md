---
id: UX-004
title: Interaction & Prototype Specification
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
  WCAG 2.2 Level AA — SC 2.1.1, 2.1.4, 2.4.3, 2.4.11, 2.5.1, 2.5.2, 2.5.4, 2.5.7, 2.5.8, 3.3.7 ·
  W3C WAI-ARIA Authoring Practices Guide (APG) · ISO 9241-210:2019 §5.6 ·
  ISO 9241-161:2016 (widgets) · OMG BPMN 2.0 (flow basis via RQ-007)
traces_to: >
  PGD-000 UX-004 · URD §19.1, §19.4, §21.4 · NFR-001, NFR-032…NFR-041, NFR-079 ·
  UI-037…UI-042 (six critical flows) · RQ-007 BPM-001…BPM-034 · UX-003 §5.4 (130 bespoke screens) ·
  audit U-09 (drag-only dispatch board fails SC 2.5.7)
depends_on: UX-001 (motion and focus tokens) · UX-002 (navigation model) · UX-003 (screen inventory) · RQ-007 (process models)
verified_on: 2026-08-18
priority: P1
needed_by: W1
enumeration_timestamp: 2026-08-18 14:45 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# UX-004 — Interaction & Prototype Specification

### Category 06 · Code `UX` · WCAG 2.2 AA · W3C ARIA APG · ISO 9241-210:2019

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `UX-004` exists in `PGD-000` Category 06.
> 2. **`PG-03` Count, do not consult.** Counts taken from the filesystem at **2026-08-18 14:45 (+06)**.
>    **Zero of 621 demand-side files contains the word "prototype."**
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-18`.

---

## 1. Purpose

`UI-037`…`UI-042` write the **words** for booking, estimate approval, payment, registration, search
and consent. This document specifies **the interactions those words sit inside** — what a pointer,
a finger, a keyboard, a scanner and a screen reader can each do, what the system does back, and how
fast.

It exists because an interaction that is not specified is invented per surface, and because the
programme has one interaction defect already identified and unresolved: **the dispatch board is
specified as drag-and-drop, and drag-only fails WCAG 2.2 SC 2.5.7** (`URD` §21.4, audit `U-09`).
That is one known instance of a class — gesture-only, drag-only, hover-only and timing-dependent
interactions — that this document closes systematically rather than one finding at a time.

It unblocks the eight prototypes that must be evaluated before their screens are built
(`UX-008`), the keyboard specification the three high-volume roles depend on (`NFR-075`,
`NFR-076`), and the perceived-performance contract that turns `NFR-001`…`NFR-041` from server
metrics into something a user experiences.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | Input-modality contracts: pointer, touch, keyboard, scanner, voice, screen reader |
| 2 | The **gesture and drag rules**, and the SC 2.5.7 remediation for the dispatch board |
| 3 | Keyboard-first operation for intake, dispatch and finance |
| 4 | Selection, bulk action, inline edit, autosave, undo and reversibility |
| 5 | The **feedback and latency contract** — what the user sees at every performance threshold |
| 6 | Motion behaviour — what animates, why, and what never does |
| 7 | Redundant-entry elimination (SC 3.3.7) |
| 8 | The **eight prototypes**: scope, fidelity, method and evaluation gate |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Motion **tokens** (durations, easings) | `UX-001` §5.8 | Values, not behaviour |
| Screen layout and states | `UX-003` | Structure, not choreography |
| The copy in each flow | `UI-037`…`UI-042` | Content |
| Navigation structure and back behaviour | `UX-002` §9.2 | Wayfinding |
| Offline interaction specifics | `UX-006` | Field conditions have their own contract |
| Accessibility conformance evidence | `UX-005` | This document states the design; `UX-005` states the conformance claim |
| Business process semantics | `RQ-007` `BPM-*` | A flow's steps are a process model's; the interaction is this document's |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Designers | The interaction vocabulary and the prototype brief |
| Front-end and mobile engineers | The behaviour contract per component and per modality |
| QA | Assertable interaction rules and the keyboard test matrix |
| Accessibility reviewer | The SC 2.5.x remediation set |
| Business owners for intake, dispatch, finance | The keyboard commitments their throughput targets rest on |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this conforms | Departure |
|---|---|---|---|
| **WCAG 2.2 AA** | **2.5.7 Dragging Movements** | §5.3 requires a single-pointer alternative for every drag, including the dispatch board | None |
| | **2.5.8 Target Size (Minimum)** | 24 px floor; 44 px programme standard; 56 px field (`UX-001` §5.6) | Exceeds the AA minimum by policy |
| | 2.5.1 Pointer Gestures | §5.2 — no path-based or multipoint gesture is ever the only way | None |
| | 2.5.2 Pointer Cancellation | §5.1 — down-event never completes an action | None |
| | 2.5.4 Motion Actuation | §5.5 — device motion is never required | None |
| | 2.1.1 / 2.1.4 Keyboard, Character Key Shortcuts | §6 | Single-character shortcuts exist for intake/dispatch/finance and are **remappable and suppressible**, as 2.1.4 requires |
| | 2.4.3 Focus Order · 2.4.11 Focus Not Obscured | §6.4 | None |
| | **3.3.7 Redundant Entry** | §9 | None |
| **W3C WAI-ARIA Authoring Practices Guide** | Pattern set | Every composite widget in `UX-001` §8 implements its APG keyboard pattern | Departures listed per component in §6.5; currently **one** — the dispatch board, which has no APG pattern |
| ISO 9241-210:2019 | §5.6, §5.7 | Prototypes are produced and **evaluated** (§10.5), not demonstrated | None |
| ISO 9241-161:2016 | §8 | Widget behaviour vocabulary | None |
| OMG BPMN 2.0 via `RQ-007` | — | Prototype scope is aligned to `BPM-*` models so a prototype tests the modelled path | None |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `URD` §19.1 | Thirteen felt-performance thresholds, each with a named user consequence |
| `URD` §19.4 | Error handling and feedback commitments |
| `URD` §21.4 | The WCAG 2.2 recommendation and **the identification of 2.5.7 as "the one material gap"** |
| `UI-037`…`UI-042` | Copy for the six cross-cutting flows |
| `RQ-007` §4.2 | 30 process models; the flow-level truth the prototypes must honour |
| `UX-003` §5.4 | The 130 bespoke screens; §9 the fidelity ladder placing F3 |
| `04-00` §P03 | Keyboard-first for intake, dispatch and finance; ≤ 3 min intake; < 10 min morning dispatch |

### 2.3 Findings this document addresses

| Finding | Source | How addressed |
|---|---|---|
| `U-09` | `URD` §26 | §5.3 specifies the dispatch board's non-drag path; SC 2.5.7 becomes satisfiable |
| Register row `UX-004` ⬜ | `PGD-000` | The flows are specified |
| **New — `UXA-09`** | This category | **Zero files in the 621-file demand-side estate contain "prototype."** No interaction has ever been tested before being built. §10 |
| **New — `UXA-10`** | This category | `UI-009`'s conflict copy offers the user a choice (`keep_mine` / `keep_theirs`) that `AR-010` §5.3's server-authoritative matrix forbids. §5.8, and `UX-006` §8.3 rules it |

---

# 3. Interaction Principles

| # | Principle | Forbids | Test |
|---|---|---|---|
| `IXN-01` | **Every action has a keyboard path.** Not "most", not "the important ones" | Any pointer-only action | `IX-K1` keyboard traversal |
| `IXN-02` | **Every gesture has a visible button.** A swipe is an accelerator, never the only way | Swipe-to-delete with no delete button | `IX-G1` gesture parity |
| `IXN-03` | **Nothing commits on press-down.** Every action completes on release, over the target, and is cancellable by moving off it | `mousedown` handlers that mutate | SC 2.5.2, `IX-P1` |
| `IXN-04` | **The system answers within 100 ms, always** — even if the answer is "working". Silence reads as failure | Any interaction with no acknowledgement | `IX-F1` feedback latency |
| `IXN-05` | **Destructive is reversible or confirmed, never both absent.** Where the action permits undo, undo is offered instead of a dialog | A confirmation dialog on a reversible action; an irreversible action with no confirmation | `IX-D1` |
| `IXN-06` | **The user is never asked twice.** Anything the system already knows is pre-filled or selectable | Re-typing an address, a phone number, an IMEI | SC 3.3.7, `IX-R1` |
| `IXN-07` | **Hover reveals nothing that matters.** Touch surfaces have no hover; a hover-only affordance is invisible to half the estate | Tooltips carrying required information; hover-only row actions | `IX-H1` |
| `IXN-08` | **Interaction cost scales with consequence.** Reversible actions are one tap; money, custody and consent actions are deliberate | One-tap payment release; swipe-to-approve an estimate | Design review |

---

# 4. Input Modalities

| Modality | Surfaces | Primary users | Contract |
|---|---|---|---|
| **Pointer** (mouse, trackpad) | `P03`, `P04`…`P08`, `P10`, `P12` | Back office, external web | §5.1 |
| **Touch** | `P01` app, `P02`, `P09`, `P11`, all web at `bp.xs`–`bp.sm` | Customers, field | §5.2, `UX-006` §5 |
| **Keyboard** | All | **Intake, dispatch and finance are keyboard-first**; motor-impaired users (`A-06`) are keyboard-only | §6 |
| **Scanner** | `P02`, `P09`, `P11`, `P03` intake | Technicians, riders, storekeepers | §7 |
| **Voice** | `P02`, `P01` | Bengali voice-to-text (`NFR-074`); low-literacy users (`A-04`) | §8 |
| **Screen reader** | All web; platform readers on `R4` | `A-05` | §6.6, `UX-005` |

| # | Rule |
|---|---|
| `IXN-09` | **A surface supports every modality its audience uses, not every modality that exists.** `P09` does not need a keyboard path for the rider's own tasks; it does need one for the coordinator view |
| `IXN-10` | Modalities **compose**. A user may scan a barcode, correct it with a keyboard and confirm with touch in one task without a mode change |

---

# 5. Pointer, Touch and Gesture

## 5.1 Pointer

| # | Rule | Basis |
|---|---|---|
| `IXN-11` | Actions complete on **up-event over the target**; moving off before release cancels | SC 2.5.2 |
| `IXN-12` | Right-click never carries an action unavailable elsewhere | `IXN-01` |
| `IXN-13` | Double-click is an accelerator only; single-click always has an equivalent path |
| `IXN-14` | Hover changes appearance, never content or availability | `IXN-07` |
| `IXN-15` | Cursor communicates affordance: pointer for navigation, text for editable, grab for draggable, not-allowed **never** — a disabled control explains itself in text (`VB-006` BT-05) |

## 5.2 Touch and gestures

| # | Rule | Basis |
|---|---|---|
| `IXN-16` | Targets ≥ 44 px (`size.target.comfortable`); ≥ 56 px on `P02`/`P09` (`size.target.field`); **absolute floor 24 px** | SC 2.5.8, `URD` §19.3 |
| `IXN-17` | **No path-based gesture is ever the only way** to do anything — no required swipe, pinch, rotate or multi-finger action | **SC 2.5.1** |
| `IXN-18` | Every swipe action is duplicated by a visible control in the row or the detail | `IXN-02`, `URD` §19.3 |
| `IXN-19` | Long-press is an accelerator only, never the sole path |
| `IXN-20` | **Device motion never actuates** — no shake-to-undo, no tilt. A technician on a motorcycle triggers it accidentally | **SC 2.5.4** |
| `IXN-21` | Single-direction scrolling per screen; **no horizontal scroll** on any surface | `URD` §19.3, SC 1.4.10 |
| `IXN-22` | Primary actions sit **bottom, thumb-reachable** on touch surfaces — not top-right desktop muscle memory | `URD` §19.3, persona `A-02` |
| `IXN-23` | Every primary flow is completable **one-handed** | `A-02`, `UX-006` §5.3 |

## 5.3 Drag — and the dispatch board *(closes `U-09`)*

**The problem.** `04-00` §P03 specifies the dispatch console as a live board on which jobs are
assigned by dragging onto technicians. `URD` §21.4 identified this as *"the one material gap"*
against WCAG 2.2: **SC 2.5.7 requires that all functionality using a dragging movement can be
achieved by a single pointer without dragging**, unless dragging is essential. Assignment is not
essential-by-dragging — it is a data change.

**The ruling.**

| # | Rule |
|---|---|
| `IXN-24` | **Every drag interaction in the estate has three equivalent paths**: (a) drag; (b) **single-pointer select-then-target** — click the job, click the technician; (c) **keyboard** — focus the job, `Enter` to pick up, arrow to a technician, `Enter` to drop, `Esc` to cancel |
| `IXN-25` | Path (b) is the **default** shown to a first-time user. Drag is discoverable but never the taught path |
| `IXN-26` | Bulk assignment uses selection, never multi-drag. **A dispatcher assigning a morning queue of 60 jobs in under 10 minutes cannot do it by dragging 60 times** — the accessibility fix is also the throughput fix |
| `IXN-27` | The drop target set is **announced** to assistive technology when a job is picked up, and constrained to valid targets (skill, certification, capacity) before the drop, not after |
| `IXN-28` | Drag has no time limit and no inertia. A trackpad user, a gloved user and a user with tremor must all succeed |

**Every drag interface in the estate, and its non-drag path:**

| Surface | Drag interaction | Single-pointer path | Keyboard path |
|---|---|---|---|
| `P03` Dispatch console | Job → technician | Select job → select technician → confirm | `Enter` / arrows / `Enter` |
| `P03` Workshop console | Job → bench, WIP column | Select job → "Move to…" menu | Same |
| `P03` Inventory console | Stock line → transfer | Select lines → "Transfer to…" | Same |
| `P06` Explore | Field → chart axis | Select field → "Add to…" menu | Same |
| `P09` Manifest | Reorder stops | "Move up" / "Move down" | Arrow keys with modifier |
| `P07` Listings | Reorder images | "Move up" / "Move down" | Same |
| `P01` Booking | Slot selection *(not drag)* | — | — |

> **`IXN-26` is the finding worth carrying to the Steering Committee.** SC 2.5.7 was read in the
> URD as an accessibility cost. It is not: the single-pointer path is faster for everyone above
> about five assignments, and `04-00` §P03 already requires the morning queue in under ten minutes.
> **The accessible design is the performant design here**, and the drag-only design would have
> failed the throughput KPI as well as the criterion.

## 5.4 Selection and bulk action

| # | Rule | Basis |
|---|---|---|
| `IXN-29` | Every list view supports selection and **bulk actions with preview and confirmation** | `URD` §19.2 |
| `IXN-30` | "Select all" selects the **loaded page** and offers an explicit "select all N matching" as a second, distinct action. Conflating them is how 4,000 records get bulk-cancelled |
| `IXN-31` | The bulk-action preview states **what will change, on how many records, and what will not change** — including records skipped because a rule blocks them |
| `IXN-32` | A bulk action that partially fails reports **per-record outcomes**, never a single "some records failed" | `URD` §19.4 |
| `IXN-33` | Bulk actions are **rollback-capable where the action permits** (`FR-SRM-086`) |
| `IXN-34` | Shift-click range selection is an accelerator; checkbox selection is the specified path |

## 5.5 Inline edit and autosave

| # | Rule |
|---|---|
| `IXN-35` | Inline edit is permitted only on fields with **no cross-field rule**. Anything a business rule reads goes through a form (`PS-11` — no business rule client-side) |
| `IXN-36` | **Autosave is explicit or absent.** Where a screen autosaves, it shows saved state and time. Where it does not, it warns on leave (`UX-002` `NVR-64`) |
| `IXN-37` | On `R4`, **every field autosaves to the local journal** — the technician never loses input to a battery death (`AR-010` §4.1). The indicator is `C-62`'s "saved on this device" |
| `IXN-38` | Autosave never commits a state transition. Saving a draft is not submitting |

## 5.6 Undo and reversibility

`NFR-079`: *destructive actions require confirmation and are reversible where the action permits.*
**Two obligations, and the estate treats them as one.**

| Class | Reversible? | Interaction |
|---|---|---|
| Fully reversible (archive, unassign, remove a filter) | Yes | **Undo toast, 10 s, no dialog.** A dialog here is friction with no safety value |
| Reversible with a trail (cancel an order, void a draft) | Yes, audited | Confirmation naming the item + undo within the window |
| Irreversible, low consequence (send a notification) | No | Confirmation naming the recipient count |
| **Irreversible, high consequence** (post an invoice, release a payout, wipe data, issue a destruction certificate) | No | Confirmation naming the item, the amount and the consequence, **plus step-up authentication** where `NFR-065` applies |

| # | Rule |
|---|---|
| `IXN-39` | **Undo where possible; confirm where not.** A confirmation dialog on a reversible action trains users to dismiss dialogs, which is what makes the irreversible ones dangerous |
| `IXN-40` | Undo is **keyboard-reachable** and the toast does not auto-dismiss while focused (SC 2.2.1) |
| `IXN-41` | The confirmation names the **specific item**, never "this record" (`URD` §19.4, `UI-007`) |

## 5.7 Error and validation interaction

| # | Rule | Basis |
|---|---|---|
| `IXN-42` | Validation fires on **blur**, not on keystroke. Per-keystroke validation tells a user their half-typed phone number is wrong | `URD` §19.4 |
| `IXN-43` | On submit, focus moves to the **first error**, and the error is announced | SC 3.3.1, 2.4.3 |
| `IXN-44` | Errors are **inline, adjacent to the field, in the user's language**, and state what to do | `NFR-078`, `UI-004` |
| `IXN-45` | A business-rule block states the rule, why it applies, and the alternative — never "not permitted" | `URD` §19.4 |
| `IXN-46` | Required fields are marked **and labelled**, never by colour alone | SC 1.4.1 |
| `IXN-47` | **No form times out and discards entered data** without warning and an extension | SC 2.2.1, `URD` §21.2 |

## 5.8 Conflict interaction — the `UI-009` contradiction *(`UXA-10`)*

`UI-009` §3.3 provides copy keys `common.conflict.keep_mine` — *"Keep my version"* — and
`common.conflict.keep_theirs`. `AR-010` §5.3 specifies a **server-authoritative authority matrix**:
assignment, pricing, stock, state and entitlement are decided by the server; evidence, notes,
timestamps and measurements are retained from the client. **The system does not offer a choice, and
must not.**

> **Ruling.** `AR-010` governs. A conflict is **disclosed, not delegated**. Where a decision genuinely
> cannot be made (`AR-010` §5.4 *Deferred*), it is raised as a **task for a supervisor**, which
> `UI-009` `common.conflict.manual` already writes correctly.
>
> `common.conflict.keep_mine` and `common.conflict.keep_theirs` are **withdrawn** and raised as a
> content change under `CG-006`. Detailed layout is `UX-006` §8.3.

> **Why this matters beyond two strings.** A technician offered "keep my version" for an assignment
> the server has already reassigned would be shown a choice the system will overrule — which is worse
> than no choice, because it destroys trust in every subsequent message the app shows.

---

# 6. Keyboard

## 6.1 Why keyboard-first is a throughput requirement

`04-00` §P03 requires *"keyboard-first operation for high-volume roles (intake, dispatch, finance)"*
and sets `NFR-076` walk-in intake at **≤ 3 minutes**, dispatch of a full morning queue at
**< 10 minutes**, and `NFR-075` new-agent competence at **≤ 4 hours**. None is reachable with a
mouse-driven interface. **The keyboard specification is an operations requirement that also
satisfies SC 2.1.1.**

## 6.2 The three keyboard-first workspaces

| Workspace | Task | Target | Keyboard commitment |
|---|---|---|---|
| Service intake | Walk-in intake | ≤ 3 min | **Zero mouse actions** on the happy path: search customer → select → scan device → symptom → confirm |
| Dispatch console | Morning queue | < 10 min | Job list traversal, assign, reassign, hold, priority — all keyboard; §5.3 path (c) |
| Finance console | Invoice, receipt, reconciliation | — | Numeric entry, line navigation, post, match — all keyboard |

## 6.3 Shortcut policy

| # | Rule | Basis |
|---|---|---|
| `IXN-48` | Single-character shortcuts exist **only** in the three workspaces above, and are **remappable and suppressible** by the user | **SC 2.1.4** |
| `IXN-49` | Single-character shortcuts are **inactive while focus is in a text input** — the defect SC 2.1.4 exists to prevent |
| `IXN-50` | Global shortcuts use a modifier and are **identical across all thirteen surfaces**: `/` focus search, `?` shortcut help, `Esc` dismiss, `g` then a letter for go-to |
| `IXN-51` | Every shortcut is discoverable from `?` and from the control's tooltip. An undiscoverable shortcut serves only its author |
| `IXN-52` | No shortcut performs an irreversible action without confirmation |

## 6.4 Focus

| # | Rule | Basis |
|---|---|---|
| `IXN-53` | Focus order follows **reading order**, per language (`UX-007` — both are left-to-right, so order is shared) | SC 2.4.3 |
| `IXN-54` | Focus is **always visible** using the `focus.*` tokens; `outline:none` without replacement is a build failure | SC 2.4.7, `UX-001` `FOC-03` |
| `IXN-55` | A focused element is **never entirely obscured** by sticky chrome or banners. Sticky regions declare height; scroll-into-view compensates | **SC 2.4.11** |
| `IXN-56` | Modals and drawers **trap focus**, close on `Esc`, and **return focus to the trigger** | APG dialog pattern |
| `IXN-57` | Dynamic content insertion never moves focus unless the user asked for it | SC 3.2.2 |
| `IXN-58` | Skip-to-content is the first focusable element on every web screen | SC 2.4.1 |

## 6.5 Composite widget patterns

Every composite widget implements its APG keyboard pattern. **Departures are listed; there is
currently one.**

| Component | APG pattern | Keys |
|---|---|---|
| `C-53` Tabs | Tabs | Arrows move, `Home`/`End` jump, `Tab` exits |
| `C-14` Select · `C-15` Combobox | Combobox | Arrows, type-ahead, `Enter`, `Esc` |
| `C-56` Menu | Menu button | Arrows, type-ahead, `Esc` |
| `C-42` Modal · `C-43` ConfirmDialog · `C-55` Drawer | Dialog (modal) | Trap, `Esc`, return focus |
| `C-24` Table | Grid | Arrows cell-to-cell, `Space` select row, `Enter` open |
| `C-54` Stepper | — | `Tab` within step; steps are links |
| `C-19` DatePicker | Date picker dialog | Arrows by day, `PgUp`/`PgDn` by month |
| **Dispatch board** | **None exists** | **Departure — §5.3 path (c) is specified here in full** |

## 6.6 Screen-reader interaction

| # | Rule |
|---|---|
| `IXN-59` | Every state change that matters is announced through a live region — `polite` for status, `assertive` only for errors that stop work (`UI-010` §3.2) |
| `IXN-60` | Long-running operations announce start, **progress at meaningful intervals**, and completion — not on every tick |
| `IXN-61` | Bulk-action results are announced as a **summary**, then made available as a list |
| `IXN-62` | Mixed-script content carries `lang` on every script change, or Bengali is read with Latin phonology (`VB-009` MX-04) |

---

# 7. Scanner Interaction

Scanning is the highest-frequency input on `P02`, `P09` and at intake, and it is the accessibility
answer for low-literacy users (`A-04`).

| # | Rule | Basis |
|---|---|---|
| `IXN-63` | **Scan-first, type-fallback, everywhere a scan is possible** | `URD` §21.3 |
| `IXN-64` | The scanner target is focused by default on any screen whose primary input is a scan. A technician should not have to tap a field first |
| `IXN-65` | A successful scan gives **haptic + audible + visual** confirmation. In a noisy branch or on a street, one channel is not enough |
| `IXN-66` | A scan that does not match is a **designed state**, not a validation error: it says what was scanned, what was expected, and offers manual entry |
| `IXN-67` | Continuous scanning (multi-item verification against a manifest) shows a **running tally against the expected set**, with unscanned items always visible |
| `IXN-68` | Scanning works **offline**, resolving against the locally held reference data, and says so when the reference data is stale (`SIR-17`) |
| `IXN-69` | Scanned identifiers render in `type.code` and are never transliterated or auto-corrected |

---

# 8. Voice Interaction

| # | Rule | Basis |
|---|---|---|
| `IXN-70` | **Bengali voice-to-text is available wherever free text is captured** on mobile | `NFR-074` |
| `IXN-71` | Voice input is always **reviewable and editable before commit**. Bengali speech recognition is imperfect and a voice-captured diagnosis becomes a permanent record |
| `IXN-72` | Voice notes are stored **as audio in addition to any transcript**, never instead of it — a technician's Bengali voice note is evidence (`P02` capability set) |
| `IXN-73` | Voice is never the only input path (`IXN-01`) |
| `IXN-74` | The system never requires the user to speak to succeed — noisy branches, customer privacy, and `A-03` in a helmet |

---

# 9. Redundant Entry — SC 3.3.7

**"No user is asked to enter the same thing twice"** is already user commitment #5 in the `URD`.
WCAG 2.2 makes it a Level A criterion, and it is the criterion most often satisfied by accident and
broken by a new step.

| # | Rule |
|---|---|
| `IXN-75` | Within a process, previously entered information is **auto-populated or selectable**. Address, phone, device, contact person, site — never re-typed |
| `IXN-76` | Multi-step flows (`C-54` Stepper) carry all prior input forward and show it at the confirmation step |
| `IXN-77` | Where re-entry is genuinely required for security (a payment PIN, a step-up code), that is one of the criterion's permitted exceptions and is **stated in the screen record** |
| `IXN-78` | Bulk upload (`P04` CSV service requests) validates against what the system already holds and **reports only genuine differences** |
| `IXN-79` | A failed submission never clears the form. The most common breach of 3.3.7 is an error page that discards input |

---

# 10. The Prototype Programme

## 10.1 `UXA-09` — the position today

Counted at 2026-08-18 14:45 (+06): **`prototype` appears in zero of the 621 demand-side files.**
`Figma` appears in one. **No interaction in this programme has ever been tested with a user before
being built**, across a scope of 12 portals, 15 critical journeys and 250,000 monthly customers.

## 10.2 What a prototype is here

> **`IXN-80`.** A prototype is an artefact a real user can attempt a real task on, without a
> facilitator explaining what to click. Anything else is a demonstration.

## 10.3 The eight prototypes

Selected by consequence, not by novelty: a flow is prototyped when getting it wrong is expensive
and discovering that late is likely.

| # | Prototype | Covers | `BPM` | Journeys | Wave | Why |
|---:|---|---|---|---|:--:|---|
| `PR-1` | **Booking, three steps** | `UI-037`, `SCN-P01` booking set | `BPM-001`, `BPM-010` | 1, 2 | **W1** | Conversion > 72% is `P01`'s primary design KPI. Every step is a drop-off |
| `PR-2` | **Estimate presentation and approval** | `UI-038`, `P01` + `P02` on-site | `BPM-016` | 1, 2, 4 | **W2** | A customer decides to spend money, sometimes on a doorstep on a technician's phone |
| `PR-3` | **Payment and checkout** | `UI-039`, bKash/Nagad/card/bank | `BPM-022` | 1, 2, 7, 8 | **W2** | Money, irreversible, four gateways, and the point the funnel is lost |
| `PR-4` | **Technician job execution, offline** | `P02` job → diagnosis → parts → evidence → QC → sign-off | `BPM-011`, `BPM-013` | 1, 2 | **W2** | The hardest deliverable in the programme (`AR-010`); 24 h offline; one hand, sunlight, gloves |
| `PR-5` | **Sync, queue and conflict disclosure** | `C-62`, `C-63`, `UI-009` | — | all field | **W2** | `AR-010` §6.1 calls this *"the single most important UX decision in the offline design"* |
| `PR-6` | **Dispatch board, all three paths** | §5.3 drag / single-pointer / keyboard | `BPM-011` | 1 | **W1** | SC 2.5.7 and the < 10-minute morning queue, in one artefact |
| `PR-7` | **Custody handover** | `P09` collection, seal, OTP, signature, POD | `BPM-012` | 3 | **W3** | Zero custody breaks is a KPI; a rider in rain at a customer's door |
| `PR-8` | **Registration, onboarding and consent** | `UI-040`, `UI-042`, `LG-008` | `BPM-027` | 7 | **W3** | Seller onboarding completion > 60%; PDPA consent must be genuinely informed |

> **`PR-1` and `PR-6` are W1** because their screens are built in W1–W2 and `SIR-37` requires design
> to lead build by one wave. `GV-004` already finds Wave 1 at 5.33× capacity — if these two are not
> scheduled now they will not happen, and the two most measured interactions in the programme will
> ship untested.

## 10.4 Fidelity and construction

| # | Rule |
|---|---|
| `IXN-81` | Prototypes are built from **`UX-001` components at real fidelity**. A grey-box prototype cannot test target size, Bengali fit or contrast — the three things most likely to fail |
| `IXN-82` | Prototypes carry **real content** from the `UI-*` packs and **real Bengali** from `BN-009`…`BN-013`, not lorem ipsum. English-only prototypes systematically under-detect layout failure (`UX-007` §5) |
| `IXN-83` | Field prototypes (`PR-4`, `PR-5`, `PR-7`) run on **the reference device — mid-range Android 11, 3 GB RAM** — never on a designer's laptop | `P02` non-negotiable #4 |
| `IXN-84` | `PR-5` is tested with **the network genuinely off**, not simulated. Airplane mode for four hours, then reconnect |
| `IXN-85` | A prototype is **thrown away**. It is not the first version of the build. Prototype code that becomes product code carries prototype decisions into production |

## 10.5 The evaluation gate

| # | Rule | Basis |
|---|---|---|
| `IXN-86` | **Every prototype is evaluated with real users under `UX-008`** before its screens enter build. Demonstration to stakeholders is not evaluation | ISO 9241-210 §5.7 |
| `IXN-87` | Participants are drawn from the persona the flow serves — real technicians for `PR-4`, real riders for `PR-7`, real customers for `PR-1` — not from the programme team |
| `IXN-88` | Evaluation runs in **Bengali** for `PR-1`, `PR-2`, `PR-4`, `PR-5`, `PR-7`, because those audiences work in Bengali |
| `IXN-89` | A prototype that fails its task-success criterion is **iterated and re-tested**, not shipped with a note. `UX-008` §6 sets the criteria |
| `IXN-90` | Findings enter the `UX-008` findings log with a severity and an owner. **A finding with no owner is an unrecorded risk** |

---

# 11. Feedback and Perceived Performance

`URD` §19.1 states thirteen thresholds with a named human consequence each. Those are **server**
targets. This section states what the **user sees** at each, which is the part a design owns.

| Elapsed | What the user sees | Rule |
|---:|---|---|
| **0–100 ms** | The result, or an immediate state change on the control | `IXN-04` — feels instantaneous |
| **100–300 ms** | Control enters `loading` state; layout does not shift | |
| **300 ms–1 s** | Inline progress in place; the rest of the screen stays usable | |
| **1–2 s** | Skeleton or progress with a **label saying what is happening** (`UI-008`) | `C-47` labelled after 2 s |
| **2–10 s** | Determinate progress where a total is knowable; **the user can continue elsewhere** | `URD` §19.1 |
| **> 10 s** | Backgrounded: the user is released, and told **where the result will appear** and how they will be notified | |
| **> 60 s** (bulk, 1,000 records) | Progress with per-record outcomes on completion | `NFR-041`, `IXN-32` |

| # | Rule |
|---|---|
| `IXN-91` | **The measured threshold and the perceived threshold are different requirements.** `NFR-001` (2 s p95) is met by the server; this table is met by the design. A screen that meets `NFR-001` and shows nothing for 1.9 s has failed the user |
| `IXN-92` | **No layout shift after first paint.** Reserve space for content that is loading |
| `IXN-93` | Optimistic UI is permitted **only** where the action is local-first and reversible (`R4` journal writes). It is forbidden for anything the server may reject — showing an estimate as approved before the server agrees is a lie the user acts on |
| `IXN-94` | Every long operation is **cancellable**, or says explicitly that it cannot be cancelled |

---

# 12. Motion Behaviour

Values are `UX-001` §5.8. This section is what they are used for.

| # | Rule |
|---|---|
| `IXN-95` | Motion **explains a spatial relationship or a state change**, or it does not happen. Decoration is not a reason |
| `IXN-96` | Entering elements use `motion.easing.standard`; leaving elements `motion.easing.exit`; state changes with no spatial movement use `motion.duration.instant` |
| `IXN-97` | **`prefers-reduced-motion` collapses everything to `instant`.** This is a token-level switch and is not per-component | SC 2.3.3 |
| `IXN-98` | Nothing moves, blinks or auto-advances for more than 5 s without a pause control | SC 2.2.2 |
| `IXN-99` | **No animation runs while the screen is idle on `R4`** — it costs battery against `NFR-082` |
| `IXN-100` | Loading skeletons shimmer at most once per second and stop after 3 s in favour of a labelled progress state |

---

# 13. Verification

| # | Check | Method | Runs |
|---|---|---|---|
| `IX-K1` | Every action reachable and operable by keyboard | Automated traversal + manual per Class B screen | Every build; manual per wave |
| `IX-K2` | Focus order matches the declared order in the screen record | Automated | Every build |
| `IX-K3` | Single-character shortcuts inactive in text inputs and remappable | Automated | Every build |
| `IX-G1` | Every gesture has a visible control equivalent | Manual, per screen record | Per release |
| `IX-D1` | Every drag has a single-pointer and a keyboard path | **Manual, exhaustive over §5.3's table** | Per release |
| `IX-P1` | No action completes on down-event | Automated event-handler lint | Every build |
| `IX-F1` | Acknowledgement within 100 ms of every interaction | Automated timing harness | Nightly |
| `IX-R1` | No field re-requests information already held in the process | Manual per flow | Per flow release |
| `IX-H1` | No information available only on hover | Automated (hover-only content detection) + manual | Every build |
| `IX-M1` | `prefers-reduced-motion` disables all transitions | Automated | Every build |

> `IX-D1` is manual and exhaustive because SC 2.5.7 cannot be automated — a scanner cannot tell
> whether an alternative path exists, only whether a drag handler is present.

---

# 14. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `UX-004-D-01` | Dispatch board and SC 2.5.7 | (a) drag-only, claim "essential"; (b) **three equivalent paths**; (c) drop drag | **(b)** | Assignment is a data change, not an essential drag. Single-pointer selection is also faster for bulk, which the < 10-min target needs | The board is more work to build and faster to use; `IX-D1` becomes a release gate |
| `UX-004-D-02` | Conflict resolution interaction (`UXA-10`) | (a) offer the user a choice per `UI-009`; (b) **disclose the server-authoritative outcome per `AR-010`** | **(b)** | `AR-010` §5.3 is the architecture; offering an overrulable choice destroys trust | Two `UI-009` keys withdrawn; content change raised under `CG-006` |
| `UX-004-D-03` | Undo versus confirm | (a) confirm everything destructive; (b) **undo where reversible, confirm where not** | **(b)** | Confirmations on reversible actions train dismissal, which endangers the irreversible ones | Requires an undo window in the API for reversible actions — raised to `IN-002` |
| `UX-004-D-04` | Optimistic UI | (a) broadly; (b) **local-first reversible actions only** | **(b)** | Showing a server-rejectable state as committed is a lie the user acts on | `R4` feels instant; web surfaces show real state |
| `UX-004-D-05` | Prototype fidelity | (a) grey-box wireflows; (b) **real components, real Bengali, reference device** | **(b)** | Grey-box cannot test target size, Bengali fit or contrast — the likeliest failures | Prototypes cost more; `IXN-85` prevents them becoming product |
| `UX-004-D-06` | Prototype count | (a) all 6 `UI-*` flows; (b) **8 — the 6 flows plus dispatch and sync/conflict** | **(b)** | The two additions are the highest-consequence interactions in the estate and neither has a copy pack to anchor it | +2 prototypes ≈ 15 PD, inside the `UX-003` §11 band |

---

# 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Which prototyping tool? **One file in 621 mentions Figma**; no tool decision exists. `IXN-81` requires component fidelity, which constrains the choice | Head of Product Design | **W0** | All eight prototypes |
| `Q-02` | Who recruits real technicians, riders and customers for evaluation? `UX-008` §4 specifies the panel; nobody owns recruitment | HR + Change Lead | **W1** | `IXN-87`, `PR-1`, `PR-6` |
| `Q-03` | Does the API support an undo window for reversible actions, or is undo a client-side deferred commit? | Chief Architect | W2 | `UX-004-D-03` |
| `Q-04` | Bengali voice-to-text provider and its offline capability — `NFR-074` requires it on mobile, and `P02` runs 24 h offline | Mobile Lead | W2 | §8 |
| `Q-05` | Is the reference device fleet procured? `IXN-83` needs mid-range Android 11 / 3 GB units in the design team's hands | Programme Manager | **W1** | `PR-4`, `PR-5`, `PR-7` |
| `Q-06` | Do the withdrawn `UI-009` keys need replacement copy for the deferred-to-supervisor case, or does `common.conflict.manual` cover it? | Content Design Lead | W2 | `UXA-10` closure |

---

# 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every WCAG 2.2 pointer and input criterion (2.5.1, 2.5.2, 2.5.4, 2.5.7, 2.5.8) has a rule that satisfies it | §5 |
| `AC-02` | **Every drag interaction in the estate is enumerated with its non-drag paths** | §5.3 |
| `AC-03` | Keyboard operation is specified for the three keyboard-first workspaces with a shortcut policy meeting SC 2.1.4 | §6 |
| `AC-04` | The `UI-009` / `AR-010` contradiction is ruled and the correction raised | §5.8, `UX-004-D-02` |
| `AC-05` | A perceived-performance contract exists for every threshold in `URD` §19.1 | §11 |
| `AC-06` | Eight prototypes are scoped, sequenced and tied to an evaluation gate | §10 |
| `AC-07` | Every rule has a named verification method, or is stated as manual-only with the reason | §13 |

**Definition of done.** Complete when every criterion is met, `Q-01` and `Q-05` are resolved, `PR-1`
and `PR-6` are scheduled in W1, and `PGD-000`'s `UX-004` row is updated with a fresh enumeration
timestamp.

---

# 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `UX-001` §5.8, §5.9 | Motion and focus tokens |
| Upstream | `UX-002` | Navigation model and back behaviour |
| Upstream | `UX-003` §5.4, §9 | The 130 bespoke screens and the F3 rung |
| Upstream | `RQ-007` `BPM-*` | Process models the prototypes must honour |
| Upstream | `AR-010` §5, §6 | Conflict authority — the basis of `UX-004-D-02` |
| Downstream | **`UX-005`** | SC 2.5.x conformance evidence derives from §5 |
| Downstream | **`UX-006`** | Field interaction specialises §5.2 and §7 |
| Downstream | **`UX-008`** | Evaluation gate `IXN-86` |
| Downstream | `QA-003` | `IX-*` checks enter the test design |
| Downstream | `IN-002` | Undo window (`Q-03`) |
| Lateral | `UI-007`, `UI-008`, `UI-009`, `UI-037`…`UI-042` | Copy for the interactions specified here; `UI-009` correction §5.8 |

---

# 18. References

**Within this repository**
`../PGD-000_…` · `./_CATEGORY_OVERVIEW.md` · `./UX-001`…`./UX-003`, `./UX-005`…`./UX-008` ·
`../01_Requirements_Engineering/RQ-006`, `RQ-007` · `../02_Architecture_and_Design/AR-010`

**Workspace**
`../../1000fix_ERP_Module/04_Portals_and_Applications/04-00` §P02, §P03, §P09 ·
`../../project_content/03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-037`…`UI-042` ·
`../../project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-007`, `UI-008`, `UI-009` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_URD.md` §19, §21.4, §26

**External standards and sources**

| Source | Verified |
|---|---|
| W3C — WCAG 2.2, **SC 2.5.7 Dragging Movements (AA, new in 2.2)**, SC 2.5.8, 2.5.1, 2.5.2, 2.5.4, 2.1.4, 2.4.11, 3.3.7 | 2026-08-18 |
| W3C WAI — ARIA Authoring Practices Guide (APG), pattern set | 2026-08-18 |
| ISO 9241-210:2019 §5.6 produce design solutions, §5.7 evaluate against requirements | 2026-08-18 |
| ISO 9241-161:2016 — Guidance on visual user-interface elements | 2026-08-18 |

---

# 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Head of Product Design | Initial issue. Closes `U-09` by enumerating **every drag interaction in the estate with three equivalent paths**, and finds the SC 2.5.7 remediation is also the throughput fix for the < 10-minute dispatch target. Rules the `UI-009` / `AR-010` conflict contradiction (`UXA-10`). Establishes the **first prototype programme in the estate** — eight prototypes with a real-user evaluation gate — against a counted position of **zero occurrences of "prototype" in 621 files** (`UXA-09`) | *(pending — `PGD-A1-09`)* |

---

*`UX-004` · Category 06 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
