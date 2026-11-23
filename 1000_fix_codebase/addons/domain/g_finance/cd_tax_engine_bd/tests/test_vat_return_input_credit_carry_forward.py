"""M51-F8 — FR-TAX-018 / FR-TAX-029: the input VAT credit ledger on the
Mushak 9.1.

The finding: `fix.vat.return` had no opening/closing credit balance, so a
period with input > output produced a negative `net_payable` that the VAT
challan refused, stranding the credit. These tests drive the real prepare /
file path as the non-admin accountant and filing approver:

(a) input above output files at net 0.00 and carries the excess;
(b) the next period consumes exactly min(opening, max(0, output - input))
    and carries the remainder;
(c) a tampered opening credit is refused at filing, naming both figures;
(d) a nil period still files and passes the credit through unchanged;
(e) an ordinary input < output period is unchanged from before the ledger;
(f) the VAT challan settles the POST-credit net payable, not output - input.

Everything runs in the fixture's company inside the rolled-back odoo_env.
"""

from __future__ import annotations

from datetime import date

import pytest
from odoo.addons.cd_tax_engine_bd.tests.test_a08_m51_controls import (
    RET,
    StubEvat,
    _credit,
    _entry,
    _refused,
    _reg,
    _vat_return,
    c,  # noqa: F401 - the shared fixture
)
from odoo.exceptions import UserError

pytestmark = [pytest.mark.tax, pytest.mark.financial]


def _shift(period: str, months: int) -> str:
    """YYYY-MM shifted by `months` (12-month arithmetic)."""
    year, month = int(period[:4]), int(period[5:7])
    index = year * 12 + (month - 1) + months
    return "%04d-%02d" % (index // 12, index % 12 + 1)


def _month_date(period: str, day: int = 5) -> date:
    return date(int(period[:4]), int(period[5:7]), day)


def _return_for(ctx, period: str):
    return ctx.as_(ctx.acct)[RET].create({"period": period})


def _file_input_excess_period(ctx):
    """Period 1: output 0.00, input 900.00. It must file at net 0.00 and
    carry 900.00 as closing credit. Returns the filed return."""
    _entry(ctx, [(ctx.vat_in, 900.0, 0.0), (ctx.ap, 0.0, 900.0)])
    _credit(ctx, vat_amount=900.0)
    ret = _vat_return(ctx)
    ret.with_user(ctx.acct).action_prepare()
    assert (ret.input_vat, ret.net_payable, ret.closing_credit) == (900.0, 0.0, 900.0)
    ret.with_user(ctx.filer).action_file_online(client=StubEvat())
    assert ret.state == "filed"
    return ret


def test_a_input_exceeds_output_files_zero_and_carries_the_excess(c):  # noqa: F811
    """FR-TAX-018: the refund position is held as closing credit — never as a
    negative payable the challan would refuse."""
    _entry(c, [(c.vat_in, 900.0, 0.0), (c.ap, 0.0, 900.0)])
    _credit(c, vat_amount=900.0)
    ret = _vat_return(c)
    ret.with_user(c.acct).action_prepare()

    assert (ret.output_vat, ret.input_vat) == (0.0, 900.0)
    assert (ret.opening_credit, ret.credit_used) == (0.0, 0.0)  # first period
    assert ret.net_payable == 0.0  # not -900.00
    assert ret.closing_credit == 900.0
    assert ret.nil_return is False  # there WAS input activity

    ret.with_user(c.filer).action_file_online(client=StubEvat())
    assert ret.state == "filed"
    assert ret.closing_credit == 900.0  # filing neither loses nor changes it


def test_b_next_period_consumes_min_and_carries_the_remainder(c):  # noqa: F811
    """credit_used = min(opening 900, output 500 - input 0) = 500; the rest
    (400) is carried forward."""
    first = _file_input_excess_period(c)
    assert first.closing_credit == 900.0

    nxt = _shift(c.period, 1)
    _reg(c, 3333.33, 500.0, invoice_date=_month_date(nxt))
    ret = _return_for(c, nxt)
    ret.with_user(c.acct).action_prepare()

    assert (ret.opening_credit, ret.output_vat, ret.input_vat) == (900.0, 500.0, 0.0)
    assert ret.credit_used == 500.0  # min(900, 500)
    assert ret.net_payable == 0.0
    assert ret.closing_credit == 400.0


def test_c_tampered_opening_credit_is_refused_naming_both(c):  # noqa: F811
    """AC-26: the opening balance must equal the last filed return's closing
    balance. A tampered 950.00 against the filed 900.00 is refused."""
    first = _file_input_excess_period(c)
    assert first.closing_credit == 900.0

    nxt = _shift(c.period, 1)
    ret = _return_for(c, nxt)
    ret.with_user(c.acct).action_prepare()
    assert ret.opening_credit == 900.0

    # arrangement: a legacy/tampered balance written past the workflow
    ret.sudo().write({"opening_credit": 950.0})
    with pytest.raises(UserError, match=r"950\.00.*900\.00"):
        ret.with_user(c.filer).action_file_online(client=StubEvat())
    assert ret.state == "prepared"


def test_d_nil_period_files_and_passes_credit_unchanged(c):  # noqa: F811
    """A mandatory NIL return with no output and no input still files, and the
    carried credit is untouched."""
    first = _file_input_excess_period(c)
    assert first.closing_credit == 900.0

    nxt = _shift(c.period, 1)
    ret = _return_for(c, nxt)
    ret.with_user(c.acct).action_prepare()

    assert ret.nil_return is True
    assert (ret.opening_credit, ret.credit_used) == (900.0, 0.0)
    assert (ret.net_payable, ret.closing_credit) == (0.0, 900.0)

    ret.with_user(c.filer).action_file_online(client=StubEvat())
    assert ret.state == "filed"
    assert ret.closing_credit == 900.0


def test_e_ordinary_input_below_output_is_unchanged(c):  # noqa: F811
    """No prior filed return, input 900 below output 4500: exactly today's
    result — net 3600, no credit consumed or created."""
    _reg(c, 30000.0, 4500.0)
    _credit(c, vat_amount=900.0)
    ret = _vat_return(c)
    ret.with_user(c.acct).action_prepare()

    assert (ret.output_vat, ret.input_vat) == (4500.0, 900.0)
    assert (ret.opening_credit, ret.credit_used) == (0.0, 0.0)
    assert ret.net_payable == 3600.0  # 4500 - 900, unchanged
    assert ret.closing_credit == 0.0


def test_f_vat_challan_settles_the_post_credit_net(c):  # noqa: F811
    """M51-11 + FR-TAX-018: the challan liability reads the return's
    post-credit net (3600), never the raw output - input (4500)."""
    _file_input_excess_period(c)

    nxt = _shift(c.period, 1)
    _reg(c, 30000.0, 4500.0, invoice_date=_month_date(nxt))
    ret = _return_for(c, nxt)
    ret.with_user(c.acct).action_prepare()

    assert (ret.opening_credit, ret.credit_used) == (900.0, 900.0)
    assert ret.net_payable == 3600.0
    assert ret.net_payable_after_vds == 3600.0

    ch = c.as_(c.acct)["fix.tax.challan"].create(
        {
            "challan_no": "CH-VAT-CREDIT-1",
            "challan_date": _month_date(nxt),
            "tax_kind": "vat",
            "amount": 3600.0,
            "vat_return_id": ret.id,
        }
    )
    assert ch.liability_total == 3600.0


def test_g_credit_fields_are_workflow_guarded(c):  # noqa: F811
    """A form cannot type the credit position: the fields move only through
    Prepare (the guarded-mixin token idiom)."""
    ret = _vat_return(c)
    _refused(
        ret.with_user(c.acct).write,
        {"opening_credit": 1.0, "credit_used": 1.0, "closing_credit": 1.0},
        match="cannot be set directly",
    )
