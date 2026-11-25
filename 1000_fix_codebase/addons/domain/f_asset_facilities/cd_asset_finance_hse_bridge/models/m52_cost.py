# m52_cost — A07 P1 (2026-11-04), report §6 P1: asset running costs reach M52.
#
# A verified facility work order, a clean fuel fill and a completed vehicle
# service each carry a cost that ended at the outbox: M52 (accounts payable &
# employee expense, cd_ap_ext) never saw it. Each raises ONE cost entry per
# source, by company / branch.
#
# A07 ERP audit (2026-11-20) — "the A07 money contract": the entry is the single
# A07 cost hand-off and it now reaches the GL.
#   * It carries the facts its source states: how it was paid (payment_method),
#     the payee and invoice reference (pinned), the branch operating unit
#     (required, never the company's first), the employee (employee expense)
#     and the employee a cost is recovered from (D9).
#   * Its account comes from the cost type's account role (decision D3:
#     system parameter cd_asset_finance_hse_bridge.account.<cost_type>, with
#     an optional .<subtype>); a rent of a commenced IFRS 16 lease goes to the
#     lease's rent clearing account (D5a). Unset: fail closed.
#   * A vendor bill entry is matched by AP to the payee's bill ON THE SAME
#     BRANCH and to one bill line, whose account becomes the entry's (the bill
#     posts it: fix.vendor.invoice._expense_account below). A rejected bill
#     returns its entries to pending; the source is stamped paid only when the
#     bill is paid (FIN-19, M47-06).
#   * Petty cash, employee expense and fuel card entries post their own entry:
#     Dr the cost account / Cr the branch's petty-cash fund (M50), the
#     employee payable, or the fuel-card clearing account reconciled to the
#     M52 card statement line (M46-03). An internal job (own labour and stock)
#     is recorded, not sent to AP (M47-19).
#   * Budget control (D16): above the remaining M54 budget of the branch and
#     account the entry is HELD until the Branch Operations Lead (facility) or
#     the Logistics Manager (fleet) releases it, plus the CFO when more than
#     BDT 100,000 over. No hard stop.
import logging

from odoo import api, fields, models
from odoo.addons.cd_fixed_asset_ext.models.fix_asset_common import money
from odoo.exceptions import UserError

from .fix_bridge_exception import (
    ACCOUNTANT,
    ACCOUNTING_MANAGER,
    dhaka_today,
    event_source,
    has_role,
    param_float,
    require_role,
    role_account,
)

_logger = logging.getLogger(__name__)

COST_TYPES = [
    ("facility_work_order", "Facility Work Order (M47)"),
    ("vehicle_fuel", "Vehicle Fuel (M46)"),
    ("vehicle_service", "Vehicle Service (M46)"),
    ("site_utility", "Site Utility Bill (M47)"),
    ("lease_rent", "Lease Rent (M47)"),
    ("vehicle_renewal", "Vehicle Document Renewal (M46)"),
    ("vehicle_fine", "Traffic Fine (M46)"),
    ("vehicle_insurance_excess", "Insurance Excess (M46)"),
    ("vehicle_insurance", "Vehicle Insurance Premium (M46)"),
    ("vehicle_lease_rent", "Vehicle Lease Rent (M46)"),
    ("licence_fee", "Licence Fee (M47)"),
    ("calibration_service", "Calibration Service (M45)"),
    ("equipment_service", "Equipment Maintenance (M45)"),
    ("equipment_expensed", "Equipment Below the Capitalisation Floor (M45)"),
    ("deposit", "Security Deposit (M47)"),
    ("advance_rent", "Advance Rent (M47)"),
]
PAYMENT_METHODS = [
    ("vendor_bill", "Vendor Bill (AP)"),
    ("petty_cash", "Petty Cash (Branch Imprest)"),
    ("employee_expense", "Employee Expense (Reimbursed)"),
    ("fuel_card", "Fuel Card"),
    ("internal", "Internal (Own Labour / Stock)"),
]
# what a source may call its payment method
METHOD_ALIASES = {
    "card": "fuel_card",
    "cash": "petty_cash",
    "cash_advance": "employee_expense",
    "expense": "employee_expense",
    "credit_account": "vendor_bill",
    "ap": "vendor_bill",
}
DIRECT_METHODS = ("petty_cash", "employee_expense", "fuel_card")
OPEN_STATES = ("pending", "held")
# R2a (2026-11-21), M47-08: a deposit / advance rent coming back, adjusted
# against dues or written off is a balance-sheet settlement M47 raises as
# "internal" (no new payee). It is not a cost to record and forget: it posts
# its own entry, crediting the deposit / advance account (role <cost type>):
#   refund    Dr the landlord's payable (AP collects the cash) / Cr the account
#   adjusted  Dr the rent clearing (role <type>.adjusted, else the IFRS 16
#             contract's clearing) / Cr the account
#   write_off Dr role <type>.write_off (Others – Provision & Write off) / Cr it
SETTLEMENT_TYPES = ("deposit", "advance_rent")
SETTLEMENT_SUBTYPES = ("refund", "adjusted", "write_off")
# a finer role that never falls back to its cost type's account: a capitalised
# fit-out's cost is CWIP (D1, 100608), never the repair expense
STRICT_SUBTYPES = (("facility_work_order", "fit_out"),)
BRANCH_LEAD = "cd_facility.group_branch_operations_lead"
LOGISTICS_MANAGER = "cd_vehicle_ext.group_logistics_manager"
CFO = "cd_entity_config.group_dofa_tier_4"
# D16: above this many BDT over the remaining budget the CFO releases too.
BUDGET_CFO_PARAM = "budget_cfo_over_bdt"
BUDGET_CFO_DEFAULT = 100000.0
# M47-05: a rent bill that differs from the scheduled rent by more than this is
# held for a Finance Manager. No figure was decided: 0 holds any difference.
RENT_TOLERANCE_PARAM = "rent_variance_tolerance_bdt"
FLEET_TYPES = (
    "vehicle_fuel",
    "vehicle_service",
    "vehicle_renewal",
    "vehicle_fine",
    "vehicle_insurance_excess",
    "vehicle_insurance",
    "vehicle_lease_rent",
)


class FixAssetCostEntry(models.Model):
    _name = "fix.asset.cost.entry"
    _description = "M52 Asset Cost Entry"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, cost_date desc, id desc"

    _key_unique = models.Constraint(
        "UNIQUE (key)", "One M52 cost entry per source document (idempotent hand-off)."
    )

    name = fields.Char(required=True, readonly=True, default="New", copy=False)
    key = fields.Char(required=True, readonly=True, index=True, copy=False)
    cost_type = fields.Selection(COST_TYPES, required=True, readonly=True)
    subtype = fields.Char(
        readonly=True, help="Utility kind, licence kind…: picks a finer account role when set"
    )
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Cost Centre (OU)", index=True, readonly=True
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", readonly=True)
    source_model = fields.Char(required=True, readonly=True)
    source_res_id = fields.Integer(required=True, readonly=True, index=True)
    source_ref = fields.Char(string="Source Document", readonly=True)
    site_id = fields.Many2one("fix.site", string="Site", readonly=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, readonly=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Cost", readonly=True)
    cost_date = fields.Date(string="Cost Date", readonly=True)
    payment_method = fields.Selection(
        PAYMENT_METHODS, required=True, default="vendor_bill", readonly=True, index=True
    )
    account_id = fields.Many2one(
        "account.account",
        string="Cost Account",
        readonly=True,
        help="From the cost type's account role (D3); the bill line or the direct entry posts it",
    )
    vendor_id = fields.Many2one("res.partner", string="Vendor", readonly=True)
    invoice_ref = fields.Char(string="Vendor Invoice Ref", readonly=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee Who Paid", readonly=True, help="Employee expense"
    )
    recovery_employee_id = fields.Many2one(
        "hr.employee",
        string="Recover From Employee",
        readonly=True,
        help="D9: the cost is recharged to this employee once HR approves the recovery",
    )
    card_id = fields.Many2one("fix.expense.card", string="Fuel Card", readonly=True)
    fuel_card_ref = fields.Char(
        string="Fuel Card Ref", readonly=True, help="The card the fill was paid with (M46)"
    )
    card_transaction_id = fields.Many2one(
        "fix.expense.card.transaction", string="Card Statement Line", readonly=True, copy=False
    )
    detail = fields.Char(readonly=True, help="Station / receipt, work type, service type")
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("held", "Held: Over Budget"),
            ("matched", "Matched to Bill"),
            ("posted", "Posted to GL"),
            ("internal", "Internal Cost (No AP)"),
            ("rejected", "Rejected"),
        ],
        default="pending",
        required=True,
        index=True,
        tracking=True,
    )
    source_changed = fields.Boolean(
        readonly=True,
        copy=False,
        help="The source document's cost changed after AP decided this entry",
    )
    vendor_invoice_id = fields.Many2one(
        "fix.vendor.invoice", string="Vendor Bill (M52)", readonly=True, copy=False, index=True
    )
    vendor_invoice_line_id = fields.Many2one(
        "fix.vendor.invoice.line", string="Bill Line", readonly=True, copy=False, index=True
    )
    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True, copy=False)
    component_move_id = fields.Many2one(
        "account.move",
        string="Rent Components Entry",
        readonly=True,
        copy=False,
        help="M47-28/08: the service charge expensed and the advance rent the landlord "
        "adjusted, split out of a rent payment once its bill posts",
    )
    paid_on = fields.Date(string="Paid On", readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    decision_note = fields.Text()
    match_invoice_id = fields.Many2one(
        "fix.vendor.invoice",
        string="Bill to Match",
        copy=False,
        help="Choose the vendor bill, then Match to Bill",
    )
    match_invoice_line_id = fields.Many2one(
        "fix.vendor.invoice.line",
        string="Bill Line to Match",
        copy=False,
        help="The bill line this cost is charged on (needed when the bill has several lines)",
    )
    # D16 budget control
    budget_line_id = fields.Many2one("fix.budget.line", string="Budget Line", readonly=True)
    budget_remaining = fields.Monetary(string="Budget Remaining", readonly=True)
    budget_overrun = fields.Monetary(string="Over Budget By", readonly=True)
    budget_ops_released_by_id = fields.Many2one(
        "res.users", string="Released (Operations)", readonly=True, copy=False
    )
    budget_cfo_released_by_id = fields.Many2one(
        "res.users", string="Released (CFO)", readonly=True, copy=False
    )

    _EDITABLE = frozenset({"decision_note", "match_invoice_id", "match_invoice_line_id"})

    def _fix_guarded_fields(self) -> set:
        # the figures are the source document's; AP decides, it does not retype them
        guarded = super()._fix_guarded_fields() | {
            n
            for n, f in self._fields.items()
            if f.store
            and n not in self._EDITABLE
            and n not in ("id", "create_uid", "create_date", "write_uid", "write_date")
            and not n.startswith(("message_", "activity_"))
            and f.type not in ("one2many", "many2many")
        }
        if any(rec.state not in OPEN_STATES for rec in self):
            guarded |= set(self._EDITABLE)
        return guarded

    def unlink(self):
        if not self.env.su:
            raise UserError("An M52 cost entry is part of the record: reject it instead.")
        return super().unlink()

    # ---- raising ----------------------------------------------------------------
    _REFRESH = (
        "amount",
        "vendor_id",
        "invoice_ref",
        "payment_method",
        "operating_unit_id",
        "branch_id",
        "employee_id",
        "recovery_employee_id",
        "card_id",
        "fuel_card_ref",
        "cost_date",
        "subtype",
        "detail",
    )
    _PINNED = ("amount", "vendor_id", "invoice_ref", "payment_method", "operating_unit_id")

    @api.model
    def _m52_clean_vals(self, vals):
        vals = {k: v for k, v in vals.items() if k in self._fields}
        method = vals.get("payment_method")
        if method in METHOD_ALIASES:
            vals["payment_method"] = METHOD_ALIASES[method]
        if "payment_method" in vals and not vals["payment_method"]:
            del vals["payment_method"]
        if vals.get("payment_method") and vals["payment_method"] not in dict(PAYMENT_METHODS):
            raise UserError("Unknown payment method %s." % vals["payment_method"])
        for name in ("vendor_id", "employee_id", "recovery_employee_id", "card_id"):
            if name in vals and hasattr(vals[name], "id"):
                vals[name] = vals[name].id
        return vals

    def _m52_differs(self, name, value):
        current = self[name]
        if self._fields[name].type == "many2one":
            return (current.id or False) != (value or False)
        if self._fields[name].type in ("float", "monetary"):
            return abs((current or 0.0) - (value or 0.0)) > 0.005
        return (current or False) != (value or False)

    @api.model
    def _m52_queue(self, record, vals):
        key = "m52:%s:%s" % (record._name, record.id)
        vals = self._m52_clean_vals(vals)
        Entry = self.sudo()._guarded()
        existing = Entry.search([("key", "=", key)], limit=1)
        if existing:
            figures = {k: vals[k] for k in self._REFRESH if k in vals}
            changed = {k: v for k, v in figures.items() if existing._m52_differs(k, v)}
            if not changed:
                return existing  # a redelivery, or a re-close with the same figures
            if existing.state in OPEN_STATES:
                pinned = set(changed) & set(self._PINNED)
                if pinned:
                    # a budget release pins the amount and the payee
                    changed.update(
                        budget_ops_released_by_id=False,
                        budget_cfo_released_by_id=False,
                        state="pending",
                    )
                existing.write(changed)
                existing.message_post(body="The source changed: figures refreshed.")
                existing._m52_after_queue()
            else:
                existing.write({"source_changed": True})
                existing.message_post(
                    body="The source changed (%s) after the entry was decided: AP reviews it."
                    % ", ".join(sorted(changed))
                )
            return existing
        vals.setdefault("payment_method", "vendor_bill")
        vals = dict(
            vals,
            key=key,
            source_model=record._name,
            source_res_id=record.id,
            source_ref=record.display_name,
            name=self.env["ir.sequence"].sudo().next_by_code("fix.asset.cost.entry")
            or "M52COST/New",
        )
        entry = Entry.create(vals)
        entry._m52_after_queue()
        return entry

    def _m52_after_queue(self):
        """Resolve the account, check the budget, and send the entry on: an
        internal job is recorded only, a petty-cash / employee / fuel-card cost
        posts its own entry (a failure leaves it pending with the reason), a
        vendor-bill cost waits for AP to match the bill."""
        for rec in self.sudo()._guarded():
            if rec.state not in OPEN_STATES:
                continue
            account = rec._m52_resolve_account(required=False)
            if account != rec.account_id:
                rec.write({"account_id": account.id})
            if rec._m52_is_settlement():
                # a balance-sheet settlement: no budget, its own entry
                try:
                    with self.env.cr.savepoint():
                        rec._m52_post_settlement()
                except UserError as exc:
                    rec.message_post(body="Not posted yet: %s" % exc)
                continue
            if rec.payment_method == "internal":
                rec.write({"state": "internal"})
                rec.message_post(
                    body="Internal job (own labour and stock): recorded for the branch's cost, "
                    "not sent to accounts payable."
                )
                continue
            if not rec._m52_budget_check():
                continue
            if rec.payment_method in DIRECT_METHODS:
                try:
                    with self.env.cr.savepoint():
                        rec._m52_post_direct()
                except UserError as exc:
                    rec.message_post(body="Not posted yet: %s" % exc)
            elif rec.state == "pending" and not rec.message_ids.filtered(
                lambda m: "Pending AP" in (m.body or "")
            ):
                rec.message_post(
                    body="Pending AP: match it to the payee's bill on the same branch when it "
                    "is entered, or reject it with a reason."
                )

    # ---- the account (D3, D5a) ----------------------------------------------------
    def _m52_lease(self):
        """The IFRS 16 contract behind a rent entry, if any."""
        self.ensure_one()
        source = self._m52_source()
        Lease = self.env["fix.lease"].sudo()
        if (
            self.cost_type in ("lease_rent", *SETTLEMENT_TYPES)
            and source
            and "lease_id" in source._fields
            and source.lease_id._name == "fix.site.lease"
        ):
            return Lease.search([("site_lease_id", "=", source.lease_id.id)], limit=1)
        if self.cost_type == "vehicle_lease_rent" and self.vehicle_id and "vehicle_id" in Lease:
            return Lease.search(
                [("vehicle_id", "=", self.vehicle_id.id), ("state", "!=", "ended")], limit=1
            )
        return Lease

    def _m52_is_settlement(self):
        self.ensure_one()
        return (
            self.cost_type in SETTLEMENT_TYPES
            and self.subtype in SETTLEMENT_SUBTYPES
            and self.payment_method == "internal"
        )

    def _m52_settlement_account(self, required=True):
        """The settlement's own account (role <type>.<subtype>): the deposit /
        advance account a refund credits (else the type's), the rent clearing an
        adjustment debits (else the IFRS 16 contract's clearing), the write-off
        account. Never the type's account for an adjustment or a write-off:
        that would debit and credit the same deposit."""
        self.ensure_one()
        company = self.company_id
        key = "%s.%s" % (self.cost_type, self.subtype)
        account = role_account(self.env, company, key)
        if not account and self.subtype == "refund":
            account = role_account(self.env, company, self.cost_type)
        if not account and self.subtype == "adjusted":
            lease = self._m52_lease()
            account = (lease.payment_account_id if lease else None) or role_account(
                self.env, company, "ifrs16_clearing"
            )
        if not account and required:
            role_account(self.env, company, key, required_for="%s (%s)" % (self.name, key))
        return account or self.env["account.account"]

    def _m52_settlement_lines(self, account):
        """(debit account, credit account, partner on the debit) of a settlement."""
        self.ensure_one()
        if self.subtype == "refund":
            from odoo.addons.cd_ap_ext.models.ap_gl import ap_account

            if not self.vendor_id:
                raise UserError(
                    "%s: a refund names the landlord who pays it back (AP collects it)." % self.name
                )
            # the landlord owes the refund: a debit on its payable that AP
            # clears when the money arrives
            return ap_account(self.env, self.company_id, "ap"), account, self.vendor_id
        held = role_account(
            self.env,
            self.company_id,
            self.cost_type,
            required_for="%s (the %s account it settles)" % (self.name, self.cost_type),
        )
        return account, held, self.vendor_id

    def _m52_post_settlement(self):
        """Post a deposit / advance settlement on its branch (M47-08)."""
        from odoo.addons.cd_ap_ext.models.ap_gl import ap_journal, post_ap_move

        self.ensure_one()
        rec = self.sudo()._guarded()
        if rec.state != "pending":
            raise UserError("%s is %s: it does not post." % (rec.name, rec.state))
        rec._m52_require_branch("a deposit settlement")
        account = rec._m52_settlement_account()
        debit, credit, partner = rec._m52_settlement_lines(account)
        if debit == credit:
            raise UserError(
                "%s would debit and credit %s: set the %s.%s account role."
                % (rec.name, debit.code, rec.cost_type, rec.subtype)
            )
        label = "%s %s" % (rec.name, rec.source_ref or "")
        amount = money(rec.amount)
        move = post_ap_move(
            rec.env,
            rec.company_id,
            ap_journal(rec.env, rec.company_id, "purchase"),
            rec.cost_date or dhaka_today(rec.env),
            label,
            [
                (debit, label, amount, 0.0, partner or None),
                (credit, label, 0.0, amount, partner or None),
            ],
            rec.operating_unit_id,
        )
        rec.write(
            {
                "state": "posted",
                "account_id": account.id,
                "move_id": move.id,
                "decided_by_id": self.env.uid,
                "decided_on": fields.Datetime.now(),
            }
        )
        rec.message_post(
            body="Settlement posted %s: Dr %s / Cr %s." % (move.name, debit.code, credit.code)
        )
        return move

    def _m52_resolve_account(self, required=True):
        self.ensure_one()
        what = "%s (%s)" % (self.name, dict(COST_TYPES).get(self.cost_type, self.cost_type))
        if self._m52_is_settlement():
            return self._m52_settlement_account(required=required)
        if self.cost_type in ("lease_rent", "vehicle_lease_rent") and not self.subtype:
            # a subtype (a break penalty) is not the contract's rent: its own role
            lease = self._m52_lease()
            if lease and lease.exemption == "none":
                if lease.state == "active":
                    # D5(a): the IFRS 16 book carries the rent; the bill clears it
                    if not lease.payment_account_id and required:
                        raise UserError(
                            "%s: lease %s has no rent clearing account." % (what, lease.name)
                        )
                    return lease.payment_account_id
                if lease.state == "draft":
                    if required:
                        raise UserError(
                            "%s: IFRS 16 lease %s is not commenced. Finance commences it (or "
                            "marks it exempt) before its rent is billed, so the rent is not "
                            "expensed and then recognised again." % (what, lease.name)
                        )
                    return self.env["account.account"]
        company = self.company_id
        if self.subtype:
            key = "%s.%s" % (self.cost_type, self.subtype)
            account = role_account(self.env, company, key)
            if account:
                return account
            if (self.cost_type, self.subtype) in STRICT_SUBTYPES:
                # capital is never expensed for want of its role
                return role_account(
                    self.env,
                    company,
                    key,
                    required_for="%s (%s)" % (what, key) if required else None,
                )
        return role_account(
            self.env, company, self.cost_type, required_for=what if required else None
        )

    # ---- budget (D16) -------------------------------------------------------------
    def _m52_committed(self, line):
        """Entries on the line's account and branch, in its window, not yet in
        the GL actuals (pending, held or matched)."""
        others = self.sudo().search(
            [
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("account_id", "=", line.account_id.id),
                ("operating_unit_id", "=", self.operating_unit_id.id),
                ("cost_date", ">=", line.date_from),
                ("cost_date", "<=", line.date_to),
                ("state", "in", ("pending", "held", "matched")),
            ]
        )
        return money(sum(others.mapped("amount")))

    def _m52_budget_check(self):
        """True when the entry may go on; False when it is held over budget."""
        self.ensure_one()
        rec = self.sudo()._guarded()
        if "fix.budget.line" not in self.env or not (
            rec.account_id and rec.operating_unit_id and rec.cost_date
        ):
            return True
        Line = self.env["fix.budget.line"].sudo()
        line = Line.search(
            [
                ("company_id", "=", rec.company_id.id),
                ("account_id", "=", rec.account_id.id),
                ("operating_unit_id", "=", rec.operating_unit_id.id),
                ("date_from", "<=", rec.cost_date),
                ("date_to", ">=", rec.cost_date),
                ("budget_id.state", "=", "approved"),
            ],
            limit=1,
        )
        if not line:
            if rec.budget_line_id:
                rec.write({"budget_line_id": False, "budget_remaining": 0.0, "budget_overrun": 0.0})
            return True
        remaining = money(line.planned_amount - line.actual_amount - rec._m52_committed(line))
        overrun = money(rec.amount - remaining) if rec.amount > remaining + 0.005 else 0.0
        rec.write(
            {
                "budget_line_id": line.id,
                "budget_remaining": remaining,
                "budget_overrun": overrun,
            }
        )
        if not overrun or rec._m52_budget_released():
            if rec.state == "held":
                rec.write({"state": "pending"})
            return True
        if rec.state != "held":
            rec.write({"state": "held"})
            rec.message_post(
                body="Held: %.2f is above the remaining %s budget of %.2f by %.2f (D16). %s "
                "releases it%s."
                % (
                    rec.amount,
                    line.account_id.display_name,
                    remaining,
                    overrun,
                    "The Logistics Manager" if rec._m52_is_fleet() else "The Branch Ops Lead",
                    ", and the CFO" if rec._m52_needs_cfo() else "",
                )
            )
        return False

    def _m52_is_fleet(self):
        return bool(self.vehicle_id) or self.cost_type in FLEET_TYPES

    def _m52_needs_cfo(self):
        limit = param_float(self.env, BUDGET_CFO_PARAM, BUDGET_CFO_DEFAULT)
        return self.budget_overrun > limit + 0.005

    def _m52_budget_released(self):
        if not self.budget_ops_released_by_id:
            return False
        return not self._m52_needs_cfo() or bool(self.budget_cfo_released_by_id)

    def action_release_budget(self, note=None):
        """D16: the Branch Operations Lead (facility) or Logistics Manager
        (fleet) releases an over-budget cost; above BDT 100,000 over, the CFO
        too. The person who recorded the cost never releases it."""
        for rec in self:
            if rec.state != "held":
                raise UserError("%s is not held for budget." % rec.name)
            text = (note or rec.decision_note or "").strip()
            if not text:
                raise UserError("Say why %s may exceed the budget (Decision Note)." % rec.name)
            source = rec._m52_source()
            if not self.env.su and source and source.create_uid == self.env.user:
                raise UserError("Segregation of duties: you recorded %s." % rec.source_ref)
            ops_role = LOGISTICS_MANAGER if rec._m52_is_fleet() else BRANCH_LEAD
            vals = {}
            if not rec.budget_ops_released_by_id and has_role(self.env, ops_role):
                vals["budget_ops_released_by_id"] = self.env.uid
            elif (
                rec._m52_needs_cfo()
                and not rec.budget_cfo_released_by_id
                and has_role(self.env, CFO)
            ):
                if rec.budget_ops_released_by_id == self.env.user:
                    raise UserError("The CFO's release is another person's.")
                vals["budget_cfo_released_by_id"] = self.env.uid
            if not vals:
                require_role(
                    self.env,
                    [ops_role] if not rec.budget_ops_released_by_id else [CFO],
                    "Releasing %s over budget" % rec.name,
                )
                raise UserError("%s is already released at your level." % rec.name)
            rec.sudo()._guarded().write(vals)
            rec.message_post(body="Budget release by %s: %s" % (self.env.user.name, text))
            if rec._m52_budget_released():
                rec.sudo()._guarded().write({"state": "pending"})
                rec._m52_after_queue()
        return True

    # ---- direct posting (petty cash, employee expense, fuel card) -----------------
    def _m52_require_branch(self, what):
        if not self.operating_unit_id:
            raise UserError(
                "%s has no branch (operating unit): %s is booked on the source's branch, never "
                "on the company's first one. The source must name its branch." % (self.name, what)
            )

    def _m52_petty_cash_account(self):
        company, ou = self.company_id, self.operating_unit_id
        if "fix.imprest.fund" in self.env:
            fund = (
                self.env["fix.imprest.fund"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("operating_unit_id", "=", ou.id),
                        ("state", "=", "active"),
                    ],
                    limit=1,
                )
            )
            if fund.account_id:
                return fund.account_id
        account = role_account(self.env, company, "petty_cash")
        if not account:
            raise UserError(
                "%s: branch %s has no active petty-cash (imprest) fund in M50 and no "
                "cd_asset_finance_hse_bridge.account.petty_cash is set: nothing posted."
                % (self.name, ou.name)
            )
        return account

    def _m52_card_transaction(self):
        """M46-03: the fuel-card statement line this fill is (card, date,
        amount), read from M52; one fill per line, never a disputed line."""
        if "fix.expense.card.transaction" not in self.env:
            raise UserError("The M52 card statement is not installed.")
        Txn = self.env["fix.expense.card.transaction"].sudo()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("txn_date", "=", self.cost_date),
            ("amount", ">=", self.amount - 0.005),
            ("amount", "<=", self.amount + 0.005),
            ("state", "!=", "disputed"),
            ("card_id.card_type", "=", "fuel"),
        ]
        ref = (self.fuel_card_ref or "").strip()
        if self.card_id:
            domain.append(("card_id", "=", self.card_id.id))
        elif len(ref) >= 4 and ref[-4:].isdigit():
            domain.append(("card_id.last_digits", "=", ref[-4:]))
        elif self.employee_id:
            domain.append(("holder_id", "=", self.employee_id.id))
        else:
            raise UserError("%s names neither the fuel card nor its holder." % self.name)
        used = (
            self.sudo()
            .search([("card_transaction_id", "!=", False), ("id", "!=", self.id)])
            .mapped("card_transaction_id")
        )
        txns = Txn.search(domain) - used
        if not txns:
            raise UserError(
                "%s: no fuel-card statement line of %.2f on %s is in M52 yet (or it is "
                "disputed / already used)." % (self.name, self.amount, self.cost_date)
            )
        if len(txns) > 1:
            raise UserError(
                "%s: %s fuel-card statement lines match (%s): AP decides which by hand."
                % (self.name, len(txns), ", ".join(txns.mapped("name")))
            )
        return txns

    def _m52_post_direct(self):
        """Post Dr the cost account / Cr the paying account, on the branch."""
        from odoo.addons.cd_ap_ext.models.ap_gl import ap_account, ap_journal, post_ap_move

        self.ensure_one()
        rec = self.sudo()._guarded()
        if rec.state != "pending":
            raise UserError("%s is %s: it does not post." % (rec.name, rec.state))
        if rec.payment_method not in DIRECT_METHODS:
            raise UserError("%s is paid by vendor bill: AP matches it to the bill." % rec.name)
        rec._m52_require_branch("a cost")
        account = rec._m52_resolve_account()
        company = rec.company_id
        partner = rec.env["res.partner"]
        txn = None
        if rec.payment_method == "petty_cash":
            credit = rec._m52_petty_cash_account()
        elif rec.payment_method == "employee_expense":
            if not rec.employee_id:
                raise UserError("%s: name the employee who paid." % rec.name)
            employee = rec.employee_id.sudo()
            partner = employee.work_contact_id or employee.user_id.partner_id
            credit = ap_account(rec.env, company, "employee_payable")
        else:
            txn = rec._m52_card_transaction()
            credit = role_account(
                rec.env, company, "fuel_card_clearing", required_for="%s (fuel card)" % rec.name
            )
        label = "%s %s" % (rec.name, rec.source_ref or "")
        move = post_ap_move(
            rec.env,
            company,
            ap_journal(rec.env, company, "purchase"),
            rec.cost_date or dhaka_today(rec.env),
            label,
            [
                (account, label, money(rec.amount), 0.0, rec.vendor_id or None),
                (credit, label, 0.0, money(rec.amount), partner or None),
            ],
            rec.operating_unit_id,
        )
        vals = {
            "state": "posted",
            "account_id": account.id,
            "move_id": move.id,
            "decided_by_id": self.env.uid,
            "decided_on": fields.Datetime.now(),
            "paid_on": move.date,
        }
        if txn:
            vals["card_transaction_id"] = txn.id
        rec.write(vals)
        rec.message_post(body="Posted %s: Dr %s / Cr %s." % (move.name, account.code, credit.code))
        rec._m52_after_posted(move.date, move.name)
        return move

    def action_post_direct(self):
        """AP posts a petty-cash / employee-expense / fuel-card cost once what
        was missing (a fund, a statement line, an account) is there."""
        require_role(self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Posting an M52 cost entry")
        for rec in self:
            source = rec._m52_source()
            if not self.env.su and source and source.create_uid == self.env.user:
                raise UserError("Segregation of duties: you recorded %s." % rec.source_ref)
            if rec._m52_is_settlement():
                rec._m52_post_settlement()
            else:
                rec._m52_post_direct()
        return True

    def _m52_after_posted(self, paid_on, ref):
        """The cost is in the GL: the source is stamped paid where the money
        left (petty cash / employee / card at posting; a bill at its payment),
        and a cost the employee bears becomes a D9 recovery for HR."""
        for rec in self:
            source = rec._m52_source()
            mark_paid = getattr(source, "_m52_mark_paid", None) if source else None
            if mark_paid and rec.payment_method in DIRECT_METHODS:
                mark_paid(rec.amount, paid_on, ref)
            if rec.recovery_employee_id:
                self.env["fix.asset.recovery"].sudo()._recovery_from_cost(rec)
            if rec.cost_type == "lease_rent" and not rec.subtype:
                rec._m52_split_rent_components()

    # ---- a rent payment's components (M47-28, M47-08) -------------------------------
    def _m52_rent_components(self):
        """(service charge, advance adjusted) inside a rent payment's amount."""
        self.ensure_one()
        source = self._m52_source()
        if not source or self.cost_type != "lease_rent" or self.subtype:
            return 0.0, 0.0
        return (
            money(getattr(source, "service_charge_due", 0.0) or 0.0),
            money(getattr(source, "advance_adjusted", 0.0) or 0.0),
        )

    def _m52_split_rent_components(self):
        """The bill posted the payment (rent + service charge - advance the
        landlord adjusted) on the rent account. Split it: the service charge is a
        non-lease component, expensed (role lease_rent.service_charge, else
        lease_rent: Office Rent); the adjusted advance rent is consumed from the
        advance account (role advance_rent). The rent account then carries the
        rent alone, which is what the IFRS 16 book clears. A failure is a visible
        exception, never a failed bill."""
        for rec in self:
            try:
                with self.env.cr.savepoint():
                    rec._m52_post_rent_components()
            except UserError as exc:
                self.env["fix.bridge.exception"].sudo().record(
                    route="m52_cost",
                    key="m52_rent_components:%s" % rec.id,
                    message="Rent %s: the service charge / adjusted advance could not be split "
                    "out of the rent account: %s" % (rec.name, exc),
                    source=rec,
                    role=ACCOUNTANT,
                    company=rec.company_id,
                )

    def _m52_post_rent_components(self):
        from odoo.addons.cd_ap_ext.models.ap_gl import ap_journal, post_ap_move

        self.ensure_one()
        rec = self.sudo()._guarded()
        if rec.component_move_id or not rec.move_id or not rec.account_id:
            return self.env["account.move"]
        service, advance = rec._m52_rent_components()
        company, account, vendor = rec.company_id, rec.account_id, rec.vendor_id or None
        label = "%s %s" % (rec.name, rec.source_ref or "")
        lines = []
        if service > 0.005:
            expense = role_account(self.env, company, "lease_rent.service_charge") or role_account(
                self.env,
                company,
                "lease_rent",
                required_for="%s (the service charge, a non-lease component)" % rec.name,
            )
            if expense != account:
                lines += [
                    (expense, "%s service charge" % label, service, 0.0, vendor),
                    (account, "%s service charge" % label, 0.0, service, vendor),
                ]
        if advance > 0.005:
            held = role_account(
                self.env,
                company,
                "advance_rent",
                required_for="%s (the advance rent the landlord adjusted)" % rec.name,
            )
            lines += [
                (account, "%s advance adjusted" % label, advance, 0.0, vendor),
                (held, "%s advance adjusted" % label, 0.0, advance, vendor),
            ]
        if not lines:
            return self.env["account.move"]
        move = post_ap_move(
            self.env,
            company,
            ap_journal(self.env, company, "purchase"),
            rec.move_id.date,
            "%s components" % label,
            lines,
            rec.operating_unit_id,
        )
        rec.write({"component_move_id": move.id})
        rec.message_post(
            body="Rent components posted %s: service charge %.2f, advance adjusted %.2f."
            % (move.name, service, advance)
        )
        self.env["fix.bridge.exception"].sudo().resolve(
            "m52_rent_components:%s" % rec.id, "posted %s" % move.name
        )
        return move

    def _m52_source(self):
        self.ensure_one()
        if self.source_model not in self.env:
            return None
        return self.env[self.source_model].sudo().browse(self.source_res_id).exists()

    # ---- AP's decision (vendor bill) ----------------------------------------------
    def _m52_bill_line(self, bill, line=None):
        line = line or self.match_invoice_line_id
        if line:
            if line.invoice_id != bill:
                raise UserError("%s is not a line of %s." % (line.description, bill.display_name))
            return line
        lines = bill.line_ids
        if len(lines) == 1:
            return lines
        free = lines.filtered(
            lambda ln: not ln.asset_cost_entry_ids and abs(ln.line_total - self.amount) <= 0.005
        )
        if len(free) == 1:
            return free
        raise UserError(
            "%s has %s lines: choose the line %s is charged on (Bill Line to Match)."
            % (bill.display_name, len(lines), self.name)
        )

    def action_match_bill(self, vendor_invoice_id=None, accept_variance=False):
        """Match the entry to the payee's bill: same company and branch, not
        rejected, the source's vendor and invoice reference, one bill line
        that the entry's account then posts. Entries on a line never exceed
        it, nor the bill's gross."""
        require_role(self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Matching an M52 cost entry")
        for rec in self:
            bill = (
                self.env["fix.vendor.invoice"].browse(int(vendor_invoice_id)).exists()
                if vendor_invoice_id
                else rec.match_invoice_id
            )
            if not bill:
                raise UserError("Choose the vendor bill %s is charged on." % rec.name)
            if rec.state == "held":
                raise UserError("%s is held over budget: it is released first." % rec.name)
            if rec.state != "pending":
                raise UserError("%s is already decided." % rec.name)
            if rec.payment_method != "vendor_bill":
                raise UserError(
                    "%s was paid by %s, not by a vendor bill: it posts its own entry "
                    "(Post)." % (rec.name, dict(PAYMENT_METHODS)[rec.payment_method])
                )
            if bill.company_id != rec.company_id:
                raise UserError("%s belongs to another company." % bill.display_name)
            if bill.approval_state == "rejected":
                raise UserError("%s is rejected: match a live bill." % bill.display_name)
            if not rec.vendor_id:
                raise UserError(
                    "%s names no vendor: a bill is matched only to the payee its source "
                    "names. The source records the vendor first." % rec.source_ref
                )
            if bill.vendor_id.commercial_partner_id != rec.vendor_id.commercial_partner_id:
                raise UserError(
                    "%s is from %s, but %s's vendor is %s."
                    % (bill.display_name, bill.vendor_id.name, rec.source_ref, rec.vendor_id.name)
                )
            if rec.invoice_ref and (bill.invoice_ref or "").strip().upper() != (
                rec.invoice_ref.strip().upper()
            ):
                raise UserError(
                    "%s is invoice %s, but %s names invoice %s."
                    % (bill.display_name, bill.invoice_ref, rec.source_ref, rec.invoice_ref)
                )
            rec._m52_require_branch("the bill")
            if bill.operating_unit_id != rec.operating_unit_id:
                raise UserError(
                    "%s is booked on %s, but %s is the cost of %s: the bill is entered on the "
                    "source's branch (BRU-FAC-20)."
                    % (
                        bill.display_name,
                        bill.operating_unit_id.name,
                        rec.source_ref,
                        rec.operating_unit_id.name,
                    )
                )
            if (
                bill.requisition_id
                and "capex_request_id" in bill.requisition_id._fields
                and (bill.requisition_id.sudo().capex_request_id)
            ):
                raise UserError(
                    "%s is a capital bill (CWIP): not a running cost." % bill.display_name
                )
            account = rec._m52_resolve_account()
            line = rec._m52_bill_line(bill)
            on_line = (
                line.asset_cost_entry_ids.filtered(lambda e: e.state in ("matched", "posted")) - rec
            )
            if on_line.account_id - account:
                raise UserError(
                    "%s already carries a cost on %s: one bill line, one account."
                    % (line.description, ", ".join(on_line.account_id.mapped("code")))
                )
            if sum(on_line.mapped("amount")) + rec.amount > line.line_total + 0.005:
                raise UserError(
                    "%s: the cost entries on line %s would total %.2f, above the line's %.2f."
                    % (
                        rec.name,
                        line.description,
                        sum(on_line.mapped("amount")) + rec.amount,
                        line.line_total,
                    )
                )
            matched = (
                self.sudo().search(
                    [("vendor_invoice_id", "=", bill.id), ("state", "in", ("matched", "posted"))]
                )
                - rec
            )
            total = sum(matched.mapped("amount")) + rec.amount
            if total > (bill.gross_amount or 0.0) + 0.005:
                raise UserError(
                    "%s: the cost entries matched to %s would total %.2f, above the bill's "
                    "%.2f." % (rec.name, bill.display_name, total, bill.gross_amount or 0.0)
                )
            if rec.cost_type == "lease_rent" and not rec.subtype and not on_line:
                # M47-05: the landlord's bill against the scheduled rent
                tolerance = param_float(self.env, RENT_TOLERANCE_PARAM, 0.0)
                variance = money(line.line_total - rec.amount)
                if abs(variance) > tolerance + 0.005:
                    if not accept_variance:
                        raise UserError(
                            "%s bills %.2f for %s, the schedule says %.2f (variance %.2f): a "
                            "Finance Manager accepts the variance (Accept Variance) with a note."
                            % (
                                bill.display_name,
                                line.line_total,
                                rec.source_ref,
                                rec.amount,
                                variance,
                            )
                        )
                    require_role(self.env, [ACCOUNTING_MANAGER], "Accepting a rent variance")
                    if not (rec.decision_note or "").strip():
                        raise UserError("Say why the rent variance is accepted (Decision Note).")
            if bill.move_id:
                posted = bill.move_id.sudo().line_ids.filtered(
                    lambda ml, a=account: ml.account_id == a and ml.debit
                )
                if not posted:
                    raise UserError(
                        "%s is already posted, and not on %s: AP reclassifies it before the "
                        "match." % (bill.display_name, account.display_name)
                    )
            source = rec._m52_source()
            refusal = getattr(source, "_m52_match_refusal", None)
            why = refusal() if refusal else None
            if why:
                raise UserError(why)
            rec.sudo()._guarded().write(
                {
                    "state": "posted" if bill.move_id else "matched",
                    "account_id": account.id,
                    "vendor_invoice_id": bill.id,
                    "vendor_invoice_line_id": line.id,
                    "move_id": bill.move_id.id,
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Matched to vendor bill %s, line %s (%s)."
                % (bill.display_name, line.description, account.code)
            )
            mark_billed = getattr(source, "_m52_mark_billed", None) if source else None
            if mark_billed:
                mark_billed(bill.invoice_date, bill.invoice_ref)
            if bill.move_id:
                rec._m52_after_posted(bill.move_id.date, bill.move_id.name)
                if bill.payment_state == "paid":
                    rec._m52_bill_paid(bill)
        return True

    def action_accept_variance(self):
        """M47-05: a Finance Manager matches a rent bill that differs from the
        schedule, with the reason in the decision note."""
        return self.action_match_bill(accept_variance=True)

    def _m52_bill_paid(self, bill):
        """The bill is paid: the source's payment stamp (FIN-19)."""
        today = dhaka_today(self.env)
        for rec in self.filtered(lambda e: e.state in ("matched", "posted") and not e.paid_on):
            line = rec.vendor_invoice_line_id
            alone = line and len(line.asset_cost_entry_ids) == 1
            amount = line.line_total if alone else rec.amount
            rec.sudo()._guarded().write({"paid_on": today})
            source = rec._m52_source()
            mark_paid = getattr(source, "_m52_mark_paid", None) if source else None
            if mark_paid:
                mark_paid(amount, today, bill.invoice_ref)

    def _m52_bill_reopened(self, bill, why):
        """M47-06: the bill was rejected: its entries go back to pending."""
        for rec in self:
            rec.sudo()._guarded().write(
                {
                    "state": "pending",
                    "vendor_invoice_id": False,
                    "vendor_invoice_line_id": False,
                    "move_id": False,
                    "match_invoice_id": False,
                    "match_invoice_line_id": False,
                    "decided_by_id": False,
                    "decided_on": False,
                }
            )
            rec.message_post(body="Back to pending: bill %s %s." % (bill.display_name, why))
            source = rec._m52_source()
            unmark = getattr(source, "_m52_mark_unbilled", None) if source else None
            if unmark:
                unmark()

    def action_reject(self, reason=None):
        require_role(self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Rejecting an M52 cost entry")
        for rec in self:
            if rec.state not in OPEN_STATES:
                raise UserError("%s is already decided." % rec.name)
            note = (reason or rec.decision_note or "").strip()
            if not note:
                raise UserError("Say why %s is rejected (Decision Note)." % rec.name)
            rec.sudo()._guarded().write(
                {
                    "state": "rejected",
                    "decision_note": note,
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Rejected: %s" % note)
        return True

    # ---- the consumers --------------------------------------------------------------
    @api.model
    def consume_facility_work_order_closed(self, event):
        """facility.work_order_closed (M47, branch-verified) -> a cost entry.
        M47-19: only a vendor job goes to AP; an internal job (own labour and
        M15 stock) is recorded as the branch's cost, never a payable."""
        order = event_source(self.env, event, "fix.facility.work.order")
        payload = event.get("payload") or {}
        cost = float(payload.get("cost") or 0.0)
        if not order or cost <= 0.0:
            return False
        site = order.site_id
        vendor_job = (payload.get("assigned_type") or "vendor") == "vendor"
        verified = payload.get("verified_at")
        vals = {
            "cost_type": "facility_work_order",
            "company_id": int(payload.get("company_id") or order.company_id.id),
            "operating_unit_id": (site.operating_unit_id or site.branch_id.operating_unit_id).id,
            "branch_id": site.branch_id.id,
            "site_id": site.id,
            "amount": cost,
            "cost_date": fields.Date.context_today(
                self.with_context(tz="Asia/Dhaka"), fields.Datetime.to_datetime(verified)
            )
            if verified
            else dhaka_today(self.env),
            "vendor_id": int(payload["vendor_id"]) if payload.get("vendor_id") else False,
            "invoice_ref": payload.get("invoice_ref") or False,
            "payment_method": "vendor_bill" if vendor_job else "internal",
            "detail": "%s / %s"
            % (payload.get("work_type") or "-", payload.get("assigned_type") or "-"),
        }
        # R2a: the facts M47 states (M47-13/19/23/35) win over what the bridge
        # derives: the payment method, the cost centre (a vehicle's job is the
        # vehicle's unit), the Dhaka cost date, the vehicle.
        for name in ("payment_method", "operating_unit_id", "vehicle_id"):
            if payload.get(name):
                vals[name] = int(payload[name]) if name.endswith("_id") else payload[name]
        if payload.get("cost_date"):
            vals["cost_date"] = fields.Date.to_date(payload["cost_date"])
        facts = getattr(order, "_m52_cost_facts", None)
        if facts:
            # what the event (published at verification) states wins; the
            # order's own facts fill only what it does not say
            for name, value in facts().items():
                if value not in (None, False) and not vals.get(name):
                    vals[name] = value
        return self._m52_queue(order, vals)

    @api.model
    def _m52_vehicle_vals(self, vehicle):
        vehicle = vehicle.sudo()
        return {
            "company_id": (vehicle.company_id or self.env.company).id,
            "operating_unit_id": (
                vehicle.operating_unit_id or vehicle.branch_id.operating_unit_id
            ).id,
            "branch_id": vehicle.branch_id.id,
            "vehicle_id": vehicle.id,
        }

    @api.model
    def consume_vehicle_fuel_recorded(self, event):
        """vehicle.fuel_recorded (M46, a fill with no open exception) -> a cost entry.
        The entry reads the fill as it stands, not the event: the recorder may
        have corrected it before the relay ran."""
        fuel = event_source(self.env, event, "fix.vehicle.fuel")
        if not fuel or (fuel.amount or 0.0) <= 0.0 or fuel.review_state not in ("none", "cleared"):
            return False
        vals = self._m52_vehicle_vals(fuel.vehicle_id)
        vals.update({"cost_type": "vehicle_fuel", **self._m52_fuel_figures(fuel)})
        return self._m52_queue(fuel, vals)

    @api.model
    def _m52_fuel_figures(self, fuel):
        """The fill's own facts: amount, date, receipt, and (M46-03) how it was
        paid, the station that bills it, the card and the employee."""
        driver = getattr(fuel, "driver_id", None)
        employee = getattr(fuel, "employee_id", None) or (
            driver.employee_id if driver and "employee_id" in driver._fields else None
        )
        station = getattr(fuel, "station_partner_id", None) or getattr(fuel, "vendor_id", None)
        figures = {
            "amount": fuel.amount,
            "cost_date": fuel.filled_on,
            "invoice_ref": fuel.receipt_no or False,
            "detail": "%s L at %s, receipt %s"
            % (fuel.litres, fuel.station or "-", fuel.receipt_no or "-"),
        }
        method = getattr(fuel, "payment_method", None)
        if method:
            figures["payment_method"] = METHOD_ALIASES.get(method, method)
        if station:
            figures["vendor_id"] = station.id
        if employee:
            figures["employee_id"] = employee.id
        card = getattr(fuel, "card_id", None)
        if card:
            figures["card_id"] = card.id
        facts = getattr(fuel, "_m52_cost_facts", None)
        if facts:
            # M46 money contract: its own facts win (branch OU, payment method,
            # station, the employee who paid, the fuel card)
            figures.update({k: v for k, v in facts().items() if v is not None})
        return figures

    @api.model
    def consume_vehicle_service_completed(self, event):
        """vehicle.service_completed (M46 PM done) -> a cost entry on the
        garage that did it and its invoice (M46-02)."""
        pm = event_source(self.env, event, "fix.vehicle.pm")
        payload = event.get("payload") or {}
        cost = float(payload.get("cost") or 0.0)
        if not pm or cost <= 0.0:
            return False
        # A service done through a work order of the one work-order spine
        # (cd_asset_workorder_spine links the WO to the PM) is charged once:
        # the WO's facility.work_order_closed entry carries the vendor and the
        # invoice reference AP matches on, so the PM adds no second entry.
        WO = self.env["fix.facility.work.order"].sudo()
        if "vehicle_pm_id" in WO._fields and WO.search_count([("vehicle_pm_id", "=", pm.id)]):
            return False
        provider = getattr(pm, "provider_id", None)
        method = getattr(pm, "payment_method", None)
        vals = self._m52_vehicle_vals(pm.vehicle_id)
        facts = getattr(pm, "_m52_cost_facts", None)
        facts = facts() if facts else {}
        vals.update(
            {
                "cost_type": "vehicle_service",
                "amount": cost,
                "cost_date": fields.Date.to_date(payload.get("done_on")) or pm.done_on,
                "vendor_id": provider.id if provider else False,
                "invoice_ref": (getattr(pm, "invoice_ref", None) or "").strip() or False,
                "payment_method": METHOD_ALIASES.get(method, method)
                or ("vendor_bill" if provider else "internal"),
                "detail": "%s service at %s km"
                % (payload.get("pm_type") or "-", payload.get("odometer") or 0),
            }
        )
        vals.update({k: v for k, v in facts.items() if v is not None})
        return self._m52_queue(pm, vals)

    @api.model
    def _m52_site_vals(self, site):
        site = site.sudo()
        return {
            "company_id": (site.company_id or self.env.company).id,
            "operating_unit_id": (site.operating_unit_id or site.branch_id.operating_unit_id).id,
            "branch_id": site.branch_id.id,
            "site_id": site.id,
        }

    @api.model
    def consume_site_utility_payable(self, event):
        """site.utility_payable (M47: a bill not held, or released after review)
        -> a cost entry on the utility account's provider (M47-12), dated the
        last day of the billed month, on the account of its utility kind."""
        bill = event_source(self.env, event, "fix.site.utility")
        payload = event.get("payload") or {}
        amount = float(payload.get("amount") or 0.0)
        if not bill or amount <= 0.0:
            return False
        account = getattr(bill, "account_id", None)
        provider = getattr(account, "provider_id", None) if account else None
        provider = (
            provider or getattr(bill, "provider_id", None) or getattr(bill, "vendor_id", None)
        )
        cost_date = dhaka_today(self.env)
        try:
            year, month = (int(x) for x in (bill.period or "").split("-")[:2])
            cost_date = fields.Date.end_of(
                fields.Date.to_date("%04d-%02d-01" % (year, month)), "month"
            )
        except (TypeError, ValueError):
            pass
        vals = self._m52_site_vals(bill.site_id)
        vals.update(
            {
                "cost_type": "site_utility",
                "subtype": bill.utility_type or False,
                "amount": amount,
                "currency_id": bill.currency_id.id,
                "cost_date": cost_date,
                "vendor_id": provider.id if provider else False,
                "invoice_ref": (getattr(bill, "invoice_ref", None) or "").strip() or False,
                "detail": "%s %s" % (bill.utility_type, bill.period),
            }
        )
        if payload.get("operating_unit_id"):
            vals["operating_unit_id"] = int(payload["operating_unit_id"])
        facts = getattr(bill, "_utility_m52_vals", None)
        if facts:
            # R2a: M47's own facts (the supply account's provider, the cost
            # centre, the period end) win; a bill that cannot state them keeps
            # what the event and the site say
            try:
                with self.env.cr.savepoint():
                    stated = facts()
            except UserError:
                stated = {}
            vals.update({k: v for k, v in stated.items() if v not in (None, False)})
            vals["amount"] = amount
        return self._m52_queue(bill, vals)

    @api.model
    def consume_lease_rent_payment_requested(self, event):
        """lease.rent_payment_requested (M47: a rent row sent to AP) -> a cost
        entry on the landlord, matched only to the landlord's bill. Its account
        is the lease's IFRS 16 rent clearing once the lease is commenced (D5a)."""
        row = event_source(self.env, event, "fix.site.lease.schedule")
        payload = event.get("payload") or {}
        amount = float(payload.get("amount") or 0.0)
        if not row or amount <= 0.0:
            return False
        vals = self._m52_site_vals(row.site_id)
        vals.update(
            {
                "cost_type": "lease_rent",
                "amount": amount,
                "currency_id": row.currency_id.id,
                "cost_date": row.due_date,
                "vendor_id": row.lease_id.lessor_id.id,
                "detail": "Rent %s, lease %s" % (row.period, row.lease_id.name),
            }
        )
        if payload.get("operating_unit_id"):
            vals["operating_unit_id"] = int(payload["operating_unit_id"])
        facts = getattr(row, "_schedule_m52_vals", None)
        if facts:
            # R2a (M47-28/08): the payment is rent + service charge - the advance
            # the landlord adjusted; the split is posted once the bill posts
            try:
                with self.env.cr.savepoint():
                    stated = facts()
            except UserError:
                stated = {}
            vals.update({k: v for k, v in stated.items() if v not in (None, False)})
            vals["amount"] = amount
        return self._m52_queue(row, vals)


class FixVendorInvoiceLineM52(models.Model):
    _inherit = "fix.vendor.invoice.line"

    asset_cost_entry_ids = fields.One2many(
        "fix.asset.cost.entry", "vendor_invoice_line_id", string="A07 Cost Entries", readonly=True
    )


class FixVendorInvoiceM52(models.Model):
    _inherit = "fix.vendor.invoice"

    def _m52_entries(self, states=("matched", "posted")):
        return (
            self.env["fix.asset.cost.entry"]
            .sudo()
            .search([("vendor_invoice_id", "in", self.ids), ("state", "in", states)])
        )

    def _expense_account(self, line):
        """The money contract: a bill line that carries A07 cost entries posts
        on their account (D3; a commenced lease's rent on its clearing, D5a)."""
        entries = line.sudo().asset_cost_entry_ids.filtered(
            lambda e: e.state in ("matched", "posted")
        )
        accounts = entries.mapped("account_id")
        if len(accounts) > 1:
            raise UserError(
                "Bill line %s carries costs on several accounts (%s): split the line."
                % (line.description, ", ".join(accounts.mapped("code")))
            )
        if accounts:
            return accounts
        return super()._expense_account(line)

    def _post_approved_bill(self):
        entries = self._m52_entries(("matched",))
        for entry in entries:
            if entry.operating_unit_id != self.operating_unit_id:
                raise UserError(
                    "Bill %s is now on %s, but its cost %s is %s's: the bill stays on the "
                    "branch of the cost it was matched to."
                    % (
                        self.invoice_ref,
                        self.operating_unit_id.name,
                        entry.name,
                        entry.operating_unit_id.name,
                    )
                )
        result = super()._post_approved_bill()
        if entries and self.move_id:
            entries._guarded().write({"state": "posted", "move_id": self.move_id.id})
            entries._m52_after_posted(self.move_id.date, self.move_id.name)
        return result

    def action_reject(self):
        result = super().action_reject()
        for bill in self.filtered(lambda b: b.approval_state == "rejected"):
            bill._m52_entries(("matched",))._m52_bill_reopened(bill, "was rejected")
        return result

    def write(self, vals):
        paying = self.browse()
        if vals.get("payment_state") == "paid":
            paying = self.filtered(lambda b: b.payment_state != "paid")
        result = super().write(vals)
        for bill in paying:
            bill._m52_entries()._m52_bill_paid(bill)
        return result


class FixVehicleFuelM52(models.Model):
    _inherit = "fix.vehicle.fuel"

    # What the M52 cost entry of a fill carries.
    _M52_FIELDS = frozenset({"amount", "filled_on", "receipt_no", "litres", "station"})

    def _m52_entry(self):
        self.ensure_one()
        return (
            self.env["fix.asset.cost.entry"]
            .sudo()
            .search([("source_model", "=", self._name), ("source_res_id", "=", self.id)], limit=1)
        )

    def write(self, vals):
        """A recorder's correction after the fill reached M52. A pending entry
        follows the fill; a corrected fill that is now held for review has no
        accepted cost, so its pending entry goes until the review clears it
        (which raises it again). Once AP has decided, the figure is theirs."""
        touched = self._M52_FIELDS & set(vals)
        if touched and not self.env.su:
            for rec in self:
                entry = rec._m52_entry()
                if (
                    entry
                    and entry.state not in OPEN_STATES
                    and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in touched)
                ):
                    raise UserError(
                        "Accounts payable has already decided the cost entry of %s (%s): "
                        "ask them before correcting this fill." % (rec.name, entry.name)
                    )
        res = super().write(vals)
        if touched:
            Entry = self.env["fix.asset.cost.entry"].sudo()
            for rec in self:
                entry = rec._m52_entry()
                if not entry or entry.state not in OPEN_STATES:
                    continue
                if rec.review_state == "held":
                    entry.unlink()
                    continue
                figures = Entry._m52_fuel_figures(rec.sudo())
                Entry._m52_queue(rec, dict(Entry._m52_vehicle_vals(rec.vehicle_id), **figures))
        return res
