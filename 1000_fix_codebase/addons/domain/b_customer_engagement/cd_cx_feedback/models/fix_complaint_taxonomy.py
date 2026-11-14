# M34 capture audit, second pass (14 Nov 2026): the maintained complaint
# taxonomy (spec section 10.1 fix.complaint.taxonomy, FR-CXM-030).
#
# FR-CXM-030 asks for complaints categorised "using a maintained taxonomy";
# section 13 gives the taxonomy to the Customer Service Manager (C R U D A).
# The estate had only a fixed six-value selection on fix.complaint, so the
# "Categorisation & SLA" page had nothing a person could capture.
#
# A taxonomy node is READ by every complaint that names it:
#   * the complaint's ISO category follows its node (a child carries its
#     parent's category, so a sub-category can never contradict its parent);
#   * a complaint raised under a node with a default severity starts at no
#     less than that severity (after intake the severity moves only through
#     Assess / Reassess, which rebind the SLA);
#   * the Category Pareto counts by node.
#
# Who writes it: the Contact Centre Supervisor group (the estate's holder of
# the Customer Service Manager's registers since the M32 pass) and the
# administrator. Every internal user reads it, because every intake names it.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

# The ISO category the complaint already carries (fix.complaint.category).
# Kept as the top level so the existing reports, events and filters keep
# their meaning; the taxonomy adds the maintained detail below it.
ISO_CATEGORIES = [
    ("service_quality", "Service Quality"),
    ("delay", "Delay / SLA"),
    ("billing", "Billing"),
    ("staff_conduct", "Staff Conduct"),
    ("device_damage", "Device Damage"),
    ("other", "Other"),
]
SEVERITY_SELECTION = [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")]
SEVERITY_RANK = {"minor": 0, "major": 1, "critical": 2}


class FixComplaintTaxonomy(models.Model):
    """One node of the complaint category tree, in English and Bengali."""

    _name = "fix.complaint.taxonomy"
    _description = "Complaint Category"
    _inherit = ["mail.thread"]
    _order = "category, complete_name, id"
    _rec_name = "complete_name"
    _parent_store = True

    code = fields.Char(required=True, tracking=True, help="Short stable code, e.g. DLY-PARTS.")
    name = fields.Char(string="Category (English)", required=True, tracking=True)
    name_bn = fields.Char(
        string="Category (Bengali)",
        required=True,
        tracking=True,
        help="DE-17: the category is read back to the customer in the "
        "acknowledgement, so it exists in Bengali.",
    )
    parent_id = fields.Many2one(
        "fix.complaint.taxonomy",
        string="Parent Category",
        index=True,
        ondelete="restrict",
        tracking=True,
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many("fix.complaint.taxonomy", "parent_id", string="Sub-categories")
    complete_name = fields.Char(compute="_compute_complete_name", store=True, recursive=True)
    category = fields.Selection(
        ISO_CATEGORIES,
        string="ISO Category",
        required=True,
        tracking=True,
        help="The top-level complaint category. A sub-category always carries its parent's.",
    )
    default_severity = fields.Selection(
        SEVERITY_SELECTION,
        tracking=True,
        help="The severity a complaint of this category starts at when the "
        "intake gives none. Assessment can still change it.",
    )
    description = fields.Text(help="When to use this category, for the person at intake.")
    active = fields.Boolean(default=True, tracking=True)
    complaint_count = fields.Integer(compute="_compute_complaint_count", string="Complaints")

    _code_unique = models.Constraint("UNIQUE (code)", "A complaint category code is used once.")

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for node in self:
            node.complete_name = (
                "%s / %s" % (node.parent_id.complete_name, node.name)
                if node.parent_id
                else node.name
            )

    def _compute_complaint_count(self):
        groups = (
            self.env["fix.complaint"]
            .sudo()
            ._read_group([("taxonomy_id", "in", self.ids)], ["taxonomy_id"], ["__count"])
        )
        counts = {node.id: count for node, count in groups}
        for node in self:
            node.complaint_count = counts.get(node.id, 0)

    @api.constrains("parent_id")
    def _check_no_cycle(self):
        if self._has_cycle():
            raise ValidationError("A complaint category cannot sit under itself.")

    @api.constrains("parent_id", "category")
    def _check_category_follows_parent(self):
        for node in self:
            if node.parent_id and node.parent_id.category != node.category:
                raise ValidationError(
                    "'%s' sits under '%s', so its ISO category must be %s."
                    % (
                        node.name,
                        node.parent_id.complete_name,
                        dict(ISO_CATEGORIES).get(node.parent_id.category),
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        # A sub-category takes its parent's ISO category when none is given,
        # so the person at the form only picks the parent.
        for vals in vals_list:
            if vals.get("parent_id") and not vals.get("category"):
                vals["category"] = self.browse(vals["parent_id"]).category
            if vals.get("code"):
                vals["code"] = vals["code"].strip().upper()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("code"):
            vals["code"] = vals["code"].strip().upper()
        if vals.get("parent_id") and "category" not in vals:
            vals["category"] = self.browse(vals["parent_id"]).category
        result = super().write(vals)
        if "category" in vals:
            # The sub-tree follows, then the complaints filed under it.
            descendants = self.search([("id", "child_of", self.ids), ("id", "not in", self.ids)])
            if descendants:
                descendants.write({"category": vals["category"]})
            complaints = (
                self.env["fix.complaint"]
                .sudo()
                .search(
                    [
                        ("taxonomy_id", "child_of", self.ids),
                        ("state", "not in", ("closed", "rejected")),
                        ("category", "!=", vals["category"]),
                    ]
                )
            )
            if complaints:
                complaints.write({"category": vals["category"]})
        return result


class FixComplaintTaxonomyLink(models.Model):
    """fix.complaint names its node; the ISO category follows the node."""

    _inherit = "fix.complaint"

    taxonomy_id = fields.Many2one(
        "fix.complaint.taxonomy",
        string="Complaint Category",
        index=True,
        ondelete="restrict",
        tracking=True,
        domain=[("active", "=", True)],
        help="FR-CXM-030: the maintained category. The ISO category follows it.",
    )

    def _fix_state_locked_fields(self) -> set:
        locked = super()._fix_state_locked_fields()
        if "category" in locked:
            locked = locked | {"taxonomy_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        # The category's default severity is the floor at intake: the new
        # complaint form shows the model default ("Minor"), so a category
        # that is always at least Major (a safety hazard, device damage)
        # would otherwise be filed as Minor by whoever did not change it.
        # After intake the severity moves through Assess / Reassess.
        Taxonomy = self.env["fix.complaint.taxonomy"].sudo()
        raised = []
        for vals in vals_list:
            if vals.get("taxonomy_id"):
                node = Taxonomy.browse(vals["taxonomy_id"])
                vals["category"] = node.category
                given = vals.get("severity") or "minor"
                floor = node.default_severity
                if floor and SEVERITY_RANK[floor] > SEVERITY_RANK[given]:
                    vals["severity"] = floor
                    raised.append((given, floor, node.complete_name))
                else:
                    raised.append(None)
            else:
                raised.append(None)
        records = super().create(vals_list)
        for rec, note in zip(records, raised, strict=True):
            if note:
                rec.message_post(
                    body="Severity raised from %s to %s at intake: category '%s' starts at %s."
                    % (note[0], note[1], note[2], note[1])
                )
        return records

    def write(self, vals):
        if vals.get("taxonomy_id"):
            node = self.env["fix.complaint.taxonomy"].sudo().browse(vals["taxonomy_id"])
            vals = dict(vals, category=node.category)
        return super().write(vals)

    @api.constrains("taxonomy_id", "category")
    def _check_category_matches_taxonomy(self):
        for rec in self:
            if rec.taxonomy_id and rec.taxonomy_id.category != rec.category:
                raise ValidationError(
                    "Complaint %s is filed under '%s', whose ISO category is %s; "
                    "change the complaint category instead of the ISO category."
                    % (
                        rec.name,
                        rec.taxonomy_id.complete_name,
                        dict(ISO_CATEGORIES).get(rec.taxonomy_id.category),
                    )
                )
