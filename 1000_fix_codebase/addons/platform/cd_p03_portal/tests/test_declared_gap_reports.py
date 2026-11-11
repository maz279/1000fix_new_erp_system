# P03 declared-gap report packs (headless walk of 8069, 12 Nov 2026).
#
# Four workspace reports rendered "report not built (... declared gap)":
#
#   * M11-brand       - the warranty-claim ledger (cd_warranty_claims) and the
#                       OEM invoices raised from claims (fix.ar.invoice with
#                       source_model='fix.warranty.claim') now exist, so the
#                       pack is BUILT from them;
#   * M12-stock       - still a gap: no seller-keyed stock record exists;
#   * M12-training    - still a gap: training/certification is keyed to staff
#                       (hr.employee), never to a marketplace seller;
#   * M40-comarketing - still a gap: no campaign carries a channel-partner key
#                       and no MDF accrual carries a campaign key.
#
# The built pack is checked against seeded claims and invoices; each gap pack
# is checked for its labels AND for the model fact its note states, so the
# day someone adds the missing link this suite fails and the gap gets built.
from __future__ import annotations

import datetime
import uuid

import pytest
from odoo import Command
from odoo.addons.cd_p03_portal.controllers.a04 import m11, m12, m40

TAG = uuid.uuid4().hex[:6].upper()


def _labels_cover(pack):
    """Labels are a {col: header} dict naming every column (never a list)."""
    assert isinstance(pack["labels"], dict)
    assert set(pack["labels"]) == set(pack["cols"])
    assert all(isinstance(v, str) and v for v in pack["labels"].values())


# --------------------------------------------------------------------- M11


@pytest.fixture()
def ledger(odoo_env):
    env = odoo_env
    for model in ("fix.warranty.claim", "fix.ar.invoice", "fix.service.order"):
        if model not in env:
            pytest.skip("%s not installed" % model)
    env.user.tz = "Asia/Dhaka"  # rolled back with the test
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    if not ou:
        pytest.skip("no operating unit in the test company")
    entity = env["fix.entity"].create(
        {"code": "GE%s" % TAG, "legal_name": "Gap Entity %s" % TAG, "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "Gap Desk %s" % TAG,
            "code": "GB%s" % TAG,
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand_a = env["fix.brand"].create({"name": "GapBrandA %s" % TAG, "code": "GA%s" % TAG})
    brand_b = env["fix.brand"].create({"name": "GapBrandB %s" % TAG, "code": "GZ%s" % TAG})
    model = env["fix.device.model"].create({"name": "GapPhone %s" % TAG, "brand_id": brand_a.id})
    customer = env["res.partner"].create({"name": "Gap Customer %s" % TAG})
    oem = env["res.partner"].create({"name": "Gap OEM %s" % TAG})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-GAP-%s" % TAG}
    )
    today = datetime.date.today()
    env["fix.warranty"].create(  # BRU-SRM-02: a warranty order needs active cover
        {
            "device_id": device.id,
            "start_date": today - datetime.timedelta(days=60),
            "end_date": today + datetime.timedelta(days=300),
            "status": "active",
        }
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Gap fault",
            "order_category": "warranty",
        }
    )

    def claim(brand, amount, state, approved=0.0, remitted=0.0, submitted=None, paid_at=None):
        rec = env["fix.warranty.claim"].create(
            {
                "operating_unit_id": ou.id,
                "service_order_id": order.id,
                "brand_id": brand.id,
                "claim_amount": amount,
            }
        )
        env.flush_all()
        # the decided state is set directly: the decision workflow is M09's
        # own suite; this pack only reads what a decided claim carries
        env.cr.execute(
            "UPDATE fix_warranty_claim SET state=%s, approved_amount=%s, "
            "remittance_amount=%s, submitted_at=%s, remitted_at=%s WHERE id=%s",
            [state, approved, remitted, submitted, paid_at, rec.id],
        )
        rec.invalidate_recordset()
        return rec

    def invoice(claim_rec, amount, state):
        inv = env["fix.ar.invoice"].create(
            {
                "company_id": claim_rec.company_id.id,
                "operating_unit_id": ou.id,
                "customer_id": oem.id,
                "source_model": "fix.warranty.claim",
                "source_id": claim_rec.id,
                "manual_reason": "Gap test claim invoice",
                "line_ids": [
                    Command.create(
                        {
                            "description": "Claim reimbursement",
                            "taxable_amount": amount,
                            "vat_amount": 0.0,
                            "line_total": amount,
                        }
                    )
                ],
            }
        )
        env.flush_all()
        env.cr.execute("UPDATE fix_ar_invoice SET state=%s WHERE id=%s", [state, inv.id])
        inv.invalidate_recordset()
        return inv

    sub = datetime.datetime(2026, 11, 1, 4, 0, 0)
    # Brand A: one settled (10 days), one partial still owed, one rejected, one open
    a_paid = claim(
        brand_a,
        10000.0,
        "remitted",
        approved=10000.0,
        remitted=10000.0,
        submitted=sub,
        paid_at=sub + datetime.timedelta(days=10),
    )
    a_part = claim(brand_a, 6000.0, "partially_approved", approved=4000.0, submitted=sub)
    claim(brand_a, 3000.0, "rejected", submitted=sub)
    claim(brand_a, 2000.0, "submitted", submitted=sub)
    invoice(a_paid, 10000.0, "paid")
    invoice(a_part, 4000.0, "draft")  # the hand-off draft: not invoiced yet
    # Brand B: one settled in 4 days, then closed
    b_paid = claim(
        brand_b,
        5000.0,
        "closed",
        approved=5000.0,
        remitted=5000.0,
        submitted=sub,
        paid_at=datetime.datetime(2026, 11, 5, 4, 0, 0),
    )
    invoice(b_paid, 5000.0, "issued")
    return env, brand_a, brand_b, b_paid


def _row(pack, brand):
    hits = [r for r in pack["rows"] if r["brand"] == brand.name]
    assert len(hits) == 1, pack["rows"]
    return hits[0]


def test_brand_reimbursement_is_built_from_the_claim_ledger(ledger):
    env, brand_a, brand_b, _b = ledger
    pack = m11.brand_reimbursement(env)
    assert pack["cols"] == [
        "brand",
        "raised",
        "approved",
        "rejected",
        "pending",
        "claimed",
        "approved_amount",
        "invoiced",
        "received",
        "recovery_pct",
        "avg_days",
        "last_received",
    ]
    _labels_cover(pack)
    assert pack["labels"]["invoiced"] == "Invoiced to OEM"
    assert pack["labels"]["avg_days"] == "Avg Days to Reimbursement"
    assert not any("declared gap" in n for n in pack["notes"])

    a = _row(pack, brand_a)
    assert (a["raised"], a["approved"], a["rejected"], a["pending"]) == (4, 2, 1, 1)
    assert a["claimed"] == 21000.0
    assert a["approved_amount"] == 14000.0
    assert a["invoiced"] == 10000.0  # the draft hand-off invoice is not counted
    assert a["received"] == 10000.0
    assert a["recovery_pct"] == round(10000.0 / 21000.0 * 100.0, 1)
    assert a["avg_days"] == 10.0  # only the settled claim has a reimbursement
    # 2026-11-11 04:00 UTC shown on the reader's wall clock (Asia/Dhaka)
    assert a["last_received"] == "2026-11-11 10:00"

    b = _row(pack, brand_b)
    assert (b["raised"], b["approved"], b["rejected"], b["pending"]) == (1, 1, 0, 0)
    assert (b["claimed"], b["invoiced"], b["received"]) == (5000.0, 5000.0, 5000.0)
    assert b["recovery_pct"] == 100.0
    assert b["avg_days"] == 4.0

    note = " ".join(pack["notes"])
    assert "1 draft" in note and "4000.00" in note  # the un-issued hand-off is declared


def test_brand_reimbursement_totals(ledger):
    env, brand_a, brand_b, _b = ledger
    pack = m11.brand_reimbursement(env)
    mine = [r for r in pack["rows"] if r["brand"] in (brand_a.name, brand_b.name)]
    totals = pack["totals"]
    assert totals["brand"] == "Total"
    # the test database may hold other claims: the totals cover every row
    assert totals["raised"] == sum(r["raised"] for r in pack["rows"])
    assert totals["received"] == round(sum(r["received"] for r in pack["rows"]), 2)
    assert sum(r["raised"] for r in mine) == 5


def test_brand_reimbursement_applies_the_company_fence(ledger):
    env, _a, brand_b, b_paid = ledger
    other = env["res.company"].create({"name": "Gap Other Co %s" % TAG})
    # a new company is granted to its creator: take it away again
    env.user.write({"company_ids": [Command.unlink(other.id)]})
    assert other not in env.user.company_ids
    env.cr.execute("UPDATE fix_warranty_claim SET company_id=%s WHERE id=%s", [other.id, b_paid.id])
    env.invalidate_all()
    pack = m11.brand_reimbursement(env)
    assert not [r for r in pack["rows"] if r["brand"] == brand_b.name]


def test_brand_reimbursement_runs_for_a_plain_internal_reader(ledger):
    """A pricing reader with no finance role: the claims are theirs to read
    (operating unit), the invoices are summed for them without an AccessError."""
    env, brand_a, _b, b_paid = ledger
    ou = b_paid.operating_unit_id
    reader = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Gap reader %s" % TAG,
                "login": "gap_reader_%s@example.test" % TAG,
                "group_ids": [Command.set([env.ref("base.group_user").id])],
                "operating_unit_ids": [Command.set(ou.ids)],
                "default_operating_unit_id": ou.id,
                "tz": "Asia/Dhaka",
            }
        )
    )
    env.flush_all()
    env.invalidate_all()
    pack = m11.brand_reimbursement(env(user=reader.id))
    a = _row(pack, brand_a)
    assert (a["raised"], a["invoiced"], a["received"]) == (4, 10000.0, 10000.0)
    assert a["last_received"] == "2026-11-11 10:00"


def test_brand_reimbursement_reads_claims_as_the_caller():
    """The claims are the caller's own search (the M09 operating-unit rule
    applies), never a sudo() read; the invoices are read only for them."""
    import inspect

    source = inspect.getsource(m11._brand_claims)
    assert 'env["fix.warranty.claim"].search(' in source
    assert "sudo()" not in source
    assert "_company_domain(" in source
    assert "_datetime_to_local(" in inspect.getsource(m11.brand_reimbursement)


# --------------------------------------------------------------------- still gaps


def test_seller_stock_stays_a_declared_gap_and_says_what_is_missing(odoo_env):
    env = odoo_env
    if "fix.marketplace.listing" not in env:
        pytest.skip("cd_marketplace not installed")
    pack = m12.stock_gap(env)
    _labels_cover(pack)
    assert pack["rows"] == []
    note = " ".join(pack["notes"])
    assert "fix.marketplace.listing" in note and "quantity" in note
    assert "fix.graded.stock" in note
    # the facts the note states
    listing = env["fix.marketplace.listing"]._fields
    assert not [n for n in listing if "qty" in n or "quantity" in n or "stock" in n]
    if "fix.graded.stock" in env:
        graded = env["fix.graded.stock"]._fields
        assert not [
            n
            for n, f in graded.items()
            if f.type == "many2one" and f.comodel_name == "fix.marketplace.seller"
        ]


def test_seller_training_stays_a_declared_gap_and_says_what_is_missing(odoo_env):
    env = odoo_env
    pack = m12.training_gap(env)
    _labels_cover(pack)
    assert pack["rows"] == []
    note = " ".join(pack["notes"])
    assert "hr.employee" in note and "fix.marketplace.seller" in note
    for model in ("fix.training.enrollment", "fix.certification"):
        if model in env:
            assert env[model]._fields["employee_id"].comodel_name == "hr.employee"
            assert not [
                n
                for n, f in env[model]._fields.items()
                if getattr(f, "comodel_name", None) == "fix.marketplace.seller"
            ]


def test_comarketing_stays_a_declared_gap_and_says_what_is_missing(odoo_env):
    env = odoo_env
    if "fix.campaign" not in env or "fix.partner" not in env:
        pytest.skip("cd_campaign / cd_partner not installed")
    pack = m40.comarketing_gap(env)
    _labels_cover(pack)
    assert pack["rows"] == []
    note = " ".join(pack["notes"])
    assert "fix.campaign" in note and "fix.partner.rebate" in note
    campaign = env["fix.campaign"]._fields
    assert not [n for n, f in campaign.items() if getattr(f, "comodel_name", None) == "fix.partner"]
    rebate = env["fix.partner.rebate"]._fields
    assert not [n for n, f in rebate.items() if getattr(f, "comodel_name", None) == "fix.campaign"]
