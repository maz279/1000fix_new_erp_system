# BI warehouse + M25 dashboards — P07-M07 (CD-M62-nn W4 / CD-M25-nn)

The dimensional model over the READ REPLICA (T01: never the primary; LB-06
— T11 intelligence is read-only downstream, no analytics write touches an
OLTP model).

- `dbt/` — the conformed model (T03/T04): dim_date/branch/customer/device/
  technician + the fact backbone (service orders, invoices, warranty claims,
  conversations, NPS)
- `kpi-register.json` — T06: the instrumented KPI register surfaced in M25
  (the BM-002 95/250 reconciliation is recorded at the gate); the 5
  dashboard sets (T05) ride these facts; the RP-* content set loads the
  definitions (T09)
- Apache Superset connects to the replica; P06 (analytics portal) embeds
  Superset + Grafana with R5's declared partial conformance
