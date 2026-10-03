---
id: FIX-ERP2-M05
module_id: M05
module_code: RMS
module_name: Remote Support & Managed Services
category: A — Service Delivery & Operations
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Corporate Services Head
system_owner: Platform Squad
priority: P1
wave: W5
---

# M05 — Remote Support & Managed Services
### Category A · Code `RMS` · New in v2.0, retained in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M05 |
| **Module code** | `RMS` |
| **Category** | A — Service Delivery & Operations |
| **Status** | Existing (introduced in v2.0, retained in v2.1) |
| **Priority** | **P1** |
| **Delivery wave** | W5 (Months 19–22) |
| **Business owner** | Corporate Services Head |
| **System owner** | Platform Squad |
| **Delivery layers** | L4 (monitoring, remote access) + L5 (custom) + conditional L6 (commercial RMM agent) |
| **Custom modules** | `cd_msp_contract`, `cd_monitoring`, `cd_alerting`, `cd_msp_ticket`, `cd_remote_session`, `cd_patch_mgmt` |
| **Requirement range** | FR-RMS-001 … FR-RMS-062 |
| **Requirement count** | **62** *(measured 2026-08-13 — supersedes the 61 recorded in `05-01` §1.3, which understated the range endpoint)* |
| **Effort estimate** | 37 person-weeks |
| **Depends on** | M08 Contract · M17 Asset Registry · M33 Party Master · M27 Contact Centre · M29 Identity · M02 Field Service |
| **Depended on by** | M01, M02, M08, M20, M25, M39, M53, M66 |

---

## 2. Purpose

M05 turns 1000FiX from a company that **fixes things when they break** into a company that
**stops them breaking** — under contract, for a monthly fee, at gross margins above 55%.

The Company's business plan commits to **six categories of managed service contract** and a
**24/7 technical support** operation covering remote, software, hardware, networking, mobile
and email support. Both are described in detail. Neither has a system.

M05 is that system: remote assistance sessions, proactive monitoring of client IT estates,
alerting and incident correlation, patch and update management, backup oversight, a contracted
service desk, and the SLA reporting that makes the contract defensible.

### Why It Exists

This is the highest-margin business line described anywhere in 1000FiX's documentation and
the only one that generates **recurring revenue with declining marginal cost**. A repair job
earns once. A managed-service contract earns every month, and the better the monitoring, the
fewer site visits are needed to service it.

It is also the line most exposed by not having a system. An MSP contract sold without
monitoring is a promise to react quickly to problems the Company will not know about until
the client phones. SLA credits accrue silently. The segment stays sub-scale because every
new client adds manual load rather than automated load.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Business Plan §Managed Service Contracts | Six contract types: Basic, Comprehensive, Security-focused, Cloud Services, Disaster Recovery & Business Continuity, IT Strategy Consulting |
| Business Plan §Managed Service features | Proactive monitoring, regular maintenance, software updates, troubleshooting and issue resolution, strategy and consulting, helpdesk and support |
| Business Plan §24/7 Technical Support | Round-the-clock support, escalation procedures, remote assistance via secure remote access tools, knowledge base and self-service, quality monitoring of support |
| Business Plan §24/7 support types | Remote technical support, software support, hardware support, networking support, mobile device support, email and account support |
| Business Plan §IT Infrastructure AMC | Servers, networking, storage, backup and recovery systems under contract |
| Service App SOW §Remote service feature | "It's like the TeamViewer app. Here, say, a customer can provide us access to his computer remotely through a desktop app" |
| Business Plan §Data Backup Solutions | Backup services requiring monitoring and restore verification — delivered jointly with M06 |
| Portal roadmap IMPL-46 | Corporate SSO and ERP API framework for enterprise clients |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Remote assistance sessions: attended, unattended, consent, recording, billing |
| 2 | Monitored estate: asset onboarding, agent deployment, agentless monitoring |
| 3 | Metric collection, storage and health scoring |
| 4 | Alert rules, correlation, de-duplication and alert-to-ticket automation |
| 5 | On-call rota, escalation policy and acknowledgement tracking |
| 6 | Runbook definition and automated remediation |
| 7 | Maintenance windows and alert suppression |
| 8 | Patch inventory, scheduling, deployment and compliance reporting |
| 9 | Endpoint protection and vulnerability posture oversight |
| 10 | Managed service desk: client ticketing, classification, contractual SLA |
| 11 | Problem and change management for client environments |
| 12 | Escalation from remote to field intervention |
| 13 | Entitlement consumption, overage detection and SLA credit calculation |
| 14 | Client service reports and service review meetings |
| 15 | Client onboarding and offboarding projects |
| 16 | Cloud subscription and licence oversight |
| 17 | Backup service oversight and restore-test tracking |
| 18 | Disaster recovery and business continuity plan register and test tracking |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Contract terms, entitlement definition, renewal | **M08** | The contract is a commercial object; M05 delivers against it |
| Recurring billing and invoicing | **M39** / **M20** | Only Category C and G handle money |
| SLA credit posting to the customer account | **M20** | M05 calculates; M20 credits |
| Asset identity and ownership | **M17** | One asset registry for all populations |
| Field visit dispatch and execution | **M02** | M05 escalates to field; it does not dispatch |
| Data recovery, backup execution, secure destruction | **M06** | Data handling has its own confidentiality regime |
| **1000FiX's own internal IT support** | **M66** | Client-facing MSP and internal IT are different businesses with different SLAs and audiences |
| Contact centre channels, telephony, agent workspace | **M27** | M05 raises client tickets; M27 owns the conversation infrastructure |
| Customer identity and corporate hierarchy | **M33** | One party master |
| Telemetry ingestion for non-MSP assets | **M48** | M48 owns the general IoT/telemetry platform; M05 owns the MSP-specific overlay |
| Security incident investigation for 1000FiX itself | **M29** / **M60** | Internal security is not a client service |

### 3.3 Shared Concepts

| Concept | M05's Role | Owning Module |
|---|---|---|
| MSP contract instance | Owns the delivery instance | M08 owns the contract |
| Monitored asset | Owns the monitoring overlay | M17 owns the asset |
| Telemetry | Owns MSP-specific collection and alerting | M48 owns the platform |
| Ticket | Owns the MSP ticket | M27 owns the conversation |
| Entitlement consumption | Reports consumption | M08 owns the balance |
| SLA credit | Calculates | M20 applies |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **RMM platforms (NinjaOne, Datto RMM, N-able, Atera, ConnectWise Automate)** | Real-time device health monitoring, software inventory, patch compliance, security posture, configurable alert thresholds per client | Per-client alert thresholds; software and patch inventory; health scoring | Per-endpoint commercial licensing at 5,000+ assets — economically unviable |
| **PSA platforms (ConnectWise Manage, Autotask, Syncro)** | Tickets, time tracking, SLAs, contracts, client communication, invoicing | Ticket + SLA + entitlement consumption model as the PSA layer, built inside the ERP | Separate PSA product — it would duplicate contract, billing and customer master |
| **ITIL 4 / ITSM practice** | Incident vs service request distinction; escalation and notification procedures; problem and change management; post-incident review | Incident/request separation; formal problem records for recurring incidents; change records with rollback plans | Full ITIL practice architecture — disproportionate for the client base |
| **Wazuh / osquery (open source)** | Endpoint telemetry, security posture, file integrity, vulnerability detection | The monitoring agent layer at zero licence cost | Their SIEM depth — not required for this service tier |
| **MeshCentral / RustDesk (open source)** | Attended and unattended remote desktop with session recording | Remote session capability without per-technician licensing | Commercial remote-support licensing |
| **SLA management practice** | Automated SLA monitoring with breach notification; proactive escalation before breach | Multi-threshold escalation; service credit automation | — |

**Design position.** Four deliberate differences.

First, **build the PSA layer inside the ERP, buy only the agent**. A commercial PSA would
duplicate the contract, customer, billing and ticketing objects that already exist in
Categories B, C and G. The RMM *agent* — the thing that runs on a client's Windows machine
and applies patches at scale — is the one component where a commercial product may be
justified, and that decision is deliberately deferred to a Wave 5 pilot (decision D-07).

Second, **monitoring exists to avoid site visits, not to generate them**. The design KPI is
**remote resolution rate above 65%**. Every alert rule is judged by whether it produces an
action that avoids a truck roll.

Third, **the client sees what we see**. The corporate portal (P04) exposes estate health,
open incidents, SLA attainment and patch compliance to the client directly. This is a
commercial choice: transparency is what allows the Company to charge a premium and to defend
a renewal.

Fourth, **24/7 is a staffing model, not a slogan**. The business plan promises round-the-clock
support. M05 makes that measurable through the on-call rota, out-of-hours routing, and SLA
clocks that respect the contracted coverage window rather than office hours.

---

## 5. Functional Areas & Features

### 5.1 Remote Assistance

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RMS-001 | Session initiation | Start a remote support session from a ticket, issuing a one-time code to the customer | P1 | L4 |
| FR-RMS-002 | Consent and authorisation | Require explicit, logged customer consent before any remote connection, displaying what will be accessed | **P0** | L5 |
| FR-RMS-003 | Attended and unattended access | Support attended sessions and, for contracted assets only, unattended access under the contract's terms | P1 | L4 |
| FR-RMS-004 | Session recording | Record sessions where policy or contract requires; store as evidence with retention rules in M24 | P1 | L4 |
| FR-RMS-005 | Session metering and billing | Meter session duration and bill by contract entitlement or on demand | P1 | L5 |
| FR-RMS-006 | File transfer control | Permit, log and malware-scan file transfers during a session | P1 | L5 |
| FR-RMS-007 | Session handover | Transfer a live session between engineers with full context | P2 | L4 |
| FR-RMS-062 | Session from the contact centre | Launch a session directly from within an active customer conversation | P1 | L5 |

### 5.2 Monitored Estate

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RMS-008 | Asset onboarding | Register a client's monitored assets — endpoints, servers, network devices, printers, cloud subscriptions — linked to the M17 registry | P1 | L5 |
| FR-RMS-009 | Agent deployment | Deploy, register and health-check a monitoring agent per asset | P1 | L4 |
| FR-RMS-010 | Agentless monitoring | Monitor network devices via SNMP and ICMP where an agent cannot be installed | P1 | L4 |
| FR-RMS-011 | Metric collection | Collect CPU, memory, disk, temperature, uptime, service state, backup state and security state, storing as time series | P1 | L4 |
| FR-RMS-012 | Software inventory | Maintain installed-software and licence inventory per asset | P2 | L4 |
| FR-RMS-013 | Configuration baseline | Record a configuration baseline per asset class and detect drift | P2 | L5 |
| FR-RMS-014 | Health score | Compute a health index per asset and per client estate | P2 | L5 |
| FR-RMS-051 | Asset discovery | Discover assets on the client network and reconcile against the registered estate | P2 | L4 |
| FR-RMS-053 | Client asset warranty tracking | Track manufacturer warranty across the client estate and alert before expiry | P2 | L5 |
| FR-RMS-056 | Agent health | Monitor and remediate agent health and coverage gaps — an unmonitored asset is a contractual failure | P1 | L5 |

### 5.3 Alerting & Incident Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RMS-015 | Alert rules | Define thresholds and conditions per asset class, client and contract tier | P1 | L5 |
| FR-RMS-016 | Alert-to-ticket | Raise a service ticket automatically from an alert, with de-duplication and correlation | P1 | L5 |
| FR-RMS-017 | Escalation policy | Escalate unacknowledged alerts through an on-call rota with acknowledgement tracking | P1 | L5 |
| FR-RMS-018 | Runbook automation | Attach and execute remediation runbooks, recording what was attempted and the outcome | P2 | L5 |
| FR-RMS-019 | Maintenance windows | Suppress alerting during agreed maintenance windows | P1 | L5 |
| FR-RMS-020 | Major incident handling | Declare a major incident, notify all affected client contacts, and run a structured resolution and post-incident review | P2 | L5 |
| FR-RMS-057 | Alert noise reduction | Tune, suppress and correlate alerts to keep the signal-to-noise ratio usable | P1 | L5 |
| FR-RMS-054 | Automation library | Maintain reusable automation scripts with approval and execution audit | P2 | L5 |
| FR-RMS-055 | Scheduled tasks | Run scheduled maintenance tasks on client assets with evidence of completion | P2 | L4 |

### 5.4 Patch, Update & Security Oversight

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RMS-021 | Patch inventory | Track available and missing patches per asset | P2 | L4/L6 |
| FR-RMS-022 | Patch scheduling | Schedule deployment by ring, maintenance window and client approval, with rollback | P2 | L4/L6 |
| FR-RMS-023 | Patch compliance reporting | Report compliance per client, asset class and criticality | P2 | L5 |
| FR-RMS-024 | Endpoint protection oversight | Monitor endpoint protection status and raise alerts on coverage gaps | P2 | L4 |
| FR-RMS-025 | Vulnerability reporting | Report known vulnerabilities on the monitored estate to the client | P3 | L4 |
| FR-RMS-044 | Security posture reporting | Report client endpoint protection, patch and vulnerability posture as a periodic deliverable | P2 | L5 |

### 5.5 Managed Service Desk

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RMS-026 | Client ticketing | Accept tickets from client contacts by portal, email, phone or chat, scoped to their entitlement | P1 | L2 |
| FR-RMS-027 | Ticket classification | Classify by service, urgency and impact, deriving priority | P1 | L2 |
| FR-RMS-028 | Contractual SLA | Apply response and resolution SLAs from the client's contract; measure and report breach | P1 | L5 |
| FR-RMS-029 | Knowledge base | Maintain solution articles and publish selected articles to client self-service | P2 | L5 |
| FR-RMS-030 | Problem management | Link recurring incidents to a problem record with root-cause and permanent-fix tracking | P2 | L5 |
| FR-RMS-031 | Change management | Record and approve changes to client environments with rollback plans | P2 | L5 |
| FR-RMS-032 | Field escalation | Escalate a remote ticket into an on-site visit through M02, carrying full context | P1 | L5 |
| FR-RMS-049 | Client contact management | Maintain authorised contacts, their permissions and escalation preferences | P1 | L5 |
| FR-RMS-050 | Client portal scope | Define exactly what each client may see and do in P04 | P1 | L5 |
| FR-RMS-058 | Client satisfaction | Measure satisfaction per ticket and per period for MSP clients | P1 | L5 |

### 5.6 Contract Delivery, Reporting & Lifecycle

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RMS-033 | Entitlement consumption | Track consumption against contracted hours, incidents, assets or seats | P1 | L5 |
| FR-RMS-034 | Overage handling | Detect overage and either bill it or request an uplift | P1 | L5 |
| FR-RMS-035 | Service reports | Generate periodic client service reports: SLA attainment, incidents, patch compliance, health, recommendations | P1 | L5 |
| FR-RMS-036 | Service review meetings | Schedule, record and track actions from client service review meetings | P2 | L5 |
| FR-RMS-037 | SLA credits | Calculate service credits automatically on breach and pass them to M20 | P1 | L5 |
| FR-RMS-038 | 24/7 coverage model | Define follow-the-clock coverage, on-call rotas and out-of-hours cost recovery | P1 | L5 |
| FR-RMS-047 | Client onboarding project | Run a structured onboarding project for each new MSP client | P1 | L5 |
| FR-RMS-048 | Client offboarding | Run controlled offboarding: agent removal, data return, access revocation, final reporting | P1 | L5 |
| FR-RMS-059 | Profitability per client | Report cost to serve against contract value per client | P2 | L5 |
| FR-RMS-060 | Capacity planning | Forecast MSP team capacity against contracted estate growth | P2 | L5 |
| FR-RMS-061 | MSP analytics | Report the full operational and commercial picture of the MSP business | P1 | L5 |

### 5.7 Specialist Service Lines

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RMS-039 | Backup service oversight | Monitor client backup job outcomes, report failures and drive remediation | P2 | L5 |
| FR-RMS-040 | Cloud subscription management | Track client cloud subscriptions, licences, usage and renewal | P2 | L4 |
| FR-RMS-041 | Cloud cost reporting | Report client cloud spend with optimisation recommendations | P3 | L5 |
| FR-RMS-042 | DR/BC plan register | Maintain client disaster-recovery and continuity plans | P2 | L5 |
| FR-RMS-043 | DR test tracking | Schedule, execute and evidence DR tests with results reporting | P2 | L5 |
| FR-RMS-045 | IT strategy deliverables | Track consulting deliverables, roadmaps and recommendations per client | P3 | L5 |
| FR-RMS-046 | Technology roadmap | Maintain a per-client technology roadmap with refresh recommendations feeding sales | P3 | L5 |
| FR-RMS-052 | Licence compliance | Report software licence compliance across the client estate | P3 | L4 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Multi-tenant isolation** | One client's telemetry, tickets and credentials are unreachable from another client's context, enforced at the query layer |
| T-02 | **Time-series storage** | Metrics land in a hypertable with compression after seven days and a defined retention policy per contract tier |
| T-03 | **Ingestion scale** | Sustained ingestion of 50,000 metric points per minute across 5,000 monitored assets |
| T-04 | **Alert evaluation** | Streaming evaluation against rules with de-duplication windows and correlation keys, not batch polling |
| T-05 | **Agent security** | Agents authenticate with per-asset credentials, communicate over TLS, and can be revoked centrally |
| T-06 | **Remote session security** | Sessions are consent-gated, time-limited, logged, optionally recorded, and terminate automatically on inactivity |
| T-07 | **Credential vaulting** | Client environment credentials are vaulted, never stored in tickets or notes, and access is audited |
| T-08 | **Runbook execution audit** | Every automated remediation records the script version, target, output and outcome |
| T-09 | **SLA clock accuracy** | Clocks honour the contracted coverage window, client holidays and agreed maintenance windows |
| T-10 | **Idempotent alert-to-ticket** | A flapping alert produces one ticket, not fifty |
| T-11 | **Client portal scoping** | Portal queries are scoped by contract at the API layer; no client-side filtering |
| T-12 | **Graceful degradation** | Loss of the monitoring platform degrades to reactive support with client notification, not silence |
| T-13 | **Performance** | Alert to ticket ≤ 10 s; estate dashboard ≤ 3 s for 500 assets; remote session establishment ≤ 15 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M05 |
|---|---|---|
| **Corporate Services Head** | Sells MSP contracts the Company cannot systematically deliver | Sells a service with visible estate health, measured SLA and a client-facing portal |
| **Remote support engineer** | Takes phone calls, uses ad-hoc remote tools, no record | Works a prioritised queue, launches consented recorded sessions, resolves without leaving the desk |
| **Client IT manager** | Phones 1000FiX when something breaks | Sees their estate health, open incidents, patch compliance and SLA attainment in the portal |
| **Field technician** | Attends every problem | Attends only what genuinely needs hands on hardware — 65% resolved remotely |
| **Account manager** | Has no data for a renewal conversation | Brings a service report with SLA attainment, incident trends and recommendations |
| **Finance** | Cannot see whether an MSP contract is profitable | Cost to serve against contract value per client, monthly |
| **CFO** | Cannot forecast recurring revenue | MSP contracts produce predictable monthly revenue with visible entitlement consumption |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **New recurring revenue line** | A deliverable managed-services business at scale rather than a promise | **BDT 95 lac/year** at steady state (base case) |
| **Truck-roll avoidance** | Remote resolution of software, configuration and network faults | **65% remote resolution**; each avoided visit saves a full technician job slot plus travel |
| **Margin quality** | Recurring revenue with declining marginal cost as automation matures | **> 55% gross margin** — the highest of any 1000FiX line |
| **Proactive intervention** | Alerts before failure rather than calls after it | Converts unplanned client downtime into planned maintenance |
| **SLA credit control** | Credits calculated automatically and visible before they accumulate | Prevents silent margin erosion on contracts |
| **Renewal defensibility** | Evidence-based service reviews | Supports the **88% contract renewal** target for MSP contracts |
| **Corporate account expansion** | Monitoring reveals ageing assets and refresh needs | Feeds M07 pipeline with qualified, evidenced opportunities |
| **24/7 commitment made real** | On-call rota, out-of-hours routing, coverage-aware SLA | Turns a marketing claim into a contractual, measurable service |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Strategic repositioning** | Moves 1000FiX up the value chain from break-fix vendor to IT services partner — the single largest change in how the Company is perceived by corporate buyers |
| **Client stickiness** | An MSP client with agents deployed and history accumulated does not switch casually |
| **Capability development** | Remote engineering is a different skill set from field repair; building it broadens the Company's talent base |
| **Reference customers** | Enterprise clients under managed service become the references that win the next tender |
| **Security posture credibility** | Managing clients' security posture requires managing your own — this raises 1000FiX's internal standard |
| **Expansion enabler** | Managed services are geography-independent; this is the line that can serve a second country before physical branches exist there |

---

## 8. Lifecycle & State Models

### 8.1 Alert

```
   DETECTED ──► CORRELATED ──► TICKET RAISED ──► ACKNOWLEDGED ──► RESOLVED ──► CLOSED
       │             │                                │
       │             └──► SUPPRESSED (maintenance window / known noise)
       │                                              │
       └──► DE-DUPLICATED (existing open alert)       └──► ESCALATED (on-call rota)
```

### 8.2 MSP Ticket

```
   ┌──────────┐
   │   NEW    │  (from alert, client portal, email, phone or chat)
   └────┬─────┘
        │ classified: service, urgency, impact → priority
   ┌────▼─────┐
   │ TRIAGED  │  ← contractual SLA clock starts on the response threshold
   └────┬─────┘
        │ assigned
   ┌────▼──────────┐
   │ IN PROGRESS   │
   └────┬──────────┘
        │
   ┌────▼──────────┐   awaiting client / awaiting vendor / scheduled change
   │  PENDING      │   ← SLA clock suspended per contract terms
   └────┬──────────┘
        │
   ┌────▼──────────┐
   │  RESOLVED     │  ← resolution recorded; client notified
   └────┬──────────┘
        │ client confirms or auto-close window elapses
   ┌────▼──────────┐
   │   CLOSED      │
   └───────────────┘

   Branches:  ESCALATED TO FIELD (M02 work order created, ticket remains parent)
              LINKED TO PROBLEM (recurring incident)
              MAJOR INCIDENT (structured handling, all contacts notified)
```

### 8.3 Client Onboarding

```
   CONTRACT SIGNED (M08)
        │
   ┌────▼────────────┐
   │ ONBOARDING      │  project created in M67
   │ INITIATED       │
   └────┬────────────┘
        │
   ┌────▼────────────┐   estate discovery · agent deployment · baseline capture
   │ ESTATE          │   contact registration · portal access · runbook authoring
   │ ONBOARDING      │   alert threshold tuning · SLA configuration
   └────┬────────────┘
        │ coverage verified ≥ agreed percentage
   ┌────▼────────────┐
   │ SERVICE LIVE    │  ← SLA clocks become contractually binding from this date
   └────┬────────────┘
        │
   ┌────▼────────────┐
   │ STEADY STATE    │  monthly reporting · quarterly service review
   └────┬────────────┘
        │ contract ends or terminates
   ┌────▼────────────┐
   │ OFFBOARDING     │  agent removal · data return · access revocation · final report
   └─────────────────┘
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-RMS-01 | No remote connection may be established without explicit, logged customer consent | **H** | CTO |
| BRU-RMS-02 | Unattended access is permitted only on assets covered by a contract that grants it | **H** | Corporate Services Head |
| BRU-RMS-03 | Client environment credentials are vaulted; they may never be recorded in a ticket, note or email | **H** | CTO |
| BRU-RMS-04 | A client asset without a healthy monitoring agent is reported as a coverage gap within 24 hours | **H** | Corporate Services Head |
| BRU-RMS-05 | SLA clocks honour the contracted coverage window, not office hours | **C** | Corporate Services Head |
| BRU-RMS-06 | Service credits are calculated automatically from measured breach; manual credits require CFO approval | **C/A** | CFO |
| BRU-RMS-07 | Entitlement over-consumption is either billed or escalated for uplift; it is never absorbed silently | **H** | Finance Manager |
| BRU-RMS-08 | A change to a client environment requires a recorded change record with a rollback plan | **H** | Corporate Services Head |
| BRU-RMS-09 | Patch deployment outside an agreed maintenance window requires client approval | **H** | Corporate Services Head |
| BRU-RMS-10 | A recurring incident occurring three or more times in a rolling period must be linked to a problem record | **H** | Quality Manager |
| BRU-RMS-11 | Client offboarding is not complete until all agents are removed and all access is revoked, evidenced | **H** | CTO |
| BRU-RMS-12 | Session recordings are retained per the contract and the retention schedule, and access is logged | **H** | Quality Manager |
| BRU-RMS-13 | A client portal user sees only their own organisation's estate, tickets and reports | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.msp.contract.instance` | `fix_msp_contract_instance` | The delivery instance of an M08 contract | contract_id, client_id, coverage_window, entitlement_summary, service_live_date, state |
| `fix.monitored.asset` | `fix_monitored_asset` | An asset under monitoring | asset_id, contract_instance_id, asset_class, agent_id, monitoring_method, last_seen, health_score |
| `fix.monitor.agent` | `fix_monitor_agent` | Deployed agent | monitored_asset_id, agent_version, credential_ref, installed_at, last_checkin, health_state |
| `fix.metric.series` | `fix_metric_series` *(TimescaleDB)* | Time-series metrics | asset_id, time, metric_code, value, unit |
| `fix.alert.rule` | `fix_alert_rule` | Threshold and condition definition | asset_class, contract_tier, client_id, metric_code, condition, threshold, severity, correlation_key |
| `fix.alert` | `fix_alert` | A raised alert | rule_id, asset_id, raised_at, severity, state, correlated_to, suppressed_reason, ticket_id |
| `fix.msp.ticket` | `fix_msp_ticket` | Client service request or incident | client_id, contract_instance_id, source, type, service, urgency, impact, priority, state, sla_policy_id, assigned_to |
| `fix.problem.record` | `fix_problem_record` | Recurring incident root cause | client_id, linked_ticket_ids, root_cause, permanent_fix, state |
| `fix.change.record` | `fix_change_record` | Change to a client environment | client_id, description, risk, approval, rollback_plan, executed_at, outcome |
| `fix.remote.session` | `fix_remote_session` | A remote assistance session | ticket_id, engineer_id, asset_id, consent_ref, started_at, ended_at, duration_min, recording_ref, files_transferred |
| `fix.patch.job` | `fix_patch_job` | Patch deployment | client_id, asset_ids, patch_set, window_id, state, results_json, rollback_available |
| `fix.runbook` | `fix_runbook` | Remediation procedure | code, trigger_condition, steps_json, automated, approval_required, version |
| `fix.runbook.execution` | `fix_runbook_execution` | Execution audit | runbook_id, alert_id, asset_id, executed_at, output, outcome |
| `fix.oncall.rota` | `fix_oncall_rota` | Coverage schedule | period, engineer_id, coverage_window, escalation_order |
| `fix.maintenance.window` | `fix_maintenance_window` | Agreed suppression period | client_id, asset_scope, start, end, purpose, approved_by |
| `fix.service.review` | `fix_service_review` | Client review meeting | client_id, period, attendees, sla_summary, actions, next_date |
| `fix.sla.credit` | `fix_sla_credit` | Calculated credit | contract_instance_id, period, breach_summary, credit_amount, state |
| `fix.client.contact.permission` | `fix_client_contact_permission` | Who may do what | client_id, party_id, permissions, escalation_preference |
| `fix.backup.oversight` | `fix_backup_oversight` | Backup job monitoring (with M06) | client_id, asset_id, plan_ref, last_run, outcome, consecutive_failures |
| `fix.dr.plan` | `fix_dr_plan` | Client DR/BC plan and tests | client_id, plan_ref, last_test_date, test_outcome, next_test_due |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.contract`, `fix.entitlement` | M08 | Read terms; report consumption |
| `fix.asset` | M17 / M49 | Read identity; create monitoring overlay |
| `fix.party`, `fix.party.hierarchy` | M33 | Read client and contacts |
| `fix.conversation` | M27 | Ticket-linked conversations |
| `fix.work.order` | M02 | Create on field escalation |
| `fix.knowledge.article` | M61 | Read and contribute |
| `fix.destruction.certificate` | M06 | Read for decommission projects |
| `fix.integration.credential` | M28 | Vaulted client credentials |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-RMS-01 | Alert threshold breached | Correlate, de-duplicate, raise a ticket, notify per escalation policy | Alert raised without ticket; escalate to duty engineer |
| AUT-RMS-02 | Alert unacknowledged beyond threshold | Escalate through the on-call rota; notify the next level | Escalate to Corporate Services Head |
| AUT-RMS-03 | Alert matched to a runbook | Execute the automated remediation; record the outcome; close if successful | Leave for manual handling; record the attempt |
| AUT-RMS-04 | Ticket SLA at 50/75/90/100% | Escalate to the assigned engineer, then team lead, then head of service | Repeat and escalate |
| AUT-RMS-05 | SLA breached | Calculate the service credit; record it against the contract instance; notify the account manager | Manual credit calculation task |
| AUT-RMS-06 | Agent stops reporting for the configured period | Raise a coverage-gap alert and a remediation ticket | Escalate |
| AUT-RMS-07 | Entitlement consumption reaches 80% / 100% | Notify the account manager; at 100% either bill overage or request uplift per contract | Manual review |
| AUT-RMS-08 | Third recurring incident of the same signature | Create a problem record and link the incidents | — |
| AUT-RMS-09 | Maintenance window starts | Suppress alerting for the defined scope; resume automatically at the end | Alerts continue; noise flagged |
| AUT-RMS-10 | Period end | Generate the client service report; publish to the portal; notify the client contacts | Manual report generation |
| AUT-RMS-11 | Client contract terminates | Initiate offboarding: schedule agent removal, access revocation and data return | Manual offboarding project |
| AUT-RMS-12 | Backup job fails twice consecutively | Raise a priority ticket and notify the client | Escalate |
| AUT-RMS-13 | Remote session ends | Store the recording, meter the duration, attach to the ticket, emit the billable event | Manual metering |
| AUT-RMS-14 | Client asset warranty expiring in 90 days | Notify the account manager with a refresh or extension recommendation | — |

---

## 12. Interfaces

### 12.1 Upstream — M05 Consumes

| Source | What | Mechanism |
|---|---|---|
| M08 Contract | Contract terms, entitlements, SLA definitions, coverage window | REST + event |
| M17 Asset Registry | Asset identity for monitored estates | REST |
| M33 Party Master | Client organisation, contacts, hierarchy | REST |
| M27 Contact Centre | Inbound client contact by phone, chat, email | Event |
| M22 Competency | Engineer certification for specialist client environments | REST |
| M55 Workforce | Engineer availability for on-call rota construction | Event projection |
| M28 Integration | Vaulted client credentials; agent communication channel | Service |
| M61 Knowledge | Solution articles and procedures | REST |
| M06 Data Services | Backup plan definitions for oversight | REST |

### 12.2 Downstream — M05 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 Service Order | Service order creation on field escalation | Command |
| M02 Field Service | Work order with full incident context | Command |
| M08 Contract | Entitlement consumption, SLA attainment | Events |
| M20 Receivable | Billable sessions, overage, SLA credits | Events |
| M39 Subscription | Recurring MSP fee basis and seat/asset counts | Events |
| M17 Asset Registry | Asset health and configuration updates | Events |
| M23 Quality | Major incidents, problem records, recurring failures | Events |
| M27 Contact Centre | Client notifications and ticket updates | Events |
| M25 Business Intelligence | Alert, ticket, SLA, health and profitability facts | Warehouse extract |
| M07 CRM | Refresh and expansion opportunities from estate analysis | Events |
| P04 Corporate Portal | Estate health, incidents, SLA, patch compliance, reports | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `alert.raised` | client, asset, rule, severity, correlation key | M27, M25 |
| `alert.escalated` | alert, escalation level, notified parties | M27 |
| `msp_ticket.created` | client, source, priority, SLA policy | M27, M25, P04 |
| `msp_ticket.acknowledged` | ticket, engineer, elapsed | M08, M25 |
| `msp_ticket.escalated_to_field` | ticket, service order, work order | M01, M02 |
| `msp_ticket.resolved` | ticket, resolution, duration, SLA outcome | M08, M20, M25, P04 |
| `sla.breached` | contract instance, ticket, breach duration, credit | M08, M20, M53 |
| `remote_session.completed` | ticket, engineer, duration, recording ref | M20, M24 |
| `entitlement.consumed` | contract instance, entitlement, quantity | M08, M39 |
| `estate.coverage_gap` | client, asset, gap duration | M08, account manager |
| `patch.compliance_reported` | client, period, compliance percentage | P04, M25 |
| `problem.identified` | client, linked incidents, signature | M23, M61 |
| `client.onboarded` | client, contract instance, assets covered, service live date | M08, M20, M67 |
| `client.offboarded` | client, agents removed, access revoked, evidence | M08, M29, M24 |
| `msp_ticket.escalated` | ticket id, client, contract, asset, severity, escalation reason, required intervention | M01, M02, M27 |
| `msp.usage_reported` | contract id, period, remote hours, incident count, patch and monitoring volumes | M39, M53, M20 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/msp/estate` | GET | Client estate with health scores | P04, P03 |
| `/api/v1/msp/assets/{id}/metrics` | GET | Time-series metrics for an asset | P03, P04 |
| `/api/v1/msp/alerts` | GET | Alert queue with filters | P03 |
| `/api/v1/msp/alerts/{id}/acknowledge` | POST | Acknowledge an alert | P03 |
| `/api/v1/msp/tickets` | GET / POST | Client ticket list and creation | P03, P04, P10 |
| `/api/v1/msp/tickets/{id}` | GET / PATCH | Ticket detail and update | P03, P04, P10 |
| `/api/v1/msp/tickets/{id}/escalate-field` | POST | Escalate to a site visit | P03 |
| `/api/v1/msp/sessions` | POST | Initiate a remote session with consent | P03, P10 |
| `/api/v1/msp/patch/schedule` | POST | Schedule a patch deployment | P03 |
| `/api/v1/msp/reports/{client}/{period}` | GET | Client service report | P04 |
| `/api/v1/msp/sla/{contract}` | GET | SLA attainment and credit position | P04, P03 |
| `/hooks/v1/agent/telemetry` | POST | Agent metric submission | Agents |
| `/hooks/v1/agent/checkin` | POST | Agent health check-in | Agents |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R13 Remote Support Engineer | C R U | Assigned clients |
| R05 Operations Director | R U A | All MSP clients |
| Corporate Services Head | C R U D A | All MSP clients |
| R22 Account Manager (Corporate) | R | Own accounts — reports and SLA |
| R35 Contact Centre Supervisor | R U | Client tickets raised through the contact centre |
| R34 Contact Centre Agent | C R | Ticket creation and status for client callers |
| R32 Quality Manager / ISO Coordinator | R | Major incidents, problems, recurring failures |
| R26 Finance Manager | R | Entitlement consumption, overage, credits, profitability |
| R33 IT / System Administrator | R U | Agent platform administration |
| R37 Corporate Portal User | R | Own organisation only — estate, tickets, reports, SLA |

**Field-level restrictions:** client credentials are never displayed; cost-to-serve is visible
to Corporate Services Head, R26 and R05 only; session recordings require explicit grant.

**Segregation of duties:** the engineer who executes a change to a client environment cannot
be the sole approver of that change (BRU-RMS-08).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Estate health board | Remote support team | Real time | All clients' assets by health score, open alerts, coverage gaps |
| Alert queue | Remote support team | Real time | Prioritised by severity, client tier and SLA risk |
| SLA attainment | Corporate Services Head, account managers | Weekly / monthly | Attainment by client, contract and priority, with breach causes |
| **Client service report** | Client (via P04) | Monthly | SLA attainment, incidents raised and resolved, patch compliance, estate health, recommendations |
| Patch compliance | Corporate Services Head, client | Monthly | Compliance by client, asset class and criticality |
| Coverage gap report | Corporate Services Head | Daily | Assets with unhealthy or missing agents |
| Remote resolution rate | Operations Director | Monthly | Percentage of tickets resolved without a site visit, by client and service type |
| Client profitability | CFO, Corporate Services Head | Monthly | Cost to serve against contract value |
| Entitlement consumption | Account managers, finance | Monthly | Consumption against contract, with overage and uplift opportunities |
| Problem and recurring incident | Quality Manager | Monthly | Problems open, permanent fixes applied, recurrence eliminated |
| On-call effectiveness | Corporate Services Head | Monthly | Out-of-hours volume, acknowledgement time, escalation rate |
| Capacity forecast | Corporate Services Head | Quarterly | Team capacity against contracted and pipeline estate growth |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-069 | Monitored assets under management | 0 | 5,000 | **8,000** |
| KPI-070 | Contractual SLA attainment | n/a | 96% | **98%** |
| KPI-071 | Remote resolution rate — no site visit | 0% | 55% | **65%** |
| KPI-072 | MSP gross margin | n/a | 48% | **55%** |
| — | Alert-to-ticket automation rate | 0% | 85% | **> 90%** |
| — | Mean time to acknowledge — P1 alert | n/a | < 15 min | **< 10 min** |
| — | Mean time to resolve — P1 incident | n/a | < 6 h | **< 4 h** |
| — | Alert noise ratio (alerts closed with no action) | n/a | < 30% | **< 15%** |
| — | Estate coverage — assets with a healthy agent | n/a | 96% | **> 99%** |
| — | Client service report delivered on schedule | n/a | 95% | **100%** |
| — | MSP client satisfaction | n/a | > 4.3/5 | **> 4.6/5** |
| — | MSP contract renewal rate | n/a | 85% | **> 90%** |
| — | Patch compliance across managed estate | n/a | 88% | **> 95%** |
| — | Coverage gaps unresolved beyond 24 h | n/a | **0** | **0** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L2 | OCA `helpdesk_mgmt`, `helpdesk_mgmt_sla`, `helpdesk_mgmt_priority` | 14% |
| L4 | Wazuh / osquery (endpoint telemetry), SNMP collector, MeshCentral / RustDesk (remote access), TimescaleDB (metrics), Grafana (operational views) | 34% |
| L5 | `cd_msp_contract`, `cd_monitoring`, `cd_alerting`, `cd_msp_ticket`, `cd_remote_session`, `cd_patch_mgmt` | 50% |
| **L6** | Commercial RMM agent — **conditional**, pending Wave 5 pilot (decision D-07) | 2% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-025 | `cd_msp_contract` — contract instance, entitlement consumption, coverage window, SLA credit | Odoo module | 6 PW |
| CD-026 | `cd_monitoring` — monitored asset, agent registry, health scoring, coverage gaps | Odoo module + service | 8 PW |
| CD-027 | `cd_alerting` — rules, correlation, de-duplication, escalation, suppression | Service | 7 PW |
| CD-028 | `cd_msp_ticket` — client ticket, contractual SLA, problem, change | Odoo module | 6 PW |
| CD-029 | `cd_remote_session` — consent, session orchestration, metering, recording linkage | Odoo module + service | 4 PW |
| CD-030 | `cd_patch_mgmt` — patch inventory, scheduling, compliance reporting | Odoo module + service | 6 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M08 Contract | An MSP contract instance requires a contract |
| M17 Asset Registry | Monitored assets require asset identity |
| M33 Party Master | Client organisation and contacts |
| M27 Contact Centre | Inbound client contact and notification |
| M02 Field Service | Escalation from remote to on-site |
| M29 Identity | Corporate SSO federation for client portal users |
| M48 IoT Platform | Shares the time-series platform — M05 may build it first if M48 is later |
| M62 Data Platform | Client reporting at scale |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing corporate AMC clients with IT scope | To be profiled | `fix.msp.contract.instance` | W5 |
| Client asset lists held by account managers | Unknown, likely spreadsheets | `fix.monitored.asset` via M17 | W5 |
| Historical support correspondence | Not migrated | — | — |

Client estates must be **discovered and onboarded**, not migrated. Onboarding each client is
a project in M67, not a data load.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | At least three pilot MSP clients are live with monitored estates and contractual SLA reporting | Client sign-off and live portal access |
| AC-02 | Alerts raise tickets automatically with de-duplication and correlation demonstrated | Scripted flapping-alert test |
| AC-03 | No remote connection is possible without logged customer consent, including via API | Negative test |
| AC-04 | Client credentials are vaulted and never appear in tickets, notes or logs | Security review and log audit |
| AC-05 | SLA clocks honour the contracted coverage window, including out-of-hours and client holidays | Test matrix across three contract tiers |
| AC-06 | Service credits are calculated automatically on breach and passed to M20 | Scripted breach scenario |
| AC-07 | Client portal shows only that client's estate, tickets and reports | Multi-tenant isolation penetration test |
| AC-08 | Monthly client service reports generate and publish automatically | Two consecutive monthly cycles |
| AC-09 | Remote resolution rate reaches 55% within the first full quarter of operation | Measured over three months |
| AC-10 | Coverage gaps are detected within 24 hours and remediated | Report over four weeks |
| AC-11 | Ingestion sustains 50,000 metric points per minute at 5,000 assets | Load test |
| AC-12 | Escalation from a remote ticket to a field visit carries full context into M02 | End-to-end demonstration |
| AC-13 | Client offboarding removes all agents and revokes all access, with evidence | Scripted offboarding of a test client |
| AC-14 | Corporate Services Head and a pilot client sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Does patch management at scale require a commercial RMM agent, or do open-source tools suffice? *(decision D-07)* | CTO / CFO | W5 pilot |
| Q-02 | What are the standard SLA tiers and their service credit schedules for each of the six contract types? | Corporate Services Head / Legal | W5 minus 2 months |
| Q-03 | What is the 24/7 staffing model — dedicated overnight shift, on-call rota, or follow-the-clock partner? | Corporate Services Head / HR | W5 minus 2 months |
| Q-04 | Do MSP contracts grant unattended remote access by default, and is that acceptable to clients? | Legal / Corporate Services Head | W5 build |
| Q-05 | Is session recording mandatory, optional, or client-configurable? What is the retention period? | Legal / Quality | W5 build |
| Q-06 | Which cloud platforms must be supported for subscription oversight — Microsoft 365, Google Workspace, AWS, Azure? | Corporate Services Head | W6 |
| Q-07 | Will 1000FiX hold cyber liability insurance for managing client environments? | CFO / Legal | W5 minus 3 months |
| Q-08 | What is the pricing model — per seat, per asset, per estate, or tiered? This drives entitlement design. | CCO / Corporate Services Head | W5 minus 2 months |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` · `M02_Field_Service_and_Dispatch_Management.md` ·
`M06_Data_Services_and_Secure_Data_Handling.md` ·
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` §6 (contract families) ·
`03_Modules/K_Platform_and_Technology/_CATEGORY_OVERVIEW.md` §3 (M05 vs M66 boundary) ·
`03_Modules/K_Platform_and_Technology/P04_Corporate_B2B_Portal.md`

**Workspace evidence**
`1000fix_business/Business planning for 1000 fix.docx` §Managed Service Contracts (six types),
§24/7 Technical Support (six support types), §IT Infrastructure AMC, §Data Backup Solutions ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Remote service feature ·
`Intergrated_web_portal/.../IMPL-46_Corporate_SSO_ERP_API_Framework.md`

**External benchmark**
RMM platform capability set — device health monitoring, software inventory, patch compliance,
security posture, per-client alerting thresholds · PSA capability set — tickets, time
tracking, SLA enforcement, contracts, client communication, invoicing · ITIL 4 — incident
versus service request, escalation and notification procedures, problem and change
management, post-incident review · SLA management practice — automated monitoring with breach
notification and proactive escalation · Wazuh, osquery, MeshCentral, RustDesk as the
open-source substrate

---

*Module M05 · Category A · 1000FiX ERP System v2.0 · CONFIDENTIAL*
