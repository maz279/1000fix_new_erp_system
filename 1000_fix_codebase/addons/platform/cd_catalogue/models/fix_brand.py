# fix.brand — the brand master (P03-M06-T05).
# 17+ brand partners; the master must exist before devices are registered (M17).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

from .catalogue_roles import ROLE_PUBLISHER, require_role

# A04 audit (2026-11-04) M37-7 / br_01: whether 1000FiX holds a brand's
# authorisation was a Boolean any user ticked, with an expiry nothing read.
# It is now a decision: requested with its evidence, approved by a Catalogue
# Publisher who did not request it (routed through M63 when cd_rate_card
# carries the engine), revoked with a reason, and lapsed by a nightly job.
# Sales read it: an item that requires the brand's authorisation is not sold
# while 1000FiX does not hold one in force.
AUTHORISATION_FIELDS = frozenset(
    {
        "authorised",
        "authorisation_expiry",
        "authorised_by",
        "authorised_at",
        "authorisation_reference",
        "authorisation_requested_by",
    }
)


class FixBrand(models.Model):
    """A brand partner (Samsung, Apple, Xiaomi, etc.).

    The brand master is referenced by:
    - fix.catalogue.item (which brand's products this item covers)
    - fix.device.model (M17 — which brand makes this device)
    - M08 agreements (brand authorisation terms)
    """

    _name = "fix.brand"
    _description = "Brand Master"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "name"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _name_unique = models.Constraint("UNIQUE (name)", "Brand name must be unique")

    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")
    code = fields.Char(
        string="Brand Code", required=True, size=10, help="Short code, e.g. SAMS, APPL"
    )
    logo = fields.Binary()
    website = fields.Char()
    support_url = fields.Char(string="Support Portal URL")
    authorised = fields.Boolean(
        string="1000FiX Authorised",
        default=False,
        tracking=True,
        readonly=True,
        help="Whether 1000FiX is currently brand-authorised for repairs. Set by an "
        "approved authorisation decision, never typed.",
    )
    authorisation_expiry = fields.Date(
        string="Authorisation Expiry",
        readonly=True,
        help="If lapsed without escalation, work requiring this brand's "
        "authorisation cannot be performed (BRU-PCM-08)",
    )
    authorised_by = fields.Many2one("res.users", readonly=True, copy=False)
    authorised_at = fields.Datetime(readonly=True, copy=False)
    authorisation_reference = fields.Char(
        readonly=True, copy=False, help="The brand's authorisation letter or agreement number."
    )
    authorisation_requested_by = fields.Many2one("res.users", readonly=True, copy=False)
    proposed_authorisation_reference = fields.Char(
        string="Authorisation Evidence (reference)",
        copy=False,
        help="Staged with the request: the brand's letter or agreement number.",
    )
    proposed_authorisation_expiry = fields.Date(string="Proposed Authorisation Expiry", copy=False)
    device_model_ids = fields.One2many("fix.device.model", "brand_id", string="Device Models")
    model_count = fields.Integer(compute="_compute_model_count", store=True)
    active = fields.Boolean(default=True, tracking=True)

    @api.depends("device_model_ids")
    def _compute_model_count(self):
        for rec in self:
            rec.model_count = len(rec.device_model_ids)

    # ---- guard ------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | set(AUTHORISATION_FIELDS)
        if any(rec.authorisation_requested_by for rec in self):
            # the request is pinned to the evidence and date it was made for
            guarded |= {"proposed_authorisation_reference", "proposed_authorisation_expiry"}
        return guarded

    def _authorisation_in_force(self, on_date=None) -> bool:
        self.ensure_one()
        rec = self.sudo()
        if not rec.authorised:
            return False
        day = on_date or fields.Date.context_today(self)
        return not rec.authorisation_expiry or rec.authorisation_expiry >= day

    # ---- decision ---------------------------------------------------------
    # Hooks the M63 engine overrides (see fix.catalogue.item).
    def _brand_route_request(self):
        return None

    def _brand_route_guard(self):
        return None

    def _brand_authority_user(self):
        return self.env.user

    def _brand_acting_users(self):
        return self.env.user

    def action_request_authorisation(self):
        """Ask for the authorisation staged on the brand (evidence reference
        and expiry). Any internal user may ask; a publisher decides."""
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.authorisation_requested_by:
                raise UserError("An authorisation request for %s is already open." % rec.name)
            ref = (rec.proposed_authorisation_reference or "").strip()
            if not ref:
                raise UserError(
                    "Record the brand's authorisation letter or agreement reference first."
                )
            if not rec.proposed_authorisation_expiry or rec.proposed_authorisation_expiry < today:
                raise UserError("An authorisation needs an expiry date that is not past.")
            rec._guarded().write({"authorisation_requested_by": self.env.uid})
            rec._brand_route_request()
        return True

    def action_approve_authorisation(self):
        """A Catalogue Publisher who did not request it grants the staged
        authorisation (from the M63 inbox when the engine is installed)."""
        self._brand_route_guard()
        authority = self._brand_authority_user()
        acting = self._brand_acting_users()
        for rec in self:
            if not rec.authorisation_requested_by:
                raise UserError("No authorisation was requested for %s." % rec.name)
            if not self.env.su:
                if not authority.has_group(ROLE_PUBLISHER):
                    raise UserError(
                        "Deciding a brand authorisation needs the Catalogue Publisher role."
                    )
                if acting & rec.authorisation_requested_by:
                    raise UserError(
                        "Segregation of duties: you requested this authorisation; another "
                        "publisher decides it."
                    )
            rec._guarded().write(
                {
                    "authorised": True,
                    "authorisation_expiry": rec.proposed_authorisation_expiry,
                    "authorisation_reference": rec.proposed_authorisation_reference,
                    "authorised_by": self.env.uid,
                    "authorised_at": fields.Datetime.now(),
                    "authorisation_requested_by": False,
                    "proposed_authorisation_reference": False,
                    "proposed_authorisation_expiry": False,
                }
            )
            rec.message_post(
                body="Brand authorisation granted by %s until %s (ref. %s)."
                % (self.env.user.name, rec.authorisation_expiry, rec.authorisation_reference)
            )
            rec._publish_authorisation("granted")
        return True

    def _brand_clear_request(self, reason=None):
        for rec in self.filtered("authorisation_requested_by"):
            rec._guarded().write({"authorisation_requested_by": False})
            rec.message_post(body="Authorisation request closed: %s" % (reason or "recalled"))

    def action_revoke_authorisation(self, reason=None):
        require_role(
            self.env,
            (ROLE_PUBLISHER,),
            "Revoking a brand authorisation",
            role="Catalogue Publisher",
        )
        if not (reason or "").strip():
            raise UserError("State why the authorisation is revoked.")
        for rec in self.filtered("authorised"):
            rec._guarded().write({"authorised": False})
            rec.message_post(
                body="Brand authorisation revoked by %s: %s" % (self.env.user.name, reason)
            )
            rec._publish_authorisation("revoked")
        return True

    def _publish_authorisation(self, change):
        for rec in self:
            publish(
                self.env,
                "catalogue.brand_authorisation_changed",
                "fix.brand",
                rec.id,
                {
                    "brand": rec.name,
                    "change": change,
                    "authorised": bool(rec.authorised),
                    "expiry": fields.Date.to_string(rec.authorisation_expiry)
                    if rec.authorisation_expiry
                    else None,
                },
            )

    @api.model
    def cron_authorisation_expiry(self):
        """Lapse every authorisation whose expiry has passed (BRU-PCM-08).
        Idempotent: a lapsed brand is no longer authorised."""
        today = fields.Date.context_today(self)
        lapsed = self.search(
            [
                ("authorised", "=", True),
                ("authorisation_expiry", "!=", False),
                ("authorisation_expiry", "<", today),
            ]
        )
        for rec in lapsed:
            rec._guarded().write({"authorised": False})
            rec.message_post(body="Brand authorisation lapsed on %s." % rec.authorisation_expiry)
        lapsed._publish_authorisation("lapsed")
        return len(lapsed)
