# cd_vendor_portal tests — P05 W3 (P06-M09).
import re
import unittest
from pathlib import Path

VIEWS = (Path(__file__).resolve().parents[1] / "views"
         / "fix_vendor_portal_views.xml").read_text(encoding="utf-8")


class TestVendorScoping(unittest.TestCase):
    def test_ea05_record_rule(self):
        """A vendor sees only their own POs — enforced by a record rule."""
        self.assertIn('rule_fix_vendor_po_self', VIEWS)
        self.assertIn("ir.rule", VIEWS)

    def test_portal_group_extends_portal_not_internal(self):
        # Quote-agnostic: the XML legitimately writes ref('base.group_portal')
        # single-quoted inside eval="..." attributes.
        self.assertRegex(VIEWS, r"""ref\(["']base\.group_portal["']\)""")
        self.assertNotRegex(VIEWS, r"""ref\(["']base\.group_user["']\)""")


class TestThreeWayFeed(unittest.TestCase):
    def test_invoice_submission_surface(self):
        """T03: vendors submit into fix.vendor.invoice (the matcher's input)."""
        self.assertIn("fix.vendor.invoice", VIEWS)

    def test_block_visibility(self):
        """G3-06: a blocked invoice stays VISIBLE (with its reason) — a
        rejected invoice the vendor cannot see becomes a support ticket."""
        ap_ext = (Path(__file__).resolve().parents[3] / "g_finance" / "cd_ap_ext"
                  / "models" / "fix_ap_ext.py").read_text(encoding="utf-8")
        self.assertIn("match_detail", ap_ext)  # the reason travels


class TestManifest(unittest.TestCase):
    def test_cd_id_is_register_member(self):
        import yaml
        manifest = (Path(__file__).resolve().parents[1]
                    / "__manifest__.py").read_text(encoding="utf-8")
        cd_id = re.search(r'"x_cd_id":\s*"([^"]+)"', manifest).group(1)
        register = yaml.safe_load((Path(__file__).resolve().parents[5]
                                   / "tooling" / "cd-register.yaml"
                                   ).read_text(encoding="utf-8"))
        ids = {item["id"] for item in register["items"]}
        self.assertIn(cd_id, ids)


if __name__ == "__main__":
    unittest.main()
