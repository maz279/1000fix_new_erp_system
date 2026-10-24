# cd_gl_ext — 100% Pure CoA Logic & Statutory Validation Tests (MD-035).
# P06-M01 / R04-M01-T02 & T05 (DoD-03: 100% financial calculation coverage).
from __future__ import annotations

import unittest
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial]

from odoo.addons.cd_gl_ext.models.coa_logic import (
    AccountRecord,
    CoaValidationError,
    account_level,
    ancestor_codes,
    parse_coa_csv,
    reconcile_trial_balance,
    validate_account_structure,
    validate_archive_attempt,
    validate_coa_rules,
    validate_posting_attempt,
    validate_type_change,
)

D = Decimal

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


class TestCoaLogic(unittest.TestCase):
    def test_parse_coa_csv_success(self):
        records = parse_coa_csv(SAMPLE_CSV)
        self.assertEqual(len(records), 14)
        cash_rec = next(r for r in records if r.account_code == "1-10-10-001")
        self.assertTrue(cash_rec.is_postable)
        self.assertFalse(cash_rec.is_control_account)
        self.assertEqual(cash_rec.requires_dimension, {"branch", "cost_centre"})
        self.assertEqual(cash_rec.entity_code, "EN-01")

        rec_ar = next(r for r in records if r.account_code == "1-10-20-001")
        self.assertTrue(rec_ar.is_control_account)
        self.assertEqual(rec_ar.control_subledger, "receivable")

    def test_parse_coa_csv_boolean_variations(self):
        csv_text = """account_code,account_name,account_type,is_postable,is_control_account,active,statutory_group
1-10-10-001,Cash,asset,1,YES,0,Cash
"""
        records = parse_coa_csv(csv_text)
        self.assertEqual(len(records), 1)
        r = records[0]
        self.assertTrue(r.is_postable)
        self.assertTrue(r.is_control_account)
        self.assertFalse(r.active)

    def test_validate_account_structure_valid(self):
        rec = AccountRecord(
            account_code="1-10-10-001",
            entity_code="EN-01",
            account_name="Cash in Hand",
            account_type="asset",
            account_subtype="cash",
            is_postable=True,
            is_control_account=False,
            control_subledger=None,
            requires_dimension={"branch"},
            statutory_group="Cash & Bank",
        )
        validate_account_structure(rec)

    def test_validate_account_structure_invalid_code_format(self):
        rec = AccountRecord(
            account_code="INVALID-CODE",
            entity_code="EN-01",
            account_name="Bad Code",
            account_type="asset",
            account_subtype="cash",
            is_postable=True,
            is_control_account=False,
            control_subledger=None,
            requires_dimension=set(),
            statutory_group="Cash",
        )
        with self.assertRaises(CoaValidationError) as ctx:
            validate_account_structure(rec)
        self.assertEqual(ctx.exception.rule, "CODE-FMT")

    def test_validate_account_structure_invalid_type(self):
        rec = AccountRecord(
            account_code="1-10-10-001",
            entity_code="EN-01",
            account_name="Bad Type",
            account_type="non_existent_type",
            account_subtype="cash",
            is_postable=True,
            is_control_account=False,
            control_subledger=None,
            requires_dimension=set(),
            statutory_group="Cash",
        )
        with self.assertRaises(CoaValidationError) as ctx:
            validate_account_structure(rec)
        self.assertEqual(ctx.exception.rule, "TYPE-FMT")

    def test_validate_account_structure_missing_statutory_group(self):
        rec = AccountRecord(
            account_code="1-10-10-001",
            entity_code="EN-01",
            account_name="No Group",
            account_type="asset",
            account_subtype="cash",
            is_postable=True,
            is_control_account=False,
            control_subledger=None,
            requires_dimension=set(),
            statutory_group="",
        )
        with self.assertRaises(CoaValidationError) as ctx:
            validate_account_structure(rec)
        self.assertEqual(ctx.exception.rule, "ERR-COA-005")

    def test_validate_account_structure_control_without_subledger(self):
        rec = AccountRecord(
            account_code="1-10-10-001",
            entity_code="EN-01",
            account_name="Bad Control",
            account_type="asset",
            account_subtype="receivable",
            is_postable=True,
            is_control_account=True,
            control_subledger=None,
            requires_dimension=set(),
            statutory_group="Receivables",
        )
        with self.assertRaises(CoaValidationError) as ctx:
            validate_account_structure(rec)
        self.assertEqual(ctx.exception.rule, "CTRL-REQ")

    def test_validate_account_structure_invalid_subledger(self):
        rec = AccountRecord(
            account_code="1-10-10-001",
            entity_code="EN-01",
            account_name="Bad Subledger",
            account_type="asset",
            account_subtype="receivable",
            is_postable=True,
            is_control_account=True,
            control_subledger="unknown_subledger",
            requires_dimension=set(),
            statutory_group="Receivables",
        )
        with self.assertRaises(CoaValidationError) as ctx:
            validate_account_structure(rec)
        self.assertEqual(ctx.exception.rule, "SUBLEDGER-FMT")

    def test_validate_account_structure_invalid_dimension(self):
        rec = AccountRecord(
            account_code="1-10-10-001",
            entity_code="EN-01",
            account_name="Bad Dim",
            account_type="asset",
            account_subtype="cash",
            is_postable=True,
            is_control_account=False,
            control_subledger=None,
            requires_dimension={"invalid_dim"},
            statutory_group="Cash",
        )
        with self.assertRaises(CoaValidationError) as ctx:
            validate_account_structure(rec)
        self.assertEqual(ctx.exception.rule, "DIM-FMT")

    def test_validate_coa_rules_coa01_non_leaf_postable(self):
        # Non-leaf code: 1-10-00-000 has NNN="000"
        rec = AccountRecord(
            account_code="1-10-00-000",
            entity_code="EN-01",
            account_name="Current Assets",
            account_type="asset",
            account_subtype="current_asset",
            is_postable=True,  # VIOLATION: Non-leaf postable
            is_control_account=False,
            control_subledger=None,
            requires_dimension=set(),
            statutory_group="Assets",
        )
        with self.assertRaises(CoaValidationError) as ctx:
            validate_coa_rules([rec])
        self.assertEqual(ctx.exception.rule, "ERR-COA-001")

    def test_validate_coa_rules_coa07_dormant_warning(self):
        rec = AccountRecord(
            account_code="1-10-10-001",
            entity_code="EN-01",
            account_name="Dormant Account",
            account_type="asset",
            account_subtype="cash",
            is_postable=True,
            is_control_account=False,
            control_subledger=None,
            requires_dimension=set(),
            statutory_group="Cash",
            has_postings=True,
            last_posting_days_ago=750,  # > 730 days
        )
        root = AccountRecord(
            account_code="1-00-00-000",
            entity_code="EN-01",
            account_name="Total Assets",
            account_type="asset",
            account_subtype="current_asset",
            is_postable=False,
            is_control_account=False,
            control_subledger=None,
            requires_dimension=set(),
            statutory_group="Assets",
        )
        res = validate_coa_rules([root, rec])
        self.assertTrue(res["valid"])
        self.assertEqual(len(res["warnings"]), 1)
        self.assertIn("WRN-COA-007", res["warnings"][0])

    def test_validate_coa_rules_sample_success(self):
        records = parse_coa_csv(SAMPLE_CSV)
        res = validate_coa_rules(records)
        self.assertTrue(res["valid"])
        self.assertEqual(res["account_count"], 14)
        self.assertEqual(res["postable_count"], 7)
        self.assertEqual(res["control_count"], 3)
        self.assertEqual(len(res["warnings"]), 0)

    def test_validate_posting_attempt_non_postable(self):
        rec = AccountRecord(
            account_code="1-10-00-000",
            entity_code="EN-01",
            account_name="Summary",
            account_type="asset",
            account_subtype="current_asset",
            is_postable=False,
            is_control_account=False,
            control_subledger=None,
            requires_dimension=set(),
            statutory_group="Assets",
        )
        with self.assertRaises(CoaValidationError) as ctx:
            validate_posting_attempt(rec, {})
        self.assertEqual(ctx.exception.rule, "ERR-COA-001")

    def test_validate_posting_attempt_control_direct_post(self):
        rec = AccountRecord(
            account_code="1-10-20-001",
            entity_code="EN-01",
            account_name="AR Control",
            account_type="asset",
            account_subtype="receivable",
            is_postable=True,
            is_control_account=True,
            control_subledger="receivable",
            requires_dimension=set(),
            statutory_group="Receivables",
        )
        # Direct manual post is forbidden (COA-02)
        with self.assertRaises(CoaValidationError) as ctx:
            validate_posting_attempt(rec, {}, is_direct_manual_post=True)
        self.assertEqual(ctx.exception.rule, "ERR-COA-002")

        # Subledger post is allowed
        validate_posting_attempt(rec, {}, is_direct_manual_post=False)

    def test_validate_posting_attempt_missing_dimension(self):
        rec = AccountRecord(
            account_code="1-10-10-001",
            entity_code="EN-01",
            account_name="Cash",
            account_type="asset",
            account_subtype="cash",
            is_postable=True,
            is_control_account=False,
            control_subledger=None,
            requires_dimension={"branch", "cost_centre"},
            statutory_group="Cash",
        )
        with self.assertRaises(CoaValidationError) as ctx:
            validate_posting_attempt(rec, {"branch": "BR-01"})
        self.assertEqual(ctx.exception.rule, "ERR-COA-003")

        # Pass when all dimensions provided
        validate_posting_attempt(rec, {"branch": "BR-01", "cost_centre": "CC-01"})

    def test_validate_archive_attempt(self):
        rec = AccountRecord(
            account_code="1-10-10-001",
            entity_code="EN-01",
            account_name="Cash",
            account_type="asset",
            account_subtype="cash",
            is_postable=True,
            is_control_account=False,
            control_subledger=None,
            requires_dimension=set(),
            statutory_group="Cash",
            balance=D("100.00"),
        )
        with self.assertRaises(CoaValidationError) as ctx:
            validate_archive_attempt(rec)
        self.assertEqual(ctx.exception.rule, "ERR-COA-004")

        rec.balance = D("0.00")
        validate_archive_attempt(rec)

    def test_validate_type_change(self):
        rec = AccountRecord(
            account_code="1-10-10-001",
            entity_code="EN-01",
            account_name="Account",
            account_type="asset",
            account_subtype="cash",
            is_postable=True,
            is_control_account=False,
            control_subledger=None,
            requires_dimension=set(),
            statutory_group="Cash",
            has_postings=True,
        )
        with self.assertRaises(CoaValidationError) as ctx:
            validate_type_change(rec, "expense")
        self.assertEqual(ctx.exception.rule, "ERR-COA-006")

        # Unchanged type succeeds
        validate_type_change(rec, "asset")

        # No postings allows change
        rec.has_postings = False
        validate_type_change(rec, "expense")

    def test_reconcile_trial_balance(self):
        records = parse_coa_csv(SAMPLE_CSV)
        # Assets: 1500 (Cash 1000, Debtors 500)
        # Liabilities: 400 (Creditors 400)
        # Equity: 800 (Share capital 800)
        # Revenue: 600 (Service repair 600)
        # Expense: 300 (Salaries 300)
        # Net Income = 600 - 300 = 300
        # Effective Equity = 800 + 300 = 1100
        # Liabilities + Effective Equity = 400 + 1100 = 1500 = Assets!
        balances = {
            "1-10-10-001": D("1000.00"),
            "1-10-20-001": D("500.00"),
            "2-10-10-001": D("400.00"),
            "3-10-10-001": D("800.00"),
            "4-10-10-001": D("600.00"),
            "5-10-10-001": D("300.00"),
            "9-99-99-999": D("999.00"),  # Unknown code ignored
        }
        res = reconcile_trial_balance(balances, records)
        self.assertTrue(res["reconciled"])
        self.assertAlmostEqual(res["discrepancy"], 0.0)
        self.assertEqual(res["total_assets"], 1500.0)
        self.assertEqual(res["total_liabilities"], 400.0)
        self.assertEqual(res["total_equity"], 800.0)
        self.assertEqual(res["total_income"], 600.0)
        self.assertEqual(res["total_expense"], 300.0)

    def test_reconcile_trial_balance_unbalanced(self):
        records = parse_coa_csv(SAMPLE_CSV)
        balances = {
            "1-10-10-001": D("1000.00"),
            "2-10-10-001": D("400.00"),
            "3-10-10-001": D("500.00"),
        }
        res = reconcile_trial_balance(balances, records)
        self.assertFalse(res["reconciled"])
        self.assertNotEqual(res["discrepancy"], 0.0)

    def test_statutory_bangladesh_coa_file(self):
        """Verify the complete MD-035 statutory Chart of Accounts file."""
        candidates = [
            Path(__file__).resolve().parents[4]
            / "project_content"
            / "02_Master_Data_and_Configuration"
            / "02E_Finance_and_Statutory"
            / "MD-035_Chart_of_Accounts_Bangladesh.csv",
            Path(__file__).resolve().parents[5]
            / "project_content"
            / "02_Master_Data_and_Configuration"
            / "02E_Finance_and_Statutory"
            / "MD-035_Chart_of_Accounts_Bangladesh.csv",
            Path(__file__).resolve().parents[6]
            / "project_content"
            / "02_Master_Data_and_Configuration"
            / "02E_Finance_and_Statutory"
            / "MD-035_Chart_of_Accounts_Bangladesh.csv",
        ]
        csv_path = next((p for p in candidates if p.is_file()), candidates[0])
        self.assertTrue(
            csv_path.is_file(), f"MD-035 CSV file missing across candidates: {candidates}"
        )
        content = csv_path.read_text(encoding="utf-8")
        records = parse_coa_csv(content)
        self.assertEqual(len(records), 79)

        # Validate complete CoA rule set
        res = validate_coa_rules(records)
        self.assertTrue(res["valid"])
        self.assertEqual(res["account_count"], 79)
        self.assertEqual(len(res["warnings"]), 0)

        # Confirm W2 inventory suspense account is present and configured
        suspense_acc = next((r for r in records if r.account_code == "1-10-99-999"), None)
        self.assertIsNotNone(suspense_acc)
        self.assertIn("Inventory", suspense_acc.account_name)
        self.assertTrue(suspense_acc.is_postable)


def _acc(code, account_type=None, postable=None, entity="EN-01", parent=None):
    """A minimal valid account; type follows the T block unless given."""
    types = {"1": "asset", "2": "liability", "3": "equity", "4": "income", "5": "expense"}
    return AccountRecord(
        account_code=code,
        entity_code=entity,
        account_name=f"Account {code}",
        account_type=account_type or types[code[0]],
        account_subtype="",
        is_postable=(not code.endswith("-000")) if postable is None else postable,
        is_control_account=False,
        control_subledger=None,
        requires_dimension=set(),
        statutory_group="Group",
        parent_account_code=parent,
    )


class TestCoaHierarchy(unittest.TestCase):
    """R01-AUDIT: MD-035 §3 T/GG/SS hierarchy + parent-account existence."""

    def test_levels_and_ancestors(self):
        self.assertEqual(account_level("1-00-00-000"), 1)
        self.assertEqual(account_level("1-10-00-000"), 2)
        self.assertEqual(account_level("1-10-20-000"), 3)
        self.assertEqual(account_level("1-10-20-030"), 4)
        self.assertEqual(
            ancestor_codes("1-10-20-030"), ["1-10-20-000", "1-10-00-000", "1-00-00-000"]
        )
        self.assertEqual(ancestor_codes("1-10-20-000"), ["1-10-00-000", "1-00-00-000"])
        self.assertEqual(ancestor_codes("1-10-00-000"), ["1-00-00-000"])
        self.assertEqual(ancestor_codes("1-00-00-000"), [])

    def test_type_block_must_match_type(self):
        with self.assertRaises(CoaValidationError) as ctx:
            validate_account_structure(_acc("4-10-10-010", account_type="expense"))
        self.assertEqual(ctx.exception.rule, "HIER-TYPE")
        self.assertIn("'4' denotes 'income'", ctx.exception.message)

    def test_subgroup_under_group_zero_is_malformed(self):
        for code in ("1-00-10-000", "1-00-00-010", "1-00-10-010"):
            with self.subTest(code=code):
                with self.assertRaises(CoaValidationError) as ctx:
                    validate_account_structure(_acc(code))
                self.assertEqual(ctx.exception.rule, "HIER-LEVEL")
                self.assertIn("group block 00", ctx.exception.message)

    def test_sequence_under_subgroup_zero_is_malformed(self):
        with self.assertRaises(CoaValidationError) as ctx:
            validate_account_structure(_acc("1-10-00-010"))
        self.assertEqual(ctx.exception.rule, "HIER-LEVEL")
        self.assertIn("subgroup block 00", ctx.exception.message)

    def test_parent_is_nearest_existing_ancestor(self):
        # 1-10-20-030 has no subgroup row; it rolls up to category 1-10-00-000.
        chart = [_acc("1-00-00-000"), _acc("1-10-00-000"), _acc("1-10-20-030")]
        res = validate_coa_rules(chart)
        self.assertEqual(res["account_count"], 3)
        self.assertEqual(res["postable_count"], 1)

    def test_lone_group_root_is_valid(self):
        self.assertEqual(validate_coa_rules([_acc("5-00-00-000")])["account_count"], 1)

    def test_orphan_without_group_root_is_refused(self):
        with self.assertRaises(CoaValidationError) as ctx:
            validate_coa_rules([_acc("2-00-00-000"), _acc("1-10-10-010")])
        self.assertEqual(ctx.exception.rule, "PARENT-MISSING")
        self.assertEqual(ctx.exception.code, "1-10-10-010")
        self.assertIn("group 1-00-00-000 is missing", ctx.exception.message)

    def test_parent_must_belong_to_the_same_entity(self):
        chart = [_acc("1-00-00-000", entity="EN-01"), _acc("1-10-10-010", entity="EN-02")]
        with self.assertRaises(CoaValidationError) as ctx:
            validate_coa_rules(chart)
        self.assertEqual(ctx.exception.rule, "PARENT-MISSING")

    def test_declared_parent_matching_hierarchy(self):
        chart = [
            _acc("1-00-00-000"),
            _acc("1-10-10-000", parent="1-00-00-000"),
            _acc("1-10-10-010", parent="1-10-10-000"),
        ]
        self.assertEqual(validate_coa_rules(chart)["account_count"], 3)

    def test_declared_parent_must_exist(self):
        chart = [_acc("1-00-00-000"), _acc("1-10-10-010", parent="1-10-10-000")]
        with self.assertRaises(CoaValidationError) as ctx:
            validate_coa_rules(chart)
        self.assertEqual(ctx.exception.rule, "PARENT-MISSING")
        self.assertIn("1-10-10-000 does not exist", ctx.exception.message)

    def test_declared_parent_cannot_skip_an_existing_level(self):
        chart = [
            _acc("1-00-00-000"),
            _acc("1-10-10-000"),
            _acc("1-10-10-010", parent="1-00-00-000"),
        ]
        with self.assertRaises(CoaValidationError) as ctx:
            validate_coa_rules(chart)
        self.assertEqual(ctx.exception.rule, "PARENT-MISMATCH")
        self.assertIn("expected 1-10-10-000", ctx.exception.message)

    def test_group_root_cannot_declare_a_parent(self):
        chart = [_acc("1-00-00-000", parent="2-00-00-000"), _acc("2-00-00-000")]
        with self.assertRaises(CoaValidationError) as ctx:
            validate_coa_rules(chart)
        self.assertEqual(ctx.exception.rule, "PARENT-MISMATCH")
        self.assertIn("none: level-1 group", ctx.exception.message)

    def test_duplicate_code_within_entity_is_refused(self):
        with self.assertRaises(CoaValidationError) as ctx:
            validate_coa_rules([_acc("1-00-00-000"), _acc("1-00-00-000")])
        self.assertEqual(ctx.exception.rule, "DUP-CODE")

    def test_same_code_in_two_entities_is_allowed(self):
        chart = [_acc("1-00-00-000", entity="EN-01"), _acc("1-00-00-000", entity="EN-02")]
        self.assertEqual(validate_coa_rules(chart)["account_count"], 2)

    def test_parse_reads_declared_parent_column(self):
        text = (
            "account_code,account_name,account_type,is_postable,statutory_group,parent_account_code\n"
            "1-00-00-000,Assets,asset,FALSE,Assets,\n"
            "1-10-10-010,Cash,asset,TRUE,Assets,1-00-00-000\n"
        )
        root, cash = parse_coa_csv(text)
        self.assertIsNone(root.parent_account_code)
        self.assertEqual(cash.parent_account_code, "1-00-00-000")
        self.assertEqual(validate_coa_rules([root, cash])["postable_count"], 1)
