# M12 seller stock positions (declared gap M12-stock closed, 12 Nov 2026).
#
# A listing carried title, category, price and state but no SKU or quantity,
# and no model tied stock to a seller, so "Seller Stock" was a declared gap.
# A position is the seller's quantity of one SKU (optionally a catalogue part)
# behind one of their listings: on hand, reserved, and therefore available.
#
# The quantities are what the seller REPORTS - from the seller API (portal),
# by an operator on their behalf, or by an import. Who reported it, when, and
# by which route are stamped by the server and guarded (fix.guarded.mixin);
# the report flags a position whose last report is older than N days as
# stale. The seller is the listing's seller, never typed, so a seller can
# only hold stock behind their own listings (the P07 record rule).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

STOCK_SOURCES = [
    ("seller", "Seller"),
    ("operator", "Operator"),
    ("import", "Import"),
]
_QTY = frozenset({"qty_on_hand", "qty_reserved"})
# In-process token for the import route; a JSON-RPC caller can put any key in
# the context but cannot put this object there.
_IMPORT_KEY = "fix_seller_stock_import"
_IMPORT_TOKEN = object()


class FixSellerStock(models.Model):
    _name = "fix.seller.stock"
    _description = "Seller Stock Position"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "seller_id, listing_id, sku"
    _rec_name = "sku"

    company_id = fields.Many2one(
        "res.company", related="listing_id.company_id", store=True, index=True, readonly=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        related="seller_id.operating_unit_id",
        store=True,
        readonly=True,
    )
    listing_id = fields.Many2one(
        "fix.marketplace.listing",
        string="Listing",
        required=True,
        ondelete="cascade",
        index=True,
    )
    seller_id = fields.Many2one(
        "fix.marketplace.seller",
        string="Seller",
        related="listing_id.seller_id",
        store=True,
        index=True,
        readonly=True,
    )
    sku = fields.Char(string="Seller SKU", required=True, index=True)
    part_id = fields.Many2one(
        "fix.catalogue.item",
        string="Catalogue Part",
        domain=[("item_type", "in", ("part", "accessory"))],
        ondelete="set null",
    )
    qty_on_hand = fields.Float(string="On Hand", digits=(16, 2), default=0.0)
    qty_reserved = fields.Float(
        string="Reserved", digits=(16, 2), default=0.0, help="Units already promised to orders."
    )
    qty_available = fields.Float(
        string="Available", digits=(16, 2), compute="_compute_available", store=True
    )
    last_updated = fields.Datetime(string="Quantity Last Reported", readonly=True, copy=False)
    updated_by_id = fields.Many2one(
        "res.users", string="Reported By", readonly=True, copy=False, ondelete="set null"
    )
    source = fields.Selection(
        STOCK_SOURCES, string="Reported Via", readonly=True, copy=False, default="operator"
    )
    note = fields.Char()

    _listing_sku_unique = models.Constraint(
        "UNIQUE (listing_id, sku)", "This listing already has a position for that SKU."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"last_updated", "updated_by_id", "source"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {"listing_id"}  # a position belongs to its listing
        return locked

    @api.depends("qty_on_hand", "qty_reserved")
    def _compute_available(self):
        for rec in self:
            rec.qty_available = (rec.qty_on_hand or 0.0) - (rec.qty_reserved or 0.0)

    @api.depends("sku", "listing_id.name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s — %s" % (rec.sku or "?", rec.listing_id.name or "?")

    @api.constrains("qty_on_hand", "qty_reserved")
    def _check_quantities(self):
        for rec in self:
            if (rec.qty_on_hand or 0.0) < 0 or (rec.qty_reserved or 0.0) < 0:
                raise ValidationError("A stock quantity cannot be negative (%s)." % rec.sku)
            if (rec.qty_reserved or 0.0) > (rec.qty_on_hand or 0.0) + 1e-6:
                raise ValidationError(
                    "%s: %.2f reserved is more than the %.2f on hand."
                    % (rec.sku, rec.qty_reserved, rec.qty_on_hand)
                )

    def _assert_sku_free(self, listing_id, sku, exclude=()):
        """One position per listing and SKU, said before the database's own
        unique constraint would abort the transaction."""
        twin = self.sudo().search(
            [("listing_id", "=", listing_id), ("sku", "=", sku), ("id", "not in", list(exclude))],
            limit=1,
        )
        if twin:
            raise ValidationError(
                "Listing %s already has a position for SKU %s: update that one."
                % (twin.listing_id.name, sku)
            )

    # ---- stamping ----------------------------------------------------------
    def _stock_source(self):
        if self.env.context.get(_IMPORT_KEY) is _IMPORT_TOKEN:
            return "import"
        if self.env.user.share:
            return "seller"
        return "operator"

    def _stock_stamp(self):
        return {
            "last_updated": fields.Datetime.now(),
            "updated_by_id": self.env.uid,
            "source": self._stock_source(),
        }

    @staticmethod
    def _clean_sku(vals):
        if isinstance(vals.get("sku"), str):
            vals["sku"] = vals["sku"].strip()
            if not vals["sku"]:
                raise ValidationError("A stock position needs a SKU.")

    @api.model_create_multi
    def create(self, vals_list):
        listings = self.env["fix.marketplace.listing"].sudo()
        for vals in vals_list:
            self._clean_sku(vals)
            listing = listings.browse(vals.get("listing_id")).exists()
            if listing and listing.state == "removed":
                raise ValidationError(
                    "Listing %s is removed: it takes no stock position." % listing.name
                )
            if listing and vals.get("sku"):
                self._assert_sku_free(listing.id, vals["sku"])
        recs = super().create(vals_list)
        # the stamp is the server's: who reported, when, and by which route
        super(FixSellerStock, recs._guarded()).write(recs._stock_stamp())
        return recs

    def write(self, vals):
        self._clean_sku(vals)
        if "sku" in vals or "listing_id" in vals:
            for rec in self:
                self._assert_sku_free(
                    vals.get("listing_id", rec.listing_id.id), vals.get("sku", rec.sku), rec.ids
                )
        res = super().write(vals)
        if _QTY & set(vals) and not self._fix_guard_has_token():
            super(FixSellerStock, self._guarded()).write(self._stock_stamp())
        return res

    def load(self, *args, **kwargs):
        """Odoo's own import (the Import button, base_import) is an import."""
        importer = self.with_context(**{_IMPORT_KEY: _IMPORT_TOKEN})
        return super(FixSellerStock, importer).load(*args, **kwargs)

    # ---- the two reporting routes -----------------------------------------
    @api.model
    def report_position(
        self, listing_id, sku, qty_on_hand, qty_reserved=0.0, part_id=None, note=None
    ):
        """Upsert one position (listing, SKU) as the caller: the seller API
        and an operator use this. Access rules decide whose listing it is."""
        sku = (sku or "").strip()
        if not sku:
            raise ValidationError("A stock position needs a SKU.")
        listing = self.env["fix.marketplace.listing"].sudo().browse(int(listing_id)).exists()
        if not listing:
            raise UserError("No such listing.")
        vals = {
            "qty_on_hand": float(qty_on_hand or 0.0),
            "qty_reserved": float(qty_reserved or 0.0),
        }
        if part_id is not None:
            vals["part_id"] = part_id or False
        if note is not None:
            vals["note"] = note
        existing = self.search([("listing_id", "=", listing.id), ("sku", "=", sku)], limit=1)
        if existing:
            existing.write(vals)
            return existing
        return self.create({"listing_id": listing.id, "sku": sku, **vals})

    @api.model
    def import_positions(self, rows):
        """Upsert a feed of positions ([{listing_id, sku, qty_on_hand,
        qty_reserved?, part_id?, note?}]), stamped as an import. Runs as the
        caller, so the same access rules apply as to a single report."""
        importer = self.with_context(**{_IMPORT_KEY: _IMPORT_TOKEN})
        created = updated = 0
        for row in rows or []:
            before = importer.search_count(
                [
                    ("listing_id", "=", int(row["listing_id"])),
                    ("sku", "=", (row.get("sku") or "").strip()),
                ]
            )
            importer.report_position(
                row["listing_id"],
                row.get("sku"),
                row.get("qty_on_hand", 0.0),
                row.get("qty_reserved", 0.0),
                part_id=row.get("part_id"),
                note=row.get("note"),
            )
            if before:
                updated += 1
            else:
                created += 1
        return {"created": created, "updated": updated}
