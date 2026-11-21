"""A07 ERP audit (2026-11-20), stream M46: the fixes, attacked on the live ORM
as NON-ADMIN users holding the role they would really hold (``odoo_env``
rolls back). Each refusal is paired with the proper path.

Owner decision D14 switches as the lead seeds them: require_fuel_receipt ON,
pm_overdue_takes_offroad ON, legacy_documents_count_valid OFF.

The M52 hand-off (fix.asset.cost.entry._m52_queue, built by stream S6) is
captured, so this suite proves what M46 hands over whatever state the
finance bridge is in; ``test_real_cost_entry_when_the_bridge_has_the_types``
checks the real entry once S6's cost types are installed.
"""

import base64
import types
from datetime import timedelta

import pytest
from odoo.addons.cd_p03_portal.controllers.a07 import m46 as m46_surface
from odoo.addons.cd_vehicle_ext.models import fix_vehicle_ops as ops
from odoo.addons.cd_vehicle_ext.models.fix_vehicle_ops import dhaka_today
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import Error as PgError

REFUSED = (UserError, ValidationError, AccessError, PgError)
OFFICER = "fleet.fleet_group_user"
LM = "cd_vehicle_ext.group_logistics_manager"
TIER2 = "cd_entity_config.group_dofa_tier_2"
TIER3 = "cd_entity_config.group_dofa_tier_3"
TIER4 = "cd_entity_config.group_dofa_tier_4"
SCAN = base64.b64encode(b"%PDF-1.4 scanned").decode()
NEW_TYPES = {"vehicle_renewal", "vehicle_fine", "vehicle_insurance_excess"}
# No test here relays the outbox: the seed backlog need not be marked (it costs
# a minute per test on the shared test database).
pytestmark = pytest.mark.relay_backlog


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED as exc:
        return str(exc) or exc.__class__.__name__
    return None


@pytest.fixture
def f(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    ICP = env["ir.config_parameter"].sudo()
    # D14 (owner, 20 Nov): as the lead seeds them
    ICP.set_param("cd_vehicle_ext.require_fuel_receipt", "True")
    ICP.set_param("cd_vehicle_ext.pm_overdue_takes_offroad", "True")
    ICP.set_param("cd_vehicle_ext.legacy_documents_count_valid", "False")
    ICP.set_param("cd_vehicle_ext.mandatory_document_types", "fitness,insurance,tax")
    ICP.set_param("cd_vehicle_ext.require_passed_preuse_check", "False")
    ICP.set_param("cd_vehicle_ext.fine_decision_lm_limit_bdt", "10000")
    ICP.set_param("cd_vehicle_ext.fine_decision_director_limit_bdt", "50000")

    def user(login, groups=(), tz=None):
        vals = {
            "name": login,
            "login": login,
            "group_ids": [
                (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
            ],
            "assigned_operating_unit_ids": [(6, 0, ou.ids)],
            "default_operating_unit_id": ou.id,
        }
        if tz:
            vals["tz"] = tz
        return env["res.users"].with_context(no_reset_password=True).create(vals)

    x = types.SimpleNamespace(env=env, ou=ou)
    x.user = user
    x.today = dhaka_today(env["fix.vehicle.check"])
    x.clerk = user("m46erp_clerk")
    x.officer, x.officer2 = user("m46erp_off", [OFFICER]), user("m46erp_off2", [OFFICER])
    x.lm, x.lm2 = user("m46erp_lm", [LM]), user("m46erp_lm2", [LM])
    x.t2 = user("m46erp_t2", [TIER2])
    x.director = user("m46erp_dir", [TIER3])
    x.cfo = user("m46erp_cfo", [TIER4])
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "M46EE", "legal_name": "M46ERP Entity", "company_id": env.company.id})
    x.branch = env["fix.branch"].create(
        {
            "name": "M46ERP Branch",
            "code": "M46EB",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fleet.vehicle.model.brand"].create({"name": "M46ERP Brand"})
    x.model = env["fleet.vehicle.model"].create(
        {"name": "M46ERP Van", "brand_id": brand.id, "vehicle_type": "car"}
    )
    x.garage = env["res.partner"].create({"name": "M46ERP Garage", "is_company": True})
    x.brta = env["res.partner"].create({"name": "M46ERP BRTA", "is_company": True})
    x.station = env["res.partner"].create({"name": "M46ERP Pump", "is_company": True})
    x.buyer = env["res.partner"].create({"name": "M46ERP Buyer", "is_company": True})
    x.insurer = env["res.partner"].create({"name": "M46ERP Insurer", "is_insurer": True})
    x.insurer2 = env["res.partner"].create({"name": "M46ERP Insurer 2", "is_insurer": True})

    def doc(v, doc_type, valid_to, scan=True):
        vals = {"vehicle_id": v.id, "doc_type": doc_type, "number": "N-%s" % doc_type}
        vals["valid_to"] = valid_to
        if scan:
            vals["evidence_file"] = SCAN
        return env["fix.vehicle.document"].with_user(x.officer).create(vals)

    def vehicle(plate, docs=True, **kw):
        vals = {"model_id": x.model.id, "license_plate": plate, "branch_id": x.branch.id}
        vals.update(kw)
        v = env["fleet.vehicle"].create(vals)
        if docs:
            for doc_type in ("fitness", "insurance", "tax"):
                doc(v, doc_type, x.today + timedelta(days=200))
        return v

    def driver(name):
        emp = env["hr.employee"].create({"name": name})
        return (
            env["fix.driver"]
            .with_user(x.officer)
            .create(
                {
                    "name": name,
                    "employee_id": emp.id,
                    "license_no": "DL-" + name,
                    "license_class": "Light",
                    "license_expiry": x.today + timedelta(days=400),
                }
            )
        )

    def check(v, ok=True, odometer=0, user=None):
        vals = {"vehicle_id": v.id, "odometer": odometer}
        vals.update({k: ok for k in ("tyres_ok", "lights_ok", "fluids_ok", "brakes_ok")})
        return env["fix.vehicle.check"].with_user(user or x.officer2).create(vals)

    def defect(v, what, safety=True, user=None):
        return (
            env["fix.vehicle.defect"]
            .with_user(user or x.clerk)
            .create(
                {
                    "vehicle_id": v.id,
                    "category": "brakes" if safety else "body",
                    "safety_critical": safety,
                    "description": what,
                }
            )
        )

    x.doc, x.vehicle, x.driver, x.check, x.defect = doc, vehicle, driver, check, defect
    x.van = vehicle("M46ERP-11-0001")
    x.drv = driver("M46ERP Driver")
    x.van.write({"fix_driver_id": x.drv.id})
    return x


@pytest.fixture
def m52(f, monkeypatch):
    """Capture what M46 hands to M52 (the S6 cost types are allowed)."""
    calls = []
    Entry = type(f.env["fix.asset.cost.entry"])
    real = ops.m52_cost_types

    def queue(self, record, vals):
        calls.append((record, dict(vals)))
        return self.browse()

    monkeypatch.setattr(Entry, "_m52_queue", queue)
    monkeypatch.setattr(ops, "m52_cost_types", lambda env: real(env) | NEW_TYPES)
    return calls


# ---------------------------------------------------------------- M46-05
def test_m46_05_open_safety_defect_blocks_the_gate_and_the_return(f):
    a = f.defect(f.van, "brakes pull left")
    off = a.offroad_id
    assert off and off.state == "offroad"
    f.check(f.van)  # the re-check after the brake repair
    b = f.defect(f.van, "steering play")  # reported after the re-check
    assert b.offroad_id == off
    blockers = "; ".join(f.van._fix_dispatch_blockers()[f.van.id])
    assert "open safety-critical defect %s" % b.name in blockers
    assert "safety-critical defect" in refused(
        f.env, lambda: off.with_user(f.officer).action_return()
    )
    a.with_user(f.officer).action_clear("pads replaced")
    assert "still open" in refused(f.env, lambda: off.with_user(f.officer).action_return())
    f.check(f.van)
    b.with_user(f.officer).action_clear("rack tightened")
    off.with_user(f.officer).action_return()
    assert off.state == "returned"
    assert not f.van._fix_dispatch_blockers().get(f.van.id)


def test_m46_05_a_deferrable_defect_does_not_block(f):
    f.defect(f.van, "mirror cracked", safety=False)
    assert not f.van._fix_dispatch_blockers().get(f.van.id)


# ---------------------------------------------------------------- M46-15
def test_m46_15_a_failed_check_put_right_no_longer_blocks_the_day(f):
    bad = f.check(f.van, ok=False)
    off = f.env["fix.vehicle.offroad"].search([("check_id", "=", bad.id)])
    assert any("failed today" in b for b in f.van._fix_dispatch_blockers()[f.van.id])
    f.check(f.van)  # tyre replaced, re-checked
    off.with_user(f.officer).action_return()
    assert not f.van._fix_dispatch_blockers().get(f.van.id)


def test_m46_15_a_failed_check_still_blocks_while_its_record_is_open(f):
    bad = f.check(f.van, ok=False)
    f.check(f.van)
    assert bad._fix_superseded() is False


# ---------------------------------------------------------------- M46-08
def test_m46_08_a_fill_below_a_check_reading_is_refused_or_held(f):
    f.check(f.van, odometer=50000)
    vals = {
        "vehicle_id": f.van.id,
        "driver_id": f.drv.id,
        "litres": 30,
        "odometer": 40000,
        "amount": 3600,
        "payment_method": "fuel_card",
        "fuel_card_ref": "CARD-7",
        "receipt_file": SCAN,
    }
    Fuel = f.env["fix.vehicle.fuel"].with_user(f.clerk)
    assert "odometer below" in refused(f.env, lambda: Fuel.create(vals))
    held = Fuel.create({**vals, "exception_reason": "odometer replaced at service"})
    assert held.review_state == "held" and "odometer_back" in held.exception_flags
    assert f.van._fix_last_odometer() == 50000


def test_m46_08_a_service_typo_and_a_device_typo_never_become_the_reading(f):
    f.check(f.van, odometer=50000)
    pm = (
        f.env["fix.vehicle.pm"]
        .with_user(f.clerk)
        .create({"vehicle_id": f.van.id, "odometer": 999999})
    )
    assert "beyond the reading" in refused(f.env, lambda: pm.with_user(f.officer).action_done())
    pm.write({"odometer": 50300})
    pm.with_user(f.officer).action_done()
    assert pm.state == "done" and f.van._fix_last_odometer() == 50300
    Tel = f.env["fix.vehicle.telemetry"]
    assert refused(
        f.env, lambda: Tel.with_user(f.officer).create({"vehicle_id": f.van.id, "odometer": 1})
    )
    feed = Tel.sudo().create({"vehicle_id": f.van.id, "odometer": 999999})
    assert feed.odometer_held and "beyond" in feed.odometer_note
    assert f.van._fix_last_odometer() == 50300
    log = f.env["fleet.vehicle.odometer"].with_user(f.officer)
    assert "below" in refused(f.env, lambda: log.create({"vehicle_id": f.van.id, "value": 100}))


# ---------------------------------------------------------------- M46-09
def test_m46_09_a_reported_defect_raises_its_own_repair(f):
    Demand = f.env["fix.maintenance.demand"]
    d = f.defect(f.van, "brake line leaking")
    event = {"aggregate": "fix.vehicle.defect", "aggregate_id": d.id, "payload": {}}
    assert Demand.consume_vehicle_defect_raised(event) is True
    demand = Demand.search(
        [("source_model", "=", "fix.vehicle.defect"), ("source_res_id", "=", d.id)]
    )
    assert len(demand) == 1 and demand.vehicle_id == f.van and demand.origin == "m46_defect"
    assert Demand.consume_vehicle_defect_raised(event) is True  # redelivery
    assert (
        Demand.search_count(
            [("source_model", "=", "fix.vehicle.defect"), ("source_res_id", "=", d.id)]
        )
        == 1
    )
    soft = f.defect(f.van, "seat torn", safety=False)
    ev2 = {"aggregate": "fix.vehicle.defect", "aggregate_id": soft.id, "payload": {}}
    assert Demand.consume_vehicle_defect_raised(ev2) is False
    # a check with the defect's id is never read for it
    assert not Demand.search(
        [("source_model", "=", "fix.vehicle.check"), ("source_res_id", "=", d.id)]
    )


# ---------------------------------------------------------------- M46-10 / 26
def _disposal(f, vehicle, **kw):
    vals = {"vehicle_id": vehicle.id, "route": "sale", "reason": "replaced by a new van"}
    vals.update(kw)
    return f.env["fix.vehicle.disposal"].with_user(f.lm).create(vals)


def test_m46_10_a_vehicle_leaves_only_through_a_cfo_approved_disposal(f):
    assert "Vehicle Disposal" in refused(f.env, lambda: f.van.with_user(f.lm).action_retire("sold"))
    Disposal = f.env["fix.vehicle.disposal"]
    assert refused(
        f.env,
        lambda: Disposal.with_user(f.officer).create(
            {"vehicle_id": f.van.id, "route": "scrap", "reason": "x"}
        ),
    ), "a Fleet Officer raised a disposal"
    d = _disposal(f, f.van)
    problem = refused(f.env, lambda: d.with_user(f.lm).action_request_approval(justification="j"))
    assert "buyer" in problem and "proceeds" in problem and "evidence" in problem
    d.write({"buyer_id": f.buyer.id, "proceeds": 900000, "evidence_file": SCAN})
    assert "not approved" in refused(f.env, lambda: d.with_user(f.lm2).action_complete())
    approve_via_inbox(d, f.cfo, requester=f.lm, justification="end of life, 9 years")
    assert d.dofa_approved and d.approval_state == "approved" and d.dofa_approved_by == f.cfo
    # the approval covers the price and the buyer it was given for
    d.with_user(f.lm).write({"proceeds": 700000})
    assert d.approval_state == "none" and not d.dofa_approved
    assert refused(f.env, lambda: d.with_user(f.lm2).action_complete())
    approve_via_inbox(d, f.cfo, requester=f.lm2, justification="revised offer")
    d.with_user(f.lm2).action_complete()
    van = f.van.with_context(active_test=False)
    assert d.state == "done" and not van.active and van.fix_disposal_id == d
    facts = d._m49_disposal_facts()
    assert facts["kind"] == "sale" and facts["proceeds"] == 700000
    assert facts["buyer_id"] == f.buyer.id and facts["approved_by_id"] == f.cfo.id


def test_m46_10_only_the_cfo_tier_is_asked_and_a_leased_van_goes_back(f):
    d = _disposal(f, f.van, route="scrap", evidence_file=SCAN)
    d.with_user(f.lm).action_request_approval(justification="write-off after flood")
    assert d.dofa_tier_required == "tier_4" or d._dofa_current_tier() == "tier_4"
    assert f.cfo in assigned(d) and f.director not in assigned(d) and f.lm not in assigned(d)
    leased = f.vehicle(
        "M46ERP-L1",
        fix_ownership_basis="leased",
        fix_contract_ref="LEASE-9",
        fix_contract_end=f.today + timedelta(days=600),
    )
    bad = _disposal(f, leased, buyer_id=f.buyer.id, proceeds=10, evidence_file=SCAN)
    assert "lessor" in refused(f.env, lambda: bad.with_user(f.lm).action_request_approval("j"))


# ---------------------------------------------------------------- M46-14
def _fine(f, amount, **kw):
    f.env["fix.vehicle.assignment"].with_user(f.officer).search(
        [("vehicle_id", "=", f.van.id), ("date", "=", f.today)]
    ) or f.env["fix.vehicle.assignment"].with_user(f.officer).create(
        {"vehicle_id": f.van.id, "date": f.today, "driver_id": f.drv.id}
    )
    vals = {
        "vehicle_id": f.van.id,
        "offence": "signal jump",
        "amount": amount,
        "case_ref": "DMP-%s" % amount,
    }
    vals.update(kw)
    return f.env["fix.vehicle.penalty"].with_user(f.lm).create(vals)


def test_m46_14_a_small_fine_is_decided_by_the_lm_and_handed_to_m52(f, m52):
    pen = _fine(f, 5000)
    assert "Payment Method" in refused(
        f.env, lambda: pen.with_user(f.lm2).action_absorb("signal fault")
    )
    pen.write({"payment_method": "vendor_bill"})
    assert "vendor" in refused(f.env, lambda: pen.with_user(f.lm2).action_absorb("signal fault"))
    pen.write({"vendor_id": f.brta.id})
    pen.with_user(f.lm2).action_absorb("signal fault confirmed")
    assert pen.state == "decided" and pen.recovery_decision == "absorb"
    [(record, vals)] = m52
    assert record == pen and vals["cost_type"] == "vehicle_fine" and vals["amount"] == 5000
    assert vals["operating_unit_id"] == f.branch.operating_unit_id.id
    assert vals["vendor_id"] == f.brta.id and vals["invoice_ref"] == "DMP-5000"
    assert vals["payment_method"] == "vendor_bill" and not vals["recovery_employee_id"]
    # "paid" is never typed: finance records it
    assert refused(f.env, lambda: pen.with_user(f.lm).write({"paid_on": f.today}))
    pen._m52_mark_paid(5000, f.today, "AP/0001")
    assert pen.paid_on == f.today and pen.payment_ref == "AP/0001"


def test_m46_14_above_the_lm_limit_the_director_or_the_cfo_approves(f, m52):
    pen = _fine(f, 30000, payment_method="petty_cash", evidence_file=SCAN)
    pen.with_user(f.lm2).action_recover("driver ran the light")
    assert pen.state == "recorded" and pen.approval_state == "pending"
    assert pen._dofa_current_tier() == "tier_3" and f.director in assigned(pen)
    assert not m52
    approve_via_inbox(pen, f.director, requester=f.lm2)
    assert pen.state == "decided" and pen.recovery_decision == "recover"
    assert pen.decided_by_id == f.lm2 and pen.dofa_approved_by == f.director
    [(record, vals)] = m52
    assert vals["recovery_employee_id"] == f.drv.employee_id.id
    big = _fine(f, 80000, payment_method="petty_cash", evidence_file=SCAN, case_ref="DMP-BIG")
    big.with_user(f.lm2).action_absorb("company route error")
    assert big._dofa_current_tier() == "tier_4"
    assert f.cfo in assigned(big) and f.director not in assigned(big)


# ---------------------------------------------------------------- M46-13
def test_m46_13_the_settlement_approval_pins_the_insurer_and_the_excess(f, m52):
    acc = (
        f.env["fix.vehicle.accident"]
        .with_user(f.clerk)
        .create(
            {
                "vehicle_id": f.van.id,
                "driver_id": f.drv.id,
                "description": "rear-ended at Mirpur 10",
                "insurer_id": f.insurer.id,
                "evidence_file": SCAN,
                "excess_amount": 5000,
                "excess_borne_by": "company",
                "excess_payment_method": "vendor_bill",
                "excess_vendor_id": f.garage.id,
                "excess_invoice_ref": "GAR-77",
                "assessed_amount": 60000,
            }
        )
    )
    acc.with_user(f.clerk).action_claim(claim_ref="INS-77")
    acc.write({"settlement_amount": 40000})
    approve_via_inbox(acc, f.t2, requester=f.lm, justification="assessor report")
    assert acc.approval_state == "approved"
    acc.with_user(f.lm).write({"insurer_id": f.insurer2.id})
    assert acc.approval_state == "none" and not acc.dofa_approved
    approve_via_inbox(acc, f.t2, requester=f.lm2, justification="insurer corrected")
    acc.with_user(f.lm).write({"excess_amount": 7000})
    assert acc.approval_state == "none"
    approve_via_inbox(acc, f.t2, requester=f.lm2, justification="excess per policy")
    acc.with_user(f.lm2).action_close(settlement="40000")
    assert acc.state == "closed"
    [(record, vals)] = m52
    assert record == acc and vals["cost_type"] == "vehicle_insurance_excess"
    assert vals["amount"] == 7000 and vals["vendor_id"] == f.garage.id
    assert vals["operating_unit_id"] == f.branch.operating_unit_id.id


def test_m46_13_an_excess_without_its_payment_facts_does_not_close(f, m52):
    acc = (
        f.env["fix.vehicle.accident"]
        .with_user(f.clerk)
        .create(
            {
                "vehicle_id": f.van.id,
                "description": "scrape",
                "insurer_id": f.insurer.id,
                "evidence_file": SCAN,
                "excess_amount": 2000,
            }
        )
    )
    acc.with_user(f.clerk).action_claim(claim_ref="INS-78")
    problem = refused(f.env, lambda: acc.with_user(f.lm).action_close(settlement="0"))
    assert "who bears the excess" in problem
    assert not m52


# ---------------------------------------------------------------- money contract
def test_renewal_fees_are_paid_through_m52_on_the_branch(f, m52):
    fitness = f.van.document_ids.filtered(lambda d: d.doc_type == "fitness")[:1]
    runner = f.env["hr.employee"].create({"name": "M46ERP Runner"})
    ren = (
        f.env["fix.vehicle.document.renewal"]
        .with_user(f.officer)
        .create(
            {
                "document_id": fitness.id,
                "responsible_employee_id": runner.id,
                "government_fee": 1200,
                "agent_fee": 300,
            }
        )
    )
    ren.with_user(f.officer).action_submit()
    ren.write({"new_document_id": f.doc(f.van, "fitness", f.today + timedelta(days=565)).id})
    assert "Payment Method" in refused(f.env, lambda: ren.with_user(f.officer2).action_complete())
    ren.write({"payment_method": "vendor_bill", "vendor_id": f.brta.id})
    assert "invoice number" in refused(f.env, lambda: ren.with_user(f.officer2).action_complete())
    ren.write({"invoice_ref": "BRTA-55"})
    ren.with_user(f.officer2).action_complete()
    [(record, vals)] = m52
    assert record == ren and vals["cost_type"] == "vehicle_renewal" and vals["amount"] == 1500
    assert vals["operating_unit_id"] == f.ou.id and vals["invoice_ref"] == "BRTA-55"


def test_a_fill_names_how_it_was_paid_and_its_vehicle_has_an_operating_unit(f):
    base = {
        "vehicle_id": f.van.id,
        "driver_id": f.drv.id,
        "litres": 30,
        "odometer": 1000,
        "amount": 3600,
        "receipt_file": SCAN,
    }
    Fuel = f.env["fix.vehicle.fuel"].with_user(f.clerk)
    assert "Payment Method" in refused(f.env, lambda: Fuel.create(base))
    assert "fuel card" in refused(
        f.env, lambda: Fuel.create({**base, "payment_method": "fuel_card"})
    )
    assert "vendor" in refused(
        f.env, lambda: Fuel.create({**base, "payment_method": "vendor_bill"})
    )
    # D14: the receipt scan is required
    no_scan = {k: v for k, v in base.items() if k != "receipt_file"}
    assert "receipt scan" in refused(
        f.env, lambda: Fuel.create({**no_scan, "payment_method": "petty_cash"})
    )
    nowhere = f.env["fleet.vehicle"].create(
        {"model_id": f.model.id, "license_plate": "M46ERP-NOOU"}
    )
    assert "operating unit" in refused(
        f.env,
        lambda: Fuel.create({**base, "vehicle_id": nowhere.id, "payment_method": "petty_cash"}),
    )
    fill = Fuel.create({**base, "payment_method": "employee_expense"})
    facts = fill._m52_cost_facts()
    assert fill.paid_by_employee_id == f.drv.employee_id
    assert facts["operating_unit_id"] == f.ou.id and facts["employee_id"] == f.drv.employee_id.id
    assert facts["payment_method"] == "employee_expense"


def test_a_service_cost_names_its_payment_and_its_garage(f):
    pm = (
        f.env["fix.vehicle.pm"]
        .with_user(f.clerk)
        .create(
            {
                "vehicle_id": f.van.id,
                "odometer": 1200,
                "cost": 3500,
                "provider_id": f.garage.id,
                "invoice_ref": "GAR-9",
            }
        )
    )
    assert "Payment Method" in refused(f.env, lambda: pm.with_user(f.officer).action_done())
    pm.write({"payment_method": "vendor_bill"})
    pm.with_user(f.officer).action_done()
    facts = pm._m52_cost_facts()
    assert facts["vendor_id"] == f.garage.id and facts["invoice_ref"] == "GAR-9"
    assert facts["operating_unit_id"] == f.ou.id


def test_m46_04_a_vehicle_follows_its_branch_operating_unit(f):
    V = f.env["fleet.vehicle"].with_user(f.lm)
    assert "branch" in refused(
        f.env, lambda: V.create({"model_id": f.model.id, "license_plate": "M46ERP-U1"})
    )
    v = V.create({"model_id": f.model.id, "license_plate": "M46ERP-U2", "branch_id": f.branch.id})
    assert v.operating_unit_id == f.branch.operating_unit_id
    other = f.env["operating.unit"].search([("id", "!=", f.ou.id)], limit=1)
    if other:
        assert "follows the branch" in refused(
            f.env, lambda: v.with_user(f.lm).write({"operating_unit_id": other.id})
        )


def test_real_cost_entry_when_the_bridge_has_the_types(f):
    if "vehicle_fine" not in ops.m52_cost_types(f.env):
        pytest.skip("S6 cost types not installed on this database yet")
    pen = _fine(f, 4000, payment_method="petty_cash", evidence_file=SCAN)
    pen.with_user(f.lm2).action_absorb("company error")
    entry = (
        f.env["fix.asset.cost.entry"]
        .sudo()
        .search([("source_model", "=", pen._name), ("source_res_id", "=", pen.id)])
    )
    assert entry and entry.cost_type == "vehicle_fine" and entry.amount == 4000
    assert entry.operating_unit_id == f.ou


# ---------------------------------------------------------------- M46-19
def test_m46_19_a_class_profile_drives_documents_tank_and_the_efficiency_flag(f):
    profile = (
        f.env["fix.vehicle.class.profile"]
        .with_user(f.officer)
        .create(
            {
                "name": "M46ERP Van class",
                "mandatory_document_types": "fitness,insurance,tax,registration",
                "tank_capacity_l": 30,
                "baseline_km_per_litre": 20,
                "deterioration_pct": 10,
            }
        )
    )
    assert refused(f.env, lambda: profile.with_user(f.officer).write({"tank_capacity_l": 50}))
    f.van.write({"fix_class_profile_id": profile.id})
    assert any("Registration" in b for b in f.van._fix_dispatch_blockers()[f.van.id])
    assert f.env["fix.vehicle.fuel"]._fix_tank_capacity(f.van) == 30
    Fuel = f.env["fix.vehicle.fuel"].sudo()
    for odo in (1000, 1100):
        Fuel.create({"vehicle_id": f.van.id, "litres": 10, "odometer": odo, "amount": 1200})
    row = next(
        r for r in m46_surface.fuel_efficiency(f.env)["rows"] if r["vehicle"].startswith(f.van.name)
    )
    assert row["km_per_litre"] == 10 and row["baseline"] == 20 and row["flag"] == "DETERIORATED"


# ---------------------------------------------------------------- M46-16 / 17
def test_m46_16_17_packs_keep_retired_vehicles_and_honour_the_period(f):
    Fuel = f.env["fix.vehicle.fuel"].sudo()
    for odo in (1000, 1300):
        Fuel.create({"vehicle_id": f.van.id, "litres": 20, "odometer": odo, "amount": 2400})
    f.env["fix.vehicle.pm"].sudo().create(
        {"vehicle_id": f.van.id, "odometer": 1300, "cost": 900}
    ).action_done()

    def row(pack, **kw):
        rows = pack(f.env, **kw)["rows"]
        return next(
            (
                r
                for r in rows
                if r.get("plate") == f.van.license_plate
                or str(r.get("vehicle", "")).startswith(f.van.name)
            ),
            None,
        )

    before = row(m46_surface.cost_per_km)
    f.van.sudo().action_retire(reason="test retirement")
    after = row(m46_surface.cost_per_km)
    assert after and after["total_cost"] == before["total_cost"] and "(retired)" in after["vehicle"]
    last_year = f.today - timedelta(days=400)
    old = row(m46_surface.maintenance_cost, date_from=str(last_year), date_to=str(last_year))
    assert old and old["cost"] == 0
    now = row(m46_surface.maintenance_cost, date_from=str(f.today), date_to=str(f.today))
    assert now["cost"] == 900


# ---------------------------------------------------------------- M46-20
def test_m46_20_the_hr_and_fleet_licence_are_one_fact(f):
    if "driving_license_exp" not in f.env["hr.employee"]._fields:
        pytest.skip("cd_hr_core not installed")
    emp = f.drv.employee_id.sudo()
    assert emp.driving_license_exp == f.drv.license_expiry
    renewed = f.today + timedelta(days=900)
    emp.write({"driving_license_exp": renewed, "driving_license_no": "DL-NEW-1"})
    assert f.drv.license_expiry == renewed and f.drv.license_no == "DL-NEW-1"
    assert not f.drv.hr_licence_mismatch
    emp.with_context(fix_driver_hr_sync=True).write({"driving_license_exp": f.today})
    f.drv.invalidate_recordset(["hr_licence_mismatch"])
    assert "expiry" in f.drv.hr_licence_mismatch


# ---------------------------------------------------------------- M46-22
def test_m46_22_the_vehicle_logbook_prints_its_history(f):
    f.check(f.van, odometer=500)
    empty = m46_surface.vehicle_logbook(f.env)
    assert not empty["rows"] and f.van.license_plate in empty["filters"][0]["options"]
    book = m46_surface.vehicle_logbook(f.env, vehicle=f.van.license_plate)
    kinds = {r["kind"] for r in book["rows"]}
    assert {"Document", "Pre-use check"} <= kinds


# ---------------------------------------------------------------- M46-23
def test_m46_23_an_accident_lists_its_cargo_and_tells_m17(f):
    Acc = f.env["fix.vehicle.accident"].with_user(f.clerk)
    vals = {"vehicle_id": f.van.id, "description": "skid", "cargo_affected": True}
    assert "affected customer devices" in refused(f.env, lambda: Acc.create(vals))
    acc = Acc.create({**vals, "cargo_note": "SN-NOT-REGISTERED-1"})
    Demand = f.env["fix.maintenance.demand"]
    assert Demand.consume_vehicle_incident_cargo(
        {"aggregate": acc._name, "aggregate_id": acc.id, "payload": {}}
    )
    assert any("SN-NOT-REGISTERED-1" in (m.body or "") for m in acc.message_ids)


# ---------------------------------------------------------------- M46-24
def test_m46_24_operational_dates_are_dhaka_dates_whatever_the_user_tz(f):
    for tz in ("Etc/GMT+12", "Etc/GMT-14"):
        u = f.user("m46erp_tz_%s" % tz[-3:].replace("+", "p").replace("-", "m"), [OFFICER], tz=tz)
        chk = (
            f.env["fix.vehicle.check"]
            .with_user(u)
            .create(
                {
                    "vehicle_id": f.van.id,
                    "tyres_ok": True,
                    "lights_ok": True,
                    "fluids_ok": True,
                    "brakes_ok": True,
                }
            )
        )
        assert chk.checked_on == f.today, tz


# ---------------------------------------------------------------- M46-25
def test_m46_25_a_registered_vehicle_is_commissioned_before_dispatch(f):
    v = (
        f.env["fleet.vehicle"]
        .with_user(f.lm)
        .create({"model_id": f.model.id, "license_plate": "M46ERP-NEW", "branch_id": f.branch.id})
    )
    assert not v.fix_commissioned and v.fix_lifecycle_state == "registered"
    assert any("not commissioned" in b for b in v._fix_dispatch_blockers()[v.id])
    assert refused(f.env, lambda: v.with_user(f.lm).write({"fix_commissioned": True}))
    assert "Fitness" in refused(f.env, lambda: v.with_user(f.officer).action_commission())
    for doc_type in ("fitness", "insurance", "tax"):
        f.doc(v, doc_type, f.today + timedelta(days=200))
    assert "pre-use check" in refused(f.env, lambda: v.with_user(f.officer).action_commission())
    f.check(v)
    v.with_user(f.officer).action_commission()
    assert v.fix_commissioned and v.fix_commissioned_by_id == f.officer
    assert not v._fix_dispatch_blockers().get(v.id)


def test_m46_17_packs_are_fenced_by_the_users_operating_units(f):
    other = f.env["operating.unit"].create(
        {
            "name": "M46ERP Other OU",
            "code": "M46OO",
            "partner_id": f.env.company.partner_id.id,
            "company_id": f.env.company.id,
        }
    )
    f.vehicle("M46ERP-FAR", docs=False, branch_id=False, operating_unit_id=other.id)
    officer_env = f.env(user=f.officer.id, su=False)
    plates = {r["plate"] for r in m46_surface.cost_per_km(officer_env)["rows"]}
    assert f.van.license_plate in plates and "M46ERP-FAR" not in plates
    everyone = {r["plate"] for r in m46_surface.cost_per_km(f.env)["rows"]}
    assert "M46ERP-FAR" in everyone
