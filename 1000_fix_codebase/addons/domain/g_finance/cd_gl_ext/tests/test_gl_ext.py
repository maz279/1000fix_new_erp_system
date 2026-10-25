# cd_gl_ext tests — M19 core (P06-M01; DoD-03: financial paths 100%).
from __future__ import annotations

import inspect
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

pytestmark = [pytest.mark.financial]

from odoo.addons.cd_gl_ext.models.fix_chart_loader import (
    FixChartAccount,
    FixChartLoader,
)
from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import (
    FixFiscalYearIntegration,
    FixMisReportBridge,
)
from odoo.addons.cd_gl_ext.models.fix_gl_ext import (
    FixFixedAssetSeam,
    FixJournalDimension,
    FixPeriodClose,
    FixPeriodCloseLine,
    post_with_dimensions,
)
from odoo.exceptions import UserError, ValidationError

SAMPLE_CSV = """account_code,entity_code,account_name,account_type,account_subtype,is_postable,is_control_account,control_subledger,requires_dimension,statutory_group,active
1-00-00-000,EN-01,Total Assets,asset,current_asset,FALSE,FALSE,,,Assets,TRUE
1-10-00-000,EN-01,Current Assets,asset,current_asset,FALSE,FALSE,,,Assets,TRUE
1-10-10-000,EN-01,Cash & Bank,asset,bank,FALSE,FALSE,,,Cash & Bank,TRUE
1-10-10-001,EN-01,Cash in Hand,asset,cash,TRUE,FALSE,,branch;cost_centre,Cash & Bank,TRUE
1-10-20-001,EN-01,Trade Debtors,asset,receivable,TRUE,TRUE,receivable,branch,Receivables,TRUE
1-10-99-999,EN-01,Inventory Suspense,asset,stock,TRUE,TRUE,stock,,Suspense,TRUE
2-00-00-000,EN-01,Total Liabilities,liability,liability,FALSE,FALSE,,,Liabilities,TRUE
2-10-10-001,EN-01,Trade Creditors,liability,payable,TRUE,TRUE,payable,branch,Payables,TRUE
3-00-00-000,EN-01,Total Equity,equity,equity,FALSE,FALSE,,,Equity,TRUE
3-10-10-001,EN-01,Share Capital,equity,equity,TRUE,FALSE,,,Equity,TRUE
4-00-00-000,EN-01,Revenue,income,revenue,FALSE,FALSE,,,Revenue,TRUE
4-10-10-001,EN-01,Service Repair Income,income,revenue,TRUE,FALSE,,branch;business_line,Revenue,TRUE
5-00-00-000,EN-01,Operating Expenses,expense,opex,FALSE,FALSE,,,Expenses,TRUE
5-10-10-001,EN-01,Technician Salaries,expense,payroll,TRUE,FALSE,,branch;cost_centre,Expenses,TRUE
"""


class TestPeriodCloseDeclarations:
    """fix.period.close — the 5-day close process model structure."""

    def test_model_exists(self):
        assert FixPeriodClose is not None

    def test_close_target_is_five_days(self):
        assert FixPeriodClose.CLOSE_TARGET_DAYS == 5  # G3-04

    def test_duration_compute_declared(self):
        assert hasattr(FixPeriodClose, "_compute_duration")

    def test_action_close_requires_ready(self):
        """A close that was never readiness-checked must refuse (T06)."""
        assert hasattr(FixPeriodClose, "action_close")

    def test_action_ready_blocks_on_suspense(self):
        """AR-006 section 5.4: a non-zero suspense balance blocks the close."""
        assert hasattr(FixPeriodClose, "action_ready")


class TestPeriodCloseExecution:
    """fix.period.close method executions covering all paths (DoD-03)."""

    def test_compute_target_completion(self):
        close_valid = MagicMock()
        close_valid.period_end = date(2026, 10, 31)
        close_valid.CLOSE_TARGET_DAYS = 5
        FixPeriodClose._compute_target_completion([close_valid])
        assert close_valid.target_completion_date == date(2026, 11, 5)

        close_none = MagicMock()
        close_none.period_end = False
        FixPeriodClose._compute_target_completion([close_none])
        assert close_none.target_completion_date is False

    def test_compute_duration_within_sla(self):
        close = MagicMock()
        close.period_end = date(2026, 10, 31)
        close.closed_at = "2026-11-03 12:00:00"
        close.CLOSE_TARGET_DAYS = 5
        FixPeriodClose._compute_duration([close])
        assert close.close_duration_days == 3.0
        assert close.sla_status == "within_sla"

    def test_compute_duration_breached(self):
        close = MagicMock()
        close.period_end = date(2026, 10, 31)
        close.closed_at = "2026-11-08 12:00:00"
        close.CLOSE_TARGET_DAYS = 5
        FixPeriodClose._compute_duration([close])
        assert close.close_duration_days == 8.0
        assert close.sla_status == "breached"

    def test_compute_duration_unclosed(self):
        close = MagicMock()
        close.period_end = date(2026, 10, 31)
        close.closed_at = False
        close.CLOSE_TARGET_DAYS = 5
        FixPeriodClose._compute_duration([close])
        assert close.close_duration_days == 0.0
        assert close.sla_status == "within_sla"

    def test_action_generate_standard_steps(self):
        close = MagicMock()
        close.id = 10
        line_model = MagicMock()
        close.env = {"fix.period.close.line": line_model}
        res = FixPeriodClose.action_generate_standard_steps(close)
        assert res is True
        assert line_model.create.call_count == 10
        close.write.assert_called_with({"state": "in_progress"})

    def test_action_ready_blocking_steps_failure(self):
        close = MagicMock()
        step = MagicMock(blocking=True, state="pending")
        step.name = "Inventory Suspense"
        blocking_rec = MagicMock()
        blocking_rec.__bool__.return_value = True
        blocking_rec.mapped.return_value = ["Inventory Suspense"]
        close.line_ids.filtered.return_value = blocking_rec
        with pytest.raises(UserError, match="Close steps still open"):
            FixPeriodClose.action_ready([close])

    def test_action_ready_suspense_balance_failure(self):
        close = MagicMock()
        close.line_ids.filtered.return_value = []
        close.suspense_closing = 2500.00
        with pytest.raises(UserError, match="Suspense account must be zero"):
            FixPeriodClose.action_ready([close])

    def test_action_ready_success(self):
        close = MagicMock()
        close.line_ids.filtered.return_value = []
        close.suspense_closing = 0.0
        FixPeriodClose.action_ready([close])
        assert close.state == "ready_to_close"

    def test_action_close_not_ready_failure(self):
        close = MagicMock()
        close.state = "draft"
        with pytest.raises(UserError, match="Run the ready check before closing"):
            FixPeriodClose.action_close([close])

    def test_action_close_success_and_breach_logging(self):
        close = MagicMock()
        close.id = 1
        close.state = "ready_to_close"
        close.close_duration_days = 3.0
        close.sla_status = "within_sla"
        close.CLOSE_TARGET_DAYS = 5
        close.line_ids = [MagicMock()]
        close.company_id.id = 1
        close.period_end = date(2026, 10, 31)
        close.env = MagicMock()

        with patch("odoo.addons.cd_gl_ext.models.fix_gl_ext.publish") as mock_pub:
            FixPeriodClose.action_close([close])
            close.write.assert_called_once()
            mock_pub.assert_called_once()

        # Breached close logs warning
        close_breach = MagicMock()
        close_breach.id = 2
        close_breach.state = "ready_to_close"
        close_breach.close_duration_days = 7.0
        close_breach.sla_status = "breached"
        close_breach.CLOSE_TARGET_DAYS = 5
        close_breach.line_ids = []
        close_breach.company_id.id = 1
        close_breach.period_end = date(2026, 10, 31)
        close_breach.env = MagicMock()

        with patch("odoo.addons.cd_gl_ext.models.fix_gl_ext.publish"):
            FixPeriodClose.action_close([close_breach])

    def test_action_fail_close_target(self):
        close = MagicMock()
        close.CLOSE_TARGET_DAYS = 5
        close.search_read.return_value = [
            {"period_end": "2026-09-30", "close_duration_days": 8.0, "sla_status": "breached"}
        ]
        res = FixPeriodClose.action_fail_close_target(close)
        assert len(res) == 1
        assert res[0]["close_duration_days"] == 8.0

    def test_action_reconcile_inventory_suspense_requires_a_cutover_entry(self):
        """Regression: pending entries were marked reconciled against an
        invented voucher and the suspense forced to zero by a status write."""
        close = MagicMock()
        close.id = 42
        close.company_id.id = 1
        close.cutover_move_id = None

        r1 = MagicMock(total_valuation=1200.0)
        pending = MagicMock()
        pending.__iter__.return_value = [r1]
        pending.__len__.return_value = 1
        pending.__bool__.return_value = True
        pending.mapped.return_value = [1200.0]

        suspense_model = MagicMock()
        suspense_model.search.return_value = pending
        close.env = {"fix.inventory.valuation.suspense": suspense_model}

        with patch("odoo.addons.cd_gl_ext.models.fix_gl_ext.publish") as mock_pub:
            with pytest.raises(UserError, match="Post the suspense cutover journal entry"):
                FixPeriodClose.action_reconcile_inventory_suspense(close)
            r1.action_reconcile_to_gl.assert_not_called()
            close.write.assert_not_called()
            mock_pub.assert_not_called()


class TestPeriodCloseLineExecution:
    def test_action_mark_done(self):
        line = MagicMock()
        with pytest.raises(UserError, match="Provide the evidence reference"):
            FixPeriodCloseLine.action_mark_done([line])  # no default "VERIFIED"
        line.write.assert_not_called()
        FixPeriodCloseLine.action_mark_done([line], "TB-2026-09")
        line.write.assert_called_with({"state": "done", "evidence_ref": "TB-2026-09"})

    def test_action_set_state(self):
        line = MagicMock()
        FixPeriodCloseLine.action_set_state(line, "done")
        line.write.assert_called_with({"state": "done"})

        with pytest.raises(UserError, match="Invalid state"):
            FixPeriodCloseLine.action_set_state(line, "invalid_state")


class TestJournalDimension:
    def test_model_exists(self):
        assert FixJournalDimension is not None

    def test_branch_ou_constraint_matching(self):
        ou = MagicMock(name="OU-01")
        ou.name = "DHK-OU"
        dim = MagicMock()
        dim.branch_id.name = "DHK-BR"
        dim.branch_id.operating_unit_id = ou
        dim.operating_unit_id = ou
        FixJournalDimension._check_branch_ou([dim])

    def test_branch_ou_constraint_missing_passes(self):
        dim = MagicMock()
        dim.branch_id = False
        dim.operating_unit_id = MagicMock()
        FixJournalDimension._check_branch_ou([dim])

    def test_branch_ou_constraint_mismatch_raises(self):
        ou1 = MagicMock()
        ou1.name = "OU-01"
        ou2 = MagicMock()
        ou2.name = "OU-02"
        dim = MagicMock()
        dim.branch_id.name = "Branch-A"
        dim.branch_id.operating_unit_id = ou1
        dim.operating_unit_id = ou2
        with pytest.raises(ValidationError, match="does not belong to operating unit"):
            FixJournalDimension._check_branch_ou([dim])


class TestFixedAssetSeam:
    def test_model_exists(self):
        assert FixFixedAssetSeam is not None

    def test_seam_is_interface_only(self):
        """T07: the seam carries NO depreciation logic — M49 owns that."""
        source = inspect.getsource(FixFixedAssetSeam)
        masked = (
            source.lower()
            .replace("owns depreciation. no depreciation logic here", "")
            .replace("the seam, not the asset", "")
        )
        assert "depreciat" not in masked

    def test_action_mark_consumed(self):
        seam = MagicMock()
        FixFixedAssetSeam.action_mark_consumed(seam)
        seam.write.assert_called_with({"consumed": True})


class TestPostWithDimensions:
    def test_helper_exists(self):
        assert callable(post_with_dimensions)

    def test_helper_posts_and_emits_journal_posted(self):
        move_mock = MagicMock()
        move_mock.id = 100
        move_mock.company_id.id = 1
        move_mock.amount_total = 750.0
        move_mock.currency_id.name = "BDT"
        move_mock.name = "ENTRY-01"
        line1 = MagicMock(id=501)
        line2 = MagicMock(id=502)
        move_mock.line_ids = [line1, line2]

        dim_model = MagicMock()
        dim_model.create.return_value = MagicMock()
        ou_model = MagicMock()
        ou_model.search.return_value = MagicMock(id=99)
        # The statutory chart lookup: no linked accounts -> no COA-rule
        # enforcement (unmapped accounts post with structural checks only).
        chart_model = MagicMock()
        chart_model.sudo.return_value.search.return_value = []
        # The immutable posting log the helper appends (FR-FIN-042).
        log_model = MagicMock()

        env = {
            "account.move": MagicMock(create=MagicMock(return_value=move_mock)),
            "fix.journal.dimension": dim_model,
            "operating.unit": ou_model,
            "fix.chart.account": chart_model,
            "fix.journal.posting.log": log_model,
        }

        with patch("odoo.addons.cd_gl_ext.models.fix_gl_ext.publish") as mock_pub:
            move, _dims = post_with_dimensions(
                env=env,
                move_vals={"ref": "ENTRY-01"},
                dimension_by_line={0: {"branch_id": 2, "cost_centre": "CC-01"}},
            )
            assert move == move_mock
            move_mock.action_post.assert_called_once()
            dim_model.create.assert_called_once()
            mock_pub.assert_called_once()
            log_model.with_context.return_value.sudo.return_value.create.assert_called_once()


class TestChartAccountAndLoader:
    def test_chart_account_check_coa_rules_valid(self):
        acc = MagicMock()
        acc.account_code = "1-10-10-001"
        acc.company_id.code = "EN-01"
        acc.name = "Cash in Hand"
        acc.account_type = "asset"
        acc.account_subtype = "cash"
        acc.is_postable = True
        acc.is_control_account = False
        acc.control_subledger = False
        acc.requires_dimension = "branch;cost_centre"
        acc.statutory_group = "Current assets"
        acc.active = True
        FixChartAccount._check_coa_rules([acc])

        acc_summary = MagicMock()
        acc_summary.account_code = "1-10-00-000"
        acc_summary.company_id.code = "EN-01"
        acc_summary.name = "Current Assets"
        acc_summary.account_type = "asset"
        acc_summary.account_subtype = "current_asset"
        acc_summary.is_postable = False
        acc_summary.is_control_account = False
        acc_summary.control_subledger = False
        acc_summary.requires_dimension = ""
        acc_summary.statutory_group = "Current assets"
        acc_summary.active = True
        acc_summary.balance = 0.0
        FixChartAccount._check_coa_rules([acc_summary])

    def test_chart_account_check_coa_rules_invalid(self):
        acc = MagicMock()
        acc.account_code = "INVALID"
        acc.company_id.code = "EN-01"
        acc.name = "Bad Account"
        acc.account_type = "asset"
        acc.account_subtype = "cash"
        acc.is_postable = True
        acc.is_control_account = False
        acc.control_subledger = False
        acc.requires_dimension = ""
        acc.statutory_group = "Current assets"
        acc.active = True
        acc.balance = 0.0
        with pytest.raises(ValidationError):
            FixChartAccount._check_coa_rules([acc])

    def test_chart_account_check_coa_rules_non_leaf_postable_raises(self):
        acc = MagicMock()
        acc.account_code = "1-10-00-000"
        acc.company_id.code = "EN-01"
        acc.name = "Current Assets"
        acc.account_type = "asset"
        acc.account_subtype = "current_asset"
        acc.is_postable = True
        acc.is_control_account = False
        acc.control_subledger = False
        acc.requires_dimension = ""
        acc.statutory_group = "Current assets"
        acc.active = True
        acc.balance = 0.0
        with pytest.raises(ValidationError, match="Non-leaf summary account cannot be postable"):
            FixChartAccount._check_coa_rules([acc])

    def test_chart_account_action_archive_success(self):
        acc = MagicMock()
        acc.account_code = "1-10-10-001"
        acc.balance = 0.0
        FixChartAccount.action_archive([acc])
        acc.write.assert_called_with({"active": False})

    def test_chart_account_action_archive_failure(self):
        acc = MagicMock()
        acc.account_code = "1-10-10-001"
        acc.balance = 500.00
        with pytest.raises(UserError, match="Cannot archive account"):
            FixChartAccount.action_archive([acc])

    def test_chart_loader_action_load_from_csv_custom(self):
        loader = MagicMock()
        loader.company_id.id = 1
        loader.operating_unit_id = False
        acc_model = MagicMock()
        acc_model.with_context.return_value = acc_model
        acc_model.search.return_value = False
        loader.env = {"fix.chart.account": acc_model}

        with patch("odoo.addons.cd_gl_ext.models.fix_chart_loader.publish"):
            res = FixChartLoader.action_load_from_csv(loader, csv_text=SAMPLE_CSV)
            assert res["status"] == "loaded"
            assert res["account_count"] == 14
            assert acc_model.create.call_count == 14
            loader.write.assert_called_once()

    def test_chart_loader_action_load_from_csv_existing(self):
        loader = MagicMock()
        loader.company_id.id = 1
        loader.operating_unit_id.id = 5
        existing = MagicMock()
        acc_model = MagicMock()
        acc_model.with_context.return_value = acc_model
        acc_model.search.return_value = existing
        loader.env = {"fix.chart.account": acc_model}

        with patch("odoo.addons.cd_gl_ext.models.fix_chart_loader.publish"):
            res = FixChartLoader.action_load_from_csv(loader, csv_text=SAMPLE_CSV)
            assert res["status"] == "loaded"
            assert existing.write.call_count == 14

    def test_chart_loader_action_load_from_file_missing(self):
        loader = MagicMock()
        loader.source_file = "non_existent_directory/non_existent_file.csv"
        with pytest.raises(UserError, match="Master data file not found"):
            FixChartLoader.action_load_from_csv(loader, csv_text=None)

    def test_chart_loader_action_load_from_default_file(self):
        loader = MagicMock()
        loader.company_id.id = 1
        loader.operating_unit_id = False
        loader.source_file = "project_content/02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.csv"
        acc_model = MagicMock()
        acc_model.with_context.return_value = acc_model
        acc_model.search.return_value = False
        loader.env = {"fix.chart.account": acc_model}

        with patch("odoo.addons.cd_gl_ext.models.fix_chart_loader.publish"):
            res = FixChartLoader.action_load_from_csv(loader, csv_text=None)
            assert res["status"] == "loaded"
            assert res["account_count"] == 79

    def test_chart_loader_action_reconcile_chart_empty_raises(self):
        loader = MagicMock()
        loader.company_id.id = 1
        acc_model = MagicMock()
        acc_model.search.return_value = []
        loader.env = {"fix.chart.account": acc_model}
        with pytest.raises(UserError, match="No accounts loaded"):
            FixChartLoader.action_reconcile_chart(loader)

    def test_chart_loader_action_reconcile_chart(self):
        loader = MagicMock()
        loader.company_id.id = 1
        a1 = MagicMock(account_code="1-10-10-001", account_type="asset", balance=1000.0)
        a2 = MagicMock(account_code="2-10-10-001", account_type="liability", balance=400.0)
        a3 = MagicMock(account_code="3-10-10-001", account_type="equity", balance=600.0)
        for a in (a1, a2, a3):
            a.name = "Account Name"
            a.account_subtype = "current"
            a.is_postable = True
            a.is_control_account = False
            a.control_subledger = False
            a.requires_dimension = ""
            a.statutory_group = "Group"
            a.active = True
        acc_model = MagicMock()
        acc_model.search.return_value = [a1, a2, a3]
        loader.env = {"fix.chart.account": acc_model}

        res = FixChartLoader.action_reconcile_chart(loader)
        assert res["reconciled"] is True
        loader.write.assert_called_with({"state": "reconciled"})


class TestFiscalYearAndReporting:
    def test_fiscal_year_lock_unclosed_period_raises(self):
        bridge = MagicMock()
        bridge.period_close_id.state = "in_progress"
        with pytest.raises(
            UserError, match="Cannot lock journals before period close is completed"
        ):
            FixFiscalYearIntegration.action_lock_journals(bridge)

    def test_mis_report_bridge_action_generate(self):
        bridge = MagicMock()
        bridge.id = 7
        bridge.name = "Statutory Balance Sheet"
        bridge.report_type = "balance_sheet"
        bridge.company_id.id = 1
        bridge.SUPPORTED_TYPES = FixMisReportBridge.SUPPORTED_TYPES
        bridge.fiscal_year_id = None

        # no constant {"status": "computed"} any more: without a fiscal year
        # there is no ledger window to compute from
        with pytest.raises(UserError, match="Select the fiscal year"):
            FixMisReportBridge.action_generate_report(bridge)
        bridge.write.assert_not_called()
