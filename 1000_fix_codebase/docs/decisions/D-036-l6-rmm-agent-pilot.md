# D-036 — L6 Commercial Component: Remote Monitoring & Management (RMM) Agent Pilot Review

| | |
|---|---|
| **Decision ID** | `D-036` |
| **Date** | 2026-10-18 (Milestone R06-M04-T05) |
| **Status** | ACCEPTED (PILOT APPROVED) |
| **Deciders** | Chief Technology Officer (CTO), Head of Managed Services (MSP Lead), Principal SRE, Lead Security Architect |
| **Allocating authority** (`DL-08`) | TSS §9 L6 Rule · `D-030` Restricted License Policy · `IR-002` P08-M07-T08 · `GV-003` Change Control |
| **Target Components** | `TC-064` RMM Agent & Collector · `cd_msp_contract` (M05) · MeshCentral / RustDesk / Wazuh / osquery Stacks |
| **Regulatory Baseline** | Bangladesh Cyber Security Act 2023 · Bangladesh PDPA Split-Residency (§0.7.3) · D-030 Copyleft Governance |

---

## 1. Context & Operational Need

1000FiX Services Ltd. operates corporate Managed Service Provider (MSP) contracts covering over 250 corporate client facilities, retail banks, and ATM kiosks nationwide. Operational requirements under M05 demand:
1. Real-time fleet health telemetry (CPU, memory, disk, network interface status, service heartbeats).
2. Autonomous alerting with automatic ticket creation in Odoo upon threshold breaches or silent agents.
3. Secure, audited remote control sessions to assist client workstations without physical dispatch.
4. PDPA-compliant explicit end-user consent before remote desktop capture or file transfer occurs.

Under `D-030` (Restricted Licence Register), client-installed endpoint software must undergo strict licensing scrutiny to ensure zero contamination of proprietary or client internal networks by copyleft network distribution obligations (e.g., AGPL-3 network trigger duties).

---

## 2. Written Open-Source Software (OSS) Alternative Review

A formal OSS evaluation was conducted across endpoint agent candidates:

| Candidate | Architecture & Transport | Licensing Assessment (D-030) | Operational Suitability | Recommendation |
|---|---|---|---|---|
| **MeshCentral** | Node.js central server; lightweight C/C++ cross-platform mesh agent (WebSockets, TLS 1.3) | **Apache-2.0** (Permissive) — Full compliance with D-030; zero copyleft risk to client environments | Mature WebRTC remote desktop, terminal, and file transfer; supports local self-hosted deployment behind NGINX reverse proxy | **Approved for Remote Support Engine** |
| **RustDesk (Self-Hosted)** | Rust-based relay & rendezvous server with desktop client | **GPL-3.0** on client; AGPL concerns on specific network server components | High performance; requires careful license boundary isolation to prevent enterprise linking concerns | **Approved as Secondary On-Demand Assist** |
| **Wazuh Agent + osquery** | C/Go endpoint daemon with SQL-like system inspection | **GPLv2 / Apache-2.0** | Industry standard endpoint detection, file integrity monitoring, and vulnerability telemetry | **Approved for Security & Inventory Ingestion** |
| **Proprietary SaaS RMM** (e.g. NinjaOne, Datto) | Proprietary closed-source agent and cloud SaaS | Proprietary subscription; foreign cloud hosting violates local telemetry residency constraints | Violates Bangladesh PDPA financial sector data residency guidelines for banking clients | **Rejected** |

---

## 3. Decision

1. **Approve Open-Source Stack for M05 MSP Platform**:
   - Deploy **MeshCentral** (Apache-2.0) and **Wazuh/osquery** (Apache-2.0 / GPLv2 isolated process boundary) as the primary managed service stack.
   - Maintain the `services/rmm-collector` microservice as an isolated, pure stdlib boundary layer that normalizes telemetry and feeds Odoo via authenticated JSON-RPC.

2. **PDPA Consent & Session Governance (Enforced in `cd_msp_contract`)**:
   - Remote screen control is forbidden without affirmative end-user authorization.
   - Model `fix.msp.remote.session` enforces explicit `consent_obtained=True` before transitioning session state to `active`.
   - All session recordings, duration logs, and operator identities are logged with immutable audit timestamps.

3. **Bilingual SLA & Service Reporting**:
   - Model `fix.msp.monthly.report` generates bilingual monthly MSP performance summaries in English and Bengali (`summary_en` and `summary_bn`) for corporate governance boards.

---

## 4. Consequences & Governance Audit

- **Copyleft Isolation**: The endpoint agent binaries are distributed as unmodified standalone service daemons under Apache-2.0, adhering strictly to `D-030`.
- **Telemetry Residency**: Telemetry collector endpoints terminate strictly within local Bangladesh private cloud infrastructure (`http://127.0.0.1:8069` internal loopback), guaranteeing compliance with financial sector data isolation mandates.
- **Review Schedule**: Evaluated annually during the ISO 9001 quality management system surveillance audit.
