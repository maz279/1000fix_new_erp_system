# Opening balances taken on from the legacy system (journal MIG, one line per
# party on the AR / AP control) are part of every party's balance. The M20
# ageing, the per-customer sub-ledger vs GL reconciliation, the brand ageing,
# the customer statement, the ageing snapshot and the live ageing grid used
# to read fix.ar.invoice only, so a customer whose whole balance was taken on
# was invisible in ageing and showed a false "difference" against the GL
# (fix_real: 153.86M over 956 customers). The M52 AP ageing had the same gap
# for the 130.04M payable take-on. E3-20 (the Mushak 6.3 row cited AR/<id>, not
# the invoice number) is at the end.
from datetime import date
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo.addons.cd_billing_engine.models.fix_ar_engine import compute_customer_statement
from odoo.addons.cd_billing_engine.tests.test_a08_m20_controls import (
    as_,
    c,  # noqa: F401 - fixture
    c_raw,  # noqa: F401 - fixture
    inv,
)

pytestmark = [pytest.mark.financial]

TAKEON = date(2026, 11, 8)
AS_OF = "2026-11-12"
OPENING = "Opening balance (take-on 2026-11-08)"


def _takeon(c, partner, amount, account=None, when=TAKEON):  # noqa: F811
    """Post a legacy take-on line for `partner` on the AR control (or
    `account`), contra on a take-on contra account, in journal MIG."""
    env = c.env
    Journal = env["account.journal"]
    mig = Journal.search([("code", "=", "MIG"), ("company_id", "=", c.company.id)], limit=1)
    if not mig:
        mig = Journal.create(
            {
                "name": "Legacy Take-on",
                "code": "MIG",
                "type": "general",
                "company_id": c.company.id,
                # after the general journal the AR engine posts on (fix_real: MISC is 9)
                "sequence": 99,
            }
        )
    contra = getattr(c, "takeon_contra", None)
    if not contra:
        contra = c.takeon_contra = (
            env["account.account"]
            .with_company(c.company)
            .create(
                {
                    "name": "Legacy Ledger Take-on Contra",
                    "code": "299901",
                    "account_type": "liability_current",
                    "company_ids": [(6, 0, c.company.ids)],
                }
            )
        )
    control = account or c.acc["ar"]
    debit, credit = (amount, 0.0) if amount > 0 else (0.0, -amount)
    move = env["account.move"].create(
        {
            "journal_id": mig.id,
            "company_id": c.company.id,
            "date": when,
            "move_type": "entry",
            "ref": "TAKEON test",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": control.id,
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
                    {
                        "account_id": contra.id,
                        "name": "contra",
                        "debit": credit,
                        "credit": debit,
                    },
                ),
            ],
        }
    )
    move.action_post()
    return move


def _m20():
    from odoo.addons.cd_p03_portal.controllers.a08 import m20

    return m20


# ---------------------------------------------------------------- M20 reports


def test_ageing_by_segment_carries_the_takeon_as_its_own_line(c):  # noqa: F811
    _takeon(c, c.customer2, 5000.0)
    inv(c, c.acct, 1000.0)  # an issued invoice for c.customer: 1,150 open
    out = _m20().ageing_by_segment(as_(c, c.acct), date_to=AS_OF)
    opening = [r for r in out["rows"] if OPENING in r["segment"]]
    assert len(opening) == 1, out["rows"]
    row = opening[0]
    # aged from the take-on date: 4 days past it on 12 Nov
    assert (row["invoices"], row["d1_30"], row["total"]) == (0, 5000.0, 5000.0)
    assert out["totals"]["total"] == 6150.0


def test_recon_counts_the_takeon_in_the_customers_subledger(c):  # noqa: F811
    _takeon(c, c.customer2, 5000.0)  # take-on only: no invoice at all
    _takeon(c, c.customer, 3000.0)
    inv(c, c.acct, 10000.0)  # 11,500 on an invoice
    out = _m20().ar_subledger_gl_recon(as_(c, c.acct))
    by = {r["customer"]: r for r in out["rows"]}
    only = by[c.customer2.name]
    assert (only["takeon_open"], only["subledger"], only["gl"], only["difference"]) == (
        5000.0,
        5000.0,
        5000.0,
        0.0,
    )
    both = by[c.customer.name]
    assert (both["invoices_open"], both["takeon_open"], both["subledger"], both["gl"]) == (
        11500.0,
        3000.0,
        14500.0,
        14500.0,
    )
    assert both["difference"] == 0.0
    assert "0 customer(s) differ" in out["title"]
    assert out["totals"]["takeon_open"] == 8000.0
    assert out["labels"]["takeon_open"].startswith("Opening Balance (take-on")


def test_a_party_without_its_stored_commercial_partner_is_still_named(c):  # noqa: F811
    """fix_real: 8 AR and 3 AP take-on parties were raw-loaded with
    commercial_partner_id NULL and fell into "(no customer on the GL line)"."""
    raw = c.env["res.partner"].create({"name": "TKO Raw %s" % c.tag})
    _takeon(c, raw, 900.0)
    c.env.cr.execute("UPDATE res_partner SET commercial_partner_id = NULL WHERE id = %s", [raw.id])
    c.env.invalidate_all()
    out = _m20().ar_subledger_gl_recon(as_(c, c.acct))
    row = next(r for r in out["rows"] if r["takeon_open"] == 900.0)
    assert (row["customer"], row["gl"], row["difference"]) == (raw.name, 900.0, 0.0)


def test_a_paid_down_takeon_shows_only_what_is_still_open(c):  # noqa: F811
    move = _takeon(c, c.customer2, 5000.0)
    line = move.line_ids.filtered(lambda ln: ln.account_id == c.acc["ar"])
    # 2,000 received and matched against the take-on line
    pay = c.env["account.move"].create(
        {
            "journal_id": c.journal.id,
            "company_id": c.company.id,
            "date": date(2026, 11, 10),
            "line_ids": [
                (0, 0, {"account_id": c.acc["cash"].id, "debit": 2000.0, "name": "cash"}),
                (
                    0,
                    0,
                    {
                        "account_id": c.acc["ar"].id,
                        "partner_id": c.customer2.id,
                        "credit": 2000.0,
                        "name": "receipt",
                    },
                ),
            ],
        }
    )
    pay.action_post()
    (line | pay.line_ids.filtered(lambda ln: ln.account_id == c.acc["ar"])).reconcile()
    out = _m20().ageing_by_segment(as_(c, c.acct), date_to=AS_OF)
    row = next(r for r in out["rows"] if OPENING in r["segment"])
    assert row["total"] == 3000.0


def test_brand_ageing_shows_a_brands_takeon_only(c):  # noqa: F811
    brand = c.env["fix.brand"].create({"name": "TKO Brand %s" % c.tag, "code": "TKO%s" % c.tag})
    oem = c.env["res.partner"].create({"name": "TKO OEM %s" % c.tag, "ref": brand.code})
    _takeon(c, oem, 7000.0)
    _takeon(c, c.customer2, 5000.0)  # an ordinary customer: never a brand receivable
    out = _m20().brand_receivable_ageing(as_(c, c.acct), date_to=AS_OF)
    assert [(r["invoice"], r["customer"], r["residual"], r["bucket"]) for r in out["rows"]] == [
        (OPENING, oem.name, 7000.0, "d1_30")
    ]
    assert out["totals"]["residual"] == 7000.0


# ---------------------------------------------------------------- statement


def test_the_customer_statement_starts_from_the_takeon(c):  # noqa: F811
    _takeon(c, c.customer2, 5000.0)
    env = as_(c, c.acct)
    # the window holds the take-on date: it is the statement's first line
    stmt = compute_customer_statement(env, c.customer2.id, date(2026, 11, 1), date(2026, 11, 30))
    assert stmt["opening"] == 0.0
    first = stmt["rows"][0]
    assert (first["kind"], first["detail"], first["charge"]) == ("takeon", OPENING, 5000.0)
    assert stmt["closing"] == 5000.0
    # a window after the take-on date opens on it
    stmt = compute_customer_statement(env, c.customer2.id, date(2026, 11, 10), date(2026, 11, 30))
    assert (stmt["opening"], stmt["rows"], stmt["closing"]) == (5000.0, [], 5000.0)


# ---------------------------------------------------------------- snapshot + live grid


def test_the_ageing_snapshot_captures_the_takeon(c):  # noqa: F811
    _takeon(c, c.customer2, 5000.0)
    snap = as_(c, c.acct)["fix.ar.aging.snapshot"].create({"company_id": c.company.id})
    snap.action_capture(as_of=date(2026, 11, 12))
    line = snap.line_ids.filtered(lambda ln: ln.customer_id == c.customer2)
    assert (line.current, line.d1_30, snap.total_open) == (0.0, 5000.0, 5000.0)


def test_the_live_ageing_grid_lists_the_takeon(c):  # noqa: F811
    from odoo.addons.cd_p03_portal.controllers import p03_ar_api

    _takeon(c, c.customer2, 5000.0)
    with mock.patch.object(p03_ar_api, "request", SimpleNamespace(env=as_(c, c.acct))):
        out = p03_ar_api.P03ArApiController().ar_aging()
    row = next(r for r in out["live"] if r["customer"].startswith(c.customer2.name))
    assert OPENING in row["customer"]
    assert sum(row[k] for k in ("current", "d1_30", "d31_60", "d61_90", "d90_plus")) == 5000.0


# ---------------------------------------------------------------- M52 AP ageing


def test_ap_ageing_carries_the_payable_takeon(c):  # noqa: F811
    from odoo.addons.cd_p03_portal.controllers.a08 import m52

    payable = (
        c.env["account.account"]
        .with_company(c.company)
        .create(
            {
                "name": "Account Payable",
                "code": "200101",
                "account_type": "liability_payable",
                "company_ids": [(6, 0, c.company.ids)],
            }
        )
    )
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_gl_ext.ledger_takeon.payable_account_code", "200101"
    )
    vendor = c.env["res.partner"].create({"name": "TKO Vendor %s" % c.tag})
    _takeon(c, vendor, -8000.0, account=payable)
    out = m52.ap_ageing(as_(c, c.acct), date_to=AS_OF)
    row = next(r for r in out["rows"] if r["vendor"].startswith(vendor.name))
    assert OPENING in row["vendor"]
    assert (row["d1_30"], row["total"]) == (8000.0, 8000.0)
    assert out["totals"]["total"] == 8000.0


# ---------------------------------------------------------------- E3-20


def test_e3_20_the_mushak_row_cites_the_invoice_number(c):  # noqa: F811
    i = inv(c, c.acct, 1000.0)
    assert i.name and i.name != "New" and not i.name.startswith("AR/")
    assert i.mushak_id.invoice_ref == i.name
