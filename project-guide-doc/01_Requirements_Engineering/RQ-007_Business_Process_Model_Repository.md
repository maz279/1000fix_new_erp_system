---
id: RQ-007
title: Business Process Model Repository (BPMN 2.0)
category: 01 — Requirements Engineering
code: RQ
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Business Process Owner (Service Operations), with the Lead Business Analyst
approver: ERP Design Authority
standards_basis: OMG BPMN 2.0 (constrained subset per SP-003 §4.2) · ISO/IEC/IEEE 29148:2018 §6.2–§6.3 · ISO 9001:2015 clause 4.4
traces_to: PGD-000 RQ-007 row · SP-001 (value streams) · SP-002 (as-is baselines) · SP-003 (notation standard) · module §8 state models
depends_on: RQ-001 (requirement set) · RQ-004 (link T-13) · RQ-009 (business rules) · SP-003 (notation, already issued)
verified_on: 2026-08-18
priority: P1
needed_by: W1
enumerated_on: 2026-08-18 02:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RQ-007 — Business Process Model Repository

### Category 01 · Code `RQ` · OMG BPMN 2.0 (constrained) · ISO 9001:2015 §4.4

---

> **What exists, measured at 2026-08-18 02:15 (+06).**
>
> | Artefact | Count | What it establishes |
> |---|---:|---|
> | Value streams (`SP-001` §4.2) | **5** | `VS-1` request-to-cash … `VS-5` lead-to-contract, with 58 stage rows |
> | As-is baseline register (`SP-002`) | 1 register | Method, site clustering, closing window — no completed baselines |
> | Notation standard (`SP-003`) | 1 standard | A constrained BPMN 2.0 subset with 10+ binding rules. **Genuinely good** |
> | Standard operating procedures (`06B`) | **28** | Step-level operational text |
> | Module state models (§8) | **67** | With **1,590 transition guard rows** |
> | **Actual process models** | **0** | One code fence in the entire 34-file process folder |
>
> **The programme has not failed to think about its processes.** It has 1,590 transition guards
> and 28 SOPs. What it lacks is the **one view nobody owns**: the cross-module view. A service
> order crossing `M01` → `M02` → `M15` → `M20` passes through four independently-authored state
> machines and one SOP written from the branch's perspective. Nothing shows the whole path, so
> nothing can show where it breaks.
>
> This document specifies that repository — and it does **not** restate `SP-003`, which already
> settles notation and does it well.

---

## 1. Purpose

Odoo workflow states and n8n orchestrations have to be configured from something. Today they would
be configured from 67 state machines that were written independently, 28 SOPs written from
operational rather than system perspective, and five value-stream stage tables. Those three views
have never been reconciled, so nobody can say whether they describe the same business.

This document creates the **process model repository**: the controlled set of executable-grade
To-Be process models that reconcile the three views, bind each process step to the requirements,
rules, roles, entities and events that realise it, and become the artefact from which workflow
configuration is derived rather than invented.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **model inventory** — which processes shall be modelled, at which level (§4) |
| 2 | The **`BPM-nnn` identifier space** and the model record schema (§3.2, §3.3) |
| 3 | The **executable-grade standard** — what a model must contain beyond `SP-003`'s notation to be configurable (§5) |
| 4 | The **three-view reconciliation** — state model, SOP and process model (§6) |
| 5 | **Traceability** — link `T-13` and every lateral link a model step carries (§7) |
| 6 | **Model conformance review** and its checklist (§8) |
| 7 | The **production plan** — sequence, ownership, throughput, wave alignment (§9) |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Notation — permitted and forbidden BPMN elements, naming, swimlanes, gateways | **`SP-003`** | Already issued, already good. `PG-02`: one document, one purpose. This document **conforms to** `SP-003`, it does not replace it |
| SOP text | `SP-007`–`SP-034` | `SP-003` rule `PD-01` makes SOP text authoritative and the diagram derivative; this document keeps that |
| As-is baseline capture method and site clustering | `SP-002` | Method already defined |
| Value stream definition | `SP-001` | `L0`/`L1` already defined |
| The requirements themselves | `RQ-001` | A model step realises requirements; it does not define them |
| Business rules | `RQ-009` | A gateway cites a rule; it does not own it |
| Workflow engine configuration | `AR-003`, `M63` | The model is the input to configuration, not the configuration |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Business process owners | The To-Be process they own and will be measured on |
| Odoo configurators | The state, transition and guard set to configure `M63`/workflow from |
| Integration engineers | The n8n orchestrations and the message flows that cross a pool boundary |
| Business analysts | The step-to-requirement binding that shows which requirements a process needs |
| QA | The end-to-end journeys `TS-012` and `QA-002` derive from |
| Training and change | The process the training material teaches (`CH-002`) |
| ISO 9001 auditors | The documented information required by clause 4.4.2 |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | How applied | Departure |
|---|---|---|
| **OMG BPMN 2.0** | Through the constrained subset defined in `SP-003` §4.2 — permitted elements, forbidden elements, unlabelled-flow prohibition, colour prohibition | The subset is a deliberate `SP-003` restriction; this document adopts it unchanged |
| ISO/IEC/IEEE 29148:2018 §6.2, §6.3 | Process models are an elicitation and analysis artefact; `T-13` binds them to requirements | None |
| ISO 9001:2015 clause 4.4 | Process approach: inputs, outputs, sequence, interaction, criteria, resources, responsibilities, risks | §5.2 makes each of clause 4.4.1's eight items a mandatory model attribute |
| ISO 9001:2015 clause 4.4.2 | Documented information to support operation and have confidence processes are carried out as planned | `SP-003` already rules that text satisfies this; models supplement |

**Verified 2026-08-18.** BPMN 2.0 remains the current OMG specification for business process
modelling notation.

### 2.2 Source material relied on

| Source | What it provides | Measured |
|---|---|---|
| `../../project_content/06_Process_SOP_and_Workflow/06A/SP-001` | Five value streams `VS-1`–`VS-5`; the `L0`–`L3` hierarchy; stream-to-wave mapping | 58 stage rows |
| `.../06A/SP-002` | As-is baseline method, site clustering (C1–C5), observer method, closing window | Register, no completed baselines |
| `.../06A/SP-003` | **The notation standard.** Rules `PD-01`–`PD-10`+, permitted/forbidden element tables, decomposition and stopping rules, naming, swimlanes | Adopted in full |
| `.../06A/SP-004`, `SP-005`, `SP-006` | Approval matrix and delegation, escalation matrix, segregation-of-duties register | Bound at gateway level |
| `.../06B/SP-007`–`SP-034` | 28 SOPs | Step-level operational text |
| `../../1000fix_ERP_Module/03_Modules/*/M*.md` §8 | State models and transition guards | **67 state models, 1,590 guard rows** |
| `.../05-06` §11 | 15 critical end-to-end journeys | 15 |
| `RQ-009` | The business rules a gateway may cite | 1,330 module rules |

### 2.3 Findings this document addresses

| Finding | Source | Treatment |
|---|---|---|
| `PGD-000` `RQ-007` row | Register | *"`SP-001`/`002`/`003` establish notation and a baseline register but hold no actual models."* Measured and confirmed: **zero models** | Addressed by §4, §9 |
| **`RQA-22`** *(raised here)* | This document | **Three views of the same processes exist and have never been reconciled**: 67 module state models (1,590 guards), 28 SOPs, and 5 value-stream stage tables | Open — §6 |
| **`RQA-23`** *(raised here)* | This document | **No cross-module process view exists.** Every state model stops at its module boundary; a service order traverses four | Open — §4.2 |
| `M-09` | `00-06` | Wave capacity never validated. Modelling makes handover volume and cross-module dependency visible before build | Partial |

---

# 3. Repository Structure

## 3.1 Levels — inherited from `SP-001` §4.1 and `SP-003` §4.3

| Level | Granularity | Artefact | Model required? | Owner |
|:--:|---|---|:--:|---|
| **L0** | Value stream | `SP-001` §4.3 stream map | One per programme, exists | Process Architect |
| **L1** | Stage | `SP-001` §4.4–4.8 stage tables | **One model per stream — 5 required, 0 exist** | Process Architect |
| **L2** | Process | An SOP in `06B` | **One model where three or more parallel paths exist** (`SP-003` §4.3) | Process Owner |
| **L3** | Activity / step | A row in the SOP §5 step table | **Never modelled** (`SP-003` §4.3) | Process Owner |

**Rule `PM-01`.** This document adds no level. `SP-003` rule `PD-02` (the stopping rule) and
`PD-03` (the 4–20 step bound) govern unchanged.

## 3.2 Identifier space

| Space | Format | Scope | Authority | Sweep result |
|---|---|---|---|---|
| `BPM-nnn` | Three digits | Programme-wide process model | **This document** | **0** prior occurrences across all five repositories at 02:15 (+06) |

**Rule `PM-02`.** A model identifier is permanent (`PG-05`). A model that is superseded is
tombstoned; its identifier is never reissued to a different process.

**Rule `PM-03`.** `BPM-nnn` identifies the **model**. It does not identify the SOP (`SP-nnn`), the
value stream (`VS-n`) or the state machine (module §8). Each model record names all three.

## 3.3 Model record schema

```yaml
model_id:        BPM-013
name:            Issue a repair estimate            # SP-003 PD-04: <Verb> <object>
level:           L2
value_stream:    VS-1                               # SP-001
sop:             SP-013                             # the authoritative text (SP-003 PD-01)
modules:         [M01, M31, M15]                    # every module the process traverses
primary_module:  M01
state_machines:  [M01 §8 service_order, M31 §8 repair_job]
roles:           [R08, R11, R14]                    # SP-003 PD-06: lanes are roles
pools:           [1000FiX, Customer]                # external pools collapsed
wave:            W1
# --- content ------------------------------------------------------------
steps:           14                                 # SP-003 PD-03: 4 <= n <= 20
gateways:        [G1 estimate above threshold?, G2 customer response?]
end_events:      [estimate approved, estimate rejected, estimate expired]
exception_paths: [customer unreachable, part unavailable, device beyond repair]
# --- bindings (RQ-004) ---------------------------------------------------
T13_requirements: [FR-SRM-014, FR-SRM-015, FR-WSR-021, FR-INV-008]
rules:            [BRU-SRM-13, BRU-SRM-14]          # RQ-009
automations:      [AUT-SRM-04]                      # module §11
entities:         [fix.service.estimate, fix.service.order]
events:           {publishes: [estimate.issued, estimate.expired], consumes: [service_order.diagnosed]}
documents:        [DT-005]                          # project_content DT-nnn
messages:         [NT-018, NT-019]                  # notification library
kpis:             [KPI-014]
# --- control -------------------------------------------------------------
status:          Draft | In review | Approved | Superseded
version:         1.0
approved_by:     Service Operations Manager
approved_on:
conformance:     {SP-003: pass, PM-check: 0 open}
```

## 3.4 Storage and format

| # | Rule |
|---|---|
| `PM-04` | The **authoritative artefact is the model record plus its SOP text** (`SP-003` `PD-01`). The diagram is derivative |
| `PM-05` | Diagrams are stored as **BPMN 2.0 XML** — the interchange format — with a rendered image alongside. A diagram that exists only as an image cannot be diffed, validated or migrated |
| `PM-06` | Model artefacts live in `01_Requirements_Engineering/RQ-007_artefacts/`, per `FOLDER_STRUCTURE.md` §5 supporting-artefact convention |
| `PM-07` | Every model carries an enumeration timestamp on its content counts (`PG-M11`) |

> **`PM-05` is the first machine-readable artefact this programme would produce.**
> `PGD-AUDIT-001` §7.3 verified that all 601 files are markdown and that **zero** `.yaml`, `.json`,
> `.sql`, `.tf` or `.py` files exist. BPMN XML is validatable, diffable and toolable; a PNG is
> none of those.

---

# 4. Model Inventory

## 4.1 L1 — value stream models *(5 required)*

| `BPM` | Value stream | Streams from `SP-001` | Wave | Modules traversed |
|---|---|---|:--:|---|
| `BPM-001` | Request-to-cash | `VS-1` | W1 | M01, M02, M03, M04, M31, M15, M20, M19 |
| `BPM-002` | Procure-to-pay | `VS-2` | W3 | M16, M41, M15, M52, M19, M42 |
| `BPM-003` | Hire-to-retire | `VS-3` | W5 | M58, M21, M22, M55, M56, M57, M59 |
| `BPM-004` | Claim-to-reimbursement | `VS-4` | W4 | M09, M01, M31, M20, M19, P08 |
| `BPM-005` | Lead-to-contract | `VS-5` | W4 | M07, M36, M08, M11, M39 |

**Rule `PM-08`.** An L1 model shows **stages and handovers**, with L2 processes as collapsed
sub-processes. `SP-001` §4.9 already identifies handovers as *"where value is lost"*; the L1 model
is where that becomes visible rather than asserted.

## 4.2 L2 — process models

**Rule `PM-09` — the modelling trigger.** An L2 process is modelled where **any** of the following
holds. Otherwise its SOP text stands alone, per `SP-003` `PD-01`.

| # | Trigger | Rationale |
|---|---|---|
| `MT-1` | Three or more parallel paths | `SP-003` §4.3, inherited |
| `MT-2` | **The process traverses two or more modules** | The cross-module view nobody owns (`RQA-23`) |
| `MT-3` | The process crosses a pool boundary — customer, brand, seller, courier, vendor | Message flow semantics are the reason BPMN was chosen (`SP-003` §4.2) |
| `MT-4` | The process carries a timer with a business consequence — SLA, expiry, statutory deadline | Boundary timer events are the second reason BPMN was chosen |
| `MT-5` | The process is one of the 15 critical journeys in `05-06` §11 | They are the E2E test basis |
| `MT-6` | The process handles money movement or custody transfer | Irreversibility |

**Applying the triggers to the 28 SOPs**

| SOP | Process | Triggers | Model | Wave |
|---|---|---|:--:|:--:|
| `SP-007` | Walk-in intake and front desk | `MT-2`, `MT-5`, `MT-6` | `BPM-010` | W1 |
| `SP-008` | On-site field service visit | `MT-2`, `MT-3`, `MT-4`, `MT-5` | `BPM-011` | W2 |
| `SP-009` | Pick-and-drop and reverse logistics | `MT-2`, `MT-3`, `MT-5`, `MT-6` | `BPM-012` | W3 |
| `SP-010` | Workshop and depot repair | `MT-1`, `MT-2`, `MT-5` | `BPM-013` | W2 |
| `SP-011` | Remote support and managed services | `MT-2`, `MT-4` | `BPM-014` | W5 |
| `SP-012` | Data recovery and secure data handling | `MT-2`, `MT-6` | `BPM-015` | W6 |
| `SP-013` | Estimate approval and rework control | `MT-2`, `MT-3`, `MT-4`, `MT-5` | `BPM-016` | W1 |
| `SP-014` | Warranty claim submission and reconciliation | `MT-2`, `MT-3`, `MT-4`, `MT-5`, `MT-6` | `BPM-017` | W4 |
| `SP-015` | Contract and AMC lifecycle | `MT-2`, `MT-4`, `MT-5` | `BPM-018` | W4 |
| `SP-016` | Spare parts issue, return and van stock | `MT-2`, `MT-6` | `BPM-019` | W2 |
| `SP-017` | Procurement to payment | `MT-2`, `MT-3`, `MT-5`, `MT-6` | `BPM-020` | W3 |
| `SP-018` | Warehouse receipt, put-away and count | `MT-2` | `BPM-021` | W3 |
| `SP-019` | Cash collection and banking | `MT-2`, `MT-6` | `BPM-022` | W3 |
| `SP-020` | Month-end and year-end close | `MT-1`, `MT-2`, `MT-4`, `MT-5` | `BPM-023` | W3 |
| `SP-021` | Payroll run and statutory filing | `MT-2`, `MT-3`, `MT-4`, `MT-5`, `MT-6` | `BPM-024` | W5 |
| `SP-022` | Time, attendance and roster | `MT-2` | `BPM-025` | W5 |
| `SP-023` | Recruitment and onboarding | `MT-2` | `BPM-026` | W6 |
| `SP-024` | Marketplace seller onboarding and governance | `MT-2`, `MT-3`, `MT-5` | `BPM-027` | W7 |
| `SP-025` | Trade-in, refurbishment and resale | `MT-1`, `MT-2`, `MT-5`, `MT-6` | `BPM-028` | W6 |
| `SP-026` | E-waste collection and disposal | `MT-2`, `MT-5`, `MT-6` | `BPM-029` | W8 |
| `SP-027` | Rental and equipment as a service | `MT-2`, `MT-5`, `MT-6` | `BPM-030` | W6 |
| `SP-028` | Complaint escalation and compensation | `MT-2`, `MT-3`, `MT-4`, `MT-5` | `BPM-031` | W4 |
| `SP-029` | Internal quality audit and CAPA | `MT-1`, `MT-2`, `MT-5` | `BPM-032` | W5 |
| `SP-030` | Health, safety and incident reporting | `MT-2`, `MT-4` | `BPM-033` | W6 |
| `SP-031` | IT service desk and change management | `MT-2` | `BPM-034` | W6 |
| `SP-032` | Operational checklist library | *none* | **No model** — a library, not a process | — |
| `SP-033` | Diagnostic and triage decision tree library | *none* | **No model** — decision tables, `RQ-009` | — |
| `SP-034` | Call and conversation script library | *none* | **No model** — content | — |

**Count check, regenerated before issue (`PG-M10`):** 5 L1 models (`BPM-001`–`BPM-005`) + 25 L2
models (`BPM-010`–`BPM-034`) = **30 models**. Three SOPs are libraries and correctly carry no
model. `BPM-006`–`BPM-009` are **reserved, unallocated** — held for L1 models if a sixth value
stream is declared.

## 4.3 Coverage against the 15 critical journeys

`05-06` §11 names 15 end-to-end journeys that must be covered by automated tests. Each maps to a
model or a chain of models; where no single model covers a journey, the chain is named and the L1
model is the integrating artefact.

| # | Critical journey | Covered by |
|---:|---|---|
| 1 | Book online → dispatch → field repair → invoice → pay → close → survey | `BPM-001` via `BPM-011`, `BPM-016`, `BPM-022` |
| 2 | Walk-in intake → workshop repair → estimate → approval → QC → handover → pay | `BPM-001` via `BPM-010`, `BPM-013`, `BPM-016` |
| 3 | Pick & drop collection → workshop → return delivery → invoice | `BPM-012`, `BPM-013` |
| 4 | Warranty job → claim → submission → approval → reimbursement → reconciliation | `BPM-004` via `BPM-017` |
| 5 | AMC sale → activation → preventive schedule → visit → renewal | `BPM-005` via `BPM-018` |
| 6 | MSP alert → ticket → remote resolution → SLA → monthly report | `BPM-014` |
| 7 | Marketplace order → seller quote → selection → job → review → commission → payout | `BPM-027` |
| 8 | Rental reservation → delivery → return → damage assessment → billing | `BPM-030` |
| 9 | Trade-in → offer → intake → data wipe → refurbishment → grading → resale | `BPM-028`, `BPM-015` |
| 10 | E-waste collection → triage → destruction → recycling → disposal certificate | `BPM-029` |
| 11 | Data recovery case → custody → recovery → handover → purge certificate | `BPM-015` |
| 12 | Purchase requisition → PO → receipt → inspection → three-way match → payment | `BPM-002` via `BPM-020`, `BPM-021` |
| 13 | Payroll cycle → attendance lock → calculation → approval → BEFTN → payslips → posting | `BPM-024`, `BPM-025` |
| 14 | Complaint → non-conformance → root cause → CAPA → verification → closure | `BPM-031`, `BPM-032` |
| 15 | Month-end close → reconciliation → VAT return → management pack | `BPM-023` |

**All 15 covered.** No journey is left without a modelled path, which is the condition `QA-002`
needs to derive E2E tests.

---

# 5. The Executable-Grade Standard

`SP-003` settles *how a model is drawn*. This section settles *what a model must contain to be
configured from* — the property the register calls "executable-grade".

## 5.1 What "executable-grade" means here

**It does not mean the model executes.** `SP-003` §4.1 already ruled that no diagram in this
programme executes, and that ruling stands — 1000FiX implements on Odoo, not a BPM engine.

It means: **an Odoo configurator, an n8n author or a test designer can derive their artefact from
the model without asking a question.** A model that requires a conversation is a picture.

## 5.2 The eight mandatory attributes *(ISO 9001:2015 §4.4.1)*

| # | Attribute | Model must state | Derived artefact |
|---|---|---|---|
| `EX-1` | **Inputs** | The trigger, its source, and the entities that must exist first | Odoo state entry condition |
| `EX-2` | **Outputs** | Every typed end event and the state each leaves the entities in | Odoo terminal states |
| `EX-3` | **Sequence** | Ordered steps with no unlabelled flow (`SP-003` forbidden list) | Transition set |
| `EX-4` | **Interaction** | Every message flow crossing a pool boundary, with its `NT-nnn` | Notification triggers, n8n orchestration |
| `EX-5` | **Criteria and methods** | Every gateway condition stated as a decidable expression citing a `BRU-` rule or a `MD-` value | Odoo transition guard |
| `EX-6` | **Resources** | The role per lane and the system per task | Odoo group and record rule |
| `EX-7` | **Responsibilities** | RACI per step (`SP-003` §4.8), with approval authority from `SP-004` | Approval configuration |
| `EX-8` | **Risks and opportunities** | Every exception path, with the failure behaviour of each automation | `AUT-` failure behaviour, error handling |

**Rule `PM-10`.** A model missing any of the eight is not approved. This is not a style
preference: each maps to a configuration artefact that would otherwise be invented by whoever
builds it first.

## 5.3 Gateway conditions must be decidable

**Rule `PM-11`.** Every gateway condition is expressed as a decidable expression over named data,
and cites the rule or reference value that supplies the threshold.

| Not acceptable | Acceptable |
|---|---|
| *Is the estimate high value?* | *Is the estimate total > the branch approval threshold in `MD-021`?* — `BRU-SRM-14` |
| *Is the customer eligible?* | *Is an active entitlement recorded for this device at the request date?* — `BRU-SRM-02`, hard |
| *Is the part available?* | *Is the free stock at the assigned location ≥ the required quantity?* — `BRU-INV-04` |

**Rule `PM-12` — exhaustive branches.** `SP-003` `PD-10` already requires exhaustive gateway
branches and names the classic miss (*no response by expiry*). This document adds the derivation
obligation: **every branch must correspond to a transition in the underlying module state model**,
or the divergence is raised as a `D-1` defect (§6.3).

## 5.4 Exception paths

**Rule `PM-13`.** Every model states, for each step that can fail: what failure looks like, who is
notified, what state the entity is left in, and how the process resumes or terminates. `SP-003`
requires an error boundary event to correspond to a row in the SOP's exception table; this rule
requires the reverse as well — **an SOP exception row with no model path is an unmodelled failure**.

**Rule `PM-14`.** Every service task cites its `AUT-<CODE>-nn` and inherits that automation's
declared failure behaviour. The module template already forbids a blank failure behaviour; this
makes the model the place it becomes visible.

---

# 6. Three-View Reconciliation *(finding `RQA-22`)*

## 6.1 The three views

| View | Artefact | Count | Perspective | Boundary |
|---|---|---:|---|---|
| **System view** | Module §8 state model + transition guards | 67 models, **1,590 guards** | What the entity may do next | Stops at the module boundary |
| **Operational view** | SOP `06B` | 28 | What the person does | Stops at the function boundary |
| **Process view** | `BPM-nnn` | **0 today, 30 required** | What the business does end to end | Crosses both |

## 6.2 Why they diverge

They were authored by different functions, at different times, against different templates, and
nothing has ever compared them. The module template enforces reciprocity for dependencies
(`RG-04`) and for entity references (§10.2) — but nothing reconciles a state transition against
the SOP step that triggers it.

## 6.3 The reconciliation rules

| # | Rule |
|---|---|
| `PM-15` | Every state transition in a module §8 model shall appear in at least one `BPM` model, as a step outcome or a gateway branch. A transition no process reaches is **dead configuration** |
| `PM-16` | Every `BPM` step that changes an entity's state shall name the module and the transition it triggers. A step that changes state by unnamed means is unbuildable |
| `PM-17` | Every SOP §5 step shall map to a `BPM` step or be declared out of system scope (a purely physical act). `SP-003` `PD-05` already forbids "and"-joined steps, so the mapping is 1:1 or 1:0 |
| `PM-18` | Every SOP exception row shall map to a `BPM` exception path (`PM-13`) |
| `PM-19` | Divergence between views is a **`D-1` defect** (`RQ-004` §8) — a link asserted at one end only. It is raised to both owners and closed only when both agree. **It is never closed by editing whichever artefact is easiest to reach** |

## 6.4 What reconciliation will find

Stated as an expectation, not a result, because the models do not yet exist:

| Expected finding class | Why it is expected |
|---|---|
| Transitions with no process | 1,590 guards written module by module, against processes that were not modelled |
| Process steps with no transition | 28 SOPs written operationally, describing acts the system may not record |
| Gateway branches with no guard | `SP-003` `PD-10`'s "third answer" — the one nobody models |
| Handover steps with no owner on one side | `SP-001` §4.9 already flags handovers as where value is lost |
| Exception rows with no path | The most consequential class: an SOP that tells staff what to do when something fails, in a system with no state for it |

**Rule `PM-20`.** The reconciliation result is published per model as a defect count, not
suppressed. A model approved with open `D-1` defects records them; a model that reports zero
divergence against a 1,590-guard estate has almost certainly not been reconciled.

---

# 7. Traceability

## 7.1 Link `T-13` — process realisation

**Rule `PM-21`.** Every `BPM` step names the requirements it realises, and every requirement
realised by a process names the model. Reciprocal, per `RQ-004` `T-13`.

## 7.2 The lateral links a model step carries

| Link | To | Authority | Purpose |
|---|---|---|---|
| Requirements | `FR-`, `SWR-` | `RQ-001` | What the system must do at this step |
| Rules | `BRU-<CODE>-nn` | `RQ-009` | The gateway condition and the enforced constraint |
| Automations | `AUT-<CODE>-nn` | Module §11 | Service tasks and their failure behaviour |
| Roles | `Rnn` | `05-04` / `SC-004` | Lanes (`SP-003` `PD-06`) |
| Segregation | `SOD-nn` | `05-04` | Where role-doubling needs a compensating control (`SP-003` `PD-09`) |
| Approvals | `SP-004` matrix | `SP-004` | Approval authority at a gateway |
| Escalation | `SP-005` matrix | `SP-005` | Timer boundary consequences |
| Entities | `fix.*` | `05-02` / `DA-001` | Data objects |
| Events | `<aggregate>.<verb>` | `IN-003` | Message flows and integration points |
| Documents | `DT-nnn` | `project_content` 05 | Printed and generated artefacts |
| Messages | `NT-nnn` | `project_content` 04 | Notifications crossing a pool boundary |
| Reference values | `MD-nnn` | `project_content` 02 | Thresholds and durations behind gateway conditions |
| KPIs | `KPI-nnn` | `06-02` | Process performance measures |
| Tests | `TC-nnn` | `QA-003` | The E2E cases derived from the model |

**Rule `PM-22`.** A model step citing an identifier that does not resolve is a `D-2` defect
(`RQ-004` §8) and blocks model approval. The 198 unregistered `KPI-nnn` and the 12 unregistered
`Rnn` mean this check will fire on the first models produced — that is the check working, not the
check failing.

---

# 8. Conformance Review

A model is approved only when all three review passes return clean.

## 8.1 Pass 1 — notation conformance *(`SP-003`)*

Executed against `SP-003` §4.10's own review checklist. Summarised here, not restated:
permitted elements only; no inclusive or complex gateway; no system as a lane; no unlabelled
sequence flow leaving a gateway; colour carries no meaning; maximum six lanes; naming per `PD-04`;
lane order per `PD-08`; matching SOP text exists.

## 8.2 Pass 2 — executable-grade conformance *(this document)*

| # | Check | Fails when |
|---|---|---|
| `PC-01` | All eight §5.2 attributes present | Any is absent |
| `PC-02` | Every gateway condition is decidable and cites its rule or reference value | A condition is a question with no data behind it |
| `PC-03` | Every gateway branch corresponds to a state transition | `PM-12` breach |
| `PC-04` | Every step that changes state names its module and transition | `PM-16` breach |
| `PC-05` | Every failable step has an exception path | `PM-13` breach |
| `PC-06` | Every service task cites an `AUT-` with a declared failure behaviour | Blank failure behaviour |
| `PC-07` | Step count within 4–20 | `SP-003` `PD-03` breach |
| `PC-08` | Every cited identifier resolves | `D-2` defect |
| `PC-09` | Every end event is typed and named | `SP-003` §4.6 breach |
| `PC-10` | BPMN XML validates against the OMG schema | `PM-05` breach |

## 8.3 Pass 3 — reconciliation *(§6)*

| # | Check | Fails when |
|---|---|---|
| `PC-11` | Every SOP step maps to a model step or is declared out of system scope | `PM-17` breach |
| `PC-12` | Every SOP exception row maps to a model exception path | `PM-18` breach |
| `PC-13` | Divergences are recorded as `D-1` defects with both owners named | `PM-19` breach |
| `PC-14` | Requirements realised by the model are bound reciprocally (`T-13`) | `PM-21` breach |

## 8.4 Approval

**Rule `PM-23`.** A model is approved by its **business process owner**, not by IT. The signature
being sought is *"this is how the business will work"*, and only the business can give it.

---

# 9. Production Plan

## 9.1 Sequence

**Rule `PM-24`.** A model is produced **one wave ahead of the build that configures from it**. A
model produced during its own wave is produced under schedule pressure, and the first casualty is
always the exception paths.

| Tranche | Models | Produce by | Consumed by |
|---|---|---|---|
| **T1** | `BPM-001` (`VS-1`), `BPM-010`, `BPM-016` | Before W1 build | M01, M04 configuration; `TS-012` journeys 1–2 |
| **T2** | `BPM-011`, `BPM-013`, `BPM-019` | Before W2 build | M02, M31, M15 |
| **T3** | `BPM-002`, `BPM-012`, `BPM-020`–`BPM-023` | Before W3 build | M03, M16, M19, M20, M41, M50 |
| **T4** | `BPM-004`, `BPM-005`, `BPM-017`, `BPM-018`, `BPM-031` | Before W4 build | M08, M09, M27, M34 |
| **T5** | `BPM-003`, `BPM-014`, `BPM-024`, `BPM-025`, `BPM-032` | Before W5 build | M05, M21–M23, M55–M57 |
| **T6** | `BPM-015`, `BPM-026`, `BPM-028`, `BPM-030`, `BPM-033`, `BPM-034` | Before W6 build | M06, M13, M14, M58–M61, M66 |
| **T7** | `BPM-027` | Before W7 build | M12, M38, M40 |
| **T8** | `BPM-029` | Before W8 build | M18, M48 |

## 9.2 Ownership

| Role | Responsibility |
|---|---|
| **Process Architect** | The five L1 models; the inventory; the reconciliation result |
| **Business Process Owner** (per stream) | L2 model content; approval (`PM-23`) |
| **Business Analyst** | `T-13` binding; identifier resolution |
| **Solution Architect** | `PM-15`/`PM-16` state-model reconciliation |
| **Integration Architect** | Message flows and pool boundaries (`EX-4`) |
| **QA** | Derivation of E2E cases; confirmation that every §4.3 journey has a modelled path |

## 9.3 The as-is question

`SP-002` defines the as-is baseline method and has completed **no** baselines. This document does
**not** require an as-is model per process.

**Rule `PM-25`.** As-is is captured as a **`SP-002` baseline record** — measurements, volumes,
timings, defect rates — not as a diagram. As-is diagrams document a system being replaced, and
consume effort that produces nothing the build uses. The one thing as-is must produce is the
**measured baseline** for the 61 unmeasured KPIs (`SP-002` §4.4), because a baseline can only be
taken before the system changes the operation (`README.md`, `BM-002`).

## 9.4 Throughput and its constraint

The binding constraint is not modelling effort; it is **business process owner availability**.
Rule `PM-23` requires their signature, and `SP-003` `PD-06` requires lanes to be real roles from
`05-04`, which means the people doing the work must be in the room. `CH-005` (Super-User &
Champion Network Charter) is the document that releases them from their day jobs, and it does not
exist. That dependency is recorded as `Q-04`.

---

# 10. Decisions Recorded

| # | Decision | Options | Chosen | Rationale |
|---|---|---|---|---|
| D-01 | Whether to restate `SP-003`'s notation | (a) Restate for completeness; (b) conform and reference | **(b)** | `PG-02`: one document, one purpose. `SP-003` is issued and good; a second notation statement would diverge |
| D-02 | Whether models are authoritative over SOP text | (a) Model wins; (b) `SP-003` `PD-01` stands — text wins | **(b)** | `SP-003`'s reasoning holds: diagrams are not translatable to Bengali without redrawing, and 28 of 34 `SP` files are bilingual |
| D-03 | Which processes to model | (a) All 28 SOPs; (b) trigger-based, `MT-1`–`MT-6` | **(b)** | Modelling a single-module linear process produces a picture of its SOP. 25 of 28 qualify anyway — but by test, not by default |
| D-04 | Diagram storage format | (a) Image; (b) **BPMN 2.0 XML** plus a rendered image | **(b)** | An image cannot be diffed, validated or migrated. This is also the estate's first machine-readable artefact |
| D-05 | As-is modelling | (a) Model as-is per process; (b) baseline records only | **(b)** | As-is diagrams document a system being switched off. The measured baseline is the part that cannot be recovered later |
| D-06 | Cross-module coverage | (a) Model per module; (b) model per process, crossing modules | **(b)** | The missing view is precisely the cross-module one (`RQA-23`). A per-module model reproduces the state machine that already exists |
| D-07 | How to close view divergence | (a) Edit the artefact that is easiest to change; (b) `D-1` defect, both owners, both agree | **(b)** | Editing one side makes the estate look consistent while being less correct — `RQ-004` `TR-07` |
| D-08 | Model approval authority | (a) Design Authority; (b) business process owner | **(b)** | The claim being signed is *"this is how the business will work"* |

---

# 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | Which BPMN tool produces schema-valid 2.0 XML, and is it funded? | Process Architect | **Now** | `PM-05`, `PC-10`; T1 production |
| Q-02 | Who are the five value-stream process owners? `SP-001` names streams, not owners | Programme Director | **Now** | `PM-23` approval for every model |
| Q-03 | Do the 1,590 transition guards get reconciled by the module authors or by the Process Architect? | Design Authority | W1 | §6.3 reconciliation ownership |
| Q-04 | When does `CH-005` release super-users, and at what weekly commitment? | Change Lead | W1 | §9.4 throughput |
| Q-05 | Is a sixth value stream needed for the marketplace, or does it sit inside `VS-1`? | Process Architect | W4 | `BPM-006`–`BPM-009` reservation; `BPM-027` scope |
| Q-06 | Does `M63` (Process Automation & Workflow Orchestration) consume `BPM` models directly, or is a translation step required? | Solution Architect | W3 | `EX-1`–`EX-8` derivation |

---

# 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The inventory names every model required, with a stated trigger for each | §4.2, `MT-1`–`MT-6` |
| AC-02 | All 15 critical journeys have a modelled path | §4.3 |
| AC-03 | `BPM-nnn` swept for collisions before reservation | §3.2, 02:15 (+06) |
| AC-04 | The model record schema carries every lateral link | §3.3, §7.2 |
| AC-05 | Executable-grade is defined as a testable property, not an adjective | §5.2, `PM-10` |
| AC-06 | Gateway conditions are required to be decidable, with worked examples | §5.3, `PM-11` |
| AC-07 | The three-view divergence is stated, measured where measurable, and given a closure rule | §6, `PM-19` |
| AC-08 | Notation is conformed to, not restated | §2.1, §8.1, decision `D-01` |
| AC-09 | Production is sequenced one wave ahead of build, with the throughput constraint named | §9.1, §9.4 |
| AC-10 | Counts reconcile: 5 L1 + 25 L2 = 30, with 3 libraries correctly unmodelled and 4 identifiers reserved | §4.2 |

---

# 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SP-001` | Value streams, hierarchy, stream-to-wave mapping |
| Upstream | `SP-002` | As-is baseline method; `PM-25` |
| Upstream | **`SP-003`** | **The notation standard this document conforms to** |
| Upstream | `SP-004`, `SP-005`, `SP-006` | Approval, escalation and SOD matrices bound at gateways |
| Upstream | `RQ-009` | The rules gateways cite |
| Lateral | `RQ-001` | Requirements realised by model steps (`T-13`) |
| Lateral | `RQ-004` | Link `T-13` and the `D-1`/`D-2` defect taxonomy |
| Lateral | Module §8 state models | Reconciled under `PM-15`, `PM-16` |
| Downstream | `AR-003` | Design derived from models |
| Downstream | `M63`, `AR-009` | Workflow and orchestration configured from models |
| Downstream | `QA-002`, `TS-012` | E2E scenarios derived from `BPM` paths |
| Downstream | `CH-002`, `TR-*` | Training built on the approved To-Be process |
| Downstream | `UX-004` | Interaction design following the modelled flow |

---

# 14. References

**Within this repository**
[`RQ-001`](RQ-001_Software_Requirements_Specification.md) ·
[`RQ-004`](RQ-004_Requirements_Traceability_Matrix.md) ·
[`RQ-008`](RQ-008_Use_Case_and_User_Story_Specification.md) ·
[`RQ-009`](RQ-009_Business_Rules_Specification.md) ·
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md)

**Workspace**
`../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-001`, `SP-002`, **`SP-003`**, `SP-004`, `SP-005`, `SP-006` ·
`../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-007`…`SP-034` ·
`../../1000fix_ERP_Module/03_Modules/*/M*.md` §8, §9, §11, §12 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06` §11

**External**

| Reference | Verified on |
|---|---|
| OMG BPMN 2.0 — Business Process Model and Notation | 2026-08-18 |
| ISO 9001:2015 clause 4.4 — process approach | 2026-08-18 |
| ISO/IEC/IEEE 29148:2018 §6.2, §6.3 | 2026-08-18 |

---

# 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. 30-model inventory with trigger-based selection; `BPM-nnn` reserved; executable-grade standard defined against ISO 9001 §4.4.1; three-view reconciliation specified; findings `RQA-22`, `RQA-23` raised. Conforms to `SP-003`, does not restate it | *Pending — `GV-002`* |

---

*`RQ-007` · Category 01 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
