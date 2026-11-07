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

# Site status changes (spec §8.1). Each transition is a routed M63 decision;
# the sign-offs it needs are taken in order, each by a different person who
# is neither the requester nor the creator.
#   planned   -> operational: readiness gate, Operations Director (BRU-FAC-04)
#   suspended -> operational: cause resolved, Operations Director (§8.1)
#   operational -> closed and closed -> planned (reopen): CFO then CEO.
# No CFO or CEO group exists, so the DOFA tier groups whose labels match are
# used: CFO = Tier 4 "CFO / CCO / COO", CEO = Tier 5 "Managing Director /
# Board" (P0). The Operations Director is the M47 role (P1).
SITE_STATUS_STAGES = {
    "opsdir": ("cd_facility.group_operations_director", "Operations Director"),
    "cfo": ("cd_entity_config.group_dofa_tier_4", "CFO (DOFA Tier 4)"),
    "ceo": ("cd_entity_config.group_dofa_tier_5", "CEO (DOFA Tier 5)"),
}
SITE_TRANSITION_STAGES = {
    "planned": ("opsdir",),
    "suspended": ("opsdir",),
    "active": ("cfo", "ceo"),
    "closed": ("cfo", "ceo"),
}
SITE_STATUS_STAMPS = (
    "status_opsdir_approved_by_id",
    "status_opsdir_approved_at",
    "status_cfo_approved_by_id",
    "status_cfo_approved_at",
    "status_ceo_approved_by_id",
    "status_ceo_approved_at",
)
SITE_SIGNERS = (
    "status_opsdir_approved_by_id",
    "status_cfo_approved_by_id",
    "status_ceo_approved_by_id",
)
# BRU-FAC-15 recovery checklist: what a closing site must have settled when
# it still holds an active lease, an open work order or a valid licence.
CLOSURE_CHECKLIST = (
    "closure_assets_recovered",
    "closure_licences_surrendered",
    "closure_deposit_settled",
    "closure_notes",
)
# BRU-FAC-04 readiness gate (§8.1: lease, trade licence, fire licence, power,
# connectivity, safety equipment, security, equipment complement, signage).
# The lease, licences and safety equipment are read from their registers;
# the rest are attested by the requester and pinned by the sign-off.
READINESS_ATTESTED = (
    "ready_power",
    "ready_connectivity",
    "ready_security",
    "ready_equipment",
    "ready_signage",
)
READINESS_PINNED = (
    *READINESS_ATTESTED,
    "readiness_notes",
    "accountable_manager_id",
    "occupancy_basis",
)
# §8.1 lists both licences in the readiness gate. Configurable because the
# licence set per local authority is confirmed at build time (Q-02).
READINESS_LICENCES_PARAM = "cd_facility.readiness_licence_types"
READINESS_LICENCES_DEFAULT = "trade,fire"

WO_OPEN_STATES = ("draft", "scheduled", "in_progress")
# Once the work is complete its cost and evidence are the record of what was
# done and spent: they are frozen (a reopen unfreezes them).
WO_COST_FROZEN_STATES = ("completed", "verified", "cancelled")
WO_FROZEN_FIELDS = ("estimated_cost", "actual_cost", "completion_notes")
WO_PERMIT_STAMPS = ("permit_approved_by_id", "permit_approved_at", "permit_valid_to")
WO_PERMIT_PINNED = ("high_risk", "hazard_type", "permit_precautions")
# A work order is raised where the site operates or must be repaired back into
# operation: fit-out work on a planned site is a site project, and a closed site
# has nothing left to maintain.
WO_SITE_STATES = ("active", "suspended")
# BRU-FAC-08 / FR-FAC-032: the priority a request is triaged to.
WO_PRIORITIES = [
    ("emergency", "Emergency (safety-critical)"),
    ("high", "High"),
    ("normal", "Normal"),
    ("low", "Low"),
]


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
    # obligations needs the recovery checklist.
    # A07 P1 (2026-11-04) M47-5/BRU-FAC-04: a new site is born Planned and
    # becomes operational only through the readiness gate, signed off by the
    # Operations Director; a licence lapse can suspend it (named decision on
    # the risk exception), and it resumes only with the Operations Director.
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
        [
            ("planned", "Planned / Fitting Out"),
            ("active", "Operational"),
            ("suspended", "Suspended"),
            ("closed", "Closed"),
        ],
        default="planned",
        required=True,
        tracking=True,
    )
    # BRU-FAC-06: exactly one accountable manager per site.
    accountable_manager_id = fields.Many2one(
        "res.users",
        string="Accountable Manager",
        tracking=True,
        help="The one person accountable for the site's facility and compliance matters "
        "(BRU-FAC-06). Required by the readiness gate.",
    )
    occupancy_basis = fields.Selection(
        [("leased", "Leased"), ("owned", "Owned"), ("licensed", "Licensed")],
        default="leased",
        required=True,
        help="A leased or licensed site needs an active lease to pass the readiness gate.",
    )
    ready_power = fields.Boolean(string="Power Connected")
    ready_connectivity = fields.Boolean(string="Connectivity Live")
    ready_security = fields.Boolean(string="Security Arrangements in Place")
    ready_equipment = fields.Boolean(string="Equipment Complement Installed (M45)")
    ready_signage = fields.Boolean(string="Signage Installed / Permitted")
    readiness_notes = fields.Text(
        string="Readiness Evidence", help="References for the attested readiness items"
    )
    opened_on = fields.Date(string="Operational Since", readonly=True, copy=False)
    suspended_reason = fields.Char(string="Suspension Reason", readonly=True, copy=False)
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
    status_opsdir_approved_by_id = fields.Many2one(
        "res.users", string="Status Change: Operations Director", readonly=True, copy=False
    )
    status_opsdir_approved_at = fields.Datetime(
        string="Operations Director Signed At", readonly=True, copy=False
    )
    status_cfo_approved_by_id = fields.Many2one(
        "res.users", string="Status Change: CFO Sign-off", readonly=True, copy=False
    )
    status_cfo_approved_at = fields.Datetime(string="CFO Signed At", readonly=True, copy=False)
    status_ceo_approved_by_id = fields.Many2one(
        "res.users", string="Status Change: CEO Sign-off", readonly=True, copy=False
    )
    status_ceo_approved_at = fields.Datetime(string="CEO Signed At", readonly=True, copy=False)
    # A07 operability (2026-11-07): a site suspended over a lapsed licence could
    # neither resume (the lapse blocks it) nor close (only an operational site
    # closed), so leaving the premises dead-ended. This says the suspended site's
    # pending status change is a closure, signed by the CFO and then the CEO.
    closure_requested = fields.Boolean(
        string="Closure Requested",
        readonly=True,
        copy=False,
        help="This suspended site is being closed rather than resumed",
    )

    def _fix_guarded_fields(self) -> set:
        return (
            super()._fix_guarded_fields()
            | {"state", "opened_on", "suspended_reason", "closure_requested"}
            | set(SITE_STATUS_STAMPS)
        )

    def write(self, vals):
        # The sign-offs are given on the checklist as it then read (the
        # approval's pin): changing the closure checklist or the readiness
        # attestations afterwards voids them, so the approvers always saw
        # what is executed.
        voided = self.browse()
        pinned = set(CLOSURE_CHECKLIST) | set(READINESS_PINNED)
        if not self._fix_guard_has_token() and pinned & set(vals):
            checklist = {k: vals[k] for k in pinned if k in vals}
            voided = self.filtered(
                lambda r: (
                    (r.approval_state in ("pending", "approved") or any(r[f] for f in SITE_SIGNERS))
                    and _changes(r, checklist)
                )
            )
        result = super().write(vals)
        if voided:
            voided._site_void_status_approval("the checklist changed after sign-off")
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

    # ---- status-change approval -------------------------------------------
    def _site_transition_stages(self):
        """The sign-offs the next status change needs, in order."""
        self.ensure_one()
        if self.state == "suspended" and self.closure_requested:
            return SITE_TRANSITION_STAGES["active"]
        return SITE_TRANSITION_STAGES.get(self.state, ())

    def _site_stage(self):
        """The sign-off the next status change still needs, or None."""
        self.ensure_one()
        for stage in self._site_transition_stages():
            if not self["status_%s_approved_by_id" % stage]:
                return stage
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
        # an earlier signatory is not also the next signature
        signed = self.env["res.users"]
        for name in SITE_SIGNERS:
            signed |= self[name]
        return super()._approval_excluded() | signed.sudo()

    def _approval_needed(self) -> bool:
        return self.state in SITE_TRANSITION_STAGES and bool(self._site_stage())

    def _approval_on_rejected(self, comment):
        self._site_void_status_approval("the status change was rejected: %s" % (comment or ""))

    def _site_void_status_approval(self, reason):
        # a service write: it also runs in the env of a rejecting approver
        for rec in self.sudo():
            if any(rec[f] for f in SITE_STATUS_STAMPS) or rec.approval_state != "none":
                rec._guarded().write(
                    {**dict.fromkeys(SITE_STATUS_STAMPS, False), "closure_requested": False}
                )
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

    @api.model
    def _readiness_licence_types(self) -> list:
        raw = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(READINESS_LICENCES_PARAM, READINESS_LICENCES_DEFAULT)
        )
        return [t.strip() for t in (raw or "").split(",") if t.strip()]

    def _site_readiness_items(self) -> list:
        """The readiness-gate items still outstanding (BRU-FAC-04). Empty = pass."""
        self.ensure_one()
        env = self.env
        out = []
        if not self.accountable_manager_id:
            out.append("an accountable manager (BRU-FAC-06)")
        if self.occupancy_basis != "owned" and not env["fix.site.lease"].sudo().search_count(
            [("site_id", "=", self.id), ("state", "=", "active")]
        ):
            out.append("an active lease")
        licences = env["fix.site.licence"].sudo().search([("site_id", "=", self.id)])
        labels = dict(env["fix.site.licence"]._fields["licence_type"].selection)
        for ltype in self._readiness_licence_types():
            if not licences.filtered(lambda ln, t=ltype: ln.licence_type == t and ln.is_valid):
                out.append("a current %s" % labels.get(ltype, ltype).lower())
        safety = env["fix.site.safety"].sudo().search([("site_id", "=", self.id)])
        if not safety:
            out.append("safety equipment on the register")
        elif safety.filtered(lambda s: s.state in ("overdue", "unfit")):
            out.append("no overdue or unfit safety equipment")
        for name in READINESS_ATTESTED:
            if not self[name]:
                out.append(self._fields[name].string.lower())
        return out

    def _site_check_ready(self):
        for rec in self:
            items = rec._site_readiness_items()
            if items:
                raise UserError(
                    "%s has not passed the readiness gate (BRU-FAC-04). Outstanding: %s."
                    % (rec.name, "; ".join(items))
                )

    def _site_open_exceptions(self):
        return (
            self.env["fix.site.risk.exception"]
            .sudo()
            .search([("site_id", "in", self.ids), ("state", "in", ("open", "continue", "suspend"))])
        )

    def _site_check_resumable(self):
        for rec in self:
            open_ex = rec._site_open_exceptions()
            if open_ex:
                raise UserError(
                    "%s cannot resume while its operating-risk exception(s) %s are unresolved: "
                    "record the renewed licence first."
                    % (rec.name, ", ".join(open_ex.mapped("name")))
                )

    def _site_require_lead(self, what):
        if not self.env.su and not self.env.user.has_group(
            "cd_facility.group_branch_operations_lead"
        ):
            raise UserError("%s is requested by a Branch Operations Lead." % what)

    def action_request_approval(self, justification=None):
        """Route the next status change for its sign-off(s): the readiness
        gate or a resumption (Operations Director), a closure or a reopening
        (CFO, then CEO)."""
        for rec in self:
            if rec.state == "planned":
                rec._site_require_lead("The readiness gate")
                rec._site_check_ready()
            elif rec.state == "suspended" and rec.closure_requested:
                rec._site_check_closable()
            elif rec.state == "suspended":
                rec._site_require_lead("Resuming a suspended site")
                rec._site_check_resumable()
            elif rec.state == "active":
                rec._site_check_closable()
        return super().action_request_approval(justification=justification)

    def action_request_closure(self, justification=None):
        """Route the closure of an operational or suspended site (CFO, then
        CEO; request once for each). A suspended site's lapse does not block
        this: leaving the premises is how it ends."""
        for rec in self:
            if rec.state not in ("active", "suspended"):
                raise UserError("Only an operational or a suspended site can be closed.")
            if rec.state == "suspended" and not rec.closure_requested:
                # an Operations Director's sign-off to resume is not for this
                rec._guarded().write(
                    {
                        "closure_requested": True,
                        "status_opsdir_approved_by_id": False,
                        "status_opsdir_approved_at": False,
                    }
                )
        return self.action_request_approval(justification=justification)

    def action_recall_approval(self):
        """A recalled closure gives a suspended site back its resumption,
        unless a signatory has already signed the closure."""
        result = super().action_recall_approval()
        self.filtered(
            lambda r: r.closure_requested and not r.status_cfo_approved_by_id
        )._guarded().write({"closure_requested": False})
        return result

    def action_approve_status_change(self):
        """The M63 apply method: one sign-off per inbox decision, in order.
        A direct press is refused (_approval_assert_routed)."""
        self._approval_assert_routed()
        # Superuser code with no deciding task (data loading, service calls).
        trusted = self.env.su and not self._approval_task()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        now = fields.Datetime.now()
        what = {
            "planned": "readiness gate",
            "suspended": "resumption",
            "active": "closure",
            "closed": "reopening",
        }
        for rec in self:
            stage = rec._site_stage()
            if not stage:
                raise UserError("%s has no status change awaiting sign-off." % rec.name)
            group, label = SITE_STATUS_STAGES[stage]
            if not trusted:
                if not authority.has_group(group):
                    raise UserError(
                        "Signing off a site status change as %s requires that authority, which "
                        "%s does not hold." % (label, authority.name)
                    )
                requester = rec.approval_request_id.sudo().requested_by_id
                signed = rec.env["res.users"]
                for name in SITE_SIGNERS:
                    signed |= rec[name]
                if acting & (rec.create_uid | requester | signed):
                    raise UserError(
                        "Segregation of duties: the creator, the requester and an earlier "
                        "signatory cannot sign off this site status change."
                    )
            # stamped as a service after the checks above: the CFO and CEO
            # sign without holding an M47 write right on the site
            rec.sudo()._guarded().write(
                {
                    "status_%s_approved_by_id" % stage: self.env.uid,
                    "status_%s_approved_at" % stage: now,
                }
            )
            rec.sudo().message_post(
                body="%s sign-off for the %s recorded by %s."
                % (label, what.get(rec.state, "status change"), self.env.user.name)
            )
        return True

    def _site_assert_status_approved(self, what):
        for rec in self:
            stage = rec._site_stage()
            if stage:
                raise UserError(
                    "%s %s needs the %s sign-off. Use Request Approval: the approval engine "
                    "routes it to the signatories in turn."
                    % (
                        what,
                        rec.name,
                        " then ".join(
                            SITE_STATUS_STAGES[s][1] for s in rec._site_transition_stages()
                        ),
                    )
                )

    def _site_consume_status_approval(self):
        self._guarded().write(
            {
                **dict.fromkeys(SITE_STATUS_STAMPS, False),
                "approval_state": "none",
                "closure_requested": False,
            }
        )

    def _site_status_event(self, before, reason=None, approver=None):
        for rec in self:
            publish(
                self.env,
                "site.status_changed",
                "fix.site",
                rec.id,
                {
                    "site": rec.name,
                    "site_id": rec.id,
                    "company_id": rec.company_id.id,
                    "from_status": before,
                    "to_status": rec.state,
                    "reason": reason or None,
                    "approver": approver or None,
                },
            )

    def action_open(self):
        """Readiness gate passed: the site becomes operational (BRU-FAC-04)."""
        for rec in self:
            if rec.state != "planned":
                raise UserError("Only a planned site passes the readiness gate.")
            rec._site_check_ready()
            rec._site_assert_status_approved("Opening")
            signatory = rec.status_opsdir_approved_by_id.name
            rec._guarded().write({"state": "active", "opened_on": fields.Date.context_today(rec)})
            rec._site_consume_status_approval()
            rec.message_post(body="Readiness gate passed; site operational (%s)." % signatory)
            publish(
                self.env,
                "site.readiness_gate_passed",
                "fix.site",
                rec.id,
                {
                    "site": rec.name,
                    "site_id": rec.id,
                    "signatory": signatory,
                    "accountable_manager": rec.accountable_manager_id.name,
                    "checklist": [rec._fields[n].string for n in READINESS_ATTESTED],
                    "outstanding": [],
                },
            )
            rec._site_status_event("planned", "readiness gate passed", signatory)
        return True

    def _site_suspend(self, reason, decided_by):
        """Suspend an operational site on a named decision (the risk
        exception's suspend decision). Not a button of its own."""
        for rec in self:
            if rec.state != "active":
                raise UserError(
                    "Only an operational site can be suspended (%s is %s)." % (rec.name, rec.state)
                )
            rec._site_void_status_approval("the site was suspended")
            rec._guarded().write({"state": "suspended", "suspended_reason": reason})
            rec.message_post(body="Site suspended by %s: %s." % (decided_by.name, reason))
            rec._site_status_event("active", reason, decided_by.name)
        return True

    def action_resume(self):
        """A suspended site resumes once the cause is resolved, on the
        Operations Director's routed sign-off (§8.1)."""
        for rec in self:
            if rec.state != "suspended":
                raise UserError("Only a suspended site can resume.")
            rec._site_check_resumable()
            rec._site_assert_status_approved("Resuming")
            signatory = rec.status_opsdir_approved_by_id.name
            rec._guarded().write({"state": "active", "suspended_reason": False})
            rec._site_consume_status_approval()
            rec.message_post(body="Site resumed (%s)." % signatory)
            rec._site_status_event("suspended", "cause resolved and re-verified", signatory)
        return True

    def action_close(self):
        for rec in self:
            if rec.state not in ("active", "suspended"):
                raise UserError("Only an operational or a suspended site can be closed.")
            before = rec.state
            if before == "suspended" and not rec.closure_requested:
                raise UserError(
                    "%s is suspended: use Request Closure Approval to close it." % rec.name
                )
            rec._site_check_closable()
            rec._site_assert_status_approved("Closing")
            open_items = rec._site_open_items()
            approver = rec.status_ceo_approved_by_id.name
            rec._guarded().write({"state": "closed", "suspended_reason": False})
            rec._site_consume_status_approval()
            # a closed site operates on no licence: nothing is left to decide
            rec._site_open_exceptions()._exception_resolve(
                "the site was closed by %s" % self.env.user.name
            )
            rec.message_post(
                body="Site closed by %s.%s"
                % (
                    self.env.user.name,
                    " Closed under the recovery checklist with %s." % ", ".join(open_items)
                    if open_items
                    else "",
                )
            )
            rec._site_status_event(before, "closure approved", approver)
        return True

    def action_reopen(self):
        """A closed site reopens into Planned: it passes the readiness gate
        again before it operates."""
        for rec in self:
            if rec.state != "closed":
                raise UserError("Only a closed site can be reopened.")
            rec._site_assert_status_approved("Reopening")
            approver = rec.status_ceo_approved_by_id.name
            # a reopened site starts any later closure with a fresh checklist
            rec._guarded().write(
                {
                    "state": "planned",
                    "opened_on": False,
                    "closure_assets_recovered": False,
                    "closure_licences_surrendered": False,
                    "closure_deposit_settled": False,
                }
            )
            rec._site_consume_status_approval()
            rec.message_post(
                body="Site reopened by %s; it operates again after the readiness gate."
                % self.env.user.name
            )
            rec._site_status_event("closed", "reopening approved", approver)
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
    # A07 P1 (2026-11-04) M47-7 / FR-FAC-033: who does the work. A vendor job
    # names the vendor before it is scheduled, and its invoice reference is
    # captured at verification for M52 (AUT-FAC-09).
    assigned_type = fields.Selection(
        [("internal", "Internal"), ("vendor", "Approved Vendor")],
        string="Assigned To",
        default="internal",
        required=True,
    )
    vendor_id = fields.Many2one("res.partner", string="Vendor", index=True)
    invoice_ref = fields.Char(
        string="Vendor Invoice Ref", copy=False, help="Routed to M52 with the cost at verification"
    )
    pm_id = fields.Many2one(
        "fix.site.pm", string="Raised by PM", readonly=True, copy=False, ondelete="set null"
    )
    # A07 P2 (2026-11-04): permit to work for high-risk jobs (hot work,
    # electrical isolation, work at height, confined space). A high-risk job
    # does not start without a permit approved by a Facility Manager who
    # neither raised the job nor does it, and valid on the start date.
    high_risk = fields.Boolean(string="High-Risk Job (Permit to Work)")
    hazard_type = fields.Selection(
        [
            ("hot_work", "Hot Work"),
            ("electrical", "Electrical Isolation"),
            ("height", "Work at Height"),
            ("confined_space", "Confined Space"),
            ("other", "Other"),
        ],
        string="Hazard",
    )
    permit_precautions = fields.Text(
        string="Permit Precautions", help="Isolation, PPE, fire watch, rescue arrangements"
    )
    permit_approved_by_id = fields.Many2one(
        "res.users", string="Permit Approved By", readonly=True, copy=False
    )
    permit_approved_at = fields.Datetime(string="Permit Approved At", readonly=True, copy=False)
    permit_valid_to = fields.Date(string="Permit Valid To", readonly=True, copy=False)
    # A07 operability (2026-11-07) BRU-FAC-08 / FR-FAC-032: a request is triaged
    # to a priority by a Facility Manager before it is approved or scheduled. A
    # state was not added: triage is a fact about a draft, not a step after it.
    priority = fields.Selection(WO_PRIORITIES, string="Priority", readonly=True, copy=False)
    triaged_by_id = fields.Many2one("res.users", string="Triaged By", readonly=True, copy=False)
    triaged_on = fields.Datetime(string="Triaged On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "priority",
            "triaged_by_id",
            "triaged_on",
            "state",
            "completed_by_id",
            "completed_at",
            "verified_by_id",
            "verified_at",
            "verification_notes",
            "pm_id",
            *WO_PERMIT_STAMPS,
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
            if self.state in ("verified", "cancelled"):
                locked.add("invoice_ref")
        return locked

    def _wo_check_site_open(self, site_ids):
        """Superuser code decides for itself (the PM job and the spine check it)."""
        if self._fix_guard_open():
            return
        for site in self.env["fix.site"].sudo().browse(site_ids):
            if site.state not in WO_SITE_STATES:
                raise UserError(
                    "%s is %s: a work order is raised on an operational or a suspended site."
                    % (site.name, dict(site._fields["state"].selection)[site.state])
                )

    def _wo_person_raised(self) -> bool:
        """Raised by a person, not by a source's own routing."""
        self.ensure_one()
        return not self.pm_id

    def _wo_assert_triaged(self):
        for rec in self:
            if not rec.priority and rec._wo_person_raised():
                raise UserError(
                    "Triage %s first: a Facility Manager gives it its priority (BRU-FAC-08)."
                    % rec.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        # A person's request is triaged by a Facility Manager. What the system
        # raises (the PM job, the spine's routing) is born triaged at normal.
        system = self._fix_guard_open()
        now = fields.Datetime.now()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.facility.work.order")
                    or f"FWO/{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
            if system and not vals.get("priority"):
                vals.update(priority="normal", triaged_on=now)
        self._wo_check_site_open({v["site_id"] for v in vals_list if v.get("site_id")})
        records = super().create(vals_list)
        for rec in records:
            publish(
                self.env,
                "facility.work_order_raised",
                "fix.facility.work.order",
                rec.id,
                {
                    "order": rec.name,
                    "site": rec.site_id.name,
                    "site_id": rec.site_id.id,
                    "work_type": rec.work_type,
                    "high_risk": bool(rec.high_risk),
                    "estimated_cost": float(rec.estimated_cost or 0.0),
                    "source": "pm" if rec.pm_id else "request",
                },
            )
        return records

    def write(self, vals):
        voided_permit = self.browse()
        if self and not self._fix_guard_open():
            # the permit is approved for the hazard and precautions as written
            permit = {k: vals[k] for k in WO_PERMIT_PINNED if k in vals}
            if permit:
                voided_permit = self.filtered(
                    lambda r: r.permit_approved_by_id and _changes(r, permit)
                )
                if (
                    "high_risk" in vals
                    and not vals["high_risk"]
                    and self.filtered(lambda r: r.high_risk)
                    and not self.env.user.has_group("cd_facility.group_facility_manager")
                ):
                    raise UserError(
                        "Only a Facility Manager may take the permit-to-work requirement "
                        "off a high-risk job."
                    )
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
            if vals.get("site_id") and _changes(self, {"site_id": vals["site_id"]}):
                self._wo_check_site_open({vals["site_id"]})
        result = super().write(vals)
        if voided_permit:
            voided_permit._guarded().write(dict.fromkeys(WO_PERMIT_STAMPS, False))
            for rec in voided_permit:
                rec.message_post(
                    body="Permit to work withdrawn: its hazard or precautions changed."
                )
        return result

    def _wo_require_state(self, allowed, what):
        for rec in self:
            if rec.state not in allowed:
                labels = dict(self._fields["state"].selection)
                raise UserError(
                    "%s cannot %s: it is %s (allowed from %s)."
                    % (rec.name, what, labels[rec.state], ", ".join(labels[s] for s in allowed))
                )

    def _wo_require_manager(self, what):
        if not self.env.su and not self.env.user.has_group("cd_facility.group_facility_manager"):
            raise UserError("%s is done by a Facility Manager." % what)

    def action_triage(self, priority=None):
        """Give an open request its priority (BRU-FAC-08). Done again, it
        changes the priority and records who changed it."""
        self._wo_require_manager("Triage")
        self._wo_require_state(WO_OPEN_STATES, "be triaged")
        wanted = (priority or "").strip().lower()
        if wanted not in dict(WO_PRIORITIES):
            raise UserError("Give the priority: emergency, high, normal or low.")
        for rec in self:
            rec._guarded().write(
                {
                    "priority": wanted,
                    "triaged_by_id": self.env.uid,
                    "triaged_on": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Triaged as %s by %s." % (wanted, self.env.user.name))
        return True

    def action_request_approval(self, justification=None):
        """Route the repair spend for its DOFA tier (before scheduling, and
        again when the actual cost passes what was approved)."""
        self._wo_require_state(WO_OPEN_STATES, "have its spend approved")
        self._wo_assert_triaged()
        for rec in self:
            _refuse_if_covered(rec)
        return super().action_request_approval(justification=justification)

    def action_schedule(self, date=None):
        self._wo_require_state(("draft",), "be scheduled")
        self._wo_assert_triaged()
        for rec in self:
            if rec.assigned_type == "vendor" and not rec.vendor_id:
                raise UserError(
                    "Name the vendor of %s before it is scheduled (FR-FAC-033)." % rec.name
                )
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
            rec._wo_assert_permit()
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
        by a Facility Manager who neither raised nor completed it. The cost
        and the vendor invoice reference then go to M52 (AUT-FAC-09)."""
        self._wo_require_state(("completed",), "be verified")
        for rec in self:
            if not self.env.su:
                if not self.env.user.has_group("cd_facility.group_facility_manager"):
                    raise UserError(
                        "Branch verification of %s is done by a Facility Manager." % rec.name
                    )
                if self.env.user in (rec.create_uid | rec.completed_by_id):
                    raise UserError(
                        "Segregation of duties: %s was raised or completed by you; another "
                        "person verifies the work." % rec.name
                    )
            if (
                rec.assigned_type == "vendor"
                and rec.actual_cost
                and not (rec.invoice_ref or "").strip()
            ):
                raise UserError(
                    "Record the vendor invoice reference of %s before verifying it: the cost "
                    "goes to M52 against that invoice." % rec.name
                )
            # a costed job closed at 0 sends nothing to M52: that needs a reason
            if rec.estimated_cost and not rec.actual_cost and not (notes or "").strip():
                raise UserError(
                    "%s was estimated at %.2f but records no actual cost. Reopen it to record "
                    "the actual cost, or say in the verification note why the job cost nothing."
                    % (rec.name, rec.estimated_cost)
                )
            # what is closed is what was approved
            rec._dofa_assert_approved("Verifying work order %s" % rec.name)
            rec._guarded().write(
                {
                    "state": "verified",
                    "verified_by_id": self.env.uid,
                    "verified_at": fields.Datetime.now(),
                    "verification_notes": (notes or "").strip() or False,
                }
            )
            # BRU-FAC-20 / AUT-FAC-09: the cost hand-off to M52 (the bridge
            # consumes it); the actual cost, never the estimate in its place.
            publish(
                self.env,
                "facility.work_order_closed",
                "fix.facility.work.order",
                rec.id,
                {
                    "order": rec.name,
                    "site": rec.site_id.name,
                    "site_id": rec.site_id.id,
                    "company_id": rec.company_id.id,
                    "work_type": rec.work_type,
                    "assigned_type": rec.assigned_type,
                    "vendor_id": rec.vendor_id.id or None,
                    "vendor": rec.vendor_id.name or None,
                    "cost": float(rec.actual_cost or 0.0),
                    "estimated_cost": float(rec.estimated_cost or 0.0),
                    "currency": rec.currency_id.name,
                    "invoice_ref": rec.invoice_ref or None,
                    "verified_by": self.env.user.name,
                    "completed_at": fields.Datetime.to_string(rec.completed_at),
                    "verified_at": fields.Datetime.to_string(rec.verified_at),
                },
            )
        return True

    # ---- permit to work ----------------------------------------------------
    def _wo_assert_permit(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if not rec.high_risk:
                continue
            if not rec.permit_approved_by_id or not rec.permit_valid_to:
                raise UserError(
                    "%s is a high-risk job: it starts only under an approved permit to work."
                    % rec.name
                )
            if rec.permit_valid_to < today:
                raise UserError(
                    "The permit to work of %s expired on %s: approve a new one."
                    % (rec.name, rec.permit_valid_to)
                )

    def action_approve_permit(self, valid_to=None):
        """Approve the permit to work for a high-risk job. Valid for the day
        unless a later date is given; no permit period is invented."""
        today = fields.Date.context_today(self)
        try:
            until = fields.Date.to_date(valid_to) if valid_to else today
        except ValueError as exc:
            raise UserError("Permit end date %r is not a date (YYYY-MM-DD)." % valid_to) from exc
        if until < today:
            raise UserError("A permit to work cannot end before today.")
        for rec in self:
            if not rec.high_risk:
                raise UserError("%s is not marked high-risk: no permit is needed." % rec.name)
            if rec.state not in WO_OPEN_STATES:
                raise UserError("A permit is approved for open work only.")
            if not rec.hazard_type or not (rec.permit_precautions or "").strip():
                raise UserError(
                    "Record the hazard and the precautions of %s before its permit is approved."
                    % rec.name
                )
            if not self.env.su:
                if not self.env.user.has_group("cd_facility.group_facility_manager"):
                    raise UserError("A permit to work is approved by a Facility Manager.")
                doer = rec.assigned_to.sudo().user_id
                if self.env.user in (rec.create_uid | doer):
                    raise UserError(
                        "Segregation of duties: the raiser or the assigned engineer of %s does "
                        "not approve its permit to work." % rec.name
                    )
            rec._guarded().write(
                {
                    "permit_approved_by_id": self.env.uid,
                    "permit_approved_at": fields.Datetime.now(),
                    "permit_valid_to": until,
                }
            )
            rec.message_post(
                body="Permit to work approved by %s until %s." % (self.env.user.name, until)
            )
        return True

    def action_reopen(self, reason=None):
        """Reopen a completed (not yet verified) work order. The completion is
        voided: its evidence and completer are cleared and a reopen event
        follows the completion event."""
        self._wo_require_manager("Reopening a work order")
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
        self._wo_require_manager("Cancelling a work order")
        self._wo_require_state(WO_OPEN_STATES, "be cancelled")
        for rec in self:
            rec._approval_void("the work order was cancelled")
            rec._guarded().write({"state": "cancelled"})
            rec.message_post(
                body="Cancelled by %s%s"
                % (self.env.user.name, ": %s" % reason.strip() if (reason or "").strip() else ".")
            )
        return True
