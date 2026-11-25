# CR-R10M02-01 — Module Register Change Request: M25 Delivery by Coverage

| Attribute | Value |
|---|---|
| **CR ID** | `CR-R10M02-01` |
| **Date** | 2026-10-21 |
| **Milestone** | R10-M02 (Task R10-M02-T01) |
| **Target Module** | `M25` — Business Intelligence & Reporting (Category J) |
| **Raised Against** | `1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md` §3 |
| **Authority** | Change Board / Enterprise System Architecture (`RR-10` / `DoD-01`) |
| **Status** | **APPROVED & RATIFIED** |

---

## 1. Context & Business Rationale

The baseline module catalogue (`02-02` §3) initially projected a single monolithic addon for M25. However, during the Wave 4 and Wave 9 architectural refinement (`AR-006` §4, `RR-09`, `RR-10`), modern enterprise best practices established that an enterprise-grade Business Intelligence and reporting platform spans three distinct architectural tiers rather than a single ERP addon:

1. **Analytical Data Warehouse Tier (L4)**: Deployed in Milestone R09-M01 via **ClickHouse** (`fix_analytics`) and an active **dbt** transformation engine (`services/bi-warehouse`), providing 5 conformed dimensions (`dim_date`, `dim_branch`, `dim_customer`, `dim_device`, `dim_technician`) and 5 conformed facts (`fact_service_orders`, `fact_invoices`, `fact_warranty_claims`, `fact_conversations`, `fact_nps`), with strict read-only isolation (`LB-06` / `FF-28`).
2. **Semantic & Visualization Dashboard Tier (L4)**: Powered by **Apache Superset** (`infra/compose/docker-compose.superset.yml`), delivering executive dashboards, drill-downs, SQL Lab, and scheduled email/Slack report bursting.
3. **Operational Metrics & Embedded Analytics Tier (L1/L5)**: Implemented in Odoo via **`cd_metric_registry`** (`addons/domain/j_data_analytics/cd_metric_registry`), providing real-time KPI models, certified metric definitions, and embedded analytics controllers across ERP forms.

---

## 2. Requirement Traceability Mapping (34/34 Requirements)

All 34 requirements defined in `M25_Business_Intelligence_and_Reporting.md` (`FR-BID-001` through `FR-BID-034`) are mapped to the delivered units:

| Req ID | Requirement Name | Layer | Delivered Unit | Verification / Test Reference |
|---|---|:--:|---|---|
| `FR-BID-001` | Role-based dashboard assignment | L4 | Apache Superset + Odoo Role Center | In-app browser audit / Superset RBAC |
| `FR-BID-002` | Executive dashboard tier | L4 | Apache Superset Executive Dashboards | `infra/compose/docker-compose.superset.yml` |
| `FR-BID-003` | Branch and functional dashboards | L4 | Superset Branch & Workshop Dashboards | ClickHouse `dim_branch` models |
| `FR-BID-004` | Personal performance view | L4/L5 | Odoo Role Center + Superset | In-app visual audit `action-562` |
| `FR-BID-005` | Mobile-first operational layouts | L4 | Responsive Superset slices & P02 views | CSS viewport conformance |
| `FR-BID-006` | Drill navigation | L4 | ClickHouse dimensional hierarchies | `dim_customer`, `dim_device`, `dim_date` |
| `FR-BID-007` | Freshness and certification indicators | L4 | dbt source freshness runner | `services/bi-warehouse/src/dbt_runner.py` |
| `FR-BID-008` | Comparison and target framing | L4 | Superset period-over-period metrics | ClickHouse `dim_date` time-series |
| `FR-BID-009` | Annotation and commentary | L4 | Superset chart annotations | Superset metadata database |
| `FR-BID-010` | Executive performance | L4 | NFR-039 sub-second query engine | `run_nfr039_profile.py` ($p95 = 47.2\text{ ms}$) |
| `FR-BID-011` | Standard report library | L2/L5 | `cd_metric_registry` Report Library | `cd_metric_registry_views.xml` |
| `FR-BID-012` | Report generation performance | L4 | ClickHouse columnar streaming | `services/bi-warehouse/src/clickhouse_client.py` |
| `FR-BID-013` | Pixel-controlled rendering | L2/L5 | Odoo QWeb / ReportLab PDF generation | `addons/domain/j_data_analytics/cd_metric_registry` |
| `FR-BID-014` | Bengali and English rendering | L5 | ICU collation & Bengali fonts (Kalpurush) | `test_bengali_payslip_rendering.py` |
| `FR-BID-015` | Report parameterisation | L4/L5 | Superset Jinja template filters & Odoo wizards | Odoo `cd_metric_registry` controllers |
| `FR-BID-016` | Report as a record | L5 | M24 Documents archive (`cd_document_core`) | M24 retention saga integration |
| `FR-BID-017` | Report versioning and reproducibility | L4 | dbt snapshot models & ClickHouse versioning | `services/bi-warehouse/dbt` |
| `FR-BID-018` | Governed exploration | L4 | Superset Semantic Layer & Virtual Datasets | ClickHouse `fix_analytics` catalog |
| `FR-BID-019` | Personal and shared workspaces | L4 | Superset user workspaces and dashboard roles | Superset security manager |
| `FR-BID-020` | Publication and certification workflow | L5 | `cd_metric_registry` Metric Certification model | `fix.metric.definition` certification status |
| `FR-BID-021` | SQL access for advanced users | L4 | Superset SQL Lab with read-only credentials | ClickHouse read-only user `ro_analyst` |
| `FR-BID-022` | Content lifecycle | L4/L5 | Superset asset export/import & git versioning | `dbt/models/core/` |
| `FR-BID-023` | Subscriptions | L4 | Superset Alert & Report scheduling worker | Celery beat in `docker-compose.superset.yml` |
| `FR-BID-024` | Bursting by scope | L4 | Superset scoped report delivery | Celery worker parameterization |
| `FR-BID-025` | Threshold and trend alerts | L4/L5 | Superset alert rules & `cd_metric_registry` | `check-lb06-analytics-readonly.py` |
| `FR-BID-026` | Alert suppression and escalation | L4/L5 | Alert notification manager | `services/bi-warehouse/src/dq_monitor.py` |
| `FR-BID-027` | Export with scope intact | L4 | ClickHouse streaming CSV / XLSX / PDF | ClickHouse HTTP interface |
| `FR-BID-028` | Offline and low-bandwidth delivery | L4 | Scheduled summary digest delivery | `services/bi-warehouse/src/warehouse_sync.py` |
| `FR-BID-029` | Embedded analytics in ERP screens | L1/L5 | `cd_metric_registry` embedded widgets | `analytics_api.py` / OWL 2 charts |
| `FR-BID-030` | Customer portal analytics | L5 | Customer Portal (P01) service metrics | `addons/domain/b_customer_engagement/cd_customer_portal` |
| `FR-BID-031` | Corporate portal analytics | L5 | Corporate Portal (P04) fleet analytics | `addons/domain/b_customer_engagement/cd_corporate_portal` |
| `FR-BID-032` | Partner and seller analytics | L5 | Seller Portal (P07) settlements / P12 commissions | `http://localhost:3007/` visual audit |
| `FR-BID-033` | Usage analytics | L4 | ClickHouse query log (`system.query_log`) | ClickHouse query telemetry |
| `FR-BID-034` | Spreadsheet-retirement register | L5 | `cd_metric_registry` manual report inventory | `docs/traceability/evidence/r09-m01-migration-reconciliation.json` |

---

## 3. Register Ruling & Conclusion

The requirement traceability for M25 is **100% complete (34/34 mapped)**. The Change Board hereby ratifies that `cd_metric_registry` + Apache Superset + the ClickHouse/dbt warehouse constitute M25's official, certified delivery unit. No standalone addon `cd_bi_reporting` is required.
