# rental_gl — M13 money-path helpers: which GL account a rental movement hits,
# which dimensions ride it, and the posting itself.
#
# A rental deposit is the CUSTOMER'S money until a charge is proven, so it is a
# liability, never revenue: received -> Dr cash/bank/MFS clearing, Cr deposits
# held; applied to a proven charge -> Dr deposits held, Cr recovery income.
# Refunds do not post here: treasury (M50) debits the liability when the bank
# confirms the money left (fix.payment.execution.debit_account_id).
#
# Estate rules, copied from settlement (M53) and AR (M20), not invented:
#   * the account of a role is configured (system parameter), never guessed -
#     a missing account REFUSES the posting and names the parameter to set;
#   * every posting goes through M19's post_with_dimensions, so the COA rules
#     (postable leaf, required dimensions) hold for rentals exactly as they do
#     for invoices;
#   * cash/bank/MFS tender accounts are M20's, so a deposit lands where an
#     invoice receipt of the same tender lands.
from odoo import fields
from odoo.addons.cd_billing_engine.models.fix_ar_engine import _ar_account, _ar_journal
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.exceptions import UserError

# role -> (default account code, label). Override per deployment with system
# parameter cd_rental_asset.account_code.<role>.
RENTAL_ACCOUNTS = {
    # MD-035 2-40-20-010 "Customer advance deposits" is linked to Odoo 212000.
    "deposit_liability": ("212000", "Customer security deposits held (liability)"),
    # MD-035 4-90-10-010 "Other income" is linked to Odoo 450000.
    "retention_income": ("450000", "Rental damage, late-fee and forfeiture recovery income"),
}

# deposit tender -> the M20 account role that tender clears into
TENDER_ROLE = {
    "cash": "cash",
    "bank": "bank",
    "bkash": "channel_mfs",
    "nagad": "channel_mfs",
    "card": "channel_mfs",
}

# deposit tender -> M50 payment-execution method
PAYMENT_METHOD = {
    "cash": "cash",
    "bank": "bank_transfer",
    "bkash": "mobile_fs",
    "nagad": "mobile_fs",
    "card": "bank_transfer",
}

# the business-line dimension of every rental posting: BL-07 "Equipment rental"
# in the 14-stream business-line master
RENTAL_BUSINESS_LINE = "BL-07"


def rental_account(env, company, role):
    """The company's GL account for a rental role. Refuses, never guesses."""
    default_code, label = RENTAL_ACCOUNTS[role]
    code = (
        env["ir.config_parameter"].sudo().get_param(f"cd_rental_asset.account_code.{role}")
        or default_code
    )
    account = (
        env["account.account"]
        .with_company(company)
        .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    )
    if not account:
        raise UserError(
            "Rental posting refused: no GL account %s (%s) exists in company %s. Configure it "
            "in the chart of accounts, or set system parameter "
            "cd_rental_asset.account_code.%s to the account code to use."
            % (code, label, company.name, role)
        )
    return account


def tender_account(env, company, method):
    """The cash / bank / MFS clearing account a deposit tender settles into."""
    role = TENDER_ROLE.get(method)
    if not role:
        raise UserError("Rental posting refused: unknown deposit tender %r" % method)
    account = _ar_account(env, company, role)
    if not account:
        raise UserError(
            "Rental posting refused: no GL account is configured for the %s tender in company "
            "%s. Set system parameter cd_billing_engine.account_code.%s."
            % (method, company.name, role)
        )
    return account


def posting_dims(env, reservation):
    """Dimensions of a rental posting: the booking branch, the configured
    cost centre, the rental business line and the reservation's operating
    unit. The OU falls back to the BRANCH's unit (a branch belongs to one
    unit — its master data), else the company's first unit; a branch from
    another unit would fail the journal dimension's branch↔OU consistency,
    so the branch wins over the company default. Never invented beyond
    these two derivations."""
    dims = env["fix.ar.invoice"]._ar_posting_dims(reservation.branch_id.id)
    param = env["ir.config_parameter"].sudo().get_param
    dims["business_line"] = param("cd_rental_asset.business_line") or RENTAL_BUSINESS_LINE
    ou = (
        reservation.operating_unit_id
        or (reservation.branch_id and reservation.branch_id.operating_unit_id)
        or env["operating.unit"].search([("company_id", "=", reservation.company_id.id)], limit=1)
    )
    dims["operating_unit_id"] = ou.id if ou else False
    return dims


def post_rental_move(env, reservation, date, ref, lines):
    """Post a balanced rental entry through M19. `lines` is
    [(account, label, debit, credit, partner|None)]. Returns the move."""
    company = reservation.company_id
    journal = _ar_journal(env, company)
    if not journal:
        raise UserError(
            "Rental posting refused: company %s has no general (miscellaneous) journal."
            % company.name
        )
    if round(sum(line[2] for line in lines) - sum(line[3] for line in lines), 2) != 0:
        raise UserError("Rental posting %s is not balanced" % ref)
    dims = posting_dims(env, reservation)
    move, _dims = post_with_dimensions(
        env,
        {
            "journal_id": journal.id,
            "company_id": company.id,
            "date": date or fields.Date.context_today(reservation),
            "ref": ref,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "name": label,
                        "account_id": account.id,
                        "partner_id": partner.id if partner else False,
                        "debit": debit,
                        "credit": credit,
                    },
                )
                for account, label, debit, credit, partner in lines
            ],
        },
        {idx: dims for idx in range(len(lines))},
        source="api",
    )
    return move
