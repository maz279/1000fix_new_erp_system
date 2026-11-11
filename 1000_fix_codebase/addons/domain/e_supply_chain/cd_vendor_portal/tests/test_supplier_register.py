# Vendor-ledger satellites (readiness report §7A steps 2–4): the M42
# supplier register + tax profiles created from an imported vendor batch,
# and the rollback that removes exactly those rows.
from __future__ import annotations

import base64
import io
import uuid

import pytest

U = uuid.uuid4().hex[:6].upper()


def _vendor_workbook() -> bytes:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(
        [
            "Complete Name",
            "Phone",
            "Email",
            "Address",
            "City",
            "Country",
            "Salesperson",
            "Customer Area",
            "PAN",
            "CIN",
        ]
    )
    ws.append(
        [
            "MEPRO TECHNOLOGY %s LIMITED" % U,
            "01711112001",
            "md_asad%s@maitrox.com" % U.lower(),
            "Level 3, Gulshan",
            "Dhaka",
            "Bangladesh",
            "",
            "",
            "770290310039",
            "",
        ]
    )
    ws.append(["SAIFUL ISLAM %s" % U, "01711112002", "", "", "", "", "", "", "", ""])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.fixture()
def vbatch(odoo_env):
    batch = odoo_env["fix.party.import.batch"].create(
        {
            "sheet_kind": "vendor",
            "source_file": base64.b64encode(_vendor_workbook()).decode(),
            "source_filename": "unit_vendor_satellites.xlsx",
            "import_ref": "VSAT-%s" % U,
        }
    )
    batch.action_stage()
    batch.action_validate()
    batch.action_import()
    batch.action_decide_registrations()
    batch.action_assign_roles()
    return batch


@pytest.mark.financial
class TestSupplierRegistration:
    def test_registers_qualified_transactional_with_tax_profile(self, odoo_env, vbatch):
        vbatch.action_register_suppliers()
        Supplier = odoo_env["fix.supplier"]
        partners = vbatch.line_ids.mapped("created_partner_id")
        suppliers = Supplier.search([("partner_id", "in", partners.ids)])
        assert len(suppliers) == len(partners)
        for sup in suppliers:
            # the legacy-mass policy: qualified/transactional, gates NOT bypassed
            assert sup.status == "qualified"
            assert sup.segment == "transactional"
            assert sup.supplier_code.startswith("SUP/")
        mepro = next(s for s in suppliers if "MEPRO" in s.name)
        assert mepro.partner_id.party_class == "dealer"
        profile = odoo_env["fix.vendor.tax.profile"].search(
            [("partner_id", "=", mepro.partner_id.id)]
        )
        assert len(profile) == 1 and profile.tin == "770290310039"
        saiful = next(s for s in suppliers if "SAIFUL" in s.name)
        assert saiful.partner_id.party_class == "individual"
        assert not odoo_env["fix.vendor.tax.profile"].search_count(
            [("partner_id", "=", saiful.partner_id.id)]
        )

    def test_idempotent(self, odoo_env, vbatch):
        vbatch.action_register_suppliers()
        vbatch.action_register_suppliers()
        partners = vbatch.line_ids.mapped("created_partner_id")
        assert odoo_env["fix.supplier"].search_count([("partner_id", "in", partners.ids)]) == len(
            partners
        )

    def test_guards(self, odoo_env, vbatch):
        from odoo.exceptions import UserError

        corp = odoo_env["fix.party.import.batch"].create(
            {"sheet_kind": "corp", "import_ref": "X-%s" % U}
        )
        with pytest.raises(UserError):
            corp.action_register_suppliers()

    def test_rollback_removes_satellites(self, odoo_env, vbatch):
        vbatch.action_register_suppliers()
        partners = vbatch.line_ids.mapped("created_partner_id")
        assert odoo_env["fix.supplier"].search_count([("partner_id", "in", partners.ids)])
        vbatch.action_rollback()
        assert not odoo_env["fix.supplier"].search_count([("partner_id", "in", partners.ids)])
        for partner in partners:
            assert not partner.exists()
