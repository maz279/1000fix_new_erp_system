# A12 · M66 Internal IT Service Management — ITSM tickets, changes and the
# internal IT asset register.
import datetime

SURFACES = {
    "fix.itsm.ticket": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_resolve"},
    },
    "fix.itsm.change": {
        "order": "planned_on desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_implement", "action_rollback"},
    },
    "fix.itsm.asset": {"order": "name", "limit": 300, "actions": set()},
    "fix.itsm.catalogue": {"order": "category, name", "limit": 300, "actions": set()},
    "fix.itsm.problem": {
        "order": "opened_on desc, id desc",
        "limit": 300,
        "actions": {"action_known_error", "action_resolve", "action_close"},
    },
    "fix.itsm.licence": {"order": "renewal_on, id", "limit": 300, "actions": set()},
    "fix.itsm.ci": {"order": "ci_class, name", "limit": 400, "actions": set()},
}


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty,
    }


def sla_report(env, date_from=None, date_to=None, **params):
    tickets = env["fix.itsm.ticket"].sudo().search([])
    rows = [
        {
            "ticket": t.name,
            "title": t.title[:50],
            "category": dict(t._fields["category"].selection).get(t.category, t.category),
            "priority": dict(t._fields["priority"].selection).get(t.priority, t.priority),
            "requester": t.requester_id.name if t.requester_id else "—",
            "age_days": (datetime.date.today() - t.create_date.date()).days
            if t.create_date
            else "—",
            "state": dict(t._fields["state"].selection).get(t.state, t.state),
        }
        for t in tickets
    ]
    open_count = len([r for r in rows if r["state"] in ("New", "Open")])
    return _pack(
        "ITSM Ticket SLA — %d open of %d" % (open_count, len(rows)),
        ["ticket", "title", "category", "priority", "requester", "age_days", "state"],
        {
            "ticket": "Ticket",
            "title": "Title",
            "category": "Category",
            "priority": "Priority",
            "requester": "Requester",
            "age_days": "Age (d)",
            "state": "State",
        },
        rows,
        ["Age measured from creation; resolution stamps the closure."],
        empty="No ITSM tickets.",
    )


def change_success(env, date_from=None, date_to=None, **params):
    changes = env["fix.itsm.change"].sudo().search([])
    groups = {}
    for c in changes:
        key = c.change_type
        g = groups.setdefault(key, {"total": 0, "implemented": 0, "rolled_back": 0, "rejected": 0})
        g["total"] += 1
        if c.state == "implemented":
            g["implemented"] += 1
        elif c.state == "rolled_back":
            g["rolled_back"] += 1
        elif c.state == "rejected":
            g["rejected"] += 1
    rows = [
        {
            "type": dict(env["fix.itsm.change"]._fields["change_type"].selection).get(k, k),
            **v,
            "success": round(v["implemented"] / v["total"] * 100.0, 1) if v["total"] else 0.0,
        }
        for k, v in sorted(groups.items())
    ]
    return _pack(
        "Change Success Rate",
        ["type", "total", "implemented", "rolled_back", "rejected", "success"],
        {
            "type": "Change Type",
            "total": "Total",
            "implemented": "Implemented",
            "rolled_back": "Rolled Back",
            "rejected": "Rejected",
            "success": "Success %",
        },
        rows,
        ["Success = implemented over all decided changes of that type."],
        empty="No change requests.",
    )


def asset_lifecycle(env, date_from=None, date_to=None, **params):
    assets = env["fix.itsm.asset"].sudo().search([])
    today = datetime.date.today()
    rows = []
    for a in assets:
        warranty = ""
        if a.warranty_end:
            days = (a.warranty_end - today).days
            warranty = "Expired" if days < 0 else "%dd" % days
        rows.append(
            {
                "asset": a.name,
                "tag": a.asset_tag,
                "kind": dict(a._fields["asset_kind"].selection).get(a.asset_kind),
                "assigned": a.assigned_to_id.name if a.assigned_to_id else "—",
                "warranty": warranty or "—",
                "state": dict(a._fields["state"].selection).get(a.state, a.state),
            }
        )
    return _pack(
        "IT Asset Lifecycle — %d asset(s)" % len(rows),
        ["asset", "tag", "kind", "assigned", "warranty", "state"],
        {
            "asset": "Asset",
            "tag": "Tag",
            "kind": "Kind",
            "assigned": "Assigned To",
            "warranty": "Warranty",
            "state": "State",
        },
        rows,
        ["Warranty shows days left (Expired once past)."],
        empty="No IT assets registered.",
    )


def category_mix(env, date_from=None, date_to=None, **params):
    tickets = env["fix.itsm.ticket"].sudo().search([])
    groups = {}
    for t in tickets:
        key = t.category
        groups[key] = groups.get(key, 0) + 1
    rows = [
        {
            "category": dict(env["fix.itsm.ticket"]._fields["category"].selection).get(k, k),
            "tickets": v,
            "share": round(v / len(tickets) * 100.0, 1) if tickets else 0.0,
        }
        for k, v in sorted(groups.items(), key=lambda kv: -kv[1])
    ]
    return _pack(
        "Ticket Category Mix",
        ["category", "tickets", "share"],
        {"category": "Category", "tickets": "Tickets", "share": "% of Tickets"},
        rows,
        ["Share is over all tickets ever recorded."],
        empty="No ITSM tickets.",
    )


REPORTS = {
    "sla_report": sla_report,
    "change_success": change_success,
    "asset_lifecycle": asset_lifecycle,
    "category_mix": category_mix,
}


def kpis(env):
    tickets = env["fix.itsm.ticket"].sudo().search([])
    changes = env["fix.itsm.change"].sudo().search([])
    assets = env["fix.itsm.asset"].sudo().search([])
    return {
        "tickets_open": len(tickets.filtered(lambda t: t.state in ("new", "open"))),
        "tickets_total": len(tickets),
        "changes_pending": len(changes.filtered(lambda c: c.state in ("draft", "approved"))),
        "changes_total": len(changes),
        "assets_in_service": len(assets.filtered(lambda a: a.state == "in_service")),
        "assets_total": len(assets),
    }
