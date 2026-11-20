# A06 ERP audit (20 Nov 2026) - real-time inventory accounting, owner
# decisions D1 (perpetual posting), D2 (account map) and D4 (stock take-on,
# zero-cost stock). Findings X01-X07, X17, X19, X36, A02, A03/P05, A32.
#
# Every test runs in a private company with the legacy-chart accounts of D2
# (created here: the shared test database has the generic chart), two
# operating units and NON-ADMIN users: a Storekeeper moves stock, an Inventory
# Controller approves, an Accounting Administrator takes the stock on.
import itertools
import json
import uuid

import pytest
from odoo import fields
from odoo.addons.cd_inventory.models.fix_valuation_suspense import dhaka_today
from odoo.exceptions import AccessError, UserError, ValidationError

from .conftest import IC, SK

REFUSED = (UserError, AccessError, ValidationError)
COST = "cd_wms_structure.group_stock_cost_viewer"
FINANCE = "account.group_account_manager"
_SEQ = itertools.count(1)

D2 = {
    "100502": "asset_current",
    "100503": "asset_current",
    "100506": "asset_current",
    "100508": "asset_current",
    "100509": "asset_current",
    "100510": "asset_current",
    "100511": "asset_current",
    "600002": "expense_direct_cost",
    "500905": "expense",
    "600007": "expense_direct_cost",
    "300101": "equity",
    "GRD100": "asset_current",
    "GRD200": "liability_current",
    "110999": "asset_current",
    "110100": "asset_current",
}


def refused(env, fn, match=None):
    with pytest.raises(REFUSED, match=match), env.cr.savepoint():
        fn()
        env.flush_all()


class World:
    def __init__(self, env):
        self.root = env
        self.tag = uuid.uuid4().hex[:6].upper()
        tag = self.tag
        self.company = env["res.company"].create({"name": "A06 Ledger Co %s" % tag})
        self.env = env(context=dict(env.context, allowed_company_ids=[self.company.id]))
        cenv = self.env
        OU = cenv["operating.unit"]
        self.ou1 = OU.create(
            {
                "name": "LED North %s" % tag,
                "code": "N%s" % tag[:5],
                "partner_id": self.company.partner_id.id,
                "company_id": self.company.id,
            }
        )
        self.ou2 = OU.create(
            {
                "name": "LED South %s" % tag,
                "code": "S%s" % tag[:5],
                "partner_id": self.company.partner_id.id,
                "company_id": self.company.id,
            }
        )
        Account = cenv["account.account"].with_company(self.company)
        self.acc = {
            code: Account.create(
                {
                    "code": code,
                    "name": "LED %s" % code,
                    "account_type": kind,
                    "company_ids": [(6, 0, self.company.ids)],
                }
            )
            for code, kind in D2.items()
        }
        self.journal = cenv["account.journal"].create(
            {"name": "Stock", "code": "STJ", "type": "general", "company_id": self.company.id}
        )
        entity = cenv["fix.entity"].create(
            {"code": "L%s" % tag, "legal_name": "A06 Ledger Ltd", "company_id": self.company.id}
        )
        self.branch1 = cenv["fix.branch"].create(
            {
                "code": "LB1%s" % tag,
                "name": "North",
                "entity_id": entity.id,
                "operating_unit_id": self.ou1.id,
            }
        )
        self.branch2 = cenv["fix.branch"].create(
            {
                "code": "LB2%s" % tag,
                "name": "South",
                "entity_id": entity.id,
                "operating_unit_id": self.ou2.id,
            }
        )
        self.keeper = self.user("keeper", SK, COST)
        self.keeper2 = self.user("keeper2", SK, COST)
        self.controller = self.user("controller", IC, COST)
        self.controller2 = self.user("controller2", IC, COST)
        self.finance = self.user("finance", FINANCE, COST)
        self.clerk = self.user("clerk")
        Loc = cenv["fix.stock.location"]
        self.north = Loc.create(
            {
                "name": "North Central",
                "code": "LN-%s" % tag,
                "location_type": "central",
                "operating_unit_id": self.ou1.id,
                "company_id": self.company.id,
                "branch_id": self.branch1.id,
            }
        )
        self.south = Loc.create(
            {
                "name": "South Branch",
                "code": "LS-%s" % tag,
                "location_type": "branch",
                "operating_unit_id": self.ou2.id,
                "company_id": self.company.id,
                "branch_id": self.branch2.id,
            }
        )
        # X36: no OU on the location, but its branch has one
        self.south_store = Loc.create(
            {
                "name": "South Store",
                "code": "LS2-%s" % tag,
                "location_type": "branch",
                "company_id": self.company.id,
                "branch_id": self.branch2.id,
            }
        )
        self.nowhere = Loc.create(
            {
                "name": "Nowhere",
                "code": "LX-%s" % tag,
                "location_type": "branch",
                "company_id": self.company.id,
            }
        )
        Part = cenv["fix.spare.part"]
        brand = cenv["fix.brand"].search([("name", "=ilike", "samsung")], limit=1)
        brand = brand or cenv["fix.brand"].create({"name": "Samsung", "code": "SAMS"})
        self.part = Part.create(
            {
                "name": "LED Display",
                "part_number": "LDP-%s" % tag,
                "unit_cost": 500.0,
                "company_id": self.company.id,
            }
        )
        self.samsung = Part.create(
            {
                "name": "LED Samsung board",
                "part_number": "LSM-%s" % tag,
                "unit_cost": 1000.0,
                "brand_id": brand.id,
                "company_id": self.company.id,
            }
        )
        self.xiaomi = Part.create(
            {
                "name": "LED Xiaomi flex",
                "part_number": "LXI-%s" % tag,
                "unit_cost": 100.0,
                "device_brand": "XIAOMI",
                "company_id": self.company.id,
            }
        )
        self.free = Part.create(
            {"name": "LED uncosted", "part_number": "LZC-%s" % tag, "company_id": self.company.id}
        )
        self.supplier = cenv["res.partner"].create({"name": "LED Supplier %s" % tag})
        emp = cenv["hr.employee"].create(
            {"name": "LED Tech %s" % tag, "user_id": self.keeper.id, "company_id": self.company.id}
        )
        self.tech = emp
        # opening stock, before the take-on (no valuation rows yet)
        self.stock(self.part, self.north, 10.0, 500.0)
        self.stock(self.samsung, self.north, 4.0, 1000.0)
        self.stock(self.xiaomi, self.south, 20.0, 100.0)
        self.stock(self.free, self.north, 6.0, 0.0)
        self.stock(self.part, self.south_store, 2.0, 500.0)

    # ------------------------------------------------------------- helpers
    def user(self, login, *groups):
        env = self.root
        ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        n = next(_SEQ)
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "%s %s" % (login, self.tag),
                    "login": "a06led.%s.%s.%d@a06.test" % (login, self.tag.lower(), n),
                    "group_ids": [(6, 0, ids)],
                    "company_id": self.company.id,
                    "company_ids": [(6, 0, self.company.ids)],
                    "assigned_operating_unit_ids": [(6, 0, (self.ou1 | self.ou2).ids)],
                    "default_operating_unit_id": self.ou1.id,
                }
            )
        )

    def as_(self, user, model):
        return self.env[model].with_user(user)

    def stock(self, part, location, qty, cost):
        return self.env["fix.stock.onhand"]._apply(part, location, "owned", qty, cost)

    def bucket(self, part, location):
        self.env.invalidate_all()
        return self.env["fix.stock.onhand"]._bucket(part, location, "owned")

    def rows(self, ref=None, kind=None):
        domain = [("company_id", "=", self.company.id)]
        if ref:
            domain.append(("source_ref", "=", ref))
        if kind:
            domain.append(("entry_type", "=", kind))
        return self.env["fix.inventory.valuation.suspense"].sudo().search(domain)

    def lines(self, move):
        """{(account code, OU code): signed balance} of a posted move."""
        out = {}
        dims = (
            self.env["fix.journal.dimension"]
            .sudo()
            .search([("move_line_id", "in", move.line_ids.ids)])
        )
        ou_of = {d.move_line_id.id: d.operating_unit_id for d in dims}
        for line in move.line_ids:
            key = (line.account_id.code, ou_of.get(line.id).code if ou_of.get(line.id) else None)
            out[key] = round(out.get(key, 0.0) + line.balance, 2)
        return out

    def takeon(self, **kw):
        return self.as_(self.finance, "fix.inventory.valuation.suspense").action_stock_takeon(
            self.company.id, **kw
        )

    def job(self):
        if getattr(self, "_job", None):
            return self._job
        cenv = self.env
        model = cenv["fix.device.model"].create(
            {"name": "LED Phone", "brand_id": cenv["fix.brand"].search([], limit=1).id}
        )
        customer = cenv["res.partner"].create({"name": "LED Customer %s" % self.tag})
        self.device = cenv["fix.device"].create(
            {
                "device_model_id": model.id,
                "owner_id": customer.id,
                "serial_number": "LEDSN-%s" % self.tag,
                "company_id": self.company.id,
            }
        )
        self._job = cenv["fix.service.order"].create(
            {
                "device_id": self.device.id,
                "customer_id": customer.id,
                "branch_id": self.branch1.id,
                "fault_description": "A06 ledger job",
                "company_id": self.company.id,
            }
        )
        return self._job

    def issue(self, part=None, location=None, qty=1.0, user=None):
        user = user or self.keeper
        rec = self.as_(user, "fix.stock.consumption").create(
            {
                "service_order_ref": self.job().name,
                "product_id": (part or self.part).id,
                "location_id": (location or self.north).id,
                "technician_id": self.tech.id,
                "quantity": qty,
                "scanned_code": (part or self.part).part_number,
                "operating_unit_id": self.ou1.id,
                "company_id": self.company.id,
            }
        )
        rec.action_scan_and_consume()
        return rec

    def receipt(self, part=None, location=None, qty=5.0, cost=520.0, **kw):
        vals = {
            "partner_id": self.supplier.id,
            "location_id": (location or self.north).id,
            "operating_unit_id": self.ou1.id,
            "company_id": self.company.id,
            "direct_reason": "A06 ledger delivery",
            "line_ids": [
                (
                    0,
                    0,
                    {"part_id": (part or self.part).id, "qty_received": qty, "qty_accepted": qty},
                )
            ],
        }
        vals.update(kw)
        rec = self.as_(self.keeper, "fix.stock.receipt").create(vals)
        rec.line_ids.sudo().write({"unit_cost": cost})
        rec.action_inspect()
        rec.with_user(self.controller).action_post()
        return rec


@pytest.fixture
def w(odoo_env):
    return World(odoo_env)


@pytest.fixture
def live(w):
    """The world after its stock take-on: real-time posting on."""
    w.summary = w.takeon()
    return w


# ===================================================================== D4 take-on
def test_x02_takeon_posts_onhand_by_brand_and_ou_and_lists_zero_cost(w):
    # only a Finance manager takes the stock on, once
    refused(
        w.env,
        lambda: w.as_(w.controller, "fix.inventory.valuation.suspense").action_stock_takeon(
            w.company.id
        ),
        "Accounting Administrator",
    )
    assert not w.company.fix_stock_realtime_from
    summary = w.takeon()
    assert w.company.fix_stock_realtime_from
    assert summary["total_value"] == 5000.0 + 4000.0 + 2000.0 + 1000.0
    # one entry per OU: Dr stock by brand / Cr 300101
    moves = w.env["account.move"].search(
        [("ref", "like", "Stock take-on"), ("company_id", "=", w.company.id)]
    )
    assert len(moves) == 2 and set(moves.mapped("state")) == {"posted"}
    balances = {}
    for move in moves:
        for key, value in w.lines(move).items():
            balances[key] = round(balances.get(key, 0.0) + value, 2)
    assert balances == {
        ("100502", w.ou1.code): 5000.0,
        ("100506", w.ou1.code): 4000.0,
        ("300101", w.ou1.code): -9000.0,
        # the south store has no OU of its own: its branch's (X36)
        ("100508", w.ou2.code): 2000.0,
        ("100502", w.ou2.code): 1000.0,
        ("300101", w.ou2.code): -3000.0,
    }
    assert set(moves.mapped("date")) == {dhaka_today()}
    rows = w.rows(kind="initial_count")
    assert len(rows) == 4 and set(rows.mapped("status")) == {"posted"}
    assert set(rows.mapped("move_id")) <= set(moves)
    # the zero-cost line goes to Finance, valued at nothing
    assert summary["zero_cost_count"] == 1
    (zero,) = summary["zero_cost_lines"]
    assert (zero["part_number"], zero["location"], zero["qty"]) == (
        w.free.part_number,
        w.north.code,
        6.0,
    )
    # idempotent: a second run is refused and posts nothing
    refused(w.env, w.takeon, "runs once")
    assert (
        w.env["account.move"].search_count(
            [("ref", "like", "Stock take-on"), ("company_id", "=", w.company.id)]
        )
        == 2
    )
    tie = w.as_(w.finance, "fix.inventory.valuation.suspense").get_stock_gl_tieout(w.company.id)
    assert tie["ties_out"], tie


def test_x02_takeon_refuses_a_location_with_no_ou_and_pending_rows(w):
    w.stock(w.part, w.nowhere, 1.0, 500.0)
    refused(w.env, w.takeon, w.nowhere.code)
    assert not w.company.fix_stock_realtime_from
    w.bucket(w.part, w.nowhere).sudo()._guarded().write({"qty": 0.0})
    # a row still pending the old cut-over is inside today's on-hand value
    w.env["fix.inventory.valuation.suspense"]._fix_post(
        "receipt", w.part, 1.0, 500.0, "LEGACY-1", location=w.north
    )
    pending = w.rows(ref="LEGACY-1")
    assert pending.status == "pending_gl_cutover"
    refused(w.env, w.takeon, "supersede_pending")
    w.takeon(supersede_pending=True)
    assert pending.status == "archived" and "superseded" in pending.archive_ref


# ===================================================== X01 / X03: posting rules
def test_x03_receipt_posts_stock_against_grni_at_the_location_ou(live):
    w = live
    rec = w.receipt(qty=5.0, cost=520.0)
    (row,) = w.rows(ref=rec.name, kind="receipt")
    assert row.status == "posted" and row.move_id.state == "posted"
    assert w.lines(row.move_id) == {("100502", w.ou1.code): 2600.0, ("100503", w.ou1.code): -2600.0}
    assert row.move_id.date == dhaka_today() == row.posting_date
    assert row.move_id.journal_id == w.journal
    assert (row.stock_account_code, row.counter_account_code) == ("100502", "100503")
    assert (
        w.env["fix.journal.posting.log"]
        .sudo()
        .search_count([("move_id", "=", row.move_id.id), ("source", "=", "inventory_subledger")])
        == 1
    )


def test_x01_brand_decides_the_stock_account(live):
    w = live
    rec = w.receipt(part=w.samsung, qty=1.0, cost=1000.0)
    move = w.rows(ref=rec.name).move_id
    assert w.lines(move)[("100506", w.ou1.code)] == 1000.0
    rec = w.receipt(
        part=w.xiaomi, location=w.south, qty=2.0, cost=100.0, operating_unit_id=w.ou2.id
    )
    move = w.rows(ref=rec.name).move_id
    assert w.lines(move) == {("100508", w.ou2.code): 200.0, ("100503", w.ou2.code): -200.0}
    # the map is a parameter: Samsung re-pointed to 100509
    w.env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.stock_posting.brand_accounts", json.dumps({"samsung": "100509"})
    )
    rec = w.receipt(part=w.samsung, qty=1.0, cost=1000.0)
    assert ("100509", w.ou1.code) in w.lines(w.rows(ref=rec.name).move_id)


def test_x01_job_issue_posts_parts_cost_and_return_reverses(live):
    w = live
    issue = w.issue(qty=2.0)
    (row,) = w.rows(ref=issue.name, kind="consumption")
    assert w.lines(row.move_id) == {("600002", w.ou1.code): 1000.0, ("100502", w.ou1.code): -1000.0}
    issue.action_return_part("excess_draw")
    back = w.rows(ref=issue.name, kind="return")
    assert w.lines(back.move_id) == {
        ("100502", w.ou1.code): 1000.0,
        ("600002", w.ou1.code): -1000.0,
    }


def test_x01_count_loss_posts_500905_after_approval(live):
    w = live
    count = w.as_(w.keeper, "fix.stock.count").create(
        {
            "location_id": w.north.id,
            "operating_unit_id": w.ou1.id,
            "company_id": w.company.id,
            "line_ids": [(0, 0, {"part_id": w.part.id, "counted_qty": 9.0})],
        }
    )
    count.action_submit()
    count.line_ids.write({"recount_qty": 9.0})
    count.write({"reason_code": "loss"})
    count.action_submit()
    count.with_user(w.controller).action_approve()
    (row,) = w.rows(ref=count.name, kind="adjustment")
    assert w.lines(row.move_id) == {("500905", w.ou1.code): 500.0, ("100502", w.ou1.code): -500.0}


def test_x01_rtv_debits_grni_and_ppv_clears_it(live):
    w = live
    rtv = w.as_(w.keeper, "fix.stock.rtv").create(
        {
            "partner_id": w.supplier.id,
            "part_id": w.part.id,
            "location_id": w.north.id,
            "qty": 2.0,
            "company_id": w.company.id,
            "no_receipt_reason": "A06 ledger stock (no goods receipt)",
            "rtv_ref": "RMA-LED-%s" % w.tag,
        }
    )
    rtv.action_submit()
    if rtv.state != "approved":
        rtv.with_user(w.controller).action_approve()
    rtv.action_ship()
    (row,) = w.rows(ref=rtv.name, kind="rtv")
    assert w.lines(row.move_id) == {("100503", w.ou1.code): 1000.0, ("100502", w.ou1.code): -1000.0}
    # the vendor credits 480 a piece: the 40 variance clears GRNI to 600007
    variance = w.env["fix.inventory.valuation.suspense"]._fix_post_price_variance(
        w.part, 2.0, 40.0, rtv.name, "600007", location=w.north, company=w.company
    )
    assert w.lines(variance.move_id) == {
        ("600007", w.ou1.code): 40.0,
        ("100503", w.ou1.code): -40.0,
    }


def test_x01_transfer_moves_value_between_ous_at_receipt(live):
    w = live
    trf = w.as_(w.keeper, "fix.stock.transfer").create(
        {
            "from_location_id": w.north.id,
            "to_location_id": w.south.id,
            "operating_unit_id": w.ou1.id,
            "company_id": w.company.id,
            "line_ids": [(0, 0, {"part_id": w.part.id, "qty": 3.0})],
        }
    )
    trf.action_submit()
    trf.with_user(w.controller).action_approve()
    trf.action_dispatch()
    # in transit the value stays the sender's: nothing posted yet
    assert not w.rows(ref=trf.name)
    trf.with_user(w.keeper2).action_receive()
    rows = w.rows(ref=trf.name, kind="transfer")
    assert len(rows) == 2 and len(rows.move_id) == 1
    assert w.lines(rows.move_id) == {
        ("100502", w.ou2.code): 1500.0,
        ("100502", w.ou1.code): -1500.0,
    }
    assert sorted(rows.mapped(lambda r: (r.operating_unit_id.code, r.total_valuation))) == sorted(
        [(w.ou1.code, -1500.0), (w.ou2.code, 1500.0)]
    )
    tie = w.env["fix.inventory.valuation.suspense"].get_stock_gl_tieout(w.company.id)
    assert tie["ties_out"], tie["rows"]


def test_d1_same_ou_transfer_posts_nothing(live):
    w = live
    hub = w.env["fix.stock.location"].create(
        {
            "name": "North hub",
            "code": "LNH-%s" % w.tag,
            "location_type": "branch",
            "operating_unit_id": w.ou1.id,
            "company_id": w.company.id,
        }
    )
    trf = w.as_(w.keeper, "fix.stock.transfer").create(
        {
            "from_location_id": w.north.id,
            "to_location_id": hub.id,
            "operating_unit_id": w.ou1.id,
            "company_id": w.company.id,
            "line_ids": [(0, 0, {"part_id": w.part.id, "qty": 1.0})],
        }
    )
    trf.action_submit()
    trf.with_user(w.controller).action_approve()
    trf.action_dispatch()
    trf.with_user(w.keeper2).action_receive()
    assert trf.state == "received" and not w.rows(ref=trf.name)


def test_x01_revaluation_needs_its_counter_and_an_external_move_is_not_doubled(live):
    w = live
    Onhand = w.env["fix.stock.onhand"]
    refused(
        w.env,
        lambda: Onhand._fix_revalue(w.part, w.north, "owned", 100.0, "REV-1"),
        "fix_stock_counter_account",
    )
    Onhand.with_context(fix_stock_counter_account="300101")._fix_revalue(
        w.part, w.north, "owned", 100.0, "REV-2"
    )
    assert w.lines(w.rows(ref="REV-2").move_id) == {
        ("100502", w.ou1.code): 100.0,
        ("300101", w.ou1.code): -100.0,
    }
    # a caller that posted the event itself names its entry: linked, not posted again
    own = w.env["fix.inventory.valuation.suspense"]._fix_gl_post(
        w.company,
        dhaka_today(),
        "Caller's own entry",
        [
            (w.acc["100502"], "x", 50.0, {"operating_unit_id": w.ou1.id}),
            (w.acc["300101"], "x", -50.0, {"operating_unit_id": w.ou1.id}),
        ],
    )
    before = w.env["account.move"].search_count([("company_id", "=", w.company.id)])
    Onhand.with_context(fix_stock_external_move_id=own.id)._fix_revalue(
        w.part, w.north, "owned", 50.0, "REV-3"
    )
    row = w.rows(ref="REV-3")
    assert row.status == "posted" and row.move_id == own
    assert w.env["account.move"].search_count([("company_id", "=", w.company.id)]) == before


def test_x01_shipment_without_document_is_refused(live):
    w = live
    refused(
        w.env,
        lambda: w.env["fix.inventory.valuation.suspense"]._fix_post(
            "shipment", w.part, -1.0, 500.0, "WAVE-X", location=w.north
        ),
        "no posting rule",
    )


def test_x01_account_not_in_chart_refuses_the_movement(live):
    w = live
    w.env["ir.config_parameter"].sudo().set_param("cd_inventory.account_code.cogs", "999999")
    before = w.bucket(w.part, w.north).qty
    refused(w.env, lambda: w.issue(qty=1.0), "999999")
    assert w.bucket(w.part, w.north).qty == before


def test_x36_location_without_any_ou_fails_closed(live):
    w = live
    w.stock(w.part, w.nowhere, 2.0, 500.0)
    refused(w.env, lambda: w.issue(location=w.nowhere, qty=1.0), "no operating unit")


# ============================================================ X19 zero cost
def test_x19_zero_cost_issue_needs_an_approved_release(live):
    w = live
    w.job()  # outside the refused savepoints below
    refused(w.env, lambda: w.issue(part=w.free, qty=2.0), "carries no cost")
    assert w.bucket(w.free, w.north).qty == 6.0
    release = w.as_(w.keeper, "fix.stock.uncosted.release").create(
        {
            "part_id": w.free.id,
            "location_id": w.north.id,
            "qty": 2.0,
            "reason": "urgent job before pricing",
            "company_id": w.company.id,
        }
    )
    release.action_submit()
    # the requester cannot approve it; a plain user neither
    refused(w.env, lambda: release.with_user(w.keeper).action_approve())
    release.with_user(w.controller).action_approve()
    w.issue(part=w.free, qty=2.0)
    assert release.state == "used" and release.qty_used == 2.0
    refused(w.env, lambda: w.issue(part=w.free, qty=1.0), "carries no cost")


def test_x19_zero_cost_count_variance_goes_to_approval(live):
    w = live
    count = w.as_(w.keeper, "fix.stock.count").create(
        {
            "location_id": w.north.id,
            "operating_unit_id": w.ou1.id,
            "company_id": w.company.id,
            "line_ids": [(0, 0, {"part_id": w.free.id, "counted_qty": 5.0})],
        }
    )
    # a 2% tolerance would have posted a 1-in-6 loss of uncosted stock directly
    w.env["ir.config_parameter"].sudo().set_param("cd_inventory.count_variance_tolerance_pct", "50")
    count.action_submit()
    assert count.state == "recount"
    count.line_ids.write({"recount_qty": 5.0})
    count.write({"reason_code": "loss"})
    count.action_submit()
    assert count.state == "to_approve"
    count.with_user(w.controller).action_approve()
    row = w.rows(ref=count.name, kind="adjustment")
    assert row.status == "posted" and not row.move_id


def test_x19_unapproved_zero_cost_adjustment_is_refused_by_the_ledger(live):
    w = live
    refused(
        w.env,
        lambda: w.env["fix.inventory.valuation.suspense"]._fix_post(
            "adjustment", w.free, -1.0, 0.0, "NO-SUCH-COUNT", location=w.north
        ),
        "carries no cost",
    )


def test_d4_finance_prices_uncosted_stock_against_takeon(live):
    w = live
    bucket = w.bucket(w.free, w.north)
    Suspense = w.env["fix.inventory.valuation.suspense"]
    refused(
        w.env,
        lambda: Suspense.with_user(w.controller).action_price_uncosted_stock(
            [{"onhand_id": bucket.id, "unit_cost": 30.0}], "FIN-PRICE-1"
        ),
    )
    Suspense.with_user(w.finance).action_price_uncosted_stock(
        [{"onhand_id": bucket.id, "unit_cost": 30.0}], "FIN-PRICE-1"
    )
    assert w.bucket(w.free, w.north).unit_cost == 30.0
    row = w.rows(kind="revaluation").filtered(lambda r: r.product_id == w.free)
    assert w.lines(row.move_id) == {("100502", w.ou1.code): 180.0, ("300101", w.ou1.code): -180.0}
    w.issue(part=w.free, qty=1.0)  # priced: no release needed any more


# ================================================================== tie-out
def test_tieout_after_the_estate_moves(live):
    w = live
    w.receipt(qty=2.0, cost=500.0)
    w.issue(qty=1.0)
    tie = w.as_(w.finance, "fix.inventory.valuation.suspense").get_stock_gl_tieout(
        w.company.id, fields.Date.to_string(dhaka_today())
    )
    assert tie["ties_out"], tie["rows"]
    by_key = {(r["account_code"], r["operating_unit_id"]): r for r in tie["rows"]}
    north = by_key[("100502", w.ou1.id)]
    assert north["gl_balance"] == north["subledger_value"] == north["onhand_value"] == 5500.0
    refused(
        w.env,
        lambda: w.as_(w.clerk, "fix.inventory.valuation.suspense").get_stock_gl_tieout(
            w.company.id
        ),
    )


def _tie(w):
    return w.as_(w.finance, "fix.inventory.valuation.suspense").get_stock_gl_tieout(
        w.company.id, fields.Date.to_string(dhaka_today())
    )


def test_tieout_absorbs_unit_cost_rounding_of_a_revaluation(live):
    """A06 integration: a revaluation of BDT 10 spread over 13 units leaves a
    unit cost of 4 decimals (10/13 a piece); qty x unit cost then differs from the posted value
    by a fraction of a paisa, which is rounding, not a break."""
    w = live
    w.receipt(qty=3.0, cost=500.0)
    Onhand = w.env["fix.stock.onhand"].sudo()
    Onhand.with_context(fix_stock_counter_account="300101")._fix_revalue(
        w.part, w.north, "owned", 10.0, "ROUNDING-%s" % w.tag
    )
    tie = _tie(w)
    north = {(r["account_code"], r["operating_unit_id"]): r for r in tie["rows"]}[
        ("100502", w.ou1.id)
    ]
    assert north["gl_minus_subledger"] == 0.0
    assert abs(north["subledger_minus_onhand"]) <= north["rounding_allowance"]
    assert tie["ties_out"], tie["rows"]


def test_tieout_catches_stock_value_changed_outside_the_ledger(live):
    """A unit cost rewritten without a valuation row is a break: the tie-out
    must say so (the allowance covers rounding only)."""
    w = live
    w.receipt(qty=2.0, cost=500.0)
    bucket = w.bucket(w.part, w.north)
    w.env.cr.execute(
        "UPDATE fix_stock_onhand SET unit_cost = unit_cost + 1 WHERE id = %s", [bucket.id]
    )
    bucket.invalidate_recordset(["unit_cost"])
    tie = _tie(w)
    assert not tie["ties_out"], tie["rows"]


# ============================================================ X17 graded stock
def _graded(w, **vals):
    w.job()
    grade = w.env["fix.refurb.grade"].search([], limit=1)
    base = {
        "device_id": w.device.id,
        "grade_id": grade.id,
        "company_id": w.company.id,
        "location_id": w.north.id,
        "acquisition_cost": 1000.0,
        "refurbishment_cost": 200.0,
        "resale_price": 2000.0,
    }
    base.update(vals)
    return w.env["fix.graded.stock"].sudo().create(base)


def test_x17_graded_unit_enters_and_leaves_the_ledger(live):
    w = live
    w.job()  # the device, outside the refused savepoint below
    icp = w.env["ir.config_parameter"].sudo()
    # the graded accounts are owner decisions: unset, the intake is refused
    refused(w.env, lambda: _graded(w), "graded")
    icp.set_param("cd_inventory.account_code.graded_stock", "GRD100")
    icp.set_param("cd_inventory.account_code.graded_intake", "GRD200")
    unit = _graded(w)
    entry = unit.ledger_entry_id
    assert entry.status == "posted"
    assert w.lines(entry.move_id) == {
        ("GRD100", w.ou1.code): 1200.0,
        ("GRD200", w.ou1.code): -1200.0,
    }
    unit.action_sell()
    sale = w.rows(kind="graded_issue")
    assert w.lines(sale.move_id) == {
        ("600002", w.ou1.code): 1200.0,
        ("GRD100", w.ou1.code): -1200.0,
    }
    # no person types the cost (A29)
    other = _graded(w)
    refused(
        w.env, lambda: other.with_user(w.controller).write({"acquisition_cost": 1.0}), "workflow"
    )


# ====================================================== X04-X07 period close
def _close(w, period_end):
    return w.env["fix.period.close"].create({"company_id": w.company.id, "period_end": period_end})


def _legacy(w, value, kind="receipt", when=None, ou=None):
    vals = {
        "company_id": w.company.id,
        "product_id": w.part.id,
        "quantity": 1.0,
        "unit_cost": value,
        "total_valuation": value,
        "entry_type": kind,
        "suspense_account_code": "110999",
    }
    if when:
        vals["posting_date"] = when
    if ou:
        vals["operating_unit_id"] = ou.id
    return w.env["fix.inventory.valuation.suspense"].create(vals)


def _cutover(w, legs, when):
    """legs: [(code, amount, ou)] signed (+ debit)."""
    move = w.env["account.move"].create(
        {
            "journal_id": w.journal.id,
            "date": when,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "c",
                        "account_id": w.acc[c].id,
                        "debit": max(a, 0.0),
                        "credit": max(-a, 0.0),
                    },
                )
                for c, a, _ou in legs
            ],
        }
    )
    move.action_post()
    for line, (_c, _a, ou) in zip(move.line_ids, legs, strict=True):
        if ou:
            w.env["fix.journal.dimension"].create(
                {"move_line_id": line.id, "company_id": w.company.id, "operating_unit_id": ou.id}
            )
    return move


def test_x04_close_measures_only_its_own_period_by_dhaka_date(w):
    import datetime as dt

    last = fields.Date.to_date("2026-09-30")
    close = _close(w, last)
    _legacy(w, 700.0, when=fields.Date.to_date("2026-10-01"))
    assert close._fix_suspense_pending() == (0, 0.0)
    close._fix_check_suspense_clear()  # next month's movement does not block September
    _legacy(w, 300.0, when=last)
    assert close._fix_suspense_pending() == (1, 300.0)
    refused(w.env, close._fix_check_suspense_clear, "still pending")
    # 23:30 UTC on 30 Sep is 1 Oct in Dhaka: the business date, not UTC
    assert dhaka_today(dt.datetime(2026, 9, 30, 18, 30)) == fields.Date.to_date("2026-10-01")


def test_x05_cutover_in_the_wrong_direction_is_refused(w):
    last = fields.Date.to_date("2026-09-30")
    _legacy(w, 1000.0, kind="receipt", when=last)
    close = _close(w, last)
    # stock IN must be credited off the suspense; a debit of the same size used to pass
    close.cutover_move_id = _cutover(w, [("110999", 1000.0, None), ("110100", -1000.0, None)], last)
    refused(w.env, close.action_reconcile_inventory_suspense, "does not clear")
    close.cutover_move_id = _cutover(w, [("110100", 1000.0, None), ("110999", -1000.0, None)], last)
    assert close.action_reconcile_inventory_suspense()["status"] == "zero_cleared"


def test_x06_suspense_figures_are_signed(w):
    last = fields.Date.to_date("2026-09-30")
    _legacy(w, 1000.0, kind="receipt", when=last)
    _legacy(w, 400.0, kind="consumption", when=last)
    close = _close(w, last)
    # 1,000 in and 400 issued is 600 of stock, not 1,400
    assert close._fix_suspense_pending() == (2, 600.0)
    data = (
        w.env["fix.inventory.valuation.suspense"]
        .with_company(w.company)
        .get_baseline_integrity([w.company.id])
    )
    assert data["companies"][0]["pending_total"] == 600.0


def test_x07_cutover_must_keep_the_operating_units(w):
    last = fields.Date.to_date("2026-09-30")
    _legacy(w, 1000.0, when=last, ou=w.ou1)
    _legacy(w, 500.0, when=last, ou=w.ou2)
    close = _close(w, last)
    close.cutover_move_id = _cutover(w, [("110100", 1500.0, None), ("110999", -1500.0, None)], last)
    refused(w.env, close.action_reconcile_inventory_suspense, "operating units")
    close.cutover_move_id = _cutover(
        w,
        [("110100", 1500.0, w.ou1), ("110999", -1000.0, w.ou1), ("110999", -500.0, w.ou2)],
        last,
    )
    assert close.action_reconcile_inventory_suspense()["status"] == "zero_cleared"


def test_d1_close_refuses_a_posted_row_without_its_entry(live):
    w = live
    rec = w.receipt(qty=1.0, cost=500.0)
    row = w.rows(ref=rec.name)
    end = fields.Date.end_of(dhaka_today(), "month")
    close = _close(w, end)
    close._fix_check_suspense_clear()
    row.sudo()._guarded().write({"move_id": False})
    refused(w.env, close._fix_check_suspense_clear, "no posted journal entry")
