# fix_payroll_disbursement — M56: the shared release, BEFTN and GL steps of
# every payroll payment (A09 workflow audit M56-4, M56-7, M56-9).
#
# The audit found an approving manager releasing his own approval (SoD-29),
# and off-cycle, bonus and WPPF documents whose 'paid' / 'posted' state
# produced no bank file and no journal entry. A payment now goes:
#   approved (routed, pinned) -> released by a Payroll Disbursement Releaser
#   who neither prepared nor approved it -> BEFTN file from the pinned payee
#   -> GL entry on the company's configured payroll accounts.
from odoo import Command, fields, models
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.exceptions import AccessError, UserError

RELEASER = "cd_payroll_bd.group_payroll_release"

PAYMENT_GL_ACCOUNTS = [
    ("payroll_salary_expense_account_id", "Salary & Wage Expense"),
    ("payroll_net_payable_account_id", "Net Salary Payable"),
]


def master_bank_details(employee):
    """(account, routing, bank name, problem) from the employee master, read as
    payroll. The account is the registered salary account record (Odoo 19
    primary_bank_account_id) or, when there is none, the master's own
    bank_account_number field; when the two disagree no account is taken and
    the problem is named (the run then fails pre-validation): a salary is
    never sent to one of two conflicting accounts."""
    master = employee.sudo()
    primary = master.primary_bank_account_id
    record_acc = (primary.acc_number or "").strip()
    field_acc = (
        (master.bank_account_number or "").strip()
        if "bank_account_number" in master._fields
        else ""
    )
    routing = (master.routing_number or "").strip() or False
    bank_name = (
        primary.bank_id.name
        or (master.bank_name if "bank_name" in master._fields else False)
        or False
    )
    if record_acc and field_acc and record_acc != field_acc:
        return (
            False,
            routing,
            bank_name,
            (
                "%s has two different registered accounts (%s on the bank account record, %s on "
                "the employee master)" % (master.name, record_acc, field_acc)
            ),
        )
    return (record_acc or field_acc or False), routing, bank_name, ""


def master_payment_channel(employee):
    """('bank' | 'mfs', provider, wallet) for the employee's salary.

    The master has no explicit salary-channel field (cd_hr_core holds a bank
    account and, separately, an MFS wallet "for daily allowances & field
    expenses"). The rule taken here (A09 round 2 decision, M56): an employee
    with ANY registered bank account is paid by bank, as today; an employee
    with no bank account and a registered MFS wallet is paid to the wallet."""
    master = employee.sudo()
    has_bank = bool(
        (master.primary_bank_account_id.acc_number or "").strip()
        or (
            (master.bank_account_number or "").strip()
            if "bank_account_number" in master._fields
            else ""
        )
    )
    wallet = (
        (master.mfs_account_number or "").strip() if "mfs_account_number" in master._fields else ""
    )
    provider = master.mfs_provider if "mfs_provider" in master._fields else False
    if not has_bank and wallet:
        return "mfs", provider or False, wallet
    return "bank", False, False


def check_releaser(records, what, conflicted):
    """SoD-29 / BRU-PAY-03: the releaser holds the release role and is none of
    the users `conflicted(rec)` returns (preparer, calculator, approver)."""
    env = records.env
    if env.su:
        return
    user = env.user
    if not user.has_group(RELEASER):
        raise AccessError(
            "Only a Payroll Disbursement Releaser (Finance) can release %s to the bank." % what
        )
    for rec in records:
        if user in conflicted(rec):
            raise UserError(
                "Release SoD violation (SOD-29): %s prepared, calculated or approved %s %s and "
                "cannot also release it." % (user.name, rec._description, rec.display_name)
            )


def payroll_gl_journal(company, accounts, what):
    """The company's payroll journal once every account `accounts` names is
    configured and belongs to the company; refused otherwise."""
    journal = company.payroll_journal_id
    missing = [label for fname, label in accounts if not company[fname]]
    if not journal:
        missing.insert(0, "Payroll Journal")
    if missing:
        raise UserError(
            "Configure the payroll accounting of %s before posting %s: %s."
            % (company.name, what, ", ".join(missing))
        )
    foreign = [label for fname, label in accounts if company not in company[fname].company_ids]
    if journal.company_id != company:
        foreign.insert(0, "Payroll Journal")
    if foreign:
        raise UserError(
            "These payroll accounts of %s do not belong to the company: %s."
            % (company.name, ", ".join(foreign))
        )
    return journal


class FixJournalPostingLogPayroll(models.Model):
    """Payroll as a posting source in M19's posting log: an automated sub-ledger, so
    a salary line with no branch, or a bonus entry that names none, takes the company
    default the statutory chart requires instead of being refused (MD-035, A08)."""

    _inherit = "fix.journal.posting.log"

    source = fields.Selection(
        selection_add=[("payroll_subledger", "Payroll Sub-ledger (M56)")],
        ondelete={"payroll_subledger": lambda recs: recs.write({"source": "api"})},
    )


def post_two_line_entry(env, company, ref, date, amount, label, debit_field, credit_field, ou=None):
    """Dr debit_field / Cr credit_field for `amount`, posted with the OU dimension."""
    currency = company.currency_id
    amount = currency.round(amount)
    if currency.compare_amounts(amount, 0.0) <= 0:
        raise UserError("%s has nothing to post to the GL." % ref)
    lines = [
        {"account_id": company[debit_field].id, "name": label, "debit": amount, "credit": 0.0},
        {"account_id": company[credit_field].id, "name": label, "debit": 0.0, "credit": amount},
    ]
    move, _dims = post_with_dimensions(
        env,
        {
            "move_type": "entry",
            "ref": ref,
            "journal_id": company.payroll_journal_id.id,
            "date": date,
            "line_ids": [Command.create(line) for line in lines],
        },
        {idx: {"operating_unit_id": ou.id if ou else False} for idx in range(len(lines))},
        source="payroll_subledger",
    )
    return move
