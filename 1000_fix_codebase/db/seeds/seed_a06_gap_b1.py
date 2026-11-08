"""seed_a06_gap_b1.py - synthetic seed rows for the A06 final pass, M15 and M41.

Why this exists. The A06 final pass added screens (Pick Lines, Warehouse
Zones), made the ownership-class change, the reservation and the warehouse
labour reports real, and put every warehouse step behind a scan, a supervisor
or a second person. On a copy of the live database those screens opened on
"0 records" (M15 Ownership-Class Changes, the M15 Reservations panel, and
the M41 Throughput, Pick Accuracy and Labour Productivity reports), so the
build looked unchanged. This file closes that, under the seed manifest rules:

  * synthetic only (DE-12), Bengali-first (DE-17), fixed values, no random;
  * state-complete where the screen shows a lifecycle (DE-16): class changes
    draft / awaiting approval / applied / rejected; waves released / picking /
    shipped; a transfer received in full and one received short;
  * idempotent: every block looks for its own `SEED-A06-` marker first, so a
    second run creates nothing;
  * no outbound anything (DE-11).

Every row is made through the PRODUCTION path, as the role that does it:
storekeepers raise and receive, an Inventory Controller posts direct receipts
and approves what a storekeeper requested, warehouse operators put away and
pick with bin and item scans, a warehouse supervisor releases the waves. No
state, approval stamp, cost or quantity is written directly, so the seed is
also a smoke test of the build against a real estate. It creates its own
locations, parts and warehouse, so live stock is not moved.

    PYTHONPATH=. .venv/Scripts/python.exe vendor/odoo/odoo-bin shell \
        -c infra/odoo-conf/local.resolved.conf -d fix_dev --no-http \
        < db/seeds/seed_a06_gap_b1.py

Each block runs in its own savepoint and reports, so one refusal from a
business rule is visible without hiding what the other blocks did.
"""

import time
from contextlib import contextmanager

MARK = "SEED-A06-"
RESULTS = []

SK = "cd_wms_structure.group_storekeeper"
OP = "cd_wms_structure.group_warehouse_operator"
IC = "cd_wms_structure.group_inventory_controller"
SUP = "cd_wms_structure.group_warehouse_supervisor"


def seed(env):
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)

    @contextmanager
    def block(name):
        started = time.monotonic()
        print(f"seed_a06_gap_b1: >> {name}", flush=True)
        try:
            with env.cr.savepoint():
                yield
            RESULTS.append(("ok", name, "%.1fs" % (time.monotonic() - started)))
        except Exception as exc:
            first = (str(exc).strip().splitlines() or [""])[0]
            RESULTS.append(("FAIL", name, f"{type(exc).__name__}: {first[:220]}"))

    def skip(name, why):
        print(f"seed_a06_gap_b1:    {name}: already seeded ({why})", flush=True)

    # ------------------------------------------------------------------ actors
    Users = env["res.users"].with_context(no_reset_password=True)

    def user(login, name, xmlids):
        found = Users.search([("login", "=", login)], limit=1)
        if found:
            return found
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return Users.create(
            {
                "name": name,
                "login": login,
                "email": login,
                "password": login,
                "group_ids": [(6, 0, groups)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )

    def employee(usr):
        Emp = env["hr.employee"]
        return Emp.search([("user_id", "=", usr.id)], limit=1) or Emp.create(
            {"name": usr.name, "user_id": usr.id}
        )

    with block("actors (storekeepers, controller, operators, supervisor)"):
        keeper = user("seed.a06.storekeeper@1000fix.test", "নাসরিন আক্তার (Storekeeper)", [SK])
        keeper2 = user("seed.a06.storekeeper2@1000fix.test", "জাহিদ হাসান (Storekeeper)", [SK])
        # the appointed Inventory Controller (appoint_approvers.py), else a synthetic one
        controller = Users.search([("login", "=", "seed.inventory.controller@1000fix.local")])
        if not controller or not controller.has_group(IC):
            controller = user(
                "seed.a06.controller@1000fix.test", "সাইফুল ইসলাম (Inventory Controller)", [IC]
            )
        operator = user("seed.a06.operator@1000fix.test", "রবিউল করিম (Warehouse Operator)", [OP])
        operator2 = user("seed.a06.operator2@1000fix.test", "শারমিন সুলতানা (Warehouse Operator)", [OP])
        supervisor = user(
            "seed.a06.supervisor@1000fix.test", "মোস্তফা কামাল (Warehouse Supervisor)", [SUP]
        )
        op_emp = employee(operator)
        employee(operator2)

    def actors():
        return (
            Users.search([("login", "=", "seed.a06.storekeeper@1000fix.test")]),
            Users.search([("login", "=", "seed.a06.storekeeper2@1000fix.test")]),
            Users.search(
                [
                    (
                        "login",
                        "in",
                        [
                            "seed.inventory.controller@1000fix.local",
                            "seed.a06.controller@1000fix.test",
                        ],
                    )
                ]
            ).filtered(lambda u: u.has_group(IC))[:1],
            Users.search([("login", "=", "seed.a06.operator@1000fix.test")]),
            Users.search([("login", "=", "seed.a06.operator2@1000fix.test")]),
            Users.search([("login", "=", "seed.a06.supervisor@1000fix.test")]),
        )

    keeper, keeper2, controller, operator, operator2, supervisor = actors()
    op_emp = env["hr.employee"].search([("user_id", "=", operator.id)], limit=1)

    # -------------------------------------------------------- locations, parts
    Loc = env["fix.stock.location"]
    Part = env["fix.spare.part"]
    with block("M15 locations and parts (storekeeper; cost by the controller)"):
        for code, name, kind in (
            ("SA6-CEN", MARK + "কেন্দ্রীয় গুদাম (Central Store)", "central"),
            ("SA6-HUB", MARK + "মিরপুর হাব (Mirpur Hub)", "branch"),
        ):
            if not Loc.search([("code", "=", code), ("company_id", "=", env.company.id)]):
                Loc.with_user(keeper).create(
                    {
                        "name": name,
                        "code": code,
                        "location_type": kind,
                        "operating_unit_id": ou.id,
                    }
                )
        for number, name, category, cost in (
            ("SA6-P01", MARK + "ডিসপ্লে প্যানেল ৬.৫ ইঞ্চি (Display Panel 6.5in)", "display", 2400.0),
            ("SA6-P02", MARK + "চার্জিং পোর্ট বোর্ড (Charging Port Board)", "charging_port", 650.0),
        ):
            part = Part.search([("part_number", "=", number), ("company_id", "=", env.company.id)])
            if not part:
                part = Part.with_user(keeper).create(
                    {"name": name, "part_number": number, "part_category": category}
                )
                part.with_user(controller).action_set_standard_cost(cost)

    central = Loc.search([("code", "=", "SA6-CEN"), ("company_id", "=", env.company.id)])
    hub = Loc.search([("code", "=", "SA6-HUB"), ("company_id", "=", env.company.id)])
    p01 = Part.search([("part_number", "=", "SA6-P01"), ("company_id", "=", env.company.id)])
    p02 = Part.search([("part_number", "=", "SA6-P02"), ("company_id", "=", env.company.id)])

    supplier = env["res.partner"].search([("name", "=", MARK + "ঢাকা পার্টস লিমিটেড")], limit=1)
    if not supplier:
        supplier = env["res.partner"].create({"name": MARK + "ঢাকা পার্টস লিমিটেড", "is_company": True})

    # -------------------------------------------------------- goods receipt
    Receipt = env["fix.stock.receipt"]
    with block("M15 direct receipt (storekeeper inspects, controller posts)"):
        reason = MARK + "opening stock for the synthetic warehouse"
        if Receipt.search([("direct_reason", "=", reason)]):
            skip("M15 direct receipt", reason)
        else:
            rec = Receipt.with_user(keeper).create(
                {
                    "partner_id": supplier.id,
                    "location_id": central.id,
                    "operating_unit_id": ou.id,
                    "direct_reason": reason,
                    "line_ids": [
                        (0, 0, {"part_id": p01.id, "qty_received": 60, "qty_accepted": 60}),
                        (0, 0, {"part_id": p02.id, "qty_received": 40, "qty_accepted": 38}),
                    ],
                }
            )
            # the cost is restricted: the controller enters it while it is a draft
            for line, cost in zip(rec.line_ids, (2400.0, 650.0), strict=True):
                line.with_user(controller).write({"unit_cost": cost})
            rec.with_user(keeper).action_inspect()
            rec.with_user(controller).action_post()

    # -------------------------------------------------------- class changes
    Change = env["fix.stock.class.change"]
    with block("M15 ownership-class changes (draft, awaiting, applied, rejected)"):
        for qty, outcome in ((1, "draft"), (2, "submitted"), (3, "done"), (4, "rejected")):
            reason = f"{MARK}owned to warranty reserve: {outcome}"
            if Change.search([("reason", "=", reason)]):
                continue
            change = Change.with_user(keeper).create(
                {
                    "part_id": p02.id,
                    "location_id": central.id,
                    "from_class": "owned",
                    "to_class": "warranty",
                    "qty": qty,
                    "reason": reason,
                }
            )
            if outcome == "draft":
                continue
            change.with_user(keeper).action_submit()
            if outcome == "done":
                change.with_user(controller).action_approve(note="Warranty reserve topped up")
            elif outcome == "rejected":
                change.with_user(controller).action_reject(note="Reserve already sufficient")

    # -------------------------------------------------------- warehouse structure
    Warehouse = env["fix.warehouse"]
    Zone = env["fix.warehouse.zone"]
    Bin = env["fix.warehouse.bin"]
    with block("M41 warehouse, zones and bins (operator)"):
        wh = Warehouse.search([("code", "=", "SA6WH"), ("company_id", "=", env.company.id)])
        if not wh:
            wh = Warehouse.with_user(operator).create(
                {
                    "name": MARK + "কেন্দ্রীয় ওয়্যারহাউস (Central Warehouse)",
                    "code": "SA6WH",
                    "operating_unit_id": ou.id,
                    "stock_location_id": central.id,
                }
            )
        for code, name, kind in (
            ("SA6S", MARK + "প্রধান স্টোরেজ (Main Storage)", "storage"),
            ("SA6I", MARK + "মান পরিদর্শন (Quality Inspection)", "inspection"),
            ("SA6Q", MARK + "কোয়ারেন্টিন (Quarantine)", "quarantine"),
        ):
            if not Zone.search([("code", "=", code), ("warehouse_id", "=", wh.id)]):
                Zone.with_user(operator).create(
                    {"warehouse_id": wh.id, "name": name, "code": code, "zone_type": kind}
                )
        storage = Zone.search([("code", "=", "SA6S"), ("warehouse_id", "=", wh.id)])
        for name in ("SA6-A-01", "SA6-A-02", "SA6-A-03"):
            if not Bin.search([("name", "=", name), ("zone_id", "=", storage.id)]):
                Bin.with_user(operator).create(
                    {
                        "zone_id": storage.id,
                        "name": name,
                        "barcode": "BC-" + name,
                        "capacity_qty": 50,
                    }
                )

    bin1 = Bin.search([("name", "=", "SA6-A-01")], limit=1)
    bin2 = Bin.search([("name", "=", "SA6-A-02")], limit=1)

    # -------------------------------------------------------- put-away
    Putaway = env["fix.wms.putaway"]
    with block("M41 put-away with bin and item scans (operator)"):
        for part, the_bin, qty in ((p01, bin1, 20), (p02, bin2, 15)):
            ref = f"{MARK}opening {part.part_number}"
            if Putaway.search([("from_ref", "=", ref)]):
                continue
            line = env["fix.stock.receipt.line"].search(
                [
                    ("part_id", "=", part.id),
                    ("is_posted", "=", True),
                    ("receipt_id.location_id", "=", central.id),
                ],
                limit=1,
            )
            pa = Putaway.with_user(operator).create(
                {
                    "part_id": part.id,
                    "qty": qty,
                    "to_bin_id": the_bin.id,
                    "receipt_line_id": line.id,
                    "from_ref": ref,
                }
            )
            pa.with_user(operator).action_complete(
                bin_code=the_bin.barcode, item_code=part.part_number
            )

    # -------------------------------------------------------- waves
    Wave = env["fix.wms.wave"]
    Task = env["fix.wms.task"]

    def seed_wave(part, the_bin, qty):
        """The seed's wave of this part and quantity, if it exists."""
        return Wave.search(
            [
                ("line_ids.part_id", "=", part.id),
                ("line_ids.bin_id", "=", the_bin.id),
                ("line_ids.qty", "=", qty),
            ],
            limit=1,
        )

    def new_wave(part, the_bin, qty):
        wave = Wave.with_user(operator).create(
            {"line_ids": [(0, 0, {"part_id": part.id, "bin_id": the_bin.id, "qty": qty})]}
        )
        wave.with_user(supervisor).action_release()
        return wave

    with block("M41 wave released, awaiting pick (pick lines, M15 reservation, RF queue)"):
        if seed_wave(p01, bin1, 4):
            skip("M41 released wave", "wave of 4 x SA6-P01")
        else:
            new_wave(p01, bin1, 4)

    with block("M41 wave picked through its task, packed, loaded and shipped"):
        if seed_wave(p02, bin2, 5):
            skip("M41 shipped wave", "wave of 5 x SA6-P02")
        else:
            wave = new_wave(p02, bin2, 5)
            line = wave.line_ids
            task = Task.search([("wave_line_id", "=", line.id)], limit=1)
            # the operator claims the free task, then completes it with his scans
            task.with_user(operator).write({"assignee_id": op_emp.id})
            task.with_user(operator).action_assign()
            task.with_user(operator).action_done(scan=f"{bin2.barcode} {p02.part_number}")
            carton = (
                env["fix.wms.carton"]
                .with_user(operator)
                .create(
                    {"wave_id": wave.id, "carton_size": "s", "contents_qty": 5, "weight_kg": 1.8}
                )
            )
            carton.with_user(operator).action_seal()
            wave.with_user(operator).action_packed()
            stage = (
                env["fix.wms.stage"]
                .with_user(operator)
                .create({"wave_id": wave.id, "lane": MARK + "L1", "load_ref": "DHA-METRO-TA-1144"})
            )
            wave.with_user(operator).action_stage()
            stage.with_user(operator).action_load(carton_scans=carton.name)
            stage.with_user(operator).action_dispatch()

    with block("M41 wave being picked by scan (picking)"):
        if seed_wave(p01, bin1, 3):
            skip("M41 picking wave", "wave of 3 x SA6-P01")
        else:
            wave = new_wave(p01, bin1, 3)
            wave.line_ids.with_user(operator2).action_scan_pick(
                bin_code=bin1.barcode, item_code=p01.part_number
            )

    # -------------------------------------------------------- transfers
    Transfer = env["fix.stock.transfer"]
    with block("M15 transfers (received in full; received short, discrepancy open)"):
        if Transfer.search(
            [("from_location_id", "=", central.id), ("to_location_id", "=", hub.id)]
        ):
            skip("M15 transfers", "seed central to seed hub")
        else:
            for part, qty, arrived in ((p01, 5, None), (p02, 6, 4)):
                transfer = Transfer.with_user(keeper).create(
                    {
                        "from_location_id": central.id,
                        "to_location_id": hub.id,
                        "operating_unit_id": ou.id,
                        "line_ids": [(0, 0, {"part_id": part.id, "qty": qty})],
                    }
                )
                transfer.with_user(keeper).action_submit()
                transfer.with_user(controller).action_approve()
                transfer.with_user(keeper).action_dispatch()
                if arrived is not None:
                    transfer.line_ids.with_user(keeper2).write({"received_qty": arrived})
                transfer.with_user(keeper2).action_receive()


def report(env):
    counts = []
    for model, domain in (
        ("fix.stock.class.change", [("reason", "like", MARK)]),
        ("fix.stock.onhand", [("reserved", ">", 0)]),
        ("fix.warehouse.zone", [("name", "like", MARK)]),
        ("fix.wms.wave.line", [("wave_id.line_ids.part_id.part_number", "like", "SA6-")]),
        ("fix.wms.task", [("state", "=", "done"), ("done_by_id", "!=", False)]),
        ("fix.stock.transfer", [("from_location_id.code", "=", "SA6-CEN")]),
    ):
        counts.append(f"  {model:<28} {env[model].sudo().search_count(domain)}")
    print("seed_a06_gap_b1: blocks")
    for status, name, detail in RESULTS:
        print("  [{}] {}{}".format(status, name, (" - " + detail) if detail else ""))
    print("seed_a06_gap_b1: row counts after seeding")
    print("\n".join(counts))


try:
    env  # noqa: B018 - provided by `odoo-bin shell`
except NameError:
    raise SystemExit(
        "seed_a06_gap_b1: run inside `odoo-bin shell` (see the module docstring)"
    ) from None
seed(env)  # noqa: F821 - `env` comes from odoo-bin shell
env.cr.commit()  # noqa: F821
report(env)  # noqa: F821
