# A06 final pass - M15 and M41 screens (A1..A7): a control is not done until a user
# can reach it. Every step runs through the real /p03/model/* endpoints as a
# NON-ADMIN user with the real role, and the refusal is asserted too.
import inspect
import itertools
import re
import types
import uuid
from pathlib import Path

import pytest
from odoo.addons.cd_p03_portal.controllers import a06
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.exceptions import AccessError, UserError

SK = "cd_wms_structure.group_storekeeper"
OP = "cd_wms_structure.group_warehouse_operator"
IC = "cd_wms_structure.group_inventory_controller"
SUP = "cd_wms_structure.group_warehouse_supervisor"

_SEQ = itertools.count(1)
STATIC = Path(g.__file__).resolve().parents[1] / "static" / "src" / "a06"


def _endpoint(name):
    fn = getattr(g.P03GenericApiController, name)
    return getattr(fn, "original_endpoint", fn)


class Screens:
    """The endpoints as the given user, and the fragments as the browser sees them."""

    def __init__(self, env):
        self.env = env
        self.tag = uuid.uuid4().hex[:6].upper()
        self.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
        self.ctl = g.P03GenericApiController()

    def user(self, login, *groups):
        ids = [self.env.ref("base.group_user").id] + [self.env.ref(x).id for x in groups]
        return (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "%s %s" % (login, self.tag),
                    "login": "a6fs.%s.%s.%d@a06.test" % (login, self.tag.lower(), next(_SEQ)),
                    "group_ids": [(6, 0, ids)],
                    "assigned_operating_unit_ids": [(6, 0, self.ou.ids)],
                    "default_operating_unit_id": self.ou.id,
                }
            )
        )

    def call(self, user, name, **kw):
        old = getattr(g, "request", None)
        g.request = types.SimpleNamespace(env=self.env(user=user.id))
        try:
            return _endpoint(name)(self.ctl, **kw)
        finally:
            g.request = old

    def act(self, user, record, method, **kwargs):
        return self.call(
            user, "model_action", model=record._name, ids=record.ids, method=method, kwargs=kwargs
        )

    def write(self, user, model, values, record_id=None, lines=None):
        return self.call(
            user, "model_write", model=model, record_id=record_id, values=values, lines=lines
        )

    def form(self, user, model, fields, record_id=None, **kw):
        return self.call(user, "model_form", model=model, fields=fields, record_id=record_id, **kw)

    def records(self, user, model, cols, **kw):
        return self.call(user, "model_records", model=model, cols=cols, **kw)


@pytest.fixture
def s(odoo_env):
    world = Screens(odoo_env)
    world.keeper = world.user("keeper", SK)
    world.keeper2 = world.user("keeper2", SK)
    world.operator = world.user("operator", OP)
    world.supervisor = world.user("supervisor", SUP)
    world.controller = world.user("controller", IC)
    world.controller2 = world.user("controller2", IC)
    world.supplier = odoo_env["res.partner"].create({"name": "A6FS Supplier " + world.tag})
    world.tech = odoo_env["hr.employee"].create({"name": "A6FS Tech " + world.tag})
    Loc = odoo_env["fix.stock.location"]
    world.central = Loc.create(
        {
            "name": "A6FS Central",
            "code": "A6C-" + world.tag,
            "location_type": "central",
            "operating_unit_id": world.ou.id,
        }
    )
    world.hub = Loc.create(
        {
            "name": "A6FS Hub",
            "code": "A6H-" + world.tag,
            "location_type": "branch",
            "operating_unit_id": world.ou.id,
        }
    )
    world.part = odoo_env["fix.spare.part"].create(
        {"name": "A6FS Part", "part_number": "A6P-" + world.tag, "unit_cost": 500.0}
    )
    odoo_env["fix.stock.onhand"]._apply(world.part, world.central, "owned", 10.0, 500.0)
    return world


# =========================================================== A1 spare part master
def test_a1_part_form_offers_the_mapping_and_saves_it(s):
    names = [
        {"name": n} for n in ("product_id", "is_serialized", "uom", "barcode", "storage_class")
    ]
    meta = s.form(s.keeper, "fix.spare.part", names, s.part.id)
    assert {f["name"] for f in meta["fields"]} == {n["name"] for n in names}
    assert not any(f["readonly"] for f in meta["fields"])
    product = s.env["product.product"].create({"name": "A6FS Bought " + s.tag})
    res = s.write(
        s.keeper,
        "fix.spare.part",
        {"product_id": product.id, "barcode": "BC-" + s.tag, "uom": "PCS"},
        s.part.id,
    )
    assert "error" not in res, res
    assert s.part.product_id == product and s.part.barcode == "BC-" + s.tag


def test_a1_part_status_buttons_are_the_controllers(s):
    res = s.act(s.keeper, s.part, "action_discontinue")
    assert not res["success"] and "Inventory Controller" in res["error"]
    assert s.part.state == "active"
    assert s.act(s.controller, s.part, "action_discontinue")["success"]
    assert s.part.state == "discontinued"
    assert s.act(s.controller, s.part, "action_mark_obsolete")["success"]
    assert s.part.state == "obsolete"
    assert s.act(s.controller, s.part, "action_reactivate")["success"]
    assert s.part.state == "active"


def test_a1_standard_cost_is_the_controllers_and_not_on_the_m41_surface(s):
    # A06 ERP audit F32: no cost on M41 (spec section 13): the action left the
    # M41 surface; the control itself still holds on the model
    res = s.act(s.controller, s.part, "action_set_standard_cost", cost=450.0)
    assert not res["success"]
    with pytest.raises((AccessError, UserError)), s.env.cr.savepoint():
        s.part.with_user(s.keeper).action_set_standard_cost(cost=1.0)
    s.part.with_user(s.controller).action_set_standard_cost(cost=450.0)
    assert s.part.unit_cost == 450.0


def test_a1_serial_control_cannot_flip_while_stock_is_held(s):
    res = s.write(s.keeper, "fix.spare.part", {"is_serialized": True}, s.part.id)
    assert "error" in res and "holds stock" in res["error"]
    assert not s.part.is_serialized


# =========================================================== A2 stock location
def test_a2_a_van_can_be_created_on_the_form_with_its_custodian(s):
    # A06 ERP audit A36: naming a van's custodian is the Inventory Controller's
    # (a storekeeper could otherwise hand stock to any technician)
    res = s.write(
        s.keeper,
        "fix.stock.location",
        {
            "name": "A6FS Van K",
            "code": "A6K-" + s.tag,
            "location_type": "van",
            "technician_id": s.tech.id,
            "operating_unit_id": s.ou.id,
        },
    )
    assert "error" in res, res
    res = s.write(
        s.controller,
        "fix.stock.location",
        {
            "name": "A6FS Van",
            "code": "A6V-" + s.tag,
            "location_type": "van",
            "technician_id": s.tech.id,
            "operating_unit_id": s.ou.id,
        },
    )
    assert "error" not in res, res
    van = s.env["fix.stock.location"].browse(res["id"])
    assert van.location_type == "van" and van.technician_id == s.tech
    # a van with no custodian is refused
    res = s.write(
        s.keeper,
        "fix.stock.location",
        {"name": "No Custodian", "code": "A6N-" + s.tag, "location_type": "van"},
    )
    assert "error" in res


def test_a2_custody_changes_only_by_a_controller(s):
    emp = s.env["hr.employee"].create({"name": "Self " + s.tag, "user_id": s.keeper.id})
    van = s.env["fix.stock.location"].create(
        {"name": "V", "code": "A6W-" + s.tag, "location_type": "van", "technician_id": s.tech.id}
    )
    res = s.write(s.keeper, "fix.stock.location", {"technician_id": emp.id}, van.id)
    assert "error" in res
    assert van.technician_id == s.tech
    meta = s.form(s.keeper, "fix.stock.location", [{"name": "technician_id"}], van.id)
    assert meta["fields"][0]["readonly"], "the form does not offer what the save refuses"
    assert "error" not in s.write(
        s.controller, "fix.stock.location", {"technician_id": emp.id}, van.id
    )
    assert van.technician_id == emp


def test_a2_location_buttons(s):
    assert not s.act(s.keeper, s.hub, "action_set_inactive")["success"]
    assert s.act(s.controller, s.hub, "action_set_inactive")["success"]
    assert s.hub.state == "inactive"
    assert s.act(s.controller, s.hub, "action_set_active")["success"]
    assert s.hub.state == "active"


def test_a2_van_audit_button_takes_the_totals(s):
    emp = s.env["hr.employee"].create({"name": "Van Tech " + s.tag, "user_id": s.controller2.id})
    van = s.env["fix.stock.location"].create(
        {"name": "V", "code": "A6U-" + s.tag, "location_type": "van", "technician_id": emp.id}
    )
    kw = {"audited_count": 4, "discrepancy_count": 1}
    assert not s.act(s.keeper, van, "action_audit_van_stock", **kw)["success"]
    assert not s.act(s.controller2, van, "action_audit_van_stock", **kw)["success"], "custodian"
    assert not s.act(s.controller, van, "action_audit_van_stock", audited_count=0)["success"]
    assert not s.act(
        s.controller, van, "action_audit_van_stock", audited_count=1, discrepancy_count=2
    )["success"]
    assert s.act(s.controller, van, "action_audit_van_stock", **kw)["success"]
    assert van.audit_discrepancy_count == 1 and van.last_audit_date


# =========================================================== A3 pick lines
def _wms(s):
    env = s.env
    wh = env["fix.warehouse"].create(
        {
            "name": "A6FS WH",
            "code": s.tag,
            "operating_unit_id": s.ou.id,
            "stock_location_id": s.central.id,
            "wms_enabled": True,
        }
    )
    zone = env["fix.warehouse.zone"].create(
        {"warehouse_id": wh.id, "name": "Pick", "code": "PK", "zone_type": "storage"}
    )
    the_bin = env["fix.warehouse.bin"].create({"zone_id": zone.id, "name": "B-" + s.tag})
    # A06 ERP audit O7 / F16: floor work is an operative's of THIS warehouse
    emp = env["hr.employee"].create({"name": "A6FS Op " + s.tag, "user_id": s.operator.id})
    env["fix.wms.operative"].create({"employee_id": emp.id, "warehouse_id": wh.id})
    env["fix.wms.slot"].sudo()._guarded().create(
        {"part_id": s.part.id, "bin_id": the_bin.id, "qty": 8.0}
    )
    wave = (
        env["fix.wms.wave"]
        .with_user(s.operator)
        .create({"line_ids": [(0, 0, {"part_id": s.part.id, "bin_id": the_bin.id, "qty": 2.0})]})
    )
    return wh, zone, the_bin, wave


def test_a3_pick_line_screen_scans_and_picks(s):
    _wh, _zone, the_bin, wave = _wms(s)
    assert s.act(s.supervisor, wave, "action_release")["success"]
    line = wave.line_ids
    res = s.act(
        s.operator, line, "action_scan_pick", bin_code="WRONG", item_code=s.part.part_number
    )
    assert not res["success"] and "Scanned bin" in res["error"]
    res = s.act(
        s.operator,
        line,
        "action_scan_pick",
        bin_code=the_bin.name,
        item_code=s.part.part_number,
        serial="",
    )
    assert res["success"], res
    assert line.state == "picked" and line.picked_qty == 2.0


def test_a3_pick_lines_show_a_real_name_in_a_picker(s):
    _wh, _zone, _bin, wave = _wms(s)
    s.env.flush_all()
    rows = s.records(
        s.operator, "fix.wms.wave.line", ["wave_id", "part_id", "bin_id", "qty", "lot_id", "state"]
    )
    assert any(r["wave_id"]["name"] == wave.name for r in rows["rows"])
    meta = s.form(
        s.supervisor,
        "fix.wms.task",
        [{"name": "wave_line_id", "domain": [["state", "=", "pending"]]}],
    )
    choice = next(c for c in meta["fields"][0]["choices"] if c["id"] == wave.line_ids.id)
    assert wave.name in choice["label"] and s.part.part_number in choice["label"]
    assert "fix.wms.wave.line," not in choice["label"]


# =========================================================== A4 zones
def test_a4_a_quarantine_zone_can_be_created_on_screen(s):
    wh, _zone, _bin, _wave = _wms(s)
    res = s.write(
        s.operator,
        "fix.warehouse.zone",
        {"warehouse_id": wh.id, "name": "QC hold", "code": "QH", "zone_type": "quarantine"},
    )
    assert "error" not in res, res
    zone = s.env["fix.warehouse.zone"].browse(res["id"])
    assert zone.zone_type == "quarantine" and not zone.reservable
    # the keeper has no write on the structure
    res = s.write(
        s.keeper,
        "fix.warehouse.zone",
        {"warehouse_id": wh.id, "name": "X", "code": "XX", "zone_type": "storage"},
    )
    assert "error" in res
    # reservable is the system's
    res = s.write(s.operator, "fix.warehouse.zone", {"reservable": True}, zone.id)
    assert "error" in res


# =========================================================== A5 counts
def test_a5_action_post_is_off_the_count_surface(s):
    count = (
        s.env["fix.stock.count"]
        .with_user(s.keeper)
        .create(
            {
                "location_id": s.central.id,
                "line_ids": [(0, 0, {"part_id": s.part.id, "counted_qty": 10.0})],
            }
        )
    )
    res = s.act(s.keeper, count, "action_post")
    assert not res["success"] and "not available" in res["error"]
    assert s.act(s.keeper, count, "action_submit")["success"]
    assert count.state == "posted"


def test_a5_the_count_form_shows_the_approver_variance_and_value(s):
    count = (
        s.env["fix.stock.count"]
        .with_user(s.keeper)
        .create(
            {
                "location_id": s.central.id,
                "line_ids": [(0, 0, {"part_id": s.part.id, "counted_qty": 7.0})],
            }
        )
    )
    fields = [{"name": "variance_value"}, {"name": "adjustment_value"}]
    lines = {
        "field": "line_ids",
        "fields": [{"name": "counted_qty"}, {"name": "expected_qty"}, {"name": "variance"}],
    }
    boss = s.form(s.controller, "fix.stock.count", fields, count.id, lines=lines)
    assert boss["record"]["variance_value"] == -1500.0
    assert boss["record"]["adjustment_value"] == 1500.0
    assert boss["lines"]["rows"][0]["expected_qty"] == 10.0
    assert boss["lines"]["rows"][0]["variance"] == -3.0
    mine = s.form(s.keeper, "fix.stock.count", fields, count.id, lines=lines)
    assert not mine["fields"], "the counter is offered no value"
    assert not mine["lines"]["rows"][0]["expected_qty"]
    assert not mine["lines"]["rows"][0]["variance"]


# =========================================================== B10 / B18 on screen
def test_b18_the_workspace_serves_cost_only_to_a_cost_viewer(s):
    cols = ["part_id", "qty", "unit_cost"]
    mine = s.records(s.keeper, "fix.stock.onhand", cols, domain=[["part_id", "=", s.part.id]])
    assert mine["rows"] and all("unit_cost" not in r for r in mine["rows"])
    boss = s.records(s.controller, "fix.stock.onhand", cols, domain=[["part_id", "=", s.part.id]])
    assert boss["rows"][0]["unit_cost"] == 500.0
    row = s.env["fix.stock.onhand"]._bucket(s.part, s.central, "owned")
    form = s.form(s.keeper, "fix.stock.onhand", [{"name": "qty"}, {"name": "unit_cost"}], row.id)
    assert [f["name"] for f in form["fields"]] == ["qty"]
    assert "unit_cost" not in form["record"]


def test_b10_the_recon_list_and_form_are_blind_to_the_counter(s):
    emp = s.env["hr.employee"].create({"name": "Tech " + s.tag, "user_id": s.keeper.id})
    van = s.env["fix.stock.location"].create(
        {"name": "V", "code": "A6R-" + s.tag, "location_type": "van", "technician_id": emp.id}
    )
    recon = s.env["fix.stock.van.recon"].with_user(s.keeper).create({"location_id": van.id})
    cols = ["name", "counted_qty", "expected_qty", "variance"]
    rows = s.records(s.keeper, "fix.stock.van.recon", cols, domain=[["id", "=", recon.id]])["rows"]
    assert rows and "expected_qty" not in rows[0] and "variance" not in rows[0]
    form = s.form(
        s.keeper,
        "fix.stock.van.recon",
        [{"name": "counted_qty"}, {"name": "expected_qty"}],
        recon.id,
    )
    assert [f["name"] for f in form["fields"]] == ["counted_qty"]


def test_b15_the_receiver_saves_the_received_quantity_on_the_form(s):
    transfer = (
        s.env["fix.stock.transfer"]
        .with_user(s.keeper)
        .create(
            {
                "from_location_id": s.central.id,
                "to_location_id": s.hub.id,
                "line_ids": [(0, 0, {"part_id": s.part.id, "qty": 5.0})],
            }
        )
    )
    assert s.act(s.keeper, transfer, "action_submit")["success"]
    assert s.act(s.controller, transfer, "action_approve")["success"]
    assert s.act(s.keeper, transfer, "action_dispatch")["success"]
    line = transfer.line_ids
    # the grid posts every column it shows
    rows = [
        {
            "id": line.id,
            "values": {
                "part_id": {"id": s.part.id},
                "qty": 5.0,
                "received_qty": 4.0,
                "discrepancy_qty": 0.0,
            },
        }
    ]
    res = s.write(
        s.keeper2, "fix.stock.transfer", {}, transfer.id, {"field": "line_ids", "rows": rows}
    )
    assert "error" not in res, res
    assert line.received_qty == 4.0
    assert s.act(s.keeper2, transfer, "action_receive")["success"]
    assert transfer.state == "discrepancy"
    res = s.act(
        s.controller, transfer, "action_resolve_discrepancy", resolution="found", note="Late van"
    )
    assert res["success"], res
    assert transfer.state == "received"


# =========================================================== A6 / A7 the fragments
def _fragment(name):
    return (STATIC / name).read_text(encoding="utf-8")


def _screens(text):
    """screen id -> its body, as form_fields.py cuts the fragment."""
    starts = [
        (m.start(), m.group(1))
        for m in re.finditer(r"^[ \t]{2,6}'([A-Za-z0-9:_-]+)':\s*\{", text, re.M)
    ]
    return {
        sid: text[pos : (starts[i + 1][0] if i + 1 < len(starts) else len(text))]
        for i, (pos, sid) in enumerate(starts)
    }


@pytest.mark.parametrize("fragment", ["m15.js", "m41.js"])
def test_a6_every_form_status_covers_its_selection(odoo_env, fragment):
    missing = {}
    for sid, body in _screens(_fragment(fragment)).items():
        if "kind: 'model_form'" not in body:
            continue
        model = re.search(r"\bmodel:\s*'([a-z0-9_.]+)'", body).group(1)
        status = re.search(
            r"status:\s*\{\s*field:\s*'(\w+)'(?:,\s*labels:\s*\{(.*?)\})?", body, re.S
        )
        if not status:
            continue
        labels = set(re.findall(r"(\w+):\s*'", status.group(2) or ""))
        keys = set(dict(odoo_env[model]._fields[status.group(1)]._description_selection(odoo_env)))
        if keys - labels:
            missing[sid] = sorted(keys - labels)
    assert not missing, missing


def test_a6_receiving_row_opens_the_receipt_form():
    text = _fragment("m41.js")
    assert re.search(r"'M41-receiving':\s*'M15-form-receipt'", text)
    assert "'M15-form-receipt': {" in _fragment("m15.js")


@pytest.mark.parametrize("fragment", ["m15.js", "m41.js"])
def test_a7_every_button_collects_what_its_method_requires(odoo_env, fragment):
    """Sweep: a button whose method needs an argument prompts for it, under the
    parameter name the method takes, and the method is on the surface."""
    problems = []
    for sid, body in _screens(_fragment(fragment)).items():
        if "kind: 'model_list'" not in body:
            continue
        model = re.search(r"\bmodel:\s*'([a-z0-9_.]+)'", body).group(1)
        for match in re.finditer(r"\{\s*m:\s*'(\w+)'(.*?)(?=\{\s*m:\s*'|\Z)", body, re.S):
            method, cfg = match.group(1), match.group(2)
            where = "%s %s.%s" % (sid, model, method)
            if method not in a06.SURFACES.get(model, {}).get("actions", ()):
                problems.append(where + " not on the surface")
            fn = getattr(type(odoo_env[model]), method, None)
            if fn is None:
                problems.append(where + " does not exist")
                continue
            params = list(inspect.signature(fn).parameters.values())[1:]
            collected = set(re.findall(r"kwarg:\s*'(\w+)'", cfg))
            for param in params:
                if param.default is inspect.Parameter.empty and param.name not in collected:
                    problems.append("%s requires %s" % (where, param.name))
            unknown = collected - {p.name for p in params}
            if unknown and not any(p.kind == p.VAR_KEYWORD for p in params):
                problems.append("%s collects unknown %s" % (where, sorted(unknown)))
    assert not problems, problems


@pytest.mark.parametrize(
    "model,method,needs",
    [
        ("fix.wms.putaway", "action_complete", {"bin_code", "item_code"}),
        ("fix.wms.wave", "action_pick_all", {"reason"}),
        ("fix.wms.wave", "action_cancel", {"reason"}),
        ("fix.wms.stage", "action_load", {"carton_scans"}),
        ("fix.stock.transfer", "action_resolve_discrepancy", {"resolution", "note"}),
        ("fix.stock.van.recon", "action_resolve", {"note"}),
    ],
)
def test_a7_methods_that_refuse_without_a_value_have_it_collected(model, method, needs):
    """These default to None and refuse inside, so the signature sweep cannot see them."""
    text = _fragment("m15.js") + _fragment("m41.js")
    found = []
    for body in _screens(text).values():
        if "model: '%s'" % model not in body or "kind: 'model_list'" not in body:
            continue
        match = re.search(r"\{\s*m:\s*'%s'(.*?)(?=\{\s*m:\s*'|\Z)" % method, body, re.S)
        if match:
            found.append(set(re.findall(r"kwarg:\s*'(\w+)'", match.group(1))))
    assert found and all(needs <= kwargs for kwargs in found), (model, method, found)


def test_a1_new_screens_are_in_the_nav_with_both_languages():
    text = _fragment("m41.js")
    for sid in ("M41-pick-lines", "M41-wh-zones"):
        assert re.search(r"\{ id: '%s', en: '[^']+', bn: '[^']+'" % sid, text), sid
