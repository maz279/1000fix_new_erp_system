# cd_tax_engine_bd — live-ORM behaviour of M51 (VAT register, Mushak 9.1,
# TDS returns, withholding certificates). DoD-03 statutory set.
#
# The NBR IVAS adapter is exercised in SANDBOX mode (no network) or through
# a stub client; nothing here reaches the NBR portal.
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

pytestmark = [pytest.mark.tax, pytest.mark.financial]

D = Decimal
COMPANY_BIN = "1234567890123"


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def _ou(env):
    return env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)


def _register_row(env, mushak_no, invoice_date, taxable, vat, **extra):
    vals = {
        "operating_unit_id": _ou(env).id,
        "mushak_no": mushak_no,
        "invoice_ref": f"AR/{mushak_no}",
        "invoice_date": invoice_date,
        "supplier_name": "1000 FiX Services Ltd.",
        "supplier_bin": COMPANY_BIN,
        "customer_name": "Walk-in customer",
        "taxable_amount": taxable,
        "vat_amount": vat,
        "total_payable": taxable + vat,
    }
    vals.update(extra)
    return env["fix.mushak.register"].create(vals)


def _posted_entry(env, amount):
    """A posted GL entry standing for the supply's posting (arrangement)."""
    company = env.company
    Account = env["account.account"]
    a1 = Account.create(
        {
            "code": "M51T901",
            "name": "AR test",
            "account_type": "asset_receivable",
            "reconcile": True,
            "company_ids": [(6, 0, company.ids)],
        }
    )
    a2 = Account.create(
        {
            "code": "M51T902",
            "name": "Revenue test",
            "account_type": "income",
            "company_ids": [(6, 0, company.ids)],
        }
    )
    journal = env["account.journal"].create(
        {"name": "M51 posting test", "code": "M51PT", "type": "general", "company_id": company.id}
    )
    move = env["account.move"].create(
        {
            "journal_id": journal.id,
            "date": "2026-09-02",
            "line_ids": [
                (0, 0, {"name": "AR", "account_id": a1.id, "debit": amount}),
                (0, 0, {"name": "Rev", "account_id": a2.id, "credit": amount}),
            ],
        }
    )
    move.action_post()
    return move


def _invoice_event(env, mushak_no, event_id="evt-1"):
    return {
        "event_id": event_id,
        "payload": {
            "mushak_no": mushak_no,
            "invoice_ref": "AR/77",
            "invoice_date": "2026-09-14",
            "supplier_name": "1000 FiX Services Ltd.",
            "supplier_bin": COMPANY_BIN,
            "customer_name": "Karim Electronics",
            "customer_bin": "9876543210123",
            "taxable_amount": 2000.0,
            "vat_amount": 300.0,
            "total_payable": 2300.0,
            "treatment_summary": "SVC: standard_15 @ 15%",
            "operating_unit_id": _ou(env).id,
        },
    }


# --------------------------------------------------------------------------- fix.vat.treatment


# Synthetic signing officer for the online-filing tests.
DECLARANT = {
    "declarant_name": "Test Declarant",
    "declarant_designation": "Test Tax Manager",
    "declarant_nid": "1234567890",
}


def _set_declarant(env):
    icp = env["ir.config_parameter"].sudo()
    for key, value in DECLARANT.items():
        icp.set_param(f"cd_tax_engine_bd.{key}", value)


class TestVatTreatment:
    def _row(self, env, code, treatment, rate, base=0.0):
        return env["fix.vat.treatment"].create(
            {
                "code": code,
                "name": code,
                "treatment_type": treatment,
                "rate": rate,
                "truncated_base": base,
            }
        )

    def test_valid_rows(self, odoo_env):
        assert self._row(odoo_env, "T-STD", "standard_15", 15.0).rate == 15.0
        assert self._row(odoo_env, "T-RED", "reduced", 7.5).rate == 7.5
        assert self._row(odoo_env, "T-EXP", "exempt", 0.0).treatment_type == "exempt"
        assert self._row(odoo_env, "T-TRN", "truncated", 0.0, base=5000.0).truncated_base == 5000.0

    def test_standard_rate_is_fixed(self, odoo_env):
        with (
            pytest.raises(ValidationError, match="carries the standard rate in force"),
            odoo_env.cr.savepoint(),
        ):
            self._row(odoo_env, "T-STD10", "standard_15", 10.0)

    def test_unscheduled_reduced_rate_refused(self, odoo_env):
        """Regression: a 'reduced' row accepted any rate although the
        determination engine only knows the scheduled 5 / 7.5 / 10."""
        with (
            pytest.raises(ValidationError, match=r"reduced rate 12% is not a scheduled rate"),
            odoo_env.cr.savepoint(),
        ):
            self._row(odoo_env, "T-RED12", "reduced", 12.0)

    def test_zero_rated_carries_no_rate(self, odoo_env):
        with (
            pytest.raises(ValidationError, match="zero_rated carries no ad-valorem rate"),
            odoo_env.cr.savepoint(),
        ):
            self._row(odoo_env, "T-ZR", "zero_rated", 5.0)

    def test_truncated_needs_positive_base(self, odoo_env):
        with pytest.raises(ValidationError, match="positive fixed base"), odoo_env.cr.savepoint():
            self._row(odoo_env, "T-TRN0", "truncated", 0.0, base=0.0)


# --------------------------------------------------------------------------- fix.mushak.register


class TestMushakRegister:
    def test_bins_are_thirteen_digits(self, odoo_env):
        with (
            pytest.raises(ValidationError, match="Supplier BIN must be a real 13-digit BIN"),
            odoo_env.cr.savepoint(),
        ):
            _register_row(
                odoo_env, "2026-000001", date(2026, 9, 1), 100.0, 15.0, supplier_bin="12345"
            )
        with (
            pytest.raises(ValidationError, match="Customer BIN must be a real 13-digit BIN"),
            odoo_env.cr.savepoint(),
        ):
            _register_row(
                odoo_env, "2026-000002", date(2026, 9, 1), 100.0, 15.0, customer_bin="98AB"
            )
        row = _register_row(odoo_env, "2026-000003", date(2026, 9, 1), 100.0, 15.0)
        assert row.customer_bin is False  # an unregistered buyer is allowed

    def test_consume_creates_once_per_event(self, odoo_env):
        register = odoo_env["fix.mushak.register"]
        row = register.consume_invoice_created(_invoice_event(odoo_env, "2026-000010"))
        assert (row.mushak_no, row.source_event_id) == ("2026-000010", "evt-1")
        assert _money(row.taxable_amount) == D("2000.00")
        assert _money(row.vat_amount) == D("300.00")
        assert _money(row.total_payable) == D("2300.00")
        assert row.customer_bin == "9876543210123"
        replay = register.consume_invoice_created(_invoice_event(odoo_env, "2026-000010"))
        assert replay == row
        assert register.search_count([("mushak_no", "=", "2026-000010")]) == 1

    def test_event_without_id_is_refused(self, odoo_env):
        """Regression: event_id None searched source_event_id = False and
        returned unrelated register rows instead of failing."""
        _register_row(odoo_env, "2026-000020", date(2026, 9, 1), 100.0, 15.0)
        event = _invoice_event(odoo_env, "2026-000021")
        event.pop("event_id")
        with pytest.raises(ValidationError, match="without event_id"), odoo_env.cr.savepoint():
            odoo_env["fix.mushak.register"].consume_invoice_created(event)

    def test_replay_adopts_the_row_the_billing_engine_wrote(self, odoo_env):
        """Regression: the billing engine writes the register row in the
        same transaction as invoice.created; consuming that event created a
        second row with the same Mushak number (unique-key crash on rebuild)."""
        written = _register_row(odoo_env, "2026-000030", date(2026, 9, 14), 2000.0, 300.0)
        adopted = odoo_env["fix.mushak.register"].consume_invoice_created(
            _invoice_event(odoo_env, "2026-000030", event_id="evt-30")
        )
        assert adopted == written
        assert written.source_event_id == "evt-30"

    def test_same_number_from_another_event_keeps_its_source(self, odoo_env):
        register = odoo_env["fix.mushak.register"]
        first = register.consume_invoice_created(_invoice_event(odoo_env, "2026-000040", "evt-a"))
        again = register.consume_invoice_created(_invoice_event(odoo_env, "2026-000040", "evt-b"))
        assert again == first
        assert first.source_event_id == "evt-a"

    def test_mark_posted_publishes_registration(self, odoo_env):
        """A08 M51-2 (M04): `posted` needs the posted GL entry of the supply.
        Without one the row is refused; with it the registration publishes."""
        row = _register_row(odoo_env, "2026-000050", date(2026, 9, 2), 1000.0, 150.0)
        with pytest.raises(UserError, match="no posted GL entry"), odoo_env.cr.savepoint():
            row.action_mark_posted()
        assert row.posted is False
        move = _posted_entry(odoo_env, 1150.0)
        row._fix_mark_posted(move)
        assert (row.posted, row.move_id) == (True, move)
        assert _events(odoo_env, "mushak.registered", row.id) == [
            {"mushak_no": "2026-000050", "vat_amount": 150.0, "invoice_date": "2026-09-02"}
        ]

    def test_rebuild_register_from_published_events(self, odoo_env):
        event = _invoice_event(odoo_env, "2026-000060")["payload"]
        publish(odoo_env, "invoice.created", "fix.ar.invoice", 60, event)
        odoo_env["fix.event.outbox"].search(
            [("event_type", "=", "invoice.created"), ("aggregate_id", "=", 60)]
        ).mark_published()
        since = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        register = odoo_env["fix.mushak.register"]
        assert register.action_rebuild_from_events(since) == 1
        assert register.search_count([("mushak_no", "=", "2026-000060")]) == 1
        # default window replays from the epoch; the replay is idempotent
        assert register.action_rebuild_from_events() >= 1
        assert register.search_count([("mushak_no", "=", "2026-000060")]) == 1


# --------------------------------------------------------------------------- fix.vat.return


def _company_env(env, name, vat=False):
    """An env on a PRIVATE company (own BIN, own OU): the shared fix_test
    database serves concurrent suites, so these tests never write the main
    company's row nor take its (company, period) return keys."""
    company = env["res.company"].create({"name": name, "vat": vat})
    env["operating.unit"].create(
        {
            "name": f"{name} OU",
            "code": f"OU{company.id}",
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    return env(context=dict(env.context, allowed_company_ids=company.ids))


@pytest.fixture
def tax_env(odoo_env):
    return _company_env(odoo_env, "M51 Tax ORM Test Co", COMPANY_BIN)


@pytest.fixture
def nobin_env(odoo_env):
    return _company_env(odoo_env, "M51 No-BIN Test Co")


class TestVatReturnPreparation:
    def test_period_sums_only_its_own_month(self, tax_env):
        """Regression: the register search had no upper bound, so the
        September return also summed October's Mushak rows."""
        _register_row(tax_env, "M-AUG", date(2026, 8, 31), 9999.0, 1499.85)
        _register_row(tax_env, "M-SEP1", date(2026, 9, 1), 1000.0, 150.0)
        _register_row(tax_env, "M-SEP2", date(2026, 9, 30), 2000.5, 300.08)
        _register_row(tax_env, "M-OCT", date(2026, 10, 1), 5000.0, 750.0)

        ret = tax_env["fix.vat.return"].action_prepare_period("2026-09", input_vat=50.25)

        assert _money(ret.total_taxable) == D("3000.50")  # 1000.00 + 2000.50
        assert _money(ret.output_vat) == D("450.08")  # 150.00 + 300.08
        assert _money(ret.input_vat) == D("50.25")
        assert _money(ret.net_payable) == D("399.83")  # 450.08 - 50.25
        assert ret.nil_return is False
        assert ret.due_date == date(2026, 10, 15)  # a Thursday: no rollover
        assert (ret.state, ret.subledger_status) == ("prepared", "pending")
        assert _events(tax_env, "vat_return.prepared", ret.id) == [
            {"period": "2026-09", "net_payable": 399.83, "nil": False, "due": "2026-10-15"}
        ]

    def test_preparation_is_idempotent_per_period(self, tax_env):
        first = tax_env["fix.vat.return"].action_prepare_period("2026-09", input_vat=0.0)
        _register_row(tax_env, "M-LATE", date(2026, 9, 20), 100.0, 15.0)
        again = tax_env["fix.vat.return"].action_prepare_period("2026-09", input_vat=0.0)
        assert again == first
        assert _money(again.output_vat) == D("0.00")

    def test_december_nil_return_rolls_into_next_year(self, tax_env):
        _register_row(tax_env, "M-JAN", date(2027, 1, 1), 100.0, 15.0)
        ret = tax_env["fix.vat.return"].action_prepare_period("2026-12", input_vat=0.0)
        assert ret.nil_return is True
        assert _money(ret.net_payable) == D("0.00")
        assert ret.due_date == date(2027, 1, 17)  # 15 Jan 2027 is a Friday -> Sun 17

    def test_company_bin_is_never_invented(self, nobin_env):
        """Regression: a company without a BIN prepared its return under
        the placeholder BIN 0000000000000."""
        with pytest.raises(UserError, match="no valid 13-digit BIN"), nobin_env.cr.savepoint():
            nobin_env["fix.vat.return"].action_prepare_period("2026-09", input_vat=0.0)

    def test_input_vat_is_never_defaulted(self, tax_env):
        """Regression: input VAT silently defaulted to 0.00, over-declaring
        the net payable whenever the caller forgot the purchase side."""
        with pytest.raises(UserError, match="Input VAT for 2026-09 must be supplied"):
            tax_env["fix.vat.return"].action_prepare_period("2026-09")
        assert not tax_env["fix.vat.return"].search([("period", "=", "2026-09")])

    def test_rows_are_classified_by_treatment_not_lumped_into_standard(self, tax_env):
        """Regression: every register row was declared on the standard_15
        line whatever its real treatment."""
        _register_row(
            tax_env,
            "M-STD",
            date(2026, 9, 2),
            1000.0,
            150.0,
            treatment_summary="SVC: standard_15 @ 15%",
        )
        _register_row(
            tax_env,
            "M-RED",
            date(2026, 9, 3),
            2000.0,
            150.0,
            treatment_summary="PART-A: reduced @ 7.5%\nPART-B: reduced @ 7.5%",
        )
        _register_row(
            tax_env, "M-EXM", date(2026, 9, 4), 500.0, 0.0, treatment_summary="EDU: exempt @ 0%"
        )
        _register_row(tax_env, "M-NOSUM", date(2026, 9, 5), 400.0, 60.0)  # 15% by rate
        _register_row(tax_env, "M-ZERO", date(2026, 9, 6), 300.0, 0.0)  # 0%, no summary
        _register_row(
            tax_env,
            "M-MIX",
            date(2026, 9, 7),
            1000.0,
            100.0,
            treatment_summary="A: standard_15 @ 15%\nB: exempt @ 0%",
        )

        ret = tax_env["fix.vat.return"].action_prepare_period("2026-09", input_vat=0.0)

        assert json.loads(ret.treatment_breakdown) == {
            "standard_15": ["1400.00", "210.00"],
            "reduced_7.5": ["2000.00", "150.00"],
            "exempt": ["500.00", "0.00"],
            "unclassified_rate_0": ["300.00", "0.00"],
            "unclassified_mixed_rate_10": ["1000.00", "100.00"],
        }
        assert _money(ret.total_taxable) == D("5200.00")
        assert _money(ret.output_vat) == D("460.00")
        assert "unclassified_mixed_rate_10, unclassified_rate_0" in ret.classification_notes
        # unclassified supplies are not filed on a guessed line
        with pytest.raises(UserError, match="no determinable VAT treatment"):
            ret.action_file_online(client=_StubClient())
        assert ret.state == "prepared"


class TestVatReturnFiling:
    def _return(self, env, gl=(450.0, 50.0), **vals):
        """A prepared return (system arrangement) whose VAT GL carries
        `gl` = (output, input): filing recomputes the reconciliation."""
        if gl is not None:
            _vat_gl(env, output_posted=gl[0], input_posted=gl[1])
        base = {
            "period": "2026-09",
            "total_taxable": 3000.0,
            "output_vat": 450.0,
            "input_vat": 50.0,
            "net_payable": 400.0,
            "state": "prepared",
            "treatment_breakdown": json.dumps({"standard_15": ["3000.0", "450.0"]}),
        }
        base.update(vals)
        return env["fix.vat.return"].create(base)

    def test_manual_confirmation_is_mandatory(self, tax_env):
        """A08 M51-1: a user never files on a typed confirmation (online only);
        the system entry point still needs a reference and the filing gate."""
        ret = self._return(tax_env)
        accountant = (
            tax_env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M51 typed filer",
                    "login": "m51-typed-filer",
                    "group_ids": [(6, 0, [tax_env.ref("account.group_account_user").id])],
                    "company_ids": [(6, 0, tax_env.companies.ids)],
                    "company_id": tax_env.company.id,
                }
            )
        )
        with pytest.raises(UserError, match="typed confirmation"), tax_env.cr.savepoint():
            ret.with_user(accountant).action_file("TYPED-12345")
        with (
            pytest.raises(UserError, match="NBR portal confirmation reference"),
            tax_env.cr.savepoint(),
        ):
            ret.action_file("")
        ret.action_file("NBR-MANUAL-2026-09")
        assert (ret.state, ret.nbr_confirmation) == ("filed", "NBR-MANUAL-2026-09")
        assert _events(tax_env, "vat_return.filed", ret.id) == [
            {"period": "2026-09", "nbr_confirmation": "NBR-MANUAL-2026-09", "net_payable": 400.0}
        ]

    def test_online_filing_fails_closed_unconfigured(self, tax_env, monkeypatch):
        """R01 re-audit: the adapter no longer self-mints NBR acceptance; with
        no endpoint configured the filing must be refused outright."""
        from odoo.exceptions import UserError

        monkeypatch.setenv("FIX_ENV", "local")
        monkeypatch.delenv("FIX_NBR_EVAT_API_URL", raising=False)
        _set_declarant(tax_env)
        ret = self._return(tax_env)
        with pytest.raises(UserError, match="NBR endpoint not configured"):
            ret.action_file_online()
        assert ret.state == "prepared"  # untouched by the refusal

    def test_online_filing_through_wire_client(self, tax_env, monkeypatch):
        """The full online path over a WIRE-STUB client at the adapter seam:
        the token below comes from the stubbed wire response, never minted
        locally (the adapter's own suite tests the real HTTP contract)."""
        from odoo.addons.cd_tax_engine_bd.models import fix_tax_returns

        monkeypatch.setenv("FIX_ENV", "local")
        monkeypatch.setenv("FIX_NBR_EVAT_API_URL", "http://nbr-wire.test/api")

        from types import SimpleNamespace

        class _WireClient:
            def build_payload(self, **kwargs):
                return {"period": kwargs.get("period", "2026-09")}

            def submit_return(self, payload):
                # Protocol-typed structurally: attributes are what filing reads.
                return SimpleNamespace(
                    status="ACCEPTED",
                    ack_token="NBR-WIRE-202609-XYZ",  # gitleaks:allow
                    filed_at="2026-10-22T00:00:00+00:00",
                )

        monkeypatch.setattr(fix_tax_returns, "_default_evat_client", lambda: _WireClient())
        ret = self._return(tax_env)
        result = ret.action_file_online()
        assert result["status"] == "success"
        assert result["period"] == "2026-09"
        assert result["token"] == "NBR-WIRE-202609-XYZ"
        assert (ret.state, ret.nbr_confirmation) == ("filed", "NBR-WIRE-202609-XYZ")
        (event,) = _events(tax_env, "vat_return.filed_online", ret.id)
        assert event["token"] == "NBR-WIRE-202609-XYZ"

    def test_default_client_is_the_sandboxed_adapter(self, monkeypatch):
        from odoo.addons.cd_tax_engine_bd.models import fix_tax_returns

        monkeypatch.setenv("FIX_ENV", "local")
        monkeypatch.delenv("FIX_NBR_EVAT_API_URL", raising=False)
        adapter_src = str(fix_tax_returns.EVAT_ADAPTER_SRC)
        monkeypatch.setattr(sys, "path", [p for p in sys.path if p != adapter_src])
        first = fix_tax_returns._default_evat_client()
        assert sys.path[0] == adapter_src
        second = fix_tax_returns._default_evat_client()  # adapter path already registered
        assert sys.path.count(adapter_src) == 1
        assert type(first).__name__ == "Int038EvatClient"
        assert first.sandbox_mode is True and second.sandbox_mode is True

    def test_online_filing_sends_the_return_figures(self, tax_env):
        client = _StubClient()
        _set_declarant(tax_env)
        ret = self._return(tax_env)
        ret.action_file_online(client=client)
        assert client.built == {
            "taxpayer_bin": COMPANY_BIN,
            "taxpayer_name": tax_env.company.name,
            "tax_period": "2026-09",
            "register_totals": {"standard_15": (D("3000.0"), D("450.0"))},
            "input_vat": D("50.0"),
            **DECLARANT,
        }
        assert ret.nbr_confirmation == "ACK-STUB-1"

    def test_online_filing_without_a_configured_declarant_is_refused(self, tax_env, monkeypatch):
        """The adapter no longer invents a declarant: with none configured the
        filing is refused and the return stays prepared."""
        from odoo.exceptions import UserError

        monkeypatch.setenv("FIX_ENV", "local")
        monkeypatch.delenv("FIX_NBR_EVAT_API_URL", raising=False)
        ret = self._return(tax_env)
        with pytest.raises(UserError, match="Declarant name is required"), tax_env.cr.savepoint():
            ret.action_file_online()
        assert ret.state == "prepared"

    def test_return_without_matching_breakdown_is_not_filed(self, tax_env):
        """Regression: filing declared the whole return on the 15% line even
        when no per-treatment breakdown existed."""
        ret = self._return(tax_env, gl=None, treatment_breakdown=False)
        client = _StubClient()
        with pytest.raises(UserError, match="no per-treatment breakdown"), tax_env.cr.savepoint():
            ret.action_file_online(client=client)
        assert client.built is None and ret.state == "prepared"

    def test_already_filed_return_refused(self, tax_env):
        ret = self._return(tax_env, gl=None, state="filed")
        with pytest.raises(UserError, match="already filed"), tax_env.cr.savepoint():
            ret.action_file_online(client=_StubClient())

    def test_unreconciled_subledger_blocks_filing(self, tax_env):
        """A08 M51-1 (M07): the status is recomputed at filing, so a typed
        'reconciled' cannot pass a GL that disagrees."""
        ret = self._return(tax_env, gl=(300.0, 50.0), subledger_status="reconciled")
        with pytest.raises(UserError, match="IRB-09"), tax_env.cr.savepoint():
            ret.action_file_online(client=_StubClient())
        assert ret.state == "prepared"

    def test_online_filing_without_company_bin_refused(self, nobin_env):
        """Regression: filing fell back to the invented BIN 1000000000000."""
        ret = self._return(nobin_env, gl=None)
        with pytest.raises(UserError, match="no valid 13-digit BIN"), nobin_env.cr.savepoint():
            ret.action_file_online(client=_StubClient())

    def test_adapter_initialisation_failure(self, tax_env, monkeypatch):
        from odoo.addons.cd_tax_engine_bd.models import fix_tax_returns

        def broken():
            raise ImportError("evat_client not deployed")

        monkeypatch.setattr(fix_tax_returns, "_default_evat_client", broken)
        ret = self._return(tax_env)
        with (
            pytest.raises(UserError, match="Failed to initialize INT-038 e-VAT client"),
            tax_env.cr.savepoint(),
        ):
            ret.action_file_online()
        assert ret.state == "prepared"

    def test_adapter_validation_error_is_surfaced(self, tax_env):
        ret = self._return(tax_env)
        with (
            pytest.raises(UserError, match="rejected return 2026-09: arithmetic mismatch"),
            tax_env.cr.savepoint(),
        ):
            ret.action_file_online(client=_StubClient(raises=ValueError("arithmetic mismatch")))
        assert ret.state == "prepared"

    def test_rejected_submission_is_surfaced(self, tax_env):
        ret = self._return(tax_env)
        with (
            pytest.raises(UserError, match="rejected return 2026-09: BIN suspended"),
            tax_env.cr.savepoint(),
        ):
            ret.action_file_online(
                client=_StubClient(status="REJECTED", messages=["BIN suspended"])
            )
        with (
            pytest.raises(UserError, match="rejected return 2026-09: REJECTED"),
            tax_env.cr.savepoint(),
        ):
            ret.action_file_online(client=_StubClient(status="REJECTED"))
        assert ret.state == "prepared"


class _StubResult:
    def __init__(self, status, messages):
        self.status = status
        self.ack_token = "ACK-STUB-1"
        self.filed_at = "2026-10-12T09:00:00+00:00"
        self.validation_messages = messages


class _StubClient:
    """Stands in for the INT-038 adapter (no network)."""

    def __init__(self, status="ACCEPTED", messages=None, raises=None):
        self.status = status
        self.messages = messages or []
        self.raises = raises
        self.built = None

    def build_payload(self, **kwargs):
        self.built = kwargs
        return kwargs

    def submit_return(self, payload):
        if self.raises:
            raise self.raises
        return _StubResult(self.status, self.messages)


def _vat_gl(env, output_posted=None, input_posted=None, when="2026-09-15"):
    """The private company's VAT GL accounts (210100 / 110500), optionally
    with a posted entry carrying the given output / input VAT."""
    company = env.company
    Account = env["account.account"]

    def acc(code, name, account_type):
        return Account.create(
            {
                "code": code,
                "name": name,
                "account_type": account_type,
                "company_ids": [(6, 0, company.ids)],
            }
        )

    out_acc = acc("210100", "VAT Output Payable", "liability_current")
    in_acc = acc("110500", "VAT Input Credit", "asset_current")
    # A08 M51-8: the input-VAT role has no default code: it is configured
    icp = env["ir.config_parameter"].sudo()
    icp.set_param("cd_tax_engine_bd.vat_input_account_code", "110500")
    bank = acc("100199", "Clearing", "asset_current")
    journal = env["account.journal"].create(
        {"name": "VAT test", "code": "VATT", "type": "general", "company_id": company.id}
    )
    if output_posted is not None or input_posted is not None:
        out_amt, in_amt = output_posted or 0.0, input_posted or 0.0
        move = env["account.move"].create(
            {
                "journal_id": journal.id,
                "date": when,
                "line_ids": [
                    (0, 0, {"name": "out", "account_id": out_acc.id, "credit": out_amt}),
                    (0, 0, {"name": "in", "account_id": in_acc.id, "debit": in_amt}),
                    (0, 0, {"name": "bal", "account_id": bank.id, "debit": out_amt - in_amt}),
                ],
            }
        )
        move.action_post()
    return out_acc, in_acc


class TestVatSubledger:
    def _return(self, env):
        return env["fix.vat.return"].create(
            {"period": "2026-09", "output_vat": 1500.0, "input_vat": 200.0, "state": "prepared"}
        )

    def test_full_alignment_against_the_posted_gl(self, tax_env):
        _vat_gl(tax_env, output_posted=1500.0, input_posted=200.0)
        ret = self._return(tax_env)
        ret.action_subledger_reconciliation()
        assert ret.subledger_status == "reconciled"
        assert _money(ret.subledger_output_variance) == D("0.00")
        assert ret.subledger_notes == "Full alignment between Mushak sub-ledger and General Ledger."
        (event,) = _events(tax_env, "vat_subledger.reconciled", ret.id)
        assert event["is_reconciled"] is True

    def test_return_is_not_compared_with_itself(self, tax_env):
        """Regression: called without GL figures (as the form button does),
        the return was compared with ITSELF and always 'reconciled'. With an
        empty GL the register VAT is a variance."""
        _vat_gl(tax_env)
        ret = self._return(tax_env)
        ret.action_subledger_reconciliation()
        assert ret.subledger_status == "variance_detected"
        assert _money(ret.subledger_output_variance) == D("1500.00")
        assert _money(ret.subledger_input_variance) == D("200.00")

    def test_gl_outside_the_period_is_ignored(self, tax_env):
        _vat_gl(tax_env, output_posted=1500.0, input_posted=200.0, when="2026-10-01")
        ret = self._return(tax_env)
        ret.action_subledger_reconciliation()
        assert ret.subledger_status == "variance_detected"

    def test_variance_is_raised_never_absorbed(self, tax_env):
        _vat_gl(tax_env, output_posted=1400.0, input_posted=200.5)
        ret = self._return(tax_env)
        ret.action_subledger_reconciliation()
        assert ret.subledger_status == "variance_detected"
        assert _money(ret.subledger_output_variance) == D("100.00")  # 1500.00 - 1400.00
        assert _money(ret.subledger_input_variance) == D("-0.50")  # 200.00 - 200.50
        assert ret.subledger_notes == (
            "GL 210100 Output VAT variance: subledger=1500.00, gl=1400.00, delta=100.00; "
            "GL 110500 Input VAT variance: subledger=200.00, gl=200.50, delta=-0.50"
        )
        (event,) = _events(tax_env, "vat_subledger.variance_detected", ret.id)
        assert (event["output_variance"], event["input_variance"]) == (100.0, -0.5)

    def test_unconfigured_gl_accounts_refuse(self, tax_env):
        ret = self._return(tax_env)
        with pytest.raises(UserError, match="No GL account for the vat_"), tax_env.cr.savepoint():
            ret.action_subledger_reconciliation()
        assert ret.subledger_status == "pending"


# --------------------------------------------------------------------------- TDS


class TestTdsReturn:
    def test_prepare_quarter(self, odoo_env):
        tds = odoo_env["fix.tds.return"].action_prepare_quarter(
            {"VENDOR-1": D("1000.00"), "VENDOR-2": D("250.50")}, date(2026, 8, 10)
        )
        assert (tds.quarter, tds.fiscal_year) == ("2026-Q1", "FY2027")
        assert _money(tds.total_withheld) == D("1250.50")
        assert tds.deductor_count == 2
        assert tds.due_date == date(2026, 10, 25)  # a Sunday: a BD working day
        assert tds.state == "prepared"
        again = odoo_env["fix.tds.return"].action_prepare_quarter({}, date(2026, 9, 1))
        assert again == tds

    def test_file_requires_a_real_acknowledgment(self, odoo_env):
        """Regression: filing without an acknowledgment minted
        NBR-TDS-<quarter>-<id> and recorded the return as filed."""
        model = odoo_env["fix.tds.return"]
        # prepared returns (system arrangement): A08 M51-1 files only from prepared
        q1 = model.create(
            {
                "quarter": "2026-Q1",
                "fiscal_year": "FY2027",
                "total_withheld": 10.0,
                "state": "prepared",
            }
        )
        q2 = model.create({"quarter": "2026-Q2", "fiscal_year": "FY2027", "state": "prepared"})
        q3 = model.create({"quarter": "2026-Q3", "fiscal_year": "FY2027", "state": "prepared"})
        q1.action_file("NBR-ACK-778")
        with (
            pytest.raises(UserError, match="Enter the NBR acknowledgment number"),
            odoo_env.cr.savepoint(),
        ):
            q2.action_file()
        assert (q2.state, q2.nbr_acknowledgment) == ("prepared", False)
        # the form route: the user keys the number in, then presses the button
        q3.nbr_acknowledgment = "NBR-TDS-ACK-9912"
        q3.action_file()
        assert (q3.state, q3.nbr_acknowledgment) == ("filed", "NBR-TDS-ACK-9912")
        with pytest.raises(UserError, match="already filed"), odoo_env.cr.savepoint():
            q3.action_file()
        assert (q1.state, q1.nbr_acknowledgment) == ("filed", "NBR-ACK-778")
        assert _events(odoo_env, "tds_return.filed", q1.id) == [
            {
                "quarter": "2026-Q1",
                "fiscal_year": "FY2027",
                "total_withheld": 10.0,
                "nbr_acknowledgment": "NBR-ACK-778",
            }
        ]

    def test_return_line_section_default(self, odoo_env):
        tds = odoo_env["fix.tds.return"].create({"quarter": "2026-Q3"})
        line = odoo_env["fix.tds.return.line"].create(
            {
                "tds_return_id": tds.id,
                "vendor_name": "Apex Logistics",
                "base_amount": 20000.0,
                "rate_percent": 5.0,
                "tds_amount": 1000.0,
            }
        )
        assert line.section_code == "52"
        assert tds.line_ids == line


# --------------------------------------------------------------------------- certificates


def _vendor_invoice(env):
    vendor = env["res.partner"].create({"name": "Apex Logistics Ltd."})
    return env["fix.vendor.invoice"].create(
        {"operating_unit_id": _ou(env).id, "vendor_id": vendor.id, "invoice_ref": "AP-1001"}
    )


def _deposited_certificate(env, **vals):
    """A draft certificate for a deduction its verified challan deposited
    (system arrangement: A08 M51-4 issues no free-standing certificate)."""
    invoice = _vendor_invoice(env)
    challan = env["fix.tax.challan"].create(
        {
            "challan_no": "CH-CERT-%s" % invoice.id,
            "challan_date": date(2026, 9, 20),
            "tax_kind": "vds",
            "amount": 15000.0,
            "state": "deposited",
            "verification_ref": "IBAS-OK",
            "verified_by_id": env.uid,
        }
    )
    rate = env.ref("cd_tax_engine_bd.tax_rate_vds_rent")
    line = env["fix.withholding.line"].create(
        {
            "tax_kind": "vds",
            "partner_id": invoice.vendor_id.id,
            "partner_tin": "123456789012",
            "psr_received": True,
            "paid_by_bank": True,
            "rate_id": rate.id,
            "document_date": date(2026, 9, 10),
            "base_amount": 100000.0,
            "amount": 15000.0,
            "vendor_invoice_id": invoice.id,
            "challan_id": challan.id,
            "state": "deposited",
        }
    )
    base = {
        "vendor_invoice_id": invoice.id,
        "supplier_name": "Apex Logistics Ltd.",
        "supplier_bin": COMPANY_BIN,
        "base_amount": 100000.0,
        "rate_percent": 15.0,
        "withheld_amount": 15000.0,
        "challan_no": challan.challan_no,
    }
    base.update(vals)
    cert = env["fix.withholding.certificate"].create(base)
    line.certificate_id = cert
    return cert


class TestWithholdingCertificate:
    def _cert(self, env, **vals):
        return _deposited_certificate(env, **vals)

    def test_free_standing_certificate_is_never_issued(self, odoo_env):
        """A08 M51-4 (W03): a certificate with no deposited deduction is refused."""
        cert = odoo_env["fix.withholding.certificate"].create(
            {
                "vendor_invoice_id": _vendor_invoice(odoo_env).id,
                "supplier_name": "Any supplier",
                "supplier_bin": COMPANY_BIN,
                "withheld_amount": 7750.0,
            }
        )
        with pytest.raises(UserError, match="certifies no deduction"), odoo_env.cr.savepoint():
            cert.action_issue()

    def test_mushak_66_numbering_and_event(self, odoo_env):
        cert = self._cert(odoo_env)
        cert.action_issue()
        assert cert.state == "issued"
        assert cert.certificate_no == "VDS-6.6/%s/%05d" % (date.today().strftime("%Y%m"), cert.id)
        assert _events(odoo_env, "withholding_certificate.issued", cert.id) == [
            {
                "certificate_no": cert.certificate_no,
                "certificate_type": "mushak_6_6",
                "supplier_name": "Apex Logistics Ltd.",
                "supplier_bin": COMPANY_BIN,
                "amount": 15000.0,
                "base_amount": 100000.0,
            }
        ]
        cert.action_issue()  # already issued: skipped, no second certificate
        assert len(_events(odoo_env, "withholding_certificate.issued", cert.id)) == 1

    def test_mushak_66_requires_supplier_bin(self, odoo_env):
        cert = self._cert(odoo_env, supplier_bin="12345")
        with (
            pytest.raises(UserError, match="13-digit supplier BIN under Rule 40"),
            odoo_env.cr.savepoint(),
        ):
            cert.action_issue()

    def test_section_52_tin_rules(self, odoo_env):
        no_tin = self._cert(odoo_env, certificate_type="section_52_income_tax", supplier_bin=False)
        no_tin.action_issue()
        assert no_tin.certificate_no.startswith("TDS-52/")
        bad_tin = self._cert(
            odoo_env, certificate_type="section_52_income_tax", supplier_tin="12AB"
        )
        with pytest.raises(UserError, match="12-digit e-TIN"), odoo_env.cr.savepoint():
            bad_tin.action_issue()
        good_tin = self._cert(
            odoo_env, certificate_type="section_52_income_tax", supplier_tin="123456789012"
        )
        good_tin.action_issue()
        assert good_tin.state == "issued"
