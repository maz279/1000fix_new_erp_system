# fix_facility_money — A07 ERP audit (2026-11-20): the M47 money facts.
#
# M47 records what a site owes and holds; the A07 bridge (cd_asset_finance_hse_bridge,
# `fix.asset.cost.entry`) turns each fact into one pending M52 cost entry and posts it.
#   * fix.site.charge: a deposit or advance rent paid to a landlord, its refund,
#     adjustment or write-off (M47-08, with a DOFA approval for every settlement),
#     a licence fee, agent cost or late penalty (M47-10), a lease break penalty
#     (M47-04);
#   * fix.site.project.cost: what a fit-out / site project actually cost, line by
#     line against the vendor's invoice, booked to CWIP (M47-11);
#   * fix.site.outage.impact: the open M01 / M02 orders of a branch stopped by an
#     outage, the window their SLA clock must not be charged for (M47-17).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_facility import dhaka_today, queue_cost, site_cost_centre
from .fix_facility_ops import BRANCH_LEAD, FACILITY_MANAGER

CHARGE_KINDS = [
    ("deposit_paid", "Security Deposit Paid"),
    ("advance_paid", "Advance Rent Paid"),
    ("deposit_refund", "Security Deposit Refunded"),
    ("deposit_adjusted", "Security Deposit Adjusted Against Dues"),
    ("deposit_write_off", "Security Deposit Written Off"),
    ("advance_refund", "Advance Rent Refunded"),
    ("advance_write_off", "Advance Rent Written Off"),
    ("lease_break_penalty", "Lease Break Penalty"),
    ("licence_fee", "Licence Government Fee"),
    ("licence_other", "Licence Agent / Inspection Cost"),
    ("licence_penalty", "Licence Late Penalty"),
]
# The M52 cost type (and subtype) of each kind. The bridge maps a cost type,
# or "<cost type>.<subtype>" where its account role is set, to its account (D3):
# deposit 100031, advance rent 100032, licence fees 500503 / 500209.
CHARGE_COST_TYPES = {
    "deposit_paid": ("deposit", False),
    "advance_paid": ("advance_rent", False),
    "deposit_refund": ("deposit", "refund"),
    "deposit_adjusted": ("deposit", "adjusted"),
    "deposit_write_off": ("deposit", "write_off"),
    "advance_refund": ("advance_rent", "refund"),
    "advance_write_off": ("advance_rent", "write_off"),
    "lease_break_penalty": ("lease_rent", "break_penalty"),
    "licence_fee": ("licence_fee", "government_fee"),
    "licence_other": ("licence_fee", "agent"),
    "licence_penalty": ("licence_fee", "penalty"),
}
# Money coming back or given up: each is a decision (BRU-FAC-15).
SETTLEMENT_KINDS = (
    "deposit_refund",
    "deposit_adjusted",
    "deposit_write_off",
    "advance_refund",
    "advance_write_off",
)
# No owner figure exists for a deposit settlement: the estate cost ladder
# (O-2, fix_facility.ESTATE_COST_DOFA_THRESHOLDS) without its Tier 0, so every
# settlement, however small, is approved by someone other than its requester.
SETTLEMENT_DOFA_THRESHOLDS = [
    (250000.0, "tier_2"),
    (1000000.0, "tier_3"),
    (float("inf"), "tier_4"),
]
PAYMENT_METHODS = [
    ("vendor_bill", "Vendor Bill (Accounts Payable)"),
    ("petty_cash", "Petty Cash"),
    ("employee_expense", "Employee Expense Claim"),
    ("internal", "Internal (no payment)"),
]
CHARGE_FACTS = (
    "site_id",
    "operating_unit_id",
    "lease_id",
    "renewal_id",
    "kind",
    "amount",
    "currency_id",
    "charge_date",
    "vendor_id",
    "payment_method",
    "employee_id",
    "state",
    "confirmed_by_id",
    "confirmed_on",
    "requested_by_id",
    "billed_on",
    "paid_on",
)


class FixApprovalMatrixFacilityMoney(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("site_charge_settlement", "Site Deposit / Advance Settlement")],
        ondelete={"site_charge_settlement": "cascade"},
    )


class FixSiteCharge(models.Model):
    _name = "fix.site.charge"
    _description = "Site Charge (deposit, advance rent, licence fee, penalty)"
    _inherit = ["mail.thread", "fix.dofa.mixin"]
    _order = "charge_date desc, id desc"

    _approval_domain = "site_charge_settlement"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    site_id = fields.Many2one("fix.site", required=True, index=True, ondelete="restrict")
    company_id = fields.Many2one(related="site_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Cost Centre (OU)", required=True, index=True
    )
    lease_id = fields.Many2one("fix.site.lease", index=True, ondelete="restrict")
    renewal_id = fields.Many2one("fix.site.licence.renewal", index=True, ondelete="restrict")
    kind = fields.Selection(CHARGE_KINDS, required=True)
    cost_type = fields.Char(compute="_compute_cost_type", store=True, string="M52 Cost Type")
    cost_subtype = fields.Char(compute="_compute_cost_type", store=True, string="M52 Subtype")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    charge_date = fields.Date(required=True, default=lambda self: dhaka_today(self))
    vendor_id = fields.Many2one("res.partner", string="Payee / Counterparty")
    invoice_ref = fields.Char(string="Invoice / Challan / Receipt Ref")
    payment_method = fields.Selection(PAYMENT_METHODS, required=True, default="vendor_bill")
    employee_id = fields.Many2one("hr.employee", string="Employee (expense claim)")
    reason = fields.Char(string="Basis")
    state = fields.Selection(
        [("draft", "Awaiting Approval"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
        tracking=True,
    )
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True)
    confirmed_by_id = fields.Many2one("res.users", string="Confirmed By", readonly=True)
    confirmed_on = fields.Date(readonly=True)
    billed_on = fields.Date(readonly=True, copy=False)
    paid_on = fields.Date(readonly=True, copy=False)

    # ---- the M52 source contract -------------------------------------------
    def _m52_mark_billed(self, bill_date=None, invoice_ref=None):
        vals = {"billed_on": bill_date or dhaka_today(self)}
        if invoice_ref:
            vals["invoice_ref"] = invoice_ref
        self.sudo()._guarded().write(vals)

    def _m52_mark_paid(self, amount, paid_on, invoice_ref=None):
        self.sudo()._guarded().write({"paid_on": paid_on})

    def _m52_mark_unbilled(self, reason=None):
        self.sudo()._guarded().write({"billed_on": False, "paid_on": False})

    @api.depends("kind", "renewal_id.licence_type")
    def _compute_cost_type(self):
        for rec in self:
            ctype, sub = CHARGE_COST_TYPES.get(rec.kind, (False, False))
            if rec.kind == "licence_fee" and rec.renewal_id:
                sub = rec.renewal_id.licence_type or sub  # trade / fire / ... (D3)
            rec.cost_type, rec.cost_subtype = ctype, sub

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if (rec.amount or 0.0) <= 0.0:
                raise ValidationError("A charge is a positive amount.")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(CHARGE_FACTS) | {"name"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields() | set(CHARGE_FACTS)
        if len(self) == 1 and self.state != "draft":
            locked |= {"invoice_ref", "reason"}
        return locked

    # ---- DOFA: a settlement is approved on its amount ----------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return (self.amount or 0.0) if self.kind in SETTLEMENT_KINDS else 0.0

    def _dofa_thresholds(self):
        return SETTLEMENT_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (%s)" % (self._dofa_amount(), dict(CHARGE_KINDS).get(self.kind, ""))

    @api.depends("amount", "kind")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"vendor_id", "lease_id", "site_id", "kind"}

    def action_dofa_approve(self):
        self._approval_assert_routed()
        return super(FixSiteCharge, self.sudo()).action_dofa_approve()

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft" or rec.kind not in SETTLEMENT_KINDS:
                raise UserError("%s needs no approval." % rec.name)
        return super().action_request_approval(
            justification=justification or (self[:1].reason if len(self) == 1 else None)
        )

    # ---- raising (services only) ------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(
                "A site charge is raised by the record it belongs to (a lease, a licence "
                "renewal, a deposit settlement), not typed in."
            )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.site.charge") or "SCHG/New"
                )
        return super().create(vals_list)

    @api.model
    def _charge_raise(
        self,
        site,
        kind,
        amount,
        lease=None,
        renewal=None,
        vendor=None,
        reason=None,
        payment_method="vendor_bill",
        employee=None,
        invoice_ref=None,
        confirm=True,
        requester=None,
        charge_date=None,
    ):
        """Raise one charge; a payment (not a settlement) is confirmed and
        queued to M52 at once. Returns the charge."""
        label = dict(CHARGE_KINDS)[kind]
        ou = site_cost_centre(site, "the %s" % label.lower())
        if payment_method == "vendor_bill" and not vendor:
            raise UserError("%s needs its payee (the vendor accounts payable pays)." % label)
        if payment_method == "employee_expense" and not employee:
            raise UserError("%s paid by an employee names the employee." % label)
        charge = (
            self.sudo()
            ._guarded()
            .create(
                {
                    "site_id": site.id,
                    "operating_unit_id": ou.id,
                    "lease_id": lease.id if lease else False,
                    "renewal_id": renewal.id if renewal else False,
                    "kind": kind,
                    "amount": round(amount, 2),
                    "currency_id": (lease.currency_id if lease else self.env.ref("base.BDT")).id,
                    "charge_date": charge_date or dhaka_today(self),
                    "vendor_id": vendor.id if vendor else False,
                    "invoice_ref": invoice_ref or False,
                    "payment_method": payment_method,
                    "employee_id": employee.id if employee else False,
                    "reason": (reason or "")[:250] or False,
                    "requested_by_id": (requester or self.env.user).id,
                }
            )
        )
        if confirm:
            charge._charge_confirm()
        return charge

    def _charge_m52_vals(self):
        self.ensure_one()
        site = self.site_id.sudo()
        return {
            "cost_type": self.cost_type,
            "subtype": self.cost_subtype or False,
            "company_id": site.company_id.id,
            "operating_unit_id": self.operating_unit_id.id,
            "branch_id": site.branch_id.id,
            "site_id": site.id,
            "amount": self.amount,
            "currency_id": self.currency_id.id,
            "cost_date": self.charge_date,
            "vendor_id": self.vendor_id.id,
            "invoice_ref": self.invoice_ref or False,
            "payment_method": self.payment_method,
            "employee_id": self.employee_id.id,
            "detail": ("%s: %s" % (dict(CHARGE_KINDS)[self.kind], self.reason or "-"))[:250],
        }

    def _charge_confirm(self):
        for rec in self.sudo():
            rec._guarded().write(
                {
                    "state": "confirmed",
                    "confirmed_by_id": self.env.uid,
                    "confirmed_on": dhaka_today(rec),
                }
            )
            queue_cost(rec, rec._charge_m52_vals())

    def action_confirm(self):
        """A settlement, once approved, is confirmed: it goes to M52. Never more
        than the lease still holds."""
        if not self.env.su and not (
            self.env.user.has_group(FACILITY_MANAGER) or self.env.user.has_group(BRANCH_LEAD)
        ):
            raise UserError("A settlement is confirmed by a Facility Manager.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not awaiting confirmation." % rec.name)
            rec._dofa_assert_approved("Settlement %s" % rec.name)
            lease = rec.lease_id.sudo()
            if lease:
                held = (
                    lease.advance_balance
                    if rec.kind.startswith("advance")
                    else lease.deposit_balance
                )
                if rec.amount > held + 0.005:
                    raise UserError(
                        "%s holds %.2f: %s of %.2f is more than that."
                        % (lease.name, held, rec.name, rec.amount)
                    )
            rec._charge_confirm()
        return True

    def action_cancel(self, reason=None):
        if not self.env.su and not self.env.user.has_group(FACILITY_MANAGER):
            raise UserError("A charge is cancelled by a Facility Manager.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a charge awaiting approval is cancelled.")
            rec.sudo()._dofa_void_approval("the settlement was cancelled")
            rec._guarded().write({"state": "cancelled"})
            rec.message_post(body="Cancelled: %s" % ((reason or "").strip() or "-"))
        return True


class FixSiteProjectCost(models.Model):
    """M47-11: what a site project actually cost, against the vendor's invoice."""

    _name = "fix.site.project.cost"
    _description = "Site Project Actual Cost Line"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "cost_date desc, id desc"

    project_id = fields.Many2one("fix.site.project", required=True, index=True, ondelete="restrict")
    site_id = fields.Many2one(related="project_id.site_id", store=True, index=True)
    company_id = fields.Many2one(related="site_id.company_id", store=True, index=True)
    description = fields.Char(required=True)
    vendor_id = fields.Many2one("res.partner", string="Vendor", required=True)
    invoice_ref = fields.Char(string="Vendor Invoice Ref", required=True)
    currency_id = fields.Many2one(related="project_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id", required=True)
    cost_date = fields.Date(required=True, default=lambda self: dhaka_today(self))
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
        tracking=True,
    )
    confirmed_by_id = fields.Many2one("res.users", readonly=True)
    confirmed_on = fields.Date(readonly=True)

    _FACTS = ("project_id", "description", "vendor_id", "invoice_ref", "amount", "cost_date")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "confirmed_by_id", "confirmed_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(self._FACTS)
        return locked

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if (rec.amount or 0.0) <= 0.0:
                raise ValidationError("A cost line is a positive amount.")

    def write(self, vals):
        if self and not self._fix_guard_open():
            facts = set(self._FACTS) & set(vals)
            for rec in self.filtered(lambda r: r.state != "draft"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in facts):
                    raise UserError("%s is confirmed: it does not change." % rec.display_name)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and not self.env.user.has_group(FACILITY_MANAGER):
            raise UserError("A project cost is recorded by a Facility Manager.")
        Project = self.env["fix.site.project"].sudo()
        for vals in vals_list:
            project = Project.browse(vals.get("project_id")).exists()
            if project and project.state == "done":
                raise UserError("%s is complete: it takes no more cost." % project.name)
        return super().create(vals_list)

    def action_confirm(self):
        """The cost is owed to the vendor: it goes to M52 (CWIP for a
        capitalised fit-out). Never past the approved budget: revise it first."""
        if not self.env.su and not self.env.user.has_group(FACILITY_MANAGER):
            raise UserError("A project cost is confirmed by a Facility Manager.")
        for rec in self:
            project = rec.project_id.sudo()
            if rec.state != "draft":
                raise UserError("%s is not a draft." % rec.display_name)
            if project.state != "in_progress":
                raise UserError("%s is not in progress: start it first." % project.name)
            project._dofa_assert_approved("Spending on project %s" % project.name)
            spent = project.actual_cost + rec.amount
            if spent > (project.budget or 0.0) + 0.005:
                raise UserError(
                    "%s would cost %.2f against its approved budget of %.2f: revise the budget "
                    "(and have it approved) first." % (project.name, spent, project.budget or 0.0)
                )
            site = project.site_id
            rec._guarded().write(
                {
                    "state": "confirmed",
                    "confirmed_by_id": self.env.uid,
                    "confirmed_on": dhaka_today(rec),
                }
            )
            queue_cost(
                rec,
                {
                    # a capitalised fit-out books to CWIP (role facility_work_order.fit_out)
                    "cost_type": "facility_work_order",
                    "subtype": "fit_out" if project.capitalise else "project",
                    "company_id": site.company_id.id,
                    "operating_unit_id": site_cost_centre(site, "project %s" % project.name).id,
                    "branch_id": site.branch_id.id,
                    "site_id": site.id,
                    "amount": rec.amount,
                    "currency_id": rec.currency_id.id,
                    "cost_date": rec.cost_date,
                    "vendor_id": rec.vendor_id.id,
                    "invoice_ref": rec.invoice_ref,
                    "payment_method": "vendor_bill",
                    "detail": (
                        "%s: %s%s"
                        % (
                            project.name,
                            rec.description,
                            " (CWIP %s)" % project.cwip_ref if project.cwip_ref else "",
                        )
                    )[:250],
                },
            )
        return True

    def action_cancel(self):
        if not self.env.su and not self.env.user.has_group(FACILITY_MANAGER):
            raise UserError("A project cost is cancelled by a Facility Manager.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("A confirmed cost is owed: it is not cancelled here.")
            rec._guarded().write({"state": "cancelled"})
        return True


# --------------------------------------------------------------------------
# M47-17: a stopped branch, and the orders whose SLA it must not be charged to
# --------------------------------------------------------------------------
IMPACT_SOURCES = (
    # model, the states in which the order is no longer running
    ("fix.service.order", ("delivered", "closed", "cancelled")),
    ("fix.field.order", ("completed", "cancelled", "declined")),
)


class FixSiteOutageImpact(models.Model):
    _name = "fix.site.outage.impact"
    _description = "Outage Impact on an Open Service Order (SLA exclusion window)"
    _inherit = ["fix.guarded.mixin"]
    _order = "window_start desc, id desc"

    outage_id = fields.Many2one("fix.site.outage", required=True, index=True, ondelete="cascade")
    site_id = fields.Many2one(related="outage_id.site_id", store=True, index=True)
    company_id = fields.Many2one(related="site_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", index=True)
    res_model = fields.Char(string="Order Type", required=True, index=True)
    res_id = fields.Many2oneReference(string="Order Record", model_field="res_model", required=True)
    order_ref = fields.Char(string="Order")
    order_state = fields.Char(string="State When Stopped")
    window_start = fields.Datetime(required=True)
    window_end = fields.Datetime(required=True)
    hours_lost = fields.Float(digits=(10, 2))

    _one_per_order = models.Constraint(
        "UNIQUE (outage_id, res_model, res_id)", "One impact row per outage and order"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "outage_id",
            "operating_unit_id",
            "res_model",
            "res_id",
            "order_ref",
            "order_state",
            "window_start",
            "window_end",
            "hours_lost",
        }


class FixSiteOutageConsumer(models.Model):
    _inherit = "fix.site.outage"

    impact_ids = fields.One2many("fix.site.outage.impact", "outage_id", string="Orders Affected")

    @api.model
    def consume_site_outage(self, event):
        """site.outage (M47-17 / AUT-FAC-12): when the branch could not operate,
        every M01 service order and M02 field order still running at that branch
        is recorded against the outage window, so its SLA (an A02 clock) can
        exclude it and no technician is charged for a dead branch. Idempotent."""
        if event.get("aggregate") != self._name:
            return False
        outage = self.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not outage or not outage.branch_stopped or not outage.ended_at:
            return False
        site = outage.site_id.sudo()
        ou = site.operating_unit_id or site.branch_id.operating_unit_id
        Impact = self.env["fix.site.outage.impact"].sudo()._guarded()
        known = {(i.res_model, i.res_id) for i in outage.impact_ids}
        made = 0
        for model, finished in IMPACT_SOURCES:
            if model not in self.env:
                continue
            Order = self.env[model].sudo()
            domain = [("state", "not in", finished), ("create_date", "<=", outage.ended_at)]
            if ou and "operating_unit_id" in Order._fields:
                domain.append(("operating_unit_id", "=", ou.id))
            elif site.branch_id and "branch_id" in Order._fields:
                domain.append(("branch_id", "=", site.branch_id.id))
            else:
                continue
            for order in Order.search(domain):
                if (model, order.id) in known:
                    continue
                Impact.create(
                    {
                        "outage_id": outage.id,
                        "operating_unit_id": ou.id,
                        "res_model": model,
                        "res_id": order.id,
                        "order_ref": order.display_name,
                        "order_state": order.state,
                        "window_start": outage.started_at,
                        "window_end": outage.ended_at,
                        "hours_lost": outage.operating_hours_lost,
                    }
                )
                made += 1
        if made:
            site.message_post(
                body="%s: %d open service / field order(s) flagged for SLA impact (%.2f "
                "operating hours lost)." % (outage.name, made, outage.operating_hours_lost)
            )
        return True
