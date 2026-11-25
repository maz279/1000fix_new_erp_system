# fix_facility_capture — M47 capture audit (2026-11-17).
#
# The audit found sub-module pages whose records could not be captured
# because the record did not exist at all (spec §5, §10.1):
#   * Statutory Compliance: a renewal was only a new licence row. Who was
#     responsible, when it was submitted, the fee challan, the inspection and
#     the cost were recorded nowhere (FR-FAC-021 P0), and the licence itself
#     held no issuing authority, fee or responsible person (FR-FAC-016 P0);
#   * Lease Administration: only the renewal-notice deadline and the end date
#     were dated. A rent review, a break option, a deposit return or a
#     landlord obligation had no record, owner or decision (FR-FAC-009/010 P0);
#   * Utilities: a "utility account" was a monthly bill. The supply account,
#     meter, tariff and billing cycle were held nowhere (FR-FAC-038 P0);
#   * Infrastructure Assets: no outage record, so branch operating hours lost
#     to a failed building service were unknown (FR-FAC-027 P0);
#   * Building PM: no generator / UPS test regime - load test, run hours, fuel
#     level, battery condition - and a missed test escalated to nobody
#     (FR-FAC-026 P0, BRU-FAC-10, AUT-FAC-11);
#   * Site Register: no site-type profile, so the compliance set a site type
#     requires was one estate-wide parameter (FR-FAC-002/017 P0, BRU-FAC-01:
#     "a fire licence where required by site type").
from datetime import datetime, timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_facility import dhaka_today
from .fix_facility_ops import _PERIOD_RE, BRANCH_LEAD, FACILITY_MANAGER, LEASE_ALERT_DAYS

OPS_DIRECTOR = "cd_facility.group_operations_director"
# no CFO group exists: DOFA Tier 4 "CFO / CCO / COO", as for the renewal decision
CFO_TIER = "cd_entity_config.group_dofa_tier_4"
_ROLE_LABELS = {
    FACILITY_MANAGER: "Facility Manager",
    BRANCH_LEAD: "Branch Operations Lead",
    OPS_DIRECTOR: "Operations Director",
    CFO_TIER: "CFO (DOFA Tier 4)",
}

# BRU-FAC-10: the spec names a test regime for generators and UPS but gives no
# interval. 30 days is a DEFAULT THE BUSINESS MUST CONFIRM, set without code.
POWER_TEST_INTERVAL_PARAM = "cd_facility.power_test_interval_days"
POWER_TEST_INTERVAL_DEFAULT = 30
POWER_ASSET_TYPES = ("generator", "ups")

# What a site-type profile can add to the trade licence every site holds.
PROFILE_LICENCE_FLAGS = (
    ("req_fire", "fire"),
    ("req_health", "health"),
    ("req_environment", "environment"),
    ("req_signage", "signage"),
    ("req_generator", "generator"),
)


def _require(env, group, what):
    if env.su or env.user.has_group(group):
        return
    raise UserError("%s is done by a %s." % (what, _ROLE_LABELS.get(group, group)))


def _reason(text, what):
    text = (text or "").strip()
    if not text:
        raise UserError("Say why: %s needs a reason." % what)
    return text


def _money(value, what):
    if (value or 0.0) < 0:
        raise ValidationError("%s cannot be negative." % what)


def _pct(value, what):
    if value and not 0.0 <= value <= 100.0:
        raise ValidationError("%s is a percentage between 0 and 100." % what)


def _today(record):
    return dhaka_today(record)


class FixSiteCaptureMixin(models.AbstractModel):
    """A recorded fact keeps its value. `_m47_frozen_fields` names what this
    record no longer lets anyone change; the workspace form shows it read-only
    and a direct write is refused. Transitions and superuser code are trusted."""

    _name = "fix.site.capture.mixin"
    _description = "M47 Recorded-Fact Freeze"
    _inherit = ["fix.guarded.mixin"]

    def _m47_frozen_fields(self) -> set:
        return set()

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and isinstance(self.id, int):
            locked |= self._m47_frozen_fields()
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                changed = sorted(
                    rec._fields[name].string or name
                    for name in rec._m47_frozen_fields() & set(vals)
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                )
                if changed:
                    raise UserError(
                        "%s is recorded: %s does not change. Record a new entry instead."
                        % (rec.display_name, ", ".join(changed))
                    )
        return super().write(vals)

    def _m47_sequence(self, vals_list, code, fallback):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(code) or fallback


# --------------------------------------------------------------------------
# Site Register: the compliance set a site type requires (FR-FAC-002/017)
# --------------------------------------------------------------------------
class FixSiteTypeProfile(models.Model):
    _name = "fix.site.type.profile"
    _description = "Site Type Requirement Profile"
    _inherit = ["mail.thread"]
    _order = "site_type"

    name = fields.Char(compute="_compute_name", store=True)
    site_type = fields.Selection(
        selection=lambda self: self.env["fix.site"]._fields["site_type"].selection,
        string="Site Type",
        required=True,
        tracking=True,
    )
    req_fire = fields.Boolean(string="Fire Licence (FSCD)", default=True, tracking=True)
    req_health = fields.Boolean(string="Health / Sanitation Licence", tracking=True)
    req_environment = fields.Boolean(string="Environmental Clearance", tracking=True)
    req_signage = fields.Boolean(string="Signage Permit", tracking=True)
    req_generator = fields.Boolean(string="Generator / Fuel Storage Permit", tracking=True)
    required_summary = fields.Char(string="Licences Required", compute="_compute_required_summary")
    notes = fields.Text(string="Basis (authority, local requirement)")
    active = fields.Boolean(default=True)

    @api.depends("site_type")
    def _compute_name(self):
        labels = dict(self._fields["site_type"]._description_selection(self.env))
        for rec in self:
            rec.name = "%s requirements" % labels.get(rec.site_type, rec.site_type or "")

    def _compute_required_summary(self):
        labels = dict(
            self.env["fix.site.licence"]._fields["licence_type"]._description_selection(self.env)
        )
        for rec in self:
            rec.required_summary = ", ".join(labels.get(t, t) for t in rec._m47_types())

    def _m47_types(self) -> list:
        """Every site holds a trade licence (BRU-FAC-01); the profile adds the rest."""
        self.ensure_one()
        return ["trade"] + [ltype for flag, ltype in PROFILE_LICENCE_FLAGS if self[flag]]

    @api.model
    def _m47_required_types(self, site_type):
        """The licence types a site of this type requires, or None when the
        type has no profile (the estate-wide parameter then applies)."""
        profile = self.sudo().search([("site_type", "=", site_type)], limit=1)
        return profile._m47_types() if profile else None

    @api.constrains("site_type", "active")
    def _check_one_profile_per_type(self):
        for rec in self.filtered("active"):
            if self.search_count([("site_type", "=", rec.site_type), ("id", "!=", rec.id)]):
                raise ValidationError(
                    "%s already has a requirement profile: change that one." % rec.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require(self.env, BRANCH_LEAD, "Setting what a site type requires")
        return super().create(vals_list)

    def write(self, vals):
        _require(self.env, BRANCH_LEAD, "Changing what a site type requires")
        return super().write(vals)


class FixSiteProfileGate(models.Model):
    _inherit = "fix.site"

    def _readiness_licence_types(self) -> list:
        """The readiness gate asks for the licences the site's type requires
        when that type has a profile; otherwise the estate-wide parameter."""
        if len(self) == 1 and self.site_type:
            types = self.env["fix.site.type.profile"]._m47_required_types(self.site_type)
            if types is not None:
                return types
        return super()._readiness_licence_types()


# --------------------------------------------------------------------------
# Statutory Compliance: the licence's authority, fee and owner (FR-FAC-016)
# --------------------------------------------------------------------------
class FixSiteLicenceCapture(models.Model):
    _inherit = "fix.site.licence"

    licence_type = fields.Selection(
        selection_add=[
            ("signage", "Signage Permit"),
            ("generator", "Generator / Fuel Storage Permit"),
        ],
        ondelete={"signage": "set default", "generator": "set default"},
    )
    authority = fields.Char(
        string="Issuing Authority", help="e.g. DNCC trade licence wing, FSCD Mirpur station"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    fee = fields.Monetary(currency_field="currency_id", string="Licence Fee")
    responsible_id = fields.Many2one(
        "res.users",
        string="Responsible for Renewal",
        help="Who renews it. Not the sole decider of the operating-risk exception a lapse "
        "raises (§13).",
    )
    renewal_ids = fields.One2many("fix.site.licence.renewal", "licence_id", string="Renewals")

    @api.constrains("fee")
    def _check_fee(self):
        for rec in self:
            _money(rec.fee, "A licence fee")


# --------------------------------------------------------------------------
# Statutory Compliance: a renewal in progress (FR-FAC-021, BRU-FAC-03)
# --------------------------------------------------------------------------
class FixSiteLicenceRenewal(models.Model):
    _name = "fix.site.licence.renewal"
    _description = "Site Licence Renewal"
    _inherit = ["mail.thread", "fix.site.capture.mixin"]
    _order = "initiated_on desc, id desc"

    name = fields.Char(required=True, default="New", copy=False)
    licence_id = fields.Many2one(
        "fix.site.licence",
        string="Licence Being Renewed",
        required=True,
        ondelete="restrict",
        index=True,
    )
    site_id = fields.Many2one(
        "fix.site", related="licence_id.site_id", store=True, string="Site", index=True
    )
    licence_type = fields.Selection(
        related="licence_id.licence_type", store=True, string="Licence Type"
    )
    expires_on = fields.Date(related="licence_id.valid_to", string="Expires On")
    responsible_id = fields.Many2one(
        "res.users", string="Responsible Person", required=True, ondelete="restrict"
    )
    authority = fields.Char(string="Issuing Authority")
    initiated_on = fields.Date(required=True, default=lambda self: dhaka_today(self))
    documents_assembled = fields.Boolean(
        string="Documents Assembled",
        help="Proof of occupancy (the lease), TIN, the current fire licence for a trade "
        "licence, and whatever the authority asks for.",
    )
    challan_ref = fields.Char(string="Fee Challan / Receipt Ref")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    government_fee = fields.Monetary(currency_field="currency_id", string="Government Fee")
    other_cost = fields.Monetary(currency_field="currency_id", string="Agent / Inspection Cost")
    penalty = fields.Monetary(currency_field="currency_id", string="Late Penalty")
    penalty_reason = fields.Char(string="Why a Penalty Was Paid")
    total_cost = fields.Monetary(
        currency_field="currency_id", compute="_compute_total_cost", store=True
    )
    inspection_required = fields.Boolean(string="Inspection Required")
    inspection_on = fields.Date(string="Inspected On")
    receipt_file = fields.Binary(string="Fee Receipt (scan)", attachment=True, copy=False)
    receipt_filename = fields.Char(string="Fee Receipt File Name", copy=False)
    new_licence_id = fields.Many2one(
        "fix.site.licence",
        string="Renewed Licence",
        ondelete="restrict",
        help="The new licence, recorded on Statutory Licences with its number and scan.",
    )
    state = fields.Selection(
        [
            ("initiated", "Initiated"),
            ("submitted", "Submitted"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="initiated",
        tracking=True,
    )
    submitted_on = fields.Date(readonly=True, copy=False)
    submitted_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True, copy=False)
    completed_by_id = fields.Many2one("res.users", string="Completed By", readonly=True, copy=False)
    completed_on = fields.Date(readonly=True, copy=False)
    cancel_reason = fields.Char(string="Cancellation Reason", readonly=True, copy=False)
    # A07 ERP audit (2026-11-20) M47-10 / FR-FAC-021: the fee, the agent's cost
    # and a late penalty reach accounts payable / the ledger as charges, each
    # with its payee and how it was paid. The fee and agent cost go when the
    # renewal is submitted (the challan is paid), the penalty when it completes.
    authority_partner_id = fields.Many2one(
        "res.partner",
        string="Authority (payee)",
        help="The authority the fee and any penalty are paid to (City Corporation, FSCD …)",
    )
    agent_id = fields.Many2one("res.partner", string="Agent (payee of the agent cost)")
    payment_method = fields.Selection(
        [
            ("vendor_bill", "Vendor Bill (Accounts Payable)"),
            ("petty_cash", "Petty Cash"),
            ("employee_expense", "Employee Expense Claim"),
        ],
        string="Paid By",
        default="vendor_bill",
        required=True,
    )
    employee_id = fields.Many2one("hr.employee", string="Employee Who Paid (expense claim)")
    charge_ids = fields.One2many("fix.site.charge", "renewal_id", string="Charges Raised")

    def _renewal_raise_charges(self, kinds):
        """M47-10: one confirmed charge per non-zero component, queued to M52."""
        Charge = self.env["fix.site.charge"].sudo()._guarded()
        for rec in self.sudo():
            site = rec.site_id
            parts = {
                "licence_fee": (rec.government_fee, rec.authority_partner_id),
                "licence_other": (rec.other_cost, rec.agent_id or rec.authority_partner_id),
                "licence_penalty": (rec.penalty, rec.authority_partner_id),
            }
            for kind in kinds:
                amount, payee = parts[kind]
                if (amount or 0.0) <= 0.0:
                    continue
                if rec.charge_ids.filtered(
                    lambda c, k=kind: c.kind == k and c.state != "cancelled"
                ):
                    continue
                Charge._charge_raise(
                    site,
                    kind,
                    amount,
                    renewal=rec,
                    vendor=payee or None,
                    payment_method=rec.payment_method,
                    employee=rec.employee_id or None,
                    invoice_ref=rec.challan_ref,
                    reason="%s %s (%s)"
                    % (
                        rec.name,
                        rec.licence_id.name,
                        rec.penalty_reason if kind == "licence_penalty" else rec.authority or "-",
                    ),
                )

    def _renewal_check_payment_facts(self, amounts):
        for rec in self:
            if not any((a or 0.0) > 0 for a in amounts(rec)):
                continue
            if rec.payment_method == "vendor_bill" and not rec.authority_partner_id:
                raise UserError(
                    "Name the authority %s pays (its payee in accounts payable)." % rec.name
                )
            if rec.payment_method == "employee_expense" and not rec.employee_id:
                raise UserError("Name the employee who paid the fees of %s." % rec.name)

    @api.depends("government_fee", "other_cost", "penalty")
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = (
                (rec.government_fee or 0.0) + (rec.other_cost or 0.0) + (rec.penalty or 0.0)
            )

    @api.constrains("government_fee", "other_cost", "penalty")
    def _check_costs(self):
        for rec in self:
            _money(rec.government_fee, "A government fee")
            _money(rec.other_cost, "An agent or inspection cost")
            _money(rec.penalty, "A penalty")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_on",
            "submitted_by_id",
            "completed_by_id",
            "completed_on",
            "cancel_reason",
        }

    def _m47_frozen_fields(self) -> set:
        if self.state in ("completed", "cancelled"):
            return {
                "licence_id",
                "responsible_id",
                "authority",
                "initiated_on",
                "documents_assembled",
                "challan_ref",
                "government_fee",
                "other_cost",
                "penalty",
                "penalty_reason",
                "inspection_required",
                "inspection_on",
                "receipt_file",
                "receipt_filename",
                "new_licence_id",
                "authority_partner_id",
                "agent_id",
                "payment_method",
                "employee_id",
            }
        if self.state == "submitted":
            # the fee and the agent cost went to accounts payable at submission
            return {
                "licence_id",
                "government_fee",
                "other_cost",
                "challan_ref",
                "authority_partner_id",
                "agent_id",
                "payment_method",
                "employee_id",
            }
        return {"licence_id"}

    def _m47_check_fire_first(self):
        """BRU-FAC-03 / AUT-FAC-02: a trade licence renewal is neither opened
        nor submitted while the site's fire licence is expired."""
        Licence = self.env["fix.site.licence"].sudo()
        for rec in self.filtered(lambda r: r.licence_type == "trade"):
            fire = Licence.search([("site_id", "=", rec.site_id.id), ("licence_type", "=", "fire")])
            if fire and not fire.filtered("is_valid"):
                raise UserError(
                    "The fire licence of %s has expired: a trade licence renewal cannot be "
                    "scheduled or submitted until it is renewed (BRU-FAC-03). Open the fire "
                    "licence renewal first." % rec.site_id.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require(self.env, FACILITY_MANAGER, "Opening a licence renewal")
        self._m47_sequence(vals_list, "fix.site.licence.renewal", "SLREN/New")
        Licence = self.env["fix.site.licence"].sudo()
        for vals in vals_list:
            licence = Licence.browse(vals.get("licence_id")).exists()
            if not licence:
                continue
            if licence.site_id.state == "closed":
                raise UserError(
                    "%s is closed: its licences are surrendered." % licence.site_id.name
                )
            if self.sudo().search_count(
                [("licence_id", "=", licence.id), ("state", "in", ("initiated", "submitted"))]
            ):
                raise UserError(
                    "%s already has a renewal in progress: continue that one." % licence.name
                )
            if not vals.get("authority") and licence.authority:
                vals["authority"] = licence.authority
        records = super().create(vals_list)
        records._m47_check_fire_first()
        return records

    def action_submit(self):
        """Initiated -> submitted to the authority, documents and fee in hand."""
        _require(self.env, FACILITY_MANAGER, "Submitting a licence renewal")
        for rec in self:
            if rec.state != "initiated":
                raise UserError("Submit an initiated renewal.")
            if not rec.documents_assembled:
                raise UserError(
                    "Assemble the documents for %s (occupancy proof, TIN and, for a trade "
                    "licence, the current fire licence) and tick Documents Assembled first."
                    % rec.name
                )
            if rec.government_fee and not (rec.challan_ref or "").strip():
                raise UserError("Record the fee challan or receipt reference of %s." % rec.name)
        self._renewal_check_payment_facts(lambda r: (r.government_fee, r.other_cost))
        self._m47_check_fire_first()
        for rec in self:
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_on": _today(rec),
                    "submitted_by_id": self.env.uid,
                }
            )
        self._renewal_raise_charges(("licence_fee", "licence_other"))
        return True

    def action_complete(self):
        """Submitted -> completed: the new licence is on the register for the
        same site and type, current, with its scan (§8.2 "new licence issued,
        evidence uploaded"). A late penalty is completed by someone other than
        the person responsible (§13: the lapse is not cleared by its owner)."""
        _require(self.env, FACILITY_MANAGER, "Completing a licence renewal")
        today = _today(self)
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Complete a submitted renewal.")
            old = rec.licence_id.sudo()
            new = rec.new_licence_id.sudo()
            if not new:
                raise UserError(
                    "Record the renewed licence on Statutory Licences, with its number and "
                    "scan, and choose it as the Renewed Licence first."
                )
            if new == old or new.site_id != old.site_id or new.licence_type != old.licence_type:
                raise UserError(
                    "The renewed licence must be a new %s of %s."
                    % (
                        dict(old._fields["licence_type"]._description_selection(self.env)).get(
                            old.licence_type
                        ),
                        old.site_id.name,
                    )
                )
            if not new.is_valid:
                raise UserError("%s is not current." % new.name)
            if old.valid_to and new.valid_to <= old.valid_to:
                raise UserError(
                    "%s runs to %s, no later than the licence it renews (%s)."
                    % (new.name, new.valid_to, old.valid_to)
                )
            if new._licence_evidence_required() and not new.evidence_file:
                raise UserError("%s has no scan attached." % new.name)
            if rec.inspection_required and not rec.inspection_on:
                raise UserError("Record the inspection date of %s." % rec.name)
            if rec.inspection_on and rec.inspection_on > today:
                raise UserError("An inspection cannot be recorded in the future.")
            if rec.penalty and not (rec.penalty_reason or "").strip():
                raise UserError("Say why a late penalty of %s was paid." % rec.penalty)
            if not self.env.su and rec.penalty and rec.responsible_id == self.env.user:
                raise UserError(
                    "Segregation of duties: a penalty arose from your renewal; another "
                    "Facility Manager completes it."
                )
            rec._renewal_check_payment_facts(lambda r: (r.penalty,))
            rec._guarded().write(
                {"state": "completed", "completed_by_id": self.env.uid, "completed_on": today}
            )
            # M47-10: the late penalty is owed (the fee went at submission)
            rec._renewal_raise_charges(("licence_fee", "licence_other", "licence_penalty"))
            rec.message_post(
                body="Renewed by %s (valid to %s); total cost %.2f."
                % (new.name, new.valid_to, rec.total_cost)
            )
        return True

    def action_cancel(self, reason=None):
        _require(self.env, FACILITY_MANAGER, "Cancelling a licence renewal")
        reason = _reason(reason, "cancelling the renewal")
        for rec in self:
            if rec.state not in ("initiated", "submitted"):
                raise UserError("Cancel a renewal that is still in progress.")
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason})
            rec.message_post(body="Cancelled by %s: %s" % (self.env.user.name, reason))
        return True


class FixSiteRiskExceptionRenewal(models.Model):
    _inherit = "fix.site.risk.exception"

    def _exception_check_decider(self):
        """§13 SoD: the licence's responsible person and whoever is
        responsible for its renewal do not decide the exception either."""
        super()._exception_check_decider()
        if self.env.su:
            return
        Renewal = self.env["fix.site.licence.renewal"].sudo()
        for rec in self:
            licence = rec.licence_id.sudo()
            responsible = licence.responsible_id | Renewal.search(
                [("licence_id", "=", licence.id)]
            ).mapped("responsible_id")
            if self.env.user in responsible:
                raise UserError(
                    "Segregation of duties: you are responsible for renewing %s; another "
                    "person decides its operating-risk exception." % licence.name
                )


# --------------------------------------------------------------------------
# Lease Administration: the dated obligations of a lease (FR-FAC-009/010)
# --------------------------------------------------------------------------
LEASE_EVENT_TYPES = [
    ("rent_review", "Rent Review"),
    ("break_option", "Break Option"),
    ("deposit_return", "Deposit Return"),
    ("landlord_obligation", "Landlord Obligation"),
    ("other", "Other Obligation"),
]
# a review or a break is a commercial decision (the CFO's, as the renewal
# decision, BRU-FAC-05); the rest is an obligation met by its owner
LEASE_DECISION_EVENTS = ("rent_review", "break_option")


class FixSiteLeaseEvent(models.Model):
    _name = "fix.site.lease.event"
    _description = "Lease Critical Event"
    _inherit = ["mail.thread", "fix.site.capture.mixin"]
    _order = "due_on, id"

    name = fields.Char(required=True, default="New", copy=False)
    lease_id = fields.Many2one(
        "fix.site.lease", string="Lease", required=True, ondelete="cascade", index=True
    )
    site_id = fields.Many2one(
        "fix.site", related="lease_id.site_id", store=True, string="Site", index=True
    )
    event_type = fields.Selection(LEASE_EVENT_TYPES, required=True, default="rent_review")
    due_on = fields.Date(string="Due On", required=True)
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", required=True, ondelete="restrict"
    )
    description = fields.Text(string="What the Lease Says")
    currency_id = fields.Many2one(related="lease_id.currency_id")
    amount = fields.Monetary(
        currency_field="currency_id",
        string="Amount Involved",
        help="The rent proposed at review, the penalty of a break, the deposit to recover.",
    )
    state = fields.Selection(
        [("open", "Open"), ("done", "Decided / Met"), ("cancelled", "Cancelled")],
        required=True,
        default="open",
        tracking=True,
    )
    decision = fields.Selection(
        [
            ("exercise", "Exercise / Proceed"),
            ("decline", "Do Not Exercise / Waive"),
            ("met", "Obligation Met"),
        ],
        readonly=True,
        copy=False,
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Date(readonly=True, copy=False)
    outcome_notes = fields.Text(string="Basis / Outcome", readonly=True, copy=False)
    days_left = fields.Integer(compute="_compute_days_left")
    # cron bookkeeping: the smallest horizon already alerted (-1 = overdue)
    alert_horizon = fields.Integer(readonly=True, copy=False)

    def _compute_days_left(self):
        today = _today(self)
        for rec in self:
            rec.days_left = (rec.due_on - today).days if rec.due_on else 0

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            _money(rec.amount, "An amount")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "decision",
            "decided_by_id",
            "decided_on",
            "outcome_notes",
            "alert_horizon",
        }

    def _m47_frozen_fields(self) -> set:
        if self.state != "open":
            return {"lease_id", "event_type", "due_on", "responsible_id", "description", "amount"}
        return {"lease_id", "event_type"}

    @api.model_create_multi
    def create(self, vals_list):
        _require(self.env, FACILITY_MANAGER, "Recording a lease critical event")
        self._m47_sequence(vals_list, "fix.site.lease.event", "SLEV/New")
        Lease = self.env["fix.site.lease"].sudo()
        for vals in vals_list:
            lease = Lease.browse(vals.get("lease_id")).exists()
            if not lease:
                continue
            # the termination consumer opens the deposit return itself (M47-17)
            if lease.state == "terminated" and not self._fix_guard_open():
                raise UserError("%s is terminated: it has no obligations left." % lease.name)
            due = fields.Date.to_date(vals.get("due_on"))
            if due and lease.start_date and due < lease.start_date:
                raise UserError(
                    "%s starts on %s: an event cannot fall before it."
                    % (lease.name, lease.start_date)
                )
            if (
                vals.get("event_type") in ("landlord_obligation", "other")
                and not (vals.get("description") or "").strip()
            ):
                raise UserError("Say what the lease obliges.")
        return super().create(vals_list)

    def write(self, vals):
        # a re-dated event is alerted again from its new date (the form posts
        # the date it shows: only a real change restarts the alerts)
        redated = (
            self.filtered(lambda r: fields.Date.to_date(vals["due_on"]) != r.due_on)
            if "due_on" in vals and not self._fix_guard_has_token()
            else self.browse()
        )
        result = super().write(vals)
        if redated:
            redated.sudo()._guarded().write({"alert_horizon": 0})
        return result

    def _decide(self, decision, notes):
        notes = _reason(notes, "recording the outcome")
        today = _today(self)
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is not open." % rec.name)
            commercial = rec.event_type in LEASE_DECISION_EVENTS
            if commercial and decision == "met":
                raise UserError(
                    "A %s is decided: exercise it or not."
                    % dict(LEASE_EVENT_TYPES)[rec.event_type].lower()
                )
            if not commercial and decision == "exercise":
                raise UserError(
                    "%s is an obligation: mark it met, or waive it with the reason." % rec.name
                )
            if not self.env.su:
                if commercial:
                    _require(self.env, CFO_TIER, "Deciding a rent review or break option")
                elif not (
                    self.env.user == rec.responsible_id or self.env.user.has_group(BRANCH_LEAD)
                ):
                    raise UserError(
                        "%s is met by its responsible person or a Branch Operations Lead."
                        % rec.name
                    )
                if self.env.user == rec.create_uid:
                    raise UserError(
                        "Segregation of duties: you recorded %s; another person decides it."
                        % rec.name
                    )
            # a service write after the checks above: the CFO (or the owner)
            # decides without holding an M47 write right on the event
            rec.sudo()._guarded().write(
                {
                    "state": "done",
                    "decision": decision,
                    "decided_by_id": self.env.uid,
                    "decided_on": today,
                    "outcome_notes": notes,
                }
            )
        return True

    def action_decide_exercise(self, notes=None):
        return self._decide("exercise", notes)

    def action_decide_decline(self, notes=None):
        return self._decide("decline", notes)

    def action_mark_met(self, notes=None):
        return self._decide("met", notes)

    def action_cancel(self, reason=None):
        _require(self.env, FACILITY_MANAGER, "Cancelling a lease critical event")
        reason = _reason(reason, "cancelling the event")
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is not open." % rec.name)
            rec._guarded().write({"state": "cancelled", "outcome_notes": reason})
        return True

    @api.model
    def cron_lease_event_alerts(self):
        """Daily (AUT-FAC-04): alert the responsible role at 90/60/30/15/7
        days and once when an open event passes its date. Idempotent."""
        today = _today(self)
        for rec in self.sudo().search([("state", "=", "open")]):
            days = (rec.due_on - today).days
            if days < 0:
                horizon = -1
            else:
                due = [h for h in LEASE_ALERT_DAYS if days <= h]
                if not due:
                    continue
                horizon = min(due)
            if rec.alert_horizon and (rec.alert_horizon == -1 or rec.alert_horizon <= horizon):
                continue
            publish(
                self.env,
                "lease.critical_date_due",
                "fix.site.lease.event",
                rec.id,
                {
                    "lease": rec.lease_id.name,
                    "site": rec.site_id.name,
                    "event_type": rec.event_type,
                    "due_on": str(rec.due_on),
                    "days_left": days,
                    "responsible_role": "CFO"
                    if rec.event_type in LEASE_DECISION_EVENTS
                    else rec.responsible_id.name,
                },
            )
            rec._guarded().write({"alert_horizon": horizon})
        return True


# --------------------------------------------------------------------------
# Utilities: the supply account and its meter (FR-FAC-038)
# --------------------------------------------------------------------------
UTILITY_TYPES = [
    ("power", "Electricity"),
    ("water", "Water"),
    ("gas", "Gas"),
    ("internet", "Internet"),
    ("phone", "Telephony"),
]


class FixSiteUtilityAccount(models.Model):
    _name = "fix.site.utility.account"
    _description = "Site Utility Supply Account"
    _inherit = ["mail.thread", "fix.site.capture.mixin"]
    _order = "site_id, utility_type, name"

    name = fields.Char(required=True, default="New", copy=False)
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    utility_type = fields.Selection(UTILITY_TYPES, required=True, default="power")
    provider_id = fields.Many2one(
        "res.partner", string="Provider", required=True, help="DESCO, DPDC, WASA, Titas, the ISP"
    )
    account_no = fields.Char(string="Account / Customer No", required=True)
    meter_no = fields.Char(string="Meter Identifier")
    tariff = fields.Char(string="Tariff", help="e.g. LT-E commercial")
    billing_cycle = fields.Selection(
        [("monthly", "Monthly"), ("bimonthly", "Every Two Months"), ("quarterly", "Quarterly")],
        default="monthly",
        required=True,
    )
    connection_capacity = fields.Char(string="Connection Capacity", help="e.g. 20 kW, 50 Mbps")
    active_from = fields.Date(required=True, default=lambda self: dhaka_today(self))
    state = fields.Selection(
        [("active", "Active"), ("closed", "Closed")], required=True, default="active", tracking=True
    )
    closed_on = fields.Date(readonly=True, copy=False)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    close_reason = fields.Char(readonly=True, copy=False)
    notes = fields.Char()
    bill_ids = fields.One2many("fix.site.utility", "account_id", string="Bills")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "closed_on",
            "closed_by_id",
            "close_reason",
        }

    def _m47_frozen_fields(self) -> set:
        # a different provider, account or site is a different account
        return {"site_id", "utility_type", "provider_id", "account_no"}

    @api.constrains("provider_id", "utility_type", "account_no")
    def _check_unique_account(self):
        for rec in self:
            number = (rec.account_no or "").strip()
            if not number:
                raise ValidationError("Record the account number.")
            twin = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("provider_id", "=", rec.provider_id.id),
                    ("utility_type", "=", rec.utility_type),
                    ("account_no", "=ilike", number),
                ],
                limit=1,
            )
            if twin:
                raise ValidationError(
                    "%s account %s is already registered as %s (%s)."
                    % (rec.provider_id.name, number, twin.name, twin.site_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require(self.env, FACILITY_MANAGER, "Registering a utility account")
        self._m47_sequence(vals_list, "fix.site.utility.account", "SUACC/New")
        return super().create(vals_list)

    def action_close(self, reason=None):
        _require(self.env, FACILITY_MANAGER, "Closing a utility account")
        reason = _reason(reason, "closing the account")
        for rec in self:
            if rec.state != "active":
                raise UserError("%s is already closed." % rec.name)
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_on": _today(rec),
                    "closed_by_id": self.env.uid,
                    "close_reason": reason,
                }
            )
        return True


class FixSiteUtilityBillAccount(models.Model):
    _inherit = "fix.site.utility"
    _description = "Site Utility Bill"

    utility_type = fields.Selection(
        selection_add=[("phone", "Telephony")], ondelete={"phone": "set default"}
    )
    account_id = fields.Many2one(
        "fix.site.utility.account",
        string="Utility Account",
        ondelete="restrict",
        index=True,
        help="The supply account (meter) billed. Filled in when the site holds one active "
        "account of the type.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        Account = self.env["fix.site.utility.account"].sudo()
        for vals in vals_list:
            if vals.get("account_id") or not vals.get("site_id"):
                continue
            accounts = Account.search(
                [
                    ("site_id", "=", vals["site_id"]),
                    ("utility_type", "=", vals.get("utility_type") or "power"),
                    ("state", "=", "active"),
                ]
            )
            if len(accounts) == 1:
                vals["account_id"] = accounts.id
            elif len(accounts) > 1 and not self._fix_guard_open():
                raise UserError(
                    "The site has %d active accounts of this utility: choose the account "
                    "(meter) this bill is for." % len(accounts)
                )
        return super().create(vals_list)

    @api.constrains("account_id", "site_id", "utility_type")
    def _check_bill_account(self):
        for rec in self.filtered("account_id"):
            account = rec.account_id.sudo()
            if account.site_id != rec.site_id or account.utility_type != rec.utility_type:
                raise ValidationError(
                    "%s is a %s account of %s, not of this bill."
                    % (account.name, account.utility_type, account.site_id.name)
                )

    @api.constrains("site_id", "utility_type", "period", "account_id")
    def _check_one_bill_per_period(self):
        """One bill per account (meter) and month, so a site with two meters
        of one utility bills both; a bill with no account keeps the original
        rule of one bill per site, utility type and month."""
        unmetered = self.filtered(lambda r: not r.account_id)
        if unmetered:
            super(FixSiteUtilityBillAccount, unmetered)._check_one_bill_per_period()
        for rec in self - unmetered:
            if not _PERIOD_RE.match(rec.period or ""):
                raise ValidationError(
                    "Utility period %r must be a calendar month written YYYY-MM." % rec.period
                )
            account = rec.account_id.sudo()
            if (
                account.state == "closed"
                and account.closed_on
                and rec.period > account.closed_on.strftime("%Y-%m")
            ):
                raise ValidationError(
                    "%s was closed on %s: it bills nothing after that."
                    % (account.name, account.closed_on)
                )
            if self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("account_id", "=", account.id),
                    ("period", "=", rec.period),
                ]
            ):
                raise ValidationError(
                    "%s already has a bill for %s. Correct that bill instead of recording "
                    "a second one." % (account.name, rec.period)
                )


# --------------------------------------------------------------------------
# Infrastructure Assets: identity (FR-FAC-024) and outages (FR-FAC-027)
# --------------------------------------------------------------------------
class FixSiteAssetIdentity(models.Model):
    _inherit = "fix.site.asset"

    make = fields.Char(string="Make")
    model_name = fields.Char(string="Model")
    capacity = fields.Char(string="Capacity", help="e.g. 60 kVA, 10 kVA, 5 TR")
    expected_life_months = fields.Integer(string="Expected Life (months)")
    power_test_ids = fields.One2many("fix.site.power.test", "asset_id", string="Power Tests")
    last_power_test_on = fields.Date(string="Last Power Test", compute="_compute_power_test")
    power_test_due_on = fields.Date(string="Power Test Due", compute="_compute_power_test")
    # cron bookkeeping: the due date already escalated (BRU-FAC-10)
    power_alerted_for = fields.Date(readonly=True, copy=False)

    @api.constrains("expected_life_months")
    def _check_life(self):
        for rec in self:
            if rec.expected_life_months < 0:
                raise ValidationError("An expected life cannot be negative.")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"power_alerted_for"}

    @api.model
    def _m47_power_interval(self) -> int:
        raw = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(POWER_TEST_INTERVAL_PARAM, str(POWER_TEST_INTERVAL_DEFAULT))
        )
        try:
            days = int(str(raw).strip())
        except ValueError:
            return POWER_TEST_INTERVAL_DEFAULT
        return days if days > 0 else POWER_TEST_INTERVAL_DEFAULT

    def _compute_power_test(self):
        interval = self._m47_power_interval()
        for rec in self:
            if rec.asset_type not in POWER_ASSET_TYPES or not isinstance(rec.id, int):
                rec.last_power_test_on = False
                rec.power_test_due_on = False
                continue
            last = max(rec.sudo().power_test_ids.mapped("tested_on") or [False]) or False
            start = last or rec.installed_on or fields.Date.to_date(rec.create_date)
            rec.last_power_test_on = last
            rec.power_test_due_on = start + timedelta(days=interval) if start else False

    @api.model
    def cron_power_test_due(self):
        """Daily (AUT-FAC-11, BRU-FAC-10): a generator or UPS in service at an
        operational site whose test is overdue escalates to the Operations
        Director, once per due date."""
        today = _today(self)
        for rec in self.sudo().search(
            [
                ("asset_type", "in", POWER_ASSET_TYPES),
                ("state", "=", "operational"),
                ("site_id.state", "=", "active"),
            ]
        ):
            due = rec.power_test_due_on
            if not due or due >= today or rec.power_alerted_for == due:
                continue
            publish(
                self.env,
                "site.power_test_overdue",
                "fix.site.asset",
                rec.id,
                {
                    "asset": rec.name,
                    "asset_type": rec.asset_type,
                    "site": rec.site_id.name,
                    "site_id": rec.site_id.id,
                    "due_on": str(due),
                    "last_test_on": str(rec.last_power_test_on) if rec.last_power_test_on else None,
                    "days_overdue": (today - due).days,
                },
            )
            rec._guarded().write({"power_alerted_for": due})
        return True


OUTAGE_SERVICES = [
    ("power", "Grid Power"),
    ("generator", "Generator"),
    ("ups", "UPS"),
    ("hvac", "Air Conditioning"),
    ("water", "Water"),
    ("connectivity", "Connectivity"),
    ("lift", "Lift"),
    ("other", "Other"),
]


class FixSiteOutage(models.Model):
    _name = "fix.site.outage"
    _description = "Infrastructure Outage"
    _inherit = ["fix.site.capture.mixin"]
    _order = "started_at desc, id desc"

    name = fields.Char(required=True, default="New", copy=False)
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    service = fields.Selection(OUTAGE_SERVICES, string="Service Lost", required=True)
    asset_id = fields.Many2one(
        "fix.site.asset", string="Asset That Failed", ondelete="restrict", index=True
    )
    started_at = fields.Datetime(string="Started", required=True, default=fields.Datetime.now)
    ended_at = fields.Datetime(string="Ended", readonly=True, copy=False)
    cause = fields.Text(required=True)
    branch_stopped = fields.Boolean(
        string="Branch Could Not Operate",
        help="The counter or workshop stopped: the duration counts as operating hours lost.",
    )
    workaround = fields.Char(string="Workaround Used")
    work_order_id = fields.Many2one(
        "fix.facility.work.order", string="Repair Work Order", ondelete="set null"
    )
    duration_hours = fields.Float(
        string="Duration (h)", compute="_compute_hours", store=True, digits=(10, 2)
    )
    operating_hours_lost = fields.Float(
        string="Operating Hours Lost", compute="_compute_hours", store=True, digits=(10, 2)
    )
    state = fields.Selection(
        [("open", "Ongoing"), ("ended", "Ended")], required=True, default="open", index=True
    )
    recorded_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True, copy=False)
    ended_by_id = fields.Many2one("res.users", string="Ended By", readonly=True, copy=False)

    @api.depends(
        "started_at",
        "ended_at",
        "branch_stopped",
        "site_id.opening_hour",
        "site_id.closing_hour",
        "site_id.weekly_off_day",
    )
    def _compute_hours(self):
        for rec in self:
            hours = 0.0
            if rec.started_at and rec.ended_at:
                hours = max((rec.ended_at - rec.started_at).total_seconds() / 3600.0, 0.0)
            rec.duration_hours = round(hours, 2)
            # A07 ERP audit (2026-11-20) M47-24: only the hours the branch was
            # open count as operating hours lost (a night outage loses none)
            lost = 0.0
            if rec.branch_stopped and hours:
                lost = rec.site_id.sudo()._site_open_hours_between(rec.started_at, rec.ended_at)
            rec.operating_hours_lost = round(lost, 2)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "ended_at",
            "ended_by_id",
            "recorded_by_id",
        }

    def _m47_frozen_fields(self) -> set:
        if self.state == "ended":
            return {"site_id", "service", "asset_id", "started_at", "cause", "branch_stopped"}
        return {"site_id"}

    @api.constrains("site_id", "asset_id", "work_order_id", "started_at")
    def _check_outage(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.asset_id and rec.asset_id.site_id != rec.site_id:
                raise ValidationError("%s is not at %s." % (rec.asset_id.name, rec.site_id.name))
            if rec.work_order_id and rec.work_order_id.site_id != rec.site_id:
                raise ValidationError(
                    "%s is a work order of another site." % rec.work_order_id.name
                )
            if rec.started_at and rec.started_at > now + timedelta(minutes=5):
                raise ValidationError("An outage cannot start in the future.")

    @api.model_create_multi
    def create(self, vals_list):
        self._m47_sequence(vals_list, "fix.site.outage", "SOUT/New")
        records = super().create(vals_list)
        records._guarded().write({"recorded_by_id": self.env.uid})
        return records

    def _m47_typed_moment(self, text):
        """A time a person typed is their wall clock (Dhaka by default); the
        database holds UTC."""
        try:
            moment = datetime.fromisoformat(str(text).strip().replace("T", " ", 1)[:19])
        except ValueError as exc:
            raise UserError("%r is not a date and time (YYYY-MM-DD HH:MM)." % text) from exc
        try:
            zone = pytz.timezone(self.env.user.tz or self.env.context.get("tz") or "Asia/Dhaka")
        except pytz.UnknownTimeZoneError:
            zone = pytz.timezone("Asia/Dhaka")
        return zone.localize(moment).astimezone(pytz.utc).replace(tzinfo=None)

    def action_end(self, ended_at=None):
        """The service is back. The duration, and for a stopped branch the
        operating hours lost, are computed; M04 and M31 are told (AUT-FAC-12)."""
        now = fields.Datetime.now()
        end = self._m47_typed_moment(ended_at) if ended_at else now
        if end > now + timedelta(minutes=5):
            raise UserError("An outage cannot end in the future.")
        for rec in self:
            if rec.state != "open":
                raise UserError("%s has already ended." % rec.name)
            if end < rec.started_at:
                raise UserError(
                    "%s started at %s: it cannot end before." % (rec.name, rec.started_at)
                )
            rec._guarded().write({"state": "ended", "ended_at": end, "ended_by_id": self.env.uid})
            publish(
                self.env,
                "site.outage",
                "fix.site.outage",
                rec.id,
                {
                    "outage": rec.name,
                    "site": rec.site_id.name,
                    "site_id": rec.site_id.id,
                    "service": rec.service,
                    "asset": rec.asset_id.name or None,
                    "started_at": str(rec.started_at),
                    "ended_at": str(rec.ended_at),
                    "duration_hours": rec.duration_hours,
                    "operating_hours_lost": rec.operating_hours_lost,
                    "branch_stopped": bool(rec.branch_stopped),
                    "cause": rec.cause,
                },
            )
        return True


# --------------------------------------------------------------------------
# Building PM: the generator / UPS test regime (FR-FAC-026, BRU-FAC-10)
# --------------------------------------------------------------------------
class FixSitePowerTest(models.Model):
    _name = "fix.site.power.test"
    _description = "Generator / UPS Test"
    _inherit = ["fix.site.capture.mixin"]
    _order = "tested_on desc, id desc"

    name = fields.Char(required=True, default="New", copy=False)
    asset_id = fields.Many2one(
        "fix.site.asset",
        string="Generator / UPS",
        required=True,
        ondelete="restrict",
        index=True,
    )
    site_id = fields.Many2one(
        "fix.site", related="asset_id.site_id", store=True, string="Site", index=True
    )
    asset_type = fields.Selection(related="asset_id.asset_type", store=True, string="Asset Type")
    tested_on = fields.Date(
        string="Tested On", required=True, default=lambda self: dhaka_today(self)
    )
    test_type = fields.Selection(
        [
            ("load_test", "Load Test"),
            ("run_test", "No-Load Run"),
            ("battery_check", "Battery Check"),
            ("fuel_check", "Fuel Check"),
        ],
        required=True,
        default="load_test",
    )
    result = fields.Selection([("pass", "Passed"), ("fail", "Failed")], required=True)
    run_hours = fields.Float(string="Hour Meter Reading")
    load_pct = fields.Float(string="Load Carried (%)")
    duration_min = fields.Integer(string="Run Duration (min)")
    fuel_level_pct = fields.Float(string="Fuel Level (%)")
    battery_condition = fields.Selection(
        [("good", "Good"), ("weak", "Weak"), ("replace", "Replace")], string="Battery Condition"
    )
    finding = fields.Text(string="What Failed / Was Found")
    tested_by_id = fields.Many2one("res.users", string="Tested By", readonly=True, copy=False)
    work_order_id = fields.Many2one(
        "fix.facility.work.order", string="Corrective Work Order", readonly=True, copy=False
    )
    notes = fields.Char()

    _TEST_FACTS = (
        "asset_id",
        "tested_on",
        "test_type",
        "result",
        "run_hours",
        "load_pct",
        "duration_min",
        "fuel_level_pct",
        "battery_condition",
        "finding",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"tested_by_id", "work_order_id"}

    def _m47_frozen_fields(self) -> set:
        # a test is what was measured on the day: a correction is a new test
        return set(self._TEST_FACTS)

    @api.constrains(*_TEST_FACTS)
    def _check_test(self):
        today = _today(self)
        for rec in self:
            asset = rec.asset_id.sudo()
            if asset.asset_type not in POWER_ASSET_TYPES:
                raise ValidationError("%s is not a generator or a UPS." % asset.name)
            if rec.tested_on and rec.tested_on > today:
                raise ValidationError("A test cannot be recorded in the future.")
            if rec.test_type in ("fuel_check", "run_test") and asset.asset_type == "ups":
                raise ValidationError(
                    "A UPS has no fuel or engine run: record a load or battery test."
                )
            if rec.result == "fail" and not (rec.finding or "").strip():
                raise ValidationError("Say what failed.")
            if rec.run_hours < 0 or rec.duration_min < 0:
                raise ValidationError("A reading cannot be negative.")
            _pct(rec.load_pct, "The load carried")
            _pct(rec.fuel_level_pct, "The fuel level")
            if rec.run_hours:
                higher = self.sudo().search(
                    [
                        ("asset_id", "=", asset.id),
                        ("id", "!=", rec.id),
                        ("tested_on", "<=", rec.tested_on),
                        ("run_hours", ">", rec.run_hours),
                    ],
                    limit=1,
                )
                if higher:
                    raise ValidationError(
                        "The hour meter of %s read %.1f on %s: it cannot go back to %.1f."
                        % (asset.name, higher.run_hours, higher.tested_on, rec.run_hours)
                    )

    @api.model_create_multi
    def create(self, vals_list):
        self._m47_sequence(vals_list, "fix.site.power.test", "SPWT/New")
        Asset = self.env["fix.site.asset"].sudo()
        for vals in vals_list:
            asset = Asset.browse(vals.get("asset_id")).exists()
            if asset and asset.state == "retired":
                raise UserError("%s is retired." % asset.name)
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"tested_by_id": self.env.uid})
            if rec.result == "fail":
                rec._m47_raise_work_order()
        return records

    def _m47_raise_work_order(self):
        """A failed test raises the corrective work order (AUT-FAC-11): the
        branch must not rely on a generator that failed its test."""
        self.ensure_one()
        site = self.site_id.sudo()
        if site.state not in ("active", "suspended"):
            return
        labels = dict(self._fields["test_type"]._description_selection(self.env))
        # A07 ERP audit (2026-11-20) M47-34: a failed generator / UPS test is
        # urgent; an emergency while the site has no grid power right now
        no_grid = (
            self.env["fix.site.outage"]
            .sudo()
            .search_count(
                [("site_id", "=", site.id), ("service", "=", "power"), ("state", "=", "open")]
            )
        )
        order = (
            self.env["fix.facility.work.order"]
            .sudo()
            ._guarded()
            .create(
                {
                    "site_id": site.id,
                    "company_id": site.company_id.id,
                    "operating_unit_id": site.operating_unit_id.id,
                    "work_type": "repair",
                    "description": "%s failed its %s on %s (%s): %s"
                    % (
                        self.asset_id.name,
                        labels.get(self.test_type, self.test_type).lower(),
                        self.tested_on,
                        self.name,
                        self.finding,
                    ),
                    "scheduled_date": self.tested_on,
                    "assigned_type": "internal",
                    "priority": "emergency" if no_grid else "high",
                    "site_asset_id": self.asset_id.id,
                }
            )
        )
        self._guarded().write({"work_order_id": order.id})
