# cd_corporate_portal tests — P04 W4 (P07-M09).
from pathlib import Path
import unittest
import yaml

MODULE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
VIEWS = (MODULE / "views" / "fix_corporate_portal_views.xml").read_text(encoding="utf-8")
# The portal group lives in security/ (loads before ir.model.access.csv).
SECURITY = (MODULE / "security" / "fix_corporate_portal_security.xml").read_text(encoding="utf-8")


class TestEa05Scoping(unittest.TestCase):
    def test_record_rule_enforces_own_contracts(self):
        self.assertIn("rule_fix_contract_corporate_self", VIEWS)
        self.assertIn("ir.rule", VIEWS)

    def test_portal_group_not_internal(self):
        self.assertIn("ref('base.group_portal')", SECURITY)
        self.assertNotIn("ref('base.group_user')", SECURITY)


class TestApiSurface(unittest.TestCase):
    def test_openapi_has_corporate_operations(self):
        import json
        spec = json.loads((REPO / "services" / "portal-contracts"
                           / "openapi-w4-portals.json").read_text(encoding="utf-8"))
        self.assertIn("/corporate/estate", spec["paths"])
        self.assertIn("/corporate/invoices/consolidated", spec["paths"])
        self.assertIn("/corporate/service-requests", spec["paths"])


class TestManifest(unittest.TestCase):
    def test_cd_id_is_register_member(self):
        import re
        manifest = (MODULE / "__manifest__.py").read_text(encoding="utf-8")
        cd_id = re.search(r'"x_cd_id":\s*"([^"]+)"', manifest).group(1)
        register = yaml.safe_load((REPO / "tooling" / "cd-register.yaml"
                                   ).read_text(encoding="utf-8"))
        ids = {item["id"] for item in register["items"]}
        self.assertIn(cd_id, ids)


if __name__ == "__main__":
    unittest.main()
