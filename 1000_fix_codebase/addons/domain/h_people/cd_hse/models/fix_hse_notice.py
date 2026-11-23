# fix_hse_notice — M59: the instant notice of a fatal or serious accident.
#
# A09 ERP audit M59-F2 (2026-11-23). Labour Rules 2015 r.69(1): on a fatal or
# serious accident the establishment authority informs, AT ONCE, the Inspector
# General (DIFE), the Deputy Commissioner, the local Inspector, the Fire
# Service, the hospital and the Industrial Police — then files Form 27 within
# two days (r.69(2)) and the final report Form 27(A) within two months or on
# the worker's return (r.69(3)). The register recorded only a boolean
# ("immediate notification required") and one DIFE dispatch date, so which
# authorities were actually told, and when, could not be shown to an inspector.
#
# One line per NAMED authority per register entry: who, when, and the reference
# the authority gave. The register's close gate lists the authorities still
# missing (fix_hse.py, _fix_instant_notice_missing).
from odoo import fields, models

# The six authorities of BLR 2015 r.69(1), in the order the Rule names them.
NOTICE_AUTHORITIES = [
    ("inspector_general", "Inspector General (DIFE)"),
    ("deputy_commissioner", "Deputy Commissioner"),
    ("local_inspector", "Local Inspector"),
    ("fire_service", "Fire Service and Civil Defence"),
    ("hospital", "Hospital"),
    ("industrial_police", "Industrial Police"),
]
AUTHORITY_LABELS = dict(NOTICE_AUTHORITIES)


class FixHseNoticeRecipient(models.Model):
    _name = "fix.hse.notice.recipient"
    _description = "Accident Instant-Notice Recipient (BLR r.69(1))"
    _order = "register_id, id"

    register_id = fields.Many2one(
        "fix.statutory.accident.register",
        string="Accident Register Entry",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        related="register_id.company_id", string="Company", store=True, index=True
    )
    authority = fields.Selection(
        NOTICE_AUTHORITIES,
        string="Authority",
        required=True,
        help="The six authorities of Labour Rules 2015 r.69(1); each is told "
        "at once on a fatal or serious accident.",
    )
    mode = fields.Selection(
        [
            ("phone", "Telephone"),
            ("sms", "SMS"),
            ("email", "E-mail"),
            ("letter", "Written letter"),
            ("in_person", "In person"),
        ],
        string="How",
        default="phone",
        required=True,
    )
    notified_on = fields.Datetime(
        string="Notified At",
        help="When this authority was told. Empty: told-not-recorded, which the "
        "register's close gate treats as not done.",
    )
    notified_by_id = fields.Many2one("res.users", string="Notified By", readonly=True)
    reference = fields.Char(
        string="Reference / Contact",
        help="The authority's reference, acknowledgement number or the officer " "spoken to.",
    )
    note = fields.Text()

    # Odoo 19 ignores the legacy `_sql_constraints` list (the registry logs
    # "no longer supported"): declare the constraint the 19 way.
    _fix_notice_register_authority_uniq = models.Constraint(
        "unique(register_id, authority)",
        "One line per authority per accident: record the second call on the "
        "same line (BLR r.69(1)).",
    )
