# fix_qms — M23: NCR, CAPA, internal audit; the stub closures (P08-M06).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish


class FixNcr(models.Model):
    """A non-conformance — from any source. Journey 14's middle."""

    _name = "fix.ncr"
    _description = "Non-Conformance Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: ("NCR/New"))
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

    def action_dispose(self, disposition, note="", approved_by=None):
        """Record the disposition of the nonconforming output."""
        for rec in self:
            if rec.state == "closed":
                raise UserError("A closed NCR cannot be re-dispositioned")
            rec.write(
                {
                    "disposition": disposition,
                    "disposition_note": note or rec.disposition_note,
                    "concession_approved_by_id": approved_by or rec.concession_approved_by_id.id,
                }
            )

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
            rec.write({"root_cause": root_cause, "state": "root_cause"})

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
        self.state = "capa_open"
        publish(
            self.env,
            "ncr.capa_opened",
            "fix.ncr",
            self.id,
            {"ncr": self.name, "severity": self.severity},
        )
        return capa

    def action_close(self):
        for rec in self:
            if rec.severity == "critical":
                # the One2many is capa_id — `rec.capa` raised AttributeError
                capa = rec.capa_id.filtered(lambda c: c.state == "closed")
                if not capa:
                    raise UserError(
                        "A CRITICAL NCR closes only through a VERIFIED, "
                        "CLOSED CAPA (CON-11 discipline)"
                    )
            rec.state = "closed"
            publish(self.env, "ncr.closed", "fix.ncr", rec.id, {"ncr": rec.name})


class FixCapa(models.Model):
    """Corrective AND preventive action with verification and closure."""

    _name = "fix.capa"
    _description = "CAPA"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
        help="Prevents recurrence; empty preventive action on a MAJOR+ " "NCR is a QMS defect"
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
            rec.state = "implemented"

    def action_verify(self, note, effective=True, verifier=None):
        for rec in self:
            if rec.state != "implemented":
                raise UserError("Verify only after implementation")
            rec.write(
                {
                    "state": "verified",
                    "verification_note": note,
                    "effectiveness_result": "effective" if effective else "not_effective",
                    "verified_on": fields.Date.context_today(rec),
                    "verified_by_id": verifier or rec.verified_by_id.id,
                }
            )
            publish(self.env, "capa.verified", "fix.capa", rec.id, {"ncr": rec.ncr_id.name})

    def action_close(self):
        for rec in self:
            if rec.state != "verified":
                raise UserError("Closure follows verification")
            rec.state = "closed"

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


class FixInternalAudit(models.Model):
    """The ISO 9001:2015 internal audit programme — CON-11's evidence base
    and the P11 field auditor's queue."""

    _name = "fix.internal.audit"
    _description = "Internal Audit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheduled_on desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True)
    scheduled_on = fields.Date(required=True)
    auditor_id = fields.Many2one("hr.employee", string="Auditor", required=True)
    scope = fields.Char(
        required=True, help="e.g. ISO 9001:2015 clause 8.5 production " "control at Dhaka branch"
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
    ncr_ids = fields.One2many("fix.ncr", "audit_id", string="Findings")

    def action_execute(self, payload=None):
        """P11 executes the checklist in the field, offline; the payload
        lands here verbatim."""
        for rec in self:
            if payload:
                rec.offline_payload = payload
            rec.state = "executed"

    def action_report(self):
        for rec in self:
            majors = rec.ncr_ids.filtered(lambda n: n.severity in ("major", "critical"))
            rec.state = "reported"
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
        """Failing a checklist raises an NCR in M23 — the takeover."""
        for rec in self:
            ncr = self.env["fix.ncr"].create(
                {
                    "source": "qc",
                    "order_id": rec.order_id.id,
                    "severity": "major",
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

    def action_raise_ncr(self):
        """The REAL NCR (the stub wrote NCR-STUB/<id> with an expiry)."""
        res = super().action_raise_ncr()
        for complaint in self:
            ncr = self.env["fix.ncr"].create(
                {
                    "source": "complaint",
                    "complaint_id": complaint.id,
                    "severity": "major" if complaint.severity != "critical" else "critical",
                    "description": complaint.description,
                }
            )
            complaint.write({"ncr_id": ncr.id})
            # Backfill the legacy stub ref for traceability of the closure
            if complaint.ncr_stub_ref and not complaint.ncr_stub_ref.startswith("NCR-STUB-CLOSED"):
                complaint.write(
                    {"ncr_stub_ref": "NCR-STUB-CLOSED/%s->%s" % (complaint.id, ncr.name)}
                )
            publish(
                self.env,
                "complaint.ncr_linked",
                "fix.complaint",
                complaint.id,
                {"ncr": ncr.name, "stub": False},
            )
        return res

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
