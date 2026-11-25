# fix_qms_capture — M23 capture audit (2026-11-19): the records the M23
# sub-module pages could not capture because they did not exist.
#
# Page 1 Policy & Objectives
#   * fix.qms.objective (FR-QMS-001/002): a measurable quality objective with
#     its owner, measurement basis, target and attainment, cascaded from the
#     company to a branch, a process or a role.
# Page 2 Process Register
#   * process purpose, interactions, controls, review date and its work
#     instruction (FR-QMS-003/004) — fields on fix.qms.process.
#   * fix.qms.change.assessment (FR-QMS-010, BRU-QMS-10): a process change is
#     released only after its QMS impact is assessed and every affected
#     document, checklist and training item is updated.
# Page 3 Checklists & Gates
#   * fix.qms.checklist.item (FR-QMS-011/016, BRU-QMS-03): the items of a
#     template, with response type, acceptance criteria and evidence; frozen
#     once the version is published — a change is a new version.
#   * applicability rules on the template (FR-QMS-013) and the independent
#     inspection rule on the gate (FR-QMS-015).
# Page 4 NCR Management: every capture source, the typed non-conformance,
#   the ISO clause affected and the containment owner and deadline
#   (FR-QMS-021..024) — fields and one action on fix.ncr.
# Page 5 RCA & CAPA
#   * fix.qms.rca (FR-QMS-026/027, BRU-QMS-04/14): 5-Why, Ishikawa or 8D;
#     the root cause must differ from the symptom, and a major or critical
#     non-conformance needs the 8D with all eight disciplines.
#   * fix.capa.action (FR-QMS-033/037, BRU-QMS-18): the CAPA's action plan;
#     a CAPA is implemented only when every action is done with evidence.
#   * the effectiveness observation window (FR-QMS-035) on fix.capa.
# Page 6 Audit Programme
#   * fix.qms.audit.programme (FR-QMS-040): the annual plan.
#   * fix.qms.auditor (FR-QMS-041, BRU-QMS-07): the auditor register; once a
#     company registers an auditor, an audit is assigned only to a registered
#     auditor who is independent of the branch and processes in scope.
#   * fix.qms.audit.finding (FR-QMS-043): major / minor / observation / OFI,
#     with its clause and evidence; a major or minor finding raises its NCR.
#   * fix.qms.evidence.release (FR-QMS-046, BRU-QMS-15): evidence released
#     to an external auditor only on the Quality Manager's approval, logged.
# Page 8 Statistics & CoPQ: a CoPQ entry names its non-conformance and the
#   cause it is attributed to (FR-QMS-029/030).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_qms import QM_GROUP, _require_quality_manager

EXECUTING_MODULES = [
    ("m23", "M23 Quality (process change)"),
    ("m22", "M22 Competency (training)"),
    ("m24", "M24 Documents (document change)"),
    ("m60", "M60 GRC (control change)"),
    ("m42", "M42 Suppliers (supplier action)"),
    ("m12", "M12 Marketplace (seller action)"),
    ("m01", "M01 Service Delivery (operations)"),
]


def _employee(env):
    """The session user's employee: these records are stamped with a person."""
    employee = env.user.employee_id
    if not employee and not env.su:
        raise UserError(
            "%s has no employee record: this step is stamped with the employee who "
            "takes it." % env.user.name
        )
    return employee


def _is_qm(env):
    return env.su or env.user.has_group(QM_GROUP)


def _blank(value):
    return not (value or "").strip()


def _norm(text):
    return " ".join((text or "").lower().split())


# ====================================================================== page 1
class FixQmsObjective(models.Model):
    """A quality objective, measurable and owned, cascaded to where it is
    achieved (ISO 9001 6.2)."""

    _name = "fix.qms.objective"
    _description = "Quality Objective"
    _inherit = ["mail.thread"]
    _order = "period desc, id desc"

    name = fields.Char(string="Objective", required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    policy_id = fields.Many2one(
        "fix.qms.policy", string="Quality Policy", required=True, ondelete="restrict", index=True
    )
    parent_id = fields.Many2one(
        "fix.qms.objective",
        string="Cascaded From",
        ondelete="restrict",
        help="The higher objective this one contributes to (FR-QMS-002).",
    )
    child_ids = fields.One2many("fix.qms.objective", "parent_id", string="Cascaded Objectives")
    scope_level = fields.Selection(
        [
            ("company", "Company"),
            ("branch", "Branch / Workshop"),
            ("process", "Process"),
            ("role", "Role"),
        ],
        string="Applies To",
        required=True,
        default="company",
    )
    branch_id = fields.Many2one("fix.branch", string="Branch")
    process_id = fields.Many2one("fix.qms.process", string="Process")
    role = fields.Char(string="Role")
    measure = fields.Char(
        string="Measurement Basis",
        required=True,
        help="How attainment is measured, e.g. 'rework orders / delivered orders, monthly'.",
    )
    target = fields.Float(required=True, tracking=True)
    actual = fields.Float(tracking=True)
    unit = fields.Char()
    higher_is_better = fields.Boolean(
        string="Higher Is Better",
        default=True,
        help="Off for objectives where lower is better (rework rate, complaints).",
    )
    period = fields.Char(required=True, help="YYYY or YYYY-MM")
    owner_id = fields.Many2one("hr.employee", string="Owner", required=True)
    review_due = fields.Date(string="Next Review")
    attainment = fields.Float(
        string="Attainment %",
        compute="_compute_attainment",
        store=True,
        help="Actual against target; for lower-is-better objectives, target against actual.",
    )

    @api.depends("target", "actual", "higher_is_better")
    def _compute_attainment(self):
        for rec in self:
            if rec.higher_is_better:
                rec.attainment = round(rec.actual / rec.target * 100.0, 1) if rec.target else 0.0
            else:
                # lower is better: at or under target is 100% or more
                rec.attainment = round(rec.target / rec.actual * 100.0, 1) if rec.actual else 100.0

    @api.constrains("scope_level", "branch_id", "process_id", "role", "parent_id", "policy_id")
    def _check_scope(self):
        for rec in self:
            if rec.scope_level == "branch" and not rec.branch_id:
                raise ValidationError("A branch objective names its branch (FR-QMS-002).")
            if rec.scope_level == "process" and not rec.process_id:
                raise ValidationError("A process objective names its process (FR-QMS-002).")
            if rec.scope_level == "role" and _blank(rec.role):
                raise ValidationError("A role objective names its role (FR-QMS-002).")
            if rec.parent_id:
                if rec.parent_id == rec or rec.parent_id in rec._cascade_descendants():
                    raise ValidationError("An objective cannot cascade from itself.")
                if rec.parent_id.policy_id != rec.policy_id:
                    raise ValidationError(
                        "'%s' cascades from an objective of another policy year." % rec.name
                    )

    def _cascade_descendants(self):
        out = self.browse()
        todo = self.child_ids
        while todo:
            out |= todo
            todo = todo.child_ids - out
        return out


# ====================================================================== page 2
class FixQmsProcessCapture(models.Model):
    _inherit = "fix.qms.process"

    purpose = fields.Text()
    interactions = fields.Char(
        string="Interactions", help="The processes this one hands to or receives from."
    )
    controls = fields.Text(string="Controls")
    review_due = fields.Date(string="Next Review")
    work_instruction_id = fields.Many2one(
        "fix.document",
        string="Process Map / Work Instruction",
        help="The controlled document in M24 (FR-QMS-004).",
    )
    change_ids = fields.One2many(
        "fix.qms.change.assessment", "process_id", string="Change Assessments"
    )


class FixQmsChangeAssessment(models.Model):
    """BRU-QMS-10: a registered process change is released only after its QMS
    impact is assessed and every affected item is updated first."""

    _name = "fix.qms.change.assessment"
    _description = "Process Change — QMS Impact Assessment"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    process_id = fields.Many2one(
        "fix.qms.process", string="Process", required=True, ondelete="restrict", index=True
    )
    change_summary = fields.Text(string="Proposed Change", required=True)
    reason = fields.Text()
    impact_note = fields.Text(string="QMS Impact Assessment")
    affects_documents = fields.Boolean(string="Affects Documents")
    documents_updated = fields.Boolean(string="Documents Updated")
    affects_checklists = fields.Boolean(string="Affects Checklists")
    checklists_updated = fields.Boolean(string="Checklists Updated")
    affects_training = fields.Boolean(string="Affects Training")
    training_updated = fields.Boolean(string="Training Updated")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("assessed", "Assessed"),
            ("released", "Released"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    assessed_by_id = fields.Many2one("hr.employee", string="Assessed By", copy=False)
    released_by_id = fields.Many2one("hr.employee", string="Released By", copy=False)
    released_on = fields.Date(copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "assessed_by_id",
            "released_by_id",
            "released_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(self._fix_guarded_fields())
        if set(self.mapped("state")) & {"released", "rejected"}:
            locked |= set(self._fields) - {"message_ids", "message_follower_ids"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.qms.change.assessment") or "CHG/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if not (self.env.su or self._fix_guard_has_token()):
            for rec in self:
                if rec.state in ("released", "rejected"):
                    raise UserError(
                        "%s is %s — the assessment is the record kept (BRU-QMS-11)."
                        % (rec.name, rec.state)
                    )
        return super().write(vals)

    def _pending_updates(self):
        self.ensure_one()
        pending = []
        if self.affects_documents and not self.documents_updated:
            pending.append("documents")
        if self.affects_checklists and not self.checklists_updated:
            pending.append("checklists")
        if self.affects_training and not self.training_updated:
            pending.append("training")
        return pending

    def action_assess(self):
        employee = _employee(self.env)
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is %s — only a draft is assessed." % (rec.name, rec.state))
            if _blank(rec.impact_note):
                raise UserError(
                    "Record the QMS impact of %s: which documents, checklists and "
                    "training it touches (BRU-QMS-10)." % rec.name
                )
            rec._guarded().write({"state": "assessed", "assessed_by_id": employee.id})
        return True

    def action_release(self):
        """BRU-QMS-10 (hard): the Quality Manager releases the change only once
        every affected document, checklist and training item is updated."""
        _require_quality_manager(self.env, "release a process change")
        employee = _employee(self.env)
        for rec in self:
            if rec.state != "assessed":
                raise UserError("Assess %s before releasing it (BRU-QMS-10)." % rec.name)
            pending = rec._pending_updates()
            if pending:
                raise UserError(
                    "%s cannot be released: update the affected %s first (BRU-QMS-10)."
                    % (rec.name, ", ".join(pending))
                )
            rec._guarded().write(
                {
                    "state": "released",
                    "released_by_id": employee.id,
                    "released_on": fields.Date.context_today(rec),
                }
            )
            rec.message_post(body="Change released by %s." % self.env.user.name)
        return True

    def action_reject(self, reason=""):
        _require_quality_manager(self.env, "reject a process change")
        for rec in self:
            if rec.state not in ("draft", "assessed"):
                raise UserError("%s is %s." % (rec.name, rec.state))
            if _blank(reason):
                raise UserError("Say why %s is rejected." % rec.name)
            rec._guarded().write({"state": "rejected"})
            rec.message_post(body="Rejected: %s" % reason.strip())
        return True


# ====================================================================== page 3
class FixQmsChecklistItem(models.Model):
    """One item of a checklist template. A published version's items never
    change (BRU-QMS-03): a change is a new version."""

    _name = "fix.qms.checklist.item"
    _description = "Checklist Template Item"
    _order = "checklist_id, sequence, id"

    checklist_id = fields.Many2one(
        "fix.qms.checklist", string="Checklist", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    sequence = fields.Integer(default=10)
    section = fields.Char()
    name = fields.Char(string="Item (English)", required=True)
    name_bn = fields.Char(string="Item (Bengali)")
    response_type = fields.Selection(
        [
            ("pass_fail", "Pass / Fail"),
            ("yes_no", "Yes / No"),
            ("measurement", "Measurement"),
            ("reading", "Reading"),
            ("text", "Text"),
        ],
        string="Response",
        required=True,
        default="pass_fail",
    )
    acceptance_criteria = fields.Char(string="Acceptance Criteria")
    evidence_required = fields.Selection(
        [
            ("none", "None"),
            ("photo", "Photograph"),
            ("measurement", "Measurement"),
            ("reading", "Reading"),
            ("signature", "Signature"),
        ],
        string="Evidence Required",
        required=True,
        default="none",
    )
    reportable = fields.Boolean(
        string="Failure Raises NCR",
        help="A failed answer is a reportable non-conformance (FR-QMS-019).",
    )

    @api.constrains("response_type", "acceptance_criteria")
    def _check_criteria(self):
        for rec in self:
            if rec.response_type in ("measurement", "reading") and _blank(rec.acceptance_criteria):
                raise ValidationError(
                    "'%s' is measured: state its acceptance criteria (FR-QMS-011)." % rec.name
                )

    def _assert_draft(self, checklists):
        if self.env.su:
            return
        for checklist in checklists:
            if checklist.state != "draft":
                raise UserError(
                    "'%s' version %s is %s — its items are frozen. Create a new version "
                    "to change them (BRU-QMS-03)."
                    % (checklist.name, checklist.version, checklist.state)
                )

    @api.model_create_multi
    def create(self, vals_list):
        checklists = self.env["fix.qms.checklist"].browse(
            [v.get("checklist_id") for v in vals_list if v.get("checklist_id")]
        )
        self._assert_draft(checklists)
        for vals in vals_list:
            if vals.get("checklist_id") and "company_id" not in vals:
                vals["company_id"] = (
                    self.env["fix.qms.checklist"].browse(vals["checklist_id"]).company_id.id
                )
        return super().create(vals_list)

    def write(self, vals):
        self._assert_draft(self.mapped("checklist_id"))
        if "checklist_id" in vals:
            self._assert_draft(self.env["fix.qms.checklist"].browse(vals["checklist_id"]))
        return super().write(vals)

    def unlink(self):
        self._assert_draft(self.mapped("checklist_id"))
        return super().unlink()


class FixQmsChecklistCapture(models.Model):
    _inherit = "fix.qms.checklist"

    item_ids = fields.One2many("fix.qms.checklist.item", "checklist_id", string="Items")
    # the count was typed (14 / 9 / 22 on the live templates) while no item
    # existed anywhere: it now counts the items the template holds
    item_count = fields.Integer(string="Item Count", compute="_compute_item_count", store=True)
    previous_version_id = fields.Many2one(
        "fix.qms.checklist", string="Previous Version", readonly=True, copy=False
    )
    applies_device_category = fields.Char(string="Device Category")
    applies_brand = fields.Char(string="Brand")
    applies_repair_level = fields.Selection(
        [
            ("any", "Any"),
            ("l1", "L1 — swap / basic"),
            ("l2", "L2 — component"),
            ("l3", "L3 — board level"),
        ],
        string="Repair Level",
        default="any",
    )
    applies_value_min = fields.Float(string="Value From (BDT)")
    applies_value_max = fields.Float(string="Value To (BDT)", help="0 = no upper limit")
    applies_delivery_mode = fields.Selection(
        [
            ("any", "Any"),
            ("counter", "Counter / walk-in"),
            ("pickup", "Pickup & drop"),
            ("field", "Field / on-site"),
            ("workshop", "Workshop"),
        ],
        string="Delivery Mode",
        default="any",
    )
    applies_customer_type = fields.Selection(
        [("any", "Any"), ("retail", "Retail"), ("corporate", "Corporate / B2B")],
        string="Customer Type",
        default="any",
    )
    applies_branch_ids = fields.Many2many(
        "fix.branch",
        "fix_qms_checklist_branch_rel",
        "checklist_id",
        "branch_id",
        string="Branches (empty = all)",
    )

    @api.depends("item_ids")
    def _compute_item_count(self):
        for rec in self:
            rec.item_count = len(rec.item_ids)

    @api.constrains("applies_value_min", "applies_value_max")
    def _check_value_band(self):
        for rec in self:
            if rec.applies_value_max and rec.applies_value_max < rec.applies_value_min:
                raise ValidationError(
                    "The value band of '%s' ends below where it starts." % rec.name
                )

    def _m23_recount_items(self):
        """Module update: the count used to be typed; recount it from the
        items so a template claiming items it does not hold reads 0."""
        records = self.sudo().with_context(active_test=False).search([])
        self.env.add_to_compute(self._fields["item_count"], records)
        records.flush_model(["item_count"])
        return True

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if set(self.mapped("state")) - {"draft"}:
            # BRU-QMS-03: a released version is frozen
            locked |= {
                "name",
                "checklist_type",
                "iso_clause",
                "version",
                "item_ids",
                "applies_device_category",
                "applies_brand",
                "applies_repair_level",
                "applies_value_min",
                "applies_value_max",
                "applies_delivery_mode",
                "applies_customer_type",
                "applies_branch_ids",
            }
        return locked

    def write(self, vals):
        frozen = set(vals) - {"state", "item_count", "message_ids"}
        if frozen and not (self.env.su or self._fix_guard_has_token()):
            for rec in self:
                if rec.state != "draft":
                    raise UserError(
                        "'%s' version %s is %s — it is frozen. Create a new version to "
                        "change it (BRU-QMS-03)." % (rec.name, rec.version, rec.state)
                    )
        return super().write(vals)

    def action_publish(self):
        _require_quality_manager(self.env, "publish a quality checklist")
        for rec in self:
            if rec.state == "draft" and not rec.item_ids:
                raise UserError(
                    "'%s' has no items: author them before publishing (FR-QMS-011)." % rec.name
                )
        return super().action_publish()

    def _next_version(self):
        self.ensure_one()
        try:
            return "%.1f" % (float(self.version or "1.0") + 1.0)
        except ValueError:
            return "%s.1" % (self.version or "1")

    def action_new_version(self):
        """BRU-QMS-03: the published version stays as executed; the change is
        authored on a new draft version that copies its items."""
        _require_quality_manager(self.env, "start a new checklist version")
        out = self.browse()
        for rec in self:
            if rec.state == "draft":
                raise UserError("'%s' is a draft — edit it directly." % rec.name)
            later = self.search([("previous_version_id", "=", rec.id)], limit=1)
            if later:
                raise UserError(
                    "'%s' version %s already has its next version %s."
                    % (rec.name, rec.version, later.version)
                )
            new = rec.copy(
                {
                    "version": rec._next_version(),
                    "previous_version_id": rec.id,
                    "state": "draft",
                }
            )
            for item in rec.item_ids:
                item.sudo().copy({"checklist_id": new.id})
            out |= new
        return out.ids


class FixQmsGateCapture(models.Model):
    _inherit = "fix.qms.gate"

    independence_required = fields.Boolean(
        string="Independent Inspection",
        help="A second person, not the technician, performs the inspection (FR-QMS-015).",
    )
    independence_value_threshold = fields.Float(
        string="Independent Above (BDT)",
        help="Order value above which the second inspection is mandatory; 0 = always.",
    )
    independence_note = fields.Char(string="Risk Basis")


# ====================================================================== page 4
NCR_SOURCES = [
    ("rework", "Rework detected (M01)"),
    ("external_audit", "External audit"),
    ("claim_rejection", "Brand claim rejection (M09)"),
    ("seller", "Marketplace seller (M12)"),
    ("safety_referral", "Safety near-miss referral (M59)"),
    ("staff_report", "Staff report"),
]


class FixNcrCapture(models.Model):
    _inherit = "fix.ncr"

    source = fields.Selection(
        selection_add=NCR_SOURCES, ondelete={key: "set default" for key, _label in NCR_SOURCES}
    )
    nc_type = fields.Selection(
        [
            ("internal", "Internal"),
            ("customer", "Customer"),
            ("supplier", "Supplier"),
            ("seller", "Marketplace Seller"),
            ("audit", "Audit"),
            ("systemic", "Systemic"),
        ],
        string="Type",
        required=True,
        default="internal",
        tracking=True,
    )
    clause_ref = fields.Char(string="ISO Clause Affected")
    containment_owner_id = fields.Many2one("hr.employee", string="Containment Owner")
    containment_due = fields.Date(string="Containment Due")
    containment_done_on = fields.Date(string="Containment Done On", copy=False)
    containment_done_by_id = fields.Many2one(
        "hr.employee", string="Containment Confirmed By", copy=False
    )
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Photo / Evidence", ondelete="set null"
    )
    rca_ids = fields.One2many("fix.qms.rca", "ncr_id", string="Root-Cause Analyses")
    finding_id = fields.Many2one(
        "fix.qms.audit.finding", string="Audit Finding", ondelete="set null", copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "containment_done_on",
            "containment_done_by_id",
            "finding_id",
        }

    @api.constrains("containment_due", "create_date")
    def _check_containment_due(self):
        for rec in self:
            if (
                rec.containment_due
                and rec.create_date
                and rec.containment_due < rec.create_date.date()
            ):
                raise ValidationError(
                    "%s: containment cannot be due before it was raised." % rec.name
                )

    def action_record_containment(self, note=""):
        """FR-QMS-024: the interim containment is its own tracked step — an
        action, an owner and a deadline, confirmed done."""
        employee = _employee(self.env)
        for rec in self:
            if rec.state == "closed":
                raise UserError("%s is closed." % rec.name)
            if rec.containment_done_on:
                raise UserError("The containment of %s is already confirmed." % rec.name)
            if (note or "").strip():
                rec.write({"containment": note.strip()})
            if _blank(rec.containment) or not rec.containment_owner_id:
                raise UserError(
                    "Record what contains %s and who owns it before confirming it "
                    "(FR-QMS-024)." % rec.name
                )
            rec._guarded().write(
                {
                    "containment_done_on": fields.Date.context_today(rec),
                    "containment_done_by_id": employee.id,
                }
            )
        return True


# ====================================================================== page 5
class FixQmsRca(models.Model):
    """Root-cause analysis of a non-conformance (FR-QMS-026/027)."""

    _name = "fix.qms.rca"
    _description = "Root-Cause Analysis"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    ncr_id = fields.Many2one("fix.ncr", string="NCR", required=True, ondelete="cascade", index=True)
    ncr_severity = fields.Selection(related="ncr_id.severity", string="Severity")
    method = fields.Selection(
        [("five_why", "5-Why"), ("ishikawa", "Ishikawa (fishbone)"), ("eight_d", "8D")],
        required=True,
        default="five_why",
    )
    symptom = fields.Text(string="Symptom (what was observed)", required=True)
    why_1 = fields.Char(string="Why 1")
    why_2 = fields.Char(string="Why 2")
    why_3 = fields.Char(string="Why 3")
    why_4 = fields.Char(string="Why 4")
    why_5 = fields.Char(string="Why 5")
    cause_people = fields.Text(string="People")
    cause_method = fields.Text(string="Method (cause)")
    cause_machine = fields.Text(string="Machine / Tools")
    cause_material = fields.Text(string="Material / Parts")
    cause_measurement = fields.Text(string="Measurement")
    cause_environment = fields.Text(string="Environment")
    d1_team = fields.Text(string="D1 Team")
    d2_problem = fields.Text(string="D2 Problem Description")
    d3_containment = fields.Text(string="D3 Interim Containment")
    d5_corrective = fields.Text(string="D5 Permanent Corrective Action")
    d6_implementation = fields.Text(string="D6 Implementation & Validation")
    d7_prevention = fields.Text(string="D7 Prevent Recurrence")
    d8_recognition = fields.Text(string="D8 Team Recognition / Closure")
    root_cause = fields.Text(string="Root Cause (D4)")
    contributing_factors = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("completed", "Completed")],
        required=True,
        default="draft",
        tracking=True,
    )
    completed_by_id = fields.Many2one("hr.employee", string="Completed By", copy=False)
    completed_on = fields.Date(copy=False)

    _EIGHT_D = (
        "d1_team",
        "d2_problem",
        "d3_containment",
        "root_cause",
        "d5_corrective",
        "d6_implementation",
        "d7_prevention",
        "d8_recognition",
    )
    _FISHBONE = (
        "cause_people",
        "cause_method",
        "cause_machine",
        "cause_material",
        "cause_measurement",
        "cause_environment",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "completed_by_id", "completed_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(self._fix_guarded_fields())
        if set(self.mapped("state")) == {"completed"}:
            locked |= set(self._fields) - {"message_ids", "message_follower_ids"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.qms.rca") or "RCA/New"
        records = super().create(vals_list)
        for rec in records:
            if rec.ncr_id.state == "closed":
                raise UserError("%s is closed: it is not investigated again." % rec.ncr_id.name)
        return records

    def write(self, vals):
        if not (self.env.su or self._fix_guard_has_token()):
            for rec in self:
                if rec.state == "completed":
                    raise UserError(
                        "%s is completed — a revised analysis is a new record "
                        "(BRU-QMS-11)." % rec.name
                    )
        return super().write(vals)

    def _missing(self):
        """What the chosen method still needs (FR-QMS-026/027)."""
        self.ensure_one()
        if self.method == "five_why":
            whys = [self.why_1, self.why_2, self.why_3, self.why_4, self.why_5]
            if len([w for w in whys if not _blank(w)]) < 3:
                return ["at least three answered whys"]
        elif self.method == "ishikawa":
            if all(_blank(self[f]) for f in self._FISHBONE):
                return ["at least one cause category"]
        else:
            return [self._fields[f].string for f in self._EIGHT_D if _blank(self[f])]
        return []

    def action_complete(self):
        """BRU-QMS-04: the root cause is recorded and is not the symptom.
        BRU-QMS-14: a major or critical non-conformance is investigated by 8D.
        Completing the analysis lands the root cause on its NCR."""
        employee = _employee(self.env)
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already completed." % rec.name)
            ncr = rec.ncr_id
            if ncr.state == "closed":
                raise UserError("%s is closed." % ncr.name)
            if ncr.severity in ("major", "critical") and rec.method != "eight_d":
                raise UserError(
                    "%s is %s: it is investigated by 8D (BRU-QMS-14)." % (ncr.name, ncr.severity)
                )
            if _blank(rec.root_cause):
                raise UserError("Record the root cause of %s (BRU-QMS-04)." % ncr.name)
            if _norm(rec.root_cause) == _norm(rec.symptom):
                raise UserError(
                    "The root cause of %s repeats the symptom — say why it happened, "
                    "not what was seen (BRU-QMS-04)." % ncr.name
                )
            missing = rec._missing()
            if missing:
                raise UserError(
                    "%s still needs: %s (FR-QMS-026/027)." % (rec.name, ", ".join(missing))
                )
            rec._guarded().write(
                {
                    "state": "completed",
                    "completed_by_id": employee.id,
                    "completed_on": fields.Date.context_today(rec),
                }
            )
            if ncr.state == "new":
                ncr.action_set_root_cause(rec.root_cause)
            else:
                # a revised analysis (after a failed verification, FR-QMS-036)
                ncr.write({"root_cause": rec.root_cause})
            ncr.message_post(body="Root cause established by %s (%s)." % (rec.name, rec.method))
        return True


class FixCapaAction(models.Model):
    """One planned action of a CAPA (FR-QMS-033/037)."""

    _name = "fix.capa.action"
    _description = "CAPA Action"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "capa_id, sequence, id"

    capa_id = fields.Many2one(
        "fix.capa", string="CAPA", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    sequence = fields.Integer(default=10)
    name = fields.Text(string="Action", required=True)
    owner_id = fields.Many2one("hr.employee", string="Owner", required=True)
    executing_module = fields.Selection(
        EXECUTING_MODULES, string="Executed In", required=True, default="m23"
    )
    external_ref = fields.Char(
        string="Record in That Module",
        help="The training, document change, control change or supplier/seller "
        "action raised in the owning module (BRU-QMS-18).",
    )
    expected_outcome = fields.Char()
    due_on = fields.Date(string="Due")
    state = fields.Selection(
        [("open", "Open"), ("done", "Done")], required=True, default="open", tracking=True
    )
    evidence_note = fields.Text(string="Completion Evidence", copy=False)
    done_on = fields.Date(copy=False)
    done_by_id = fields.Many2one("hr.employee", string="Done By", copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "done_on", "done_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(self._fix_guarded_fields())
        if set(self.mapped("state")) == {"done"}:
            locked |= {"capa_id", "name", "owner_id", "executing_module", "external_ref", "due_on"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            capa = self.env["fix.capa"].browse(vals.get("capa_id") or [])
            if capa and capa.state != "open" and not self.env.su:
                raise UserError(
                    "The CAPA of %s is %s — actions are planned while it is open."
                    % (capa.ncr_id.name, capa.state)
                )
            if capa and "company_id" not in vals:
                vals["company_id"] = capa.company_id.id
        return super().create(vals_list)

    def write(self, vals):
        if not (self.env.su or self._fix_guard_has_token()):
            for rec in self:
                if rec.state == "done":
                    raise UserError("This CAPA action is done — it is the record kept.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            for rec in self:
                if rec.state == "done" or rec.capa_id.state != "open":
                    raise UserError("A completed or implemented CAPA action is not deleted.")
        return super().unlink()

    def action_done(self, note=""):
        """Completed by its owner or the Quality Manager, with the evidence; an
        action executed in another module names the record there (BRU-QMS-18)."""
        employee = _employee(self.env)
        for rec in self:
            if rec.state != "open":
                raise UserError("This CAPA action is already done.")
            if not _is_qm(self.env) and employee != rec.owner_id:
                raise UserError("A CAPA action is completed by its owner or the Quality Manager.")
            evidence = (note or rec.evidence_note or "").strip()
            if not evidence:
                raise UserError("Record the evidence that the action was done (FR-QMS-033).")
            if rec.executing_module != "m23" and _blank(rec.external_ref):
                raise UserError(
                    "This action is executed in %s: name the record there that shows it "
                    "complete (BRU-QMS-18)." % dict(EXECUTING_MODULES)[rec.executing_module]
                )
            rec._guarded().write(
                {
                    "state": "done",
                    "evidence_note": evidence,
                    "done_on": fields.Date.context_today(rec),
                    "done_by_id": employee.id,
                }
            )
        return True


class FixCapaCapture(models.Model):
    _inherit = "fix.capa"

    action_ids = fields.One2many("fix.capa.action", "capa_id", string="Action Plan")
    open_action_count = fields.Integer(
        string="Open Actions", compute="_compute_open_action_count", store=True
    )
    observation_window_days = fields.Integer(
        string="Observation Window (days)",
        help="Days after implementation before effectiveness may be verified "
        "(FR-QMS-035). 0 = verify at once.",
    )
    verification_due_on = fields.Date(string="Verification Due", copy=False)

    @api.depends("action_ids.state")
    def _compute_open_action_count(self):
        for rec in self:
            rec.open_action_count = len(rec.action_ids.filtered(lambda a: a.state == "open"))

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"verification_due_on"}

    @api.constrains("observation_window_days")
    def _check_window(self):
        for rec in self:
            if rec.observation_window_days < 0:
                raise ValidationError("The observation window cannot be negative.")

    def action_implement(self):
        for rec in self:
            open_actions = rec.action_ids.filtered(lambda a: a.state == "open")
            if open_actions:
                raise UserError(
                    "The CAPA of %s has %d open action(s): each is completed with its "
                    "evidence before the CAPA is implemented (FR-QMS-033)."
                    % (rec.ncr_id.name, len(open_actions))
                )
        res = super().action_implement()
        for rec in self:
            rec._guarded().write(
                {
                    "verification_due_on": fields.Date.context_today(rec)
                    + timedelta(days=rec.observation_window_days or 0)
                }
            )
        return res

    def action_verify(self, note=None, effective=True):
        today = fields.Date.context_today(self)
        for rec in self:
            if (
                rec.observation_window_days
                and rec.verification_due_on
                and today < rec.verification_due_on
            ):
                raise UserError(
                    "The CAPA of %s is verified after its %d-day observation window, on "
                    "or after %s (FR-QMS-035)."
                    % (rec.ncr_id.name, rec.observation_window_days, rec.verification_due_on)
                )
        return super().action_verify(note=note, effective=effective)


# ====================================================================== page 6
class FixQmsAuditProgramme(models.Model):
    """The annual internal audit plan (FR-QMS-040)."""

    _name = "fix.qms.audit.programme"
    _description = "Internal Audit Programme"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "year desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    year = fields.Char(required=True)
    process_ids = fields.Many2many(
        "fix.qms.process",
        "fix_qms_audit_programme_process_rel",
        "programme_id",
        "process_id",
        string="Processes In Scope",
    )
    branch_ids = fields.Many2many(
        "fix.branch",
        "fix_qms_audit_programme_branch_rel",
        "programme_id",
        "branch_id",
        string="Branches / Workshops In Scope",
    )
    supplier_seller_scope = fields.Char(
        string="Supplier & Seller Classes",
        help="Supplier and marketplace-seller classes audited (BRU-QMS-17).",
    )
    frequency_note = fields.Text(string="Frequency Rules")
    audit_ids = fields.One2many("fix.internal.audit", "programme_id", string="Audits")
    planned_count = fields.Integer(string="Audits Planned", compute="_compute_coverage")
    uncovered_processes = fields.Integer(
        string="Processes Without an Audit", compute="_compute_coverage"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("closed", "Closed")],
        required=True,
        default="draft",
        tracking=True,
    )
    approved_by_id = fields.Many2one("hr.employee", string="Approved By", copy=False)
    approved_on = fields.Date(copy=False)

    _year_unique = models.Constraint(
        "UNIQUE (company_id, year)", "One internal audit programme per company and year."
    )

    @api.depends("audit_ids", "audit_ids.process_ids", "process_ids")
    def _compute_coverage(self):
        for rec in self:
            rec.planned_count = len(rec.audit_ids)
            covered = rec.audit_ids.mapped("process_ids")
            rec.uncovered_processes = len(rec.process_ids - covered)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by_id", "approved_on"}

    def action_approve(self):
        _require_quality_manager(self.env, "approve the audit programme")
        employee = _employee(self.env)
        for rec in self:
            if rec.state != "draft":
                raise UserError("'%s' is %s." % (rec.name, rec.state))
            if not rec.process_ids and not rec.branch_ids:
                raise UserError(
                    "'%s' covers nothing: name the processes and branches it audits "
                    "(FR-QMS-040)." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": employee.id,
                    "approved_on": fields.Date.context_today(rec),
                }
            )
        return True

    def action_close(self):
        _require_quality_manager(self.env, "close the audit programme")
        for rec in self:
            if rec.state != "approved":
                raise UserError(
                    "'%s' is %s — only an approved programme closes." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "closed"})
        return True


class FixQmsAuditor(models.Model):
    """The auditor register: competence and independence (FR-QMS-041)."""

    _name = "fix.qms.auditor"
    _description = "QMS Auditor"
    _inherit = ["mail.thread"]
    _order = "id desc"
    _rec_name = "employee_id"

    employee_id = fields.Many2one("hr.employee", string="Auditor", required=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    standards = fields.Char(required=True, default="ISO 9001:2015")
    competence_note = fields.Text(
        string="Competence Evidence",
        required=True,
        help="Lead-auditor course, ISO 19011 training, audits shadowed (M22 record).",
    )
    competence_attachment_id = fields.Many2one(
        "ir.attachment", string="Certificate", ondelete="set null"
    )
    qualified_on = fields.Date(required=True, default=fields.Date.context_today)
    excluded_branch_ids = fields.Many2many(
        "fix.branch",
        "fix_qms_auditor_branch_rel",
        "auditor_id",
        "branch_id",
        string="Own Area (excluded branches)",
    )
    excluded_process_ids = fields.Many2many(
        "fix.qms.process",
        "fix_qms_auditor_process_rel",
        "auditor_id",
        "process_id",
        string="Own Work (excluded processes)",
    )
    active = fields.Boolean(default=True)

    _employee_unique = models.Constraint(
        "UNIQUE (company_id, employee_id)", "An auditor is registered once per company."
    )

    def _check_editor(self):
        if not _is_qm(self.env):
            raise UserError("The auditor register is kept by the Quality Manager (FR-QMS-041).")

    @api.model_create_multi
    def create(self, vals_list):
        self._check_editor()
        return super().create(vals_list)

    def write(self, vals):
        if set(vals) - {"message_ids", "message_follower_ids"}:
            self._check_editor()
        return super().write(vals)


class FixInternalAuditCapture(models.Model):
    _inherit = "fix.internal.audit"

    name = fields.Char(string="Reference", copy=False, readonly=True, default="New")
    programme_id = fields.Many2one(
        "fix.qms.audit.programme", string="Programme", ondelete="restrict", index=True
    )
    finding_ids = fields.One2many("fix.qms.audit.finding", "audit_id", string="Audit Findings")
    auditee_acknowledged_on = fields.Date(string="Auditee Acknowledged", copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"auditee_acknowledged_on"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.internal.audit") or "IA/New"
                )
        records = super().create(vals_list)
        records._check_auditor_independence()
        return records

    def write(self, vals):
        res = super().write(vals)
        if {"auditor_id", "branch_id", "process_ids"} & set(vals):
            self._check_auditor_independence()
        return res

    def _check_auditor_independence(self):
        """BRU-QMS-07 / AUT-QMS-13: once a company keeps an auditor register,
        an audit is assigned only to a registered, active auditor who is
        independent of the branch and processes in scope."""
        Auditor = self.env["fix.qms.auditor"].sudo().with_context(active_test=False)
        for rec in self:
            entries = Auditor.search([("company_id", "=", rec.company_id.id)])
            if not entries.filtered("active"):
                continue  # no register kept yet for this company
            entry = entries.filtered(lambda a, r=rec: a.employee_id == r.auditor_id)[:1]
            if not entry or not entry.active:
                raise UserError(
                    "%s is not an active registered auditor: assign a competent auditor "
                    "from the auditor register (FR-QMS-041)." % rec.auditor_id.name
                )
            if rec.branch_id in entry.excluded_branch_ids:
                raise UserError(
                    "%s may not audit %s — it is their own area (BRU-QMS-07)."
                    % (rec.auditor_id.name, rec.branch_id.name)
                )
            own = (rec.process_ids & entry.excluded_process_ids) | rec.process_ids.filtered(
                lambda p, r=rec: p.process_owner_id == r.auditor_id
            )
            if own:
                raise UserError(
                    "%s may not audit their own work or process: %s (BRU-QMS-07)."
                    % (rec.auditor_id.name, ", ".join(own.mapped("code")))
                )

    def action_report(self):
        """AUT-QMS-14: every major or minor finding is in the corrective-action
        system before the report is issued."""
        for rec in self:
            rec.finding_ids.filtered(
                lambda f: f.classification in ("major", "minor") and not f.ncr_id
            ).action_raise_ncr()
        return super().action_report()

    def action_acknowledge(self):
        """FR-QMS-044: the auditee acknowledges the issued report."""
        for rec in self:
            if rec.state != "reported":
                raise UserError("The auditee acknowledges an issued report.")
            if rec.auditee_acknowledged_on:
                raise UserError("Already acknowledged.")
            if not self.env.su and self.env.user.employee_id == rec.auditor_id:
                raise UserError("The auditee acknowledges the report, not the auditor.")
            rec._guarded().write({"auditee_acknowledged_on": fields.Date.context_today(rec)})
            rec.message_post(body="Report acknowledged by %s." % self.env.user.name)
        return True


class FixQmsAuditFinding(models.Model):
    """One finding of a process audit (FR-QMS-043)."""

    _name = "fix.qms.audit.finding"
    _description = "Process Audit Finding"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    audit_id = fields.Many2one(
        "fix.internal.audit", string="Audit", required=True, ondelete="cascade", index=True
    )
    classification = fields.Selection(
        [
            ("major", "Major non-conformity"),
            ("minor", "Minor non-conformity"),
            ("observation", "Observation"),
            ("ofi", "Opportunity for improvement"),
        ],
        required=True,
        default="minor",
        tracking=True,
    )
    clause_ref = fields.Char(string="ISO Clause", required=True)
    statement = fields.Text(string="Finding", required=True)
    evidence = fields.Text(string="Objective Evidence", required=True)
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Evidence File", ondelete="set null"
    )
    owner_id = fields.Many2one("hr.employee", string="Auditee Owner")
    ncr_id = fields.Many2one("fix.ncr", string="NCR", copy=False, ondelete="set null")
    ncr_state = fields.Selection(related="ncr_id.state", string="NCR State")
    state = fields.Selection(
        [("open", "Open"), ("ncr_raised", "NCR Raised"), ("closed", "Closed")],
        required=True,
        default="open",
        tracking=True,
    )
    closed_on = fields.Date(copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "ncr_id", "closed_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(self._fix_guarded_fields())
        if set(self.mapped("state")) - {"open"}:
            locked |= {"audit_id", "classification", "clause_ref", "statement", "evidence"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.qms.audit.finding") or "AF/New"
                )
            if vals.get("audit_id") and "company_id" not in vals:
                vals["company_id"] = (
                    self.env["fix.internal.audit"].browse(vals["audit_id"]).company_id.id
                )
        records = super().create(vals_list)
        for rec in records:
            if rec.audit_id.state != "executed" and not self.env.su:
                raise UserError(
                    "Findings are raised while the audit is executed — %s is %s."
                    % (rec.audit_id.name, rec.audit_id.state)
                )
        return records

    def write(self, vals):
        if not (self.env.su or self._fix_guard_has_token()):
            locked = {"audit_id", "classification", "clause_ref", "statement", "evidence"} & set(
                vals
            )
            for rec in self:
                if locked and rec.state != "open":
                    raise UserError(
                        "%s is %s — the finding is the record kept (BRU-QMS-11)."
                        % (rec.name, rec.state)
                    )
        return super().write(vals)

    def action_raise_ncr(self):
        """A major or minor finding enters the corrective-action system."""
        for rec in self:
            if rec.classification not in ("major", "minor"):
                raise UserError(
                    "%s is an %s: it raises no NCR — close it with its note."
                    % (rec.name, dict(self._fields["classification"].selection)[rec.classification])
                )
            if rec.ncr_id:
                raise UserError("%s already raised %s." % (rec.name, rec.ncr_id.name))
            ncr = self.env["fix.ncr"].create(
                {
                    "source": "audit",
                    "nc_type": "audit",
                    "audit_id": rec.audit_id.id,
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.audit_id.operating_unit_id.id,
                    "severity": rec.classification,
                    "clause_ref": rec.clause_ref,
                    "description": "%s — %s (evidence: %s)"
                    % (rec.name, rec.statement.strip(), rec.evidence.strip()),
                }
            )
            ncr._guarded().write({"finding_id": rec.id})
            rec._guarded().write({"ncr_id": ncr.id, "state": "ncr_raised"})
        return True

    def action_close(self, note=""):
        """An observation or OFI is closed by the Quality Manager with a note; a
        non-conformity closes when its NCR closes."""
        _require_quality_manager(self.env, "close an audit finding")
        for rec in self:
            if rec.state == "closed":
                raise UserError("%s is closed." % rec.name)
            if rec.classification in ("major", "minor"):
                if not rec.ncr_id or rec.ncr_id.state != "closed":
                    raise UserError("%s closes when its NCR is closed (BRU-QMS-05)." % rec.name)
            elif _blank(note):
                raise UserError("Say how %s was considered." % rec.name)
            rec._guarded().write({"state": "closed", "closed_on": fields.Date.context_today(rec)})
            if (note or "").strip():
                rec.message_post(body=note.strip())
        return True


class FixQmsEvidenceRelease(models.Model):
    """BRU-QMS-15: evidence released to an external auditor needs the
    Quality Manager's approval and is logged (FR-QMS-046)."""

    _name = "fix.qms.evidence.release"
    _description = "External Audit Evidence Release"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    certification_id = fields.Many2one(
        "fix.qms.certification", string="External Audit", ondelete="set null"
    )
    external_party = fields.Char(string="Requested By (auditor / body)", required=True)
    request_note = fields.Text(string="Evidence Requested", required=True)
    document_id = fields.Many2one("fix.document", string="Document (M24)", ondelete="set null")
    attachment_id = fields.Many2one("ir.attachment", string="Evidence File", ondelete="set null")
    access_until = fields.Date(string="Access Until")
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("released", "Released"),
            ("refused", "Refused"),
        ],
        required=True,
        default="requested",
        tracking=True,
    )
    requested_by_user_id = fields.Many2one(
        "res.users", string="Recorded By", default=lambda self: self.env.user, copy=False
    )
    approved_by_id = fields.Many2one("hr.employee", string="Approved By", copy=False)
    released_on = fields.Datetime(copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "released_on",
            "requested_by_user_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(self._fix_guarded_fields())
        if set(self.mapped("state")) - {"requested"}:
            locked |= {
                "external_party",
                "request_note",
                "document_id",
                "attachment_id",
                "certification_id",
            }
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.qms.evidence.release") or "EVR/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if not (self.env.su or self._fix_guard_has_token()):
            moved = {
                "external_party",
                "request_note",
                "document_id",
                "attachment_id",
                "certification_id",
            }
            for rec in self:
                if rec.state != "requested" and moved & set(vals):
                    raise UserError(
                        "%s is %s — what was approved is what is released." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def action_approve(self):
        _require_quality_manager(self.env, "approve an evidence release")
        employee = _employee(self.env)
        for rec in self:
            if rec.state != "requested":
                raise UserError("%s is %s." % (rec.name, rec.state))
            if not (rec.document_id or rec.attachment_id):
                raise UserError("Attach the evidence %s releases." % rec.name)
            if not self.env.su and rec.requested_by_user_id == self.env.user:
                raise UserError(
                    "%s was recorded by you: another Quality Manager approves its "
                    "release (BRU-QMS-15)." % rec.name
                )
            rec._guarded().write({"state": "approved", "approved_by_id": employee.id})
        return True

    def action_release(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("%s is released only after approval (BRU-QMS-15)." % rec.name)
            rec._guarded().write({"state": "released", "released_on": fields.Datetime.now()})
            rec.message_post(
                body="Evidence released to %s by %s (access log, BRU-QMS-15)."
                % (rec.external_party, self.env.user.name)
            )
        return True

    def action_refuse(self, reason=""):
        _require_quality_manager(self.env, "refuse an evidence release")
        for rec in self:
            if rec.state not in ("requested", "approved"):
                raise UserError("%s is %s." % (rec.name, rec.state))
            if _blank(reason):
                raise UserError("Say why %s is refused." % rec.name)
            rec._guarded().write({"state": "refused"})
            rec.message_post(body="Refused: %s" % reason.strip())
        return True


# ====================================================================== page 8
class FixQmsCopqCapture(models.Model):
    _inherit = "fix.qms.copq"

    ncr_id = fields.Many2one("fix.ncr", string="NCR", ondelete="set null", index=True)
    attributed_cause = fields.Selection(
        [
            ("process", "Process"),
            ("person", "Person / workmanship"),
            ("supplier", "Supplier"),
            ("seller", "Marketplace seller"),
            ("model", "Device model / design"),
            ("part", "Part"),
            ("training", "Training gap"),
            ("unknown", "Not yet attributed"),
        ],
        string="Attributed Cause",
        required=True,
        default="unknown",
    )
    attribution_basis = fields.Char(string="Attribution Basis")

    @api.constrains("attributed_cause", "attribution_basis")
    def _check_basis(self):
        for rec in self:
            if rec.attributed_cause != "unknown" and _blank(rec.attribution_basis):
                raise ValidationError(
                    "%s: record the basis of its attribution (FR-QMS-029)." % rec.name
                )
