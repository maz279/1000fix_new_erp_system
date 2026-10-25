# fix_board_pack — M54 board pack: a period summary assembled from the FP&A
# reports, kept as lines and exported as a CSV file on the record.
import base64
import csv
import io

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class FixBoardPack(models.Model):
    """Draft -> assembled (figures frozen, CSV attached) -> issued by a
    Finance Manager who did not assemble it."""

    _name = "fix.board.pack"
    _description = "Board Pack"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_to desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, tracking=True)
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("assembled", "Assembled"), ("issued", "Issued")],
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )
    line_ids = fields.One2many("fix.board.pack.line", "pack_id", string="Pack Lines", copy=False)
    export_file = fields.Binary(string="CSV Export", attachment=True, readonly=True, copy=False)
    export_filename = fields.Char(readonly=True, copy=False)
    assembled_by = fields.Many2one("res.users", readonly=True, copy=False)
    assembled_at = fields.Datetime(readonly=True, copy=False)
    issued_by = fields.Many2one("res.users", readonly=True, copy=False)
    issued_at = fields.Datetime(readonly=True, copy=False)

    @api.constrains("date_from", "date_to")
    def _check_window(self) -> None:
        for pack in self:
            if pack.date_from > pack.date_to:
                raise ValidationError("Board pack %s ends before it starts" % pack.name)

    def action_assemble(self):
        engine = self.env["fix.fpa.engine"]
        for pack in self:
            if pack.state == "issued":
                raise UserError("Board pack %s is issued and frozen" % pack.name)
            rows = engine.board_pack_rows(pack.date_from, pack.date_to)
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(["Section", "Metric", "Amount (BDT)", "Detail"])
            for r in rows:
                writer.writerow(
                    [
                        r["section"],
                        r["metric"],
                        "" if r["amount"] is None else r["amount"],
                        r["detail"],
                    ]
                )
            pack.line_ids.unlink()
            pack.write(
                {
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "sequence": idx,
                                "section": r["section"],
                                "metric": r["metric"],
                                "amount": r["amount"] or 0.0,
                                "has_amount": r["amount"] is not None,
                                "detail": r["detail"],
                            },
                        )
                        for idx, r in enumerate(rows, start=1)
                    ],
                    "export_file": base64.b64encode(buf.getvalue().encode("utf-8-sig")),
                    "export_filename": "board-pack-%s-%s.csv" % (pack.date_from, pack.date_to),
                    "state": "assembled",
                    "assembled_by": self.env.uid,
                    "assembled_at": fields.Datetime.now(),
                }
            )
        return True

    def action_issue(self):
        if not self.env.su and not self.env.user.has_group("account.group_account_manager"):
            raise AccessError("Issuing a board pack needs the Finance Manager role")
        for pack in self:
            if pack.state != "assembled":
                raise UserError("Assemble board pack %s before issuing it" % pack.name)
            if pack.assembled_by == self.env.user:
                raise UserError(
                    "Segregation of duties: %s assembled board pack %s and cannot issue it"
                    % (self.env.user.name, pack.name)
                )
            pack.write(
                {"state": "issued", "issued_by": self.env.uid, "issued_at": fields.Datetime.now()}
            )
        return True

    def write(self, vals):
        frozen = set(vals) - {"message_main_attachment_id"}
        if frozen and any(p.state == "issued" for p in self):
            raise UserError("An issued board pack is frozen")
        return super().write(vals)

    def unlink(self):
        if any(p.state == "issued" for p in self):
            raise UserError("An issued board pack is kept for the record")
        return super().unlink()


class FixBoardPackLine(models.Model):
    _name = "fix.board.pack.line"
    _description = "Board Pack Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "pack_id, sequence"

    pack_id = fields.Many2one("fix.board.pack", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="pack_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    sequence = fields.Integer()
    section = fields.Char(required=True)
    metric = fields.Char(required=True)
    amount = fields.Monetary(currency_field="currency_id")
    has_amount = fields.Boolean()
    detail = fields.Char()
