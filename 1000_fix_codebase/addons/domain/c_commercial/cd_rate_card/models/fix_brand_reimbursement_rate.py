# M11 brand reimbursement rate card (FR-PRC-015, BRU-PRC-12, spec §10.1
# fix.brand.reimbursement.rate).
#
# M11 capture audit (2026-11-13): the spec makes M11 the OWNER of what each
# brand pays 1000FiX for warranty work ("M09 claims against it"), and the
# workspace had a "Brand Reimbursement Rates" screen, but no such record
# existed: the screen showed the claim-recovery report and nobody could record
# a brand's rate. This is that rate card: per brand and repair level, a labour
# rate and a parts markup, effective-dated and versioned. A rate is in force
# only once a Price-Book Releaser who did not author it releases it (M63),
# exactly as a discount band is; a released rate never changes - a new version
# supersedes it from its own effective date, and the old one keeps its window
# so a claim is valued at the version in force on its service date.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .pricing_roles import ROLE_OFFICER, ROLE_RELEASER, require_releaser_not_author, require_role

REPAIR_LEVELS = [
    ("l1", "Level 1 - Modular / Quick Fix"),
    ("l2", "Level 2 - Component / Soldering"),
    ("l3", "Level 3 - Chip-Level / Advanced Depot"),
]

# what the release covers: none of it changes once the rate leaves Draft
RATE_TERMS = frozenset(
    {
        "brand_id",
        "repair_level",
        "currency_id",
        "labour_rate",
        "parts_markup_pct",
        "valid_from",
        "company_id",
    }
)


class FixBrandReimbursementRate(models.Model):
    _name = "fix.brand.reimbursement.rate"
    _description = "Brand Reimbursement Rate"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "brand_id, repair_level, valid_from desc, id desc"

    _approval_domain = "pricing_brand_rate"
    _approval_apply_method = "action_approve"
    _approval_group = ROLE_RELEASER
    _approval_routed = True

    name = fields.Char(compute="_compute_name", store=True)
    brand_id = fields.Many2one(
        "fix.brand", string="Brand", required=True, index=True, ondelete="restrict"
    )
    repair_level = fields.Selection(
        REPAIR_LEVELS,
        string="Repair Level",
        required=True,
        default="l1",
        help="The workshop repair level the brand pays this rate for.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    labour_rate = fields.Monetary(
        string="Labour Rate per Job",
        currency_field="currency_id",
        required=True,
        help="What the brand pays for the labour of one warranty job at this level.",
    )
    parts_markup_pct = fields.Float(
        string="Parts Handling Markup (%)",
        default=0.0,
        help="What the brand pays on top of the cost of the parts fitted (0 when the brand "
        "supplies the parts or pays them at cost).",
    )
    valid_from = fields.Date(string="Effective From", required=True)
    valid_to = fields.Date(
        string="Effective Until",
        readonly=True,
        copy=False,
        help="Set when a later version takes over; empty while this version is the latest.",
    )
    version = fields.Integer(
        readonly=True, copy=False, help="Numbered on release, per brand and level."
    )
    circular_reference = fields.Char(
        string="Brand Circular / Agreement Ref.",
        help="The brand's rate circular or service agreement this rate comes from.",
    )
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_review", "In Review"),
            ("active", "In Force"),
            ("superseded", "Superseded"),
            ("retired", "Retired"),
        ],
        required=True,
        default="draft",
        readonly=True,
        tracking=True,
        help="Claims are valued at an In Force or Superseded rate for its window.",
    )
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", string="Released By", readonly=True, copy=False)
    approved_at = fields.Datetime(string="Released On", readonly=True, copy=False)

    _rate_bounds = models.Constraint(
        "CHECK (labour_rate > 0 AND parts_markup_pct >= 0 AND parts_markup_pct <= 100)",
        "A reimbursement rate is positive and its parts markup runs from 0 to 100%.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_by",
            "approved_by",
            "approved_at",
            "version",
            "valid_to",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= RATE_TERMS
        return locked

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | RATE_TERMS

    @api.depends("brand_id", "repair_level", "version", "valid_from")
    def _compute_name(self):
        levels = dict(REPAIR_LEVELS)
        for rec in self:
            level = (levels.get(rec.repair_level) or "").split(" - ")[0]
            tag = "v%d" % rec.version if rec.version else "draft"
            rec.name = "%s · %s · %s" % (rec.brand_id.name or "?", level or "?", tag)

    @staticmethod
    def _check_vals(vals):
        if "labour_rate" in vals and (vals["labour_rate"] or 0.0) <= 0:
            raise ValidationError("A reimbursement labour rate must be positive.")
        pct = vals.get("parts_markup_pct")
        if pct is not None and not 0.0 <= pct <= 100.0:
            raise ValidationError("The parts markup runs from 0 to 100%.")

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Recording a brand reimbursement rate")
        for vals in vals_list:
            self._check_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER,), "Changing a brand reimbursement rate")
            touched = RATE_TERMS & set(vals)
            for rec in self:
                if rec.state == "draft" or not touched:
                    continue
                moved = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
                if moved:
                    raise UserError(
                        "%s is %s: its rate cannot change any more (BRU-PRC-12). Record a new "
                        "version with its own effective date instead."
                        % (rec.display_name, dict(rec._fields["state"].selection)[rec.state])
                    )
            self._check_vals(vals)
        return super().write(vals)

    # ------------------------------------------------------------------ lifecycle
    def _later_in_force(self):
        """A released version of the same brand and level that starts on or
        after this one: releasing this one would rewrite that history."""
        self.ensure_one()
        return self.search(
            [
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("brand_id", "=", self.brand_id.id),
                ("repair_level", "=", self.repair_level),
                ("state", "in", ("active", "superseded", "retired")),
                ("valid_from", ">=", self.valid_from),
            ],
            limit=1,
        )

    def action_request_approval(self, justification=None):
        require_role(self.env, (ROLE_OFFICER,), "Submitting a brand reimbursement rate")
        for rec in self:
            resubmit = rec.state == "in_review" and rec.approval_state in ("none", "returned")
            if rec.state != "draft" and not resubmit:
                raise UserError("Only a Draft reimbursement rate is submitted for release.")
            clash = rec._later_in_force()
            if clash:
                raise UserError(
                    "%s already prices this brand and level from %s; a new version starts "
                    "after it." % (clash.display_name, clash.valid_from)
                )
            rec._guarded().write({"state": "in_review", "submitted_by": self.env.uid})
        return super().action_request_approval(justification=justification)

    def action_submit(self):
        return self.action_request_approval()

    def action_approve(self):
        """Release: this version is in force from its effective date; the one
        it follows keeps its window up to the day before (BRU-PRC-12)."""
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Only a reimbursement rate In Review is released.")
            require_releaser_not_author(
                self.env,
                authority,
                acting,
                rec,
                rec.create_uid | rec.submitted_by,
                "Releasing a brand reimbursement rate",
            )
            clash = rec._later_in_force()
            if clash:
                raise UserError(
                    "%s already prices this brand and level from %s."
                    % (clash.display_name, clash.valid_from)
                )
            siblings = self.search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("brand_id", "=", rec.brand_id.id),
                    ("repair_level", "=", rec.repair_level),
                    ("state", "in", ("active", "superseded", "retired")),
                ]
            )
            previous = siblings.filtered(lambda r: r.state == "active")
            if previous:
                previous._guarded().write(
                    {"state": "superseded", "valid_to": rec.valid_from - timedelta(days=1)}
                )
            rec._guarded().write(
                {
                    "state": "active",
                    "version": max(siblings.mapped("version") or [0]) + 1,
                    "approved_by": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def _approval_on_rejected(self, comment):
        self.filtered(lambda r: r.state == "in_review")._guarded().write({"state": "draft"})
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "in_review")._guarded().write({"state": "draft"})
        return result

    def action_retire(self, reason=None):
        """The brand stopped paying this rate (agreement ended): it prices no
        claim with a service date after today. History stays."""
        require_role(
            self.env,
            (ROLE_RELEASER,),
            "Retiring a brand reimbursement rate",
            role="Price-Book Releaser",
        )
        if not (reason or "").strip():
            raise UserError("State why the brand rate is retired.")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "active":
                raise UserError("Only a rate in force is retired.")
            rec._guarded().write({"state": "retired", "valid_to": max(today, rec.valid_from)})
            rec.message_post(body="Retired: %s" % reason.strip())
        return True

    # ------------------------------------------------------------------ consumers
    @api.model
    def rate_for(self, brand, repair_level="l1", on_date=None, company=None):
        """The released rate a warranty job of `brand` at `repair_level` is
        reimbursed at on `on_date` (BRU-PRC-12: the version in force on the
        service date, superseded or not). Empty when the brand has none."""
        if not brand:
            return self.browse()
        day = on_date or fields.Date.context_today(self)
        company = company or self.env.company
        return self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("brand_id", "=", brand.id),
                ("repair_level", "=", repair_level),
                ("state", "in", ("active", "superseded", "retired")),
                ("valid_from", "<=", day),
                "|",
                ("valid_to", "=", False),
                ("valid_to", ">=", day),
            ],
            order="valid_from desc, id desc",
            limit=1,
        )

    def reimbursement_for(self, parts_cost=0.0):
        """What the brand owes for one job at this rate: labour plus parts at
        cost plus the markup, rounded once to the paisa."""
        self.ensure_one()
        parts = float(parts_cost or 0.0)
        return round(self.labour_rate + parts * (1.0 + (self.parts_markup_pct or 0.0) / 100.0), 2)
