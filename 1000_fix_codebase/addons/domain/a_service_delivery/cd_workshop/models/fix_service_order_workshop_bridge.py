# fix.service.order bridge (M31): the order book → workshop pipeline seam.
# 921 service orders existed with ZERO workshop jobs — nothing created one
# (measured 2026-10-26: all five cd_workshop tables empty). Workshop-type
# orders (walk-in bench jobs and mail-in devices) now hand over with one
# action; the job inherits workshop (branch-matched), device, customer,
# priority and the L1 default repair level for bench routing.
from odoo import fields, models
from odoo.exceptions import UserError


class FixServiceOrderWorkshopBridge(models.Model):
    _inherit = "fix.service.order"

    workshop_job_ids = fields.One2many("fix.workshop.job", "order_id", string="Workshop Jobs")
    workshop_job_count = fields.Integer(
        string="Workshop Jobs", compute="_compute_workshop_job_count"
    )

    def _compute_workshop_job_count(self):
        for order in self:
            order.workshop_job_count = len(order.workshop_job_ids)

    def _default_workshop(self):
        """Pick this order's workshop: the one attached to the order's
        branch if linked, else the central workshop, else any active."""
        Workshop = self.env["fix.workshop"].sudo()
        candidates = Workshop.search([("active", "=", True)])
        if not candidates:
            return Workshop
        # branch-linked first
        linked = candidates.filtered(lambda w: w.branch_id == self.branch_id)
        if linked:
            return linked[:1]
        central = candidates.filtered(lambda w: w.workshop_type == "central")
        return (central or candidates)[:1]

    def action_create_workshop_job(self, repair_level="l1", workshop_id=None):
        """Hand a service order to the workshop pipeline (M31). Creates a
        DRAFT workshop job routed at the given repair level (L1 modular
        default; L2/L3 remain a supervisor decision — the certification and
        burn-in gates apply from there)."""
        Job = self.env["fix.workshop.job"]
        created = Job
        for order in self:
            if order.state in ("closed", "cancelled"):
                raise UserError(
                    "Order %s is %s — it can no longer enter the workshop."
                    % (order.name, order.state)
                )
            if workshop_id:
                workshop = self.env["fix.workshop"].sudo().browse(workshop_id).exists()
            else:
                workshop = order._default_workshop()
            if not workshop:
                raise UserError(
                    "No active workshop facility exists — create one first "
                    "(Workshop Facilities master)."
                )
            priority_map = {"0": "normal", "1": "normal", "2": "high", "3": "urgent"}
            created |= Job.create(
                {
                    "order_id": order.id,
                    "workshop_id": workshop.id,
                    "device_id": order.device_id.id,
                    "customer_id": order.customer_id.id,
                    "repair_level": repair_level,
                    "priority": priority_map.get(order.priority or "1", "normal"),
                    # fault_description is required on the job — the order's
                    # reported fault carries over (never fabricated)
                    "fault_description": order.fault_description
                    or "Handed over from service order %s" % order.name,
                }
            )
        return created
