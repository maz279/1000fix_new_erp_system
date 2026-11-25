# fix_facility_compliance — M47 records the A07 P1/P2 pass adds (2026-11-04):
# the operating-risk exception a licence lapse raises (BRU-FAC-02, AUT-FAC-03),
# the lease rent schedule (FR-FAC-012, BRU-FAC-12) and the versioned lease
# data extract for M19/M49 (BRU-FAC-13/14). The schedule and the extract are
# insert-only: only the lease's own service (superuser or a transition token)
# writes them, so the record Finance reads is the record M47 published.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

from .fix_facility import dhaka_today, site_cost_centre

# Who takes the continue-or-suspend decision (spec §8.1 "Operations Director
# / CEO", §13 R01 CEO). No CEO group exists: DOFA Tier 5 "Managing Director /
# Board" stands for the CEO, as in the P0 site-closure sign-off.
EXCEPTION_DECIDERS = ("cd_facility.group_operations_director", "cd_entity_config.group_dofa_tier_5")


class FixSiteRiskException(models.Model):
    """An operating-risk exception: a site operating on a lapsed licence."""

    _name = "fix.site.risk.exception"
    _description = "Site Operating-Risk Exception"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
        today = dhaka_today(self)
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
        today = dhaka_today(self)
        lapsed = self.sudo().search([("state", "=", "continue"), ("review_due_on", "<", today)])
        for rec in lapsed:
            rec._guarded().write({"state": "open", "decision_notes": False})
            rec.message_post(
                body="The continue decision lapsed on %s: a new decision is required."
                % rec.review_due_on
            )
        # a closed site operates on nothing: one left open is resolved, not chased
        self.sudo().search(
            [("state", "in", ("open", "continue", "suspend")), ("site_id.state", "=", "closed")]
        )._exception_resolve("the site is closed")
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        for rec in self.sudo().search([("state", "=", "open")]):
            if rec.last_escalated_on == today:
                continue
            rec._guarded().write({"last_escalated_on": today})
            # A07 ERP audit (2026-11-20) M47-15 / AUT-FAC-03: the escalation
            # reaches the people who decide (Operations Director, CEO), each day
            # a new to-do, not a chatter line nobody is told about
            deciders = rec._exception_decider_users()
            summary = (
                "Decide: %s is operating on a lapsed licence (%s) with no continue-or-suspend "
                "decision" % (rec.site_id.name, rec.licence_id.name or "-")
            )
            if todo:
                for user in deciders:
                    rec.activity_schedule(
                        activity_type_id=todo.id, summary=summary[:200], user_id=user.id
                    )
            rec.message_post(
                body="Escalation: %s is still operating on a lapsed licence with no decision. "
                "Told: %s." % (rec.site_id.name, ", ".join(deciders.mapped("name")) or "nobody")
            )
        return True

    def _exception_decider_users(self):
        self.ensure_one()
        users = self.env["res.users"]
        for xmlid in EXCEPTION_DECIDERS:
            group = self.env.ref(xmlid, raise_if_not_found=False)
            if group:
                users |= group.sudo().all_user_ids
        company = self.site_id.sudo().company_id
        return users.filtered(
            lambda u: u.active and not u.share and (not company or company in u.company_ids)
        )


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
    # A07 ERP audit (2026-11-20) M47-28: a payment covers `months` of rent (its
    # frequency) and carries the service charge; the advance rent the landlord
    # adjusts is taken off what is owed (M47-08).
    months = fields.Integer(default=1, help="Months of rent this payment covers")
    rent_due = fields.Monetary(currency_field="currency_id")
    service_charge_due = fields.Monetary(currency_field="currency_id", string="Service Charge")
    advance_adjusted = fields.Monetary(
        currency_field="currency_id",
        string="Advance Adjusted",
        help="Advance rent the landlord adjusted against this payment",
    )
    amount_payable = fields.Monetary(
        currency_field="currency_id",
        string="Payable",
        compute="_compute_amount_payable",
        store=True,
        help="Rent plus service charge, less the advance adjusted",
    )
    # M47-03: what the current terms would charge for a payment already sent
    revised_rent_due = fields.Monetary(
        currency_field="currency_id",
        string="Revised (after modification)",
        help="The amount under the lease's current terms, where it differs from what was sent",
    )
    # M47-27: rent before `schedule_from` (paid outside the system): never sent
    historical = fields.Boolean(string="History (not payable here)")
    cancelled = fields.Boolean(string="Cancelled (lease ended)")
    paid_amount = fields.Monetary(currency_field="currency_id", help="Paid on the vendor bill")
    paid_on = fields.Date()
    invoice_ref = fields.Char(string="Invoice Ref (M52)")
    ap_requested_on = fields.Date(string="Sent to AP On", readonly=True, copy=False)
    ap_block_reason = fields.Char(string="Not Sent Because", readonly=True, copy=False)
    # M47-06: a match to the landlord's bill is not a payment
    matched_on = fields.Date(string="Billed / Matched On")
    variance = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_variance",
        help="Paid (on the landlord's bill) minus payable",
    )

    @api.depends("rent_due", "service_charge_due", "advance_adjusted")
    def _compute_amount_payable(self):
        for rec in self:
            rec.amount_payable = round(
                (rec.rent_due or 0.0)
                + (rec.service_charge_due or 0.0)
                - (rec.advance_adjusted or 0.0),
                2,
            )

    @api.depends("amount_payable", "paid_amount", "paid_on")
    def _compute_variance(self):
        for rec in self:
            rec.variance = (
                (rec.paid_amount or 0.0) - (rec.amount_payable or 0.0) if rec.paid_on else 0.0
            )

    def _schedule_m52_vals(self):
        self.ensure_one()
        lease = self.lease_id.sudo()
        site = lease.site_id
        detail = "Rent %s, lease %s" % (self.period, lease.name)
        if self.service_charge_due:
            detail += ", service charge %.2f" % self.service_charge_due
        if self.advance_adjusted:
            detail += ", advance adjusted %.2f" % self.advance_adjusted
        return {
            "cost_type": "lease_rent",
            "company_id": (site.company_id or self.env.company).id,
            "operating_unit_id": site_cost_centre(site, "the rent of %s" % lease.name).id,
            "branch_id": site.branch_id.id,
            "site_id": site.id,
            "amount": self.amount_payable,
            "currency_id": self.currency_id.id,
            "cost_date": self.due_date,
            "vendor_id": lease.lessor_id.id,
            "payment_method": "vendor_bill",
            "detail": detail[:250],
        }

    def _schedule_refusal(self):
        """Why this payment cannot go to accounts payable, or None."""
        self.ensure_one()
        lease = self.lease_id.sudo()
        if self.historical:
            return (
                "%s of %s is before the lease's Rent Payable From date (%s): it is history, "
                "paid outside the system (M47-27)." % (self.period, lease.name, lease.schedule_from)
            )
        if self.cancelled:
            return "%s of %s was cancelled when the lease ended." % (self.period, lease.name)
        if lease.state != "active":
            return "Lease %s is %s: no rent is sent." % (
                lease.name,
                dict(lease._fields["state"].selection)[lease.state],
            )
        return None

    def _schedule_send(self):
        """Send the payment (service write): the advance the landlord adjusts is
        taken off, and the event states what AP owes, to whom, on which unit."""
        for rec in self.sudo():
            if rec.paid_on or rec.matched_on or rec.ap_requested_on:
                continue
            why = rec._schedule_refusal()
            if why:
                raise UserError(why)
            lease = rec.lease_id
            if lease.advance_adjust_monthly and lease.advance_balance > 0.005:
                adjust = min(
                    lease.advance_adjust_monthly * (rec.months or 1),
                    lease.advance_balance,
                    (rec.rent_due or 0.0) + (rec.service_charge_due or 0.0),
                )
                rec._guarded().write({"advance_adjusted": round(adjust, 2)})
            vals = rec._schedule_m52_vals()
            rec._guarded().write({"ap_requested_on": dhaka_today(rec), "ap_block_reason": False})
            publish(
                self.env,
                "lease.rent_payment_requested",
                rec._name,
                rec.id,
                {
                    "lease": lease.name,
                    "site": rec.site_id.name,
                    "site_id": rec.site_id.id,
                    "period": rec.period,
                    "due_date": str(rec.due_date),
                    "amount": float(rec.amount_payable or 0.0),
                    "lessor_id": lease.lessor_id.id,
                    "rent": float(rec.rent_due or 0.0),
                    "service_charge": float(rec.service_charge_due or 0.0),
                    "advance_adjusted": float(rec.advance_adjusted or 0.0),
                    "operating_unit_id": vals["operating_unit_id"],
                },
            )

    def action_send_to_ap(self):
        """Send this payment's rent to AP as a pending cost entry (BRU-FAC-12).
        Accounts payable matches it to the landlord's bill. Sending it twice is
        one entry. The daily job sends what falls due (M47-07)."""
        if not self.env.su and not self.env.user.has_group("cd_facility.group_facility_manager"):
            raise UserError("Rent is sent to accounts payable by a Facility Manager.")
        self._schedule_send()
        return True

    @api.model
    def _schedule_due_domain(self, today):
        return [
            ("due_date", "<=", today),
            ("ap_requested_on", "=", False),
            ("matched_on", "=", False),
            ("paid_on", "=", False),
            ("historical", "=", False),
            ("cancelled", "=", False),
            ("lease_id.state", "=", "active"),
        ]

    @api.model
    def cron_rent_due_to_ap(self):
        """Daily (AUT-FAC-06, M47-07): every payment of an active lease that has
        fallen due (Dhaka day) and is not yet with accounts payable is sent. One
        that cannot go (no cost centre) keeps the reason on the row, and the next
        run tries again. Idempotent."""
        today = dhaka_today(self)
        sent = 0
        for row in self.sudo().search(self._schedule_due_domain(today), order="due_date, id"):
            try:
                with self.env.cr.savepoint():
                    row._schedule_send()
                sent += 1
            except UserError as exc:
                reason = str(exc)[:250]
                if row.ap_block_reason != reason:
                    row._guarded().write({"ap_block_reason": reason})
                    row.lease_id.message_post(
                        body="Rent %s could not go to accounts payable: %s" % (row.period, reason)
                    )
        return sent

    def _m52_match_refusal(self):
        self.ensure_one()
        return self._schedule_refusal() if (self.historical or self.cancelled) else None

    # ---- the M52 source contract (cd_asset_finance_hse_bridge m52_cost.py) --
    def _m52_mark_billed(self, bill_date=None, invoice_ref=None):
        """AP matched this rent to the landlord's bill (M47-06): billed, not paid."""
        self.sudo()._guarded().write(
            {"matched_on": bill_date or dhaka_today(self), "invoice_ref": invoice_ref or False}
        )

    def _m52_mark_paid(self, amount, paid_on, invoice_ref=None):
        """M47-05: the landlord's bill is paid: paid = the bill's amount for this
        payment, so a landlord who over-bills shows as a variance."""
        vals = {"paid_amount": amount, "paid_on": paid_on}
        if invoice_ref:
            vals["invoice_ref"] = invoice_ref
        self.sudo()._guarded().write(vals)

    def _m52_mark_unbilled(self, reason=None):
        """M47-06: the bill was rejected or reset: the rent is owed again (its
        cost entry is back with AP), neither billed nor paid."""
        for rec in self.sudo():
            rec._guarded().write(
                {"matched_on": False, "paid_amount": 0.0, "paid_on": False, "invoice_ref": False}
            )
            rec.lease_id.message_post(
                body="Rent %s is owed again: its landlord bill was %s."
                % (rec.period, reason or "rejected or reset")
            )


class FixSiteLeaseExtract(models.Model):
    _name = "fix.site.lease.extract"
    _description = "Lease Data Extract (IFRS 16)"
    _inherit = ["fix.site.lease.insert.only"]
    _order = "lease_id, version desc"

    lease_id = fields.Many2one("fix.site.lease", required=True, ondelete="cascade", index=True)
    site_id = fields.Many2one(related="lease_id.site_id", store=True, index=True)
    version = fields.Integer(required=True)
    reason = fields.Selection(
        [
            ("recorded", "Lease Recorded"),
            ("modified", "Lease Modified"),
            ("terminated", "Lease Terminated"),
        ],
        required=True,
    )
    payload = fields.Text(help="The accounting-relevant lease data, as published to M19/M49")
    published_at = fields.Datetime()
    consumed_by_m19_at = fields.Datetime(string="Consumed by M19 At")

    _lease_version_unique = models.Constraint(
        "UNIQUE (lease_id, version)", "One extract per lease and version"
    )
