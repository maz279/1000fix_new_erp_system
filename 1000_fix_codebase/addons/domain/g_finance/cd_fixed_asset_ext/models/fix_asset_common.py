# fix_asset_common — M49 helpers shared by the asset, capex, lifecycle and
# lease models: month arithmetic, the accounting-group / SoD gates, the
# period gate, the authority ladders, and the single fail-closed journal-entry
# writer every M49 posting goes through (M19's post_with_dimensions).
import logging
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

MANAGER_GROUP = "account.group_account_manager"
USER_GROUP = "account.group_account_user"

# ---- the authority ladders (A08 M49-6, P1-1) -------------------------------
# The spec gives no capex BDT bands: capex is "approved within the authority
# matrix"; the CFO approves above a threshold and the CEO above the CFO band
# (M49 §13, R03 / R01). The defaults mirror the procurement ladder of the one
# DoA table (05-04 §7: <=50k / <=500k / <=2M CFO / above CEO). A disposal is
# authorised on what leaves the books (the larger of NBV and proceeds):
# <=25,000 a manager, above that the CFO (05-04 §7 write-off, mirrored by M45
# BRU-EAM-11); a write-off for loss / theft always needs the CFO (BRU-FXA-19).
# A revaluation or impairment is a CFO decision at any amount (M49 §8:
# "Impaired / Revalued": CFO). Every band is a config key; the M30 DOFA ladder
# (fix.dofa.ladder) overrides when ruled.
CAPEX_FLOOR = "cd_fixed_asset_ext.capex_dofa_no_approval_max"
CAPEX_TIER2 = "cd_fixed_asset_ext.capex_dofa_tier2_max"
CAPEX_TIER3 = "cd_fixed_asset_ext.capex_dofa_tier3_max"
CAPEX_TIER4 = "cd_fixed_asset_ext.capex_dofa_tier4_max"
DISPOSAL_FLOOR = "cd_fixed_asset_ext.disposal_dofa_no_approval_max"
DISPOSAL_TIER2 = "cd_fixed_asset_ext.disposal_dofa_tier2_max"
REVALUATION_FLOOR = "cd_fixed_asset_ext.revaluation_dofa_no_approval_max"
# BRU-FXA-03 (A08 M49-10): a period does not close while the register and its
# GL control accounts disagree by more than the tolerance. 0 switches it off.
CLOSE_GATE = "cd_fixed_asset_ext.close_gate_register_gl"
CLOSE_GATE_TOLERANCE = "cd_fixed_asset_ext.close_gate_tolerance"
# BRU-FXA-24 (capture audit 2026-11-17): a capital project whose budget is at
# or above the threshold has a post-implementation review due within the
# period after completion. Both are config keys (CFO policy).
PIR_THRESHOLD = "cd_fixed_asset_ext.capital_project_review_threshold"
PIR_DAYS = "cd_fixed_asset_ext.capital_project_review_days"
DEFAULTS = {
    CAPEX_FLOOR: 0.0,
    CAPEX_TIER2: 50000.0,
    CAPEX_TIER3: 500000.0,
    CAPEX_TIER4: 2000000.0,
    DISPOSAL_FLOOR: 0.0,
    DISPOSAL_TIER2: 25000.0,
    REVALUATION_FLOOR: 0.0,
    CLOSE_GATE: 1.0,
    CLOSE_GATE_TOLERANCE: 1.0,
    PIR_THRESHOLD: 5000000.0,
    PIR_DAYS: 180.0,
}


def money(value) -> float:
    """Half-up to 2 dp (BDT), via Decimal so 0.005 never rounds to even."""
    return float(Decimal(str(value or 0.0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def month_start(day: date) -> date:
    return day.replace(day=1)


def month_end(day: date) -> date:
    return day + relativedelta(day=31)


def add_months(day: date, months: int) -> date:
    return day + relativedelta(months=months)


def float_param(env, key):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    if raw in (None, False, ""):
        return float(DEFAULTS[key])
    try:
        return float(raw)
    except (TypeError, ValueError):
        _logger.warning("%s is not a number (%r); using %s", key, raw, DEFAULTS[key])
        return float(DEFAULTS[key])


def capex_ladder(env):
    return [
        (float_param(env, CAPEX_FLOOR), "tier_0"),
        (float_param(env, CAPEX_TIER2), "tier_2"),
        (float_param(env, CAPEX_TIER3), "tier_3"),
        (float_param(env, CAPEX_TIER4), "tier_4"),
        (float("inf"), "tier_5"),
    ]


def disposal_ladder(env, write_off=False):
    if write_off:
        return [(float_param(env, DISPOSAL_FLOOR), "tier_0"), (float("inf"), "tier_4")]
    return [
        (float_param(env, DISPOSAL_FLOOR), "tier_0"),
        (float_param(env, DISPOSAL_TIER2), "tier_2"),
        (float("inf"), "tier_4"),
    ]


def revaluation_ladder(env):
    return [(float_param(env, REVALUATION_FLOOR), "tier_0"), (float("inf"), "tier_4")]


def attach_upload(record, link_field, data, filename, fallback):
    """A file uploaded on a workspace form becomes an attachment of the record,
    linked on its evidence many2many: the many2many itself offers only a pick
    list of files already in the system, which is no way to attach one."""
    if not data:
        return False
    attachment = record.env["ir.attachment"].create(
        {
            "name": filename or fallback,
            "datas": data,
            "res_model": record._name,
            "res_id": record.id,
        }
    )
    record.write({link_field: [(4, attachment.id)]})
    return attachment


def attachment_names(attachments) -> str:
    return ", ".join(attachments.sudo().mapped("name"))


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


def check_sod(env, requester, what: str, record=None) -> None:
    """Segregation of duties: the person who raised a document never approves
    it — enforced for every user, superuser included. The record's creator is
    compared too (A08 M49-5: requested_by_id was rewritable)."""
    raisers = env["res.users"]
    if requester:
        raisers |= requester
    if record is not None and record.create_uid:
        raisers |= record.create_uid
    if env.user in raisers:
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


def assert_period_open(env, company, day, what="This posting"):
    """BRU-FXA-23 (A08 M49-7): no M49 entry into a closed period (the company
    lock dates, or an M19 period close marked closed) nor into a month not yet
    reached. Odoo used to re-date a locked entry silently while the register
    kept the old month."""
    today = fields.Date.context_today(env["res.users"])
    if day > month_end(today):
        raise UserError(env._("%s is dated %s, a period not yet reached: refused.", what, day))
    comp = company.sudo()
    locks = [
        comp[f] for f in ("fiscalyear_lock_date", "hard_lock_date") if f in comp._fields and comp[f]
    ]
    if locks and day <= max(locks):
        raise UserError(
            env._(
                "%s is dated %s, inside the closed period (lock date %s): refused.",
                what,
                day,
                max(locks),
            )
        )
    if "fix.period.close" in env:
        closed = (
            env["fix.period.close"]
            .sudo()
            .search_count(
                [
                    ("company_id", "=", company.id),
                    ("state", "=", "closed"),
                    ("period_end", ">=", month_start(day)),
                    ("period_end", "<=", month_end(day)),
                ]
            )
        )
        if closed:
            raise UserError(
                env._("%s falls in %s, a closed period: refused.", what, day.strftime("%Y-%m"))
            )


def post_entry(env, company, journal, entry_date, ref, lines, operating_unit=None):
    """Create and post ONE balanced account.move through M19's posting API
    (post_with_dimensions, source fixed_asset: chart rules, dimensions and the
    posting log — A08 M49-10), after the period gate.

    lines: [(account, debit, credit, label)]; zero lines are dropped. Raises
    UserError (nothing created — callers run inside the request savepoint)
    when the entry would not balance or has nothing to post."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    assert_period_open(env, company, entry_date, ref)
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
    ou = operating_unit or env["operating.unit"].sudo().search(
        [("company_id", "=", company.id)], limit=1
    )
    move_vals = {
        "move_type": "entry",
        "company_id": company.id,
        "journal_id": journal.id,
        "date": entry_date,
        "ref": ref,
        "line_ids": vals,
    }
    dims = {i: {"operating_unit_id": ou.id} for i in range(len(vals))} if ou else {}
    post_env = (
        env(context=dict(env.context, allowed_company_ids=company.ids))
        if env.su or company in env.user.company_ids
        else env
    )
    Move = post_env["account.move"]
    if hasattr(Move, "_fix_post_via_m19"):  # B3's documented M19 API
        move = Move._fix_post_via_m19(
            move_vals, "fixed_asset", source_ref=ref, dimension_by_line=dims
        )
    else:
        move, _dims = post_with_dimensions(post_env, move_vals, dims, source="fixed_asset")
    if move.date != entry_date:
        raise UserError(env._("%s would be re-dated %s by the ledger: refused.", ref, move.date))
    return move
