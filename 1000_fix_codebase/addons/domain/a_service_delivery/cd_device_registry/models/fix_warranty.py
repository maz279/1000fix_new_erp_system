# fix.warranty — warranty status model (P04-M01-T04).
# Built in the registry so M09 reads rather than duplicates.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

# A02 audit M01-W1 (security/fix_device_registry_groups.xml, ships empty).
WARRANTY_OFFICER_GROUP = "cd_device_registry.group_warranty_officer"

# The terms a verification stands behind. While a warranty is pending they
# may be corrected (pending cover gives no entitlement); once a warranty is
# verified, voided or expired they are frozen, so cover cannot be extended
# after the fact (a clerk moved end_date to 2030 through P03).
_TERMS = frozenset(
    {"device_id", "warranty_type", "start_date", "end_date", "proof_document_id", "deductible"}
)


class FixWarranty(models.Model):
    """A warranty claim/status record for a device."""

    _name = "fix.warranty"
    _description = "Warranty"
    # fix.approvable.mixin carries fix.guarded.mixin (A02 audit B1: the
    # verification is routed, fix_warranty_approval.py).
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "device_id, start_date desc"

    def _fix_guarded_fields(self) -> set:
        # A02 audit M01-W1: any user created ACTIVE cover with no proof, or
        # flipped pending to active and stamped the verification by a plain
        # write - and so opened a free warranty job. Only Verify and Void
        # change these.
        return super()._fix_guarded_fields() | {
            "status",
            "verified_by",
            "verified_at",
            "void_reason",
            # A07 P1 (2026-11-04): stamped by cron_warranty_expiry only.
            "expiry_notified_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(w.status != "pending" for w in self):
            locked |= _TERMS
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            touched = _TERMS & set(vals)
            for rec in self.filtered(lambda w: w.status != "pending"):
                changed = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed:
                    raise UserError(
                        "The warranty on %s is %s: its terms (%s) are frozen. Register a "
                        "new warranty for new cover."
                        % (
                            rec.device_id.display_name,
                            rec.status,
                            ", ".join(self._fields[n].string or n for n in sorted(changed)),
                        )
                    )
        return super().write(vals)

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )

    warranty_type = fields.Selection(
        [
            ("manufacturer", "Manufacturer Warranty"),
            ("brand_standard", "Brand Standard Warranty"),
            ("extended", "Extended/1000FiX"),
            ("brand_auth", "Brand Authorisation"),
            ("none", "No Warranty"),
        ],
        required=True,
        default="manufacturer",
        tracking=True,
    )
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True, tracking=True)
    status = fields.Selection(
        [
            ("active", "Active"),
            ("expired", "Expired"),
            ("voided", "Voided"),
            ("pending", "Pending Verification"),
        ],
        # A02 audit M01-W1: born pending. Pending cover gives no entitlement
        # until a Warranty Officer verifies its proof.
        default="pending",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )

    # Warranty terms
    coverage_details = fields.Text()
    deductible = fields.Monetary(string="Deductible", currency_field="currency_id", default=0.0)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )

    # Proof
    proof_document_id = fields.Many2one(
        "fix.document",
        string="Proof Document",
        help="Purchase receipt or warranty card via the M24-core API",
    )
    verified_by = fields.Many2one("res.users", readonly=True, copy=False)
    verified_at = fields.Datetime(readonly=True, copy=False)
    void_reason = fields.Text(string="Void Reason", readonly=True, copy=False)
    verification_state = fields.Selection(
        [
            ("unverified", "Proof Not Verified"),
            ("verified", "Proof Verified"),
            ("not_required", "No Warranty — Nothing to Verify"),
        ],
        string="Verification",
        compute="_compute_verification_state",
        store=True,
        help="Whether a person has checked the purchase proof behind this "
        "warranty. Unverified cover is still cover — it is just cover nobody "
        "has stood behind yet.",
    )

    verification_blocker = fields.Char(
        string="To Verify, Needed",
        compute="_compute_verification_blocker",
        help="What this warranty is waiting on. A queue of 53 'unverified' "
        "rows is a number; a queue that says each row has no proof attached "
        "is work someone can pick up (A04 audit, 2026-11-01).",
    )

    @api.depends("verification_state", "proof_document_id", "status")
    def _compute_verification_blocker(self):
        for rec in self:
            if (
                rec.verification_state == "verified"
                or rec.verification_state == "not_required"
                or rec.status in ("voided", "expired")
            ):
                rec.verification_blocker = False
            elif not rec.proof_document_id:
                rec.verification_blocker = (
                    "Attach the purchase receipt or warranty card, then Verify"
                )
            else:
                rec.verification_blocker = "Proof is attached - ready to Verify"

    @api.depends("verified_at", "warranty_type")
    def _compute_verification_state(self):
        for rec in self:
            if rec.warranty_type == "none":
                rec.verification_state = "not_required"
            elif rec.verified_at:
                rec.verification_state = "verified"
            else:
                rec.verification_state = "unverified"

    # ---- A07 P1/P2 (2026-11-04), M17-5 / M17-13 -----------------------------
    # AUT-AST-10 notice horizon: the spec says "configured horizons" and gives
    # no number; 30 days is a default the business must confirm (B2).
    EXPIRY_NOTICE_DAYS_PARAM = "cd_device_registry.warranty_expiry_notice_days"

    expiry_notified_on = fields.Date(string="Expiry Notice Sent On", readonly=True, copy=False)

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        # A07 audit M17-13: cover ending before it started was accepted.
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError(
                    "A warranty cannot end (%s) before it starts (%s)."
                    % (rec.end_date, rec.start_date)
                )

    def _a07_verify_checks(self):
        """BRU-AST-03: no verified cover on a provisional identity; and the
        proof must be about this device or warranty (a document filed on
        another customer verified cover, M17-13). An unfiled proof is filed
        against the warranty now, so it cannot prove a second one."""
        from .fix_device import bind_evidence

        self.ensure_one()
        self.device_id.assert_identity_resolved("have its warranty verified")
        if self.proof_document_id:
            bind_evidence(self.proof_document_id, [self, self.device_id], "proof document")

    @api.model
    def cron_warranty_expiry(self):
        """ir_cron_warranty_expiry (daily, AUT-AST-10). An active warranty
        whose end date has passed becomes `expired` (53 live rows read active
        after they ended); cover ending within the notice horizon is announced
        once as device.warranty_expiring. Idempotent, superuser-safe, and every
        effect goes through the guard. Returns (expired, announced)."""
        today = fields.Date.context_today(self.with_context(tz="Asia/Dhaka"))
        days = int(
            self.env["ir.config_parameter"].sudo().get_param(self.EXPIRY_NOTICE_DAYS_PARAM, 30) or 0
        )
        Warranty = self.sudo()
        ended = Warranty.search([("status", "=", "active"), ("end_date", "<", today)])
        for w in ended:
            w._guarded().write({"status": "expired"})
            w.message_post(body="Expired: the cover ended on %s." % w.end_date)
            w.device_id._publish(
                "device.warranty_expired",
                {
                    "device_id": w.device_id.id,
                    "warranty_id": w.id,
                    "warranty_type": w.warranty_type,
                    "end_date": str(w.end_date),
                    "owner_id": w.device_id.owner_id.id or None,
                },
            )
        soon = Warranty.search(
            [
                ("status", "=", "active"),
                ("end_date", ">=", today),
                ("end_date", "<=", today + timedelta(days=days)),
                ("expiry_notified_on", "=", False),
            ]
        )
        for w in soon:
            w._guarded().write({"expiry_notified_on": today})
            w.device_id._publish(
                "device.warranty_expiring",
                {
                    "device_id": w.device_id.id,
                    "warranty_id": w.id,
                    "warranty_type": w.warranty_type,
                    "end_date": str(w.end_date),
                    "days_left": (w.end_date - today).days,
                    "owner_id": w.device_id.owner_id.id or None,
                },
            )
        return len(ended), len(soon)

    # ---- end A07 P1/P2 ------------------------------------------------------

    def action_verify(self):
        """Record that the warranty's proof was checked by a person.

        `verified_by` / `verified_at` shipped as readonly fields with no method
        anywhere that set them, so all 55 live warranties read "Verified At —"
        and there was no way to change that: the status 'pending' had no exit
        (A04 audit, 2026-11-01). Verification is what moves a pending warranty
        to active, so it needs proof on file and a named verifier.
        """
        for warranty in self:
            warranty._fix_assert_officer("verify")
            if warranty.status in ("voided", "expired"):
                raise UserError(
                    "Warranty on %s is %s and cannot be verified."
                    % (warranty.device_id.display_name, warranty.status)
                )
            if warranty.warranty_type != "none" and not warranty.proof_document_id:
                raise UserError(
                    "Attach the purchase receipt or warranty card before "
                    "verifying the warranty on %s: a verification with no "
                    "proof on file is not evidence." % warranty.device_id.display_name
                )
            warranty._a07_verify_checks()  # A07 P2 (2026-11-04)
            warranty._guarded().write(
                {
                    "verified_by": self.env.user.id,
                    "verified_at": fields.Datetime.now(),
                    "status": "active" if warranty.status == "pending" else warranty.status,
                }
            )
            warranty.message_post(body="Warranty proof verified by %s." % self.env.user.name)
        return True

    def _fix_assert_officer(self, verb: str) -> None:
        """A3: the Warranty Officer role, and never on cover the officer
        registered (segregation of duties)."""
        self.ensure_one()
        if self.env.su:
            return
        user = self.env.user
        if not user.has_group(WARRANTY_OFFICER_GROUP):
            raise UserError(
                "Only a Warranty Officer can %s a warranty. No one holds that role "
                "yet? It is a business appointment; ask an administrator." % verb
            )
        if self.create_uid == user:
            raise UserError(
                "Segregation of duties: the person who registered the warranty on %s "
                "cannot %s it." % (self.device_id.display_name, verb)
            )

    def action_void(self, reason: str = ""):
        """Void a warranty — the other missing exit from 'pending'. A Warranty
        Officer, with a reason (A02 audit M01-W3)."""
        # A voided warranty says so first: a second void is refused whatever
        # reason is given, and only then is the reason itself required.
        for warranty in self:
            if warranty.status == "voided":
                raise UserError("This warranty is already voided.")
        if not (reason or "").strip():
            raise UserError("Give the reason the warranty is voided.")
        for warranty in self:
            warranty._fix_assert_officer("void")
            warranty._guarded().write({"status": "voided", "void_reason": reason.strip()})
            warranty.message_post(
                body="Warranty voided by %s. Reason: %s" % (self.env.user.name, reason.strip())
            )
        return True
