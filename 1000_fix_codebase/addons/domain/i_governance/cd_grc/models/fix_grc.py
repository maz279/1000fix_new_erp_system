# fix_grc — M60: Governance, Risk, Compliance & Assurance (P09-M08 & R07-M05).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

RISK_OWNER_GROUP = "cd_grc.group_grc_risk_owner"
OFFICER_GROUP = "cd_grc.group_grc_officer"
# A10 P1-5 (M60-7): who may accept a residual ABOVE the stated appetite —
# the Delegated Authority Owner (CFO), never the risk's own owner.
APPETITE_ACCEPTOR_GROUP = "cd_grc.group_grc_dofa_admin"

RISK_CATEGORIES = [
    ("strategic", "Strategic"),
    ("operational", "Operational (Service Delivery)"),
    ("financial", "Financial"),
    ("compliance", "Statutory & Regulatory Compliance"),
    ("cyber", "Cybersecurity & Data Protection (PDPA/ISO 27001)"),
    ("hse", "Health, Safety & Environment (BLA 2006)"),
]


def _require_group(env, group, why):
    """An A10 role gate; superuser code (crons, relay) is trusted."""
    if env.su:
        return
    if not env.user.has_group(group):
        raise UserError(why)


class FixRiskAppetite(models.Model):
    """M60: the stated risk appetite — the maximum residual score the board
    tolerates per category (A10 P1-5, M60-7). One statement per category per
    company; the Compliance Officer maintains it. An unstated category bounds
    nothing: no risk in it is 'above appetite', and the KPI says so."""

    _name = "fix.risk.appetite"
    _description = "Risk Appetite Statement"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "category"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    category = fields.Selection(RISK_CATEGORIES, required=True)
    max_residual_score = fields.Integer(
        string="Maximum Residual Score",
        required=True,
        help="The largest residual score (likelihood × impact, 1-25) accepted "
        "for this category without an above-appetite acceptance through M63.",
    )
    note = fields.Text(string="Appetite Statement")

    # Odoo 19: models.Constraint replaces the legacy _sql_constraints list
    _one_appetite_per_category = models.Constraint(
        "UNIQUE (company_id, category)",
        "One appetite statement per category and company (A10 P1-5).",
    )

    @api.constrains("max_residual_score")
    def _check_appetite_score(self):
        for rec in self:
            if not 1 <= rec.max_residual_score <= 25:
                raise ValidationError(
                    "The appetite is a residual score ceiling on the 1-25 scale "
                    "(likelihood × impact, each 1-5)."
                )


class FixRiskRegister(models.Model):
    """M60: Enterprise Risk Register with likelihood/impact matrix and residual risk tracking."""

    _name = "fix.risk.register"
    _description = "Risk Register Entry"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "risk_score desc, name"

    # A10 P1-5 (M60-7): an above-appetite residual acceptance is a routed M63
    # decision. The engine routes it to the Delegated Authority Owner (CFO)
    # group minus the requester/creator; the apply method is the acceptance
    # itself, which stamps the APPROVER as the acceptor.
    _approval_domain = "risk_acceptance"
    _approval_apply_method = "action_accept_residual"
    _approval_group = APPETITE_ACCEPTOR_GROUP

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Risk Description", required=True)
    category = fields.Selection(RISK_CATEGORIES, required=True, default="operational")
    likelihood = fields.Selection(
        [
            ("1", "Rare (1)"),
            ("2", "Unlikely (2)"),
            ("3", "Possible (3)"),
            ("4", "Likely (4)"),
            ("5", "Almost Certain (5)"),
        ],
        default="3",
        required=True,
    )
    impact = fields.Selection(
        [
            ("1", "Insignificant (1)"),
            ("2", "Minor (2)"),
            ("3", "Moderate (3)"),
            ("4", "Major (4)"),
            ("5", "Severe / Catastrophic (5)"),
        ],
        default="3",
        required=True,
    )
    risk_score = fields.Integer(string="Inherent Risk Score", compute="_compute_score", store=True)
    # --- residual risk (after the controls) ---------------------------------
    # GRC practice: inherent risk is what the register scores before controls;
    # residual risk is what remains once the linked controls operate, and a
    # residual above appetite needs an explicit, named acceptance.
    residual_likelihood = fields.Selection(
        [(str(i), str(i)) for i in range(1, 6)],
        string="Residual likelihood",
        help="1-5 after the linked controls are applied.",
    )
    residual_impact = fields.Selection(
        [(str(i), str(i)) for i in range(1, 6)],
        string="Residual impact",
    )
    residual_score = fields.Integer(compute="_compute_residual", store=True)
    residual_band = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        compute="_compute_residual",
        store=True,
    )
    residual_accepted_by_id = fields.Many2one("hr.employee", string="Residual accepted by")
    residual_accepted_on = fields.Date(string="Residual accepted on")
    # --- appetite (A10 P1-5, M60-7) ----------------------------------------
    # The stated appetite is the fix.risk.appetite row for the category; a
    # risk with no residual assessed yet is judged on its INHERENT score —
    # treating an unassessed residual as within appetite was the audit's
    # original sin (untested controls counted as effective).
    appetite_limit = fields.Integer(
        string="Category Appetite (max residual)",
        compute="_compute_appetite",
        help="The stated maximum residual score for this risk's category.",
    )
    appetite_stated = fields.Boolean(compute="_compute_appetite")
    above_appetite = fields.Boolean(
        string="Above Appetite",
        compute="_compute_appetite",
        help="True when the residual score (inherent, if not yet assessed) "
        "exceeds the appetite stated for the category. Accepting it is a "
        "routed M63 decision, not the owner's own signature.",
    )
    # A10 P1-5 (M60-8): a linked control whose latest test was not fully
    # effective — the flag the acceptance gate and the portal read.
    control_deficient = fields.Boolean(
        string="Deficient Control",
        compute="_compute_control_deficiency",
        store=True,
        help="True when a linked ACTIVE control's latest test was partially "
        "effective or ineffective.",
    )

    @api.depends("residual_likelihood", "residual_impact")
    def _compute_residual(self):
        for rec in self:
            lk = int(rec.residual_likelihood or 0)
            im = int(rec.residual_impact or 0)
            rec.residual_score = lk * im
            score = rec.residual_score
            rec.residual_band = (
                ("high" if score >= 15 else "medium" if score >= 8 else "low") if score else False
            )

    def _compute_appetite(self):
        Appetite = self.env["fix.risk.appetite"].sudo()
        for rec in self:
            row = Appetite.search(
                [("category", "=", rec.category), ("company_id", "=", rec.company_id.id)], limit=1
            )
            rec.appetite_limit = row.max_residual_score if row else 0
            rec.appetite_stated = bool(row)
            # conservative: until the residual is assessed, the inherent
            # score stands — an unknown residual is never 'within appetite'
            score = (
                rec.residual_score
                if (rec.residual_likelihood and rec.residual_impact)
                else (rec.risk_score or 0)
            )
            rec.above_appetite = bool(row) and score > row.max_residual_score

    @api.depends("control_ids.state", "control_ids.test_result")
    def _compute_control_deficiency(self):
        for rec in self:
            rec.control_deficient = bool(
                rec.control_ids.filtered(
                    lambda c: c.state == "active" and c.test_result in ("partially", "ineffective")
                )
            )

    @api.constrains("residual_score")
    def _check_residual_within_inherent(self):
        for rec in self:
            if rec.residual_score and rec.risk_score and rec.residual_score > rec.risk_score:
                raise ValidationError(
                    "The residual score (%d) of '%s' may not exceed its inherent "
                    "score (%d): controls mitigate risk, they do not add it "
                    "(A10 P1-5, M60-8)." % (rec.residual_score, rec.name, rec.risk_score)
                )

    @api.constrains("residual_score", "residual_accepted_by_id")
    def _check_residual_acceptance(self):
        for rec in self:
            if rec.residual_band == "high" and not rec.residual_accepted_by_id:
                raise ValidationError(
                    "A HIGH residual risk needs a named acceptance (residual accepted by)."
                )

    mitigation = fields.Text(string="Mitigation & Treatment Strategy")
    control_ids = fields.One2many("fix.control", "risk_id", string="Mitigating Controls")
    owner_id = fields.Many2one("hr.employee", string="Risk Owner")
    review_date = fields.Date(string="Next Review Date")
    state = fields.Selection(
        [
            ("open", "Active / Open"),
            ("mitigating", "Mitigating / Under Treatment"),
            ("accepted", "Residual Accepted"),
            ("closed", "Closed / Retired"),
        ],
        default="open",
        required=True,
        tracking=True,
    )

    @api.depends("likelihood", "impact")
    def _compute_score(self):
        for rec in self:
            rec.risk_score = int(rec.likelihood or "3") * int(rec.impact or "3")

    def _fix_guarded_fields(self) -> set:
        """A10 R1: the lifecycle and the acceptance record change only through
        the actions below — a typed 'accepted' with a typed acceptor is the
        self-attestation the audit found (M60-7)."""
        return super()._fix_guarded_fields() | {
            "state",
            "residual_accepted_by_id",
            "residual_accepted_on",
        }

    # ---- M63 hooks (A10 P1-5) ----------------------------------------------
    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.above_appetite

    def _approval_amount(self) -> float:
        self.ensure_one()
        return float(self.residual_score or 0)

    def _approval_pinned_fields(self) -> set:
        # What the acceptance was decided ON: the assessment, the category
        # (the appetite it is measured against) and whose risk it is. A change
        # voids the pending or granted acceptance (A11 audit E4, M63-6).
        return super()._approval_pinned_fields() | {
            "category",
            "owner_id",
            "residual_likelihood",
            "residual_impact",
        }

    def _require_risk_owner(self):
        _require_group(
            self.env,
            RISK_OWNER_GROUP,
            "Only a Risk Owner accepts a residual or closes a risk (A10 R1, M60-7).",
        )

    def _employee_of_user(self):
        employee = self.env["hr.employee"].search([("user_id", "=", self.env.user.id)], limit=1)
        if not employee:
            raise UserError(
                "%s has no employee record — the acceptance must name an employee "
                "of the Risk Owner group." % self.env.user.name
            )
        return employee

    def _assert_reduction_grounded(self):
        """A10 P1-5 (M60-8): a residual assessed BELOW the inherent score is a
        claim that the controls reduced it — the claim must be grounded in
        linked, tested controls, not in a number somebody typed."""
        self.ensure_one()
        if (self.residual_score or 0) >= (self.risk_score or 0):
            return  # no reduction claimed: an honest acceptance cites no control
        active = self.control_ids.filtered(lambda c: c.state == "active")
        if not active:
            raise UserError(
                "The residual of '%s' is assessed below its inherent score, but "
                "no ACTIVE control is linked to it: the reduction is not "
                "grounded. Link the controls that mitigate it (A10 P1-5, M60-8)." % self.name
            )
        ineffective = active.filtered(lambda c: c.test_result == "ineffective")
        if ineffective:
            raise UserError(
                "The residual of '%s' claims a reduction grounded on a control "
                "whose latest test was INEFFECTIVE (%s). Re-test before "
                "accepting it (A10 P1-5, M60-9)."
                % (self.name, ", ".join(ineffective.mapped("name")))
            )

    def action_accept_residual(self, justification=None):
        """A10 R1 + P1-5 (M60-7): the residual acceptance. Within the stated
        appetite it is the Risk Owner's own signature; ABOVE the appetite it
        is not — the owner asks, the M63 engine routes the decision to the
        Delegated Authority Owner (CFO group) minus the requester and the
        record's creator, and the deciding task applies this same method with
        the APPROVER stamped as the acceptor. The acceptor and the date come
        from the deciding session, never from a typed field."""
        task = self._approval_task()
        if not task:
            # the direct path is the Risk Owner's; the engine's apply path
            # (task in context) is the CFO's — RPC cannot forge a recordset
            # into the context, so this split is not bypassable
            self._require_risk_owner()
        for rec in self:
            if rec.state == "closed":
                raise UserError(
                    "'%s' is closed — reopen it before accepting its residual." % rec.name
                )
            if not rec.residual_likelihood or not rec.residual_impact:
                raise UserError(
                    "Assess the residual likelihood and impact of '%s' before "
                    "accepting it." % rec.name
                )
            rec._assert_reduction_grounded()
            if rec.above_appetite and not task:
                # P1-5: not the owner's own signature. The request carries the
                # appetite breach as its justification; the engine routes it to
                # someone other than the requester and the creator.
                rec.action_request_approval(
                    justification=justification
                    or "Residual %d exceeds the stated %s appetite (%d)."
                    % (
                        rec.residual_score,
                        dict(rec._fields["category"].selection).get(rec.category, rec.category),
                        rec.appetite_limit,
                    )
                )
                continue
            if rec.above_appetite and task:
                acceptor = rec._employee_of_user()
                if rec.owner_id and acceptor == rec.owner_id:
                    raise UserError(
                        "Segregation of duties: the residual of '%s' is above the "
                        "stated appetite, so the risk owner may not also be the "
                        "acceptor (A10 P1-5, M60-7)." % rec.name
                    )
            rec._guarded().write(
                {
                    "state": "accepted",
                    "residual_accepted_by_id": rec._employee_of_user().id,
                    "residual_accepted_on": fields.Date.context_today(rec),
                }
            )
            rec.message_post(
                body="Residual %d (%s) accepted by %s%s."
                % (
                    rec.residual_score or 0,
                    rec.residual_band or "—",
                    rec.residual_accepted_by_id.name,
                    " — above the stated appetite (approved through M63)"
                    if rec.above_appetite
                    else "",
                )
            )
        return True

    def action_close(self):
        self._require_risk_owner()
        for rec in self:
            if rec.state == "closed":
                raise UserError("'%s' is already closed." % rec.name)
            rec._guarded().write({"state": "closed"})
            rec.message_post(body="Risk closed by %s." % self.env.user.name)
        return True

    def action_reopen(self):
        self._require_risk_owner()
        for rec in self:
            if rec.state != "closed":
                raise UserError("'%s' is not closed." % rec.name)
            rec._guarded().write({"state": "open"})
            rec.message_post(body="Risk reopened by %s." % self.env.user.name)
        return True


class FixControl(models.Model):
    """M60: Internal Control definition and effectiveness assessment."""

    _name = "fix.control"
    _description = "Internal Control"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Control Title", required=True)
    control_code = fields.Char(string="Control Code (e.g. CTL-SEC-01)")
    control_type = fields.Selection(
        [("preventive", "Preventive"), ("detective", "Detective"), ("corrective", "Corrective")],
        required=True,
        default="preventive",
    )
    frequency = fields.Selection(
        [
            ("continuous", "Automated / Continuous"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
        ],
        default="continuous",
        required=True,
    )
    risk_id = fields.Many2one("fix.risk.register", string="Risk Addressed")
    # A10 P1-5 (M60-9): a control without an accountable owner cannot be
    # remediated when its test fails — and the tester may not be the owner.
    owner_id = fields.Many2one(
        "hr.employee",
        string="Control Owner",
        help="Accountable for the control operating and for remediating a "
        "failed test (the tester may not be the owner).",
    )
    obligation_ids = fields.Many2many("fix.compliance.obligation", string="Mapped Obligations")
    last_tested = fields.Date(string="Last Assessment Date")
    test_result = fields.Selection(
        [
            ("effective", "Effective"),
            ("partially", "Partially Effective"),
            ("ineffective", "Ineffective"),
        ],
        tracking=True,
    )
    evidence_doc_id = fields.Many2one(
        "fix.document",
        string="Control Evidence (M24)",
        help="Evidence artefact stored in M24 document store per ADR D-040",
    )
    state = fields.Selection(
        [("active", "Active"), ("inactive", "Inactive")],
        default="active",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        # A10 R1: a control leaving the framework is a compliance decision.
        # A10 P1-5 (M60-9): the assessment record (last_tested / test_result)
        # is the CONCLUSION of a test record, stamped by it — a typed
        # 'effective' was a self-attested control.
        return super()._fix_guarded_fields() | {"state", "last_tested", "test_result"}

    def action_activate(self):
        _require_group(
            self.env, OFFICER_GROUP, "Only a Compliance Officer activates a control (A10 R1)."
        )
        for rec in self:
            if rec.state != "inactive":
                raise UserError("'%s' is already active." % rec.name)
            rec._guarded().write({"state": "active"})
        return True

    def action_retire(self):
        _require_group(
            self.env, OFFICER_GROUP, "Only a Compliance Officer retires a control (A10 R1)."
        )
        for rec in self:
            if rec.state != "active":
                raise UserError("'%s' is not active." % rec.name)
            rec._guarded().write({"state": "inactive"})
            rec.message_post(body="Control retired by %s." % self.env.user.name)
        return True


class FixComplianceFramework(models.Model):
    """M60: Authoritative compliance frameworks (ISO 9001, ISO 27001, PDPA, Labour Act)."""

    _name = "fix.compliance.framework"
    _description = "Compliance Standard & Framework Matrix"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "code, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Framework Name", required=True)
    code = fields.Selection(
        [
            ("iso_9001", "ISO 9001:2015 Quality Management"),
            ("iso_27001", "ISO/IEC 27001:2022 Information Security"),
            ("pdpa_2023", "Bangladesh PDPA 2023 / 2026"),
            ("bla_2006", "Bangladesh Labour Act 2006 & Rules 2015"),
            ("iso_14001", "ISO 14001:2015 Environmental Management"),
        ],
        string="Framework Identifier",
        required=True,
        default="iso_9001",
    )
    standard_edition = fields.Char(string="Edition / Revision", default="Current")
    certifying_body = fields.Char(
        string="Certification Body / Regulator", default="DNV / DIFE / DoE"
    )
    obligation_ids = fields.One2many(
        "fix.compliance.obligation", "framework_id", string="Obligations"
    )
    finding_ids = fields.One2many("fix.audit.finding", "framework_id", string="Audit Findings")
    clause_count = fields.Integer(
        string="Total Mapped Clauses", compute="_compute_clause_stats", store=True
    )
    compliance_score = fields.Float(
        string="Compliance Rate (%)", compute="_compute_clause_stats", store=True
    )
    last_audit_date = fields.Date(string="Last External/Internal Audit")
    next_audit_date = fields.Date(string="Next Surveillance Audit")
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [("draft", "Draft Mapping"), ("active", "Enforced & Audited"), ("archived", "Archived")],
        default="active",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        # A10 R1: a framework entering or leaving enforcement changes what the
        # whole compliance register reports.
        return super()._fix_guarded_fields() | {"state"}

    def action_activate(self):
        _require_group(
            self.env,
            OFFICER_GROUP,
            "Only a Compliance Officer enforces a framework (A10 R1).",
        )
        for rec in self:
            if rec.state == "active":
                raise UserError("'%s' is already enforced." % rec.name)
            rec._guarded().write({"state": "active"})
        return True

    def action_archive(self):
        _require_group(
            self.env,
            OFFICER_GROUP,
            "Only a Compliance Officer archives a framework (A10 R1).",
        )
        for rec in self:
            if rec.state != "active":
                raise UserError("'%s' is not enforced." % rec.name)
            rec._guarded().write({"state": "archived"})
            rec.message_post(body="Framework archived by %s." % self.env.user.name)
        return True

    @api.depends("obligation_ids.compliance_status")
    def _compute_clause_stats(self):
        for rec in self:
            rec.clause_count = len(rec.obligation_ids)
            # "Not Applicable" clauses are out of scope: counting them in the
            # denominator scored an excluded clause as a failure. An
            # UNASSESSED clause (A10 S6: the honest default) is out of the
            # denominator too — nobody assessed it — and a framework whose
            # every clause is unassessed scores ZERO, not the 100% the old
            # "compliant" default invented: no compliance is proven yet.
            assessed = rec.obligation_ids.filtered(lambda o: o.compliance_status != "unassessed")
            applicable = assessed.filtered(lambda o: o.compliance_status != "not_applicable")
            if applicable:
                compliant = len(applicable.filtered(lambda o: o.compliance_status == "compliant"))
                partial = len(
                    applicable.filtered(lambda o: o.compliance_status == "partially_compliant")
                )
                rec.compliance_score = round(
                    ((compliant + (0.5 * partial)) / len(applicable)) * 100.0, 1
                )
            elif rec.obligation_ids.filtered(lambda o: o.compliance_status == "unassessed"):
                rec.compliance_score = 0.0
            else:
                # no clauses at all, or every clause assessed Not Applicable
                rec.compliance_score = 100.0


class FixComplianceObligation(models.Model):
    """M60: Specific clause or statutory requirement under a compliance framework."""

    _name = "fix.compliance.obligation"
    _description = "Compliance Obligation & Clause"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "clause_reference, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    framework_id = fields.Many2one(
        "fix.compliance.framework", string="Compliance Framework", required=True
    )
    name = fields.Char(string="Requirement Title", required=True)
    clause_reference = fields.Char(string="Clause / Section Reference", required=True)
    mandatory = fields.Boolean(string="Mandatory Statutory Requirement", default=True)
    control_ids = fields.Many2many("fix.control", string="Enforcing Controls")
    evidence_doc_id = fields.Many2one(
        "fix.document",
        string="Compliance Evidence (M24 Document)",
        help="Evidentiary record registered in M24 kernel per ADR D-040",
    )
    compliance_status = fields.Selection(
        [
            # A10 S6 (D5/decorative flags): the default was "compliant" — a
            # register nobody assessed scored 100%. An obligation is
            # compliant only once a Compliance Officer has assessed it.
            ("unassessed", "Not Yet Assessed"),
            ("compliant", "Fully Compliant"),
            ("partially_compliant", "Partially Compliant"),
            ("non_compliant", "Non-Compliant"),
            ("not_applicable", "Not Applicable"),
        ],
        default="unassessed",
        required=True,
        tracking=True,
    )
    notes = fields.Text(string="Audit & Assessment Notes")
    # A10 P1-2 (M60-10): the obligation's review clock. next_review_date is
    # the owner's plan; the daily cron nags (at most once a day) until the
    # review moves it forward — an obligation with no clock never came due.
    next_review_date = fields.Date(string="Next Review Due")
    last_review_reminder_on = fields.Date()

    @api.model
    def cron_obligation_review(self):
        """The daily obligation clock (A10 P1-2, M60-10): due obligations are
        announced on the outbox — at most once a day each, until the owner's
        review moves the due date forward."""
        today = fields.Date.today()
        due = self.search(
            [
                ("next_review_date", "!=", False),
                ("next_review_date", "<=", today),
            ]
        ).filtered(lambda o: not o.last_review_reminder_on or o.last_review_reminder_on < today)
        for rec in due:
            publish(
                self.env,
                "grc.obligation.due",
                "fix.compliance.obligation",
                rec.id,
                {
                    "obligation": rec.name,
                    "clause": rec.clause_reference,
                    "framework": rec.framework_id.name,
                    "due": str(rec.next_review_date),
                },
            )
            rec.last_review_reminder_on = today
            rec.message_post(
                body="Compliance review due since %s (clause %s)."
                % (rec.next_review_date, rec.clause_reference)
            )
        return len(due)

    def consume_obligation_due(self, env_from_relay):
        """In-Odoo consumer for grc.obligation.due (relay-only): the
        obligation's own thread is the audit trail of the nag."""
        if not self.env.su:
            raise UserError("The obligation clock consumer runs from the event relay only.")
        ob = self.browse(int(env_from_relay.get("aggregate_id") or 0)).exists()
        if ob:
            ob.message_post(body="Review reminder relayed to the obligation thread.")
        return True

    def _fix_guarded_fields(self) -> set:
        # A10 S6 (D5): the assessment is the Compliance Officer's act, not a
        # typed field — the framework's compliance score reads exactly this
        # field, so a typed status invented the figure the board reads.
        return super()._fix_guarded_fields() | {"compliance_status"}

    def action_assess(self, status, notes=None):
        """Assess the obligation's compliance (A10 S6, M60): the Compliance
        Officer's recorded verdict, on the thread, from a fixed vocabulary."""
        valid = [
            value
            for value, _label in type(self).compliance_status.selection
            if value != "unassessed"
        ]
        if status not in valid:
            raise UserError("Assess %s as one of: %s." % (self._description, ", ".join(valid)))
        _require_group(
            self.env,
            OFFICER_GROUP,
            "Only a Compliance Officer assesses an obligation (A10 S6).",
        )
        labels = dict(type(self).compliance_status.selection)
        for rec in self:
            rec._guarded().write({"compliance_status": status})
            body = "Assessed %s by %s." % (labels[status], self.env.user.name)
            if (notes or "").strip():
                body += " %s" % notes.strip()
            rec.message_post(body=body)
        return True


class FixAuditFinding(models.Model):
    """M60: Internal & External Audit Non-Conformances and Corrective Actions (CAPA)."""

    _name = "fix.audit.finding"
    _description = "Audit Finding & CAPA"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "audit_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Finding Summary", required=True)
    finding_code = fields.Char(string="Finding Reference (e.g. AUD-2026-001)")
    framework_id = fields.Many2one(
        "fix.compliance.framework", string="Audited Framework", required=True
    )
    obligation_id = fields.Many2one(
        "fix.compliance.obligation", string="Breached Obligation / Clause"
    )
    finding_type = fields.Selection(
        [
            ("major_nc", "Major Non-Conformance"),
            ("minor_nc", "Minor Non-Conformance"),
            ("ofi", "Opportunity for Improvement (OFI)"),
        ],
        default="minor_nc",
        required=True,
        tracking=True,
    )
    auditor_id = fields.Many2one("hr.employee", string="Lead Auditor", required=True)
    audit_date = fields.Date(string="Audit Date", default=fields.Date.today, required=True)
    target_closure_date = fields.Date(string="CAPA Target Closure Date", required=True)
    description = fields.Text(string="Condition & Objective Evidence", required=True)
    root_cause_analysis = fields.Text(string="Root Cause Analysis (5-Why / Fishbone)")
    remediation_plan = fields.Text(string="Corrective Action Plan (CAPA)")
    closure_evidence_doc_id = fields.Many2one(
        "fix.document",
        string="Closure Evidence Document (M24)",
        help="Signed verification artefact in M24 volume store per ADR D-040",
    )
    capa_status = fields.Selection(
        [
            ("open", "Open Non-Conformance"),
            ("capa_submitted", "CAPA Submitted"),
            ("verified", "Effectiveness Verified"),
            ("closed", "Closed & Certified"),
        ],
        default="open",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        # A10 R1: the CAPA lifecycle on a finding changes only through its
        # actions — a typed 'verified'/'closed' is the skip the audit found
        # (M60-15).
        return super()._fix_guarded_fields() | {"capa_status"}

    def action_submit_capa(self, plan_text=""):
        for rec in self:
            if rec.capa_status == "closed":
                # R1: otherwise submit-after-close would quietly reopen the
                # loop the closure gate just closed.
                raise UserError("'%s' is closed — a closed CAPA is not resubmitted." % rec.name)
            vals = {"capa_status": "capa_submitted"}
            if plan_text:
                vals["remediation_plan"] = plan_text
            rec._guarded().write(vals)
            rec.message_post(body="CAPA submitted%s." % (" with a plan" if plan_text else ""))

    def action_verify_closure(self):
        """Closure is verified by the finding's auditor or a Compliance
        Officer — never by whoever happens to be logged in — over a
        documented remediation plan (A10 R1, M60-15)."""
        for rec in self:
            if not self.env.su:
                auditor_user = rec.auditor_id.user_id
                if self.env.user != auditor_user and not self.env.user.has_group(OFFICER_GROUP):
                    raise UserError(
                        "The closure of '%s' is verified by its auditor (%s) or a "
                        "Compliance Officer (A10 R1)." % (rec.name, rec.auditor_id.name or "—")
                    )
            if rec.capa_status not in ("capa_submitted",):
                raise UserError("Submit the CAPA of '%s' before verifying its closure." % rec.name)
            if not rec.remediation_plan:
                raise UserError("A remediation plan must be documented before verifying closure.")
            rec._guarded().write({"capa_status": "closed"})
            publish(
                self.env,
                "grc.capa_closed",
                "fix.audit.finding",
                rec.id,
                {"code": rec.finding_code or rec.name, "framework": rec.framework_id.name},
            )
