"""Shared M40 test set-up (A04 ERP audit, 20 Nov 2026).

Since M40-F11 a partner is onboarded only when it is bound to a published
programme, its M08 agreement is in force and its onboarding checklist is
done; since M40-F5 a commission rate is a routed decision; since M40-F12 a
rebate basis is read from paid M20 invoices. Tests that exercise something
else prepare those preconditions here, as the system (they are not what the
test proves)."""

from datetime import timedelta

from odoo import fields

PAYOUT_PARAMS = {
    "cd_settlement_ext.account_code.partner_rebate_payout": "500306",
    "cd_settlement_ext.account_code.partner_mdf_expense": "500210",
    "cd_settlement_ext.account_code.partner_payable": "200202",
    "cd_settlement_ext.account_code.tds_payable": "200905",
    "cd_partner.account_code.royalty_income": "400109",
    "cd_partner.account_code.franchise_fee_income": "400109",
}
ACCOUNT_TYPES = {
    "500306": ("Sales Commission", "expense"),
    "500210": ("Marketing Expense", "expense"),
    "200202": ("Accrued - Commissions", "liability_current"),
    "200905": ("Tax Payable", "liability_current"),
    "400109": ("Other Income", "income_other"),
}


def ensure_account(env, code, company=None):
    company = company or env.company
    Account = env["account.account"].sudo().with_company(company)
    acc = Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    if not acc:
        name, atype = ACCOUNT_TYPES[code]
        acc = Account.create(
            {
                "code": code,
                "name": name,
                "account_type": atype,
                "company_ids": [(6, 0, [company.id])],
            }
        )
    return acc


def configure_payout_accounts(env, company=None):
    params = env["ir.config_parameter"].sudo()
    for key, code in PAYOUT_PARAMS.items():
        ensure_account(env, code, company)
        params.set_param(key, code)


def guarded_write(rec, vals):
    rec = rec.sudo()
    (rec._guarded() if hasattr(rec, "_guarded") else rec).write(vals)


def published_programme(env, ptype, company=None):
    Prog = env["fix.partner.programme"].sudo()
    prog = Prog.search(
        [("partner_type", "=", ptype), ("state", "=", "published"), ("code", "=like", "TST-%")],
        limit=1,
    )
    if prog:
        return prog
    prog = Prog.create(
        {
            "name": "Test %s programme" % ptype,
            "code": "TST-%s" % ptype.upper(),
            "partner_type": ptype,
            "entry_criteria": "Test criteria",
            "company_id": (company or env.company).id,
            "tier_ids": [(0, 0, {"code": "T1", "name": "Tier 1", "criteria": "c1"})],
        }
    )
    guarded_write(prog, {"state": "published"})
    return prog


def agreement(env, party, company=None):
    company = company or env.company
    ou = env["operating.unit"].sudo().search([("company_id", "=", company.id)], limit=1)
    today = fields.Date.context_today(env.user)
    contract = (
        env["fix.contract"]
        .sudo()
        .create(
            {
                "name": "Partner agreement %s" % party.name,
                "family": "amc",
                "customer_id": party.id,
                "operating_unit_id": ou.id,
                "company_id": company.id,
                "date_start": today - timedelta(days=1),
                "date_end": today + timedelta(days=365),
                "annual_value": 1.0,
            }
        )
    )
    guarded_write(contract, {"state": "active"})
    return contract


def make_onboardable(env, partner, checklist=True):
    """Programme, agreement in force and (unless checklist=False) a done
    checklist - as the system."""
    partner = partner.sudo()
    vals = {}
    if not partner.programme_id:
        vals["programme_id"] = published_programme(env, partner.partner_type).id
    if not partner.contract_id or partner.contract_id.state not in ("active", "expiring"):
        vals["contract_id"] = agreement(env, partner.partner_id, partner.company_id).id
    if vals:
        guarded_write(partner, vals)
    if not checklist:
        return partner
    Step = env["fix.partner.onboarding"].sudo()
    if not partner.onboarding_ids:
        Step.create({"partner_id": partner.id, "step": "documents", "name": "Statutory documents"})
    for step in partner.onboarding_ids.filtered(lambda s: s.required and s.state != "done"):
        guarded_write(step, {"state": "done"})
    return partner


def approved_rate(partner, rate):
    """The partner's approved commission rate (the routed decision is
    M40-F5's own test)."""
    guarded_write(partner, {"commission_rate": rate})


def paid_invoice(env, party, amount, on_date=None, company=None, ou=None):
    """A paid M20 invoice of `party` (taxable `amount`), dated `on_date`."""
    company = company or env.company
    on_date = on_date or fields.Date.context_today(env.user)
    Invoice = env["fix.ar.invoice"].sudo()
    inv = Invoice._fix_draft_invoice_from_source(
        "test.m40",
        "test-%s-%s-%s" % (party.id, amount, Invoice.search_count([]) + 1),
        party,
        [{"description": "Test supply", "taxable_amount": amount}],
        "Test invoice",
        company=company,
        operating_unit=ou,
        invoice_date=on_date,
    )
    guarded_write(inv, {"state": "paid"})
    return env["fix.ar.invoice"].browse(inv.id)


CONSENT = {"consent_given": True, "consent_method": "written"}
