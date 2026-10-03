---
id: FIX-ERP2-016
title: Non-Functional Requirements & Architecture Standards
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Non-Functional Requirements & Architecture Standards
# NFR-001 … NFR-092

> NFR-001 to NFR-030 are carried forward from the v1.0 BRD unchanged in intent, with
> targets raised where v2.0 scope demands it. NFR-031 onward are new.

---

## 1. Performance

| ID | Requirement | Target | Measured By | Pri |
|---|---|---|---|:--:|
| NFR-001 | ERP screen load time under normal load | ≤ 2 s p95 (was 3 s) | Synthetic monitoring | P0 |
| NFR-002 | API response time | ≤ 400 ms p95 (was 500 ms) | Gateway metrics | P0 |
| NFR-003 | Concurrent internal users without degradation | 800+ (was 500) | Load test | P0 |
| NFR-004 | Concurrent customer portal users | 75,000+ (was 50,000) | Load test | P0 |
| NFR-005 | Standard report generation | ≤ 20 s (was 30 s) | Report timing log | P1 |
| NFR-031 | Customer 360 view load | ≤ 2 s | Instrumentation | P0 |
| NFR-032 | Booking availability calculation | ≤ 800 ms p95 | API metrics | P0 |
| NFR-033 | Dispatch board refresh | ≤ 1 s for 500 open jobs | Instrumentation | P1 |
| NFR-034 | Live map update latency | ≤ 5 s from GPS emission | End-to-end trace | P1 |
| NFR-035 | Search results (any entity, including Bengali text) | ≤ 600 ms p95 | Instrumentation | P1 |
| NFR-036 | Technician app job list load on 3G | ≤ 8 s cold, ≤ 2 s warm | Field test | P0 |
| NFR-037 | Offline sync completion after 24 h offline | ≤ 30 s on 3G | Field test | P0 |
| NFR-038 | Executive dashboard load | ≤ 5 s | Instrumentation | P1 |
| NFR-039 | Warehouse query (analytical) | ≤ 10 s p95 | Warehouse metrics | P2 |
| NFR-040 | Invoice generation from job closure | ≤ 5 s | Instrumentation | P0 |
| NFR-041 | Bulk operation (1,000 records) | ≤ 60 s with progress feedback | Load test | P1 |
| NFR-042 | Payment confirmation round trip | ≤ 3 s p95 | Gateway metrics | P0 |
| NFR-043 | Event delivery to consumer | ≤ 5 s p95 | Event platform metrics | P1 |
| NFR-044 | Batch job (nightly route optimisation, all technicians) | ≤ 20 minutes | Job monitor | P1 |

---

## 2. Availability & Continuity

| ID | Requirement | Target | Pri |
|---|---|---|:--:|
| NFR-006 | System uptime during Bangladesh business hours (09:00–22:00 BST) | ≥ 99.9% | P0 |
| NFR-045 | System uptime 24×7 (managed services requires it) | ≥ 99.7% | P1 |
| NFR-007 | Disaster recovery objectives | RPO ≤ 15 min, RTO ≤ 2 h (was 1 h / 4 h) | P0 |
| NFR-008 | Zero-downtime deployment for planned changes | Standard for all releases | P1 |
| NFR-046 | Customer portal availability | ≥ 99.9% | P0 |
| NFR-047 | Technician app functional without connectivity | 24 hours | P0 |
| NFR-048 | Payment path availability | ≥ 99.95% with multi-gateway failover | P0 |
| NFR-049 | Planned maintenance window | Outside 08:00–23:00 BST; ≤ 4 h per month; announced 72 h ahead | P1 |
| NFR-050 | Graceful degradation | Every P0 integration has a documented, tested manual fallback | P0 |
| NFR-051 | DR drill | Full failover exercised twice yearly with documented results | P0 |
| NFR-052 | Backup verification | Automated restore test weekly | P0 |

---

## 3. Scalability

| ID | Requirement | Target | Pri |
|---|---|---|:--:|
| NFR-009 | Growth headroom without re-architecture | 5× users and 10× data over 5 years | P0 |
| NFR-010 | Elastic capacity for demand peaks | Automatic scaling for seasonal and promotional peaks | P1 |
| NFR-053 | Service order volume | 5 million per year by year 5 | P0 |
| NFR-054 | Device registry | 5 million assets | P0 |
| NFR-055 | Telemetry ingestion | 50,000 points per minute | P2 |
| NFR-056 | GPS ingestion | 400 technicians at 30-second intervals sustained | P1 |
| NFR-057 | Marketplace scale | 5,000 sellers, 50,000 listings | P2 |
| NFR-058 | Branch scale | 200 branches without configuration redesign | P1 |
| NFR-059 | Multi-entity scale | 10 legal entities across 5 countries | P2 |
| NFR-060 | Document store | 50 TB with sub-10-second retrieval | P1 |

---

## 4. Security

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-011 | Role-based access control with field-level granularity | P0 |
| NFR-012 | MFA mandatory for admin, finance, HR and all privileged roles | P0 |
| NFR-013 | AES-256 at rest; TLS 1.2+ (TLS 1.3 preferred) in transit | P0 |
| NFR-014 | Complete immutable audit trail — who, what, when, before, after | P0 |
| NFR-015 | Branch-level data isolation enforced at the record level | P0 |
| NFR-061 | Field-level encryption for S3-classified data with separate key material | P0 |
| NFR-062 | Secrets held in a vault; never in code, configuration files or logs | P0 |
| NFR-063 | Malware scanning on every file upload before storage or serving | P0 |
| NFR-064 | Segregation of duties enforced by the permission engine | P0 |
| NFR-065 | Step-up authentication for sensitive actions | P0 |
| NFR-066 | Automated dependency, container and infrastructure vulnerability scanning in CI and in production | P1 |
| NFR-067 | Annual penetration test with findings tracked to closure | P1 |
| NFR-068 | Rate limiting and bot protection on all public endpoints | P0 |
| NFR-069 | Session policy: 30-minute idle timeout for external, 60-minute for internal, absolute 12-hour maximum | P0 |
| NFR-070 | All privileged sessions recorded | P1 |
| NFR-071 | Non-production environments use masked data only | P0 |
| NFR-072 | Security incident response with defined severities and breach-notification assessment | P1 |

---

## 5. Usability & Accessibility

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-016 | Full Bengali and English support in interfaces, notifications, reports and data entry | P0 |
| NFR-017 | Technician app supported on Android 11+ with 3 GB RAM on intermittent 4G | P0 |
| NFR-018 | Offline mode with automatic sync on reconnection | P0 |
| NFR-019 | Responsive design for mobile, tablet and desktop across all portals | P0 |
| NFR-020 | Low-bandwidth mode for field and rural operation | P0 |
| NFR-073 | WCAG 2.1 AA compliance on all web portals | P1 |
| NFR-074 | Bengali input including phonetic typing and voice-to-text on mobile | P1 |
| NFR-075 | New service agent reaches competence in ≤ 4 hours of training | P1 |
| NFR-076 | Walk-in intake completed in ≤ 3 minutes | P1 |
| NFR-077 | Any record reachable in ≤ 4 clicks from any starting point | P1 |
| NFR-078 | Every error message states what happened and what to do next, in the user's language | P1 |
| NFR-079 | Destructive actions require confirmation and are reversible where possible | P1 |
| NFR-080 | Consistent design system across all 12 portals — one component library, one token set | P1 |
| NFR-081 | Critical customer paths under 400 KB first load | P1 |
| NFR-082 | Technician app battery consumption ≤ 12% per 8-hour shift excluding navigation | P1 |

---

## 6. Compliance

> **Revision 2.1 — audit findings C-04 and C-05.** The previous version of this section cited
> the **Digital Security Act 2018**, which has been repealed twice, and made no reference to
> the **Personal Data Protection Act 2026**, which is the governing data protection statute in
> Bangladesh. Both errors are corrected below. Every citation carries a *verified-on* date
> under rule DoD-17.

### 6.1 Regulatory Currency — Bangladesh Statutes

| Statute | Status | Verified |
|---|---|---|
| Digital Security Act 2018 | **Repealed** by the Cyber Security Act 2023 (passed 13 September 2023) | 2026-08-12 |
| Cyber Security Act 2023 | **Repealed** by the Cyber Security Ordinance 2025 (21 May 2025) | 2026-08-12 |
| **Cyber Security Ordinance 2025** | **In force** | 2026-08-12 |
| Personal Data Protection Ordinance 2025 | Issued 6 November 2025; amended by Ordinance No. 23 of 2026 (5 February 2026); **repealed** on enactment of the Act | 2026-08-12 |
| **Personal Data Protection Act 2026 (Law 63 of 2026)** | **In force** — enacted April 2026. Complaint and enforcement mechanisms activate **~13 May 2027**, inside Wave 4 | 2026-08-12 |
| ICT Act 2006 | In force | 2026-08-12 |
| VAT and Supplementary Duty Act 2012 | In force | 2026-08-12 |
| Bangladesh Labour Act 2006 (as amended) | In force | 2026-08-12 |

### 6.2 Core Compliance Requirements

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-021 | Bangladesh VAT (Mushak) invoice format compliance — Mushak 6.3 tax invoice per the VAT and SD Act 2012 | P0 |
| NFR-022 | Bangladesh NBR income tax computation compliance | P0 |
| NFR-023 | **Bangladesh ICT Act 2006 and Cyber Security Ordinance 2025 compliance** *(corrected — audit C-04a)* | P0 |
| NFR-024 | ISO 9001:2015 audit trail and documentation requirements | P0 |
| NFR-025 | ISO 27001 security control alignment | P1 |
| NFR-083 | Bangladesh Labour Act compliance in HR and payroll | P0 |
| NFR-084 | Bangladesh e-waste and environmental handling rules | P1 |
| NFR-085 | Consumer protection obligations on marketplace transactions | P0 |
| NFR-087 | Data-subject rights supportable within legal constraints — see NFR-093 for the statutory set | P1 |
| NFR-088 | Records retention per the statutory schedule, enforced by the system | P0 |
| NFR-089 | SOC 2 / ISO 27001 readiness for enterprise and multi-country expansion | P2 |
| NFR-100 | **Mushak 9.1 monthly VAT return filed by the 15th of the following month, submitted through the NBR VAT Online portal (vat.gov.bd)** *(added — audit H-05)* | P0 |
| NFR-101 | **Input VAT credit claimable only against valid, compliant Mushak 6.3 invoices; the system must block credit claims without one** *(added — audit H-05)* | P0 |

### 6.3 Personal Data Protection Act 2026 — Statutory Obligations

> **These requirements are new.** The previous specification contained none of them.
> The regulator is the **National Data Management Authority**.

| ID | Requirement | Owning Module | Pri |
|---|---|---|:--:|
| NFR-090 | Process personal data only on consent or a stated legitimate ground, recorded per processing purpose | M33 | **P0** |
| NFR-091 | Consent must be **clear, explicit, specific and freely given**, with a heightened *specific consent* standard for sensitive personal data unless a legitimate ground applies | M33 | **P0** |
| NFR-092 | Issue a **transparency notice** before or during processing, stating data categories, purposes, risks, retention periods, third-party transfers and the withdrawal procedure | M33 | **P0** |
| NFR-093 | Support data-subject rights: **access and portability**, **rectification with controller notification within 30 days**, **erasure** on purpose cessation, consent withdrawal, unlawful processing or legal requirement, and **withdrawal of consent** through a simplified procedure | M33, M29 | **P0** |
| NFR-094 | **Notify the National Data Management Authority** of any breach likely to cause significant damage, within the prescribed timeframe | M60, M29 | **P0** |
| NFR-095 | Maintain processing records for a **minimum of five years** | M24, M29 | P0 |
| NFR-096 | **Appoint a Chief Data Officer** if the Company is classified a *significant* data fiduciary, with the role, authority and reporting line defined | M60 | **P0** |
| NFR-097 | Implement technical and organisational measures for security, integrity and confidentiality proportionate to risk | M29 | P0 |
| NFR-098 | Treat a processor's processing as the controller's own; flow equivalent obligations to every processor and sub-processor by contract | M42, M60 | P0 |
| NFR-099 | **Restrict large-scale transfer of Sensitive Personally Identifiable Data** — including government unique identifiers (NID, passport, TIN), biometric identifiers, genetic information and criminal records — notify the Authority of cross-border transfers and disclose the safeguards applied | M29, M65 | **P0** |

**Penalty exposure:** up to **BDT 25 lakh** for security failures or rights violations, and up
to **BDT 50 lakh** for significant data fiduciaries, with additional fines for repeated
violations. This exposure is registered as risk **RSK-032** in `00-04`.

### 6.4 Data Residency — Corrected Architecture Position

> **Audit finding C-05.** The previous NFR-086 mandated a single approved region, inherited
> from the v1.0 assumption of Singapore hosting. That position conflicts with NFR-099.

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-086 | **Split-residency data architecture.** Sensitive Personally Identifiable Data as defined by the PDPA 2026 — NID, passport, TIN, biometric templates, and recovered customer data held under M06 — is stored in a **Bangladesh-resident** data store. The remainder of each record may be held in the regional store. Records are joined by a resident key, never by duplicating the sensitive field. | **P0** |
| NFR-086a | The data model must carry a residency classification on every field, and the platform must enforce it at write time — not by convention | **P0** |
| NFR-086b | Any cross-border transfer of a residency-classified field requires an Authority notification record and a documented safeguard before the transfer executes | **P0** |
| NFR-086c | Non-production environments never contain unmasked residency-classified data in any region | **P0** |

**Dependency:** a **legal opinion on the split-residency design is required before the Wave 1
architecture is fixed**. This is registered as dependency **DEP-31** in `00-04` and as
decision **D-13**.

**Fields currently classified as residency-restricted:**

| Field | Entity | Owning Module |
|---|---|---|
| National ID number | `fix.identity.document` | M33 |
| Passport number | `fix.identity.document` | M33 |
| TIN | `fix.party`, `hr.employee` | M33, M21 |
| Biometric attendance template | `fix.attendance.record` | M55 |
| Recovered customer data and its index | `fix.recovered.inventory` | M06 |
| Marketplace seller KYC documents | `fix.mp.seller.document` | M12 |
| Criminal record checks (where collected) | `fix.mp.seller.document` | M12 |
| NFR-088 | Records retention per the statutory schedule, enforced by the system | P0 |
| NFR-089 | SOC 2 / ISO 27001 readiness for enterprise and multi-country expansion | P2 |

---

## 7. Maintainability & Operability

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-026 | API-first architecture with documented REST APIs for all integrations | P0 |
| NFR-027 | No-code configuration for workflows, forms, thresholds and business rules | P0 |
| NFR-028 | Customisation without modifying core product code | P0 |
| NFR-090 | Unit test coverage ≥ 80% on custom code; 100% on financial calculations | P0 |
| NFR-091 | Every module ships with an operational runbook | P0 |
| NFR-092 | Distributed tracing across all services with a single correlation id | P1 |

### Additional Operability Standards

| # | Standard |
|---|---|
| OPS-01 | Every deployment is automated, repeatable and reversible |
| OPS-02 | Configuration is versioned and promoted through environments, never hand-edited in production |
| OPS-03 | Every alert has a runbook entry; alerts without actions are removed |
| OPS-04 | Log levels are consistent; logs are structured and searchable; no personal data in logs |
| OPS-05 | Every scheduled job reports success, failure and duration; silent failure is a defect |
| OPS-06 | Feature flags allow any new capability to be disabled without a deployment |
| OPS-07 | Database migrations are forward-only, tested against a production-sized dataset, and reversible by a documented procedure |
| OPS-08 | Capacity is reviewed monthly against growth; scaling decisions are made ahead of the need |

---

## 8. Data Integrity

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-029 | All transactions ACID-compliant with full rollback | P0 |
| NFR-030 | Automated daily backups with 30-day retention; weekly with 1-year; monthly with 7-year | P0 |
| DI-01 | Financial calculations use decimal arithmetic; no floating point in money paths | P0 |
| DI-02 | Every financial posting is reconcilable to its source transaction | P0 |
| DI-03 | Referential integrity enforced at the database level, not only in application code | P0 |
| DI-04 | Offline sync guarantees zero data loss and zero double-application | P0 |
| DI-05 | Event delivery is at-least-once with idempotent consumption | P0 |
| DI-06 | Data quality tests run on every warehouse load; failures block dependent refreshes | P1 |
| DI-07 | Cross-system reconciliation runs nightly with divergence alerting | P1 |
| DI-08 | Soft deletion only; hard deletion requires an approved, logged procedure | P0 |

---

## 9. Localisation Standards

| Aspect | Standard |
|---|---|
| Primary language (field & customer) | Bengali (bn-BD) |
| Secondary language | English (en) |
| Character encoding | UTF-8 throughout |
| Bengali collation | ICU `bn-BD` for sorting and comparison |
| Bengali fonts | Rendered correctly across Android, iOS, Windows and print output |
| Bengali input | Phonetic and Unicode keyboard support; voice-to-text on mobile |
| Number format | Bangladeshi lakh/crore grouping (12,34,567) in Bengali locale; international grouping in English locale |
| Currency | BDT (৳) primary, two decimal places; multi-currency supported |
| Date format | DD/MM/YYYY; Bengali month names in the Bengali locale |
| Time | 12-hour with Bengali AM/PM equivalents; stored UTC, displayed Asia/Dhaka |
| Calendar | Gregorian with Bangladesh public holidays including moon-dependent dates |
| Fiscal year | July–June |
| Address | Division → District → Upazila/Thana → Union/Ward → Postcode |
| Phone | +880 with Bangladesh mobile operator validation |
| National ID | 10-digit and 17-digit formats validated |
| Translation completeness | 100% of user-facing strings before any module is accepted |
| Translation quality | Professionally translated and reviewed by a native speaker; machine translation is not acceptable for release |

---

## 10. Environmental & Device Support

| Category | Supported |
|---|---|
| Desktop browsers | Chrome, Edge, Firefox (latest two versions); Safari (latest two) |
| Minimum desktop resolution | 1366×768 (the common branch hardware) |
| Mobile OS — technician, rider, auditor | Android 11+ (primary); iOS 15+ (secondary) |
| Mobile OS — customer | Android 9+; iOS 14+ |
| Minimum device specification (field apps) | 3 GB RAM, 32 GB storage, GPS, camera, 4G |
| Network | Functional on 3G; optimised for 4G; full offline capability where specified |
| Peripherals | Thermal receipt printers, label printers, barcode/QR scanners, biometric devices, signature capture, queue displays, kiosks |
| Printing | A4 and thermal receipt formats; Bengali rendering verified on all supported printers |

---

## 11. Testing Standards

| Level | Coverage | Tooling Standard |
|---|---|---|
| Unit | ≥ 80% of custom code; 100% of financial and tax calculations | Framework-native, run on every commit |
| Integration | All module-to-module contracts and all external integrations against sandboxes | Automated in CI |
| Contract | Every published API validated against its OpenAPI specification | Automated in CI |
| Event | Every producer/consumer pair tested for schema compatibility and idempotency | Automated in CI |
| End-to-end | Every critical business journey (see below) | Automated, run nightly |
| Performance | Every NFR performance target, at 1.5× expected peak | Before each wave gate |
| Security | SAST, DAST, dependency scanning on every build; penetration test annually | Automated + annual engagement |
| Accessibility | WCAG 2.1 AA automated scan plus manual audit per portal | Before each portal release |
| Localisation | Translation completeness, Bengali rendering, formatting, and layout under text expansion | Before each wave gate |
| Offline | 24-hour offline operation with a scripted conflict scenario set | Before each mobile release |
| Data migration | Reconciliation and control totals on every load | Before every cutover |
| UAT | Every P0 and P1 requirement, executed by named business super-users | Before each wave gate |

### Critical Journeys Covered by End-to-End Tests

1. Book online → dispatch → field repair → invoice → pay → close → survey
2. Walk-in intake → workshop repair → estimate → approval → QC → handover → pay
3. Pick & drop collection → workshop → return delivery → invoice
4. Warranty job → claim creation → submission → approval → reimbursement → reconciliation
5. AMC sale → activation → preventive schedule → visit → renewal
6. MSP alert → ticket → remote resolution → SLA measurement → monthly service report
7. Marketplace order → seller quote → customer selection → job → review → commission → payout
8. Rental reservation → delivery → return → damage assessment → billing
9. Trade-in request → offer → intake → data wipe → refurbishment → grading → resale
10. E-waste collection → triage → destruction → recycling → disposal certificate
11. Data recovery case → custody → recovery → handover → purge certificate
12. Purchase requisition → PO → receipt → inspection → three-way match → payment
13. Payroll cycle → attendance lock → calculation → approval → BEFTN → payslips → posting
14. Complaint → non-conformance → root cause → CAPA → verification → closure
15. Month-end close → reconciliation → VAT return → management pack

---

## 12. Architecture Standards (Restated as Testable Rules)

| # | Standard | How It Is Verified |
|---|---|---|
| AS-01 | No module reads another module's tables directly | Static analysis in CI; architecture review |
| AS-02 | All custom models inherit chatter and activity mixins | Model registry check in CI |
| AS-03 | All custom models carry entity and operating-unit fields | Model registry check in CI |
| AS-04 | Naming conventions (`fix.` / `fix_`) enforced | Linter rule |
| AS-05 | OCA modules extended, not forked, without architecture approval | Repository review |
| AS-06 | State transitions declared in one place per model | Code review checklist |
| AS-07 | Every API versioned and documented in OpenAPI 3.1 | CI validation against the spec |
| AS-08 | Every write path emits its domain event through the outbox | Event coverage test |
| AS-09 | No business logic in views, controllers or portal code | Code review checklist; portal contract test |
| AS-10 | Money always uses decimal with an explicit currency | Linter rule; financial test suite |
| AS-11 | Timestamps stored UTC | Schema check |
| AS-12 | All user-facing strings translatable and translated | Translation coverage report at 100% |
| AS-13 | Offline apps use append-only journals with server-authoritative resolution | Offline test suite |
| AS-14 | S3 data encrypted at field level with access logging | Security test suite |
| AS-15 | Every module ships with tests and KPI instrumentation | Definition-of-done gate |

---

*Next document: `17_Implementation_Roadmap_and_Phasing.md`*
