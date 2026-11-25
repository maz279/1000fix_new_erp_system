# fix_msp_lifecycle — A02 audit P1/P2 for M05 (2026-11-04): the MSP layer
# follows the M08 contract it sells on, and the jobs nobody ran are scheduled.
#
#   * entitlement: ticketing, remote sessions and SLA credits check that the
#     M08 term is in force (7 of 9 live MSP contracts sat on DRAFT contracts
#     that still carried alerts and sessions); a renewal re-points the MSP
#     layer to the new term (contract.renewed consumer);
#   * "within SLA" on the monthly report is measured from resolution times;
#   * crons (B4): the monthly report + SLA credit computation, and the
#     maintenance-window open / close events (window state is derived, so the
#     boundary is published once, idempotently, when it is crossed).
#
# FILE NAME IS LOAD-BEARING: sorts after fix_msp_ext, so the models it
# extends are all defined first.
import logging
from datetime import datetime, time, timedelta

import pytz
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

from .msp_periods import BD_TZ, dhaka_date, dhaka_month, dhaka_previous_month, dhaka_today


def _dhaka_midnight(day):
    """Midnight in Dhaka at the END of ``day``, as naive UTC."""
    local = datetime.combine(day, time.max)
    return BD_TZ.localize(local).astimezone(pytz.utc).replace(tzinfo=None)


_logger = logging.getLogger(__name__)

# Whether the M08 term must be in force for MSP work. On by default: an
# alert ticket on a draft contract is unpaid entitlement work. A business
# may turn it off while it brings its contracts into force.
ENTITLEMENT_PARAM = "cd_msp_contract.entitlement_required"
IN_FORCE = ("active", "expiring")
NEVER_IN_FORCE = ("draft", "pending_signature")


def _param_on(env, key, default="1") -> bool:
    raw = env["ir.config_parameter"].sudo().get_param(key, default)
    return str(raw or "").strip().lower() not in ("", "0", "false", "no", "off")


class FixApprovalMatrixMsp(models.Model):
    """The M05 decision domains the M63 rule book can address (A02 audit B1)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("msp_change", "MSP Change (CAB / Emergency)"),
            ("msp_sla_credit", "MSP SLA Credit"),
            ("msp_patch_exception", "MSP Patch Install Exception"),
        ],
        ondelete={
            "msp_change": "cascade",
            "msp_sla_credit": "cascade",
            "msp_patch_exception": "cascade",
        },
    )


class FixMspContractLifecycle(models.Model):
    _inherit = "fix.msp.contract"

    contract_state = fields.Selection(
        related="contract_id.state", string="M08 Contract State", readonly=True
    )
    entitled = fields.Boolean(
        compute="_compute_entitled",
        string="Entitled Today",
        help="The M08 contract is active (or expiring) and today is inside its term",
    )
    alert_resolve_hours_major = fields.Float(
        string="Major Alert Resolution Target (h)",
        default=4.0,
        help="An alert resolved within this many hours of being raised counts as within SLA",
    )
    alert_resolve_hours_minor = fields.Float(
        string="Minor Alert Resolution Target (h)", default=24.0
    )

    # ---- entitlement -------------------------------------------------------
    def _msp_entitlement_denial(self, day=None) -> str:
        """'' when the M08 term covers ``day`` (default today), else why not."""
        self.ensure_one()
        contract = self.contract_id.sudo()
        day = day or fields.Date.context_today(self)
        if contract.state not in IN_FORCE:
            return "its M08 contract %s is '%s', not in force" % (
                contract.code or contract.name,
                dict(contract._fields["state"].selection).get(contract.state, contract.state),
            )
        if not (contract.date_start <= day <= contract.date_end):
            return "today is outside the M08 term %s to %s" % (
                contract.date_start,
                contract.date_end,
            )
        return ""

    def _compute_entitled(self):
        for msp in self:
            msp.entitled = bool(msp.contract_id) and not msp._msp_entitlement_denial()

    def _msp_assert_entitled(self, what):
        if not _param_on(self.env, ENTITLEMENT_PARAM):
            return
        for msp in self:
            denial = msp._msp_entitlement_denial()
            if denial:
                raise UserError(
                    "%s is refused: MSP contract %s is not entitled - %s. Activate or renew "
                    "the contract first." % (what, msp.name, denial)
                )

    def _msp_never_in_force(self) -> bool:
        """True when the switch is on and the M08 term never came into force:
        no SLA credit is owed on it."""
        self.ensure_one()
        return _param_on(self.env, ENTITLEMENT_PARAM) and (
            self.contract_id.sudo().state in NEVER_IN_FORCE
        )

    # ---- SLA measure (A02 audit M05-P2) ------------------------------------
    def _msp_target_hours(self, alert) -> float:
        self.ensure_one()
        # A02 ERP pass 2 (M05-S13): the target in force when it was raised
        terms = self._msp_terms_at(alert.create_date)
        if alert.severity == "major":
            return terms.alert_resolve_hours_major or 4.0
        return terms.alert_resolve_hours_minor or 24.0

    def _msp_period_sla(self, alerts, as_of=None) -> dict:
        """Within / breached / pending counts and the attainment for ``alerts``.

        Within: resolved inside its severity's resolution target. Breached:
        resolved late, resolved with no resolution time (no evidence), or
        still open past its target. Pending: open and still inside its target,
        so not yet judged. Attainment = within / (within + breached); 1.0 when
        nothing could be judged."""
        self.ensure_one()
        as_of = as_of or fields.Datetime.now()
        within = breached = pending = 0
        for alert in alerts:
            deadline = alert.create_date + timedelta(hours=self._msp_target_hours(alert))
            if alert.state == "resolved":
                if alert.resolved_at and alert.resolved_at <= deadline:
                    within += 1
                else:
                    breached += 1
            elif as_of > deadline:
                breached += 1
            else:
                pending += 1
        measured = within + breached
        return {
            "within": within,
            "breached": breached,
            "pending": pending,
            "attainment": round(within / measured, 4) if measured else 1.0,
        }

    # ---- contract.renewed (R8 consumer) ------------------------------------
    @api.model
    def consume_contract_renewed(self, event: dict) -> dict:
        """A renewal creates a NEW M08 term; the MSP layer kept pointing at the
        expired one (A02 audit probe L1). Re-point every MSP contract of the
        old term. Idempotent: a second delivery finds none left on it."""
        if not self.env.su:
            raise AccessError("contract.renewed is consumed by the event relay only.")
        payload = event.get("payload") or {}
        Contract = self.env["fix.contract"].sudo()
        renewal = Contract.browse(int(event.get("aggregate_id") or 0)).exists()
        old_code = payload.get("old_code")
        old = Contract.search([("code", "=", old_code)], limit=1) if old_code else Contract
        if not renewal or not old or old == renewal:
            return {"repointed": 0, "reason": "renewal or previous term not found"}
        msps = self.sudo().search([("contract_id", "=", old.id)])
        for msp in msps:
            msp.write({"contract_id": renewal.id})
            msp.message_post(
                body="Re-pointed from contract %s to its renewal %s (contract.renewed)."
                % (old.code, renewal.code)
            )
        return {"repointed": len(msps)}

    # ---- B4: the monthly report and the credit run -------------------------
    @api.model
    def _msp_previous_month(self, today=None):
        """Last Dhaka calendar month as UTC bounds (A02 ERP audit M05-F15)."""
        return dhaka_previous_month(today)

    def _msp_period_pending(self, period) -> int:
        """Alerts of ``period`` still open inside their resolution target."""
        self.ensure_one()
        alerts = (
            self.env["fix.msp.alert"]
            .sudo()
            .search(
                [
                    ("msp_contract_id", "=", self.id),
                    ("create_date", ">=", period[0]),
                    ("create_date", "<=", period[1]),
                ]
            )
        )
        return self._msp_period_sla(alerts)["pending"]

    def _msp_report_months(self, today=None):
        """Every finished Dhaka month this contract owes a report for, oldest
        first (A02 ERP pass 2, M05-S14): from the month its service started
        (go-live, else the M08 term start) to last month, within the term and
        never after the offboarding (M05-S07). At most 24 months back."""
        self.ensure_one()
        today = today or dhaka_today()
        last = dhaka_previous_month(today)
        term = self.contract_id.sudo()
        start = term.date_start
        if self.service_live_at:
            # A02 pass-2 review: the months from the day the SLA bound (target
            # go-live, capped at 30 days from the start: D9) to a LATE go-live
            # are binding and owed a report, so they start the walk, not the
            # go-live; and the day is the Dhaka business day (the UTC date of
            # a go-live before 06:00 Dhaka was the day before)
            live = dhaka_date(self._msp_sla_binds_at() or self.service_live_at)
            start = max(start, live) if start else live
        if not start:
            return []
        start = max(start.replace(day=1), (today.replace(day=1) - relativedelta(months=24)))
        months = []
        day = start
        while True:
            bounds = dhaka_month(day)
            if bounds[2] > last[2]:
                break
            ended = term.date_end and bounds[0] > _dhaka_midnight(term.date_end)
            gone = self.offboarded_at and self.offboarded_at < bounds[0]
            if not ended and not gone:
                months.append(bounds)
            day = day.replace(day=1) + relativedelta(months=1)
        return months

    @api.model
    def cron_monthly_service_reports(self):
        """Generate every unreported finished month's report of every MSP
        contract, then compute its SLA credits. Idempotent: run daily, it acts
        once per contract and month. One savepoint per contract, so one bad row
        does not stop the others.

        A02 ERP pass 2 (M05-S14): it looked at last month only, so a month
        whose alerts were still open on the 1st, or a day the cron did not run,
        was never reported (and its credit never computed). It now walks every
        month since go-live; a month still unreportable on the 10th opens an
        activity for the contract's owner."""
        Report = self.env["fix.msp.service.report"].sudo()
        today = dhaka_today()
        last = self._msp_previous_month()
        done = 0
        for msp in self.sudo().search([]):
            if msp._msp_never_in_force():
                continue
            try:
                with self.env.cr.savepoint():
                    for period in msp._msp_report_months(today):
                        report = Report.search(
                            [("msp_contract_id", "=", msp.id), ("period_label", "=", period[2])],
                            limit=1,
                        )
                        # M05-S01: a report with no attainment figure is
                        # recomputed (it no longer blocks the month's credit)
                        if report and not report._msp_needs_figure():
                            continue
                        # A02 ERP audit M05-F8: wait until every alert of the
                        # month can be judged; the next run tries again
                        if msp._msp_period_pending(period):
                            if period[2] == last[2] and today.day >= 10:
                                msp._msp_report_overdue_activity(period)
                            continue
                        msp._msp_monthly_report(period)
                        done += 1
                    msp.action_compute_sla_credits()
            except Exception:
                _logger.exception("M05 monthly report failed for MSP contract %s", msp.id)
        return done

    def _msp_report_overdue_activity(self, period):
        """Once a month: the report of ``period`` is still not made on the
        10th (alerts open inside their target)."""
        self.ensure_one()
        if self.report_overdue_activity_period == period[2]:
            return
        self._guarded().write({"report_overdue_activity_period": period[2]})
        user = self.create_uid if self.create_uid and self.create_uid.active else self.env.user
        self.activity_schedule(
            "mail.mail_activity_data_todo",
            user_id=user.id,
            summary="%s service report overdue" % period[2],
            note="The %s report of %s is still not made: alerts of the month are open inside "
            "their target. Resolve them so the month is judged and its credit computed."
            % (period[2], self.name),
        )


class FixMspServiceReportLifecycle(models.Model):
    _inherit = "fix.msp.service.report"

    resolved_total_count = fields.Integer(string="Resolved (any time)")
    breached_count = fields.Integer(string="Breached SLA")
    pending_count = fields.Integer(
        string="Open Within Target", help="Open alerts still inside their target; not judged"
    )

    _FIGURES = (
        "alert_count",
        "resolved_count",
        "sla_attainment",
        "resolved_total_count",
        "breached_count",
        "pending_count",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "resolved_total_count",
            "breached_count",
            "pending_count",
        }


class FixMspMaintenanceWindowLifecycle(models.Model):
    _inherit = "fix.msp.maintenance.window"

    opened_published_at = fields.Datetime(string="Opening Published At", readonly=True, copy=False)
    closed_published_at = fields.Datetime(string="Closing Published At", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"opened_published_at", "closed_published_at"}

    def _msp_window_payload(self) -> dict:
        self.ensure_one()
        return {
            "window": self.name,
            "window_id": self.id,
            "msp_contract_id": self.msp_contract_id.id or False,
            "suppress_alerts": bool(self.suppress_alerts),
            "start_at": fields.Datetime.to_string(self.start_at),
            "end_at": fields.Datetime.to_string(self.end_at),
        }

    def _msp_publish_boundaries(self, now=None):
        """Publish msp.window_opened / msp.window_closed once each, when an
        approved window crosses its start or its end (or closes early). A
        window closed before it ever opened publishes neither."""
        now = now or fields.Datetime.now()
        for window in self.sudo():
            opened = (
                window.approved_at
                and window.start_at <= now
                and (not window.closed_at or window.closed_at > window.start_at)
            )
            if opened and not window.opened_published_at:
                publish(
                    self.env,
                    "msp.window_opened",
                    "fix.msp.maintenance.window",
                    window.id,
                    window._msp_window_payload(),
                )
                window._guarded().write({"opened_published_at": now})
            if (
                window.opened_published_at
                and not window.closed_published_at
                and (window.closed_at or window.end_at < now)
            ):
                payload = dict(
                    window._msp_window_payload(),
                    closed_early=bool(window.closed_at and window.closed_at < window.end_at),
                )
                publish(
                    self.env,
                    "msp.window_closed",
                    "fix.msp.maintenance.window",
                    window.id,
                    payload,
                )
                window._guarded().write({"closed_published_at": now})

    @api.model
    def cron_window_boundaries(self):
        """B4: windows have no stored state, so nothing announced the moment
        alert suppression began or ended. Every run publishes the boundaries
        crossed since the last one."""
        now = fields.Datetime.now()
        candidates = self.sudo().search(
            [
                ("approved_at", "!=", False),
                "|",
                ("opened_published_at", "=", False),
                ("closed_published_at", "=", False),
                ("start_at", "<=", now),
            ]
        )
        for window in candidates:
            try:
                with self.env.cr.savepoint():
                    window._msp_publish_boundaries(now)
            except Exception:
                _logger.exception("M05 window boundary failed for window %s", window.id)
        return True


class FixMspSlaCreditLifecycle(models.Model):
    _inherit = "fix.msp.sla.credit"

    def action_request_approval(self, justification=None):
        """A credit is asked for only on a contract that was ever in force."""
        for credit in self:
            if credit.msp_contract_id._msp_never_in_force():
                raise UserError(
                    "No SLA credit is owed on MSP contract %s: its M08 contract never came "
                    "into force." % credit.msp_contract_id.name
                )
        return super().action_request_approval(justification=justification)
