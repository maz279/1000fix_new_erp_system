---
id: DA-009
title: Reference Data & Code List Register
category: 03 — Data & Information Architecture
code: DA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Technical Director (domain DD-11)
approver: Chief Architect
standards_basis: >
  ISO/IEC 11179-1:2023 · ISO/IEC 11179-32:2023 (concept system registration) ·
  DAMA-DMBOK 2.0 (2024 maintenance revision) — Reference & Master Data ·
  ISO 3166 / ISO 4217 / ISO 8601 for adopted external code sets
traces_to: >
  PGD-000 DA-009 · MD-019…MD-028 · MD-027 (status labels, STA-01…STA-07) · MD-026 (reason codes) ·
  AS-06 · DA-001 §4.6 · DA-002 attributes 15–16 · AR-003 DP-01
depends_on: DA-001 · DA-002 · DA-003 · MD-001
verified_on: 2026-08-18
priority: P1
needed_by: W1
enumeration_timestamp: 2026-08-18 14:30 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# DA-009 — Reference Data & Code List Register

### Category 03 · Code `DA` · ISO/IEC 11179-32:2023 · DAMA-DMBOK 2.0

---

## 1. Purpose

Forty-eight `MD-*` files hold reference-data **content**: fault codes, resolution codes, reason codes,
status labels, priority bands, units of measure, tax codes, currencies. They are well-structured, they
carry validation rules, and each has an owner.

**What does not exist is a register of code-list *identity*.** Nothing states how many code lists
there are, which ones exist, which model consumes which, or which enum in code corresponds to which
`MD-*` row. The register names the consequence precisely: *"`MD-026` reason codes and `MD-027` status
labels can drift from the enum values in code."*

They can, and nothing would detect it.

This document is that register: the identity space `CL-nnn`, the mandatory metadata per list, the
binding between a list and the columns that use it, the change authority, and the drift detection that
makes `MD-027` `STA-01` enforceable.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | What reference data is, and the boundary with master data |
| 2 | **The measured code-list population** |
| 3 | The `CL-nnn` identity space and its mandatory metadata |
| 4 | **Binding** — a list to the columns that consume it |
| 5 | **The 348 state machines** as code lists, and their transition maps |
| 6 | Adopted external standards — ISO, statutory, brand-supplied |
| 7 | Change authority, versioning and effective dating |
| 8 | Bilingual and customer-facing labels |
| 9 | **Drift detection** — the check the estate lacks |
| 10 | Distribution and caching |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Code-list **content** — the actual values | The 48 `MD-*` files | Retained as content authority. This registers the list, not its members |
| Master data (party, asset, catalogue) | `DA-004` | §2.1 states the boundary |
| Field definitions | `DA-002` | This document supplies attributes 15–16 |
| State machine *behaviour* — guards, transitions in code | `AR-003` DP-01, per-module SDD | This document registers the state **set** and the declared map |
| Business rules acting on a code | `05-05` | |
| Glossary terms | `RR-001` | A term is not a code |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Developers** | §4 binding — which register a `Selection` field must agree with |
| Content authors (`MD-*`, `UI-*`) | §7 change authority; §8 labels |
| `DA-002` stewards | Attributes 15–16 |
| QA | §9 drift checks are directly testable |
| Localisation | §8 — every customer-facing code needs a Bengali label |

---

## 2. What Reference Data Is

### 2.1 The boundary with master data

`DA-004` §2.2 sets the three-way test. Restated from this side:

| | Master data | **Reference data** |
|---|---|---|
| Lifecycle | **Independent** — created, changes, retires on its own | **None** — a value exists or does not |
| Duplicates | **Real and must be merged** | **Impossible** — two fault codes are not "the same code twice" |
| Volume | Thousands to millions | **Tens to hundreds per list** |
| Change | Continuous, operational | **Governed, versioned, approved** |
| Needs | Survivorship, match/merge, golden record, hierarchy | **Versioning, effective dating, bilingual labels, drift detection** |

> **The distinction determines what machinery gets built.** `DA-004`'s merge, survivorship and unmerge
> apparatus is meaningless for a reason code. This document's drift detection and version pinning are
> meaningless for a customer.

### 2.2 The classes of reference data

| Class | Governed by | Examples |
|---|---|---|
| **Internal enumerations** | This register + `MD-*` | Fault codes, resolution codes, reason codes, hold reasons, disposition codes |
| **State sets** | This register + `MD-027` | **348 model state machines** (§5) |
| **Adopted external standards** | This register; **content is not ours** | ISO 3166 countries, ISO 4217 currencies, ISO 8601 |
| **Statutory code sets** | This register; **content set by an authority** | Mushak tax codes, NBR account heads, BEFTN bank codes |
| **Partner-supplied** | This register; **content set by a third party** | Brand claim rejection codes, courier status codes |
| **Configuration enumerations** | This register | Delivery modes, channels, priority bands, UoM |

> **The last three classes are the ones that break.** We do not control the content, the third party
> changes it without telling us, and the first symptom is a rejected claim or a failed filing.
> §6 states the handling.

---

## 3. The Measured Population

Counted at **2026-08-18 14:30 (+06)**.

| Measure | Count | Source |
|---|---:|---|
| `MD-*` files holding reference-data content | **10** of 48 (`MD-019`…`MD-028`) | Enumerated |
| Additional `MD-*` files carrying code sets | **~8** (`MD-035` accounts, `MD-037` tax, `MD-038` payment, `MD-039` currency, `MD-023` UoM, `MD-036` dimensions, `MD-043` payroll elements, `MD-047` e-waste routes) | Enumerated |
| **Entities declaring a `state` field** | **348** | `DA-001` §2.2 |
| **States estimated across all state machines** | **600–1,200** | `MD-027` §7 |
| Distinct field names suggesting an enumeration (`*_code`, `*_type`, `*_status`, `*_reason`) | **~470** | Derived from the 5,301 field names |
| **Code lists registered today** | **0** | — |

### 3.1 Findings

> **`PGD-A5-15` — no register of code-list identity exists, and the estate has roughly 470 candidates.**
>
> The 48 `MD-*` files hold content for perhaps 25 lists. **The field-name analysis suggests ~470
> columns are enumerations** — `order_type`, `channel`, `repair_level`, `disposition_code`,
> `hold_reason`, `grade`, `severity`, and 348 `state` columns. **Most have no `MD-*` file and no
> register entry**, so their permitted values exist only as a `Selection` list in Python.
>
> That is not automatically wrong — a two-value internal flag does not need a governed register. **But
> nothing currently distinguishes the ones that do from the ones that do not**, and §4.2's binding
> rule is what makes that a decision rather than an accident.

> **`PGD-A5-16` — `MD-027` `STA-01` is unenforceable as written, and the gap is measurable.**
>
> `MD-027` `STA-01` (class **H**, hard block): *"Every `fix.*` model with a `state` field must have a
> complete register entry set."*
>
> **348 models declare a `state`.** `MD-027` §7 estimates **600–1,200 states**, which at 348 models is
> an average of 1.7–3.4 states per machine — **implausibly low** for machines like `fix.service.order`
> (14 states) or `fix.warranty.claim`. Either the estimate was made against a much smaller model count,
> or many of the 348 are expected to be trivial.
>
> Either way, **`STA-01` cannot be enforced against a register that does not know how many models it
> should contain.** §5.3 makes it enforceable by deriving the expected set from the schema.

---

## 4. The Register

### 4.1 Identity

| Attribute | Rule |
|---|---|
| `list_id` | **`CL-nnn`** — permanent, never reused, allocated by the Technical Director (DD-11) |
| `name` | Business name |
| `class` | §2.2 — internal / state set / adopted external / statutory / partner / configuration |
| `owner` | A `DA-003` §3.2 domain owner |
| `content_source` | The `MD-*` file, the external standard, or "this register" |
| `authority` | Who may add, deactivate or change a member |
| `versioned` | Whether members are version-pinned (§7.2) |
| `effective_dated` | Whether members carry `valid_from` / `valid_to` |
| `bilingual` | Whether members require Bengali labels (§8) |
| `customer_facing` | Whether any member is shown to a customer |
| `member_count` | **Counted, not asserted** |
| `bound_columns` | **§4.2 — every column consuming this list** |

### 4.2 Binding — the rule that makes the register useful

> **A code list with no declared bindings is a spreadsheet.** The binding is what turns it into a
> control.

| # | Rule |
|---|---|
| **BD-01** | **Every enumerated column in `DA-002` declares its `CL-nnn`** (attribute 15, value domain) |
| **BD-02** | **Every `CL-nnn` declares its bound columns.** The two directions must agree — a `DA-002` `RC-1`-class reconciliation |
| **BD-03** | A column bound to a list is enforced by a **check constraint or FK generated from the register** (`DA-001` §4.6 S-02), never hand-written |
| **BD-04** | A column with an enumeration and **no** `CL-nnn` is either (a) registered, or (b) explicitly recorded as **local** with a stated reason. **Silence is not an option** |
| **BD-05** | A **local** enumeration may not be customer-facing, may not appear in a report, and may not cross a module boundary. Any of those three promotes it to a registered list |

> **BD-05 is the test that keeps the register at a sensible size.** A two-value internal processing
> flag stays local. The moment it appears on a dashboard, it needs a label, a Bengali label, an owner
> and a change authority — so it becomes a `CL-nnn`.

### 4.3 Members

| Attribute | Rule |
|---|---|
| `code` | The stored technical value. **ASCII, never Bengali** (`MD-001` `CF-04`), never displayed (`MD-027` `STA-04`) |
| `label_en`, `label_bn` | Internal labels |
| `customer_label_en`, `customer_label_bn` | Null where not customer-visible |
| `description` | What the code **means** — the `F3` lesson (`DA-002` §1) |
| `sort_order` | Display order |
| `active` | Archived, never deleted (`MD-001` `GR-05`) |
| `valid_from`, `valid_to` | Where effective-dated |
| `semantic_token` | For state sets — one of the eight `VB-008` tokens |
| `requires_reason` | Where selecting it demands a reason code |

| # | Rule |
|---|---|
| **MB-01** | **A code is never reused, even after archive** (`MD-001` `GR-04`, `RG-02`). Audit trails reference it |
| **MB-02** | Deactivating a member does **not** invalidate historical rows carrying it |
| **MB-03** | Adding a member is additive; **changing a member's meaning is a new member plus deactivation of the old** |
| **MB-04** | Every member has a `description`. A code with a label and no definition is a code two people use differently |

---

## 5. State Sets — the 348

### 5.1 Why state sets are reference data

A `state` column's permitted values are an enumeration with an owner, labels, bilingual requirements
and a change authority. **`MD-027` already models it correctly** — keyed `model_name` + `state_key`,
with `allowed_next_states` carrying the transition map, `semantic_token` for colour, and
`is_customer_visible` driving the label requirement.

### 5.2 The relationship to `AR-003` DP-01 and AS-06

| Concern | Owner |
|---|---|
| **The state set** — which states exist, their labels, their tokens | **`DA-009` / `MD-027`** |
| **The transition map** — which transitions are permitted | **`MD-027` `allowed_next_states`**, declared once (AS-06) |
| **The guards** — under what condition a transition is allowed | **`AR-003` §9**, per module SDD |
| **The enforcement** — `_do_transition` | `AR-003` DP-01; `AR-012` `FF-06` |

> **The register holds the *set* and the *map*; the module holds the *guards*.** `MD-027` `STA-02`
> rejects a transition not in `allowed_next_states`; the module additionally rejects one whose guard
> fails. Both are needed: the register makes the map inspectable and bilingual; the module makes it
> conditional.

### 5.3 Making `STA-01` enforceable

`MD-027` `STA-01` requires every `fix.*` model with a `state` to have a complete register entry set.
**It cannot be enforced against an unknown denominator.**

| # | Rule |
|---|---|
| **ST-01** | **The expected set is derived from the schema**, not asserted: every model in `DA-002` with a `state` column (currently **348**) must have a `CL-nnn` state set |
| **ST-02** | The check is **generated and run in CI** — `AR-012` `FF-37` |
| **ST-03** | A model with a `state` and no registered set **fails the design gate** (`AR-003` X-03 extended) |
| **ST-04** | A registered state not reachable by any transition **warns** (`MD-027` `STA-07`) |
| **ST-05** | A model with no terminal state **fails** (`MD-027` `STA-06`) |
| **ST-06** | **The 600–1,200 estimate is replaced by a count** once the sets are registered, and `MD-027` §7 is corrected |

### 5.4 The customer-visible subset

`MD-027` `STA-03` requires both customer labels where `is_customer_visible`. The estate consequence:

| # | Rule |
|---|---|
| **CV-01** | **A state key is never displayed to a customer** (`STA-04`) |
| **CV-02** | Every customer-visible state carries **English and Bengali** customer labels |
| **CV-03** | A customer-visible state set is a **content deliverable**, not only a technical one — `UI-*` and `BN-*` own the wording |
| **CV-04** | **Changing a customer-visible label is a customer communication change**, subject to content approval, not a developer edit |

---

## 6. Adopted, Statutory and Partner Code Sets

**We do not control the content of these, and they change without notice.**

| Class | Examples | Owner | Change source |
|---|---|---|---|
| **Adopted external** | ISO 3166 countries, ISO 4217 currencies, ISO 8601 | DD-09 Ops | Standards body |
| **Statutory** | Mushak tax codes, NBR account heads, BEFTN bank codes, e-waste disposal routes | DD-06 CFO | **Government** |
| **Partner-supplied** | Brand claim rejection codes, courier status codes, payment gateway response codes | DD-08 CCO | **17+ brands, 4 couriers, 3 rails** |

### 6.1 Handling

| # | Rule |
|---|---|
| **EX-01** | An external set is **registered with its source, its version and its verification date** |
| **EX-02** | **Content is never edited locally.** A local variant is a new list with a mapping to the external one |
| **EX-03** | **An anticorruption mapping** translates the external set to the internal one (`AR-005` §7). A brand's rejection code maps to our reason code; the brand's code never enters our domain model |
| **EX-04** | **Currency is verified at every wave gate** and recorded in `RR-005` — the same control as `AR-013` §9 |
| **EX-05** | An **unrecognised inbound code** is quarantined and alerted, never silently mapped to "other" |
| **EX-06** | A statutory set change is treated as a **regulatory change**, with the same currency discipline as a statute |

> **EX-05 is the rule that prevents a silent data-quality collapse.** A brand adding a rejection code
> we do not recognise, silently bucketed as "other", produces a claim-rejection analysis that is
> correct in total and useless in detail — and nobody notices for months.

---

## 7. Change Authority and Versioning

### 7.1 Authority

| Action | Authority |
|---|---|
| Create a `CL-nnn` | Technical Director (DD-11) with the domain owner |
| Add a member | The list's declared authority (§4.1) |
| Deactivate a member | Domain owner |
| **Change a customer-facing label** | Domain owner **+ Content Design + Localisation** (`MD-027` §8) |
| Change a state transition map | **Design Authority** — it is a behaviour change (AS-06) |
| Change a statutory or partner set | **Not ours.** Absorbed via §6 |

### 7.2 Versioning and pinning

| # | Rule |
|---|---|
| **VS-01** | A list is **versioned** where a historical record must be interpreted against the version in force |
| **VS-02** | **Version pinning is required** where a contract or statutory document cites a code — `DT-031` §9 already pins `MD-028` SLA band versions |
| **VS-03** | **Effective dating** (`DA-001` §4.7) applies where a member's meaning changes over time — tax codes, payroll elements, SLA bands |
| **VS-04** | **A historical row is interpreted against the version in force at its event date**, never the current one (`DA-007` KY-05) |
| **VS-05** | A version change **notifies registered consumers before it takes effect** (`RP-006` `SM-15` discipline) |

> **VS-02 exists because of `DT-031`.** A printed SLA annex cites band definitions; if the band changes
> and the annex is not pinned, the printed contract and the system disagree — and the contract wins in
> a dispute.

---

## 8. Labels and Bilingual Requirements

| # | Rule |
|---|---|
| **LB-01** | Every code has `label_en` and `label_bn` (AS-12) |
| **LB-02** | Every **customer-visible** code additionally has `customer_label_en` and `customer_label_bn` |
| **LB-03** | Bengali label columns are sized **1.4×** their English counterpart (`DA-001` T-04) |
| **LB-04** | **The code itself is ASCII and never displayed** (`CF-04`, `STA-04`) |
| **LB-05** | Translation completeness is **100% before acceptance** (`AR-012` `FF-24`) |
| **LB-06** | A label change is a **content change**, not a data change (CV-04) |

---

## 9. Drift Detection

**The register names the risk: code lists drift from the enums in code.** Five checks close it.

| # | Check | Compares | Enforcement |
|---|---|---|---|
| **DR-01** | **Schema ↔ register** | Every enumerated column's permitted values against its `CL-nnn` members | **CI, blocking.** `AR-012` `FF-37` |
| **DR-02** | **State completeness** | Every model with a `state` has a registered set (ST-01) | **CI, blocking** |
| **DR-03** | **Transition map ↔ code** | `MD-027` `allowed_next_states` against the module's declared `_TRANSITIONS` | **CI, blocking** |
| **DR-04** | **Binding symmetry** | `DA-002` attribute 15 ↔ `CL-nnn` `bound_columns` (BD-02) | CI, blocking |
| **DR-05** | **Value drift in data** | Distinct values present in production against registered members (`DA-008` `PQ-DRIFT`) | Monthly; a value not in the register is a defect |

> **DR-03 is the one that would have prevented the class of defect the estate keeps finding.** A
> transition map declared in `MD-027` and a `_TRANSITIONS` structure declared in code are two
> statements of the same fact — exactly the shape of `F3` (`DT-031` vs `MD-028`) and of `AP-01`
> (`05-03` vs module §12.3). **Two statements of one fact diverge unless something joins them.**

---

## 10. Distribution and Caching

| # | Rule |
|---|---|
| **DS-01** | Reference data is **read-mostly and cacheable**; caching is expected |
| **DS-02** | A cache carries the **list version**; a version change invalidates it |
| **DS-03** | Offline clients (`AR-010` §7.1) hold reference data as **versioned scoped reference data**, refreshed on sync |
| **DS-04** | The portal receives lists by **event on change** (`catalogue.updated` pattern), never by nightly export (`DA-004` DI-01) |
| **DS-05** | A **customer-visible label change propagates to every surface** — portal, app, notification templates, printed documents |
| **DS-06** | Reference data is **`S0` or `S1`** and carries no personal data; it is freely cacheable under `DA-005` §6 |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **How many of the ~470 enumeration candidates become `CL-nnn` (`PGD-A5-15`)?** BD-04/BD-05 make it a decision; someone must take it | Technical Director / Data Architect | **W1** | The register's size and effort |
| **Q-02** | **Is `MD-027` §7's 600–1,200 estimate corrected once the 348 sets are registered (ST-06)?** | Enterprise Architecture | W1 | `STA-01` enforceability |
| **Q-03** | Who authors the state sets for 348 models — module squads or Enterprise Architecture? | Chief Architect | **W0** | `AR-003` design gate |
| **Q-04** | Are partner code sets (brand rejection codes) obtainable in advance, or discovered at first use? EX-05 quarantines the unknown, but a quarantine at go-live is a blocked claim | CCO / M09 owner | W4 | Claim processing |
| **Q-05** | Does `DA-009` become the authority over `MD-019`…`MD-028`, or register alongside them? §1.1 says register alongside; consumers need it stated | Enterprise Architecture | W1 | Which document a developer reads |

---

## 12. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-D9-01 | Scope | Register content; **register identity, `MD-*` keeps content** | **Identity only** | The 48 `MD-*` files are good content documents; duplicating members would create the drift this document exists to prevent | `MD-*` retained as content authority |
| D-D9-02 | Local enumerations | Register everything; **register with a stated local exception** | **BD-04/BD-05** | Registering a two-value internal flag is ceremony; leaving a customer-facing code unregistered is a defect | Three tests promote a local to registered |
| D-D9-03 | State sets | Separate mechanism; **treat as reference data** | **Reference data** | `MD-027` already models them correctly; a second mechanism would diverge | 348 sets in the register |
| D-D9-04 | `STA-01` denominator | Assert; **derive from the schema** | **Derive (ST-01)** | A hard-block rule against an unknown denominator cannot fire | `FF-37` |
| D-D9-05 | External sets | Edit locally; **adopt + anticorruption mapping** | **Mapping (EX-02, EX-03)** | A brand's code entering our domain model makes their change our migration | Mapping per external source |
| D-D9-06 | Unknown inbound codes | Map to "other"; **quarantine and alert** | **Quarantine** | Silent bucketing produces analysis that is right in total and useless in detail | EX-05; Q-04 |
| D-D9-07 | Transition map location | Code only; register only; **register declares, code enforces guards** | **Both, reconciled** | The register makes it inspectable and bilingual; the module makes it conditional | DR-03 joins them |

---

## 13. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The boundary with master data is stated and consequential | §2.1 |
| AC-02 | The population is measured, not asserted | §3 |
| AC-03 | Every list carries identity, ownership, authority and **bound columns** | §4.1, §4.2 |
| AC-04 | Local enumerations have a stated exception rule with three promotion tests | BD-04, BD-05 |
| AC-05 | **The 348 state machines are registered as code lists, and `STA-01` becomes enforceable** | §5.3 ST-01…ST-06 |
| AC-06 | External, statutory and partner sets have an anticorruption rule and a quarantine rule | §6.1 |
| AC-07 | Versioning and pinning are specified, with the `DT-031` case | §7.2 |
| AC-08 | Every code carries bilingual labels; customer-visible codes carry customer labels | §8 |
| AC-09 | **Five drift checks exist, and DR-03 joins the two statements of the transition map** | §9 |

**Definition of done.** Complete when every criterion is met, Q-01 and Q-03 are resolved, and
`PGD-000`'s `DA-009` row is updated. **The register is 0-populated on issue and says so** (§3).

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `DA-001` §4.6 | `state` column rules; check constraints generated from this register |
| Upstream | `DA-003` DD-11 | Technical Director owns codes and reference data |
| Upstream | **`MD-019`…`MD-028`, `MD-035`…`MD-039`** | Content authority, retained |
| Upstream | **`MD-027`** | The state-label model this generalises |
| Downstream | `DA-002` attributes 15–16 | Value domain and valid values reference `CL-nnn` |
| Downstream | `DA-008` `PQ-DRIFT` | DR-05 value drift |
| Downstream | `AR-003` §9 | State sets and transition maps per module SDD |
| Downstream | `AR-012` `FF-37` | Drift checks DR-01…DR-04 |
| Downstream | `AR-010` §7.1 | Offline reference-data scope and versioning |
| Downstream | `UI-*`, `BN-*` | Customer-facing labels are content deliverables |
| Lateral | `RR-005` | Currency of adopted external and statutory sets |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md` §4.6 ·
`./DA-002_Data_Dictionary.md` · `./DA-003_Data_Governance_Framework_and_Stewardship_Model.md` ·
`./DA-004_Master_Data_Management_Design.md` §2.2 · `./DA-008_Data_Quality_Management_Plan.md` ·
`../02_Architecture_and_Design/AR-003_Software_Design_Description.md` §5.1 ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md`

**Workspace**
`../../project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md` ·
`../../project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md` · `../../project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md` ·
`../../project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md` · `../../project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md` ·
`../../project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-001_Master_Data_Governance_Charter.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md`

**External standards**

| Standard | Version | Verified |
|---|---|---|
| [ISO/IEC 11179-1:2023](https://www.iso.org/standard/78914.html) | Edition 4 | 2026-08-18 |
| [ISO/IEC 11179-32:2023 — Concept system registration](https://www.iso.org/standard/78926.html) | 2023 | 2026-08-18 |
| [DAMA-DMBOK](https://www.damadmbok.org/) — Reference & Master Data | 2.0 (2024 maintenance revision) | 2026-08-18 |
| ISO 3166 · ISO 4217 · ISO 8601 | Current | 2026-08-18 |

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Establishes the `CL-nnn` identity space with **binding** as the rule that makes it a control. Registers the **348 state machines** and makes `MD-027` `STA-01` enforceable by deriving its denominator from the schema. Raises `PGD-A5-15` (~470 unregistered enumeration candidates) and `PGD-A5-16` (`STA-01` unenforceable as written) | *Pending — Chief Architect* |

---

*`DA-009` · Category 03 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
