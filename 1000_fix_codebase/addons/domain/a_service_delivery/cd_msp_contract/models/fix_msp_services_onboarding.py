# fix_msp_services_onboarding — M05 sub-module 10 "Onboarding Projects"
# (capture audit pass 2, 2026-11-18).
#
# FR-RMS-047 (P1) and the client-onboarding lifecycle (spec §8.3): a signed
# MSP contract is onboarded through a structured project - estate discovery,
# agent deployment, baseline capture, contact registration, portal access,
# runbook authoring, alert threshold tuning and SLA configuration - and goes
# live only when the agreed share of its estate is reporting. SLA clocks are
# contractually binding from that moment, not before. The page's button used
# to open the MSP contract itself: no record held the project, its steps or
# the go-live.
#
# FR-RMS-048: offboarding also returns the client's data, evidenced, before it
# completes (agent removal and access revocation were already enforced).
#
# FILE NAME IS LOAD-BEARING: sorts (and so imports) after fix_msp_services,
# whose client contacts a step checks, and after fix_msp_rules_bru, whose
# SLA measure the go-live narrows.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .msp_roles import GROUP_ENGINEER, require_role

EVIDENCE_MIN = 10
# BRU-RMS-04: an agent silent this long is a coverage gap (fix_msp_rules)
REPORTING_HOURS = 24

# spec §8.3 ESTATE ONBOARDING, in the order the work is done
ONBOARDING_STEPS = [
    ("discovery", "Estate discovery", "What was found on the client network and reconciled."),
    ("agents", "Agent deployment", "At least one asset is enrolled on the contract."),
    ("baseline", "Baseline capture", "Every enrolled asset has a first reading."),
    ("contacts", "Contact registration", "A client contact may raise tickets."),
    ("portal", "Client portal access", "Who at the client was given portal access, and what."),
    ("runbooks", "Runbook authoring", "An active runbook covers this contract."),
    ("alerts", "Alert threshold tuning", "An active alert rule watches this contract's estate."),
    ("sla", "SLA configuration", "The SLA target and coverage window are set on the contract."),
]


def _evidence(value, what):
    value = (value or "").strip()
    if len(value) < EVIDENCE_MIN:
        raise UserError("Write the evidence of %s (at least %d characters)." % (what, EVIDENCE_MIN))
    return value


class FixMspOnboarding(models.Model):
    """The onboarding project of one MSP contract (FR-RMS-047)."""

    _name = "fix.msp.onboarding"
    _description = "MSP Client Onboarding Project"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "started_by_id",
            "live_at",
            "live_by_id",
            "live_coverage_pct",
        }

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Onboarding Project", required=True)
    msp_contract_id = fields.Many2one(
        "fix.msp.contract", string="MSP Contract", required=True, index=True, ondelete="restrict"
    )
    kickoff_date = fields.Date(string="Kick-off", required=True, default=fields.Date.today)
    target_live_date = fields.Date(string="Target Go-Live")
    coverage_target_pct = fields.Float(
        string="Coverage Needed to Go Live (%)",
        required=True,
        default=95.0,
        tracking=True,
        help="Share of the covered devices whose agent must be reporting before the "
        "service goes live (spec §8.3).",
    )
    notes = fields.Text(string="Scope & Notes")
    step_ids = fields.One2many("fix.msp.onboarding.step", "onboarding_id", string="Checklist")
    state = fields.Selection(
        [
            ("initiated", "Onboarding Initiated"),
            ("onboarding", "Estate Onboarding"),
            ("live", "Service Live"),
        ],
        default="initiated",
        required=True,
        tracking=True,
    )
    started_by_id = fields.Many2one(
        "res.users", string="Started By", default=lambda self: self.env.user, readonly=True
    )
    step_count = fields.Integer(compute="_compute_progress", string="Steps")
    step_done_count = fields.Integer(compute="_compute_progress", string="Steps Done")
    covered_count = fields.Integer(compute="_compute_coverage", string="Covered Devices")
    reporting_count = fields.Integer(compute="_compute_coverage", string="Agents Reporting")
    coverage_pct = fields.Float(compute="_compute_coverage", string="Coverage Now (%)")
    live_at = fields.Datetime(string="Service Live Since", readonly=True, copy=False)
    live_by_id = fields.Many2one("res.users", string="Taken Live By", readonly=True, copy=False)
    live_coverage_pct = fields.Float(string="Coverage at Go-Live (%)", readonly=True, copy=False)

    _contract_unique = models.Constraint(
        "unique(msp_contract_id)", "An MSP contract has one onboarding project."
    )

    @api.depends("step_ids.done")
    def _compute_progress(self):
        for project in self:
            project.step_count = len(project.step_ids)
            project.step_done_count = len(project.step_ids.filtered("done"))

    def _compute_coverage(self):
        # not stored: "reporting" moves with the clock, never with a write
        cutoff = fields.Datetime.now() - timedelta(hours=REPORTING_HOURS)
        for project in self:
            msp = project.msp_contract_id
            assets = msp.asset_ids.filtered(lambda a: not a.agent_removed_at)
            reporting = assets.filtered(lambda a: a.last_seen and a.last_seen >= cutoff)
            covered = msp.device_count or len(assets)
            project.covered_count = covered
            project.reporting_count = len(reporting)
            project.coverage_pct = round(100.0 * len(reporting) / covered, 1) if covered else 0.0

    @api.constrains("coverage_target_pct")
    def _check_coverage_target(self):
        for project in self:
            if not 0 < project.coverage_target_pct <= 100:
                raise ValidationError("The coverage needed to go live is between 1 and 100 %.")

    @api.constrains("kickoff_date", "target_live_date")
    def _check_dates(self):
        for project in self:
            if project.target_live_date and project.target_live_date < project.kickoff_date:
                raise ValidationError("The target go-live is on or after the kick-off.")

    @api.model_create_multi
    def create(self, vals_list):
        """Started by an engineer on an in-service contract that has not gone
        live; the §8.3 checklist comes with it."""
        require_role(self.env, [GROUP_ENGINEER], "Starting a client onboarding")
        contracts = self.env["fix.msp.contract"].browse(
            [v["msp_contract_id"] for v in vals_list if v.get("msp_contract_id")]
        )
        contracts._msp_assert_in_service("Starting an onboarding")
        for msp in contracts:
            if msp.service_live_at:
                raise UserError("MSP contract %s is already live." % msp.name)
            # A02 ERP audit M05-F2: an onboarding opened on a contract that is
            # already delivering service suspended its whole SLA. A contract
            # with an alert or a service report is in service: it is not
            # onboarded again, and its SLA clocks keep running.
            if msp._msp_service_history():
                raise UserError(
                    "MSP contract %s is already in service (it has alerts or service reports): "
                    "its SLA is binding and an onboarding project cannot suspend it." % msp.name
                )
        for vals in vals_list:
            if not vals.get("msp_contract_id"):
                continue
            msp = self.env["fix.msp.contract"].browse(vals["msp_contract_id"])
            # the project belongs where its contract does
            vals["company_id"] = msp.company_id.id
            if msp.operating_unit_id and not vals.get("operating_unit_id"):
                vals["operating_unit_id"] = msp.operating_unit_id.id
            if not vals.get("name"):
                vals["name"] = "Onboarding: %s" % msp.name
        projects = super().create(vals_list)
        steps = self.env["fix.msp.onboarding.step"]._guarded()
        for project in projects:
            steps.create(
                [
                    {
                        "onboarding_id": project.id,
                        "sequence": 10 * (i + 1),
                        "code": code,
                        "name": label,
                        "requirement": requirement,
                    }
                    for i, (code, label, requirement) in enumerate(ONBOARDING_STEPS)
                ]
            )
        return projects

    def write(self, vals):
        if "msp_contract_id" in vals and any(
            p.msp_contract_id.id != vals["msp_contract_id"] for p in self
        ):
            raise UserError("An onboarding project stays on the contract it was started for.")
        if not self._fix_guard_open() and any(p.state == "live" for p in self):
            frozen = set(vals) & {"coverage_target_pct", "kickoff_date", "target_live_date"}
            if frozen:
                raise UserError("The service is live: its onboarding is a closed record.")
        return super().write(vals)

    def unlink(self):
        if any(p.step_done_count or p.state == "live" for p in self):
            raise UserError("An onboarding with completed steps is evidence and is not deleted.")
        return super().unlink()

    def action_go_live(self):
        """SERVICE LIVE (spec §8.3): every checklist step done and the agreed
        share of the estate reporting. SLA clocks bind from this moment."""
        require_role(self.env, [GROUP_ENGINEER], "Taking an MSP service live")
        for project in self:
            if project.state == "live":
                raise UserError("%s is already live." % project.name)
            msp = project.msp_contract_id
            msp._msp_assert_in_service("Going live")
            msp._msp_assert_entitled("Going live")
            open_steps = project.step_ids.filtered(lambda s: not s.done)
            if open_steps:
                raise UserError(
                    "%s cannot go live: %s still to do."
                    % (
                        project.name,
                        ", ".join(open_steps.mapped("name")),
                    )
                )
            if project.coverage_pct < project.coverage_target_pct:
                raise UserError(
                    "%s cannot go live: %d of %d covered devices are reporting (%.1f %%), "
                    "%.1f %% is agreed. Deploy the missing agents first."
                    % (
                        project.name,
                        project.reporting_count,
                        project.covered_count,
                        project.coverage_pct,
                        project.coverage_target_pct,
                    )
                )
            now = fields.Datetime.now()
            project._guarded().write(
                {
                    "state": "live",
                    "live_at": now,
                    "live_by_id": self.env.uid,
                    "live_coverage_pct": project.coverage_pct,
                }
            )
            msp.sudo().write({"service_live_at": now})
            msp.message_post(
                body="Service live (%s): SLA clocks are contractually binding from now. "
                "Coverage %.1f %%." % (self.env.user.name, project.coverage_pct)
            )
        return True


class FixMspOnboardingStep(models.Model):
    """One step of the onboarding checklist. Done once, with its evidence;
    the steps the system can verify are verified when they are marked."""

    _name = "fix.msp.onboarding.step"
    _description = "MSP Onboarding Step"
    _inherit = ["fix.guarded.mixin"]
    _order = "onboarding_id, sequence, id"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "onboarding_id",
            "code",
            "name",
            "requirement",
            "done",
            "done_by_id",
            "done_at",
            "evidence",
        }

    onboarding_id = fields.Many2one(
        "fix.msp.onboarding", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="onboarding_id.company_id", store=True)
    operating_unit_id = fields.Many2one(related="onboarding_id.operating_unit_id", store=True)
    msp_contract_id = fields.Many2one(related="onboarding_id.msp_contract_id", store=True)
    sequence = fields.Integer(default=10)
    code = fields.Selection([(c, label) for c, label, _r in ONBOARDING_STEPS], required=True)
    name = fields.Char(string="Step", required=True)
    requirement = fields.Char(string="Done When")
    done = fields.Boolean(readonly=True)
    done_by_id = fields.Many2one("res.users", string="Done By", readonly=True)
    done_at = fields.Datetime(string="Done At", readonly=True)
    evidence = fields.Text(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError("The checklist comes with the onboarding project; steps are not added.")
        return super().create(vals_list)

    def unlink(self):
        if not self._fix_guard_open():
            raise UserError("A checklist step is not deleted.")
        return super().unlink()

    def _msp_unmet(self) -> str:
        """Why the system cannot accept this step yet ('' when it can)."""
        self.ensure_one()
        msp = self.onboarding_id.msp_contract_id
        assets = msp.asset_ids.filtered(lambda a: not a.agent_removed_at)
        if self.code == "agents" and not assets:
            return "no asset is enrolled on %s yet (Estate & Agents)" % msp.name
        if self.code == "baseline":
            if not assets:
                return "no asset is enrolled on %s yet" % msp.name
            unread = assets.filtered(lambda a: not a.last_seen)
            if unread:
                return "%s has no reading yet (Record a Health Reading, or its agent reports)" % (
                    ", ".join(unread.mapped(lambda a: a.hostname or a.agent_id))
                )
        if self.code == "contacts" and not msp.client_contact_ids.filtered(
            lambda c: c.active and c.can_raise_tickets
        ):
            return "no registered client contact of %s may raise tickets" % msp.name
        if self.code == "runbooks" and not self.env["fix.msp.runbook"].search_count(
            [("active", "=", True), ("scope_contract_id", "in", [False, msp.id])]
        ):
            return "no active runbook covers %s" % msp.name
        if self.code == "alerts" and not self.env["fix.msp.alert.rule"].search_count(
            [("active", "=", True), ("msp_contract_id", "in", [False, msp.id])]
        ):
            return "no active alert rule watches %s" % msp.name
        if self.code == "sla" and not (msp.sla_target_pct and msp.coverage_window):
            return "the SLA target of %s is not set" % msp.name
        return ""

    def action_mark_done(self, evidence=None):
        require_role(self.env, [GROUP_ENGINEER], "Completing an onboarding step")
        text = _evidence(evidence, "this onboarding step")
        for step in self:
            project = step.onboarding_id
            if project.state == "live":
                raise UserError("%s is live: its checklist is closed." % project.name)
            if step.done:
                raise UserError("'%s' is already done." % step.name)
            unmet = step._msp_unmet()
            if unmet:
                raise UserError("'%s' cannot be marked done: %s." % (step.name, unmet))
            step._guarded().write(
                {
                    "done": True,
                    "done_by_id": self.env.uid,
                    "done_at": fields.Datetime.now(),
                    "evidence": text,
                }
            )
            if project.state == "initiated":
                project._guarded().write({"state": "onboarding"})
            project.message_post(body="%s done (%s): %s" % (step.name, self.env.user.name, text))
        return True


class FixMspContractOnboarding(models.Model):
    _inherit = "fix.msp.contract"

    onboarding_ids = fields.One2many(
        "fix.msp.onboarding", "msp_contract_id", string="Onboarding Project"
    )
    service_live_at = fields.Datetime(
        string="Service Live Since",
        readonly=True,
        copy=False,
        tracking=True,
        help="Set when the onboarding project goes live: SLA clocks are contractually "
        "binding from this moment (spec §8.3).",
    )
    # FR-RMS-048 data return
    data_returned_at = fields.Datetime(string="Client Data Returned At", readonly=True, copy=False)
    data_return_evidence = fields.Text(string="Data Return Evidence", readonly=True, copy=False)

    def _msp_service_history(self, before=None) -> bool:
        """True when the contract delivered service (an alert or a service
        report) before ``before`` (default: ever)."""
        self.ensure_one()
        domain = [("msp_contract_id", "=", self.id)]
        if before:
            domain.append(("create_date", "<", before))
        return bool(
            self.env["fix.msp.alert"].sudo().search_count(domain, limit=1)
            or self.env["fix.msp.service.report"].sudo().search_count(domain, limit=1)
        )

    def _msp_onboarding_window(self):
        """(start, live) of the onboarding during which SLA clocks do not bind
        yet, or None when every alert binds.

        A02 ERP audit M05-F2: any onboarding project, even one opened on a
        contract already in service, suspended the contract's SLA until a
        go-live that never came. Only a genuine onboarding suspends it: a
        project opened before the contract delivered any service. Alerts
        raised from its start to the go-live are not measured; everything
        else is."""
        self.ensure_one()
        binds = self._msp_sla_binds_at()
        if not binds:
            return None
        project = self.onboarding_ids.sorted("id")[:1]
        # A02 ERP pass 2 (M05-S08): the window ends when the SLA binds
        return project.create_date, binds

    def _msp_period_sla(self, alerts, as_of=None) -> dict:
        """Alerts raised during a genuine onboarding (before go-live) are not
        measured: SLA clocks bind from go-live (spec §8.3). Every other alert
        is, so an onboarding project never suspends the SLA of a contract that
        is already in service."""
        self.ensure_one()
        # A02 ERP pass 2 (M05-S08, owner decision D9): the SLA binds at the
        # go-live, but never later than the target go-live date and never
        # later than 30 days from the contract start: an onboarding that never
        # went live suspended the SLA for ever.
        binds = self._msp_sla_binds_at()
        if binds:
            alerts = alerts.filtered(lambda a: a.create_date >= binds)
        return super()._msp_period_sla(alerts, as_of=as_of)

    def action_record_data_returned(self, evidence=None):
        """FR-RMS-048: what was handed back (or confirmed deleted) and how."""
        require_role(self.env, [GROUP_ENGINEER], "Recording the client's data return")
        text = _evidence(evidence, "the data return")
        for msp in self:
            if msp.lifecycle != "offboarding":
                raise UserError("Data is returned during offboarding: start it first.")
            msp._guarded().write(
                {"data_returned_at": fields.Datetime.now(), "data_return_evidence": text}
            )
            msp.message_post(body="Client data returned (%s): %s" % (self.env.user.name, text))
        return True

    def action_complete_offboarding(self):
        """Agents removed and access revoked (checked first, as before), then
        the data returned, each with its evidence (FR-RMS-048)."""
        for msp in self:
            ready = (
                msp.lifecycle == "offboarding"
                and msp.access_revoked_at
                and not msp.asset_ids.filtered(lambda a: not a.agent_removed_at)
            )
            if ready and not msp.data_returned_at:
                raise UserError(
                    "Offboarding of %s is not complete: record the return of the client's "
                    "data, with its evidence (FR-RMS-048)." % msp.name
                )
        return super().action_complete_offboarding()
