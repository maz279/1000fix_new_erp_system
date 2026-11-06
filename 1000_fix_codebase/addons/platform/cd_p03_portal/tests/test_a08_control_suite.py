# A08 control suite (A08 workflow audit, P0 F3/F6 and P3): one sweep over
# EVERY workflow-controlled field of the A08 Finance surfaces, run as a
# non-admin user.
#
# The A08 audit (2026-11-04) found 0 of 97 finance models guarded and no write
# whitelist: an accountant forged a bill's approval, a payment's state and a
# statement line's match, and plain users wrote five finance models. Per
# guarded field a changing write() is refused by the guard; no workspace form
# offers it; plain users cannot write finance documents except the three an
# employee raises (an expense claim, a referral, a subscription), whose
# workflow fields are guarded. Behaviour tests live in each finance addon's
# tests/test_a08_*_controls.py.

import itertools

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a08
from odoo.addons.cd_p03_portal.controllers.a08.writable import WRITABLE
from odoo.exceptions import UserError

_SEQ = itertools.count(1)
# fix.mushak.register refuses `posted` by what it needs (a posted GL entry) before
# the generic guard answers, which is the stricter of the two refusals.
GUARD_MESSAGE = "changes only through its workflow|cannot be marked posted"
SIMPLE = {
    "char",
    "text",
    "boolean",
    "selection",
    "integer",
    "float",
    "monetary",
    "date",
    "datetime",
    "many2one",
}

# The 71 models the audit's exposure sweep found with an open workflow field
# (working/A08_evidence/probes/cross_area/a08_exposure_sweep.out.txt).
EXPOSED = (
    "fix.allocation.rule",
    "fix.ar.consolidated.bill",
    "fix.ar.dispute",
    "fix.ar.impairment",
    "fix.ar.invoice",
    "fix.ar.payment.link",
    "fix.ar.receipt",
    "fix.asset.depreciation.run",
    "fix.asset.disposal",
    "fix.asset.revaluation",
    "fix.asset.tax.rate",
    "fix.asset.transfer",
    "fix.asset.verification.campaign",
    "fix.asset.verification.line",
    "fix.bank.facility",
    "fix.bank.statement.import",
    "fix.bank.statement.line",
    "fix.board.pack",
    "fix.budget.version",
    "fix.capex.budget",
    "fix.capex.request",
    "fix.cash.deposit",
    "fix.chart.loader",
    "fix.cheque",
    "fix.cod.settlement",
    "fix.commission.ledger",
    "fix.consolidation.book",
    "fix.cost.allocation",
    "fix.credit.note",
    "fix.cwip.entry",
    "fix.employee.advance",
    "fix.expense.claim",
    "fix.facility.repayment",
    "fix.fiscal.period.bridge",
    "fix.fixed.asset",
    "fix.fx.revaluation",
    "fix.gateway.settlement",
    "fix.gateway.settlement.line",
    "fix.imprest.count",
    "fix.imprest.fund",
    "fix.imprest.topup",
    "fix.imprest.voucher",
    "fix.input.vat.credit",
    "fix.intercompany.transaction",
    "fix.journal.template",
    "fix.lease",
    "fix.lease.schedule.line",
    "fix.mushak.register",
    "fix.nil.return.generator",
    "fix.payment.execution",
    "fix.payment.run",
    "fix.payout.reconciliation",
    "fix.payout.run",
    "fix.performance.obligation",
    "fix.period.close",
    "fix.referral",
    "fix.revenue.schedule",
    "fix.seller.statement",
    "fix.settlement.adjustment",
    "fix.subscription",
    "fix.tax.audit.pack",
    "fix.tax.challan",
    "fix.tds.return",
    "fix.vat.return",
    "fix.vds.certificate.received",
    "fix.vendor.invoice",
    "fix.vendor.note",
    "fix.warranty.provision",
    "fix.withholding.certificate",
    "fix.withholding.line",
)

# An employee still raises these; their workflow fields are guarded.
EMPLOYEE_WRITABLE = {
    "fix.expense.claim",
    "fix.expense.claim.line",
    "fix.referral",
    "fix.subscription",
}


@pytest.fixture
def clerk_env(odoo_env):
    n = next(_SEQ)
    user = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A08 Control Suite Clerk %d" % n,
                "login": "a08.control.suite.%d@a08.test" % n,
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    return odoo_env(user=user.id)


def _forged_value(env, field, current):
    """A value different from `current` that a forger would send."""
    if field.type == "boolean":
        return not current
    if field.type == "selection":
        values = [v for v, _l in (field._description_selection(env) or [])]
        others = [v for v in values if v != current]
        return others[-1] if others else None
    if field.type in ("integer", "float", "monetary"):
        return (current or 0) + 7
    if field.type == "date":
        return fields.Date.add(fields.Date.today(), days=-400)
    if field.type == "datetime":
        return fields.Datetime.add(fields.Datetime.now(), days=-400)
    if field.type == "many2one":
        other = env[field.comodel_name].sudo().search([], limit=2)
        other = other - current if current else other
        return other[:1].id or None
    return "forged-by-the-control-suite"


@pytest.mark.parametrize("model", EXPOSED)
def test_every_exposed_model_is_guarded(odoo_env, model):
    """S2: each model the audit found with an open workflow field now names
    it among its guarded fields."""
    assert model in odoo_env, "%s is no longer installed" % model
    record = odoo_env[model]
    assert hasattr(record, "_fix_guarded_fields"), "%s has no workflow guard" % model
    assert record.browse()._fix_guarded_fields(), "%s guards no field" % model


@pytest.mark.parametrize("model", EXPOSED)
def test_every_guarded_field_refuses_a_direct_write(odoo_env, clerk_env, model):
    """R9 b: for every guarded field, a changing write() is refused by the guard."""
    record = clerk_env[model].new({})
    guarded = sorted(record._fix_guarded_fields())
    checked = 0
    for name in guarded:
        field = record._fields.get(name)
        if not field or field.type not in SIMPLE or not field.store or field.compute:
            continue
        value = _forged_value(clerk_env, field, record[name])
        if value is None:
            continue
        with pytest.raises(UserError, match=GUARD_MESSAGE):
            record.write({name: value})
        checked += 1
    assert checked or not guarded, "%s declares guarded fields but none could be attacked" % model


@pytest.mark.parametrize("model", sorted(a08.SURFACES))
def test_no_form_offers_a_guarded_field_as_editable(odoo_env, model):
    """A workflow-owned field is never an editable input on a workspace form,
    so the screen never offers what the server refuses."""
    if not hasattr(odoo_env[model], "_fix_guarded_fields"):
        pytest.skip("%s carries no workflow-controlled fields" % model)
    guarded = odoo_env[model].browse()._fix_guarded_fields()
    offered = guarded & set(WRITABLE.get(model, ()))
    assert not offered, "the %s form offers workflow fields as editable: %s" % (
        model,
        sorted(offered),
    )


@pytest.mark.parametrize("model", sorted(a08.SURFACES))
def test_a_plain_user_cannot_write_finance_documents(odoo_env, clerk_env, model):
    """F6: finance powers belong to the finance roles. A plain employee may
    raise only an expense claim, a referral or a subscription."""
    records = clerk_env[model]
    if model in EMPLOYEE_WRITABLE:
        return
    assert not records.has_access("write"), "%s is still writable by a plain user" % model
    assert not records.has_access("create"), "%s is still creatable by a plain user" % model
