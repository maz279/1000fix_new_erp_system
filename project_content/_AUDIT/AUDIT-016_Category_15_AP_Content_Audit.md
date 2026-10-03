---
id: FIX-ERP2-AUDIT-016
title: Category 15 AP — Integration & Developer Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 12 Category 15 AP files, the event and endpoint identifier spaces they reconcile, their citations into the module repository and the content register, cross-register integrity, gate F7, the audit-trail integrity of the _AUDIT folder, and the concurrent-authoring condition observed during the audit window
mandate: Audit required on completion of Category 15 authoring (rule CM-R9)
extends: AUDIT-001 … AUDIT-015
enumeration_date: 2026-08-17 16:49 UTC
method: Filesystem enumeration and identifier extraction only (RG-06, CP-11). No figure in this report is projected, and none is taken from what a document says about itself — including this category's own files. Every count carries the UTC instant it was taken, because the repository was under concurrent modification throughout the audit window (finding AP-17).
---

# Category 15 `AP` — Integration & Developer Content Audit
### 12 files · **428 of 452** registered content files written *(enumerated 2026-08-17 16:49 UTC)*

---

## 1. Method and result

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F7 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration and extraction.
**Enumeration instant 2026-08-17 16:49 UTC**, stated to the minute rather than the day because
four other categories were being written during the same window.

Seven category-specific extractions were run:

| Extraction | What was compared |
|---|---|
| **Y1** | Every content identifier cited, against the 452 register rows |
| **Y2** | **Every event name used in `05-03` §3.3, `P04` §12.3 and `P08` §12.3, against the `05-03` §4.2 inventory** — the extraction that produced finding AP-01 |
| **Y3** | Every `NFR-`, `AS-`, `DI-`, `EA-`, `SOD-`, `OPS-`, `API-`, `IP-`, `INT-` identifier against its declared range, **and each `NFR-` against its meaning in both `05-06` §6.3 and §7** |
| **Y4** | Every `FR-IPF-`, `FR-SEC-`, `FR-POR-` identifier against its module's §5 table |
| **Y5** | Every `BRU-` and `BR-STD-` identifier against `05-05` and the owning module |
| **Y6** | Every gate criterion `Gn-nn` against `06-02` §4 |
| **Y7** | Register filenames against disk, byte for byte; front-matter key sets against `TS-001`'s established 24 |

**Eighteen findings — 2 critical, 6 high, 7 medium, 3 low.** Three were remediated during the
audit; fifteen are open, and **twelve of those are owned outside the content function.**

| Severity | Count | Fixed | Open |
|---|---:|---:|---:|
| Critical | 2 | 0 | 2 |
| High | 6 | 0 | 6 |
| Medium | **7** | **3** | 4 |
| Low | 3 | 0 | 3 |

> **Three findings in this report are against the auditor's own work** (AP-10, AP-11, AP-18), and
> all three were fixed during the audit. **AP-18 is against this report itself** — its gate F7 wave
> row was written from memory rather than derived, and two cancelling errors produced a false pass.
> The convention inherited from `00-07` requires them to be stated anyway: the cause matters more
> than the fix.

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | **12 of 12** ✅ |
| **A2** Total written | **428 of 452**, enumerated 2026-08-17 16:49 UTC ✅ *(a moving figure — see AP-17)* |
| **A5** Files on disk with no register entry | Zero ✅ |
| **B1** ID uniqueness | 12 unique ✅ |
| **B2** Contiguity `AP-001`…`AP-012` | No gaps ✅ |
| **B4** File name matches ID | **12 of 12**, byte-identical to the Master Index §4 register ✅ |
| **B5** Bengali counterparts | **0 required, 0 present** — `CG-010` §3.2 allocates `AP` as 0 bilingual / 12 English-only ✅ |
| **C1/C2** `purpose:` and `traces_to:` present | 12 of 12 ✅ |
| **D2** Files in their declared subfolder | **12 flat**, matching Master Index §3.2 — Category 15 declares no subfolders ✅ |
| **D3** No spaces or ampersands in any path | Zero ✅ |
| **E7** Template conformance | **All six `TPL_Content_File_Front_Matter.md` sections present, in order, in all 12**, plus the `Open Items` and `Definition of Done` blocks the category convention adds ✅ |
| **F1** Front matter complete | **All 24 keys present in all 12**, and the key set is **identical, in order, to `TS-001`'s** — verified by extraction, not by eye ✅ |
| **Y1** Content-ID citations | **102 distinct identifiers cited; 102 registered.** Zero unregistered ✅ |
| **Y3** Range checks | **32 distinct `NFR-` cited, all within `NFR-001`…`NFR-101`**; `AS-01`…`15`, `DI-01`…`08`, `EA-01`…`12`, `SOD-01`…`12`, `OPS-01`…`08`, `API-01`…`12`, `IP-01`…`10`, `INT-001`…`047` all in range ✅ — **but see AP-02, which is a defect in the range itself, not in the citations** |
| **Y4** `FR-` citations | **37 `FR-IPF-`** all within `M28`'s 001–057 · **5 `FR-SEC-`** all resolve in `M29` §5 · **17 `FR-POR-`** all within `P08` §5's 229–254 ✅ |
| **Y5** `BRU-` citations | **23 distinct.** `BRU-IPF-04`…`22` → `M28` §9 · `BRU-SEC-02`, `-25` → `M29` §9 · `BRU-SRM-01`…`11` → `05-05` (20 `BRU-SRM` rows present) · `BR-STD-01`, `-04`, `-06` → `05-05` (`BR-STD-01`…`07`) ✅ |
| **Y6** Gate criteria | **15 distinct cited — `G3-01`, `-02`, `-03`, `-06`, `-07`, `-09`; `G4-01`, `-02`, `-05`, `-08`; `G5-02`; `G6-02`; `G7-02`, `-04`; `G8-04` — all 15 resolve in `06-02` §4** ✅ |
| **Y7** Register filenames vs disk | **Byte-identical, both directions**, all 12 rows ✅ |

### 2.1 Cross-register reconciliation — gate F7

**All seven dimensions reconcile exactly.**

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---|---:|:--:|
| File count | Master Index §4 | 12 | 12 | ✅ |
| Priority `P0`/`P1`/`P2`/`P3` | Master Index §1 | 0 / 6 / 6 / 0 | 0 / 6 / 6 / 0 | ✅ |
| Wave per file | Master Index §4 rows | **W3×7, W4×5** | All 12 match | ✅ *(expected value corrected — finding AP-18)* |
| Content class A/B/C/D/E | `CG-002` §4.1 | 0 / 1 / 0 / 9 / 2 | 0 / 1 / 0 / 9 / 2 | ✅ |
| Bilingual / English-only | `CG-010` §3.2 | 0 / 12 | 0 / 12 | ✅ |
| Template allocation | `CG-009` §3, §3.1 | 12 × template 1 Generic | 12 × template 1 | ✅ |
| Subfolder allocation | Master Index §3.2 | 12 flat | 12 flat | ✅ |

**The single Class `B` file is `AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md`** — the
only file in the category whose content is a legal position rather than a technical one, and the
only one whose failure mode is a regulatory penalty rather than a support ticket. It carries
Legal Counsel as approver and an unsigned Approval Record block, per `CM-R7` and `CG-007`.

**The two Class `E` files are `AP-001` and `AP-002`** — the developer-portal information
architecture and the API reference content standard. Both govern *how the category's other ten
files are constructed and published*; neither is read by an external developer to perform a task.
Every other file is Class `D`, because each is read by someone outside the programme's
English-working core to do a job. The allocation is recorded here so it is not later reassigned.

**`CG-009` §3 allocates all twelve to template 1 with two required additions** — an
endpoint/event reference table and an error catalogue table. **Both additions are present in all
twelve**, verified by extraction. Where a file has no natural error surface, the addition is
satisfied by the nearest true equivalent and the substitution is declared in the file's own
template-conformance note rather than silently omitted.

---

## 3. Findings

### AP-01 — Twenty-one event names are consumed by specifications and do not exist in the inventory

**Severity: CRITICAL · Status: OPEN · Owner: Enterprise Architecture with CTO**

**What was found.** Extraction Y2 compared every event name used in `05-03` §3.3 (the CON-03
portal webhook contract), `P04` §12.3 and `P08` §12.3 against the `05-03` §4.2 event inventory.

**Twenty-one distinct event names are consumed and are not registered.** They fall into three
classes:

| Class | Count | Examples | Remedy |
|---|---:|---|---|
| **Same fact, two names** | 5 | `estimate.issued` vs `service_order.estimated` · `sla.at_risk` vs `sla.warning` · `invoice.issued` vs `invoice.created` · `contract.renewal_due` vs `contract.expiring` · `claim.submitted` vs `warranty_claim.submitted` | Correct the specification to the inventory name. Free |
| **Coarse projection of finer events** | 2 | `service_order.status_changed` · `consignment.status_changed` | Decide whether the portal contract receives a projection or the fine-grained set. A projection is a legitimate design; an undocumented one is not |
| **Genuinely missing registration** | **14** | `credit_note.issued` · `claim.evidence_incomplete` · `recall.execution_updated` · `asset.estate_reconciled` · `loyalty.points_changed` · `entitlement.threshold_crossed` · `technician.location_updated` · `catalogue.updated` · `stock.consignment_consumed` · `stock.consignment_reconciled` · `stock.rtv_raised` · `asset.alert_raised` · `project.milestone_reached` · `credit_note.issued` | Register, or the consuming specification is describing behaviour the platform will not provide |

**Why it is Critical.** `AUDIT_Checklist_Recurring.md` defines Critical as *"a required artefact
assumed present when absent"*. Three of the fourteen are not documentation conveniences:

| Event | What depends on it |
|---|---|
| `claim.evidence_incomplete` | **A control.** `P08` `T-05` uses it to *suppress claim submission* when the evidence pack is incomplete against the brand's rules. `G4-02`'s 90% first-submission approval target rests on that suppression |
| `recall.execution_updated` | **Product safety.** `P08` `FR-POR-254` publishes recall execution status to the brand |
| `credit_note.issued` | **The SLA remedy.** `P04` `AC-10` requires service credits to be published to the client *without prompting*; a credit note is how a credit reaches them, and `05-04` §7 gives credit notes their own approval matrix |

`05-03` §4.2 is headed *"Event Inventory (Principal Events)"*. **"Principal" is doing a great deal
of work in that heading.** If the inventory is deliberately partial, then `FR-IPF-032`'s living
catalogue — generated from the registry rather than maintained by hand — will be the first
document that reveals the true event count, at which point every consumer specification written
against the inventory is incomplete. If it is meant to be complete, fourteen registrations are
missing.

**How it happened.** The same mechanism as `AUDIT-005` `NT-01`, `AUDIT-003` `MD-01` and
`AUDIT-002`: **a summary table written before the specifications that consume it, and never
reconciled against them.** `05-03` §4.2 was authored as a cross-cutting inventory; `P04` §12.3 and
`P08` §12.3 were authored later, per portal, by whoever knew that portal. Neither author was
wrong; nobody ran the join. Prose review would not have caught it — extraction caught all
twenty-one.

**Remediation instruction.** Enterprise Architecture to (a) rule on whether `05-03` §4.2 is
complete or principal, and say so in the heading; (b) correct the five naming divergences in the
consuming specifications, not in the inventory; (c) decide the projection question for the two
coarse events; (d) register the fourteen, or amend the specifications that consume them. Recorded
as `AP-003` `O-06`, `AP-007` `O-04` and `AP-008` `O-03`.

---

### AP-02 — `05-06` uses `NFR-090`, `NFR-091` and `NFR-092` for two different requirements each

**Severity: CRITICAL · Status: OPEN · Owner: Enterprise Architecture**

**What was found.** Extraction Y3 resolved each cited `NFR-` identifier against **both** places it
appears in `05-06`:

| ID | `05-06` §6.3 — PDPA 2026 | `05-06` §7 — Maintainability & Operability |
|---|---|---|
| **NFR-090** | Process personal data only on consent or a stated legitimate ground, recorded per processing purpose | Unit test coverage ≥ 80% on custom code; 100% on financial calculations |
| **NFR-091** | Consent must be clear, explicit, specific and freely given, with a heightened standard for sensitive personal data | Every module ships with an operational runbook |
| **NFR-092** | Issue a **transparency notice** before or during processing, stating categories, purposes, risks, retention, third-party transfers and withdrawal | **Distributed tracing** across all services with a single correlation id |

Additionally, **`NFR-088` and `NFR-089` appear twice** — once in §6.2 and again as two stray rows
appended to §6.4's *"Fields currently classified as residency-restricted"* table, where they do
not belong structurally at all.

**Category 15 is the first content set to cite both senses within one category, and both citations
are correct against their source.** `AP-002`, `AP-003`, `AP-004` and `AP-006` cite `NFR-092` as
distributed tracing — following `M28` §2, which cites it that way. `AP-012` cites `NFR-092` as the
PDPA transparency notice — following `05-06` §6.3 directly. Neither is a citation error; the
identifier is genuinely ambiguous.

**Why it is Critical.** *"Work done against the wrong artefact"* is the definition, and this is
the cleanest possible instance: an engineer assigned "satisfy `NFR-092`" can correctly implement
either OpenTelemetry tracing or a data-protection transparency notice. One is a `P1` observability
requirement; the other is a **`P0` statutory obligation under a statute whose enforcement
mechanisms activate around 13 May 2027, inside Wave 4**, carrying a penalty exposure of up to
BDT 25 lakh. A traceability matrix (`RF-003`) keyed on `NFR-092` will show the obligation as
covered when the wrong one has been built.

**How it happened.** `05-06` §6.3 states plainly that *"these requirements are new — the previous
specification contained none of them"*, and §6.4 records the same for the residency block. **Ten
PDPA requirements were inserted into a numbering space that already ran to `NFR-092` in §7**, and
the insertion continued the §6 sequence rather than extending the document's high-water mark. The
duplicate `NFR-088`/`NFR-089` rows in §6.4 are the visible residue of the same edit.

This is the fourth identifier-collision finding in the programme's audit history — after `00-07`
H2-04 (22 KPI identifiers meaning two things), H2-05, and the portal audit's X-01. **It is the
first where the two meanings sit inside one document.**

**Remediation instruction.** Enterprise Architecture to renumber the three PDPA requirements to
the next free range (`NFR-102`…`NFR-104` on current evidence), correct every citation across the
module repository and the content set, and delete the two stray `NFR-088`/`NFR-089` rows from
§6.4. **`05-06` §7's `NFR-090`…`NFR-092` are older and more widely cited — including by `M28`
itself — so the PDPA block is the one that moves.** Until renumbered, every citation of
`NFR-090`, `NFR-091` or `NFR-092` must name its section: `05-06` §6.3 `NFR-092` or `05-06` §7
`NFR-092`.

---

### AP-03 — All twelve files are registered at a wave after the wave that first consumes them

**Severity: HIGH · Status: OPEN · Owner: Programme Content Lead with Platform Engineering Lead**

**What was found.** Extraction of each file's registered wave against the first wave in which a
specification, gate criterion or integration consumes it:

| File | Registered | First consumed | Driver |
|---|:--:|:--:|---|
| `AP-001` Developer portal IA | W4 | **W3** | `05-03` §8 lands INT-024…026 (three couriers, external dev teams) in W3 |
| `AP-002` API reference standard | W3 | **W1** | `FR-IPF-012` and `FR-IPF-018` are `P0`/W1; `AS-07` applies from the first published endpoint |
| `AP-003` Event catalogue | W3 | **W1** | `AS-08` and `DM-15` apply from the first write path |
| `AP-004` Webhooks | W3 | **W1** | `05-03` §3.3 gives the CON-03 portal eleven webhooks, live from W1 |
| `AP-005` Auth, scopes, limits | W3 | **W1** | `M28` and `M29` are both `P0`/W1; the gateway validates tokens from the first request |
| `AP-006` Error catalogue | W3 | **W1** | `FR-IPF-006` enforces the envelope from W1 |
| `AP-007` Brand guide | W4 | W4 | Aligned — but blocked on `AP-005` and `AP-004` |
| `AP-008` Corporate guide | W4 | W4 | Aligned — but see AP-07 |
| `AP-009` Payment runbook | W3 | W3 | Aligned |
| `AP-010` Sandbox | W4 | **W3** | Prerequisite for the W3 courier integrations and for `AP-007`/`AP-008` onboarding |
| `AP-011` Deprecation notices | W4 | **W3** | `API-02`'s two-version obligation applies from the second version of anything |
| `AP-012` Disclosure register | W3 | W3 | Aligned — but three W3 counterparties are `Undetermined`; see AP-08 |

**Eight of twelve are late against their own consumers, and six of those eight are needed in
W1** — three waves and roughly fourteen months before the register places them.

**This is the sixth consecutive category with the same defect**, and it is the first in which the
concentration lands on **W1**. `AUDIT-008` found three instances in `KB`, `AUDIT-009` two in `TR`,
`AUDIT-010` two in `HC`, `AUDIT-014` nine in `TS`, and `AUDIT-015` recorded the pattern again in
`RP`. **Twenty-eight instances across six categories is not a series of oversights.**

`AUDIT-010` §7 concluded that the register was sequenced by *when a file's subject matures* rather
than by *when its consumers need it*. Category 15 is the strongest evidence yet, because the
consumers here are not judgement calls — they are `P0` functional requirements with a stated wave.
`FR-IPF-002`, `-003`, `-004`, `-006`, `-012`, `-016`, `-018`, `-021`, `-023`, `-024`, `-025` are
**all `P0`, all W1**, and every one of them consumes content this register places at W3.

**Remediation instruction.** Correct the eight waves, **or** record a documented exception per
file. **Do not correct them one at a time** — `AUDIT-010` R-02 did that for two `HC` files and the
pattern recurred four times since at increasing volume. The sequencing basis needs correcting
once, register-wide, and Categories 19 `MM` and 99 `RF` are the last two unauthored categories in
which to do it before the whole register is written. Recorded as `O-01` or `O-02` in each of the
eight files.

---

### AP-04 — No webhook signature scheme exists anywhere in the repository

**Severity: HIGH · Status: OPEN · Owner: CTO with Security Lead**

**What was found.** `FR-IPF-035` requires every outbound webhook to be signed. `FR-IPF-037`
requires inbound signature verification. `05-03` §5.1 registers the receiver family with
"signature verification". **No document in the module repository states an algorithm, a header
set, a signed-content construction, a replay window, a rotation-overlap behaviour, or a
comparison requirement.**

`AP-004` §4.4 proposes a complete scheme aligned to the Standard Webhooks specification —
HMAC-SHA256 over `webhook-id`, `webhook-timestamp` and the raw body, three headers, a five-minute
tolerance, constant-time comparison, and multi-signature during rotation — and marks it a
proposal throughout, per `CG-012` and `CM-R8`.

**Why it matters now rather than at W4.** The CON-03 portal platform consumes eleven webhooks
from **W1** (`05-03` §3.3). Until the scheme is decided, either the portal accepts unverified
POSTs, or each side implements a different scheme and the integration fails at the first delivery.
A forged `payment.received` to an unverified endpoint is a financial-fraud vector, and the
endpoint URL is discoverable by anyone who has seen one delivery.

**Compounding it:** extraction found **no webhook management endpoint registered anywhere**.
`M28` §12.5 lists eighteen platform endpoints — schemas, catalogue, subscriptions, dead letters,
replay, APIs, consumers, credentials, integrations, health, fallback test, sync, reconciliation,
trace — **and none for webhook endpoint registration, testing or secret rotation**, despite
`FR-IPF-034` requiring a registry and `fix_webhook_endpoint` existing as an entity. `AP-004` `O-03`.

**Remediation instruction.** CTO and Security Lead to ratify a signature scheme before the W1
portal contract is implemented. Adopting the proposal in `AP-004` §4.4 is the cheapest route,
because a partner's existing library will already implement it. Register the three missing
management endpoints. Recorded as `AP-004` `O-01` and `O-03`.

---

### AP-05 — No scope naming convention exists, and every credential is scoped by judgement

**Severity: HIGH · Status: OPEN · Owner: Solution Architect with Security Lead**

**What was found.** `FR-IPF-003` enforces the caller's authorisation scope at the gateway.
`EA-11` binds external API access to the credential's scope and forbids widening by parameter.
`API-10` forbids any endpoint returning data outside the caller's scope. `AP-002` `AR-04` requires
every published operation to declare the scope it needs, by name.

**Not one scope name appears anywhere in the repository.** `05-03` §5.1 names twelve API families
and their auth model; a family is a routing concept, not a permission.

**The operational consequence.** A brand partner signs an agreement covering warranty claims for
their own brand. An engineer issues the credential. Which scope? There is no list, so the engineer
grants what the partner asked for — a judgement made at a keyboard. `EA-11` is then satisfied by a
credential that was too wide when it was issued, and no control downstream can detect it, because
scope enforcement enforces the scope that was granted.

`AP-005` §4.3 proposes `<resource>:<action>[:<qualifier>]` with four actions — deliberately
excluding `delete`, because `DI-08` permits soft deletion only — and eight grant rules including
the separation of `approve` from `write` that `05-04` §6's segregation rules depend on. It is
marked a proposal throughout.

**Why it is High rather than Medium.** `M28` and `M29` are both `P0`/W1 and the gateway validates
tokens from the first request. Every credential issued between W1 and the decision is scoped
without a register, and re-scoping a live partner credential later is a breaking change requiring
notice under `AP-011`.

**Remediation instruction.** Solution Architect and Security Lead to ratify a scope vocabulary
before the first credential is issued, and to record it in `05-03` §5 so that `AP-002` `AR-04` can
be enforced in CI. Recorded as `AP-005` `O-01`, and it blocks `AP-002` `AR-04`, `AP-007` §4.5 and
`AP-008` §4.5.

---

### AP-06 — Three payment availability commitments do not reconcile with each other

**Severity: HIGH · Status: OPEN · Owner: CTO with CFO**

**What was found.** Authoring `AP-009` against the payment rails surfaced three commitments that
cannot all hold:

| # | Commitment | Source | In tension with |
|---|---|---|---|
| 1 | Payment confirmation round trip **≤ 3 s p95** | `NFR-042` | bKash's own published guidance recommends a **30-second** call timeout for its tokenised-checkout API. A rail whose provider expects 30 s cannot be confirmed inside a 3 s p95 budget end to end |
| 2 | Fallback engages **automatically within 2 minutes** of an induced outage | `M28` `AC-13` | `05-03` §7 detects unavailability at *< 99% over 15 minutes* and error rate at *> 2% over 5 minutes*. **A 5-minute detection window cannot produce a 2-minute failover** unless circuit-breaker state, not the monitoring window, drives it — which is a design position stated nowhere |
| 3 | Payment path availability **≥ 99.95% with multi-gateway failover** | `NFR-048` | 99.95% is ~22 minutes of downtime per month. **The card path has a single acquirer (INT-003) and no second acquirer anywhere in `05-03` §2.1**, so for card payments there is no failover to be had |

**Why it is High.** All three are `P0`. Each constrains the others, and a connector built to
satisfy one will fail the others. `G3-03` requires bKash, Nagad and card payments live and
reconciling at the W3 gate, so the reconciliation is needed before the connectors are built, not
after.

**Remediation instruction.** CTO and CFO to resolve the three together: restate `NFR-042` as an
internal-processing budget excluding third-party call time, or accept a longer p95; state
explicitly that circuit-breaker state drives failover; and either procure a second card acquirer
or restate `NFR-048` as applying to the aggregate payment path rather than to every method.
Recorded as `AP-009` `O-01`.

---

### AP-07 — The capability the register calls "a condition of contract" is `P3`, three waves late

**Severity: HIGH · Status: OPEN · Owner: Commercial Director with CTO**

**What was found.** The Master Index register justification for `AP-008` reads: *"Enterprise
clients increasingly require ticket and asset integration as a condition of contract."*

| Capability | Integration | Wave | Priority |
|---|---|:--:|:--:|
| Corporate portal go-live | `P04` | **W4** — Month 18 | — |
| Client ITSM ticket exchange | **`INT-047`** | **W7** — Month 30 | **`P3`** |
| Client SSO federation | **`INT-046`** | **W6** — Month 26 | `P2` |

`05-03` §2 describes `P3` as *"enhancement; opportunistic"*. `06-02` `G4-05` requires **ten or
more corporate clients transacting on the B2B portal at the W4 gate**.

**So the programme expects to sign ten or more corporate clients in Month 18 against a capability
its own register says is a condition of contract, scheduled for Month 30, at the lowest priority
in the catalogue and explicitly marked deferrable.** Either the priority is wrong or the
justification is.

**Why it is High.** `AUDIT_Checklist_Recurring.md` defines High as *"materially misleading, or a
budget or scope exposure"*. This is a commercial exposure before it is a technical one: an account
manager reading the register justification will answer "yes" to a client asking about ServiceNow
integration, twelve months before it exists, at a priority that permits deferral.

**Remediation instruction.** Commercial Director to establish how many contracted or prospective
corporate clients actually make ticket integration a condition — `P04` Q-01 asks the adjacent
question and is also unanswered. If the answer is more than none, `INT-047`'s priority and wave
are wrong. If it is none, the register justification is. **Do not sell against W7 capability at
W4.** Recorded as `AP-008` `O-01`.

---

### AP-08 — The Class `B` register cannot be completed, and three W3 counterparties are undetermined

**Severity: HIGH · Status: OPEN · Owner: Legal Counsel with Security Lead**

**What was found.** `AP-012` is the single Class `B` file in the category and the only one whose
failure mode is a regulatory penalty. Authoring it produced four separate gaps:

| # | Gap | Consequence |
|---|---|---|
| 1 | **9 of 53 counterparties have a `Determined` field-level register; 38 cannot be specified** because their integrations are not yet designed | Structural and expected — but only workable if the promotion gate (`AP-010` `P-02`, `AP-012` `RV-2`) actually holds. An integration reaching production with `Undetermined` rows defeats `IP-10` silently |
| 2 | **The three W3 courier integrations are `Undetermined`** and carry customer **name, phone and address** | Under `AP-012` `DS-01`, no consignment may be booked with Pathao, RedX or Steadfast/Sundarban until their rows are determined and `NFR-098` processor contracts exist. **This blocks W3 pick-and-drop**, in the same wave `G3-07` requires unbroken custody with zero exceptions |
| 3 | **No DPIA exists or is scheduled**, and **no processor-contract inventory exists** | `NFR-098` requires equivalent obligations flowed by contract to every processor and sub-processor. Without a processor list there is no contract list to check. At least four processing activities need assessment — NID verification, speech-to-text, ad delivery, seller KYC |
| 4 | **No DPO or CDO is appointed and the significant-data-fiduciary classification has not been made** (`NFR-096`) | The classification determines whether the penalty ceiling is BDT 25 lakh or BDT 50 lakh, and the role is a named reviewer of this file |

**The highest-risk single row is `INT-034` NID verification**, which transmits a national
identifier. It requires all three of: `LG-2S` specific consent under `NFR-091`; the `NFR-086b`
gate — an Authority notification record and a documented safeguard **before** the transfer
executes; and confirmation that the verification service is Bangladesh-resident under `NFR-086`.
**None of the three exists.** The integration is W7 and identity verification is the control the
marketplace trust model rests on.

**Why it is High and not Critical.** The register is authored, the gaps are enumerated with
owners, and `DS-01`'s default is refusal — so the exposure is realised only if the promotion gate
is bypassed. It becomes Critical the first time an integration ships with `Undetermined` rows.

**Remediation instruction.** Legal Counsel to determine the three courier rows before W3 minus
three months; commission the DPIA; build the processor-contract inventory against `NFR-098`; and
put the significant-data-fiduciary classification to the CEO. Recorded as `AP-012` `O-01`…`O-06`.

---

### AP-09 — `CG-002` §6 and §4.1 disagree on Category 15's approver class

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead**

`CG-002` §6 assigns Category 15 a single **"Approver class: D"**. `CG-002` §4.1 allocates the
category as **1 B · 9 D · 2 E**. Under §4, a Class B file is approved by **Legal Counsel** and a
Class E file by the **Programme Content Lead** — neither of which is §6's Content Design Lead.

Category 15 is not unique in this: `MD`, `NT`, `DT`, `TS`, `RP` and `EO` all carry compound
approver classes in §6, and `§4.1` gives all of them mixed allocations. **§6 is a per-category
summary of a per-file property**, and for six categories it cannot be both correct and singular.

`AP-012` follows §4.1 (Legal Counsel), and `AP-001`/`AP-002` follow §4.1 (Programme Content
Lead), because §4.1 is declared authoritative in `CG-002`'s own note: *"Counts are derived from
§4.1, which is the authoritative allocation."*

**Remediation instruction.** Correct `CG-002` §6's approver column to show the class **set** per
category, or add a note that §4.1 governs per file. One-line fix; recorded because six categories
inherit it.

---

### AP-10 — `AC-nn` is document-scoped and was cited unqualified

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Programme Content Lead (auditor's own authoring)**

**What was found.** `M28`, `P04` and `P08` each run their own `AC-01`… acceptance-criterion
sequence. `AC-08` means *"100% of published endpoints have a current, CI-validated OpenAPI 3.1
specification"* in `M28` and *"a 2,000-line consolidated invoice decomposes and filters in under 3
seconds"* in `P04`. **Both meanings were used in this category, unqualified, in different files.**

Fifty-eight `AC-nn` references were extracted across the twelve files. Nineteen were already
qualified with their owning document; thirty-nine were not.

This is the same class as the module-scoped rule-family pattern `AUDIT-010` and `AUDIT-014`
recorded for `BRU-QMS-*`, `BRU-CAI-*` and `BRU-KMS-*` — an identifier series that reads global and
is not.

**Remediation applied.** All ambiguous references qualified: `AC-08` → `M28` `AC-08` (5), `AC-13`
→ `M28` `AC-13` (9), `AC-01` → `P04` `AC-01` (1). `AP-008`, which uses `AC-nn` thirty-three times
and always means `P04`, carries an explicit identifier-scoping declaration in its
template-conformance note rather than thirty-three inline qualifications. **Verified by
re-extraction after the fix.**

---

### AP-11 — `AP-006`'s title carried a word not in its file stem

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Programme Content Lead (auditor's own authoring)**

The register file name is `AP-006_Error_Code_Catalogue_and_Remediation_Copy.md`; the file was
authored with `title: API Error Code Catalogue and Remediation Copy`. Every other file in the
category, and every file in Category 13, derives its title from its stem word for word.

Fixed in both the front matter and the H1.

**Five titles restore punctuation their stems cannot carry** — `AP-005` (comma), `AP-007` and
`AP-008` (em dash), `AP-011` (comma), `AP-012` (hyphen in "Field-Level"). **That is not the same
defect and is not a defect at all:** a file name cannot hold a comma, an em dash or a hyphen
without breaking the `<CODE>-<nnn>_<Title_Case_With_Underscores>` convention, so restoring
punctuation in the title is required rather than optional. `AP-006`'s defect was an added **word**.
Recorded so the distinction is not lost on the next sweep, and so a future check does not flag all
five.

---

### AP-18 — This report's own F7 wave row was stated before it was derived

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Programme Content Lead (auditor's own work)**

**What was found.** §2.1's gate F7 table originally carried **"W3×6, W4×6"** as the expected wave
distribution, against an actual of "all 12 match", and concluded ✅.

**Extraction of the Master Index §4 register rows gives `W3×7, W4×5`.** The twelve files match the
register exactly, so the conclusion was right — **but the expected value was written from memory
rather than derived, and it was wrong in both columns simultaneously, which is why the error
cancelled and the row still read as a pass.**

**Why it matters more than the arithmetic.** This is the exact failure mode gate F7 exists to
catch, occurring **inside the audit that verifies gate F7**. `AUDIT-002`, `AUDIT-003` and
`AUDIT-005` all found the same thing — *a summary table written before the derivation it
summarises, and never reconciled against it* — and `AUDIT_Checklist_Recurring.md`'s F7 note says
so explicitly: *"Prose review missed all three; enumeration caught all three."* Prose review missed
this one too. It was caught on a final re-derivation pass, four checks after the table was written.

**A cancelling error is worse than a visible one**, because a mismatch would have failed the row
and forced a re-derivation. Two compensating errors produce a green tick over an unverified claim.

**Remediation applied.** The row now reads `W3×7, W4×5`, extracted from the register by `awk` over
the `AP-` rows rather than recalled. **Every other F7 row was re-derived at the same time and all
six were already correct.**

**Instruction to the next auditor.** Derive every F7 expected value from its source register in the
same pass that derives the actual, and never from the audit's own earlier prose. Proposed as an
addition to `RG-08` in §7.

---

### AP-12 — The partner sandbox is a seventh environment and `TS-001` §4.7 recognises six

**Severity: MEDIUM · Status: OPEN · Owner: CTO with QA Lead and `M30` owner**

`TS-001` §4.7 specifies six environments — `DEV`, `CI`, `SIT`, `UAT`, `PERF`, `TRAIN` — and
records at its `O-03` that **none of the six is specified or provisioned**. `FR-IPF-019` requires
a sandbox with representative masked data for external consumers.

`AP-010` §4.2 tested each of the six against the requirement. **None can serve**, and `UAT`
emphatically cannot: `TS-001` §4.7 requires UAT data to be *frozen during a UAT cycle*, and
`TX-08` voids a script whose expected results were not written before execution. **A partner
exercising integration flows in UAT changes the data business super-users are signing against.**

The sandbox's data-state requirements are unlike any of the six: stable enough to build against,
resettable per partner, externally reachable, externally credentialled, and holding **no real
personal data at all** — a stricter bar than `NFR-071`'s masking, because the population with
access is outside the company.

**Remediation instruction.** Add `SANDBOX` to the environment inventory in `TS-001` §4.7 with its
own data-state row, and carry it into whatever provisions the other six. Recorded as `AP-010`
`O-03`; it is a correction to a Category 13 file, so it needs the QA Lead as well as the author.

---

### AP-13 — `AP-009` is runbook-shaped and `CG-009` §3 allocates it the generic template

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with Content Design Lead**

`CG-009` §3 allocates all twelve `AP` files to template 1 (Generic) with two additions.
`AP-009_Payment_Gateway_Integration_Runbook_Content.md` is, by its own registered name and by its
content, a **runbook**: failure modes, manual fallback, drills, escalation. `TPL_Runbook.md`
exists and governs exactly that shape — health checks, routine operations, failure modes, incident
response, manual fallback, backup and recovery, break-glass — for the sixteen Category 17 files.

The allocation was **followed as written** (`CP-09`), and the runbook material sits inside §4
rather than in runbook sections. The file is coherent; the question is whether the allocation is
right.

`OP-014_Manual_Fallback_Procedure_Set.md` is the adjacent Category 17 file and it **does** use
`TPL_Runbook.md`. Two files covering the manual fallback for the same `P0` integrations, on two
different templates, is a boundary worth settling before both are approved.

**Remediation instruction.** Content Design Lead to rule on whether `AP-009` moves to template 12,
and to state the `AP-009` / `OP-014` boundary in one place. Recorded as `AP-009` `O-08`.

---

### AP-14 — The six-month API notice promise appears in no partner agreement

**Severity: MEDIUM · Status: OPEN · Owner: Legal Counsel with Commercial Director**

`05-03` §3.4 and `API-02` promise at least two concurrent API versions and **six months' notice**
before removing one. `BRU-IPF-05` makes it a hard rule internally and `FR-IPF-014` enforces the
clock.

**The promise is made in an architecture document.** `LG-003` corporate terms, `LG-005` brand
terms, `LG-006` vendor terms and `LG-007` partner terms are the instruments that would bind it,
and none is cited anywhere as containing an API notice clause.

**The asymmetry runs both ways.** 1000FiX cannot contractually require a partner to migrate off a
deprecated version — which is precisely why `M28` Q-08 (*"what is the escalation path when a
consumer refuses to migrate and blocks a sunset?"*) has no answer and `BRU-IPF-05` gives the
platform no unilateral remedy. And a partner cannot hold 1000FiX to the six months, so a shortened
notice has no contractual consequence.

**Remediation instruction.** Legal Counsel to add a reciprocal API lifecycle clause to the four
partner agreements — notice period, the partner's obligation to maintain a supported version, and
the emergency security exception — before the first external contract is signed. Recorded as
`AP-011` `O-02`, and it is the missing piece of `AP-011` §4.7 stage 3.

---

### AP-15 — Category 15 carries zero relative markdown links

**Severity: LOW · Status: OPEN · Owner: Programme Content Lead**

Extraction found **zero relative markdown links** across all twelve files. Every cross-reference
is a backticked identifier — `` `AP-005` ``, `` `05-03` §4.2 `` — which resolves for a reader who
knows the repository and does not resolve for one who does not.

`AUDIT-014` `D1` counted **13 relative links across 18 `TS` files**, and `CG-006` and `CG-009`
both use them. Check `D1` passes trivially — zero links, zero broken — but the check was written
to catch broken links, not to notice their absence.

The category's audience makes this worth acting on: `AP-001` §3 identifies seven audiences, five
of them **external**, and an external developer reading `` `LG-005` `` has no way to reach it.

**Remediation instruction.** Add relative links on first mention of each cross-category reference,
at least for the files published externally. Consider extending check `D1` to report a link
density so that "zero broken" and "zero present" are distinguishable.

---

### AP-16 — Audit-trail dates run ahead of the filesystem

**Severity: LOW · Status: OPEN · Owner: Programme Content Lead**

Extraction of front-matter dates against filesystem timestamps found the audit trail dated ahead
of the work it records:

| Artefact | Declared date | Enumeration instant in its own body | Filesystem |
|---|---|---|---|
| `AUDIT-014` | 2026-08-19 | 2026-08-19 | written 2026-08-17 |
| `AUDIT-015` | **2026-08-20** | **2026-08-17 16:45 UTC** | written 2026-08-17 |
| README / Master Index | various, to 2026-08-20 | — | modified 2026-08-17 16:46–16:47 UTC |

`AUDIT-015` carries `date: 2026-08-20` and `enumeration_date: 2026-08-20` while its own §2 states
the count was taken at **2026-08-17 16:45 UTC** — three days earlier than the report that quotes
it.

`CG-012` and `CM-R8` require a verification date on every claim, and `CP-11` requires counts to be
generated and dated. **A date that runs ahead of the evidence it stamps undermines both**, and it
is the audit trail — the one artefact whose chronology has to be reliable.

This report is dated **2026-08-18** and stamps its enumeration to the minute in UTC, which is the
convention proposed for adoption.

**Remediation instruction.** Adopt a single rule: `date:` is the day the artefact was written, and
`enumeration_date:` is the UTC instant the count was taken. Correct `AUDIT-015`'s header.

---

### AP-17 — Four categories were authored concurrently and the completion figure was rewritten mid-flight

**Severity: LOW · Status: OPEN · Owner: Programme Content Lead**

**What was found.** During the Category 15 authoring and audit window:

| UTC instant | Event |
|---|---|
| 15:53 | Category 14 `RP`, 16 `CM`, 17 `OP`, 18 `EO` folders empty; enumeration would return 352 |
| 16:38–16:45 | Categories 14, 16 and 18 written; 17 `OP` written to 15 of 16 |
| **16:45** | `AUDIT-015` enumerates **427**, with `OP` **caught mid-authoring at 15 of 16** and recorded as such |
| 16:46–16:47 | Master Index §1 and README rewritten to 427, described as *"a floor"* |
| **16:49** | This audit enumerates **428** — `OP-016` had landed in the intervening four minutes |

`AUDIT-015` handled this correctly: it labelled 427 **"a floor, not a total"**, named `OP` as in
flight, and said so in the README row. That is the right response and it is why this is Low rather
than High.

**But it is the live recurrence of the hazard gate F7 exists for.** `AUDIT-014` `TS-11` recorded
the fifth gate-F7 breach — *"a completion figure that led the work rather than lagging it"*. Here
the figure did not lead the work, but it was **taken during** it, and it was already stale four
minutes after publication. A figure that is correct for four minutes is not a figure a Steering
Committee paper can quote.

**Remediation instruction.** Add to gate F7: **a completion figure is taken only when no category
is in flight, and it carries its UTC instant.** Where a figure must be published during authoring,
it is labelled a floor and names the categories in flight — which `AUDIT-015` did, and which
should become the rule rather than a good instinct. Proposed as rule `RG-08` in §7.

---

## 4. Findings summary

| ID | Finding | Severity | Owner | Status |
|---|---|:--:|---|:--:|
| **AP-01** | 21 event names consumed by specifications, unregistered; 14 genuinely missing including a control and a safety flow | **Critical** | Enterprise Architecture + CTO | Open |
| **AP-02** | `NFR-090`/`-091`/`-092` mean two different requirements each in `05-06`; `NFR-088`/`-089` duplicated | **Critical** | Enterprise Architecture | Open |
| **AP-03** | 8 of 12 files registered after first consumption; 6 needed at W1 | High | Programme Content Lead | Open |
| **AP-04** | No webhook signature scheme exists; no webhook management endpoints registered | High | CTO + Security Lead | Open |
| **AP-05** | No scope naming convention exists; credentials scoped by judgement | High | Solution Architect + Security Lead | Open |
| **AP-06** | Three payment availability commitments do not reconcile | High | CTO + CFO | Open |
| **AP-07** | ITSM integration is `P3`/W7 against a W4 "condition of contract" | High | Commercial Director + CTO | Open |
| **AP-08** | Class `B` register incompletable; 3 W3 couriers undetermined; no DPIA, processor inventory or DPO | High | Legal Counsel + Security Lead | Open |
| **AP-09** | `CG-002` §6 and §4.1 disagree on approver class for six categories | Medium | Programme Content Lead | Open |
| **AP-10** | `AC-nn` document-scoped, cited unqualified | Medium | Programme Content Lead | **Fixed** |
| **AP-11** | `AP-006` title carried a word not in its stem | Medium | Programme Content Lead | **Fixed** |
| **AP-12** | Partner sandbox is a seventh environment; `TS-001` §4.7 has six | Medium | CTO + QA Lead | Open |
| **AP-13** | `AP-009` runbook-shaped on the generic template; `AP-009`/`OP-014` boundary unstated | Medium | Content Design Lead | Open |
| **AP-14** | Six-month API notice promise in no partner agreement | Medium | Legal Counsel + Commercial | Open |
| **AP-18** | This report’s own gate F7 wave row was stated before it was derived, with two cancelling errors producing a false pass | Medium | Programme Content Lead | **Fixed** |
| **AP-15** | Zero relative markdown links in a category with five external audiences | Low | Programme Content Lead | Open |
| **AP-16** | Audit-trail dates run ahead of the evidence they stamp | Low | Programme Content Lead | Open |
| **AP-17** | Four categories authored concurrently; completion figure stale within four minutes | Low | Programme Content Lead | Open |

---

## 5. Remediation applied during the audit

| # | Change | File(s) | Finding |
|---|---|---|---|
| 1 | `AC-08` qualified to `M28` `AC-08` — 5 occurrences | `AP-001`, `AP-002` | AP-10 |
| 2 | `AC-13` qualified to `M28` `AC-13` — 9 occurrences | `AP-009` | AP-10 |
| 3 | `AC-01` qualified to `P04` `AC-01` — 1 occurrence | `AP-010` | AP-10 |
| 4 | Identifier-scoping declaration added, covering 33 `P04` `AC-nn` references | `AP-008` | AP-10 |
| 5 | `title:` and H1 corrected to match the file stem | `AP-006` | AP-11 |
| 5a | **Gate F7 wave row corrected from `W3×6, W4×6` to the derived `W3×7, W4×5`; all seven F7 rows re-derived from their source registers** | this report §2.1 | **AP-18** |
| 6 | Master Index §1 completion figure and Category 15 status row updated with a UTC-stamped count | `1000FiX_ERP_Content_Master_Index.md` | AP-17 |
| 7 | README status table and audit index updated | `README.md` | AP-17 |

**Nothing else was changed.** Findings AP-01 through AP-09 and AP-12 through AP-17 are reported,
not quietly fixed — twelve of the fifteen open findings are owned outside the content function and
cannot be closed by editing content.

---

## 6. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Rule on whether `05-03` §4.2 is a complete inventory or a principal subset, and say so in the heading.** Everything in AP-01 follows from that one word | Enterprise Architecture | **W1** |
| **R-02** | **Renumber the three PDPA requirements out of the `NFR-090`…`NFR-092` collision**, delete the stray `NFR-088`/`-089` rows in `05-06` §6.4, and sweep every citation in both repositories | Enterprise Architecture | **W1** |
| **R-03** | **Correct the register's sequencing basis once, register-wide, before Categories 19 and 99 are authored.** Twenty-eight late-registration instances across six categories will not be fixed file by file — `AUDIT-010` R-02 already proved that | Programme Content Lead + CTO | **Before Category 19 authoring** |
| **R-04** | **Extend audit check `F4` to cover `AP-006` → `UI-004`.** `F4` today verifies only that error-message IDs cited by `MD` validation rules exist in `UI-004`. `AP-006` §4.9 establishes a 24-row binding register between API error codes and UI keys, and it needs the same mechanical check | Programme Content Lead | W3 |
| **R-05** | **Ratify the three W1-blocking platform decisions together** — webhook signature scheme (AP-04), scope vocabulary (AP-05) and the `API-04`/RFC 9457 envelope question. All three are cheap now and expensive after W1 endpoints ship | CTO + Security Lead + Solution Architect | **W1 design** |
| **R-06** | **Add `SANDBOX` to the `TS-001` §4.7 environment inventory** with its own data-state row, and carry it into provisioning | QA Lead + CTO | W3 |
| **R-07** | **Commission the DPIA and build the processor-contract inventory.** `NFR-098` is unmet across 47 integrations and enforcement activates inside Wave 4 | Legal Counsel + `M60` owner | **W3** |
| **R-08** | **Add a reciprocal API lifecycle clause to `LG-003`, `LG-005`, `LG-006` and `LG-007`** before the first external contract is signed | Legal Counsel | **W3** |
| **R-09** | **Correct `CG-002` §6's approver column** to show the class set per category, or note that §4.1 governs per file. Six categories inherit the inconsistency | Programme Content Lead | W3 |
| **R-10** | **Adopt the date convention in AP-16** and correct `AUDIT-015`'s header | Programme Content Lead | Immediate |

---

## 7. Closure

**Category 15 `AP` is complete as specified: 12 of 12, all at `Draft`.** Gate F7 reconciles
exactly across all seven dimensions. All 102 cited content identifiers, all 37 `FR-IPF-`, all 5
`FR-SEC-`, all 17 `FR-POR-`, all 23 `BRU-`, all 15 gate criteria and all 32 `NFR-` citations
resolve.

**No file in this category can reach `Approved`.** Each carries between six and eight open items,
and the binding constraints are:

| Constraint | Files affected |
|---|---|
| Three W1 platform decisions unmade — signature scheme, scope vocabulary, error envelope | `AP-002`, `AP-004`, `AP-005`, `AP-006` — 4 of 12 |
| Fourteen unregistered events | `AP-003`, `AP-007`, `AP-008` — 3 of 12 |
| Named approvers not recorded | **All 12** |
| Legal Counsel sign-off absent (`CM-R7`) | `AP-012` — the Class `B` file |

**The category's own finding about itself.** Eleven of the twelve files record, in their own open
items, that they are registered at a wave after the wave that consumes them. That is not modesty:
`FR-IPF-002`, `-003`, `-004`, `-006`, `-012`, `-016`, `-018`, `-021`, `-023`, `-024` and `-025`
are all `P0` and all W1, and every one of them consumes content this register places at W3 or W4.
**Category 15 is content the platform needs before the platform exists**, and the register does
not say so.

### Proposed governance rule

> **`RG-08` — A completion figure is taken only when no category is in flight, and it carries the
> UTC instant it was taken.** Where a figure must be published while authoring is in progress, it
> is labelled a **floor**, names the categories in flight, and states their partial counts.
>
> Derived from AP-17. `AUDIT-015` did all three by instinct and was still four minutes out of date
> on publication. Gate F7 already blocks a category being *declared complete* on a divergent
> count; `RG-08` extends the same discipline to the repository total, which is the figure that
> reaches a Steering Committee paper.

---

*Audit 016 · Category 15 `AP` · 1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
