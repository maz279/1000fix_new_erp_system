---
id: FIX-ERP2-M<nn>
module_id: M<nn>
module_code: <XXX>
module_name: <Full Module Name>
category: <A–K> — <Category Name>
project: 1000FiX ERP System v2.0
version: 1.0
date: <YYYY-MM-DD>
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: <Role, from the 05-04 register>
system_owner: <Squad>
priority: P0 | P1 | P2 | P3
wave: W<n>
---

# M<nn> — <Full Module Name>
### Category <X> · Code `<XXX>` · <Existing (retained) | Existing (re-scoped) | ★ New in v2.1>

---

> **How to use this template.** This is the **house 19-section structure**. Every one of the 85
> specifications in `03_Modules` conforms to it; a new module that does not will fail the
> documentation gate. Section numbers and titles are fixed — do not renumber, merge or omit a
> section. Where a section genuinely does not apply, keep the heading and state why in one line.
>
> **Before you write a single identifier, read §0 below.** Most defects found in the August 2026
> audits were identifier-space violations, not content errors.

---

## 0. Identifier Rules — Read First

`FR-`, `BRU-` and `AUT-` are **module-local** and prefixed with this module's code. Everything
else is **programme-wide** and must already exist in its owning register before you use it
(rule **RG-01**, extended).

| Space | Scope | Allocating authority | Rule |
|---|---|---|---|
| `FR-<CODE>-nnn` | Module-local | `05-01` §1.3 | Permanent. A withdrawn ID is **retired, never reissued** (RG-02) |
| `BRU-<CODE>-nn` | Module-local | This file | Classify each rule H / A / S / C |
| `AUT-<CODE>-nn` | Module-local | This file | Every automation needs a declared failure behaviour |
| `KPI-nnn` | **Programme-wide** | Programme KPI register | Do **not** allocate locally. A shared metric must carry a note naming the co-owning module |
| `CD-nnn` | **Programme-wide** | `02_Architecture/02-05` | Do **not** allocate locally. 48 identifiers currently collide — see any module's §16.2 warning |
| `R nn` (roles) | **Programme-wide** | `05_Cross_Cutting_Specifications/05-04` | R01–R38 registered; R39–R50 introduced by modules and **awaiting registration**. Never reuse an ID for a different role |
| `SOD-nn` | **Programme-wide** | `05-04` | SOD-01…12 registered; 13–30 used but unregistered |
| `NFR-nnn` | **Programme-wide** | `05-06` | Cite, do not invent |

**RG-06 — count, do not consult.** Every figure describing what this file contains
(requirement count, effort, entity count) must be **counted from this file at the time of
writing**. A number stated in a register is not evidence. The requirement count is the number of
**requirement rows**, not the highest allocated identifier — that distinction caused the largest
finding in both repository audits.

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M<nn> |
| **Module code** | `<XXX>` |
| **Category** | <A–K> — <Category Name> |
| **Status** | Existing (retained) / Existing (re-scoped — <what moved and where>) / ★ New |
| **Priority** | **P0** — cannot be descoped / P1 / P2 / P3 |
| **Delivery wave** | W<n> (Months <x>–<y>) |
| **Business owner** | <Role> |
| **System owner** | <Squad> |
| **Delivery layers** | L1 Odoo `<module>` · L2 OCA `<module>` · L5 custom |
| **Custom modules** | `cd_<name>`, … |
| **Requirement range** | FR-<XXX>-001 … FR-<XXX>-nnn |
| **Requirement count** | **<n>** *(measured <YYYY-MM-DD>)* |
| **Effort estimate** | **<n> person-weeks** *(measured)* |
| **Depends on** | M<nn> <Name> · … |
| **Depended on by** | M<nn>, … *(must reciprocate — see §0 and the check below)* |

> **Reciprocity (RG-04).** Every module named in **Depends on** must name this module in its own
> **Depended on by**, and vice versa. A blanket phrase — *"All 66 other modules and all 12
> portals"* — satisfies the rule for genuine platform modules only.

---

## 2. Purpose

> One paragraph, in plain language, stating what this module is for and why the business needs
> it. Written so a branch manager understands it, not only an architect.

### Why It Exists

<2–4 sentences of business justification, traced to evidence — not to opinion.>

### Evidence Basis

| Source | What It Establishes |
|---|---|
| <Workspace document · section> | <the requirement or commitment it evidences> |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree. If §3.2 says a
> capability belongs to another module, that module's §3.1 must claim it.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | … |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| … | **M<nn>** <Name> | … |

### 3.3 Shared Concepts

| Concept | This Module's Role | Owning Module |
|---|---|---|
| … | Reads live / writes via API / consumes event | M<nn> |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| SAP S/4HANA <component> | … | … | … |
| Oracle Fusion Cloud | … | … | … |
| Microsoft Dynamics 365 | … | … | … |
| IFS Cloud | … | … | … |
| Odoo 19 / OCA `<module>` | … | … | … |
| Specialist after-sales platforms | … | … | … |

**Design position.** <One paragraph on where 1000FiX deliberately differs from the benchmark and
why — usually Bangladesh context, cost discipline, Bengali-first interfaces, or field conditions.>

---

## 5. Functional Areas & Features

### 5.1 <Functional Area Name>

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-<XXX>-001 | … | … | **P0** | L5 |

*(Repeat per functional area. Every requirement must be independently testable.)*

> **Retired requirement identifiers.** *(Include this block only if identifiers inside the
> allocation were never issued.)* <n> identifiers inside `FR-<XXX>-001 … <hi>` were never issued
> and are **retired, not reissued**, under RG-02: <list>. The measured count is **<n>**.

---

## 6. Technical Functions

Engineering behaviours the module must exhibit. Not user-visible, but they determine whether the
module survives production.

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Idempotency** | … |
| T-02 | **Concurrency** | … |
| T-03 | **Transactional outbox** | Every state change writes its domain event in the same transaction |
| T-…  | **Performance envelope** | <p95 latencies and volume ceilings> |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M<nn> |
|---|---|---|
| **<Role>** | … | … |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| … | … | … |

> Every monetary figure must trace to `06-02` or the Scope Charter. Where no baseline exists,
> say so and state no number — an absolute target against an unmeasured baseline cannot be
> assessed as met or missed (audit finding H2-10).

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|

---

## 8. Lifecycle & State Model

```
<state machine, where this module owns one>
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-<XXX>-01 | … | **H** | <Role> |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.<name>` | `fix_<name>` | … | … |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.<name>` | M<nn> | Live read via API / event projection |

> **Name the owner's entity exactly.** A referenced entity must appear verbatim in the owning
> module's §10.1. 255 references across the estate currently name entities their declared owner
> does not define — the single largest technical defect found in the August 2026 audit. Check
> before you write.

---

## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-<XXX>-01 | … | … | **<never leave blank>** |

---

## 12. Interfaces

### 12.1 Upstream — M<nn> Consumes

| Source | What | Mechanism |
|---|---|---|
| M<nn> | … | Event `<name>` / REST `<endpoint>` |

### 12.2 Downstream — M<nn> Provides

| Consumer | What | Mechanism |
|---|---|---|

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `<aggregate>.<past_tense_verb>` | … | M<nn>, … |

> **Contract symmetry.** Every event named in another module's §12.1 must appear here. Every
> event here should have at least one declared consumer.

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R<nn> <Name — exactly as registered in `05-04`> | C R U D A | own / branch / zone / entity / all |

**Field-level restrictions:** <fields visible only to named roles>
**Segregation of duties:** <incompatible combinations, citing SOD-nn>

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|

---

## 15. KPIs

| KPI ID | Metric | Baseline | W<n> Target | W<n> Target |
|---|---|---|---|---|
| KPI-<nnn> | … | <or **unmeasured**> | … | … |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `<module>` | <%> |
| L2 | OCA `<module>` | <%> |
| L5 | `cd_<name>` | <%> |

### 16.2 Custom Development

> ⚠ CD identifiers are **provisional** until allocated by `02_Architecture/02-05`. Do not create
> a build backlog item from an identifier in this table until 02-05 has issued it.

| CD ID | Component | Type | Effort |
|---|---|---|---|

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|

> **Wave check.** No prerequisite may land in a later wave than this module. If it does, either
> the wave is wrong or the dependency is not a true prerequisite — say which, explicitly.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | … | … |

**Definition of done:** all criteria in `02_Architecture/02-02` §7 plus the module-specific
criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | … | <Role> | W<n> build |

---

## 19. References

**Internal**
`03_Modules/<X>_<Category>/_CATEGORY_OVERVIEW.md` ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-02_Data_Model_and_Entity_Catalogue.md` · `05-04_Role_Permission_and_Access_Matrix.md` ·
`05-05_Business_Rules_and_Automation_Catalogue.md` ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

> Verify every path resolves before issuing. Nine module files carried references to superseded
> filenames until the August 2026 audit corrected them.

**Workspace evidence**
<BRD / URD / SOW / Company Profile sections actually relied on>

**External benchmark**
<Products and standards actually consulted, each with a verification date where regulatory>

---

*Module M<nn> · Category <X> · 1000FiX ERP System v2.0 · CONFIDENTIAL*
