# cd_inventory — Replenishment Engine & Reorder Rules with M43 Seam (CD-M15-02).
from __future__ import annotations

import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class FixReorderRule(models.Model):
    """Dynamic Spare Parts Replenishment Rules with M43 Machine Learning Seam.

    Controls minimum/maximum stocking thresholds across hubs, service centres,
    and mobile technician vans. In Phase R07, Milestone M43 extends the seam method
    `compute_dynamic_reorder_point()` with predictive demand forecasting without
    replacing this baseline logic.
    """

    _name = "fix.reorder.rule"
    _description = "Spare Part Reorder Rule"
    _order = "spare_part_id, branch_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
    suggested_order_qty = fields.Float(
        string="Suggested Order Qty",
        compute="_compute_suggested_order_qty",
        store=False,
    )

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
        for rec in self:
            if rec.spare_part_id:
                rec.current_stock = rec.spare_part_id.qty_available
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
                seq = self.env["ir.sequence"].next_by_code("fix.reorder.rule")
                vals["name"] = seq or f"RDR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return super().create(vals_list)

    def compute_dynamic_reorder_point(self) -> float:
        """M43 Seam Method: Computes dynamic reorder point.

        Baseline (Phase R03): Evaluates min_qty + safety_stock buffer.
        Phase R07 extension: When m43_ai_override is True, uses predictive
        lead-time demand modeling without modifying callers.
        """
        self.ensure_one()
        if self.m43_ai_override and self.m43_predicted_demand > 0:
            # Dynamic calculation from M43 demand model
            daily_forecast = self.m43_predicted_demand / 7.0
            lead_time_demand = daily_forecast * self.lead_time_days
            return round(lead_time_demand + self.safety_stock, 2)
        # Static heuristic fallback
        return self.min_qty + self.safety_stock

    def action_trigger_reorder(self) -> dict:
        """Manually or automatically trigger replenishment alert and outbox event."""
        self.ensure_one()
        self._compute_current_stock()
        order_qty = max(1.0, self.max_qty - self.current_stock)
        now_utc = fields.Datetime.now()

        self.write(
            {
                "state": "alert",
                "last_alert_date": now_utc,
            }
        )

        # Emit M15 outbox event: reorder.triggered
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

        return {
            "status": "alert_triggered",
            "rule": self.name,
            "part": self.spare_part_id.part_number,
            "order_qty": order_qty,
        }

    @api.model
    def check_replenishment_alerts(self) -> dict:
        """Cron / Scheduled Action to sweep all active reorder rules and trigger alerts."""
        active_rules = self.search([("state", "in", ["active", "alert"])])
        triggered = []

        for rule in active_rules:
            rule._compute_current_stock()
            if rule.current_stock <= rule.min_qty:
                res = rule.action_trigger_reorder()
                triggered.append(res)
            elif rule.state == "alert" and rule.current_stock > rule.min_qty:
                rule.write({"state": "active"})

        return {
            "rules_checked": len(active_rules),
            "alerts_triggered": len(triggered),
            "details": triggered,
        }
