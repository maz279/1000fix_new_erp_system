# fix_msp_rules_bru — the M05 business rules the bidirectional audit (2026-11-13)
# found with nothing behind them. Each class names its rule.
#
#   BRU-RMS-02  unattended access only on a contract that grants it
#   BRU-RMS-05  SLA clocks run on the contracted coverage window
#   BRU-RMS-07  devices beyond the contracted count are billed or uplifted,
#               never absorbed
#   BRU-RMS-10  the third incident on an asset in a rolling period is linked
#               to a problem record before it is resolved
#   BRU-RMS-11  offboarding completes only when every agent is removed and
#               access is revoked, each evidenced
#   BRU-RMS-12  session recordings are kept per the contract, and every
#               opening of one is logged
#
# FILE NAME IS LOAD-BEARING: sorts (and so imports) after fix_msp_rules.
import re
from datetime import datetime, time, timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .msp_roles import GROUP_ENGINEER, require_role

BD_TZ = pytz.timezone("Asia/Dhaka")
# Bangladesh working week: Sunday to Thursday (Friday and Saturday are the weekend)
BUSINESS_DAYS = {6, 0, 1, 2, 3}  # date.weekday(): Mon=0 … Sun=6
BUSINESS_START, BUSINESS_END = time(9, 0), time(18, 0)
RECURRENCE_PARAM = "cd_msp_contract.recurring_incident_threshold"
RECURRENCE_DAYS_PARAM = "cd_msp_contract.recurring_incident_days"
EVIDENCE_MIN = 10


def _evidence(text, what):
    text = (text or "").strip()
    if len(text) < EVIDENCE_MIN:
        raise UserError(
            "Record the evidence for %s (at least %d characters)." % (what, EVIDENCE_MIN)
        )
    return text


def add_business_hours(start_utc, hours, holidays=frozenset()):
    """``start_utc`` (naive UTC) plus ``hours`` of Sunday–Thursday 09:00–18:00
    Asia/Dhaka working time, as naive UTC. A date in ``holidays`` (the
    contract's holiday calendar) is closed like the weekend."""
    local = pytz.utc.localize(start_utc).astimezone(BD_TZ).replace(tzinfo=None)
    remaining = timedelta(hours=hours)
    for _ in range(3660):  # ten years of days: a target never runs that long
        day_open = datetime.combine(local.date(), BUSINESS_START)
        day_close = datetime.combine(local.date(), BUSINESS_END)
        open_day = local.weekday() in BUSINESS_DAYS and local.date() not in holidays
        if open_day and local < day_close:
            begin = max(local, day_open)
            available = day_close - begin
            if remaining <= available:
                end = begin + remaining
                return BD_TZ.localize(end).astimezone(pytz.utc).replace(tzinfo=None)
            remaining -= available
        local = datetime.combine(local.date() + timedelta(days=1), BUSINESS_START)
    raise UserError("The SLA target is longer than the working calendar can measure.")


class FixMspContractBru(models.Model):
    _inherit = "fix.msp.contract"

    # BRU-RMS-02
    unattended_access = fields.Boolean(
        string="Unattended Access Granted",
        tracking=True,
        help="The contract allows sessions on its assets with no client user at the "
        "device. Without it every session is attended.",
    )
    # BRU-RMS-05
    coverage_window = fields.Selection(
        [("24x7", "24 × 7"), ("business", "Business Hours (Sun–Thu 09:00–18:00)")],
        string="SLA Coverage Window",
        default="24x7",
        required=True,
        tracking=True,
        help="The hours in which the resolution clock runs (BRU-RMS-05).",
    )
    holiday_calendar_id = fields.Many2one(
        "fix.working.calendar",
        string="Holiday Calendar",
        tracking=True,
        help="Business-hours SLA clocks stop on this calendar's holidays and closures. "
        "Empty: only the Friday–Saturday weekend is closed.",
    )
    # BRU-RMS-12
    recording_retention_days = fields.Integer(
        string="Recording Retention (days)",
        default=365,
        tracking=True,
        help="How long a session recording reference is kept after the session ends; "
        "0 keeps it for the life of the contract.",
    )
    # BRU-RMS-07
    enrolled_count = fields.Integer(compute="_compute_enrolled_count", string="Enrolled Devices")
    # BRU-RMS-11
    lifecycle = fields.Selection(
        [
            ("in_service", "In Service"),
            ("offboarding", "Offboarding"),
            ("offboarded", "Offboarded"),
        ],
        string="Service Lifecycle",
        default="in_service",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )
    offboarding_started_at = fields.Datetime(readonly=True, copy=False)
    access_revoked_at = fields.Datetime(string="Access Revoked At", readonly=True, copy=False)
    access_revoked_evidence = fields.Text(
        string="Access Revocation Evidence", readonly=True, copy=False
    )
    offboarded_at = fields.Datetime(string="Offboarded At", readonly=True, copy=False)
    offboarded_by_id = fields.Many2one(
        "res.users", string="Offboarded By", readonly=True, copy=False
    )

    @api.depends("asset_ids")
    def _compute_enrolled_count(self):
        for msp in self:
            msp.enrolled_count = len(msp.asset_ids)

    @api.constrains("device_count")
    def _check_device_count_covers_estate(self):
        for msp in self:
            enrolled = msp._msp_enrolled()
            if msp.device_count and msp.device_count < enrolled:
                raise ValidationError(
                    "MSP contract %s already monitors %d devices: the covered devices "
                    "cannot drop to %d. Offboard devices first."
                    % (msp.name, enrolled, msp.device_count)
                )

    def _msp_enrolled(self) -> int:
        """Assets enrolled on this contract, counted in the database (the
        one2many cache can hold a row a refused save rolled back)."""
        self.ensure_one()
        return (
            self.env["fix.monitored.asset"].sudo().search_count([("msp_contract_id", "=", self.id)])
        )

    @api.constrains("recording_retention_days")
    def _check_retention(self):
        for msp in self:
            if msp.recording_retention_days < 0:
                raise ValidationError("The recording retention cannot be negative.")

    # ---- BRU-RMS-05 -------------------------------------------------------
    def _msp_deadline(self, alert, kind="resolve"):
        """When ``alert`` breaches: its severity's target in the contracted
        coverage window. 24 × 7 adds clock hours; business hours count only
        Sun–Thu 09:00–18:00 in Dhaka, so an alert raised on Thursday evening
        is not breached over the weekend.

        A02 ERP pass 2 (M05-S13): the target, window and holidays are the
        terms in force when the alert was raised, not today's; ``kind``
        "response" gives the response deadline (None when the contract sets
        no response target)."""
        self.ensure_one()
        raised = alert.create_date or fields.Datetime.now()
        terms = self._msp_terms_at(raised)
        if kind == "response":
            name = "response_hours_%s" % ("major" if alert.severity == "major" else "minor")
            hours = terms[name] or 0.0
            if hours <= 0:
                return None
        else:
            hours = self._msp_target_hours(alert)
        if terms.coverage_window == "business":
            return add_business_hours(
                raised, hours, self._msp_holiday_dates_of(terms.holiday_calendar_id)
            )
        return raised + timedelta(hours=hours)

    def _msp_holiday_dates(self):
        """Every closed date of the contract's holiday calendar."""
        self.ensure_one()
        days = set()
        for holiday in self.holiday_calendar_id.sudo().holiday_ids:
            day = holiday.date_from
            while day <= holiday.date_to:
                days.add(day)
                day += timedelta(days=1)
        return frozenset(days)

    def _msp_period_sla(self, alerts, as_of=None) -> dict:
        """As before (within / breached / pending), with the deadline taken
        from the coverage window instead of always counting clock hours."""
        self.ensure_one()
        as_of = as_of or fields.Datetime.now()
        within = breached = pending = response_breached = 0
        tta, ttr = [], []
        for alert in alerts:
            # A02 ERP pass 2 (M05-S02 / S18): the deadline stamped when the
            # alert was raised, extended by its waiting-on-client pauses; the
            # response target counts too when the contract sets one.
            until = alert.resolved_at if alert.state == "resolved" else as_of
            deadline = alert._msp_effective_deadline("resolve", until)
            respond = alert._msp_effective_deadline("response", alert.responded_at or until)
            paused = alert._msp_paused_seconds(until)
            missed_response = bool(
                respond
                and (
                    (alert.responded_at and alert.responded_at > respond)
                    or (not alert.responded_at and until > respond)
                )
            )
            response_breached += int(missed_response)
            if alert.responded_at:
                tta.append((alert.responded_at - alert.create_date).total_seconds() / 60.0)
            if alert.state == "resolved":
                if alert.resolved_at:
                    ttr.append(
                        max((alert.resolved_at - alert.create_date).total_seconds() - paused, 0)
                        / 60.0
                    )
                if alert.resolved_at and alert.resolved_at <= deadline and not missed_response:
                    within += 1
                else:
                    breached += 1
            elif as_of > deadline or missed_response:
                breached += 1
            else:
                pending += 1
        measured = within + breached
        return {
            "within": within,
            "breached": breached,
            "pending": pending,
            "response_breached": response_breached,
            "mtta_minutes": round(sum(tta) / len(tta), 1) if tta else 0.0,
            "mttr_minutes": round(sum(ttr) / len(ttr), 1) if ttr else 0.0,
            "attainment": round(within / measured, 4) if measured else 1.0,
        }

    # ---- BRU-RMS-11 -------------------------------------------------------
    def _msp_assert_in_service(self, what):
        for msp in self:
            if msp.lifecycle != "in_service":
                raise UserError(
                    "%s is refused: MSP contract %s is %s." % (what, msp.name, msp.lifecycle)
                )

    def action_start_offboarding(self):
        require_role(self.env, [GROUP_ENGINEER], "Starting a client offboarding")
        for msp in self:
            if msp.lifecycle != "in_service":
                raise UserError("MSP contract %s is already %s." % (msp.name, msp.lifecycle))
            msp._guarded().write(
                {"lifecycle": "offboarding", "offboarding_started_at": fields.Datetime.now()}
            )
            msp.message_post(body="Offboarding started by %s." % self.env.user.name)
        return True

    def action_record_access_revoked(self, evidence=None):
        """Every client credential, portal user and remote-access grant of
        this contract is revoked; the evidence says how it was checked."""
        require_role(self.env, [GROUP_ENGINEER], "Recording access revocation")
        text = _evidence(evidence, "the access revocation")
        for msp in self:
            if msp.lifecycle != "offboarding":
                raise UserError("Access is revoked during offboarding: start it first.")
            msp._guarded().write(
                {
                    "access_revoked_at": fields.Datetime.now(),
                    "access_revoked_evidence": text,
                }
            )
            msp.message_post(body="Access revoked (%s): %s" % (self.env.user.name, text))
        return True

    def action_complete_offboarding(self):
        """BRU-RMS-11: complete only when every agent is removed and access is
        revoked, each with its evidence."""
        require_role(self.env, [GROUP_ENGINEER], "Completing a client offboarding")
        for msp in self:
            if msp.lifecycle != "offboarding":
                raise UserError("MSP contract %s is not offboarding." % msp.name)
            left = msp.asset_ids.filtered(lambda a: not a.agent_removed_at)
            if left:
                raise UserError(
                    "Offboarding of %s is not complete: the agent is still on %s. Record "
                    "each agent's removal with its evidence (BRU-RMS-11)."
                    % (msp.name, ", ".join(left.mapped(lambda a: a.hostname or a.agent_id)))
                )
            if not msp.access_revoked_at:
                raise UserError(
                    "Offboarding of %s is not complete: record that the client's access "
                    "is revoked, with its evidence (BRU-RMS-11)." % msp.name
                )
            msp._guarded().write(
                {
                    "lifecycle": "offboarded",
                    "offboarded_at": fields.Datetime.now(),
                    "offboarded_by_id": self.env.uid,
                }
            )
            msp.message_post(
                body="Offboarding completed by %s: %d agent(s) removed, access revoked."
                % (self.env.user.name, len(msp.asset_ids))
            )
        return True


class FixMonitoredAssetBru(models.Model):
    _inherit = "fix.monitored.asset"

    # BRU-RMS-11
    agent_removed_at = fields.Datetime(string="Agent Removed At", readonly=True, copy=False)
    agent_removal_evidence = fields.Text(string="Agent Removal Evidence", readonly=True, copy=False)

    @api.constrains("msp_contract_id")
    def _check_contract_capacity(self):
        """BRU-RMS-07: a device beyond the contracted count is not absorbed.
        Raise the covered devices (an uplift, billed at the per-device price)
        before enrolling it. A contract with no count bills every enrolled
        device."""
        for msp in self.mapped("msp_contract_id"):
            enrolled = msp._msp_enrolled()
            # A02 ERP audit M05-F4: a contract with no covered-device count
            # enrolled without limit, and billing never saw the devices. A
            # device is enrolled only against a contracted count (fail closed).
            if not msp.device_count:
                raise ValidationError(
                    "MSP contract %s has no contracted device count, so no device can be "
                    "enrolled on it: the commercial approver sets the covered devices (Amend "
                    "Commercial Terms) first (BRU-RMS-07)." % msp.name
                )
            if enrolled > msp.device_count:
                raise ValidationError(
                    "MSP contract %s covers %d devices and this would be device %d. Raise "
                    "the covered devices on the contract (an uplift, billed at the "
                    "per-device price) before enrolling another (BRU-RMS-07)."
                    % (msp.name, msp.device_count, enrolled)
                )

    @api.model_create_multi
    def create(self, vals_list):
        contracts = self.env["fix.msp.contract"].browse(
            [v["msp_contract_id"] for v in vals_list if v.get("msp_contract_id")]
        )
        contracts._msp_assert_in_service("Enrolling an asset")
        return super().create(vals_list)

    def action_record_agent_removal(self, evidence=None):
        require_role(self.env, [GROUP_ENGINEER], "Recording an agent removal")
        text = _evidence(evidence, "the agent removal")
        for asset in self:
            if asset.msp_contract_id.lifecycle != "offboarding":
                raise UserError(
                    "Agents are removed during offboarding: start the offboarding of %s first."
                    % asset.msp_contract_id.name
                )
            if asset.agent_removed_at:
                raise UserError(
                    "The agent on %s is already recorded as removed." % asset.display_name
                )
            asset.write({"agent_removed_at": fields.Datetime.now(), "agent_removal_evidence": text})
            asset.message_post(body="Agent removed (%s): %s" % (self.env.user.name, text))
        return True


class FixRemoteSessionBru(models.Model):
    _inherit = "fix.remote.session"

    # BRU-RMS-02
    access_mode = fields.Selection(
        [("attended", "Attended (client user present)"), ("unattended", "Unattended")],
        string="Access Mode",
        default="attended",
        required=True,
    )
    # BRU-RMS-12
    recording_purged_at = fields.Datetime(string="Recording Purged At", readonly=True, copy=False)
    recording_access_count = fields.Integer(
        string="Recording Opened", readonly=True, copy=False, default=0
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"recording_purged_at", "recording_access_count"}

    @api.constrains("access_mode", "msp_contract_id")
    def _check_unattended_granted(self):
        for session in self:
            if (
                session.access_mode == "unattended"
                and not session.msp_contract_id.unattended_access
            ):
                raise ValidationError(
                    "MSP contract %s does not grant unattended access: the session must be "
                    "attended by a client user (BRU-RMS-02)." % session.msp_contract_id.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        contracts = self.env["fix.msp.contract"].browse(
            [v["msp_contract_id"] for v in vals_list if v.get("msp_contract_id")]
        )
        contracts._msp_assert_in_service("Opening a remote session")
        return super().create(vals_list)

    def action_start(self):
        for session in self:
            session.msp_contract_id._msp_assert_in_service("Starting a remote session")
            if (
                session.access_mode == "unattended"
                and not session.msp_contract_id.unattended_access
            ):
                raise UserError(
                    "MSP contract %s does not grant unattended access (BRU-RMS-02)."
                    % session.msp_contract_id.name
                )
        return super().action_start()

    def action_open_recording(self):
        """BRU-RMS-12: the recording reference is shown to the person who asks,
        and the opening is logged on the session."""
        self.ensure_one()
        require_role(self.env, [GROUP_ENGINEER], "Opening a session recording")
        if not self.recording_url:
            raise UserError(
                "This session has no recording reference%s."
                % (" (purged under the retention rule)" if self.recording_purged_at else "")
            )
        self._guarded().write({"recording_access_count": self.recording_access_count + 1})
        self.message_post(body="Session recording opened by %s." % self.env.user.name)
        return {
            "secret": self.recording_url,
            "note": "Session recording reference (opening logged)",
        }

    @api.model
    def cron_purge_recordings(self):
        """BRU-RMS-12: drop the recording reference of a session ended longer
        ago than its contract's retention (0 = keep for the contract's life)."""
        now = fields.Datetime.now()
        purged = 0
        sessions = self.sudo().search([("ended_at", "!=", False), ("recording_url", "!=", False)])
        for session in sessions:
            days = session.msp_contract_id.recording_retention_days
            if days and session.ended_at < now - timedelta(days=days):
                session._guarded().write({"recording_url": False, "recording_purged_at": now})
                session.message_post(
                    body="Recording reference purged: %d-day retention elapsed." % days
                )
                purged += 1
        return purged


class FixMspAlertBru(models.Model):
    _inherit = "fix.msp.alert"

    # BRU-RMS-10
    problem_id = fields.Many2one(
        "fix.msp.change.record",
        string="Problem Record",
        domain=[("kind", "=", "problem")],
        ondelete="set null",
        help="The problem record a recurring incident is linked to (BRU-RMS-10).",
    )
    recurring = fields.Boolean(
        compute="_compute_recurring",
        string="Recurring",
        help="This asset has had the threshold number of alerts in the rolling period.",
    )

    @api.constrains("problem_id")
    def _check_problem_kind(self):
        for alert in self:
            if alert.problem_id and alert.problem_id.kind != "problem":
                raise ValidationError("Link the incident to a problem record, not a change.")

    def _msp_recurrence(self):
        params = self.env["ir.config_parameter"].sudo()
        threshold = int(params.get_param(RECURRENCE_PARAM, "3") or 3)
        days = int(params.get_param(RECURRENCE_DAYS_PARAM, "30") or 30)
        return threshold, days

    def _msp_recent_count(self):
        self.ensure_one()
        threshold, days = self._msp_recurrence()
        since = (self.create_date or fields.Datetime.now()) - timedelta(days=days)
        return self.sudo().search_count(
            [
                ("asset_id", "=", self.asset_id.id),
                ("create_date", ">=", since),
                ("create_date", "<=", self.create_date or fields.Datetime.now()),
            ]
        )

    def _compute_recurring(self):
        for alert in self:
            threshold, _days = alert._msp_recurrence()
            alert.recurring = bool(alert.id) and alert._msp_recent_count() >= threshold

    def _msp_needs_problem(self) -> bool:
        self.ensure_one()
        return self.recurring and not self.problem_id

    def action_resolve(self, note=""):
        """BRU-RMS-10: the third incident on an asset in the rolling period is
        linked to a problem record (root cause and permanent fix) before it
        is closed as just another fix."""
        for alert in self:
            if alert._msp_needs_problem():
                threshold, days = alert._msp_recurrence()
                raise UserError(
                    "%s has had %d alerts in %d days: link this one to a problem record "
                    "before resolving it (BRU-RMS-10)."
                    % (
                        alert.asset_id.hostname or alert.asset_id.agent_id,
                        alert._msp_recent_count(),
                        days,
                    )
                )
        return super().action_resolve(note=note)


# ---- BRU-RMS-03: credentials are vaulted, never written in a ticket or note --
# A secret typed as "password: ..." (or pwd / PIN / passphrase / secret / API
# key / token, followed by ":" or "=" and a value) is refused wherever an M05
# user writes free text. The vault (M28) is where client credentials live.
CREDENTIAL = re.compile(
    r"\b(pass(word|wd|phrase)?|pwd|pin|secret|api[\s_-]?key|access[\s_-]?key|token)\b"
    r"\s*[:=]\s*\S+",
    re.IGNORECASE,
)
# A02 ERP pass 2 (M05-S19): every free-text field an M05 user writes (the
# guard covered six models and missed the evidence, notes and reasons of the
# rest), and the chatter (message_post) of every guarded model.
FREE_TEXT = {
    "fix.msp.alert": ("message", "resolution_note", "reclassified_reason"),
    "fix.remote.session": ("session_summary", "recording_url"),
    "fix.msp.runbook": ("name", "script"),
    "fix.msp.runbook.run": ("output_note",),
    "fix.msp.change.record": (
        "name",
        "description",
        "rollback_plan",
        "resolution_note",
        "pir_note",
    ),
    "fix.msp.backup.job": ("note", "plan_ref"),
    "fix.msp.contract": ("access_revoked_evidence", "data_return_evidence"),
    "fix.monitored.asset": ("agent_removal_evidence",),
    "fix.msp.patch.update": (
        "title",
        "fail_note",
        "test_note",
        "exception_reason",
        "client_approval_evidence",
    ),
    "fix.msp.sla.credit": ("reason", "dofa_justification"),
    "fix.msp.maintenance.window": ("name", "purpose"),
    "fix.msp.major.incident": ("name", "impact", "resolution_note", "review_note"),
    "fix.msp.service.review": ("attendees", "summary"),
    "fix.msp.review.action": ("name",),
    "fix.msp.dr.plan": ("scope",),
    "fix.msp.dr.test": ("evidence",),
    "fix.msp.roadmap.item": ("name", "description"),
    "fix.msp.onboarding": ("notes",),
    "fix.msp.onboarding.step": ("evidence",),
    "fix.msp.alert.pause": ("reason",),
}

_CREDENTIAL_REFUSAL = (
    "%s holds what looks like a credential. Client credentials are kept in the "
    "credential vault, never in a ticket or note (BRU-RMS-03): remove it and refer to "
    "the vault entry instead."
)


def _assert_no_credentials(model, vals_list):
    for vals in vals_list:
        for name in FREE_TEXT.get(model._name, ()):
            text = vals.get(name)
            if isinstance(text, str) and CREDENTIAL.search(text):
                field = model._fields.get(name)
                raise ValidationError(_CREDENTIAL_REFUSAL % (field.string if field else name))


def check_message_body(kwargs):
    """A note typed on the chatter is free text too (M05-S19). Called from
    each model's own message_post: a mixin's override would sit behind
    mail.thread in the method order and never run."""
    body = kwargs.get("body")
    if body and CREDENTIAL.search(re.sub(r"<[^>]+>", " ", str(body))):
        raise ValidationError(_CREDENTIAL_REFUSAL % "The message")


class _NoCredentials(models.AbstractModel):
    _name = "fix.msp.no.credentials.mixin"
    _description = "BRU-RMS-03 credential guard"

    @api.model_create_multi
    def create(self, vals_list):
        _assert_no_credentials(self, vals_list)
        return super().create(vals_list)

    def write(self, vals):
        _assert_no_credentials(self, [vals])
        return super().write(vals)


class FixMspAlertNoCred(models.Model):
    _name = "fix.msp.alert"
    _inherit = ["fix.msp.alert", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixRemoteSessionNoCred(models.Model):
    _name = "fix.remote.session"
    _inherit = ["fix.remote.session", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspRunbookNoCred(models.Model):
    _name = "fix.msp.runbook"
    _inherit = ["fix.msp.runbook", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspRunbookRunNoCred(models.Model):
    _name = "fix.msp.runbook.run"
    _inherit = ["fix.msp.runbook.run", "fix.msp.no.credentials.mixin"]


class FixMspChangeRecordNoCred(models.Model):
    _name = "fix.msp.change.record"
    _inherit = ["fix.msp.change.record", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspBackupJobNoCred(models.Model):
    _name = "fix.msp.backup.job"
    _inherit = ["fix.msp.backup.job", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)
