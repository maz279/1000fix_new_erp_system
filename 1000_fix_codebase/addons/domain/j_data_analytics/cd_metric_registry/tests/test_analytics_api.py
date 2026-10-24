# cd_metric_registry tests — P06 Analytics API surface (source-level).
import re
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
API = (MODULE / "controllers" / "analytics_api.py").read_text(encoding="utf-8")
MANIFEST = (MODULE / "__manifest__.py").read_text(encoding="utf-8")


class TestNoDataInPortalLayer(unittest.TestCase):
    """P06's special requirement: the portal layer holds no data — KPIs
    are read_group aggregations, embeds are config-driven frames."""

    def test_kpis_use_read_group_not_record_math(self):
        self.assertGreaterEqual(API.count("read_group("), 3)

    def test_no_business_model_search(self):
        # no per-record search loops — only grouped aggregation
        self.assertNotIn(".search(\n", API)

    def test_embed_urls_from_config_only(self):
        self.assertIn("ir.config_parameter", API)
        self.assertNotIn("http://", API.replace("127.0.0.1", ""))
        self.assertNotIn("https://", API)

    def test_embed_none_when_unconfigured(self):
        # None (not a fake URL) when the deployment set no embed host
        self.assertIn("embed_url", API)
        self.assertIn("embed_available", API)

    def test_registry_is_navigation_not_data(self):
        # the dashboard list mirrors M25 groups — static by design
        self.assertIn("DASHBOARDS", API)
        self.assertIn('"executive"', API)
        self.assertIn('"warranty"', API)


class TestApiSurface(unittest.TestCase):
    def test_openapi_has_analytics_operations(self):
        import json

        spec = json.loads(
            (REPO / "contracts" / "openapi" / "w4-portals.json").read_text(encoding="utf-8")
        )
        self.assertIn("/analytics/dashboards", spec["paths"])
        self.assertIn("/analytics/kpis", spec["paths"])
        self.assertIn("/analytics/kpis/register", spec["paths"])
        self.assertIn("/analytics/governance/catalogue", spec["paths"])
        self.assertIn("/analytics/governance/lineage", spec["paths"])
        self.assertIn("/analytics/governance/dq", spec["paths"])
        self.assertIn("/analytics/governance/residency", spec["paths"])
        self.assertIn("/analytics/stt/dashboard", spec["paths"])

    def test_routes_json_auth_user_readonly(self):
        routes = re.findall(
            r'@http\.route\("(/analytics/[^"]+)"[^)]*type="jsonrpc",\s*'
            r'auth="user",\s*readonly=True',
            API,
        )
        self.assertEqual(len(routes), 8, routes)
        self.assertIn("/analytics/dashboards", routes)
        self.assertIn("/analytics/kpis", routes)
        self.assertIn("/analytics/kpis/register", routes)
        self.assertIn("/analytics/governance/catalogue", routes)
        self.assertIn("/analytics/governance/lineage", routes)
        self.assertIn("/analytics/governance/dq", routes)
        self.assertIn("/analytics/governance/residency", routes)
        self.assertIn("/analytics/stt/dashboard", routes)

    def test_invalid_dashboard_is_rejected(self):
        self.assertIn("invalid_dashboard", API)

    def test_manifest_gained_kpi_deps(self):
        self.assertIn("cd_service_order", MANIFEST)
        self.assertIn("cd_warranty_claims", MANIFEST)


if __name__ == "__main__":
    unittest.main()
