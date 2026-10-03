---
id: FIX-ERP2-AUDIT-017
title: Category 17 OP — Operations, Support & Runbooks Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-20
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 16 Category 17 OP files, the severity and fallback identifier spaces they own, their citations into the module repository and the content register, cross-register integrity, gate F7, the operational controls the category asserts but the company does not yet operate, and the inbound findings carried from AUDIT-014, AUDIT-015 and AUDIT-016
mandate: Audit required on completion of Category 17 authoring (rule CM-R9)
extends: AUDIT-001 … AUDIT-016
enumeration_date: 2026-08-20
method: Filesystem enumeration and identifier extraction only (RG-06, CP-11). No figure in this report is projected, and none is taken from what a document says about itself — including this category's own files. Where a figure contradicts an upstream specification, the enumeration is stated and the specification is the finding.
---

# Category 17 `OP` — Operations, Support & Runbooks Content Audit
### 16 files · **428 of 452** registered content files now written *(enumerated 2026-08-20)*

---

## 1. Method and result

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F7 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration and extraction. **Enumeration date
2026-08-20.**

Nine category-specific extractions were run:

| Extraction | What was compared |
|---|---|
| **Z1** | Every content identifier cited by the category against the 452 register rows |
| **Z2** | The `05-03` integration catalogue re-enumerated row by row, and its own priority summary and P0 fallback register compared against that enumeration |
| **Z3** | Every `NFR-`, `INT-`, `KPI-`, `IP-`, `OPS-`, `DI-`, `Mnn` and `Pnn` identifier checked against its declared range |
| **Z4** | Every `BRU-`, `FR-`, `Gn-nn`, `A-nn`, `TE-En`, `CON-nn` and `DM-nn` identifier resolved to its owning document |
| **Z5** | Every intra-category citation compared against the two files' register waves, to detect consumption before existence |
| **Z6** | All 24 required front-matter keys in all 16 files, and the seven `F7` reconciliation dimensions |
| **Z7** | Template conformance by `content_type` — six sections for Generic, eleven for Runbook, five for Notification |
| **Z8** | The category's `bilingual:` flags against `CG-010` §3.2's per-category allocation |
| **Z9** | Relative-link density against every completed sibling category |

**Twenty-six findings — 1 critical, 9 high, 11 medium, 5 low.** Four were remediated during the
audit; twenty-two are open, and **sixteen of those are owned outside the content function**.

| Severity | Count | Fixed | Open |
|---|---:|---:|---:|
| Critical | 1 | 0 | 1 |
| High | 9 | 0 | 9 |
| Medium | 11 | 1 | 10 |
| Low | 5 | 3 | 2 |
| **Total** | **26** | **4** | **22** |

> **The characteristic finding of this category is different from every category before it.**
> Categories 00–16 and 18 were audited mainly for *internal* integrity — do the identifiers resolve,
> do the counts reconcile, is the Bengali present. Category 17 passes those checks almost cleanly
> (§2). Its findings are about something else: **this category documents operational controls that
> the company does not yet operate.** A break-glass procedure with no vault, a rota with no
> engineers, a DR playbook with no DR environment, and a fallback set with no printed forms are not
> content defects. They are the content correctly describing an absence — and that absence is what
> the audit records.

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | **16 of 16** ✅ |
| **A2** Total written | **428 of 452**, enumerated 2026-08-20; only `MM` (12) and `RF` (12) remain ✅ |
| **A5** Files on disk with no register entry | **Zero** — across the whole repository, not only this category ✅ |
| **B1** ID uniqueness | 16 unique ✅ |
| **B2** Contiguity `OP-001`…`OP-016` | No gaps ✅ |
| **B4** File name matches ID | 16 of 16 ✅ |
| **C1/C2** `purpose:` and `traces_to:` present | 16 of 16 ✅ |
| **D1** Internal links resolve | **356 relative links, zero broken** ✅ *(links added during this audit — finding OP-22)* |
| **D2** Files in their declared location | **16 flat**, matching Master Index §3 — Category 17 declares no subfolders ✅ |
| **D3** No spaces or ampersands in any path | Zero ✅ |
| **E7** Template conformance | **All 11 `TPL_Runbook` sections present in all 6 runbook files; all 6 `TPL_Content_File_Front_Matter` sections in all 7 generic files; all 5 `TPL_Notification_Template` sections in all 3 notification files** ✅ |
| **F1** Front matter complete | **All 24 required keys present in all 16 files, no extra keys** ✅ |
| **Z1** Content-ID citations | **99 distinct content identifiers cited, 99 resolve** against the 452 register rows — **zero unresolved** ✅ |
| **Z3** Range checks | 48 distinct `NFR-` cited, all within `NFR-001`…`NFR-101`; 21 `INT-` all within `INT-001`…`INT-047`; 6 `KPI-` within `KPI-085`…`KPI-094`; `IP-01`…`IP-10`, `OPS-01`…`OPS-08`, `DI-04`…`DI-07` all in range; 20 modules all within `M01`…`M67`; all 12 portals valid ✅ |
| **Z4** Technical identifiers | `BRU-ADM-02`, `BRU-SEC-06` resolve in `05-05`; `BRU-QMS-02`, `BRU-QMS-09` in `M23` §9; `FR-ITS-008`, `FR-ITS-009`, `FR-ITS-030` in `M66` §5; `G1-01`, `G1-12`, `G2-01`, `G2-10`, `G3-01`, `G3-09`, `G4-01`, `G4-09` in `06-02` §4; `A-85`, `A-86` in `SP-004`; `TE-E1`, `TE-E9`, `TE-E12` in `SP-005`; `CON-03` in `05-03` §3; `DM-15` in `05-02` — **all resolve** ✅ |
| **Z7** Content-type allocation | Generic 7, Runbook 6, Notification 3 — each matched to the template it declares ✅ |
| **Z8** Bilingual allocation | **Exactly `OP-003`, `OP-004`, `OP-005`, `OP-014` carry `bilingual: yes`** — the four files `CG-010` §3.2 names, no more and no fewer ✅ |
| **G2** Content class | 13 Class C, 3 Class D; gate sets declared in every Definition of Done ✅ |

### 2.1 Cross-register reconciliation — gate F7

**All seven dimensions reconcile exactly.**

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---|---:|:--:|
| File count | Master Index §4 | 16 | 16 | ✅ |
| Priority `P0`/`P1`/`P2`/`P3` | Master Index §1 | 5 / 8 / 3 / 0 | 5 / 8 / 3 / 0 | ✅ |
| Wave per file | Master Index §4 rows | 16 matches | 16 matches | ✅ |
| Filename per file | Master Index §4 rows | 16 byte-identical | 16 byte-identical | ✅ |
| Owner per file | Master Index §4 rows | 16 semantically equal | 16 semantically equal | ⚠ *lexical variance — finding OP-25* |
| Bilingual count | `CG-010` §3.2 | 4 | 4 | ✅ |
| Register rows vs disk, both directions | `CP-11` | 0 / 0 | 0 / 0 | ✅ |

### 2.2 Wave distribution as authored

| Wave | Files |
|:--:|---|
| W1 | 10 — `OP-001`, `OP-002`, `OP-003`, `OP-004`, `OP-006`, `OP-007`, `OP-009`, `OP-013`, `OP-014`, `OP-015` |
| W2 | 4 — `OP-005`, `OP-011`, `OP-012`, `OP-016` |
| W3 | 1 — `OP-008` |
| W4 | 1 — `OP-010` |

---

## 3. Findings

### OP-01 — The lawful disaster-recovery path for Bangladesh-resident personal data does not exist

**Severity: CRITICAL · Status: OPEN · Owner: CTO with Legal Counsel and the DPO**

**What was found.** `NFR-086` requires Sensitive Personally Identifiable Data — NID, passport, TIN,
biometric templates and recovered customer data — to be held in a **Bangladesh-resident** store, and
`NFR-086b` requires an Authority notification and a documented safeguard **before** any cross-border
transfer of a residency-classified field executes.

`OP-012` §4.3 therefore has only three possible recovery routes for that store, and **the only
lawful one is unavailable**:

| Route | Available? |
|---|---|
| Operate without the sensitive fields until the store returns | Yes — degraded, and only for an unreachable store, not a lost one |
| Restore from a resident backup to a **resident** target | **No resident DR target exists** |
| Restore into the regional environment | **A regulatory act** under `NFR-086b`, requiring Authority notification and a documented safeguard *before* execution |

**Why it is critical.** In an outage affecting the resident store, an engineer at 02:00 has a choice
between a two-hour RTO and a cross-border transfer of exactly the data category the Act singles out.
`OP-012` `RD-01` forbids the second, correctly. That leaves **no route that both restores service
and complies**, and the constraint is invisible until the night it binds.

**What the content did.** `OP-012` §4.3 states the sequence, `RD-01` states the prohibition in
advance, and `OP-012` OI-02 records the gap. Content cannot close it.

**Action.** Provision a Bangladesh-resident DR target for the residency-classified store, **or**
obtain, in advance and in writing, the Authority position on emergency cross-border restoration with
a pre-documented safeguard. **Before W2.** Until one of those exists, `NFR-007` does not apply to
residency-classified data and the programme should say so rather than imply otherwise.

---

### OP-02 — The disaster recovery environment is named in the architecture and provisioned nowhere

**Severity: HIGH · Status: OPEN · Owner: CTO with Platform Engineering**

**What was found.** `02-05` §9 lists six environments — `local`, `dev`, `staging`, `training`,
`prod`, **`dr`**. `02-05` §8.1 sizes and costs **five**. The `dr` environment appears in no sizing
table, no cost progression and no infrastructure line.

Three further preconditions of `NFR-007` are also absent:

| Requirement | State |
|---|---|
| Continuous WAL archiving to a **separate failure domain** (RPO ≤ 15 min) | Not provisioned (`OP-007` OI-03) |
| An **immutable backup copy outside the primary provider account** | Not provisioned (`OP-012` OI-03) — without it, the ransomware and account-compromise scenarios in `OP-012` §5 have no assured recovery path |
| A rehearsed failover (`NFR-051`: twice yearly, documented) | No exercise scheduled anywhere in `06-01` (`OP-012` OI-07) |

**Consequence.** `NFR-007` (RPO 15 min / RTO 2 h) is currently an aspiration with no infrastructure
behind it, and `OP-012` is a design document rather than an executable playbook. The honest RAG
status for DR readiness is **red**, and `OP-012` §3 `HC-01` requires that to be reported monthly to
the Steering Committee.

**Action.** Size, cost and provision `dr`; add the two backup preconditions; schedule the first full
exercise before the W2 gate. Owner: CTO. **This is the largest unfunded operational obligation the
content register has surfaced.**

---

### OP-03 — `05-03`'s P0 fallback register omits a P0 integration, and its priority counts are wrong

**Severity: HIGH · Status: OPEN (upstream) · Owner: Enterprise Architecture**

**What was found.** Extraction `Z2` re-enumerated `05-03` §2.1–§2.7 row by row:

| Priority | `05-03` §2 summary states | **Enumerated 2026-08-20** | Variance |
|---|---:|---:|---:|
| P0 | 12 | **13** | +1 |
| P1 | 17 | **14** | −3 |
| P2 | 12 | 12 | 0 |
| P3 | 6 | **8** | +2 |
| Total | 47 | 47 | 0 |

Separately, the **P0 fallback register in `05-03` §7 has no entry for `INT-013` (email)**, which the
catalogue marks `P0`. `IP-09` requires a defined manual fallback for **every** P0 integration, and
`NFR-050` makes it a tested one. Email is the delivery path for invoices, corporate notifications
and inbound ticket parsing.

The §7 register also contains fallbacks for `INT-015` telephony (P1) and `INT-043` LLM inference
(P2). Holding a fallback for a non-P0 integration is good practice; **counting those entries as
evidence of P0 coverage is what makes the register read as complete when it is not.**

**Consequence.** Any statement of the form *"all twelve P0 integrations have a documented fallback"*
is wrong in both the numerator and the denominator.

**What the content did.** `OP-014` §4.4 enumerates **thirteen** P0 integrations, supplies `FB-05` for
email, and separates the four non-P0 procedures into §4.5 with an explicit note that they do not
count toward `IP-09` coverage. `OP-008` §7 carries the same correction for the engineering audience.

**Action.** Correct `05-03` §2's priority summary and add `INT-013` to §7. Owner: Enterprise
Architecture. Content has compensated; the specification is still wrong.

---

### OP-04 — Platform incident severity had three claimed owners and no owner

**Severity: HIGH · Status: OPEN (upstream corrections) · Owner: Business Process Lead and QA Lead**

**What was found.** Before this category existed, four documents pointed at the platform severity
scale and three of them pointed at the wrong place:

| Document | Points at | Correct? |
|---|---|---|
| `NT-021` §2.1 | Defines `Sev1`–`Sev4` itself and routes response "per `OP-013`" | ✅ — the only correct pointer |
| `SP-005` §5 and §12 | "`OP-008` — technical severity classification" | ❌ `OP-008` is a component runbook |
| `SP-031` §2 | "Technical incident runbooks and severity classification → `OP-008`" | ❌ same |
| `TS-018` §2 | "IT incident management and its own severity scale → `M66`, `SP-031`, `OP-002`" | ❌ `M66` owns *ticket priority*; `OP-002` is the hypercare plan |

An engineer following `SP-005` at 02:00 reaches a runbook containing no severity table.

**What the content did.** `OP-013` §4.1 now carries the canonical scale, extending `NT-021`'s
definitions with acknowledgement, cadence, authority and review obligations; §4.2 sets out the four
distinct scales in the programme (`Sev1`–`Sev4` platform, `S1`–`S4` defect, `MD-028` service,
`M66` ticket) and the only three sanctioned relationships between them. `OP-008` OI-06 records the
conflict from the other end.

**Action.** Three one-line corrections: `SP-005` §5/§12 and `SP-031` §2 to point at `OP-013` §4.1;
`TS-018` §2 to distinguish platform severity from IT ticket priority. Until made, the register
contains a control with two published owners.

---

### OP-05 — Thirty-eight intra-category dependencies invert the register's waves

**Severity: HIGH · Status: OPEN (register change proposed) · Owner: Programme Office**

**What was found.** Extraction `Z5` compared every intra-category citation against the two files'
register waves. **Thirty-eight citation pairs run backwards in time.** The material ones:

| Needed at | File | Register wave | Cited by |
|:--:|---|:--:|---|
| **W1** | `OP-005` Status page and maintenance copy | **W2** | `OP-001`, `OP-002`, `OP-003`, `OP-004`, `OP-006`, `OP-007`, `OP-009`, `OP-013`, `OP-014` — nine W1 files |
| **W1** | `OP-016` Post-incident review | **W2** | `OP-002` (`HX-17` is a W1 hypercare exit criterion), `OP-004`, `OP-007`, `OP-009`, `OP-013`, `OP-014`; and `NT-021` `AL-07` (W1) requires a review for every W1 `Sev1`/`Sev2` |
| **W1** | `OP-008` Integration and event runbook | **W3** | `NT-021` (W1) names it as the remedy for four W1 alerts; `OP-002`, `OP-007`, `OP-009` cite it |
| W2 | `OP-010` Data platform runbook | W4 | Time-series ingestion — the only irreplaceable data store — starts at W2 (`02-05` §4) |

**Consequence.** `OP-004` (W1) tells users to follow a status page that the register does not
require until W2. `OP-002`'s hypercare cannot meet `HX-17` at W1. `NT-021`'s alerts point at a
runbook two waves away.

This is now unmistakably systemic. `AUDIT-014` TS-02 recorded the fourth consecutive category,
`AUDIT-015` RP-05 added five, and `AUDIT-016` AP-03 took the register-wide total to **39 files
across six categories**. Category 17 adds **four files** — `OP-005`, `OP-008`, `OP-010`, `OP-016` —
taking it to **43 across seven categories**. The cause is the same every time: **the register
assigns a wave by the module a file traces to, not by the wave of the file that consumes it.**

**Action.** Register change: `OP-005` → W1, `OP-016` → W1, `OP-008` → W1, `OP-010` → W2. Owner:
Programme Office. The alternative — leaving them — means W1 operates without a status page, without
a review method and without an integration runbook, which is what the first wave will actually
experience.

---

### OP-06 — The support model is `P0` at W1 and the platform it runs on arrives at W6

**Severity: HIGH · Status: OPEN · Owner: CTO**

**What was found.** `OP-001` is `P0`/**W1** and traces to `M66`. `M66` §1 is `P2`/**W6 (Months
23–26)**, verified 2026-08-20. `OP-003` (`P1`/W1) traces to the same module. The register carries no
lead-time note on either row.

Consequences that follow from the twenty-month gap:

| Capability | Before W6 |
|---|---|
| Ticketing | OCA `helpdesk` in `P03` — adequate, and the same substrate `M66` later builds on |
| SLA clock | No holiday-calendar awareness — **SLA attainment cannot be reported before W6** |
| Escalation on breach | Manual, by one supervisor, from a daily review — a named single point of failure |
| CMDB and asset register | Neither exists; the `100% of company IT assets tracked` KPI is unevidenceable |
| **Paging** | **No paging platform is named anywhere in `02-05`.** `OP-013` §4.4 describes acknowledgement and auto-escalation the programme cannot currently perform |

**What the content did.** `OP-001` §4.9 sets out the interim model capability by capability and
names what each interim costs; `OP-013` OI-05 records the paging gap.

**Action.** Either accept the interim model explicitly (Steering decision) or bring the `M66`
ticketing and paging subset forward to W1. **The paging gap is the sharper of the two**: an on-call
rota with no paging mechanism is a telephone list.

---

### OP-07 — `NFR-091` requires 67 module runbooks and the register contains none

**Severity: HIGH · Status: OPEN · Owner: CTO with Programme Office**

**What was found.** `05-06` §7 `NFR-091`: *"Every module ships with an operational runbook"*, `P0`.
`02-05` §9 repeats it as a definition-of-done item: *"Every module ships with a README, a runbook and
its OpenAPI specification"*.

The content register carries **five component runbooks** (`OP-007`…`OP-011`) and one playbook
(`OP-012`). They are scoped to platform components — ERP core, integration, identity, data platform,
mobile — **not to any of the 67 modules**. No module-level runbook is registered.

**Two readings, and the programme has not chosen one:**

| Reading | Consequence |
|---|---|
| Component runbooks satisfy `NFR-091` | Then `NFR-091` should say so, and `02-05` §9's per-module definition of done should be amended |
| `NFR-091` means what it says | **67 module runbooks are an unregistered content obligation** — at the observed 20–35 KB per runbook, that is a body of work comparable to two entire content categories |

**Action.** Decide, and amend either `NFR-091` or the register. Recorded in `OP-007` OI-05.

---

### OP-08 — Break-glass access is documented and does not exist

**Severity: HIGH · Status: OPEN · Owner: CTO with Security Lead**

**What was found.** `OP-009` §9 and `OP-007` §9 describe a break-glass capability with five
components: a vault break-glass path, a sealed offline credential envelope in the head-office safe,
two named signatories, quarterly testing (`BG-10`), and immediate rotation after use (`BG-11`).

**None of it exists.** There is no vault path, no envelope, no safe procedure, no named holders and
no test schedule. `OP-009` OI-01 states it as the highest-priority open item in the category.

**Why it matters more than it looks.** Break-glass is the single control that makes the `PS-01`
architecture safe: every portal depends on one identity provider, deliberately, and break-glass is
the compensating control for that concentration. An identity outage with no break-glass path means
administrative recovery is improvised under `Sev1` conditions — which is precisely the circumstance
in which improvised privileged access becomes an unattributable production change.

**Action.** Establish the vault path, the sealed envelope, the signatories and the quarterly test
**before W1 go-live**. This is days of work, not months, and it is the cheapest high-severity item
in this report.

---

### OP-09 — The on-call rota needs ten people and has none

**Severity: HIGH · Status: OPEN · Owner: CTO with HR Director**

**What was found.** `NFR-045` sets 24×7 availability at ≥ 99.7%. `OP-013` §4.3 states the rota
arithmetic: a sustainable 24×7 primary rota on weekly shifts needs **six** platform engineers
(one-in-six) and **four** security responders; at four it is one-in-four, at which point people
leave, and at three it becomes two people and a fiction.

The programme has **no identified rota members**. `M66` §11 Q-02 records the same unanswered
question for IT staffing generally: *"How many IT staff are there, and what is the intended tier
structure? A tiered model with escalation paths requires enough people to have tiers."*

Three dependent gaps follow: no on-call allowance or time-in-lieu terms agreed with HR
(`OP-013` OI-03); `RT-05`'s late-start protection unenforceable; and `OP-001` §4.7's T1 service desk
(2 FTE at W1 rising to 6–8) equally unfunded.

**Action.** Staff the rota and agree its terms before W1 go-live, or restate `NFR-045` as a
business-hours target. **An unstaffed rota does not degrade gracefully — it degrades into two
people, and then into one.**

---

### OP-10 — Thirty-eight access profiles do not exist, and the register they would check against is ambiguous

**Severity: HIGH · Status: OPEN · Owner: Security Lead with CFO and Enterprise Architecture**

**What was found.** Two compounding gaps:

**(a) No standard access profiles.** `05-04` carries 38 roles. `OP-015` §4.2 makes the standard
profile the mechanism that keeps 38 roles administrable, attached to the role in `MD-009`. **No
profile has been authored for any role.** Until they exist, every W1 grant is bespoke and justified
by precedent — which is the exact failure mode `OP-015` §1 exists to prevent.

**(b) The segregation-of-duties register is not in a state that can be enforced.** `NFR-064` requires
SoD enforcement by the permission engine. `SP-006` §3 records that `05-04` §6 registers
`SOD-01`…`SOD-12` while module files use `SOD-01`…`SOD-30`, and that **nine numbers carry two
different meanings**, with the second meanings reallocated to `SOD-31`…`SOD-39`. Grant-time
enforcement cannot be built against an identifier space in that condition, and `M60` will test a
control whose number means two things.

**Action.** Author the 38 profiles before W1 provisioning; ratify `SP-006`'s reallocation before
`NFR-064` enforcement is built. Recorded as `OP-015` OI-01 and OI-05.

---

### OP-11 — `06-06_Deployment_and_Operations_Plan.md` does not exist

**Severity: MEDIUM · Status: OPEN · Owner: CTO**

**What was found.** The register traces `OP-002` to `06-06_Deployment_and_Operations_Plan.md`.
Enumeration of `1000fix_ERP_Module/06_Delivery_and_Implementation/` returns **two files**: `06-01`
and `06-02`. `06-06` does not exist, and neither do `06-03`, `06-04` or `06-05`.

This is the **third** category to be authored against a missing `06-` document: `AUDIT-011` recorded
the same for `06-03_Data_Migration_Strategy.md` (Category 12) and `06-05_Change_Management_and_Training_Plan.md`
is cited by Category 16.

**Consequence.** Operational decisions that a deployment and operations plan would own — environment
strategy, release calendar, capacity planning, operational acceptance criteria — are made inside
content or not at all. `OP-002` marks each such assumption **[assumes 06-06]** rather than absorbing
it silently.

**Action.** Either write `06-06`, or record formally that Category 17 is the operational plan of
record and amend the register's trace. Recorded as `OP-002` OI-02.

---

### OP-12 — Ninety-four open decisions, and the log they must be recorded in does not exist

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead**

**What was found.** The sixteen files carry **94 explicit open decisions** (`OP-nnn-OI-nn`),
distributed 5–8 per file. Every Definition of Done in the category ends with the same unticked item:
*"Decision(s) taken while authoring logged in `RF-006`"*.

**`RF-006_Content_Decision_Log_and_Change_Control.md` does not exist.** Category 99 `RF` is
unstarted — 0 of 12 files, enumerated 2026-08-20. It is the only content ID cited by this category
that resolves in the register and not on disk (`Z1`).

**Consequence.** Ninety-four decisions with named owners and deadlines have nowhere to be tracked,
and the Definition of Done cannot be completed for any file in the category for a reason unrelated to
the file. The same is true for Categories 14–16 and 18.

**Action.** Write `RF-006` ahead of the rest of Category 99 — it is now blocking the completion of
five categories, not one.

---

### OP-13 — `CG-010`'s per-file bilingual model cannot express a file whose outputs are bilingual

**Severity: MEDIUM · Status: OPEN · Owner: Localisation Lead with Content Design**

**What was found.** `CG-010` §3.2 allocates four bilingual files to Category 17 — `OP-003`, `OP-004`,
`OP-005`, `OP-014` — and the category matches that exactly (`Z8` ✅).

But `OP-006` (English-only) produces **eight audience extracts**, four of which reach branch staff,
field technicians, customers and Bengali-reading sellers. `CG-010` §3.3's audience rule makes those
four bilingual. The file is English; four of its outputs are not, and `CG-010`'s per-file boolean
cannot represent that.

`OP-006` §4.5 declares the departure explicitly rather than resolving it silently, and records it as
OI-01.

**Action.** Amend `CG-010` to allow a file-level flag plus an output-level allocation, or split the
release-note extracts into their own register entries. The same pattern will recur wherever a
governance file generates user-facing artefacts.

---

### OP-14 — The status page depends on the estate it exists to report on

**Severity: MEDIUM · Status: OPEN · Owner: Platform Engineering**

**What was found.** `OP-005` `SP-10` requires the status page to be hosted independently of the ERP
estate. `02-05` §8 provisions no such hosting. `OP-004` §4 identifies the consequence: in a `Sev1`
affecting the estate, the status page — the single source of truth for external communication
(`IC-07`) — may be unavailable at exactly the moment every other channel points at it.

The same dependency affects the login-screen notice, which `OP-009` §6 relies on to reach users
locked out by an identity incident.

**Action.** Provision independent hosting before W2, or accept a documented fallback to SMS plus the
public website banner as the primary external channel. Recorded as `OP-005` OI-02 and `OP-004` OI-05.

---

### OP-15 — Leaver revocation has two deadlines, twenty-three hours apart

**Severity: MEDIUM · Status: OPEN · Owner: CTO with Internal Audit**

**What was found.** `SP-031` §1 requires leaver access to be revoked **within one hour**
(`BRU-SEC-06`). `KPI-090` measures orphaned accounts **beyond 24 hours**, target zero.

Both are current, both are cited, and they differ by a factor of twenty-four. An organisation
operating to the KPI would breach the rule daily without the KPI ever reporting it.

`OP-015` §4.6 operates to the one-hour rule and treats anything beyond it as a control failure, and
records the conflict as OI-04 rather than averaging the two.

**Action.** Align: either `KPI-090`'s tolerance becomes one hour, or `BRU-SEC-06` becomes 24 hours
and the difference is a deliberate risk acceptance. Do not leave both.

---

### OP-16 — Gate G3 is unachievable for the whole category, and no file can leave `Draft`

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead**

**What was found.** All 16 files are `status: Draft`. Thirteen are Class C and three Class D; both
classes make **G3 Technical mandatory** — *"does it match what the system actually does, at the
pinned release?"* (`CG-007` §2.1).

**No system exists to match.** The environment is delivered from W1 to W8. Every command, threshold,
dashboard name and procedure in `OP-007`…`OP-012` is unverifiable at authoring time, and each of
those files states so in its header rather than implying verification it has not had.

Six files additionally carry a **"Last tested" column reading *Not yet*** in their backup and
recovery tables — deliberately, because `NFR-052` requires a weekly restore test that cannot run
against an environment that does not exist.

**Consequence.** Category 17 cannot reach `Approved` for the same structural reason as Categories 05,
10 and 13: the gate is real, the blocker is upstream, and the honest position is a `Draft` that says
why. This is the fifth category in that position.

**Action.** Establish a **G3-on-build** convention: every runbook carries an execution date per
procedure, set the first time the procedure is actually run, and G3 is granted per procedure rather
than per file. Without it, the six runbooks will still be at `Draft` at go-live.

---

### OP-17 — Four bilingual files have no Bengali, and for one of them the Bengali is the operational version

**Severity: MEDIUM · Status: OPEN · Owner: Localisation Lead**

**What was found.** `OP-003`, `OP-004`, `OP-005` and `OP-014` declare `bilingual: yes` and name their
`_BN.md` counterparts. **None of the four counterpart files exists.** Bengali strings are authored
inline — 68 macros in `OP-003`, 26 templates in `OP-004`, 19 in `OP-005`, and the counter
instructions in `OP-014` — but none has passed **G4 in-context review** (`BN-018`), which `CG-007`
makes mandatory for bilingual content.

**For `OP-014` this is a `P0` blocker, not a translation task.** The file is written to be printed in
Bengali and held at the counter in 51+ branches. Its English version is the governance copy; the
Bengali version is the one a cashier reads during a payment outage. A `P0` file that its audience
cannot read is not complete in any useful sense.

**Action.** Author and G4-review the four counterparts, `OP-014` first, before W1. Recorded as
`OP-003` OI-01, `OP-004` OI-01, `OP-005` OI-01 and `OP-014` OI-05.

---

### OP-18 — The breach-notification clock the content plans around is not law yet

**Severity: MEDIUM · Status: OPEN · Owner: Legal Counsel with the DPO**

**What was found.** `NFR-094` requires notification of the National Data Management Authority for any
breach likely to cause significant damage, **"within the prescribed timeframe"**. Research on
2026-08-20 confirms the Personal Data Protection Act 2026 leaves that period **to regulations that
are not yet published**, with the wider enforcement framework activating later.

`OP-004` `RN-03` therefore states a **72-hour planning assumption**, marks it explicitly as a
planning figure and not a legal statement, and requires it to be *replaced* rather than inherited.
The supporting sources are Class **P3** (`CG-012` §3), which may not be the sole basis of a statutory
claim — hence the marking.

**Action.** Legal to confirm the position and set the figure in `LG-024`; `OP-004` follows. Until
then, no document may state a notification deadline as fact.

---

### OP-19 — `NFR-090`, `NFR-091` and `NFR-092` each mean two different things in `05-06`

**Severity: MEDIUM · Status: OPEN (upstream) · Owner: Enterprise Architecture**
**Confirms `AUDIT-016` AP-02, surfaced independently and on the same day.** AP-02 rates it
**Critical** on the strength of its wider citation base; that rating stands and this entry does not
compete with it. It is retained because the remediation differs: Category 17 had to *apply* AP-02's
disambiguation convention to four of its own files, and `OP-007`'s entire justification rests on one
of the three colliding numbers.

**What was found.** Extraction `Z3` surfaced a collision in the source specification, not in the
content:

| Identifier | Meaning in `05-06` §7 (Maintainability) | Meaning in `05-06` §6 (Privacy, PDPA) |
|---|---|---|
| `NFR-090` | Unit test coverage ≥ 80%; 100% on financial calculations | Process personal data only on consent or a stated legitimate ground |
| `NFR-091` | **Every module ships with an operational runbook** | Consent must be clear, explicit, specific and freely given |
| `NFR-092` | Distributed tracing with a single correlation id | Issue a transparency notice before or during processing |

`OP-007` cites `NFR-091` in its `purpose:` for the runbook obligation; a reader checking `05-06` will
find the consent standard first, because §6 precedes §7.

**Consequence.** Three `P0` requirements are ambiguous by identifier across the whole programme. This
is the same identifier-collision failure mode as `00-07` H2-04/H2-05 and `SP-006`'s `SOD-` space, and
`SP-006` already established the rule (`RG-01` extended: register-first for every programme-wide
identifier space).

**Remediation applied here.** Every Category 17 citation of the three numbers now names its
section — `05-06` §7 `NFR-091` for the runbook obligation and `NFR-092` for tracing, `05-06` §6.3
`NFR-090` for purpose limitation — in `OP-001`, `OP-007`, `OP-008` and `OP-010`, following the
convention `AUDIT-016` AP-02 §5 established.

**Action.** Renumber one of the two sets in `05-06` and sweep the citations repository-wide. Owner:
Enterprise Architecture, per `AUDIT-016` R-02.

---

### OP-20 — There is no delegated authority for emergency spend during an incident

**Severity: MEDIUM · Status: OPEN · Owner: CFO**

**What was found.** `SP-004` sets approval authority for procurement, master data, access and change.
It contains no delegation for **operational emergency spend** — expedited vendor support, emergency
capacity, an alternate provider at 02:00.

`OP-013` §4.8 proposes limits (on-call up to BDT 25,000; platform lead up to BDT 100,000; CTO above)
and marks them clearly as a proposal (`AU-01`). Until they are set, the CTO is the only spend
authority in an incident, which is a single point of delay in exactly the scenario where delay is
expensive.

**Action.** CFO to add an incident-spend delegation to `SP-004`, or ratify `OP-013`'s proposal.

---

### OP-21 — `OP-015` cited the wrong document as the segregation-of-duties register, corrected

**Severity: MEDIUM · Status: FIXED · Owner: Programme Content Lead**

**What was found.** `OP-015` §4.7 originally described its incompatible-duty table as *"illustrative —
the register is `05-04`"*. `05-04` §6 carries **twelve** SoD controls; the register that harmonises the
identifier space is **`SP-006`**, which reconciles `SOD-01`…`SOD-30` in module files against those
twelve and reallocates nine collided meanings to `SOD-31`…`SOD-39`.

**Remediation applied.** `OP-015` §4.7 now names `SP-006` as the register, `SP-006` is added to
`traces_to:` and to the Dependencies table, a `P1` source is recorded, and OI-05 is rewritten to state
the identifier-space condition rather than a vague completeness doubt. **The finding was found by
resolving citations, not by reading the file** — `Z4` is what surfaced it.

---

### OP-22 — The category was authored with zero navigable links, repeating `RP-13`

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Extraction `Z9` compared relative-link density across every completed category:

| Category | Files | Relative links |
|---|---:|---:|
| 09 `HC` | 20 | 173 |
| 10 `LG` | 24 | 380 |
| 12 `DM` | 14 | 128 |
| 13 `TS` | 18 | 13 |
| 14 `RP` | 16 | 89 *(after `RP-13` remediation)* |
| **15 `AP`** | 12 | **0** |
| 16 `CM` | 18 | 156 |
| 18 `EO` | 14 | 224 |
| **17 `OP` at first write** | 16 | **0** |

Check `D1` passed **vacuously** — zero links, zero broken — exactly as `AUDIT-015` `RP-13` recorded
for Category 14.

**Remediation applied.** **356 relative links** added: the first occurrence of every distinct content
identifier in each file now links to the file it names. **All 356 resolve** (`D1` re-run).

**A second observation, which is the more useful one.** `RP-13` was issued and **Category 15 `AP` was
completed afterwards with zero links** — the finding did not propagate to the work in flight. A
finding that does not change the next author's behaviour has not been actioned, only recorded. This
is now a recommendation (§6 R-04), not a Category 17 finding.

---

### OP-23 — Section references to `OP-013` drifted across seven files during authoring, corrected

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Seven files cited `OP-013` §3 (severity), §4 (declaration), §5 (incident roles)
and §7 (out-of-band communications) — a section structure that would have been correct for a runbook
but not for a `TPL_Content_File_Front_Matter` file, whose six top-level sections are fixed. When
`OP-013` was authored to its template, those references pointed into `## 5. Dependencies` and
`## 6. Maintenance`.

**Remediation applied.** All references corrected to `§4.1`, `§4.5`, `§4.6` and `§4.10` across
`OP-001`, `OP-002`, `OP-004`, `OP-005`, `OP-007`, `OP-008` and `OP-012`. **This is a hazard specific
to the generic template**: any file needing more than six addressable sections must express them as
`§4.n`, and cross-references written before the target is authored will point at the wrong place.

---

### OP-24 — `OP-016` had a section-numbering gap, corrected

**Severity: LOW · Status: FIXED · Owner: Programme Content Lead**

**What was found.** `OP-016` ran `§4.1`…`§4.13` with **no `§4.8`**. No other file cited an `OP-016`
subsection, so nothing was broken; the numbering was simply wrong.

**Remediation applied.** Renumbered to `§4.1`…`§4.12`, contiguous. Verified by heading extraction.

---

### OP-25 — Owner strings in front matter differ lexically from the register

**Severity: LOW · Status: OPEN · Owner: Programme Content Lead**

**What was found.** All 16 owners are semantically identical to the register; **nine differ
lexically**, because the register uses a compact form and the front matter a prose form:

| Register | Front matter |
|---|---|
| `Support + Programme` | `Support Lead with Programme Office` |
| `Support + Comms` | `Support Lead with Communications` |
| `Platform + Risk` | `Platform Engineering with Risk` |
| `Operations + Platform` | `Operations with Platform Engineering` |
| `Programme + Content Design` | `Programme Office with Content Design` |
| … four more of the same shape | |

**Consequence.** An automated `F7` owner check that compares strings will report nine mismatches
where there are none. The check currently in `AUDIT_Checklist_Recurring.md` is manual, so this has
not yet produced a false finding — but it will the first time it is automated.

**Action.** Either normalise the front matter to the register's compact form, or record in the
checklist that `F7` owner comparison is semantic. Recommended: the latter, since the prose form is
more useful to a reader.

---

### OP-26 — The register's "eleven external audiences" is not enumerated anywhere upstream

**Severity: LOW · Status: OPEN · Owner: Programme Office**

**What was found.** The register's `OP-001` row justifies the file by *"800+ internal users and
eleven external audiences"*. The 800+ figure resolves to `NFR-003`. **The eleven is enumerated in no
upstream document** — not `04-00`, not `05-04`, not `00-02`.

`OP-001` §4.1 therefore enumerates eleven populations, derived from the six external-facing portals
plus the two non-portal counterparty groups that raise system-affecting contacts, and **declares the
derivation** under `CG-012` §2 rather than presenting it as a register fact. `HC-015` will publish
contact routes against whatever set is confirmed.

**Action.** Confirm or correct the enumeration. If the intended eleven differs, `OP-001` §4.1 and
`HC-015` both change.

---

## 4. What this category cannot evidence

Four things `OP` asserts cannot be evidenced today, for reasons outside content. They are listed
separately from the findings because no content action closes them.

| Assertion | Why it cannot be evidenced | Owner |
|---|---|---|
| `NFR-007` RPO 15 min / RTO 2 h | No DR environment, no separate-domain WAL archiving, no exercise (OP-01, OP-02) | CTO |
| `NFR-045` 24×7 availability ≥ 99.7% | No staffed rota, no paging platform (OP-06, OP-09) | CTO + HR |
| `NFR-050` every P0 integration has a **tested** fallback | The procedures exist; the printed forms, reserved Mushak ranges and drills do not (`OP-014` OI-01, OI-02) | Operations + Tax |
| `KPI-090` zero orphaned accounts beyond 24 h | No JML automation before `M66` at W6; no access profiles; no recertification tooling (OP-10) | Security |

**One inbound finding lands directly on this category.** `AUDIT-016` AP-01 records that **14 domain
event names are consumed by specifications and do not exist in the `05-03` §4.2 inventory**.
`OP-008` operates the event platform those names travel on: its §5 failure modes, §4 replay
procedure and §10 schema-change rules all assume an inventory that is authoritative. **Until AP-01
is closed, `OP-008`'s consumer-migration evidence (`CR-03`) cannot be complete**, because the set of
consumers is not fully enumerable. No Category 17 action closes it.

**Two statutory dependencies are also unresolved and are recorded here so they are not read as
content gaps:** the PDPA 2026 notification period (OP-18) and whether the Company is or will be
declared Critical Information Infrastructure under the Cyber Security Ordinance 2025, which would
convert `OP-004` template 24 from optional to a standing obligation with its own SOC reporting
cadence (`OP-004` OI-03).

---

## 5. Remediation applied during this audit

| # | Change | Files affected | Verification |
|---|---|---|---|
| 1 | `SP-006` established as the SoD register; `traces_to:`, Dependencies, a `P1` source and OI-05 rewritten (OP-21) | `OP-015` | Citation resolves; `SP-006` §3 quoted accurately |
| 2 | **356 relative links added**, first occurrence of every distinct content ID per file (OP-22) | All 16 | `D1` re-run: **356 links, 0 broken** |
| 3 | `OP-013` section references corrected to `§4.1`/`§4.5`/`§4.6`/`§4.10` (OP-23) | 7 files | Grep confirms no `OP-013 §3/§4)/§5/§7` remains |
| 4 | `OP-016` renumbered `§4.1`…`§4.12`, contiguous (OP-24) | `OP-016` | Heading extraction |
| 5 | `OP-007` OI-05 restated precisely: five component runbooks, zero module runbooks, two readings of `NFR-091` (OP-07) | `OP-007` | — |
| 6 | `AUDIT-016` AP-02's section-naming convention applied to all citations of `NFR-090`/`-091`/`-092` (OP-19) | `OP-001`, `OP-007`, `OP-008`, `OP-010` | Grep: no bare citation of the three numbers remains |

---

## 6. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | Provision the `dr` environment, the out-of-account immutable backup and separate-domain WAL archiving, and schedule the first `NFR-051` exercise | CTO | Before W2 |
| **R-02** | Resolve the residency DR question (OP-01) with Legal in advance, in writing | CTO + Legal | Before W2 |
| **R-03** | Move `OP-005`, `OP-016` and `OP-008` to W1 in the register, and `OP-010` to W2 | Programme Office | Immediately |
| **R-04** | **Make findings propagate to work in flight.** `RP-13` was issued and the next category was still authored with zero links. Add a pre-authoring check to `CG-008`: before starting a category, read the last two audits' `FIXED` findings | Programme Content Lead | Immediately |
| **R-05** | Write `RF-006` ahead of the rest of Category 99 — it now blocks Definition of Done in five categories and 94 decisions in this one | Programme Content Lead | Immediately |
| **R-06** | Establish the G3-on-build convention (OP-16) so runbooks can be approved procedure by procedure as the platform is delivered | CTO + Content Lead | W1 |
| **R-07** | Establish break-glass — vault path, sealed envelope, signatories, quarterly test — as the cheapest high-severity remediation available | Security Lead | Before W1 go-live |
| **R-08** | Correct `05-03` (P0 count and the `INT-013` fallback) and `05-06` (`NFR-090`/`091`/`092` collision) | Enterprise Architecture | W1 |
| **R-09** | Author the four Bengali counterparts, `OP-014` first | Localisation Lead | Before W1 |
| **R-10** | Fund the fallback pack (13 items × 51+ sites, serial-controlled) and obtain the reserved Mushak ranges — without them `IP-09` compliance is documentary only | Operations + Tax | Before W1 |

---

## 7. Closure

**Category 17 `OP` is complete as specified: 16 of 16 files, 500 KB, 70,706 words, all at
`Draft`.** *(Re-enumerated after this audit's own remediation added 356 links; the figure lags the
work, per the rule `AUDIT-014` TS-11 established.)* Every register dimension reconciles, every citation resolves, every template conforms,
and the four bilingual files are exactly the four `CG-010` names.

**None of the sixteen can reach `Approved`**, for two reasons that are both upstream: G3 requires a
system that does not exist yet (OP-16), and the four bilingual files require a Bengali counterpart
that has not been authored (OP-17).

The category's own conclusion, stated in its files rather than inferred here, is that **the 1000FiX
programme currently has operational content and no operational capability**: a DR playbook with no
DR environment, a rota with no engineers, a break-glass procedure with no vault, a fallback set with
no printed forms, and a support model whose platform arrives twenty months after the model is needed.

That is not a criticism of the content. It is what the content was written to make visible, and it is
the first time the programme's operational readiness has been enumerated rather than assumed.

**With Category 17 complete, 428 of 452 registered content files are written. Categories 19 `MM`
(12) and 99 `RF` (12) remain.**

---

*`AUDIT-017` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
