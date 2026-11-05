"""A04 hand-off closure (2026-11-05): an encashed tender bond reaches the GL.

working/A04_Workflow_and_Approval_Report.md §7.10 left "tender-bond
encashment GL (treasury workstream)" open: the DOFA-routed claim decision
records that the procuring entity encashed the bank guarantee, and nothing
carried the loss to the books.

The source event is produced by the real bond chain (activate -> claim ->
the DOFA decision from the M63 inbox), then delivered the way production
delivers it: ``cron_relay()`` as the superuser with this module's consumer
isolated on. The consumer posts Dr guarantee encashment loss / Cr outgoing
clearing from the treasury account roles (fail closed on a missing account),
re-reads the bond (state "claimed", amount from the record) and is idempotent
per bond. ``odoo_env`` rolls back after each test.
"""

import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
EVENT = "tender_bond.claimed"
LOSS_ROLE = "cd_cash_position.account_code.bond_encashment_loss"
CLEARING_ROLE = "cd_cash_position.account_code.outgoing_clearing"


@pytest.fixture
def w(odoo_env):
    env = odoo_env

    def tier(n):
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "A4 bond tier %d" % n,
                    "login": "a4bond.t%d@a04.test" % n,
                    "group_ids": [
                        (
                            6,
                            0,
                            [
                                env.ref("base.group_user").id,
                                env.ref("cd_entity_config.group_dofa_tier_%d" % n).id,
                            ],
                        )
                    ],
                }
            )
        )

    x = types.SimpleNamespace(env=env)
    x.tiers = {n: tier(n) for n in (1, 2, 3, 4)}
    x.agency = env["res.partner"].create({"name": "A4 Bond Procuring Entity"})
    x.ou = env["operating.unit"].search([], limit=1)
    x.today = fields.Date.context_today(env["fix.tender.bond"])
    # the treasury roles the consumer resolves (any two real accounts; the
    # consumer must never guess an account itself)
    accounts = (
        env["account.account"].sudo().search([("company_ids", "in", env.company.id)], limit=2)
    )
    assert len(accounts) == 2, "the company chart has no accounts to configure"
    env["ir.config_parameter"].sudo().set_param(LOSS_ROLE, accounts[0].code)
    env["ir.config_parameter"].sudo().set_param(CLEARING_ROLE, accounts[1].code)
    x.loss_account, x.clearing_account = accounts[0], accounts[1]
    return x


def _bond(w, amount=20000.0):
    """A real active bond on a submitted tender (PPR r.25 band respected)."""
    env = w.env
    tender = env["fix.tender"].create(
        {
            "name": "A4 C7 Bond Tender",
            "client_name": "BD Ministry",
            "client_id": w.agency.id,
            "operating_unit_id": w.ou.id,
            "estimated_value": 750000.0,
            "bid_value": 700000.0,
            "due_date": w.today + timedelta(days=10),
            "score_fit": 4,
            "score_capacity": 4,
            "score_competition": 3,
            "score_margin": 3,
            "score_risk": 2,
            "requirement_ids": [
                (
                    0,
                    0,
                    {"requirement": "Trade licence", "state": "complied", "evidence_ref": "TL-1"},
                )
            ],
        }
    )
    bond = env["fix.tender.bond"].create(
        {
            "tender_id": tender.id,
            "bond_type": "bid",
            "amount": amount,
            "bank": "Sonali Bank",
            "guarantee_no": "BG-A4C7",
            "expires_on": w.today + timedelta(days=120),
        }
    )
    bond.action_activate()
    assert bond.state == "active"
    return bond


def _claimed(w, bond):
    """The DOFA-routed claim decision, run from the M63 inbox."""
    bond.action_claim(reason="bid security forfeited (PPR r.25)")
    assert bond.approval_state == "pending"
    tasks = bond.approval_request_id.task_ids.filtered(lambda t: t.state == "pending")
    assert tasks, "the claim request reached no inbox"
    approver = tasks[0].assigned_user_id
    tasks[0].with_user(approver).action_approve(comment="bank debit advice seen")
    bond.invalidate_recordset()
    assert bond.state == "claimed" and bond.claimed_by == approver
    return bond


def _relay(w):
    Consumer = w.env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "=", EVENT)])
    assert len(mine) == 1 and mine.model == "fix.a04.bond.consumers"
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": w.env.cr.now() - timedelta(minutes=1)})
    w.env["fix.event.outbox"].cron_relay()
    w.env.invalidate_all()


def _bond_move(w, bond):
    return (
        w.env["account.move"]
        .sudo()
        .search(
            [
                ("ref", "=", "BOND-ENCASH-%s" % bond.name),
                ("company_id", "=", bond.tender_id.company_id.id),
            ],
            limit=1,
        )
    )


def test_the_encashment_posts_its_loss_to_the_gl(w):
    bond = _claimed(w, _bond(w))
    _relay(w)
    move = _bond_move(w, bond)
    assert move and move.state == "posted", "the claimed bond produced no GL move"
    lines = {(ln.account_id.id, round(ln.debit, 2), round(ln.credit, 2)) for ln in move.line_ids}
    assert (w.loss_account.id, 20000.0, 0.0) in lines
    assert (w.clearing_account.id, 0.0, 20000.0) in lines
    assert round(sum(ln.debit for ln in move.line_ids), 2) == round(
        sum(ln.credit for ln in move.line_ids), 2
    )


def test_relaying_twice_posts_one_move(w):
    bond = _claimed(w, _bond(w))
    _relay(w)
    _relay(w)
    moves = (
        w.env["account.move"]
        .sudo()
        .search(
            [
                ("ref", "=", "BOND-ENCASH-%s" % bond.name),
                ("company_id", "=", bond.tender_id.company_id.id),
            ]
        )
    )
    assert len(moves) == 1


def _delivery_error(w):
    """The last delivery attempt's error text for this consumer (the relay
    records a failed fix.event.consumer.delivery instead of raising)."""
    sub = w.env["fix.event.consumer"].sudo().search([("event_type", "=", EVENT)], limit=1)
    Delivery = w.env["fix.event.consumer.delivery"].sudo()
    row = Delivery.search([("subscription_id", "=", sub.id)], order="id desc", limit=1)
    return (row.state, row.last_error or "")


def test_a_forged_payload_amount_is_refused(w):
    bond = _claimed(w, _bond(w))
    outbox = w.env["fix.event.outbox"].sudo()
    row = outbox.search(
        [
            ("event_type", "=", EVENT),
            ("aggregate", "=", "fix.tender.bond"),
            ("aggregate_id", "=", bond.id),
        ],
        limit=1,
    )
    assert row, "the claim published no event"
    import json

    payload = json.loads(row.payload)
    payload["amount"] = 999999.0
    row.payload = json.dumps(payload)
    _relay(w)
    state, error = _delivery_error(w)
    assert state == "failed" and "says BDT" in error, (state, error)
    assert not _bond_move(w, bond)


def test_a_bond_that_is_not_claimed_is_refused(w):
    bond = _bond(w)  # active, never claimed: no event yet — forge one
    w.env["fix.event.outbox"].sudo().create(
        {
            "event_type": EVENT,
            "aggregate": "fix.tender.bond",
            "aggregate_id": bond.id,
            "payload": '{"bond": "%s", "amount": 20000.0}' % bond.name,
        }
    )
    _relay(w)
    state, error = _delivery_error(w)
    assert state == "failed" and "not claimed" in error, (state, error)


def test_a_missing_account_refuses_with_the_parameter(w):
    w.env["ir.config_parameter"].sudo().set_param(LOSS_ROLE, False)
    bond = _claimed(w, _bond(w))
    _relay(w)
    state, error = _delivery_error(w)
    assert state == "failed" and "bond_encashment_loss" in error, (state, error)
    assert not _bond_move(w, bond)


def test_the_consumer_runs_only_from_the_relay(w):
    bond = _claimed(w, _bond(w))
    clerk = (
        w.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A4 bond clerk",
                "login": "a4bond.clerk@a04.test",
                "group_ids": [(6, 0, [w.env.ref("base.group_user").id])],
            }
        )
    )
    event = {
        "aggregate": "fix.tender.bond",
        "aggregate_id": bond.id,
        "payload": '{"amount": 20000.0}',
    }
    with pytest.raises(AccessError, match="relay"), w.env.cr.savepoint():
        w.env["fix.a04.bond.consumers"].with_user(clerk).consume_tender_bond_claimed(event)
