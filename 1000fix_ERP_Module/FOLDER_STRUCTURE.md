---
id: FIX-ERP2-STRUCT
title: Folder Structure & Repository Map
project: 1000FiX ERP System v2.0
version: 2.2
date: 2026-08-15
status: ACTIVE
classification: CONFIDENTIAL
last_enumerated: 2026-08-15
revision_note: "v2.2 applies audit AUDIT-001 findings AF-01, AF-02, AF-13, AF-18"
---

# Folder Structure & Repository Map
# 1000FiX ERP System v2.0 — Module Documentation Repository

---

## 1. Design Principles

| # | Principle | Consequence |
|---|---|---|
| FS-01 | **One module, one file** | Every ERP module has exactly one authoritative specification file. No module is described in two places. |
| FS-02 | **Category folders, not pillar folders** | Modules are grouped by business capability category (A–K), which is stable, rather than by delivery wave, which changes. |
| FS-03 | **Numbered prefixes for ordering** | Folders and cross-cutting documents carry numeric prefixes so file listings sort into reading order. |
| FS-04 | **Module IDs never change** | `M01`–`M67` are permanent. A module may be renamed or re-scoped; its ID and file name stem persist. |
| FS-05 | **Cross-cutting content lives once** | Data model, integrations, roles, rules, NFRs are maintained in `05_Cross_Cutting_Specifications/`, referenced from module files, never duplicated into them. |
| FS-06 | **Superseded content is archived, not deleted** | `99_Reference/_Superseded/` retains earlier drafts for traceability, clearly marked. |
| FS-07 | **Every folder has an overview** | Each module category folder carries a `_CATEGORY_OVERVIEW.md` explaining its scope and boundaries. |
| FS-08 | **Templates are enforced** | `03_Modules/_MODULE_TEMPLATE.md` defines the mandatory section set for every module file. |

---

## 2. Complete Tree

> **Revision 2.2 — audit findings H-06, AF-01, AF-02, AF-13, AF-18.** The tree below is the
> **target** structure. It shows both written and planned files without distinction, which
> caused `README.md` to link to five files that do not exist.
>
> **Reading key:** files marked **✅** exist. Everything else is **planned**.
>
> **Correction (2026-08-15).** Revision 2.1 of this file stated the repository was
> "28% complete (35 of 123 files)" on the same date that `README.md` stated 76%. Both were
> wrong. Direct enumeration on 2026-08-15 returns **123 markdown files on disk**, with the
> **specification layer complete** — 67 of 67 modules and 12 of 12 portals written. Sixteen
> planned files remain unwritten (research layer 5, reference layer 4, delivery 4, `00-05`,
> architecture 2). See finding **AF-02** in
> `../project_content/_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md`.

### Files that currently exist — enumerated 2026-08-15

```
README.md ✅                    FOLDER_STRUCTURE.md ✅
00-01 ✅  00-02 ✅  00-03 ✅  00-04 ✅  00-06 ✅  00-07 ✅       (00-05 MISSING — finding AF-04)
01_Research_and_Benchmarking/   EMPTY — 0 of 5 written (finding AF-05)
02-01 ✅  02-02 ✅  02-05 ✅                                     (02-03, 02-04 planned)
03_Modules/_MODULE_TEMPLATE.md ✅   _MODULE_SET_AUDIT_REPORT.md ✅
03_Modules/A…K/_CATEGORY_OVERVIEW.md ✅ (all 11)
03_Modules/  M01 … M67 ✅  — ALL 67 MODULE SPECIFICATIONS WRITTEN
03_Modules/  _CATEGORY_{E,F,G,J,K}_AUDIT_REPORT.md ✅ (5 of 11 categories audited)
04-00 ✅                                                        (P01–P12 exist but are MISFILED)
05-01 ✅  05-02 ✅  05-03 ✅  05-04 ✅  05-05 ✅  05-06 ✅
06-01 ✅  06-02 ✅                                               (06-03 … 06-06 planned)
99_Reference/_Superseded/ (5 archived pillar drafts) ✅          (99-01 … 99-04 planned)
```

> ⚠ **Finding AF-01 — the twelve portal specifications are in the wrong folder.**
> `P01`–`P12` and `_PORTAL_SUITE_AUDIT_REPORT.md` are currently saved in
> `03_Modules/K_Platform_and_Technology/`, not in `04_Portals_and_Applications/` as the target
> tree below requires. They are complete and authoritative (771 KB, 10,020 lines); only their
> location is wrong. This breaks principles **FS-01** and **FS-02**, corrupts automated counts,
> and leaves four module files (`M02`, `M03`, `M04`, `M05`) citing them at a path that will
> break when corrected (**AF-14**).
>
> **The move is not executed** because §8 of this document requires CTO approval for structural
> changes. Remediation instruction: move the thirteen files, update the four references, and
> regenerate the `README.md` completeness table in one change.

### Target tree

```
1000fix_ERP_Module/
│
├── README.md                                    Entry point and navigation guide
├── FOLDER_STRUCTURE.md                          This file
│
├── 00_Governance_and_Charter/                   WHY the programme exists and how it is governed
│   ├── 00-01_Master_Index_and_Document_Map.md
│   ├── 00-02_Executive_Summary_and_Scope_Charter.md
│   ├── 00-03_Scope_Expansion_Delta_v1_to_v2.md
│   ├── 00-04_Risks_Assumptions_Dependencies_and_Governance.md
│   └── 00-05_Decision_Log_and_Change_Control.md
│
├── 01_Research_and_Benchmarking/                EVIDENCE the design is grounded in
│   ├── 01-01_ERP_Market_Benchmark_Study.md
│   ├── 01-02_Competitor_Module_Feature_Matrix.md
│   ├── 01-03_Module_Gap_Analysis.md
│   ├── 01-04_Industry_Best_Practice_Reference.md
│   └── 01-05_Workspace_Source_Evidence_Register.md
│
├── 02_Architecture/                             HOW the 67 modules fit together
│   ├── 02-01_ERP_Module_Architecture_and_System_Map.md
│   ├── 02-02_Module_Catalogue_Master_Register.md
│   ├── 02-03_Module_Boundary_and_Overlap_Rules.md
│   ├── 02-04_Module_Dependency_Map.md
│   └── 02-05_Technology_Stack_and_Build_vs_Buy.md
│
├── 03_Modules/                                  WHAT each module does — 67 files
│   ├── _MODULE_TEMPLATE.md
│   │
│   ├── A_Service_Delivery_and_Operations/                      (7 modules)
│   │   ├── _CATEGORY_OVERVIEW.md
│   │   ├── M01_Service_Request_and_Order_Management.md
│   │   ├── M02_Field_Service_and_Dispatch_Management.md
│   │   ├── M03_Service_Logistics_and_Reverse_Logistics.md
│   │   ├── M04_Branch_and_Front_Desk_Operations.md
│   │   ├── M05_Remote_Support_and_Managed_Services.md
│   │   ├── M06_Data_Services_and_Secure_Data_Handling.md
│   │   └── M31_Workshop_and_Depot_Repair_Management.md          ★ new
│   │
│   ├── B_Customer_Engagement_and_Experience/                   (7 modules)
│   │   ├── _CATEGORY_OVERVIEW.md
│   │   ├── M07_CRM_Sales_Pipeline_and_Account_Management.md
│   │   ├── M10_Loyalty_Membership_and_Rewards.md
│   │   ├── M27_Omnichannel_Contact_Centre_and_Communications.md
│   │   ├── M32_Conversational_AI_and_Virtual_Assistant.md       ★ new
│   │   ├── M33_Customer_and_Party_Master_Management.md          ★ new
│   │   ├── M34_Customer_Experience_Feedback_and_Complaints.md   ★ new
│   │   └── M35_Marketing_Campaigns_and_Demand_Generation.md     ★ new
│   │
│   ├── C_Commercial_Pricing_and_Revenue/                       (9 modules)
│   │   ├── _CATEGORY_OVERVIEW.md
│   │   ├── M08_Contract_Lifecycle_Management.md
│   │   ├── M09_Warranty_Protection_Plans_and_Claims.md
│   │   ├── M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md
│   │   ├── M12_Marketplace_and_Seller_Ecosystem.md
│   │   ├── M36_Quotation_Estimation_and_Tender_Management.md    ★ new
│   │   ├── M37_Product_and_Service_Catalogue_Management.md      ★ new
│   │   ├── M38_ECommerce_and_Digital_Storefront.md              ★ new
│   │   ├── M39_Subscription_and_Recurring_Revenue.md            ★ new
│   │   └── M40_Partner_Channel_Alliance_and_Franchise.md        ★ new
│   │
│   ├── D_Circular_and_Asset_Based_Business/                    (3 modules)
│   │   ├── _CATEGORY_OVERVIEW.md
│   │   ├── M13_Rental_and_Equipment_as_a_Service.md
│   │   ├── M14_TradeIn_Refurbishment_and_Resale.md
│   │   └── M18_EWaste_Recycling_and_Circular_Economy.md
│   │
│   ├── E_Supply_Chain_and_Inventory/                           (6 modules)
│   │   ├── _CATEGORY_OVERVIEW.md
│   │   ├── M15_Spare_Parts_and_Inventory_Management.md
│   │   ├── M16_Procurement_and_Strategic_Sourcing.md
│   │   ├── M41_Warehouse_Management.md                          ★ new
│   │   ├── M42_Supplier_Relationship_and_Performance.md         ★ new
│   │   ├── M43_Demand_Planning_and_Replenishment.md             ★ new
│   │   └── M44_Import_Trade_Compliance_and_Landed_Cost.md       ★ new
│   │
│   ├── F_Asset_Equipment_and_Facilities/                       (5 modules)
│   │   ├── _CATEGORY_OVERVIEW.md
│   │   ├── M17_Device_and_Customer_Asset_Registry.md
│   │   ├── M45_Enterprise_Asset_and_Test_Equipment.md           ★ new
│   │   ├── M46_Fleet_and_Vehicle_Management.md                  ★ new
│   │   ├── M47_Facility_Branch_Infrastructure_and_Workplace.md  ★ new
│   │   └── M48_IoT_Telemetry_and_Predictive_Maintenance.md      ★ new
│   │
│   ├── G_Finance_and_Treasury/                                 (8 modules)
│   │   ├── _CATEGORY_OVERVIEW.md
│   │   ├── M19_Financial_Accounting_and_General_Ledger.md
│   │   ├── M20_Accounts_Receivable_Invoicing_and_Collections.md
│   │   ├── M49_Fixed_Assets_and_Capital_Investment.md           ★ new
│   │   ├── M50_Treasury_Cash_and_Banking.md                     ★ new
│   │   ├── M51_Tax_and_Regulatory_Compliance_Bangladesh.md      ★ new
│   │   ├── M52_Accounts_Payable_and_Employee_Expense.md         ★ new
│   │   ├── M53_Revenue_Recognition_Commission_and_Settlement.md ★ new
│   │   └── M54_Cost_Accounting_Budgeting_and_FPA.md             ★ new
│   │
│   ├── H_People_and_Workforce/                                 (7 modules)
│   │   ├── _CATEGORY_OVERVIEW.md
│   │   ├── M21_Core_HR_and_Employee_Lifecycle.md
│   │   ├── M22_Learning_Competency_and_Certification.md
│   │   ├── M55_Time_Attendance_and_Workforce_Scheduling.md      ★ new
│   │   ├── M56_Payroll_Benefits_and_Statutory_Compliance.md     ★ new
│   │   ├── M57_Performance_Incentives_and_Compensation.md       ★ new
│   │   ├── M58_Talent_Acquisition_and_Onboarding.md             ★ new
│   │   └── M59_Health_Safety_and_Wellbeing.md                   ★ new
│   │
│   ├── I_Governance_Risk_Quality_and_Knowledge/                (4 modules)
│   │   ├── _CATEGORY_OVERVIEW.md
│   │   ├── M23_Quality_Management_System.md
│   │   ├── M24_Document_Records_and_ESignature.md
│   │   ├── M60_Governance_Risk_and_Compliance.md                ★ new
│   │   └── M61_Knowledge_Management_and_Technical_Library.md    ★ new
│   │
│   ├── J_Data_Analytics_and_Intelligence/                      (4 modules)
│   │   ├── _CATEGORY_OVERVIEW.md
│   │   ├── M25_Business_Intelligence_and_Reporting.md
│   │   ├── M26_AIML_Services_and_Model_Operations.md
│   │   ├── M62_Data_Platform_Warehouse_and_Governance.md        ★ new
│   │   └── M63_Process_Automation_and_Workflow_Orchestration.md ★ new
│   │
│   └── K_Platform_and_Technology/                              (7 modules)
│       ├── _CATEGORY_OVERVIEW.md
│       ├── M28_Integration_API_and_Event_Platform.md
│       ├── M29_Identity_Access_and_Information_Security.md
│       ├── M30_Platform_Administration_and_Configuration.md
│       ├── M64_Master_Data_Management_and_Configuration.md      ★ new
│       ├── M65_Multi_Entity_Multi_Country_and_Localisation.md   ★ new
│       ├── M66_Internal_IT_Service_Management.md                ★ new
│       └── M67_Project_Program_and_Portfolio_Management.md      ★ new
│
├── 04_Portals_and_Applications/                 WHO consumes the modules — 12 surfaces
│   ├── 04-00_Portal_Suite_Overview.md
│   ├── P01_Customer_Self_Service_Portal_and_Mobile_Application.md
│   ├── P02_Technician_Mobile_Application.md
│   ├── P03_Admin_Operations_Portal.md
│   ├── P04_Corporate_B2B_Portal.md
│   ├── P05_Vendor_and_Supplier_Portal.md
│   ├── P06_Analytics_and_Executive_Dashboard.md
│   ├── P07_Marketplace_Seller_Portal_and_Application.md
│   ├── P08_Brand_Partner_Portal.md
│   ├── P09_Logistics_and_Rider_Application.md
│   ├── P10_Contact_Centre_Agent_Console.md
│   ├── P11_Field_Auditor_and_Quality_Application.md
│   └── P12_Partner_and_Referral_Portal.md
│
├── 05_Cross_Cutting_Specifications/             Content shared by all modules — maintained once
│   ├── 05-01_Feature_and_Function_Register.md
│   ├── 05-02_Data_Model_and_Entity_Catalogue.md
│   ├── 05-03_Integration_and_API_Catalogue.md
│   ├── 05-04_Role_Permission_and_Access_Matrix.md
│   ├── 05-05_Business_Rules_and_Automation_Catalogue.md
│   └── 05-06_NonFunctional_Requirements_and_Standards.md
│
├── 06_Delivery_and_Implementation/              WHEN and HOW it gets built
│   ├── 06-01_Implementation_Roadmap_and_Phasing.md
│   ├── 06-02_KPI_Benefits_and_Acceptance_Criteria.md
│   ├── 06-03_Data_Migration_Strategy.md
│   ├── 06-04_Testing_and_Quality_Strategy.md
│   ├── 06-05_Change_Management_and_Training_Plan.md
│   └── 06-06_Deployment_and_Operations_Plan.md
│
└── 99_Reference/                                Supporting reference material
    ├── 99-01_Glossary_and_Acronyms.md
    ├── 99-02_Identifier_Conventions.md
    ├── 99-03_Document_Standards_and_Templates.md
    ├── 99-04_Source_Document_Index.md
    └── _Superseded/
        ├── SUPERSEDED_Pillar_A_Core_Service_Operations.md
        ├── SUPERSEDED_Pillar_B_Customer_Commercial_Revenue.md
        ├── SUPERSEDED_Pillar_C_Supply_Chain_and_Asset.md
        ├── SUPERSEDED_Pillar_D_Finance_People_Governance.md
        └── SUPERSEDED_Pillar_E_Intelligence_and_Platform.md
```

---

## 3. Folder Purpose Reference

| Folder | Answers | Primary Audience | Change Frequency |
|---|---|---|---|
| `00_Governance_and_Charter` | Why are we doing this, who decides, what are the risks | Board, executives | Low — changes on formal decisions |
| `01_Research_and_Benchmarking` | What does world-class look like, what were we missing | Architects, executives | Low — refreshed annually |
| `02_Architecture` | How do 67 modules fit together without overlapping | Architects, vendor | Medium — on architecture decisions |
| `03_Modules` | What exactly does each module do | Business owners, developers, QA | High — the working specification layer |
| `04_Portals_and_Applications` | How do users reach the modules | UX, frontend, business owners | Medium |
| `05_Cross_Cutting_Specifications` | Rules that apply everywhere | Developers, QA, security | Medium |
| `06_Delivery_and_Implementation` | When, in what order, with what proof | PMO, delivery teams | High during delivery |
| `99_Reference` | Definitions, conventions, history | All | Low |

---

## 4. Module Category Definitions

| Cat | Name | Definition — what belongs here | Count |
|---|---|---|---:|
| **A** | Service Delivery & Operations | Everything that happens to a customer's device or IT estate, from request to completion, in any delivery mode | 7 |
| **B** | Customer Engagement & Experience | Who the customer is, how we know them, how we talk to them, how they feel about us | 7 |
| **C** | Commercial, Pricing & Revenue | What we sell, what we charge, what we agree, and every route to market | 9 |
| **D** | Circular & Asset-Based Business | Business lines where 1000FiX owns or takes possession of the asset itself | 3 |
| **E** | Supply Chain & Inventory | Materials in, materials stored, materials consumed, and the suppliers behind them | 6 |
| **F** | Asset, Equipment & Facilities | Physical things the Company operates: customer assets, own tools, vehicles, buildings, connected devices | 5 |
| **G** | Finance & Treasury | Money — recorded, collected, paid, planned, taxed and reported | 8 |
| **H** | People & Workforce | Employing, scheduling, paying, developing and protecting the workforce | 7 |
| **I** | Governance, Risk, Quality & Knowledge | Proving the business is well-run: quality, risk, compliance, records, know-how | 4 |
| **J** | Data, Analytics & Intelligence | Turning operational data into insight, prediction and automation | 4 |
| **K** | Platform & Technology | The technical substrate every module depends on | 7 |
| | | **Total** | **67** |

---

## 5. File Naming Convention

### Module Files

```
M<nn>_<Descriptive_Name_In_Title_Case_With_Underscores>.md
```

- `nn` is the permanent two-digit module ID (`01`–`67`).
- The name may be revised; the ID never is.
- Files sort naturally within their category folder.

### Cross-Cutting and Programme Files

```
<folder-number>-<sequence>_<Descriptive_Name>.md
```

Example: `05-03_Integration_and_API_Catalogue.md` — third document in folder `05`.

### Portal Files

```
P<nn>_<Portal_Name>.md
```

### Reserved Prefixes

| Prefix | Meaning |
|---|---|
| `_` | Non-content file: template, category overview, archive folder |
| `SUPERSEDED_` | Retained for traceability; not authoritative |
| `DRAFT_` | Work in progress; not approved |

---

## 6. Mandatory Module File Sections

Every file in `03_Modules/` must contain these sections, in this order. The template in
`03_Modules/_MODULE_TEMPLATE.md` is the enforced form.

| # | Section | Purpose |
|---|---|---|
| 1 | Module Identity | ID, category, code, status, priority, wave, owners, layers, effort |
| 2 | Purpose | Why the module exists, in plain language |
| 3 | Scope Boundary | Explicit **in scope** and **out of scope — owned by Mnn** lists. This is the anti-overlap control. |
| 4 | Benchmark Basis | Which enterprise systems provide this capability and what was adopted |
| 5 | Functional Areas & Features | Numbered `FR-<CODE>-nnn` requirement tables |
| 6 | Business Rules | Enforced rules with classification |
| 7 | Data Entities | Owned entities and referenced entities |
| 8 | Lifecycle & State Model | State machines where the module owns one |
| 9 | Automations | Trigger → action → failure behaviour |
| 10 | Interfaces | Upstream modules, downstream modules, events, external integrations |
| 11 | Roles & Permissions | Which of the 38 roles use it and at what access level |
| 12 | Reports & Analytics | Operational and management outputs |
| 13 | KPIs | Baseline and target |
| 14 | Delivery | Layer allocation, custom modules, dependencies, effort, wave |
| 15 | Acceptance Criteria | Testable gate conditions |

---

## 7. Overlap Control

The single greatest risk in a 67-module architecture is two modules claiming the same
capability. Three controls prevent it.

| Control | Mechanism |
|---|---|
| **Declared boundary** | Section 3 of every module file lists what is explicitly *out* of scope and names the module that owns it. Both sides of every boundary must agree. |
| **Boundary register** | `02_Architecture/02-03_Module_Boundary_and_Overlap_Rules.md` holds every contested boundary and its resolution. |
| **Single-owner rule for entities** | `05_Cross_Cutting_Specifications/05-02` assigns every data entity to exactly one owning module. A module that references an entity it does not own must say so. |

---

## 8. Maintenance Rules

| Rule | Detail |
|---|---|
| A new module requires an architecture decision record and an entry in the master register before its file is created |
| A module file is never edited to add capability that belongs to another module — the boundary register is updated instead |
| Cross-cutting documents are the source of truth for shared content; module files reference them and do not restate them |
| Renaming a module updates the file name and every reference, but never the ID |
| Superseded documents move to `99_Reference/_Superseded/` with a `SUPERSEDED_` prefix and a header note; they are not deleted |
| The folder structure itself is versioned in this file; changes require CTO approval |

---

## 9. Reading Paths

| If you are… | Read in this order |
|---|---|
| **A board member** | `00-02` → `00-03` → `06-02` |
| **The CTO or an architect** | `01-01` → `01-03` → `02-01` → `02-02` → `02-03` → `02-04` |
| **A business module owner** | `_CATEGORY_OVERVIEW.md` for your category → your `Mnn_*.md` file → `05-04` roles → `06-02` KPIs |
| **An implementation vendor** | `00-02` → `02-01` → `02-02` → all `03_Modules/` → `05-*` → `06-01` |
| **A developer starting a module** | Your `Mnn_*.md` → `05-02` data model → `05-03` integration → `05-06` NFRs → `02-05` stack |
| **A QA engineer** | Your `Mnn_*.md` §15 → `05-01` requirements → `05-05` rules → `06-04` test strategy |
| **A new joiner** | `README.md` → `99-01` glossary → `02-01` architecture → your category overview |

---

*Maintained by: Enterprise Architecture, 1000FiX Services Limited*
