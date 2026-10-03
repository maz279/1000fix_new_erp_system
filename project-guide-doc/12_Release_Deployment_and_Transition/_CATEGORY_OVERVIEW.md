---
id: PGD-CAT-12
category: 12 — Release, Deployment & Transition
code: RL
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
owner: Release Manager / PMO
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# Category 12 — Release, Deployment & Transition (`RL`)

## Purpose

**Nine waves. 51+ branches. 250,000+ customers a month. And — counted at issue, not quoted —
32 legacy sources that must be switched off, 4 retained by design, 1 purged and 11 that are not
systems at all** (`RL-006` §3).

`06-06_Deployment_and_Operations_Plan.md` was planned in `FOLDER_STRUCTURE.md` and never written.
This category holds the documents that turn a built system into a live one, nine times, without
the business stopping.

## Documents

> ### ✅ Authored 2026-08-19 · audited [`PGD-AUDIT-CAT-12`](../_AUDIT/PGD-AUDIT-CAT-12_Category_12_Release_Deployment_and_Transition_Audit.md) · 24 findings, 9 closed
>
> Six documents, **272 governing rules**, in six verified-unused rule spaces. The category code
> `RL` is deliberately **not** a rule prefix — `RL-01`…`RL-12` is already `TR-024`'s space, used 36
> times. Read the ✅ narrowly: the audit's seventh test finds the category **specified and not
> executable**, blocked by five appointments, one dataset, sixteen translations, one baseline
> report and two registers — every one named, owned and dated.

| ID | Document | Rule space | Rules | Status | Pri | Needed by |
|---|---|:--:|---:|:--:|:--:|:--:|
| `RL-001` | [Release Management & Versioning Policy](RL-001_Release_Management_and_Versioning_Policy.md) | `RMP` | 47 | ✅ | P1 | W1 |
| `RL-002` | [Deployment Plan & Go-Live Checklist](RL-002_Deployment_Plan_and_Go_Live_Checklist.md) | `DPY` | 49 | ✅ | **P0** | W1 |
| `RL-003` | [Go-Live Readiness Assessment & Gate Criteria](RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) | `GLR` | 31 | ✅ | **P0** | W1 |
| `RL-004` | [Rollout & Branch Wave Deployment Plan](RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) | `RLO` | 43 | ✅ | **P0** | W2 |
| `RL-005` | [Post-Implementation Review Standard](RL-005_Post_Implementation_Review_Standard.md) | `PIR` | 45 | ✅ | P2 | W2 |
| `RL-006` | [Legacy Decommissioning Plan](RL-006_Legacy_Decommissioning_Plan.md) | `DCM` | 57 | ✅ | P1 | W3 |
| | **Total** | | **272** | **6 ✅** | | |

## What the category found

Five things no document in the estate previously stated:

| # | Finding | Where |
|:--:|---|---|
| 1 | **The rollout rate is 2–3 sites per week, and it is bounded by floor-walkers** — not by technology, training or migration. Derived from `05-04` §5's counted branch-resident population (538 – ≥873) and `OP-002` §4.4's ratios. With `HD-03`'s clock, **W2's rollout outlasts W2** | `RL-004` §7; audit `RLA-07` **CRITICAL** |
| 2 | **Sixteen files declare a Bengali counterpart; none exists.** Including the branch readiness checklist and the manual fallback pack. The rollout cannot begin | `RL-004` §12; audit `RLA-18` **CRITICAL** |
| 3 | **Of `DM-002`'s 48 legacy sources, 32 are retirable, 4 are retained by design, 1 is purge-only and 11 are not systems.** `GV-001` §12.1's *"all 48 decommissioned"* cannot be met as written | `RL-006` §3, §4; audit `RLA-10` |
| 4 | **No wave review may claim any benefit until `BM-002` issues** — and a baseline cannot be captured retrospectively, so every month it slips forecloses a wave's claim permanently | `RL-005` §7.3; audit `RLA-09` **HIGH** |
| 5 | **Three of seven readiness dimensions have no appointed assessor.** Read literally, Wave 1 cannot go live | `RL-003` §11; audit §8 |

## Seams closed

| Interface | Raised by | Closed by |
|---|---|---|
| `CUT-01` — *"the application must be deployed, smoke-tested and stable before the freeze instant"*, with no date | `MG-006` `Q-01` | `RL-001` `RMP-25`/`RMP-26` — **T−15 and T−25 working days**, derived from `DM-014`'s phase model |
| `RBK-16` — *"must not retire a source until … a declared stabilisation period has passed"*, with no period | `MG-007` `Q-04` | `RL-006` `DCM-13` — the later of hypercare exit and gate, **plus one further full business cycle**, floor 30 days |
| *"CAB membership, cadence and quorum defined — outstanding"* | `SP-031` Definition of Done | `RL-001` §8.2 — a named body, asynchronous by default, convened for High risk |
| `SP-031` requires a CAB; `M66` §4 rejects one | Both current, contradictory | `RL-001` `RL-001-D-01` — the word doing the damage is *"meeting"* |

## Gate criteria are not readiness assessment

`06-02` §4 lists wave-gate acceptance criteria. That is necessary and not sufficient. What is
missing is the **assessment instrument**: who checks, against what evidence, with what authority
to stop a go-live.

| Readiness dimension | Evidence source | Assessor |
|---|---|---|
| Functional | `QA-011` coverage report, `QA-009` UAT sign-off | Business owner |
| Technical | `PE-002` environment verification, `QA-006` performance results | Platform lead |
| Data | `MG-004` reconciliation evidence | Finance controller + Migration lead |
| Operational | `SV-004` on-call live, `SV-003` runbooks tested | Service manager |
| People | `CH-002` training completion, `CH-004` adoption readiness | Change lead |
| Security | `SC-009` pen-test remediation, `SC-003` DPIA sign-off | CISO / DPO |
| Commercial | `CO-003` deliverable acceptance | PMO |

**All seven are now named in `RL-003` §4.2, each with a veto and a stated veto scope.** Three of the
seven — `RD-4` Security, `RD-5` Operational and `RD-7` Commercial — have **no appointed post-holder**
(`GLR-26`), and `RL-003` §11.3 supplies dated interims rather than pretending otherwise.

## Rollout is a site problem, not a programme problem

`06-01` §6 describes a rollout approach at programme altitude. `CM-012` provides a branch
readiness *communication checklist*. Neither answers the operational questions:

- Which of the 51+ branches is the pilot, and on what selection criteria?
- What is the per-site readiness bar — hardware, connectivity, trained staff, stock counted?
- Who is on site, for how long, and what is the fallback if a branch fails its bar?
- What is the sequence across 8 administrative divisions, and what is the pause rule?

`RL-004` answers them. Without it, 51 branches will be sequenced by convenience.

## Decommissioning is a compliance obligation, not tidy-up

The RFP §4.3 commits contractually to retiring **21 legacy practices**. `DM-002` names **48 sources**,
of which **32 are retirable**. `RL-006` §4 reconciles the two and finds **nine sources with no
contractual accountability and one contractual commitment with no source behind it**.

Systems that are never formally switched off keep costing licence and hosting money, keep holding
**personal data outside the retention schedule** (`LG-009`, `DA-006`), and keep offering an
un-patched attack surface. Under PDPA 2026 the second of those is a live exposure, not an
inefficiency.

## What "done" looks like for this category

1. ✅ A deployment plan exists **per wave** — `RL-002` §12 — with a 59-item go-live checklist, 19
   standing smoke cases and eight mechanical abort triggers.
2. ✅ `RL-003` gives seven assessors a documented veto against 39 enumerated evidence items — and
   refuses to average them into a single readiness score (`GLR-15`).
3. ◐ `RL-004` states the sequence, the rate and seven pause triggers. **It cannot state dates**
   until `MD-003` is populated — the branch master is still class `P3`.
4. ✅ `RL-005` measures estimate accuracy every wave at three levels, each naming its denominator.
   The register's *"834-vs-1,513"* framing is corrected: `GV-007` records **four** figures —
   834 / 1,513 / 1,842 / 3,022 PW — with a widest ratio of **4.7×**.
5. ✅ Every source has a disposition, a retirement state, an archive decision and a proof standard —
   and every proof is a **negative test**, an attempt that fails (`DCM-44`).

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `08_Quality` | `RL-003` consumes `QA-011` coverage and `QA-009` sign-off |
| Upstream | `09_Migration` | `RL-002` sequences around `MG-006` cutover |
| Upstream | `11_Operations` | `RL-003` requires `SV-004` to exist, not be documented |
| Upstream | `13_Change` | `RL-004` per-site bar includes `CH-002` training completion |
| Downstream | `15_Benefits` | `RL-005` feeds `BM-004` benefits realisation and `BM-005` lessons |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Release manager, PMO, branch managers, service manager, business owners |
| Change frequency | **High during rollout — one instance per wave** |
| Standards basis | ITIL 4 release & deployment management · PRINCE2 stage boundaries · DORA deployment practice |

## Existing material to build from

`1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` §6 and §8, `06-02` §4 ·
`project_content/17_Operations_Support_and_Runbooks/OP-006` (release notes standard) ·
`project_content/16_Change_Management_and_Comms/CM-006`, `CM-012` ·
`project_content/12_Data_Migration_Content/DM-002` (legacy source inventory), `DM-014` ·
`primary-doc/…RFP.md` §4 (legacy decommissioning commitment), §12 (9-wave approach)

---

*Category 12 · `RL` · 6 documents · 272 rules · audited `PGD-AUDIT-CAT-12` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
