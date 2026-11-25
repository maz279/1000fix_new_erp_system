# fix_marketplace_award - M12 job masking, award acceptance and seller
# probation (A04 ERP audit, round 2, 21 Nov 2026).
#
#   M12-F7   Before award a seller sees an open job as a short brief and the
#            customer's initials (BRU-MKP-04): the order's customer, linked
#            service order and description are staff fields
#            (groups=base.group_user on fix.marketplace.order), and a seller
#            reads the job through the projection below. Only the awarded
#            seller sees the full job; the customer's contact only while it
#            is revealed (award to completion, BRU-ECM-05).
#   M12-F15  An award must be accepted by the awarded seller within the
#            acceptance window (cd_marketplace.award_acceptance_hours,
#            default 24); otherwise the job-lapse cron returns it to bidding.
#            The job starts only once accepted.
#            A seller is Provisional (on probation) until compliance confirms
#            them: a provisional seller holds at most
#            cd_marketplace.probation_job_cap open jobs (default 3).
#            Both defaults are THE BUSINESS'S to confirm (OWNER).
import logging
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_marketplace import (
    COMPLIANCE_GROUP,
    OPERATOR_GROUP,
    _assert_role,
)

_logger = logging.getLogger(__name__)

ACCEPT_HOURS_PARAM = "cd_marketplace.award_acceptance_hours"
ACCEPT_HOURS_DEFAULT = 24
PROBATION_CAP_PARAM = "cd_marketplace.probation_job_cap"
PROBATION_CAP_DEFAULT = 3
BRIEF_CHARS_PARAM = "cd_marketplace.job_brief_chars"
BRIEF_CHARS_DEFAULT = 140
# the awarded jobs a seller is still working on
OPEN_JOB_STATES = ("selected", "in_progress", "completed")

_PHONE_RE = re.compile(r"(?:\+?\d[\d\s\-]{6,}\d)")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def _int_param(env, key, default, floor=1):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    try:
        value = int(raw) if raw not in (None, "", False) else default
    except (TypeError, ValueError):
        _logger.warning("%s is not a whole number (%r); %s is used.", key, raw, default)
        value = default
    return max(value, floor)


def job_brief(text, limit):
    """A short, contact-free description of a job: phone numbers and email
    addresses are blanked, and the text is cut at `limit` characters."""
    text = " ".join(str(text or "").split())
    text = _EMAIL_RE.sub("[email hidden]", text)
    text = _PHONE_RE.sub("[number hidden]", text)
    if len(text) > limit:
        text = text[: max(limit - 1, 1)].rstrip() + "…"
    return text


def masked_name(name):
    """'Rahim Karim' -> 'R. K.' (a customer is never named before award)."""
    parts = [p for p in str(name or "").split() if p]
    return " ".join("%s." % p[0].upper() for p in parts) or "Customer"


class FixMarketplaceSellerStanding(models.Model):
    _inherit = "fix.marketplace.seller"

    standing = fields.Selection(
        [("provisional", "Provisional (probation)"), ("full", "Full Seller")],
        string="Standing",
        default="provisional",
        required=True,
        readonly=True,
        tracking=True,
        help="A provisional seller takes at most the probation job cap of open jobs "
        "(cd_marketplace.probation_job_cap) until compliance confirms them.",
    )
    standing_changed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    standing_changed_at = fields.Datetime(readonly=True, copy=False)
    standing_reason = fields.Char(readonly=True, copy=False)
    open_job_count = fields.Integer(
        string="Open Jobs", compute="_compute_open_job_count", compute_sudo=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "standing",
            "standing_changed_by_id",
            "standing_changed_at",
            "standing_reason",
        }

    def _compute_open_job_count(self):
        Order = self.env["fix.marketplace.order"].sudo()
        for rec in self:
            rec.open_job_count = (
                Order.search_count(
                    [("revealed_seller_id", "=", rec.id), ("state", "in", OPEN_JOB_STATES)]
                )
                if rec.id
                else 0
            )

    @api.model
    def _probation_cap(self) -> int:
        return _int_param(self.env, PROBATION_CAP_PARAM, PROBATION_CAP_DEFAULT)

    def _assert_within_probation_cap(self):
        """M12-F15: a provisional seller takes no job beyond the cap."""
        for rec in self.sudo():
            if rec.standing != "provisional":
                continue
            cap = rec._probation_cap()
            held = (
                self.env["fix.marketplace.order"]
                .sudo()
                .search_count(
                    [("revealed_seller_id", "=", rec.id), ("state", "in", OPEN_JOB_STATES)]
                )
            )
            if held >= cap:
                raise UserError(
                    "%s is a provisional seller on probation and already holds %d open job(s), "
                    "the probation cap of %d: no further job is awarded until a job closes or "
                    "compliance confirms the seller." % (rec.name, held, cap)
                )

    def _set_standing(self, standing, reason):
        for rec in self:
            rec.sudo()._guarded().write(
                {
                    "standing": standing,
                    "standing_changed_by_id": self.env.uid,
                    "standing_changed_at": fields.Datetime.now(),
                    "standing_reason": reason,
                }
            )
            rec.sudo().message_post(
                body="Standing: %s (%s)."
                % (dict(rec._fields["standing"].selection)[standing], reason)
            )

    def action_confirm_standing(self, reason=None):
        """Compliance ends the probation of a verified, CFO-approved seller."""
        _assert_role(self.env, COMPLIANCE_GROUP, "Confirming a seller's standing")
        for rec in self:
            if rec.standing == "full":
                continue
            if rec.kyc_status != "verified" or not rec.cfo_approved:
                raise UserError(
                    "%s is not KYC-verified and CFO-approved: probation ends only for an "
                    "approved seller." % rec.name
                )
            if self.env.user.partner_id.commercial_partner_id == (
                rec.partner_id.commercial_partner_id
            ):
                raise UserError("A seller's own account never confirms its standing.")
            rec._set_standing("full", (reason or "").strip() or "probation completed")
        return True

    def action_place_on_probation(self, reason=None):
        """Compliance returns a seller to probation, with the reason."""
        _assert_role(self.env, COMPLIANCE_GROUP, "Placing a seller on probation")
        reason = (str(reason).strip() if reason else "") or ""
        if not reason:
            raise UserError("State why the seller is placed on probation.")
        self.filtered(lambda r: r.standing != "provisional")._set_standing("provisional", reason)
        return True


class FixSellerQuoteLapse(models.Model):
    _inherit = "fix.seller.quote"

    state = fields.Selection(
        selection_add=[("lapsed", "Award Lapsed")], ondelete={"lapsed": "set default"}
    )


class FixMarketplaceOrderAward(models.Model):
    _inherit = "fix.marketplace.order"

    # ---- M12-F7: what a seller sees ----------------------------------------
    seller_job_brief = fields.Char(
        string="Job Brief",
        compute="_compute_seller_view",
        compute_sudo=False,
        help="The job as every seller sees it before award: a short description with no "
        "contact details.",
    )
    seller_description = fields.Text(
        string="Job Description (seller view)", compute="_compute_seller_view", compute_sudo=False
    )
    seller_customer_name = fields.Char(
        string="Customer (seller view)", compute="_compute_seller_view", compute_sudo=False
    )
    seller_customer_contact = fields.Char(
        string="Customer Contact (seller view)",
        compute="_compute_seller_view",
        compute_sudo=False,
    )

    # ---- M12-F15: the award acceptance window -------------------------------
    award_expires_at = fields.Datetime(
        string="Accept By",
        readonly=True,
        copy=False,
        help="The awarded seller accepts the job by then, or it goes back to bidding.",
    )
    award_accepted_at = fields.Datetime(string="Award Accepted", readonly=True, copy=False)
    award_accepted_by_id = fields.Many2one(
        "res.users", string="Accepted By", readonly=True, copy=False
    )
    award_accept_channel = fields.Selection(
        [("seller", "By the seller"), ("operator", "Recorded by an operator")],
        string="Accepted How",
        readonly=True,
        copy=False,
    )
    award_lapse_count = fields.Integer(string="Lapsed Awards", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "award_expires_at",
            "award_accepted_at",
            "award_accepted_by_id",
            "award_accept_channel",
            "award_lapse_count",
        }

    # ------------------------------------------------------------ projection
    def _mkp_is_awarded_seller(self, user=None) -> bool:
        self.ensure_one()
        user = user or self.env.user
        seller = self.sudo().revealed_seller_id
        return bool(seller) and (
            seller.partner_id.commercial_partner_id == user.partner_id.commercial_partner_id
        )

    @api.depends_context("uid")
    @api.depends("description", "customer_id", "revealed_seller_id", "customer_contact_revealed")
    def _compute_seller_view(self):
        staff = self.env.su or self.env.user._is_internal()
        limit = _int_param(self.env, BRIEF_CHARS_PARAM, BRIEF_CHARS_DEFAULT, floor=20)
        for rec in self:
            src = rec.sudo()
            full = staff or rec._mkp_is_awarded_seller()
            desc = src.description or ""
            brief = job_brief(desc, limit)
            partner = src.customer_id
            rec.seller_job_brief = brief
            rec.seller_description = desc if full else brief
            rec.seller_customer_name = partner.name if full else masked_name(partner.name)
            contact = ""
            if staff or (full and src.customer_contact_revealed):
                contact = " | ".join(
                    filter(
                        None,
                        [
                            partner.phone,
                            partner.email,
                            " ".join((partner.contact_address or "").split()),
                        ],
                    )
                )
            rec.seller_customer_contact = contact

    # ------------------------------------------------------------ award
    @api.model
    def _award_hours(self) -> int:
        return _int_param(self.env, ACCEPT_HOURS_PARAM, ACCEPT_HOURS_DEFAULT)

    def action_select_quote(self, quote):
        # M12-F15: a provisional seller takes no job beyond the probation cap
        quote.seller_id._assert_within_probation_cap()
        result = super().action_select_quote(quote)
        expires = fields.Datetime.now() + timedelta(hours=self._award_hours())
        for rec in self.filtered(lambda r: r.state == "selected"):
            rec._guarded().write(
                {
                    "award_expires_at": expires,
                    "award_accepted_at": False,
                    "award_accepted_by_id": False,
                    "award_accept_channel": False,
                }
            )
        return result

    def action_accept_award(self):
        """The awarded seller accepts the job inside the acceptance window
        (from the seller portal), or an operator records the seller's
        acceptance on their behalf. An award past its window lapses here."""
        now = fields.Datetime.now()
        accepted = True
        for rec in self:
            src = rec.sudo()
            if self.env.su or (rec._mkp_is_awarded_seller() and not self.env.user._is_internal()):
                channel = "seller"
            elif self.env.user.has_group(OPERATOR_GROUP):
                channel = "operator"
            else:
                raise UserError(
                    "Only the awarded seller accepts a job (or an operator records it)."
                )
            if src.state != "selected" or not src.selected_quote_id:
                raise UserError("Order %s has no award waiting for acceptance." % src.name)
            if src.award_accepted_at:
                continue
            if src.award_expires_at and src.award_expires_at < now:
                # too late: the award lapses now (kept - nothing is raised, so
                # the lapse is not rolled back) and nothing is accepted
                src._lapse_award("the seller did not accept by %s" % src.award_expires_at)
                accepted = False
                continue
            src._guarded().write(
                {
                    "award_accepted_at": now,
                    "award_accepted_by_id": self.env.uid,
                    "award_accept_channel": channel,
                }
            )
            src.message_post(
                body="Award accepted (%s) by %s."
                % (dict(src._fields["award_accept_channel"].selection)[channel], self.env.user.name)
            )
        return accepted

    def action_start_job(self):
        for rec in self:
            if rec.state == "selected" and not rec.sudo().award_accepted_at:
                raise UserError(
                    "The seller has not accepted the award of %s yet (accept by %s): the job "
                    "starts once accepted (A04 ERP M12-F15)."
                    % (rec.sudo().name, rec.sudo().award_expires_at or "-")
                )
        return super().action_start_job()

    def _lapse_award(self, reason):
        """Return an unaccepted award to bidding: the awarded quote lapses,
        the others compete again, the contact is withdrawn and nothing is
        pinned. Superuser service (the cron, or an acceptance too late)."""
        for rec in self.sudo():
            if rec.state != "selected" or rec.award_accepted_at:
                continue
            lapsed = rec.selected_quote_id
            seller = lapsed.seller_id
            lapsed._guarded().write({"state": "lapsed"})
            others = rec.quote_ids.filtered(lambda q: q.state == "not_selected")
            others._guarded().write({"state": "submitted"})
            rec._guarded().write(
                {
                    "state": "quoted" if others else "open",
                    "selected_quote_id": False,
                    "awarded_price": 0.0,
                    "commission_rate": rec._default_commission_rate(),
                    "customer_contact_revealed": False,
                    "revealed_seller_id": False,
                    "award_expires_at": False,
                    "award_lapse_count": rec.award_lapse_count + 1,
                }
            )
            rec.message_post(
                body="Award to %s lapsed (%s): the job is back for quotes." % (seller.name, reason)
            )
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Award lapsed: choose another quote",
                note="%s did not accept the job in time." % seller.name,
                user_id=rec.create_uid.id or self.env.uid,
            )
        return True

    @api.model
    def cron_lapse_unaccepted_awards(self, limit=500):
        """M12-F15: awards not accepted inside their window go back to
        bidding. Idempotent: only selected, unaccepted, expired awards."""
        due = self.sudo().search(
            [
                ("state", "=", "selected"),
                ("award_accepted_at", "=", False),
                ("award_expires_at", "!=", False),
                ("award_expires_at", "<", fields.Datetime.now()),
            ],
            limit=limit,
        )
        for order in due:
            try:
                with self.env.cr.savepoint():
                    order._lapse_award("not accepted by %s" % order.award_expires_at)
            except UserError as exc:
                _logger.warning("marketplace award %s did not lapse: %s", order.name, exc)
        return len(due)
