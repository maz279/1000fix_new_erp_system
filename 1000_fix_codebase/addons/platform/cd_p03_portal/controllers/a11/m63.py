# A11 · M63 Process Automation — surfaces, packs and KPIs over the automation
# register, workflow instances, the unified task inbox, the DoA matrix,
# substitutions, business rules and the AUT/escalation signals.
import datetime

from odoo import fields
from odoo.exceptions import AccessError, UserError

# A11 audit E1: the fields /p03/model/write accepts on each M63 surface,
# exactly what the M63 workspace forms (static/src/a11/m63.js) offer as
# editable. A surface with no form accepts nothing. Workflow fields (states,
# stamps, the approver, the version) are never listed: they change only
# through their actions. The ACL still decides who may write at all: the
# rule book (matrix, rules, automations, instances) is the DoA
# Administrator's. Kept in step with the forms by test_a11_e1_e4.py.
WRITABLE = {
    "fix.automation": frozenset(
        {
            "code",
            "trigger",
            "engine",
            "engine_ref",
            "failure_policy",
            "implementation",
            "executor_note",
            "action",
            "active",
        }
    ),
    # An instance is started by its automation's engine and changed only by a
    # recorded manual intervention (M63 capture audit 2026-11-18): its form
    # shows it, it is never typed.
    "fix.workflow.instance": frozenset(),
    "fix.workflow.task": frozenset(),
    "fix.approval.matrix": frozenset(
        {
            "name",
            "decision_domain",
            "res_model",
            "condition",
            "threshold",
            "approver_role",
            "notes",
            "approver_group_id",
            "approval_policy",
            "sla_hours",
            "calendar_id",
            "max_escalations",
            "escalate_to_id",
            "final_action",
            "date_from",
            "date_to",
            "active",
        }
    ),
    "fix.approval.request": frozenset(),
    "fix.approval.history": frozenset(),
    "fix.approval.substitution": frozenset(
        {"absent_approver_id", "delegate_id", "start_date", "end_date", "reason"}
    ),
    "fix.business.rule": frozenset(
        {
            "code",
            "name",
            "domain_area",
            "rule_type",
            "expression",
            "error_message",
            "automation_id",
            "active",
        }
    ),
    # M63 capture audit (2026-11-18): the run's results are set by the run.
    "fix.rule.simulation": frozenset({"matrix_id", "date_from", "date_to"}),
    "fix.automation.register": frozenset(
        {
            "name",
            "process_area",
            "owning_module",
            "volume_per_month",
            "automated",
            "automation_id",
            "stp_rate",
            "notes",
            "active",
        }
    ),
    "fix.workflow.intervention": frozenset({"instance_id", "action", "reason"}),
}

SURFACES = {
    "fix.automation": {
        "order": "code",
        "limit": 300,
        # The grid the surface serves (mirrored by M63-definitions in the
        # fragment): the register row, the mechanism that really executes it,
        # and the three computed verdicts a reader needs to tell fact from
        # fiction. binding_state / executor_active / coverage_state are
        # computed and therefore never writable.
        "cols": [
            "code",
            "trigger",
            "engine",
            "engine_ref",
            "implementation",
            "binding_state",
            "coverage_state",
            "executor_active",
            "failure_policy",
            "active",
        ],
        "actions": set(),
        "writable": WRITABLE["fix.automation"],
    },
    "fix.workflow.instance": {
        "order": "started_at desc, id desc",
        "limit": 400,
        # Each one is a recorded manual intervention with a reason.
        "actions": {"action_complete", "action_fail", "action_escalate", "action_terminate"},
        "writable": WRITABLE["fix.workflow.instance"],
    },
    "fix.workflow.task": {
        "order": "created_at desc, id desc",
        "limit": 500,
        # R7: decided only by the assignee; the record's own approve method
        # runs inside the decision with the DOFA checks.
        "actions": {"action_approve", "action_reject", "action_return"},
        "writable": WRITABLE["fix.workflow.task"],
    },
    "fix.approval.matrix": {
        "order": "res_model, decision_domain, date_from desc, id",
        "limit": 200,
        # G9: a dated row in force is never edited in place; New Version
        # closes it and opens the successor. The engine guard holds the line
        # regardless of what the form offers.
        "actions": {"action_test_rule", "action_new_version"},
        "writable": WRITABLE["fix.approval.matrix"],
    },
    # Read-only evidence: requests change only through their tasks, and the
    # history refuses every write.
    "fix.approval.request": {
        "order": "requested_at desc, id desc",
        "limit": 500,
        "actions": set(),
        "writable": WRITABLE["fix.approval.request"],
    },
    "fix.approval.history": {
        "order": "at desc, id desc",
        "limit": 1000,
        "actions": set(),
        "writable": WRITABLE["fix.approval.history"],
    },
    "fix.approval.substitution": {
        "order": "start_date desc, id desc",
        "limit": 200,
        "actions": {"action_activate", "action_expire"},
        "writable": WRITABLE["fix.approval.substitution"],
    },
    "fix.business.rule": {
        "order": "code",
        "limit": 300,
        "actions": {"action_new_version"},
        "writable": WRITABLE["fix.business.rule"],
    },
    # M63 capture audit (2026-11-18): rule simulation, the routine-work
    # register and manual interventions. Simulations and interventions are
    # evidence: created, never changed.
    "fix.rule.simulation": {
        "order": "run_at desc, id desc",
        "limit": 300,
        "actions": set(),
        "writable": WRITABLE["fix.rule.simulation"],
    },
    "fix.automation.register": {
        "order": "process_area, name",
        "limit": 500,
        "actions": {"action_mark_reviewed"},
        "writable": WRITABLE["fix.automation.register"],
    },
    "fix.workflow.intervention": {
        "order": "at desc, id desc",
        "limit": 500,
        "actions": set(),
        "writable": WRITABLE["fix.workflow.intervention"],
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


def _routine_work_totals(env):
    """(total volume, automated volume, straight-through volume) over the
    routine-work register — the denominator of the automation rate.

    fix.automation.register semantics (read from the model, 19.0.1.2.0):
      volume_per_month  how often the task happens in a month
      automated         a task counts as automated only when it names the
                        automation that does it
      stp_rate          the share of that volume completed with no human step
      automated_volume  volume_per_month x stp_rate/100, and 0 unless automated
    So the automation rate is the share of registered volume a named
    automation covers, and the STP share is the share that flows through with
    no human step (never the two conflated)."""
    rows = env["fix.automation.register"].sudo().search([])
    total = sum(rows.mapped("volume_per_month"))
    automated = sum(row.volume_per_month for row in rows if row.automated)
    straight_through = sum(rows.mapped("automated_volume"))
    return total, automated, straight_through


def automation_rate(env, date_from=None, date_to=None, **params):
    """Automation rate by process area, over the routine-work register.

    The register is the denominator of the 85% target (spec AUT-BPA-21,
    AC-25): every recurring task with its monthly volume, and the share an
    automation completes straight through. It replaced a count of AUT rows
    against hand-entered tasks, which measured nothing a person does."""
    entries = env["fix.automation.register"].search([])
    groups = {}
    for entry in entries:
        g = groups.setdefault(
            entry.process_area or "Unassigned",
            {"tasks": 0, "automated_tasks": 0, "volume": 0, "automated": 0.0},
        )
        g["tasks"] += 1
        g["automated_tasks"] += 1 if entry.automated else 0
        g["volume"] += entry.volume_per_month
        g["automated"] += entry.automated_volume
    rows = [
        {
            "area": key,
            "tasks": v["tasks"],
            "automated_tasks": v["automated_tasks"],
            "volume": v["volume"],
            "automated": round(v["automated"], 1),
            "rate": round(v["automated"] / v["volume"] * 100.0, 1) if v["volume"] else 0.0,
        }
        for key, v in sorted(groups.items())
    ]
    total, _coverage_volume, straight_through = _routine_work_totals(env)
    rate = round(straight_through / total * 100.0, 1) if total else None
    return _pack(
        "Automation Rate by Process — %s of routine-work volume automated straight "
        "through (target 85%%)" % ("%.1f%%" % rate if rate is not None else "not measurable"),
        ["area", "tasks", "automated_tasks", "volume", "automated", "rate"],
        {
            "area": "Process Area",
            "tasks": "Routine Tasks",
            "automated_tasks": "Automated Tasks",
            "volume": "Volume / Month",
            "automated": "Automated Volume",
            "rate": "Automation Rate %",
        },
        rows,
        [
            "Each routine task counts by its monthly volume; an automated task counts the "
            "volume its automation completes with no human step (volume x straight-through "
            "rate), so a task 'partly automated' contributes only its automated part. A task "
            "counts as automated only when it names the active automation that does it.",
            "This pack weights each task by its straight-through rate. The Automation Rate "
            "KPI next to it counts the share of registered volume a named automation "
            "COVERS (automated or not straight through), so the two numbers differ by "
            "design and both are stated on their tile.",
            "Without registered routine work the 85% target has no denominator and cannot "
            "be measured, only claimed — the pack then shows no rate at all.",
        ],
        totals={
            "area": "Total",
            "tasks": len(entries),
            "automated_tasks": len(entries.filtered("automated")),
            "volume": total,
            "automated": round(straight_through, 1),
            "rate": rate,
        },
        empty="No routine work is registered yet: add each recurring task on the "
        "Audit & Performance page.",
    )


def approval_cycle_time(env, date_from=None, date_to=None, **params):
    """Approval cycle time: decided tasks from creation to decision."""
    tasks = env["fix.workflow.task"].search([("state", "=", "done")])
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
    instances = env["fix.workflow.instance"].search([("escalated", "=", True)])
    tasks = env["fix.workflow.task"].search([("state", "=", "pending")])
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
    """Rule change log: version bumps and last editor per rule.

    `last_changed_on` is stored in UTC; it is printed in the CALLER's
    timezone (the grid already does), with the zone named in the column
    label — a pack that printed UTC beside a Dhaka grid read six hours apart
    (A11 pass 1, D-L14)."""
    rules = env["fix.business.rule"].search([])
    tz_name = env.tz or "UTC"
    rows = []
    for rule in rules:
        changed_on = "—"
        if rule.last_changed_on:
            local = fields.Datetime.context_timestamp(rule, rule.last_changed_on)
            changed_on = local.strftime("%Y-%m-%d %H:%M")
        rows.append(
            {
                "code": rule.code,
                "name": rule.name[:60],
                "area": rule.domain_area or "—",
                "type": dict(rule._fields["rule_type"].selection).get(rule.rule_type),
                "version": rule.version,
                "changed_by": rule.last_changed_by.name if rule.last_changed_by else "—",
                "changed_on": changed_on,
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
            "changed_on": "Changed On (%s)" % tz_name,
            "active": "Active",
        },
        rows,
        [
            "Each version bump is recorded on the rule; no separate audit table exists, so "
            "the current version and last change are the log. Times are shown in the "
            "reader's timezone (%s), the same as the grid." % tz_name,
        ],
        empty="No business rules recorded.",
    )


def _require_scheduled_jobs_reader(env):
    """E6 pattern (m25._require_finance_reader): the ir.cron estate is
    infrastructure, not business data. A refused caller gets a specific
    error, never a silent partial list."""
    if env.su:
        return
    group = env.ref("cd_workflow_engine.group_doa_administrator", raise_if_not_found=False)
    if not group or env.user not in group.user_ids:
        raise UserError(
            "Scheduled Jobs is reserved for DoA Administrators (M63): the Odoo "
            "scheduled-action estate (interval, last and next run) is platform "
            "infrastructure, not business data, and is not served to your account."
        )


def scheduled_jobs(env, date_from=None, date_to=None, **params):
    """The REAL scheduled jobs of this estate: ir.cron rows, with the module
    that owns each one. The previous "Scheduled Jobs" screen listed the 16
    register rows whose engine claimed Airflow — DAGs that do not exist
    (A11 pass 1, D-L13)."""
    _require_scheduled_jobs_reader(env)
    crons = env["ir.cron"].sudo().with_context(active_test=False).search([], order="nextcall, id")
    owners = {}
    rows_xml = (
        env["ir.model.data"]
        .sudo()
        .search_read(
            [("model", "=", "ir.cron"), ("res_id", "in", crons.ids)],
            ["module", "name", "res_id"],
        )
    )
    for data in rows_xml:
        owners.setdefault(data["res_id"], "%s.%s" % (data["module"], data["name"]))
    tz_name = env.tz or "UTC"

    def _local(value):
        if not value:
            return "—"
        # an empty recordset is a BaseModel too: only its env (the caller's
        # timezone) is read
        local = fields.Datetime.context_timestamp(env["ir.cron"], value)
        return local.strftime("%Y-%m-%d %H:%M")

    rows = []
    for cron in crons:
        rows.append(
            {
                "job": cron.cron_name or "—",
                "module": owners.get(cron.id, "—"),
                "interval": "%s %s" % (cron.interval_number, cron.interval_type or ""),
                "active": "Yes" if cron.active else "No",
                "last_run": _local(cron.lastcall),
                "next_run": _local(cron.nextcall),
            }
        )
    return _pack(
        "Scheduled Jobs — %d Odoo scheduled action(s)" % len(rows),
        ["job", "module", "interval", "active", "last_run", "next_run"],
        {
            "job": "Scheduled Action",
            "module": "Owning Module (xmlid)",
            "interval": "Interval",
            "active": "Active",
            "last_run": "Last Run (%s)" % tz_name,
            "next_run": "Next Run (%s)" % tz_name,
        },
        rows,
        [
            "These are Odoo scheduled actions (ir.cron) — the mechanism that really runs "
            "this estate's automations. Airflow DAGs are not used by these automations: "
            "the register names ir.cron, model methods and event consumers.",
            "Sorted by next run. Times are shown in the reader's timezone (%s)." % tz_name,
        ],
        empty="No scheduled action in the registry.",
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
        {
            "measure": "Approver = creator, requester, amount-changer or their delegate "
            "(must be 0)",
            "value": k["approver_is_creator"],
        },
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
        approved = Shift.search([("supervisor_variance_approved_by", "!=", False)])
        out["cash_variance_self_approved"] = len(
            approved.filtered(
                lambda s: (
                    s.supervisor_variance_approved_by in (s.counted_by | s.operator_id.user_id)
                )
            )
        )
    Cert = env.get("fix.data.wipe.certificate")
    if Cert is not None:
        verified = Cert.search([("verified_by_id", "!=", False)])
        out["wipe_cert_self_verified"] = len(
            verified.filtered(lambda c: c.verified_by_id == c.technician_id)
        )
    Order = env.get("fix.service.order")
    if Order is not None:
        delivered = Order.search([("state", "in", ("delivered", "closed"))])
        out["delivery_otp_verified_pct"] = _pct(
            len(delivered.filtered("delivery_otp_verified")), len(delivered)
        )
    Field = env.get("fix.field.order")
    if Field is not None:
        done = Field.search([("state", "=", "completed")])
        evidenced = done.filtered(
            lambda f: (
                (f.customer_otp_verified or f.customer_signature_attachment_id)
                and f.post_work_photo_attachment_id
            )
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
    "scheduled_jobs": scheduled_jobs,
}


def kpis(env):
    instances = env["fix.workflow.instance"].search([])
    tasks = env["fix.workflow.task"].search([])
    rules = env["fix.business.rule"].search([])
    decided = tasks.filtered(lambda t: t.state == "done" and t.created_at and t.decided_at)
    month_start = datetime.date.today().replace(day=1)
    month_start_dt = datetime.datetime.combine(month_start, datetime.time.min)
    running = instances.filtered(lambda i: i.state == "running")
    total_hours = sum((t.decided_at - t.created_at).total_seconds() / 3600.0 for t in decided)
    approvals = env["fix.approval.request"].approval_kpis()
    a02 = a02_control_figures(env)
    # A4-F01: the coverage tiles count the CATALOGUE by what really executes
    # each row — full+verified, partial+verified, nothing — never the number
    # of rows. A 'broken' row (claims an implementation its reference cannot
    # back) is in none of the three and is reported by the gap report.
    catalogue = env["fix.automation"].with_context(active_test=False).search([])
    coverage = {"implemented": 0, "partial": 0, "planned": 0, "broken": 0}
    for row in catalogue:
        coverage[row.coverage_state] += 1
    # A4-F06: both rates come from the routine-work register (the 85% target's
    # denominator); with no registered work they are None ("—"), never 0.0.
    routine_total, routine_automated, routine_stp = _routine_work_totals(env)
    automation_rate = round(routine_automated / routine_total * 100.0, 1) if routine_total else None
    stp_share = round(routine_stp / routine_total * 100.0, 1) if routine_total else None
    # A4-F13: escalations = approval-history escalations this month PLUS
    # escalated workflow instances this month. If the caller may not read the
    # history the tile is None, not a smaller number.
    try:
        with env.cr.savepoint():
            approval_escalations = env["fix.approval.history"].search_count(
                [("event", "=", "escalated"), ("at", ">=", month_start_dt)]
            )
    except AccessError:
        approval_escalations = None
    instance_escalations = len(
        instances.filtered(
            lambda i: i.escalated and i.started_at and i.started_at >= month_start_dt
        )
    )
    escalations_mtd = (
        None if approval_escalations is None else approval_escalations + instance_escalations
    )
    return {
        "a02_variance_self_approved": a02["cash_variance_self_approved"],
        "a02_cert_self_verified": a02["wipe_cert_self_verified"],
        "a02_delivery_otp_pct": a02["delivery_otp_verified_pct"],
        "a02_completion_evidence_pct": a02["field_completion_evidence_pct"],
        "automation_rate": automation_rate,
        "rules_unsimulated": len(env["fix.approval.matrix"]._rules_in_force_never_simulated()),
        "interventions_mtd": env["fix.workflow.intervention"].search_count(
            [("at", ">=", month_start_dt)]
        ),
        "open_workflows": len(running),
        "avg_approval_time": round(total_hours / len(decided), 1) if decided else 0.0,
        "rule_repository": len(rules),
        "escalations_mtd": escalations_mtd,
        "stp_share": stp_share,
        "automations": coverage["implemented"],
        "automations_partial": coverage["partial"],
        "automations_planned": coverage["planned"],
        "automations_broken": coverage["broken"],
        "approvals_pending": approvals["pending"],
        "approvals_overdue": approvals["pending_over_72h"],
        "approver_is_creator": approvals["approver_is_creator"],
        "approval_median_hours": approvals["median_cycle_hours"],
    }
