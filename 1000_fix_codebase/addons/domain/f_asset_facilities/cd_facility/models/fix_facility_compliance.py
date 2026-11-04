# fix_facility_compliance — M47 records the A07 P1/P2 pass adds (2026-11-04):
# the operating-risk exception a licence lapse raises (BRU-FAC-02, AUT-FAC-03),
# the lease rent schedule (FR-FAC-012, BRU-FAC-12) and the versioned lease
# data extract for M19/M49 (BRU-FAC-13/14). The schedule and the extract are
# insert-only: only the lease's own service (superuser or a transition token)
# writes them, so the record Finance reads is the record M47 published.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

# Who takes the continue-or-suspend decision (spec §8.1 "Operations Director
# / CEO", §13 R01 CEO). No CEO group exists: DOFA Tier 5 "Managing Director /
# Board" stands for the CEO, as in the P0 site-closure sign-off.
EXCEPTION_DECIDERS = ("cd_facility.group_operations_director", "cd_entity_config.group_dofa_tier_5")


class FixSiteRiskException(models.Model):
    """An operating-risk exception: a site operating on a lapsed licence."""

    _name = "fix.site.risk.exception"
    _description = "Site Operating-Risk Exception"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "raised_at desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True)
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True, readonly=True
    )
    company_id = fields.Many2one(related="site_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="site_id.operating_unit_id", store=True, index=True, string="Operating Unit"
    )
    licence_id = fields.Many2one(
        "fix.site.licence", string="Lapsed Licence", ondelete="set null", readonly=True
    )
    licence_type = fields.Selection(
        related="licence_id.licence_type", store=True, string="Licence Type"
    )
    raised_at = fields.Datetime(readonly=True, default=fields.Datetime.now)
    severity = fields.Selection(
        [("high", "High"), ("critical", "Critical")], default="high", required=True, readonly=True
    )
    state = fields.Selection(
        [
            ("open", "Open: Decision Required"),
            ("continue", "Continue (dated decision)"),
            ("suspend", "Site Suspended"),
            ("resolved", "Resolved"),
        ],
        default="open",
        required=True,
        tracking=True,
    )
    decision_notes = fields.Text(
        string="Decision Basis", help="Interim arrangements and why operation continues or stops"
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_at = fields.Datetime(string="Decided At", readonly=True, copy=False)
    review_due_on = fields.Date(
        string="Decision Review Date",
        readonly=True,
        copy=False,
        help="A continue decision holds until this date; then it must be taken again",
    )
    resolved_at = fields.Datetime(readonly=True, copy=False)
    resolution = fields.Char(readonly=True, copy=False)
    last_escalated_on = fields.Date(readonly=True, copy=False)

    _GUARDED = (
        "state",
        "decided_by_id",
        "decided_at",
        "review_due_on",
        "resolved_at",
        "resolution",
        "last_escalated_on",
        "site_id",
        "licence_id",
        "severity",
        "raised_at",
        "name",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._GUARDED)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "open":
            locked.add("decision_notes")
        return locked

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and "decision_notes" in vals
            and self.filtered(lambda r: r.state != "open")
        ):
            raise UserError("A recorded decision keeps the basis it was taken on.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("An operating-risk exception is part of the compliance record.")
        return super().unlink()

    # ---- raising (the licence service calls this) -------------------------
    @api.model
    def _exception_raise(self, licence):
        exc = (
            self.sudo()
            ._guarded()
            .create(
                {
                    "name": self.env["ir.sequence"].sudo().next_by_code("fix.site.risk.exception")
                    or "SRISK/New",
                    "site_id": licence.site_id.id,
                    "licence_id": licence.id,
                    "severity": "critical" if licence.licence_type in ("trade", "fire") else "high",
                }
            )
        )
        exc.message_post(
            body="Operating-risk exception: %s lapsed (valid to %s). A named, dated "
            "continue-or-suspend decision is required (BRU-FAC-02)."
            % (licence.name, licence.valid_to or "-")
        )
        licence.site_id.message_post(
            body="Operating-risk exception %s raised: %s lapsed." % (exc.name, licence.name)
        )
        publish(
            self.env,
            "site.risk_exception_raised",
            "fix.site.risk.exception",
            exc.id,
            {
                "exception": exc.name,
                "site": exc.site_id.name,
                "site_id": exc.site_id.id,
                "licence": licence.name,
                "licence_type": licence.licence_type,
                "expiry": str(licence.valid_to) if licence.valid_to else None,
                "severity": exc.severity,
                "decision_required": True,
            },
        )
        return exc

    def _exception_resolve(self, how):
        for rec in self.sudo():
            rec._guarded().write(
                {"state": "resolved", "resolved_at": fields.Datetime.now(), "resolution": how[:250]}
            )
            rec.message_post(body="Resolved: %s." % how)

    # ---- decisions --------------------------------------------------------
    def _exception_check_decider(self):
        if self.env.su:
            return
        user = self.env.user
        if not any(user.has_group(g) for g in EXCEPTION_DECIDERS):
            raise UserError(
                "The continue-or-suspend decision is taken by the Operations Director or the "
                "CEO (DOFA Tier 5)."
            )
        for rec in self:
            # §13 SoD: the person responsible for the renewal is not the sole
            # approver of the exception its lapse raised
            responsible = (
                rec.licence_id.sudo().create_uid | rec.site_id.sudo().accountable_manager_id
            )
            if user in responsible:
                raise UserError(
                    "Segregation of duties: you are responsible for %s's licence renewal; "
                    "another person decides its operating-risk exception." % rec.site_id.name
                )

    def _exception_decide(self, decision, review_due_on=None, notes=None):
        notes = (notes or "").strip()
        for rec in self:
            if rec.state != "open":
                raise UserError("%s has no decision pending." % rec.name)
            if not (notes or (rec.decision_notes or "").strip()):
                raise UserError("Record the basis of the decision on %s first." % rec.name)
        self._exception_check_decider()
        for rec in self:
            # a service write after the checks above: the CEO (DOFA Tier 5)
            # decides without holding an M47 role, so no write ACL is assumed
            rec.sudo()._guarded().write(
                {
                    **({"decision_notes": notes} if notes else {}),
                    "state": decision,
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "review_due_on": review_due_on or False,
                }
            )
            if decision == "suspend":
                rec.site_id.sudo()._site_suspend(
                    "operating-risk exception %s (%s lapsed)" % (rec.name, rec.licence_id.name),
                    self.env.user,
                )
            publish(
                self.env,
                "site.risk_decision_recorded",
                "fix.site.risk.exception",
                rec.id,
                {
                    "exception": rec.name,
                    "site": rec.site_id.name,
                    "site_id": rec.site_id.id,
                    "decision": decision,
                    "decided_by": self.env.user.name,
                    "review_due_on": str(review_due_on) if review_due_on else None,
                },
            )
        return True

    def action_decide_continue(self, review_due_on=None, notes=None):
        """Continue operating on the lapse until a named review date."""
        today = fields.Date.context_today(self)
        try:
            review = fields.Date.to_date(review_due_on) if review_due_on else None
        except ValueError as exc:
            raise UserError("Review date %r is not a date (YYYY-MM-DD)." % review_due_on) from exc
        if not review or review <= today:
            raise UserError(
                "A continue decision is dated: give the review date (after today) by which it "
                "is taken again."
            )
        return self._exception_decide("continue", review, notes)

    def action_decide_suspend(self, notes=None):
        """Suspend the site until the lapse is resolved and it is re-verified."""
        for rec in self:
            if rec.site_id.state != "active":
                raise UserError("%s is not operating: nothing to suspend." % rec.site_id.name)
        return self._exception_decide("suspend", notes=notes)

    # ---- daily escalation (AUT-FAC-03: escalate daily until decided) ------
    @api.model
    def _exception_escalate(self):
        today = fields.Date.context_today(self)
        lapsed = self.sudo().search([("state", "=", "continue"), ("review_due_on", "<", today)])
        for rec in lapsed:
            rec._guarded().write({"state": "open", "decision_notes": False})
            rec.message_post(
                body="The continue decision lapsed on %s: a new decision is required."
                % rec.review_due_on
            )
        for rec in self.sudo().search([("state", "=", "open")]):
            if rec.last_escalated_on == today:
                continue
            rec._guarded().write({"last_escalated_on": today})
            rec.message_post(
                body="Escalation: %s is still operating on a lapsed licence with no decision."
                % rec.site_id.name
            )
        return True


class _InsertOnly(models.AbstractModel):
    """Rows only the lease service writes (superuser or transition token)."""

    _name = "fix.site.lease.insert.only"
    _description = "Insert-only lease record"
    _inherit = ["fix.guarded.mixin"]

    def _insert_only_refuse(self):
        raise UserError(
            "%s rows are written by the lease itself (record, modification, M52 payment "
            "match) and cannot be created, edited or deleted directly." % self._description
        )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            self._insert_only_refuse()
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            self._insert_only_refuse()
        return super().write(vals)

    def unlink(self):
        if self and not self._fix_guard_open():
            self._insert_only_refuse()
        return super().unlink()


class FixSiteLeaseSchedule(models.Model):
    _name = "fix.site.lease.schedule"
    _description = "Lease Rent Schedule"
    _inherit = ["fix.site.lease.insert.only"]
    _order = "lease_id, due_date"

    lease_id = fields.Many2one("fix.site.lease", required=True, ondelete="cascade", index=True)
    site_id = fields.Many2one(related="lease_id.site_id", store=True, index=True)
    period = fields.Char(required=True, help="YYYY-MM")
    due_date = fields.Date(required=True)
    escalation_year = fields.Integer(help="Lease years completed when the rent falls due")
    currency_id = fields.Many2one(related="lease_id.currency_id")
    rent_due = fields.Monetary(currency_field="currency_id")
    paid_amount = fields.Monetary(currency_field="currency_id", help="Matched by M52")
    paid_on = fields.Date()
    invoice_ref = fields.Char(string="Invoice Ref (M52)")
    variance = fields.Monetary(
        currency_field="currency_id", compute="_compute_variance", help="Paid minus due"
    )

    @api.depends("rent_due", "paid_amount")
    def _compute_variance(self):
        for rec in self:
            rec.variance = (rec.paid_amount or 0.0) - (rec.rent_due or 0.0) if rec.paid_on else 0.0


class FixSiteLeaseExtract(models.Model):
    _name = "fix.site.lease.extract"
    _description = "Lease Data Extract (IFRS 16)"
    _inherit = ["fix.site.lease.insert.only"]
    _order = "lease_id, version desc"

    lease_id = fields.Many2one("fix.site.lease", required=True, ondelete="cascade", index=True)
    site_id = fields.Many2one(related="lease_id.site_id", store=True, index=True)
    version = fields.Integer(required=True)
    reason = fields.Selection(
        [("recorded", "Lease Recorded"), ("modified", "Lease Modified")], required=True
    )
    payload = fields.Text(help="The accounting-relevant lease data, as published to M19/M49")
    published_at = fields.Datetime()
    consumed_by_m19_at = fields.Datetime(string="Consumed by M19 At")

    _lease_version_unique = models.Constraint(
        "UNIQUE (lease_id, version)", "One extract per lease and version"
    )
