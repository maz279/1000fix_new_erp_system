"""M17 capture pass 2 (2026-11-19): the records the spec places on the
sub-module pages, driven through the workspace endpoints as NON-ADMIN users.

p1 asset label + further identifiers (FR-AST-002/008/010), p2 accessory
register + actual configuration (FR-AST-012/015, BRU-AST-08), p3 population
change (FR-AST-022, BRU-AST-10/11), p7 warranty derivation basis
(BRU-AST-16), p8 estate nodes + dated placements (FR-AST-038), p10
end-of-life decision (FR-AST-048, BRU-AST-19), p11 stewardship worklist
(FR-AST-051, BRU-AST-22).
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_device_registry.tests.test_a07_m17_operability import (
    ok,
    saved,
    ui,  # noqa: F401 - the fixture
)
from odoo.addons.cd_device_registry.tests.test_a07_p1_controls import (
    _user,
    c,  # noqa: F401 - the fixture
    dev,
    doc,
    refused,
)

# A07 ERP audit (2026-11-20) M17-17: a requested population change applies
# when an Operations Director (R05) who did not request it approves it.
POP_APPROVER = "cd_device_registry.group_device_population_approver"


def _err(out):
    return out.get("error") or ("" if out.get("success") else str(out))


@pytest.fixture
def tech(c):  # noqa: F811
    return c.env["hr.employee"].create({"name": "M17P2 Labelling Technician"})


@pytest.fixture
def client(c):  # noqa: F811
    corp = c.env["res.partner"].create({"name": "M17P2 Corp Ltd", "is_company": True})
    c.staff = c.env["res.partner"].create({"name": "M17P2 Staffer", "parent_id": corp.id})
    c.outsider = c.env["res.partner"].create({"name": "M17P2 Outsider"})
    return corp


# ===================================================================== p1
def test_a_label_issues_a_tag_that_finds_the_device_and_relabel_keeps_the_old(c, ui, tech):  # noqa: F811
    d = dev(c)
    first = c.env["fix.device.label"].browse(
        saved(
            ui.write(
                c.clerk,
                model="fix.device.label",
                values={"device_id": d.id, "label_type": "qr", "applied_by_id": tech.id},
            )
        )
    )
    assert first.name.startswith("FXT-") and first.state == "active"
    d.invalidate_recordset()
    assert d.asset_tag == first.name
    assert c.env["fix.device"].with_user(c.clerk).name_search(first.name)[0][0] == d.id
    # a second label without a reason is refused
    out = ui.write(
        c.clerk, model="fix.device.label", values={"device_id": d.id, "applied_by_id": tech.id}
    )
    assert "replaced" in _err(out)
    second = c.env["fix.device.label"].browse(
        saved(
            ui.write(
                c.clerk,
                model="fix.device.label",
                values={"device_id": d.id, "applied_by_id": tech.id, "replace_reason": "torn"},
            )
        )
    )
    first.invalidate_recordset()
    d.invalidate_recordset()
    assert first.state == "replaced" and second.replaces_label_id == first
    assert d.asset_tag == second.name
    tags = c.env["fix.device.identifier"].search(
        [("device_id", "=", d.id), ("identifier_type", "=", "asset_tag")]
    )
    assert set(tags.mapped("is_current")) == {True, False} and len(tags) == 2
    # a label is permanent; its state cannot be typed
    assert "error" in ui.write(
        c.clerk, model="fix.device.label", record_id=second.id, values={"label_type": "nfc"}
    )
    assert refused(c.env, lambda: second.with_user(c.clerk).write({"state": "replaced"}))
    assert refused(c.env, lambda: second.with_user(c.clerk).unlink())


def test_a_label_date_is_not_in_the_future(c, tech):  # noqa: F811
    d = dev(c)
    later = fields.Date.context_today(c.env["fix.device"]) + timedelta(days=3)
    assert refused(
        c.env,
        lambda: c.env["fix.device.label"]
        .with_user(c.clerk)
        .create({"device_id": d.id, "applied_by_id": tech.id, "applied_on": later}),
    )


def test_add_identifier_records_and_a_shared_value_raises_a_conflict(c, ui):  # noqa: F811
    a, b = dev(c), dev(c)
    kw = {"identifier_type": "brand_service_tag", "value": "st-123 45"}
    ok(
        ui.action(
            c.clerk, model="fix.device", ids=[a.id], method="action_add_identifier", kwargs=kw
        )
    )
    row = c.env["fix.device.identifier"].search(
        [("device_id", "=", a.id), ("identifier_type", "=", "brand_service_tag")]
    )
    assert row.value_normalised == "ST-12345" and row.captured_by_id == c.clerk
    # the same value twice on the same device is refused
    again = ui.action(
        c.clerk, model="fix.device", ids=[a.id], method="action_add_identifier", kwargs=kw
    )
    assert "already carries" in _err(again)
    # a serial is not added this way
    bad = ui.action(
        c.clerk,
        model="fix.device",
        ids=[a.id],
        method="action_add_identifier",
        kwargs={"identifier_type": "serial_number", "value": "X"},
    )
    assert "identifier type" in _err(bad)
    # the same value on another device: recorded, both on the worklist
    ok(
        ui.action(
            c.clerk,
            model="fix.device",
            ids=[b.id],
            method="action_add_identifier",
            kwargs={"identifier_type": "brand_service_tag", "value": " ST-12345"},
        )
    )
    issues = c.env["fix.device.quality.issue"].search([("issue_type", "=", "conflict")])
    assert {a, b} <= set(issues.device_id)


# ===================================================================== p2
def test_held_accessories_block_the_release_until_returned_or_missing(c, ui):  # noqa: F811
    d = dev(c)
    acc = [
        c.env["fix.device.accessory"].browse(
            saved(
                ui.write(
                    c.clerk,
                    model="fix.device.accessory",
                    values={"device_id": d.id, "accessory_type": t, "quantity": 1},
                )
            )
        )
        for t in ("charger", "bag")
    ]
    assert all(a.state == "held" and a.name.startswith("DACC/") for a in acc)
    grade = c.env["fix.device.condition"].with_user(c.clerk).create({"device_id": d.id})
    grade.with_user(c.clerk2).action_confirm()
    release = {
        "device_id": d.id,
        "event": "issued",
        "to_party_id": c.owner.id,
        "condition_id": grade.id,
        "evidence_document_id": doc(c, doc_type="custody_photo").id,
        "accessories_reconciled": True,
    }
    out = ui.write(c.clerk, model="fix.device.custody", values=dict(release))
    assert "BRU-AST-08" in _err(out) and acc[0].name in _err(out)
    ok(
        ui.action(
            c.clerk,
            model="fix.device.accessory",
            ids=[acc[0].id],
            method="action_return",
            kwargs={},
        )
    )
    # missing needs a reason (a blank one is no reason)
    blank = ui.action(
        c.clerk,
        model="fix.device.accessory",
        ids=[acc[1].id],
        method="action_report_missing",
        kwargs={"reason": "   "},
    )
    assert "Say what is missing" in _err(blank)
    ok(
        ui.action(
            c.clerk,
            model="fix.device.accessory",
            ids=[acc[1].id],
            method="action_report_missing",
            kwargs={"reason": "bag not found; customer told"},
        )
    )
    # what was received is not rewritten, and a returned one is not re-held
    assert "error" in ui.write(
        c.clerk, model="fix.device.accessory", record_id=acc[0].id, values={"quantity": 3}
    )
    assert refused(c.env, lambda: acc[0].with_user(c.clerk).write({"state": "held"}))
    release["evidence_document_id"] = doc(c, doc_type="custody_photo").id
    saved(ui.write(c.clerk, model="fix.device.custody", values=release))


def test_a_new_configuration_value_closes_the_previous_one(c, ui):  # noqa: F811
    d = dev(c)
    today = fields.Date.context_today(c.env["fix.device"])
    old = c.env["fix.device.configuration"].browse(
        saved(
            ui.write(
                c.clerk,
                model="fix.device.configuration",
                values={
                    "device_id": d.id,
                    "attribute": "memory",
                    "value": "8",
                    "unit": "GB",
                    "source": "intake",
                    "effective_from": str(today - timedelta(days=30)),
                },
            )
        )
    )
    new = c.env["fix.device.configuration"].browse(
        saved(
            ui.write(
                c.clerk,
                model="fix.device.configuration",
                values={
                    "device_id": d.id,
                    "attribute": "memory",
                    "value": "16",
                    "unit": "GB",
                    "source": "diagnostic",
                },
            )
        )
    )
    old.invalidate_recordset()
    assert not old.is_current and old.effective_to == new.effective_from and new.is_current
    # earlier than the current value: refused
    out = ui.write(
        c.clerk,
        model="fix.device.configuration",
        values={
            "device_id": d.id,
            "attribute": "memory",
            "value": "4",
            "source": "customer",
            "effective_from": str(today - timedelta(days=60)),
        },
    )
    assert "error" in out
    assert "error" in ui.write(
        c.clerk, model="fix.device.configuration", record_id=new.id, values={"value": "32"}
    )


# ===================================================================== p3
def test_population_changes_only_by_a_reason_coded_change(c, ui):  # noqa: F811
    d = dev(c)
    assert d.population == "customer_owned"
    assert refused(c.env, lambda: d.with_user(c.agent).write({"population": "rental_pool"}))
    vals = {"device_id": d.id, "to_population": "rental_pool", "reason_code": "rental_onboarding"}
    # the clerk lacks the Device Registry Agent role
    assert "error" in ui.write(c.clerk, model="fix.device.population.change", values=dict(vals))
    change = c.env["fix.device.population.change"].browse(
        saved(ui.write(c.agent, model="fix.device.population.change", values=dict(vals)))
    )
    assert change.state == "requested" and d.population == "customer_owned"
    director = _user(c.env, "m17p2_opsdir", c.ou, [POP_APPROVER])
    change.with_user(director).action_approve()
    d.invalidate_recordset()
    assert d.population == "rental_pool" and change.from_population == "customer_owned"
    assert change.recorded_by_id == c.agent
    # BRU-AST-11: back to customer-owned only with the ownership transfer
    back = {"device_id": d.id, "to_population": "customer_owned", "reason_code": "sale_to_customer"}
    assert "BRU-AST-11" in _err(
        ui.write(c.agent, model="fix.device.population.change", values=dict(back))
    )
    other = (
        c.env["fix.device.ownership"]
        .sudo()
        .create(
            {
                "device_id": dev(c).id,
                "to_partner_id": c.buyer.id,
                "transfer_type": "sale",
                "reason": "x",
            }
        )
    )
    assert "another device" in _err(
        ui.write(
            c.agent, model="fix.device.population.change", values=dict(back, ownership_id=other.id)
        )
    )
    own = (
        c.env["fix.device.ownership"]
        .sudo()
        .create(
            {
                "device_id": d.id,
                "to_partner_id": c.buyer.id,
                "transfer_type": "sale",
                "reason": "sold",
            }
        )
    )
    back_change = c.env["fix.device.population.change"].browse(
        saved(
            ui.write(
                c.agent,
                model="fix.device.population.change",
                values=dict(back, ownership_id=own.id),
            )
        )
    )
    back_change.with_user(director).action_approve()
    d.invalidate_recordset()
    assert d.population == "customer_owned"
    # the same value again, a forged origin, an edit: refused
    assert "already" in _err(
        ui.write(c.agent, model="fix.device.population.change", values=dict(back))
    )
    assert "error" in ui.write(
        c.agent, model="fix.device.population.change", record_id=change.id, values={"notes": "x"}
    )


# ===================================================================== p7
def test_a_defaulted_warranty_date_is_not_verified(c, ui):  # noqa: F811
    d = dev(c)
    today = fields.Date.context_today(c.env["fix.device"])
    w = c.env["fix.warranty"].browse(
        saved(
            ui.write(
                c.clerk,
                model="fix.warranty",
                values={
                    "device_id": d.id,
                    "warranty_type": "manufacturer",
                    "start_date": str(today - timedelta(days=10)),
                    "end_date": str(today + timedelta(days=355)),
                    "derivation_basis": "manufacture_default",
                    "proof_document_id": doc(c, doc_type="warranty_card").id,
                },
            )
        )
    )
    assert w.basis_flag and "defaulted" in (w.verification_blocker or "").lower()
    out = ui.action(
        c.clerk,
        model="fix.warranty",
        ids=[w.id],
        method="action_request_approval",
        kwargs={"justification": "card"},
    )
    assert "BRU-AST-16" in _err(out)
    w.with_user(c.clerk).write({"derivation_basis": "purchase_evidence"})
    ok(
        ui.action(
            c.clerk,
            model="fix.warranty",
            ids=[w.id],
            method="action_request_approval",
            kwargs={"justification": "card"},
        )
    )


# ===================================================================== p8
def test_estate_nodes_form_a_site_department_user_tree(c, ui, client):  # noqa: F811
    estate = c.env["fix.device.estate"].create({"name": "M17P2 Estate", "client_id": client.id})
    site = c.env["fix.device.estate.node"].browse(
        saved(
            ui.write(
                c.clerk,
                model="fix.device.estate.node",
                values={"estate_id": estate.id, "node_type": "site", "name": "Gulshan"},
            )
        )
    )
    dept = c.env["fix.device.estate.node"].browse(
        saved(
            ui.write(
                c.clerk,
                model="fix.device.estate.node",
                values={
                    "estate_id": estate.id,
                    "node_type": "department",
                    "name": "Finance",
                    "parent_id": site.id,
                },
            )
        )
    )
    assert dept.complete_name == "Gulshan / Finance"
    # a department needs a site; a user node needs the client's own employee
    assert "error" in ui.write(
        c.clerk,
        model="fix.device.estate.node",
        values={"estate_id": estate.id, "node_type": "department", "name": "X"},
    )
    assert "error" in ui.write(
        c.clerk,
        model="fix.device.estate.node",
        values={
            "estate_id": estate.id,
            "node_type": "user",
            "name": "Y",
            "parent_id": dept.id,
            "contact_id": c.outsider.id,
        },
    )
    no_contact = ui.write(
        c.clerk,
        model="fix.device.estate.node",
        values={"estate_id": estate.id, "node_type": "user", "name": "Z", "parent_id": dept.id},
    )
    assert "employee" in _err(no_contact)
    saved(
        ui.write(
            c.clerk,
            model="fix.device.estate.node",
            values={
                "estate_id": estate.id,
                "node_type": "user",
                "name": "Staffer",
                "parent_id": dept.id,
                "contact_id": c.staff.id,
            },
        )
    )


def test_a_placement_moves_the_device_and_keeps_the_dated_history(c, ui, client):  # noqa: F811
    estate = c.env["fix.device.estate"].create({"name": "M17P2 Estate B", "client_id": client.id})
    Node = c.env["fix.device.estate.node"]
    site = Node.create({"estate_id": estate.id, "node_type": "site", "name": "Motijheel"})
    dept = Node.create(
        {"estate_id": estate.id, "node_type": "department", "name": "IT", "parent_id": site.id}
    )
    d = dev(c, owner_id=client.id)
    stray = dev(c)  # someone else's
    today = fields.Date.context_today(c.env["fix.device"])
    base = {"estate_id": estate.id, "move_reason": "issued to IT"}
    # someone else's device, or no node in an organised estate: refused
    assert "belongs to" in _err(
        ui.write(
            c.clerk,
            model="fix.device.estate.placement",
            values=dict(base, device_id=stray.id, node_id=site.id),
        )
    )
    assert "nodes" in _err(
        ui.write(c.clerk, model="fix.device.estate.placement", values=dict(base, device_id=d.id))
    )
    first = c.env["fix.device.estate.placement"].browse(
        saved(
            ui.write(
                c.clerk,
                model="fix.device.estate.placement",
                values=dict(
                    base,
                    device_id=d.id,
                    node_id=site.id,
                    placed_from=str(today - timedelta(days=5)),
                ),
            )
        )
    )
    d.invalidate_recordset()
    assert d.estate_id == estate and d.estate_node_id == site
    second = c.env["fix.device.estate.placement"].browse(
        saved(
            ui.write(
                c.clerk,
                model="fix.device.estate.placement",
                values=dict(base, device_id=d.id, node_id=dept.id, move_reason="moved to IT"),
            )
        )
    )
    first.invalidate_recordset()
    d.invalidate_recordset()
    assert (
        not first.is_current and first.placed_to == second.placed_from and d.estate_node_id == dept
    )
    # the node is moved only by a placement
    assert refused(c.env, lambda: d.with_user(c.clerk).write({"estate_node_id": site.id}))
    # backdating before the current placement: refused
    assert "earlier" in _err(
        ui.write(
            c.clerk,
            model="fix.device.estate.placement",
            values=dict(
                base, device_id=d.id, node_id=site.id, placed_from=str(today - timedelta(days=9))
            ),
        )
    )
    # taking the device out of the estate on the asset closes the placement
    d.with_user(c.clerk).write({"estate_id": False})
    second.invalidate_recordset()
    d.invalidate_recordset()
    assert not second.is_current and not d.estate_node_id


def test_an_estate_set_on_the_asset_is_recorded_as_a_placement(c, client):  # noqa: F811
    estate = c.env["fix.device.estate"].create({"name": "M17P2 Estate C", "client_id": client.id})
    d = dev(c, user=c.clerk, owner_id=client.id, estate_id=estate.id)
    rows = c.env["fix.device.estate.placement"].search([("device_id", "=", d.id)])
    assert len(rows) == 1 and rows.is_current and rows.estate_id == estate


# ===================================================================== p10
def test_an_end_of_life_route_needs_the_instruction_and_another_approver(c, ui):  # noqa: F811
    d = dev(c)
    vals = {"device_id": d.id, "route": "dispose", "basis": "board beyond repair"}
    eol = c.env["fix.device.eol.decision"].browse(
        saved(ui.write(c.bm, model="fix.device.eol.decision", values=dict(vals)))
    )
    # customer-owned: the instruction is required, and must match the route
    assert "BRU-AST-19" in _err(
        ui.action(
            c.bm, model="fix.device.eol.decision", ids=[eol.id], method="action_request", kwargs={}
        )
    )
    eol.with_user(c.bm).write({"customer_instruction": "refurbish"})
    assert "does not allow" in _err(
        ui.action(
            c.bm, model="fix.device.eol.decision", ids=[eol.id], method="action_request", kwargs={}
        )
    )
    eol.with_user(c.bm).write({"customer_instruction": "recycle"})
    ok(
        ui.action(
            c.bm, model="fix.device.eol.decision", ids=[eol.id], method="action_request", kwargs={}
        )
    )
    # one open decision per device
    assert "open end-of-life" in _err(
        ui.write(c.bm, model="fix.device.eol.decision", values=dict(vals))
    )
    # the requester cannot approve; a clerk cannot; another Branch Manager can
    assert "Segregation" in _err(
        ui.action(
            c.bm, model="fix.device.eol.decision", ids=[eol.id], method="action_approve", kwargs={}
        )
    )
    assert not ui.action(
        c.clerk, model="fix.device.eol.decision", ids=[eol.id], method="action_approve", kwargs={}
    )["success"]
    assert refused(c.env, lambda: eol.with_user(c.bm2).write({"state": "approved"}))
    ok(
        ui.action(
            c.bm2, model="fix.device.eol.decision", ids=[eol.id], method="action_approve", kwargs={}
        )
    )
    d.invalidate_recordset()
    assert d.lifecycle_stage == "obsolete" and d.population == "ewaste_pending"
    assert d.eol_customer_instruction == "recycle" and d.lifecycle_decided_by_id == c.bm2
    assert c.env["fix.device.population.change"].search(
        [("device_id", "=", d.id), ("reason_code", "=", "eol_decision")]
    )
    assert "error" in ui.write(
        c.bm, model="fix.device.eol.decision", record_id=eol.id, values={"basis": "changed"}
    )


# ===================================================================== p11
def test_the_stewardship_worklist_is_worked_by_assignee_or_branch_manager(c, ui):  # noqa: F811
    d = dev(c)
    issue = c.env["fix.device.quality.issue"].browse(
        saved(
            ui.write(
                c.clerk,
                model="fix.device.quality.issue",
                values={
                    "device_id": d.id,
                    "issue_type": "incomplete",
                    "description": "no model photo",
                },
            )
        )
    )
    # A07 ERP audit M17-12: the assignee is a Branch Manager's to set
    assert refused(c.env, lambda: issue.with_user(c.clerk).write({"assigned_to_id": c.clerk.id}))
    issue.with_user(c.bm).action_assign(c.clerk2.id)
    assert issue.state == "open" and issue.raised_by_id == c.clerk
    # someone else (not assignee, not BM) cannot work it
    assert not ui.action(
        c.clerk, model="fix.device.quality.issue", ids=[issue.id], method="action_start", kwargs={}
    )["success"]
    ok(
        ui.action(
            c.clerk2,
            model="fix.device.quality.issue",
            ids=[issue.id],
            method="action_start",
            kwargs={},
        )
    )
    assert not ui.action(
        c.clerk2,
        model="fix.device.quality.issue",
        ids=[issue.id],
        method="action_resolve",
        kwargs={},
    )["success"]
    assert refused(c.env, lambda: issue.with_user(c.clerk2).write({"state": "resolved"}))
    ok(
        ui.action(
            c.bm,
            model="fix.device.quality.issue",
            ids=[issue.id],
            method="action_resolve",
            kwargs={"resolution": "photo added"},
        )
    )
    issue.invalidate_recordset()
    assert issue.state == "resolved" and issue.resolved_by_id == c.bm
    assert "error" in ui.write(
        c.bm, model="fix.device.quality.issue", record_id=issue.id, values={"severity": "low"}
    )


def test_the_sweep_lists_old_provisional_devices_once_and_escalates(c):  # noqa: F811
    d = (
        c.env["fix.device"]
        .with_user(c.clerk)
        .create(
            {
                "device_model_id": c.model.id,
                "owner_id": c.owner.id,
                "register_provisional": True,
                "provisional_reason": "label unreadable",
            }
        )
    )
    old = fields.Datetime.now() - timedelta(days=30)
    c.env.flush_all()
    c.env.cr.execute("UPDATE fix_device SET create_date = %s WHERE id = %s", (old, d.id))
    d.invalidate_recordset()
    Issue = c.env["fix.device.quality.issue"]
    Issue.cron_steward_sweep()
    Issue.cron_steward_sweep()
    found = Issue.search([("device_id", "=", d.id), ("issue_type", "=", "provisional")])
    assert len(found) == 1
    # a provisional issue is not resolved while the device is provisional
    assert refused(c.env, lambda: found.with_user(c.bm).action_resolve("done"))
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_device_quality_issue SET raised_at = %s WHERE id = %s", (old, found.id)
    )
    found.invalidate_recordset()
    Issue.cron_steward_sweep()
    found.invalidate_recordset()
    assert found.escalated and found.escalated_at


def test_every_new_form_saves_with_its_declared_required_fields(c):  # noqa: F811
    """No form omits a field the model requires and does not default."""
    for model in (
        "fix.device.label",
        "fix.device.accessory",
        "fix.device.configuration",
        "fix.device.population.change",
        "fix.device.estate.node",
        "fix.device.estate.placement",
        "fix.device.eol.decision",
        "fix.device.quality.issue",
    ):
        Model = c.env[model]
        defaults = Model.default_get(list(Model._fields))
        required = {
            n
            for n, f in Model._fields.items()
            if f.required and f.store and not f.compute and not f.related and n not in defaults
        }
        form_required = {
            "fix.device.label": {"device_id", "applied_by_id", "label_type", "applied_on"},
            "fix.device.accessory": {"device_id", "accessory_type", "quantity", "received_on"},
            "fix.device.configuration": {
                "device_id",
                "attribute",
                "value",
                "source",
                "effective_from",
            },
            "fix.device.population.change": {"device_id", "to_population", "reason_code"},
            "fix.device.estate.node": {"estate_id", "node_type", "name"},
            "fix.device.estate.placement": {"device_id", "estate_id", "placed_from", "move_reason"},
            "fix.device.eol.decision": {"device_id", "route", "basis"},
            "fix.device.quality.issue": {"device_id", "issue_type", "severity", "description"},
        }[model]
        assert required <= form_required, (model, required - form_required)
