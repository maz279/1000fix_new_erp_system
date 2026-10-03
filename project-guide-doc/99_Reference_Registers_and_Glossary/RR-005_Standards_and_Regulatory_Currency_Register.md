---
id: RR-005
title: Standards and Regulatory Currency Register
category: 99 — Reference, Registers & Glossary
code: RR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture
approver: Chief Technology Officer
standards_basis: ISO 10007:2017 §5.3 (configuration identification of referenced items) · ISO 19011:2018 §6.4 (evidence and verification) · ISO 37301:2021 §4.5, §8.1 (compliance obligations register) · ISO 9001:2015 §7.5.3.2 (control of external documented information) · ISO/IEC 11179-6:2023 §7 (registration status)
traces_to: PGD-000 Category 99 RR-005 · PGD-000 §2.1 row 21 · PGD-000 §3 "Standards citation corrected (PGD-A2-07)" · _CATEGORY_OVERVIEW "RR-005 prevents a second class of finding" · 00-06 §9, §10 · 00-06 C-04, C-04a, H-01, M-01 · SC-008 · RF-008 SR-01…SR-04 · DoD-17 · QAA-04
depends_on: PGD-000 · RR-002 · RR-003 · RR-004
verified_on: 2026-08-19
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
enumeration_timestamp: 2026-08-19 19:54 (repository wall clock — see §4.4)
rule_prefix: CUR — verified to return zero occurrences in identifier form across all 792 markdown files of the workspace before allocation, at 2026-08-19 19:54. Candidates STC, RCY and SRG were also free; SRG was rejected as visually close to SRC-nnn, the legacy-source space carrying 566 occurrences
review_cycle: Every wave gate, and on any entry whose next_review falls due — §9
---

# RR-005 — Standards and Regulatory Currency Register
# 1000FiX ERP System & Portal Suite v2.0

### Category 99 · Code `RR` · ISO 10007:2017 · ISO 19011:2018 · ISO 37301:2021

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 99 as `RR-005`,
>    status ⛔, priority **P0**, needed by **Now**. It was registered before it was written.
> 2. **`PG-03` / `RG-06` Count, do not consult.** Every figure in §4 and §5 was counted from the
>    filesystem at **2026-08-19 19:54**, by the commands printed in §4.1.
> 3. **`PG-06` Cite standards.** ISO 10007:2017 §5.3, ISO 19011:2018 §6.4 and ISO 37301:2021 §8.1
>    govern. Departures are declared in §2.1.
> 4. **`PG-M4` Verify citations.** This is the document that *is* `PG-M4`. Every row in §5, §6 and
>    §7 carries a **verification source** and a **verified-on date**, and eleven rows carry a
>    correction because the verification failed.

---

## 1. Purpose

Three of the most serious findings in the 1000FiX audit history are the same control failure
wearing three costumes: a citation was correct when written, the world moved, and nobody
re-checked. `00-06` **C-04** cited the Digital Security Act 2018, repealed twice by then.
`00-06` **H-01** cited NIST SP 800-88 Rev. 1, withdrawn. `00-06` **M-01** gave Odoo 19 the wrong
release month. `00-06` §9 proposed the fix — *"every statutory and standards citation carries a
verified-on date and is re-verified at each wave gate"* — and it has been a proposal ever since.

**This register is that fix, executed for the engineering estate.** It names every standard,
statute, regulation, framework and vendor version the 133 guiding documents rely on; states which
edition is current at the verification date; states which the estate actually cites; and where
those differ, says so and assigns the correction to a named owner with a date.

It also does the thing a currency register exists to do and a one-off audit cannot: it puts a
**next-review gate** on every row, so that the next time the world moves the programme finds out
from a scheduled check rather than from an auditor.

**Eleven currency defects were found by writing it.** Three are material and new to this estate:
Bangladesh's cyber-security statute has moved a **third** time and the engineering estate cites the
superseded instrument in 22 files; **IEEE 1016-2009 — the governing standard for `AR-003` and one
of `PGD-000`'s own thirteen bases — is Inactive-Reserved at IEEE SA**; and **PCI DSS v4.0, retired
on 31 December 2024, is still the cited version** in the payment-integration chain.

> **On novelty, stated honestly.** `project_content/99_.../RF-008` is the **content** estate's
> equivalent register, issued 2026-08-18, registering 44 instruments and 6 methodologies. It
> already found the ISO 9001:2026 supersession and the repealed-cyber-instrument class. This
> register does not claim either as new; §5.10 records the overlap, and the fact that three `RR`
> documents were drafted without knowing `RF-008` existed is itself a finding — `RR-004`
> `EVR-F-07`.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | Every **international and national standard** cited anywhere in `project-guide-doc/`, with current edition, cited edition and delta |
| 2 | Every **Bangladesh statute, ordinance and regulator instrument** the platform must satisfy, with its succession chain |
| 3 | Every **industry framework** relied on as a normative basis — ITIL, PMBOK, PRINCE2, TOGAF, OWASP, ACMP, Kirkpatrick, SLSA, SPDX, CycloneDX, OpenChain |
| 4 | Every **vendor and product version claim** load-bearing on the architecture — Odoo above all |
| 5 | The **verification protocol**: what counts as evidence, who may record it, how long it is good for |
| 6 | The **review calendar**, bound to `GV-009` wave gates rather than to the calendar month |
| 7 | The **enforcement checks** that make a stale citation mechanically detectable |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The **content** estate's external references | `RF-008` | Issued 2026-08-18, 44 instruments, currently maintained. Referenced and reconciled in §5.10; **not restated** |
| The **compliance obligation** — who must do what, by when | `SC-008` | This register answers *"is the citation current?"*; `SC-008` answers *"are we compliant?"*. A current citation of a law nobody obeys is still a finding, and it is `SC-008`'s |
| **Internal** sources — the 792 workspace files | `RR-004` | An external source has a publisher and an edition; an internal one has a path and a baseline |
| Licence obligations of third-party components | `CO-004`, `BE-007` | Licence currency is a dependency question, tracked in the SBOM |
| **Legal interpretation** of any statute | External counsel, via `GV-005` `DEP-31` | This register records the instrument, its date and its status. It does not advise on it, and §6 says so on every row |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Document authors** | Before writing `standards_basis:` — §5 is the authoritative citation form, with its edition |
| **Auditors** | The one place a citation's currency can be checked without re-doing the research |
| **CTO / Steering Committee** | §8's eleven defects, three of which need a decision this quarter |
| **Quality Manager** | §5.2 — the ISO 9001 transition, which lands inside Wave 1 |
| **Security & Privacy Lead** | §6.1's succession chains and §6.2's residency provision |
| **External counsel** | §6, as the programme's statement of which instruments it believes are in force, for confirmation |
| **The vendor** | §7 — the product versions the contract is written against |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 10007:2017** *Configuration management* | §5.3 Configuration identification | Every externally-referenced item is a configuration item with an identity (`ISO nnnnn:yyyy`), a version (the edition) and a change record — §5's *Cited* vs *Current* columns | None. Extending §5.3's *"documents referenced by the configuration information"* to referenced external items is its natural reading |
| **ISO 19011:2018** *Auditing management systems* | §6.4.3, §6.4.7 | §3.3 defines four evidence classes and requires the **publisher's own catalogue** for any §5 status claim. Secondary sources are recorded as such | 19011 assumes an audit programme. This register is maintained by authors as a side effect of writing; §9 assigns one reviewer role and a cadence in its place. Declared |
| **ISO 37301:2021** *Compliance management* | §4.5, §8.1 | §6 is a compliance-obligations register in 37301's sense: obligation source, instrument, status, owner, review date | §6 records obligations' **sources**, not the obligations. The obligation set is `SC-008`'s. Boundary in §1.1 |
| **ISO 9001:2015** *Quality management* | §7.5.3.2 control of external documented information | *"Documented information of external origin … shall be identified as appropriate, and controlled."* This register is that identification | None — and note the recursion: **the standard governing this register is itself in §5.2 with a supersession date 28 days out** |
| **ISO/IEC 11179-6:2023** | §7 Registration status | §3.2's five currency states specialise 11179-6's registration-status lifecycle to external items | An extension. `RR-002` §3.5 and `RR-004` §3.2 apply the same model, deliberately, so a reader learns it once |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `00-06` §9, §10 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_*.md` | Proposes this register; supplies `C-04`, `C-04a`, `H-01`, `M-01` and the original verification-source table |
| **`RF-008`** | `../../project_content/99_Reference_and_Registers/RF-008_External_Standards_and_Regulatory_Reference_Register.md` | The content estate's equivalent — **44 instruments, 6 methodologies, findings `SR-01`…`SR-04`**. Method adopted; §5.10 reconciles |
| `RF-002` §4.7 | `../../project_content/99_Reference_and_Registers/RF-002_*.md` | `EV-F1` — sixty-eight content files with a future verification date. Re-run against this estate in `RR-004` §5.7.3 |
| `SC-008` | `../05_Security_Privacy_and_Compliance/SC-008_*.md` | The obligations resting on §6's instruments |
| `QA-001`, `QA-008` §3 | `../08_Quality_Engineering_and_Test/` | The WCAG 2.2 / ISO/IEC 40500:2025 position — verified here and adopted unchanged |
| `RL-006` | `../12_Release_Deployment_and_Transition/RL-006_*.md` | Written on NIST SP 800-88r2 and IEEE 2883:2022 from the outset — the estate's first document to get `H-01` right by construction |
| `RR-002` §5, §7.2 | `./RR-002_Identifier_Convention_Standard.md` | Identifier forms and the `rule_prefix:` collision-check procedure, followed here |
| `RR-004` §5.7 | `./RR-004_Source_Document_Index_and_Evidence_Register.md` | Internal path and reference integrity — the internal counterpart of this register's external verification |
| `PGD-000` §3 | `../PGD-000_*.md` | The `Basis` line — thirteen standards, one of which this register finds Inactive-Reserved |
| Publishers' own catalogues | iso.org · standards.ieee.org · csrc.nist.gov · w3.org · pcisecuritystandards.org · owasp.org | **Primary evidence** for every §5 status claim. URLs in §15 |
| Bangladesh press and policy trackers | Prothom Alo · The Business Standard · Dhaka Tribune · BSS · Digital Policy Alert | **Secondary** evidence for §6, recorded as such. `CUR-Q-01` escalates gazette confirmation to counsel |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| `00-06` **C-04 / C-04a** *(critical)* | Digital Security Act 2018 cited after two repeals | §6.1 carries the chain **to a third repeal the engineering estate has not recorded** — `CUR-F-01`. The *diagnosis* closes; the remediation is 22 files, assigned |
| `00-06` **H-01** | NIST SP 800-88 r1 cited after withdrawal | §5.6 records r1 **withdrawn 26 September 2025**, r2 published the same day, and IEEE 2883-2022 + **IEEE 2883.1-2025** as the technique authorities r2 defers to. Closed in diagnosis; **8 r1 citations survive**, `CUR-F-06` |
| `00-06` **M-01** | *"Odoo 19 released October 2025"* | §7.1 records **18 September 2025**, and adds what matters more: **Odoo 20 is expected 24–26 September 2026**, five weeks out. Closed and extended |
| `00-06` §9's proposal | *"re-verified at each wave gate"* | §9 is that calendar, gate-bound. Closed **in specification**; it closes in fact at the first executed review |
| `PGD-A2-07` | *"ISO/IEC 38500 (IT governance)"* with no edition | §5.2 registers **ISO/IEC 38500:2024 edition 3**. Generalised: `CUR-F-07` counts **twelve** heavily-cited items with no edition at all |
| `DoD-17` | *"a verified-on date on every regulatory citation"* | 130 of 130 documents carry `verified_on:`. §4.3 measures what that is worth |
| `QAA-04` | `05-06` §11 and `TS-016` say WCAG 2.1; `QA-001` says 2.2 | Not closed here — `QA-008` §3's ruling is adopted. §5.4 records both citation populations so the residual edit list is visible |
| `RF-008` `SR-02` | Six content files cite a repealed instrument | Same defect class, different estate. §6.1 measures the engineering estate: **22 files**. Cross-referenced, not duplicated |

---

## 3. How This Register Works

### 3.1 The row schema

Eight columns. A row missing any of them is a note, not a register entry.

| Column | Meaning |
|---|---|
| **Item** | The externally-published item, in its authoritative citation form |
| **Current edition** | What the publisher's own catalogue says is in force at the verification date |
| **Cited in estate** | The edition the repository actually cites, with the occurrence count |
| **Status** | Per §3.2 |
| **Where it bites** | The `PGD` document(s) whose conformance claim depends on this item |
| **Verified** | The date the *Current edition* column was checked against a primary source |
| **Src** | Primary (`P`) or secondary (`S`) evidence — §3.3 |
| **Next review** | The gate at which this row is re-checked — §9 |

### 3.2 Currency states

| Symbol | State | Meaning | What it obliges |
|:--:|---|---|---|
| ✅ | **Current** | Cited edition is the edition in force | Nothing. Re-verify at next review |
| ⏳ | **Current — successor announced** | In force, with a confirmed publication or effective date for its replacement | A dated transition plan before the successor's effective date |
| ⚠ | **Stale citation** | The estate cites a superseded but still-published edition | Edit list, owner, date. The conformance claim is **not void**, but it is measured against the wrong text |
| ⛔ | **Withdrawn or repealed** | The cited item has been withdrawn, retired or repealed | The conformance claim built on it is **void**. A defect, not a tidy-up |
| ◐ | **Undated citation** | Cited with no edition at all | **Unfalsifiable.** Cannot be verified, therefore cannot be conformed to. `PGD-A2-07`'s class |

> **⛔ and ◐ are the two that matter.** ⛔ voids a claim. ◐ makes a claim untestable — which is
> worse in one specific way: a ⛔ is found by an auditor in an afternoon; a ◐ is found by nobody,
> because there is nothing to check it against.

### 3.3 Evidence classes

| Class | What it is | Acceptable for | Not acceptable for |
|:--:|---|---|---|
| **P1** | The publisher's own catalogue or standard page — `iso.org/standard/nnnnn.html`, `standards.ieee.org`, `csrc.nist.gov`, `w3.org` | Any status claim, including ⛔ | — |
| **P2** | The publisher's own announcement, press release or blog | Any status claim | Effective dates, where catalogue and announcement differ |
| **S1** | A national body reselling the item — BSI, ANSI, DIN, SIS, IEC Webstore | Existence and edition date | **Withdrawal status.** Resellers routinely list withdrawn editions |
| **S2** | Reputable press, law-firm briefings, policy trackers | **§6 Bangladesh statutes only**, where no online primary gazette is reliably reachable | Anything in §5 |

> **Rule `CUR-03`.** A §5 row may not rest on S-class evidence. A §6 row may, must say so, and
> must carry an open question to counsel. Every S-class row in this issue is in `CUR-Q-01`.
>
> **`RF-008` §4.8 makes the sharper version of this point and it is adopted here:** of its 44
> instruments, **1 has a controlled programme copy**. The same is true of this register — every
> status below rests on published text read on the verification date, not on a version-stamped
> instrument the company holds. That is adequate for currency tracking and **not adequate for a
> statutory filing**, which is why §6 carries `CUR-Q-01` rather than a clean bill.

### 3.4 The rules

| # | Rule | Enforced by |
|---|---|---|
| `CUR-01` | **Every citation of an external item carries its edition or year.** `ISO 9001` is not a citation; `ISO 9001:2015` is | `CHK-C1` |
| `CUR-02` | **Every document citing a statute, standard or vendor version carries `verified_on:`**, and the date is when the *citation* was checked, not when the document was written | `CHK-C2` |
| `CUR-03` | **A §5 row rests on P-class evidence.** §6 may rest on S-class and must declare it | Row inspection |
| `CUR-04` | **A ⛔ row voids the conformance claim built on it.** The claim is restated or withdrawn, not left standing with a footnote | Gate review |
| `CUR-05` | **The estate cites one edition of one item.** Where two are cited, one is the ruling edition and the other is an edit list with an owner | `CHK-C3` |
| `CUR-06` | **A `verified_on` date in the future is a defect**, not a plan | `CHK-C4`, `RF-002` `EV-F1` |
| `CUR-07` | **`next_review` is a gate, not a date.** Calendar reviews slip silently; gates have someone standing at them | §9 |
| `CUR-08` | **A successor with a confirmed publication date is registered before it publishes**, not after | §5, ⏳ rows |
| `CUR-09` | **No document claims conformance to a standard it does not cite by edition** — the ◐ prohibition | `CHK-C1` |
| `CUR-10` | **This register is re-verified in full at every wave gate**, and every row's verification date moves or the row is marked lapsed | §9 |

---

## 4. The Measured Position

### 4.1 Method

```bash
# The external-citation population. Note the digit ranges: an under-specified
# pattern under-reports silently — it does not error.
grep -rhoE '(ISO(/IEC)?(/IEEE)? ?[0-9]{3,5}(-[0-9]+)?(:[0-9]{4})?|IEEE [0-9]{3,5}(\.[0-9])?(-[0-9]{4})?|NIST SP [0-9]{3}-[0-9]+[A-Za-z0-9]*|WCAG ?[0-9]\.[0-9]|PCI[ -]DSS( v?[0-9.]+)?|RFC ?[0-9]{3,4})' \
  --include='*.md' project-guide-doc | sed 's/  */ /g' | sort | uniq -c | sort -rn

# Documents carrying a verification date, and the distinct values
grep -rh '^verified_on:' --include='*.md' project-guide-doc | sed 's/verified_on: *//' \
  | sort | uniq -c

# Statutory citations, case-folded
grep -rhoiE 'cyber security (act|ordinance|bill)[, ]*20[0-9]{2}' --include='*.md' \
  project-guide-doc | tr 'A-Z' 'a-z' | sort | uniq -c
```

> ### A caution about the first command, recorded because it happened
>
> The first pattern drafted for this register capped IEEE numbers at four digits —
> `IEEE [0-9]{3,4}`. It reported three standards that do not exist: **`IEEE 2911`, `IEEE 2914` and
> `IEEE 4201`.** They are `IEEE 29119`, `IEEE 29148` and `IEEE 42010`, truncated by the author's own
> regex.
>
> **The pattern did not fail. It reported a smaller, wrong world, confidently.** This is `RF-001`
> §4.3 `GL-02` — the two-segment regex that silently dropped all 34 `SRM2` requirements — recurring
> in a different estate, and `RR-004` §4.1 records a third instance from the same afternoon. It is
> the argument for printing the pattern next to the number, every time.

### 4.2 The counted position

| Measure | Counted 2026-08-19 19:54 | Comparison |
|---|---:|---|
| Markdown files in the workspace | **792** | `PGD-000` §3 records 782 at 02:41 |
| Markdown files in `project-guide-doc/` | **171** | `PGD-000` §3 records 161 |
| Guiding documents on disk | **133** | `PGD-000` §0.5 records **119** authored |
| Distinct external-citation **forms** in `project-guide-doc/` | **248** | Not previously counted anywhere |
| Distinct **items** behind those forms, after normalising editions | **≈150** | — |
| Items registered individually in §5, §6, §7 | **118** | The remainder are single-citation RFCs and benchmarks, registered by family in §5.8 |
| Guiding documents carrying `verified_on:` | **130 of 130** | 100% — `DoD-17` met |
| Distinct `verified_on` values in the estate | **2** — `2026-08-18` (97), `2026-08-19` (34) | §4.3 |
| Distinct items named in `standards_basis:` front matter | **68** | The normative subset |
| Instruments registered by `RF-008` for the content estate | **44** + 6 methodologies | §5.10 |

### 4.3 What the 100% `verified_on` compliance is actually worth

**Every one of the 130 guiding documents carries `verified_on:`.** That is a genuine and unusual
achievement and `DoD-17` is met. Measured honestly, it is worth less than it looks:

| Observation | Figure | Consequence |
|---|---:|---|
| Distinct `verified_on` values in the estate | **2** | Every document was verified on the day it was written, and **no document has ever been re-verified** |
| Documents whose `verified_on` equals their `date` | **130 of 130** | `verified_on` is currently a synonym for `date`. It carries no independent information |
| Documents carrying a `next_review` or `review_cycle` | **3** — `RR-003`, `RR-004`, this one | Nothing else schedules a second verification |
| Age of the oldest verification at this issue | **1 day** | Which is why nothing has gone stale *yet*, and why the control has never been tested |

> ### `CUR-F-08` — the estate has a verification *date* and no verification *cycle*
>
> `DoD-17` asked for a date and got one, 130 times. What it did not ask for — and what `00-06` §9
> actually proposed — is **re-verification at each wave gate**. Until §9 executes once,
> `verified_on` records that somebody looked, once, on the day they were writing anyway.
>
> **The test is cheap and it is `CHK-C2`.** Run today it passes 130 of 130 — the estate is one day
> old. Run at `G1` it fails all 130 unless §9 has run, which is exactly what it is for.
>
> **Severity Medium**, and rising by one day per day.

### 4.4 A note on the timestamps in this repository

Every timestamp in `project-guide-doc/` carries the suffix `(+06)` — Bangladesh Standard Time,
correct for 1000FiX Services Limited, Dhaka. The host that produced these files reports its offset
as **+08:00**:

```
$ date "+%Y-%m-%d %H:%M %z"
2026-08-19 19:54 +0800
```

The wall-clock values recorded across the estate are therefore the **host's local time, labelled
with the business's timezone**. If the host clock is right, every `(+06)` label in this repository
is two hours off; if the host is misconfigured to a neighbouring zone, the labels are right and the
host is wrong. **This register cannot tell which**, and says so rather than silently picking one.

This issue therefore stamps its enumeration as *repository wall clock* and raises `CUR-Q-05`. It is
a small thing with one sharp edge: **`MG-006`'s cutover runbook and `RL-002`'s deployment windows
are written in `T−n` against wall-clock instants**, and a two-hour ambiguity in a freeze window is
not a documentation defect, it is an outage.

---

## 5. The Standards Register

Occurrence counts are for `project-guide-doc/` at the enumeration timestamp.

### 5.1 Systems and software engineering — the estate's spine

| Item | Current edition | Cited in estate | Status | Where it bites | Verified | Src | Next review |
|---|---|---|:--:|---|---|:--:|---|
| **ISO/IEC/IEEE 29148** Requirements engineering | **2018** (2nd ed.); ISO records it **under revision** | `:2018` × 80 | ⏳ | `RQ-001`, `RQ-002`, `RQ-005`, `RQ-006`, `RQ-008` | 2026-08-19 | P1 | `G1` |
| **ISO/IEC/IEEE 42010** Architecture description | **2022** | `:2022` × 54, undated × 10 | ✅ ◐ | `AR-001`, `AR-002`, `AR-008` | 2026-08-19 | P1 | `G2` |
| **IEEE 1016** Software design descriptions | **1016-2009 — Inactive-Reserved** at IEEE SA | `1016-2009` × 25, `1016` × 11 | ⛔ | **`AR-003`**, and `PGD-000` §3 *Basis* | 2026-08-19 | P1 | **Now** |
| **ISO/IEC/IEEE 12207** Software life cycle processes | **2017** | `:2017` × 15 | ✅ | `BE-006`, `GV-011`, `RR-003` | 2026-08-19 | P1 | `G2` |
| **ISO/IEC/IEEE 15288** System life cycle processes | **2023** | `:2023` × 6 | ✅ | `AR-002`, `RQ-002` | 2026-08-19 | P1 | `G2` |
| **ISO/IEC/IEEE 15289** Information item content | **2019** | cited in `RR-003`, `RR-004` | ✅ | `RR-003` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC/IEEE 24765** Systems & software vocabulary | **2017** | `:2017` × 3 | ✅ | `RR-001` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC/IEEE 1044** Classification of anomalies | **2009** | `:2009` × 5 | ✅ | `QA-010` | 2026-08-19 | P1 | `G3` |
| **IEEE 1012** Verification and validation | **2016** (+2017 corrigendum) | `1012` × 4, undated | ◐ | `QA-001` | 2026-08-19 | P1 | `G2` |

> ### `CUR-F-03` — `IEEE 1016-2009` is Inactive-Reserved, and it is `AR-003`'s governing standard
>
> **What was found.** IEEE Standards Association lists **IEEE 1016-2009** as an **Inactive-Reserved
> Standard**. In IEEE SA's own words, inactive-reserved standards *"have been removed from active
> status through a ballot where the standard is made inactive as a consensus decision of a
> balloting group."* The text remains purchasable and citable; **it is not maintained.**
>
> **Why it matters.** `IEEE 1016-2009` is:
>
> - the `standards_basis:` of **`AR-003` Software Design Description**, the document from which all
>   93 design units derive, and item 5 on `PGD-000` §2.1's critical path;
> - one of thirteen standards on **`PGD-000` §3's `Basis` line** — the register's own statement of
>   authority;
> - cited **36 times** in this repository, 25 with the edition and 11 without;
> - a `standards_basis` entry of **`RR-003`**, the document that sets the section set every design
>   document is measured against.
>
> **This is `H-01` exactly** — *"NIST SP 800-88 r1 withdrawn"* — same shape, same class, different
> publisher, found by the same method four days later. That is the argument that `00-06` §9's
> control was never the problem and its non-execution was.
>
> **What it does *not* mean.** Inactive-Reserved is not *wrong*. IEEE 1016-2009's ten design
> viewpoints remain the most usable published decomposition of an SDD, and **no successor exists** —
> ISO/IEC/IEEE 42010:2022 covers architecture description, not detailed design, and does not
> replace it. **The correct remediation is not to change standard. It is to stop claiming
> conformance to a maintained standard that is not maintained.**
>
> **Remediation.** `AR-003`, `RR-003` and `PGD-000` §3 restate the basis as *"IEEE 1016-2009
> (Inactive-Reserved; adopted as the design-viewpoint taxonomy, no successor published — see
> `RR-005` §5.1)"*. Owner **Enterprise Architecture**, **Now**. **Severity High.**

### 5.2 Management systems — and the one that republishes in 28 days

| Item | Current edition | Cited in estate | Status | Where it bites | Verified | Src | Next review |
|---|---|---|:--:|---|---|:--:|---|
| **ISO 9001** Quality management | **2015** — **ISO 9001:2026 publishes 16 September 2026**; DIS 27 Aug 2025, FDIS balloted mid-April 2026; ~3-year transition to autumn 2029 | `:2015` × 146; **`:2026` × 0 before `RR-003`** | ⏳ ◐ | `GV-010`, `QA-001`, `CH-001`, `CH-002`, `RL-005`, and the **footer of 14 documents in this repository** | 2026-08-19 | P2 | **Now** |
| **ISO/IEC 20000-1** Service management | **2018** | `:2018` × 53, undated × 11 | ✅ ◐ | `SV-001`, `SV-002`, `SV-006` | 2026-08-19 | P1 | `G3` |
| **ISO 22301** Business continuity | **2019** | `:2019` × 16, undated × 8 | ✅ ◐ | `PE-007` | 2026-08-19 | P1 | `G3` |
| **ISO 10007** Configuration management | **2017** | `:2017` × 32, undated × 12 | ✅ ◐ | `GV-011`, `RR-002`, `RR-004`, this document | 2026-08-19 | P1 | `G3` |
| **ISO 31000** Risk management | **2018** | `:2018` × 13 | ✅ | `GV-005` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC 38500** Governance of IT | **2024** (3rd ed.) | `:2024` × 13, undated × 5 | ✅ ◐ | `GV-002`, `PGD-000` §3 | 2026-08-18 | P1 | `G3` |
| **ISO 19011** Auditing management systems | **2018** | `:2018` × 14, undated × 4 | ✅ ◐ | `GV-010`, `RR-004`, this document | 2026-08-19 | P1 | `G4` |
| **ISO 21500** PPP context | **2021** | `:2021` × 11 | ✅ | `GV-001`, `CH-003` | 2026-08-19 | P1 | `G4` |
| **ISO 21502** Project management guidance | **2020** | `:2020` × 110, undated × 5 | ✅ ◐ | 11 documents' `standards_basis` | 2026-08-19 | P1 | `G4` |
| **ISO 21503** Programme management | **2022** | `:2022` × 19 | ✅ | `GV-004` | 2026-08-19 | P1 | `G4` |
| **ISO 30401** Knowledge management | **2018** | `:2018` × 5, undated × 4 | ✅ ◐ | `SV-003` | 2026-08-19 | P1 | `G4` |
| **ISO 10015** Competence & training | **2019** | `:2019` × 16 | ✅ | `CH-002` | 2026-08-19 | P1 | `G4` |
| **ISO 10018** People engagement | **2020** | `:2020` × 16, **`:2012` × 4** | ⚠ | `CH-001`, `CH-005` | 2026-08-19 | P1 | `G2` |
| **ISO 37301** Compliance management | **2021** | undated × 4 | ◐ | `SC-008`, this document | 2026-08-19 | P1 | `G3` |
| **ISO 15489-1** Records management | **2016** | `:2016` × 11, undated × 5 | ✅ ◐ | `DA-006`, `GV-011`, `RR-004` | 2026-08-19 | P1 | `G4` |

> ### `CUR-F-02` — ISO 9001 republishes on 16 September 2026, twenty-eight days from this issue
>
> **Attribution first.** `RF-008` **already found this** for the content estate, recording *"38
> files cite 2015 clauses; no transition plan exists"*. It is **not new to the programme**. It is
> new to the **engineering** estate, where it has a different and larger exposure, and it is the
> clearest available demonstration of `RR-004` `EVR-F-07`: two currency registers, one finding,
> discovered twice.
>
> **The engineering exposure, counted:**
>
> | Exposure | Detail |
> |---|---:|
> | `ISO 9001:2015` citations in `project-guide-doc/` | **146** |
> | Guiding documents naming it in `standards_basis:` | **6** |
> | Documents carrying *"ISO 9001:2015 Certified"* in the **footer** | **14** in this repository, **25** across the workspace |
> | Guiding documents citing `ISO 9001:2026` before `RR-003` | **0** |
>
> **The footer is the part that is not a citation.** *"ISO 9001:2015 Certified"* is a **certification
> claim about the company**, printed on 25 files. It is accurate today and acquires an expiry on
> 16 September 2026 — not immediately false, because the certificate remains valid through a
> three-year transition, but a claim nobody has dated.
>
> **The timing is the finding, not the content.** A three-year transition is generous. The defect is
> that publication lands **inside Wave 1**, and a programme baselining its quality documents in
> August baselines them against a standard superseded in September.
>
> **Remediation.** Three acts, none expensive:
> 1. Register the successor — done, this row, ⏳.
> 2. `GV-010` adds a transition item with the 2029 outer date and the surveillance audit at which
>    the certification body first asks. Owner **Quality Manager**, **W1**.
> 3. The 146 citations gain nothing; the **undated** ones are the real work, and they are
>    `CUR-F-07`'s.
>
> **Severity High**, on timing rather than content.

### 5.3 Security, privacy and cryptography

| Item | Current edition | Cited in estate | Status | Where it bites | Verified | Src | Next review |
|---|---|---|:--:|---|---|:--:|---|
| **ISO/IEC 27001** ISMS | **2022** (+ **Amd 1:2024**, climate action) | `:2022` × 65, undated × 41 | ✅ ◐ | `SC-001`, `SC-005`, `SC-009` | 2026-08-19 | P1 | `G2` |
| **ISO/IEC 27002** Controls | **2022** | `:2022` × 6 | ✅ | `SC-001` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC 27005** InfoSec risk management | **2022** | `:2022` × 6 | ✅ | `SC-002` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC 27701** PIMS | **2025** — 2nd ed., **standalone management-system standard**, published **14 October 2025** | `:2025` × 10, undated × 3 | ✅ ◐ | `SC-003`, `DA-005` | 2026-08-19 | P1 | `G2` |
| **ISO/IEC 29134** Privacy impact assessment | **2023** | `:2023` × 11, **`:2017` × 3** | ⚠ | `SC-003` | 2026-08-19 | P1 | `G2` |
| **ISO/IEC 29100** Privacy framework | **2024** | `:2024` × 3 | ✅ | `SC-003` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC 19790** Cryptographic modules | **2025** — 3rd ed., published **26 February 2025** | **undated × 25** | ◐ | `SC-006` | 2026-08-19 | P1 | **W1** |
| **ISO/IEC 20889** De-identification | **2018** | `:2018` × 6, undated × 6 | ✅ ◐ | `QA-004`, `DA-005` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC 27031 / 27037 / 27040 / 27041 / 27018 / 27035-1** | 2011 · 2012 · 2015 · 2015 · 2019 · 2023 | mixed, mostly undated | ◐ | `SC-010`, `SC-011`, `PE-007` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC 42001** AI management systems | **2023** | `:2023` × 5 | ✅ | `AR-011` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC 23894** AI risk management | **2023** | `:2023` × 5 | ✅ | `AR-011` | 2026-08-19 | P1 | `G3` |

> **`ISO/IEC 19790` is cited 25 times and dated zero times**, while its third edition published in
> February 2025 and materially revised the 2012 text. `SC-006` is a cryptography and key-management
> **standard**; a standard whose own basis is undated cannot state which security levels it
> requires. This is the single worst ◐ in the register and is called out separately in `CUR-F-07`.

### 5.4 Accessibility and human-centred design — the family the estate already got right

| Item | Current edition | Cited in estate | Status | Where it bites | Verified | Src | Next review |
|---|---|---|:--:|---|---|:--:|---|
| **WCAG** | **2.2**, W3C Rec. 5 Oct 2023, updated 12 Dec 2024; adopted as **ISO/IEC 40500:2025** on **21 October 2025** | `2.2` × 135, **`2.1` × 26** | ⚠ | `UX-005`, `QA-008` | 2026-08-19 | P1 | `G2` |
| **ISO/IEC 40500** | **2025** (= WCAG 2.2) | `:2025` × 11 | ✅ | `UX-005`, `QA-008` | 2026-08-19 | P1 | `G3` |
| **EN 301 549** | **V3.2.1 (2021-03)** | undated × 14 | ◐ | `QA-008` | 2026-08-19 | S1 | `G3` |
| **ISO 9241-210** Human-centred design | **2019** | `:2019` × 21, undated × 7 | ✅ ◐ | `UX-001`, `UX-004` | 2026-08-19 | P1 | `G3` |
| **ISO 9241-11** Usability definitions | **2018** | `:2018` × 9, undated × 4 | ✅ ◐ | `UX-008` | 2026-08-19 | P1 | `G4` |
| **ISO 25062** CIF for reporting usability evaluations | **2025** — **replaces ISO/IEC 25062:2006** | `ISO 25062:2025` × 14, **`ISO/IEC 25062:2006` × 4** | ⚠ | `UX-008` | 2026-08-19 | P1 | `G2` |
| **ISO/IEC 25066** Usability evaluation reports | **2016** | `:2016` × 5 | ✅ | `UX-008` | 2026-08-19 | P1 | `G4` |
| **WCAG 3.0** | **Working Draft — not a Recommendation** | `3.0` × 4 | ✅ | `UX-005` (horizon only) | 2026-08-19 | P1 | `G4` |

> **This family is the estate's best currency work and it should be said so.** `QA-001` and
> `QA-008` independently established the WCAG 2.2 / ISO/IEC 40500:2025 position, **dated it to the
> day**, and *ruled* the `05-06` / `TS-016` conflict rather than averaging it. Every one of those
> four claims was re-verified here against W3C and ISO primary sources and **no error was found.**
> The residual ⚠ is the 26 surviving `WCAG 2.1` citations, which `QAA-04` already owns.

### 5.5 Quality models, data and measurement

| Item | Current edition | Cited in estate | Status | Where it bites | Verified | Src | Next review |
|---|---|---|:--:|---|---|:--:|---|
| **ISO/IEC 25010** Product quality model | **2023** (2nd ed., **9 characteristics**) | `:2023` × 70, undated × 24, **`:2011` × 8** | ⚠ ◐ | `RQ-006`, `AR-001`, `AR-012`, `QA-001` | 2026-08-19 | P1 | **W1** |
| **ISO/IEC 25012** Data quality model | **2008** | `:2008` × 6, undated × 26 | ✅ ◐ | `DA-008` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC 25023** Quality measurement | **2016** | `:2016` × 4, undated × 7 | ✅ ◐ | `AR-012` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC 25040** Evaluation process | **2024** — supersedes `:2011` | **`:2011` × 4** | ⚠ | `QA-001` | 2026-08-19 | S1 | **W1** |
| **ISO 8000-61** Data quality management process | **2016** | `:2016` × 19 | ✅ | `DA-008` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC 5055** Automated source code measures | **2021** | `:2021` × 6 | ✅ | `BE-002`, `BE-009` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC 11179** parts 1, 5, 6, 31, 32 | 1:2023 · 5:2015 · 6:2023 · 31:2023 · 32:2023 | ×47 total, as cited | ✅ | `RR-002`, `DA-002`, `DA-009` | 2026-08-19 | P1 | `G3` |
| **ISO/IEC/IEEE 29119** parts 1–4 | 1:2022 · 2:2021 · 3:2021 · 4:2021 | ×80 total, as cited | ✅ | `QA-001` … `QA-011` | 2026-08-19 | P1 | `G2` |

> **`ISO/IEC 25010:2011` is cited 8 times against `:2023`'s 70, and the two editions differ
> materially.** The 2023 edition restructures to **nine** characteristics, adding *Safety* and
> relocating *Security* and *Compatibility*. A quality-attribute scenario written against the 2011
> taxonomy and measured against the 2023 one does not fail loudly — it fails by measuring a
> characteristic that is no longer where the scenario put it. **`AR-001`'s eleven quality-attribute
> scenarios and `AR-012`'s 184 fitness functions are the exposure.** Owner **Enterprise
> Architecture**, **W1**.

### 5.6 NIST, IEEE technical, and the sanitisation chain

| Item | Current edition | Cited in estate | Status | Where it bites | Verified | Src | Next review |
|---|---|---|:--:|---|---|:--:|---|
| **NIST SP 800-88** Media sanitization | **Rev. 2**, published **26 September 2025**. **Rev. 1 withdrawn the same day** | `800-88r2` × 15 + r2 × 4, **`r1` × 8** | ⚠ | `RL-006`, `DA-006`, `SC-006` | 2026-08-19 | P1 | `G2` |
| **IEEE 2883** Sanitizing storage | **2883-2022** — approved 16 Jun 2022, published 17 Aug 2022 | ×44, incl. `2883-2022` × 8 | ✅ | `RL-006` | 2026-08-19 | P1 | `G3` |
| **IEEE 2883.1** Recommended practice for use of sanitization methods | **2883.1-2025** | `2883.1-2025` × 11 | ✅ | `RL-006` | 2026-08-19 | P1 | `G3` |
| **NIST SP 800-218** SSDF | **1.1 (2022)**; **800-218A (2024)** for generative AI | `800-218` × 17, `800-218A` × 3 | ✅ | `SC-005`, `BE-003` | 2026-08-19 | P1 | `G3` |
| **NIST SP 800-207** Zero trust architecture | **2020** | ×14 | ✅ | `SC-001`, `PE-001` | 2026-08-19 | P1 | `G3` |
| **NIST SP 800-61** Incident response | **Rev. 3 (April 2025)** | `800-61r3` × 4, `800-61` × 7 | ✅ ◐ | `SC-011` | 2026-08-19 | P1 | `G3` |
| **NIST SP 800-63** Digital identity | **Rev. 4 (2024)** | `800-63` × 7, `800-63B` × 3 | ◐ | `SC-004` | 2026-08-19 | P1 | **W1** |
| **NIST SP 800-57 / 800-34 / 800-40 / 800-92 / 800-115 / 800-154 / 800-188 / 800-190** | Pt1 R5 · R2 · R4 · 2006 · 2008 · draft · 2023 · 2017 | mixed, mostly undated | ◐ | `SC-006`, `PE-007`, `SC-009`, `SC-010`, `PE-005` | 2026-08-19 | P1 | `G3` |

> **`NIST SP 800-88 r1` survives 8 times in this repository** — the exact citation `00-06` **H-01**
> was raised against, inside the repository written to close it. `RL-006` got it right by
> construction; `DA-006` and `SC-006` did not. This is `H-01` **unfinished**, not a new finding, and
> it is in §8 as `CUR-F-06` because the remediation is an edit list nobody has been given.
>
> **The substantive point about r2 the estate has not absorbed.** Rev. 2 is not a re-issue: it
> **removes the per-media technique tables** and defers technique detail to **IEEE 2883** and NSA
> specifications, reorienting around a *Media Sanitization Program*. A document citing r2 while
> reproducing r1's Clear/Purge/Destroy tables cites the right edition and quotes the wrong one.
> `RL-006` avoided this. The check is `CHK-C5`.

### 5.7 Frameworks and bodies of practice

| Item | Current edition | Cited in estate | Status | Where it bites | Verified | Src | Next review |
|---|---|---|:--:|---|---|:--:|---|
| **ITIL** | **ITIL 4** (2019, 2023 practice updates) | `ITIL 4` × 56, `ITIL` × 5 | ✅ | `SV-001`, `SV-006`, `RL-001` | 2026-08-19 | P2 | `G4` |
| **PMBOK Guide** | **7th Edition (2021)** | ×53 | ✅ | `GV-004`, `GV-007`, `CH-003` | 2026-08-19 | P2 | `G4` |
| **PRINCE2** | **7th Edition (2023)** | ×74 | ✅ | `GV-002`, `GV-006`, `GV-009` | 2026-08-19 | P2 | `G4` |
| **TOGAF** | **10th Edition (2022)** | `TOGAF 10` × 9, `TOGAF` × 3 | ✅ ◐ | `AR-002` | 2026-08-19 | P2 | `G4` |
| **OWASP ASVS** | **5.0.0**, released **30 May 2025** (Global AppSec EU, Barcelona) | `ASVS 5` × 16, **`ASVS 4` × 12**, undated × 8 | ⚠ ◐ | `SC-005`, `QA-007` | 2026-08-19 | P2 | **W1** |
| **OWASP Top 10** | **2021** (web); a **2025** edition released November 2025 | undated × 16 | ◐ | `QA-007`, `SC-002` | 2026-08-19 | P2 | **W1** |
| **OWASP SAMM / WSTG / CRS / Cheat Sheets** | SAMM 2.0 · WSTG 4.2 · CRS 4.x | mixed, undated | ◐ | `SC-005`, `QA-007` | 2026-08-19 | P2 | `G3` |
| **PCI DSS** | **v4.0.1** (June 2024). **v4.0 retired 31 December 2024.** All 51 future-dated requirements mandatory since **31 March 2025** | **`v4.0` × 7**, `PCI-DSS` undated × 10 | ⛔ ◐ | `IN-007`, `SC-001`, `SC-006` | 2026-08-19 | P2 | **Now** |
| **STRIDE** | Microsoft threat-modelling taxonomy — stable, unversioned | ×45 | ✅ | `SC-002` | 2026-08-19 | P2 | — |
| **ACMP Standard for Change Management** | **v2 (2025)** | ×29 | ✅ | `CH-001`, `CH-004`, `CH-005` | 2026-08-19 | P2 | `G4` |
| **ADKAR / Kotter / Kirkpatrick** | Prosci ADKAR · Kotter 8 Accelerators · New World Kirkpatrick | ×42 combined | ✅ | `CH-001`, `CH-002`, `CH-004` | 2026-08-19 | P2 | `G4` |
| **SLSA** | **v1.0** (2023) | ×30, undated | ◐ | `BE-007`, `PE-004` | 2026-08-19 | P2 | `G3` |
| **SPDX** | **3.0** (2024); **ISO/IEC 5962:2021** is SPDX 2.2.1 | ×36, undated | ◐ | `BE-007`, `CO-004` | 2026-08-19 | P2 | **W1** |
| **CycloneDX** | **1.6** (2024); **ECMA-424** | ×27, undated | ◐ | `BE-007`, `CO-004` | 2026-08-19 | P2 | **W1** |
| **OpenChain** | **ISO/IEC 5230:2020**; security assurance **ISO/IEC 18974:2023** | `5230` × 22, `18974:2023` × 4 | ✅ | `CO-004`, `BE-007` | 2026-08-19 | P1 | `G3` |
| **CIS Benchmarks** | Rolling, per-platform | ×7, undated | ◐ | `PE-005`, `PE-009` | 2026-08-19 | P2 | `G3` |
| **SOC 2** | AICPA TSC 2017 (rev. 2022) | ×5 | ◐ | `CO-003` | 2026-08-19 | P2 | `G4` |
| **BABOK** | **v3** (2015); v4 in development | ×11 | ◐ | `RQ-005` | 2026-08-19 | P2 | `G4` |

> **`SPDX`, `CycloneDX` and `SLSA` are cited 93 times between them and versioned zero times.** For a
> programme whose `CO-004` licence register and `BE-007` SBOM standard are **contractual
> deliverables**, an unversioned SBOM format is not a citation defect — it is an **acceptance-test
> defect**, because *"produce an SBOM"* without a format version is not testable. `CUR-F-07`.

### 5.8 Protocol and encoding references

Forty-one distinct RFCs and ISO data standards are cited, each one to seven times. Registered by
family; all are stable published references with no currency question.

| Family | Members cited | Status | Note |
|---|---|:--:|---|
| **IETF RFC** | 9457 (×29), 9110, 8446, 8705, 7662, 6890, 6234, 4033, 3986, 3339, 9700, 9745, 8594, 1918 | ✅ | RFCs are immutable once published; currency is a question of *obsoletion*, not edition. **RFC 9745** (deprecation) and **RFC 8594** (sunset) are correctly paired in `IN-005` |
| **ISO data standards** | 8601 (dates) · 4217 (currency) · 3166 (country) · 639 (language) | ✅ | Cited undated. **Declared exception to `CUR-01`** — `RR-005-D-03` |
| **W3C** | WCAG 2.2 · WCAG2ICT · ACT Rules Format · WAI-ARIA | ✅ | §5.4 |
| **Unicode** | The Unicode Standard **17.0** (9 September 2025); **17.1 scheduled September 2026** | ⏳ | `UX-007`, Bengali block U+0980–U+09FF. Already correctly dated by `UX-007` |

### 5.9 Vendor-adjacent technical conventions

| Item | Position | Cited | Note |
|---|---|---:|---|
| **OCA Development Guidelines** | Rolling, no version | `BE-002`, `AR-007` | ◐ by nature — the OCA does not version its guidelines. Registered so the absence of an edition is a recorded fact rather than an omission |
| **Odoo 19.0 module conventions / ORM conventions** | Bound to the Odoo release, §7.1 | `BE-002`, `AR-007` | ✅ Correctly version-bound |
| **OMG BPMN 2.0 · DMN 1.4 · SBVR** | 2011 · 2022 · 2019 | `RQ-007`, `RQ-009` | ✅ |
| **MADR 4.0 · Nygard ADR pattern** | 4.0 (2022) · unversioned | `AR-004` | ✅ |

### 5.10 The boundary with `RF-008`

`project_content/99_.../RF-008` is the **content** estate's external-standards register: **44
instruments, 6 methodologies, 460 lines, issued 2026-08-18**, with findings `SR-01`…`SR-04`. It is
not restated here and is not superseded.

| Question | Rule |
|---|---|
| Which register governs a standard cited by **both** estates? | **This one** for the engineering claim; `RF-008` for the content claim. They must not disagree |
| What happens when they do? | The disagreement **is** the finding. `CHK-C6` compares them mechanically |
| Was a disagreement found at this issue? | **Not tested row-by-row.** `RF-008` was read for method and for its four findings. `CUR-Q-06` |
| What did the partial read establish? | `RF-008` covers **ISO 9001:2026** and the repealed-cyber-instrument class (`SR-02`), and does **not** cover IEEE 1016, PCI DSS, OWASP ASVS, ISO/IEC 25010:2011, ISO/IEC 40500 or Odoo. **Coverage is complementary, not duplicative — but nobody designed it that way** |

> **`RF-008` §4.8's structural finding is adopted verbatim, because it is the truest sentence in
> either register:** *"One controlled copy out of forty-four … Every other status rests on
> published text read on the verification date, not on a version-stamped instrument held by the
> company."* The same is true of all 118 rows here. It is adequate for currency tracking and
> **inadequate for a statutory filing**, and §6 says so.

---

## 6. The Bangladesh Statutory and Regulatory Register

> **Evidence class.** Every row in §6 rests on **S2** evidence — reputable press, law-firm
> briefings and policy trackers — because no reliably reachable primary gazette source was
> available at the verification date. `CUR-03` requires this declared, and `CUR-Q-01` escalates
> confirmation to external counsel via `GV-005` `DEP-31`. **No row in §6 may support a filing or a
> contractual representation until that confirmation returns.**

### 6.1 The cyber-security succession chain — now five instruments deep

| # | Instrument | In force from | Superseded by | On |
|---:|---|---|---|---|
| 1 | **Information and Communication Technology Act, 2006** (§57 especially) | 2006 | Substantially absorbed into the DSA | 2018 |
| 2 | **Digital Security Act, 2018** | Oct 2018 | Cyber Security Act, 2023 | **13 September 2023** |
| 3 | **Cyber Security Act, 2023** | 13 Sept 2023 (assented) | **Cyber Security Ordinance, 2025** | **21–22 May 2025** (gazetted 21 May) |
| 4 | **Cyber Security Ordinance, 2025** (Ordinance No. 25 of 2025) | 21 May 2025 | **Cyber Security Bill/Act, 2026** — ordinance repealed and replaced by Parliament | **30 April 2026** |
| 5 | **Cyber Security Act, 2026**, as amended by the **Cyber Security (Amendment) Act, 2026** | 30 April 2026 | — in force | — |

> ### `CUR-F-01` — the engineering estate cites the third instrument in a chain that is five deep
>
> **What was found**, counted in `project-guide-doc/` at 2026-08-19 19:54:
>
> | Citation | Occurrences | Files |
> |---|---:|---:|
> | `Cyber Security Ordinance 2025` | **37** | **22** |
> | `Cyber Security Act 2023` | 7 | — |
> | `Cyber Security Act 2026` | **0** | **0** |
> | `Cyber Security (Amendment)` | **0** | **0** |
>
> A search of **all 792 workspace markdown files** for the 2026 instrument returns **zero**.
>
> **Why it matters.** This is `00-06` **C-04** — *"Digital Security Act 2018, repealed twice"* — at
> its **third** generation. The pattern is now unmistakable: **Bangladesh's cyber statute has
> changed roughly every eighteen months since 2018**, and the programme has been caught three times
> in a row, each time by a different document set, each time found by an auditor rather than by a
> control.
>
> The exposure is concrete. `SC-001`, `SC-008`, `SC-010`, `SC-011` and `DA-005` build obligations —
> breach reporting, lawful-interception response, evidence preservation, offence classification — on
> the text of a repealed instrument. The 2026 Act materially changed penalties, bailability and
> platform take-down duties; obligations derived from the 2025 ordinance's text are, at best,
> unverified.
>
> **What this register does *not* claim.** It does not state what the 2026 Act requires — that is
> `SC-008`'s work and counsel's. It states that **the instrument the estate cites is not the
> instrument in force**, which is a fact about the citation and is this register's business.
>
> **Remediation.**
> 1. **Now** — `SC-008` opens a work item to obtain the gazetted text of the Cyber Security Act 2026
>    and its Amendment, via counsel (`GV-005` `DEP-31`). Owner **Security & Privacy Lead**.
> 2. **W1** — the 22 files are re-cited. Owner **Enterprise Architecture**; the file list is
>    reproducible by `CHK-C5`.
> 3. **W1** — `SC-008` re-derives every obligation sourced from the 2025 ordinance and marks those
>    that changed. Owner **Security & Privacy Lead**.
>
> **Severity CRITICAL.** Not because the citation is untidy, but because a security-obligation
> register built on a repealed statute is the first thing a regulator, an auditor and a plaintiff
> would each find.

### 6.2 Data protection — the chain the estate got right

| # | Instrument | In force from | Superseded by | On |
|---:|---|---|---|---|
| 1 | **Personal Data Protection Ordinance, 2025** (PDPO) | Gazetted **6 November 2025** | Amended by Ordinance No. 23 of 2026 | 5 Feb 2026 |
| 2 | **Personal Data Protection (Amendment) Ordinance, 2026** (No. 23 of 2026) | **5 February 2026** | Repealed with the PDPO | Apr 2026 |
| 3 | **Personal Data Protection Act, 2026** (**Law 63 of 2026**) | Passed by Parliament **April 2026** | — in force | — |

| Attribute | Position | Estate coverage |
|---|---|---:|
| Regulator | **National Data Management Authority** | **43** workspace files ✅ |
| Full enforcement / compliance | **≈13 May 2027** | **55** files ✅ |
| Law number | **Law 63 of 2026** | **32** files ✅ |
| Named officer duty | **Chief Data Officer** appointment | **100** files ✅ |
| **Residency** | Restricts large-scale transfer of sensitive PII — **NID, passport, biometric, genetic** — abroad without authorisation. The **February 2026 Amendment Ordinance** required at least one **synchronised real-time copy** inside Bangladesh for restricted data and data processed by Critical Information Infrastructure | `SC-007` — **whether the Act carried that wording forward is `CUR-Q-02`** |
| Breach notification | To the Authority where a breach causes *"significant damage"*, in the manner prescribed by regulations — **regulations not yet issued** | `SC-011` — the timeline is currently **unknowable** and should be recorded as such, not assumed |
| Risk assessment | Mandated, though not named "DPIA" | `SC-003` ✅ |
| Administrative fines | Up to **BDT 25 lakh**; up to **BDT 50 lakh** for designated significant controllers | `SC-008`; `CO-005` TCO risk line |

> **This is the estate's best statutory work and it should be recorded as such.** PDPA 2026 is cited
> correctly — by law number, with the right regulator, the right enforcement date and the right
> officer duty — across dozens of files. It is direct evidence that the estate *can* track a moving
> instrument when someone is watching, and therefore that `CUR-F-01` is a gap in **coverage**, not
> in capability.
>
> **The one open point is residency, and it is `SC-007`'s.** The February 2026 Amendment introduced
> an in-country synchronised-copy requirement; the April 2026 Act repealed the Ordinance it
> amended. Whether that requirement survived into the Act, and in what words, decides whether
> `SC-007`'s design is compliant or merely careful. **`CUR-Q-02`, owner Security & Privacy Lead,
> W1** — a question for counsel, not for a search engine.

### 6.3 Tax, corporate and employment instruments

| Instrument | Position | Cited | Where it bites |
|---|---|---:|---|
| **VAT and Supplementary Duty Act, 2012** (+ Rules 2016, as amended by successive Finance Acts) | In force | ×9 | `DT-*` statutory outputs; Mushak forms |
| **Mushak forms** — 6.1 (×4), 6.3 (×71), 6.6 (×1), 9.1 (×20) | Prescribed under the VAT Rules; **changed by SRO at any Finance Act** | **×96** | `IN-007`, `DA-009`, `DT` templates. **Highest-churn statutory artefact in the estate** |
| **Income Tax Act, 2023** | In force (replaced the 1984 Ordinance) | ×5 | Payroll, withholding, `e-TIN` (×189) |
| **Companies Act, 1994** / RJSC filings | In force | — | `GV-001`, `CO-003` |
| **Bangladesh Labour Act, 2006** + **Labour Rules, 2015** | In force, both amended | ×12 / ×5 | `CH-002` statutory safety training; HR modules |
| **BEFTN** — Bangladesh Electronic Funds Transfer Network | Bangladesh Bank operating rules | ×80 | `IN-007` |
| **NBR VAT Online / e-TIN** | Live services; interface specifications change without a standards process. **Online VAT submission mandatory from July 2026** (`RF-008` `SR-01`) | ×91 / ×189 | `IN-007`, `MG-002` |
| **BTRC** directions | Applicable to platform take-down duties under the 2026 Act | — | `SC-008` |

> ### `CUR-F-11` — the Mushak forms have no currency owner
>
> Ninety-six citations of four prescribed forms whose layout and field set are changed by SRO,
> typically at the June Finance Act. **Nothing in the engineering estate names an owner for
> detecting that change.** A statutory invoice printed to a superseded Mushak layout is rejected at
> the counter, not at a gate.
>
> `RF-008` `SR-01` has already done the hard part for the filing *basis* — establishing that Mushak
> 9.1 is **monthly, by the 15th of the following month**, and that the quarterly citation in a `DT`
> file is an exception to be confirmed at `G6`. What neither register has is an owner for the
> **form layout**.
>
> **Owner: Finance Controller. Next review: at every Finance Act — annually in June.** This is the
> one row in this register whose review is a calendar date rather than a gate, and it is
> `CUR-07`'s declared exception, because the Finance Act is itself a calendar event.
> **Severity Medium**, becoming High at first invoice.

---

## 7. Vendor and Product Version Register

### 7.1 Odoo — the version claim the whole architecture rests on

| Fact | Position | Verified | Src |
|---|---|---|:--:|
| Odoo 19 release date | **18 September 2025** — `00-06` **M-01** corrected *"October 2025"* | 2026-08-19 | P2 |
| Edition in scope | **Community Edition (CE)**, per `TD-01` | 2026-08-19 | P1 |
| Support policy | Odoo supports the **three most recent major versions** — currently **17, 18, 19** | 2026-08-19 | S1 |
| **Odoo 20** | Expected at **Odoo Experience 2026, 24–26 September 2026**; general availability typically 2–4 weeks after | 2026-08-19 | S1 |
| Estate citations | `Odoo 19` × 63 · `Odoo 19.0` × 50 · **`Odoo 20` × 20** | 2026-08-19 | — |

> ### `CUR-F-04` — Odoo 20 lands five weeks from this issue, inside Wave 1
>
> **The estate already knows** — `Odoo 20` is cited 20 times, and `AR-013`'s technology radar and
> `AR-007`'s fork register are written for a versioned core. This row exists to **put a date on
> something the estate refers to without one**, and to state the two consequences that follow from
> the support policy:
>
> 1. On Odoo 20's release the supported set becomes **18, 19, 20**. Odoo 19 remains supported for
>    roughly two further years, so a Wave 1 build on 19.0 is **not stranded**.
> 2. **The 58 custom modules are the exposure, not the core.** `AR-007`'s decision tree and
>    `BE-007`'s dependency standard both assume a stable ORM surface, and a major version lands in
>    the middle of the build. `AR-013` should carry a **dated** *"evaluate 20, do not adopt in W1"*
>    position rather than leave it to be decided in October by whoever notices.
>
> **Remediation.** `AR-013` adds a dated radar entry; `CO-003`'s deliverable schedule states the
> target version explicitly so acceptance is not argued later. Owner **Enterprise Architecture**,
> **W1**. **Severity Medium** — high impact, high notice.

### 7.2 Platform components

| Component | Version claimed | Currency question | Owner | Next review |
|---|---|---|---|---|
| **PostgreSQL** | as declared in `PE-001` / `02-05` | Annual major release each September; five-year supported-version window | Infrastructure Lead | `G2` |
| **Python** | Odoo 19's declared runtime | Bound to the Odoo version, not chosen independently | Build Lead | `G2` |
| **Container runtime / orchestrator** | `PE-005` | **CIS Benchmark** currency (§5.7) rather than version currency | Infrastructure Lead | `G3` |
| **Payment and financial gateways** | `IN-007` | **Not standards — live interfaces.** No edition, no withdrawal notice, no catalogue page. They change when the counterparty changes them | Integration Lead | **Continuous** |
| **NBR VAT Online / BEFTN** | §6.3 | As above, with statutory force | Finance Controller | **Continuous** |

> **The last two rows are what a standards register normally misses.** The only currency control
> available for a live interface is **continuous certification**, which is exactly what `IN-008`
> specifies. Registered here so that *"everything is current"* is never claimed while those two rows
> are unmonitored.

---

## 8. Findings

Eleven. Three are new and material; the rest are prior findings whose **remediation** is measured
here for the first time, or findings the content estate already holds.

| # | Finding | Severity | New? | Owner | Needed by |
|---|---|:--:|:--:|---|---|
| `CUR-F-01` | **Cyber Security Ordinance 2025 cited 37 times in 22 files; repealed 30 April 2026** by the Cyber Security Act 2026. Zero workspace citations of the instrument in force | **CRITICAL** | **New to this estate**; class recorded by `RF-008` `SR-02` | Security & Privacy Lead | **Now** |
| `CUR-F-02` | **ISO 9001:2026 publishes 16 September 2026** — 28 days out. 146 `:2015` citations, 6 `standards_basis` entries, and an ISO 9001:2015 certification claim in **25 workspace footers** | **High** | **No** — `RF-008` found it for the content estate. New to the engineering estate | Quality Manager | **Now** |
| `CUR-F-03` | **IEEE 1016-2009 is Inactive-Reserved** and is `AR-003`'s governing standard, `RR-003`'s basis, and one of `PGD-000` §3's thirteen bases. 36 citations | **High** | **New** | Enterprise Architecture | **Now** |
| `CUR-F-04` | **PCI DSS v4.0 cited 7 times; v4.0 retired 31 December 2024.** Current is v4.0.1, with 51 future-dated requirements mandatory since 31 March 2025 | **High** | **New** | Security & Privacy Lead | **W1** |
| `CUR-F-05` | **OWASP ASVS 4 cited 12 times alongside ASVS 5's 16.** ASVS 5.0.0 (30 May 2025) is canonical, and the two number their requirements differently — a test written to one cannot be traced to the other | Medium | **New** | QA Lead | **W1** |
| `CUR-F-06` | **Six items are cited in two editions at once** — 25010 (2011/2023), 25062 (2006/2025), 10018 (2012/2020), 29134 (2017/2023), WCAG (2.1/2.2), SP 800-88 (r1/r2). **`H-01`'s r1 survives 8 times in the repository written to close it** | Medium | Partly | Enterprise Architecture | **W1** |
| `CUR-F-07` | **Twelve heavily-cited items carry no edition at all** — ISO 9001 (undated), ISO/IEC 27001 (41), **ISO/IEC 19790 (25, and it is `SC-006`'s basis)**, ISO/IEC 25012 (26), ISO/IEC 25010 (24), ISO 10007 (12), ISO/IEC 20000-1 (11), SPDX (36), SLSA (30), CycloneDX (27), OWASP Top 10 (16), EN 301 549 (14). **`PGD-A2-07` at scale** | Medium | Partly | Enterprise Architecture | **W1** |
| `CUR-F-08` | **`verified_on` has 100% coverage and 2 distinct values.** Every document was verified on the day it was written; nothing has been re-verified; only 3 of 133 schedule a second verification | Medium | **New** | PMO | **W1** |
| `CUR-F-09` | **NIST SP 800-88 r2 removed the per-media technique tables** and defers to IEEE 2883. A document citing r2 while reproducing r1's tables cites the right edition and quotes the wrong one | Low | **New** | Security & Privacy Lead | `G2` |
| `CUR-F-10` | **`RF-008` and this register have never been reconciled.** Two external-standards registers in one workspace, complementary by accident, with no precedence rule until §5.10 | Medium | **New** | Enterprise Architecture | `G2` |
| `CUR-F-11` | **The four Mushak forms (96 citations) have no currency owner**, and change by SRO at each Finance Act | Medium | **New** | Finance Controller | **W1** |

### 8.1 Severity basis

Deliberately the same scale `RR-002` §8.1 and `RR-004` §8 use, so findings across the three
registers are comparable:

**CRITICAL** = a legal, contractual or regulatory position rests on an instrument not in force.
**High** = a conformance claim can be made that is wrong and looks right. **Medium** = a reader is
misled but a mechanical check would catch it. **Low** = a latent trap with no current instance.

### 8.2 What the eleven have in common

Ten of the eleven are **one control failing in ten places**, and the control is `00-06` §9's —
*"re-verified at each wave gate."* Proposed since the first governance audit; executed zero times.

The eleventh, `CUR-F-08`, is the reason. **The estate implemented the visible half of the control
and not the invisible half.** `verified_on` is a front-matter field, so it reached 100% compliance
in a day. A *review cycle* is invisible until it fails, so it reached zero. That is not
carelessness — it is what happens when a control's evidence is a field rather than an event.

**§9 is the event.**

---

## 9. The Review Calendar

`CUR-07`: reviews bind to gates, not dates. A calendar review slips silently because nobody is
standing at a calendar.

| Gate | From `GV-009` | What is re-verified | Trigger |
|---|---|---|---|
| **Now** (pre-`G1`) | — | `CUR-F-01`, `CUR-F-02`, `CUR-F-03`, `CUR-F-04`, and every ⛔ row | The four Now-dated findings |
| **`G1`** | Wave 1 entry | **All 118 rows.** All ⏳ rows; all §6 statutory rows; the Odoo position | Full re-verification |
| **`G2`** | Wave 1 build exit | §5.1, §5.3, §5.4, §5.6 — the rows test and security claims rest on | Rows marked `G2` |
| **`G3`** | Wave 2 entry | §5.2, §5.5, §5.7 | Rows marked `G3` |
| **`G4`** | Wave 2+ | §5.7 frameworks; §5.2 project-management standards | Rows marked `G4` |
| **June, annually** | — | **Mushak forms and Finance Act instruments only** — §6.3's declared exception | `CUR-F-11` |
| **Continuous** | — | Payment gateways, NBR VAT Online, BEFTN — via `IN-008` certification, not via this register | §7.2 |

**What "re-verified" means, operationally.** For each row in scope: open the publisher's catalogue
page; compare the edition to the **Current edition** column; if it moved, set the status, register
the successor and its date, and raise a finding with an owner. Update **Verified**. **A row whose
Verified date predates the last completed gate is *lapsed*, and `CHK-C2` fails on it.**

**Effort, counted rather than guessed.** 118 rows, of which 41 are individual P1 catalogue lookups
and the rest are family checks: **one person-day per full re-verification, four times a year.**
Against eleven findings of which one is critical, that is the cheapest control in this register —
and `RR-004` §9 reached the same conclusion independently about its own.

---

## 10. Enforcement

Numbered `CHK-C*` so as not to collide with `RR-002` §10's `CHK-01`…`06` or `RR-004` §10's
`CHK-E1`…`E6`.

| # | Check | Detects | Gate |
|---|---|---|---|
| `CHK-C1` | **Undated citation** — any `ISO`, `IEC`, `IEEE`, `NIST SP`, `PCI DSS` or `OWASP` token not followed by an edition or year | `CUR-F-07`, `CUR-01`, `CUR-09` | Warn at commit, **fail at `G1`** |
| `CHK-C2` | **Lapsed verification** — any document whose `verified_on` predates the last completed gate | `CUR-F-08`, `CUR-02` | Warn, **fail at gate** |
| `CHK-C3` | **Dual-edition citation** — the same item cited in two editions across the repository | `CUR-F-06`, `CUR-05` | **Fail** |
| `CHK-C4` | **Future verification date** — `verified_on` later than the file's modification date | `CUR-06`, `RF-002` `EV-F1` | **Fail** |
| `CHK-C5` | **Retired-citation sweep** — any occurrence of a ⛔ citation string from §5 or §6 | `CUR-F-01`, `-04`, `-06` | **Fail** |
| `CHK-C6` | **Register divergence** — an item registered in both this register and `RF-008` with a different current edition | `CUR-F-10` | Warn |

```bash
# CHK-C5 — the retired-citation sweep. Run before every gate.
# Output at this issue: 64 hits across the repository. That is the remediation backlog.
grep -rn -E 'Cyber Security Ordinance,? ?2025|PCI DSS v4\.0([^.]|$)|NIST SP 800-88 ?r1|ISO/IEC 25010:2011|ISO/IEC 25062:2006|ISO 10018:2012|ISO/IEC 29134:2017|OWASP ASVS 4' \
  --include='*.md' project-guide-doc | cut -d: -f1 | sort | uniq -c | sort -rn

# CHK-C3 — dual-edition citation. Any item appearing with two different years.
grep -rhoE 'ISO(/IEC)?(/IEEE)? [0-9]{3,5}(-[0-9]+)?:[0-9]{4}' --include='*.md' project-guide-doc \
  | sort -u | sed -E 's/:[0-9]{4}$//' | uniq -d

# CHK-C4 — a verification date later than the file itself. RF-002 EV-F1's method.
for f in $(find project-guide-doc -name '*.md'); do
  v=$(sed -n 's/^verified_on: *//p' "$f" | head -1); m=$(date -r "$f" +%F)
  [ -n "$v" ] && [ "$v" \> "$m" ] && echo "FUTURE $v > $m  $f"
done
```

> **`CHK-C5` run at this issue returns 64 hits across the repository.** That number is the
> remediation backlog for `CUR-F-01`, `-04`, `-05` and `-06`, and it is small enough to clear in an
> afternoon — which is the point. **The findings are cheap to fix and were expensive to find**, and
> that asymmetry is the whole argument for running the check rather than writing the register again
> next year.

---

## 11. Decisions Recorded

`DL-06` / `RR-002` `IDC-07`: identifiers take the form `RR-005-D-nn`.

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RR-005-D-01` | Scope versus `SC-008` | (a) one register of instruments **and** obligations; (b) instruments and currency here, obligations in `SC-008` | **(b)** | An obligations register is re-derived when a statute moves; a currency register is what *tells* it to. Merging them gives the trigger and the response the same owner and the same review date — which is how `C-04` survived two repeals | `SC-008` gains a dependency on §6; §9's gate reviews feed it |
| `RR-005-D-02` | `IEEE 1016-2009`'s Inactive-Reserved status | (a) migrate `AR-003` to another standard; (b) **retain and declare the status**; (c) drop the conformance claim | **(b)** | No successor exists — ISO/IEC/IEEE 42010:2022 covers architecture description, not detailed design. The taxonomy remains the best available; only the *claim* of conformance to a maintained standard is wrong | `AR-003`, `RR-003` and `PGD-000` §3 restate the basis with the status attached |
| `RR-005-D-03` | The four undated ISO data standards (8601, 4217, 3166, 639) | (a) enforce `CUR-01` uniformly; (b) **declare an exception** | **(b)** | These four are cited undated by everyone, are stable, and enforcing editions on them would bury `CHK-C1`'s real output in noise | §5.8 declares it; `CHK-C1` excludes the four by name |
| `RR-005-D-04` | Evidence class for §6 | (a) hold §6 until primary gazette sources are obtained; (b) **publish on S2, declared, with escalation to counsel** | **(b)** | `CUR-F-01` is CRITICAL and dated. Holding a critical finding for weeks pending a document request is a worse failure than publishing it labelled | Every §6 row declares S2; `CUR-Q-01` escalates; no §6 row may support a filing until confirmed |
| `RR-005-D-05` | Review cadence | (a) quarterly calendar; (b) **wave gates**; (c) both | **(b)**, with one declared exception | A calendar review has nobody standing at it. `00-06` §9 proposed gates and was right | §9; the Finance Act / Mushak row is the single calendar exception, because the Finance Act is itself a calendar event |
| `RR-005-D-06` | The `(+06)` / `+08:00` timestamp divergence | (a) assume the labels are right; (b) assume the host is right and restate every timestamp; (c) **record the ambiguity and escalate** | **(c)** | Both readings fit the evidence and this register cannot distinguish them. Restating 171 files' timestamps on a guess would manufacture false precision | §4.4; `CUR-Q-05`; this document stamps *repository wall clock* |
| `RR-005-D-07` | Whether to restate `RF-008`'s 44 rows here | (a) restate for completeness; (b) **reference and reconcile mechanically** | **(b)** | Restating creates a second copy that goes stale independently — the defect `RR-006` exists to prevent. `RF-001`/`RR-001` set the same precedent for glossaries, and `RR-004`/`RF-002` for source indexes | §5.10; `CHK-C6`; `CUR-Q-06` |
| `RR-005-D-08` | Whether to claim `CUR-F-02` as a new finding | (a) claim it; (b) **attribute it to `RF-008` and record the duplication as its own finding** | **(b)** | The content estate found it first, and pretending otherwise would make this register an instance of the defect it is reporting | `CUR-F-10`; `RR-004` `EVR-F-07` |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `CUR-Q-01` | Will counsel confirm §6's rows against the gazette — in particular the **Cyber Security Act 2026's commencement** and the status of the 2025 Ordinance? | **External counsel**, via Security & Privacy Lead | **Now** | `CUR-F-01`; every `SC-008` obligation derived from the 2025 ordinance |
| `CUR-Q-02` | Did the **Personal Data Protection Act, 2026** carry forward the February 2026 Amendment Ordinance's **in-country synchronised-copy** requirement, and in what words? | **External counsel**, via Security & Privacy Lead | **W1** | `SC-007` residency design; `PE-001` region placement; `CO-005` TCO |
| `CUR-Q-03` | Does the programme adopt **ISO 9001:2026** before or after the Wave 1 baseline, given publication on 16 September 2026 and a three-year transition? | **Quality Manager / CTO** | **Now** | `GV-010`; the footer claim in 25 files |
| `CUR-Q-04` | Which body ratifies `CUR-01`…`CUR-10`? `PGD-A1-09` records that none exists | **Board** | **Now** | Every ✅ in this estate (`PGD-A2-25`) |
| `CUR-Q-05` | Are this repository's `(+06)` timestamp labels correct, or is the host clock authoritative at `+08:00`? | **PMO / Infrastructure Lead** | **W1** | `MG-006` cutover instants; `RL-002` freeze windows; every enumeration timestamp in the estate |
| `CUR-Q-06` | Row-by-row reconciliation of this register against `RF-008` — who runs it, and when? | Enterprise Architecture / Programme Content Lead | `G2` | `CUR-F-10`; `CHK-C6` |
| `CUR-Q-07` | Who owns detection of **Mushak form layout changes** at each Finance Act? Assumed here to be the Finance Controller | **CFO** | **W1** | `CUR-F-11`; every statutory print template in `DT-*` |

> Seven questions, seven named owners, seven dates. **`CUR-Q-01`, `CUR-Q-03` and `CUR-Q-04` are
> escalated to `GV-005` RAID at issue.**

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every external item cited in `project-guide-doc/` appears in §5, §6 or §7, or is covered by a §5.8 family row | 248 citation forms reduced to ≈150 items; **118 registered individually, the remainder by family**. Met, with the family-row method declared in `AC-11` |
| `AC-02` | Every registered row carries all eight §3.1 columns | Row inspection; **met at issue** |
| `AC-03` | Every §5 status claim rests on P-class evidence; every §6 row declares its S2 class | §5 rows carry `P1`/`P2`; §6 carries a blanket S2 declaration and `CUR-Q-01`; **met at issue** |
| `AC-04` | The three findings `00-06` proposed this register to prevent — `C-04`, `H-01`, `M-01` — each have a current position and a residual edit list | §2.3, §5.6, §6.1, §7.1; **met at issue**, with `C-04`'s remediation open and assigned |
| `AC-05` | Every figure carries the enumeration timestamp and a reproducible command | §4.1; **met at issue** |
| `AC-06` | Every row carries a next-review gate; every finding an owner and a date | 118 of 118 rows; 11 of 11 findings; **met at issue** |
| `AC-07` | This document's rule prefix was collision-checked before allocation per `RR-002` `IDC-08` | `rule_prefix:` front matter, 792-file denominator and timestamp; **met at issue** |
| `AC-08` | The six checks are runnable as written | `CHK-C1`, `CHK-C3`, `CHK-C4`, `CHK-C5` executed during authoring; `CHK-C2` specified and runnable; **`CHK-C6` blocked on `CUR-Q-06`** |
| `AC-09` | Findings the content estate already holds are attributed, not claimed | `CUR-F-02` attributed to `RF-008`; `RR-005-D-08`; **met at issue** |
| `AC-10` | The register is reconciled row-by-row with `RF-008` | **Not met.** `RF-008` read for method and findings only. `CUR-Q-06`. Stated rather than claimed, per `PG-M2` |
| `AC-11` | One row per item | **Deliberately not met** — forty-one RFCs each cited once do not repay 41 rows. §5.8's family method is declared, not concealed |

**Definition of done.** Complete when every criterion above is met, `PGD-000`'s `RR-005` row is
updated with a fresh enumeration timestamp, and the approver has signed. **`AC-10` and `AC-11`
carry residual or deliberately-declined work and are stated as such**, because a completeness claim
this register cannot support is the one claim a currency register must never make.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `PGD-000` | Registers this document; §3's `Basis` line is corrected by `CUR-F-03` |
| Upstream | `00-06` §9, §10 | Proposes this register; supplies `C-04`, `H-01`, `M-01` |
| Upstream | `RR-002` §5, §7.2 | Identifier forms and the `rule_prefix:` procedure |
| Upstream | `RR-003` §6.2 | The front-matter schema in which `verified_on:` and `review_cycle:` live |
| Upstream | `RR-004` §5.7 | Internal reference integrity — the internal counterpart of this register |
| Downstream | `SC-008` | Receives §6's instruments; re-derives obligations when a §9 review moves a row |
| Downstream | `SC-003`, `SC-007` | Receive `CUR-Q-02` — the residency question |
| Downstream | `SC-001`, `SC-010`, `SC-011`, `DA-005` | Receive `CUR-F-01`'s re-citation list |
| Downstream | `AR-003`, `RR-003`, `PGD-000` §3 | Receive `RR-005-D-02` — the IEEE 1016 status restatement |
| Downstream | `QA-001`, `QA-007`, `QA-008` | Receive `CUR-F-05`; §5.4 adopts `QA-008` §3 unchanged |
| Downstream | `AR-013`, `CO-003` | Receive `CUR-F-04` — the dated Odoo 20 radar entry |
| Downstream | `GV-010` | Receives `CUR-F-02` — the ISO 9001:2026 transition item |
| Downstream | `CO-004`, `BE-007` | Receive `CUR-F-07`'s SBOM-format versioning requirement |
| Downstream | `PE-004` | Hosts `CHK-C1`…`CHK-C6` as pipeline gates |
| Downstream | `RR-006` | The generated index; §9's review output is one of its feeds |
| Lateral | `../../project_content/99_Reference_and_Registers/RF-008` | The content estate's equivalent. Referenced and reconciled by `CHK-C6`, **not restated** |
| Lateral | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_*.md` §9 | The proposal this document executes |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
`./_CATEGORY_OVERVIEW.md` · `./RR-001_Glossary_and_Acronym_Register.md` ·
`./RR-002_Identifier_Convention_Standard.md` ·
`./RR-003_Document_Standards_and_Template_Library.md` ·
`./RR-004_Source_Document_Index_and_Evidence_Register.md` ·
`./RR-006_Master_Cross_Reference_and_Traceability_Index.md` ·
`../05_Security_Privacy_and_Compliance/SC-003_Data_Protection_Impact_Assessment_PDPA_2026.md` ·
`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md` ·
`../05_Security_Privacy_and_Compliance/SC-008_Regulatory_Compliance_Obligations_Register.md` ·
`../02_Architecture_and_Design/AR-003_Software_Design_Description.md` ·
`../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md` ·
`../08_Quality_Engineering_and_Test/QA-008_Accessibility_Test_Plan.md` ·
`../12_Release_Deployment_and_Transition/RL-006_Legacy_Decommissioning_Plan.md`

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` §9, §10 ·
`../../project_content/99_Reference_and_Registers/RF-008_External_Standards_and_Regulatory_Reference_Register.md` ·
`../../project_content/99_Reference_and_Registers/RF-002_Source_Document_and_Evidence_Index.md` §4.7 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md`

**External sources, with verification dates**

*Primary (P1 / P2) — verified 2026-08-19*

| Item | Source |
|---|---|
| NIST SP 800-88 Rev. 1 withdrawal, 26 September 2025; Rev. 2 published same day | `nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-88r1.pdf` |
| IEEE 2883-2022; IEEE 2883.1-2025 | `standards.ieee.org` · `ieeexplore.ieee.org/document/9856626` |
| **IEEE 1016-2009 — Inactive-Reserved** | `standards.ieee.org/standard/1016-2009.html` |
| WCAG 2.2 approved as ISO/IEC 40500:2025, 21 October 2025 | `w3.org/WAI/news/2025-10-21/wcag22-iso` · `iso.org/standard/91029.html` |
| ISO/IEC 19790:2025 (3rd ed., 26 February 2025) | `iso.org/standard/82423.html` |
| ISO/IEC 27701:2025 (2nd ed., standalone MSS, 14 October 2025) | `iso.org/standard/27701` |
| ISO 25062:2025, replacing ISO/IEC 25062:2006 | `iso.org/standard/84255.html` |
| ISO/IEC/IEEE 29148:2018 — under revision | `iso.org/standard/72089.html` |
| **ISO 9001:2026 — publication 16 September 2026**; DIS 27 Aug 2025; FDIS April 2026; ~3-year transition | `iso.org/standard/88464.html`; SGS, DQS and TÜV transition guidance |
| PCI DSS v4.0.1 current; v4.0 retired 31 December 2024; future-dated requirements effective 31 March 2025 | `blog.pcisecuritystandards.org` |
| OWASP ASVS 5.0.0, released 30 May 2025 | `owasp.org/www-project-application-security-verification-standard/` |

*Secondary (S1 / S2) — verified 2026-08-19, subject to `CUR-Q-01`*

| Item | Source |
|---|---|
| Personal Data Protection Act, 2026 (Law 63 of 2026); PDPO 2025 gazetted 6 Nov 2025; Amendment Ordinance No. 23 of 2026 of 5 Feb 2026; enforcement ≈13 May 2027; National Data Management Authority | Securiti overview · Digital Policy Alert · Prothom Alo |
| Cyber Security Ordinance, 2025 (No. 25 of 2025), gazetted 21 May 2025, repealing the Cyber Security Act 2023 | The Business Standard · Prothom Alo · Digital Policy Alert · Wikipedia *Cyber Security Act, 2023* |
| **Cyber Security Bill/Act 2026 — ordinance repealed and replaced, 30 April 2026**; Cyber Security (Amendment) Bill 2026 passed | Dhaka Tribune · BSS · Prothom Alo · Transparency International Bangladesh |
| Odoo 19 released 18 September 2025; three-version support policy; **Odoo 20 expected at Odoo Experience, 24–26 September 2026** | Odoo release and event listings; independent partner briefings |

> **Every external claim in this document is attributable to a source above and dated.** Where the
> source class is S, the row says so. This is `CUR-03` applied to the register's own references —
> because a currency register whose own evidence is unattributed would be a good joke and a bad
> control.

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture | Initial issue. 118 rows across three registers; 11 findings (1 CRITICAL, 3 High, 6 new to the programme); 8 decisions; 7 open questions; 6 checks; a gate-bound review calendar. Executes `00-06` §9, proposed and unexecuted since the first governance audit | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`RR-005` · Category 99 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
*1000FiX Services Limited · ERP Programme · Enterprise Architecture*
