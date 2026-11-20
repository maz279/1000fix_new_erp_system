# fix_import_common — M44 shared rules: roles, configuration and the GL seam.
#
# A06 workflow audit (2026-11-03), findings M44-1..15. Everything a business
# must decide (tolerances, the LC authority ladder, the landing charge, the
# GL accounts) is read from ir.config_parameter here, with a conservative
# default or none at all. A posting whose account is not configured is
# REFUSED: nothing lands on a guessed account.
from odoo import fields
from odoo.exceptions import UserError

OFFICER = "cd_import_order.group_fix_import_officer"
APPROVER = "cd_import_order.group_fix_import_approver"
FINANCE = "account.group_account_user"

# The formula version stored on every Bill of Entry line (FR-ITC-033).
FORMULA_VERSION = "FR-ITC-033/v1"

# ---- configuration keys (documented in runbook.md) ------------------------
P = "cd_import_order."
PARAM_LANDING_CHARGE = P + "landing_charge_pct"  # default 1.0 (spec FR-ITC-033)
PARAM_LC_TOLERANCE = P + "lc_value_tolerance_pct"  # default 0
PARAM_PROFORMA_TOLERANCE = P + "proforma_tolerance_pct"  # default 0
PARAM_LC_REQUIRES_LCA = P + "lc_requires_lca"  # default "1"
PARAM_LC_LADDER = P + "lc_dofa_ladder"  # default "inf:tier_4"
PARAM_BOE_DOCS = P + "boe_required_documents"  # default "bl,invoice,packing"
# D6 / M44-03: customs rounds each levy; a difference up to BDT 10 per Bill of
# Entry is rounding and needs no variance acceptance
PARAM_DUTY_VARIANCE = P + "duty_variance_tolerance"  # BDT, default 10
DEFAULT_DUTY_VARIANCE = 10.0
PARAM_JOURNAL = P + "journal_code"  # general journal; default: company's first
PARAM_PAYMENT_JOURNAL = P + "payment_journal_code"  # bank/cash journal; REQUIRED
PARAM_LC_REQUIRES_FACILITY = P + "lc_requires_facility"  # default "1" (BRU-ITC-06)
PARAM_ADVANCE_CAP = P + "advance_cap_pct"  # default 0: every advance needs a stated reason
PARAM_IRC_WARNING_DAYS = P + "irc_expiry_warning_days"  # default 30 (BRU-ITC-03)
# 120 days stands in for Bangladesh Bank's 4-month Bill of Entry guideline;
# Finance confirms the figure.
PARAM_BOE_REMITTANCE_DAYS = P + "boe_remittance_match_days"  # default 120

# role -> label. Each role's account code is the system parameter
# cd_import_order.account_code.<role>.
ACCOUNT_ROLES = {
    "inventory": "Inventory (stock valuation)",
    "duty_clearing": "Customs duty clearing (CD/RD/SD paid, awaiting landed cost)",
    "landed_accrual": "Landed-cost accrual (freight, insurance, clearing, estimates)",
    "vat_input": "Import VAT input tax (recoverable)",
    "at_input": "Advance Tax (AT) recoverable",
    "ait_advance": "Advance Income Tax (AIT) paid at import",
    "variance": "Landed-cost variance / cost-of-sales adjustment",
    "grni": "Goods received not invoiced (import goods value awaiting the supplier bill)",
    "lc_clearing": "LC payments clearing (retired: D6 settles the supplier in AP)",
    "fx_difference": "Exchange difference on LC settlement (settlement rate vs commitment rate)",
    "lc_margin": "LC margin held by the bank (M44-12)",
}
# Owner decision D6 (20 Nov 2026), legacy chart codes. Used when the role's
# parameter is unset; a configured code wins. The account must still exist in
# the company's chart, else the posting is refused.
#  - variance: duty and landed-cost variance 600007 Purchase Price Variance
#    (M44-01 / X10: the old 610000 is not in the chart)
#  - duty_clearing: customs duty paid is an asset awaiting capitalisation,
#    100302 Deposits - Customs (owner item 6), not the 200306 liability
#  - fx_difference: 500030 Foreign Exchange Gain/Loss
#  - lc_margin: 100812 L/C Margin
DEFAULT_ACCOUNT_CODES = {
    "variance": "600007",
    "duty_clearing": "100302",
    "fx_difference": "500030",
    "lc_margin": "100812",
}
# configured values D6 replaces (a data repair the owner decided)
SUPERSEDED_ACCOUNT_CODES = {"variance": ("610000",), "duty_clearing": ("200306",)}


def param(env, key, default=None):
    return env["ir.config_parameter"].sudo().get_param(key, default)


def param_float(env, key, default=0.0):
    raw = param(env, key)
    if raw in (None, False, ""):
        return default
    try:
        return float(raw)
    except (TypeError, ValueError) as exc:
        raise UserError("System parameter %s must be a number (it is %r)." % (key, raw)) from exc


def param_bool(env, key, default=True):
    raw = param(env, key)
    if raw in (None, False, ""):
        return default
    return str(raw).strip().lower() not in ("0", "false", "no", "off")


def today(record):
    return fields.Date.context_today(record)


# ---- roles and segregation of duties --------------------------------------
def require_group(env, xmlid, what):
    """Refuse unless the acting user holds the role (superuser code is trusted)."""
    if env.su:
        return
    if not env.user.has_group(xmlid):
        group = env.ref(xmlid, raise_if_not_found=False)
        raise UserError("%s requires the %s role." % (what, group.name if group else xmlid))


def require_other_person(env, record, what, *parties):
    """Two-person rule: the decider is not the record's creator, nor any of
    `parties` (users who proposed or changed what is being approved). Set
    from env.user inside the action, never from a parameter."""
    if env.su:
        return
    involved = record.create_uid
    for party in parties:
        involved |= party
    if env.user in involved:
        raise UserError(
            "Segregation of duties: %s must be decided by someone other than the person "
            "who recorded or changed it." % what
        )


def changes(records, vals):
    """True when `vals` would change a stored value of one of `records`
    (the P03 form echoes every field it shows)."""
    names = [n for n in vals if n in records._fields]
    return any(rec._fix_guard_differs(n, vals[n], rec[n]) for rec in records for n in names)


def refuse_locked(records, vals, locked, why):
    """Refuse a change to any of `locked` (a callable rec -> set of names)."""
    if not records or records._fix_guard_open():
        return
    for rec in records:
        names = [n for n in vals if n in locked(rec)]
        if names and changes(rec, {n: vals[n] for n in names}):
            labels = ", ".join(sorted(rec._fields[n].string or n for n in names))
            raise UserError("%s cannot be changed on %s: %s" % (labels, rec.display_name, why))


def alert_users(record, group_xmlid=None, *fallback):
    """Who an alert goes to: the role's active users, else the named people."""
    users = record.env["res.users"]
    if group_xmlid:
        users = record.env.ref(group_xmlid).sudo().all_user_ids.filtered("active")
    if not users:
        for person in fallback:
            users |= person
    return users.filtered("active")


def schedule_alert(record, summary, note, users):
    """A to-do on a record carrying mail.activity.mixin, one per person. The
    caller stamps its own 'alerted on' field, so a daily job asks once."""
    su = record.sudo()
    for user in users:
        su.activity_schedule(
            "mail.mail_activity_data_todo", summary=summary, note=note, user_id=user.id
        )


# ---- GL seam ---------------------------------------------------------------
def stock_valuation_code(env):
    """The account M15 books every stock-valuation movement against.

    Until the M19 GL cutover, M15 records each receipt (with its landed-cost
    estimate) and each landed-cost revaluation in its valuation suspense
    ledger against this account, and the cutover journal later moves the whole
    pending total to Inventory. The import journal's stock line therefore
    posts to the same account: debiting Inventory here as well would bring the
    same value into the GL twice, once now and once at the cutover."""
    return (
        env["fix.inventory.valuation.suspense"]
        .default_get(["suspense_account_code"])
        .get("suspense_account_code")
    )


def import_account(env, company, role):
    """The company's GL account for an import role, refused when unconfigured.

    The stock line ("inventory") is not configurable: it is M15's valuation
    suspense account (see stock_valuation_code)."""
    key = P + "account_code." + role
    code = (
        stock_valuation_code(env)
        if role == "inventory"
        else (param(env, key) or DEFAULT_ACCOUNT_CODES.get(role))
    )
    account = env["account.account"]
    if code:
        account = (
            env["account.account"]
            .sudo()
            .with_company(company)
            .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        )
    if not account:
        raise UserError(
            "No GL account for %s in %s: set system parameter %s to an account code of "
            "this company's chart. Nothing was posted." % (ACCOUNT_ROLES[role], company.name, key)
        )
    return account


def import_journal(env, company, kind="general"):
    """kind 'general': the journal in cd_import_order.journal_code, else the
    company's first general journal. kind 'payment': the bank/cash journal in
    cd_import_order.payment_journal_code (REQUIRED: duty paid to customs never
    leaves a guessed bank)."""
    Journal = env["account.journal"].sudo()
    if kind == "payment":
        code = param(env, PARAM_PAYMENT_JOURNAL)
        journal = Journal.browse()
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
                "No duty payment bank journal configured in %s: set system parameter %s "
                "to the code of the bank journal customs duty is paid from. Nothing was "
                "posted." % (company.name, PARAM_PAYMENT_JOURNAL)
            )
        return journal
    code = param(env, PARAM_JOURNAL)
    domain = [("company_id", "=", company.id), ("type", "=", "general")]
    journal = Journal.search(domain + ([("code", "=", code)] if code else []), limit=1)
    if not journal:
        raise UserError(
            "No general journal in %s for import postings (system parameter %s). "
            "Nothing was posted." % (company.name, PARAM_JOURNAL)
        )
    return journal


def default_params(env):
    """D6 defaults, applied at install/upgrade: an unset import account role
    takes its D6 code, a value D6 superseded (variance 610000, duty clearing
    200306) is replaced, and the BoE rounding tolerance becomes BDT 10 when
    nobody set one. Returns the keys changed."""
    icp = env["ir.config_parameter"].sudo()
    changed = []
    for role, code in DEFAULT_ACCOUNT_CODES.items():
        key = P + "account_code." + role
        current = icp.get_param(key)
        if not current or current in SUPERSEDED_ACCOUNT_CODES.get(role, ()):
            icp.set_param(key, code)
            changed.append(key)
    if icp.get_param(PARAM_DUTY_VARIANCE) in (None, False, "", "0", "0.0"):
        icp.set_param(PARAM_DUTY_VARIANCE, str(DEFAULT_DUTY_VARIANCE))
        changed.append(PARAM_DUTY_VARIANCE)
    return changed


def post_import_move(
    env, company, journal, entry_date, ref, lines, operating_unit=None, partner=None
):
    """Post ONE balanced entry through M19's engine (post_with_dimensions).

    lines: [(account, label, amount)] where a positive amount is a debit and a
    negative one a credit; zero lines are dropped. Posted as superuser: the
    action that calls this has already checked the user's role, and the
    import roles do not carry accounting rights."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    su = env(su=True)
    move_lines = []
    total_d = total_c = 0.0
    for account, label, amount in lines:
        amount = round(amount or 0.0, 2)
        if not amount:
            continue
        debit, credit = (amount, 0.0) if amount > 0 else (0.0, -amount)
        total_d += debit
        total_c += credit
        move_lines.append(
            (
                0,
                0,
                {
                    "account_id": account.id,
                    "name": label,
                    "debit": debit,
                    "credit": credit,
                    "partner_id": partner.id if partner else False,
                },
            )
        )
    if not move_lines:
        return su["account.move"]
    if abs(round(total_d, 2) - round(total_c, 2)) > 0.005:
        raise UserError(
            "%s does not balance (%.2f / %.2f): nothing was posted." % (ref, total_d, total_c)
        )
    # X13: an import entry carries the import's own operating unit; it is never
    # attributed to the company's first OU
    ou = operating_unit
    if not ou:
        raise UserError(
            "%s: the import order has no operating unit, so the entry cannot carry the "
            "branch dimension. Set the order's operating unit. Nothing was posted." % ref
        )
    dims = {i: {"operating_unit_id": ou.id} for i in range(len(move_lines))}
    move, _dims = post_with_dimensions(
        su(context=dict(su.context, allowed_company_ids=[company.id])),
        {
            "move_type": "entry",
            "company_id": company.id,
            "journal_id": journal.id,
            "date": entry_date,
            "ref": ref,
            "line_ids": move_lines,
        },
        dims,
        source="import_subledger",
    )
    return move
