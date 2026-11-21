"""A05 workflow audit, M18 e-waste & ESG controls (cd_ewaste + the P03 surface).

Each control the A05 probes (working/A05_evidence/probes/m18/probe_m18.py)
found open is attacked as a NON-ADMIN user three ways where it applies: the
wrong transition, a plain write(), and /p03/model/write. The legitimate path
is proved too. Outcomes are asserted, never source text.
"""

from datetime import timedelta

import pytest
from odoo.addons.cd_ewaste.tests.m18_fixtures import (
    M18,
    attachment,
    events,
    make_user,
    refused,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task


@pytest.fixture
def m(odoo_env):
    x = M18(odoo_env)
    try:
        yield x
    finally:
        x.close()


# =================================================== E3 / M18-1: collection
def test_collection_state_forgery_refused_three_ways(m):
    col = m.collection()
    assert refused(m.env, lambda: col.write({"state": "certified"}))
    res = m.p03_write(m.clerk, "fix.ewaste.collection", col.id, {"state": "recycled"})
    assert res.get("error")
    assert refused(m.env, lambda: m.collection(state="recycled"))
    # the wrong transition: certificate from 'collected'
    assert refused(m.env, lambda: col.action_issue_certificate())
    assert col.state == "collected"


def test_collection_evidence_and_figure_fields_guarded(m):
    col = m.collection()
    for vals in (
        {"disposal_certificate_ref": "DISPOSE/FAKE"},
        {"esg_co2_saved_kg": 9000.0},
        {"triage_grade": "reuse"},
        {"wipe_required": False},
        {"batch_id": m.env["fix.ewaste.batch"].create({}).id},
    ):
        assert refused(m.env, lambda v=vals: col.write(v)), vals
        assert m.p03_write(m.clerk, "fix.ewaste.collection", col.id, vals).get("error"), vals
    assert not col.disposal_certificate_ref and not col.esg_co2_saved_kg


def test_wipe_gate_runs_on_every_path(m):
    dev = m.device()
    col = m.collection(device_id=dev.id)
    m.triage(col, "recycle", data_bearing=True)
    col.with_user(m.dispatcher).action_secure_destruction()
    assert col.wipe_certificate_id.sanitization_status == "pending_verification"
    assert refused(m.env, lambda: col.with_user(m.dispatcher).action_recycle())
    # trusted code too: the gate is in the state change, not in the action
    assert refused(m.env, lambda: col.sudo()._guarded().write({"state": "recycled"}))
    # the legitimate path: the verifier verifies the operator's evidence
    cert = col.wipe_certificate_id
    cert.sudo().write(
        {
            "wipe_log_attachment_id": m.env["ir.attachment"]
            .create({"name": "log", "raw": b"shred ok"})
            .id
        }
    )
    cert.with_user(m.verifier).action_verify()
    col.with_user(m.dispatcher).action_recycle()
    assert col.state == "recycled"


# ============================================== E4 / M18-2: one cert one item
def test_one_wipe_certificate_releases_one_item(m):
    dev = m.device()
    cert = m.verified_cert(dev.serial_number)
    a = m.collection(device_id=dev.id)
    m.triage(a, "recycle")
    a.write({"wipe_certificate_id": cert.id})
    a.with_user(m.dispatcher).action_secure_destruction()
    a.with_user(m.dispatcher).action_recycle()
    b = m.collection(device_id=m.device().id)
    m.triage(b, "recycle")
    assert refused(m.env, lambda: b.write({"wipe_certificate_id": cert.id}))
    res = m.p03_write(
        m.clerk,
        "fix.ewaste.collection",
        b.id,
        {"device_id": dev.id, "wipe_certificate_id": cert.id},
    )
    assert res.get("error")
    # the device a certificate is bound to is frozen after triage
    assert refused(m.env, lambda: b.write({"device_id": dev.id}))
    assert b.wipe_certificate_id != cert


# ==================================================== E2 / M18-5: ESG figures
def test_esg_metrics_have_no_entry_path(m):
    Metric = m.env["fix.esg.metric"]
    assert refused(
        m.env,
        lambda: Metric.with_user(m.clerk).create(
            {
                "name": "CO2 forged",
                "metric_type": "co2_saved",
                "period": "2026-11",
                "value": 1_000_000.0,
            }
        ),
    )
    res = m.p03_write(
        m.clerk,
        "fix.esg.metric",
        None,
        {
            "name": "forged",
            "metric_type": "ewaste_collected",
            "period": "2026-11",
            "value": 50_000.0,
        },
    )
    assert res.get("error")
    period = m.today.strftime("%Y-%m")
    m.collection(weight_kg=0.4)
    m.collection(weight_kg=0.6)
    rows = Metric.with_user(m.clerk).compute_period(period)
    collected = rows.filtered(lambda r: r.metric_type == "ewaste_collected")
    company = m.env.company
    expected = sum(
        m.env["fix.ewaste.collection"]
        .search(
            [
                ("company_id", "=", company.id),
                ("collected_on", ">=", m.today.replace(day=1)),
                ("collected_on", "<=", m.today),
            ]
        )
        .mapped("weight_kg")
    )
    assert collected.value == pytest.approx(round(expected, 3))
    assert collected.computed and collected.scope == "inventory"
    avoided = rows.filtered(lambda r: r.metric_type == "co2_saved")
    assert avoided.scope == "avoided" and avoided.factor_version
    # a computed figure cannot be re-typed
    assert refused(m.env, lambda: collected.with_user(m.clerk).write({"value": 9.0}))
    assert m.p03_write(m.clerk, "fix.esg.metric", collected.id, {"value": 9.0}).get("error")


def test_co2_is_computed_and_frozen_with_the_weight(m):
    col = m.ready_item(weight=0.5)
    assert col.esg_co2_saved_kg == pytest.approx(0.75)
    assert col.co2_factor_version
    assert refused(m.env, lambda: col.write({"weight_kg": 6000.0}))
    res = m.p03_write(
        m.clerk, "fix.ewaste.collection", col.id, {"weight_kg": 0.9, "esg_co2_saved_kg": 9000.0}
    )
    assert res.get("error")
    assert col.weight_kg == 0.5 and col.esg_co2_saved_kg == pytest.approx(0.75)
    other = m.collection(device_id=m.device().id)
    m.triage(other, "recycle")
    other.write({"wipe_certificate_id": m.verified_cert(other.device_id.serial_number).id})
    other.with_user(m.dispatcher).action_secure_destruction()
    assert refused(m.env, lambda: other.with_user(m.dispatcher).action_recycle(9000.0))


def test_weight_is_bounded_per_item(m):
    assert refused(m.env, lambda: m.collection(weight_kg=1000.0, material_type="phone"))
    ok = m.collection(weight_kg=5.0, material_type="phone", item_count=10)
    assert ok.weight_kg == 5.0
    assert m.p03_write(m.clerk, "fix.ewaste.collection", ok.id, {"weight_kg": 900.0}).get("error")


# ================================================ E2 / M18-6: the DoE return
def _return(m, period=None, **vals):
    return (
        m.env["fix.ewaste.return"]
        .with_user(m.compliance)
        .create(
            {
                "period": period or m.today.strftime("%Y-%m"),
                "due_date": m.today + timedelta(days=20),
                **vals,
            }
        )
    )


def test_mass_balance_reports_the_real_tonnage(m):
    item = m.ready_item(weight=0.5)
    batch = m.processed_batch([item])
    ret = _return(m)
    ret.action_calculate_mass_balance()
    received = sum(
        m.env["fix.ewaste.collection"]
        .search(
            [
                ("company_id", "=", ret.company_id.id),
                ("collected_on", ">=", m.today.replace(day=1)),
                ("collected_on", "<=", m.today),
            ]
        )
        .mapped("weight_kg")
    )
    assert ret.total_tonnage_collected == pytest.approx(round(received / 1000.0, 3))
    assert ret.total_tonnage_collected > 0
    processed = sum(
        m.env["fix.ewaste.batch"]
        .search(
            [
                ("company_id", "=", ret.company_id.id),
                ("state", "=", "processed"),
                ("processed_on", ">=", m.today.replace(day=1)),
            ]
        )
        .mapped("processed_weight_kg")
    )
    assert batch.processed_weight_kg == pytest.approx(0.5)
    assert ret.total_tonnage_recycled == pytest.approx(round(processed / 1000.0, 3))
    # the figures are never typed
    assert refused(m.env, lambda: ret.write({"total_tonnage_collected": 10.0}))
    assert m.p03_write(
        m.compliance, "fix.ewaste.return", ret.id, {"total_tonnage_recycled": 9.5}
    ).get("error")


def test_zero_and_duplicate_returns_refused(m):
    m.registration()
    ret = _return(m, period="1999-01")
    assert refused(m.env, lambda: ret.action_submit_return())
    assert ret.state == "draft"
    assert refused(m.env, lambda: _return(m, period="1999-01"))
    ret.write({"nil_return_reason": "Branch closed all month."})
    ret.action_submit_return()
    assert ret.state == "submitted" and ret.submitted_by_id == m.compliance
    assert refused(m.env, lambda: _return(m, period="not-a-period"))


def test_return_cannot_be_self_accepted_and_is_frozen(m):
    m.registration()
    m.collection(weight_kg=0.5)
    ret = _return(m)
    # the clerk cannot prepare, submit or accept
    assert refused(m.env, lambda: ret.with_user(m.clerk).action_submit_return())
    assert refused(m.env, lambda: ret.with_user(m.clerk).action_accept_return())
    # accept from draft: the wrong transition
    cfo2 = make_user(m.env, "cfo2", ["cd_ewaste.group_ewaste_finance_approver"])
    assert refused(m.env, lambda: ret.with_user(cfo2).action_accept_return())
    ret.action_submit_return()
    assert ret.total_tonnage_collected > 0
    # the submitter holding the CFO role still cannot accept their own return
    m.compliance.write(
        {"group_ids": [(4, m.env.ref("cd_ewaste.group_ewaste_finance_approver").id)]}
    )
    ret.write({"authority_ack_ref": "DOE-ACK-1"})
    assert refused(m.env, lambda: ret.action_accept_return())
    assert refused(m.env, lambda: ret.with_user(m.clerk).write({"state": "accepted"}))
    ret.with_user(cfo2).action_accept_return()
    assert ret.state == "accepted" and ret.accepted_by_id == cfo2
    for vals in ({"period": "2020-01"}, {"authority_ack_ref": "X"}, {"due_date": "2020-01-01"}):
        assert refused(m.env, lambda v=vals: ret.with_user(m.compliance).write(v)), vals
        assert m.p03_write(m.compliance, "fix.ewaste.return", ret.id, vals).get("error"), vals


# ============================================== E2 / M18-11: company scoping
def test_kpis_and_reports_stay_in_the_users_company(m):
    from odoo.addons.cd_p03_portal.controllers.a05 import m18 as surf

    env = m.env
    m.collection(weight_kg=0.5)
    cenv = env(user=m.clerk.id)
    before_k = surf.kpis(cenv)
    before = {name: fn(cenv) for name, fn in surf.REPORTS.items()}
    co_b = env["res.company"].create({"name": "M18 Other Co"})
    other = env["fix.ewaste.collection"].create(
        {
            "customer_id": m.customer.id,
            "company_id": co_b.id,
            "weight_kg": 150.0,
            "material_type": "other",
        }
    )
    env["fix.ewaste.return"].create(
        {"company_id": co_b.id, "period": "2026-01", "due_date": m.today}
    )
    m.env["fix.esg.metric"].compute_period(m.today.strftime("%Y-%m"), co_b)
    user_b = make_user(env, "clerk_b", company=co_b)
    assert other.with_user(user_b).weight_kg == 150.0
    # the clerk's figures do not move by a single kilogram
    assert surf.kpis(cenv) == before_k
    for name, fn in surf.REPORTS.items():
        assert fn(cenv) == before[name], name
    # and the other company's user sees exactly its own 150 kg
    kb = surf.kpis(env(user=user_b.id))
    assert kb["total_intake_kg"] == pytest.approx(150.0)
    assert surf.collection_volume(env(user=user_b.id))["totals"]["weight_kg"] == 150.0


# ============================================== E4 / E5 / M18-3: the recycler
def test_recycler_registration_needs_another_persons_approval(m):
    Partner = m.env["fix.ewaste.partner"].with_user(m.clerk)
    assert refused(
        m.env,
        lambda: Partner.create(
            {"name": "Backyard Smelter", "certificate_no": "DOE/TYPED/1", "state": "active"}
        ),
    )
    p = m.partner()
    assert p.state == "draft"
    assert m.p03_write(m.clerk, "fix.ewaste.partner", p.id, {"state": "active"}).get("error")
    # a direct press is refused: it is approved from the approver's inbox
    assert refused(m.env, lambda: p.with_user(m.approver).action_approve_partner())
    # the registrant never decides, even holding the role
    m.dispatcher.write(
        {"group_ids": [(4, m.env.ref("cd_ewaste.group_ewaste_recycler_approver").id)]}
    )
    p.action_request_approval()
    assert not inbox_task(p, m.dispatcher)
    approve_via_inbox(p, m.approver, requester=m.dispatcher)
    assert p.state == "active" and p.approved_by_id == m.approver
    # the licence is frozen once approved
    assert refused(m.env, lambda: p.write({"valid_to": m.today + timedelta(days=5000)}))
    assert m.p03_write(m.clerk, "fix.ewaste.partner", p.id, {"certificate_no": "OTHER"}).get(
        "error"
    )
    # segregation of duties: the approver does not dispatch to it
    m.approver.write({"group_ids": [(4, m.env.ref("cd_ewaste.group_ewaste_dispatcher").id)]})
    b = m.batch(partner=p)
    m.ready_item()
    b.action_load_ready_items()
    assert refused(m.env, lambda: b.with_user(m.approver).action_dispatch())


def test_dispatch_rechecks_the_licence_on_every_path(m):
    p = m.approved_partner()
    m.ready_item()
    b = m.batch(partner=p)
    b.action_load_ready_items()
    m.weigh_out(b)  # A05 S3 M18-16: weighed out, so only the licence can refuse
    # suspended
    p.with_user(m.approver).action_suspend()
    assert refused(m.env, lambda: b.action_dispatch())
    # lapsed after approval (time passing), and no cron has run yet
    p2 = m.approved_partner()
    m.env.flush_all()
    m.env.cr.execute(
        "UPDATE fix_ewaste_partner SET valid_to=%s WHERE id=%s",
        (m.today - timedelta(days=30), p2.id),
    )
    m.env.invalidate_all()
    b.write({"partner_id": p2.id})
    assert refused(m.env, lambda: b.action_dispatch())
    # the direct write and trusted code go through the same gate
    assert refused(m.env, lambda: b.write({"state": "dispatched"}))
    assert refused(m.env, lambda: b.sudo()._guarded().write({"state": "dispatched"}))
    assert m.p03_write(m.dispatcher, "fix.ewaste.batch", b.id, {"state": "dispatched"}).get("error")
    # an unapproved (draft) recycler
    b.write({"partner_id": m.partner().id})
    assert refused(m.env, lambda: b.action_dispatch())
    # the recycler panel switch (report §7.6): an ISO-only recycler is off-panel
    iso = m.approved_partner(certification="iso_14001")
    b.write({"partner_id": iso.id})
    assert refused(m.env, lambda: b.action_dispatch())
    assert b.state == "draft"
    m.env["ir.config_parameter"].sudo().set_param(
        "cd_ewaste.recycler_required_certifications", "doe,iso_14001"
    )
    b.action_dispatch()
    assert b.state == "dispatched" and b.manifest_id


def test_licence_expiry_cron(m):
    p = m.approved_partner()
    m.env.flush_all()
    m.env.cr.execute(
        "UPDATE fix_ewaste_partner SET valid_to=%s WHERE id=%s", (m.today - timedelta(days=1), p.id)
    )
    m.env.invalidate_all()
    soon = m.approved_partner(valid_to=m.today + timedelta(days=10))
    m.env["fix.ewaste.partner"].cron_licence_expiry()
    assert p.state == "expired"
    assert soon.state == "active" and soon.expiry_warned_on == m.today
    m.env["fix.ewaste.partner"].cron_licence_expiry()  # safe to re-run
    assert p.state == "expired"


# ================================================ M18-7: batch forgery
def test_batch_dispatch_and_processing_cannot_be_forged(m):
    Batch = m.env["fix.ewaste.batch"]
    assert refused(m.env, lambda: Batch.with_user(m.clerk).create({"material_type": "phone"}))
    assert refused(
        m.env,
        lambda: Batch.with_user(m.dispatcher).create(
            {"material_type": "phone", "weight_kg": 9999.0}
        ),
    )
    b = m.batch()
    assert refused(m.env, lambda: b.write({"state": "processed"}))
    assert m.p03_write(
        m.dispatcher, "fix.ewaste.batch", b.id, {"state": "processed", "weight_kg": 9999.0}
    ).get("error")
    # no items, no dispatch
    assert refused(m.env, lambda: b.action_dispatch())
    item = m.ready_item(weight=0.5)
    b.action_load_ready_items()
    assert item.batch_id == b and b.weight_kg == pytest.approx(0.5)
    m.weigh_out(b)  # A05 S3 M18-16
    b.action_dispatch()
    # receive and process have their own steps and evidence
    assert refused(m.env, lambda: b.action_process())
    b.write({"received_weight_kg": 9999.0, "recycler_receipt_ref": "R-9"})
    assert refused(m.env, lambda: b.action_receive())  # outside the weighbridge tolerance
    b.write({"received_weight_kg": 0.49})
    b.action_receive()
    assert refused(m.env, lambda: b.action_process())  # no recycler evidence
    assert refused(m.env, lambda: b.write({"received_weight_kg": 9999.0}))  # frozen now
    b.write({"processing_evidence_id": attachment(m.env).id})
    b.action_process()
    assert b.state == "processed" and b.processed_weight_kg == pytest.approx(0.49)


# ========================================= M18-4 / M18-10: disposal certificate
def test_certificate_lifecycle_issue_freeze_revoke(m):
    Cert = m.env["fix.ewaste.certificate"]
    item = m.ready_item(weight=0.5)
    partner = m.approved_partner()
    assert refused(
        m.env,
        lambda: Cert.with_user(m.clerk).create(
            {"collection_id": item.id, "partner_id": partner.id, "state": "issued"}
        ),
    )
    assert m.p03_write(
        m.clerk,
        "fix.ewaste.certificate",
        None,
        {
            "collection_id": item.id,
            "partner_id": partner.id,
            "certificate_no": "FORGED",
            "state": "issued",
        },
    ).get("error")
    batch = m.processed_batch([item], partner=partner)
    batch.action_record_certificate()
    cert = batch.certificate_ids
    assert cert.state == "draft" and cert.partner_id == partner
    cert.with_user(m.dispatcher).write(
        {
            "certificate_no": "REC-1",
            "evidence_attachment_id": attachment(m.env).id,
            "recycler_stated_weight_kg": 50.0,
        }
    )
    assert refused(m.env, lambda: cert.with_user(m.clerk).action_issue())
    assert refused(m.env, lambda: cert.with_user(m.compliance).action_issue())  # 50 kg != 0.5
    cert.with_user(m.dispatcher).write({"recycler_stated_weight_kg": 0.5})
    cert.with_user(m.compliance).action_issue()
    assert cert.state == "issued" and item in cert.collection_ids
    assert item.state == "certified" and item.disposal_certificate_id == cert
    assert events(m.env, "ewaste.certificate_issued", item.id) == 1
    # frozen once issued
    for vals in ({"weight_kg": 900.0}, {"certificate_no": "EDITED"}, {"issued_on": "2025-01-01"}):
        assert refused(m.env, lambda v=vals: cert.with_user(m.compliance).write(v)), vals
        assert m.p03_write(m.compliance, "fix.ewaste.certificate", cert.id, vals).get("error")
    # revoke, never re-issue
    assert refused(m.env, lambda: cert.with_user(m.compliance).action_revoke())  # no reason
    cert.with_user(m.compliance).write({"revoke_reason": "Recycler failed audit"})
    cert.with_user(m.compliance).action_revoke()
    assert cert.state == "revoked" and item.state == "recycled"
    assert refused(m.env, lambda: cert.with_user(m.compliance).write({"state": "issued"}))
    assert refused(m.env, lambda: cert.sudo().write({"state": "issued"}))
    assert m.p03_write(m.compliance, "fix.ewaste.certificate", cert.id, {"state": "issued"}).get(
        "error"
    )


def test_collection_certify_button_uses_the_batch_certificate(m):
    item = m.ready_item(weight=0.5)
    batch = m.processed_batch([item])
    assert refused(m.env, lambda: item.action_issue_certificate())  # none recorded yet
    batch.action_record_certificate()
    batch.certificate_ids.with_user(m.dispatcher).write(
        {
            "certificate_no": "REC-2",
            "evidence_attachment_id": attachment(m.env).id,
            "recycler_stated_weight_kg": 0.5,
        }
    )
    res = m.p03_action(m.compliance, "fix.ewaste.collection", [item.id], "action_issue_certificate")
    assert res.get("success"), res
    assert item.state == "certified"


# ===================================================== E8 / M18-8: batteries
def _hazmat_point(m, classes=("li_sound", "li_damaged"), ceiling=50.0):
    """A05 S3 M18-12: hazmat is accepted only at a point with a ceiling for
    its class, activated by an HSE officer who did not register it."""
    p = (
        m.env["fix.ewaste.collection.point"]
        .with_user(m.clerk)
        .create(
            {
                "name": "Hazmat Store %s" % m.today,
                "kind": "hazmat_store",
                "capacity_kg": 1000.0,
                "responsible_id": m.env["hr.employee"].create({"name": "Store Lead"}).id,
                "limit_ids": [(0, 0, {"hazard_class": k, "max_kg": ceiling}) for k in classes],
            }
        )
    )
    p.with_user(m.hse).action_activate()
    return p


def _hazmat_item(m, point, weight=0.3, **vals):
    col = m.collection(
        material_type="battery", weight_kg=weight, collection_point_id=point.id, **vals
    )
    m.triage(col, "hazardous")
    return col


def test_battery_inspection_is_recorded_by_an_hse_inspector(m):
    point = _hazmat_point(m)
    col = _hazmat_item(m, point, condition="swollen")
    bat = col.battery_ids.with_user(m.clerk)
    assert bat.swollen_cell and bat.collection_point_id == point
    assert refused(m.env, lambda: bat.action_inspect_and_quarantine())
    assert not bat.terminal_taped
    assert refused(m.env, lambda: bat.write({"terminal_taped": True}))
    assert m.p03_write(m.clerk, "fix.ewaste.battery", bat.id, {"terminal_taped": True}).get("error")
    hse_bat = bat.with_user(m.hse)
    assert refused(m.env, lambda: hse_bat.action_inspect_and_quarantine())  # no evidence
    hse_bat.write({"inspection_evidence_id": attachment(m.env, "photo.jpg").id})
    hse_bat.action_inspect_and_quarantine()
    assert bat.terminal_taped and bat.inspected_by_id == m.hse
    assert bat.quarantine_barrel_ref and bat.storage_location == point.name
    # what was inspected is frozen
    assert refused(m.env, lambda: hse_bat.write({"swollen_cell": False}))
    # state jumps
    assert refused(m.env, lambda: bat.with_user(m.dispatcher).action_process())
    assert refused(m.env, lambda: bat.action_dispatch())  # no batch
    assert refused(m.env, lambda: bat.write({"state": "dispatched"}))
    assert bat.state == "stored"


def test_battery_stream_dispatch_process_and_hazmat_disposal(m):
    point = _hazmat_point(m)
    col = _hazmat_item(m, point, weight=0.4)
    assert col.state == "hazmat" and len(col.battery_ids) == 1
    assert refused(m.env, lambda: col.with_user(m.dispatcher).action_secure_destruction())
    bat = col.battery_ids
    bat.with_user(m.hse).write({"inspection_evidence_id": attachment(m.env, "photo.jpg").id})
    bat.with_user(m.hse).action_inspect_and_quarantine()
    swollen = _hazmat_item(m, point, weight=0.2, condition="swollen").battery_ids
    swollen.with_user(m.hse).write({"inspection_evidence_id": attachment(m.env, "p2.jpg").id})
    swollen.with_user(m.hse).action_inspect_and_quarantine()
    b = m.batch(material="battery")
    b.action_load_ready_items()
    assert bat in b.battery_ids
    # swollen and sound cells are never shipped together (BRU-ESG-08)
    if len(set(b.battery_ids.mapped("swollen_cell"))) > 1:
        m.weigh_out(b)
        assert refused(m.env, lambda: b.action_dispatch())
        swollen.sudo()._guarded().write({"batch_id": False})
    m.weigh_out(b)
    b.action_dispatch()
    assert bat.state == "dispatched" and b.manifest_id.hazardous
    b.write({"received_weight_kg": b.weight_kg, "recycler_receipt_ref": "R-B"})
    b.action_receive()
    b.write({"processing_evidence_id": attachment(m.env).id})
    b.action_process()
    # A05 S3 M18-07: processed is not disposed - the certificate disposes it
    assert bat.state == "processed" and col.state == "hazmat"
    m.issued_certificate(b)
    assert col.state == "disposed"


def test_battery_location_ceiling(m):
    point = _hazmat_point(m, ceiling=1.0)
    first = _hazmat_item(m, point, weight=0.8)
    assert first.battery_ids.collection_point_id == point
    over = _hazmat_item(m, point, weight=0.5)
    # over the class ceiling: not accepted there (and HSE alerted)
    assert not over.battery_ids.collection_point_id
    assert refused(
        m.env,
        lambda: over.battery_ids.with_user(m.hse).write({"collection_point_id": point.id}),
    )


# ===================================================== P2: triage by assessor
def test_triage_is_an_assessors_write_once_decision(m):
    col = m.collection()
    Triage = m.env["fix.ewaste.triage"]
    assert refused(
        m.env,
        lambda: Triage.with_user(m.clerk).create({"collection_id": col.id, "decision": "reuse"}),
    )
    assert refused(m.env, lambda: col.action_triage_recycle())  # the clerk's button
    other = m.env["hr.employee"].create({"name": "Someone Else"})
    assert refused(
        m.env,
        lambda: Triage.with_user(m.assessor).create(
            {"collection_id": col.id, "decision": "recycle", "inspector_id": other.id}
        ),
    )
    assert refused(
        m.env,
        lambda: Triage.with_user(m.assessor).create(
            {"collection_id": col.id, "decision": "recycle", "decided_on": "2025-01-01"}
        ),
    )
    t = m.triage(col, "recycle", data_bearing=True)
    assert t.inspector_id.user_id == m.assessor and t.decided_by_id == m.assessor
    assert col.state == "triaged" and col.data_bearing and col.wipe_required
    assert events(m.env, "ewaste.triaged", col.id) == 1
    for vals in ({"decision": "reuse"}, {"data_bearing": False}, {"decided_on": "2025-01-01"}):
        assert refused(m.env, lambda v=vals: t.with_user(m.assessor).write(v)), vals
        assert m.p03_write(m.assessor, "fix.ewaste.triage", t.id, vals).get("error"), vals
    # a second decision on the same item is refused
    assert refused(m.env, lambda: m.triage(col, "reuse"))


def test_reuse_item_routes_to_m14_not_the_shredder(m):
    col = m.collection(device_id=m.device().id)
    res = m.p03_action(m.assessor, "fix.ewaste.collection", [col.id], "action_triage_reuse")
    assert res.get("success"), res
    assert col.state == "routed" and col.triage_grade == "reuse"
    assert events(m.env, "ewaste.reuse_routed", col.id) == 1
    assert refused(m.env, lambda: col.with_user(m.dispatcher).action_secure_destruction())
    assert refused(m.env, lambda: col.sudo().write({"state": "destruction"}))


# ===================================================== E12: crons
def test_storage_clock_cron(m):
    col = m.collection(weight_kg=0.5)
    m.env.flush_all()
    m.env.cr.execute(
        "UPDATE fix_ewaste_collection SET collected_on=%s WHERE id=%s",
        (m.today - timedelta(days=200), col.id),
    )
    m.env.invalidate_all()
    col._compute_storage_deadline()
    assert col.storage_deadline < m.today
    m.env["fix.ewaste.collection"].cron_storage_clock()
    assert col.storage_overdue
    assert m.p03_write(m.clerk, "fix.ewaste.collection", col.id, {"storage_overdue": False}).get(
        "error"
    )
    # the DoE extension: +90 days, recorded by compliance with its reference
    assert refused(m.env, lambda: col.action_apply_storage_extension())
    col.write({"storage_extension_ref": "DOE-EXT-7"})
    col.with_user(m.compliance).action_apply_storage_extension()
    assert col.storage_extended and not col.storage_overdue
    assert col.storage_deadline >= m.today
    assert refused(m.env, lambda: col.with_user(m.compliance).action_apply_storage_extension())


def test_return_due_cron(m):
    late = _return(m, period="2025", due_date=m.today - timedelta(days=3))
    due = _return(m, period="2026", due_date=m.today + timedelta(days=5))
    m.env["fix.ewaste.return"].cron_return_due()
    assert late.is_overdue and late.reminder_sent_on == m.today
    assert due.reminder_sent_on == m.today
    m.env["fix.ewaste.return"].cron_return_due()  # safe to re-run


# ================================================ P2: Basel PIC, registration
def test_cross_border_transfer_needs_a_basel_consent(m):
    p = m.approved_partner()
    m.ready_item()
    b = m.batch(partner=p)
    b.action_load_ready_items()
    india = m.env.ref("base.in")
    b.write({"destination_country_id": india.id})
    assert refused(m.env, lambda: b.action_dispatch())
    Pic = m.env["fix.ewaste.basel.pic"]
    assert refused(
        m.env,
        lambda: Pic.with_user(m.clerk).create(
            {"partner_id": p.id, "destination_country_id": india.id}
        ),
    )
    pic = Pic.with_user(m.compliance).create(
        {
            "partner_id": p.id,
            "destination_country_id": india.id,
            "consent_ref": "PIC-1",
            "importing_authority": "CPCB",
            "valid_to": m.today + timedelta(days=90),
            "evidence_attachment_id": attachment(m.env).id,
        }
    )
    assert refused(m.env, lambda: pic.with_user(m.compliance).action_record_consent())  # own
    assert refused(m.env, lambda: pic.with_user(m.compliance).write({"state": "consented"}))
    pic.with_user(m.compliance2).action_record_consent()
    assert pic.state == "consented"
    assert refused(m.env, lambda: pic.with_user(m.compliance).write({"max_weight_kg": 1e6}))
    b.write({"basel_pic_id": pic.id})
    m.weigh_out(b)
    b.action_dispatch()
    assert b.state == "dispatched" and b.manifest_id.basel_pic_id == pic


def test_doe_return_is_filed_under_an_active_registration(m):
    m.collection(weight_kg=0.5)
    ret = _return(m)
    assert refused(m.env, lambda: ret.action_submit_return())
    Reg = m.env["fix.ewaste.registration"]
    assert refused(m.env, lambda: Reg.with_user(m.clerk).create({"registration_no": "X"}))
    reg = Reg.with_user(m.compliance).create(
        {
            "registration_no": "DOE-1",
            "valid_to": m.today + timedelta(days=100),
            "evidence_attachment_id": attachment(m.env).id,
        }
    )
    assert refused(m.env, lambda: reg.with_user(m.compliance).action_activate())  # own record
    reg.with_user(m.compliance2).action_activate()
    assert refused(m.env, lambda: reg.with_user(m.compliance).write({"registration_no": "Y"}))
    ret.action_submit_return()
    assert ret.registration_id == reg


# ================================================ E10 / P2: money with approval
def test_incentive_and_recycler_money_are_routed_approvals(m):
    # A05 S3: raised by the e-waste floor (M18-22), on the collection's OU,
    # with its branch and payment terms (I2)
    Settlement = m.env["fix.ewaste.settlement"].with_user(m.dispatcher)
    ou = m.env["operating.unit"].search([("company_id", "=", m.env.company.id)], limit=1)
    entity = m.env["fix.entity"].search([("company_id", "=", m.env.company.id)], limit=1) or m.env[
        "fix.entity"
    ].create({"code": "M18CTL", "legal_name": "M18 Entity", "company_id": m.env.company.id})
    branch = m.env["fix.branch"].create(
        {"name": "M18 Branch", "code": "M18BR", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    terms = {"branch_id": branch.id, "payment_method": "cash"}
    col = m.collection(weight_kg=0.5, operating_unit_id=ou.id)
    inc = Settlement.create(
        {
            "kind": "incentive",
            "collection_id": col.id,
            "partner_id": m.customer.id,
            "amount": 200.0,
            **terms,
        }
    )
    assert refused(
        m.env,
        lambda: Settlement.create(
            {
                "kind": "incentive",
                "collection_id": col.id,
                "partner_id": m.clerk.partner_id.id,
                "amount": 200.0,
                **terms,
            }
        ),
    )  # the payee is the collection's customer
    assert refused(m.env, lambda: inc.with_user(m.cfo).action_approve_settlement())  # direct
    assert refused(m.env, lambda: inc.write({"state": "approved"}))
    # no incentive before the item is assessed (BRU-ESG-13)
    inc.action_request_approval()
    task = inbox_task(inc, m.cfo)
    assert task
    assert refused(m.env, lambda: task.with_user(m.cfo).action_approve())
    m.triage(col, "recycle")
    approve_via_inbox(inc, m.cfo, requester=m.dispatcher)
    assert inc.state == "approved" and inc.approved_by_id == m.cfo
    assert events(m.env, "ewaste.settlement_approved", inc.id) == 1
    assert refused(m.env, lambda: inc.write({"amount": 9000.0}))
    assert m.p03_write(m.dispatcher, "fix.ewaste.settlement", inc.id, {"amount": 9000.0}).get(
        "error"
    )
    # a recycler fee waits for the recycler's receipt
    batch = m.dispatched_batch()
    batch.sudo()._guarded().write({"operating_unit_id": ou.id})
    fee = Settlement.create(
        {
            "kind": "recycler_fee",
            "batch_id": batch.id,
            "partner_id": batch.partner_id.partner_id.id,
            "amount": 1500.0,
            **terms,
        }
    )
    fee.action_request_approval()
    assert refused(m.env, lambda: inbox_task(fee, m.cfo).with_user(m.cfo).action_approve())


# ================================================ wiring: the P03 buttons
def test_battery_and_return_buttons_are_whitelisted(m):
    from odoo.addons.cd_p03_portal.controllers.a05 import SURFACES

    for model, methods in {
        "fix.ewaste.battery": {
            "action_inspect_and_quarantine",
            "action_dispatch",
            "action_process",
        },
        "fix.ewaste.return": {
            "action_calculate_mass_balance",
            "action_submit_return",
            "action_accept_return",
        },
        "fix.ewaste.partner": {"action_request_approval", "action_recall_approval"},
        "fix.ewaste.settlement": {"action_request_approval", "action_recall_approval"},
    }.items():
        assert methods <= SURFACES[model]["actions"], model
    ret = _return(m)
    res = m.p03_action(m.compliance, "fix.ewaste.return", [ret.id], "action_calculate_mass_balance")
    assert res.get("success"), res
    res = m.p03_action(m.clerk, "fix.ewaste.return", [ret.id], "action_submit_return")
    assert not res.get("success") and "Compliance Officer" in res.get("error", "")
