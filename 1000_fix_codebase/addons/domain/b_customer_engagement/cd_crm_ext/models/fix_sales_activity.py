# fix.sales.activity — the M07 interaction log (FR-CRM-045, spec §10.1).
#
# M07 audit 2026-11-13: the "Activities" sub-module page had no capture
# button, and the "Activity (call/visit/meeting)" form it pointed at edited a
# LEAD: its fields were the lead's next-activity snapshot (activity_summary,
# activity_type_id, activity_date_deadline), which Odoo computes from
# mail.activity. The due date is read-only, so every save that set one was
# refused, and a summary or type written on a lead with no pending activity
# went nowhere. Opened blank, the form created a new lead named after the
# "activity". Nothing a seller did - a call, a site visit, a meeting - was
# ever recorded.
#
# This is the record the spec names: one row per interaction against a lead,
# an opportunity or an account, with its outcome and the next step. A next
# step with a date schedules a To-Do for the owner on the lead (or account),
# which is the reminder FR-CRM-045 asks for.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

ACTIVITY_TYPES = [
    ("call", "Phone Call"),
    ("meeting", "Meeting"),
    ("site_visit", "Site Visit"),
    ("email", "E-mail"),
    ("task", "Task"),
]

OUTCOMES = [
    ("progressed", "Progressed"),
    ("neutral", "No Change"),
    ("objection", "Objection Raised"),
    ("no_contact", "No Contact Made"),
]


class FixSalesActivity(models.Model):
    """A call, meeting, site visit, e-mail or task a seller carried out."""

    _name = "fix.sales.activity"
    _description = "Sales Activity"
    _inherit = ["mail.thread"]
    _order = "occurred_at desc, id desc"

    name = fields.Char(string="Subject", required=True, tracking=True)
    activity_type = fields.Selection(
        ACTIVITY_TYPES, string="Activity Type", required=True, default="call", tracking=True
    )
    occurred_at = fields.Datetime(
        string="When", required=True, default=fields.Datetime.now, tracking=True
    )
    duration_minutes = fields.Integer(string="Duration (minutes)")
    location = fields.Char(string="Location / Site Address")

    lead_id = fields.Many2one(
        "crm.lead",
        string="Lead / Opportunity",
        index=True,
        ondelete="set null",
        tracking=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Account",
        index=True,
        tracking=True,
        help="The customer the activity was with. Taken from the lead when " "left empty.",
    )
    subject_type = fields.Selection(
        [("lead", "Lead"), ("opportunity", "Opportunity"), ("account", "Account")],
        string="Logged Against",
        compute="_compute_subject_type",
        store=True,
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Done By",
        required=True,
        index=True,
        default=lambda self: self.env.user,
        tracking=True,
    )

    outcome = fields.Selection(OUTCOMES, string="Outcome", tracking=True)
    notes = fields.Text(string="Notes / Minutes")
    next_action = fields.Char(string="Next Step")
    next_action_date = fields.Date(string="Next Step Due")
    reminder_activity_id = fields.Many2one(
        "mail.activity",
        string="Reminder",
        readonly=True,
        copy=False,
        ondelete="set null",
        help="The To-Do scheduled for the owner on the lead or account.",
    )

    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("lead_id", "lead_id.type")
    def _compute_subject_type(self):
        for rec in self:
            if rec.lead_id:
                rec.subject_type = "opportunity" if rec.lead_id.type == "opportunity" else "lead"
            else:
                rec.subject_type = "account"

    # `name` is required, so it is in every create: a constraint on lead_id /
    # partner_id alone never ran for an activity that set NEITHER of them
    @api.constrains("lead_id", "partner_id", "name")
    def _check_subject(self):
        for rec in self:
            if not rec.lead_id and not rec.partner_id:
                raise ValidationError(
                    "Log the activity against a lead, an opportunity or an account (FR-CRM-045)."
                )

    @api.constrains("duration_minutes")
    def _check_duration(self):
        for rec in self:
            if rec.duration_minutes and rec.duration_minutes < 0:
                raise ValidationError("An activity cannot last a negative number of minutes.")

    # ------------------------------------------------------------------
    # ORM
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [dict(vals) for vals in vals_list]
        for vals in vals_list:
            if vals.get("lead_id") and not vals.get("partner_id"):
                lead = self.env["crm.lead"].browse(vals["lead_id"]).exists()
                if lead.partner_id:
                    vals["partner_id"] = lead.partner_id.id
        records = super().create(vals_list)
        records.filtered("next_action_date")._schedule_reminder()
        return records

    def write(self, vals):
        result = super().write(vals)
        if {"next_action", "next_action_date", "owner_id"} & set(vals):
            self._schedule_reminder()
        return result

    # ------------------------------------------------------------------
    # The reminder (FR-CRM-045)
    # ------------------------------------------------------------------
    def _reminder_target(self):
        self.ensure_one()
        return self.lead_id or self.partner_id

    def _schedule_reminder(self):
        """One pending To-Do per activity: a changed next step replaces it."""
        for rec in self:
            old = rec.reminder_activity_id.with_context(active_test=False).exists()
            if old and old.active:
                # a superseded, still-pending reminder is this record's own
                # bookkeeping; a reminder already marked done stays history
                old.sudo().unlink()
            target = rec._reminder_target()
            activity = False
            if rec.next_action_date and target:
                summary = rec.next_action or ("Follow up: %s" % rec.name)
                activity = target.activity_schedule(
                    act_type_xmlid="mail.mail_activity_data_todo",
                    date_deadline=rec.next_action_date,
                    summary=summary[:256],
                    note="From %s: %s" % (dict(ACTIVITY_TYPES).get(rec.activity_type), rec.name),
                    user_id=rec.owner_id.id,
                )
            if activity or rec.reminder_activity_id:
                super(FixSalesActivity, rec).write(
                    {"reminder_activity_id": activity.id if activity else False}
                )
