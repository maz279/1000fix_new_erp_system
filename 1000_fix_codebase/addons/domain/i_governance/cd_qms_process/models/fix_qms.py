# fix_qms — M23: NCR, CAPA, internal audit; the stub closures (P08-M06).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixNcr(models.Model):
    """A non-conformance — from any source. Journey 14's middle."""
    _name = "fix.ncr"
    _description = "Non-Conformance Record"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M23",
        "form": "NCR",
        "fields": ["source", "severity", "description", "order_id", "complaint_id",
                   "audit_id"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True,
                       default=lambda self: ("NCR/New"))
    source = fields.Selection(
        [("service_order", "Service Order"), ("qc", "QC Checklist"),
         ("complaint", "Complaint (M34)"), ("supplier", "Supplier (M42)"),
         ("audit", "Internal Audit")], required=True, default="service_order")
    order_id = fields.Many2one("fix.service.order", string="Service Order",
                               ondelete="set null")
    complaint_id = fields.Many2one("fix.complaint", string="Complaint",
                                   ondelete="set null")
    severity = fields.Selection([("minor", "Minor"), ("major", "Major"),
                                 ("critical", "Critical")],
                                default="minor", required=True, tracking=True)
    description = fields.Text(required=True)
    root_cause = fields.Text()
    state = fields.Selection(
        [("new", "New"), ("root_cause", "Root Cause Identified"),
         ("capa_open", "CAPA Open"), ("verification", "Verification"),
         ("closed", "Closed")],
        default="new", required=True, tracking=True)
    capa_id = fields.One2many("fix.capa", "ncr_id", string="CAPA")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("fix.ncr") \
                or "NCR/%s" % fields.Date.today()
        return super().create(vals_list)

    def action_set_root_cause(self, root_cause):
        for rec in self:
            if rec.state != "new":
                raise UserError("Root cause lands on a NEW NCR")
            rec.write({"root_cause": root_cause, "state": "root_cause"})

    def action_open_capa(self):
        for rec in self:
            if rec.state != "root_cause":
                raise UserError("Identify the root cause before CAPA")
            capa = self.env["fix.capa"].create({
                "ncr_id": rec.id, "severity": rec.severity})
            rec.state = "capa_open"
            publish(self.env, "ncr.capa_opened", "fix.ncr", rec.id,
                    {"ncr": rec.name, "severity": rec.severity})
            return capa

    def action_close(self):
        for rec in self:
            if rec.severity == "critical":
                capa = rec.capa.filtered(lambda c: c.state == "closed")
                if not capa:
                    raise UserError(
                        "A CRITICAL NCR closes only through a VERIFIED, "
                        "CLOSED CAPA (CON-11 discipline)")
            rec.state = "closed"
            publish(self.env, "ncr.closed", "fix.ncr", rec.id,
                    {"ncr": rec.name})


class FixCapa(models.Model):
    """Corrective AND preventive action with verification and closure."""
    _name = "fix.capa"
    _description = "CAPA"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M23",
        "form": "CAPA",
        "fields": ["ncr_id", "severity", "corrective_action", "owner_id",
                   "preventive_action", "due_on"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    ncr_id = fields.Many2one("fix.ncr", required=True, ondelete="cascade")
    severity = fields.Selection([("minor", "Minor"), ("major", "Major"),
                                 ("critical", "Critical")],
                                default="minor", required=True, tracking=True)
    corrective_action = fields.Text(required=True)
    preventive_action = fields.Text(
        help="Prevents recurrence; empty preventive action on a MAJOR+ "
             "NCR is a QMS defect")
    owner_id = fields.Many2one("hr.employee", string="Owner", required=True)
    due_on = fields.Date()
    state = fields.Selection(
        [("open", "Open"), ("implemented", "Implemented"),
         ("verified", "Verified"), ("closed", "Closed")],
        default="open", required=True, tracking=True)
    verification_note = fields.Text()

    def action_implement(self):
        for rec in self:
            if rec.severity in ("major", "critical") and not rec.preventive_action:
                raise UserError(
                    "A MAJOR/CRITICAL CAPA requires a PREVENTIVE action")
            rec.state = "implemented"

    def action_verify(self, note):
        for rec in self:
            if rec.state != "implemented":
                raise UserError("Verify only after implementation")
            rec.write({"state": "verified", "verification_note": note})
            publish(self.env, "capa.verified", "fix.capa", rec.id,
                    {"ncr": rec.ncr_id.name})

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

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True)
    scheduled_on = fields.Date(required=True)
    auditor_id = fields.Many2one("hr.employee", string="Auditor",
                                 required=True)
    scope = fields.Char(required=True,
                        help="e.g. ISO 9001:2015 clause 8.5 production "
                             "control at Dhaka branch")
    offline_payload = fields.Text(
        string="Offline Capture (P11)",
        help="JSON captured by the P11 field-auditor application offline; "
             "synced when connectivity returns")
    state = fields.Selection([("planned", "Planned"), ("executed", "Executed"),
                              ("reported", "Reported")],
                             default="planned", required=True, tracking=True)
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
            majors = rec.ncr_ids.filtered(
                lambda n: n.severity in ("major", "critical"))
            rec.state = "reported"
            publish(self.env, "audit.reported", "fix.internal.audit", rec.id,
                    {"branch": rec.branch_id.name,
                     "major_findings": len(majors),
                     # CON-11: zero major non-conformances traced to SYSTEMS
                     "systems_traced": bool(
                         rec.nccr_systems_traced()) if hasattr(
                             rec, "nccr_systems_traced") else False})

    def nccr_systems_traced(self):
        """CON-11's question: do any MAJOR findings trace to SYSTEMS (a
        process/control defect) rather than isolated human error?"""
        self.ensure_one()
        for ncr in self.ncr_ids:
            if ncr.severity in ("major", "critical"):
                if ncr.root_cause and "system" in ncr.root_cause.lower():
                    return True
        return False


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixNcrAuditLink(models.Model):
    """Bridge: an audit finding IS an NCR with the audit as source."""
    _inherit = "fix.ncr"

    audit_id = fields.Many2one("fix.internal.audit", string="Audit",
                               ondelete="set null")


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixQcChecklistM23Ext(models.Model):
    """P08-M06-T04: QC ownership transfers to M23 (AR-005 — exactly one
    owning module). The M31 -> M23 stub CLOSES: a failed checklist raises
    a REAL NCR; the M23 linkage field replaces the intent-only stub."""
    _inherit = "fix.qc.checklist"

    ncr_id = fields.Many2one("fix.ncr", string="NCR (M23)",
                             ondelete="set null",
                             help="The M23 non-conformance this failed "
                                  "checklist raised — the GV-005 stub "
                                  "(expiry 2027-03-31) is closed")

    def action_fail_with_ncr(self):
        """Failing a checklist raises an NCR in M23 — the takeover."""
        for rec in self:
            ncr = self.env["fix.ncr"].create({
                "source": "qc",
                "order_id": rec.order_id.id,
                "severity": "major",
                "description": "QC checklist failed for order %s"
                               % rec.order_id.name,
            })
            rec.write({"state": "failed", "ncr_id": ncr.id})
            publish(self.env, "qc.ncr_raised", "fix.qc.checklist", rec.id,
                    {"ncr": ncr.name})


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixComplaintM23Ext(models.Model):
    """P08-M06-T05: the M34 -> M23 and M42 -> M23 stubs CLOSE. The
    complaint's journey-14 linkage becomes real relations."""
    _inherit = "fix.complaint"

    ncr_id = fields.Many2one("fix.ncr", string="NCR",
                             ondelete="set null")
    capa_id = fields.Many2one("fix.capa", string="CAPA",
                              ondelete="set null")

    def action_raise_ncr(self):
        """The REAL NCR (the stub wrote NCR-STUB/<id> with an expiry)."""
        res = super().action_raise_ncr()
        for complaint in self:
            ncr = self.env["fix.ncr"].create({
                "source": "complaint",
                "complaint_id": complaint.id,
                "severity": "major" if complaint.severity != "critical"
                            else "critical",
                "description": complaint.description,
            })
            complaint.write({"ncr_id": ncr.id})
            # Backfill the legacy stub ref for traceability of the closure
            if complaint.ncr_stub_ref and not complaint.ncr_stub_ref.startswith(
                    "NCR-STUB-CLOSED"):
                complaint.write({
                    "ncr_stub_ref": "NCR-STUB-CLOSED/%s->%s"
                                    % (complaint.id, ncr.name)})
            publish(self.env, "complaint.ncr_linked", "fix.complaint",
                    complaint.id, {"ncr": ncr.name, "stub": False})
        return res

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")