# Discount reason codes (M11 FR-PRC-030, BRU-PRC-13, KPI-C11-07).
#
# M11 capture audit, pass 2 (18 Nov 2026): the Discount Governance page
# captured a discount request with a free-text justification only. The spec
# asks for a reason code from a governed list on every discount above a
# configurable threshold (a hard block), reported by the discount leakage
# report and measured by KPI-C11-07. The list lives here, beside the discount
# approval it qualifies.
#
# Enforcement starts once the business has released its list: a request may
# not be held hostage to an empty list, so while no reason code is active the
# rule has nothing to choose from and does not block. From the first active
# code on, a request above the threshold without one is refused.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

THRESHOLD_PARAM = "cd_quotation.discount_reason_threshold_pct"
PRICING_OFFICER = "cd_rate_card.group_pricing_officer"


def _require_keeper(env, what):
    if env.su:
        return
    group = env.ref(PRICING_OFFICER, raise_if_not_found=False)
    if group and env.user.has_group(PRICING_OFFICER):
        return
    if not group and env.user.has_group("base.group_system"):
        return
    raise AccessError(
        "%s needs the Pricing Officer role (M11): the reason list is governed." % what
    )


class FixDiscountReason(models.Model):
    _name = "fix.discount.reason"
    _description = "Discount Reason Code"
    _order = "sequence, code"

    code = fields.Char(required=True, index=True)
    name = fields.Char(string="Reason", required=True)
    description = fields.Text(string="When to Use It")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    use_count = fields.Integer(string="Times Used", compute="_compute_use_count")

    _code_unique = models.Constraint(
        "UNIQUE (company_id, code)", "A reason code is unique within the company."
    )

    def _compute_use_count(self):
        Approval = self.env["fix.discount.approval"].sudo()
        for rec in self:
            rec.use_count = (
                Approval.search_count([("reason_code_id", "=", rec.id)]) if rec.id else 0
            )

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s - %s" % (rec.code or "?", rec.name or "")

    @api.model_create_multi
    def create(self, vals_list):
        _require_keeper(self.env, "Adding a discount reason code")
        for vals in vals_list:
            if vals.get("code"):
                vals["code"] = vals["code"].strip().upper()
        return super().create(vals_list)

    def write(self, vals):
        _require_keeper(self.env, "Changing a discount reason code")
        if {"code", "company_id"} & set(vals):
            used = self.filtered(lambda r: r.use_count)
            if used:
                raise UserError(
                    "Reason %s is on %d discount request(s): its code stays as it is. "
                    "Archive it and add a new one." % (used[0].code, used[0].use_count)
                )
            if vals.get("code"):
                vals = dict(vals, code=vals["code"].strip().upper())
        return super().write(vals)

    def unlink(self):
        _require_keeper(self.env, "Removing a discount reason code")
        if self.filtered(lambda r: r.use_count):
            raise UserError("A reason code that was used is archived, never deleted.")
        return super().unlink()

    @api.model
    def threshold(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(THRESHOLD_PARAM, "0")
        try:
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    @api.model
    def governed(self, company):
        """True once the company has an active reason list to choose from."""
        return bool(self.sudo().search_count([("company_id", "=", company.id)], limit=1))


class FixDiscountApprovalReason(models.Model):
    _inherit = "fix.discount.approval"

    reason_code_id = fields.Many2one(
        "fix.discount.reason",
        string="Reason Code",
        index=True,
        ondelete="restrict",
        domain="[('company_id', '=', company_id)]",
        help="From the governed list (BRU-PRC-13): required above the threshold.",
    )

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(a.state != "pending" for a in self):
            locked |= {"reason_code_id"}
        return locked

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"reason_code_id"}

    def write(self, vals):
        if "reason_code_id" in vals and not self._fix_guard_open():
            decided = self.filtered(
                lambda a: a.state != "pending"
                and a._fix_guard_differs("reason_code_id", vals["reason_code_id"], a.reason_code_id)
            )
            if decided:
                raise UserError("A decided discount request keeps the reason it was decided on.")
        return super().write(vals)

    def _check_reason_code(self):
        Reason = self.env["fix.discount.reason"]
        threshold = Reason.threshold()
        for rec in self:
            if rec.reason_code_id or (rec.discount_pct or 0.0) <= threshold + 1e-9:
                continue
            if Reason.governed(rec.company_id):
                raise UserError(
                    "A %.2f%% discount needs a reason code from the governed list "
                    "(BRU-PRC-13): choose one before asking for approval." % rec.discount_pct
                )

    def action_request_approval(self, justification=None):
        self._check_reason_code()
        return super().action_request_approval(justification=justification)
