# fix_board_pack — M54 board pack: a period summary assembled from the FP&A
# reports, kept as lines and exported as a CSV file on the record.
#
# A08 remediation (B3, 4 Nov 2026; M54-3, P1-5): the state and the
# assembled/issued stamps are guarded (only the transitions write them, so the
# assembler is always the user who ran Assemble); the lines are written only by
# Assemble and are frozen from then on (an issued pack's figures can no longer
# be re-typed); Issue re-checks the lines against the fingerprint taken at
# assembly, and the pack is issued by a Finance Manager who did not assemble it.
import base64
import csv
import hashlib
import io
import json

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

_LINE_TOKEN = object()
_LINE_KEY = "fix_board_pack_assembly"


class FixBoardPack(models.Model):
    """Draft -> assembled (figures frozen, CSV attached) -> issued by a
    Finance Manager who did not assemble it."""

    _name = "fix.board.pack"
    _description = "Board Pack"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    content_hash = fields.Char(
        string="Figures Fingerprint",
        readonly=True,
        copy=False,
        help="SHA-256 of the assembled lines; Issue refuses a pack whose lines differ.",
    )
    assembled_by = fields.Many2one("res.users", readonly=True, copy=False)
    assembled_at = fields.Datetime(readonly=True, copy=False)
    issued_by = fields.Many2one("res.users", readonly=True, copy=False)
    issued_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "export_file",
            "export_filename",
            "content_hash",
            "assembled_by",
            "assembled_at",
            "issued_by",
            "issued_at",
        }

    @api.constrains("date_from", "date_to")
    def _check_window(self) -> None:
        for pack in self:
            if pack.date_from > pack.date_to:
                raise ValidationError("Board pack %s ends before it starts" % pack.name)

    @staticmethod
    def _fingerprint(lines) -> str:
        payload = [
            [
                ln.sequence,
                ln.section,
                ln.metric,
                round(ln.amount or 0.0, 2),
                bool(ln.has_amount),
                ln.detail or "",
            ]
            for ln in lines.sorted("sequence")
        ]
        return hashlib.sha256(json.dumps(payload).encode("utf-8")).hexdigest()

    def action_assemble(self):
        if not self.env.su and not (
            self.env.user.has_group("account.group_account_user")
            or self.env.user.has_group("account.group_account_manager")
        ):
            raise AccessError(
                "Assembling a board pack needs the Accountant or Finance Manager role"
            )
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
            Line = self.env["fix.board.pack.line"].sudo().with_context(**{_LINE_KEY: _LINE_TOKEN})
            pack.line_ids.sudo().with_context(**{_LINE_KEY: _LINE_TOKEN}).unlink()
            lines = Line.create(
                [
                    {
                        "pack_id": pack.id,
                        "sequence": idx,
                        "section": r["section"],
                        "metric": r["metric"],
                        "amount": r["amount"] or 0.0,
                        "has_amount": r["amount"] is not None,
                        "detail": r["detail"],
                    }
                    for idx, r in enumerate(rows, start=1)
                ]
            )
            pack._guarded().write(
                {
                    "export_file": base64.b64encode(buf.getvalue().encode("utf-8-sig")),
                    "export_filename": "board-pack-%s-%s.csv" % (pack.date_from, pack.date_to),
                    "content_hash": self._fingerprint(lines),
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
            if self._fingerprint(pack.sudo().line_ids) != pack.content_hash:
                raise UserError(
                    "Board pack %s's figures differ from what was assembled; assemble it again."
                    % pack.name
                )
            pack._guarded().write(
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
    """One figure of an assembled pack: written by Assemble only."""

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

    _FIGURE_FIELDS = {
        "pack_id",
        "sequence",
        "section",
        "metric",
        "amount",
        "has_amount",
        "detail",
        "currency_id",
    }

    def _assembling(self) -> bool:
        return self.env.context.get(_LINE_KEY) is _LINE_TOKEN

    @api.model_create_multi
    def create(self, vals_list):
        if not self._assembling():
            raise UserError("Board pack figures are produced by Assemble, never typed.")
        return super().create(vals_list)

    def write(self, vals):
        if set(vals) & self._FIGURE_FIELDS and not self._assembling():
            raise UserError(
                "Board pack figures are frozen once assembled; re-assemble the draft pack "
                "instead (an issued pack is final)."
            )
        return super().write(vals)

    def unlink(self):
        if not self._assembling():
            raise UserError("Board pack figures are produced by Assemble, never deleted by hand.")
        return super().unlink()
