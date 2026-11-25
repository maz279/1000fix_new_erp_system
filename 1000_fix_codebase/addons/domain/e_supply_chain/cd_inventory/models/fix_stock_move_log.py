# fix_stock_move_log - the immutable stock-movement ledger (FR-INV-005).
#
# A06 ERP audit 20 Nov 2026 A20: the on-hand rows were the only record of
# stock; a bucket kept its current quantity and nothing said how it got there,
# so ageing could read only lots (0 on fix_real, X30), an as-at position or a
# turnover figure could not be computed (A22/A23, KPI-045/046) and a count
# could not tell what moved while it was open (A04). Every quantity change of
# fix.stock.onhand._apply now appends one row here: the bucket, the signed
# quantity, the cost it moved at, the balance after it and the document that
# moved it. Rows are written by the ledger code only (as the system), are
# readable by stock users of their company / operating unit, and can never be
# changed or deleted.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_inventory_approval import COST_GROUP

# context keys a movement passes so its log row names the document
REF_KEY = "fix_move_ref"
MODEL_KEY = "fix_move_model"
RES_KEY = "fix_move_res_id"


class FixStockMoveLog(models.Model):
    _name = "fix.stock.move.log"
    _description = "Stock Movement Ledger"
    _order = "moved_at desc, id desc"

    moved_at = fields.Datetime(required=True, readonly=True, index=True)
    move_date = fields.Date(
        string="Business Date (Dhaka)", required=True, readonly=True, index=True
    )
    company_id = fields.Many2one("res.company", required=True, readonly=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", readonly=True, index=True)
    part_id = fields.Many2one(
        "fix.spare.part",
        string="Spare Part",
        required=True,
        readonly=True,
        index=True,
        ondelete="restrict",
    )
    location_id = fields.Many2one(
        "fix.stock.location",
        string="Location",
        required=True,
        readonly=True,
        index=True,
        ondelete="restrict",
    )
    ownership_class = fields.Char(readonly=True, index=True)
    stock_status = fields.Char(readonly=True, index=True)
    qty = fields.Float(string="Quantity (signed)", readonly=True)
    balance_qty = fields.Float(string="Balance After", readonly=True)
    unit_cost = fields.Float(string="Unit Cost (BDT)", readonly=True, groups=COST_GROUP)
    value = fields.Float(string="Value (BDT)", readonly=True, groups=COST_GROUP)
    reference = fields.Char(readonly=True, index=True)
    res_model = fields.Char(string="Document Model", readonly=True)
    res_id = fields.Integer(string="Document ID", readonly=True)
    user_id = fields.Many2one("res.users", string="Moved By", readonly=True)

    @api.model
    def _fix_log(self, bucket, delta, unit_cost):
        """Append the row for one movement of `bucket` (system path)."""
        ctx = self.env.context
        now = fields.Datetime.now()
        location = bucket.location_id
        return (
            self.sudo()
            .with_context(fix_move_log_write=True)
            .create(
                {
                    "moved_at": now,
                    "move_date": fields.Date.context_today(self.with_context(tz="Asia/Dhaka"), now),
                    "company_id": bucket.company_id.id,
                    "operating_unit_id": bucket.operating_unit_id.id or False,
                    "part_id": bucket.part_id.id,
                    "location_id": location.id,
                    "ownership_class": bucket.ownership_class,
                    "stock_status": bucket.stock_status,
                    "qty": round(delta, 4),
                    "balance_qty": round(bucket.qty or 0.0, 4),
                    "unit_cost": round(unit_cost or 0.0, 4),
                    "value": round(delta * (unit_cost or 0.0), 2),
                    "reference": ctx.get(REF_KEY) or False,
                    "res_model": ctx.get(MODEL_KEY) or False,
                    "res_id": ctx.get(RES_KEY) or 0,
                    "user_id": self.env.uid,
                }
            )
        )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("fix_move_log_write"):
            raise UserError("The stock movement ledger is written by stock movements only.")
        return super().create(vals_list)

    def write(self, vals):
        raise UserError("The stock movement ledger is final: a row is never changed.")

    def unlink(self):
        raise UserError("The stock movement ledger is final: a row is never deleted.")


def move_ctx(record, ref=None):
    """The context a document's movements carry into the log."""
    return {
        REF_KEY: ref or getattr(record, "name", False) or False,
        MODEL_KEY: record._name,
        RES_KEY: record.id,
    }
