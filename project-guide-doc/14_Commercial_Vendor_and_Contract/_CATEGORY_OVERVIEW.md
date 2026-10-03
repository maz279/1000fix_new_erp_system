---
id: PGD-CAT-14
category: 14 — Commercial, Vendor & Contract
code: CO
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-19
status: DRAFT FOR APPROVAL — ALL FIVE OUTSTANDING DOCUMENTS AUTHORED
owner: CFO / Head of Procurement
enumeration_timestamp: 2026-08-19 03:02 (+06)
audit: ../_AUDIT/PGD-AUDIT-CAT-14_Category_14_Commercial_Vendor_and_Contract_Audit.md
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# Category 14 — Commercial, Vendor & Contract (`CO`)

> **✅ All five outstanding documents authored and issued 2026-08-19**, and audited the same day in
> [`PGD-AUDIT-CAT-14`](../_AUDIT/PGD-AUDIT-CAT-14_Category_14_Commercial_Vendor_and_Contract_Audit.md).
> **4,850 lines · 396 KB · 230 governing rules across six prefixes · 47 open questions · 39 recorded
> decisions · 22 findings raised (`CVA-01`…`CVA-22`).**
>
> The audit ran as **eleven filesystem extractions** and **seventeen machine re-summed tables**,
> and found **ten further defects (`CVA-23`…`CVA-32`) — nine of them in this category's own
> authoring. Nine were corrected before issue; one is referred to `SV-005`.** Three would each
> have survived a careful reading: a duplicate rule, a roll-up drifted from its own table, and
> **eight cross-references that resolved correctly but pointed at the wrong rules**.
>
> The ✅ is **qualified**, on the same basis as Categories 09 and 13. Tests (a), (b) and (c) of
> `PGD-000` §0.3 are met and verified; test (d)'s **approval record** does not exist and cannot,
> until `GV-001` `CC-01` constitutes a body that can create one (`PGD-A2-25`).

## Purpose

The RFP is written, strong and **issued**. What follows it is a **selection decision, a contract, a
deliverable acceptance schedule, a cost baseline and a licence position**. These are the documents
that make the technical estate *enforceable against a supplier* rather than merely descriptive.

## Documents

| ID | Document | Prefix | Rules | Lines | Status | Pri | Needed by |
|---|---|---|---:|---:|:--:|:--:|:--:|
| `CO-001` | Request for Proposal | — | — | — | ✅ [`RFP`](../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md) | **P0** | Issued |
| [`CO-002`](CO-002_Vendor_Evaluation_and_Selection_Report.md) | Vendor Evaluation & Selection Report | `VES-nn` | 40 | 965 | ✅ † ‡ | P1 | W1 |
| [`CO-003`](CO-003_Statement_of_Work_and_Deliverable_Acceptance_Schedule.md) | Statement of Work & Deliverable Acceptance Schedule | `SOW-nn` · `PDoD-nn` | 74 + 7 | 906 | ✅ † | **P0** | W1 |
| [`CO-004`](CO-004_Licence_and_Open_Source_Compliance_Register.md) | Licence & Open-Source Compliance Register | `LIC-nn` | 45 | 791 | ✅ † | P1 | W1 |
| [`CO-005`](CO-005_Total_Cost_of_Ownership_Model.md) | **Total Cost of Ownership Model** | `TCO-nn` | 15 | 1,488 | ✅ † | **P0** | **Now** |
| [`CO-006`](CO-006_Procurement_and_Purchase_Plan.md) | Procurement & Purchase Plan | `PPP-nn` | 49 | 700 | ✅ † | P2 | W1 |
| | **Total** | **6 prefixes** | **230** | **4,850** | | | |

**Verification** *(regenerated from the rows per `PG-M10`)*: rules 40 + 74 + 7 + 45 + 15 + 49 =
**230** ✓ · lines 965 + 906 + 791 + 1,488 + 700 = **4,850** ✓.

† The ✅ is qualified — no approval record can exist until `CC-01` constitutes an approving body.
‡ `CO-002` is issued as **Part A only** — the evaluation *instrument*, deliberately containing no
scores. Part B, the record and the award recommendation, completes at v2.0 by 3 March 2027
(`CO-002-D-01`).

## The single most urgent item in this category

**`CVA-02` — Critical, and time-limited to 17 September 2026.**

| Date | Event |
|---|---|
| **13 Aug 2026** | RFP v2.0 issued. §16.1 publishes a **$690K–$1,150K** envelope; §17.2 criterion 7 requires *"an independent capacity analysis against **1,513 PW**"* |
| **18 Aug 2026** | `GV-007` supersedes 1,513 PW with **1,842 PW build / 3,022 PW programme** |
| **19 Aug 2026** | `GV-008` supersedes the envelope with **$1,024K–$2,608K**; `CO-005` restates it again at **$1,488K–$4,330K** |
| **17 Sept 2026** | ⚠ **Written-question deadline — the last date the RFP's own machinery can carry a correction** |
| 30 Oct 2026 | Proposal submission deadline |

**Both** mechanisms an evaluation has for detecting an under-scoped bid — criterion 7's capacity
benchmark and §16.1's envelope test — are keyed to the superseded figure (`CVA-09`). As published,
the instrument **rewards the optimistic bidder and penalises the accurate one**, and criterion 7
carries a sub-50 elimination floor. `CO-005` §9.4 and `CO-002` §5.4 specify **RFP Addendum 1**.

## The cost problem, restated

| Figure the Board holds | Position now |
|---|---|
| 834 person-weeks build effort | **3,022 PW** across four work streams (`GV-007` §7.1) |
| $290K–$470K implementation cost | People cost **$859K / $1,358K / $2,228K** (`GV-008` §4.2) |
| **$455K–$780K three-year TCO** | **$1,488K – $4,330K, expected $2,558K** — Tier 1, incremental cash (`CO-005` §7.1). **4.1× the midpoint** |
| *(no five-year figure existed)* | **$1,912K – $5,367K, expected $3,249K** — Tier 1, five years |
| *(no economic figure existed)* | **$2,311K – $6,568K, expected $3,977K** — Tier 2, including the internal draw |
| Content production effort | 520–775 PW, costed at **$114K–$310K** (`GV-008` §4.2) |
| *(never counted)* | **A steady-state run rate of $207K–$531K a year**, expected **$337K** — the figure that persists after the programme ends |

`00-06` `H-02` instructed: **"Do not present the current TCO to the Board as final."** `CO-005` is
the document that replaces it, and it discharges the two deferrals `GV-008` left behind —
`GV-008-D-03` (re-derive the non-people lines) and `GV-008` `Q-03` (what `BD-R` costs).

## The 22 findings

| Range | Raised in | Theme |
|---|---|---|
| `CVA-01` | `CO-005` | The **`CO-nn` rule-prefix collision** — 108 occurrences across 30 files and 3 repositories |
| **`CVA-02`** | `CO-005` | **Critical.** The live RFP carries a superseded envelope and effort basis |
| `CVA-03` – `CVA-06` | `CO-005` | No tax line anywhere · FX 11.5% adrift · the `dr` double-count in `PE-002` §9.1 · hypercare duration |
| `CVA-07` – `CVA-09` | `CO-002` | `MQ-06` calibrated to a superseded scope · disciplines priced but unstaffed · **both bid-realism safeguards broken by one stale figure** |
| `CVA-10` – `CVA-14` | `CO-003` | Retention ambiguity · **the conditional-pass funding conflict** · the warranty tail past closure · `DoD-17` has no recurrence rule · **the twelve portals have no Definition of Done** |
| `CVA-15` – `CVA-18` | `CO-004` | **OCA is AGPL-3, not LGPL-3** · **Redis 7.x spans two licence regimes** · no outbound licence position · two review cadences |
| `CVA-19` – `CVA-22` | `CO-006` | **The device estate is unowned** · the hub count is stated nowhere · two L6 review cadences · no sustainable-procurement position |

**Three are High or Critical and act on a deadline**: `CVA-02` (17 September 2026), `CVA-11` (before
contract signature), and `CVA-06` as re-graded — RFP §14.1 prices **36** hypercare weeks where
`SV-005` requires **56**.

## What each document changed

| Document | The thing it settled that nothing else could |
|---|---|
| **`CO-002`** | An evaluation instrument **frozen before the bids open**. `CO-002-D-01` explains why a document issued eleven weeks early and containing no scores is worth more than one written afterwards: *the date it was frozen is the primary evidence in a challenge* |
| **`CO-003`** | That the register's 140 documents are **not 140 authorship deliverables** — 131 already exist, so the obligation is conform-and-maintain. **Seven were genuinely the supplier's to author; one was discharged during the audit window** |
| **`CO-004`** | **Five licence positions independently verified; three found to differ.** The OCA layer is AGPL-3, and its network-service obligation is discharged by RFP §19.1(4)'s upstream-contribution clause — which the estate had recorded as community goodwill rather than as a legal discharge |
| **`CO-005`** | The re-derivation `GV-008` deferred, a five-year horizon the RFP demands and the Company never computed, and the **twelve cost lines no document carried** — tax, FX, escalation, hypercare, PMO, `BD-R`, eleven environments, the internal draw |
| **`CO-006`** | A purchase route for `02-05` §6's CFO-approval control, and an owner for the **215–430 technician devices** that mitigate a Critical risk and had been assigned to a document that did not exist |

## Licence obligations now have owners

| Licence | Components | Obligation owner |
|---|---|---|
| **AGPL-3** | Metabase, Grafana, MinIO, RustDesk, **Loki, Tempo, and the OCA module layer** | Chief Architect · Platform Engineering |
| **LGPL-3** | Odoo 19 CE **only** — *not* OCA | Chief Architect |
| **Sustainable Use** | n8n — internal only; **the breach is a product decision, not a commit** | **CFO with Chief Architect** |
| **BSL / TSL** | Redpanda · TimescaleDB | Chief Architect |
| **RSALv2 / SSPL** | **Redis 7.4–7.8 — a licence class in no policy list** | Chief Architect |
| **GPL-2** | Wazuh, on client endpoints under `M05` | **Legal Counsel** |
| **Outbound** | What 1000FiX grants five external populations | **Legal Counsel** — `CVA-17` |

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `00_Governance` | `GV-007` supplies effort; `GV-008` names `CO-005` as its successor and poses `Q-03` |
| Upstream | `10_Infrastructure` | `PE-001`, `PE-002`, `PE-006`, `PE-007` supply the drivers `CO-005` §5 prices; `PE-006-F-07` and `PE-002-F-04` refer their numbers here |
| Upstream | `11_Service_Operations` | **`SV-005`, issued the same day, superseded `CO-005`'s own hypercare estimate** and was adopted at audit under `TCO-02` |
| Upstream | `13_Training` | `CH-002` §7.1 assigns learner devices to `CO-006` and learner time to `CO-005` |
| Downstream | **All** | `CO-003` §5 is what makes every other category's documents contractually owed |
| Downstream | `15_Benefits` | `BM-003` inherits the verified FX rate and the restated payback; `PGD-A2-10` remains its own |
| Peer | `02_Architecture`, `07_Build` | `AR-013` and `BE-007` own the radar and the machine check; `CO-004` owns the accountable register |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Board, CFO, procurement, legal, PMO, Steering Committee, supplier |
| Change frequency | **Low** — except `CO-004`, which `LIC-35` makes a standing register reviewed at **every wave gate**, and `CO-005`, re-baselined at every gate under `TCO-11` |
| Standards basis | ISO 15686-5:2017 · AACE 17R-97 · ISO 37500:2014 · ISO 44001:2017 · ISO 9001:2015 §8.4 · ISO/IEC/IEEE 12207:2017 · ISO/IEC 5230:2020 · ISO/IEC 19770-1/-3 · ISO 20400:2017 · SPDX 3.0.1 · CycloneDX 1.7 |

---

*Category 14 · `CO` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
