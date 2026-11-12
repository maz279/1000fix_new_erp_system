# M12 marketplace listings: the seller's published service listing.
#
# A04 workflow audit (2026-11-03) M12-10, C2-C4 build (2026-11-04): a listing
# had no methods and no company. An "active" listing was created for a
# KYC-REJECTED seller, and the one live active listing belongs to a seller
# with no CFO approval. A listing is now draft -> submitted -> active, and
# goes live only when a Marketplace Compliance Reviewer other than the
# submitter approves it from the M63 inbox, for a verified, CFO-approved
# seller. Price, category and seller are frozen while it is live (withdraw
# it to draft to change them).
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_marketplace import COMPLIANCE_GROUP, OPERATOR_GROUP, _assert_role, _seller_users

LISTING_STATES = [
    ("draft", "Draft"),
    ("submitted", "Awaiting Approval"),
    ("active", "Active"),
    ("paused", "Paused"),
    ("rejected", "Rejected"),
    ("removed", "Removed"),
]
LIVE_STATES = ("submitted", "active", "paused")
_TERMS = {"name", "seller_id", "category_id", "list_price", "currency_id", "description"}


class FixMarketplaceListing(models.Model):
    _name = "fix.marketplace.listing"
    _description = "Marketplace Listing"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "name"

    _approval_domain = "marketplace_listing"
    _approval_apply_method = "action_approve"
    _approval_group = COMPLIANCE_GROUP
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(string="Listing Title", required=True)
    seller_id = fields.Many2one(
        "fix.marketplace.seller", required=True, ondelete="cascade", index=True
    )
    category_id = fields.Many2one("product.category", string="Category")
    list_price = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    description = fields.Text()
    state = fields.Selection(
        LISTING_STATES, required=True, default="draft", readonly=True, tracking=True
    )
    submitted_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(readonly=True)
    # M12-stock (12 Nov 2026): the seller's reported stock behind the listing.
    stock_ids = fields.One2many("fix.seller.stock", "listing_id", string="Seller Stock")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_by_id",
            "approved_by_id",
            "approved_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state in (*LIVE_STATES, "removed"):
            locked |= _TERMS
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state in (*LIVE_STATES, "removed")):
                changed = [
                    n for n in _TERMS & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "Listing %s is %s: withdraw it to draft to change %s, then submit it "
                        "again." % (rec.name, rec.state, ", ".join(sorted(changed)))
                    )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        _assert_role(self.env, OPERATOR_GROUP, "Creating a marketplace listing")
        return super().create(vals_list)

    def _check_seller(self):
        self.ensure_one()
        seller = self.seller_id
        if seller.kyc_status != "verified" or not seller.cfo_approved:
            raise UserError(
                "%s is not KYC-verified and CFO-approved: its listings cannot go live "
                "(BRU-ECM-01)." % seller.name
            )
        if self.category_id and self.category_id not in seller.category_ids:
            raise UserError(
                "%s is not qualified for %s (BRU-ECM-07)." % (seller.name, self.category_id.name)
            )
        # M12 capture audit (13 Nov 2026): no listing of a suspended seller
        # goes live (submit or resume), BRU-MKP-11.
        seller._assert_not_suspended("putting a listing live")

    # ---- approval-engine hooks ------------------------------------------
    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.state == "submitted"

    def _approval_amount(self) -> float:
        return abs(self.list_price or 0.0)

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"seller_id", "category_id"}

    def _approval_excluded(self):
        excluded = super()._approval_excluded()
        return excluded | (self.submitted_by_id | _seller_users(self.seller_id)).sudo()

    def _approval_on_rejected(self, comment):
        for rec in self.filtered(lambda r: r.state == "submitted"):
            rec.sudo()._guarded().write({"state": "rejected"})
            rec.sudo().message_post(body="Listing rejected: %s" % (comment or "-"))

    # ---- lifecycle --------------------------------------------------------
    def action_submit(self):
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Submitting a listing")
            if rec.state not in ("draft", "rejected"):
                raise UserError("Only a draft or rejected listing is submitted.")
            if rec.list_price < 0:
                raise UserError("A listing price cannot be negative.")
            rec._check_seller()
            rec._guarded().write({"state": "submitted", "submitted_by_id": self.env.uid})
            rec.action_request_approval()
        return True

    def action_approve(self):
        """The M63 apply method: a compliance reviewer publishes the listing."""
        self._approval_assert_routed()
        trusted = self.env.su and not self._approval_task()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted listing is approved.")
            if not trusted:
                if not authority.has_group(COMPLIANCE_GROUP):
                    raise UserError(
                        "A listing is approved by a Marketplace Compliance Reviewer, which %s "
                        "is not." % authority.name
                    )
                if acting & (rec.create_uid | rec.submitted_by_id | _seller_users(rec.seller_id)):
                    raise UserError(
                        "Segregation of duties: whoever created or submitted listing %s does "
                        "not approve it." % rec.name
                    )
            rec._check_seller()
            rec._guarded().write(
                {
                    "state": "active",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_pause(self):
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Pausing a listing")
            if rec.state != "active":
                raise UserError("Only an active listing is paused.")
            rec._guarded().write({"state": "paused"})
        return True

    def action_resume(self):
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Resuming a listing")
            if rec.state != "paused":
                raise UserError("Only a paused listing is resumed.")
            rec._check_seller()
            rec._guarded().write({"state": "active"})
        return True

    def action_withdraw(self):
        """Back to draft to change the listing's terms (it is approved again)."""
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Withdrawing a listing")
            if rec.state not in ("active", "paused", "rejected"):
                raise UserError("Only a live or rejected listing is withdrawn to draft.")
            rec._guarded().write({"state": "draft", "approved_by_id": False, "approved_at": False})
        return True

    def action_remove(self):
        for rec in self:
            _assert_role(self.env, OPERATOR_GROUP, "Removing a listing")
            if rec.state == "removed":
                raise UserError("Listing %s is already removed." % rec.name)
            if rec.approval_state == "pending":
                rec.sudo()._approval_void("the listing was removed")
            rec._guarded().write({"state": "removed"})
        return True
