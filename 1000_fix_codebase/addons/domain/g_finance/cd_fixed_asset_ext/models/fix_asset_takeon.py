# fix_asset_takeon — M49 legacy fixed-asset register take-on (2026-11-25).
#
# The asset lane of the governed take-on family (fix.ledger.takeon /
# fix.legacy.ledger / fix.ap.takeon / fix.bank.takeon): upload the legacy
# register spreadsheet -> stage -> validate (crosswalks, arithmetic,
# quarantine) -> post through the M19 funnel -> rollback by mirror.
#
# An asset cannot be typed into service: BRU-FXA-01 activates it only from a
# posted capitalisation seam. The take-on therefore posts TWO entries on the
# MIG journal dated the take-on date:
#   1. acquisition — Dr each category's asset account per asset (= gross),
#      Cr the take-on contra (2.99.99.901);
#   2. opening accumulated depreciation — Dr the contra, Cr each category's
#      accumulated account per asset (= legacy accum).
# One seam per asset points at its posted debit line; the draft asset is
# created with its legacy reference (MIG-03) and activated. The opening
# depreciation runs (book + tax) carry posted lines equal to the legacy accum
# whose GL is ALREADY carried by entry 2 — no second posting. The engine's
# _book_amount then charges (NBV - salvage) / remaining months from the next
# month (life_months = remaining + 1, the opening line counts as one posted
# month), landing exactly on salvage in the last month.
#
# Idempotency: external ids __asset_takeon__.a_<import_ref>_<SL>; a re-run
# quarantines rows already taken on. The contra holds the net legacy position
# until every subledger is taken on, then reclassifies to opening equity
# (tier-1 rule, fix_ledger_takeon).
import base64
import io
import json
import logging
from datetime import date

from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_asset_common import (
    assert_period_open,
    dhaka_today,
    money,
    month_end,
    month_start,
    post_entry,
)

_logger = logging.getLogger(__name__)

TAKEON_JOURNAL_CODE = "MIG"
CONTRA_CODE = "2.99.99.901"
CONTRA_NAME = "Legacy Ledger Take-on Contra"
XID_MODULE = "__asset_takeon__"

# code-first (the 1 cross-coded row resolves by its code), then head.
# Overridable per estate: ir.config_parameter
# cd_fixed_asset_ext.takeon.category_crosswalk (JSON {code-or-head: category code}).
DEFAULT_CATEGORY_CROSSWALK = {
    "100039": "FURN",
    "100041": "IT",
    "100043": "OFF",
    "100044": "VEH",
    "100803": "TOOL",
    "100040": "RENO",
    "100042": "EST",
    "100804": "SW",
    "Furniture": "FURN",
    "Computer & Computer Equipment": "IT",
    "Office Equipment": "OFF",
    "Vehicle": "VEH",
    "Tools": "TOOL",
    "Office Renovation": "RENO",
    "Establishment": "EST",
    "Software and Software Development": "SW",
    "Office Decoration": "RENO",
}

# header aliases of the compiled register (Asset_List_Compiled.xlsx layout)
HEADER_ALIASES = {
    "sl": ["sl", "serial", "serial no", "sl no"],
    "coa_code": ["coa code", "code", "gl code", "account code"],
    "coa_head": ["coa head", "head", "asset head", "category"],
    "product": ["product name (short)", "product name", "asset name", "description", "particulars"],
    "acquired": ["acquisition date", "purchase date", "date of acquisition", "date"],
    "fy": ["financial year", "fy", "fiscal year"],
    "branch": ["cost centre / branch", "cost centre", "branch", "location", "cost center / branch"],
    "cost": ["cost (tk)", "cost", "gross", "purchase cost", "original cost"],
    "accum": [
        "accumulated depreciation (tk)",
        "accumulated depreciation",
        "accum dep",
        "accumulated",
    ],
    "nbv": ["net book value (tk)", "net book value", "nbv", "book value"],
    "pct": ["depreciation %", "dep %", "depreciation percent"],
    "voucher": ["voucher / move no", "voucher", "move no", "voucher no", "reference"],
}


def _norm_header(raw):
    return str(raw or "").strip().lower()


def _match_columns(header_row):
    """Map the file's header row onto the canonical column keys."""
    cols = {}
    for idx, raw in enumerate(header_row):
        h = _norm_header(raw)
        for key, aliases in HEADER_ALIASES.items():
            if key not in cols and h in aliases:
                cols[key] = idx
    return cols


def _is_total_row(values):
    return any(
        isinstance(v, str) and v.strip().lower().startswith(("total", "grand total"))
        for v in values
    )


def _as_date(value):
    if isinstance(value, date):
        return value
    if value in (None, ""):
        return False
    text = str(value).strip()[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return False


def _as_float(value):
    if value in (None, ""):
        return 0.0
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return 0.0


class FixAssetTakeonBatch(models.Model):
    _name = "fix.asset.takeon.batch"
    _description = "Fixed Asset Take-on Batch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Take-on", compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    source_file = fields.Binary(string="Asset Register (.xlsx)", attachment=True)
    source_filename = fields.Char(string="File Name")
    import_ref = fields.Char(
        string="Import Reference",
        required=True,
        copy=False,
        default=lambda self: "ASSET-%s" % fields.Date.context_today(self).strftime("%Y-%m"),
        help="Permanent legacy-key prefix (MIG-03): <ref>-SL-<serial>.",
    )
    takeon_date = fields.Date(
        string="Take-on Date (period boundary)",
        required=True,
        default=lambda self: month_end(dhaka_today(self.env)),
        tracking=True,
    )
    contra_operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Contra Line Branch",
        help="The wash line's dimension; every asset line carries its own branch.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("staged", "Staged"),
            ("validated", "Validated"),
            ("posted", "Posted"),
            ("rolled_back", "Rolled Back"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.asset.takeon.line", "batch_id", string="Lines")
    decision_log = fields.Text(string="Decision Log", readonly=True, copy=False)
    line_count = fields.Integer(string="Source Rows", compute="_compute_counts", store=True)
    ready_count = fields.Integer(string="Ready Rows", compute="_compute_counts", store=True)
    quarantined_count = fields.Integer(string="Quarantined", compute="_compute_counts", store=True)
    posted_count = fields.Integer(string="Posted Assets", compute="_compute_counts", store=True)
    total_cost = fields.Monetary(string="Total Cost", compute="_compute_counts", store=True)
    total_accum = fields.Monetary(
        string="Total Accumulated Depreciation", compute="_compute_counts", store=True
    )
    total_nbv = fields.Monetary(string="Total NBV", compute="_compute_counts", store=True)
    move_ids = fields.Many2many("account.move", string="Take-on Entries", readonly=True, copy=False)
    run_ids = fields.Many2many(
        "fix.asset.depreciation.run", string="Opening Depreciation Runs", readonly=True, copy=False
    )

    @api.depends("import_ref", "takeon_date")
    def _compute_name(self):
        for rec in self:
            rec.name = "Asset Take-on %s (%s)" % (
                rec.import_ref or "",
                rec.takeon_date or "",
            )

    @api.depends(
        "line_ids.state", "line_ids.cost", "line_ids.accum_depreciation", "line_ids.asset_id"
    )
    def _compute_counts(self):
        for rec in self:
            lines = rec.line_ids
            rec.line_count = len(lines)
            rec.ready_count = len(lines.filtered(lambda ln: ln.state == "ready"))
            rec.quarantined_count = len(lines.filtered(lambda ln: ln.state == "quarantined"))
            rec.posted_count = len(lines.filtered(lambda ln: ln.state == "posted"))
            rec.total_cost = money(sum(lines.mapped("cost")))
            rec.total_accum = money(sum(lines.mapped("accum_depreciation")))
            rec.total_nbv = money(sum(lines.mapped("nbv")))

    # ------------------------------------------------------------- helpers
    def _log(self, message):
        self.ensure_one()
        stamp = fields.Datetime.now()
        user = self.env.user.name
        self.sudo().write(
            {"decision_log": "%s\n[%s] %s: %s" % (self.decision_log or "", stamp, user, message)}
        )

    def _category_crosswalk(self):
        raw = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cd_fixed_asset_ext.takeon.category_crosswalk")
        )
        walk = dict(DEFAULT_CATEGORY_CROSSWALK)
        if raw:
            try:
                walk.update(json.loads(raw))
            except (TypeError, ValueError):
                _logger.warning("takeon category_crosswalk parameter is not JSON; using defaults")
        return walk

    def _branch_crosswalk(self):
        raw = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cd_gl_ext.legacy_ledger.branch_crosswalk")
        )
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            return {}

    def _resolve_branch(self, label):
        """name -> estate crosswalk -> canonical aliases; the branch's own OU."""
        from odoo.addons.cd_gl_ext.models.fix_legacy_ledger import LEGACY_BRANCH_ALIASES

        Branch = self.env["fix.branch"].sudo()
        company = self.company_id
        domain = [("company_id", "in", (company.id, False))]
        label = (label or "").strip()
        if not label:
            return self.env["fix.branch"]
        branch = Branch.search([("name", "=", label), *domain], limit=1)
        if branch:
            return branch
        target = self._branch_crosswalk().get(label) or LEGACY_BRANCH_ALIASES.get(label)
        if target:
            branch = Branch.search([("name", "=", target), *domain], limit=1)
        return branch or self.env["fix.branch"]

    def _ensure_mig_journal(self):
        Journal = self.env["account.journal"].sudo()
        journal = Journal.search(
            [("code", "=", TAKEON_JOURNAL_CODE), ("company_id", "=", self.company_id.id)], limit=1
        )
        if not journal:
            journal = Journal.create(
                {
                    "name": "Legacy Take-on",
                    "code": TAKEON_JOURNAL_CODE,
                    "type": "general",
                    "company_id": self.company_id.id,
                }
            )
        return journal

    def _ensure_contra(self):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import ensure_legacy_account

        return ensure_legacy_account(
            self.env, self.company_id, CONTRA_NAME, CONTRA_CODE, "liability_current"
        )

    def _xid_name(self, sl):
        return "a_%s_%s" % (self.import_ref, sl)

    # ------------------------------------------------------------- actions
    def action_stage(self):
        """Parse the register: one line per asset row, total rows skipped."""
        self.ensure_one()
        if self.state not in ("draft", "staged"):
            raise UserError(self.env._("Only a draft or staged take-on can be staged."))
        if not self.source_file:
            raise UserError(self.env._("Attach the asset register spreadsheet first."))
        import openpyxl

        try:
            wb = openpyxl.load_workbook(
                io.BytesIO(base64.b64decode(self.source_file)), read_only=True, data_only=True
            )
        except Exception as exc:
            raise UserError(
                self.env._("The file is not a readable .xlsx workbook: %s", exc)
            ) from exc
        ws = wb.worksheets[0]
        rows = list(ws.iter_rows(values_only=True))
        header_idx, cols = None, {}
        for i, row in enumerate(rows[:10]):
            cand = _match_columns(row)
            if {"sl", "cost", "accum", "product"}.issubset(cand):
                header_idx, cols = i, cand
                break
        if header_idx is None:
            raise UserError(
                self.env._(
                    "No recognised header row (need SL / Product / Cost / Accumulated "
                    "Depreciation columns)."
                )
            )
        self.line_ids.unlink()
        vals = []
        skipped = 0
        for row in rows[header_idx + 1 :]:
            values = list(row)
            if all(v in (None, "") for v in values):
                continue
            if _is_total_row(values):
                skipped += 1
                continue

            def cell(key, values=values):
                idx = cols.get(key)
                return values[idx] if idx is not None and idx < len(values) else None

            vals.append(
                {
                    "batch_id": self.id,
                    "sl": int(_as_float(cell("sl"))) if cell("sl") not in (None, "") else 0,
                    "legacy_coa_code": str(cell("coa_code") or "").strip(),
                    "legacy_head": str(cell("coa_head") or "").strip(),
                    "product_name": str(cell("product") or "").strip(),
                    "acquisition_date": _as_date(cell("acquired")),
                    "fy_label": str(cell("fy") or "").strip(),
                    "branch_label": str(cell("branch") or "").strip(),
                    "cost": money(_as_float(cell("cost"))),
                    "accum_depreciation": money(_as_float(cell("accum"))),
                    "source_nbv": money(_as_float(cell("nbv"))),
                    "dep_fraction": _as_float(cell("pct")),
                    "voucher": str(cell("voucher") or "").strip(),
                    "state": "staged",
                }
            )
        self.env["fix.asset.takeon.line"].create(vals)
        self.write({"state": "staged"})
        self._log(
            "Staged %s row(s) from %s (%s total row(s) skipped)."
            % (len(vals), self.source_filename or "upload", skipped)
        )
        return True

    def action_validate(self):
        """Resolve crosswalks, prove the arithmetic, quarantine what fails."""
        self.ensure_one()
        if self.state not in ("staged", "validated"):
            raise UserError(self.env._("Stage the spreadsheet before validating."))
        walk = self._category_crosswalk()
        Category = self.env["fix.asset.category"].sudo()
        xids = self.env["ir.model.data"].sudo()
        seen = set()
        ready = quarantined = 0
        for line in self.line_ids:
            reasons = []
            if not line.sl:
                reasons.append("missing SL (row key)")
            elif line.sl in seen:
                reasons.append("duplicate SL %s in file" % line.sl)
            seen.add(line.sl)
            if xids.search_count(
                [("module", "=", XID_MODULE), ("name", "=", self._xid_name(line.sl))]
            ):
                reasons.append("SL %s already taken on (external id exists)" % line.sl)
            if line.cost <= 0:
                reasons.append("cost must be above zero")
            if line.accum_depreciation < 0 or line.accum_depreciation > line.cost + 0.005:
                reasons.append("accumulated depreciation outside [0, cost]")
            if abs(line.cost - line.accum_depreciation - line.source_nbv) > 0.005:
                reasons.append("cost - accumulated != NBV in source")
            if not line.acquisition_date:
                reasons.append("missing/invalid acquisition date")
            elif self.takeon_date and line.acquisition_date > month_end(self.takeon_date):
                reasons.append("acquisition after the take-on month")
            cat_code = walk.get(line.legacy_coa_code) or walk.get(line.legacy_head)
            category = (
                Category.search(
                    [("code", "=", cat_code), ("company_id", "=", self.company_id.id)], limit=1
                )
                if cat_code
                else Category
            )
            if not category:
                reasons.append(
                    "no category for code/head %r (crosswalk -> %s)"
                    % (line.legacy_coa_code or line.legacy_head, cat_code or "?")
                )
            branch = self._resolve_branch(line.branch_label)
            if not branch:
                reasons.append("branch %r unresolved" % line.branch_label)
            elif not branch.operating_unit_id:
                reasons.append("branch %s has no operating unit" % branch.name)
            life = line.life_months or (category.useful_life_months if category else 0)
            if life <= 0:
                reasons.append("useful life (months) must be set")
            if reasons:
                line.write({"state": "quarantined", "reject_reason": "; ".join(reasons)})
                quarantined += 1
            else:
                line.write(
                    {
                        "state": "ready",
                        "reject_reason": False,
                        "category_id": category.id,
                        "branch_id": branch.id,
                        "operating_unit_id": branch.operating_unit_id.id,
                        "life_months": life,
                        "legacy_reference": "%s-SL-%s" % (self.import_ref, line.sl),
                    }
                )
                ready += 1
        self.write({"state": "validated"})
        self._log("Validated: %s ready, %s quarantined." % (ready, quarantined))
        return True

    def action_post(self):
        """Post the two take-on entries, capitalise and activate every ready
        row, carry the opening accumulated depreciation into the register."""
        self.ensure_one()
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import require_takeon_authority

        require_takeon_authority(self.env, "Posting an asset take-on")
        if self.state != "validated":
            raise UserError(self.env._("Validate the take-on before posting."))
        ready = self.line_ids.filtered(lambda ln: ln.state == "ready")
        if not ready:
            raise UserError(self.env._("Nothing ready to post."))
        if not self.contra_operating_unit_id:
            raise UserError(self.env._("Set the contra line's branch (Contra Line Branch) first."))
        assert_period_open(self.env, self.company_id, self.takeon_date, self.name)
        for cat in ready.mapped("category_id"):
            if not (cat.journal_id and cat.asset_account_id and cat.accumulated_account_id):
                raise UserError(
                    self.env._(
                        "Category %s is not wired (journal, asset and accumulated accounts): "
                        "configure it before the take-on posts.",
                        cat.code,
                    )
                )
        journal = self._ensure_mig_journal()
        contra = self._ensure_contra()
        company = self.company_id
        total_cost = money(sum(ready.mapped("cost")))
        total_accum = money(sum(ready.mapped("accum_depreciation")))

        # 1. acquisition: one debit per asset on its category's asset account
        entry = [
            (
                ln.category_id.asset_account_id,
                ln.cost,
                0.0,
                "SL-%s %s %s" % (ln.sl, ln.voucher, ln.product_name[:40]),
                ln.operating_unit_id,
            )
            for ln in ready
        ]
        entry.append(
            (
                contra,
                0.0,
                total_cost,
                "%s asset cost" % self.import_ref,
                self.contra_operating_unit_id,
            )
        )
        move_cost = post_entry(
            self.env,
            company,
            journal,
            self.takeon_date,
            "%s-ASSET-TAKEON" % self.import_ref,
            entry,
        )
        debit_by_label = {line.name: line for line in move_cost.line_ids if line.debit > 0}

        # 2. opening accumulated depreciation: one credit per asset
        entry = [
            (
                contra,
                total_accum,
                0.0,
                "%s opening accum" % self.import_ref,
                self.contra_operating_unit_id,
            )
        ]
        for ln in ready:
            if ln.accum_depreciation > 0:
                entry.append(
                    (
                        ln.category_id.accumulated_account_id,
                        0.0,
                        ln.accum_depreciation,
                        "SL-%s %s opening accum" % (ln.sl, ln.voucher),
                        ln.operating_unit_id,
                    )
                )
        move_accum = (
            post_entry(
                self.env,
                company,
                journal,
                self.takeon_date,
                "%s-ASSET-ACCUM" % self.import_ref,
                entry,
            )
            if total_accum > 0
            else self.env["account.move"]
        )

        # 3. seams + draft assets + activation (BRU-FXA-01)
        Seam = self.env["fix.fixed.asset.seam"].sudo()
        Asset = self.env["fix.fixed.asset"]
        period = month_start(self.takeon_date)
        for ln in ready:
            label = "SL-%s %s %s" % (ln.sl, ln.voucher, ln.product_name[:40])
            move_line = debit_by_label.get(label)
            if not move_line:
                raise UserError(self.env._("The acquisition entry lost the line of SL %s.", ln.sl))
            seam = Seam.create(
                {
                    "company_id": company.id,
                    "operating_unit_id": ln.operating_unit_id.id,
                    "name": "%s SL-%s" % (self.import_ref, ln.sl),
                    "move_line_id": move_line.id,
                    "currency_id": company.currency_id.id,
                    "amount": ln.cost,
                    "asset_category": ln.category_id.code,
                }
            )
            asset = Asset.create(
                {
                    "company_id": company.id,
                    "name": ln.product_name,
                    "category_id": ln.category_id.id,
                    "operating_unit_id": ln.operating_unit_id.id,
                    "custodian_id": ln.custodian_id.id or False,
                    "gross": ln.cost,
                    "salvage": ln.salvage,
                    "life_months": ln.life_months,
                    "purchase_date": ln.acquisition_date,
                    "depreciation_start": period,
                    "seam_id": seam.id,
                    "legacy_reference": ln.legacy_reference,
                    "takeon_batch_id": self.id,
                }
            )
            asset.action_activate()
            self.env["ir.model.data"].sudo().create(
                {
                    "module": XID_MODULE,
                    "name": self._xid_name(ln.sl),
                    "model": "fix.fixed.asset",
                    "res_id": asset.id,
                    "noupdate": True,
                }
            )
            ln.write({"state": "posted", "asset_id": asset.id, "seam_id": seam.id})

        # 4. opening depreciation runs: posted lines whose GL entry 2 carries
        Run = self.env["fix.asset.depreciation.run"]
        Line = self.env["fix.asset.depreciation.line"].sudo()
        runs = self.env["fix.asset.depreciation.run"]
        charged = ready.filtered(lambda ln: ln.accum_depreciation > 0)
        for book in ("book", "tax"):
            run = Run.create(
                {
                    "company_id": company.id,
                    "book": book,
                    "period_start": period,
                }
            )
            Line.create(
                [
                    {
                        "run_id": run.id,
                        "asset_id": ln.asset_id.id,
                        "book": book,
                        "period_start": period,
                        "amount": ln.accum_depreciation,
                    }
                    for ln in charged
                ]
            )
            run._guarded().write(
                {
                    "state": "posted",
                    "move_ids": [(6, 0, move_accum.ids)],
                    "note": self.env._(
                        "Opening accumulated depreciation of take-on %s: the GL is carried "
                        "by entry %s — no second posting. The next monthly run charges the "
                        "remaining life.",
                        self.import_ref,
                        move_accum.name or "(no accum)",
                    ),
                }
            )
            runs |= run
        self.write(
            {
                "state": "posted",
                "move_ids": [(6, 0, (move_cost | move_accum).ids)],
                "run_ids": [(6, 0, runs.ids)],
            }
        )
        self._log(
            "Posted %s asset(s): cost %s, accum %s, NBV %s on %s (entries %s)."
            % (
                len(ready),
                total_cost,
                total_accum,
                money(total_cost - total_accum),
                self.takeon_date,
                ", ".join((move_cost | move_accum).mapped("name")),
            )
        )
        return True

    def action_rollback(self):
        """Mirror both entries, retire the opening runs, reverse activation
        and remove the draft assets and seams (MIG-07: rehearsed)."""
        self.ensure_one()
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import require_takeon_authority

        require_takeon_authority(self.env, "Rolling back an asset take-on")
        if self.state != "posted":
            raise UserError(self.env._("Only a posted take-on can be rolled back."))
        posted = self.line_ids.filtered(lambda ln: ln.state == "posted")
        journal = self._ensure_mig_journal()
        contra = self._ensure_contra()
        company = self.company_id
        assert_period_open(self.env, company, self.takeon_date, "Rollback %s" % self.name)
        total_cost = money(sum(posted.mapped("cost")))
        total_accum = money(sum(posted.mapped("accum_depreciation")))
        # mirrors: swap debit/credit, same accounts, branches and labels
        entry = [
            (
                ln.category_id.asset_account_id,
                0.0,
                ln.cost,
                "ROLLBACK SL-%s %s" % (ln.sl, ln.voucher),
                ln.operating_unit_id,
            )
            for ln in posted
        ]
        entry.append(
            (
                contra,
                total_cost,
                0.0,
                "ROLLBACK %s asset cost" % self.import_ref,
                self.contra_operating_unit_id,
            )
        )
        mirror_cost = post_entry(
            self.env,
            company,
            journal,
            self.takeon_date,
            "ROLLBACK %s-ASSET-TAKEON" % self.import_ref,
            entry,
        )
        mirrors = mirror_cost
        if total_accum > 0:
            entry = [
                (
                    contra,
                    0.0,
                    total_accum,
                    "ROLLBACK %s opening accum" % self.import_ref,
                    self.contra_operating_unit_id,
                )
            ]
            for ln in posted:
                if ln.accum_depreciation > 0:
                    entry.append(
                        (
                            ln.category_id.accumulated_account_id,
                            ln.accum_depreciation,
                            0.0,
                            "ROLLBACK SL-%s opening accum" % ln.sl,
                            ln.operating_unit_id,
                        )
                    )
            mirrors |= post_entry(
                self.env,
                company,
                journal,
                self.takeon_date,
                "ROLLBACK %s-ASSET-ACCUM" % self.import_ref,
                entry,
            )
        # opening runs: back to draft (guarded), lines then runs removable
        for run in self.run_ids:
            run._guarded().write({"state": "draft"})
            run.line_ids.sudo().unlink()
            run.sudo().unlink()
        # assets: reverse activation, then delete the drafts
        for ln in posted:
            asset = ln.asset_id
            if asset:
                asset._guarded().write(
                    {"state": "draft", "seam_id": False, "acquisition_move_id": False}
                )
                asset.sudo().unlink()
            if ln.seam_id:
                ln.seam_id.sudo().unlink()
            self.env["ir.model.data"].sudo().search(
                [("module", "=", XID_MODULE), ("name", "=", self._xid_name(ln.sl))]
            ).unlink()
            ln.write({"state": "ready", "asset_id": False, "seam_id": False})
        self.write({"state": "rolled_back", "move_ids": [(6, 0, mirrors.ids)]})
        self._log(
            "Rolled back: mirror entries %s; assets, seams and opening runs removed."
            % ", ".join(mirrors.mapped("name"))
        )
        return True


class FixAssetTakeonLine(models.Model):
    _name = "fix.asset.takeon.line"
    _description = "Fixed Asset Take-on Line"
    _order = "batch_id desc, sl"

    batch_id = fields.Many2one(
        "fix.asset.takeon.batch", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="batch_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="batch_id.currency_id")
    sl = fields.Integer(string="SL (legacy serial)", index=True)
    legacy_coa_code = fields.Char(string="Legacy COA Code")
    legacy_head = fields.Char(string="Legacy COA Head")
    product_name = fields.Char(string="Product / Asset")
    acquisition_date = fields.Date(string="Acquisition Date")
    fy_label = fields.Char(string="Financial Year (source)")
    branch_label = fields.Char(string="Cost Centre / Branch (source)")
    cost = fields.Monetary(string="Cost")
    accum_depreciation = fields.Monetary(string="Accumulated Depreciation")
    source_nbv = fields.Monetary(string="NBV (source)")
    nbv = fields.Monetary(string="NBV (cost - accum)", compute="_compute_nbv", store=True)
    dep_fraction = fields.Float(string="Depreciation Fraction (source)")
    voucher = fields.Char(string="Voucher / Move No")
    category_id = fields.Many2one("fix.asset.category", string="Resolved Category")
    branch_id = fields.Many2one("fix.branch", string="Resolved Branch")
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    custodian_id = fields.Many2one("hr.employee", string="Custodian")
    life_months = fields.Integer(
        string="Useful Life (months, remaining + 1)",
        help="The opening take-on line counts as one posted month: set remaining life + 1.",
    )
    salvage = fields.Monetary(string="Salvage Value")
    state = fields.Selection(
        [
            ("staged", "Staged"),
            ("quarantined", "Quarantined"),
            ("ready", "Ready"),
            ("posted", "Posted"),
            ("error", "Error"),
        ],
        default="staged",
        required=True,
        index=True,
    )
    reject_reason = fields.Char(string="Quarantine Reason")
    asset_id = fields.Many2one("fix.fixed.asset", string="Asset", readonly=True, copy=False)
    seam_id = fields.Many2one(
        "fix.fixed.asset.seam", string="Capitalisation Seam", readonly=True, copy=False
    )
    legacy_reference = fields.Char(string="Legacy Reference (MIG-03)", readonly=True, copy=False)

    @api.depends("cost", "accum_depreciation")
    def _compute_nbv(self):
        for rec in self:
            rec.nbv = money(rec.cost - rec.accum_depreciation)
