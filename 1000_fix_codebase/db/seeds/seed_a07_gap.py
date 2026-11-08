"""seed_a07_gap.py - synthetic rows for the A07 asset screens the party purge emptied.

Why this exists. On 8 Nov 2026 the real-customer cut-over (CD-M33-01) purged
every synthetic party and 46 synthetic employees from fix_dev. Every A07 row
hanging off them went too: the four drivers, all IoT actions, the leases and
their rent schedule, facility PM plans, occupancy records and the employees
of all 25 seed.a07.* users. 29 of the 90 A07 screens opened on "0 records".
This file refills them under the seed manifest rules:

  * synthetic only (DE-12), Bengali-first (DE-17), fixed values, no random;
  * state-complete where a screen shows a lifecycle (DE-16): a driver active
    and one suspended for an expired licence; a passed and a failed pre-use
    check; a lease approved and one awaiting approval; a PM plan done and
    open; an instrument issued and returned; a transfer received; an IoT
    action proposed, approved and done;
  * idempotent: every block looks for its own `SEED-A07-` marker first, so a
    second run creates nothing;
  * no outbound anything (DE-11).

Every row is made through the PRODUCTION path, as the role that does it,
including the A07 decisions of 8 Nov (B9-B11): a Fleet Officer registers
drivers and assigns vans, the assigned Driver records their own pre-use check,
a Facility Manager writes leases and asks for their approval with a reason,
the DOFA approver decides from the inbox, an Equipment Custodian issues and
transfers instruments, an IoT Operator records a prediction naming the
published M26 model and asks for the action's approval with a reason. No
state, approval stamp or amount is written directly. Only the actors
(employees for the seed users, synthetic counterparties) are made as the
superuser, as a person's HR and party records would be.

    PYTHONPATH=. .venv/Scripts/python.exe vendor/odoo/odoo-bin shell \
        -c infra/odoo-conf/local.resolved.conf -d fix_dev --no-http \
        < db/seeds/seed_a07_gap.py

Set FIX_A07_COMMIT=1 to keep the result; otherwise everything is rolled back
and only the report is printed. Each block runs in its own savepoint and
reports, so one refusal from a business rule is visible without hiding what
the other blocks did.
"""

import base64
import os
import time
from contextlib import contextmanager
from datetime import date, timedelta

MARK = "SEED-A07-"
RESULTS = []
LOGIN = "seed.a07.%s@1000fix.local"
PDM_MODEL = "m26.predictive.maintenance"  # the published M26 predictive-maintenance model
OK = {"tyres_ok": True, "lights_ok": True, "fluids_ok": True, "brakes_ok": True}


def seed(env):
    today = date.today()
    company = env.ref("base.main_company")
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    Users = env["res.users"]

    @contextmanager
    def block(name):
        started = time.monotonic()
        print(f"seed_a07_gap: >> {name}", flush=True)
        try:
            with env.cr.savepoint():
                yield
            RESULTS.append(("ok", name, "%.1fs" % (time.monotonic() - started)))
        except Exception as exc:
            first = (str(exc).strip().splitlines() or [""])[0]
            RESULTS.append(("FAIL", name, f"{type(exc).__name__}: {first[:260]}"))

    def skip(name, why):
        RESULTS.append(("skip", name, f"already seeded ({why})"))

    def u(key):
        found = Users.search([("login", "=", LOGIN % key)], limit=1)
        if not found:
            raise RuntimeError("missing user %s: run appoint_approvers.py first" % (LOGIN % key))
        return found

    def employee(usr):
        Emp = env["hr.employee"]
        return Emp.search([("user_id", "=", usr.id)], limit=1) or Emp.create(
            {"name": usr.name, "user_id": usr.id, "company_id": company.id}
        )

    def partner(ref, name, **kw):
        Partner = env["res.partner"]
        return Partner.search([("ref", "=", MARK + ref)], limit=1) or Partner.create(
            {"name": name, "ref": MARK + ref, "company_id": company.id, **kw}
        )

    def scan(label):
        """A synthetic one-line PDF standing for a scanned paper (DE-12)."""
        return base64.b64encode((f"%PDF-1.4 SEED-A07 {label}").encode()).decode()

    def evidence(label, res_model, res_id, doc_type="asset_document"):
        attachment = env["ir.attachment"].create(
            {"name": f"{label}.pdf", "raw": (f"%PDF-1.4 SEED-A07 {label}").encode()}
        )
        return env["fix.document"].create(
            {
                "name": MARK + label,
                "attachment_id": attachment.id,
                "document_type": doc_type,
                "res_model": res_model,
                "res_id": res_id,
            }
        )

    def approve(record, requester, justification):
        """Ask as the requester; decide from the inbox as the task's assignee."""
        if record.approval_state != "pending":
            record.with_user(requester).action_request_approval(justification=justification)
        task = record.approval_request_id.task_ids.filtered(lambda t: t.state == "pending")[:1]
        if not task or not task.assigned_user_id:
            raise RuntimeError(f"no assigned inbox task for {record.display_name}")
        task.with_user(task.assigned_user_id).action_approve(comment="SEED-A07 decision")
        return task.assigned_user_id

    # ------------------------------------------------------------------ actors
    with block("actors: employees for the seed users, synthetic counterparties"):
        for key in (
            "driver",
            "custodian",
            "cal.technician",
            "quality1",
            "quality2",
            "fleet1",
            "fleet2",
            "facility1",
            "facility2",
            "hse",
            "iot.operator",
            "branch.lead",
            "dispatcher",
            "logistics",
            "device.agent",
            "device.branch",
        ):
            employee(u(key))
        partner("LESSOR-1", "রহমান প্রপার্টিজ লিমিটেড (SEED-A07)", is_company=True)
        partner("LESSOR-2", "নূর এস্টেটস (SEED-A07)", is_company=True)
        partner("PM-1", "শীতল এয়ারকন সার্ভিসেস (SEED-A07)", is_company=True)
        partner("PM-2", "নিরাপদ ফায়ার সেফটি (SEED-A07)", is_company=True)
        partner("CLIENT-1", "সবুজ টেক্সটাইলস লিমিটেড (SEED-A07)", is_company=True)
        partner("OWNER-1", "করিম হোসেন (SEED-A07)")
        partner("OWNER-2", "ফাতেমা বেগম (SEED-A07)")

    def p(ref):
        return env["res.partner"].search([("ref", "=", MARK + ref)], limit=1)

    def emp(key):
        return env["hr.employee"].search([("user_id", "=", u(key).id)], limit=1)

    # ---------------------------------------------------------------- M46 fleet
    Driver = env["fix.driver"]
    with block("M46 drivers, van assignment, pre-use checks, telematics"):
        if Driver.search_count([("license_no", "like", MARK)]):
            skip("M46 drivers", "drivers with a SEED-A07 licence")
        else:
            officer = u("fleet1")
            karim = Driver.with_user(officer).create(
                {
                    "name": u("driver").name,
                    "employee_id": emp("driver").id,
                    "license_no": MARK + "DL-0001",
                    "license_class": "LMV",
                    "license_expiry": today + timedelta(days=400),
                    "phone": "01700000701",
                }
            )
            spare = env["hr.employee"].create(
                {"name": "সেলিম মিয়া (Driver, SEED-A07)", "company_id": company.id}
            )
            selim = Driver.with_user(officer).create(
                {
                    "name": spare.name,
                    "employee_id": spare.id,
                    "license_no": MARK + "DL-0002",
                    "license_class": "LMV",
                    "license_expiry": today + timedelta(days=200),
                    "phone": "01700000702",
                }
            )
            lapsed = env["hr.employee"].create(
                {"name": "জসিম উদ্দিন (Driver, SEED-A07)", "company_id": company.id}
            )
            Driver.with_user(officer).create(
                {
                    "name": lapsed.name,
                    "employee_id": lapsed.id,
                    "license_no": MARK + "DL-0003",
                    "license_class": "LMV",
                    "license_expiry": today - timedelta(days=20),
                    "phone": "01700000703",
                }
            )  # born suspended: the licence has expired (AUT-FLT-05)
            vans = env["fleet.vehicle"].search([], order="id", limit=2)
            van_a, van_b = vans[0], vans[1]
            van_a.with_user(officer).write({"fix_driver_id": karim.id})
            van_b.with_user(officer).write({"fix_driver_id": selim.id})
            # B10: the assigned Driver records their own van's check, as themselves
            env["fix.vehicle.check"].with_user(u("driver")).create({"vehicle_id": van_a.id, **OK})
            # a Fleet Officer records the other van's, which fails on its brakes
            env["fix.vehicle.check"].with_user(officer).create(
                {
                    "vehicle_id": van_b.id,
                    **dict(OK, brakes_ok=False),
                    "defects": "Brake pedal soft; sent to workshop (SEED-A07)",
                }
            )
            # the statutory register a van needs before it is dispatched (BRU-FLT-01)
            Doc = env["fix.vehicle.document"]
            for van in (van_a, van_b):
                for kind, years in (("fitness", 1), ("insurance", 1), ("tax", 1)):
                    if Doc.search_count(
                        [
                            ("vehicle_id", "=", van.id),
                            ("doc_type", "=", kind),
                            ("valid_to", ">=", today),
                        ]
                    ):
                        continue
                    Doc.with_user(officer).create(
                        {
                            "vehicle_id": van.id,
                            "doc_type": kind,
                            "number": MARK + f"{kind.upper()}-{van.id}",
                            "valid_from": today - timedelta(days=30),
                            "valid_to": today + timedelta(days=365 * years - 30),
                            "evidence_file": scan(f"{kind} {van.id}"),
                            "evidence_filename": f"{kind}-{van.id}.pdf",
                        }
                    )
            Assignment = env["fix.vehicle.assignment"]
            Assignment.with_user(officer).create(
                {
                    "vehicle_id": van_a.id,
                    "date": today,
                    "driver_id": karim.id,
                    # the technician on the van must hold a driving licence (BRU-HSE-07)
                    "technician_id": emp("driver").id,
                    "operating_unit_id": ou.id,
                }
            )
            Telemetry = env["fix.vehicle.telemetry"]
            now = env.cr.now()
            Telemetry.with_user(officer).create(
                {
                    "vehicle_id": van_a.id,
                    "device_ref": MARK + "GPS-01",
                    "last_ping": now - timedelta(minutes=4),
                    "fuel_level_pct": 64,
                }
            )
            Telemetry.with_user(officer).create(
                {
                    "vehicle_id": van_b.id,
                    "device_ref": MARK + "GPS-02",
                    "last_ping": now - timedelta(hours=30),
                    "fuel_level_pct": 18,
                }
            )

    # ----------------------------------------------------------- M47 facilities
    Lease = env["fix.site.lease"]
    with block("M47 leases (approved and awaiting), rent schedule, extract"):
        if Lease.search_count([("name", "like", MARK)]):
            skip("M47 leases", "leases named SEED-A07")
        else:
            fm = u("facility1")
            sites = env["fix.site"].search(
                [("state", "=", "active"), ("occupancy_basis", "=", "leased")], order="id"
            )
            first = Lease.with_user(fm).create(
                {
                    "name": MARK + "LEASE-AGRABAD",
                    "site_id": sites[0].id,
                    "lessor_id": p("LESSOR-1").id,
                    "start_date": today.replace(day=1) - timedelta(days=150),
                    "end_date": today.replace(day=1) + timedelta(days=3 * 365),
                    "monthly_rent": 85000,
                    "escalation_pct": 5.0,
                    "deposit": 510000,
                    "notice_period_days": 90,
                }
            )
            second = Lease.with_user(fm).create(
                {
                    "name": MARK + "LEASE-SONADANGA",
                    "site_id": sites[2].id,
                    "lessor_id": p("LESSOR-2").id,
                    "start_date": today.replace(day=1) - timedelta(days=60),
                    "end_date": today.replace(day=1) + timedelta(days=2 * 365),
                    "monthly_rent": 42000,
                    "escalation_pct": 4.0,
                    "deposit": 252000,
                    "notice_period_days": 60,
                }
            )
            # rent to accounts payable, and the IFRS 16 extract for the new lease
            due = first.schedule_ids.sorted("due_date")[:1]
            if due:
                due.with_user(fm).action_send_to_ap()
            first.with_user(fm).action_publish_ifrs16()
            # a renewal of the first lease, approved from the inbox and applied
            first.with_user(fm).action_open_modification()
            first.with_user(fm).write(
                {
                    "proposed_end_date": first.end_date + timedelta(days=2 * 365),
                    "proposed_monthly_rent": 89250,
                    "proposed_escalation_pct": 5.0,
                    "modification_reason": "Two-year extension at 5% uplift (SEED-A07)",
                }
            )
            approve(first, fm, "Extension keeps the Agrabad branch at below-market rent (SEED-A07)")
            if first.modification_open:
                first.with_user(fm).action_apply_modification()
            # a rent review of the second, waiting in the approver's inbox
            second.with_user(fm).action_open_modification()
            second.with_user(fm).write(
                {
                    "proposed_monthly_rent": 46000,
                    "modification_reason": "Landlord rent review after the road widening (SEED-A07)",
                }
            )
            second.with_user(fm).action_request_approval(
                justification="Rent review within the 10% band agreed at signing (SEED-A07)"
            )

    with block("M47 occupancy and condition, building-services PM"):
        Cond = env["fix.site.condition"]
        if Cond.search_count([("name", "like", MARK)]):
            skip("M47 occupancy", "conditions named SEED-A07")
        else:
            fm = u("facility1")
            sites = env["fix.site"].search([("state", "=", "active")], order="id", limit=4)
            for site, pct, grade in zip(
                sites, (92.0, 78.5, 64.0, 88.0), ("a", "b", "c", "b"), strict=False
            ):
                Cond.with_user(fm).create(
                    {
                        "name": MARK + f"COND-{site.id}",
                        "site_id": site.id,
                        "inspected_on": today - timedelta(days=7),
                        "occupancy_pct": pct,
                        "condition_grade": grade,
                        "inspector_id": emp("facility1").id,
                        "notes": "Quarterly walk-through (SEED-A07)",
                    }
                )
            Pm = env["fix.site.pm"]
            done = Pm.with_user(fm).create(
                {
                    "name": MARK + f"PM-HVAC-{sites[0].id}",
                    "site_id": sites[0].id,
                    "service_type": "hvac",
                    "provider_id": p("PM-1").id,
                    "scheduled_on": today - timedelta(days=10),
                    "cost": 18000,
                    "interval_months": 3,
                }
            )
            done.with_user(fm).action_done(done_on=today - timedelta(days=9))
            for site, kind, provider, days in (
                (sites[1], "fire", "PM-2", 12),
                (sites[2], "generator", "PM-1", 20),
                (sites[3], "lift", "PM-1", 35),
            ):
                Pm.with_user(fm).create(
                    {
                        "name": MARK + f"PM-{kind.upper()}-{site.id}",
                        "site_id": site.id,
                        "service_type": kind,
                        "provider_id": p(provider).id,
                        "scheduled_on": today + timedelta(days=days),
                        "cost": 12000,
                        "interval_months": 6,
                    }
                )

    # ---------------------------------------------------------- M45 equipment
    with block("M45 calibration profile, issue and return, transfer, verification"):
        Issue = env["fix.equipment.issue"]
        if Issue.search_count([("reference", "like", MARK)]):
            skip("M45 equipment ops", "issues referenced SEED-A07")
        else:
            keeper = u("custodian")
            # B9: the calibrations of the synthetic seed instruments wait for a
            # usage decision; a Quality Manager who did not record them accepts
            seeds = env["fix.equipment"].search([("name", "like", "Seed Equipment")], order="id")
            waiting = env["fix.calibration"].search(
                [
                    ("equipment_id", "in", seeds.ids),
                    ("decision_state", "=", "pending"),
                    ("result", "in", ["pass", "adjusted"]),
                ],
                order="id",
            )
            for cal in waiting:
                decider = u("quality2") if cal.create_uid != u("quality2") else u("quality1")
                cal.with_user(decider).action_accept_calibration()
            items = seeds | env["fix.equipment"].search(
                [("name", "not like", "AUDIT"), ("name", "not like", "Seed Equipment")], order="id"
            )
            usable = seeds.filtered(lambda e: e.operational_status == "available")
            env["fix.calibration.profile"].with_user(u("quality1")).create(
                {
                    "equipment_id": items[5].id,
                    "interval_months": 12,
                    "provider_requirement": "accredited",
                    "required_traceability": "BSTI / national standard (SEED-A07)",
                }
            )
            out = Issue.with_user(keeper).create(
                {
                    "equipment_id": usable[0].id,
                    "custodian_id": emp("dispatcher").id,
                    "reference": MARK + "ISS-01",
                    "issued_on": today - timedelta(days=3),
                    "due_on": today + timedelta(days=4),
                    "condition_out": "Good",
                }
            )
            back = Issue.with_user(keeper).create(
                {
                    "equipment_id": usable[1].id,
                    "custodian_id": emp("driver").id,
                    "reference": MARK + "ISS-02",
                    "issued_on": today - timedelta(days=12),
                    "due_on": today - timedelta(days=5),
                    "condition_out": "Good",
                }
            )
            back.with_user(keeper).action_return(condition="good")
            del out
            moving = usable[2]
            to_branch = env["fix.branch"].search(
                [("id", "!=", moving.branch_id.id)], order="id", limit=1
            )
            transfer = (
                env["fix.equipment.transfer"]
                .with_user(keeper)
                .create(
                    {
                        "equipment_id": moving.id,
                        "to_branch_id": to_branch.id,
                        "to_custodian_id": emp("hse").id,
                        "transfer_date": today - timedelta(days=2),
                        "notes": "Rebalance to the regional hub (SEED-A07)",
                    }
                )
            )
            transfer.with_user(keeper).action_dispatch()
            transfer.with_user(u("quality1")).action_receive()
            for item, found in ((items[3], True), (items[4], True), (items[10], False)):
                env["fix.equipment.verification"].with_user(keeper).create(
                    {
                        "equipment_id": item.id,
                        "campaign_ref": MARK + "PV-2026-Q4",
                        "verified_on": today - timedelta(days=1),
                        "location": "Tejgaon tool crib",
                        "found": found,
                        "verifier_id": emp("custodian").id,
                        "condition": "Good" if found else "",
                    }
                )

    # ----------------------------------------------------------- M17 devices
    with block("M17 client estate and an ownership transfer"):
        Estate = env["fix.device.estate"]
        if Estate.search_count([("name", "like", MARK)]):
            skip("M17 estates", "estates named SEED-A07")
        else:
            agent = u("device.agent")
            Estate.with_user(agent).create(
                {
                    "name": MARK + "সবুজ টেক্সটাইলস - গাজীপুর কারখানা",
                    "client_id": p("CLIENT-1").id,
                    "site": "Gazipur factory",
                    "department": "IT",
                    "cost_centre": "CC-IT-01",
                    "company_id": company.id,
                }
            )
            device = (
                env["fix.device"]
                .with_user(agent)
                .create(
                    {
                        "name": "Dell Latitude 5440 (SEED-A07)",
                        "owner_id": p("OWNER-1").id,
                        "serial_number": MARK + "SN-5440-0001",
                        "company_id": company.id,
                        "operating_unit_id": ou.id,
                        "device_model_id": env["fix.device.model"]
                        .search([], order="id", limit=1)
                        .id,
                    }
                )
            )
            receipt = evidence("SALE-RECEIPT-5440", "fix.device", device.id)
            device.with_user(agent).action_transfer_ownership(
                new_owner_id=p("OWNER-2").id,
                transfer_type="sale",
                reason="Sold to a family member (SEED-A07)",
                evidence_document_id=receipt.id,
                channel="back_office",
            )

    # ------------------------------------------------------------- M48 IoT
    with block("M48 adapters carry the company (screen lists company rows only)"):
        unscoped = env["fix.iot.adapter"].search([("company_id", "=", False)])
        if not unscoped:
            skip("M48 adapters", "every adapter has a company")
        else:
            unscoped.with_user(u("iot.admin")).write({"company_id": company.id})

    with block("M48 prediction and prescriptive actions (proposed, approved, done)"):
        Pdm = env["fix.predictive.maintenance"]
        if Pdm.search_count([("name", "like", MARK)]):
            skip("M48 actions", "predictions named SEED-A07")
        else:
            operator = u("iot.operator")
            items = env["fix.equipment"].search([("name", "not like", "AUDIT")], order="id")
            Action = env["fix.iot.action"]
            plans = (
                (items[6], "failure_predicted", 0.91, 6, "replace", "high", "done"),
                (items[7], "degrading", 0.74, 21, "inspect", "medium", "approved"),
                (items[9], "failure_predicted", 0.83, 10, "calibrate", "high", "proposed"),
            )
            for n, (item, kind, conf, days, act_type, prio, target) in enumerate(plans, 1):
                pred = Pdm.with_user(operator).create(
                    {
                        "name": f"{MARK}PDM-{n:02d}",
                        "equipment_id": item.id,
                        "prediction": kind,
                        "confidence": conf,
                        "estimated_days_to_failure": days,
                        "model_name": PDM_MODEL,
                        "feature_window_from": env.cr.now() - timedelta(days=30),
                        "feature_window_to": env.cr.now(),
                        "company_id": company.id,
                        "operating_unit_id": ou.id,
                    }
                )
                action = Action.with_user(operator).create(
                    {
                        "prediction_id": pred.id,
                        "action_type": act_type,
                        "priority": prio,
                        "technician_id": emp("dispatcher").id,
                        "scheduled_on": today + timedelta(days=2),
                        "notes": f"Raised from {pred.name} (SEED-A07)",
                    }
                )
                if target == "proposed":
                    continue
                approve(
                    action,
                    operator,
                    "Vibration and temperature trend above the alarm band for 72 hours (SEED-A07)",
                )
                if target == "done":
                    action.with_user(operator).action_dispatch()
                    action.with_user(operator).write(
                        {"outcome_evidence_ref": f"{MARK}JOB-CARD-{n:02d}"}
                    )
                    action.with_user(operator).action_done_confirmed(
                        note="Bearing wear confirmed at teardown; bearing replaced (SEED-A07)"
                    )

    with block("M48 retention change (requested and applied)"):
        Change = env["fix.iot.retention.change"]
        if Change.search_count([("reason", "like", MARK)]):
            skip("M48 retention", "changes with a SEED-A07 reason")
        else:
            admin_u = u("iot.admin")
            stream = env["fix.iot.stream"].search([], order="id", limit=1)
            change = Change.with_user(admin_u).create(
                {
                    "change_type": "retention",
                    "stream_id": stream.id,
                    "proposed_days": 400,
                    "reason": MARK + "PDPA 2026 retention review: keep 13 months for trend models",
                }
            )
            approve(change, admin_u, "Retention review agreed with the consent officer (SEED-A07)")
            # the M63 engine applies the approved change (action_apply) itself


def report(env):
    counts = []
    for model, domain in (
        ("fix.driver", [("license_no", "like", MARK)]),
        ("fix.vehicle.check", []),
        ("fix.vehicle.assignment", []),
        ("fix.vehicle.telemetry", [("device_ref", "like", MARK)]),
        ("fix.site.lease", [("name", "like", MARK)]),
        ("fix.site.lease.schedule", [("lease_id.name", "like", MARK)]),
        ("fix.site.lease.extract", [("lease_id.name", "like", MARK)]),
        ("fix.asset.cost.entry", []),
        ("fix.site.condition", [("name", "like", MARK)]),
        ("fix.site.pm", [("name", "like", MARK)]),
        ("fix.calibration.profile", []),
        ("fix.equipment.issue", [("reference", "like", MARK)]),
        ("fix.equipment.transfer", []),
        ("fix.equipment.verification", [("campaign_ref", "like", MARK)]),
        ("fix.device.estate", [("name", "like", MARK)]),
        ("fix.device.ownership", []),
        ("fix.iot.adapter", [("company_id", "!=", False)]),
        ("fix.iot.action", []),
        ("fix.iot.retention.change", []),
        ("fix.asset.alert", [("module", "=", "M48")]),
    ):
        counts.append(
            f"  {model:<28} {env[model].sudo().with_context(active_test=False).search_count(domain)}"
        )
    print("seed_a07_gap: blocks")
    for status, name, detail in RESULTS:
        print("  [{}] {}{}".format(status, name, (" - " + detail) if detail else ""))
    print("seed_a07_gap: row counts")
    print("\n".join(counts))


try:
    env  # noqa: B018 - provided by `odoo-bin shell`
except NameError:
    raise SystemExit(
        "seed_a07_gap: run inside `odoo-bin shell` (see the module docstring)"
    ) from None
seed(env)  # noqa: F821 - `env` comes from odoo-bin shell
report(env)  # noqa: F821
if os.environ.get("FIX_A07_COMMIT") == "1":
    env.cr.commit()  # noqa: F821
    print("seed_a07_gap: committed")
else:
    env.cr.rollback()  # noqa: F821
    print("seed_a07_gap: rolled back (set FIX_A07_COMMIT=1 to keep)")
