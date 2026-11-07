# cd_demand_plan test fixtures: users in the M43 roles, an M15 part at two
# locations, M15 consumption / on-hand builders and the P03 endpoint harness.
# Everything is created inside the rolled-back `odoo_env` transaction.
from __future__ import annotations

import types
import uuid
from datetime import date, datetime

import pytest

PLANNER = "cd_demand_plan.group_fix_demand_planner"
APPROVER = "cd_demand_plan.group_fix_demand_approver"


def _month(first: date, delta: int) -> date:
    years, month0 = divmod(first.month - 1 + delta, 12)
    return date(first.year + years, month0 + 1, 1)


class M43:
    def __init__(self, env):
        self.env = env
        self.tag = uuid.uuid4().hex[:6].upper()
        self.company = env.company
        self.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
        self.this_month = date.today().replace(day=1)
        self.period = "%04d-%02d" % (self.this_month.year, self.this_month.month)
        last = _month(self.this_month, -1)
        self.last_period = "%04d-%02d" % (last.year, last.month)
        self.tech = env["hr.employee"].create({"name": "M43 Technician %s" % self.tag})
        self.clerk = self.user("clerk")
        self.planner = self.user("planner", [PLANNER])
        self.planner2 = self.user("planner2", [PLANNER])
        self.approver = self.user("approver", [APPROVER])
        self.approver2 = self.user("approver2", [APPROVER])
        self.tmpl = env["product.template"].create(
            {"name": "M43 Display assembly %s" % self.tag, "standard_price": 1000.0}
        )
        self.prod = self.tmpl.product_variant_id
        self.part = env["fix.spare.part"].create(
            {
                "name": "M43 Display assembly %s" % self.tag,
                "part_number": "M43-%s" % self.tag,
                "unit_cost": 1000.0,
            }
        )
        self.vendor = env["res.partner"].create(
            {"name": "M43 Supplier %s" % self.tag, "is_company": True}
        )
        self.supplier = env["fix.supplier"].create(
            {"name": self.vendor.name, "partner_id": self.vendor.id, "status": "active"}
        )
        self.branch = env["fix.branch"].search([], limit=1) or self._make_branch()
        self.loc = self.location("A")
        self.loc2 = self.location("B")

    # ---------------------------------------------------------------- builders
    def _make_branch(self):
        """M15 publishes a reorder rule per branch; the test database may hold
        no branch (nor the entity a branch belongs to)."""
        env = self.env
        entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
            "fix.entity"
        ].create(
            {
                "code": ("E%s" % self.tag)[:10],
                "legal_name": "M43 Entity %s" % self.tag,
                "company_id": env.company.id,
            }
        )
        return env["fix.branch"].create(
            {
                "code": ("M43%s" % self.tag)[:10],
                "name": "M43 Branch %s" % self.tag,
                "entity_id": entity.id,
                "operating_unit_id": self.ou.id,
            }
        )

    def user(self, role, groups=(), employee=True):
        env = self.env
        ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        login = "m43_%s_%s" % (role, self.tag.lower())
        user = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "group_ids": [(6, 0, ids)],
                    "assigned_operating_unit_ids": [(6, 0, self.ou.ids)],
                    "default_operating_unit_id": self.ou.id,
                }
            )
        )
        if employee:
            env["hr.employee"].create({"name": "Employee %s" % login, "user_id": user.id})
        return user

    def location(self, suffix, van=False):
        vals = {
            "name": "M43 Loc %s %s" % (suffix, self.tag),
            "code": ("M43%s%s" % (suffix, self.tag))[:16],
            "location_type": "van" if van else "branch",
            "company_id": self.company.id,
            "branch_id": self.branch.id,
        }
        if van:
            vals["technician_id"] = self.tech.id
        return self.env["fix.stock.location"].create(vals)

    def consume(self, qty, when, loc=None, part=None):
        if isinstance(when, date) and not isinstance(when, datetime):
            when = datetime(when.year, when.month, when.day, 10, 0)
        return self.env["fix.stock.consumption"].create(
            {
                "service_order_ref": "M43-SO-%s" % self.tag,
                "scanned_code": "M43-SCAN",
                "product_id": (part or self.part).id,
                "location_id": (loc or self.loc).id,
                "technician_id": self.tech.id,
                "quantity": qty,
                "state": "consumed",
                "consumed_at": when,
                "unit_cost": (part or self.part).unit_cost,
            }
        )

    def month(self, delta, day=5):
        return _month(self.this_month, delta).replace(day=day)

    def stock(self, qty, loc=None, part=None, ownership="owned"):
        return self.env["fix.stock.onhand"].create(
            {
                "part_id": (part or self.part).id,
                "location_id": (loc or self.loc).id,
                "ownership_class": ownership,
                "qty": qty,
                "unit_cost": 1000.0,
            }
        )

    def segment(self, abc="b", criticality="medium", classified=True, product=None):
        return self.env["fix.demand.segment"].create(
            {
                "product_id": (product or self.prod).id,
                "part_id": self.part.id,
                "abc_class": abc,
                "criticality": criticality,
                "classified_on": date.today() if classified else False,
            }
        )

    def policy(self, avg, std, lead, service="95", review=30, state="active", loc=None, **kw):
        vals = {
            "product_id": self.prod.id,
            "part_id": self.part.id,
            "location_id": (loc or self.loc).id,
            "avg_daily_demand": avg,
            "demand_stddev": std,
            "lead_time_days": lead,
            "service_level_pct": service,
            "review_period_days": review,
            "history_computed_on": datetime.now(),
            "state": state,
        }
        vals.update(kw)
        return self.env["fix.demand.policy"].create(vals)

    def forecast(self, qty, period=None, state="published", loc=None, **kw):
        vals = {
            "product_id": self.prod.id,
            "part_id": self.part.id,
            "location_id": (loc or self.loc).id,
            "period": period or self.period,
            "has_override": True,
            "override_qty": qty,
            "override_rationale": "test fixture",
            "state": state,
        }
        vals.update(kw)
        return self.env["fix.demand.forecast"].create(vals)

    def plan(self, user=None, **kw):
        nxt = _month(self.this_month, 1)
        vals = {
            "name": "M43-PLAN-%s" % self.tag,
            "period_start": self.this_month,
            "period_end": date.fromordinal(nxt.toordinal() - 1),  # last day of this month
            "product_id": self.tmpl.id,
            "part_id": self.part.id,
            "location_id": self.loc.id,
            "operating_unit_id": self.ou.id,
            "vendor_id": self.vendor.id,
        }
        vals.update(kw)
        return self.env["fix.demand.plan"].with_user(user or self.planner).create(vals)

    def ready_plan(self, forecast=10.0, stock=5.0, avg=2.0, std=0.0, lead=10, review=30):
        """Policy ROP = avg x lead (+ SS), published forecast and on-hand."""
        self.policy(avg, std, lead, review=review)
        self.forecast(forecast)
        if stock:
            self.stock(stock)
        return self.plan()


@pytest.fixture
def m43(odoo_env):
    return M43(odoo_env)


@pytest.fixture
def p03(m43):
    """Call /p03/model/write and /p03/model/action as a chosen user."""
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    ma = getattr(
        g.P03GenericApiController.model_action,
        "original_endpoint",
        g.P03GenericApiController.model_action,
    )
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(user):
        req = types.SimpleNamespace(env=m43.env(user=user.id))
        g.request = req
        s.request = req

    as_user(m43.clerk)
    try:
        yield types.SimpleNamespace(
            as_user=as_user,
            write=lambda **kw: mw(ctl, **kw),
            action=lambda **kw: ma(ctl, **kw),
        )
    finally:
        g.request, s.request = old_g, old_s
