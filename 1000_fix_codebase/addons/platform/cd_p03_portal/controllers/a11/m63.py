# A11 · M63 Process Automation — surfaces, packs and KPIs over the automation
# register, workflow instances, the unified task inbox, the DoA matrix,
# substitutions, business rules and the AUT/escalation signals.
import datetime

SURFACES = {
    "fix.automation": {"order": "code", "limit": 300, "actions": set()},
    "fix.workflow.instance": {
        "order": "started_at desc, id desc",
        "limit": 400,
        "actions": {"action_complete", "action_fail", "action_escalate"},
    },
    "fix.workflow.task": {
        "order": "created_at desc, id desc",
        "limit": 500,
        # R7: decided only by the assignee; the record's own approve method
        # runs inside the decision with the DOFA checks.
        "actions": {"action_approve", "action_reject", "action_return"},
    },
    "fix.approval.matrix": {
        "order": "res_model, decision_domain, date_from desc, id",
        "limit": 200,
        "actions": {"action_test_rule"},
    },
    # Read-only evidence: requests change only through their tasks, and the
    # history refuses every write.
    "fix.approval.request": {"order": "requested_at desc, id desc", "limit": 500, "actions": set()},
    "fix.approval.history": {"order": "at desc, id desc", "limit": 1000, "actions": set()},
    "fix.approval.substitution": {
        "order": "start_date desc, id desc",
        "limit": 200,
        "actions": {"action_activate", "action_expire"},
    },
    "fix.business.rule": {"order": "code", "limit": 300, "actions": {"action_new_version"}},
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


def automation_rate(env, date_from=None, date_to=None, **params):
    """Automation rate by process area: automated definitions vs manual tasks."""
    automations = env["fix.automation"].sudo().search([])
    tasks = env["fix.workflow.task"].sudo().search([])
    rules = env["fix.business.rule"].sudo().search([])
    groups = {}
    for rule in rules:
        key = rule.domain_area or "Unassigned"
        groups.setdefault(key, {"automations": 0, "manual": 0})
    for automation in automations:
        key = automation.code.split("-")[0] if "-" in automation.code else "Core"
        groups.setdefault(key, {"automations": 0, "manual": 0})
        groups[key]["automations"] += 1
    for task in tasks:
        if task.task_type == "data_entry":
            key = "Manual entry"
            groups.setdefault(key, {"automations": 0, "manual": 0})
            groups[key]["manual"] += 1
    rows = []
    for key, v in sorted(groups.items()):
        total = v["automations"] + v["manual"]
        rows.append(
            {
                "area": key,
                "automations": v["automations"],
                "manual": v["manual"],
                "rate": round(v["automations"] / total * 100.0, 1) if total else 0.0,
            }
        )
    return _pack(
        "Automation Rate by Process",
        ["area", "automations", "manual", "rate"],
        {
            "area": "Process Area",
            "automations": "Automated",
            "manual": "Manual Steps",
            "rate": "Automation Rate %",
        },
        rows,
        [
            "Automated counts register rows in the AUT; manual counts recorded data-entry "
            "tasks. Areas with no automation show 0%, not a blank."
        ],
        totals={
            "area": "Total",
            "automations": sum(r["automations"] for r in rows),
            "manual": sum(r["manual"] for r in rows),
        },
        empty="No automation register rows or tasks recorded.",
    )


def approval_cycle_time(env, date_from=None, date_to=None, **params):
    """Approval cycle time: decided tasks from creation to decision."""
    tasks = env["fix.workflow.task"].sudo().search([("state", "=", "done")])
    rows = []
    for task in tasks:
        if not (task.created_at and task.decided_at):
            continue
        hours = (task.decided_at - task.created_at).total_seconds() / 3600.0
        rows.append(
            {
                "task": task.name,
                "type": dict(task._fields["task_type"].selection).get(task.task_type),
                "assigned": task.assigned_to_id.name if task.assigned_to_id else "—",
                "created": str(task.created_at)[:16],
                "decided": str(task.decided_at)[:16],
                "hours": round(hours, 1),
            }
        )
    rows.sort(key=lambda r: -r["hours"])
    avg = round(sum(r["hours"] for r in rows) / len(rows), 1) if rows else 0.0
    return _pack(
        "Approval Cycle Time — avg %s h over %d decided task(s)" % (avg, len(rows)),
        ["task", "type", "assigned", "created", "decided", "hours"],
        {
            "task": "Task",
            "type": "Type",
            "assigned": "Assigned To",
            "created": "Created",
            "decided": "Decided",
            "hours": "Hours",
        },
        rows,
        [
            "Hours are measured from task creation to the recorded decision; pending tasks "
            "are not counted."
        ],
        totals={"task": "Average", "hours": avg},
        empty="No decided tasks recorded.",
    )


def escalation_analysis(env, date_from=None, date_to=None, **params):
    """Escalation analysis: escalated instances and overdue pending tasks."""
    instances = env["fix.workflow.instance"].sudo().search([("escalated", "=", True)])
    tasks = env["fix.workflow.task"].sudo().search([("state", "=", "pending")])
    now = fields_datetime_now()
    rows = []
    for instance in instances:
        rows.append(
            {
                "kind": "Workflow escalated",
                "reference": instance.name,
                "detail": instance.res_model or "—",
                "when": str(instance.started_at)[:16],
                "age_hours": round((now - instance.started_at).total_seconds() / 3600.0, 1)
                if instance.started_at
                else "—",
                "state": dict(instance._fields["state"].selection).get(
                    instance.state, instance.state
                ),
            }
        )
    for task in tasks:
        if not task.due_at or task.due_at >= now:
            continue
        rows.append(
            {
                "kind": "Task overdue",
                "reference": task.name,
                "detail": task.assigned_to_id.name if task.assigned_to_id else "Unassigned",
                "when": str(task.created_at)[:16],
                "age_hours": round((now - task.due_at).total_seconds() / 3600.0, 1),
                "state": "Pending",
            }
        )
    rows.sort(key=lambda r: -r["age_hours"] if isinstance(r["age_hours"], float) else 0)
    return _pack(
        "Escalation Analysis — %d escalation(s)" % len(rows),
        ["kind", "reference", "detail", "when", "age_hours", "state"],
        {
            "kind": "Kind",
            "reference": "Reference",
            "detail": "Detail",
            "when": "Since",
            "age_hours": "Age (h)",
            "state": "State",
        },
        rows,
        ["Escalated workflow instances plus pending tasks past their due time."],
        empty="No escalations or overdue tasks.",
    )


def rule_change_log(env, date_from=None, date_to=None, **params):
    """Rule change log: version bumps and last editor per rule."""
    rules = env["fix.business.rule"].sudo().search([])
    rows = []
    for rule in rules:
        rows.append(
            {
                "code": rule.code,
                "name": rule.name[:60],
                "area": rule.domain_area or "—",
                "type": dict(rule._fields["rule_type"].selection).get(rule.rule_type),
                "version": rule.version,
                "changed_by": rule.last_changed_by.name if rule.last_changed_by else "—",
                "changed_on": str(rule.last_changed_on or "—")[:16],
                "active": "Yes" if rule.active else "No",
            }
        )
    rows.sort(key=lambda r: r["changed_on"], reverse=True)
    return _pack(
        "Rule Change Log",
        ["code", "name", "area", "type", "version", "changed_by", "changed_on", "active"],
        {
            "code": "Code",
            "name": "Rule",
            "area": "Process Area",
            "type": "Rule Type",
            "version": "Version",
            "changed_by": "Changed By",
            "changed_on": "Changed On",
            "active": "Active",
        },
        rows,
        [
            "Each version bump is recorded on the rule; no separate audit table exists, so "
            "the current version and last change are the log."
        ],
        empty="No business rules recorded.",
    )


def fields_datetime_now():
    from odoo import fields as _f

    return _f.Datetime.now()


def approval_kpis(env, date_from=None, date_to=None, **params):
    """R11: the approval engine's health - pending by age, approvals by tier,
    approver = creator (must be 0), voids, escalations and cycle time."""
    k = env["fix.approval.request"].approval_kpis()
    rows = [
        {"measure": "Pending (all)", "value": k["pending"]},
        {"measure": "Pending under 24 h", "value": k["pending_under_24h"]},
        {"measure": "Pending 24-72 h", "value": k["pending_24_72h"]},
        {"measure": "Pending over 72 h", "value": k["pending_over_72h"]},
    ]
    rows += [
        {"measure": "Approved at %s" % tier.replace("_", " ").title(), "value": n}
        for tier, n in sorted(k["approved_by_tier"].items())
    ]
    rows += [
        {"measure": "Approver = creator (must be 0)", "value": k["approver_is_creator"]},
        {"measure": "Approvals voided by a change", "value": k["voided_by_change"]},
        {"measure": "Escalations", "value": k["escalations"]},
        {"measure": "Median cycle time (h)", "value": k["median_cycle_hours"]},
    ]
    return _pack(
        "Approval KPIs",
        ["measure", "value"],
        {"measure": "Measure", "value": "Value"},
        rows,
        [
            "Counted from fix.approval.request and its append-only history. Cycle time is "
            "request to decision, wall-clock hours."
        ],
        empty="No approval requests yet.",
    )


def _pct(part, whole):
    return round(part / whole * 100.0, 1) if whole else 0.0


def a02_control_figures(env) -> dict:
    """A02 audit C3: the service-operations controls, as numbers.

    The engine's "approver = creator" counts only routed requests, so it saw
    none of A02's own sign-offs. These read the A02 records directly: a cash
    variance approved by the cashier who counted it, a wipe certificate
    verified by the technician who wrote it, a delivery released without a
    verified OTP, and a field job completed without its evidence. Each module
    is read only when it is installed."""
    out = {
        "cash_variance_self_approved": 0,
        "wipe_cert_self_verified": 0,
        "delivery_otp_verified_pct": 0.0,
        "field_completion_evidence_pct": 0.0,
    }
    Shift = env.get("fix.cash.shift")
    if Shift is not None:
        approved = Shift.sudo().search([("supervisor_variance_approved_by", "!=", False)])
        out["cash_variance_self_approved"] = len(
            approved.filtered(
                lambda s: s.supervisor_variance_approved_by
                in (s.counted_by | s.operator_id.user_id)
            )
        )
    Cert = env.get("fix.data.wipe.certificate")
    if Cert is not None:
        verified = Cert.sudo().search([("verified_by_id", "!=", False)])
        out["wipe_cert_self_verified"] = len(
            verified.filtered(lambda c: c.verified_by_id == c.technician_id)
        )
    Order = env.get("fix.service.order")
    if Order is not None:
        delivered = Order.sudo().search([("state", "in", ("delivered", "closed"))])
        out["delivery_otp_verified_pct"] = _pct(
            len(delivered.filtered("delivery_otp_verified")), len(delivered)
        )
    Field = env.get("fix.field.order")
    if Field is not None:
        done = Field.sudo().search([("state", "=", "completed")])
        evidenced = done.filtered(
            lambda f: (f.customer_otp_verified or f.customer_signature_attachment_id)
            and f.post_work_photo_attachment_id
        )
        out["field_completion_evidence_pct"] = _pct(len(evidenced), len(done))
    return out


def a02_controls(env, **params):
    """A02 audit C3: segregation of duties and evidence coverage in A02."""
    k = a02_control_figures(env)
    rows = [
        {
            "measure": "Cash variance approved by its own cashier (must be 0)",
            "value": k["cash_variance_self_approved"],
        },
        {
            "measure": "Wipe certificate verified by its technician (must be 0)",
            "value": k["wipe_cert_self_verified"],
        },
        {"measure": "Deliveries with a verified OTP (%)", "value": k["delivery_otp_verified_pct"]},
        {
            "measure": "Field completions with full evidence (%)",
            "value": k["field_completion_evidence_pct"],
        },
    ]
    return _pack(
        "A02 Control KPIs",
        ["measure", "value"],
        {"measure": "Measure", "value": "Value"},
        rows,
        [
            "Read from the M04 cash shifts, M06 wipe certificates, M01 delivered or closed "
            "orders and M02 completed field orders. Evidence = a verified customer OTP or "
            "signature, plus the post-work photo."
        ],
    )


REPORTS = {
    "approval_kpis": approval_kpis,
    "a02_controls": a02_controls,
    "automation_rate": automation_rate,
    "approval_cycle_time": approval_cycle_time,
    "escalation_analysis": escalation_analysis,
    "rule_change_log": rule_change_log,
}


def kpis(env):
    automations = env["fix.automation"].sudo().search([])
    instances = env["fix.workflow.instance"].sudo().search([])
    tasks = env["fix.workflow.task"].sudo().search([])
    rules = env["fix.business.rule"].sudo().search([])
    decided = tasks.filtered(lambda t: t.state == "done" and t.created_at and t.decided_at)
    month_start = datetime.date.today().replace(day=1)
    escalations = instances.filtered(
        lambda i: i.escalated and i.started_at and i.started_at.date() >= month_start
    )
    running = instances.filtered(lambda i: i.state == "running")
    completed = instances.filtered(lambda i: i.state == "completed")
    total_hours = sum((t.decided_at - t.created_at).total_seconds() / 3600.0 for t in decided)
    approvals = env["fix.approval.request"].approval_kpis()
    a02 = a02_control_figures(env)
    return {
        "a02_variance_self_approved": a02["cash_variance_self_approved"],
        "a02_cert_self_verified": a02["wipe_cert_self_verified"],
        "a02_delivery_otp_pct": a02["delivery_otp_verified_pct"],
        "a02_completion_evidence_pct": a02["field_completion_evidence_pct"],
        "automation_rate": round(len(completed) / len(instances) * 100.0, 1) if instances else 0.0,
        "open_workflows": len(running),
        "avg_approval_time": round(total_hours / len(decided), 1) if decided else 0.0,
        "rule_repository": len(rules),
        "escalations_mtd": len(escalations),
        "stp_share": round(
            len(instances.filtered(lambda i: not i.escalated)) / len(instances) * 100.0, 1
        )
        if instances
        else 0.0,
        "automations": len(automations),
        "approvals_pending": approvals["pending"],
        "approvals_overdue": approvals["pending_over_72h"],
        "approver_is_creator": approvals["approver_is_creator"],
        "approval_median_hours": approvals["median_cycle_hours"],
    }
