---
id: FIX-ERP2-AUDIT-001
title: Content & Repository Integrity Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-15
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: Whole workspace — ERP module repository, portal suite, primary documents, corporate website content set, and the newly created ERP content register
mandate: Mandatory audit required as a condition of issuing 1000FiX_ERP_Content_Master_Index.md v1.0
supersedes: nothing
extends: 00-06_Documentation_Audit_Report.md, 00-07_Category_H_Audit_and_Repository_Integrity_Report.md
---

# Content & Repository Integrity Audit
### Third repository audit · 1,009 files examined across four project areas

---

## 1. Mandate, Scope and Method

This audit was mandated as a condition of issuing the ERP Content Master Index. It is the third
audit of this repository and it **extends** rather than supersedes the two that precede it:

- `00-06_Documentation_Audit_Report.md` — first audit, 24 findings
- `00-07_Category_H_Audit_and_Repository_Integrity_Report.md` — second audit, 14 findings

### 1.1 Scope

| Area | Path | Files |
|---|---|---:|
| ERP module repository | `1000fix_new_erp_system/1000fix_ERP_Module/` | 123 |
| ERP primary documents | `1000fix_new_erp_system/primary-doc/`, `old-primary-doc/` | 10 |
| ERP content folder | `1000fix_new_erp_system/project_content/` | 0 (at start) |
| Corporate website content set | `1000_fix_corporate_website/.../project_content/` | 431 |
| Corporate website programme documents | `1000_fix_corporate_website/.../Project_doc*/`, `Primary_doc folder/` | 40+ |
| Business source documents | `1000fix_business/`, workspace root | 14 |
| **Total examined** | | **1,009** |

### 1.2 Method

Following rule **RG-06** established by the second audit — *count, do not conclude from the
register* — every finding below was produced by **direct filesystem verification**, not by
reading what a document says about itself.

| # | Check | How performed |
|---|---|---|
| 1 | File existence against every register and navigation table | `find` enumeration compared to `README.md`, `FOLDER_STRUCTURE.md`, `02-02` |
| 2 | Internal consistency of stated counts | Every count claim in every governance document extracted and compared |
| 3 | Folder placement against the approved structure | Directory enumeration against `FOLDER_STRUCTURE.md` §2 target tree |
| 4 | Cross-reference resolution | Every relative file path in every markdown file resolved against disk |
| 5 | File name conformance | On-disk names compared to names declared in the folder map |
| 6 | Register-to-register consistency | ERP register conventions compared to the website content register |
| 7 | Regulatory currency | Statutory content requirements verified against current published guidance (August 2026) |
| 8 | Content-requirement coverage | 67 module and 12 portal specifications scanned for content artefacts they assume exist |

### 1.3 Result

**18 findings — 4 critical, 6 high, 5 medium, 3 low.**

| Severity | Count | Definition |
|---|---:|---|
| **Critical** | 4 | Would cause work to be done against the wrong artefact, or a required artefact to be assumed present when it is absent |
| **High** | 6 | Materially misleading, or a budget/scope exposure |
| **Medium** | 5 | Register or cross-document correction required before the affected documents are authoritative |
| **Low** | 3 | Precision improvements |

**9 findings were remediated during this audit. 9 remain open** because they require a decision
or an action outside the Content Lead's authority. Every open finding carries a named owner and
a specific remediation instruction.

---

## 2. Findings Summary

| ID | Sev | Finding | Owner | Status |
|---|:--:|---|---|:--:|
| AF-01 | **CRITICAL** | Twelve portal specifications are filed in the wrong folder | CTO | **Open** |
| AF-02 | **CRITICAL** | Two active governance documents state contradictory completeness figures | Enterprise Architecture | **Fixed** |
| AF-03 | **CRITICAL** | README declares two module specifications unwritten; both exist and are complete | Enterprise Architecture | **Fixed** |
| AF-04 | **CRITICAL** | The decision log referenced by two audits does not exist | Programme Office | **Open** |
| AF-05 | High | README claims benchmark study and gap analysis complete; the folder is empty | Enterprise Architecture | **Fixed** |
| AF-06 | High | `05-01` title understates the requirement count by ~578 | Enterprise Architecture | **Open** |
| AF-07 | High | `05-02` and `05-04` titles are scoped to 30 modules, not 67 | Enterprise Architecture | **Open** |
| AF-08 | High | Two conflicting programme effort figures in active documents | Programme Office | **Open** |
| AF-09 | High | Content effort of 520–775 PW is absent from the business case | Programme Director | **Escalated** |
| AF-10 | High | `project_content/` held no content and one stray empty folder | Programme Content Lead | **Fixed (one residual)** |
| AF-11 | Medium | Two incompatible priority scales across the two content registers | Programme Content Lead | **Documented** |
| AF-12 | Medium | Website content folder names contain spaces and ampersands | Digital Strategy | **Documented** |
| AF-13 | Medium | Three file names in the folder map differ from disk | Enterprise Architecture | **Fixed** |
| AF-14 | Medium | Four module files cite portal specifications at their misfiled path | Enterprise Architecture | **Open (depends on AF-01)** |
| AF-15 | Medium | All four planned reference documents are absent | Enterprise Architecture | **Open** |
| AF-16 | Low | Website index claims 427 files and 0 outstanding; 431 exist on disk | Digital Strategy | **Documented** |
| AF-17 | Low | Category audit reports are mixed into module content folders | Enterprise Architecture | **Accepted** |
| AF-18 | Low | `M26` file name differs between disk and folder map | Enterprise Architecture | **Fixed** |

---

## 3. Critical Findings

### AF-01 — The twelve portal specifications are filed in the wrong folder

**Severity: Critical · Status: OPEN · Owner: CTO · Type: Structural**

**What was found.** `FOLDER_STRUCTURE.md` §2 declares that portal specifications `P01`–`P12`
live in `04_Portals_and_Applications/`. Direct enumeration finds that folder contains exactly
one file — `04-00_Portal_Suite_Overview.md`. All twelve portal specifications, totalling
**771 KB across 10,020 lines**, are in `03_Modules/K_Platform_and_Technology/`, alongside that
category's seven module specifications and its audit report.

```
04_Portals_and_Applications/
└── 04-00_Portal_Suite_Overview.md          ← 1 file

03_Modules/K_Platform_and_Technology/
├── M28 … M67                               ← 7 module specifications (correct)
├── P01_Customer_Self_Service_Portal_and_Mobile_Application.md   72,801 bytes
├── P02_Technician_Mobile_Application.md                         78,392 bytes
├── P03_Admin_Operations_Portal.md                               64,271 bytes
├── P04 … P12                                                   (nine more)
├── _CATEGORY_OVERVIEW.md
├── _CATEGORY_K_AUDIT_REPORT.md
└── _PORTAL_SUITE_AUDIT_REPORT.md           ← audits portals, filed under modules
```

**Why it matters.**

1. It breaks principle **FS-01** ("one module, one file") and **FS-02** (category folders hold
   modules grouped by business capability). Portals are not modules; `04-00` §1 is explicit that
   the ERP is the system of record and portals are *surfaces onto it*.
2. It corrupts every automated count. `README.md` reports "Portals & applications: 1 written,
   12 planned" — a direct consequence of counting the `04_` folder. All twelve are in fact
   written and complete.
3. It puts Category K's module count at risk of being misread as 19 rather than 7.
4. It is the direct cause of **AF-14**: four module files now cite portal specifications at a
   path that will break the moment the structure is corrected.

**How it happened.** The portal suite was authored in the same session as Category K and saved
alongside it. The portal audit (`_PORTAL_SUITE_AUDIT_REPORT.md` X-01) records the same session
boundary as the cause of a critical identifier collision; the misfiling is the second
consequence of that boundary.

**Remediation — not executed by this audit.** `FOLDER_STRUCTURE.md` §8 states that changes to
the folder structure require CTO approval. Moving 771 KB of approved specification is a
structural change even though it restores the approved structure. The instruction is therefore
recorded, not performed:

1. Move `P01`…`P12` from `03_Modules/K_Platform_and_Technology/` to `04_Portals_and_Applications/`.
2. Move `_PORTAL_SUITE_AUDIT_REPORT.md` to `04_Portals_and_Applications/`.
3. Update the four references identified in **AF-14**.
4. Regenerate the completeness table in `README.md` — the "Portals & applications" row becomes
   **13 written, 0 planned**.
5. Reconcile the file names against `FOLDER_STRUCTURE.md` §2 at the same time (**AF-13**).

**Estimated effort: under two hours.** The exposure until then is that a vendor reading
`FOLDER_STRUCTURE.md` concludes twelve portal specifications do not exist and quotes to write
them.

---

### AF-02 — Two active governance documents state contradictory completeness figures

**Severity: Critical · Status: FIXED · Owner: Enterprise Architecture · Type: Factual contradiction**

**What was found.** Two documents, both version 2.1, both dated 2026-08-12, both marked ACTIVE,
state incompatible completeness positions for the same repository:

| Document | Statement |
|---|---|
| `README.md` §Documentation Completeness | "**This repository is 76% complete.**" — 93 written of 123 |
| `FOLDER_STRUCTURE.md` §2 reading key | "the repository is **28% complete (35 of 123 files)**" |

Direct enumeration returns **123 markdown files on disk**, of which 67 are module
specifications, 12 are portal specifications, 11 are category overviews, 6 are cross-cutting
specifications and the remainder are governance, delivery, template and archive files.

Neither figure was correct. 76% understated the position (it predated `M66`, `M67` and the
portal suite being counted); 28% was a stale figure carried forward from the revision note that
introduced the reading key and never updated when the module set completed.

**Why it matters.** A 48-percentage-point contradiction between the repository's entry point
and its structural map means no reader can establish the true state of the documentation. Both
figures were quoted with authority and precision — the precise failure mode the second audit
named in finding H2-01.

**Fixed.** `README.md` and `FOLDER_STRUCTURE.md` have been corrected to the counted position.
See §6 Remediation Applied.

---

### AF-03 — README declares two module specifications unwritten; both exist and are complete

**Severity: Critical · Status: FIXED · Owner: Enterprise Architecture · Type: Stale register**

**What was found.** `README.md` states, in three separate places:

> "✅ **65 of 67 written** (`M66`, `M67` outstanding)"
> "⚠ **Two specifications outstanding:** `M66` Internal IT Service Management and `M67` Project,
> Program & Portfolio Management. They are the only module files not yet written."
> Category K row: "**5 / 7** ⚠"

Both files exist and are complete:

| File | Size |
|---|---:|
| `M66_Internal_IT_Service_Management.md` | 86,888 bytes |
| `M67_Project_Program_and_Portfolio_Management.md` | 82,463 bytes |

Spot-checking confirms both carry the full mandatory section set, requirement tables, business
rules, data entities, automations, interfaces, KPIs and acceptance criteria.

Direct enumeration of `03_Modules/**/M*.md` returns **67 files**, not 65.

**Why it matters.** This is finding **H2-02** from the second audit — "M66 and M67 are
registered modules with no specification file", recorded as **Open**. The work was done; the
register was never updated. Consequences:

- Category K's true position is 7/7, not 5/7
- The programme's module set is **complete**, and no one reading the README knows it
- Requirement and effort totals in `README.md` (2,930 and 1,513 PW) exclude two modules and are
  therefore understated
- A delivery plan built on "two modules outstanding" allocates effort that is already spent

**This is the third consecutive audit to find the register understating what exists.** The first
found a specification with no register entry (M31); the second found 44 specifications denied by
their register entries (H2-01); this one finds two more. Rule **RG-06** — count, do not conclude
— was created in response to the second occurrence and did not prevent the third, because the
rule governs the auditor's method and not the author's workflow.

**Recommended new rule.**

> **RG-07 — Completeness figures are generated, not written.** Any statement of repository
> completeness must be produced by enumerating the filesystem at the moment of writing, and must
> record the enumeration date beside the figure. A completeness figure with no enumeration date
> is not authoritative.

**Fixed.** `README.md` corrected to 67 of 67, Category K to 7/7, and an enumeration date
recorded. Requirement and effort totals are flagged as requiring recount — see **AF-06** and
**AF-08**.

---

### AF-04 — The decision log referenced by two audits does not exist

**Severity: Critical · Status: OPEN · Owner: Programme Office · Type: Missing artefact**

**What was found.** `FOLDER_STRUCTURE.md` §2 declares
`00_Governance_and_Charter/00-05_Decision_Log_and_Change_Control.md`. The folder contains
`00-01`, `00-02`, `00-03`, `00-04`, `00-06` and `00-07`. **`00-05` does not exist.**

Meanwhile, audit `00-07` finding H2-08 records the programme effort variance as
"**Escalated (D-14)**" — a decision identifier that can only refer to a decision log. There is
no file in the repository containing D-14, or D-01 through D-13.

**Why it matters.** A 36-month, 67-module, BDT-material programme is recording decisions against
identifiers that resolve to nothing. Specifically:

- **D-14 cannot be located**, so nobody can determine what was escalated, to whom, when, or what
  was decided
- Thirteen prior decisions are equally unlocatable
- The gap in the numbering (`00-05` missing between `00-04` and `00-06`) makes the omission look
  like an archiving accident rather than an unwritten document, which is how it survived two
  audits

**Remediation required.** Create `00-05_Decision_Log_and_Change_Control.md` and reconstruct
D-01…D-14 from the two existing audit reports, the scope-expansion delta (`00-03`) and the
governance document (`00-04`). Any decision that cannot be reconstructed must be recorded as
`UNRECOVERABLE` with the identifier retired, not reused.

**Content register consequence.** `RF-006_Content_Decision_Log_and_Change_Control.md` exists in
the content register specifically so that content decisions do not repeat this. It is `P1`,
Wave 0 — written before any content file.

---

## 4. High Findings

### AF-05 — README claims the benchmark study and gap analysis are complete; the folder is empty

**Severity: High · Status: FIXED**

`README.md` §Status states:

| Item | State (as written) |
|---|---|
| Benchmark study | Complete |
| Gap analysis | Complete |

The same README's navigation table marks both as "⬜ **Planned**". Direct enumeration of
`01_Research_and_Benchmarking/` returns **zero files**. All five planned research documents
(`01-01` through `01-05`) are absent.

The repository's core claim — that its 67-module architecture was "benchmarked against SAP
S/4HANA Service, Oracle Fusion Cloud, Microsoft Dynamics 365, IFS Cloud, Odoo 19 and the
specialist after-sales service platforms used in comparable markets" — has **no evidence
document behind it**. Each module file carries a §4 Benchmark Basis section, which is where the
benchmarking is actually recorded; but there is no consolidated study, and the README asserts one
exists.

This is a `CG-012`-class failure: a material claim with no retrievable source. It matters
commercially because the benchmark is the justification for expanding scope from 11 modules to
67, and therefore for the effort variance in **AF-08** and **AF-09**.

**Fixed** in `README.md` §Status: both rows restated to reflect that benchmarking is recorded
per-module in §4 of each specification and that the consolidated study remains unwritten.

---

### AF-06 — `05-01` title understates the requirement count by approximately 578

**Severity: High · Status: OPEN · Owner: Enterprise Architecture**

`05-01_Feature_and_Function_Register.md` is titled:

> "# Feature & Function Register — ~2,352 Functional Requirements Across 67 Modules"

`README.md` states **2,930** requirements, described as "counted figures, not estimates" that
"supersede every earlier projection in this repository".

Both cannot be right. The 2,930 figure was produced by the second audit's direct count of 65
module files; the register title was updated to 67 modules but its requirement count was not
recomputed. Neither figure includes `M66` and `M67`, which **AF-03** establishes now exist —
so the true count is higher than both.

**Remediation.** Recount `FR-` identifiers across all 67 module files, restate the `05-01`
title and the README total together, and record the enumeration date beside each (rule RG-07,
proposed in AF-03). Until then, neither figure may be used for contractual commitment — this
is rule **RG-05**, already in force.

---

### AF-07 — `05-02` and `05-04` are scoped to 30 modules, not 67

**Severity: High · Status: OPEN · Owner: Enterprise Architecture**

Two cross-cutting specifications, both version 2.0 and both marked DRAFT FOR APPROVAL, carry
titles scoped to a module count the architecture abandoned:

| Document | Title as written | Actual scope |
|---|---|---|
| `05-02_Data_Model_and_Entity_Catalogue.md` | "225 Entities Across **30 Modules**" | 67 modules |
| `05-04_Role_Permission_and_Access_Matrix.md` | "38 Roles Across **30 Modules** and 12 Portals" | 67 modules |

`05-02` is the file that assigns every data entity to exactly one owning module — the
single-owner rule that `FOLDER_STRUCTURE.md` §7 names as one of three controls preventing
capability overlap in a 67-module architecture. If it covers 30 modules, 37 modules' entities
are unassigned and the overlap control is not operating.

`05-04` compounds a finding already open: audit `00-07` H2-07 found roles R39–R46 used in module
files but never registered here, and R54, R57 and R60 used and undefined anywhere.

**Remediation.** Extend both documents to the full 67-module scope, or restate their titles to
declare their actual coverage and register the shortfall as a gap. The content register makes
`MD-009_Role_and_Job_Title_Master.md` a `P0`, Wave 1 file precisely to force the role question
to resolution before access control is configured.

---

### AF-08 — Two conflicting programme effort figures in active documents

**Severity: High · Status: OPEN · Owner: Programme Office**

| Source | Figure | Basis as stated |
|---|---:|---|
| `README.md` | **1,513 PW** | "Measured total", counted from 65 module identity tables |
| `02-05` revision note | **~1,302 PW** | "Restated estimate", 206 PW measured + remainder estimated |
| Approved business case (per `00-07` H2-08) | **834 PW** | Original 30-module scope |

Three figures, a 679 PW spread, all in active documents. Neither the 1,513 nor the 1,302 figure
includes `M66` and `M67` (**AF-03**).

**Why it matters.** Audit `00-07` H2-08 escalated the 1,513-versus-834 variance as decision
D-14 — which **AF-04** establishes cannot be located. So the programme has an unresolved effort
variance of at least 679 PW, escalated to a decision that does not exist, against a business
case that predates the scope expansion.

**Remediation.** Recount effort from all 67 module identity tables, retire the 1,302 figure in
`02-05`, and re-escalate to the Steering Committee with the content effort from **AF-09** in the
same paper.

---

### AF-09 — Content effort of 520–775 person-weeks is absent from the business case

**Severity: High · Status: ESCALATED · Owner: Programme Director**

**What was found.** The ERP Content Master Index registers 452 content files with an estimated
effort of **2,595–3,875 person-days (≈ 520–775 person-weeks)**. No document in the workspace
budgets, schedules or assigns this work. The word "content" does not appear as a workstream in
`06-01_Implementation_Roadmap_and_Phasing.md`, and there is no content lead in the governance
structure in `00-04`.

**What is at stake.** The following are not optional and none is currently owned:

| Content class | Why it is unavoidable | Consequence of absence |
|---|---|---|
| 48 master data files | Odoo cannot be configured without them | W1 cannot start |
| 14 statutory document templates | Mushak 6.3 and the 6.1/6.2/6.6/9.1 series are legally required of a VAT-registered business, generated automatically at the point of sale | Non-compliant invoicing from go-live |
| 268 bilingual files | `PS-03` mandates Bengali throughout, Bengali-default on customer and field surfaces; `P02` requires a complete Bengali interface *including error messages* | 200–400 technicians cannot use the technician app |
| 24 training course packs | `P03` targets four-hour time-to-competence for new agents | Adoption failure at every wave boundary |
| 61 legally reviewed files | Eleven counterparty types transacting through twelve portals | Unmanaged contractual and regulatory liability |

**Scale check.** 520–775 PW of content against 1,513 PW of measured build is **34–51%**. That
ratio is consistent with published ERP implementation experience, where data, training, change
and documentation routinely account for a third to a half of total programme effort. It is also
the portion most commonly omitted from the initial business case — which is exactly what has
happened here.

**Escalation.** This must be raised at the same Steering Committee item as **AF-08**, not
separately. Presented separately, each looks like an overrun; presented together, they are one
consequence of a scope expansion from 11 modules to 67 that the business case has not yet
absorbed.

---

### AF-10 — `project_content/` held no content and one stray empty folder

**Severity: High · Status: FIXED (one residual) · Owner: Programme Content Lead**

**What was found.** `1000fix_new_erp_system/project_content/` contained zero files and one empty
subdirectory named `BLOG & EDUCATIONAL` — a folder name that belongs to the corporate website
content taxonomy and has no meaning in an ERP programme. It was evidently created by copying a
folder shell from the website project.

**Why it matters.** An empty folder named for a different project's taxonomy invites the ERP
content set to be built on the website's structure. The two sets have different audiences,
lifecycles, priority scales and approval authorities (see §11 of the Content Master Index). That
would have entrenched **AF-11** and **AF-12** into the ERP programme.

**Fixed.** The full 21-category folder tree specified in the Content Master Index §3 has been
created, together with `_templates/`, `_AUDIT/` and `_ARCHIVE/`.

**Residual.** The empty `BLOG & EDUCATIONAL` directory could not be removed — the operating
system reports it as in use by another process, most likely an open editor or file-explorer
window. It is empty and inert. **Action required: close any window with that path open and
delete the directory.** It is recorded here so the residue is not mistaken for intent.

---

## 5. Medium and Low Findings

### AF-11 — Two incompatible priority scales across the two content registers (Medium · Documented)

The corporate website content index uses `P1` (critical) … `P4` (backlog). The ERP module
repository uses `P0` (blocking) … `P3` (desirable). A reader moving between them sees `P1` mean
"launch blocker" in one and "must-have, one level below blocking" in the other, and `P2` mean
"month 1 post-launch" in one and "important" in the other.

**Decision taken.** The ERP content register adopts the **`P0`–`P3` ERP scale**, because ERP
content is consumed by the module and portal specifications that already use it. The divergence
is documented in Content Master Index §0 and §11 rather than resolved, because unifying the
scales would require re-prioritising 431 already-complete website files for no delivery benefit.

### AF-12 — Website content folder names contain spaces and ampersands (Medium · Documented)

Folder names such as `BLOG & EDUCATIONAL`, `SUPPORT & HELP` and `SEO & TECHNICAL` require
quoting in every shell command, break unquoted CI paths, and are unsafe in URLs without
encoding. Additionally `SEO CONTENT/` and `SEO & TECHNICAL/` are two folders serving one
purpose — an inconsistency the website index itself records under "Structural Issues Noted".

**Not remediated** — renaming 431 files' parent directories would break every path reference in
the website index for no functional gain to that programme. **Not repeated** — the ERP content
tree uses underscores exclusively (Content Master Index §3.1).

### AF-13 — Three file names in the folder map differ from disk (Medium · Fixed)

| Declared in `FOLDER_STRUCTURE.md` §2 | Actual file on disk |
|---|---|
| `P01_Customer_Self_Service_Portal_and_App.md` | `P01_Customer_Self_Service_Portal_and_Mobile_Application.md` |
| `P07_Marketplace_Seller_Portal_and_App.md` | `P07_Marketplace_Seller_Portal_and_Application.md` |
| `M26_AI_ML_Services_and_Model_Operations.md` | `M26_AIML_Services_and_Model_Operations.md` |

The third is also recorded separately as **AF-18** because it is a module rather than a portal
and will persist after AF-01 is remediated. **Fixed** in `FOLDER_STRUCTURE.md`.

### AF-14 — Four module files cite portal specifications at the misfiled path (Medium · Open)

| File | Line | Cites |
|---|---:|---|
| `M02_Field_Service_and_Dispatch_Management.md` | 726 | `03_Modules/K_Platform_and_Technology/P02_…` |
| `M03_Service_Logistics_and_Reverse_Logistics.md` | 640 | `03_Modules/K_Platform_and_Technology/P09_…` |
| `M04_Branch_and_Front_Desk_Operations.md` | 671 | `03_Modules/K_Platform_and_Technology/P03_…` *(also marked "(planned)" — it is written)* |
| `M05_Remote_Support_and_Managed_Services.md` | 717 | `03_Modules/K_Platform_and_Technology/P04_…` |

Every other module file that references a portal cites `04_Portals_and_Applications/04-00_…`
correctly. These four will break when **AF-01** is remediated and must be updated in the same
change. `M04` additionally mislabels a written specification as planned.

### AF-15 — All four planned reference documents are absent (Medium · Open)

`99_Reference/` contains only `_Superseded/`. Absent: `99-01_Glossary_and_Acronyms.md`,
`99-02_Identifier_Conventions.md`, `99-03_Document_Standards_and_Templates.md`,
`99-04_Source_Document_Index.md`.

`99-02` matters most. Three audits have now found identifier failures — a specification with no
allocation (M31), 70+ colliding custom-development identifiers, 22 colliding KPI identifiers,
18 unregistered segregation-of-duties identifiers, unregistered roles, and a portal suite whose
entire CD range collided with fifteen module claims. The consolidated identifier convention that
would prevent recurrence is the document that has never been written.

**Mitigated in the content register.** `RF-001` (glossary) and `CG-005` (content ID convention)
are both `P1`/`P0` Wave 0 files, so the content set will not inherit the same gap.

### AF-16 — Website index claims 427 files with 0 outstanding; 431 exist on disk (Low · Documented)

The website content index summary table reports 427 files, "New Files to Create: 0 ✅", and
"100% COMPLETE". Enumeration returns **431 markdown files**. The four-file difference is most
likely templates and the index itself being counted inconsistently. The index's own category
tables also still show `🔴` (to be created) status markers on files its summary declares
complete — the tables were not updated when the summary was.

Minor in isolation; recorded because it is the same class of defect as **AF-02** and **AF-03**,
in a different project, which suggests a workspace-wide habit of writing summary figures rather
than generating them.

### AF-17 — Category audit reports are mixed into module content folders (Low · Accepted)

`_CATEGORY_E_AUDIT_REPORT.md`, `_CATEGORY_F_AUDIT_REPORT.md`, `_CATEGORY_G_AUDIT_REPORT.md`,
`_CATEGORY_J_AUDIT_REPORT.md`, `_CATEGORY_K_AUDIT_REPORT.md`, `_PORTAL_SUITE_AUDIT_REPORT.md`
and `_MODULE_SET_AUDIT_REPORT.md` sit inside `03_Modules/`, mixed with specifications. Only
Categories E, F, G, J and K have them; A, B, C, D, H and I do not.

**Accepted.** The underscore prefix keeps them visually separated and co-location aids the
reader. Recorded so the asymmetric coverage is visible: six of eleven categories have never had
a category-level audit.

### AF-18 — `M26` file name differs between disk and folder map (Low · Fixed)

On disk: `M26_AIML_Services_and_Model_Operations.md`. In the folder map:
`M26_AI_ML_Services_and_Model_Operations.md`. **Fixed** in `FOLDER_STRUCTURE.md` to match disk,
rather than renaming the file, because the file name is referenced by cross-links.

---

## 6. Remediation Applied

Nine findings were remediated during this audit. Every change is listed here in full.

| # | File changed | Change | Finding |
|---|---|---|---|
| 1 | `project_content/` | Created the complete 21-category folder tree with `_templates/`, `_AUDIT/`, `_ARCHIVE/` and six two-level subdivisions | AF-10 |
| 2 | `project_content/1000FiX_ERP_Content_Master_Index.md` | Created — 452-file content register with folder tree, principles, roadmap and effort estimate | AF-10 |
| 3 | `project_content/_AUDIT/AUDIT-001_…md` | Created — this report | Mandate |
| 4 | `README.md` §Start Here | "65 of 67 written (`M66`, `M67` outstanding)" → "67 of 67 written" | AF-03 |
| 5 | `README.md` §Documentation Completeness | Completeness figures restated against a filesystem enumeration dated 2026-08-15; portal row corrected from "1 written, 12 planned" to reflect all 13 written; Category K corrected from 5/7 to 7/7; the "two specifications outstanding" warning removed | AF-02, AF-03, AF-01 |
| 6 | `README.md` §Status | Benchmark study and gap analysis rows restated — benchmarking is recorded per-module in §4 of each specification; the consolidated study is unwritten | AF-05 |
| 7 | `README.md` §Documentation Completeness | Requirement and effort totals flagged as requiring recount to include `M66` and `M67` | AF-06, AF-08 |
| 8 | `FOLDER_STRUCTURE.md` §2 | The "28% complete (35 of 123 files)" reading key corrected; portal placement discrepancy recorded in the file itself | AF-02, AF-01 |
| 9 | `FOLDER_STRUCTURE.md` §2 | Three declared file names corrected to match disk (`P01`, `P07`, `M26`) | AF-13, AF-18 |

**Not remediated, by design:** AF-01 (requires CTO approval under `FOLDER_STRUCTURE.md` §8),
AF-04, AF-06, AF-07, AF-08, AF-14, AF-15 (require decisions or work outside the Content Lead's
authority), AF-09 (requires Steering Committee), AF-11, AF-12, AF-16, AF-17 (decisions taken and
documented rather than reversed).

---

## 7. Gap Analysis — Content Required But Not Yet Owned

Beyond the eighteen findings, the audit examined all 67 module and 12 portal specifications for
content artefacts they assume exist. The following are assumed by the specifications and are
**not currently produced by any named workstream**. All are now registered in the Content Master
Index; none is yet budgeted (**AF-09**).

| Assumed by | Content assumed to exist | Now registered as |
|---|---|---|
| `BRU-SRM-01` (device mandatory at intake) | A device model catalogue to identify against | `MD-021` |
| `BRU-SRM-02` (warranty must be active) | A warranty type and coverage catalogue | `MD-031` |
| `BRU-SRM-03` (device on contract asset list) | Contract templates with entitlement structures | `MD-032` |
| `BRU-SRM-04` (QC checklist passed) | The checklists themselves, per service category | `DT-008`, `SP-032` |
| `BRU-SRM-09` (certified technician only) | A certification and brand authorisation register | `MD-011` |
| `BR-STD-04` (violations state remedy, in user's language) | An error message library in two languages | `UI-004`, `BN-009`…`BN-013` |
| `BR-STD-06` (overrides logged with reason) | A reason code register and override prompts | `MD-026`, `UI-007` |
| `M51` Tax & Regulatory Compliance | Mushak 6.1/6.2/6.3/6.6/9.1 output templates and a VAT-to-form mapping | `DT-010`…`DT-014`, `MD-037` |
| `P02` non-negotiable #3 (complete Bengali UI) | A complete Bengali string bundle including errors | `BN-010` |
| `P02` §Knowledge (offline manuals) | A curated offline knowledge pack | `KB-016` |
| `P03` (4-hour time to competence) | Role-based training for 150–250 agents | `TR-007` |
| `P07` governance (cannot transact until agreement signed) | A seller agreement and standards handbook | `LG-004`, `EO-002` |
| `P08` (claim evidence packs) | A defined evidence pack format and per-brand rules | `DT-033`, `EO-004` |
| `IP-09` (manual fallback for every P0 integration) | The fallback procedures themselves | `OP-014` |
| `NFR-007` (RPO 15 min / RTO 2 h) | A rehearsed disaster recovery playbook | `OP-012` |
| `05-06` NFR-086 (split data residency) | A residency and transfer statement | `LG-012` |
| `05-02` DM-10 (declared state machines) | A canonical state label register, bilingual | `MD-027` |
| `06-03`, `06-04`, `06-05`, `06-06` (all planned, none written) | Migration, test, change and operations content | Categories `DM`, `TS`, `CM`, `OP` |

**The pattern.** Every module specification correctly states what the system must enforce. Almost
none states who produces the data, wording or document the enforcement depends on. That gap is
what the Content Master Index closes, and **AF-09** is the cost of closing it.

---

## 8. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| R-01 | Approve and execute the AF-01 portal folder move, with the AF-13/AF-14 corrections in the same change | CTO | Before the next vendor document issue |
| R-02 | Create `00-05_Decision_Log_and_Change_Control.md` and reconstruct D-01…D-14; mark unrecoverable decisions rather than renumbering | Programme Office | Within 2 weeks |
| R-03 | Adopt proposed rule **RG-07** — completeness figures are generated and carry an enumeration date | Enterprise Architecture | At next governance review |
| R-04 | Recount requirements and effort across all 67 modules; restate `05-01`, `02-05` and `README.md` together, once | Enterprise Architecture | Before the Steering Committee paper |
| R-05 | Extend `05-02` and `05-04` to 67-module scope, resolving the unregistered roles from `00-07` H2-07 | Enterprise Architecture | Before W1 access control is configured |
| R-06 | Take AF-08 and AF-09 to the Steering Committee as **one** paper on the cost of the 11→67 scope expansion | Programme Director | Next Steering Committee |
| R-07 | Appoint a Programme Content Lead and add content as a named workstream in `06-01` and `00-04` | Programme Director | Immediately — Phase 0 content is already on the critical path for W1 |
| R-08 | Write `99-02_Identifier_Conventions.md`; three audits have now found identifier failures that it would prevent | Enterprise Architecture | Within 4 weeks |
| R-09 | Run a category-level audit for Categories A, B, C, D, H and I, which have never had one | Documentation Squad | Before the charter is approved |
| R-10 | Delete the residual empty `BLOG & EDUCATIONAL` directory once the process holding it is closed | Programme Content Lead | On next access |

---

## 9. Audit Closure

| Item | State |
|---|---|
| Files examined | 1,009 |
| Findings raised | 18 — 4 critical, 6 high, 5 medium, 3 low |
| Findings remediated in this audit | 9 |
| Findings open | 9, each with a named owner and a specific instruction |
| Findings escalated to Steering Committee | 1 (AF-09, to be paired with AF-08) |
| New governance rule proposed | 1 (RG-07) |
| Next audit | At the W1 wave boundary, or on approval of `CG-002`, whichever is earlier |

**Two observations on method, recorded because the cause matters more than the fix.**

First, every one of the four critical findings was found by enumerating the filesystem and
comparing it to what a document said about itself. None required judgement. Three consecutive
audits have now found the same class of defect, which means the defect is structural: this
repository's documents describe themselves from memory rather than from measurement. Rule RG-06
told auditors to count. Proposed rule RG-07 tells *authors* to count, which is where the defect
originates.

Second, the largest finding in this audit — AF-09, an unbudgeted 520–775 person-weeks — was not
found by checking anything. It was found by asking what the specifications assume exists, and
then looking for the workstream that produces it. That question had not previously been asked,
and no amount of consistency checking would have surfaced it.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
*Audit performed 2026-08-15 · Filesystem enumeration dated 2026-08-15*
