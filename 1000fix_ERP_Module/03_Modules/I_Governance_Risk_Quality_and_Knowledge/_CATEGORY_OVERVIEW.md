---
id: FIX-ERP2-CAT-I
category: I
category_name: Governance, Risk, Quality & Knowledge
module_count: 4
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT
---

# Category I — Governance, Risk, Quality & Knowledge

**4 modules · Category owner: Quality Manager / Chief Financial Officer**

---

## 1. What Belongs in This Category

Proving the business is well run — and keeping what it knows.

1000FiX is **Bangladesh's only ISO 9001:2015 certified IT service provider**. That
certification is a commercial differentiator quoted in every corporate tender, and an
operational obligation that requires documented, traceable, continually improved processes.

If a capability answers *"can we demonstrate this to an auditor, a regulator, a brand
partner or a court"* — or *"how do we not lose what our best technician knows"* — it belongs
here.

---

## 2. Modules

| ID | Module | Status | Priority | Wave | One-Line Definition |
|---|---|---|:--:|:--:|---|
| **M23** | Quality Management System | Re-scoped | P1 | W5 | ISO 9001:2015 operating system: policies, process register, checklists, non-conformance, CAPA, internal audit, management review |
| **M60** | Governance, Risk & Compliance ★ | New | P2 | W6 | Enterprise risk register, internal control framework, controls testing, compliance obligations, legal matters, insurance, licences |
| **M24** | Document, Records & E-Signature | Re-scoped | P1 | W3 | Every document: storage, versioning, templates, signature, retention, legal hold, disposal, evidence packs |
| **M61** | Knowledge Management & Technical Library ★ | New | P2 | W6 | Repair manuals, wiring diagrams, solution articles, troubleshooting trees, tribal knowledge, brand bulletins and recall notices |

★ = new in v2.1 after enterprise benchmarking.

---

## 3. Why Quality and GRC Are Separate

Both run investigations and both produce actions, which tempts a merge. They answer to
different authorities and operate on different timescales.

| | M23 Quality Management | M60 Governance, Risk & Compliance |
|---|---|---|
| **Question** | "Is the work right, and are our processes improving?" | "Is the enterprise controlled, compliant and protected?" |
| **Scope** | Service delivery processes | The whole company, including finance, legal, security, third parties |
| **Standard** | ISO 9001:2015 (and ISO 27001 operational controls) | Internal control framework; statutory obligations; contractual obligations |
| **Objects** | Non-conformance, CAPA, audit finding, checklist, complaint | Risk, control, control test, obligation, legal matter, policy exception, insurance policy, licence |
| **Cadence** | Continuous, transactional | Quarterly assessment, annual attestation |
| **Audience** | Certification body, brand partners, customers | Board, auditors, regulators, insurers |
| **Analogue** | SAP *QM* · IFS *Quality Management* | SAP *GRC* · Oracle *Risk Management Cloud* |

**Rule:** M23 owns process quality; M60 owns enterprise control. A repeated quality failure
that becomes a systemic exposure is escalated from M23 into M60's risk register.

---

## 4. Why Knowledge and Documents Are Separate

This distinction is invisible until it is missing, and then it is expensive.

| | M24 Document & Records | M61 Knowledge Management |
|---|---|---|
| **Content** | Records of what happened — invoices, contracts, service reports, certificates, evidence packs | Knowledge of how to do things — repair procedures, wiring diagrams, fault→fix mappings, technique notes |
| **Value** | Legal and audit defensibility | Technician capability and first-time fix rate |
| **Lifecycle** | Created once, retained, disposed at end of retention | Continuously revised, rated, superseded |
| **Access** | Restricted, controlled, logged | Broad, searchable, offline on the technician app |
| **Quality measure** | Retrievability and integrity | Usefulness — does it resolve the fault? |
| **Analogue** | Records management / DMS | Service knowledge base / IFS *Knowledge Management* |

**Why 1000FiX needs M61 specifically:** the business plan describes a knowledge base with FAQ
articles, troubleshooting guides, video tutorials and user manuals. More importantly, a
company doing board-level repair across 17 brands carries enormous undocumented expertise in
a small number of senior technicians. That is a single point of failure.

---

## 5. Category Boundary Map

| Capability | Owned By | Not Owned By |
|---|---|---|
| Quality checklist templates | **M23** | M01, M31 (execute them) |
| Checklist execution and result | **M01** / **M31** | M23 (defines and analyses) |
| Non-conformance, root cause, CAPA | **M23** | M34, M59 |
| Customer-facing complaint and resolution communication | **M34** (Category B) | M23 |
| Safety incident and investigation | **M59** (Category H) | M23 |
| Internal audit programme | **M23** for process audits; **M60** for control audits | — |
| Enterprise risk register | **M60** | M23 (quality risks feed it) |
| Internal control definition and testing | **M60** | M19 (executes controls) |
| Compliance obligation register | **M60** | M51 (executes tax obligations) |
| Legal matters, litigation, IP, licences | **M60** | — |
| Insurance policies and claims | **M60** | M13, M46 (raise claims) |
| Segregation-of-duties rules | **M29** enforces; **M60** defines and tests | — |
| Document storage, versioning, retention | **M24** | All modules file into it |
| E-signature envelopes | **M24** | M08, M13, M12 (all request signatures) |
| Repair procedures, diagrams, solution articles | **M61** | M22 (turns them into courses) |
| Training courses and assessment | **M22** (Category H) | M61 |
| Brand technical bulletins and recall notices | **M61** receives; **M01** acts | — |
| Evidence pack assembly for a claim or audit | **M24** | M09, M23 (request them) |

---

## 6. ISO 9001:2015 Clause Coverage

M23 is not a document library that mentions ISO. It is the operating system of the
management system, clause by clause.

| Clause | Requirement | Where It Lives |
|---|---|---|
| 4 — Context | Organisation context, interested parties | M23 |
| 5 — Leadership | Policy, roles, responsibilities | M23 |
| 6 — Planning | Risks and opportunities, quality objectives | M23 → M60 |
| 7.1.5 — Monitoring & measuring resources | Calibration of test equipment | **M45** |
| 7.2 — Competence | Competency framework, certification | **M22** |
| 7.5 — Documented information | Document and records control | **M24** |
| 8.2 — Customer requirements | Service order, contract, entitlement | M01, M08 |
| 8.4 — External providers | Supplier and seller qualification and control | **M42**, **M12** |
| 8.5.1 — Production & service provision | Checklists, work instructions, traceability | M01, M31, M61 |
| 8.5.2 — Identification & traceability | Asset registry, parts genealogy | **M17**, **M15** |
| 8.6 — Release of products | QC gate before completion | M01, M31 |
| 8.7 — Nonconforming output | Non-conformance handling | M23 |
| 9.1 — Monitoring & measurement | KPIs, CSAT | M25, M34 |
| 9.2 — Internal audit | Audit programme and findings | M23 |
| 9.3 — Management review | Structured review with required inputs | M23 |
| 10 — Improvement | CAPA and effectiveness verification | M23 |

**The point:** ISO compliance is distributed across the whole ERP by design. M23 is the
module that proves it, not the module that does all of it.

---

## 7. Statutory Retention Schedule (M24)

| Document Class | Retention | Basis |
|---|---|---|
| Financial transactions, invoices, Mushak documents | 7 years | Companies Act / NBR |
| Customer records | 7 years after last transaction | Business law |
| Service and repair records | 5 years | Operational and warranty |
| Warranty claim evidence | 7 years | Brand partner audit |
| Employee records | 10 years after termination | Bangladesh Labour Act |
| Payroll and tax records | 7 years | NBR |
| Audit logs and access records | 5 years | ICT Act / ISO 27001 |
| Data-recovery case records | 5 years; recovered data purged per agreement | ISO 27001 / DSA 2018 |
| Data destruction certificates | 7 years | Customer assurance |
| E-waste disposal certificates | 7 years | Environmental compliance |
| Contracts | 7 years after expiry | Contract law |
| ISO management-system records | 3 certification cycles | ISO 9001 |
| Marketplace seller agreements and KYC | 7 years after termination | Regulatory and dispute |
| Health and safety incident records | 10 years | Labour Act |

---

## 8. Category KPIs

| KPI | Baseline | Target | Owning Module |
|---|---|---|---|
| ISO 9001 surveillance major non-conformances | unknown | **Zero** | M23 |
| CAPA closed on time | unmeasured | > 95% | M23 |
| CAPA effectiveness verified | unmeasured | > 90% | M23 |
| Repeat non-conformance from the same root cause | unmeasured | < 5% | M23 |
| Internal audit plan completion | manual | 100% | M23 |
| Rework rate (company-wide) | unmeasured | < 3% | M23 |
| Enterprise risks with a current owner and review date | n/a | 100% | M60 |
| Key controls tested per cycle | n/a | 100% | M60 |
| Compliance obligations with evidence of discharge | n/a | 100% | M60 |
| Licences and insurance current | manual | 100% | M60 |
| Documents auto-filed from transactions | 0% | > 96% | M24 |
| Document retrieval time | minutes to days | < 10 seconds | M24 |
| Paper documents in active use | 100% | **Zero by W6** | M24 |
| Evidence pack assembly time | hours | < 5 minutes | M24 |
| Retention violations | unknown | **Zero** | M24 |
| Knowledge articles covering top 100 fault codes | 0% | 100% | M61 |
| First-time fix improvement attributable to knowledge use | n/a | +4 percentage points | M61 |
| Knowledge article usefulness rating | n/a | > 4.0 / 5 | M61 |

---

## 9. Category Delivery Sequence

```
W3   M24 Document & Records ──────► every module needs somewhere to file
W5   M23 Quality Management ──────► ISO operating system live
W6   M60 Governance, Risk & Compliance ─┐
     M61 Knowledge Management ──────────┴──► control and capability
```

M24 comes early because it is infrastructure: from Wave 3 onward every module generates
documents that must be retained and retrievable.

---

## 10. Category Risks

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| ISO certification jeopardised during transition | **Critical** — commercial differentiator lost | QMS documentation updated in step with every process change; certification body informed of the programme | M23 |
| Quality module becomes a document graveyard | High — no actual improvement | CAPA effectiveness verification is mandatory; repeat non-conformance triggers management review | M23 |
| Risk register written once and never revisited | Medium | Quarterly review is a governance obligation, tracked as a KPI | M60 |
| Records disposed of before retention expiry | High — legal exposure | Disposal is system-enforced, never manual; legal hold overrides retention | M24 |
| Senior technicians retire with undocumented expertise | High — capability loss across board-level repair | Knowledge capture is a definition-of-done item on complex repairs; articles rated and maintained | M61 |
| Knowledge base becomes stale and distrusted | Medium | Article review dates; usefulness ratings; unused or low-rated articles flagged for revision | M61 |

---

*Category I · 1000FiX ERP System v2.0*
