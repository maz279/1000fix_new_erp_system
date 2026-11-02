# fix.transparency.notice — versioned PDPA transparency notices (M33,
# FR-CPM-037). Consent captured without a notice version is not valid
# consent (BRU-CPM-08), so the notice register is a prerequisite of the
# consent registry, not documentation.
from odoo import api, fields, models


class FixTransparencyNotice(models.Model):
    """A published transparency-notice version (Bengali + English)."""

    _name = "fix.transparency.notice"
    _description = "Transparency Notice"
    _order = "version desc"
    # Odoo 19 constraint attribute form
    _version_unique = models.Constraint("UNIQUE (version)", "Each notice version exists once")

    version = fields.Char(string="Version", required=True, help="Semantic version, e.g. 1.2")
    purpose_set = fields.Char(
        string="Purposes Covered",
        help="Comma-separated purposes this notice covers (marketing, research…)",
    )
    text_en = fields.Text(string="Notice Text (English)", required=True)
    text_bn = fields.Text(string="Notice Text (Bengali)", required=True)
    published_at = fields.Datetime(string="Published At", default=fields.Datetime.now)
    retired_at = fields.Datetime(string="Retired At")
    active = fields.Boolean(
        string="Active",
        compute="_compute_active",
        store=True,
        help="Published and not retired — the versions new consent is captured against",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("version")
    def _compute_display_name(self):
        # No name field: every consent row's notice rendered as
        # "fix.transparency.notice,1" instead of the version it agreed to.
        for notice in self:
            notice.display_name = "গোপনীয়তা বিজ্ঞপ্তি (Privacy Notice) v%s" % (notice.version or "?")

    @api.depends("published_at", "retired_at")
    def _compute_active(self):
        for notice in self:
            notice.active = bool(notice.published_at) and not notice.retired_at

    def action_retire(self):
        """Retire a version: existing consents keep their reference (they were
        validly captured); new captures must use the successor (AUT-CPM-07
        prompts re-acceptance at next interaction)."""
        self.write({"retired_at": fields.Datetime.now()})
        return True
