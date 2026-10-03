---
id: FIX-ERP2-CAT-F
category: F
category_name: Asset, Equipment & Facilities
module_count: 5
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT
---

# Category F — Asset, Equipment & Facilities

**5 modules · Category owner: Service Operations Director / Chief Technology Officer**

---

## 1. What Belongs in This Category

Physical things the Company knows about, uses or is responsible for — and their condition
over time.

Four distinct populations of asset exist, and conflating them is the classic ERP mistake:

| Population | Owner | Purpose | Module |
|---|---|---|---|
| Customer devices | Customer | Serviced by us | **M17** |
| Company tools, test and diagnostic equipment | 1000FiX | Used to perform service | **M45** |
| Vehicles | 1000FiX | Move people and goods | **M46** |
| Buildings and branch infrastructure | Leased or owned | House the operation | **M47** |

A fifth cross-cutting concern — **connected assets emitting telemetry** — spans all four and
is owned by **M48**.

---

## 2. Modules

| ID | Module | Status | Priority | Wave | One-Line Definition |
|---|---|---|:--:|:--:|---|
| **M17** | Device & Customer Asset Registry | Re-scoped | P1 | W2 | The identity, ownership, history and condition of every device and asset the Company touches |
| **M45** | Enterprise Asset & Test Equipment ★ | New | P2 | W5 | Company-owned tools, diagnostic and test equipment: issue, custody, calibration, maintenance, retirement |
| **M46** | Fleet & Vehicle Management ★ | New | P2 | W5 | Service vans, rider motorcycles and company vehicles: documents, servicing, fuel, drivers, telematics, cost per kilometre |
| **M47** | Facility, Branch Infrastructure & Workplace ★ | New | P3 | W7 | 51+ premises: leases, utilities, maintenance, security, safety equipment, occupancy, opening and closing |
| **M48** | IoT Telemetry & Predictive Maintenance ★ | New | P2 | W8 | Time-series ingestion from connected assets, health scoring, threshold alerting and failure prediction |

★ = new in v2.1 after enterprise benchmarking.

---

## 3. Why the Registry and EAM Are Separate

| | M17 Device & Customer Asset Registry | M45 Enterprise Asset & Test Equipment |
|---|---|---|
| **Population** | Devices belonging to customers, plus rental-pool and refurbishment units | Tools, oscilloscopes, soldering stations, hot-air rework stations, ESD equipment, IT assets, branch equipment |
| **Primary question** | "What is this device, who owns it, what has been done to it?" | "Where is our tool, who has it, is it calibrated, is it fit to use?" |
| **Analogue** | SAP *Equipment / Technical Object* · IFS *Serialised Object* | SAP *EAM/PM* · Oracle *Maintenance Cloud* · IFS *Asset Management* |
| **Failure mode** | Wrong service history → wrong repair → rework | Uncalibrated test equipment → invalid measurement → failed QC and rejected warranty claim |
| **Regulatory hook** | Warranty evidence | ISO 9001 clause 7.1.5 — monitoring and measuring resources |

**Rule:** M17 never holds a company tool. M45 never holds a customer device. Both link to
**M49 Fixed Assets** where the item is capitalised.

---

## 4. Why IoT Is Its Own Module

Telemetry is a fundamentally different data problem from a registry: unbounded volume,
time-series storage, downsampling, retention policy, streaming alert evaluation and
model inference. Putting it inside M17 would force a transactional registry to carry a
data-engineering workload.

| | M17 Registry | M48 IoT & Predictive |
|---|---|---|
| Data shape | Rows, thousands per asset lifetime | Points, millions per asset per year |
| Store | PostgreSQL | TimescaleDB hypertable, compressed |
| Access pattern | Look up one asset | Aggregate windows across a fleet |
| Consumer | Every service transaction | Alerting, health scoring, ML |

---

## 5. Category Boundary Map

| Capability | Owned By | Not Owned By |
|---|---|---|
| Asset identity, serial, brand, model | **M17** | M13, M14, M45, M48 (all reference) |
| Brand and model master data | **M37** Catalogue | M17 (references) |
| Customer asset estate structure (site → department → user) | **M17** | M33 (owns the party hierarchy) |
| Service history of a device | **M17** projects from **M01** | — |
| Parts genealogy (which part went into which device) | **M17** | M15 (owns the part) |
| Company tool custody and calibration | **M45** | M17, M15 |
| Vehicle documents, servicing, fuel | **M46** | M45 |
| Vehicle GPS position for dispatch | **M02** consumes; **M46** owns the device | — |
| Van stock inside a vehicle | **M15** | M46 |
| Branch premises, lease, utilities | **M47** | M30 (owns branch configuration as an org unit) |
| Fire, safety and first-aid equipment at a branch | **M47** inventory; **M59** compliance | — |
| Fixed asset capitalisation and depreciation | **M49** | M17, M45, M46, M47 (all operational only) |
| Telemetry ingestion and retention | **M48** | M17 |
| Failure prediction model | **M26** builds; **M48** applies | — |
| Preventive maintenance schedule for customer assets | **M08** contract-driven, **M17** plan-driven | M45 (own equipment only) |

---

## 6. Calibration — The Control That Protects Warranty Revenue

ISO 9001:2015 requires that measuring equipment used to verify conformity is calibrated and
traceable. For 1000FiX this is not a paperwork exercise: a brand partner auditing a rejected
claim will ask whether the multimeter that measured the fault was in calibration.

| Control | Enforcement |
|---|---|
| Every measuring instrument has a calibration record with due date | M45 |
| An instrument past its calibration date is marked out of service | M45, automatic |
| A QC result recorded with an out-of-calibration instrument is flagged | M23 |
| Calibration certificates are retained for the statutory period | M24 |
| Calibration compliance is a Wave 5 gate criterion | M45 |

---

## 7. Category KPIs

| KPI | Baseline | Target | Owning Module |
|---|---|---|---|
| Devices with complete registry data | unmeasured | > 95% | M17 |
| Assets identified at intake without manual entry | unmeasured | > 90% | M17 |
| Corporate estates reconciled | unmeasured | > 90% of contracted estates | M17 |
| Tool and equipment inventory accuracy | untracked | > 98% | M45 |
| Calibration compliance | unmeasured | **100%** | M45 |
| Tools unaccounted for at audit | untracked | 0 | M45 |
| Vehicle availability | unmeasured | > 95% | M46 |
| Cost per kilometre | untracked | baselined W5, −12% by W8 | M46 |
| Vehicle document compliance (fitness, insurance, tax) | manual | 100% current | M46 |
| Branch statutory compliance (fire, safety, licences) | manual | 100% current | M47 |
| Facility maintenance requests closed within SLA | n/a | > 90% | M47 |
| Telemetry ingestion reliability | n/a | > 99.5% | M48 |
| Predicted failures confirmed (precision) | n/a | > 70% | M48 |
| Proactive interventions from prediction | 0 | > 500 per year | M48 |

---

## 8. Category Delivery Sequence

```
W2   M17 Asset Registry ──────────► every device known before service scales
W5   M45 Tools & Calibration ──┐
     M46 Fleet ────────────────┴──► operational assets under control
W7   M47 Facilities ──────────────► premises and compliance
W8   M48 IoT & Predictive ────────► telemetry and prediction (needs M62 data platform)
```

M17 is early because M01 and M09 cannot work without it. M48 is late because it needs the
data platform (M62) and accumulated history.

---

## 9. Category Risks

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| Device identity resolution fails at intake | High — every downstream record is wrong | Multiple identifiers (serial, IMEI, asset tag, QR); fuzzy match with confirmation; label programme | M17 |
| Corporate asset estates never reconciled | Medium — contract entitlement disputes | Reconciliation report comparing declared estate to assets actually seen in service | M17 |
| Calibration lapses discovered during a brand audit | High — claim rejections and certification risk | Automatic out-of-service marking; calibration compliance as a gate criterion | M45 |
| Vehicles managed on paper alongside the system | Medium | Documents and servicing driven from the system with expiry alerting | M46 |
| Facilities treated as out of scope, then bolted on | Medium — statutory compliance gaps at 51+ sites | Included explicitly at P3; minimum viable scope is compliance and maintenance | M47 |
| Telemetry volume overwhelms the transactional database | High — platform-wide performance | Time-series store with compression and retention from day one; never in PostgreSQL tables | M48 |
| Telemetry collected without customer consent | High — legal | Only agreed signals; disclosed collection; opt-out honoured | M48 |

---

*Category F · 1000FiX ERP System v2.0*
