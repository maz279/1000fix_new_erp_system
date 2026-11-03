# fix_facility — M47: facility, branch infrastructure & maintenance work orders (P10-M05 / R08-M03).
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

# ---- DOFA ladders (A07 audit 2026-11-03, decision B2) ---------------------
# The M47 spec names the deciding roles but gives no BDT figures, so each
# ladder reuses the closest existing estate ladder. Both are DEFAULTS THE
# BUSINESS MUST CONFIRM; a fix.approval.matrix row overrides them per model
# without code.
#
# Facility repair spend: the estate's repair ladder, cd_workshop
# BER_DOFA_THRESHOLDS (fix_workshop_job.py:143) — Tier 2 up to BDT 10,000,
# Tier 3 up to 50,000, Tier 4 above. Any costed work order is approved.
WO_SPEND_DOFA_THRESHOLDS = [
    (10000.0, "tier_2"),
    (50000.0, "tier_3"),
    (float("inf"), "tier_4"),
]
# Estate cost decisions (capex project budget, lease commitment, site-asset
# retirement): cd_rental_asset fix_rental_fleet.py:28 — Tier 2 up to BDT
# 250,000, Tier 3 up to 1,000,000, Tier 4 (CFO) above. Nothing at risk is Tier 0.
ESTATE_COST_DOFA_THRESHOLDS = [
    (0.0, "tier_0"),
    (250000.0, "tier_2"),
    (1000000.0, "tier_3"),
    (float("inf"), "tier_4"),
]

# Site closure and reopening (spec §8.1: "CEO + CFO"). No role groups exist
# yet (P1), so the DOFA tier groups whose labels match are used: CFO = Tier 4
# "CFO / CCO / COO", CEO = Tier 5 "Managing Director / Board". Two separate
# sign-offs, by two different people, CFO first.
SITE_STATUS_STAGES = {
    "cfo": ("cd_entity_config.group_dofa_tier_4", "CFO (DOFA Tier 4)"),
    "ceo": ("cd_entity_config.group_dofa_tier_5", "CEO (DOFA Tier 5)"),
}
SITE_STATUS_STAMPS = (
    "status_cfo_approved_by_id",
    "status_cfo_approved_at",
    "status_ceo_approved_by_id",
    "status_ceo_approved_at",
)
# BRU-FAC-15 recovery checklist: what a closing site must have settled when
# it still holds an active lease, an open work order or a valid licence.
CLOSURE_CHECKLIST = (
    "closure_assets_recovered",
    "closure_licences_surrendered",
    "closure_deposit_settled",
    "closure_notes",
)

WO_OPEN_STATES = ("draft", "scheduled", "in_progress")
# Once the work is complete its cost and evidence are the record of what was
# done and spent: they are frozen (a reopen unfreezes them).
WO_COST_FROZEN_STATES = ("completed", "verified", "cancelled")
WO_FROZEN_FIELDS = ("estimated_cost", "actual_cost", "completion_notes")


def _changes(records, vals) -> bool:
    """True when `vals` would change a value on one of `records`. Echoing the
    current value (the P03 form posts every field) is no change."""
    names = [n for n in vals if n in records._fields]
    return any(rec._fix_guard_differs(n, vals[n], rec[n]) for rec in records for n in names)


def _refuse_if_covered(rec):
    """A request for an approval the record already holds is a duplicate."""
    if not rec.dofa_approved:
        return
    try:
        rec._dofa_assert_approved()
    except ValidationError:
        return  # the approval no longer covers it: re-approval is due
    raise UserError(
        "%s already holds an approval that covers %s."
        % (rec.display_name, rec._dofa_amount_label())
    )


class FixApprovalMatrixFacility(models.Model):
    """M47 decision domains on the DoA register (A07 audit 2026-11-03)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("facility_wo_spend", "Facility Work-Order Spend"),
            ("site_status", "Site Closure / Reopening"),
            ("site_capex", "Site Capex Project Budget"),
            ("lease_modification", "Lease Renewal / Modification"),
            ("site_asset_retirement", "Site Asset Retirement"),
        ],
        ondelete=dict.fromkeys(
            (
                "facility_wo_spend",
                "site_status",
                "site_capex",
                "lease_modification",
                "site_asset_retirement",
            ),
            "cascade",
        ),
    )


class FixSite(models.Model):
    _name = "fix.site"
    _description = "Site / Facility"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]

    # A07 audit (2026-11-03) M47-5: close and reopen were one-line clicks and
    # `state` was writable, so a plain user closed a site holding an active
    # lease, a 600k deposit, an open work order and a valid licence. A status
    # change is now a routed M63 decision signed by the CFO and then the CEO
    # (neither the requester nor the creator), and a closure with open
    # obligations needs the recovery checklist. The readiness gate (planned /
    # fitting out) is P2 and not built here.
    _approval_domain = "site_status"
    _approval_apply_method = "action_approve_status_change"
    _approval_group = SITE_STATUS_STAGES["cfo"][0]
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    site_type = fields.Selection(
        [
            ("branch", "Service Branch"),
            ("warehouse", "Warehouse"),
            ("office", "Corporate Office"),
            ("data_centre", "Data Centre"),
        ],
        required=True,
        default="branch",
    )
    branch_id = fields.Many2one("fix.branch", string="Branch (M30)", ondelete="set null")
    address = fields.Text()
    floor_area_sqm = fields.Float(string="Floor Area (sqm)")
    lease_start = fields.Date()
    lease_end = fields.Date()
    monthly_rent = fields.Float(string="Monthly Rent (BDT)")
    equipment_ids = fields.Many2many(
        "fix.equipment",
        string="Linked Site Assets",
        help="Equipments deployed at this facility (M45)",
    )
    work_order_ids = fields.One2many("fix.facility.work.order", "site_id", string="Work Orders")
    asset_ids = fields.One2many("fix.site.asset", "site_id", string="Infrastructure Assets")
    state = fields.Selection(
        [("active", "Active"), ("closed", "Closed")], default="active", required=True, tracking=True
    )
    closure_assets_recovered = fields.Boolean(
        string="Assets Recovered",
        help="Plant, equipment (M45), stock (M15) and vehicles (M46) recovered and reconciled",
    )
    closure_licences_surrendered = fields.Boolean(string="Licences Surrendered")
    closure_deposit_settled = fields.Boolean(
        string="Deposit Recovered / Written Off",
        help="The lease deposit is recovered, or written off with its own approval",
    )
    closure_notes = fields.Text(
        string="Recovery Notes", help="What was recovered, surrendered and settled, with references"
    )
    status_cfo_approved_by_id = fields.Many2one(
        "res.users", string="Status Change: CFO Sign-off", readonly=True, copy=False
    )
    status_cfo_approved_at = fields.Datetime(string="CFO Signed At", readonly=True, copy=False)
    status_ceo_approved_by_id = fields.Many2one(
        "res.users", string="Status Change: CEO Sign-off", readonly=True, copy=False
    )
    status_ceo_approved_at = fields.Datetime(string="CEO Signed At", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"} | set(SITE_STATUS_STAMPS)

    def write(self, vals):
        # The CFO and CEO sign off the closure with the checklist as it then
        # read (the approval's pin): ticking or editing it afterwards voids
        # the sign-offs, so the approvers always saw what is executed.
        voided = self.browse()
        if not self._fix_guard_has_token() and set(CLOSURE_CHECKLIST) & set(vals):
            checklist = {k: vals[k] for k in CLOSURE_CHECKLIST if k in vals}
            voided = self.filtered(
                lambda r: (
                    (
                        r.approval_state in ("pending", "approved")
                        or r.status_cfo_approved_by_id
                        or r.status_ceo_approved_by_id
                    )
                    and _changes(r, checklist)
                )
            )
        result = super().write(vals)
        if voided:
            voided._site_void_status_approval("the closure checklist changed after sign-off")
        return result

    def action_link_assets(self):
        for rec in self:
            publish(
                self.env,
                "site.assets_linked",
                "fix.site",
                rec.id,
                {"site": rec.name, "assets_count": len(rec.equipment_ids)},
            )

    # ---- status-change approval (CFO, then CEO) ----------------------------
    def _site_stage(self):
        """The sign-off the status change still needs: 'cfo', 'ceo' or None."""
        self.ensure_one()
        if not self.status_cfo_approved_by_id:
            return "cfo"
        if not self.status_ceo_approved_by_id:
            return "ceo"
        return None

    def _approval_group_xmlid(self):
        stage = self._site_stage() if len(self) == 1 else "cfo"
        return SITE_STATUS_STAGES[stage or "ceo"][0]

    def _approval_holders(self, group):
        users = super()._approval_holders(group)
        if self._site_stage() == "cfo":
            # Tier groups imply the tiers below: route the CFO sign-off to
            # Tier 4 holders, not to the Tier 5 CEO who signs second.
            users = self._approval_lowest_competent(users, "tier_4")
        return users

    def _approval_excluded(self):
        # the CFO who signed first is not also the second signature
        return super()._approval_excluded() | self.status_cfo_approved_by_id.sudo()

    def _approval_needed(self) -> bool:
        return self.state in ("active", "closed") and bool(self._site_stage())

    def _approval_on_rejected(self, comment):
        self._site_void_status_approval("the status change was rejected: %s" % (comment or ""))

    def _site_void_status_approval(self, reason):
        for rec in self:
            if any(rec[f] for f in SITE_STATUS_STAMPS) or rec.approval_state != "none":
                rec._guarded().write(dict.fromkeys(SITE_STATUS_STAMPS, False))
                rec._approval_void(reason)
                rec.message_post(body="Site status-change sign-offs withdrawn: %s." % reason)

    def _site_open_items(self) -> list:
        """What the site still holds: active leases, open work orders (a
        completed one still awaits verification) and valid licences."""
        self.ensure_one()
        env = self.env
        counts = [
            (
                env["fix.site.lease"]
                .sudo()
                .search_count([("site_id", "=", self.id), ("state", "=", "active")]),
                "active lease(s)",
            ),
            (
                env["fix.facility.work.order"]
                .sudo()
                .search_count(
                    [
                        ("site_id", "=", self.id),
                        ("state", "in", (*WO_OPEN_STATES, "completed")),
                    ]
                ),
                "open work order(s)",
            ),
            (
                env["fix.site.licence"]
                .sudo()
                .search_count([("site_id", "=", self.id), ("is_valid", "=", True)]),
                "valid licence(s)",
            ),
        ]
        return ["%d %s" % (n, label) for n, label in counts if n]

    def _closure_checklist_done(self) -> bool:
        self.ensure_one()
        return bool(
            self.closure_assets_recovered
            and self.closure_licences_surrendered
            and self.closure_deposit_settled
            and (self.closure_notes or "").strip()
        )

    def _site_check_closable(self):
        for rec in self:
            items = rec._site_open_items()
            if items and not rec._closure_checklist_done():
                raise UserError(
                    "%s still holds %s. Complete the recovery checklist (assets recovered, "
                    "licences surrendered, deposit recovered or written off, recovery notes) "
                    "before its closure is approved or executed (BRU-FAC-15)."
                    % (rec.name, ", ".join(items))
                )

    def action_request_approval(self, justification=None):
        """Route the next status change (close an active site, reopen a closed
        one) for the CFO sign-off, then again for the CEO's."""
        for rec in self:
            if rec.state == "active":
                rec._site_check_closable()
        return super().action_request_approval(justification=justification)

    def action_approve_status_change(self):
        """The M63 apply method: one sign-off per inbox decision, CFO first.
        A direct press is refused (_approval_assert_routed)."""
        self._approval_assert_routed()
        # Superuser code with no deciding task (data loading, service calls).
        trusted = self.env.su and not self._approval_task()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        now = fields.Datetime.now()
        for rec in self:
            stage = rec._site_stage()
            if not stage or rec.state not in ("active", "closed"):
                raise UserError("%s has no status change awaiting sign-off." % rec.name)
            group, label = SITE_STATUS_STAGES[stage]
            if not trusted:
                if not authority.has_group(group):
                    raise UserError(
                        "Signing off a site status change as %s requires that authority, which "
                        "%s does not hold." % (label, authority.name)
                    )
                requester = rec.approval_request_id.sudo().requested_by_id
                if acting & (rec.create_uid | requester | rec.status_cfo_approved_by_id):
                    raise UserError(
                        "Segregation of duties: the creator, the requester and the first "
                        "signatory cannot sign off this site status change."
                    )
            rec._guarded().write(
                {
                    "status_%s_approved_by_id" % stage: self.env.uid,
                    "status_%s_approved_at" % stage: now,
                }
            )
            rec.message_post(
                body="%s sign-off for %s recorded by %s."
                % (label, "closure" if rec.state == "active" else "reopening", self.env.user.name)
            )
        return True

    def _site_assert_status_approved(self, what):
        for rec in self:
            if rec._site_stage():
                raise UserError(
                    "%s %s needs the CFO and the CEO sign-off. Use Request Approval: the "
                    "approval engine routes it to them in turn." % (what, rec.name)
                )

    def _site_consume_status_approval(self):
        self._guarded().write(
            {**dict.fromkeys(SITE_STATUS_STAMPS, False), "approval_state": "none"}
        )

    def action_close(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active site can be closed.")
            rec._site_check_closable()
            rec._site_assert_status_approved("Closing")
            open_items = rec._site_open_items()
            rec._guarded().write({"state": "closed"})
            rec._site_consume_status_approval()
            rec.message_post(
                body="Site closed by %s.%s"
                % (
                    self.env.user.name,
                    " Closed under the recovery checklist with %s." % ", ".join(open_items)
                    if open_items
                    else "",
                )
            )
        return True

    def action_reopen(self):
        for rec in self:
            if rec.state != "closed":
                raise UserError("Only a closed site can be reopened.")
            rec._site_assert_status_approved("Reopening")
            # a reopened site starts any later closure with a fresh checklist
            rec._guarded().write(
                {
                    "state": "active",
                    "closure_assets_recovered": False,
                    "closure_licences_surrendered": False,
                    "closure_deposit_settled": False,
                }
            )
            rec._site_consume_status_approval()
            rec.message_post(body="Site reopened by %s." % self.env.user.name)
        return True


class FixFacilityWorkOrder(models.Model):
    _name = "fix.facility.work.order"
    _description = "Facility Work Order"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "id desc"
    # A07 audit (2026-11-03) M47-1/-6/-7: the three actions were one-line state
    # assignments with no source-state check; `state` was writable, a WO was
    # born `completed`, a 5M repair needed nobody else, completion carried no
    # evidence, the raiser closed their own WO and the actual cost was edited
    # after completion. Now:
    #   draft -> (DOFA spend approval) -> scheduled -> in_progress ->
    #   completed (notes) -> verified (by someone else); cancel before
    #   completion; reopen voids a completion.
    # fix.dofa.mixin brings fix.approvable.mixin (cd_workflow_engine) and the
    # guard; naming the approvable mixin again here breaks the class MRO.
    # (_inherit stays above this note: audit-view-integrity reads only the
    # first 600 characters of a class for it.)

    _approval_domain = "facility_wo_spend"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    def _dofa_amount(self) -> float:
        """The spend at risk: the higher of the estimate and the actual, so an
        actual above the approved estimate needs re-approval at completion."""
        self.ensure_one()
        return max(self.estimated_cost or 0.0, self.actual_cost or 0.0)

    def _dofa_thresholds(self):
        return WO_SPEND_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (facility repair spend)" % self._dofa_amount()

    @api.depends("estimated_cost", "actual_cost")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one("fix.site", string="Site", required=True, ondelete="cascade")
    equipment_id = fields.Many2one(
        "fix.equipment",
        string="Target Equipment",
        help="Target infrastructure asset from cd_equipment_register (M46)",
    )
    work_type = fields.Selection(
        [
            ("maintenance", "Preventive Maintenance"),
            ("repair", "Emergency Repair"),
            ("upgrade", "Infrastructure Upgrade"),
            ("inspection", "Compliance Inspection"),
        ],
        required=True,
        default="maintenance",
    )
    description = fields.Text(required=True)
    assigned_to = fields.Many2one("hr.employee", string="Assigned Engineer")
    scheduled_date = fields.Date(default=fields.Date.context_today)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    estimated_cost = fields.Monetary(string="Estimated Cost", currency_field="currency_id")
    actual_cost = fields.Monetary(string="Actual Cost", currency_field="currency_id")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("scheduled", "Scheduled"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("verified", "Verified / Closed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    completion_notes = fields.Text(
        string="Completion Evidence",
        copy=False,
        help="What was done and the evidence reference (photos, report, vendor sheet). "
        "Required to complete; frozen once completed.",
    )
    completed_by_id = fields.Many2one("res.users", string="Completed By", readonly=True, copy=False)
    completed_at = fields.Datetime(string="Completed At", readonly=True, copy=False)
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_at = fields.Datetime(string="Verified At", readonly=True, copy=False)
    verification_notes = fields.Text(string="Verification Notes", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "completed_by_id",
            "completed_at",
            "verified_by_id",
            "verified_at",
            "verification_notes",
        }

    def _wo_site_pinned(self) -> bool:
        # the approval is for this site's work; it does not move underneath it
        return self.state != "draft" or self.approval_state in ("pending", "approved")

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1:
            if self.state in WO_COST_FROZEN_STATES:
                locked |= set(WO_FROZEN_FIELDS)
            if self._wo_site_pinned():
                locked.add("site_id")
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.facility.work.order")
                    or f"FWO/{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in WO_FROZEN_FIELDS if k in vals}
            if frozen and _changes(
                self.filtered(lambda r: r.state in WO_COST_FROZEN_STATES), frozen
            ):
                raise UserError(
                    "The cost and completion evidence of a completed, verified or cancelled "
                    "work order are the record of what was done and cannot be edited. Reopen "
                    "the work order to correct them."
                )
            if "site_id" in vals and _changes(
                self.filtered(lambda r: r._wo_site_pinned()), {"site_id": vals["site_id"]}
            ):
                raise UserError(
                    "A scheduled or approved work order stays on its site. Cancel it and raise "
                    "a new one for the other site."
                )
        return super().write(vals)

    def _wo_require_state(self, allowed, what):
        for rec in self:
            if rec.state not in allowed:
                labels = dict(self._fields["state"].selection)
                raise UserError(
                    "%s cannot %s: it is %s (allowed from %s)."
                    % (rec.name, what, labels[rec.state], ", ".join(labels[s] for s in allowed))
                )

    def action_request_approval(self, justification=None):
        """Route the repair spend for its DOFA tier (before scheduling, and
        again when the actual cost passes what was approved)."""
        self._wo_require_state(WO_OPEN_STATES, "have its spend approved")
        for rec in self:
            _refuse_if_covered(rec)
        return super().action_request_approval(justification=justification)

    def action_schedule(self, date=None):
        self._wo_require_state(("draft",), "be scheduled")
        for rec in self:
            rec._dofa_assert_approved("Scheduling work order %s" % rec.name)
            vals = {"state": "scheduled"}
            if date:
                vals["scheduled_date"] = date
            rec._guarded().write(vals)
        return True

    def action_start(self):
        self._wo_require_state(("scheduled",), "be started")
        for rec in self:
            # an estimate raised after scheduling voided the approval
            rec._dofa_assert_approved("Starting work order %s" % rec.name)
            rec._guarded().write({"state": "in_progress"})
        return True

    def action_complete(self, notes=None):
        """Complete with evidence (BRU-FAC-07). An actual cost above the
        approved amount needs re-approval first."""
        self._wo_require_state(("in_progress",), "be completed")
        for rec in self:
            evidence = (notes or rec.completion_notes or "").strip()
            if not evidence:
                raise UserError(
                    "Record the completion evidence for %s: what was done and the evidence "
                    "reference (photos, service report, vendor job sheet)." % rec.name
                )
            rec._dofa_assert_approved("Completing work order %s" % rec.name)
            rec._guarded().write(
                {
                    "state": "completed",
                    "completion_notes": evidence,
                    "completed_by_id": self.env.uid,
                    "completed_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "facility.work_order_completed",
                "fix.facility.work.order",
                rec.id,
                {
                    "order": rec.name,
                    "site": rec.site_id.name,
                    "work_type": rec.work_type,
                    # the actual cost, never the estimate in its place (M47-7)
                    "cost": float(rec.actual_cost or 0.0),
                    "estimated_cost": float(rec.estimated_cost or 0.0),
                },
            )
        return True

    def action_verify(self, notes=None):
        """Branch verification closes the work order (BRU-FAC-07, §13 SoD):
        by someone who neither raised nor completed it."""
        self._wo_require_state(("completed",), "be verified")
        for rec in self:
            if not self.env.su and self.env.user in (rec.create_uid | rec.completed_by_id):
                raise UserError(
                    "Segregation of duties: %s was raised or completed by you; another person "
                    "verifies the work." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "verified",
                    "verified_by_id": self.env.uid,
                    "verified_at": fields.Datetime.now(),
                    "verification_notes": (notes or "").strip() or False,
                }
            )
        return True

    def action_reopen(self, reason=None):
        """Reopen a completed (not yet verified) work order. The completion is
        voided: its evidence and completer are cleared and a reopen event
        follows the completion event."""
        self._wo_require_state(("completed",), "be reopened")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("State why the work order is reopened.")
        for rec in self:
            previous = rec.completion_notes
            rec._guarded().write(
                {
                    "state": "in_progress",
                    "completion_notes": False,
                    "completed_by_id": False,
                    "completed_at": False,
                }
            )
            rec.message_post(
                body="Reopened by %s: %s. Voided completion evidence: %s"
                % (self.env.user.name, reason, previous or "-")
            )
            publish(
                self.env,
                "facility.work_order_reopened",
                "fix.facility.work.order",
                rec.id,
                {"order": rec.name, "site": rec.site_id.name, "reason": reason},
            )
        return True

    def action_cancel(self, reason=None):
        self._wo_require_state(WO_OPEN_STATES, "be cancelled")
        for rec in self:
            rec._approval_void("the work order was cancelled")
            rec._guarded().write({"state": "cancelled"})
            rec.message_post(
                body="Cancelled by %s%s"
                % (self.env.user.name, ": %s" % reason.strip() if (reason or "").strip() else ".")
            )
        return True
