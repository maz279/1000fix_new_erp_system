"""cd_qms_process — live-ORM behaviour of M23: NCR -> CAPA -> closure,
internal audits and the QC / complaint stub closures (journey 14)."""

from __future__ import annotations

import json
from datetime import date

import pytest
from odoo.exceptions import UserError


def _events(env, event_type, aggregate_id):
    domain = [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)]
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def _ou(env):
    return env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)


def _branch(env, code="QMS01"):
    # the entity lives on a private company (one entity per company: the
    # shared fix_test database serves concurrent suites)
    company = env["res.company"].create({"name": f"M23 QMS {code} Test Co"})
    entity = env["fix.entity"].create(
        {"code": "EN-QMS", "legal_name": "QMS Test Entity", "company_id": company.id}
    )
    return env["fix.branch"].create(
        {"code": code, "name": "Mirpur", "entity_id": entity.id, "operating_unit_id": _ou(env).id}
    )


def _ncr(env, severity="minor", **vals):
    return env["fix.ncr"].create(
        {"source": "audit", "severity": severity, "description": "Torque not logged", **vals}
    )


@pytest.fixture
def owner(odoo_env):
    return odoo_env["hr.employee"].create({"name": "QA Lead Farhana"})


class TestNcrCapa:
    def test_root_cause_then_capa(self, odoo_env, owner):
        ncr = _ncr(odoo_env, "major")
        assert ncr.name.startswith("NCR/")
        assert ncr.state == "new"
        with (
            pytest.raises(UserError, match="Identify the root cause before CAPA"),
            odoo_env.cr.savepoint(),
        ):
            ncr.action_open_capa("Retrain", owner_id=owner.id)
        ncr.action_set_root_cause("Torque driver out of calibration")
        assert (ncr.state, ncr.root_cause) == ("root_cause", "Torque driver out of calibration")
        with (
            pytest.raises(UserError, match="Root cause lands on a NEW NCR"),
            odoo_env.cr.savepoint(),
        ):
            ncr.action_set_root_cause("again")

        capa = ncr.action_open_capa("Recalibrate drivers", "Monthly calibration", owner_id=owner.id)
        assert ncr.state == "capa_open"
        assert ncr.capa_id == capa
        assert (capa.severity, capa.owner_id, capa.corrective_action) == (
            "major",
            owner,
            "Recalibrate drivers",
        )
        assert capa.preventive_action == "Monthly calibration"
        assert _events(odoo_env, "ncr.capa_opened", ncr.id) == [
            {"ncr": ncr.name, "severity": "major"}
        ]

    def test_capa_needs_corrective_action_and_owner(self, odoo_env, owner):
        """Regression: action_open_capa() created fix.capa without its
        required corrective_action / owner_id and failed for every NCR."""
        ncr = _ncr(odoo_env)
        ncr.action_set_root_cause("Process gap")
        with pytest.raises(UserError, match="needs its corrective action"), odoo_env.cr.savepoint():
            ncr.action_open_capa("   ", owner_id=owner.id)
        with pytest.raises(UserError, match="accountable owner"), odoo_env.cr.savepoint():
            ncr.action_open_capa("Fix the process")  # superuser has no employee
        user = odoo_env["res.users"].create({"name": "QA Officer", "login": "qa_officer@qms.test"})
        owner.user_id = user
        capa = ncr.with_user(user).sudo().action_open_capa("Fix the process")
        assert capa.owner_id == owner
        assert capa.preventive_action is False

    def test_capa_gates(self, odoo_env, owner):
        ncr = _ncr(odoo_env, "critical")
        ncr.action_set_root_cause("System: firmware flashing script skips verify")
        capa = ncr.action_open_capa("Patch script", owner_id=owner.id)
        with (
            pytest.raises(UserError, match="requires a PREVENTIVE action"),
            odoo_env.cr.savepoint(),
        ):
            capa.action_implement()
        with (
            pytest.raises(UserError, match="Verify only after implementation"),
            odoo_env.cr.savepoint(),
        ):
            capa.action_verify("too early")
        with (
            pytest.raises(UserError, match="Closure follows verification"),
            odoo_env.cr.savepoint(),
        ):
            capa.action_close()
        capa.preventive_action = "Checksum gate in CI"
        capa.action_implement()
        capa.action_verify("Verified on 20 devices")
        assert (capa.state, capa.verification_note) == ("verified", "Verified on 20 devices")
        # A10 Q1: the verdict travels on the event (an ineffective verdict
        # reopens the CAPA and must reach the consumers the same way)
        assert _events(odoo_env, "capa.verified", capa.id) == [{"ncr": ncr.name, "effective": True}]

        # Regression: closing a CRITICAL NCR read `rec.capa` (no such field)
        # and raised AttributeError instead of applying the CON-11 gate.
        # A10 Q2: the disposition and containment come first — an NCR closed
        # without its ISO 9001 8.7 record is the defect this gate removes.
        ncr.action_dispose("scrap", "Board scrapped under MRB review")
        ncr.containment = "Affected batch quarantined at the bench"
        with (
            pytest.raises(UserError, match="CRITICAL NCR closes only through a VERIFIED"),
            odoo_env.cr.savepoint(),
        ):
            ncr.action_close()
        capa.action_close()
        ncr.action_close()
        assert ncr.state == "closed"
        assert _events(odoo_env, "ncr.closed", ncr.id) == [{"ncr": ncr.name}]

    def test_minor_capa_and_ncr_close_after_disposition(self, odoo_env, owner):
        ncr = _ncr(odoo_env)
        ncr.action_set_root_cause("Operator slip")
        capa = ncr.action_open_capa("Coach operator", owner_id=owner.id)
        capa.action_implement()  # minor: preventive optional
        assert capa.state == "implemented"
        # A10 Q2: even a MINOR NCR closes with its disposition recorded
        with (
            pytest.raises(UserError, match="Record the disposition"),
            odoo_env.cr.savepoint(),
        ):
            ncr.action_close()
        ncr.action_dispose("rework", "Reworked and re-checked")
        ncr.action_close()
        assert ncr.state == "closed"


class TestInternalAudit:
    def _audit(self, env, owner):
        return env["fix.internal.audit"].create(
            {
                "branch_id": _branch(env).id,
                "scheduled_on": date(2026, 11, 3),
                "auditor_id": owner.id,
                "scope": "ISO 9001:2015 clause 8.5 at Mirpur",
            }
        )

    def test_field_execution_and_report(self, odoo_env, owner):
        audit = self._audit(odoo_env, owner)
        audit.action_execute()
        assert (audit.state, audit.offline_payload) == ("executed", False)
        audit.action_execute('{"checklist": "8.5", "ok": 11, "nc": 1}')
        assert audit.offline_payload == '{"checklist": "8.5", "ok": 11, "nc": 1}'
        _ncr(odoo_env, "major", audit_id=audit.id, root_cause="Operator skipped step")
        _ncr(odoo_env, "minor", audit_id=audit.id, root_cause="System label printer")
        _ncr(odoo_env, "critical", audit_id=audit.id)
        assert audit.nccr_systems_traced() is False  # only the MINOR finding names a system
        audit.action_report()
        assert audit.state == "reported"
        assert _events(odoo_env, "audit.reported", audit.id) == [
            {"branch": "Mirpur", "major_findings": 2, "systems_traced": False}
        ]

    def test_major_systems_finding_is_traced(self, odoo_env, owner):
        audit = self._audit(odoo_env, owner)
        _ncr(odoo_env, "major", audit_id=audit.id, root_cause="SYSTEM: ERP allowed skipping QC")
        # A10 Q3: reporting needs the executed checklist evidence
        audit.action_execute('{"checklist": "9.2", "ok": 4, "nc": 1}')
        audit.action_report()
        assert _events(odoo_env, "audit.reported", audit.id)[0]["systems_traced"] is True


class TestStubClosures:
    def _order(self, env):
        brand = env["fix.brand"].create({"name": "Zeltrix QMS Test Brand", "code": "ZQMS"})
        model = env["fix.device.model"].create(
            {"brand_id": brand.id, "name": "ZQ-1", "device_type": "laptop"}
        )
        device = env["fix.device"].create({"device_model_id": model.id})
        customer = env["res.partner"].create({"name": "Nusrat Jahan"})
        return env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": customer.id,
                "branch_id": _branch(env).id,
                "fault_description": "Display flicker",
            }
        )

    def test_failed_qc_raises_a_real_ncr(self, odoo_env):
        order = self._order(odoo_env)
        checklist = odoo_env["fix.qc.checklist"].create({"order_id": order.id})
        checklist.action_fail_with_ncr()
        ncr = checklist.ncr_id
        assert (checklist.state, ncr.source, ncr.severity, ncr.order_id) == (
            "failed",
            "qc",
            "major",
            order,
        )
        assert ncr.description == "QC checklist failed for order %s" % order.name
        assert _events(odoo_env, "qc.ncr_raised", checklist.id) == [{"ncr": ncr.name}]

    def _complaint(self, env, severity):
        return env["fix.complaint"].create(
            {
                "operating_unit_id": _ou(env).id,
                "name": f"CMP-{severity}",
                "customer_id": env["res.partner"].create({"name": "Arif Hossain"}).id,
                "severity": severity,
                "state": "investigating",
                "description": "Device returned with scratches",
            }
        )

    @pytest.mark.parametrize(
        ("severity", "ncr_severity"),
        # A10 S6 (M23-12): severity carries across 1:1 — it used to flatten
        # every non-critical complaint into a MAJOR NCR.
        [("minor", "minor"), ("major", "major"), ("critical", "critical")],
    )
    def test_complaint_links_a_real_ncr(self, odoo_env, severity, ncr_severity):
        complaint = self._complaint(odoo_env, severity)
        complaint.action_raise_ncr()
        ncr = complaint.ncr_id
        assert (ncr.source, ncr.severity, ncr.complaint_id) == (
            "complaint",
            ncr_severity,
            complaint,
        )
        assert complaint.state == "ncr_raised"
        assert complaint.ncr_stub_ref == "NCR-STUB-CLOSED/%s->%s" % (complaint.id, ncr.name)
        assert _events(odoo_env, "complaint.ncr_linked", complaint.id) == [
            {"ncr": ncr.name, "severity": ncr_severity, "stub": False}
        ]

    def test_complaint_without_stub_ref_is_not_backfilled(self, odoo_env, monkeypatch):
        from odoo.addons.cd_cx_feedback.models.fix_cx_feedback import FixComplaint

        def raise_without_stub(self):
            self.write({"state": "ncr_raised"})

        monkeypatch.setattr(FixComplaint, "action_raise_ncr", raise_without_stub)
        complaint = self._complaint(odoo_env, "major")
        complaint.action_raise_ncr()
        assert complaint.ncr_id
        assert complaint.ncr_stub_ref is False


class TestRegisterControls:
    """A10 S6 (M23-9/M23-16, the R1 stragglers): the four framework registers
    — policy, process, checklist, gate — were bare models whose state was a
    typed form input and whose actions flipped it for anyone."""

    def _user(self, env, name, groups=()):
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": name,
                    "login": "qms.reg.%s@a10.test" % name.replace(" ", ".").lower(),
                    "group_ids": [
                        (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                    ],
                }
            )
        )

    def test_policy_approval_is_the_quality_managers_act(self, odoo_env):
        env = odoo_env
        policy = env["fix.qms.policy"].create(
            {"name": "Quality Policy 2026", "year": "2026", "policy_text": "We fix it right."}
        )
        clerk = self._user(env, "Reg Clerk")
        qm = self._user(env, "Reg QM", ("cd_qms_process.group_qms_quality_manager",))
        with (
            pytest.raises(UserError, match="changes only through its workflow"),
            env.cr.savepoint(),
        ):
            policy.with_user(clerk).write({"state": "approved"})
        with pytest.raises(UserError, match="Only the Quality Manager"), env.cr.savepoint():
            policy.with_user(clerk).action_approve()
        with pytest.raises(UserError, match="no policy text"), env.cr.savepoint():
            env["fix.qms.policy"].create({"name": "Empty", "year": "2026"}).action_approve()
        policy.with_user(qm).action_approve()
        assert policy.state == "approved"
        # M23-9: approved text edited in place
        with (
            pytest.raises(UserError, match="cannot be edited in place"),
            env.cr.savepoint(),
        ):
            policy.with_user(qm).write({"policy_text": "We fix it fast."})
        with pytest.raises(UserError, match="approval starts from a draft"), env.cr.savepoint():
            policy.action_approve()  # su passes the gate; the state refuses

    def test_register_states_move_only_through_the_quality_manager(self, odoo_env):
        env = odoo_env
        clerk = self._user(env, "Reg Clerk Two")
        qm = self._user(env, "Reg QM Two", ("cd_qms_process.group_qms_quality_manager",))
        process = env["fix.qms.process"].create({"name": "Bench repair", "code": "PR-BENCH"})
        checklist = env["fix.qms.checklist"].create({"name": "QC bench checklist"})
        # M23 capture audit (2026-11-19): a template is published with its
        # items (FR-QMS-011); one with none is refused
        env["fix.qms.checklist.item"].create(
            {"checklist_id": checklist.id, "name": "Screen intact"}
        )
        gate = env["fix.qms.gate"].create({"name": "Pre-dispatch gate", "code": "GATE-1"})
        for rec, action in (
            (process, "action_retire"),
            (checklist, "action_publish"),
            (gate, "action_retire"),
        ):
            with (
                pytest.raises(UserError, match="changes only through its workflow"),
                env.cr.savepoint(),
            ):
                rec.with_user(clerk).write({"state": "retired"})
            with pytest.raises(UserError, match="Only the Quality Manager"), env.cr.savepoint():
                getattr(rec.with_user(clerk), action)()
        checklist.with_user(qm).action_publish()
        assert checklist.state == "published"
        checklist.with_user(qm).action_retire()
        assert checklist.state == "retired"
        with pytest.raises(UserError, match="only a published checklist"), env.cr.savepoint():
            checklist.action_retire()
        process.with_user(qm).action_retire()
        gate.with_user(qm).action_retire()
        assert (process.state, gate.state) == ("retired", "retired")
        with pytest.raises(UserError, match="already retired"), env.cr.savepoint():
            process.action_retire()
