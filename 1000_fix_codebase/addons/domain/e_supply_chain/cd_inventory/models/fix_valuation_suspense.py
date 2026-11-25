# cd_inventory — M15->M19 Inventory Valuation Suspense Account Model (GV-005 Stub).
# Inventory movements and baseline loads post valuation to suspense account
# 110999 until General Ledger (M19) cutover in Wave 3 / Phase R04.
#
# A06 audit (2026-11-03) M15-7 / S0: the ledger M19 will clear was editable
# by every user (a clerk marked an entry reconciled at 0 and created a
# BDT 500,000 "initial_count" entry), and on fix_dev the initial baseline is
# loaded TWICE (2 x 1,900 rows, BDT 50.4M pending against BDT 12.6M of
# stock). The model is now system-written only: no user ACL creates or
# writes it, every field is guarded, rows cannot be deleted, and "reconciled"
# is reachable only through the M19 cutover (cd_gl_ext period close, which
# proves a posted journal entry clears the pending total) or trusted code.
# get_baseline_integrity() reports a duplicated baseline and the suspense
# against the on-hand value so Finance sees the problem; it changes nothing.
from __future__ import annotations

from datetime import datetime

import pytz
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

from .fix_inventory_approval import VALUED_CLASSES

FINANCE_ADMIN_GROUP = "account.group_account_manager"

# The GL account the period close moves this suspense off. 110999 is the
# development chart's code; a company on its own chart (the real legacy chart
# has no 110999) names its account in this parameter, or the close refuses.
SUSPENSE_ACCOUNT_PARAM = "cd_inventory.valuation_suspense_account_code"
DEFAULT_SUSPENSE_ACCOUNT_CODE = "110999"


def suspense_account_code(env):
    """The account code every new suspense row is stamped with."""
    code = env["ir.config_parameter"].sudo().get_param(SUSPENSE_ACCOUNT_PARAM) or ""
    return code.strip() or DEFAULT_SUSPENSE_ACCOUNT_CODE


def dhaka_today(moment=None):
    """The Asia/Dhaka business date of `moment` (a naive UTC datetime, now
    when omitted): the GL date of a stock movement and its period cut-off."""
    moment = moment or datetime.utcnow()
    return pytz.utc.localize(moment).astimezone(pytz.timezone("Asia/Dhaka")).date()


# How each entry type moves the company's stock value. Consumption and return
# predate this file and carry the VALUE CONSUMED (an issue +, its return -);
# every later type carries the stock movement itself (+ in, - out).
STOCK_EFFECT = {
    "consumption": -1.0,
    "return": -1.0,
    "initial_count": 1.0,
    "revaluation": 1.0,
    "receipt": 1.0,
    "adjustment": 1.0,
    "write_off": 1.0,
    "rtv": 1.0,
    "shipment": 1.0,
    "class_change": 1.0,
    # G1: a return to vendor's purchase-price variance moves no stock; the
    # cut-over clears it from the suspense account to its clearing account
    "price_variance": 0.0,
    # A06 ERP (D1): an inter-OU transfer is two rows (- at the sender's OU,
    # + at the receiver's), graded refurbished stock enters (+) and leaves (-)
    "transfer": 1.0,
    "graded_intake": 1.0,
    "graded_issue": 1.0,
}


def stock_effect_value(entry) -> float:
    """The signed stock-value movement of one row (+ into stock, - out)."""
    return round((entry.total_valuation or 0.0) * STOCK_EFFECT.get(entry.entry_type, 1.0), 2)


# G1 (owner decision 12 Nov 2026): the account a return to vendor's
# purchase-price variance is cleared to by the period-close cut-over. Unset:
# the variance is recorded on the RTV only, never posted to a guessed account.
PRICE_VARIANCE_PARAM = "cd_inventory.account_code.price_variance"


class FixInventoryValuationSuspense(models.Model):
    """M15 Inventory Valuation Suspense Entries (GV-005 STUB-M15-M19-001)."""

    _name = "fix.inventory.valuation.suspense"
    _description = "Inventory Valuation Suspense Entry"
    _order = "create_date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

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
        string="Entry Reference",
        required=True,
        copy=False,
        default="New",
        index=True,
    )
    name_bn = fields.Char(
        string="মূল্যায়ন এন্ট্রি রেফারেন্স (বাংলা)",
        help="Bengali reference per DoD-08",
    )

    consumption_id = fields.Many2one(
        "fix.stock.consumption",
        string="Originating Consumption",
        index=True,
        ondelete="set null",
    )
    source_ref = fields.Char(string="Source Document", index=True)
    # A06 ERP X17: a graded refurbished unit is a device, not a part; its rows
    # name the unit instead (one of the two is always set, see _check_subject)
    product_id = fields.Many2one(
        "fix.spare.part",
        string="Spare Part",
        index=True,
    )
    graded_stock_id = fields.Many2one(
        "fix.graded.stock", string="Graded Refurb Unit", index=True, ondelete="restrict"
    )
    # A06 ERP D1 (owner decision 20 Nov 2026): every row posts its own
    # balanced journal entry as the movement happens. The subledger keeps the
    # movement; the GL entry, the accounts it used and the business (Dhaka)
    # date are recorded on it.
    location_id = fields.Many2one(
        "fix.stock.location", string="Stock Location", index=True, ondelete="restrict"
    )
    posting_date = fields.Date(
        string="Business Date",
        index=True,
        help="The Asia/Dhaka date of the movement: the GL date and the period cut-off.",
    )
    move_id = fields.Many2one(
        "account.move", string="Journal Entry", index=True, readonly=True, copy=False
    )
    stock_account_code = fields.Char(string="Stock Account", readonly=True, copy=False)
    counter_account_code = fields.Char(string="Counter Account", readonly=True, copy=False)
    posted_at = fields.Datetime(string="Posted On", readonly=True, copy=False)
    quantity = fields.Float(
        string="Movement Quantity",
        required=True,
        default=0.0,
    )
    unit_cost = fields.Float(
        string="Unit Cost (BDT)",
        required=True,
        default=0.0,
    )
    total_valuation = fields.Float(
        string="Total Valuation (BDT)",
        required=True,
        default=0.0,
    )

    entry_type = fields.Selection(
        [
            ("consumption", "Job Consumption"),
            ("return", "Job Return"),
            ("revaluation", "Inventory Revaluation"),
            ("initial_count", "Physical Baseline Migration"),
            ("receipt", "Goods Receipt"),
            ("adjustment", "Count / Van Adjustment"),
            ("write_off", "Scrap / Write-off"),
            ("rtv", "Return to Vendor"),
            ("shipment", "Warehouse Shipment"),
            ("class_change", "Ownership-Class Change"),
            ("price_variance", "Purchase Price Variance (RTV)"),
            ("transfer", "Inter-OU Transfer"),
            ("graded_intake", "Graded Refurb Intake"),
            ("graded_issue", "Graded Refurb Sale / Disposal"),
        ],
        string="Entry Type",
        required=True,
        default="consumption",
    )

    suspense_account_code = fields.Char(
        string="Suspense Account Code",
        required=True,
        default=lambda self: suspense_account_code(self.env),
        help="Suspense clearing account code (system parameter %s, default %s)"
        % (SUSPENSE_ACCOUNT_PARAM, DEFAULT_SUSPENSE_ACCOUNT_CODE),
    )
    # G1: a row that is not stock (STOCK_EFFECT 0) names the account the
    # cut-over moves its value to, off the suspense account: Dr <account> /
    # Cr suspense for a positive value (a loss), the reverse for a gain.
    clearing_account_code = fields.Char(
        string="Clears To Account",
        help="Price-variance rows: the account the period-close cut-over clears this value "
        "to from the suspense account (system parameter %s when it was booked)."
        % PRICE_VARIANCE_PARAM,
    )
    status = fields.Selection(
        [
            ("pending_gl_cutover", "Pending GL Cutover (M19 Suspense)"),
            ("posted", "Posted to GL (real time)"),
            ("reconciled", "Reconciled to GL"),
            ("archived", "Archived"),
        ],
        string="GL Status",
        required=True,
        default="pending_gl_cutover",
        index=True,
    )

    stub_reference = fields.Char(
        string="GV-005 Stub Reference",
        required=True,
        default="STUB-M15-M19-001",
        readonly=True,
        help="Reference in docs/traceability/gv-005-stub-register.md",
    )
    stub_expiry_date = fields.Date(
        string="Stub Expiry Target",
        default=lambda self: fields.Date.to_date("2026-11-30"),
        readonly=True,
        help="Expiry target: Wave 3 / Phase R04 M19 GL cutover",
    )

    gl_cutover_ref = fields.Char(string="GL Cutover Voucher Ref")
    reconciled_at = fields.Datetime(string="Reconciled Timestamp")
    # S0: a duplicated baseline row archived on Finance authority (never deleted)
    archived_by_id = fields.Many2one("res.users", string="Archived By", readonly=True, copy=False)
    archived_at = fields.Datetime(string="Archived On", readonly=True, copy=False)
    archive_ref = fields.Char(string="Finance Approval Ref", readonly=True, copy=False)
    duplicate_of_id = fields.Many2one(
        "fix.inventory.valuation.suspense",
        string="Duplicate Of",
        readonly=True,
        copy=False,
        help="The baseline row this one duplicated (the one kept).",
    )
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        readonly=True,
        copy=False,
        help="MIG-03: permanent source-system reference written by the inventory "
        "loader (migrations/load_inventory.py) - never edited, never copied",
    )

    # Every stored business field is evidence for the M19 cutover: none is typed.
    _SYSTEM_FIELDS = (
        "company_id",
        "operating_unit_id",
        "name",
        "name_bn",
        "consumption_id",
        "source_ref",
        "product_id",
        "quantity",
        "unit_cost",
        "total_valuation",
        "entry_type",
        "suspense_account_code",
        "clearing_account_code",
        "status",
        "gl_cutover_ref",
        "reconciled_at",
        "legacy_reference",
        "archived_by_id",
        "archived_at",
        "archive_ref",
        "duplicate_of_id",
        "graded_stock_id",
        "location_id",
        "posting_date",
        "move_id",
        "stock_account_code",
        "counter_account_code",
        "posted_at",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._SYSTEM_FIELDS)

    @api.constrains("product_id", "graded_stock_id")
    def _check_subject(self):
        for entry in self:
            if not entry.product_id and not entry.graded_stock_id:
                raise UserError("A valuation entry names the spare part or graded unit it values.")

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError(
                "Valuation suspense entries are written by the stock movements "
                "themselves; they cannot be created by hand."
            )
        Consumption = self.env["fix.stock.consumption"].sudo()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                seq = self.env["ir.sequence"].next_by_code("fix.inventory.valuation.suspense")
                vals["name"] = seq or f"VAL-SUSP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            if "total_valuation" not in vals and "quantity" in vals and "unit_cost" in vals:
                vals["total_valuation"] = vals["quantity"] * vals["unit_cost"]
            # A06 ERP D1: the business date and the location every row is
            # posted from (a job issue writes its row directly, naming only
            # its consumption)
            vals.setdefault("posting_date", dhaka_today())
            if not vals.get("location_id") and vals.get("consumption_id"):
                vals["location_id"] = Consumption.browse(vals["consumption_id"]).location_id.id
        records = super().create(vals_list)
        # A06 ERP D1: each row posts its own journal entry now (a company on
        # real-time posting; rows of a company not yet switched over by its
        # stock take-on stay pending for the old cut-over)
        records._fix_post_realtime()
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            touched = set(vals) & set(self._SYSTEM_FIELDS)
            if touched:
                self._fix_guard_refuse(touched)
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError(
                "Valuation suspense entries are audit evidence for the M19 cutover and "
                "cannot be deleted."
            )
        return super().unlink()

    # ------------------------------------------------------------------ posting
    @api.model
    def _fix_post(
        self, entry_type, part, quantity, unit_cost, source_ref, location=None, ownership="owned"
    ):
        """Book one movement (system path). Non-owned classes (consignment,
        customer property) are held stock and never valued (BRU-INV-02)."""
        if ownership not in VALUED_CLASSES or not quantity:
            return self.browse()
        company = (location.company_id if location else False) or part.company_id
        operating_unit = (location.operating_unit_id if location else False) or (
            part.operating_unit_id
        )
        return self.sudo().create(
            {
                "company_id": company.id,
                "operating_unit_id": operating_unit.id if operating_unit else False,
                "location_id": location.id if location else False,
                "product_id": part.id,
                "quantity": quantity,
                "unit_cost": unit_cost or 0.0,
                "total_valuation": round(quantity * (unit_cost or 0.0), 2),
                "entry_type": entry_type,
                "source_ref": source_ref or False,
                "suspense_account_code": suspense_account_code(self.env),
                "status": "pending_gl_cutover",
            }
        )

    @api.model
    def _fix_post_price_variance(
        self, part, quantity, value, source_ref, account_code, location=None, company=None
    ):
        """G1: book a return to vendor's purchase-price variance, `value` =
        quantity x (average cost the stock left at - price the vendor
        credits), as a pending row of its own. It moves no stock (STOCK_EFFECT
        0): the period-close cut-over clears it from the suspense account to
        `account_code` (Dr PPV / Cr suspense for a loss)."""
        value = round(value or 0.0, 2)
        if abs(value) < 0.005 or not account_code:
            return self.browse()
        company = company or (location.company_id if location else False) or part.company_id
        operating_unit = (location.operating_unit_id if location else False) or (
            part.operating_unit_id
        )
        return self.sudo().create(
            {
                "company_id": company.id,
                "operating_unit_id": operating_unit.id if operating_unit else False,
                "location_id": location.id if location else False,
                "product_id": part.id,
                "quantity": quantity,
                "unit_cost": round(value / quantity, 4) if quantity else value,
                "total_valuation": value,
                "entry_type": "price_variance",
                "source_ref": source_ref or False,
                "suspense_account_code": suspense_account_code(self.env),
                "clearing_account_code": account_code,
                "status": "pending_gl_cutover",
            }
        )

    # ------------------------------------------------------------ reconciliation
    def _fix_cutover_clearings(self) -> dict:
        """G1: {account code: value} the cut-over must move off the suspense
        account to other accounts (price-variance rows), on top of the stock
        movement _fix_stock_effect_total sizes. A positive value is debited
        to the account and credited to the suspense account."""
        out = {}
        for entry in self.filtered(lambda e: e.clearing_account_code):
            code = entry.clearing_account_code
            out[code] = round(out.get(code, 0.0) + entry.total_valuation, 2)
        return out

    def _fix_stock_effect_total(self) -> float:
        """The net stock-value movement of these entries: each row's value with
        the sign STOCK_EFFECT gives its type (a consumption carries the value
        consumed, so it moves stock out). The period close sizes the suspense
        cutover on this, not on the raw sum of the rows (E2E2, 11 Nov: a 1,500
        job issue was counted as 1,500 into stock)."""
        return round(sum(e.total_valuation * STOCK_EFFECT.get(e.entry_type, 1.0) for e in self), 2)

    def action_reconcile_to_gl(self, gl_voucher_ref: str) -> dict:
        """Mark suspense entries reconciled against an M19 cutover journal.

        Trusted code (sudo) may call it. Otherwise the voucher must be the
        POSTED cutover journal entry of an M19 period close of the entry's
        company (cd_gl_ext's action_reconcile_inventory_suspense, which has
        already proved that the entry clears the pending total); a typed
        voucher reference reconciles nothing."""
        if not gl_voucher_ref:
            raise UserError("GL Voucher reference is mandatory for reconciliation.")
        if not self.env.su:
            self._fix_check_cutover_voucher(gl_voucher_ref)
        now = fields.Datetime.now()
        for rec in self:
            if rec.status != "pending_gl_cutover":
                raise UserError("Suspense entry %s is not pending GL cutover." % rec.name)
            rec.sudo()._guarded().write(
                {"status": "reconciled", "gl_cutover_ref": gl_voucher_ref, "reconciled_at": now}
            )
        if len(self) == 1:
            return {"status": "reconciled", "entry": self.name, "gl_voucher": gl_voucher_ref}
        return {"status": "reconciled", "entries": len(self), "gl_voucher": gl_voucher_ref}

    def _fix_check_cutover_voucher(self, voucher):
        if "account.move" not in self.env or "fix.period.close" not in self.env:
            raise AccessError("Suspense entries are reconciled only by the M19 GL cutover.")
        Close = self.env["fix.period.close"].sudo()
        for company in self.mapped("company_id"):
            move = (
                self.env["account.move"]
                .sudo()
                .search(
                    [
                        ("name", "=", voucher),
                        ("company_id", "=", company.id),
                        ("state", "=", "posted"),
                    ],
                    limit=1,
                )
            )
            close = (
                Close.search(
                    [("company_id", "=", company.id), ("cutover_move_id", "=", move.id)], limit=1
                )
                if move and "cutover_move_id" in Close._fields
                else Close.browse()
            )
            if not move or not close:
                raise AccessError(
                    "%s is not the posted cutover journal entry of an M19 period close of %s: "
                    "suspense entries are reconciled only by the GL cutover."
                    % (voucher, company.name)
                )

    # ------------------------------------------------------- integrity report
    @api.model
    def get_baseline_integrity(self, company_ids=None) -> dict:
        """Read-only: is the initial-count baseline loaded more than once, and
        how does the pending suspense compare with the on-hand value?

        A duplicate is a pending `initial_count` row identical to another in
        company, part, reference, quantity and unit cost. Nothing is changed:
        removing duplicates is a Finance decision taken before the
        2026-11-30 cutover. Reads as the caller (company rules apply)."""
        companies = (
            self.env["res.company"].browse(company_ids) if company_ids else self.env.companies
        )
        result = []
        Onhand = self.env["fix.stock.onhand"]
        for company in companies:
            pending = self.search(
                [("company_id", "=", company.id), ("status", "=", "pending_gl_cutover")]
            )
            baseline = pending.filtered(lambda e: e.entry_type == "initial_count")
            groups = self._baseline_groups(baseline)
            duplicate_groups = [rows for rows in groups.values() if len(rows) > 1]
            blocked = self._baseline_blocked_keys(company, groups)
            extra_rows = sum(len(rows) - 1 for rows in duplicate_groups)
            excess_value = round(
                sum(rows[0].total_valuation * (len(rows) - 1) for rows in duplicate_groups), 2
            )
            baseline_total = round(sum(baseline.mapped("total_valuation")), 2)
            movement_value = round(
                sum(
                    e.total_valuation * STOCK_EFFECT.get(e.entry_type, 1.0)
                    for e in pending - baseline
                ),
                2,
            )
            buckets = Onhand.search(
                [("company_id", "=", company.id), ("ownership_class", "in", VALUED_CLASSES)]
            )
            onhand_value = round(sum((b.qty or 0.0) * (b.unit_cost or 0.0) for b in buckets), 2)
            implied = round(baseline_total - excess_value + movement_value, 2)
            result.append(
                {
                    "company_id": company.id,
                    "company": company.name,
                    "pending_entries": len(pending),
                    # A06 ERP X06: the signed stock movement (an issue is stock
                    # OUT), not the raw sum of the rows' values
                    "pending_total": pending._fix_stock_effect_total(),
                    "pending_clearings": round(sum(pending._fix_cutover_clearings().values()), 2),
                    "baseline_entries": len(baseline),
                    "baseline_total": baseline_total,
                    "duplicate_groups": len(duplicate_groups),
                    "duplicate_extra_rows": extra_rows,
                    "duplicate_excess_value": excess_value,
                    "baseline_after_dedup": round(baseline_total - excess_value, 2),
                    "movement_value": movement_value,
                    "onhand_value": onhand_value,
                    "implied_stock_value": implied,
                    "gap_vs_onhand": round(implied - onhand_value, 2),
                    "baseline_duplicated": bool(duplicate_groups),
                    # action_archive_duplicate_baseline can clear them (no group
                    # holds a row already reconciled to the GL)
                    "dedup_available": bool(duplicate_groups) and not blocked,
                    "dedup_blocked_groups": len(blocked),
                }
            )
        return {"companies": result}

    # ------------------------------------------- S0: archive the duplicates
    @api.model
    def _baseline_key(self, entry):
        return (
            entry.product_id.id,
            entry.legacy_reference or entry.name,
            round(entry.quantity, 4),
            round(entry.unit_cost, 4),
        )

    @api.model
    def _baseline_groups(self, entries):
        groups = {}
        for entry in entries.sorted("id"):
            groups.setdefault(self._baseline_key(entry), []).append(entry)
        return groups

    @api.model
    def _baseline_blocked_keys(self, company, groups):
        """Duplicate groups that also hold a row already reconciled to the GL:
        archiving their pending copies would hide a cutover already made."""
        reconciled = self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("entry_type", "=", "initial_count"),
                ("status", "=", "reconciled"),
            ]
        )
        keys = {self._baseline_key(entry) for entry in reconciled}
        return {key for key, rows in groups.items() if len(rows) > 1 and key in keys} | {
            key for key in keys if key in groups
        }

    @api.model
    def action_archive_duplicate_baseline(self, company_id, finance_approval_ref):
        """S0 (A06): archive every extra copy of a duplicated initial-count
        baseline, keeping exactly one row per group. Accounting
        Administrators only, on a Finance approval reference. Rows are
        archived (status 'archived', who / when / the reference recorded),
        never deleted; the M19 cutover clears only 'pending_gl_cutover' rows.
        Idempotent. Refuses if any duplicated group holds a reconciled row."""
        if not self.env.su and not self.env.user.has_group(FINANCE_ADMIN_GROUP):
            raise AccessError(
                "Only an Accounting Administrator can archive the duplicated baseline."
            )
        ref = (finance_approval_ref or "").strip()
        if not ref:
            raise UserError("Give the Finance approval reference for archiving the baseline.")
        company = self.env["res.company"].browse(int(company_id)).exists()
        if not company:
            raise UserError("Unknown company %s." % company_id)
        Suspense = self.sudo()
        pending = Suspense.search(
            [
                ("company_id", "=", company.id),
                ("entry_type", "=", "initial_count"),
                ("status", "=", "pending_gl_cutover"),
            ]
        )
        groups = self._baseline_groups(pending)
        blocked = self._baseline_blocked_keys(company, groups)
        if blocked:
            raise UserError(
                "%d duplicated baseline group(s) already hold a row reconciled to the GL: "
                "archiving their copies would hide a cutover already made. Resolve those "
                "with Finance first; nothing was archived." % len(blocked)
            )
        now = fields.Datetime.now()
        archived = Suspense.browse()
        value = 0.0
        for rows in groups.values():
            if len(rows) < 2:
                continue
            keep = rows[0]
            for extra in rows[1:]:
                extra._guarded().write(
                    {
                        "status": "archived",
                        "archived_by_id": self.env.uid,
                        "archived_at": now,
                        "archive_ref": ref,
                        "duplicate_of_id": keep.id,
                    }
                )
                archived |= extra
                value += extra.total_valuation
        summary = {
            "company_id": company.id,
            "finance_approval_ref": ref,
            "archived_rows": len(archived),
            "archived_value": round(value, 2),
            "groups": len([rows for rows in groups.values() if len(rows) > 1]),
            "archived_by": self.env.uid,
        }
        if archived:
            publish(
                self.env,
                "inventory.baseline_deduplicated",
                "fix.inventory.valuation.suspense",
                archived[:1].id,
                summary,
            )
        return summary
