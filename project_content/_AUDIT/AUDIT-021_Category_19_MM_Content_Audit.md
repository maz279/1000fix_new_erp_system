---
id: FIX-ERP2-AUDIT-021
title: Category 19 MM — Multimedia & Asset Specifications Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 12 Category 19 MM files, their citations into the module repository and the content register, cross-register integrity, gate F7, the inbound obligations eight other categories delegated to this one, and the concurrency between this category and Category 99
mandate: Audit required on completion of Category 19 authoring (rule CM-R9)
extends: AUDIT-001 … AUDIT-020
enumeration_date: 2026-08-17 18:26 UTC
method: Filesystem enumeration and identifier extraction only (RG-06, CP-11). No figure in this report is projected, and none is taken from what a document says about itself — including what this category's own files say about themselves. Eighteen claims made by this category's own files, and thirteen made about it by files in five other categories, were found false by extraction and corrected; they are reported as findings, not as silent edits. One finding in this report was itself invalidated during the audit by concurrent authoring and is retained with its correction (MM-15).
---

# Category 19 `MM` — Multimedia & Asset Specifications Content Audit
### 12 files · **452 of 452 registered content files now written — the register is complete on disk**

---

## 1. Method and result

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F7 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration and extraction.
**Enumeration instant 2026-08-17 18:26 UTC.**

Nine category-specific extractions were run:

| Extraction | What was compared |
|---|---|
| **Y1** | Every content identifier cited, against the 452 register rows and against disk |
| **Y2** | Every relative markdown link, resolved against the filesystem, both before and after remediation |
| **Y3** | Register filenames against disk, byte for byte, both directions; register row cell counts |
| **Y4** | Every front-matter key against the 24-key house set |
| **Y5** | Section headings against `TPL_Content_File_Front_Matter.md`, and the `CG-009` §3 `MM` required addition |
| **Y6** | Every file-local rule prefix against the 21 content category codes and against prefixes in use elsewhere |
| **Y7** | Each file's registered wave against the wave of the file that first consumes it |
| **Y8** | **Every inbound claim about Category 19's existence, in every other category** |
| **Y9** | Each of the eleven inbound `MM-*` delegations, against what the written file actually discharges |

**Fifteen findings — 1 critical, 3 high, 5 medium, 6 low.** Six were remediated during the audit
and one was resolved by an event during it (MM-15); **eight are open**, and seven of those are
owned outside the content function.

| Severity | Count | Fixed / resolved | Open |
|---|---:|---:|---:|
| Critical | 1 | 0 | 1 |
| High | 3 | 0 | 3 |
| Medium | 5 | 2 | 3 |
| Low | 6 | **5** | **1** |

> **Four findings in this report are against the auditor's own authoring** (MM-08, MM-10, MM-11,
> MM-15). That is stated because the convention inherited from audit `00-07` requires it, and
> because three of the four were introduced by the same pass that exists to prevent them.

> **On concurrency — and this time it is not a footnote.** **Category 99 `RF` was authored
> between 01:27 and 02:19 local while Category 19 was being written.** All twelve `RF` files
> landed, **including `RF-006` Content Decision Log and `RF-009` Sample and Reference Data Pack**,
> which nine `MM` files had recorded as unwritten. **Eighteen claims in this category's own files
> were false at the moment the audit ran.** `AUDIT-016` AP-17 recorded the register-count
> consequence of concurrent authoring; this is the first instance where concurrency made a
> category's **substantive open items** wrong rather than its arithmetic. See finding MM-08 — and
> MM-15, where it happened a third time, to a finding inside this report.

> **This report is `AUDIT-021`, not `AUDIT-019` or `AUDIT-020`.** `AUDIT-019` is occupied on disk
> by the Category 16 `CM` audit, written at 01:13. **`AUDIT-020` was allocated by register
> citation** — Master Index §1 and `RF-008` both cite it — **and was absent from disk at the
> enumeration instant; it was written by the concurrent session during this audit** (MM-15). The
> `AUDIT-012` `BN-24` precedent governs either way: **the register allocation wins and the later
> report moves.** `AUDIT-014` `TS-03` recorded what went wrong when a slot was vacated and never
> filled; **no slot is vacated here.**

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | **12 of 12** ✅ |
| **A2** Total written | **452 of 452**, enumerated 2026-08-17 18:26 UTC. **The register is complete on disk for the first time.** Categories 19 `MM` and 99 `RF` both completed in this window ✅ |
| **A5** Files on disk with no register entry | Zero ✅ |
| **B1** ID uniqueness | 12 unique ✅ |
| **B2** Contiguity `MM-001`…`MM-012` | No gaps ✅ |
| **B4** File name matches ID | **12 of 12, byte for byte against the register, both directions** ✅ |
| **C1/C2** `purpose:` and `traces_to:` present | 12 of 12 ✅ |
| **D1** Internal links resolve | **573 relative links, zero broken** ✅ |
| **D2** Files in their declared subfolder | **12 flat**, matching Master Index §3.2, which declares `MM-001 … MM-012` with no subfolders ✅ |
| **D3** No spaces or ampersands in any path | Zero ✅ |
| **E7** Template conformance | **All six `TPL_Content_File_Front_Matter.md` sections present, in order, in all 12** ✅ *(with a declared adaptation in every file — finding MM-05)* |
| **F1** Front matter complete | **All 24 required keys present in all 12** ✅ |
| **Y1** Content-ID citations | **173 distinct identifiers cited, 173 resolve on disk.** Zero unregistered ✅ *(after remediation — finding MM-10)* |
| **Y5** `CG-009` required addition | **All 12 carry a deliverable specification table** stating format, dimensions, colour, naming and metadata ✅ |
| **Y6** Rule-prefix integrity | **525 file-local rules defined across 12 prefixes; zero now collide with a content category code** ✅ *(after remediation — finding MM-11)* |

### 2.1 Cross-register reconciliation — gate F7

**All seven dimensions reconcile exactly.** Every figure below was extracted from the files' front
matter, not read from the register.

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---|---:|:--:|
| File count | Master Index §4 | 12 | 12 | ✅ |
| Priority `P0`/`P1`/`P2`/`P3` | Master Index §1 | 0 / 1 / 7 / 4 | 0 / 1 / 7 / 4 | ✅ |
| Wave per file | Master Index §4 rows | W1×6, W2×3, W4×1, W6×2 | All 12 match | ✅ |
| Content class A/B/C/D/E | `CG-002` §4.1 | 0 / 0 / 0 / 12 / 0 | 0 / 0 / 0 / 12 / 0 | ✅ |
| Bilingual / English-only | `CG-010` §3.2 | 0 / 12 | 0 / 12 | ✅ |
| Template allocation | `CG-009` §3 | 12 Generic | 12 Generic | ✅ |
| Subfolder allocation | Master Index §3.2 | 12 flat | 12 flat | ✅ |

**The single `P1` is `MM-002`**, and the allocation is correct for a reason the register does not
state: five files in three other categories — `CG-011` `AT-08`, `CG-008` `U-41`/`HC-c`, `HC-002`
`HS-19`/`HS-21`, `UI-010` `A-07` and `AP-012` §4.5.6 — **delegate a personal-data control to it**,
not a style rule. `MM-002` is the only file in this category with a second owner (Security).

**The class allocation is the cleanest in the register: twelve files, one class, one approver.**
Unlike `EO` (`AUDIT-018` EO-10) and the six categories `AUDIT-016` AP-09 named, `CG-002` §6 and
§4.1 agree for Category 19 without qualification. **One consequence of that cleanliness is a
defect** — see MM-09.

### 2.2 `CG-010`'s rationale — the one that got it right

`AUDIT-017` `OP-13` and `AUDIT-018` `EO-13` both found `CG-010`'s per-file bilingual model unable
to express *"a file whose outputs are bilingual"*, and `AUDIT-018` concluded that **two categories
hitting the same limit from opposite directions makes it a `CG-010` defect.**

**For Category 19, `CG-010` §3.2 anticipated the case and printed it in the rationale column:**

> *"Specifications for suppliers, who work in English. **The assets they produce are bilingual;
> the briefs are not.**"*

**This is the only rationale in §3.2 that states the distinction.** Category 19 therefore does not
add a third instance to that finding — but the *obligation* the rationale creates had nowhere to
land, and now does: `MM-001` §4.8 `AS-16`…`AS-19`, which state that a bilingual asset is two
assets, that cost is quoted per language, and that a missing Bengali variant blocks the pair.
**Recorded as evidence for the `AUDIT-017` R-\* / `AUDIT-018` remediation that `CG-010` should
carry this column form for every category.**

---

## 3. Findings

### MM-01 — The screenshot control cannot be operated, and six files now assume it can

**Severity: CRITICAL · Status: OPEN · Owner: Test Lead with Security and Content Design**

**What was found.** `MM-002` is the category's only `P1` because five files delegate a
personal-data control to it. **The control has three preconditions and none of them exists.**

| Precondition | Rule | State |
|---|---|---|
| A sandbox to capture from | `MM-002` `SC-01`, `SC-02` — *"never from production. No exception, no waiver"* | **`TS-002` does not exist** |
| A person to verify redaction who is not the author | `SC-29`; `CO-04` reviewer ≠ author | **No Chief Data Officer is appointed** (`LG-008` `O-05`) |
| Tooling that strips metadata, flattens redaction and stamps the register | `SC-24`, `SC-28`, `SC-43` | **Undecided** (`MM-002` `O-07`) |

**Six files now record the sandbox absence independently** — `HC-002` `O-02`, `TR-003` `O-01`,
`HC-020` `O-04`, `MM-001` `O-03`, `MM-002` `O-01`, `MM-007` `O-04`. That is not six problems; it
is one problem discovered six times by six authors, which `CG-012` §6 treats as evidence a
constraint is real rather than an authoring artefact.

**Why it is Critical.** `AUDIT_Checklist_Recurring.md` defines Critical as *"a required artefact
assumed present when absent."* **Fifteen help sets, twenty course packs, sixteen knowledge files
and every release note assume screenshots can be produced.** They cannot be produced lawfully:
`SC-01` prohibits production capture and there is no alternative source. **The pressure this
creates is the dangerous part** — an author against a wave gate, with no sandbox and a template
demanding a screenshot, will capture from production, and a production screenshot of this system
contains `S3` restricted data by definition (`05-02` §10): National ID, TIN, bank details,
biometric templates, seller KYC documents.

**A screenshot defeats the `T5` access controls in a single act.** `05-04` §4 makes those fields
allow-listed, step-up authenticated and logged on every access; `LG-008` `PI-05` requires bulk
export to be approved and logged. **A screenshot in a published help article is an unlogged,
unauthenticated, permanent, freely copyable export**, published to 250,000+ customers a month —
against a statute whose enforcement mechanisms activate around **13 May 2027**, inside Wave 4, at
**BDT 25 lakh rising to BDT 50 lakh** (`05-06` §6.3, `RSK-032`).

**Remediation instruction.** **Sequence `TS-002` ahead of the first help set and the first course
pack, not alongside them.** Appoint the redaction verifier — it need not be the Chief Data
Officer, but it must be someone who is not the author and it must be named. Select the tooling
before volume begins: **a manual redaction pipeline at this volume fails silently at exactly the
step that matters.** Until all three exist, **no screenshot may be produced anywhere in the
programme**, and that position should be stated in `CG-008` rather than left implicit in `SC-01`.

---

### MM-02 — The category specifies production the programme has not budgeted, and now the number is visible

**Severity: HIGH · Status: OPEN · Owner: Content Design Lead and HR Director with Finance**

**What was found.** The Master Index §7 estimate for Category 19 is **45–70 person-days**, with
the qualifier *"specification only; production cost is separate."* **The separate cost appears in
no plan, and the twelve written files now make its shape countable for the first time:**

| Production commitment | Source | Scale |
|---|---|---|
| **Customer how-to video** | `MM-007` §4.1, from `HC-020` | **22 scripts × 2 languages = 44 productions**, plus 88 caption files and 44 transcripts |
| **Training video** | `MM-006` §4.2 | Five series across 20 course packs, **including HSE-gated safety content** |
| **Photography** | `MM-009` §4.5 | Eight shot groups, **representative across branches outside Dhaka and more than one division** |
| **Animation** | `MM-008` §4.1 | Seven explainers, light and dark, static fallbacks, per-portal player testing |
| **Icon set** | `MM-004` §4.1 | **53 glyphs**, 16 px optical variants, five-size ramp, six states, contrast proof sheets |
| **Illustration** | `MM-005` §4.4 | **11 distinct assets serving 22 states**, plus a cultural review panel |
| **Screenshots** | `MM-002` §4.10 | **Recurring for the life of the product**, doubled for Bengali, re-captured every release |
| **Print specimens** | `MM-010` §4.10 | Ten-specimen regression set, **physically printed on every printer model** |

**Four files record the absence independently** — `MM-006` `O-01`, `MM-007` `O-01`, `MM-008`
`O-04`, `MM-009` `O-08` — and `HC-020` `O-02` recorded it before this category existed:
*"44 productions in two languages is a programme, and it appears in no plan."*

**Why it is High.** `AUDIT_Checklist_Recurring.md` defines High as *"materially misleading, or a
budget or scope exposure."* **This is a scope exposure that compounds `AF-09`**, the content
effort variance already escalated alongside the 1,513 PW versus 834 PW build variance (`D-14`).
The specification estimate is honest; **the register's silence about production is what
misleads**, because a reader of §7 sees 45–70 person-days against a category that commissions a
film unit, a photographic commission, a motion studio and an icon designer.

**And one item is not a project cost at all.** Screenshot production is a **recurring operational
load**: capture, redact, second-person verify, annotate, register and re-capture per release,
across two languages, for the life of the product. It has no home in a project budget and no owner
in `CG-002` §3.

**Remediation instruction.** Produce a production cost envelope for Category 19 and take it to
Steering **in the same paper as `AF-09`**, not separately — the reasoning `CG-002` §9 already
applies to the content estimate against the build variance. Separate the recurring screenshot load
from the one-off commissions and assign it an owner.

---

### MM-03 — Twelve files now record an unnamed accessibility reviewer, and four blocking gates have no one to operate them

**Severity: HIGH · Status: OPEN · Owner: Content Design Lead**

**What was found.** Every one of the twelve `MM` files records that **no accessibility reviewer is
named.** The gap was already recorded by `TR-003` `O-02`, `HC-002` `O-04` and `HC-016` `O-04`;
Category 19 adds nine more instances and, more seriously, **four gates that block acceptance:**

| Gate | File | What it blocks |
|---|---|---|
| Accessibility deliverables as acceptance criteria | `MM-001` §4.11 | **A media delivery cannot be accepted** — captions, transcripts, alt text and description are blocking checks |
| Icon non-text contrast at 3:1 and focus verification | `MM-004` §4.5, §4.4 | **The design-system library cannot be released** — fifteen icon-only controls stand alone and each needs a verified focus ring |
| Tagged-PDF reading order in bilingual parallel columns | `MM-010` §4.8 | **The hardest accessibility check in the programme**, on 34 bilingual templates, 26 of them statutory |
| The three Level A criteria motion can breach by existing | `MM-008` §4.5 | **SC 2.2.2, SC 2.3.1 and SC 1.1.1** — none visible in a static review |

**Why it is High.** `PS-04` and `NFR-073` make WCAG 2.1 AA **contractual** on all web portals, and
`05-06` §11 requires an automated scan **plus a manual audit** before each portal release. **The
manual audit has no auditor.** `TS-016` `O-07` recorded the reciprocal gap from the test side —
media accessibility obligations *"with no owning specification"* — and this category has now
supplied the specifications, which converts the finding from a content gap into a **staffing** gap
with a contractual consequence.

**`CG-011` §8.2 compounds it.** Bengali screen-reader testing requires *"a Bengali-speaking tester
with real assistive technology"*, and none is identified either.

**Remediation instruction.** Name an accessibility reviewer with authority to block a release, and
a Bengali-speaking tester. **This is the fourth consecutive category to ask** — after `TR`, `HC`
and the `MM` files themselves — and the request has escalated from "no reviewer for content" to
"four acceptance gates with no operator."

---

### MM-04 — Four files are consumed before they exist; the seventh consecutive category, and the fourth request

**Severity: HIGH · Status: OPEN · Owner: Programme Content Lead**

**What was found.** Extraction `Y7` compared each file's registered wave against the wave of the
file that first consumes it.

| File | Registered | First consumed | Basis |
|---|:--:|:--:|---|
| **`MM-005`** Illustration and empty-state artwork | **W2** | **W1** | `UI-006` is `P1` at **W1** and its own position is *"on day one of every wave, every screen is an empty state"*. W1 is the first wave with users on it — `P03` and its fourteen workspaces |
| **`MM-008`** Animated explainer | **W6** | **W2** | `HC-016` is W2 and surfaces the animations. **Four waves.** The first users of `P04`, `P05` and `P08` meet a tour with no asset |
| **`MM-011`** Email and HTML asset spec | **W2** | **W1** | `CM-005` (`P1`, W1) and `CM-009` (W1) both name it as their layout authority; `CM-005` `O-05` recorded the absence before this file existed |
| **`MM-003`** Diagram visual standard | **W1** | **W0** | `SP-003` is W0 and cites it for the visual half of its notation |

**`MM-010` is a different shape and is reported separately as MM-07.**

**This is the seventh consecutive category with the same defect.** `AUDIT-008` found three in
`KB`, `AUDIT-009` two in `TR`, `AUDIT-010` two in `HC`, `AUDIT-014` **nine** in `TS`, `AUDIT-015`
five in `RP`, `AUDIT-016` **twelve** in `AP`, `AUDIT-018` six in `EO`. **With these four the
register-wide total is at least 43 across seven categories**, and the Category 16 audit
(`AUDIT-019`) may have added more.

`AUDIT-014` R-02 asked for the sequencing basis to be corrected **once, register-wide, before
Categories 14–19 and 99 were authored.** All six have since been authored. `AUDIT-015` R-04
repeated it. `AUDIT-018` R-03 recorded it as the third escalation and warned explicitly against
patching file by file, because `AUDIT-010` R-02 did so and the pattern recurred.

**This report therefore does not patch its four.** Each is recorded in its own file's `O-01` as
*"reported, not patched, per `AUDIT-018` R-03"*.

**Remediation instruction.** As `AUDIT-014` R-02, `AUDIT-015` R-04 and `AUDIT-018` R-03 —
**correct the basis once, register-wide.** The two that cannot wait are **`MM-011` (W2 → W1)**,
because two W1 `CM` files already cite it as operative, and **`MM-005` (W2 → W1)**, because `P03`
launches at W1 with fourteen workspaces whose empty states are the launch experience.

---

### MM-05 — Template 17 does not exist, and this is the sixth category to declare the same adaptation

**Severity: MEDIUM · Status: FIXED (declared and contained) · Owner: Content Design**

**What was found.** `CG-009` §3 allocates all 12 `MM` files to **template 1 Generic** with one
required addition — *"deliverable specification table (format, dimensions, colour, naming,
metadata)"* — and §6 proposes **template 17 `TPL_Asset_Specification.md`** at `P3` with the
recommendation that it and its peers be added *"before their categories are authored."*
**`_templates/` holds 12 templates and no `TPL_Asset_Specification.md`.**

All twelve files carry the required addition and all twelve declare the adaptation in a
conformance note. **One is a substitution rather than a direct application:**

| File | Substitution | Why |
|---|---|---|
| `MM-012` | **The asset record schema** (§4.9) in place of a deliverable table | Its deliverable **is** the register; a "format, dimensions, colour" table for a register is meaningless. The 34-field record schema states what every asset must carry, which is the same obligation in the correct shape |

**This is the sixth occurrence of the same template-set defect.** `AUDIT-008` `KB-10`,
`AUDIT-009` `TR-11`, `AUDIT-010` `HC-11`, `AUDIT-014` `TS-14` and `AUDIT-018` `EO-06` found it in
five other categories. **Six categories have now adapted a template the same way and declared it
the same way, and `E7` has passed on all six.**

**Remediation instruction.** As `AUDIT-018` R-06 — add the variant to `_templates/`, **or amend
`CG-009` §3 once to permit the declared adaptation.** **This recommendation has now been made six
times.** At six occurrences the correct conclusion is that `CG-009` §6's proposal was right and
was simply never actioned; the cheaper fix is the one-line amendment, not five new templates.

---

### MM-06 — The 1000FiX master identity is still unowned, and `MM-001` declines to become its silent home

**Severity: MEDIUM · Status: OPEN · Owner: Brand Lead**

**What was found.** `AUDIT-018` `EO-13` found that **no file in this content set holds the 1000FiX
logo, its clear space, minimum size, colour system or misuse rules**, and `R-13` asked the Brand
Lead either to register the identity standard in `VB` **or to accept `MM-001` as its home**,
before a mark is issued to any partner.

**`MM-001` §4.12 declines**, and states the reasoning:

| Question | `MM-001`'s position |
|---|---|
| Does it hold the identity? | **No.** It is a production and delivery specification; an identity standard states construction, clear space, minimum size, misuse and lock-ups — a different document, owner and review cycle |
| What does it do instead? | Governs how identity assets are **produced and delivered** once the standard exists, and records the gap as its `O-01` with the two available resolutions |
| Can a mark be issued now? | **No.** `EO-012` `CB-03` remains unenforceable |

**Why this is reported rather than closed.** Accepting `MM-001` as the home would close `R-13` on
paper and leave `EO-012` §4.4's approval checklist with nothing to check against — items 3, 4 and
5 are *"reproduction from supplied files, clear space and minimum size, approved lock-ups"*.
**A recorded gap with a named owner is a better answer than a false home**, which is the position
`CG-012` §6 takes on unsourceable claims generally.

**Remediation instruction.** As `AUDIT-018` R-13, **now second-requested**: register a new `VB`
file whose identifier the Programme Content Lead allocates under `CG-005` `ID-04`, **or** adopt
`CB-001` from the corporate-website set by reference and accept its separate approval authority.
`MM-001` `O-01` sets the date at **W1**, earlier than `R-13`'s W7, because `MM-010` and `MM-011`
both need identity assets at W1 and W2.

---

### MM-07 — All 44 `DT` templates were authored before the specification that renders them

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with Platform Engineering**

**What was found.** Category 05 `DT` is complete at 44 of 44 and `MM-010` is registered at the
same wave, **W1**. `VB-004` §15 names `MM-010` as *"the design deliverable this standard is
implemented as"* and `DT-001` §10 as *"the design deliverable that implements this standard"* —
**but both were written, and all 43 subordinate templates authored, before it existed.**

Each template's `DT-001` §3 layout declarations — zones used, overflow behaviour, bilingual
pattern — were therefore written against **`VB-004` prose** rather than against a component
inventory. `MM-010` §4.4 now defines twelve components and `PT-11` requires a template to compose
them rather than draw primitives.

**This is not the MM-04 shape.** The wave is correct; the **authoring order** is inverted. It is
closer to `AUDIT-018` `EO-08`, where `SP-024` guessed identifiers against an unwritten register
and both guesses landed on real files.

**Why it matters.** `CG-007` gate `G6` requires the **rendered output** to be verified against the
instrument, not only the specification. A template whose declarations do not map onto the engine's
component set will be discovered at `G6`, on a statutory document, by an external adviser.

**Remediation instruction.** Run a reconciliation pass — **every template's declared zones,
overflow behaviour and bilingual pattern checked against `MM-010` §4.4 and §4.6 — before the
engine is built, not after.** `MM-010` `O-01` records it. Note that `PT-13`'s blocking-field guard
will surface `AUDIT-013` `LG-01`'s nine missing `MD-028` fields as a **blocked render at W1**
rather than as a wrong document later, which is the correct outcome and should be expected.

---

### MM-08 — Category 99 landed mid-audit and made eighteen of this category's own claims false; thirteen inbound claims were false in the other direction

**Severity: MEDIUM · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Category 19 was authored between roughly 01:07 and 02:20 local. **Category 99
`RF` was authored between 01:27 and 02:19 in the same window**, and all twelve files landed —
including **`RF-006` Content Decision Log** and **`RF-009` Sample and Reference Data Pack**.

`MM` files had recorded both as unwritten, following `AUDIT-017` `OP-12` (*"ninety-four open
decisions, and the log they must be recorded in does not exist"*) and `AUDIT-018`'s index note
(*"`RF-006` remains unwritten and is now named as a blocking dependency by three Category 18
files"*).

**Extraction found eighteen false claims in this category's own files:**

| Claim | Instances |
|---|---:|
| `RF-006` — **unwritten** in the §6 Maintenance change-log row | **12** |
| `RF-006`/`RF-009` **does not exist** in an Open Item or a rule | **6** |

**And extraction `Y8` found the mirror image in eight other files:**

| File | Claim |
|---|---|
| `TR-003` `O-04` | *"`MM-001` multimedia specifications are unwritten (Category 19 unstarted)"* |
| `HC-002` `O-01` | *"`MM-002` screenshot production specification is unwritten"* |
| `HC-020` scope note, §Before-you-start, `O-01` | *"(Category 19, unstarted)"* · *"unwritten"* · *"nothing can be filmed"* |
| `TS-016` `O-07` | *"Category 19 is unstarted"* |
| `CM-005` §Out-of-scope, `O-05` | *"`MM` holds zero files"* |
| `CM-009` ×2 | *"Category 19 holds zero files"* |
| `CM-010` ×2 | *"Category 19 holds zero files"* |
| `EO-012` ×3 | *"`MM-012`, unwritten"* · *"both unwritten"* |

**Why it is reported rather than quietly fixed.** This is precisely the failure `CG-002` §1
identifies as the largest finding in each of three prior audits: *"work existed that no register
knew about, or a register described work that did not exist"* — `00-06` C-02, `00-07` H2-01,
`AUDIT-001` AF-03. **It occurred twice in one hour, in both directions, purely from concurrency**,
and neither side could have detected it by reading.

**Remediation applied.**

- **18 claims corrected in the 12 `MM` files.** The change-log rows now link `RF-006`; the four
  affected Open Items are **restated as read-across obligations rather than deleted** — the log
  exists, the `MM` entries have not been made, and that is a live backlog with an owner.
- **13 claims corrected in 8 files across 5 other categories**, each restated so the specification
  gap closes and the **substantive** gap behind it stays visible. `HC-020` `O-01` is the clearest
  case: *"Nothing can still be filmed, but for a different reason"* — no crew, no budget, no
  sandbox.

**Remediation instruction, open.** `AUDIT-016` AP-17 proposed rule `RG-08` for concurrent
authoring and it covers **counts**. **It does not cover claims.** Extend it: *a category
completing while another is in flight re-checks every existence claim it makes about the other,
in both directions, before its audit issues.* Neither `AUDIT-018` nor this report would have found
it without an explicit extraction.

---

### MM-09 — Category 19's cleanest dimension produces its sharpest modelling defect: a class-`B` instrument inside a twelve-`D` category

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with Legal Counsel**

**What was found.** `CG-002` §4.1 allocates Category 19 as **0 A / 0 B / 0 C / 12 D / 0 E**, and
§6 gives it a single approver class, **D**. Gate `F7` passes exactly. **Unlike the six categories
`AUDIT-016` AP-09 named and the `EO` case in `AUDIT-018` EO-10, there is no class-set conflict
here at all.**

**And that is the problem.** `MM-009` §4.2 requires a **bilingual photographic consent and release
form**. That artefact:

- is an **operative legal instrument** — `LG-008` `CN-R1` invalidates a consent recorded without
  the notice version; `CN-R2` requires an affirmative act; `PH-09` makes the Bengali version the
  one most subjects actually read;
- **fails as processing if defective** — not as comprehension, which is `CG-002` §4's own
  definition of class `B` rather than class `D`;
- **cannot be class `B` in this category** without breaking `F7`'s class dimension.

`MM-009` §7 `O-01` records the position taken: **the form is drafted and approved by Legal Counsel
under `LG-008`, and `MM-009` cites it rather than holding it.** That is correct and it leaves a
brief owned by Brand requiring an instrument owned by Legal, with **no register row expressing the
dependency.**

**Why it matters.** A later reader of `CG-002` §4.1 sees a category with no legal exposure. A
later reader of `MM-009` sees a Brand file requiring a consent form. **Neither sees that the form
is the control on which the lawfulness of the whole shoot rests.**

**Remediation instruction.** Either register the consent-and-release form as a `LG` artefact with
its own row — the honest answer, and it moves `CG-010`'s and `CG-002`'s counts by one — or record
in `CG-002` §4.1 that a category's class allocation covers its **files** and not the **instruments
they require**. Fold into `AUDIT-016` AP-09 and `AUDIT-018` R-10 rather than reporting separately;
**this is the third distinct shape of the same `CG-002` §6 modelling limit.**

---

### MM-10 — The auditor cited an identifier that does not exist, in the file whose subject is not doing that

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Extraction `Y1` resolved **175 distinct content identifiers**, of which
**174 existed on disk. One did not: `VB-011`.**

It appeared once, in `MM-001` `O-01`, in the remediation text for `AUDIT-018` `R-13`:
*"register it in `VB` (a new `VB-011`, which requires an ID allocation under `CG-005` `ID-04`)"*.

**The parenthesis is self-aware and the citation is still wrong.** `CG-005` `ID-07` states that
content files *"cite programme-wide identifiers — they **never allocate** them"*, and `ID-04`
reserves allocation to the Programme Content Lead. **Writing `VB-011` in backticks allocates it in
substance**, and to an extraction it is indistinguishable from a real identifier. This is exactly
the failure `AUDIT-014` `TS-13` and `AUDIT-015` predicted and `AUDIT-018` `EO-08` described —
*"an ID guessed correctly in form and wrongly in value is invisible to a resolver"* — except that
here it was guessed correctly in form and **in a value that does not exist at all**, which is why
extraction caught it and would not have caught the `SP-024` case.

**Why it is reported rather than quietly fixed.** It was introduced in `MM-001` §7 — the file that
sets the acceptance standard for the whole category — by the same pass that exists to prevent
unregistered citations. `AUDIT-018` `EO-14` set the precedent for reporting an auditor's own
malformed note.

**Remediation applied.** Rewritten to *"register a new file in the `VB` category, whose identifier
is allocated by the Programme Content Lead from the `VB` growth range under `CG-005` `ID-04` —
**this file does not name a number, because content cites identifiers and never allocates them**
(`ID-07`)"*. **Y1 re-run: 173 distinct, all resolve.**

---

### MM-11 — Three content category codes were used as file-local rule prefixes; 43 instances renamed

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Extraction `Y6` compared every file-local rule prefix against the 21 content
category codes. **`MM-001` used three of them:**

| Prefix as used | Meant | Collides with |
|---|---|---|
| `MD-01`…`MD-06` | Metadata rules | **`MD-001`…`MD-048`** Master Data — 48 files |
| `CM-01`…`CM-08` | Colour management | **`CM-001`…`CM-018`** Change Management — 18 files, **and `CM-R1`…`CM-R10`** maintenance rules |
| `RF-01`…`RF-05` | Raster formats | **`RF-001`…`RF-012`** Reference & Registers — 12 files |

**Why it matters.** `CG-005` §3.2 lists codes that must never be allocated and warns specifically
about confusability; §3.3 **registers the `DM` collision as a real, known problem** requiring
qualification on first use, and records that *"the content space yields the qualification
burden."* **Adding three more collisions in the file that other `MM` files cite most is the
opposite of that discipline** — and `MM-009`, `MM-012`, `MM-002`, `MM-005`, `MM-008` and `MM-011`
were all citing `MM-001 MD-02` and `MM-001 CM-08` across file boundaries.

**Remediation applied.** Renamed throughout — **43 instances across 7 files**:

| Was | Now | Meaning |
|---|---|---|
| `MD-nn` | **`MT-nn`** | Metadata |
| `CM-nn` | **`CS-nn`** | Colour standard |
| `RF-nn` | **`RA-nn`** | Raster |

**Verified:** zero remaining two-digit `MD-`/`CM-`/`RF-` rule references; all three-digit content
IDs (`CM-001`, `CM-005`, `CM-009`, `CM-010`, `CM-016`, `MD-003`…`MD-046`, `RF-006`, `RF-009`)
intact; all 573 links still resolve.

---

### MM-12 — File-local rule prefixes are reused across files by house practice, and no file says so

**Severity: LOW · Status: OPEN · Owner: Programme Content Lead with Enterprise Architecture**

**What was found.** After MM-11's remediation, twelve prefixes remain and **three are reused
elsewhere in the register:**

| Prefix | Used here | Also used by |
|---|---|---|
| `PT-` | `MM-010` — print template, `PT-01`…`PT-52` | **`HC-016` `PT-01`…`PT-28`** (product tour) · **`VB-005` `PT-01`…`PT-06`** (plain-text parity) |
| `EA-` | `MM-011` — email asset, `EA-01`…`EA-50` | **`CG-011` `EA-01`…`EA-09`** (error accessibility) · **`05-04` `EA-01`…`EA-12`** (external access) |
| `AC-` | `MM-001` — accessibility, `AC-01`…`AC-07` | **`VB-004`, `VB-005`, `VB-007`, `VB-009`** all use `AC-` |

**This is established house practice, not a defect.** `VB-004`, `VB-005`, `VB-007` and `VB-009`
already share `AC-`, `BL-`, `CL-` and `T-`, and cross-file citations qualify them — `VB-005`
`CL-01`, `VB-004` `AC-03`. **Every cross-file citation in Category 19 is qualified**, verified by
extraction. **The defect is that the convention is written down nowhere**, so each new author
rediscovers it and an extraction cannot distinguish a qualified reuse from a collision.

**Remediation instruction.** Fold into `AUDIT-015` R-11 and `AUDIT-018` R-12, which already ask
`CG-005` to state the identifier-citation convention in both directions. **Add a third direction:
file-local rule prefixes are file-scoped, are always qualified by their owning file on
cross-reference, and must not reuse a content category code** — which is MM-11 stated as a rule
instead of as a remediation.

---

### MM-13 — Link density is the highest in the register, and check `D1` still passes vacuously elsewhere

**Severity: LOW · Status: FIXED (for this category) · Owner: Programme Content Lead**

**What was found.** Check `D1` at first write: **573 relative markdown links across 12 files, zero
broken** — **47.8 links per file, the highest density in the repository.**

| Category | Links | Files | Per file |
|---|---:|---:|---:|
| 09 `HC` | 172 | 20 | 8.6 |
| 10 `LG` | 380 | 24 | 15.8 |
| 14 `RP` | 89 | 16 | 5.6 *(after `AUDIT-015` remediation)* |
| **15 `AP`** | **0** | 12 | **0 — still open** |
| 17 `OP` | 356 | 16 | 22.3 *(after `AUDIT-017` remediation)* |
| 18 `EO` | 224 | 14 | 16.0 *(after `AUDIT-018` remediation)* |
| **19 `MM`** | **573** | **12** | **47.8** |

**Category 19 is the first category since `AUDIT-013` to be authored above the house band rather
than remediated into it.** One link required correction during authoring — a link to `RF-009`
while Category 99 was still unwritten, which `CG-012` `EX-03` prohibits (*"never link to a planned
document as though it were written"*). It was converted to plain text, and then **converted back
to a link when Category 99 landed** — which is `EX-03` working exactly as intended.

**The check itself is still broken.** `AUDIT-015` RP-13 diagnosed it precisely: *"the check that
found this was a comparison, not a threshold"* — `D1` as written passes vacuously at zero links.
**`AUDIT-015` R-12, `AUDIT-017` OP-22 and `AUDIT-018` R-11 have all asked for a density threshold.
It has not been added, and Category 15 `AP` remains at exactly zero.**

**Remediation instruction.** As `AUDIT-018` R-11, **fourth request**: add a link-density threshold
to `D1`. And remediate Category 15, which is now the only category in the register at zero and has
been since `AUDIT-016`.

---

### MM-14 — Two evidence bases in this category are `class: P3` and both convert on test sets that do not exist

**Severity: LOW · Status: OPEN · Owner: Platform Engineering**

**What was found.** Extraction of every `sources:` block found **four `class: P3` entries**, each
correctly marked and each carrying a conversion note:

| Claim | File | Converts on |
|---|---|---|
| AVIF/WebP support and compression figures | `MM-001` | The §4.11 device and client qualification matrix |
| Email client rendering and dark-mode behaviour | `MM-011` | The §4.9 client test matrix |
| Modern raster formats unreliable in email | `MM-011` | As above |
| The reliable accessible-SVG markup pattern | `MM-003` | The `TS-016` screen-reader pass |
| Bangladesh mobile speed context | `MM-006` | *(not a design input — used only to show a national average is not the design case)* |

**None of the three test sets exists.** `VB-004` §14 records the printer test set as outstanding;
`VB-005` §14 records the email client account set as outstanding; `TS-016` has no named
accessibility reviewer and no Bengali-speaking tester.

**Why it matters.** `VB-005` states the rule for its own P3 sources: *"No template may be approved
on the P3 evidence alone."* **The same rule now binds `MM-001`'s format chain, `MM-011`'s entire
email asset position and `MM-003`'s SVG accessibility pattern** — and all three files record it.
This is honest sourcing under `CG-012` `EV-02`, and it is also **three specifications that cannot
reach `Approved`.**

**Remediation instruction.** Establish the three test sets — printers, email clients, assistive
technology including Bengali — as one Platform Engineering deliverable rather than three. They are
already outstanding against `VB-004`, `VB-005` and `TS-016`; **Category 19 adds a fourth and fifth
dependency on the same absent capability** (`MM-001` `O-07`, `MM-004` `O-06`, `MM-010` `O-03`,
`MM-011` `O-02`).

---

### MM-15 — The register cited an audit report that did not exist; it landed during this audit — the third concurrency instance in one hour

**Severity: LOW · Status: RESOLVED BY EVENT · Owner: Programme Content Lead**

**What was found, and when.** At the enumeration instant — **2026-08-17 18:26 UTC** — Master Index
§1 attributed the 452-of-452 completion figure to **`AUDIT-020` §2**, and `RF-008` cited
**`AUDIT-020` finding `RF99-03`**. **`_AUDIT/` then contained `AUDIT-001` … `AUDIT-019`.
`AUDIT-020` did not exist on disk**, and the finding was raised as the `AF-05` shape — the failure
`AUDIT-001` recorded when `README.md` claimed a benchmark study was *"Complete"* against an empty
folder, and which `CG-012` `EX-01` addresses: *"a claim that an artefact exists is verified by
**checking that it exists**, at the moment of writing."*

**`AUDIT-020_Category_99_RF_Content_Audit.md` was then written by the concurrent session while
this report was being drafted**, and re-enumeration confirms it on disk. **The citation is now
correct and the finding is void as originally written.**

**Why it is retained rather than deleted.** Deleting it would leave this report claiming a
cleanliness it did not observe, and **the sequence is the evidence for R-08.** Within one hour:

| # | Claim | Was true when written | Became false / true by concurrency |
|---:|---|---|---|
| 1 | Nine `MM` files: *"`RF-006` does not exist"* | ✅ | **Became false** — MM-08 |
| 2 | Eight files in five categories: *"Category 19 holds zero files"* | ✅ | **Became false** — MM-08 |
| 3 | **This report: *"`AUDIT-020` does not exist"*** | ✅ | **Became false — against the auditor's own audit** |

**The third instance is the most instructive**, because it happened inside a report whose method
line commits to enumeration over assertion, **and it was still wrong within minutes of being
written.** `AUDIT-018` `EO-14` set the precedent for reporting an auditor's own defect; this is
the same convention applied to an auditor's own *finding*.

**The consequence for slot allocation is unchanged.** `AUDIT-019` was occupied on disk,
`AUDIT-020` was allocated by citation and is now occupied on disk, **and this report is
`AUDIT-021` from its first registration.** No slot was vacated, which is the failure
`AUDIT-014` `TS-03` recorded.

**Remediation instruction.** No action on the citation — it now resolves. **The action is R-08**:
extend proposed rule `RG-08` from counts to claims, in both directions, **and add an
existence-recheck immediately before an audit issues**, because this instance shows the window
between drafting a finding and publishing it is itself long enough to invalidate one. Then index
`AUDIT-001` … `AUDIT-021` in `RF-012`, which now exists.

---

## 4. Inbound obligations discharged — extraction `Y9`

**Eleven files across eight categories delegated something to Category 19.** Each was checked
against what the written file actually contains.

| Delegated by | Delegated | Discharged by | Complete? |
|---|---|---|:--:|
| `CG-011` `AT-08` | Screenshots use sample data with personal data redacted | `MM-002` §4.3, §4.4 | ✅ |
| `CG-008` `U-41`, `HC-c` | The Definition-of-Done media item | `MM-002` §4.4, §4.9 | ✅ |
| `HC-002` `HS-19`, `HS-21` | Sandbox capture, redaction, bilingual alt text | `MM-002` §4.1, §4.4, §4.6 | ✅ |
| `UI-010` `A-07` | Screenshots use sample data, redacted | `MM-002` §4.3 | ✅ |
| **`AP-012` §4.5.6** | **Claim photographs must not contain a person or an identifying document** | **`MM-002` §4.4.3**, including the reflection and second-serial paths | ✅ |
| `TR-003` §4.10, `O-04` | Media resolution, format and compression for storyboards | `MM-001` §4.2, `MM-006` | ✅ |
| `HC-020` `O-01` | The production specification behind 22 scripts | `MM-001` §4.5, `MM-007` | ✅ **specification**; ✖ **resourcing** |
| `VB-007` §10 step 3, §11 | *"Design the glyph to `MM-004`"* | `MM-004` §4.2, §4.9 | ✅ |
| `VB-005` §12 | Asset production specification | `MM-011` | ✅ |
| `VB-004` §15 / `DT-001` §10 | The design deliverable implementing the print standard | `MM-010` | ✅ |
| `UI-006` §7, §10 | Empty-state artwork, decorative with empty alt | `MM-005` §4.4, §4.6 | ✅ |
| `HC-016` | Onboarding animation per external portal | `MM-008` | ✅ |
| `DT-044` §10 | The design deliverable implementing the label contract | `MM-001` class A11, `MM-010` §4.7 | ✅ |
| `EO-012` §4 | Asset delivery standard and repository standard | `MM-001`, `MM-012` | ⚠ **repository yes; identity no** (MM-06) |
| `TS-016` `O-07` | An owning specification for accessible media | `MM-001` §4.7, `MM-002` §4.6, `MM-003` §4.6 | ✅ |
| `CM-005` `O-05`, `CM-009`, `CM-010` | Layout authority for wave, newsletter and deck assets | `MM-010`, `MM-011`, `MM-003` §4.7 | ✅ |
| `SP-003` §4.11 | The visual half of the notation standard | `MM-003` | ✅ |

**Fifteen of seventeen discharged in full. Two are partial and both are reported**: `HC-020`'s
production dependency (MM-02) and `EO-012`'s identity dependency (MM-06).

---

## 5. Remediation applied during this audit

| # | Change | File(s) |
|---:|---|---|
| 1 | **`VB-011` citation removed** — a proposed-but-unallocated identifier, replaced with an allocation instruction that names no number (MM-10) | `MM-001` |
| 2 | **43 rule-prefix instances renamed** — `MD-`→`MT-`, `CM-`→`CS-`, `RF-`→`RA-` (MM-11) | `MM-001`, `MM-002`, `MM-005`, `MM-008`, `MM-009`, `MM-011`, `MM-012` |
| 3 | **12 change-log rows corrected** — `RF-006` from *unwritten* to written, with a relative link (MM-08) | All 12 |
| 4 | **6 Open Items and rules restated** — `RF-006`/`RF-009` from *does not exist* to **read-across obligations with the backlog named** (MM-08) | `MM-001`, `MM-003`, `MM-004`, `MM-010` ×3, `MM-012` |
| 5 | **13 inbound claims corrected across 8 files in 5 other categories** — *"Category 19 holds zero files"*, *"unwritten"*, *"unstarted"* — each restated so the specification gap closes and the substantive gap stays visible (MM-08) | `TR-003`, `HC-002`, `HC-020` ×3, `TS-016`, `CM-005` ×2, `CM-009` ×2, `CM-010` ×2, `EO-012` ×3 |
| 6 | **One `RF-009` link converted to plain text during authoring under `CG-012` `EX-03`, then converted back when Category 99 landed** (MM-13) | `MM-010` |

**Not remediated, deliberately:** the four wave registrations in MM-04. `AUDIT-014` R-02,
`AUDIT-015` R-04 and `AUDIT-018` R-03 all asked for the sequencing basis to be corrected **once,
register-wide**, and `AUDIT-018` explicitly warned against patching file by file after
`AUDIT-010` R-02 did so and the pattern recurred. **Patching four more would be the fourth
repetition of a method already recorded as failed.**

---

## 6. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Sequence `TS-002` ahead of the first help set and course pack; name the redaction verifier; select the redaction tooling.** Until all three exist, **no screenshot may be produced anywhere in the programme** — state that in `CG-008` rather than leaving it implicit in `MM-002` `SC-01` (MM-01) | **Test Lead with Security and Content Design** | **W1 — blocking, absolutely** |
| **R-02** | **Produce a Category 19 production cost envelope — video ×2 series, photography, animation, icons, illustration — and take it to Steering in the same paper as `AF-09`.** Separate the **recurring** screenshot load from the one-off commissions and give it an owner (MM-02) | Content Design Lead and HR Director with Finance | **W1** |
| **R-03** | **Name an accessibility reviewer with authority to block a release, and a Bengali-speaking assistive-technology tester.** Four acceptance gates in this category have no operator, and `PS-04`/`NFR-073` are contractual (MM-03) | Content Design Lead with QA | **W1 — fourth consecutive request** |
| **R-04** | **Correct the register's sequencing basis once, register-wide** (MM-04) — **fourth request**, after `AUDIT-014` R-02, `AUDIT-015` R-04 and `AUDIT-018` R-03. Move **`MM-011` to W1** and **`MM-005` to W1** ahead of that correction, because W1 consumers already cite both as operative | Programme Content Lead | **W1** |
| **R-05** | **Add an asset-specification template variant to `_templates/`, or amend `CG-009` §3 once to permit the declared adaptation** (MM-05) — **sixth request**, superseding `AUDIT-008` R-05, `AUDIT-009` R-09, `AUDIT-010` R-10, `AUDIT-014` R-12 and `AUDIT-018` R-06. **At six occurrences the amendment is the cheaper fix** | Content Design | **W2** |
| **R-06** | **Register the 1000FiX identity standard in `VB` with a Programme-Content-Lead-allocated ID, or adopt `CB-001` by reference** (MM-06) — **second request**, after `AUDIT-018` R-13. `MM-001` declines the home and `EO-012` `CB-03` stays unenforceable | Brand Lead with Programme Content Lead | **W1 — earlier than `R-13`'s W7, because `MM-010` and `MM-011` need identity assets at W1–W2** |
| **R-07** | **Reconcile all 44 `DT` template layout declarations against `MM-010` §4.4 and §4.6 before the print engine is built** (MM-07). Expect `PT-13` to surface `AUDIT-013` `LG-01`'s nine missing `MD-028` fields as a blocked render | Programme Content Lead with Platform Engineering | **W1** |
| **R-08** | **Extend proposed rule `RG-08` from counts to claims**: a category completing while another is in flight re-checks every existence claim it makes about the other, **in both directions**, before its audit issues (MM-08). Neither `AUDIT-018` nor this report would have found it without an explicit extraction | Programme Content Lead | **W1** |
| **R-09** | **Register the photographic consent-and-release form as an `LG` artefact, or record in `CG-002` §4.1 that a class allocation covers files and not the instruments they require** (MM-09). Fold into `AUDIT-016` AP-09 and `AUDIT-018` R-10 — **third distinct shape of the same modelling limit** | Programme Content Lead with Legal Counsel | **W2** |
| **R-10** | **State the file-local rule-prefix convention in `CG-005`** — file-scoped, always qualified on cross-reference, **never reusing a content category code** (MM-11, MM-12). Extends `AUDIT-015` R-11 and `AUDIT-018` R-12 with a third direction | Programme Content Lead with Enterprise Architecture | **W2** |
| **R-11** | **Add a link-density threshold to `D1`** (MM-13) — **fourth request**, after `AUDIT-015` R-12, `AUDIT-017` OP-22 and `AUDIT-018` R-11. **And remediate Category 15 `AP`, which is the only category in the register still at exactly zero** | Programme Content Lead | **W1** |
| **R-12** | **Establish the printer, email-client and assistive-technology test sets as one Platform Engineering deliverable** (MM-14). Five files across three categories now depend on the same absent capability, and **three `MM` specifications cannot reach `Approved` without it** | Platform Engineering | **W2** |
| **R-13** | **Index `AUDIT-001` … `AUDIT-021` in `RF-012`**, which now exists and can finally discharge `CP-11`'s counted-verification requirement (MM-15). The `AUDIT-020` citation resolved during this audit and needs no action | Programme Content Lead | **W1** |

---

## 7. Closure

Category 19 is **complete as specified**: 12 of 12 files written, all seven cross-register
dimensions reconciling exactly, **573 internal links resolving with zero broken**, **173 content
identifiers all resolving**, **525 file-local rules** defined across twelve non-colliding
prefixes, and the `CG-009` §3 deliverable-specification requirement discharged in all twelve.
**Seventeen inbound delegations were checked and fifteen are discharged in full.**

**With Category 99 completing in the same window, the register is written: 452 of 452.**

**Four observations belong in front of the Steering Committee.**

**First, the register is written and almost nothing in it can be executed.** Category 19 is the
clearest instance because it sits at the end of every dependency chain. Its twelve files specify
work that requires a sandbox that does not exist, a budget that does not exist, an accessibility
reviewer who does not exist, a printer test set that does not exist, an email client test set that
does not exist, a DAM that does not exist, and a Chief Data Officer who does not exist. **Every
one of those was recorded by an earlier category before this one was authored.** The programme has
not accumulated documentation debt; it has accumulated **capability** debt, and `AUDIT-017`'s
conclusion about Category 17 — *"the programme has operational content and no operational
capability"* — is now true of the content estate as a whole.

**Second, the highest-consequence file in this category is a data-protection control, and it
cannot be operated.** `MM-002` is `P1` because five files delegate personal-data redaction to it.
Its first rule prohibits capture from production **without a waiver clause, deliberately** — and
its only lawful alternative does not exist. **The failure mode is not that no screenshots get
made; it is that they get made from production under schedule pressure**, by the author least
equipped to judge what is in frame, into an artefact published to 250,000 customers a month, three
months before the Personal Data Protection Act's enforcement machinery activates.

**Third, concurrency has now produced a defect that no amount of careful reading could have
caught — three times in one hour.** Two categories written in the same window each made eighteen
and thirteen false statements about the other's existence, **and this report then made a
fourteenth about an audit that was written while the finding was being drafted.** All three sets
were true when written. **`AUDIT-016` AP-17 proposed a rule for counts; this shows the same
exposure applies to substantive claims and to findings themselves**, and the only thing that found
any of it was extraction run in both directions, twice.

**Fourth, four recommendations are now past the threshold check `G1` sets, and one has been made
six times.** The template variant (six), the sequencing basis (four), the link-density check
(four) and the accessibility reviewer (four). **`G1` asks whether a finding has been open across
three consecutive audits. All four cleared that bar some time ago**, and the register is now
complete, which removes the last reason to defer them: there are no more categories to author
before acting.

| Rule | Status |
|---|---|
| `CM-R1` register-first | ✅ All 12 registered before authoring; zero divergence both directions; **zero unregistered IDs cited after remediation** |
| `CM-R2` figures regenerated by enumeration | ✅ Every figure enumerated at 2026-08-17 18:26 UTC; **the completion total moved 428 → 452 during the window and was re-enumerated rather than inherited** |
| `CM-R8` every claim sourced and dated | ⚠ **Four `class: P3` sources, each correctly marked with a conversion condition** — and all three conversion test sets are absent (MM-14) |
| `CM-R9` audit on category completion | ✅ This report |
| `CP-01` one asset, one file | ✅ Boundaries drawn against `VB-003`…`VB-009`, `DT-001`, `DT-044`, `RP-007`, `RP-014`, `SP-003`, `HC-016`, `HC-020`, `UI-006`, `CG-005`. **`MM-002` §4.4 made the single redaction standard for screenshots and photographs alike, rather than splitting it** |
| `CP-02` IDs permanent, never reused | ✅ Honoured. **This report is `AUDIT-021` from first registration; `AUDIT-019` is on disk and `AUDIT-020` is allocated by citation. No slot vacated** |
| `CP-03` every file declares why it exists | ✅ 12 of 12 |
| `CP-09` templates enforced | ⚠ **Template 17 does not exist; all 12 declare their adaptation** (MM-05) — sixth occurrence |
| `CP-11` counted, not estimated | ✅ Every figure enumerated at a stated UTC instant, including the 53-glyph icon inventory, the 22-state artwork inventory and the 22-script video library — **each derived from its consuming standard, not rounded** |
| `RG-06` never read what a document says about itself | ✅ **Eighteen claims in this category's own files, and thirteen in eight files elsewhere, were found false by extraction and corrected** (MM-08). **A finding in this report was invalidated the same way and is retained with its correction rather than deleted** (MM-15) |
| Gate **F7** category-completion reconciliation | ✅ **Seven dimensions, zero divergence** |
| Check **D1** all internal links resolve | ✅ **573 links, zero broken, at first write.** ⚠ **Still fails as a check** — it passes vacuously at zero, and Category 15 is still at zero for the fourth audit running |
| Check **G1** findings open across three audits | ⚠ **Four recommendations past the threshold: R-05 template variant (6th), R-04 sequencing basis (4th), R-11 link-density check (4th), R-03 accessibility reviewer (4th)** |

> **Index note.** This report and `AUDIT-001` through `AUDIT-019` must be indexed in `RF-012`,
> which **now exists** — Category 99 completed in this window. `RF-006` also now exists, and
> **`AUDIT-017` OP-12's ninety-four open decisions, plus every `MM` format, tooling, licence and
> retention decision, must be entered into it.** The log was created in this register specifically
> so content would not repeat the module repository's missing `00-05` (`AF-04`). **It exists. The
> entries do not. That is the last opportunity, and it is still open.**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
