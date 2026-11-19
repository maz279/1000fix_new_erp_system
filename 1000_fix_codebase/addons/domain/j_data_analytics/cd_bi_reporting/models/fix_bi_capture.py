# fix_bi_capture - M25 second capture pass (19 Nov 2026).
#
# The 14 Nov pass gave every M25 page a "+ New". This pass asks whether each
# page captures the record the spec names for it (M25 spec §5, §8, §10):
#
#   p1 Role Dashboards   - FR-BID-009 annotation: no model. The dashboard
#                          had no business owner (BRU-BID-07) and the steward
#                          verified nothing before certification (§8.1,
#                          BRU-BID-10).
#   p2 Report Library    - FR-BID-011 owner/definition/certification and
#                          FR-BID-017 reproducible runs with restatement
#                          flags (BRU-BID-08/09): no model.
#   p3 Self-Service      - FR-BID-018/019 a saved exploration in a personal
#                          workspace: no model (the page offered a dashboard).
#   p4 Distribution      - FR-BID-025/026 a raised alert routed for
#                          acknowledgement, suppressed and escalated
#                          (T-14, BRU-BID-14): no model.
#   p5 Embedded          - FR-BID-029 an embedded chart placement and its
#                          signed, short-lived token (T-08, BRU-BID-12/18): no
#                          model (the page offered the sync connection).
#   p7 Lifecycle & Usage - FR-BID-033 usage telemetry: no model.
import base64
import hashlib
import hmac
import json
import re
import secrets
import time
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _

from .fix_bi_selfservice import CERTIFIER_GROUP, DASHBOARD_ROLES

AUTHOR_GROUP = "cd_bi_reporting.group_bi_author"

DASHBOARD_TIERS = [
    ("executive", "Executive"),
    ("functional", "Functional"),
    ("branch", "Branch"),
    ("personal", "Personal"),
    ("portal", "Portal"),
]

REVIEW_CYCLES = [
    ("monthly", "Monthly"),
    ("quarterly", "Quarterly"),
    ("half_yearly", "Half-yearly"),
    ("yearly", "Yearly"),
]


def _is_steward(env):
    return env.su or env.user.has_group(CERTIFIER_GROUP)


def _metric_bank(env):
    return env["fix.bi.alert.subscription"]._known_metric_keys()


def _check_metric_keys(records, names):
    """Every metric a record names must be one the M25 metric bank computes
    (T-01: no figure is computed outside it; FR-BID-018: a question is
    composed from metrics, never by redefining one)."""
    keys = _metric_bank(records.env)
    if not keys:
        return  # bank unavailable: never guess on the user's behalf
    for rec in records:
        for name in names:
            value = rec[name]
            if value and value not in keys:
                raise ValidationError(
                    _("Metric %(key)r is not computed by the M25 metric bank. Known: %(known)s.")
                    % {"key": value, "known": ", ".join(sorted(keys))}
                )


def _device_class(user_agent):
    ua = (user_agent or "").lower()
    if not ua:
        return "unknown"
    if "ipad" in ua or "tablet" in ua:
        return "tablet"
    if "mobi" in ua or "android" in ua or "iphone" in ua:
        return "mobile"
    return "desktop"


# ---------------------------------------------------------------------------
# p1 - the dashboard: business owner, decision supported, steward verification
# ---------------------------------------------------------------------------


class FixBiDashboardCapture(models.Model):
    _inherit = "fix.bi.dashboard"

    name_bn = fields.Char(string="Name (Bengali)")
    tier = fields.Selection(DASHBOARD_TIERS, default="functional", required=True)
    business_owner_id = fields.Many2one(
        "res.users",
        string="Business Owner",
        tracking=True,
        help="BRU-BID-07: the functional head who owns the content and accepts it "
        "for the audience. Not the author.",
    )
    decision_supported = fields.Text(
        string="Decision It Supports",
        help="Spec §8.1 Requested -> In Build: the decision this dashboard serves.",
    )
    review_cycle = fields.Selection(REVIEW_CYCLES, default="quarterly", required=True)
    verified_by = fields.Many2one("res.users", readonly=True, copy=False)
    verified_at = fields.Datetime(readonly=True, copy=False)
    verification_note = fields.Text(readonly=True, copy=False)
    annotation_ids = fields.One2many("fix.bi.annotation", "dashboard_id", string="Annotations")

    _VERIFY_FIELDS = frozenset({"verified_by", "verified_at", "verification_note"})
    # what the steward verified: changing any of it voids the verification
    _CONTENT_FIELDS = frozenset({"name", "name_bn", "role", "description", "sections_json"})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            typed = self._VERIFY_FIELDS.intersection(k for k, v in vals.items() if v)
            if typed:
                raise ValidationError(
                    _("The steward's verification is recorded by its action, not typed (%s).")
                    % ", ".join(sorted(typed))
                )
        return super().create(vals_list)

    def write(self, vals):
        engine = self.env.context.get("bi_lifecycle_engine")
        if not engine and self._VERIFY_FIELDS.intersection(vals):
            raise UserError(_("The steward's verification is recorded by Verify Content only."))
        if not engine and self._CONTENT_FIELDS.intersection(vals):
            verified = self.filtered("verified_at")
            if verified:
                # the steward verified THIS content; an edit needs a new check
                verified.with_context(bi_lifecycle_engine=True).write(
                    dict.fromkeys(self._VERIFY_FIELDS, False)
                )
        return super().write(vals)

    @api.constrains("business_owner_id", "owner_id")
    def _check_business_owner_not_author(self):
        for rec in self:
            if rec.business_owner_id and rec.business_owner_id == rec.owner_id:
                raise ValidationError(
                    _(
                        "The business owner accepts the content the author built - "
                        "name the functional head, not the author (spec §8.1)."
                    )
                )

    def action_steward_verify(self, note=None):
        """In Review -> verified (spec §8.1): definition, scope, performance and
        Bengali rendering checked by the Data Steward (BRU-BID-10)."""
        note = (note or "").strip()
        for rec in self:
            if rec.state != "review":
                raise UserError(_("A dashboard is verified while it is In Review."))
            if not _is_steward(self.env):
                raise UserError(_("Verifying content is a BI Data Steward act (M25)."))
            if rec.owner_id == self.env.user and not self.env.su:
                raise UserError(_("The author cannot verify their own dashboard (spec §13 SoD)."))
            steward_user = rec.steward_id.user_id
            if steward_user and steward_user != self.env.user and not self.env.su:
                raise UserError(
                    _("%s is the named steward of this dashboard; they verify it.")
                    % rec.steward_id.display_name
                )
            if not note:
                raise UserError(
                    _(
                        "Say what was verified: definition, scope behaviour and the "
                        "Bengali rendering (BRU-BID-10)."
                    )
                )
            rec.with_context(bi_lifecycle_engine=True).write(
                {
                    "verified_by": self.env.user.id,
                    "verified_at": fields.Datetime.now(),
                    "verification_note": note,
                }
            )
            rec.message_post(body=_("Content verified by the steward: %s") % note)
        return True

    def _assert_certifiable(self):
        for rec in self:
            if not rec.business_owner_id:
                raise UserError(
                    _(
                        "Name the business owner first: every published dashboard has one (BRU-BID-07)."
                    )
                )
            if not (rec.decision_supported or "").strip():
                raise UserError(_("State the decision this dashboard supports (spec §8.1)."))
            if not rec.verified_at:
                raise UserError(
                    _(
                        "Submit it for review and have the steward verify the content "
                        "(definition, scope, Bengali rendering) before certification (BRU-BID-10)."
                    )
                )

    def action_request_approval(self, justification=None):
        self._assert_certifiable()
        return super().action_request_approval(justification=justification)

    def action_certify(self):
        # the routed-only refusal comes first: a direct press is told to use
        # the approver's inbox before anything about the content (A03 suite)
        self._approval_assert_routed()
        self._assert_certifiable()
        return super().action_certify()


# ---------------------------------------------------------------------------
# p1 - FR-BID-009 annotation and commentary
# ---------------------------------------------------------------------------


class FixBiAnnotation(models.Model):
    """A named owner's explanation of a figure or period, shown to the
    audience of the cockpit it is written on."""

    _name = "fix.bi.annotation"
    _description = "BI Annotation"
    _order = "create_date desc, id desc"

    name = fields.Char(string="Headline", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    role = fields.Selection(
        DASHBOARD_ROLES, string="Shown On (Role Cockpit)", required=True, default="all", index=True
    )
    dashboard_id = fields.Many2one("fix.bi.dashboard", ondelete="cascade", index=True)
    metric_key = fields.Char(string="Metric")
    period = fields.Char(required=True, help="The period explained, e.g. 2026-11 or Week 46.")
    text_en = fields.Text(string="Explanation (English)", required=True)
    text_bn = fields.Text(string="Explanation (Bengali)")
    author_id = fields.Many2one(
        "res.users", required=True, readonly=True, default=lambda self: self.env.user, index=True
    )
    active = fields.Boolean(default=True, help="Withdrawn annotations leave the cockpit.")

    @api.constrains("metric_key")
    def _check_metric(self):
        _check_metric_keys(self, ["metric_key"])

    @api.constrains("dashboard_id", "role")
    def _check_role_matches(self):
        for rec in self:
            if rec.dashboard_id and rec.dashboard_id.role != rec.role:
                raise ValidationError(
                    _("The annotation shows on the dashboard's own cockpit (%s).")
                    % dict(DASHBOARD_ROLES).get(rec.dashboard_id.role)
                )

    def _assert_may_annotate(self):
        """FR-BID-009: a NAMED owner annotates. On a dashboard with a business
        owner that is the owner (or a steward); on a role cockpit a BI author
        or steward."""
        user = self.env.user
        if self.env.su:
            return
        for rec in self:
            owner = rec.dashboard_id.business_owner_id
            if owner and owner != user and not _is_steward(self.env):
                raise AccessError(
                    _("Only %s, the dashboard's business owner, annotates it (FR-BID-009).")
                    % owner.name
                )
            if not (user.has_group(AUTHOR_GROUP) or _is_steward(self.env)):
                raise AccessError(_("Annotating a cockpit is a BI Author or Data Steward act."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.pop("author_id", None)
            if vals.get("dashboard_id") and not vals.get("role"):
                vals["role"] = self.env["fix.bi.dashboard"].browse(vals["dashboard_id"]).role
        recs = super().create(vals_list)
        recs._assert_may_annotate()
        return recs

    def write(self, vals):
        vals.pop("author_id", None)
        if not self.env.su:
            for rec in self:
                if rec.author_id != self.env.user and not _is_steward(self.env):
                    raise AccessError(_("Only the author edits or withdraws an annotation."))
        res = super().write(vals)
        self._assert_may_annotate()
        return res

    @api.model
    def _for_role(self, role):
        """The live annotations a role cockpit shows (its own and 'all')."""
        roles = [role, "all"] if role != "all" else ["all"]
        return self.search([("role", "in", roles)], limit=20)


# ---------------------------------------------------------------------------
# p2 - FR-BID-011 the library entry, FR-BID-017 the reproducible run
# ---------------------------------------------------------------------------


class FixBiReportDefinition(models.Model):
    """One standard report of the library with its owner, definition and
    certification status (FR-BID-011). The figures stay computed by the pack."""

    _name = "fix.bi.report.definition"
    _description = "BI Standard Report Definition"
    _inherit = ["mail.thread"]
    _order = "report_key"
    _rec_name = "name"

    name = fields.Char(required=True)
    name_bn = fields.Char(string="Name (Bengali)")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    report_key = fields.Char(string="Report", required=True, index=True)
    owning_module = fields.Char(required=True, default="M25")
    business_owner_id = fields.Many2one("res.users", string="Business Owner", required=True)
    definition = fields.Text(
        required=True, help="What the report measures and for whom, in words (FR-BID-011)."
    )
    layout_type = fields.Selection(
        [("analytical", "Analytical"), ("pixel_controlled", "Pixel-controlled (statutory)")],
        required=True,
        default="analytical",
    )
    fmt_csv = fields.Boolean(string="CSV", default=True)
    fmt_xlsx = fields.Boolean(string="XLSX", default=True)
    fmt_pdf = fields.Boolean(string="PDF", default=True)
    retention_to_m24 = fields.Boolean(
        string="File Runs as Records (M24)",
        help="FR-BID-016: a run of this report is evidence and is retained.",
    )
    certification_state = fields.Selection(
        [("draft", "Draft"), ("certified", "Certified"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
        copy=False,
    )
    certified_by = fields.Many2one("res.users", readonly=True, copy=False)
    certified_at = fields.Datetime(readonly=True, copy=False)
    run_ids = fields.One2many("fix.bi.report.run", "definition_id", string="Runs")
    run_count = fields.Integer(compute="_compute_run_count")

    _key_unique = models.Constraint(
        "UNIQUE (report_key, company_id)", "A library report is registered once per company."
    )
    _LIFECYCLE = frozenset({"certification_state", "certified_by", "certified_at"})

    @api.depends("run_ids")
    def _compute_run_count(self):
        for rec in self:
            rec.run_count = len(rec.run_ids)

    @api.constrains("report_key")
    def _check_report_key(self):
        valid = self.env["fix.bi.distribution.schedule"]._valid_report_keys()
        for rec in self:
            if valid and rec.report_key not in valid:
                raise ValidationError(
                    _("Report %(key)r is not in the M25 report library. Valid: %(valid)s.")
                    % {"key": rec.report_key, "valid": ", ".join(sorted(valid))}
                )

    @api.constrains("fmt_csv", "fmt_xlsx", "fmt_pdf")
    def _check_formats(self):
        for rec in self:
            if not (rec.fmt_csv or rec.fmt_xlsx or rec.fmt_pdf):
                raise ValidationError(_("A report is offered in at least one output format."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._LIFECYCLE.intersection(
                k
                for k, v in vals.items()
                if v and not (k == "certification_state" and v == "draft")
            ):
                raise ValidationError(_("A library report is registered as a draft."))
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("bi_report_engine"):
            if self._LIFECYCLE.intersection(vals):
                raise UserError(_("Certification moves only through Certify / Retire."))
            if any(rec.certification_state == "retired" for rec in self):
                raise UserError(_("A retired library report is closed."))
            # the steward certified THIS definition: a changed one is a draft again
            if {"definition", "report_key", "layout_type"}.intersection(vals):
                certified = self.filtered(lambda r: r.certification_state == "certified")
                if certified:
                    certified.with_context(bi_report_engine=True).write(
                        {
                            "certification_state": "draft",
                            "certified_by": False,
                            "certified_at": False,
                        }
                    )
        return super().write(vals)

    def action_certify(self):
        for rec in self:
            if rec.certification_state != "draft":
                raise UserError(_("Only a draft library report is certified."))
            if not _is_steward(self.env):
                raise UserError(_("Certifying a library report is a BI Data Steward act."))
            if self.env.user in (rec.create_uid, rec.business_owner_id) and not self.env.su:
                raise UserError(
                    _(
                        "Certification is an independent check: the person who "
                        "registered or owns the report does not certify it (§13 SoD)."
                    )
                )
            rec.with_context(bi_report_engine=True).write(
                {
                    "certification_state": "certified",
                    "certified_by": self.env.user.id,
                    "certified_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body=_("Certified by %s.") % self.env.user.name)
        return True

    def action_retire(self):
        for rec in self:
            if rec.certification_state == "retired":
                raise UserError(_("Already retired."))
            if not _is_steward(self.env):
                raise UserError(_("Retiring a library report is a BI Data Steward act."))
            rec.with_context(bi_report_engine=True).write({"certification_state": "retired"})
        return True

    @staticmethod
    def _parse_day(value, label):
        value = (value or "").strip()
        if not value:
            return None
        try:
            return fields.Date.to_date(value)
        except ValueError as exc:
            raise UserError(_("%s must be a date (YYYY-MM-DD).") % label) from exc

    def action_generate_run(self, date_from=None, date_to=None):
        """Generate the report as the CALLER (their scope and entitlements,
        BRU-BID-02) and stamp the run so it can be reproduced (BRU-BID-08)."""
        from odoo.addons.cd_p03_portal.controllers import report_delivery

        self.ensure_one()
        if self.certification_state == "retired":
            raise UserError(_("A retired report is no longer generated."))
        start = self._parse_day(date_from, _("Period from"))
        end = self._parse_day(date_to, _("Period to"))
        if start and end and start > end:
            raise UserError(_("The period starts after it ends."))
        params = {}
        if start:
            params["date_from"] = str(start)
        if end:
            params["date_to"] = str(end)
        module, _sep, key = self.report_key.partition(":")
        began = time.monotonic()
        as_of = fields.Datetime.now()
        out = report_delivery.run_pack(self.env, module, key, params)
        duration = int((time.monotonic() - began) * 1000)
        run = (
            self.env["fix.bi.report.run"]
            .sudo()
            .with_context(bi_report_engine=True)
            .create(
                {
                    "definition_id": self.id,
                    "company_id": self.company_id.id,
                    "report_key": self.report_key,
                    "requested_by": self.env.user.id,
                    "data_as_of": as_of,
                    "period_from": start,
                    "period_to": end,
                    "parameters": json.dumps(params, sort_keys=True),
                    "scope_applied": ", ".join(
                        self.env["res.company"].browse(self.env.companies.ids).mapped("name")
                    ),
                    "row_count": len(out.get("rows") or []),
                    "duration_ms": duration,
                    "definition_certified": self.certification_state == "certified",
                    "definition_version": fields.Datetime.to_string(self.write_date or as_of),
                }
            )
        )
        return {"run_id": run.id, "rows": run.row_count, "duration_ms": duration}


class FixBiReportRun(models.Model):
    """One generation of a library report, stamped for reproduction and
    flagged when the period it covers is restated (FR-BID-017)."""

    _name = "fix.bi.report.run"
    _description = "BI Report Run"
    _order = "generated_at desc, id desc"
    _rec_name = "report_key"

    definition_id = fields.Many2one(
        "fix.bi.report.definition", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one("res.company", required=True, index=True)
    report_key = fields.Char(required=True)
    requested_by = fields.Many2one("res.users", required=True)
    generated_at = fields.Datetime(required=True, default=fields.Datetime.now)
    data_as_of = fields.Datetime(required=True)
    period_from = fields.Date()
    period_to = fields.Date()
    parameters = fields.Char()
    scope_applied = fields.Char(help="The companies the requester's read covered.")
    row_count = fields.Integer()
    duration_ms = fields.Integer(string="Duration (ms)")
    definition_certified = fields.Boolean(string="Certified Definition")
    definition_version = fields.Char(help="The definition revision the run was generated from.")
    restatement_flag = fields.Boolean(string="Restated", readonly=True)
    restatement_reference = fields.Char(readonly=True)
    flagged_by = fields.Many2one("res.users", readonly=True)
    flagged_at = fields.Datetime(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("bi_report_engine"):
            raise UserError(_("A report run is recorded by Generate Run, never typed."))
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("bi_report_engine"):
            raise UserError(
                _("A report run is append-only; a restatement is flagged by its action.")
            )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError(_("Report runs are retained (BRU-BID-08)."))
        return super().unlink()

    def action_flag_restatement(self, reference=None):
        """BRU-BID-09: a report covering a restated period is marked affected."""
        reference = (reference or "").strip()
        if not _is_steward(self.env):
            raise UserError(_("Flagging a restatement is a BI Data Steward act."))
        if not reference:
            raise UserError(_("Name the restatement (M62 / M19 reference) that affects this run."))
        for rec in self:
            if rec.restatement_flag:
                raise UserError(_("This run is already flagged as restated."))
            rec.sudo().with_context(bi_report_engine=True).write(
                {
                    "restatement_flag": True,
                    "restatement_reference": reference,
                    "flagged_by": self.env.user.id,
                    "flagged_at": fields.Datetime.now(),
                }
            )
        return True


# ---------------------------------------------------------------------------
# p3 - FR-BID-018/019 a saved exploration in a personal workspace
# ---------------------------------------------------------------------------


class FixBiExploration(models.Model):
    """A saved analyst question composed from measured metrics. Personal
    until its author shares it with the other analysts; it reaches a
    management audience only as a certified dashboard (BRU-BID-06)."""

    _name = "fix.bi.exploration"
    _description = "BI Exploration (Saved Question)"
    _order = "write_date desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    question = fields.Text(required=True, help="The question in words.")
    metric_key = fields.Char(string="Metric", required=True)
    metric_key_2 = fields.Char(string="Second Metric")
    metric_key_3 = fields.Char(string="Third Metric")
    target_role = fields.Selection(
        DASHBOARD_ROLES, string="Role It Would Serve", required=True, default="all"
    )
    author_id = fields.Many2one(
        "res.users", required=True, readonly=True, default=lambda self: self.env.user, index=True
    )
    workspace = fields.Selection(
        [("personal", "Personal"), ("shared", "Shared with Analysts")],
        required=True,
        default="personal",
        readonly=True,
    )
    state = fields.Selection(
        [("open", "Exploring"), ("promoted", "Promoted to Dashboard")],
        required=True,
        default="open",
        readonly=True,
    )
    last_run_at = fields.Datetime(readonly=True)
    last_result = fields.Text(readonly=True)
    dashboard_id = fields.Many2one("fix.bi.dashboard", readonly=True, copy=False)

    _SYSTEM = frozenset(
        {"author_id", "workspace", "state", "last_run_at", "last_result", "dashboard_id"}
    )

    @api.constrains("metric_key", "metric_key_2", "metric_key_3")
    def _check_metrics(self):
        _check_metric_keys(self, ["metric_key", "metric_key_2", "metric_key_3"])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            for key in self._SYSTEM:
                vals.pop(key, None)
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("bi_explore_engine"):
            if self._SYSTEM.intersection(vals):
                raise UserError(_("Sharing, running and promoting are done by their actions."))
            self._assert_author()
            if any(rec.state == "promoted" for rec in self):
                raise UserError(_("A promoted exploration lives on as its dashboard."))
        return super().write(vals)

    def unlink(self):
        self._assert_author()
        return super().unlink()

    def _assert_author(self):
        if self.env.su:
            return
        for rec in self:
            if rec.author_id != self.env.user:
                raise AccessError(_("Only the author changes their exploration (FR-BID-019)."))

    def _metrics_named(self):
        self.ensure_one()
        return [k for k in (self.metric_key, self.metric_key_2, self.metric_key_3) if k]

    def action_run(self):
        """Answer the question now, read as the caller (their scope)."""
        from odoo.addons.cd_p03_portal.controllers.a11 import m25

        bank = m25._metrics(self.env)
        for rec in self:
            lines = []
            for key in rec._metrics_named():
                value = bank.get(key)
                lines.append("%s: %s" % (key, "—" if value is None else value))
            rec.with_context(bi_explore_engine=True).write(
                {"last_run_at": fields.Datetime.now(), "last_result": "\n".join(lines)}
            )
        return True

    def action_share(self):
        self._assert_author()
        for rec in self:
            if rec.workspace == "shared":
                raise UserError(_("Already shared with the analysts."))
            rec.with_context(bi_explore_engine=True).write({"workspace": "shared"})
        return True

    def action_promote(self):
        """Build a dashboard candidate: a DRAFT dashboard that still has to be
        reviewed, verified and certified (BRU-BID-06)."""
        self._assert_author()
        Dashboard = self.env["fix.bi.dashboard"]
        for rec in self:
            if rec.state == "promoted":
                raise UserError(_("Already promoted to %s.") % rec.dashboard_id.display_name)
            dash = Dashboard.create(
                {
                    "name": rec.name,
                    "role": rec.target_role,
                    "company_id": rec.company_id.id,
                    "description": rec.question,
                    "sections_json": json.dumps([{"metrics": rec._metrics_named()}]),
                }
            )
            rec.with_context(bi_explore_engine=True).write(
                {"state": "promoted", "dashboard_id": dash.id}
            )
        return True


# ---------------------------------------------------------------------------
# p4 - FR-BID-025/026 raised alerts: routed, acknowledged, escalated
# ---------------------------------------------------------------------------


class FixBiAlertSubscriptionCapture(models.Model):
    _inherit = "fix.bi.alert.subscription"

    owner_id = fields.Many2one(
        "res.users",
        string="Threshold Owner",
        default=lambda self: self.env.user,
        help="BRU-BID-13: the receiving role owns the threshold.",
    )
    suppression_hours = fields.Integer(
        string="Suppression Window (hours)",
        default=24,
        help="T-14: a repeated breach inside the window adds to the open alert.",
    )
    escalate_after_hours = fields.Integer(string="Escalate After (hours)", default=4)
    escalate_to_id = fields.Many2one("res.users", string="Escalate To")
    instance_ids = fields.One2many("fix.bi.alert.instance", "alert_id", string="Raised Alerts")

    @api.constrains("suppression_hours", "escalate_after_hours")
    def _check_windows(self):
        for rec in self:
            if rec.suppression_hours < 0 or rec.escalate_after_hours <= 0:
                raise ValidationError(
                    _("The suppression window cannot be negative and escalation needs a window.")
                )

    def _evaluate(self):
        # only a real measurement raises or closes: a metric the alert's scope
        # cannot compute leaves last_checked_at unstamped, so clear it first
        before = self.last_checked_at
        self.with_context(bi_alert_engine=True).write({"last_checked_at": False})
        crossed = super()._evaluate()
        if not self.last_checked_at:
            self.with_context(bi_alert_engine=True).write({"last_checked_at": before})
        else:
            Instance = self.env["fix.bi.alert.instance"].sudo().with_context(bi_alert_engine=True)
            if crossed:
                Instance._raise_for(self, self.last_value)
            else:
                Instance._close_recovered(self, self.last_value)
        return crossed


class FixBiAlertInstance(models.Model):
    """One raised alert (spec entity fix.alert.instance)."""

    _name = "fix.bi.alert.instance"
    _description = "BI Raised Alert"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "raised_at desc, id desc"
    _rec_name = "alert_id"

    alert_id = fields.Many2one(
        "fix.bi.alert.subscription", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one("res.company", required=True, index=True)
    metric_key = fields.Char(required=True)
    comparator = fields.Char()
    threshold = fields.Float()
    raised_at = fields.Datetime(required=True, default=fields.Datetime.now)
    observed_value = fields.Float()
    last_observed_value = fields.Float()
    repeat_count = fields.Integer(string="Repeats Suppressed")
    routed_to = fields.Char()
    state = fields.Selection(
        [
            ("open", "Open"),
            ("escalated", "Escalated"),
            ("acknowledged", "Acknowledged"),
            ("closed", "Closed"),
        ],
        required=True,
        default="open",
        index=True,
    )
    acknowledged_by = fields.Many2one("res.users")
    acknowledged_at = fields.Datetime()
    ack_note = fields.Text(string="Acknowledgement Note")
    escalated_at = fields.Datetime()
    escalated_to_id = fields.Many2one("res.users")
    closed_at = fields.Datetime()
    close_note = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("bi_alert_engine"):
            raise UserError(_("An alert is raised by the evaluator, never typed."))
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("bi_alert_engine"):
            business = [k for k in vals if not k.startswith(("message_", "activity_"))]
            if business:
                raise UserError(_("A raised alert moves only by Acknowledge and Close."))
        return super().write(vals)

    def _engine(self):
        return self.sudo().with_context(bi_alert_engine=True)

    @api.model
    def _raise_for(self, alert, value):
        """Raise, or suppress into the live one (T-14 alert idempotency)."""
        live = self.search(
            [("alert_id", "=", alert.id), ("state", "!=", "closed")],
            order="raised_at desc",
            limit=1,
        )
        window = fields.Datetime.now() - timedelta(hours=alert.suppression_hours or 0)
        recent = self.search(
            [("alert_id", "=", alert.id), ("raised_at", ">=", window)],
            order="raised_at desc",
            limit=1,
        )
        held = live or recent
        if held:
            held._engine().write(
                {"repeat_count": held.repeat_count + 1, "last_observed_value": value}
            )
            return held
        return self.create(
            {
                "alert_id": alert.id,
                "company_id": alert.company_id.id,
                "metric_key": alert.metric_key,
                "comparator": alert.comparator,
                "threshold": alert.threshold,
                "observed_value": value,
                "last_observed_value": value,
                "routed_to": alert.recipients,
            }
        )

    @api.model
    def _close_recovered(self, alert, value):
        """An ACKNOWLEDGED alert closes when the metric is back inside the
        threshold; an unacknowledged one keeps waiting for its owner."""
        done = self.search([("alert_id", "=", alert.id), ("state", "=", "acknowledged")])
        done._engine().write(
            {
                "state": "closed",
                "closed_at": fields.Datetime.now(),
                "last_observed_value": value,
                "close_note": _("Metric back inside the threshold."),
            }
        )
        return done

    def _may_act(self):
        """The routed recipients, the threshold owner, or the escalation
        contact act on an alert (FR-BID-025 named role)."""
        self.ensure_one()
        user = self.env.user
        if self.env.su:
            return True
        if user in (self.alert_id.owner_id, self.escalated_to_id, self.alert_id.escalate_to_id):
            return True
        mails = {m.strip().lower() for m in (self.routed_to or "").split(",") if m.strip()}
        return bool(mails & {(user.login or "").lower(), (user.email or "").lower()})

    def action_acknowledge(self, note=None):
        for rec in self:
            if rec.state not in ("open", "escalated"):
                raise UserError(_("Only an open or escalated alert is acknowledged."))
            if not rec._may_act():
                raise AccessError(
                    _(
                        "The alert is routed to its recipients, its owner and its escalation contact."
                    )
                )
            rec._engine().write(
                {
                    "state": "acknowledged",
                    "acknowledged_by": self.env.user.id,
                    "acknowledged_at": fields.Datetime.now(),
                    "ack_note": (note or "").strip() or False,
                }
            )
        return True

    def action_close(self, note=None):
        for rec in self:
            if rec.state != "acknowledged":
                raise UserError(_("Acknowledge the alert before closing it."))
            if not rec._may_act():
                raise AccessError(_("Only the people the alert is routed to close it."))
            note = (note or "").strip()
            if not note:
                raise UserError(_("Say why the alert is closed."))
            rec._engine().write(
                {"state": "closed", "closed_at": fields.Datetime.now(), "close_note": note}
            )
        return True

    @api.model
    def _cron_escalate(self):
        """BRU-BID-14 / AUT-BID-08: an unacknowledged alert escalates."""
        now = fields.Datetime.now()
        escalated = 0
        for rec in self.sudo().search([("state", "=", "open")]):
            hours = rec.alert_id.escalate_after_hours or 0
            if not hours or rec.raised_at + timedelta(hours=hours) > now:
                continue
            target = rec.alert_id.escalate_to_id
            rec._engine().write(
                {"state": "escalated", "escalated_at": now, "escalated_to_id": target.id or False}
            )
            if target:
                rec._engine().activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=target.id,
                    summary=_("Escalated BI alert: %s") % rec.alert_id.name,
                )
            else:
                rec._engine().message_post(
                    body=_("Escalated with no escalation contact named on the alert.")
                )
            escalated += 1
        return escalated


# ---------------------------------------------------------------------------
# p5 - FR-BID-029..032 embedded chart placement and its signed token
# ---------------------------------------------------------------------------

PORTAL_AUDIENCES = {"customer_p01", "corporate_p04", "partner_p05"}
MAX_TOKEN_TTL = 900


class FixBiEmbeddedSurface(models.Model):
    """Where a chart is embedded, for whom, bound to which context, and how
    long its token lives (spec entity fix.embedded.surface)."""

    _name = "fix.bi.embedded.surface"
    _description = "BI Embedded Surface"
    _inherit = ["mail.thread"]
    _order = "host_module, host_screen"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    host_module = fields.Char(required=True, help="The host module (M01-M67) or portal (P01-P07).")
    host_screen = fields.Char(required=True, help="The screen the chart sits on.")
    audience = fields.Selection(
        [
            ("internal", "Internal users"),
            ("customer_p01", "Customer portal (P01)"),
            ("corporate_p04", "Corporate portal (P04)"),
            ("partner_p05", "Partner / seller portal (P05/P07)"),
        ],
        required=True,
        default="internal",
    )
    audience_group_id = fields.Many2one(
        "res.groups", string="Internal Audience Group", ondelete="restrict"
    )
    context_binding = fields.Selection(
        [
            ("scope", "The viewer's own ERP scope"),
            ("record", "The record on the host screen"),
            ("viewer_party", "The viewing party only"),
        ],
        required=True,
        default="record",
    )
    metric_key = fields.Char(string="Metric", required=True)
    metric_key_2 = fields.Char(string="Second Metric")
    token_ttl_seconds = fields.Integer(string="Token Lifetime (s)", required=True, default=300)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
        readonly=True,
    )
    author_id = fields.Many2one(
        "res.users", required=True, readonly=True, default=lambda self: self.env.user
    )
    activated_by = fields.Many2one("res.users", readonly=True)
    activated_at = fields.Datetime(readonly=True)

    _SYSTEM = frozenset({"state", "author_id", "activated_by", "activated_at"})

    @api.constrains("metric_key", "metric_key_2")
    def _check_metrics(self):
        _check_metric_keys(self, ["metric_key", "metric_key_2"])

    @api.constrains("host_module")
    def _check_host(self):
        for rec in self:
            if not re.fullmatch(r"(M(0[1-9]|[1-6]\d)|P0[1-7])", rec.host_module or ""):
                raise ValidationError(
                    _("Host module is a module code M01-M69 or a portal P01-P07.")
                )

    @api.constrains("token_ttl_seconds")
    def _check_ttl(self):
        for rec in self:
            if not 30 <= rec.token_ttl_seconds <= MAX_TOKEN_TTL:
                raise ValidationError(
                    _("An embed token lives 30 to %d seconds (BRU-BID-12: short-lived).")
                    % MAX_TOKEN_TTL
                )

    @api.constrains("audience", "context_binding")
    def _check_portal_binding(self):
        for rec in self:
            if rec.audience in PORTAL_AUDIENCES and rec.context_binding != "viewer_party":
                raise ValidationError(
                    _(
                        "A portal chart shows only the viewing party's own data: bind it "
                        "to the viewing party (BRU-BID-18)."
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            for key in self._SYSTEM:
                vals.pop(key, None)
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("bi_embed_engine"):
            if self._SYSTEM.intersection(vals):
                raise UserError(_("A surface is activated and retired by its actions."))
            if any(rec.state != "draft" for rec in self):
                raise UserError(
                    _("An active or retired surface is not edited; retire and replace it.")
                )
        return super().write(vals)

    def action_activate(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft surface is activated."))
            if not _is_steward(self.env):
                raise UserError(_("Activating an embedded surface is a BI Data Steward act."))
            if rec.author_id == self.env.user and not self.env.su:
                raise UserError(_("The author does not activate their own surface (§13 SoD)."))
            rec.with_context(bi_embed_engine=True).write(
                {
                    "state": "active",
                    "activated_by": self.env.user.id,
                    "activated_at": fields.Datetime.now(),
                }
            )
        return True

    def action_retire(self):
        for rec in self:
            if rec.state == "retired":
                raise UserError(_("Already retired."))
            if not _is_steward(self.env):
                raise UserError(_("Retiring an embedded surface is a BI Data Steward act."))
            rec.with_context(bi_embed_engine=True).write({"state": "retired"})
        return True

    # ---- T-08 signed, short-lived, scope-bound, single-use tokens ----------

    def _secret(self):
        secret = self.env["ir.config_parameter"].sudo().get_param("database.secret")
        if not secret:
            raise UserError(_("No signing secret: embedded analytics are unavailable."))
        return secret.encode()

    def _viewer_allowed(self, user):
        self.ensure_one()
        if self.audience == "internal":
            if user.share:
                return False
            return not self.audience_group_id or self.audience_group_id in user.all_group_ids
        return bool(user.share and user.partner_id)

    def _issue_token(self, record_ref=None):
        """AUT-BID-16: a signed token bound to this surface, this viewer and
        this context, living token_ttl_seconds, redeemable once."""
        self.ensure_one()
        user = self.env.user
        if self.state != "active":
            raise UserError(_("The surface is not active."))
        if not self._viewer_allowed(user):
            raise AccessError(_("You are not in this chart's audience; nothing is embedded."))
        if self.context_binding == "record" and not record_ref:
            raise UserError(_("This chart is bound to the record in context; name the record."))
        if self.context_binding == "viewer_party":
            record_ref = "res.partner,%d" % user.partner_id.id
        jti = secrets.token_urlsafe(18)
        expires = int(time.time()) + self.token_ttl_seconds
        payload = {
            "s": self.id,
            "u": user.id,
            "r": record_ref or "",
            "exp": expires,
            "jti": jti,
        }
        body = base64.urlsafe_b64encode(json.dumps(payload, sort_keys=True).encode()).decode()
        sig = hmac.new(self._secret(), body.encode(), hashlib.sha256).hexdigest()
        self.env["fix.bi.embed.token"].sudo().create(
            {
                "surface_id": self.id,
                "jti": jti,
                "user_id": user.id,
                "record_ref": record_ref or False,
                "expires_at": fields.Datetime.now() + timedelta(seconds=self.token_ttl_seconds),
            }
        )
        return {"token": "%s.%s" % (body, sig), "expires_in": self.token_ttl_seconds}

    @api.model
    def _redeem_token(self, token):
        """Verify and consume: a token is the issuing viewer's, unexpired,
        unaltered and used once (BRU-BID-12 non-replayable)."""
        try:
            body, sig = (token or "").rsplit(".", 1)
            payload = json.loads(base64.urlsafe_b64decode(body.encode()))
        except (ValueError, TypeError) as exc:
            raise AccessError(_("Malformed embed token.")) from exc
        surface = self.sudo().browse(int(payload.get("s") or 0)).exists()
        if not surface:
            raise AccessError(_("Unknown embedded surface."))
        good = hmac.new(surface._secret(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(good, sig):
            raise AccessError(_("The embed token signature does not match."))
        if payload.get("u") != self.env.user.id:
            raise AccessError(_("The embed token was issued to another user."))
        if int(payload.get("exp") or 0) < time.time():
            raise AccessError(_("The embed token has expired."))
        ledger = (
            self.env["fix.bi.embed.token"]
            .sudo()
            .search([("jti", "=", payload.get("jti")), ("surface_id", "=", surface.id)], limit=1)
        )
        if not ledger or ledger.consumed_at:
            raise AccessError(_("The embed token was already used."))
        ledger.write({"consumed_at": fields.Datetime.now()})
        if surface.state != "active":
            raise AccessError(_("The surface is no longer active."))
        return payload


class FixBiEmbedToken(models.Model):
    """The issued-token ledger that makes a token single-use."""

    _name = "fix.bi.embed.token"
    _description = "BI Embed Token Ledger"
    _order = "id desc"
    _rec_name = "jti"

    surface_id = fields.Many2one("fix.bi.embedded.surface", required=True, ondelete="cascade")
    jti = fields.Char(required=True, index=True)
    user_id = fields.Many2one("res.users", required=True)
    record_ref = fields.Char()
    expires_at = fields.Datetime(required=True)
    consumed_at = fields.Datetime()

    _jti_unique = models.Constraint("UNIQUE (jti)", "A token id is issued once.")


# ---------------------------------------------------------------------------
# p7 - FR-BID-033 usage analytics
# ---------------------------------------------------------------------------


class FixBiContentUsage(models.Model):
    """Who viewed what, from which device class. Append-only."""

    _name = "fix.bi.content.usage"
    _description = "BI Content Usage"
    _order = "viewed_at desc, id desc"
    _rec_name = "content_ref"

    content_type = fields.Selection(
        [
            ("role_dashboard", "Role Dashboard"),
            ("report", "Report"),
            ("embedded", "Embedded Chart"),
        ],
        required=True,
    )
    content_ref = fields.Char(required=True, index=True)
    user_id = fields.Many2one("res.users", required=True, index=True)
    company_id = fields.Many2one("res.company", required=True, index=True)
    device_class = fields.Selection(
        [
            ("desktop", "Desktop"),
            ("mobile", "Mobile"),
            ("tablet", "Tablet"),
            ("unknown", "Unknown"),
        ],
        required=True,
        default="unknown",
    )
    viewed_at = fields.Datetime(required=True, default=fields.Datetime.now)

    def write(self, vals):
        raise UserError(_("Usage telemetry is append-only."))

    @api.model
    def _log_view(self, content_type, content_ref, user_agent=None):
        """Record one view as the viewer. Telemetry never blocks the view."""
        try:
            with self.env.cr.savepoint():
                self.sudo().create(
                    {
                        "content_type": content_type,
                        "content_ref": content_ref,
                        "user_id": self.env.user.id,
                        "company_id": self.env.company.id,
                        "device_class": _device_class(user_agent),
                    }
                )
        except Exception:
            return False
        return True
