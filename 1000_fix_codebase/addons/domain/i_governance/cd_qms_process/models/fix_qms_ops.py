# fix_qms_ops — M23: policy/objectives, process register, checklist templates,
# quality gates, certification surveillance, management review and CoPQ.
# NCRs, CAPAs and internal audits live in fix_qms.py.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

QM_GROUP = "cd_qms_process.group_qms_quality_manager"

# A10 P1-6 (M23-8): ISO 9.3.2 — the input kinds a management review must
# have PULLED from the system before it is held. Every kind maps to records
# the system already holds; none of them is typed.
# A10 deep audit (2026-11-22, A1-F04): the set was incomplete (no 9.3.2 b,
# d, e, f, c.2, c.5) and cited clause letters that do not exist (g/h).
# The full set below keeps every legacy key (stored rows stay valid) with
# its clause reference corrected, and adds the six missing considerations.
REVIEW_INPUT_KINDS = [
    ("prior_actions", "Actions from previous reviews (9.3.2 a)"),
    ("issues_changes", "Changes in external and internal issues (9.3.2 b)"),
    ("customer_feedback", "Customer satisfaction and feedback (9.3.2 c.1)"),
    ("objectives_attainment", "Extent to which quality objectives are met (9.3.2 c.2)"),
    ("process_performance", "Process performance and conformity (9.3.2 c.3)"),
    ("nonconformities", "Nonconformities and corrective actions (9.3.2 c.4)"),
    ("monitoring_results", "Monitoring and measurement results (9.3.2 c.5)"),
    ("audit_results", "Audit results and surveillance (9.3.2 c.6)"),
    ("external_providers", "External provider performance (9.3.2 c.7)"),
    ("resources_adequacy", "Adequacy of resources (9.3.2 d)"),
    ("risk_effectiveness", "Effectiveness of risk and opportunity actions (9.3.2 e)"),
    ("improvement_opportunities", "Opportunities for improvement (9.3.2 f)"),
]


def _require_quality_manager(env, why):
    """A10 Q3: the certificate record belongs to the Quality Manager."""
    if env.su:
        return
    if not env.user.has_group(QM_GROUP):
        raise UserError("Only the Quality Manager may %s (A10 Q3)." % why)


class FixQmsPolicy(models.Model):
    _name = "fix.qms.policy"
    _description = "Quality Policy & Objective"
    _inherit = ["fix.guarded.mixin"]
    _order = "year desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    year = fields.Char(required=True)
    policy_text = fields.Text()
    objective = fields.Char(string="Quality Objective")
    target = fields.Float(string="Target")
    actual = fields.Float(string="Actual")
    unit = fields.Char()
    owner_id = fields.Many2one("hr.employee", string="Owner")
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("reviewed", "Reviewed")],
        required=True,
        default="draft",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    def write(self, vals):
        # A10 S6 (M23-9): an approved policy's text is the certified
        # statement — editing it in place rewrites what was approved. Next
        # year's policy is a new record.
        if "policy_text" in vals:
            for rec in self.filtered(lambda r: r.state == "approved"):
                raise UserError(
                    "'%s' (%s) is approved — its text is the certified statement and "
                    "cannot be edited in place (A10 S6)." % (rec.name, rec.year)
                )
        return super().write(vals)

    def action_approve(self):
        # A10 S6 (M23-9): approval was a state flip by anyone.
        _require_quality_manager(self.env, "approve the quality policy")
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "'%s' is %s — approval starts from a draft policy." % (rec.name, rec.state)
                )
            if not (rec.policy_text or "").strip():
                raise UserError("Approve what? '%s' carries no policy text." % rec.name)
            rec._guarded().write({"state": "approved"})


class FixQmsProcess(models.Model):
    _name = "fix.qms.process"
    _description = "QMS Process Register"
    _inherit = ["fix.guarded.mixin"]
    _order = "code"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    process_owner_id = fields.Many2one("hr.employee", string="Process Owner")
    iso_clause = fields.Char(string="ISO 9001 Clause")
    process_type = fields.Selection(
        [("core", "Core / Value Stream"), ("support", "Support"), ("management", "Management")],
        required=True,
        default="core",
    )
    inputs = fields.Char()
    outputs = fields.Char()
    kpi_definition = fields.Char(string="Process KPI")
    state = fields.Selection(
        [("active", "Active"), ("retired", "Retired")], required=True, default="active"
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A process code is unique per company"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    def action_retire(self):
        """A10 S6: retiring a QMS process is the Quality Manager's act, and
        the register keeps its history — the state is never typed."""
        _require_quality_manager(self.env, "retire a QMS process")
        for rec in self:
            if rec.state != "active":
                raise UserError("'%s' is already %s." % (rec.code, rec.state))
            rec._guarded().write({"state": "retired"})
        return True


class FixQmsChecklist(models.Model):
    _name = "fix.qms.checklist"
    _description = "Quality Checklist Template"
    _inherit = ["fix.guarded.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    checklist_type = fields.Selection(
        [
            ("qc", "QC Bench Check"),
            ("audit", "Audit Checklist"),
            ("handover", "Handover"),
            ("safety", "Safety Walk"),
        ],
        required=True,
        default="qc",
    )
    iso_clause = fields.Char(string="ISO Clause")
    item_count = fields.Integer(string="Items")
    version = fields.Char(default="1.0")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    def action_publish(self):
        """A10 S6 (M23-16): publication was a state flip by anyone — a bench
        checklist the floor follows is published by the Quality Manager."""
        _require_quality_manager(self.env, "publish a quality checklist")
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "'%s' is %s — only a draft checklist is published." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "published"})
        return True

    def action_retire(self):
        """A10 S6: retiring a published checklist is the Quality Manager's
        act; the template's history stays."""
        _require_quality_manager(self.env, "retire a quality checklist")
        for rec in self:
            if rec.state != "published":
                raise UserError(
                    "'%s' is %s — only a published checklist is retired." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "retired"})
        return True


class FixQmsGate(models.Model):
    _name = "fix.qms.gate"
    _description = "Quality Gate"
    _inherit = ["fix.guarded.mixin"]
    _order = "sequence, id"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    sequence = fields.Integer(default=10)
    stage = fields.Char(string="Process Stage")
    mandatory_checklist_id = fields.Many2one("fix.qms.checklist", string="Mandatory Checklist")
    blocking = fields.Boolean(string="Blocks Progression", default=True)
    state = fields.Selection(
        [("active", "Active"), ("retired", "Retired")], required=True, default="active"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    def action_retire(self):
        """A10 S6 (M23-16): a quality gate's state was typed and decorative —
        retiring one is at least now the Quality Manager's recorded act."""
        _require_quality_manager(self.env, "retire a quality gate")
        for rec in self:
            if rec.state != "active":
                raise UserError("Gate %s is already %s." % (rec.code, rec.state))
            rec._guarded().write({"state": "retired"})
        return True


class FixQmsCertification(models.Model):
    _name = "fix.qms.certification"
    _description = "Certification & Surveillance Audit"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "audit_date desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    standard = fields.Char(required=True, default="ISO 9001:2015")
    body = fields.Char(string="Certification Body")
    certificate_no = fields.Char()
    audit_type = fields.Selection(
        [
            ("stage_1", "Stage 1"),
            ("stage_2", "Stage 2"),
            ("surveillance", "Surveillance"),
            ("recertification", "Recertification"),
        ],
        required=True,
        default="surveillance",
    )
    audit_date = fields.Date(required=True, default=fields.Date.context_today)
    valid_until = fields.Date()
    result = fields.Selection(
        [
            ("pending", "Pending"),
            ("passed", "Passed"),
            ("minor_ncs", "Passed with Minor NCs"),
            ("major_ncs", "Major NCs"),
            ("failed", "Failed"),
        ],
        required=True,
        default="pending",
    )
    notes = fields.Char()
    # A10 Q3 (M23-6): the PASS claim is only as good as the certificate
    # behind it — the record points at the scanned certificate document
    certificate_doc_id = fields.Many2one(
        "fix.document",
        string="Certificate Document",
        help="The scanned certificate from the certification body; a PASS is "
        "recorded only with the document attached (A10 Q3).",
    )

    def _fix_guarded_fields(self) -> set:
        """A10 Q3 (M23-6, E x01–x04): the audit RESULT is typed by the
        Quality Manager through the actions — never by a plain write that
        flips a failed audit to passed or sets valid_until = 2099.
        A10 deep audit (2026-11-22, A1-F08): the guard now also freezes the
        validity window and the certificate number AFTER creation — a quiet
        extension of a certificate's life is a new surveillance row's fact,
        not an edit."""
        return {"result", "valid_until", "certificate_no", "surveillance_band_notified"}

    # A10 deep audit (2026-11-22, A1-F03): the surveillance clock. Which
    # expiry band the Quality Managers were already told about ('90', '30',
    # 'overdue') — set once per band by the daily cron, never typed.
    surveillance_band_notified = fields.Char(readonly=True)

    @api.constrains("valid_until", "audit_date")
    def _check_validity_window(self):
        for rec in self:
            if rec.valid_until and rec.audit_date and rec.valid_until <= rec.audit_date:
                raise ValidationError(
                    "The certificate's validity ends after its audit date "
                    "(valid_until %s follows audit_date %s)." % (rec.valid_until, rec.audit_date)
                )

    @api.model
    def cron_certification_surveillance(self):
        """A10 deep audit (2026-11-22, A1-F03): nothing watched valid_until —
        a lapsed ISO certificate (the company's headline credential) would
        have gone unnoticed. Daily: each passed certificate entering the
        90-day and 30-day surveillance window, or past its validity, tells
        the Quality Managers ONCE per band."""
        today = fields.Date.context_today(self)
        group = self.env.ref(QM_GROUP, raise_if_not_found=False)
        managers = (
            group.sudo().user_ids if group else self.env["res.users"]
        ).filtered(lambda u: u.active and not u.share)
        if not managers:
            return True
        for rec in self.sudo().search([("result", "=", "passed"), ("valid_until", "!=", False)]):
            days = (rec.valid_until - today).days
            band = "overdue" if days < 0 else "30" if days <= 30 else "90" if days <= 90 else None
            if band is None or rec.surveillance_band_notified == band:
                continue
            rec._guarded().write({"surveillance_band_notified": band})
            rec.message_post(
                body=(
                    "Certification surveillance: %s (%s, certificate %s) %s — "
                    "valid until %s. Book the audit with the certification body."
                    % (
                        rec.name,
                        rec.standard,
                        rec.certificate_no or "—",
                        "has LAPSED"
                        if band == "overdue"
                        else "enters its %s-day surveillance window" % band,
                        rec.valid_until,
                    )
                ),
                partner_ids=managers.mapped("partner_id").ids,
                subtype_xmlid="mail.mt_comment",
            )
        return True

    def action_pass(self):
        """A10 Q3: a PASS is recorded by the Quality Manager, with the
        certificate document attached."""
        _require_quality_manager(self.env, "record a passed certification")
        for rec in self:
            if not rec.certificate_doc_id:
                raise UserError(
                    "Attach the certificate document before recording %s as passed "
                    "(A10 Q3)." % rec.name
                )
            rec._guarded().write({"result": "passed"})

    def action_record_result(self, result=None):
        """A10 Q3: any other outcome (minor NCs, major NCs, failed) is
        recorded by the Quality Manager — including walking a result back to
        pending when a mistake is corrected."""
        _require_quality_manager(self.env, "record a certification result")
        valid = {"pending", "minor_ncs", "major_ncs", "failed"}
        if result not in valid:
            raise UserError(
                "Record one of %s (use action_pass for a passed certificate)."
                % ", ".join(sorted(valid))
            )
        for rec in self:
            rec._guarded().write({"result": result})


class FixQmsReview(models.Model):
    """ISO 9.3: the management review.

    A10 P1-6 (M23-8): the audit found a review with no ISO 9.3 inputs (the
    pack lived in a report, not on the record), free-text decisions that
    tracked nothing, and a closed review that reopened because `state` was
    a typist's field. Now the inputs are PULLED from the system (one line
    per required 9.3.2 kind, each a count of real records), the outputs are
    tracked action lines with owners and dates, the record is held only
    over a complete input set by the Quality Manager with a chairperson
    named, and the closure is TOP MANAGEMENT's routed decision (DOFA
    Tier 5 — the engine's inbox, never the QM's own pen). A closed review
    does not reopen: the state is guarded and no action reopens it.
    """

    _name = "fix.qms.review"
    _description = "Management Review (ISO 9.3)"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "review_date desc, id desc"

    _approval_domain = "qms_review_closure"
    _approval_apply_method = "action_apply_closure"
    _approval_routed = True

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    review_date = fields.Date(required=True, default=fields.Date.context_today)
    chairperson_id = fields.Many2one("hr.employee", string="Chairperson")
    attendees = fields.Char()
    agenda = fields.Text()
    decisions = fields.Text()
    input_ids = fields.One2many("fix.qms.review.input", "review_id", string="Inputs (9.3.2)")
    action_ids = fields.One2many("fix.qms.review.action", "review_id", string="Tracked Actions")
    inputs_missing = fields.Integer(
        compute="_compute_inputs",
        string="Missing Inputs",
        help="ISO 9.3.2 input kinds not yet pulled for this review. A review "
        "is held only at zero.",
    )
    open_actions = fields.Integer(
        compute="_compute_open_actions",
        store=True,
        string="Open Actions",
        help="ISO 9.3.3 output lines still open. System-counted, never typed.",
    )
    closed_on = fields.Date(copy=False)
    closed_by_id = fields.Many2one(
        "hr.employee",
        string="Closed by",
        copy=False,
        help="The top-management approver the engine recorded.",
    )
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("held", "Held"), ("closed", "Closed")],
        required=True,
        default="scheduled",
        tracking=True,
    )

    @api.depends("input_ids.kind")
    def _compute_inputs(self):
        want = {kind for kind, _label in REVIEW_INPUT_KINDS}
        for rec in self:
            rec.inputs_missing = len(want - set(rec.input_ids.mapped("kind")))

    @api.depends("action_ids.state")
    def _compute_open_actions(self):
        for rec in self:
            rec.open_actions = len(rec.action_ids.filtered(lambda a: a.state == "open"))

    def _fix_guarded_fields(self) -> set:
        # A10 P1-6 (M23-8): the lifecycle is the workflow's — a closed review
        # stayed closed because nothing stopped typing it open again.
        return super()._fix_guarded_fields() | {"state", "closed_on", "closed_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(self._fix_guarded_fields())
        if set(self.mapped("state")) == {"closed"}:
            # the closed review is the record kept: agenda, attendees and
            # decisions freeze with it
            locked |= {"name", "review_date", "chairperson_id", "attendees", "agenda", "decisions"}
        return locked

    # ---- M63 hooks -------------------------------------------------------
    def _approval_needed(self) -> bool:
        return self.state == "held"

    def _approval_tier(self):
        # ISO 9.3.1: TOP MANAGEMENT conducts the review and owns its outputs,
        # so the closure is a DOFA Tier 5 (MD / Board) decision.
        return "tier_5"

    def _approval_pinned_fields(self) -> set:
        # the closure was decided ON this record: moving what was reviewed
        # under a pending closure voids the request (A11 E4, M63-6)
        return super()._approval_pinned_fields() | {
            "review_date",
            "chairperson_id",
            "agenda",
            "decisions",
        }

    # ---- the inputs (9.3.2) ----------------------------------------------
    def _review_window(self):
        """(date_from, date_to]: since the company's previous review, up to
        and including this review's date. The first review sees all history."""
        self.ensure_one()
        prev = self.search(
            [
                ("company_id", "=", self.company_id.id),
                ("id", "!=", self.id),
                ("review_date", "<", self.review_date),
            ],
            order="review_date desc",
            limit=1,
        )
        return (prev.review_date if prev else False, self.review_date)

    def _window_domain(self, field_name, window, date_field=False):
        """A search domain bound to the review window. Datetime fields need
        the day after the review (a bare date is midnight); date fields are
        inclusive of the review day itself."""
        date_from, date_to = window
        bound = (
            (field_name, "<=", date_to)
            if date_field
            else (field_name, "<", date_to + timedelta(days=1))
        )
        domain = [bound]
        if date_from:
            domain.append((field_name, ">=", date_from))
        return domain

    def _copq_in_window(self, window):
        """CoPQ periods are 'YYYY-MM' strings: the months the window covers."""
        date_from, date_to = window
        domain = [("period", "<=", date_to.strftime("%Y-%m"))]
        if date_from:
            months = []
            cur = date_from.replace(day=1)
            end = date_to.replace(day=1)
            while cur <= end:
                months.append(cur.strftime("%Y-%m"))
                cur = (cur.replace(day=28) + timedelta(days=4)).replace(day=1)
            domain.append(("period", "in", months))
        return self.env["fix.qms.copq"].sudo().search(self._scoped(domain))

    def _scoped(self, domain):
        """A snapshot counts THIS company's records, never another's."""
        self.ensure_one()
        return [*domain, ("company_id", "=", self.company_id.id)]

    def _input_snapshot(self, kind, window):
        """(summary, headline, open_count) for one 9.3.2 kind — counts of
        records the system holds, never an estimate."""
        self.ensure_one()
        env = self.env
        date_from, date_to = window
        span = "window %s..%s" % (date_from or "(first review)", date_to)
        today = fields.Date.context_today(self)
        if kind == "prior_actions":
            earlier = self.search(
                [("company_id", "=", self.company_id.id), ("review_date", "<", self.review_date)]
            )
            acts = env["fix.qms.review.action"].sudo().search([("review_id", "in", earlier.ids)])
            open_acts = acts.filtered(lambda a: a.state == "open")
            overdue = open_acts.filtered(lambda a: a.due_on and a.due_on < today)
            detail = "; ".join("%s (due %s)" % (a.name, a.due_on) for a in open_acts[:5])
            summary = (
                "%d tracked action(s) from %d earlier review(s); %d still open, %d "
                "overdue. %s"
                % (len(acts), len(earlier), len(open_acts), len(overdue), detail or "None open.")
            )
            return summary, "%d open of %d" % (len(open_acts), len(acts)), len(open_acts)
        if kind == "customer_feedback":
            complaints = (
                env["fix.complaint"]
                .sudo()
                .search(self._scoped(self._window_domain("create_date", window)))
            )
            open_c = complaints.filtered(lambda c: c.state not in ("closed", "rejected"))
            critical = complaints.filtered(lambda c: c.severity == "critical")
            summary = (
                "%d complaint(s) received (%s); %d unresolved, %d critical. "
                "ISO 10002: each unresolved one names the recovery owed."
                % (
                    len(complaints),
                    span,
                    len(open_c),
                    len(critical),
                )
            )
            return summary, "%d received, %d open" % (len(complaints), len(open_c)), len(open_c)
        if kind == "process_performance":
            ncrs = (
                env["fix.ncr"]
                .sudo()
                .search(self._scoped(self._window_domain("create_date", window)))
            )
            majors = ncrs.filtered(lambda n: n.severity in ("major", "critical"))
            copq_rows = self._copq_in_window(window)
            copq_total = round(sum(float(c.amount or 0.0) for c in copq_rows), 2)
            summary = (
                "%d NCR(s) raised (%s), %d major/critical; CoPQ BDT %.2f over %d "
                "period record(s) in the window."
                % (len(ncrs), span, len(majors), copq_total, len(copq_rows))
            )
            return summary, "%d NCRs, CoPQ %.2f" % (len(ncrs), copq_total), len(ncrs)
        if kind == "nonconformities":
            capas = (
                env["fix.capa"]
                .sudo()
                .search(self._scoped(self._window_domain("create_date", window)))
            )
            open_capas = capas.filtered(lambda c: c.state != "closed")
            overdue = open_capas.filtered(lambda c: c.due_on and c.due_on < today)
            summary = (
                "%d CAPA(s) opened (%s); %d unclosed, %d overdue, %d verified awaiting "
                "closure."
                % (
                    len(capas),
                    span,
                    len(open_capas),
                    len(overdue),
                    len(capas.filtered(lambda c: c.state == "verified")),
                )
            )
            return summary, "%d open, %d overdue" % (len(open_capas), len(overdue)), len(open_capas)
        if kind == "audit_results":
            audits = (
                env["fix.internal.audit"]
                .sudo()
                .search(self._scoped(self._window_domain("scheduled_on", window, date_field=True)))
            )
            certs = (
                env["fix.qms.certification"]
                .sudo()
                .search(self._scoped(self._window_domain("audit_date", window, date_field=True)))
            )
            cert_bits = sorted("%s: %s" % (c.name, c.result) for c in certs)
            parts = [
                "%d internal audit(s) in the window (%d executed/reported)"
                % (len(audits), len(audits.filtered(lambda a: a.state in ("executed", "reported"))))
            ]
            findings = env.get("fix.audit.finding")
            if findings:
                rows = findings.sudo().search(
                    self._scoped(self._window_domain("audit_date", window, date_field=True))
                )
                parts.append(
                    "%d governance audit finding(s) (%d still open/submitted)"
                    % (
                        len(rows),
                        len(rows.filtered(lambda f: f.capa_status != "closed")),
                    )
                )
            if cert_bits:
                parts.append("certification: " + "; ".join(cert_bits))
            summary = "%s (%s). %s." % ("; ".join(parts), span, "ISO 9.2 results feed 9.3")
            return (
                summary,
                "%d audits, %d certs" % (len(audits), len(certs)),
                len(audits) + len(certs),
            )
        if kind == "external_providers":
            suppliers = (
                env["fix.ncr"]
                .sudo()
                .search(
                    [
                        *self._scoped(self._window_domain("create_date", window)),
                        ("source", "=", "supplier"),
                    ]
                )
            )
            open_sup = suppliers.filtered(lambda n: n.state != "closed")
            summary = (
                "%d supplier NCR(s) (%s), %d unclosed — external provider "
                "performance the review must weigh (9.3.2 c.7)."
                % (len(suppliers), span, len(open_sup))
            )
            return summary, "%d supplier NCRs" % len(suppliers), len(open_sup)
        # ---- A10 deep audit (2026-11-22, A1-F04): the six missing
        # considerations ISO 9001:2015 9.3.2 requires. Each still counts
        # records the system holds; the judgement itself is the review's.
        if kind == "issues_changes":
            Regulatory = env.get("fix.grc.regulatory.change")
            changes = (
                Regulatory.sudo().search(
                    self._scoped(self._window_domain("effective_on", window, date_field=True))
                )
                if Regulatory is not None
                else Regulatory
            )
            summary = (
                "%d regulatory change(s) identified (%s); the review records the "
                "changes in internal and external issues it decides to act on "
                "(9.3.2 b)."
                % (len(changes) if changes else 0, span)
            )
            return summary, "%d regulatory changes" % (len(changes) if changes else 0), 0
        if kind == "objectives_attainment":
            objectives = env["fix.qms.objective"].sudo().search(
                self._scoped([("period", "<=", date_to.strftime("%Y"))])
            )
            measured = objectives.filtered(lambda o: o.actual or o.attainment)
            attained = objectives.filtered(
                lambda o: o.attainment >= 100.0 if o.higher_is_better else o.attainment > 0.0
            )
            summary = (
                "%d quality objective(s), %d with a measurement, %d at target — "
                "the extent to which the objectives are met (9.3.2 c.2)."
                % (len(objectives), len(measured), len(attained))
            )
            return summary, "%d of %d at target" % (len(attained), len(objectives)), max(
                len(objectives) - len(attained), 0
            )
        if kind == "monitoring_results":
            Checklist = env["fix.qc.checklist"]
            checks = Checklist.sudo().search(
                self._scoped(self._window_domain("checked_at", window))
            )
            failed = checks.filtered(lambda c: c.state == "failed")
            Test = env.get("fix.grc.control.test")
            tests = (
                Test.sudo().search(self._scoped(self._window_domain("tested_on", window, date_field=True)))
                if Test is not None
                else Test
            )
            summary = (
                "%d QC inspection(s) completed (%s), %d failed; %s — the "
                "monitoring and measurement results (9.3.2 c.5)."
                % (
                    len(checks),
                    span,
                    len(failed),
                    (
                        "%d control test(s), %d not fully effective"
                        % (len(tests), len(tests.filtered(lambda t: t.result != "effective")))
                        if tests is not None
                        else "no control-test register installed"
                    ),
                )
            )
            return summary, "%d inspections, %d failed" % (len(checks), len(failed)), len(failed)
        if kind == "resources_adequacy":
            branches = env["fix.branch"].sudo().search_count([("active", "=", True)]) if "fix.branch" in env else 0
            employees = env["hr.employee"].sudo().search_count([("active", "=", True)])
            summary = (
                "On-roll: %d active employee(s) across %d active branch(es) (%s); "
                "the review records its judgement on the adequacy of resources "
                "(9.3.2 d) — people, infrastructure and environment for the "
                "operation of processes."
                % (employees, branches, span)
            )
            return summary, "%d on-roll, %d branches" % (employees, branches), 0
        if kind == "risk_effectiveness":
            Risk = env.get("fix.risk.register")
            risks = (
                Risk.sudo().search(self._scoped([]))
                if Risk is not None
                else Risk
            )
            assessed = (
                risks.filtered(lambda r: r.residual_likelihood and r.residual_impact)
                if risks is not None
                else risks
            )
            summary = (
                "%d risk register entr(ies), %d with a residual assessed%s — "
                "the effectiveness of actions taken on risks and opportunities "
                "(9.3.2 e) is the review's judgement on that register."
                % (
                    len(risks) if risks is not None else 0,
                    len(assessed) if assessed is not None else 0,
                    "" if risks is not None else " (no risk register installed)",
                )
            )
            return summary, "%d risks, %d assessed" % (
                len(risks) if risks is not None else 0,
                len(assessed) if assessed is not None else 0,
            ), 0
        if kind == "improvement_opportunities":
            capas = env["fix.capa"].sudo().search(
                self._scoped(self._window_domain("create_date", window))
            )
            effective = capas.filtered(lambda c: c.effectiveness_result == "effective")
            # the knowledge library's own flag (AUT-KMS-17): articles the
            # field repeatedly rejected — reached through env.get (no
            # dependency on cd_knowledge)
            Article = env.get("fix.knowledge.article")
            flagged = (
                Article.sudo().search_count([("flagged_on", "!=", False)])
                if Article is not None
                else 0
            )
            summary = (
                "%d CAPA(s) in the window, %d verified effective; %d flagged "
                "knowledge article(s) — the opportunities for improvement the "
                "review decides to take (9.3.2 f)."
                % (
                    len(capas),
                    len(effective),
                    flagged,
                )
            )
            return summary, "%d effective CAPAs" % len(effective), 0
        raise UserError("Unknown review input kind: %s" % kind)

    def action_pull_inputs(self):
        """ISO 9.3.2 (A10 P1-6, M23-8): pull the review's inputs from the
        live system — one line per required kind, each a count of records
        that exist, stamped with when it was pulled. Typed inputs are not
        inputs: the summary fields are guarded and only this action writes
        them."""
        _require_quality_manager(self.env, "pull the management review inputs")
        Input = self.env["fix.qms.review.input"].sudo()
        for rec in self:
            if rec.state == "closed":
                raise UserError(
                    "'%s' is closed — a closed review's inputs are the record kept." % rec.name
                )
            window = rec._review_window()
            for kind, _label in REVIEW_INPUT_KINDS:
                summary, headline, count = rec._input_snapshot(kind, window)
                vals = {
                    "summary": summary,
                    "metric": headline,
                    "source_count": count,
                    "pulled_on": fields.Datetime.now(),
                }
                line = rec.input_ids.filtered(lambda i, k=kind: i.kind == k)
                if line:
                    line._guarded().write(vals)
                else:
                    Input.create(dict(vals, review_id=rec.id, kind=kind))
            rec.message_post(
                body="ISO 9.3.2 inputs pulled: %d section(s), window %s..%s."
                % (len(REVIEW_INPUT_KINDS), window[0] or "(first review)", window[1])
            )
        return True

    # ---- the meeting (9.3.1) and the outputs (9.3.3) ---------------------
    def action_hold(self):
        """ISO 9.3.1/9.3.2 (A10 P1-6, M23-8): a review is HELD by the Quality
        Manager only over a COMPLETE pulled input set, with the chairperson
        (top management) named."""
        _require_quality_manager(self.env, "hold a management review")
        for rec in self:
            if rec.state != "scheduled":
                raise UserError(
                    "'%s' is %s — hold a review that is scheduled." % (rec.name, rec.state)
                )
            if not rec.chairperson_id:
                raise UserError(
                    "Name the chairperson of '%s' — top management conducts the "
                    "review (ISO 9.3.1)." % rec.name
                )
            if rec.inputs_missing:
                have = set(rec.input_ids.mapped("kind"))
                missing = ", ".join(
                    sorted(label for kind, label in REVIEW_INPUT_KINDS if kind not in have)
                )
                raise UserError(
                    "Pull the inputs of '%s' first — missing: %s (ISO 9.3.2)." % (rec.name, missing)
                )
            rec._guarded().write({"state": "held"})
            rec.message_post(
                body="Review held by %s over %d pulled input section(s); %d tracked "
                "action(s) open (ISO 9.3)."
                % (self.env.user.name, len(rec.input_ids), rec.open_actions)
            )
        return True

    def _assert_outputs_tracked(self):
        """ISO 9.3.3: the outputs are opportunities, changes, resource needs
        and ACTIONS — as tracked lines with owners, not prose."""
        for rec in self:
            prose = (rec.decisions or "").strip()
            if prose and not rec.action_ids:
                raise UserError(
                    "'%s' records decisions only as prose — add them as tracked "
                    "actions with owners and due dates (ISO 9.3.3)." % rec.name
                )
            if not prose and not rec.action_ids:
                raise UserError(
                    "A management review has outputs: record '%s' decisions and at "
                    "least one tracked action (ISO 9.3.3)." % rec.name
                )

    def action_close(self, justification=None):
        """ISO 9.3.3 (A10 P1-6, M23-8): the Quality Manager SUBMITS the held
        review for closure — top management (DOFA Tier 5) decides it from
        the M63 inbox. The closure write itself is action_apply_closure,
        which only the engine may run."""
        _require_quality_manager(self.env, "submit a management review for closure")
        for rec in self:
            if rec.state == "closed":
                raise UserError(
                    "'%s' is closed — a closed review does not reopen (A10 P1-6)." % rec.name
                )
            if rec.state != "held":
                raise UserError("Hold '%s' before closing it (ISO 9.3)." % rec.name)
            rec._assert_outputs_tracked()
            rec.action_request_approval(
                justification=justification
                or "Close the %s management review: %d tracked action(s), %d open."
                % (rec.review_date, len(rec.action_ids), rec.open_actions)
            )
        return True

    def action_apply_closure(self):
        """The engine's apply path (M63): runs in the deciding approver's
        session with the task in context — the ONLY write to `closed`."""
        self._approval_assert_routed()
        task = self._approval_task()
        for rec in self:
            if rec.state == "closed":
                raise UserError(
                    "'%s' is closed — a closed review does not reopen (A10 P1-6)." % rec.name
                )
            if rec.state != "held":
                raise UserError("Hold '%s' before closing it (ISO 9.3)." % rec.name)
            rec._assert_outputs_tracked()
            approver = task.on_behalf_of_id or rec.env.user
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_on": fields.Date.context_today(rec),
                    "closed_by_id": (approver.employee_id or rec.chairperson_id).id,
                }
            )
            rec.message_post(
                body="Review closed by %s (top management, DOFA Tier 5): %d tracked "
                "action(s), %d open (ISO 9.3.3)."
                % (approver.name, len(rec.action_ids), rec.open_actions)
            )
        return True


class FixQmsReviewInput(models.Model):
    """One pulled ISO 9.3.2 input section — a snapshot the system counted."""

    _name = "fix.qms.review.input"
    _description = "Management Review Input (ISO 9.3.2)"
    _inherit = ["fix.guarded.mixin"]
    _order = "review_id, id"

    review_id = fields.Many2one("fix.qms.review", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    kind = fields.Selection(REVIEW_INPUT_KINDS, required=True)
    summary = fields.Text()
    metric = fields.Char(string="Headline")
    source_count = fields.Integer()
    pulled_on = fields.Datetime()

    _one_line_per_kind = models.Constraint(
        "UNIQUE (review_id, kind)",
        "Each ISO 9.3.2 input kind appears once per review (A10 P1-6).",
    )

    def _fix_guarded_fields(self) -> set:
        # the snapshot is PULLED, never typed: a summary somebody wrote by
        # hand is an audit finding, not an input (A10 P1-6, M23-8)
        return {"review_id", "kind", "summary", "metric", "source_count", "pulled_on"}


class FixQmsReviewAction(models.Model):
    """One tracked ISO 9.3.3 output: an action with an owner and a date."""

    _name = "fix.qms.review.action"
    _description = "Management Review Action (ISO 9.3.3)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    review_id = fields.Many2one("fix.qms.review", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Text(string="Decision / Action", required=True)
    owner_id = fields.Many2one("hr.employee", string="Owner", required=True, index=True)
    due_on = fields.Date(string="Due")
    state = fields.Selection(
        [("open", "Open"), ("done", "Done")], required=True, default="open", tracking=True
    )
    done_on = fields.Date(copy=False)
    done_by_id = fields.Many2one("hr.employee", string="Done by", copy=False)

    def _fix_guarded_fields(self) -> set:
        # completion is stamped by action_done — the owner's or the QM's act,
        # with the date the system knows, not a typed one
        return {"state", "done_on", "done_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(self._fix_guarded_fields())
        if set(self.mapped("state")) == {"done"}:
            # the completed action is the record kept
            locked |= {"review_id", "name", "owner_id", "due_on"}
        return locked

    def action_done(self, note=""):
        """The tracked action is completed by its owner or the Quality
        Manager (A10 P1-6): whoever it is, the date and the doer are the
        system's stamp."""
        for rec in self:
            if rec.state != "open":
                raise UserError("Tracked action %d is already done." % rec.id)
            if not self.env.su:
                actor = self.env.user.employee_id
                if actor != rec.owner_id and not self.env.user.has_group(QM_GROUP):
                    raise UserError(
                        "A tracked action is completed by its owner or the Quality "
                        "Manager (A10 P1-6)."
                    )
            rec._guarded().write(
                {
                    "state": "done",
                    "done_on": fields.Date.context_today(rec),
                    "done_by_id": (self.env.user.employee_id or rec.owner_id).id,
                }
            )
            if (note or "").strip():
                rec.message_post(body=note)
        return True


class FixApprovalMatrixQmsReview(models.Model):
    """A10 P1-6 (M23-8): lets a DoA matrix row target the review closure
    (narrowing the coded Tier 5 authority per A11 E3)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("qms_review_closure", "Management Review Closure (ISO 9.3)")],
        ondelete={"qms_review_closure": "cascade"},
    )


class FixQmsCopq(models.Model):
    _name = "fix.qms.copq"
    _description = "Cost of Poor Quality"
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    period = fields.Char(required=True, help="YYYY-MM")
    category = fields.Selection(
        [
            ("rework", "Rework"),
            ("scrap", "Scrap"),
            ("warranty", "Warranty"),
            ("complaint", "Complaint Handling"),
            ("inspection", "Inspection"),
            ("downtime", "Downtime"),
        ],
        required=True,
        default="rework",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    source_ref = fields.Char()
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.qms.copq") or "COPQ/New"
        return super().create(vals_list)
