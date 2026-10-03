---
id: DA-004
title: Master Data Management Design
category: 03 — Data & Information Architecture
code: DA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: MDM Lead
approver: Chief Data Officer (unappointed — see DA-003 §5)
standards_basis: >
  DAMA-DMBOK 2.0 (2024 maintenance revision) — Reference & Master Data knowledge area ·
  ISO/IEC 11179-1:2023 · Golden-record / survivorship practice · ISO/IEC 25012
traces_to: >
  PGD-000 DA-004 · M64 MDM · MD-001 (charter) · DM-011 (migration matching & survivorship) ·
  AR-008 (party kernel) · DA-001 §4.5 (keys) · DA-003 (stewardship)
depends_on: DA-001 · DA-003 · AR-008 · DM-011
verified_on: 2026-08-18
priority: P1
needed_by: W2
enumeration_timestamp: 2026-08-18 14:30 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# DA-004 — Master Data Management Design

### Category 03 · Code `DA` · DAMA-DMBOK 2.0 Reference & Master Data · Golden-record design

---

## 1. Purpose

`M64` specifies MDM as a **module**. The 48 `MD-*` files provide **seed content**. `DM-011` designs
matching and survivorship **for the migration**. `MD-001` charters **ownership**.

**What does not exist is the design for steady state** — the question the register puts precisely:
*"how two customer records become one, and what happens to the loser's service history."*

A migration deduplicates once, against a frozen extract, with a funded stewardship queue. Production
deduplicates **continuously**, against live data, while a technician is at a customer's door and a
payout is pending. Those are different problems, and only the first has a design.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | Which entities are master data, and which are not |
| 2 | The golden-record model — style, and why |
| 3 | **Match, merge and split in steady state**, including the live-transaction cases `DM-011` does not face |
| 4 | Survivorship at attribute level, extended from `DM-011` §2.7 to production |
| 5 | **What happens to the loser** — history, transactions, balances, consent, identity |
| 6 | Hierarchy management — corporate accounts, party roles, catalogue, organisation |
| 7 | Distribution to consuming systems and the portal platform |
| 8 | The **unmerge** obligation and its window |
| 9 | The `M64` timing gap and the interim design |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Migration-time matching and cleansing | `DM-011`, `MG-003` | One-time; this document is steady state |
| Master-data **content** | The 48 `MD-*` files | Retained as content authority |
| Ownership and stewardship roles | `DA-003` | This document consumes them |
| Quality rules and scorecard | `DA-008`, `RP-016` | Measurement, not merging |
| Code lists and enumerations | `DA-009` | Reference data, not master data (§2.2) |
| Physical schema | `DA-001` | |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **M64 developers** | This is the module's design brief |
| MDM Lead and domain stewards | §4–§6 are the operating model |
| M33 (party) developers | §5 — the party merge is the hardest case and the most consequential |
| Finance | §5.4 — what happens to a balance on merge |
| DPO | §5.6 — a wrong merge is a personal-data incident, not a quality defect |

---

## 2. What Is Master Data

### 2.1 The test

> **A record is master data if it is (a) referenced by more than one business process, (b) has an
> independent lifecycle, and (c) more than one system or team must agree on it.**

Reference data (§2.2) is agreed but has no independent lifecycle. Transactional data has a lifecycle
but is not agreed — it belongs to the process that created it.

### 2.2 The three classes, and why the distinction matters

| Class | Definition | Examples | Governed by |
|---|---|---|---|
| **Master data** | Agreed, independently lifecycled, cross-process | Party, asset, catalogue item, employee, branch, vendor, seller, contract | **`DA-004`** — this document |
| **Reference data** | Agreed, no independent lifecycle, enumerated | Fault codes, reason codes, status labels, UoM, tax codes, currencies | **`DA-009`** |
| **Transactional data** | Process-owned, not agreed | Service orders, invoices, movements, events | The owning module |

> **Conflating master and reference data is the most common MDM design error.** A fault code needs
> version control and an approval workflow; it does not need survivorship, match/merge or a golden
> record, because two fault codes are never "the same code recorded twice by different branches".
> Building merge machinery for reference data wastes it; omitting it for master data is fatal.

### 2.3 The master-data entities

| Domain (`DA-003` §3.2) | Master entities | Merge risk |
|---|---|---|
| **DD-01 Party** | `fix.party` + roles, hierarchy, addresses, identity documents | **Highest** — §5 |
| **DD-02 Device & asset** | `fix.asset`, brand, model | **High** — a wrong serial blocks a warranty claim |
| **DD-03 Catalogue & pricing** | `fix.catalogue.item`, part, service kit | Medium |
| **DD-05 Supply** | Vendor, warehouse location | Medium |
| **DD-07 Workforce** | `hr.employee`, position, competency | Low volume, **high consequence** |
| **DD-08 Commercial agreement** | Contract, marketplace seller | Medium |
| **DD-09 Organisation** | Entity, branch, zone | Very low volume; changes are governed, not merged |

---

## 3. The Golden-Record Model

### 3.1 Style — registry, consolidation or coexistence

| Style | What it means | Assessment |
|---|---|---|
| **Registry** | Sources keep their records; MDM holds only cross-references | **Rejected.** The ERP *is* the system of record (`AR-002` AP-01); there are no persistent competing sources at steady state |
| **Consolidation** | MDM builds a golden record for reporting; sources stay authoritative | **Rejected.** Produces a golden record nobody transacts against |
| **Centralised / coexistence** | **The ERP holds the golden record and transacts on it.** External systems synchronise from it | **Chosen** |

### 3.2 The chosen model

| # | Rule |
|---|---|
| **GR-01** | **The golden record is the operational record.** There is no separate "MDM copy" — a golden record nobody transacts against is a report |
| **GR-02** | The golden record is built **attribute by attribute**, not by choosing a winning row (`DM-011` `DQ-17`) |
| **GR-03** | Every attribute carries its **authoritative source, its survivorship rule and the date it won** (`DQ-18`) |
| **GR-04** | **The merge loser is retained**, `active = False`, with `golden_record_id` pointing at the survivor (`DQ-19`, `MD-013`). Never deleted (DM-06) |
| **GR-05** | **Every entity in `DA-001` has exactly one owning master dataset.** An attribute maintained in two places is a defect (`MD-001` `GR-01`) |
| **GR-06** | A code is **never reused**, even after archive (`MD-001` `GR-04`) |

### 3.3 Why the loser is retained rather than deleted

Four independent reasons, any one of which is sufficient:

| Reason | Detail |
|---|---|
| **Referential integrity** | `DA-001` §6.2 sets transaction → master as `RESTRICT`. Deleting the loser would be refused by the database, and forcing it would orphan history |
| **Reversibility** | `DQ-20` requires merges reversible during the burn-down. An unmergeable merge means the auto-merge threshold was set too low |
| **Inbound references** | A customer quoting an old order number, a brand quoting an old claim, a courier quoting an old consignment — all resolve through the loser |
| **Audit** | `RC-22` retains access logs 5 years. A log entry referencing a deleted party is unexplainable |

---

## 4. Match and Merge in Steady State

### 4.1 What changes from `DM-011`

`DM-011` §2.5–§2.7 designs matching for the migration. **The algorithm carries over unchanged.** What
changes is the context, and the context is harder:

| Dimension | Migration (`DM-011`) | **Steady state (this document)** |
|---|---|---|
| Data | Frozen extract | **Live, changing during evaluation** |
| Timing | Batch, before go-live | **Continuous, at create and on change** |
| Transactions in flight | None | **Open orders, reserved stock, pending payouts, active SLA clocks** |
| Stewardship capacity | Funded migration team | **Business-as-usual, competing with operations** |
| Cost of a wrong merge | Correctable before go-live | **A personal-data incident** (`DQ-15`) |
| Reversibility | Full, during burn-down | **Bounded window** (§7) |

### 4.2 When matching runs

| Trigger | Behaviour |
|---|---|
| **Party create** | Real-time candidate check on `primary_mobile`, `nid` (via CD-233), `bin`. **Pass 1 only** — a create must not block on fuzzy scoring |
| Party update to an identity key | Re-evaluate pass 1 and 2 |
| **Nightly batch** | Full pass 1–3 over records changed since the last run |
| Weekly | Full pass 3 sweep over the active population |
| On demand | Steward-initiated for a named candidate set |
| **Asset create** | Real-time on `imei`, `serial` + `model_code` (pass 1) |

> **A create is checked synchronously on deterministic keys only.** A branch agent at a counter with a
> customer in front of them cannot wait for fuzzy scoring across 3 M parties (NFR-076: intake in ≤ 3
> minutes). Fuzzy candidates surface in the nightly queue.

### 4.3 The thresholds

Carried from `DM-011` §2.6 **unchanged**, so pre- and post-go-live behaviour is comparable.

| Band | Score | Action |
|---|---|---|
| **Auto-merge** | ≥ **0.95** | Merged automatically; survivorship applied |
| **Review** | 0.80 – 0.95 | **Stewardship queue** — a human decides |
| Weak candidate | 0.65 – 0.80 | Recorded as a *possible link*, not merged |
| No match | < 0.65 | Distinct |

**`DQ-15` asymmetric caution carries over in full:** for `fix.party`, auto-merge requires **0.95 *and*
a pass-1 or pass-2 match**. A pass-3 score of 0.96 does not auto-merge.

### 4.4 What blocks an automatic merge in production

**Six blocking conditions that do not exist at migration time.** Any one routes to the steward queue.

| # | Blocker | Why |
|---|---|---|
| **MB-01** | **Either party has an open financial balance** | `DQ-17`: *"Two balances are two facts, not one."* Merging creates a balance nobody can reconcile |
| **MB-02** | Either party has an **open service order, active SLA clock or dispatched technician** | A merge mid-job re-points the order under the technician's feet |
| **MB-03** | Either party has a **pending payout or commission entry** (marketplace seller) | Money in flight to a party identity that is about to change |
| **MB-04** | The two parties have **conflicting consent states** | `MS-20` / `DQ-17`: consent never survives from either record. A merge cannot manufacture a consent position |
| **MB-05** | Either party is under a **legal hold** or has an open data-subject request | `OV-01` is absolute |
| **MB-06** | The two parties hold **different residency-classified identifiers** (two different NIDs) | Two NIDs is strong evidence of two people. **Escalate, never merge** |

> **MB-06 is the safety catch.** Pass 1 matches on mobile; two people can share a mobile — a family, a
> shop counter. If both records carry a *different* NID, the mobile match is a false positive and an
> automatic merge would expose one person's service history to another.

### 4.5 Survivorship — extended to production

`DM-011` §2.7's attribute rules carry over. **Four additions for steady state:**

| Attribute class | Survivorship rule | Source |
|---|---|---|
| Identity keys — mobile, NID, BIN | Most recently **verified**, then most frequent | `DQ-17` |
| Names | Longest complete form from the most authoritative source | `DQ-17` |
| Bengali name | From the source with verified encoding | `DQ-17` |
| Address | Most recently **used** — an address with a completed delivery wins | `DQ-17` |
| Segment, tier, credit terms | From the **commercially authoritative** source, never the most recent edit | `DQ-17` |
| **Consent** | **Never survives from either record** | `DQ-17`, `MS-20` |
| Dates | Earliest evidenced, from a document where one exists | `DQ-17` |
| Free text | Concatenated with source attribution | `DQ-17` |
| Balances and quantities | **Never merged** — escalate | `DQ-17`, MB-01 |
| **Loyalty points** | **Summed, with a ledger entry recording the merge** | **New** — a balance the customer can see; silently losing it is visible and indefensible |
| **Privilege tier** | **The higher tier survives** | **New** — never demote a customer through an administrative action |
| **Marketplace seller score** | **Never merged — escalate to the Council** | **New** — a score is earned; merging two sellers' reputations is a commercial and fairness question |
| **Certifications (employee)** | **Union of both**, each retaining its own expiry | **New** — a certification is evidence, and losing one blocks dispatch (`I-38`) |

---

## 5. What Happens to the Loser

**The register's question, answered.**

### 5.1 The re-pointing rule

| # | Rule |
|---|---|
| **RP-01** | **Every transactional reference is re-pointed to the survivor**, in one transaction |
| **RP-02** | The loser is retained `active = False` with `golden_record_id` → survivor |
| **RP-03** | **Every re-pointed row records the merge** — `merged_from_id` and `merged_at`, so a report can explain why a 2024 order sits under a party created in 2026 |
| **RP-04** | A **`party.merged` domain event** is published (`AR-009`), and every consumer holding a party id reacts. `05-03` §4.2 already registers `customer.merged`; `AR-008` §3 rules the aggregate name `party` |
| **RP-05** | Re-pointing is **one transaction**. A partial merge is worse than no merge |

### 5.2 What re-points, by class

| Class | Behaviour |
|---|---|
| Service and work orders | Re-pointed. History consolidates — **this is the point of merging** |
| Assets and ownership | Re-pointed; ownership history preserved with both party references |
| Contracts and entitlements | Re-pointed. **Entitlement balances are additive**; overlapping coverage is flagged to the account manager |
| Invoices, payments, credit notes | Re-pointed. **Balances are not summed** — MB-01 means the merge did not proceed automatically |
| Loyalty points | **Summed with a ledger entry** (§4.5) |
| Consent records | **Both retained, neither inherited.** The survivor's consent position is whatever it was |
| Identity documents | **Both retained.** MB-06 means an automatic merge did not proceed if they differ |
| Audit and access logs | **Never re-pointed.** A log records what happened to *that* record at *that* time |
| Notifications | Not re-pointed; historical delivery is a historical fact |
| Warehouse / analytics | **`party.merged` triggers a dimension update** — `DA-007` §6 Type-2 SCD handles it |

> **The audit-log exception matters.** Re-pointing an access log would rewrite the record of who
> accessed what — which is the one thing an audit log exists to prevent (`RS-08`: audit entries are
> insert-only and cannot be deleted by anyone).

### 5.3 The customer-visible consequence

| Question | Answer |
|---|---|
| Does the customer see their old orders? | **Yes** — that is the benefit |
| Does an old order number still resolve? | **Yes**, via the loser's `golden_record_id` |
| Do their loyalty points survive? | **Yes**, summed, with a ledger entry |
| Does their privilege tier drop? | **No** — the higher survives |
| Are they told? | **Yes**, where the merge changes anything they can see. `UI-*` copy is a content dependency (§10 Q-04) |

### 5.4 The finance position

| # | Rule |
|---|---|
| **FN-01** | **A merge never sums two balances.** MB-01 routes it to a steward |
| **FN-02** | Where a steward proceeds, the merge is executed as an **explicit transfer with a journal entry**, not as a silent consolidation. Finance must be able to see it happened |
| **FN-03** | Posted documents are **immutable**. An invoice raised to the loser keeps the loser's name and address as printed — that is what the customer holds and what the NBR received |
| **FN-04** | Only the **party reference** is re-pointed, so future statements consolidate; the historical document does not change |

> **FN-03 is the rule most likely to be argued about.** Re-printing a Mushak 6.3 with the survivor's
> details would produce a document that disagrees with the copy in the customer's file. The ledger
> consolidates; the artefact does not.

### 5.5 Split — the inverse operation

| # | Rule |
|---|---|
| **SP-01** | **A split is not an unmerge.** It separates records that were always distinct but recorded as one — typically a shop counter's shared mobile |
| **SP-02** | A split requires a **steward decision with evidence**; it is never automatic |
| **SP-03** | Transactions are re-pointed **individually** by the steward. There is no algorithm for which order belonged to whom |
| **SP-04** | A split produces a **new party**, never resurrects a merged loser (that is unmerge, §7) |
| **SP-05** | Where transactions cannot be attributed, they **stay with the original** and the fact is recorded |

### 5.6 The personal-data position

> **A wrong merge exposes one person's service history, addresses and contact details to another.**
> `DQ-15` names it: *"a personal-data incident under the PDPA 2026, not a data-quality defect."*

| # | Rule |
|---|---|
| **PD-01** | A merge later determined wrong is handled as a **potential personal-data breach**, assessed under `SC-011`, not as a data-quality ticket |
| **PD-02** | The **CDO** is notified of any unmerge performed for a data-protection reason |
| **PD-03** | Breach notification to the Authority (NFR-094) is assessed where the exposure is material |

---

## 6. Hierarchies

### 6.1 The four hierarchies

| Hierarchy | Structure | Owner | Rules |
|---|---|---|---|
| **Corporate account** | Group → company → division → site | DD-01 / CCO | Consolidated invoicing, entitlement inheritance, approval chains |
| **Party role** | One party, many simultaneous roles | DD-01 / CCO | **A seller may also be a customer** (`AR-001` §6.3) |
| **Catalogue** | Category → family → item → variant | DD-03 / CCO | Pricing and compatibility inherit |
| **Organisation** | Entity → branch → zone → team | DD-09 / Ops | Record-rule scoping (T1–T3) |

### 6.2 Rules

| # | Rule |
|---|---|
| **HR-01** | **Every hierarchy is acyclic**, enforced by a check on write. A cycle in a corporate account makes consolidated invoicing non-terminating |
| **HR-02** | Depth is **bounded and declared** — corporate 4, catalogue 4, organisation 4 |
| **HR-03** | Inheritance is **declared per attribute**, never implicit. Payment terms inherit; credit limit does not |
| **HR-04** | A node move **re-parents children** and emits an event; it does not orphan them |
| **HR-05** | **Effective-dated** where a restructure must not rewrite history (`DA-001` §4.7) |
| **HR-06** | A **party holding multiple roles is not a hierarchy** — it is one record with several role rows (`AR-012` `FF-08`) |

> **HR-06 is the rule the estate's own architecture calls the easiest to violate.** Modelling seller,
> customer, vendor and partner as separate master records joined by reference produces exactly the
> duplicate-identity problem the programme exists to remove — and it is unrecoverable once transaction
> volume accrues against the duplicates.

---

## 7. Unmerge

| # | Rule |
|---|---|
| **UM-01** | **A merge is reversible for 90 days**, or until a transaction is created against the survivor that could not have belonged to either original — whichever is sooner |
| **UM-02** | Reversal restores the loser to `active = True` and re-points only the rows carrying its `merged_from_id` |
| **UM-03** | Rows created *after* the merge are **not** re-pointed. They belong to the survivor |
| **UM-04** | **After the window, unmerge is a split** (§5.5) — manual, evidence-based, steward-executed |
| **UM-05** | Every unmerge is logged with actor, reason and timestamp, and **the CDO is notified where the reason is data protection** (PD-02) |

> **The window exists because `DQ-20` requires reversibility and physics does not.** Once a customer
> has placed an order against the merged identity, paid an invoice and earned points, "which original
> did this belong to" has no answer. Ninety days is a judgement — long enough for a wrong merge to
> surface at the next service contact, short enough to bound the state the system must retain.

---

## 8. Distribution

### 8.1 Who consumes master data

| Consumer | Mechanism | Latency |
|---|---|---|
| ERP modules | **Direct** — one golden record, no distribution (GR-01) | — |
| **Portal platform** (`CON-03`) | `party.*`, `catalogue.*` events + versioned API | Event-driven, near real-time |
| Warehouse (`DA-007`) | Event projection → Type-2 SCD dimension | Per freshness guarantee |
| Keycloak | Identity provisioning on `employee.joined` / `.left` | ≤ 1 hour for leaver |
| External partners | **Never directly.** Scoped API only | Per contract |

### 8.2 Rules

| # | Rule |
|---|---|
| **DI-01** | **Distribution is by event, not by batch export.** A nightly CSV of the party master is a second copy that diverges |
| **DI-02** | `party.merged` is a **first-class event every consumer must handle** (RP-04) |
| **DI-03** | A consumer holding a party id must **tolerate re-pointing** — resolve through `golden_record_id`, never assume an id is permanent |
| **DI-04** | **No consumer receives a residency-classified value** (`DA-001` §10) |
| **DI-05** | Portal caches are **for performance, never for truth** (`AR-002` EP-01) |
| **DI-06** | A **nightly reconciliation** compares party and asset counts with the portal; divergence alerts (`05-03` §3.4) |

> **DI-03 is the requirement most likely to be missed by a consumer team.** An integration that caches
> `party_id = 4471` and never re-resolves will silently point at a merged-away record.

---

## 9. The `M64` Timing Gap

> `DM-011` §2.9 records it precisely: **`M64` is a W2 module; tiers `X1`–`X5` load at W1.** The gate
> that scores every migration batch arrives one wave after the batches.

**This document extends the same problem to steady state**, because MDM machinery is needed before
`M64` exists:

| Capability | Needed from | `M64` delivers |
|---|---|---|
| Party create-time deterministic matching | **W1** — M33 goes live in W1 | W2 |
| Golden-record survivorship | **W1** | W2 |
| Stewardship queue | **W1** | W2 |
| Hierarchy management | W1 (corporate accounts in M07) | W2 |
| Full match/merge with fuzzy scoring | W2 | W2 |

### 9.1 The interim design

| # | Rule |
|---|---|
| **IM-01** | **W1 M33 implements pass-1 deterministic matching and blocking on exact duplicates**, inside `cd_party_master` (CD-145…148). This is a small, bounded capability, not an MDM platform |
| **IM-02** | The W1 stewardship queue is a **task list in M33**, using the same states and the same rule identifiers `M64` will use, so the work is comparable and transferable (`DQ-26`'s principle) |
| **IM-03** | Fuzzy matching (pass 3) **does not exist in W1**. Candidates accumulate and are evaluated when `M64` arrives — recorded as a **known, bounded gap**, not a silent one |
| **IM-04** | **`M64` re-scores the W1 population when it arrives.** An interim gate producing no comparable evidence is not a gate (`DQ-26`) |
| **IM-05** | The W1 interim is registered in **`GV-005` RAID with an expiry at the W2 gate** (`AR-006` D-A6-04) |

> **This is `AR-006`'s stub-the-seam pattern (ADR-023) applied to data rather than to an interface.**
> Build the deterministic half early where it is cheap; connect the rest when the module lands; and
> **register the gap with an expiry** so it cannot quietly persist.

---

## 10. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is the W1 interim (§9.1) accepted as M33 scope?** Without it, W1 has no duplicate prevention on the party kernel | Steering / `GV-004` | **W0 — blocking** | M33 W1 scope |
| **Q-02** | **Is the stewardship queue resourced for steady state?** `DQ-16` sizes the migration queue in thousands of decisions; production adds a continuous rate | Domain owners / Programme Manager | W1 | `SW-01`; `DA-003` `GM-06` |
| **Q-03** | Is the **90-day unmerge window** (UM-01) accepted? It bounds retained state and the reversibility promise | CDO / MDM Lead | W2 | `M64` design |
| **Q-04** | Does a customer-visible merge require notification copy? No `UI-*` pack currently covers it | Content Lead | W2 | §5.3 |
| **Q-05** | **Marketplace seller score on merge** — escalate to Council, or a rule? (§4.5) | CCO / Council | W7 | M12 |
| **Q-06** | Does `DM-011`'s auto-merge threshold of 0.95 hold for production, where a wrong merge is not correctable pre-go-live? | CDO / MDM Lead | W2 | §4.3 |

---

## 11. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-D4-01 | MDM style | Registry; consolidation; **centralised/coexistence** | **Centralised** | The ERP is the system of record; a golden record nobody transacts against is a report | No separate MDM copy |
| D-D4-02 | Golden record construction | Winning row; **attribute by attribute** | **Attribute (GR-02)** | `DQ-17` already established it for migration; production must match so behaviour is comparable | Per-attribute survivorship |
| D-D4-03 | Merge loser | Delete; **retain `active = False`** | **Retain** | Four independent reasons (§3.3), any one sufficient | `golden_record_id` on every master entity |
| D-D4-04 | Production merge blockers | None beyond `DM-011`; **six additional** | **Six (§4.4)** | Live transactions, balances and consent do not exist at migration time | More steward work, fewer incidents |
| D-D4-05 | Thresholds | Re-derive for production; **carry `DM-011`'s unchanged** | **Carry** | Pre- and post-go-live quality must be comparable (`DQ-26` principle) | Q-06 tests the assumption |
| D-D4-06 | Balances on merge | Sum; **never — escalate** | **Never** | `DQ-17`: two balances are two facts | MB-01; FN-02 explicit transfer |
| D-D4-07 | Loyalty points on merge | Highest; **sum with a ledger entry** | **Sum** | The customer can see the balance; silently losing it is indefensible | Ledger entry required |
| D-D4-08 | Unmerge | Permanent; **90-day window** | **90 days** | Reversibility is required (`DQ-20`) and is physically bounded by transactions against the survivor | Beyond it, a split |
| D-D4-09 | Distribution | Batch export; **event** | **Event (DI-01)** | A nightly CSV is a second copy that diverges | `party.merged` is first-class |

---

## 12. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Master, reference and transactional data are distinguished by a stated test | §2.1, §2.2 |
| AC-02 | The golden-record style is chosen with rejected options analysed | §3.1 |
| AC-03 | **The register's question is answered** — what happens to the loser's history, balances, consent and identity | §5 |
| AC-04 | Production-only merge blockers are enumerated | §4.4 — six |
| AC-05 | Survivorship extends `DM-011` with the production-only attribute classes | §4.5 — four additions |
| AC-06 | Hierarchies have acyclicity, bounded depth and declared inheritance | §6.2 |
| AC-07 | Unmerge has a stated window and a stated reason for the bound | §7 |
| AC-08 | Distribution is event-based with a re-pointing tolerance requirement | §8.2 |
| AC-09 | The `M64` timing gap has an interim design with a registered expiry | §9.1 |
| AC-10 | The personal-data consequence of a wrong merge is stated as an incident, not a defect | §5.6 |

**Definition of done.** Complete when every criterion is met, Q-01 and Q-02 are resolved, and
`PGD-000`'s `DA-004` row is updated.

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-008` | The party kernel and its invariants (I-10) |
| Upstream | `DA-001` §4.5, §6.2 | Keys; `RESTRICT` is why the loser cannot be deleted |
| Upstream | `DA-003` | Domain owners and stewards |
| Upstream | `DM-011` §2.5–§2.9 | Matching, thresholds, survivorship — carried forward |
| Downstream | **`M64`** | This is the module's design brief |
| Downstream | `M33` | §9.1 W1 interim |
| Downstream | `AR-009` | `party.merged` as a first-class event |
| Downstream | `DA-007` | Type-2 SCD handling of merges |
| Downstream | `DA-008` | Duplicate rate is D1's dominant quality dimension (40% weight) |
| Downstream | `SC-011` | A wrong merge is assessed as a potential breach |
| Lateral | The 48 `MD-*` files | Content authority, retained |

---

## 14. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md` ·
`./DA-003_Data_Governance_Framework_and_Stewardship_Model.md` ·
`./DA-007_Analytical_and_Dimensional_Model_Specification.md` ·
`./DA-008_Data_Quality_Management_Plan.md` · `./DA-009_Reference_Data_and_Code_List_Register.md` ·
`../02_Architecture_and_Design/AR-008_Domain_Model_and_Bounded_Context_Map.md`

**Workspace**
`../../project_content/12_Data_Migration_Content/DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md` §2.5–§2.9 ·
`../../project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-001_Master_Data_Governance_Charter.md` ·
`../../project_content/02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md` ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M64_Master_Data_Management_and_Configuration.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md` §3.4, §4.2

**External standards**

| Source | Version | Verified |
|---|---|---|
| [DAMA-DMBOK](https://www.damadmbok.org/) — Reference & Master Data knowledge area | 2.0 (2024 maintenance revision) | 2026-08-18 |
| [ISO/IEC 11179-1:2023](https://www.iso.org/standard/78914.html) | Edition 4 | 2026-08-18 |
| [Bangladesh PDPA 2026](https://securiti.ai/bangladesh-personal-data-protection-act-overview/) | Enforcement ~13 May 2027 | 2026-08-18 |

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Answers the register's question — what happens to the merge loser's history, balances, consent and identity. Adds **six production-only merge blockers** and four survivorship classes `DM-011` does not face. Extends the `M64` W1/W2 timing gap to steady state with a registered interim | *Pending — CDO, unappointed* |

---

*`DA-004` · Category 03 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
