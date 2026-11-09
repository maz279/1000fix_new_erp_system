# Legacy AP ledger take-on wizard (2026-11-09 accounts_payable report §5.4).
#
# The 200101 Account Payable export is a voucher-level open-items register
# (Date / Journal Entry / Branch / Company / Created by / Created on /
# Debit / Credit / Balance) with NO party column: the legacy register lists
# payables as positive debits and every row's Balance equals its own open
# amount. That file cannot become 297 subledger bills (no vendor, and the
# three-way-match subledger must not carry fabricated approvals) — it is
# taken on at GL control-account level through the SAME governed M19 funnel
# the partner-ledger wizard uses:
#
#   stage the register -> validate (arithmetic identity, duplicates,
#   zero-value quarantine, branch crosswalk) -> post ONE voucher-level
#   control entry (one credit line per open voucher on a DEDICATED
#   non-reconcileable legacy control account under the source code, the
#   resolved branch + operating unit dimensioned on every line, net on the
#   take-on contra account) -> rollback (mirror entry) if Finance rejects.
#
# Legacy sign convention: the register's debits ARE payables, so they post
# as CREDITS on the credit-normal control account (report §2.4). Every row
# keeps its legacy identity (voucher ref, dates, creator, branch label)
# verbatim plus a unique legacy_reference key (MIG-03) so the load is
# idempotent and re-runnable.
import base64
import io
import logging
import re

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?")
_PAREN = re.compile(r"^\s*(.+?)\s*\(([^()]*)\)\s*$")

LINE_STATES = [
    ("staged", "Staged (raw)"),
    ("quarantined", "Quarantined (not posted)"),
    ("ready", "Validated — ready to post"),
    ("posted", "Posted to the AP control account"),
    ("error", "Error"),
]


def _to_float(raw):
    if raw is None:
        return 0.0
    try:
        return float(str(raw).replace(",", "").strip() or 0.0)
    except (TypeError, ValueError):
        return None


def _to_date(raw):
    text = str(raw or "").strip()[:10]
    if not _DATE.match(text):
        return False
    return fields.Date.to_date(text)


def _to_datetime(raw):
    text = str(raw or "").strip()
    if not _DATETIME.match(text):
        return False
    try:
        return fields.Datetime.to_datetime(text.replace("T", " ")[:19])
    except ValueError:
        return False


class FixApTakeonBatch(models.Model):
    _name = "fix.ap.takeon.batch"
    _description = "Legacy AP Ledger Take-on"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    takeon_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        help="The cut-over date of the opening entry — a period boundary, "
        "agreed in the W0 reconciliation before anything loads on the "
        "real estate.",
    )
    source_file = fields.Binary(string="Legacy AP Register Spreadsheet", attachment=True)
    source_filename = fields.Char()
    import_ref = fields.Char(
        required=True,
        help="Control-total reference stamped on the entry and log, e.g. "
        "AP-2026-11. Row keys are the legacy voucher refs themselves.",
    )
    legacy_account_code = fields.Char(
        default="200101",
        required=True,
        help="The source ledger's control-account code (traceability only; "
        "posting goes to the resolved target AP control account below).",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("staged", "Staged"),
            ("validated", "Validated"),
            ("posted", "Opening Entry Posted"),
            ("rolled_back", "Rolled Back"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.ap.takeon.line", "batch_id")
    line_count = fields.Integer(compute="_compute_counts", store=True)
    ready_count = fields.Integer(compute="_compute_counts", store=True)
    quarantined_count = fields.Integer(compute="_compute_counts", store=True)
    posted_count = fields.Integer(compute="_compute_counts", store=True)
    total_open = fields.Monetary(
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
        help="Net open position of the non-quarantined rows (the amount the "
        "opening entry carries; credits are the legacy register's debits).",
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    control_account_id = fields.Many2one(
        "account.account",
        string="Posting Target Account",
        domain=[("account_type", "in", ["liability_current", "liability_payable"])],
        help="Default: the dedicated non-reconcileable 'Account Payable "
        "(Legacy 200101 Control)' archive account, mirroring the legacy AR "
        "lane — the register's vouchers are anonymous (no party), so they "
        "never touch the reconcileable payable control the partner take-on "
        "owns. Set the live AP control account here only on an estate where "
        "no partner take-on has posted (the fix_real path, report §5.4).",
    )
    contra_account_id = fields.Many2one(
        "account.account",
        string="Take-on Contra Account",
        domain=[("account_type", "=", "liability_current")],
        help="Carries the net legacy AP position until the remaining "
        "subledgers are taken on (report §5.4).",
    )
    posted_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    decision_log = fields.Text(readonly=True, copy=False)

    # --------------------------------------------------------- helpers
    def _log(self, msg):
        self.ensure_one()
        stamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.message_post(body="[%s] %s" % (stamp, msg))
        self.decision_log = "%s\n[%s] %s" % (self.decision_log or "", stamp, msg)

    def _ensure_control_account(self):
        """Dedicated non-reconcileable archive account under the legacy code
        (the AR lane's doctrine): liability_current so the anonymous
        voucher lines never trigger payable-control partner semantics and
        never double-count the partner-ledger take-on. Odoo 19 keeps the
        per-company code in code_store — account.account itself has no
        company_id."""
        self.ensure_one()
        Account = self.env["account.account"]
        code = self.legacy_account_code or "200101"
        existing = Account.search(
            [("code", "=", code), ("account_type", "=", "liability_current")], limit=1
        )
        if existing:
            return existing
        clash = Account.search([("code", "=", code)], limit=1)
        if clash:
            raise UserError(
                _(
                    "Account %s already exists as %s (%s). The AP register archive "
                    "posts to a dedicated liability_current account — pick the "
                    "posting target explicitly."
                )
                % (code, clash.name, clash.account_type)
            )
        try:
            return Account.create(
                {
                    "name": "Account Payable (Legacy 200101 Control)",
                    "code": code,
                    "account_type": "liability_current",
                    "reconcile": False,
                }
            )
        except Exception:
            try:
                return Account.create(
                    {
                        "name": "Account Payable (Legacy 200101 Control)",
                        "account_type": "liability_current",
                        "reconcile": False,
                        "code_store": {str(self.company_id.id): code},
                    }
                )
            except Exception:
                _logger.exception("legacy AP control account create failed")
                raise UserError(
                    _(
                        "Could not create the legacy AP control account %s. Create it "
                        "on the posting chart first, or pick an existing account."
                    )
                    % code
                ) from None

    def _ensure_contra_account(self):
        """The same tier-1 contra the partner-ledger and legacy-AR take-ons
        wash against, so all legacy lanes reconcile in one place."""
        self.ensure_one()
        Account = self.env["account.account"]
        existing = Account.search([("name", "=", "Legacy Ledger Take-on Contra")], limit=1)
        if existing:
            return existing
        try:
            return Account.create(
                {
                    "name": "Legacy Ledger Take-on Contra",
                    "code": "2-99-99-901",
                    "account_type": "liability_current",
                }
            )
        except Exception:
            return Account.create(
                {
                    "name": "Legacy Ledger Take-on Contra",
                    "account_type": "liability_current",
                    "code_store": {str(self.company_id.id): "2-99-99-901"},
                }
            )

    def _resolve_branch(self, label):
        """Crosswalk the register's Branch label to fix.branch: exact, then
        ilike. Returns (branch or empty record, matched: bool)."""
        Branch = self.env["fix.branch"]
        label = str(label or "").strip()
        if not label:
            return Branch, True
        branch = Branch.search([("name", "=ilike", label)], limit=1)
        if branch:
            return branch, True
        token = re.sub(r"[^0-9a-z]+", " ", label.casefold()).strip()
        first = token.split()[0] if token else ""
        if first:
            branch = Branch.search([("name", "ilike", first)], limit=1)
            if branch:
                return branch, True
        return Branch, False

    # --------------------------------------------------------- actions
    def action_stage(self):
        """Parse the register: header row detected by a literal 'Date' first
        cell; every cell is text (the legacy report writer exports strings);
        footer 'Total' rows are skipped by date-shape validation."""
        self.ensure_one()
        if self.state not in ("draft", "staged"):
            raise UserError(_("Only a draft or staged take-on can be staged."))
        if not self.source_file:
            raise UserError(_("Upload the legacy AP register spreadsheet first."))
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
        for idx, row in enumerate(rows):
            if str(row[0] or "").strip() == "Date":
                header_idx = idx
                break
        if header_idx is None:
            raise UserError(_("No header row found (first cell must be 'Date')."))
        Line = self.env["fix.ap.takeon.line"]
        Line.search([("batch_id", "=", self.id)]).unlink()
        n = 0
        skipped = 0
        for row in rows[header_idx + 1 :]:
            raw_date = str(row[0] or "").strip()
            if not raw_date:
                continue
            entry_date = _to_date(raw_date)
            if not entry_date:
                skipped += 1  # footer / total / note rows
                continue
            raw_ref = str(row[1] or "").strip()
            m = _PAREN.match(raw_ref)
            source_note = ""
            if m:
                raw_ref, source_note = m.group(1).strip(), m.group(2).strip()
            debit = _to_float(row[6]) if len(row) > 6 else None
            credit = _to_float(row[7]) if len(row) > 7 else None
            balance = _to_float(row[8]) if len(row) > 8 else None
            if debit is None or credit is None or balance is None:
                raise UserError(_("Voucher %s: debit/credit/balance are not numbers.") % raw_ref)
            Line.create(
                {
                    "batch_id": self.id,
                    "row_no": n + 1,
                    "legacy_ref": raw_ref,
                    "source_ref_note": source_note,
                    "legacy_date": entry_date,
                    "legacy_branch": str(row[2] or "").strip(),
                    "legacy_company": str(row[3] or "").strip(),
                    "legacy_created_by": str(row[4] or "").strip(),
                    "legacy_created_on": _to_datetime(row[5]) if len(row) > 5 else False,
                    "debit": debit,
                    "credit": credit,
                    "balance": balance,
                    "line_state": "staged",
                }
            )
            n += 1
        self.state = "staged"
        self._log(
            "staged %d open vouchers from %s (%d non-voucher rows skipped)"
            % (n, self.source_filename or "spreadsheet", skipped)
        )
        return True

    def action_validate(self):
        """Arithmetic identity, duplicate voucher refs, zero-value quarantine
        and the branch crosswalk — nothing posts yet."""
        self.ensure_one()
        if self.state != "staged":
            raise UserError(_("Stage the register first."))
        seen = {}
        bad_identity = dup = zero = 0
        branch_unmatched = 0
        for line in self.line_ids:
            if abs(line.debit - line.credit - line.balance) > 0.005:
                bad_identity += 1
                line.line_state = "quarantined"
                line.notes = "Debit - Credit != Balance (%.2f)" % (
                    line.debit - line.credit - line.balance
                )
                continue
            if abs(line.balance) < 0.005:
                zero += 1
                line.line_state = "quarantined"
                line.notes = "zero-amount open item (excluded from the entry)"
                continue
            if line.legacy_ref in seen:
                dup += 1
                line.line_state = "quarantined"
                line.notes = "duplicate voucher ref (first kept: row %d)" % seen[line.legacy_ref]
                continue
            seen[line.legacy_ref] = line.row_no
            line.legacy_reference = "AP:%s" % line.legacy_ref
            line.branch_id, matched = self._resolve_branch(line.legacy_branch)
            if not matched:
                branch_unmatched += 1
                line.notes = "branch label '%s' not matched — posts on company default" % (
                    line.legacy_branch or ""
                )
            else:
                line.notes = False
            line.line_state = "ready"
        total = sum(self.line_ids.filtered(lambda ln: ln.line_state == "ready").mapped("balance"))
        self.state = "validated"
        self._log(
            "validated %d rows: %d ready (open %.2f), %d quarantined "
            "(identity %d, zero %d, duplicate %d); %d branch labels unmatched"
            % (
                len(self.line_ids),
                len(self.line_ids.filtered(lambda ln: ln.line_state == "ready")),
                total,
                bad_identity + zero + dup,
                bad_identity,
                zero,
                dup,
                branch_unmatched,
            )
        )
        return True

    def action_post(self):
        """Post ONE voucher-level control entry through the governed M19
        funnel: a credit line per open voucher on the posting target (the
        register's debits are payables — report §2.4 sign flip), the
        resolved branch + its operating unit on every line's dimension row,
        and the net on the take-on contra account."""
        self.ensure_one()
        if self.state != "validated":
            raise UserError(_("Validate the register first."))
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = self.company_id
        control = self.control_account_id or self._ensure_control_account()
        self.control_account_id = control.id
        contra = self.contra_account_id or self._ensure_contra_account()
        self.contra_account_id = contra.id
        Journal = self.env["account.journal"]
        mig = Journal.search([("code", "=", "MIG"), ("company_id", "=", company.id)], limit=1)
        if not mig:
            mig = Journal.create(
                {
                    "name": "Legacy Take-on",
                    "code": "MIG",
                    "type": "general",
                    "company_id": company.id,
                }
            )
        quarantined = self.line_ids.filtered(lambda ln: ln.line_state == "quarantined")
        quarantined_net = sum(quarantined.mapped("balance"))
        lines = []
        dimension_by_line = {}
        vouchers = 0
        for line in self.line_ids.filtered(lambda ln: ln.line_state == "ready"):
            lines.append(
                (
                    0,
                    0,
                    {
                        "account_id": control.id,
                        "name": "Legacy AP take-on %s" % line.legacy_ref,
                        "debit": -line.balance if line.balance < 0 else 0.0,
                        "credit": line.balance if line.balance > 0 else 0.0,
                    },
                )
            )
            if line.branch_id and line.branch_id.operating_unit_id:
                dimension_by_line[vouchers] = {
                    "branch_id": line.branch_id.id,
                    "operating_unit_id": line.branch_id.operating_unit_id.id,
                }
            line.line_state = "posted"
            vouchers += 1
        if not lines:
            raise UserError(_("Nothing to post — no validated rows carry an open amount."))
        net = sum(ln[2]["debit"] - ln[2]["credit"] for ln in lines)
        lines.append(
            (
                0,
                0,
                {
                    "account_id": contra.id,
                    "name": "Legacy AP take-on contra (%s, net open position of %s)"
                    % (self.import_ref, self.source_filename or "register"),
                    "debit": -net if net < 0 else 0.0,
                    "credit": net if net > 0 else 0.0,
                },
            )
        )
        move, _dims = post_with_dimensions(
            self.env,
            {
                "journal_id": mig.id,
                "company_id": company.id,
                "date": self.takeon_date,
                "move_type": "entry",
                "ref": "%s-AP-TAKEON" % self.import_ref,
                "narration": _(
                    "Opening AP position from legacy register %s (source account %s): "
                    "%d open vouchers, net %.2f on the contra account until the "
                    "supplier subledger take-on completes%s."
                )
                % (
                    self.source_filename or "",
                    self.legacy_account_code,
                    vouchers,
                    net,
                    _(" (quarantined %.2f excluded)") % quarantined_net if quarantined else "",
                ),
                "line_ids": lines,
            },
            dimension_by_line,
            source="suspense",
            source_ref="%s AP register take-on" % self.import_ref,
        )
        self.posted_move_id = move.id
        self.state = "posted"
        self._log(
            "posted %s (%d lines: %d voucher credits + contra, net %.2f on %s; "
            "posting target %s from source account %s; %d rows quarantined %.2f)"
            % (
                move.name,
                len(move.line_ids),
                vouchers,
                net,
                contra.name,
                control.name,
                self.legacy_account_code,
                len(quarantined),
                quarantined_net,
            )
        )
        return True

    def action_rollback(self):
        """Reverse the opening entry (mirror entry through the same funnel)
        and park the batch. The voucher rows stay staged for a corrected run."""
        self.ensure_one()
        if self.state != "posted" or not self.posted_move_id:
            raise UserError(_("Only a posted take-on can be rolled back."))
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        move = self.posted_move_id
        mirror = []
        for line in move.line_ids:
            if abs(line.balance) < 0.005:
                continue
            mirror.append(
                (
                    0,
                    0,
                    {
                        "account_id": line.account_id.id,
                        "date_maturity": line.date_maturity or False,
                        "name": "AP take-on rollback: %s" % (line.name or "")[:44],
                        "debit": -line.balance if line.balance < 0 else 0.0,
                        "credit": line.balance if line.balance > 0 else 0.0,
                    },
                )
            )
        reversal, _dims = post_with_dimensions(
            self.env,
            {
                "journal_id": move.journal_id.id,
                "company_id": move.company_id.id,
                "date": fields.Date.context_today(self),
                "move_type": "entry",
                "ref": "ROLLBACK %s" % (move.ref or move.name),
                "narration": _("Rollback of legacy AP take-on %s.") % (move.name or ""),
                "line_ids": mirror,
            },
            {},
            source="suspense",
            source_ref="%s AP register rollback" % self.import_ref,
        )
        posted = self.line_ids.filtered(lambda ln: ln.line_state == "posted")
        posted.write({"line_state": "ready"})
        self.state = "rolled_back"
        self._log(
            "rolled back via mirror entry %s (%d voucher rows returned to ready)"
            % (reversal.name, len(posted))
        )
        return True

    @api.depends("line_ids", "line_ids.line_state")
    def _compute_counts(self):
        for batch in self:
            lines = batch.line_ids
            batch.line_count = len(lines)
            batch.ready_count = len(lines.filtered(lambda ln: ln.line_state == "ready"))
            batch.quarantined_count = len(lines.filtered(lambda ln: ln.line_state == "quarantined"))
            batch.posted_count = len(lines.filtered(lambda ln: ln.line_state == "posted"))

    @api.depends("line_ids.balance", "line_ids.line_state")
    def _compute_totals(self):
        for batch in self:
            batch.total_open = sum(
                batch.line_ids.filtered(lambda ln: ln.line_state in ("ready", "posted")).mapped(
                    "balance"
                )
            )


class FixApTakeonLine(models.Model):
    _name = "fix.ap.takeon.line"
    _description = "Legacy AP Ledger Take-on Line"
    _order = "batch_id, row_no"

    batch_id = fields.Many2one("fix.ap.takeon.batch", required=True, ondelete="cascade")
    row_no = fields.Integer()
    legacy_ref = fields.Char(
        string="Legacy Voucher",
        index=True,
        help="Journal Entry value verbatim, e.g. PPBLM/2026/00296.",
    )
    source_ref_note = fields.Char(
        help="Parenthetical on the voucher (the 6 of 297 rows that carry one)."
    )
    legacy_reference = fields.Char(index=True, help="MIG-03 idempotency key: AP:<voucher ref>.")
    legacy_date = fields.Date(string="Voucher Date")
    legacy_created_by = fields.Char(string="Legacy Created By")
    legacy_created_on = fields.Datetime(string="Legacy Created On")
    legacy_branch = fields.Char(string="Legacy Branch Label")
    legacy_company = fields.Char(string="Legacy Company Label")
    branch_id = fields.Many2one("fix.branch", string="Matched Branch")
    debit = fields.Monetary(currency_field="currency_id")
    credit = fields.Monetary(currency_field="currency_id")
    balance = fields.Monetary(
        currency_field="currency_id", help="The row's own open amount (register convention)."
    )
    currency_id = fields.Many2one(related="batch_id.currency_id")
    line_state = fields.Selection(LINE_STATES, default="staged")
    notes = fields.Char()
