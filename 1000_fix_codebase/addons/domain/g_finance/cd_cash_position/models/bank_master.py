# cd_cash_position — Bank Account Master (A08 · M50): the finance view over
# Odoo's own bank journals (account.journal, type bank) and bank accounts
# (res.partner.bank), with the Bangladesh fields treasury needs: the 9-digit
# branch routing number (BEFTN/RTGS) and the account type.
from __future__ import annotations

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .treasury_common import gl_balance

BD_ACCOUNT_TYPES = [
    ("current", "Current Account (CD)"),
    ("savings", "Savings Account (SB)"),
    ("snd", "Short Notice Deposit (SND)"),
    ("fdr", "Fixed Deposit (FDR)"),
    ("od_cc", "Overdraft / Cash Credit"),
    ("mfs_wallet", "MFS Merchant Wallet"),
    ("gateway", "Payment Gateway Merchant Account"),
]
ROUTING_RE = re.compile(r"^\d{9}$")


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    fix_routing_number = fields.Char(
        string="Routing Number",
        size=9,
        help="Bangladesh Bank 9-digit branch routing number (BEFTN / RTGS)",
    )
    fix_branch_name = fields.Char(string="Bank Branch")
    fix_account_type = fields.Selection(BD_ACCOUNT_TYPES, string="BD Account Type")

    @api.constrains("fix_routing_number")
    def _check_fix_routing_number(self):
        for acct in self:
            if acct.fix_routing_number and not ROUTING_RE.match(acct.fix_routing_number):
                raise ValidationError(
                    "Routing number %s must be exactly 9 digits." % acct.fix_routing_number
                )


class AccountJournal(models.Model):
    _inherit = "account.journal"

    fix_routing_number = fields.Char(
        related="bank_account_id.fix_routing_number", readonly=False, string="Routing Number"
    )
    fix_branch_name = fields.Char(
        related="bank_account_id.fix_branch_name", readonly=False, string="Bank Branch"
    )
    fix_account_type = fields.Selection(
        related="bank_account_id.fix_account_type", readonly=False, string="BD Account Type"
    )
    fix_treasury_role = fields.Selection(
        [
            ("operating", "Operating"),
            ("collection", "Collection"),
            ("payroll", "Payroll"),
            ("mfs_wallet", "MFS Wallet"),
            ("gateway", "Gateway Settlement"),
            ("deposit", "Term Deposit"),
        ],
        string="Treasury Role",
    )
    fix_signatories = fields.Char(string="Authorised Signatories")
    fix_company_currency_id = fields.Many2one(
        related="company_id.currency_id", string="Company Currency"
    )
    fix_gl_balance = fields.Monetary(
        string="GL Balance",
        compute="_compute_fix_treasury",
        currency_field="fix_company_currency_id",
        help="Posted balance of the journal's GL account (company currency)",
    )
    fix_foreign_balance = fields.Monetary(
        string="Foreign-Currency Balance",
        compute="_compute_fix_treasury",
        currency_field="currency_id",
        help="Posted amount in the journal's own currency (foreign-currency accounts)",
    )
    fix_unmatched_lines = fields.Integer(
        string="Unmatched Statement Lines", compute="_compute_fix_treasury"
    )

    def _compute_fix_treasury(self):
        Line = self.env["fix.bank.statement.line"]
        for journal in self:
            account = journal.default_account_id
            journal.fix_gl_balance = gl_balance(self.env, account, journal.company_id)
            foreign = 0.0
            if (
                account
                and journal.currency_id
                and journal.currency_id != journal.company_id.currency_id
            ):
                groups = self.env["account.move.line"]._read_group(
                    [
                        ("account_id", "=", account.id),
                        ("parent_state", "=", "posted"),
                        ("currency_id", "=", journal.currency_id.id),
                    ],
                    [],
                    ["amount_currency:sum"],
                )
                foreign = groups[0][0] or 0.0 if groups else 0.0
            journal.fix_foreign_balance = foreign
            journal.fix_unmatched_lines = (
                Line.search_count(
                    [("journal_id", "=", journal.id), ("match_state", "=", "unmatched")]
                )
                if journal.id
                else 0
            )


class FixJournalPostingLog(models.Model):
    """Treasury postings are logged under their own source (FR-FIN-042)."""

    _inherit = "fix.journal.posting.log"

    source = fields.Selection(
        selection_add=[("treasury", "Treasury (M50)")], ondelete={"treasury": "set default"}
    )
