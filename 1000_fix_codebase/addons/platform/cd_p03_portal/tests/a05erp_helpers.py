"""Shared fixtures of the A05 ERP audit report / document tests (20 Nov 2026).

The report tests measure the PACKS, not the workflows that produce the rows,
so the rows are written straight to the database (state, dates, ledger
postings) the way the workflow leaves them, and the tracking history a
hand-over leaves is recorded with its own date. Everything is rolled back by
the odoo_env fixture.
"""

import datetime
import itertools

import pytz

SEQ = itertools.count(1)


def branch(env):
    """A branch that belongs to an operating unit (created when the test
    database has none; the company's legal entity is reused)."""
    found = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if found:
        return found
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].search([], limit=1)
    if not entity:
        entity = env["fix.entity"].create(
            {"legal_name": "A05ERP Entity", "code": "A5EENT", "company_id": env.company.id}
        )
    return env["fix.branch"].create(
        {
            "name": "A05ERP Branch",
            "code": "A5E-BR",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )


def other_ou(env, ou):
    other = env["operating.unit"].search(
        [("id", "!=", ou.id), ("company_id", "=", env.company.id)], limit=1
    )
    return other or env["operating.unit"].create(
        {
            "name": "A05ERP Other OU %d" % next(SEQ),
            "code": "A5E%d" % next(SEQ),
            "partner_id": env.company.partner_id.id,
            "company_id": env.company.id,
        }
    )


def dhaka_noon_utc(day):
    """Naive-UTC instant of 12:00 Dhaka on ``day``."""
    tz = pytz.timezone("Asia/Dhaka")
    local = tz.localize(datetime.datetime.combine(day, datetime.time(12, 0)))
    return local.astimezone(pytz.utc).replace(tzinfo=None)


def set_cols(rec, **vals):
    """Write columns as the workflow leaves them (no ORM gate: the report is
    under test, not the transition)."""
    # pending ORM writes first: a create's deferred write must not land after
    # (and over) the row written here
    rec.env.flush_all()
    cols = ", ".join('"%s" = %%s' % k for k in vals)
    rec.env.cr.execute(
        'UPDATE "%s" SET %s WHERE id = %%s' % (rec._table, cols), [*vals.values(), rec.id]
    )
    rec.env.invalidate_all()
    return rec


def track(rec, value, day, field="state"):
    """Record the tracking history of ``field`` becoming ``value`` on ``day``."""
    env = rec.env
    fld = env["ir.model.fields"]._get(rec._name, field)
    label = dict(rec._fields[field]._description_selection(env)).get(value, value)
    env["mail.message"].sudo().create(
        {
            "model": rec._name,
            "res_id": rec.id,
            "message_type": "notification",
            "body": "",
            "date": dhaka_noon_utc(day),
            "tracking_value_ids": [
                (0, 0, {"field_id": fld.id, "old_value_char": "", "new_value_char": label})
            ],
        }
    )


def user(env, login, groups=(), ou=None, modules=()):
    """An internal user with the given groups (plus every group the named
    modules declare, so the module's own ACL never refuses first)."""
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    if modules:
        ids += (
            env["ir.model.data"]
            .sudo()
            .search([("module", "in", list(modules)), ("model", "=", "res.groups")])
            .mapped("res_id")
        )
    vals = {
        "name": "%s %d" % (login, next(SEQ)),
        "login": "a05erp.%s.%d@a05.test" % (login, next(SEQ)),
        "group_ids": [(6, 0, ids)],
    }
    if ou:
        vals["assigned_operating_unit_ids"] = [(6, 0, ou.ids)]
        vals["default_operating_unit_id"] = ou.id
    return env["res.users"].with_context(no_reset_password=True).create(vals)


def row_of(pack, key, value):
    rows = [r for r in pack["rows"] if r.get(key) == value]
    return rows[0] if rows else None
