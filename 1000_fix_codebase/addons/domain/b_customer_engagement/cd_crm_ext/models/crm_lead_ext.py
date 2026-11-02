# crm.lead extension — party-linked, lead-to-service-order conversion (P04-M04).
# Extended, not forked (AS-05/FF-03). M07 rebuild (2026-10-27) adds the
# pipeline, forecast-category, win/loss and stage-gating fields.
import logging
from datetime import timedelta

from odoo import fields, models
from odoo.exceptions import ValidationError
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

    # --- M07 rebuild: pipeline, forecast, win/loss, stage gating ------------
    pipeline_id = fields.Many2one(
        "fix.pipeline",
        string="Pipeline",
        index=True,
        tracking=True,
        help="FR-CRM-010: distinct pipelines per revenue stream (fix.pipeline)",
    )
    forecast_category = fields.Selection(
        [
            ("commit", "Commit"),
            ("best_case", "Best Case"),
            ("pipeline", "Pipeline"),
            ("omitted", "Omitted"),
        ],
        string="Forecast Category",
        default="pipeline",
        tracking=True,
        help="FR-CRM-019: classified independently of stage probability",
    )
    competitor = fields.Char(string="Competitor", help="FR-CRM-015 win/loss intelligence")
    competitor_price_bdt = fields.Monetary(
        string="Competitor Bid (BDT)",
        currency_field="company_currency",
        help="Competitor bid price in BDT for win/loss analysis",
    )
    loss_reason_category = fields.Selection(
        [
            ("price", "Price / Commercials"),
            ("sla_capability", "SLA / Capability"),
            ("payment_terms", "Payment Terms"),
            ("competitor_incumbent", "Competitor Incumbent"),
            ("other", "Other"),
        ],
        string="Loss Reason Category",
        tracking=True,
    )
    price_position = fields.Selection(
        [("premium", "Premium"), ("par", "At Market"), ("discounted", "Discounted")],
        string="Price Position",
    )
    lost_reason_code = fields.Char(
        string="Loss Reason Code",
        help="BRU-CRM-05: every Lost outcome requires a structured reason",
    )
    contract_ref = fields.Char(
        string="Contract / PO Reference",
        tracking=True,
        help="Reference to signed customer contract or PO in Documents tab (REQ-07.1)",
    )
    contract_verified = fields.Boolean(
        string="Contract / PO Verified",
        default=False,
        tracking=True,
        help="Verified status of attached contract or PO (REQ-07.1)",
    )
    rate_card_approved = fields.Boolean(
        string="Commercial Rate Card Approved",
        default=False,
        tracking=True,
        help="Approved status of corporate commercial rate card (FLAW-07.1)",
    )
    is_cross_sell = fields.Boolean(
        string="Cross-Sell / Upsell",
        index=True,
        help="FR-CRM-044: qualified expansion from the installed base",
    )
    criteria_confirmed = fields.Boolean(
        string="Stage Entry Criteria Confirmed",
        help="BRU-CRM-03: confirmed immediately before advancing into a gated "
        "stage; resets on every stage change",
    )

    def _check_won_gate(self, vals, lead=None):
        """REQ-07.1: a deal becomes Won by ANY path — a won stage, probability
        reaching 100, or creation directly at 100 — only with a verified signed
        contract / PO and no credit hold. (Audit 2026-10-31: creating an
        opportunity at probability=100 bypassed the stage-only gate.)"""
        becoming_won = False
        if "stage_id" in vals:
            stage = self.env["crm.stage"].browse(vals["stage_id"]).exists()
            becoming_won = bool(stage and getattr(stage, "is_won", False))
        if vals.get("probability") == 100:
            becoming_won = True
        if not becoming_won:
            return
        partner = (
            vals.get("partner_id") and self.env["res.partner"].browse(vals["partner_id"])
        ) or (lead and lead.partner_id)
        contract_ref = vals.get("contract_ref") or (lead and lead.contract_ref) or False
        contract_verified = vals.get(
            "contract_verified", (lead and lead.contract_verified) or False
        )
        if not (contract_ref and contract_verified):
            raise ValidationError(
                "Stage gate violation: Signed customer contract or Purchase Order reference and verification required in Documents tab before marking as Won (REQ-07.1)."
            )
        if partner and partner.party_status in ("blocked", "credit_hold"):
            raise ValidationError(
                "Cannot mark opportunity as Won: Linked customer party '%s' is on credit hold or blocked."
                % partner.name
            )
        # REQ-07.1 also bars a win while the client carries receivables more
        # than 60 days overdue. party_status is a manual flag; this measures
        # the ledger (audit 2026-10-31: the gate never looked at invoices).
        if partner:
            overdue = self._overdue_receivables(partner, days=60)
            if overdue:
                raise ValidationError(
                    "Cannot mark opportunity as Won: '%s' has %d invoice(s) more "
                    "than 60 days overdue totalling BDT %.2f. Clear the "
                    "receivable or obtain a credit waiver first (REQ-07.1)."
                    % (partner.name, len(overdue), sum(overdue.mapped("amount_residual")))
                )

    def _overdue_receivables(self, partner, days=60):
        """Issued invoices for this party still unpaid beyond `days`.

        Returns an empty recordset when M20 billing is not installed, so the
        gate degrades to the party_status check rather than blocking sales.
        """
        if "fix.ar.invoice" not in self.env:
            return self.env["crm.lead"].browse()
        cutoff = fields.Date.today() - timedelta(days=days)
        return (
            self.env["fix.ar.invoice"]
            .sudo()
            .search(
                [
                    ("customer_id", "=", partner.commercial_partner_id.id),
                    ("state", "not in", ("draft", "cancelled", "paid")),
                    ("amount_residual", ">", 0),
                    ("invoice_date", "<=", cutoff),
                ]
            )
        )

    def create(self, vals):
        vals = dict(vals or {})
        if vals.get("type") in (False, "opportunity") or "type" not in vals:
            self._check_won_gate(vals)
        return super().create(vals)

    def write(self, vals):
        target_stage = None
        if "stage_id" in vals:
            target_stage = self.env["crm.stage"].browse(vals["stage_id"]).exists()
            moved_pipeline = (
                self.env["fix.pipeline"].browse(vals["pipeline_id"]).exists()
                if vals.get("pipeline_id")
                else None
            )
            vals = dict(vals)
            for lead in self:
                pipeline = moved_pipeline or lead.pipeline_id
                entry = (
                    pipeline.stage_rules().get(target_stage.name)
                    if (pipeline and target_stage)
                    else None
                )
                if (
                    entry
                    and entry.get("requires_confirmation")
                    and (not vals.get("criteria_confirmed") and not lead.criteria_confirmed)
                ):
                    raise ValidationError(
                        "Stage '%s' requires its entry criteria confirmed before "
                        "advancing (BRU-CRM-03: %s)"
                        % (target_stage.name, entry.get("criteria") or "criteria not met")
                    )
                # REQ-07.1: Gating for transitions to Won (stage path)
                if (
                    target_stage
                    and getattr(target_stage, "is_won", False)
                    and lead.type == "opportunity"
                ):
                    self._check_won_gate({**vals, "stage_id": target_stage.id}, lead)

            # confirmation is per stage entry: it is consumed by the move
            vals["criteria_confirmed"] = False

        # REQ-07.1: ...and the probability path. This MUST sit outside the
        # `stage_id` branch: writing probability=100 on its own also wins the
        # deal, and nesting the check left `lead.write({"probability": 100})`
        # as an unguarded route to Won (A03 zero-trust audit 2026-10-31).
        if vals.get("probability") == 100:
            for lead in self:
                if lead.type == "opportunity" and lead.probability != 100:
                    self._check_won_gate({k: v for k, v in vals.items() if k != "stage_id"}, lead)

        # FLAW-07.2: Transition to Lost must capture competitor and structured reason
        if vals.get("probability") == 0:
            for lead in self:
                if lead.type == "opportunity" and (lead.probability or 0) > 0:
                    comp = vals.get("competitor") or lead.competitor
                    reason = vals.get("lost_reason_code") or lead.lost_reason_code
                    if not comp or not comp.strip():
                        raise ValidationError(
                            "Loss analysis mandatory: Please specify winning competitor (FLAW-07.2 / REQ-07.3)."
                        )
                    if not reason or not reason.strip():
                        raise ValidationError(
                            "Loss analysis mandatory: Please specify structured loss reason code (FLAW-07.2 / BRU-CRM-05)."
                        )
        return super().write(vals)

    # Conversion tracking (T06: lead-to-service-order)
    converted_service_order_id = fields.Many2one(
        "fix.service.order",
        string="Converted Service Order",
        readonly=True,
        help="The service order created from this lead",
    )

    def action_convert_to_service_order(self):
        """Convert a lead to a service order (T06).

        FLAW-07.1: Restrict conversion exclusively to Won stage with approved
        commercial rate card and no credit hold — for leads AND opportunities
        (an unqualified lead bypassing the gate was the original flaw).
        """
        for lead in self:
            is_won = (
                getattr(lead.stage_id, "is_won", False)
                or (lead.stage_id and "won" in (lead.stage_id.name or "").lower())
                or (lead.probability == 100)
            )
            if not is_won:
                raise ValidationError(
                    "Converting an opportunity into a service order is restricted exclusively to opportunities in 'won' stage (FLAW-07.1 / REQ-07.2)."
                )
            if not lead.rate_card_approved:
                raise ValidationError(
                    "Cannot convert opportunity: Active approved commercial rate card is required (FLAW-07.1)."
                )
            if lead.partner_id and lead.partner_id.party_status in ("blocked", "credit_hold"):
                raise ValidationError(
                    "Cannot convert opportunity: Customer account '%s' is currently on credit hold or blocked (FLAW-07.1)."
                    % lead.partner_id.name
                )

            if not lead.partner_id:
                raise ValidationError("Cannot convert: No customer linked to this lead.")

            device = self.env["fix.device"].search(
                [("owner_id", "child_of", lead.partner_id.commercial_partner_id.id)],
                order="id desc",
                limit=1,
            )
            if not device:
                raise ValidationError(
                    "Cannot convert: The customer has no registered device (M17)."
                )

            branch = device.branch_id or self.env["fix.branch"].search([], limit=1)
            if not branch:
                raise ValidationError("Cannot convert: No branch is configured.")

            order = self.env["fix.service.order"].create(
                {
                    "customer_id": lead.partner_id.id,
                    "device_id": device.id,
                    "branch_id": branch.id,
                    "service_type": "walk_in",
                    "fault_description": html2plaintext(lead.description or "").strip()
                    or "Converted from CRM lead",
                    "state": "intake",
                }
            )
            lead.converted_service_order_id = order.id
            if not getattr(lead.stage_id, "is_won", False):
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
