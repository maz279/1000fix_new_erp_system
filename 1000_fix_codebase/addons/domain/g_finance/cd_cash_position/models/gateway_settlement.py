# cd_cash_position — Gateway / MFS Settlement (A08 · M50).
#
# bKash / Nagad / SSLCOMMERZ pay merchants in batches, net of their fee
# (MDR, and VAT on it). Treasury imports the provider's settlement report
# (CSV — no gateway API is called), then runs the three-way match:
#   1. each report line <-> the receipt we booked (M20 fix.ar.receipt by
#      trx id, or a storefront order paid on that rail);
#   2. the report's net total <-> the bank credit (a statement line);
# and only a fully matched batch posts: Dr bank (net) + Dr fees / Cr the
# channel clearing account the receipts debited (gross).
from __future__ import annotations

import base64
import csv
import hashlib
import io
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from .treasury_common import bank_account_of, post_treasury_move, treasury_account

PROVIDERS = [
    ("bkash", "bKash"),
    ("nagad", "Nagad"),
    ("sslcommerz", "SSLCOMMERZ"),
    ("other", "Other Gateway / Wallet"),
]
# provider -> AR receipt methods (M20 RECEIPT_METHODS) it settles
PROVIDER_RECEIPT_METHODS = {
    "bkash": ("bkash",),
    "nagad": ("nagad",),
    "sslcommerz": ("card",),
    "other": ("mobile_wallet", "card", "bkash", "nagad"),
}
HEADER_ALIASES = {
    "trx_id": ("trxid", "transactionid", "tranid", "valid", "trx", "transaction", "paymentid"),
    "date": ("date", "transactiondate", "trandate", "txndate", "trxdate", "datetime"),
    "gross": ("amount", "gross", "grossamount", "transactionamount", "trxamount"),
    "fee": ("fee", "mdr", "commission", "charge", "servicecharge", "merchantfee", "mdrfee"),
    "fee_vat": ("vat", "feevat", "vatonfee", "vatonmdr"),
    "net": ("net", "netamount", "settledamount", "settlementamount", "payable", "storeamount"),
}


def _norm(header):
    return re.sub(r"[^a-z0-9]", "", (header or "").lower())


def _num(value):
    raw = (value or "").replace(",", "").strip()
    if not raw:
        return None
    try:
        return round(float(raw), 2)
    except ValueError as exc:
        raise UserError("Unreadable amount '%s' in the settlement report." % value) from exc


def parse_settlement_csv(content: str) -> list[dict]:
    """Parse a provider settlement report into {trx_id, date, gross, fee,
    fee_vat, net}. Column names vary per provider; the aliases above cover
    the common exports. A row without a transaction id or amount is
    refused, never skipped silently."""
    reader = csv.DictReader(io.StringIO(content.lstrip("﻿")))
    if not reader.fieldnames:
        raise UserError("The settlement report is empty.")
    colmap = {}
    for key, aliases in HEADER_ALIASES.items():
        for name in reader.fieldnames:
            if _norm(name) in aliases:
                colmap[key] = name
                break
    missing = [k for k in ("trx_id", "gross") if k not in colmap]
    if missing:
        raise UserError(
            "Settlement report columns not recognised: need a transaction id and an amount "
            "(found: %s)." % ", ".join(reader.fieldnames)
        )
    rows = []
    for lineno, row in enumerate(reader, start=2):
        if not any((v or "").strip() for v in row.values()):
            continue
        trx = (row.get(colmap["trx_id"]) or "").strip()
        gross = _num(row.get(colmap["gross"]))
        if not trx or gross is None:
            raise UserError("Settlement report line %s has no transaction id or amount." % lineno)
        fee = _num(row.get(colmap["fee"])) if "fee" in colmap else None
        vat = _num(row.get(colmap["fee_vat"])) if "fee_vat" in colmap else None
        net = _num(row.get(colmap["net"])) if "net" in colmap else None
        vat = vat or 0.0
        if fee is None:
            fee = round(gross - net - vat, 2) if net is not None else 0.0
        if net is None:
            net = round(gross - fee - vat, 2)
        if abs(gross - fee - vat - net) > 0.01:
            raise UserError(
                "Settlement report line %s does not add up (gross %s - fee %s - VAT %s != net %s)."
                % (lineno, gross, fee, vat, net)
            )
        date_raw = (row.get(colmap["date"]) or "").strip() if "date" in colmap else ""
        rows.append(
            {
                "trx_id": trx,
                "date": date_raw[:10] or False,
                "gross": gross,
                "fee": fee,
                "fee_vat": vat,
                "net": net,
            }
        )
    return rows


class FixGatewaySettlement(models.Model):
    _name = "fix.gateway.settlement"
    _description = "Gateway / MFS Settlement Batch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "settlement_date desc, id desc"

    name = fields.Char(string="Batch Ref", readonly=True, copy=False, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    provider = fields.Selection(PROVIDERS, required=True, default="bkash")
    provider_batch_ref = fields.Char(string="Provider Settlement Ref", index=True)
    settlement_date = fields.Date(required=True, default=fields.Date.context_today)
    journal_id = fields.Many2one(
        "account.journal",
        string="Credited To",
        required=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    report_file = fields.Binary(string="Settlement Report (CSV)", attachment=True)
    report_filename = fields.Char()
    report_hash = fields.Char(readonly=True, copy=False, index=True)
    line_ids = fields.One2many("fix.gateway.settlement.line", "batch_id", string="Lines")
    total_gross = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True
    )
    total_fee = fields.Monetary(
        string="Fees (MDR)", currency_field="currency_id", compute="_compute_totals", store=True
    )
    total_fee_vat = fields.Monetary(
        string="VAT on Fees", currency_field="currency_id", compute="_compute_totals", store=True
    )
    total_net = fields.Monetary(currency_field="currency_id", compute="_compute_totals", store=True)
    line_count = fields.Integer(compute="_compute_totals", store=True)
    exception_count = fields.Integer(compute="_compute_totals", store=True, string="Exceptions")
    statement_line_id = fields.Many2one(
        "fix.bank.statement.line", string="Bank Credit", readonly=True, copy=False
    )
    bank_matched = fields.Boolean(
        compute="_compute_totals", store=True, string="Bank Credit Matched"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("imported", "Imported — Awaiting Bank Credit"),
            ("exceptions", "Exceptions"),
            ("matched", "Three-Way Matched"),
            ("posted", "Posted"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)

    @api.depends(
        "line_ids.gross",
        "line_ids.fee",
        "line_ids.fee_vat",
        "line_ids.net",
        "line_ids.match_state",
        "statement_line_id",
    )
    def _compute_totals(self):
        for b in self:
            b.total_gross = sum(b.line_ids.mapped("gross"))
            b.total_fee = sum(b.line_ids.mapped("fee"))
            b.total_fee_vat = sum(b.line_ids.mapped("fee_vat"))
            b.total_net = sum(b.line_ids.mapped("net"))
            b.line_count = len(b.line_ids)
            b.exception_count = len(b.line_ids.filtered(lambda ln: ln.match_state != "matched"))
            b.bank_matched = bool(
                b.statement_line_id and abs(b.statement_line_id.amount - b.total_net) < 0.005
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.gateway.settlement") or "GWS"
                )
        return super().create(vals_list)

    def provider_label(self):
        self.ensure_one()
        return dict(PROVIDERS).get(self.provider, "").upper()

    # ---------------------------------------------------------------- import

    def action_import_report(self):
        for b in self:
            if b.state != "draft":
                raise UserError("The report is imported once, on a draft batch.")
            if not b.report_file:
                raise UserError("Attach the provider's settlement report (CSV) first.")
            content = base64.b64decode(b.report_file).decode("utf-8-sig", errors="replace")
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            if self.search_count([("report_hash", "=", digest), ("id", "!=", b.id)]):
                raise UserError("This settlement report was already imported in another batch.")
            rows = parse_settlement_csv(content)
            if not rows:
                raise UserError("The settlement report has no transaction lines.")
            b.write(
                {
                    "report_hash": digest,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "trx_id": r["trx_id"],
                                "txn_date": r["date"],
                                "gross": r["gross"],
                                "fee": r["fee"],
                                "fee_vat": r["fee_vat"],
                                "net": r["net"],
                            },
                        )
                        for r in rows
                    ],
                    "state": "imported",
                }
            )
            b.line_ids._match_receipt()
            b._match_bank()
            b._recompute_match()
        return True

    # ----------------------------------------------------------------- match

    def _match_bank(self):
        """Leg 3: the bank credit of exactly the net total, on the credited
        account, on/after the settlement date (within the window)."""
        for b in self:
            if b.statement_line_id or not b.line_ids:
                continue
            lines = self.env["fix.bank.statement.line"].search(
                [
                    ("company_id", "=", b.company_id.id),
                    ("match_state", "=", "unmatched"),
                    ("journal_id", "in", (b.journal_id.id, False)),
                    ("date", ">=", b.settlement_date - timedelta(days=1)),
                    ("date", "<=", b.settlement_date + timedelta(days=10)),
                ]
            )
            hits = lines.filtered(lambda ln, b=b: abs(ln.amount - b.total_net) < 0.005)
            if len(hits) == 1:
                b.statement_line_id = hits.id
                hits.write(
                    {
                        "match_state": "auto",
                        "matched_gateway_id": b.id,
                        "matched_kind": "gateway",
                        "matched_invoice_ref": b.name,
                    }
                )

    def _recompute_match(self):
        for b in self:
            if b.state in ("draft", "posted"):
                continue
            if b.exception_count:
                b.state = "exceptions"
            elif b.bank_matched:
                b.state = "matched"
            else:
                b.state = "imported"

    def action_match(self):
        """Re-run the three-way match (after receipts or the bank statement
        arrive)."""
        for b in self:
            if b.state in ("draft", "posted"):
                raise UserError("Import the report first; a posted batch is final.")
            b.line_ids.filtered(lambda ln: ln.match_state != "matched")._match_receipt()
            b._match_bank()
            b._recompute_match()
        return True

    def action_post(self):
        """Dr bank (net) + Dr fees (+ VAT on fees) / Cr channel clearing
        (gross) — only for a fully three-way matched batch."""
        for b in self:
            if b.state != "matched":
                raise UserError(
                    "%s is not three-way matched (receipts, report and bank credit) — not posted."
                    % b.name
                )
            bank = bank_account_of(b.journal_id)
            clearing = treasury_account(self.env, b.company_id, "channel_clearing")
            fees = treasury_account(self.env, b.company_id, "gateway_fees")
            vat_acc = treasury_account(self.env, b.company_id, "gateway_fee_vat", required=False)
            lines = [
                (
                    bank,
                    "%s settlement %s" % (b.provider_label(), b.provider_batch_ref or b.name),
                    b.total_net,
                    0.0,
                    None,
                ),
            ]
            if vat_acc:
                lines += [
                    (fees, "%s fees (MDR)" % b.provider_label(), b.total_fee, 0.0, None),
                    (vat_acc, "VAT on %s fees" % b.provider_label(), b.total_fee_vat, 0.0, None),
                ]
            else:
                lines.append(
                    (
                        fees,
                        "%s fees incl. VAT" % b.provider_label(),
                        b.total_fee + b.total_fee_vat,
                        0.0,
                        None,
                    )
                )
            lines.append(
                (clearing, "%s receipts cleared" % b.provider_label(), 0.0, b.total_gross, None)
            )
            move = post_treasury_move(
                self.env,
                b.company_id,
                b.statement_line_id.date or b.settlement_date,
                "GWS %s — %s" % (b.name, b.provider_label()),
                lines,
                source="treasury",
            )
            b.write({"state": "posted", "move_id": move.id})
        return True


class FixGatewaySettlementLine(models.Model):
    _name = "fix.gateway.settlement.line"
    _description = "Gateway Settlement Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "batch_id, id"

    batch_id = fields.Many2one(
        "fix.gateway.settlement", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="batch_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="batch_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="batch_id.currency_id")
    provider = fields.Selection(related="batch_id.provider", store=True)
    trx_id = fields.Char(string="Transaction ID", required=True, index=True)
    txn_date = fields.Date(string="Transaction Date")
    gross = fields.Monetary(currency_field="currency_id")
    fee = fields.Monetary(string="Fee (MDR)", currency_field="currency_id")
    fee_vat = fields.Monetary(string="VAT on Fee", currency_field="currency_id")
    net = fields.Monetary(currency_field="currency_id")
    receipt_model = fields.Char(readonly=True)
    receipt_res_id = fields.Integer(readonly=True)
    receipt_name = fields.Char(string="Our Receipt", readonly=True)
    receipt_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    match_state = fields.Selection(
        [
            ("matched", "Matched"),
            ("missing_receipt", "No Receipt Booked"),
            ("amount_mismatch", "Amount Differs"),
            ("duplicate", "Duplicate Transaction"),
            ("refund", "Refund / Chargeback — Review"),
        ],
        default="missing_receipt",
        required=True,
    )

    def _find_receipt(self):
        """(model, id, name, amount) of the receipt booked for this trx id."""
        self.ensure_one()
        trx = self.trx_id.strip()
        company = self.batch_id.company_id
        if "fix.ar.receipt" in self.env:
            receipts = self.env["fix.ar.receipt"].search(
                [
                    ("company_id", "=", company.id),
                    ("reference", "=ilike", trx),
                    ("state", "=", "confirmed"),
                    ("method", "in", PROVIDER_RECEIPT_METHODS[self.batch_id.provider]),
                ]
            )
            if receipts:
                return [("fix.ar.receipt", r.id, r.name, r.amount) for r in receipts]
        if "fix.storefront.order" in self.env:
            rail_domain = (
                [("payment_rail", "=", self.batch_id.provider)]
                if self.batch_id.provider in ("bkash", "nagad", "sslcommerz")
                else [("payment_rail", "!=", "cod")]
            )
            orders = self.env["fix.storefront.order"].search(
                [
                    ("company_id", "=", company.id),
                    ("payment_ref", "=ilike", trx),
                    ("state", "in", ("paid", "dispatched", "delivered")),
                    *rail_domain,
                ]
            )
            return [("fix.storefront.order", o.id, o.name, o.total_amount) for o in orders]
        return []

    def _match_receipt(self):
        for ln in self:
            if ln.gross < 0:
                ln.match_state = "refund"
                continue
            dup = self.search_count(
                [
                    ("trx_id", "=ilike", ln.trx_id.strip()),
                    ("id", "!=", ln.id),
                    ("company_id", "=", ln.company_id.id),
                ]
            )
            if dup:
                ln.match_state = "duplicate"
                continue
            found = ln._find_receipt()
            if not found:
                ln.write({"match_state": "missing_receipt"})
                continue
            if len(found) > 1:
                ln.write(
                    {"match_state": "duplicate", "receipt_name": ", ".join(f[2] for f in found)}
                )
                continue
            model, res_id, name, amount = found[0]
            ln.write(
                {
                    "receipt_model": model,
                    "receipt_res_id": res_id,
                    "receipt_name": name,
                    "receipt_amount": amount,
                    "match_state": "matched"
                    if abs(amount - ln.gross) < 0.005
                    else "amount_mismatch",
                }
            )
