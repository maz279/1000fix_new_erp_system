# Legacy bank-ledger take-on wizard (2026-11-09 AB Bank capability report
# R2 Option B / R3 — the guided cut-over path for bank ledger exports).
#
# The "Ledger Statement" spreadsheets exported from the production Odoo
# (abbank folder: Date / Journal Entry / Branch / Company / Created by /
# Created on / Debit / Credit / Balance, titled
# "Ledger Statement: <GL code> <account name>") are BOOK HISTORY, never bank
# evidence: they must not enter fix.bank.statement.* (hardened against
# hand-made lines by design). The doctrine this wizard implements — the same
# one the 69-entry LEGACY-AB load exercised on 2026-11-09 — is row-level
# history: every source row posts as its OWN dated two-line entry (bank GL
# <-> take-on contra) through the governed M19 funnel, carrying the branch
# dimension and the full source provenance (move name in the ref; reference,
# source branch, creator, created-on and file in the narration; audit fields
# are never fabricated). Zero-amount rows are quarantined under a named
# decision (report D2), rows whose ref already exists are skipped (a re-run
# cannot double-post), and rollback is ONE combined mirror entry that keeps
# every branch dimension.
import base64
import datetime
import io
import json
import logging
import re

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

from .fix_gl_ext import require_takeon_authority

_logger = logging.getLogger(__name__)

_TITLE_RE = re.compile(r"^\s*Ledger Statement:\s*(\S+)\s*(.*)$", re.I)
_MOVE_RE = re.compile(r"^(.+?)\s*(?:\((.*)\))?\s*$")

LINE_STATES = [
    ("staged", "Staged (raw)"),
    ("linked", "Branch resolved"),
    ("quarantined", "Quarantined (not posted)"),
    ("posted", "Posted"),
    ("error", "Error"),
]


def _norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip()).casefold()


# Branch label crosswalk — the alias map maintained by the legacy control
# lane (fix_legacy_ledger.LEGACY_BRANCH_ALIASES) is the estate's canonical
# crosswalk; a local copy keeps this wizard self-contained if that lane is
# refactored away.
try:  # pragma: no cover - import shape depends on load order
    from .fix_legacy_ledger import LEGACY_BRANCH_ALIASES as _ALIASES
except Exception:  # ImportError and any reshape of that module
    _ALIASES = {
        "1000Fix Services Ltd.": "1000 FiX Head Office",
        "Head Office Customer Care": "1000 FiX Head Office",
        "Corporate Service Branch": "Corporate Service Center",
        "Sony-Smart Service Operation": "Sony Smart Service Operation",
        "LG Operation": "LG Service Operation",
        "Other Home Appliances Services": "Other Home Appliance Service Center",
    }


class FixBankTakeonBatch(models.Model):
    _name = "fix.bank.takeon.batch"
    _description = "Legacy Bank-Ledger Take-on"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(
        required=True,
        tracking=True,
        default=lambda self: _("Legacy bank ledger %s") % fields.Date.context_today(self),
    )
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    import_ref = fields.Char(
        required=True,
        default=lambda self: "LEGBANK-%s" % fields.Date.context_today(self).strftime("%Y-%m"),
        help="Prefix logged on every posting-log row this batch writes.",
    )
    source_file = fields.Binary(string="Bank Ledger Spreadsheet", attachment=True)
    source_filename = fields.Char()
    bank_gl_code = fields.Char(
        string="Bank GL Code",
        copy=False,
        help="Captured from the export title ('Ledger Statement: <code> …'); "
        "set manually when the export carries no title.",
    )
    bank_gl_name = fields.Char(string="Bank GL (legacy name)", copy=False)
    bank_gl_account_id = fields.Many2one(
        "account.account",
        string="Bank GL (resolved)",
        readonly=True,
        copy=False,
        domain=[("account_type", "in", ("asset_cash", "asset_current"))],
    )
    contra_account_id = fields.Many2one(
        "account.account",
        string="Take-on Contra Account",
        domain=[("account_type", "=", "liability_current")],
        help="Carries the mirrored side of every history row (the tier-1 take-on "
        "contra; reclassifies to opening equity once all subledgers are on).",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("staged", "Staged"),
            ("validated", "Validated"),
            ("posted", "History Posted"),
            ("rolled_back", "Rolled Back"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.bank.takeon.line", "batch_id")
    line_count = fields.Integer(compute="_compute_counts", store=True)
    linked_count = fields.Integer(compute="_compute_counts", store=True)
    quarantined_count = fields.Integer(compute="_compute_counts", store=True)
    posted_count = fields.Integer(compute="_compute_counts", store=True, string="Posted Rows")
    branch_count = fields.Integer(compute="_compute_counts", store=True, string="Distinct Branches")
    total_debit = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    total_credit = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    total_net = fields.Monetary(compute="_compute_totals", store=True, currency_field="currency_id")
    date_from = fields.Date(compute="_compute_totals", store=True)
    date_to = fields.Date(compute="_compute_totals", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    decision_log = fields.Text(readonly=True, copy=False)

    # --------------------------------------------------------- helpers
    def _log(self, msg):
        self.ensure_one()
        stamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.message_post(body="[%s] %s" % (stamp, msg))
        self.decision_log = "%s\n[%s] %s" % (self.decision_log or "", stamp, msg)

    def _ensure_contra_account(self):
        self.ensure_one()
        from .fix_gl_ext import ensure_legacy_account

        return ensure_legacy_account(
            self.env,
            self.company_id,
            "Legacy Ledger Take-on Contra",
            "2.99.99.901",
            "liability_current",
        )

    # --------------------------------------------------------- actions
    def action_stage(self):
        """Parse the export: title row names the target GL, header row is
        detected (the export carries title + record-count preamble), one
        staged line per data row, trailing Total row skipped."""
        self.ensure_one()
        if self.state not in ("draft", "staged"):
            raise UserError(_("Only a draft or staged take-on can be staged."))
        if not self.source_file:
            raise UserError(_("Upload the bank ledger spreadsheet first."))
        try:
            import openpyxl
        except ImportError:
            raise UserError(_("openpyxl is not available on this server.")) from None
        workbook = openpyxl.load_workbook(
            io.BytesIO(base64.b64decode(self.source_file)), read_only=True, data_only=True
        )
        sheet = workbook.worksheets[0]
        rows = list(sheet.iter_rows(values_only=True))
        workbook.close()

        header_idx = None
        for idx, row in enumerate(rows[:10]):
            cells = [str(c or "").strip() for c in (row or [])]
            if len(cells) >= 9 and cells[0] == "Date" and "Debit" in cells and "Credit" in cells:
                header_idx = idx
                break
        if header_idx is None:
            raise UserError(
                _(
                    "No header row found (expected Date / Journal Entry / Branch / "
                    "… / Debit / Credit / Balance within the first 10 rows)."
                )
            )

        title = ""
        for row in rows[:header_idx]:
            text = str((row or [""])[0] or "")
            if text.strip().lower().startswith("ledger statement"):
                title = text
                break
        m = _TITLE_RE.match(title)
        if m:
            self.bank_gl_code = m.group(1)[:20]
            self.bank_gl_name = m.group(2)[:120]
        elif not self.bank_gl_code:
            raise UserError(
                _(
                    "No 'Ledger Statement: <GL code>' title row found — set the "
                    "Bank GL Code manually before staging."
                )
            )

        Line = self.env["fix.bank.takeon.line"]
        Line.search([("batch_id", "=", self.id)]).unlink()
        n = 0
        for row in rows[header_idx + 1 :]:
            cells = list((row or [])[:9])
            if not any(c is not None for c in cells):
                continue
            first = str(cells[0] or "").strip()
            if not first or first.lower().startswith("total"):
                continue
            (
                raw_date,
                journal_entry,
                branch_raw,
                _company_raw,
                created_by,
                created_on,
                debit,
                credit,
                balance,
            ) = cells
            try:
                debit = float(debit or 0.0)
                credit = float(credit or 0.0)
                balance = float(balance or 0.0)
            except (TypeError, ValueError):
                raise UserError(
                    _("Row %d: debit/credit/balance are not numbers.") % (header_idx + 2 + n)
                ) from None
            entry_date = None
            if isinstance(raw_date, datetime.datetime):
                entry_date = raw_date.date()
            elif isinstance(raw_date, datetime.date):
                entry_date = raw_date
            elif raw_date:
                try:
                    entry_date = datetime.date.fromisoformat(str(raw_date)[:10])
                except ValueError:
                    entry_date = None
            created_on_dt = False
            if isinstance(created_on, datetime.datetime):
                created_on_dt = created_on
            elif created_on:
                try:
                    created_on_dt = datetime.datetime.strptime(
                        str(created_on)[:19], "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError:
                    created_on_dt = False
            Line.create(
                {
                    "batch_id": self.id,
                    "row_no": n + 1,
                    "entry_date": entry_date,
                    "journal_entry": str(journal_entry or "")[:180],
                    "branch_raw": str(branch_raw or "").strip()[:120],
                    "created_by_name": str(created_by or "").strip()[:80],
                    "created_on": created_on_dt,
                    "debit": debit,
                    "credit": credit,
                    "balance": balance,
                    "line_state": "staged",
                }
            )
            n += 1
        if not n:
            raise UserError(_("No data rows found below the header."))
        self.state = "staged"
        self._log(
            "staged %d rows from %s (bank GL %s)"
            % (n, self.source_filename or "spreadsheet", self.bank_gl_code)
        )
        return True

    def action_validate(self):
        """Re-prove each row's arithmetic, resolve branches through the
        crosswalk, quarantine zero-amount rows under the named decision,
        resolve the target GL. Nothing posts silently."""
        self.ensure_one()
        if self.state != "staged":
            raise UserError(_("Stage the spreadsheet first."))
        Branch = self.env["fix.branch"].sudo().with_context(active_test=False)
        by_name = {}
        for b in Branch.search([]):
            by_name[_norm(b.name)] = b
        by_legacy = {}
        for b in Branch.search([("legacy_reference", "!=", False)]):
            by_legacy.setdefault(_norm(b.legacy_reference), b)
        estate_cw = {}
        raw_cw = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cd_gl_ext.legacy_ledger.branch_crosswalk")
        )
        if raw_cw:
            try:
                estate_cw = {str(k).strip(): str(v).strip() for k, v in json.loads(raw_cw).items()}
            except ValueError:
                estate_cw = {}
        bad_arith = bad_branch = bad_date = zero_rows = 0
        for line in self.line_ids:
            notes = []
            if abs(line.debit - line.credit - line.balance) > 0.005:
                bad_arith += 1
                notes.append("Debit - Credit != Balance")
            if not line.entry_date:
                bad_date += 1
                notes.append("missing/invalid date")
            raw = (line.branch_raw or "").strip()
            branch = by_name.get(_norm(raw)) or by_legacy.get(_norm(raw))
            if not branch:
                alias = _ALIASES.get(raw)
                branch = by_name.get(_norm(alias)) if alias else None
            if not branch:
                # Final leg — the estate crosswalk parameter the legacy
                # control lane reads (cd_gl_ext.legacy_ledger.branch_crosswalk):
                # the real branch master consolidates legacy brand labels onto
                # physical service centres a single alias cannot express.
                target = estate_cw.get(raw)
                if target:
                    branch = by_name.get(_norm(target)) or by_legacy.get(_norm(target))
            if branch:
                line.branch_resolved_id = branch.id
                line.line_state = "linked"
            else:
                bad_branch += 1
                notes.append("branch label unresolved")
                line.branch_resolved_id = False
                line.line_state = "quarantined"
            if line.line_state == "linked" and abs(line.balance) < 0.005:
                zero_rows += 1
                notes.append("zero-amount row — not posted (decision D2)")
                line.line_state = "quarantined"
            line.notes = "; ".join(notes)
            if notes and line.line_state != "quarantined":
                line.line_state = "quarantined"
        if not self.bank_gl_code:
            raise UserError(_("No Bank GL Code set."))
        account = (
            self.env["account.account"]
            .with_company(self.company_id)
            .search([("code", "=", self.bank_gl_code)], limit=1)
        )
        if not account:
            raise UserError(
                _("Bank GL %s does not exist on the posting chart.") % self.bank_gl_code
            )
        self.bank_gl_account_id = account.id
        self.state = "validated"
        self._log(
            "validated %d rows: %d branch-resolved, %d quarantined (arithmetic "
            "%d, branch %d, date %d, zero-amount %d); target GL %s"
            % (
                len(self.line_ids),
                len(self.line_ids) - bad_branch - zero_rows,
                bad_branch + zero_rows,
                bad_arith,
                bad_branch,
                bad_date,
                zero_rows,
                account.code or self.bank_gl_code,
            )
        )
        return True

    def action_post(self):
        """Row-level history: every resolved row posts as its OWN dated
        two-line entry (bank GL <-> contra) through the M19 funnel with the
        branch + operating-unit dimension and full provenance. Idempotent:
        a row whose ref already exists on a posted entry is skipped."""
        self.ensure_one()
        require_takeon_authority(self.env, "Posting a legacy take-on")
        if self.state != "validated":
            raise UserError(_("Validate the batch first."))
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = self.company_id
        gl = self.bank_gl_account_id
        if not gl:
            raise UserError(_("No resolved bank GL — validate first."))
        contra = self.contra_account_id or self._ensure_contra_account()
        self.contra_account_id = contra.id
        mig = self.env["account.journal"].search(
            [("code", "=", "MIG"), ("company_id", "=", company.id)], limit=1
        )
        if not mig:
            mig = self.env["account.journal"].create(
                {
                    "name": "Legacy Take-on",
                    "code": "MIG",
                    "type": "general",
                    "company_id": company.id,
                }
            )
        Move = self.env["account.move"].sudo()
        posted, skipped = [], []
        for line in self.line_ids.filtered(lambda ln: ln.line_state == "linked"):
            m = _MOVE_RE.match(line.journal_entry or "")
            move_name = (m.group(1) if m else "").strip() or ("row %d" % line.row_no)
            paren = (m.group(2) if m else "") or ""
            ref = "LEGACY %s" % move_name
            # scheme-agnostic + GL-scoped guard: the first AB load (2026-11-09
            # script) used "LEGACY-AB <move>", this wizard writes "LEGACY <move>"
            # — a source row is its history either way, so match on the move
            # name itself. But a legacy move that touched TWO bank GLs (an
            # inter-bank transfer appears in both accounts' exports under the
            # same move name) is a different economic leg per GL: only a posted
            # move carrying a line on THIS batch's bank GL makes the row a
            # duplicate. (SCB lane, 2026-11-10.)
            dup_domain = [
                ("state", "=", "posted"),
                ("line_ids.account_id", "=", gl.id),
            ]
            if Move.search_count([*dup_domain, ("ref", "=", ref)]) or (
                move_name
                and not move_name.startswith("row ")
                and Move.search_count([*dup_domain, ("ref", "like", "%" + move_name)])
            ):
                skipped.append(move_name)
                line.line_state = "posted"
                continue
            branch = line.branch_resolved_id
            dims = {
                0: {"branch_id": branch.id, "operating_unit_id": branch.operating_unit_id.id},
                1: {"branch_id": branch.id, "operating_unit_id": branch.operating_unit_id.id},
            }
            narration = "%s | src branch: %s | by %s%s | file: %s" % (
                paren or "(no ref)",
                line.branch_raw or "",
                line.created_by_name or "",
                (" @ " + line.created_on.strftime("%Y-%m-%d %H:%M:%S")) if line.created_on else "",
                self.source_filename or "",
            )
            amount = line.balance
            move, _d = post_with_dimensions(
                self.env,
                {
                    "journal_id": mig.id,
                    "company_id": company.id,
                    "date": line.entry_date or fields.Date.context_today(self),
                    "move_type": "entry",
                    "ref": ref,
                    "narration": narration[:400],
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "account_id": gl.id,
                                "name": ref,
                                "debit": amount if amount > 0 else 0.0,
                                "credit": -amount if amount < 0 else 0.0,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "account_id": contra.id,
                                "name": "Legacy bank take-on contra",
                                "debit": -amount if amount < 0 else 0.0,
                                "credit": amount if amount > 0 else 0.0,
                            },
                        ),
                    ],
                },
                dims,
                source="suspense",
                source_ref="%s bank history take-on" % self.import_ref,
            )
            posted.append(move)
            line.line_state = "posted"
        if not posted and not skipped:
            raise UserError(_("No postable rows (all quarantined or zero)."))
        if posted and self.source_file and self.source_filename:
            anchor = posted[0]
            if (
                not self.env["ir.attachment"]
                .sudo()
                .search_count(
                    [
                        ("res_model", "=", "account.move"),
                        ("res_id", "=", anchor.id),
                        ("name", "=", self.source_filename),
                    ]
                )
            ):
                self.env["ir.attachment"].sudo().create(
                    {
                        "name": self.source_filename,
                        "datas": self.source_file,
                        "res_model": "account.move",
                        "res_id": anchor.id,
                        "company_id": company.id,
                    }
                )
        quarantined = self.line_ids.filtered(lambda ln: ln.line_state == "quarantined")
        self.state = "posted"
        self._log(
            "posted %d row entries on GL %s (%d skipped as already posted); %d "
            "quarantined rows excluded, their net %.2f stays unposted; evidence "
            "file attached to %s"
            % (
                len(posted),
                gl.code or self.bank_gl_code,
                len(skipped),
                len(quarantined),
                sum(quarantined.mapped("balance")),
                posted[0].name if posted else "-",
            )
        )
        return True

    def action_rollback(self):
        """ONE combined mirror entry reversing everything this batch posted
        (identified through the immutable posting log), each mirrored line
        keeping its branch dimension. The staged rows stay — they are the
        evidence; only the ledger position rolls back."""
        self.ensure_one()
        require_takeon_authority(self.env, "Rolling back a legacy take-on")
        if self.state != "posted":
            raise UserError(_("Only a posted take-on can be rolled back."))
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        logs = (
            self.env["fix.journal.posting.log"]
            .sudo()
            .search([("source_ref", "=", "%s bank history take-on" % self.import_ref)])
        )
        moves = logs.mapped("move_id").filtered(lambda mv: mv.state == "posted")
        if not moves:
            raise UserError(_("No posted entries found for this batch."))
        dim_rows = (
            self.env["fix.journal.dimension"]
            .sudo()
            .search([("move_line_id", "in", moves.line_ids.ids)])
        )
        branch_by_line = {d.move_line_id.id: d for d in dim_rows}
        mirror, dims = [], {}
        for line in moves.line_ids:
            if abs(line.balance) < 0.005:
                continue
            mirror.append(
                (
                    0,
                    0,
                    {
                        "account_id": line.account_id.id,
                        "name": "Bank take-on rollback: %s" % (line.name or "")[:48],
                        "debit": -line.balance if line.balance < 0 else 0.0,
                        "credit": line.balance if line.balance > 0 else 0.0,
                    },
                )
            )
            dim = branch_by_line.get(line.id)
            if dim:
                dims[len(mirror) - 1] = {
                    "branch_id": dim.branch_id.id,
                    "operating_unit_id": dim.operating_unit_id.id,
                }
        reversal, _d = post_with_dimensions(
            self.env,
            {
                "journal_id": moves[:1].journal_id.id,
                "company_id": self.company_id.id,
                "date": fields.Date.context_today(self),
                "move_type": "entry",
                "ref": "ROLLBACK %s bank history" % self.import_ref,
                "narration": _("Rollback of legacy bank take-on %s (%d entries).")
                % (self.import_ref, len(moves)),
                "line_ids": mirror,
            },
            dims,
            source="suspense",
            source_ref="%s bank rollback" % self.import_ref,
        )
        self.line_ids.filtered(lambda ln: ln.line_state == "posted").write({"line_state": "linked"})
        self.state = "rolled_back"
        self._log("rolled back via combined mirror %s (staged rows retained)" % reversal.name)
        return True

    @api.depends("line_ids", "line_ids.line_state")
    def _compute_counts(self):
        for batch in self:
            lines = batch.line_ids
            batch.line_count = len(lines)
            batch.linked_count = len(lines.filtered(lambda ln: ln.line_state == "linked"))
            batch.quarantined_count = len(lines.filtered(lambda ln: ln.line_state == "quarantined"))
            batch.posted_count = len(lines.filtered(lambda ln: ln.line_state == "posted"))
            batch.branch_count = len(
                lines.filtered(lambda ln: ln.branch_resolved_id).mapped("branch_resolved_id")
            )

    @api.depends("line_ids.debit", "line_ids.credit", "line_ids.balance", "line_ids.entry_date")
    def _compute_totals(self):
        for batch in self:
            lines = batch.line_ids
            batch.total_debit = sum(lines.mapped("debit"))
            batch.total_credit = sum(lines.mapped("credit"))
            batch.total_net = sum(lines.mapped("balance"))
            dates = [d for d in lines.mapped("entry_date") if d]
            batch.date_from = min(dates) if dates else False
            batch.date_to = max(dates) if dates else False


class FixBankTakeonLine(models.Model):
    _name = "fix.bank.takeon.line"
    _description = "Legacy Bank-Ledger Take-on Line"
    _order = "batch_id, row_no"

    batch_id = fields.Many2one("fix.bank.takeon.batch", required=True, ondelete="cascade")
    row_no = fields.Integer()
    entry_date = fields.Date(string="Date")
    journal_entry = fields.Char(string="Journal Entry (legacy)")
    branch_raw = fields.Char(string="Branch (legacy label)")
    branch_resolved_id = fields.Many2one("fix.branch", string="Branch (resolved)")
    created_by_name = fields.Char(string="Created By (legacy)")
    created_on = fields.Datetime(string="Created On (legacy)")
    debit = fields.Monetary(currency_field="currency_id")
    credit = fields.Monetary(currency_field="currency_id")
    balance = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(related="batch_id.currency_id")
    line_state = fields.Selection(LINE_STATES, default="staged")
    notes = fields.Char()
