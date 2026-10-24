"""Behavioural tests for the P04 corporate portal API (live ORM).

``odoo_env`` (fix_test, rolled back per test) with ``odoo.http.request``
replaced by a stand-in carrying the caller's ``env``: every read and write runs
under the caller's own access rights, exactly as in production.
"""

from contextlib import contextmanager
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo.addons.cd_corporate_portal.controllers import corporate_api
from odoo.addons.cd_corporate_portal.controllers.corporate_api import CorporateApiController


@contextmanager
def _as(env, user):
    with patch.object(corporate_api, "request", SimpleNamespace(env=env(user=user.id))):
        yield CorporateApiController()


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    # fix.entity is UNIQUE per company: a dedicated company avoids queueing
    # behind other suites' entity on the shared test database
    company = env["res.company"].create({"name": "Corporate Portal Test Co"})
    entity = env["fix.entity"].create(
        {"code": "CORPENT", "legal_name": "Corporate Test Entity", "company_id": company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "Corp Motijheel",
            "code": "CORPMJ",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "CorpBrand", "code": "CORPBR"})
    model = env["fix.device.model"].create({"name": "Corp Laptop 14", "brand_id": brand.id})
    acme = env["res.partner"].create({"name": "ACME Garments Ltd", "is_company": True})
    acme_it = env["res.partner"].create({"name": "ACME IT Desk", "parent_id": acme.id})
    other = env["res.partner"].create({"name": "Other Corp Ltd", "is_company": True})
    laptop = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": acme_it.id, "serial_number": "SN-CORP-0001"}
    )
    # Multi-company correctness (R01 re-audit): the fixture's branch lives in
    # the dedicated test company; the requesting admin must be ALLOWED there,
    # mirroring a real corporate portal user provisioned for that company.
    env.ref("base.user_admin").company_ids = [(4, company.id)]
    return SimpleNamespace(
        env=env,
        admin=env.ref("base.user_admin"),
        ou=ou,
        branch=branch,
        model=model,
        acme=acme,
        other=other,
        laptop=laptop,
    )


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (1.999, "2.00"),  # regression: was "1.00" (fraction rounded on its own)
        (-1234.5, "-1,234.50"),  # regression: was "-1,2340.50"
        (12345678, "1,23,45,678.00"),
        (999, "999.00"),
        ("x", "0.00"),
    ],
)
def test_amounts_are_south_asian_grouped(amount, expected):
    assert corporate_api._fmt_bdt(amount) == expected


def test_estate_reports_warranty_status(world):
    env = world.env
    bare = env["fix.device"].create(
        {
            "device_model_id": world.model.id,
            "owner_id": world.acme.id,
            "serial_number": "SN-CORP-0002",
        }
    )
    env["fix.warranty"].create(
        {
            "device_id": world.laptop.id,
            "start_date": date.today() - timedelta(days=30),
            "end_date": date.today() + timedelta(days=335),
            "status": "active",
        }
    )
    with _as(env, world.admin) as ctrl:
        res = ctrl.estate()
    rows = {d["id"]: d for d in res["devices"]}
    covered, uncovered = rows[world.laptop.id], rows[bare.id]
    assert (covered["brand"], covered["model"], covered["identifier"]) == (
        "CorpBrand",
        "Corp Laptop 14",
        "SN-COR…",
    )
    assert covered["warranty_status"] == "active"
    assert covered["warranty_end"] == str(date.today() + timedelta(days=335))
    assert (uncovered["warranty_status"], uncovered["warranty_end"]) == ("pending", None)


def test_consolidated_invoices_are_vat_inclusive_gross_and_payable_net(world):
    """Regression: net was computed as taxable value MINUS VAT."""
    env = world.env
    invoices = env["fix.ar.invoice"]
    invoice = invoices.create(
        {
            "operating_unit_id": world.ou.id,
            "customer_id": world.acme.id,
            "source_model": "fix.service.order",
            "source_id": 1,
            "invoice_date": date.today(),
            "loyalty_discount_amount": 50.0,
        }
    )
    env["fix.ar.invoice.line"].create(
        {"invoice_id": invoice.id, "taxable_amount": 1000.0, "vat_amount": 150.0}
    )
    voided = invoices.create(
        {
            "operating_unit_id": world.ou.id,
            "customer_id": world.acme.id,
            "source_model": "fix.service.order",
            "source_id": 2,
            "state": "cancelled",
        }
    )
    with _as(env, world.admin) as ctrl:
        res = ctrl.consolidated_invoices()
    rows = {r["id"]: r for r in res["invoices"]}
    assert voided.id not in rows
    row = rows[invoice.id]
    assert row["invoice_no"] == f"AR-{invoice.id:05d}"
    assert row["customer"] == "ACME Garments Ltd"
    assert (row["gross_bdt"], row["vat_bdt"], row["net_bdt"]) == ("1,150.00", "150.00", "1,100.00")


def test_service_request_validation(world):
    with _as(world.env, world.admin) as ctrl:
        bad_category = ctrl.service_requests(order_category="goodwill")
        no_customer = ctrl.service_requests(order_category="standard")
        no_device = ctrl.service_requests(order_category="amc", customer_id=world.acme.id)
        no_fault = ctrl.service_requests(
            order_category="standard", customer_id=world.acme.id, device_id=world.laptop.id
        )
        ghost = ctrl.service_requests(
            order_category="standard",
            customer_id="acme",
            device_id=world.laptop.id,
            fault_description="Fan noise",
        )
        foreign = ctrl.service_requests(
            order_category="standard",
            customer_id=world.other.id,
            device_id=world.laptop.id,
            fault_description="Fan noise",
        )
    assert bad_category["error"]["code"] == "invalid_category"
    assert no_customer["error"]["code"] == "missing_customer"
    assert no_device["error"]["code"] == "missing_device"
    assert no_fault["error"]["code"] == "missing_fault"
    assert ghost["error"]["code"] == "not_found"
    assert foreign["error"]["code"] == "not_owner"


def test_service_request_is_created_and_tracked(world):
    with _as(world.env, world.admin) as ctrl:
        created = ctrl.service_requests(
            order_category="amc",
            customer_id=world.acme.id,  # the company; the device sits with its IT desk
            device_id=world.laptop.id,
            fault_description="Keyboard dead",
        )
        tracked = ctrl.service_requests()
    order = world.env["fix.service.order"].browse(created["id"])
    assert (order.customer_id, order.device_id, order.branch_id) == (
        world.acme,
        world.laptop,
        world.branch,
    )
    row = next(o for o in tracked["orders"] if o["id"] == order.id)
    assert (row["customer"], row["state"]) == ("ACME Garments Ltd", order.state)
    assert row["device"] == world.laptop.name


def test_service_request_model_gates_leave_nothing_behind(world):
    with _as(world.env, world.admin) as ctrl:
        res = ctrl.service_requests(
            order_category="warranty",  # no active warranty: BRU-SRM-02 refuses
            customer_id=world.acme.id,
            device_id=world.laptop.id,
            fault_description="Hinge cracked",
        )
    assert res["error"]["code"] == "server_validation"
    assert "BRU-SRM-02" in res["error"]["message"]
    assert not world.env["fix.service.order"].search([("device_id", "=", world.laptop.id)])


def test_corporate_users_see_only_their_own_companys_contracts(world):
    """Regression (EA-05): the record rule was [('customer_id.partner_share', '=',
    True)] - true for EVERY customer - so any corporate user read all tenants'
    contracts."""
    env = world.env
    group = env.ref("cd_corporate_portal.group_fix_corporate_portal")
    buyer = env["res.partner"].create({"name": "ACME Procurement", "parent_id": world.acme.id})
    corporate_user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "ACME Procurement",
                "login": "procurement@acme.test",
                "partner_id": buyer.id,
                "group_ids": [(6, 0, [group.id])],
            }
        )
    )

    def contract(code, customer):
        return env["fix.contract"].create(
            {
                "operating_unit_id": world.ou.id,
                "code": code,
                "name": f"AMC {code}",
                "family": "amc",
                "customer_id": customer.id,
                "date_start": date(2026, 1, 1),
                "date_end": date(2026, 12, 31),
                "annual_value": 120000.0,
            }
        )

    own = contract("CORP-AMC-ACME", world.acme)
    theirs = contract("CORP-AMC-OTHER", world.other)
    visible = (
        env["fix.contract"].with_user(corporate_user).search([("id", "in", (own | theirs).ids)])
    )
    assert visible == own


def test_service_request_needs_an_intake_branch(world):
    branches = type(world.env["fix.branch"])
    with (
        patch.object(branches, "search", return_value=world.env["fix.branch"]),
        _as(world.env, world.admin) as ctrl,
    ):
        res = ctrl.service_requests(
            order_category="standard",
            customer_id=world.acme.id,
            device_id=world.laptop.id,
            fault_description="Fan noise",
        )
    assert res["error"]["code"] == "no_branch"


def _corporate_user(world, partner, login):
    env = world.env
    group = env.ref("cd_corporate_portal.group_fix_corporate_portal")
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": partner.name,
                "login": login,
                "partner_id": partner.id,
                "group_ids": [(6, 0, [group.id])],
                "company_id": world.branch.company_id.id,
                "company_ids": [(6, 0, [world.branch.company_id.id])],
            }
        )
    )


def test_portal_service_request_ignores_the_client_customer_id(world):
    """Regression: the API trusted the client's customer_id (the UI falls back
    to partner 1) - a corporate user could book for / probe any partner. The
    customer is now the session's commercial partner."""
    env = world.env
    buyer = env["res.partner"].create({"name": "ACME Buyer", "parent_id": world.acme.id})
    user = _corporate_user(world, buyer, "buyer@acme.test")
    with _as(env, user) as ctrl:
        created = ctrl.service_requests(
            order_category="standard",
            customer_id=world.other.id,  # forged: ignored
            device_id=world.laptop.id,
            fault_description="Screen flicker",
        )
        foreign_device = env["fix.device"].create(
            {
                "device_model_id": world.model.id,
                "owner_id": world.other.id,
                "serial_number": "SN-CORP-OTHER",
            }
        )
        refused = ctrl.service_requests(
            order_category="standard",
            customer_id=world.other.id,
            device_id=foreign_device.id,
            fault_description="Probe",
        )
        tracked = ctrl.service_requests()
    order = env["fix.service.order"].browse(created["id"])
    assert order.customer_id == world.acme
    assert refused["error"]["code"] == "not_found"
    assert not env["fix.service.order"].search([("device_id", "=", foreign_device.id)])
    assert {o["id"] for o in tracked["orders"]} == {order.id}


def test_portal_estate_and_invoices_are_fenced_to_the_tenant(world):
    env = world.env
    buyer = env["res.partner"].create({"name": "ACME Buyer 2", "parent_id": world.acme.id})
    user = _corporate_user(world, buyer, "buyer2@acme.test")
    theirs = env["fix.device"].create(
        {"device_model_id": world.model.id, "owner_id": world.other.id, "serial_number": "SN-X-1"}
    )
    with _as(env, user) as ctrl:
        estate = ctrl.estate()
        invoices = ctrl.consolidated_invoices()
    ids = {d["id"] for d in estate["devices"]}
    assert world.laptop.id in ids and theirs.id not in ids
    assert all(r["customer"] != "Other Corp Ltd" for r in invoices["invoices"])


def test_corporate_users_see_only_their_own_subscriptions_and_conversations(world):
    env = world.env
    buyer = env["res.partner"].create({"name": "ACME Buyer 3", "parent_id": world.acme.id})
    user = _corporate_user(world, buyer, "buyer3@acme.test")
    user.company_ids = [(4, env.company.id)]  # the conversations' company
    rules = env["ir.rule"].search(
        [
            ("groups", "in", env.ref("cd_corporate_portal.group_fix_corporate_portal").id),
            ("model_id.model", "in", ["fix.subscription", "fix.conversation"]),
        ]
    )
    assert set(rules.mapped("model_id.model")) == {"fix.subscription", "fix.conversation"}
    assert all("commercial_partner_id" in r.domain_force for r in rules)
    Conversation = env["fix.conversation"]
    mine = Conversation.create({"customer_id": world.acme.id, "operating_unit_id": world.ou.id})
    theirs = Conversation.create({"customer_id": world.other.id, "operating_unit_id": world.ou.id})
    visible = Conversation.with_user(user).search([("id", "in", (mine | theirs).ids)])
    assert visible == mine
