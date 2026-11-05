# A10 remediation (2026-11-05), S6: the journey-14 hand-offs become real.
#
# The audit's three broken hand-offs, closed here as behaviour:
#   M34 complaint -> NCR  every non-critical complaint landed as a MAJOR
#                      NCR (severity mis-map), and the linkage fields were
#                      plain-writable, so a clerk forged an unrelated CAPA
#                      onto a critical complaint and the closure gate
#                      passed. Severity now carries 1:1, the linkage is
#                      guarded, and the CAPA is the Quality Manager's act
#                      over the real chain (complaint -> NCR -> the CAPA
#                      raised from that NCR).
#   M01 QC checklist -> NCR  a second call on the same failure stacked a
#                      second NCR. The raise is once, and the NCR carries
#                      the checklist's operating unit.
#   M42 supplier CAR -> NCR  a CRITICAL CAR closed with no root cause and
#                      no NCR anywhere. The CAR announces itself through
#                      the event relay; this module's consumer raises the
#                      NCR for the majors — once per CAR.
import itertools
import json

import pytest
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

QM = "cd_qms_process.group_qms_quality_manager"
GUARD = "changes only through its workflow"

_SEQ = itertools.count(1)


def _user(env, name, ou, groups=()):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 S6 %s %d" % (name, n),
                "login": "a10s6.%s.%d@a10.test" % (name.replace(" ", "").lower(), n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
                # the OU isolation rules gate fix.complaint to the user's
                # assigned units — a user holding none can create nothing
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def _ou(env):
    n = next(_SEQ)
    return env["operating.unit"].create(
        {
            "name": "A10 S6 OU %d" % n,
            "code": ("S6-%d" % n)[:16],
            "company_id": env.company.id,
            "partner_id": env["res.partner"].create({"name": "A10 S6 OU %d" % n}).id,
        }
    )


def _branch(env, ou):
    n = next(_SEQ)
    entity = env["fix.entity"].create(
        {
            "legal_name": "A10 S6 Entity %d" % n,
            "code": ("S6E%d" % n)[:10],
            "company_id": env.company.id,
        }
    )
    return env["fix.branch"].create(
        {
            "name": "A10 S6 Branch %d" % n,
            "code": ("S6-BR%d" % n)[:10],
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )


def _complaint(env, user, ou, severity="minor", **vals):
    rec = (
        env["fix.complaint"]
        .with_user(user)
        .create(
            {
                "name": "A10 S6 complaint",
                "customer_id": env["res.partner"]
                .create({"name": "A10 S6 Customer %d" % next(_SEQ)})
                .id,
                "operating_unit_id": ou.id,
                "description": "Same fault twice in one week.",
                "severity": severity,
                **vals,
            }
        )
    )
    rec.with_user(user).action_assess(severity)
    rec.with_user(user).action_investigate()
    return rec


def _order_chain(env, ou):
    n = next(_SEQ)
    brand = env["fix.brand"].create({"name": "A10 S6 Brand %d" % n, "code": ("S6B%d" % n)[:10]})
    model = env["fix.device.model"].create({"name": "A10 S6 Model %d" % n, "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "A10 S6 Order Customer %d" % n})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "A10S6-%d" % n}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": _branch(env, ou).id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "No power",
        }
    )
    return order


@pytest.fixture
def m(odoo_env):
    env = odoo_env
    x = type("M", (), {})()
    x.env = env
    x.ou = _ou(env)
    x.clerk = _user(env, "clerk", x.ou)
    x.qm = _user(env, "qm", x.ou, [QM])
    x.qm_emp = env["hr.employee"].create({"name": "A10 S6 QM", "user_id": x.qm.id})
    x.owner_emp = env["hr.employee"].create({"name": "A10 S6 Owner"})
    return x


# ------------------------------------------- the complaint -> NCR hand-off
def test_the_complaints_ncr_carries_its_severity_one_to_one(m):
    env = m.env
    minor = _complaint(env, m.clerk, m.ou, severity="minor")
    minor.with_user(m.clerk).action_raise_ncr()
    assert minor.state == "ncr_raised"
    assert minor.ncr_id.severity == "minor"  # was always 'major' before
    assert minor.ncr_id.source == "complaint"
    assert minor.ncr_id.complaint_id == minor
    assert minor.ncr_id.operating_unit_id == m.ou
    critical = _complaint(env, m.clerk, m.ou, severity="critical")
    critical.with_user(m.clerk).action_raise_ncr()
    assert critical.ncr_id.severity == "critical"
    # the event says what was raised — the honest severity, not a flat one
    payload = json.loads(
        env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", "complaint.ncr_linked"),
                ("aggregate_id", "=", critical.id),
            ],
            order="id desc",
            limit=1,
        )
        .payload
    )
    assert payload["severity"] == "critical" and payload["stub"] is False
    # the raise is once — a complaint carries one NCR. The base gate refuses
    # the second call (the complaint is already in ncr_raised); the M23 gate
    # refuses it again were the state ever rewound with the NCR still linked.
    with pytest.raises(UserError, match=r"Investigate|already carries its NCR"):
        minor.with_user(m.clerk).action_raise_ncr()
    assert env["fix.ncr"].sudo().search_count([("complaint_id", "=", minor.id)]) == 1


def test_the_complaints_linkage_is_never_typed(m):
    env = m.env
    complaint = _complaint(env, m.clerk, m.ou, severity="critical")
    with pytest.raises(UserError, match=GUARD):
        complaint.with_user(m.clerk).write(
            {
                "ncr_id": env["fix.ncr"]
                .create({"source": "complaint", "severity": "minor", "description": "typed"})
                .id
            }
        )
    with pytest.raises(UserError, match=GUARD):
        complaint.with_user(m.clerk).write({"capa_id": 1})
    complaint.with_user(m.clerk).action_raise_ncr()
    assert complaint.ncr_id  # the action's write, not a typed one


# ------------------------------------------- the complaint -> CAPA hand-off
def _capa(env, ncr, owner_emp, severity="major"):
    return env["fix.capa"].create(
        {
            "ncr_id": ncr.id,
            "severity": severity,
            "corrective_action": "Rework the bench process and re-train",
            "owner_id": owner_emp.id,
        }
    )


def test_the_capa_is_linked_by_the_quality_manager_over_the_real_chain(m):
    env = m.env
    complaint = _complaint(env, m.clerk, m.ou, severity="critical")
    complaint.with_user(m.clerk).action_raise_ncr()
    capa = _capa(env, complaint.ncr_id, m.owner_emp)
    # no NCR, no link: the CAPA closes the loop the NCR opens
    fresh = _complaint(env, m.clerk, m.ou, severity="critical")
    with pytest.raises(UserError, match="Raise the NCR"):
        fresh.with_user(m.qm).action_link_capa(capa_id=capa.id)
    # not the clerk's act — the Quality Manager's
    with pytest.raises(UserError, match="Only the Quality Manager"):
        complaint.with_user(m.clerk).action_link_capa(capa_id=capa.id)
    # an unrelated CAPA — raised from ANOTHER NCR — never satisfies the gate
    other_ncr = env["fix.ncr"].create(
        {"source": "service_order", "severity": "major", "description": "Unrelated"}
    )
    other_capa = _capa(env, other_ncr, m.owner_emp)
    with pytest.raises(UserError, match="not to"):
        complaint.with_user(m.qm).action_link_capa(capa_id=other_capa.id)
    assert not complaint.capa_id
    # the real chain links — by id, or by taking the NCR's only CAPA
    complaint.with_user(m.qm).action_link_capa()
    assert complaint.capa_id == capa
    # and the closure gate now reads the CAPA's REAL state, not a reference
    assert complaint._capa_closure_denial() == "linked CAPA is 'open', not verified"


# ------------------------------------------- the QC checklist -> NCR raise
def test_a_failed_checklist_raises_one_ncr_for_its_unit(m):
    env = m.env
    order = _order_chain(env, m.ou)
    checklist = env["fix.qc.checklist"].create({"order_id": order.id, "operating_unit_id": m.ou.id})
    checklist.action_fail_with_ncr()
    first = checklist.ncr_id
    assert (checklist.state, first.source, first.severity) == ("failed", "qc", "major")
    assert first.operating_unit_id == m.ou  # was blank before
    # the relay's reality: the second call returns the same NCR, not a second
    checklist.action_fail_with_ncr()
    assert checklist.ncr_id == first
    assert (
        env["fix.ncr"].sudo().search_count([("order_id", "=", order.id), ("source", "=", "qc")])
        == 1
    )


# ------------------------------------------- the supplier CAR -> NCR relay
def _car_event(env, car_name, car_id, severity, supplier="A10 S6 Supplier"):
    publish(
        env,
        "supplier.car.raised",
        "fix.supplier.car",
        car_id,  # aggregate_id is the integer id; the NAME travels in the payload
        {
            "car": car_name,
            "supplier_id": 1,
            "supplier": supplier,
            "issue": "Shipment failed incoming inspection",
            "severity": severity,
            "due": "2026-12-01",
        },
        metadata={"module": "TEST", "reason": "A10 S6"},
    )


def test_a_major_supplier_car_becomes_an_ncr_once(m):
    env = m.env
    # the wiring is registered, not implied
    consumers = (
        env["fix.event.consumer"].sudo().search([("event_type", "=", "supplier.car.raised")])
    )
    assert {c.method for c in consumers} >= {"consume_supplier_car_raised"}
    _car_event(env, "SCAR/4211", 4211, "critical")
    handled = env["fix.event.outbox"].sudo().cron_relay()
    assert handled >= 1
    ncr = env["fix.ncr"].sudo().search([("car_ref", "=", "SCAR/4211")])
    assert len(ncr) == 1
    assert (ncr.source, ncr.severity) == ("supplier", "critical")
    assert "Shipment failed incoming inspection" in ncr.description
    # redelivery changes nothing — one NCR per CAR
    _car_event(env, "SCAR/4211", 4211, "critical")
    env["fix.event.outbox"].sudo().cron_relay()
    assert len(env["fix.ncr"].sudo().search([("car_ref", "=", "SCAR/4211")])) == 1
    # a minor CAR is coaching, not a non-conformance record
    _car_event(env, "SCAR/4212", 4212, "minor")
    env["fix.event.outbox"].sudo().cron_relay()
    assert not env["fix.ncr"].sudo().search([("car_ref", "=", "SCAR/4212")])
    # the consumer is the relay's, not an RPC
    with pytest.raises(AccessError, match="run only from the event relay"):
        env["fix.ncr"].with_user(m.clerk).consume_supplier_car_raised(
            {
                "event_type": "supplier.car.raised",
                "aggregate": "fix.supplier.car",
                "aggregate_id": 4211,
                "payload": {"car": "SCAR/4211", "severity": "major"},
                "company_id": env.company.id,
            }
        )
