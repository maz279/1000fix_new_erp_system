---
id: FIX-ERP2-PORTAL-AUDIT
title: Portal & Application Suite Specification Audit Report
scope: P01–P12 as issued 2026-08-13
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: FINDINGS ISSUED — REGISTER UPDATES REQUIRED
classification: CONFIDENTIAL — Internal Use Only
auditor: Enterprise Architecture
---

# Portal & Application Suite — Specification Audit Report
### Twelve portal files · 10,020 lines · 771 KB

---

## 1. Purpose and Method

This audit examined the twelve portal specification files issued on 2026-08-13 against the
portal principle and cross-portal standards in `04-00_Portal_Suite_Overview.md`, the governance
rules in `02-02` §1, the role and access matrix in `05-04`, and the sixty-seven module
specifications now present in `03_Modules`.

Five methods were applied.

| Method | What Was Checked |
|---|---|
| **Structural consistency** | Section completeness against the house 19-section structure; frontmatter against `04-00` §2; filename convention |
| **Identifier integrity** | `FR-POR`, `PRU`, `AC` and `CD` continuity, uniqueness and collision — within each file, across the suite, and **against all 67 module files** |
| **Boundary symmetry** | Every portal's out-of-scope claim checked against the module or portal named; every module claim directed at a portal checked for reciprocation |
| **Standards conformance** | The portal principle (`04-00` §1) and the twelve cross-portal standards (PS-01…PS-12) traced into each file's technical functions and portal rules |
| **Arithmetic and evidence** | Requirement and effort roll-ups; every regulatory, standards and vendor claim checked against a primary or authoritative secondary source |

**Result: 1 critical finding (found and corrected during the audit), 0 high, 5 medium and
3 low.** The critical finding is recorded in full because it arose from a change in the
repository between the specification work and the audit, and the same exposure will recur for
any future author.

---

## 2. Findings Summary

| Severity | Count | Definition |
|---|---:|---|
| **Critical** | 1 | Would cause a build against the wrong specification — **found and corrected before issue** |
| **High** | 0 | Materially misleading or missing |
| **Medium** | 5 | Register or cross-document updates required before these files are authoritative |
| **Low** | 3 | Precision improvements and decisions to confirm |
| **Total** | **9** | |

---

## 3. Critical Finding — Found and Corrected

### X-01 — Portal CD identifiers collided with fifteen module allocations

**Severity: Critical (as found) · Status: CORRECTED before issue · Type: Identifier collision**

**What happened.** The portal specifications were authored immediately after Category F, when
`03_Modules` contained specification files for Categories A–F only and the highest custom-
development identifier claimed anywhere was **CD-173** (M48). The portal suite was therefore
allocated **CD-174…187**, continuing from that ceiling and recording **CD-188 as the next free
ID**.

Between that allocation and this audit, **the remaining sixty-one module specifications were
completed**, and Categories G, H, I, J and K claimed identifiers **up to CD-199**. The portal
allocation collided with fifteen module claims:

| Portal ID | Also claimed by |
|---|---|
| CD-174, CD-175 | M51 Tax & Regulatory Compliance (Category G) |
| CD-176 … CD-179 | M53 Revenue Recognition, Commission & Settlement (Category G) |
| CD-180 … CD-182 | M49 Fixed Assets & Capital Investment (Category G) |
| CD-183 … CD-186 | M54 Cost Accounting, Budgeting & FP&A (Category G) |
| CD-187 | M62 Data Platform, Warehouse & Governance (Category J) |

**Correction applied.** The whole portal suite was reallocated **+26** to the range
**CD-200 … CD-213**, above the true ceiling of CD-199 (claimed by M63 Process Automation,
Category J):

| Portal | CD ID(s) | Portal | CD ID(s) |
|---|---|---|---|
| P01 | **CD-200** (web), **CD-201** (app) | P07 | **CD-207** (web), **CD-208** (app) |
| P02 | **CD-202** | P08 | **CD-209** |
| P03 | **CD-203** | P09 | **CD-210** |
| P04 | **CD-204** | P10 | **CD-211** |
| P05 | **CD-205** | P11 | **CD-212** |
| P06 | **CD-206** | P12 | **CD-213** |

**CD-214 is the next free identifier.** Verified: zero collisions against all 67 module files.

> **Root cause, and why it will recur.** `02-05` §5.2 registers only `cd_*` Odoo modules and
> assigns no identifiers to portal applications, which `02-05` §5.4 lists separately. In the
> absence of a single authoritative register, every author must derive the ceiling by scanning
> the repository — and that ceiling moves whenever another author commits. **This is the same
> exposure that audit finding M-01 in `02-05` already names.** Until a unified CD register
> exists, every new specification carries this risk. Raised again as **M-04** below with
> increased urgency.

---

## 4. Checks Passed

| # | Check | Result |
|---|---|---|
| P-01 | All 19 house sections present, in order, in all twelve files | **Pass** — 12/12 |
| P-02 | Frontmatter portal ID, code, wave and technology match `04-00` §2 | **Pass** — 12/12, including P01's split W2 web / W6 native delivery |
| P-03 | Filename convention consistent with the module files in the same directory | **Pass** — `P<nn>_<Name>.md` |
| P-04 | **`FR-POR` namespace integrity across all twelve files** | **Pass** — **358 requirements, 001…358 contiguous, zero gaps, zero duplicates.** This is the suite's single most important identifier check, because all twelve files share one namespace |
| P-05 | Declared requirement range and count match the requirements actually specified | **Pass** — 12/12 |
| P-06 | `PRU` portal-rule identifiers unique within each file | **Pass** — 224 rules |
| P-07 | Acceptance-criteria count matches the definition-of-done statement | **Pass** — 12/12 |
| P-08 | CD identifiers unique within the suite | **Pass** — 14 components, no duplicates |
| P-09 | CD identifiers do not collide with any of the 67 module files | **Pass** *after correcting X-01* |
| P-10 | Portal-suite CD block statement is internally consistent | **Pass** — carried in P01 §16.2 with each subsequent file referencing its predecessor |
| P-11 | Every internal document cross-reference resolves | **Pass** — the only unresolved reference is `06-02`, correctly and repeatedly flagged as *not yet issued* |
| P-12 | Every `04-00` per-portal KPI is adopted verbatim by its portal | **Pass** — 54 KPIs across 12 portals, all present |
| P-13 | Every `04-00` per-portal capability area is covered by at least one requirement | **Pass** — 12/12 |
| P-14 | The portal principle (`04-00` §1) is enforced as an explicit rule in every file | **Pass** — every file carries a class-H rule stating it persists no authoritative business state |
| P-15 | PS-11 (no client-side business rule) is enforced as an explicit rule in every file | **Pass** — 12/12 |
| P-16 | PS-01 (single sign-on via M29) and PS-02 (all traffic via the M28 gateway) are stated in every file | **Pass** — 12/12 |
| P-17 | PS-08 (offline with queued sync) is claimed by exactly the three portals `04-00` names | **Pass** — P02, P09, P11 only |
| P-18 | `04-00` §P07's four governance requirements are each a class-H portal rule in P07 | **Pass** — PRU-P07-01…04 |
| P-19 | `04-00` §P02's seven non-negotiable requirements each appear as a technical function in P02 | **Pass** — T-01…T-12 |
| P-20 | Role access matches `05-04` §2 exactly | **Pass** — including the negative cases: R36 only on P01, R16 only on P09, R34 only on P10, no external party on P03 or P06 |
| P-21 | Every module claim directed at a portal is reciprocated | **Pass** — verified for M15→P08 consignment reconciliation, M17→P04 estate, M45→P05 calibration and P11 verification, M46→P02/P09 pre-use check, M47→P05 facility vendors and P11 inspection, M48→P08 cohort reliability, M03→P09 custody |
| P-22 | Every regulatory and standards claim is traced to a source cited in §19 | **Pass** — WCAG 2.1 AA and 3.1.2, ISO 9001 clause 9.2, ISO/IEC 17025, KYC/KYB practice, IFRS-adjacent none claimed |
| P-23 | Architecture standards AS-08, AS-13 and AS-14 addressed where applicable | **Pass** — AS-13 in all three offline applications |
| P-24 | No portal specifies an L6 component except where `02-05` §5 approves one | **Pass** — P10 (CPaaS) and P07 (identity verification) only |

---

## 5. Medium Findings — Register Updates Required

### M-01 — `05-01` §4 portal requirement allocation is superseded by a factor of 2.6

**Owner: Enterprise Architecture · Target: `05_Cross_Cutting_Specifications/05-01` §4**

`05-01` §4 allocates `FR-POR-001 … FR-POR-140` across the twelve portals with `141–180`
reserved. Measurement supersedes it:

| Portal | `05-01` | Measured | Δ | Portal | `05-01` | Measured | Δ |
|---|---:|---:|---:|---|---:|---:|---:|
| P01 | 26 | **40** | +14 | P07 | 16 | **34** | +18 |
| P02 | 22 | **38** | +16 | P08 | 7 | **26** | +19 |
| P03 | 18 | **34** | +16 | P09 | 8 | **28** | +20 |
| P04 | 16 | **32** | +16 | P10 | 6 | **28** | +22 |
| P05 | 9 | **26** | +17 | P11 | 3 | **24** | +21 |
| P06 | 7 | **24** | +17 | P12 | 2 | **24** | +22 |
| | | | | **Total** | **140** | **358** | **+218** |

The reserved block (141–180) is insufficient by a wide margin. The files therefore use a
**contiguous re-allocation of `FR-POR-001 … FR-POR-358`** preserving the existing portal
ordering, with **359–400 reserved**:

| Portal | Range | Portal | Range |
|---|---|---|---|
| P01 | FR-POR-001 … 040 | P07 | FR-POR-195 … 228 |
| P02 | FR-POR-041 … 078 | P08 | FR-POR-229 … 254 |
| P03 | FR-POR-079 … 112 | P09 | FR-POR-255 … 282 |
| P04 | FR-POR-113 … 144 | P10 | FR-POR-283 … 310 |
| P05 | FR-POR-145 … 170 | P11 | FR-POR-311 … 334 |
| P06 | FR-POR-171 … 194 | P12 | FR-POR-335 … 358 |

`05-01` §4 requires replacement with this table.

> **Why the original allocation was so far out.** The `05-01` figures were extrapolated from
> `04-00`'s capability tables, which describe *what* each portal does but not the requirements
> needed to specify it testably. The undercount is largest exactly where `04-00` is most
> compressed — P11 (3 → 24) and P12 (2 → 24) are described in `04-00` in a handful of lines each
> but are complete applications.

### M-02 — Portal effort is not represented in the programme estimate

**Owner: Enterprise Architecture / Programme Manager · Target: `02-05` §5.1 and §5.4**

Measured portal effort is **298 person-weeks**. `02-05` §5.4 records 6 Next.js portals at
148 PW and 4 Flutter applications at 126 PW — **274 PW for ten deliverables**, with P03 (Odoo
web client) and P06 (Metabase/Grafana) not counted at all.

| Grouping | `02-05` §5.4 | Measured |
|---|---:|---:|
| The ten application deliverables | 274 PW | **252 PW** |
| P03 Admin Operations Portal | not counted | **30 PW** |
| P06 Analytics & Executive Dashboard | not counted | **16 PW** |
| **Total** | **274 PW** | **298 PW** |

The ten counted deliverables come in slightly under estimate; the gap is the two surfaces the
register omits.

> **The larger estimating risk is inside P03.** Its 30 PW covers the **workspace framework and
> three purpose-built consoles only**. The content of the other eleven consoles is specified and
> costed within each owning module. A plan reading "P03 = 30 PW → fourteen complete consoles"
> would understate the work by an order of magnitude. This is recorded in `P03` §16.2 and raised
> as `P03` Q-09.

### M-03 — Portal KPIs require identifier allocation

**Owner: Enterprise Architecture · Target: `06-02` (not yet issued)**

No portal has a `KPI-0nn` identifier. **168 unnumbered metrics** are specified across the twelve
files, of which the **54 KPIs named in `04-00`** are adopted verbatim and **114 are new**.
Existing numbered KPIs (KPI-002, KPI-004, KPI-011, KPI-041, KPI-042, KPI-050) are cited as
**supported**, never claimed.

`06-02_KPI_Benefits_and_Acceptance_Criteria.md` is referenced by every portal file, by the
Category F files and by `M15`, but **does not exist**. Until it is issued, no specification in
the repository can allocate a KPI identifier, and this finding recurs for every category and
every portal.

### M-04 — The unified CD register is now urgent, not deferred

**Owner: Enterprise Architecture · Target: `02-05` §5**

Finding X-01 above is the second manifestation of an issue `02-05` already carries as audit
finding M-01. The repository now contains **67 module files and 12 portal files claiming
CD-001 … CD-213 across nine independent authoring efforts**, with no single register.

Required:

| Action | Detail |
|---|---|
| Create the unified register | One table, every CD ID, its owner, its type (Odoo module, service, application), its effort |
| Record the reallocations | Category E (CD-139…156), Category F (CD-157…173, plus CD-078/079 moved M17 → M48), portals (**CD-200…213**) |
| Record the ceiling | **CD-213 claimed; CD-214 next free** |
| Add a claiming procedure | So the next author does not derive the ceiling by scanning |

### M-05 — Portal specifications are filed outside the portal documentation area

**Owner: Enterprise Architecture / CTO · Target: filing decision**

The twelve portal specifications are filed in
`03_Modules/K_Platform_and_Technology/` **at the requester's explicit direction**, alongside
the seven Category K *module* specifications (M28, M29, M30, M64, M65, M66, M67).

This creates three inconsistencies with the repository's own structure:

| Inconsistency | Detail |
|---|---|
| **Object types are mixed** | The directory now holds two different object classes — modules and portals — with different identifier schemes (`M<nn>` / `FR-<CODE>` versus `P<nn>` / `FR-POR`) |
| **The category overview does not describe them** | `K_Platform_and_Technology/_CATEGORY_OVERVIEW.md` states "**7 modules**" and describes only the technical substrate. It does not mention P01–P12, and its §2 module table, §9 category KPIs and §10 delivery sequence exclude them |
| **The architecture counts them separately** | `_CATEGORY_OVERVIEW.md` §1 refers to "67 modules, **12 portals**" as distinct populations, and `04_Portals_and_Applications/` exists for precisely this content |

**Recommendation:** either (a) move the twelve files to `04_Portals_and_Applications/`, which
requires no content change since every file's `category:` field already reads *"Portal &
Application Suite (filed under K — Platform & Technology)"*; or (b) retain the current location
and amend `K_Platform_and_Technology/_CATEGORY_OVERVIEW.md` to state that the directory holds
7 modules **and** 12 portals, with the portals' KPIs and delivery sequence added.

**Option (a) is recommended.** Option (b) makes Category K structurally unlike every other
category. This is a filing decision for the CTO, and it is recorded here so the inconsistency is
a known choice rather than an accident.

---

## 6. Low Findings

### L-01 — Cross-portal standards are cited selectively rather than exhaustively

**Severity: Low · Type: Precision**

All twelve files bind themselves to *"the twelve cross-portal standards in `04-00` §3"* in their
definition of done, and each cites inline the standards that bear materially on it — between
6 and 11 of the 12 per file. PS-01, PS-02, PS-03, PS-09 and PS-11 appear in all twelve; PS-06
(design system) and PS-10 (instrumentation) appear only where the portal shares the component
library or owns a critical funnel.

This is defensible — a blanket citation of all twelve in every file would add noise without
information — but a reviewer checking conformance to a specific standard must read the
definition of done rather than search for the token. **No action required; recorded for
reviewers.**

### L-02 — Three portals depend on components that land after they do

**Severity: Low as documentation · Medium as delivery risk · Type: Sequencing**

Each is recorded on both sides, and each is a real interim gap:

| Portal | Wave | Depends on | Lands | Interim position |
|---|:--:|---|:--:|---|
| **P02** | W2 | **M45** instrument fitness gate (FR-POR-068) | W5 | Instrument identified but **not fitness-verified** for three waves. Recorded in `P02` §16.3 and `M45` §16.3 |
| **P09** | W3 | **M46** vehicle pre-use check (FR-POR-258) | W5 | Riders who drive complete **no in-app check** for two waves. Recorded in `P09` §16.3 |
| **P10** | W4 | **L6 CPaaS provider** | procurement | The console **cannot be built against an unknown platform**. Recorded as `P10` Q-01, needed W4 minus 6 months |

The first two are accepted gaps that must not be forgotten at the Wave 5 gate. The third is a
procurement dependency on the critical path and is the most likely cause of a P10 slip.

### L-03 — The offline journal is reused three times, and its owner is not named

**Severity: Low · Type: Ownership**

P02 builds the append-only offline journal, idempotent ordered replay, three-tier conflict
policy and sync reporting in Wave 2. **P09 reuses it in Wave 3 and P11 in Wave 5.** The reuse is
stated from both sides in all three files and is the single largest structural efficiency in the
suite — it is why P09 costs 22 PW and P11 costs 16 PW rather than roughly 35 and 26.

However, **no file names the component's long-term owner.** A shared component reused by three
applications across three waves, with no named owner, is a maintenance liability. It should be
assigned to the Field Platform Squad as a versioned internal library with its own change
control.

---

## 7. Suite-Level Observations

### 7.1 The portal principle holds throughout

`04-00` §1 states that no portal holds authoritative state and no portal implements business
rules. Every one of the twelve files enforces both as **class-H portal rules**, and the
acceptance criteria test them:

| Portal | "No authoritative state" | "No client-side business rule" |
|---|---|---|
| P01–P12 | PRU-P**nn**-01 or -02 in every file | PRU in every file, plus a technical function |

**P03 is the instructive exception, and it is handled correctly.** As the Odoo web client it has
no data boundary at all — no projection, no cache, no synchronisation — and instead carries two
stronger rules: it adds no table and no field (PRU-P03-02) and implements no business logic
(PRU-P03-01), both tested by schema diff and static analysis. That is the right adaptation of
the principle to a surface that is not a separate application.

### 7.2 Three portals hold the estate's hardest privacy boundaries

| Portal | Boundary | Enforced by |
|---|---|---|
| **P08** Brand Partner | **No customer identity, contact, address or unrelated history reaches a brand partner — including in audit mode** | PRU-P08-01, AC-01, cohort minimum-population suppression |
| **P04** Corporate B2B | No cross-organisation data exposure | PRU-P04-01, AC-01, named the portal's highest-severity test |
| **P12** Partner & Referral | A partner sees only the leads they submitted — never the customer base | PRU-P12-02, AC-01 |

Each is stated as the portal's highest-severity acceptance criterion and each is tested by
penetration test rather than by review. P08's is the most commercially pressured — a brand
partner is a powerful counterparty who would find customer data valuable — and it is the one
most likely to be challenged in negotiation.

### 7.3 The suite's four "zero" targets are all custody or integrity measures

| Target | Portal | Source |
|---|---|---|
| Offline sync failures: **zero** | P02 | `04-00` §P02 |
| Custody breaks: **zero** | P09 | `04-00` §P09 |
| Journal entries lost: **zero** | P02, P09, P11 | Specified here |
| Commission accuracy: **100%** | P12 | `04-00` §P12 |

Three of the four are guaranteed by the same component — the offline journal (L-03) — which
concentrates a great deal of the suite's integrity commitment in one piece of software and
reinforces the case for naming its owner.

### 7.4 Screen switches: the only design-governing metric in the suite

`04-00` §P10 sets **agent screen switches per contact under 3**. P10 §6 T-03 elevates it from a
KPI to a design constraint: *"a capability requiring a fourth is redesigned or explicitly
accepted as a P03 hand-off."* This is the only instance in the suite where a measured user-
experience number governs scope decisions, and it is the correct treatment for the surface where
30–60 people spend an entire shift.

### 7.5 Bengali is a release gate in eleven of twelve portals

Every portal except P08 (English-primary, reflecting an international brand-partner audience)
makes complete Bengali a class-H rule and a release gate, consistent with `04-00` PS-03 and
AS-12. Three portals go further and make **Bengali the default**: P01 (customers), P02
(technicians) and P09 (riders) — the three highest-volume human audiences in the estate.

Two files independently raise the same resourcing question — `P01` Q-11 and `P10` Q-09 — about
who owns Bengali content. **The Company should answer it once**; machine translation is excluded
by `04-00`, which makes this a staffing commitment, not a tooling choice.

---

## 8. Register Update Worklist

| # | Action | Target | Owner | Priority |
|---|---|---|---|---|
| 1 | **Create the unified CD register**; record CD-200…213 for portals and CD-214 as next free | `02-05` §5 | Enterprise Architecture | **Urgent — X-01 will recur** |
| 2 | Replace the `FR-POR` allocation with the 001…358 table in §5 M-01 | `05-01` §4 | Enterprise Architecture | High |
| 3 | Add 298 PW of portal effort to the programme estimate; note the P03 costing caveat | `02-05` §5.1, §5.4 | Programme Manager | **Before the next planning cycle** |
| 4 | Issue `06-02` and allocate KPI identifiers for 119 new portal metrics | `06-02` | Enterprise Architecture | Medium |
| 5 | **Decide the filing question**: move to `04_Portals_and_Applications/`, or amend the K category overview | Filing | CTO | **High — structural** |
| 6 | Name the owner of the shared offline journal component | Delivery plan | CTO / Field Platform Squad | Medium |
| 7 | Contract the L6 CPaaS provider | Procurement | CTO / CFO | **W4 minus 6 months** |
| 8 | Confirm the P02/M45 and P09/M46 interim gaps at the Wave 5 gate | Wave 5 gate | Operations Director | Wave 5 |
| 9 | Resolve Bengali content ownership once, for P01 and P10 together | Resourcing | CCO / Marketing Head | **W2 minus 3 months** |
| 10 | Establish the P10 AHT and FCR baseline before deployment | `P10` Q-02 | Customer Service Manager | **W4, before go-live** |

---

## 9. Earliest Open Questions Across the Suite

144 open questions are recorded across the twelve files — twelve per portal. Those needing an
answer earliest:

| Question | File | Owner | Needed by |
|---|---|---|---|
| Which CPaaS provider is contracted, and does its SDK support embedded softphone, barge-in, whisper and recording streaming? | P10 Q-01 | CTO / CFO | **W4 − 6 months** |
| Which accredited identity-verification provider, at what per-check cost, for both NID and trade licence? | P07 Q-01 | CCO / CTO / CFO | **W7 − 6 months** |
| Metabase Enterprise or Apache Superset? Row-level security is a hard requirement with a licence-cost consequence | P06 Q-02 | CTO / CFO | **W4 − 3 months** |
| Is the branch hardware baseline confirmed as 1366×768, and what is the actual estate? | P03 Q-01 | CTO | **W1 − 2 months** |
| What is the technician device estate, and is it company-issued or BYOD? | P02 Q-01/Q-02 | CTO / HR Director | **W2 − 4 months** |
| Can the legacy tracking URL be redirected, and who controls the DNS? | P01 Q-02 | CTO | **W2 − 3 months** |
| Who owns Bengali content? *(P01 Q-11 and P10 Q-09 are the same question)* | P01 / P10 | CCO / Marketing Head | **W2 − 3 months** |
| What consent purposes must be presented separately, and has Legal approved the Bengali wording? | P01 Q-08 | CCO / Legal | **W2 − 2 months** |
| Is a booking permitted without login? The single largest funnel decision | P01 Q-04 | CCO | **W2 design** |
| Is portal-only PO acknowledgement and invoicing mandated after a transition period? | P05 Q-02 | Procurement / CFO | **W3 design** |
| What is the current AHT and FCR baseline? | P10 Q-02 | Customer Service Manager | **W4, before deployment** |
| Are the eleven module-owned P03 consoles costed inside their modules' estimates? | P03 Q-09 | CTO / Programme Manager | **W1 planning** |

**Questions the Company should answer once, not eleven times:**

| Recurring question | Raised in |
|---|---|
| Are quality/behaviour scores an input to incentives, or to coaching only? | P02, P10, M46 |
| Is continuous location during shift acceptable, or is event capture the limit? | P02 Q-05, P09 Q-11 |
| Is partner/seller commission subject to tax withholding, and at what rate? | P07 Q-09, P12 Q-08 |
| Which brands will use a portal, and which mandate their own system? | P08 Q-01, M15 Q-07, M17 Q-03 |

---

## 10. Audit Conclusion

The twelve portal specifications are **structurally sound, internally consistent, and consistent
with the sixty-seven module specifications and the portal suite overview**. The shared
`FR-POR` namespace — the suite's principal integrity risk, since twelve files write into one
sequence — is contiguous across 358 requirements with zero gaps and zero duplicates. Every
`04-00` capability area and KPI is covered, role access matches `05-04` §2 exactly including its
negative cases, and every boundary directed at a portal by a module is reciprocated.

**One critical finding was found and corrected**: the portal CD allocation collided with fifteen
module claims made after the portal work was authored. The suite was reallocated to
**CD-200…213** and re-verified clean against all 67 module files. That collision is not an
authoring error so much as a symptom — the repository has no single CD register, nine
independent authoring efforts have now claimed identifiers, and **the next author faces the same
exposure**. Item 1 of the worklist is consequently marked urgent.

The five medium findings are all register updates outside the portal files. Two are material to
planning: the `FR-POR` allocation is superseded by a factor of 2.6 (**M-01**), and 298 person-
weeks of portal effort are only partly represented in the programme estimate, with a specific
under-costing hazard inside P03 (**M-02**).

One decision is genuinely open rather than merely pending: **these files are filed in Category K
at explicit direction, and that placement is structurally inconsistent with the repository's own
model** (**M-05**). It is recorded so the inconsistency is a known choice.

**Recommendation: accept the twelve specifications, and open the ten-item register worklist in
§8 — beginning with the unified CD register.**

---

*Portal & Application Suite Audit · 1000FiX ERP System v2.0 · CONFIDENTIAL*
