# fix_payroll_ops — M56: salary structures, festival bonus runs, tax
# certificates, quarterly withholding returns and off-cycle payments.
# Periods, payslips and BEFTN batches live in fix_payroll.py.
#
# A09 workflow audit (2026-11-03), P0 A4: each document here was a set of
# plain-writable state flags. An officer created and approved his own
# BDT 5,000,000 off-cycle payment, then changed its amount and payee; wrote
# 'paid' directly; "trustee-approved" WPPF himself and rewrote the profit.
# Every document now carries fix.payroll.state.lock: state, the actor stamps
# and the computed amounts change only in a transition, and what was approved
# freezes. Approval needs the Payroll Manager role and a second person.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

PAYROLL_MANAGER = "cd_payroll_bd.group_payroll_manager"


def check_payroll_approver(records, what, makers):
    """Approval of `what`: the Payroll Manager role, and an approver who is
    none of the users `makers(rec)` returns (preparer, calculator)."""
    user = records.env.user
    if not user.has_group(PAYROLL_MANAGER):
        raise AccessError("Only a Payroll Manager can approve %s." % what)
    for rec in records:
        if user in makers(rec):
            raise UserError(
                "Maker-Checker SoD violation: %s %s was prepared or calculated by %s, who "
                "cannot also approve it." % (rec._description, rec.display_name, user.name)
            )


class FixPayrollStructure(models.Model):
    _name = "fix.payroll.structure"
    _description = "Salary Structure"
    _order = "grade"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    grade = fields.Char(string="Grade / Band")
    basic_pct = fields.Float(string="Basic % of Gross", default=60.0)
    house_rent_pct = fields.Float(string="House Rent %", default=30.0)
    transport_fixed = fields.Monetary(currency_field="currency_id", string="Transport (fixed)")
    medical_fixed = fields.Monetary(currency_field="currency_id", string="Medical (fixed)")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    pf_applicable = fields.Boolean(string="Provident Fund Applicable", default=True)
    gratuity_applicable = fields.Boolean(string="Gratuity Applicable", default=True)
    active = fields.Boolean(default=True)

    _basic_house_range = models.Constraint(
        "CHECK (basic_pct >= 0 AND basic_pct <= 100 AND house_rent_pct >= 0 AND house_rent_pct <= 100)",
        "Structure percentages are 0-100",
    )


class FixFestivalBonusRun(models.Model):
    _name = "fix.payroll.bonus.run"
    _description = "Festival Bonus Run"
    _inherit = ["fix.payroll.state.lock"]
    _order = "bonus_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    festival = fields.Selection(
        [
            ("eid_ul_fitr", "Eid-ul-Fitr"),
            ("eid_ul_adha", "Eid-ul-Adha"),
            ("durga_puja", "Durga Puja"),
            ("other", "Other"),
        ],
        required=True,
        default="eid_ul_fitr",
    )
    bonus_date = fields.Date(required=True, default=fields.Date.context_today)
    basis = fields.Selection(
        [("basic", "Basic Salary"), ("gross", "Gross Salary")],
        required=True,
        default="basic",
    )
    multiplier = fields.Float(string="Multiplier (months)", default=1.0)
    employee_count = fields.Integer(readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("paid", "Paid")],
        required=True,
        default="draft",
    )
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", readonly=True, default=lambda self: self.env.user
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(string="Approved On", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "prepared_by_id",
            "approved_by_id",
            "approved_on",
            "employee_count",
            "total_amount",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {"festival", "bonus_date", "basis", "multiplier", "company_id"}
            locked |= {"operating_unit_id", "currency_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.payroll.bonus.run") or "BON/New"
                )
        return super().create(vals_list)

    def action_approve(self):
        check_payroll_approver(self, "a festival bonus run", lambda rec: rec.prepared_by_id)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft bonus run")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_on": fields.Datetime.now(),
                }
            )

    def action_pay(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Pay an approved bonus run")
            rec._guarded().write({"state": "paid"})


class FixPayrollCertificate(models.Model):
    _name = "fix.payroll.certificate"
    _description = "Tax / Salary Certificate"
    _inherit = ["fix.payroll.state.lock"]
    _order = "fiscal_year desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    certificate_type = fields.Selection(
        [
            ("salary", "Salary Certificate"),
            ("tax", "Tax Deduction Certificate"),
            ("employment", "Employment Certificate"),
        ],
        required=True,
        default="salary",
    )
    fiscal_year = fields.Char(required=True)
    # stamped by action_issue: a draft certificate has not been issued
    issued_on = fields.Date(readonly=True)
    amount = fields.Monetary(currency_field="currency_id", string="Annual Figure")
    total_gross = fields.Monetary(currency_field="currency_id", string="Total Gross Salary")
    total_basic = fields.Monetary(currency_field="currency_id", string="Total Basic Salary")
    total_allowances = fields.Monetary(currency_field="currency_id", string="Total Allowances")
    total_tax_withheld = fields.Monetary(
        currency_field="currency_id", string="Total Income Tax Withheld (TDS)"
    )
    total_pf_deducted = fields.Monetary(
        currency_field="currency_id", string="Total Provident Fund Contributed"
    )
    challan_refs = fields.Char(string="Treasury Challan References")
    state = fields.Selection(
        [("draft", "Draft"), ("issued", "Issued")],
        default="draft",
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    reference = fields.Char()

    def _fix_guarded_fields(self) -> set:
        # the figures come from the payslips, never typed (A09 probe T4: a
        # certificate was issued with a typed gross of 9,999,999)
        return super()._fix_guarded_fields() | {
            "state",
            "issued_on",
            "amount",
            "total_gross",
            "total_basic",
            "total_allowances",
            "total_tax_withheld",
            "total_pf_deducted",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state == "issued":
            locked |= {"employee_id", "certificate_type", "fiscal_year", "company_id"}
            locked |= {"currency_id", "challan_refs", "reference"}
        return locked

    def action_compute_from_payslips(self):
        """Aggregate fiscal year payslips for the employee (ITA 2023 s.108/114 certificate)."""
        for rec in self:
            if rec.state == "issued":
                raise UserError("Certificate %s is issued - its figures are final." % rec.name)
            slips = self.env["fix.payslip"].search(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("company_id", "=", rec.company_id.id),
                ]
            )
            gross = sum(slips.mapped("gross"))
            basic = sum(slips.mapped("basic"))
            allow = sum(slips.mapped("allowances_total"))
            # the payslip's withheld tax (it read a non-existent `income_tax`
            # and crashed, A09 probe T1)
            tax = sum(slips.mapped("tax_withheld"))
            pf = sum(slips.mapped("pf_employee"))
            rec._guarded().write(
                {
                    "total_gross": gross,
                    "total_basic": basic,
                    "total_allowances": allow,
                    "total_tax_withheld": tax,
                    "total_pf_deducted": pf,
                    "amount": tax if rec.certificate_type == "tax" else gross,
                }
            )

    def action_issue(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Issue a draft certificate")
            # always from the payslips at the moment of issue
            rec.action_compute_from_payslips()
            rec._guarded().write({"state": "issued", "issued_on": fields.Date.context_today(self)})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.payroll.certificate") or "CERT/New"
                )
        return super().create(vals_list)


class FixWithholdingReturn(models.Model):
    _name = "fix.payroll.return"
    _description = "Quarterly Withholding Return"
    _inherit = ["fix.payroll.state.lock"]
    _order = "period desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    period = fields.Char(required=True, help="Quarter, e.g. Q1-2026")
    period_start = fields.Date(string="Period Start")
    period_end = fields.Date(string="Period End")
    challan_number = fields.Char(string="Treasury Challan No")
    challan_date = fields.Date(string="Treasury Challan Date")
    tax_zone = fields.Char(string="NBR Tax Zone / Circle")
    employee_count = fields.Integer()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total_tax = fields.Monetary(currency_field="currency_id", string="Tax Withheld")
    filed_on = fields.Date(readonly=True)
    acknowledgement = fields.Char(string="NBR Acknowledgement")
    state = fields.Selection(
        [("draft", "Draft"), ("filed", "Filed")], required=True, default="draft"
    )

    def _fix_guarded_fields(self) -> set:
        # the totals come from the payslips (action_reconcile_payslips)
        return super()._fix_guarded_fields() | {"state", "filed_on", "employee_count", "total_tax"}

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state == "filed":
            locked |= {"period", "period_start", "period_end", "challan_number"}
            locked |= {"challan_date", "tax_zone", "acknowledgement", "company_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.payroll.return") or "PWR/New"
                )
        return super().create(vals_list)

    def action_reconcile_payslips(self):
        """Reconcile quarterly/monthly payslip TDS totals against withholding return."""
        for rec in self:
            if rec.state == "filed":
                raise UserError("Return %s is filed - its totals are final." % rec.name)
            # `tax_withheld` is the payslip's field (`income_tax` crashed, A09 T2)
            domain = [("company_id", "=", rec.company_id.id), ("tax_withheld", ">", 0)]
            if rec.period_start:
                domain.append(("period_id.period_start", ">=", rec.period_start))
            if rec.period_end:
                domain.append(("period_id.period_end", "<=", rec.period_end))
            slips = self.env["fix.payslip"].search(domain)
            rec._guarded().write(
                {
                    "employee_count": len(slips.mapped("employee_id")),
                    "total_tax": sum(slips.mapped("tax_withheld")),
                }
            )

    def action_file(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("File a draft return")
            rec._guarded().write({"state": "filed", "filed_on": fields.Date.context_today(self)})


class FixOffcyclePayment(models.Model):
    _name = "fix.payroll.offcycle"
    _description = "Off-Cycle Payment"
    _inherit = ["fix.payroll.state.lock"]
    _order = "payment_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    payment_type = fields.Selection(
        [
            ("advance", "Salary Advance"),
            ("arrear", "Arrear"),
            ("adjustment", "Adjustment"),
            ("settlement", "Final Settlement Part"),
        ],
        required=True,
        default="arrear",
    )
    payment_date = fields.Date(required=True, default=fields.Date.context_today)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    reason = fields.Char()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("paid", "Paid"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", readonly=True, default=lambda self: self.env.user
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(string="Approved On", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "prepared_by_id",
            "approved_by_id",
            "approved_on",
        }

    def _payroll_state_locked_fields(self) -> set:
        # what was approved is what is paid: amount AND payee (A09 probe O4)
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {"employee_id", "amount", "currency_id", "payment_type"}
            locked |= {"payment_date", "company_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.payroll.offcycle") or "OFC/New"
                )
        return super().create(vals_list)

    def action_approve(self):
        check_payroll_approver(self, "an off-cycle payment", lambda rec: rec.prepared_by_id)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft off-cycle payment")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_on": fields.Datetime.now(),
                }
            )

    def action_pay(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Pay an approved off-cycle payment")
            rec._guarded().write({"state": "paid"})


class FixWppfAllocation(models.Model):
    """BLA 2006 Chapter XV (Sections 232-252): Workers' Profit Participation Fund (WPPF).

    Statutory 5% of net profit allocated 80:10:10 across:
    - 80% Participatory Fund (2/3 distributed equally, 1/3 invested per s.242)
    - 10% Welfare Fund
    - 10% Bangladesh Workers Welfare Foundation Fund (BWWF Act 2006)
    """

    _name = "fix.wppf.allocation"
    _description = "WPPF 5% Profit Participation Allocation (BLA Ch. XV)"
    _inherit = ["fix.payroll.state.lock"]
    _order = "fiscal_year desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    fiscal_year = fields.Char(required=True, string="Fiscal Year", help="e.g. 2025-2026")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    net_profit = fields.Monetary(
        currency_field="currency_id", required=True, string="Audited Net Profit (BLA s.234)"
    )
    total_wppf_pool = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="Total 5% WPPF Pool",
    )
    participatory_fund_amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="Participatory Fund (80%)",
    )
    welfare_fund_amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="Welfare Fund (10%)",
    )
    welfare_foundation_amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="BWWF Government Foundation (10%)",
    )
    equal_distribution_pool = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="2/3 Cash Distribution Pool (BLA s.242)",
    )
    investment_pool_share = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="1/3 Investment Unit Pool (BLA s.242)",
    )
    eligible_workers_count = fields.Integer(
        string="Eligible Beneficiaries Count (BLA s.240)", default=0
    )
    per_worker_equal_share = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_wppf_split",
        store=True,
        string="Equal Per-Worker Cash Share",
    )
    fiscal_year_end_date = fields.Date(string="Fiscal Year Close Date")
    distribution_due_date = fields.Date(
        string="Statutory Transfer Deadline (9 Months, s.234)",
        compute="_compute_wppf_split",
        store=True,
    )
    bwwf_challan_ref = fields.Char(string="BWWF 10% Deposit Challan Ref")
    trustee_board_resolution_ref = fields.Char(string="Board of Trustees Resolution Ref")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("calculated", "Calculated"),
            ("approved", "Trustee Approved"),
            ("posted", "Distributed & Posted"),
        ],
        default="draft",
        required=True,
    )
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", readonly=True, default=lambda self: self.env.user
    )
    calculated_by_id = fields.Many2one("res.users", string="Calculated By", readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(string="Approved On", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "prepared_by_id",
            "calculated_by_id",
            "approved_by_id",
            "approved_on",
            "total_wppf_pool",
            "participatory_fund_amount",
            "welfare_fund_amount",
            "welfare_foundation_amount",
            "equal_distribution_pool",
            "investment_pool_share",
            "per_worker_equal_share",
            "distribution_due_date",
        }

    def _payroll_state_locked_fields(self) -> set:
        # the profit and headcount the pool was calculated from freeze with
        # the calculation (A09 probe W4); the trustee resolution with approval
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {"net_profit", "eligible_workers_count", "fiscal_year"}
            locked |= {"fiscal_year_end_date", "company_id", "currency_id"}
        if self.state in ("approved", "posted"):
            locked |= {"trustee_board_resolution_ref"}
        if self.state == "posted":
            locked |= {"bwwf_challan_ref"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.wppf.allocation")
                    or f"WPPF/{vals.get('fiscal_year') or 'New'}"
                )
        return super().create(vals_list)

    @api.depends("net_profit", "eligible_workers_count", "fiscal_year_end_date")
    def _compute_wppf_split(self):
        from datetime import timedelta

        for rec in self:
            profit = max(float(rec.net_profit or 0.0), 0.0)
            pool = round(profit * 0.05, 2)
            part = round(pool * 0.80, 2)
            welfare = round(pool * 0.10, 2)
            foundation = round(pool - part - welfare, 2)
            cash_pool = round(part * (2.0 / 3.0), 2)
            inv_pool = round(part - cash_pool, 2)
            cnt = int(rec.eligible_workers_count or 0)
            per_worker = round(cash_pool / cnt, 2) if cnt > 0 else 0.0
            rec.total_wppf_pool = pool
            rec.participatory_fund_amount = part
            rec.welfare_fund_amount = welfare
            rec.welfare_foundation_amount = foundation
            rec.equal_distribution_pool = cash_pool
            rec.investment_pool_share = inv_pool
            rec.per_worker_equal_share = per_worker
            if rec.fiscal_year_end_date:
                rec.distribution_due_date = fields.Date.to_date(
                    rec.fiscal_year_end_date
                ) + timedelta(days=270)
            else:
                rec.distribution_due_date = False

    def action_calculate(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Calculate a draft WPPF allocation.")
            if rec.net_profit <= 0:
                raise UserError("Net profit must be positive to compute WPPF 5% allocation.")
            rec = rec._guarded()
            if not rec.eligible_workers_count:
                cnt = self.env["hr.employee"].search_count(
                    [("company_id", "=", rec.company_id.id), ("active", "=", True)]
                )
                rec.write({"eligible_workers_count": max(cnt, 1)})
            rec._compute_wppf_split()
            rec.write({"state": "calculated", "calculated_by_id": self.env.user.id})

    def action_approve(self):
        check_payroll_approver(
            self,
            "a WPPF allocation",
            lambda rec: rec.prepared_by_id | rec.calculated_by_id,
        )
        for rec in self:
            if rec.state != "calculated":
                raise UserError("Calculate WPPF allocation before Trustee Board approval.")
            if not rec.trustee_board_resolution_ref:
                raise UserError(
                    "Board of Trustees resolution reference is required to approve WPPF allocation."
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_on": fields.Datetime.now(),
                }
            )

    def action_post(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Approve WPPF allocation before posting distribution.")
            if not rec.bwwf_challan_ref:
                raise UserError(
                    "BWWF 10% Government Welfare Foundation deposit challan reference is required before posting."
                )
            rec._guarded().write({"state": "posted"})
