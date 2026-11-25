# RB-51 — National 51+ Branch Rollout & Operational Transition Runbook
## 1000FiX ERP System v2.0 · Category 12 (Release, Deployment & Transition) · RL-004 Conformance

| Metadata | Details |
|---|---|
| **Runbook ID** | `RB-51-BRANCH-ROLLOUT` |
| **Document Version** | 1.0 (Enterprise Release Baseline) |
| **Governance Standard** | ITIL 4 Deployment Management · ISO 21502:2020 §7.7 · RL-004 · OP-002 §4.4 · SV-005 |
| **Authoritative Register** | 53 Operational Service Centres across all 8 Administrative Divisions (`SC-001`…`SC-053`) |
| **Owning Lead** | Branch Operations Lead with the Change Lead |
| **Approving Authority** | Operations Director with the Programme Director |
| **Exit Criterion** | Gate G7 Criterion `G7-7` ("All 51+ branches live") — 100% Go-Live with Zero Rollout Blockers |

---

## 1. Executive Summary & Purpose

This runbook governs the phased, national rollout of the 1000FiX Integrated Smart ERP System v2.0 across Bangladesh's largest after-sales repair network. Replacing the legacy WordPress/manual tracking mechanism, this deployment brings **53 verified brick-and-mortar service centres** into live production across four sequential operational waves.

The rollout enforces:
1. **Operating Unit Multi-Branch Isolation (`AS-03`)**: Each branch functions as an independent accounting and operational unit within the Odoo 19 kernel, with strictly segregated customer records, inventory, and cash drawers.
2. **Bilingual Statutory Compliance (`BRN-01`)**: Every service centre UI, ticket intake printout, SMS notification, and VAT Mushak 6.3 invoice is rendered with full Bengali font conjunct shaping (`TR-07`).
3. **Bound Floor-Walking Capacity (`OP-002` §4.4)**: Staffing allocation of 1 floor-walker per 12–15 users for 5 working days post-go-live, preventing user abandonment.
4. **Super-User Enablement (`D-002`)**: Formal deployment of the Board-approved 85 named super-users (`D-002-ROSTER-2026-10`) leading on-site training and hypercare.

---

## 2. The 53 Service Centres Cohort Architecture (Waves 1–4)

Rollout is structured across 4 synchronized waves according to the geographic hierarchy of Bangladesh:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        NATIONAL ROLLOUT MATRIX                         │
├───────────────┬───────────────────────────────┬───────────┬────────────┤
│ Wave          │ Geographic Coverage           │ Centres   │ Codes      │
├───────────────┼───────────────────────────────┼───────────┼────────────┤
│ Wave 1        │ Flagship & Pilot Hubs         │ 6 Sites   │ SC-001,004,│
│ (Pilot)       │ (Dhaka HQ, Mirpur, Uttara,    │           │ SC-040,043,│
│               │  Agrabad, Zindabazar)         │           │ PC-01..05  │
├───────────────┼───────────────────────────────┼───────────┼────────────┤
│ Wave 2        │ Greater Dhaka Commercial Hubs │ 16 Sites  │ SC-002..003│
│ (Dhaka Metro) │ (Motijheel, IDB, Multiplan,   │           │ SC-005..015│
│               │  Gazipur, Narayanganj, Savar, │           │ SC-052..053│
│               │  Tangail, Narsingdi, Manikganj)│          │            │
├───────────────┼───────────────────────────────┼───────────┼────────────┤
│ Wave 3        │ Major Regional Hubs           │ 24 Sites  │ SC-020..026│
│ (Regional)    │ (Chattogram, Sylhet, Khulna,  │           │ SC-032..036│
│               │  Rajshahi Divisions)          │           │ SC-041..042│
│               │                               │           │ SC-044..051│
├───────────────┼───────────────────────────────┼───────────┼────────────┤
│ Wave 4        │ National Frontier Completion  │ 12 Sites  │ SC-016..019│
│ (National)    │ (Mymensingh, Rangpur,         │           │ SC-027..031│
│               │  Barishal Divisions)          │           │ SC-037..039│
├───────────────┼───────────────────────────────┼───────────┼────────────┤
│ TOTAL         │ All 8 Administrative Divisions│ 53 Sites  │ SC-001..053│
└───────────────┴───────────────────────────────┴───────────┴────────────┘
```

---

## 3. Site Readiness Gate Checklists (`RB-01`…`RB-12`)

Before a service centre receives authorization to cut over from legacy systems to ERP v2.0, all 12 operational readiness domains must be verified and signed off by the Zone Coordinator:

| Rule ID | Readiness Domain | Verification Method | Pass Criteria | Responsible |
|---|---|---|---|---|
| `RB-01` | **Network & Power** | On-site speed test at peak hour | Dual ISP active (≥ 10 Mbps) + Online UPS (≥ 2 hr runtime) | IT Admin |
| `RB-02` | **Hardware & Terminals**| Asset barcode scan & health audit | POS printers, 2D barcode scanners, webcams connected | IT Admin |
| `RB-03` | **Master Data Setup** | DB check (`fix_branch`, `operating_unit`)| Branch record active, correct GPS, manager assigned | MDM Analyst |
| `RB-04` | **Staff Roster** | HR system validation | Minimum 1 Manager + 2 Techs + 1 Front-Desk agent rostered | HR Business Partner |
| `RB-05` | **Super-User Training**| LMS completion certificate (`TR-011`) | Branch manager and lead tech ≥ 85% test score | L&D Lead |
| `RB-06` | **Cash Drawer Setup** | Finance verification | Petty cash baseline counted, money receipt sequence locked | Branch Accountant |
| `RB-07` | **Physical Stock Audit**| Witnessed physical count sheet | Physical inventory matches legacy balance within ±0.1% | Warehouse Supv. |
| `RB-08` | **Device Custody Audit**| Device serial intake audit | In-shop customer repair devices tagged with 2D QR codes | Front-Desk Lead |
| `RB-09` | **Signage & Collateral**| Physical photo verification | 1000FiX ISO 9001:2015 brand branding + hotline 16743 | Marketing Lead |
| `RB-10` | **Local Emergency Kit** | Physical inspection | Bengali manual paper forms (`OP-014`) on site | Operations Lead |
| `RB-11` | **Security & CCTV** | Security center ping | CCTV feeds online, DVR storage verified ≥ 30 days | HSE / Security Lead |
| `RB-12` | **Cutover Authorization**| Electronic signature in Odoo | Signed Go-Live certificate approved by Operations Director | Operations Director |

---

## 4. Floor-Walking Resourcing Model (`OP-002` §4.4)

To eliminate post-cutover failure, human support is deployed on-site during operational hours:
- **Pilot Sites (Wave 1)**: 2–3 dedicated floor-walkers per site for 10 consecutive working days.
- **Subsequent Sites (Waves 2–4)**: 1–2 dedicated floor-walkers per site for 5 consecutive working days.
- **Ratio Standard**: 1 floor-walker per 12–15 active staff users.
- **Local Champion Ownership**: At day T+6 (or T+11 for pilot), the on-site Branch Champion assumes ongoing L1 frontline coaching.

---

## 5. Super-User Training Program (`D-002` / `CH-002`)

The 85 named individuals from Board Resolution `D-002-ROSTER-2026-10` lead the operational training:
1. **Curriculum Tracks**:
   - `TR-002`: Core ERP Navigation & Security Hygiene (8 hours)
   - `TR-011`: Branch Manager & Service Desk Command (16 hours)
   - `TR-012`: Diagnostics & Workshop Repair Lifecycle (12 hours)
   - `TR-024`: Spare Parts Consumption & Inventory Scan (8 hours)
2. **Cohort Verification**:
   - Each wave cohort completes 100% syllabus coverage in the staging sandbox (`PE-002`) prior to live data migration.
   - Zero access provisioning occurs without LMS certification.

---

## 6. Opening Balance & Cutover Migration Sequence

1. **T-2 Days (Data Freeze)**:
   - Freeze legacy intake registers.
   - Export active customer repair tickets and uncollected devices.
2. **T-1 Day (Stock Count & Reconciliation)**:
   - Perform physical stock count across spare parts and accessories.
   - Generate initial stock journal (`fix.stock.quant`) linked to `operating.unit`.
3. **T-0 (Cutover Instant — 06:00 Asia/Dhaka)**:
   - Import legacy active work orders with legacy references (`BR:SC:SC-xxx`).
   - Open primary cash drawer with statutory float.
   - Dispatch first live ticket through P03 Front Desk Workspace.

---

## 7. Hypercare Support Window & Exit Criteria (`SV-005`)

- **Duration**: 14 calendar days per site following cutover.
- **Exit Gates**:
  1. Transaction adoption rate ≥ 95% against pre-cutover baseline.
  2. Zero unresolved Severity 1 (P0) operational incidents.
  3. Daily cash reconciliation variance = ৳0.00 across 5 consecutive days.
  4. Average customer check-in intake time ≤ 180 seconds.
- Upon passing all 4 gates, the site transitions from Hypercare to Standard Operations.

---

## 8. Emergency Pause & Rollback Protocol (`RLO-37`…`RLO-41`)

If systemic failure occurs:
- **Triggers**:
  - `PA-1`: More than ⅓ of sites in a wave fail the same readiness check.
  - `PA-2`: Transaction adoption at live sites drops below 90% at T+10.
  - `PA-6`: Any statutory exposure or Sev-1 data loss incident.
- **Action**:
  - Immediately pause the *next* wave. Never rollback live, stabilized sites (`RLO-37`).
  - Execute root-cause remediation within 48 hours.
  - Re-pilot a single site under 2× floor-walking before resuming wave cadence (`RLO-40`).

---

## 9. Formal Approval & Signoff Matrix

| Role | Name | Signature Status | Date |
|---|---|---|---|
| **Branch Operations Lead** | Habibur Rahman | **SIGNED** | 2026-10-20 |
| **Change & Enablement Lead** | Rumana Islam | **SIGNED** | 2026-10-20 |
| **Chief Technology Officer** | Tariqul Islam, CISA | **SIGNED** | 2026-10-20 |
| **Operations Director** | Engr. Zakir Hossain | **APPROVED & ISSUED** | 2026-10-20 |

---
*1000FiX Services Limited · National ERP Operations Command · ISO 9001:2015 Certified*
