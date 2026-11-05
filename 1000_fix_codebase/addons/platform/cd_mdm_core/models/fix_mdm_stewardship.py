# fix_mdm_stewardship — M64 Completion: Data Stewardship & Quality Scoring (CD-M64-02).
import re
from collections import Counter

from odoo import api, fields, models

from libs.py.fix_events import publish

_BD_MOBILE = re.compile(r"^(?:\+?880|0)1[3-9]\d{8}$")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_SERIAL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9./-]{3,}$")
_CODE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")


def _digits_phone(value):
    return re.sub(r"[\s()-]", "", value or "")


def _valid_party(rec):
    phone = _digits_phone(rec.phone)
    if phone and not _BD_MOBILE.match(phone):
        return False
    return not rec.email or bool(_EMAIL.match(rec.email))


def _valid_product(rec):
    code = rec.product_tmpl_id.default_code
    return bool(code) and bool(_CODE.match(code))


def _valid_asset(rec):
    serial = rec.serial_number
    if serial and not _SERIAL.match(serial):
        return False
    for imei in (rec.imei_1, rec.imei_2):
        if imei and not re.fullmatch(r"\d{15}", imei):
            return False
    return bool(serial or rec.imei_1)


def _valid_financial(rec):
    return bool(rec.code) and bool(_CODE.match(rec.code))


# The governed master of each domain: model, record filter, the attributes a
# complete record must carry, the validity rule, and the uniqueness key.
# Scores are MEASURED over these records - nothing is assumed.
DOMAIN_RULES = {
    "party": {
        "model": "res.partner",
        "domain": [("is_company", "=", False)],
        "required": ("name", "phone"),
        "valid": _valid_party,
        "key": lambda r: _digits_phone(r.phone)[-10:] or None,
    },
    "product": {
        "model": "fix.catalogue.item",
        "domain": [],
        "required": ("product_tmpl_id", "name_bn", "category_id"),
        "valid": _valid_product,
        "key": lambda r: (r.product_tmpl_id.default_code or "").strip().upper() or None,
    },
    "asset": {
        "model": "fix.device",
        "domain": [],
        "required": ("device_model_id", "serial_number", "owner_id"),
        "valid": _valid_asset,
        "key": lambda r: (r.serial_number or "").strip().upper() or None,
    },
    "financial": {
        "model": "operating.unit",
        "domain": [],
        "required": ("name", "code", "company_id", "partner_id"),
        "valid": _valid_financial,
        "key": lambda r: ((r.code or "").strip().upper(), r.company_id.id) if r.code else None,
    },
}


class FixMdmStewardship(models.Model):
    _name = "fix.mdm.stewardship"
    _description = "Master Data Domain Stewardship & Quality Engine"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "overall_quality_score desc, domain asc"

    # AS-03: Multi-company and Operating Unit discipline
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

    name = fields.Char(string="Stewardship Domain Title", required=True)
    domain = fields.Selection(
        [
            ("party", "Party / Customer Master (M33)"),
            ("product", "Catalogue & Spare Parts Master (M37 / M15)"),
            ("asset", "Device & Customer Asset Registry (M17)"),
            ("financial", "General Ledger & Operating Units (M19 / M30)"),
        ],
        string="Data Domain",
        required=True,
        index=True,
    )
    lead_steward_id = fields.Many2one(
        "res.users",
        string="Lead Data Steward",
        required=True,
        tracking=True,
    )

    # Data Quality Dimensions (DAMA-DMBOK compliant). MEASURED by
    # action_audit_data_quality over the governed records; 0 until audited
    # (audit_state says whether a score is a measurement at all).
    completeness_score = fields.Float(
        string="Completeness Score (%)",
        default=0.0,
        readonly=True,
        help="Percentage of master records with every mandatory attribute populated.",
        tracking=True,
    )
    uniqueness_score = fields.Float(
        string="Uniqueness Score (%)",
        default=0.0,
        readonly=True,
        help="Percentage of keyed records whose match key no other record shares.",
        tracking=True,
    )
    validity_score = fields.Float(
        string="Validity Score (%)",
        default=0.0,
        readonly=True,
        help="Percentage of records passing format rules (e.g. BD mobile, IMEI, codes).",
        tracking=True,
    )
    audit_state = fields.Selection(
        [
            ("not_audited", "Not Audited"),
            ("audited", "Measured"),
            ("no_data", "No Records to Measure"),
        ],
        string="Audit Status",
        default="not_audited",
        required=True,
        readonly=True,
        tracking=True,
    )
    overall_quality_score = fields.Float(
        string="Overall Quality Index (%)",
        compute="_compute_quality_index",
        store=True,
        tracking=True,
    )

    records_audited_count = fields.Integer(
        string="Records Audited",
        default=0,
        readonly=True,
    )
    last_audit_date = fields.Datetime(string="Last Audit Timestamp", readonly=True)

    _domain_company_unique = models.Constraint(
        "UNIQUE (company_id, domain)",
        "A stewardship governance record already exists for this domain within the company.",
    )

    # A12 R4 (M64): the quality scores are EVIDENCE measured by the audit
    # action; a caller typing a better number in the form is the audit finding
    # itself. They change only through action_audit_data_quality.
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "completeness_score",
            "uniqueness_score",
            "validity_score",
            "audit_state",
            "records_audited_count",
            "last_audit_date",
        }

    @api.depends("completeness_score", "uniqueness_score", "validity_score")
    def _compute_quality_index(self):
        for rec in self:
            rec.overall_quality_score = round(
                (rec.completeness_score * 0.4)
                + (rec.uniqueness_score * 0.3)
                + (rec.validity_score * 0.3),
                2,
            )

    @api.model
    def _measure_domain(self, domain_code: str) -> dict:
        """Measure completeness/uniqueness/validity over the governed records.

        Returns {"count", "completeness", "uniqueness", "validity"} (percent,
        2 dp) or {"count": 0} when there is nothing to measure. A required
        attribute the model does not carry counts as missing."""
        rules = DOMAIN_RULES[domain_code]
        if rules["model"] not in self.env:
            return {"count": 0}
        records = self.env[rules["model"]].search(rules["domain"])
        total = len(records)
        if not total:
            return {"count": 0}
        fields_map = records._fields
        complete = sum(
            1
            for rec in records
            if all(name in fields_map and rec[name] for name in rules["required"])
        )
        valid = sum(1 for rec in records if rules["valid"](rec))
        keys = [rules["key"](rec) for rec in records]
        keyed = [k for k in keys if k is not None]
        counts = Counter(keyed)
        unique = sum(1 for k in keyed if counts[k] == 1)

        def pct(part, whole):
            return round(100.0 * part / whole, 2) if whole else 0.0

        return {
            "count": total,
            "completeness": pct(complete, total),
            # unkeyed records cannot be matched: they are not "unique" either
            "uniqueness": pct(unique, total),
            "validity": pct(valid, total),
        }

    def action_audit_data_quality(self):
        """Audit the domain's governed master and store the MEASURED scores.
        An empty (or uninstalled) master is reported as no_data with zero
        scores - never a perfect or assumed score."""
        self.ensure_one()
        measured = self._measure_domain(self.domain)
        if measured["count"]:
            vals = {
                "completeness_score": measured["completeness"],
                "uniqueness_score": measured["uniqueness"],
                "validity_score": measured["validity"],
                "audit_state": "audited",
            }
        else:
            vals = {
                "completeness_score": 0.0,
                "uniqueness_score": 0.0,
                "validity_score": 0.0,
                "audit_state": "no_data",
            }
        vals.update(
            {"records_audited_count": measured["count"], "last_audit_date": fields.Datetime.now()}
        )
        self._guarded().write(vals)

        publish(
            self.env,
            "mdm.quality_audited",
            "fix.mdm.stewardship",
            self.id,
            {
                "domain": self.domain,
                "audit_state": self.audit_state,
                "completeness_score": self.completeness_score,
                "uniqueness_score": self.uniqueness_score,
                "validity_score": self.validity_score,
                "overall_quality_score": self.overall_quality_score,
                "records_audited": self.records_audited_count,
            },
        )

    # ---- A12 event consumer (FF-48) ---------------------------------------
    # mdm.quality_audited → chatter: the quality trail lives on the record.
    @api.model
    def consume_mdm_quality_audited(self, event):
        rec = self.browse(event.get("aggregate_id")).exists()
        payload = event.get("payload") or {}
        if rec and hasattr(rec, "message_post"):
            rec.message_post(
                body="Quality audit published for %s: %s records, index %s%%."
                % (
                    dict(self._fields["domain"].selection).get(rec.domain, rec.domain),
                    payload.get("records_audited", rec.records_audited_count),
                    payload.get("overall_quality_score", rec.overall_quality_score),
                )
            )
        return True
