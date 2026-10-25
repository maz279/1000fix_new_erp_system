"""return_logic tests — P07-M04-T08 (DoD-03: 100% of return-calc paths).

Statutory correctness: holiday rollover, nil returns, TDS quarter mapping
against the BD fiscal year, BIN validation.
"""

from __future__ import annotations

import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.tax, pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))

from return_logic import (
    TDS_SECTION_RATES,
    ReturnError,
    TdsLine,
    aggregate_register,
    classify_register_row,
    next_working_day,
    prepare_tds_return,
    prepare_vat_return,
    prepare_vds_certificate,
    reconcile_vat_subledger,
    tds_quarter_for_date,
    tds_return_due_date,
    vat_return_due_date,
)

D = Decimal


class TestHolidayRollover(unittest.TestCase):
    def test_weekend_friday_rolls_to_sunday(self):
        # 2026-01-16 is a Friday -> rolls to Saturday -> Sunday 18th
        self.assertEqual(next_working_day(date(2026, 1, 16), set()), date(2026, 1, 18))

    def test_saturday_rolls_to_sunday(self):
        self.assertEqual(next_working_day(date(2026, 1, 17), set()), date(2026, 1, 18))

    def test_working_day_unchanged(self):
        self.assertEqual(next_working_day(date(2026, 1, 19), set()), date(2026, 1, 19))  # Mon

    def test_extra_holiday_rolls(self):
        # Monday 2026-10-19 declared a holiday -> Tuesday
        self.assertEqual(
            next_working_day(date(2026, 10, 19), {date(2026, 10, 19)}), date(2026, 10, 20)
        )

    def test_fixed_holiday_16_december(self):
        self.assertEqual(next_working_day(date(2026, 12, 16), set()), date(2026, 12, 17))


class TestVatReturnDueDate(unittest.TestCase):
    def test_normal_fifteenth(self):
        # 2026-11-15 is a Sunday
        self.assertEqual(vat_return_due_date("2026-10"), date(2026, 11, 15))

    def test_fifteenth_on_weekend_rolls(self):
        # Period 2026-02 -> due 2026-03-15: Sunday, a WORKING day in BD
        # (weekend is Fri+Sat) -> stays
        self.assertEqual(vat_return_due_date("2026-02"), date(2026, 3, 15))
        # Period 2026-12 -> due 2027-01-15: a FRIDAY -> rolls Sat -> Sun 17th
        self.assertEqual(vat_return_due_date("2026-12"), date(2027, 1, 17))

    def test_december_period_rolls_year(self):
        # Period 2026-11 -> due 2026-12-15: Tuesday -> stays
        self.assertEqual(vat_return_due_date("2026-11"), date(2026, 12, 15))


class TestPrepareVatReturn(unittest.TestCase):
    def test_full_return(self):
        ret = prepare_vat_return(
            "1234567890123",
            "2026-10",
            {"standard_15": (D("100000"), D("15000")), "zero_rated": (D("5000"), D("0"))},
            input_vat=D("3000"),
        )
        self.assertFalse(ret.nil_return)
        self.assertEqual(ret.total_taxable, D("105000.00"))
        self.assertEqual(ret.total_output_vat, D("15000.00"))
        self.assertEqual(ret.net_payable, D("12000.00"))

    def test_nil_return_mandatory(self):
        """A period with no transactions still returns a return."""
        ret = prepare_vat_return("1234567890123", "2026-10", {})
        self.assertTrue(ret.nil_return)
        self.assertEqual(ret.net_payable, D("0.00"))

    def test_input_vat_exceeds_output(self):
        ret = prepare_vat_return(
            "1234567890123", "2026-10", {"standard_15": (D("1000"), D("150"))}, input_vat=D("300")
        )
        self.assertEqual(ret.net_payable, D("-150.00"))  # refund position

    def test_bad_bin_refused(self):
        with self.assertRaises(ReturnError):
            prepare_vat_return("12345", "2026-10", {})

    def test_lines_quantised(self):
        ret = prepare_vat_return(
            "1234567890123", "2026-10", {"standard_15": (D("99.999"), D("15"))}
        )
        self.assertEqual(ret.lines[0].taxable_value, D("100.00"))


class TestTdsQuarters(unittest.TestCase):
    def test_july_is_q1_fy2027(self):
        quarter, fy = tds_quarter_for_date(date(2026, 7, 15))
        self.assertEqual(quarter, "2026-Q1")
        self.assertEqual(fy, "FY2027")

    def test_june_is_q4_fy2027(self):
        quarter, fy = tds_quarter_for_date(date(2027, 6, 30))
        self.assertEqual(quarter, "2026-Q4")
        self.assertEqual(fy, "FY2027")

    def test_january_is_q3(self):
        quarter, _fy = tds_quarter_for_date(date(2027, 1, 15))
        self.assertEqual(quarter, "2026-Q3")

    def test_october_is_q2(self):
        quarter, _fy = tds_quarter_for_date(date(2026, 10, 2))
        self.assertEqual(quarter, "2026-Q2")


class TestTdsDueDates(unittest.TestCase):
    def test_four_statutory_dates(self):
        self.assertEqual(tds_return_due_date("2026-Q1"), date(2026, 10, 25))
        self.assertEqual(tds_return_due_date("2026-Q2"), date(2027, 1, 25))
        self.assertEqual(tds_return_due_date("2026-Q3"), date(2027, 4, 25))
        self.assertEqual(tds_return_due_date("2026-Q4"), date(2027, 7, 25))

    def test_prepare_tds_return(self):
        ret = prepare_tds_return({"vendor-A": D("5000"), "vendor-B": D("3000")}, date(2026, 8, 15))
        self.assertEqual(ret.quarter, "2026-Q1")
        self.assertEqual(ret.total_withheld, D("8000.00"))
        self.assertEqual(ret.dedor_count if hasattr(ret, "dedor_count") else ret.deductor_count, 2)

    def test_negative_withheld_refused(self):
        with self.assertRaises(ReturnError):
            prepare_tds_return({"v": D("-1")}, date(2026, 8, 15))


class TestRegisterClassification(unittest.TestCase):
    """Register rows are declared on their own Mushak 9.1 line, never lumped
    into standard_15 (regression)."""

    def test_summary_names_the_treatment(self):
        self.assertEqual(classify_register_row(500, 0, "EDU: exempt @ 0%"), "exempt")
        self.assertEqual(
            classify_register_row(1000, 75, "P:1: reduced @ 7.5%\nQ: reduced @ 7.50%"),
            "reduced_7.5",
        )
        self.assertEqual(classify_register_row(100, 0, "X: zero_rated @ 0%"), "zero_rated")

    def test_unreadable_summary_lines_are_ignored(self):
        """Lines with no "<product>: <treatment> @ <rate>" shape, or an empty
        treatment, name nothing - the row falls back to its effective rate."""
        self.assertEqual(
            classify_register_row(1000, 150, "free text, no separator\nP:  @ 15%\n\n"),
            "standard_15",
        )

    def test_rate_identifies_a_summary_less_row(self):
        self.assertEqual(classify_register_row(D("2000.50"), D("300.08"), ""), "standard_15")
        self.assertEqual(classify_register_row(1000, 50, ""), "reduced_5")
        self.assertEqual(classify_register_row(1000, 100, ""), "reduced_10")

    def test_undeterminable_rows_are_flagged_per_actual_rate(self):
        self.assertEqual(classify_register_row(300, 0, ""), "unclassified_rate_0")
        self.assertEqual(classify_register_row(1000, 123.4, ""), "unclassified_rate_12.34")
        self.assertEqual(classify_register_row(0, 5, ""), "unclassified_vat_only")
        self.assertEqual(classify_register_row(0, 0, ""), "unclassified_rate_0")
        # a blended 15% + exempt row at 7.5% is NOT inferred to be reduced
        self.assertEqual(
            classify_register_row(1000, 75, "A: standard_15 @ 15%\nB: exempt @ 0%"),
            "unclassified_mixed_rate_7.5",
        )
        # an unreadable summary rate falls back to the row's own rate
        self.assertEqual(classify_register_row(1000, 75, "A: reduced @ abc%"), "reduced_7.5")
        self.assertEqual(
            classify_register_row(1000, 80, "A: reduced @ abc%"), "unclassified_rate_8"
        )

    def test_aggregate_sums_per_line(self):
        totals = aggregate_register(
            [(1000, 150, ""), (400, 60, "S: standard_15 @ 15%"), (300, 0, "")]
        )
        self.assertEqual(
            totals,
            {
                "standard_15": (D("1400"), D("210")),
                "unclassified_rate_0": (D("300"), D("0")),
            },
        )


class TestVatSubledgerReconciliation(unittest.TestCase):
    def test_reconciliation_zero_variance(self):
        recon = reconcile_vat_subledger(
            period="2026-10",
            register_output_vat=D("150000.00"),
            gl_210100_output_vat=D("150000.00"),
            register_input_vat=D("45000.00"),
            gl_110500_input_vat=D("45000.00"),
        )
        self.assertTrue(recon.is_reconciled)
        self.assertEqual(recon.output_variance, D("0.00"))
        self.assertEqual(recon.input_variance, D("0.00"))
        self.assertEqual(len(recon.notes), 0)

    def test_reconciliation_output_variance_detected(self):
        recon = reconcile_vat_subledger(
            period="2026-10",
            register_output_vat=D("150000.00"),
            gl_210100_output_vat=D("148500.00"),
            register_input_vat=D("45000.00"),
            gl_110500_input_vat=D("45000.00"),
        )
        self.assertFalse(recon.is_reconciled)
        self.assertEqual(recon.output_variance, D("1500.00"))
        self.assertEqual(recon.input_variance, D("0.00"))
        self.assertTrue(any("GL 210100" in n for n in recon.notes))

    def test_reconciliation_input_variance_detected(self):
        recon = reconcile_vat_subledger(
            period="2026-10",
            register_output_vat=D("150000.00"),
            gl_210100_output_vat=D("150000.00"),
            register_input_vat=D("45000.00"),
            gl_110500_input_vat=D("47200.00"),
        )
        self.assertFalse(recon.is_reconciled)
        self.assertEqual(recon.output_variance, D("0.00"))
        self.assertEqual(recon.input_variance, D("-2200.00"))
        self.assertTrue(any("GL 110500" in n for n in recon.notes))


class TestTdsSectionLines(unittest.TestCase):
    def test_statutory_rates(self):
        self.assertEqual(TDS_SECTION_RATES["52"], D("0.05"))
        self.assertEqual(TDS_SECTION_RATES["52AA"], D("0.10"))
        self.assertEqual(TDS_SECTION_RATES["53A"], D("0.05"))
        self.assertEqual(TDS_SECTION_RATES["53F"], D("0.10"))
        self.assertEqual(TDS_SECTION_RATES["56"], D("0.20"))

    def test_tds_line_dataclass(self):
        line = TdsLine(
            vendor_name="Acme Corp Ltd.",
            vendor_tin="123456789012",
            vendor_bin="1234567890123",
            section_code="52",
            base_amount=D("100000.00"),
            rate_percent=D("5.0"),
            tds_amount=D("5000.00"),
            challan_no="CH-2026-001",
            challan_date=date(2026, 10, 10),
        )
        self.assertEqual(line.vendor_name, "Acme Corp Ltd.")
        self.assertEqual(line.section_code, "52")
        self.assertEqual(line.tds_amount, D("5000.00"))


class TestTdsLineValidation(unittest.TestCase):
    def test_section_alias_and_withheld_fallback(self):
        line = TdsLine(
            vendor_tin="",
            vendor_name="Rahim Traders",
            section="53F",
            base_amount=D("2000"),
            withheld_amount=D("200.00"),
        )
        self.assertEqual((line.section, line.section_code), ("53F", "53F"))
        self.assertEqual((line.tds_amount, line.withheld_amount), (D("200.00"), D("200.00")))

    def test_default_section_is_52(self):
        self.assertEqual(TdsLine(vendor_tin="", vendor_name="X").section_code, "52")

    def test_negative_amounts_refused(self):
        with self.assertRaisesRegex(ReturnError, "cannot be negative"):
            TdsLine(vendor_tin="", vendor_name="X", base_amount=D("-1"))
        with self.assertRaisesRegex(ReturnError, "cannot be negative"):
            TdsLine(vendor_tin="", vendor_name="X", tds_amount=D("-0.01"))

    def test_unknown_section_refused(self):
        with self.assertRaisesRegex(ReturnError, "Unknown TDS statutory section '99'"):
            TdsLine(vendor_tin="", vendor_name="X", section_code="99")


class TestMushak66VdsCertificate(unittest.TestCase):
    def test_valid_vds_certificate(self):
        cert = prepare_vds_certificate(
            certificate_no="VDS-6.6/202610/00001",
            issue_date=date(2026, 10, 20),
            supplier_name="Apex Logistics Ltd.",
            supplier_bin="1234567890123",
            supplier_address="Tejgaon I/A, Dhaka",
            customer_name="1000 FiX Services Ltd.",
            customer_bin="9876543210123",
            invoice_no="INV-2026-099",
            invoice_date=date(2026, 10, 15),
            taxable_amount=D("100000.00"),
            vat_rate=D("0.15"),
            vat_amount=D("15000.00"),
            vds_amount=D("15000.00"),
            treasury_challan_no="CH-987654",
            treasury_challan_date=date(2026, 10, 18),
            bank_branch="Sonali Bank, Principal Branch",
        )
        self.assertEqual(cert.certificate_no, "VDS-6.6/202610/00001")
        self.assertEqual(
            cert.net_payable_to_supplier, D("100000.00")
        )  # Base + VAT - VDS = 100k + 15k - 15k
        self.assertEqual(cert.supplier_bin, "1234567890123")

    def test_invalid_supplier_bin_raises(self):
        with self.assertRaises(ReturnError):
            prepare_vds_certificate(
                certificate_no="VDS-6.6/202610/00002",
                issue_date=date(2026, 10, 20),
                supplier_name="Apex Logistics Ltd.",
                supplier_bin="12345",  # invalid BIN length
                supplier_address="Dhaka",
                customer_name="1000 FiX Services Ltd.",
                customer_bin="9876543210123",
                invoice_no="INV-2026-100",
                invoice_date=date(2026, 10, 15),
                taxable_amount=D("50000.00"),
                vat_rate=D("0.15"),
                vat_amount=D("7500.00"),
                vds_amount=D("7500.00"),
            )

    def test_vds_exceeds_vat_raises(self):
        with self.assertRaises(ReturnError):
            prepare_vds_certificate(
                certificate_no="VDS-6.6/202610/00003",
                issue_date=date(2026, 10, 20),
                supplier_name="Apex Logistics Ltd.",
                supplier_bin="1234567890123",
                supplier_address="Dhaka",
                customer_name="1000 FiX Services Ltd.",
                customer_bin="9876543210123",
                invoice_no="INV-2026-101",
                invoice_date=date(2026, 10, 15),
                taxable_amount=D("50000.00"),
                vat_rate=D("0.15"),
                vat_amount=D("7500.00"),
                vds_amount=D("10000.00"),  # Exceeds VAT
            )


class TestVdsCertificateParties(unittest.TestCase):
    def _cert(self, **kw):
        base = {
            "certificate_no": "VDS-6.6/202610/00009",
            "deductor_bin": "9876543210123",
            "deductor_name": "1000 FiX Services Ltd.",
            "deductee_bin": "1234567890123",
            "deductee_name": "Apex Logistics Ltd.",
            "total_amount": D("2000.005"),
            "vat_amount": D("300.004"),
            "vds_amount": D("150"),
            "challan_no": "CH-1",
        }
        base.update(kw)
        return prepare_vds_certificate(**base)

    def test_deductor_deductee_naming_and_rounding(self):
        cert = self._cert()
        self.assertEqual(cert.supplier_name, "Apex Logistics Ltd.")
        self.assertEqual(cert.supplier_bin, "1234567890123")
        self.assertEqual(cert.deductor_name, "1000 FiX Services Ltd.")
        self.assertEqual(cert.total_invoice_amount, D("2000.01"))  # half-up
        self.assertEqual(cert.vat_amount, D("300.00"))
        self.assertEqual(cert.treasury_challan_no, "CH-1")
        # 2000.01 + 300.00 - 150.00
        self.assertEqual(cert.net_payable_to_supplier, D("2150.01"))

    def test_invalid_deductor_bin_refused(self):
        with self.assertRaisesRegex(ReturnError, "Deductor BIN must be 13 digits"):
            self._cert(deductor_bin="98765")

    def test_zero_vds_refused(self):
        with self.assertRaisesRegex(ReturnError, "must be positive"):
            self._cert(vds_amount=D("0"))


class TestPurity(unittest.TestCase):
    def test_no_odoo_imports(self):
        import inspect

        import return_logic

        source = inspect.getsource(return_logic)
        self.assertNotIn("from odoo", source)


if __name__ == "__main__":
    unittest.main()
