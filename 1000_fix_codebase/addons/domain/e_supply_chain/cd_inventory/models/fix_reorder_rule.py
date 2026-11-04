# cd_inventory — Replenishment Engine & Reorder Rules with M43 Seam (CD-M15-02).
#
# A06 audit (2026-11-03) M15-12: the rule compared the company-wide
# aggregate (a hub par never alerted while another store held stock), the
# manual trigger alerted above the minimum, every sweep re-published the
# same alert, nothing scheduled the sweep, no requisition reached M16 and the
# workspace form let a clerk archive an alerting rule. Now current stock is
# the rule's OWN location (unrestricted, available, valued classes), an
# alert is raised only on ENTERING the reorder point (one event per
# shortage), the sweep is an ir.cron, the alert raises a draft M16
# requisition suggestion and the state is guarded.
from __future__ import annotations

import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_inventory_approval import VALUED_CLASSES

_logger = logging.getLogger(__name__)

# hr.employee id a replenishment requisition is raised in the name of when the
# rule, its location and its branch name nobody (business decision, unset).
PARAM_DEFAULT_REQUESTER = "cd_inventory.reorder_default_requester_id"


class FixReorderRule(models.Model):
    """Dynamic Spare Parts Replenishment Rules with M43 Machine Learning Seam."""

    _name = "fix.reorder.rule"
    _description = "Spare Part Reorder Rule"
    _order = "spare_part_id, branch_id"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )
    name = fields.Char(
        string="Rule Code",
        required=True,
        copy=False,
        default="New",
        index=True,
    )
    name_bn = fields.Char(
        string="রি-অর্ডার রুল নাম (বাংলা)",
        help="Bengali rule name per DoD-08",
    )

    spare_part_id = fields.Many2one(
        "fix.spare.part",
        string="Spare Part",
        required=True,
        index=True,
    )
    location_id = fields.Many2one(
        "fix.stock.location",
        string="Stock Location / Van",
        required=True,
        index=True,
    )
    branch_id = fields.Many2one(
        "fix.branch",
        string="Operating Branch / Hub",
        required=True,
        index=True,
    )
    requester_id = fields.Many2one(
        "hr.employee",
        string="Replenishment Requester",
        help="The employee a replenishment requisition is raised in the name of "
        "(the store keeper of this location). Without one the alert is raised "
        "but no requisition is drafted.",
    )

    min_qty = fields.Float(
        string="Minimum Stock (Reorder Point)",
        default=5.0,
        required=True,
        help="When stock falls at or below this level, replenishment is triggered",
    )
    max_qty = fields.Float(
        string="Target Maximum Stock",
        default=20.0,
        required=True,
        help="Target stock quantity after replenishment",
    )
    safety_stock = fields.Float(
        string="Safety Buffer Stock",
        default=2.0,
        required=True,
    )
    lead_time_days = fields.Integer(
        string="Replenishment Lead Time (Days)",
        default=3,
        required=True,
    )

    current_stock = fields.Float(
        string="Current Stock On Hand",
        compute="_compute_current_stock",
        store=False,
        help="Unrestricted, unreserved stock of the part at THIS location.",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active Rule"),
            ("alert", "Replenishment Alert"),
            ("ordered", "Requisition In Flight"),
            ("archived", "Archived"),
        ],
        string="Status",
        default="active",
        index=True,
        tracking=True,
    )

    last_alert_date = fields.Datetime(string="Last Alert Triggered At")
    requisition_id = fields.Many2one(
        "fix.requisition", string="Replenishment Requisition", readonly=True, copy=False
    )
    suggested_order_qty = fields.Float(
        string="Suggested Order Qty",
        compute="_compute_suggested_order_qty",
        store=False,
    )
    # provenance of the par levels when M43 publishes them from a plan
    published_by_id = fields.Many2one("res.users", string="Published By", readonly=True, copy=False)
    published_at = fields.Datetime(string="Published On", readonly=True, copy=False)
    plan_source_ref = fields.Char(string="Published From Plan", readonly=True, copy=False)

    # -------------------------------------------------------------------------
    # M43 Machine Learning Seam (Phase R07 Dynamic Replenishment extension)
    # -------------------------------------------------------------------------
    m43_ai_override = fields.Boolean(
        string="M43 Dynamic AI Forecast Active",
        default=False,
        help="When true, compute_dynamic_reorder_point() consumes ML demand forecasts",
    )
    m43_predicted_demand = fields.Float(
        string="M43 7-Day Forecast Demand",
        default=0.0,
        help="Populated by M43 demand forecast worker in Phase R07",
    )
    m43_model_version = fields.Char(
        string="M43 Seam Interface Version",
        default="m43_seam_v1.0",
        readonly=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "last_alert_date",
            "requisition_id",
            "published_by_id",
            "published_at",
            "plan_source_ref",
        }

    @api.constrains("min_qty", "max_qty")
    def _check_quantities(self):
        for rec in self:
            if rec.min_qty < 0:
                raise ValidationError("Minimum quantity cannot be negative.")
            if rec.max_qty <= rec.min_qty:
                raise ValidationError(
                    "Maximum stock level must strictly exceed minimum reorder point."
                )

    @api.depends("spare_part_id", "location_id")
    def _compute_current_stock(self):
        Onhand = self.env["fix.stock.onhand"].sudo()
        for rec in self:
            if rec.spare_part_id and rec.location_id:
                rows = Onhand.search(
                    [
                        ("part_id", "=", rec.spare_part_id.id),
                        ("location_id", "=", rec.location_id.id),
                        ("stock_status", "=", "unrestricted"),
                        ("ownership_class", "in", VALUED_CLASSES),
                    ]
                )
                rec.current_stock = round(sum(rows.mapped("available_qty")), 4)
            else:
                rec.current_stock = 0.0

    @api.depends("current_stock", "max_qty", "min_qty")
    def _compute_suggested_order_qty(self):
        for rec in self:
            if rec.current_stock <= rec.min_qty:
                rec.suggested_order_qty = max(0.0, rec.max_qty - rec.current_stock)
            else:
                rec.suggested_order_qty = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                seq = self.env["ir.sequence"].sudo().next_by_code("fix.reorder.rule")
                vals["name"] = seq or f"RDR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return super().create(vals_list)

    def compute_dynamic_reorder_point(self) -> float:
        """M43 Seam Method: Computes dynamic reorder point."""
        self.ensure_one()
        if self.m43_ai_override and self.m43_predicted_demand > 0:
            daily_forecast = self.m43_predicted_demand / 7.0
            lead_time_demand = daily_forecast * self.lead_time_days
            return round(lead_time_demand + self.safety_stock, 2)
        return self.min_qty + self.safety_stock

    # ----------------------------------------------------------- alerting
    def _enter_alert(self) -> dict:
        """Raise the alert once: state, event, requisition suggestion."""
        self.ensure_one()
        self._compute_current_stock()
        order_qty = max(1.0, self.max_qty - self.current_stock)
        now_utc = fields.Datetime.now()
        self._guarded().write({"state": "alert", "last_alert_date": now_utc})

        event_payload = {
            "rule_id": self.id,
            "rule_code": self.name,
            "spare_part_id": self.spare_part_id.id,
            "part_number": self.spare_part_id.part_number,
            "part_name": self.spare_part_id.name,
            "location_id": self.location_id.id,
            "location_code": self.location_id.code,
            "branch_id": self.branch_id.id,
            "branch_name": self.branch_id.name,
            "current_stock": self.current_stock,
            "min_qty": self.min_qty,
            "suggested_order_qty": order_qty,
            "m43_dynamic_reorder_point": self.compute_dynamic_reorder_point(),
            "triggered_at": str(now_utc),
        }
        try:
            from libs.py.fix_events import publish

            publish(self.env, "reorder.triggered", "fix.reorder.rule", self.id, event_payload)
        except Exception:
            _logger.exception("reorder.triggered event publish failed for rule %s", self.id)

        self._draft_requisition(order_qty)
        return {
            "status": "alert_triggered",
            "rule": self.name,
            "part": self.spare_part_id.part_number,
            "order_qty": order_qty,
        }

    def _draft_requisition(self, order_qty):
        """AUT-INV-03: hand the shortage to M16 as a DRAFT requisition (a
        suggestion a buyer reviews); the rule then reads 'Requisition In
        Flight'. Without a requester or an operating unit nothing is invented:
        the alert stands and the chatter says why."""
        self.ensure_one()
        if "fix.requisition" not in self.env:
            return False
        requester = self._replenishment_requester()
        ou = (
            self.operating_unit_id
            or self.location_id.operating_unit_id
            or self.branch_id.operating_unit_id
        )
        if not requester or not ou:
            self.message_post(
                body="Replenishment alert raised; NO requisition drafted (%s). Set the rule's "
                "requester, the branch manager or %s."
                % (
                    "no replenishment requester" if not requester else "no operating unit",
                    PARAM_DEFAULT_REQUESTER,
                )
            )
            return False
        part = self.spare_part_id
        try:
            with self.env.cr.savepoint():
                requisition = (
                    self.env["fix.requisition"]
                    .sudo()
                    .create(
                        {
                            "company_id": self.company_id.id,
                            "operating_unit_id": ou.id,
                            "branch_id": self.branch_id.id,
                            "requested_by": requester.id,
                            "description": "Replenish %s at %s: %s %s (reorder rule %s)"
                            % (
                                part.part_number,
                                self.location_id.code,
                                order_qty,
                                part.uom or "PCS",
                                self.name,
                            ),
                            "estimate_amount": round(
                                order_qty * (part.average_cost or part.unit_cost or 0.0), 2
                            ),
                            "urgency": "urgent" if self.current_stock <= 0 else "normal",
                        }
                    )
                )
        except Exception as exc:  # the M16 model refused the suggestion
            _logger.warning("reorder rule %s: requisition not drafted: %s", self.name, exc)
            self.message_post(body="Replenishment alert raised; requisition refused: %s" % exc)
            return False
        self._guarded().write({"state": "ordered", "requisition_id": requisition.id})
        return requisition

    def _replenishment_requester(self):
        """Who the requisition is raised in the name of (A06 M15-12): the
        rule's requester, else the location's custodian, else the branch
        manager, else the configured default, else the acting user."""
        self.ensure_one()
        Employee = self.env["hr.employee"].sudo()
        branch = self.branch_id.sudo()
        manager = (
            branch.employee_manager_id if "employee_manager_id" in branch._fields else Employee
        )
        if not manager and branch.manager_id:
            manager = Employee.search([("user_id", "=", branch.manager_id.id)], limit=1)
        default = Employee
        raw = self.env["ir.config_parameter"].sudo().get_param(PARAM_DEFAULT_REQUESTER)
        if raw:
            try:
                default = Employee.browse(int(raw)).exists()
            except (TypeError, ValueError):
                default = Employee
        acting = Employee.search([("user_id", "=", self.env.uid)], limit=1)
        return self.requester_id or self.location_id.technician_id or manager or default or acting

    def action_trigger_reorder(self) -> dict:
        """Manual trigger: only at or below the reorder point, and only once
        per shortage."""
        self.ensure_one()
        self._compute_current_stock()
        if self.state in ("alert", "ordered"):
            raise UserError("Rule %s is already alerting for this shortage." % self.name)
        if self.state not in ("active", "draft"):
            raise UserError("Rule %s is archived." % self.name)
        if self.current_stock > self.min_qty:
            raise UserError(
                "Stock of %s at %s is %s, above the reorder point %s: nothing to reorder."
                % (
                    self.spare_part_id.part_number,
                    self.location_id.code,
                    self.current_stock,
                    self.min_qty,
                )
            )
        return self._enter_alert()

    def action_activate(self):
        for rec in self:
            if rec.state not in ("draft", "archived"):
                raise UserError("Rule %s is already active." % rec.name)
            rec._guarded().write({"state": "active"})
        return True

    def action_archive_rule(self):
        for rec in self:
            if rec.state in ("alert", "ordered"):
                raise UserError(
                    "Rule %s is alerting a shortage: it cannot be archived until stock "
                    "recovers." % rec.name
                )
            rec._guarded().write({"state": "archived"})
        return True

    @api.model
    def check_replenishment_alerts(self) -> dict:
        """The ir.cron sweep: alert rules that ENTER their reorder point; clear
        alerts whose stock recovered. A rule already alerting is not
        re-published."""
        rules = self.search([("state", "in", ["active", "alert", "ordered"])])
        triggered = []
        for rule in rules:
            rule._compute_current_stock()
            if rule.state == "active" and rule.current_stock <= rule.min_qty:
                triggered.append(rule._enter_alert())
            elif rule.state in ("alert", "ordered") and rule.current_stock > rule.min_qty:
                rule._guarded().write({"state": "active", "requisition_id": False})
        return {
            "rules_checked": len(rules),
            "alerts_triggered": len(triggered),
            "details": triggered,
        }

    # ------------------------------------------------- cross-builder contract
    @api.model
    def _fix_publish_from_plan(
        self, part, location, min_qty, max_qty, source_ref, predicted_demand=None
    ):
        """M43 publishes par levels from an approved plan: create or update
        the rule of this part at this location and record who published it
        and from what plan. Returns the rule."""
        if not part or not location:
            raise UserError("A published reorder rule needs a part and a location.")
        if min_qty is None or max_qty is None or min_qty < 0 or max_qty <= min_qty:
            raise UserError(
                "Plan %s: maximum (%s) must exceed the minimum (%s) and neither be negative."
                % (source_ref, max_qty, min_qty)
            )
        stamp = {
            "min_qty": min_qty,
            "max_qty": max_qty,
            "published_by_id": self.env.user.id,
            "published_at": fields.Datetime.now(),
            "plan_source_ref": source_ref or False,
        }
        if predicted_demand is not None:
            if predicted_demand < 0:
                raise UserError("Plan %s: the predicted demand cannot be negative." % source_ref)
            stamp["m43_predicted_demand"] = predicted_demand
        rule = self.sudo().search(
            [("spare_part_id", "=", part.id), ("location_id", "=", location.id)], limit=1
        )
        if rule:
            rule._guarded().write(stamp)
            if rule.state == "archived":
                rule._guarded().write({"state": "active"})
            return rule.with_env(self.env)
        branch = location.branch_id
        if not branch and location.operating_unit_id and "fix.branch" in self.env:
            branch = (
                self.env["fix.branch"]
                .sudo()
                .search([("operating_unit_id", "=", location.operating_unit_id.id)], limit=1)
            )
        if not branch:
            raise UserError(
                "Location %s has no branch: set its branch before publishing a reorder rule."
                % location.code
            )
        vals = dict(
            stamp,
            spare_part_id=part.id,
            location_id=location.id,
            branch_id=branch.id,
            company_id=location.company_id.id or part.company_id.id,
            operating_unit_id=location.operating_unit_id.id or False,
            state="active",
        )
        return self.sudo()._guarded().create(vals).with_env(self.env)
