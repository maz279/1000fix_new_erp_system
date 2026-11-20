# A04 ERP audit (20 Nov 2026), X1/X2: one way for every A04 report pack and
# KPI to read its rows.
#
# The packs read with sudo() so that a manager sees the whole register, not
# only the rows their record rules expose. That is only safe when the read is
# limited to the companies the caller is allowed into, and it is only correct
# when it honours the period the screen asked for. 96/96 packs ignored the
# period and ~60 read across companies. Use scoped() instead of
# env[model].sudo().search([...]).
import datetime

import pytz
from odoo import fields

_DHAKA = pytz.timezone("Asia/Dhaka")


def _as_date(value):
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    try:
        return fields.Date.to_date(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _dhaka_day_start_utc(day):
    """00:00 Asia/Dhaka of `day`, as a naive UTC datetime (Odoo storage)."""
    local = _DHAKA.localize(datetime.datetime.combine(day, datetime.time.min))
    return local.astimezone(pytz.utc).replace(tzinfo=None)


def period_domain(Model, date_field, date_from=None, date_to=None):
    """Domain for `date_from <= date_field <= date_to` (inclusive business days).

    A Datetime field is compared on Asia/Dhaka day boundaries; a Date field
    directly. Either bound may be empty. Unknown fields add nothing."""
    if not date_field or date_field not in Model._fields:
        return []
    start, end = _as_date(date_from), _as_date(date_to)
    field = Model._fields[date_field]
    dom = []
    if field.type == "datetime":
        if start:
            dom.append((date_field, ">=", _dhaka_day_start_utc(start)))
        if end:
            dom.append((date_field, "<", _dhaka_day_start_utc(end + datetime.timedelta(days=1))))
    else:
        if start:
            dom.append((date_field, ">=", start))
        if end:
            dom.append((date_field, "<=", end))
    return dom


def company_domain(env, Model, company_field="company_id"):
    """Rows of the caller's allowed companies (plus shared rows with no company)."""
    if company_field not in Model._fields:
        return []
    return ["|", (company_field, "=", False), (company_field, "in", env.companies.ids)]


def scoped(
    env,
    model,
    domain=None,
    date_field=None,
    date_from=None,
    date_to=None,
    company_field="company_id",
    order=None,
    limit=None,
):
    """sudo() search limited to the caller's companies and the report period."""
    Model = env[model].sudo()
    dom = list(domain or [])
    dom += company_domain(env, Model, company_field)
    dom += period_domain(Model, date_field, date_from, date_to)
    return Model.search(dom, order=order, limit=limit)


def scoped_count(
    env,
    model,
    domain=None,
    date_field=None,
    date_from=None,
    date_to=None,
    company_field="company_id",
):
    Model = env[model].sudo()
    dom = list(domain or [])
    dom += company_domain(env, Model, company_field)
    dom += period_domain(Model, date_field, date_from, date_to)
    return Model.search_count(dom)
