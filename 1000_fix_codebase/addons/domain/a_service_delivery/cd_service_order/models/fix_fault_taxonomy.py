# M37 capture audit, third pass (2026-11-19). The Fault Taxonomy page captured
# a flat fault code with its brand claim codes; FR-CAT-042 asks for the
# symptom -> category -> fault code -> root-cause tree in both languages,
# FR-CAT-025 maps a fault code to the repair operations that resolve it (the
# M36 estimate starts from that), and FR-CAT-020 gives a service its default
# SLA template. None of it existed.
#
# - fix.fault.symptom: what the customer reports, bilingual, per device type.
# - fix.fault.code: Bengali name, the symptoms it presents as, its root causes
#   (lines) and its resolving operations.
# - fix.catalogue.item: the inverse operation <-> fault mapping and the
#   default SLA template (M08 may override it contractually).
from odoo import api, fields, models
from odoo.exceptions import ValidationError

DEVICE_TYPES = [
    ("any", "Any device"),
    ("smartphone", "Smartphone"),
    ("tablet", "Tablet"),
    ("laptop", "Laptop"),
    ("desktop", "Desktop"),
    ("tv", "Television"),
    ("appliance", "Home appliance"),
    ("other", "Other"),
]


class FixFaultSymptom(models.Model):
    """FR-CAT-042: the top of the taxonomy - the symptom as the customer
    describes it at intake."""

    _name = "fix.fault.symptom"
    _description = "Fault Symptom (customer-reported)"
    _order = "code"
    _rec_name = "name"

    code = fields.Char(required=True, index=True)
    name = fields.Char(string="Symptom (English)", required=True)
    name_bn = fields.Char(string="Symptom (Bengali)")
    device_type = fields.Selection(DEVICE_TYPES, required=True, default="any")
    description = fields.Text(string="How the Customer Says It")
    fault_code_ids = fields.Many2many(
        "fix.fault.code",
        "fix_fault_code_symptom_rel",
        "symptom_id",
        "fault_id",
        string="Fault Codes It Presents As",
    )
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("UNIQUE (code)", "Symptom code must be unique")

    @api.onchange("code")
    def _onchange_code(self):
        if self.code:
            self.code = self.code.strip().upper()


class FixFaultRootCause(models.Model):
    """FR-CAT-042: the bottom of the taxonomy - why the fault happened."""

    _name = "fix.fault.root.cause"
    _description = "Fault Root Cause"
    _order = "fault_id, code"

    fault_id = fields.Many2one(
        "fix.fault.code", string="Fault Code", required=True, index=True, ondelete="cascade"
    )
    code = fields.Char(required=True)
    name = fields.Char(string="Root Cause (English)", required=True)
    name_bn = fields.Char(string="Root Cause (Bengali)")
    is_customer_induced = fields.Boolean(
        string="Customer-Induced",
        help="Liquid, drop, misuse: the brand warranty does not cover it (M09).",
    )

    _code_per_fault = models.Constraint(
        "UNIQUE (fault_id, code)", "A root-cause code appears once under a fault code."
    )


class FixFaultCodeTaxonomy(models.Model):
    _inherit = "fix.fault.code"

    name_bn = fields.Char(string="Fault (Bengali)")
    symptom_ids = fields.Many2many(
        "fix.fault.symptom",
        "fix_fault_code_symptom_rel",
        "fault_id",
        "symptom_id",
        string="Presents As (Symptoms)",
    )
    root_cause_ids = fields.One2many("fix.fault.root.cause", "fault_id", string="Root Causes")
    operation_ids = fields.Many2many(
        "fix.catalogue.item",
        "fix_fault_code_operation_rel",
        "fault_id",
        "item_id",
        string="Resolving Operations",
        domain=[("item_type", "in", ["labour", "service", "inspection"])],
        help="The repair operations that typically resolve this fault (FR-CAT-025); the "
        "estimate is pre-populated from them.",
    )

    @api.constrains("operation_ids")
    def _check_operations(self):
        for rec in self:
            wrong = rec.operation_ids.filtered(
                lambda i: i.item_type not in ("labour", "service", "inspection")
            )
            if wrong:
                raise ValidationError(
                    "%s is a %s item, not a repair operation." % (wrong[0].name, wrong[0].item_type)
                )


class FixCatalogueItemFaults(models.Model):
    _inherit = "fix.catalogue.item"

    fault_code_ids = fields.Many2many(
        "fix.fault.code",
        "fix_fault_code_operation_rel",
        "item_id",
        "fault_id",
        string="Faults It Resolves",
    )
    default_sla_policy_id = fields.Many2one(
        "fix.sla.policy",
        string="Default SLA Template",
        ondelete="restrict",
        help="FR-CAT-020: the SLA a job for this service starts under; a contract may "
        "override it.",
    )
