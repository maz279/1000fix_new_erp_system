# A06 control suite (A06 workflow audit, P0 S1/S2 and P3): one sweep over
# EVERY workflow-controlled field and routed approval of the A06 Supply Chain
# surfaces, run as a non-admin user.
#
# The A06 audit (2026-11-03) found all 66 A06 models writable by a plain
# internal user, none guarded and no write whitelist, so a clerk raised and
# sent a BDT 5M purchase order, activated a supplier by typing its status and
# marked a valuation-suspense row reconciled. This suite is the A02 control
# suite applied to A06: per guarded field, a changing write() is refused by
# the guard; no workspace form offers the field as editable; a plain user can
# no longer write the A06 documents at all; and the routed approvals ignore a
# re-pointed approver group in the (still user-writable) M63 rule book. The
# per-module behaviour tests live in each addon's tests/test_a06_*_controls.py.

import itertools

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a06
from odoo.addons.cd_p03_portal.controllers.a06.writable import WRITABLE
from odoo.exceptions import AccessError, UserError

_SEQ = itertools.count(1)
GUARD_MESSAGE = "changes only through its workflow"
SIMPLE = {
    "char",
    "text",
    "boolean",
    "selection",
    "integer",
    "float",
    "monetary",
    "date",
    "datetime",
    "many2one",
}

# The 58 models the audit's exposure sweep found with an open workflow field
# (working/A06_evidence/probes/cross_area/a06_exposure_sweep.out.txt; the
# three that exposed only `active` are left out).
EXPOSED = (
    "fix.demand.forecast",
    "fix.demand.plan",
    "fix.demand.policy",
    "fix.demand.rebalance",
    "fix.demand.review",
    "fix.demand.scenario",
    "fix.demand.segment",
    "fix.import.arrival",
    "fix.import.boe",
    "fix.import.hs",
    "fix.import.irc",
    "fix.import.landed",
    "fix.import.lc",
    "fix.import.lca",
    "fix.import.order",
    "fix.import.proforma",
    "fix.import.shipdoc",
    "fix.inventory.valuation.suspense",
    "fix.procurement.award",
    "fix.procurement.bid",
    "fix.procurement.blanket",
    "fix.procurement.expedite",
    "fix.procurement.inspection",
    "fix.procurement.rfq",
    "fix.purchase.order",
    "fix.reorder.rule",
    "fix.requisition",
    "fix.spare.part",
    "fix.stock.consumption",
    "fix.stock.count",
    "fix.stock.count.line",
    "fix.stock.location",
    "fix.stock.lot",
    "fix.stock.quarantine",
    "fix.stock.receipt",
    "fix.stock.receipt.line",
    "fix.stock.rtv",
    "fix.stock.transfer",
    "fix.stock.van.recon",
    "fix.supplier",
    "fix.supplier.activation",
    "fix.supplier.car",
    "fix.supplier.document",
    "fix.supplier.performance",
    "fix.supplier.qualification",
    "fix.supplier.requalification",
    "fix.supplier.review",
    "fix.supplier.risk",
    "fix.supplier.screening",
    "fix.wms.carton",
    "fix.wms.dock",
    "fix.wms.floor.count",
    "fix.wms.putaway",
    "fix.wms.slot",
    "fix.wms.stage",
    "fix.wms.task",
    "fix.wms.wave",
    "fix.wms.wave.line",
)

# Any employee may still raise a purchase requisition (its state is guarded).
EMPLOYEE_WRITABLE = {"fix.requisition"}

# Supplier bank-detail proposals are confidential (M42-3): not even readable
# by employees outside the supplier stewards and approvers.
CONFIDENTIAL = {"fix.supplier.bank.change"}

# Approvals the audit required to be routed by amount (S3, R4).
ROUTED = ("fix.requisition", "fix.purchase.order", "fix.import.lc")


@pytest.fixture
def clerk_env(odoo_env):
    n = next(_SEQ)
    user = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A06 Control Suite Clerk %d" % n,
                "login": "a06.control.suite.%d@a06.test" % n,
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    return odoo_env(user=user.id)


def _forged_value(env, field, current):
    """A value different from `current` that a forger would send."""
    if field.type == "boolean":
        return not current
    if field.type == "selection":
        values = [v for v, _l in (field._description_selection(env) or [])]
        others = [v for v in values if v != current]
        return others[-1] if others else None
    if field.type in ("integer", "float", "monetary"):
        return (current or 0) + 7
    if field.type == "date":
        return fields.Date.add(fields.Date.today(), days=-400)
    if field.type == "datetime":
        return fields.Datetime.add(fields.Datetime.now(), days=-400)
    if field.type == "many2one":
        other = env[field.comodel_name].sudo().search([], limit=2)
        other = other - current if current else other
        return other[:1].id or None
    return "forged-by-the-control-suite"


@pytest.mark.parametrize("model", EXPOSED)
def test_every_exposed_model_is_guarded(odoo_env, model):
    """S2: each model the audit found with an open workflow field now names
    it among its guarded fields."""
    assert model in odoo_env, "%s is no longer installed" % model
    record = odoo_env[model]
    assert hasattr(record, "_fix_guarded_fields"), "%s has no workflow guard" % model
    assert record.browse()._fix_guarded_fields(), "%s guards no field" % model


@pytest.mark.parametrize("model", EXPOSED)
def test_every_guarded_field_refuses_a_direct_write(odoo_env, clerk_env, model):
    """R9 b: for every guarded field, a changing write() is refused by the guard."""
    record = clerk_env[model].new({})
    guarded = sorted(record._fix_guarded_fields())
    checked = 0
    for name in guarded:
        field = record._fields.get(name)
        if not field or field.type not in SIMPLE or not field.store or field.compute:
            continue
        if not record._has_field_access(field, "read"):
            # field-restricted (cost, a van's expected quantity; A06 final pass):
            # this user may not even read it, so the ORM refuses before the guard.
            # test_a_restricted_field_is_still_guarded_for_who_may_read_it below.
            with pytest.raises(AccessError):
                record.write({name: _forged_value(clerk_env, field, False)})
            checked += 1
            continue
        value = _forged_value(clerk_env, field, record[name])
        if value is None:
            continue
        with pytest.raises(UserError, match=GUARD_MESSAGE):
            record.write({name: value})
        checked += 1
    assert checked or not guarded, "%s declares guarded fields but none could be attacked" % model


@pytest.mark.parametrize(
    "model,name",
    [
        ("fix.stock.consumption", "unit_cost"),
        ("fix.stock.quarantine", "unit_cost"),
        ("fix.stock.rtv", "unit_cost"),
        ("fix.stock.van.recon", "expected_qty"),
    ],
)
def test_a_restricted_field_is_still_guarded_for_who_may_read_it(odoo_env, model, name):
    """The field restriction does not replace the guard: an Inventory Controller
    reads the cost and the expected quantity, and still cannot type them."""
    n = next(_SEQ)
    controller = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A06 Control Suite Controller %d" % n,
                "login": "a06.control.controller.%d@a06.test" % n,
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            odoo_env.ref("base.group_user").id,
                            odoo_env.ref("cd_wms_structure.group_inventory_controller").id,
                        ],
                    )
                ],
            }
        )
    )
    record = odoo_env(user=controller.id)[model].new({})
    with pytest.raises(UserError, match=GUARD_MESSAGE):
        record.write({name: 7.0})


@pytest.mark.parametrize("model", sorted(a06.SURFACES))
def test_no_form_offers_a_guarded_field_as_editable(odoo_env, model):
    """A workflow-owned field is never an editable input on a workspace form,
    so the screen never offers what the server refuses."""
    if not hasattr(odoo_env[model], "_fix_guarded_fields"):
        pytest.skip("%s carries no workflow-controlled fields" % model)
    guarded = odoo_env[model].browse()._fix_guarded_fields()
    offered = guarded & set(WRITABLE.get(model, ()))
    assert not offered, "the %s form offers workflow fields as editable: %s" % (
        model,
        sorted(offered),
    )


@pytest.mark.parametrize("model", sorted(a06.SURFACES))
def test_a_plain_user_cannot_write_a06_documents(odoo_env, clerk_env, model):
    """S1: the A06 powers moved from base.group_user to role groups. A plain
    employee keeps read access (other modules read stock and suppliers) and,
    for a requisition only, may raise one."""
    records = clerk_env[model]
    if model in EMPLOYEE_WRITABLE:
        assert records.has_access("create"), "%s: employees can no longer raise one" % model
        return
    if model in CONFIDENTIAL:
        assert not records.has_access("read"), "%s is readable by a plain user" % model
    assert model in CONFIDENTIAL or records.has_access("read") or model.startswith("fix.wms."), (
        "%s is no longer readable by employees" % model
    )
    assert not records.has_access("write"), "%s is still writable by a plain user" % model
    assert not records.has_access("create"), "%s is still creatable by a plain user" % model


@pytest.mark.parametrize("model", ROUTED)
def test_routed_approvals_use_the_engine(odoo_env, model):
    """S3/R4: these approvals are routed requests (M63), not a state flip."""
    records = odoo_env[model]
    assert hasattr(records, "action_request_approval") and "approval_state" in records._fields, (
        "%s is not a routed approval" % model
    )
    assert records._approval_routed, "%s can still be approved directly" % model


@pytest.mark.parametrize("model", ROUTED)
def test_routed_approvals_ignore_a_repointed_matrix_group(odoo_env, clerk_env, model):
    """The M63 rule book is still writable by every user (A11 audit M63-2,
    fix E1-E4 pending). A06 must not take its approver from it: a clerk who
    re-points a matrix row to his own group gains nothing."""
    clerk_group = clerk_env.ref("base.group_user")
    rule = odoo_env["fix.approval.matrix"].new({"approver_group_id": clerk_group.id})
    record = odoo_env[model].new({})
    for tier in ("tier_1", "tier_2", "tier_4"):
        group = record._approval_group_for(rule, tier)
        assert group != clerk_group, "%s takes its approver from the matrix" % model
