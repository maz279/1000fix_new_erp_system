# A03 · M33 Customer & Party Master — the models the generic workspace screens
# may read, the workflow methods they may call (/p03/model/records,
# /p03/model/action), the computed reports (/p03/model/report) and the module
# KPI tiles. Reads use the CALLER's environment; only the company-wide list
# reads sudo after check_access (the generic endpoint's own rule).
#
# Rebuild 2026-10-27: mirrors the CANONICAL registry M33 — 5 groups,
# 15 screens, 6 reports, 5 forms, freg src 100 — over cd_party_master.
import datetime
import logging

from odoo import fields

_logger = logging.getLogger(__name__)

SURFACES = {
    "res.partner": {
        "order": "write_date desc, id desc",
        "limit": 200,
        "actions": {"action_reactivate_party"},
    },
    "fix.party.role": {
        "order": "partner_id, role_type",
        "limit": 300,
        "actions": set(),
    },
    "fix.party.hierarchy": {
        "order": "date_from desc, id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.bd.address": {
        # Party-side addresses (FR-CPM-014/016): the D365 Address-with-GPS
        # form writes here; the governed BD parts live on the platform model.
        "order": "write_date desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.identity.document": {
        "order": "partner_id, document_type",
        "limit": 300,
        # A03 audit M33-9: KYC verification by a data steward (four eyes).
        "actions": {"action_kyc_submit", "action_kyc_verify", "action_kyc_fail"},
    },
    "fix.transparency.notice": {
        "order": "version desc",
        "limit": 100,
        "actions": {"action_retire"},
    },
    "fix.consent": {
        "order": "date_granted desc, id desc",
        "limit": 300,
        "actions": {"action_withdraw"},
    },
    "fix.otp.log": {
        "order": "requested_at desc, id desc",
        "limit": 200,
        "actions": {"action_mark_verified", "action_expire"},
    },
    "fix.registration.approval": {
        "order": "requested_at desc, id desc",
        "limit": 200,
        # A03 audit M33-1: the steps are decided in the M63 inbox; pressing
        # approve on the record was one person doing both steps.
        "actions": {"action_request_approval", "action_recall_approval"},
    },
    "fix.party.duplicate": {
        "order": "score desc, id desc",
        "limit": 200,
        "actions": {"action_review", "action_confirm", "action_dismiss"},
    },
    "fix.party.merge": {
        "order": "requested_at desc, id desc",
        "limit": 200,
        "actions": {"action_execute", "action_reverse"},
    },
    "fix.party.quality": {
        "order": "composite desc, id desc",
        "limit": 300,
        "actions": {"action_recompute"},
    },
    "fix.rights.request": {
        "order": "received_at desc, id desc",
        "limit": 200,
        "actions": {"action_verify", "action_start", "action_fulfil", "action_reject"},
    },
    "fix.segment": {
        "order": "code",
        "limit": 100,
        "actions": {"action_add_members", "action_remove_member"},
    },
    "fix.segment.membership": {
        "order": "segment_id, entered_at desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.credit.profile": {
        # The model of record is cd_billing_engine's (M20, FR-ARB-030/031);
        # M33 surfaces it (spec §3.3) — its own hold action is the workflow.
        "order": "write_date desc, id desc",
        "limit": 200,
        "actions": {"action_toggle_hold"},
    },
    "fix.dedup.rule": {"order": "id desc", "limit": 400, "actions": set()},
    # --- added by the A03 gap-closure build -------------------
    # Each of these is bound by a workspace screen below; an
    # unservable surface is what test_a03_registry_coverage exists
    # to catch, and a surface no screen opens is dead weight it
    # also catches.
    "fix.dedup.job": {
        "order": "started_at desc, id desc",
        "limit": 200,
        "actions": {"action_run"},
    },
}


# ---------------------------------------------------------------- reports
def _r(value):
    return round(value or 0.0, 1)


def party_360(env, limit=50, **_kw):
    """The 360 summary board: per party — roles, consent currency, identity,
    quality, credit hold. Assembled from live reads, never literals. All
    selection values render as LABELS, never raw keys (audit D10: the user's
    PDF showed 'draft'/'employee'/'none' leaking through)."""
    partners = env["res.partner"].search(
        ["|", ("customer_rank", ">", 0), ("role_ids", "!=", False)],
        order="write_date desc",
        limit=int(limit or 50),
    )
    # The credit profile model of record lives in cd_billing_engine (loads
    # after the party module) — reach it by search, not a one2many.
    credit_by_customer = {p.customer_id.id: p for p in env["fix.credit.profile"].search([])}

    # label maps straight off the models' own selection definitions
    def sel_labels(model, field):
        meta = env[model].fields_get([field], attributes=["selection"])
        return dict(meta.get(field, {}).get("selection") or [])

    status_lbl = sel_labels("res.partner", "party_status")
    role_lbl = sel_labels("fix.party.role", "role_type")
    consent_lbl = sel_labels("fix.consent", "state")
    rows = []
    for p in partners:
        latest = p.consent_ids.filtered(lambda c: c.state in ("granted", "withdrawn"))[:1]
        credit = credit_by_customer.get(p.id)
        rows.append(
            {
                "party": p.name,
                "status": status_lbl.get(p.party_status, p.party_status),
                "roles": ", ".join(
                    sorted({role_lbl.get(r.role_type, r.role_type) for r in p.role_ids})
                )
                or "—",
                "identity_docs": len(p.identity_document_ids),
                "consent": (consent_lbl.get(latest.state, latest.state) if latest else "none"),
                "quality": next((q.composite for q in p.quality_ids), None),
                "credit_hold": ("hold" if credit and credit.credit_hold else "none")
                if credit
                else "—",
            }
        )
    cols = ["party", "status", "roles", "identity_docs", "consent", "quality", "credit_hold"]
    return {
        "title": "Party 360 (top %d by activity)" % len(partners),
        "cols": cols,
        "labels": {
            "party": "Party",
            "status": "Status",
            "roles": "Roles",
            "identity_docs": "Identity Docs",
            "consent": "Consent (latest)",
            "quality": "Quality %",
            "credit_hold": "Credit Hold",
        },
        "rows": rows,
        "notes": [
            "Assembled from live party reads; consent shows the latest decision "
            "(granted/withdrawn), never an inferred state.",
        ],
        "empty": "No parties with roles or customer activity yet.",
    }


def customer_growth(env, date_from=None, date_to=None, **_kw):
    """New parties by district (state) in the window — the registry's
    'Customer Growth by District' report."""
    today = datetime.date.today()
    dt = fields.Date.to_date(date_to) or today
    df = fields.Date.to_date(date_from) or datetime.date(dt.year, 1, 1)
    if df > dt:
        df, dt = dt, df
    partners = env["res.partner"].search(
        [
            "|",
            ("customer_rank", ">", 0),
            ("role_ids", "!=", False),
            ("create_date", ">=", fields.Datetime.to_datetime(df)),
            ("create_date", "<=", datetime.datetime.combine(dt, datetime.time(23, 59))),
        ]
    )
    by_district = {}
    for p in partners:
        key = p.state_id.name or "(unassigned district)"
        by_district[key] = by_district.get(key, 0) + 1
    rows = [{"district": d, "new_parties": n} for d, n in sorted(by_district.items())]
    cols = ["district", "new_parties"]
    return {
        "title": "Customer Growth by District %s to %s" % (df, dt),
        "cols": cols,
        "labels": {"district": "District", "new_parties": "New Parties"},
        "rows": rows,
        "totals": {"district": "Total", "new_parties": len(partners)} if rows else None,
        "notes": [
            "District = Odoo state on the party (the governed BD geography seam is cd_entity_config.fix.bd.address)."
        ],
        "empty": "No new parties in this window.",
    }


def data_quality_scorecard(env, **_kw):
    """Quality composite by band — from scored records only; unscored parties
    are counted as a gap, never averaged in as zero."""
    Quality = env["fix.party.quality"]
    scored = Quality.search([])
    bands = {"90+": 0, "75-89": 0, "60-74": 0, "<60": 0}
    for q in scored:
        c = q.composite or 0
        key = "90+" if c >= 90 else "75-89" if c >= 75 else "60-74" if c >= 60 else "<60"
        bands[key] += 1
    governed = env["fix.party.role"].search([]).mapped("partner_id")
    rows = [{"band": b, "parties": n} for b, n in bands.items()]
    rows.append(
        {
            "band": "unscored",
            "parties": len(set(governed.ids) - set(scored.mapped("partner_id").ids)),
        }
    )
    return {
        "title": "Data Quality Scorecard",
        "cols": ["band", "parties"],
        "labels": {"band": "Composite Band", "parties": "Parties"},
        "rows": rows,
        "notes": [
            "Composite = 50% completeness + 30% validity + 20% recency (KPI-120). Recompute from the Quality Scores screen."
        ],
        "empty": "No scored parties yet — run Recompute.",
    }


def duplicate_merge_audit(env, **_kw):
    """Every merge with survivor, victim, executor and outcome."""
    merges = env["fix.party.merge"].search([], order="requested_at desc")
    rows = [
        {
            "requested": str(m.requested_at)[:16],
            "survivor": m.survivor_id.name,
            "victim": m.victim_id.name,
            "state": m.state,
            "executed_by": m.executed_by.name or "—",
            "reversible_until": str(m.reversible_until)[:16] if m.reversible_until else "—",
        }
        for m in merges
    ]
    cols = ["requested", "survivor", "victim", "state", "executed_by", "reversible_until"]
    return {
        "title": "Duplicate Merge Audit",
        "cols": cols,
        "labels": {
            "requested": "Requested",
            "survivor": "Survivor",
            "victim": "Victim",
            "state": "State",
            "executed_by": "Executed By",
            "reversible_until": "Reversible Until",
        },
        "rows": rows,
        "notes": ["Automated merge is prohibited (BRU-CPM-04): every row is a steward action."],
        "empty": "No merges recorded.",
    }


def consent_coverage(env, **_kw):
    """Consent state by purpose and channel — the CDO's weekly view.
    Selection keys render as labels (audit D10)."""
    consents = env["fix.consent"].search([])
    purpose_lbl = dict(
        env["fix.consent"].fields_get(["purpose"], attributes=["selection"])["purpose"]["selection"]
    )
    channel_lbl = dict(
        env["fix.consent"].fields_get(["channel"], attributes=["selection"])["channel"]["selection"]
    )
    agg = {}
    for c in consents:
        key = (c.purpose or "—", c.channel or "—")
        bucket = agg.setdefault(key, {"granted": 0, "withdrawn": 0, "superseded": 0, "expired": 0})
        bucket[c.state] = bucket.get(c.state, 0) + 1
    rows = [
        {
            "purpose": purpose_lbl.get(k[0], k[0]),
            "channel": channel_lbl.get(k[1], k[1]),
            "granted": v["granted"],
            "withdrawn": v["withdrawn"],
            "superseded": v["superseded"],
            "expired": v["expired"],
        }
        for k, v in sorted(agg.items())
    ]
    cols = ["purpose", "channel", "granted", "withdrawn", "superseded", "expired"]
    return {
        "title": "Consent Coverage Report",
        "cols": cols,
        "labels": {c: c.replace("_", " ").title() for c in cols},
        "rows": rows,
        "notes": [
            "granted = currently valid; superseded = the grant a withdrawal replaced "
            "(append-only chain, T-09).",
        ],
        "empty": "No consent records.",
    }


def credit_exposure_by_segment(env, **_kw):
    """Credit profiles summed per segment membership (billing's exposure)."""
    Membership = env["fix.segment.membership"]
    profiles = env["fix.credit.profile"].search([])
    by_customer = {p.customer_id.id: p for p in profiles}
    agg = {}
    for m in Membership.search([("exited_at", "=", False)]):
        profile = by_customer.get(m.partner_id.id)
        if profile:
            key = m.segment_id.name or m.segment_id.code
            row = agg.setdefault(key, {"members": 0, "limit": 0.0, "exposure": 0.0, "holds": 0})
            row["members"] += 1
            row["limit"] += profile.credit_limit or 0.0
            row["exposure"] += profile.exposure or 0.0
            if profile.credit_hold:
                row["holds"] += 1
    rows = [
        {
            "segment": s,
            "members": v["members"],
            "credit_limit": round(v["limit"], 2),
            "exposure": round(v["exposure"], 2),
            "holds": v["holds"],
        }
        for s, v in sorted(agg.items())
    ]
    cols = ["segment", "members", "credit_limit", "exposure", "holds"]
    return {
        "title": "Credit Exposure by Segment",
        "cols": cols,
        "labels": {
            "segment": "Segment",
            "members": "Members",
            "credit_limit": "Credit Limit (BDT)",
            "exposure": "Open Exposure (BDT)",
            "holds": "On Hold",
        },
        "rows": rows,
        "notes": [
            "Model of record: cd_billing_engine fix.credit.profile (M20); enforcement at order time is M20."
        ],
        "empty": "No credit profiles in any segment.",
    }


def corporate_hierarchy_map(env, **_kw):
    """Hierarchy edges with relation types — the account structure map.
    Relation keys render as labels; party ids ride along so same-NAMED
    parties stay distinguishable (the seed pool cycles ~10 Bengali names
    across 15k partners — name collisions are expected, ids disambiguate:
    audit D15, from the user's 'corporate hierarchy map' PDF)."""
    edges = env["fix.party.hierarchy"].search([], order="relation_type, parent_id")
    rel_lbl = dict(
        env["fix.party.hierarchy"].fields_get(["relation_type"], attributes=["selection"])[
            "relation_type"
        ]["selection"]
    )
    rows = [
        {
            "parent": "%s #%s" % (e.parent_id.name, e.parent_id.id),
            "child": "%s #%s" % (e.child_id.name, e.child_id.id),
            "relation": rel_lbl.get(e.relation_type, e.relation_type),
            "since": str(e.date_from or ""),
            "until": str(e.date_to or "") or "current",
        }
        for e in edges
    ]
    cols = ["parent", "child", "relation", "since", "until"]
    return {
        "title": "Corporate Hierarchy Map",
        "cols": cols,
        "labels": {
            "parent": "Parent",
            "child": "Child",
            "relation": "Relation",
            "since": "Since",
            "until": "Until",
        },
        "rows": rows,
        "notes": [
            "Group → company → site structures (FR-CPM-008); closed relations keep their until-date, never deleted."
        ],
        "empty": "No hierarchy relations recorded.",
    }


REPORTS = {
    "party_360": party_360,
    "customer_growth_by_district": customer_growth,
    "data_quality_scorecard": data_quality_scorecard,
    "duplicate_merge_audit": duplicate_merge_audit,
    "consent_coverage": consent_coverage,
    "credit_exposure_by_segment": credit_exposure_by_segment,
    "corporate_hierarchy_map": corporate_hierarchy_map,
}


# ---------------------------------------------------------------- KPIs
def kpis(env):
    """The registry's six M33 tiles — live reads, never literals."""
    out = {}

    def safe(key, fn):
        try:
            out[key] = fn()
        except Exception:  # unreadable for this user -> honest placeholder
            _logger.debug("M33 KPI %s unavailable", key, exc_info=True)
            out[key] = None

    Partner = env["res.partner"]
    companies = [("company_id", "in", env.companies.ids)]

    safe(
        "active_customers",
        lambda: Partner.search_count(
            [
                ("party_status", "=", "active"),
                "|",
                ("customer_rank", ">", 0),
                ("role_ids.role_type", "=", "customer"),
            ]
        ),
    )
    total_parties = Partner.search_count(
        ["|", ("customer_rank", ">", 0), ("role_ids", "!=", False)]
    )
    open_dups = env["fix.party.duplicate"].search_count(
        [("state", "in", ("new", "reviewed", "confirmed"))]
    )
    safe("duplicate_rate", lambda: _r(100.0 * open_dups / total_parties) if total_parties else 0.0)
    governed = env["fix.party.role"].search([]).mapped("partner_id")
    scored = env["fix.party.quality"].search([]).mapped("partner_id")
    safe(
        "golden_coverage",
        lambda: _r(100.0 * len(set(governed.ids) & set(scored.ids)) / len(governed.ids))
        if governed
        else 0.0,
    )
    safe(
        "consent_current",
        lambda: _r(
            100.0 * Partner.search_count([("consent_ids.state", "=", "granted")]) / total_parties
        )
        if total_parties
        else 0.0,
    )
    safe(
        "credit_holds",
        lambda: env["fix.credit.profile"].search_count([("credit_hold", "=", True), *companies]),
    )
    today = datetime.date.today()
    safe(
        "new_today",
        lambda: Partner.search_count(
            [
                "|",
                ("customer_rank", ">", 0),
                ("role_ids", "!=", False),
                ("create_date", ">=", fields.Datetime.to_datetime(today)),
            ]
        ),
    )
    return out
