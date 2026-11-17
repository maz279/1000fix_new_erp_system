# cd_settlement_ext: M53 capture audit (2026-11-17), the four new records on
# a real database. Every decision runs as a NON-ADMIN user holding the real
# finance role (the users of test_a08_m53_controls' fixture): acct and acct2
# are Accountants, mgr and mgr2 Accounting Administrators, cfo the DOFA
# Tier 4 approver. Arrangement that is not under test is done as superuser
# and says so. Everything rolls back (odoo_env).
from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

from . import test_a08_m53_controls as _base

c = _base.c
as_ = _base.as_
sub = _base.sub
system_row = _base.system_row
inbox_approve = _base.inbox_approve
_commissioned_order = _base._commissioned_order
declare_marketplace_agent = _base.declare_marketplace_agent

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
TODAY = date.today()


# ------------------------------------------------------------------ SSP (page 2)
def _ssp(c, user, **kw):
    vals = {
        "company_id": c.company.id,
        "obligation_type": "amc_service",
        "method": "observable",
        "value": 9000.0,
        "tolerance_pct": 10.0,
        "effective_from": TODAY - timedelta(days=400),
        "basis_ref": "AMC price list 2025",
    }
    vals.update(kw)
    return as_(c, user)["fix.ssp"].create(vals)


def _approved_ssp(c, **kw):
    ssp = _ssp(c, c.acct, **kw)
    ssp.with_user(c.acct).action_submit()
    ssp.with_user(c.mgr).action_approve()
    return ssp


def test_ssp_is_approved_by_another_administrator_then_frozen(c):
    ssp = _ssp(c, c.acct)
    ssp.with_user(c.acct).action_submit()
    with pytest.raises(REFUSED):
        ssp.with_user(c.acct2).action_approve()  # an accountant does not approve
    with pytest.raises(REFUSED):
        ssp.with_user(c.mgr).action_reject(reason="")  # a rejection states why
    ssp.with_user(c.mgr).action_approve()
    assert ssp.state == "active" and ssp.approved_by_id == c.mgr
    with pytest.raises(UserError):
        ssp.with_user(c.mgr).write({"value": 1.0})
    with pytest.raises(UserError):
        ssp.with_user(c.mgr).unlink()
    mine = _ssp(c, c.mgr, obligation_type="parts")
    mine.with_user(c.mgr).action_submit()
    with pytest.raises(UserError):
        mine.with_user(c.mgr).action_approve()  # not the submitter


def test_a_new_ssp_supersedes_the_old_from_its_date(c):
    old = _approved_ssp(c)
    new = _approved_ssp(c, value=9500.0, effective_from=TODAY - timedelta(days=30))
    assert old.state == "superseded" and old.effective_to == TODAY - timedelta(days=31)
    Ssp = c.env["fix.ssp"]
    assert Ssp._in_force(c.company, "amc_service", "standard", TODAY) == new
    assert Ssp._in_force(c.company, "amc_service", "standard", TODAY - timedelta(days=60)) == old
    earlier = _ssp(c, c.acct, effective_from=TODAY - timedelta(days=60))
    earlier.with_user(c.acct).action_submit()
    with pytest.raises(UserError, match="takes effect after it"):
        earlier.with_user(c.mgr).action_approve()


def test_ssp_stamps_cannot_be_typed(c):
    with pytest.raises(UserError):
        _ssp(c, c.acct, state="active")
    ssp = _ssp(c, c.acct)
    with pytest.raises(UserError):
        ssp.with_user(c.acct).write({"approved_by_id": c.mgr.id})
    with pytest.raises(ValidationError):
        _ssp(c, c.acct, value=0.0)
    assert _ssp(c, c.acct, method="residual", value=0.0).state == "draft"


def _bundle(c, amc_ssp, parts_ssp):
    s = sub(c, c.acct, contract_value=10000.0, contract_end_date=TODAY + timedelta(days=300))
    Ob = as_(c, c.acct)["fix.performance.obligation"]
    amc = Ob.create({"subscription_id": s.id, "name": "AMC", "standalone_price": amc_ssp})
    parts = Ob.create(
        {
            "subscription_id": s.id,
            "name": "Parts",
            "obligation_type": "parts",
            "standalone_price": parts_ssp,
        }
    )
    return s, amc, parts


def test_allocation_refuses_a_typed_ssp_outside_the_band(c):
    _approved_ssp(c)  # AMC service 9,000 +/- 10%
    s, amc, parts = _bundle(c, 12000.0, 1000.0)
    with pytest.raises(UserError, match="AUT-REV-03"):
        s.with_user(c.acct).action_allocate_price()
    assert amc.state == "draft" and not amc.allocated_amount
    amc.with_user(c.acct).write({"standalone_price": 9500.0})
    s.with_user(c.acct).action_allocate_price()
    assert amc.ssp_basis == "ssp" and amc.ssp_id.value == 9000.0
    assert parts.ssp_basis == "contract" and not parts.ssp_id  # no parts SSP on file
    assert abs(amc.allocated_amount + parts.allocated_amount - 10000.0) < 0.001
    with pytest.raises(UserError):
        amc.with_user(c.acct).write({"ssp_basis": "contract"})


def test_a_single_obligation_contract_is_not_held_by_the_ssp(c):
    _approved_ssp(c)
    s = sub(c, c.acct, contract_value=20000.0, contract_end_date=TODAY + timedelta(days=300))
    s.with_user(c.acct).action_generate_revrec_schedule()
    assert s.obligation_ids.state == "scheduled"


# ------------------------------------------------------------------ modifications (page 4)
def _scheduled(c, value=12000.0, days_back=60, days_ahead=300):
    """A two-obligation contract, allocated and scheduled, started in the past."""
    start = TODAY - timedelta(days=days_back)
    s = sub(
        c,
        c.acct,
        start_date=start,
        next_invoice_date=start,
        contract_value=value,
        contract_end_date=TODAY + timedelta(days=days_ahead),
    )
    Ob = as_(c, c.acct)["fix.performance.obligation"]
    for name, ssp in (("AMC", 9000.0), ("Priority SLA", 3000.0)):
        Ob.create(
            {
                "subscription_id": s.id,
                "name": name,
                "standalone_price": ssp,
                "start_date": start,
                "end_date": s.contract_end_date,
            }
        )
    s.with_user(c.acct).action_allocate_price()
    s.obligation_ids.with_user(c.acct).action_create_schedule()
    return s


def _mod(c, user, s, **kw):
    vals = {
        "subscription_id": s.id,
        "modification_date": TODAY,
        "nature": "price",
        "treatment": "prospective",
        "new_contract_value": 15000.0,
        "reason": "Customer added two sites",
        "evidence_ref": "Addendum %s" % uuid.uuid4().hex[:4],
    }
    vals.update(kw)
    return as_(c, user)["fix.contract.modification"].create(vals)


def test_prospective_modification_versions_the_schedules(c):
    s = _scheduled(c)
    old = s.obligation_ids.mapped("schedule_id")
    m = _mod(c, c.acct, s)
    assert m.name.startswith("CMOD/")
    m.with_user(c.acct).action_submit()
    with pytest.raises(REFUSED):
        m.with_user(c.acct2).action_approve()  # an accountant does not approve
    m.with_user(c.mgr).action_approve()
    assert m.state == "applied" and m.approved_by_id == c.mgr
    # the old versions are closed and KEPT with what they recognised
    assert set(old.mapped("state")) == {"cancelled"}
    earned = sum(old.mapped("recognized_amount"))
    assert earned > 0 and all(o.line_ids for o in old)
    new = s.obligation_ids.mapped("schedule_id")
    assert not (new & old) and set(new.mapped("state")) == {"active"}
    assert set(new.mapped("source_model")) == {"fix.contract.modification.line"}
    # the remainder of the new price, allocated 3:1 by SSP, exactly
    assert abs(sum(new.mapped("total_amount")) - (15000.0 - earned)) < 0.005
    assert abs(sum(s.obligation_ids.mapped("allocated_amount")) - 15000.0) < 0.005
    assert s.contract_value == 15000.0 and len(m.line_ids) == 2
    # the new version recognises (it is not held, nothing yet elapsed today)
    new.with_user(c.acct).action_recognize_period(as_of=TODAY + timedelta(days=30))
    assert all(n.recognized_amount > 0 for n in new)
    # a released schedule line is still never edited (BRU-REV-04)
    with pytest.raises(UserError):
        old[0].with_user(c.acct).write({"total_amount": 1.0})


def test_the_requester_does_not_approve_and_stamps_are_not_typed(c):
    s = _scheduled(c)
    m = _mod(c, c.mgr, s)
    m.with_user(c.mgr).action_submit()
    with pytest.raises(UserError, match="Segregation"):
        m.with_user(c.mgr).action_approve()
    with pytest.raises(UserError):
        m.with_user(c.mgr2).write({"new_contract_value": 99999.0})  # submitted: frozen
    with pytest.raises(UserError):
        _mod(c, c.acct, s, state="applied")
    m.with_user(c.mgr2).action_reject(reason="Addendum not signed")
    assert m.state == "rejected" and s.contract_value == 12000.0


def test_cumulative_catchup_goes_to_the_cfo_as_a_manual_schedule(c):
    s = _scheduled(c)
    m = _mod(c, c.acct, s, treatment="cumulative_catchup", new_contract_value=18000.0)
    m.with_user(c.acct).action_submit()
    m.with_user(c.mgr).action_approve()
    catch = m.catchup_schedule_id
    assert m.catchup_amount > 0 and catch.state == "draft" and catch.source_model == "manual"
    assert abs(catch.total_amount - m.catchup_amount) < 0.005
    lines = m.line_ids
    assert abs(sum(lines.mapped("catchup_amount")) - m.catchup_amount) < 0.005
    total = sum(
        lines.mapped(lambda ln: ln.recognised_before + ln.catchup_amount + ln.remaining_amount)
    )
    assert abs(total - 18000.0) < 0.01
    # nothing is released before the CFO approves it (BRU-REV-01)
    with pytest.raises(UserError):
        catch.with_user(c.acct).action_recognize_period()
    catch.with_user(c.acct).action_request_cfo_approval()
    inbox_approve(c, catch, c.cfo)
    catch.with_user(c.acct).action_recognize_period()
    assert abs(catch.recognized_amount - m.catchup_amount) < 0.005


def test_modification_guards(c):
    s = _scheduled(c)
    # a price below what is already recognised is a reversal, not a modification
    low = _mod(c, c.acct, s, new_contract_value=100.0)
    low.with_user(c.acct).action_submit()
    with pytest.raises(UserError, match="reversal"):
        low.with_user(c.mgr).action_approve()
    # no revenue is recognised ahead of time
    future = _mod(c, c.acct, s, modification_date=TODAY + timedelta(days=5))
    future.with_user(c.acct).action_submit()
    with pytest.raises(UserError, match="on or after"):
        future.with_user(c.mgr).action_approve()
    # added scope is a separate contract, and only it is
    with pytest.raises(ValidationError):
        _mod(c, c.acct, s, nature="scope")
    with pytest.raises(ValidationError):
        _mod(c, c.acct, s, treatment="separate_contract")
    other = sub(c, c.acct, contract_value=5000.0)
    sep = _mod(
        c,
        c.acct,
        s,
        nature="scope",
        treatment="separate_contract",
        new_contract_value=0.0,
        separate_subscription_id=other.id,
    )
    sep.with_user(c.acct).action_submit()
    sep.with_user(c.mgr).action_approve()
    assert sep.state == "applied" and not sep.line_ids
    # a contract with nothing scheduled changes its price the old way
    fresh = sub(c, c.acct, contract_value=5000.0)
    with pytest.raises(UserError, match="Request Transaction Price"):
        _mod(c, c.acct, fresh).with_user(c.acct).action_submit()


# ------------------------------------------------------------------ principal / agent (page 5)
def _position(c, user, **kw):
    vals = {
        "company_id": c.company.id,
        "arrangement": "marketplace",
        "position": "agent",
        "decision_ref": "D-03 board minute 12",
        "opinion_ref": "Auditor letter 2026/07",
        "effective_from": TODAY - timedelta(days=10),
    }
    vals.update(kw)
    return as_(c, user)["fix.revenue.presentation"].create(vals)


def _marketplace_row(c):
    c.env["fix.commission.scheme"].create(
        {
            "name": "Seller 10%",
            "scheme_type": "seller",
            "commission_rate": 0.10,
            "tds_rate": 0.10,
            "date_from": date(2025, 7, 1),
            "company_id": c.company.id,
        }
    )
    _seller, order = _commissioned_order(c, gross=4000.0)
    out = c.env["fix.a04.finance.consumers"].consume_commission_earned(
        {"aggregate": "fix.marketplace.order", "aggregate_id": order.id, "payload": {}}
    )
    return c.env["fix.commission.ledger"].browse(out["id"])


def test_marketplace_commission_waits_for_the_declared_position(c):
    row = _marketplace_row(c)
    with pytest.raises(UserError, match="BRU-REV-09"):
        row.with_user(c.acct).action_post_to_gl()
    with pytest.raises(UserError, match="BRU-REV-09"):
        row.sudo().action_post_to_gl()  # trusted code is held too
    assert row.state == "earned" and not row.gl_move_id
    p = _position(c, c.acct)
    p.with_user(c.acct).action_submit()
    with pytest.raises(REFUSED):
        p.with_user(c.acct2).action_approve()
    p.with_user(c.mgr).action_approve()
    assert p.state == "active"
    with pytest.raises(UserError):
        p.with_user(c.mgr).write({"position": "principal"})
    row.with_user(c.acct).action_post_to_gl()
    assert row.state == "accrued" and row.gl_move_id


def test_a_principal_declaration_is_refused_by_the_net_ledger(c):
    row = _marketplace_row(c)
    p = _position(c, c.mgr, position="principal")
    p.with_user(c.mgr).action_submit()
    with pytest.raises(UserError, match="Segregation"):
        p.with_user(c.mgr).action_approve()  # not the requester
    p.with_user(c.mgr2).action_approve()
    with pytest.raises(UserError, match="PRINCIPAL"):
        row.with_user(c.acct).action_post_to_gl()
    # a new AGENT declaration supersedes it from its date
    agent = _position(c, c.acct, effective_from=TODAY - timedelta(days=2))
    agent.with_user(c.acct).action_submit()
    agent.with_user(c.mgr).action_approve()
    assert p.state == "superseded" and p.effective_to == TODAY - timedelta(days=3)
    row.with_user(c.acct).action_post_to_gl()
    assert row.state == "accrued"


def test_partner_commission_needs_no_marketplace_position(c):
    _referral, led = _base.accrued_referral(c)
    assert led.state == "accrued"


# ------------------------------------------------------------------ payout holds (pages 7, 8)
def _hold(c, user, **kw):
    vals = {
        "company_id": c.company.id,
        "partner_id": c.payee.id,
        "reason": "quality",
        "note": "Two rework complaints this month",
    }
    vals.update(kw)
    return as_(c, user)["fix.payout.hold"].create(vals)


def test_a_whole_payee_hold_keeps_the_payee_out_of_the_run(c):
    _ref, led = _base.accrued_referral(c)
    h = _hold(c, c.acct)
    assert h.scope == "payee" and h.name.startswith("PHD/")
    h.with_user(c.acct).action_raise()
    assert h.state == "active" and h.raised_by_id == c.acct and h.held_amount > 0
    run = as_(c, c.acct)["fix.payout.run"].create(
        {"period": "2026-10", "company_id": c.company.id, "operating_unit_id": c.ou.id}
    )
    with pytest.raises(UserError, match="No accrued commissions"):
        run.action_collect_accrued()
    # an accountant cannot release it, nor anyone without a reason
    with pytest.raises(REFUSED):
        h.with_user(c.acct2).action_release(reason="ok")
    with pytest.raises(UserError):
        h.with_user(c.mgr).action_release(reason="")
    h.with_user(c.mgr).action_release(reason="Complaints closed with no fault")
    assert h.state == "released" and h.outcome == "resolved" and h.released_by_id == c.mgr
    run.action_collect_accrued()
    assert led in run.commission_ids


def _accrued_for(c, taxable):
    """Proper path for a second referred customer (one commission per customer)."""
    customer = c.env["res.partner"].create({"name": "M53 Referred %s" % uuid.uuid4().hex[:4]})
    inv = _base.paid_invoice(c, taxable, customer=customer)
    r = as_(c, c.acct)["fix.referral"].create(
        {
            "name": "REF-%s" % uuid.uuid4().hex[:6],
            "partner_id": c.fpartner.id,
            "referred_partner_id": customer.id,
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
        }
    )
    r.with_user(c.sales).action_convert(invoice=inv)
    r.with_user(c.sales).action_earn_commission()
    r.with_user(c.acct).action_accrue_commission()
    return r.commission_ledger_id


def test_a_dispute_holds_only_the_disputed_lines(c):
    _r1, led1 = _base.accrued_referral(c, taxable=20000.0)
    led2 = _accrued_for(c, 10000.0)
    with pytest.raises(ValidationError, match="BRU-REV-17"):
        _hold(c, c.acct, reason="settlement_dispute")
    d = _hold(c, c.acct, reason="settlement_dispute", commission_ids=[(6, 0, led1.ids)])
    d.with_user(c.acct).action_raise()
    assert d.scope == "lines" and abs(d.held_amount - led1.net_payable) < 0.005
    run = as_(c, c.acct)["fix.payout.run"].create(
        {"period": "2026-10", "company_id": c.company.id, "operating_unit_id": c.ou.id}
    )
    run.action_collect_accrued()
    assert led2 in run.commission_ids and led1 not in run.commission_ids
    # forcing the disputed line back in is refused at preparation
    run.write({"commission_ids": [(4, led1.id)]})
    with pytest.raises(UserError, match="FR-REV-035"):
        run.action_prepare()
    # a dispute closes with its coded outcome
    with pytest.raises(UserError, match="outcome"):
        d.with_user(c.mgr).action_release(reason="settled")
    d.with_user(c.mgr).action_release(reason="Statement line confirmed", outcome="rejected")
    assert d.outcome == "rejected"


def test_the_raiser_is_not_the_sole_releaser(c):
    h = _hold(c, c.mgr, reason="kyc", note="Trade licence expired")
    h.with_user(c.mgr).action_raise()
    with pytest.raises(UserError, match="Segregation"):
        h.with_user(c.mgr).action_release(reason="Licence renewed")
    h.with_user(c.mgr2).action_release(reason="Licence renewed")
    assert h.state == "released"


def test_hold_guards(c):
    _ref, led = _base.accrued_referral(c)
    other = c.env["fix.commission.ledger"].browse(
        system_row(c, 5000.0, 0.05, payee=c.payee2, post=False).id
    )
    with pytest.raises(ValidationError):
        _hold(c, c.acct, commission_ids=[(6, 0, other.ids)])  # another payee's line
    h = _hold(c, c.acct)
    with pytest.raises(UserError):
        h.with_user(c.acct).write({"state": "active"})
    with pytest.raises(REFUSED):
        h.with_user(c.plain).action_raise()
    h.with_user(c.acct).action_raise()
    with pytest.raises(UserError):
        h.with_user(c.acct).write({"note": "rewritten"})
    with pytest.raises(UserError):
        h.with_user(c.acct).unlink()
    assert led.state == "accrued"
