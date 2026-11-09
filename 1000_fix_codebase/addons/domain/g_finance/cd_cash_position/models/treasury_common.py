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
    # A04 hand-off closure (2026-11-05): the tender-bond encashment leg — the
    # procuring entity encashed a bank guarantee, a realised loss.
    "bond_encashment_loss": "Bank guarantee encashment loss (tender bonds, PPR r.25)",
    "cheque_returned": "Returned (bounced) customer cheques receivable",
    # R1 (CIH capability report, 2026-11-09): a received cheque is money IN
    # HAND, not money in the bank — it is staged here from receipt until the
    # bank statement clears it (the D365 bridging-account / SAP special G/L
    # equivalent; the company's legacy chart calls it 16556556).
    "cheque_in_hand": "Cheques in hand (received, held until the bank clears them)",
}

GROUP_ACCOUNTANT = "account.group_account_user"
GROUP_ADMIN = "account.group_account_manager"


def param(env, key, default=None):
    return env["ir.config_parameter"].sudo().get_param(key) or default


def float_param(env, key, default):
    """A numeric system parameter; an unset or unreadable value gives the
    documented default (never a silent zero)."""
    raw = env["ir.config_parameter"].sudo().get_param(key)
    if raw in (None, False, ""):
        return float(default)
    try:
        return float(raw)
    except (TypeError, ValueError):
        return float(default)


def bool_param(env, key, default=True):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    if raw in (None, False, ""):
        return default
    return str(raw).strip().lower() not in ("0", "false", "no", "off")


def has_role(env, xmlid) -> bool:
    """Superuser code (crons, seeds, service calls) is trusted; a person must
    hold the group."""
    if env.su or env.user.has_group(xmlid):
        return True
    # an Accounting Administrator can do what an accountant does
    return xmlid == GROUP_ACCOUNTANT and env.user.has_group(GROUP_ADMIN)


ROLE_LABELS = {GROUP_ACCOUNTANT: "Accountant", GROUP_ADMIN: "Accounting Administrator"}


def require_role(env, xmlid, what):
    if not has_role(env, xmlid):
        group = env.ref(xmlid, raise_if_not_found=False)
        label = ROLE_LABELS.get(xmlid) or (group.name if group else xmlid)
        raise UserError("%s needs the %s role, which you do not hold." % (what, label))


def treasury_alert(record, summary, note, deadline=None):
    """Raise a treasury incident on `record`: a chatter note plus a to-do
    activity for each Accounting Administrator of its company (the M50
    escalation roles have no dedicated groups yet). No duplicate activity
    while one with the same summary is still open."""
    env = record.env
    company = record.company_id if "company_id" in record._fields else env.company
    record.sudo().message_post(body="%s: %s" % (summary, note))
    open_same = record.sudo().activity_ids.filtered(lambda a: a.summary == summary)
    if open_same:
        return open_same
    group = env.ref(GROUP_ADMIN, raise_if_not_found=False)
    users = (
        group.sudo().all_user_ids.filtered(
            lambda u: u.active and not u.share and company in u.company_ids
        )
        if group
        else env["res.users"]
    )
    activities = env["mail.activity"]
    for user in users:
        activities |= record.sudo().activity_schedule(
            "mail.mail_activity_data_todo",
            date_deadline=deadline,
            summary=summary,
            note=note,
            user_id=user.id,
        )
    return activities


def require_other_person(env, users, what):
    """Maker-checker: the acting user must not be any of `users` (the maker,
    submitter, preparer...). Superuser service code acts for nobody."""
    if env.su:
        return
    users = users.filtered(lambda u: u)
    if env.user in users:
        raise UserError(
            "Segregation of duties: %s must be done by someone other than %s."
            % (what, ", ".join(users.mapped("name")))
        )


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
