# Tests for cd_multi_entity (Milestone R10-M01 / CD-M65-01..03).
import json
from datetime import date
from unittest.mock import MagicMock

import pytest


class TestFixConsolidation:
    """fix.consolidation.book, fix.consolidation.line, and fix.elimination.entry tests."""

    def test_consolidation_models_exist(self):
        from odoo.addons.cd_multi_entity.models.fix_consolidation import (
            FixConsolidationBook,
            FixConsolidationLine,
            FixEliminationEntry,
        )

        assert FixConsolidationBook is not None
        assert FixConsolidationLine is not None
        assert FixEliminationEntry is not None

    def test_consolidation_code_constraint(self):
        from odoo.addons.cd_multi_entity.models.fix_consolidation import FixConsolidationBook

        assert hasattr(FixConsolidationBook, "_code_unique")

    def test_consolidation_totals_computation(self):
        from odoo.addons.cd_multi_entity.models.fix_consolidation import FixConsolidationBook

        book = MagicMock()
        line1 = MagicMock(account_type="revenue", consolidated_amount=1200000.0)
        line2 = MagicMock(account_type="expense", consolidated_amount=750000.0)
        elim1 = MagicMock(amount=50000.0, elimination_type="revenue_expense")
        elim2 = MagicMock(amount=20000.0, elimination_type="receivable_payable")

        book.line_ids = [line1, line2]
        book.elimination_ids = [elim1, elim2]

        # Invoke the logic of _compute_totals directly; `self` is a recordset
        # stand-in that iterates the book and carries PL_ELIMINATION_TYPES.
        holder = MagicMock(PL_ELIMINATION_TYPES=FixConsolidationBook.PL_ELIMINATION_TYPES)
        holder.__iter__.return_value = iter([book])
        FixConsolidationBook._compute_totals(holder)

        assert book.total_subsidiary_revenue == 1200000.0
        assert book.total_subsidiary_expense == 750000.0
        assert book.total_eliminations == 70000.0
        # IC revenue is eliminated against the mirror IC expense (balance-sheet
        # eliminations do not touch P&L), so group profit is unchanged.
        assert book.consolidated_revenue == 1150000.0
        assert book.consolidated_expense == 700000.0
        assert book.net_consolidated_profit == 1200000.0 - 750000.0


class TestFixIntercompany:
    """fix.intercompany.rule and fix.intercompany.transaction tests."""

    def test_intercompany_models_exist(self):
        from odoo.addons.cd_multi_entity.models.fix_intercompany import (
            FixIntercompanyRule,
            FixIntercompanyTransaction,
        )

        assert FixIntercompanyRule is not None
        assert FixIntercompanyTransaction is not None

    def test_transfer_pricing_defaults(self):
        from odoo.addons.cd_multi_entity.models.fix_intercompany import FixIntercompanyRule

        # Transfer pricing must comply with NBR ITA 2023 s.107
        assert "transfer_pricing_compliant" in dir(FixIntercompanyRule)
        assert "markup_percent" in dir(FixIntercompanyRule)

    def test_mirror_bill_generation_logic(self):
        from odoo.addons.cd_multi_entity.models.fix_intercompany import FixIntercompanyTransaction

        tx = MagicMock(reference="IC-TXN-2026-0099", mirror_invoice_ref=False)
        tx.ensure_one = MagicMock()

        FixIntercompanyTransaction.action_generate_mirror(tx)

        tx.write.assert_called_once()
        args = tx.write.call_args[0][0]
        assert args["mirror_invoice_ref"] == "MIRROR-AP-IC-TXN-2026-0099"
        assert args["state"] == "pending_matching"


class TestLocalisationAndStatutoryCalendar:
    """Bangladesh tax calendar, address validation, and entity localisation tests (R10-M01-T03)."""

    def test_entity_localisation_fields(self):
        from odoo.addons.cd_multi_entity.models.fix_localisation import FixEntityLocalisation

        assert "bin_number" in dir(FixEntityLocalisation)
        assert "tin_number" in dir(FixEntityLocalisation)
        assert "statutory_calendar_rule" in dir(FixEntityLocalisation)

    def test_mushak_vat_return_due_date_calculation(self):
        from odoo.addons.cd_multi_entity.models.fix_localisation import FixEntityLocalisation

        entity = MagicMock(spec=FixEntityLocalisation)
        entity.ensure_one = MagicMock()
        entity.vat_statutory_day = 15
        entity.statutory_calendar_rule = "mushak_next_working_day"
        entity.env = {"fix.country.pack.line": MagicMock(search=MagicMock(return_value=[]))}

        # Case 1: Standard month where 15th is a Sunday (e.g., Nov 15, 2026 is Sunday)
        # Period = Oct 2026 (month 10) -> Due month = Nov 2026 (month 11), day 15 is Sunday (weekday 6)
        due1 = FixEntityLocalisation.get_vat_return_due_date(entity, 2026, 10)
        assert due1 == date(2026, 11, 15)
        assert due1.weekday() not in (4, 5)  # Not Friday or Saturday

        # Case 2: Period = Jul 2026 (month 7) -> Due month = Aug 2026 (month 8), Aug 15, 2026 is Saturday (weekday 5)
        # Must roll over to Sunday, Aug 16, 2026!
        due2 = FixEntityLocalisation.get_vat_return_due_date(entity, 2026, 7)
        assert due2 == date(2026, 8, 16)
        assert due2.weekday() == 6  # Sunday!

    def test_tds_quarterly_due_dates(self):
        from odoo.addons.cd_multi_entity.models.fix_localisation import FixEntityLocalisation

        entity = MagicMock(spec=FixEntityLocalisation)
        entity.ensure_one = MagicMock()

        # Q1 (Jul-Sep 2026) -> Due Oct 15, 2026
        due_q1 = FixEntityLocalisation.get_tds_quarter_due_date(entity, 1, 2027)
        assert due_q1.month == 10
        assert due_q1.day >= 15
        assert due_q1.weekday() not in (4, 5)

        # Q2 (Oct-Dec 2026) -> Due Jan 15, 2027 (Jan 15, 2027 is Friday! Must rollover to Sunday Jan 17, 2027!)
        due_q2 = FixEntityLocalisation.get_tds_quarter_due_date(entity, 2, 2027)
        assert due_q2.month == 1
        assert due_q2 == date(2027, 1, 17)
        assert due_q2.weekday() == 6  # Rolled over from Friday to Sunday!

    def test_bd_address_validation(self):
        from odoo.addons.cd_multi_entity.models.fix_localisation import FixEntityLocalisation
        from odoo.exceptions import ValidationError

        entity = MagicMock(spec=FixEntityLocalisation)

        valid_addr = {
            "division": "Dhaka",
            "district": "Dhaka",
            "upazila": "Tejgaon",
            "postcode": "1208",
        }
        assert FixEntityLocalisation.validate_bd_address(entity, valid_addr) is True

        # Invalid postcode (non-4-digit)
        invalid_addr = {
            "division": "Dhaka",
            "district": "Dhaka",
            "postcode": "12089",  # 5 digits invalid
        }
        with pytest.raises(ValidationError):
            FixEntityLocalisation.validate_bd_address(entity, invalid_addr)


class TestNilReturnAutomation:
    """Statutory Nil-Return generator tests (R10-M01-T04)."""

    def test_nil_return_model_exists(self):
        from odoo.addons.cd_multi_entity.models.fix_localisation import FixNilReturnGenerator

        assert FixNilReturnGenerator is not None

    def test_nil_return_generation_payload_schema(self):
        from odoo.addons.cd_multi_entity.models.fix_localisation import FixNilReturnGenerator

        rec = MagicMock(spec=FixNilReturnGenerator)
        rec.ensure_one = MagicMock()
        rec.state = "verified"
        rec.entity_id = MagicMock(
            code="1000FIX-BD",
            legal_name="1000 FiX Services Ltd.",
            bin_number="1882991029102",
            tin_number="881920391029",
        )
        rec.period_year = 2026
        rec.period_month = 6
        rec.env = MagicMock()
        rec.env.user.name = "Compliance Officer"

        FixNilReturnGenerator.action_generate_nil_packs(rec)

        rec.write.assert_called_once()
        args = rec.write.call_args[0][0]
        assert args["state"] == "generated"

        # Verify Mushak 9.1 zero return payload
        mushak_json = json.loads(args["mushak_9_1_nil_payload"])
        assert mushak_json["mushak_form"] == "9.1"
        assert mushak_json["submission_type"] == "NIL"
        assert mushak_json["part_3_supplies"]["total_sales_value"] == 0.0
        assert mushak_json["part_5_net_tax"]["net_payable"] == 0.0
        assert mushak_json["bin"] == "1882991029102"

        # Verify TDS nil payload
        tds_json = json.loads(args["tds_nil_payload"])
        assert tds_json["form"] == "TDS_MONTHLY_NIL"
        assert tds_json["is_nil_declaration"] is True
        assert tds_json["total_tds_deducted"] == 0.0


class TestBangladeshCountryPackData:
    """Bangladesh Divisions, Districts, and Public Holidays reference pack tests (CD-M65-01)."""

    def test_divisions_count(self):
        from odoo.addons.cd_multi_entity.models.fix_bd_country_pack_data import BANGLADESH_DIVISIONS

        assert len(BANGLADESH_DIVISIONS) == 8
        codes = [d["code"] for d in BANGLADESH_DIVISIONS]
        assert "BD-30" in codes  # Dhaka

    def test_districts_count(self):
        from odoo.addons.cd_multi_entity.models.fix_bd_country_pack_data import BANGLADESH_DISTRICTS

        assert len(BANGLADESH_DISTRICTS) == 64
        # Every district must have code, parent division, and Bengali name
        for dist in BANGLADESH_DISTRICTS:
            assert dist["code"]
            assert dist["parent"]
            assert dist["name_bn"]

    def test_statutory_holidays_defined(self):
        from odoo.addons.cd_multi_entity.models.fix_bd_country_pack_data import (
            STATUTORY_HOLIDAYS_2026,
        )

        assert len(STATUTORY_HOLIDAYS_2026) >= 10
        names = [h["name"] for h in STATUTORY_HOLIDAYS_2026]
        assert any("Independence" in n for n in names)
        assert any("Eid-ul-Fitr" in n for n in names)
        assert any("Victory Day" in n for n in names)
