# fix_demand_capture - M43 capture audit (2026-11-16): the spec §10.1 records
# that every sub-module page captures and that did not exist.
#
#  - fix.demand.adjustment   page 1  outlier / censored-demand overlay on the
#                                    M15 history (FR-DPL-003/004, T-01); the
#                                    forecast applies it, the source never changes
#  - fix.demand.driver       page 3  known demand influence (FR-DPL-013)
#  - fix.demand.service.target page 5 service level per segment (FR-DPL-018);
#                                    a policy below its target is not activated
#  - fix.demand.lead.time    page 6  lead time per product and supplier, the
#                                    quoted figure beside the measured one
#                                    (FR-DPL-019, BRU-DPL-09)
#  - fix.demand.npi          page 7  new-part initial stocking (FR-DPL-030)
#  - fix.demand.eol          page 7  run-down and last-time buy (FR-DPL-031,
#                                    BRU-DPL-14: approver, and CFO above a value)
#  - fix.demand.van.par      page 8  van par recommendation (FR-DPL-029,
#                                    BRU-DPL-12); approval publishes it to M15
#  - fix.demand.network.policy page 8 where a part is held (FR-DPL-027); a
#                                    policy or van par outside it is refused
from datetime import timedelta
from math import ceil, sqrt

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_demand_common import (
    APPROVER,
    CFG_LEAD_TIME_WINDOW_DAYS,
    PERIOD_RE,
    PLANNER,
    add_months,
    consumed_by_day,
    consumed_by_month,
    dhaka_today,
    has_usable_history,
    mean_and_stddev,
    month_start,
    param,
    refuse_self_decision,
    require_role,
    z_for,
)

CFG_LTB_CFO_THRESHOLD = "cd_demand_plan.ltb_cfo_threshold"  # default 500,000 BDT
CFO = "cd_entity_config.group_dofa_tier_4"
# M43-08: a service level is any percentage (50 to 99.99); 90/95/98/99 are the
# segment defaults the owner keeps (D7)
SERVICE_LEVELS = [("90", "90%"), ("95", "95%"), ("98", "98%"), ("99", "99%")]
ABC = [("a", "A"), ("b", "B"), ("c", "C")]
CRITICALITY = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")]
LOCATION_TYPES = [("central", "Central Warehouse"), ("branch", "Branch"), ("van", "Van")]
DEMAND_STREAMS = [
    ("routine", "Routine repair"),
    ("warranty_campaign", "Warranty campaign"),
    ("contract", "Contract / AMC scheduled work"),
    ("project", "Project roll-out"),
    ("rental", "Rental fleet"),
    ("refurbishment", "Refurbishment"),
]


def _sequence(env, code, fallback):
    return env["ir.sequence"].next_by_code(code) or fallback


def _frozen(rec, vals, names, why):
    changed = [n for n in names & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])]
    if changed:
        labels = ", ".join(sorted(rec._fields[n].string or n for n in changed))
        raise UserError("%s cannot be changed on %s: %s." % (labels, rec.display_name, why))


class _DemandRecord(models.AbstractModel):
    """Shared shape: a numbered, company-scoped, guarded record whose inputs
    freeze once it leaves its first state."""

    _name = "fix.demand.capture.mixin"
    _description = "M43 captured record"
    _inherit = ["fix.guarded.mixin"]

    _sequence_code = None
    _sequence_fallback = "New"
    _open_states = ("draft",)
    _inputs = frozenset()

    name = fields.Char(required=True, default="New", copy=False)
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", default=lambda self: self.env.user, readonly=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "prepared_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state not in self._open_states:
            locked |= set(self._inputs)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New" and self._sequence_code:
                vals["name"] = _sequence(self.env, self._sequence_code, self._sequence_fallback)
        return super().create(vals_list)

    def write(self, vals):
        edited = self.browse()
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state not in self._open_states:
                    _frozen(rec, vals, set(self._inputs), "it is %s" % rec.state)
                elif any(
                    rec._fix_guard_differs(n, vals[n], rec[n])
                    for n in set(self._inputs) & set(vals)
                ):
                    edited |= rec
        res = super().write(vals)
        if edited:
            edited._guarded().write({"prepared_by_id": self.env.user.id})
        return res

    def _decide(self, state, **extra):
        self._guarded().write(dict(extra, state=state))


def _check_period(value, label="Period"):
    if value and not PERIOD_RE.match(value):
        raise ValidationError("%s %r is not a YYYY-MM month." % (label, value))


# =====================================================================
# Page 1 - History & Cleansing: the overlay on M15 history (T-01)
# =====================================================================
class FixDemandAdjustment(models.Model):
    _name = "fix.demand.adjustment"
    _description = "Demand History Adjustment"
    _inherit = ["fix.demand.capture.mixin"]
    _order = "period desc, id desc"
    _sequence_code = "fix.demand.adjustment"
    _sequence_fallback = "DADJ/New"
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    _inputs = frozenset(
        {
            "product_id",
            "part_id",
            "location_id",
            "period",
            "adjustment_type",
            "demand_stream",
            "adjusted_qty",
            "reason",
        }
    )

    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="restrict", index=True
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="M15 Spare Part", required=True, ondelete="restrict", index=True
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Stock Location", index=True, help="Empty = all locations"
    )
    period = fields.Char(required=True, help="YYYY-MM: the month of history adjusted")
    adjustment_type = fields.Selection(
        [
            ("outlier_exclude", "Outlier: exclude the month"),
            ("outlier_replace", "Outlier: replace with a typical value"),
            ("reclassify", "Reclassify out of routine demand"),
            ("censored", "Censored demand: add stock-out unmet demand"),
        ],
        string="Treatment",
        required=True,
    )
    demand_stream = fields.Selection(
        DEMAND_STREAMS,
        string="Moved To Stream",
        help="Reclassify: the stream the spike belongs to (BRU-DPL-05)",
    )
    original_qty = fields.Float(
        string="M15 Consumption (source)",
        readonly=True,
        help="The M15 figure of the month when the adjustment was applied; never edited",
    )
    adjusted_qty = fields.Float(string="Adjusted Quantity")
    reason = fields.Text(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("applied", "Applied"), ("revoked", "Revoked")],
        required=True,
        default="draft",
    )
    applied_by_id = fields.Many2one("res.users", string="Applied By", readonly=True)
    applied_on = fields.Datetime(string="Applied On", readonly=True)
    revoke_reason = fields.Char(string="Revoke Reason", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "original_qty",
            "applied_by_id",
            "applied_on",
            "revoke_reason",
        }

    @api.constrains("period")
    def _check_period_format(self):
        for rec in self:
            _check_period(rec.period)

    @api.constrains("adjustment_type", "demand_stream", "adjusted_qty", "reason")
    def _check_treatment(self):
        for rec in self:
            if not (rec.reason or "").strip():
                raise ValidationError("Every history adjustment records its reason (FR-DPL-003).")
            if rec.adjusted_qty < 0:
                raise ValidationError("An adjusted quantity cannot be negative.")
            if rec.adjustment_type == "reclassify" and rec.demand_stream in (False, "routine"):
                raise ValidationError(
                    "A reclassified month names the non-routine stream it moves to."
                )
            if rec.adjustment_type == "outlier_replace" and rec.adjusted_qty <= 0:
                raise ValidationError(
                    "Replacing an outlier needs the typical value; to drop the month, exclude it."
                )

    def _source_qty(self):
        first = month_start(self.period)
        return consumed_by_month(
            self.env, self.company_id, self.part_id, self.location_id, first, 1
        )[0]

    def action_apply(self):
        require_role(self.env, PLANNER, what="Applying a history adjustment")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Apply a draft adjustment")
            clash = self.search_count(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("part_id", "=", rec.part_id.id),
                    ("location_id", "=", rec.location_id.id),
                    ("period", "=", rec.period),
                    ("state", "=", "applied"),
                ]
            )
            if clash:
                raise UserError(
                    "%s already has an applied adjustment for %s: revoke it first."
                    % (rec.part_id.display_name, rec.period)
                )
            source = round(rec._source_qty(), 3)
            if rec.adjustment_type in ("outlier_exclude", "outlier_replace", "reclassify"):
                if source <= 0:
                    raise UserError(
                        "%s has no M15 consumption in %s: there is no outlier to treat."
                        % (rec.part_id.display_name, rec.period)
                    )
                if rec.adjustment_type == "outlier_replace" and rec.adjusted_qty >= source:
                    raise UserError(
                        "An outlier replacement lowers the month (M15 shows %g)." % source
                    )
            if rec.adjustment_type == "censored" and rec.adjusted_qty <= source:
                raise UserError(
                    "A censored-demand correction raises the month above the %g M15 consumed "
                    "while out of stock (BRU-DPL-19)." % source
                )
            vals = {
                "original_qty": source,
                "applied_by_id": self.env.user.id,
                "applied_on": fields.Datetime.now(),
            }
            if rec.adjustment_type in ("outlier_exclude", "reclassify"):
                rec._guarded().write({"adjusted_qty": 0.0})
            rec._decide("applied", **vals)
        return True

    def action_revoke(self, reason=None):
        require_role(self.env, PLANNER, APPROVER, what="Revoking a history adjustment")
        if not (reason or "").strip():
            raise UserError("State why the adjustment is revoked.")
        for rec in self:
            if rec.state != "applied":
                raise UserError("Revoke an applied adjustment")
            rec._decide("revoked", revoke_reason=reason.strip())
        return True

    @api.model
    def _overlay(self, company, part, location, first, buckets):
        """The monthly series with every applied adjustment laid over it. The
        M15 source is untouched; returns (series, periods adjusted)."""
        if not part:
            return list(buckets), []
        months = len(buckets)
        periods = {
            "%04d-%02d" % (d.year, d.month): i
            for i, d in enumerate(add_months(first, k) for k in range(months))
        }
        rows = self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("part_id", "=", part.id),
                ("location_id", "=", location.id if location else False),
                ("period", "in", list(periods)),
                ("state", "=", "applied"),
            ]
        )
        out = list(buckets)
        touched = []
        for row in rows:
            out[periods[row.period]] = row.adjusted_qty
            touched.append(row.period)
        return out, sorted(touched)

    @api.model
    def _excluded_periods(self, company, part, location, periods):
        """M43-10: the months an applied 'exclude' treatment drops from the
        series. They are not zero-demand months: the average and the deviation
        are taken over the months that remain."""
        if not part or not periods:
            return set()
        return set(
            self.sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("part_id", "=", part.id),
                    ("location_id", "=", location.id if location else False),
                    ("period", "in", list(periods)),
                    ("state", "=", "applied"),
                    ("adjustment_type", "=", "outlier_exclude"),
                ]
            )
            .mapped("period")
        )

    @api.model
    def _overlay_daily(self, company, part, location, first, daily):
        """M43-10: the policy's DAILY series with the applied adjustments laid
        over it: an excluded month's days leave the sample, a replaced,
        reclassified or censored month is rescaled to its adjusted total (spread
        evenly when M15 shows nothing). Returns the series to measure."""
        if not part or not daily:
            return list(daily)
        by_month = {}
        for i in range(len(daily)):
            day = first + timedelta(days=i)
            by_month.setdefault("%04d-%02d" % (day.year, day.month), []).append(i)
        rows = self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("part_id", "=", part.id),
                ("location_id", "=", location.id if location else False),
                ("period", "in", list(by_month)),
                ("state", "=", "applied"),
            ]
        )
        series = list(daily)
        dropped = set()
        for row in rows:
            idx = by_month[row.period]
            if row.adjustment_type == "outlier_exclude":
                dropped.update(idx)
                continue
            source = sum(series[i] for i in idx)
            target = row.adjusted_qty or 0.0
            for i in idx:
                series[i] = series[i] * target / source if source > 0 else target / len(idx)
        return [q for i, q in enumerate(series) if i not in dropped]


# =====================================================================
# Page 3 - Forecast Orchestration: known demand drivers (FR-DPL-013)
# =====================================================================
class FixDemandDriver(models.Model):
    _name = "fix.demand.driver"
    _description = "Demand Driver"
    _inherit = ["fix.demand.capture.mixin"]
    _order = "period_from desc, id desc"
    _sequence_code = "fix.demand.driver"
    _sequence_fallback = "DDRV/New"
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    _inputs = frozenset(
        {
            "driver_type",
            "source_ref",
            "product_id",
            "location_id",
            "period_from",
            "period_to",
            "expected_impact_pct",
            "basis",
        }
    )

    driver_type = fields.Selection(
        [
            ("installed_base", "Installed base (M17)"),
            ("contract", "Contract / AMC schedule (M08)"),
            ("campaign", "Warranty campaign (M09)"),
            ("seasonality", "Seasonality"),
            ("branch_opening", "Branch opening"),
        ],
        string="Driver",
        required=True,
    )
    source_ref = fields.Char(string="Source Reference", help="e.g. the M09 campaign or contract")
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="restrict", index=True
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Stock Location", help="Empty = every location"
    )
    period_from = fields.Char(string="From (YYYY-MM)", required=True)
    period_to = fields.Char(string="To (YYYY-MM)", required=True)
    expected_impact_pct = fields.Float(string="Expected Impact %", required=True)
    basis = fields.Text(string="Basis", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    @api.constrains("period_from", "period_to", "expected_impact_pct", "basis")
    def _check_driver(self):
        for rec in self:
            _check_period(rec.period_from, "From")
            _check_period(rec.period_to, "To")
            if rec.period_to < rec.period_from:
                raise ValidationError("A driver ends on or after the month it starts.")
            if rec.expected_impact_pct < -100 or rec.expected_impact_pct > 500:
                raise ValidationError("The expected impact is -100% to +500%.")
            if not rec.expected_impact_pct:
                raise ValidationError("A driver with no expected impact changes nothing.")
            if not (rec.basis or "").strip():
                raise ValidationError("State what the expected impact is based on.")

    def action_activate(self):
        require_role(self.env, PLANNER, what="Activating a demand driver")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Activate a draft driver")
            rec._decide("active")
        return True

    def action_retire(self):
        require_role(self.env, PLANNER, APPROVER, what="Retiring a demand driver")
        for rec in self:
            if rec.state != "active":
                raise UserError("Retire an active driver")
            rec._decide("retired")
        return True

    @api.model
    def _covering(self, forecast):
        """Active drivers of the forecast's product, month and location."""
        if not (forecast.product_id and forecast.period):
            return self.browse()
        return self.sudo().search(
            [
                ("company_id", "=", forecast.company_id.id),
                ("product_id", "=", forecast.product_id.id),
                ("state", "=", "active"),
                ("period_from", "<=", forecast.period),
                ("period_to", ">=", forecast.period),
                "|",
                ("location_id", "=", False),
                ("location_id", "=", forecast.location_id.id),
            ]
        )


class FixDemandForecastDrivers(models.Model):
    _inherit = "fix.demand.forecast"

    override_driver_id = fields.Many2one(
        "fix.demand.driver",
        string="Override Driver",
        domain=[("state", "=", "active")],
        help="The driver an override answers, when there is one",
    )
    driver_impact_pct = fields.Float(
        string="Driver Impact %", compute="_compute_driver_impact", help="Active drivers' sum"
    )
    driver_note = fields.Char(string="Active Drivers", compute="_compute_driver_impact")

    @api.depends("product_id", "location_id", "period", "company_id")
    def _compute_driver_impact(self):
        Driver = self.env["fix.demand.driver"]
        for rec in self:
            drivers = Driver._covering(rec)
            rec.driver_impact_pct = round(sum(drivers.mapped("expected_impact_pct")), 1)
            rec.driver_note = (
                "; ".join("%s %+g%%" % (d.name, d.expected_impact_pct) for d in drivers) or False
            )

    @api.constrains("override_driver_id", "has_override", "product_id")
    def _check_override_driver(self):
        for rec in self.filtered("override_driver_id"):
            if not rec.has_override:
                raise ValidationError("A driver is cited by a planner override.")
            if rec.override_driver_id.product_id != rec.product_id:
                raise ValidationError("The cited driver is for another product.")


# =====================================================================
# Page 5 - Safety Stock & ROP: service-level targets (FR-DPL-018)
# =====================================================================
class FixDemandServiceTarget(models.Model):
    _name = "fix.demand.service.target"
    _description = "Service-Level Target"
    _inherit = ["fix.demand.capture.mixin"]
    _order = "abc_class, effective_from desc, id desc"
    _sequence_code = "fix.demand.service.target"
    _sequence_fallback = "DSLT/New"
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    _inputs = frozenset(
        {"abc_class", "criticality", "location_type", "target_pct", "effective_from", "rationale"}
    )

    abc_class = fields.Selection(ABC, string="ABC Class", required=True)
    criticality = fields.Selection(CRITICALITY, help="Empty = any criticality")
    location_type = fields.Selection(LOCATION_TYPES, help="Empty = any location")
    target_pct = fields.Float(
        string="Target Service Level %", required=True, help="50 to 99.99 (M43-08)"
    )
    effective_from = fields.Date(required=True, default=fields.Date.context_today)
    rationale = fields.Char()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("superseded", "Superseded")],
        required=True,
        default="draft",
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"approved_by_id", "approved_on"}

    @api.constrains("target_pct")
    def _check_target(self):
        for rec in self:
            if not 50.0 <= (rec.target_pct or 0.0) < 100.0:
                raise ValidationError("A service-level target is 50% to 99.99%.")

    def _key_domain(self):
        return [
            ("id", "!=", self.id),
            ("company_id", "=", self.company_id.id),
            ("abc_class", "=", self.abc_class),
            ("criticality", "=", self.criticality),
            ("location_type", "=", self.location_type),
        ]

    def action_activate(self):
        """A Demand Plan Approver other than its author sets the target; the
        target it replaces is superseded."""
        require_role(self.env, APPROVER, what="Setting a service-level target")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Activate a draft target")
            refuse_self_decision(
                self.env, rec.create_uid | rec.prepared_by_id, "Service-level target %s" % rec.name
            )
            self.search([*rec._key_domain(), ("state", "=", "active")])._decide("superseded")
            rec._decide(
                "active", approved_by_id=self.env.user.id, approved_on=fields.Datetime.now()
            )
        return True

    @api.model
    def _for_policy(self, policy):
        """The most specific active target for the policy's segment and
        location type, or an empty recordset (unclassified parts have none)."""
        seg = policy._segment()
        if not seg or not seg.classified_on:
            return self.browse()
        crit = "critical" if seg._is_critical() else seg.criticality
        loc_type = policy.location_id.location_type if policy.location_id else False
        targets = self.sudo().search(
            [
                ("company_id", "=", policy.company_id.id),
                ("state", "=", "active"),
                ("abc_class", "=", seg.abc_class),
                ("criticality", "in", [False, crit]),
                ("location_type", "in", [False, loc_type]),
                ("effective_from", "<=", fields.Date.context_today(self)),
            ]
        )
        return targets.sorted(
            lambda t: (bool(t.criticality) + bool(t.location_type), t.effective_from),
            reverse=True,
        )[:1]


# =====================================================================
# Page 6 - Lead-Time: per product and supplier (FR-DPL-019, BRU-DPL-09)
# =====================================================================
def supplier_lead_times(env, company, product, vendor, since):
    """Days from PO sent to posted receipt for this supplier's M16 receipts of
    the product, and from commitment to receipt for its M44 imports with no
    M16 PO. Same sampling as the policy's observed lead time."""
    out = []
    if "fix.purchase.receipt.line" in env:
        lines = (
            env["fix.purchase.receipt.line"]
            .sudo()
            .search(
                [
                    ("product_id", "=", product.id),
                    ("receipt_id.state", "=", "posted"),
                    ("receipt_id.company_id", "=", company.id),
                    ("receipt_id.received_on", ">=", since),
                    ("receipt_id.purchase_order_id.vendor_id", "=", vendor.id),
                ]
            )
        )
        for line in lines:
            order = line.receipt_id.purchase_order_id
            received = line.receipt_id.received_on
            if order.sent_at and received and (received - order.sent_at.date()).days >= 0:
                out.append(((received - order.sent_at.date()).days, "domestic"))
    if "fix.import.order.line" in env:
        lines = (
            env["fix.import.order.line"]
            .sudo()
            .search(
                [
                    ("part_id.product_id", "=", product.id),
                    ("order_id.company_id", "=", company.id),
                    ("order_id.received_on", ">=", since),
                    ("order_id.m16_receipt_id", "=", False),
                    ("order_id.supplier_id", "=", vendor.id),
                ]
            )
        )
        for line in lines:
            order = line.order_id
            proformas = (
                env["fix.import.proforma"]
                .sudo()
                .search([("order_id", "=", order.id), ("state", "=", "approved")])
            )
            stamps = [d for d in proformas.mapped("decided_on") if d]
            start = min(stamps) if stamps else order.create_date
            days = (order.received_on - start.date()).days
            if days >= 0:
                out.append((days, "import"))
    return out


def _p95(values):
    if not values:
        return 0.0
    ordered = sorted(values)
    return float(ordered[min(len(ordered) - 1, ceil(0.95 * len(ordered)) - 1)])


class FixDemandLeadTime(models.Model):
    _name = "fix.demand.lead.time"
    _description = "Lead-Time Model"
    _inherit = ["fix.demand.capture.mixin"]
    _order = "product_id, vendor_id"
    _sequence_code = "fix.demand.lead.time"
    _sequence_fallback = "DLTM/New"
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    _open_states = ("quoted", "measured")
    _inputs = frozenset({"product_id", "vendor_id", "quoted_days", "window_days", "notes"})

    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="restrict", index=True
    )
    vendor_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, ondelete="restrict", index=True
    )
    quoted_days = fields.Integer(
        string="Quoted Lead Time (days)",
        required=True,
        help="The supplier's quoted figure, kept for comparison only (BRU-DPL-09)",
    )
    window_days = fields.Integer(
        string="Receipt Window (days)", default=lambda self: self._default_window()
    )
    supply_source = fields.Selection(
        [("domestic", "Domestic (M16)"), ("import", "Import (M44)"), ("mixed", "Mixed")],
        string="Supply Source",
        readonly=True,
    )
    sample_count = fields.Integer(string="Receipts Measured", readonly=True)
    mean_days = fields.Float(string="Actual Mean (days)", readonly=True)
    std_dev_days = fields.Float(string="Actual Std Dev (days)", readonly=True)
    p95_days = fields.Float(string="Actual P95 (days)", readonly=True)
    variance_days = fields.Float(
        string="Actual − Quoted (days)", compute="_compute_variance", help="Positive = late"
    )
    measured_on = fields.Datetime(string="Measured On", readonly=True)
    notes = fields.Char()
    state = fields.Selection(
        [("quoted", "Quoted only"), ("measured", "Measured")],
        required=True,
        default="quoted",
    )

    _product_vendor_unique = models.Constraint(
        "UNIQUE (company_id, product_id, vendor_id)", "One lead-time model per product and supplier"
    )

    @api.model
    def _default_window(self):
        return param(self.env, CFG_LEAD_TIME_WINDOW_DAYS, 365, int)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "supply_source",
            "sample_count",
            "mean_days",
            "std_dev_days",
            "p95_days",
            "measured_on",
        }

    @api.depends("mean_days", "quoted_days", "sample_count")
    def _compute_variance(self):
        for rec in self:
            rec.variance_days = (
                round(rec.mean_days - rec.quoted_days, 1) if rec.sample_count else 0.0
            )

    @api.constrains("quoted_days", "window_days")
    def _check_days(self):
        for rec in self:
            if rec.quoted_days <= 0:
                raise ValidationError("The quoted lead time is a positive number of days.")
            if rec.window_days < 30 or rec.window_days > 1095:
                raise ValidationError("The receipt window is 30 to 1095 days.")

    def write(self, vals):
        res = super().write(vals)
        if {"product_id", "vendor_id", "window_days"} & set(vals) and not self._fix_guard_open():
            # what was measured belongs to the old key: measure again
            self._guarded().write(
                {
                    "state": "quoted",
                    "sample_count": 0,
                    "mean_days": 0.0,
                    "std_dev_days": 0.0,
                    "p95_days": 0.0,
                    "supply_source": False,
                    "measured_on": False,
                }
            )
        return res

    def action_measure(self):
        """Mean, deviation and P95 of the actual receipts of this product
        from this supplier (M16 PO sent -> receipt; M44 commitment -> receipt)."""
        require_role(self.env, PLANNER, what="Measuring a lead time")
        today = dhaka_today()  # M43-21
        for rec in self:
            samples = supplier_lead_times(
                rec.env,
                rec.company_id,
                rec.product_id,
                rec.vendor_id,
                today - timedelta(days=rec.window_days),
            )
            if not samples:
                raise UserError(
                    "%s has no posted receipt of %s in the last %d days: the lead time stays "
                    "the quoted %d days, unmeasured."
                    % (
                        rec.vendor_id.display_name,
                        rec.product_id.display_name,
                        rec.window_days,
                        rec.quoted_days,
                    )
                )
            days = [d for d, _src in samples]
            sources = {src for _d, src in samples}
            mean, std = mean_and_stddev(days)
            rec._decide(
                "measured",
                sample_count=len(days),
                mean_days=round(mean, 2),
                std_dev_days=round(std, 2),
                p95_days=_p95(days),
                supply_source=sources.pop() if len(sources) == 1 else "mixed",
                measured_on=fields.Datetime.now(),
            )
        return True


# =====================================================================
# Page 7 - Planned Orders: new-part introduction (FR-DPL-030)
# =====================================================================
class FixDemandNpi(models.Model):
    _name = "fix.demand.npi"
    _description = "New-Part Introduction Recommendation"
    _inherit = ["fix.demand.capture.mixin"]
    _order = "id desc"
    _sequence_code = "fix.demand.npi"
    _sequence_fallback = "DNPI/New"
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    _inputs = frozenset(
        {
            "product_id",
            "part_id",
            "analogy_part_id",
            "installed_base_ref",
            "location_ids",
            "recommended_initial_qty",
            "confidence",
            "rationale",
        }
    )

    product_id = fields.Many2one(
        "product.product", string="New Product", required=True, ondelete="restrict", index=True
    )
    part_id = fields.Many2one("fix.spare.part", string="New M15 Spare Part", index=True)
    analogy_part_id = fields.Many2one(
        "fix.spare.part", string="Analogy Part", help="A similar part whose M15 demand guides"
    )
    analogy_monthly_avg = fields.Float(
        string="Analogy Avg / Month (12 m)", compute="_compute_analogy"
    )
    installed_base_ref = fields.Char(string="Installed Base / Launch Data (M17)")
    location_ids = fields.Many2many(
        "fix.stock.location",
        "fix_demand_npi_location_rel",
        "npi_id",
        "location_id",
        string="Stock At",
    )
    recommended_initial_qty = fields.Float(string="Initial Quantity", required=True)
    confidence = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")], required=True, default="low"
    )
    rationale = fields.Text(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("rejected", "Rejected")],
        required=True,
        default="draft",
    )
    approved_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    approved_on = fields.Datetime(string="Decided On", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "approved_by_id",
            "approved_on",
            "analogy_monthly_avg",
        }

    @api.depends("analogy_part_id", "company_id")
    def _compute_analogy(self):
        first = add_months(dhaka_today().replace(day=1), -12)
        for rec in self:
            if not rec.analogy_part_id:
                rec.analogy_monthly_avg = 0.0
                continue
            months = consumed_by_month(
                rec.env, rec.company_id, rec.analogy_part_id, False, first, 12
            )
            rec.analogy_monthly_avg = round(sum(months) / 12.0, 2)

    @api.constrains("recommended_initial_qty", "rationale", "part_id", "analogy_part_id")
    def _check_npi(self):
        for rec in self:
            if rec.recommended_initial_qty <= 0:
                raise ValidationError("The initial stocking quantity is positive.")
            if not (rec.rationale or "").strip():
                raise ValidationError("State the basis of the initial stocking quantity.")
            if rec.part_id and rec.part_id == rec.analogy_part_id:
                raise ValidationError("A part is not its own analogy.")

    def action_approve(self):
        require_role(self.env, APPROVER, what="Approving a new-part recommendation")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft recommendation")
            refuse_self_decision(
                self.env, rec.create_uid | rec.prepared_by_id, "Recommendation %s" % rec.name
            )
            if not (rec.analogy_part_id or (rec.installed_base_ref or "").strip()):
                raise UserError(
                    "Recommendation %s has neither an analogy part nor installed-base data: "
                    "there is nothing it is based on (FR-DPL-030)." % rec.name
                )
            if rec.part_id and has_usable_history(rec.env, rec.company_id, rec.part_id, False):
                raise UserError(
                    "%s already has M15 history: plan it from its own demand, not as a new "
                    "part." % rec.part_id.display_name
                )
            rec._decide(
                "approved", approved_by_id=self.env.user.id, approved_on=fields.Datetime.now()
            )
        return True

    def action_reject(self):
        require_role(self.env, APPROVER, what="Rejecting a new-part recommendation")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Reject a draft recommendation")
            rec._decide(
                "rejected", approved_by_id=self.env.user.id, approved_on=fields.Datetime.now()
            )
        return True


# =====================================================================
# Page 7 - Planned Orders: end-of-life and last-time buy (FR-DPL-031)
# =====================================================================
class FixDemandEol(models.Model):
    _name = "fix.demand.eol"
    _description = "End-of-Life / Last-Time-Buy Plan"
    _inherit = ["fix.demand.capture.mixin"]
    _order = "run_down_start desc, id desc"
    _sequence_code = "fix.demand.eol"
    _sequence_fallback = "DEOL/New"
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    _inputs = frozenset(
        {
            "part_id",
            "successor_part_id",
            "run_down_start",
            "last_buy_date",
            "projected_remaining_demand",
            "last_time_buy_qty",
            "rationale",
        }
    )

    part_id = fields.Many2one(
        "fix.spare.part", string="Part Going Out", required=True, ondelete="restrict", index=True
    )
    successor_part_id = fields.Many2one("fix.spare.part", string="Successor Part")
    run_down_start = fields.Date(string="Run-Down Start", required=True)
    last_buy_date = fields.Date(string="Last-Buy Window Closes")
    projected_remaining_demand = fields.Float(string="Projected Remaining Demand", required=True)
    last_time_buy_qty = fields.Float(string="Last-Time-Buy Qty", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    last_time_buy_value = fields.Monetary(
        string="Last-Time-Buy Value",
        currency_field="currency_id",
        compute="_compute_value",
        store=True,
        readonly=True,
    )
    needs_cfo = fields.Boolean(string="Needs CFO", compute="_compute_value", store=True)
    rationale = fields.Text(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("cfo", "Awaiting CFO"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    cfo_approved_by_id = fields.Many2one("res.users", string="CFO Approved By", readonly=True)
    decided_on = fields.Datetime(readonly=True)
    reject_reason = fields.Char(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "last_time_buy_value",
            "needs_cfo",
            "approved_by_id",
            "cfo_approved_by_id",
            "decided_on",
            "reject_reason",
        }

    @api.depends("last_time_buy_qty", "part_id")
    def _compute_value(self):
        threshold = param(self.env, CFG_LTB_CFO_THRESHOLD, 500000.0)
        for rec in self:
            cost = rec.part_id.sudo().unit_cost if rec.part_id else 0.0
            rec.last_time_buy_value = round((rec.last_time_buy_qty or 0.0) * cost, 2)
            rec.needs_cfo = rec.last_time_buy_value > threshold

    @api.constrains(
        "part_id", "successor_part_id", "last_time_buy_qty", "projected_remaining_demand"
    )
    def _check_eol(self):
        for rec in self:
            if rec.part_id == rec.successor_part_id:
                raise ValidationError("A part does not succeed itself.")
            if rec.last_time_buy_qty < 0 or rec.projected_remaining_demand < 0:
                raise ValidationError("Quantities cannot be negative.")
            if not (rec.rationale or "").strip():
                raise ValidationError("State why the part runs down and how the quantity is set.")

    def action_approve(self):
        """BRU-DPL-14: a Demand Plan Approver who did not prepare it; above
        the value threshold it then waits for the CFO."""
        require_role(self.env, APPROVER, what="Approving a last-time buy")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft end-of-life plan")
            refuse_self_decision(
                self.env, rec.create_uid | rec.prepared_by_id, "Plan %s" % rec.name
            )
            if rec.last_time_buy_qty and not rec.part_id.sudo().unit_cost:
                raise UserError(
                    "%s has no M15 standard cost: the last-time-buy value cannot be weighed."
                    % rec.part_id.display_name
                )
            rec._decide(
                "cfo" if rec.needs_cfo else "approved",
                approved_by_id=self.env.user.id,
                decided_on=fields.Datetime.now(),
            )
        return True

    def action_approve_cfo(self):
        require_role(self.env, CFO, what="Approving a last-time buy above the value threshold")
        for rec in self:
            if rec.state != "cfo":
                raise UserError("Plan %s is not awaiting the CFO" % rec.name)
            refuse_self_decision(
                self.env,
                rec.create_uid | rec.prepared_by_id | rec.approved_by_id,
                "Plan %s" % rec.name,
            )
            rec._decide(
                "approved", cfo_approved_by_id=self.env.user.id, decided_on=fields.Datetime.now()
            )
        return True

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why the plan is rejected.")
        for rec in self:
            if rec.state == "cfo":
                require_role(self.env, CFO, what="Rejecting a last-time buy at CFO stage")
            else:
                require_role(self.env, APPROVER, what="Rejecting a last-time buy")
            if rec.state not in ("draft", "cfo"):
                raise UserError("Reject a plan that is still awaiting a decision")
            rec._decide("rejected", reject_reason=reason.strip(), decided_on=fields.Datetime.now())
        return True


# =====================================================================
# Page 8 - Network: where a part is held (FR-DPL-027)
# =====================================================================
class FixDemandNetworkPolicy(models.Model):
    _name = "fix.demand.network.policy"
    _description = "Network Stocking Policy"
    _inherit = ["fix.demand.capture.mixin"]
    _order = "part_id, id desc"
    _sequence_code = "fix.demand.network.policy"
    _sequence_fallback = "DNET/New"
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    _inputs = frozenset({"part_id", "central_stock", "location_ids", "van_stock", "rationale"})

    part_id = fields.Many2one(
        "fix.spare.part", string="M15 Spare Part", required=True, ondelete="restrict", index=True
    )
    central_stock = fields.Boolean(string="Held at Central", default=True)
    location_ids = fields.Many2many(
        "fix.stock.location",
        "fix_demand_network_location_rel",
        "policy_id",
        "location_id",
        string="Forward-Stocked At",
        help="Branch locations that hold the part",
    )
    van_stock = fields.Boolean(string="Held on Vans")
    rationale = fields.Text(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("superseded", "Superseded")],
        required=True,
        default="draft",
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"approved_by_id", "approved_on"}

    @api.constrains("location_ids", "rationale")
    def _check_network(self):
        for rec in self:
            if not (rec.rationale or "").strip():
                raise ValidationError("State why the part is held where it is (FR-DPL-027).")
            wrong = rec.location_ids.filtered(lambda loc: loc.location_type != "branch")
            if wrong:
                raise ValidationError(
                    "Forward stocking lists branch locations; central and vans have their own "
                    "switches (%s)." % ", ".join(wrong.mapped("display_name"))
                )

    def action_approve(self):
        require_role(self.env, APPROVER, what="Approving a network stocking policy")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft network policy")
            refuse_self_decision(
                self.env, rec.create_uid | rec.prepared_by_id, "Network policy %s" % rec.name
            )
            self.search(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("part_id", "=", rec.part_id.id),
                    ("state", "=", "approved"),
                ]
            )._decide("superseded")
            rec._decide(
                "approved", approved_by_id=self.env.user.id, approved_on=fields.Datetime.now()
            )
        return True

    @api.model
    def _refusal(self, company, part, location):
        """Why the approved network policy does not hold the part at the
        location, or False (no policy, or the location is allowed)."""
        if not (part and location):
            return False
        pol = self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("part_id", "=", part.id),
                ("state", "=", "approved"),
            ],
            limit=1,
        )
        if not pol:
            return False
        kind = location.location_type
        allowed = (
            (kind == "central" and pol.central_stock)
            or (kind == "van" and pol.van_stock)
            or (kind == "branch" and location in pol.location_ids)
            or kind not in ("central", "branch", "van")
        )
        if allowed:
            return False
        return "network policy %s does not hold %s at %s (%s)" % (
            pol.name,
            part.display_name,
            location.display_name,
            dict(location._fields["location_type"].selection).get(kind),
        )


# =====================================================================
# Page 8 - Van par recommendation (FR-DPL-029, BRU-DPL-12)
# =====================================================================
class FixDemandVanPar(models.Model):
    _name = "fix.demand.van.par"
    _description = "Van Par Recommendation"
    _inherit = ["fix.demand.capture.mixin"]
    _order = "id desc"
    _sequence_code = "fix.demand.van.par"
    _sequence_fallback = "DVPR/New"
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    _open_states = ("proposed",)
    _inputs = frozenset(
        {
            "van_location_id",
            "part_id",
            "history_days",
            "replenish_days",
            "service_level_pct",
            "min_qty",
            "max_qty",
            "deviation_reason",
        }
    )

    van_location_id = fields.Many2one(
        "fix.stock.location",
        string="Van",
        required=True,
        ondelete="restrict",
        index=True,
        domain=[("location_type", "=", "van")],
    )
    technician_id = fields.Many2one(
        related="van_location_id.technician_id", string="Technician", readonly=True
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="M15 Spare Part", required=True, ondelete="restrict", index=True
    )
    history_days = fields.Integer(string="History Window (days)", default=90)
    replenish_days = fields.Integer(
        string="Van Replenishment Cycle (days)", default=7, help="Days between van top-ups"
    )
    service_level_pct = fields.Float(string="Service Level %", required=True, default=95.0)
    avg_daily_demand = fields.Float(string="Van Avg Daily Use", readonly=True)
    demand_stddev = fields.Float(string="Van Use Std Dev", readonly=True)
    suggested_min = fields.Float(string="Suggested Min", readonly=True)
    suggested_max = fields.Float(string="Suggested Max", readonly=True)
    computed_on = fields.Datetime(string="Computed On", readonly=True)
    min_qty = fields.Float(string="Par Min")
    max_qty = fields.Float(string="Par Max")
    deviation_reason = fields.Char(
        string="Why Not the Suggestion", help="Needed when the par differs from the suggestion"
    )
    state = fields.Selection(
        [("proposed", "Proposed"), ("applied", "Applied to M15"), ("rejected", "Rejected")],
        required=True,
        default="proposed",
    )
    approved_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    approved_on = fields.Datetime(string="Decided On", readonly=True)
    published_rule_id = fields.Many2one(
        "fix.reorder.rule", string="M15 Reorder Rule", readonly=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "avg_daily_demand",
            "demand_stddev",
            "suggested_min",
            "suggested_max",
            "computed_on",
            "approved_by_id",
            "approved_on",
            "published_rule_id",
        }

    @api.constrains(
        "van_location_id",
        "history_days",
        "replenish_days",
        "min_qty",
        "max_qty",
        "service_level_pct",
    )
    def _check_par(self):
        for rec in self:
            if rec.van_location_id.location_type != "van":
                raise ValidationError("A van par is set on a van stock location.")
            if rec.history_days < 7 or rec.history_days > 730:
                raise ValidationError("The history window is 7 to 730 days.")
            if rec.replenish_days < 1 or rec.replenish_days > 90:
                raise ValidationError("The van replenishment cycle is 1 to 90 days.")
            if rec.min_qty < 0 or rec.max_qty < 0:
                raise ValidationError("Par levels cannot be negative.")
            if not 50.0 <= (rec.service_level_pct or 0.0) < 100.0:
                raise ValidationError("The service level is 50% to 99.99%.")

    def write(self, vals):
        res = super().write(vals)
        keys = {"van_location_id", "part_id", "history_days", "replenish_days", "service_level_pct"}
        if keys & set(vals) and not self._fix_guard_open():
            self._guarded().write(
                {"computed_on": False, "suggested_min": 0.0, "suggested_max": 0.0}
            )
        return res

    def action_compute(self):
        """From the van's own M15 consumption: min = use over the cycle +
        z x sigma x sqrt(cycle); max = min + use over one more cycle. The
        planner's par defaults to the suggestion."""
        require_role(self.env, PLANNER, what="Computing a van par")
        today = dhaka_today()  # M43-21
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Compute a proposed van par")
            daily = consumed_by_day(
                rec.env,
                rec.company_id,
                rec.part_id,
                rec.van_location_id,
                today - timedelta(days=rec.history_days),
                rec.history_days,
            )
            mean, std = mean_and_stddev(daily)
            z = z_for(rec.service_level_pct)  # M43-08: inverse normal, any level
            cycle = rec.replenish_days
            low = ceil(round(mean * cycle + z * std * sqrt(cycle), 6))
            high = ceil(round(low + mean * cycle, 6))
            vals = {
                "avg_daily_demand": round(mean, 4),
                "demand_stddev": round(std, 4),
                "suggested_min": float(low),
                "suggested_max": float(high),
                "computed_on": fields.Datetime.now(),
            }
            rec._guarded().write(vals)
            if not (rec.min_qty or rec.max_qty):
                rec._guarded().write({"min_qty": float(low), "max_qty": float(high)})
        return True

    def action_approve(self):
        """BRU-DPL-12: computed by M43, approved by someone other than its
        author, then enforced by M15 as the van's reorder rule."""
        require_role(self.env, APPROVER, what="Approving a van par")
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Approve a proposed van par")
            refuse_self_decision(
                self.env, rec.create_uid | rec.prepared_by_id, "Van par %s" % rec.name
            )
            if not rec.computed_on:
                raise UserError(
                    "Van par %s is not computed from the van's M15 use: compute it first."
                    % rec.name
                )
            if rec.max_qty <= rec.min_qty:
                raise UserError("Van par %s: the maximum must exceed the minimum." % rec.name)
            deviates = (rec.min_qty, rec.max_qty) != (rec.suggested_min, rec.suggested_max)
            if deviates and not (rec.deviation_reason or "").strip():
                raise UserError(
                    "Van par %s differs from the computed %g / %g: record why."
                    % (rec.name, rec.suggested_min, rec.suggested_max)
                )
            why = self.env["fix.demand.network.policy"]._refusal(
                rec.company_id, rec.part_id, rec.van_location_id
            )
            if why:
                raise UserError("Van par %s: %s." % (rec.name, why))
            rule = self.env["fix.reorder.rule"]._fix_publish_from_plan(
                rec.part_id, rec.van_location_id, rec.min_qty, rec.max_qty, rec.name
            )
            rec._decide(
                "applied",
                approved_by_id=self.env.user.id,
                approved_on=fields.Datetime.now(),
                published_rule_id=rule[:1].id if rule else False,
            )
        return True

    def action_reject(self):
        require_role(self.env, APPROVER, what="Rejecting a van par")
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Reject a proposed van par")
            rec._decide(
                "rejected", approved_by_id=self.env.user.id, approved_on=fields.Datetime.now()
            )
        return True


# =====================================================================
# The policy reads the targets and the network policy
# =====================================================================
class FixDemandPolicyCapture(models.Model):
    _inherit = "fix.demand.policy"

    segment_target = fields.Char(string="Segment Target", compute="_compute_segment_target")

    @api.depends("product_id", "location_id", "company_id")
    def _compute_segment_target(self):
        Target = self.env["fix.demand.service.target"]
        for rec in self:
            target = Target._for_policy(rec)
            # target_pct is a float since M43-08 (any level): 98.0 reads "98%"
            rec.segment_target = (
                "%g%% (%s)" % (float(target.target_pct or 0.0), target.name) if target else False
            )

    def action_activate(self):
        Target = self.env["fix.demand.service.target"]
        Network = self.env["fix.demand.network.policy"]
        for rec in self:
            target = Target._for_policy(rec)
            if target and rec.service_level_pct + 1e-9 < target.target_pct:
                raise UserError(
                    "Policy %s serves %s%% but the service-level target %s for this segment "
                    "is %s%% (FR-DPL-018): raise the service level."
                    % (rec.name, rec.service_level_pct, target.name, target.target_pct)
                )
            why = Network._refusal(rec.company_id, rec.part_id, rec.location_id)
            if why:
                raise UserError("Policy %s: %s." % (rec.name, why))
        return super().action_activate()
