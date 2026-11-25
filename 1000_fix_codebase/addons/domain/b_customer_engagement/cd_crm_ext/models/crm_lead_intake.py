# R8 consumer: a marketing journey asks M07 for a lead.
#
# A03 audit §4.1 step 1: cd_campaign's journey "publish event" step emits
# journey.lead_requested (fix_journey_runtime.py `_step_publish_event`) so
# that a journey can hand a warm contact to sales without depending on
# cd_crm_ext. Nothing consumed it, so the hand-off stopped at the outbox row.
#
# Payload (contracts/events/journey_lead_requested.json):
#   journey_id, journey, campaign_id, partner_id, step, note
# The aggregate is the fix.campaign.journey.member.
#
# Idempotent twice over: per EVENT (a redelivered event is a no-op), and per
# SOURCE (the same party, asked for again by the same journey while its lead
# is still open, is linked to that lead with a note instead of duplicated).
from odoo import api, fields, models


class CrmLeadIntake(models.Model):
    _inherit = "crm.lead"

    source_event_id = fields.Char(
        string="Source Event",
        index=True,
        copy=False,
        readonly=True,
        help="The outbox event that raised this lead (journey.lead_requested).",
    )
    source_ref = fields.Char(
        string="Source Reference",
        index=True,
        copy=False,
        readonly=True,
        help="journey:<id>:partner:<id> for a lead a marketing journey requested.",
    )
    source_event_log = fields.Text(
        string="Later Requests",
        copy=False,
        readonly=True,
        help="Event ids of later requests for the same lead, one per line.",
    )

    @staticmethod
    def _journey_source_ref(payload: dict, aggregate_id) -> str:
        partner_id = payload.get("partner_id")
        if partner_id:
            return "journey:%s:partner:%s" % (payload.get("journey_id") or 0, partner_id)
        return "journey:%s:member:%s" % (payload.get("journey_id") or 0, aggregate_id or 0)

    @api.model
    def _journey_lead_owner(self, partner):
        """The account's current owner (BRU-CRM-08), else nobody: an
        unassigned lead is visible to the team, a lead assigned to the
        consumer's superuser is not."""
        if not partner:
            return self.env["res.users"]
        assignment = (
            self.env["fix.account.assignment"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", partner.commercial_partner_id.id),
                    ("effective_to", "=", False),
                ],
                order="effective_from desc, id desc",
                limit=1,
            )
        )
        return assignment.owner_id

    @api.model
    def consume_journey_lead_requested(self, event: dict):
        """Create, or link, the CRM lead a journey asked for. Returns the lead."""
        payload = event.get("payload") or {}
        event_id = event.get("event_id") or ""
        Lead = self.sudo().with_context(active_test=False, mail_create_nosubscribe=True)
        if event_id:
            seen = Lead.search(
                [
                    "|",
                    ("source_event_id", "=", event_id),
                    ("source_event_log", "ilike", event_id),
                ],
                limit=1,
            )
            if seen:
                return seen

        partner = self.env["res.partner"].browse()
        if payload.get("partner_id"):
            partner = self.env["res.partner"].sudo().browse(int(payload["partner_id"])).exists()
        source_ref = self._journey_source_ref(payload, event.get("aggregate_id"))
        note = (payload.get("note") or "").strip()

        open_lead = Lead.search(
            [("source_ref", "=", source_ref), ("active", "=", True), ("probability", "<", 100)],
            limit=1,
        )
        if open_lead:
            log = "\n".join(filter(None, [open_lead.source_event_log, event_id]))
            open_lead.write({"source_event_log": log})
            open_lead.message_post(
                body="Journey '%s' asked for this lead again (step '%s')%s."
                % (
                    payload.get("journey") or "",
                    payload.get("step") or "",
                    ": %s" % note if note else "",
                )
            )
            return open_lead

        owner = self._journey_lead_owner(partner)
        company_id = event.get("company_id") or self.env.company.id
        return Lead.create(
            {
                "name": "Campaign lead: %s (%s)"
                % (partner.name or "unknown contact", payload.get("journey") or "journey"),
                "type": "lead",
                "lead_source": "campaign",
                "partner_id": partner.id or False,
                "user_id": owner.id or False,
                "company_id": company_id,
                "description": note or False,
                "source_event_id": event_id or False,
                "source_ref": source_ref,
            }
        )
