# Behavioural tests for the M07 rebuild surfaces (2026-10-27): stage gating
# (BRU-CRM-03), loss reasons (BRU-CRM-05), forecast immutability (BRU-CRM-06),
# renewal no-delete (BRU-CRM-12), owner coverage (BRU-CRM-08), QBR actions.
# Same `odoo_env` convention as cd_party_master — rolled back after every test.
import json

import pytest
from odoo.exceptions import ValidationError


def _partner(env, name="Corp Client Ltd"):
    return env["res.partner"].create({"name": name, "customer_rank": 1})


def _pipeline(env, stages=None):
    return env["fix.pipeline"].create(
        {
            "code": "MSP-TEST",
            "name": "Managed Services",
            "revenue_stream": "msp",
            "stages_json": json.dumps(
                stages
                or [
                    {"stage": "Discovery", "criteria": None, "requires_confirmation": False},
                    {
                        "stage": "Proposal",
                        "criteria": "quotation requested from M36",
                        "requires_confirmation": True,
                        "probability": 40,
                    },
                ]
            ),
        }
    )


def _stage(env, name="Proposal", team=None):
    existing = env["crm.stage"].search([("name", "=", name)], limit=1)
    if existing:
        return existing
    return env["crm.stage"].create({"name": name, "sequence": 5})


# --- stage gating (BRU-CRM-03) -------------------------------------------------


def test_gated_stage_requires_confirmation_and_consumes_it(odoo_env):
    pipeline = _pipeline(odoo_env)
    stage = _stage(odoo_env, "Proposal")
    lead = odoo_env["crm.lead"].create(
        {"name": "MSP pursuit", "type": "opportunity", "pipeline_id": pipeline.id}
    )
    with pytest.raises(ValidationError, match="BRU-CRM-03"):
        lead.write({"stage_id": stage.id})
    # confirming in the same write as the move is the intended path
    lead.write({"stage_id": stage.id, "criteria_confirmed": True})
    assert lead.stage_id == stage
    assert not lead.criteria_confirmed  # consumed by the move


def test_ungated_stage_moves_freely(odoo_env):
    pipeline = _pipeline(odoo_env)
    stage = _stage(odoo_env, "Discovery")
    lead = odoo_env["crm.lead"].create(
        {"name": "Early pursuit", "type": "opportunity", "pipeline_id": pipeline.id}
    )
    lead.write({"stage_id": stage.id})
    assert lead.stage_id == stage


# --- structured loss reasons (BRU-CRM-05) ---------------------------------------


def test_losing_an_opportunity_requires_a_reason_code(odoo_env):
    """FLAW-07.2 / REQ-07.3: a lost deal must record the winning competitor
    AND the structured loss reason before the loss write is accepted."""
    lead = odoo_env["crm.lead"].create(
        {"name": "Deal", "type": "opportunity", "probability": 60, "expected_revenue": 100000}
    )
    with pytest.raises(ValidationError, match="Loss analysis mandatory"):
        lead.write({"probability": 0})
    # reason alone is not enough — the winning competitor is also mandatory
    with pytest.raises(ValidationError, match="Loss analysis mandatory"):
        lead.write({"probability": 0, "lost_reason_code": "PRICE"})
    lead.write({"probability": 0, "lost_reason_code": "PRICE", "competitor": "RivalFix"})
    assert lead.lost_reason_code == "PRICE"
    assert lead.competitor == "RivalFix"


# --- forecast snapshots (BRU-CRM-06/07) ------------------------------------------


def test_snapshot_is_immutable_and_adjustment_is_attributable(odoo_env):
    env = odoo_env
    pipeline = _pipeline(env)
    Snapshot = env["fix.forecast.snapshot"]
    snap = Snapshot.create(
        {
            "period": "2026-10",
            "owner_id": env.user.id,
            "pipeline_id": pipeline.id,
            "commit_value": 50000,
            "best_case_value": 80000,
            "pipeline_value": 120000,
        }
    )
    with pytest.raises(ValidationError, match="BRU-CRM-06"):
        snap.write({"commit_value": 99999})
    # the single legitimate later write: the attributable adjustment
    snap.write({"manager_adjustment": -5000, "adjustment_reason": "Q4 caution"})
    assert snap.commit_value == 50000
    assert snap.manager_adjustment == -5000
    assert snap.adjusted_by.id == env.user.id


# --- renewal pipeline (BRU-CRM-12, FR-CRM-043) -----------------------------------


def test_auto_created_renewal_cannot_be_deleted_but_can_be_closed(odoo_env):
    env = odoo_env
    import datetime

    renewal = env["fix.renewal"].create(
        {
            "source_type": "contract",
            "partner_id": _partner(env).id,
            "value": 150000,
            "expiry_date": datetime.date.today() + datetime.timedelta(days=60),
            "auto_created": True,
        }
    )
    with pytest.raises(ValidationError, match="BRU-CRM-12"):
        renewal.unlink()
    renewal.action_win()
    assert renewal.state == "renewed"


def test_lapse_opens_a_winback_opportunity(odoo_env):
    env = odoo_env
    _pipeline(env)  # ensure pipeline config exists
    winback = env["fix.pipeline"].search([("revenue_stream", "=", "winback")], limit=1)
    if not winback:
        winback = env["fix.pipeline"].create(
            {"code": "WINBACK", "name": "Win-Back", "revenue_stream": "winback"}
        )
    import datetime

    renewal = env["fix.renewal"].create(
        {
            "source_type": "membership",
            "partner_id": _partner(env).id,
            "expiry_date": datetime.date.today(),
        }
    )
    renewal.action_lapse()
    assert renewal.state == "lapsed"
    opp = env["crm.lead"].search(
        [("name", "=", "Win-back: Corp Client Ltd"), ("type", "=", "opportunity")]
    )
    assert len(opp) == 1


# --- account coverage (BRU-CRM-08) ------------------------------------------------


def test_unowned_accounts_get_an_owner(odoo_env):
    env = odoo_env
    _partner(env, "Orphan Account")
    closed = env["fix.account.assignment"].action_assign_unowned()
    assert closed >= 1
    orphans = env["res.partner"].search(
        [("name", "=", "Orphan Account"), ("customer_rank", ">", 0)]
    )
    owner = env["fix.account.assignment"].search(
        [("partner_id", "=", orphans.id), ("effective_to", "=", False)]
    )
    assert owner and owner.owner_id


# --- QBR flow (FR-CRM-036/037) -----------------------------------------------------


def test_qbr_lifecycle_and_action_tracking(odoo_env):
    env = odoo_env
    import datetime

    qbr = env["fix.qbr"].create(
        {
            "partner_id": _partner(env).id,
            "period": "2026-Q4",
            "scheduled_for": datetime.date.today(),
        }
    )
    action = env["fix.qbr.action"].create(
        {
            "qbr_id": qbr.id,
            "description": "Deliver SLA report pack",
            "due_date": datetime.date.today(),
        }
    )
    assert qbr.open_action_count == 1
    action.action_close()
    qbr.invalidate_recordset()
    assert qbr.open_action_count == 0
    # FLAW-07.3 / REQ-07.4: holding a QBR demands attendees, minutes and the
    # presentation pack reference — each gap is refused with a named field.
    with pytest.raises(ValidationError, match="attendees"):
        qbr.action_mark_held()
    qbr.write({"attendees": "CTO, Head of IT"})
    with pytest.raises(ValidationError, match="minutes"):
        qbr.action_mark_held()
    qbr.write({"decisions": "Renewal committed; SLA pack reviewed"})
    with pytest.raises(ValidationError, match="presentation pack"):
        qbr.action_mark_held()
    qbr.action_mark_data_ready(document_ref="sharepoint://qbr/2026-Q4-pack")
    qbr.action_mark_held()
    assert qbr.state == "held" and qbr.held_on
