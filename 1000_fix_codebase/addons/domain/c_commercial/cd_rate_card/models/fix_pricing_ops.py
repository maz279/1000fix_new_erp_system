# M11 pricing operations: price books and versions, price floors, promotions
# and simulation requests. Rate cards, dynamic rules, price explanations and
# discount approvals already live in cd_rate_card / cd_dynamic_pricing.
#
# A04 audit (2026-11-04) M11-1..M11-11: every object here was data with no
# lifecycle. A clerk activated his own unapproved version with a future date,
# ticked the below-floor override flag, lowered the floor itself, created a
# 150% promotion and typed a simulation result. Each now has a lifecycle whose
# state fields only its transitions write (fix.guarded.mixin), its releases
# are decided by someone other than the author through the M63 approval
# engine, and the Pricing Officer / Price-Book Releaser roles do the work.
import json

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .pricing_roles import (
    DEFAULT_DISCOUNT_LADDER,
    ROLE_OFFICER,
    ROLE_RELEASER,
    has_role,
    require_releaser_not_author,
    require_role,
)

DOFA_TIERS = [
    ("tier_0", "Tier 0 — No Approval Required"),
    ("tier_1", "Tier 1 — Team Lead / Supervisor"),
    ("tier_2", "Tier 2 — Branch / Operations Manager"),
    ("tier_3", "Tier 3 — CX / Commercial Director"),
    ("tier_4", "Tier 4 — CFO / CCO / COO"),
    ("tier_5", "Tier 5 — Managing Director / Board"),
]
DOFA_TIER_GROUP = {
    "tier_1": "cd_entity_config.group_dofa_tier_1",
    "tier_2": "cd_entity_config.group_dofa_tier_2",
    "tier_3": "cd_entity_config.group_dofa_tier_3",
    "tier_4": "cd_entity_config.group_dofa_tier_4",
    "tier_5": "cd_entity_config.group_dofa_tier_5",
}


class FixApprovalMatrixPricing(models.Model):
    """M11 / M37 decision domains on the DoA register (A04 audit 2026-11-04)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("pricing_version", "Price-Book Version Release"),
            ("pricing_change", "Rate / Floor Change"),
            ("pricing_promotion", "Promotion Release"),
            ("pricing_floor_override", "Below-Floor Price Override"),
            ("pricing_discount_policy", "Discount Band Release"),
            ("catalogue_item", "Catalogue Item Activation"),
            ("catalogue_brand_authorisation", "Brand Authorisation"),
        ],
        ondelete=dict.fromkeys(
            (
                "pricing_version",
                "pricing_change",
                "pricing_promotion",
                "pricing_floor_override",
                "pricing_discount_policy",
                "catalogue_item",
                "catalogue_brand_authorisation",
            ),
            "cascade",
        ),
    )


def _officer_write_check(records, vals, what, frozen=frozenset(), open_states=("draft",)):
    """Shared write rule: outside a transition only a Pricing Officer edits,
    and a record that left its open state keeps the fields it was released
    with (its approval covers them)."""
    if records._fix_guard_open():
        return
    require_role(records.env, (ROLE_OFFICER,), what)
    touched = frozen & set(vals)
    if not touched:
        return
    for rec in records:
        if rec.state in open_states:
            continue
        moved = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
        if moved:
            raise UserError(
                "%s is %s: %s cannot change any more; its release covered them. "
                "Author a new one instead."
                % (
                    rec.display_name,
                    dict(rec._fields["state"].selection).get(rec.state),
                    ", ".join(sorted(rec._fields[n].string or n for n in moved)),
                )
            )


class FixPriceBook(models.Model):
    _name = "fix.price.book"
    _description = "Price Book"
    _inherit = ["fix.guarded.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # A04 audit M11-1 (pb_01): a book went Active with only a draft version.
    # It now goes Active when its first released version activates, and is
    # retired by a releaser; the state is never typed.
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
        readonly=True,
    )
    active = fields.Boolean(default=True)
    active_version_id = fields.Many2one(
        "fix.price.version", compute="_compute_active_version", string="Version in Force"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    def _compute_active_version(self):
        Version = self.env["fix.price.version"]
        for book in self:
            book.active_version_id = Version.search(
                [("book_id", "=", book.id), ("state", "=", "active")], limit=1
            )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Creating a price book")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER,), "Changing a price book")
            if "code" in vals and any(b.state != "draft" for b in self):
                raise UserError("A price book's code is fixed once a version of it is live.")
        return super().write(vals)

    def action_retire(self, reason=None):
        """Active -> Retired (releaser): its version in force is superseded."""
        require_role(
            self.env, (ROLE_RELEASER,), "Retiring a price book", role="Price-Book Releaser"
        )
        now = fields.Datetime.now()
        for book in self:
            if book.state != "active":
                raise UserError("Only an Active price book is retired.")
            live = self.env["fix.price.version"].search(
                [("book_id", "=", book.id), ("state", "in", ("active", "approved"))]
            )
            live._guarded().write({"state": "superseded", "superseded_at": now})
            book._guarded().write({"state": "retired"})
            for v in live:
                v.message_post(
                    body="Superseded: price book retired by %s%s."
                    % (self.env.user.name, ": %s" % reason if reason else "")
                )
        return True


VERSION_STATES = [
    ("draft", "Draft"),
    ("in_review", "In Review"),
    ("approved", "Approved (awaiting effective date)"),
    ("active", "Active"),
    ("superseded", "Superseded"),
]
VERSION_FROZEN = frozenset({"name", "book_id", "version", "effective_from"})


class FixPriceVersion(models.Model):
    """Spec §8.1: Draft -> In Review -> Approved -> Active -> Superseded.

    A04 audit M11-1 (pv_01..pv_07): state and approved_by were free fields.
    The author submits; a Price-Book Releaser who is neither the author nor
    the submitter approves from the M63 inbox; the version activates on its
    effective date (Dhaka) and supersedes the one in force. One active
    version per book; never an active version dated in the future."""

    _name = "fix.price.version"
    _description = "Price Book Version"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "book_id, effective_from desc"

    _approval_domain = "pricing_version"
    _approval_apply_method = "action_approve"
    _approval_group = ROLE_RELEASER
    _approval_routed = True

    name = fields.Char(required=True)
    book_id = fields.Many2one("fix.price.book", required=True, ondelete="restrict", index=True)
    version = fields.Char(required=True)
    effective_from = fields.Date(required=True)
    state = fields.Selection(VERSION_STATES, required=True, default="draft", readonly=True)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)
    submitted_at = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Text(readonly=True, copy=False)
    activated_at = fields.Datetime(readonly=True, copy=False)
    superseded_at = fields.Datetime(readonly=True, copy=False)
    superseded_by_id = fields.Many2one("fix.price.version", readonly=True, copy=False)
    note = fields.Char()

    _one_active_per_book = models.UniqueIndex(
        "(book_id) WHERE state = 'active'",
        "A price book has one active version at a time.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by",
            "approved_at",
            "submitted_by",
            "submitted_at",
            "rejection_reason",
            "activated_at",
            "superseded_at",
            "superseded_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= VERSION_FROZEN
        return locked

    @api.constrains("state", "effective_from")
    def _check_active_dating(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state == "active" and rec.effective_from and rec.effective_from > today:
                raise ValidationError(
                    "Version %s is dated %s: a version is never active before its "
                    "effective date." % (rec.display_name, rec.effective_from)
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Authoring a price-book version")
        return super().create(vals_list)

    def write(self, vals):
        _officer_write_check(self, vals, "Changing a price-book version", VERSION_FROZEN)
        return super().write(vals)

    # ---- lifecycle ----------------------------------------------------------
    def action_request_approval(self, justification=None):
        """Draft -> In Review, routed to a Price-Book Releaser."""
        require_role(self.env, (ROLE_OFFICER,), "Submitting a price-book version")
        now = fields.Datetime.now()
        for rec in self:
            resubmit = rec.state == "in_review" and rec.approval_state in ("none", "returned")
            if rec.state != "draft" and not resubmit:
                raise UserError("Only a Draft version is submitted for release.")
            if rec.book_id.state == "retired":
                raise UserError("%s is retired; it takes no new version." % rec.book_id.name)
            rec._guarded().write(
                {
                    "state": "in_review",
                    "submitted_by": self.env.uid,
                    "submitted_at": now,
                    "rejection_reason": False,
                }
            )
        return super().action_request_approval(justification=justification)

    def action_submit(self):
        return self.action_request_approval()

    def action_approve(self):
        """In Review -> Approved (then Active when its date has come). From the
        approver's M63 inbox only."""
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Only a version In Review is approved.")
            require_releaser_not_author(
                self.env,
                authority,
                acting,
                rec,
                rec.create_uid | rec.submitted_by,
                "Releasing a price-book version",
            )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Released by %s." % self.env.user.name)
            if rec.effective_from <= today:
                rec._activate()
        return True

    def _approval_on_rejected(self, comment):
        for rec in self.filtered(lambda r: r.state == "in_review"):
            rec._guarded().write({"state": "draft", "rejection_reason": comment or False})
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "in_review")._guarded().write({"state": "draft"})
        return result

    def _activate(self):
        """Approved -> Active; the version in force on the book is superseded.
        System transition (approval on or after the date, or the daily job)."""
        now = fields.Datetime.now()
        for rec in self.sorted(lambda v: (v.effective_from, v.id)):
            if rec.state != "approved":
                continue
            current = self.search(
                [("book_id", "=", rec.book_id.id), ("state", "=", "active"), ("id", "!=", rec.id)]
            )
            if current:
                current._guarded().write(
                    {"state": "superseded", "superseded_at": now, "superseded_by_id": rec.id}
                )
                # the one-active index is not deferrable: the old version
                # leaves Active before the new one enters it
                current.flush_recordset(["state"])
            rec._guarded().write({"state": "active", "activated_at": now})
            if rec.book_id.state == "draft":
                rec.book_id._guarded().write({"state": "active"})
            rec.message_post(body="Active from %s." % rec.effective_from)
            publish(
                self.env,
                "pricing.book_activated",
                "fix.price.version",
                rec.id,
                {
                    "book_id": rec.book_id.id,
                    "book_code": rec.book_id.code,
                    "version": rec.version,
                    "effective_from": fields.Date.to_string(rec.effective_from),
                    "approved_by_id": rec.approved_by.id or None,
                    "superseded_ids": current.ids,
                },
            )

    @api.model
    def cron_activate_due_versions(self):
        """AUT-PRC-07: activate each book's latest approved version whose date
        has come (Dhaka date). An approved version overtaken by a later one
        before it ever went live is superseded without activating.
        Idempotent."""
        today = fields.Date.context_today(self)
        due = self.search(
            [("state", "=", "approved"), ("effective_from", "<=", today)],
            order="effective_from, id",
        )
        now = fields.Datetime.now()
        done = self.browse()
        for book in due.mapped("book_id"):
            mine = due.filtered(lambda v, b=book: v.book_id == b)
            latest = mine[-1]
            skipped = mine - latest
            if skipped:
                skipped._guarded().write(
                    {"state": "superseded", "superseded_at": now, "superseded_by_id": latest.id}
                )
            latest._activate()
            done |= latest
        return len(done)


class FixPriceFloor(models.Model):
    _name = "fix.price.floor"
    _description = "Price Floor"
    _inherit = ["fix.dofa.mixin"]
    _order = "name"

    # A below-floor sale is a concession, so it carries the same authority the
    # rest of the estate uses: the tier follows the size of the discount, the
    # approver must hold it, and the person who raised it cannot clear it.
    # The first implementation stamped env.user with no check at all
    # (A04 audit, 2026-10-31).
    # The spec (BRU-PRC-04) asks for a CCO-level approval for EVERY
    # below-floor price; this ladder is the estate's, kept until the business
    # rules on floor-override authority per tier (report §7 item 7).
    _DOFA_DISCOUNT_THRESHOLDS = [
        (15.0, "tier_2"),  # up to 15% below floor
        (30.0, "tier_3"),  # up to 30% below floor
        (float("inf"), "tier_4"),
    ]
    # A04 audit (2026-11-04) M11-2/M11-3: the override is a routed DOFA
    # approval (M63 inbox), and the floor gate reads the DOFA stamp, which the
    # mixin pins to the depth that was approved.
    _approval_domain = "pricing_floor_override"
    _approval_apply_method = "action_approve_dofa_override"
    _approval_routed = True

    # A11 audit P2 (A04 area): the override used to be cleared by whoever
    # pressed Approve while holding the tier — no request, no named approver,
    # no deadline, no delegate, no history. It is now a routed M63 request:
    # the raiser asks (action_request_override_approval), the engine routes to
    # the holders of the tier the shortfall derives (minus the raiser and the
    # amount-changer), and the flags are stamped from the approver's inbox
    # only. The shortfall percentage is the approval amount, so moving the
    # floor or the proposed price while the request is pending withdraws it.
    _approval_domain = "price_floor_override"
    _approval_apply_method = "action_approve_dofa_override"
    _approval_routed = True

    name = fields.Char(required=True)
    product_code = fields.Char(required=True, index=True)
    catalogue_item_id = fields.Many2one("fix.catalogue.item", string="Catalogue Item")
    book_id = fields.Many2one("fix.price.book", string="Price Book")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    floor_price = fields.Monetary(
        required=True,
        help="The minimum sellable price. Set when the floor is created; changed only "
        "by an approved price change (fix.price.change).",
    )
    active = fields.Boolean(default=True)

    # A04 audit M11-8 (pf_09): dofa_tier was a free Selection ("Tier 1 <15%")
    # that disagreed with the tier actually enforced. It now shows that tier.
    dofa_tier = fields.Selection(
        [(t.replace("_", ""), label) for t, label in DOFA_TIERS],
        string="Required DOFA Tier for Floor Override",
        compute="_compute_dofa_override",
    )
    # A04 audit M11-2 (pf_01): the bespoke override flag was writable and the
    # gate trusted it. Both now derive from the DOFA stamp.
    dofa_override_approved = fields.Boolean(
        string="DOFA Override Approved", compute="_compute_dofa_override"
    )
    dofa_override_user_id = fields.Many2one(
        "res.users", string="DOFA Override Approver", compute="_compute_dofa_override"
    )

    proposed_override_price = fields.Monetary(
        string="Proposed Below-Floor Price",
        help="The price the override is being sought for. The DOFA tier is "
        "derived from how far below the floor it sits.",
    )
    # staging for a floor change; the change itself is a fix.price.change
    proposed_floor_price = fields.Monetary(string="Proposed New Floor", copy=False)
    floor_change_reason = fields.Text(string="Floor Change Reason", copy=False)

    # Fields an internal user may write to ask for an override.
    _REQUEST_FIELDS = frozenset({"proposed_override_price", "dofa_justification"})

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "dofa_override_approved",
            "dofa_override_user_id",
            "dofa_tier",
        }
        if self:
            # A04 audit M11-5 (pf_08): the floor is the control; it changes
            # only through an approved price change.
            guarded |= {"floor_price", "product_code", "catalogue_item_id", "active"}
        return guarded

    @api.depends("floor_price", "proposed_override_price", "dofa_approved", "dofa_approved_by")
    def _compute_dofa_override(self):
        for rec in self:
            rec.dofa_tier = rec._dofa_current_tier().replace("_", "")
            rec.dofa_override_approved = bool(rec.dofa_approved and rec.proposed_override_price)
            rec.dofa_override_user_id = rec.dofa_approved_by if rec.dofa_approved else False

    def _dofa_amount(self) -> float:
        """Percentage below floor — the measure the tier is derived from."""
        self.ensure_one()
        if not self.floor_price or not self.proposed_override_price:
            return 0.0
        shortfall = self.floor_price - self.proposed_override_price
        if shortfall <= 0:
            return 0.0
        return (shortfall / self.floor_price) * 100.0

    def _dofa_thresholds(self):
        return self._DOFA_DISCOUNT_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "a price %.1f%% below the floor for '%s'" % (
            self._dofa_amount(),
            self.product_code,
        )

    @api.depends("floor_price", "proposed_override_price")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Setting a price floor")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open() and set(vals) - self._REQUEST_FIELDS:
            require_role(self.env, (ROLE_OFFICER,), "Changing a price floor")
        return super().write(vals)

    def _floor_precheck(self):
        """The authority and segregation checks, before the routing check, so
        a refusal names its real cause."""
        for rec in self:
            tier = rec._dofa_current_tier()
            group = DOFA_TIER_GROUP.get(tier)
            if group and not rec._dofa_authority_user().has_group(group):
                raise UserError(
                    "DOFA authority insufficient: %s requires %s. You do not hold that "
                    "approval authority." % (rec._dofa_amount_label(), dict(DOFA_TIERS)[tier])
                )
            if rec.create_uid and rec.create_uid in rec._dofa_acting_users():
                raise UserError(
                    "Segregation of duties: %s was raised by you and must be approved by "
                    "a different %s." % (rec._dofa_amount_label(), dict(DOFA_TIERS)[tier])
                )

    def action_approve_dofa_override(self):
        """Approve a below-floor price under real DOFA authority (M63 inbox)."""
        for rec in self:
            if not rec.proposed_override_price:
                raise UserError(
                    "Record the proposed below-floor price before seeking an "
                    "override: the approval tier is derived from how far below "
                    "the floor it sits."
                )
            if not self.env.su:
                rec._floor_precheck()
            rec.action_dofa_approve()
        return True

    def _fix_guarded_fields(self) -> set:
        # The override stamps change only through the approve action.
        return super()._fix_guarded_fields() | {"dofa_override_approved", "dofa_override_user_id"}

    def validate_price_against_floor(self, proposed_price: float):
        """Statutory guard blocking transaction pricing below floor without DOFA
        approval. Reads the DOFA stamp, which covers the depth approved."""
        self.ensure_one()
        if (proposed_price or 0.0) + 0.005 >= self.floor_price:
            return True
        if not (self.dofa_approved and self.proposed_override_price):
            raise UserError(
                "Proposed price %.2f BDT is strictly below statutory price floor %.2f BDT "
                "for '%s'. DOFA Commercial Director override approval is mandatory before "
                "proceeding." % (proposed_price, self.floor_price, self.product_code)
            )
        # An override only covers the price it was granted for.
        if (proposed_price or 0.0) + 0.005 < self.proposed_override_price:
            raise UserError(
                "Proposed price %.2f BDT is below the %.2f BDT the DOFA "
                "override was granted for on '%s'. Re-approval is required."
                % (proposed_price, self.proposed_override_price, self.product_code)
            )
        self._dofa_assert_approved("A below-floor price")
        return True

    @api.model
    def _floors_for(self, product):
        """Active floors that govern `product` (by code or catalogue item)."""
        product = product.sudo()
        code = (product.default_code or "").strip()
        item = product.product_tmpl_id.catalogue_item_id[:1]
        domain = []
        if code:
            domain = [("product_code", "=", code)]
        if item:
            domain = ["|", ("catalogue_item_id", "=", item.id)] + (domain or [("id", "=", 0)])
        return self.sudo().search(domain) if domain else self.sudo().browse()

    def action_request_floor_change(self):
        """Raise a price change for the floor staged on this record."""
        require_role(self.env, (ROLE_OFFICER,), "Raising a floor change")
        Change = self.env["fix.price.change"]
        for rec in self:
            if not (rec.floor_change_reason or "").strip():
                raise UserError("State why the floor changes (FR-PRC-034).")
            change = Change.create(
                {
                    "target_type": "floor",
                    "change_type": "change",
                    "floor_id": rec.id,
                    "proposed_value": rec.proposed_floor_price,
                    "reason": rec.floor_change_reason,
                }
            )
            change.action_submit()
            rec.write({"proposed_floor_price": 0.0, "floor_change_reason": False})
        return True

    def action_request_retire(self, reason=None):
        require_role(self.env, (ROLE_OFFICER,), "Raising a floor retirement")
        if not (reason or "").strip() and not all(r.floor_change_reason for r in self):
            raise UserError("State why the floor is retired.")
        for rec in self:
            self.env["fix.price.change"].create(
                {
                    "target_type": "floor",
                    "change_type": "retire",
                    "floor_id": rec.id,
                    "reason": reason or rec.floor_change_reason,
                }
            ).action_submit()
        return True


PROMOTION_STATES = [
    ("draft", "Draft"),
    ("in_review", "In Review"),
    ("approved", "Approved (awaiting start)"),
    ("active", "Active"),
    ("ended", "Ended"),
]
PROMOTION_FROZEN = frozenset(
    {
        "code",
        "company_id",
        "discount_type",
        "value",
        "channel",
        "valid_from",
        "valid_until",
        "stackable",
        "priority",
        "budget_amount",
        "max_uses",
    }
)


class FixPromotion(models.Model):
    """A04 audit M11-6 (pr_01..pr_05): promotions had no approval, budget,
    stacking or bounds; 150% and inverted windows were accepted. Now: bounded
    value and window, a budget and usage cap consumed by the pricing path,
    stacking rules, and release by a Price-Book Releaser through M63."""

    _name = "fix.promotion"
    _description = "Promotion"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "name"

    _approval_domain = "pricing_promotion"
    _approval_apply_method = "action_approve"
    _approval_group = ROLE_RELEASER
    _approval_routed = True

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    discount_type = fields.Selection(
        [("percent", "Percentage"), ("fixed", "Fixed amount")],
        required=True,
        default="percent",
    )
    value = fields.Float(required=True)
    channel = fields.Selection(
        [
            ("all", "All channels"),
            ("portal", "Customer portal"),
            ("branch", "Branch"),
            ("corporate", "Corporate"),
        ],
        required=True,
        default="all",
    )
    valid_from = fields.Date()
    valid_until = fields.Date()
    state = fields.Selection(PROMOTION_STATES, required=True, default="draft", readonly=True)
    active = fields.Boolean(default=True)
    stackable = fields.Boolean(
        help="A stackable promotion combines with other stackable ones; an exclusive "
        "one (the default) is never combined (FR-PRC-04x)."
    )
    priority = fields.Integer(
        default=10, help="Lower runs first when exclusive promotions compete on equal value."
    )
    budget_amount = fields.Monetary(
        string="Budget (BDT)", help="Total discount this promotion may give. 0 = no budget cap."
    )
    budget_used = fields.Monetary(string="Budget Used", readonly=True, copy=False)
    max_uses = fields.Integer(string="Usage Cap", help="0 = no cap.")
    use_count = fields.Integer(string="Times Used", readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)
    rejection_reason = fields.Text(readonly=True, copy=False)
    ended_reason = fields.Char(readonly=True, copy=False)

    _value_bounds = models.Constraint(
        "CHECK (value > 0 AND (discount_type != 'percent' OR value <= 100))",
        "A promotion gives a positive discount, and a percentage of at most 100.",
    )
    _budget_not_negative = models.Constraint(
        "CHECK (COALESCE(budget_amount, 0) >= 0 AND COALESCE(max_uses, 0) >= 0)",
        "A promotion's budget and usage cap cannot be negative.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by",
            "approved_at",
            "submitted_by",
            "rejection_reason",
            "ended_reason",
            "budget_used",
            "use_count",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= PROMOTION_FROZEN
        return locked

    @staticmethod
    def _check_bound_vals(vals, current=None):
        """Before the INSERT/UPDATE, so the user gets a ValidationError and not
        the SQL CHECK's IntegrityError."""
        if "value" in vals or "discount_type" in vals:
            dtype = vals.get("discount_type") or (current.discount_type if current else "percent")
            value = vals.get("value", current.value if current else 0.0)
            if (value or 0.0) <= 0.0:
                raise ValidationError("A promotion gives a positive discount.")
            if dtype == "percent" and value > 100.0:
                raise ValidationError(
                    "A %.0f%% promotion would pay the customer to buy: at most 100%%." % value
                )
        for name in ("budget_amount", "max_uses"):
            if (vals.get(name) or 0) < 0:
                raise ValidationError("A promotion's budget and usage cap cannot be negative.")

    @api.constrains("valid_from", "valid_until")
    def _check_window(self):
        for rec in self:
            if rec.valid_from and rec.valid_until and rec.valid_until < rec.valid_from:
                raise ValidationError(
                    "Promotion %s ends (%s) before it starts (%s)."
                    % (rec.code, rec.valid_until, rec.valid_from)
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Creating a promotion")
        for vals in vals_list:
            self._check_bound_vals(dict({"value": 0.0}, **vals))
        return super().create(vals_list)

    def write(self, vals):
        _officer_write_check(self, vals, "Changing a promotion", PROMOTION_FROZEN)
        for rec in self:
            self._check_bound_vals(vals, rec)
        return super().write(vals)

    # ---- lifecycle ----------------------------------------------------------
    def action_request_approval(self, justification=None):
        require_role(self.env, (ROLE_OFFICER,), "Submitting a promotion")
        for rec in self:
            resubmit = rec.state == "in_review" and rec.approval_state in ("none", "returned")
            if rec.state != "draft" and not resubmit:
                raise UserError("Only a Draft promotion is submitted for release.")
            if not (rec.valid_from and rec.valid_until):
                raise UserError("A promotion needs its validity window before release.")
            if rec.valid_until < fields.Date.context_today(self):
                raise UserError("Promotion %s would already have ended." % rec.code)
            rec._guarded().write(
                {"state": "in_review", "submitted_by": self.env.uid, "rejection_reason": False}
            )
        return super().action_request_approval(justification=justification)

    def action_submit(self):
        return self.action_request_approval()

    def action_approve(self):
        """In Review -> Approved (Active once its window opens). From the M63
        inbox, by a releaser who did not author or submit it."""
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Only a promotion In Review is released.")
            require_releaser_not_author(
                self.env,
                authority,
                acting,
                rec,
                rec.create_uid | rec.submitted_by,
                "Releasing a promotion",
            )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
            if rec.valid_from <= today:
                rec._start()
        return True

    def _approval_on_rejected(self, comment):
        for rec in self.filtered(lambda r: r.state == "in_review"):
            rec._guarded().write({"state": "draft", "rejection_reason": comment or False})
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "in_review")._guarded().write({"state": "draft"})
        return result

    def _start(self):
        for rec in self.filtered(lambda r: r.state == "approved"):
            rec._guarded().write({"state": "active"})
            publish(
                self.env,
                "pricing.promotion_activated",
                "fix.promotion",
                rec.id,
                {
                    "code": rec.code,
                    "discount_type": rec.discount_type,
                    "value": rec.value,
                    "channel": rec.channel,
                    "valid_until": fields.Date.to_string(rec.valid_until),
                    "approved_by_id": rec.approved_by.id or None,
                },
            )

    def _end(self, reason):
        for rec in self.filtered(lambda r: r.state in ("approved", "active")):
            rec._guarded().write({"state": "ended", "ended_reason": reason})
            rec.message_post(body="Promotion ended: %s" % reason)

    def action_end(self, reason=None):
        require_role(self.env, (ROLE_OFFICER,), "Ending a promotion")
        if not (reason or "").strip():
            raise UserError("State why the promotion ends early.")
        self._end(reason)
        return True

    # ---- the pricing path (consumers: M36 quotation, M38 storefront) --------
    def _usable_on(self, channel=None, on_date=None):
        self.ensure_one()
        day = on_date or fields.Date.context_today(self)
        return bool(
            self.state == "active"
            and self.active
            and (not self.valid_from or self.valid_from <= day)
            and (not self.valid_until or self.valid_until >= day)
            and (self.channel == "all" or not channel or self.channel == channel)
            and (not self.max_uses or self.use_count < self.max_uses)
            and (not self.budget_amount or self.budget_used < self.budget_amount - 0.005)
        )

    def discount_on(self, base_price):
        """The discount this promotion gives on `base_price` (never more than
        the price, never more than what is left of its budget)."""
        self.ensure_one()
        base = max(base_price or 0.0, 0.0)
        raw = base * self.value / 100.0 if self.discount_type == "percent" else self.value
        if self.budget_amount:
            raw = min(raw, max(self.budget_amount - self.budget_used, 0.0))
        return round(min(raw, base), 2)

    @api.model
    def best_combination(self, promotions, base_price, channel=None):
        """Stacking rules: exclusive promotions never combine (the best one
        wins, priority breaking ties); stackable ones add up; the larger of
        the two outcomes applies. Returns (promotions, discount)."""
        usable = promotions.filtered(lambda p: p._usable_on(channel))
        exclusive = usable.filtered(lambda p: not p.stackable)
        best_ex = max(
            exclusive, key=lambda p: (p.discount_on(base_price), -p.priority), default=None
        )
        stack = usable.filtered("stackable")
        stack_total = min(sum(p.discount_on(base_price) for p in stack), base_price or 0.0)
        ex_total = best_ex.discount_on(base_price) if best_ex else 0.0
        if stack and stack_total >= ex_total:
            return stack, round(stack_total, 2)
        return (best_ex or self.browse()), round(ex_total, 2)

    def consume(self, amount):
        """Record one use giving `amount` of discount; refused once the budget
        or the usage cap is spent. A service method: the selling document
        calls it, not the user."""
        self.ensure_one()
        rec = self.sudo()
        if not rec._usable_on():
            raise UserError("Promotion %s is not usable now." % rec.code)
        if rec.budget_amount and rec.budget_used + amount > rec.budget_amount + 0.005:
            raise UserError("Promotion %s has not enough budget left." % rec.code)
        rec._guarded().write(
            {"use_count": rec.use_count + 1, "budget_used": rec.budget_used + amount}
        )
        exhausted = (rec.max_uses and rec.use_count >= rec.max_uses) or (
            rec.budget_amount and rec.budget_used >= rec.budget_amount - 0.005
        )
        if exhausted:
            rec._end("budget or usage cap reached")
        return True

    @api.model
    def cron_promotion_window(self):
        """Approved promotions start on their first day; active ones end after
        their last day or once their budget is spent (Dhaka date).
        Idempotent."""
        today = fields.Date.context_today(self)
        starting = self.search([("state", "=", "approved"), ("valid_from", "<=", today)])
        starting._start()
        ending = self.search([("state", "in", ("approved", "active")), ("valid_until", "<", today)])
        ending._end("validity window ended")
        spent = self.search([("state", "=", "active")]).filtered(
            lambda p: (p.max_uses and p.use_count >= p.max_uses)
            or (p.budget_amount and p.budget_used >= p.budget_amount - 0.005)
        )
        spent._end("budget or usage cap reached")
        return len(starting) + len(ending) + len(spent)


POLICY_FROZEN = frozenset({"role", "min_pct", "max_pct", "requires_approval", "approval_tier"})


class FixDiscountPolicy(models.Model):
    """Who may give how much discount without escalation.

    A04 audit M11-9 (dp_01): the policy was read by nothing and a clerk could
    widen any band. It is now THE discount ladder (discount_ladder()), each
    band released by a Price-Book Releaser through M63; until a band is
    released the spec's BRU-PRC-06 ladder applies."""

    _name = "fix.discount.policy"
    _description = "Discount Policy"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "min_pct"

    _approval_domain = "pricing_discount_policy"
    _approval_apply_method = "action_approve"
    _approval_group = ROLE_RELEASER
    _approval_routed = True

    name = fields.Char(required=True)
    role = fields.Selection(
        [
            ("agent", "Service Agent"),
            ("supervisor", "Supervisor"),
            ("manager", "Manager"),
            ("director", "Director"),
        ],
        required=True,
        default="agent",
    )
    min_pct = fields.Float(required=True, default=0.0, help="Band start (inclusive).")
    max_pct = fields.Float(required=True, default=5.0, help="Band end (inclusive).")
    requires_approval = fields.Boolean(default=True)
    approval_tier = fields.Selection(
        DOFA_TIERS,
        default="tier_2",
        required=True,
        help="The DOFA tier that approves a discount in this band when it needs approval.",
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_review", "In Review"),
            ("active", "In Force"),
            ("retired", "Retired"),
        ],
        required=True,
        default="draft",
        readonly=True,
        help="Only an In Force band is part of the discount ladder.",
    )
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)

    _band_bounds = models.Constraint(
        "CHECK (min_pct >= 0 AND max_pct <= 100 AND min_pct < max_pct)",
        "A discount band runs from 0 to 100% and ends after it starts.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by", "submitted_by"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= POLICY_FROZEN
        return locked

    @staticmethod
    def _check_band_vals(vals):
        lo, hi = vals.get("min_pct"), vals.get("max_pct")
        for v in (lo, hi):
            if v is not None and not 0.0 <= v <= 100.0:
                raise ValidationError("A discount band runs from 0 to 100%.")
        if lo is not None and hi is not None and lo >= hi:
            raise ValidationError("A discount band ends after it starts.")

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Authoring a discount band")
        for vals in vals_list:
            self._check_band_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        _officer_write_check(self, vals, "Changing a discount band", POLICY_FROZEN)
        self._check_band_vals(vals)
        return super().write(vals)

    def _overlapping(self):
        self.ensure_one()
        return self.search(
            [
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("state", "=", "active"),
                ("min_pct", "<", self.max_pct),
                ("max_pct", ">", self.min_pct),
            ]
        )

    def action_request_approval(self, justification=None):
        require_role(self.env, (ROLE_OFFICER,), "Submitting a discount band")
        for rec in self:
            resubmit = rec.state == "in_review" and rec.approval_state in ("none", "returned")
            if rec.state != "draft" and not resubmit:
                raise UserError("Only a Draft discount band is submitted.")
            rec._guarded().write({"state": "in_review", "submitted_by": self.env.uid})
        return super().action_request_approval(justification=justification)

    def action_submit(self):
        return self.action_request_approval()

    def action_approve(self):
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Only a band In Review is released.")
            require_releaser_not_author(
                self.env,
                authority,
                acting,
                rec,
                rec.create_uid | rec.submitted_by,
                "Releasing a discount band",
            )
            clash = rec._overlapping()
            if clash:
                raise UserError(
                    "Band %s overlaps the band in force %s; retire that one first."
                    % (rec.name, clash[0].name)
                )
            rec._guarded().write({"state": "active", "approved_by": self.env.uid})
        return True

    def _approval_on_rejected(self, comment):
        self.filtered(lambda r: r.state == "in_review")._guarded().write({"state": "draft"})
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "in_review")._guarded().write({"state": "draft"})
        return result

    def action_retire(self):
        require_role(
            self.env, (ROLE_RELEASER,), "Retiring a discount band", role="Price-Book Releaser"
        )
        for rec in self:
            if rec.state != "active":
                raise UserError("Only a band in force is retired.")
            rec._guarded().write({"state": "retired"})
        return True

    @api.model
    def discount_ladder(self, company=None):
        """THE discount ladder: [(upper bound % inclusive, DOFA tier)], the
        last entry a ceiling. Released bands of the company; the spec's
        BRU-PRC-06 ladder while none is released. Callers: the discount
        approval (M36), the estimate (M01) and any selling document."""
        company = company or self.env.company
        bands = (
            self.sudo()
            .search([("company_id", "=", company.id), ("state", "=", "active")])
            .sorted("max_pct")
        )
        if not bands:
            return list(DEFAULT_DISCOUNT_LADDER)
        ladder = [(b.max_pct, b.approval_tier if b.requires_approval else "tier_0") for b in bands]
        if ladder[-1][0] < 100.0:
            # above every released band: the CCO (BRU-PRC-06)
            ladder.append((float("inf"), "tier_4"))
        return ladder

    @api.model
    def tier_for_discount(self, pct, company=None):
        for bound, tier in self.discount_ladder(company):
            if (pct or 0.0) <= bound:
                return tier
        return "tier_4"


class FixPriceSimulation(models.Model):
    """A04 audit M11-10 (ps_01): state and result were typed by hand. The
    result is computed by action_compute from the released rate card, the
    floor and the active promotions; nobody types it."""

    _name = "fix.price.simulation"
    _description = "Price Simulation Request"
    _inherit = ["fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    catalogue_item_id = fields.Many2one("fix.catalogue.item", string="Catalogue Item")
    rate_card_id = fields.Many2one("fix.rate.card", string="Rate Card")
    input_json = fields.Text(
        help="Scenario inputs as JSON: quantity, customer_tier, contract_no, channel, price."
    )
    result_json = fields.Text(readonly=True, help="Computed output — filled by the pricing engine.")
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed")],
        required=True,
        default="draft",
        readonly=True,
    )
    requested_by = fields.Many2one("res.users", default=lambda self: self.env.user, readonly=True)
    computed_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {"state", "result_json", "computed_at"}
        if self:
            guarded |= {"requested_by"}
        return guarded

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self:
                if rec.requested_by != self.env.user and not has_role(self.env, ROLE_OFFICER):
                    raise UserError("Only the requester edits a simulation request.")
        return super().write(vals)

    def _inputs(self):
        self.ensure_one()
        raw = (self.input_json or "").strip()
        if not raw:
            return {}
        try:
            data = json.loads(raw)
        except ValueError as exc:
            raise UserError("The simulation inputs are not valid JSON: %s" % exc) from exc
        if not isinstance(data, dict):
            raise UserError("The simulation inputs must be a JSON object.")
        return data

    def action_compute(self):
        """Price the scenario as the engine would: the released rate card for
        the item (contract > tier), the quantity, the floor, and the best
        promotion combination. Writes the result; never writes a price."""
        Card = self.env["fix.rate.card"].sudo()
        Floor = self.env["fix.price.floor"].sudo()
        Promo = self.env["fix.promotion"].sudo()
        for rec in self:
            data = rec._inputs()
            qty = float(data.get("quantity") or 1.0)
            if qty <= 0:
                raise UserError("Simulate a positive quantity.")
            code = rec.rate_card_id.product_code or (
                rec.catalogue_item_id.product_tmpl_id.default_code or ""
            )
            card = rec.rate_card_id.sudo()
            if not card or card.state != "released":
                card = Card._resolve(
                    code,
                    tier=int(data.get("customer_tier") or 0),
                    contract_no=data.get("contract_no") or None,
                )
            if not card:
                raise UserError("No released rate card prices %s." % (code or rec.name))
            unit = card.unit_price
            promos, discount = Promo.best_combination(
                Promo.search([("state", "=", "active")]), unit, data.get("channel")
            )
            floors = Floor.search([("product_code", "=", card.product_code)])
            floor = max(floors.mapped("floor_price") or [0.0])
            net = round(unit - discount, 2)
            result = {
                "rate_card_id": card.id,
                "rate_card": card.name,
                "unit_price": unit,
                "quantity": qty,
                "gross": round(unit * qty, 2),
                "promotions": promos.mapped("code"),
                "promotion_discount_per_unit": discount,
                "net_unit_price": net,
                "net_total": round(net * qty, 2),
                "floor_price": floor,
                "net_below_floor": bool(floor and net + 0.005 < floor),
            }
            proposed = data.get("price")
            if proposed is not None:
                result["proposed_price"] = float(proposed)
                result["proposed_below_floor"] = bool(floor and float(proposed) + 0.005 < floor)
            rec._guarded().write(
                {
                    "state": "computed",
                    "result_json": json.dumps(result, sort_keys=True),
                    "computed_at": fields.Datetime.now(),
                }
            )
        return True


class FixApprovalMatrixFloorDomains(models.Model):
    """A11 audit P2: lets a DoA matrix row target the routed price-floor
    override (SLA, escalation, policy) without touching any other DOFA
    approval."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("price_floor_override", "Price-Floor Override")],
        ondelete={"price_floor_override": "cascade"},
    )
