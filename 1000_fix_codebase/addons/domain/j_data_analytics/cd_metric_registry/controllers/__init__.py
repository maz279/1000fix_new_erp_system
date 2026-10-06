# cd_metric_registry controllers — the P06 Analytics API surface (PP5).
#
# Serves the W4 OpenAPI contract: /analytics/dashboards (the embedded-BI
# registry + the Superset/Grafana seam) and /analytics/kpis (backend
# read_group aggregations over the real business models — the portal
# renders, never aggregates; AS-09 applies to numbers as much as money).
from . import analytics_api
