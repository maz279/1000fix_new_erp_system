# crm.lead extension — party-linked, lead-to-service-order conversion (P04-M04).
# Extended, not forked (AS-05/FF-03). M07 rebuild (2026-10-27) adds the
# pipeline, forecast-category, win/loss and stage-gating fields.
#
# A03 P2 (2026-11-03): the Won gate was self-certified. The seller ticked
# `contract_verified` and `rate_card_approved` on their own deal and won it
# (A03 audit G-M07-1). Both are now evidence fields that only the routed
# contract verification (M63 engine, domain contract_verification) sets, and
# the approver is never the seller or the record's creator.
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext

logger = logging.getLogger(__name__)

# Who verifies a seller's signed contract / PO. A sales manager (Odoo's
# "Sales: Administrator") is the default; a fix.approval.matrix row for the
# contract_verification domain can name another group without a code change.
CONTRACT_VERIFIER_GROUP = "sales_team.group_sale_manager"

# The loss-analysis fields a Lost outcome must carry (FLAW-07.2 / BRU-CRM-05).
LOSS_FIELDS = (
    "competitor",
    "competitor_price_bdt",
    "loss_reason_category",
    "lost_reason_code",
    "lost_reason_id",
)


class CrmLeadExt(models.Model):
    """Extend Odoo crm.lead with party-kernel linkage and service-order conversion.

    W1 scope: lead and opportunity only. The estimate hand-off (the A03 P2
    "approved quote before order" rule) lives in crm_lead_quote.py.
    """

    _name = "crm.lead"
    _inherit = ["crm.lead", "fix.approvable.mixin"]

    # A03 audit G-M07-1 / R7: contract verification is a routed approval.
    _approval_domain = "contract_verification"
    _approval_apply_method = "action_verify_contract"
    _approval_group = CONTRACT_VERIFIER_GROUP
    _approval_routed = True

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
        readonly=True,
        copy=False,
        tracking=True,
        help="Set only by the routed contract verification (M63): a sales "
        "manager other than the seller checks the signed contract / PO "
        "(REQ-07.1, A03 audit G-M07-1).",
    )
    rate_card_approved = fields.Boolean(
        string="Commercial Rate Card Approved",
        default=False,
        readonly=True,
        copy=False,
        tracking=True,
        help="Confirmed by the same verifier, who checks that the contract / "
        "PO prices match the approved commercial rate card (FLAW-07.1). The "
        "seller cannot set it.",
    )
    contract_verified_by = fields.Many2one(
        "res.users", string="Contract Verified By", readonly=True, copy=False
    )
    contract_verified_at = fields.Datetime(string="Contract Verified On", readonly=True, copy=False)
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

    # Conversion tracking (T06: lead-to-service-order)
    converted_service_order_id = fields.Many2one(
        "fix.service.order",
        string="Converted Service Order",
        readonly=True,
        copy=False,
        help="The service order created from this lead",
    )

    # ------------------------------------------------------------------
    # Field guard and the routed contract verification (G-M07-1)
    # ------------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "contract_verified",
            "rate_card_approved",
            "contract_verified_by",
            "contract_verified_at",
            "converted_service_order_id",
        }

    def _fix_form_locked_fields(self) -> set:
        """M07 audit 2026-11-13: the Lead and Opportunity forms post the record
        type they create (no user holds crm.group_use_lead on the estate, so
        Odoo's default made every "+ New Lead" an opportunity, invisible on
        the Leads list). Once the record exists the type changes only through
        conversion, which checks the party match (BRU-CRM-02)."""
        locked = super()._fix_form_locked_fields()
        return locked | {"type"} if self else locked

    def action_convert_to_opportunity(self):
        """FR-CRM-006/007: a qualified lead becomes an opportunity on the
        party it was matched to; conversion never creates a party (BRU-CRM-02,
        BRU-CRM-01 - party identity belongs to M33). The source attribution
        and everything captured on the lead are kept."""
        for lead in self:
            if lead.type != "lead":
                raise UserError("'%s' is already an opportunity." % lead.name)
            if not lead.active:
                raise UserError("'%s' is archived; restore it before converting." % lead.name)
            if not lead.partner_id:
                raise UserError(
                    "Match '%s' to its customer in the party master first (Linked "
                    "Customer / Party on the lead). A lead never creates a new "
                    "party when it converts (BRU-CRM-02)." % lead.name
                )
        for lead in self:
            lead.convert_opportunity(lead.partner_id)
            lead.message_post(
                body="Converted to an opportunity on %s." % lead.partner_id.display_name
            )
        return True

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return bool((self.contract_ref or "").strip()) and not self.contract_verified

    def _approval_excluded(self):
        """The seller never verifies their own deal, even when they are not
        the record's creator (a lead reassigned to them, or raised by a
        campaign)."""
        return super()._approval_excluded() | self.user_id.sudo()

    def action_request_contract_verification(self, justification=None):
        """Ask a sales manager to verify the signed contract / PO (REQ-07.1)."""
        for lead in self:
            if not (lead.contract_ref or "").strip():
                raise UserError(
                    "Record the signed contract or purchase order reference on "
                    "'%s' before asking for it to be verified." % lead.name
                )
            if lead.contract_verified:
                raise UserError("The contract on '%s' is already verified." % lead.name)
        return self.action_request_approval(justification=justification)

    def action_verify_contract(self):
        """The approver's decision, run by the M63 engine from their inbox."""
        self._approval_assert_routed()
        for lead in self:
            if lead.contract_verified:
                raise UserError("The contract on '%s' is already verified." % lead.name)
            if not (lead.contract_ref or "").strip():
                raise UserError("'%s' has no contract or PO reference to verify." % lead.name)
            # The group the request was routed to: a matrix row's group when
            # the business has ruled one, else the sales managers.
            group = lead._approval_group_for(lead._approval_rule(), False)
            authority = lead._approval_authority_user()
            if group and not (self.env.su or authority in group.sudo().all_user_ids):
                raise UserError(
                    "Verifying a customer contract needs %s authority." % group.display_name
                )
            acting = lead._approval_acting_users()
            if not self.env.su and (lead.user_id in acting or lead.create_uid in acting):
                raise UserError(
                    "Segregation of duties: the seller or the person who raised "
                    "'%s' cannot verify its contract." % lead.name
                )
            lead._guarded().write(
                {
                    "contract_verified": True,
                    "rate_card_approved": True,
                    "contract_verified_by": self.env.user.id,
                    "contract_verified_at": fields.Datetime.now(),
                }
            )
            lead.message_post(
                body="Contract / PO %s verified against the approved rate card by %s."
                % (lead.contract_ref, self.env.user.name)
            )
        return True

    def _approval_on_rejected(self, comment):
        for lead in self:
            lead.message_post(
                body="Contract verification refused: %s" % (comment or "no reason given")
            )

    def _void_contract_verification(self, reason: str) -> None:
        """A changed contract reference is a different contract (G-M07-1)."""
        for lead in self:
            if lead.approval_state in ("pending", "approved"):
                lead._approval_void(reason)
            if lead.contract_verified or lead.rate_card_approved:
                lead._guarded().write(
                    {
                        "contract_verified": False,
                        "rate_card_approved": False,
                        "contract_verified_by": False,
                        "contract_verified_at": False,
                    }
                )
                lead.message_post(body="Contract verification withdrawn: %s" % reason)

    # ------------------------------------------------------------------
    # Gates
    # ------------------------------------------------------------------
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
        # A03 audit W5 (M33-3): the draft-party switch (no-op under 'allow').
        if partner and hasattr(partner, "_fix_assert_party_usable_downstream"):
            partner._fix_assert_party_usable_downstream("a won opportunity")
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
        # A03 P2 (SAP Sales Cloud V2): an approved quote is a precondition of
        # the order. A record created already won has no estimate yet.
        if lead:
            lead._check_quote_gate()
        elif self._quote_gate_enabled():
            raise ValidationError(
                "An opportunity cannot be created already won: raise its estimate, "
                "have it approved, then mark the deal Won."
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

    def _gating_pipeline(self, moved_pipeline=None):
        """The pipeline whose stage rules gate this lead.

        A lead with no pipeline used to be gated by nothing, and most leads
        have none, so BRU-CRM-03 was inert (A03 audit G-M07-11). They fall
        back to the shipped standard pipeline."""
        self.ensure_one()
        return (
            moved_pipeline
            or self.pipeline_id
            or self.env.ref("cd_crm_ext.pipeline_standard", raise_if_not_found=False)
            or self.env["fix.pipeline"]
        )

    def _check_stage_entry(self, stage, pipeline, confirmed: bool) -> None:
        entry = pipeline.stage_rules().get(stage.name) if (pipeline and stage) else None
        if entry and entry.get("requires_confirmation") and not confirmed:
            raise ValidationError(
                "Stage '%s' requires its entry criteria confirmed before "
                "advancing (BRU-CRM-03: %s)"
                % (stage.name, entry.get("criteria") or "criteria not met")
            )

    def _is_decided_won(self) -> bool:
        self.ensure_one()
        return bool(getattr(self.stage_id, "is_won", False) or self.probability == 100)

    def _check_loss_analysis(self, vals) -> None:
        """FLAW-07.2 / BRU-CRM-05: a lost opportunity names the competitor and
        a structured reason, whichever path loses it."""
        for lead in self:
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

    # ------------------------------------------------------------------
    # ORM
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        # A03 audit G-M07-3: without model_create_multi a batch create (an
        # import, a list create) crashed before reaching the gate.
        vals_list = [dict(vals or {}) for vals in vals_list]
        default_type = self.env.context.get("default_type")
        for vals in vals_list:
            if vals.get("type", default_type) in (False, None, "opportunity"):
                self._check_won_gate(vals)
            if vals.get("stage_id"):
                stage = self.env["crm.stage"].browse(vals["stage_id"]).exists()
                pipeline = self.env["fix.pipeline"].browse(vals.get("pipeline_id")).exists()
                pipeline = pipeline or self.env.ref(
                    "cd_crm_ext.pipeline_standard", raise_if_not_found=False
                )
                if stage and not getattr(stage, "is_won", False):
                    self._check_stage_entry(stage, pipeline, bool(vals.get("criteria_confirmed")))
        return super().create(vals_list)

    def write(self, vals):
        if "stage_id" in vals:
            target_stage = self.env["crm.stage"].browse(vals["stage_id"]).exists()
            moved_pipeline = (
                self.env["fix.pipeline"].browse(vals["pipeline_id"]).exists()
                if vals.get("pipeline_id")
                else None
            )
            vals = dict(vals)
            for lead in self:
                if target_stage and lead.stage_id != target_stage:
                    lead._check_stage_entry(
                        target_stage,
                        lead._gating_pipeline(moved_pipeline),
                        bool(vals.get("criteria_confirmed") or lead.criteria_confirmed),
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
            self.filtered(
                lambda lead: lead.type == "opportunity" and (lead.probability or 0) > 0
            )._check_loss_analysis(vals)

        # A03 audit G-M07-2: archiving an open opportunity is losing it, and
        # skipped the loss analysis (so did probability 0.5 then archive).
        if "active" in vals and not vals["active"]:
            self.filtered(
                lambda lead: lead.active
                and lead.type == "opportunity"
                and not lead._is_decided_won()
            )._check_loss_analysis(vals)

        contract_moved = self.browse()
        if "contract_ref" in vals:
            contract_moved = self.filtered(
                lambda lead: (lead.contract_ref or "") != (vals["contract_ref"] or "")
                and (lead.contract_verified or lead.approval_state in ("pending", "approved"))
            )
        result = super().write(vals)
        if contract_moved:
            contract_moved._void_contract_verification(
                "the contract / PO reference changed; verify the new one."
            )
        return result

    # ------------------------------------------------------------------
    # Won / Lost
    # ------------------------------------------------------------------
    def action_set_lost(self, reason=None, **additional_values):
        """Lost: capture the loss analysis FIRST, then archive.

        Odoo archives before it writes the values it was given, so the
        archive-time loss check would never see them. `reason` is the P03
        prompt's value and is the structured loss reason code."""
        if reason and not additional_values.get("lost_reason_code"):
            additional_values["lost_reason_code"] = reason
        loss = {k: additional_values[k] for k in LOSS_FIELDS if k in additional_values}
        if loss:
            self.write(loss)
        return super().action_set_lost(**additional_values)

    # ------------------------------------------------------------------
    # Hand-off
    # ------------------------------------------------------------------
    def action_convert_to_service_order(self):
        """Convert a lead to a service order (T06).

        FLAW-07.1: Restrict conversion exclusively to Won stage with approved
        commercial rate card and no credit hold — for leads AND opportunities
        (an unqualified lead bypassing the gate was the original flaw). A03
        P2: and with the approved estimate the order is built on.
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
            if lead.converted_service_order_id:
                raise UserError(
                    "'%s' was already converted to service order %s."
                    % (lead.name, lead.converted_service_order_id.display_name)
                )
            quote = lead._check_quote_gate()
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
            # A03 audit W5 (M33-3): the draft-party switch (no-op under 'allow').
            if hasattr(lead.partner_id, "_fix_assert_party_usable_downstream"):
                lead.partner_id._fix_assert_party_usable_downstream("a converted service order")

            device = self.env["fix.device"].search(
                [("owner_id", "child_of", lead.partner_id.commercial_partner_id.id)],
                order="id desc",
                limit=1,
            )
            if not device:
                lead._refuse_deviceless_conversion()

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
            lead._guarded().write({"converted_service_order_id": order.id})
            # The pre-sales estimate becomes the order's estimate: the work is
            # done at the price the customer approved.
            if quote and not quote.order_id:
                quote.write({"order_id": order.id})
            if not getattr(lead.stage_id, "is_won", False):
                lead.action_set_won()
            self._emit_lead_event("lead.converted_to_order", lead, order)

    def _refuse_deviceless_conversion(self):
        """A03 audit G-M07-9: B2B prospects have no registered device, so the
        single-device repair order cannot be their hand-off."""
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id
        if partner.is_company:
            raise ValidationError(
                "Cannot convert: '%s' is a corporate account with no registered "
                "device (M17). A corporate deal is handed off as a service "
                "contract (M08 Service Contracts) under contract / PO %s, not as a "
                "single repair order. Create the contract in M08, or register the "
                "devices to be serviced in M17 and convert again."
                % (partner.name, self.contract_ref or "(none recorded)")
            )
        raise ValidationError(
            "Cannot convert: The customer has no registered device (M17). "
            "Register the customer's device first."
        )

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
