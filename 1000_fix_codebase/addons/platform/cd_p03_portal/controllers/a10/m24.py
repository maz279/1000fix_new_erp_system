# A10 · M24 Documents & E-Signature — surfaces, packs and KPIs over the
# governed document repository, templates, e-signature envelopes and retention
# classes (cd_document_core + cd_esignature).
import datetime

SURFACES = {
    "fix.document": {
        "order": "create_date desc, id desc",
        "limit": 500,
        "actions": {
            # A10 D2/P1-1: the lifecycle moves through actions, never typed
            "action_legal_hold",
            "action_release_hold",
            "action_assert_can_destroy",
            "action_dispose",
            "action_sync_to_mayan",
            "action_submit_review",
            "action_publish",
            "action_new_revision",
        },
    },
    "fix.document.template": {
        "order": "code, version desc",
        "limit": 200,
        # capture pass 2: a version is approved by a Document Controller who did
        # not write it, and changed only by a new version (FR-DMS-021)
        "actions": {"action_approve", "action_new_version", "action_retire"},
    },
    "fix.retention.class": {"order": "name", "limit": 100, "actions": set()},
    "fix.legal.hold": {"order": "id desc", "limit": 200, "actions": {"action_release"}},
    "fix.disposal.record": {"order": "id desc", "limit": 200, "actions": set()},
    "fix.esignature.envelope": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_send", "action_check_complete", "action_void", "action_verify"},
    },
    "fix.esignature.signer": {
        "order": "envelope_id, sequence",
        "limit": 500,
        "actions": {"action_sign", "action_decline"},
    },
    # ---- capture pass 2 (2026-11-19): the spec records that had no model ----
    "fix.document.class": {
        "order": "code",
        "limit": 300,
        "actions": {"action_activate", "action_retire"},
        "pickers": {"retention_class_id": [("active", "=", True)]},
    },
    "fix.document.exception": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_resolve"},
        "pickers": {"doc_class_id": [("state", "=", "active")]},
    },
    "fix.physical.record": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_record_destruction"},
        "pickers": {"document_id": [("state", "!=", "destroyed")]},
    },
    "fix.document.integrity.check": {"order": "id desc", "limit": 100, "actions": set()},
    "fix.document.integrity.divergence": {"order": "id", "limit": 300, "actions": set()},
    "fix.document.distribution": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_distribute"},
        "pickers": {
            "document_id": [
                ("is_controlled", "=", True),
                ("control_state", "=", "published"),
                ("is_current", "=", True),
            ],
            "recipient_ids": [("share", "=", False)],
        },
    },
    "fix.document.acknowledgement": {
        "order": "id desc",
        "limit": 400,
        "actions": {"action_acknowledge"},
    },
    "fix.disposal.batch": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_refresh",
            "action_submit",
            "action_approve",
            "action_reject",
            "action_execute",
        },
    },
    "fix.retention.violation": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_investigate", "action_close"},
    },
    "fix.legal.hold.order": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_apply", "action_release"},
    },
    "fix.evidence.pack": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_collect", "action_assemble", "action_verify"},
        "pickers": {"document_ids": [("state", "!=", "destroyed")]},
    },
    "fix.external.release": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_request", "action_grant", "action_revoke"},
        "pickers": {
            "pack_id": [("state", "=", "sealed")],
            "document_ids": [("state", "!=", "destroyed"), ("isolation_tier", "!=", "T5")],
        },
    },
    "fix.document.access.log": {"order": "id desc", "limit": 500, "actions": set()},
    "fix.esignature.wet.signature": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
        "pickers": {
            "envelope_id": [("state", "in", ("sent", "partially_signed"))],
            "signer_id": [
                ("signed_at", "=", False),
                ("envelope_id.state", "in", ("sent", "partially_signed")),
            ],
        },
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


def retention_compliance(env, date_from=None, date_to=None, **params):
    """Retention compliance: documents by retention class and expiry state."""
    docs = env["fix.document"].search([])
    today = datetime.date.today()
    groups = {}
    for doc in docs:
        key = doc.retention_class_id.name if doc.retention_class_id else "Unclassified"
        g = groups.setdefault(key, {"docs": 0, "expired": 0, "on_hold": 0, "upcoming": 0})
        g["docs"] += 1
        if doc.legal_hold:
            g["on_hold"] += 1
        elif doc.retention_expires and doc.retention_expires < today:
            g["expired"] += 1
        elif doc.retention_expires and (doc.retention_expires - today).days <= 90:
            g["upcoming"] += 1
    rows = [{"class": k, **v} for k, v in sorted(groups.items())]
    return _pack(
        "Retention Compliance",
        ["class", "docs", "expired", "upcoming", "on_hold"],
        {
            "class": "Retention Class",
            "docs": "Documents",
            "expired": "Expired (not held)",
            "upcoming": "Expiring in 90d",
            "on_hold": "Legal Hold",
        },
        rows,
        [
            "A document under legal hold is never counted as expired for disposal: the hold is "
            "the override the model enforces."
        ],
        totals={
            "class": "Total",
            "docs": sum(r["docs"] for r in rows),
            "expired": sum(r["expired"] for r in rows),
            "upcoming": sum(r["upcoming"] for r in rows),
            "on_hold": sum(r["on_hold"] for r in rows),
        },
        empty="No documents in the repository.",
    )


def signature_status(env, date_from=None, date_to=None, **params):
    """Signature status: envelopes and their signer progress."""
    envelopes = env["fix.esignature.envelope"].search([])
    rows = []
    for envl in envelopes:
        signers = envl.signer_ids
        # A10 M24-12 (k01): the old row counted a signer 'state' field that
        # does not exist, so 'signed' was always 0. The signature is signed_at.
        signed = len(signers.filtered("signed_at"))
        rows.append(
            {
                "envelope": envl.name,
                "document": envl.document_id.name if envl.document_id else "—",
                "signers": len(signers),
                "signed": signed,
                "state": dict(envl._fields["state"].selection).get(envl.state, envl.state),
                "completed": str(envl.completed_at or "—"),
            }
        )
    rows.sort(key=lambda r: r["envelope"], reverse=True)
    # only envelopes still awaiting signatures are pending — declined, voided
    # and expired ones are decided, not pending
    pending = len(envelopes.filtered(lambda e: e.state in ("sent", "partially_signed")))
    return _pack(
        "Signature Status — %d pending envelope(s)" % pending,
        ["envelope", "document", "signers", "signed", "state", "completed"],
        {
            "envelope": "Envelope",
            "document": "Document",
            "signers": "Signers",
            "signed": "Signed",
            "state": "State",
            "completed": "Completed At",
        },
        rows,
        [
            "Signed counts signers whose state is no longer pending; the envelope completes "
            "when every signer has signed."
        ],
        empty="No signature envelopes recorded.",
    )


def repository_growth(env, date_from=None, date_to=None, **params):
    """Repository growth by month and document type."""
    docs = env["fix.document"].search([])
    groups = {}
    for doc in docs:
        month = doc.create_date.strftime("%Y-%m") if doc.create_date else "Unknown"
        key = (
            month,
            dict(doc._fields["document_type"].selection).get(doc.document_type)
            if doc.document_type
            else "—",
        )
        groups[key] = groups.get(key, 0) + 1
    rows = [{"month": m, "type": t, "documents": c} for (m, t), c in sorted(groups.items())]
    return _pack(
        "Repository Growth",
        ["month", "type", "documents"],
        {"month": "Month", "type": "Document Type", "documents": "Documents"},
        rows,
        [
            "Counts by the document's creation month and type; linked attachments are not "
            "double-counted."
        ],
        totals={"month": "Total", "documents": sum(r["documents"] for r in rows)},
        empty="No documents in the repository.",
    )


def access_audit(env, date_from=None, date_to=None, **params):
    """Access audit export: documents with their integrity and hold signals."""
    docs = env["fix.document"].search([])
    rows = []
    for doc in docs:
        rows.append(
            {
                "document": doc.name[:70],
                "type": dict(doc._fields["document_type"].selection).get(doc.document_type)
                if doc.document_type
                else "—",
                "linked_model": doc.res_model or "—",
                "isolation": dict(doc._fields["isolation_tier"].selection).get(doc.isolation_tier)
                if doc.isolation_tier
                else "—",
                "retention_expires": str(doc.retention_expires or "—"),
                "legal_hold": "Yes" if doc.legal_hold else "No",
                "active": "Yes" if doc.active else "No",
            }
        )
    rows.sort(key=lambda r: r["document"])
    return _pack(
        "Access Audit Export",
        [
            "document",
            "type",
            "linked_model",
            "isolation",
            "retention_expires",
            "legal_hold",
            "active",
        ],
        {
            "document": "Document",
            "type": "Type",
            "linked_model": "Linked Model",
            "isolation": "Isolation Tier",
            "retention_expires": "Retention Expires",
            "legal_hold": "Legal Hold",
            "active": "Active",
        },
        rows,
        ["An evidence export of the repository's governance signals for a given point in time."],
        empty="No documents in the repository.",
    )


REPORTS = {
    "retention_compliance": retention_compliance,
    "signature_status": signature_status,
    "repository_growth": repository_growth,
    "access_audit": access_audit,
}


def kpis(env):
    docs = env["fix.document"].search([])
    envelopes = env["fix.esignature.envelope"].search([])
    # A10 M24-12: an envelope is pending only while signatures may still land
    pending = len(envelopes.filtered(lambda e: e.state in ("sent", "partially_signed")))
    held = len(docs.filtered(lambda d: d.legal_hold))
    auto_filed = len(docs.filtered(lambda d: d.retention_class_id))
    return {
        "documents": len(docs),
        "auto_filed": auto_filed,
        "search_p95": None,
        "pending_esignatures": pending,
        "legal_holds": held,
        # capture pass 2: this KPI counted completed signature envelopes; it is
        # the evidence packs sealed within the five-minute target (KPI-C24-04)
        "evidence_packs_5min": env["fix.evidence.pack"].search_count(
            [("state", "=", "sealed"), ("assembly_seconds", "<=", 300)]
        ),
    }
