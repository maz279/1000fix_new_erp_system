# cd_ap_ext — the AP sub-ledger's GL account roles and posting (CD-M52-01).
#
# Every posting goes through M19's hardened engine (post_with_dimensions,
# via the tax engine's post_tax_move). Account roles resolve from system
# parameters cd_ap_ext.account_code.<role>; a role without a configured
# (or default) account FAILS CLOSED with a UserError — nothing is posted to a
# guessed account. Tax roles (input VAT, TDS/VDS payable) are the tax
# engine's, so the AP posting and the VAT sub-ledger reconciliation agree.
from odoo import fields, models
from odoo.addons.cd_tax_engine_bd.models.fix_tax_compliance import post_tax_move
from odoo.addons.cd_tax_engine_bd.models.fix_tax_master import tax_account
from odoo.exceptions import UserError


class FixJournalPostingLogAp(models.Model):
    """The AP sub-ledger as a posting source in M19's posting log."""

    _inherit = "fix.journal.posting.log"

    source = fields.Selection(
        selection_add=[("ap_subledger", "AP Sub-ledger (M52)")],
        ondelete={"ap_subledger": lambda recs: recs.write({"source": "api"})},
    )


# role -> (default chart code or None, label)
AP_ACCOUNTS = {
    "ap": ("211000", "Trade payables (control)"),
    # Odoo generic chart: 211100 "Bills to receive" = goods received not invoiced
    "grni": ("211100", "Goods received not invoiced (GRNI clearing)"),
    "expense": (None, "Default purchase / expense account"),
    "employee_payable": (None, "Employee reimbursements payable"),
    "employee_advance": (None, "Employee advances and floats"),
}
TAX_ROLES = ("vat_input", "tds_payable", "vds_payable")


def ap_account(env, company, role):
    """The company's GL account for an AP role — refused when unconfigured."""
    if role in TAX_ROLES:
        return tax_account(env, company, role)
    default, label = AP_ACCOUNTS[role]
    param = "cd_ap_ext.account_code.%s" % role
    code = env["ir.config_parameter"].sudo().get_param(param) or default
    account = env["account.account"]
    if code:
        account = (
            env["account.account"]
            .with_company(company)
            .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        )
    if not account:
        raise UserError(
            "No GL account for %s in %s: set system parameter %s to an account code of "
            "this company's chart. Nothing was posted." % (label, company.name, param)
        )
    return account


def ap_journal(env, company, kind):
    """kind 'purchase': the company's purchase journal (or the one configured
    in cd_ap_ext.bill_journal_code); kind 'payment': the bank journal
    configured in cd_ap_ext.payment_journal_code (required — money leaving
    the company is never posted to a guessed bank)."""
    icp = env["ir.config_parameter"].sudo()
    Journal = env["account.journal"]
    if kind == "purchase":
        code = icp.get_param("cd_ap_ext.bill_journal_code")
        domain = [("company_id", "=", company.id), ("type", "=", "purchase")]
        journal = Journal.search(domain + ([("code", "=", code)] if code else []), limit=1)
        if not journal:
            raise UserError(
                "No purchase journal in %s for vendor bill postings (system parameter "
                "cd_ap_ext.bill_journal_code). Nothing was posted." % company.name
            )
        return journal
    code = icp.get_param("cd_ap_ext.payment_journal_code")
    journal = Journal
    if code:
        journal = Journal.search(
            [
                ("company_id", "=", company.id),
                ("code", "=", code),
                ("type", "in", ("bank", "cash")),
            ],
            limit=1,
        )
    if not journal or not journal.default_account_id:
        raise UserError(
            "No payment bank journal configured in %s: set system parameter "
            "cd_ap_ext.payment_journal_code to the code of the bank journal vendor and "
            "employee payments leave from. Nothing was posted." % company.name
        )
    return journal


def post_ap_move(env, company, journal, entry_date, ref, lines, operating_unit=None):
    """Post a balanced AP entry; lines: [(account, label, debit, credit, partner)]."""
    return post_tax_move(
        env, company, journal, entry_date, ref, lines, operating_unit, source="ap_subledger"
    )
