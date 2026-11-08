# fix_facility_ops — M47: site leases, statutory licences, utility accounts,
# occupancy/condition inspections, building PM, safety equipment, security
# incidents and site open/close projects. Sites and facility work orders live in
# fix_facility.py.
import json
import re
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Domain

from libs.py.fix_events import publish

from .fix_facility import ESTATE_COST_DOFA_THRESHOLDS, _changes, _refuse_if_covered

# AUT-FAC-14: safety equipment alerts the branch 30 days before its inspection
# or refill date; inside that window the item is "due", after it "overdue".
SAFETY_DUE_DAYS = 30
# AUT-FAC-01: licence alerts at 90, 60, 30, 15 and 7 days before expiry.
LICENCE_ALERT_DAYS = (90, 60, 30, 15, 7)
# AUT-FAC-04: lease critical-date horizons; inside 30 days of the renewal
# notice deadline the decision request repeats daily to the CFO.
LEASE_ALERT_DAYS = (90, 60, 30, 15, 7)
LEASE_DECISION_DAILY_DAYS = 30
# BRU-FAC-11 / AUT-FAC-13: a utility bill whose amount or consumption is this
# many times its own trailing average (up to the last 3 periods of the same
# site and utility) is held from payment until reviewed. The spec says "the
# configured anomaly threshold" and gives no figure: 2.0 is a DEFAULT THE
# BUSINESS MUST CONFIRM (decision B2), set without code in this parameter.
UTILITY_FACTOR_PARAM = "cd_facility.utility_anomaly_factor"
UTILITY_FACTOR_DEFAULT = "2.0"
UTILITY_HISTORY = 3
# BRU-FAC-18 / AUT-FAC-15: an injury opens an HSE case the same day; BLA 2006
# s.80 gives the Inspector notice within 2 working days. Without a working
# calendar the clock counts calendar days, which can only be earlier.
HSE_NOTICE_DAYS = 2
# Switch (default off, so live work is not stopped before the M59 bridge
# exists): an injury incident closes only once its HSE case is linked.
INJURY_CLOSE_PARAM = "cd_facility.injury_close_requires_hse_case"
# FR-FAC-025 / M47-9: the spec gives no PM or inspection interval, so a plan
# or item carries its own. These business defaults (whole months, empty =
# none) apply where a plan or item has none; the business set 3 on 4 Nov 2026.
PM_INTERVAL_PARAM = "cd_facility.default_pm_interval_months"
INSPECTION_INTERVAL_PARAM = "cd_facility.default_inspection_interval_months"
# A07 operability (2026-11-07): a NEW licence carries its scan. Licences recorded
# before this rule hold none and keep counting; turn this off only to load a batch.
LICENCE_EVIDENCE_PARAM = "cd_facility.require_licence_evidence"
FACILITY_MANAGER = "cd_facility.group_facility_manager"
BRANCH_LEAD = "cd_facility.group_branch_operations_lead"


def _default_months(env, key) -> int:
    """A whole-month business default from ir.config_parameter, or 0 for none."""
    raw = env["ir.config_parameter"].sudo().get_param(key) or ""
    try:
        months = int(str(raw).strip())
    except ValueError:
        return 0
    return months if months > 0 else 0


_PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

UTILITY_GUARDED = (
    "flagged",
    "review_state",
    "anomaly_basis",
    "anomaly_evaluated",
    "reviewed_by_id",
    "reviewed_at",
    "review_notes",
)


# The terms a lease modification changes, and the proposal that carries them.
LEASE_TERM_FIELDS = ("start_date", "end_date", "monthly_rent", "escalation_pct")
# Also fixed once recorded: a deposit, a lessor and a notice period reach IFRS 16
# and the renewal deadline, so they move through a modification too. A lease is
# never moved to another site: a new site is a new lease. A notice period left
# blank when the lease was recorded may be filled in once (it only ever brings
# the renewal deadline earlier).
LEASE_RECORDED_FIELDS = ("site_id", "lessor_id", "deposit", "currency_id")
LEASE_PROPOSAL_FIELDS = (
    "proposed_end_date",
    "proposed_monthly_rent",
    "proposed_escalation_pct",
    "proposed_deposit",
    "proposed_notice_period_days",
    "proposed_lessor_id",
    "modification_reason",
)
# A shortened term that gives up no rent (it had already ended) still needs a
# decision: the smallest amount above Tier 0.
LEASE_SHORTENING_FLOOR = 0.01


def _lease_commitment(rent, escalation_pct, start, end, today) -> float:
    """The rent still owed from today to `end`: one payment per month, each
    escalated by `escalation_pct` on every anniversary of `start`. The DOFA
    amount of a renewal or modification (an approval measure, not the IFRS 16
    liability, which M47 never computes: BRU-FAC-13)."""
    if not rent or not end or end < today:
        return 0.0
    cursor = max(today, start or today)
    total = 0.0
    while cursor <= end:
        years = relativedelta(cursor, start).years if start and cursor >= start else 0
        total += rent * (1.0 + (escalation_pct or 0.0) / 100.0) ** years
        cursor += relativedelta(months=1)
    return round(total, 2)


class FixSiteLease(models.Model):
    _name = "fix.site.lease"
    _description = "Site Lease"
    _order = "end_date desc, id desc"
    # A07 audit (2026-11-03) M47-8: a plain write extended a lease by five
    # years and cut its rent, and a terminated lease was made active again.
    # The terms (dates, rent, escalation) now change only through a
    # modification: Open Modification copies the terms into a proposal, the
    # proposal is approved under DOFA on the total remaining commitment, and
    # Apply Modification writes it. `state` moves only by its actions.
    _inherit = ["fix.dofa.mixin"]  # brings fix.approvable.mixin and the guard

    _approval_domain = "lease_modification"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    def _dofa_amount(self) -> float:
        self.ensure_one()
        if not self.modification_open:
            return 0.0
        today = fields.Date.context_today(self)
        proposed = _lease_commitment(
            self.proposed_monthly_rent,
            self.proposed_escalation_pct,
            self.start_date,
            self.proposed_end_date,
            today,
        )
        if not (
            self.proposed_end_date and self.end_date and self.proposed_end_date < self.end_date
        ):
            return proposed
        # A shorter term is measured on the rent it gives up as well: an end
        # date in the past owes nothing from today, and needed no approval.
        current = _lease_commitment(
            self.monthly_rent, self.escalation_pct, self.start_date, self.end_date, today
        )
        return max(proposed, current - proposed, LEASE_SHORTENING_FLOOR)

    def _dofa_thresholds(self):
        return ESTATE_COST_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (lease commitment under the proposed terms, or the rent given up)" % (
            self._dofa_amount()
        )

    @api.depends(
        "modification_open",
        "start_date",
        "proposed_end_date",
        "proposed_monthly_rent",
        "proposed_escalation_pct",
        "end_date",
        "monthly_rent",
        "escalation_pct",
    )
    def _compute_dofa_tier_required(self):
        # The live gates read _dofa_current_tier(); this stored column is the
        # tier at the last write (the commitment shrinks as the months pass).
        return super()._compute_dofa_tier_required()

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    lessor_id = fields.Many2one("res.partner", string="Lessor", required=True)
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    monthly_rent = fields.Monetary(currency_field="currency_id")
    escalation_pct = fields.Float(string="Escalation %", default=0.0)
    deposit = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [("active", "Active"), ("expired", "Expired"), ("terminated", "Terminated")],
        required=True,
        default="active",
    )
    notes = fields.Char()
    modification_open = fields.Boolean(
        string="Modification Open",
        readonly=True,
        copy=False,
        help="A renewal or modification is being proposed for approval",
    )
    proposed_end_date = fields.Date(string="Proposed End Date", copy=False)
    proposed_monthly_rent = fields.Monetary(
        string="Proposed Monthly Rent", currency_field="currency_id", copy=False
    )
    proposed_escalation_pct = fields.Float(string="Proposed Escalation %", copy=False)
    proposed_deposit = fields.Monetary(
        string="Proposed Deposit", currency_field="currency_id", copy=False
    )
    proposed_notice_period_days = fields.Integer(
        string="Proposed Renewal Notice (days)", copy=False
    )
    proposed_lessor_id = fields.Many2one("res.partner", string="Proposed Lessor", copy=False)
    modification_reason = fields.Char(string="Modification Reason", copy=False)
    terminated_reason = fields.Char(string="Termination Reason", readonly=True, copy=False)
    # A07 P2 (2026-11-04) M47-8 / BRU-FAC-05: the renewal-notice deadline and
    # the decision that must be recorded before it passes (CFO).
    notice_period_days = fields.Integer(
        string="Renewal Notice (days)",
        help="Days before the end date by which the landlord must be told (from the lease)",
    )
    renewal_notice_date = fields.Date(
        string="Renewal Notice Deadline", compute="_compute_renewal_notice_date", store=True
    )
    renewal_decision = fields.Selection(
        [("renew", "Renew"), ("renegotiate", "Renegotiate"), ("exit", "Exit (do not renew)")],
        string="Renewal Decision",
        readonly=True,
        copy=False,
    )
    renewal_decision_by_id = fields.Many2one(
        "res.users", string="Decided By", readonly=True, copy=False
    )
    renewal_decision_on = fields.Date(string="Decided On", readonly=True, copy=False)
    renewal_decision_notes = fields.Char(string="Decision Notes", readonly=True, copy=False)
    # cron bookkeeping: the last critical-date alert sent, "<kind>:<date>:<days>"
    critical_alert_key = fields.Char(readonly=True, copy=False)
    schedule_ids = fields.One2many("fix.site.lease.schedule", "lease_id", string="Rent Schedule")
    extract_ids = fields.One2many("fix.site.lease.extract", "lease_id", string="IFRS 16 Extracts")
    current_rent = fields.Monetary(
        string="Current Monthly Rent",
        currency_field="currency_id",
        compute="_compute_current_rent",
        help="Today's rent from the schedule: the commencement rent escalated on each "
        "anniversary (FR-FAC-012)",
    )

    @api.depends("end_date", "notice_period_days")
    def _compute_renewal_notice_date(self):
        for rec in self:
            rec.renewal_notice_date = (
                rec.end_date - timedelta(days=rec.notice_period_days)
                if rec.end_date and rec.notice_period_days
                else rec.end_date
            )

    def _compute_current_rent(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.current_rent = rec._lease_rent_on(today)

    def _lease_rent_on(self, day) -> float:
        """The scheduled rent for the month of `day` (the commencement rent
        escalated on every anniversary); the lease's own figure outside the
        term or before a schedule exists."""
        self.ensure_one()
        period = day.strftime("%Y-%m")
        row = self.schedule_ids.filtered(lambda r: r.period == period)[:1]
        if row:
            return row.rent_due
        if self.start_date and self.end_date and self.start_date <= day <= self.end_date:
            years = relativedelta(day, self.start_date).years
            return round(
                self.monthly_rent * (1.0 + (self.escalation_pct or 0.0) / 100.0) ** years, 2
            )
        return self.monthly_rent

    _dates_ordered = models.Constraint(
        "CHECK (end_date >= start_date)", "Lease end cannot precede its start"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "modification_open",
            "terminated_reason",
            "renewal_decision",
            "renewal_decision_by_id",
            "renewal_decision_on",
            "renewal_decision_notes",
            "critical_alert_key",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1:
            # a recorded lease's terms move only through a modification
            locked |= set(LEASE_TERM_FIELDS) | set(LEASE_RECORDED_FIELDS)
            if self.notice_period_days:
                locked.add("notice_period_days")
            if not self.modification_open:
                locked |= set(LEASE_PROPOSAL_FIELDS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.lease") or "LEASE/New"
        leases = super().create(vals_list)
        today = fields.Date.context_today(self)
        for rec in leases:
            # a lease recorded after its end date is expired, not active (M47-8)
            if rec.state == "active" and rec.end_date and rec.end_date < today:
                rec.sudo()._guarded().write({"state": "expired"})
            rec.sudo()._lease_build_schedule()
            rec._lease_publish_recorded()
        return leases

    def _lease_publish_recorded(self):
        """BRU-FAC-13/14, AUT-FAC-05: the lease data goes to M19/M49."""
        self.ensure_one()
        publish(
            self.env,
            "lease.recorded",
            "fix.site.lease",
            self.id,
            {
                "lease": self.name,
                "site": self.site_id.name,
                "site_id": self.site_id.id,
                "lessor": self.lessor_id.name,
                "start_date": str(self.start_date),
                "end_date": str(self.end_date),
                "monthly_rent": float(self.monthly_rent or 0.0),
                "escalation_pct": float(self.escalation_pct or 0.0),
                "deposit": float(self.deposit or 0.0),
                "notice_period_days": self.notice_period_days or 0,
            },
        )
        self.sudo()._lease_publish_extract("recorded")

    def action_publish_ifrs16(self):
        """Publish a lease recorded before the extract existed to M19/M49.
        A07 operability (2026-11-07): the extract was published only at create,
        so the live leases never reached IFRS 16. One extract per lease version:
        a lease that has one has nothing new to publish. Nothing does this on
        deploy: a Facility Manager publishes each lease when it is ready."""
        if not self.env.su and not self.env.user.has_group(FACILITY_MANAGER):
            raise UserError("A lease is published to IFRS 16 by a Facility Manager.")
        for rec in self:
            if rec.state == "terminated":
                raise UserError("Lease %s is terminated: there is nothing to publish." % rec.name)
            if rec.extract_ids:
                continue
            if not rec.schedule_ids:
                rec.sudo()._lease_build_schedule()
            rec._lease_publish_recorded()
        return True

    # ---- rent schedule and IFRS 16 extract (A07 P2, FR-FAC-012, BRU-FAC-13)
    def _lease_build_schedule(self):
        """One row per month of the term, the rent escalated on each
        anniversary. Rows already paid, and rows before this month, are the
        record and are kept; the rest is rebuilt from the current terms."""
        Schedule = self.env["fix.site.lease.schedule"].sudo()
        this_month = fields.Date.context_today(self).replace(day=1)
        for rec in self:
            if not rec.start_date or not rec.end_date:
                continue
            keep = rec.schedule_ids.filtered(lambda r: r.paid_amount or r.due_date < this_month)
            (rec.schedule_ids - keep)._guarded().unlink()
            kept = set(keep.mapped("period"))
            rows = []
            cursor = rec.start_date
            while cursor <= rec.end_date:
                period = cursor.strftime("%Y-%m")
                if period not in kept:
                    years = relativedelta(cursor, rec.start_date).years
                    rows.append(
                        {
                            "lease_id": rec.id,
                            "period": period,
                            "due_date": cursor,
                            "rent_due": round(
                                rec.monthly_rent
                                * (1.0 + (rec.escalation_pct or 0.0) / 100.0) ** years,
                                2,
                            ),
                            "escalation_year": years,
                        }
                    )
                cursor += relativedelta(months=1)
            if rows:
                Schedule._guarded().create(rows)

    def _lease_publish_extract(self, reason):
        """A new version of the lease data extract for M19/M49. M47 never
        computes the right-of-use asset or the liability (BRU-FAC-13)."""
        Extract = self.env["fix.site.lease.extract"].sudo()
        for rec in self:
            version = (max(rec.extract_ids.mapped("version")) if rec.extract_ids else 0) + 1
            term = (
                relativedelta(rec.end_date, rec.start_date)
                if rec.start_date and rec.end_date
                else None
            )
            data = {
                "state": rec.state,
                "terminated_reason": rec.terminated_reason or None,
                "lease": rec.name,
                "site": rec.site_id.name,
                "lessor": rec.lessor_id.name,
                "commencement": str(rec.start_date),
                "end_date": str(rec.end_date),
                "term_months": (term.years * 12 + term.months + (1 if term.days else 0))
                if term
                else 0,
                "monthly_rent": float(rec.monthly_rent or 0.0),
                "escalation_pct": float(rec.escalation_pct or 0.0),
                "deposit": float(rec.deposit or 0.0),
                "notice_period_days": rec.notice_period_days or 0,
                "renewal_decision": rec.renewal_decision or None,
                "fixed_payments_total": round(sum(rec.schedule_ids.mapped("rent_due")), 2),
            }
            Extract._guarded().create(
                {
                    "lease_id": rec.id,
                    "version": version,
                    "reason": reason,
                    "payload": json.dumps(data, sort_keys=True),
                    "published_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "lease.extract_published",
                "fix.site.lease",
                rec.id,
                {"lease": rec.name, "version": version, "reason": reason, "extract": data},
            )

    def write(self, vals):
        if self and not self._fix_guard_open():
            terms = {k: vals[k] for k in (*LEASE_TERM_FIELDS, *LEASE_RECORDED_FIELDS) if k in vals}
            if terms and _changes(self, terms):
                raise UserError(
                    "A lease's site, lessor, dates, rent, escalation and deposit change only "
                    "through a renewal or modification: Open Modification, enter the proposed "
                    "terms, request approval, then Apply Modification (BRU-FAC-05/14)."
                )
            if "notice_period_days" in vals and _changes(
                self.filtered("notice_period_days"),
                {"notice_period_days": vals["notice_period_days"]},
            ):
                raise UserError(
                    "A lease's renewal notice period, once recorded, changes through a "
                    "modification."
                )
            proposal = {k: vals[k] for k in LEASE_PROPOSAL_FIELDS if k in vals}
            if proposal and _changes(self.filtered(lambda r: not r.modification_open), proposal):
                raise UserError("Open a modification before proposing new lease terms.")
        voided = self.browse()
        proposal = {k: vals[k] for k in LEASE_PROPOSAL_FIELDS if k in vals}
        if proposal and not self._fix_guard_has_token():
            # the approval is for the terms as proposed: any change voids it
            voided = self.filtered(
                lambda r: (
                    (r.approval_state in ("pending", "approved") or r.dofa_approved)
                    and _changes(r, proposal)
                )
            )
        result = super().write(vals)
        if voided:
            voided._dofa_void_approval("the proposed lease terms changed after approval")
        return result

    def _lease_require_state(self, allowed, what):
        for rec in self:
            if rec.state not in allowed:
                raise UserError(
                    "Lease %s cannot %s: it is %s."
                    % (rec.name, what, dict(self._fields["state"].selection)[rec.state])
                )

    def action_open_modification(self):
        """Start a renewal or modification: the proposal starts from the
        current terms and is edited before approval is requested."""
        self._lease_require_state(("active", "expired"), "be renewed or modified")
        for rec in self:
            if rec.modification_open:
                raise UserError("Lease %s already has a modification open." % rec.name)
            rec._guarded().write(
                {
                    "modification_open": True,
                    "proposed_end_date": rec.end_date,
                    "proposed_monthly_rent": rec.monthly_rent,
                    "proposed_escalation_pct": rec.escalation_pct,
                    "proposed_deposit": rec.deposit,
                    "proposed_notice_period_days": rec.notice_period_days,
                    "proposed_lessor_id": rec.lessor_id.id,
                    "modification_reason": False,
                }
            )
        return True

    def _lease_clear_proposal(self):
        self._guarded().write(
            {
                "modification_open": False,
                "proposed_end_date": False,
                "proposed_monthly_rent": 0.0,
                "proposed_escalation_pct": 0.0,
                "proposed_deposit": 0.0,
                "proposed_notice_period_days": 0,
                "proposed_lessor_id": False,
                "modification_reason": False,
            }
        )

    def _lease_consume_approval(self):
        self._guarded().write(
            {
                "dofa_approved": False,
                "dofa_approved_by": False,
                "dofa_approved_at": False,
                "dofa_approved_tier": False,
                "dofa_approved_amount": 0.0,
                "approval_state": "none",
            }
        )

    def action_discard_modification(self):
        for rec in self:
            if not rec.modification_open:
                raise UserError("Lease %s has no modification open." % rec.name)
            rec._dofa_void_approval("the lease modification was discarded")
            rec._lease_clear_proposal()
        return True

    def action_dofa_approve(self):
        """The approver (a DOFA tier holder) needs no M47 write right on the
        lease: the routing check runs as the approver, then the approval is
        stamped as a service. The tier, SoD and justification checks still
        read the approver (sudo keeps the user)."""
        self._approval_assert_routed()
        return super(FixSiteLease, self.sudo()).action_dofa_approve()

    def action_request_approval(self, justification=None):
        for rec in self:
            if not rec.modification_open:
                raise UserError(
                    "Open a modification on lease %s and enter the proposed terms first." % rec.name
                )
            _refuse_if_covered(rec)
        return super().action_request_approval(justification=justification)

    def action_apply_modification(self):
        """Write the approved terms. The approval is consumed: the next
        modification needs its own."""
        self._lease_require_state(("active", "expired"), "be renewed or modified")
        today = fields.Date.context_today(self)
        for rec in self:
            if not rec.modification_open or not rec.proposed_end_date:
                raise UserError("Lease %s has no proposed terms to apply." % rec.name)
            if rec.proposed_end_date < rec.start_date:
                raise UserError("The proposed end date cannot precede the lease start.")
            rec._dofa_assert_approved("The modification of lease %s" % rec.name)
            before = {k: rec[k] for k in ("end_date", "monthly_rent", "escalation_pct")}
            new = {
                "end_date": rec.proposed_end_date,
                "monthly_rent": rec.proposed_monthly_rent,
                "escalation_pct": rec.proposed_escalation_pct,
            }
            vals = dict(new)
            # a proposal opened before these three existed leaves them as they are
            if rec.proposed_lessor_id:
                vals.update(
                    deposit=rec.proposed_deposit,
                    notice_period_days=rec.proposed_notice_period_days,
                    lessor_id=rec.proposed_lessor_id.id,
                )
            if rec.state == "expired" and rec.proposed_end_date >= today:
                vals["state"] = "active"  # a renewal of an expired lease
            reason = rec.modification_reason
            if vals["end_date"] != rec.end_date:
                # a new term needs its own renewal decision (BRU-FAC-05)
                vals.update(
                    {
                        "renewal_decision": False,
                        "renewal_decision_by_id": False,
                        "renewal_decision_on": False,
                        "renewal_decision_notes": False,
                        "critical_alert_key": False,
                    }
                )
            rec._guarded().write(vals)
            rec._lease_clear_proposal()
            rec._lease_consume_approval()
            rec.sudo()._lease_build_schedule()
            # BRU-FAC-14: a modification is a remeasurement trigger for M19/M49
            publish(
                self.env,
                "lease.modified",
                "fix.site.lease",
                rec.id,
                {
                    "lease": rec.name,
                    "site": rec.site_id.name,
                    "reason": reason or None,
                    "before": {k: str(v) if k == "end_date" else v for k, v in before.items()},
                    "after": {k: str(v) if k == "end_date" else v for k, v in new.items()},
                },
            )
            rec.sudo()._lease_publish_extract("modified")
        return True

    # ---- renewal decision (BRU-FAC-05: CFO) --------------------------------
    def _lease_record_decision(self, decision, notes):
        notes = (notes or "").strip()
        if not notes:
            raise UserError("State the basis of the renewal decision.")
        for rec in self:
            if rec.state != "active":
                raise UserError("A renewal decision is recorded for an active lease.")
            if not self.env.su:
                # no CFO group exists: DOFA Tier 4 "CFO / CCO / COO" (P0)
                if not self.env.user.has_group("cd_entity_config.group_dofa_tier_4"):
                    raise UserError(
                        "The renewal decision of lease %s is the CFO's (DOFA Tier 4)." % rec.name
                    )
                if self.env.user == rec.create_uid:
                    raise UserError(
                        "Segregation of duties: you recorded lease %s; another person decides "
                        "its renewal." % rec.name
                    )
            # a service write after the checks above: the CFO decides without
            # holding an M47 write right on the lease
            rec.sudo()._guarded().write(
                {
                    "renewal_decision": decision,
                    "renewal_decision_by_id": self.env.uid,
                    "renewal_decision_on": fields.Date.context_today(rec),
                    "renewal_decision_notes": notes,
                }
            )
        return True

    def action_decide_renew(self, notes=None):
        return self._lease_record_decision("renew", notes)

    def action_decide_renegotiate(self, notes=None):
        return self._lease_record_decision("renegotiate", notes)

    def action_decide_exit(self, notes=None):
        return self._lease_record_decision("exit", notes)

    # ---- scheduled job (AUT-FAC-04) ----------------------------------------
    @api.model
    def cron_lease_critical_dates(self):
        """Daily: build any missing rent schedule, expire leases past their
        end date, and raise the critical-date and renewal-decision alerts.
        Idempotent: each alert is sent once per date and horizon, except the
        decision request inside 30 days of the notice deadline, which repeats
        daily until the decision is recorded (AUT-FAC-04)."""
        today = fields.Date.context_today(self)
        leases = self.sudo().search([("state", "=", "active")])
        for rec in leases.filtered(lambda r: not r.schedule_ids):
            rec._lease_build_schedule()
        for rec in leases:
            if rec.end_date < today and not rec.modification_open:
                rec._guarded().write({"state": "expired"})
                rec._lease_alert("expiry", rec.end_date, (rec.end_date - today).days)
                continue
            notice = rec.renewal_notice_date
            if notice and not rec.renewal_decision:
                days = (notice - today).days
                if days <= LEASE_DECISION_DAILY_DAYS:
                    key = "decision:%s:%s" % (notice, today)
                    if rec.critical_alert_key != key:
                        publish(
                            self.env,
                            "lease.renewal_decision_required",
                            "fix.site.lease",
                            rec.id,
                            {
                                "lease": rec.name,
                                "site": rec.site_id.name,
                                "deadline": str(notice),
                                "days_left": days,
                                "responsible_role": "CFO",
                            },
                        )
                        rec._guarded().write({"critical_alert_key": key})
                    continue
            days_to_end = (rec.end_date - today).days
            for horizon in LEASE_ALERT_DAYS:
                if days_to_end <= horizon:
                    rec._lease_alert("expiry", rec.end_date, horizon)
                    break
        return True

    def _lease_alert(self, kind, due_on, horizon):
        self.ensure_one()
        key = "%s:%s:%s" % (kind, due_on, horizon)
        if self.critical_alert_key == key:
            return
        today = fields.Date.context_today(self)
        publish(
            self.env,
            "lease.critical_date_due",
            "fix.site.lease",
            self.id,
            {
                "lease": self.name,
                "site": self.site_id.name,
                "event_type": kind,
                "due_on": str(due_on),
                "days_left": (due_on - today).days,
                "responsible_role": "CFO",
            },
        )
        self._guarded().write({"critical_alert_key": key})

    def action_expire(self):
        """An active lease past its end date is recorded as expired."""
        self._lease_require_state(("active",), "expire")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.end_date >= today:
                raise UserError(
                    "Lease %s runs until %s. Terminate it to end it early."
                    % (rec.name, rec.end_date)
                )
            if rec.modification_open:
                raise UserError("Apply or discard the open modification of %s first." % rec.name)
            rec._guarded().write({"state": "expired"})
        return True

    def action_terminate(self, reason=None):
        """End a lease early: a Branch Operations Lead's act, with its reason.
        Finance hears of it: an event and a new extract version, which a
        commenced IFRS 16 contract receives as a modification item."""
        if not self.env.su and not self.env.user.has_group(BRANCH_LEAD):
            raise UserError("A lease is terminated by a Branch Operations Lead.")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("State why the lease is terminated.")
        self._lease_require_state(("active", "expired"), "be terminated")
        for rec in self:
            if rec.modification_open:
                rec.action_discard_modification()
            rec._guarded().write({"state": "terminated", "terminated_reason": reason})
            publish(
                self.env,
                "lease.terminated",
                "fix.site.lease",
                rec.id,
                {
                    "lease": rec.name,
                    "site": rec.site_id.name,
                    "site_id": rec.site_id.id,
                    "end_date": str(rec.end_date),
                    "reason": reason,
                    "terminated_by": self.env.user.name,
                },
            )
            rec.sudo()._lease_publish_extract("terminated")
        return True


class FixSiteLicence(models.Model):
    _name = "fix.site.licence"
    _description = "Site Statutory Licence"
    _inherit = ["fix.guarded.mixin"]
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    licence_type = fields.Selection(
        [
            ("trade", "Trade Licence"),
            ("fire", "Fire Safety"),
            ("health", "Health / Sanitation"),
            ("environment", "Environment"),
            ("other", "Other"),
        ],
        required=True,
        default="trade",
    )
    number = fields.Char(string="Licence Number")
    issued_on = fields.Date()
    valid_to = fields.Date()
    # A07 operability (2026-11-07): any internal user recorded a dated "valid"
    # licence with no number and no evidence, and it satisfied the readiness
    # gate and resolved an open risk exception.
    evidence_file = fields.Binary(string="Licence Scan", attachment=True, copy=False)
    evidence_filename = fields.Char(string="Scan File Name", copy=False)
    state = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired"), ("suspended", "Suspended")],
        required=True,
        default="valid",
    )
    # A07 audit (2026-11-03, M47-3/M47-4): `is_valid` was a STORED compute on
    # today's date with no cron, so a licence that lapsed yesterday still read
    # "Valid Today" and the Licence Gaps KPI under-counted. It is now computed
    # on every read and searchable. A licence with no `valid_to` is NOT valid:
    # open-ended validity is unevidenced (AC-21: loaded without evidence ->
    # expired), so it counts as a gap until an expiry date is recorded.
    is_valid = fields.Boolean(
        string="Valid Today", compute="_compute_is_valid", search="_search_is_valid"
    )

    @api.depends("state", "valid_to")
    def _compute_is_valid(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_valid = bool(rec.state == "valid" and rec.valid_to and rec.valid_to >= today)

    def _search_is_valid(self, operator, value):
        if operator not in ("in", "not in"):
            return NotImplemented
        today = fields.Date.context_today(self)
        valid = Domain(
            [("state", "=", "valid"), ("valid_to", "!=", False), ("valid_to", ">=", today)]
        )
        domain = Domain.OR([valid if flag else ~valid for flag in {bool(v) for v in value}])
        return ~domain if operator == "not in" else domain

    # cron bookkeeping: the smallest expiry horizon already alerted (AUT-FAC-01)
    alert_horizon = fields.Integer(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"alert_horizon"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.valid_to:
            locked.add("valid_to")
        return locked

    @api.model
    def _licence_evidence_required(self) -> bool:
        raw = self.env["ir.config_parameter"].sudo().get_param(LICENCE_EVIDENCE_PARAM, "True")
        return str(raw).strip().lower() not in ("0", "false", "no", "")

    def _is_lapsed(self, today) -> bool:
        return self.state == "expired" or bool(self.valid_to and self.valid_to < today)

    def _licence_check_fire_dependency(self):
        """BRU-FAC-03 / AUT-FAC-02: no trade licence renewal while the site's
        fire licence is expired. A site that holds a fire licence and none
        of them is current cannot record a current trade licence."""
        for rec in self.filtered(lambda r: r.licence_type == "trade" and r.is_valid):
            fire = self.sudo().search(
                [("site_id", "=", rec.site_id.id), ("licence_type", "=", "fire")]
            )
            if fire and not fire.filtered("is_valid"):
                raise UserError(
                    "%s cannot record a trade licence renewal while its fire licence is "
                    "expired (BRU-FAC-03). Renew the fire licence first." % rec.site_id.name
                )

    def _licence_resolve_exceptions(self):
        """A current licence resolves the site's open risk exceptions for
        its type (the renewal is the resolution)."""
        Exc = self.env["fix.site.risk.exception"].sudo()
        for rec in self.filtered("is_valid"):
            Exc.search(
                [
                    ("site_id", "=", rec.site_id.id),
                    ("licence_type", "=", rec.licence_type),
                    ("state", "in", ("open", "continue", "suspend")),
                ]
            )._exception_resolve("renewed by %s (valid to %s)" % (rec.name, rec.valid_to))

    def _licence_sync_compliance(self, mark_expired=True):
        """Lapse handling (AUT-FAC-03): mark the licence expired (the daily
        job), publish site.compliance_expired and raise the operating-risk
        exception, unless a current licence of the same type supersedes it.
        Recording an already-lapsed licence raises the exception at once."""
        today = fields.Date.context_today(self)
        Exc = self.env["fix.site.risk.exception"].sudo()
        for rec in self.sudo():
            if not rec._is_lapsed(today) or rec.state == "suspended":
                continue
            if rec.state == "valid" and mark_expired:
                rec._guarded().write({"state": "expired"})
                publish(
                    self.env,
                    "site.compliance_expired",
                    "fix.site.licence",
                    rec.id,
                    {
                        "site": rec.site_id.name,
                        "site_id": rec.site_id.id,
                        "licence": rec.name,
                        "licence_type": rec.licence_type,
                        "expiry": str(rec.valid_to) if rec.valid_to else None,
                    },
                )
            superseded = self.sudo().search_count(
                [
                    ("site_id", "=", rec.site_id.id),
                    ("licence_type", "=", rec.licence_type),
                    ("id", "!=", rec.id),
                    ("is_valid", "=", True),
                ]
            )
            # the exception is about operating on a lapse: a planned site is
            # not operating (its readiness gate needs current licences) and a
            # closed one has surrendered them
            if superseded or rec.site_id.state != "active":
                continue
            if not Exc.search_count([("licence_id", "=", rec.id)]):
                Exc._exception_raise(rec)

    @api.model
    def cron_licence_expiry(self):
        """Daily (AUT-FAC-01/03): expiry alerts at 90/60/30/15/7 days, lapse
        handling, and the daily escalation of undecided risk exceptions.
        Idempotent: each horizon is alerted once per licence."""
        today = fields.Date.context_today(self)
        licences = self.sudo().search([("state", "=", "valid")])
        for rec in licences:
            if not rec.valid_to:
                continue
            days = (rec.valid_to - today).days
            if days < 0:
                continue
            due = [h for h in LICENCE_ALERT_DAYS if days <= h]
            if due and (not rec.alert_horizon or min(due) < rec.alert_horizon):
                publish(
                    self.env,
                    "site.compliance_expiring",
                    "fix.site.licence",
                    rec.id,
                    {
                        "site": rec.site_id.name,
                        "site_id": rec.site_id.id,
                        "licence": rec.name,
                        "licence_type": rec.licence_type,
                        "expiry": str(rec.valid_to),
                        "days_remaining": days,
                    },
                )
                rec._guarded().write({"alert_horizon": min(due)})
        self.sudo().search([("state", "in", ("valid", "expired"))])._licence_sync_compliance()
        self.env["fix.site.risk.exception"].sudo()._exception_escalate()
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.licence") or "SLIC/New"
                )
            # superuser code (data loading, seeds) is trusted, as elsewhere here
            if not self._fix_guard_open():
                if not (vals.get("number") or "").strip():
                    raise UserError("Record the licence number.")
                if self._licence_evidence_required() and not vals.get("evidence_file"):
                    raise UserError("Attach the scan of the licence.")
        records = super().create(vals_list)
        if not self.env.su:
            records._licence_check_fire_dependency()
        records._licence_resolve_exceptions()
        records._licence_sync_compliance(mark_expired=False)
        return records

    def write(self, vals):
        # A07 audit (2026-11-03, M47-2/M47-3): an expired licence was revived
        # to `valid` by a plain write (or the P03 form) with no renewal and no
        # new evidence. A lapsed licence (state expired, or its end date has
        # passed) cannot be made valid again by a plain user: a renewal is a
        # NEW licence row with its own number and dates, so the lapse stays on
        # record. Marking it expired or suspended stays open. Superuser code
        # (seeds, data loading, sudo services) is trusted.
        if self and not self._fix_guard_open():
            self._licence_check_recorded_facts(vals)
        if self and not self._fix_guard_open() and ("state" in vals or "valid_to" in vals):
            today = fields.Date.context_today(self)
            new_to = (
                (fields.Date.to_date(vals["valid_to"]) or False) if "valid_to" in vals else None
            )
            for rec in self:
                state = vals.get("state", rec.state)
                valid_to = new_to if "valid_to" in vals else rec.valid_to
                changed = state != rec.state or valid_to != (rec.valid_to or False)
                if state == "valid" and changed and rec._is_lapsed(today):
                    raise UserError(
                        "Licence %s has lapsed (valid to %s, state %s) and cannot be made "
                        "valid again. Record the renewal as a new licence with its own "
                        "number and validity dates." % (rec.name, rec.valid_to or "-", rec.state)
                    )
        # the form posts the date it shows: only a real change restarts the alerts
        redated = (
            self.filtered(
                lambda r: (fields.Date.to_date(vals["valid_to"]) or False) != (r.valid_to or False)
            )
            if "valid_to" in vals
            else self.browse()
        )
        result = super().write(vals)
        if {"state", "valid_to", "licence_type"} & set(vals) and not self._fix_guard_has_token():
            if redated:
                redated._guarded().write({"alert_horizon": 0})
            if not self.env.su:
                self._licence_check_fire_dependency()
            self._licence_resolve_exceptions()
        return result

    def _licence_check_recorded_facts(self, vals):
        """What a recorded licence keeps. Its end date is the licence's: a
        renewal is a new row with its own number, dates and scan. A row from
        before the evidence rule is dated once, and only with its scan."""
        required = self._licence_evidence_required()
        for rec in self:
            if "number" in vals and rec.number and not (vals["number"] or "").strip():
                raise UserError("A licence keeps its number.")
            if (
                required
                and "evidence_file" in vals
                and rec.evidence_file
                and not vals["evidence_file"]
            ):
                raise UserError("A licence keeps its scan: attach the new scan instead.")
            if "valid_to" not in vals:
                continue
            new_to = fields.Date.to_date(vals["valid_to"]) or False
            if new_to == (rec.valid_to or False):
                continue
            if rec.valid_to:
                raise UserError(
                    "The end date of licence %s is recorded (%s) and does not change. Record "
                    "the renewal as a new licence with its own number, dates and scan."
                    % (rec.name, rec.valid_to)
                )
            if required and not (vals.get("evidence_file") or rec.evidence_file):
                raise UserError("Attach the scan of licence %s to date it." % rec.name)


class FixSiteUtility(models.Model):
    _name = "fix.site.utility"
    _description = "Site Utility Account"
    _inherit = ["fix.guarded.mixin"]
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    period = fields.Char(required=True, help="YYYY-MM")
    utility_type = fields.Selection(
        [("power", "Electricity"), ("water", "Water"), ("gas", "Gas"), ("internet", "Internet")],
        required=True,
        default="power",
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    usage = fields.Float(string="Usage")
    unit = fields.Char(string="Unit", default="kWh")
    flagged = fields.Boolean(string="Anomaly Flagged", default=False, readonly=True)
    notes = fields.Char()
    # A07 P1 (2026-11-04) M47-13 / BRU-FAC-11: the flag was a manual tick the
    # recorder could clear. A bill is now evaluated against its own history
    # on record (and by the daily job); a breach holds it from payment until
    # a Branch Operations Lead who did not record it releases or confirms it.
    review_state = fields.Selection(
        [
            ("none", "Not Held"),
            ("held", "Held for Review"),
            ("released", "Released after Review"),
            ("confirmed", "Anomaly Confirmed"),
        ],
        string="Payment Hold",
        default="none",
        required=True,
        readonly=True,
        copy=False,
    )
    anomaly_basis = fields.Char(string="Anomaly Basis", readonly=True, copy=False)
    anomaly_evaluated = fields.Boolean(readonly=True, copy=False)
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True, copy=False)
    reviewed_at = fields.Datetime(string="Reviewed At", readonly=True, copy=False)
    review_notes = fields.Char(string="Review Notes", readonly=True, copy=False)
    # A07 operability (2026-11-07): "held from payment" enforced nothing, as no
    # bill reached accounts payable. A bill not held (and one released after
    # review) now raises a pending M52 cost entry through the bridge, a held or
    # confirmed bill cannot be matched there, and the match stamps these.
    ap_requested_on = fields.Date(string="Sent to AP On", readonly=True, copy=False)
    paid_amount = fields.Monetary(
        string="Paid", currency_field="currency_id", readonly=True, copy=False
    )
    paid_on = fields.Date(string="Paid On", readonly=True, copy=False)
    invoice_ref = fields.Char(string="Invoice Ref (M52)", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(UTILITY_GUARDED)

    def _utility_send_to_ap(self):
        """Ask accounts payable for this bill. The bridge raises one pending
        cost entry per bill however often this runs, and refreshes its figure
        while AP has not decided it."""
        for rec in self:
            rec._guarded().write({"ap_requested_on": fields.Date.context_today(rec)})
            publish(
                self.env,
                "site.utility_payable",
                rec._name,
                rec.id,
                {
                    "record": rec.name,
                    "site": rec.site_id.name,
                    "site_id": rec.site_id.id,
                    "utility_type": rec.utility_type,
                    "period": rec.period,
                    "amount": float(rec.amount or 0.0),
                },
            )

    def action_send_to_ap(self):
        """A bill from before this rule, not held: send it to accounts payable."""
        if not self.env.su and not self.env.user.has_group(FACILITY_MANAGER):
            raise UserError("A bill is sent to accounts payable by a Facility Manager.")
        for rec in self:
            if rec.paid_on or rec.ap_requested_on:
                continue
            if rec.review_state not in ("none", "released"):
                raise UserError("%s is held from payment until it is reviewed." % rec.name)
            rec._utility_send_to_ap()
        return True

    def _m52_match_refusal(self):
        """Why accounts payable may not match this bill now, or nothing."""
        self.ensure_one()
        if self.review_state in ("held", "confirmed"):
            return "%s is held from payment: %s." % (
                self.name,
                dict(self._fields["review_state"].selection)[self.review_state],
            )
        return None

    def _m52_mark_paid(self, amount, paid_on, invoice_ref):
        """Accounts payable matched this bill."""
        self.sudo()._guarded().write(
            {"paid_amount": amount, "paid_on": paid_on, "invoice_ref": invoice_ref}
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.utility") or "SUTL/New"
                )
        records = super().create(vals_list)
        records._utility_evaluate()
        return records

    def write(self, vals):
        figures = {k: vals[k] for k in ("amount", "usage") if k in vals}
        if (
            self
            and figures
            and not self._fix_guard_open()
            and _changes(self.filtered(lambda r: r.review_state != "none" or r.paid_on), figures)
        ):
            raise UserError(
                "A bill under or after anomaly review keeps the figures it was reviewed "
                "on. Record a correction note and ask the reviewer."
            )
        result = super().write(vals)
        if {"amount", "usage", "period"} & set(vals) and not self._fix_guard_has_token():
            self._utility_evaluate()
        return result

    def _utility_factor(self) -> float:
        raw = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(UTILITY_FACTOR_PARAM, UTILITY_FACTOR_DEFAULT)
        )
        try:
            return float(raw)
        except (TypeError, ValueError):
            return float(UTILITY_FACTOR_DEFAULT)

    def _utility_evaluate(self):
        """AUT-FAC-13: compare the bill with its own history (up to the last
        3 earlier periods of the same site and utility). A breach holds it."""
        factor = self._utility_factor()
        for rec in self.sudo():
            if rec.review_state != "none":
                continue
            history = rec.search(
                [
                    ("id", "!=", rec.id),
                    ("site_id", "=", rec.site_id.id),
                    ("utility_type", "=", rec.utility_type),
                    ("period", "<", rec.period),
                ],
                order="period desc",
                limit=UTILITY_HISTORY,
            )
            basis = []
            if history and factor > 0:
                avg_amount = sum(history.mapped("amount")) / len(history)
                if avg_amount > 0 and rec.amount >= factor * avg_amount:
                    basis.append(
                        "amount %.2f is %.1fx the %d-period average %.2f"
                        % (rec.amount, rec.amount / avg_amount, len(history), avg_amount)
                    )
                used = history.filtered(lambda h: h.usage > 0)
                if used and rec.usage:
                    avg_usage = sum(used.mapped("usage")) / len(used)
                    if rec.usage >= factor * avg_usage:
                        basis.append(
                            "usage %.2f is %.1fx the %d-period average %.2f"
                            % (rec.usage, rec.usage / avg_usage, len(used), avg_usage)
                        )
            vals = {"anomaly_evaluated": True}
            if basis:
                vals.update(
                    {
                        "flagged": True,
                        "review_state": "held",
                        "anomaly_basis": "; ".join(basis)[:250],
                    }
                )
            rec._guarded().write(vals)
            if basis:
                rec._utility_publish_anomaly()
            else:
                rec._utility_send_to_ap()

    def _utility_publish_anomaly(self):
        for rec in self:
            publish(
                self.env,
                "site.utility_anomaly",
                "fix.site.utility",
                rec.id,
                {
                    "record": rec.name,
                    "site": rec.site_id.name,
                    "site_id": rec.site_id.id,
                    "utility_type": rec.utility_type,
                    "period": rec.period,
                    "amount": float(rec.amount or 0.0),
                    "usage": float(rec.usage or 0.0),
                    "basis": rec.anomaly_basis or None,
                },
            )

    @api.model
    def cron_utility_anomaly(self):
        """Daily: evaluate bills recorded without an evaluation (imports,
        service writes). Idempotent: each bill is evaluated once."""
        self.sudo().search([("anomaly_evaluated", "=", False)])._utility_evaluate()
        return True

    def _utility_review(self, outcome, notes):
        notes = (notes or "").strip()
        if not notes:
            raise UserError("Record the basis of the anomaly review.")
        for rec in self:
            if rec.review_state != "held":
                raise UserError("%s is not held for review." % rec.name)
            if not self.env.su:
                if not self.env.user.has_group("cd_facility.group_branch_operations_lead"):
                    raise UserError("A utility anomaly is reviewed by a Branch Operations Lead.")
                if self.env.user == rec.create_uid:
                    raise UserError(
                        "Segregation of duties: you recorded %s; another person reviews its "
                        "anomaly (§13)." % rec.name
                    )
            rec._guarded().write(
                {
                    "review_state": outcome,
                    "flagged": outcome == "confirmed",
                    "reviewed_by_id": self.env.uid,
                    "reviewed_at": fields.Datetime.now(),
                    "review_notes": notes,
                }
            )
            if outcome == "released":
                rec.sudo()._utility_send_to_ap()
        return True

    def action_release(self, notes=None):
        """Reviewed: the bill is genuine and goes to accounts payable."""
        return self._utility_review("released", notes)

    def action_confirm_anomaly(self, notes=None):
        """Reviewed: the anomaly is real; the bill stays out of payment."""
        return self._utility_review("confirmed", notes)

    # A07 audit (2026-11-03, M47-13): the same site / utility / period was
    # accepted twice and a free-text period ("last month") once, and both were
    # double-counted in Cost per Site and the per-sqft KPI. One bill per site,
    # utility type and calendar month, and the period is a real YYYY-MM.
    # A Python constraint, not SQL UNIQUE, so the upgrade does not fail on a
    # database that already holds duplicates; new or edited rows are checked.
    @api.constrains("site_id", "utility_type", "period")
    def _check_one_bill_per_period(self):
        for rec in self:
            if not _PERIOD_RE.match(rec.period or ""):
                raise ValidationError(
                    "Utility period %r must be a calendar month written YYYY-MM." % rec.period
                )
            twin = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("site_id", "=", rec.site_id.id),
                    ("utility_type", "=", rec.utility_type),
                    ("period", "=", rec.period),
                ]
            )
            if twin:
                raise ValidationError(
                    "%s already has a %s bill for %s. Correct that bill instead of "
                    "recording a second one."
                    % (
                        rec.site_id.name,
                        dict(rec._fields["utility_type"].selection).get(rec.utility_type),
                        rec.period,
                    )
                )

    def action_flag(self):
        """Hold a bill for review by hand (anyone may raise the concern;
        only a reviewer who did not record it clears it)."""
        for rec in self:
            if rec.review_state == "held":
                continue
            if rec.paid_on:
                raise UserError("%s is already paid: it cannot be held." % rec.name)
            rec._guarded().write(
                {
                    "flagged": True,
                    "review_state": "held",
                    "anomaly_basis": ("Flagged by %s" % self.env.user.name)[:250],
                    "reviewed_by_id": False,
                    "reviewed_at": False,
                    "review_notes": False,
                }
            )
            rec._utility_publish_anomaly()
        return True


class FixSiteCondition(models.Model):
    _name = "fix.site.condition"
    _description = "Site Occupancy & Condition"
    _order = "inspected_on desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    inspected_on = fields.Date(required=True, default=fields.Date.context_today)
    occupancy_pct = fields.Float(string="Occupancy %", default=100.0)
    condition_grade = fields.Selection(
        [("a", "A — Excellent"), ("b", "B — Good"), ("c", "C — Fair"), ("d", "D — Poor")],
        required=True,
        default="b",
    )
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    notes = fields.Text()

    _occupancy_range = models.Constraint(
        "CHECK (occupancy_pct >= 0 AND occupancy_pct <= 100)",
        "Occupancy is a 0–100 percentage",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.condition") or "SCND/New"
                )
        return super().create(vals_list)


class FixSitePm(models.Model):
    _name = "fix.site.pm"
    _description = "Building Services PM"
    # A07 audit (2026-11-03) M47-16: a fire-system PM was written to `done`
    # with no done date. `state` and `done_on` are set only by Mark Done.
    _inherit = ["fix.guarded.mixin"]
    _order = "scheduled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    service_type = fields.Selection(
        [
            ("hvac", "HVAC"),
            ("lift", "Lift / Elevator"),
            ("fire", "Fire Systems"),
            ("generator", "Generator"),
            ("pest", "Pest Control"),
            ("cleaning", "Deep Cleaning"),
        ],
        required=True,
        default="hvac",
    )
    provider_id = fields.Many2one("res.partner", string="Service Provider")
    scheduled_on = fields.Date(required=True, default=fields.Date.context_today)
    done_on = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cost = fields.Monetary(currency_field="currency_id")
    state = fields.Selection([("open", "Open"), ("done", "Done")], required=True, default="open")
    notes = fields.Char()
    # A07 P1 (2026-11-04) M47-15 / FR-FAC-025 / AUT-FAC-10: recurrence and
    # the work order a due PM raises. The spec gives no interval per service
    # (§10.1 "interval_value"), so none is invented: set it per plan.
    interval_months = fields.Integer(
        string="Repeat Every (months)",
        help="Empty: the business default (cd_facility.default_pm_interval_months) "
        "applies, or a one-off job when there is none. Set: marking it done "
        "schedules the next one.",
    )
    next_pm_id = fields.Many2one("fix.site.pm", string="Next PM", readonly=True, copy=False)
    work_order_id = fields.Many2one(
        "fix.facility.work.order", string="Work Order", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "done_on", "next_pm_id", "work_order_id"}

    @api.constrains("state", "done_on")
    def _check_done_has_date(self):
        for rec in self:
            if rec.state == "done" and not rec.done_on:
                raise ValidationError("A completed PM job records the date it was done.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.pm") or "SPM/New"
        return super().create(vals_list)

    def action_done(self, done_on=None):
        """Mark an open PM job done on `done_on` (default today), never later."""
        today = fields.Date.context_today(self)
        try:
            done = fields.Date.to_date(done_on) if done_on else today
        except ValueError as exc:
            raise UserError("Done date %r is not a date (YYYY-MM-DD)." % done_on) from exc
        if done > today:
            raise UserError("A PM job cannot be recorded as done in the future (%s)." % done)
        if not self.env.su and not self.env.user.has_group(FACILITY_MANAGER):
            raise UserError("A PM job is marked done by a Facility Manager.")
        for rec in self:
            if rec.state != "open":
                raise UserError("Complete an open PM job")
            # the job's work order, with its approval, permit and verification,
            # is what completes it (verifying the order marks the PM done)
            order = rec.sudo().work_order_id
            if order and order.state not in ("verified", "cancelled"):
                raise UserError(
                    "%s is being done under work order %s: verifying that order completes it."
                    % (rec.name, order.name)
                )
            rec._guarded().write({"state": "done", "done_on": done})
            months = (
                rec.interval_months
                if rec.interval_months and rec.interval_months > 0
                else _default_months(self.env, PM_INTERVAL_PARAM)
            )
            if months:
                nxt = rec.sudo().create(
                    {
                        "site_id": rec.site_id.id,
                        "service_type": rec.service_type,
                        "provider_id": rec.provider_id.id,
                        "scheduled_on": rec.scheduled_on + relativedelta(months=months),
                        "interval_months": rec.interval_months,
                        "cost": rec.cost,
                        "currency_id": rec.currency_id.id,
                    }
                )
                rec._guarded().write({"next_pm_id": nxt.id})
        return True

    @api.model
    def cron_pm_due(self):
        """Daily (AUT-FAC-10): an open PM that is due raises its scheduled
        facility work order, once. The WO goes through its own approval and
        lifecycle (a costed one is approved under DOFA before scheduling)."""
        today = fields.Date.context_today(self)
        WO = self.env["fix.facility.work.order"].sudo()
        for rec in self.sudo().search(
            [
                ("state", "=", "open"),
                ("scheduled_on", "<=", today),
                ("work_order_id", "=", False),
                ("site_id.state", "in", ("active", "suspended")),
            ]
        ):
            labels = dict(rec._fields["service_type"].selection)
            wo = WO._guarded().create(
                {
                    "site_id": rec.site_id.id,
                    "company_id": rec.site_id.company_id.id,
                    "operating_unit_id": rec.site_id.operating_unit_id.id,
                    "work_type": "maintenance",
                    "description": "Preventive maintenance %s: %s (scheduled %s)"
                    % (rec.name, labels.get(rec.service_type), rec.scheduled_on),
                    "scheduled_date": rec.scheduled_on,
                    "estimated_cost": rec.cost,
                    "assigned_type": "vendor" if rec.provider_id else "internal",
                    "vendor_id": rec.provider_id.id,
                    "pm_id": rec.id,
                }
            )
            rec._guarded().write({"work_order_id": wo.id})
        return True


class FixSiteSafety(models.Model):
    _name = "fix.site.safety"
    _description = "Site Safety Equipment"
    _inherit = ["fix.guarded.mixin"]
    _order = "next_check"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    equipment_type = fields.Selection(
        [
            ("extinguisher", "Fire Extinguisher"),
            ("alarm", "Fire Alarm"),
            ("cctv", "CCTV"),
            ("first_aid", "First Aid Kit"),
            ("other", "Other"),
        ],
        required=True,
        default="extinguisher",
    )
    ref = fields.Char(string="Tag / Reference")
    last_check = fields.Date()
    next_check = fields.Date(required=True)
    # A07 P1 (2026-11-04) M47-9: the inspection interval of THIS item (the
    # spec sets it "per equipment class" and gives no figure, so none is
    # invented), who recorded the last check, and the unfit notice to M59.
    inspection_interval_months = fields.Integer(
        string="Inspection Interval (months)",
        help="When set, Record Check rolls the next check by this interval; when "
        "empty, by the business default (cd_facility.default_inspection_interval_months).",
    )
    last_checked_by_id = fields.Many2one(
        "res.users", string="Last Checked By", readonly=True, copy=False
    )
    unfit_notified_for = fields.Date(readonly=True, copy=False)
    # A07 operability (2026-11-07): a check recorded a date and no outcome, so an
    # extinguisher that failed its check read OK. A failed item is Unfit whatever
    # its next date says, until a later check passes, and M59 raises a hazard.
    last_result = fields.Selection(
        [("pass", "Passed"), ("fail", "Failed")],
        string="Last Result",
        readonly=True,
        copy=False,
    )
    last_finding = fields.Char(string="Last Finding", readonly=True, copy=False)
    # A07 audit (2026-11-03, M47-9): `state` was typed and defaulted to `ok`,
    # so an extinguisher 45 days past its check was born `ok` and the overdue
    # KPI read 0; a plain write or the P03 form cleared an overdue item. The
    # status is now derived from `next_check` against today on every read
    # (BRU-FAC-09): overdue once the date has passed, due inside the
    # AUT-FAC-14 30-day alert window, ok otherwise. It is searchable, so the
    # grid's state filter keeps working.
    state = fields.Selection(
        [("ok", "OK"), ("due", "Due"), ("overdue", "Overdue"), ("unfit", "Unfit: Failed Check")],
        compute="_compute_state",
        search="_search_state",
    )
    notes = fields.Char()

    @api.depends("next_check", "last_result")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        due_by = today + timedelta(days=SAFETY_DUE_DAYS)
        for rec in self:
            if rec.last_result == "fail":
                rec.state = "unfit"
            elif not rec.next_check or rec.next_check < today:
                rec.state = "overdue"
            elif rec.next_check <= due_by:
                rec.state = "due"
            else:
                rec.state = "ok"

    def _search_state(self, operator, value):
        if operator not in ("in", "not in"):
            return NotImplemented
        today = fields.Date.context_today(self)
        due_by = today + timedelta(days=SAFETY_DUE_DAYS)
        failed = Domain("last_result", "=", "fail")
        by_state = {
            "unfit": failed,
            "overdue": ~failed & Domain("next_check", "<", today),
            "due": ~failed & Domain("next_check", ">=", today) & Domain("next_check", "<=", due_by),
            "ok": ~failed & Domain("next_check", ">", due_by),
        }
        domain = Domain.OR([by_state[v] for v in value if v in by_state])
        return ~domain if operator == "not in" else domain

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # the status is derived; a typed value would be discarded anyway
            vals.pop("state", None)
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.safety") or "SSAF/New"
        return super().create(vals_list)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "last_checked_by_id",
            "unfit_notified_for",
            "last_result",
            "last_finding",
        }

    def write(self, vals):
        # A07 audit (2026-11-03, M47-9): with the status derived from the
        # dates, forging moved to the dates themselves. Outside Record Check a
        # plain user may not change `last_check` (that is the inspection
        # record) or move `next_check` LATER (that clears overdue with no
        # inspection); bringing a check forward stays open. Writing the status
        # it already has (the P03 form posts every field) is accepted.
        vals = dict(vals)
        typed_state = vals.pop("state", None)
        if self and not self._fix_guard_open():
            new_next = fields.Date.to_date(vals["next_check"]) if vals.get("next_check") else None
            for rec in self:
                if typed_state is not None and typed_state != rec.state:
                    raise UserError(
                        "The status of %s is derived from its next check date (%s) and "
                        "cannot be set by hand. Use Record Check after an inspection."
                        % (rec.name, rec.next_check)
                    )
                if "last_check" in vals and (fields.Date.to_date(vals["last_check"]) or False) != (
                    rec.last_check or False
                ):
                    raise UserError(
                        "The last check of %s is recorded by Record Check, not by editing."
                        % rec.name
                    )
                if new_next and rec.next_check and new_next > rec.next_check:
                    raise UserError(
                        "The next check of %s cannot be pushed later than %s by editing. "
                        "Use Record Check after an inspection." % (rec.name, rec.next_check)
                    )
        if not vals:
            return True
        return super().write(vals)

    def action_check_pass(self, next_check=None):
        """Record a check the item passed."""
        return self.action_check(next_check=next_check, result="pass")

    def action_check_fail(self, next_check=None, finding=None):
        """Record a check the item failed: it is unfit, and M59 raises a hazard."""
        return self.action_check(next_check=next_check, result="fail", finding=finding)

    def action_check(self, next_check=None, result=None, finding=None):
        """Record an inspection today, its result, and the next one.

        A07 audit (2026-11-03, M47-9): the check stamped `ok` and left
        `next_check` in the past. The module holds no inspection interval and
        the spec gives none per equipment type, so none is invented: the
        inspector states the next check date, which must be after today.
        """
        today = fields.Date.context_today(self)
        finding = (finding or "").strip()
        if result not in ("pass", "fail"):
            raise UserError("Say whether the item passed or failed the check.")
        if result == "fail" and not finding:
            raise UserError("Say what failed on the check.")
        try:
            next_date = fields.Date.to_date(next_check) if next_check else None
        except ValueError as exc:
            raise UserError("Next check date %r is not a date (YYYY-MM-DD)." % next_check) from exc
        default_months = _default_months(self.env, INSPECTION_INTERVAL_PARAM)
        for rec in self:
            due = next_date
            months = (
                rec.inspection_interval_months
                if rec.inspection_interval_months and rec.inspection_interval_months > 0
                else default_months
            )
            if not due and months:
                due = today + relativedelta(months=months)
            if not due:
                raise UserError(
                    "Enter the next check date when recording a check of %s: it has no "
                    "inspection interval." % rec.name
                )
            if due <= today:
                raise UserError("The next check date must be after today (%s)." % today)
            rec._guarded().write(
                {
                    "last_check": today,
                    "next_check": due,
                    "last_checked_by_id": self.env.uid,
                    "last_result": result,
                    "last_finding": finding or False,
                }
            )
            if result == "fail":
                publish(
                    self.env,
                    "site.safety_check_failed",
                    "fix.site.safety",
                    rec.id,
                    {
                        "item": rec.name,
                        "site": rec.site_id.name,
                        "site_id": rec.site_id.id,
                        "equipment_type": rec.equipment_type,
                        "ref": rec.ref or None,
                        "checked_on": str(today),
                        "finding": finding,
                    },
                )
        return True

    @api.model
    def cron_safety_due(self):
        """Daily (AUT-FAC-14): equipment past its inspection date is unfit;
        the site's safety status goes to M59 once per lapse (BRU-FAC-09)."""
        today = fields.Date.context_today(self)
        for rec in self.sudo().search([("next_check", "<", today)]):
            if rec.unfit_notified_for == rec.next_check:
                continue
            publish(
                self.env,
                "site.safety_equipment_unfit",
                "fix.site.safety",
                rec.id,
                {
                    "item": rec.name,
                    "site": rec.site_id.name,
                    "site_id": rec.site_id.id,
                    "equipment_type": rec.equipment_type,
                    "ref": rec.ref or None,
                    "due_date": str(rec.next_check),
                },
            )
            rec._guarded().write({"unfit_notified_for": rec.next_check})
        return True


class FixSiteIncident(models.Model):
    _name = "fix.site.incident"
    _description = "Site Security Incident"
    # A07 audit (2026-11-03) M47-10: the reporter closed their own HIGH injury
    # incident with no resolution, and `state` was writable directly and via
    # the P03 form. Close now needs a resolution and a closer other than the
    # reporter; `state` and the closing record are set only by Close. The
    # M59 HSE hand-off is P1 and not built here.
    _inherit = ["fix.guarded.mixin"]
    _order = "occurred_on desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    incident_type = fields.Selection(
        [
            ("theft", "Theft / Burglary"),
            ("trespass", "Trespass"),
            ("injury", "Injury"),
            ("fire", "Fire"),
            ("other", "Other"),
        ],
        required=True,
        default="theft",
    )
    occurred_on = fields.Date(required=True, default=fields.Date.context_today)
    description = fields.Text(required=True)
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], required=True, default="open"
    )
    resolution = fields.Text(
        copy=False, help="Root cause and action taken. Required to close; frozen once closed."
    )
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    closed_at = fields.Datetime(string="Closed At", readonly=True, copy=False)
    # A07 P1/P2 (2026-11-04) M47-10 / BRU-FAC-18: an injury opens an M59 HSE
    # case the same day. M47 publishes `site.incident` with the s.80 clock;
    # the bridge creates the case and writes its reference back.
    injuries_flag = fields.Boolean(
        string="Injury Involved",
        help="Set for an Injury incident; tick for any other with injuries",
    )
    hse_notice_due_on = fields.Date(
        string="Inspector Notice Due (s.80)",
        readonly=True,
        copy=False,
        help="BLA 2006 s.80: notice to the Inspector within 2 working days of the "
        "accident. Counted in calendar days here, which is never later.",
    )
    hse_case_ref = fields.Char(string="HSE Case (M59)", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "closed_by_id",
            "closed_at",
            "hse_notice_due_on",
            "hse_case_ref",
        }

    def _incident_set_injury_clock(self, recount=False):
        """The s.80 date of an injury. `recount`: the accident date moved."""
        for rec in self.filtered(
            lambda r: r.injuries_flag and (recount or not r.hse_notice_due_on)
        ):
            rec._guarded().write(
                {"hse_notice_due_on": rec.occurred_on + timedelta(days=HSE_NOTICE_DAYS)}
            )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state == "closed":
            locked.add("resolution")
        return locked

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and "resolution" in vals
            and _changes(
                self.filtered(lambda r: r.state == "closed"), {"resolution": vals["resolution"]}
            )
        ):
            raise UserError("A closed incident's resolution is the record it was closed on.")
        if (
            self
            and not self._fix_guard_open()
            and "injuries_flag" in vals
            and not vals["injuries_flag"]
            and self.filtered("injuries_flag")
            and not self.env.user.has_group("cd_facility.group_branch_operations_lead")
        ):
            # un-ticking it would take an injury out of the HSE route
            raise UserError("Only a Branch Operations Lead may clear an incident's injury flag.")
        vals = dict(vals)
        if vals.get("incident_type") == "injury":
            vals["injuries_flag"] = True
        # what M59 and M60 were told no longer holds: they are told again
        retold = self.filtered(
            lambda r: (
                ("incident_type" in vals and vals["incident_type"] != r.incident_type)
                or (vals.get("injuries_flag") and not r.injuries_flag)
            )
        )
        result = super().write(vals)
        if vals.get("injuries_flag"):
            self._incident_set_injury_clock()
        if "occurred_on" in vals:
            self._incident_set_injury_clock(recount=True)
        retold._incident_publish()
        return result

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.incident") or "SINC/New"
                )
            if vals.get("incident_type") == "injury":
                vals["injuries_flag"] = True
        records = super().create(vals_list)
        records._incident_set_injury_clock()
        records._incident_publish()
        return records

    def _incident_publish(self):
        for rec in self:
            # AUT-FAC-15: M59 (HSE case on injury) and M60 (risk register)
            publish(
                self.env,
                "site.incident",
                "fix.site.incident",
                rec.id,
                {
                    "incident": rec.name,
                    "site": rec.site_id.name,
                    "site_id": rec.site_id.id,
                    "incident_type": rec.incident_type,
                    "severity": rec.severity,
                    "injuries_flag": bool(rec.injuries_flag),
                    "occurred_on": str(rec.occurred_on),
                    "hse_notice_due_on": str(rec.hse_notice_due_on)
                    if rec.hse_notice_due_on
                    else None,
                    "description": rec.description,
                },
            )

    def _incident_check_closer(self):
        """Who closes (A07 P1): an injury incident is closed by HSE (cd_hse's
        HSE Officer, where installed) or a Branch Operations Lead (spec:
        HR Director for injury); any other by a Facility Manager."""
        self.ensure_one()
        user = self.env.user
        if self.injuries_flag:
            hse = self.env.ref("cd_hse.group_hse_officer", raise_if_not_found=False)
            if not (
                user.has_group("cd_facility.group_branch_operations_lead")
                or (hse and user.has_group("cd_hse.group_hse_officer"))
            ):
                raise UserError(
                    "An injury incident (%s) is closed by HSE or a Branch Operations Lead."
                    % self.name
                )
            requires_case = (
                self.env["ir.config_parameter"].sudo().get_param(INJURY_CLOSE_PARAM, "False")
            )
            if str(requires_case).lower() in ("1", "true", "yes") and not self.hse_case_ref:
                raise UserError(
                    "%s involves an injury: it closes once its M59 HSE case is linked." % self.name
                )
        elif not user.has_group("cd_facility.group_facility_manager"):
            raise UserError("A site incident is closed by a Facility Manager.")

    def action_close(self, resolution=None):
        for rec in self:
            if rec.state != "open":
                raise UserError("Close an open incident")
            text = (resolution or rec.resolution or "").strip()
            if not text:
                raise UserError(
                    "Record the resolution of %s (root cause and action taken) to close it."
                    % rec.name
                )
            # the reporter does not close their own incident (§13 SoD);
            # superuser code (data fixes, service calls) stays trusted
            if not self.env.su:
                if rec.create_uid == self.env.user:
                    raise UserError(
                        "Segregation of duties: you reported %s; another person closes it."
                        % rec.name
                    )
                rec._incident_check_closer()
            rec._guarded().write(
                {
                    "state": "closed",
                    "resolution": text,
                    "closed_by_id": self.env.uid,
                    "closed_at": fields.Datetime.now(),
                }
            )
        return True


class FixSiteProject(models.Model):
    _name = "fix.site.project"
    _description = "Site Open / Close Project"
    # A07 audit (2026-11-03) M47-12: the creator started a 50M project alone,
    # another user raised the budget 1M -> 9M mid-project and `state` was
    # written straight to `done`. Start (and completion) now need a DOFA
    # approval of the budget; raising the budget after approval voids it, so
    # the project cannot complete until it is approved again.
    _inherit = ["fix.dofa.mixin"]  # brings fix.approvable.mixin and the guard
    _order = "planned_on desc, id desc"

    _approval_domain = "site_capex"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.budget or 0.0

    def _dofa_thresholds(self):
        return ESTATE_COST_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (capex project budget)" % self._dofa_amount()

    @api.depends("budget")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    project_type = fields.Selection(
        [("open", "Site Opening"), ("close", "Site Closure"), ("relocate", "Relocation")],
        required=True,
        default="open",
    )
    planned_on = fields.Date(required=True, default=fields.Date.context_today)
    done_on = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    budget = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [("planned", "Planned"), ("in_progress", "In Progress"), ("done", "Done")],
        required=True,
        default="planned",
    )
    notes = fields.Char()
    # A07 P1 (2026-11-04) M47-81: once signed off or started, the budget is
    # revised only by Revise Budget, with a reason, by a Facility Manager.
    budget_proposed = fields.Monetary(
        string="Proposed Budget", currency_field="currency_id", copy=False
    )
    budget_change_reason = fields.Char(string="Budget Change Reason", copy=False)
    budget_revised_by = fields.Many2one("res.users", readonly=True, copy=False)
    budget_revised_on = fields.Date(readonly=True, copy=False)
    budget_revision_note = fields.Char(readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.project") or "SPRJ/New"
                )
        return super().create(vals_list)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "done_on",
            "budget_revised_by",
            "budget_revised_on",
            "budget_revision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and (self.state != "planned" or self.dofa_approved):
            locked.add("budget")
        return locked

    def write(self, vals):
        # A07 P1 M47-81: the audit raised an in-progress project's budget 1M -> 9M
        # by a plain write. Approval voiding alone let the spend run on unapproved
        # until completion; the approved budget now stays as signed off.
        if (
            self
            and "budget" in vals
            and not self._fix_guard_open()
            and _changes(
                self.filtered(lambda r: r.state != "planned" or r.dofa_approved),
                {"budget": vals["budget"]},
            )
        ):
            raise UserError(
                "The budget of an approved or started project is changed with Revise "
                "Budget (the proposed budget and a reason); raising it needs re-approval."
            )
        return super().write(vals)

    def action_revise_budget(self, new_budget=None, reason=None):
        """Apply the staged Proposed Budget with its reason. A raise withdraws the
        DOFA approval (fix.dofa.mixin), so the project completes only once the
        new budget is approved; a cut leaves the approval standing."""
        for rec in self:
            if rec.state == "done":
                raise UserError("A completed project's budget is final.")
            if not self.env.su and not self.env.user.has_group(
                "cd_facility.group_facility_manager"
            ):
                raise UserError("Revising a project budget needs the Facility Manager role.")
            new = rec.budget_proposed if new_budget is None else new_budget
            why = (reason or rec.budget_change_reason or "").strip()
            if not new or new <= 0:
                raise UserError("Enter the proposed budget for %s." % rec.name)
            if not why:
                raise UserError("Give the reason for revising the budget of %s." % rec.name)
            rec._guarded().write(
                {
                    "budget": new,
                    "budget_proposed": False,
                    "budget_change_reason": False,
                    "budget_revised_by": self.env.user.id,
                    "budget_revised_on": fields.Date.context_today(self),
                    "budget_revision_note": "%.2f -> %.2f: %s" % (rec.budget, new, why),
                }
            )
        return True

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state not in ("planned", "in_progress"):
                raise UserError("A completed project's budget is not approved again.")
            _refuse_if_covered(rec)
        return super().action_request_approval(justification=justification)

    def action_start(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Start a planned project")
            rec._dofa_assert_approved("Starting capex project %s" % rec.name)
            rec._guarded().write({"state": "in_progress"})
        return True

    def action_done(self):
        for rec in self:
            if rec.state != "in_progress":
                raise UserError("Complete an in-progress project")
            # a budget raised after start voided the approval: re-approve first
            rec._dofa_assert_approved("Completing capex project %s" % rec.name)
            # M47-12/84: a closure project is done when the site has closed
            # (CFO + CEO sign-off and the recovery checklist), never before.
            if rec.project_type == "close" and rec.site_id.state != "closed":
                raise UserError(
                    "Closure project %s completes once %s has closed: request the site "
                    "closure (CFO and CEO sign-off) and close the site first."
                    % (rec.name, rec.site_id.name)
                )
            rec._guarded().write({"state": "done", "done_on": fields.Date.context_today(self)})
        return True


class FixSiteAsset(models.Model):
    """Building plant at a site: the register behind M47 Branch Asset Register."""

    _name = "fix.site.asset"
    _description = "Site Infrastructure Asset"
    # A07 audit (2026-11-03) M47-11: a plain user retired a 4M generator with
    # no approval, and a retired asset was restored by writing `state`.
    # Retirement is now a DOFA decision on the asset's value; `state` moves
    # only by its actions and retirement is final.
    _inherit = ["fix.dofa.mixin"]  # brings fix.approvable.mixin and the guard
    _order = "site_id, asset_type, name"

    _approval_domain = "site_asset_retirement"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.value or 0.0

    def _dofa_thresholds(self):
        return ESTATE_COST_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (site asset value retired)" % self._dofa_amount()

    @api.depends("value")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    asset_type = fields.Selection(
        [
            ("hvac", "HVAC Plant"),
            ("lift", "Lift / Elevator"),
            ("generator", "Generator"),
            ("fire_pump", "Fire Pump"),
            ("ups", "UPS"),
            ("cctv", "CCTV System"),
            ("electrical", "Electrical Distribution"),
            ("other", "Other"),
        ],
        required=True,
        default="hvac",
    )
    tag = fields.Char(string="Asset Tag")
    serial_no = fields.Char(string="Serial No")
    installed_on = fields.Date()
    warranty_end = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    value = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [
            ("operational", "Operational"),
            ("maintenance", "Under Maintenance"),
            ("retired", "Retired"),
        ],
        required=True,
        default="operational",
    )
    notes = fields.Char()
    retired_on = fields.Date(readonly=True, copy=False)
    retire_reason = fields.Char(string="Retirement Reason", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "retired_on", "retire_reason"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state == "retired":
            locked.add("value")
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.asset") or "SASET/New"
        return super().create(vals_list)

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and "value" in vals
            and _changes(self.filtered(lambda r: r.state == "retired"), {"value": vals["value"]})
        ):
            raise UserError("A retired asset's value is the value that was written off.")
        return super().write(vals)

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state == "retired":
                raise UserError("%s is already retired." % rec.name)
            _refuse_if_covered(rec)
        return super().action_request_approval(justification=justification)

    def action_maintenance(self):
        for rec in self:
            if rec.state != "operational":
                raise UserError("Take an operational asset into maintenance")
            rec._guarded().write({"state": "maintenance"})
        return True

    def action_restore(self):
        for rec in self:
            if rec.state != "maintenance":
                raise UserError("Restore an asset that is under maintenance")
            rec._guarded().write({"state": "operational"})
        return True

    def action_retire(self, reason=None):
        """Retire (final). Above Tier 0 the asset's value needs DOFA approval."""
        for rec in self:
            if rec.state not in ("operational", "maintenance"):
                raise UserError("Retire an operational asset or one under maintenance")
            rec._dofa_assert_approved("Retiring site asset %s" % rec.name)
            rec._guarded().write(
                {
                    "state": "retired",
                    "retired_on": fields.Date.context_today(self),
                    "retire_reason": (reason or "").strip() or False,
                }
            )
        return True
