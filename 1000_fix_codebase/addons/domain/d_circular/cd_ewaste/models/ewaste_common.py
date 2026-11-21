# ewaste_common - shared M18 roles, switches and helpers (A05 audit, M18).
#
# The A05 workflow audit found that cd_ewaste had no role at all: every user
# could triage, dispatch, issue a disposal certificate, register a recycler
# and "accept" a DoE return. The roles below are the spec's §13 roles; the
# switches are the open business decisions of report §7, each with a safe
# default (an ir.config_parameter named cd_ewaste.<switch>).
import calendar
import re
from datetime import date

from odoo import fields
from odoo.exceptions import UserError

# --------------------------------------------------------------------- roles
G_ASSESSOR = "cd_ewaste.group_ewaste_triage_assessor"
G_HSE = "cd_ewaste.group_ewaste_hse_officer"
G_DISPATCH = "cd_ewaste.group_ewaste_dispatcher"
G_RECYCLER_APPROVER = "cd_ewaste.group_ewaste_recycler_approver"
G_COMPLIANCE = "cd_ewaste.group_ewaste_compliance_officer"
G_FINANCE = "cd_ewaste.group_ewaste_finance_approver"

# ------------------------------------------------------------------ switches
# Report §7.7 (ESG method): the avoided-emissions factor and the version
# stamped on every figure computed with it. Avoided CO2 is reported apart
# from the inventory (GHG Protocol: avoided emissions are not a reduction).
P_CO2_FACTOR = "cd_ewaste.co2_avoided_factor"
P_CO2_VERSION = "cd_ewaste.co2_avoided_factor_version"
DEFAULT_CO2_FACTOR = 1.5
DEFAULT_CO2_VERSION = "M18-PROVISIONAL-1.5"
# Report §7.6 (recycler panel): the certifications a recycler must hold to be
# dispatched to. Default: a DoE licence only.
P_PANEL = "cd_ewaste.recycler_required_certifications"
DEFAULT_PANEL = "doe"
# Batch weighbridge tolerance (spec T-05), percent.
P_TOLERANCE = "cd_ewaste.weight_tolerance_pct"
DEFAULT_TOLERANCE = 5.0
# Hazardous Waste (E-waste) Management Rules 2021: 180 days of storage, plus
# 90 when the DoE grants an extension.
P_STORAGE_DAYS = "cd_ewaste.storage_days"
P_STORAGE_EXT_DAYS = "cd_ewaste.storage_extension_days"
DEFAULT_STORAGE_DAYS = 180
DEFAULT_STORAGE_EXT_DAYS = 90
P_RETURN_REMINDER_DAYS = "cd_ewaste.return_reminder_days"
P_LICENCE_WARNING_DAYS = "cd_ewaste.licence_warning_days"
DEFAULT_REMINDER_DAYS = 30
# BRU-ESG-07: battery mass held at one storage location.
P_BATTERY_CEILING = "cd_ewaste.battery_location_ceiling_kg"
DEFAULT_BATTERY_CEILING = 500.0
# A DoE return is filed only under an active DoE registration (fail closed).
P_RETURN_NEEDS_REGISTRATION = "cd_ewaste.return_requires_registration"
# Per-item weight ceiling by material (M18-5 / F6c): a phone is not 1000 kg.
# Generous on purpose (packaging, rugged and feature phones): it bounds an
# absurd figure, it does not replace the weighbridge reconciliation (T-05).
P_MAX_ITEM_WEIGHT = "cd_ewaste.max_item_weight_kg.%s"
DEFAULT_MAX_ITEM_WEIGHT = {
    "phone": 2.5,
    "tablet": 3.0,
    "laptop": 8.0,
    "accessory": 10.0,
    "battery": 60.0,
    "other": 200.0,
}
# Media that always hold data, whatever the triage says (FR-ESG-009).
DATA_MATERIALS = ("phone", "laptop", "tablet")


def param(env, key, default):
    return env["ir.config_parameter"].sudo().get_param(key, default)


def param_float(env, key, default) -> float:
    try:
        return float(param(env, key, default))
    except (TypeError, ValueError):
        return float(default)


def param_int(env, key, default) -> int:
    try:
        return int(float(param(env, key, default)))
    except (TypeError, ValueError):
        return int(default)


def param_on(env, key, default="1") -> bool:
    return str(param(env, key, default)).strip().lower() not in ("0", "false", "no", "off", "")


def co2_factor(env, company=None):
    """(kg CO2e avoided per kg, the factor version stamped on the figure).

    FR-ESG-019 / T-08 (capture pass 2): the company's ACTIVE, approved factor
    set wins; the configured parameter is the fallback until one exists."""
    if "fix.esg.factor.set" in env:
        active = env["fix.esg.factor.set"]._fix_active_for(company or env.company)
        if active:
            return active.co2_avoided_per_kg, active.name
    return (
        param_float(env, P_CO2_FACTOR, DEFAULT_CO2_FACTOR),
        param(env, P_CO2_VERSION, DEFAULT_CO2_VERSION) or DEFAULT_CO2_VERSION,
    )


def panel(env) -> set:
    raw = param(env, P_PANEL, DEFAULT_PANEL) or DEFAULT_PANEL
    return {p.strip() for p in raw.split(",") if p.strip()}


def require_group(env, xmlid, label, doing):
    """Refuse unless the user holds the role. Superuser code is trusted."""
    if env.su or env.user.has_group(xmlid):
        return
    raise UserError("Only a %s may %s." % (label, doing))


def employee_of(env, user=None):
    user = user or env.user
    return env["hr.employee"].sudo().search([("user_id", "=", user.id)], limit=1)


def today(env):
    """The business day: Asia/Dhaka (UTC+6), whoever runs the code (A05
    M18-25). Odoo forces TZ=UTC and the cron user has no tz, so the user's
    own context_today put a 01:00 Dhaka job on yesterday."""
    return fields.Date.context_today(env["res.users"].with_context(tz=DHAKA_TZ))


def default_today(record):
    """Field default: the Dhaka business day."""
    return today(record.env)


# ------------------------------------------------------- A05 build (S3)
DHAKA_TZ = "Asia/Dhaka"
# D1 (owner, 20 Nov 2026): the GL accounts of e-waste money, by code, set by
# the deploy data. FAIL CLOSED when unset or unknown in the company's chart.
P_ACCOUNT = "cd_ewaste.account_code.%s"
ACCOUNT_ROLES = {
    # 400109 Other Income
    "recovery_income": "e-waste recovered-material (scrap) income",
    # NEW 'E-waste Collection & Recycling Cost' (expense)
    "recycling_cost": "e-waste collection incentives and recycler fees (expense)",
}
# AUT-ESG-11: the recycler's certificate is due this many days after the
# transfer unless the recycler's own agreed window says otherwise.
P_CERT_DUE_DAYS = "cd_ewaste.certificate_due_days"
DEFAULT_CERT_DUE_DAYS = 30
# ... and transfers to it are suspended at this many overdue batches.
P_SUSPEND_AFTER = "cd_ewaste.certificate_overdue_suspend_after"
DEFAULT_SUSPEND_AFTER = 2
# AUT-ESG-12: licence warnings at T-60, T-30 and T-7 days.
P_LICENCE_STAGES = "cd_ewaste.licence_warning_stages"
DEFAULT_LICENCE_STAGES = "60,30,7"
# XC-24: the amount ladder of an e-waste settlement until DoA rules one
# (fix.dofa.ladder for fix.ewaste.settlement): at or below the first bound the
# E-Waste Finance Approver decides alone, above it a DOFA tier.
SETTLEMENT_TIERS = [
    (50000.0, False),
    (250000.0, "tier_2"),
    (1000000.0, "tier_3"),
    (float("inf"), "tier_4"),
]


def account(env, company, role):
    """The company's GL account for an e-waste money role. Refuses, never
    guesses (D1: deploy data sets cd_ewaste.account_code.<role>)."""
    key = P_ACCOUNT % role
    code = (param(env, key, "") or "").strip()
    label = ACCOUNT_ROLES.get(role, role)
    if not code:
        raise UserError(
            "E-waste money refused: system parameter %s (the GL account for %s) is not set."
            % (key, label)
        )
    acc = (
        env["account.account"]
        .sudo()
        .with_company(company)
        .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    )
    if not acc:
        raise UserError(
            "E-waste money refused: system parameter %s names account %s (%s), which is not "
            "in the chart of %s." % (key, code, label, company.name)
        )
    return acc


def licence_stages(env):
    raw = param(env, P_LICENCE_STAGES, DEFAULT_LICENCE_STAGES) or DEFAULT_LICENCE_STAGES
    out = set()
    for part in str(raw).split(","):
        try:
            days = int(part.strip())
        except ValueError:
            continue
        if days > 0:
            out.add(days)
    return sorted(out, reverse=True) or [60, 30, 7]


_PERIOD = re.compile(r"^(\d{4})(?:-(?:(\d{2})|[Qq]([1-4])))?$")


def period_bounds(period):
    """(first day, last day) of 'YYYY', 'YYYY-MM' or 'YYYY-Qn'; None if unparsable."""
    m = _PERIOD.match((period or "").strip())
    if not m:
        return None
    year = int(m.group(1))
    if m.group(2):
        month = int(m.group(2))
        if not 1 <= month <= 12:
            return None
        return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])
    if m.group(3):
        q = int(m.group(3))
        first = 3 * (q - 1) + 1
        last = first + 2
        return date(year, first, 1), date(year, last, calendar.monthrange(year, last)[1])
    return date(year, 1, 1), date(year, 12, 31)


def frozen_refuse(rec, names, why):
    labels = ", ".join(sorted(rec._fields[n].string or n for n in names))
    raise UserError("%s %s: %s can no longer change." % (rec.display_name, why, labels))


def changed_fields(rec, vals, names):
    """Of `names` in vals, those whose value would really change on `rec`."""
    return {n for n in set(vals) & set(names) if rec._fix_guard_differs(n, vals[n], rec[n])}


# ------------------------------------------------------------------ uploads
# M18 capture audit (13 Nov 2026): every M18 evidence link (licence, PIC,
# registration, recycler certificate, processing evidence, battery photo) was
# a picker over EXISTING attachments - nobody could upload the scan, so a
# recycler was never dispatchable and no certificate could be issued from the
# workspace. A form now sends the file itself (a non-stored file + file name);
# it becomes an attachment of the record and fills the link, which then
# passes the model's own state and freeze rules like any other write.
# `uploads` maps each link field to its (file field, file-name field).


def lift_uploads(records, vals, uploads):
    """vals with each staged file replaced by its new attachment's id."""
    staged = {f for pair in uploads.values() for f in pair}
    if not staged & set(vals):
        return vals
    vals = dict(vals)
    pending = []
    for link, (file_field, name_field) in uploads.items():
        data = vals.pop(file_field, None)
        name = (vals.pop(name_field, None) or "").strip()
        if data:
            pending.append((link, data, name))
    if not pending:
        return vals
    if len(records) != 1:
        raise UserError("Upload a scan on one record at a time.")
    for link, data, name in pending:
        label = records._fields[link].string or link
        attachment = records.env["ir.attachment"].create(
            {
                "name": name or "%s - %s" % (records.display_name, label),
                "datas": data,
                "res_model": records._name,
                "res_id": records.id,
            }
        )
        vals[link] = attachment.id
    return vals


def stage_uploads(vals_list, uploads):
    """Take the files off new records' values: they are attached after create
    (an attachment needs its record), through write() and its rules."""
    staged = {f for pair in uploads.values() for f in pair}
    return [{k: vals.pop(k) for k in list(vals) if k in staged} for vals in vals_list]


def attach_staged(records, staged):
    for rec, files in zip(records, staged, strict=True):
        if any(files.values()):
            rec.write(files)


def lock_uploads(locked, uploads):
    """A file input is locked whenever the link it fills is."""
    for link, pair in uploads.items():
        if link in locked:
            locked |= set(pair)
    return locked


def months_between(first, last):
    """The 'YYYY-MM' periods from first to last (dates), inclusive."""
    out = []
    if not first or not last or first > last:
        return out
    y, m = first.year, first.month
    while (y, m) <= (last.year, last.month):
        out.append("%04d-%02d" % (y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def notify(record, summary, note, group_xmlid=None):
    """Post on the record and, when someone holds the group, schedule a to-do
    for the first holder in the record's company. Safe to re-run."""
    record = record.sudo()
    if hasattr(record, "message_post"):
        record.message_post(body=note)
    if not group_xmlid or not hasattr(record, "activity_schedule"):
        return
    group = record.env.ref(group_xmlid, raise_if_not_found=False)
    if not group:
        return
    company = record.company_id if "company_id" in record._fields else record.env.company
    users = group.all_user_ids.filtered(lambda u: u.active and company in u.company_ids)
    if not users:
        return
    todo = record.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
    existing = record.activity_ids.filtered(lambda a: a.summary == summary)
    if todo and not existing:
        record.activity_schedule(
            activity_type_id=todo.id, summary=summary, note=note, user_id=users[0].id
        )
