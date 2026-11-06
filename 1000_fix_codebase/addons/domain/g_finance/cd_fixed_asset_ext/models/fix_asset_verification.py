# fix_asset_verification — M49 physical verification campaigns.
#
# A campaign snapshots the active assets in scope (company / branch) as
# "pending" lines; tags scanned in the field (mobile scanner -> the
# action_record_scan API, or the line form) mark them found or misplaced and
# unknown tags are recorded as unregistered finds. Closing the campaign marks
# whatever was not seen as missing — the input for a write-off disposal.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_asset_common import USER_GROUP, require_group

RESULTS = [
    ("pending", "Pending"),
    ("found", "Found"),
    ("misplaced", "Found at Another Branch"),
    ("missing", "Missing"),
    ("unregistered", "Found — Not in Register"),
]


class FixAssetVerificationCampaign(models.Model):
    _name = "fix.asset.verification.campaign"
    _description = "Physical Verification Campaign"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    _order = "date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Branch Scope", help="Leave empty: every branch."
    )
    name = fields.Char(string="Campaign", required=True, tracking=True)
    date = fields.Date(string="Count Date", required=True, default=fields.Date.context_today)
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user
    )
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"), ("closed", "Closed")],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.asset.verification.line", "campaign_id", string="Results")
    expected_count = fields.Integer(string="Expected", compute="_compute_counts")
    found_count = fields.Integer(string="Found", compute="_compute_counts")
    missing_count = fields.Integer(string="Missing", compute="_compute_counts")
    misplaced_count = fields.Integer(string="Misplaced", compute="_compute_counts")
    unregistered_count = fields.Integer(string="Not in Register", compute="_compute_counts")
    pending_count = fields.Integer(string="Pending", compute="_compute_counts")

    @api.depends("line_ids.result")
    def _compute_counts(self):
        for rec in self:
            res = rec.line_ids.mapped("result")
            rec.expected_count = len(rec.line_ids.filtered("asset_id"))
            rec.found_count = res.count("found")
            rec.missing_count = res.count("missing")
            rec.misplaced_count = res.count("misplaced")
            rec.unregistered_count = res.count("unregistered")
            rec.pending_count = res.count("pending")

    def action_start(self):
        """Snapshot the register in scope as pending lines."""
        require_group(self.env, USER_GROUP, "Starting a verification campaign")
        Line = self.env["fix.asset.verification.line"]
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft campaigns can be started."))
            domain = [("company_id", "=", rec.company_id.id), ("state", "=", "active")]
            if rec.operating_unit_id:
                domain.append(("operating_unit_id", "=", rec.operating_unit_id.id))
            assets = self.env["fix.fixed.asset"].search(domain)
            if not assets:
                raise UserError(self.env._("No active assets in the campaign's scope."))
            Line._guarded().create(
                [
                    {
                        "campaign_id": rec.id,
                        "asset_id": a.id,
                        "operating_unit_id": a.operating_unit_id.id,
                        "expected_custodian_id": a.custodian_id.id,
                    }
                    for a in assets
                ]
            )
            rec._guarded().write({"state": "in_progress"})
        return True

    def action_record_scan(self, tag, operating_unit_id=None):
        """One scanned tag (mobile scanner API). Returns the line's result."""
        self.ensure_one()
        if self.state != "in_progress":
            raise UserError(self.env._("Start the campaign before scanning."))
        tag = (tag or "").strip()
        if not tag:
            raise UserError(self.env._("Empty tag."))
        line = self.line_ids.filtered(lambda ln: ln.asset_id.code == tag)[:1]
        if not line:
            line = self.line_ids.filtered(lambda ln: ln.scanned_tag == tag)[:1]
        if line:
            line.write({"scanned_tag": tag, "scanned_operating_unit_id": operating_unit_id})
            line._apply_scan()
        else:
            line = (
                self.env["fix.asset.verification.line"]
                ._guarded()
                .create(
                    {
                        "campaign_id": self.id,
                        "scanned_tag": tag,
                        "scanned_operating_unit_id": operating_unit_id,
                        "operating_unit_id": operating_unit_id,
                    }
                )
            )
            line._apply_scan()
        return {"line_id": line.id, "result": line.result}

    def action_close(self):
        """Close: everything still pending is missing."""
        require_group(self.env, USER_GROUP, "Closing a verification campaign")
        for rec in self:
            if rec.state != "in_progress":
                raise UserError(self.env._("Only campaigns in progress can be closed."))
            rec.line_ids.filtered(lambda ln: ln.result == "pending")._guarded().write(
                {"result": "missing"}
            )
            rec._guarded().write({"state": "closed"})
        return True


class FixAssetVerificationLine(models.Model):
    _name = "fix.asset.verification.line"
    _description = "Physical Verification Result"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "campaign_id desc, id"

    campaign_id = fields.Many2one(
        "fix.asset.verification.campaign",
        string="Campaign",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(related="campaign_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Expected Branch")
    asset_id = fields.Many2one("fix.fixed.asset", string="Asset", index=True)
    asset_code = fields.Char(related="asset_id.code", string="Asset Tag")
    expected_custodian_id = fields.Many2one("hr.employee", string="Expected Custodian")
    scanned_tag = fields.Char(string="Scanned Tag")
    scanned_operating_unit_id = fields.Many2one("operating.unit", string="Scanned At Branch")
    scanned_at = fields.Datetime(string="Scanned At", readonly=True)
    result = fields.Selection(
        RESULTS, string="Result", default="pending", required=True, tracking=True
    )
    note = fields.Text(string="Note")
    corrected_by_id = fields.Many2one(
        "res.users",
        string="Corrected By",
        readonly=True,
        copy=False,
        help="A result set by hand (no scan) — never by the counter (BRU-FXA-15)",
    )

    def _fix_guarded_fields(self) -> set:
        # A08 M49-1 (probe 51): 'found' was typed with no scan
        return super()._fix_guarded_fields() | {
            "result",
            "scanned_at",
            "corrected_by_id",
            "asset_id",
        }

    def _apply_scan(self):
        for line in self:
            if not line.asset_id:
                result = "unregistered"
            elif (
                line.scanned_operating_unit_id
                and line.operating_unit_id
                and line.scanned_operating_unit_id != line.operating_unit_id
            ):
                result = "misplaced"
            else:
                result = "found"
            line._guarded().write({"result": result, "scanned_at": fields.Datetime.now()})

    def _check_open(self):
        for line in self:
            if line.campaign_id.state != "in_progress":
                raise UserError(self.env._("The campaign is not in progress."))

    def _check_corrector(self):
        """BRU-FXA-15: a result set without a scan is a correction, never made
        by the counter (the campaign's responsible)."""
        for line in self:
            if not self.env.su and self.env.user == line.campaign_id.responsible_id:
                raise UserError(
                    self.env._(
                        "Segregation of duties: the counter of %s does not correct its "
                        "results by hand; another accountant does.",
                        line.campaign_id.name,
                    )
                )

    def action_mark_found(self):
        require_group(self.env, USER_GROUP, "Recording a verification result")
        self._check_open()
        self._check_corrector()
        self._guarded().write(
            {
                "result": "found",
                "scanned_at": fields.Datetime.now(),
                "corrected_by_id": self.env.uid,
            }
        )
        return True

    def action_mark_missing(self):
        require_group(self.env, USER_GROUP, "Recording a verification result")
        self._check_open()
        self._check_corrector()
        self._guarded().write({"result": "missing", "corrected_by_id": self.env.uid})
        return True
