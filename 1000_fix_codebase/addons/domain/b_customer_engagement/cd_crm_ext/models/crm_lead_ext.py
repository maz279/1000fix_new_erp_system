# crm.lead extension — party-linked, lead-to-service-order conversion (P04-M04).
# Extended, not forked (AS-05/FF-03). W1 slice: lead + opportunity only.
import logging

from odoo import fields, models
from odoo.tools import html2plaintext

logger = logging.getLogger(__name__)


class CrmLeadExt(models.Model):
    """Extend Odoo crm.lead with party-kernel linkage and service-order conversion.

    W1 scope: lead and opportunity only. Quotation/pricing (W4 slice)
    is deferred explicitly in the backlog (P04-M04-T08).
    """

    _inherit = "crm.lead"

    # Party kernel linkage (T03: an account is a party with a customer role)
    party_role_id = fields.Many2one(
        "fix.party.role",
        string="Party Role (Customer)",
        domain=[("role_type", "=", "customer")],
        help="The fix.party.role linking this lead's account to the party kernel",
    )
    linked_partner_id = fields.Many2one(
        "res.partner",
        string="Linked Party",
        related="party_role_id.partner_id",
        store=True,
        readonly=True,
        help="The res.partner this lead maps to through the party kernel",
    )

    # Lead source tracking
    lead_source = fields.Selection(
        [
            ("walk_in", "Walk-in"),
            ("hotline", "Hotline 16743"),
            ("website", "Website"),
            ("portal", "Portal P01"),
            ("referral", "Referral"),
            ("campaign", "Campaign"),
            ("social", "Social Media"),
        ],
        default="walk_in",
        tracking=True,
    )

    # Conversion tracking (T06: lead-to-service-order)
    converted_service_order_id = fields.Many2one(
        "fix.service.order",
        string="Converted Service Order",
        readonly=True,
        help="The service order created from this lead",
    )

    def action_convert_to_service_order(self):
        """Convert a lead to a service order (T06).

        M17: every order needs an identified device - the order is opened on the
        customer's most recently registered device, at that device's branch
        (else the first branch). The lead moves to 'won'. A lead without a
        customer, a registered device or any branch is not converted; the
        chatter says why.

        Fixed (R01 coverage pass): the order was created with neither a device
        nor a branch - both required - so every conversion failed; crm.lead has
        no branch_id, so the old ``hasattr`` probe was always False.
        """
        for lead in self:
            if not lead.partner_id:
                lead.message_post(body="Cannot convert: no customer linked to this lead.")
                continue
            device = self.env["fix.device"].search(
                [("owner_id", "child_of", lead.partner_id.commercial_partner_id.id)],
                order="id desc",
                limit=1,
            )
            if not device:
                lead.message_post(
                    body="Cannot convert: the customer has no registered device (M17)."
                )
                continue
            branch = device.branch_id or self.env["fix.branch"].search([], limit=1)
            if not branch:
                lead.message_post(body="Cannot convert: no branch is configured.")
                continue
            order = self.env["fix.service.order"].create(
                {
                    "customer_id": lead.partner_id.id,
                    "device_id": device.id,
                    "branch_id": branch.id,
                    "service_type": "walk_in",
                    # crm.lead.description is HTML; the order's fault is plain text
                    "fault_description": html2plaintext(lead.description or "").strip()
                    or "Converted from CRM lead",
                    "state": "intake",
                }
            )
            lead.converted_service_order_id = order.id
            lead.action_set_won()
            self._emit_lead_event("lead.converted_to_order", lead, order)

    def _emit_lead_event(self, event: str, lead, order=None):
        from libs.py.fix_events import publish

        publish(
            self.env,
            event,
            "crm.lead",
            lead.id,
            {
                "lead_id": lead.id,
                "lead_name": lead.name,
                "partner_id": lead.partner_id.id if lead.partner_id else None,
                "service_order_id": order.id if order else None,
            },
        )
