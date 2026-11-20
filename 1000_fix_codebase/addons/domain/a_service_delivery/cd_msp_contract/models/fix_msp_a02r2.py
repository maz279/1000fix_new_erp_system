# fix_msp_a02r2 — A02 ERP pass-2 audit (2026-11-20), builder stream S4, M05.
#
#   M05-S02  an alert's contract, asset, severity and source are fixed once it
#            is raised; its SLA deadline is stamped when it is raised (with the
#            terms then in force) and only a reasoned reclassification, while
#            the alert is still new, restamps it.
#   M05-S07  an offboarded contract raises no alert; a terminated or expired
#            M08 contract starts the offboarding; a completed offboarding is
#            published so M39 churns the subscription.
#   M05-S08  the onboarding that has not gone live by the day the SLA binds
#            (target go-live, capped at 30 days from the contract start) is
#            escalated.
#   M05-S11  alerts, service reports and SLA credits carry their contract's
#            company and operating unit.
#   M05-S13  the terms history (fix.msp.terms.amendment): what was in force
#            on any day.
#   M05-S15  the bilingual client service report (PDF) and its delivery to the
#            client's reporting contacts through M27.
#   M05-S16  an MSP ticket escalates to an M02 field order with its context.
#   M05-S17  remote-session time is metered against the hours entitlement:
#            notice at 80 %, overage billed at the contract's rate.
#   M05-S18  response target, first response, waiting-on-client pauses,
#            threshold escalations; MTTA / MTTR on the report and the credit.
#
# FILE NAME IS LOAD-BEARING: imported after fix_msp_a02_controls.
import logging
from datetime import datetime, time, timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_msp_rules_bru import check_message_body
from .msp_periods import BD_TZ, dhaka_month, dhaka_today
from .msp_roles import GROUP_ENGINEER, require_role

_logger = logging.getLogger(__name__)

REASON_MIN = 10
# M05-S18: an open alert is escalated to the next rota level once this share
# of its resolution target has elapsed (a business number)
ESCALATION_PCT_PARAM = "cd_msp_contract.escalation_threshold_pct"
ESCALATION_PCT_DEFAULT = 75.0
# M05-S17 (D11): the client is told at this share of the hours entitlement
HOURS_NOTICE_PCT = 80.0
# M05-S08 (D9): the longest onboarding before the SLA binds
SLA_BIND_CAP_DAYS = 30


def _dhaka_date(stamp):
    """The Dhaka calendar date of a naive-UTC datetime (or a date)."""
    if not stamp:
        return dhaka_today()
    if isinstance(stamp, datetime):
        return pytz.utc.localize(stamp).astimezone(BD_TZ).date()
    return stamp


def _dhaka_midnight_utc(day):
    """Midnight in Dhaka of ``day``, as naive UTC."""
    return BD_TZ.localize(datetime.combine(day, time.min)).astimezone(pytz.utc).replace(tzinfo=None)


# ------------------------------------------------------------ M05-S13 history


class FixMspTermsAmendment(models.Model):
    """One row of a contract's terms history: the terms in force from its
    effective date until the next row (A02 ERP pass 2, M05-S13). Written only
    by action_amend_terms; the M39 consumer reads the money delta from here
    (M05-S05), never from the event."""

    _name = "fix.msp.terms.amendment"
    _description = "MSP Contract Terms History"
    _inherit = ["fix.guarded.mixin"]
    _order = "msp_contract_id, effective_date desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", required=True, index=True, ondelete="cascade"
    )
    kind = fields.Selection(
        [("baseline", "Terms Before the First Amendment"), ("amendment", "Amendment")],
        required=True,
        default="amendment",
    )
    effective_date = fields.Date(required=True, index=True)
    reason = fields.Char()
    amended_by_id = fields.Many2one("res.users", string="Amended By")
    currency_id = fields.Many2one(related="msp_contract_id.currency_id")
    device_count = fields.Integer(string="Covered Devices")
    per_device_monthly = fields.Monetary(currency_field="currency_id")
    monthly_value = fields.Monetary(string="Monthly Fee", currency_field="currency_id")
    sla_target_pct = fields.Float(string="SLA Target %")
    alert_resolve_hours_major = fields.Float(string="Major Resolution (h)")
    alert_resolve_hours_minor = fields.Float(string="Minor Resolution (h)")
    response_hours_major = fields.Float(string="Major Response (h)")
    response_hours_minor = fields.Float(string="Minor Response (h)")
    coverage_window = fields.Selection(
        [("24x7", "24 × 7"), ("business", "Business Hours")], string="Coverage Window"
    )
    holiday_calendar_id = fields.Many2one("fix.working.calendar", string="Holiday Calendar")
    parts_included = fields.Boolean(string="Parts Entitlement")
    remote_hours_monthly = fields.Float(string="Remote Hours a Month")
    overage_hourly_rate = fields.Monetary(currency_field="currency_id")
    device_count_before = fields.Integer(string="Devices Before")
    per_device_monthly_before = fields.Monetary(
        string="Per-Device Price Before", currency_field="currency_id"
    )
    monthly_value_before = fields.Monetary(
        string="Monthly Fee Before", currency_field="currency_id"
    )
    monthly_delta = fields.Monetary(
        string="Monthly Fee Change",
        currency_field="currency_id",
        compute="_compute_delta",
        store=True,
    )
    billing_state = fields.Selection(
        [
            ("none", "No Fee Change"),
            ("pending", "To Bill (M39)"),
            ("requested", "Price Change Requested"),
            ("billed", "Billed"),
            ("flagged", "Flagged: Not Billed Automatically"),
        ],
        string="Billing",
        default="none",
        required=True,
    )
    billing_ref = fields.Char(string="M39 Price Change")
    billing_note = fields.Char(string="Billing Note")

    def _fix_guarded_fields(self) -> set:
        return set(self._fields) - {
            "id",
            "display_name",
            "create_uid",
            "create_date",
            "write_uid",
            "write_date",
            "currency_id",
            "monthly_delta",
        }

    @api.depends("monthly_value", "monthly_value_before")
    def _compute_delta(self):
        for row in self:
            row.monthly_delta = round(
                (row.monthly_value or 0.0) - (row.monthly_value_before or 0.0), 2
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError("The terms history is written by Amend SLA / Commercial Terms only.")
        return super().create(vals_list)

    def unlink(self):
        if not self._fix_guard_open():
            raise UserError("The terms history is evidence and is not deleted.")
        return super().unlink()


class FixMspContractA02r2(models.Model):
    _inherit = "fix.msp.contract"

    remote_notice_period = fields.Char(
        string="Hours Notice Sent For",
        readonly=True,
        copy=False,
        help="The month (YYYY-MM) the client was last told it used 80 % of its remote hours.",
    )
    remote_exceeded_period = fields.Char(
        string="Hours Exceeded Notice For", readonly=True, copy=False
    )
    remote_minutes_mtd = fields.Float(
        string="Remote Minutes This Month", compute="_compute_remote_usage"
    )
    remote_usage_pct = fields.Float(
        string="Remote Hours Used This Month (%)", compute="_compute_remote_usage"
    )
    report_overdue_activity_period = fields.Char(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "remote_notice_period",
            "remote_exceeded_period",
            "report_overdue_activity_period",
        }

    # ---- M05-S13: the terms in force on a day -----------------------------
    def _msp_terms_at(self, when=None):
        """The terms in force on ``when`` (a UTC datetime or a Dhaka date):
        the latest history row effective on or before it, else the
        contract's own terms (a contract never amended)."""
        self.ensure_one()
        day = _dhaka_date(when)
        row = (
            self.env["fix.msp.terms.amendment"]
            .sudo()
            .search(
                [("msp_contract_id", "=", self.id), ("effective_date", "<=", day)],
                order="effective_date desc, id desc",
                limit=1,
            )
        )
        return row or self.sudo()

    def _msp_holiday_dates_of(self, calendar):
        days = set()
        for holiday in calendar.sudo().holiday_ids:
            day = holiday.date_from
            while day <= holiday.date_to:
                days.add(day)
                day += timedelta(days=1)
        return frozenset(days)

    # ---- M05-S08: when the SLA binds -------------------------------------
    def _msp_sla_binds_at(self):
        """The UTC moment the SLA becomes binding, or None (binding from the
        start). Only a genuine onboarding (opened before any service) defers
        it: to the go-live, but never past the target go-live date, and never
        past 30 days from the contract start (owner decision D9)."""
        self.ensure_one()
        project = self.onboarding_ids.sorted("id")[:1]
        if not project or not project.create_date:
            return None
        if self._msp_service_history(before=project.create_date):
            return None
        start = self.contract_id.sudo().date_start or _dhaka_date(project.create_date)
        cap = _dhaka_midnight_utc(start + timedelta(days=SLA_BIND_CAP_DAYS))
        if project.target_live_date:
            cap = min(cap, _dhaka_midnight_utc(project.target_live_date))
        if self.service_live_at:
            cap = min(cap, self.service_live_at)
        return cap

    # ---- M05-S07: the M08 contract ended ---------------------------------
    def _msp_offboard_on_contract_end(self, contract, why):
        msps = self.sudo().search(
            [("contract_id", "=", contract.id), ("lifecycle", "=", "in_service")]
        )
        for msp in msps:
            msp._guarded().write(
                {"lifecycle": "offboarding", "offboarding_started_at": fields.Datetime.now()}
            )
            msp.message_post(
                body="Offboarding started: the M08 contract %s %s. Remove the agents, revoke "
                "access and return the client's data to complete it (BRU-RMS-11)."
                % (contract.code or contract.name, why)
            )
        return {"offboarding": len(msps)}

    @api.model
    def consume_contract_terminated(self, event: dict) -> dict:
        if not self.env.su:
            raise AccessError("contract.terminated is consumed by the event relay only.")
        payload = event.get("payload") or {}
        if payload.get("kind") and payload.get("kind") != "termination":
            return {"offboarding": 0, "reason": "a suspension does not end the service"}
        contract = self.env["fix.contract"].sudo().browse(int(payload.get("contract_id") or 0))
        contract = contract.exists()
        if not contract or contract.state != "terminated":
            return {"offboarding": 0, "reason": "contract not terminated"}
        return self._msp_offboard_on_contract_end(contract, "was terminated")

    @api.model
    def consume_contract_expired(self, event: dict) -> dict:
        if not self.env.su:
            raise AccessError("contract.expired is consumed by the event relay only.")
        contract = self.env["fix.contract"].sudo().browse(int(event.get("aggregate_id") or 0))
        contract = contract.exists()
        if not contract or contract.state != "expired":
            return {"offboarding": 0, "reason": "contract not expired"}
        return self._msp_offboard_on_contract_end(contract, "expired")

    def action_complete_offboarding(self):
        result = super().action_complete_offboarding()
        for msp in self.filtered(lambda m: m.lifecycle == "offboarded"):
            contract = msp.contract_id.sudo()
            publish(
                self.env,
                "msp.client_offboarded",
                "fix.msp.contract",
                msp.id,
                {
                    "msp_contract_id": msp.id,
                    "contract_id": contract.id,
                    "contract_code": contract.code or "",
                    "offboarded_at": fields.Datetime.to_string(msp.offboarded_at),
                },
            )
        return result

    # ---- M05-S17: remote hours -----------------------------------------
    def _msp_remote_minutes(self, start, end):
        """Metered minutes of the sessions ended in [start, end] (UTC)."""
        self.ensure_one()
        sessions = (
            self.env["fix.remote.session"]
            .sudo()
            .search(
                [
                    ("msp_contract_id", "=", self.id),
                    ("ended_at", ">=", start),
                    ("ended_at", "<=", end),
                ]
            )
        )
        return round(sum(sessions.mapped("duration_minutes")), 1)

    def _compute_remote_usage(self):
        start, end, _label = dhaka_month(dhaka_today())
        for msp in self:
            minutes = msp._msp_remote_minutes(start, end) if msp.id else 0.0
            msp.remote_minutes_mtd = minutes
            hours = msp.remote_hours_monthly or 0.0
            msp.remote_usage_pct = round(100.0 * minutes / 60.0 / hours, 1) if hours else 0.0

    def _msp_meter_hours(self, ended_at):
        """After a session ends: tell the client at 80 % of the month's
        entitlement and again once it is exceeded, once each a month."""
        self.ensure_one()
        hours = self.remote_hours_monthly or 0.0
        if hours <= 0:
            return
        start, end, label = dhaka_month(_dhaka_date(ended_at))
        used = self._msp_remote_minutes(start, end) / 60.0
        pct = 100.0 * used / hours
        msp = self.sudo()
        if pct >= HOURS_NOTICE_PCT and msp.remote_notice_period != label:
            msp._guarded().write({"remote_notice_period": label})
            msp._msp_hours_notice(label, used, hours, "threshold")
        if pct > 100.0 and msp.remote_exceeded_period != label:
            msp._guarded().write({"remote_exceeded_period": label})
            msp._msp_hours_notice(label, used, hours, "exceeded")

    def _msp_hours_notice(self, label, used, hours, kind):
        rate = self.overage_hourly_rate or 0.0
        if kind == "threshold":
            text = "%s has used %.1f of its %.1f remote-support hours for %s (%.0f %%)." % (
                self.name,
                used,
                hours,
                label,
                100.0 * used / hours,
            )
        else:
            text = "%s has exceeded its %.1f remote-support hours for %s (%.1f used): %s" % (
                self.name,
                hours,
                label,
                used,
                "the hours above it are billed at BDT %.2f an hour" % rate
                if rate
                else "the contract has no overage rate, so the excess is flagged, not billed",
            )
        self.message_post(body=text)
        publish(
            self.env,
            "msp.remote_hours_%s" % kind,
            "fix.msp.contract",
            self.id,
            {"period": label, "used_hours": round(used, 2), "entitled_hours": hours},
        )
        self._msp_notify_contacts(
            "msp-hours-%s:%s:%s" % (kind, self.id, label), "Remote support hours", text
        )

    # ---- M27 delivery to the client's contacts ----------------------------
    def _msp_reporting_partners(self):
        self.ensure_one()
        contacts = self.client_contact_ids.filtered(
            lambda c: c.active and c.role in ("it_manager", "viewer")
        )
        partners = contacts.mapped("partner_id")
        return partners or self.contract_id.sudo().customer_id

    def _msp_notify_contacts(self, key, subject, body, partners=None):
        """Queue an e-mail to each reporting contact through M27's one exit
        (consent, provider and evidence apply there). Soft: without M27 the
        message stays on the contract's chatter."""
        self.ensure_one()
        Delivery = self.env.get("fix.notif.delivery")
        if Delivery is None:
            return 0
        queued = 0
        for partner in partners or self._msp_reporting_partners():
            try:
                Delivery.sudo().queue(
                    channel="email",
                    purpose="service_updates",
                    partner=partner,
                    subject=subject,
                    body=body,
                    lawful_basis="contract",
                    source_model=self._name,
                    source_id=self.id,
                    dedup_key="%s:%s" % (key, partner.id),
                    operating_unit=self.operating_unit_id,
                    company=self.company_id,
                )
                queued += 1
            except (UserError, ValidationError) as exc:
                self.message_post(body="%s not sent to %s: %s" % (subject, partner.name, exc))
        return queued

    # ---- M05-S08: overdue onboarding -----------------------------------
    @api.model
    def cron_onboarding_overdue(self):
        """An onboarding not live when the SLA binds is escalated once."""
        now = fields.Datetime.now()
        done = 0
        for project in (
            self.env["fix.msp.onboarding"]
            .sudo()
            .search([("state", "!=", "live"), ("overdue_escalated_at", "=", False)])
        ):
            binds = project.msp_contract_id._msp_sla_binds_at()
            if not binds or binds > now:
                continue
            project._guarded().write({"overdue_escalated_at": now})
            body = (
                "Onboarding %s is not live and the SLA of %s became binding on %s UTC "
                "(target go-live, capped at %d days from the contract start): its alerts "
                "are measured from then. Finish the checklist and go live."
                % (
                    project.name,
                    project.msp_contract_id.name,
                    fields.Datetime.to_string(binds),
                    SLA_BIND_CAP_DAYS,
                )
            )
            project.message_post(body=body)
            user = project.started_by_id or project.create_uid
            if user:
                project.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=user.id,
                    summary="Onboarding overdue: SLA binding",
                    note=body,
                )
            publish(
                self.env,
                "msp.onboarding_overdue",
                "fix.msp.onboarding",
                project.id,
                {"msp_contract_id": project.msp_contract_id.id, "binds_at": str(binds)},
            )
            done += 1
        return done


class FixMspOnboardingA02r2(models.Model):
    _inherit = "fix.msp.onboarding"

    overdue_escalated_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"overdue_escalated_at"}

    def action_go_live(self):
        """M05-S06 (D8): the M39 subscription bills the contract, so the
        service goes live only when exactly one live subscription is there."""
        Sub = self.env.get("fix.subscription")
        if Sub is not None:
            for project in self:
                contract = project.msp_contract_id.contract_id
                live = Sub.sudo().search_count(
                    [
                        ("contract_id", "=", contract.id),
                        ("state", "not in", ("cancelled", "churned")),
                    ]
                )
                if live != 1:
                    raise UserError(
                        "%s cannot go live: the M08 contract %s has %d live M39 subscriptions; "
                        "exactly one bills the managed service. Set up (or close the extra) "
                        "subscription first." % (project.name, contract.display_name, live)
                    )
        return super().action_go_live()


# --------------------------------------------------- alerts (S02 S07 S11 S18)


class FixMspAlertPause(models.Model):
    """A waiting-on-client interval of an alert: the SLA clock stops (M05-S18)."""

    _name = "fix.msp.alert.pause"
    _description = "MSP Alert SLA Pause"
    _inherit = ["fix.guarded.mixin"]
    _order = "started_at desc"

    alert_id = fields.Many2one("fix.msp.alert", required=True, index=True, ondelete="cascade")
    company_id = fields.Many2one(related="alert_id.company_id", store=True)
    operating_unit_id = fields.Many2one(related="alert_id.operating_unit_id", store=True)
    msp_contract_id = fields.Many2one(related="alert_id.msp_contract_id", store=True)
    started_at = fields.Datetime(required=True)
    ended_at = fields.Datetime()
    reason = fields.Char(required=True)
    started_by_id = fields.Many2one("res.users", string="Paused By")
    ended_by_id = fields.Many2one("res.users", string="Resumed By")

    def _fix_guarded_fields(self) -> set:
        return {"alert_id", "started_at", "ended_at", "reason", "started_by_id", "ended_by_id"}

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError("An SLA pause is recorded by Pause (Waiting on Client) only.")
        return super().create(vals_list)

    def unlink(self):
        if not self._fix_guard_open():
            raise UserError("An SLA pause is evidence and is not deleted.")
        return super().unlink()


class _ContractScoped(models.AbstractModel):
    """M05-S11: a record of a contract is in its contract's company and
    operating unit (records raised by a cron took the cron user's)."""

    _name = "fix.msp.contract.scoped.mixin"
    _description = "M05 company / OU of the contract"

    def _msp_scope_vals(self, vals_list):
        Contract = self.env["fix.msp.contract"].sudo()
        for vals in vals_list:
            msp = Contract.browse(vals.get("msp_contract_id") or 0).exists()
            if not msp:
                continue
            vals.setdefault("company_id", msp.company_id.id)
            if msp.operating_unit_id and not vals.get("operating_unit_id"):
                vals["operating_unit_id"] = msp.operating_unit_id.id

    @api.constrains("company_id", "operating_unit_id", "msp_contract_id")
    def _check_contract_scope(self):
        for rec in self:
            msp = rec.msp_contract_id.sudo()
            if not msp:
                continue
            if rec.company_id != msp.company_id:
                raise ValidationError(
                    "%s of %s must be in the contract's company (%s), not %s."
                    % (rec._description, msp.name, msp.company_id.name, rec.company_id.name)
                )
            if msp.operating_unit_id and rec.operating_unit_id != msp.operating_unit_id:
                raise ValidationError(
                    "%s of %s must be in the contract's operating unit (%s)."
                    % (rec._description, msp.name, msp.operating_unit_id.name)
                )


ALERT_FROZEN = ("msp_contract_id", "asset_id", "severity", "source")


class FixMspAlertA02r2(models.Model):
    _name = "fix.msp.alert"
    _inherit = ["fix.msp.alert", "fix.msp.contract.scoped.mixin"]

    sla_deadline = fields.Datetime(
        string="Resolution Deadline",
        readonly=True,
        copy=False,
        help="Stamped when the alert is raised, with the terms then in force (pauses extend "
        "it). Only a reclassification while the alert is new restamps it.",
    )
    response_deadline = fields.Datetime(string="Response Deadline", readonly=True, copy=False)
    acked_at = fields.Datetime(string="Acknowledged At", readonly=True, copy=False)
    responded_at = fields.Datetime(
        string="First Response At",
        readonly=True,
        copy=False,
        help="The first acknowledgement, ticket or resolution.",
    )
    pause_ids = fields.One2many("fix.msp.alert.pause", "alert_id", string="SLA Pauses")
    paused = fields.Boolean(compute="_compute_paused", string="SLA Clock Paused")
    breach_notified_at = fields.Datetime(string="Breach Escalated At", readonly=True, copy=False)
    reclassified_reason = fields.Char(readonly=True, copy=False)
    field_order_ref = fields.Char(string="Field Order (M02)", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "sla_deadline",
            "response_deadline",
            "acked_at",
            "responded_at",
            "breach_notified_at",
            "reclassified_reason",
            "field_order_ref",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        return locked | set(ALERT_FROZEN) if self else locked

    def _compute_paused(self):
        for alert in self:
            alert.paused = bool(alert.pause_ids.filtered(lambda p: not p.ended_at))

    @api.model_create_multi
    def create(self, vals_list):
        self._msp_scope_vals(vals_list)
        Contract = self.env["fix.msp.contract"].sudo()
        for vals in vals_list:
            msp = Contract.browse(vals.get("msp_contract_id") or 0).exists()
            if msp and msp.lifecycle == "offboarded":
                raise UserError(
                    "MSP contract %s is offboarded: it raises no alert or ticket (M05-S07)."
                    % msp.name
                )
        alerts = super().create(vals_list)
        alerts._msp_stamp_deadlines()
        return alerts

    def write(self, vals):
        if not self._fix_guard_open():
            for alert in self.filtered("id"):
                changed = [
                    n
                    for n in ALERT_FROZEN
                    if n in vals and alert._fix_guard_differs(n, vals[n], alert[n])
                ]
                if changed:
                    raise UserError(
                        "%s cannot change once the alert is raised: its SLA was set from them. "
                        "A new alert can be reclassified (Reclassify, with the reason)."
                        % ", ".join(alert._fields[n].string or n for n in changed)
                    )
        return super().write(vals)

    def _msp_stamp_deadlines(self):
        for alert in self:
            msp = alert.msp_contract_id.sudo()
            alert._guarded().sudo().write(
                {
                    "sla_deadline": msp._msp_deadline(alert),
                    "response_deadline": msp._msp_deadline(alert, kind="response") or False,
                }
            )

    def _msp_paused_seconds(self, until=None):
        self.ensure_one()
        until = until or fields.Datetime.now()
        total = 0.0
        for pause in self.pause_ids:
            end = min(pause.ended_at or until, until)
            if end > pause.started_at:
                total += (end - pause.started_at).total_seconds()
        return total

    def _msp_effective_deadline(self, kind="resolve", until=None):
        """The stamped deadline plus the waiting-on-client pauses before
        ``until`` (None when the contract sets no target of that kind)."""
        self.ensure_one()
        stamped = self.sla_deadline if kind == "resolve" else self.response_deadline
        if not stamped:
            stamped = self.msp_contract_id.sudo()._msp_deadline(self, kind=kind)
        if not stamped:
            return None
        return stamped + timedelta(seconds=self._msp_paused_seconds(until))

    def _msp_mark_response(self, now=None):
        for alert in self.filtered(lambda a: not a.responded_at):
            alert._guarded().write({"responded_at": now or fields.Datetime.now()})

    def action_acknowledge(self):
        res = super().action_acknowledge()
        now = fields.Datetime.now()
        self._guarded().write({"acked_at": now})
        self._msp_mark_response(now)
        return res

    def action_to_ticket(self):
        res = super().action_to_ticket()
        self._msp_mark_response()
        return res

    def action_resolve(self, note=""):
        res = super().action_resolve(note=note)
        for alert in self:
            alert._msp_mark_response(alert.resolved_at)
            # the clock stops at the fix: an open pause ends with it
            open_pause = alert.pause_ids.filtered(lambda p: not p.ended_at)
            if open_pause:
                open_pause._guarded().write(
                    {"ended_at": alert.resolved_at, "ended_by_id": self.env.uid}
                )
        return res

    # ---- M05-S02: reclassify --------------------------------------------
    def action_reclassify(self, severity=None, reason=None):
        """Change a NEW alert's severity, with the reason: the deadlines are
        restamped from the raise time. Once acknowledged it is fixed."""
        require_role(self.env, [GROUP_ENGINEER], "Reclassifying an alert")
        reason = (reason or "").strip()
        if len(reason) < REASON_MIN:
            raise UserError("Give the reason for the reclassification (at least 10 characters).")
        if severity not in dict(self._fields["severity"].selection):
            raise UserError("The severity is one of: minor, major.")
        for alert in self:
            if alert.state != "new":
                raise UserError(
                    "Alert %s is %s: only a new alert is reclassified." % (alert.id, alert.state)
                )
            if alert.severity == severity:
                raise UserError("Alert %s already is %s." % (alert.id, severity))
            old = alert.severity
            alert._guarded().write({"severity": severity, "reclassified_reason": reason})
            alert._msp_stamp_deadlines()
            alert.message_post(
                body="Reclassified %s -> %s by %s: %s" % (old, severity, self.env.user.name, reason)
            )
        return True

    # ---- M05-S18: waiting on the client ---------------------------------
    def action_pause(self, reason=None):
        require_role(self.env, [GROUP_ENGINEER], "Pausing an alert's SLA clock")
        reason = (reason or "").strip()
        if len(reason) < REASON_MIN:
            raise UserError(
                "Say what the client must do before work continues (at least 10 characters)."
            )
        for alert in self:
            if alert.state == "resolved":
                raise UserError("Alert %s is resolved." % alert.id)
            if alert.paused:
                raise UserError("Alert %s is already paused." % alert.id)
            self.env["fix.msp.alert.pause"].sudo()._guarded().create(
                {
                    "alert_id": alert.id,
                    "started_at": fields.Datetime.now(),
                    "reason": reason,
                    "started_by_id": self.env.uid,
                }
            )
            alert.message_post(body="SLA clock paused by %s: %s" % (self.env.user.name, reason))
        return True

    def action_resume(self):
        require_role(self.env, [GROUP_ENGINEER], "Resuming an alert's SLA clock")
        for alert in self:
            pause = alert.pause_ids.filtered(lambda p: not p.ended_at)
            if not pause:
                raise UserError("Alert %s is not paused." % alert.id)
            pause.sudo()._guarded().write(
                {"ended_at": fields.Datetime.now(), "ended_by_id": self.env.uid}
            )
            alert.message_post(body="SLA clock resumed by %s." % self.env.user.name)
        return True

    # ---- M05-S18: threshold escalations ----------------------------------
    @api.model
    def cron_threshold_escalations(self):
        """Every open alert: escalated to the next rota level when the
        response target is missed or the threshold share of the resolution
        target has elapsed; notified once when the resolution target is
        breached."""
        params = self.env["ir.config_parameter"].sudo()
        try:
            share = float(params.get_param(ESCALATION_PCT_PARAM, ESCALATION_PCT_DEFAULT))
        except (TypeError, ValueError):
            share = ESCALATION_PCT_DEFAULT
        now = fields.Datetime.now()
        done = 0
        for alert in self.sudo().search([("state", "!=", "resolved")]):
            if alert.paused:
                continue
            deadline = alert._msp_effective_deadline("resolve", now)
            respond = alert._msp_effective_deadline("response", now)
            why = ""
            if respond and not alert.responded_at and now > respond:
                why = "its response target passed with no response"
            elif deadline:
                total = (deadline - alert.create_date).total_seconds()
                if total > 0 and (now - alert.create_date).total_seconds() >= total * share / 100.0:
                    why = "%.0f %% of its resolution target has elapsed" % share
            if why and not alert.escalated:
                alert.action_escalate()
                alert.message_post(body="Escalated automatically: %s." % why)
                done += 1
            if deadline and now > deadline and not alert.breach_notified_at:
                alert._guarded().write({"breach_notified_at": now})
                alert.message_post(
                    body="Resolution target breached at %s UTC."
                    % fields.Datetime.to_string(deadline)
                )
                publish(
                    self.env,
                    "msp.alert_sla_breached",
                    "fix.msp.alert",
                    alert.id,
                    {"msp_contract_id": alert.msp_contract_id.id, "severity": alert.severity},
                )
        return done

    # ---- M05-S16: escalate to an M02 field visit ------------------------
    def action_escalate_to_field(self, note=None):
        """A ticket the remote work cannot fix becomes an M02 field order on
        its service order, carrying the context (alert, asset, contract,
        remote sessions)."""
        require_role(self.env, [GROUP_ENGINEER], "Escalating an MSP ticket to a field visit")
        FieldOrder = self.env.get("fix.field.order")
        if FieldOrder is None:
            raise UserError("Field service (M02) is not installed on this server.")
        note = (note or "").strip()
        if len(note) < REASON_MIN:
            raise UserError("Say why a visit is needed (at least 10 characters).")
        created = []
        for alert in self:
            if alert.state != "ticketed" or not alert.order_id:
                raise UserError(
                    "Alert %s is %s: only a ticketed alert (with its service order) goes to a "
                    "field visit." % (alert.id, alert.state)
                )
            if alert.field_order_ref:
                raise UserError(
                    "Alert %s already went to field visit %s." % (alert.id, alert.field_order_ref)
                )
            order = alert.order_id.sudo()
            zone = order.branch_id.zone_id
            if not zone:
                raise UserError(
                    "Branch %s has no dispatch zone: set one before a field visit."
                    % order.branch_id.name
                )
            sessions = (
                self.env["fix.remote.session"]
                .sudo()
                .search(
                    [("asset_id", "=", alert.asset_id.id), ("ended_at", "!=", False)],
                    order="ended_at desc",
                    limit=3,
                )
            )
            context_lines = [
                "MSP ticket (alert %s, %s): %s" % (alert.id, alert.severity, alert.message),
                "Contract: %s; asset: %s (%s)"
                % (
                    alert.msp_contract_id.name,
                    alert.asset_id.hostname or alert.asset_id.agent_id,
                    alert.asset_id.ip_address or "-",
                ),
                "Why a visit: %s" % note,
            ] + [
                "Remote session %s: %s" % (s.ended_at, (s.session_summary or "-")[:200])
                for s in sessions
            ]
            partner = order.customer_id
            fo = FieldOrder.sudo().create(
                {
                    "order_id": order.id,
                    "zone_id": zone.id,
                    "operating_unit_id": (
                        order.operating_unit_id or order.branch_id.operating_unit_id
                    ).id,
                    "company_id": order.company_id.id,
                    "priority": "2" if alert.severity == "major" else "1",
                    "scheduled_start": False,
                    "customer_address": " ".join(p for p in [partner.street, partner.city] if p)
                    or None,
                    "notes": "\n".join(context_lines),
                }
            )
            ref = "%s,%s" % (fo._name, fo.id)
            alert._guarded().write({"field_order_ref": fo.name or ref})
            alert.message_post(
                body="Escalated to field visit %s by %s: %s" % (fo.name, self.env.user.name, note)
            )
            publish(
                self.env,
                "msp.ticket_escalated_to_field",
                "fix.msp.alert",
                alert.id,
                {"field_order_id": fo.id, "service_order_id": order.id, "reason": note},
            )
            created.append(fo.id)
        return {"field_order_ids": created}


class FixMspServiceReportA02r2(models.Model):
    _name = "fix.msp.service.report"
    _inherit = ["fix.msp.service.report", "fix.msp.contract.scoped.mixin"]

    response_breached_count = fields.Integer(string="Response Target Missed")
    mtta_minutes = fields.Float(string="MTTA (min)", help="Mean time to the first response")
    mttr_minutes = fields.Float(string="MTTR (min)", help="Mean time to resolve, pauses excluded")
    sla_not_binding = fields.Boolean(
        string="SLA Not Yet Binding",
        help="The whole month fell before the SLA became binding (onboarding): no attainment, "
        "no credit.",
    )
    sla_binds_at = fields.Datetime(string="SLA Binds From")
    remote_minutes = fields.Float(string="Remote Session Minutes")
    remote_hours_entitled = fields.Float(string="Remote Hours Entitled")
    overage_hours = fields.Float(string="Overage Hours")
    overage_rate = fields.Float(string="Overage Rate (BDT / h)")
    overage_amount = fields.Float(string="Overage Billed (BDT, VAT excl.)")
    overage_flagged = fields.Boolean(
        string="Overage Not Billed (No Rate)",
        help="Hours above the entitlement on a contract with no overage rate (D11).",
    )
    overage_published_at = fields.Datetime(readonly=True, copy=False)
    patch_compliance_pct = fields.Float(string="Patch Compliance %")
    health_score_avg = fields.Float(string="Average Health Score")
    credit_amount = fields.Float(
        string="SLA Credit (BDT)", compute="_compute_credit_amount", help="The month's SLA credit"
    )

    _A02R2_FIGURES = (
        "response_breached_count",
        "mtta_minutes",
        "mttr_minutes",
        "sla_not_binding",
        "sla_binds_at",
        "remote_minutes",
        "remote_hours_entitled",
        "overage_hours",
        "overage_rate",
        "overage_amount",
        "overage_flagged",
        "overage_published_at",
        "patch_compliance_pct",
        "health_score_avg",
    )

    def _fix_guarded_fields(self) -> set:
        return (
            super()._fix_guarded_fields()
            | set(self._A02R2_FIGURES)
            | {
                "msp_contract_id",
                "period_label",
                "pending_count",
                "breached_count",
                "resolved_total_count",
            }
        )

    def _msp_needs_figure(self) -> bool:
        """True when the report has no attainment figure although its month
        is binding (M05-S01): it is recomputed, not left to block the credit."""
        self.ensure_one()
        if self.sla_not_binding:
            return False
        self.flush_recordset(["sla_attainment"])
        self.env.cr.execute(
            "SELECT sla_attainment IS NULL FROM fix_msp_service_report WHERE id = %s", [self.id]
        )
        row = self.env.cr.fetchone()
        return bool(row and row[0])

    def _compute_credit_amount(self):
        Credit = self.env["fix.msp.sla.credit"].sudo()
        for report in self:
            credit = Credit.search([("service_report_id", "=", report.id)], limit=1)
            report.credit_amount = credit.credit_amount if credit else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        # M05-S01: a report is the monthly computation's, never typed: an
        # empty report made by hand blocked the month's real report and with
        # it the SLA credit.
        if not self._fix_guard_open():
            raise UserError(
                "A service report is made by Generate Monthly Report (or the nightly run), "
                "which computes its figures; it is not created by hand."
            )
        self._msp_scope_vals(vals_list)
        return super().create(vals_list)

    def action_print_service_report(self):
        self.ensure_one()
        self.check_access("read")
        return {"print_url": "/report/pdf/cd_msp_contract.report_msp_service_report/%s" % self.id}

    @api.model
    def consume_service_report_published(self, event: dict) -> dict:
        """M05-S15: the month's report goes to the client's reporting
        contacts (M27 e-mail), once per report."""
        if not self.env.su:
            raise AccessError("msp.service_report_published is consumed by the event relay only.")
        report = self.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not report:
            return {"queued": 0, "reason": "report not found"}
        msp = report.msp_contract_id
        body = "%s\n\n%s\n\n%s" % (
            report.summary_en or "",
            report.summary_bn or "",
            "The full report (breaches, patch compliance, estate health, SLA credit) is "
            "attached to your monthly service review; ask your account manager for the PDF.",
        )
        queued = msp._msp_notify_contacts(
            "msp-report:%s" % report.id,
            "Managed services report %s / পরিচালিত সেবা প্রতিবেদন" % report.period_label,
            body,
        )
        return {"queued": queued}


class FixMspSlaCreditA02r2(models.Model):
    _name = "fix.msp.sla.credit"
    _inherit = ["fix.msp.sla.credit", "fix.msp.contract.scoped.mixin"]

    mtta_minutes = fields.Float(related="service_report_id.mtta_minutes", string="MTTA (min)")
    mttr_minutes = fields.Float(related="service_report_id.mttr_minutes", string="MTTR (min)")
    response_breached_count = fields.Integer(
        related="service_report_id.response_breached_count", string="Response Target Missed"
    )

    @api.model_create_multi
    def create(self, vals_list):
        # M05-S01: a credit typed by hand is a manual credit with its amount;
        # an amountless row only blocked the month's computed credit.
        if not self._fix_guard_open():
            for vals in vals_list:
                try:
                    amount = float(vals.get("manual_amount") or 0.0)
                except (TypeError, ValueError):
                    amount = 0.0
                if amount <= 0.0:
                    raise UserError(
                        "A credit entered by hand is a manual credit: give its amount (and the "
                        "DOFA justification). The computed credit of a month is drafted by "
                        "Compute SLA Credits from its service report."
                    )
        self._msp_scope_vals(vals_list)
        return super().create(vals_list)


class FixRemoteSessionA02r2(models.Model):
    _inherit = "fix.remote.session"

    duration_minutes = fields.Float(
        string="Metered Minutes",
        readonly=True,
        copy=False,
        help="Started to ended, stamped when the session ends (M05-S17).",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"duration_minutes"}

    def action_end(self, recording_url=None):
        result = super().action_end(recording_url=recording_url)
        for session in self:
            if session.started_at and session.ended_at:
                minutes = round((session.ended_at - session.started_at).total_seconds() / 60.0, 1)
                session._guarded().write({"duration_minutes": max(minutes, 0.0)})
                session.msp_contract_id._msp_meter_hours(session.ended_at)
        return result


# ------------------------------------------- M05-S15: the printable report


class MspServiceReportPdf(models.AbstractModel):
    """The bilingual client service report's payload: built from the
    report's stored figures and the month's records, never in the template."""

    _name = "report.cd_msp_contract.report_msp_service_report"
    _description = "MSP Client Service Report (PDF)"

    def _when(self, stamp):
        if not stamp:
            return "-"
        return pytz.utc.localize(stamp).astimezone(BD_TZ).strftime("%d-%b-%Y %H:%M")

    def _payload(self, report):
        msp = report.msp_contract_id
        start, end, _label = dhaka_month(
            datetime.strptime(report.period_label + "-01", "%Y-%m-%d").date()
        )
        alerts = (
            self.env["fix.msp.alert"]
            .sudo()
            .search(
                [
                    ("msp_contract_id", "=", msp.id),
                    ("create_date", ">=", start),
                    ("create_date", "<=", end),
                ],
                order="create_date",
            )
        )
        breaches = []
        for alert in alerts:
            until = alert.resolved_at or end
            deadline = alert._msp_effective_deadline("resolve", until)
            if deadline and (not alert.resolved_at or alert.resolved_at > deadline):
                breaches.append(
                    [
                        self._when(alert.create_date),
                        alert.asset_id.hostname or alert.asset_id.agent_id or "-",
                        alert.severity,
                        (alert.message or "")[:80],
                        self._when(deadline),
                        self._when(alert.resolved_at),
                    ]
                )
        credit = (
            self.env["fix.msp.sla.credit"]
            .sudo()
            .search(
                [("msp_contract_id", "=", msp.id), ("period_label", "=", report.period_label)],
                limit=1,
            )
        )
        attainment = (
            "Not yet binding / এখনও বাধ্যতামূলক নয়"
            if report.sla_not_binding
            else "%.1f %%" % (report.sla_attainment_pct or 0.0)
        )
        return {
            "client": msp.contract_id.customer_id.name or "-",
            "contract": msp.name,
            "period": report.period_label,
            "summary_en": report.summary_en or "",
            "summary_bn": report.summary_bn or "",
            "printed_at": datetime.now(BD_TZ).strftime("%d-%b-%Y %H:%M"),
            "printed_by": self.env.user.name,
            "blocks": [
                {
                    "title": "Service Levels / সেবার মান",
                    "rows": [
                        ("SLA attainment / এসএলএ অর্জন", attainment),
                        (
                            "SLA target / লক্ষ্য",
                            "%.1f %%" % (credit.target_pct or msp.sla_target_pct),
                        ),
                        ("Alerts / সতর্কতা", report.alert_count),
                        ("Resolved within target / লক্ষ্যের মধ্যে সমাধান", report.resolved_count),
                        ("Breaches / লঙ্ঘন", report.breached_count),
                        ("Response target missed / সাড়া দিতে দেরি", report.response_breached_count),
                        ("MTTA (min)", "%.1f" % report.mtta_minutes),
                        ("MTTR (min)", "%.1f" % report.mttr_minutes),
                    ],
                },
                {
                    "title": "Estate / এস্টেট",
                    "rows": [
                        ("Patch compliance / প্যাচ সম্মতি", "%.1f %%" % report.patch_compliance_pct),
                        ("Average health score / গড় স্বাস্থ্য স্কোর", "%.1f" % report.health_score_avg),
                        (
                            "Remote support minutes / রিমোট সাপোর্ট (মিনিট)",
                            "%.0f" % report.remote_minutes,
                        ),
                        (
                            "Remote hours entitled / প্রাপ্য ঘণ্টা",
                            "%.1f" % report.remote_hours_entitled
                            if report.remote_hours_entitled
                            else "Not metered",
                        ),
                        ("Overage hours / অতিরিক্ত ঘণ্টা", "%.2f" % report.overage_hours),
                    ],
                },
                {
                    "title": "SLA Credit / এসএলএ ক্রেডিট",
                    "rows": [
                        (
                            "Credit (BDT, before VAT) / ক্রেডিট (ভ্যাট ছাড়া)",
                            "%.2f" % (credit.credit_amount if credit else 0.0),
                        ),
                        (
                            "State / অবস্থা",
                            dict(credit._fields["state"].selection).get(credit.state, "-")
                            if credit
                            else "No credit owed / কোনো ক্রেডিট নেই",
                        ),
                    ],
                },
            ],
            "tables": [
                {
                    "title": "SLA Breaches / এসএলএ লঙ্ঘন",
                    "cols": ["Raised", "Asset", "Severity", "Alert", "Deadline", "Resolved"],
                    "rows": breaches,
                }
            ],
        }

    def _get_report_values(self, docids, data=None):
        reports = self.env["fix.msp.service.report"].browse(docids).exists()
        reports.check_access("read")
        return {
            "doc_ids": reports.ids,
            "doc_model": "fix.msp.service.report",
            "docs": reports,
            "payloads": {r.id: self._payload(r.sudo()) for r in reports},
        }


# ------------------------------------------- M05-S19: the credential guard
# The models the guard did not cover (fix_msp_rules_bru.FREE_TEXT lists their
# fields). message_post is checked on each model's own class: a mixin's
# override would sit behind mail.thread and never run.
class FixMspContractNoCred(models.Model):
    _name = "fix.msp.contract"
    _inherit = ["fix.msp.contract", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspMonitoredAssetNoCred(models.Model):
    _name = "fix.monitored.asset"
    _inherit = ["fix.monitored.asset", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspPatchUpdateNoCred(models.Model):
    _name = "fix.msp.patch.update"
    _inherit = ["fix.msp.patch.update", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspSlaCreditNoCred(models.Model):
    _name = "fix.msp.sla.credit"
    _inherit = ["fix.msp.sla.credit", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspMaintenanceWindowNoCred(models.Model):
    _name = "fix.msp.maintenance.window"
    _inherit = ["fix.msp.maintenance.window", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspMajorIncidentNoCred(models.Model):
    _name = "fix.msp.major.incident"
    _inherit = ["fix.msp.major.incident", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspServiceReviewNoCred(models.Model):
    _name = "fix.msp.service.review"
    _inherit = ["fix.msp.service.review", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspDrPlanNoCred(models.Model):
    _name = "fix.msp.dr.plan"
    _inherit = ["fix.msp.dr.plan", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspRoadmapItemNoCred(models.Model):
    _name = "fix.msp.roadmap.item"
    _inherit = ["fix.msp.roadmap.item", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspOnboardingNoCred(models.Model):
    _name = "fix.msp.onboarding"
    _inherit = ["fix.msp.onboarding", "fix.msp.no.credentials.mixin"]

    def message_post(self, **kwargs):
        check_message_body(kwargs)
        return super().message_post(**kwargs)


class FixMspReviewActionNoCred(models.Model):
    _name = "fix.msp.review.action"
    _inherit = ["fix.msp.review.action", "fix.msp.no.credentials.mixin"]


class FixMspDrTestNoCred(models.Model):
    _name = "fix.msp.dr.test"
    _inherit = ["fix.msp.dr.test", "fix.msp.no.credentials.mixin"]


class FixMspOnboardingStepNoCred(models.Model):
    _name = "fix.msp.onboarding.step"
    _inherit = ["fix.msp.onboarding.step", "fix.msp.no.credentials.mixin"]


class FixMspAlertPauseNoCred(models.Model):
    _name = "fix.msp.alert.pause"
    _inherit = ["fix.msp.alert.pause", "fix.msp.no.credentials.mixin"]
