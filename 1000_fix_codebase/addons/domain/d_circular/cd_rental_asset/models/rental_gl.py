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
from odoo import fields, models
from odoo.addons.cd_billing_engine.models.fix_ar_engine import _ar_account, _ar_journal
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.exceptions import UserError

# role -> label. The account of each role is a system parameter
# cd_rental_asset.account_code.<role> set by the deployment (owner decision D1,
# A05 FIN-01/M13-05/M13-08): there is NO code default, because the chart the
# old defaults named (212000 / 450000) is not the company's chart and 212000 is
# M20's deferred revenue. An unset or unknown code REFUSES the posting and
# names the parameter to set.
#   deposit_liability  the NEW "Customer Security Deposit - Rental" liability
#   recovery_income    400111 Loss Adjustment Income: deposit deductions,
#                      forfeits, damage above the deposit, loss of a unit
#   rental_income      400108 Rental Service Income: the rental charge, the
#                      damage waiver fee, late and cancellation fees
RENTAL_ACCOUNTS = {
    "deposit_liability": "Customer security deposit - rental (liability)",
    "recovery_income": "Rental damage and loss recovery income",
    "rental_income": "Rental service income",
}
ACCOUNT_PARAM = "cd_rental_asset.account_code.%s"

# deposit tender -> the M20 account role that tender clears into
TENDER_ROLE = {
    "cash": "cash",
    "bank": "bank",
    "bkash": "channel_mfs",
    "nagad": "channel_mfs",
    "card": "channel_mfs",
}

# deposit tender -> M50 payment-execution method. A card deposit goes back to
# the card it came from (A05 FIN-25): M50's "card" method, which names the
# original card payment, never a bank transfer to an account the customer
# never gave.
PAYMENT_METHOD = {
    "cash": "cash",
    "bank": "bank_transfer",
    "bkash": "mobile_fs",
    "nagad": "mobile_fs",
    "card": "card",
}

# the business-line dimension of every rental posting: BL-07 "Equipment rental"
# in the 14-stream business-line master
RENTAL_BUSINESS_LINE = "BL-07"


def rental_account(env, company, role):
    """The company's GL account for a rental role. Refuses, never guesses."""
    label = RENTAL_ACCOUNTS[role]
    param = ACCOUNT_PARAM % role
    code = (env["ir.config_parameter"].sudo().get_param(param) or "").strip()
    if not code:
        raise UserError(
            "Rental posting refused: system parameter %s (%s) is not set. Finance names "
            "the account of this role (owner decision D1) before rentals post." % (param, label)
        )
    account = (
        env["account.account"]
        .sudo()
        .with_company(company)
        .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    )
    if not account:
        raise UserError(
            "Rental posting refused: system parameter %s names account %s (%s), which does "
            "not exist in company %s's chart." % (param, code, label, company.name)
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


class FixJournalPostingLogRental(models.Model):
    """Rentals as a posting source in M19's posting log: an automated sub-ledger,
    so a rental with no booking branch takes the company default (MD-035)."""

    _inherit = "fix.journal.posting.log"

    source = fields.Selection(
        selection_add=[("rental_subledger", "Rentals Sub-ledger (M13)")],
        ondelete={"rental_subledger": lambda recs: recs.write({"source": "api"})},
    )


def posting_operating_unit(reservation):
    """The operating unit of a rental posting: the booking BRANCH's unit
    (A05 FIN-09). A branch belongs to one unit (its master data); the
    reservation's own unit is derived from it and must agree. No company
    first-unit fallback: a rental with no branch, or a branch with no unit,
    is refused, never booked to an arbitrary unit."""
    branch = reservation.sudo().branch_id
    if not branch:
        raise UserError(
            "Rental %s has no booking branch: its postings carry the branch and the "
            "branch's operating unit. Set the branch before the money moves." % reservation.name
        )
    ou = branch.operating_unit_id
    if not ou:
        raise UserError(
            "Branch %s belongs to no operating unit: rental %s cannot be posted."
            % (branch.display_name, reservation.name)
        )
    own = reservation.sudo().operating_unit_id
    if own and own != ou:
        raise UserError(
            "Rental %s is booked at branch %s (unit %s) but carries unit %s: the unit "
            "comes from the branch." % (reservation.name, branch.display_name, ou.name, own.name)
        )
    return ou


def posting_dims(env, reservation):
    """Dimensions of a rental posting: the booking branch, the configured
    cost centre, the rental business line and the BRANCH's operating unit
    (posting_operating_unit). Never invented beyond these."""
    ou = posting_operating_unit(reservation)
    dims = env["fix.ar.invoice"]._ar_posting_dims(reservation.branch_id.id)
    param = env["ir.config_parameter"].sudo().get_param
    dims["business_line"] = param("cd_rental_asset.business_line") or RENTAL_BUSINESS_LINE
    dims["operating_unit_id"] = ou.id
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
        source="rental_subledger",
    )
    return move
