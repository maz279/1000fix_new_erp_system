# P03 declared-gap report packs (headless walk of 8069, 12 Nov 2026).
#
# Four workspace reports rendered "report not built (... declared gap)". All
# four are now BUILT, each from the record its gap note named as missing:
#
#   * M11-brand       - the warranty-claim ledger (cd_warranty_claims) and the
#                       OEM invoices raised from claims (fix.ar.invoice with
#                       source_model='fix.warranty.claim');
#   * M12-stock       - fix.seller.stock, the seller's position per listing
#                       and SKU (on hand, reserved, who reported it and when);
#   * M12-training    - fix.seller.certification against fix.seller.standard,
#                       whose category mapping says what a seller must hold;
#   * M40-comarketing - fix.campaign.partner_ids (co-marketing partners) and
#                       fix.partner.rebate.campaign_id (the MDF's campaign),
#                       with revenue only from the M35 touch attribution.
#
# Each pack is checked against seeded records, read as the caller inside the
# company fence.
from __future__ import annotations

import datetime
import uuid

import pytest
from odoo import Command, fields
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
        "card_in_force",  # the brand rate card in force (M11, 6e1ba619)
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


# ------------------------------------------------- M12-stock / M12-training / M40-comarketing
#
# Built 12 Nov 2026 from the links the gap notes named as missing:
# fix.seller.stock (seller position per listing and SKU), fix.seller.standard /
# fix.seller.certification (seller-keyed standards with expiry), and
# fix.campaign.partner_ids + fix.partner.rebate.campaign_id (co-marketing).


def _set(env, rec, field, value):
    """Put a stamp the server owns where a test needs it (an old report, a
    certificate about to expire): set in SQL, never through the guard."""
    env.flush_all()
    env.cr.execute("UPDATE %s SET %s=%%s WHERE id=%%s" % (rec._table, field), [value, rec.id])
    rec.invalidate_recordset()


@pytest.fixture()
def market(odoo_env):
    env = odoo_env
    if "fix.marketplace.listing" not in env:
        pytest.skip("cd_marketplace not installed")
    env.user.tz = "Asia/Dhaka"  # rolled back with the test
    x = type("Market", (), {})()
    x.env = env
    x.cat = env["product.category"].create({"name": "Gap Screens %s" % TAG})

    def seller(name, categories=()):
        return env["fix.marketplace.seller"].create(
            {
                "name": name,
                "partner_id": env["res.partner"].create({"name": name}).id,
                "category_ids": [Command.set(list(categories))],
            }
        )

    x.s1 = seller("Gap Seller One %s" % TAG, x.cat.ids)
    x.s2 = seller("Gap Seller Two %s" % TAG)
    x.l1 = env["fix.marketplace.listing"].create(
        {"name": "Gap Screen Swap %s" % TAG, "seller_id": x.s1.id, "category_id": x.cat.id}
    )
    x.l2 = env["fix.marketplace.listing"].create(
        {"name": "Gap Battery Swap %s" % TAG, "seller_id": x.s2.id}
    )
    return x


def _position(env, listing, sku, qty, reserved=0.0, last=None):
    pos = env["fix.seller.stock"].create(
        {"listing_id": listing.id, "sku": sku, "qty_on_hand": qty, "qty_reserved": reserved}
    )
    if last:
        _set(env, pos, "last_updated", last)
    return pos


def _sku_row(pack, sku):
    hits = [r for r in pack["rows"] if r["sku"] == sku]
    assert len(hits) == 1, pack["rows"]
    return hits[0]


def test_seller_stock_is_built_from_the_seller_positions(market):
    env = market.env
    now = fields.Datetime.now()  # naive UTC, as stored
    _position(env, market.l1, "GA-%s" % TAG, 10, 3)
    _position(env, market.l1, "GB-%s" % TAG, 5, last=datetime.datetime(2026, 10, 1, 4, 0))
    _position(env, market.l2, "GC-%s" % TAG, 2, 2, last=now - datetime.timedelta(days=5))

    pack = m12.seller_stock(env)
    assert pack["cols"] == [
        "seller",
        "listing",
        "sku",
        "part",
        "on_hand",
        "reserved",
        "available",
        "last_update",
        "age_days",
        "source",
        "stale",
    ]
    _labels_cover(pack)
    assert pack["labels"]["available"] == "Available"
    assert not any("declared gap" in n for n in pack["notes"])

    a = _sku_row(pack, "GA-%s" % TAG)
    assert (a["seller"], a["listing"]) == (market.s1.name, market.l1.name)
    assert (a["on_hand"], a["reserved"], a["available"]) == (10.0, 3.0, 7.0)
    assert a["age_days"] == 0 and a["stale"] == "✗"
    assert a["source"] == "Operator"

    b = _sku_row(pack, "GB-%s" % TAG)
    assert b["last_update"] == "2026-10-01 10:00"  # 04:00 UTC on the Dhaka wall clock
    assert b["age_days"] >= 30 and b["stale"] == "✓"

    c = _sku_row(pack, "GC-%s" % TAG)
    assert (c["seller"], c["available"]) == (market.s2.name, 0.0)
    assert c["age_days"] == 5 and c["stale"] == "✗"

    # the threshold is the report's parameter (the screen's filter sends a string)
    tight = m12.seller_stock(env, stale_days="3")
    assert _sku_row(tight, "GC-%s" % TAG)["stale"] == "✓"
    assert any("3 days" in n for n in tight["notes"])
    assert pack["filters"][0]["key"] == "stale_days"
    assert pack["filters"][0]["options"][0] == "30"

    totals = pack["totals"]
    assert totals["seller"] == "Total"
    assert totals["on_hand"] == round(sum(r["on_hand"] for r in pack["rows"]), 2)
    assert totals["stale"] == sum(1 for r in pack["rows"] if r["stale"] == "✓")


def test_seller_stock_names_live_listings_with_no_position(market):
    env = market.env
    market.l2.write({"state": "active"})  # seed-style, as the trusted superuser
    pack = m12.seller_stock(env)
    note = " ".join(pack["notes"])
    assert "no stock position" in note and market.l2.name in note


def test_seller_stock_applies_the_company_fence(market):
    env = market.env
    pos = _position(env, market.l1, "GF-%s" % TAG, 1)
    other = env["res.company"].create({"name": "Gap Stock Co %s" % TAG})
    env.user.write({"company_ids": [Command.unlink(other.id)]})
    _set(env, pos, "company_id", other.id)
    assert not [r for r in m12.seller_stock(env)["rows"] if r["sku"] == "GF-%s" % TAG]


def test_seller_stock_runs_for_a_plain_internal_reader(market):
    env = market.env
    _position(env, market.l1, "GR-%s" % TAG, 4, 1)
    reader = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Gap stock reader %s" % TAG,
                "login": "gap_stock_reader_%s@example.test" % TAG,
                "group_ids": [Command.set([env.ref("base.group_user").id])],
                "tz": "Asia/Dhaka",
            }
        )
    )
    env.flush_all()
    pack = m12.seller_stock(env(user=reader.id))
    assert _sku_row(pack, "GR-%s" % TAG)["available"] == 3.0


def _dhaka_today(env):
    return fields.Date.context_today(env["fix.seller.certification"].with_context(tz="Asia/Dhaka"))


def _standard(env, code, categories=(), months=12):
    return env["fix.seller.standard"].create(
        {
            "name": "Standard %s" % code,
            "code": code,
            "validity_months": months,
            "category_ids": [Command.set(list(categories))],
        }
    )


def _held(env, seller, standard, expires, state="verified"):
    cert = env["fix.seller.certification"].create(
        {
            "seller_id": seller.id,
            "standard_id": standard.id,
            "issued_on": datetime.date(2026, 1, 1),
            "certificate_no": "C-%s-%s" % (standard.code, seller.id),
        }
    )
    cert.write({"expires_on": expires, "state": state})  # seed-style (superuser)
    return cert


def _seller_row(pack, seller):
    hits = [r for r in pack["rows"] if r["seller"] == seller.name]
    assert len(hits) == 1, pack["rows"]
    return hits[0]


def test_seller_standards_are_built_from_seller_certifications(market):
    env = market.env
    today = _dhaka_today(env)
    req_a = _standard(env, "GSA%s" % TAG, market.cat.ids)
    req_b = _standard(env, "GSB%s" % TAG, market.cat.ids)
    extra = _standard(env, "GSC%s" % TAG)
    pend = _standard(env, "GSD%s" % TAG)
    _held(env, market.s1, req_a, today + datetime.timedelta(days=10))
    _held(env, market.s1, extra, today - datetime.timedelta(days=3), state="expired")
    _held(env, market.s1, pend, today + datetime.timedelta(days=300), state="submitted")
    _held(env, market.s2, extra, today + datetime.timedelta(days=200))

    pack = m12.seller_standards(env)
    assert pack["cols"] == [
        "seller",
        "tier",
        "held",
        "expiring",
        "expired",
        "missing",
        "pending",
        "status",
    ]
    _labels_cover(pack)
    assert not any("declared gap" in n for n in pack["notes"])

    one = _seller_row(pack, market.s1)
    assert req_a.code in one["held"]  # expiring is still held
    assert req_a.code in one["expiring"]
    assert extra.code in one["expired"] and extra.code not in one["held"]
    assert req_b.code in one["missing"] and req_a.code not in one["missing"]
    assert pend.code in one["pending"]
    assert one["status"] == "Missing required"

    two = _seller_row(pack, market.s2)
    assert extra.code in two["held"]
    assert two["missing"] == "—" and two["expiring"] == "—"
    assert two["status"] == "OK"

    # the expiry window is a parameter
    narrow = m12.seller_standards(env, expiring_days="5")
    assert _seller_row(narrow, market.s1)["expiring"] == "—"


def test_seller_standards_count_a_lapsed_verified_certificate_as_expired(market):
    """A verified certificate past its date the cron has not yet visited is
    not held: the report reads the date, not only the state."""
    env = market.env
    today = _dhaka_today(env)
    req = _standard(env, "GSL%s" % TAG, market.cat.ids)
    _held(env, market.s1, req, today - datetime.timedelta(days=1))
    one = _seller_row(m12.seller_standards(env), market.s1)
    assert req.code in one["expired"] and req.code in one["missing"]
    assert req.code not in one["held"]


def test_the_built_m12_reports_read_as_the_caller():
    import inspect

    for fn in (m12.seller_stock, m12.seller_standards):
        source = inspect.getsource(fn)
        assert "sudo()" not in source
        assert "_company_domain(" in source
    assert "_datetime_to_local(" in inspect.getsource(m12.seller_stock)


@pytest.fixture()
def comarketing(odoo_env):
    env = odoo_env
    if "fix.campaign" not in env or "fix.partner" not in env:
        pytest.skip("cd_campaign / cd_partner not installed")
    x = type("CoMarketing", (), {})()
    x.env = env

    def partner(name):
        rec = env["fix.partner"].create(
            {
                "name": name,
                "partner_id": env["res.partner"].create({"name": name}).id,
                "partner_type": "alliance",
            }
        )
        rec.write({"state": "onboarded"})  # seed-style (superuser)
        return rec

    x.p1 = partner("Gap Alliance One %s" % TAG)
    x.p2 = partner("Gap Alliance Two %s" % TAG)
    x.c1 = env["fix.campaign"].create(
        {"name": "Gap Co-Promo A %s" % TAG, "channel": "social", "budget": 20000.0}
    )
    x.c2 = env["fix.campaign"].create(
        {"name": "Gap Co-Promo B %s" % TAG, "channel": "sms", "budget": 5000.0}
    )
    x.c1.write({"partner_ids": [Command.set((x.p1 | x.p2).ids)]})
    x.c2.write({"partner_ids": [Command.set(x.p1.ids)]})

    def mdf(p, campaign, basis, state):
        rec = env["fix.partner.rebate"].create(
            {
                "name": "Gap MDF %s" % TAG,
                "partner_id": p.id,
                "period": "2026-Q4",
                "basis": basis,
                "rate": 0.1,
                "kind": "mdf",
                "campaign_id": campaign.id,
            }
        )
        rec.write({"state": state})  # seed-style (superuser)
        return rec

    mdf(x.p1, x.c1, 50000.0, "accrued")  # 5,000 accrued
    mdf(x.p1, x.c2, 20000.0, "draft")  # 2,000 planned
    mdf(x.p1, x.c2, 10000.0, "cancelled")  # never counted
    mdf(x.p2, x.c1, 30000.0, "approved")  # 3,000 approved for payout
    mdf(x.p2, x.c1, 10000.0, "paid")  # 1,000 paid

    # Attribution (M35 touch ledger): one customer touched only by C1 converts
    # for a known 12,000; another touched only by C2 converts with no value.
    touch = env["fix.campaign.touch"]
    t0 = datetime.datetime(2026, 11, 2, 4, 0)
    buyer = env["res.partner"].create({"name": "Gap Buyer %s" % TAG})
    lead = env["res.partner"].create({"name": "Gap Lead %s" % TAG})
    touch.create(
        {"campaign_id": x.c1.id, "partner_id": buyer.id, "touch_type": "send", "occurred_at": t0}
    )
    touch.create(
        {
            "campaign_id": x.c1.id,
            "partner_id": buyer.id,
            "touch_type": "conversion",
            "occurred_at": t0 + datetime.timedelta(days=1),
            "value_bdt": 12000.0,
            "value_known": True,
        }
    )
    touch.create(
        {"campaign_id": x.c2.id, "partner_id": lead.id, "touch_type": "send", "occurred_at": t0}
    )
    touch.create(
        {
            "campaign_id": x.c2.id,
            "partner_id": lead.id,
            "touch_type": "conversion",
            "occurred_at": t0 + datetime.timedelta(days=2),
        }
    )
    return x


def _partner_row(pack, partner):
    hits = [r for r in pack["rows"] if r["partner"] == partner.name]
    assert len(hits) == 1, pack["rows"]
    return hits[0]


def test_comarketing_is_built_from_the_campaign_and_mdf_links(comarketing):
    x = comarketing
    pack = m40.comarketing(x.env)
    assert pack["cols"] == [
        "partner",
        "campaigns",
        "mdf_planned",
        "mdf_accrued",
        "mdf_approved",
        "mdf_paid",
        "attributed_conversions",
        "attributed_revenue",
        "revenue_basis",
    ]
    _labels_cover(pack)
    assert not any("declared gap" in n for n in pack["notes"])

    one = _partner_row(pack, x.p1)
    assert x.c1.name in one["campaigns"] and x.c2.name in one["campaigns"]
    assert (one["mdf_planned"], one["mdf_accrued"], one["mdf_approved"], one["mdf_paid"]) == (
        2000.0,
        5000.0,
        0.0,
        0.0,
    )
    # C1's known 12,000 counts; C2's conversion has no value on file and is
    # excluded from revenue, which the basis says
    assert one["attributed_revenue"] == 12000.0
    assert one["attributed_conversions"] == 2.0
    assert one["revenue_basis"].startswith("partial")

    two = _partner_row(pack, x.p2)
    assert two["campaigns"] == x.c1.name
    assert (two["mdf_accrued"], two["mdf_approved"], two["mdf_paid"]) == (0.0, 3000.0, 1000.0)
    assert two["attributed_revenue"] == 12000.0
    assert two["revenue_basis"] == "complete"


def test_comarketing_totals_count_a_shared_campaign_once(comarketing):
    x = comarketing
    pack = m40.comarketing(x.env)
    mine = [r for r in pack["rows"] if r["partner"] in (x.p1.name, x.p2.name)]
    assert len(mine) == 2
    totals = pack["totals"]
    assert totals["partner"] == "Total"
    assert totals["mdf_accrued"] == round(sum(r["mdf_accrued"] for r in pack["rows"]), 2)
    # C1 is co-funded by both partners: its revenue is not added twice
    assert totals["attributed_revenue"] < sum(r["attributed_revenue"] or 0.0 for r in pack["rows"])
    note = " ".join(pack["notes"])
    assert "not a partner share" in note


def test_comarketing_revenue_is_none_without_known_value(comarketing):
    x = comarketing
    lone = x.env["fix.partner"].create(
        {
            "name": "Gap Alliance Three %s" % TAG,
            "partner_id": x.env["res.partner"].create({"name": "Gap A3 %s" % TAG}).id,
            "partner_type": "alliance",
        }
    )
    lone.write({"state": "onboarded"})
    x.c2.write({"partner_ids": [Command.link(lone.id)]})
    row = _partner_row(m40.comarketing(x.env), lone)
    assert row["attributed_revenue"] is None
    assert row["revenue_basis"].startswith("no known value")


def test_comarketing_reads_partners_as_the_caller():
    import inspect

    source = inspect.getsource(m40.comarketing)
    assert "sudo()" not in source
    assert 'env["fix.campaign.touch"].attribute(' in inspect.getsource(m40._campaign_revenue)
