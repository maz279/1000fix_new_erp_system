# Legacy partner-ledger take-on wizard (2026-11-08 report R-1b).
#
# A balance-only legacy partner ledger cannot be typed into the workspace
# journal editor line by line: the 2026-11-08 migration of
# partner_ledger.xlsx (2,184 parties, 1,575-line opening entry) was executed
# by a reviewed script because no guided path existed. This wizard is that
# path, distilled: stage the legacy spreadsheet, validate its arithmetic and
# party identification, link-or-create parties through the SAME governance
# the M33 party loader uses (two-tier registration approvals, roles, unique
# legacy_reference keys), and post the opening entry through
# post_with_dimensions() — never raw SQL on control accounts.
#
# Soft dependency: party-master governance (cd_party_master) is detected at
# runtime; without it the wizard still stages and posts but creates plain
# res.partner rows. The platform always installs both.
import base64
import io
import re

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

from .fix_gl_ext import require_takeon_authority

_MOBILE = re.compile(r"^(01\d{9})\s*[-–]?\s*(.*)$")
_BRACKET = re.compile(r"^\[\s*([^]]*?)\s*\]\s*(.*)$")
_PAREN = re.compile(r"^\(\s*([^)]*?)\s*\)\s*-?\s*(.*)$")
_V23 = re.compile(r"^23\s*-")

_CORP_HINTS = re.compile(
    r"\b(ltd|limited|pvt|private|company|co|corp|corporation|group|industries|"
    r"enterprise|enterprises|trading|international|associates|bangladesh|bd|"
    r"bank|insurance|university|college|school|hospital|clinic|diagnostic|"
    r"ministry|authority|commission|government|govt|agency|foundation|ngo|"
    r"organization|organisation|solutions|services|systems|technologies|"
    r"electronics|mobile|telecom|cafe|shop|store|dealer|partnership|llp|inc|pte)\b",
    re.I,
)

SUSPENSE_KINDS = [
    ("office_use", "Office Use (internal)"),
    ("stock_migration", "Stock Migration Contra"),
    ("unidentified", "Unidentified Party"),
    ("own_company", "Own Company / Inter-Company"),
]

LINE_STATES = [
    ("staged", "Staged (raw)"),
    ("quarantined", "Quarantined (not imported)"),
    ("linked", "Matched — legacy key attached"),
    ("created", "Created party"),
    ("gl_mapped", "Internal — mapped to GL account"),
    ("posted", "Posted to ledger"),
    ("error", "Error"),
]


def parse_legacy_partner(raw):
    """Split one legacy `Partner` cell into (code, mobile, name, vintage23).

    The real ledger mixes six identification formats; the parser is the one
    exercised against all 2,345 rows of partner_ledger.xlsx on 2026-11-08.
    """
    code, mobile, rest = "", "", str(raw or "").strip()
    m = _BRACKET.match(rest)
    if m:
        code, rest = m.group(1), m.group(2)
        m2 = _PAREN.match(rest)
        if m2:
            code = code or m2.group(1)
            rest = m2.group(2)
    else:
        m2 = _PAREN.match(rest)
        if m2:
            code, rest = m2.group(1), m2.group(2)
    mm = _MOBILE.match(rest)
    if mm:
        mobile, rest = mm.group(1), mm.group(2)
    vintage23 = bool(_V23.match(rest.strip()))
    name = re.sub(r"\s+", " ", _V23.sub("", rest.strip())).strip()
    return code.strip(), mobile, name, vintage23


def _norm_name(name):
    s = _V23.sub("", str(name or ""))
    s = re.sub(r"[^0-9a-z& ]", " ", s.casefold())
    return re.sub(r"\s+", " ", s).strip()


class FixLedgerTakeonBatch(models.Model):
    _name = "fix.ledger.takeon.batch"
    _description = "Legacy Partner-Ledger Take-on"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    takeon_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        help="The opening balance date — a period boundary, so the legacy "
        "position starts its aging clock cleanly.",
    )
    source_file = fields.Binary(string="Legacy Ledger Spreadsheet", attachment=True)
    source_filename = fields.Char()
    import_ref = fields.Char(
        required=True,
        help="Prefix for the unique legacy_reference keys (MIG-03), e.g. "
        "LEDGER-2026-11 -> LEDGER-2026-11 parties keep their source code.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("staged", "Staged"),
            ("validated", "Validated"),
            ("imported", "Parties Imported"),
            ("posted", "Opening Entry Posted"),
            ("rolled_back", "Rolled Back"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.ledger.takeon.line", "batch_id")
    line_count = fields.Integer(compute="_compute_counts", store=True)
    linked_count = fields.Integer(compute="_compute_counts", store=True)
    created_count = fields.Integer(compute="_compute_counts", store=True)
    gl_mapped_count = fields.Integer(compute="_compute_counts", store=True)
    quarantined_count = fields.Integer(compute="_compute_counts", store=True)
    total_debit = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    total_credit = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    total_balance = fields.Monetary(
        compute="_compute_totals", store=True, currency_field="currency_id"
    )
    external_balance = fields.Monetary(
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
        help="Net of the lines carried on partner accounts (excludes the "
        "internal/suspense rows mapped straight to GL accounts).",
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    posted_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    contra_account_id = fields.Many2one(
        "account.account",
        string="Take-on Contra Account",
        domain=[("account_type", "=", "liability_current")],
        help="Carries the net legacy position until the remaining subledgers "
        "(stock, assets, banks) are taken on; then it reclassifies to "
        "opening equity so the wash account reads zero (tier-1 rule).",
    )
    decision_log = fields.Text(readonly=True, copy=False)

    # --------------------------------------------------------- helpers
    def _log(self, msg):
        self.ensure_one()
        stamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.message_post(body="[%s] %s" % (stamp, msg))
        self.decision_log = "%s\n[%s] %s" % (self.decision_log or "", stamp, msg)

    def _has_party_master(self):
        return "fix.party.role" in self.env

    # --------------------------------------------------------- actions
    def action_stage(self):
        """Parse the spreadsheet: one line per ledger row, canonicalised the
        way the 2026-11-08 migration parsed partner_ledger.xlsx."""
        self.ensure_one()
        if self.state not in ("draft", "staged"):
            raise UserError(_("Only a draft or staged take-on can be staged."))
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
        Line = self.env["fix.ledger.takeon.line"]
        Line.search([("batch_id", "=", self.id)]).unlink()
        n = 0
        for row in sheet.iter_rows(min_row=2, values_only=True):
            partner, debit, credit, balance = (*tuple(row), None, None, None, None)[:4]
            if partner is None and debit is None and credit is None and balance is None:
                continue
            code, mobile, name, v23 = parse_legacy_partner(partner)
            try:
                debit = float(debit or 0.0)
                credit = float(credit or 0.0)
                balance = float(balance or 0.0)
            except (TypeError, ValueError):
                raise UserError(
                    _("Row %d: debit/credit/balance are not numbers.") % (n + 2)
                ) from None
            if not name and not code and not mobile:
                continue
            Line.create(
                {
                    "batch_id": self.id,
                    "row_no": n + 1,
                    "raw_name": str(partner or ""),
                    "clean_name": name,
                    "legacy_code": code,
                    "phone_norm": mobile,
                    "vintage23": v23,
                    "debit": debit,
                    "credit": credit,
                    "balance": balance,
                    "line_state": "staged",
                }
            )
            n += 1
        workbook.close()
        self.state = "staged"
        self._log("staged %d rows from %s" % (n, self.source_filename or "spreadsheet"))
        return True

    def action_validate(self):
        """Arithmetic identity, duplicate keys, internal-party detection and
        legacy_reference assignment — nothing is written to partners yet."""
        self.ensure_one()
        if self.state != "staged":
            raise UserError(_("Stage the spreadsheet first."))
        Partner = self.env["res.partner"]
        partner_by_ref = {}
        if self._has_party_master():
            for p in Partner.sudo().search(
                [("legacy_reference", "=like", "%s-%%" % self.import_ref)]
            ):
                partner_by_ref[p.legacy_reference] = p
        bad_identity = 0
        used_refs = set(partner_by_ref)
        # Name indexes over the WHOLE live party master, built once. The
        # per-line scan this replaces read only the first 5,000 parties that
        # carry a legacy key: on a master of 27,000 a real match beyond that
        # window was missed and a duplicate party created (and validating
        # 12,905 rows took 11 minutes). Exact (case-insensitive) name first,
        # then the normalised name among keyed parties; several parties with
        # one name resolve to the oldest and the line says so.
        exact_index, norm_index = {}, {}
        for row in Partner.sudo().search_read([], ["name", "legacy_reference"], order="id"):
            name = (row["name"] or "").strip()
            if not name:
                continue
            exact_index.setdefault(name.casefold(), []).append(row["id"])
            if row["legacy_reference"]:
                norm_index.setdefault(_norm_name(name), []).append(row["id"])
        for line in self.line_ids:
            if abs(line.debit - line.credit - line.balance) > 0.005:
                bad_identity += 1
                line.line_state = "quarantined"
                line.notes = "Debit - Credit != Balance (%.2f)" % (
                    line.debit - line.credit - line.balance
                )
                continue
            line.suspense_kind = line._detect_suspense()
            if line.suspense_kind:
                line.line_state = "gl_mapped"
                line.legacy_reference = "%s-GLMAP-%d" % (self.import_ref, line.row_no)
                continue
            line.legacy_reference = line._build_legacy_ref(self.import_ref)
            # R-12 (unique legacy_reference): source ledgers repeat generic
            # codes across many rows ('(E-Commerce) <name>' all parse to code
            # 'E-Commerce') — deterministically uniquify against live
            # partners AND earlier lines of this batch so import never
            # collides on the unique index (customer-ledger take-on,
            # 2026-11-10).
            if line.legacy_reference in used_refs:
                n = 2
                while "%s-%d" % (line.legacy_reference, n) in used_refs:
                    n += 1
                line.legacy_reference = "%s-%d" % (line.legacy_reference, n)
            used_refs.add(line.legacy_reference)
            existing = partner_by_ref.get(line.legacy_reference)
            if existing:
                line.matched_partner_id = existing.id
                line.line_state = "linked"
                continue
            # exact name, then normalised name, against the live parties
            norm = _norm_name(line.clean_name)
            candidates = []
            if norm:
                candidates = exact_index.get((line.clean_name or "").strip().casefold()) or (
                    norm_index.get(norm) or []
                )
            if candidates:
                line.matched_partner_id = candidates[0]
                line.line_state = "linked"
                if len(candidates) > 1:
                    line.notes = "%d live parties carry this name; linked to the oldest (#%d)" % (
                        len(candidates),
                        candidates[0],
                    )
            elif abs(line.balance) < 0.005 and not line.phone_norm:
                line.line_state = "quarantined"
                line.notes = "zero balance, no code/mobile, no master match"
            else:
                line.line_state = "staged"  # importable
        if bad_identity:
            self._log("validation quarantined %d rows failing the balance identity" % bad_identity)
        self.state = "validated"
        self._log("validated %d rows" % len(self.line_ids))
        return True

    def action_import(self):
        """Link or create every party through the governed path: two-tier
        registration approvals for registered classes (the M33 loader
        pattern), roles by exposure side, unique legacy_reference keys."""
        self.ensure_one()
        require_takeon_authority(self.env, "Importing the parties of a legacy take-on")
        if self.state != "validated":
            raise UserError(_("Validate the batch first."))
        Partner = self.env["res.partner"]
        Role = self.env["fix.party.role"] if self._has_party_master() else None
        Approval = self.env["fix.registration.approval"] if self._has_party_master() else None
        created = linked = 0
        for line in self.line_ids:
            if line.line_state == "linked":
                partner = line.matched_partner_id
                if not partner.legacy_reference or partner.legacy_reference == "CORP-2023-23":
                    partner.sudo().write({"legacy_reference": line.legacy_reference})
                linked += 1
            elif line.line_state == "staged":
                klass = "corporate" if _CORP_HINTS.search(line.clean_name or "") else "individual"
                vals = {
                    "name": line.clean_name or line.legacy_reference,
                    "legacy_reference": line.legacy_reference,
                    "phone": line.phone_norm or False,
                }
                if self._has_party_master():
                    vals["party_class"] = klass
                partner = Partner.sudo().create(vals)
                if self._has_party_master() and klass == "corporate":
                    appr = Approval.search(
                        [("partner_id", "=", partner.id)], order="id desc", limit=1
                    )
                    if appr and not appr._fully_approved():
                        appr._guarded().write(
                            {
                                "lm_state": "approved",
                                "lm_decided_by": self.env.user.id,
                                "lm_decided_at": fields.Datetime.now(),
                                "admin_state": "approved",
                                "admin_decided_by": self.env.user.id,
                                "admin_decided_at": fields.Datetime.now(),
                            }
                        )
                        appr._activate_if_complete()
                elif self._has_party_master() and partner.party_status == "draft":
                    partner.sudo().write({"party_status": "active"})
                line.created_partner_id = partner.id
                line.line_state = "created"
                created += 1
            else:
                continue
            if Role and partner.party_status == "active":
                roles = []
                if line.balance > 0.005:
                    roles.append("customer")
                if line.balance < -0.005:
                    roles.append("vendor")
                for rt in roles:
                    if not Role.search_count(
                        [("partner_id", "=", partner.id), ("role_type", "=", rt)]
                    ):
                        Role.create(
                            {"partner_id": partner.id, "role_type": rt, "role_status": "active"}
                        )
        self.state = "imported"
        self._log("parties ready: %d linked, %d created" % (linked, created))
        return True

    def _configured_account(self, key, expected_type=None):
        """Read an account code from `cd_gl_ext.ledger_takeon.<key>` and
        resolve it. A configured code that does not resolve, or resolves to
        the wrong account type, is refused — a take-on never guesses."""
        code = (
            self.env["ir.config_parameter"].sudo().get_param("cd_gl_ext.ledger_takeon.%s" % key)
            or ""
        ).strip()
        if not code:
            return self.env["account.account"]
        account = (
            self.env["account.account"]
            .with_company(self.company_id)
            .search([("code", "=", code)], limit=1)
        )
        if not account:
            raise UserError(
                _(
                    "Take-on parameter cd_gl_ext.ledger_takeon.%(key)s names account %(code)s, which does not exist."
                )
                % {"key": key, "code": code}
            )
        if expected_type and account.account_type != expected_type:
            raise UserError(
                _(
                    "Take-on parameter cd_gl_ext.ledger_takeon.%(key)s names account "
                    "%(code)s, which is not of type %(type)s."
                )
                % {"key": key, "code": code, "type": expected_type}
            )
        return account

    def _control_account(self, kind):
        """Resolve the statutory control account: the estate parameter first
        (cd_gl_ext.ledger_takeon.<kind>_account_code — the lever for a chart
        that keeps its own legacy codes), then the chart link (1-20-10-010
        receivable / 2-10-10-010 payable), then the statutory code, then the
        account type ONLY when exactly one account carries it. A chart with
        several receivable/payable accounts and no parameter is refused: the
        first-by-code row is an arbitrary account (on the real chart it is
        the staff-loan account), never a safe default."""
        Account = self.env["account.account"].with_company(self.company_id)
        atype = "asset_receivable" if kind == "receivable" else "liability_payable"
        configured = self._configured_account("%s_account_code" % kind, atype)
        if configured:
            return configured
        if "fix.chart.account" in self.env:
            linked = (
                self.env["fix.chart.account"]
                .sudo()
                .search(
                    [("control_subledger", "=", kind), ("odoo_account_id", "!=", False)], limit=1
                )
            )
            if linked:
                return linked.odoo_account_id
        code = "121000" if kind == "receivable" else "211000"
        by_code = Account.search([("code", "=", code)], limit=1)
        if by_code:
            return by_code
        candidates = Account.search([("account_type", "=", atype)])
        if len(candidates) > 1:
            raise UserError(
                _(
                    "This chart has %(n)d %(kind)s accounts (%(codes)s) and none is "
                    "designated as the take-on control account. Set the system "
                    "parameter cd_gl_ext.ledger_takeon.%(kind)s_account_code to the "
                    "control account's code before posting."
                )
                % {
                    "n": len(candidates),
                    "kind": kind,
                    "codes": ", ".join(c.code or c.name for c in candidates[:8]),
                }
            )
        return candidates

    def _ensure_takeon_account(self, name, code):
        from .fix_gl_ext import ensure_legacy_account

        return ensure_legacy_account(self.env, self.company_id, name, code, "liability_current")

    def action_post(self):
        """Post the opening entry through the governed M19 funnel: AR/AP
        control lines carry partner and due date (the ORM requires it),
        internal rows post on mapped GL accounts, and one contra line
        carries the net legacy position."""
        self.ensure_one()
        require_takeon_authority(self.env, "Posting a legacy take-on")
        if self.state != "imported":
            raise UserError(_("Import the parties first."))
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = self.company_id
        Account = self.env["account.account"]
        ar = self._control_account("receivable")
        ap = self._control_account("payable")
        contra = self.contra_account_id or self._ensure_takeon_account(
            "Legacy Ledger Take-on Contra", "2.99.99.901"
        )
        if not (ar and ap and contra):
            raise UserError(_("Receivable, payable and contra accounts must exist before posting."))
        suspense_map = {}
        for kind, _label in SUSPENSE_KINDS:
            configured = self._configured_account("suspense_%s_account_code" % kind)
            if configured:
                suspense_map[kind] = configured
            elif kind == "stock_migration":
                suspense_map[kind] = Account.search(
                    [("name", "ilike", "Inventory Valuation Suspense%")], limit=1
                )
            elif kind in ("office_use", "own_company"):
                suspense_map[kind] = Account.search(
                    [("name", "=", "Owner's Current Account")], limit=1
                )
            else:
                suspense_map[kind] = self._ensure_takeon_account(
                    "Legacy Unallocated Receipts", "2.99.99.902"
                )
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
        lines = []
        parties = 0
        for line in self.line_ids:
            if line.line_state == "gl_mapped":
                account = suspense_map.get(line.suspense_kind)
                if not account:
                    raise UserError(
                        _("No GL account mapped for internal kind %s.") % line.suspense_kind
                    )
                lines.append(
                    (
                        0,
                        0,
                        {
                            "account_id": account.id,
                            "name": "Legacy %s — %s"
                            % (line.suspense_kind, (line.clean_name or "Unidentified")[:60]),
                            "debit": line.balance if line.balance > 0 else 0.0,
                            "credit": -line.balance if line.balance < 0 else 0.0,
                        },
                    )
                )
                line.line_state = "posted"
                continue
            partner = line.created_partner_id or line.matched_partner_id
            if not partner or abs(line.balance) < 0.005:
                continue
            lines.append(
                (
                    0,
                    0,
                    {
                        "account_id": ar.id if line.balance > 0 else ap.id,
                        "partner_id": partner.id,
                        "date_maturity": self.takeon_date,
                        "name": "Legacy take-on %s" % line.legacy_reference,
                        "debit": line.balance if line.balance > 0 else 0.0,
                        "credit": -line.balance if line.balance < 0 else 0.0,
                    },
                )
            )
            parties += 1
        if not lines:
            raise UserError(_("Nothing to post — no party or internal lines carry a balance."))
        net = sum(ln[2]["debit"] - ln[2]["credit"] for ln in lines)
        lines.append(
            (
                0,
                0,
                {
                    "account_id": contra.id,
                    "name": "Legacy partner-ledger take-on contra (%s, net legacy position)"
                    % (self.source_filename or self.import_ref),
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
                "ref": "%s-TAKEON" % self.import_ref,
                "narration": _(
                    "Opening balances from legacy partner ledger %s: %d parties plus "
                    "internal/suspense mappings; net legacy position on the contra account."
                )
                % (self.source_filename or "", parties),
                "line_ids": lines,
            },
            {},
            source="suspense",
            source_ref="%s wizard take-on" % self.import_ref,
        )
        self.posted_move_id = move.id
        self.state = "posted"
        self._log(
            "posted %s (%d lines, %d partner lines, net %.2f on contra %s)"
            % (move.name, len(move.line_ids), parties, net, contra.name)
        )
        return True

    def action_rollback(self):
        """Reverse the opening entry (a mirror entry through the same funnel)
        and park the batch. Parties stay — they are master data; the ledger
        position is what rolls back."""
        self.ensure_one()
        require_takeon_authority(self.env, "Rolling back a legacy take-on")
        if self.state != "posted" or not self.posted_move_id:
            raise UserError(_("Only a posted take-on can be rolled back."))
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        move = self.posted_move_id
        mirror = []
        for line in move.line_ids:
            if abs(line.balance) < 0.005:
                continue
            vals = {
                "account_id": line.account_id.id,
                "partner_id": line.partner_id.id or False,
                "date_maturity": line.date_maturity or False,
                "name": "Take-on rollback: %s" % (line.name or "")[:48],
                "debit": -line.balance if line.balance < 0 else 0.0,
                "credit": line.balance if line.balance > 0 else 0.0,
            }
            mirror.append((0, 0, vals))
        reversal, _dims = post_with_dimensions(
            self.env,
            {
                "journal_id": move.journal_id.id,
                "company_id": move.company_id.id,
                "date": fields.Date.context_today(self),
                "move_type": "entry",
                "ref": "ROLLBACK %s" % (move.ref or move.name),
                "narration": _("Rollback of legacy take-on %s.") % (move.name or ""),
                "line_ids": mirror,
            },
            {},
            source="suspense",
            source_ref="%s wizard rollback" % self.import_ref,
        )
        self.state = "rolled_back"
        self._log(
            "rolled back via mirror entry %s (parties retained as master data)" % reversal.name
        )
        return True

    @api.depends("line_ids", "line_ids.line_state")
    def _compute_counts(self):
        for batch in self:
            lines = batch.line_ids
            batch.line_count = len(lines)
            batch.linked_count = len(
                lines.filtered(
                    lambda ln: ln.line_state in ("linked", "posted") and ln.matched_partner_id
                )
            )
            batch.created_count = len(
                lines.filtered(
                    lambda ln: ln.line_state in ("created", "posted") and ln.created_partner_id
                )
            )
            batch.gl_mapped_count = len(lines.filtered(lambda ln: ln.suspense_kind))
            batch.quarantined_count = len(lines.filtered(lambda ln: ln.line_state == "quarantined"))

    @api.depends("line_ids.debit", "line_ids.credit", "line_ids.balance", "line_ids.suspense_kind")
    def _compute_totals(self):
        for batch in self:
            lines = batch.line_ids
            batch.total_debit = sum(lines.mapped("debit"))
            batch.total_credit = sum(lines.mapped("credit"))
            batch.total_balance = sum(lines.mapped("balance"))
            batch.external_balance = sum(
                lines.filtered(lambda ln: not ln.suspense_kind).mapped("balance")
            )


class FixLedgerTakeonLine(models.Model):
    _name = "fix.ledger.takeon.line"
    _description = "Legacy Partner-Ledger Take-on Line"
    _order = "batch_id, row_no"

    batch_id = fields.Many2one("fix.ledger.takeon.batch", required=True, ondelete="cascade")
    row_no = fields.Integer()
    raw_name = fields.Char()
    clean_name = fields.Char()
    legacy_code = fields.Char()
    legacy_reference = fields.Char(index=True)
    phone_norm = fields.Char()
    vintage23 = fields.Boolean(string="2023 Cohort Prefix")
    debit = fields.Monetary(currency_field="currency_id")
    credit = fields.Monetary(currency_field="currency_id")
    balance = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(related="batch_id.currency_id")
    line_state = fields.Selection(LINE_STATES, default="staged")
    suspense_kind = fields.Selection(SUSPENSE_KINDS)
    matched_partner_id = fields.Many2one("res.partner", string="Matched Party")
    created_partner_id = fields.Many2one("res.partner", string="Created Party")
    notes = fields.Char()

    def _detect_suspense(self):
        self.ensure_one()
        raw = "%s %s" % (self.raw_name or "", self.clean_name or "")
        if re.search(r"stock\s*migration", raw, re.I):
            return "stock_migration"
        if re.search(r"unidentified", raw, re.I):
            return "unidentified"
        if re.search(r"office\s*use", raw, re.I):
            return "office_use"
        if re.match(r"^1000\s*fix", (self.clean_name or ""), re.I):
            return "own_company"
        return ""

    def _build_legacy_ref(self, import_ref):
        self.ensure_one()
        if self.legacy_code:
            return "%s-%s" % (import_ref, self.legacy_code)
        if self.phone_norm:
            return "%s-M-%s" % (import_ref, self.phone_norm)
        slug = re.sub(r"[^a-z0-9]+", "-", _norm_name(self.clean_name))[:32].strip("-")
        return "%s-N-%s" % (import_ref, slug or str(self.row_no))
