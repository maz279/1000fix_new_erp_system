# cd_inventory — real-time stock accounting (A06 ERP audit, 20 Nov 2026).
#
# Owner decisions D1/D2/D4: inventory posts each movement to the GL as it
# happens; the 110999 suspense stub and the month-end cut-over typed by a
# person are retired. fix.inventory.valuation.suspense stays the stock
# valuation SUBLEDGER (one row per movement, written by the same callers
# through the same _fix_post), and every row now posts its own balanced
# account.move at the Dhaka business date of the movement, with the branch
# operating unit of the stock location on every line (cd_gl_ext
# post_with_dimensions). The row records the entry, both accounts and the date.
#
# Posting rules (account codes are the legacy chart's, D2; each is an
# ir.config_parameter so a company on another chart names its own, and a code
# that is not in the company's chart REFUSES the movement - nothing is posted
# to a guessed account):
#   receipt              Dr stock(brand) / Cr GRNI 100503 (PO, import, direct
#                        receipt: the supplier bill clears GRNI). A receipt
#                        whose source document is not a purchase names its own
#                        counter account (param receipt_counter_by_source) or
#                        is refused.
#   consumption, return, counter_sale, storefront_sale
#                        Dr parts cost 600002 / Cr stock (a return reverses)
#   adjustment, write_off, class_change
#                        Dr/Cr 500905 vs stock
#   rtv                  Dr GRNI / Cr stock (the AP credit note then clears
#                        GRNI against AP); price_variance Dr 600007 / Cr GRNI
#   revaluation          Dr/Cr stock vs the account the CALLER names
#                        (context fix_stock_counter_account), else refused
#   initial_count        Dr stock / Cr 300101 (the stock take-on, D4)
#   transfer             same stock account, Cr sender OU / Dr receiver OU,
#                        at receipt by the receiver (in transit stays the
#                        sender's, BRU-INV-16)
#   graded_intake/issue  graded refurbished stock (X17): accounts are OWNER
#                        parameters with no default
#   shipment             refused: stock that leaves the ledger with no M15
#                        document behind it has no account (M41 F01)
#
# A caller that has already posted its own journal entry for the same event
# (M44 import receipt and landed cost) says so with the context key
# fix_stock_external_move_id=<account.move id>: its rows are marked posted
# with that entry and no second entry is made.
#
# Switch-over: real time starts per company at its stock take-on
# (res.company.fix_stock_realtime_from, written only by the take-on). Rows of
# a company not switched over stay pending for the old cut-over, which still
# clears them; the take-on supersedes them explicitly.
from __future__ import annotations

import json
import logging
import re

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from .fix_inventory_approval import (
    CONTROLLER_GROUP,
    STOREKEEPER_GROUP,
    VALUED_CLASSES,
    location_class,
)
from .fix_valuation_suspense import PRICE_VARIANCE_PARAM, dhaka_today, stock_effect_value

_logger = logging.getLogger(__name__)

EPS = 1e-6
SOURCE = "inventory_subledger"

P = "cd_inventory."
PARAM_JOURNAL = P + "stock_posting.journal_code"
DEFAULT_JOURNAL = "STJ"
PARAM_BRAND_ACCOUNTS = P + "stock_posting.brand_accounts"
PARAM_RECEIPT_SOURCES = P + "stock_posting.receipt_counter_by_source"
# GRNI is shared with AP (cd_ap_ext debits it when the bill arrives): this
# module's own parameter wins, else AP's, else the D2 code.
AP_GRNI_PARAM = "cd_ap_ext.account_code.grni"

# role -> (parameter, D2 default code or None, label)
ACCOUNT_ROLES = {
    "stock_default": (P + "account_code.stock_default", "100502", "Stock (other brands)"),
    "grni": (P + "account_code.grni", "100503", "Goods received not invoiced (Stock Incoming)"),
    "cogs": (P + "account_code.cogs", "600002", "Parts cost on jobs and sales"),
    "stock_adjustment": (
        P + "account_code.stock_adjustment",
        "500905",
        "Count losses / gains and write-offs",
    ),
    "price_variance": (PRICE_VARIANCE_PARAM, "600007", "Purchase price variance"),
    "takeon_equity": (P + "account_code.takeon_equity", "300101", "Stock take-on (opening)"),
    # X17: no owner decision yet - fail closed until Finance names them
    "graded_stock": (P + "account_code.graded_stock", None, "Graded refurbished stock"),
    "graded_intake": (
        P + "account_code.graded_intake",
        None,
        "Graded refurbished intake (trade-in payout clearing)",
    ),
}

# D2: stock account by the part's brand. Keys are matched against the part's
# brand master (name, code) and its legacy brand text, lower case.
DEFAULT_BRAND_ACCOUNTS = {
    "samsung": "100506",
    "xiaomi": "100508",
    "huawei": "100509",
    "cooler": "100510",
    "whirlpool": "100511",
}

# Receipts from these source documents are purchases: their counter is GRNI.
PURCHASE_SOURCES = ("", "fix.purchase.receipt", "fix.purchase.order", "fix.import.order")

COUNTER_ROLE = {
    "consumption": "cogs",
    "return": "cogs",
    "counter_sale": "cogs",
    "storefront_sale": "cogs",
    "adjustment": "stock_adjustment",
    "write_off": "stock_adjustment",
    "class_change": "stock_adjustment",
    "rtv": "grni",
    "initial_count": "takeon_equity",
    "graded_intake": "graded_intake",
    "graded_issue": "cogs",
}
# X19 / D4: outgoing (or counted) movements of stock with no cost need an approval
ISSUE_TYPES = ("consumption", "counter_sale", "storefront_sale")
ZERO_COST_GUARDED = (*ISSUE_TYPES, "adjustment", "write_off")


def _norm(text) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _param(env, key, default=None):
    value = env["ir.config_parameter"].sudo().get_param(key)
    return value.strip() if isinstance(value, str) and value.strip() else default


def _json_param(env, key, default):
    raw = _param(env, key)
    if not raw:
        return dict(default)
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise UserError("System parameter %s is not valid JSON: %s" % (key, exc)) from exc
    if not isinstance(data, dict):
        raise UserError("System parameter %s must be a JSON object." % key)
    return {_norm(k): str(v).strip() for k, v in data.items()}


def role_code(env, role) -> str | None:
    """The account code of a posting role: its parameter, else the D2 default."""
    param, default, _label = ACCOUNT_ROLES[role]
    code = _param(env, param)
    if not code and role == "grni":
        code = _param(env, AP_GRNI_PARAM)
    return code or default


class FixJournalPostingLogInventory(models.Model):
    """The stock subledger as a posting source in M19's posting log."""

    _inherit = "fix.journal.posting.log"

    source = fields.Selection(
        selection_add=[(SOURCE, "Inventory Sub-ledger (M15)")],
        ondelete={SOURCE: lambda recs: recs.write({"source": "api"})},
    )


class ResCompanyStockPosting(models.Model):
    _inherit = "res.company"

    fix_stock_realtime_from = fields.Datetime(
        string="Real-time Stock Posting Since",
        readonly=True,
        copy=False,
        help="Set by the company's stock take-on (A06 ERP D1/D4): from then on every M15 "
        "movement posts its own journal entry. Empty: movements wait for the old cut-over.",
    )


class FixValuationSuspensePosting(models.Model):
    """The posting engine of the stock subledger."""

    _inherit = "fix.inventory.valuation.suspense"

    # ---------------------------------------------------------------- switch
    @api.model
    def _fix_realtime(self, company) -> bool:
        return bool(company and company.sudo().fix_stock_realtime_from)

    # ------------------------------------------------------------- accounts
    @api.model
    def _fix_account(self, company, code, what):
        if not code:
            param = next((p for r, (p, _d, lbl) in ACCOUNT_ROLES.items() if lbl == what), "")
            raise UserError(
                "No GL account is configured for %s in %s (system parameter %s): nothing was "
                "posted and the stock movement is refused." % (what, company.name, param)
            )
        account = (
            self.env["account.account"]
            .sudo()
            .with_company(company)
            .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        )
        if not account:
            raise UserError(
                "Account %s (%s) is not in the chart of %s: nothing was posted and the stock "
                "movement is refused." % (code, what, company.name)
            )
        return account

    @api.model
    def _fix_role_account(self, company, role):
        return self._fix_account(company, role_code(self.env, role), ACCOUNT_ROLES[role][2])

    @api.model
    def _fix_brand_keys(self, part) -> list:
        """The governed brand master decides; the legacy brand text only when
        the part has no brand master (A30: 358 parts disagree on fix_real)."""
        part = part.sudo()
        brand = part.brand_id if "brand_id" in part._fields else False
        if brand:
            keys = [_norm(brand.name), _norm(brand.code)]
        else:
            keys = [_norm(part.device_brand if "device_brand" in part._fields else "")]
        return [k for k in keys if k]

    @api.model
    def _fix_stock_code(self, part) -> str:
        """D2: the stock account code of a part, by its brand."""
        mapping = _json_param(self.env, PARAM_BRAND_ACCOUNTS, DEFAULT_BRAND_ACCOUNTS)
        for candidate in self._fix_brand_keys(part):
            for key, code in mapping.items():
                words = candidate.split(" ")
                if candidate == key or key in words or candidate.startswith(key + " "):
                    return code
        return role_code(self.env, "stock_default")

    @api.model
    def _fix_stock_account(self, part, company):
        """The stock account of a part in a company (public: M44 debits the
        same account when it posts an import itself)."""
        return self._fix_account(
            company,
            self._fix_stock_code(part),
            "Stock of %s" % (part.sudo().part_number or part.display_name),
        )

    @api.model
    def _fix_journal(self, company):
        code = _param(self.env, PARAM_JOURNAL, DEFAULT_JOURNAL)
        journal = (
            self.env["account.journal"]
            .sudo()
            .search(
                [("company_id", "=", company.id), ("code", "=", code), ("type", "=", "general")],
                limit=1,
            )
        )
        if not journal:
            raise UserError(
                "No general journal %s in %s for stock postings (system parameter %s): the "
                "stock movement is refused." % (code, company.name, PARAM_JOURNAL)
            )
        return journal

    # ----------------------------------------------------- operating unit
    @api.model
    def _fix_location_ou(self, location, company=None):
        """X36: the OU of a stock location, else of its branch; never the
        company's first OU. Refuses when neither names one."""
        location = location.sudo()
        ou = location.operating_unit_id or location.branch_id.operating_unit_id
        company = company or location.company_id
        if ou and company and ou.company_id and ou.company_id != company:
            ou = location.branch_id.operating_unit_id
            if ou.company_id and ou.company_id != company:
                ou = ou.browse()
        if not ou:
            raise UserError(
                "Stock location %s has no operating unit (neither on the location nor on its "
                "branch): its stock cannot be posted to the GL. Set the location's operating "
                "unit; nothing was posted." % (location.code or location.display_name)
            )
        return ou

    @api.model
    def _fix_dims(self, ou, location=None):
        dims = {"operating_unit_id": ou.id}
        branch = location.sudo().branch_id if location else False
        if branch and branch.operating_unit_id == ou:
            dims["branch_id"] = branch.id
        return dims

    # ------------------------------------------------------------- posting
    @api.model
    def _fix_gl_post(self, company, date, ref, lines, source_ref=None):
        """Post ONE balanced entry: lines = [(account, label, amount, dims)],
        amount > 0 debit, < 0 credit. Refused unless it balances."""
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        su = self.env(su=True)
        move_lines, dims, debit, credit = [], {}, 0.0, 0.0
        for account, label, amount, line_dims in lines:
            amount = round(amount or 0.0, 2)
            if not amount:
                continue
            dr, cr = (amount, 0.0) if amount > 0 else (0.0, -amount)
            debit += dr
            credit += cr
            dims[len(move_lines)] = dict(line_dims)
            move_lines.append(
                (0, 0, {"account_id": account.id, "name": label[:256], "debit": dr, "credit": cr})
            )
        if not move_lines:
            return su["account.move"]
        if abs(round(debit, 2) - round(credit, 2)) > 0.005:
            raise UserError(
                "%s does not balance (%.2f / %.2f): nothing was posted." % (ref, debit, credit)
            )
        move, _dims = post_with_dimensions(
            su(context=dict(su.context, allowed_company_ids=[company.id])),
            {
                "move_type": "entry",
                "company_id": company.id,
                "journal_id": self._fix_journal(company).id,
                "date": date,
                "ref": ref[:256],
                "line_ids": move_lines,
            },
            dims,
            source=SOURCE,
            source_ref=source_ref,
        )
        return move

    def _fix_mark_posted(self, move, stock_code=None, counter_code=None, ou=None):
        vals = {"status": "posted", "posted_at": fields.Datetime.now(), "move_id": move.id or False}
        if stock_code is not None:
            vals["stock_account_code"] = stock_code
        if counter_code is not None:
            vals["counter_account_code"] = counter_code
        if ou:
            vals["operating_unit_id"] = ou.id
        self.sudo()._guarded().write(vals)

    def _fix_post_realtime(self):
        """Post every row of a real-time company (called by create())."""
        if self.env.context.get("fix_stock_no_autopost"):
            return
        external = self.env.context.get("fix_stock_external_move_id")
        for entry in self.sudo():
            if entry.status != "pending_gl_cutover" or not self._fix_realtime(entry.company_id):
                continue
            if external:
                entry._fix_post_external(external)
            else:
                entry._fix_post_one()

    def _fix_post_external(self, move_ref):
        """The caller posted this event's journal itself: link it, never post twice."""
        self.ensure_one()
        move_id = move_ref.id if hasattr(move_ref, "id") else int(move_ref)
        move = self.env["account.move"].sudo().browse(move_id).exists()
        if not move or move.state != "posted" or move.company_id != self.company_id:
            raise UserError(
                "Valuation entry %s names journal entry %s as already posted, but it is not a "
                "posted entry of %s." % (self.name, move_id, self.company_id.name)
            )
        ou = self._fix_row_ou()
        stock_code = self._fix_row_stock_code()
        self._fix_mark_posted(move, stock_code=stock_code, counter_code="", ou=ou)

    def _fix_row_ou(self):
        self.ensure_one()
        if self.location_id:
            return self._fix_location_ou(self.location_id, self.company_id)
        if self.graded_stock_id:
            return self.graded_stock_id._fix_graded_ou()
        if self.operating_unit_id:
            return self.operating_unit_id
        raise UserError(
            "Valuation entry %s (%s) names no stock location: its operating unit is unknown and "
            "nothing was posted." % (self.name, self.source_ref or self.entry_type)
        )

    def _fix_row_stock_code(self):
        self.ensure_one()
        if self.graded_stock_id:
            return role_code(self.env, "graded_stock")
        return self._fix_stock_code(self.product_id)

    def _fix_receipt_counter_role_code(self):
        """GRNI for a purchase; a receipt from another source names its account."""
        self.ensure_one()
        receipt = (
            self.env["fix.stock.receipt"]
            .sudo()
            .search(
                [("name", "=", self.source_ref), ("company_id", "=", self.company_id.id)], limit=1
            )
            if self.source_ref
            else self.env["fix.stock.receipt"]
        )
        source = (receipt.source_model or "") if receipt else ""
        if source in PURCHASE_SOURCES:
            if receipt and self._fix_is_import_receipt(receipt):
                raise UserError(
                    "Receipt %s is an import (M44): the import order posts its own journal and "
                    "must name it (context fix_stock_external_move_id), so that the goods are "
                    "not posted to GRNI twice. Nothing was posted." % receipt.name
                )
            return role_code(self.env, "grni"), ACCOUNT_ROLES["grni"][2]
        mapping = _json_param(self.env, PARAM_RECEIPT_SOURCES, {})
        code = mapping.get(_norm(source))
        if not code:
            raise UserError(
                "Receipt %s comes from %s, which is not a purchase: its counter account is not "
                "configured (system parameter %s, a JSON object source model -> account code). "
                "Nothing was posted." % (receipt.name, source, PARAM_RECEIPT_SOURCES)
            )
        return code, "Receipt counter for %s" % source

    def _fix_is_import_receipt(self, receipt):
        if receipt.source_model == "fix.import.order":
            return True
        if "fix.import.order" not in self.env or not receipt.purchase_order_id:
            return False
        Import = self.env["fix.import.order"].sudo()
        if "purchase_order_id" not in Import._fields:
            return False
        return bool(
            Import.search_count(
                [
                    ("purchase_order_id", "=", receipt.purchase_order_id.id),
                    ("receipt_id", "=", False),
                ]
            )
        )

    def _fix_counter(self):
        """(code, label) of the account the stock movement is set against."""
        self.ensure_one()
        kind = self.entry_type
        if kind == "receipt":
            return self._fix_receipt_counter_role_code()
        if kind == "revaluation":
            code = self.env.context.get("fix_stock_counter_account")
            if not code:
                raise UserError(
                    "A stock revaluation (%s) is posted against the account its caller names "
                    "(context fix_stock_counter_account), and none was named: nothing was "
                    "posted." % (self.source_ref or self.name)
                )
            return str(code), "Revaluation counter"
        if kind == "shipment":
            raise UserError(
                "Stock leaving the ledger as a warehouse shipment (%s) has no posting rule: it "
                "leaves through an M15 transfer, return to vendor or job issue. Nothing was "
                "posted (A06 ERP M41 F01)." % (self.source_ref or self.name)
            )
        if kind == "transfer":
            raise UserError("A transfer row is posted with its transfer, not on its own.")
        role = COUNTER_ROLE.get(kind)
        if not role:
            raise UserError(
                "Valuation entry type %s has no posting rule: nothing was posted." % kind
            )
        if kind == "graded_issue" and self.env.context.get("fix_stock_counter_role"):
            role = self.env.context["fix_stock_counter_role"]
        return role_code(self.env, role), ACCOUNT_ROLES[role][2]

    def _fix_post_one(self):
        """Post this row's own balanced entry (real time)."""
        self.ensure_one()
        company = self.company_id
        ou = self._fix_row_ou()
        self._fix_check_zero_cost()
        date = self.posting_date or fields.Date.context_today(self)
        label = "%s %s" % (
            dict(self._fields["entry_type"].selection).get(self.entry_type, self.entry_type),
            self.source_ref or self.name,
        )
        subject = (
            self.product_id.sudo().part_number
            if self.product_id
            else (self.graded_stock_id.sudo().name or "")
        )
        dims = self._fix_dims(ou, self.location_id)
        if self.entry_type == "price_variance":
            # G1: moves no stock - Dr PPV / Cr GRNI for a loss (the AP note
            # credited GRNI at the billed price, the RTV debited it at cost)
            value = round(self.total_valuation or 0.0, 2)
            code = self.clearing_account_code or role_code(self.env, "price_variance")
            ppv = self._fix_account(company, code, ACCOUNT_ROLES["price_variance"][2])
            grni = self._fix_role_account(company, "grni")
            move = self._fix_gl_post(
                company,
                date,
                "%s %s" % (label, subject),
                [(ppv, label, value, dims), (grni, label, -value, dims)],
                source_ref=self.name,
            )
            self._fix_mark_posted(move, stock_code="", counter_code=grni.code, ou=ou)
            return move
        value = stock_effect_value(self)
        stock_code = self._fix_row_stock_code()
        counter_code, counter_label = self._fix_counter()
        if abs(value) < 0.005:
            # a movement of stock carrying no value moves no GL balance
            self._fix_mark_posted(
                self.env["account.move"], stock_code=stock_code, counter_code=counter_code, ou=ou
            )
            return self.env["account.move"]
        stock = self._fix_account(
            company,
            stock_code,
            ACCOUNT_ROLES["graded_stock"][2] if self.graded_stock_id else "Stock of %s" % subject,
        )
        counter = self._fix_account(company, counter_code, counter_label)
        move = self._fix_gl_post(
            company,
            date,
            "%s %s" % (label, subject),
            [
                (stock, "%s %s" % (label, subject), value, dims),
                (counter, "%s %s" % (label, subject), -value, dims),
            ],
            source_ref=self.name,
        )
        self._fix_mark_posted(move, stock_code=stock.code, counter_code=counter.code, ou=ou)
        return move

    # ------------------------------------------------- X19 zero-cost control
    def _fix_check_zero_cost(self):
        """D4: stock with no cost is not counted, issued or written off
        without an approval until Finance prices it."""
        self.ensure_one()
        if self.entry_type not in ZERO_COST_GUARDED or not self.product_id:
            return
        if abs(self.unit_cost or 0.0) > EPS or not self.quantity:
            return
        if self.entry_type == "adjustment":
            approved = self._fix_doc_approved("fix.stock.count")
        elif self.entry_type == "write_off":
            approved = self._fix_doc_approved("fix.stock.quarantine")
        else:
            approved = self.env["fix.stock.uncosted.release"]._fix_consume(
                self.product_id, self.location_id, abs(self.quantity), self.source_ref or self.name
            )
        if not approved:
            raise UserError(
                "%s at %s carries no cost: until Finance prices it, it is counted, issued or "
                "written off only with an Inventory Controller's approval (for an issue: an "
                "approved Uncosted Stock Release). Nothing was moved (A06 ERP D4)."
                % (self.product_id.sudo().part_number, self.location_id.sudo().code or "-")
            )

    def _fix_doc_approved(self, model):
        if not self.source_ref or model not in self.env:
            return False
        doc = (
            self.env[model]
            .sudo()
            .search(
                [("name", "=", self.source_ref), ("company_id", "=", self.company_id.id)], limit=1
            )
        )
        return bool(doc and doc.approved_by_id)

    # ------------------------------------------------------------ transfers
    @api.model
    def _fix_post_transfer(self, transfer, lines, ref=None):
        """A06 ERP D1: stock received from another operating unit moves its
        value between the two OUs on the same stock account: Cr the sender's
        OU, Dr the receiver's, at the value sent. lines = [(part, qty, cost)].
        Same OU: nothing to post. Another company: refused (X20)."""
        transfer = transfer.sudo()
        company = transfer.company_id
        if not self._fix_realtime(company):
            return self.browse()
        src, dst = transfer.from_location_id, transfer.to_location_id
        if src.company_id and dst.company_id and src.company_id != dst.company_id:
            raise UserError(
                "Transfer %s moves stock between two companies, which is refused (inter-company "
                "transfers are not posted)." % transfer.name
            )
        if location_class(src) not in VALUED_CLASSES:
            return self.browse()
        src_ou = self._fix_location_ou(src, company)
        dst_ou = self._fix_location_ou(dst, company)
        if src_ou == dst_ou:
            return self.browse()
        ref = ref or transfer.name
        rows = self.browse()
        gl_lines = []
        Rows = self.sudo().with_context(fix_stock_no_autopost=True)
        for part, qty, cost in lines:
            if qty <= EPS:
                continue
            value = round(qty * (cost or 0.0), 2)
            out_row = Rows.create(
                {
                    "company_id": company.id,
                    "operating_unit_id": src_ou.id,
                    "location_id": src.id,
                    "product_id": part.id,
                    "quantity": -qty,
                    "unit_cost": cost or 0.0,
                    "total_valuation": -value,
                    "entry_type": "transfer",
                    "source_ref": ref,
                }
            )
            in_row = Rows.create(
                {
                    "company_id": company.id,
                    "operating_unit_id": dst_ou.id,
                    "location_id": dst.id,
                    "product_id": part.id,
                    "quantity": qty,
                    "unit_cost": cost or 0.0,
                    "total_valuation": value,
                    "entry_type": "transfer",
                    "source_ref": ref,
                }
            )
            rows |= out_row | in_row
            if value:
                account = self._fix_stock_account(part, company)
                label = "Transfer %s %s" % (ref, part.sudo().part_number)
                gl_lines += [
                    (account, label, value, self._fix_dims(dst_ou, dst)),
                    (account, label, -value, self._fix_dims(src_ou, src)),
                ]
        move = (
            self._fix_gl_post(
                company, rows[:1].posting_date, "Transfer %s" % ref, gl_lines, source_ref=ref
            )
            if gl_lines
            else self.env["account.move"]
        )
        for row in rows:
            code = self._fix_stock_code(row.product_id)
            row._fix_mark_posted(move, stock_code=code, counter_code=code)
        return rows

    # ------------------------------------------------------------- tie-out
    @api.model
    def _fix_stock_codes(self, company) -> set:
        mapping = _json_param(self.env, PARAM_BRAND_ACCOUNTS, DEFAULT_BRAND_ACCOUNTS)
        codes = set(mapping.values()) | {role_code(self.env, "stock_default")}
        graded = role_code(self.env, "graded_stock")
        if graded:
            codes.add(graded)
        return {c for c in codes if c}

    @api.model
    def get_stock_gl_tieout(self, company=None, date=None) -> dict:
        """Per stock account x operating unit: the subledger (posted
        valuation rows up to `date`), the on-hand value now (qty x unit cost of
        the valued classes, graded units in stock) and the GL balance at
        `date`, with the differences. Read-only; Finance / cost viewers."""
        if not self.env.su and not (
            self.env.user.has_group("account.group_account_user")
            or self.env.user.has_group("cd_wms_structure.group_stock_cost_viewer")
        ):
            raise AccessError("The stock-to-GL tie-out is for Finance and cost viewers.")
        company = (
            self.env["res.company"].browse(int(company))
            if isinstance(company, int)
            else (company or self.env.company)
        ).sudo()
        date = fields.Date.to_date(date) if date else dhaka_today()
        codes = self._fix_stock_codes(company)
        table = {}

        def cell(code, ou):
            return table.setdefault(
                (code, ou.id if ou else False),
                {"subledger": 0.0, "onhand": 0.0, "gl": 0.0, "ou": ou},
            )

        Rows = self.sudo()
        for entry in Rows.search(
            [
                ("company_id", "=", company.id),
                ("status", "=", "posted"),
                ("posting_date", "<=", date),
                ("entry_type", "!=", "price_variance"),
            ]
        ):
            if entry.stock_account_code:
                cell(entry.stock_account_code, entry.operating_unit_id)["subledger"] += (
                    stock_effect_value(entry)
                )
        ou_cache = {}
        for bucket in (
            self.env["fix.stock.onhand"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("ownership_class", "in", VALUED_CLASSES),
                    ("qty", ">", 0),
                ]
            )
        ):
            loc = bucket.location_id
            if loc.id not in ou_cache:
                try:
                    ou_cache[loc.id] = self._fix_location_ou(loc, company)
                except UserError:
                    ou_cache[loc.id] = self.env["operating.unit"]
            cell(self._fix_stock_code(bucket.part_id), ou_cache[loc.id])["onhand"] += round(
                bucket.qty * (bucket.unit_cost or 0.0), 2
            )
        graded_code = role_code(self.env, "graded_stock")
        if graded_code:
            for unit in (
                self.env["fix.graded.stock"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("state", "in", ("in_stock", "reserved")),
                        ("ledger_entry_id", "!=", False),
                    ]
                )
            ):
                cell(graded_code, unit._fix_graded_ou())["onhand"] += unit.inventory_valuation
        accounts = (
            self.env["account.account"]
            .sudo()
            .with_company(company)
            .search([("code", "in", list(codes)), ("company_ids", "in", company.id)])
        )
        if accounts:
            lines = (
                self.env["account.move.line"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("parent_state", "=", "posted"),
                        ("account_id", "in", accounts.ids),
                        ("date", "<=", date),
                    ]
                )
            )
            dim_ou = {}
            if lines and "fix.journal.dimension" in self.env:
                for dim in (
                    self.env["fix.journal.dimension"]
                    .sudo()
                    .search([("move_line_id", "in", lines.ids)])
                ):
                    dim_ou[dim.move_line_id.id] = dim.operating_unit_id
            for line in lines:
                cell(line.account_id.code, dim_ou.get(line.id))["gl"] += line.balance
        rows = []
        for (code, _ou_id), vals in sorted(
            table.items(),
            key=lambda kv: (kv[0][0], kv[1]["ou"].display_name if kv[1]["ou"] else ""),
        ):
            sub, onhand, gl = (round(vals[k], 2) for k in ("subledger", "onhand", "gl"))
            rows.append(
                {
                    "account_code": code,
                    "operating_unit_id": vals["ou"].id if vals["ou"] else False,
                    "operating_unit": vals["ou"].display_name if vals["ou"] else "",
                    "subledger_value": sub,
                    "onhand_value": onhand,
                    "gl_balance": gl,
                    "gl_minus_subledger": round(gl - sub, 2),
                    "subledger_minus_onhand": round(sub - onhand, 2),
                }
            )
        totals = {
            k: round(sum(r[k] for r in rows), 2)
            for k in (
                "subledger_value",
                "onhand_value",
                "gl_balance",
                "gl_minus_subledger",
                "subledger_minus_onhand",
            )
        }
        return {
            "company_id": company.id,
            "company": company.name,
            "date": str(date),
            "realtime_since": str(company.fix_stock_realtime_from or ""),
            "onhand_as_of": str(dhaka_today()),
            "rows": rows,
            "totals": totals,
            "ties_out": all(
                abs(r["gl_minus_subledger"]) < 0.005 and abs(r["subledger_minus_onhand"]) < 0.005
                for r in rows
            ),
        }


class FixStockTransferPosting(models.Model):
    """D1: a transfer received from another OU moves the value between OUs."""

    _inherit = "fix.stock.transfer"

    def _fix_posting_plan(self, short=False):
        plan = {}
        Onhand = self.env["fix.stock.onhand"]
        for rec in self.sudo():
            lines = []
            src_cls = location_class(rec.from_location_id)
            for line in rec.line_ids:
                if short:
                    qty = line.discrepancy_qty or 0.0
                    cost = line.unit_cost or 0.0
                else:
                    qty = line._received_quantity()
                    if line.is_dispatched:
                        cost = line.unit_cost or 0.0
                    else:
                        bucket = Onhand._bucket(line.part_id, rec.from_location_id, src_cls)
                        cost = bucket.unit_cost if bucket else 0.0
                lines.append((line.part_id, qty, cost))
            plan[rec.id] = lines
        return plan

    def action_receive(self):
        plan = self._fix_posting_plan()
        result = super().action_receive()
        Suspense = self.env["fix.inventory.valuation.suspense"]
        for rec in self.sudo():
            if rec.state in ("received", "discrepancy"):
                Suspense._fix_post_transfer(rec, plan.get(rec.id, []))
        return result

    def action_resolve_discrepancy(self, resolution=None, note=None):
        found = (resolution or "").strip().lower() == "found"
        plan = self._fix_posting_plan(short=True) if found else {}
        result = super().action_resolve_discrepancy(resolution=resolution, note=note)
        Suspense = self.env["fix.inventory.valuation.suspense"]
        for rec in self.sudo():
            if found:
                Suspense._fix_post_transfer(rec, plan.get(rec.id, []), ref="%s/FOUND" % rec.name)
        return result


class FixStockCountZeroCost(models.Model):
    """D4 / X19: a variance on stock with no cost is never inside tolerance:
    it goes to recount and to an Inventory Controller's approval."""

    _inherit = "fix.stock.count"

    def _tolerance_ok(self, line):
        ok = super()._tolerance_ok(line)
        if not ok or not self.env["fix.inventory.valuation.suspense"]._fix_realtime(
            self.company_id
        ):
            return ok
        if line.ownership_class not in VALUED_CLASSES or abs(line._line_delta()) <= EPS:
            return ok
        return abs(line._snapshot().unit_cost or 0.0) > EPS


class FixStockUncostedRelease(models.Model):
    """D4 / X19: an Inventory Controller's approval to issue a stated quantity
    of a part that carries no cost at a location, until Finance prices it.
    The issue draws it down; nothing else is released."""

    _name = "fix.stock.uncosted.release"
    _description = "Uncosted Stock Release"
    _order = "id desc"
    _inherit = ["fix.inventory.approval.mixin", "mail.thread"]

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Location", required=True, ondelete="restrict"
    )
    qty = fields.Float(string="Quantity Released", required=True)
    qty_used = fields.Float(string="Quantity Issued", readonly=True, default=0.0)
    reason = fields.Char(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("used", "Used Up"),
        ],
        required=True,
        default="draft",
    )
    issue_refs = fields.Char(string="Issued On", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "qty_used", "issue_refs"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = "UCR/%s" % fields.Datetime.now().strftime("%Y%m%d%H%M%S")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open() and self.filtered(lambda r: r.state != "draft"):
            business = set(vals) & {"part_id", "location_id", "qty", "company_id", "reason"}
            if business:
                raise UserError("A submitted uncosted stock release is final.")
        return super().write(vals)

    def action_submit(self):
        if not (
            self.env.su
            or self.env.user.has_group(STOREKEEPER_GROUP)
            or self.env.user.has_group(CONTROLLER_GROUP)
        ):
            raise AccessError("A Storekeeper requests an uncosted stock release.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Submit a draft release.")
            if (rec.qty or 0.0) <= 0:
                raise UserError("Release a positive quantity.")
            rec._inv_stamp_request()
            rec._guarded().write({"state": "submitted"})
        return True

    def action_approve(self, note=None):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Release %s is not awaiting approval." % rec.name)
        self._inv_check_approver()
        for rec in self.sudo():
            rec._inv_stamp_approval(note)
            rec._guarded().write({"state": "approved"})
        return True

    def action_reject(self, note=None):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Release %s is not awaiting approval." % rec.name)
        self._inv_check_approver()
        for rec in self.sudo():
            rec._inv_stamp_approval(note or "rejected")
            rec._guarded().write({"state": "rejected"})
        return True

    @api.model
    def _fix_consume(self, part, location, qty, ref):
        """Draw `qty` from approved releases of this part at this location;
        False when they do not cover it (nothing is drawn then)."""
        releases = self.sudo().search(
            [
                ("part_id", "=", part.id),
                ("location_id", "=", location.id),
                ("state", "=", "approved"),
            ],
            order="id",
        )
        free = sum(max((r.qty or 0.0) - (r.qty_used or 0.0), 0.0) for r in releases)
        if free + EPS < qty:
            return False
        left = qty
        for rec in releases:
            if left <= EPS:
                break
            take = min(max((rec.qty or 0.0) - (rec.qty_used or 0.0), 0.0), left)
            if take <= EPS:
                continue
            used = round((rec.qty_used or 0.0) + take, 4)
            vals = {
                "qty_used": used,
                "issue_refs": ", ".join(x for x in (rec.issue_refs, ref) if x),
            }
            if used + EPS >= rec.qty:
                vals["state"] = "used"
            rec._guarded().write(vals)
            left -= take
        return True
