# fix.ap.takeon — lifecycle of the legacy 200101 AP register take-on
# (accounts_payable report 2026-11-09 §5.4): stage -> validate -> post ->
# rollback, on a miniature of the real export's shape (title/total/filler
# header rows, text cells, parenthetical voucher refs, a 'Total' footer).
from __future__ import annotations

import base64
import io
from decimal import Decimal

import pytest
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

D = Decimal

REGISTER_ROWS = [
    # (date, journal_entry, branch, company, created_by, created_on, debit, credit, balance)
    (
        "2026-10-17",
        "PPBLM/2026/00296 (INV-MSNHO-2026-000127)",
        "1000Fix Services Ltd.",
        "1000Fix Services Limited",
        "Md. Tanjin Ahmed Rabby",
        "2026-10-17 13:03:52",
        "72300",
        "0",
        "72300",
    ),
    (
        "2026-10-17",
        "PPBLM/2026/00295",
        "1000Fix Services Ltd.",
        "1000Fix Services Limited",
        "Md. Tanjin Ahmed Rabby",
        "2026-10-17 12:57:38",
        "260500",
        "0",
        "260500",
    ),
    (
        "2026-04-23",
        "PABBLB/2026/00001",
        "Sony-Smart Service Operation",
        "1000Fix Services Limited",
        "M. Sayed Raihan",
        "2026-04-23 10:00:00",
        "125000",
        "0",
        "125000",
    ),
    (
        "2026-04-16",
        "PPBLM/2026/00043",
        "1000Fix Services Ltd.",
        "1000Fix Services Limited",
        "Md. Tanjin Ahmed Rabby",
        "2026-04-16 09:00:00",
        "0",
        "0",
        "0",
    ),
    # duplicate of voucher 295 (quarantined at validate)
    (
        "2026-10-17",
        "PPBLM/2026/00295",
        "1000Fix Services Ltd.",
        "1000Fix Services Limited",
        "Md. Tanjin Ahmed Rabby",
        "2026-10-17 12:57:38",
        "1000",
        "0",
        "1000",
    ),
    # identity failure (quarantined at validate)
    (
        "2026-07-14",
        "PPBLM/2026/00135",
        "1000Fix Services Ltd.",
        "1000Fix Services Limited",
        "Md. Tanjin Ahmed Rabby",
        "2026-07-14 15:40:28",
        "500",
        "0",
        "999",
    ),
]
READY_TOTAL = Decimal("457800")  # 72,300 + 260,500 + 125,000


def _register_xlsx():
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "200101 Account Payable"
    ws.append(["Ledger Statement: 200101 Account Payable"])
    ws.append(["Total Records: %d" % len(REGISTER_ROWS)])
    ws.append(["╖"])
    ws.append(
        [
            "Date",
            "Journal Entry",
            "Branch",
            "Company",
            "Created by",
            "Created on",
            "Debit",
            "Credit",
            "Balance",
        ]
    )
    for row in REGISTER_ROWS:
        ws.append(list(row))
    ws.append(["Total", None, None, None, None, None, None, None, None])
    buf = io.BytesIO()
    wb.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


@pytest.fixture()
def batch(odoo_env):
    return odoo_env["fix.ap.takeon.batch"].create(
        {
            "name": "TEST AP register take-on",
            "import_ref": "AP-TEST",
            "legacy_account_code": "200101",
            "takeon_date": "2026-11-01",
            "source_file": _register_xlsx(),
            "source_filename": "200101_test.xlsx",
        }
    )


class TestApTakeon:
    def test_stage_parses_register_and_skips_footer(self, odoo_env, batch):
        batch.action_stage()
        assert batch.state == "staged"
        assert batch.line_count == len(REGISTER_ROWS)
        first = batch.line_ids.filtered(lambda ln: ln.row_no == 1)
        assert first.legacy_ref == "PPBLM/2026/00296"
        assert first.source_ref_note == "INV-MSNHO-2026-000127"
        assert first.debit == 72300.0 and first.balance == 72300.0
        sony = batch.line_ids.filtered(lambda ln: ln.legacy_ref == "PABBLB/2026/00001")
        assert sony.legacy_branch == "Sony-Smart Service Operation"
        assert str(first.legacy_date) == "2026-10-17"
        # no line carries the footer
        assert not batch.line_ids.filtered(lambda ln: ln.legacy_ref == "Total")

    def test_validate_quarantines_zero_duplicate_identity(self, odoo_env, batch):
        batch.action_stage()
        batch.action_validate()
        assert batch.state == "validated"
        quarantined = batch.line_ids.filtered(lambda ln: ln.line_state == "quarantined")
        assert len(quarantined) == 3
        notes = " | ".join(quarantined.mapped("notes"))
        assert "zero-amount" in notes
        assert "duplicate voucher ref" in notes
        assert "!=" in notes
        ready = batch.line_ids.filtered(lambda ln: ln.line_state == "ready")
        assert len(ready) == 3
        assert set(ready.mapped("legacy_reference")) == {
            "AP:PPBLM/2026/00296",
            "AP:PPBLM/2026/00295",
            "AP:PABBLB/2026/00001",
        }
        assert D(str(batch.total_open)) == READY_TOTAL

    def test_post_writes_balanced_voucher_level_entry(self, odoo_env, batch):
        batch.action_stage()
        batch.action_validate()
        batch.action_post()
        assert batch.state == "posted"
        move = batch.posted_move_id
        assert move.state == "posted" and move.journal_id.code == "MIG"
        # every ready voucher is one credit line + exactly one contra line
        voucher_lines = move.line_ids.filtered(
            lambda ln: ln.name.startswith("Legacy AP take-on ") and "contra" not in ln.name
        )
        assert len(voucher_lines) == 3
        # the register's debits are payables: they post as CREDITS (§2.4)
        assert all(ln.credit > 0 and ln.debit == 0 for ln in voucher_lines)
        assert D(str(sum(voucher_lines.mapped("credit")))) == READY_TOTAL
        contra_lines = move.line_ids - voucher_lines
        assert len(contra_lines) == 1
        assert D(str(contra_lines[0].debit)) == READY_TOTAL
        assert D(str(sum(move.line_ids.mapped("debit")))) == D(
            str(sum(move.line_ids.mapped("credit")))
        )
        # dedicated non-reconcileable legacy control account, not the payable control
        assert voucher_lines.mapped("account_id").ensure_one().account_type == "liability_current"
        assert not voucher_lines.mapped("account_id").reconcile
        # every line kept its voucher identity
        assert set(voucher_lines.mapped("name")) == {
            "Legacy AP take-on PPBLM/2026/00296",
            "Legacy AP take-on PPBLM/2026/00295",
            "Legacy AP take-on PABBLB/2026/00001",
        }
        # the governed funnel logged the posting
        log = odoo_env["fix.journal.posting.log"].search(
            [("source_ref", "like", "AP-TEST AP register take-on")]
        )
        assert len(log) == 1 and log.move_id == move
        # lines flipped to posted; counts follow
        assert batch.posted_count == 3 and batch.quarantined_count == 3

    def test_double_post_refused(self, odoo_env, batch):
        batch.action_stage()
        batch.action_validate()
        batch.action_post()
        with pytest.raises(UserError):
            batch.action_post()

    def test_rollback_mirrors_and_requeues(self, odoo_env, batch):
        batch.action_stage()
        batch.action_validate()
        batch.action_post()
        move = batch.posted_move_id
        batch.action_rollback()
        assert batch.state == "rolled_back"
        reversals = odoo_env["account.move"].search([("ref", "=", "ROLLBACK %s" % move.ref)])
        assert len(reversals) == 1
        assert D(str(sum(reversals.line_ids.mapped("debit")))) == D(
            str(sum(reversals.line_ids.mapped("credit")))
        )
        # voucher lines net to zero across the pair
        for ref in ("PPBLM/2026/00296", "PPBLM/2026/00295", "PABBLB/2026/00001"):
            pair = move.line_ids.filtered(
                lambda ln, _ref=ref: ln.name == "Legacy AP take-on %s" % _ref
            ) | reversals.line_ids.filtered(
                lambda ln, _ref=ref: ln.name == "AP take-on rollback: Legacy AP take-on %s" % _ref
            )
            assert D(str(sum(pair.mapped("credit")))) == D(str(sum(pair.mapped("debit"))))
        assert batch.posted_count == 0 and batch.ready_count == 3

    def test_post_refused_before_validate(self, odoo_env, batch):
        batch.action_stage()
        with pytest.raises(UserError):
            batch.action_post()
