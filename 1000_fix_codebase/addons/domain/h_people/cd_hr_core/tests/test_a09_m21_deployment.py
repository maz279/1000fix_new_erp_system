# A09 M21 deployment test (BUILD_BRIEF §6.8, §7): what must exist in the
# database for the M21 controls to run at all. A cron method without its
# ir.cron never runs while its unit test still passes; a consumer without its
# fix.event.consumer row never receives an event.
import pytest
from odoo.addons.cd_p03_portal.controllers import a09, form_fields
from odoo.addons.cd_p03_portal.controllers.a09 import m21

CRONS = {
    "cd_hr_core.ir_cron_m21_probation_review": "_cron_probation_review",
    "cd_hr_core.ir_cron_m21_contract_expiry": "_cron_contract_expiry",
    "cd_hr_core.ir_cron_m21_last_working_day": "_cron_process_last_working_days",
    "cd_hr_core.ir_cron_m21_settlement_due": "_cron_flag_overdue_settlements",
    "cd_hr_core.ir_cron_m21_disciplinary_deadlines": "_cron_disciplinary_deadlines",
    # A09 round 2
    "cd_hr_core.ir_cron_m21_abandonment_timeline": "_cron_abandonment_timeline",
    "cd_hr_core.ir_cron_m21_identity_residency": "_cron_identity_residency_move",
}
GROUPS = (
    "cd_hr_core.group_hr_legal_counsel",
    "cd_hr_core.group_hr_executive",
    "cd_hr_core.group_hr_finance",
    "cd_hr_core.group_clearance_it",
    "cd_hr_core.group_clearance_assets",
)
ACLS = (
    "cd_hr_core.access_fix_employment_contract_legal",
    "cd_hr_core.access_fix_hr_transfer_executive",
    "cd_hr_core.access_fix_hr_transfer_finance",
    "cd_hr_core.access_fix_hr_transfer_assets",
    "cd_hr_core.access_fix_hr_exit_finance",
    "cd_hr_core.access_fix_hr_exit_it",
    "cd_hr_core.access_fix_hr_exit_assets",
    "cd_hr_core.access_fix_hr_master_change_user",
    "cd_hr_core.access_fix_hr_master_change_officer",
    "cd_hr_core.access_fix_hr_disciplinary_case_officer",
    "cd_hr_core.access_fix_hr_disciplinary_case_executive",
    # A09 round 2
    "cd_hr_core.access_fix_hr_identity_access_log_manager",
    "cd_hr_core.access_fix_hr_abandonment_officer",
    "cd_hr_core.access_fix_hr_abandonment_executive",
)
M21_MODELS = (
    "hr.employee",
    "fix.employment.contract",
    "fix.hr.transfer",
    "fix.hr.exit",
    "fix.hr.document",
    "fix.hr.education",
    "fix.hr.experience",
    "fix.hr.master.change",
    "fix.hr.disciplinary.case",
    "fix.hr.abandonment",
)


@pytest.mark.parametrize("xmlid,method", sorted(CRONS.items()))
def test_every_m21_cron_exists_active_and_calls_a_real_method(odoo_env, xmlid, method):
    cron = odoo_env.ref(xmlid)
    assert cron.active and cron.state == "code"
    assert method in cron.code
    assert callable(getattr(odoo_env[cron.model_id.model], method))


def test_the_leaver_consumer_is_subscribed(odoo_env):
    sub = odoo_env.ref("cd_hr_core.event_consumer_employee_left_access")
    assert (sub.event_type, sub.model, sub.method, sub.active) == (
        "employee.left",
        "hr.employee",
        "consume_employee_left",
        True,
    )
    assert odoo_env.ref("cd_event_outbox.ir_cron_event_relay").active


@pytest.mark.parametrize("xmlid", GROUPS)
def test_decision_roles_exist_and_hold_only_root_and_admin(odoo_env, xmlid):
    group = odoo_env.ref(xmlid)
    allowed = odoo_env.ref("base.user_root") | odoo_env.ref("base.user_admin")
    # test users created by other tests are rolled back; nothing else is seeded
    assert not (group.user_ids - allowed).filtered(lambda u: not u.login.endswith("test.local"))
    assert odoo_env.ref("base.group_user") in group.implied_ids


@pytest.mark.parametrize("xmlid", ACLS)
def test_new_acl_rows_exist(odoo_env, xmlid):
    assert odoo_env.ref(xmlid).perm_read


def test_m21_surfaces_expose_the_new_actions_and_drop_the_unrouted_ones():
    actions = {model: conf["actions"] for model, conf in a09.SURFACES.items()}
    assert {"action_mark_left", "action_confirm_keycloak_deprovisioned"} <= actions["hr.employee"]
    assert "action_export_form6a_register" not in actions["hr.employee"]
    assert "action_approve_legal_signoff" not in actions["fix.employment.contract"]
    assert "action_terminate" not in actions["fix.employment.contract"]
    assert "action_approve" not in actions["fix.hr.transfer"]
    assert "action_settle" not in actions["fix.hr.exit"]
    assert {"action_confirm_notice", "action_compute_settlement"} <= actions["fix.hr.exit"]
    assert "form6a_register" in m21.REPORTS


def test_new_m21_surfaces_are_served_with_a_whitelist():
    """The master-change and disciplinary surfaces are in the area, and the
    whitelist generator knows them (a surface with no entry fails import)."""
    new = {"fix.hr.master.change", "fix.hr.disciplinary.case"}
    assert new <= set(a09.SURFACES)
    assert new <= form_fields.surface_models("a09")


@pytest.mark.parametrize("model", M21_MODELS)
def test_no_m21_form_offers_a_guarded_field(odoo_env, model):
    """The forms (the generator's input) never offer a guarded field, so the
    regenerated whitelist cannot let one through."""
    editable = form_fields.editable_by_model().get(model, set())
    guarded = odoo_env[model].browse()._fix_guarded_fields()
    assert not (editable & guarded), sorted(editable & guarded)


def test_upgrade_rederives_stale_dossier_flags(odoo_env):
    """Rows saved while the flags defaulted to True are reset by the upgrade step."""
    emp = odoo_env["hr.employee"].create({"name": "M21 Stale Dossier"})
    odoo_env.flush_all()
    odoo_env.cr.execute(
        "UPDATE hr_employee SET doc_appointment_signed = TRUE, doc_nid_verified = TRUE WHERE id = %s",
        (emp.id,),
    )
    odoo_env.invalidate_all()
    assert emp.doc_appointment_signed
    odoo_env["hr.employee"]._fix_recompute_evidence_flags()
    odoo_env.invalidate_all()
    assert not emp.doc_appointment_signed and not emp.doc_nid_verified


def test_the_mover_consumer_is_subscribed(odoo_env):
    sub = odoo_env.ref("cd_hr_core.event_consumer_employee_moved_review")
    assert (sub.event_type, sub.model, sub.method, sub.active) == (
        "employee.moved",
        "hr.employee",
        "consume_employee_moved",
        True,
    )


def test_the_role_change_consumer_is_subscribed(odoo_env):
    sub = odoo_env.ref("cd_hr_core.event_consumer_employee_role_changed_review")
    assert (sub.event_type, sub.model, sub.method, sub.active) == (
        "employee.role_changed",
        "hr.employee",
        "consume_employee_role_changed",
        True,
    )


def test_round2_surfaces_actions_and_reports_are_served():
    actions = {model: conf["actions"] for model, conf in a09.SURFACES.items()}
    assert "action_issue_service_certificate" in actions["fix.hr.exit"]
    assert {"action_issue_notice", "action_record_explanation", "action_request_approval"} <= (
        actions["fix.hr.abandonment"]
    )
    assert "action_deem_resigned" not in actions["fix.hr.abandonment"]  # inbox only
    assert "fix.hr.abandonment" in form_fields.surface_models("a09")
    assert {"identity_access_log", "data_cleanup"} <= set(m21.REPORTS)


def test_the_identity_hash_key_exists_and_the_fields_are_not_stored(odoo_env):
    """The HMAC key is created at install; the three identifiers are computed
    (held in the resident store), their hashes and the pointer are stored."""
    assert odoo_env["ir.config_parameter"].sudo().get_param("cd_hr_core.identity_hash_key")
    fields_ = odoo_env["hr.employee"]._fields
    for name in ("nid_number", "tin_number", "birth_reg_number"):
        assert not fields_[name].store and fields_[name].inverse and fields_[name].search
    for name in ("nid_hash", "tin_hash", "birth_reg_hash", "residency_ref"):
        assert fields_[name].store
