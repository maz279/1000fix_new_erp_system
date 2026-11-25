# fix_bi_manual_pack — M25 FR-BID-034: the spreadsheet-retirement register.
#
# The spec calls this "the programme that decides whether M25 succeeded"
# (§8.2, KPI-094 manual management reports -> zero). Before this model the
# register existed nowhere: the "Spreadsheets Retired" KPI tile had no
# source and the Lifecycle & Usage page captured a dashboard instead.
#
# Lifecycle (spec §8.2, compressed to the states a person acts on):
#   registered -> parallel_run -> accepted -> retired
#                      |  ^
#                      v  |  (discrepancy: investigated against M62)
#                  investigated
#
# Rules carried here:
#   BRU-BID-16 (H) a pack cannot be retired until its replacement completed a
#              reconciled parallel run (result = matched).
#   BRU-BID-17 (A) once the replacement is accepted the source data behind the
#              pack is retired — stamped with the retirement, by a steward.
#   §13 SoD    the pack's owner is never the person who retires it, and the
#              reconciliation is recorded by a BI Data Steward, not the owner.
#   AUT-BID-13 a discrepancy holds the retirement and is investigated against
#              M62 (the metric), never against the dashboard.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

STEWARD_GROUP = "cd_bi_reporting.group_bi_certifier"

PACK_STATES = [
    ("registered", "Registered"),
    ("parallel_run", "Parallel Run"),
    ("investigated", "Discrepancy Investigated"),
    ("accepted", "Replacement Accepted"),
    ("retired", "Retired"),
]


class FixBiManualPack(models.Model):
    """One manual management pack (a spreadsheet someone assembles by hand)
    on its way to zero."""

    _name = "fix.bi.manual.pack"
    _description = "Manual Pack (Spreadsheet-Retirement Register)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "state, name"

    name = fields.Char(string="Pack Name", required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    function_area = fields.Selection(
        [
            ("executive", "Executive / Board"),
            ("service", "Service Operations"),
            ("commercial", "Commercial / Sales"),
            ("finance", "Finance"),
            ("people", "People / HR"),
            ("supply", "Supply Chain"),
            ("quality", "Quality"),
            ("other", "Other"),
        ],
        string="Function",
        required=True,
        default="finance",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Pack Owner",
        required=True,
        tracking=True,
        default=lambda self: self.env.user,
        help="The person who assembles this pack today.",
    )
    frequency = fields.Selection(
        [
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("ad_hoc", "Ad hoc"),
        ],
        required=True,
        default="monthly",
    )
    effort_hours = fields.Float(
        string="Effort (hours per cycle)",
        help="Hours spent assembling one cycle of the pack - the labour the "
        "retirement releases (KPI: manual pack effort released).",
    )
    metrics_harvested = fields.Text(
        string="Metrics in the Pack",
        help="The figures the pack carries, harvested into the M62 metric "
        "definitions so the replacement shows the same numbers.",
    )
    replacement_dashboard_id = fields.Many2one(
        "fix.bi.dashboard",
        string="Replacement Dashboard",
        ondelete="restrict",
        tracking=True,
    )
    replacement_report_key = fields.Char(
        string="Replacement Report",
        tracking=True,
        help="A standard report of the M25 library (module:report, e.g. M25:branch_league).",
    )
    state = fields.Selection(
        PACK_STATES, required=True, default="registered", tracking=True, copy=False
    )
    parallel_run_started_at = fields.Datetime(readonly=True, copy=False)
    reconciliation_result = fields.Selection(
        [("matched", "Figures Match"), ("discrepancy", "Discrepancy")],
        readonly=True,
        copy=False,
        tracking=True,
    )
    reconciliation_note = fields.Text(readonly=True, copy=False)
    reconciled_by = fields.Many2one("res.users", readonly=True, copy=False)
    reconciled_at = fields.Datetime(readonly=True, copy=False)
    source_data_retired_at = fields.Datetime(
        readonly=True,
        copy=False,
        help="BRU-BID-17: the manual path is no longer available from this moment.",
    )
    retired_by = fields.Many2one("res.users", readonly=True, copy=False)
    retired_at = fields.Datetime(readonly=True, copy=False)

    _LIFECYCLE_FIELDS = frozenset(
        {
            "state",
            "parallel_run_started_at",
            "reconciliation_result",
            "reconciliation_note",
            "reconciled_by",
            "reconciled_at",
            "source_data_retired_at",
            "retired_by",
            "retired_at",
        }
    )

    # ---- guards ----------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            stray = self._LIFECYCLE_FIELDS.intersection(
                k for k, v in vals.items() if v and not (k == "state" and v == "registered")
            )
            if stray:
                raise ValidationError(
                    _(
                        "A manual pack enters the register as REGISTERED - its parallel "
                        "run, reconciliation and retirement are recorded by the "
                        "register's own actions, never by the create form (%s)."
                    )
                    % ", ".join(sorted(stray))
                )
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("bi_pack_engine"):
            touched = self._LIFECYCLE_FIELDS.intersection(vals)
            if touched:
                raise UserError(
                    _(
                        "The register's lifecycle (%s) moves only through its actions: "
                        "start the parallel run, record the reconciliation, retire."
                    )
                    % ", ".join(sorted(touched))
                )
            business = [k for k in vals if not k.startswith(("message_", "activity_"))]
            if business and any(rec.state == "retired" for rec in self):
                raise UserError(_("A retired pack is closed on the register; it cannot be edited."))
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(rec.state != "registered" for rec in self):
            raise UserError(
                _("Only a pack still at Registered can be removed; the register keeps the rest.")
            )
        return super().unlink()

    @api.constrains("effort_hours")
    def _check_effort(self):
        for rec in self:
            if rec.effort_hours < 0:
                raise ValidationError(_("Effort per cycle cannot be negative."))

    @api.constrains("replacement_report_key")
    def _check_replacement_report(self):
        # A1-F10: the library is the domain module's own (fix_bi_library), so
        # an unknown replacement key is always REFUSED — the old skip "if
        # valid" only happened because the keys came from the portal
        # controller, which a backend-only install does not have.
        valid = self.env["fix.bi.distribution.schedule"]._valid_report_keys()
        for rec in self:
            key = rec.replacement_report_key
            if key and key not in valid:
                raise ValidationError(
                    _("Report %r is not in the M25 report library. Valid: %s.")
                    % (key, ", ".join(sorted(valid)))
                )

    # ---- helpers -----------------------------------------------------------

    def _is_steward(self):
        return self.env.su or self.env.user.has_group(STEWARD_GROUP)

    def _replacement_ready(self):
        """A certified dashboard, or a standard report of the library (the
        library's packs are code-reviewed and served live, spec §5.2)."""
        self.ensure_one()
        if self.replacement_dashboard_id:
            return self.replacement_dashboard_id.state == "certified"
        return bool(self.replacement_report_key)

    def _lifecycle_write(self, vals):
        return self.with_context(bi_pack_engine=True).write(vals)

    # ---- actions -------------------------------------------------------------

    def action_start_parallel_run(self):
        """Registered/investigated -> parallel run: both the pack and its
        certified replacement are produced and their figures compared."""
        for rec in self:
            if rec.state not in ("registered", "investigated"):
                raise UserError(
                    _("Only a registered or investigated pack can start a parallel run.")
                )
            if not rec._replacement_ready():
                raise UserError(
                    _(
                        "Name the replacement first: a CERTIFIED dashboard or a standard "
                        "report of the library. A pack cannot be compared with nothing."
                    )
                )
            rec._lifecycle_write(
                {
                    "state": "parallel_run",
                    "parallel_run_started_at": fields.Datetime.now(),
                    "reconciliation_result": False,
                    "reconciliation_note": False,
                    "reconciled_by": False,
                    "reconciled_at": False,
                }
            )
            rec.message_post(body=_("Parallel run started."))
        return True

    def _reconcile(self, result, note):
        for rec in self:
            if rec.state != "parallel_run":
                raise UserError(_("A reconciliation is recorded on a pack in its parallel run."))
            if not rec._is_steward():
                raise UserError(
                    _(
                        "Recording the reconciliation is a BI Data Steward act (M25) - the "
                        "pack's figures are checked independently of the people who make it."
                    )
                )
            if rec.owner_id == self.env.user and not self.env.su:
                raise UserError(
                    _("The pack's owner cannot reconcile their own pack (spec §13 SoD).")
                )
            note = (note or "").strip()
            if result == "discrepancy" and not note:
                raise UserError(
                    _("Say what differs - the investigation is raised against the metric (M62).")
                )
            rec._lifecycle_write(
                {
                    "state": "accepted" if result == "matched" else "investigated",
                    "reconciliation_result": result,
                    "reconciliation_note": note or False,
                    "reconciled_by": self.env.user.id,
                    "reconciled_at": fields.Datetime.now(),
                }
            )
            if result == "matched":
                rec.message_post(body=_("Parallel run reconciled: figures match. %s") % note)
            else:
                rec.message_post(
                    body=_(
                        "Parallel run discrepancy - retirement held; investigate the "
                        "metric definition in M62, not the dashboard (AUT-BID-13): %s"
                    )
                    % note
                )
        return True

    def action_reconcile_matched(self, note=None):
        return self._reconcile("matched", note)

    def action_reconcile_discrepancy(self, note=None):
        return self._reconcile("discrepancy", note)

    def action_retire(self):
        """Accepted -> retired: the manual path closes (BRU-BID-16/17)."""
        for rec in self:
            if rec.state != "accepted" or rec.reconciliation_result != "matched":
                raise UserError(
                    _(
                        "A pack is retired only after a reconciled parallel run with "
                        "matching figures (BRU-BID-16)."
                    )
                )
            if not rec._is_steward():
                raise UserError(
                    _("Retiring a manual pack is a BI Data Steward act (M25, BRU-BID-17).")
                )
            if rec.owner_id == self.env.user and not self.env.su:
                raise UserError(
                    _(
                        "The pack's owner cannot approve its own retirement (spec §13 SoD) "
                        "- another steward retires it."
                    )
                )
            now = fields.Datetime.now()
            rec._lifecycle_write(
                {
                    "state": "retired",
                    "retired_by": self.env.user.id,
                    "retired_at": now,
                    "source_data_retired_at": now,
                }
            )
            rec.message_post(
                body=_("Retired by %s - the manual path is closed.") % self.env.user.name
            )
        return True
