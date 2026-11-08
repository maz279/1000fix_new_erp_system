# cd_party_master — governed party import (M33, report §7 steps 2-9).
#
# The real-customer cut-over loader: stage the source spreadsheet, cleanse
# per the auditable rules (legacy-code extraction, parent/branch name
# decomposition, phone/email normalisation, division mapping, quarantine),
# match against the live party master, create parties as DRAFT with their
# legacy_reference (MIG-03), bulk-decide the two-tier registration approval
# as a system-trusted cut-over path, and reconcile counts. Every rule that
# touches a row is recorded on the line; every action appends to the batch
# decision log (who, when, what).
from __future__ import annotations

import base64
import datetime
import re

from odoo import api, fields, models
from odoo.exceptions import UserError

BD_MOBILE = re.compile(r"^01[3-9]\d{8}$")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
OUTLOOK = re.compile(r"<\s*([^<>\s]+@[^<>\s]+)\s*>")
YEAR_PREFIX = re.compile(r"^\s*(2\d)\s*-\s*")

# State-column values → BD division names (res.country.state, code BD).
# The sheet mixes divisions and districts; districts fall back to their
# division so the governed address always carries a division.
DISTRICT_TO_DIVISION = {
    "cumilla": "Chattogram",
    "coxs bazar": "Chattogram",
    "cox bazar": "Chattogram",
    "noakhali": "Chattogram",
    "feni": "Chattogram",
    "bogura": "Rajshahi",
    "jashore": "Khulna",
    "dinajpur": "Rangpur",
    "sirajgonj": "Rajshahi",
    "gazipur": "Dhaka",
    "kustia": "Khulna",
    "kushtia": "Khulna",
    "barishal": "Barishal",
    "bhola": "Barishal",
}
LINE_STATES = [
    ("staged", "Staged (raw)"),
    ("validated", "Validated"),
    ("quarantined", "Quarantined"),
    ("error", "Error"),
    ("matched", "Matched existing party"),
    ("created", "Created"),
    ("linked", "Matched — legacy key attached"),
]

_SHEET_COLUMNS = {
    # sheet kind → (header→field map, class, default tag)
    "corp": {
        "Complete Name": "raw_name",
        "Mobile": "raw_phone",
        "E-mail": "raw_email",
        "Street": "raw_street",
        "State": "raw_state",
        "Country": "raw_country",
        "Tags": "raw_tag",
    },
    "stbl": {
        "Complete Name": "raw_name",
        "Phone": "raw_phone",
        "Email": "raw_email",
        "Salesperson": "raw_salesperson",
        "City": "raw_city",
        "Country": "raw_country",
        "Tag": "raw_tag",
    },
}


def _norm_name(value: str) -> str:
    s = YEAR_PREFIX.sub("", str(value or "").strip())
    s = re.sub(r"[\(\)]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _norm_phone(value) -> tuple[str, str]:
    """(normalised, note). BD mobile canonicalised; landline/international
    kept verbatim (tagged), never rejected."""
    raw = str(value or "").strip()
    digits = re.sub(r"\D", "", raw)
    if BD_MOBILE.fullmatch(digits):
        return digits, ""
    if raw.startswith("+880") or raw.startswith("880"):
        local = re.sub(r"^880?", "", digits)
        if local.startswith("1") and len(local) == 10:
            return "0" + local, "880-prefix normalised"
        return digits, "international/880 number kept as digits"
    if len(digits) in (8, 9) and digits.startswith("02"):
        return digits, "landline kept as-is"
    if 9 <= len(digits) <= 10 and digits.startswith("1"):
        return digits, "likely truncated mobile — flagged for callback"
    return digits or raw, "off-format number kept as-is"


def _norm_email(value) -> tuple[str, str]:
    raw = str(value or "").strip()
    if not raw:
        return "", ""
    m = OUTLOOK.search(raw)
    if m:
        raw = m.group(1)
    raw = raw.strip().strip(";,").replace(" ", "")
    if EMAIL.fullmatch(raw):
        return raw.lower(), "display-format parsed" if m else ""
    return "", "invalid email dropped: %s" % raw[:60]


def _split_parent_branch(name: str) -> tuple[str, str, str]:
    """'PARENT, 23-PARENT (BRANCH)' → (legacy_code, parent, branch).
    Both segments must look like names for a split to count (the QA pass
    measured 132 such rows)."""
    raw = str(name or "").strip()
    code = ""
    m = YEAR_PREFIX.match(raw)
    if m:
        code = m.group(1)
    if "," not in raw:
        return code, _norm_name(raw), ""
    left, _, right = raw.partition(",")
    parent, branch = _norm_name(left), _norm_name(right)
    # the branch usually repeats the parent prefix — drop it if so
    bp = YEAR_PREFIX.sub("", branch)
    if parent and bp.lower().startswith(parent.lower()):
        bp = bp[len(parent) :].lstrip(" -–(").rstrip(") ").strip()
    if not parent or not bp:
        return code, _norm_name(raw), ""
    return code, parent, bp


class FixPartyImportBatch(models.Model):
    _name = "fix.party.import.batch"
    _description = "Party Import Batch (M33 real-customer cut-over)"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    sheet_kind = fields.Selection(
        [("corp", "Corporate customer list"), ("stbl", "STBL & Principal list")],
        required=True,
        default="corp",
    )
    source_file = fields.Binary(string="Source Spreadsheet", attachment=True)
    source_filename = fields.Char()
    import_ref = fields.Char(
        string="Import Reference",
        required=True,
        default=lambda self: "CORP-%d" % datetime.date.today().year,
        help="MIG-03 grouping key stored with each legacy_reference",
    )
    lawful_basis = fields.Selection(
        [("contract", "Contractual necessity"), ("legal_obligation", "Legal obligation")],
        string="PDPA Lawful Basis (Act 63 of 2026)",
        required=True,
        default="contract",
        help="Legitimate interest is NOT an enumerated basis under the PDPA 2026; "
        "the import must ride on contract or legal obligation.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("staged", "Staged"),
            ("validated", "Validated"),
            ("imported", "Imported"),
            ("approved", "Registrations decided"),
            ("reconciled", "Reconciled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.party.import.line", "batch_id")
    line_count = fields.Integer(compute="_compute_counts", store=True)
    error_count = fields.Integer(compute="_compute_counts", store=True)
    quarantined_count = fields.Integer(compute="_compute_counts", store=True)
    matched_count = fields.Integer(compute="_compute_counts", store=True)
    created_count = fields.Integer(compute="_compute_counts", store=True)
    hierarchy_count = fields.Integer(compute="_compute_counts", store=True)
    decision_log = fields.Text(readonly=True)

    @api.depends("company_id", "create_date", "sheet_kind")
    def _compute_name(self):
        kinds = {"corp": "Corporate list", "stbl": "STBL & Principal list"}
        for batch in self:
            when = (batch.create_date or fields.Datetime.now()).strftime("%Y-%m-%d")
            batch.name = "Party import — %s — %s" % (kinds.get(batch.sheet_kind, "?"), when)

    @api.depends("line_ids.line_state", "line_ids.created_partner_id", "line_ids.parent_partner_id")
    def _compute_counts(self):
        for batch in self:
            lines = batch.line_ids
            batch.line_count = len(lines)
            batch.error_count = len(lines.filtered(lambda ln: ln.line_state == "error"))
            batch.quarantined_count = len(lines.filtered(lambda ln: ln.line_state == "quarantined"))
            batch.matched_count = len(
                lines.filtered(lambda ln: ln.line_state in ("matched", "linked"))
            )
            batch.created_count = len(lines.filtered(lambda ln: ln.created_partner_id))
            batch.hierarchy_count = len(lines.filtered(lambda ln: ln.parent_partner_id))

    def _log(self, message: str):
        self.ensure_one()
        stamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M")
        who = self.env.user.name or "?"
        self.decision_log = "%s[%s] %s: %s\n" % (
            self.decision_log or "",
            stamp,
            who,
            message,
        )

    # ------------------------------------------------------------------ stage
    def action_stage(self):
        """Parse the spreadsheet into staged lines with the raw values — no
        transformation yet, one line per source row (auditability)."""
        self.ensure_one()
        if not self.source_file:
            raise UserError("Attach the source spreadsheet first.")
        try:
            from openpyxl import load_workbook
        except ImportError as exc:  # pragma: no cover — odoo ships openpyxl
            raise UserError("openpyxl unavailable: %s" % exc) from exc
        import io

        wb = load_workbook(
            io.BytesIO(base64.b64decode(self.source_file)), read_only=True, data_only=True
        )
        # pick the sheet FOR THE CHOSEN LAYOUT — the workbook has two sheets
        # (Corp first, STBL and Principal second) and the 2026-11-08 trial
        # caught both batches staging sheet 1.
        wanted = "corp" if self.sheet_kind == "corp" else "stbl"
        ws = next(
            (s for s in wb.worksheets if wanted in s.title.lower().replace("&", "and")),
            wb.worksheets[0] if self.sheet_kind == "corp" else wb.worksheets[-1],
        )
        colmap = _SHEET_COLUMNS[self.sheet_kind]
        header = None
        staged = []
        for row in ws.iter_rows(values_only=True):
            if header is None:
                cells = [str(c or "").strip() for c in row]
                if "Complete Name" in cells:
                    header = cells
                continue
            vals = {}
            for i, h in enumerate(header):
                if h in colmap and i < len(row):
                    vals[colmap[h]] = row[i]
            if not (vals.get("raw_name") or "").strip():
                continue  # fully blank row
            staged.append((0, 0, {**vals, "row_no": len(staged) + 2}))
        if not staged:
            raise UserError("No rows staged — is the sheet the %s layout?" % self.sheet_kind)
        self.line_ids.unlink()
        self.line_ids = staged
        self._log(
            "staged %d rows from %s (sheet %r)" % (len(staged), self.source_filename, ws.title)
        )
        self.state = "staged"
        return True

    # -------------------------------------------------------------- validate
    def action_validate(self):
        """Apply every cleansing rule, resolve divisions and salespersons,
        and match each line against the live party master."""
        self.ensure_one()
        if self.state == "draft":
            raise UserError("Stage the spreadsheet first.")
        Partner = self.env["res.partner"]
        State = self.env["res.country.state"]
        User = self.env["res.users"]
        bd = self.env.ref("base.bd", raise_if_not_found=False) or self.env["res.country"].search(
            [("code", "=", "BD")], limit=1
        )
        divisions = {s.name.lower(): s for s in State.search([("country_id", "=", bd.id)])}
        users_by_name = {u.name.strip().lower(): u for u in User.search([])}
        # existing parties by normalised name and by phone (exact)
        existing = Partner.search(["|", ("name", "!=", False), ("phone", "!=", False)], limit=60000)
        by_name, by_phone = {}, {}
        for p in existing:
            by_name.setdefault(_norm_name(p.name), p)
            key = re.sub(r"\D", "", p.phone or "")
            if key:
                by_phone.setdefault(key, p)

        for line in self.line_ids:
            notes = []
            code, parent, branch = _split_parent_branch(line.raw_name)
            if code:
                line.legacy_reference = "%s-%s" % (self.import_ref, code)
            else:
                # no year code in the source (two vintages): the normalised
                # name is the permanent key so every row stays MIG-3-traceable
                slug = re.sub(r"[^A-Z0-9]+", "-", _norm_name(line.raw_name).upper()).strip("-")[:24]
                line.legacy_reference = "%s-%s" % (self.import_ref, slug) if slug else ""
            line.clean_name = branch or parent
            line.parent_name = (branch and parent) or ""
            phone, note = _norm_phone(line.raw_phone)
            line.phone_norm = phone
            if note:
                notes.append(note)
            if re.fullmatch(r"\d*0{6,}", phone or ""):
                notes.append("placeholder number quarantined")
            email, note = _norm_email(line.raw_email)
            line.email_norm = email
            if note:
                notes.append(note)
            # division: direct hit, else district fallback
            raw_state = str(line.raw_state or "").strip().lower().rstrip("(bd)").strip()
            line.district_raw = raw_state if raw_state not in divisions else ""
            division = divisions.get(raw_state)
            if not division and raw_state in DISTRICT_TO_DIVISION:
                division = divisions.get(DISTRICT_TO_DIVISION[raw_state].lower())
                notes.append("district %r mapped to division %s" % (raw_state, division.name))
            line.division_id = division
            if not division and line.raw_state:
                notes.append("unmapped state %r kept as district" % raw_state)
            if line.raw_salesperson:
                user = users_by_name.get(str(line.raw_salesperson).strip().lower())
                line.user_id = user
                if not user:
                    notes.append("salesperson not a user — left unassigned")
            # match: normalised exact name, or exact phone — against the live
            # master AND the earlier lines of this batch (the source file has
            # intra-file duplicates: MSF two-vintage, repeated branch rows).
            # A BRANCH row never matches on its bare branch fragment ("KHULNA"
            # matched an unrelated party in the 2026-11-08 debug) — only the
            # full raw name counts for branches.
            match = by_name.get(_norm_name(line.raw_name))
            if not match and not line.parent_name:
                match = by_name.get(_norm_name(line.clean_name))
            if not match and phone:
                match = by_phone.get(phone)
            line.matched_partner_id = False
            line.dup_of_line_id = False
            if match is not None and match._name == "res.partner":
                line.matched_partner_id = match
                line.line_state = "matched"
                notes.append("matched existing party #%d" % match.id)
            elif match is not None and match._name == "fix.party.import.line":
                # intra-batch duplicate of an earlier line — no second party
                line.dup_of_line_id = match
                line.line_state = "matched"
                notes.append("duplicate within batch of row %d" % match.row_no)
            elif not line.clean_name:
                line.line_state = "error"
                notes.append("no usable name")
            elif any("quarantined" in n for n in notes):
                line.line_state = "quarantined"
            else:
                line.line_state = "validated"
            line.notes = "; ".join(notes)
            # register this line for intra-batch duplicate detection
            if line.line_state == "validated":
                by_name.setdefault(_norm_name(line.raw_name), line)
                by_name.setdefault(_norm_name(line.clean_name), line)
                if phone:
                    by_phone.setdefault(phone, line)
        self._log(
            "validated %d lines: %d matched, %d quarantined"
            % (
                len(self.line_ids),
                len(self.line_ids.filtered(lambda ln: ln.line_state == "matched")),
                len(self.line_ids.filtered(lambda ln: ln.line_state == "quarantined")),
            )
        )
        self.state = "validated"
        return True

    # --------------------------------------------------------------- import
    def action_import(self):
        """Create parties as DRAFT (the lifecycle guard's only legal birth
        state) with legacy_reference, tags, division and the PDPA stamp;
        branches attach to their parent via fix.party.hierarchy. Matched
        lines get the legacy key attached instead of a duplicate."""
        self.ensure_one()
        if self.state != "validated":
            raise UserError("Validate the batch first.")
        Partner = self.env["res.partner"]
        Category = self.env["res.partner.category"]
        Hierarchy = self.env["fix.party.hierarchy"]
        bd = self.env.ref("base.bd", raise_if_not_found=False) or self.env["res.country"].search(
            [("code", "=", "BD")], limit=1
        )
        party_class = "corporate" if self.sheet_kind == "corp" else "dealer"
        # tags: create-if-missing per distinct source tag
        tag_cache = {}

        def tag_ids(tag_label):
            if not tag_label:
                return []
            if tag_label not in tag_cache:
                cat = Category.search([("name", "=", tag_label)], limit=1)
                if not cat:
                    cat = Category.create({"name": tag_label})
                tag_cache[tag_label] = cat
            return [(4, tag_cache[tag_label].id)]

        # pass 1: parents + plain rows
        for line in self.line_ids.filtered(lambda ln: not ln.parent_name):
            if line.line_state == "matched":
                self._attach_legacy(line)
                continue
            if line.line_state != "validated":
                continue
            line.created_partner_id = Partner.create(
                {
                    "name": line.clean_name,
                    "is_company": True,
                    "party_class": party_class,
                    "legacy_reference": line.legacy_reference or None,
                    "street": line.raw_street or False,
                    "state_id": line.division_id.id or False,
                    "country_id": bd.id,
                    "phone": line.phone_norm or False,
                    "email": line.email_norm or False,
                    "category_id": tag_ids(line.raw_tag),
                    "user_id": line.user_id.id or False,
                    "street2": line.district_raw or False,
                    "city": line.raw_city or False,
                }
            )
            line.line_state = "created"
            self._pdpa_stamp(line.created_partner_id)
        # pass 2: branches onto their parents (by normalised parent name)
        all_lines = self.line_ids
        for line in self.line_ids.filtered(lambda ln: ln.parent_name):
            if line.line_state != "validated":
                continue
            parent = all_lines.filtered(
                lambda ln, me=line: not ln.parent_name
                and _norm_name(ln.clean_name) == _norm_name(me.parent_name)
                and ln.created_partner_id
            )[:1].created_partner_id
            if not parent:
                # the parent row may itself be matched or absent — resolve live
                parent = Partner.search([("name", "ilike", line.parent_name)], limit=1)
            line.created_partner_id = Partner.create(
                {
                    "name": line.clean_name,
                    "is_company": True,
                    "party_class": party_class,
                    "legacy_reference": line.legacy_reference or None,
                    "street": line.raw_street or False,
                    "state_id": line.division_id.id or False,
                    "country_id": bd.id,
                    "phone": line.phone_norm or False,
                    "email": line.email_norm or False,
                    "category_id": tag_ids(line.raw_tag),
                    "street2": line.district_raw or False,
                    "city": line.raw_city or False,
                }
            )
            if parent:
                Hierarchy.create(
                    {
                        "parent_id": parent.id,
                        "child_id": line.created_partner_id.id,
                        "relation_type": "corporate",
                    }
                )
                line.parent_partner_id = parent
            line.line_state = "created"
            self._pdpa_stamp(line.created_partner_id)
        self._log(
            "imported: %d created, %d hierarchy links, %d matched lines keyed"
            % (
                len(self.line_ids.filtered(lambda ln: ln.created_partner_id)),
                len(self.line_ids.filtered(lambda ln: ln.parent_partner_id)),
                len(self.line_ids.filtered(lambda ln: ln.line_state == "linked")),
            )
        )
        self.state = "imported"
        return True

    def _attach_legacy(self, line):
        """A matched party gets the legacy key (idempotent re-runs). An
        intra-batch duplicate links to the party its source line created."""
        partner = line.matched_partner_id
        if not partner and line.dup_of_line_id:
            partner = line.dup_of_line_id.created_partner_id
            line.matched_partner_id = partner
        if partner and not partner.legacy_reference:
            partner.sudo().write({"legacy_reference": line.legacy_reference or None})
        line.line_state = "linked"

    def _pdpa_stamp(self, partner):
        partner.message_post(
            body=(
                "Imported by the M33 cut-over loader under PDPA Act 63 of 2026 — "
                "lawful basis: %s. Source: %s. Marketing consent NOT granted by "
                "import (no consent manufactured); service contact only."
                % (self.lawful_basis, self.source_filename or self.import_ref)
            )
        )

    # ---------------------------------------------------- bulk registration
    def action_decide_registrations(self):
        """Two-tier registration for every imported corporate/dealer party.
        Creating a registered-class party AUTO-OPENS its registration approval
        (res.partner._fix_open_registration), so this decides the EXISTING
        approval as a system-trusted cut-over path — the inbox routing and its
        SoD remain the human path; the operator running the loader is recorded
        on every step here and in the batch decision log."""
        self.ensure_one()
        if self.state != "imported":
            raise UserError("Import the batch first.")
        Approval = self.env["fix.registration.approval"]
        decided = skipped = 0
        for line in self.line_ids.filtered(lambda ln: ln.created_partner_id):
            partner = line.created_partner_id
            if partner.party_status not in ("draft", "pending_approval"):
                skipped += 1
                continue
            approval = Approval.search([("partner_id", "=", partner.id)], order="id desc", limit=1)
            if not approval or approval._fully_approved():
                skipped += 1
                continue
            approval._guarded().write(
                {
                    "lm_state": "approved",
                    "lm_decided_by": self.env.user.id,
                    "lm_decided_at": fields.Datetime.now(),
                    "admin_state": "approved",
                    "admin_decided_by": self.env.user.id,
                    "admin_decided_at": fields.Datetime.now(),
                }
            )
            approval._activate_if_complete()
            decided += 1
        self._log(
            "registrations decided for %d parties (%d already active/decided)" % (decided, skipped)
        )
        self.state = "approved"
        self.action_assign_roles()
        return True

    def action_assign_roles(self):
        """Give every created party its classification ROLE (M33: one party,
        many roles — never masters). Corp list → customer role; STBL/
        Principal list → brand-partner role. Idempotent, and only for
        usable parties (an active role requires an active party)."""
        self.ensure_one()
        Role = self.env["fix.party.role"]
        role_type = "customer" if self.sheet_kind == "corp" else "brand_partner"
        created = skipped = 0
        for line in self.line_ids.filtered(lambda ln: ln.created_partner_id):
            partner = line.created_partner_id
            if Role.search_count([("partner_id", "=", partner.id), ("role_type", "=", role_type)]):
                skipped += 1
                continue
            if partner.party_status != "active":
                skipped += 1
                continue
            Role.create(
                {
                    "partner_id": partner.id,
                    "role_type": role_type,
                    "role_status": "active",
                }
            )
            created += 1
        self._log("roles assigned: %d %s (%d skipped)" % (created, role_type, skipped))
        return True

    # ------------------------------------------------------------- rollback
    def action_rollback(self):
        """Reverse THIS batch's creations — the cut-over's rollback lever
        (report §7). A created party is removable only while nothing
        references it (documents make the party history and it is kept);
        approvals and hierarchy links created with it go first. Matched/
        linked parties stay (they pre-existed); the legacy keys attached to
        them by this batch are cleared."""
        self.ensure_one()
        Approval = self.env["fix.registration.approval"]
        Hierarchy = self.env["fix.party.hierarchy"]
        referencing = [
            ("fix.service.order", "customer_id"),
            ("account.move", "partner_id"),
            ("fix.contract", "partner_id"),
            ("fix.subscription", "partner_id"),
            ("fix.vendor.invoice", "partner_id"),
        ]
        removed = kept = 0
        for line in self.line_ids.filtered(lambda ln: ln.created_partner_id):
            partner = line.created_partner_id
            referenced = False
            for model, field in referencing:
                try:
                    if self.env[model].search_count([(field, "=", partner.id)]):
                        referenced = True
                        break
                except Exception:  # noqa: S112 — absent model = nothing references
                    continue
            if referenced:
                kept += 1
                continue
            Approval.search([("partner_id", "=", partner.id)]).unlink()
            Hierarchy.search(
                ["|", ("parent_id", "=", partner.id), ("child_id", "=", partner.id)]
            ).unlink()
            partner.unlink()
            removed += 1
        # matched parties pre-existed: only undo the legacy key we attached
        for line in self.line_ids.filtered(lambda ln: ln.matched_partner_id):
            partner = line.matched_partner_id
            if partner.legacy_reference and partner.legacy_reference.startswith(self.import_ref):
                partner.sudo().write({"legacy_reference": False})
        self._log("rollback: %d created parties removed, %d kept (referenced)" % (removed, kept))
        self.state = "validated"
        return True

    # ---------------------------------------------------------- reconcile
    def action_reconcile(self) -> dict:
        """Counts by state/tag/division against the source — the migration's
        own audit artefact."""
        self.ensure_one()
        lines = self.line_ids
        by_state = {}
        for state, _label in LINE_STATES:
            n = len(lines.filtered(lambda ln, s=state: ln.line_state == s))
            if n:
                by_state[state] = n
        by_tag = {}
        for line in lines:
            by_tag[line.raw_tag or "(none)"] = by_tag.get(line.raw_tag or "(none)", 0) + 1
        by_division = {}
        for line in lines.filtered(lambda ln: ln.division_id):
            by_division[line.division_id.name] = by_division.get(line.division_id.name, 0) + 1
        summary = {
            "source_rows": len(lines),
            "by_state": by_state,
            "by_tag": by_tag,
            "by_division": by_division,
            "unmapped_state_rows": len(
                lines.filtered(lambda ln: ln.raw_state and not ln.division_id)
            ),
            "created": len(lines.filtered(lambda ln: ln.created_partner_id)),
            "matched_or_linked": len(
                lines.filtered(lambda ln: ln.line_state in ("matched", "linked"))
            ),
        }
        self._log("reconciled: %s" % summary)
        self.state = "reconciled"
        return summary
