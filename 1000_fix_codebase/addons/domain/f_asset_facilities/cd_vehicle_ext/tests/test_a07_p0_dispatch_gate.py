"""A07 audit P0 (E3), M46 Fleet & Vehicles: the dispatch gate as controls.

The A07 workflow audit (2026-11-03, working/A07_evidence/probes/m46/
probe_m46.py) found the gate read only the two header dates on fleet.vehicle:
an expired insurance / tax-token DOCUMENT, an open off-road record, a failed
brake check, an open accident and a suspended or expired-licence driver were
all assigned; typing a future insurance date made an uninsured van
dispatchable; write() bypassed the gate and the overlap check; and the stored
is_valid stayed True after a document expired.

Every control is tested both ways, as NON-ADMIN users created here: the
bypass is refused, and the legitimate path still works. ``odoo_env``
(addons/conftest.py) rolls back after every test.
"""

import base64
import types
from datetime import timedelta

import pytest
from odoo.addons.cd_vehicle_ext.models.fix_vehicle import MANDATORY_DOCS_PARAM, PREUSE_PARAM
from odoo.addons.cd_vehicle_ext.models.fix_vehicle_ops import dhaka_today
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import Error as PgError

REFUSED = (UserError, ValidationError, AccessError, PgError)
# A07 P1 (FR-FLT-009 / AC-21): a document counts only with its evidence scan,
# so the fixture's documents carry one (fixture updated for P1).
SCAN = base64.b64encode(b"%PDF-1.4 scanned certificate").decode()


def refused(env, fn):
    """The refusal text, or None when fn() went through (rolled back to a
    savepoint either way)."""
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED as exc:
        return str(exc)
    return None


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)

    def user(login, groups=()):
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "group_ids": [
                        (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                    ],
                    "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                    "default_operating_unit_id": ou.id,
                }
            )
        )

    x = types.SimpleNamespace(env=env, ou=ou)
    x.today = dhaka_today(env["fix.vehicle.check"])
    x.clerk = user("a07p0m46_clerk")
    x.fleet = user("a07p0m46_fleet", ["fleet.fleet_group_user"])
    # A07 P1: closing a claim is the Logistics Manager's
    x.lm = user("a07p0m46_lm", ["cd_vehicle_ext.group_logistics_manager"])
    brand = env["fleet.vehicle.model.brand"].create({"name": "A07P0 Brand"})
    x.model = env["fleet.vehicle.model"].create({"name": "A07P0 Van", "brand_id": brand.id})

    def driver(name, **kw):
        emp = env["hr.employee"].create({"name": name})
        vals = {
            "name": name,
            "employee_id": emp.id,
            "license_no": "DL-" + name,
            "license_expiry": x.today + timedelta(days=400),
        }
        vals.update(kw)
        return env["fix.driver"].create(vals)

    def vehicle(plate, docs=("fitness", "insurance", "tax"), days=200, **kw):
        """A van with the given statutory documents valid for `days` more days."""
        vals = {"model_id": x.model.id, "license_plate": plate, "operating_unit_id": ou.id}
        vals.update(kw)
        v = env["fleet.vehicle"].create(vals)
        for doc_type in docs:
            doc(v, doc_type, x.today + timedelta(days=days))
        return v

    def doc(v, doc_type, valid_to, scan=True, **kw):
        vals = {"vehicle_id": v.id, "doc_type": doc_type, "number": "N-" + doc_type}
        vals.update({"valid_to": valid_to, **kw})
        if scan:
            vals.setdefault("evidence_file", SCAN)
        return env["fix.vehicle.document"].with_user(x.fleet).create(vals)

    def assign(v, user=None, day=None, **kw):
        vals = {"vehicle_id": v.id, "date": day or x.today, "operating_unit_id": ou.id}
        vals.update(kw)
        return env["fix.vehicle.assignment"].with_user(user or x.clerk).create(vals)

    x.driver, x.vehicle, x.doc, x.assign = driver, vehicle, doc, assign
    x.good = vehicle("A07P0-GOOD")
    return x


# ------------------------------------------------------------ the register decides
def test_compliant_van_is_assigned_by_a_plain_user(w):
    a = w.assign(w.good)
    assert a.vehicle_id == w.good
    assert w.good.with_user(w.clerk).action_assert_dispatchable() is True
    assert w.good.compliance_ok and not w.good.dispatch_blockers


@pytest.mark.parametrize("doc_type", ["fitness", "insurance", "tax"])
def test_missing_or_expired_mandatory_document_refuses(w, doc_type):
    others = [t for t in ("fitness", "insurance", "tax") if t != doc_type]
    missing = w.vehicle("A07P0-MISS-" + doc_type, docs=others)
    assert "no valid" in refused(w.env, lambda: w.assign(missing))
    expired = w.vehicle("A07P0-EXP-" + doc_type, docs=others)
    w.doc(expired, doc_type, w.today - timedelta(days=1), state="expired")
    assert refused(w.env, lambda: w.assign(expired))
    # an expired copy does not hide a valid renewal on file
    w.doc(expired, doc_type, w.today + timedelta(days=30))
    assert w.assign(expired)


def test_header_dates_are_information_only(w):
    """M46-3 / BRU-FLT-03: typing a future insurance date is no override.
    A07 P1: the header dates are read from the register and cannot be typed."""
    v = w.vehicle("A07P0-HDR", docs=("fitness", "tax"))
    assert "register" in refused(
        w.env,
        lambda: v.with_user(w.fleet).write({"insurance_expiry": w.today + timedelta(days=365)}),
    )
    assert "Insurance" in refused(w.env, lambda: w.assign(v))
    assert not v.compliance_ok and not v.insurance_expiry
    # the register decides, and the header follows it
    ins = w.doc(v, "insurance", w.today + timedelta(days=120))
    assert v.insurance_expiry == ins.valid_to and w.assign(v)


def test_documents_must_cover_the_assignment_day(w):
    v = w.vehicle("A07P0-SHORT", days=3)
    assert w.assign(v, day=w.today + timedelta(days=2))
    assert "ended on" in refused(w.env, lambda: w.assign(v, day=w.today + timedelta(days=10)))


def test_document_not_yet_in_force_is_not_valid(w):
    v = w.vehicle("A07P0-FUTURE", docs=("fitness", "tax"))
    w.doc(v, "insurance", w.today + timedelta(days=300), valid_from=w.today + timedelta(days=5))
    assert refused(w.env, lambda: w.assign(v))


def test_registration_type_exists_and_is_switchable(w):
    keys = dict(w.env["fix.vehicle.document"]._fields["doc_type"].selection)
    assert "registration" in keys
    assert w.assign(w.good)  # not mandatory by default
    w.env["ir.config_parameter"].sudo().set_param(
        MANDATORY_DOCS_PARAM, "fitness,insurance,tax_token,registration"
    )
    v = w.vehicle("A07P0-REG")
    assert "Registration" in refused(w.env, lambda: w.assign(v))
    w.doc(v, "registration", w.today + timedelta(days=900))
    assert w.assign(v)


# ------------------------------------------------------------ operational blockers
def test_open_offroad_refuses_until_returned(w):
    off = (
        w.env["fix.vehicle.offroad"]
        .with_user(w.clerk)
        .create({"vehicle_id": w.good.id, "reason": "Brake failure"})
    )
    assert "off-road" in refused(w.env, lambda: w.assign(w.good))
    # A07 P0 recipe M46-8: a passed re-check, and a person other than the opener
    w.env["fix.vehicle.check"].with_user(w.clerk).create(
        {
            "vehicle_id": w.good.id,
            "tyres_ok": True,
            "lights_ok": True,
            "fluids_ok": True,
            "brakes_ok": True,
        }
    )
    off.with_user(w.fleet).action_return()
    assert w.assign(w.good)


@pytest.mark.parametrize("state", ["reported", "claimed"])
def test_open_accident_refuses(w, state):
    acc = (
        w.env["fix.vehicle.accident"]
        .with_user(w.clerk)
        .create({"vehicle_id": w.good.id, "description": "Side collision", "claim_ref": "CL-1"})
    )
    if state == "claimed":
        acc.action_claim()
    assert "open accident" in refused(w.env, lambda: w.assign(w.good))
    if state == "claimed":
        # A07 P0 recipe M46-10: closed by someone other than the reporter;
        # A07 P1: a Logistics Manager, with the insurer and the evidence. The
        # accident also took the van off-road: a re-check and a return follow.
        insurer = w.env["res.partner"].create({"name": "A07P0 Insurer"})
        acc.with_user(w.clerk).write({"insurer_id": insurer.id, "evidence_file": SCAN})
        acc.with_user(w.lm).action_close(settlement=0)
        assert "off-road" in refused(w.env, lambda: w.assign(w.good))
        w.env["fix.vehicle.check"].with_user(w.clerk).create(
            {
                "vehicle_id": w.good.id,
                "tyres_ok": True,
                "lights_ok": True,
                "fluids_ok": True,
                "brakes_ok": True,
            }
        )
        w.env["fix.vehicle.offroad"].search(
            [("vehicle_id", "=", w.good.id), ("state", "=", "offroad")]
        ).with_user(w.fleet).action_return()
        assert w.assign(w.good)


def test_failed_check_today_refuses_but_yesterdays_does_not(w):
    """A07 P1 (BRU-FLT-04, AUT-FLT-08): yesterday's failed check no longer
    lapses at midnight: it took the vehicle off-road, until a passed re-check
    and a return to service by someone else. Today's failure refuses too."""
    Check = w.env["fix.vehicle.check"].with_user(w.clerk)
    Check.create(
        {"vehicle_id": w.good.id, "brakes_ok": False, "checked_on": w.today - timedelta(days=1)}
    )
    tomorrow = w.today + timedelta(days=1)
    assert "off-road" in refused(w.env, lambda: w.assign(w.good, day=tomorrow))
    Check.create(
        {
            "vehicle_id": w.good.id,
            "tyres_ok": True,
            "lights_ok": True,
            "fluids_ok": True,
            "brakes_ok": True,
        }
    )
    w.env["fix.vehicle.offroad"].search(
        [("vehicle_id", "=", w.good.id), ("state", "=", "offroad")]
    ).with_user(w.fleet).action_return()
    assert w.assign(w.good, day=tomorrow)
    Check.create({"vehicle_id": w.good.id, "brakes_ok": False, "defects": "No brakes"})
    assert "pre-use check" in refused(w.env, lambda: w.assign(w.good))


def test_passed_check_required_only_when_switched_on(w):
    assert w.assign(w.good)  # default off
    v = w.vehicle("A07P0-PREUSE")
    w.env["ir.config_parameter"].sudo().set_param(PREUSE_PARAM, "True")
    assert "no passed pre-use check" in refused(w.env, lambda: w.assign(v))
    # a future day cannot have today's check yet: not required for it
    assert w.assign(v, day=w.today + timedelta(days=1))
    # A07 P0 recipe M46-7: each item answered OK (they no longer default to True)
    w.env["fix.vehicle.check"].with_user(w.clerk).create(
        {
            "vehicle_id": v.id,
            "tyres_ok": True,
            "lights_ok": True,
            "fluids_ok": True,
            "brakes_ok": True,
        }
    )
    assert w.assign(v)


# ------------------------------------------------------------------ the driver
def test_driver_suspended_or_licence_expired_refuses(w):
    d = w.driver("A07P0 Drv")
    assert w.assign(w.good, driver_id=d.id).driver_id == d
    v2 = w.vehicle("A07P0-DRV2")
    d.license_expiry = w.today - timedelta(days=1)
    assert "licence expired" in refused(w.env, lambda: w.assign(v2, driver_id=d.id))
    d.license_expiry = False
    assert "no licence expiry" in refused(w.env, lambda: w.assign(v2, driver_id=d.id))
    d.license_expiry = w.today + timedelta(days=30)
    d.action_suspend(reason="A07 P0 test")  # A07 P0 recipe M46-6: a reason
    assert "suspended" in refused(w.env, lambda: w.assign(v2, driver_id=d.id))


def test_vehicle_driver_is_the_default_driver(w):
    """BRU-FLT-06: no driver given = the vehicle's assigned driver, and gated."""
    d = w.driver("A07P0 Default", license_expiry=w.today - timedelta(days=3))
    w.good.fix_driver_id = d
    assert "licence expired" in refused(w.env, lambda: w.assign(w.good))
    assert "licence expired" in refused(
        w.env, lambda: w.good.with_user(w.clerk).action_assert_dispatchable()
    )
    # A07 P1 (AUT-FLT-05): registered with a lapsed licence, the driver was
    # born suspended; the renewal is recorded, then an officer reinstates.
    assert d.state == "suspended"
    d.license_expiry = w.today + timedelta(days=100)
    d.with_user(w.fleet).action_reinstate(reason="Licence renewed")
    assert w.assign(w.good).driver_id == d


# ------------------------------------------------------------ write() (M46-4)
def test_write_cannot_repoint_to_a_blocked_vehicle(w):
    bad = w.vehicle("A07P0-BAD", docs=("fitness", "tax"))
    a = w.assign(w.good)
    assert refused(w.env, lambda: a.with_user(w.clerk).write({"vehicle_id": bad.id}))
    suspended = w.driver("A07P0 Susp", state="suspended")
    assert refused(w.env, lambda: a.with_user(w.clerk).write({"driver_id": suspended.id}))
    # a field outside the vehicle gate still saves; BRU-HSE-07 (merged with
    # A09) still demands the repointed technician hold a valid licence.
    tech = w.driver("A07P0 Tech", license_class="Light")
    a.with_user(w.clerk).write({"technician_id": tech.employee_id.id})
    assert a.technician_id == tech.employee_id


def test_write_cannot_double_book_a_day(w):
    w.assign(w.good)
    b = w.assign(w.good, day=w.today + timedelta(days=1))
    assert "overlaps are refused" in refused(
        w.env, lambda: b.with_user(w.clerk).write({"date": w.today})
    )
    b.with_user(w.clerk).write({"date": w.today + timedelta(days=2)})
    assert b.date == w.today + timedelta(days=2)


def test_overlap_is_seen_across_operating_units(w):
    """The overlap count runs as superuser: an OU the caller cannot read is
    still the van's other place."""
    other_ou = w.env["operating.unit"].create(
        {"name": "A07P0 OU2", "code": "A7P2", "partner_id": w.env.company.partner_id.id}
    )
    w.env["fix.vehicle.assignment"].create(
        {"vehicle_id": w.good.id, "date": w.today, "operating_unit_id": other_ou.id}
    )
    assert "overlaps are refused" in refused(w.env, lambda: w.assign(w.good))


# ----------------------------------------------------- documents (M46-5, D9)
def test_is_valid_follows_the_clock_and_is_searchable(w):
    d = w.doc(w.good, "other", w.today + timedelta(days=5))
    assert d.is_valid
    Doc = w.env["fix.vehicle.document"]
    assert d in Doc.search([("is_valid", "=", True)])
    w.env.flush_all()
    w.env.cr.execute(
        "UPDATE fix_vehicle_document SET valid_to=%s WHERE id=%s",
        (w.today - timedelta(days=3), d.id),
    )
    w.env.invalidate_all()
    assert not d.is_valid
    assert d not in Doc.search([("is_valid", "=", True)])
    assert d in Doc.search([("is_valid", "=", False)])
    assert not Doc._fields["is_valid"].store


def test_plain_user_cannot_revive_an_expired_document(w):
    d = w.doc(w.good, "fitness", w.today - timedelta(days=20), state="expired", scan=False)
    msg = refused(
        w.env,
        lambda: d.with_user(w.clerk).write(
            {"state": "valid", "valid_to": w.today + timedelta(days=365)}
        ),
    )
    assert "cannot be made valid again" in msg
    # a lapsed-by-date document cannot be pushed out either
    stale = w.doc(w.good, "insurance", w.today + timedelta(days=5))
    w.env.flush_all()
    w.env.cr.execute(
        "UPDATE fix_vehicle_document SET valid_to=%s WHERE id=%s",
        (w.today - timedelta(days=1), stale.id),
    )
    w.env.invalidate_all()
    assert refused(
        w.env,
        lambda: stale.with_user(w.fleet).write({"valid_to": w.today + timedelta(days=300)}),
    )
    # marking it expired, editing its number, and recording the renewal all work
    # (A07 P1: the Fleet Officer keeps the register; a plain employee reads it)
    assert refused(w.env, lambda: stale.with_user(w.clerk).action_expire())
    stale.with_user(w.fleet).action_expire()  # A07 P0 recipe: state is guarded
    d.with_user(w.fleet).write({"number": "FIT-OLD-1"})
    assert w.doc(w.good, "fitness", w.today + timedelta(days=365)).is_valid
    # superuser data loading stays trusted
    d.sudo().write(
        {"state": "valid", "valid_to": w.today + timedelta(days=1), "evidence_file": SCAN}
    )
    assert d.is_valid
