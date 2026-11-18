# fix_rental_capture — M13 capture pass 2 (2026-11-19).
#
# The 13 Nov pass gave every M13 sub-module page a button. Measured against
# the spec (FR-RNT-001…044, BRU-RNT-01…22, §10.1 entities) eight things the
# spec asks a person to record had no record anywhere, and two hard rules
# were not enforced at all:
#
#   page 1  FR-RNT-031 inter-branch redeployment     fix.rental.redeployment
#   page 2  FR-RNT-010 (P1) eligibility & exposure   fix.rental.exposure (+ override)
#           BRU-RNT-20 (H) verified identity          gate on the reservation
#   page 3  FR-RNT-016/033 extension / variation      fix.rental.extension
#   page 4  FR-RNT-036 damage-waiver product          fix.rental.waiver.plan + election
#   page 5  FR-RNT-021/023 (P1) photographs, T-04,    fix.rental.condition.photo
#           BRU-RNT-01/19 (H)                         + photo minimum at both ends
#   page 6  FR-RNT-025 loss, theft & non-return,      fix.rental.loss
#           BRU-RNT-11/22
#   page 7  FR-RNT-027 swap-out                       fix.rental.swap
#   page 8  FR-RNT-028 / AUT-RNT-12 PM by calendar    fix.rental.pm.plan + daily job
#           or usage
#
# Nothing here invents a business number: no waiver plan, exposure limit or
# PM interval is seeded. The rules apply once the owner records them; the
# identity and photograph rules are hard rules of the spec and apply now
# (switchable per system parameter, read in rental_policy).
from __future__ import annotations

import base64
import hashlib
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from . import rental_policy as policy

OPEN_STATES = ("reserved", "delivered", "active")
LIVE_STATES = ("delivered", "active")
ASSET_CATEGORIES = [
    ("camera", "Camera & Lens"),
    ("laptop", "Laptop & PC"),
    ("projector", "Projector & Display"),
    ("audio", "Audio & Lighting"),
    ("tool", "Power Tool"),
    ("medical", "Medical Device"),
    ("network", "Network Equipment"),
    ("other", "Other"),
]
GRADES = [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")]


def _refuse(message):
    raise ValidationError(message)


def _seq(env, code, prefix):
    return env["ir.sequence"].sudo().next_by_code(code) or "%s/New" % prefix


def _final_after_create(model, recs, vals, editable_states, open_fields=()):
    """Refuse a change to a record outside its editable states (the guard
    stays open for transitions and superuser code)."""
    if not recs or recs._fix_guard_open():
        return
    for rec in recs:
        if rec.state in editable_states:
            continue
        changed = [
            n
            for n in vals
            if n in rec._fields
            and n not in open_fields
            and rec._fields[n].store
            and not n.startswith(("message_", "activity_"))
            and rec._fix_guard_differs(n, vals[n], rec[n])
        ]
        if changed:
            _refuse("%s %s is %s: it is final." % (model._description, rec.name, rec.state))


# =====================================================================
# Page 2 — eligibility & exposure (FR-RNT-010 P1, BRU-RNT-05/20)
# =====================================================================
class FixRentalExposure(models.Model):
    """A party's rental exposure limit and risk tier (spec fix.rental.exposure).

    Finance sets the limit; the system computes the open exposure from the
    party's live rentals (unit value less the deposit agreed on each). A
    booking that would take the party above its limit is refused at
    reservation unless an exposure override was approved (BRU-RNT-05)."""

    _name = "fix.rental.exposure"
    _description = "Rental Exposure Limit"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "partner_id"
    _rec_name = "partner_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Party",
        required=True,
        index=True,
        ondelete="cascade",
        help="The commercial party: the limit covers every contact of the company",
    )
    risk_tier = fields.Selection(
        [("low", "Low"), ("standard", "Standard"), ("high", "High")],
        required=True,
        default="standard",
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    exposure_limit = fields.Monetary(
        string="Exposure Limit (BDT)",
        currency_field="currency_id",
        required=True,
        tracking=True,
        help="The most unsecured fleet value (unit value less deposit) the party may "
        "hold on rent at once",
    )
    basis = fields.Text(
        string="Basis of the Limit",
        required=True,
        help="Why this limit: verified identity, deposit tier and the party's own rental "
        "history (spec §4, first design position)",
    )
    reviewed_by = fields.Many2one("res.users", readonly=True, copy=False)
    reviewed_on = fields.Date(readonly=True, copy=False)
    current_exposure = fields.Monetary(
        string="Open Exposure", currency_field="currency_id", compute="_compute_exposure"
    )
    headroom = fields.Monetary(
        string="Headroom", currency_field="currency_id", compute="_compute_exposure"
    )
    open_rental_count = fields.Integer(string="Open Rentals", compute="_compute_exposure")

    _partner_unique = models.Constraint(
        "UNIQUE (partner_id, company_id)", "A party has one rental exposure limit per company"
    )
    _limit_positive = models.Constraint(
        "CHECK (exposure_limit >= 0)", "An exposure limit cannot be negative"
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"reviewed_by", "reviewed_on"}

    @api.depends("partner_id", "exposure_limit")
    def _compute_exposure(self):
        Res = self.env["fix.rental.reservation"]
        for rec in self:
            rentals = Res._exposure_rentals(rec.partner_id)
            rec.current_exposure = sum(r._exposure_value() for r in rentals)
            rec.open_rental_count = len(rentals)
            rec.headroom = (rec.exposure_limit or 0.0) - rec.current_exposure

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            partner = self.env["res.partner"].browse(vals.get("partner_id")).exists()
            if partner and partner.commercial_partner_id != partner:
                vals["partner_id"] = partner.commercial_partner_id.id
        recs = super().create(vals_list)
        recs._guarded().write(
            {"reviewed_by": self.env.uid, "reviewed_on": fields.Date.context_today(self)}
        )
        return recs

    def write(self, vals):
        res = super().write(vals)
        if set(vals) & {"exposure_limit", "risk_tier", "basis"} and not self.env.context.get(
            "_exposure_stamp"
        ):
            self.with_context(_exposure_stamp=True)._guarded().write(
                {"reviewed_by": self.env.uid, "reviewed_on": fields.Date.context_today(self)}
            )
        return res


class FixRentalExposureOverride(models.Model):
    """BRU-RNT-05: a booking above the party's exposure limit proceeds only on a
    recorded, approved justification. The person who asked never decides."""

    _name = "fix.rental.exposure.override"
    _description = "Rental Exposure Override"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    reservation_id = fields.Many2one(
        "fix.rental.reservation",
        string="Booking",
        required=True,
        index=True,
        ondelete="cascade",
        domain=[("state", "=", "draft")],
    )
    company_id = fields.Many2one(related="reservation_id.company_id", store=True, index=True)
    customer_id = fields.Many2one(related="reservation_id.customer_id", store=True)
    currency_id = fields.Many2one(related="reservation_id.currency_id")
    exposure_limit = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    exposure_after = fields.Monetary(
        string="Exposure With This Booking", currency_field="currency_id", readonly=True
    )
    excess = fields.Monetary(
        string="Above the Limit", currency_field="currency_id", readonly=True, copy=False
    )
    justification = fields.Text(required=True)
    state = fields.Selection(
        [("requested", "Requested"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="requested",
        required=True,
        readonly=True,
        tracking=True,
        copy=False,
    )
    requested_by = fields.Many2one("res.users", readonly=True, copy=False)
    decided_by = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    decision_note = fields.Char(readonly=True, copy=False)

    _GUARDED = frozenset(
        {
            "state",
            "exposure_limit",
            "exposure_after",
            "excess",
            "requested_by",
            "decided_by",
            "decided_on",
            "decision_note",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked.add("reservation_id")
            if any(r.state != "requested" for r in self):
                locked.add("justification")
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        Res = self.env["fix.rental.reservation"]
        snaps = []
        for vals in vals_list:
            res = Res.browse(vals.get("reservation_id")).exists()
            if not res:
                continue
            if res.state != "draft":
                _refuse(
                    "An exposure override is requested before the booking is confirmed: %s is %s."
                    % (res.name, res.state)
                )
            limit, after = res._exposure_check()
            if limit is None or after <= limit + 0.005:
                _refuse(
                    "Booking %s does not take %s above an exposure limit: no override is needed."
                    % (res.name, res.customer_id.commercial_partner_id.name)
                )
            vals["name"] = _seq(self.env, "fix.rental.exposure.override", "RNT-OVR")
            snaps.append(
                {
                    "exposure_limit": limit,
                    "exposure_after": after,
                    "excess": round(after - limit, 2),
                    "requested_by": self.env.uid,
                }
            )
        recs = super().create(vals_list)
        for rec, snap in zip(recs, snaps, strict=False):
            rec._guarded().write(snap)
        return recs

    def write(self, vals):
        _final_after_create(self, self, vals, ("requested",))
        return super().write(vals)

    def _decide(self, state, note):
        for rec in self:
            if rec.state != "requested":
                raise UserError("Override %s is already %s." % (rec.name, rec.state))
            if rec.requested_by == self.env.user:
                raise UserError(
                    "You asked for override %s: another person decides it (BRU-RNT-05)." % rec.name
                )
            rec._guarded().write(
                {
                    "state": state,
                    "decided_by": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                    "decision_note": note or False,
                }
            )
            rec.reservation_id.message_post(
                body="Exposure override %s %s by %s%s"
                % (rec.name, state, self.env.user.name, (": %s" % note) if note else "")
            )

    def action_approve(self):
        self._decide("approved", None)
        return True

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say why the override is rejected.")
        self._decide("rejected", reason.strip())
        return True


# =====================================================================
# Page 3 — extension (FR-RNT-016) as a versioned variation (FR-RNT-033)
# =====================================================================
class FixRentalExtension(models.Model):
    """An in-flight extension: the new return date is checked against the
    downstream bookings of the unit and re-priced on the rate ladder, then
    applied by someone other than whoever requested it. The agreement's
    version moves on; the record is the amendment."""

    _name = "fix.rental.extension"
    _description = "Rental Extension"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    reservation_id = fields.Many2one(
        "fix.rental.reservation",
        string="Rental",
        required=True,
        index=True,
        ondelete="cascade",
        domain=[("state", "in", LIVE_STATES)],
    )
    company_id = fields.Many2one(related="reservation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="reservation_id.operating_unit_id", store=True)
    customer_id = fields.Many2one(related="reservation_id.customer_id", store=True)
    rental_asset_id = fields.Many2one(related="reservation_id.rental_asset_id")
    currency_id = fields.Many2one(related="reservation_id.currency_id")
    old_date_to = fields.Date(string="Due Back Before", readonly=True, copy=False)
    new_date_to = fields.Date(string="New Return Date", required=True)
    reason = fields.Text(string="Customer's Request", required=True)
    old_charge = fields.Monetary(
        string="Rental Charge Before", currency_field="currency_id", readonly=True, copy=False
    )
    new_charge = fields.Monetary(
        string="Rental Charge After (rate ladder)",
        currency_field="currency_id",
        compute="_compute_preview",
    )
    charge_delta = fields.Monetary(
        string="Additional Charge", currency_field="currency_id", compute="_compute_preview"
    )
    availability_result = fields.Char(string="Availability", compute="_compute_preview")
    applied_charge = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    agreement_version = fields.Integer(string="Agreement Version", readonly=True, copy=False)
    state = fields.Selection(
        [("requested", "Requested"), ("applied", "Applied"), ("rejected", "Rejected")],
        default="requested",
        required=True,
        readonly=True,
        tracking=True,
        copy=False,
    )
    requested_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    applied_on = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Char(readonly=True, copy=False)

    _GUARDED = frozenset(
        {
            "state",
            "old_date_to",
            "old_charge",
            "applied_charge",
            "agreement_version",
            "requested_by",
            "approved_by",
            "applied_on",
            "rejection_reason",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked.add("reservation_id")
            if any(r.state != "requested" for r in self):
                locked |= {"new_date_to", "reason"}
        return locked

    @api.depends("new_date_to", "reservation_id.date_to", "reservation_id.date_from")
    def _compute_preview(self):
        for rec in self:
            res = rec.reservation_id
            if not (res and rec.new_date_to and res.date_from):
                rec.new_charge = rec.charge_delta = 0.0
                rec.availability_result = False
                continue
            days = max((rec.new_date_to - res.date_from).days + 1, 1)
            rec.new_charge = res._ladder_charge(days)
            rec.charge_delta = rec.new_charge - (res.rental_charge or 0.0)
            if rec.state != "requested":
                rec.availability_result = rec.state.capitalize()
            else:
                rec.availability_result = res._extension_denial(rec.new_date_to) or "Available"

    @api.constrains("new_date_to", "reservation_id")
    def _check_dates(self):
        for rec in self.filtered(lambda r: r.state == "requested"):
            if rec.new_date_to <= (rec.old_date_to or rec.reservation_id.date_to):
                raise ValidationError(
                    "An extension moves the return date later than %s."
                    % (rec.old_date_to or rec.reservation_id.date_to)
                )

    @api.model_create_multi
    def create(self, vals_list):
        Res = self.env["fix.rental.reservation"]
        for vals in vals_list:
            res = Res.browse(vals.get("reservation_id")).exists()
            if res and res.state not in LIVE_STATES:
                _refuse(
                    "An extension varies a rental out with the customer; %s is %s."
                    % (res.name, res.state)
                )
            vals["name"] = _seq(self.env, "fix.rental.extension", "RNT-EXT")
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write(
                {
                    "old_date_to": rec.reservation_id.date_to,
                    "old_charge": rec.reservation_id.rental_charge,
                    "requested_by": self.env.uid,
                }
            )
        return recs

    def write(self, vals):
        _final_after_create(self, self, vals, ("requested",))
        return super().write(vals)

    def action_apply(self):
        today = fields.Date.context_today(self)
        for rec in self:
            res = rec.reservation_id
            if rec.state != "requested":
                raise UserError("Extension %s is %s." % (rec.name, rec.state))
            if res.state not in LIVE_STATES:
                raise UserError("Rental %s is %s: nothing to extend." % (res.name, res.state))
            if rec.requested_by == self.env.user:
                raise UserError("You requested extension %s: another person applies it." % rec.name)
            if res.date_to != rec.old_date_to:
                raise UserError(
                    "Rental %s's return date moved since %s was requested; request it again."
                    % (res.name, rec.name)
                )
            denial = res._extension_denial(rec.new_date_to)
            if denial:
                raise UserError("Extension %s cannot be applied: %s." % (rec.name, denial))
            version = (res.agreement_version or 1) + 1
            vals = {"date_to": rec.new_date_to, "agreement_version": version}
            if res.overdue_since and rec.new_date_to >= today:
                vals["overdue_since"] = False
            # the guard token opens the frozen agreement terms for this
            # recorded variation only; availability is re-checked by the
            # record's own constraint on the write
            res._guarded().write(vals)
            fee = res._late_fee_on(today) if res.date_to < today else 0.0
            res._guarded().write({"late_fee": fee})
            rec._guarded().write(
                {
                    "state": "applied",
                    "approved_by": self.env.uid,
                    "applied_on": fields.Datetime.now(),
                    "applied_charge": res.rental_charge,
                    "agreement_version": version,
                }
            )
            res.message_post(
                body="Agreement v%d: return date %s → %s by extension %s (charge %.2f → %.2f), "
                "applied by %s."
                % (
                    version,
                    rec.old_date_to,
                    rec.new_date_to,
                    rec.name,
                    rec.old_charge,
                    res.rental_charge,
                    self.env.user.name,
                )
            )
        return True

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say why the extension is refused.")
        for rec in self:
            if rec.state != "requested":
                raise UserError("Extension %s is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "rejected", "rejection_reason": reason.strip()})
        return True


# =====================================================================
# Page 4 — the damage-waiver product (FR-RNT-036, BRU-RNT-10)
# =====================================================================
class FixRentalWaiverPlan(models.Model):
    """An elective damage waiver: a % of the gross rental for a published
    excess and published exclusions. Explicitly not insurance (spec Q-04):
    it cannot be published without the legal review reference, and its
    published terms never change (a new plan replaces a retired one)."""

    _name = "fix.rental.waiver.plan"
    _description = "Rental Damage Waiver Plan"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "state, name"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    fee_pct = fields.Float(
        string="Waiver Fee (% of gross rental)", required=True, digits=(5, 2), tracking=True
    )
    excess_amount = fields.Monetary(
        string="Excess per Incident (BDT)",
        currency_field="currency_id",
        required=True,
        tracking=True,
        help="What the customer still pays on a covered damage; the rest is waived",
    )
    covers_accessories = fields.Boolean(string="Covers Missing Accessories")
    covers_theft = fields.Boolean(
        string="Covers Theft (with police report)",
        help="BRU-RNT-10: theft is never covered without a police report",
    )
    exclusions = fields.Text(
        string="Published Exclusions",
        required=True,
        default="Theft without a police report; gross negligence; deliberate damage; use "
        "outside the agreed purpose (BRU-RNT-10). A recovered unit remains Company "
        "property whatever is paid (BRU-RNT-11).",
    )
    legal_review_ref = fields.Char(
        string="Legal Review Reference",
        tracking=True,
        help="Spec Q-04: Legal's confirmation that the waiver is not a regulated insurance "
        "product. A plan is not published without it.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
        copy=False,
    )
    published_by = fields.Many2one("res.users", readonly=True, copy=False)
    published_on = fields.Date(readonly=True, copy=False)
    election_count = fields.Integer(compute="_compute_election_count")

    _fee_range = models.Constraint(
        "CHECK (fee_pct > 0 AND fee_pct <= 100)", "The waiver fee is a percentage above 0"
    )
    _excess_positive = models.Constraint(
        "CHECK (excess_amount >= 0)", "The waiver excess cannot be negative"
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"state", "published_by", "published_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(r.state != "draft" for r in self):
            locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    def _compute_election_count(self):
        Res = self.env["fix.rental.reservation"].sudo()
        for rec in self:
            rec.election_count = Res.search_count([("waiver_plan_id", "=", rec.id)])

    def write(self, vals):
        _final_after_create(self, self, vals, ("draft",))
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(r.state != "draft" for r in self):
            _refuse("A published waiver plan is part of the agreements that elected it.")
        return super().unlink()

    def action_publish(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Waiver plan %s is %s." % (rec.name, rec.state))
            if not (rec.legal_review_ref or "").strip():
                raise UserError(
                    "Waiver plan %s needs Legal's review reference before it is offered: a "
                    "damage waiver must not be a regulated insurance product (spec Q-04)."
                    % rec.name
                )
            if rec.create_uid == self.env.user:
                raise UserError(
                    "You configured waiver plan %s: another person publishes it." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "published",
                    "published_by": self.env.uid,
                    "published_on": fields.Date.context_today(self),
                }
            )
        return True

    def action_retire(self):
        for rec in self:
            if rec.state != "published":
                raise UserError(
                    "Only a published plan is retired (%s is %s)." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "retired"})
        return True


# =====================================================================
# Page 5 — condition photographs (FR-RNT-021/023, T-04, BRU-RNT-01/19)
# =====================================================================
class FixRentalConditionPhoto(models.Model):
    """One photograph of a condition report: hashed at capture, filed in M24,
    never replaced; sealed (no delete) once the rental moves past the
    report's stage."""

    _name = "fix.rental.condition.photo"
    _description = "Rental Condition Photograph"
    _inherit = ["fix.guarded.mixin"]
    _order = "condition_id, sequence, id"
    _rec_name = "view_code"

    condition_id = fields.Many2one(
        "fix.rental.condition",
        string="Condition Report",
        required=True,
        index=True,
        ondelete="cascade",
    )
    reservation_id = fields.Many2one(
        related="condition_id.reservation_id", store=True, index=True, string="Rental"
    )
    report_type = fields.Selection(related="condition_id.report_type", store=True)
    company_id = fields.Many2one(related="condition_id.company_id", store=True, index=True)
    sequence = fields.Integer(default=10)
    view_code = fields.Selection(
        [
            ("front", "Front"),
            ("back", "Back / Lid"),
            ("left", "Left Side"),
            ("right", "Right Side"),
            ("top", "Top"),
            ("bottom", "Bottom / Base"),
            ("screen", "Screen / Lens"),
            ("ports", "Ports & Connectors"),
            ("serial", "Serial Label"),
            ("accessories", "Accessories"),
            ("damage", "Damage Close-up"),
            ("other", "Other"),
        ],
        string="View",
        required=True,
        default="front",
    )
    attachment_id = fields.Many2one(
        "ir.attachment", string="Photograph (upload)", required=True, ondelete="restrict"
    )
    document_id = fields.Many2one(
        "fix.document", string="Filed in M24", readonly=True, copy=False, ondelete="restrict"
    )
    sha256 = fields.Char(string="SHA-256 at Capture", readonly=True, copy=False)
    captured_at = fields.Datetime(readonly=True, copy=False)
    captured_by = fields.Many2one("res.users", readonly=True, copy=False)
    device_ref = fields.Char(string="Capture Device")
    note = fields.Char()
    integrity_ok = fields.Boolean(
        string="Integrity Verified",
        compute="_compute_integrity",
        help="The stored photograph still hashes to the value taken at capture",
    )

    _GUARDED = frozenset({"document_id", "sha256", "captured_at", "captured_by"})

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    def _sealed(self):
        self.ensure_one()
        cond = self.condition_id
        return not cond._stage_open(cond.reservation_id, cond.report_type)

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked |= {"condition_id", "attachment_id"}
            if any(r._sealed() for r in self):
                locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    @staticmethod
    def _digest(attachment):
        raw = attachment.sudo().raw or b""
        if not raw and attachment.sudo().datas:
            raw = base64.b64decode(attachment.sudo().datas)
        return hashlib.sha256(raw).hexdigest() if raw else False

    def _compute_integrity(self):
        for rec in self:
            rec.integrity_ok = bool(rec.sha256) and self._digest(rec.attachment_id) == rec.sha256

    @api.model_create_multi
    def create(self, vals_list):
        Cond = self.env["fix.rental.condition"]
        Att = self.env["ir.attachment"]
        for vals in vals_list:
            cond = Cond.browse(vals.get("condition_id")).exists()
            if (
                cond
                and not self.env.su
                and not cond._stage_open(cond.reservation_id, cond.report_type)
            ):
                _refuse(
                    "Condition report %s is final: its rental has moved past the %s stage, so no "
                    "photograph is added to it." % (cond.name, cond.report_type)
                )
            att = Att.browse(vals.get("attachment_id")).exists().sudo()
            if not att:
                _refuse("A condition photograph needs the photograph itself.")
            if not (att.mimetype or "").startswith("image/"):
                _refuse(
                    "%s is not a photograph (%s): upload the image the inspector took."
                    % (att.name, att.mimetype or "unknown type")
                )
        recs = super().create(vals_list)
        Doc = self.env["fix.document"].sudo()
        for rec in recs:
            att = rec.attachment_id.sudo()
            digest = self._digest(att)
            if not digest:
                _refuse("The uploaded photograph is empty.")
            cond = rec.condition_id
            doc = Doc.create(
                {
                    "name": "%s %s photo %s" % (cond.name, cond.report_type, rec.view_code),
                    "attachment_id": att.id,
                    "document_type": "custody_photo",
                    "res_model": "fix.rental.condition",
                    "res_id": cond.id,
                    "company_id": cond.company_id.id,
                }
            )
            rec._guarded().write(
                {
                    "document_id": doc.id,
                    "sha256": digest,
                    "captured_at": fields.Datetime.now(),
                    "captured_by": self.env.uid,
                }
            )
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                changed = [
                    n
                    for n in vals
                    if n in rec._fields and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if not changed:
                    continue
                guarded = self._fix_guarded_fields() & set(changed)
                if guarded:  # the guard's own refusal for its fields
                    self._fix_guard_refuse(guarded)
                if {"attachment_id", "condition_id"} & set(changed):
                    _refuse(
                        "A condition photograph is never replaced (T-04): add a new one and "
                        "delete this one while the report is still open."
                    )
                if rec._sealed():
                    _refuse(
                        "Photograph of %s is sealed: the rental has moved past the report's "
                        "stage (BRU-RNT-19)." % rec.condition_id.name
                    )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(r._sealed() for r in self):
            _refuse(
                "A condition photograph cannot be deleted after its report is used (BRU-RNT-19)."
            )
        # A photograph withdrawn while its report is open keeps its file: the
        # M24 register is permanent, so the file now belongs to its document
        # (an upload is linked to the photo, and deleting the photo would take
        # the file the document points at).
        for rec in self.sudo().filtered("document_id"):
            rec.attachment_id.write({"res_model": "fix.document", "res_id": rec.document_id.id})
            rec.document_id.write(
                {
                    "description": "Withdrawn from condition report %s by %s before it was used."
                    % (rec.condition_id.name, self.env.user.name)
                }
            )
        return super().unlink()

    def _seal_documents(self):
        """The M24 copies are signature-locked once the stage closes, so the
        file behind a hash can never be swapped there either."""
        docs = self.mapped("document_id").sudo().filtered(lambda d: not d.signature_locked)
        if docs:
            docs.write({"signature_locked": True})


class FixRentalCondition(models.Model):
    _inherit = "fix.rental.condition"

    report_type = fields.Selection(
        selection_add=[
            ("swap_out", "Swap — Replacement Dispatched"),
            ("swap_in", "Swap — Faulty Unit Received"),
        ],
        ondelete={"swap_out": "cascade", "swap_in": "cascade"},
    )
    photo_ids = fields.One2many("fix.rental.condition.photo", "condition_id", string="Photographs")
    photo_count = fields.Integer(compute="_compute_photos", string="Photograph Count")
    outbound_photo_ids = fields.Many2many(
        "fix.rental.condition.photo",
        compute="_compute_photos",
        string="Outbound Photographs (for comparison)",
        help="FR-RNT-023: the pre-delivery photographs of the same rental, beside this "
        "post-return report",
    )
    swap_id = fields.Many2one("fix.rental.swap", readonly=True, copy=False, ondelete="set null")

    @api.depends("photo_ids", "reservation_id", "report_type")
    def _compute_photos(self):
        Photo = self.env["fix.rental.condition.photo"]
        for rec in self:
            rec.photo_count = len(rec.photo_ids)
            if rec.report_type == "post_return" and rec.reservation_id:
                rec.outbound_photo_ids = Photo.search(
                    [
                        ("reservation_id", "=", rec.reservation_id.id),
                        ("report_type", "=", "pre_delivery"),
                    ]
                )
            else:
                rec.outbound_photo_ids = Photo.browse()


# =====================================================================
# Page 6 — loss, theft & non-return (FR-RNT-025, BRU-RNT-11/22)
# =====================================================================
class FixRentalLoss(models.Model):
    """A unit not coming back. Escalated notice → recovery → legal; either
    recovered (the rental then returns as usual: the unit stays Company
    property, BRU-RNT-11) or written off on the fleet unit's routed write-off
    approval with a claim decision (BRU-RNT-22): the deposit is forfeited up
    to the agreed valuation, any balance is invoiced through M20, the unit is
    Lost and M49 starts its disposal."""

    _name = "fix.rental.loss"
    _description = "Rental Loss / Non-Return"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    reservation_id = fields.Many2one(
        "fix.rental.reservation",
        string="Rental",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("state", "in", LIVE_STATES)],
    )
    company_id = fields.Many2one(related="reservation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="reservation_id.operating_unit_id", store=True)
    customer_id = fields.Many2one(related="reservation_id.customer_id", store=True)
    rental_asset_id = fields.Many2one(
        related="reservation_id.rental_asset_id", store=True, string="Fleet Unit"
    )
    currency_id = fields.Many2one(related="reservation_id.currency_id")
    kind = fields.Selection(
        [("non_return", "Not Returned"), ("loss", "Lost by the Customer"), ("theft", "Stolen")],
        required=True,
        default="non_return",
        tracking=True,
    )
    circumstances = fields.Text(required=True)
    reported_at = fields.Datetime(readonly=True, copy=False)
    reported_by = fields.Many2one("res.users", readonly=True, copy=False)
    police_report_ref = fields.Char(string="Police Report (GD / FIR) No")
    valuation = fields.Monetary(
        string="Agreed Replacement Valuation",
        currency_field="currency_id",
        tracking=True,
        help="What the customer is charged for the unit; defaults to its net book value",
    )
    claim_decision = fields.Selection(
        [("claim", "Insurance Claim Raised"), ("no_claim", "Decided Not to Claim")],
        tracking=True,
    )
    claim_ref = fields.Char(string="Insurance Claim Reference")
    no_claim_reason = fields.Text(string="Why No Claim")
    escalation_stage = fields.Selection(
        [
            ("notice", "Formal Notice"),
            ("recovery", "Recovery"),
            ("legal", "Legal Escalation"),
        ],
        default="notice",
        required=True,
        readonly=True,
        tracking=True,
        copy=False,
    )
    state = fields.Selection(
        [("open", "Open"), ("recovered", "Recovered"), ("written_off", "Written Off")],
        default="open",
        required=True,
        readonly=True,
        tracking=True,
        copy=False,
    )
    recovered_on = fields.Date(readonly=True, copy=False)
    written_off_on = fields.Date(readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    forfeited_amount = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    invoiced_amount = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)

    _GUARDED = frozenset(
        {
            "state",
            "escalation_stage",
            "reported_at",
            "reported_by",
            "recovered_on",
            "written_off_on",
            "approved_by",
            "forfeited_amount",
            "invoiced_amount",
        }
    )
    _valuation_positive = models.Constraint(
        "CHECK (valuation IS NULL OR valuation >= 0)", "A valuation cannot be negative"
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked.add("reservation_id")
            if any(r.state != "open" for r in self):
                locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        Res = self.env["fix.rental.reservation"]
        for vals in vals_list:
            res = Res.browse(vals.get("reservation_id")).exists()
            if res:
                if res.state not in LIVE_STATES:
                    _refuse(
                        "A loss is reported on a rental out with the customer; %s is %s."
                        % (res.name, res.state)
                    )
                if res.loss_ids.filtered(lambda r: r.state == "open"):
                    _refuse("Rental %s already has an open loss case." % res.name)
                if "valuation" not in vals and res.rental_asset_id:
                    vals["valuation"] = res.rental_asset_id._dofa_amount()
            vals["name"] = _seq(self.env, "fix.rental.loss", "RNT-LOSS")
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write(
                {"reported_at": fields.Datetime.now(), "reported_by": self.env.uid}
            )
            rec.reservation_id.message_post(
                body="%s opened: %s." % (rec.name, dict(rec._fields["kind"].selection)[rec.kind])
            )
        return recs

    def write(self, vals):
        _final_after_create(self, self, vals, ("open",))
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            _refuse("A loss case is evidence: close it as recovered or written off.")
        return super().unlink()

    _NEXT_STAGE = {"notice": "recovery", "recovery": "legal"}

    def action_escalate(self):
        """AUT-RNT-14: formal notice → recovery → legal; each step is a to-do
        for the booker with what is due next."""
        for rec in self:
            if rec.state != "open":
                raise UserError("Loss %s is %s." % (rec.name, rec.state))
            nxt = self._NEXT_STAGE.get(rec.escalation_stage)
            if not nxt:
                raise UserError("Loss %s is already with Legal." % rec.name)
            rec._guarded().write({"escalation_stage": nxt})
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="%s escalated to %s"
                % (rec.name, dict(rec._fields["escalation_stage"].selection)[nxt]),
                user_id=rec.reservation_id.create_uid.id or self.env.uid,
            )
        return True

    def action_recover(self):
        """The unit came back: the case closes and the rental is returned as
        any other (condition report, damage, settlement). The unit was never
        anything but Company property (BRU-RNT-11)."""
        for rec in self:
            if rec.state != "open":
                raise UserError("Loss %s is %s." % (rec.name, rec.state))
            rec._guarded().write(
                {"state": "recovered", "recovered_on": fields.Date.context_today(self)}
            )
            rec.reservation_id.message_post(
                body="%s: unit recovered. Record its return, then its condition report." % rec.name
            )
        return True

    def action_request_writeoff(self, justification=None):
        """The write-off of a lost unit is the fleet unit's own routed
        write-off approval (tiered on its book value): asked here, decided in
        the approver's M63 inbox, never by the person who asked."""
        for rec in self:
            if rec.state != "open":
                raise UserError("Loss %s is %s." % (rec.name, rec.state))
            asset = rec.rental_asset_id
            if not asset:
                raise UserError(
                    "Rental %s names no fleet unit to write off." % rec.reservation_id.name
                )
            asset.action_request_approval(
                justification=justification or "%s: %s" % (rec.name, rec.circumstances)
            )
        return True

    def _writeoff_denial(self):
        self.ensure_one()
        if self.state != "open":
            return "loss %s is %s" % (self.name, self.state)
        if self.escalation_stage == "notice" and self.kind == "non_return":
            return (
                "a non-return is written off only after recovery has been attempted (escalate it)"
            )
        if self.kind == "theft" and not (self.police_report_ref or "").strip():
            return "a theft is written off only on its police report (BRU-RNT-10)"
        if not self.valuation or self.valuation <= 0:
            return "the agreed replacement valuation is missing"
        if self.claim_decision == "claim" and not (self.claim_ref or "").strip():
            return "the insurance claim reference is missing"
        if self.claim_decision == "no_claim" and not (self.no_claim_reason or "").strip():
            return "the documented decision not to claim is missing"
        if not self.claim_decision:
            return "record the insurance claim or the decision not to claim (BRU-RNT-22)"
        if self.reported_by == self.env.user:
            return "you reported this loss: another person writes it off"
        return ""

    def action_write_off(self):
        Ledger = self.env["fix.rental.deposit"]
        for rec in self:
            denial = rec._writeoff_denial()
            if denial:
                raise UserError("Loss %s cannot be written off: %s." % (rec.name, denial))
            res = rec.reservation_id
            asset = rec.rental_asset_id
            if asset:
                asset._dofa_assert_approved("Rental loss write-off")
            rec._guarded().write(
                {
                    "state": "written_off",
                    "written_off_on": fields.Date.context_today(self),
                    "approved_by": self.env.uid,
                }
            )
            held = res._ledger_balance()
            take = round(min(held, rec.valuation), 2)
            if take > 0:
                Ledger._post(res, "forfeit", take, "Forfeited against lost unit (%s)" % rec.name)
            balance = round(max(held - take, 0.0), 2)
            if balance > 0:
                Ledger._post(res, "refund", balance, "Deposit balance after loss write-off")
            excess = round(max(rec.valuation - take, 0.0), 2)
            res._guarded().write(
                {"state": "lost", "deposit_refunded": balance, "excess_billed": excess}
            )
            if excess > 0:
                res._hand_off_excess(excess)
            rec._guarded().write({"forfeited_amount": take, "invoiced_amount": excess})
            if asset:
                asset._guarded().write(
                    {"status": "lost", "retired_on": fields.Date.context_today(self)}
                )
                fa = asset.fixed_asset_id.sudo()
                if fa and fa.state == "active":
                    result = fa.action_dispose() or {}
                    ids = result.get("disposal_ids") or []
                    if ids:
                        asset._guarded().write({"disposal_id": ids[0]})
            publish(
                self.env,
                "rental.asset_lost",
                "fix.rental.loss",
                rec.id,
                {
                    "rental": res.name,
                    "asset": asset.name or "",
                    "kind": rec.kind,
                    "valuation": float(rec.valuation),
                    "claim_ref": rec.claim_ref or "",
                },
            )
        return True


# =====================================================================
# Page 7 — swap-out against the contracted SLA (FR-RNT-027)
# =====================================================================
class FixRentalSwap(models.Model):
    """In-rental replacement: a fault is answered by putting another unit in
    the customer's hands within the swap SLA. Executing it moves the rental
    to the replacement, sends the faulty unit to turnaround and records a
    condition report on both units."""

    _name = "fix.rental.swap"
    _description = "Rental Swap-Out"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    reservation_id = fields.Many2one(
        "fix.rental.reservation",
        string="Rental",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("state", "in", LIVE_STATES)],
    )
    company_id = fields.Many2one(related="reservation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="reservation_id.operating_unit_id", store=True)
    customer_id = fields.Many2one(related="reservation_id.customer_id", store=True)
    out_asset_id = fields.Many2one(
        "fix.rental.asset", string="Faulty Unit (coming back)", readonly=True, copy=False
    )
    in_asset_id = fields.Many2one(
        "fix.rental.asset",
        string="Replacement Unit",
        required=True,
        domain=[("status", "=", "available")],
    )
    fault = fields.Text(string="Fault", required=True)
    reported_at = fields.Datetime(readonly=True, copy=False)
    sla_hours = fields.Integer(string="Swap SLA (hours)", readonly=True, copy=False)
    sla_target = fields.Datetime(string="Swap Due By", readonly=True, copy=False)
    executed_at = fields.Datetime(readonly=True, copy=False)
    sla_met = fields.Boolean(string="SLA Met", readonly=True, copy=False)
    out_grade = fields.Selection(GRADES, string="Faulty Unit Grade on Receipt")
    out_notes = fields.Text(string="Faulty Unit Condition")
    in_grade = fields.Selection(GRADES, string="Replacement Grade at Dispatch")
    in_notes = fields.Text(string="Replacement Condition")
    returned_report_id = fields.Many2one(
        "fix.rental.condition", string="Report — Faulty Unit", readonly=True, copy=False
    )
    replacement_report_id = fields.Many2one(
        "fix.rental.condition", string="Report — Replacement", readonly=True, copy=False
    )
    state = fields.Selection(
        [("open", "Open"), ("executed", "Executed"), ("cancelled", "Cancelled")],
        default="open",
        required=True,
        readonly=True,
        tracking=True,
        copy=False,
    )

    _GUARDED = frozenset(
        {
            "state",
            "out_asset_id",
            "reported_at",
            "sla_hours",
            "sla_target",
            "executed_at",
            "sla_met",
            "returned_report_id",
            "replacement_report_id",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked.add("reservation_id")
            if any(r.state != "open" for r in self):
                locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        Res = self.env["fix.rental.reservation"]
        hours = policy.param_int(self.env, "swap_sla_hours", 24)
        for vals in vals_list:
            res = Res.browse(vals.get("reservation_id")).exists()
            if res and res.state not in LIVE_STATES:
                _refuse(
                    "A swap replaces a unit out with the customer; %s is %s."
                    % (res.name, res.state)
                )
            vals["name"] = _seq(self.env, "fix.rental.swap", "RNT-SWAP")
        recs = super().create(vals_list)
        now = fields.Datetime.now()
        for rec in recs:
            rec._guarded().write(
                {
                    "out_asset_id": rec.reservation_id.rental_asset_id.id,
                    "reported_at": now,
                    "sla_hours": hours,
                    "sla_target": now + timedelta(hours=hours),
                }
            )
        return recs

    def write(self, vals):
        _final_after_create(self, self, vals, ("open",))
        return super().write(vals)

    def action_execute(self):
        Cond = self.env["fix.rental.condition"].sudo()
        for rec in self:
            res = rec.reservation_id
            old, new = rec.out_asset_id, rec.in_asset_id
            if rec.state != "open":
                raise UserError("Swap %s is %s." % (rec.name, rec.state))
            if res.state not in LIVE_STATES:
                raise UserError("Rental %s is %s." % (res.name, res.state))
            if not old:
                raise UserError("Rental %s has no fleet unit to swap out." % res.name)
            if new == old:
                raise UserError("The replacement must be another unit.")
            if new.status != "available":
                raise UserError("Replacement %s is %s, not available." % (new.name, new.status))
            if res.rental_sku_id and new.rental_sku_id != res.rental_sku_id:
                raise UserError(
                    "Replacement %s is a %s; the customer rented a %s."
                    % (new.name, new.rental_sku_id.display_name, res.rental_sku_id.display_name)
                )
            if not (rec.out_grade and rec.in_grade):
                raise UserError(
                    "Grade both units before the swap: the condition of each is recorded "
                    "(FR-RNT-027)."
                )
            today = fields.Date.context_today(self)
            # availability of the replacement is the reservation's own constraint
            res._guarded().write(
                {"rental_asset_id": new.id, "device_id": new.device_id.id or False}
            )
            new._guarded().write({"status": "out"})
            old._guarded().write({"status": "maintenance"})
            self.env["fix.rental.turnaround"]._guarded().create(
                {
                    "rental_asset_id": old.id,
                    "reservation_id": res.id,
                    "company_id": res.company_id.id,
                    "returned_on": today,
                    "grade_before": rec.out_grade,
                }
            )
            common = {"reservation_id": res.id, "company_id": res.company_id.id, "swap_id": rec.id}
            returned = Cond.create(
                dict(
                    common,
                    rental_asset_id=old.id,
                    report_type="swap_in",
                    grade=rec.out_grade,
                    notes="Swap %s — fault: %s\n%s" % (rec.name, rec.fault, rec.out_notes or ""),
                    maintenance_required=True,
                )
            )
            replacement = Cond.create(
                dict(
                    common,
                    rental_asset_id=new.id,
                    report_type="swap_out",
                    grade=rec.in_grade,
                    notes="Swap %s — replacement dispatched\n%s" % (rec.name, rec.in_notes or ""),
                )
            )
            now = fields.Datetime.now()
            rec._guarded().write(
                {
                    "state": "executed",
                    "executed_at": now,
                    "sla_met": now <= rec.sla_target,
                    "returned_report_id": returned.id,
                    "replacement_report_id": replacement.id,
                }
            )
            res.message_post(
                body="Swap %s: %s replaced by %s (%s the %dh SLA)."
                % (
                    rec.name,
                    old.name,
                    new.name,
                    "within" if rec.sla_met else "OUTSIDE",
                    rec.sla_hours,
                )
            )
            publish(
                self.env,
                "rental.swap_executed",
                "fix.rental.swap",
                rec.id,
                {
                    "agreement": res.name,
                    "out_asset": old.name,
                    "in_asset": new.name,
                    "sla_met": bool(rec.sla_met),
                },
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Swap %s is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "cancelled"})
        return True


# =====================================================================
# Page 8 — preventive maintenance by calendar or usage (FR-RNT-028)
# =====================================================================
class FixRentalPmPlan(models.Model):
    """When a fleet unit is due for preventive maintenance: every N days, or
    after N days on rent since its last service, whichever comes first. A
    unit's plan is the one for its SKU, else the one for its category. The
    daily job takes due units out of availability (AUT-RNT-12)."""

    _name = "fix.rental.pm.plan"
    _description = "Rental Preventive Maintenance Plan"
    _inherit = ["mail.thread"]
    _order = "rental_sku_id, category, id"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rental_sku_id = fields.Many2one("fix.rental.sku", string="Rental SKU", ondelete="cascade")
    category = fields.Selection(ASSET_CATEGORIES, string="Fleet Category")
    interval_days = fields.Integer(string="Every (calendar days)", tracking=True)
    usage_rental_days = fields.Integer(string="Or After (days on rent)", tracking=True)
    checklist = fields.Text(string="Maintenance Checklist")
    active = fields.Boolean(default=True)

    _numbers = models.Constraint(
        "CHECK (interval_days >= 0 AND usage_rental_days >= 0)",
        "Intervals cannot be negative",
    )

    @api.constrains("rental_sku_id", "category", "interval_days", "usage_rental_days", "active")
    def _check_plan(self):
        for rec in self:
            if not (rec.rental_sku_id or rec.category):
                raise ValidationError("A PM plan applies to a rental SKU or a fleet category.")
            if not (rec.interval_days or rec.usage_rental_days):
                raise ValidationError(
                    "A PM plan says when maintenance falls due: a calendar interval, a usage "
                    "limit, or both."
                )
            if rec.active:
                dup = self.search_count(
                    [
                        ("id", "!=", rec.id),
                        ("active", "=", True),
                        ("company_id", "=", rec.company_id.id),
                        ("rental_sku_id", "=", rec.rental_sku_id.id or False),
                        ("category", "=", False if rec.rental_sku_id else rec.category),
                    ]
                )
                if dup:
                    raise ValidationError(
                        "Another active PM plan already covers this %s."
                        % ("SKU" if rec.rental_sku_id else "category")
                    )


# =====================================================================
# Page 1 — inter-branch redeployment (FR-RNT-031)
# =====================================================================
class FixRentalRedeployment(models.Model):
    """Move an available fleet unit to another branch with an M03 branch
    transfer; it is re-homed when the receiving branch confirms custody (a
    different person from whoever dispatched it). Its rental and
    utilisation history stay on the unit."""

    _name = "fix.rental.redeployment"
    _description = "Rental Fleet Redeployment"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rental_asset_id = fields.Many2one(
        "fix.rental.asset",
        string="Fleet Unit",
        required=True,
        index=True,
        domain=[("status", "=", "available")],
    )
    from_operating_unit_id = fields.Many2one(
        "operating.unit", string="From Branch", readonly=True, copy=False
    )
    to_operating_unit_id = fields.Many2one("operating.unit", string="To Branch", required=True)
    reason = fields.Text(
        string="Why (demand evidence)",
        required=True,
        help="AUT-RNT-18: the demand at the receiving branch, or the idle time at this one",
    )
    consignment_id = fields.Many2one(
        "fix.consignment", string="Branch Transfer (M03)", readonly=True, copy=False
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_transit", "In Transit"),
            ("received", "Received"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
        copy=False,
    )
    dispatched_by = fields.Many2one("res.users", readonly=True, copy=False)
    dispatched_on = fields.Datetime(readonly=True, copy=False)
    received_by = fields.Many2one("res.users", readonly=True, copy=False)
    received_on = fields.Datetime(readonly=True, copy=False)

    _GUARDED = frozenset(
        {
            "state",
            "from_operating_unit_id",
            "consignment_id",
            "dispatched_by",
            "dispatched_on",
            "received_by",
            "received_on",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(r.state != "draft" for r in self):
            locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = _seq(self.env, "fix.rental.redeployment", "RNT-RDP")
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write(
                {"from_operating_unit_id": rec.rental_asset_id.operating_unit_id.id or False}
            )
        return recs

    def write(self, vals):
        _final_after_create(self, self, vals, ("draft",))
        res = super().write(vals)
        if "rental_asset_id" in vals:
            for rec in self.filtered(lambda r: r.state == "draft"):
                rec._guarded().write(
                    {"from_operating_unit_id": rec.rental_asset_id.operating_unit_id.id or False}
                )
        return res

    def action_dispatch(self):
        Res = self.env["fix.rental.reservation"].sudo()
        for rec in self:
            asset = rec.rental_asset_id
            if rec.state != "draft":
                raise UserError("Redeployment %s is %s." % (rec.name, rec.state))
            if asset.status != "available":
                raise UserError(
                    "%s is %s: only an available unit moves branch." % (asset.name, asset.status)
                )
            if rec.to_operating_unit_id == asset.operating_unit_id:
                raise UserError(
                    "%s is already homed at %s." % (asset.name, rec.to_operating_unit_id.name)
                )
            if Res.search_count([("rental_asset_id", "=", asset.id), ("state", "in", OPEN_STATES)]):
                raise UserError(
                    "%s has open bookings at its branch: move it after them." % asset.name
                )
            ou = asset.operating_unit_id or self.env.user.default_operating_unit_id
            if not ou:
                raise UserError("%s has no home branch to dispatch it from." % asset.name)
            consignment = (
                self.env["fix.consignment"]
                .sudo()
                .create(
                    {
                        "consignment_type": "branch_transfer",
                        "scheduled_date": fields.Datetime.now(),
                        "operating_unit_id": ou.id,
                        "company_id": rec.company_id.id,
                    }
                )
            )
            asset._guarded().write({"status": "transit"})
            rec._guarded().write(
                {
                    "state": "in_transit",
                    "consignment_id": consignment.id,
                    "dispatched_by": self.env.uid,
                    "dispatched_on": fields.Datetime.now(),
                }
            )
        return True

    def action_receive(self):
        for rec in self:
            if rec.state != "in_transit":
                raise UserError("Redeployment %s is %s." % (rec.name, rec.state))
            if rec.dispatched_by == self.env.user:
                raise UserError(
                    "You dispatched %s: the receiving branch confirms its custody." % rec.name
                )
            user = self.env.user
            dest = rec.sudo().to_operating_unit_id
            if dest not in user.operating_unit_ids and not user.has_group(
                "operating_unit.group_manager_operating_unit"
            ):
                raise UserError(
                    "%s is received by a member of the receiving branch %s." % (rec.name, dest.name)
                )
            # A custody transition: the receiving clerk is checked above; the
            # unit is still homed at the sending branch, outside that clerk's
            # record rules, so the re-homing is written by the system.
            asset = rec.sudo().rental_asset_id
            asset.message_post(
                body="Re-homed from %s to %s (%s), received by %s."
                % (rec.sudo().from_operating_unit_id.name or "-", dest.name, rec.name, user.name)
            )
            asset._guarded().write({"status": "available", "operating_unit_id": dest.id})
            rec._guarded().write(
                {
                    "state": "received",
                    "received_by": self.env.uid,
                    "received_on": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "in_transit"):
                raise UserError("Redeployment %s is %s." % (rec.name, rec.state))
            if rec.state == "in_transit":
                rec.rental_asset_id._guarded().write({"status": "available"})
            rec._guarded().write({"state": "cancelled"})
        return True


# =====================================================================
# The existing models: hooks for the records above
# =====================================================================
class FixRentalAsset(models.Model):
    _inherit = "fix.rental.asset"

    status = fields.Selection(
        selection_add=[("transit", "In Transit"), ("lost", "Lost")],
        ondelete={"transit": "set default", "lost": "set default"},
    )
    redeployment_ids = fields.One2many("fix.rental.redeployment", "rental_asset_id")
    pm_plan_id = fields.Many2one("fix.rental.pm.plan", compute="_compute_pm", string="PM Plan")
    pm_due_on = fields.Date(string="PM Due On", compute="_compute_pm")
    rental_days_since_service = fields.Integer(compute="_compute_pm")

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(r.status == "lost" for r in self):
            locked |= {
                n for n, f in self._fields.items() if f.store and not n.startswith("message_")
            }
        return locked

    def _pm_plan(self):
        self.ensure_one()
        Plan = self.env["fix.rental.pm.plan"].sudo()
        dom = [("active", "=", True), ("company_id", "=", self.company_id.id)]
        return Plan.search([*dom, ("rental_sku_id", "=", self.rental_sku_id.id)], limit=1) or (
            Plan.search(
                [*dom, ("rental_sku_id", "=", False), ("category", "=", self.category)], limit=1
            )
        )

    def _compute_pm(self):
        for rec in self:
            plan = rec._pm_plan() if rec.id else self.env["fix.rental.pm.plan"]
            rec.pm_plan_id = plan
            base = rec.last_service_date or rec.acquisition_date
            due = rec.next_service_due
            if plan.interval_days and not due and base:
                due = base + timedelta(days=plan.interval_days)
            rec.pm_due_on = due
            since = rec.last_service_date
            rec.rental_days_since_service = sum(
                r.duration_days
                for r in rec.reservation_ids
                if r.state not in ("draft", "cancelled") and (not since or r.date_from >= since)
            )

    def _pm_due_reason(self, today):
        self.ensure_one()
        plan = self.pm_plan_id
        if not plan:
            return ""
        if plan.interval_days and self.pm_due_on and self.pm_due_on <= today:
            return "calendar PM due on %s" % self.pm_due_on
        if plan.usage_rental_days and self.rental_days_since_service >= plan.usage_rental_days:
            return "%d days on rent since the last service (plan: %d)" % (
                self.rental_days_since_service,
                plan.usage_rental_days,
            )
        return ""

    @api.model
    def cron_rental_pm_due(self):
        """Daily (AUT-RNT-12): an available unit whose PM has fallen due
        leaves availability; its turnaround is the maintenance work."""
        today = fields.Date.context_today(self)
        sent = self.browse()
        for asset in self.sudo().search([("status", "=", "available")]):
            reason = asset._pm_due_reason(today)
            if not reason:
                continue
            asset.action_send_to_maintenance()
            asset.message_post(
                body="Preventive maintenance due (%s): taken out of availability." % reason
            )
            sent |= asset
        return len(sent)


class FixRentalTurnaround(models.Model):
    _inherit = "fix.rental.turnaround"

    def action_ready(self):
        res = super().action_ready()
        today = fields.Date.context_today(self)
        for rec in self:
            plan = rec.rental_asset_id._pm_plan()
            if plan.interval_days:
                rec.rental_asset_id._guarded().write(
                    {"next_service_due": today + timedelta(days=plan.interval_days)}
                )
            elif plan:
                rec.rental_asset_id._guarded().write({"next_service_due": False})
        return res


class FixRentalReservation(models.Model):
    _inherit = "fix.rental.reservation"

    state = fields.Selection(
        selection_add=[("lost", "Lost / Written Off")], ondelete={"lost": "set default"}
    )
    waiver_plan_id = fields.Many2one(
        "fix.rental.waiver.plan",
        string="Damage Waiver Elected",
        ondelete="restrict",
        index=True,
        domain=[("state", "=", "published")],
        tracking=True,
        help="FR-RNT-036: the customer's election, a term of the agreement",
    )
    waiver_fee = fields.Monetary(
        string="Damage Waiver Fee",
        currency_field="currency_id",
        compute="_compute_waiver_fee",
        store=True,
    )
    agreement_version = fields.Integer(
        string="Agreement Version", default=1, readonly=True, copy=False
    )
    extension_ids = fields.One2many("fix.rental.extension", "reservation_id")
    swap_ids = fields.One2many("fix.rental.swap", "reservation_id")
    loss_ids = fields.One2many("fix.rental.loss", "reservation_id")
    exposure_override_ids = fields.One2many("fix.rental.exposure.override", "reservation_id")
    identity_verified = fields.Boolean(
        string="Identity Verified (M33)", compute="_compute_identity_verified"
    )

    @api.depends("rental_charge", "waiver_plan_id", "waiver_plan_id.fee_pct")
    def _compute_waiver_fee(self):
        for rec in self:
            pct = rec.waiver_plan_id.fee_pct if rec.waiver_plan_id else 0.0
            rec.waiver_fee = round((rec.rental_charge or 0.0) * pct / 100.0, 2)

    def _compute_identity_verified(self):
        for rec in self:
            rec.identity_verified = rec._identity_verified()

    # ---- guard & terms ------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"agreement_version"}

    def _frozen_fields(self) -> set:
        if self.state == "lost":
            return {
                name
                for name, field in self._fields.items()
                if field.store and not name.startswith(("message_", "activity_", "website_message"))
            }
        frozen = super()._frozen_fields()
        if self.agreement_state in ("sent", "signed") or self.state != "draft":
            frozen.add("waiver_plan_id")
        return frozen

    def _terms_digest(self):
        digest = super()._terms_digest()
        if self.waiver_plan_id:
            digest = hashlib.sha256(
                ("%s|waiver:%d" % (digest, self.waiver_plan_id.id)).encode()
            ).hexdigest()
        return digest

    @api.constrains("waiver_plan_id")
    def _check_waiver_plan(self):
        for rec in self.filtered("waiver_plan_id"):
            if rec.waiver_plan_id.state != "published":
                raise ValidationError(
                    "Waiver plan %s is %s: only a published plan is offered."
                    % (rec.waiver_plan_id.name, rec.waiver_plan_id.state)
                )

    def write(self, vals):
        before = {}
        if "rental_asset_id" in vals:
            before = {r.id: r.rental_asset_id for r in self}
            unit = self.env["fix.rental.asset"].browse(vals["rental_asset_id"] or []).exists()
            if unit and not self._fix_guard_open():
                for rec in self.filtered(lambda r: r.rental_asset_id != unit):
                    # FR-RNT-032 / BRU-RNT-14: the unit picked is of the SKU the
                    # customer booked, and rentable
                    if rec.rental_sku_id and unit.rental_sku_id != rec.rental_sku_id:
                        _refuse(
                            "Unit %s is a %s; booking %s is for a %s."
                            % (
                                unit.name,
                                unit.rental_sku_id.display_name,
                                rec.name,
                                rec.rental_sku_id.display_name,
                            )
                        )
                    if unit.status not in ("available", "reserved"):
                        _refuse("Unit %s is %s and cannot be allocated." % (unit.name, unit.status))
        res = super().write(vals)
        if before:
            # FR-RNT-032 allocation at pick: a unit named on a confirmed
            # booking is held for it
            for rec in self.filtered(lambda r: r.state == "reserved" and r.rental_asset_id):
                if (
                    before.get(rec.id) != rec.rental_asset_id
                    and rec.rental_asset_id.status == "available"
                ):
                    rec._set_asset_status("reserved")
        return res

    # ---- the rate ladder, reused by the extension preview ------------
    def _ladder_charge(self, days):
        self.ensure_one()
        days = max(days or 1, 1)
        if days >= 30 and self.monthly_rate:
            return (days // 30) * self.monthly_rate + (days % 30) * (
                self.daily_rate or self.monthly_rate / 30.0
            )
        if days >= 7 and self.weekly_rate:
            return (days // 7) * self.weekly_rate + (days % 7) * (
                self.daily_rate or self.weekly_rate / 7.0
            )
        return days * (self.daily_rate or 0.0)

    def _extension_denial(self, new_date_to):
        """'' when this rental's unit is free up to `new_date_to` (plus the
        turnaround padding before the next booking), else the conflict."""
        self.ensure_one()
        pad = timedelta(days=policy.param_int(self.env, "turnaround_padding_days", 1))
        Res = self.sudo()
        if self.rental_asset_id:
            clash = Res.search(
                [
                    ("rental_asset_id", "=", self.rental_asset_id.id),
                    ("state", "in", OPEN_STATES),
                    ("date_from", "<=", new_date_to + pad),
                    ("date_to", ">=", self.date_from - pad),
                    ("id", "!=", self.id),
                ],
                limit=1,
            )
            if clash:
                return "unit %s is booked from %s by %s" % (
                    self.rental_asset_id.name,
                    clash.date_from,
                    clash.name,
                )
        if self.device_id:
            clash = Res.search(
                [
                    ("device_id", "=", self.device_id.id),
                    ("state", "in", OPEN_STATES),
                    ("date_from", "<=", new_date_to),
                    ("date_to", ">=", self.date_from),
                    ("id", "!=", self.id),
                ],
                limit=1,
            )
            if clash:
                return "the device is booked from %s by %s" % (clash.date_from, clash.name)
        sku = self.rental_sku_id
        if (
            sku
            and sku.max_rental_days
            and (new_date_to - self.date_from).days + 1 > sku.max_rental_days
        ):
            return "rental SKU %s allows at most %d days" % (sku.display_name, sku.max_rental_days)
        return ""

    # ---- eligibility (FR-RNT-010, BRU-RNT-05/20) ---------------------
    def _identity_verified(self):
        self.ensure_one()
        partner = self.customer_id
        if not partner:
            return False
        today = fields.Date.context_today(self)
        return bool(
            self.env["fix.identity.document"]
            .sudo()
            .search_count(
                [
                    ("partner_id", "in", (partner | partner.commercial_partner_id).ids),
                    ("verification_status", "=", "verified"),
                    ("active", "=", True),
                    "|",
                    ("expiry_date", "=", False),
                    ("expiry_date", ">=", today),
                ]
            )
        )

    @api.model
    def _exposure_rentals(self, partner):
        if not partner:
            return self.browse()
        commercial = partner.commercial_partner_id
        return self.sudo().search(
            [
                ("customer_id", "child_of", commercial.id),
                ("state", "in", OPEN_STATES),
            ]
        )

    def _exposure_value(self):
        """The unsecured fleet value this rental puts with the customer: the
        unit's book value (for a pool booking, the dearest unit of the SKU)
        less the deposit agreed on it."""
        self.ensure_one()
        asset = self.rental_asset_id
        if asset:
            value = asset._dofa_amount() or asset.purchase_cost or 0.0
        elif self.rental_sku_id:
            units = (
                self.env["fix.rental.asset"]
                .sudo()
                .search(
                    [
                        ("rental_sku_id", "=", self.rental_sku_id.id),
                        ("status", "not in", ("retired", "lost")),
                    ]
                )
            )
            value = max([u._dofa_amount() or u.purchase_cost or 0.0 for u in units] or [0.0])
        else:
            value = 0.0
        return round(max(value - (self.deposit_collected or 0.0), 0.0), 2)

    def _exposure_check(self):
        """(limit, exposure with this booking); limit None when the party has
        no exposure limit recorded."""
        self.ensure_one()
        profile = (
            self.env["fix.rental.exposure"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", self.customer_id.commercial_partner_id.id),
                    ("company_id", "=", self.company_id.id),
                ],
                limit=1,
            )
        )
        if not profile:
            return None, 0.0
        others = self._exposure_rentals(self.customer_id) - self
        after = sum(r._exposure_value() for r in others) + self._exposure_value()
        return profile.exposure_limit, round(after, 2)

    def _assert_eligible(self):
        self.ensure_one()
        if (
            policy.param_on(self.env, "require_verified_identity", True)
            and not self._identity_verified()
        ):
            _refuse(
                "Rental %s: %s has no verified identity document in the party master (M33). "
                "Rental to an unverified party is not permitted (BRU-RNT-20)."
                % (self.name, self.customer_id.display_name)
            )
        limit, after = self._exposure_check()
        if limit is None or after <= limit + 0.005:
            return
        approved = self.exposure_override_ids.filtered(lambda o: o.state == "approved")
        if approved and after <= limit + max(approved.mapped("excess")) + 0.005:
            return
        _refuse(
            "Rental %s would take %s to an open exposure of %.2f, above its limit of %.2f "
            "(FR-RNT-010). Request an exposure override with the justification; another person "
            "approves it (BRU-RNT-05)."
            % (self.name, self.customer_id.commercial_partner_id.name, after, limit)
        )

    # ---- gates ----------------------------------------------------------
    def _gate_reserved(self):
        super()._gate_reserved()
        asset = self.rental_asset_id
        if asset and asset.status in ("transit", "lost"):
            _refuse("Fleet asset %s is %s and cannot be reserved" % (asset.name, asset.status))
        self._assert_eligible()

    def _photo_minimum(self):
        return policy.param_int(self.env, "condition_photo_minimum", 1)

    def _require_photos(self, report_type, step):
        minimum = self._photo_minimum()
        if not minimum:
            return
        photos = self.condition_ids.filtered(lambda c: c.report_type == report_type).mapped(
            "photo_ids"
        )
        if len(photos) < minimum:
            _refuse(
                "Rental %s cannot be %s: its %s condition report carries %d photograph(s); at "
                "least %d are required (BRU-RNT-01). Add them with Add a Condition Photograph."
                % (self.name, step, report_type.replace("_", "-"), len(photos), minimum)
            )

    def _gate_delivered(self):
        super()._gate_delivered()
        self._require_photos("pre_delivery", "handed over")
        self.condition_ids.filtered(lambda c: c.report_type == "pre_delivery").mapped(
            "photo_ids"
        )._seal_documents()

    def _gate_damage_assess(self):
        super()._gate_damage_assess()
        if self._return_inspection_required():
            self._require_photos("post_return", "assessed")

    def _gate_closed(self):
        super()._gate_closed()
        if self._return_inspection_required():
            self._require_photos("post_return", "closed")
        self.condition_ids.filtered(lambda c: c.report_type == "post_return").mapped(
            "photo_ids"
        )._seal_documents()

    def _validate_transition(self, new_state):
        if new_state == "lost":
            self.ensure_one()
            if self.state not in LIVE_STATES:
                _refuse(
                    "Rental %s is %s: only a rental out on hire is lost." % (self.name, self.state)
                )
            if not self.loss_ids.filtered(lambda r: r.state == "written_off"):
                _refuse(
                    "Rental %s is marked lost only by the write-off of its loss case." % self.name
                )
            return
        return super()._validate_transition(new_state)


class FixRentalDamage(models.Model):
    _inherit = "fix.rental.damage"

    waiver_exclusion = fields.Selection(
        [
            ("none", "None — covered if the plan covers it"),
            ("negligence", "Gross negligence"),
            ("deliberate", "Deliberate damage"),
            ("misuse", "Use outside the agreed purpose"),
        ],
        string="Waiver Exclusion (BRU-RNT-10)",
        default="none",
        required=True,
    )
    police_report_ref = fields.Char(
        string="Police Report (theft)",
        help="BRU-RNT-10: a theft is covered by the waiver only on a police report",
    )
    waiver_relief = fields.Monetary(
        string="Waived by the Damage Waiver",
        currency_field="currency_id",
        compute="_compute_waiver_relief",
        store=True,
        help="Cost above the elected plan's excess, when the damage is covered",
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"waiver_relief"}

    @api.depends(
        "cost",
        "category",
        "waiver_exclusion",
        "police_report_ref",
        "reservation_id.waiver_plan_id",
    )
    def _compute_waiver_relief(self):
        for rec in self:
            plan = rec.reservation_id.waiver_plan_id
            relief = 0.0
            covered = bool(plan) and rec.waiver_exclusion == "none"
            if covered and rec.category == "lost":
                covered = plan.covers_theft and bool((rec.police_report_ref or "").strip())
            if covered and rec.category == "accessory":
                covered = plan.covers_accessories
            if covered:
                relief = max((rec.cost or 0.0) - (plan.excess_amount or 0.0), 0.0)
            rec.waiver_relief = round(relief, 2)

    @api.depends("cost", "recovered_amount", "waived_amount", "waiver_relief")
    def _compute_unrecovered(self):
        for rec in self:
            rec.unrecovered_loss_amount = max(
                (rec.cost or 0.0)
                - (rec.recovered_amount or 0.0)
                - (rec.waived_amount or 0.0)
                - (rec.waiver_relief or 0.0),
                0.0,
            )
            rec.settled = rec.unrecovered_loss_amount <= 0.005

    def _chargeable(self):
        self.ensure_one()
        return round(
            max(
                (self.cost or 0.0) - (self.waived_amount or 0.0) - (self.waiver_relief or 0.0), 0.0
            ),
            2,
        )

    @api.depends("cost", "recovered_amount", "waived_amount", "waiver_relief")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return max(
            (self.cost or 0.0)
            - (self.recovered_amount or 0.0)
            - (self.waived_amount or 0.0)
            - (self.waiver_relief or 0.0),
            0.0,
        )
