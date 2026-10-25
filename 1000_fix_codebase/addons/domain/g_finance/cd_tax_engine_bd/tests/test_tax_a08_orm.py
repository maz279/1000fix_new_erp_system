# cd_tax_engine_bd — A08 M51 live-ORM behaviour (CD-M51-01): the
# effective-dated Tax Rate Master and statutory parameters, the statutory
# calendar from due-day master data, challans settling deductions with a GL
# posting, input VAT credit tracking feeding the 9.1, the quarterly
# withholding return from deduction lines, and the audit support pack.
from __future__ import annotations

import base64
import io
import json
import zipfile
from datetime import date

import pytest
from odoo.addons.cd_tax_engine_bd.models.fix_tax_compliance import quarter_bounds
from odoo.exceptions import UserError, ValidationError

pytestmark = [pytest.mark.financial, pytest.mark.tax]


@pytest.fixture
def tax(odoo_env):
    env = odoo_env
    company = env.company
    company.vat = "1234567890123"
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    Account = env["account.account"]

    def acc(code, name, kind):
        found = Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        return found or Account.create(
            {
                "code": code,
                "name": name,
                "account_type": kind,
                "company_ids": [(6, 0, [company.id])],
            }
        )

    tds = acc("990253", "Test TDS payable", "liability_current")
    vds = acc("990252", "Test VDS payable", "liability_current")
    icp = env["ir.config_parameter"].sudo()
    icp.set_param("cd_tax_engine_bd.account_code.tds_payable", "990253")
    icp.set_param("cd_tax_engine_bd.account_code.vds_payable", "990252")
    bank = env["account.journal"].search(
        [("company_id", "=", company.id), ("type", "=", "bank")], limit=1
    )
    icp.set_param("cd_tax_engine_bd.challan_journal_code", bank.code)
    supplier = env["res.partner"].create({"name": "Meghna Courier Ltd."})
    return {
        "env": env,
        "company": company,
        "ou": ou,
        "tds": tds,
        "vds": vds,
        "bank": bank,
        "supplier": supplier,
    }


def _deduction(t, kind="tds", amount=500.0, on="2026-09-10", **vals):
    rate = t["env"].ref(
        "cd_tax_engine_bd.tax_rate_tds_service_general"
        if kind == "tds"
        else "cd_tax_engine_bd.tax_rate_vds_rent"
    )
    return t["env"]["fix.withholding.line"].create(
        {
            "operating_unit_id": t["ou"].id,
            "tax_kind": kind,
            "partner_id": t["supplier"].id,
            "partner_tin": "123456789012",
            "rate_id": rate.id,
            "section": rate.section,
            "document_date": on,
            "base_amount": amount * 10,
            "rate": rate.rate,
            "amount": amount,
            "source_ref": "BILL-%s" % on,
            **vals,
        }
    )


class TestRateMaster:
    def test_seeded_defaults_are_flagged_and_effective(self, tax):
        Rate = tax["env"]["fix.tax.rate"]
        row = Rate.find_rate("tds", "rent_commercial", date(2026, 10, 1))
        assert (row.rate, row.section, row.verify_with_adviser) == (10.0, "ITA 2023 s.109", True)
        assert Rate.find_rate("vat", "standard", date(2026, 10, 1)).verify_with_adviser is False
        with pytest.raises(UserError, match="No effective TDS rate"):
            Rate.find_rate("tds", "rent_commercial", date(2024, 1, 1))

    def test_overlapping_windows_are_refused(self, tax):
        Rate = tax["env"]["fix.tax.rate"]
        Rate.create(
            {"tax_kind": "tds", "code": "x_test", "name": "X", "rate": 5, "date_from": "2026-07-01"}
        )
        with pytest.raises(ValidationError, match="overlapping"), tax["env"].cr.savepoint():
            Rate.create(
                {
                    "tax_kind": "tds",
                    "code": "x_test",
                    "name": "X2",
                    "rate": 6,
                    "date_from": "2027-01-01",
                }
            )
        with pytest.raises(ValidationError, match="between 0 and 100"), tax["env"].cr.savepoint():
            Rate.create({"tax_kind": "tds", "code": "y", "name": "Y", "rate": 120})

    def test_parameters_company_override_and_fail_closed(self, tax):
        Param = tax["env"]["fix.tax.parameter"]
        assert Param.get_value("mushak610_threshold", date(2026, 10, 1)) == 200000.0
        Param.create(
            {
                "key": "mushak610_threshold",  # gitleaks:allow - a parameter name
                "value": 250000,
                "date_from": "2026-10-01",
            }
        )
        assert Param.get_value("mushak610_threshold", date(2026, 10, 2)) == 250000.0
        assert Param.get_value("mushak610_threshold", date(2026, 9, 30)) == 200000.0
        with pytest.raises(UserError, match="has no row valid"):
            Param.get_value("rtgs_min_amount", date(2020, 1, 1))


class TestStatutoryCalendar:
    def test_due_dates_from_master_and_status_from_records(self, tax):
        env = tax["env"]
        Rule = env["fix.statutory.due.rule"]
        # September 2026: 9.1 due 15 Oct (Thursday); TDS deposit 14 Oct; VDS 7 Oct
        assert Rule.due_date_for("vat_91_return", date(2026, 9, 30)) == date(2026, 10, 15)
        # 25 Oct 2026 is a Sunday (a BD working day): quarter Jul-Sep
        assert Rule.due_date_for("wht_return", date(2026, 9, 30)) == date(2026, 10, 25)
        line = _deduction(tax, on="2026-09-10")
        rows = Rule.calendar(date(2026, 10, 1), date(2026, 10, 31))
        by_ob = {(r["rule"].obligation, r["period"]): r for r in rows}
        assert by_ob[("tds_deposit", "2026-09")]["status"] in ("due", "overdue")
        assert "not yet deposited" in by_ob[("tds_deposit", "2026-09")]["detail"]
        assert by_ob[("vds_deposit", "2026-09")]["status"] == "nothing_due"
        assert by_ob[("wht_return", "2026-Q1")]["detail"] == "No return prepared"
        line.state = "deposited"
        env["fix.statutory.filing"].create(
            {
                "rule_id": env.ref("cd_tax_engine_bd.due_rule_vat_91").id,
                "period_key": "2026-09",
                "filed_on": "2026-10-12",
                "reference": "IVAS-ACK-1",
            }
        )
        rows = {
            (r["rule"].obligation, r["period"]): r
            for r in Rule.calendar(date(2026, 10, 1), date(2026, 10, 31))
        }
        assert rows[("tds_deposit", "2026-09")]["status"] == "done"
        assert rows[("vat_91_return", "2026-09")]["status"] == "done"

    def test_annual_rule(self, tax):
        Rule = tax["env"]["fix.statutory.due.rule"]
        rows = Rule.calendar(date(2027, 1, 1), date(2027, 1, 31))
        itr = [r for r in rows if r["rule"].obligation == "company_itr"]
        assert [(r["period"], r["due_date"]) for r in itr] == [("FY2026", date(2027, 1, 17))]


class TestChallan:
    def test_link_confirm_post_and_certify_flow(self, tax):
        env = tax["env"]
        a = _deduction(tax, amount=400.0)
        b = _deduction(tax, amount=600.0)
        _deduction(tax, kind="vds", amount=900.0)  # other tax: not linked
        challan = env["fix.tax.challan"].create(
            {
                "challan_no": "AC-2026-0001",
                "challan_date": "2026-10-12",
                "tax_kind": "tds",
                "period": "2026-09",
                "amount": 999.0,
            }
        )
        challan.action_link_open_deductions()
        assert challan.withholding_line_ids == a | b
        with pytest.raises(UserError, match="does not equal"), env.cr.savepoint():
            challan.action_confirm_deposit()
        challan.amount = 1000.0
        challan.action_confirm_deposit()
        assert (challan.state, a.state, b.state) == ("deposited", "deposited", "deposited")
        lines = {line.account_id: (line.debit, line.credit) for line in challan.move_id.line_ids}
        assert lines[tax["tds"]] == (1000.0, 0.0)
        assert lines[tax["bank"].default_account_id] == (0.0, 1000.0)
        with pytest.raises(Exception, match=r"already recorded|unique"), env.cr.savepoint():
            env["fix.tax.challan"].create(
                {
                    "challan_no": "AC-2026-0001",
                    "challan_date": "2026-10-12",
                    "tax_kind": "tds",
                    "amount": 1,
                }
            )

    def test_unconfigured_bank_journal_fails_closed(self, tax):
        env = tax["env"]
        env["ir.config_parameter"].sudo().set_param("cd_tax_engine_bd.challan_journal_code", "")
        line = _deduction(tax, amount=100.0)
        challan = env["fix.tax.challan"].create(
            {"challan_no": "AC-X", "challan_date": "2026-10-12", "tax_kind": "tds", "amount": 100.0}
        )
        line.challan_id = challan
        with pytest.raises(UserError, match="challan_journal_code"), env.cr.savepoint():
            challan.action_confirm_deposit()
        assert challan.state == "draft" and line.state == "withheld"

    def test_certificate_needs_a_deposit(self, tax):
        line = _deduction(tax)
        with pytest.raises(UserError, match="after the challan deposit"), tax["env"].cr.savepoint():
            line.action_issue_certificate()


class TestInputCreditAndVatReturn:
    def _credit(self, t, **vals):
        return t["env"]["fix.input.vat.credit"].create(
            {
                "partner_id": t["supplier"].id,
                "supplier_bin": "9876543210123",
                "supplier_mushak_no": "63-55",
                "invoice_date": "2026-09-05",
                "taxable_amount": 10000.0,
                "vat_amount": 1500.0,
                **vals,
            }
        )

    def test_eligibility_reasons_and_claim_window(self, tax):
        ok = self._credit(tax)
        assert (ok.claim_period, ok.claim_deadline) == ("2026-09", "2027-01")
        ok.action_check_eligibility()
        assert ok.state == "eligible"
        no_bin = self._credit(tax, supplier_bin=False)
        no_bin.action_check_eligibility()
        assert (no_bin.state, no_bin.ineligible_reason) == (
            "ineligible",
            "Supplier BIN missing or not 13 digits",
        )
        enlisted = self._credit(tax, supplier_enlisted=True)
        enlisted.action_check_eligibility()
        assert enlisted.state == "ineligible"
        with (
            pytest.raises(ValidationError, match="after the last allowed"),
            tax["env"].cr.savepoint(),
        ):
            ok.claim_period = "2027-02"
        with pytest.raises(ValidationError, match="its own period"), tax["env"].cr.savepoint():
            self._credit(tax, adjustment_type="decrease", claim_period="2026-10")

    def test_prepare_91_claims_credits_nets_adjustments_and_locks_when_filed(self, tax):
        env = tax["env"]
        env["fix.mushak.register"].create(
            {
                "operating_unit_id": tax["ou"].id,
                "mushak_no": "M63-A08-1",
                "invoice_ref": "INV-A08-1",
                "invoice_date": "2026-09-20",
                "supplier_name": tax["company"].name,
                "supplier_bin": "1234567890123",
                "customer_name": "Walk-in",
                "taxable_amount": 20000.0,
                "vat_amount": 3000.0,
                "total_payable": 23000.0,
                "treatment_summary": "standard_15",
            }
        )
        good = self._credit(tax)
        good.action_check_eligibility()
        later = self._credit(tax, claim_period="2026-10")
        later.action_check_eligibility()
        dec = self._credit(tax, adjustment_type="decrease", vat_amount=200.0)
        dec.action_check_eligibility()
        ret = env["fix.vat.return"].create({"period": "2026-09"})
        ret.action_prepare()
        assert (ret.output_vat, ret.input_vat, ret.net_payable) == (3000.0, 1300.0, 1700.0)
        assert ret.due_date == date(2026, 10, 15)
        assert (good.state, dec.state, later.state) == ("claimed", "claimed", "eligible")
        assert ret.input_credit_ids == good | dec
        ret.state = "filed"
        with pytest.raises(UserError, match="filed"), env.cr.savepoint():
            ret.action_prepare()

    def test_period_format(self, tax):
        with pytest.raises(ValidationError, match="YYYY-MM"), tax["env"].cr.savepoint():
            tax["env"]["fix.vat.return"].create({"period": "2026-9"})


class TestTdsReturn:
    def test_quarter_bounds(self):
        assert quarter_bounds("2026-Q1") == (date(2026, 7, 1), date(2026, 9, 30))
        assert quarter_bounds("2026-Q3") == (date(2027, 1, 1), date(2027, 3, 31))

    def test_prepare_from_deductions(self, tax):
        env = tax["env"]
        _deduction(tax, amount=500.0, on="2026-07-15")
        _deduction(tax, amount=250.0, on="2026-09-30")
        _deduction(tax, amount=999.0, on="2026-10-01")  # next quarter
        ret = env["fix.tds.return"].create({"quarter": "2026-Q1"})
        ret.action_prepare()
        assert (ret.total_withheld, ret.deductor_count, ret.fiscal_year) == (750.0, 1, "FY2027")
        assert ret.due_date == date(2026, 10, 25)
        assert set(ret.line_ids.mapped("section_code")) == {"90"}
        with pytest.raises(ValidationError, match="fiscal-year start"), env.cr.savepoint():
            env["fix.tds.return"].create({"quarter": "Q1-2026"})


class TestAuditPack:
    def test_generate_verify_and_detect_tampering(self, tax):
        env = tax["env"]
        _deduction(tax, amount=321.0, on="2026-09-03")
        pack = env["fix.tax.audit.pack"].create(
            {"date_from": "2026-09-01", "date_to": "2026-09-30"}
        )
        pack.action_generate()
        assert pack.state == "generated" and pack.integrity_status == "intact"
        raw = base64.b64decode(pack.attachment_id.datas)
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            names = set(zf.namelist())
            manifest = json.loads(zf.read("manifest.json"))
            deductions = zf.read("withholding_deductions.csv").decode()
        assert {"manifest.json", "mushak_6_2_sales_register.csv", "tax_challans.csv"} <= names
        assert "321.0" in deductions
        entry = next(f for f in manifest["files"] if f["name"] == "withholding_deductions.csv")
        assert entry["rows"] == 1 and len(entry["sha256"]) == 64
        with pytest.raises(UserError, match="already generated"), env.cr.savepoint():
            pack.action_generate()
        pack.action_verify()
        assert pack.integrity_status == "intact"
        pack.attachment_id.datas = base64.b64encode(raw + b"x")
        pack.action_verify()
        assert pack.integrity_status == "tampered"


class TestVdsReceivedClaim:
    """Mushak 6.6 received (cd_billing_engine): settled certificates are taken
    as the 9.1's VDS credit, cleared Dr VAT payable / Cr VDS receivable on
    filing, and marked claimed exactly once."""

    def test_prepare_and_file_claims_the_certificates(self, tax):
        env = tax["env"]
        if "fix.vds.certificate.received" not in env:
            pytest.skip("cd_billing_engine VDS certificates not installed")
        invoice = env["fix.ar.invoice"].create(
            {
                "operating_unit_id": tax["ou"].id,
                "customer_id": env["res.partner"].create({"name": "Corporate VDS Customer"}).id,
                "source_model": "test.a08",
                "source_id": 1,
                "invoice_date": "2026-09-18",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "description": "AMC service",
                            "taxable_amount": 3000.0,
                            "vat_amount": 450.0,
                            "line_total": 3450.0,
                        },
                    )
                ],
            }
        )
        company = tax["company"]
        Account = env["account.account"]
        for code, kind in (("210100", "liability_current"), ("132000", "asset_receivable")):
            if not Account.search([("code", "=", code), ("company_ids", "in", company.id)]):
                Account.create(
                    {
                        "code": code,
                        "name": code,
                        "account_type": kind,
                        "company_ids": [(6, 0, [company.id])],
                    }
                )
        cert = (
            env["fix.vds.certificate.received"]
            .sudo()
            .create(
                {
                    "invoice_id": invoice.id,
                    "certificate_no": "66-A08-1",
                    "certificate_date": "2026-09-20",
                    "period": "2026-09",
                    "vds_amount": 450.0,
                }
            )
        )
        cert.write({"state": "settled"})
        ret = env["fix.vat.return"].create({"period": "2026-09"})
        ret.action_prepare()
        assert ret.vds_received_credit == 450.0
        assert ret.net_payable_after_vds == ret.net_payable - 450.0
        ret.action_file("IVAS-ACK-A08")
        assert cert.state == "claimed"
        lines = {ln.account_id.code: (ln.debit, ln.credit) for ln in ret.vds_claim_move_id.line_ids}
        assert lines == {"210100": (450.0, 0.0), "132000": (0.0, 450.0)}
