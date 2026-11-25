# SV-004 — Post-Go-Live Hypercare Operating Manual
## 1000FiX ERP System v2.0 · Category 12 (Release, Deployment & Transition) · SV-001 / P12-M04 Conformance

| Metadata | Details |
|---|---|
| **Operating Manual ID** | `SV-004-HYPERCARE-OPERATING-MANUAL` |
| **Document Version** | 1.0 (Live Operations Baseline) |
| **Governance Standard** | ITIL v4 Service Transition · SV-001 Service Levels · SV-004 Escalation Protocol |
| **Hypercare Duration** | 30 Days Post-Cutover (24/7 Coverage for Week 1–2; 16/7 Coverage for Week 3–4) |
| **Command Lead** | Head of Service Operations (Anisur Rahman) & Principal SRE Lead |
| **Status** | ACTIVE — DAY-1 OPERATIONAL |

---

### 1. Purpose & Objectives

The Hypercare phase provides heightened operational vigilance, accelerated defect triage, and hands-on super-user support following production go-live. The primary objectives are:
1. Guarantee 99.9% system availability during initial transaction scaling across all 53 service centres.
2. Resolve user adoption friction and transitional inquiries before they impact SLA commitments.
3. Rapidly remediate minor edge defects under strict hotfix change control without destabilizing core transactional engines.

---

### 2. Service Level Agreements (Standard SV-001)

Incidents reported during Hypercare are triaged according to strict contractual response and resolution timeframes:

| Severity Level | Definition | Target Response (Ack) | Target Workaround | Target Permanent Fix |
|---|---|---|---|---|
| **P1 — Critical** | Total system outage, branch unable to intake or invoice, data corruption. | **≤ 15 minutes** | **≤ 2 hours** | **≤ 4 hours** |
| **P2 — Major** | Partial degradation (e.g. one portal slow, printer driver failure in a bay). | **≤ 30 minutes** | **≤ 4 hours** | **≤ 8 hours** |
| **P3 — Moderate** | Non-blocking functional defect, single-user UI glitch, report formatting. | **≤ 2 hours** | **≤ 8 hours** | **≤ 24 hours** |
| **P4 — Minor** | Informational query, cosmetic styling enhancement, feature clarification. | **≤ 4 hours** | N/A | Next Sprint Cycle |

---

### 3. 24/7 On-Call Escalation Rota (8 Divisions)

The nationwide support network operates around the clock with designated primary and secondary engineers:

| Division | Primary On-Call Lead | Secondary Escalation (SRE) | Regional Support Bay |
|---|---|---|---|
| **Dhaka Central** | Tanvir Ahmed (Ext. 101) | Shakil Hossain (SRE) | Motijheel Flagship Hub |
| **Dhaka North & Suburbs** | Mahfuzur Rahman (Ext. 102) | Kazi Moniruzzaman (DBA) | Uttara Diagnostic Centre |
| **Chattogram** | Farzana Yasmin (Ext. 103) | Arifur Rahman (DevOps) | Agrabad Commercial Centre |
| **Rajshahi** | Shahriar Kabir (Ext. 104) | Tanvir Ahmed (SRE) | Shaheb Bazar Service Hub |
| **Khulna** | Masud Rana (Ext. 105) | Shakil Hossain (SRE) | Shib Bari Service Centre |
| **Barisal** | Nusrat Jahan (Ext. 106) | Arifur Rahman (DevOps) | Sadar Road Centre |
| **Sylhet** | Rezwanul Hoque (Ext. 107) | Kazi Moniruzzaman (DBA) | Zindabazar Regional Bay |
| **Rangpur & Mymensingh** | Kamrul Islam (Ext. 108) | Shakil Hossain (SRE) | Station Road Service Bay |

---

### 4. Daily Incident Cadence & Reporting

1. **08:30 BST — Morning Operational Sweep**: Verify all 53 service centre POS terminals online, overnight batch jobs completed, database WAL replication lag < 5s.
2. **13:00 BST — Midday Triage Standup**: Review open P2/P3 tickets, assess common user error patterns, push hotfix guidance to super-user Telegram channel.
3. **18:30 BST — Evening Close & Balance Sweep**: Audit branch cashier end-of-day balances, verify Mushak 6.3 invoice sequencing, ensure BEFTN payroll file sync.
4. **21:00 BST — Daily Stability Report**: Publish the automated operational telemetry report to Executive Steering Committee.

---

### 5. Hypercare Exit Criteria

Hypercare formally transitions to standard Business-as-Usual (BAU) support upon achieving all four exit gates:
1. **Error Budget Consumption**: Monthly API error budget consumption remains **< 10%** over 14 consecutive days.
2. **Ticket Arrival Stability**: New support ticket volume stabilizes at **< 10 tickets/day** nationwide for 5 consecutive business days.
3. **Zero Severity-1 Outages**: Zero unresolved P1 incidents and zero database rollback emergencies for 14 consecutive days.
4. **KPI Baseline Flatline**: Service order turnaround time (TAT) and customer booking conversion meet or exceed pre-programme baseline targets.
