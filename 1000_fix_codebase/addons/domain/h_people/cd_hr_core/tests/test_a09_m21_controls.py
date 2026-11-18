# A09 M21 acceptance suite (P0-b B1-B6, P1 C1-C3/C5/C6, P2) for Core HR:
# the employee master, contracts, movements, exits, documents, nominees,
# positions and the disciplinary procedure.
#
# Evidence standard (BUILD_BRIEF §7): every attack runs as a freshly created
# NON-admin user, writes go through call_kw with the client-controlled
# `tracking_disable` key (the A09 report §8.4 bypass), workspace paths go
# through the real /p03 controller, and each control's proper path is then
# proved for the right role. No inspect.getsource or hasattr.
import itertools
import json
from datetime import date, timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_hr_core.tests.residency_memory import install
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a09 import m21 as m21_surfaces
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.service.model import call_kw

REFUSED = (AccessError, UserError, ValidationError)
_SEQ = itertools.count(1)
TODAY = fields.Date.today()


class FakeRequest:
    def __init__(self, env):
        self.env = env


def _user(env, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M21 User %d" % n,
                "login": "a09-m21-%d@test.local" % n,
                "tz": "UTC",
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _emp(env, user=None, **vals):
    n = next(_SEQ)
    return env["hr.employee"].create(
        {"name": "M21 Employee %d" % n, "user_id": user.id if user else False, **vals}
    )


def _contract(env, emp, **vals):
    base = {
        "employee_id": emp.id,
        "contract_type": "permanent",
        "joining_date": date(2020, 1, 1),
        "basic_monthly": 30000.0,
    }
    base.update(vals)
    return env["fix.employment.contract"].create(base)


def _rpc_write(env, user, model, rec, vals):
    return call_kw(
        env(user=user.id, context={"tracking_disable": True})[model], "write", [[rec.id], vals], {}
    )


def _rpc_create(env, user, model, vals):
    return call_kw(
        env(user=user.id, context={"tracking_disable": True})[model], "create", [vals], {}
    )


def _task(rec, user):
    return (
        rec.env["fix.workflow.task"]
        .sudo()
        .search(
            [
                ("request_id", "=", rec.approval_request_id.id),
                ("assigned_user_id", "=", user.id),
                ("state", "=", "pending"),
            ]
        )
    )


def _approve(rec, user):
    task = _task(rec, user)
    assert task, "no inbox task for %s on %s" % (user.name, rec.display_name)
    task.with_user(user).action_approve()


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(r.payload) for r in env["fix.event.outbox"].search(domain, order="id")]


@pytest.fixture(autouse=True)
def residency(monkeypatch):
    """NID / birth registration / e-TIN go to the resident store (round 2);
    an in-memory store stands in so the values round-trip in these tests."""
    return install(monkeypatch)


@pytest.fixture
def w(odoo_env):
    class W:
        pass

    c = W()
    env = c.env = odoo_env
    global TODAY
    TODAY = fields.Date.context_today(odoo_env.user)  # the tz the code dates by
    c.plain = _user(env)
    c.hro = _user(env, "cd_hr_core.group_hr_officer")
    c.hro2 = _user(env, "cd_hr_core.group_hr_officer")
    c.hro3 = _user(env, "cd_hr_core.group_hr_officer")
    c.legal = _user(env, "cd_hr_core.group_hr_legal_counsel")
    c.execu = _user(env, "cd_hr_core.group_hr_executive")
    c.fin = _user(env, "cd_hr_core.group_hr_finance")
    c.it = _user(env, "cd_hr_core.group_clearance_it")
    c.assets = _user(env, "cd_hr_core.group_clearance_assets")
    c.mgr = _user(env)
    c.dmgr = _user(env)
    c.mgr_emp = _emp(env, c.mgr)
    c.dmgr_emp = _emp(env, c.dmgr)
    c.me = _emp(env, c.plain, parent_id=c.mgr_emp.id)
    c.colleague = _emp(env)
    return c


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


# ============================================================ master (M21-1, M21-9)
@pytest.mark.parametrize(
    "field,value",
    [
        ("nid_number", "NID-ABC-12"),
        ("nid_number", "123456789012"),  # 12 digits
        ("tin_number", "12345"),
        ("routing_number", "BRAC-01"),
        ("mfs_account_number", "abc"),
        ("mfs_account_number", "01212345678"),  # 012 is no mobile operator
        ("birth_reg_number", "12345"),
        ("bank_account_number", "ACC-1"),
    ],
)
def test_master_formats_are_refused_for_hr(w, field, value):
    target = _emp(w.env)
    with pytest.raises(ValidationError):
        _rpc_write(w.env, w.hro, "hr.employee", target, {field: value})


def test_master_valid_formats_are_accepted(w):
    target = _emp(w.env)
    vals = {
        "nid_number": "19901234567890123",
        "tin_number": "123456789012",
        "routing_number": "060274689",
        "mfs_account_number": "01712345678",
        "bank_account_number": "1501203345001",
    }
    _rpc_write(w.env, w.hro, "hr.employee", target, vals)
    assert target.nid_number == "19901234567890123"
    for nid in ("1234567890", "1234567890123"):
        _rpc_write(w.env, w.hro, "hr.employee", _emp(w.env), {"nid_number": nid})


def test_duplicate_nid_and_tin_are_refused(w):
    _emp(w.env, nid_number="1234567891", tin_number="111122223333")
    other = _emp(w.env)
    with pytest.raises(ValidationError, match="already recorded"):
        _rpc_write(w.env, w.hro, "hr.employee", other, {"nid_number": "1234567891"})
    with pytest.raises(ValidationError, match="already recorded"):
        _rpc_write(w.env, w.hro, "hr.employee", other, {"tin_number": "111122223333"})


def test_employee_code_is_unique_and_permanent(w):
    _emp(w.env, employee_code="E-M21-1")
    other = _emp(w.env, employee_code="E-M21-2")
    with pytest.raises(ValidationError, match="already in use"):
        _rpc_create(w.env, w.hro, "hr.employee", {"name": "Dup", "employee_code": "E-M21-1"})
    with pytest.raises(UserError, match="permanent"):
        _rpc_write(w.env, w.hro, "hr.employee", other, {"employee_code": "E-M21-9"})
    assert other.employee_code == "E-M21-2"


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("bank_account_number", "9999000011112222", "Employee Master Change"),
        ("routing_number", "090261725", "Employee Master Change"),
        ("mfs_account_number", "01899999999", "Employee Master Change"),
        ("nid_number", "9999999999", "Employee Master Change"),
        ("basic_wage", 250000.0, "Transfer / Promotion"),
        ("wage", 400000.0, "Transfer / Promotion"),
        ("overtime_eligible", False, "Transfer / Promotion"),
    ],
)
def test_payroll_employee_master_is_never_written_directly(w, field, value, match):
    """M21-1: once on the payroll, even HR cannot repoint the salary channel."""
    _contract(w.env, w.colleague, state="active")
    with pytest.raises(UserError, match=match):
        _rpc_write(w.env, w.hro, "hr.employee", w.colleague, {field: value})


def test_salary_account_record_cannot_be_rewritten_behind_the_gate(w):
    partner = w.colleague.work_contact_id
    bank = w.env["res.partner.bank"].create(
        {"acc_number": "1501203345009", "partner_id": partner.id}
    )
    w.colleague.write({"bank_account_ids": [(6, 0, [bank.id])]})
    _contract(w.env, w.colleague, state="active")
    with pytest.raises(UserError, match="salary account"):
        _rpc_write(w.env, w.hro, "res.partner.bank", bank, {"acc_number": "9999000011112222"})


def test_master_change_is_maker_checker(w):
    _contract(w.env, w.colleague, state="active")
    req = w.env(user=w.hro.id)["fix.hr.master.change"].create(
        {
            "employee_id": w.colleague.id,
            "reason": "New salary account",
            "proposed_bank_account_number": "2702150098761",
            "proposed_routing_number": "090261725",
        }
    )
    req.action_submit()
    assert req.approval_state == "pending" and req.state == "submitted"
    # the maker gets no task and cannot apply it directly
    assert not _task(req, w.hro)
    with pytest.raises(UserError, match="approver's inbox"):
        req.with_user(w.hro).action_apply_change()
    # a submitted proposal is frozen
    with pytest.raises(UserError, match="never edited"):
        _rpc_write(
            w.env,
            w.hro,
            "fix.hr.master.change",
            req,
            {"proposed_bank_account_number": "1111111111"},
        )
    _approve(req, w.hro2)
    assert req.state == "applied"
    assert w.colleague.bank_account_number == "2702150098761"
    assert w.colleague.routing_number == "090261725"
    assert w.colleague.primary_bank_account_id.acc_number == "2702150098761"
    msg = w.colleague.message_ids[:1].body or ""
    assert "2702150098761" not in msg  # the log names fields, never values
    assert _events(w.env, "employee.master.changed", w.colleague.id)[-1]["fields"]


def test_master_change_carries_the_routing_number_to_the_payee_account(w):
    """E2E3 flow 9: the approved salary account reached res.partner.bank
    without its BEFTN routing number, so treasury refused every BEFTN
    disbursement to the employee ("payee account ... has no routing number")."""
    Bank = w.env["res.partner.bank"]
    if "fix_routing_number" not in Bank._fields:
        pytest.skip("no treasury routing field on res.partner.bank in this database")
    _contract(w.env, w.colleague, state="active")
    req = w.env(user=w.hro.id)["fix.hr.master.change"].create(
        {
            "employee_id": w.colleague.id,
            "reason": "New salary account",
            "proposed_bank_account_number": "2702150098761",
            "proposed_routing_number": "090261725",
        }
    )
    req.action_submit()
    _approve(req, w.hro2)
    bank = w.colleague.primary_bank_account_id
    assert bank.acc_number == "2702150098761"
    assert bank.fix_routing_number == "090261725"
    # a routing-only change (branch moved) reaches the same payee account
    req2 = w.env(user=w.hro.id)["fix.hr.master.change"].create(
        {
            "employee_id": w.colleague.id,
            "reason": "Branch moved",
            "proposed_routing_number": "060274689",
        }
    )
    req2.action_submit()
    _approve(req2, w.hro2)
    assert w.colleague.routing_number == "060274689"
    assert w.colleague.primary_bank_account_id == bank
    assert bank.fix_routing_number == "060274689"
    # and the routing number cannot be rewritten behind the gate either
    with pytest.raises(UserError, match="salary account"):
        _rpc_write(w.env, w.hro, "res.partner.bank", bank, {"fix_routing_number": "010000001"})


def test_employee_raises_own_bank_change_and_never_decides_it(w):
    _contract(w.env, w.me, state="active")
    req = w.env(user=w.plain.id)["fix.hr.master.change"].create(
        {
            "employee_id": w.me.id,
            "reason": "Moved bank",
            "proposed_mfs_account_number": "01712345670",
        }
    )
    req.action_submit()
    assert not _task(req, w.plain)
    _approve(req, w.hro)
    assert w.me.sudo().mfs_account_number == "01712345670"
    # ...but never for a colleague
    with pytest.raises(AccessError):
        w.env(user=w.plain.id)["fix.hr.master.change"].create(
            {
                "employee_id": w.colleague.id,
                "reason": "x",
                "proposed_mfs_account_number": "01712345671",
            }
        )


def test_master_change_refused_when_the_master_moved_meanwhile(w):
    req = w.env(user=w.hro.id)["fix.hr.master.change"].create(
        {"employee_id": w.colleague.id, "reason": "r", "proposed_tin_number": "123412341234"}
    )
    req.action_submit()
    w.colleague.write({"tin_number": "999988887777"})  # changed outside the request
    task = _task(req, w.hro2)
    with pytest.raises(UserError, match="changed since"):
        task.with_user(w.hro2).action_approve()


def test_master_change_proposal_formats_are_checked(w):
    with pytest.raises(ValidationError):
        w.env(user=w.hro.id)["fix.hr.master.change"].create(
            {"employee_id": w.colleague.id, "reason": "r", "proposed_routing_number": "12AB"}
        )


def test_direct_position_or_branch_change_announces_a_move(w):
    pos = w.env["fix.org.position"].create({"name": "M21 Mover Seat"})
    w.colleague.write({"position_id": pos.id})
    assert _events(w.env, "employee.moved", w.colleague.id)


# ============================================================ dossier (M21-10)
def test_a_new_employee_claims_no_evidence(w):
    emp = _emp(w.env)
    flags = [
        "doc_nid_verified",
        "doc_tin_verified",
        "doc_psr_verified",
        "doc_appointment_signed",
        "doc_nda_signed",
        "doc_service_book_scanned",
        "doc_medical_fit_certified",
        "doc_police_pcc_cleared",
        "customer_nda_signed",
        "esd_certified",
    ]
    assert not any(emp[f] for f in flags)
    assert emp.academic_verified == "pending" and not emp.prev_reference_status
    assert emp.sudo().color_blindness == "untested"


def _doc(env, user, emp, doc_type="nid_smart", file=b"c2Nhbg==", **vals):
    return env(user=user.id)["fix.hr.document"].create(
        {"employee_id": emp.id, "doc_type": doc_type, "file_data": file, **vals}
    )


def test_document_is_verified_by_a_second_person_with_a_file(w):
    doc = _doc(w.env, w.hro, w.colleague)
    assert not doc.verified
    with pytest.raises(UserError, match="someone other"):
        doc.with_user(w.hro).action_verify()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(w.env, w.hro, "fix.hr.document", doc, {"verified": True})
    nofile = _doc(w.env, w.hro, w.colleague, doc_type="tin_cert", file=False)
    with pytest.raises(UserError, match="Attach"):
        nofile.with_user(w.hro2).action_verify()
    doc.with_user(w.hro2).action_verify()
    assert doc.verified and doc.verified_by_id == w.hro2
    assert w.colleague.doc_nid_verified
    # a new file is new evidence
    _rpc_write(w.env, w.hro, "fix.hr.document", doc, {"file_data": b"bmV3"})
    assert not doc.verified and not w.colleague.doc_nid_verified


def test_generated_letters_never_self_verify_and_only_the_employee_acknowledges(w):
    me = w.me
    _contract(w.env, me, state="active")  # Form 6 states the contract's terms
    doc = me.with_user(w.hro).action_generate_form6_appointment()
    assert doc.generated and not doc.verified and not me.doc_appointment_signed
    with pytest.raises(UserError, match="unsigned"):
        doc.with_user(w.hro2).action_verify()
    with pytest.raises(UserError, match="Only"):
        doc.with_user(w.hro).action_acknowledge()
    _rpc_write(w.env, w.hro, "fix.hr.document", doc, {"file_data": b"c2lnbmVk"})  # the signed scan
    doc.with_user(w.hro2).action_verify()
    assert not me.doc_appointment_signed  # verified, not yet acknowledged
    doc.with_user(w.plain).action_acknowledge()
    assert me.doc_appointment_signed


def test_service_book_is_append_only(w):
    book = w.colleague.with_user(w.hro).action_generate_form7_service_book()
    hrm = _user(w.env, "hr.group_hr_manager")
    with pytest.raises(UserError, match="append-only"):
        _rpc_write(w.env, hrm, "fix.hr.document", book, {"issued_on": date(2020, 1, 1)})
    with pytest.raises(UserError, match="never deleted"):
        book.with_user(hrm).unlink()


def test_education_and_reference_checks_need_a_second_person(w):
    edu = w.env(user=w.hro.id)["fix.hr.education"].create(
        {
            "employee_id": w.colleague.id,
            "degree_title": "Diploma",
            "major_group": "EEE",
            "board_university": "BTEB",
            "passing_year": 2018,
            "gpa_score": 3.5,
            "certificate_file": b"Y2VydA==",
        }
    )
    assert edu.is_verified == "pending"
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(w.env, w.hro, "fix.hr.education", edu, {"is_verified": "verified_online"})
    with pytest.raises(UserError, match="someone other"):
        edu.with_user(w.hro).action_verify_online()
    edu.with_user(w.hro2).action_verify_online()
    assert w.colleague.academic_verified == "verified_online"
    exp = w.env(user=w.hro.id)["fix.hr.experience"].create(
        {
            "employee_id": w.colleague.id,
            "company_name": "Prior Ltd",
            "designation_held": "Tech",
            "start_date": date(2015, 1, 1),
            "end_date": date(2018, 1, 1),
        }
    )
    assert not exp.reference_status
    with pytest.raises(UserError, match="evidence"):
        exp.with_user(w.hro2).action_reference_positive()
    _rpc_write(w.env, w.hro, "fix.hr.experience", exp, {"supervisor_phone": "01711111111"})
    exp.with_user(w.hro2).action_reference_positive()
    assert w.colleague.prev_reference_status == "verified_positive"


def test_psr_is_verified_by_someone_other_than_its_recorder(w):
    emp = w.colleague
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(w.env, w.hro, "hr.employee", emp, {"psr_status": "verified"})
    emp.write({"psr_ack_number": "PSR-1", "psr_tax_year": "2026-2027"})
    emp.with_user(w.hro).action_record_psr_submission()
    with pytest.raises(UserError, match="recorded the PSR"):
        emp.with_user(w.hro).action_verify_psr()
    with pytest.raises(UserError, match="Attach"):
        emp.with_user(w.hro2).action_verify_psr()
    emp.write({"doc_psr_file": b"cHNy"})
    emp.with_user(w.hro2).action_verify_psr()
    assert emp.psr_status == "verified" and emp.psr_verified_by_id == w.hro2


# ============================================================ contracts (M21-8)
def _signed_off(c, contract):
    contract.with_user(c.hro).action_request_legal_signoff()
    _approve(contract, c.legal)
    return contract


def test_contract_born_active_is_refused_for_hr(w):
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_create(
            w.env,
            w.hro,
            "fix.employment.contract",
            {
                "employee_id": w.colleague.id,
                "contract_type": "probation",
                "joining_date": str(TODAY),
                "probation_end": str(TODAY + timedelta(days=375)),
                "weekly_hours": 72,
                "basic_monthly": 0,
                "state": "active",
            },
        )


def test_legal_signoff_is_routed_and_activation_needs_it(w):
    contract = w.env(user=w.hro.id)["fix.employment.contract"].create(
        {
            "employee_id": w.colleague.id,
            "contract_type": "permanent",
            "joining_date": str(TODAY),
            "basic_monthly": 40000,
        }
    )
    with pytest.raises(UserError, match="sign-off before activation"):
        contract.with_user(w.hro).action_activate()
    contract.with_user(w.hro).action_request_legal_signoff()
    assert contract.legal_signoff_state == "pending" and contract.approval_state == "pending"
    with pytest.raises(UserError, match="approver's inbox"):
        contract.with_user(w.legal).action_approve_legal_signoff()
    for vals in ({"legal_signoff_state": "approved"}, {"signed_by_legal_counsel": "Counsel X"}):
        with pytest.raises(UserError, match="changes only through its workflow"):
            _rpc_write(w.env, w.hro, "fix.employment.contract", contract, vals)
    _approve(contract, w.legal)
    assert contract.legal_signoff_state == "approved"
    assert contract.signed_by_legal_counsel == w.legal.name
    contract.with_user(w.hro2).action_activate()
    assert contract.state == "active"


def test_the_drafter_who_is_also_counsel_never_signs_off(w):
    both = _user(w.env, "cd_hr_core.group_hr_officer", "cd_hr_core.group_hr_legal_counsel")
    contract = w.env(user=both.id)["fix.employment.contract"].create(
        {"employee_id": w.colleague.id, "joining_date": str(TODAY), "basic_monthly": 1}
    )
    contract.with_user(both).action_request_legal_signoff()
    assert not _task(contract, both)


def test_terms_changed_after_signoff_void_it(w):
    contract = _contract(w.env, w.colleague)
    _signed_off(w, contract)
    _rpc_write(w.env, w.hro, "fix.employment.contract", contract, {"basic_monthly": 90000})
    assert contract.legal_signoff_state == "pending" and contract.approval_state == "none"
    with pytest.raises(UserError, match="sign-off"):
        contract.with_user(w.hro).action_activate()


def test_active_contract_is_never_edited_in_place(w, call):
    contract = _contract(w.env, w.colleague, state="active")
    for vals in (
        {"basic_monthly": 250000},
        {"joining_date": "2019-01-01"},
        {"probation_end": "2020-03-01"},
    ):
        with pytest.raises(UserError, match="new version"):
            _rpc_write(w.env, w.hro, "fix.employment.contract", contract, vals)
    res = call(
        w.env(user=w.hro.id),
        "model_write",
        model="fix.employment.contract",
        record_id=contract.id,
        values={"basic_monthly": 250000, "state": "draft"},
    )
    assert not res.get("success"), res
    assert contract.basic_monthly == 30000.0 and contract.state == "active"


def test_hr_officer_cannot_raise_own_pay_sod_25(w):
    own = _emp(w.env, w.hro)
    active = _contract(w.env, own, state="active")
    new = w.env["fix.employment.contract"].browse(
        active.with_user(w.hro3).action_new_version()["res_id"]
    )
    _rpc_write(w.env, w.hro, "fix.employment.contract", new, {"basic_monthly": 250000})
    new.with_user(w.hro).action_request_legal_signoff()
    _approve(new, w.legal)
    with pytest.raises(UserError, match="own contract"):
        new.with_user(w.hro).action_activate()


def test_versioning_supersedes_and_announces_the_pay_change(w):
    old = _contract(w.env, w.colleague, state="active")
    new = w.env["fix.employment.contract"].browse(
        old.with_user(w.hro).action_new_version(effective_date=TODAY)["res_id"]
    )
    assert new.joining_date == old.joining_date  # payroll counts service from it
    _rpc_write(w.env, w.hro, "fix.employment.contract", new, {"basic_monthly": 36000})
    _signed_off(w, new)
    new.with_user(w.hro2).action_activate()
    assert (old.state, new.state) == ("superseded", "active")
    assert old.date_end == TODAY - timedelta(days=1)
    assert _events(w.env, "contract.versioned", new.id)
    assert _events(w.env, "salary_structure.changed", new.id)[0]["basic"] == 36000.0


def _reviewed(w, contract, recommendation):
    """Arrangement (superuser): the line manager's submitted probation review
    (M21 capture pass 2), written by w.mgr, never by the deciding officer."""
    review = w.env["fix.hr.probation.review"].create(
        {
            "employee_id": contract.employee_id.id,
            "reviewer_id": w.mgr.id,
            "rating_attendance": "4",
            "rating_quality": "4",
            "rating_skill": "4",
            "rating_conduct": "4",
            "recommendation": recommendation,
            "concerns": "Arranged by the test.",
        }
    )
    review.action_submit()
    return review


def test_probation_confirmation_extension_and_deemed_permanence(w):
    contract = _contract(
        w.env,
        w.colleague,
        contract_type="probation",
        probation_class="skilled",
        joining_date=TODAY - timedelta(days=30),
        probation_end=TODAY + timedelta(days=30),
        state="active",
    )
    contract.employee_id.write({"user_id": w.hro2.id})
    with pytest.raises(UserError, match="your own"):
        contract.with_user(w.hro2).action_confirm_probation()
    contract.employee_id.write({"user_id": False})
    # M21 capture pass 2: HR decides on the line manager's submitted review
    _reviewed(w, contract, "extend")
    contract.with_user(w.hro).action_extend_probation()
    assert contract.probation_extended and contract.probation_decision == "extended"
    with pytest.raises(UserError, match="already extended"):
        contract.with_user(w.hro).action_extend_probation()
    # past its end with no decision: deemed permanent by the cron (s.4(8))
    contract.write({"probation_end": TODAY - timedelta(days=1)})
    w.env["fix.employment.contract"]._cron_probation_review()
    assert contract.contract_type == "permanent" and contract.probation_decision == "deemed"
    assert _events(w.env, "employee.confirmed", w.colleague.id)[-1]["deemed"] is True
    clerical = _contract(
        w.env,
        _emp(w.env),
        contract_type="probation",
        joining_date=TODAY - timedelta(days=10),
        probation_end=TODAY + timedelta(days=60),
        state="active",
    )
    with pytest.raises(UserError, match="skilled"):
        clerical.with_user(w.hro).action_extend_probation()
    _reviewed(w, clerical, "confirm")
    clerical.with_user(w.hro).action_confirm_probation()
    assert clerical.employee_id.employment_type == "permanent"


def test_fixed_term_expiry_alerts_once_and_expires(w):
    soon = _contract(
        w.env,
        w.colleague,
        contract_type="fixed_term",
        date_end=TODAY + timedelta(days=20),
        state="active",
    )
    gone = _contract(
        w.env,
        _emp(w.env),
        contract_type="fixed_term",
        date_end=TODAY - timedelta(days=1),
        state="active",
    )
    Contract = w.env["fix.employment.contract"]
    Contract._cron_contract_expiry()
    assert soon.expiry_alert_days == 30 and len(soon.activity_ids) == 1
    Contract._cron_contract_expiry()
    assert len(soon.activity_ids) == 1  # idempotent
    assert gone.state == "expired"
    assert _events(w.env, "employment.contract.expired", gone.id)


# ============================================================ movement (M21-3)
def _promotion(c, subject, **vals):
    # A pay change is a new version of the employee's ACTIVE contract and its
    # gross is the sum of the components (M21 audit T1): the subject is on a
    # 30,000-basic contract and is promoted to a 36,000 basic.
    if not c.env["fix.employment.contract"].search(
        [("employee_id", "=", subject.id), ("state", "=", "active")]
    ):
        _contract(c.env, subject, state="active")
    return c.env(user=c.hro.id)["fix.hr.transfer"].create(
        {
            "employee_id": subject.id,
            "movement_type": "promotion",
            "to_manager_id": c.dmgr_emp.id,
            "proposed_gross": 36000,
            "proposed_basic": 36000,
            **vals,
        }
    )


def _through_hr_audit(c, mv):
    mv.with_user(c.mgr).action_recommend()
    mv.with_user(c.dmgr).action_concur()
    mv.with_user(c.hro2).action_hr_audit()


def test_promotion_proper_path_with_distinct_owners(w):
    old = _contract(w.env, w.me, state="active")
    mv = _promotion(w, w.me)
    _through_hr_audit(w, mv)
    with pytest.raises(UserError, match="Finance clearance"):
        mv.with_user(w.hro2).action_request_approval()
    mv.with_user(w.fin).action_finance_approve()
    mv.with_user(w.hro3).action_request_approval()
    with pytest.raises(UserError, match="approver's inbox"):
        mv.with_user(w.execu).action_approve()
    _approve(mv, w.execu)
    assert mv.state == "approved" and mv.executive_user_id == w.execu
    mv.with_user(w.mgr).action_tick_open_jobs()
    mv.with_user(w.assets).action_tick_toolkit()
    mv.with_user(w.assets).action_tick_spare_parts()
    mv.with_user(w.assets).action_tick_storekeeper()
    mv.with_user(w.fin).action_tick_imprest()
    mv.write({"toolkit_challan_no": "CH-1"})
    mv.with_user(w.hro3).action_clear_handover()
    mv.with_user(w.hro3).action_apply()
    assert mv.state == "applied"
    assert w.me.sudo().wage == 36000 and w.me.parent_id == w.dmgr_emp
    assert old.state == "superseded" and mv.new_contract_id.state == "active"
    assert mv.new_contract_id.basic_monthly == 36000
    assert _events(w.env, "salary_structure.changed", mv.new_contract_id.id)
    assert _events(w.env, "employee.moved", mv.id)


def test_one_person_cannot_sign_two_steps(w):
    hrm = _user(w.env, "hr.group_hr_manager", "cd_hr_core.group_hr_finance")
    mv = _promotion(w, w.colleague)  # no line manager: HR recommends
    mv.with_user(hrm).action_recommend()
    with pytest.raises(UserError):
        mv.with_user(hrm).action_concur()
    mv.with_user(w.dmgr).action_concur()
    with pytest.raises(UserError, match="already"):
        mv.with_user(hrm).action_hr_audit()
    # the initiator signs no step either
    with pytest.raises(UserError):
        mv.with_user(w.hro).action_hr_audit()


def test_only_the_line_manager_recommends_their_report(w):
    mv = _promotion(w, w.me)
    with pytest.raises(UserError, match="decided by"):
        mv.with_user(w.hro2).action_recommend()
    mv.with_user(w.mgr).action_recommend()


def test_movement_state_and_approval_cannot_be_written(w, call):
    mv = _promotion(w, w.colleague)
    for vals in (
        {"state": "handover_cleared"},
        {"executive_approval": "approved"},
        {"finance_head_approval": "approved"},
        {"toolkit_returned": True},
        {"executive_id": w.mgr_emp.id},
    ):
        with pytest.raises(UserError, match="changes only through its workflow"):
            _rpc_write(w.env, w.hro, "fix.hr.transfer", mv, vals)
    res = call(
        w.env(user=w.hro.id),
        "model_write",
        model="fix.hr.transfer",
        record_id=mv.id,
        values={"state": "handover_cleared", "executive_approval": "approved"},
    )
    assert not res.get("success"), res
    assert mv.state == "draft"
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_create(
            w.env,
            w.hro,
            "fix.hr.transfer",
            {"employee_id": w.colleague.id, "executive_id": w.mgr_emp.id},
        )


def test_pay_raised_after_approval_is_refused(w):
    mv = _promotion(w, w.me)
    _through_hr_audit(w, mv)
    mv.with_user(w.fin).action_finance_approve()
    mv.with_user(w.hro3).action_request_approval()
    _approve(mv, w.execu)
    with pytest.raises(UserError, match="frozen"):
        _rpc_write(w.env, w.hro, "fix.hr.transfer", mv, {"proposed_gross": 600000})
    with pytest.raises(UserError, match="never returns to draft"):
        mv.with_user(w.hro).action_reset_draft()


def test_self_promotion_is_never_decided_by_the_subject(w):
    own = _emp(w.env, w.execu, parent_id=w.mgr_emp.id)
    mv = _promotion(w, own)
    _through_hr_audit(w, mv)
    mv.with_user(w.fin).action_finance_approve()
    mv.with_user(w.hro3).action_request_approval()
    assert not _task(mv, w.execu)


def test_position_seats_block_dual_occupancy(w):
    seat = w.env["fix.org.position"].create({"name": "M21 Branch Manager"})
    w.colleague.write({"position_id": seat.id})
    with pytest.raises(ValidationError, match="full"), w.env.cr.savepoint():
        _rpc_write(w.env, w.hro, "hr.employee", _emp(w.env), {"position_id": seat.id})
    mv = _promotion(w, w.me, to_position_id=seat.id)
    _through_hr_audit(w, mv)
    mv.with_user(w.fin).action_finance_approve()
    with pytest.raises(UserError, match="full"):
        mv.with_user(w.hro3).action_request_approval()
    seat.write({"headcount": 2})
    mv.with_user(w.hro3).action_request_approval()


# ============================================================ exit (M21-7)
def _exit(c, emp, **vals):
    return c.env(user=c.hro.id)["fix.hr.exit"].create(
        {"employee_id": emp.id, "exit_type": "resignation", **vals}
    )


def _handed_over(c, ex):
    """Arrangement (superuser): the leaver's knowledge handover, accepted
    (M21 capture pass 2: the HR clearance waits for it)."""
    handover = c.env["fix.hr.exit.handover"].create(
        {"exit_id": ex.id, "successor_id": _emp(c.env).id, "open_work": "none"}
    )
    handover.action_hand_over()
    handover.action_accept()
    return handover


def _cleared(c, ex):
    ex.with_user(c.hro2).action_confirm_notice()
    ex.with_user(c.it).action_clear_it()
    ex.with_user(c.fin).action_clear_finance()
    _handed_over(c, ex)
    ex.with_user(c.hro2).action_clear_hr()
    ex.with_user(c.assets).action_clear_assets()
    ex.with_user(c.hro2).action_clear()
    return ex


def _fake_settlement(net):
    def _breakdown(self):
        return {"lines": [("Gratuity", net)], "net": net, "basis": "test hook (I1)"}

    return _breakdown


@pytest.fixture
def payroll_hook(w):
    Exit = type(w.env["fix.hr.exit"])
    holder = {"net": 123456.78}
    with mock.patch.object(
        Exit, "_fix_settlement_breakdown", lambda self: _fake_settlement(holder["net"])(self)
    ):
        yield holder


def test_notice_periods_are_statutory(w):
    _contract(w.env, w.colleague, state="active")
    lwd = TODAY + timedelta(days=60)
    zero = _exit(w, w.colleague, last_working_day=lwd)
    with pytest.raises(UserError, match="notice date"):
        zero.with_user(w.hro2).action_confirm_notice()
    zero.write({"notice_date": lwd - timedelta(days=30)})
    assert (zero.notice_required_days, zero.notice_shortfall_days) == (60, 30)  # s.27 permanent
    with pytest.raises(UserError, match="30 days short"):
        zero.with_user(w.hro2).action_confirm_notice()
    zero.write({"notice_shortfall_treatment": "pay_in_lieu"})
    zero.with_user(w.hro2).action_confirm_notice()
    assert zero.state == "notice"
    other = _emp(w.env)
    _contract(w.env, other, state="active")
    term = _exit(
        w,
        other,
        exit_type="termination",
        notice_date=TODAY,
        last_working_day=TODAY + timedelta(days=60),
        notice_shortfall_treatment="waived",
    )
    assert term.notice_required_days == 120  # s.26, permanent
    with pytest.raises(UserError, match="cannot waive"):
        term.with_user(w.hro2).action_confirm_notice()


def test_retirement_is_at_sixty(w):
    young = _emp(w.env, birthday=TODAY - timedelta(days=365 * 40))
    ex = _exit(w, young, exit_type="retirement")
    with pytest.raises(UserError, match="60 years"):
        ex.with_user(w.hro2).action_confirm_notice()
    old = _emp(w.env, birthday=date(TODAY.year - 61, 1, 1))
    ok = _exit(w, old, exit_type="retirement")
    ok.with_user(w.hro2).action_confirm_notice()
    assert ok.state == "notice"


def test_each_clearance_tick_has_one_owner(w):
    ex = _exit(w, w.colleague, exit_type="contract_end")
    ex.with_user(w.hro2).action_confirm_notice()
    with pytest.raises(UserError, match="Exit Clearance: IT"):
        ex.with_user(w.hro2).action_clear_it()
    with pytest.raises(UserError):
        ex.with_user(w.it).action_clear_finance()
    with pytest.raises(UserError, match="you raised it"):
        ex.with_user(w.hro).action_clear_hr()  # the exit's creator
    for vals in ({"clearance_it": True}, {"state": "settled"}, {"settlement_amount": 9999999}):
        with pytest.raises(UserError, match="changes only through its workflow"):
            _rpc_write(w.env, w.hro, "fix.hr.exit", ex, vals)
    with pytest.raises(UserError, match="ticked by its owner"):
        ex.with_user(w.hro2).action_clear()
    ex.with_user(w.it).action_clear_it()
    assert ex.clearance_it_by_id == w.it


def test_exit_state_cannot_be_forged_through_the_workspace(w, call):
    ex = _exit(w, w.colleague)
    res = call(
        w.env(user=w.hro.id),
        "model_write",
        model="fix.hr.exit",
        record_id=ex.id,
        values={"state": "settled", "settlement_amount": 9999999},
    )
    assert not res.get("success"), res
    res = call(
        w.env(user=w.fin.id),
        "model_action",
        model="fix.hr.exit",
        ids=[ex.id],
        method="action_settle",
    )
    assert not res.get("success")
    assert ex.state == "draft"


def test_settlement_is_payrolls_figure_pinned_and_approved_by_finance(w, payroll_hook):
    contract = _contract(w.env, w.colleague, state="active")
    lwd = TODAY - timedelta(days=1)
    ex = _cleared(w, _exit(w, w.colleague, exit_type="contract_end", last_working_day=lwd))
    with pytest.raises(UserError, match="Compute the settlement"):
        ex.with_user(w.hro2).action_request_approval()
    ex.with_user(w.hro2).action_compute_settlement()
    assert ex.settlement_amount == 123456.78
    ex.with_user(w.hro2).action_request_approval()
    preparer = ex.settlement_computed_by_id
    assert not _task(ex, preparer)
    with pytest.raises(UserError, match="approver's inbox"):
        ex.with_user(w.fin).action_settle()
    _approve(ex, w.fin)
    assert ex.state == "settled" and ex.settled_on == TODAY
    # I3: the contract ends on the last working day, the leaver is recorded once
    assert contract.state == "terminated" and contract.date_end == lwd
    assert w.colleague.left_date == lwd
    assert len(_events(w.env, "employee.left", w.colleague.id)) == 1
    assert w.colleague.keycloak_deprovision_status == "pending"
    assert _events(w.env, "exit.settled", ex.id)[0]["net"] == 123456.78


def test_settlement_changed_after_routing_is_refused(w, payroll_hook):
    _contract(w.env, w.colleague, state="active")
    ex = _cleared(w, _exit(w, w.colleague, exit_type="contract_end"))
    ex.with_user(w.hro2).action_compute_settlement()
    ex.with_user(w.hro2).action_request_approval()
    payroll_hook["net"] = 9999999.0
    task = _task(ex, w.fin)
    with pytest.raises(UserError, match="route it again"):
        task.with_user(w.fin).action_approve()
    assert ex.state == "cleared"


def test_without_payrolls_hook_no_settlement_figure_exists(w):
    if "fix.payroll.period" in w.env:
        # payroll's override is installed: its figures are tested in
        # cd_payroll_bd (test_settlement_breakdown_is_computed_never_typed)
        pytest.skip("cd_payroll_bd is installed and computes the settlement")
    ex = _cleared(w, _exit(w, w.colleague, exit_type="contract_end"))
    with pytest.raises(UserError, match="computed by payroll"):
        ex.with_user(w.hro2).action_compute_settlement()


def test_leaver_recorded_on_the_last_working_day_and_odoo_access_revoked(w):
    leaver_user = _user(w.env)
    emp = _emp(w.env, leaver_user)
    ex = _exit(w, emp, exit_type="contract_end", last_working_day=TODAY - timedelta(days=1))
    ex.with_user(w.hro2).action_confirm_notice()
    Exit = w.env["fix.hr.exit"]
    assert Exit._cron_process_last_working_days() >= 1
    assert emp.left_date == TODAY - timedelta(days=1) and emp.left_at
    assert emp.employment_status == "left"
    assert len(_events(w.env, "employee.left", emp.id)) == 1
    Exit._cron_process_last_working_days()
    assert len(_events(w.env, "employee.left", emp.id)) == 1  # idempotent
    # the relay consumer: a plain user cannot call it ...
    with pytest.raises(AccessError):
        w.env(user=w.plain.id)["hr.employee"].consume_employee_left(
            {"payload": {"employee_id": emp.id}}
        )
    # ... the relay delivers employee.left and the Odoo login is archived
    w.env["fix.event.outbox"].cron_relay()
    assert not leaver_user.active and emp.odoo_access_revoked_at


def test_a_mover_opens_one_access_review_and_changes_no_access(w):
    """C3 (JML mover): a move leaves the old access in place, so the relay
    opens one access review for a person to re-certify; nothing is changed."""
    mover_user = _user(w.env)
    emp = _emp(w.env, mover_user)
    groups_before = mover_user.group_ids
    dept = w.env["hr.department"].create({"name": "A09 Mover Destination"})
    emp.write({"department_id": dept.id})  # announced as employee.moved
    assert _events(w.env, "employee.moved", emp.id)
    with pytest.raises(AccessError):
        w.env(user=w.plain.id)["hr.employee"].consume_employee_moved(
            {"payload": {"employee_id": emp.id}}
        )
    w.env["fix.event.outbox"].cron_relay()
    reviews = emp.activity_ids.filtered(lambda a: a.summary == "Mover access review")
    assert len(reviews) == 1 and mover_user.login in reviews.note
    assert reviews.user_id != mover_user
    # a second move while the review is open does not stack another one
    payload = {"employee_id": emp.id, "from_branch": "Uttara", "to_branch": "Mirpur"}
    assert w.env["hr.employee"].consume_employee_moved({"payload": payload}) is False
    assert mover_user.active and mover_user.group_ids == groups_before


def test_s30_settlement_clock_and_overdue_flag(w):
    ex = _exit(
        w, w.colleague, exit_type="contract_end", last_working_day=TODAY - timedelta(days=60)
    )
    assert ex.settlement_due_date > ex.last_working_day + timedelta(days=30)  # working days
    ex.with_user(w.hro2).action_confirm_notice()
    w.env["fix.hr.exit"]._cron_flag_overdue_settlements()
    assert ex.settlement_overdue
    w.env["fix.hr.exit"]._cron_flag_overdue_settlements()
    assert len(_events(w.env, "exit.settlement.overdue", ex.id)) == 1


def test_dismissal_needs_a_decided_case_and_one_open_exit(w):
    ex = _exit(w, w.colleague, exit_type="dismissal")
    with pytest.raises(UserError, match="disciplinary case"):
        ex.with_user(w.hro2).action_confirm_notice()
    with pytest.raises(ValidationError, match="open exit"):
        _exit(w, w.colleague)


# ============================================================ disciplinary (s.23/24)
def _case(c, emp, **vals):
    return c.env(user=c.hro.id)["fix.hr.disciplinary.case"].create(
        {
            "employee_id": emp.id,
            "allegation": "Missing toolkit",
            "misconduct_category": "theft_fraud",
            **vals,
        }
    )


def test_disciplinary_procedure_follows_s24(w):
    case = _case(w, w.colleague)
    case.with_user(w.hro).action_charge()
    with pytest.raises(UserError, match="at least 7"):
        case.with_user(w.hro).action_hold_hearing()
    case.write({"explanation": "I returned it"})
    case.with_user(w.hro).action_record_explanation()
    case.with_user(w.hro).action_hold_hearing()
    case.write({"employer_rep_ids": [(6, 0, [w.mgr_emp.id])]})
    with pytest.raises(UserError, match="equal numbers"):
        case.with_user(w.hro).action_start_enquiry()
    case.write({"worker_rep_ids": [(6, 0, [w.dmgr_emp.id])]})
    case.with_user(w.hro).action_start_enquiry()
    assert case.enquiry_due == TODAY + timedelta(days=60)
    case.write({"findings": "Proven", "proposed_outcome": "dismissal"})
    case.with_user(w.hro).action_conclude_enquiry()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(w.env, w.hro, "fix.hr.disciplinary.case", case, {"outcome": "exonerated"})
    case.with_user(w.hro).action_request_approval()
    assert not _task(case, w.hro)  # the case officer never decides
    _approve(case, w.execu)
    assert case.state == "decided" and case.outcome == "dismissal"
    assert _events(w.env, "disciplinary.decided", case.id)
    # the decision opened the draft dismissal exit (M21 audit E12); HR confirms it
    ex = w.env["fix.hr.exit"].search([("disciplinary_case_id", "=", case.id)])
    assert len(ex) == 1 and ex.exit_type == "dismissal" and ex.state == "draft"
    ex.with_user(w.hro2).action_confirm_notice()
    assert ex.state == "notice"


def test_suspension_is_capped_and_needs_a_ruled_allowance(w):
    case = _case(w, w.colleague)
    case.with_user(w.hro).action_charge()
    with pytest.raises(UserError, match="not ruled"):
        case.with_user(w.hro).action_suspend()
    # test data standing in for counsel's ruling (a company setting, not code)
    w.env.company.fix_hr_suspension_subsistence_pct = 33.0
    with pytest.raises(UserError, match="at most 60"):
        case.with_user(w.hro).action_suspend(days=61)
    case.with_user(w.hro).action_suspend(days=60)
    assert case.suspended and case.suspended_until == TODAY + timedelta(days=59)
    assert _events(w.env, "employee.suspended", w.colleague.id)[-1]["subsistence_pct"] == 33.0
    case.sudo().write({"suspended_until": TODAY - timedelta(days=1)})  # 60 days on
    w.env["fix.hr.disciplinary.case"]._cron_disciplinary_deadlines()
    assert not case.suspended
    with pytest.raises(ValidationError, match="at least 7"):
        _case(w, _emp(w.env), reply_days=6)


# ============================================================ nominees (M21-12)
def test_nominee_shares_total_at_most_100(w):
    Dep = w.env(user=w.hro.id)["fix.hr.dependant"]
    Dep.create({"employee_id": w.colleague.id, "name": "A", "is_nominee": True, "nominee_pct": 60})
    Dep.create({"employee_id": w.colleague.id, "name": "B", "is_nominee": True, "nominee_pct": 40})
    with pytest.raises(ValidationError, match="exceed 100"):
        Dep.create(
            {"employee_id": w.colleague.id, "name": "C", "is_nominee": True, "nominee_pct": 90}
        )
    with pytest.raises(ValidationError, match="Only a nominee"):
        Dep.create({"employee_id": _emp(w.env).id, "name": "D", "nominee_pct": 10})


# ============================================================ workspace (M21-5, M21-13)
def test_form6a_register_is_a_report_for_hr_and_refused_to_others(w, call):
    out = call(w.env(user=w.hro.id), "model_report", module="M21", report="form6a_register")
    assert "error" not in out and out["rows"]
    out = call(w.env(user=w.plain.id), "model_report", module="M21", report="form6a_register")
    assert "error" in out


def test_kpis_count_employees_with_a_verified_service_book(w):
    """M21-13: the KPI counted documents (+4 for one employee)."""
    before = m21_surfaces.kpis(w.env(user=w.hro.id))["service_books_complete"]
    emp = _emp(w.env)
    for _i in range(3):
        _doc(w.env, w.hro, emp, doc_type="service_book").with_user(w.hro2).action_verify()
    _doc(w.env, w.hro, _emp(w.env), doc_type="service_book")  # unverified: not counted
    after = m21_surfaces.kpis(w.env(user=w.hro.id))["service_books_complete"]
    assert after == before + 1


def test_establishment_register_uses_the_sanctioned_headcount(w, call):
    w.env["fix.org.position"].create({"name": "M21 Seat Of Three", "headcount": 3})
    out = call(w.env(user=w.hro.id), "model_report", module="M21", report="establishment_register")
    row = next(r for r in out["rows"] if r["position"] == "M21 Seat Of Three")
    assert (row["sanctioned"], row["vacant"]) == (3, 3)


# ============================================================ PII reads (M21-4)
def test_plain_employee_reads_only_own_exit_document_dependant(w):
    ex = _exit(w, w.colleague, reason="Health")
    doc = _doc(w.env, w.hro, w.colleague)
    dep = w.env["fix.hr.dependant"].create(
        {
            "employee_id": w.colleague.id,
            "name": "Child",
            "relation": "child",
            "nid": "12345678901234567",
        }
    )
    plain = w.env(user=w.plain.id)
    for rec in (ex, doc, dep):
        assert not plain[rec._name].search([("id", "=", rec.id)])
    own = _doc(w.env, w.hro, w.me)
    assert plain["fix.hr.document"].search([("id", "=", own.id)])


def test_line_manager_reads_own_reports_movement_only(w):
    mine = _promotion(w, w.me)
    other = _promotion(w, w.colleague)
    seen = w.env(user=w.mgr.id)["fix.hr.transfer"].search([("id", "in", (mine | other).ids)])
    assert seen == mine


def test_bank_and_identity_changes_are_tracked(w):
    """M21-9 / BRU-HCM-07: a bank change wrote 0 tracking rows. Tracking is
    written at commit (precommit hook), which the test runs explicitly.

    Round 2: the NID is held in the resident store, so its change is on the
    history as a note naming the field; a tracking row would have copied the
    number into the regional database (old and new value in clear)."""
    target = _emp(w.env)
    w.env.cr.precommit.run()
    Tracking = w.env["mail.tracking.value"].sudo()
    before = Tracking.search_count([("mail_message_id.res_id", "=", target.id)])
    target.with_user(w.hro).write({"routing_number": "222222222", "nid_number": "1234567812"})
    w.env.flush_all()
    w.env.cr.precommit.run()
    rows = Tracking.search([("mail_message_id.res_id", "=", target.id)])
    assert len(rows) > before
    assert "routing_number" in set(rows.mapped("field_id.name"))
    assert "1234567812" not in (rows.mapped("new_value_char") + rows.mapped("old_value_char"))
    notes = target.message_ids.mapped("body")
    assert any("NID recorded" in (b or "") for b in notes)
    assert not any("1234567812" in (b or "") for b in notes)


def test_workspace_form_locks_the_payroll_channel(w, call):
    _contract(w.env, w.colleague, state="active")
    locked = w.colleague._fix_form_locked_fields()
    assert {"bank_account_number", "routing_number", "basic_wage"} <= locked
    assert not ({"bank_account_number", "routing_number"} & _emp(w.env)._fix_form_locked_fields())


def test_hire_draft_from_an_offer_is_accepted_and_gated_at_activation(w):
    """I6 / M58: the hire creates a DRAFT probation contract (offer basic, the
    rest of gross as other_allowance) before the probation end is known."""
    draft = w.env(user=w.hro.id)["fix.employment.contract"].create(
        {
            "employee_id": w.colleague.id,
            "contract_type": "probation",
            "joining_date": str(TODAY),
            "basic_monthly": 24000.0,
            "other_allowance": 12000.0,
        }
    )
    assert draft.state == "draft" and not draft.probation_end
    _signed_off(w, draft)
    with pytest.raises(UserError, match="probation end date"):
        draft.with_user(w.hro2).action_activate()


def test_a_confirmed_and_settled_exit_keeps_its_terms(w, payroll_hook):
    """M21-F7 (A09 probe): the last working day is frozen once the exit is
    confirmed, and the settled amount and date stay as settled."""
    _contract(w.env, w.colleague, state="active")
    ex = _exit(w, w.colleague, exit_type="contract_end", last_working_day=TODAY - timedelta(days=1))
    _cleared(w, ex)
    moved = {"last_working_day": str(TODAY - timedelta(days=200))}
    with pytest.raises(UserError, match="frozen"):
        _rpc_write(w.env, w.hro, "fix.hr.exit", ex, moved)
    ex.with_user(w.hro2).action_compute_settlement()
    ex.with_user(w.hro2).action_request_approval()
    _approve(ex, w.fin)
    assert ex.state == "settled"
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(w.env, w.hro, "fix.hr.exit", ex, {"settlement_amount": 250000})
    with pytest.raises(UserError, match="frozen"):
        _rpc_write(w.env, w.hro, "fix.hr.exit", ex, moved)


def test_an_hr_officer_on_the_payroll_cannot_raise_their_own_pay(w):
    """M21-D9 (A09 probe): pay changes go through a movement or a contract
    version, never a direct write on the master - not even by HR."""
    own = _emp(w.env, w.hro)
    _contract(w.env, own, state="active")
    for vals in ({"wage": 500000.0}, {"basic_wage": 250000.0}):
        with pytest.raises(UserError):
            _rpc_write(w.env, w.hro, "hr.employee", own, vals)
