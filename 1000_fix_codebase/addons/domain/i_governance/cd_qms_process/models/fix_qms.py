# fix_qms — M23: NCR, CAPA, internal audit; the stub closures (P08-M06).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

QM_GROUP = "cd_qms_process.group_qms_quality_manager"


def _require_quality_manager(env, why):
    """A10 Q1/Q2/Q3: the Quality Manager role decides, not whoever calls."""
    if env.su:
        return
    if not env.user.has_group(QM_GROUP):
        raise UserError("Only the Quality Manager may %s (A10 Q-series)." % why)


class FixNcr(models.Model):
    """A non-conformance — from any source. Journey 14's middle."""

    _name = "fix.ncr"
    _description = "Non-Conformance Record"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "NCR/New")
    source = fields.Selection(
        [
            ("service_order", "Service Order"),
            ("qc", "QC Checklist"),
            ("complaint", "Complaint (M34)"),
            ("supplier", "Supplier (M42)"),
            ("audit", "Internal Audit"),
        ],
        required=True,
        default="service_order",
    )
    order_id = fields.Many2one("fix.service.order", string="Service Order", ondelete="set null")
    complaint_id = fields.Many2one("fix.complaint", string="Complaint", ondelete="set null")
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")],
        default="minor",
        required=True,
        tracking=True,
    )
    description = fields.Text(required=True)
    root_cause = fields.Text()
    # A10 Q2 (M23-3): ISO 9001 8.7.1(f) — the containment of the
    # nonconformity's effect is a record of its own, required before a
    # MAJOR/CRITICAL NCR may close.
    containment = fields.Text(
        string="Containment",
        tracking=True,
        help="What was done to contain the effect of the nonconformity "
        "(ISO 9001 8.7.1 f). Required before a MAJOR/CRITICAL NCR closes.",
    )
    # ISO 9001 8.7.1: what was done with the nonconforming output, and 8.7.2:
    # the record of it. A concession (use-as-is) needs an authorised approver.
    disposition = fields.Selection(
        [
            ("rework", "Rework to conform"),
            ("repair", "Repair (concession to repair)"),
            ("replace", "Replace"),
            ("return", "Return to customer / supplier"),
            ("scrap", "Scrap / destroy"),
            ("use_as_is", "Use as is (concession by authority)"),
            ("pending", "Not yet dispositioned"),
        ],
        default="pending",
        required=True,
        tracking=True,
        help="ISO 9001 8.7.1: the action taken on the nonconforming output.",
    )
    disposition_note = fields.Text()
    concession_approved_by_id = fields.Many2one(
        "hr.employee",
        string="Concession approved by",
        help="Required for 'Use as is': ISO 9001 8.7.1 requires an authorised concession.",
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("root_cause", "Root Cause Identified"),
            ("capa_open", "CAPA Open"),
            ("verification", "Verification"),
            ("closed", "Closed"),
        ],
        default="new",
        required=True,
        tracking=True,
    )
    capa_id = fields.One2many("fix.capa", "ncr_id", string="CAPA")

    def _fix_guarded_fields(self) -> set:
        """A10 Q2 (M23-2/-3): the lifecycle and the disposition record
        change only through the actions — a plain write must not close an
        NCR or grant itself a concession."""
        return {"state", "disposition", "concession_approved_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(self._fix_guarded_fields())
        if set(self.mapped("state")) == {"closed"}:
            # the closed record is append-only (BRU-QMS-11)
            locked |= {"root_cause", "containment", "disposition_note", "description"}
        return locked

    @api.constrains("disposition", "concession_approved_by_id", "disposition_note")
    def _check_disposition(self):
        for rec in self:
            if rec.disposition == "use_as_is" and not rec.concession_approved_by_id:
                raise ValidationError(
                    "A 'use as is' disposition needs the authorising employee "
                    "(ISO 9001 8.7.1 concession)."
                )
            if (
                rec.disposition not in ("pending", "use_as_is")
                and not (rec.disposition_note or "").strip()
            ):
                raise ValidationError(
                    "Record what was done for the %s disposition (ISO 9001 8.7.2)."
                    % rec.disposition
                )

    def action_dispose(self, disposition, note=""):
        """Record the disposition of the nonconforming output.

        A10 Q2 (M23-4): a 'use as is' concession is authorised by the
        acting Quality Manager (stamped from the session), never by an
        employee the caller names."""
        for rec in self:
            if rec.state == "closed":
                raise UserError("A closed NCR cannot be re-dispositioned")
            vals = {
                "disposition": disposition,
                "disposition_note": note or rec.disposition_note,
            }
            if disposition == "use_as_is":
                _require_quality_manager(self.env, "authorise a use-as-is concession")
                employee = self.env.user.employee_id
                if not employee:
                    raise UserError(
                        "The concession approver needs an employee record "
                        "(the session user has none)."
                    )
                vals["concession_approved_by_id"] = employee.id
            rec._guarded().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("fix.ncr") or "NCR/%s" % fields.Date.today()
            )
        return super().create(vals_list)

    def action_set_root_cause(self, root_cause):
        for rec in self:
            if rec.state != "new":
                raise UserError("Root cause lands on a NEW NCR")
            rec._guarded().write({"root_cause": root_cause, "state": "root_cause"})

    def action_open_capa(self, corrective_action, preventive_action="", owner_id=None):
        """Open the CAPA for this NCR (journey 14).

        fix.capa REQUIRES its corrective action and an accountable owner;
        the former argument-less call created neither and failed on the NOT
        NULL columns for every NCR. The owner defaults to the acting user's
        employee."""
        self.ensure_one()
        if self.state != "root_cause":
            raise UserError("Identify the root cause before CAPA")
        if not (corrective_action or "").strip():
            raise UserError("A CAPA needs its corrective action")
        owner = self.env["hr.employee"].browse(owner_id) if owner_id else self.env.user.employee_id
        if not owner:
            raise UserError("A CAPA needs an accountable owner (an employee)")
        capa = self.env["fix.capa"].create(
            {
                "ncr_id": self.id,
                "severity": self.severity,
                "corrective_action": corrective_action,
                "preventive_action": preventive_action or False,
                "owner_id": owner.id,
            }
        )
        self._guarded().write({"state": "capa_open"})
        publish(
            self.env,
            "ncr.capa_opened",
            "fix.ncr",
            self.id,
            {"ncr": self.name, "severity": self.severity},
        )
        return capa

    def action_close(self):
        """A10 Q2 (M23-3): an NCR closes with its full record — disposition,
        containment and root cause for MAJOR/CRITICAL, and a CAPA that was
        VERIFIED EFFECTIVE (a 'not effective' CAPA blocks closure)."""
        for rec in self:
            if rec.state == "closed":
                raise UserError("%s is already closed." % rec.name)
            if rec.disposition == "pending":
                raise UserError(
                    "Record the disposition of %s before closing it (ISO 9001 8.7.1)." % rec.name
                )
            if rec.severity in ("major", "critical"):
                if not (rec.containment or "").strip():
                    raise UserError(
                        "Record the containment of %s before closing it (ISO 9001 "
                        "8.7.1 f)." % rec.name
                    )
                if not (rec.root_cause or "").strip():
                    raise UserError("Identify the root cause of %s before closing it." % rec.name)
                # reads the GUARDED capa state/effectiveness — a CAPA that
                # merely "closed" without a verified-effective verdict does
                # not open this gate
                effective_capa = rec.capa_id.filtered(
                    lambda c: c.state == "closed" and c.effectiveness_result == "effective"
                )
                if not effective_capa:
                    raise UserError(
                        # one source line: the control-suite grep test pins this phrase
                        "A %s NCR closes only through a VERIFIED-EFFECTIVE, CLOSED CAPA (ISO 9001 10.2.1 d — CON-11 discipline)."
                        % rec.severity.upper()
                    )
            rec._guarded().write({"state": "closed"})
            publish(self.env, "ncr.closed", "fix.ncr", rec.id, {"ncr": rec.name})


class FixCapa(models.Model):
    """Corrective AND preventive action with verification and closure."""

    _name = "fix.capa"
    _description = "CAPA"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    ncr_id = fields.Many2one("fix.ncr", required=True, ondelete="cascade")
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")],
        default="minor",
        required=True,
        tracking=True,
    )
    corrective_action = fields.Text(required=True)
    preventive_action = fields.Text(
        help="Prevents recurrence; empty preventive action on a MAJOR+ NCR is a QMS defect"
    )
    owner_id = fields.Many2one("hr.employee", string="Owner", required=True)
    due_on = fields.Date()
    state = fields.Selection(
        [
            ("open", "Open"),
            ("implemented", "Implemented"),
            ("verified", "Verified"),
            ("closed", "Closed"),
        ],
        default="open",
        required=True,
        tracking=True,
    )
    verification_note = fields.Text()
    # ISO 9001 10.2.1(d): the corrective action's effectiveness must be reviewed;
    # 10.2.2 requires the results retained as documented information.
    effectiveness_result = fields.Selection(
        [
            ("pending", "Not yet verified"),
            ("effective", "Effective"),
            ("not_effective", "Not effective — reopen"),
        ],
        default="pending",
        required=True,
        tracking=True,
    )
    verified_on = fields.Date()
    verified_by_id = fields.Many2one("hr.employee", string="Verified by")
    # A10 Q1 (M23-1): who implemented — the verifier may be neither the
    # owner nor the implementer
    implemented_by_id = fields.Many2one("hr.employee", string="Implemented by")

    def _fix_guarded_fields(self) -> set:
        """A10 Q1 (M23-2): the verdict record is system-stamped. verified_by
        was a caller-typed parameter — anyone named anyone, including
        themself, and a 'not effective' verdict closed anyway."""
        return {"state", "effectiveness_result", "verified_on", "verified_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(self._fix_guarded_fields())
        if set(self.mapped("state")) == {"closed"}:
            # the closed corrective/preventive actions freeze too
            locked |= {"corrective_action", "preventive_action", "verification_note"}
        return locked

    @api.constrains("effectiveness_result", "verification_note")
    def _check_effectiveness(self):
        for rec in self:
            if rec.effectiveness_result != "pending" and not (rec.verification_note or "").strip():
                raise ValidationError(
                    "The effectiveness verdict needs the verification evidence in the note "
                    "(ISO 9001 10.2.2)."
                )

    def action_implement(self):
        for rec in self:
            if rec.severity in ("major", "critical") and not rec.preventive_action:
                raise UserError("A MAJOR/CRITICAL CAPA requires a PREVENTIVE action")
            rec._guarded().write(
                {
                    "state": "implemented",
                    "implemented_by_id": (self.env.user.employee_id or rec.implemented_by_id).id,
                }
            )

    def action_verify(self, note=None, effective=True):
        """A10 Q1 (M23-1): the effectiveness verdict is given by the acting
        QUALITY MANAGER (never a caller-named verifier), who is neither the
        CAPA owner nor its implementer. A 'not effective' verdict REOPENS
        the CAPA — it can never close on it."""
        _require_quality_manager(self.env, "verify a CAPA's effectiveness")
        verifier = self.env.user.employee_id
        if not verifier and not self.env.su:
            raise UserError("The verifier needs an employee record (the session user has none).")
        if isinstance(effective, str):
            # the workspace prompt arrives as text — "no" is an honest answer
            effective = effective.strip().lower() in ("yes", "y", "true", "1", "effective")
        for rec in self:
            if rec.state != "implemented":
                raise UserError("Verify only after implementation")
            what = "the CAPA of %s" % rec.ncr_id.name
            if not (note or "").strip():
                raise UserError(
                    "The effectiveness verdict on %s needs the verification evidence "
                    "in the note (ISO 9001 10.2.2)." % what
                )
            if verifier and verifier == rec.owner_id:
                raise UserError(
                    "The owner of %s cannot verify their own action's effectiveness "
                    "(A10 Q1)." % what
                )
            if verifier and rec.implemented_by_id and verifier == rec.implemented_by_id:
                raise UserError(
                    "The implementer of %s cannot verify its effectiveness (A10 Q1)." % what
                )
            verdict = "effective" if effective else "not_effective"
            rec._guarded().write(
                {
                    "state": "verified" if effective else "open",
                    "verification_note": note,
                    "effectiveness_result": verdict,
                    "verified_on": fields.Date.context_today(rec),
                    "verified_by_id": verifier.id if verifier else False,
                }
            )
            publish(
                self.env,
                "capa.verified",
                "fix.capa",
                rec.id,
                {"ncr": rec.ncr_id.name, "effective": bool(effective)},
            )

    def action_close(self):
        for rec in self:
            if rec.effectiveness_result == "not_effective":
                raise UserError(
                    "The CAPA of %s was verified NOT EFFECTIVE — it reopens and is "
                    "reworked, never closed on a failed verdict (A10 Q1)." % rec.ncr_id.name
                )
            if rec.state != "verified":
                raise UserError(
                    "Closure follows verification — the CAPA of %s stands in state "
                    "'%s'." % (rec.ncr_id.name, rec.state)
                )
            rec._guarded().write({"state": "closed"})

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


class FixInternalAudit(models.Model):
    """The ISO 9001:2015 internal audit programme — CON-11's evidence base
    and the P11 field auditor's queue."""

    _name = "fix.internal.audit"
    _description = "Internal Audit"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "scheduled_on desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True)
    scheduled_on = fields.Date(required=True)
    auditor_id = fields.Many2one("hr.employee", string="Auditor", required=True)
    scope = fields.Char(
        required=True, help="e.g. ISO 9001:2015 clause 8.5 production control at Dhaka branch"
    )
    offline_payload = fields.Text(
        string="Offline Capture (P11)",
        help="JSON captured by the P11 field-auditor application offline; "
        "synced when connectivity returns",
    )
    state = fields.Selection(
        [("planned", "Planned"), ("executed", "Executed"), ("reported", "Reported")],
        default="planned",
        required=True,
        tracking=True,
    )
    # A10 Q3 (M23-5): WHICH processes were audited — the objectivity check
    # (auditor ≠ process owner) is only possible when the scope is linked
    # to the process register instead of free text
    process_ids = fields.Many2many(
        "fix.qms.process",
        "fix_internal_audit_process_rel",
        "audit_id",
        "process_id",
        string="Audited Processes",
        help="The QMS processes in scope; the auditor may not own any of them "
        "(ISO 9001 9.2 objectivity and impartiality).",
    )
    ncr_ids = fields.One2many("fix.ncr", "audit_id", string="Findings")

    def _fix_guarded_fields(self) -> set:
        """A10 Q3 (M23-2): the programme state moves only through the
        actions — a plain write cannot mark an audit reported without its
        evidence."""
        return {"state"}

    def action_execute(self, payload=None):
        """P11 executes the checklist in the field, offline; the payload
        lands here verbatim.

        A10 Q3 (M23-5): the auditor may not audit a process they own —
        ISO 9001 9.2 requires objectivity and impartiality, and the free-text
        scope used to hide exactly that conflict."""
        for rec in self:
            if not self.env.su:
                conflicts = rec.process_ids.filtered(
                    lambda p, r=rec: p.process_owner_id == r.auditor_id
                )
                if conflicts:
                    raise UserError(
                        "The auditor of %s owns the audited process %s — an auditor "
                        "may not audit their own process (ISO 9001 9.2, A10 Q3)."
                        % (rec.scope or "Audit %d" % rec.id, ", ".join(conflicts.mapped("code")))
                    )
            vals = {"state": "executed"}
            if payload:
                vals["offline_payload"] = payload
            rec._guarded().write(vals)

    def action_report(self):
        """A10 Q3 (M23-6): a report is filed on EXECUTED evidence, and every
        MAJOR/CRITICAL finding leaves the audit with its CAPA raised — the
        report is not a checkbox, it is the record that commits the
        findings to the corrective-action system."""
        for rec in self:
            if rec.state != "executed":
                raise UserError(
                    "Report %s only after it is executed (the checklist evidence "
                    "must be in first)." % (rec.scope or "Audit %d" % rec.id)
                )
            if not (rec.offline_payload or "").strip():
                raise UserError(
                    "Reporting %s needs the executed checklist evidence (the "
                    "offline capture payload, ISO 9001 9.2.2)." % (rec.scope or "Audit %d" % rec.id)
                )
            majors = rec.ncr_ids.filtered(lambda n: n.severity in ("major", "critical"))
            auto_capas = self.env["fix.capa"]
            for ncr in majors.filtered(lambda n: not n.capa_id):
                owner = rec.process_ids[:1].process_owner_id or rec.auditor_id
                auto_capas |= self.env["fix.capa"].create(
                    {
                        "ncr_id": ncr.id,
                        "severity": ncr.severity,
                        "corrective_action": "Address the audit finding %s: %s"
                        % (ncr.name, (ncr.description or "").strip()),
                        "owner_id": owner.id,
                    }
                )
                if ncr.state in ("new", "root_cause"):
                    ncr._guarded().write({"state": "capa_open"})
            rec._guarded().write({"state": "reported"})
            publish(
                self.env,
                "audit.reported",
                "fix.internal.audit",
                rec.id,
                {
                    "branch": rec.branch_id.name,
                    "major_findings": len(majors),
                    # CON-11: zero major non-conformances traced to SYSTEMS
                    "systems_traced": rec.nccr_systems_traced(),
                },
            )

    def nccr_systems_traced(self):
        """CON-11's question: do any MAJOR findings trace to SYSTEMS (a
        process/control defect) rather than isolated human error?"""
        self.ensure_one()
        for ncr in self.ncr_ids:
            if (
                ncr.severity in ("major", "critical")
                and ncr.root_cause
                and "system" in ncr.root_cause.lower()
            ):
                return True
        return False

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


class FixNcrAuditLink(models.Model):
    """Bridge: an audit finding IS an NCR with the audit as source."""

    _inherit = "fix.ncr"

    audit_id = fields.Many2one("fix.internal.audit", string="Audit", ondelete="set null")

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


class FixQcChecklistM23Ext(models.Model):
    """P08-M06-T04: QC ownership transfers to M23 (AR-005 — exactly one
    owning module). The M31 -> M23 stub CLOSES: a failed checklist raises
    a REAL NCR; the M23 linkage field replaces the intent-only stub."""

    _inherit = "fix.qc.checklist"

    ncr_id = fields.Many2one(
        "fix.ncr",
        string="NCR (M23)",
        ondelete="set null",
        help="The M23 non-conformance this failed "
        "checklist raised — the GV-005 stub "
        "(expiry 2027-03-31) is closed",
    )

    def action_fail_with_ncr(self):
        """Failing a checklist raises an NCR in M23 — the takeover.

        A10 S6 (M23-12): the raise is ONCE — a checklist already failed
        with its NCR keeps it instead of stacking a second NCR on the same
        failure, and the NCR carries the checklist's operating unit (it
        used to land with none)."""
        for rec in self:
            if rec.ncr_id and rec.state == "failed":
                continue  # already raised — the honest answer is no second NCR
            ncr = self.env["fix.ncr"].create(
                {
                    "source": "qc",
                    "order_id": rec.order_id.id,
                    "severity": "major",
                    "operating_unit_id": rec.operating_unit_id.id,
                    "description": "QC checklist failed for order %s" % rec.order_id.name,
                }
            )
            # The checklist state is guarded (A02 audit M01-6): a QMS failure
            # is a legitimate system transition, so it writes with the token.
            rec._guarded().write({"state": "failed", "ncr_id": ncr.id})
            publish(self.env, "qc.ncr_raised", "fix.qc.checklist", rec.id, {"ncr": ncr.name})

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


class FixComplaintM23Ext(models.Model):
    """P08-M06-T05: the M34 -> M23 and M42 -> M23 stubs CLOSE. The
    complaint's journey-14 linkage becomes real relations."""

    _inherit = "fix.complaint"

    ncr_id = fields.Many2one("fix.ncr", string="NCR", ondelete="set null")
    capa_id = fields.Many2one("fix.capa", string="CAPA", ondelete="set null")

    def _fix_guarded_fields(self) -> set:
        # A10 S6 (M23-12): the linkage is the system's record of the
        # hand-off, never a typed field — the audit linked an unrelated
        # CAPA to a critical complaint with a plain portal write and the
        # closure gate passed. ncr_id/capa_id move only through the
        # actions below.
        return super()._fix_guarded_fields() | {"ncr_id", "capa_id"}

    def action_raise_ncr(self):
        """The REAL NCR (the stub wrote NCR-STUB/<id> with an expiry).

        A10 S6 (M23-12): severity carries across 1:1 — every minor
        complaint used to land as a MAJOR NCR and inflated the major
        count — and the raise is ONCE per complaint."""
        res = super().action_raise_ncr()
        for complaint in self:
            if complaint.ncr_id:
                raise UserError(
                    "%s already carries its NCR %s — a complaint raises one "
                    "(A10 S6)." % (complaint.name, complaint.ncr_id.name)
                )
            ncr = self.env["fix.ncr"].create(
                {
                    "source": "complaint",
                    "complaint_id": complaint.id,
                    "severity": complaint.severity,
                    "operating_unit_id": complaint.operating_unit_id.id,
                    "description": complaint.description,
                }
            )
            vals = {"ncr_id": ncr.id}
            # Backfill the legacy stub ref for traceability of the closure
            if complaint.ncr_stub_ref and not complaint.ncr_stub_ref.startswith("NCR-STUB-CLOSED"):
                vals["ncr_stub_ref"] = "NCR-STUB-CLOSED/%s->%s" % (complaint.id, ncr.name)
            complaint._guarded().write(vals)
            publish(
                self.env,
                "complaint.ncr_linked",
                "fix.complaint",
                complaint.id,
                {"ncr": ncr.name, "severity": ncr.severity, "stub": False},
            )
        return res

    def action_link_capa(self, capa_id=None):
        """A10 S6 (M23-12): a critical complaint's closure gate reads
        capa_id, so the link is the Quality Manager's act over the REAL
        chain — complaint -> NCR -> the CAPA raised from that NCR. An
        unrelated CAPA typed into the field never satisfies the gate
        again."""
        _require_quality_manager(self.env, "link a complaint's CAPA")
        for complaint in self:
            if not complaint.ncr_id:
                raise UserError(
                    "Raise the NCR of %s first — the CAPA closes the loop the "
                    "NCR opens (A10 S6)." % complaint.name
                )
            capa = self.env["fix.capa"].browse(int(capa_id or 0)).exists()
            if not capa and len(complaint.ncr_id.capa_id) == 1:
                capa = complaint.ncr_id.capa_id  # the one CAPA of its own NCR
            if not capa:
                raise UserError(
                    "Name the CAPA raised from NCR %s of %s (A10 S6)."
                    % (complaint.ncr_id.name, complaint.name)
                )
            if capa.ncr_id != complaint.ncr_id:
                raise UserError(
                    "That CAPA belongs to NCR %s, not to %s — a complaint "
                    "closes on the CAPA of its own non-conformance (A10 S6)."
                    % (capa.ncr_id.name, complaint.ncr_id.name)
                )
            complaint._guarded().write({"capa_id": capa.id})
            complaint.message_post(
                body="CAPA of %s linked by %s (the closure gate now reads the "
                "real corrective action)." % (capa.ncr_id.name, self.env.user.name)
            )
        return True

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
