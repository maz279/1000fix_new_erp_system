# Shared fixtures for the A06 M15/M41 control tests (live ORM, rolled back).
#
# Setup runs as the superuser (odoo_env); every attack and every proper-path
# step runs as a NON-ADMIN user created in the transaction with exactly the
# role it needs: a plain employee (base.group_user), a Storekeeper, a
# Warehouse Operator or an Inventory Controller.
import itertools
import types
import uuid

import pytest

SK = "cd_wms_structure.group_storekeeper"
OP = "cd_wms_structure.group_warehouse_operator"
IC = "cd_wms_structure.group_inventory_controller"

_SEQ = itertools.count(1)


def make_service_order(env, branch, tag):
    brand = env["fix.brand"].create({"name": "A06 Inv Brand %s" % tag, "code": "AB%s" % tag})
    model = env["fix.device.model"].create({"name": "A06 Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "A06 Inv Customer %s" % tag})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "A06SN-%s" % tag}
    )
    return env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "A06 inventory test job",
        }
    )


class Inv(types.SimpleNamespace):
    """The test world: users, locations, parts and a few helpers."""

    def user(self, login, *groups):
        env = self.env
        ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        n = next(_SEQ)
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "%s %s" % (login, self.tag),
                    "login": "a06inv.%s.%s.%d@a06.test" % (login, self.tag.lower(), n),
                    "group_ids": [(6, 0, ids)],
                    "assigned_operating_unit_ids": [(6, 0, self.ou.ids)],
                    "default_operating_unit_id": self.ou.id,
                }
            )
        )

    def stock(self, part, location, qty, cost, cls="owned", status="unrestricted"):
        return self.env["fix.stock.onhand"]._apply(part, location, cls, qty, cost, status=status)

    def bucket(self, part, location, cls="owned", status="unrestricted"):
        self.env.invalidate_all()
        return self.env["fix.stock.onhand"]._bucket(part, location, cls, status)

    def qty(self, part, location, cls="owned", status="unrestricted"):
        row = self.bucket(part, location, cls, status)
        return row.qty if row else 0.0

    def events(self, event_type, aggregate=None, aggregate_id=None):
        domain = [("event_type", "=", event_type)]
        if aggregate:
            domain.append(("aggregate", "=", aggregate))
        if aggregate_id:
            domain.append(("aggregate_id", "=", aggregate_id))
        return self.env["fix.event.outbox"].sudo().search_count(domain)

    def suspense(self, source_ref=None, entry_type=None):
        domain = []
        if source_ref:
            domain.append(("source_ref", "=", source_ref))
        if entry_type:
            domain.append(("entry_type", "=", entry_type))
        return self.env["fix.inventory.valuation.suspense"].sudo().search(domain)

    def job(self):
        """A real service order (M15-10: an issue names a real job)."""
        if getattr(self, "_job", None):
            return self._job
        self._job = make_service_order(self.env, self.branch(), self.tag)
        return self._job

    def issue(self, user, part=None, location=None, qty=1.0, tech=None, serial=False, **kw):
        vals = {
            "service_order_ref": self.job().name,
            "product_id": (part or self.part).id,
            "location_id": (location or self.central).id,
            "technician_id": (tech or self.tech1).id,
            "quantity": qty,
            "scanned_code": (part or self.part).part_number,
            "operating_unit_id": self.ou.id,
        }
        if serial:
            vals["serial_number"] = serial
        vals.update(kw)
        return self.env["fix.stock.consumption"].with_user(user).create(vals)

    def receipt(
        self, user, part=None, location=None, rec=5.0, acc=5.0, cost=500.0, serial=False, **kw
    ):
        line = {
            "part_id": (part or self.part).id,
            "qty_received": rec,
            "qty_accepted": acc,
            "unit_cost": cost,
        }
        if serial:
            line["line_no"] = serial
        vals = {
            "partner_id": self.supplier.id,
            "location_id": (location or self.hub).id,
            "operating_unit_id": self.ou.id,
            "line_ids": [(0, 0, line)],
        }
        vals.update(kw)
        return self.env["fix.stock.receipt"].with_user(user).create(vals)

    def count(self, user, counted, part=None, location=None, **line_kw):
        line = {"part_id": (part or self.part).id, "counted_qty": counted}
        line.update(line_kw)
        return (
            self.env["fix.stock.count"]
            .with_user(user)
            .create(
                {
                    "location_id": (location or self.central).id,
                    "operating_unit_id": self.ou.id,
                    "line_ids": [(0, 0, line)],
                }
            )
        )

    def transfer(self, user, qty=5.0, frm=None, to=None, part=None):
        return (
            self.env["fix.stock.transfer"]
            .with_user(user)
            .create(
                {
                    "from_location_id": (frm or self.central).id,
                    "to_location_id": (to or self.hub).id,
                    "operating_unit_id": self.ou.id,
                    "line_ids": [(0, 0, {"part_id": (part or self.part).id, "qty": qty})],
                }
            )
        )

    def rtv(self, user, qty=2.0, **kw):
        vals = {
            "partner_id": self.supplier.id,
            "part_id": self.part.id,
            "location_id": self.central.id,
            "qty": qty,
        }
        vals.update(kw)
        return self.env["fix.stock.rtv"].with_user(user).create(vals)

    def quarantine(self, user, qty=1.0, part=None, location=None, **kw):
        vals = {
            "part_id": (part or self.part).id,
            "location_id": (location or self.central).id,
            "qty": qty,
        }
        vals.update(kw)
        return self.env["fix.stock.quarantine"].with_user(user).create(vals)

    def putaway(self, user, qty, bin_rec=None, part=None, line=None, **kw):
        vals = {
            "part_id": (part or self.wpart).id,
            "qty": qty,
            "to_bin_id": (bin_rec or self.bin).id,
            "receipt_line_id": (line if line is not None else self.grn_line).id or False,
        }
        vals.update(kw)
        return self.env["fix.wms.putaway"].with_user(user).create(vals)

    def wave(self, qty=4, bin_rec=None, part=None, user=None):
        return (
            self.env["fix.wms.wave"]
            .with_user(user or self.operator)
            .create(
                {
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "part_id": (part or self.wpart).id,
                                "bin_id": (bin_rec or self.bin).id,
                                "qty": qty,
                            },
                        )
                    ]
                }
            )
        )

    def cfo(self, *extra_groups):
        """A DOFA Tier 4 holder (the CFO band of BRU-INV-11/24)."""
        return self.user("cfo", "cd_entity_config.group_dofa_tier_4", *extra_groups)

    def approve_in_inbox(self, record, approver):
        task = record.approval_request_id.task_ids.filtered(
            lambda t: t.state == "pending" and t.assigned_user_id == approver
        )
        assert task, "%s has no inbox task for %s (routed to %s)" % (
            approver.name,
            record.display_name,
            record.approval_request_id.task_ids.mapped("assigned_user_id.name"),
        )
        task.with_user(approver).action_approve(comment="approved")
        return task

    def branch(self):
        if getattr(self, "_branch", None):
            return self._branch
        env = self.env
        company = env["res.company"].create({"name": "A06 Inv Co %s" % self.tag})
        entity = env["fix.entity"].create(
            {"code": "E%s" % self.tag, "legal_name": "A06 Inv Ltd", "company_id": company.id}
        )
        self._branch = env["fix.branch"].create(
            {
                "code": "B%s" % self.tag,
                "name": "A06 Inv Branch",
                "entity_id": entity.id,
                "operating_unit_id": self.ou.id,
            }
        )
        return self._branch

    def p03(self, user):
        """The P03 workspace endpoints, called as `user`."""
        import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
        import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

        ctl = g.P03GenericApiController()
        mw = getattr(g.P03GenericApiController.model_write, "original_endpoint", None)
        ma = getattr(g.P03GenericApiController.model_action, "original_endpoint", None)
        mw = mw or g.P03GenericApiController.model_write
        ma = ma or g.P03GenericApiController.model_action
        env = self.env(user=user.id)
        request = types.SimpleNamespace(env=env)

        def call(fn, **kw):
            old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)
            g.request = request
            s.request = request
            try:
                return fn(ctl, **kw)
            finally:
                g.request, s.request = old_g, old_s

        return types.SimpleNamespace(
            write=lambda **kw: call(mw, **kw), action=lambda **kw: call(ma, **kw)
        )


@pytest.fixture
def inv(odoo_env):
    env = odoo_env
    tag = uuid.uuid4().hex[:6].upper()
    x = Inv(env=env, tag=tag)
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.clerk = x.user("clerk")  # a plain employee: no inventory role
    x.keeper = x.user("keeper", SK)
    x.keeper2 = x.user("keeper2", SK)
    x.operator = x.user("operator", OP)
    x.operator2 = x.user("operator2", OP)
    x.controller = x.user("controller", IC)
    x.controller2 = x.user("controller2", IC)
    x.techuser = x.user("tech", SK)
    Emp = env["hr.employee"]
    x.tech1 = Emp.create({"name": "A06 Tech One %s" % tag, "user_id": x.techuser.id})
    x.tech2 = Emp.create({"name": "A06 Tech Two %s" % tag})
    x.op_emp = Emp.create({"name": "A06 Operator %s" % tag, "user_id": x.operator.id})
    Loc = env["fix.stock.location"]
    x.central = Loc.create(
        {
            "name": "A06 Central",
            "code": "A6C-" + tag,
            "location_type": "central",
            "operating_unit_id": x.ou.id,
        }
    )
    x.hub = Loc.create(
        {
            "name": "A06 Hub",
            "code": "A6H-" + tag,
            "location_type": "branch",
            "operating_unit_id": x.ou.id,
        }
    )
    x.van = Loc.create(
        {
            "name": "A06 Van",
            "code": "A6V-" + tag,
            "location_type": "van",
            "technician_id": x.tech1.id,
            "operating_unit_id": x.ou.id,
        }
    )
    Part = env["fix.spare.part"]
    x.part = Part.create({"name": "A06 Display", "part_number": "A6P-" + tag, "unit_cost": 500.0})
    x.spart = Part.create(
        {
            "name": "A06 Board (serial)",
            "part_number": "A6S-" + tag,
            "unit_cost": 8000.0,
            "is_serialized": True,
        }
    )
    x.stock(x.part, x.central, 10.0, 500.0)
    x.stock(x.spart, x.central, 2.0, 8000.0)
    Lot = env["fix.stock.lot"]
    x.lot1 = Lot.create(
        {
            "name": "A6SN1-" + tag,
            "part_id": x.spart.id,
            "location_id": x.central.id,
            "qty": 1.0,
            "received_on": "2026-10-01",
        }
    )
    x.lot2 = Lot.create(
        {
            "name": "A6SN2-" + tag,
            "part_id": x.spart.id,
            "location_id": x.central.id,
            "qty": 1.0,
            "received_on": "2026-10-01",
        }
    )
    x.supplier = env["res.partner"].create({"name": "A06 Supplier " + tag})
    return x
