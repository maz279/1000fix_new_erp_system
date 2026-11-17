# M64 Master Data Management: Sub-Module Capture Audit (2026-11-18)

**Trigger.** The user observed that not every M64 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M64_Master_Data_Management_and_Configuration.md`. Sections used:
  - §3: scope (24 capabilities) and boundaries (M33/M37 own content, M63 executes parameters, M30 owns technical configuration);
  - §5: FR-MDM-001 … 034, in five areas (domain register and stewardship, change control, data quality, matching / golden record / hierarchies, reference data and business parameters);
  - §8: the change-request, duplicate and reference-value lifecycles;
  - §9: BRU-MDM-01 … 22;
  - §10.1: the 22 owned entities;
  - §13: roles and segregation of duties.
- Code:
  - `cd_p03_portal/static/src/a12/m64.js`: the page registry (6 sub-module pages);
  - `cd_p03_portal/controllers/a12/m64.py`: surfaces, writable fields, reports and KPIs;
  - `cd_mdm_core/models/*.py`: change request, steward request approval, domain stewardship, golden and match rules, governed attributes;
  - `cd_entity_config/models/fix_platform_ops*.py`: steward request, DQ rule, code list and entry, duplicate candidate, cross-reference.
- Live data (fix_real, read-only count on 18 Nov): 0 data domains, 0 steward requests, 0 change requests, 4 DQ rules, 2 code lists with 7 entries, 0 cross-references, 1 golden rule, 2 match rules, 18 governed attributes, 361 duplicate candidates, and **no active user holds the MDM Domain Steward group**.

## 1. What was there (HEAD 00326139)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Stewardship | Steward Request | Steward Request | The page lists the **domain register** (`fix.mdm.stewardship`) with no chip, so no data domain could be set up from it. The register held one steward and an owner only: **no deputy** to take the work on absence (FR-MDM-004 P0), **no technical custodian or criticality** (FR-MDM-001 P0). |
| 2 | Data Quality | DQ Rule | DQ Rule | The evaluator **counted** failures per rule, and nothing else: **no remediation worklist** existed (FR-MDM-021 P0, FR-MDM-005 steward console). A steward could not take on a failing record, assign it, or close it, and nothing checked that a "fixed" record now passes. |
| 3 | Code Lists | Code List | Code List Entry | The page lists **cross-references** with no chip (FR-MDM-032 P0): a mapping could not be captured from the page. |
| 4 | Golden Records | Golden Record Rule | **none** | **No chip at all.** Match rules and governed attributes were listed and uncapturable from the page. **No governed hierarchy** existed anywhere (FR-MDM-028 P1, FR-MDM-029 P0, BRU-MDM-18 H). |
| 5 | Workflows | Change Request (module button) | Change Request | Single change requests only. **No bulk change set** (FR-MDM-013 P0, BRU-MDM-08 H "reviewed and approved as a set and applied all-or-nothing"): a mass update had to be raised as N unrelated requests, each decided and applied on its own. |
| 6 | Audit | Duplicate Candidate | none | None: a steward raises a suspected pair here (spec §8.2 "steward-initiated"); merges route to M33. |
| — | (no page) | — | — | **No business parameter registry anywhere** (FR-MDM-033 P0, BRU-MDM-15/16/17 H): the thresholds, ceilings and periods M63 is meant to execute had no governed home, no owner approval, no version and no effective date. |

Guard `cd_p03_portal/tests/test_m64_capture_buttons.py` on HEAD: **13 of 19 tests fail**: pages 1, 2, 3, 4, 5 and 7, registers listed with no capture on their page, the missing models, the child grids, the deputy, and the worklist button.

## 2. What was built

### Backend: `cd_mdm_core` 19.0.1.3.0, new file `models/fix_mdm_capture.py`

- **`fix.mdm.dq.remediation`** (FR-MDM-021, FR-MDM-005): one failing record of one rule, with priority, business impact, assigned steward and due date.
  - **Raise Remediation Worklist** on the DQ rule list raises one item per failing record (one open item per rule and record, at most 200 per run; severity sets the priority). Stewards only.
  - **Resolve** re-checks the rule against that one record and refuses while it still fails.
  - **Waive** needs a reason and a steward who neither wrote the rule nor raised the item (spec §13 "the person who defines a quality rule cannot be the sole approver of an exception to it").
  - The assignee must hold the steward group. State, resolution and stamps change only through the actions.
- **`fix.mdm.business.parameter`** + **`fix.mdm.parameter.change`** (FR-MDM-033, BRU-MDM-15/16/17):
  - a parameter has a dotted key unique per company, a business area, a type (whole number, decimal, amount, percentage, days, yes/no, text), bounds, a business owner and a "read by" note naming the M63 rules that execute it;
  - its value is checked against type and bounds; the **owner, or a steward other than the drafter, activates it**; after that its key, type, bounds and value are frozen;
  - a value changes only through a **Parameter Change**: a new value, an effective date that is not in the past, and a reason. Submit checks the value and records the one it replaces. The change is **routed to the parameter's owner**, or to a steward when the owner proposed it; the proposer never decides it. The approval publishes it;
  - `value_at(key, date)` answers the value in force on any date (documents dated before the effective date keep the old value), and **Value in Force** shows today's.
  - M64 stores the number and executes nothing (BRU-MDM-15).
- **`fix.mdm.hierarchy`** + **`fix.mdm.hierarchy.node`** (FR-MDM-028/029, BRU-MDM-18):
  - a classification, spend-category, cost-centre roll-up or segmentation tree, keyed in one form; each node names its parent by code;
  - the save is refused for an **orphan**, a **cycle**, a **repeated code** or a node **deeper than the hierarchy's deepest level**; level and parent are computed;
  - a **second steward publishes** (not the builder); a published tree is frozen; **New Version** makes the next draft, and publishing it retires the version it replaces.
- **`fix.mdm.change.batch`** + **`fix.mdm.change.batch.line`** (FR-MDM-013, BRU-MDM-08):
  - one target model, a justification, and one row per record with its proposed values;
  - **Submit** runs every check a single change request runs (governed-attribute register, routing hook, critical DQ gate, a dry-run write) on every row, refuses a record named twice, records each row's current values and a preview, and freezes the set;
  - routed through M63 to a domain steward who did not raise it;
  - **Apply writes every row or none**: a record that changed after submit stops the whole set.
- **Domain register** (`fix.mdm.stewardship`, FR-MDM-001/004): **deputy steward** (must hold the steward group and differ from the lead), **technical custodian** and **criticality**. Appointing the deputy and custodian is a Platform Admin's decision, like the lead.
- Security: access rows (read for everyone, maintenance for stewards, proposals for every internal user), own-or-steward edit rules for parameter changes and bulk sets, company isolation for every new register.

### Workspace: `m64.js`, `controllers/a12/m64.py`

| Page | "+ New" | Chips after |
|---|---|---|
| 1 Stewardship | Steward Request | Steward Request, **Data Domain** (deputy, custodian, criticality) |
| 2 Data Quality | DQ Rule | DQ Rule, **DQ Remediation**; the rule list gained **Raise Remediation Worklist**; new **Remediation Worklist** list with Start / Resolve / Waive |
| 3 Code Lists | Code List | Code List Entry, **Cross-Reference** |
| 4 Golden Records | Golden Record Rule | **Match Rule, Governed Attribute, Governed Hierarchy**; new **Governed Hierarchies** list with Publish / New Version |
| 5 Workflows | Change Request | Change Request, **Bulk Change Set**; new **Bulk Change Sets** list with Submit / Route / Recall / Cancel / Apply |
| 6 Audit | Duplicate Candidate | unchanged |
| **7 Business Parameters (new)** | **Business Parameter** | **Business Parameter, Parameter Change**; report chip **Business Parameter Register** |

Every new surface declares its buttons and the fields its form may write; no state, decision stamp or measured value is writable. Two KPIs added: Open Remediations, Active Parameters.

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m64_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry; it also checks every page's captures, that every listed register has a capture on its page, every list button against the served surface, every form field against the writable list, and that no state, stamp or measured value can be typed. | **HEAD 00326139: 13 of 19 fail** (pages 1, 2, 3, 4, 5 and 7, listed registers with no capture, the missing models, grids, deputy, worklist button). After: **19/19.** |
| Estate page standard `test_estate_module_pages.py` (all 67 modules) and the A12 write whitelist. | **All pass** (the first run caught that the Business Parameter form chip was on no page; fixed). |
| Live tests `cd_mdm_core/tests/test_m64_capture.py`, run as freshly created non-admin users (three stewards, a clerk, a business owner, a Platform Admin) on a private clone `fix_test_m64` (`-u all`, exit 0, no error). Parameter changes and bulk sets are decided through the real M63 inbox. | **19/19.** The first run caught a real defect, fixed before this result: a parameter's business owner (not a steward) could not activate or retire it, because the transition wrote under the owner's own access rights. |
| Mutation check: each rule removed in turn (resolve re-check, waiver segregation, worklist stewards only, steward assignee, one open item per record, percentage bounds, drafter cannot activate, active value frozen, change routed to the owner, no backdated change, history by effective date, orphan, depth, builder cannot publish, published nodes frozen, bulk freshness, bulk repeated record, bulk rows frozen after submit, bulk submitter cannot decide, deputy must be a steward; page 4 chips, page 7, worklist button). | **23 of 23 mutations turned the tests red**; the source was restored byte for byte. The first run left one survivor (bulk submitter): the M63 engine already refuses the requester and creator, so a test was added for a submitter who is neither. |
| Regression on the same clone: every `cd_mdm_core`, `cd_entity_config`, `cd_party_master` and `cd_workflow_engine` test, the A12 DOFA coverage, write whitelist and M30/M65 suites, the estate guard, the M33 and M64 guards. | **1,384 tests: 1,380 passed, 2 skipped, 2 failed.** The two failures (`test_a03_w_merge_kyc_draft` "an invoice" cases) **fail identically with the HEAD 00326139 code on the same database**: the commercial-document BIN check now fires before the KYC check the test expects; not touched here. Two existing M64 tests needed updating for the new grids (a third "Proposed Changes" label; grid fields checked against the child model). |
| Isolation-rule drift check (`generate-isolation-rules.py --check`). | `cd_mdm_core` clean (hand-written company rules); the 7 modules it lists are other work. |
| Workspace UI on a private server (port 8096) over the clone, signed in as admin. | All 7 sub-module pages render with the "+ New" and chips in the table above. A **Governed Hierarchy was saved from the form** with two node rows; the server computed PARTS at level 1 and SCREENS at level 2 under it. Before admin held the steward group the save was refused with the access message (correct). A server probe of every M64 screen (lists, forms, reports): **40/40 served without error.** |

## 4. Not built here (owner decisions or other modules)

- **No one can steward on fix_real yet**: no active user holds the MDM Domain Steward group, and no data domain exists. Every steward decision (change requests, bulk sets, remediation, hierarchy publication, code-list publication) has nobody to route to until the owners name stewards per domain (spec §13 grants: R17 parts, R19 suppliers, R26 finance, R30 HR, R32 quality) and a Platform Admin registers the domains. This is a role grant, so it needs the user's approval.
- **Which parameters exist and who owns them** (spec T-13 estimates about 300): approval bands, discount ceilings, SLA targets, credit limits. The registry is empty by design; the values are business decisions. Wiring the M63 rules to read `value_at` instead of their own constants is the follow-up once the parameters exist.
- **Emergency change path** (FR-MDM-014 P1, BRU-MDM-09): apply now, retrospective approval within 24 h, automatic revert. Not built: it needs the CTO's rule for who may use it.
- **Unmerge** (FR-MDM-027, T-06) belongs to the M33 merge; **lineage** (FR-MDM-034, T-10) is derived from live dependencies by design, so it has no capture.
- **Domain events** `mdm.parameter_changed` / `mdm.hierarchy_changed` / `mdm.records_merged` (spec §12.3) are not in the event contract registry; the decisions are recorded in each record's chatter. Adding the contracts is a separate change.
- **Deputy routing on absence** (FR-MDM-004): the deputy is recorded; the M63 substitution register already moves an absent approver's tasks to a delegate.

## 5. State

**Committed on `fix/m64-capture-buttons` (worktree `1000 fix/m64cap-wt`), not landed on the shared branch and not deployed.** Landing and deploying (`-u cd_mdm_core,cd_p03_portal` on fix_real and fix_dev, then a restart so the new surfaces are served) wait for the user's go-ahead.
