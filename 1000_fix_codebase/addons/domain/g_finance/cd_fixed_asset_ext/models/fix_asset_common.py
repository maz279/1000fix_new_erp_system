# fix_asset_common — M49 helpers shared by the asset, capex, lifecycle and
# lease models: month arithmetic, the accounting-group / SoD gates and the
# single fail-closed journal-entry writer every M49 posting goes through.
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

MANAGER_GROUP = "account.group_account_manager"
USER_GROUP = "account.group_account_user"


def money(value) -> float:
    """Half-up to 2 dp (BDT), via Decimal so 0.005 never rounds to even."""
    return float(Decimal(str(value or 0.0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def month_start(day: date) -> date:
    return day.replace(day=1)


def month_end(day: date) -> date:
    return day + relativedelta(day=31)


def add_months(day: date, months: int) -> date:
    return day + relativedelta(months=months)


def require_group(env, group: str, what: str) -> None:
    """Workflow steps reachable over the generic workspace action endpoint
    re-check the accounting group in code (ACL write alone is not enough)."""
    if env.su:
        return
    # In Odoo 19 the accounting Administrator does not imply "Show Full
    # Accounting Features", so the manager also passes the accountant gate.
    allowed = (group, MANAGER_GROUP) if group == USER_GROUP else (group,)
    if not any(env.user.has_group(g) for g in allowed):
        label = "accounting manager" if group == MANAGER_GROUP else "accountant"
        raise UserError(env._("%s needs the %s role.", what, label))


def check_sod(env, requester, what: str) -> None:
    """Segregation of duties: the person who raised a document never approves
    it — enforced for every user, superuser included."""
    if requester and requester == env.user:
        raise UserError(
            env._(
                "%s: segregation of duties — the requester cannot approve their own request.",
                what,
            )
        )


def require_accounts(record, fnames, what: str) -> None:
    """Fail closed when a posting account/journal is not configured."""
    missing = [record._fields[f].string for f in fnames if not record[f]]
    if missing:
        raise UserError(
            record.env._(
                "%s cannot be posted: configure %s on %s first.",
                what,
                ", ".join(missing),
                record.display_name,
            )
        )


def post_entry(env, company, journal, entry_date, ref, lines):
    """Create and post ONE balanced account.move.

    lines: [(account, debit, credit, label)]; zero lines are dropped. Raises
    UserError (nothing created — callers run inside the request savepoint)
    when the entry would not balance or has nothing to post."""
    vals = []
    total_d = total_c = 0.0
    for account, debit, credit, label in lines:
        debit, credit = money(debit), money(credit)
        if not debit and not credit:
            continue
        if debit < 0:  # a negative debit is a credit (and vice versa)
            debit, credit = 0.0, credit - debit
        if credit < 0:
            debit, credit = debit - credit, 0.0
        total_d += debit
        total_c += credit
        vals.append(
            (0, 0, {"account_id": account.id, "debit": debit, "credit": credit, "name": label})
        )
    if not vals:
        raise UserError(env._("Nothing to post for %s.", ref))
    if abs(money(total_d) - money(total_c)) > 0.001:
        raise UserError(env._("%s does not balance — nothing was posted.", ref))
    move = (
        env["account.move"]
        .with_company(company)
        .create(
            {
                "move_type": "entry",
                "company_id": company.id,
                "journal_id": journal.id,
                "date": entry_date,
                "ref": ref,
                "line_ids": vals,
            }
        )
    )
    move.action_post()
    return move
