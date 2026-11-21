# fix_tradein_ops — M14: the valuation, provenance, grading, QA, harvest and
# refurb-warranty records behind the registry screens. The trade-in request and
# its lifecycle live in fix_tradein.py; these models compose with it.
#
# A05 workflow audit (2026-11-03), M14-5/6/12/16/17/18 + P2: every verdict
# on these records (provenance clearance and its flags, the QA result, the
# harvest and warranty state, the valuation override) was a free field. Each
# is now guarded (fix.guarded.mixin) and set by its action, by the role the
# report names, never by the person whose work it checks.
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_tradein import (
    _NID_RE,
    GROUP_PROVENANCE_OFFICER,
    GROUP_QA_INSPECTOR,
    GROUP_VALUATION_MANAGER,
    GROUP_WARRANTY_OFFICER,
    PARAM_HARVEST_LOCATION,
    PARAM_QA_MIN_PASS_PCT,
    _param,
    _param_float,
    nid_placeholder,
)

_EPS = 0.005


def _assert_role(env, group, what):
    """Superuser service code is trusted; a person needs the role."""
    if env.su:
        return
    if not env.user.has_group(group):
        role = env.ref(group, raise_if_not_found=False)
        raise AccessError("%s needs the %s role." % (what, role.name if role else group))


# XC-24: the A05 DOFA ladder for trade-in valuation, payout and write-off
# (Appraisal Specialist to 50k, Service Hub Lead to 250k, Head of Circular
# Economy to 1M, CFO above), the one the payout approval already uses.
_DOFA_LADDER = ((50000.0, 1), (250000.0, 2), (1000000.0, 3), (float("inf"), 4))


def _assert_amount_tier(env, amount, what):
    """The approver's DOFA tier covers `amount` (higher tiers imply lower)."""
    if env.su or (amount or 0.0) <= 0:
        return
    tier = next(t for bound, t in _DOFA_LADDER if amount <= bound)
    group = "cd_entity_config.group_dofa_tier_%d" % tier
    if not env.user.has_group(group):
        raise AccessError(
            "%s of BDT %.2f needs DOFA tier %d authority (XC-24)." % (what, amount, tier)
        )


class FixTradeinPriceGrid(models.Model):
    """The governed market reference price of one device model (P2: a
    governed valuation grid). A row prices valuations only once a valuation
    manager other than its author approves it; an approved row is frozen and
    is replaced, not edited."""

    _name = "fix.tradein.price.grid"
    _description = "Trade-In Price Grid"
    _inherit = ["fix.guarded.mixin"]
    _order = "device_model_id, valid_from desc, id desc"

    _TERMS = frozenset({"device_model_id", "market_ref_price", "valid_from", "company_id"})

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    device_model_id = fields.Many2one(
        "fix.device.model", string="Device Model", required=True, index=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    market_ref_price = fields.Monetary(
        string="Market Reference Price", currency_field="currency_id", required=True
    )
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("retired", "Retired")],
        required=True,
        default="draft",
        readonly=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    notes = fields.Char(string="Source of the Price")

    _price_positive = models.Constraint(
        "CHECK (market_ref_price > 0)", "A grid price must be positive"
    )

    @api.depends("device_model_id", "valid_from")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s from %s" % (rec.device_model_id.name or "?", rec.valid_from or "")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by_id", "approved_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._TERMS
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in self._TERMS & set(vals)):
                    raise UserError(
                        "Grid price %s is %s: it is replaced by a new row, not edited."
                        % (rec.name, rec.state)
                    )
        return super().write(vals)

    def action_approve(self):
        _assert_role(self.env, GROUP_VALUATION_MANAGER, "Approving a grid price")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft grid price is approved.")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: a grid price you entered is approved by another valuation manager."
                )
            older = self.sudo().search(
                [
                    ("device_model_id", "=", rec.device_model_id.id),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "approved"),
                    ("valid_from", "<=", rec.valid_from),
                ]
            )
            older._guarded().write({"state": "retired"})
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_retire(self):
        _assert_role(self.env, GROUP_VALUATION_MANAGER, "Retiring a grid price")
        self._guarded().write({"state": "retired"})
        return True

    @api.model
    def _price_for(self, device_model, company, on_date):
        if not device_model:
            return self.browse()
        return self.sudo().search(
            [
                ("device_model_id", "=", device_model.id),
                ("company_id", "=", company.id),
                ("state", "=", "approved"),
                ("valid_from", "<=", on_date),
            ],
            order="valid_from desc, id desc",
            limit=1,
        )


class FixTradeinValuation(models.Model):
    """An automated valuation of one trade-in, with a manual final offer.

    P2 (governed valuation grid, approval on any override): the market price
    comes from the approved grid row of the device model. A typed price, a
    final offer other than the computed one, or a model with no grid row is
    an OVERRIDE: it states its reason and is approved by a valuation manager
    other than the valuer before it can be applied."""

    _name = "fix.tradein.valuation"
    _description = "Trade-In Valuation"
    _inherit = ["fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    _INPUTS = frozenset(
        {
            "tradein_id",
            "market_ref_price",
            "age_months",
            "age_factor_pct",
            "condition_factor_pct",
            "final_offer",
            "method",
            "override_reason",
            "currency_id",
        }
    )

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    device_model_id = fields.Many2one(
        related="tradein_id.device_model_id", string="Device Model", store=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    grid_id = fields.Many2one(
        "fix.tradein.price.grid",
        string="Grid Price",
        compute="_compute_grid",
        help="The approved grid row of the device model on the valuation date",
    )
    market_ref_price = fields.Monetary(
        string="Market Reference Price", currency_field="currency_id", required=True
    )
    age_months = fields.Integer(string="Age (months)", default=0)
    age_factor_pct = fields.Integer(string="Age Factor %", default=100)
    condition_factor_pct = fields.Integer(string="Condition Factor %", default=100)
    computed_offer = fields.Monetary(
        string="Computed Offer",
        currency_field="currency_id",
        compute="_compute_offer",
        store=True,
    )
    final_offer = fields.Monetary(string="Final Offer", currency_field="currency_id")
    applied_offer = fields.Monetary(
        string="Applied Offer", currency_field="currency_id", readonly=True, copy=False
    )
    method = fields.Selection(
        [("rules", "Rules Engine"), ("manual", "Manual Override")],
        required=True,
        default="rules",
    )
    is_override = fields.Boolean(
        string="Override",
        compute="_compute_override",
        help="No grid row, a price other than the grid's, a final offer other than the "
        "computed one, or a manual method: needs a valuation manager's approval.",
    )
    override_reason = fields.Char()
    override_state = fields.Selection(
        [
            ("none", "Not Needed"),
            ("pending", "Approval Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="none",
        required=True,
        readonly=True,
        copy=False,
    )
    override_approved_by_id = fields.Many2one(
        "res.users", string="Override Approved By", readonly=True, copy=False
    )
    override_approved_at = fields.Datetime(readonly=True, copy=False)
    valuated_on = fields.Date(required=True, default=fields.Date.context_today)
    valuated_by_id = fields.Many2one(
        "res.users", string="Valuated By", default=lambda self: self.env.user
    )
    state = fields.Selection(
        [("draft", "Draft"), ("applied", "Applied"), ("superseded", "Superseded")],
        required=True,
        default="draft",
        readonly=True,
    )

    _factors_range = models.Constraint(
        "CHECK (age_factor_pct >= 0 AND age_factor_pct <= 100 "
        "AND condition_factor_pct >= 0 AND condition_factor_pct <= 100)",
        "Age and condition factors are percentages between 0 and 100",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "applied_offer",
            "override_state",
            "override_approved_by_id",
            "override_approved_at",
            "valuated_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(
            r.state != "draft" or r.override_state in ("pending", "approved") for r in self
        ):
            locked |= self._INPUTS
        return locked

    @api.depends("device_model_id", "valuated_on", "company_id")
    def _compute_grid(self):
        Grid = self.env["fix.tradein.price.grid"]
        for rec in self:
            rec.grid_id = Grid._price_for(rec.device_model_id, rec.company_id, rec.valuated_on)

    @api.depends("market_ref_price", "age_factor_pct", "condition_factor_pct")
    def _compute_offer(self):
        for rec in self:
            rec.computed_offer = round(
                (rec.market_ref_price or 0.0)
                * (rec.age_factor_pct or 0)
                / 100.0
                * (rec.condition_factor_pct or 0)
                / 100.0,
                2,
            )

    @api.depends("grid_id", "market_ref_price", "final_offer", "computed_offer", "method")
    def _compute_override(self):
        for rec in self:
            rec.is_override = bool(
                rec.method == "manual"
                or not rec.grid_id
                or abs((rec.market_ref_price or 0.0) - rec.grid_id.market_ref_price) > _EPS
                or (rec.final_offer and abs(rec.final_offer - rec.computed_offer) > _EPS)
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.valuation") or "TVAL/New"
                )
            if not vals.get("market_ref_price") and vals.get("tradein_id"):
                tradein = self.env["fix.tradein.request"].browse(vals["tradein_id"])
                grid = self.env["fix.tradein.price.grid"]._price_for(
                    tradein.device_model_id,
                    tradein.company_id,
                    vals.get("valuated_on") or fields.Date.context_today(self),
                )
                if grid:
                    vals["market_ref_price"] = grid.market_ref_price
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(
                lambda r: r.state != "draft" or r.override_state in ("pending", "approved")
            ):
                names = [
                    n
                    for n in self._INPUTS & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if names:
                    raise UserError(
                        "Valuation %s is %s: its inputs are frozen. Start a new valuation."
                        % (rec.name, rec.state if rec.state != "draft" else "awaiting approval")
                    )
        return super().write(vals)

    def action_request_override_approval(self):
        for rec in self:
            if rec.state != "draft" or not rec.is_override:
                raise UserError("Only a draft override valuation is sent for approval.")
            if not (rec.override_reason or "").strip():
                raise UserError("A manual override must state its reason")
            if rec.override_state == "pending":
                raise UserError("Valuation %s is already awaiting approval." % rec.name)
            rec._guarded().write({"override_state": "pending"})
        return True

    def action_approve_override(self):
        _assert_role(self.env, GROUP_VALUATION_MANAGER, "Approving a valuation override")
        for rec in self:
            if rec.override_state != "pending":
                raise UserError("Only a pending override is approved.")
            _assert_amount_tier(
                self.env, rec.final_offer or rec.computed_offer, "Approving a valuation override"
            )
            if not self.env.su and self.env.user in (
                rec.create_uid | rec.valuated_by_id | rec.tradein_id.create_uid
            ):
                raise UserError(
                    "Segregation of duties: the valuer or the trade-in's creator does not "
                    "approve their own override."
                )
            rec._guarded().write(
                {
                    "override_state": "approved",
                    "override_approved_by_id": self.env.uid,
                    "override_approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject_override(self):
        _assert_role(self.env, GROUP_VALUATION_MANAGER, "Rejecting a valuation override")
        for rec in self:
            if rec.override_state != "pending":
                raise UserError("Only a pending override is rejected.")
            rec._guarded().write({"override_state": "rejected"})
        return True

    def action_apply_to_tradein(self):
        """Apply the final (or computed) offer to the trade-in request."""
        for rec in self:
            if rec.state == "applied":
                raise UserError("Valuation %s has already been applied" % rec.name)
            if rec.state != "draft":
                raise UserError("Valuation %s is %s." % (rec.name, rec.state))
            tradein = rec.tradein_id
            if tradein.state not in ("draft", "offered"):
                raise UserError(
                    "Trade-in %s is '%s' — a valuation applies before the offer is accepted"
                    % (tradein.name, tradein.state)
                )
            offer = rec.final_offer or rec.computed_offer
            if offer <= 0:
                raise UserError("The valuation has no positive offer to apply")
            if rec.is_override:
                if not (rec.override_reason or "").strip():
                    raise UserError("A manual override must state its reason")
                if rec.override_state != "approved":
                    raise UserError(
                        "Valuation %s overrides the price grid (%s): a valuation manager "
                        "approves it before it is applied."
                        % (
                            rec.name,
                            "no approved grid price for the model"
                            if not rec.grid_id
                            else "the price or offer differs from the grid",
                        )
                    )
            vals = {"offered_value": offer}
            # Revised offer: an offer already sent is withdrawn and sent again,
            # so the customer accepts the value they are actually offered.
            if tradein.state == "offered" and abs(tradein.offered_value - offer) > _EPS:
                vals["state"] = "draft"
            tradein._guarded().write(vals)
            others = self.sudo().search(
                [("tradein_id", "=", tradein.id), ("state", "=", "applied"), ("id", "!=", rec.id)]
            )
            others._guarded().write({"state": "superseded"})
            rec._guarded().write({"state": "applied", "applied_offer": offer})
        return True


class FixTradeinProvenance(models.Model):
    """The IMEI / blacklist / stolen / activation-lock screen for one trade-in.

    A05 audit M14-5/6, E7: rows were born NID-verified, NEIR-checked and
    'Valid & Whitelisted' with a hard-coded NID; the NEIR check was a stub
    that cleared any IMEI; state and hit flags were free writes. Now:
      - nothing is verified by default, and the NEIR status reads
        'unchecked' until a real NEIR check runs (none exists before the BTRC
        NEIR relaunch of 1 January 2027);
      - a provenance officer (not the trade-in's creator) clears a screen,
        with its evidence, an IMEI and the activation lock (Find My / FRP)
        recorded OFF; that also verifies the seller's NID against the card;
      - anyone may RAISE a hit (it flags the screen); nobody lowers one. A
        flagged screen is a hard stop for the trade-in, with no override."""

    _name = "fix.tradein.provenance"
    _description = "Trade-In Provenance Screen"
    _inherit = ["fix.guarded.mixin"]
    _order = "checked_on desc, id desc"

    _HITS = ("blacklist_hit", "stolen_hit")
    _EVIDENCE = frozenset(
        {
            "tradein_id",
            "imei",
            "customer_nid_no",
            "evidence_attachment_id",
            "evidence_ref",
            "lock_status",
            "company_id",
        }
    )

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    imei = fields.Char(string="IMEI / Serial")
    blacklist_checked = fields.Boolean(default=False, readonly=True)
    blacklist_hit = fields.Boolean(string="Blacklisted", default=False)
    stolen_checked = fields.Boolean(default=False, readonly=True)
    stolen_hit = fields.Boolean(string="Reported Stolen", default=False)
    warranty_checked = fields.Boolean(
        default=False,
        readonly=True,
        help="No OEM warranty lookup is integrated: never set by a person.",
    )
    warranty_active = fields.Boolean(string="Under Warranty", default=False, readonly=True)
    # P2 anti-theft lock check (Find My / Google FRP)
    lock_status = fields.Selection(
        [
            ("unknown", "Not checked"),
            ("off", "Off — no activation lock / FRP"),
            ("on", "On — activation lock / FRP present"),
        ],
        string="Activation Lock (Find My / FRP)",
        default="unknown",
        required=True,
    )
    btrc_neir_checked = fields.Boolean(
        string="BTRC NEIR Online Check", default=False, readonly=True
    )
    btrc_neir_status = fields.Selection(
        [
            ("unchecked", "Unchecked — NEIR not queried"),
            ("valid", "Valid & Whitelisted"),
            ("unregistered", "Unregistered Device"),
            ("stolen", "Reported Stolen / Blacklisted"),
            ("pending", "Pending Query"),
            # D4: the manual NEIR result a provenance officer records
            ("clear", "Clear (manual NEIR result)"),
            ("blocked", "Blocked (manual NEIR result)"),
            ("not_found", "Not Found (manual NEIR result)"),
        ],
        string="BTRC NEIR Status",
        default="unchecked",
        required=True,
        readonly=True,
    )
    neir_evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="NEIR Result Evidence", readonly=True, copy=False
    )
    neir_evidence_ref = fields.Char(string="NEIR Lookup Reference", readonly=True, copy=False)
    neir_result_by_id = fields.Many2one(
        "res.users", string="NEIR Result Recorded By", readonly=True, copy=False
    )
    neir_result_at = fields.Datetime(string="NEIR Result Recorded At", readonly=True, copy=False)
    customer_nid_no = fields.Char(string="Customer Smart NID")
    customer_nid_verified = fields.Boolean(
        string="Customer NID Verified", default=False, readonly=True
    )
    evidence_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Screening Evidence",
        ondelete="restrict",
        help="The lookup screenshots / NID card scan the officer cleared on",
    )
    evidence_ref = fields.Char(string="Lookup Reference")
    notes = fields.Text()
    checked_on = fields.Date(required=True, default=fields.Date.context_today, readonly=True)
    cleared_by_id = fields.Many2one("res.users", string="Cleared By", readonly=True, copy=False)
    cleared_at = fields.Datetime(readonly=True, copy=False)
    flagged_by_id = fields.Many2one("res.users", string="Flagged By", readonly=True, copy=False)
    flag_reason = fields.Char(readonly=True, copy=False)
    state = fields.Selection(
        [("pending", "Pending"), ("cleared", "Cleared"), ("flagged", "Flagged")],
        required=True,
        default="pending",
        readonly=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "blacklist_checked",
            "stolen_checked",
            "warranty_checked",
            "warranty_active",
            "btrc_neir_checked",
            "btrc_neir_status",
            "customer_nid_verified",
            "checked_on",
            "cleared_by_id",
            "cleared_at",
            "flagged_by_id",
            "flag_reason",
            "neir_evidence_attachment_id",
            "neir_evidence_ref",
            "neir_result_by_id",
            "neir_result_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(p.state != "pending" for p in self):
            locked |= self._EVIDENCE
        if self and any(p.stolen_hit or p.blacklist_hit for p in self):
            locked |= set(self._HITS)
        return locked

    @api.constrains("imei")
    def _check_imei(self):
        for rec in self:
            if rec.imei and (not rec.imei.isdigit() or len(rec.imei) != 15):
                raise ValidationError("An IMEI is exactly 15 digits")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.provenance") or "PROV/New"
                )
        records = super().create(vals_list)
        records.filtered(lambda p: p.stolen_hit or p.blacklist_hit)._flag("hit recorded at intake")
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                lowered = [h for h in self._HITS if h in vals and rec[h] and not vals[h]]
                if lowered:
                    raise UserError(
                        "A stolen or blacklist hit on %s cannot be removed: a hit is a hard "
                        "stop. Record a new screen only if the register itself is corrected."
                        % rec.name
                    )
                if rec.state != "pending":
                    names = [
                        n
                        for n in self._EVIDENCE & set(vals)
                        if rec._fix_guard_differs(n, vals[n], rec[n])
                    ]
                    if names:
                        raise UserError(
                            "Provenance screen %s is %s: its evidence is frozen. A new check "
                            "is a new screen." % (rec.name, rec.state)
                        )
        raised = self.filtered(lambda p: not (p.stolen_hit or p.blacklist_hit))
        result = super().write(vals)
        raised.filtered(lambda p: p.stolen_hit or p.blacklist_hit)._flag("hit recorded")
        return result

    def unlink(self):
        if not self.env.su:
            raise UserError("A provenance screen is evidence and is not deleted.")
        return super().unlink()

    def _flag(self, reason):
        for rec in self.filtered(lambda p: p.state != "flagged"):
            rec._guarded().write(
                {
                    "state": "flagged",
                    "flagged_by_id": self.env.uid,
                    "flag_reason": reason,
                    "btrc_neir_status": "stolen"
                    if rec.btrc_neir_status == "valid"
                    else rec.btrc_neir_status,
                }
            )

    def action_clear(self):
        """The provenance officer clears the screen on recorded evidence."""
        _assert_role(self.env, GROUP_PROVENANCE_OFFICER, "Clearing a provenance screen")
        for rec in self:
            if rec.blacklist_hit or rec.stolen_hit:
                raise UserError(
                    "A provenance check with a blacklist or stolen hit cannot be cleared"
                )
            if rec.state != "pending":
                raise UserError("Provenance screen %s is %s." % (rec.name, rec.state))
            if not (rec.imei and rec.imei.isdigit() and len(rec.imei) == 15):
                raise UserError("Record the device's 15-digit IMEI before clearing")
            if not (rec.evidence_attachment_id or (rec.evidence_ref or "").strip()):
                raise UserError(
                    "Attach the blacklist / stolen lookup evidence (or its reference) before "
                    "clearing"
                )
            if rec.lock_status != "off":
                raise UserError(
                    "The activation lock (Find My / FRP) is %s: the seller removes it before "
                    "the device is traded."
                    % dict(rec._fields["lock_status"].selection)[rec.lock_status]
                )
            if not self.env.su and rec.tradein_id.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: the provenance of a trade-in you raised is cleared "
                    "by another provenance officer."
                )
            nid = (rec.customer_nid_no or "").strip()
            request_nid = (rec.tradein_id.customer_nid or "").strip()
            nid_ok = bool(
                nid and nid == request_nid and _NID_RE.match(nid) and not nid_placeholder(nid)
            )
            if nid and not nid_ok:
                raise UserError(
                    "The NID sighted (%s) is not the seller's NID on the trade-in (%s), or is "
                    "not a valid identity number." % (nid, request_nid or "none")
                )
            rec._guarded().write(
                {
                    "state": "cleared",
                    "blacklist_checked": True,
                    "stolen_checked": True,
                    "customer_nid_verified": nid_ok,
                    "checked_on": fields.Date.context_today(rec),
                    "cleared_by_id": self.env.uid,
                    "cleared_at": fields.Datetime.now(),
                }
            )
        return True

    def action_flag(self, reason=None):
        """Anyone may flag a device: flagging fails safe."""
        for rec in self:
            if rec.state == "flagged":
                continue
            if not (rec.stolen_hit or rec.blacklist_hit or (reason or "").strip()):
                raise UserError("Say why the device is flagged (or record the hit).")
            rec._flag((reason or "").strip() or "hit recorded")
        return True

    def action_run_neir_check(self):
        """BTRC NEIR lookup. No NEIR integration exists, so this records
        nothing and clears nothing: the provenance officer records the manual
        NEIR result with its evidence (action_record_neir_result, D4)."""
        for rec in self:
            if rec.btrc_neir_status not in ("unchecked", "pending"):
                continue
            rec._guarded().write({"btrc_neir_status": "unchecked", "btrc_neir_checked": False})
        return {
            "neir_status": "unchecked",
            "message": "BTRC NEIR is not integrated: a provenance officer records the NEIR "
            "result (clear / blocked / not found) with its evidence.",
        }

    def action_record_neir_result(
        self, result=None, evidence_ref=None, evidence_attachment_id=None
    ):
        """D4 (owner 20 Nov 2026): a provenance officer who did not raise the
        trade-in records the manual NEIR result with its evidence (an
        attachment or a lookup reference). 'blocked' flags the screen (a hard
        stop); only 'clear' passes the gate."""
        _assert_role(self.env, GROUP_PROVENANCE_OFFICER, "Recording a NEIR result")
        if result not in ("clear", "blocked", "not_found"):
            raise UserError("A NEIR result is clear, blocked or not_found.")
        try:
            attachment = (
                self.env["ir.attachment"].browse(int(evidence_attachment_id)).exists()
                if evidence_attachment_id
                else self.env["ir.attachment"]
            )
        except (TypeError, ValueError):
            attachment = self.env["ir.attachment"]
        ref = (evidence_ref or "").strip()
        if not (attachment or ref):
            raise UserError("Attach the NEIR lookup evidence or give its reference.")
        for rec in self:
            if rec.state == "flagged":
                raise UserError("Provenance screen %s is flagged: a hit is a hard stop." % rec.name)
            if not self.env.su and rec.tradein_id.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: the NEIR result of a trade-in you raised is recorded "
                    "by another provenance officer."
                )
            rec._guarded().write(
                {
                    "btrc_neir_status": result,
                    "btrc_neir_checked": True,
                    "neir_evidence_attachment_id": attachment.id or False,
                    "neir_evidence_ref": ref or False,
                    "neir_result_by_id": self.env.uid,
                    "neir_result_at": fields.Datetime.now(),
                }
            )
            if result == "blocked":
                rec._flag("NEIR result: blocked")
        return True


class FixTradeinGrade(models.Model):
    """The recorded A–E grading result (battery, screen, cosmetic, functional).

    M14-18: a grade row created after resale-ready rewrote the request's
    grade while the stock kept the old one. A grade is recorded while the
    unit is in refurbishment, and frozen once the unit is graded."""

    _name = "fix.tradein.grade"
    _description = "Trade-In Grading Result"
    _order = "graded_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    grade = fields.Selection(
        [
            ("a", "A — Like New"),
            ("b", "B — Good"),
            ("c", "C — Fair"),
            ("d", "D — Poor"),
            ("e", "E — Parts Only"),
        ],
        required=True,
        default="b",
    )
    battery_health_pct = fields.Integer(string="Battery Health %", default=100)
    screen_grade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], string="Screen", default="a"
    )
    cosmetic_grade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], string="Cosmetic", default="a"
    )
    functional_grade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], string="Functional", default="a"
    )
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    graded_on = fields.Date(required=True, default=fields.Date.context_today)
    notes = fields.Text()
    cycle = fields.Integer(string="Refurbishment Cycle", readonly=True, default=1)

    _battery_range = models.Constraint(
        "CHECK (battery_health_pct >= 0 AND battery_health_pct <= 100)",
        "Battery health must be a percentage between 0 and 100",
    )

    def _refuse_unless_refurbishing(self, tradeins):
        if self.env.su:
            return
        late = tradeins.filtered(lambda t: t.state != "refurbished")
        if late:
            raise UserError(
                "Trade-in %s is %s: a grade is recorded while the unit is in refurbishment, "
                "never after it is graded." % (late[0].name, late[0].state)
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = [v.get("tradein_id") for v in vals_list if v.get("tradein_id")]
        self._refuse_unless_refurbishing(self.env["fix.tradein.request"].browse(ids))
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.grade") or "TGRD/New"
                )
        records = super().create(vals_list)
        # the grading result is the trade-in's grade: keep the request aligned
        for rec in records:
            # M14-05: a grade belongs to the unit's current refurbishment cycle
            rec.sudo()._guarded().write({"cycle": rec.tradein_id.sudo().refurb_cycle or 1})
            if rec.tradein_id.state == "refurbished":
                rec.tradein_id.write(
                    {"grade": rec.grade, "battery_health_pct": rec.battery_health_pct}
                )
        return records

    def write(self, vals):
        self._refuse_unless_refurbishing(self.mapped("tradein_id"))
        result = super().write(vals)
        if {"grade", "battery_health_pct"} & set(vals):
            for rec in self.filtered(lambda r: r.tradein_id.state == "refurbished"):
                rec.tradein_id.write(
                    {"grade": rec.grade, "battery_health_pct": rec.battery_health_pct}
                )
        return result

    def unlink(self):
        self._refuse_unless_refurbishing(self.mapped("tradein_id"))
        return super().unlink()


class FixRefurbQa(models.Model):
    """Final QA of a refurbished unit — the test battery and battery health.

    M14-12 (measurable QA): the verdict was a free selection ('pass' with 0
    of 12 tests). It is now derived from the results when a QA inspector
    submits them (pass only at or above cd_tradein.qa_min_pass_pct, 100% by
    default), and the results are frozen once submitted."""

    _name = "fix.refurb.qa"
    _description = "Refurbishment QA"
    _inherit = ["fix.guarded.mixin"]
    _order = "checked_on desc, id desc"

    _RESULTS = frozenset(
        {
            "tradein_id",
            "refurbishment_id",
            "battery_health_pct",
            "tests_total",
            "tests_passed",
            "inspector_id",
            "company_id",
        }
    )

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    refurbishment_id = fields.Many2one(
        "fix.refurbishment", string="Refurb Step", ondelete="set null"
    )
    battery_health_pct = fields.Integer(string="Battery Health %", default=100)
    tests_total = fields.Integer(string="Tests", default=12)
    tests_passed = fields.Integer(string="Passed", default=0)
    pass_pct = fields.Float(string="Pass %", compute="_compute_pass", store=True)
    qa_state = fields.Selection(
        [("pass", "Pass"), ("fail", "Fail"), ("pending", "Pending")],
        required=True,
        default="pending",
        readonly=True,
    )
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    inspected_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True, copy=False)
    checked_on = fields.Date(required=True, default=fields.Date.context_today)
    notes = fields.Text()
    cycle = fields.Integer(string="Refurbishment Cycle", readonly=True, default=1)

    _tests_range = models.Constraint(
        "CHECK (tests_passed >= 0 AND tests_total > 0 AND tests_passed <= tests_total)",
        "Passed tests must be between 0 and the total tests",
    )
    _battery_range = models.Constraint(
        "CHECK (battery_health_pct >= 0 AND battery_health_pct <= 100)",
        "Battery health must be a percentage between 0 and 100",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "qa_state",
            "inspected_by_id",
            "checked_on",
            "cycle",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(q.qa_state != "pending" for q in self):
            locked |= self._RESULTS
        return locked

    @api.depends("tests_passed", "tests_total")
    def _compute_pass(self):
        for rec in self:
            rec.pass_pct = (
                round((rec.tests_passed or 0) / rec.tests_total * 100.0, 1)
                if rec.tests_total
                else 0.0
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            ids = [v.get("tradein_id") for v in vals_list if v.get("tradein_id")]
            for rec in self.env["fix.tradein.request"].browse(ids):
                if rec.state != "refurbished":
                    raise UserError(
                        "Trade-in %s is %s: QA is recorded while the unit is in refurbishment."
                        % (rec.name, rec.state)
                    )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.refurb.qa") or "RQA/New"
        records = super().create(vals_list)
        # M14-05: a QA belongs to the unit's current refurbishment cycle
        for rec in records.filtered("tradein_id"):
            rec.sudo()._guarded().write({"cycle": rec.tradein_id.sudo().refurb_cycle or 1})
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda q: q.qa_state != "pending"):
                names = [
                    n
                    for n in self._RESULTS & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if names:
                    raise UserError(
                        "QA %s is submitted (%s): its results are frozen. A re-test is a new "
                        "QA record." % (rec.name, rec.qa_state)
                    )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(q.qa_state != "pending" for q in self):
            raise UserError("A submitted QA result is evidence and is not deleted.")
        return super().unlink()

    def action_submit_result(self):
        """The QA inspector submits the measured results; the verdict follows."""
        _assert_role(self.env, GROUP_QA_INSPECTOR, "Submitting a QA result")
        threshold = _param_float(self.env, PARAM_QA_MIN_PASS_PCT, 100.0)
        for rec in self:
            if rec.qa_state != "pending":
                raise UserError("QA %s is already submitted (%s)." % (rec.name, rec.qa_state))
            if rec.tradein_id.state != "refurbished":
                raise UserError("QA is submitted while the unit is in refurbishment.")
            if not rec.tests_total or rec.tests_total <= 0:
                raise UserError("A QA result needs the number of tests run.")
            technicians = (
                rec.tradein_id.sudo()
                .refurbishment_ids.filtered(lambda s: s.step != "intake")
                .mapped("completed_by_id")
            )
            if not self.env.su and self.env.user in technicians:
                raise UserError(
                    "QA independence: a technician who completed this unit's repair steps "
                    "does not pass its QA."
                )
            verdict = "pass" if rec.pass_pct >= threshold - 1e-6 else "fail"
            rec._guarded().write(
                {
                    "qa_state": verdict,
                    "inspected_by_id": self.env.uid,
                    "checked_on": fields.Date.context_today(rec),
                }
            )
        return True


class FixTradeinHarvest(models.Model):
    """Harvesting a component from a trade-in into parts or recycling.

    M14-16 (harvest workflow): there was no action and `state` was a free
    write, so harvested parts reached no inventory. Harvest now runs from a
    graded parts-only (grade E) unit after its data wipe and hold period:
    to spare stock it raises a draft M15 goods receipt (fix.stock.receipt,
    sourced to the harvest line) for the storekeeper to inspect and post; to
    recycling it is announced to M18 (event tradein.harvested)."""

    _name = "fix.tradein.harvest"
    _description = "Trade-In Harvest"
    _inherit = ["fix.guarded.mixin"]
    _order = "harvested_on desc, id desc"

    _TERMS = frozenset(
        {"tradein_id", "component", "part_name", "part_id", "quantity", "unit_value", "target"}
    )

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    component = fields.Selection(
        [
            ("screen", "Screen / Display"),
            ("battery", "Battery"),
            ("camera", "Camera Module"),
            ("board", "Main Board"),
            ("speaker", "Speaker / Mic"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    part_name = fields.Char(string="Part Name")
    part_id = fields.Many2one(
        "fix.spare.part",
        string="Spare Part (M15)",
        ondelete="restrict",
        help="The M15 part the component is received into (spare stock / refurb)",
    )
    quantity = fields.Integer(default=1)
    unit_value = fields.Monetary(string="Unit Value", currency_field="currency_id")
    total_value = fields.Monetary(
        string="Total Value",
        currency_field="currency_id",
        compute="_compute_total",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    target = fields.Selection(
        [
            ("spare_stock", "Spare Stock (M15)"),
            ("refurb", "Refurbishment"),
            ("recycle", "Recycle (M18)"),
        ],
        required=True,
        default="spare_stock",
    )
    state = fields.Selection(
        [("pending", "Pending"), ("harvested", "Harvested"), ("scrapped", "Scrapped")],
        required=True,
        default="pending",
        readonly=True,
    )
    receipt_id = fields.Many2one(
        "fix.stock.receipt", string="M15 Goods Receipt", readonly=True, copy=False
    )
    harvested_by_id = fields.Many2one("res.users", string="Harvested By", readonly=True, copy=False)
    harvested_on = fields.Date(default=fields.Date.context_today)
    notes = fields.Char()

    _quantity_positive = models.Constraint(
        "CHECK (quantity > 0)", "Harvest quantity must be positive"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "receipt_id", "harvested_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(h.state != "pending" for h in self):
            locked |= self._TERMS | {"harvested_on", "company_id", "currency_id"}
        return locked

    @api.depends("quantity", "unit_value")
    def _compute_total(self):
        for rec in self:
            rec.total_value = round((rec.quantity or 0) * (rec.unit_value or 0.0), 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.harvest") or "HARV/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda h: h.state != "pending"):
                names = [
                    n for n in self._TERMS & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if names:
                    raise UserError("Harvest %s is %s: it is final." % (rec.name, rec.state))
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(h.state != "pending" for h in self):
            raise UserError("A harvested or scrapped line is not deleted.")
        return super().unlink()

    def _harvest_denial(self) -> str:
        self.ensure_one()
        tradein = self.tradein_id
        # A05 ERP M14-09/21: a unit is harvested once its write-off routed it
        # to parts only (a QA-failed unit included), never from stock
        if tradein.state != "parts_only":
            return (
                "trade-in %s is %s: a unit is harvested once an approved write-off routed it "
                "to parts only" % (tradein.name, tradein.state)
            )
        stop = tradein._provenance_hard_stop()
        if stop:
            return stop
        denial = tradein._wipe_gate_denial(tradein.wipe_certificate_id, tradein.device_id)
        if denial:
            return "Journey 9 wipe gate: %s" % denial
        return tradein._hold_denial()

    def action_harvest(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("Harvest %s is %s." % (rec.name, rec.state))
            denial = rec._harvest_denial()
            if denial:
                raise UserError("Harvest refused: %s." % denial)
            vals = {"state": "harvested", "harvested_by_id": self.env.uid}
            if rec.target in ("spare_stock", "refurb"):
                rec._harvest_assert_value()
                vals["receipt_id"] = rec._harvest_receipt().id
            rec._guarded().write(vals)
            if rec.target in ("spare_stock", "refurb"):
                rec._harvest_relieve()
            publish(
                self.env,
                "tradein.harvested",
                "fix.tradein.harvest",
                rec.id,
                {
                    "tradein": rec.tradein_id.name,
                    "component": rec.component,
                    "part": rec.part_id.part_number if rec.part_id else (rec.part_name or ""),
                    "quantity": rec.quantity,
                    "value": float(rec.total_value),
                    "target": rec.target,
                    "receipt": rec.receipt_id.name if rec.receipt_id else "",
                },
            )
        return True

    def _harvest_assert_value(self):
        """M14-20 / FIN-20: a harvested part enters M15 at a share of the
        unit's carrying cost, never above what is left of it."""
        self.ensure_one()
        tradein = self.tradein_id.sudo()
        left = tradein._ledger_carrying()
        if (self.total_value or 0.0) > left + _EPS:
            raise UserError(
                "Harvest %s: BDT %.2f is more than the BDT %.2f of %s's cost still in stock. A "
                "harvested part is valued from the unit's cost, never above it."
                % (self.name, self.total_value, left, tradein.name)
            )

    def _harvest_relieve(self):
        """Move the part's value out of refurbished stock into M15 (its
        valuation suspense account, where M15 stock is held until the GL
        cut-over)."""
        self.ensure_one()
        from odoo.addons.cd_inventory.models.fix_valuation_suspense import suspense_account_code

        from .fix_tradein_ledger import tradein_account

        tradein = self.tradein_id.sudo()
        amount = round(self.total_value or 0.0, 2)
        if amount <= _EPS:
            return
        code = suspense_account_code(self.env)
        m15 = (
            self.env["account.account"]
            .sudo()
            .with_company(tradein.company_id)
            .search([("code", "=", code), ("company_ids", "in", tradein.company_id.id)], limit=1)
        )
        if not m15:
            raise UserError(
                "Harvest %s: M15's valuation suspense account %s is not in the chart of %s "
                "(cd_inventory.valuation_suspense_account_code)."
                % (self.name, code, tradein.company_id.name)
            )
        stock = tradein_account(self.env, tradein.company_id, "refurb_stock")
        tradein._ledger_post(
            "harvest",
            "harvest:%d" % self.id,
            amount,
            -amount,
            [
                (m15, "Harvest %s into M15 (%s)" % (self.name, tradein.name), amount, 0.0, None),
                (stock, "Harvest %s out of refurbished stock" % self.name, 0.0, amount, None),
            ],
            "harvest %s" % self.name,
        )

    def _harvest_receipt(self):
        """A draft M15 goods receipt for the harvested part (cd_inventory's
        public receipt path: the storekeeper inspects and posts it)."""
        self.ensure_one()
        if not self.part_id:
            raise UserError("Name the M15 spare part the %s is received into." % self.component)
        if (self.unit_value or 0.0) <= 0:
            raise UserError("A harvested part needs its unit value (the cost it is stocked at).")
        try:
            location_id = int(_param(self.env, PARAM_HARVEST_LOCATION, 0) or 0)
        except (TypeError, ValueError):
            location_id = 0
        location = self.env["fix.stock.location"].sudo().browse(location_id).exists()
        if not location:
            raise UserError(
                "No M15 receiving location is configured for harvested parts (system parameter "
                "%s): configured, never guessed." % PARAM_HARVEST_LOCATION
            )
        Receipt = self.env["fix.stock.receipt"].sudo()
        receipt = Receipt.search(
            [("source_model", "=", self._name), ("source_res_id", "=", self.id)], limit=1
        )
        if receipt:
            return receipt
        tradein = self.tradein_id
        return Receipt.create(
            {
                "company_id": self.company_id.id,
                "operating_unit_id": tradein.operating_unit_id.id or False,
                "partner_id": self.company_id.partner_id.id,
                "location_id": location.id,
                "ownership_class": "owned",
                "source_model": self._name,
                "source_res_id": self.id,
                "source_ref": "%s / %s" % (self.name, tradein.name),
                "inspection_notes": "Harvested from trade-in %s" % tradein.name,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "part_id": self.part_id.id,
                            "qty_received": self.quantity,
                            "qty_accepted": self.quantity,
                            "unit_cost": self.unit_value,
                            "source_line_ref": self.name,
                        },
                    )
                ],
            }
        )

    def action_scrap(self, reason=None):
        for rec in self:
            if rec.state != "pending":
                raise UserError("Harvest %s is %s." % (rec.name, rec.state))
            if not (reason or "").strip():
                raise UserError("State why the component is scrapped.")
            rec._guarded().write({"state": "scrapped", "notes": reason.strip()[:200]})
        return True


class FixTradeinWarranty(models.Model):
    """The warranty issued on a refurbished, resold unit.

    M14-17: a warranty was a manual row any clerk created and voided. It is
    now issued by the resale itself (the graded_stock.sold consumer on the
    trade-in), with an M17 fix.warranty for the device, and voided only by a
    warranty officer with a reason."""

    _name = "fix.tradein.warranty"
    _description = "Refurbished Unit Warranty"
    _inherit = ["fix.guarded.mixin"]
    _order = "start_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    months = fields.Integer(string="Warranty (months)", default=6)
    sale_no = fields.Integer(string="Sale No.", readonly=True, index=True)
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(compute="_compute_end", store=True)
    terms = fields.Text()
    claims_count = fields.Integer(string="Claims", default=0, readonly=True)
    graded_stock_ref = fields.Char(string="Resold Stock Unit", readonly=True, index=True)
    device_warranty_id = fields.Many2one(
        "fix.warranty", string="Device Warranty (M17)", readonly=True, ondelete="set null"
    )
    void_reason = fields.Text(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("active", "Active"),
            ("expired", "Expired"),
            ("void", "Void"),
            # M14-05/07: the buyer brought the unit back; this sale's cover ends
            ("returned", "Closed by Return"),
        ],
        required=True,
        default="active",
        readonly=True,
    )

    _months_positive = models.Constraint(
        "CHECK (months > 0)", "A refurbished-unit warranty is at least one month"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "claims_count",
            "graded_stock_ref",
            "device_warranty_id",
            "void_reason",
            "tradein_id",
            "months",
            "start_date",
            "sale_no",
        }

    @api.depends("start_date", "months")
    def _compute_end(self):
        """M14-06: calendar months (a sale on 31 August ends on 28/29 February,
        it no longer crashes on a missing day)."""
        for rec in self:
            if rec.start_date and rec.months:
                rec.end_date = rec.start_date + relativedelta(months=rec.months)
            else:
                rec.end_date = False

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(
                "A refurbished-unit warranty is issued by the resale of the unit, not typed."
            )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.warranty") or "TWAR/New"
                )
        return super().create(vals_list)

    def unlink(self):
        if not self.env.su:
            raise UserError("A warranty is voided with a reason, not deleted.")
        return super().unlink()

    def action_void(self, reason=None):
        _assert_role(self.env, GROUP_WARRANTY_OFFICER, "Voiding a refurbished-unit warranty")
        for rec in self:
            if rec.state != "active":
                raise UserError("Warranty %s is %s." % (rec.name, rec.state))
            if not (reason or "").strip():
                raise UserError("State why the warranty is voided.")
            rec._guarded().write({"state": "void", "void_reason": reason.strip()})
        return True
