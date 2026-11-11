# cd_ap_ext — the AP sub-ledger's GL account roles and posting (CD-M52-01).
#
# Every posting goes through M19's hardened engine (post_with_dimensions,
# via the tax engine's post_tax_move). Account roles resolve from system
# parameters cd_ap_ext.account_code.<role>; a role without a configured
# (or default) account FAILS CLOSED with a UserError — nothing is posted to a
# guessed account. Tax roles (input VAT, TDS/VDS payable) are the tax
# engine's, so the AP posting and the VAT sub-ledger reconciliation agree.
from odoo import fields, models
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
    # A08 M52-8: an advance recovered through payroll clears against salaries
    # payable; Odoo generic chart: 230000 "Salary Payable"
    "salary_payable": ("230000", "Salaries payable (payroll recovery of advances)"),
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


PURCHASE_JOURNAL_PARAM = "cd_ap_ext.bill_journal_code"
# The name the first seed wrote and the databases carry. The reader looked only
# at the name above, so the configured journal was ignored; still honoured.
LEGACY_PURCHASE_JOURNAL_PARAM = "cd_ap_ext.purchase_journal_code"


def ap_journal(env, company, kind):
    """kind 'purchase': the purchase journal configured in
    cd_ap_ext.bill_journal_code (legacy name: cd_ap_ext.purchase_journal_code),
    or the company's only purchase journal — never a guess between several;
    kind 'payment': the bank journal configured in
    cd_ap_ext.payment_journal_code (required — money leaving the company is
    never posted to a guessed bank)."""
    icp = env["ir.config_parameter"].sudo()
    Journal = env["account.journal"]
    if kind == "purchase":
        code = (
            icp.get_param(PURCHASE_JOURNAL_PARAM)
            or icp.get_param(LEGACY_PURCHASE_JOURNAL_PARAM)
            or ""
        ).strip()
        domain = [("company_id", "=", company.id), ("type", "=", "purchase")]
        if code:
            journal = Journal.search([*domain, ("code", "=", code)], limit=1)
            if not journal:
                raise UserError(
                    "No purchase journal with code %s in %s for vendor bill postings (system "
                    "parameter %s). Nothing was posted."
                    % (code, company.name, PURCHASE_JOURNAL_PARAM)
                )
            return journal
        journals = Journal.search(domain, limit=2)
        if not journals:
            raise UserError(
                "No purchase journal in %s for vendor bill postings (system parameter "
                "%s). Nothing was posted." % (company.name, PURCHASE_JOURNAL_PARAM)
            )
        if len(journals) > 1:
            raise UserError(
                "%s has more than one purchase journal: set system parameter %s to the code "
                "of the journal vendor bills post to. Nothing was posted."
                % (company.name, PURCHASE_JOURNAL_PARAM)
            )
        return journals
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


def _ap_posting_dims(env):
    """Dimensions for every AP-family GL posting (the AR pattern): the
    configured default cost centre and business line, so COA-003 rules on
    tax-payable and expense accounts are satisfied. Values come from config
    params — postings never invent values beyond configured defaults."""
    param = env["ir.config_parameter"].sudo().get_param
    return {
        "cost_centre": param("cd_ap_ext.default_cost_centre")
        or param("cd_billing_engine.default_cost_centre")
        or "CORP",
        "business_line": param("cd_ap_ext.default_business_line")
        or param("cd_billing_engine.default_business_line")
        or "RETAIL",
    }


def post_ap_move(
    env, company, journal, entry_date, ref, lines, operating_unit=None, line_dimensions=None
):
    """Post a balanced AP entry; lines: [(account, label, debit, credit, partner)].
    Same engine as the tax subledger, plus the AP default cost-centre and
    business-line dimensions on every line (COA-003). line_dimensions: {index
    into `lines`: {dimension: value}} overrides them on one line (an expense
    line's own cost centre, BRU-APE-16)."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    debit = round(sum(line[2] for line in lines), 2)
    credit = round(sum(line[3] for line in lines), 2)
    if abs(debit - credit) > 0.005:
        raise UserError("Unbalanced posting refused (%.2f / %.2f)" % (debit, credit))
    ou = operating_unit or env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    move_vals = {
        "journal_id": journal.id,
        "company_id": company.id,
        "date": entry_date,
        "ref": ref,
        "move_type": "entry",
        "line_ids": [
            (
                0,
                0,
                {
                    "account_id": account.id,
                    "name": label,
                    "debit": round(dr, 2),
                    "credit": round(cr, 2),
                    "partner_id": partner.id if partner else False,
                },
            )
            for account, label, dr, cr, partner in lines
            if round(dr, 2) or round(cr, 2)
        ],
    }
    line_dims = {"operating_unit_id": ou.id} if ou else {}
    line_dims.update(_ap_posting_dims(env))
    kept = [i for i, line in enumerate(lines) if round(line[2], 2) or round(line[3], 2)]
    overrides = line_dimensions or {}
    dims = {
        position: {**line_dims, **{k: v for k, v in overrides.get(i, {}).items() if v}}
        for position, i in enumerate(kept)
    }
    move, _attached = post_with_dimensions(env, move_vals, dims, source="ap_subledger")
    return move
