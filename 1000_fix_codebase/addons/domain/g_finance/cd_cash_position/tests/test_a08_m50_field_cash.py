"""A08 B13 rework — M50-F5 / FR-TRE-017 on M02's existing field-cash register.

M02's ``fix.field.cash.recon`` (FR-FSM-056 / BRU-FSM-07) is the one
per-technician per-day register. This suite exercises the treasury controls
added to it from cd_cash_position:

  (a) counted above receipts beyond tolerance -> submitting needs a reason;
  (b) within tolerance -> submit / confirm proceed and the state is clear;
  (c) above the escalation threshold -> Dr rider_shortage / Cr branch_cash,
      then action_clear_variance recovers it;
  (d) a prior-day open variance blocks the next submit (FR-TRE-017 /
      BRU-TRE-04);
  (e) self-confirm is refused (the M02 BRU-FSM-07 rule);
  (f) receipts_amount ties out to a real fix.ar.receipt plus quoted refs.

M02 computes its own job figures in ``_fix_measure``; the tests patch it to
return the counted amount as the job figure so the M02 variance is zero and
the FR-TRE-017 receipts variance is the only one exercised. The register is
created and submitted through its normal flow (dispatcher / technician), and
confirmed by a finance manager.
"""

# ruff: noqa: F811  (the fixtures are imported and used as parameters)
from datetime import timedelta

import pytest
from odoo.exceptions import AccessError, UserError

from .test_a02r2_service_order_cod import so  # noqa: F401 - fixture
from .test_a08_m50_controls import _user, bal, c  # noqa: F401 - fixture

pytestmark = [pytest.mark.financial]

RECON = "fix.field.cash.recon"
TOLERANCE = "cd_cash_position.field_cash_tolerance"
ESCALATE = "cd_cash_position.field_cash_escalate_above"
DISPATCHER = "cd_field_service.group_fix_field_service_manager"


@pytest.fixture
def zero_job_variance(c, monkeypatch):
    """M02's job figures return the counted amount as still outstanding, so
    the M02 variance is zero; the receipts variance is what the test drives."""
    Model = type(c.env[RECON])

    def _measure(self):
        return {
            "order_count": 0,
            "cash_collected": 0.0,
            "cash_handed_over": 0.0,
            "cash_outstanding": self.counted_amount or 0.0,
            "order_refs": False,
        }

    monkeypatch.setattr(Model, "_fix_measure", _measure)
    return _measure


def _params(c, tolerance=10.0, escalation=1000.0):
    params = c.env["ir.config_parameter"].sudo()
    params.set_param(TOLERANCE, str(tolerance))
    params.set_param(ESCALATE, str(escalation))


def _dispatcher(c):
    if not hasattr(c, "b13_dispatcher"):
        c.b13_dispatcher = _user(c.env, "b13_disp%s" % c.n, [DISPATCHER])
    return c.b13_dispatcher


def _technician(c, user=None):
    partner = c.env["res.partner"].create({"name": "B13 Technician Contact %s" % c.n})
    vals = {
        "name": "B13 Technician %s" % c.n,
        "company_id": c.company.id,
        "work_contact_id": partner.id,
    }
    if "operating_unit_id" in c.env["hr.employee"]._fields:
        vals["operating_unit_id"] = c.ou.id
    if user:
        vals["user_id"] = user.id
    return c.env["hr.employee"].create(vals)


def _receipt(c, tech, amount, day=None, linked=True):
    """A confirmed cash M20 receipt. Linked: the field-collection link
    source_order_id -> fix.service.order.technician_id with
    settlement_source field_collection. Unlinked: a receipt the technician
    must quote (no source order)."""
    if linked:
        order = c.order()
        order.sudo()._guarded().write(
            {"technician_id": tech.id, "settlement_source": "field_collection"}
        )
        source_order_id = order.id
        customer = order.customer_id
    else:
        source_order_id = False
        customer = c.customer
    return (
        c.env["fix.ar.receipt"]
        .sudo()
        .create(
            {
                "company_id": c.company.id,
                "operating_unit_id": c.ou.id,
                "branch_id": c.branch.id,
                "customer_id": customer.id,
                "amount": amount,
                "method": "cash",
                "receipt_date": day or c.today,
                "reference": "B13/%s/%s/%s" % (c.n, amount, linked),
                "source_order_id": source_order_id,
                "state": "confirmed",
            }
        )
    )


def _recon(
    c,
    tech,
    counted,
    day=None,
    user=None,
    reason=None,
    quoted=None,
    quoted_amount=0.0,
    quoted_refs=None,
):
    vals = {
        "employee_id": tech.id,
        "recon_date": day or c.today,
        "counted_amount": counted,
    }
    if reason:
        vals["variance_reason"] = reason
    if quoted:
        vals["quoted_receipt_ids"] = [(6, 0, [receipt.id for receipt in quoted])]
    if quoted_amount:
        vals["quoted_receipt_amount"] = quoted_amount
    if quoted_refs:
        vals["quoted_receipt_refs"] = quoted_refs
    return c.env[RECON].with_user(user or _dispatcher(c)).create(vals)


def _submit(c, rec, user=None, reason=None):
    user = user or _dispatcher(c)
    if reason and not rec.variance_reason:
        rec.with_user(user).write({"variance_reason": reason})
    rec.with_user(user).action_submit()


def _confirm(c, rec, user=None):
    rec.with_user(user or c.mgr).action_confirm()


def _clear(c, rec, user=None, reference="B13/CLEAR", method="none", journal_id=None):
    rec.with_user(user or c.mgr2).action_clear_variance(
        reference=reference, method=method, journal_id=journal_id
    )


# ---------------------------------------------------------------- (a) reason
def test_a_above_tolerance_needs_a_reason(so, zero_job_variance):
    c = so
    _params(c, tolerance=10.0, escalation=1000.0)
    tech = _technician(c)
    _receipt(c, tech, 1000.0)
    rec = _recon(c, tech, 1200.0)
    assert rec.receipts_amount == 1000.0
    assert rec.receipts_variance == 200.0

    with pytest.raises(UserError, match="FR-TRE-017"):
        _submit(c, rec)
    assert rec.state == "draft"

    _submit(c, rec, reason="Customer paid BDT 200 for a part not on the receipt")
    assert rec.state == "submitted"
    assert rec.receipts_variance == 200.0
    assert rec.variance_state == "open"


# ---------------------------------------------------------------- (b) tolerance
def test_b_within_tolerance_confirms(so, zero_job_variance):
    c = so
    _params(c, tolerance=10.0, escalation=1000.0)
    tech = _technician(c)
    _receipt(c, tech, 1000.0)
    rec = _recon(c, tech, 1005.0)

    _submit(c, rec)
    assert rec.state == "submitted"
    assert rec.receipts_variance == 5.0
    assert rec.variance_state == "clear"

    _confirm(c, rec)
    assert rec.state == "confirmed"
    assert rec.variance_state == "clear"


# ---------------------------------------------------------------- (c) escalation
def test_c_above_escalation_books_the_shortfall_and_recovers_it(so, zero_job_variance):
    c = so
    _params(c, tolerance=10.0, escalation=100.0)
    tech = _technician(c)
    _receipt(c, tech, 1000.0)
    rec = _recon(c, tech, 400.0, reason="Cash bag lost between customer and branch")

    _submit(c, rec)
    assert rec.state == "submitted"
    assert rec.receipts_variance == -600.0 and rec.variance_state == "open"

    _confirm(c, rec)
    assert rec.state == "confirmed"
    assert rec.shortfall_amount == 600.0
    assert rec.shortfall_move_id.state == "posted"
    assert rec.shortage_booked and rec.variance_state == "open"
    assert bal(c, c.acc["rider_shortage"]) == 600.0
    assert bal(c, c.acc["branch_cash"]) == -600.0
    short_line = rec.shortfall_move_id.line_ids.filtered(
        lambda line: line.account_id == c.acc["rider_shortage"]
    )
    assert short_line.partner_id == tech.work_contact_id
    assert short_line.debit == 600.0

    _clear(c, rec, user=c.mgr2, reference="B13/PAY/1", method="cash", journal_id=c.bank.id)
    assert rec.variance_state == "recovered"
    assert rec.recovery_move_id.state == "posted"
    assert bal(c, c.acc["rider_shortage"]) == 0.0
    assert bal(c, c.bank_acc) == 600.0


# ---------------------------------------------------------------- (d) block
def test_d_prior_open_variance_blocks_the_next_submit(so, zero_job_variance):
    c = so
    _params(c, tolerance=10.0, escalation=10000.0)
    tech = _technician(c)
    yesterday = c.today - timedelta(days=1)

    _receipt(c, tech, 1000.0, day=yesterday)
    prior = _recon(c, tech, 500.0, day=yesterday, reason="Under investigation")
    _submit(c, prior)
    assert prior.state == "submitted" and prior.variance_state == "open"

    _receipt(c, tech, 500.0, day=c.today)
    today = _recon(c, tech, 500.0)
    with pytest.raises(UserError, match="FR-TRE-017") as err:
        _submit(c, today)
    message = str(err.value)
    assert "BRU-TRE-04" in message
    assert prior.name in message
    assert today.state == "draft"

    Recon = c.env[RECON]
    assert Recon._fix_technician_has_open_variance(tech, before_day=c.today)
    assert not Recon._fix_technician_has_open_variance(tech, before_day=yesterday)


# ---------------------------------------------------------------- (e) self-confirm
def test_e_self_confirm_is_refused(so, zero_job_variance):
    c = so
    _params(c, tolerance=10.0, escalation=1000.0)
    tech_user = _user(c.env, "b13_tech%s" % c.n, [DISPATCHER])
    tech = _technician(c, user=tech_user)
    _receipt(c, tech, 1000.0)
    rec = _recon(c, tech, 1000.0, user=tech_user)

    _submit(c, rec, user=tech_user)
    with pytest.raises(AccessError, match="BRU-FSM-07"):
        _confirm(c, rec, user=tech_user)
    assert rec.state == "submitted"

    _confirm(c, rec, user=c.mgr)
    assert rec.state == "confirmed" and rec.confirmed_by_id == c.mgr


# ---------------------------------------------------------------- (f) tie-out
def test_f_receipts_tie_out_from_real_receipts(so, zero_job_variance):
    c = so
    _params(c, tolerance=10.0, escalation=1000.0)
    tech = _technician(c)
    _receipt(c, tech, 1000.0)
    quoted = _receipt(c, tech, 250.0, linked=False)
    rec = _recon(
        c,
        tech,
        500.0,
        quoted=[quoted],
        quoted_amount=100.0,
        quoted_refs="PAPER/1",
    )
    assert rec.receipts_amount == 1350.0
    assert rec.receipts_variance == -850.0

    other = _technician(c)
    _receipt(c, other, 999.0)
    assert rec._fix_receipts_total() == 1350.0
