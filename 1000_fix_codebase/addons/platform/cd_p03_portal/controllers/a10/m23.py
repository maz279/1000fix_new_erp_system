# A10 · M23 Quality Management (ISO) — surfaces, packs and KPIs over the NCR,
# CAPA and internal-audit engines plus the framework models (policy, process
# register, checklists, gates, certification, management review, CoPQ).

SURFACES = {
    "fix.qms.policy": {
        "order": "year desc, id desc",
        "limit": 200,
        "actions": {"action_approve"},
    },
    "fix.qms.process": {
        "order": "code",
        "limit": 300,
        # A10 S6: the register's state is the Quality Manager's act
        "actions": {"action_retire"},
    },
    "fix.qms.checklist": {
        "order": "name",
        "limit": 200,
        "actions": {"action_publish", "action_retire", "action_new_version"},
    },
    "fix.qms.gate": {
        "order": "sequence, id",
        "limit": 200,
        "actions": {"action_retire"},
    },
    "fix.ncr": {
        "order": "id desc",
        "limit": 400,
        # M23 capture audit (2026-11-19): the typed "Set Root Cause" left the
        # workspace — a person establishes the root cause through a completed
        # Root-Cause Analysis (fix.qms.rca), which refuses a symptom repeated
        # as the cause (BRU-QMS-04) and a major NCR without 8D (BRU-QMS-14).
        # The model method stays for system hand-offs (M60 control tests).
        "actions": {
            "action_record_containment",
            "action_open_capa",
            "action_dispose",
            "action_close",
        },
    },
    "fix.capa": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_implement", "action_verify", "action_close"},
    },
    "fix.internal.audit": {
        "order": "scheduled_on desc, id desc",
        "limit": 300,
        "actions": {"action_execute", "action_report", "action_acknowledge"},
    },
    "fix.qms.certification": {
        "order": "audit_date desc, id desc",
        "limit": 200,
        "actions": {"action_pass", "action_record_result"},
    },
    "fix.qms.review": {
        "order": "review_date desc, id desc",
        "limit": 200,
        "actions": {"action_pull_inputs", "action_hold", "action_close"},
    },
    # ISO 9.3.2 inputs are PULLED by fix.qms.review.action_pull_inputs (the
    # model guards every field): a read-only register, no actions, no writes.
    "fix.qms.review.input": {
        "order": "review_id desc, id",
        "limit": 400,
        "actions": set(),
    },
    "fix.qms.review.action": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_done"},
    },
    "fix.qms.copq": {"order": "period desc, id desc", "limit": 500, "actions": set()},
    # M23 capture audit (2026-11-19): the spec records the pages lacked
    "fix.qms.objective": {"order": "period desc, id desc", "limit": 300, "actions": set()},
    "fix.qms.change.assessment": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_assess", "action_release", "action_reject"},
    },
    # items are authored inside their template's grid; this register reads
    "fix.qms.checklist.item": {
        "order": "checklist_id, sequence, id",
        "limit": 500,
        "actions": set(),
    },
    "fix.qms.rca": {"order": "id desc", "limit": 300, "actions": {"action_complete"}},
    "fix.capa.action": {"order": "id desc", "limit": 400, "actions": {"action_done"}},
    "fix.qms.audit.programme": {
        "order": "year desc, id desc",
        "limit": 100,
        "actions": {"action_approve", "action_close"},
    },
    "fix.qms.auditor": {"order": "id desc", "limit": 200, "actions": set()},
    "fix.qms.audit.finding": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_raise_ncr", "action_close"},
    },
    "fix.qms.evidence.release": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_approve", "action_release", "action_refuse"},
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


def ncr_capa_register(env, date_from=None, date_to=None, **params):
    """NCR & CAPA register: every NCR with its severity, state and CAPA count."""
    ncrs = env["fix.ncr"].search([])
    capas = env["fix.capa"].search([])
    rows = []
    for ncr in ncrs:
        related = capas.filtered(lambda c, n=ncr.id: c.ncr_id.id == n)
        rows.append(
            {
                "ncr": ncr.name,
                "severity": dict(ncr._fields["severity"].selection).get(ncr.severity),
                "state": dict(ncr._fields["state"].selection).get(ncr.state, ncr.state),
                "source": dict(ncr._fields["source"].selection).get(ncr.source),
                "disposition": dict(ncr._fields["disposition"].selection).get(
                    ncr.disposition, ncr.disposition
                ),
                "capas": len(related),
                "capa_state": ", ".join(sorted({c.state for c in related})) or "—",
                "effectiveness": ", ".join(
                    sorted(
                        {
                            dict(c._fields["effectiveness_result"].selection).get(
                                c.effectiveness_result, c.effectiveness_result
                            )
                            for c in related
                        }
                    )
                )
                or "—",
            }
        )
    rows.sort(key=lambda r: r["ncr"], reverse=True)
    return _pack(
        "NCR & CAPA Register — %d NCR(s)" % len(rows),
        [
            "ncr",
            "severity",
            "state",
            "source",
            "disposition",
            "capas",
            "capa_state",
            "effectiveness",
        ],
        {
            "ncr": "NCR",
            "severity": "Severity",
            "state": "State",
            "source": "Source",
            "disposition": "Disposition",
            "effectiveness": "CAPA effectiveness",
            "capas": "CAPAs",
            "capa_state": "CAPA States",
        },
        rows,
        [
            "One row per NCR; the CAPA count and their states come from the linked CAPA "
            "records, not from a stored counter."
        ],
        totals={"ncr": "Total", "capas": sum(r["capas"] for r in rows)},
        empty="No NCRs recorded.",
    )


def audit_programme(env, date_from=None, date_to=None, **params):
    """Audit programme status: internal audits and their findings."""
    audits = env["fix.internal.audit"].search([])
    rows = []
    for audit in audits:
        findings = audit.finding_ids
        rows.append(
            {
                "audit": audit.name or "Audit-%s" % audit.id,
                "branch": audit.branch_id.name,
                "scheduled": str(audit.scheduled_on),
                "auditor": audit.auditor_id.name,
                "scope": audit.scope or "—",
                "findings": len(findings),
                "state": dict(audit._fields["state"].selection).get(audit.state, audit.state),
            }
        )
    rows.sort(key=lambda r: r["scheduled"], reverse=True)
    return _pack(
        "Audit Programme Status",
        ["audit", "branch", "scheduled", "auditor", "scope", "findings", "state"],
        {
            "audit": "Audit",
            "branch": "Branch",
            "scheduled": "Scheduled",
            "auditor": "Auditor",
            "scope": "Scope",
            "findings": "Findings",
            "state": "State",
        },
        rows,
        [
            "Findings count the audit's own finding records (major, minor, observation and "
            "opportunity for improvement); a major or minor finding raises its NCR."
        ],
        totals={"audit": "Total", "findings": sum(r["findings"] for r in rows)},
        empty="No internal audits recorded.",
    )


def repeat_failure(env, date_from=None, date_to=None, **params):
    """Repeat-failure escalation: NCRs whose source reference repeats."""
    ncrs = env["fix.ncr"].search([])
    groups = {}
    for ncr in ncrs:
        key = ncr.order_id.name if getattr(ncr, "order_id", False) and ncr.order_id else None
        if not key:
            key = ncr.description[:40] if ncr.description else "Unspecified"
        groups.setdefault(key, []).append(ncr)
    rows = []
    for key, batch in groups.items():
        if len(batch) < 2:
            continue
        rows.append(
            {
                "reference": key,
                "occurrences": len(batch),
                "severities": ", ".join(sorted({b.severity for b in batch})),
                "latest": max(b.id for b in batch),
                "states": ", ".join(sorted({b.state for b in batch})),
            }
        )
    rows.sort(key=lambda r: -r["occurrences"])
    return _pack(
        "Repeat-Failure Escalation — %d repeated reference(s)" % len(rows),
        ["reference", "occurrences", "severities", "latest", "states"],
        {
            "reference": "Service Order / Description",
            "occurrences": "Occurrences",
            "severities": "Severities",
            "latest": "Latest NCR",
            "states": "States",
        },
        rows,
        [
            "Groups NCRs by their service order, else by the first 40 characters of the "
            "description; two or more occurrences is a repeat failure."
        ],
        empty="No repeated failures detected.",
    )


def copq_analysis(env, date_from=None, date_to=None, **params):
    """CoPQ analysis by period and category."""
    records = env["fix.qms.copq"].search([])
    groups = {}
    for rec in records:
        key = (rec.period, dict(rec._fields["category"].selection).get(rec.category))
        groups[key] = groups.get(key, 0.0) + float(rec.amount or 0.0)
    rows = [
        {"period": p, "category": c, "amount": round(v, 2)} for (p, c), v in sorted(groups.items())
    ]
    return _pack(
        "CoPQ Analysis — cost of poor quality",
        ["period", "category", "amount"],
        {"period": "Period", "category": "Category", "amount": "Amount"},
        rows,
        [
            "Recorded CoPQ lines only; rework/scrap/warranty/complaint/inspection/downtime "
            "categories are the model's own selection."
        ],
        totals={"period": "Total", "amount": round(sum(r["amount"] for r in rows), 2)},
        empty="No CoPQ records.",
    )


def management_review_pack(env, date_from=None, date_to=None, **params):
    """Management review pack: the review record plus the quality signals a
    review needs (open NCRs, CAPA states, audit findings, CoPQ total)."""
    reviews = env["fix.qms.review"].search([], order="review_date desc", limit=1)
    ncrs = env["fix.ncr"].search([])
    capas = env["fix.capa"].search([])
    copq = env["fix.qms.copq"].search([])
    audit = env["fix.internal.audit"].search([])
    latest = reviews[:1]
    rows = [
        {
            "section": "Review",
            "metric": "Latest review",
            "value": latest.name if latest else "—",
            "detail": str(latest.review_date or "—") if latest else "—",
        },
        {
            "section": "Review",
            "metric": "ISO 9.3.2 inputs pulled",
            "value": len(latest.input_ids) if latest else 0,
            "detail": (
                "%d required kind(s) missing (A10 P1-6)" % latest.inputs_missing
                if latest
                else "no review"
            ),
        },
        {
            "section": "Review",
            "metric": "Tracked actions open (9.3.3)",
            "value": latest.open_actions if latest else 0,
            "detail": "of %d action line(s)" % len(latest.action_ids) if latest else "—",
        },
        {
            "section": "Nonconformance",
            "metric": "Open NCRs",
            "value": len(ncrs.filtered(lambda n: n.state not in ("closed",))),
            "detail": "not closed",
        },
        {
            "section": "Nonconformance",
            "metric": "Major / critical NCRs",
            "value": len(ncrs.filtered(lambda n: n.severity in ("major", "critical"))),
            "detail": "all time",
        },
        {
            "section": "CAPA",
            "metric": "CAPA open",
            "value": len(capas.filtered(lambda c: c.state != "closed")),
            "detail": "not closed",
        },
        {
            "section": "CAPA",
            "metric": "CAPA verified",
            "value": len(capas.filtered(lambda c: c.state == "verified")),
            "detail": "awaiting close",
        },
        {
            "section": "Audit",
            "metric": "Internal audits executed",
            "value": len(audit.filtered(lambda a: a.state in ("executed", "reported"))),
            "detail": "of %d" % len(audit),
        },
        {
            "section": "CoPQ",
            "metric": "CoPQ recorded",
            "value": round(sum(float(c.amount or 0.0) for c in copq), 2),
            "detail": "BDT all periods",
        },
    ]
    return _pack(
        "Management Review Pack",
        ["section", "metric", "value", "detail"],
        {"section": "Section", "metric": "Metric", "value": "Value", "detail": "Basis"},
        rows,
        [
            "The pack assembles the review record with the live quality signals; the review's "
            "own decisions stay on the review record.",
            "A10 P1-6: the ISO 9.3.2 inputs live ON the review (fix.qms.review.input lines "
            "pulled by action_pull_inputs — never typed) and the outputs are tracked action "
            "lines (9.3.3). The counts here mirror those records; this pack reports, it does "
            "not decide.",
        ],
        empty="No review signals.",
    )


REPORTS = {
    "ncr_capa_register": ncr_capa_register,
    "audit_programme": audit_programme,
    "repeat_failure": repeat_failure,
    "copq_analysis": copq_analysis,
    "management_review": management_review_pack,
}


def kpis(env):
    # A10 S6 (M23-10): the tiles read with the CALLER's scope — the isolation
    # rules apply, so a Dhaka clerk no longer counts Chattogram's
    # non-conformances — and every number is measured from the record that
    # owns it, not invented.
    ncrs = env["fix.ncr"].search([])
    capas = env["fix.capa"].search([])
    copq = env["fix.qms.copq"].search([])
    open_ncrs = ncrs.filtered(lambda n: n.state != "closed")
    # A10 (D7, M23-10): 'on time' means the verified date beat the due date —
    # counting every verified CAPA as on-time invented the figure the
    # certification body reads.
    verdicts = capas.filtered(lambda c: c.effectiveness_result != "pending")
    on_time = verdicts.filtered(
        lambda c: not c.due_on or (c.verified_on and c.verified_on <= c.due_on)
    )
    # A10 S6 (M23-10): 'open audit findings' counted AUDITS (planned and
    # executed programmes). Findings are their own record — the GRC audit
    # finding (fix.audit.finding) — and one is open until its CAPA is closed.
    findings = env["fix.audit.finding"].search([("capa_status", "!=", "closed")])
    # M23 capture audit (2026-11-19): the process audit now records its own
    # findings (fix.qms.audit.finding) - an open one is any not yet closed
    process_findings = env["fix.qms.audit.finding"].search_count([("state", "!=", "closed")])
    # first-pass yield is the QC checklist's own verdict: passed over
    # COMPLETED checks (passed or failed). Pending checks measure nothing.
    completed = env["fix.qc.checklist"].search([("state", "in", ("passed", "failed"))])
    first_pass = (
        round(len(completed.filtered(lambda q: q.state == "passed")) / len(completed) * 100.0, 1)
        if completed
        else None
    )
    return {
        "major_ncs": len(ncrs.filtered(lambda n: n.severity in ("major", "critical"))),
        "capa_on_time": round(len(on_time) / len(verdicts) * 100.0, 1) if verdicts else 0.0,
        "open_ncrs": len(open_ncrs),
        "audit_findings": len(findings) + process_findings,
        "first_pass_qc": first_pass,
        "copq": round(sum(float(c.amount or 0.0) for c in copq), 2),
    }
