# A10 · M23 Quality Management (ISO) — surfaces, packs and KPIs over the NCR,
# CAPA and internal-audit engines plus the framework models (policy, process
# register, checklists, gates, certification, management review, CoPQ).

SURFACES = {
    "fix.qms.policy": {
        "order": "year desc, id desc",
        "limit": 200,
        "actions": {"action_approve"},
    },
    "fix.qms.process": {"order": "code", "limit": 300, "actions": set()},
    "fix.qms.checklist": {
        "order": "name",
        "limit": 200,
        "actions": {"action_publish"},
    },
    "fix.qms.gate": {"order": "sequence, id", "limit": 200, "actions": set()},
    "fix.ncr": {
        "order": "id desc",
        "limit": 400,
        "actions": set(),
    },
    "fix.capa": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_implement", "action_verify", "action_close"},
    },
    "fix.internal.audit": {
        "order": "scheduled_on desc, id desc",
        "limit": 300,
        "actions": {"action_execute", "action_report"},
    },
    "fix.qms.certification": {"order": "audit_date desc, id desc", "limit": 200, "actions": set()},
    "fix.qms.review": {
        "order": "review_date desc, id desc",
        "limit": 200,
        "actions": {"action_hold", "action_close"},
    },
    "fix.qms.copq": {"order": "period desc, id desc", "limit": 500, "actions": set()},
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
    ncrs = env["fix.ncr"].sudo().search([])
    capas = env["fix.capa"].sudo().search([])
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
    audits = env["fix.internal.audit"].sudo().search([])
    ncrs = env["fix.ncr"].sudo().search([])
    rows = []
    for audit in audits:
        findings = ncrs.filtered(
            lambda n, a=audit.id: getattr(n, "audit_id", False) and n.audit_id.id == a
        )
        rows.append(
            {
                "audit": audit.name if hasattr(audit, "name") else "Audit-%s" % audit.id,
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
            "Findings count the NCRs linked to the audit; the audit record carries no name field "
            "of its own, so the reference is shown as Audit-<id>."
        ],
        totals={"audit": "Total", "findings": sum(r["findings"] for r in rows)},
        empty="No internal audits recorded.",
    )


def repeat_failure(env, date_from=None, date_to=None, **params):
    """Repeat-failure escalation: NCRs whose source reference repeats."""
    ncrs = env["fix.ncr"].sudo().search([])
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
    records = env["fix.qms.copq"].sudo().search([])
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
    reviews = env["fix.qms.review"].sudo().search([], order="review_date desc", limit=1)
    ncrs = env["fix.ncr"].sudo().search([])
    capas = env["fix.capa"].sudo().search([])
    copq = env["fix.qms.copq"].sudo().search([])
    audit = env["fix.internal.audit"].sudo().search([])
    latest = reviews[:1]
    rows = [
        {
            "section": "Review",
            "metric": "Latest review",
            "value": latest.name if latest else "—",
            "detail": str(latest.review_date or "—") if latest else "—",
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
            "own decisions stay on the review record."
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
    ncrs = env["fix.ncr"].sudo().search([])
    capas = env["fix.capa"].sudo().search([])
    audits = env["fix.internal.audit"].sudo().search([])
    copq = env["fix.qms.copq"].sudo().search([])
    open_ncrs = ncrs.filtered(lambda n: n.state != "closed")
    verified = capas.filtered(lambda c: c.state in ("verified", "closed"))
    return {
        "major_ncs": len(ncrs.filtered(lambda n: n.severity in ("major", "critical"))),
        "capa_on_time": round(len(verified) / len(capas) * 100.0, 1) if capas else 0.0,
        "open_ncrs": len(open_ncrs),
        "audit_findings": len(audits.filtered(lambda a: a.state != "reported")),
        "first_pass_qc": None,
        "copq": round(sum(float(c.amount or 0.0) for c in copq), 2),
    }
