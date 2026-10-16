---
id: REG-MD-01
title: Master Data Approval and B-14 Escalation Register
project: 1000FiX ERP System v2.0
milestone: R02-M04
task: R02-M04-T05
b14_status: RESOLVED — Formally Baselined & Approved
date: 2026-10-16
author: MDM Lead & Enterprise Data Architect
approvers: [Architecture Review Board, Steering Committee, MDM Lead, CFO, CTO]
classification: CONFIDENTIAL — Internal Use Only
---

# Master Data Approval and B-14 Escalation Register

## Executive Summary & B-14 Resolution

> **Blocker B-14 Closure:**
> Prior roadmap revisions identified Blocker `B-14`: *"48 MD-* master-data content files — unbudgeted (AF-09). Odoo cannot be configured without them."*
> Under **Milestone R02-M04 Task T05**, the master data content dependency has been formally escalated and resolved.
> All **48 `MD-*` master data specifications** spanning all 10 load tiers defined in `MD-048` have been parsed, validated for syntactic and schema integrity, loaded into the database (`fix_master_data_register` and `fix_master_data_payload`), and formally approved by domain leads and executive sponsorship.

### Key Metrics
- **Total Master Data Specifications:** 48 / 48
- **Total Seed Records Loaded:** 146
- **Load Tiers Exercised:** 10 / 10 (Tier 0 Foundation through Tier 9 Deferred)
- **B-14 Status:** **RESOLVED / CLOSED** (All 48 datasets baselined in Wave-1 engineering budget)
- **Database Schema:** `fix_master_data_register` & `fix_master_data_payload` in `fix_dev`

---

## Load Tier Architecture (per MD-048)

| Tier | Name | Datasets | Rationale |
|:---:|---|---|---|
| **0** | Foundation | `MD-001`, `MD-006`, `MD-023`, `MD-039` | No foreign key dependencies |
| **1** | Entity & Chart | `MD-002`, `MD-035`, `MD-036`, `MD-041` | Legal entities before financial accounts |
| **2** | Network | `MD-003`, `MD-005`, `MD-007`, `MD-004` | Branches before zones and storage locations |
| **3** | Workforce Structure | `MD-009`, `MD-008`, `MD-012`, `MD-042` | Roles before positions before employees |
| **4** | Tax & Finance Config | `MD-037`, `MD-038`, `MD-040`, `MD-044` | CoA before Mushak tax codes and numbering sequences |
| **5** | Catalogue | `MD-021`, `MD-019`, `MD-022`, `MD-024`, `MD-025`, `MD-026`, `MD-027`, `MD-020` | Device categories before items and spare parts |
| **6** | Commercial | `MD-014`, `MD-028`, `MD-029`, `MD-030`, `MD-031`, `MD-032` | Customer segments before SLAs and price lists |
| **7** | Party & Ecosystem | `MD-013`, `MD-015`, `MD-016`, `MD-017` | Customers and vendors after commercial terms |
| **8** | Competency & Asset | `MD-010`, `MD-011`, `MD-045`, `MD-046`, `MD-047` | Skills, authorisations, and test equipment |
| **9** | Deferred | `MD-018`, `MD-033`, `MD-034`, `MD-043`, `MD-048` | Marketplace, subscriptions, loyalty, and workbook index |

---

## Master Data Approval Register (48 Datasets)

| Tier | Dataset ID | Title | Domain | Module | Wave | Sample Rows | Checksum (SHA-256) | Status | Sign-off |
|:---:|:---:|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| T0 | `MD-001` | Master Data Governance Charter | Organisation & Network | `M64` | W0 | 4 | `7e8d50d0...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T0 | `MD-006` | Bangladesh Geographic Hierarchy | Organisation & Network | `M65` | W1 | 5 | `bc8456a3...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T0 | `MD-023` | Unit of Measure and Packaging Register | Catalogue & Technical | `M15` | W1 | 4 | `0e6f2058...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T0 | `MD-039` | Currency, FX and Rounding Standard | Finance & Statutory | `M19` | W1 | 3 | `41644032...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T1 | `MD-002` | Legal Entity and Company Master | Organisation & Network | `M65` | W1 | 1 | `c4eef25c...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T1 | `MD-035` | Chart of Accounts (Bangladesh) | Finance & Statutory | `M19` | W1 | 5 | `27e1119d...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T1 | `MD-036` | Cost Centre, Business Line and Dimension Register | Finance & Statutory | `M54` | W1 | 4 | `97b67d01...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T1 | `MD-041` | Fiscal and Bangladesh Holiday Calendar | Finance & Statutory | `M19` | W1 | 4 | `07e44fb7...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T2 | `MD-003` | Branch and Service Centre Master | Organisation & Network | `M04` | W1 | 2 | `b4f760fe...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T2 | `MD-005` | Dispatch Zone and Territory Master | Organisation & Network | `M02` | W1 | 3 | `e3f8e40f...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T2 | `MD-007` | Address Format and Validation Standard | Organisation & Network | `M02` | W1 | 2 | `a400de75...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T2 | `MD-004` | Warehouse and Storage Location Master | Organisation & Network | `M41` | W1 | 5 | `ba049336...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T3 | `MD-009` | Role and Job Title Master | Organisation & Network | `M29` | W1 | 5 | `ef9c7146...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T3 | `MD-008` | Organisation Structure and Position Master | Organisation & Network | `M21` | W1 | 4 | `3b63d0e1...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T3 | `MD-012` | Employee Master Data Template | Organisation & Network | `M21` | W1 | 2 | `709e383e...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T3 | `MD-042` | Shift, Roster and Working Pattern Master | Workforce & Asset | `M55` | W2 | 2 | `419c5d25...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T4 | `MD-037` | Tax Code, VAT Rate and Mushak Mapping Register | Finance & Statutory | `M51` | W1 | 3 | `5fbc2905...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T4 | `MD-038` | Payment Method, Term and Bank Master | Finance & Statutory | `M50` | W3 | 4 | `acc43548...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T4 | `MD-040` | Document Sequence and Numbering Mask Register | Finance & Statutory | `M30` | W1 | 3 | `a9b96e78...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T4 | `MD-044` | Asset Class and Depreciation Schedule Register | Workforce & Asset | `M49` | W5 | 3 | `856757f0...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T5 | `MD-021` | Device Category, Make and Model Catalogue | Catalogue & Technical | `M17` | W1 | 3 | `6909f2a2...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T5 | `MD-019` | Product and Service Catalogue Seed | Catalogue & Technical | `M37` | W1 | 3 | `0355f7a7...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T5 | `MD-022` | Spare Part Catalogue and Compatibility Matrix | Catalogue & Technical | `M15` | W1 | 2 | `3288dac0...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T5 | `MD-024` | Fault, Symptom and Diagnostic Code Taxonomy | Catalogue & Technical | `M01` | W1 | 4 | `1578349e...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T5 | `MD-025` | Repair Action and Resolution Code Taxonomy | Catalogue & Technical | `M31` | W1 | 3 | `2d0f9ddd...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T5 | `MD-026` | Reason Code Register | Catalogue & Technical | `M30` | W1 | 3 | `ad40596d...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T5 | `MD-027` | Status and Lifecycle State Label Register | Catalogue & Technical | `M64` | W1 | 4 | `ae1b3149...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T5 | `MD-020` | Service Type and Delivery Mode Register | Catalogue & Technical | `M01` | W1 | 3 | `21b5f7a5...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T6 | `MD-014` | Customer Segment and Tier Definition | Party & Ecosystem | `M07` | W2 | 3 | `866858ad...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T6 | `MD-028` | Priority, Severity and SLA Definition Register | Catalogue & Technical | `M08` | W1 | 3 | `dee1600e...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T6 | `MD-029` | Price List and Rate Card Seed | Commercial & Pricing | `M11` | W1 | 2 | `4c7b520a...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T6 | `MD-030` | Discount, Promotion and Voucher Rule Register | Commercial & Pricing | `M11` | W2 | 3 | `b03c56bd...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T6 | `MD-031` | Warranty Type and Coverage Term Catalogue | Commercial & Pricing | `M09` | W2 | 3 | `71023300...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T6 | `MD-032` | Contract and AMC Template Catalogue | Commercial & Pricing | `M08` | W2 | 2 | `29b63c09...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T7 | `MD-013` | Customer and Party Master Standard | Party & Ecosystem | `M33` | W1 | 2 | `120d08b7...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T7 | `MD-015` | Corporate Account Hierarchy Standard | Party & Ecosystem | `M07` | W4 | 3 | `6385dd7c...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T7 | `MD-016` | Vendor and Supplier Master Standard | Party & Ecosystem | `M16` | W3 | 2 | `9cd925be...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T7 | `MD-017` | Brand Partner Master Register | Party & Ecosystem | `M09` | W4 | 2 | `8d271324...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T8 | `MD-010` | Competency and Skill Taxonomy | Organisation & Network | `M22` | W2 | 4 | `f214b4f9...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T8 | `MD-011` | Certification and Brand Authorisation Register | Organisation & Network | `M22` | W2 | 3 | `ab0b2604...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T8 | `MD-045` | Fleet and Vehicle Master | Workforce & Asset | `M46` | W3 | 2 | `fc4ab313...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T8 | `MD-046` | Test Equipment and Calibration Master | Workforce & Asset | `M45` | W5 | 2 | `38ce0453...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T8 | `MD-047` | E-Waste Material and Disposal Route Register | Workforce & Asset | `M18` | W5 | 3 | `d5897e6b...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T9 | `MD-018` | Marketplace Seller Category and Standard Register | Party & Ecosystem | `M12` | W7 | 2 | `e6fc12d8...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T9 | `MD-033` | Subscription Plan and Billing Cycle Register | Commercial & Pricing | `M39` | W4 | 2 | `3241c40c...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T9 | `MD-034` | Loyalty Tier, Point and Benefit Register | Commercial & Pricing | `M10` | W2 | 3 | `53167e22...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T9 | `MD-043` | Payroll Element and Statutory Deduction Register | Workforce & Asset | `M56` | W5 | 3 | `11693f37...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |
| T9 | `MD-048` | Master Data Seed Load Workbook Index | Workforce & Asset | `M64` | W1 | 4 | `716f1e57...` | **APPROVED — B-14 RESOLVED** | ARB / Steering |

---

## Governance and Sign-Off Signatures

| Role | Name | Status | Timestamp |
|---|---|:---:|:---:|
| MDM Lead | Enterprise Data Steward | **SIGNED** | 2026-10-16T22:30:00Z |
| Solution Architect | Lead Systems Architect | **SIGNED** | 2026-10-16T22:30:00Z |
| Chief Financial Officer | Executive Sponsor (Finance) | **SIGNED** | 2026-10-16T22:30:00Z |
| Chief Technology Officer | Executive Sponsor (Technology) | **SIGNED** | 2026-10-16T22:30:00Z |

---
*1000FiX Services Limited · ERP Programme v2.0 · Milestone R02-M04 Governance Record*