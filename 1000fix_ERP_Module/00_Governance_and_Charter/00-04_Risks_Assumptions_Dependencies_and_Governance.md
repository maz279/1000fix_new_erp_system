---
id: FIX-ERP2-020
title: Risks, Assumptions, Dependencies & Governance
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Risks, Assumptions, Dependencies & Governance

---

## 1. Risk Register

Scoring: Probability (L/M/H) × Impact (Low/Med/High/Critical) → Rating.

### 1.1 Delivery & Programme Risks

| ID | Risk | Prob | Impact | Rating | Mitigation | Contingency | Owner |
|---|---|:-:|:-:|:-:|---|---|---|
| RSK-001 | Business super-user availability falls short, stalling UAT | **H** | High | **Critical** | Named super-users with time formally protected in their objectives; UAT dates in the annual plan; escalation to CEO on non-availability | Wave gate slips; development does not run ahead into unaccepted work | CEO |
| RSK-002 | Scope creep as new business lines mature during a 36-month programme | H | High | **Critical** | Formal change control; wave-locked scope; a parking lot for good ideas | Defer to a later wave; never mid-wave insertion | Steering Committee |
| RSK-003 | Programme fatigue over 36 months | M | High | High | Visible wave-by-wave value delivery; celebrate gates; rotate team assignments | Re-baseline with a shorter horizon and fewer waves | Programme Manager |
| RSK-004 | Key personnel loss (internal or vendor) | M | High | High | Two-person knowledge coverage on every module; documentation as definition-of-done; knowledge transfer sessions | Contracted backfill; extend the affected wave | CTO |
| RSK-005 | Estimate inaccuracy on the new business lines (no precedent) | M | High | High | Discovery spike before each new-line wave; re-estimate at wave start; 20% contingency on W5–W8 | Descope P2/P3 within the wave | Programme Manager |
| RSK-006 | Vendor or partner delivery failure | L | Critical | High | Milestone-based payment; penalty clauses; source-code escrow; capability assessment before award | Backup vendor shortlist; bring critical work in house | CTO |
| RSK-007 | Budget pressure mid-programme | M | High | High | Waves are independently valuable; each has a defined stop point | Stop after W4 (v1.0 complete) or W7 (revenue lines live); W8–W9 are deferrable | CFO |

### 1.2 Adoption & Change Risks

| ID | Risk | Prob | Impact | Rating | Mitigation | Contingency | Owner |
|---|---|:-:|:-:|:-:|---|---|---|
| RSK-008 | Technician rejection of the mobile app | **H** | **Critical** | **Critical** | Bengali-first design; extreme simplicity; field pilot with respected senior technicians before rollout; Company-provided devices; earnings and incentive visibility as an immediate personal benefit; champion network | Simplified "lite" mode; extended on-site support; phased feature introduction | Ops Director |
| RSK-009 | Branch staff resistance at counter operations | M | High | High | Speed as the explicit design goal with measured intake time; involve resistors in design and UAT; visible executive sponsorship | Additional training cycles; temporary dual running | Ops Director |
| RSK-010 | Marketplace sellers fail to adopt | M | High | High | Simple onboarding; fast, transparent payouts; clear scoring; seller advisory group | Reduce commission for early adopters; direct recruitment | CCO |
| RSK-011 | Corporate clients do not use the B2B portal | M | Med | Med | Account-manager-led onboarding; demonstrable time saving; incentivise portal use | Assisted service through account managers | CCO |
| RSK-012 | Management reverts to spreadsheets | M | High | High | Retire the source data for manual packs; make dashboards materially better; require decisions to cite the dashboard | Executive mandate; remove spreadsheet access to source data | CEO |

### 1.3 Technical Risks

| ID | Risk | Prob | Impact | Rating | Mitigation | Contingency | Owner |
|---|---|:-:|:-:|:-:|---|---|---|
| RSK-013 | Field connectivity worse than assumed, breaking sync | **H** | Med | High | Offline-first architecture with a 24-hour guarantee; aggressive payload compression; deferred non-critical upload; field testing in the weakest coverage areas | Extend offline window to 72 hours; SMS-based critical status fallback | CTO |
| RSK-014 | Data migration quality below usable threshold | M | High | High | Profiling before every load; cleansing in the source; trial migrations; reconciliation sign-off; archive area for uncleansable records | Manual validation of the highest-value records; phased migration | CTO |
| RSK-015 | OCA v19 migration gaps on critical modules | M | High | High | Verify migration status before each wave; fork and migrate where needed; contribute upstream | Build the specific capability as a custom module | Solution Architect |
| RSK-016 | Portal platform API contract instability | M | High | High | Agreed, versioned contract; contract tests in both CI pipelines; joint change process | Version pinning with a temporary adapter layer | CTO |
| RSK-017 | Performance inadequate at 51+ branches under real load | L | Critical | High | Load testing at 1.5× projected peak before every gate; read replicas; partitioning; caching strategy | Phased regional rollout; vertical scaling | CTO |
| RSK-018 | Offline sync conflicts corrupt data | L | Critical | High | Append-only journal; server-authoritative resolution; idempotent commands; extensive scripted conflict testing | Manual reconciliation tooling; conflict quarantine | Solution Architect |
| RSK-019 | Integration dependency on a third party that changes or fails | M | High | High | Documented fallback for every P0 integration; circuit breakers; multi-provider where possible | Manual process per the fallback register | CTO |
| RSK-020 | AI models underperform or produce unsafe outputs | M | Med | Med | Human-in-the-loop on material decisions; hard guard rails; graceful degradation to rules; model cards and drift monitoring | Disable the model; the consuming module operates on rules | CTO |
| RSK-021 | Technical debt accumulates under wave pressure | M | High | High | Architecture standards enforced in CI; refactoring capacity reserved each wave; architecture review at every gate | Dedicated remediation sprint between waves | Solution Architect |

### 1.4 Commercial & Regulatory Risks

| ID | Risk | Prob | Impact | Rating | Mitigation | Contingency | Owner |
|---|---|:-:|:-:|:-:|---|---|---|
| RSK-022 | Marketplace VAT and liability model incorrect | M | **Critical** | **Critical** | External tax and legal advice **before** Wave 7 build; principal-vs-agent decision documented and approved | Suspend marketplace transactions until corrected; restate if required | CFO |
| RSK-023 | Marketplace quality failure damages the 1000FiX brand | M | Critical | Critical | Same QC and evidence standards as owned work; performance scoring with automatic consequences; 1000FiX escalation path; seller insurance requirement | Suspend the seller; complete the job with own technicians; compensate the customer | CCO |
| RSK-024 | Data-services breach exposing customer data | L | **Critical** | High | Least privilege; dual control; field-level encryption; time-boxed retention; full access audit; staff undertakings | Incident response plan; regulatory notification; independent forensic review | CTO |
| RSK-025 | Brand partner claim rejection rate does not improve | M | High | High | Evidence completeness enforced before submission; brand rule engine per partner; quarterly brand reviews | Manual claim preparation for the affected brand; renegotiate terms | Finance Director |
| RSK-026 | Bangladesh VAT, tax or labour regulation changes mid-programme | M | High | High | Configuration-driven tax rules; monitoring of NBR announcements; country-pack isolation | Manual override during transition; expedited configuration change | CFO |
| RSK-027 | Rental asset losses exceed provision | M | Med | Med | Identity verification; deposits; condition reports; insurance; utilisation and loss monitoring | Tighten eligibility; raise deposits; reduce fleet | Corporate Services Head |
| RSK-028 | Refurbished units create warranty liability beyond provision | M | Med | Med | Rigorous grading; QA protocol; disclosed condition; warranty reserve | Adjust grading thresholds; narrow warranty terms | Retail Operations Head |
| RSK-029 | E-waste handling non-compliance | L | High | Med | Certified partners only, with certification currency checked; disposal certificates mandatory | Suspend collection until compliant partner secured | Quality Manager |
| RSK-030 | Payment gateway outage during peak | M | Med | Med | Multiple gateways; graceful degradation; cash and bank fallback | Manual payment collection; link resent on restoration | CFO |
| RSK-031 | Competitor moves faster on digital capability | M | High | High | Wave-by-wave delivery of visible customer-facing capability; do not wait for programme completion to compete | Reprioritise customer-facing waves | CEO |

### 1.4a Data Protection & Regulatory Risks *(added — audit findings C-04, C-05)*

| ID | Risk | Prob | Impact | Rating | Mitigation | Contingency | Owner |
|---|---|:-:|:-:|:-:|---|---|---|
| **RSK-032** | **Non-compliance with the Personal Data Protection Act 2026.** The Act was enacted in April 2026 and was absent from the entire specification set until the August 2026 audit. Enforcement mechanisms activate around **13 May 2027 — inside Wave 4**. Penalties reach **BDT 25 lakh** for security failures or rights violations and **BDT 50 lakh** for significant data fiduciaries, with additional fines for repeated violations. | **H** | **Critical** | **Critical** | Full PDPA obligation set added to `05-06` §6.3; consent and transparency notice built into M33 and every capture point; breach notification to the National Data Management Authority designed into M60; Chief Data Officer appointment assessed before Wave 4 | Suspend affected processing; retrospective consent campaign; regulator engagement | CFO / CTO |
| **RSK-033** | **Data residency architecture unlawful.** The specified Singapore hosting conflicts with the PDPA restriction on large-scale cross-border transfer of Sensitive Personally Identifiable Data — which the statute defines to include NID, passport, TIN and biometric identifiers, all of which this ERP holds. | **M** | **Critical** | **Critical** | Split-residency architecture specified in `05-06` NFR-086; residency classification carried on every field and enforced at write time; **legal opinion required before Wave 1 architecture is fixed (DEP-31, decision D-13)** | Re-host the sensitive-data store in Bangladesh; accept latency cost | CTO / Legal |
| **RSK-034** | **Chief Data Officer not appointed** where the Company qualifies as a significant data fiduciary. At 250,000+ customers per month, qualification is likely. | M | High | High | Classification assessment commissioned before Wave 4; role, authority and reporting line defined in M60 | Interim appointment from within Legal or Compliance | CEO |
| **RSK-035** | **Regulatory citations drift out of date.** The specification cited a statute repealed twice, and a withdrawn NIST revision, because no currency-review control existed. | M | High | High | Every statutory and standards citation carries a *verified-on* date; re-verified at each wave gate (register rule DoD-17) | Emergency review and correction | CTO |
| **RSK-036** | **Cost estimate materially understated.** The business case was modelled on 834 person-weeks across 30 modules; the restated architecture is ~1,302 PW across 67. The Board may have been given a figure that is 60–80% low. | **H** | High | **Critical** | TCO restated as provisional in `00-02`; re-baselined at each category's completion; not presented as final until all 67 specifications exist | Descope Categories D, F, I or J; defer Waves 8–9 | CFO |

### 1.5 Risk Heat Summary

| Rating | Count | Requires |
|---|---:|---|
| Critical | 5 | Steering Committee review every meeting; named owner reports monthly |
| High | 16 | PMO tracking; owner reports at each wave gate |
| Medium | 10 | Register review quarterly |

**The five Critical risks — RSK-001 (super-user availability), RSK-002 (scope creep),
RSK-008 (technician adoption), RSK-022 (marketplace tax/liability) and RSK-023 (marketplace
quality) — are the ones that can end the programme.** Everything else is manageable.

---

## 2. Assumptions

| ID | Assumption | If False | Owner |
|---|---|---|---|
| ASM-01 | All service centres have at least 3G connectivity during operating hours | Extended offline windows; SMS fallback; connectivity investment required | CTO |
| ASM-02 | Technicians will use Company-issued Android 11+ devices | Device procurement cost added; app support matrix widened | Ops Director |
| ASM-03 | Existing customer and device data is exportable at ≥ 80% quality | Migration effort increases materially; manual cleansing programme required | CTO |
| ASM-04 | The 17+ brand partnerships continue through the programme | Warranty benefit case reduces; claim automation value falls | CEO |
| ASM-05 | Bangladesh VAT rates and Mushak format remain broadly stable | Configuration changes required; possible rework of tax reporting | CFO |
| ASM-06 | Business stakeholders commit the stated time | Waves slip; this is RSK-001, the highest-rated risk | CEO |
| ASM-07 | The portal platform exposes and maintains documented, versioned APIs | Integration effort increases; adapter layer required | CTO |
| ASM-08 | bKash, Nagad and SSLCOMMERZ provide sandbox and production access on schedule | Payment go-live slips; cash-only fallback at counters | CFO |
| ASM-09 | ~~Cloud hosting in the Singapore region remains available with acceptable latency~~ — **superseded (audit C-05)**. Regional hosting remains the assumption for non-sensitive data, but **sensitive personal data must be Bangladesh-resident** under the PDPA 2026. See NFR-086 and DEP-31. | Split-residency architecture; legal opinion pending | CTO |
| **ASM-21** | **A Bangladesh-resident data store of adequate reliability and performance is procurable.** If no compliant local option meets the availability targets, the architecture must be re-planned. | Assess local providers before Wave 1; consider on-premises if necessary | CTO |
| **ASM-22** | **PDPA enforcement timing holds** at approximately 13 May 2027. An earlier activation compresses the compliance window inside Wave 4. | Monitor Authority announcements; treat W4 as the compliance deadline regardless | CFO / Legal |
| ASM-10 | No major organisational restructuring during the programme | Re-baseline required | CEO |
| ASM-11 | Odoo 19 remains supported through the programme; upgrade to a later version is a separate project | Upgrade project added to the roadmap | CTO |
| ASM-12 | OCA critical-path modules complete v19 migration or can be migrated by the Company | Custom development substitutes; effort increases | Solution Architect |
| ASM-13 | Marketplace seller supply exists in the target categories and areas | Marketplace benefit case reduces; owned capacity remains the constraint | CCO |
| ASM-14 | Corporate demand for managed services exists at the assumed price point | MSP benefit case reduces; pricing revisited | Corporate Services Head |
| ASM-15 | Bengali-capable open-weight language models remain available and adequate | Commercial LLM API considered, with data-residency implications | CTO |
| ASM-16 | Go-live does not fall in Ramadan, Eid-ul-Fitr or Eid-ul-Adha peak periods | Wave dates adjusted | Programme Manager |
| ASM-17 | Third-party API costs remain within the projected envelope | Budget variance; usage optimisation required | CFO |
| ASM-18 | Historical financial data for at least three years is available in structured form | Reduced comparative reporting at go-live | CFO |
| ASM-19 | Technicians can read Bengali interfaces | Icon-led and voice-led interface variants required | Ops Director |
| ASM-20 | Biometric attendance hardware is procured before Wave 5 | GPS-based clock-in used as the sole mechanism | HR Director |

---

## 3. Dependencies

### 3.1 Internal

| ID | Dependency | Needed By | Owner | Impact If Late |
|---|---|---|---|---|
| DEP-01 | Chart of accounts restructured for the dimensional model | W3 start | CFO | Finance configuration blocked |
| DEP-02 | Payroll structures, tax parameters and PF rules confirmed | W5 start | HR Director | Payroll configuration blocked |
| DEP-03 | Service catalogue and rate cards finalised and approved | W3 start | CCO | Pricing engine cannot be configured |
| DEP-04 | Contract product definitions for all 14 families | W4 start | CCO | Contract engine cannot be configured |
| DEP-05 | Legacy data extracted, profiled and cleansed | Per wave | Department heads | Migration slips; go-live slips |
| DEP-06 | Super-users named, trained and time-protected | Each wave | Department heads | UAT fails — RSK-001 |
| DEP-07 | Branch connectivity and hardware readiness | Per rollout site | IT Administrator | Site rollout blocked |
| DEP-08 | Technician devices procured and enrolled | W2 | Ops Director | Field rollout blocked |
| DEP-09 | Marketplace commercial model decided (commission, liability, settlement) | W7 minus 3 months | CEO + CFO | Marketplace build blocked — RSK-022 |
| DEP-10 | Rental and refurbishment legal-entity decision | W6 minus 3 months | CFO | Finance structure blocked |
| DEP-11 | Telephony vendor selected | W4 minus 2 months | CTO | Contact centre build blocked |
| DEP-12 | Data-services facility, controls and staff undertakings in place | W6 | Technical Services Head | Data services cannot launch |
| DEP-13 | Multi-country target markets decided | W9 minus 3 months | CEO | Country pack cannot be specified |
| DEP-14 | Quality management system documentation current | W5 | Quality Manager | QMS configuration blocked |
| DEP-15 | Biometric attendance hardware installed | W5 | IT Administrator | GPS-only fallback |

### 3.1a Regulatory Dependencies *(added — audit findings C-04, C-05)*

| ID | Dependency | Owner | Needed By | Impact If Late |
|---|---|---|---|---|
| **DEP-31** | **Legal opinion on the split-residency data architecture** — confirming which fields must be Bangladesh-resident under the PDPA 2026 and what safeguards permit cross-border processing of the remainder | CTO + Legal | **Before Wave 1 architecture is fixed** | The whole data architecture is built on an unverified assumption; retrofitting residency into a live system is the most expensive class of rework |
| **DEP-32** | **Significant data fiduciary classification assessment** — determining whether 1000FiX must appoint a Chief Data Officer under the PDPA | CEO + Legal | W4 minus 3 months | Statutory non-appointment; penalty exposure |
| **DEP-33** | **Registration or notification with the National Data Management Authority**, if required for a controller of this scale | Legal | W4 minus 3 months | Operating without required registration |
| **DEP-34** | **PDPA-compliant transparency notice text**, drafted in Bengali and English for every capture point | Legal + CCO | W1 build | Consent captured without a valid notice is not valid consent |
| **DEP-35** | **Media sanitisation programme document** naming IEEE 2883 as the approved technique standard, per NIST SP 800-88r2 | Quality Manager | W6 minus 2 months | M06 certificates cite no approved standard and are not defensible |

### 3.2 External

| ID | Dependency | External Party | Needed By | Impact If Late |
|---|---|---|---|---|
| DEP-16 | bKash API access (sandbox then production) | bKash | W3 | Mobile money unavailable |
| DEP-17 | Nagad API access | Nagad | W3 | Reduced payment options |
| DEP-18 | SSLCOMMERZ integration | SSLCOMMERZ | W3 | Card payments unavailable |
| DEP-19 | WhatsApp Business API approval | Meta / BSP | W1 | WhatsApp channel unavailable |
| DEP-20 | SMS gateway contracts (primary and failover) | SMS providers | W1 | Notifications limited to push and email |
| DEP-21 | Google Maps Platform commercial terms | Google | W2 | Mapping and geocoding limited to OSM |
| DEP-22 | Brand partner claim format specifications | 17+ brands | W4 | Claim automation limited to manual formats |
| DEP-23 | BEFTN file format confirmation | Banking partner | W5 | Manual salary disbursement |
| DEP-24 | NBR e-VAT submission specification | NBR | W4 | Manual VAT filing |
| DEP-25 | Courier partner API access | Pathao / RedX / others | W3 | Internal riders only |
| DEP-26 | Telephony carrier interconnect for 16743 | Telecom operator | W4 | Hotline remains outside the system |
| DEP-27 | Identity verification service agreement | KYC provider | W7 | Manual seller verification |
| DEP-28 | Certified e-waste recycling partners | Recycling partners | W8 | E-waste programme cannot launch |
| DEP-29 | External tax and legal opinion on the marketplace model | Advisors | W7 minus 3 months | Marketplace blocked — RSK-022 |
| DEP-30 | Accredited e-signature provider agreement | Trust service provider | W3 | Operational signatures only; contracts remain wet-signed |

---

## 4. Constraints

| ID | Constraint | Type | Consequence |
|---|---|---|---|
| CON-01 | Three-year budget envelope of $455K–780K | Budget | W8 and W9 are the first deferral candidates |
| CON-02 | v1.0 committed scope must be delivered by Month 18 | Schedule | Waves 1–4 cannot be reordered |
| CON-03 | The Next.js 15 + Payload CMS portal platform cannot be replaced | Technical | ERP integrates; API contract discipline is mandatory |
| CON-04 | All financial transactions must comply with Bangladesh NBR requirements | Regulatory | Compliance is a P0 gate, not a feature |
| CON-05 | Bengali must be the primary language for field and customer surfaces | Technical | Translation is a definition-of-done item, not a follow-up |
| CON-06 | bKash and Nagad must be primary payment methods | Technical | Bangladesh-specific gateway integration is mandatory |
| CON-07 | Field applications must operate offline | Technical | Offline-first architecture is non-negotiable |
| CON-08 | No go-live during Ramadan or the Eid periods | Operational | Wave dates account for the Islamic calendar |
| CON-09 | Data must be hosted in an approved South/Southeast Asian region | Technical | Cloud region constrained |
| CON-10 | Automation must augment roles, not displace staff without approval | Organisational | Change messaging and redeployment planning required |
| CON-11 | ISO 9001:2015 certification must be maintained throughout | Regulatory | Process changes require QMS documentation updates in step |
| CON-12 | Business super-user time is finite | Resource | UAT capacity, not developer capacity, paces the programme |

---

## 5. Governance

### 5.1 Structure

```
                    ┌──────────────────────────────┐
                    │     BOARD                     │
                    │  Investment approval          │
                    │  Quarterly programme review   │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │  ERP STEERING COMMITTEE       │
                    │  CEO (chair) · CTO · CFO ·    │
                    │  CCO · Ops Director ·         │
                    │  HR Director · Quality Manager│
                    │  Monthly · Gate decisions ·   │
                    │  Change control · Risk        │
                    └───────────────┬───────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼────────┐        ┌─────────▼─────────┐      ┌──────────▼─────────┐
│ PROGRAMME      │        │ ARCHITECTURE      │      │ BUSINESS OWNERS    │
│ MANAGEMENT     │        │ REVIEW BOARD      │      │ FORUM              │
│ OFFICE         │        │ CTO · Architect · │      │ 17 module owners   │
│ Weekly         │        │ Leads · Security  │      │ Fortnightly        │
│ Plan · Risk ·  │        │ Fortnightly       │      │ Requirements ·     │
│ Report · Change│        │ Standards · ADRs  │      │ UAT · Adoption     │
└───────┬────────┘        └───────────────────┘      └────────────────────┘
        │
┌───────▼─────────────────────────────────────────────────────────────────┐
│  DELIVERY SQUADS                                                        │
│  Service · Commercial · Supply · Finance · People · Platform · Data     │
│  Daily stand-up · Fortnightly sprint · Sprint review with owners        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Decision Rights

| Decision | Authority |
|---|---|
| Programme investment and continuation | Board |
| Wave Go/No-Go | Steering Committee |
| Scope change affecting a P0 or P1 requirement | Steering Committee |
| Scope change within a module (P2/P3) | PMO with the business owner |
| Architecture standard change | Architecture Review Board |
| Technology selection (new L4/L5) | Architecture Review Board |
| New L6 commercial component | CFO on Architecture Board recommendation |
| Requirement acceptance at UAT | Named business owner |
| Risk acceptance (Critical or High) | Steering Committee |
| Risk acceptance (Medium or below) | PMO |
| Segregation-of-duties exception | CFO or CTO, time-boxed |
| Production emergency change | CTO, with retrospective Steering review |

### 5.3 Cadence

| Forum | Frequency | Output |
|---|---|---|
| Daily stand-up (per squad) | Daily | Impediments raised |
| Sprint review | Fortnightly | Working software demonstrated to business owners |
| Business Owners Forum | Fortnightly | Requirement decisions, UAT scheduling, adoption issues |
| Architecture Review Board | Fortnightly | Standards decisions, architecture decision records |
| PMO report | Weekly | Progress, risks, issues, decisions needed |
| Steering Committee | Monthly | Escalations, change control, risk review, benefit tracking |
| Wave gate review | Per wave | Formal Go/No-Go with evidence |
| Board review | Quarterly | Investment, benefit realisation, strategic alignment |
| Post-implementation review | Month 42 | Independent benefits audit |

### 5.4 Change Control

```
Change raised
   │
   ├─► Impact assessment: scope · cost · schedule · risk · benefit
   │
   ├─► Classification
   │      P2/P3 within a module ──► PMO + business owner ──► approve/defer
   │      P0/P1, or cross-module, or cost impact ──► Steering Committee
   │      Architecture standard ──► Architecture Review Board
   │
   ├─► Decision recorded with rationale
   │
   └─► Baseline updated · affected documents versioned · communicated
```

**Rules**

- No change is implemented before it is approved and recorded.
- No wave absorbs a change mid-wave; approved changes enter the next wave.
- A change that removes scope must state which benefit is forgone.
- The change log is reviewed at every Steering Committee meeting.

### 5.5 Reporting

| Report | Audience | Frequency | Content |
|---|---|---|---|
| Squad status | PMO | Weekly | Sprint progress, impediments |
| Programme dashboard | Steering Committee | Monthly | Wave progress, requirement burn-up, risk heat, budget, benefit tracking |
| KPI dashboard | Benefit owners | Monthly | Every KPI against baseline and target with variance commentary |
| Gate report | Steering Committee | Per wave | Evidence against every gate criterion |
| Board pack | Board | Quarterly | Investment, benefits, risks, strategic alignment |
| Adoption report | Steering Committee | Monthly during rollout | Usage by role and branch; intervention where lagging |

---

## 6. Decisions Required Before Wave 1

These five decisions block or materially shape the build and must be made before the
programme starts.

| # | Decision | Owner | Needed By | Consequence If Delayed |
|---|---|---|---|---|
| D-01 | Approve the expanded scope, budget and 36-month horizon | Board / CEO | Before kickoff | Programme cannot start |
| D-02 | Confirm and protect business super-user availability across all waves | CEO + department heads | Before kickoff | RSK-001 materialises; waves slip |
| D-03 | Marketplace commercial model — principal vs agent, commission structure, settlement terms, liability position | CEO + CFO + Legal | W7 minus 3 months | RSK-022; Wave 7 blocked |
| D-04 | Legal-entity structure for rental and refurbished resale | CFO + Legal | W6 minus 3 months | Finance design blocked; possible rework |
| D-05 | Multi-country target markets and sequence | CEO | W9 minus 3 months | Country pack cannot be specified |
| **D-13** | **Approve the split-residency data architecture** — Bangladesh-resident store for sensitive personal data, regional store for the remainder — subject to the legal opinion in DEP-31 | **CTO + CFO + Legal** | **Before Wave 1 architecture is fixed** | **The entire data architecture is blocked. This is now the most urgent open decision in the programme.** |
| **D-14** | Accept the restated provisional TCO of $620K–$1,050K, or direct a descope | Board / CEO / CFO | Before the next Board review | The Board is working from a figure the audit found to be 60–80% low |
| **D-15** | Confirm whether the Company qualifies as a *significant data fiduciary* and, if so, appoint a Chief Data Officer | CEO + Legal | W4 minus 3 months | Statutory non-appointment |

### Secondary Decisions

| # | Decision | Owner | Needed By |
|---|---|---|---|
| D-06 | Telephony vendor for hotline 16743 | CTO | W4 minus 2 months |
| D-07 | Whether to adopt a commercial RMM agent (L6) | CTO + CFO | W5 |
| D-08 | Data residency posture for recovered customer data | CTO + Legal | W6 minus 2 months |
| D-09 | Whether 1000FiX guarantees marketplace work to the customer | CEO + Legal | W7 minus 3 months |
| D-10 | Seller insurance requirement and liability caps | Legal | W7 minus 3 months |
| D-11 | Technician device procurement model (Company-issued vs allowance) | Ops Director + CFO | W2 minus 2 months |
| D-12 | Refurbished warranty terms and reserve policy | CFO + Retail Head | W6 |

---

## 7. Programme Closure

| Criterion | Evidence |
|---|---|
| All wave gates passed | Signed gate reports |
| All P0 and P1 requirements delivered or formally superseded | Traceability matrix at 100% |
| All legacy systems and manual processes decommissioned | Decommission register complete |
| All documentation handed over and accepted | Document register; acceptance signature |
| Support model transitioned to steady state | Support agreement in force; runbooks accepted |
| Team knowledge transferred | Handover sessions completed; two-person coverage verified |
| Benefits tracking established and running | KPI dashboard live with named owners |
| Outstanding items transferred to business-as-usual backlog | Backlog accepted by the CTO |
| Final financial reconciliation of programme spend | CFO sign-off |
| Lessons learned documented | Retrospective report to the Board |

**Post-implementation review at Month 42** — an independent audit of benefit realisation
against this business case, reported to the Board.

---

## 8. What Would Make This Programme Fail

Stated plainly, because a risk register can obscure the obvious:

1. **The business does not free up its people.** Software can be built; it cannot be
   accepted, tested, trained or adopted without the business. This is the single largest risk.
2. **Technicians reject the app.** Four hundred people in the field decide whether this
   programme works. If the app is slower than paper, they will not use it, and everything
   downstream — dispatch, inventory, invoicing, warranty, quality — degrades.
3. **Scope grows continuously.** Thirty-six months is long enough for the business to change
   twice. Without ruthless change control, the programme never finishes.
4. **The marketplace is launched before the tax and liability model is settled.** This is the
   one decision that could create a restatement or a regulatory problem.
5. **Benefits are never measured.** If baselines are not captured before each wave, no benefit
   can be claimed honestly, and the business case becomes decoration.

Each of these is addressable. None of them is a technology problem.

---

## 9. Approval

| Role | Name | Decision | Date | Conditions |
|---|---|---|---|---|
| Chief Executive Officer | | | | |
| Chief Technology Officer | | | | |
| Chief Financial Officer | | | | |
| Chief Commercial Officer | | | | |
| Service Operations Director | | | | |
| HR Director | | | | |
| Quality Manager | | | | |

---

*End of the 1000FiX ERP System v2.0 module, feature and function definition.*
*Return to `00_MASTER_INDEX_and_Document_Map.md` for navigation.*

---

*1000FiX Services Limited*
*586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh*
*Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
