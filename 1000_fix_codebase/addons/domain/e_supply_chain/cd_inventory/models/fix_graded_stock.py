# cd_inventory — Graded Stock & Refurbished Inventory Valuation (M15 / P09-M04-T08 / R07-M03-T03).
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

# A04 integration (2026-11-04, M38 gst_01 / p03_06): any internal user could
# write a unit `sold` (at a resale price of 1.0) through the ORM or the P03
# form, with no order and no graded_stock.sold event. The state moves only
# through the transitions below (fix.guarded.mixin); the storefront and
# marketplace reach them as sudo() service code.
#
# A05 ERP audit (20 Nov 2026) M14-04 / XC-09: a plain user still CREATED a unit
# in stock (tradein_id 999999, price 1.0, cost 0) and the storefront sold it,
# and the costs, the price and the origin trade-in stayed free fields. A unit
# is now born only from its trade-in's Resale Ready (cd_tradein, under the
# guard); what it costs, sells for and came from is written only by the M14
# valued ledger and pricing actions; and every reservation and sale re-asks
# the unit whether it may be sold (_fix_sale_denial, extended by cd_tradein
# with the M06 wipe gate, the NEIR re-check, the approved listing price and a
# write-off). A storefront return no longer goes back on the shelf: it is
# held (returned) for a new wipe, QA and grade (M14-05).
STOCK_GUARDED = {
    "state",
    "tradein_id",
    "tradein_ref",
    "device_id",
    "grade_id",
    "acquisition_cost",
    "refurbishment_cost",
    "resale_price",
    "currency_id",
    "company_id",
    "operating_unit_id",
    "sold_at",
}
# kept for importers: every one of these is now guarded in every state
STOCK_FROZEN = {
    "device_id",
    "grade_id",
    "acquisition_cost",
    "refurbishment_cost",
    "resale_price",
    "currency_id",
}
FROZEN_STATES = ("reserved", "sold", "scrapped", "returned")
# A06 ERP X17 / A29 (20 Nov 2026): graded refurbished stock was outside the
# ledger and any user could type its cost. The cost now comes from the unit's
# source (the trade-in's payout and refurbishment cost), typed by no one, and
# a unit of a company on real-time stock posting enters the stock valuation
# subledger at intake (Dr graded stock / Cr trade-in intake clearing) and
# leaves it when sold (Dr parts cost 600002) or scrapped (Dr 500905). The two
# graded accounts are owner decisions: unset, the intake is refused.
COST_FIELDS = {"acquisition_cost", "refurbishment_cost"}
ON_SHELF = ("in_stock", "reserved")
# A sale or reservation outside an order (walk-in, write-off of a hold) is an
# Inventory Controller's call; the storefront reaches these as sudo() service.
STOCK_CONTROLLER = "cd_wms_structure.group_inventory_controller"
# M14-30: what a unit cost and its margin are read by costing staff only
COST_GROUP = "cd_wms_structure.group_stock_cost_viewer"


class FixGradedStock(models.Model):
    """Refurbished and graded device stock in M15 inventory with grade-aware valuation.
    Valuation = Acquisition Cost (Trade-In payout) + Refurbishment Cost (Parts + Labour).
    A financial inventory path ensuring margin visibility per device."""

    _name = "fix.graded.stock"
    _description = "Graded & Refurbished Inventory"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )
    name = fields.Char(
        string="Stock Tag / Serial",
        required=True,
        copy=False,
        default="New",
        index=True,
    )
    device_id = fields.Many2one(
        "fix.device",
        string="Device Serial",
        required=True,
        index=True,
        ondelete="restrict",
    )
    tradein_id = fields.Integer(
        string="Originating Trade-In ID",
        index=True,
        readonly=True,
    )
    tradein_ref = fields.Char(
        string="Originating Trade-In Ref",
        index=True,
        readonly=True,
    )

    grade_id = fields.Many2one(
        "fix.refurb.grade",
        string="Refurbishment Grade",
        required=True,
        index=True,
        help="Grade A/B/C/D/E determining resale pricing and warranty",
    )
    location_id = fields.Many2one(
        "fix.stock.location",
        string="Warehouse Location",
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT"),
    )

    # Financial valuation fields (AS-10 Monetary)
    acquisition_cost = fields.Monetary(
        groups=COST_GROUP,
        string="Acquisition Cost (Trade-In)",
        currency_field="currency_id",
        required=True,
        default=0.0,
        readonly=True,
        help="Price paid to customer during trade-in intake",
    )
    refurbishment_cost = fields.Monetary(
        groups=COST_GROUP,
        string="Refurbishment Cost",
        currency_field="currency_id",
        default=0.0,
        readonly=True,
        help="Parts consumed and labour costs during workshop repair",
    )
    inventory_valuation = fields.Monetary(
        groups=COST_GROUP,
        string="Inventory Valuation",
        currency_field="currency_id",
        compute="_compute_valuation",
        store=True,
        help="Total capitalized inventory cost: Acquisition + Refurbishment",
    )
    resale_price = fields.Monetary(
        string="Target Resale Price",
        currency_field="currency_id",
        required=True,
        default=0.0,
        readonly=True,
        help="The approved listing price (VAT inclusive). Set by the pricing approval or an "
        "approved markdown, never typed.",
    )
    projected_margin = fields.Monetary(
        groups=COST_GROUP,
        string="Projected Margin",
        currency_field="currency_id",
        compute="_compute_margin",
        store=True,
    )
    sold_at = fields.Datetime(string="Sold On", readonly=True, copy=False)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_stock", "In Stock (Available)"),
            ("reserved", "Reserved"),
            ("sold", "Sold / Delivered"),
            ("returned", "Returned - Held for Re-wipe, QA and Grade"),
            ("scrapped", "Scrapped / E-Waste"),
        ],
        string="Inventory Status",
        default="in_stock",
        required=True,
        tracking=True,
    )

    ledger_entry_id = fields.Many2one(
        "fix.inventory.valuation.suspense",
        string="Stock Ledger Intake",
        readonly=True,
        copy=False,
        help="The valuation entry that took this unit into the stock ledger (A06 ERP X17).",
    )

    def _fix_guarded_fields(self) -> set:
        # X17 / A29: the cost comes from the unit's source, never a person
        guarded = super()._fix_guarded_fields() | STOCK_GUARDED | COST_FIELDS
        guarded |= {"ledger_entry_id"}
        if any(rec.state in FROZEN_STATES for rec in self):
            guarded |= STOCK_FROZEN
        return guarded

    @api.depends("acquisition_cost", "refurbishment_cost")
    def _compute_valuation(self):
        for rec in self:
            rec.inventory_valuation = (rec.acquisition_cost or 0.0) + (
                rec.refurbishment_cost or 0.0
            )

    @api.depends("resale_price", "inventory_valuation")
    def _compute_margin(self):
        for rec in self:
            rec.projected_margin = (rec.resale_price or 0.0) - (rec.inventory_valuation or 0.0)

    @api.constrains("acquisition_cost", "refurbishment_cost", "resale_price")
    def _check_financial_amounts(self):
        for rec in self:
            if rec.acquisition_cost < 0:
                raise ValidationError("Acquisition cost cannot be negative")
            if rec.refurbishment_cost < 0:
                raise ValidationError("Refurbishment cost cannot be negative")
            if rec.resale_price < 0:
                raise ValidationError("Resale price cannot be negative")

    @api.model_create_multi
    def create(self, vals_list):
        # M14-04: a graded unit is stocked by its trade-in (Resale Ready), the
        # one path that capitalises it on the valued ledger and checks the
        # wipe gate, provenance and grade. Nobody types one into stock.
        if not self._fix_guard_open():
            raise UserError(
                "A graded refurbished unit is stocked by its trade-in's Resale Ready (M14), "
                "which values it on the refurbished-stock ledger. It is not created by hand."
            )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.graded.stock") or "STK/GRD/New"
                )
        records = super().create(vals_list)
        for rec in records:
            rec._fix_take_source_cost()
            if rec.state in ON_SHELF:
                rec._fix_graded_intake()
        return records

    def write(self, vals):
        watched = {"state"} | COST_FIELDS
        before = (
            {rec.id: (rec.state, rec.inventory_valuation) for rec in self}
            if watched & set(vals)
            else {}
        )
        result = super().write(vals)
        for rec in self.filtered(lambda r: r.id in before):
            old_state, old_value = before[rec.id]
            rec._fix_graded_follow(old_state, old_value)
        return result

    # ---- A06 ERP X17: the unit in the stock ledger ------------------------
    def _fix_source(self):
        """The trade-in the unit came from (cd_tradein is not a dependency)."""
        self.ensure_one()
        if not self.tradein_id or "fix.tradein.request" not in self.env:
            return None
        return self.env["fix.tradein.request"].sudo().browse(self.tradein_id).exists() or None

    def _fix_take_source_cost(self):
        """The cost is the source's: what the seller is paid (graded value,
        else the offer) and the refurbishment cost recorded on the trade-in."""
        self.ensure_one()
        source = self._fix_source()
        if source is None:
            return
        vals = {}
        acquisition = source.graded_value or source.offered_value or 0.0
        refurb = source.refurbishment_cost if "refurbishment_cost" in source._fields else None
        if abs((self.acquisition_cost or 0.0) - acquisition) > 1e-6:
            vals["acquisition_cost"] = acquisition
        if refurb is not None and abs((self.refurbishment_cost or 0.0) - refurb) > 1e-6:
            vals["refurbishment_cost"] = refurb
        if vals:
            super(FixGradedStock, self.sudo()._guarded()).write(vals)

    def _fix_graded_ou(self):
        """The unit's operating unit: its location's (or the location's
        branch's), its own, its trade-in's; never the company's first OU."""
        self.ensure_one()
        rec = self.sudo()
        if rec.location_id:
            ou = rec.location_id.operating_unit_id or rec.location_id.branch_id.operating_unit_id
            if ou:
                return ou
        if rec.operating_unit_id:
            return rec.operating_unit_id
        source = rec._fix_source()
        if (
            source is not None
            and "operating_unit_id" in source._fields
            and source.operating_unit_id
        ):
            return source.operating_unit_id
        raise UserError(
            "Graded unit %s has no location, operating unit or trade-in operating unit: its stock "
            "value cannot be posted. Nothing was posted." % rec.name
        )

    def _fix_ledger(self):
        return self.env["fix.inventory.valuation.suspense"].sudo()

    def _fix_graded_row(self, entry_type, value, ref, counter_role=None):
        self.ensure_one()
        rec = self.sudo()
        Ledger = self._fix_ledger()
        if counter_role:
            Ledger = Ledger.with_context(fix_stock_counter_role=counter_role)
        qty = 1.0 if value >= 0 else -1.0
        return Ledger.create(
            {
                "company_id": rec.company_id.id,
                "operating_unit_id": rec._fix_graded_ou().id,
                "location_id": rec.location_id.id or False,
                "graded_stock_id": rec.id,
                "quantity": qty,
                "unit_cost": abs(value),
                "total_valuation": round(value, 2),
                "entry_type": entry_type,
                "source_ref": ref,
            }
        )

    def _fix_books_elsewhere(self) -> bool:
        """True when another module keeps this unit's books from purchase to
        sale - the A05 M14 refurbished ledger (owner decision D1/D3, 21 Nov
        2026: the device is booked into stock at the payout, refurbishment is
        absorbed and cost of sale relieved by the trade-in) - so the graded
        posting below must not post the same value a second time."""
        return False

    def _fix_graded_intake(self):
        """Take an on-shelf unit into the stock ledger at its source cost."""
        self.ensure_one()
        rec = self.sudo()
        if rec._fix_books_elsewhere():
            return
        if rec.ledger_entry_id or not self._fix_ledger()._fix_realtime(rec.company_id):
            return
        entry = rec._fix_graded_row(
            "graded_intake", rec.inventory_valuation or 0.0, rec.tradein_ref or rec.name
        )
        super(FixGradedStock, rec._guarded()).write({"ledger_entry_id": entry.id})

    def _fix_graded_follow(self, old_state, old_value):
        """Post what a state or cost change did to a unit in the ledger."""
        self.ensure_one()
        rec = self.sudo()
        if rec._fix_books_elsewhere():
            return
        if not rec.ledger_entry_id:
            if rec.state in ON_SHELF and old_state not in ON_SHELF:
                rec._fix_graded_intake()
            return
        value = rec.inventory_valuation or 0.0
        if old_state in ON_SHELF and rec.state == "sold":
            rec._fix_graded_row("graded_issue", -value, "%s sold" % rec.name)
        elif old_state in ON_SHELF and rec.state == "scrapped":
            rec._fix_graded_row(
                "graded_issue", -value, "%s scrapped" % rec.name, "stock_adjustment"
            )
        elif old_state == "sold" and rec.state in ON_SHELF:
            rec._fix_graded_row("graded_issue", value, "%s returned" % rec.name)
        elif rec.state in ON_SHELF and old_state in ON_SHELF:
            diff = round(value - (old_value or 0.0), 2)
            if abs(diff) > 0.005:
                # the trade-in settled at another figure: the intake follows it
                rec._fix_graded_row("graded_intake", diff, "%s cost change" % rec.name)

    def _fix_require_controller(self, what):
        if not (self.env.su or self.env.user.has_group(STOCK_CONTROLLER)):
            raise UserError("%s is done from its order, or by an Inventory Controller." % what)

    # ------------------------------------------------------------ sale gates
    def _fix_sale_denial(self) -> str:
        """Why this unit may not be committed to a buyer now, or ''. The
        trade-in module extends it with the M06 wipe gate, the NEIR re-check,
        the approved listing price and a write-off (A05 M14-04)."""
        self.ensure_one()
        return ""

    def _fix_assert_saleable(self, what="This sale"):
        for rec in self:
            denial = rec._fix_sale_denial()
            if denial:
                raise UserError("%s refused: %s cannot be sold (%s)." % (what, rec.name, denial))

    def _fix_cogs_relieved(self) -> float:
        """The cost the latest sale took off stock (the valued ledger's COGS),
        0.0 where no valued ledger holds the unit. cd_tradein overrides it."""
        self.ensure_one()
        return 0.0

    # ------------------------------------------------------------ transitions
    def action_reserve(self):
        self._fix_require_controller("Reserving a graded unit")
        for rec in self:
            if rec.state != "in_stock":
                raise UserError("Only in-stock items can be reserved")
            rec._fix_assert_saleable("Reserving %s" % rec.name)
            rec._guarded().write({"state": "reserved"})

    def action_release(self):
        """A reservation that did not become a sale goes back on the shelf."""
        self._fix_require_controller("Releasing a graded unit")
        for rec in self:
            if rec.state != "reserved":
                raise UserError("Only a reserved item can be released back to stock")
            rec._guarded().write({"state": "in_stock"})

    def action_sell(self):
        self._fix_require_controller("Selling a graded unit")
        for rec in self:
            if rec.state not in ("in_stock", "reserved"):
                raise UserError("Only in-stock or reserved items can be sold")
            rec._fix_assert_saleable("Selling %s" % rec.name)
            rec._guarded().write({"state": "sold", "sold_at": fields.Datetime.now()})
            publish(
                self.env,
                "graded_stock.sold",
                "fix.graded.stock",
                rec.id,
                {
                    "device": rec.device_id.name if rec.device_id else "",
                    "grade": rec.grade_id.code if rec.grade_id else "",
                    # the event is the system's: cost and margin read as such
                    "valuation": float(rec.sudo().inventory_valuation),
                    "resale_price": float(rec.resale_price),
                    "margin": float(rec.sudo().projected_margin),
                },
            )

    def action_receive_return(self, reason=None):
        """A sold unit comes back from its buyer (M14-05). It is HELD, never
        put back on the shelf: it is re-wiped, re-tested and re-graded by its
        trade-in before it is stocked again (cd_tradein extends this)."""
        self._fix_require_controller("Receiving a returned graded unit")
        for rec in self:
            if rec.state != "sold":
                raise UserError(
                    "Only a sold unit is received back (%s is %s)." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "returned"})
            rec.message_post(
                body="Returned by the buyer%s: held for a new data wipe, QA and grade."
                % ((": %s" % reason) if reason else "")
            )
        return True
