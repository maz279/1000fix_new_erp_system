---
id: FIX-ERP2-018
title: KPI, Benefits & Acceptance Criteria
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# KPI, Benefits & Acceptance Criteria

---

## 1. Business Objectives

Each objective is measurable, owned and traced to modules. BO-01 to BO-10 are carried
forward from the v1.0 BRD with raised targets. BO-11 to BO-18 are new.

| ID | Objective | Metric | Baseline | Target | By | Owner | Modules |
|---|---|---|---|---|---|---|---|
| BO-01 | Automate the service order lifecycle | % processed without manual intervention | 20% | 85% | M34 | Ops Director | M01, M02, M20 |
| BO-02 | Maximise field technician productivity | Jobs per technician per day | 4–5 | 8–9 | M26 | Ops Director | M02, M26 |
| BO-03 | Achieve inventory accuracy across all locations | Accuracy rate | 75% | 98%+ | M18 | Inventory Manager | M15 |
| BO-04 | Recover all eligible warranty revenue | % claims submitted within 72 hours | ~50% at 30–90 days | 95%+ | M18 | Finance Director | M09 |
| BO-05 | Improve customer satisfaction and reduce turnaround | CSAT · TAT | 3.8/5 · unmeasured | 4.7/5 · <24h IT, <4h appliance | M22 | Customer Service Manager | M01, M07, M27 |
| BO-06 | Compress the financial close | Days to close | 15–20 | ≤ 3 | M20 | CFO | M19, M20 |
| BO-07 | Give management real-time visibility | Time to branch performance data | Days | Real-time | M18 | CEO | M25 |
| BO-08 | Grow contract subscriptions | Renewal rate · contract base | 60% · baseline | 88% · 2.5× | M30 | CCO | M08, M10 |
| BO-09 | Remove capacity constraints on growth | Annual revenue growth | Baseline | +87% over 18 months post-W4 | M36 | CEO | All |
| BO-10 | Full Bangladesh regulatory compliance | Compliance findings · late filings | Manual, error-prone | Zero | M18 | CFO / HR Director | M19, M21, M23 |
| **BO-11** | **Build managed services into a material revenue line** | MSP revenue share | 0% | ≥ 12% of revenue | M34 | Corporate Services Head | M05, M08 |
| **BO-12** | **Scale delivery capacity beyond owned headcount** | Marketplace share of job volume | 0% | ≥ 25% | M34 | CCO | M12 |
| **BO-13** | **Establish rental as a profitable asset business** | Fleet utilisation · gross margin | n/a | 68% · 55% | M32 | Corporate Services Head | M13 |
| **BO-14** | **Build a circular device business** | Refurbished units sold per year · margin | 0 | 12,000 · 22% | M34 | Retail Operations Head | M14, M18 |
| **BO-15** | **Make competency an enforced control** | Claims rejected for uncertified technician | Unknown | Zero | M24 | Quality Manager | M22 |
| **BO-16** | **Bring every customer conversation into the system** | Conversations captured | ~0% | 100% | M20 | Customer Service Manager | M27 |
| **BO-17** | **Make decisions on live data** | Manual reporting packs | 100% | Zero | M34 | CTO | M25 |
| **BO-18** | **Be ready to operate in a second country** | Time to stand up a country pack | Not possible | ≤ 12 weeks | M36 | CTO | M30 |

---

## 2. KPI Register

### 2.1 Service Delivery

| ID | KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|---|
| KPI-001 | Service order automation rate | 20% | 65% | 85% | M01 |
| KPI-002 | Average TAT — IT equipment | unmeasured | < 36 h | < 24 h | M01 |
| KPI-003 | Average TAT — appliance on-site | unmeasured | < 6 h | < 4 h | M01 |
| KPI-004 | First-time fix rate | 70% | 82% | 88% | M01 |
| KPI-005 | Rework rate | unmeasured | < 5% | < 3% | M01, M23 |
| KPI-006 | SLA compliance | unmeasured | 92% | 96% | M01 |
| KPI-007 | QC first-pass rate | unmeasured | 92% | 95% | M01 |
| KPI-008 | Estimate approval conversion | unmeasured | 72% | 78% | M11 |
| KPI-009 | Devices uncollected > 30 days | unmeasured | < 1% | < 0.5% | M01 |
| KPI-010 | Walk-in intake time | ~10 min | < 4 min | < 3 min | M04 |

### 2.2 Field Operations

| ID | KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|---|
| KPI-011 | Jobs per technician per day | 4–5 | 7 | 8–9 | M02 |
| KPI-012 | Technician utilisation | 55% | 74% | 82% | M02 |
| KPI-013 | Automatic assignment rate | 0% | 20% | 70% | M02, M26 |
| KPI-014 | Travel time as % of working day | ~35% | 26% | 22% | M02 |
| KPI-015 | On-time arrival within window | unmeasured | 88% | 92% | M02 |
| KPI-016 | Technician app daily active usage | 0% | 92% | 95% | M02 |
| KPI-017 | Offline sync failures | n/a | 0 | 0 | M02 |
| KPI-018 | Logistics on-time collection/delivery | unmeasured | 90% | 93% | M03 |
| KPI-019 | Chain-of-custody exceptions | untracked | 0 | 0 | M03 |

### 2.3 Customer

| ID | KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|---|
| KPI-020 | CSAT | 3.8/5 | 4.4/5 | 4.7/5 | M07 |
| KPI-021 | NPS | unmeasured | 42 | 55 | M07 |
| KPI-022 | Online booking rate | 40% | 72% | 88% | P01 |
| KPI-023 | Customer churn | ~15% | 11% | < 8% | M07, M26 |
| KPI-024 | Complaint resolution within SLA | unmeasured | 90% | 95% | M23 |
| KPI-025 | Status enquiries deflected to self-service | 0% | 60% | 80% | M27 |
| KPI-026 | AI first-contact resolution | 0% | 40% | 55% | M27 |
| KPI-027 | First-contact resolution (all channels) | unmeasured | 70% | 78% | M27 |

### 2.4 Commercial

| ID | KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|---|
| KPI-028 | AMC/RAMC renewal rate | 60% | 80% | 88% | M08 |
| KPI-029 | Contract base growth | baseline | 1.6× | 2.5× | M08 |
| KPI-030 | Contract SLA attainment | unmeasured | 95% | 97% | M08 |
| KPI-031 | Contracts with negative margin | unknown | < 6% | < 3% | M08 |
| KPI-032 | Quotation-to-order conversion | unmeasured | 72% | 78% | M11 |
| KPI-033 | Gross margin on paid repair | baseline | +2 pts | +4 pts | M11 |
| KPI-034 | Privilege membership base | baseline | 2× | 3× | M10 |
| KPI-035 | Referral-attributed new customers | 0% | 6% | 12% | M10 |
| KPI-036 | Warranty product attach rate | unmeasured | 12% | 18% | M09 |

### 2.5 Warranty & Claims

| ID | KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|---|
| KPI-037 | Claims submitted within 72 hours | ~50% at 30–90 days | 92% | 95% | M09 |
| KPI-038 | Warranty revenue leakage | 15–20% | 5% | < 2% | M09 |
| KPI-039 | First-submission approval rate | unmeasured | 90% | 92% | M09 |
| KPI-040 | Days from service to reimbursement | 60–120 | 55 | < 45 | M09 |
| KPI-041 | Claims with complete evidence at submission | unmeasured | 96% | 98% | M09 |

### 2.6 Supply Chain

| ID | KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|---|
| KPI-042 | Inventory accuracy | 75% | 96% | 98% | M15 |
| KPI-043 | Part availability at first request | unmeasured | 88% | 93% | M15 |
| KPI-044 | Stockout-caused job delays | unmeasured | < 6% | < 3% | M15 |
| KPI-045 | Inventory turns per year | unmeasured | 4.5 | 6+ | M15 |
| KPI-046 | Dead stock as % of value | unmeasured | < 8% | < 5% | M15 |
| KPI-047 | Van stock variance | untracked | < 2% | < 1% | M15 |
| KPI-048 | Vendor on-time delivery | unmeasured | 88% | 92% | M16 |
| KPI-049 | Three-way match exception rate | n/a | < 8% | < 5% | M16 |

### 2.7 Financial

| ID | KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|---|
| KPI-050 | Month-end close cycle | 15–20 days | 5 days | ≤ 3 days | M19 |
| KPI-051 | Bank reconciliation auto-match | manual | 90% | 94% | M19 |
| KPI-052 | Days sales outstanding | unmeasured | 38 | < 32 | M19, M20 |
| KPI-053 | Invoices auto-generated | 0% | 100% | 100% | M20 |
| KPI-054 | Invoice within 1 hour of closure | ~3–7 days | 95% | 97% | M20 |
| KPI-055 | Billing accuracy (credit notes as % of invoices) | unmeasured | < 2.5% | < 1.5% | M20 |
| KPI-056 | Revenue leakage (unbilled delivered work) | unknown | < 1.5% | < 0.5% | M20 |
| KPI-057 | VAT returns filed on time with zero adjustment | manual | 100% | 100% | M19 |
| KPI-058 | Tax compliance findings | unmeasured | Zero | Zero | M19 |

### 2.8 People & Quality

| ID | KPI | Baseline | W5 | W8 | Source |
|---|---|---|---|---|---|
| KPI-059 | Payroll processing time | 3 days | 6 h | < 4 h | M21 |
| KPI-060 | Payroll corrections per run | unmeasured | < 0.5% | < 0.3% | M21 |
| KPI-061 | Attendance capture completeness | manual | 98% | 99% | M21 |
| KPI-062 | Certifications current (no lapses) | unknown | 100% | 100% | M22 |
| KPI-063 | Claims rejected for uncertified technician | unknown | Zero | Zero | M22 |
| KPI-064 | Mandatory training completion on time | unmeasured | 95% | 98% | M22 |
| KPI-065 | Employee self-service adoption | 0% | 75% | 85% | M21 |
| KPI-066 | CAPA closed on time | unmeasured | 90% | 95% | M23 |
| KPI-067 | ISO major non-conformances | unknown | Zero | Zero | M23 |
| KPI-068 | Internal audit plan completion | manual | 100% | 100% | M23 |

### 2.9 New Business Lines

| ID | KPI | Target | By | Source |
|---|---|---|---|---|
| KPI-069 | Monitored assets under management | 5,000 | W6 | M05 |
| KPI-070 | MSP SLA attainment | 98% | W6 | M05 |
| KPI-071 | Remote resolution rate (no site visit) | 65% | W6 | M05 |
| KPI-072 | MSP gross margin | 55% | W7 | M05 |
| KPI-073 | Data recovery success rate | 82% | W7 | M06 |
| KPI-074 | Data-services custody exceptions | Zero | W6 | M06 |
| KPI-075 | Rental fleet utilisation | 68% | W7 | M13 |
| KPI-076 | Rental damage recovery rate | 85% | W7 | M13 |
| KPI-077 | Refurbishment yield | 88% | W7 | M14 |
| KPI-078 | Refurbished units sold per year | 12,000 | W8 | M14 |
| KPI-079 | Approved active marketplace sellers | 500 | W8 | M12 |
| KPI-080 | Marketplace share of job volume | 25% | W8 | M12 |
| KPI-081 | Marketplace dispute rate | < 1.5% | W8 | M12 |
| KPI-082 | Seller payout accuracy | 100% | W7 | M20 |
| KPI-083 | E-waste diversion from landfill | 92% | W8 | M18 |
| KPI-084 | Disposal certificates on file | 100% | W8 | M18 |

### 2.10 Platform

| ID | KPI | Target | Source |
|---|---|---|---|
| KPI-085 | System uptime (business hours) | ≥ 99.9% | M28 |
| KPI-086 | API p95 latency | < 400 ms | M28 |
| KPI-087 | Event delivery success | > 99.9% | M28 |
| KPI-088 | Integration failures undetected > 5 min | Zero | M28 |
| KPI-089 | Critical vulnerabilities open > 7 days | Zero | M29 |
| KPI-090 | Orphaned accounts after leaver | Zero beyond 24 h | M29 |
| KPI-091 | Backup restore tests passed | 100% | M29 |
| KPI-092 | Bengali translation completeness | 100% | M30 |
| KPI-093 | Data quality test pass rate | > 99% | M25 |
| KPI-094 | Manual management reports remaining | Zero | M25 |
| KPI-095 | Overall automation of routine work | 85% | All |

---

## 3. Benefit Model

### 3.1 Annual Benefit at Steady State (Year 3+)

| # | Benefit | Conservative | Base | Optimistic | Module | First Realised |
|---|---|---:|---:|---:|---|---|
| 1 | Warranty revenue recovery | 60 | 100 | 140 | M09 | W4 |
| 2 | Technician productivity | 85 | 130 | 175 | M02, M26 | W2 |
| 3 | Inventory cost reduction | 20 | 34 | 50 | M15, M26 | W3 |
| 4 | Administrative labour savings | 38 | 62 | 88 | All | W3 |
| 5 | Customer retention | 46 | 78 | 112 | M07, M10, M27 | W4 |
| 6 | AMC/RAMC renewal uplift | 42 | 72 | 100 | M08 | W5 |
| 7 | Financial close & cash flow | 15 | 26 | 38 | M19, M20 | W3 |
| 8 | Managed services (MSP) | 55 | 95 | 145 | M05 | W6 |
| 9 | Rental gross margin | 28 | 48 | 72 | M13 | W7 |
| 10 | Refurbishment & resale margin | 38 | 65 | 96 | M14 | W7 |
| 11 | Marketplace commission & advertising | 48 | 84 | 130 | M12 | W8 |
| 12 | Data services | 17 | 30 | 46 | M06 | W7 |
| 13 | E-waste material recovery | 7 | 12 | 19 | M18 | W9 |
| 14 | Dynamic pricing margin uplift | 22 | 40 | 62 | M11, M26 | W8 |
| | **Total (BDT lac per year)** | **521** | **876** | **1,273** | | |
| | **Total (USD @ 110)** | **~$474K** | **~$797K** | **~$1.16M** | | |

### 3.2 Benefit Realisation Curve

| Period | Cumulative Benefit (Base, BDT lac) | Notes |
|---|---:|---|
| Year 1 (M1–M12) | 45 | Pilot productivity and early automation only |
| Year 2 (M13–M24) | 310 | v1.0 scope fully live; warranty and contract benefits landing |
| Year 3 (M25–M36) | 645 | New business lines ramping |
| Year 4 (steady state) | 876 | Full run rate |
| Year 5 | 920 | Compounding on customer base growth |

### 3.3 Cost Model

| Category | Year 1 | Year 2 | Year 3 | 3-Year Total |
|---|---:|---:|---:|---:|
| Software licensing | $0–12K | $0–12K | $0–12K | $0–36K |
| Implementation & custom development | $135K–210K | $95K–160K | $60K–100K | $290K–470K |
| Infrastructure / hosting | $12K–20K | $18K–32K | $22K–44K | $52K–96K |
| Third-party APIs | $9K–20K | $14K–33K | $18K–42K | $41K–95K |
| Training & change management | $10K–18K | $7K–14K | $5K–11K | $22K–43K |
| Support & maintenance | — | $20K–45K | $30K–65K | $50K–110K |
| **Total** | **$166K–280K** | **$154K–296K** | **$135K–274K** | **$455K–850K*** |

*The headline range in Doc 01 is $455K–$780K, using the mid-point of the optimistic
maintenance assumption. The upper bound here reflects the worst case on every line
simultaneously, which is unlikely.*

### 3.4 Return

| Scenario | 3-Yr Benefit | 3-Yr Cost | Net | ROI | Payback |
|---|---:|---:|---:|---:|---|
| Conservative | $1.24M | $780K | $460K | 59% | 24 months |
| Base case | $1.96M | $610K | $1.35M | 221% | 17 months |
| Optimistic | $2.61M | $455K | $2.16M | 475% | 12 months |

### 3.5 Benefit Ownership

Each benefit has a named owner accountable for realising it. Benefits are tracked monthly
from the wave in which they first become realisable.

| Benefit | Owner | Measured From |
|---|---|---|
| Warranty revenue recovery | Finance Director | W4 |
| Technician productivity | Ops Director | W2 |
| Inventory cost reduction | Inventory Manager | W3 |
| Administrative labour savings | Ops Director | W3 |
| Customer retention | CCO | W4 |
| Contract renewal uplift | CCO | W5 |
| Close & cash flow | CFO | W3 |
| MSP revenue | Corporate Services Head | W6 |
| Rental margin | Corporate Services Head | W7 |
| Refurbishment margin | Retail Operations Head | W7 |
| Marketplace revenue | CCO | W8 |
| Data services revenue | Technical Services Head | W7 |
| E-waste recovery | Quality Manager | W9 |
| Pricing margin uplift | CCO | W8 |

---

## 4. Wave Gate Acceptance Criteria

Each gate is a formal Go/No-Go. **All criteria must be met**; partial passes are recorded as
conditional with a dated remediation plan.

### Gate 1 — Foundation (Month 4)

| # | Criterion | Evidence |
|---|---|---|
| G1-01 | Service orders created from all live channels at pilot sites | Demonstration + transaction log |
| G1-02 | Full service order lifecycle operating end to end | Demonstration |
| G1-03 | Walk-in intake completed in under 3 minutes by branch staff | Timed observation, 20 samples |
| G1-04 | SLA clocks and escalations firing correctly | Test evidence |
| G1-05 | Customer and device data migrated and reconciled | Signed reconciliation |
| G1-06 | Single sign-on and role framework operating for all delivered roles | Security test report |
| G1-07 | Audit trail complete for all delivered objects | Audit sample review |
| G1-08 | 100% Bengali translation on delivered screens | Translation coverage report |
| G1-09 | Zero critical or high security findings | Security review |
| G1-10 | Performance targets met for delivered screens | Load test report |
| G1-11 | UAT signed off by named super-users | Signed UAT record |
| G1-12 | Runbooks and training materials delivered | Document register |

### Gate 2 — Field Operations (Month 8)

| # | Criterion |
|---|---|
| G2-01 | Technician app in daily use by 100% of Dhaka technicians |
| G2-02 | 24-hour offline operation demonstrated with zero data loss |
| G2-03 | Sync completing within 30 seconds on 3G after 24 hours offline |
| G2-04 | Route optimisation reducing measured travel time by ≥ 15% |
| G2-05 | GPS tracking and customer tracking page live |
| G2-06 | Inventory accuracy ≥ 95% at migrated locations, verified by count |
| G2-07 | Van stock reconciling daily with variance < 2% |
| G2-08 | Online booking rate ≥ 60% at pilot sites |
| G2-09 | Paper service forms withdrawn in Dhaka |
| G2-10 | Privilege benefits applying automatically and correctly |

### Gate 3 — Money & Movement (Month 13)

| # | Criterion |
|---|---|
| G3-01 | 100% of invoices generated automatically from closed jobs |
| G3-02 | Payment auto-matching ≥ 90% |
| G3-03 | bKash, Nagad and card payments live and reconciling |
| G3-04 | Mushak invoices accepted with zero NBR exceptions |
| G3-05 | First full month-end closed within 5 days |
| G3-06 | Three-way matching blocking unmatched vendor invoices |
| G3-07 | Pick & drop operating with unbroken chain of custody, zero exceptions |
| G3-08 | Financial history migrated and reconciled to the trial balance |
| G3-09 | Branch cash reconciling daily across all live branches |

### Gate 4 — Agreements & Contact (Month 18) — v1.0 Scope Complete

| # | Criterion |
|---|---|
| G4-01 | Warranty claims auto-created within 24 h and submitted within 72 h |
| G4-02 | First-submission approval rate ≥ 90% |
| G4-03 | Contract engine operating all live product families |
| G4-04 | Preventive maintenance work generating automatically on schedule |
| G4-05 | 10+ corporate clients transacting on the B2B portal |
| G4-06 | Hotline conversations captured in the system of record |
| G4-07 | AI assistant resolving ≥ 40% of first contacts |
| G4-08 | Consolidated B2B invoicing operating correctly |
| G4-09 | Executive and branch dashboards in weekly management use |
| G4-10 | **Every v1.0 BRD requirement demonstrated as delivered or formally superseded** |

### Gate 5 — People, Quality & MSP (Month 22)

| # | Criterion |
|---|---|
| G5-01 | First payroll run processed, validated and paid with zero errors |
| G5-02 | BEFTN file accepted by the bank without rework |
| G5-03 | Zero uncertified technicians assignable to brand warranty work |
| G5-04 | ISO 9001 internal audit executed entirely in the system |
| G5-05 | First MSP clients live with monitored estates and SLA reporting |
| G5-06 | All 51+ service centres operating on the platform |
| G5-07 | Attendance capture ≥ 98% complete across all branches |

### Gate 6 — New Asset Businesses (Month 26)

| # | Criterion |
|---|---|
| G6-01 | Rental transacting with full condition, deposit and damage control |
| G6-02 | Zero refurbished units released without a data destruction certificate |
| G6-03 | Data-services chain of custody with zero exceptions |
| G6-04 | Automatic dispatch assignment ≥ 50% with ≥ 88% dispatcher agreement |
| G6-05 | Parts demand forecast accuracy within target |
| G6-06 | Customer native mobile apps published and adopted |

### Gate 7 — Marketplace (Month 30)

| # | Criterion |
|---|---|
| G7-01 | 200+ approved sellers transacting |
| G7-02 | Payout accuracy 100% with zero unexplained variance |
| G7-03 | Marketplace jobs meeting the same quality and evidence standards as owned jobs |
| G7-04 | Dispute rate below target with all disputes resolved within SLA |
| G7-05 | VAT treatment validated by external tax advice |
| G7-06 | Dynamic pricing operating within guard rails with a complete decision audit |

### Gate 8 — Intelligence & Sustainability (Month 34)

| # | Criterion |
|---|---|
| G8-01 | All management reporting served from the warehouse; zero manual packs |
| G8-02 | Predictive maintenance precision ≥ 70% on the pilot estate |
| G8-03 | Overall automation of routine operational work ≥ 85% |
| G8-04 | E-waste chain fully certified with zero uncertified disposals |
| G8-05 | Every production model has a current model card and drift monitoring |

### Gate 9 — Expansion Readiness (Month 36)

| # | Criterion |
|---|---|
| G9-01 | A test entity in a second country stood up in ≤ 12 weeks using configuration only |
| G9-02 | Consolidated multi-entity reporting validated |
| G9-03 | Full-scale load test passed at 1.5× projected peak |
| G9-04 | All programme documentation handed over and accepted |
| G9-05 | Support model transitioned to steady state |

---

## 5. Programme-Level Success Criteria

The programme is successful if, at Month 36:

| # | Criterion | Measure |
|---|---|---|
| 1 | All 14 revenue streams transact end to end in the ERP | Zero shadow spreadsheets in any revenue process |
| 2 | Routine operational work is 85% automated | KPI-095 |
| 3 | Month-end close completes in ≤ 3 days across all entities and lines | KPI-050 |
| 4 | 95%+ of eligible warranty claims submitted within 72 hours | KPI-037 |
| 5 | Marketplace delivers ≥ 25% of job volume | KPI-080 |
| 6 | MSP and rental together contribute ≥ 20% of revenue | BO-11, BO-13 |
| 7 | ISO 9001 surveillance passes with zero systems-related major non-conformances | KPI-067 |
| 8 | A second country entity can be stood up without core code change | G9-01 |
| 9 | Management decisions are made on live dashboards | KPI-094 |
| 10 | CSAT ≥ 4.7 and technician app usage ≥ 95% | KPI-020, KPI-016 |

---

## 6. Benefit Tracking Discipline

| Practice | Detail |
|---|---|
| Baseline capture | Every KPI's baseline is measured and signed off **before** the relevant wave begins. A KPI without a baseline cannot claim a benefit. |
| Monthly reporting | The PMO publishes a KPI dashboard monthly; benefit owners comment on variance |
| Quarterly review | The Steering Committee reviews benefit realisation against plan and agrees corrective action |
| Attribution discipline | Benefits are attributed to the ERP only where a causal mechanism is documented; general market growth is excluded |
| Post-implementation review | Full benefits audit at Month 42, six months after programme closure |
| Honest reporting | Missed benefits are reported as missed, with the reason. A benefit case that is never revisited is not a business case. |

---

*Next document: `19_Technology_Stack_and_Build_vs_Buy_Decisions.md`*
