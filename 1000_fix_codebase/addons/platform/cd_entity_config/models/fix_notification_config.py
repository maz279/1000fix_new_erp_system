# fix.notification.config — M30's notification configuration (P04-M05-T06).
# The dispatcher (services/notification-dispatcher) reads routing, quiet-hours
# and frequency policy from HERE — the runtime copy of the NT-001/NT-002/NT-003
# decisions. "Customer notification preference is a consent-adjacent obligation,
# not a convenience."
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .fix_entity import require_platform_admin

# NT-003 §2.1 — the send windows (Asia/Dhaka). The dispatcher's registry is
# the machine copy; this model is the governed runtime source of overrides.
QUIET_HOUR_WINDOWS = [
    ("24/7", "24/7 (security & transactional — QH-01)"),
    ("08:00-21:00", "08:00-21:00 (service-related)"),
    ("10:00-20:00", "10:00-20:00 (marketing — BTRC)"),
]

# NT-003 §2.2: only transactional and security traffic may be uncapped.
# Marketing and service messages carry a 7-day rolling cap by policy, so a
# stored 0 ("uncapped") on those classes is a policy breach, not a default.
CAPPED_CLASSES = ("marketing", "service")


class FixNotificationConfig(models.Model):
    """Channel routing + suppression configuration the dispatcher honours."""

    _name = "fix.notification.config"
    _description = "Notification Configuration"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _consent_class_channel_unique = models.Constraint(
        "UNIQUE (consent_class, channel)", "One configuration row per consent class and channel"
    )

    name = fields.Char(string="Configuration", compute="_compute_name", store=True)
    consent_class = fields.Selection(
        [
            ("security", "Security (OTP)"),
            ("transactional", "Transactional"),
            ("service", "Service-Related"),
            ("marketing", "Marketing"),
        ],
        string="Consent Class",
        required=True,
        help="NT-002: the class routes the SMS lane (BD-01 masking vs non-masking)",
    )
    channel = fields.Selection(
        [
            ("sms", "SMS (INT-010)"),
            ("whatsapp", "WhatsApp (INT-012)"),
            ("email", "Email (INT-013)"),
            ("push", "Push (Novu)"),
            ("in_app", "In-App (NT-018)"),
        ],
        string="Channel",
        required=True,
    )
    send_window = fields.Selection(
        QUIET_HOUR_WINDOWS,
        string="Send Window",
        required=True,
        default="24/7",
        tracking=True,
        help="QH-04: windows are Asia/Dhaka; there is no per-customer timezone",
    )
    frequency_cap = fields.Integer(
        string="Frequency Cap (7-day rolling)",
        default=0,
        help="0 = uncapped (NT-003 §2.2: transactional and security are uncapped)",
    )
    combined_cap_non_transactional = fields.Integer(
        string="Combined Cap (non-transactional)",
        default=4,
        help="NT-003: all non-transactional classes combined, rolling 7 days",
    )
    sms_route = fields.Selection(
        [
            ("masking", "Masking (alphanumeric sender — 1000FiX)"),
            ("non-masking", "Non-masking (numeric sender)"),
        ],
        string="SMS Route",
        default="masking",
        help="BD-02: a marketing message never uses the masking route",
    )
    stale_discard_hours = fields.Integer(
        string="Stale Discard (hours)",
        default=24,
        help="QH-03: a held message this old when the window opens is discarded",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("consent_class", "channel")
    def _compute_name(self):
        for config in self:
            config.name = f"{config.consent_class} / {config.channel}"

    # company_id present: notification policy is per-company governed data
    # (AS-03 companion — config carries company, not OU: an OU-level split of
    # consent policy would fragment the customer's preference record).

    # A12 X4 / M30 (b08-b10): caps policy is customer-protection law (BTRC /
    # BD-02), so the config register is Platform Admin master data.
    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The notification-policy register")
        return super().create(vals_list)

    def write(self, vals):
        require_platform_admin(self.env, "The notification-policy register")
        return super().write(vals)

    def unlink(self):
        require_platform_admin(self.env, "The notification-policy register")
        return super().unlink()

    # A12 M30-10 (b09, b10): the constraint used to depend on the cap fields
    # only, so writing sms_route ALONE put marketing SMS on the masking route,
    # and a marketing row created with cap 0 (uncapped) passed. Every policy
    # input the rule reads is now a trigger, so no single-field write can
    # sidestep it.
    @api.constrains(
        "consent_class",
        "channel",
        "sms_route",
        "frequency_cap",
        "combined_cap_non_transactional",
    )
    def _check_caps(self):
        for config in self:
            if config.frequency_cap < 0 or config.combined_cap_non_transactional < 0:
                raise ValidationError("Frequency caps cannot be negative")
            if config.consent_class == "marketing" and config.sms_route == "masking":
                raise ValidationError("BD-02: a marketing message never uses the masking route")
            if config.consent_class in CAPPED_CLASSES and config.frequency_cap == 0:
                raise ValidationError(
                    "NT-003: only transactional and security traffic may be "
                    "uncapped — set a 7-day frequency cap for %s messages." % config.consent_class
                )
