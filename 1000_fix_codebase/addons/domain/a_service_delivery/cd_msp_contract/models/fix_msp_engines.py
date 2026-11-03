# fix_msp_engines — M05 iteration 2: the compliance engines the module
# charter names (runbooks, patching, SLA credits, on-call rota, maintenance
# windows, problem & change) plus the estate polish the workspace screens
# showed missing on 2026-10-26 (asset display names, health scoring, SLA %
# display, contract SLA target).
#
# FILE NAME IS LOAD-BEARING: fix_msp < fix_msp_engines < fix_msp_ext keeps
# the alphabetical import order in models/__init__.py correct.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Domain

from libs.py.fix_events import publish

from .msp_roles import (
    GROUP_CAB,
    GROUP_CHANGE_MANAGER,
    GROUP_CREDIT_APPROVER,
    GROUP_ENGINEER,
    has_any,
    require_other_person,
    require_role,
)

# ---------------------------------------------------------------- runbooks


class FixMspRunbook(models.Model):
    """A remediation runbook: the steps an operator (or a future automation
    agent) runs against an unhealthy asset. Executions are RECORDED —
    action_execute logs a run; it never pretends the platform itself ran
    a script on the device."""

    _name = "fix.msp.runbook"
    _description = "MSP Runbook"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    trigger = fields.Selection(
        [
            ("manual", "Manual"),
            ("alert_major", "Major Alert"),
            ("asset_offline", "Asset Offline"),
            ("health_degraded", "Health Degraded"),
        ],
        default="manual",
        required=True,
        help="When this runbook applies; auto_run books it for the on-call "
        "technician when the condition fires",
    )
    scope_contract_id = fields.Many2one(
        "fix.msp.contract", string="Scoped To Contract", help="Empty = every contract"
    )
    script = fields.Text(required=True, string="Remediation Steps")
    auto_run = fields.Boolean(
        string="Auto-Run", default=False, help="Booked automatically when the trigger fires"
    )
    auto_resolve_alert = fields.Boolean(
        string="Resolve Alert on Success",
        default=False,
        help="A successful execution resolves the asset's open alert with a note",
    )
    active = fields.Boolean(default=True)
    run_ids = fields.One2many("fix.msp.runbook.run", "runbook_id", string="Executions")
    run_count = fields.Integer(compute="_compute_run_stats", string="Executions")
    last_run_at = fields.Datetime(compute="_compute_run_stats", string="Last Execution")

    @api.depends("run_ids.finished_at")
    def _compute_run_stats(self):
        for book in self:
            book.run_count = len(book.run_ids)
            book.last_run_at = max(
                (r.finished_at or r.started_at for r in book.run_ids), default=False
            )

    def action_execute(self, asset=None, alert_id=None):
        """Record an execution of this runbook against an asset. ``asset``
        accepts an asset id or an agent identifier (the workspace prompt
        sends free text). The run is created and finished in one call —
        the operator clicks AFTER performing the steps; optionally the
        asset's open alert is resolved with a note."""
        for book in self:
            if not book.active:
                raise UserError("Runbook %s is archived — reactivate it first" % book.name)
            Asset = self.env["fix.monitored.asset"]
            if isinstance(asset, str) and asset.strip():
                target = Asset.search(
                    ["|", ("agent_id", "=", asset.strip()), ("hostname", "=", asset.strip())],
                    limit=1,
                )
                if not target:
                    raise UserError("No monitored asset matches '%s'" % asset)
            elif isinstance(asset, int) and asset:
                target = Asset.browse(asset)
                if not target.exists():
                    raise UserError("Monitored asset %s does not exist" % asset)
            else:
                domain = (
                    [("msp_contract_id", "=", book.scope_contract_id.id)]
                    if book.scope_contract_id
                    else []
                )
                target = Asset.search(domain, limit=1)
                if not target:
                    raise UserError("No monitored asset in scope — name one explicitly")
            alert = None
            if alert_id:
                alert = self.env["fix.msp.alert"].browse(int(alert_id)).exists()
            run = (
                self.env["fix.msp.runbook.run"]
                ._guarded()
                .create(
                    {
                        "runbook_id": book.id,
                        "asset_id": target.id,
                        "alert_id": alert.id if alert else False,
                        "state": "success",
                        "started_at": fields.Datetime.now(),
                        "finished_at": fields.Datetime.now(),
                        "output_note": "Executed via workspace/ops console",
                    }
                )
            )
            if book.auto_resolve_alert and not alert:
                alert = self.env["fix.msp.alert"].search(
                    [
                        ("asset_id", "=", target.id),
                        ("state", "in", ("new", "acked", "ticketed")),
                    ],
                    limit=1,
                )
            if book.auto_resolve_alert and alert and alert.state != "resolved":
                alert.action_resolve(note="Runbook '%s' executed (run #%s)" % (book.name, run.id))
            publish(
                self.env,
                "msp.runbook_executed",
                "fix.msp.runbook.run",
                run.id,
                {"runbook": book.name, "asset": target.agent_id},
            )
        return True


class FixMspRunbookRun(models.Model):
    """One recorded execution of a runbook (accountability log)."""

    _name = "fix.msp.runbook.run"
    _description = "MSP Runbook Execution"
    _inherit = ["fix.guarded.mixin"]
    _order = "started_at desc"

    def _fix_guarded_fields(self) -> set:
        # A02 audit M05-3: the run log is accountability evidence; its outcome
        # and timing are written by action_execute / action_finish only.
        return super()._fix_guarded_fields() | {"state", "started_at", "finished_at"}

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    runbook_id = fields.Many2one("fix.msp.runbook", required=True, ondelete="cascade")
    asset_id = fields.Many2one("fix.monitored.asset", required=True)
    alert_id = fields.Many2one("fix.msp.alert", string="Alert", ondelete="set null")
    state = fields.Selection(
        [("running", "Running"), ("success", "Success"), ("failed", "Failed")],
        default="running",
        required=True,
    )
    started_at = fields.Datetime(default=fields.Datetime.now, required=True)
    finished_at = fields.Datetime(readonly=True)
    output_note = fields.Char(string="Output / Note")

    def action_finish(self, note="", ok=True):
        """Close a running execution with the operator's outcome."""
        for run in self:
            if run.state != "running":
                raise UserError("Execution %s already finished (%s)" % (run.id, run.state))
            run._guarded().write(
                {
                    "state": (ok and "success") or "failed",
                    "finished_at": fields.Datetime.now(),
                    "output_note": note or run.output_note,
                }
            )


# -------------------------------------------------------------- patching


class FixMspPatchPolicy(models.Model):
    """How patches behave for a contract (or globally when no contract)."""

    _name = "fix.msp.patch.policy"
    _description = "MSP Patch Policy"
    _inherit = ["fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", string="Scoped To Contract", help="Empty = estate-wide default"
    )
    category = fields.Selection(
        [("os", "OS"), ("third_party", "Third-Party"), ("firmware", "Firmware")],
        default="os",
        required=True,
    )
    auto_approve = fields.Boolean(
        default=False,
        help="Missing updates are pre-approved without a review step - only once a CAB "
        "member or the change manager approved this policy, and never for a critical "
        "patch unless a CAB member approved it",
    )
    max_defer_days = fields.Integer(default=7, string="Max Defer Days")
    active = fields.Boolean(default=True)
    # A02 audit M05-6 (probe P3): any user's auto-approve policy pre-approved a
    # critical patch. The policy itself is now a CAB / change-manager decision.
    approved_by_id = fields.Many2one(
        "res.users", string="Policy Approved By", readonly=True, copy=False
    )
    approved_at = fields.Datetime(string="Policy Approved At", readonly=True, copy=False)
    approved_by_cab = fields.Boolean(
        string="Approved by a CAB Member",
        readonly=True,
        copy=False,
        help="Only a policy a CAB member approved may auto-approve critical patches",
    )

    # Changing what the policy covers withdraws its approval.
    _POLICY_TERMS = {"auto_approve", "category", "msp_contract_id", "active", "company_id"}

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"approved_by_id", "approved_at", "approved_by_cab"}

    def write(self, vals):
        terms = self._POLICY_TERMS & set(vals)
        voided = self.browse()
        if terms and not self._fix_guard_open():
            voided = self.filtered(
                lambda p: p.id
                and p.approved_at
                and any(p._fix_guard_differs(n, vals[n], p[n]) for n in terms)
            )
        result = super().write(vals)
        if voided:
            voided._guarded().write(
                {"approved_by_id": False, "approved_at": False, "approved_by_cab": False}
            )
        return result

    def action_approve(self):
        """A CAB member or the change manager approves the policy; never the
        person who wrote it."""
        for policy in self:
            require_role(self.env, [GROUP_CAB, GROUP_CHANGE_MANAGER], "Approving a patch policy")
            require_other_person(self.env, policy.create_uid, "Approving a patch policy")
            policy._guarded().write(
                {
                    "approved_by_id": self.env.user.id,
                    "approved_at": fields.Datetime.now(),
                    "approved_by_cab": has_any(self.env, [GROUP_CAB]),
                }
            )
        return True


class FixMspPatchUpdate(models.Model):
    """A patch an asset needs — the compliance register's atom."""

    _name = "fix.msp.patch.update"
    _description = "MSP Patch Update"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one("fix.msp.contract", required=True, index=True)
    asset_id = fields.Many2one("fix.monitored.asset", required=True, index=True)
    identifier = fields.Char(string="Patch ID", help="e.g. KB5034441, chrome-128")
    title = fields.Char(required=True)
    severity = fields.Selection(
        [("critical", "Critical"), ("high", "High"), ("medium", "Medium"), ("low", "Low")],
        default="medium",
        required=True,
    )
    category = fields.Selection(
        [("os", "OS"), ("third_party", "Third-Party"), ("firmware", "Firmware")],
        default="os",
        required=True,
    )
    state = fields.Selection(
        [
            ("missing", "Missing"),
            ("approved", "Approved"),
            ("installed", "Installed"),
            ("failed", "Failed"),
            ("deferred", "Deferred"),
        ],
        default="missing",
        required=True,
        tracking=True,
    )
    approved_date = fields.Date(readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    auto_approved_policy_id = fields.Many2one(
        "fix.msp.patch.policy", string="Auto-Approved By Policy", readonly=True, copy=False
    )
    installed_at = fields.Datetime(readonly=True)
    deferred_until = fields.Date(readonly=True)
    fail_note = fields.Char(string="Failure Note", copy=False, readonly=True)

    # Odoo 19: models.Constraint replaces the legacy _sql_constraints list
    _asset_patch_unique = models.Constraint(
        "UNIQUE (asset_id, identifier)", "This patch is already tracked for the asset"
    )

    def _fix_guarded_fields(self) -> set:
        # A02 audit M05-3 / M05-6 (probe P2): /p03/model/write set a patch
        # 'installed' with no approval and no install time.
        return super()._fix_guarded_fields() | {
            "state",
            "approved_date",
            "approved_by_id",
            "auto_approved_policy_id",
            "installed_at",
            "deferred_until",
            "fail_note",
        }

    def _auto_approving_policy(self):
        """The approved auto-approve policy that covers this patch, if any. A
        critical patch is covered only by a policy a CAB member approved."""
        self.ensure_one()
        policies = self.env["fix.msp.patch.policy"].search(
            [
                ("auto_approve", "=", True),
                ("approved_at", "!=", False),
                ("category", "=", self.category),
                "|",
                ("msp_contract_id", "=", False),
                ("msp_contract_id", "=", self.msp_contract_id.id),
            ]
        )
        if self.severity == "critical":
            policies = policies.filtered("approved_by_cab")
        return policies[:1]

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for upd in records.filtered(lambda u: u.state == "missing"):
            policy = upd._auto_approving_policy()
            if policy:
                upd._guarded().write(
                    {
                        "state": "approved",
                        "approved_date": fields.Date.today(),
                        "auto_approved_policy_id": policy.id,
                    }
                )
        return records

    def action_approve(self):
        for upd in self:
            if upd.state not in ("missing", "deferred", "failed"):
                raise UserError("Patch %s cannot be approved from state '%s'" % (upd.id, upd.state))
            if upd.severity == "critical":
                # A critical patch is the change a CAB looks at (A02 audit M05-6).
                require_role(
                    self.env, [GROUP_CAB, GROUP_CHANGE_MANAGER], "Approving a critical patch"
                )
            else:
                require_role(
                    self.env,
                    [GROUP_ENGINEER, GROUP_CAB, GROUP_CHANGE_MANAGER],
                    "Approving a patch",
                )
            upd._guarded().write(
                {
                    "state": "approved",
                    "approved_date": fields.Date.today(),
                    "approved_by_id": self.env.user.id,
                }
            )

    def action_install(self):
        for upd in self:
            # A02 audit M05-6 (probe P1): install was accepted from 'missing',
            # so approval was skippable. Only an approved patch installs.
            if upd.state != "approved":
                raise UserError(
                    "Patch %s is '%s' - only an approved patch can be marked installed."
                    % (upd.identifier or upd.title, upd.state)
                )
            upd._guarded().write({"state": "installed", "installed_at": fields.Datetime.now()})
            publish(
                self.env,
                "msp.patch_installed",
                "fix.msp.patch.update",
                upd.id,
                {"patch": upd.identifier or upd.title, "asset": upd.asset_id.agent_id},
            )

    def action_defer(self, days=7):
        for upd in self:
            if upd.state == "installed":
                raise UserError("Patch %s is installed — nothing to defer" % upd.id)
            upd._guarded().write(
                {
                    "state": "deferred",
                    "deferred_until": fields.Date.today() + timedelta(days=int(days or 7)),
                }
            )

    def action_fail(self, note=""):
        for upd in self:
            if upd.state == "installed":
                raise UserError("Patch %s is installed — cannot mark failed" % upd.id)
            upd._guarded().write({"state": "failed", "fail_note": note or None})


# ------------------------------------------------------------- SLA credits


class FixMspSlaCredit(models.Model):
    """An SLA credit owed to a client when attainment misses the contract
    target (FluxBilling-style: measurable, table-driven, claim or automatic).
    The credit becomes money through the M20 billing seam
    (msp.sla_credit_applied).

    A02 audit M05-2: the amount was a typed field, so a plain user created,
    self-approved and applied a BDT 5,000,000 credit, and an approval at 4,500
    was applied at 450,000. The amount is now COMPUTED from the service report
    and the contract (BRU-RMS-06: credits are automatic). A manual credit or
    override is a separate figure that needs the DOFA tier of its amount; any
    approval pins the amount it covered."""

    _name = "fix.msp.sla.credit"
    _description = "MSP SLA Credit"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "create_date desc"

    # BRU-RMS-06: "manual credits need CFO approval", so every manual amount
    # is Tier 4. A business change to the ladder is this one list.
    _DOFA_MANUAL_CREDIT_THRESHOLDS = [(float("inf"), "tier_4")]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    msp_contract_id = fields.Many2one("fix.msp.contract", required=True, index=True)
    service_report_id = fields.Many2one(
        "fix.msp.service.report", string="Service Report", ondelete="set null"
    )
    period_label = fields.Char(string="Period", required=True)
    attainment_pct = fields.Float(
        string="Attainment %", compute="_compute_amounts", store=True, readonly=True
    )
    target_pct = fields.Float(
        string="Target %", compute="_compute_amounts", store=True, readonly=True
    )
    breach_count = fields.Integer(
        string="Breaches",
        compute="_compute_amounts",
        store=True,
        readonly=True,
        help="Unresolved alerts in the period",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    computed_amount = fields.Monetary(
        string="Computed Credit",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
        readonly=True,
        help="Shortfall % of the contract's monthly value, capped at the monthly value",
    )
    manual_amount = fields.Monetary(
        string="Manual Credit / Override",
        currency_field="currency_id",
        copy=False,
        help="A credit typed by hand instead of the computed one. It needs the DOFA "
        "tier its amount requires (BRU-RMS-06: CFO) and cannot exceed the monthly value.",
    )
    manual_set_by_id = fields.Many2one(
        "res.users", string="Manual Amount Set By", readonly=True, copy=False
    )
    is_manual = fields.Boolean(compute="_compute_amounts", store=True, readonly=True)
    credit_amount = fields.Monetary(
        string="Credit Amount",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
        readonly=True,
    )
    reason = fields.Char()
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("applied", "Applied to Billing")],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    approved_amount = fields.Monetary(
        string="Credit Amount Approved",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The amount the approval covers; any other amount needs re-approval",
    )
    applied_by_id = fields.Many2one("res.users", string="Applied By", readonly=True, copy=False)
    applied_at = fields.Datetime(readonly=True, copy=False)

    _contract_period_unique = models.Constraint(
        "UNIQUE (msp_contract_id, period_label)",
        "A credit already exists for this contract and period",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "service_report_id",
            "credit_amount",
            "computed_amount",
            "is_manual",
            "attainment_pct",
            "target_pct",
            "breach_count",
            "manual_set_by_id",
            "approved_by_id",
            "approved_at",
            "approved_amount",
            "applied_by_id",
            "applied_at",
        }

    def _msp_frozen_fields(self) -> set:
        self.ensure_one()
        frozen = set()
        if self.state != "draft":
            frozen |= {"msp_contract_id", "period_label", "currency_id"}
        if self.state == "applied":
            frozen |= {"manual_amount", "reason", "dofa_justification"}
        return frozen

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        return locked | self._msp_frozen_fields() if self else locked

    # ---- DOFA: the manual figure only ------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.manual_amount or 0.0

    def _dofa_thresholds(self):
        return self._DOFA_MANUAL_CREDIT_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "a manual SLA credit of BDT %.2f" % (self.manual_amount or 0.0)

    @api.depends("manual_amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    # ---- the amount -----------------------------------------------------
    @api.depends(
        "service_report_id.sla_attainment",
        "service_report_id.alert_count",
        "service_report_id.resolved_count",
        "msp_contract_id.sla_target_pct",
        "msp_contract_id.monthly_value",
        "manual_amount",
    )
    def _compute_amounts(self):
        for credit in self:
            contract = credit.msp_contract_id
            report = credit.service_report_id
            target = contract.sla_target_pct or 0.0
            credit.target_pct = target
            if report:
                attainment = round((report.sla_attainment or 0.0) * 100.0, 1)
                shortfall = min(max(target - attainment, 0.0), 100.0)
                amount = round((contract.monthly_value or 0.0) * shortfall / 100.0, 2)
                credit.attainment_pct = attainment
                credit.breach_count = report.alert_count - report.resolved_count
                credit.computed_amount = min(amount, contract.monthly_value or 0.0)
            else:
                credit.attainment_pct = 0.0
                credit.breach_count = 0
                credit.computed_amount = 0.0
            credit.is_manual = (credit.manual_amount or 0.0) > 0.0
            credit.credit_amount = (
                credit.manual_amount if credit.is_manual else credit.computed_amount
            )

    @api.constrains("manual_amount", "msp_contract_id")
    def _check_manual_amount(self):
        for credit in self:
            amount = credit.manual_amount or 0.0
            if amount < 0:
                raise ValidationError("A manual SLA credit cannot be negative.")
            cap = credit.msp_contract_id.monthly_value or 0.0
            if amount > cap + 0.005:
                raise ValidationError(
                    "A manual SLA credit of BDT %.2f exceeds the contract's monthly value of "
                    "BDT %.2f - a credit is capped at the monthly value." % (amount, cap)
                )

    def write(self, vals):
        if not self._fix_guard_open():
            for credit in self.filtered("id"):
                changed = [
                    name
                    for name in credit._msp_frozen_fields() & set(vals)
                    if credit._fix_guard_differs(name, vals[name], credit[name])
                ]
                if changed:
                    raise UserError(
                        "%s cannot change on a credit that is %s."
                        % (
                            ", ".join(sorted(credit._fields[n].string or n for n in changed)),
                            dict(credit._fields["state"].selection)[credit.state].lower(),
                        )
                    )
        typed = self.filtered(
            lambda c: c.id
            and "manual_amount" in vals
            and c._fix_guard_differs("manual_amount", vals["manual_amount"], c.manual_amount)
        )
        result = super().write(vals)
        if typed and not self._fix_guard_open():
            typed._guarded().write({"manual_set_by_id": self.env.user.id})
        # The approval covers the amount that was approved: a different amount
        # voids it at once (A02 audit M05-2, probe S2).
        for credit in self.filtered(lambda c: c.state == "approved"):
            if abs((credit.credit_amount or 0.0) - (credit.approved_amount or 0.0)) > 0.005:
                credit._guarded().write(
                    {
                        "state": "draft",
                        "approved_by_id": False,
                        "approved_at": False,
                        "approved_amount": 0.0,
                    }
                )
                credit.message_post(
                    body="Approval withdrawn: the credit amount changed from BDT %.2f to "
                    "BDT %.2f after approval; it must be approved again."
                    % (credit.approved_amount or 0.0, credit.credit_amount or 0.0)
                )
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self._fix_guard_open():
            typed = records.filtered("manual_amount")
            if typed:
                typed._guarded().write({"manual_set_by_id": self.env.user.id})
        return records

    def action_approve(self):
        for credit in self:
            if credit.state != "draft":
                raise UserError("Credit %s is not draft" % credit.id)
            if (credit.credit_amount or 0.0) <= 0.0:
                raise UserError(
                    "Credit %s has no amount: its service report met the target, and no "
                    "manual credit was entered." % (credit.period_label or credit.id)
                )
            if credit.is_manual:
                # BRU-RMS-06: a manual credit or override needs the DOFA tier its
                # amount requires (tier group, segregation of duties, written
                # justification, amount pin).
                credit.action_dofa_approve()
                credit._dofa_assert_approved("The manual SLA credit")
            else:
                require_role(self.env, [GROUP_CREDIT_APPROVER], "Approving an SLA credit")
            require_other_person(
                self.env, credit.create_uid | credit.manual_set_by_id, "Approving an SLA credit"
            )
            credit._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_at": fields.Datetime.now(),
                    "approved_amount": credit.credit_amount,
                }
            )

    def action_apply(self):
        """Hand the credit to billing (M20 seam). The event carries
        everything the invoice leg needs; no invoice is fabricated here."""
        for credit in self:
            if credit.state != "approved":
                raise UserError("Credit %s must be approved before applying" % credit.id)
            require_role(self.env, [GROUP_CREDIT_APPROVER], "Applying an SLA credit to billing")
            # Re-checked at the point of consequence: the approval covers the
            # amount approved, not whatever the record now says.
            if abs((credit.credit_amount or 0.0) - (credit.approved_amount or 0.0)) > 0.005:
                raise UserError(
                    "Credit %s was approved at BDT %.2f but now stands at BDT %.2f - it "
                    "must be approved again before it is applied."
                    % (credit.period_label, credit.approved_amount, credit.credit_amount)
                )
            if credit.is_manual:
                credit._dofa_assert_approved("The manual SLA credit")
            credit._guarded().write(
                {
                    "state": "applied",
                    "applied_by_id": self.env.user.id,
                    "applied_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "msp.sla_credit_applied",
                "fix.msp.sla.credit",
                credit.id,
                {
                    "contract": credit.msp_contract_id.name,
                    "period": credit.period_label,
                    "amount": credit.approved_amount,
                },
            )


# ------------------------------------------------------------- on-call rota


class FixMspOncallShift(models.Model):
    """The NOC on-call rota: who carries the pager, at which escalation
    level, and when (PagerDuty-style levels; the rotation is data, not
    code)."""

    _name = "fix.msp.oncall.shift"
    _description = "MSP On-Call Shift"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "start_at desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    technician_id = fields.Many2one("hr.employee", string="Technician", required=True)
    level = fields.Selection(
        [("primary", "Primary"), ("secondary", "Secondary"), ("manager", "Manager")],
        default="primary",
        required=True,
    )
    start_at = fields.Datetime(required=True)
    end_at = fields.Datetime(required=True)
    state = fields.Selection(
        [("planned", "Planned"), ("active", "Active"), ("closed", "Closed")],
        default="planned",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        # A02 audit M05-3 (probe O1): the shift form offered 'Shift State' as
        # an input, and a field write activated a second overlapping primary.
        return super()._fix_guarded_fields() | {"state"}

    @api.constrains("start_at", "end_at")
    def _check_window(self):
        for shift in self:
            if shift.end_at <= shift.start_at:
                raise UserError("On-call shift %s must end after it starts" % shift.name)

    @api.model
    def current_primary(self):
        """The active primary on-call employee right now (None outside cover)."""
        shift = self.search([("state", "=", "active"), ("level", "=", "primary")], limit=1)
        return shift.technician_id or None

    def action_activate(self):
        for shift in self:
            if shift.state != "planned":
                raise UserError("Shift %s is not planned" % shift.name)
            # A02 audit M05-12: two overlapping active shifts at one level make
            # "who carries the pager" arbitrary. Searched as the system so a
            # shift in another operating unit still counts.
            clash = self.sudo().search(
                [
                    ("id", "!=", shift.id),
                    ("state", "=", "active"),
                    ("level", "=", shift.level),
                    ("company_id", "=", shift.company_id.id),
                    ("start_at", "<", shift.end_at),
                    ("end_at", ">", shift.start_at),
                ],
                limit=1,
            )
            if clash:
                raise UserError(
                    "Shift %s overlaps the active %s shift %s - close that shift first, so "
                    "only one person carries the %s pager."
                    % (shift.name, shift.level, clash.name, shift.level)
                )
            shift._guarded().write({"state": "active"})
            publish(
                self.env,
                "msp.oncall_shift_active",
                "fix.msp.oncall.shift",
                shift.id,
                {"technician": shift.technician_id.name, "level": shift.level},
            )

    def action_close(self):
        for shift in self:
            if shift.state != "active":
                raise UserError("Shift %s is not active" % shift.name)
            shift._guarded().write({"state": "closed"})


# ------------------------------------------------------ maintenance windows


class FixMspMaintenanceWindow(models.Model):
    """A scheduled change window: alerting is suppressed for the covered
    contract(s) while the window is open, so planned work does not page
    the on-call (the classic RMM maintenance-window behaviour).

    A02 audit M05-5 (probe W1): any user created an estate-wide window and
    wrote state='active', which silenced an offline alert for 30 days. The
    state is now DERIVED from the approval and the time range: a window is
    active only when a CAB member (estate-wide) or the change manager approved
    it and the clock is inside its range. Nobody writes it."""

    _name = "fix.msp.maintenance.window"
    _description = "MSP Maintenance Window"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "start_at desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    msp_contract_id = fields.Many2one(
        "fix.msp.contract",
        string="Scoped To Contract",
        help="Empty = every contract (estate-wide: needs a CAB member's approval)",
    )
    suppress_alerts = fields.Boolean(default=True, string="Suppress Alerting")
    purpose = fields.Char()
    start_at = fields.Datetime(required=True)
    end_at = fields.Datetime(required=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    closed_at = fields.Datetime(string="Closed Early At", readonly=True, copy=False)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    state = fields.Selection(
        [("planned", "Planned"), ("active", "Active"), ("closed", "Closed")],
        compute="_compute_state",
        search="_search_state",
        help="Derived: active only while an approved window's time range is running",
    )

    # An approved window is the thing that was approved: to change its scope
    # or its times, close it and raise a new one.
    _APPROVED_FROZEN_FIELDS = {
        "name",
        "msp_contract_id",
        "suppress_alerts",
        "start_at",
        "end_at",
        "company_id",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_at",
            "closed_at",
            "closed_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        return locked | self._APPROVED_FROZEN_FIELDS if self and self.approved_at else locked

    def write(self, vals):
        if not self._fix_guard_open():
            for window in self.filtered(lambda w: w.id and w.approved_at):
                changed = [
                    name
                    for name in self._APPROVED_FROZEN_FIELDS & set(vals)
                    if window._fix_guard_differs(name, vals[name], window[name])
                ]
                if changed:
                    raise UserError(
                        "%s cannot change on an approved maintenance window. Close it and "
                        "raise a new window for approval."
                        % ", ".join(sorted(window._fields[n].string or n for n in changed))
                    )
        return super().write(vals)

    @api.constrains("start_at", "end_at")
    def _check_window(self):
        for window in self:
            if window.end_at <= window.start_at:
                raise UserError("Maintenance window %s must end after it starts" % window.name)

    @api.depends("approved_at", "closed_at", "start_at", "end_at")
    def _compute_state(self):
        now = fields.Datetime.now()
        for window in self:
            if window.closed_at or (window.end_at and window.end_at < now):
                window.state = "closed"
            elif window.approved_at and window.start_at and window.start_at <= now:
                window.state = "active"
            else:
                window.state = "planned"

    def _search_state(self, operator, value):
        if operator != "in":
            return NotImplemented
        now = fields.Datetime.now()
        closed = Domain("closed_at", "!=", False) | Domain("end_at", "<", now)
        active = Domain.AND(
            [
                Domain("closed_at", "=", False),
                Domain("end_at", ">=", now),
                Domain("approved_at", "!=", False),
                Domain("start_at", "<=", now),
            ]
        )
        planned = Domain.AND(
            [
                Domain("closed_at", "=", False),
                Domain("end_at", ">=", now),
                Domain("approved_at", "=", False) | Domain("start_at", ">", now),
            ]
        )
        by_state = {"closed": closed, "active": active, "planned": planned}
        return Domain.OR(by_state[v] for v in value if v in by_state)

    def _msp_open_for(self, contract):
        """True when this window is approved, running now and covers ``contract``."""
        self.ensure_one()
        return self.state == "active" and (
            not self.msp_contract_id or self.msp_contract_id == contract
        )

    @api.model
    def alerting_suppressed(self, asset):
        """True when ``asset`` sits under an ACTIVE window that suppresses
        alerting (used by ingest_telemetry before raising an alert)."""
        windows = self.search([("state", "=", "active"), ("suppress_alerts", "=", True)])
        contract = asset.msp_contract_id
        return any(window._msp_open_for(contract) for window in windows)

    def action_approve(self):
        """Approve the window. An estate-wide window silences every client's
        alerting, so it needs a CAB member; a contract window may also be
        approved by the change manager. Never by the person who raised it."""
        for window in self:
            if window.approved_at:
                raise UserError("Window %s is already approved" % window.name)
            if window.closed_at or window.end_at <= fields.Datetime.now():
                raise UserError("Window %s is over - raise a new window" % window.name)
            if window.msp_contract_id:
                require_role(
                    self.env,
                    [GROUP_CAB, GROUP_CHANGE_MANAGER],
                    "Approving a maintenance window",
                )
            else:
                require_role(
                    self.env,
                    [GROUP_CAB],
                    "Approving an estate-wide maintenance window (it silences alerting "
                    "for every client)",
                )
            require_other_person(self.env, window.create_uid, "Approving a maintenance window")
            window._guarded().write(
                {"approved_by_id": self.env.user.id, "approved_at": fields.Datetime.now()}
            )
            publish(
                self.env,
                "msp.maintenance_window_open",
                "fix.msp.maintenance.window",
                window.id,
                {
                    "window": window.name,
                    "start_at": fields.Datetime.to_string(window.start_at),
                    "end_at": fields.Datetime.to_string(window.end_at),
                },
            )

    def action_close(self):
        """Close the window early (it closes on its own at its end time)."""
        for window in self:
            if window.state == "closed":
                raise UserError("Window %s is already closed" % window.name)
            require_role(
                self.env, [GROUP_CAB, GROUP_CHANGE_MANAGER], "Closing a maintenance window"
            )
            window._guarded().write(
                {"closed_at": fields.Datetime.now(), "closed_by_id": self.env.user.id}
            )


# ------------------------------------------------------- problem & change


class FixMspChangeRecord(models.Model):
    """ITIL-style problem & change records for the managed estate, with a
    lightweight CAB: draft → approved → implemented → closed (or rejected).

    A02 audit M05-1: the requester approved and implemented his own high-risk
    change with no rollback plan, no CAB approver and no window. Now:
      * a normal change is approved by a CAB member, an emergency change by
        the change manager; never by the requester (the acting user is
        stamped as cab_approver_id);
      * a high-risk change needs a rollback plan before approval;
      * a normal change is implemented only inside an approved maintenance
        window that is open now and covers its contract, and not by the
        person who approved it;
      * an emergency change may be implemented at once, but cannot close
        before a post-implementation review."""

    _name = "fix.msp.change.record"
    _description = "MSP Problem & Change Record"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Title", required=True)
    kind = fields.Selection(
        [("change", "Change"), ("problem", "Problem")], default="change", required=True
    )
    msp_contract_id = fields.Many2one("fix.msp.contract", string="Contract", index=True)
    asset_id = fields.Many2one("fix.monitored.asset", string="Asset")
    description = fields.Text()
    risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")], default="medium", required=True
    )
    change_type = fields.Selection(
        [("standard", "Standard"), ("normal", "Normal"), ("emergency", "Emergency")],
        default="normal",
        required=True,
    )
    emergency = fields.Boolean(
        compute="_compute_emergency",
        store=True,
        help="Emergency path: the change manager approves, the change may be "
        "implemented outside a window, and a post-implementation review is "
        "required before close",
    )
    requested_by = fields.Many2one("hr.employee", string="Requested By")
    implemented_at = fields.Datetime(readonly=True)
    implemented_by_id = fields.Many2one(
        "res.users", string="Implemented By", readonly=True, copy=False
    )
    resolution_note = fields.Char(readonly=True, copy=False)

    # --- A02 Enterprise Data Capture (M05 CAB & Rollback Specification) ---
    cab_approver_id = fields.Many2one(
        "res.users",
        string="CAB Approving Authority",
        tracking=True,
        readonly=True,
        copy=False,
        help="Stamped with the acting user by action_approve; never typed",
    )
    approved_at = fields.Datetime(readonly=True, copy=False)
    rollback_plan = fields.Text(
        string="Documented Backout & Rollback Plan",
    )
    maintenance_window_id = fields.Many2one(
        "fix.msp.maintenance.window",
        string="Scheduled Maintenance Window",
    )
    pir_note = fields.Text(string="Post-Implementation Review", readonly=True, copy=False)
    pir_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True, copy=False)
    pir_at = fields.Datetime(string="Reviewed At", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("implemented", "Implemented"),
            ("closed", "Closed"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # What the CAB approved: frozen once the record leaves draft.
    _APPROVED_FROZEN_FIELDS = {
        "name",
        "kind",
        "msp_contract_id",
        "asset_id",
        "description",
        "risk",
        "change_type",
        "requested_by",
        "rollback_plan",
        "company_id",
    }

    def _fix_guarded_fields(self) -> set:
        # A02 audit M05-1 / M05-3 (probes C5, C6): state and cab_approver_id
        # were forged to 'implemented' / self by ORM and by P03.
        return super()._fix_guarded_fields() | {
            "state",
            "cab_approver_id",
            "approved_at",
            "implemented_at",
            "implemented_by_id",
            "resolution_note",
            "pir_note",
            "pir_by_id",
            "pir_at",
        }

    def _msp_frozen_fields(self) -> set:
        self.ensure_one()
        frozen = set()
        if self.state != "draft":
            frozen |= self._APPROVED_FROZEN_FIELDS
        if self.state not in ("draft", "approved"):
            frozen.add("maintenance_window_id")
        return frozen

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        return locked | self._msp_frozen_fields() if self else locked

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self.filtered("id"):
                changed = [
                    name
                    for name in rec._msp_frozen_fields() & set(vals)
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                ]
                if changed:
                    raise UserError(
                        "%s cannot change once the change record is %s: the approval "
                        "covers what was approved. Reject it and raise a new record."
                        % (
                            ", ".join(sorted(rec._fields[n].string or n for n in changed)),
                            dict(rec._fields["state"].selection)[rec.state].lower(),
                        )
                    )
        return super().write(vals)

    @api.depends("change_type")
    def _compute_emergency(self):
        for rec in self:
            rec.emergency = rec.change_type == "emergency"

    def _msp_requesters(self):
        self.ensure_one()
        return self.create_uid | self.requested_by.user_id

    def action_approve(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Record %s is not draft" % rec.id)
            if rec.emergency:
                require_role(self.env, [GROUP_CHANGE_MANAGER], "Approving an emergency change")
            else:
                require_role(self.env, [GROUP_CAB], "Approving a change (CAB)")
            require_other_person(self.env, rec._msp_requesters(), "Approving a change")
            if rec.risk == "high" and not (rec.rollback_plan or "").strip():
                raise UserError(
                    "Change %s is high risk: document the backout and rollback plan "
                    "before it is approved (BRU-RMS-08)." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "cab_approver_id": self.env.user.id,
                    "approved_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "msp.change_approved",
                "fix.msp.change.record",
                rec.id,
                {"title": rec.name},
            )

    def action_reject(self, note=""):
        for rec in self:
            if rec.state not in ("draft", "approved"):
                raise UserError("Record %s cannot be rejected from '%s'" % (rec.id, rec.state))
            require_role(self.env, [GROUP_CAB, GROUP_CHANGE_MANAGER], "Rejecting a change")
            rec._guarded().write({"state": "rejected", "resolution_note": note or None})

    def action_implement(self, note=""):
        now = fields.Datetime.now()
        for rec in self:
            if rec.state != "approved":
                raise UserError("Record %s must be approved before implementation" % rec.id)
            if rec.risk == "high" and not (rec.rollback_plan or "").strip():
                raise UserError("Change %s is high risk and has no rollback plan." % rec.name)
            # The approver does not also carry out the change (spec §13).
            require_other_person(self.env, rec.cab_approver_id, "Implementing a change")
            if not rec.emergency:
                window = rec.maintenance_window_id
                if not window:
                    raise UserError(
                        "Change %s has no maintenance window. Link an approved window "
                        "(or raise it as an emergency change)." % rec.name
                    )
                if not window._msp_open_for(rec.msp_contract_id):
                    raise UserError(
                        "Change %s may be implemented only inside its approved maintenance "
                        "window while it is open, for this contract. Window %s is %s%s."
                        % (
                            rec.name,
                            window.name,
                            window.state,
                            "" if window.approved_at else " and not approved",
                        )
                    )
            rec._guarded().write(
                {
                    "state": "implemented",
                    "implemented_at": now,
                    "implemented_by_id": self.env.user.id,
                    "resolution_note": note or rec.resolution_note,
                }
            )
            publish(
                self.env,
                "msp.change_implemented",
                "fix.msp.change.record",
                rec.id,
                {"title": rec.name},
            )

    def action_record_review(self, note=""):
        """The post-implementation review an emergency change needs before it
        closes. A CAB member or the change manager, not the implementer."""
        for rec in self:
            if rec.state != "implemented":
                raise UserError("Only an implemented change is reviewed.")
            if not (note or "").strip():
                raise UserError("Write the review: what was done, the outcome, follow-ups.")
            require_role(
                self.env,
                [GROUP_CAB, GROUP_CHANGE_MANAGER],
                "Recording a post-implementation review",
            )
            require_other_person(
                self.env, rec.implemented_by_id, "Recording a post-implementation review"
            )
            rec._guarded().write(
                {
                    "pir_note": note.strip(),
                    "pir_by_id": self.env.user.id,
                    "pir_at": fields.Datetime.now(),
                }
            )
        return True

    def action_close(self, note=""):
        for rec in self:
            if rec.state not in ("implemented", "rejected"):
                raise UserError(
                    "Record %s must be implemented (or rejected) before closing" % rec.id
                )
            if rec.state == "implemented" and rec.emergency and not rec.pir_at:
                raise UserError(
                    "Emergency change %s needs its post-implementation review before it "
                    "closes." % rec.name
                )
            rec._guarded().write(
                {"state": "closed", "resolution_note": note or rec.resolution_note}
            )


# ------------------------------------------- estate & contract polish exts


class FixMonitoredAssetEngines(models.Model):
    """Estate polish: real display names and a live health score."""

    _inherit = "fix.monitored.asset"

    alert_ids = fields.One2many("fix.msp.alert", "asset_id", string="Alerts")
    open_alert_count = fields.Integer(compute="_compute_open_alerts", string="Open Alerts")
    health_score = fields.Integer(
        compute="_compute_health_score",
        store=True,
        string="Health Score",
        help="100 healthy; 50 degraded; 0 offline — minus 5 per open alert, floored at 0",
    )

    @api.depends("alert_ids.state")
    def _compute_open_alerts(self):
        for asset in self:
            asset.open_alert_count = len(asset.alert_ids.filtered(lambda a: a.state != "resolved"))

    @api.depends("health", "alert_ids.state")
    def _compute_health_score(self):
        for asset in self:
            open_alerts = len(asset.alert_ids.filtered(lambda a: a.state != "resolved"))
            base = {"healthy": 100, "degraded": 50, "offline": 0}.get(asset.health, 0)
            asset.health_score = max(0, base - 5 * open_alerts)

    @api.depends("hostname", "agent_id")
    def _compute_display_name(self) -> None:
        for asset in self:
            asset.display_name = asset.hostname or asset.agent_id or "asset %s" % asset.id


class FixMspContractEngines(models.Model):
    """Contract polish: the SLA target the credits engine measures against
    and the computed monthly value."""

    _inherit = "fix.msp.contract"

    sla_target_pct = fields.Float(
        string="SLA Target %", default=90.0, help="Monthly attainment target (percentage)"
    )
    monthly_value = fields.Monetary(
        compute="_compute_monthly_value",
        store=True,
        currency_field="currency_id",
        string="Monthly Value",
        help="Per-device monthly × covered devices",
    )
    credit_ids = fields.One2many("fix.msp.sla.credit", "msp_contract_id", string="SLA Credits")

    @api.depends("per_device_monthly", "device_count", "asset_ids")
    def _compute_monthly_value(self):
        for contract in self:
            devices = contract.device_count or len(contract.asset_ids)
            contract.monthly_value = (contract.per_device_monthly or 0.0) * devices

    def action_compute_sla_credits(self):
        """Draft a credit for every period whose report attainment missed the
        target: shortfall % of the monthly value (capped at the monthly
        value). Idempotent per (contract, period).

        The amount is computed on the credit from its report and this
        contract (A02 audit M05-2). A report with NO attainment figure is not
        read as 0%: it produces no credit and is flagged (A02 audit M05-11)."""
        Credit = self.env["fix.msp.sla.credit"]
        Report = self.env["fix.msp.service.report"]
        for contract in self:
            reports = contract.report_ids
            missing = Report
            if reports:
                reports.flush_recordset(["sla_attainment"])
                self.env.cr.execute(
                    "SELECT id FROM fix_msp_service_report WHERE id IN %s "
                    "AND sla_attainment IS NULL",
                    [tuple(reports.ids)],
                )
                missing = Report.browse([row[0] for row in self.env.cr.fetchall()])
            for report in missing.filtered(lambda r: not r.attainment_flagged):
                report._guarded().write({"attainment_flagged": True})
                report.message_post(
                    body="No SLA attainment figure on this report, so no SLA credit was "
                    "computed for %s. Regenerate the report to compute one." % report.period_label
                )
            for report in reports - missing:
                attainment = round((report.sla_attainment or 0.0) * 100.0, 1)
                if attainment >= contract.sla_target_pct:
                    continue
                if Credit.search_count(
                    [
                        ("msp_contract_id", "=", contract.id),
                        ("period_label", "=", report.period_label),
                    ]
                ):
                    continue
                Credit._guarded().create(
                    {
                        "msp_contract_id": contract.id,
                        "service_report_id": report.id,
                        "period_label": report.period_label,
                        "operating_unit_id": report.operating_unit_id.id
                        or contract.operating_unit_id.id,
                        "reason": "Attainment %.1f%% below target %.1f%%"
                        % (attainment, contract.sla_target_pct),
                    }
                )
        return True


class FixMspAlertEngines(models.Model):
    """The on-call escalation flag on alerts."""

    _inherit = "fix.msp.alert"

    escalated = fields.Boolean(
        copy=False,
        readonly=True,
        help="Escalated beyond first response (pages the next rota level). Set by "
        "action_escalate only.",
    )
    escalated_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"escalated", "escalated_at"}

    def action_escalate(self):
        for alert in self:
            if alert.state == "resolved":
                raise UserError("Alert %s is resolved — nothing to escalate" % alert.id)
            if alert.escalated:
                raise UserError("Alert %s is already escalated" % alert.id)
            alert._guarded().write({"escalated": True, "escalated_at": fields.Datetime.now()})
            publish(
                self.env,
                "msp.alert_escalated",
                "fix.msp.alert",
                alert.id,
                {"asset": alert.asset_id.agent_id, "severity": alert.severity},
            )


class FixMspServiceReportEngines(models.Model):
    """Report polish: the percentage column the workspace grid shows."""

    _inherit = "fix.msp.service.report"

    sla_attainment_pct = fields.Float(
        compute="_compute_attainment_pct",
        store=True,
        string="SLA Attainment %",
        help="sla_attainment (0-1) rendered as a percentage",
    )

    @api.depends("sla_attainment")
    def _compute_attainment_pct(self):
        for report in self:
            report.sla_attainment_pct = round((report.sla_attainment or 0.0) * 100.0, 1)
