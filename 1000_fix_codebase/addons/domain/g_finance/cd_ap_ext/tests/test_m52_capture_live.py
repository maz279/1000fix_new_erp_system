# cd_ap_ext: M52 capture audit (2026-11-17), the new AP records on a real
# database. Every decision runs as a NON-ADMIN user holding the real finance
# role (the users of test_a08_m52_controls' fixture): acc1/acc2/acc3 are
# Accountants, mgr/mgr2 Accounting Administrators. Arrangement that is not
# under test (an issued PO with its receipt) is done as superuser and says
# so. Everything rolls back (odoo_env).
from __future__ import annotations

import base64
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_ap_ext.models.ap_gl import ap_account
from odoo.addons.cd_ap_ext.models.fix_ap_capture import (
    BUCKETS,
    ageing_by_vendor,
    takeon_open_at,
)
from odoo.addons.cd_ap_ext.tests import test_a08_m52_operability as _ops
from odoo.exceptions import AccessError, UserError, ValidationError

from . import test_a08_m52_controls as _base

c = _base.c
bill = _base.bill
approve = _base.approve
issued_po = _base.issued_po
run = _base.run
_SEQ = _base._SEQ
# the Request Payment path (M50's relay and the clearing account), as the
# operability suite drives it
paying = _ops.paying
relay = _ops.relay
treasury_paid = _ops.treasury_paid
execution_of = _ops.execution_of

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)


@pytest.fixture(autouse=True)
def _no_default_tolerance(c):
    """These tests are about APPROVED tolerance rows: the A06 D8 default
    (+2 % or +BDT 500 a unit with no row) is switched off for them; its own
    test is test_a06_p2p_money.test_d8_default_tolerance_larger_of_two_percent_or_500."""
    icp = c.env["ir.config_parameter"].sudo()
    icp.set_param("cd_ap_ext.match_price_tolerance_pct", "0")
    icp.set_param("cd_ap_ext.match_price_tolerance_abs", "0")


def _refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except Exception as exc:  # any refusal counts: the caller names the one it expects
        return exc
    return None


def _po_bill(c, price, qty=10.0, received=10.0):
    """A PO bill against an issued PO with its accepted receipt (superuser
    arrangement), captured by an accountant."""
    po = issued_po(c, qty=received or qty, price=100.0, received=received)
    return bill(c, price, qty=qty, po=po)


def _tolerance(c, user, **kw):
    # the fixture's bills are dated 1 Oct 2026: the row is in force by then
    vals = {"reason": "Supplier rounding on spares %s" % next(_SEQ), "effective_from": "2026-01-01"}
    vals.update(kw)
    return c.env["fix.ap.match.tolerance"].with_user(user).create(vals)


def _active_tolerance(c, **kw):
    t = _tolerance(c, c.acc1, **kw)
    t.with_user(c.acc1).action_submit()
    t.with_user(c.mgr).action_approve()
    return t


# ------------------------------------------------------------------ tolerances
def test_without_a_tolerance_the_match_stays_exact(c):
    b = _po_bill(c, 104.0)
    assert b.match_state == "blocked" and "price above PO" in b.match_detail
    assert _po_bill(c, 100.0).match_state == "matched"


def test_a_tolerance_is_approved_by_a_second_administrator_and_frozen(c):
    t = _tolerance(c, c.mgr, price_pct=5.0)
    t.with_user(c.mgr).action_submit()
    with pytest.raises(UserError):
        t.with_user(c.acc2).action_approve()  # an accountant does not approve
    with pytest.raises(UserError):
        t.with_user(c.mgr).action_approve()  # nor the requester
    with pytest.raises(UserError):
        t.with_user(c.mgr).write({"price_pct": 50.0})  # submitted: frozen
    with pytest.raises(UserError):
        t.with_user(c.acc1).write({"state": "active"})
    t.with_user(c.mgr2).action_approve()
    assert t.state == "active" and t.approved_by_id == c.mgr2
    with pytest.raises(UserError):
        t.with_user(c.mgr2).unlink()


def test_an_approved_tolerance_rematches_open_bills_within_its_limits(c):
    within = _po_bill(c, 104.0)
    beyond = _po_bill(c, 106.0)
    assert within.match_state == "blocked" and beyond.match_state == "blocked"
    t = _active_tolerance(c, price_pct=5.0)
    assert within.match_state == "matched"
    assert "within the approved tolerance" in within.match_detail and t.name in within.match_detail
    assert beyond.match_state == "blocked"


def test_the_larger_price_limit_wins_and_quantity_has_its_own(c):
    # A06 D8: with both limits, the LARGER applies (1 % = 1.00 < 2.00 a unit)
    _active_tolerance(c, price_pct=1.0, price_abs=2.0)
    assert _po_bill(c, 103.0).match_state == "blocked"  # 3 > 2 per unit
    assert _po_bill(c, 101.5).match_state == "matched"
    qty_over = _po_bill(c, 100.0, qty=10.3)
    assert qty_over.match_state == "blocked"  # no quantity tolerance yet
    _active_tolerance(c, qty_pct=5.0, price_pct=5.0, price_abs=2.0)
    assert _po_bill(c, 100.0, qty=10.3).match_state == "matched"
    assert _po_bill(c, 100.0, qty=11.0).match_state == "blocked"


def test_a_new_version_supersedes_the_active_row(c):
    old = _active_tolerance(c, price_pct=5.0)
    new = _tolerance(c, c.acc1, price_pct=1.0)
    new.with_user(c.acc1).action_submit()
    assert new.supersedes_id == old
    new.with_user(c.mgr).action_approve()
    assert old.state == "superseded" and new.state == "active"
    assert _po_bill(c, 104.0).match_state == "blocked"


def test_tolerance_limits_are_validated(c):
    with pytest.raises(ValidationError):
        _tolerance(c, c.acc1, price_pct=150.0)
    with pytest.raises(ValidationError):
        _tolerance(c, c.acc1, price_abs=-1.0)
    with pytest.raises(UserError):
        _tolerance(c, c.plain, price_pct=1.0)  # not a finance user


# ------------------------------------------------------------------ match exception cases
def test_a_blocked_bill_gets_a_case_that_closes_only_when_its_cause_is_fixed(c):
    b = _po_bill(c, 104.0)
    b.with_user(c.acc1).action_open_match_case()
    case = b.open_match_case_id
    assert case and case.exception_type == "price" and case.responsible_party == "buyer"
    assert "price above PO" in case.variance_detail and case.owner_id == c.acc1
    assert case.name.startswith("MEX/")
    with pytest.raises(UserError):
        b.with_user(c.acc2).action_open_match_case()  # one open case per bill
    with pytest.raises(UserError):
        case.with_user(c.acc1).write({"state": "resolved"})
    with pytest.raises(UserError):
        case.with_user(c.acc1).write({"variance_detail": "nothing wrong"})
    case.with_user(c.acc1).write({"resolution_code": "matched", "resolution_note": "fixed"})
    with pytest.raises(UserError):
        case.with_user(c.acc1).action_resolve()  # still blocked: no override
    _active_tolerance(c, price_pct=5.0)  # the cause is fixed (approved tolerance)
    case.with_user(c.acc1).action_resolve()
    assert case.state == "resolved" and case.resolved_by_id == c.acc1
    with pytest.raises(UserError):
        case.with_user(c.acc1).write({"action_note": "rewrite history"})
    with pytest.raises(UserError):
        case.with_user(c.mgr).unlink()


def test_a_matched_bill_has_no_exception_case(c):
    b = _po_bill(c, 100.0)
    with pytest.raises(UserError):
        c.env["fix.ap.match.exception"].with_user(c.acc1).create({"invoice_id": b.id})


def test_the_daily_check_opens_and_closes_cases(c):
    b = _po_bill(c, 104.0)
    Case = c.env["fix.ap.match.exception"]
    Case._cron_match_exceptions()
    case = b.open_match_case_id
    assert case and case.owner_id == c.acc1
    _active_tolerance(c, price_pct=5.0)
    Case._cron_match_exceptions()
    assert case.state == "resolved" and case.resolution_code == "matched"


# ------------------------------------------------------------------ disputes
def _dispute(c, b, user=None, **kw):
    vals = {
        "invoice_id": b.id,
        "disputed_amount": 2000.0,
        "reason_code": "quality",
        "description": "Two boards dead on arrival",
    }
    vals.update(kw)
    return c.env["fix.ap.dispute"].with_user(user or c.acc1).create(vals)


def test_an_open_dispute_holds_the_bill_from_every_payment_path(c):
    b = approve(c, bill(c, 10000.0))
    r = run(c)
    assert b in r._candidate_bills()
    d = _dispute(c, b)
    assert d.name.startswith("APD/") and d.raised_by_id == c.acc1
    assert b not in r._candidate_bills()
    with pytest.raises(UserError):
        b.with_user(c.acc2).action_request_payment()
    d.with_user(c.acc2).write({"outcome": "not_upheld", "resolution_note": "Boards tested fine"})
    with pytest.raises(UserError):
        d.with_user(c.acc1).action_resolve()  # not the raiser
    d.with_user(c.acc2).write({"outcome": "upheld", "resolution_note": "Vendor agreed"})
    with pytest.raises(UserError):
        d.with_user(c.acc2).action_resolve()  # upheld needs the vendor's credit note
    d.with_user(c.acc2).write({"outcome": "not_upheld", "resolution_note": "Boards tested fine"})
    d.with_user(c.acc2).action_resolve()
    assert d.state == "resolved" and d.resolved_by_id == c.acc2
    assert b in r._candidate_bills()
    with pytest.raises(UserError):
        d.with_user(c.acc2).write({"disputed_amount": 1.0})


def test_a_dispute_is_raised_on_an_approved_unpaid_bill_for_at_most_its_value(c):
    draft = bill(c, 10000.0)
    with pytest.raises(UserError):
        _dispute(c, draft)
    b = approve(c, bill(c, 10000.0))
    assert isinstance(
        _refused(c.env, lambda: _dispute(c, b, disputed_amount=b.gross_amount + 1)),
        ValidationError,
    )
    with pytest.raises(UserError):
        _dispute(c, b, user=c.plain)
    _dispute(c, b)
    with pytest.raises(UserError):
        _dispute(c, b)  # one open dispute per bill


def test_a_dispute_held_bill_is_refused_on_a_proposed_run(c):
    b = approve(c, bill(c, 10000.0))
    r = run(c)
    r.with_user(c.acc1).action_propose()
    line = r.line_ids.filtered(lambda ln: b in ln.bill_ids)
    assert line.state != "skipped"
    _dispute(c, b, user=c.acc2)
    with pytest.raises(UserError):
        r.with_user(c.acc1).action_submit()


# ------------------------------------------------------------------ vendor statements
def test_a_vendor_statement_is_compared_explained_and_signed_by_a_second_person(c):
    b = approve(c, bill(c, 10000.0))
    s = (
        c.env["fix.ap.vendor.statement"]
        .with_user(c.acc1)
        .create(
            {
                "partner_id": c.vendor.id,
                "statement_date": fields.Date.context_today(c.env.user),
                "statement_balance": b.total_payable + 500.0,
                "statement_file": base64.b64encode(b"statement"),
                "statement_filename": "statement.pdf",
            }
        )
    )
    s.with_user(c.acc1).action_compare()
    assert s.ledger_balance == pytest.approx(b.total_payable)
    assert s.difference == pytest.approx(500.0) and s.open_bill_count == 1
    with pytest.raises(UserError):
        s.with_user(c.acc2).action_sign_off()  # a difference needs its items
    with pytest.raises(UserError):
        s.with_user(c.acc1).write({"ledger_balance": s.statement_balance})
    s.with_user(c.acc1).write({"reconciling_items": "Bill INV-778 dated 30 Sep not received"})
    with pytest.raises(UserError):
        s.with_user(c.acc1).action_sign_off()  # the preparer
    s.with_user(c.acc2).action_sign_off()
    assert s.state == "signed" and s.signed_by_id == c.acc2
    with pytest.raises(UserError):
        s.with_user(c.acc1).write({"statement_balance": 1.0})


# ------------------------------------------------------------------ ageing snapshots
def test_an_ageing_snapshot_is_kept_exactly_as_taken(c):
    b = approve(c, bill(c, 10000.0))
    # the latest past date with no snapshot kept yet (a database may hold one
    # for today already: a snapshot is one per date and never deleted)
    Snap = c.env["fix.ap.ageing.snapshot"]
    today = fields.Date.context_today(c.env.user)
    while Snap.search_count([("company_id", "=", c.company.id), ("as_of", "=", today)]):
        today -= timedelta(days=1)
    snap = Snap.with_user(c.acc1).create({"as_of": today})
    line = snap.line_ids.filtered(lambda ln: ln.partner_id == c.vendor)
    assert line and line.total == pytest.approx(b.total_payable)
    assert snap.taken_by_id == c.acc1 and snap.total >= b.total_payable - 0.01
    with pytest.raises(UserError):
        snap.with_user(c.acc1).write({"as_of": "2026-01-01"})
    with pytest.raises(UserError):
        snap.with_user(c.mgr).unlink()
    with pytest.raises(UserError):
        line.with_user(c.mgr).write({"total": 0.0})
    assert (
        _refused(
            c.env,
            lambda: c.env["fix.ap.ageing.snapshot"].with_user(c.acc2).create({"as_of": today}),
        )
        is not None
    )  # one per date
    with pytest.raises(UserError):
        c.env["fix.ap.ageing.snapshot"].with_user(c.acc1).create(
            {"as_of": "2099-01-01"}
        )  # a date that has not come
    with pytest.raises(UserError):
        c.env["fix.ap.ageing.snapshot"].with_user(c.plain).create({"as_of": "2026-10-31"})


# ------------------------------------------ ageing as of a past date (A08 M52-F5)
# Audit A3 M52-F5 (probe3b B): the ageing "as of" a past date read the CURRENT
# payment state, so a bill unpaid on that date but paid since (77,500 on
# 1 Nov, paid 21 Nov) had vanished from it (0.00). The ageing is now read as of
# its date: what each bill, note and legacy take-on item still owed ON it. A
# payment counts from the date of the entry that cleared the payable.
def _today(c):
    return fields.Date.context_today(c.env.user)


def _ageing(c, as_of):
    """The AP ageing at `as_of`, read as an accountant."""
    return ageing_by_vendor(c.env(user=c.acc1.id), c.company, as_of)[0]


def _sum(row):
    return round(sum(row[key] for key, _label in BUCKETS), 2)


def _sum_all(c, as_of):
    """The whole ageing at `as_of`, legacy take-on included."""
    return round(sum(_sum(row) for row in _ageing(c, as_of).values()), 2)


def _owed(c, as_of):
    """What the ageing at `as_of` says the fixture vendor is owed (her own
    line, without a legacy take-on)."""
    return round(
        sum(
            _sum(row)
            for label, row in _ageing(c, as_of).items()
            if row["partner_id"] == c.vendor.id and "·" not in label
        ),
        2,
    )


def _paid_by_run(c, b, payment_date=None):
    """The bill is paid by a payment run whose entry is dated `payment_date`
    (default today): proposed, submitted, approved, released, executed."""
    r = (
        c.env["fix.payment.run"]
        .with_user(c.acc1)
        .create(
            {"rail": "beftn", "due_by": _base.DUE_BY, "payment_date": payment_date or _today(c)}
        )
    )
    r.with_user(c.acc1).action_propose()
    r.with_user(c.acc1).action_submit()
    r.with_user(c.mgr).action_approve()
    r.with_user(c.acc2).action_release()
    return r


def test_f5_a_bill_paid_after_the_as_of_date_is_still_open_on_it(c):
    today = _today(c)
    before = today - timedelta(days=5)
    b = approve(c, bill(c, 10000.0))  # 9,000 payable, dated 1 Oct
    assert _owed(c, before) == 9000.0
    r = _paid_by_run(c, b)  # the run pays today
    assert (_owed(c, before), _owed(c, today)) == (9000.0, 9000.0)  # in flight: still owed
    _base.treasury_execute(c, r.line_ids.execution_id)
    r.with_user(c.acc2).action_sync_bank_status()
    assert (b.payment_state, r.line_ids.move_id.date) == ("paid", today)
    assert _owed(c, before) == 9000.0  # paid AFTER that date: still owed on it
    assert _owed(c, today) == 0.0  # and gone from a later one
    # a snapshot taken now of that earlier date freezes the same figure
    Snap = c.env["fix.ap.ageing.snapshot"]
    while Snap.search_count([("company_id", "=", c.company.id), ("as_of", "=", before)]):
        before -= timedelta(days=1)
    snap = Snap.with_user(c.acc1).create({"as_of": before})
    line = snap.line_ids.filtered(lambda ln: "·" not in ln.label and ln.partner_id == c.vendor)
    assert len(line) == 1 and line.total == 9000.0
    # the vendor's statement of that date counts the bill too
    s = (
        c.env["fix.ap.vendor.statement"]
        .with_user(c.acc1)
        .create({"partner_id": c.vendor.id, "statement_date": before, "statement_balance": 0.0})
    )
    s.with_user(c.acc1).action_compare()
    assert (s.ledger_balance, s.open_bill_count, s.difference) == (9000.0, 1, -9000.0)
    later = (
        c.env["fix.ap.vendor.statement"]
        .with_user(c.acc1)
        .create({"partner_id": c.vendor.id, "statement_date": today, "statement_balance": 0.0})
    )
    later.with_user(c.acc1).action_compare()
    assert (later.ledger_balance, later.open_bill_count) == (0.0, 0)


def test_f5_a_bill_request_paid_after_the_as_of_date_is_still_open_on_it(c, paying):
    today = _today(c)
    before = today - timedelta(days=5)
    b = approve(c, bill(c, 10000.0))
    b.with_user(c.acc1).action_request_payment()
    relay(c, "payment.requested", "fix.vendor.invoice", b.id)
    ex = execution_of(c, b._name, b.id)
    assert _owed(c, today) == 9000.0  # asked for, not paid
    treasury_paid(c, ex)
    relay(
        c,
        "payment.executed",
        "fix.payment.execution",
        ex.id,
        "cd_ap_ext.consumer_payment_executed_ap",
    )
    assert (b.payment_state, b.payment_move_id.date) == ("paid", today)
    assert (_owed(c, before), _owed(c, today)) == (9000.0, 0.0)


def test_f5_a_returned_payment_counts_until_the_day_it_came_back(c):
    """The other side of the as-of date: a payment the bank took back is in
    force from its own date until the return is dated, no longer."""
    today = _today(c)
    b = approve(c, bill(c, 10000.0))
    r = _paid_by_run(c, b, payment_date=today - timedelta(days=2))
    _base.treasury_execute(c, r.line_ids.execution_id)
    r.with_user(c.acc2).action_sync_bank_status()
    assert b.payment_state == "paid"
    assert _owed(c, today - timedelta(days=1)) == 0.0  # paid two days ago: not owed yesterday
    _base.treasury_fail(c, r.line_ids.execution_id)  # returned after clearing, today
    r.with_user(c.acc2).action_sync_bank_status()
    assert (r.line_ids.state, b.payment_state) == ("failed", "not_paid")
    assert (_owed(c, today - timedelta(days=1)), _owed(c, today)) == (0.0, 9000.0)


def test_f5_a_note_netted_after_the_as_of_date_still_counts_on_it(c):
    today = _today(c)
    before = today - timedelta(days=5)
    b = approve(c, bill(c, 20000.0))  # 18,000 payable
    note = (
        c.env["fix.vendor.note"]
        .with_user(c.acc1)
        .create(
            {
                "invoice_id": b.id,
                "note_type": "decrease",
                "mushak_ref": "67-F5-1",
                "note_date": _base.D + timedelta(days=3),
                "amount": 5000.0,
            }
        )
    )
    note.with_user(c.acc2).action_approve()
    assert note.signed_total == -5000.0
    assert _owed(c, before) == 13000.0
    r = _paid_by_run(c, b)  # the run nets the note; the bank has not paid yet
    assert (note.state, b.payment_state, r.state) == ("applied", "in_run", "released")
    assert _owed(c, today) == 13000.0  # until the bank pays, the payable is not reduced
    _base.treasury_execute(c, r.line_ids.execution_id)
    r.with_user(c.acc2).action_sync_bank_status()
    assert (_owed(c, before), _owed(c, today)) == (13000.0, 0.0)


# ---- the legacy take-on lane: the GL lines, posted as superuser (arrangement)
def _account(c, code, name, kind):
    Account = c.env["account.account"]
    return Account.search(
        [("code", "=", code), ("company_ids", "in", c.company.id)], limit=1
    ) or Account.create(
        {"code": code, "name": name, "account_type": kind, "company_ids": [(6, 0, c.company.ids)]}
    )


def _journal(c, code, name):
    Journal = c.env["account.journal"]
    return Journal.search(
        [("code", "=", code), ("company_id", "=", c.company.id)], limit=1
    ) or Journal.create({"name": name, "code": code, "type": "general", "company_id": c.company.id})


def _takeon_control(c):
    """A payable control the legacy take-on is configured on (on the live
    estate the take-on and the bills share 200101)."""
    control = _account(c, "299105", "F5 legacy payable control", "liability_payable")
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_gl_ext.ledger_takeon.payable_account_code", "299105"
    )
    return control


def _post_on_control(c, journal, control, partner, amount, on, name):
    """One posted entry on the control: a credit (`amount` > 0) or a debit
    (`amount` < 0) for `partner`, contra another account. Returns the
    control's line."""
    debit, credit = (-amount, 0.0) if amount < 0 else (0.0, amount)
    contra = _account(c, "299906", "F5 legacy take-on contra", "liability_current")
    move = c.env["account.move"].create(
        {
            "journal_id": journal.id,
            "company_id": c.company.id,
            "date": on,
            "move_type": "entry",
            "ref": name,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": control.id,
                        "partner_id": partner.id,
                        "date_maturity": on,
                        "name": name,
                        "debit": debit,
                        "credit": credit,
                    },
                ),
                (
                    0,
                    0,
                    {"account_id": contra.id, "name": "contra", "debit": credit, "credit": debit},
                ),
            ],
        }
    )
    move.action_post()
    return move.line_ids.filtered(lambda ln: ln.account_id == control)


def _takeon_owed(c, partner, as_of):
    """What the ageing at `as_of` says a party's legacy take-on still owes."""
    return round(
        sum(
            _sum(row)
            for label, row in _ageing(c, as_of).items()
            if row["partner_id"] == partner.id and "·" in label
        ),
        2,
    )


def test_f5_b_a_take_on_item_settled_after_the_as_of_ages_at_its_residual(c):
    today = _today(c)
    before = today - timedelta(days=5)
    control = _takeon_control(c)
    legacy = c.env["res.partner"].create({"name": "F5 Legacy Vendor"})
    taken = _post_on_control(
        c, _journal(c, "MIG", "Legacy Take-on"), control, legacy, 10000.0, _base.D, "Legacy take-on"
    )
    assert (_takeon_owed(c, legacy, before), _takeon_owed(c, legacy, today)) == (
        10000.0,
        10000.0,
    )
    paid = _post_on_control(
        c,
        _journal(c, "F5PAY", "F5 Legacy Settlements"),
        control,
        legacy,
        -4000.0,
        today,
        "Legacy balance paid",
    )
    (taken | paid).reconcile()  # 4,000 of it cleared today
    assert taken.amount_residual == -6000.0  # Odoo: 6,000 is open NOW
    assert _takeon_owed(c, legacy, before) == 10000.0  # 10,000 was open on that date
    assert _takeon_owed(c, legacy, today) == 6000.0
    on = takeon_open_at(c.env, c.company, control, today)[legacy.id]
    assert (on["residual"], on["date"]) == (-6000.0, _base.D)  # Odoo's own residual for today
    assert _takeon_owed(c, legacy, _base.D - timedelta(days=1)) == 0.0  # taken on the day itself
    # it is the party's own line, aged from the take-on date: 14 days on 15 Oct
    row = next(
        row
        for label, row in _ageing(c, date(2026, 10, 15)).items()
        if row["partner_id"] == legacy.id and "·" in label
    )
    assert (row["d1_30"], _sum(row)) == (10000.0, 10000.0)


def test_f5_d_the_ageing_ties_to_the_payable_controls_at_every_step(c):
    """Regression (d): open bills, a credit note, a run in flight, the payment
    and the legacy take-on. At each step the ageing as of today moves exactly
    as the two payable controls do, so their totals still tie."""
    today = _today(c)
    ap = ap_account(c.env, c.company, "ap")
    legacy_control = _takeon_control(c)
    start = (
        _sum_all(c, today),
        _base.balance(c.env, ap),
        _base.balance(c.env, legacy_control),
    )
    legacy = c.env["res.partner"].create({"name": "F5 Legacy Vendor"})
    taken = _post_on_control(
        c,
        _journal(c, "MIG", "Legacy Take-on"),
        legacy_control,
        legacy,
        8000.0,
        _base.D,
        "Legacy take-on",
    )
    paid = _post_on_control(
        c,
        _journal(c, "F5PAY", "F5 Legacy Settlements"),
        legacy_control,
        legacy,
        -3000.0,
        today,
        "Legacy balance paid",
    )
    (taken | paid).reconcile()

    def ties():
        """How much the ageing rose since the start; it equals what the two
        payable controls took up (credit-normal)."""
        ageing, on_ap, on_takeon = (
            _sum_all(c, today),
            _base.balance(c.env, ap),
            _base.balance(c.env, legacy_control),
        )
        assert ageing - start[0] == pytest.approx(-(on_ap - start[1]) - (on_takeon - start[2]))
        return ageing - start[0]

    assert ties() == 5000.0  # the legacy take-on, 3,000 of it paid
    b1 = approve(c, bill(c, 10000.0))  # 9,000 payable
    b2 = approve(c, bill(c, 20000.0, ref="A08B2-F5-2"))  # 18,000 payable
    note = (
        c.env["fix.vendor.note"]
        .with_user(c.acc1)
        .create(
            {
                "invoice_id": b2.id,
                "note_type": "decrease",
                "mushak_ref": "67-F5-2",
                "note_date": _base.D + timedelta(days=3),
                "amount": 5000.0,
            }
        )
    )
    note.with_user(c.acc2).action_approve()
    assert ties() == 27000.0
    r = _paid_by_run(c, b1)  # one line: both bills and the note
    assert r.line_ids.amount == 22000.0 and b1.payment_state == "in_run"
    assert ties() == 27000.0  # released to the bank, nothing paid: no change
    _base.treasury_execute(c, r.line_ids.execution_id)
    r.with_user(c.acc2).action_sync_bank_status()
    assert (b1.payment_state, b2.payment_state, note.state) == ("paid", "paid", "applied")
    assert ties() == 5000.0


# ------------------------------------------------------------------ GRNI accrual
def test_a_grni_accrual_is_computed_from_receipts_and_confirmed_by_a_second_person(c):
    po = issued_po(c, qty=5.0, price=200.0, received=5.0)  # arrangement (superuser)
    today = fields.Date.context_today(c.env.user)
    a = c.env["fix.ap.grni.accrual"].with_user(c.acc1).create({"period_end": today})
    a.with_user(c.acc1).action_compute()
    mine = a.line_ids.filtered(lambda ln: ln.po_line_id.order_id == po)
    assert mine and mine.open_qty == pytest.approx(5.0) and mine.accrual == pytest.approx(1000.0)
    assert a.grni_total >= 1000.0 and a.state == "computed"
    with pytest.raises(UserError):
        mine.with_user(c.acc1).write({"accrual": 0.0})
    a.with_user(c.acc1).write({"unrecorded_estimate": 25000.0})
    with pytest.raises(UserError):
        a.with_user(c.acc2).action_confirm()  # an accountant does not confirm
    with pytest.raises(UserError):
        a.with_user(c.mgr).action_confirm()  # the estimate needs its basis
    a.with_user(c.acc1).write({"unrecorded_basis": "October utilities and rent, no bill yet"})
    a.with_user(c.mgr).action_confirm()
    assert a.state == "confirmed" and a.confirmed_by_id == c.mgr
    # A08 M52-F1 (FR-APE-031 P0): the confirm is the posting moment
    assert a.move_id.state == "posted" and a.reversal_move_id.state == "posted"
    with pytest.raises(UserError):
        a.with_user(c.mgr).write({"unrecorded_estimate": 1.0})
    with pytest.raises(UserError):
        a.with_user(c.mgr).unlink()


def test_a_billed_receipt_leaves_the_grni_accrual(c):
    po = issued_po(c, qty=5.0, price=200.0, received=5.0)
    b = (
        c.env["fix.vendor.invoice"]
        .with_user(c.acc1)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "vendor_id": c.vendor.id,
                "invoice_ref": "M52CAP-GRNI-%d" % next(_SEQ),
                "bill_type": "po",
                "requisition_id": po.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": c.product.id,
                            "description": "board",
                            "quantity": 5.0,
                            "unit_price": 200.0,
                            "tds_category": "supply_of_goods",
                        },
                    )
                ],
            }
        )
    )
    assert b.match_state == "matched"
    # A06 X26: a bill clears GRNI when it posts (the as-at basis reads posted bills)
    approve(c, b)
    a = (
        c.env["fix.ap.grni.accrual"]
        .with_user(c.acc1)
        .create({"period_end": max(b.invoice_date, fields.Date.context_today(c.env.user))})
    )
    a.with_user(c.acc1).action_compute()
    assert not a.line_ids.filtered(lambda ln: ln.po_line_id.order_id == po)


def test_the_accrual_creator_does_not_confirm_it(c):
    a = (
        c.env["fix.ap.grni.accrual"]
        .with_user(c.mgr)
        .create({"period_end": fields.Date.context_today(c.env.user)})
    )
    a.with_user(c.mgr).action_compute()
    with pytest.raises(UserError):
        a.with_user(c.mgr).action_confirm()
    a.with_user(c.mgr2).action_confirm()
    assert a.state == "confirmed"


# ------------------------------------------- GRNI accrual posting (A08 M52-F1)
def _confirmed_accrual(c, estimate=0.0, basis=""):
    """An accrual over an issued PO with its accepted receipt (superuser
    arrangement), computed by acc1 and confirmed by the manager: the second
    person the model requires."""
    po = issued_po(c, qty=5.0, price=200.0, received=5.0)
    a = (
        c.env["fix.ap.grni.accrual"]
        .with_user(c.acc1)
        .create({"period_end": fields.Date.context_today(c.env.user)})
    )
    a.with_user(c.acc1).action_compute()
    if estimate:
        a.with_user(c.acc1).write({"unrecorded_estimate": estimate, "unrecorded_basis": basis})
    a.with_user(c.mgr).action_confirm()
    return a, po


def test_confirming_the_accrual_posts_the_period_end_entry(c):
    """A08 M52-F1 (FR-APE-031 P0 / BRU-APE-22 H): the second person's confirm
    posts the money — Dr each line's expense account and the unrecorded
    estimate, Cr the GRNI accrual liability, dated the period end, in the
    purchase journal, with the AP dimensions on every line and the vendor on
    the PO's leg. Mutation: the old confirm wrote only state fields and no
    account.move appeared (probe2 G)."""
    a, po = _confirmed_accrual(c, estimate=25000.0, basis="October utilities and rent, no bill yet")
    move = a.move_id
    assert move and move.state == "posted"
    assert move.date == a.period_end and move.journal_id.type == "purchase"
    seat = c.a["grni_accrual"]
    credits = move.line_ids.filtered(lambda ln: ln.account_id == seat)
    debits = move.line_ids.filtered(lambda ln: ln.account_id != seat)
    total = pytest.approx(a.grni_total + 25000.0)
    assert sum(credits.mapped("credit")) == total and not sum(credits.mapped("debit"))
    assert sum(debits.mapped("debit")) == total and not sum(debits.mapped("credit"))
    mine = debits.filtered(lambda ln: ln.name.endswith(po.name))
    assert mine and mine.partner_id == c.vendor.commercial_partner_id
    dims = c.env["fix.journal.dimension"].search([("move_line_id", "in", move.line_ids.ids)])
    assert dims and all(d.operating_unit_id for d in dims)
    assert any(d.operating_unit_id == po.operating_unit_id for d in dims)


def test_the_accrual_entry_reverses_on_the_first_day_of_the_next_period(c):
    """BRU-APE-22 H: the accrual is superseded next period — the mirror entry is
    linked back on the accrual (reversal_move_id), dated the first day of the
    month after the period end (the recurring engine's auto-reverse idiom), and
    is an exact per-account mirror, so the pair nets to nothing once both are
    in and the vendor bills post fresh."""
    a, _po = _confirmed_accrual(c)
    rev = a.reversal_move_id
    assert rev and rev.state == "posted" and rev.journal_id == a.move_id.journal_id
    end = fields.Date.to_date(a.period_end)
    assert rev.date == (end.replace(day=28) + timedelta(days=4)).replace(day=1)

    def per_account(move):
        out = {}
        for line in move.line_ids:
            out[line.account_id] = round(out.get(line.account_id, 0.0) + line.balance, 2)
        return out

    assert not (set(per_account(a.move_id)) ^ set(per_account(rev)))
    for account, balance in per_account(a.move_id).items():
        assert round(balance + per_account(rev)[account], 2) == 0.0


def test_the_posting_funnel_logs_the_accrual_and_its_reversal(c):
    """FR-FIN-042: both entries went through the estate's funnel — one
    fix.journal.posting.log row each, as AP sub-ledger postings."""
    a, _po = _confirmed_accrual(c)
    rows = c.env["fix.journal.posting.log"].search(
        [("move_id", "in", (a.move_id | a.reversal_move_id).ids)]
    )
    assert {r.move_id.id for r in rows} == {a.move_id.id, a.reversal_move_id.id}
    assert all(r.source == "ap_subledger" and r.state == "posted" for r in rows)


def test_a_refused_confirm_posts_nothing(c):
    """The SoD around the confirm is the gate on the money too: an accountant,
    and the person who computed the accrual, are refused — and nothing reaches
    the ledger while they are (the accrual stays computed, no entry, no
    reversal)."""
    issued_po(c, qty=5.0, price=200.0, received=5.0)
    a = (
        c.env["fix.ap.grni.accrual"]
        .with_user(c.acc1)
        .create({"period_end": fields.Date.context_today(c.env.user)})
    )
    a.with_user(c.acc1).action_compute()
    before = c.env["account.move"].search_count([])
    with pytest.raises(UserError):
        a.with_user(c.acc2).action_confirm()  # an accountant does not confirm
    with pytest.raises(UserError):
        a.with_user(c.acc1).action_confirm()  # the computer is not the checker
    assert c.env["account.move"].search_count([]) == before
    assert a.state == "computed" and not a.move_id and not a.reversal_move_id


def test_the_close_seam_blocks_a_confirmed_accrual_without_its_entry(c):
    """BRU-APE-22 H: a period cannot close over a confirmed-but-unposted GRNI
    accrual. Confirming posts both legs, so the seam is exercised on the record
    a guarded write could leave behind; a posted accrual and an empty period's
    accrual block nothing. _fix_close_blockers is the query the M19 close
    checklist wires next to its own _fix_check_* refusals."""
    Accrual = c.env["fix.ap.grni.accrual"].sudo()
    a, _po = _confirmed_accrual(c)
    assert not Accrual._fix_close_blockers(c.company, a.period_end)
    a._guarded().write({"move_id": False})  # the hole the finding stood on
    assert a in Accrual._fix_close_blockers(c.company, a.period_end)
    assert not Accrual._fix_close_blockers(c.company, a.period_end - timedelta(days=1))
    empty = Accrual.with_user(c.mgr).create({"period_end": date(2020, 1, 31)})
    empty.with_user(c.mgr).action_compute()
    assert empty.grni_total == 0.0
    empty.with_user(c.mgr2).action_confirm()
    assert empty.state == "confirmed" and not empty.move_id
    assert empty not in Accrual._fix_close_blockers(c.company, empty.period_end)


# ------------------------------------------------------------------ cards
def test_card_spend_is_explained_and_approved_by_finance_never_the_holder(c):
    holder = c.env["hr.employee"].create({"name": "M52CAP Fuel Holder", "user_id": c.acc2.id})
    with pytest.raises(ValidationError):
        c.env["fix.expense.card"].with_user(c.acc1).create(
            {"issuer": "Padma Oil", "last_digits": "12345", "holder_id": holder.id}
        )
    card = (
        c.env["fix.expense.card"]
        .with_user(c.acc1)
        .create(
            {
                "card_type": "fuel",
                "issuer": "Padma Oil",
                "last_digits": "4321",
                "holder_id": holder.id,
            }
        )
    )
    txn = (
        c.env["fix.expense.card.transaction"]
        .with_user(c.acc1)
        .create(
            {
                "card_id": card.id,
                "txn_date": "2026-11-02",
                "merchant": "Tejgaon filling station",
                "amount": 3200.0,
                "statement_ref": "PO-STMT-11-0007",
            }
        )
    )
    assert card.unexplained_count == 1
    with pytest.raises(UserError):
        txn.with_user(c.acc2).action_explain()  # no category / cost centre / receipt
    txn.with_user(c.acc2).write(
        {
            "category_id": c.other.id,
            "cost_centre": "JOB-77",
            "receipt_file": base64.b64encode(b"receipt"),
            "receipt_filename": "r.jpg",
        }
    )
    txn.with_user(c.acc2).action_explain()
    with pytest.raises(UserError):
        txn.with_user(c.acc2).action_approve()  # the cardholder
    with pytest.raises(UserError):
        txn.with_user(c.acc2).write({"amount": 32.0})  # as the issuer printed it
    txn.with_user(c.mgr).action_approve()
    assert txn.state == "approved" and txn.approved_by_id == c.mgr
    with pytest.raises(UserError):
        txn.with_user(c.acc1).write({"cost_centre": "JOB-1"})
    with pytest.raises(UserError):
        txn.with_user(c.mgr).unlink()
    assert (
        _refused(
            c.env,
            lambda: c.env["fix.expense.card.transaction"]
            .with_user(c.acc1)
            .create(
                {
                    "card_id": card.id,
                    "txn_date": "2026-11-02",
                    "merchant": "again",
                    "amount": 1.0,
                    "statement_ref": "PO-STMT-11-0007",
                }
            ),
        )
        is not None
    )  # recorded once
