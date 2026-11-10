# Legacy GL control-ledger import (2026-11-09 AR ledger 201 report, Lane 2).
#
# The 201_Account_Receivable_Ledger.xlsx export from the production Odoo is
# 3,739 anonymous journal lines on legacy control account 100201 (Feb-Nov
# 2026, 48 branches, 19 POS payment-method journals, net -BDT 33.6M credit).
# The top-class ERP doctrine (SAP FI-AR open-item object, D365 one-voucher-
# per-customer, Odoo per-partner open invoices) and the 2026-11-09 readiness
# report both refuse re-posting that history transaction-by-transaction on
# receivable accounts: the lines carry no partner and no due date, so they
# can neither reconcile nor age, and they would double-count the partner
# take-on already posted through fix.ledger.takeon.batch (MIG/2026/11/0001).
#
# This is the complementary lane: an auditable read-only ARCHIVE of every
# source line plus ONE branch-dimensioned control entry that lands the net
# position on a dedicated legacy control account (not a receivable account,
# so the partner/due-date constraints are never triggered). The archive is
# the GL-side reconciliation evidence for the partner-ledger take-on.
#
# Staging never trusts the sheet: header row is detected, amounts are
# re-parsed, per-row debit-credit=balance is re-proved, branch labels are
# resolved through name -> legacy_reference -> the crosswalk aliases, and
# anything unresolvable is quarantined (posted never, visible always).
import base64
import datetime
import io
import json
import logging
import re

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

# Legacy journal-entry prefixes in the 201 export -> (target journal code on
# the posting chart, human label). The POS payment-method receipts (bKash,
# Nagad, bank POS terminals) map to their own journals exactly the way Odoo
# POS payment methods and D365 Commerce tender types do (report Part D.3).
# Odoo journal codes cap at 5 characters, so six-character legacy prefixes
# land on their 5-char forms (PBKASH->PBKAS, PPOSPU->PPOSP, PNAGAD->PNAGA,
# PABBLE->PABBL, PDBBLS/PDBBL->PDBBL, PIBBLA->PIBBL, PABBLB->PABBB); the
# journal names carry the full legacy prefix for the audit trail.
LEGACY_JOURNAL_MAP = {
    "PBKASH": ("PBKAS", "POS bKash Receipts (legacy prefix PBKASH)"),
    "PPOSPU": ("PPOSP", "POS Sales/Purchase (legacy prefix PPOSPU)"),
    "PABBLE": ("PABBL", "POS ABL Bank (legacy prefix PABBLE)"),
    "PDBBLS": ("PDBBL", "POS DBBL (S) (legacy prefix PDBBLS)"),
    "PSCB": ("PSCB", "POS Standard Chartered (legacy)"),
    "PNAGAD": ("PNAGA", "POS Nagad Receipts (legacy prefix PNAGAD)"),
    "PBNK4": ("PBNK4", "POS Bank Journal 4 (legacy)"),
    "PBNK3": ("PBNK3", "POS Bank Journal 3 (legacy)"),
    "PDBBL": ("PDBBL", "POS DBBL (legacy prefix PDBBL)"),
    "PBNK1": ("PBNK1", "POS Bank Journal 1 (legacy)"),
    "PMBL": ("PMBL", "POS MB Bank (legacy)"),
    "PPBLM": ("PPBLM", "POS PBL (M) (legacy)"),
    "PIBBLA": ("PIBBL", "POS IBBL (A) (legacy prefix PIBBLA)"),
    "PABBLB": ("PABBB", "POS ABB (B) (legacy prefix PABBLB)"),
    "CIH": ("CIH", "Cash in Hand (legacy)"),
    "AILABLE": ("ABBLE", "ABL Bank (legacy)"),
    "DBBLS": ("DBBLS", "DBBL (S) (legacy)"),
    "SCB": ("SCB", "Standard Chartered (legacy)"),
    "DBBL": ("DBBL", "Dutch-Bangla Bank (legacy)"),
}

# Crosswalk: branch label as printed in the legacy ledger -> the branch name
# expected in the live fix.branch master. Sourced from
# _migration/staged/crosswalk_branch.csv (2026-11-09 user-migration work,
# 47/48 coverage) plus the manual Coca-Cola resolution; branches that already
# match by name are absent on purpose — name match runs first.
LEGACY_BRANCH_ALIASES = {
    "1000Fix Services Ltd.": "1000 FiX Head Office",
    "Head Office Customer Care": "1000 FiX Head Office",
    "Barishal CSC": "Barishal Service Center",
    "Basundhara City CSC": "Basundhara City Service Center",
    "Bogura CSC": "Bogura Service Center",
    "Chattogram CSC": "Chattogram Service Center",
    "Cumilla CSC": "Cumilla Service Center",
    "Dinajpur CSC": "Dinajpur Service Center",
    "Elephant Road CSC": "Elephant Road Service Center",
    "Feni CSC": "Feni Service Center",
    "Gazipur CSC": "Gazipur Service Center",
    "IDB CSC": "IDB Bhaban Service Center",
    "Jashore CSC": "Jashore Service Center",
    "Khulna CSC": "Khulna Service Center",
    "Motijheel CSC": "Motijheel Service Center",
    "Mymensingh CSC": "Mymensingh Service Center",
    "Noakhali CSC": "Noakhali Service Center",
    # measured 2026-11-09: the branch master holds "Rangpur City Service
    # Center" (BR-0027) and nothing else for Rangpur — the previous target
    # name matched no branch, quarantining every Rangpur ledger row.
    "Rangpur CSC": "Rangpur City Service Center",
    "R F Tower CSC": "R F Tower Service Center",
    "Rajshahi CSC": "Rajshahi Service Center",
    "Uttara CSC": "Uttara Service Center",
    "Sylhet CSC": "Sylhet Service Center",
    "Corporate Service Branch": "Corporate Service Center",
    "Coca-Cola": "Coca-Cola Service Center",
    "Honor B.City ASC": "Honor Bashundhara ASC",
    "Honor Mirpur ASC": "Honor Mirpur ASC",
    "Honor Uttara ASC": "Honor Uttara ASC",
    "Honor JFP ESP": "Jamuna Future Park Service Center",
    "Jamuna Future Park CSC": "Jamuna Future Park Service Center",
    "Sony-Smart Service Operation": "Sony Smart Service Operation",
    "LG Operation": "LG Service Operation",
    "Whirlpool Service Operation": "Whirlpool Service Operation",
    "Other Home Appliances Services": "Other Home Appliances Service Center",
    "Xiaomi -Mirpur-10": "Xiaomi Mirpur-10",
    "Xiaomi -Chattagram": "Xiaomi Chattagram",
    "Xiaomi -Mymensingh": "Xiaomi Mymensingh",
    "Xiaomi -Savar": "Xiaomi Savar",
    "Xiaomi-Gazipur": "Xiaomi Gazipur",
    "Xiaomi-Narayanganj": "Xiaomi Narayanganj",
    "Xiaomi -Bogura": "Xiaomi Bogura",
    "Xiaomi-Jashore": "Xiaomi Jashore",
    "Xiaomi -Dinajpur": "Xiaomi Dinajpur",
    "Xiaomi-Kushtia": "Xiaomi Kushtia",
    "Xiaomi-Brahmanbaria": "Xiaomi Brahmanbaria",
    "Xiaomi-Feni (QSP)": "Xiaomi Feni QSP",
    "Xiaomi Sirajganj": "Xiaomi Sirajganj",
    "Samsung CSP Dhaka": "Samsung CSP Dhaka",
}

LINE_STATES = [
    ("staged", "Staged (raw)"),
    ("linked", "Branch resolved"),
    ("quarantined", "Quarantined (not posted)"),
    ("posted", "Posted (control entry)"),
    ("error", "Error"),
]

_PREFIX_RE = re.compile(r"^([A-Z][A-Z0-9]*)/")
_INV_REF_RE = re.compile(r"\((INV/\d{4}/\d+)\)")


def _norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip()).casefold()


class FixLegacyLedgerBatch(models.Model):
    _name = "fix.legacy.ledger.batch"
    _description = "Legacy GL Control-Ledger Import (Archive)"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(
        required=True,
        tracking=True,
        default=lambda self: _("Legacy control ledger %s") % fields.Date.context_today(self),
    )
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    import_ref = fields.Char(
        required=True,
        default=lambda self: "LEGAR-%s" % fields.Date.context_today(self).strftime("%Y-%m"),
        help="Prefix for the archive keys of every staged line (MIG-03 style).",
    )
    source_file = fields.Binary(string="Legacy Ledger Spreadsheet", attachment=True)
    source_filename = fields.Char()
    legacy_account_code = fields.Char(
        default="100201",
        required=True,
        help="Account code the ledger was exported under in the legacy system.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("staged", "Staged"),
            ("validated", "Validated"),
            ("posted", "Control Entry Posted"),
            ("rolled_back", "Rolled Back"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    control_account_id = fields.Many2one(
        "account.account",
        string="Legacy Control Account (posting target)",
        domain=[("account_type", "=", "asset_current")],
        help="Dedicated GL account carrying the archived legacy position. It is "
        "deliberately NOT a receivable account: the archived lines are anonymous "
        "(no partner, no due date) so they must never touch a reconcileable "
        "receivable control (report Part B.3).",
    )
    contra_account_id = fields.Many2one(
        "account.account",
        string="Take-on Contra Account",
        domain=[("account_type", "=", "liability_current")],
        help="Carries the net legacy position until the remaining subledgers "
        "are taken on (same tier-1 rule as the partner-ledger take-on).",
    )
    posted_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    decision_log = fields.Text(readonly=True, copy=False)

    line_ids = fields.One2many("fix.legacy.ledger.line", "batch_id")
    line_count = fields.Integer(compute="_compute_counts", store=True)
    linked_count = fields.Integer(compute="_compute_counts", store=True)
    quarantined_count = fields.Integer(compute="_compute_counts", store=True)
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

    # --------------------------------------------------------- helpers
    def _log(self, msg):
        self.ensure_one()
        stamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.message_post(body="[%s] %s" % (stamp, msg))
        self.decision_log = "%s\n[%s] %s" % (self.decision_log or "", stamp, msg)

    def _ensure_control_account(self):
        """Create the legacy control account on first use. asset_current and
        not reconcileable: an archive position, posted through the M19 funnel
        with branch dimensions, but never a partner-facing receivable.
        (Odoo 19: account.account carries no stored company_id — the code is
        company-dependent via code_store, so the search keys on the code.)"""
        self.ensure_one()
        Account = self.env["account.account"]
        code = self.legacy_account_code or "100201"
        existing = Account.search([("code", "=", code)], limit=1)
        if existing:
            return existing
        try:
            return Account.create(
                {
                    "name": "Account Receivable (Legacy 201 Control)",
                    "code": code,
                    "account_type": "asset_current",
                    "reconcile": False,
                }
            )
        except Exception:
            _logger.exception("legacy control account create failed")
            raise UserError(
                _(
                    "Could not create legacy control account %s. Create it on the "
                    "posting chart first, or pick an existing account."
                )
                % code
            ) from None

    def _ensure_contra_account(self):
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

    # --------------------------------------------------------- actions
    def action_stage(self):
        """Parse the legacy ledger statement: header row detected (the export
        carries a title and a record-count row above it), one archive line per
        data row, the trailing Total row skipped."""
        self.ensure_one()
        if self.state not in ("draft", "staged"):
            raise UserError(_("Only a draft or staged import can be staged."))
        if not self.source_file:
            raise UserError(_("Upload the legacy ledger spreadsheet first."))
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

        Line = self.env["fix.legacy.ledger.line"]
        Line.search([("batch_id", "=", self.id)]).unlink()
        n = 0
        for row in rows[header_idx + 1 :]:
            cells = list((row or [])[:9])
            if not any(c is not None for c in cells):
                continue
            first = str(cells[0] or "").strip()
            if first == "Total" or first.startswith("Total"):
                continue
            (
                raw_date,
                journal_entry,
                branch_raw,
                company_raw,
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
            if raw_date:
                if isinstance(raw_date, datetime.datetime):
                    entry_date = raw_date.date()
                elif isinstance(raw_date, datetime.date):
                    entry_date = raw_date
                else:
                    try:
                        entry_date = datetime.date.fromisoformat(str(raw_date)[:10])
                    except ValueError:
                        entry_date = None
            prefix = ""
            m = _PREFIX_RE.match(str(journal_entry or ""))
            if m:
                prefix = m.group(1)
            inv = _INV_REF_RE.search(str(journal_entry or ""))
            created_on_dt = False
            if created_on:
                if isinstance(created_on, datetime.datetime):
                    created_on_dt = created_on
                else:
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
                    "journal_prefix": prefix,
                    "invoice_ref": inv.group(1) if inv else "",
                    "branch_raw": str(branch_raw or "").strip()[:120],
                    "company_raw": str(company_raw or "").strip()[:120],
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
            "staged %d rows from %s (account %s)"
            % (n, self.source_filename or "spreadsheet", self.legacy_account_code)
        )
        return True

    def action_validate(self):
        """Re-prove the arithmetic, resolve every branch label through
        name -> legacy_reference -> the built-in aliases -> the estate
        crosswalk parameter, and quarantine anything that cannot resolve
        (nothing posts silently).

        The estate crosswalk (`cd_gl_ext.legacy_ledger.branch_crosswalk`,
        JSON {legacy label: branch name}) is what the user/employee
        migration sessions established for the REAL branch master — several
        legacy brand labels consolidate onto one physical service centre
        (Sony ops -> HQ, Honor B.City -> Bashundhara City SC), so a single
        legacy_reference stamp cannot express it."""
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
        bad_arith = bad_branch = bad_date = 0
        for line in self.line_ids:
            notes = []
            if abs(line.debit - line.credit - line.balance) > 0.005:
                bad_arith += 1
                notes.append("Debit - Credit != Balance")
            if not line.entry_date:
                bad_date += 1
                notes.append("missing/invalid date")
            raw = line.branch_raw or ""
            branch = by_name.get(_norm(raw))
            if not branch:
                branch = by_legacy.get(_norm(raw))
            if not branch:
                alias = LEGACY_BRANCH_ALIASES.get(raw.strip())
                branch = by_name.get(_norm(alias)) if alias else None
                if branch and not branch.legacy_reference:
                    branch.sudo().write({"legacy_reference": raw.strip()[:80]})
            if not branch:
                target = estate_cw.get(raw.strip())
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
            line.notes = "; ".join(notes)
            if notes and line.line_state != "quarantined":
                line.line_state = "quarantined"
        self.state = "validated"
        self._log(
            "validated %d rows: %d branch-resolved, %d quarantined "
            "(arithmetic %d, branch %d, date %d)"
            % (
                len(self.line_ids),
                len(self.line_ids) - bad_branch,
                bad_branch,
                bad_arith,
                bad_branch,
                bad_date,
            )
        )
        return True

    def action_post(self):
        """Post ONE branch-dimensioned control entry through the M19 funnel:
        per-branch net lines on the legacy control account (branch + its own
        operating unit on every line's dimension row), one contra line for
        the net. Quarantined lines never post; their total is logged."""
        self.ensure_one()
        if self.state != "validated":
            raise UserError(_("Validate the batch first."))
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
        postable = self.line_ids.filtered(lambda ln: ln.line_state == "linked")
        if not postable:
            raise UserError(_("No line resolved a branch — nothing to post."))
        quarantined = self.line_ids.filtered(lambda ln: ln.line_state == "quarantined")
        quarantined_net = sum(quarantined.mapped("balance"))

        # Aggregate per resolved branch (deterministic order for review).
        order = {}
        for line in postable:
            order.setdefault(line.branch_resolved_id, []).append(line)
        lines = []
        dimension_by_line = {}
        idx = 0
        for branch in sorted(order, key=lambda b: (b.name or "")):
            group = order[branch]
            debit = sum(g.debit for g in group)
            credit = sum(g.credit for g in group)
            net = debit - credit
            if abs(net) < 0.005:
                continue
            lines.append(
                (
                    0,
                    0,
                    {
                        "account_id": control.id,
                        "name": "Legacy %s control — %s (%d rows)"
                        % (self.legacy_account_code, branch.name, len(group)),
                        "debit": net if net > 0 else 0.0,
                        "credit": -net if net < 0 else 0.0,
                    },
                )
            )
            dimension_by_line[idx] = {
                "branch_id": branch.id,
                "operating_unit_id": branch.operating_unit_id.id,
            }
            idx += 1
        if not lines:
            raise UserError(_("Every resolved branch nets to zero — nothing to post."))
        net = sum(ln[2]["debit"] - ln[2]["credit"] for ln in lines)
        lines.append(
            (
                0,
                0,
                {
                    "account_id": contra.id,
                    "name": "Legacy %s control import contra (%s, net; quarantined %.2f excluded)"
                    % (
                        self.legacy_account_code,
                        self.source_filename or self.import_ref,
                        quarantined_net,
                    ),
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
                "date": fields.Date.context_today(self),
                "move_type": "entry",
                "ref": "%s-CTRL" % self.import_ref,
                "narration": _(
                    "Legacy GL control-ledger archive %s: %d of %d rows posted as "
                    "%d branch-dimensioned control lines on account %s; net carried "
                    "on the contra account. Read-only archive — reconciliation "
                    "evidence for the partner-ledger take-on, never re-posted "
                    "transaction-by-transaction."
                )
                % (
                    self.source_filename or self.import_ref,
                    len(postable),
                    len(self.line_ids),
                    len(lines) - 1,
                    control.code or control.name,
                ),
                "line_ids": lines,
            },
            dimension_by_line,
            source="suspense",
            source_ref="%s legacy control import" % self.import_ref,
        )
        self.posted_move_id = move.id
        postable.write({"line_state": "posted"})
        self.state = "posted"
        self._log(
            "posted %s (%d lines incl. contra; net %.2f on contra %s; %d "
            "quarantined rows excluded, their net %.2f stays unposted)"
            % (move.name, len(move.line_ids), net, contra.name, len(quarantined), quarantined_net)
        )
        return True

    def action_rollback(self):
        """Reverse the control entry with a mirror entry (same funnel). The
        archive lines stay — they are the evidence; only the ledger position
        rolls back."""
        self.ensure_one()
        if self.state != "posted" or not self.posted_move_id:
            raise UserError(_("Only a posted import can be rolled back."))
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        move = self.posted_move_id
        mirror = []
        dims = {}
        branch_by_line = {}
        dim_rows = (
            self.env["fix.journal.dimension"]
            .sudo()
            .search([("move_line_id", "in", move.line_ids.ids)])
        )
        for dim in dim_rows:
            branch_by_line[dim.move_line_id.id] = dim
        for _i, line in enumerate(move.line_ids):
            if abs(line.balance) < 0.005:
                continue
            vals = {
                "account_id": line.account_id.id,
                "name": "Control import rollback: %s" % (line.name or "")[:48],
                "debit": -line.balance if line.balance < 0 else 0.0,
                "credit": line.balance if line.balance > 0 else 0.0,
            }
            mirror.append((0, 0, vals))
            dim = branch_by_line.get(line.id)
            if dim:
                dims[len(mirror) - 1] = {
                    "branch_id": dim.branch_id.id,
                    "operating_unit_id": dim.operating_unit_id.id,
                }
        reversal, _d = post_with_dimensions(
            self.env,
            {
                "journal_id": move.journal_id.id,
                "company_id": move.company_id.id,
                "date": fields.Date.context_today(self),
                "move_type": "entry",
                "ref": "ROLLBACK %s" % (move.ref or move.name),
                "narration": _("Rollback of legacy control import %s.") % (move.name or ""),
                "line_ids": mirror,
            },
            dims,
            source="suspense",
            source_ref="%s control rollback" % self.import_ref,
        )
        self.line_ids.filtered(lambda ln: ln.line_state == "posted").write({"line_state": "linked"})
        self.state = "rolled_back"
        self._log("rolled back via mirror entry %s (archive lines retained)" % reversal.name)
        return True

    @api.depends("line_ids", "line_ids.line_state")
    def _compute_counts(self):
        for batch in self:
            lines = batch.line_ids
            batch.line_count = len(lines)
            batch.linked_count = len(
                lines.filtered(lambda ln: ln.line_state in ("linked", "posted"))
            )
            batch.quarantined_count = len(lines.filtered(lambda ln: ln.line_state == "quarantined"))
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


class FixLegacyLedgerLine(models.Model):
    _name = "fix.legacy.ledger.line"
    _description = "Legacy GL Control-Ledger Line (Archive)"
    _order = "batch_id, row_no"

    batch_id = fields.Many2one("fix.legacy.ledger.batch", required=True, ondelete="cascade")
    row_no = fields.Integer()
    entry_date = fields.Date(string="Date")
    journal_entry = fields.Char(string="Journal Entry")
    journal_prefix = fields.Char(string="Journal", index=True)
    invoice_ref = fields.Char(string="Legacy Invoice Ref", index=True)
    branch_raw = fields.Char(string="Branch (legacy label)")
    branch_resolved_id = fields.Many2one("fix.branch", string="Branch (resolved)")
    company_raw = fields.Char(string="Company (legacy)")
    created_by_name = fields.Char(string="Created By (legacy)")
    created_on = fields.Datetime(string="Created On (legacy)")
    debit = fields.Monetary(currency_field="currency_id")
    credit = fields.Monetary(currency_field="currency_id")
    balance = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(related="batch_id.currency_id")
    line_state = fields.Selection(LINE_STATES, default="staged")
    notes = fields.Char()
