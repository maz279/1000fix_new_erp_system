# fix_rental_fleet — M13: the fleet, kits, deposit ledger, condition reports
# and turnaround records the workspace screens read. The reservation and its
# damage lines already live in fix_rental_asset.py; these models compose with
# them (one fleet item per reservation, one deposit event per money movement).
#
# A05 workflow audit (2026-11-03): the asset status, the turnaround state and
# the ledger's GL state were writable by anyone; a refused GL posting left a
# posted journal entry that Repost doubled; rental staff never reached the GL;
# the wipe gate was opt-in and accepted a typed "x" as a SHA-256. Now the
# workflow fields are guarded, the ledger is immutable and posts as a system
# transition inside a savepoint, and a data-bearing unit is released only on a
# verified M06 certificate bound to its serial.
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from . import rental_policy as policy
from .rental_gl import (
    PAYMENT_METHOD,
    post_rental_move,
    rental_account,
    tender_account,
)

_COST_BASIS = ("purchase_cost", "residual_value", "useful_life_days", "acquisition_date")


def _refuse(message):
    raise ValidationError(message)


def _straight_line_nbv(cost, residual, life, acquisition_date, today):
    """IAS 16 straight-line net book value (the asset's own computation)."""
    cost = cost or 0.0
    residual = residual or 0.0
    life = life or 1095
    daily = (cost - residual) / float(life) if life > 0 and cost > residual else 0.0
    days = (today - acquisition_date).days if acquisition_date and acquisition_date <= today else 0
    accum = min(daily * days, max(cost - residual, 0.0))
    return round(max(residual, cost - accum), 2)


class FixRentalAsset(models.Model):
    """A serialised item in the rental fleet (the Fleet Register unit)."""

    _name = "fix.rental.asset"
    _description = "Rental Fleet Asset"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "name"

    # A11 audit P2 (A05 area): the retirement write-off's DOFA stamp used to
    # be given by whoever pressed Approve while holding the tier — no request,
    # no named approver, no deadline, no delegate, no history. It is now a
    # routed M63 request: whoever retires the unit asks
    # (action_request_approval), the engine routes to the holders of the tier
    # the net book value derives (minus the raiser and the amount-changer),
    # and the DOFA stamp is given from the approver's inbox only. The net book
    # value is the approval amount, so a revaluation while the request is
    # pending withdraws it.
    _approval_domain = "rental_asset_writeoff"
    _approval_routed = True

    # A05 DOFA matrix — Rental Fleet Asset Retirement / Write-Off: never a
    # branch decision (tier 1 is NOT permitted); Fleet Maintenance Lead from
    # BDT 50k, Head of Supply Chain from 250k, CEO & CFO above 1M.
    _DOFA_THRESHOLDS = [
        (0.0, "tier_0"),
        (250000.0, "tier_2"),
        (1000000.0, "tier_3"),
        (float("inf"), "tier_4"),
    ]

    def _dofa_thresholds(self):
        return self._DOFA_THRESHOLDS

    def _m49_book_value(self, fixed_asset=None):
        fa = (self.fixed_asset_id if fixed_asset is None else fixed_asset).sudo()
        if not fa or fa.state != "active":
            return 0.0
        return round(fa.book_nbv or 0.0, 2)

    def _dofa_amount(self) -> float:
        """The book value written off by retirement — never the purchase
        cost (a fully depreciated asset risks only its residual). When the
        unit is capitalised in M49, the higher of the two book values: M49 is
        the ledger's own figure and cannot be typed down here."""
        self.ensure_one()
        return max(self.net_book_value or 0.0, self._m49_book_value())

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (net book value)" % self._dofa_amount()

    @api.depends("net_book_value", "fixed_asset_id")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    name = fields.Char(string="Asset Code", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    rental_sku_id = fields.Many2one(
        "fix.rental.sku", string="Rental SKU", required=True, ondelete="restrict", index=True
    )
    device_id = fields.Many2one("fix.device", string="Device (M17)", ondelete="set null")
    fixed_asset_id = fields.Many2one(
        "fix.fixed.asset",
        string="Fixed Asset (M49)",
        ondelete="set null",
        help="The capitalised asset in the fixed-asset register; retirement hands it "
        "to M49 disposal",
    )
    disposal_id = fields.Many2one(
        "fix.asset.disposal",
        string="M49 Disposal",
        readonly=True,
        copy=False,
        ondelete="set null",
        help="The M49 write-off document started when the unit was retired",
    )
    serial_no = fields.Char(string="Serial Number")
    category = fields.Selection(
        [
            ("camera", "Camera & Lens"),
            ("laptop", "Laptop & PC"),
            ("projector", "Projector & Display"),
            ("audio", "Audio & Lighting"),
            ("tool", "Power Tool"),
            ("medical", "Medical Device"),
            ("network", "Network Equipment"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    condition_grade = fields.Selection(
        [("a", "A — Like new"), ("b", "B — Good"), ("c", "C — Fair"), ("d", "D — Poor")],
        required=True,
        default="a",
    )
    battery_health_pct = fields.Integer(string="Battery Health %", default=100)
    status = fields.Selection(
        [
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("out", "On Rent"),
            ("maintenance", "In Maintenance"),
            ("retired", "Retired"),
        ],
        required=True,
        default="available",
        index=True,
        readonly=True,
        copy=False,
    )
    acquisition_date = fields.Date()
    purchase_cost = fields.Monetary(currency_field="currency_id")
    residual_value = fields.Monetary(
        string="Residual Value", currency_field="currency_id", default=0.0
    )
    useful_life_days = fields.Integer(
        string="Useful Life (Days)", default=1095, help="3-year statutory useful life under IAS 16"
    )
    daily_depreciation = fields.Monetary(
        string="Daily Depreciation (BDT)",
        currency_field="currency_id",
        compute="_compute_depreciation",
        store=True,
    )
    net_book_value = fields.Monetary(
        string="Net Book Value (BDT)",
        currency_field="currency_id",
        compute="_compute_depreciation",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    accumulated_depreciation = fields.Monetary(
        string="Accumulated Depreciation (BDT)",
        currency_field="currency_id",
        compute="_compute_depreciation",
        store=True,
        help="Straight-line depreciation accrued since acquisition (IAS 16), "
        "capped at cost − residual",
    )
    reservation_ids = fields.One2many(
        "fix.rental.reservation", "rental_asset_id", string="Reservation History"
    )
    turnaround_ids = fields.One2many("fix.rental.turnaround", "rental_asset_id")
    last_service_date = fields.Date(string="Last Preventive Service")
    next_service_due = fields.Date(
        string="Next Service Due",
        help="PM due date; turnaround resets it on completion",
    )
    total_repair_cost = fields.Monetary(
        string="Lifetime Repair Cost",
        currency_field="currency_id",
        help="Rolled-up workshop cost of keeping this unit in the fleet",
    )
    rental_days_total = fields.Integer(
        string="Rental Days (Lifetime)",
        compute="_compute_utilisation",
        store=True,
    )
    cumulative_revenue = fields.Monetary(
        string="Cumulative Revenue",
        currency_field="currency_id",
        compute="_compute_utilisation",
        store=True,
    )
    utilization_rate_30d = fields.Float(
        string="Utilisation % (30 days)",
        compute="_compute_utilisation",
        help="Rented days in the last 30 ÷ 30 — the fleet-health KPI's numerator",
    )
    retired_on = fields.Date(readonly=True, copy=False)
    retirement_reason = fields.Char()
    notes = fields.Text()

    @api.depends("purchase_cost", "residual_value", "useful_life_days", "acquisition_date")
    def _compute_depreciation(self):
        today = fields.Date.context_today(self)
        for rec in self:
            cost = rec.purchase_cost or 0.0
            residual = rec.residual_value or 0.0
            life = rec.useful_life_days or 1095
            daily = (cost - residual) / float(life) if life > 0 and cost > residual else 0.0
            rec.daily_depreciation = round(daily, 2)

            if rec.acquisition_date and rec.acquisition_date <= today:
                days_in_service = (today - rec.acquisition_date).days
            else:
                days_in_service = 0

            accum_deprec = min(daily * days_in_service, max(cost - residual, 0.0))
            nbv = max(residual, cost - accum_deprec)
            rec.accumulated_depreciation = round(accum_deprec, 2)
            rec.net_book_value = round(nbv, 2)

    @api.depends(
        "reservation_ids.state",
        "reservation_ids.duration_days",
        "reservation_ids.rental_charge",
        "reservation_ids.late_fee",
        "reservation_ids.date_from",
        "reservation_ids.date_to",
    )
    def _compute_utilisation(self):
        from datetime import timedelta

        today = fields.Date.context_today(self)
        window_start = today - timedelta(days=29)
        for rec in self:
            live = rec.reservation_ids.filtered(lambda r: r.state != "cancelled")
            rec.rental_days_total = sum(live.mapped("duration_days"))
            rec.cumulative_revenue = sum(
                (r.rental_charge or 0.0) + (r.late_fee or 0.0) for r in live
            )
            rented = sum(
                max((min(r.date_to, today) - max(r.date_from, window_start)).days + 1, 0)
                for r in live
                if r.date_from
                and r.date_to
                and r.state in ("reserved", "delivered", "active")
                and r.date_from <= today
                and r.date_to >= window_start
            )
            rec.utilization_rate_30d = round(min(rented, 30) / 30.0 * 100.0, 1)

    _battery_range = models.Constraint(
        "CHECK (battery_health_pct >= 0 AND battery_health_pct <= 100)",
        "Battery health must be a percentage between 0 and 100",
    )
    _purchase_cost_positive = models.Constraint(
        "CHECK (purchase_cost >= 0)",
        "Purchase cost cannot be negative",
    )

    # ---- guard -----------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"status", "retired_on", "disposal_id"}

    def _fix_guard_refuse(self, names):
        try:
            super()._fix_guard_refuse(names)
        except UserError as exc:
            _refuse(str(exc))

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(r.status == "retired" for r in self):
            locked |= {
                n for n, f in self._fields.items() if f.store and not n.startswith("message_")
            }
        return locked

    def _at_risk_with(self, vals):
        """The retirement amount at risk if `vals` were written."""
        self.ensure_one()
        to_date = fields.Date.to_date
        acq = (
            to_date(vals["acquisition_date"])
            if "acquisition_date" in vals
            else self.acquisition_date
        )
        nbv = _straight_line_nbv(
            vals.get("purchase_cost", self.purchase_cost),
            vals.get("residual_value", self.residual_value),
            vals.get("useful_life_days", self.useful_life_days),
            acq,
            fields.Date.context_today(self),
        )
        fa = self.fixed_asset_id
        if "fixed_asset_id" in vals:
            fa = self.env["fix.fixed.asset"].browse(vals["fixed_asset_id"] or [])
        return max(nbv, self._m49_book_value(fa))

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.status == "retired":
                    changed = [
                        n
                        for n in vals
                        if n in rec._fields
                        and rec._fields[n].store
                        and not n.startswith("message_")
                        and rec._fix_guard_differs(n, vals[n], rec[n])
                    ]
                    if changed:
                        _refuse("Fleet asset %s is retired: its record is final." % rec.name)
                if set(vals) & (set(_COST_BASIS) | {"fixed_asset_id"}):
                    # M13-10: the book value decides the retirement tier, so a
                    # user may not type it down (cost to 0, a shorter life, an
                    # earlier acquisition, unlinking M49). Raising it is fine.
                    before = rec._dofa_amount()
                    after = rec._at_risk_with(vals)
                    if after + 0.005 < before:
                        _refuse(
                            "Fleet asset %s: the change would cut its book value from %.2f "
                            "to %.2f. The cost basis is fixed at acquisition; a write-down "
                            "is an M49 impairment, not an edit." % (rec.name, before, after)
                        )
        return super().write(vals)

    # ---- actions ---------------------------------------------------------
    def action_retire(self):
        """Retire a fleet unit. A unit on rent or booked must come back (or
        be cancelled) first; the write-off of its book value carries a routed
        DOFA approval (the A05 matrix forbids tier-1 retirement outright), and
        the M49 fixed asset is handed to its disposal."""
        Res = self.env["fix.rental.reservation"].sudo()
        for rec in self:
            if rec.status == "retired":
                raise UserError("%s is already retired" % rec.name)
            if rec.status in ("out", "reserved"):
                raise ValidationError("Return the asset before retiring it")
            if Res.search_count(
                [
                    ("rental_asset_id", "=", rec.id),
                    ("state", "in", ("reserved", "delivered", "active")),
                ]
            ):
                raise ValidationError(
                    "%s still has open bookings: cancel or complete them first" % rec.name
                )
            rec._dofa_assert_approved("Fleet asset retirement")
            rec._guarded().write(
                {"status": "retired", "retired_on": fields.Date.context_today(self)}
            )
            fa = rec.fixed_asset_id.sudo()
            if fa and fa.state == "active":
                result = fa.action_dispose() or {}
                disposal_ids = result.get("disposal_ids") or []
                if disposal_ids:
                    rec._guarded().write({"disposal_id": disposal_ids[0]})
                rec.message_post(
                    body="Retired; M49 disposal %s started for %s (finance approves and posts it)."
                    % (rec.disposal_id.display_name or "-", fa.display_name)
                )
        return True

    def action_send_to_maintenance(self):
        """Available -> maintenance for preventive maintenance: a turnaround
        is opened, and only its completion releases the unit."""
        for rec in self:
            if rec.status != "available":
                raise UserError(
                    "%s is %s: only an available unit goes to maintenance" % (rec.name, rec.status)
                )
            rec._guarded().write({"status": "maintenance"})
            rec._open_turnaround()
        return True

    def _open_turnaround(self):
        self.ensure_one()
        open_ta = self.turnaround_ids.filtered(lambda t: t.state not in ("ready", "retired"))
        if open_ta:
            return open_ta[:1]
        return (
            self.env["fix.rental.turnaround"]
            ._guarded()
            .create(
                {
                    "rental_asset_id": self.id,
                    "company_id": self.company_id.id,
                    "returned_on": fields.Date.context_today(self),
                    "grade_before": self.condition_grade,
                }
            )
        )

    def _approval_on_rejected(self, comment):
        """A11 audit P2: an inbox rejection of the write-off is evidence on
        the asset's thread — the retirement does not proceed."""
        for rec in self:
            rec.message_post(
                body="Retirement write-off rejected by %s: %s"
                % (rec.env.user.name, comment or "no comment recorded")
            )

    def action_ready(self):
        """A unit returns to the fleet only through its turnaround (checklist
        and wipe gate). An asset in maintenance with no open turnaround gets
        one opened; it is released when that turnaround is completed."""
        for rec in self:
            if rec.status == "retired":
                raise UserError(
                    "%s is retired — reactivation is a reversal of a governed write-off, "
                    "not a status flip" % rec.name
                )
            if rec.status != "maintenance":
                raise UserError(
                    "%s is %s: only a unit in maintenance is released to the fleet, and "
                    "only through its turnaround." % (rec.name, rec.status)
                )
            turnaround = rec.turnaround_ids.filtered(lambda t: t.state not in ("ready", "retired"))[
                :1
            ]
            if not turnaround:
                turnaround = rec._open_turnaround()
                rec.message_post(
                    body="Turnaround %s opened: the unit is released when it is completed."
                    % turnaround.name
                )
                continue
            turnaround.action_ready()
        return True


class FixRentalKit(models.Model):
    """A kit bundles a rental SKU with its accessories and deposit.

    The kit deposit is the minimum security deposit of a reservation that
    names the kit (cd_rental_asset.enforce_sku_deposit)."""

    _name = "fix.rental.kit"
    _description = "Rental Kit"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rental_sku_id = fields.Many2one(
        "fix.rental.sku", string="Rental SKU", required=True, ondelete="restrict"
    )
    accessories = fields.Text(
        string="Included Accessories",
        help="One per line: what ships with the kit and must come back",
    )
    accessory_count = fields.Integer(
        compute="_compute_accessory_count", store=True, string="Accessories"
    )
    deposit = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    active = fields.Boolean(default=True)

    @api.depends("accessories")
    def _compute_accessory_count(self):
        for rec in self:
            lines = (rec.accessories or "").splitlines()
            rec.accessory_count = len([line for line in lines if line.strip()])


# Every business field of a ledger movement is written by the money path only.
_LEDGER_GUARDED = frozenset(
    {
        "name",
        "company_id",
        "reservation_id",
        "kind",
        "amount",
        "currency_id",
        "method",
        "date",
        "journal_entry_id",
        "gl_state",
        "gl_note",
        "payment_execution_id",
        "damage_id",
    }
)


class FixRentalDeposit(models.Model):
    """One money movement against a rental's security deposit.

    Immutable: created only by the rental money path (_post), never typed;
    its amount, kind and GL link change only through the posting itself. The
    cashier's MFS/bank reference and a note stay editable until it posts."""

    _name = "fix.rental.deposit"
    _description = "Rental Deposit Movement"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    reservation_id = fields.Many2one(
        "fix.rental.reservation", required=True, ondelete="restrict", index=True
    )
    customer_id = fields.Many2one(
        related="reservation_id.customer_id", string="Customer", store=True, index=True
    )
    kind = fields.Selection(
        [
            ("collect", "Collected"),
            ("refund", "Refunded"),
            ("deduction", "Deducted"),
            ("forfeit", "Forfeited"),
        ],
        required=True,
        default="collect",
        readonly=True,
    )
    amount = fields.Monetary(required=True, currency_field="currency_id", readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    method = fields.Selection(
        [
            ("cash", "Cash"),
            ("bkash", "bKash"),
            ("nagad", "Nagad"),
            ("card", "Card / SSLCOMMERZ"),
            ("bank", "Bank Transfer"),
        ],
        required=True,
        default="cash",
        readonly=True,
    )
    reference = fields.Char()
    date = fields.Date(required=True, default=fields.Date.context_today, readonly=True)
    note = fields.Char()
    journal_entry_id = fields.Many2one(
        "account.move",
        string="GL Journal Entry",
        readonly=True,
        copy=False,
        help="Dual-entry General Ledger move behind this movement",
    )
    gl_state = fields.Selection(
        [
            ("pending", "GL Pending"),
            ("posted", "GL Posted"),
            ("refund_queued", "Refund Queued (M50)"),
            ("failed", "GL Failed"),
        ],
        string="GL State",
        default="pending",
        required=True,
        copy=False,
        tracking=True,
        readonly=True,
        help="Money movements post to the General Ledger or say why they "
        "did not — 'GL Ready' notes and silent sub-ledger rows are not "
        "an audit trail.",
    )
    gl_note = fields.Char(
        string="GL Note",
        copy=False,
        readonly=True,
        help="Why a movement carries no journal entry (legacy rows, refused postings)",
    )
    payment_execution_id = fields.Many2one(
        "fix.payment.execution",
        string="Refund Instruction (M50)",
        readonly=True,
        copy=False,
        ondelete="set null",
        help="Treasury instruction returning the customer's money — M50 posts "
        "Dr deposits held / Cr bank when the bank confirms it left",
    )
    damage_id = fields.Many2one(
        "fix.rental.damage",
        string="Offset Damage Record",
        ondelete="set null",
        index=True,
        readonly=True,
        help="The proven damage/late-fee charge this deduction settles",
    )

    _amount_positive = models.Constraint(
        "CHECK (amount >= 0)", "A deposit movement cannot be negative"
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | _LEDGER_GUARDED

    def _fix_guard_refuse(self, names):
        try:
            super()._fix_guard_refuse(names)
        except UserError as exc:
            _refuse(str(exc))

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(r.gl_state in ("posted", "refund_queued") for r in self):
            locked |= {"reference", "note"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            _refuse(
                "Deposit movements are made by the rental money path (reserve, close, "
                "cancel), which posts them to the General Ledger or queues the refund "
                "with treasury. A movement cannot be typed."
            )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.rental.deposit") or "DEP/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open() and set(vals) & {"reference", "note"}:
            for rec in self.filtered(lambda r: r.gl_state in ("posted", "refund_queued")):
                for name in {"reference", "note"} & set(vals):
                    if rec._fix_guard_differs(name, vals[name], rec[name]):
                        _refuse("Deposit movement %s is posted: it is final." % rec.name)
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            _refuse("The deposit ledger is append-only: a movement is never deleted.")
        return super().unlink()

    def _post(self, reservation, kind, amount, note="", damage=None, method="cash"):
        """One money movement against a rental deposit — sub-ledger row AND
        General Ledger, or an honest refusal.

        collect    Dr cash/bank/MFS clearing .... Cr customer deposits held
        deduction  Dr customer deposits held ..... Dr→Cr damage/late-fee recovery income
        forfeit    Dr customer deposits held ..... Cr recovery income
        refund     no GL here: an M50 payment instruction is queued; treasury
                   debits the deposits-held liability when the bank confirms
                   the money left (the estate's two-stage money rule).

        The accounts come from rental_gl (statutory chart 2-40-20-010 /
        4-90-10-010, overridable per system parameter) and the posting goes
        through M19's post_with_dimensions, so the COA-01/02/03 rules bind
        rentals exactly as they bind invoices. A missing account or booking
        branch REFUSES the movement — money is never parked on a guess."""
        if not amount or amount <= 0:
            return self.browse()
        vals = {
            "reservation_id": reservation.id,
            "company_id": reservation.company_id.id,
            "currency_id": reservation.currency_id.id,
            "kind": kind,
            "amount": amount,
            "method": method,
            "note": note or dict(self._fields["kind"].selection).get(kind, ""),
            "damage_id": damage.id if damage else False,
        }
        # the guard token stays inside this transition: hand back a clean record
        rec = self.browse(self._guarded().create(vals).id)
        if kind == "refund":
            rec._queue_refund()
        else:
            rec._post_gl()
        return rec

    def _adopt_orphan_move(self):
        """A posting refused before the savepoint existed (M13-1) left posted
        moves linked to no row. Repost adopts the matching one instead of
        posting the money a second time."""
        self.ensure_one()
        reservation = self.reservation_id
        Move = self.env["account.move"].sudo()
        linked = self.sudo().search([("journal_entry_id", "!=", False)]).mapped("journal_entry_id")
        candidates = Move.search(
            [
                ("ref", "=", "RDEP %s — %s" % (reservation.name, self.kind)),
                ("state", "=", "posted"),
                ("company_id", "=", reservation.company_id.id),
                ("id", "not in", linked.ids),
            ]
        )
        for move in candidates:
            if abs((move.amount_total or 0.0) - (self.amount or 0.0)) <= 0.005:
                return move
        return Move.browse()

    def _post_gl(self, adopt=False):
        """Post this movement's dual-entry (collect / deduction / forfeit).

        A system transition: the business action (reserve, close) ran under
        the user's own rights; the posting itself runs as the system, so a
        rental clerk needs no accounting access (M13-2), inside a savepoint,
        so a refusal raised after the move was created leaves no move behind
        (M13-1)."""
        for rec in self:
            if rec.journal_entry_id:
                continue  # idempotent: one movement, one journal entry
            reservation = rec.reservation_id.sudo()
            company = reservation.company_id
            env = self.env(su=True)
            try:
                if adopt:
                    orphan = rec._adopt_orphan_move()
                    if orphan:
                        rec._guarded().write(
                            {
                                "journal_entry_id": orphan.id,
                                "gl_state": "posted",
                                "gl_note": "Adopted the journal entry left by an earlier "
                                "refused posting",
                            }
                        )
                        continue
                with self.env.cr.savepoint():
                    liability = rental_account(env, company, "deposit_liability")
                    partner = reservation.customer_id
                    if rec.kind == "collect":
                        tender = tender_account(env, company, rec.method)
                        lines = [
                            (
                                tender,
                                "%s: %s received" % (rec.name, rec.method),
                                rec.amount,
                                0.0,
                                partner,
                            ),
                            (liability, "%s: deposits held" % rec.name, 0.0, rec.amount, partner),
                        ]
                    elif rec.kind in ("deduction", "forfeit"):
                        income = rental_account(env, company, "retention_income")
                        lines = [
                            (
                                liability,
                                "%s: deposits held applied" % rec.name,
                                rec.amount,
                                0.0,
                                partner,
                            ),
                            (
                                income,
                                "%s: %s recovery" % (rec.name, rec.kind),
                                0.0,
                                rec.amount,
                                None,
                            ),
                        ]
                    else:
                        raise UserError(
                            "Deposit movement %s is a %s: refunds queue with treasury, "
                            "they do not post here" % (rec.name, rec.kind)
                        )
                    move = post_rental_move(
                        env,
                        reservation,
                        rec.date,
                        "RDEP %s — %s" % (reservation.name, rec.kind),
                        lines,
                    )
                rec._guarded().write(
                    {"journal_entry_id": move.id, "gl_state": "posted", "gl_note": False}
                )
            except UserError as exc:
                # The money moved in the real world; the ledger row must exist
                # whatever the GL configuration says. The savepoint rolled the
                # refused move back; the refusal is pinned on the row
                # (gl_state=failed + the exact reason), chatter carries it, and
                # action_repost_gl posts it once the account or the booking
                # branch is configured. Never a silent skip, never a lost
                # collection, never a second posting.
                reason = str(exc)[:250]
                rec._guarded().write({"gl_state": "failed", "gl_note": reason})
                rec.sudo().message_post(
                    body="GL posting refused: %s — fix the configuration and press "
                    "Repost GL." % reason
                )

    def _queue_refund(self):
        """Queue the refund with M50 treasury (idempotent on this movement).
        The deposits-held liability is the account the confirmation debits,
        so the customer's money leaves the books exactly once. A system
        hand-off: treasury records are not the rental clerk's to touch."""
        env = self.env(su=True)
        for rec in self:
            if rec.kind != "refund":
                raise UserError("Only refunds queue a treasury instruction")
            if rec.payment_execution_id:
                continue
            reservation = rec.reservation_id.sudo()
            liability = rental_account(env, reservation.company_id, "deposit_liability")
            journal = env["account.journal"].search(
                [("type", "=", "bank"), ("company_id", "=", reservation.company_id.id)], limit=1
            )
            payment = env["fix.payment.execution"].create(
                {
                    "company_id": reservation.company_id.id,
                    "operating_unit_id": (
                        reservation.operating_unit_id
                        or env["operating.unit"].search(
                            [("company_id", "=", reservation.company_id.id)], limit=1
                        )
                    ).id,
                    "source_model": "fix.rental.deposit",
                    "source_id": rec.id,
                    "payee": reservation.customer_id.name,
                    "partner_id": reservation.customer_id.id,
                    "amount": rec.amount,
                    "method": PAYMENT_METHOD.get(rec.method, "bank_transfer"),
                    "debit_account_id": liability.id,
                    "journal_id": journal.id,
                }
            )
            rec._guarded().write(
                {
                    "payment_execution_id": payment.id,
                    "gl_state": "refund_queued",
                    "gl_note": "Refund queued as %s — GL posts on bank confirmation (M50)"
                    % payment.name,
                }
            )

    def action_repost_gl(self):
        """Operator recovery for a movement whose posting was refused (the
        account or branch was configured after the fact). Only an unposted
        movement reposts, and a move an earlier refusal left behind is
        adopted rather than posted again."""
        for rec in self:
            if rec.journal_entry_id or rec.gl_state == "posted":
                raise UserError(
                    "%s already carries journal entry %s"
                    % (rec.name, rec.journal_entry_id.name or "-")
                )
            if rec.kind == "refund":
                raise UserError("Refunds post through M50, not here")
            if rec.gl_state not in ("failed", "pending"):
                raise UserError("%s is %s: nothing to repost" % (rec.name, rec.gl_state))
            rec._post_gl(adopt=True)
        return True


class FixRentalCondition(models.Model):
    """A pre-delivery or post-return condition report for one rental.

    The handover evidence: a rental is not delivered without a pre-delivery
    report, nor assessed or closed without a post-return one. A report is
    written at its stage and is final once the rental moves past it."""

    _name = "fix.rental.condition"
    _description = "Rental Condition Report"
    _order = "reported_on desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    reservation_id = fields.Many2one(
        "fix.rental.reservation", required=True, ondelete="cascade", index=True
    )
    rental_asset_id = fields.Many2one("fix.rental.asset", string="Fleet Asset", ondelete="set null")
    report_type = fields.Selection(
        [("pre_delivery", "Pre-Delivery"), ("post_return", "Post-Return")],
        required=True,
        default="post_return",
    )
    grade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], required=True, default="a"
    )
    battery_health_pct = fields.Integer(string="Battery Health %", default=100)
    charge_cycles = fields.Integer(
        string="Charge Cycles", help="Battery cycle count read at inspection"
    )
    charger_ok = fields.Boolean(string="Charger Present", default=True)
    case_ok = fields.Boolean(string="Case / Bag Present", default=True)
    screen_ok = fields.Boolean(string="Screen Intact", default=True)
    ports_ok = fields.Boolean(string="Ports & Connectors OK", default=True)
    body_condition_rating = fields.Selection(
        [("mint", "Mint"), ("good", "Good"), ("fair", "Fair"), ("poor", "Poor")],
        string="Body Condition",
    )
    maintenance_required = fields.Boolean(
        string="Maintenance Required",
        help="The 15-point check failed something the turnaround must fix",
    )
    notes = fields.Text()
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    photos_ref = fields.Char(string="Photo Evidence Ref")
    reported_on = fields.Date(required=True, default=fields.Date.context_today)

    _battery_range = models.Constraint(
        "CHECK (battery_health_pct >= 0 AND battery_health_pct <= 100)",
        "Battery health must be a percentage between 0 and 100",
    )

    _STAGE_STATES = {
        "pre_delivery": ("draft", "reserved"),
        "post_return": ("returned", "damage_assess"),
    }

    def _stage_open(self, reservation, report_type):
        return reservation.state in self._STAGE_STATES.get(report_type, ())

    def _fix_form_locked_fields(self) -> set:
        if self and any(not r._stage_open(r.reservation_id, r.report_type) for r in self):
            return {n for n, f in self._fields.items() if f.store}
        return {"reservation_id", "report_type"} if self else set()

    @api.model_create_multi
    def create(self, vals_list):
        Res = self.env["fix.rental.reservation"]
        for vals in vals_list:
            res = Res.browse(vals.get("reservation_id")).exists()
            if res:
                if not vals.get("rental_asset_id") and res.rental_asset_id:
                    vals["rental_asset_id"] = res.rental_asset_id.id
                rtype = vals.get("report_type") or "post_return"
                if not self.env.su and not self._stage_open(res, rtype):
                    _refuse(
                        "A %s condition report is written while the rental is %s; rental "
                        "%s is %s."
                        % (
                            rtype.replace("_", "-"),
                            " or ".join(self._STAGE_STATES[rtype]),
                            res.name,
                            res.state,
                        )
                    )
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.rental.condition") or "COND/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self.env.su:
            for rec in self:
                for name in ("reservation_id", "report_type"):
                    if name in vals and vals[name] != (
                        rec[name].id if name == "reservation_id" else rec[name]
                    ):
                        _refuse("A condition report stays on its rental and stage.")
                if not self._stage_open(rec.reservation_id, rec.report_type):
                    _refuse(
                        "Condition report %s is final: rental %s has moved past its stage."
                        % (rec.name, rec.reservation_id.name)
                    )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(
            not r._stage_open(r.reservation_id, r.report_type) for r in self
        ):
            _refuse("A condition report is handover evidence: it is kept once used.")
        return super().unlink()


_TURN_GUARDED = frozenset(
    {
        "state",
        "ready_timestamp",
        "available_on",
        "rental_asset_id",
        "reservation_id",
        "returned_on",
        "grade_before",
        "nist_wipe_hash",
    }
)


class FixRentalTurnaround(models.Model):
    """The clean → inspect → re-grade → ready loop after a return.

    Opened by the return (or by sending a unit to maintenance), never typed;
    its state moves only through its actions, and it is final once ready."""

    _name = "fix.rental.turnaround"
    _description = "Rental Turnaround"
    _inherit = ["fix.guarded.mixin"]
    _order = "returned_on desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rental_asset_id = fields.Many2one(
        "fix.rental.asset", string="Fleet Asset", required=True, ondelete="cascade", index=True
    )
    reservation_id = fields.Many2one(
        "fix.rental.reservation", string="Reservation", ondelete="set null"
    )
    returned_on = fields.Date(required=True, default=fields.Date.context_today)
    cleaning_done = fields.Boolean()
    sensor_cleaned = fields.Boolean(string="Sensors Cleaned")
    connectors_inspected = fields.Boolean(string="Connectors Inspected")
    firmware_updated = fields.Boolean(string="Firmware Updated")
    inspection_done = fields.Boolean()
    # NIST SP 800-88 sanitization of the returned unit's storage (the
    # customer's data leaves with the device; M06's certificate is the
    # cryptographic evidence, the hash the tamper-proof fingerprint)
    data_wipe_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate",
        string="Data Wipe Certificate (M06)",
        ondelete="set null",
        index=True,
        help="M06 NIST SP 800-88 wipe evidence for the returned unit",
    )
    nist_wipe_hash = fields.Char(
        string="NIST Wipe Hash (SHA-256)",
        copy=False,
        readonly=True,
        help="The verified evidence hash of the M06 certificate that released the unit "
        "(copied from the certificate, never typed)",
    )
    memory_card_wiped = fields.Boolean(string="Memory Card Wiped")
    internal_storage_factory_reset = fields.Boolean(string="Internal Storage Reset")
    grade_before = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], string="Grade Before"
    )
    regrade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], string="Re-Graded As"
    )
    battery_health_after_pm = fields.Integer(
        string="Battery Health After PM %",
        help="Measured after cleaning/PM; the regrade must reflect it",
    )
    functional_score_pct = fields.Integer(
        string="Functional Score %",
        help="Bench functional test result after turnaround (0-100)",
    )
    technician_id = fields.Many2one("hr.employee", string="Turnaround Technician")
    ready_timestamp = fields.Datetime(
        string="Ready Timestamp",
        readonly=True,
        copy=False,
        help="When the unit was released to the fleet",
    )
    available_on = fields.Date(string="Available From", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("cleaning", "Cleaning"),
            ("inspection", "Inspection"),
            ("ready", "Ready"),
            ("retired", "Retired"),
        ],
        required=True,
        default="pending",
        readonly=True,
        copy=False,
    )
    notes = fields.Char()

    _battery_pm_range = models.Constraint(
        "CHECK (battery_health_after_pm >= 0 AND battery_health_after_pm <= 100 "
        "AND functional_score_pct >= 0 AND functional_score_pct <= 100)",
        "Battery health and functional score are percentages between 0 and 100",
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | _TURN_GUARDED

    def _fix_guard_refuse(self, names):
        try:
            super()._fix_guard_refuse(names)
        except UserError as exc:
            _refuse(str(exc))

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(r.state in ("ready", "retired") for r in self):
            locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            _refuse(
                "A turnaround is opened by the rental return or by sending the unit to "
                "maintenance, not typed."
            )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.rental.turnaround") or "TURN/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            final = self.filtered(lambda r: r.state in ("ready", "retired"))
            for rec in final:
                if any(
                    n in rec._fields and rec._fix_guard_differs(n, vals[n], rec[n]) for n in vals
                ):
                    _refuse("Turnaround %s is %s: it is final." % (rec.name, rec.state))
        return super().write(vals)

    def _data_bearing(self):
        self.ensure_one()
        return self.rental_asset_id.category in policy.data_bearing_categories(self.env)

    def _release_denial(self):
        """'' when this turnaround may release its unit, else why not."""
        self.ensure_one()
        asset = self.rental_asset_id
        if self.state not in ("pending", "cleaning", "inspection"):
            return "turnaround %s is %s" % (self.name, self.state)
        if asset.status != "maintenance":
            return "fleet asset %s is %s, not in maintenance" % (asset.name, asset.status)
        missing = [
            label
            for flag, label in (
                (self.cleaning_done, "cleaning"),
                (self.inspection_done, "inspection"),
                (self.regrade, "the re-grade"),
                (self.technician_id, "the technician"),
            )
            if not flag
        ]
        if missing:
            return "the turnaround checklist is incomplete (%s)" % ", ".join(missing)
        if self._data_bearing():
            cert = self.data_wipe_certificate_id
            denial = cert._fix_certify_denial(asset.serial_no)
            if denial:
                return (
                    "unit %s is data-bearing (%s): %s — attach M06's verified wipe "
                    "certificate for this serial (NIST SP 800-88); a typed hash is not "
                    "evidence" % (asset.name, asset.category, denial)
                )
            cert = cert.sudo()
            if cert.verified_at and cert.verified_at.date() < self.returned_on:
                return (
                    "wipe certificate %s was verified on %s, before this return (%s): it "
                    "does not cover the last customer's data"
                    % (cert.name, cert.verified_at.date(), self.returned_on)
                )
            reused = self.sudo().search_count(
                [
                    ("data_wipe_certificate_id", "=", cert.id),
                    ("state", "=", "ready"),
                    ("id", "!=", self.id),
                ]
            )
            if reused:
                return "wipe certificate %s already released another turnaround" % cert.name
        return ""

    def action_ready(self):
        """Release the unit back to the rentable fleet: the checklist done,
        and for a data-bearing unit (cd_rental_asset.data_bearing_categories)
        M06's verified wipe certificate, bound to this unit's serial and
        verified after this return. Not opt-in: no box has to be ticked for
        the gate to apply."""
        for rec in self:
            denial = rec._release_denial()
            if denial:
                raise UserError("Turnaround %s cannot release the unit: %s." % (rec.name, denial))
            today = fields.Date.context_today(self)
            rec._guarded().write(
                {
                    "state": "ready",
                    "available_on": today,
                    "ready_timestamp": fields.Datetime.now(),
                    "nist_wipe_hash": rec.data_wipe_certificate_id.sudo().verified_hash or False,
                }
            )
            asset_vals = {
                "status": "available",
                "last_service_date": today,
                "next_service_due": today + relativedelta(months=3),
            }
            if rec.regrade:
                asset_vals["condition_grade"] = rec.regrade
            rec.rental_asset_id._guarded().write(asset_vals)
        return True

    def action_retire(self):
        for rec in self:
            if rec.state in ("ready", "retired"):
                raise UserError("Turnaround %s is %s." % (rec.name, rec.state))
            asset = rec.rental_asset_id
            if not asset.retirement_reason:
                asset.write({"retirement_reason": rec.notes or "Retired at turnaround"})
            asset.action_retire()
            rec._guarded().write({"state": "retired"})
        return True
