# Service Transition Handover Record — Milestone R11-M04-T04
## 1000FiX ERP System v2.0 · Category 11 (Service Operations & Support) · SV-001

| Metadata | Details |
|---|---|
| **Document Ref** | `R11-M04-T04-SERVICE-TRANSITION-HANDOVER` |
| **Standards Basis** | ISO/IEC 20000-1:2018 · ITIL 4 · SV-001 / SV-004 |
| **Computed handover status** | FAIL |
| **Checks** | 6 PASS / 1 FAIL / 10 UNMEASURED |
| **Recorded at** | 2026-10-22T14:34:46.029707+00:00 |
| **Tool** | `tooling/scripts/execute_service_transition.py` (GV-009: statuses computed in this run) |

---

### 1. Service Level Performance (SV-001)

| Severity | Metric | Contract Target | Measured Actual | Status |
|---|---|:---:|:---:|:---:|
| P1_Critical | Target Ack Time | <= 15 min | not measured | UNMEASURED |
| P1_Critical | Target Resolution Time | <= 4 hours | not measured | UNMEASURED |
| P2_Major | Target Ack Time | <= 30 min | not measured | UNMEASURED |
| P2_Major | Target Resolution Time | <= 8 hours | not measured | UNMEASURED |
| P3_Moderate | Target Ack Time | <= 2 hours | not measured | UNMEASURED |
| P4_Minor | Target Ack Time | <= 4 hours | not measured | UNMEASURED |
| Global | System Availability (Uptime) | >= 99.90% | not measured | UNMEASURED |

_requires production ITSM incident records / availability monitoring for the measurement window; none are available to this tool._

---

### 2. On-Call Escalation Rota

1. **Dhaka Central** (Motijheel Flagship Hub): Tanvir Ahmed (Senior Infrastructure Lead)
2. **Dhaka North & Suburbs** (Uttara Diagnostic Centre): Mahfuzur Rahman (Systems Administrator)
3. **Chattogram** (Agrabad Commercial Centre): Farzana Yasmin (Regional Service Lead)
4. **Rajshahi** (Shaheb Bazar Service Hub): Shahriar Kabir (Field Support Engineer)
5. **Khulna** (Shib Bari Service Centre): Masud Rana (Regional Operations Engineer)
6. **Barisal** (Sadar Road Centre): Nusrat Jahan (Support Specialist)
7. **Sylhet** (Zindabazar Regional Bay): Rezwanul Hoque (Service Operations Lead)
8. **Rangpur & Mymensingh** (Station Road Service Bay): Kamrul Islam (Field Network Engineer)

- `SV004_ROTA_DOCUMENTED`: FAIL — SV-004-hypercare-operating-manual.md missing

- `SV004_ROTA_ACCEPTED`: UNMEASURED — requires the paging configuration and each BAU lead's acceptance of the rota

---

### 3. Operational Artefacts

| Asset | Identifier | Recipient | Status | Detail |
|---|---|---|:---:|---|
| Module operational runbooks | `docs/runbooks/master-runbook-index.json` | ITSM Knowledge Base (M66) | PASS | 70/70 indexed module runbooks present |
| Master Cutover Runbook | `docs/runbooks/RB-53-production-cutover-master-runbook.md` | SRE Documentation Repository | PASS | docs/runbooks/RB-53-production-cutover-master-runbook.md present |
| Branch Rollout Runbook | `docs/runbooks/RB-51-branch-rollout-runbook.md` | Field Operations Management | PASS | docs/runbooks/RB-51-branch-rollout-runbook.md present |
| Disaster Recovery & Failover Manual | `docs/runbooks/RB-52-dr-disaster-recovery-and-cutover.md` | Principal DBA & DR Lead | PASS | docs/runbooks/RB-52-dr-disaster-recovery-and-cutover.md present |
| Doctor Health Diagnostic Harness | `tooling/scripts/doctor.ps1` | ITSM Level-2 Support Desk | PASS | tooling/scripts/doctor.ps1 present |
| Prometheus Alert Rules | `infra/observability/prometheus/fix-alerts.yml` | SOC / NOC Operations Team | PASS | infra/observability/prometheus/fix-alerts.yml present |
| custody acceptance | `-` | - | UNMEASURED | requires each recipient's acknowledgement of operational custody |

---

### 4. Acceptance & Transition Sign-Off

- Head of IT Service Management (ITSM) — Anisur Rahman (1000FiX Services Limited): signature not recorded
- Head of Customer Care & Contact Centre — Shabnam Mustari (1000FiX Services Limited): signature not recorded
- Service Delivery Director — Khandaker Farhad (1000FiX Services Limited): signature not recorded
- Outgoing Programme Director — Syed Tarique Hasan (Enterprise Solutions International Ltd): signature not recorded

Not accepted: the computed handover status is FAIL; acceptance requires every check to pass, including the named signatures.
