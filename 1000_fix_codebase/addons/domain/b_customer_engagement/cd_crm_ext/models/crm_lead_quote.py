# Opportunity -> estimate hand-off: "an approved quote before the order".
#
# A03 audit G-M07-9 / §4.1 step 5: nothing linked a CRM opportunity to the
# estimate it was sold on, so a deal was won and converted with no approved
# price behind it, and a 40% discount whose only approval was REJECTED was
# quoted and accepted (G-M36-2). SAP Sales Cloud V2 makes an approved sales
# quote a precondition of the sales order and limits edits while the quote is
# in approval. This does the same on the estate's single estimate concept
# (AS-01: fix.estimate, owned by cd_service_order and quoted by M36):
#
#   * an opportunity raises its estimate, or links an existing one;
#   * Won and the service-order conversion refuse unless the LATEST linked
#     estimate is approved, its DOFA discount approval still covers it, no
#     discount request is pending or was last rejected, and it has not been
#     edited upwards since it was approved;
#   * while the estimate's discount approval is pending, the M63 engine
#     voids the request on any change to the discount (its void-on-change),
#     so an edit cannot ride an approval that did not see it.
#
# A pre-sales estimate has no service order yet (the order is what the won
# deal converts INTO), so `order_id` is optional here when the estimate
# belongs to an opportunity; conversion then moves it onto the new order.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext

# ir.config_parameter switch. "1" (default) = Won and conversion require an
# approved linked estimate. "0" restores the pre-P2 behaviour. Business
# decision: whether some opportunity types (e.g. a walk-in B2C repair) may
# be won without a pre-sales estimate.
QUOTE_GATE_PARAM = "cd_crm_ext.won_requires_approved_estimate"


class FixEstimateCrm(models.Model):
    """The estimate side of the link."""

    _inherit = "fix.estimate"

    lead_id = fields.Many2one(
        "crm.lead",
        string="Opportunity",
        index=True,
        ondelete="set null",
        tracking=True,
        help="The CRM opportunity this estimate quotes. A revision keeps the link.",
    )
    # A pre-sales estimate quotes a deal before any service order exists.
    order_id = fields.Many2one(required=False)
    approved_total = fields.Monetary(
        string="Total When Approved",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The grand total the approver signed off. An estimate edited above "
        "it no longer counts as approved for a CRM Won or conversion.",
    )
    approval_stamped_at = fields.Datetime(
        string="Approval Recorded On",
        readonly=True,
        copy=False,
        help="Set only by the estimate's Approve action.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"approved_total", "approval_stamped_at"}

    @api.constrains("order_id", "lead_id")
    def _check_estimate_owner(self):
        for est in self:
            if not est.order_id and not est.lead_id:
                raise ValidationError(
                    "An estimate belongs to a service order or to a CRM opportunity."
                )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            for vals in vals_list:
                if vals.get("lead_id") and vals.get("state") == "approved":
                    raise UserError(
                        "An opportunity's estimate is approved through its Approve "
                        "action, not created approved."
                    )
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            # The CRM gate trusts `state == approved` on a linked estimate, so
            # only the Approve action may put it there.
            if vals.get("state") == "approved" and self.filtered("lead_id"):
                raise UserError(
                    "An opportunity's estimate is approved through its Approve "
                    "action, which applies the customer, manager and DOFA checks."
                )
            if "lead_id" in vals:
                moved = self.filtered(
                    lambda e: e.lead_id
                    and e.lead_id.id != (vals["lead_id"] or False)
                    and e.state == "approved"
                )
                if moved:
                    raise UserError(
                        "An approved estimate stays with the opportunity it was "
                        "approved for. Revise it to quote another deal."
                    )
            if (
                vals.get("lead_id")
                and "state" not in vals
                and self.filtered(lambda e: e.state == "approved" and not e.approval_stamped_at)
            ):
                raise UserError(
                    "This estimate was approved before its approval could be "
                    "recorded. Revise it and approve the revision to quote an "
                    "opportunity with it."
                )
        return super().write(vals)

    def action_approve(self):
        # The A02 approve method writes state itself; the token lets that
        # write through the linked-estimate guard above.
        result = super(FixEstimateCrm, self._guarded()).action_approve()
        for est in self.filtered(lambda e: e.state == "approved"):
            est._guarded().write(
                {"approved_total": est.grand_total, "approval_stamped_at": fields.Datetime.now()}
            )
        return result


class CrmLeadQuote(models.Model):
    """The opportunity side: raise, link, and gate on the approved estimate."""

    _inherit = "crm.lead"

    estimate_ids = fields.One2many("fix.estimate", "lead_id", string="Estimates / Quotes")
    quote_estimate_id = fields.Many2one(
        "fix.estimate",
        string="Current Estimate",
        compute="_compute_quote",
        help="The latest linked estimate (highest version). Won and conversion read this one.",
    )
    quote_status = fields.Char(string="Quote Status", compute="_compute_quote")

    @api.depends(
        "estimate_ids",
        "estimate_ids.state",
        "estimate_ids.version",
        "estimate_ids.grand_total",
        "estimate_ids.approval_state",
    )
    def _compute_quote(self):
        for lead in self:
            quote = lead._quote_latest()
            lead.quote_estimate_id = quote
            if not quote:
                lead.quote_status = "No estimate raised"
                continue
            blockers = lead._quote_blockers(quote)
            lead.quote_status = (
                "Approved: %s, BDT %.2f" % (lead._quote_label(quote), quote.grand_total)
                if not blockers
                else "Not cleared: %s" % blockers[0]
            )

    # ---- helpers --------------------------------------------------------
    @api.model
    def _quote_gate_enabled(self) -> bool:
        value = self.env["ir.config_parameter"].sudo().get_param(QUOTE_GATE_PARAM, "1")
        return str(value).strip().lower() not in ("0", "false", "no", "off")

    @staticmethod
    def _quote_label(estimate) -> str:
        return "estimate #%d v%d" % (estimate.id, estimate.version)

    def _quote_latest(self):
        self.ensure_one()
        return self.estimate_ids.sorted(lambda e: (e.version, e.id), reverse=True)[:1]

    def _quote_blockers(self, estimate) -> list:
        """Why `estimate` does not yet clear this deal. Empty = cleared."""
        label = self._quote_label(estimate)
        if estimate.state != "approved":
            return [
                "%s is %s; it must be approved."
                % (label, dict(estimate._fields["state"].selection).get(estimate.state))
            ]
        blockers = []
        if not estimate.approval_stamped_at:
            blockers.append(
                "%s carries no record of its approval; revise it and approve the revision." % label
            )
        if estimate.approved_total and estimate.grand_total > estimate.approved_total + 0.005:
            blockers.append(
                "%s was approved at BDT %.2f but now totals BDT %.2f; revise it and "
                "have the revision approved."
                % (label, estimate.approved_total, estimate.grand_total)
            )
        if estimate.approval_state == "pending":
            blockers.append("%s has a discount approval still pending." % label)
        try:
            estimate._dofa_assert_approved("The discount on %s" % label)
        except ValidationError as exc:
            blockers.append(str(exc.args[0] if exc.args else exc))
        # M36 discount requests (cd_quotation), read softly: this module does
        # not depend on it.
        if "approval_ids" in estimate._fields:
            requests = estimate.approval_ids.sorted("id")
            if requests.filtered(lambda a: a.state == "pending"):
                blockers.append("%s has a discount request still pending." % label)
            elif requests and requests[-1].state == "rejected":
                blockers.append(
                    "The last discount request on %s was rejected; quote a discount "
                    "that was approved." % label
                )
        if getattr(estimate, "quotation_state", False) == "declined":
            blockers.append("The customer declined %s." % label)
        return blockers

    def _check_quote_gate(self):
        """Raise unless the latest linked estimate clears the deal. Returns it."""
        self.ensure_one()
        if not self._quote_gate_enabled():
            return self._quote_latest()
        quote = self._quote_latest()
        if not quote:
            raise ValidationError(
                "'%s' has no estimate. Raise or link the estimate the customer is "
                "buying on and have it approved before the deal is won or "
                "converted (approved quote before order)." % self.name
            )
        blockers = self._quote_blockers(quote)
        if blockers:
            raise ValidationError(
                "'%s' cannot be won or converted yet: %s" % (self.name, " ".join(blockers))
            )
        return quote

    # ---- user actions ----------------------------------------------------
    def action_raise_estimate(self):
        """Open the pre-sales estimate for this opportunity (one draft at a time)."""
        self.ensure_one()
        if not self.partner_id:
            raise UserError(
                "Link the customer party to '%s' before raising its estimate." % self.name
            )
        draft = self.estimate_ids.filtered(lambda e: e.state == "draft")[:1]
        if draft:
            return {
                "estimate_id": draft.id,
                "note": "%s is already open as a draft." % self._quote_label(draft),
            }
        estimate = self.env["fix.estimate"].create(
            {
                "lead_id": self.id,
                "company_id": (self.company_id or self.env.company).id,
                "diagnostic_notes": html2plaintext(self.description or "").strip() or False,
            }
        )
        self.message_post(
            body="%s raised for this opportunity. Add its lines in M36 Quotations, "
            "then send and approve it." % self._quote_label(estimate)
        )
        return {"estimate_id": estimate.id, "note": "Add the lines in M36 Quotations."}

    def action_link_estimate(self, estimate=None):
        """Link an existing estimate (by its number) to this opportunity."""
        self.ensure_one()
        digits = "".join(ch for ch in str(estimate or "") if ch.isdigit())
        found = self.env["fix.estimate"].browse(int(digits)).exists() if digits else None
        if not found:
            raise UserError("Give the number of an existing estimate to link.")
        if found.lead_id == self:
            return {"estimate_id": found.id, "note": "Already linked."}
        if found.lead_id:
            raise UserError(
                "%s already quotes '%s'." % (self._quote_label(found), found.lead_id.name)
            )
        customer = found.order_id.customer_id.commercial_partner_id
        if customer and self.partner_id and customer != self.partner_id.commercial_partner_id:
            raise UserError(
                "%s is for %s, not for this opportunity's customer %s."
                % (self._quote_label(found), customer.name, self.partner_id.name)
            )
        found.write({"lead_id": self.id})
        self.message_post(body="%s linked to this opportunity." % self._quote_label(found))
        return {"estimate_id": found.id}
