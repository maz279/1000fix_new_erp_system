# A12 · M66 Internal IT Service Management — ITSM tickets, changes and the
# internal IT asset register.
#
# A12 workflow audit (2026-11-04) R4/X5: this surface declared no writable
# fields (the form endpoint then wrote whatever it was sent, state included)
# and its buttons covered a fraction of the lifecycle. Every surface key now
# declares its WRITABLE whitelist — workflow fields (state, resolution,
# escalated, approved_by, PIR) are NOT in it: they move only through the
# whitelisted actions below. KPIs and reports read as the CALLER (R4): no
# sudo, so the role's own read scope is what the numbers show.
import datetime

SURFACES = {
    "fix.itsm.ticket": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_assign", "action_start", "action_resolve", "action_close"},
        # R4: the ticket list reads in the CALLER's scope (sudo read is the
        # lead/B1 plumbing change that consumes this flag — see Needs).
        "rules": True,
    },
    "fix.itsm.change": {
        "order": "planned_on desc, id desc",
        "limit": 300,
        # action_approve is deliberately absent: approval runs through the M63
        # inbox (P1-1), never a direct button.
        "actions": {"action_submit", "action_implement", "action_record_pir", "action_rollback"},
    },
    "fix.itsm.asset": {
        "order": "name",
        "limit": 300,
        "actions": {"action_allocate", "action_send_repair", "action_recover", "action_retire"},
    },
    "fix.itsm.catalogue": {
        "order": "category, name",
        "limit": 300,
        "actions": set(),
    },
    "fix.itsm.problem": {
        "order": "opened_on desc, id desc",
        "limit": 300,
        "actions": {"action_investigate", "action_known_error", "action_resolve", "action_close"},
    },
    "fix.itsm.licence": {"order": "renewal_on, id", "limit": 300, "actions": set()},
    "fix.itsm.ci": {"order": "ci_class, name", "limit": 400, "actions": set()},
}

# R4: what /p03/model/write may set per surface. Workflow-controlled fields
# (state, resolution, escalated, resolved_on, approved_by_id, implemented_on,
# the PIR fields, known_error) are absent on purpose: the model guard refuses
# them anyway, and the whitelist keeps the form from even offering them.
WRITABLE = {
    "fix.itsm.ticket": {
        "title",
        "description",
        "category",
        "priority",
        "requester_id",
        "assigned_to",
        "catalogue_id",
        "operating_unit_id",
    },
    "fix.itsm.change": {
        "title",
        "change_type",
        "risk",
        "risk_probability",
        "risk_impact",
        "requested_by_id",
        "implementer_id",
        "planned_on",
        "implementation_plan",
        "test_plan",
        "rollback_plan",
        "change_window_hours",
        "asset_ids",
        "release_note",
    },
    "fix.itsm.asset": {
        "name",
        "asset_tag",
        "asset_kind",
        "assigned_to_id",
        "serial_no",
        "warranty_end",
        "os_version",
        # wipe_certificate is NOT here (M66-9): the evidence is supplied to
        # action_retire, which stamps it in a guarded write — a direct column
        # write would let anyone re-paper a retired asset.
    },
    "fix.itsm.catalogue": {
        "code",
        "name",
        "category",
        "description",
        "fulfilment_team",
        "target_hours",
        "cost_per_request",
        "requires_approval",
        "active",
    },
    "fix.itsm.problem": {
        "title",
        "description",
        "root_cause",
        "workaround",
        "severity",
        "owner_id",
        "opened_on",
    },
    "fix.itsm.licence": {
        "name",
        "vendor",
        "licence_type",
        "seats_owned",
        "seats_assigned",
        "unit_cost",
        "purchased_on",
        "renewal_on",
    },
    "fix.itsm.ci": {
        "name",
        "ci_class",
        "ci_key",
        "environment_id",
        "owner_id",
        "depends_on",
        "criticality",
        "support_hours",
        "life_status",
        "asset_id",
    },
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
    # R4: caller scope — the reader sees the tickets their role may see.
    tickets = env["fix.itsm.ticket"].search([])
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
            "deadline": str(t.sla_deadline or "—"),
            "escalated": "Yes" if t.escalated else "",
            "state": dict(t._fields["state"].selection).get(t.state, t.state),
        }
        for t in tickets
    ]
    open_count = len([r for r in rows if r["state"] in ("New", "Assigned", "In Progress")])
    breach_count = len([r for r in rows if r["escalated"] == "Yes"])
    return _pack(
        "ITSM Ticket SLA — %d open of %d, %d escalated" % (open_count, len(rows), breach_count),
        [
            "ticket",
            "title",
            "category",
            "priority",
            "requester",
            "age_days",
            "deadline",
            "escalated",
            "state",
        ],
        {
            "ticket": "Ticket",
            "title": "Title",
            "category": "Category",
            "priority": "Priority",
            "requester": "Requester",
            "age_days": "Age (d)",
            "deadline": "SLA Deadline",
            "escalated": "Escalated",
            "state": "State",
        },
        rows,
        [
            "Age measured from creation; the deadline is the catalogue target hours "
            "(default 8h) from creation. Escalated tickets passed it: the hourly cron "
            "raised their priority and flagged them."
        ],
        empty="No ITSM tickets.",
    )


def change_success(env, date_from=None, date_to=None, **params):
    changes = env["fix.itsm.change"].search([])
    groups = {}
    for c in changes:
        key = c.change_type
        g = groups.setdefault(key, {"total": 0, "implemented": 0, "rolled_back": 0, "rejected": 0})
        g["total"] += 1
        # implemented + reviewed both mean the change landed and stuck.
        if c.state in ("implemented", "reviewed"):
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
        [
            "Success = implemented (incl. post-reviewed) over all decided changes of "
            "that type. Approvals themselves run through the M63 approval inbox."
        ],
        empty="No change requests.",
    )


def asset_lifecycle(env, date_from=None, date_to=None, **params):
    assets = env["fix.itsm.asset"].search([])
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
        [
            "Warranty shows days left (Expired once past). Retirement needs the "
            "data-wipe certificate and an unassigned asset (M66-9)."
        ],
        empty="No IT assets registered.",
    )


def category_mix(env, date_from=None, date_to=None, **params):
    tickets = env["fix.itsm.ticket"].search([])
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
    # R4: caller scope. A plain internal user sees their own read scope, not
    # the whole company's register through sudo.
    tickets = env["fix.itsm.ticket"].search([])
    changes = env["fix.itsm.change"].search([])
    assets = env["fix.itsm.asset"].search([])
    return {
        "tickets_open": len(
            tickets.filtered(lambda t: t.state in ("new", "assigned", "in_progress"))
        ),
        "tickets_escalated": len(tickets.filtered(lambda t: t.escalated)),
        "tickets_total": len(tickets),
        "changes_pending": len(changes.filtered(lambda c: c.approval_state == "pending")),
        "changes_total": len(changes),
        "assets_in_service": len(assets.filtered(lambda a: a.state == "in_service")),
        "assets_total": len(assets),
    }
