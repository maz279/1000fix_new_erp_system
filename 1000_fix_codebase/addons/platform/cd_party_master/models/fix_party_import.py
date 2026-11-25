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
import hashlib
import re

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

# The loader activates parties and stamps both registration tiers under sudo,
# so only system code or the 1000FiX registration administrator runs it
# (2026-11-10 audit: every internal user could).
LOADER_GROUP = "cd_party_master.group_party_registration_admin"

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
    # 1000 FiX vendor ledger export (2026-11-08 readiness report §2): a
    # single-sheet legacy res.partner dump. Address IS the street column;
    # PAN/CIN carry the (mixed-validity) statutory identifiers; Customer
    # Area is a branch/area token kept for stewardship, not an OU mapping.
    "vendor": {
        "Complete Name": "raw_name",
        "Phone": "raw_phone",
        "Email": "raw_email",
        "Address": "raw_street",
        "City": "raw_city",
        "Country": "raw_country",
        "Salesperson": "raw_salesperson",
        "Customer Area": "raw_area",
        "PAN": "raw_pan",
        "CIN": "raw_cin",
    },
}

# The legacy system exports ONE res.partner dump layout under three filters
# (2026-11-10 audit): "vendor.xlsx" is in fact the full contact list (every
# row of customer.xlsx is in it), so loading it whole on the vendor lane made
# 23,824 walk-in customers "vendors" with supplier-register rows. The layout
# is therefore shared by three lanes that differ only in the ROLE they grant:
#   vendor   → vendor role (+ M42 supplier register, cd_vendor_portal)
#   customer → customer role
#   contact  → no role (a party the business knows, with no trading role yet)
PARTNER_DUMP_KINDS = ("vendor", "customer", "contact")
_SHEET_COLUMNS["customer"] = _SHEET_COLUMNS["vendor"]
_SHEET_COLUMNS["contact"] = _SHEET_COLUMNS["vendor"]
_DUMP_LABEL = {"vendor": "Vendor", "customer": "Customer", "contact": "Contact"}
ROLE_BY_KIND = {
    "corp": "customer",
    "stbl": "brand_partner",
    "vendor": "vendor",
    "customer": "customer",
    "contact": None,
}

# Vendor-ledger classification (report §2.2): the file mixes formal
# companies with a very large population of individual payees (honorific
# names, single tokens, phone-as-name). A company-shaped name becomes a
# dealer-class party; everything else is an individual. Deterministic and
# recorded per line — stewards can re-classify later.
_VENDOR_COMPANY_RE = re.compile(
    r"\b(ltd|limited|pvt|private|llc|inc|corp|corporation|company|enterprises?|"
    r"traders?|trading|shops?|stores?|agenc(?:y|ies)|distribut(?:or|ors|orship)|"
    r"suppliers?|dealers?|refrigeration|electronics?|electricals?|engineering|"
    r"technolog(?:y|ies)|techno|computers?|mobile|telecom|services?|servicing|"
    r"cent(?:er|re)s?|points?|works?|workshops?|houses?|syndicate|associates|"
    r"group|authority|hospitals?|clinics?|diagnostics?|schools?|colleges?|"
    r"universit(?:y|ies)|institutes?|banks?|insurance|foundations?|"
    r"organizations?|organisations?|international|imports?|exports?|"
    r"industr(?:y|ies))\b|\)$",
    re.I,
)

# Vendor-ledger operational noise that is not a payee at all (report §2.2):
# call attempts, product strings, self-references and the stock-migration
# counter-account. Quarantined with the reason, never imported.
_VENDOR_NOISE_RE = re.compile(
    r"no answer|not reachable|wrong number|didn.?t pick|switch off"
    r"|stock migration|\bDDR\d\b|\bGB\b|®|1000fix services",
    re.I,
)

# City/Area tokens → BD division for the vendor sheet (its geography column
# is City, not State). Extends the district map with the file's measured
# area spellings (report §2.1); unknown tokens stay as city text.
VENDOR_CITY_TO_DIVISION = {
    "uttara": "Dhaka",
    "mirpur": "Dhaka",
    "gulshan": "Dhaka",
    "banani": "Dhaka",
    "dhanmondi": "Dhaka",
    "narayanganj": "Dhaka",
    "gazipur": "Dhaka",
    "bogura": "Rajshahi",
    "cox's bazar": "Chattogram",
    "chattogram": "Chattogram",
    "ctg": "Chattogram",
    "mymensingh": "Mymensingh",
}


def _vendor_party_class(clean_name: str) -> tuple[bool, str]:
    """(is_company, party_class) for a vendor-ledger name — dealer for
    company-shaped names, individual for the payee mass."""
    if _VENDOR_COMPANY_RE.search(clean_name or ""):
        return True, "dealer"
    return False, "individual"


def _vendor_tax_ids(raw_pan, raw_cin) -> tuple[str, list]:
    """Classify the PAN/CIN columns (report §2.1 / gap V10) → (tin, notes).

    A 12-digit PAN is an e-TIN (the only identifier that satisfies the
    fix.vendor.tax.profile constraint). 2026-prefixed 10–11-digit CINs are
    new-vintage BINs held back for verification (the profile's BIN field is
    strictly 13-digit); 8-digit CINs are legacy system ids, not tax ids.
    """
    notes = []
    tin = ""
    pan = str(raw_pan or "").strip()
    cin = str(raw_cin or "").strip()
    if re.fullmatch(r"\d{12}", pan):
        tin = pan
        notes.append("e-TIN classified from PAN")
    elif pan:
        notes.append("PAN not a 12-digit e-TIN — kept as raw only")
    if re.fullmatch(r"2026\d{6,9}", cin):
        notes.append("2026-vintage BIN pending verification — not auto-loaded")
    elif re.fullmatch(r"\d{8}", cin):
        notes.append("CIN is a legacy system id, not a tax identifier")
    elif cin:
        notes.append("CIN unrecognised format — kept as raw only")
    return tin, notes


def _norm_name(value: str) -> str:
    s = YEAR_PREFIX.sub("", str(value or "").strip())
    s = re.sub(r"[\(\)]", " ", s)
    s = re.sub(r"\s+,", ",", s)  # "Service , Bangladesh" → "Service, Bangladesh"
    return re.sub(r"\s+", " ", s).strip()


def _loose_name(value: str) -> str:
    """Case/punctuation-insensitive form for fallback matching. The 2026-11-09
    discovery: a parallel `partner_ledger.xlsx` import created 1,747 vendor
    parties whose branch markers are DASH-form ('WV — COX'S BAZAR') while this
    ledger spells them paren-form — the exact key misses, the loose key hits."""
    return re.sub(r"[^a-z0-9]", "", _norm_name(value).lower())


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


def _split_parent_branch(name: str) -> tuple[str, str, str, str]:
    """'23-PARENT, 23-PARENT (BRANCH)' → (legacy_code, full_name, parent, branch).

    The FULL cleaned name is always the record's display name — a comma in a
    source name is usually just part of it ('Aga Khan Education Service,
    Bangladesh', 'icddr,b'); it signals a PARENT→BRANCH hierarchy only when
    the right segment repeats the parent. The 2026-11-08 audit caught 125
    imported records named after their bare branch fragment ('Bangladesh',
    'Feni', 'b') because the first cut decomposed every comma."""
    raw = str(name or "").strip()
    code = ""
    m = YEAR_PREFIX.match(raw)
    if m:
        code = m.group(1)
    if "," not in raw:
        return code, _norm_name(raw), "", ""
    left, _, right = raw.partition(",")
    parent, branch = _norm_name(left), _norm_name(right)
    bp = YEAR_PREFIX.sub("", branch)
    # a real parent→branch row ONLY when the right segment repeats the
    # parent ("WV, WV (KHULNA)"); any other comma is part of the name
    if parent and bp.lower().startswith(parent.lower()):
        tail = bp[len(parent) :].lstrip(" -–(").rstrip(") ").strip()
        if tail:
            return code, "%s — %s" % (parent, tail), parent, tail
    return code, _norm_name(raw), "", ""


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
        [
            ("corp", "Corporate customer list"),
            ("stbl", "STBL & Principal list"),
            ("vendor", "Vendor ledger list (supplier master)"),
            ("customer", "Customer list (legacy partner dump)"),
            ("contact", "Contact list (legacy partner dump, no role)"),
        ],
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
        kinds = {
            "corp": "Corporate list",
            "stbl": "STBL & Principal list",
            "vendor": "Vendor ledger",
            "customer": "Customer list",
            "contact": "Contact list",
        }
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

    def _fix_import_check_authority(self):
        """Refuse a person who is not a registration administrator. The
        cut-over scripts run as the superuser and pass, as trusted code does
        everywhere else in M33."""
        if self.env.su or self.env.user.has_group(LOADER_GROUP):
            return
        raise AccessError(
            "The party cut-over loader creates and activates parties and decides their "
            "registrations: it needs the '%s' group, which %s does not hold."
            % (self.env.ref(LOADER_GROUP).sudo().name, self.env.user.name)
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
        # caught both batches staging sheet 1. The vendor ledger is a
        # single-sheet export ("Sheet1"), so the first worksheet is it.
        if self.sheet_kind in PARTNER_DUMP_KINDS:
            ws = wb.worksheets[0]
            colmap = _SHEET_COLUMNS["vendor"]
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
                raise UserError("No rows staged — is the sheet the legacy partner-dump layout?")
            self.line_ids.unlink()
            self.line_ids = staged
            self._log(
                "staged %d rows from %s (sheet %r)" % (len(staged), self.source_filename, ws.title)
            )
            self.state = "staged"
            return True
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
        by_name, by_phone, by_loose = {}, {}, {}
        for p in existing:
            by_name.setdefault(_norm_name(p.name), p)
            key = re.sub(r"\D", "", p.phone or "")
            if key:
                by_phone.setdefault(key, p)
            loose = _loose_name(p.name)
            if len(loose) >= 6:
                by_loose.setdefault(loose, p)

        for line in self.line_ids:
            # single write per line (26,680-row vendor ledger: per-field
            # assignment would mean ~10 UPDATEs per row)
            vals = {}
            notes = []
            is_vendor = self.sheet_kind in PARTNER_DUMP_KINDS
            # vendor source-fidelity repairs (report §7A step 1, measured in
            # the file): the ledger carries phone numbers AS names (2,496
            # rows), phone numbers in the email column, and the gamil.com
            # typo domain — repaired here where every rule is noted per line
            match_name = line.raw_name
            src_phone = line.raw_phone
            src_email = line.raw_email
            if is_vendor:
                vendor_name = str(line.raw_name or "").strip()
                phone_head = re.match(r"^(01\d{9})\s+(.+)$", vendor_name)
                if phone_head:
                    vendor_name = phone_head.group(2).strip()
                    if not str(line.raw_phone or "").strip():
                        src_phone = phone_head.group(1)
                        notes.append("phone recovered from name prefix")
                    match_name = vendor_name
                elif re.fullmatch(r"01\d{9}", vendor_name):
                    if not str(line.raw_phone or "").strip():
                        src_phone = vendor_name
                    vendor_name = "%s %s" % (_DUMP_LABEL[self.sheet_kind], vendor_name)
                    notes.append("phone-only name titled")
                    match_name = vendor_name
                if src_email and not EMAIL.fullmatch(str(src_email).strip()):
                    stripped = str(src_email).strip()
                    if re.fullmatch(r"01\d{9}", stripped):
                        if not str(src_phone or "").strip():
                            src_phone = stripped
                            notes.append("phone rescued from email column")
                        src_email = ""
            code, full_name, parent, branch = _split_parent_branch(
                match_name if is_vendor else line.raw_name
            )
            # the year code alone is NOT unique (every corp row shares '23')
            # — the R-12 uniqueness guard rejects key collisions. The key is
            # code + name slug: unique per source row, still traceable to
            # the vintage, and stable across re-runs. The slug is built from
            # the DECOMPOSED full name; when truncation would cut it (a
            # parent and its branch share a long prefix), a digest tail
            # keeps the key unique.
            slug = re.sub(r"[^A-Z0-9]+", "-", _norm_name(full_name).upper()).strip("-")
            if len(slug) > 40:
                slug = "%s-%s" % (
                    slug[:40],
                    hashlib.sha256(slug.encode()).hexdigest()[:6].upper(),
                )
            if code and not is_vendor and slug:
                vals["legacy_reference"] = "%s-%s-%s" % (self.import_ref, code, slug)
            else:
                # no year code in the source (two vintages) — or the vendor
                # ledger, whose `23-` rows are the SAME parties as their
                # un-prefixed twins: the normalised-name slug is the permanent
                # key, so both vintages collapse onto one party (MIG-03)
                vals["legacy_reference"] = "%s-%s" % (self.import_ref, slug) if slug else ""
            # the record's name is ALWAYS the full cleaned source name; the
            # comma split only ever signals a parent→branch hierarchy
            vals["clean_name"] = full_name
            vals["parent_name"] = (branch and parent) or ""
            phone, note = _norm_phone(src_phone)
            if phone and not re.search(r"\d", phone):
                # a person's name / text in the phone column (vendor ledger
                # §2.1) — never written onto the party
                notes.append("non-numeric phone dropped: %s" % phone[:40])
                phone = ""
            vals["phone_norm"] = phone
            if note:
                notes.append(note)
            if re.fullmatch(r"\d*0{6,}", phone or ""):
                notes.append("placeholder number quarantined")
            email, note = _norm_email(src_email)
            vals["email_norm"] = email
            if note:
                notes.append(note)
            if is_vendor:
                # the gamil.com typo domain (63 measured rows) — repaired,
                # never silently dropped (it passes the format check, so the
                # repair must inspect the domain, not only the dropped ones)
                fixed = ""
                if vals["email_norm"] and vals["email_norm"].endswith("@gamil.com"):
                    fixed = vals["email_norm"].replace("gamil.com", "gmail.com")
                elif not vals["email_norm"] and src_email:
                    candidate = str(src_email).strip().lower().replace("gamil.com", "gmail.com")
                    if candidate.endswith("@gmail.com") and EMAIL.fullmatch(candidate):
                        fixed = candidate
                if fixed:
                    vals["email_norm"] = fixed
                    notes.append("gamil.com typo repaired")
            if is_vendor:
                # --- vendor-ledger rules (readiness report §7A step 1) ---
                if _VENDOR_NOISE_RE.search(str(line.raw_name or "")):
                    notes.append("operational noise / internal reference quarantined — not a payee")
                if email.endswith("@1000fix.com"):
                    notes.append("internal staff payee quarantined — route via employee advance")
                tin, tax_notes = _vendor_tax_ids(line.raw_pan, line.raw_cin)
                vals["tax_tin"] = tin
                notes.extend(tax_notes)
                _company_shape, party_klass = _vendor_party_class(full_name)
                notes.append("vendor class: %s" % party_klass)
                # geography comes from the City column (no State in this sheet)
                geo = str(line.raw_city or "").strip().lower().rstrip("(bd)").strip()
            else:
                party_klass = None
                geo = str(line.raw_state or "").strip().lower().rstrip("(bd)").strip()
            vals["district_raw"] = geo if geo not in divisions else ""
            division = divisions.get(geo)
            if not division and geo in DISTRICT_TO_DIVISION:
                division = divisions.get(DISTRICT_TO_DIVISION[geo].lower())
                notes.append("district %r mapped to division %s" % (geo, division.name))
            if not division and is_vendor and geo in VENDOR_CITY_TO_DIVISION:
                division = divisions.get(VENDOR_CITY_TO_DIVISION[geo].lower())
                if division:
                    notes.append("city %r mapped to division %s" % (geo, division.name))
            vals["division_id"] = division.id if division else False
            if not division and geo and not is_vendor:
                notes.append("unmapped state %r kept as district" % geo)
            if line.raw_salesperson:
                user = users_by_name.get(str(line.raw_salesperson).strip().lower())
                vals["user_id"] = user.id if user else False
                if not user:
                    notes.append("salesperson not a user — left unassigned")
            # match: normalised exact name, or exact phone — against the live
            # master AND the earlier lines of this batch (the source file has
            # intra-file duplicates: MSF two-vintage, repeated branch rows).
            # A BRANCH row never matches on its bare branch fragment ("KHULNA"
            # matched an unrelated party in the 2026-11-08 debug) — only the
            # full raw name counts for branches.
            match = by_name.get(_norm_name(match_name))
            if not match and not vals["parent_name"]:
                match = by_name.get(_norm_name(vals["clean_name"]))
            if not match and phone:
                match = by_phone.get(phone)
            if not match:
                loose = _loose_name(match_name)
                if len(loose) >= 6:
                    match = by_loose.get(loose)
                    if match is not None:
                        notes.append("loose-name matched existing party #%d" % match.id)
            vals["matched_partner_id"] = False
            vals["dup_of_line_id"] = False
            if match is not None and match._name == "res.partner":
                vals["matched_partner_id"] = match.id
                vals["line_state"] = "matched"
                notes.append("matched existing party #%d" % match.id)
            elif match is not None and match._name == "fix.party.import.line":
                # intra-batch duplicate of an earlier line — no second party
                vals["dup_of_line_id"] = match.id
                vals["line_state"] = "matched"
                notes.append("duplicate within batch of row %d" % match.row_no)
            elif not vals["clean_name"]:
                vals["line_state"] = "error"
                notes.append("no usable name")
            elif any("quarantined" in n for n in notes):
                vals["line_state"] = "quarantined"
            else:
                vals["line_state"] = "validated"
            vals["notes"] = "; ".join(notes)
            line.write(vals)
            # register this line for intra-batch duplicate detection
            if vals["line_state"] == "validated":
                by_name.setdefault(_norm_name(match_name), line)
                by_name.setdefault(_norm_name(vals["clean_name"]), line)
                loose = _loose_name(match_name)
                if len(loose) >= 6:
                    by_loose.setdefault(loose, line)
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
        self._fix_import_check_authority()
        if self.state != "validated":
            raise UserError("Validate the batch first.")
        Partner = self.env["res.partner"]
        Category = self.env["res.partner.category"]
        Hierarchy = self.env["fix.party.hierarchy"]
        bd = self.env.ref("base.bd", raise_if_not_found=False) or self.env["res.country"].search(
            [("code", "=", "BD")], limit=1
        )
        party_class = "corporate" if self.sheet_kind == "corp" else "dealer"

        def _birth(line_or_name):
            """(is_company, party_class) for a party's birth — per-line for
            the vendor ledger (company-shaped names → dealer, the payee mass
            → individual), uniform for the customer sheets."""
            if self.sheet_kind in PARTNER_DUMP_KINDS:
                name = (
                    line_or_name.clean_name if hasattr(line_or_name, "clean_name") else line_or_name
                )
                return _vendor_party_class(name)
            return True, party_class

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

        # R-12 (unique legacy_reference) vs the real ledger: case-variant
        # names ('MANIK' vs 'Manik') are DIFFERENT parties to the
        # case-sensitive matcher but slug to the SAME uppercase key — the
        # import uniquifies each key deterministically (-2, -3, ...) against
        # both the live master and this batch's earlier creations
        used_refs = set(
            Partner.search([("legacy_reference", "!=", False)]).mapped("legacy_reference")
        )

        def unique_ref(line):
            ref = line.legacy_reference
            if not ref or ref not in used_refs:
                if ref:
                    used_refs.add(ref)
                return ref
            n = 2
            while "%s-%d" % (ref, n) in used_refs:
                n += 1
            candidate = "%s-%d" % (ref, n)
            used_refs.add(candidate)
            line.legacy_reference = candidate
            return candidate

        # pass 1: parents + plain rows
        for line in self.line_ids.filtered(lambda ln: not ln.parent_name):
            if line.line_state == "matched":
                self._attach_legacy(line)
                continue
            if line.line_state != "validated":
                continue
            is_co, pclass = _birth(line)
            line.created_partner_id = Partner.create(
                {
                    "name": line.clean_name,
                    "is_company": is_co,
                    "party_class": pclass,
                    "legacy_reference": unique_ref(line) or None,
                    "company_id": self.company_id.id,
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
            if line.line_state == "matched":
                # a matched BRANCH line never enters pass 1 (parent_name
                # filter) — attach its legacy key here or it stays 'matched'
                # forever without a party link (audit D-1, 2026-11-10)
                self._attach_legacy(line)
                continue
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
                    "is_company": _birth(line)[0],
                    "party_class": _birth(line)[1],
                    "legacy_reference": unique_ref(line) or None,
                    "company_id": self.company_id.id,
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
        intra-batch duplicate links to the party its source line created.
        R-12: if the key already belongs to a different party (case-variant
        names slug identically), a deterministic suffix keeps the write legal
        instead of failing the batch."""
        partner = line.matched_partner_id
        if not partner and line.dup_of_line_id:
            partner = line.dup_of_line_id.created_partner_id
            line.matched_partner_id = partner
        if partner and not partner.legacy_reference:
            ref = line.legacy_reference
            if ref:
                clash = self.env["res.partner"].search(
                    [("legacy_reference", "=", ref), ("id", "!=", partner.id)], limit=1
                )
                if clash:
                    suffix = 2
                    while self.env["res.partner"].search_count(
                        [("legacy_reference", "=", "%s-%d" % (ref, suffix))]
                    ):
                        suffix += 1
                    ref = "%s-%d" % (ref, suffix)
                    line.legacy_reference = ref
            partner.sudo().write({"legacy_reference": ref or None})
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
        self._fix_import_check_authority()
        if self.state != "imported":
            raise UserError("Import the batch first.")
        Approval = self.env["fix.registration.approval"]
        decided = activated = skipped = 0
        lines = self.line_ids.filtered(lambda ln: ln.created_partner_id)
        # one search for the whole batch (the vendor ledger carries tens of
        # thousands of lines — a per-line search is minutes of pure overhead)
        approvals = {}
        for approval in Approval.search(
            [("partner_id", "in", lines.mapped("created_partner_id").ids)]
        ):
            approvals.setdefault(approval.partner_id.id, approval)
        for line in lines:
            partner = line.created_partner_id
            if partner.party_status not in ("draft", "pending_approval"):
                skipped += 1
                continue
            if partner.party_class == "individual":
                # individuals open no two-tier registration (BRU-CPM-02 covers
                # dealer/corporate/government); the governed activation is the
                # same guarded status write action_reactivate_party performs,
                # recorded per party with the cut-over reason
                partner.sudo()._guarded().write({"party_status": "active"})
                partner.message_post(
                    body=(
                        "Activated by the M33 %s-list cut-over (individual party; "
                        "batch %s). Reason: legacy partner master migration."
                        % (_DUMP_LABEL.get(self.sheet_kind, "party").lower(), self.import_ref)
                    )
                )
                activated += 1
                continue
            approval = approvals.get(partner.id)
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
            "registrations decided for %d parties, %d individuals activated (%d already active/decided)"
            % (decided, activated, skipped)
        )
        self.state = "approved"
        self.action_assign_roles()
        return True

    def action_assign_roles(self):
        """Give every created party its classification ROLE (M33: one party,
        many roles — never masters). Corp list → customer role; STBL/
        Principal list → brand-partner role; vendor ledger → vendor role,
        ALSO on matched parties (the dual-role rows: a party that is already
        an active customer gains its vendor role, never a second party).
        Idempotent, and only for usable parties (an active role requires an
        active party)."""
        self.ensure_one()
        self._fix_import_check_authority()
        Role = self.env["fix.party.role"]
        role_type = ROLE_BY_KIND[self.sheet_kind]
        if not role_type:
            self._log("roles assigned: none (contact list carries no trading role)")
            self.action_score_quality()
            return True
        lines = self.line_ids.filtered(
            lambda ln: ln.created_partner_id
            or (self.sheet_kind in PARTNER_DUMP_KINDS and ln.matched_partner_id)
        )
        partners = lines.mapped(lambda ln: ln.created_partner_id or ln.matched_partner_id)
        # one read_group for the whole batch (26k-row scale)
        existing = {
            row["partner_id"][0]
            for row in Role.read_group(
                [("partner_id", "in", partners.ids), ("role_type", "=", role_type)],
                ["partner_id"],
                ["partner_id"],
            )
        }
        created = skipped = 0
        for partner in partners:
            if partner.id in existing:
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
        if created:
            # golden-record quality follows the role (readiness report: the
            # imported estate must carry quality scores, not wait for a
            # manual sweep — golden_coverage jumps the moment roles exist)
            self.action_score_quality()
        return True

    def action_score_quality(self):
        """(Re)compute fix.party.quality for THIS batch's created parties —
        the golden-record scorecard the M33 KPI reads."""
        self.ensure_one()
        Quality = self.env["fix.party.quality"]
        scored = 0
        for line in self.line_ids.filtered(lambda ln: ln.created_partner_id):
            partner = line.created_partner_id
            existing = Quality.search([("partner_id", "=", partner.id)], limit=1)
            if existing:
                existing.action_recompute()
            else:
                Quality.create({"partner_id": partner.id, **Quality._score_partner(partner)})
            scored += 1
        self._log("quality scored: %d parties" % scored)
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
        self._fix_import_check_authority()
        Approval = self.env["fix.registration.approval"]
        Hierarchy = self.env["fix.party.hierarchy"]
        referencing = [
            ("fix.service.order", "customer_id"),
            ("account.move", "partner_id"),
            ("fix.contract", "partner_id"),
            ("fix.subscription", "partner_id"),
            ("fix.vendor.invoice", "partner_id"),
            # a supplier-register row pins its partner (ondelete=restrict);
            # the cd_vendor_portal rollback removes this batch's rows first
            ("fix.supplier", "partner_id"),
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
        if self.sheet_kind in PARTNER_DUMP_KINDS:
            # Odoo 19 _read_group yields (groupby-value, aggregate-value) tuples
            summary["by_party_class"] = dict(
                sorted(
                    (klass or "(none)", count)
                    for klass, count in self.env["res.partner"]._read_group(
                        [("id", "in", lines.mapped("created_partner_id").ids)],
                        groupby=["party_class"],
                        aggregates=["id:count"],
                    )
                )
            )
        self._log("reconciled: %s" % summary)
        self.state = "reconciled"
        return summary
