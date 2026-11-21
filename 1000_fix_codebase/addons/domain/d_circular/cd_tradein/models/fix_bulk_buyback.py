# fix_bulk_buyback — M14 corporate bulk buy-back (FR-TRF-009, BRU-TRF-23,
# AUT-TRF-22).
#
# M14 capture audit (2026-11-13): the "Bulk Buy-Back" sub-module page listed
# every trade-in and offered "+ New Trade-In Request" - one unit at a time,
# with no lot, no declared asset list and nothing to reconcile against. A
# corporate fleet buy-back is a LOT: the client declares its assets, the lot
# is received, each declared asset becomes its own trade-in (valued, screened
# and wiped per unit, like any other), and the lot is not closed until every
# declared asset is reconciled to an intake or a documented exception.
#
# The lot links its trade-ins through its asset lines only, so the trade-in
# table is unchanged.
from odoo import api, fields, models
from odoo.exceptions import UserError

_MATCHED = "matched"
_EXCEPTION = "exception"
_PENDING = "pending"
_OPENED = "opened"
# A05 ERP M14-17: an asset is reconciled only once its unit was collected AND
# its data wipe certified, not the moment a draft intake exists
_CERTIFIED_STATES = ("wiped", "refurbished", "graded", "resale_ready", "parts_only", "closed")


def _norm_identifier(value):
    return "".join((value or "").split()).upper()


class FixBulkBuyback(models.Model):
    _name = "fix.bulk.buyback"
    _description = "Corporate Bulk Buy-Back Lot"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    partner_id = fields.Many2one(
        "res.partner", string="Corporate Client", required=True, index=True, tracking=True
    )
    contract_ref = fields.Char(string="Buy-Back Contract / PO Reference", tracking=True)
    account_manager_id = fields.Many2one(
        "res.users", string="Account Manager", default=lambda self: self.env.user
    )
    lot_price_basis = fields.Selection(
        [
            ("per_unit", "Per-unit valuation (each unit valued on the price grid)"),
            ("lot", "Agreed lot price"),
        ],
        string="Lot Pricing",
        required=True,
        default="per_unit",
        tracking=True,
    )
    lot_price = fields.Monetary(
        string="Agreed Lot Price", currency_field="currency_id", tracking=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    asset_ids = fields.One2many(
        "fix.bulk.buyback.asset", "buyback_id", string="Declared Asset List", copy=False
    )
    declared_asset_count = fields.Integer(
        string="Declared Assets", compute="_compute_counts", store=True
    )
    matched_count = fields.Integer(
        string="Reconciled to an Intake", compute="_compute_counts", store=True
    )
    exception_count = fields.Integer(
        string="Documented Exceptions", compute="_compute_counts", store=True
    )
    pending_count = fields.Integer(
        string="Not Yet Reconciled", compute="_compute_counts", store=True
    )
    offered_total = fields.Monetary(
        string="Offers on the Lot's Units",
        currency_field="currency_id",
        compute="_compute_offered_total",
        help="The sum of the offers made on the lot's trade-ins, to compare with the "
        "agreed lot price.",
    )
    opened_count = fields.Integer(
        string="Intake Opened, Not Yet Certified", compute="_compute_counts", store=True
    )
    allocated_total = fields.Monetary(
        string="Lot Price Allocated",
        currency_field="currency_id",
        compute="_compute_offered_total",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("received", "Received"), ("closed", "Closed")],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    received_at = fields.Datetime(readonly=True, copy=False)
    received_by_id = fields.Many2one("res.users", string="Received By", readonly=True, copy=False)
    closed_at = fields.Datetime(readonly=True, copy=False)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    notes = fields.Text()

    # once received, the client and the pricing are what the trade-ins carry
    _FROZEN_RECEIVED = frozenset(
        {"partner_id", "company_id", "lot_price_basis", "lot_price", "currency_id"}
    )

    _lot_price_positive = models.Constraint(
        "CHECK (lot_price IS NULL OR lot_price >= 0)", "A lot price cannot be negative"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "received_at",
            "received_by_id",
            "closed_at",
            "closed_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(rec.state == "closed" for rec in self):
            locked |= {
                name
                for name, field in self._fields.items()
                if field.store and name not in ("message_ids", "activity_ids")
            }
        elif any(rec.state != "draft" for rec in self):
            locked |= self._FROZEN_RECEIVED
        return locked

    @api.depends("asset_ids", "asset_ids.status")
    def _compute_counts(self):
        for rec in self:
            statuses = rec.asset_ids.mapped("status")
            rec.declared_asset_count = len(statuses)
            rec.matched_count = statuses.count(_MATCHED)
            rec.exception_count = statuses.count(_EXCEPTION)
            rec.opened_count = statuses.count(_OPENED)
            rec.pending_count = statuses.count(_PENDING)

    def _compute_offered_total(self):
        for rec in self:
            tradeins = rec.asset_ids.sudo().mapped("tradein_id")
            rec.offered_total = sum(
                tradeins.filtered(lambda t: t.state != "rejected").mapped("offered_value")
            )
            rec.allocated_total = sum(rec.asset_ids.mapped("allocated_price"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.bulk.buyback") or "BBK/New"
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state == "draft":
                    continue
                frozen = (
                    set(vals)
                    - {
                        "message_ids",
                        "activity_ids",
                        "message_follower_ids",
                        "message_main_attachment_id",
                    }
                    if rec.state == "closed"
                    else self._FROZEN_RECEIVED & set(vals)
                )
                names = [
                    n
                    for n in frozen
                    if n in self._fields
                    and self._fields[n].store
                    and n != "asset_ids"
                    and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if names:
                    raise UserError(
                        "Buy-back lot %s is %s: %s can no longer change."
                        % (
                            rec.name,
                            rec.state,
                            ", ".join(sorted(self._fields[n].string or n for n in names)),
                        )
                    )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(rec.state != "draft" for rec in self):
            raise UserError("A received or closed buy-back lot is evidence and is not deleted.")
        return super().unlink()

    # ------------------------------------------------------------------ actions
    def action_open_intakes(self):
        """AUT-TRF-22: the lot is received; every declared asset not yet
        reconciled gets its own draft trade-in for the client, which is then
        valued, screened, wiped and paid like any other unit (per-unit
        certification). Also run again for an asset declared after receipt."""
        Tradein = self.env["fix.tradein.request"]
        Device = self.env["fix.device"]
        for rec in self:
            if rec.state == "closed":
                raise UserError("Buy-back lot %s is closed." % rec.name)
            if not rec.asset_ids:
                raise UserError(
                    "Buy-back lot %s declares no asset: list the client's assets first." % rec.name
                )
            if rec.lot_price_basis == "lot" and not rec.lot_price:
                raise UserError(
                    "Buy-back lot %s is priced as a lot: enter the agreed lot price." % rec.name
                )
            # M14-23: every intake of the lot is taken in at the lot's OU
            if not rec.operating_unit_id:
                raise UserError(
                    "Buy-back lot %s has no operating unit: the lot's intakes are taken in at "
                    "one." % rec.name
                )
            opened = 0
            for asset in rec.asset_ids.filtered(
                lambda a: not a.tradein_id and not a.exception_reason
            ):
                ident = asset.serial_number
                device = Device.search(
                    [
                        "|",
                        "|",
                        ("serial_number", "=ilike", ident),
                        ("imei_1", "=", ident),
                        ("imei_2", "=", ident),
                    ],
                    limit=2,
                )
                vals = {
                    "customer_id": rec.partner_id.id,
                    "company_id": rec.company_id.id,
                    "currency_id": rec.currency_id.id,
                    # FR-TRF-001: the fifth intake channel
                    "intake_channel": "corporate",
                }
                if len(device) == 1:
                    vals["device_id"] = device.id
                if rec.operating_unit_id:
                    vals["operating_unit_id"] = rec.operating_unit_id.id
                tradein = Tradein.create(vals)
                tradein.message_post(
                    body="Opened from corporate buy-back lot %s, declared asset %s%s."
                    % (
                        rec.name,
                        ident,
                        " (%s)" % asset.asset_tag if asset.asset_tag else "",
                    )
                )
                asset._guarded().write({"tradein_id": tradein.id})
                opened += 1
            if rec.state == "draft":
                rec._guarded().write(
                    {
                        "state": "received",
                        "received_at": fields.Datetime.now(),
                        "received_by_id": self.env.uid,
                    }
                )
            rec.message_post(body="%d trade-in intake(s) opened for the declared assets." % opened)
        return True

    def action_close(self):
        """BRU-TRF-23: closed only when every declared asset is reconciled to
        an intake or a documented exception."""
        for rec in self:
            if rec.state != "received":
                raise UserError(
                    "Only a received buy-back lot is closed (%s is %s)." % (rec.name, rec.state)
                )
            pending = rec.asset_ids.filtered(lambda a: a.status in (_PENDING, _OPENED))
            if pending:
                raise UserError(
                    "Buy-back lot %s cannot close: %d declared asset(s) are not reconciled to a "
                    "collected, wipe-certified unit or a documented exception (%s)."
                    % (rec.name, len(pending), ", ".join(pending[:10].mapped("serial_number")))
                )
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_at": fields.Datetime.now(),
                    "closed_by_id": self.env.uid,
                }
            )
        return True

    def action_allocate_lot_price(self):
        """M14-17 / FIN-22: the agreed lot price is shared across the lot's
        live units in proportion to their grid valuation (their applied or
        computed offer), equally where none is valued, the last unit taking
        the rounding so the shares sum to the lot price exactly. Each unit is
        then offered its share (its draft offer is set to it)."""
        for rec in self:
            if rec.lot_price_basis != "lot" or not rec.lot_price:
                raise UserError("Buy-back lot %s is not priced as a lot." % rec.name)
            assets = rec.asset_ids.filtered(
                lambda a: a.tradein_id and a.tradein_id.state != "rejected"
            )
            if not assets:
                raise UserError("Buy-back lot %s has no open intake to allocate to." % rec.name)
            late = assets.filtered(lambda a: a.tradein_id.state != "draft")
            if late:
                raise UserError(
                    "Buy-back lot %s: %s already has an offer out; the lot price is allocated "
                    "before the offers." % (rec.name, late[0].tradein_id.name)
                )
            Valuation = self.env["fix.tradein.valuation"].sudo()
            weights = []
            for asset in assets:
                val = Valuation.search(
                    [("tradein_id", "=", asset.tradein_id.id)], order="id desc", limit=1
                )
                weights.append(val.final_offer or val.computed_offer or 0.0 if val else 0.0)
            total = sum(weights)
            if total <= 0:
                weights = [1.0] * len(assets)
                total = float(len(assets))
            shares, left = [], round(rec.lot_price, 2)
            for i, weight in enumerate(weights):
                share = left if i == len(weights) - 1 else round(rec.lot_price * weight / total, 2)
                shares.append(share)
                left = round(left - share, 2)
            for asset, share in zip(assets, shares, strict=True):
                asset._guarded().write({"allocated_price": share})
                asset.tradein_id.sudo()._guarded().write({"offered_value": share})
            rec.message_post(
                body="Lot price BDT %.2f allocated across %d unit(s)."
                % (rec.lot_price, len(assets))
            )
        return True


class FixBulkBuybackAsset(models.Model):
    _name = "fix.bulk.buyback.asset"
    _description = "Declared Asset of a Bulk Buy-Back Lot"
    _inherit = ["fix.guarded.mixin"]
    _order = "buyback_id, id"
    _rec_name = "serial_number"

    buyback_id = fields.Many2one(
        "fix.bulk.buyback", string="Buy-Back Lot", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        related="buyback_id.company_id", store=True, index=True, string="Company"
    )
    asset_tag = fields.Char(string="Client Asset Tag")
    serial_number = fields.Char(string="Serial / IMEI (as declared)", required=True)
    description = fields.Char(string="Make / Model (as declared)")
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In Intake", readonly=True, copy=False, index=True
    )
    tradein_state = fields.Selection(related="tradein_id.state", string="Intake State")
    exception_reason = fields.Char(
        string="Documented Exception",
        help="Why this declared asset has no intake: not received, retained by the client, "
        "declined the offer, wrong serial on the list…",
    )
    exception_by_id = fields.Many2one(
        "res.users", string="Exception Recorded By", readonly=True, copy=False
    )
    exception_at = fields.Datetime(string="Exception Recorded At", readonly=True, copy=False)
    currency_id = fields.Many2one(related="buyback_id.currency_id", string="Currency")
    allocated_price = fields.Monetary(
        string="Allocated Lot Price",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="This unit's share of the agreed lot price (Allocate Lot Price).",
    )
    status = fields.Selection(
        [
            (_PENDING, "Not Reconciled"),
            (_OPENED, "Intake Opened (not yet collected and certified)"),
            (_MATCHED, "Collected and Wipe-Certified"),
            (_EXCEPTION, "Exception"),
        ],
        compute="_compute_status",
        store=True,
    )

    _serial_unique_in_lot = models.Constraint(
        "UNIQUE (buyback_id, serial_number)", "An asset is declared once per lot."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "tradein_id",
            "exception_by_id",
            "exception_at",
            "allocated_price",
        }

    @api.depends("tradein_id", "tradein_id.state", "exception_reason")
    def _compute_status(self):
        for rec in self:
            state = rec.tradein_id.state if rec.tradein_id else False
            if state in _CERTIFIED_STATES:
                rec.status = _MATCHED
            elif (rec.exception_reason or "").strip():
                rec.status = _EXCEPTION
            elif state and state != "rejected":
                rec.status = _OPENED
            else:
                rec.status = _PENDING

    def _refuse_if_closed(self, lots):
        if self.env.su:
            return
        closed = lots.filtered(lambda b: b.state == "closed")
        if closed:
            raise UserError(
                "Buy-back lot %s is closed: its declared assets no longer change." % closed[0].name
            )

    @api.model_create_multi
    def create(self, vals_list):
        lots = self.env["fix.bulk.buyback"].browse(
            [v["buyback_id"] for v in vals_list if v.get("buyback_id")]
        )
        self._refuse_if_closed(lots)
        if not self._fix_guard_open():
            sent = self._fix_guarded_fields() & {k for vals in vals_list for k in vals}
            if sent:
                self._fix_guard_refuse(sent)
        for vals in vals_list:
            if "serial_number" in vals:
                vals["serial_number"] = _norm_identifier(vals["serial_number"])
            if (vals.get("exception_reason") or "").strip():
                vals.update(exception_by_id=self.env.uid, exception_at=fields.Datetime.now())
        # the exception stamp is the system's own, written under the guard
        return super(FixBulkBuybackAsset, self._guarded()).create(vals_list)

    def write(self, vals):
        self._refuse_if_closed(self.mapped("buyback_id"))
        if "serial_number" in vals:
            vals = dict(vals, serial_number=_norm_identifier(vals["serial_number"]))
            if not self._fix_guard_open():
                linked = self.filtered(
                    lambda a: a.tradein_id and a.serial_number != vals["serial_number"]
                )
                if linked:
                    raise UserError(
                        "Declared asset %s has its intake %s: the declared serial no longer "
                        "changes." % (linked[0].serial_number, linked[0].tradein_id.name)
                    )
        result = super().write(vals)
        if "exception_reason" in vals:
            documented = bool((vals["exception_reason"] or "").strip())
            self._guarded().write(
                {
                    "exception_by_id": self.env.uid if documented else False,
                    "exception_at": fields.Datetime.now() if documented else False,
                }
            )
        return result

    def unlink(self):
        self._refuse_if_closed(self.mapped("buyback_id"))
        if not self.env.su and any(a.tradein_id for a in self):
            raise UserError(
                "A declared asset with an intake is reconciliation evidence and is not removed: "
                "document an exception instead."
            )
        return super().unlink()
