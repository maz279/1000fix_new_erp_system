# A08 · M51 — the workspace endpoints over the tax backend: the statutory
# calendar, the Mushak 6.10 high-value register and the 6.7/6.8 note
# register answer through /p03/model/report from real records and master
# data, the KPI hook returns real values, and the 9.1 preparation runs (or
# refuses honestly) through /p03/model/action. Pattern: test_p03_generic_api.
from __future__ import annotations

import itertools
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a08 import m51

_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call(odoo_env):
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@pytest.fixture
def tax(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    n = next(_SEQ)
    acc = env["res.users"].create(
        {
            "name": f"M51 Accountant {n}",
            "login": f"m51-acc-{n}@test.local",
            "group_ids": [
                (6, 0, [env.ref("base.group_user").id, env.ref("account.group_account_user").id])
            ],
            "operating_unit_ids": [(6, 0, [ou.id])],
            "default_operating_unit_id": ou.id,
        }
    )
    return {"env": env, "ou": ou, "acc": acc}


def _register(t, no, total, on="2026-09-12"):
    return t["env"]["fix.mushak.register"].create(
        {
            "operating_unit_id": t["ou"].id,
            "mushak_no": no,
            "invoice_ref": "INV-" + no,
            "invoice_date": on,
            "supplier_name": "1000 FiX Services Ltd.",
            "supplier_bin": "1234567890123",
            "customer_name": "Bashundhara Corporate",
            "customer_bin": "1234567890128",  # a repeated-digit BIN is now refused (M51-2)
            "taxable_amount": round(total / 1.15, 2),
            "vat_amount": round(total - total / 1.15, 2),
            "total_payable": total,
        }
    )


def test_statutory_calendar_from_master_data(tax, call):
    res = call(
        tax["env"](user=tax["acc"]),
        "model_report",
        module="M51",
        report="statutory_calendar",
        params={"date_from": "2026-10-01", "date_to": "2026-10-31"},
    )
    rows = {(r["obligation"], r["period"]): r for r in res["rows"]}
    vat = rows[("Mushak 9.1 return and VAT payment", "2026-09")]
    assert (vat["due_date"], vat["basis"]) == ("2026-10-15", "verify with adviser")
    wht = rows[("Quarterly withholding tax return", "2026-Q1")]
    assert (wht["due_date"], wht["basis"]) == ("2026-10-25", "confirmed")
    assert res["cols"] == [
        "due_date",
        "obligation",
        "period",
        "authority",
        "status",
        "detail",
        "basis",
    ]


def test_mushak_610_threshold_is_master_data(tax, call):
    big = _register(tax, "A08-610-1", 250000.0)
    _register(tax, "A08-610-2", 150000.0)
    res = call(
        tax["env"](user=tax["acc"]),
        "model_report",
        module="M51",
        report="mushak_610",
        params={"date_from": "2026-09-01", "date_to": "2026-09-30"},
    )
    numbers = [r["number"] for r in res["rows"]]
    assert big.mushak_no in numbers and "A08-610-2" not in numbers
    assert "200,000" in res["title"]


def test_note_register_lists_vendor_notes(tax):
    env = tax["env"]
    vendor = env["res.partner"].create({"name": "Teesta Panels"})
    bill = env["fix.vendor.invoice"].create(
        {
            "operating_unit_id": tax["ou"].id,
            "vendor_id": vendor.id,
            "invoice_ref": "TP-1",
            "invoice_date": "2026-09-01",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": env["product.product"].create({"name": "Panel"}).id,
                        "description": "Panel",
                        "unit_price": 5000.0,
                    },
                )
            ],
        }
    )
    env["fix.vendor.note"].create(
        {
            "invoice_id": bill.id,
            "note_type": "increase",
            "mushak_ref": "68-0007",
            "note_date": "2026-09-15",
            "amount": 500.0,
            "vat_amount": 75.0,
        }
    )
    res = m51.note_register(env, date_from="2026-09-01", date_to="2026-09-30")
    row = next(r for r in res["rows"] if r["number"] == "68-0007")
    assert (row["form"], row["side"], row["against"], row["vat"]) == (
        "6.8",
        "Purchase",
        "TP-1",
        75.0,
    )


def test_vat_return_prepare_through_the_endpoint(tax, call):
    env = tax["env"]
    ret = env["fix.vat.return"].create({"period": "2026-09"})
    env.company.vat = False
    res = call(
        env(user=tax["acc"]),
        "model_action",
        model="fix.vat.return",
        ids=[ret.id],
        method="action_prepare",
    )
    assert res["success"] is False and "13-digit BIN" in res["error"]
    env.company.vat = "1234567890123"
    _register(tax, "A08-91-1", 11500.0)
    res = call(
        env(user=tax["acc"]),
        "model_action",
        model="fix.vat.return",
        ids=[ret.id],
        method="action_prepare",
    )
    assert res["success"] is True
    assert (ret.state, ret.output_vat) == ("prepared", 1500.0)
    refused = call(
        env(user=tax["acc"]),
        "model_action",
        model="fix.vat.return",
        ids=[ret.id],
        method="action_file",
    )
    assert refused == {"success": False, "error": "Action not available for this surface"}


def test_kpis_are_real_values(tax):
    out = m51.kpis(tax["env"])
    assert set(out) >= {
        "vat91_latest",
        "input_credit_open",
        "certificates_due",
        "overdue_obligations",
    }
    assert isinstance(out["overdue_obligations"], int)
