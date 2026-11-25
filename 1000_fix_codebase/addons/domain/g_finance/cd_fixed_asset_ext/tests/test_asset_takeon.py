# cd_fixed_asset_ext tests — the legacy register take-on lane (2026-11-25).
# Live-ORM behaviour: stage/validate/post/rollback, the seam activation,
# opening accumulated depreciation carry, the no-double-charge rule, the
# remaining-life go-forward charge, quarantine and authority.
import base64
import io
import json
import uuid
from datetime import date

import pytest
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]


def balance(env, account):
    """Posted balance (debit - credit) of an account."""
    lines = env["account.move.line"].search(
        [("account_id", "=", account.id), ("parent_state", "=", "posted")]
    )
    return round(sum(lines.mapped("debit")) - sum(lines.mapped("credit")), 2)


HEADERS = [
    "SL",
    "COA Code",
    "COA Head",
    "Product Name (Short)",
    "Acquisition Date",
    "Financial Year",
    "Cost Centre / Branch",
    "Cost (Tk)",
    "Accumulated Depreciation (Tk)",
    "Net Book Value (Tk)",
    "Depreciation %",
    "Voucher / Move No",
]


def _xlsx(rows):
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Asset List"
    ws.append(HEADERS)
    for r in rows:
        ws.append(list(r))
    buf = io.BytesIO()
    wb.save(buf)
    return base64.b64encode(buf.getvalue())


def _row(sl, code, head, name, acq, branch, cost, accum, voucher="JV-00001-2020"):
    return [
        sl,
        code,
        head,
        name,
        acq,
        "FY 2020-21",
        branch,
        cost,
        accum,
        round(cost - accum, 2),
        (accum / cost if cost else 0),
        voucher,
    ]


@pytest.fixture
def takeon(m49):
    """A wired category crosswalk, a real branch on the fixture OU, and a
    batch factory staging arbitrary rows."""
    env = m49["env"]
    company = m49["company"]
    tag = uuid.uuid4().hex[:8]
    env["ir.config_parameter"].sudo().set_param(
        "cd_fixed_asset_ext.takeon.category_crosswalk",
        json.dumps({"TKEY": m49["category"].code, "Test Head": m49["category"].code}),
    )
    entity = env["fix.entity"].create(
        {
            "code": "TK%s" % tag[:6].upper(),
            "legal_name": "Take-on Test Entity %s" % tag,
            "company_id": company.id,
        }
    )
    branch = env["fix.branch"].create(
        {
            "code": "TB%s" % tag[:6].upper(),
            "name": "Take-on Branch %s" % tag,
            "entity_id": entity.id,
            "operating_unit_id": m49["ou"].id,
        }
    )

    def make_batch(rows, ref=None):
        return env["fix.asset.takeon.batch"].create(
            {
                "company_id": company.id,
                "source_file": _xlsx(rows),
                "source_filename": "test_register.xlsx",
                "import_ref": ref or "AST-%s" % tag,
                "takeon_date": date.today().replace(day=28),
                "contra_operating_unit_id": m49["ou"].id,
            }
        )

    return {**m49, "branch": branch, "tag": tag, "make_batch": make_batch}


def _good_rows(branch_name):
    return [
        _row(
            1,
            "TKEY",
            "Test Head",
            "Desktop PC",
            date(2020, 1, 15),
            branch_name,
            120000.0,
            40000.0,
            "JV-00001-2020",
        ),
        _row(
            2,
            "TKEY",
            "Test Head",
            "Laptop",
            date(2020, 6, 1),
            branch_name,
            60000.0,
            0.0,
            "JV-00002-2020",
        ),
    ]


class TestAssetTakeon:
    def test_stage_validate_post_capitalises_and_activates(self, takeon):
        env = takeon["env"]
        batch = takeon["make_batch"](_good_rows(takeon["branch"].name))
        batch.action_stage()
        assert batch.state == "staged"
        assert batch.line_count == 2
        batch.action_validate()
        assert batch.state == "validated"
        assert batch.ready_count == 2
        assert batch.quarantined_count == 0
        batch.action_post()
        assert batch.state == "posted"
        assert batch.posted_count == 2
        assets = batch.line_ids.mapped("asset_id")
        assert len(assets) == 2
        assert all(a.state == "active" for a in assets)
        a1 = batch.line_ids.filtered(lambda ln: ln.sl == 1).asset_id
        assert a1.gross == 120000.0
        assert a1.accumulated_depreciation == 40000.0
        assert a1.book_nbv == 80000.0
        assert a1.legacy_reference == "%s-SL-1" % batch.import_ref
        assert a1.takeon_batch_id == batch
        assert a1.seam_id.consumed
        # the GL carries cost, accum and the net on the contra
        cat = takeon["category"]
        assert balance(env, cat.asset_account_id) == 180000.0
        assert balance(env, cat.accumulated_account_id) == -40000.0
        contra = env["account.account"].search([("code", "=", "2.99.99.901")], limit=1)
        assert balance(env, contra) == -140000.0
        # external ids (MIG-03 idempotency keys)
        xid = env["ir.model.data"].search(
            [("module", "=", "__asset_takeon__"), ("name", "=", "a_%s_1" % batch.import_ref)]
        )
        assert xid.res_id == a1.id
        # opening runs posted, GL carried by the accum entry (no second posting)
        assert len(batch.run_ids) == 2
        assert all(r.state == "posted" for r in batch.run_ids)
        book_run = batch.run_ids.filtered(lambda r: r.book == "book")
        assert book_run.total_amount == 40000.0
        assert book_run.asset_count == 1  # the zero-accum asset carries no opening line

    def test_next_month_charges_remaining_life_and_never_double(self, takeon):
        env = takeon["env"]
        batch = takeon["make_batch"](_good_rows(takeon["branch"].name))
        batch.action_stage()
        batch.action_validate()
        batch.action_post()
        a1 = batch.line_ids.filtered(lambda ln: ln.sl == 1).asset_id
        a1.life_months = 60  # remaining 59 + the opening month
        # the take-on month is already charged: a run for it skips the asset
        period = batch.takeon_date.replace(day=1)
        run = env["fix.asset.depreciation.run"].create(
            {"company_id": takeon["company"].id, "book": "book", "period_start": period}
        )
        run.action_compute()
        assert a1 not in run.line_ids.asset_id
        # the zero-accum asset starts in its take-on month
        a2 = batch.line_ids.filtered(lambda ln: ln.sl == 2).asset_id
        assert a2 in run.line_ids.asset_id
        # the go-forward charge re-spreads NBV over the remaining months
        next_month = date(period.year + (period.month == 12), period.month % 12 + 1, 1)
        assert a1._book_amount(next_month) == round(80000.0 / 59, 2)

    def test_quarantine_bad_rows_and_post_the_rest(self, takeon):
        branch = takeon["branch"].name
        rows = [
            *_good_rows(branch),
            _row(
                3, "TKEY", "Test Head", "Bad identity", date(2020, 1, 1), branch, 100.0, 150.0
            ),  # accum > cost
            _row(
                4,
                "TKEY",
                "Test Head",
                "Unknown branch",
                date(2020, 1, 1),
                "Nowhere CSC",
                5000.0,
                1000.0,
            ),
            _row(1, "TKEY", "Test Head", "Duplicate SL", date(2020, 1, 1), branch, 900.0, 100.0),
        ]
        batch = takeon["make_batch"](rows)
        batch.action_stage()
        batch.action_validate()
        assert batch.ready_count == 2
        assert batch.quarantined_count == 3
        reasons = batch.line_ids.filtered(lambda ln: ln.state == "quarantined").mapped(
            "reject_reason"
        )
        assert any("accumulated" in r for r in reasons)
        assert any("unresolved" in r for r in reasons)
        assert any("duplicate" in r for r in reasons)
        batch.action_post()
        assert batch.posted_count == 2

    def test_second_takeon_of_same_key_is_quarantined(self, takeon):
        rows = _good_rows(takeon["branch"].name)
        b1 = takeon["make_batch"](rows, ref="AST-DUP-%s" % takeon["tag"])
        b1.action_stage()
        b1.action_validate()
        b1.action_post()
        b2 = takeon["make_batch"](rows, ref="AST-DUP-%s" % takeon["tag"])
        b2.action_stage()
        b2.action_validate()
        assert b2.ready_count == 0
        assert b2.quarantined_count == 2
        assert all(
            "already taken on" in ln.reject_reason
            for ln in b2.line_ids.filtered(lambda ln: ln.state == "quarantined")
        )

    def test_rollback_mirrors_and_retires_everything(self, takeon):
        env = takeon["env"]
        batch = takeon["make_batch"](_good_rows(takeon["branch"].name))
        batch.action_stage()
        batch.action_validate()
        batch.action_post()
        cat = takeon["category"]
        contra = env["account.account"].search([("code", "=", "2.99.99.901")], limit=1)
        batch.action_rollback()
        assert batch.state == "rolled_back"
        assert batch.posted_count == 0
        assert env["fix.fixed.asset"].search_count([("takeon_batch_id", "=", batch.id)]) == 0
        assert env["fix.fixed.asset.seam"].search_count([("name", "like", batch.import_ref)]) == 0
        assert (
            env["fix.asset.depreciation.run"].search_count([("id", "in", batch.run_ids.ids)]) == 0
        )
        assert (
            env["ir.model.data"].search_count(
                [("module", "=", "__asset_takeon__"), ("name", "like", "a_%s" % batch.import_ref)]
            )
            == 0
        )
        assert balance(env, cat.asset_account_id) == 0.0
        assert balance(env, cat.accumulated_account_id) == 0.0
        assert balance(env, contra) == 0.0
        assert all(ln.state == "ready" for ln in batch.line_ids)

    def test_posting_needs_accounting_administrator(self, takeon):
        batch = takeon["make_batch"](_good_rows(takeon["branch"].name))
        batch.action_stage()
        batch.action_validate()
        with pytest.raises(UserError):
            batch.with_user(takeon["users"]["accountant"]).action_post()

    def test_unwired_category_fails_closed(self, takeon):
        takeon["category"].journal_id = False
        batch = takeon["make_batch"](_good_rows(takeon["branch"].name))
        batch.action_stage()
        batch.action_validate()
        with pytest.raises(UserError):
            batch.action_post()
