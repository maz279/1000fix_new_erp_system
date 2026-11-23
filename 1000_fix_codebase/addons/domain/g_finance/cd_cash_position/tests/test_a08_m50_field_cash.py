"""A08 B13 — M50-F5 / FR-TRE-017: field technician cash reconciliation.

The audit found no per-technician, per-day reconciliation of the cash a field
technician declares against the M20 receipts issued for that technician's
field collections, and no block on further collection (BRU-TRE-04 covered
riders only). The cases below are the control's acceptance tests:

  (a) declared above receipts beyond tolerance -> variance_open, reason
      mandatory;
  (b) within tolerance -> verified/closed automatically;
  (c) above the escalation threshold -> the shortage is booked as a
      receivable against the technician (rider-COD ledger pattern) and can be
      recovered;
  (d) a prior-day open variance blocks the next declaration, naming
      FR-TRE-017 / BRU-TRE-04;
  (e) the technician cannot verify their own day (SOD-12) and a declared day
      is evidence that cannot be deleted.

Uses the A08 M50 fixture (``c``) and its service-order factory (``so``).
``odoo_env`` rolls back after every test.
"""

# ruff: noqa: F811  (the fixtures are imported and used as parameters)
from datetime import timedelta

import pytest
from odoo.exceptions import AccessError, UserError

from .test_a02r2_service_order_cod import so  # noqa: F401 - fixture
from .test_a08_m50_controls import _user, bal, c  # noqa: F401 - fixture

pytestmark = [pytest.mark.financial]

RECON = "fix.field.cash.reconciliation"
TOLERANCE = "cd_cash_position.field_cash_tolerance"
ESCALATE = "cd_cash_position.field_cash_escalate_above"


def _params(c, tolerance=10.0, escalation=1000.0):
    params = c.env["ir.config_parameter"].sudo()
    params.set_param(TOLERANCE, str(tolerance))
    params.set_param(ESCALATE, str(escalation))


def _technician(c, user=None):
    partner = c.env["res.partner"].create({"name": "B13 Technician Contact %s" % c.n})
    vals = {
        "name": "B13 Technician %s" % c.n,
        "company_id": c.company.id,
        "work_contact_id": partner.id,
    }
    if user:
        vals["user_id"] = user.id
    return c.env["hr.employee"].create(vals)


def _receipt(c, tech, amount, day=None):
    """A confirmed M20 receipt for a field collection by ``tech``.

    The receipt has no technician field: the field link is its
    source_order_id -> fix.service.order.technician_id with settlement_source
    field_collection, which is what the reconciliation reads. The receipt is
    created already confirmed (the reconciliation reads confirmed receipts;
    its GL posting is M20's own concern)."""
    order = c.order()
    order.sudo()._guarded().write(
        {"technician_id": tech.id, "settlement_source": "field_collection"}
    )
    return (
        c.env["fix.ar.receipt"]
        .sudo()
        .create(
            {
                "company_id": c.company.id,
                "operating_unit_id": c.ou.id,
                "branch_id": c.branch.id,
                "customer_id": order.customer_id.id,
                "amount": amount,
                "method": "cash",
                "receipt_date": day or c.today,
                "reference": "B13/%s/%s" % (c.n, amount),
                "source_order_id": order.id,
                "state": "confirmed",
            }
        )
    )


def _recon(c, tech, declared, day=None, user=None):
    return (
        c.env[RECON]
        .with_user(user or c.acct)
        .create(
            {
                "company_id": c.company.id,
                "operating_unit_id": c.ou.id,
                "branch_id": c.branch.id,
                "technician_id": tech.id,
                "reconciliation_date": day or c.today,
                "declared_amount": declared,
            }
        )
    )


# ---------------------------------------------------------------- (a) reason
def test_a_declared_above_receipts_beyond_tolerance_needs_a_reason(so):
    c = so
    _params(c, tolerance=10.0, escalation=1000.0)
    tech = _technician(c)
    _receipt(c, tech, 1000.0)
    rec = _recon(c, tech, 1200.0)
    assert rec.receipts_preview_amount == 1000.0
    assert rec.variance_preview == 200.0

    with pytest.raises(UserError, match="FR-TRE-017"):
        rec.action_declare()
    assert rec.state == "draft"

    rec.action_declare(reason="Customer paid BDT 200 for a part not on the receipt")
    assert rec.state == "variance_open"
    assert rec.receipts_amount == 1000.0
    assert rec.variance == 200.0
    assert rec.variance_tier == "open"
    assert rec.tolerance_amount == 10.0 and rec.escalation_amount == 1000.0
    assert not rec.shortfall_move_id
    assert rec.recovery_state == "none"


# ---------------------------------------------------------------- (b) tolerance
def test_b_within_tolerance_closes_automatically(so):
    c = so
    _params(c, tolerance=10.0, escalation=1000.0)
    tech = _technician(c)
    _receipt(c, tech, 1000.0)
    rec = _recon(c, tech, 1005.0)

    rec.action_declare()
    assert rec.state == "verified"
    assert rec.auto_verified
    assert rec.variance == 5.0 and rec.variance_tier == "none"
    assert rec.verified_at and not rec.verified_by_id


# ---------------------------------------------------------------- (c) escalation
def test_c_above_escalation_books_the_shortfall_and_recovers_it(so):
    c = so
    _params(c, tolerance=10.0, escalation=100.0)
    tech = _technician(c)
    _receipt(c, tech, 1000.0)
    rec = _recon(c, tech, 400.0)

    rec.action_declare(reason="Cash bag lost between the customer and the branch")
    assert rec.state == "variance_open"
    assert rec.variance == -600.0 and rec.variance_tier == "escalated"
    assert rec.recovery_state == "open" and rec.shortfall_amount == 600.0
    assert rec.shortfall_move_id.state == "posted"

    # the shortage is a receivable against the technician, and the drawer cash
    # the field receipts debited is relieved
    assert bal(c, c.acc["rider_shortage"]) == 600.0
    assert bal(c, c.acc["branch_cash"]) == -600.0
    short_line = rec.shortfall_move_id.line_ids.filtered(
        lambda line: line.account_id == c.acc["rider_shortage"]
    )
    assert short_line.partner_id == tech.work_contact_id
    assert short_line.debit == 600.0

    # finance verifies, then a different finance admin clears it by repayment
    rec.with_user(c.mgr).action_verify()
    assert rec.verified_by_id == c.mgr
    rec.with_user(c.mgr2).action_clear_variance(
        reference="B13/PAY/1", method="cash", journal_id=c.bank.id
    )
    assert rec.state == "recovered" and rec.recovery_state == "recovered"
    assert rec.recovery_move_id.state == "posted"
    assert bal(c, c.acc["rider_shortage"]) == 0.0
    assert bal(c, c.bank_acc) == 600.0


# ---------------------------------------------------------------- (d) block
def test_d_prior_open_variance_blocks_the_next_declaration(so):
    c = so
    _params(c, tolerance=10.0, escalation=10000.0)
    tech = _technician(c)
    yesterday = c.today - timedelta(days=1)

    _receipt(c, tech, 1000.0, day=yesterday)
    prior = _recon(c, tech, 500.0, day=yesterday)
    prior.action_declare(reason="Under investigation with the branch cashier")
    assert prior.state == "variance_open"

    _receipt(c, tech, 500.0, day=c.today)
    today = _recon(c, tech, 500.0)
    with pytest.raises(UserError, match="FR-TRE-017") as err:
        today.action_declare()
    message = str(err.value)
    assert "BRU-TRE-04" in message
    assert prior.name in message
    assert today.state == "draft"

    # the public block M02 / M20 asks before accepting another collection
    Recon = c.env[RECON]
    assert Recon._fix_technician_has_open_variance(tech, before_day=c.today)
    assert not Recon._fix_technician_has_open_variance(tech, before_day=yesterday)


# ---------------------------------------------------------------- (e) SoD / evidence
def test_e_self_verification_is_refused_and_evidence_cannot_be_deleted(so):
    c = so
    _params(c, tolerance=10.0, escalation=10000.0)
    tech_user = _user(
        c.env,
        "b13_techmgr%s" % c.n,
        ["account.group_account_manager", "cd_cash_position.group_field_cash_technician"],
    )
    tech = _technician(c, user=tech_user)
    _receipt(c, tech, 1000.0)
    rec = _recon(c, tech, 500.0, user=tech_user)
    line = (
        c.env["fix.field.cash.reconciliation.line"]
        .with_user(tech_user)
        .create(
            {
                "reconciliation_id": rec.id,
                "reference": "QUOTED/1",
                "amount": 100.0,
                "note": "Paper receipt quoted by the technician",
            }
        )
    )

    rec.with_user(tech_user).action_declare(reason="Paper receipt not in M20")
    assert rec.state == "variance_open"
    assert rec.receipts_amount == 1100.0

    # the technician also holds a finance role, but still cannot verify their
    # own day
    with pytest.raises(UserError, match="Segregation"):
        rec.with_user(tech_user).action_verify()
    rec.with_user(c.mgr).action_verify()
    assert rec.verified_by_id == c.mgr

    with pytest.raises(UserError, match="evidence"):
        rec.with_user(c.mgr).unlink()
    with pytest.raises(UserError, match="evidence"):
        line.with_user(c.mgr).unlink()


# ---------------------------------------------------------------- ACL / own
def test_f_a_technician_sees_and_creates_only_their_own_day(so):
    c = so
    _params(c, tolerance=10.0, escalation=1000.0)
    tech_user = _user(
        c.env,
        "b13_tech%s" % c.n,
        ["cd_cash_position.group_field_cash_technician"],
    )
    tech = _technician(c, user=tech_user)
    other = _technician(c)

    own = _recon(c, tech, 100.0, user=tech_user)
    foreign = _recon(c, other, 200.0, user=c.acct)

    visible = c.env[RECON].with_user(tech_user).search([])
    assert own in visible and foreign not in visible
    with pytest.raises((AccessError, UserError)):
        c.env[RECON].with_user(tech_user).create(
            {
                "company_id": c.company.id,
                "operating_unit_id": c.ou.id,
                "technician_id": other.id,
                "reconciliation_date": c.today,
                "declared_amount": 50.0,
            }
        )
