# A08 · M52 — the workspace endpoints over the AP backend: every REPORTS
# function answers through /p03/model/report from real records (ageing,
# GRNI from PO receipts, expense by category, duplicate log), the KPI hook
# returns real numbers, and workflow actions run (or refuse honestly)
# through /p03/model/action. The module-level `request` is patched with the
# rolled-back odoo_env (pattern: test_p03_generic_api.py).
from __future__ import annotations

import itertools
from datetime import date, timedelta
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a08 import m52

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


def _user(env, ou, *groups):
    n = next(_SEQ)
    return env["res.users"].create(
        {
            "name": f"M52 User {n}",
            "login": f"m52-user-{n}@test.local",
            "group_ids": [(6, 0, [env.ref(g).id for g in ("base.group_user", *groups)])],
            "operating_unit_ids": [(6, 0, [ou.id])],
            "default_operating_unit_id": ou.id,
        }
    )


@pytest.fixture
def ap(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    vendor = env["res.partner"].create({"name": "Karnaphuli Components Ltd."})
    # A08 M52-10: a PSR counts only with its proof attached, and a vendor with
    # no TIN pays the non-filer rate; this vendor files, so TDS is the base 5%.
    psr_proof = env["ir.attachment"].create({"name": "PSR-K.pdf", "datas": "UFNSLUs="})
    env["fix.vendor.tax.profile"].create(
        {
            "partner_id": vendor.id,
            "taxpayer_type": "company",
            "tin": "123456789013",
            "psr_reference": "PSR-K",
            "psr_valid_until": "2099-06-30",
            "psr_attachment_ids": [(6, 0, psr_proof.ids)],
        }
    )
    product = env["product.product"].create({"name": "Compressor 1.5T"})
    return {
        "env": env,
        "ou": ou,
        "vendor": vendor,
        "product": product,
        "acc": _user(env, ou, "account.group_account_user"),
        "clerk": _user(env, ou),
    }


def _bill(ap, price, qty=1.0, ref=None, po=None, **vals):
    return ap["env"]["fix.vendor.invoice"].create(
        {
            "operating_unit_id": ap["ou"].id,
            "vendor_id": ap["vendor"].id,
            "invoice_ref": ref or "KC-%d" % next(_SEQ),
            "requisition_id": po.id if po else False,
            # G3-06: a PO-type bill with no purchase order is "unmatched" and
            # is refused at submission. A bill raised here without a PO is a
            # non-PO bill (approval-matrix control); one with a PO keeps the
            # three-way match (a non-PO bill may not carry a PO at all).
            "bill_type": "po" if po else "non_po",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": ap["product"].id,
                        "description": "Compressor",
                        "quantity": qty,
                        "unit_price": price,
                        "tds_category": "supply_of_goods",
                    },
                )
            ],
            **vals,
        }
    )


def test_ap_ageing_buckets_from_due_dates(ap, call):
    env = ap["env"]
    today = date.today()
    old = _bill(ap, 10000.0, invoice_date=today - timedelta(days=80), payment_term_days=30)
    fresh = _bill(ap, 2000.0, invoice_date=today, payment_term_days=30)
    _bill(ap, 999.0)  # draft: not a payable yet
    (old | fresh).write({"approval_state": "approved"})
    res = call(env(user=ap["acc"]), "model_report", module="M52", report="ap_ageing", params={})
    row = next(r for r in res["rows"] if r["vendor"] == "Karnaphuli Components Ltd.")
    # 10,000 less 5% TDS = 9,500 at 50 days past due; 1,900 not due
    assert (row["d31_60"], row["current"], row["total"]) == (9500.0, 1900.0, 11400.0)
    assert res["cols"][0] == "vendor" and "d90" in res["labels"]


def test_report_reads_with_the_callers_rights(ap, call):
    res = call(ap["env"](user=ap["clerk"]), "model_report", module="M52", report="ap_ageing")
    assert "error" in res and "rows" not in res


def test_grni_from_po_receipts_less_invoiced_quantity(ap, call):
    env = ap["env"]
    po = env["fix.purchase.order"].create(
        {
            "operating_unit_id": ap["ou"].id,
            "vendor_id": ap["vendor"].id,
            "line_ids": [
                (0, 0, {"product_id": ap["product"].id, "qty_ordered": 5.0, "unit_price": 3000.0})
            ],
        }
    )
    # A06 S3/S7: goods are received only on an approved, sent PO to an active
    # supplier. Approval routing is tested in cd_requisition; here the PO is
    # put in the approved state directly so the report's arithmetic is tested.
    supplier = env["fix.supplier"].create(
        {"name": ap["vendor"].name, "partner_id": ap["vendor"].id, "status": "active"}
    )
    for doc_type in ("trade_licence", "tin", "vat"):
        env["fix.supplier.document"].create(
            {"supplier_id": supplier.id, "doc_type": doc_type, "state": "valid"}
        )
    po.action_record_requisition_exception(reason="A08 GRNI report test PO")
    po._guarded().write(
        {
            "approval_state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": po._dofa_current_tier(),
            "dofa_approved_amount": po.amount_total,
        }
    )
    po.action_send()
    po.action_record_receipt({po.line_ids.id: 3.0})
    # A06 ERP audit X26 / P13: GRNI is one as-at basis that ties to the GL
    # account, so only a POSTED bill reduces it; a draft bill has not cleared
    # anything yet (a posted bill's reduction: cd_ap_ext test_x26)
    _bill(ap, 3000.0, qty=1.0, po=po)
    res = call(env(user=ap["acc"]), "model_report", module="M52", report="grni_accruals")
    row = next(r for r in res["rows"] if r["po"] == po.name)
    assert (row["received"], row["invoiced"], row["open_qty"], row["accrual"]) == (
        3.0,
        0.0,
        3.0,
        9000.0,
    )
    assert row["received_on"] == str(date.today())


def test_expense_by_category_and_duplicate_log(ap, call):
    env = ap["env"]
    employee = env["hr.employee"].create({"name": "Technician Sumon"})
    claim = env["fix.expense.claim"].create(
        {
            "operating_unit_id": ap["ou"].id,
            "employee_id": employee.id,
            "description": "Site visit",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "category_id": env.ref("cd_ap_ext.expense_category_conveyance").id,
                        "unit_amount": 750.0,
                    },
                )
            ],
        }
    )
    claim.state = "approved"
    res = m52.expense_by_category(env, date_from=str(date.today()), date_to=str(date.today()))
    assert {
        "category": "Local conveyance (rickshaw, CNG, ride-share)",
        "lines": 1,
        "amount": 750.0,
    } in res["rows"]
    _bill(ap, 100.0, ref="DUP-9")
    _bill(ap, 100.0, ref="dup-9 ")
    dup = m52.duplicate_bills(env)
    assert len([r for r in dup["rows"] if r["rule"] == "Same reference"]) == 2


def test_kpis_are_real_numbers(ap):
    env = ap["env"]
    # A06 ERP audit P09: a non-PO bill needs an active, registered supplier
    supplier = env["fix.supplier"].create(
        {"name": ap["vendor"].name, "partner_id": ap["vendor"].id, "status": "active"}
    )
    for doc_type in ("trade_licence", "tin", "vat"):
        env["fix.supplier.document"].create(
            {"supplier_id": supplier.id, "doc_type": doc_type, "state": "valid"}
        )
    before = m52.kpis(env)
    bill = _bill(ap, 1000.0)
    bill.action_submit_approval()
    after = m52.kpis(env)
    assert after["bills_to_approve"] == before["bills_to_approve"] + 1
    assert isinstance(after["tds_mtd"], float)


def test_actions_through_the_endpoint_refuse_honestly(ap, call):
    env = ap["env"]
    run = env["fix.payment.run"].create({"due_by": "2000-01-01"})
    res = call(
        env(user=ap["acc"]),
        "model_action",
        model="fix.payment.run",
        ids=[run.id],
        method="action_propose",
    )
    assert res["success"] is False and "No approved, matched" in res["error"]
    rows = call(
        env(user=ap["acc"]),
        "model_records",
        model="fix.payment.run",
        cols=["name", "rail", "state", "total_amount"],
    )
    assert any(r["id"] == run.id and r["state"]["key"] == "draft" for r in rows["rows"])
