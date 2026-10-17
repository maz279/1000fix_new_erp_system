# PE-008 Alert Fatigue & Operational Observability Review

**Document Reference:** `docs/traceability/pe-008-alert-fatigue-review.md`  
**Milestone:** R04-M05 (Observability Wiring, Journey Automation, and G3)  
**Standard Compliance:** NFR-092, PE-008, SV-004 on-call policy  
**Last Audit:** October 2026 (Gate G3 Go-Live)

---

## 1. Executive Summary & Design Principles

Alert fatigue is fundamentally treated as an **architectural defect**, not an inevitable operational friction. Under PE-008 and SV-004:
1. **Actionability Mandate:** Every alert in `infra/observability/prometheus/fix-alerts.yml` must explicitly name an operational action, designate a specific engineering/operations owner (`labels.team`), and provide a link to a verified remediation runbook (`annotations.runbook`).
2. **Multi-Window Multi-Burn-Rate Protection:** To eliminate transient blips, alerts employ dual-window evaluation (e.g. fast burn 5m/2m vs slow burn 30m/15m) preventing noisy paging during momentary spikes while guaranteeing rapid escalation during systemic outages.
3. **Correlation ID Integration:** All alert incidents correlate to logs in Loki and traces in Tempo via `x-fix-correlation-id` and W3C `traceparent` headers.

---

## 2. Operational Dashboards (PE-008)

Four dedicated operational dashboards are deployed in `infra/observability/grafana/dashboards/`:

| Dashboard UID | Name | Primary Focus | Key SLIs / Thresholds |
|---|---|---|---|
| `fix-dispatch-operations` | Dispatch & Field Service Operations | Field technician queue, SLA adherence, and routing | Auto-dispatch rate $\ge 85\%$, On-time arrival $\ge 95\%$, Queue depth $< 25$ |
| `fix-gps-health` | Mobile Technician GPS & Telemetry Health | Fleet telemetry, ping frequency, and device battery | Transit ping interval p95 $\le 30$s, Drift accuracy $< 25$m, Battery $< 20\%$ alerts |
| `fix-payment-rails` | Payment Gateway Rails & Settlement | bKash, Nagad, SSLCommerz uptime, latency, and match rate | Gateway success rate $\ge 98\%$, Latency p95 $< 2$s, Auto-match rate $\ge 90\%$ |
| `fix-period-close` | Financial Period Close & Trial Balance | Accounting period close velocity and integrity | Stages 1–6 checklist, Suspense balance $= 0.00$ BDT, Imbalance $= 0.00$ BDT |

---

## 3. Anti-Fatigue Alerting Inventory & Triage Policy

| Alert Name | Group | Severity | Team | Evaluation Window | Action / Runbook Summary |
|---|---|---|---|---|---|
| `InvoiceAutomationGap` | `fix-service-to-cash` | `critical` | `finance` | 15m breach of 98% | Check billing engine consumer; review `fix.ar.invoice` chatter. |
| `PaymentMatchRateBelowGate` | `fix-service-to-cash` | `warning` | `finance` | 1h below 85% | Inspect reconciliation service log; review new bank statement narration rules. |
| `OutboxBacklog` | `fix-service-to-cash` | `critical` | `platform` | 10m backlog > 500 | Check transactional outbox drain worker; replay from oldest pending. |
| `NotificationDeliveryDegraded` | `fix-service-to-cash` | `warning` | `platform` | 30m below 90% | Verify SMS/email fallback register (IP-09) and carrier API limits. |
| `SuspenseNotCleared` | `fix-service-to-cash` | `critical` | `finance` | 1h approaching close | Reconcile suspense account before month-end close (refused by model if non-zero). |
| `DispatchQueueStalled` | `fix-dispatch-and-field` | `critical` | `operations` | 10m backlog > 30 | Check candidate scoring engine & Redis cache; trigger manual batch dispatch. |
| `SlaBreachCluster` | `fix-dispatch-and-field` | `warning` | `operations` | 5m breach > 5 | Open Operations Workspace; redistribute tickets to floating field technicians. |
| `GpsSignalBlackoutCluster` | `fix-gps-telemetry` | `warning` | `platform` | 5m timeouts > 10 | Inspect mobile gateway telemetry ingestion endpoint and Cloudflare WS termination. |
| `PaymentGatewayBurnRateCritical` | `fix-payment-rails` | `critical` | `finance` | 2m failure rate > 5% | Verify payment-connectors token refresh; check bKash/SSLCommerz incident portals. |
| `PaymentReconciliationDrift` | `fix-payment-rails` | `warning` | `finance` | 2h unmatched > 50 | Trigger MFS statement re-poll; inspect raw transaction logs for schema changes. |
| `TrialBalanceOutOfBalance` | `fix-period-close` | `critical` | `finance` | 1m discrepancy > 0.01 | **CRITICAL INTEGRITY**: Run `verify_gl_integrity.py` to isolate unbalanced journal entries. |
| `PeriodCloseStalled` | `fix-period-close` | `warning` | `finance` | 6h duration > 5 days | Review open checklist items in `fix.period.close`; finalize VAT Mushak 9.1. |

---

## 4. Verification & Audit Sign-Off

- **Alert Noise Reduction:** Zero un-owned alerts. All 12 alerts mapped to either `finance`, `operations`, or `platform`.
- **Runbook Coverage:** 100% of alerts carry executable runbook annotations.
- **Traceability Linkage:** Dashboards and alerts directly reference their associated NFRs (`NFR-040`, `NFR-081`, `NFR-092`), architecture standards (`AS-08`, `AR-006`), and Gate criteria (`G3-01` through `G3-06`).
