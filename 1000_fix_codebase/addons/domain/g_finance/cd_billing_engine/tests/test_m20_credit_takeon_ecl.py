# A08 · M20-F1 / M20-F2 (B3, Nov 2026): credit-limit enforcement and the
# IFRS 9 ECL run both ignored the legacy take-on receivables — the estate's
# entire real AR (fix_real: ৳15.39 Cr open over 957 partners). Regressions:
#   F1 (a) issuing against a 100 limit with a 5,000 take-on trips over-limit
#         and the invoicing gate (FR-ARB-030);
#   F1 (b) the stored exposure recomputes on invoice issue and on receipt
#         allocation (it used to move only when the limit/customer changed);
#   F1     the M01 credit-release room counts the take-on too;
#   F2 (c) the ECL exposure basis is the ageing snapshot's own basis — the
#         run and the snapshot agree, take-on amounts aged from their
#         take-on date into their REAL buckets (never blanket-bucketed).
import uuid
from datetime import date

import pytest

# ruff: noqa: F811  (the M20 fixture is imported and used as a parameter)
from odoo.addons.cd_billing_engine.tests.test_a08_m20_controls import (  # noqa: F401
    as_,
    c,
    c_raw,
    ecl_rates,
    inv,
    rcpt,
)
from odoo.addons.cd_billing_engine.tests.test_takeon_opening_balances import _takeon
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import m04  # noqa: F401
from odoo.addons.cd_front_desk_finance.tests.test_a02_order_money_reaches_books import (  # noqa: F401
    books,
)
from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import fin  # noqa: F401
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

AS_OF = date(2026, 11, 12)


def _profile(env, customer, limit=0.0):
    """A credit profile, its limit set the way a migration/seed does (a user
    cannot type one: BRU-CPM-12, only an approved change request sets it)."""
    return env.env["fix.credit.profile"].create(
        {
            "company_id": env.company.id,
            "customer_id": customer.id,
            "credit_limit": limit,
        }
    )


def _inv_for(fx, customer, taxable, maker=None, issuer=None):
    """A manual invoice issued for an arbitrary customer (the inv() helper
    bills fx.customer only)."""
    maker = maker or fx.acct
    i = as_(fx, maker)["fix.ar.invoice"].create_manual_invoice(
        {
            "customer_id": customer.id,
            "operating_unit_id": fx.ou.id,
            "company_id": fx.company.id,
        },
        [{"description": "Job", "taxable_amount": taxable}],
        reason_code="B3 take-on test",
    )
    i.with_user(issuer or fx.acct2).action_issue()
    return i


def _books_takeon(m, partner, amount, when=date(2026, 11, 8)):
    """A legacy take-on line on the books world's own AR control (the role
    parameter points at m.ar), in journal MIG like the real take-on."""
    env = m.env
    mig = env["account.journal"].search(
        [("code", "=", "MIG"), ("company_id", "=", env.company.id)], limit=1
    )
    if not mig:
        mig = env["account.journal"].create(
            {
                "name": "Legacy Take-on",
                "code": "MIG",
                "type": "general",
                "company_id": env.company.id,
                "sequence": 99,
            }
        )
    contra = env["account.account"].create(
        {
            "name": "B3 take-on contra",
            "code": "B3TKO%s" % uuid.uuid4().hex[:6].upper(),
            "account_type": "liability_current",
        }
    )
    debit, credit = (amount, 0.0) if amount > 0 else (0.0, -amount)
    move = env["account.move"].create(
        {
            "journal_id": mig.id,
            "company_id": env.company.id,
            "date": when,
            "move_type": "entry",
            "ref": "TAKEON test (B3)",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": m.ar.id,
                        "partner_id": partner.id,
                        "date_maturity": when,
                        "name": "Legacy take-on %s" % partner.name,
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
    return move


# ------------------------------------------------- M20-F1 (a): the gate bites
def test_the_stored_exposure_counts_the_legacy_takeon(c):
    _takeon(c, c.customer, 5000.0)
    prof = _profile(c, c.customer)
    # no limit set: the measure is complete, nothing to breach
    assert (prof.exposure, prof.over_limit) == (5000.0, False)


def test_issue_against_a_small_limit_with_takeon_trips_over_limit_and_the_gate(c):
    _takeon(c, c.customer, 5000.0)  # the migrated open balance on the AR control
    prof = _profile(c, c.customer, limit=100.0)
    assert prof.over_limit, "5,000 taken on against a 100 limit is over it"
    # issuing ANYTHING more is refused at the gate — before, the exposure sat
    # at 0.0 and the customer was invoiced fresh money past the limit
    with pytest.raises(UserError, match="FR-ARB-030"):
        inv(c, c.acct, 100.0)
    # a customer with room under the limit still invoices: the gate measures,
    # it does not block the world
    _profile(c, c.customer2, limit=10000.0)
    assert _inv_for(c, c.customer2, 100.0).state == "issued"


# ------------------------------------- M20-F1 (b): the stored figure follows AR
def test_exposure_recomputes_on_issue_and_on_receipt_allocation(c):
    prof = _profile(c, c.customer)
    assert prof.exposure == 0.0
    i = inv(c, c.acct, 1000.0)  # issued: 1,150 open (VAT 15%)
    assert (prof.exposure, i.amount_residual) == (1150.0, 1150.0)
    r = rcpt(c, c.acct, 500.0)
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i.id, "amount": 500.0}
    )
    # the allocation moved the residual, so the profile's stored exposure
    # moved with it — no profile edit in between
    assert (prof.exposure, i.amount_residual) == (650.0, 650.0)


# ------------------------------- M20-F1: the M01 release room counts take-on
def test_credit_release_counts_the_legacy_takeon(books):
    m = books
    order = m.job(1000.0)  # 1,150 due with VAT
    _books_takeon(m, order.customer_id.commercial_partner_id, 5000.0)
    prof = m.env["fix.credit.profile"].create(
        {
            "customer_id": order.customer_id.id,
            "company_id": order.company_id.id,
            "credit_limit": 6000.0,
        }
    )
    # 5,000 already owed on account: 1,000 left, the order needs 1,150
    with pytest.raises(UserError, match="left under its"):
        order.with_user(m.fin_manager).action_release_on_credit()
    prof.credit_limit = 6200.0  # su: the seeded limit moves (as a migration would)
    order.with_user(m.fin_manager).action_release_on_credit()
    assert order.payment_settlement_state == "credit_approved"


# --------------------------------- M20-F2 (c): the run is the snapshot's basis
def test_ecl_exposure_equals_the_ageing_snapshot_total_incl_takeon(c):
    ecl_rates(c)
    _takeon(c, c.customer2, 5000.0)  # 4 days at AS_OF: the 1-30 bucket
    _takeon(c, c.customer, 7000.0, when=date(2026, 8, 1))  # 103 days: 90+, its REAL bucket
    inv(c, c.acct, 1000.0, when=date(2026, 11, 10))  # 1,150 within net-30: current
    snap = as_(c, c.acct)["fix.ar.aging.snapshot"].create({"company_id": c.company.id})
    snap.action_capture(as_of=AS_OF)
    run = as_(c, c.acct)["fix.ar.impairment"].create(
        {
            "company_id": c.company.id,
            "journal_id": c.journal.id,
            "as_of": AS_OF,
            "expense_account_id": c.acc["ecl_expense"].id,
            "provision_account_id": c.acc["ecl_provision"].id,
        }
    )
    run.action_compute()
    # the probe gap: run exposure 432.50 vs snapshot 153,860,191.59 — the two
    # now agree by construction (same invoices, same take-on, same buckets)
    assert run.total_exposure == snap.total_open == 13150.0
    assert {ln.bucket: ln.exposure for ln in run.line_ids} == {
        "current": 1150.0,
        "d1_30": 5000.0,
        "d31_60": 0.0,
        "d61_90": 0.0,
        "d90_plus": 7000.0,
    }
    # the provision follows the same ageing (0.5% / 2% / 50% per ecl_rates)
    assert run.total_provision == 3605.75
