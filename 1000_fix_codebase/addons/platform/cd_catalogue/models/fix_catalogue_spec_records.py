# M37 capture audit (2026-11-14): three records the spec (§10.1) owns that the
# estate did not have, so three sub-module pages had nothing relevant to
# capture.
#
# - fix.srt.baseline  (FR-CAT-023/024, BRU-CAT-11): the effective-dated
#   standard-repair-time register. The SRT was one float on the item, typed
#   in place; now an officer proposes a baseline with its evidence and a
#   publisher who did not propose it approves it, which is what moves the
#   item's standard time.
# - fix.part.crossref (FR-CAT-030): OEM <-> aftermarket cross-references and
#   approved alternates, with direction and a quality note.
# - fix.catalogue.publication (FR-CAT-044): a versioned channel projection -
#   what was published to which channel, when, by whom, its content hash and
#   its completeness score; an incomplete customer-facing projection is
#   refused.
#
# File name sorts after fix_catalogue_item (ruff I001 re-sorts the imports in
# models/__init__.py, and these models point at the item).
import hashlib

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .catalogue_roles import ROLE_OFFICER, ROLE_PUBLISHER, require_role
from .fix_catalogue_item import REPAIR_LEVELS, SELLABLE_STATES

SRT_SOURCES = [
    ("initial", "Initial baseline"),
    ("time_study", "Time study"),
    ("oem", "Brand / OEM published time"),
    ("calibration", "Calibration from measured actuals (M01 / M31)"),
]
SRT_STATES = [
    ("draft", "Draft"),
    ("proposed", "Proposed"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("superseded", "Superseded"),
]
# What a proposal covers: none of it changes once it leaves Draft.
SRT_TERMS = frozenset(
    {
        "item_id",
        "device_model_id",
        "repair_level",
        "minutes",
        "source",
        "sample_size",
        "observed_avg_minutes",
        "effective_from",
        "reason",
        "company_id",
    }
)
SRT_DECISION = frozenset(
    {
        "state",
        "previous_minutes",
        "proposed_by",
        "proposed_at",
        "approved_by",
        "approved_at",
        "applied_at",
        "rejection_reason",
    }
)
# The items an SRT belongs to: the ones a technician performs.
SRT_ITEM_TYPES = ("labour", "service", "inspection")


class FixSrtBaseline(models.Model):
    """One standard repair time, proposed with its evidence and approved by a
    second person before it moves the item (BRU-CAT-11)."""

    _name = "fix.srt.baseline"
    _description = "Standard Repair Time Baseline"
    _inherit = ["fix.guarded.mixin", "mail.thread"]
    _order = "item_id, effective_from desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    item_id = fields.Many2one(
        "fix.catalogue.item",
        string="Repair Operation / Service",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("item_type", "in", list(SRT_ITEM_TYPES))],
    )
    device_model_id = fields.Many2one(
        "fix.device.model",
        string="Device Model",
        ondelete="restrict",
        help="Blank: the operation's general standard time, which is what the item carries. "
        "A model makes it a model-specific time.",
    )
    repair_level = fields.Selection(REPAIR_LEVELS, string="Repair Level", required=True)
    minutes = fields.Float(string="Standard Time (minutes)", required=True)
    previous_minutes = fields.Float(
        string="Standard Before (minutes)",
        readonly=True,
        help="The item's standard time when this baseline was proposed.",
    )
    source = fields.Selection(SRT_SOURCES, required=True, default="time_study")
    sample_size = fields.Integer(
        string="Measured Jobs", help="Jobs the calibration was measured on."
    )
    observed_avg_minutes = fields.Float(string="Measured Average (minutes)")
    effective_from = fields.Date(required=True, default=fields.Date.context_today, index=True)
    reason = fields.Text(string="Why This Baseline", required=True)
    state = fields.Selection(SRT_STATES, required=True, default="draft", tracking=True, index=True)
    proposed_by = fields.Many2one("res.users", readonly=True, copy=False)
    proposed_at = fields.Datetime(readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    applied_at = fields.Datetime(
        readonly=True, copy=False, help="When the item's standard time was moved to it."
    )
    rejection_reason = fields.Text(readonly=True, copy=False)

    _minutes_positive = models.Constraint(
        "CHECK (minutes > 0)", "A standard repair time needs a positive number of minutes."
    )

    @api.depends("item_id", "device_model_id", "repair_level", "minutes", "effective_from")
    def _compute_name(self):
        levels = dict(REPAIR_LEVELS)
        for rec in self:
            rec.name = "%s%s · %s · %g min from %s" % (
                rec.item_id.name or "?",
                " / %s" % rec.device_model_id.name if rec.device_model_id else "",
                (levels.get(rec.repair_level) or "").split(" - ")[0],
                rec.minutes or 0.0,
                rec.effective_from or "",
            )

    # ---- guard ------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(SRT_DECISION)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= SRT_TERMS
        return locked

    @api.constrains("item_id")
    def _check_item_type(self):
        for rec in self:
            if rec.item_id.item_type not in SRT_ITEM_TYPES:
                raise ValidationError(
                    "A standard repair time belongs to a repair operation, service or "
                    "inspection, not to a %s item (%s)."
                    % (rec.item_id.item_type, rec.item_id.display_name)
                )

    @api.constrains("source", "sample_size", "observed_avg_minutes")
    def _check_calibration_evidence(self):
        """FR-CAT-024: a calibration re-baseline rests on measured actuals."""
        for rec in self.filtered(lambda r: r.source == "calibration"):
            if rec.sample_size <= 0 or rec.observed_avg_minutes <= 0:
                raise ValidationError(
                    "A calibration baseline states how many jobs were measured and their "
                    "measured average time."
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Proposing a standard repair time")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER,), "Changing a standard repair time")
            terms = SRT_TERMS & set(vals)
            for rec in self.filtered(lambda r: r.state != "draft"):
                moved = [n for n in terms if rec._fix_guard_differs(n, vals[n], rec[n])]
                if moved:
                    raise UserError(
                        "This baseline is %s: what it proposes is fixed. Propose a new one."
                        % dict(SRT_STATES)[rec.state]
                    )
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "A %s standard-time baseline is history and is never deleted."
                    % dict(SRT_STATES)[rec.state]
                )
        if not self.env.su:
            require_role(self.env, (ROLE_OFFICER,), "Deleting a standard repair time")
        return super().unlink()

    # ---- workflow ---------------------------------------------------------
    def action_propose(self):
        require_role(self.env, (ROLE_OFFICER,), "Proposing a standard repair time")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a Draft baseline is proposed.")
            rec._guarded().write(
                {
                    "state": "proposed",
                    "proposed_by": self.env.uid,
                    "proposed_at": fields.Datetime.now(),
                    "previous_minutes": (rec.item_id.standard_labour_time or 0.0) * 60.0,
                    "rejection_reason": False,
                }
            )
            rec.message_post(body="Proposed by %s." % self.env.user.name)
        return True

    def action_approve(self):
        """BRU-CAT-11: the governed re-baseline. A publisher who neither wrote
        nor proposed it approves; the item's standard time moves on the
        effective date (today or by the daily job)."""
        require_role(
            self.env,
            (ROLE_PUBLISHER,),
            "Approving a standard repair time",
            role="Catalogue Publisher",
        )
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Only a Proposed baseline is approved.")
            if not self.env.su and self.env.user & (rec.create_uid | rec.proposed_by):
                raise UserError(
                    "Segregation of duties: you wrote or proposed this baseline, so another "
                    "publisher approves it (BRU-CAT-05/11)."
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Approved by %s." % self.env.user.name)
        self.filtered(lambda r: r.effective_from <= fields.Date.context_today(r))._apply()
        return True

    def action_reject(self, reason=None):
        require_role(
            self.env,
            (ROLE_PUBLISHER,),
            "Rejecting a standard repair time",
            role="Catalogue Publisher",
        )
        if not (reason or "").strip():
            raise UserError("State why the baseline is rejected.")
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Only a Proposed baseline is rejected.")
            rec._guarded().write({"state": "rejected", "rejection_reason": reason})
            rec.message_post(body="Rejected by %s: %s" % (self.env.user.name, reason))
        return True

    def _apply(self):
        """Supersede the baseline it replaces; a general one (no model) also
        moves the item's standard time, through the item's guard."""
        for rec in self.filtered(lambda r: r.state == "approved" and not r.applied_at):
            older = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("item_id", "=", rec.item_id.id),
                    ("device_model_id", "=", rec.device_model_id.id or False),
                    ("repair_level", "=", rec.repair_level),
                    ("state", "=", "approved"),
                    ("applied_at", "!=", False),
                ]
            )
            older._guarded().write({"state": "superseded"})
            rec._guarded().write({"applied_at": fields.Datetime.now()})
            if not rec.device_model_id:
                rec.item_id.sudo()._guarded().write({"standard_labour_time": rec.minutes / 60.0})
                rec.item_id.sudo().message_post(
                    body="Standard repair time re-baselined to %g min (approved baseline #%d)."
                    % (rec.minutes, rec.id)
                )

    @api.model
    def cron_apply_due_baselines(self):
        """Approved baselines whose effective date has come. Idempotent."""
        due = self.search(
            [
                ("state", "=", "approved"),
                ("applied_at", "=", False),
                ("effective_from", "<=", fields.Date.context_today(self)),
            ],
            order="effective_from, id",
        )
        due._apply()
        return len(due)


CROSSREF_RELATIONS = [
    ("oem_equivalent", "OEM equivalent (same part, other code)"),
    ("approved_alternate", "Approved alternate"),
    ("aftermarket", "Aftermarket equivalent"),
    ("compatible", "Compatible substitute (with limits)"),
]
# The relations where the quality of the alternate differs from the part's:
# the directional quality note is mandatory there (FR-CAT-030).
NOTE_REQUIRED = ("aftermarket", "compatible")
PART_TYPES = ("part", "accessory")


class FixPartCrossref(models.Model):
    """FR-CAT-030: a part's cross-reference or approved alternate."""

    _name = "fix.part.crossref"
    _description = "Part Cross-Reference / Alternate"
    _order = "part_item_id, relation_type, id"
    _rec_name = "display_label"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    part_item_id = fields.Many2one(
        "fix.catalogue.item",
        string="Part",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("item_type", "in", list(PART_TYPES))],
    )
    alt_item_id = fields.Many2one(
        "fix.catalogue.item",
        string="Alternate / Cross-Referenced Part",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("item_type", "in", list(PART_TYPES))],
    )
    relation_type = fields.Selection(CROSSREF_RELATIONS, string="Relation", required=True)
    direction = fields.Selection(
        [
            ("one_way", "One way: the alternate may replace the part"),
            ("two_way", "Both ways: either replaces the other"),
        ],
        required=True,
        default="one_way",
    )
    device_model_ids = fields.Many2many(
        "fix.device.model",
        string="Only For Models",
        help="Blank: wherever the part fits. Otherwise the alternate is valid only on these models.",
    )
    quality_note = fields.Text(
        string="Quality Note",
        help="How the alternate differs in quality, life or warranty. Mandatory for an "
        "aftermarket or compatible alternate.",
    )
    active = fields.Boolean(default=True)
    display_label = fields.Char(compute="_compute_display_label", store=True)

    _unique_relation = models.Constraint(
        "UNIQUE (part_item_id, alt_item_id, relation_type)",
        "This cross-reference is already recorded.",
    )
    _not_self = models.Constraint(
        "CHECK (part_item_id <> alt_item_id)", "A part is not its own alternate."
    )

    @api.depends("part_item_id", "alt_item_id", "relation_type", "direction")
    def _compute_display_label(self):
        for rec in self:
            rec.display_label = "%s %s %s" % (
                rec.part_item_id.name or "?",
                "<->" if rec.direction == "two_way" else "->",
                rec.alt_item_id.name or "?",
            )

    @api.constrains("part_item_id", "alt_item_id", "relation_type", "quality_note")
    def _check_crossref(self):
        for rec in self:
            for item in rec.part_item_id | rec.alt_item_id:
                if item.item_type not in PART_TYPES:
                    raise ValidationError(
                        "A cross-reference links spare parts or accessories; %s is a %s item."
                        % (item.display_name, item.item_type)
                    )
            if rec.relation_type in NOTE_REQUIRED and not (rec.quality_note or "").strip():
                raise ValidationError(
                    "An %s alternate needs its quality note (FR-CAT-030)."
                    % dict(CROSSREF_RELATIONS)[rec.relation_type].lower()
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Recording a part cross-reference")
        return super().create(vals_list)

    def write(self, vals):
        require_role(self.env, (ROLE_OFFICER,), "Changing a part cross-reference")
        return super().write(vals)

    def unlink(self):
        require_role(self.env, (ROLE_OFFICER,), "Deleting a part cross-reference")
        return super().unlink()


PUBLICATION_CHANNELS = [
    ("portal", "Customer portal / website"),
    ("app", "Customer mobile app"),
    ("corporate", "Corporate (B2B) portal"),
    ("marketplace", "Marketplace"),
    ("print", "Printed catalogue"),
    ("pos", "Counter / POS (staff-facing)"),
]
# Customer-facing projections carry only published items and are refused
# when any of them is incomplete (FR-CAT-044, BRU-CAT-04); the staff POS
# carries every sellable item and records its score.
CUSTOMER_FACING = ("portal", "app", "corporate", "marketplace", "print")
# Computed at publication; nobody types them (the workspace form re-sends
# every field it shows, so an unchanged value is accepted, a changed one not).
PUBLICATION_SNAPSHOT = frozenset(
    {
        "version",
        "item_count",
        "incomplete_count",
        "completeness_pct",
        "content_hash",
        "published_at",
    }
)
PUBLICATION_FIXED = frozenset({"channel", "company_id"})


class FixCataloguePublication(models.Model):
    """FR-CAT-044: one versioned catalogue projection published to a channel.
    It is a snapshot: written once, never edited (except its note) or deleted."""

    _name = "fix.catalogue.publication"
    _description = "Catalogue Channel Publication"
    _inherit = ["fix.guarded.mixin"]
    _order = "published_at desc, id desc"
    _rec_name = "display_label"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    channel = fields.Selection(PUBLICATION_CHANNELS, required=True, index=True)
    version = fields.Integer(readonly=True, copy=False)
    item_count = fields.Integer(readonly=True, copy=False)
    incomplete_count = fields.Integer(
        string="Incomplete Items",
        readonly=True,
        copy=False,
        help="Items without their Bengali name or hierarchy position.",
    )
    completeness_pct = fields.Float(string="Completeness (%)", readonly=True, copy=False)
    content_hash = fields.Char(readonly=True, copy=False)
    published_at = fields.Datetime(readonly=True, copy=False)
    note = fields.Text(string="Release Note")
    display_label = fields.Char(compute="_compute_display_label", store=True)

    @api.depends("channel", "version")
    def _compute_display_label(self):
        names = dict(PUBLICATION_CHANNELS)
        for rec in self:
            rec.display_label = "%s v%d" % (names.get(rec.channel) or "?", rec.version or 0)

    @api.model
    def _incomplete_for(self, items, channel):
        """Items without their Bengali name or hierarchy position, or (third
        pass, FR-CAT-005/044) without an attribute their class's attribute
        set requires for this channel."""
        Sets = self.env["fix.catalogue.attribute.set"]
        sets = {}

        def lacking(item):
            if not (item.name_bn or "").strip() or not item.category_id:
                return True
            if item.item_type not in sets:
                sets[item.item_type] = Sets._for(item.item_type)
            attr_set = sets[item.item_type]
            return bool(attr_set and attr_set._missing(item, channel))

        return items.filtered(lacking)

    def _projection(self, channel):
        Item = self.env["fix.catalogue.item"].sudo()
        states = ("published",) if channel in CUSTOMER_FACING else SELLABLE_STATES
        return Item.search([("state", "in", list(states))], order="id")

    @api.model_create_multi
    def create(self, vals_list):
        require_role(
            self.env,
            (ROLE_PUBLISHER,),
            "Publishing a catalogue projection",
            role="Catalogue Publisher",
        )
        prepared = []
        for vals in vals_list:
            vals = dict(vals)
            channel = vals.get("channel")
            if channel not in dict(PUBLICATION_CHANNELS):
                raise UserError("Choose the channel to publish to.")
            items = self._projection(channel)
            if not items:
                raise UserError(
                    "There is nothing to publish to %s: no item is %s."
                    % (
                        dict(PUBLICATION_CHANNELS)[channel],
                        "Active and Published" if channel in CUSTOMER_FACING else "Active",
                    )
                )
            incomplete = self._incomplete_for(items, channel)
            if channel in CUSTOMER_FACING and incomplete:
                raise UserError(
                    "%d of the %d items for %s lack their Bengali name or hierarchy position; "
                    "an incomplete customer-facing catalogue is not published (FR-CAT-044)."
                    % (len(incomplete), len(items), dict(PUBLICATION_CHANNELS)[channel])
                )
            digest = hashlib.sha256(
                "|".join(
                    "%d:%s:%s" % (i.id, i.state, fields.Datetime.to_string(i.write_date))
                    for i in items
                ).encode()
            ).hexdigest()
            last = self.sudo().search([("channel", "=", channel)], order="version desc", limit=1)
            vals.update(
                {
                    "version": (last.version or 0) + 1,
                    "item_count": len(items),
                    "incomplete_count": len(incomplete),
                    "completeness_pct": round(
                        100.0 * (len(items) - len(incomplete)) / len(items), 2
                    ),
                    "content_hash": digest,
                    "published_at": fields.Datetime.now(),
                }
            )
            prepared.append(vals)
        records = super(FixCataloguePublication, self._guarded()).create(prepared)
        # hand back records WITHOUT the guard token in their context, or the
        # caller's next write on them would pass the snapshot guard
        return self.browse(records.ids)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(PUBLICATION_SNAPSHOT)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= PUBLICATION_FIXED
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(
                self.env, (ROLE_PUBLISHER,), "Editing a release note", role="Catalogue Publisher"
            )
            for rec in self:
                moved = [
                    n
                    for n in PUBLICATION_FIXED & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if moved:
                    raise UserError(
                        "A published catalogue projection is a snapshot; only its release "
                        "note changes."
                    )
        return super().write(vals)

    def unlink(self):
        raise UserError("A catalogue publication is history and is never deleted.")
