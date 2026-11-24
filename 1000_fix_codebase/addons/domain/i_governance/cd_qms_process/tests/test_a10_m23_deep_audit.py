# A10 deep audit (2026-11-22) — M23 fixes landed from the five-auditor sweep:
#
# A1-F01/F02/A5-F06  the Quality Gates register is enforced: a gate names its
#                    checkpoint, fix.service.order._check_qc_gate consults the
#                    active blocking gates (M01's own hard baseline stays), and
#                    fix.qc.checklist consumes its fix.qms.checklist template —
#                    items, acceptance criteria, evidence demands and the
#                    reportable flag reach the bench.
# A1-F05             a failed completion raises its NCR through the takeover
#                    method (MAJOR, checklist-linked, once).
# A1-F03             the certification surveillance clock (90/30-day windows
#                    and a lapse tell the Quality Managers once per band).
# A1-F04             the management review input set covers the full ISO
#                    9001:2015 9.3.2 a-f, clause letters corrected.
#
# The odoo_env fixture rolls everything back.
# ruff: noqa: F811  (fixtures are imported and used as parameters)
from datetime import date, timedelta

import pytest
from odoo import Command
from odoo.addons.cd_contact_centre.tests.test_a02_p1p2_cd_contact_centre import (  # noqa: F401
    so,
)
from odoo.exceptions import UserError

QM_GROUP = "cd_qms_process.group_qms_quality_manager"


def _to_qc(env, order):
    est = env["fix.estimate"].create(
        {
            "order_id": order.id,
            "line_ids": [
                Command.create(
                    {"line_type": "labour", "description": "fix", "quantity": 1, "unit_price": 900}
                )
            ],
        }
    )
    est.action_send()
    est.action_approve()
    order.action_start_repair()
    order.action_submit_qc()


def _template(env, name="DA Bench Template", reportable=False):
    template = env["fix.qms.checklist"].create(
        {
            "name": name,
            "item_ids": [
                Command.create(
                    {
                        "name": "Torque the hinge to spec",
                        "response_type": "pass_fail",
                        "acceptance_criteria": "4.5 Nm ±0.2",
                        "evidence_required": "measurement",
                        "reportable": reportable,
                    }
                ),
                Command.create(
                    {
                        "name": "Firmware version current",
                        "response_type": "pass_fail",
                        "acceptance_criteria": ">= 2.4.1",
                        "evidence_required": "none",
                    }
                ),
            ],
        }
    )
    template.action_publish()
    return template


def _gate(env, template, checkpoint="qc_pass"):
    return env["fix.qms.gate"].create(
        {
            "name": "DA Gate %s" % checkpoint,
            "code": "DA-QG-%s" % checkpoint[-4:],
            "stage": "Before customer handover",
            "checkpoint": checkpoint,
            "mandatory_checklist_id": template.id,
            "blocking": True,
            "state": "active",
        }
    )


# ---------------------------------------- A1-F02: templates reach the bench
def test_the_execution_checklist_consumes_its_template(odoo_env, so):
    env = odoo_env
    template = _template(env)
    _gate(env, template)
    _to_qc(env, so)
    checklist = env["fix.qc.checklist"].create({"order_id": so.id})
    assert checklist.template_id == template
    items = checklist.item_ids.sorted("sequence")
    assert len(items) == 2
    first = items[0]
    assert first.acceptance_criteria == "4.5 Nm ±0.2"
    assert first.evidence_required == "measurement"
    assert first.template_item_id


# ----------------------------------- A1-F01: the gate register finally bites
def test_the_gate_blocks_ready_without_its_template_passed(odoo_env, so):
    env = odoo_env
    template = _template(env, name="DA Gate Template")
    _gate(env, template)
    _to_qc(env, so)
    # the gate's template checklist, created but never completed (FIRST, so
    # the stage-based one below is the newest M01's baseline reads)…
    env["fix.qc.checklist"].create({"order_id": so.id})
    template_based = env["fix.qc.checklist"].search(
        [("order_id", "=", so.id), ("template_id", "=", template.id)]
    )
    assert len(template_based) == 1 and template_based.state == "pending"
    # …and a stage-based checklist that passes (M01's own baseline is
    # satisfied by the NEWEST checklist)
    stage_based = env["fix.qc.checklist"].create(
        {
            "order_id": so.id,
            "visual_inspection_passed": True,
            "functional_test_passed": True,
            "safety_electrical_passed": True,
            "cleaning_sanitization_passed": True,
        }
    )
    # M01's hard gate is satisfied by the completed stage-based checklist —
    # the REGISTER now refuses with its own named reason
    stage_based.action_complete()
    with pytest.raises(UserError, match="DA Gate qc_pass.*DA Gate Template"):
        so.action_ready()
    # complete the template checklist and the same order goes Ready
    template_based.item_ids.write({"passed": True})
    template_based.action_complete()
    so.action_ready()
    assert so.state == "ready"


# ----------------------------------- A1-F05: the failed completion raises its NCR
def test_a_failed_completion_raises_its_major_ncr(odoo_env, so):
    env = odoo_env
    _to_qc(env, so)
    checklist = env["fix.qc.checklist"].create(
        {
            "order_id": so.id,
            "visual_inspection_passed": True,
            "functional_test_passed": False,
            "safety_electrical_passed": True,
            "cleaning_sanitization_passed": True,
        }
    )
    checklist.action_complete()
    checklist.invalidate_recordset()
    assert checklist.state == "failed"
    assert checklist.ncr_id and checklist.ncr_id.severity == "major"
    assert checklist.ncr_id.source == "qc"
    # the raise is once: completing is refused on a done checklist, and the
    # idempotence guard inside action_fail_with_ncr keeps the same NCR
    with pytest.raises(UserError, match="already failed"):
        checklist.action_complete()
    assert env["fix.ncr"].search_count([("order_id", "=", so.id), ("source", "=", "qc")]) == 1


# --------------------------------------------- A1-F03: the certification clock
def test_the_certification_surveillance_clock_notifies_once_per_band(odoo_env):
    env = odoo_env
    today = date.today()
    cert = env["fix.qms.certification"].create(
        {
            "name": "DA ISO 9001 surveillance",
            "standard": "ISO 9001:2015",
            "audit_type": "surveillance",
            "audit_date": today - timedelta(days=340),
            "valid_until": today + timedelta(days=25),  # inside the 30-day band
            "result": "passed",
        }
    )
    env["fix.qms.certification"].cron_certification_surveillance()
    cert.invalidate_recordset()
    assert cert.surveillance_band_notified == "30"
    told = len(cert.message_ids.filtered(lambda m: "30-day surveillance window" in (m.body or "")))
    assert told == 1
    # the second run is silent; the band only moves when the window does
    env["fix.qms.certification"].cron_certification_surveillance()
    cert.invalidate_recordset()
    assert cert.surveillance_band_notified == "30"
    told_again = len(
        cert.message_ids.filtered(lambda m: "30-day surveillance window" in (m.body or ""))
    )
    assert told_again == 1
    # a lapsed certificate graduates to the overdue band — told again
    cert._guarded().write({"valid_until": today - timedelta(days=1)})
    env["fix.qms.certification"].cron_certification_surveillance()
    cert.invalidate_recordset()
    assert cert.surveillance_band_notified == "overdue"
    assert len(cert.message_ids.filtered(lambda m: "has LAPSED" in (m.body or ""))) == 1
    # the validity window is frozen after creation (A1-F08)
    with pytest.raises(UserError), env.cr.savepoint():
        cert.with_user(env.ref("base.user_admin")).write(
            {"valid_until": today + timedelta(days=3650)}
        )


# --------------------------------- A1-F04: the full 9.3.2 input set pulls
def test_the_review_input_set_covers_the_full_932_clauses(odoo_env):
    env = odoo_env
    from odoo.addons.cd_qms_process.models.fix_qms_ops import REVIEW_INPUT_KINDS

    kinds = {kind for kind, _label in REVIEW_INPUT_KINDS}
    assert kinds == {
        "prior_actions",
        "issues_changes",
        "customer_feedback",
        "objectives_attainment",
        "process_performance",
        "nonconformities",
        "monitoring_results",
        "audit_results",
        "external_providers",
        "resources_adequacy",
        "risk_effectiveness",
        "improvement_opportunities",
    }
    # every label cites a clause that actually exists in ISO 9001:2015 9.3.2
    for _kind, label in REVIEW_INPUT_KINDS:
        assert "(9.3.2" in label
        assert "(9.3.2 g)" not in label and "(9.3.2 h)" not in label
    chair = env["hr.employee"].create({"name": "A10 DA Review Chair"})
    review = env["fix.qms.review"].create(
        {
            "name": "DA management review",
            "review_date": date.today(),
            "chairperson_id": chair.id,
        }
    )
    review.action_pull_inputs()
    pulled = set(review.input_ids.mapped("kind"))
    assert pulled == kinds  # all twelve pull from the live system
    review.invalidate_recordset()
    assert review.inputs_missing == 0
