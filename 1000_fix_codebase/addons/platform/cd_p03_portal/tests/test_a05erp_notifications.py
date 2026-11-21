"""A05 ERP audit XC-20 / M13-26 (20 Nov 2026): the customer hears of the A05
milestones - a rental due back, a rental overdue on the 1st, 3rd and 7th day,
a trade-in offer with its expiry, a trade-in payout - by SMS (and e-mail when
they have an address), in their language, once per event.

The payloads are interface I5's (S1 / S2 publish them); the consumers run as
the relay does (superuser) and queue through fix.notif.delivery.queue().
"""

import itertools
from datetime import timedelta

import pytest
from odoo.addons.cd_p03_portal.controllers.a05.m13 import dhaka_today
from odoo.addons.cd_p03_portal.tests import a05erp_helpers
from odoo.exceptions import AccessError

_SEQ = itertools.count(1)
A05_EVENTS = ("rental.return_due", "rental.overdue", "tradein.offer_issued", "tradein.paid")


def _branch(env):
    return a05erp_helpers.branch(env)


@pytest.fixture
def n(odoo_env):
    env = odoo_env
    for model in ("fix.rental.reservation", "fix.tradein.request", "fix.notif.delivery"):
        if model not in env:
            pytest.skip("%s not installed" % model)
    i = next(_SEQ)
    branch = _branch(env)
    customer = env["res.partner"].create(
        {
            "name": "A05ERP Notify Customer %d" % i,
            "phone": "0171100%04d" % i,
            "email": "a05erp.notify.%d@example.com" % i,
            "preferred_language": "bn",
        }
    )
    tmpl = env["product.template"].create({"name": "A05ERP Notify Projector %d" % i})
    item = env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
    sku = env["fix.rental.sku"].create(
        {"catalogue_item_id": item.id, "daily_rate": 1000, "security_deposit": 5000}
    )
    today = dhaka_today(env)
    res = env["fix.rental.reservation"].create(
        {
            "customer_id": customer.id,
            "rental_sku_id": sku.id,
            "operating_unit_id": branch.operating_unit_id.id,
            "branch_id": branch.id,
            "date_from": today - timedelta(days=5),
            "date_to": today - timedelta(days=1),
        }
    )
    env.cr.execute("UPDATE fix_rental_reservation SET state = 'active' WHERE id = %s", [res.id])
    res.invalidate_recordset(["state"])
    tradein = env["fix.tradein.request"].create(
        {
            "customer_id": customer.id,
            "offered_value": 12000,
            "operating_unit_id": branch.operating_unit_id.id,
        }
    )
    return type("N", (), {"env": env, "customer": customer, "res": res, "tradein": tradein})


def _rows(env, record):
    return (
        env["fix.notif.delivery"]
        .sudo()
        .search([("source_model", "=", record._name), ("source_id", "=", record.id)])
    )


def test_the_four_a05_consumers_are_registered_and_active(odoo_env):
    consumers = (
        odoo_env["fix.event.consumer"]
        .sudo()
        .search([("event_type", "in", A05_EVENTS), ("model", "=", "fix.notif.delivery")])
    )
    assert sorted(consumers.mapped("event_type")) == sorted(A05_EVENTS)
    assert all(consumers.mapped("active"))
    for tmpl in (
        "rental_return_due",
        "rental_overdue",
        "tradein_offer",
        "tradein_paid",
    ):
        for channel in ("sms", "email"):
            rec = odoo_env.ref("cd_contact_centre.notif_tmpl_a05_%s_%s" % (tmpl, channel))
            assert rec.channel == channel and rec.consent_class == "transactional"
            assert rec.body_bn and rec.body, "a Bengali and an English body (DE-17)"


def test_return_due_reaches_the_customer_in_bengali_by_sms_and_email_once(n):
    Delivery = n.env["fix.notif.delivery"]
    event = {
        "event_id": "a05erp-due-1",
        "payload": {
            "reservation_id": n.res.id,
            "partner_id": n.customer.id,
            "due_at": str(n.res.date_to),
        },
    }
    out = Delivery.consume_rental_return_due(event)
    assert out["queued"], out
    rows = _rows(n.env, n.res)
    assert sorted(rows.mapped("channel")) == ["email", "sms"]
    sms = rows.filtered(lambda r: r.channel == "sms")
    assert n.res.name in sms.body and "ফেরত" in sms.body, sms.body
    assert (sms.purpose, sms.lawful_basis) == ("service_updates", "contract")
    # the relay redelivers: one event, one message per channel
    Delivery.consume_rental_return_due(dict(event, event_id="a05erp-due-1b"))
    assert len(_rows(n.env, n.res)) == 2


def test_overdue_reminders_go_on_days_1_3_and_7_only(n):
    Delivery = n.env["fix.notif.delivery"]
    sent = []
    for day in range(1, 9):
        out = Delivery.consume_rental_overdue(
            {
                "event_id": "a05erp-over-%d" % day,
                "payload": {
                    "reservation_id": n.res.id,
                    "partner_id": n.customer.id,
                    "days_overdue": day,
                },
            }
        )
        if out.get("queued"):
            sent.append(day)
    assert sent == [1, 3, 7]
    sms = _rows(n.env, n.res).filtered(lambda r: r.channel == "sms")
    assert len(sms) == 3
    assert any("7" in body for body in sms.mapped("body"))


def test_a_returned_rental_is_not_chased(n):
    n.env.cr.execute(
        "UPDATE fix_rental_reservation SET state = 'returned' WHERE id = %s", [n.res.id]
    )
    n.res.invalidate_recordset(["state"])
    out = n.env["fix.notif.delivery"].consume_rental_overdue(
        {"event_id": "a05erp-over-x", "payload": {"reservation_id": n.res.id, "days_overdue": 1}}
    )
    assert out == {"queued": False, "reason": "the rental is not out"}
    assert not _rows(n.env, n.res)


def test_tradein_offer_and_payout_reach_the_seller(n):
    Delivery = n.env["fix.notif.delivery"]
    out = Delivery.consume_tradein_offer_issued(
        {
            "event_id": "a05erp-offer-1",
            "payload": {
                "tradein_id": n.tradein.id,
                "partner_id": n.customer.id,
                "amount": 12000,
                "valid_until": "2026-11-27",
            },
        }
    )
    assert out["queued"], out
    out = Delivery.consume_tradein_paid(
        {
            "event_id": "a05erp-paid-1",
            "payload": {"tradein_id": n.tradein.id, "partner_id": n.customer.id, "amount": 11500},
        }
    )
    assert out["queued"], out
    sms = _rows(n.env, n.tradein).filtered(lambda r: r.channel == "sms")
    bodies = " ".join(sms.mapped("body"))
    assert "12,000.00" in bodies and "2026-11-27" in bodies
    assert "11,500.00" in bodies
    # an e-mail too, in Bengali (the customer's language)
    mails = _rows(n.env, n.tradein).filtered(lambda r: r.channel == "email")
    assert len(mails) == 2 and all(m.language == "bn" for m in mails)


def test_a_customer_without_an_email_gets_the_sms_only(n):
    n.customer.email = False
    out = n.env["fix.notif.delivery"].consume_tradein_paid(
        {"event_id": "a05erp-paid-2", "payload": {"tradein_id": n.tradein.id, "amount": 100}}
    )
    assert out["queued"], out
    assert _rows(n.env, n.tradein).mapped("channel") == ["sms"]


def test_only_the_relay_may_call_the_consumers(n):
    user = (
        n.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A05ERP Notify Clerk",
                "login": "a05erp.notify.clerk.%d@a05.test" % next(_SEQ),
                "group_ids": [(6, 0, [n.env.ref("base.group_user").id])],
            }
        )
    )
    with pytest.raises(AccessError):
        n.env["fix.notif.delivery"].with_user(user).consume_tradein_paid(
            {"event_id": "x", "payload": {"tradein_id": n.tradein.id}}
        )
