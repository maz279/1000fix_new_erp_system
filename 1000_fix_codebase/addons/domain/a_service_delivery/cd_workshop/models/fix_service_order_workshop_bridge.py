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
            # A02 audit M31 step 1: a draft order has not been booked in at
            # the counter (no device receipt), so it does not reach the bench.
            if order.state == "draft":
                raise UserError(
                    "Order %s is still a draft: book the device in at M01 intake before "
                    "it is received into the workshop." % order.name
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
            # A02 audit M01-13 (M01-owned lines): the job uses the order's own
            # priority values; the old '0'-'3' keys sent urgent as 'normal'.
            priority_map = {
                "normal": "normal",
                "high": "high",
                "urgent": "urgent",
                "emergency": "emergency",
            }
            # ...and no second live workshop job for the same order.
            order._fix_assert_no_live_handoff(
                order.workshop_job_ids.filtered(
                    lambda j: j.state not in ("delivered", "cancelled")
                ),
                "workshop job",
            )
            job = Job.create(
                {
                    "order_id": order.id,
                    "workshop_id": workshop.id,
                    "device_id": order.device_id.id,
                    "customer_id": order.customer_id.id,
                    "repair_level": repair_level,
                    "priority": priority_map.get(order.priority or "normal", "normal"),
                    # fault_description is required on the job — the order's
                    # reported fault carries over (never fabricated)
                    "fault_description": order.fault_description
                    or "Handed over from service order %s" % order.name,
                    **order._m31_bookin_from_order(),
                }
            )
            job._m31_link_comeback()
            created |= job
        return created

    def _m31_bookin_from_order(self) -> dict:
        """A02 audit M31 step 2: the job's book-in starts from what the M01
        counter recorded at intake (condition, accessory bag, LCI, photo); the
        bench completes it and the job's intake checks it."""
        self.ensure_one()
        order = self.sudo()
        vals = {}
        if "cosmetic_condition_notes" in order._fields and order.cosmetic_condition_notes:
            vals["bookin_condition"] = order.cosmetic_condition_notes
        if "accessory_bag_barcode" in order._fields and order.accessory_bag_barcode:
            vals["bookin_accessory_bag"] = order.accessory_bag_barcode
            vals["bookin_accessories"] = "Sealed accessory bag %s (M01 intake)" % (
                order.accessory_bag_barcode
            )
        if "lci_tripped" in order._fields:
            vals["bookin_lci_tripped"] = bool(order.lci_tripped)
        if "intake_photo_attachment_id" in order._fields and order.intake_photo_attachment_id:
            vals["bookin_photo_attachment_id"] = order.intake_photo_attachment_id.id
        return vals
