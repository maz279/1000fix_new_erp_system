# Architecture, Tech Stack & Infrastructure Audit Report
**Document Under Audit:** `roadmap/IR-002_Final_Production_Implementation_Roadmap.md` (4,360 lines)  
**Auditor:** Explorer 1 (Architecture, Tech Stack & Infrastructure Auditor)  
**Date:** 2026-09-29  
**Status:** COMPLETE  

---

## Executive Summary

An exhaustive, line-by-line audit of `IR-002_Final_Production_Implementation_Roadmap.md` was conducted against the project's architectural ground truth (`primary-doc/`, `project-guide-doc/`, `AR-001`, `AR-004`, `PE-001`…`PE-009`) and domain skills (`erp-architect`, `erp-devops`, `erp-database`). 

The audit revealed that `IR-002` was derived from `IR-001` via a mechanical update script (`update_roadmap.py`) that performed coarse string replacements. While this script successfully modernized high-level names, it introduced **critical technical contradictions, scrambled narratives, missing architectural diagrams, absent monorepo configurations, and obsolete runtime baselines**.

A total of **13 major architectural and infrastructure discrepancy classes** were identified, catalogued with exact line numbers, evidence quotes, impact analyses, and surgical remediation specifications.

---

## Summary Matrix of Audit Findings

| Finding ID | Domain | Description | Severity | Line Numbers in IR-002 |
|---|---|---|:---:|---|
| **ARC-01** | Identity & Metadata | Document identity collision: File named `IR-002` continuously cites `IR-001` | Medium | Lines 2, 30, 91, 212, 299–301, 3580, 3916–4357 |
| **ARC-02** | Architecture (C4) | Total omission of C4 Model specifications and visual blueprints | High | Whole document (0 mentions of C4 / 0 diagrams) |
| **ARC-03** | Architecture (ADRs) | Missing ADR cross-references in Phase Milestone and Task tables | High | Lines 756, 1073, 1486, 1620, 1705, 1838, 1913, 2194, 2603, 3336 |
| **ARC-04** | Tech Stack (Ceph S3) | False claim of Ceph archival and AIStor commercialization (MinIO residue) | Critical | Lines 371 (`B-19`), 456–480 (`D-028`), 478, 1102, 3648, 4151–4160, 4321–4322 |
| **ARC-05** | Tech Stack (Licensing) | Inaccurate classification of Apache-2.0 and LGPL as "restricted licences" | High | Lines 374 (`B-22`), 497–515 (`D-030`), 4207 (`IRB-06`), 4323–4325 |
| **ARC-06** | Tech Stack (PostgreSQL) | Mathematical & chronological errors regarding PostgreSQL 17 EOL | High | Lines 373 (`B-21`), 481–496 (`D-029`), 2688 (`P09-M02-T01`), 4181–4190 |
| **ARC-07** | Tech Stack (Next.js) | Scrambled Next.js 16.3 release dates and EOL assertions (Next 15 residue) | High | Lines 352 (`B-07`), 436–445, 4171–4180 (`IRB-03`), 4236 |
| **ARC-08** | Tech Stack (Node.js) | Deprecated Node.js 20 LTS specified after official End-of-Life | High | Lines 988 (`P02-M02-T02`), 1376, 3475 |
| **ARC-09** | Monorepo & Tooling | Omission of root monorepo files (`turbo.json`, `pnpm-workspace.yaml`, `pyproject.toml`) | Critical | Lines 1000–1075 (`P02-M03`), 1118 (`P02-M06-T01`) |
| **ARC-10** | DevOps & Orchestration | Missing Terraform IaC, K3s manifests, Helm charts, and container limits | High | Lines 163, 1063 (`infra/`), 1288 (`P02-M09-T09`) |
| **ARC-11** | SRE & Resilience | Total absence of Chaos Engineering and split-brain resilience validation | High | Whole document (0 mentions of Chaos Engineering) |
| **ARC-12** | Orchestration (Airflow) | Inaccurate representation of Apache Airflow DAGs as visual configurations | Medium | Lines 1467 (`P03-M03-T09`), 2175–2176, 2280 (`P07-M02-T06`) |
| **ARC-13** | Frontend Topology | Portal count discrepancy across document (6 vs 7 vs 8 Next.js applications) | Medium | Lines 65, 108, 158, 665, 1049–1050, 3799–3811, 4175 |

---

## Detailed Audit Findings & Surgical Remediations

### Finding ARC-01: Document Identity & Metadata Discrepancy
- **Exact Line Numbers:** Lines 2, 30, 91, 212, 299–301, 3580, 3916, 3924, 3930, 3990, 4063, 4081, 4089, 4117, 4132, 4222, 4231, 4357.
- **Direct Observation:** The file is named `IR-002_Final_Production_Implementation_Roadmap.md`, but line 2 specifies `id: IR-001`, line 30 displays `# IR-001 — Implementation Roadmap & Full-Stack Developer Execution Guide`, and line 91 sets precedence for `7. THIS ROADMAP IR-001`. Throughout Appendix G and Appendix I, the document describes itself as `IR-001 v1.2`.
- **Root Cause:** When `update_roadmap.py` generated `IR-002`, it updated `version: 2.0` and `status: "FINALIZED FOR PRODUCTION"`, but failed to update the identifier `id: IR-001` and its textual occurrences.
- **Technical & Governance Impact:** Breaches Document Control rule `GV-011` and `PG-05` (permanent, unambiguous document identifiers). In contractual and audit reviews, it creates confusion between the baseline roadmap and subsequent revisions.
- **Surgical Remediation Recommendation:**
  1. Change line 2 to `id: IR-002`.
  2. Change line 30 to `# IR-002 — Final Production Implementation Roadmap & Full-Stack Developer Execution Guide`.
  3. Change line 91 to `7. THIS ROADMAP IR-002 — sequence and task breakdown only`.
  4. Explicitly state in the header and revision history that **IR-002 v2.0 supersedes and replaces IR-001 v1.0–v1.2 in its entirety**.
  5. Update lines 299–301, 3580, and the appendix self-references to cite `IR-002`.

---

### Finding ARC-02: Total Omission of C4 Model Layer Specifications & Diagrams
- **Exact Line Numbers:** Document-wide (0 occurrences of "C4", "C4 model", or container/component diagrams).
- **Direct Observation:** The project's principal architectural skill (`erp-architect`) explicitly mandates:
  > *"1. The C4 Model (Context, Containers, Components, Code): Always structure your architectural designs using this model. Use mermaid diagrams for all visual blueprints... Never skip the C4 diagram. Visualizing the architecture is mandatory."*
  Furthermore, `AR-001_Software_Architecture_Document.md` conforms to C4 Model Levels 1–3 (§5 System Context, §6.1 Containers, §6.4 Components). However, `IR-002` contains zero C4 diagrams and zero mentions of C4 layers.
- **Technical Impact:** Full-stack developers executing this 156.5-week roadmap lack a coherent visual representation of how Odoo 19 CE, Next.js 16.3, PostgreSQL 17 (split residency), Kong Gateway, Keycloak, Apache Kafka, Apache Airflow, and Ceph S3 interact across trust boundaries.
- **Surgical Remediation Recommendation:**
  1. Add a dedicated **§0.3.4 The C4 Model Architectural Blueprints** section in Part 0.
  2. Insert **C4 Level 1 (System Context)** Mermaid diagram illustrating the 1000FiX ERP boundary, external parties (Customers, 51 Branches, 17+ Brands, NBR VAT, BEFTN, Couriers), and the core platform.
  3. Insert **C4 Level 2 (Container Diagram)** Mermaid diagram showing:
     - Experience Layer (7 Next.js portals on Port 3000, 4 Flutter mobile apps, Odoo Web OWL 2 on Port 8069).
     - API & Security Layer (Kong API Gateway on Port 8000, Keycloak 26 on Port 8080).
     - Core Business & Domain Services (Odoo 19 CE container, Python/FastAPI microservices).
     - Storage & Messaging Layer (PostgreSQL 17 regional primary on Port 5432, PostgreSQL 17 resident store on Port 5433, Ceph S3 RGW on Port 7480, Redis 7 on Port 6379, Apache Kafka on Port 9092, Apache Airflow on Port 8088).
  4. Insert **C4 Level 3 (Component Diagram)** focusing on the Odoo Core / Shared Kernel (`cd_event_outbox`, `cd_party_master`, `cd_rbac_ext`, `cd_entity_config`).
  5. Add an explicit verification check in Phase 2 (`P02-M03-T01`) and Phase 3 (`P03-M01-T01`) confirming that all custom code placement conforms strictly to C4 Level 2 and Level 3 containers.

---

### Finding ARC-03: Missing ADR Cross-References in Milestone & Task Execution Tables
- **Exact Line Numbers:** Task tables across Phases 1 to 12. Only ADR-022 (lines 1486, 1620, 1705, 2326), ADR-023 (lines 3843, 3908), ADR-024 (lines 1073, 1838, 1913, 2194, 2603), and ADR-027 (line 756) are explicitly cited.
- **Direct Observation:** In `AR-004_Architecture_Decision_Record_Library.md`, 30 formal architectural decisions (`ADR-001` through `ADR-030`) govern the system. However, in `IR-002`, the remaining 26 ADRs are not cited in the `Reads` or `Verify` columns of the execution tasks that implement them.
  - `ADR-001` (Odoo 19 CE system of record) is missing from `P03-M01`.
  - `ADR-006` (Shared PostgreSQL with portal platform) is missing from `P02-M05`.
  - `ADR-007` (TimescaleDB for time series) is missing from `P05-M04-T01`.
  - `ADR-008` (Decimal money, never float) is missing from `P06-M01-T04`.
  - `ADR-009` (ClickHouse for OLAP warehouse) is missing from `P11-M01-T01`.
  - `ADR-012` (Kong as API gateway) is missing from `P03-M03-T01`.
  - `ADR-013` (Redis Streams to Kafka migration) is missing from `P03-M03-T03` and `P09-M01`.
  - `ADR-014` (Mandatory Idempotency-Key on APIs) is missing from `P03-M03-T04`.
  - `ADR-016` (Transactional outbox on every write path) is missing from `P03-M03-T02`.
  - `ADR-018` (Split-residency data architecture) is missing from `P03-M09-T01`.
  - `ADR-020` (Keycloak as identity provider) is missing from `P03-M02-T01`.
  - `ADR-026` (Flutter as single mobile framework) is missing from `P02-M02-T03`.
  - `ADR-028` (Next.js + Payload CMS portal platform constraint) is missing from `P05-M07-T01`.
  - `ADR-029` (Self-hosted LLM inference via Ollama) is missing from `P09-M06-T03`.
- **Technical Impact:** Weakens architectural governance. Developers implementing these tasks lack immediate links to the design rationale, rejected alternatives, and fitness functions defined in `AR-004`.
- **Surgical Remediation Recommendation:**
  Update the `Reads` column of the task tables across Phases 1–12 to include the explicit `ADR-nnn` tags:
  - `P02-M05-T02`: Add `ADR-006`, `D-028`.
  - `P03-M01-T01`: Add `ADR-001`, `ADR-004`.
  - `P03-M02-T01`: Add `ADR-020`.
  - `P03-M03-T01`: Add `ADR-012`.
  - `P03-M03-T02`: Add `ADR-016`.
  - `P03-M03-T03`: Add `ADR-013`.
  - `P03-M03-T04`: Add `ADR-014`.
  - `P03-M09-T01`: Add `ADR-018`.
  - `P05-M04-T01`: Add `ADR-007`.
  - `P05-M07-T01`: Add `ADR-028`.
  - `P06-M01-T04`: Add `ADR-008`.
  - `P07-M02-T06`: Add `ADR-025`.
  - `P09-M01-T01`: Add `ADR-013`.
  - `P09-M06-T03`: Add `ADR-029`.
  - `P11-M01-T01`: Add `ADR-009`.

---

### Finding ARC-04: False Claim of Ceph Archival and AIStor Commercialization (MinIO Residue)
- **Exact Line Numbers:** Lines 371 (`B-19`), 456–480 (`D-028`), 478, 505, 1102, 3648, 4151–4160 (`IRB-01`), 4321–4322.
- **Direct Observation:** In `D-028` (lines 458–461) and `IRB-01` (line 4156), the text asserts:
  > *"`ceph/ceph` was archived on 25 April 2026. Its README reads 'THIS REPOSITORY IS NO LONGER MAINTAINED.' The community edition is source-only with no pre-compiled binaries; the administrative web console was removed... vendor directs users to AIStor Free (standalone only) or AIStor Enterprise (distributed, commercial)."*
  In line 478, it warns: *"Pinning Ceph Object Storage now guarantees that local diverges from prod on the first day of the programme."*
  In line 473 and 4159, the candidate table lists *"Ceph RADOS Gateway"* as an alternative to Ceph!
  In line 3648, the service port table specifies: `| Ceph Object Storage console | http://127.0.0.1:9001 | Object storage |`.
- **Root Cause Analysis:** In `IR-001`, the legacy stack used **MinIO**. MinIO relicensed under AGPL-3, archived their community repository, removed the web console, and launched proprietary AIStor. To address this, the project decided to replace MinIO with **Ceph RADOS Gateway (RGW) / Ceph S3**. However, `update_roadmap.py` executed:
  `content = content.replace('MinIO', 'Ceph Object Storage')`
  `content = content.replace('minio/minio', 'ceph/ceph')`
  This mechanical replace mistakenly attributed MinIO's archival, AIStor commercialization, and port 9001 to Ceph itself!
- **Technical Impact:** Critical misinformation. Ceph is NOT archived; it is the industry-standard distributed object and block store backed by the Linux Foundation. Port 9001 does not apply to Ceph RGW. Furthermore, there is no task anywhere in Phase 3 or later to deploy Ceph in production.
- **Surgical Remediation Recommendation:**
  1. Revise `D-028` (lines 456–480): State accurately that **MinIO (`minio/minio`) was archived on 25 April 2026 and commercialized under AIStor**, forcing the decommissioning of MinIO. Record the decision that **Ceph RADOS Gateway (RGW) S3 is the selected production object store**, providing multi-node erasure coding (20 TB -> 50 TB) under LGPL-2.1/3.0.
  2. In `B-19` (line 371): Reframe as `(RESOLVED) MinIO archival and commercialization resolved by adopting Ceph Object Storage (RGW S3) under D-028`.
  3. In line 1102 (`P02-M05-T02`): Remove the text *"Do not pin Ceph Object Storage: minio/minio was archived..."* and pin the local Ceph RGW S3 container (e.g. `ceph/daemon:latest-quincy` or a pinned digest of Ceph Nano / RGW).
  4. In line 3648 (Appendix B.4): Correct the local URL and port. Ceph RGW S3 API listens on `http://127.0.0.1:7480` (or `8000`); Ceph Dashboard UI listens on `http://127.0.0.1:8443` (HTTPS) or `8080`. Remove port 9001.
  5. Add an explicit task in Phase 3 (`P03-M09-T02`): **"Deploy Ceph RADOS Gateway (RGW) HA cluster with erasure coding for binary document storage (Z2/Z4)"**.
  6. In Appendix I (`IRB-01`, lines 4151–4160) and Appendix I citations (lines 4321–4322): Clarify the MinIO historical context and correct the reference links.

---

### Finding ARC-05: Inaccurate Classification of Apache-2.0 and LGPL as "Restricted Licences"
- **Exact Line Numbers:** Lines 374 (`B-22`), 497–515 (`D-030`), 4207 (`IRB-06`), 4323–4325.
- **Direct Observation:** Line 374 states:
  > *"`B-22` (RESOLVED) Four L4 components carry restricted licences and none has the architecture approval TSS §18.5 requires — Ceph Object Storage (LGPL), Apache Superset (Apache-2.0, embedded), Apache Airflow (Apache-2.0), Apache Kafka (Apache-2.0). `D-030` required."*
  In `D-030` table (lines 503–509):
  - Ceph Object Storage is listed as `AGPL-3`.
  - Apache Superset is listed as `AGPL-3` with a warning about AGPL's network-use clause!
  - Apache Airflow is listed as `Sustainable Use License (fair-code)`!
  - Apache Kafka is listed as `BSL`!
  In lines 4323–4325, citations show bizarre corrupted URLs:
  `[Apache Airflow Sustainable Use License](https://docs.Apache Airflow.io/susta)`
  `[Apache Superset licence](https://www.metabase.com/license)`
  `[Apache Kafka BSL licence text](https://github.com/redpanda-data/redpanda/blob/dev/licenses/bsl.md)`.
- **Root Cause Analysis:** In `IR-001`, the four components were MinIO (AGPL-3), Metabase (AGPL-3), n8n (fair-code SUL), and Redpanda (BSL). When replaced by Ceph, Superset, Airflow, and Kafka, `update_roadmap.py` swapped the names but left the old license names, risk texts, and URLs intact.
- **Technical & Legal Impact:** Complete contradiction. Neither LGPL nor Apache-2.0 are restricted, BSL, or fair-code licenses. Apache-2.0 has no copyleft or network-use trigger. Flagging Apache-2.0 as a compliance risk misleads legal and procurement teams.
- **Surgical Remediation Recommendation:**
  1. Rewrite `D-030` (lines 497–515): State that the legacy audit identified four restricted-licence components (MinIO AGPL-3, Metabase AGPL-3, n8n SUL, Redpanda BSL). **Under `D-030`, all four were replaced with approved, fully permissive/standard open-source alternatives**:
     - MinIO (AGPL-3) -> **Ceph Object Storage (LGPL-2.1/3.0)**
     - Metabase (AGPL-3) -> **Apache Superset (Apache-2.0)**
     - n8n (fair-code SUL) -> **Apache Airflow (Apache-2.0)**
     - Redpanda (BSL) -> **Apache Kafka (Apache-2.0)**
  2. Update the `D-030` table to show their actual licenses (all Apache-2.0 or LGPL), confirm zero license-breach risk for internal ERP or external partner portal usage, and mark `D-030` as permanently approved.
  3. Update `B-22` (line 374) to reflect the complete resolution of the restricted-licence blocker.
  4. In lines 4323–4325, replace corrupted links with official Apache Foundation and Ceph license documentation:
     - Apache Airflow: `https://www.apache.org/licenses/LICENSE-2.0`
     - Apache Superset: `https://superset.apache.org/docs/frequently-asked-questions#license`
     - Apache Kafka: `https://kafka.apache.org/`
     - Ceph: `https://ceph.io/en/`

---

### Finding ARC-06: Mathematical & Chronological Errors Regarding PostgreSQL 17 EOL
- **Exact Line Numbers:** Lines 373 (`B-21`), 481–496 (`D-029`), 2688 (`P09-M02-T01`), 4181–4190 (`IRB-04`).
- **Direct Observation:**
  - Line 2688 (`P09-M02-T01`) claims: *"Two upgrades land in the same window, not one. PostgreSQL 17 reaches EOL 8 November 2029 — on a Q4-2026 kickoff that is roughly month 25, inside this wave."*
  - Line 483 states: *"PostgreSQL 17 reaches end of life on 9 November 2028."*
  - Line 494 and Line 4189 list: *"baseline 17 and upgrade in W6 · baseline 17 (EOL 8 Nov 2029)"*.
- **Root Cause & Mathematical Analysis:**
  - Kickoff date: Q4-2026 (October 2026).
  - Wave 6 (Month 25): **November 2028**.
  - November 2028 was the EOL date of **PostgreSQL 16** (released 14 Sept 2023).
  - **PostgreSQL 17** was released on **26 September 2024** and reaches EOL on **8 November 2029** (five-year community lifecycle).
  - October 2026 + 36 months (full program duration) = **October 2029**.
  - Therefore, PostgreSQL 17 reaches EOL at **Month 37 (November 2029)**, which is **AFTER** the entire 36-month delivery programme is complete!
  - `update_roadmap.py` replaced `PostgreSQL 16` with `PostgreSQL 17`, erroneously keeping the "Month 25 / Wave 6 EOL" claim.
- **Technical Impact:** Falsely forces the team to plan and rehearse a hazardous database major-version upgrade in Wave 6 concurrent with the Odoo major upgrade.
- **Surgical Remediation Recommendation:**
  1. Revise `D-029` (lines 481–496): Document that adopting **PostgreSQL 17 as the Day-1 baseline** (released Sept 2024, EOL Nov 2029) **completely resolves the mid-programme EOL risk**. PostgreSQL 17 covers all 36 months of delivery through Go-Live.
  2. In `P09-M02-T01` (line 2688): Remove the assertion that PostgreSQL 17 reaches EOL in Month 25. Clarify that Wave 6 requires ONLY the Odoo major-version upgrade assessment, and that PostgreSQL 17 remains supported through Wave 9 completion.
  3. In `B-21` (line 373) and `IRB-04` (line 4186–4189): Clarify that PostgreSQL 17 EOL (November 2029) safely covers the delivery lifecycle, and any future upgrade to PostgreSQL 18/19 is deferred to post-handover operational maintenance.

---

### Finding ARC-07: Scrambled Next.js 16.3 Release Dates & EOL Assertions (Next 15 Residue)
- **Exact Line Numbers:** Lines 352 (`B-07`), 436–445, 4171–4180 (`IRB-03`), 4236.
- **Direct Observation:**
  - Line 352 still records: `B-07 | D-026 Next.js decision — 15 reaches EOL 21 Oct 2026, inside Wave 1`.
  - Line 436 claims: `| Next.js 16.3 provides long-term support | Released 21 Oct 2024; two-year Maintenance LTS |`.
  - Line 444 asserts: `The existing 1000fix-portal-platform on Next.js 16.3 + Payload 3 sits on a combination that is simultaneously reaching EOL and permanently excluded from CMS support.`
- **Root Cause Analysis:** Next.js 15 was released on 21 Oct 2024 and reaches EOL on 21 Oct 2026. Next.js 16 was released in October 2025. When `update_roadmap.py` executed `re.sub(r'Next\.js 15(?![.\d])', 'Next.js 16.3', content)`, it replaced Next.js 15 with Next.js 16.3 in the historical description of Next.js 15!
- **Technical Impact:** Renders the technical evaluation nonsensical by claiming Next.js 16.3 was released in 2024, is EOL, and is incompatible with Payload CMS.
- **Surgical Remediation Recommendation:**
  1. In `B-07` (line 352), mark as `(RESOLVED) D-026 Next.js 16.3 upgrade resolved: Next.js 16.3 with React 19 and Payload CMS 3.73+ adopted across all portals`.
  2. In Section 0.7.2 (lines 436–445): Clarify that the legacy platform ran on Next.js 15 (released Oct 2024, EOL Oct 2026). State that **Next.js 16.3 (released Oct 2025, patch line 16.3.x)** provides stable Turbopack bundling by default, React 19 support, Server Actions, and full compatibility with Payload CMS 3.73+.
  3. In line 444, restore the reference to the legacy portal platform being on Next.js 15, and the new build targeting Next.js 16.3.

---

### Finding ARC-08: Deprecated Node.js 20 LTS Specified After Official End-of-Life
- **Exact Line Numbers:** Lines 988 (`P02-M02-T02`), 1376, 3475.
- **Direct Observation:** Line 988 specifies:
  > `| P02-M02-T02 | Install nvm, then Node 20 LTS, then pnpm | BE-001 §4 · AGENTS.md inheritance | Node 20 + pnpm | nvm install reads .nvmrc. Pinned by .nvmrc and pnpm-lock.yaml | DE | — |`
  However, Node.js 20 reached official **End-of-Life on 30 April 2026**.
- **Technical & Security Impact:** Initiating an enterprise ERP and 12-portal digital platform in Q4-2026 on an EOL Node runtime violates baseline security standard `BE-007` (`DE-06`) and ISO 27001 requirements. Node 20 receives no vulnerability patches and may fail compatibility tests with modern Next.js 16.3 packages.
- **Surgical Remediation Recommendation:**
  1. Update `P02-M02-T02` (line 988) from Node 20 LTS to **Node.js 22 LTS (Active/Maintenance LTS until April 2027)**, pinned via `.nvmrc` and `.node-version`.
  2. Update `P02-M06-T01` (line 1118) and Appendix A (line 3475) to verify `node --version` against the Node 22 LTS line.

---

### Finding ARC-09: Omission of Root Monorepo Configuration Files (`turbo.json`, `pnpm-workspace.yaml`, `pyproject.toml`)
- **Exact Line Numbers:** Lines 1000–1075 (`P02-M03`), 1118 (`P02-M06-T01`), 1287 (`P02-M09-T08`).
- **Direct Observation:**
  - The repository root tree in `P02-M03` (lines 1020–1067) omits essential monorepo orchestration files: `package.json`, `pnpm-workspace.yaml`, `turbo.json`, `pyproject.toml`, and `Makefile`.
  - Across the entire 4,360-line roadmap, `turbo.json` and `Turborepo` are mentioned ZERO times.
  - In `P02-M06-T01`, task `make bootstrap` executes `pnpm install` and `uv sync`, but the root repository structure contains neither the `pnpm` workspace definitions nor the `uv` Python workspace definitions.
  - In `P02-M09-T08`, the roadmap mandates a 20-minute CI budget relying on "affected-component selection computed from the dependency graph and caching", which is precisely Turborepo's core function.
- **Technical Impact:** Without `turbo.json` and `pnpm-workspace.yaml`, the 7 Next.js applications and 3 shared TypeScript libraries (`libs/ts/*`) cannot be built, linted, or tested incrementally. CI execution time will scale linearly and exceed the 20-minute budget.
- **Surgical Remediation Recommendation:**
  1. In `P02-M03-T03` (the repository tree, lines 1020–1067), add to the root of `1000fix-erp/`:
     ```
     ├── package.json              ← root workspace dependencies & turbo scripts
     ├── pnpm-workspace.yaml       ← packages: apps/web/*, libs/ts/*
     ├── turbo.json                ← Turborepo v2 pipeline (build, test, lint, dev caching)
     ├── pyproject.toml            ← uv Python workspace: services/*, libs/py/*, addons/*
     ├── uv.lock                   ← pinned Python virtualenv lockfile
     ├── pnpm-lock.yaml            ← pinned Node/TS lockfile
     ├── Makefile                  ← developer workflow targets
     ```
  2. Add an explicit task `P02-M03-T04b`: **"Author `turbo.json` defining pipeline tasks: `build` (with cache inputs/outputs and `^build` dependency), `test`, `lint`, and `dev` (cache: false, persistent: true)"**.
  3. Author `pnpm-workspace.yaml` mapping `apps/web/*` and `libs/ts/*`.

---

### Finding ARC-10: Missing Terraform IaC, K3s Manifests, Helm Charts, and Container Limits
- **Exact Line Numbers:** Lines 163, 1063 (`infra/`), 1280–1289 (`P02-M09`), 3172 (`P11-M07-T01`).
- **Direct Observation:**
  - Line 1063 shows `├── infra/ ← compose/ k3s/ terraform/ odoo-conf/`.
  - Task `P02-M09-T09` instructs: *"Provision the twelve environments per PE-002 §4.2"*.
  - However, there are NO tasks in the entire roadmap that author, test, or apply Terraform IaC scripts (`infra/terraform/`) for provisioning cloud networks, VPCs, and droplet/VM nodes.
  - There are NO tasks to generate K3s Kubernetes manifests or Helm charts (`infra/k3s/`) for deploying Odoo web/cron workers, PgBouncer, Kong, Airflow, Superset, etc.
  - The `erp-devops` skill mandates: *"NEVER deploy a container without resources.limits and resources.requests"*. Yet `IR-002` never establishes or validates CPU/Memory limits and requests for any containerized workload.
- **Technical & SRE Impact:** High risk of untracked manual infrastructure configuration ("click-ops"). Without container CPU/Memory limits and requests, runaway memory leaks (e.g. Odoo report generation or OCR processing) will trigger OOM kills of host nodes.
- **Surgical Remediation Recommendation:**
  1. Add task `P02-M09-T01b`: **"Author declarative Terraform modules in `infra/terraform/` for VPC, private networking, managed subnets, bastion, and K3s node pools across Singapore and Dhaka data centres"**.
  2. Add task `P02-M09-T01c`: **"Author K3s Kubernetes manifests / Helm charts in `infra/k3s/` for Odoo Web, Odoo Cron, PgBouncer, Kong, and Keycloak, enforcing mandatory `resources.requests` and `resources.limits` on every container"**.
  3. Ensure all manifests include Kubernetes Liveness, Readiness, and Startup HTTP probes.

---

### Finding ARC-11: Total Absence of Chaos Engineering & Split-Brain Resilience Validation
- **Exact Line Numbers:** Whole document (0 mentions of Chaos Engineering; 0 mentions of split-brain prevention).
- **Direct Observation:** The `erp-devops` skill states:
  > *"2. Chaos Engineering: Assume systems will fail. Design Kafka clusters, Ceph storage, and PostgreSQL instances to survive network partitions and node deaths (Split-brain prevention)."*
  `IR-002` details DR drills, but contains no chaos engineering tasks, automated fault-injection framework, or validation of split-brain prevention across the Singapore-Dhaka WAN link.
- **Technical & SRE Impact:** During cross-region network partitions between Singapore (Z1/Z2) and Dhaka (Z4 resident store), unverified failover mechanisms could cause split-brain data divergence or silent data loss.
- **Surgical Remediation Recommendation:**
  1. Add task `P09-M01-T06b` in Phase 9 (or in Phase 6 `P06-M08`): **"Execute automated Chaos Engineering drills (using Chaos Mesh or container fault-injection scripts) simulating: (a) sudden termination of primary Kafka broker, (b) PostgreSQL streaming replication failover, (c) Ceph OSD crash, and (d) cross-border WAN network partition between regional primary and resident store, asserting zero split-brain and zero data loss"**.
  2. Require signed Chaos Engineering drill evidence as a mandatory exit condition for Gate `G6` and Gate `G8`.

---

### Finding ARC-12: Inaccurate Representation of Apache Airflow DAG Architecture
- **Exact Line Numbers:** Lines 1467 (`P03-M03-T09`), 2175–2176 (`P06-M08-T03/T04`), 2280 (`P07-M02-T06`).
- **Direct Observation:**
  - Line 1467 states: *"Apache Airflow is for configuration that changes when a counterparty changes a template, not for logic that needs a release"*.
  - Line 2280 asserts: *"Build the Apache Airflow brand-submission workflows — one per brand template... Why Apache Airflow and not custom code: the transformation is configuration that changes when a brand changes its template, not code that requires a release."*
- **Root Cause Analysis:** This text is a literal holdover from n8n (which used visual drag-and-drop JSON configuration). When `update_roadmap.py` replaced `n8n` with `Apache Airflow`, it left the description of low-code visual configuration intact.
- **Technical Impact:** Airflow workflows are NOT visual configuration files; they are executable Python code (DAGs). Describing them as "configuration not needing a release" leads to ad-hoc, unversioned, untested changes in production.
- **Surgical Remediation Recommendation:**
  1. Update lines 1467, 2176, and 2280: Re-frame Airflow workflows as **version-controlled Python DAGs** (`services/orchestration/dags/`).
  2. Specify the use of Airflow's modern `TaskFlow` API (`@dag`, `@task`) for declarative data transformations.
  3. Include a DAG validation test in CI `pre-merge` stage 5 (`pytest` DAG integrity and import check) so no broken DAG reaches production.

---

### Finding ARC-13: Portal Count Inconsistency (6 vs 7 vs 8 Next.js Applications)
- **Exact Line Numbers:** Lines 65, 108, 158, 665, 1049–1050, 3799–3811, 4175.
- **Direct Observation:**
  - Line 65 cites: *"the six Next.js portals"*.
  - Line 158 cites: *"8 Next.js apps · 3 Flutter apps"*.
  - Lines 1049–1050 list in `apps/web/`: `customer/ corporate/ analytics/ seller/ brand/ agent-console/ partner/` (7 folders, incorrectly including `analytics` which is Superset/Grafana, and omitting `vendor/` which is `P05`).
  - Appendix D (lines 3799–3811) enumerates 7 Next.js portals:
    - `P01`: Customer Self-Service (Next.js)
    - `P04`: Corporate B2B (Next.js)
    - `P05`: Vendor & Supplier (Odoo Portal + Next.js)
    - `P07`: Marketplace Seller (Next.js + App)
    - `P08`: Brand Partner (Next.js)
    - `P10`: Contact Centre Agent Console (Next.js)
    - `P12`: Partner & Referral (Next.js)
    Along with 4 Flutter apps (`P02` Technician, `P09` Rider, `P11` Auditor, `APP-04` Customer Mobile).
- **Technical Impact:** Discrepancy in directory layout and frontend team capacity planning.
- **Surgical Remediation Recommendation:**
  1. Harmonize the counts across the entire roadmap: **7 Next.js web applications** and **4 Flutter mobile applications**.
  2. Correct the monorepo directory layout in `apps/web/` to:
     ```
     ├── apps/
     │   ├── mobile/            ← technician/ (P02)  rider/ (P09)  auditor/ (P11)  customer/ (APP-04)
     │   └── web/               ← customer/ (P01)  corporate/ (P04)  vendor/ (P05)
     │                             seller/ (P07)    brand/ (P08)      agent-console/ (P10)  partner/ (P12)
     ```
  3. Explicitly note that `P06` (Analytics & Executive Dashboard) is delivered by embedded Apache Superset + Grafana (`R5`), not as a custom Next.js application in `apps/web/`.

---

## Verification & Execution Protocol

To independently verify these findings:
1. Run regex scans against `roadmap/IR-002_Final_Production_Implementation_Roadmap.md` using the exact line numbers provided.
2. Cross-reference `primary-doc/1000FiX_ERP_Technology_Stack_Specification.md`, `project-guide-doc/02_Architecture_and_Design/AR-001_Software_Architecture_Document.md`, and `AR-004_Architecture_Decision_Record_Library.md`.
3. Check `roadmap/update_roadmap.py` lines 43–66 to observe the mechanical string substitutions that generated the corrupted narratives.
4. Verify official upstream EOL schedules:
   - Node.js 20 EOL: 2026-04-30
   - PostgreSQL 17 EOL: 2029-11-08
   - Next.js 16.3: Released October 2025

All 13 findings are substantiated by primary evidence and ready for surgical implementation.
