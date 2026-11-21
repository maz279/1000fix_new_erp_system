"""Shared fixtures for the A05 M18 behaviour tests (cd_ewaste).

Every actor is a freshly created NON-ADMIN user holding only the role groups
its step needs: the superuser is trusted by the field guard and would hide a
gap. P03 calls go through the real controller functions with request.env
bound to the acting user. The odoo_env fixture rolls everything back.
"""

import base64
import itertools
import types
from datetime import timedelta

from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
_SEQ = itertools.count(1)

G = types.SimpleNamespace(
    assessor="cd_ewaste.group_ewaste_triage_assessor",
    hse="cd_ewaste.group_ewaste_hse_officer",
    dispatcher="cd_ewaste.group_ewaste_dispatcher",
    recycler_approver="cd_ewaste.group_ewaste_recycler_approver",
    compliance="cd_ewaste.group_ewaste_compliance_officer",
    finance="cd_ewaste.group_ewaste_finance_approver",
    verifier="cd_data_case.group_wipe_verifier",
)


def refused(env, fn):
    """Run fn in a savepoint; return the refusal (or None if it went through)."""
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED as exc:
        return exc
    return None


def make_user(env, login, groups=(), employee=False, company=None):
    n = next(_SEQ)
    company = company or env.company
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    vals = {
        "name": "M18 %s %d" % (login, n),
        "login": "a05m18.%s.%d@a05.test" % (login, n),
        "group_ids": [(6, 0, ids)],
        "company_id": company.id,
        "company_ids": [(6, 0, [company.id])],
    }
    if ou:
        vals.update({"operating_unit_ids": [(6, 0, ou.ids)], "default_operating_unit_id": ou.id})
    user = env["res.users"].with_context(no_reset_password=True).create(vals)
    assert not user.has_group("base.group_system")
    if employee:
        env["hr.employee"].create({"name": user.name, "user_id": user.id, "company_id": company.id})
    return user


def attachment(env, name="evidence.pdf", raw=b"evidence"):
    return env["ir.attachment"].create({"name": name, "datas": base64.b64encode(raw)})


class M18:
    def __init__(self, env):
        self.env = env
        self.clerk = make_user(env, "clerk")
        self.clerk2 = make_user(env, "clerk2")
        self.assessor = make_user(env, "assessor", [G.assessor], employee=True)
        self.hse = make_user(env, "hse", [G.hse])
        self.dispatcher = make_user(env, "dispatcher", [G.dispatcher])
        self.approver = make_user(env, "approver", [G.recycler_approver])
        self.compliance = make_user(env, "compliance", [G.compliance])
        self.compliance2 = make_user(env, "compliance2", [G.compliance])
        self.cfo = make_user(env, "cfo", [G.finance])
        self.verifier = make_user(env, "verifier", [G.verifier])
        self.customer = env["res.partner"].create({"name": "M18 Donor"})
        brand = env["fix.brand"].create({"name": "M18Brand", "code": "M18BR%d" % next(_SEQ)})
        self.dmodel = env["fix.device.model"].create({"name": "M18 Phone", "brand_id": brand.id})
        self.today = fields.Date.context_today(env["res.users"])
        self.n = 0
        import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

        self._g = g
        self._ctl = g.P03GenericApiController()
        self._saved = getattr(g, "request", None)

    def close(self):
        self._g.request = self._saved

    # ------------------------------------------------------------ P03
    def p03_write(self, user, model, rec_id, values):
        g = self._g
        g.request = types.SimpleNamespace(env=self.env(user=user.id))
        fn = getattr(
            g.P03GenericApiController.model_write,
            "original_endpoint",
            g.P03GenericApiController.model_write,
        )
        return fn(self._ctl, model=model, record_id=rec_id, values=values)

    def p03_action(self, user, model, ids, method, kwargs=None):
        g = self._g
        g.request = types.SimpleNamespace(env=self.env(user=user.id))
        fn = getattr(
            g.P03GenericApiController.model_action,
            "original_endpoint",
            g.P03GenericApiController.model_action,
        )
        return fn(self._ctl, model=model, ids=ids, method=method, kwargs=kwargs)

    # ------------------------------------------------------------ records
    def as_(self, user, rec):
        return rec.with_user(user)

    def device(self):
        self.n += 1
        return self.env["fix.device"].create(
            {
                "device_model_id": self.dmodel.id,
                "serial_number": "M18-SN-%04d-%d" % (self.n, next(_SEQ)),
            }
        )

    def collection(self, user=None, **vals):
        vals.setdefault("customer_id", self.customer.id)
        vals.setdefault("weight_kg", 0.5)
        return self.env["fix.ewaste.collection"].with_user(user or self.clerk).create(vals)

    def verified_cert(self, serial):
        log = self.env["ir.attachment"].create(
            {"name": "shred.log", "raw": b"run %s: PASS" % serial.encode()}
        )
        cert = (
            self.env["fix.data.wipe.certificate"]
            .with_user(self.clerk)
            .create(
                {
                    "method": "physical_destruction",
                    "wipe_log_attachment_id": log.id,
                    "serial_number": serial,
                }
            )
        )
        cert.with_user(self.verifier).action_verify()
        assert cert.sanitization_status == "verified"
        return cert

    def triage(self, col, grade="recycle", **vals):
        return (
            self.env["fix.ewaste.triage"]
            .with_user(self.assessor)
            .create({"collection_id": col.id, "decision": grade, **vals})
        )

    def ready_item(self, weight=0.5, material="phone"):
        """A data-bearing phone, triaged, destroyed under a verified M06
        certificate and released for the recycler ('recycled')."""
        dev = self.device()
        col = self.collection(device_id=dev.id, weight_kg=weight, material_type=material)
        cert = self.verified_cert(dev.serial_number)
        self.triage(col, "recycle", data_bearing=True)
        col.with_user(self.clerk).write({"wipe_certificate_id": cert.id})
        # A05 S3 M18-28: destruction and release are the floor's (dispatcher)
        col.with_user(self.dispatcher).action_secure_destruction()
        col.with_user(self.dispatcher).action_recycle_estimated()
        assert col.state == "recycled"
        return col

    def partner(self, user=None, **vals):
        vals.setdefault("name", "M18 Recycler %d" % next(_SEQ))
        vals.setdefault("certification", "doe")
        vals.setdefault("certificate_no", "DOE-LIC-%d" % next(_SEQ))
        vals.setdefault("valid_from", self.today - timedelta(days=30))
        vals.setdefault("valid_to", self.today + timedelta(days=300))
        vals.setdefault("licence_attachment_id", attachment(self.env, "licence.pdf").id)
        # A05 S3 M18-06: a recycler is qualified with its business contact
        if "partner_id" not in vals:
            vals["partner_id"] = (
                self.env["res.partner"].create({"name": "%s (contact)" % vals["name"]}).id
            )
        # A05 S3 M18-22: registered by the e-waste floor, not any user
        p = self.env["fix.ewaste.partner"].with_user(user or self.dispatcher).create(vals)
        # capture pass 2 (BRU-ESG-18): where its material goes next is
        # declared at qualification
        self.downstream(p)
        return p

    def downstream(self, partner, material="all", user=None, **vals):
        return (
            self.env["fix.ewaste.partner.downstream"]
            .with_user(user or self.dispatcher)
            .create(
                {
                    "partner_id": partner.id,
                    "name": "M18 Smelter %d" % next(_SEQ),
                    "material_class": material,
                    "evidence_attachment_id": attachment(self.env, "downstream.pdf").id,
                    **vals,
                }
            )
        )

    def approved_partner(self, **vals):
        p = self.partner(**vals)
        approve_via_inbox(p, self.approver, requester=self.dispatcher)
        assert p.state == "active", p.state
        # ... and verified by an approver who did not declare it (FR-ESG-024)
        p.downstream_ids.with_user(self.approver).action_verify()
        return p

    def batch(self, partner=None, material="phone", **vals):
        return (
            self.env["fix.ewaste.batch"]
            .with_user(self.dispatcher)
            .create(
                {
                    "partner_id": (partner or self.approved_partner()).id,
                    "material_type": material,
                    **vals,
                }
            )
        )

    def dispatched_batch(self, items=None, partner=None):
        items = items or [self.ready_item()]
        b = self.batch(partner=partner)
        b.action_load_ready_items()
        assert set(items) <= set(b.collection_ids), (items, b.collection_ids)
        self.weigh_out(b)
        b.action_dispatch()
        assert b.state == "dispatched"
        return b

    def weigh_out(self, batch, net=None):
        """A05 S3 M18-16: the outbound weighbridge ticket, before dispatch."""
        net = batch.weight_kg if net is None else net
        batch.with_user(self.dispatcher).write(
            {
                "outbound_ticket_ref": "WB-OUT-%d" % next(_SEQ),
                "outbound_gross_kg": net + 10.0,
                "outbound_tare_kg": 10.0,
            }
        )
        return batch

    def processed_batch(self, items=None, partner=None):
        b = self.dispatched_batch(items, partner)
        b.write({"received_weight_kg": b.weight_kg, "recycler_receipt_ref": "RCV-1"})
        b.action_receive()
        b.write({"processing_evidence_id": attachment(self.env, "processed.pdf").id})
        b.action_process()
        assert b.state == "processed"
        return b

    def issued_certificate(self, batch=None):
        batch = batch or self.processed_batch()
        batch.action_record_certificate()
        cert = batch.certificate_ids
        cert.with_user(self.dispatcher).write(
            {
                "certificate_no": "REC-CERT-1",
                "recycler_stated_weight_kg": batch.processed_weight_kg,
                "evidence_attachment_id": attachment(self.env, "cert.pdf").id,
            }
        )
        cert.with_user(self.compliance).action_issue()
        assert cert.state == "issued"
        return cert

    def registration(self):
        reg = (
            self.env["fix.ewaste.registration"]
            .with_user(self.compliance)
            .create(
                {
                    "registration_no": "DOE-EW-REG-1",
                    "valid_from": self.today - timedelta(days=10),
                    "valid_to": self.today + timedelta(days=365),
                    "evidence_attachment_id": attachment(self.env, "reg.pdf").id,
                }
            )
        )
        reg.with_user(self.compliance2).action_activate()
        return reg


def events(env, event_type, aggregate_id):
    return env["fix.event.outbox"].search_count(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)]
    )
