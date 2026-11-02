# A10 · M60 Governance, Risk & Compliance — surfaces, packs and KPIs over the
# risk register, controls/testing, SoD, authority, obligations, licences,
# policies, legal matters, PDPA requests and whistleblowing.
import datetime

SURFACES = {
    "fix.risk.register": {
        "order": "id desc",
        "limit": 400,
        "actions": set(),
    },
    "fix.control": {"order": "control_code", "limit": 400, "actions": set()},
    "fix.grc.control.test": {"order": "tested_on desc, id desc", "limit": 400, "actions": set()},
    "fix.grc.sod.rule": {
        "order": "name",
        "limit": 300,
        "actions": {"action_waive"},
    },
    "fix.grc.authority": {"order": "amount_limit desc", "limit": 200, "actions": set()},
    "fix.compliance.obligation": {"order": "clause_reference", "limit": 400, "actions": set()},
    "fix.grc.licence": {"order": "valid_to", "limit": 300, "actions": set()},
    "fix.grc.policy": {
        "order": "code",
        "limit": 300,
        "actions": {"action_approve"},
    },
    "fix.grc.legal": {
        "order": "opened_on desc, id desc",
        "limit": 300,
        "actions": {"action_close"},
    },
    "fix.grc.pdpa": {
        "order": "received_on desc, id desc",
        "limit": 300,
        "actions": {"action_fulfil"},
    },
    "fix.grc.whistle": {
        "order": "reported_on desc, id desc",
        "limit": 300,
        "actions": {"action_investigate"},
    },
    "fix.compliance.framework": {"order": "id desc", "limit": 400, "actions": set()},
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


def risk_heat_map(env, date_from=None, date_to=None, **params):
    """Risk heat map: the register grouped by likelihood × impact."""
    risks = env["fix.risk.register"].sudo().search([])
    rows = []
    for risk in risks:
        rows.append(
            {
                "risk": risk.name[:70],
                "category": dict(risk._fields["category"].selection).get(risk.category),
                "likelihood": risk.likelihood,
                "impact": getattr(risk, "impact", None) or "—",
                "score": risk.risk_score or 0,
                "band": (
                    "High"
                    if (risk.risk_score or 0) >= 15
                    else "Medium"
                    if (risk.risk_score or 0) >= 8
                    else "Low"
                ),
            }
        )
    rows.sort(key=lambda r: -r["score"])
    high = len([r for r in rows if r["band"] == "High"])
    return _pack(
        "Risk Heat Map — %d risk(s), %d in the High band (score 15+)" % (len(rows), high),
        ["risk", "category", "likelihood", "impact", "score", "band"],
        {
            "risk": "Risk",
            "category": "Category",
            "likelihood": "Likelihood",
            "impact": "Impact",
            "score": "Inherent Score",
            "band": "Band",
        },
        rows,
        [
            "The register computes inherent score as likelihood × impact (1-5 each, so 1-25). "
            "There is no appetite field on the model, so the band is the declared score rule "
            "(High 15+, Medium 8-14, Low below 8) — not a stored appetite."
        ],
        empty="No risks recorded.",
    )


def control_deficiency(env, date_from=None, date_to=None, **params):
    """Control deficiency log: controls whose latest test was not effective."""
    controls = env["fix.control"].sudo().search([])
    tests = env["fix.grc.control.test"].sudo().search([], order="tested_on desc")
    rows = []
    for control in controls:
        control_tests = tests.filtered(lambda t, c=control.id: t.control_id.id == c)
        latest = control_tests[:1]
        if not latest:
            continue
        if latest.result == "effective":
            continue
        rows.append(
            {
                "control": control.control_code or control.name,
                "name": control.name[:60],
                "frequency": dict(control._fields["frequency"].selection).get(control.frequency),
                "tested": str(latest.tested_on),
                "exceptions": latest.exceptions,
                "result": dict(latest._fields["result"].selection).get(latest.result),
                "owner": control.risk_id.name[:40] if control.risk_id else "—",
            }
        )
    rows.sort(key=lambda r: r["tested"], reverse=True)
    return _pack(
        "Control Deficiency Log",
        ["control", "name", "frequency", "tested", "exceptions", "result", "owner"],
        {
            "control": "Control Code",
            "name": "Control",
            "frequency": "Frequency",
            "tested": "Last Tested",
            "exceptions": "Exceptions",
            "result": "Result",
            "owner": "Risk Addressed",
        },
        rows,
        [
            "Only controls with a latest test result of partially effective or ineffective are "
            "deficiencies; untested controls are not counted as effective."
        ],
        empty="No control deficiencies recorded.",
    )


def licence_expiry(env, date_from=None, date_to=None, **params):
    """Corporate licence expiry register."""
    licences = env["fix.grc.licence"].sudo().search([])
    today = datetime.date.today()
    rows = []
    for lic in licences:
        days = (lic.valid_to - today).days if lic.valid_to else None
        rows.append(
            {
                "licence": lic.name,
                "type": dict(lic._fields["licence_type"].selection).get(lic.licence_type),
                "number": lic.number or "—",
                "authority": lic.authority or "—",
                "valid_to": str(lic.valid_to or "—"),
                "days_left": days if days is not None else "—",
                "state": dict(lic._fields["state"].selection).get(lic.state, lic.state),
            }
        )
    rows.sort(key=lambda r: r["valid_to"])
    gaps = len([r for r in rows if r["state"] in ("Expired", "Suspended")])
    return _pack(
        "Licence Expiry Register — %d gap(s)" % gaps,
        ["licence", "type", "number", "authority", "valid_to", "days_left", "state"],
        {
            "licence": "Licence",
            "type": "Type",
            "number": "Number",
            "authority": "Authority",
            "valid_to": "Valid To",
            "days_left": "Days Left",
            "state": "State",
        },
        rows,
        ["Days left is computed from the validity date; a negative number is already expired."],
        empty="No corporate licences recorded.",
    )


def attestation_status(env, date_from=None, date_to=None, **params):
    """Policy attestation status: policies requiring attestation and their state."""
    policies = env["fix.grc.policy"].sudo().search([])
    rows = []
    for policy in policies:
        rows.append(
            {
                "code": policy.code,
                "policy": policy.name[:60],
                "type": dict(policy._fields["policy_type"].selection).get(policy.policy_type),
                "version": policy.version,
                "approved_on": str(policy.approved_on or "—"),
                "review_due": str(policy.review_due or "—"),
                "attestation": "Required" if policy.attestation_required else "Not required",
                "state": dict(policy._fields["state"].selection).get(policy.state, policy.state),
            }
        )
    rows.sort(key=lambda r: r["code"])
    required = len([r for r in rows if r["attestation"] == "Required"])
    return _pack(
        "Attestation Status — %d policy(ies) requiring attestation" % required,
        ["code", "policy", "type", "version", "approved_on", "review_due", "attestation", "state"],
        {
            "code": "Code",
            "policy": "Policy",
            "type": "Type",
            "version": "Version",
            "approved_on": "Approved",
            "review_due": "Review Due",
            "attestation": "Attestation",
            "state": "State",
        },
        rows,
        [
            "The model records whether attestation is required; per-employee attestation "
            "sign-offs are not stored, so no compliance percentage is claimed."
        ],
        empty="No policies recorded.",
    )


def _ineffective_latest(env, controls, tests):
    count = 0
    for control in controls:
        latest = tests.filtered(lambda t, c=control.id: t.control_id.id == c)[:1]
        if latest and latest.result == "ineffective":
            count += 1
    return count


def board_risk_pack(env, date_from=None, date_to=None, **params):
    """Board risk pack: the live risk/control/compliance signals."""
    risks = env["fix.risk.register"].sudo().search([])
    controls = env["fix.control"].sudo().search([])
    tests = env["fix.grc.control.test"].sudo().search([], order="tested_on desc")
    licences = env["fix.grc.licence"].sudo().search([])
    legal = env["fix.grc.legal"].sudo().search([])
    pdpa = env["fix.grc.pdpa"].sudo().search([])
    rows = [
        {
            "section": "Risk",
            "metric": "Risks registered",
            "value": len(risks),
            "detail": "all categories",
        },
        {
            "section": "Risk",
            "metric": "High-likelihood risks",
            "value": len(risks.filtered(lambda r: r.likelihood in ("4", "5"))),
            "detail": "likelihood 4-5",
        },
        {
            "section": "Control",
            "metric": "Controls",
            "value": len(controls),
            "detail": "in framework",
        },
        {
            "section": "Control",
            "metric": "Ineffective controls (latest test)",
            "value": _ineffective_latest(env, controls, tests),
            "detail": "latest test per control",
        },
        {
            "section": "Compliance",
            "metric": "Licence gaps",
            "value": len(licences.filtered(lambda ln: ln.state in ("expired", "suspended"))),
            "detail": "expired/suspended",
        },
        {
            "section": "Legal",
            "metric": "Open legal matters",
            "value": len(legal.filtered(lambda ln: ln.state != "closed")),
            "detail": "not closed",
        },
        {
            "section": "Data",
            "metric": "PDPA requests pending",
            "value": len(pdpa.filtered(lambda p: p.outcome == "pending")),
            "detail": "pending",
        },
    ]
    return _pack(
        "Board Risk Pack",
        ["section", "metric", "value", "detail"],
        {"section": "Section", "metric": "Metric", "value": "Value", "detail": "Basis"},
        rows,
        ["Assembles the live registers; it does not restate historical board decisions."],
        empty="No GRC signals.",
    )


REPORTS = {
    "risk_heat_map": risk_heat_map,
    "control_deficiency": control_deficiency,
    "licence_expiry": licence_expiry,
    "attestation": attestation_status,
    "board_risk_pack": board_risk_pack,
}


def kpis(env):
    risks = env["fix.risk.register"].sudo().search([])
    controls = env["fix.control"].sudo().search([])
    licences = env["fix.grc.licence"].sudo().search([])
    legal = env["fix.grc.legal"].sudo().search([])
    pdpa = env["fix.grc.pdpa"].sudo().search([])
    policies = env["fix.grc.policy"].sudo().search([])
    today = datetime.date.today()
    above_appetite = len([r for r in risks if (r.risk_score or 0) >= 15])
    return {
        "risks_above_appetite": above_appetite,
        "control_tests_due": len(
            controls.filtered(
                lambda c: not c.last_tested or c.last_tested <= today - datetime.timedelta(days=365)
            )
        ),
        "licence_gaps": len(licences.filtered(lambda ln: ln.state in ("expired", "suspended"))),
        "policy_attestations": len(
            policies.filtered(lambda p: p.attestation_required and p.state == "approved")
        ),
        "legal_matters_open": len(legal.filtered(lambda ln: ln.state != "closed")),
        "dsr_pending": len(pdpa.filtered(lambda p: p.outcome == "pending")),
    }
