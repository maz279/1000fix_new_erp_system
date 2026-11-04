# A06 deployment wiring (A06 workflow audit S1 and P2): what a unit test that
# calls a method directly cannot see.
#
# A role nobody can be appointed to, a cron method with no ir.cron record, or
# an event consumer that names a method the model does not have all pass every
# behaviour test and do nothing in production (the A03 gap-closure build
# nearly shipped 19 crons with no record). This keeps the A06 wiring honest.
import pytest

A06_ADDONS = (
    "cd_inventory",
    "cd_wms_structure",
    "cd_requisition",
    "cd_vendor_portal",
    "cd_demand_plan",
    "cd_import_order",
)

# S1: the roles. Operational groups carry the development admin so the
# workspace keeps working; approver groups ship EMPTY, because who approves is
# a business appointment (A06 report section 7) and the maker never approves.
OPERATIONAL = (
    "cd_wms_structure.group_storekeeper",
    "cd_wms_structure.group_warehouse_operator",
    "cd_requisition.group_fix_procurement_buyer",
    "cd_requisition.group_fix_procurement_receiver",
    "cd_vendor_portal.group_fix_supplier_steward",
    "cd_demand_plan.group_fix_demand_planner",
    "cd_import_order.group_fix_import_officer",
)
APPROVERS = (
    "cd_wms_structure.group_inventory_controller",
    "cd_requisition.group_fix_procurement_approver",
    "cd_requisition.group_fix_procurement_manager",
    "cd_vendor_portal.group_fix_supplier_approver",
    "cd_demand_plan.group_fix_demand_approver",
    "cd_import_order.group_fix_import_approver",
)


@pytest.mark.parametrize("xmlid", OPERATIONAL + APPROVERS)
def test_every_a06_role_exists_and_implies_employee(odoo_env, xmlid):
    group = odoo_env.ref(xmlid, raise_if_not_found=False)
    assert group, "role %s is not installed" % xmlid
    assert odoo_env.ref("base.group_user") in group.all_implied_ids, xmlid


@pytest.mark.parametrize("xmlid", APPROVERS)
def test_approver_roles_do_not_carry_the_development_admin(odoo_env, xmlid):
    """The admin is the maker in the workspace; were he also the approver, the
    first installation would ship self-approval."""
    group = odoo_env.ref(xmlid)
    assert odoo_env.ref("base.user_admin") not in group.user_ids, xmlid


def _a06_records(env, model):
    data = env["ir.model.data"].sudo().search([("module", "in", A06_ADDONS), ("model", "=", model)])
    return env[model].sudo().browse(data.mapped("res_id")).exists()


def test_every_a06_cron_record_runs_a_method_that_exists(odoo_env):
    crons = _a06_records(odoo_env, "ir.cron")
    assert crons, "the A06 addons ship no scheduled job"
    for cron in crons:
        model = odoo_env[cron.model_id.model]
        code = (cron.code or "").strip()
        assert code.startswith("model."), (cron.name, code)
        method = code[len("model.") :].split("(")[0]
        assert callable(getattr(model, method, None)), "%s calls missing %s.%s" % (
            cron.name,
            cron.model_id.model,
            method,
        )
        assert cron.active, "%s is shipped inactive" % cron.name


def test_every_a06_event_consumer_names_a_real_method(odoo_env):
    consumers = _a06_records(odoo_env, "fix.event.consumer")
    events = set(consumers.mapped("event_type"))
    # P2 hand-offs that have a real consumer now.
    for needed in ("inspection.rejected", "goods.received", "po.acknowledged"):
        assert needed in events, "no A06 consumer for %s" % needed
    for consumer in consumers:
        assert consumer.model in odoo_env, (consumer.name, consumer.model)
        assert callable(getattr(odoo_env[consumer.model], consumer.method, None)), (
            consumer.name,
            consumer.method,
        )
