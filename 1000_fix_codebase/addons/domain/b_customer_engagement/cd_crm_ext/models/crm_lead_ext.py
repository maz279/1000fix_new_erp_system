# crm.lead extension — party-linked, lead-to-service-order conversion (P04-M04).
# Extended, not forked (AS-05/FF-03). W1 slice: lead + opportunity only.
from odoo import api, fields, models

import logging

logger = logging.getLogger(__name__)


class CrmLeadExt(models.Model):
    """Extend Odoo crm.lead with party-kernel linkage and service-order conversion.

    W1 scope: lead and opportunity only. Quotation/pricing (W4 slice)
    is deferred explicitly in the backlog (P04-M04-T08).
    """
    _inherit = "crm.lead"

    # Party kernel linkage (T03: an account is a party with a customer role)
    party_role_id = fields.Many2one(
        "fix.party.role", string="Party Role (Customer)",
        domain=[("role_type", "=", "customer")],
        help="The fix.party.role linking this lead's account to the party kernel")
    linked_partner_id = fields.Many2one(
        "res.partner", string="Linked Party",
        related="party_role_id.partner_id", store=True, readonly=True,
        help="The res.partner this lead maps to through the party kernel")

    # Lead source tracking
    lead_source = fields.Selection(
        [("walk_in", "Walk-in"), ("hotline", "Hotline 16743"),
         ("website", "Website"), ("portal", "Portal P01"),
         ("referral", "Referral"), ("campaign", "Campaign"),
         ("social", "Social Media")],
        default="walk_in", tracking=True)

    # Conversion tracking (T06: lead-to-service-order)
    converted_service_order_id = fields.Many2one(
        "fix.service.order", string="Converted Service Order", readonly=True,
        help="The service order created from this lead")

    def action_convert_to_service_order(self):
        """Convert a lead to a service order (T06).

        Creates a service order with the lead's customer and device info.
        The lead moves to 'won' stage.
        """
        for lead in self:
            if not lead.partner_id:
                lead.message_post(body="Cannot convert: no customer linked to this lead.")
                continue
            order = self.env["fix.service.order"].create({
                "customer_id": lead.partner_id.id,
                "branch_id": lead.branch_id.id if hasattr(lead, 'branch_id') and lead.branch_id else False,
                "service_type": "walk_in",
                "fault_description": lead.description or "Converted from CRM lead",
                "state": "intake",
            })
            lead.converted_service_order_id = order.id
            lead.action_set_won()
            self._emit_lead_event("lead.converted_to_order", lead, order)

    def _emit_lead_event(self, event: str, lead, order=None):
        from libs.py.fix_events import publish
        publish(self.env, event, "crm.lead", lead.id, {
            "lead_id": lead.id, "lead_name": lead.name,
            "partner_id": lead.partner_id.id if lead.partner_id else None,
            "service_order_id": order.id if order else None,
        })
