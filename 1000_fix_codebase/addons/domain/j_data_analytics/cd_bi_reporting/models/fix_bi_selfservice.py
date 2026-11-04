# M25 self-service BI: saved dashboards with a CERTIFICATION lifecycle,
# scheduled distribution with an entitlement-re-checking worker, and
# threshold alerts.
#
# A11 audit G8 (M25-6/-8): the dashboard had no lifecycle at all and the
# schedule was configuration with nothing behind it. Now: a dashboard is
# born draft, is reviewed by its steward, and reaches CERTIFIED only
# through an approved M63 request decided by a certifier who is NOT the
# author (author != steward, spec §13 SoD); the distribution worker
# validates the report key, resolves every recipient to an active internal
# user, re-checks their entitlement at send time, and writes an export log
# row per dispatch.
import base64
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

DASHBOARD_ROLES = [
    ("all", "All Roles"),
    ("ceo", "CEO"),
    ("coo", "COO / Operations"),
    ("cfo", "CFO / Finance"),
    ("cco", "CCO / Commercial"),
    ("service", "Service"),
    ("finance", "Finance Analytics"),
    ("people", "People"),
    ("quality", "Quality"),
]

CERTIFIER_GROUP = "cd_bi_reporting.group_bi_certifier"

# Packs carrying finance figures: a recipient must hold the BI finance
# group to receive them (E6 — same gate as the on-screen pack).
FINANCE_PACKS = {"M25:finance_pack", "M25:executive_pack"}


def _pack_required_group(pack):
    """The group a reader must hold to open this pack (E6 mirror)."""
    if pack in FINANCE_PACKS:
        return "cd_bi_reporting.group_bi_finance"
    return None


class FixBiDashboard(models.Model):
    """A saved dashboard definition with the spec §8.1 lifecycle:
    draft -> review -> certified -> retired.

    G8: certification runs through the approval engine (M63) as a routed
    request decided by the BI certifier group — the author can never
    certify their own dashboard."""

    _name = "fix.bi.dashboard"
    _description = "Saved BI Dashboard"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "role, name"

    _approval_domain = "bi_content"
    _approval_apply_method = "action_certify"
    _approval_group = CERTIFIER_GROUP
    _approval_routed = True

    name = fields.Char(required=True)
    role = fields.Selection(DASHBOARD_ROLES, required=True, default="all", index=True)
    description = fields.Text()
    is_shared = fields.Boolean(
        help="Shared dashboards are visible to every internal user of the company."
    )
    owner_id = fields.Many2one(
        "res.users", required=True, default=lambda self: self.env.user, index=True
    )
    steward_id = fields.Many2one(
        "hr.employee",
        string="Data Steward",
        help="The steward who reviews the content before the certification "
        "request (spec §13: a named person, not a role).",
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    sections_json = fields.Text(
        string="Layout (JSON)",
        help="Self-service layout contract: ordered KPI/report sections. "
        "An empty value means the dashboard uses its role's standard pack.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("review", "In Review"),
            ("certified", "Certified"),
            ("retired", "Retired"),
        ],
        required=True,
        default="draft",
        tracking=True,
        copy=False,
        help="G8 lifecycle: certification is granted by an approved M63 "
        "request (author != certifier); retirement is a steward act.",
    )
    certified_by = fields.Many2one("res.users", readonly=True, copy=False)
    certified_at = fields.Datetime(readonly=True, copy=False)
    retired_by = fields.Many2one("res.users", readonly=True, copy=False)
    retired_at = fields.Datetime(readonly=True, copy=False)
    last_viewed_at = fields.Datetime(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Born certified would skip the whole point of the lifecycle (G8).
            if vals.get("state", "draft") != "draft":
                raise ValidationError(
                    _(
                        "A dashboard is created as a DRAFT — certification is granted by an approved request (M63), never by the create form."
                    )
                )
        return super().create(vals_list)

    def write(self, vals):
        # G8: the lifecycle fields move only through the record's own
        # governed actions — the engine apply, and retirement.
        if "state" in vals and not self.env.context.get("bi_lifecycle_engine"):
            for rec in self:
                if vals["state"] != rec.state:
                    raise UserError(
                        _(
                            "Dashboard %s changes state only through the certification engine (M63) or action_retire — not by editing the field."
                        )
                        % rec.display_name
                    )
        # SoD defense in depth: nobody — not even the engine — stamps the
        # AUTHOR as the certifier of their own content.
        if vals.get("certified_by"):
            for rec in self:
                if vals["certified_by"] == rec.owner_id.id:
                    raise UserError(
                        _("The author cannot certify their own dashboard (spec §13 SoD).")
                    )
        return super().write(vals)

    def action_submit_review(self):
        """Draft -> review: the steward picks it up (spec §8.1 step 3)."""
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only a draft dashboard can enter review."))
            if not rec.steward_id:
                raise UserError(
                    _(
                        "Name the data steward before entering review — certification is a named person's act (§13)."
                    )
                )
            rec.with_context(bi_lifecycle_engine=True).write({"state": "review"})
            rec.message_post(body=_("Review started — steward: %s.") % rec.steward_id.display_name)
        return True

    def action_certify(self):
        """The engine calls this AS THE CERTIFIER once the request is granted.
        G8 SoD: the author never certifies their own content."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state not in ("draft", "review"):
                raise UserError(_("Only a draft or in-review dashboard can be certified."))
            approver = self.env.user
            if approver.id == rec.owner_id.id:
                raise UserError(
                    _(
                        "The author cannot certify their own dashboard (spec §13 SoD) — the request must be decided by another certifier."
                    )
                )
            rec.with_context(bi_lifecycle_engine=True).write(
                {
                    "state": "certified",
                    "certified_by": approver.id,
                    "certified_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body=_("Certified by %s through an approved request (M63).") % approver.name
            )
        return True

    def action_retire(self):
        """Certified -> retired: a steward/officer act (spec §8.1 step 8)."""
        for rec in self:
            if rec.state != "certified":
                raise UserError(_("Only a certified dashboard can be retired."))
            if not (self.env.su or self.env.user.has_group(CERTIFIER_GROUP)):
                raise UserError(_("Retiring a certified dashboard is a data-steward act (M25)."))
            rec.with_context(bi_lifecycle_engine=True).write(
                {
                    "state": "retired",
                    "retired_by": self.env.user.id,
                    "retired_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body=_("Retired by %s.") % self.env.user.name)
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec.message_post(body=_("Certification request rejected: %s") % (comment or ""))


class FixBiDistributionSchedule(models.Model):
    """A scheduled distribution of one report pack (cadence + recipients).

    G8: the report key must exist in the M25 report library; every recipient
    must be an ACTIVE INTERNAL USER of the company (the internal-domain
    allow-list — an address nobody logs in with is refused at save time and
    re-checked at send time, when the recipient must ALSO still hold the
    pack's entitlement group)."""

    _name = "fix.bi.distribution.schedule"
    _description = "BI Distribution Schedule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    report_key = fields.Char(
        required=True,
        help="The report to distribute, as module:report (e.g. M25:branch_league). "
        "Validated against the report library — an unknown key is refused.",
    )
    cadence = fields.Selection(
        [("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly")],
        required=True,
        default="weekly",
    )
    recipients = fields.Char(
        required=True,
        help="Comma-separated e-mail addresses. Each must belong to an active "
        "internal user (the internal allow-list) entitled to the pack; "
        "entitlement is re-checked at every send.",
    )
    format = fields.Selection(
        [("csv", "CSV"), ("pdf", "PDF"), ("xlsx", "XLSX")],
        required=True,
        default="csv",
    )
    active = fields.Boolean(default=True)
    last_sent_at = fields.Datetime(readonly=True)
    last_status = fields.Selection(
        [("never", "Never Sent"), ("sent", "Sent"), ("failed", "Failed"), ("partial", "Partial")],
        required=True,
        default="never",
        readonly=True,
    )
    last_note = fields.Char(readonly=True)
    note = fields.Char(help="Free note for the distribution owner.")

    # ---- validation -------------------------------------------------------

    @api.model
    def _valid_report_keys(self):
        """The report library the portal registers (controllers/a11/m25.py).
        Read dynamically so the module never hard-codes a second list that
        would drift from the real one."""
        try:
            from odoo.addons.cd_p03_portal.controllers.a11 import m25
        except ImportError:
            return set()
        return {"M25:%s" % key for key in getattr(m25, "REPORTS", {})}

    @api.constrains("report_key")
    def _check_report_key(self):
        valid = self._valid_report_keys()
        for rec in self:
            if rec.report_key and rec.report_key not in valid:
                raise ValidationError(
                    _("Report key %r is not in the M25 report library. Valid keys: %s.")
                    % (rec.report_key, ", ".join(sorted(valid)) or "(library unavailable)")
                )

    def _recipients_list(self):
        self.ensure_one()
        return [r.strip() for r in (self.recipients or "").split(",") if r.strip()]

    def _resolve_recipient(self, email):
        """The active internal user owning this address, or None (the
        internal-domain allow-list: an address no user owns is refused)."""
        Users = self.env["res.users"].sudo().with_context(active_test=True)
        return Users.search([("login", "=ilike", email)], limit=1) or Users.search(
            [("email", "=ilike", email)], limit=1
        )

    @api.constrains("recipients")
    def _check_recipients(self):
        for rec in self:
            for email in rec._recipients_list():
                user = rec._resolve_recipient(email)
                if not user:
                    raise ValidationError(
                        _(
                            "Recipient %r is not an active internal user — external addresses are not allowed on BI distributions (G8)."
                        )
                        % email
                    )
                if user.company_id and user.company_id != rec.company_id:
                    raise ValidationError(
                        _("Recipient %r belongs to another company.") % user.display_name
                    )

    # ---- the worker (G8) --------------------------------------------------

    def _pack_out(self):
        """Render the pack once, under the schedule's company scope."""
        self.ensure_one()
        _, _, report = self.report_key.partition(":")
        try:
            from odoo.addons.cd_p03_portal.controllers.a11 import m25
        except ImportError as exc:
            raise UserError(_("The report library is unavailable: %s") % exc) from exc
        fn = getattr(m25, "REPORTS", {}).get(report)
        if fn is None:
            raise UserError(_("Report key %r is not in the report library.") % self.report_key)
        env = self.with_context(allowed_company_ids=self.company_id.ids).sudo().env
        return fn(env)

    def _pack_csv(self, out):
        header = out.get("labels") or {}
        lines = [",".join(header.get(c, c) for c in out.get("cols") or [])]
        for row in out.get("rows") or []:
            lines.append(
                ",".join(
                    '"%s"' % str(row.get(c, "")).replace('"', "'") for c in out.get("cols") or []
                )
            )
        text = "\n".join(lines)
        return ("Report %s\n\n%s" % (self.report_key, text)).encode("utf-8")

    def _dispatch_one(self):
        """Send one schedule now: validate the key, re-check every
        recipient's entitlement, mail the entitled ones, log the dispatch."""
        self.ensure_one()
        out = self._pack_out()
        required_group = _pack_required_group(self.report_key)
        sent, skipped = 0, []
        for email in self._recipients_list():
            user = self._resolve_recipient(email)
            reason = None
            if not user:
                reason = "no longer an active internal user"
            elif required_group and not user.has_group(required_group):
                reason = "lost the pack entitlement (%s)" % required_group.split(".")[-1]
            if reason:
                skipped.append("%s (%s)" % (email, reason))
                continue
            self.env["mail.mail"].sudo().create(
                {
                    "subject": "[1000FiX BI] %s" % (out.get("title") or self.report_key),
                    "body_html": "<pre>%s</pre>"
                    % ((out.get("title") or self.report_key).replace("<", "&lt;")),
                    "email_to": email,
                    "auto_delete": False,
                    "attachment_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "%s.csv" % self.report_key.replace(":", "_"),
                                "datas": base64.b64encode(self._pack_csv(out)).decode("ascii"),
                            },
                        )
                    ],
                }
            )
            sent += 1
        self.env["fix.bi.export.log"].sudo().create(
            {
                "user_id": self.env.user.id,
                "pack": self.report_key,
                "channel": "distribution",
                "format": "csv",
                "company_ids": self.company_id.name,
                "row_count": len(out.get("rows") or []),
            }
        )
        status = "sent" if sent and not skipped else ("partial" if sent else "failed")
        self.with_context(bi_distribution_worker=True).write(
            {
                "last_sent_at": fields.Datetime.now(),
                "last_status": status,
                "last_note": "sent %d, skipped %d%s"
                % (sent, len(skipped), (": " + "; ".join(skipped)) if skipped else ""),
            }
        )
        return status

    def action_send_now(self):
        for rec in self:
            rec._dispatch_one()
        return True

    @api.model
    def _cron_dispatch(self):
        """The distribution worker: every active schedule whose cadence came
        due. Failures are recorded on the schedule, never silent."""
        today = fields.Date.today()
        ran = 0
        for rec in self.sudo().search([("active", "=", True)]):
            if not rec.last_sent_at:
                due = True
            else:
                last = rec.last_sent_at.date()
                due = (
                    rec.cadence == "daily"
                    or (rec.cadence == "weekly" and (today - last).days >= 7)
                    or (rec.cadence == "monthly" and (today - last).days >= 28)
                )
            if not due:
                continue
            try:
                rec._dispatch_one()
                ran += 1
            except (UserError, ValidationError) as exc:
                rec.with_context(bi_distribution_worker=True).write(
                    {"last_status": "failed", "last_note": str(exc)[:500]}
                )
                _logger.warning("M25 distribution failed for %s: %s", rec.display_name, exc)
        _logger.info("M25 distribution worker: %d schedule(s) dispatched", ran)
        return ran


class FixBiAlertSubscription(models.Model):
    """A threshold alert on any KPI metric key.

    G8 (M25-8) closes the alert half of the finding: `metric_key` is
    validated against the live metric bank (an unknown key is refused at
    save time — an alert can no longer watch a metric nobody computes), and
    `_cron_evaluate` is the missing runner: it measures the watched metric
    under the alert's company scope, stamps last_value/last_checked_at, and
    records a fire when the threshold is crossed. Outbound notification
    transport stays declared porting phase and is never simulated."""

    _name = "fix.bi.alert.subscription"
    _description = "BI Threshold Alert"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    metric_key = fields.Char(
        required=True, help="KPI key to watch, e.g. overdue_gt_60d or ar_invoices_mtd."
    )
    comparator = fields.Selection(
        [("gt", "Greater than"), ("lt", "Less than")], required=True, default="gt"
    )
    threshold = fields.Float(required=True)
    recipients = fields.Char(required=True, help="Comma-separated e-mail addresses.")
    active = fields.Boolean(default=True)
    last_value = fields.Float(readonly=True)
    last_checked_at = fields.Datetime(readonly=True)
    last_fired_at = fields.Datetime(readonly=True)
    note = fields.Char(
        help="The watched metric is visible live on the role dashboards; outbound "
        "notification transport is porting phase and is never simulated."
    )

    # ---- validation (G8 / M25-8) -------------------------------------------

    @api.model
    def _known_metric_keys(self):
        """The metric bank the portal computes (controllers/a11/m25.py),
        resolved under the superuser so the key list never depends on the
        saving user's read scope — the keys are code, not data."""
        try:
            from odoo.addons.cd_p03_portal.controllers.a11 import m25
        except ImportError:
            return set()
        try:
            return set(m25._metrics(self.env(su=True)))
        except Exception as exc:
            _logger.warning("M25 metric bank unavailable to the alert constraint: %s", exc)
            return set()

    @api.constrains("metric_key")
    def _check_metric_key(self):
        keys = self._known_metric_keys()
        if not keys:
            return  # library unavailable: never guess on the user's behalf
        for rec in self:
            if rec.metric_key and rec.metric_key not in keys:
                raise ValidationError(
                    _(
                        "Metric key %r is not computed by the M25 metric bank — an "
                        "alert may only watch a metric the platform actually "
                        "measures (G8). Known keys: %s."
                    )
                    % (rec.metric_key, ", ".join(sorted(keys)))
                )

    # ---- the evaluator (G8 / M25-8) ----------------------------------------

    def _current_value(self):
        """The watched metric measured under the ALERT's company scope."""
        self.ensure_one()
        from odoo.addons.cd_p03_portal.controllers.a11 import m25

        env = self.with_context(allowed_company_ids=self.company_id.ids).sudo().env
        value = m25._metrics(env).get(self.metric_key)
        return value if isinstance(value, int | float) else None

    def _evaluate(self):
        """Measure once, stamp the read, record a fire on crossing."""
        self.ensure_one()
        value = self._current_value()
        if value is None:
            # not computable under this scope: stated as never checked,
            # never silently treated as zero
            return False
        crossed = value > self.threshold if self.comparator == "gt" else value < self.threshold
        self.with_context(bi_alert_engine=True).write(
            {"last_value": value, "last_checked_at": fields.Datetime.now()}
        )
        if crossed:
            self.with_context(bi_alert_engine=True).write({"last_fired_at": fields.Datetime.now()})
            _logger.info(
                "M25 alert %s fired: %s = %s %s %s",
                self.display_name,
                self.metric_key,
                value,
                ">" if self.comparator == "gt" else "<",
                self.threshold,
            )
        return crossed

    @api.model
    def _cron_evaluate(self):
        """The alert runner: every active subscription evaluated hourly."""
        ran = fired = 0
        for rec in self.sudo().search([("active", "=", True)]):
            try:
                with self.env.cr.savepoint():
                    if rec._evaluate():
                        fired += 1
                ran += 1
            except Exception as exc:
                _logger.warning("M25 alert %s could not evaluate: %s", rec.display_name, exc)
        _logger.info("M25 alert evaluator: %d alert(s) checked, %d fired", ran, fired)
        return {"checked": ran, "fired": fired}


class FixApprovalMatrixM25Domains(models.Model):
    """The M25 governance decision domain on the DoA matrix."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("bi_content", "BI Content Certification")],
        ondelete=dict.fromkeys(("bi_content",), "cascade"),
    )
