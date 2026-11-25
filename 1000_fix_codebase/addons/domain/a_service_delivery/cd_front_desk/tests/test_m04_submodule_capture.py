"""M04 Function Register: every sub-module page captures its own data.

Reported 2026-11-13 from the M04 workspace: not every sub-module page had a
data-capture button. Measured on the registry before the fix: 2 of the 10
pages offered one (Counter Workstation, Shift Operations).

- Token & Queue, Cash Drawer and Counter Sales had forms, but every M04 list
  said ``create: false``, so the page rule (p03_workspace.js fregCreate)
  offered nothing.
- Device Storage, Collection & Handover and Payment Capture work on an intake
  or sale that already exists and had no form at all. The registry's
  'Device Storage Assignment' and 'Handover (ID verified)' forms had been
  dropped because they opened a blank intake, and nothing replaced them.
- Banking & Deposits had no form although M50's deposit form exists.
- Branch Admin listed M30's branch master; the checklists the spec gives
  M04 (FR-FRD-020/024) were a report derived from cash shifts.
- And the forms that did exist could not save: the token, intake and shift
  require an operating unit that none of their forms asks for.

The button rule is JavaScript; it is executed here over the real registry by
the cd_p03_portal ``registry`` fixture. Each capture is then saved through
the real controller as a non-admin front-desk user, never as the superuser.
``odoo_env`` (addons/conftest.py): fix_test, rolled back after every test.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import types
from pathlib import Path

import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.tests.test_submodule_create_button import (  # noqa: F401 - fixture
    registry,
)
from odoo.exceptions import UserError

from . import test_a02_p0_m04 as p0

m04 = p0.m04

# sub-module -> (the form its button opens, the button's words)
EXPECTED = {
    "1": ("M04-form-token", "Issue Queue Token"),
    "2": ("M04-form-storage", "Walk-in Intake"),
    "3": ("M04-form-storage-assign", "Assign Storage Bin"),
    "4": ("M04-form-release", "Release Device to Collector"),
    "5": ("M04-form-countersale", "Counter Sale"),
    "6": ("M04-form-shift", "Open a Cash Shift"),
    "7": ("M04-form-payment", "Take Counter Payment"),
    # capture audit 2026-11-18: the shift handover (FR-FRD-022); shifts open on page 6
    "8": ("M04-form-shift-handover", "Write Shift Handover"),
    "9": ("M50-form-deposit", "Cash Deposit"),
    "10": ("M04-form-checklist", "Start Opening / Closing Checklist"),
}


def _rows(registry):  # noqa: F811 - the imported fixture
    return {r["no"]: r for r in registry["rows"] if r["mid"] == "M04"}


def _screens():
    """The M04 fragment's own screens (and M50's deposit form), read by node."""
    import odoo.addons.cd_p03_portal as portal

    src = Path(portal.__file__).parent / "static" / "src"
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the M04 fragment")
    probe = (
        "import { pathToFileURL } from 'node:url';\n"
        "import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';\n"
        "import { tmpdir } from 'node:os';\n"
        "import { join } from 'node:path';\n"
        "const dir = mkdtempSync(join(tmpdir(), 'm04cap'));\n"
        "const out = {};\n"
        "for (const src of process.argv.slice(1)) {\n"
        "  const file = join(dir, src.replace(/.*[\\\\/]/, '').replace('.js', '.mjs'));\n"
        "  writeFileSync(file, readFileSync(src, 'utf-8'));\n"
        "  const M = await import(pathToFileURL(file).href);\n"
        "  Object.assign(out, M.SCREENS || {});\n"
        "}\n"
        "console.log(JSON.stringify(out));\n"
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary, inline probe, our files
        [node, "--input-type=module", "-e", probe, str(src / "a02" / "m04.js")],
        capture_output=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


@pytest.fixture(scope="module")
def screens():
    return _screens()


@pytest.fixture
def ui(m04, monkeypatch):
    cls = api.P03GenericApiController
    ctl = cls()

    def call(name, user, **kw):
        monkeypatch.setattr(
            api, "request", types.SimpleNamespace(env=m04.env(user=user.id, su=False))
        )
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    return types.SimpleNamespace(
        records=lambda user, **kw: call("model_records", user, **kw),
        write=lambda user, **kw: call("model_write", user, **kw),
        action=lambda user, **kw: call("model_action", user, **kw),
    )


def _form_values(cfg, values):
    """Only what the form shows and lets the user type: a test cannot save a
    field the workspace never sends."""
    editable = {f["name"] for s in cfg["sections"] for f in s["fields"] if not f.get("readonly")}
    extra = set(values) - editable
    assert not extra, "%s does not let the user enter %s" % (cfg["title"], sorted(extra))
    return values


# --- every page offers its capture -------------------------------------------


def test_every_m04_submodule_offers_its_capture(registry):  # noqa: F811 - the imported fixture
    rows = _rows(registry)
    assert sorted(rows, key=int) == sorted(EXPECTED, key=int)
    got = {
        no: ((r["create"] or {}).get("screen"), (r["create"] or {}).get("label"))
        for no, r in rows.items()
    }
    assert got == EXPECTED
    assert all(r["formKind"] == "model_form" for r in rows.values())
    # each page names the form its button opens in "Forms Capturing It"
    for no, r in rows.items():
        chips = [registry["chips"].get("M04:" + f) for f in r["forms"]]
        assert EXPECTED[no][0] in chips, (no, r["forms"])


def test_the_branch_master_stays_with_m30(registry):  # noqa: F811 - the imported fixture
    """Branch Admin captures the branch's daily checklists; the branch itself
    is M30's configuration (M04 spec section 3.2)."""
    assert _rows(registry)["10"]["model"] == "fix.branch.checklist"
    assert not any(r["model"] == "fix.branch" for r in _rows(registry).values())


def test_every_m04_form_shows_fields_of_its_model(screens, odoo_env):
    """A form field the model lacks renders empty and can never be saved."""
    bad = []
    for sid, cfg in screens.items():
        if cfg.get("kind") not in ("model_form", "model_list"):
            continue
        model = odoo_env[cfg["model"]]
        names = list(cfg.get("cols") or [])
        for section in cfg.get("sections") or []:
            names += [f["name"] for f in section["fields"]]
        names += list((cfg.get("pickRecord") or {}).get("cols") or [])
        names += [c[0] for c in (cfg.get("pickRecord") or {}).get("domain") or []]
        bad += ["%s.%s" % (sid, n) for n in names if n not in model._fields]
        if cfg.get("lines"):
            child = odoo_env[model._fields[cfg["lines"]["field"]].comodel_name]
            bad += [
                "%s.lines.%s" % (sid, f["name"])
                for f in cfg["lines"]["fields"]
                if f["name"] not in child._fields
            ]
    assert not bad, "\n  ".join(bad)


def test_every_m04_model_is_served_to_the_workspace(screens):
    served = {cfg["model"] for cfg in screens.values() if cfg.get("model")}
    assert not served - set(api.SURFACES), served - set(api.SURFACES)
    for sid, cfg in screens.items():
        for act in cfg.get("actions") or []:
            assert act["m"] in api.SURFACES[cfg["model"]]["actions"], (sid, act["m"])


# --- each capture saves through the workspace, as a counter user -------------


def test_a_token_is_issued_from_the_form(m04, ui, screens):
    """Sub-module 1. The operating unit is the branch's: the form never asks."""
    cfg = screens["M04-form-token"]
    res = ui.write(
        m04.cashier,
        model="fix.token.queue",
        values=_form_values(
            cfg,
            {
                "branch_id": m04.branch.id,
                "service_type": "drop_off",
                "customer_id": m04.customer.id,
                "notes": "Screen flickers after a fall",
            },
        ),
    )
    assert "error" not in res, res
    token = m04.env["fix.token.queue"].browse(res["id"])
    assert token.operating_unit_id == m04.branch.operating_unit_id
    assert token.state == "waiting" and token.token_number >= 1


def test_a_walkin_intake_is_saved_from_the_form(m04, ui, screens):
    """Sub-module 2: it had a button, and the save failed on the operating unit."""
    res = ui.write(
        m04.cashier,
        model="fix.walkin.intake",
        values=_form_values(
            screens["M04-form-storage"],
            {
                "branch_id": m04.branch.id,
                "customer_id": m04.customer.id,
                "device_id": m04.device.id,
                "fault_description": "No power",
                "accessory_bag_barcode": "BAG-0001",
            },
        ),
    )
    assert "error" not in res, res
    intake = m04.env["fix.walkin.intake"].browse(res["id"])
    assert intake.operating_unit_id == m04.branch.operating_unit_id


def test_storage_and_handover_proof_are_recorded_on_the_picked_intake(m04, ui, screens):
    """Sub-modules 3 and 4: the intake is picked from the form's own list,
    the bin and the customer's signed receipt are written to it, and the
    hand-over then completes through the list action and its checks."""
    intake = m04.intake(device_id=m04.device.id)
    store, hand = screens["M04-form-storage-assign"], screens["M04-form-handover"]
    for cfg in (store, hand):
        listed = ui.records(
            m04.cashier,
            model="fix.walkin.intake",
            cols=cfg["pickRecord"]["cols"],
            domain=cfg["pickRecord"]["domain"],
        )
        assert intake.id in {r["id"] for r in listed["rows"]}

    loc = m04.env["fix.storage.location"].create({"branch_id": m04.branch.id, "code": "SHELF-B3"})
    res = ui.write(
        m04.cashier,
        model="fix.walkin.intake",
        record_id=intake.id,
        values=_form_values(
            store, {"storage_location_id": loc.id, "accessory_bag_barcode": "BAG-7"}
        ),
    )
    assert "error" not in res, res
    res = ui.write(
        m04.cashier,
        model="fix.walkin.intake",
        record_id=intake.id,
        values=_form_values(
            hand,
            {"handover_method": "signature", "customer_signature_attachment_id": m04.signature.id},
        ),
    )
    assert "error" not in res, res
    intake.invalidate_recordset()
    assert intake.storage_bin_code == "SHELF-B3"

    for method in ("action_submit_for_handover", "action_complete_handover"):
        res = ui.action(m04.cashier, model="fix.walkin.intake", ids=[intake.id], method=method)
        assert res["success"], (method, res)
    intake.invalidate_recordset()
    assert intake.state == "completed" and intake.service_order_id

    # handed over: it leaves both pick lists, and the proof is frozen
    for cfg in (store, hand):
        listed = ui.records(
            m04.cashier,
            model="fix.walkin.intake",
            cols=["state"],
            domain=cfg["pickRecord"]["domain"],
        )
        assert intake.id not in {r["id"] for r in listed["rows"]}
    res = ui.write(
        m04.cashier,
        model="fix.walkin.intake",
        record_id=intake.id,
        values={"handover_method": "otp"},
    )
    assert "error" in res


def test_a_shift_is_opened_and_a_sale_rung_up_and_paid_from_the_forms(m04, ui, screens):
    """Sub-modules 6/8 (open a shift), 5 (ring up a sale) and 7 (take the
    payment on the picked sale, then confirm it from Payment Capture)."""
    res = ui.write(
        m04.cashier,
        model="fix.cash.shift",
        values=_form_values(
            screens["M04-form-shift"],
            {
                "branch_id": m04.branch.id,
                "shift_date": str(fields.Date.today()),
                "shift_type": "morning",
                "operator_id": m04.cashier_emp.id,
                "opening_float": 2000.0,
            },
        ),
    )
    assert "error" not in res, res
    shift = m04.env["fix.cash.shift"].browse(res["id"])
    assert shift.state == "open"
    assert shift.operating_unit_id == m04.branch.operating_unit_id

    res = ui.write(
        m04.cashier,
        model="fix.counter.sale",
        values=_form_values(
            screens["M04-form-countersale"],
            {
                "shift_id": shift.id,
                "branch_id": m04.branch.id,
                "product_id": m04.product.id,
                "quantity": 1,
                "unit_price": 1000.0,
                "payment_method": "cash",
            },
        ),
    )
    assert "error" not in res, res
    sale = m04.env["fix.counter.sale"].browse(res["id"])

    pay = screens["M04-form-payment"]
    listed = ui.records(
        m04.cashier, model="fix.counter.sale", cols=["name"], domain=pay["pickRecord"]["domain"]
    )
    assert sale.id in {r["id"] for r in listed["rows"]}

    # a bKash payment with no TrxID is refused at confirm, in plain words
    res = ui.write(
        m04.cashier,
        model="fix.counter.sale",
        record_id=sale.id,
        values=_form_values(pay, {"payment_method": "bkash"}),
    )
    assert "error" not in res, res
    res = ui.action(m04.cashier, model="fix.counter.sale", ids=[sale.id], method="action_confirm")
    assert not res["success"] and "transaction reference" in res["error"]

    res = ui.write(
        m04.cashier,
        model="fix.counter.sale",
        record_id=sale.id,
        values=_form_values(pay, {"payment_method": "cash", "tendered_amount": 1000.0}),
    )
    assert "error" not in res, res
    res = ui.action(m04.cashier, model="fix.counter.sale", ids=[sale.id], method="action_confirm")
    assert res["success"], res
    sale.invalidate_recordset()
    shift.invalidate_recordset()
    assert sale.state == "confirmed" and sale.mushak_63_ref
    assert shift.cash_payments == sale.total


def test_a_plain_user_still_cannot_open_a_shift(m04, ui):
    res = ui.write(
        m04.plain,
        model="fix.cash.shift",
        values={
            "branch_id": m04.branch.id,
            "shift_type": "morning",
            "operator_id": m04.cashier_emp.id,
            "opening_float": 1.0,
        },
    )
    assert "error" in res


def test_a_deposit_is_recorded_from_the_banking_page(m04, ui):
    """Sub-module 9 offers M50's own deposit form; it is saved by a user with
    the accounting rights M50 requires, and refused to a counter cashier."""
    journal = m04.env["account.journal"].search([("type", "=", "bank")], limit=1)
    if not journal:
        pytest.skip("fix_test has no bank journal")
    accountant = (
        m04.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "m04 deposit accountant",
                "login": "m04.deposit.%d@cap.test" % m04.branch.id,
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            m04.env.ref("base.group_user").id,
                            m04.env.ref("account.group_account_user").id,
                        ],
                    )
                ],
            }
        )
    )
    vals = {
        "branch_id": m04.branch.id,
        "business_date": "2026-11-13",
        "journal_id": journal.id,
        "amount": 1500.0,
        "slip_no": "SLIP-M04-1",
        "operating_unit_id": m04.ou.id,
    }
    res = ui.write(accountant, model="fix.cash.deposit", values=vals)
    assert "error" not in res, res
    assert m04.env["fix.cash.deposit"].browse(res["id"]).state == "draft"
    assert "error" in ui.write(m04.cashier, model="fix.cash.deposit", values=vals)


def test_a_checklist_starts_with_its_items_and_is_signed_off(m04, ui, screens):
    """Sub-module 10 (and 8): FR-FRD-020/024 items, ticked on the form,
    signed off from the list, then frozen."""
    cfg = screens["M04-form-checklist"]
    res = ui.write(
        m04.cashier,
        model="fix.branch.checklist",
        values=_form_values(
            cfg,
            {
                "branch_id": m04.branch.id,
                "checklist_type": "opening",
                "checklist_date": "2026-11-13",
            },
        ),
    )
    assert "error" not in res, res
    chk = m04.env["fix.branch.checklist"].browse(res["id"])
    assert chk.operating_unit_id == m04.branch.operating_unit_id
    assert set(chk.line_ids.mapped("area")) == {"safety", "equipment", "stock", "cash", "staffing"}

    # a second opening checklist for the same branch and day is refused
    again = ui.write(
        m04.cashier,
        model="fix.branch.checklist",
        values={
            "branch_id": m04.branch.id,
            "checklist_type": "opening",
            "checklist_date": "2026-11-13",
        },
    )
    assert "error" in again

    # sign-off refuses an item neither ticked nor explained
    res = ui.action(
        m04.cashier, model="fix.branch.checklist", ids=[chk.id], method="action_complete"
    )
    assert not res["success"] and "not done" in res["error"]

    lines = chk.line_ids
    rows = [{"id": line.id, "values": {"done": True}} for line in lines[:-1]]
    rows.append({"id": lines[-1].id, "values": {"note": "Second agent on leave, manager covering"}})
    res = ui.write(
        m04.cashier,
        model="fix.branch.checklist",
        record_id=chk.id,
        values={"handover_notes": "Printer 2 jams"},
        lines={"field": "line_ids", "rows": rows},
    )
    assert "error" not in res, res
    res = ui.action(
        m04.cashier, model="fix.branch.checklist", ids=[chk.id], method="action_complete"
    )
    assert res["success"], res
    chk.invalidate_recordset()
    assert chk.state == "completed" and chk.completed_by_id == m04.cashier
    assert chk.open_item_count == 1

    # signed off: frozen, items included, and the stamp cannot be typed
    assert "error" in ui.write(
        m04.cashier, model="fix.branch.checklist", record_id=chk.id, values={"handover_notes": "x"}
    )
    assert "error" in ui.write(
        m04.cashier,
        model="fix.branch.checklist",
        record_id=chk.id,
        values={},
        lines={"field": "line_ids", "rows": [{"id": lines[-1].id, "values": {"done": True}}]},
    )
    # the workspace drops a typed sign-off (it is not a form input) ...
    res = ui.write(
        m04.cashier,
        model="fix.branch.checklist",
        values={
            "branch_id": m04.branch.id,
            "checklist_type": "closing",
            "checklist_date": "2026-11-13",
            "state": "completed",
            "completed_by_id": m04.manager.id,
        },
    )
    closing = m04.env["fix.branch.checklist"].browse(res["id"])
    assert closing.state == "draft" and not closing.completed_by_id
    # ... and the model refuses it from any other caller
    with pytest.raises(UserError, match="workflow"):
        m04.env["fix.branch.checklist"].with_user(m04.cashier).create(
            {
                "branch_id": m04.branch2.id,
                "checklist_type": "closing",
                "state": "completed",
            }
        )


def test_a_plain_user_cannot_sign_a_checklist_off(m04):
    chk = m04.env["fix.branch.checklist"].create(
        {"branch_id": m04.branch.id, "checklist_type": "closing"}
    )
    assert len(chk.line_ids) == 4
    with pytest.raises(Exception):  # noqa: B017 - ACL or role refusal, either is a refusal
        chk.with_user(m04.plain).action_complete()
