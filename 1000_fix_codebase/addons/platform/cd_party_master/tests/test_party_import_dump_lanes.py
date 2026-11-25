# Customer and contact lanes of the legacy partner-dump layout (2026-11-10
# audit). The legacy "vendor.xlsx" is the full contact list, so the dump
# layout needs lanes that grant the customer role or no role at all — the
# vendor lane alone turned every walk-in customer into a supplier.
from __future__ import annotations

import base64
import io
import uuid

import pytest

U = uuid.uuid4().hex[:6].upper()

HEADER = [
    "City",
    "Complete Name",
    "Country",
    "Email",
    "Phone",
    "Salesperson",
    "Address",
    "PAN",
    "CIN",
    "Customer Area",
]


def _workbook(rows) -> str:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(HEADER)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


ROWS = [
    ["Dhaka", "RAHIM TRADERS %s" % U, "Bangladesh", "", "01711222001", "", "", "", "", ""],
    [None, "Mr Karim %s" % U, None, None, "01711222002", None, None, None, None, None],
    [None, "01711222003 Babu %s" % U, None, None, None, None, None, None, None, None],
]


def _run(env, kind, ref):
    batch = env["fix.party.import.batch"].create(
        {
            "sheet_kind": kind,
            "import_ref": ref,
            "source_file": _workbook(ROWS),
            "source_filename": "%s_test.xlsx" % kind,
        }
    )
    batch.action_stage()
    batch.action_validate()
    batch.action_import()
    batch.action_decide_registrations()
    return batch


def _roles(env, batch):
    partners = batch.line_ids.mapped("created_partner_id")
    return partners, env["fix.party.role"].search([("partner_id", "in", partners.ids)])


class TestPartnerDumpLanes:
    def test_customer_lane_grants_customer_role_only(self, odoo_env):
        batch = _run(odoo_env, "customer", "CUSTT-%s" % U)
        partners, roles = _roles(odoo_env, batch)
        assert len(partners) == 3
        assert set(partners.mapped("party_status")) == {"active"}
        assert set(roles.mapped("role_type")) == {"customer"}
        assert len(roles) == 3
        # the phone carried as a name prefix is recovered, as on the vendor lane
        babu = partners.filtered(lambda p: "Babu" in p.name)
        assert babu and not babu.name.startswith("017")

    def test_contact_lane_grants_no_role(self, odoo_env):
        batch = _run(odoo_env, "contact", "CONTT-%s" % U)
        partners, roles = _roles(odoo_env, batch)
        assert len(partners) == 3
        assert set(partners.mapped("party_status")) == {"active"}
        assert not roles
        assert "none (contact list carries no trading role)" in batch.decision_log

    def test_supplier_register_refuses_non_vendor_lanes(self, odoo_env):
        if not hasattr(odoo_env["fix.party.import.batch"], "action_register_suppliers"):
            pytest.skip("cd_vendor_portal not installed")
        from odoo.exceptions import UserError

        batch = _run(odoo_env, "customer", "CUSTS-%s" % U)
        with pytest.raises(UserError, match="vendor-ledger batches only"):
            batch.action_register_suppliers()

    def test_vendor_lane_on_existing_customer_adds_the_second_role(self, odoo_env):
        """One party, many roles: a customer that is also a supplier keeps a
        single party record and gains the vendor role."""
        first = _run(odoo_env, "customer", "CUSTD-%s" % U)
        customers = first.line_ids.mapped("created_partner_id")
        second = _run(odoo_env, "vendor", "VENDD-%s" % U)
        assert not second.line_ids.mapped("created_partner_id"), "no duplicate party"
        roles = odoo_env["fix.party.role"].search([("partner_id", "in", customers.ids)])
        by_partner = {}
        for role in roles:
            by_partner.setdefault(role.partner_id.id, set()).add(role.role_type)
        assert all(kinds == {"customer", "vendor"} for kinds in by_partner.values())
        assert len(by_partner) == 3
