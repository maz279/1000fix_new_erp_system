# cd_cash_position — shared treasury helpers (A08 · M50).
#
# Every treasury posting resolves its GL accounts from per-deployment system
# parameters (cd_cash_position.account_code.<role>) and FAILS CLOSED when one
# is missing: nothing is posted to a guessed account. Postings go through
# M19's hardened post_with_dimensions (chart rules, dimensions, posting log).
from __future__ import annotations

import re

from odoo.exceptions import UserError

PARAM_PREFIX = "cd_cash_position.account_code."

# role -> human label (used in the refusal message and the settings notes)
ACCOUNT_ROLES = {
    "branch_cash": "Branch cash on hand (drawer cash awaiting deposit)",
    "cash_in_transit": "Cash-in-transit (deposits between branch and bank)",
    "cod_clearing": "Rider COD receivable / clearing",
    "rider_shortage": "Rider shortage recoverable",
    "gateway_fees": "Gateway / MFS merchant fees (MDR)",
    "gateway_fee_vat": "VAT on gateway fees (optional; else included in fees)",
    "cash_shortage": "Cash shortage / over (under investigation)",
    "channel_clearing": "MFS / card channel clearing (AR receipts land here)",
    "outgoing_clearing": "Outgoing payments clearing (default debit of a payment)",
    "interest_expense": "Interest expense on bank facilities",
    "bank_charges": "Bank charges expense",
}


def param(env, key, default=None):
    return env["ir.config_parameter"].sudo().get_param(key) or default


def treasury_account(env, company, role, required=True):
    """The company's GL account for a treasury role, or a UserError naming
    the parameter to configure (fail closed). `required=False` returns an
    empty recordset instead (reports use it to say what is not configured)."""
    code = param(env, PARAM_PREFIX + role)
    if not code and role == "channel_clearing":
        # the same account M20 receipts debit for bKash/Nagad/card
        code = param(env, "cd_billing_engine.account_code.channel_mfs")
    account = env["account.account"]
    if code:
        account = (
            env["account.account"]
            .sudo()
            .with_company(company)
            .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        )
    if not account and required:
        raise UserError(
            "Treasury posting refused: no GL account for '%s' in %s. Set the system parameter "
            "%s%s to the account code — nothing is posted to a guessed account."
            % (ACCOUNT_ROLES.get(role, role), company.name, PARAM_PREFIX, role)
        )
    return account


def bank_account_of(journal):
    """The GL account behind a bank/cash journal (fail closed)."""
    if not journal:
        raise UserError("Select the bank account (bank journal) first.")
    if journal.type not in ("bank", "cash"):
        raise UserError("%s is not a bank or cash journal." % journal.display_name)
    if not journal.default_account_id:
        raise UserError("Bank journal %s has no GL account configured." % journal.display_name)
    return journal.default_account_id


def posting_dims(env, branch=None):
    """Dimensions for treasury postings: the branch plus the configured
    default cost centre / business line (same defaults as M20)."""
    return {
        "branch_id": branch.id if branch else False,
        "cost_centre": param(env, "cd_cash_position.default_cost_centre")
        or param(env, "cd_billing_engine.default_cost_centre")
        or "CORP",
        "business_line": param(env, "cd_cash_position.default_business_line")
        or param(env, "cd_billing_engine.default_business_line")
        or "RETAIL",
    }


def post_treasury_move(env, company, entry_date, ref, lines, branch=None, source="treasury"):
    """Post a balanced treasury entry on the company's general journal.

    lines: [(account, label, debit, credit, partner|None)] — zero lines are
    dropped; the caller balances. Returns the posted account.move."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    journal = env["account.journal"].search(
        [("type", "=", "general"), ("company_id", "=", company.id)], limit=1
    )
    if not journal:
        raise UserError("Treasury posting refused: %s has no general journal." % company.name)
    kept = [ln for ln in lines if round(ln[2], 2) or round(ln[3], 2)]
    debit = round(sum(ln[2] for ln in kept), 2)
    credit = round(sum(ln[3] for ln in kept), 2)
    if not kept or abs(debit - credit) > 0.005:
        raise UserError("Treasury posting refused: unbalanced entry (%s / %s)." % (debit, credit))
    move_vals = {
        "journal_id": journal.id,
        "company_id": company.id,
        "date": entry_date,
        "ref": ref,
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
            for account, label, dr, cr, partner in kept
        ],
    }
    dims = posting_dims(env, branch)
    move, _dims = post_with_dimensions(
        env, move_vals, {i: dict(dims) for i in range(len(kept))}, source=source
    )
    return move


def gl_balance(env, accounts, company=None, date_to=None, date_from=None):
    """Posted balance (debit - credit) of the given accounts."""
    if not accounts:
        return 0.0
    domain = [("account_id", "in", accounts.ids), ("parent_state", "=", "posted")]
    if company:
        domain.append(("company_id", "=", company.id))
    if date_to:
        domain.append(("date", "<=", date_to))
    if date_from:
        domain.append(("date", ">=", date_from))
    groups = env["account.move.line"]._read_group(domain, [], ["balance:sum"])
    return round(groups[0][0] or 0.0, 2) if groups else 0.0


_TOKEN_SPLIT = re.compile(r"[\s,;:|#()\[\]]+")


def has_token(text, token):
    """Whole-token reference match: 'AR/5' is in 'paid AR/5 ok' but NOT in
    'AR/55' (the old substring match accepted both)."""
    if not token or not text:
        return False
    token = token.strip().upper()
    return token in {t.strip(".").upper() for t in _TOKEN_SPLIT.split(text) if t}
