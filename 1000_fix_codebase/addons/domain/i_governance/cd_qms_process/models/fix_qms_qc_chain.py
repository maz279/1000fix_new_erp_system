# fix_qms_qc_chain — A10 deep audit (2026-11-22): the Quality Gates register
# was decorative. Two blocking gates (QG-01 "Job creation", QG-02 "Before
# customer handover") configured on live governed nothing: no M01 flow read
# fix.qms.gate, and the M23 checklist templates (applicability rules, per-item
# acceptance criteria, evidence requirements, reportable items) never reached
# the bench — fix.qc.checklist had no template link at all (A1-F01/F02, A5-F06).
#
# This file closes the chain, all inside cd_qms_process (which already depends
# on cd_service_order — no new dependency, no M01 file touched):
#
#   * fix.qms.gate gains a CHECKPOINT (where it bites) and is enforced through
#     fix.service.order._check_qc_gate — the same choke point M01's own hard
#     gate uses, so every path to Ready shares it.
#   * fix.qc.checklist links its fix.qms.checklist template and materialises
#     the template's items (criteria, evidence, reportable) for the inspector.
#   * a failed completion raises its NCR through action_fail_with_ncr (the
#     dead takeover method): a MAJOR, checklist-linked non-conformance. The
#     relay consumer's minor NCR dedupes against it (it notes the open
#     source='qc' NCR instead of raising a second one).
from odoo import api, fields, models
from odoo.exceptions import UserError

GATE_QC = "qc_pass"
GATE_JOB = "job_creation"


class FixQmsGateCheckpoint(models.Model):
    """Where a gate bites. The legacy free-text ``stage`` stays for display;
    the checkpoint is the enforceable contract."""

    _inherit = "fix.qms.gate"

    checkpoint = fields.Selection(
        [
            (GATE_QC, "QC pass — the order may not be Ready/Delivered past it"),
            (GATE_JOB, "Job creation — the intake checklist must exist"),
        ],
        required=True,
        default=GATE_QC,
        help="A10 deep audit 2026-11-22: a gate names WHERE it blocks. "
        "qc_pass is enforced by fix.service.order._check_qc_gate; "
        "job_creation seeds the order's checklist from the mandatory template.",
    )


class FixQcItemM23(models.Model):
    """The bench item carries its template's criteria and evidence demands."""

    _inherit = "fix.qc.item"

    template_item_id = fields.Many2one("fix.qms.checklist.item", ondelete="set null", index=True)
    name_bn = fields.Char(string="Item (Bengali)")
    acceptance_criteria = fields.Char(
        help="The pass condition this item is judged against (from the template)."
    )
    evidence_required = fields.Selection(
        [
            ("none", "None"),
            ("photo", "Photograph"),
            ("measurement", "Measurement"),
            ("reading", "Reading"),
            ("signature", "Signature"),
        ],
        default="none",
        help="What the inspector must capture for this item to count as evidence.",
    )
    reportable = fields.Boolean(
        string="Failure Raises NCR",
        help="A failed item with this flag raises a non-conformance on completion.",
    )


class FixQcChecklistM23Chain(models.Model):
    """The execution checklist consumes its M23 template."""

    _inherit = "fix.qc.checklist"

    template_id = fields.Many2one(
        "fix.qms.checklist",
        string="Checklist Template (M23)",
        readonly=True,
        ondelete="set null",
        index=True,
        help="The published M23 template this inspection runs: its items, "
        "criteria and evidence demands were materialised for the bench.",
    )

    # ------------------------------------------------------------------
    # template resolution (A1-F02): the applicability rules finally route
    # ------------------------------------------------------------------
    def _m23_candidate_templates(self):
        return self.env["fix.qms.checklist"].sudo().search([("state", "=", "published")])

    def _m23_template_matches(self, template, order) -> bool:
        sudo_order = order.sudo()
        if template.applies_device_category:
            category = sudo_order.category_id.name if "category_id" in sudo_order._fields else ""
            device_cat = (
                sudo_order.device_id.category_id.name
                if "device_id" in sudo_order._fields and sudo_order.device_id
                else ""
            )
            if template.applies_device_category not in (category or "", device_cat or ""):
                return False
        if template.applies_brand:
            brand = (
                sudo_order.device_id.brand_id.name
                if "device_id" in sudo_order._fields and sudo_order.device_id
                else (sudo_order.brand or "")
            )
            if template.applies_brand != (brand or ""):
                return False
        if template.applies_repair_level and template.applies_repair_level != "any":
            level = sudo_order.repair_level if "repair_level" in sudo_order._fields else ""
            if template.applies_repair_level != (level or ""):
                return False
        if template.applies_value_min or template.applies_value_max:
            value = order._fix_amount_due()
            if template.applies_value_min and value < template.applies_value_min:
                return False
            if template.applies_value_max and value > template.applies_value_max:
                return False
        if template.applies_delivery_mode and template.applies_delivery_mode != "any":
            mode = sudo_order.delivery_mode if "delivery_mode" in sudo_order._fields else ""
            if template.applies_delivery_mode != (mode or ""):
                return False
        if template.applies_customer_type and template.applies_customer_type != "any":
            is_corp = (
                bool(sudo_order.partner_id and sudo_order.partner_id.is_company)
                if "partner_id" in sudo_order._fields
                else False
            )
            kind = "corporate" if is_corp else "retail"
            if template.applies_customer_type != kind:
                return False
        if template.applies_branch_ids:
            branch = (
                sudo_order.branch_id
                if "branch_id" in sudo_order._fields
                else (
                    sudo_order.operating_unit_id
                    if "operating_unit_id" in sudo_order._fields
                    else None
                )
            )
            if branch and branch not in template.applies_branch_ids:
                return False
        return True

    def _m23_resolve_template(self, order):
        """The template this inspection runs: an active gate's mandatory
        checklist first (the register's explicit word), else the best
        applicability match (most rules matched wins)."""
        Gate = self.env["fix.qms.gate"].sudo()
        for gate in Gate.search(
            [("state", "=", "active"), ("checkpoint", "in", (GATE_QC, GATE_JOB))]
        ):
            if (
                gate.mandatory_checklist_id
                and gate.mandatory_checklist_id.state == "published"
                and self._m23_template_matches(gate.mandatory_checklist_id, order)
            ):
                return gate.mandatory_checklist_id
        best, best_score = None, -1
        for template in self._m23_candidate_templates():
            if not self._m23_template_matches(template, order):
                continue
            score = (
                sum(
                    1
                    for f in (
                        "applies_device_category",
                        "applies_brand",
                    )
                    if template[f]
                )
                + (
                    1
                    if template.applies_repair_level and template.applies_repair_level != "any"
                    else 0
                )
                + (
                    1
                    if template.applies_delivery_mode and template.applies_delivery_mode != "any"
                    else 0
                )
                + (
                    1
                    if template.applies_customer_type and template.applies_customer_type != "any"
                    else 0
                )
                + (1 if template.applies_branch_ids else 0)
                + (1 if (template.applies_value_min or template.applies_value_max) else 0)
            )
            if score > best_score:
                best, best_score = template, score
        return best

    def _m23_materialise_items(self):
        Item = self.env["fix.qc.item"].sudo()
        for rec in self:
            template = rec.template_id
            if not template or rec.item_ids:
                continue
            for pos, template_item in enumerate(template.item_ids.sorted("sequence"), start=1):
                Item.create(
                    {
                        "checklist_id": rec.id,
                        "name": template_item.name,
                        "name_bn": template_item.name_bn,
                        "sequence": pos * 10,
                        "template_item_id": template_item.id,
                        "acceptance_criteria": template_item.acceptance_criteria,
                        "evidence_required": template_item.evidence_required,
                        "reportable": template_item.reportable,
                    }
                )

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        # a checklist born with NEITHER items NOR ticked inspection stages
        # runs its template: the gate register and the applicability rules
        # decide WHICH one (A1-F02). A stage-based checklist (the form's four
        # ticked stages are its items) keeps that path untouched.
        stage_fields = (
            "visual_inspection_passed",
            "functional_test_passed",
            "safety_electrical_passed",
            "cleaning_sanitization_passed",
        )
        for rec in recs.filtered(
            lambda r: not r.item_ids
            and not r.template_id
            and not any(r[name] for name in stage_fields)
        ):
            template = rec._m23_resolve_template(rec.order_id)
            if template:
                rec._guarded().write({"template_id": template.id})
                rec._m23_materialise_items()
        return recs

    def action_complete(self):
        result = super().action_complete()
        # A1-F05: the failed inspection raises its NCR through the takeover
        # method — MAJOR, checklist-linked (the relay's order-level minor NCR
        # dedupes against it: it notes the open source='qc' NCR instead).
        for rec in self:
            if rec.state == "failed" and not rec.ncr_id:
                rec.action_fail_with_ncr()
        return result


class FixServiceOrderQmsGates(models.Model):
    """A1-F01: the gate register is enforced at M01's own Ready choke point.
    super() keeps the hardcoded baseline (a PASSED checklist with items); the
    register adds WHICH checklist (the gate's mandatory template) and the
    independence rule above the gate's threshold."""

    _inherit = "fix.service.order"

    def _check_qc_gate(self) -> None:
        super()._check_qc_gate()
        gates = (
            self.env["fix.qms.gate"]
            .sudo()
            .search(
                [("state", "=", "active"), ("checkpoint", "=", GATE_QC), ("blocking", "=", True)]
            )
        )
        if not gates:
            return
        newest = self._fix_release_checklist()
        for gate in gates:
            if gate.mandatory_checklist_id:
                passed = (
                    self.env["fix.qc.checklist"]
                    .sudo()
                    .search_count(
                        [
                            ("order_id", "=", self.id),
                            ("template_id", "=", gate.mandatory_checklist_id.id),
                            ("state", "=", "passed"),
                        ]
                    )
                )
                if not passed:
                    raise UserError(
                        "Quality gate %s (%s) blocks order %s: its mandatory checklist "
                        "'%s' has no PASSED inspection for this order. Complete that "
                        "checklist first (FR-QMS-015, BRU-QMS-02)."
                        % (gate.code, gate.name, self.name, gate.mandatory_checklist_id.name)
                    )
            if gate.independence_required:
                amount = self._fix_amount_due()
                threshold = gate.independence_value_threshold or 0.0
                if threshold and amount <= threshold:
                    continue  # below the gate's risk band
                if not newest.inspected_by:
                    raise UserError(
                        "Quality gate %s (%s) requires an independent inspection for "
                        "order %s: the passing checklist names no inspector."
                        % (gate.code, gate.name, self.name)
                    )
                if self.repair_completed_by and newest.inspected_by == self.repair_completed_by:
                    raise UserError(
                        "Quality gate %s (%s) blocks order %s: the person who completed "
                        "the repair (%s) may not also pass its inspection above BDT %s."
                        % (
                            gate.code,
                            gate.name,
                            self.name,
                            self.repair_completed_by.name,
                            f"{threshold:,.0f}" if threshold else "0",
                        )
                    )
