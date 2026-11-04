# fix.catalogue.item — catalogue metadata on product.template (P03-M06-T01).
# The catalogue kernel: every downstream module (M01, M11, M12, M13, M14, M15)
# consumes this rather than re-inventing product concepts.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .catalogue_roles import (
    RESTRICTED_CHANNELS,
    ROLE_OFFICER,
    ROLE_PUBLISHER,
    SALE_GATE_PARAM,
    require_role,
)

logger = logging.getLogger(__name__)

# A04 audit (2026-11-04) M37-1/M37-2: the lifecycle of the spec (§8). The
# keys of the first version are kept (approved = Active, deprecated =
# Discontinued) so the live rows and the reports keep their meaning.
ITEM_STATES = [
    ("draft", "Draft"),
    ("in_review", "In Review"),
    ("approved", "Active"),
    ("published", "Active and Published"),
    ("restricted", "Restricted"),
    ("deprecated", "Discontinued"),
    ("obsolete", "Obsolete"),
]
# States in which an item may be sold, quoted or contracted (BRU-CAT-14).
SELLABLE_STATES = ("approved", "published", "restricted")
# Never sold again: no new sale of a discontinued or obsolete item.
CLOSED_STATES = ("deprecated", "obsolete")
# What the approval covers: the classification an approved item is sold
# under. Changing it means revising the item (back to Draft, approved again).
FROZEN_WHEN_DECIDED = frozenset(
    {
        "product_tmpl_id",
        "item_type",
        "category_id",
        "brand_id",
        "company_id",
        "is_out_of_scope",
        "is_warranty_eligible",
        "requires_brand_authorisation",
    }
)
LIFECYCLE_FIELDS = frozenset(
    {
        "state",
        "approved_by",
        "approved_at",
        "submitted_by",
        "submitted_at",
        "is_published",
        "rejection_reason",
        "restriction_reason",
        "discontinued_at",
        "discontinue_reason",
        "successor_id",
        "end_of_support_date",
    }
)


class FixCatalogueItem(models.Model):
    """Catalogue metadata for a product or service.

    Extends product.template via a separate model — one catalogue item per
    product.template. The TSS §3.2 kernel row 2: "a single product catalogue
    with service kits, parts, bundles".
    """

    _name = "fix.catalogue.item"
    _description = "Catalogue Item"
    # A04 audit (2026-11-04) M37-1: state, approver and publication were free
    # fields; the guard makes them change only through the lifecycle below.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "product_tmpl_id"
    # Without a name source Odoo falls back to "model,id" for display_name,
    # so EVERY many2one pointing at a catalogue item rendered as
    # "fix.catalogue.item,19739" - on the kit list, on estimates, anywhere
    # one was shown. The catalogue wraps a product.template one-to-one, so
    # the product's name is its name.
    # (A04 audit, 2026-11-01, raised from the M37 Kits & Bundles panel.)
    #
    # Done as a compute, NOT as a stored related Char. product.template.name
    # is translatable (jsonb), and Odoo warns that a stored related on a
    # translated field "will not be computed correctly in all languages" -
    # which in a bilingual-by-mandate estate (DE-17) means a Bengali session
    # could read a stale English name. Resolving through the relation each
    # time is always right in the active language.

    # AS-03: company_id + operating_unit_id
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product Template",
        required=True,
        ondelete="cascade",
        index=True,
        help="The product this catalogue item wraps — one-to-one",
    )
    # The English name, mirroring the wrapped product template - the pair to
    # name_bn below, declared the same way for the same reason.
    #
    # This is NOT optional decoration: without it fix.catalogue.item has no
    # name source at all, Odoo falls back to "model,id", and every many2one
    # pointing here renders as "fix.catalogue.item,19739" - on kits, rate
    # cards, rBOM lines, rental SKUs and price simulations.
    #
    # READ-ONLY on purpose. name_bn was once writable here and editing it
    # overwrote the product's English name (R01 re-audit 2026-10-22).
    #
    # Removing this field DROPS the column, and a running Odoo whose registry
    # still expects it then fails every read of this model with
    # UndefinedColumn. Do not delete it without restarting the server
    # (A04 audit, 2026-11-01).
    name = fields.Char(
        related="product_tmpl_id.name",
        string="Name",
        store=True,
        readonly=True,
        index=True,
    )

    # DE-17 Bengali-first
    # R01 re-audit 2026-10-22: this mirrored product_tmpl_id.NAME (the English,
    # translatable name) - the "Bengali" column showed English, and editing it
    # overwrote the product's English name. It mirrors the Bengali name.
    name_bn = fields.Char(
        related="product_tmpl_id.name_bn", string="Name (Bengali)", readonly=False, store=True
    )
    description_bn = fields.Char(string="Description (Bengali)")

    # Catalogue classification
    item_type = fields.Selection(
        [
            ("service", "Service"),
            ("part", "Spare Part"),
            ("accessory", "Accessory"),
            ("bundle", "Bundle / Kit"),
            ("labour", "Labour Only"),
            ("inspection", "Inspection / Diagnostic"),
            # M37 re-audit: the registry's form promises NINE catalogue item
            # types (FR-CAT); the enum only had six. The protection, rental and
            # subscription SKU families are now first-class types.
            ("protection", "Protection Plan"),
            ("rental", "Rental SKU"),
            ("subscription", "Subscription / Contract"),
        ],
        required=True,
        default="service",
        tracking=True,
        help="The catalogue item type determines which modules may consume it",
    )
    category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        help="Odoo's own category tree; the catalogue's organisational spine",
    )
    brand_id = fields.Many2one(
        "fix.brand", string="Brand", help="Brand master — 17+ brand partners"
    )
    device_model_ids = fields.Many2many(
        "fix.device.model",
        string="Compatible Device Models",
        help="Which device models this item is compatible with",
    )

    # AS-10 (FF-22): every price is Monetary with explicit currency_id.
    # NEVER Float for a price field.
    standard_labour_time = fields.Float(
        string="Standard Labour Time (hours)",
        help="The estimated labour hours for this service — used by M01 for "
        "scheduling and M54 for cost allocation",
    )

    # Flags
    is_warranty_eligible = fields.Boolean(
        default=True,
        tracking=True,
        help="Whether this item can be serviced under manufacturer warranty",
    )
    is_out_of_scope = fields.Boolean(
        default=False, help="Items marked out-of-scope are refused at intake (M01)"
    )
    requires_brand_authorisation = fields.Boolean(
        default=False, help="True for items that only a brand-authorised technician may handle"
    )
    active = fields.Boolean(default=True, tracking=True)

    # M37 lifecycle & publication (v2 rebuild): the registry promises an
    # approval queue, a lifecycle view and a publication/Bilingual-gap
    # report — those need a state, an approver and a public flag.
    # A04 audit (2026-11-04) M37-1: every one of them changes only through a
    # transition (submit, approve from the M63 inbox, publish, restrict,
    # discontinue, revise); none is typed.
    state = fields.Selection(
        ITEM_STATES,
        required=True,
        default="draft",
        tracking=True,
        index=True,
    )
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    submitted_by = fields.Many2one("res.users", string="Submitted By", readonly=True, copy=False)
    submitted_at = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Text(readonly=True, copy=False)
    is_published = fields.Boolean(
        string="Published on the Web",
        readonly=True,
        copy=False,
        help="Visible in the public catalogue. Set by Publish, never typed.",
    )
    restriction_reason = fields.Text(readonly=True, copy=False)
    discontinued_at = fields.Date(readonly=True, copy=False)
    discontinue_reason = fields.Text(
        readonly=True, copy=False, help="Why there is no successor, when none is declared."
    )
    successor_id = fields.Many2one(
        "fix.catalogue.item",
        string="Successor Item",
        readonly=True,
        copy=False,
        help="The item that replaces a discontinued one (BRU-CAT-09).",
    )
    end_of_support_date = fields.Date(
        readonly=True,
        copy=False,
        help="After this date the discontinued item becomes Obsolete (nightly job).",
    )
    proposed_successor_id = fields.Many2one(
        "fix.catalogue.item",
        string="Proposed Successor",
        copy=False,
        help="Staged by the officer; Discontinue reads it.",
    )
    proposed_end_of_support = fields.Date(
        string="Proposed End of Support", copy=False, help="Staged; Discontinue reads it."
    )
    is_sellable = fields.Boolean(
        compute="_compute_is_sellable",
        help="Whether a new sale of this item is accepted now (BRU-CAT-14).",
    )
    srt_observed_minutes = fields.Float(
        string="Observed Repair Minutes",
        help="Measured workshop time for the SRT calibration-variance report.",
    )

    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _product_tmpl_unique = models.Constraint(
        "UNIQUE (product_tmpl_id)", "Each product.template maps to exactly one catalogue item"
    )

    @api.constrains("state", "is_published", "name_bn")
    def _check_bengali_name_on_publish(self):
        """Bangla-first catalogue integrity gate (FLAW-37.1)."""
        for rec in self:
            if (rec.state == "published" or rec.is_published) and not (
                rec.name_bn and rec.name_bn.strip()
            ):
                raise ValidationError(
                    f"Catalogue Item '{rec.product_tmpl_id.name or rec.id}' cannot be published without a Bengali name (name_bn). "
                    "Bangla-first catalogue compliance is mandatory."
                )

    # ---- guard -----------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(LIFECYCLE_FIELDS)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= FROZEN_WHEN_DECIDED
        return locked

    # ---- sellability (BRU-CAT-14, A04 audit M37-2) --------------------------
    def _sale_gate_on(self) -> bool:
        raw = self.env["ir.config_parameter"].sudo().get_param(SALE_GATE_PARAM, "0")
        return str(raw).strip().lower() not in ("0", "false", "no", "off", "")

    def _sale_refusal(self, channel=None):
        """Why a new sale of this item is refused on `channel`, or None."""
        self.ensure_one()
        item = self.sudo()
        label = item.name or item.product_tmpl_id.display_name or str(item.id)
        if not item.active:
            return "catalogue item '%s' is archived" % label
        if item.state in CLOSED_STATES:
            return "catalogue item '%s' is %s; it is no longer sold%s" % (
                label,
                dict(ITEM_STATES)[item.state],
                " (successor: %s)" % item.successor_id.name if item.successor_id else "",
            )
        if item.state == "restricted" and (channel or "") in RESTRICTED_CHANNELS:
            return "catalogue item '%s' is restricted and is not sold on the %s channel" % (
                label,
                channel,
            )
        if item.is_out_of_scope:
            return "catalogue item '%s' is out of scope for 1000FiX" % label
        if item.requires_brand_authorisation and not (
            item.brand_id and item.brand_id._authorisation_in_force()
        ):
            return (
                "catalogue item '%s' needs a current brand authorisation from %s, which "
                "1000FiX does not hold" % (label, item.brand_id.name or "its brand")
            )
        if item.state not in SELLABLE_STATES and self._sale_gate_on():
            return "catalogue item '%s' is %s; only an Active item is sold" % (
                label,
                dict(ITEM_STATES)[item.state],
            )
        return None

    def _fix_assert_sellable(self, channel=None):
        for rec in self:
            reason = rec._sale_refusal(channel)
            if reason:
                raise UserError("Cannot sell this: %s (BRU-CAT-14)." % reason)
        return True

    @api.depends("state", "active", "is_out_of_scope", "requires_brand_authorisation")
    def _compute_is_sellable(self):
        for rec in self:
            rec.is_sellable = bool(rec.id) and not rec._sale_refusal()

    # ---- create / write / unlink --------------------------------------------
    # Event emission (AS-08). A04 audit M37-8: the event names are literal at
    # every publish() call, so the wiring scanner (FF-48) sees them.
    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Creating a catalogue item")
        records = super().create(vals_list)
        for rec in records:
            publish(
                self.env, "catalogue.item_created", "fix.catalogue.item", rec.id, rec._payload()
            )
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER,), "Changing a catalogue item")
            frozen = FROZEN_WHEN_DECIDED & set(vals)
            decided = self.filtered(lambda r: r.state != "draft")
            if frozen and decided:
                moved = sorted(
                    {
                        name
                        for rec in decided
                        for name in frozen
                        if rec._fix_guard_differs(name, vals[name], rec[name])
                    }
                )
                if moved:
                    raise UserError(
                        "%s is %s: its classification (%s) is what was approved. Revise "
                        "the item (back to Draft) and have the change approved."
                        % (
                            decided[:1].display_name,
                            dict(ITEM_STATES)[decided[:1].state],
                            ", ".join(self._fields[n].string for n in moved),
                        )
                    )
            if "name_bn" in vals and not self.env.su:
                # The Bengali name lives on the product template, which a
                # Catalogue Officer may not write; the role was checked above.
                vals = dict(vals)
                self.mapped("product_tmpl_id").sudo().write({"name_bn": vals.pop("name_bn")})
        result = super().write(vals)
        if "is_out_of_scope" in vals or "is_warranty_eligible" in vals:
            for rec in self:
                publish(
                    self.env,
                    "catalogue.item_changed",
                    "fix.catalogue.item",
                    rec.id,
                    rec._payload(),
                )
        return result

    def _references(self):
        """Every stored many2one in the registry that points at this item, as
        [(model, count)]. BRU-CAT-03: an item ever referenced by a kit, rental
        SKU, rBOM line, rate card, order or listing is never deleted."""
        self.ensure_one()
        out = []
        fields_ = (
            self.env["ir.model.fields"]
            .sudo()
            .search(
                [
                    ("relation", "=", self._name),
                    ("ttype", "=", "many2one"),
                    ("store", "=", True),
                ]
            )
        )
        for f in fields_:
            model = self.env.get(f.model)
            if model is None or model._abstract or not model._auto or f.name not in model._fields:
                continue
            if not model._fields[f.name].store:
                continue
            domain = [(f.name, "=", self.id)]
            if f.model == self._name:
                domain.append(("id", "!=", self.id))
            count = model.sudo().with_context(active_test=False).search_count(domain)
            if count:
                out.append((f.model, count))
        return out

    def unlink(self):
        if not self.env.su:
            require_role(self.env, (ROLE_OFFICER,), "Deleting a catalogue item")
            for rec in self:
                if rec.state != "draft":
                    raise UserError(
                        "%s is %s: a catalogue item that was ever approved is never "
                        "deleted (BRU-CAT-03). Discontinue it instead."
                        % (rec.display_name, dict(ITEM_STATES)[rec.state])
                    )
                refs = rec._references()
                if refs:
                    raise UserError(
                        "%s is referenced by %s and cannot be deleted (BRU-CAT-03). Archive "
                        "or discontinue it instead."
                        % (rec.display_name, ", ".join("%d %s" % (n, m) for m, n in refs))
                    )
        return super().unlink()

    def _payload(self):
        self.ensure_one()
        return {
            "product_tmpl_id": self.product_tmpl_id.id,
            "item_type": self.item_type,
            "brand_id": self.brand_id.id if self.brand_id else None,
        }

    # ---- lifecycle ------------------------------------------------------------
    # Hooks a module carrying the M63 approval engine overrides (cd_rate_card,
    # which loads after both cd_catalogue and cd_workflow_engine): submitting
    # routes the approval, and approve then runs only from the inbox. Without
    # the engine they are no-ops and the role and SoD checks still apply.
    def _catalogue_route_submit(self):
        return None

    def _catalogue_route_guard(self):
        return None

    def _catalogue_authority_user(self):
        return self.env.user

    def _catalogue_acting_users(self):
        return self.env.user

    def _completeness_problems(self):
        """AUT-CAT-01: what keeps this item from leaving Draft."""
        self.ensure_one()
        problems = []
        if not (self.name_bn or "").strip():
            problems.append("a Bengali name (BRU-CAT-04)")
        if not (self.product_tmpl_id.name or "").strip():
            problems.append("an English name")
        if not self.category_id:
            problems.append("a product category (its place in the hierarchy, BRU-CAT-02)")
        Item = self.sudo().with_context(active_test=False)
        code = (self.product_tmpl_id.default_code or "").strip()
        if code:
            dup = Item.search(
                [("id", "!=", self.id), ("product_tmpl_id.default_code", "=ilike", code)],
                limit=1,
            )
            if dup:
                problems.append(
                    "a unique code: '%s' is already used by %s (BRU-CAT-13)" % (code, dup.name)
                )
        same_name = Item.search(
            [
                ("id", "!=", self.id),
                ("name", "=ilike", self.product_tmpl_id.name or ""),
                ("item_type", "=", self.item_type),
            ],
            limit=1,
        )
        if same_name:
            problems.append(
                "a unique name: another %s item is called '%s' (BRU-CAT-13)"
                % (self.item_type, same_name.name)
            )
        return problems

    def action_submit(self):
        """Draft -> In Review (Catalogue Officer), after the completeness and
        duplicate checks; the approval is then routed to a publisher."""
        require_role(self.env, (ROLE_OFFICER,), "Submitting a catalogue item")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a Draft item is submitted for review.")
            problems = rec._completeness_problems()
            if problems:
                raise UserError(
                    "%s cannot leave Draft yet. It needs: %s."
                    % (rec.display_name, "; ".join(problems))
                )
            rec._guarded().write(
                {
                    "state": "in_review",
                    "submitted_by": self.env.uid,
                    "submitted_at": fields.Datetime.now(),
                    "rejection_reason": False,
                }
            )
            rec.message_post(body="Submitted for review by %s." % self.env.user.name)
            rec._catalogue_route_submit()
        return True

    def action_approve(self):
        """In Review -> Active. A Catalogue Publisher who neither authored nor
        submitted the item (BRU-CAT-05, SOD-13); from the M63 inbox."""
        self._catalogue_route_guard()
        authority = self._catalogue_authority_user()
        acting = self._catalogue_acting_users()
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Only an item In Review is approved.")
            if not self.env.su:
                if not authority.has_group(ROLE_PUBLISHER):
                    raise UserError(
                        "Approving a catalogue item needs the Catalogue Publisher role."
                    )
                if acting & (rec.create_uid | rec.submitted_by):
                    raise UserError(
                        "Segregation of duties: you authored or submitted %s, so another "
                        "publisher approves it (BRU-CAT-05)." % rec.display_name
                    )
            problems = rec._completeness_problems()
            if problems:
                raise UserError(
                    "%s is no longer complete: %s." % (rec.display_name, "; ".join(problems))
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Approved and activated by %s." % self.env.user.name)
            publish(
                self.env,
                "catalogue.item_activated",
                "fix.catalogue.item",
                rec.id,
                dict(rec._payload(), approved_by_id=self.env.uid),
            )
        return True

    def _catalogue_return_to_draft(self, reason):
        for rec in self.filtered(lambda r: r.state == "in_review"):
            rec._guarded().write({"state": "draft", "rejection_reason": reason or False})
            rec.message_post(body="Returned to Draft: %s" % (reason or "recalled"))

    def _require_publisher(self, what):
        require_role(self.env, (ROLE_PUBLISHER,), what, role="Catalogue Publisher")
        if self.env.su:
            return
        for rec in self:
            if rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you authored %s; another publisher does this "
                    "(%s)." % (rec.display_name, what)
                )

    def action_publish(self):
        """Active -> Active and Published (customer-facing channel)."""
        self._require_publisher("Publishing a catalogue item")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an Active (approved) item is published.")
            if not (rec.name_bn or "").strip():
                raise UserError(
                    "%s cannot be published without a Bengali name (BRU-CAT-04)." % rec.display_name
                )
            rec._guarded().write({"state": "published", "is_published": True})
            rec.message_post(body="Published by %s." % self.env.user.name)
        return True

    def action_unpublish(self):
        self._require_publisher("Withdrawing a catalogue item from the web")
        for rec in self:
            if rec.state != "published":
                raise UserError("Only a published item is withdrawn from the web.")
            rec._guarded().write({"state": "approved", "is_published": False})
        return True

    def action_restrict(self, reason=None):
        """Active -> Restricted: new customer-facing sale blocked (BRU-CAT-14)."""
        self._require_publisher("Restricting a catalogue item")
        if not (reason or "").strip():
            raise UserError("State why the item is restricted and to whom it is still sold.")
        for rec in self:
            if rec.state not in ("approved", "published"):
                raise UserError("Only an Active item is restricted.")
            rec._guarded().write(
                {"state": "restricted", "is_published": False, "restriction_reason": reason}
            )
            rec.message_post(body="Restricted by %s: %s" % (self.env.user.name, reason))
        return True

    def action_lift_restriction(self):
        self._require_publisher("Lifting a restriction")
        for rec in self:
            if rec.state != "restricted":
                raise UserError("Only a Restricted item has a restriction to lift.")
            rec._guarded().write({"state": "approved", "restriction_reason": False})
        return True

    def action_discontinue(self, reason=None):
        """Active / Restricted -> Discontinued (BRU-CAT-09): a successor staged
        on the item, or a stated reason for having none; no new sale after."""
        self._require_publisher("Discontinuing a catalogue item")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state not in SELLABLE_STATES:
                raise UserError("Only an Active or Restricted item is discontinued.")
            successor = rec.proposed_successor_id
            if successor == rec:
                raise UserError("An item cannot succeed itself.")
            if successor and successor.state not in SELLABLE_STATES:
                raise UserError("The successor %s is not Active." % successor.display_name)
            if not successor and not (reason or "").strip():
                raise UserError(
                    "Declare a successor item (Proposed Successor) or state why there is "
                    "none (BRU-CAT-09)."
                )
            end = rec.proposed_end_of_support
            if end and end < today:
                raise UserError("The end of support cannot be in the past.")
            rec._guarded().write(
                {
                    "state": "deprecated",
                    "is_published": False,
                    "discontinued_at": today,
                    "discontinue_reason": reason or False,
                    "successor_id": successor.id or False,
                    "end_of_support_date": end or False,
                    "proposed_successor_id": False,
                    "proposed_end_of_support": False,
                }
            )
            rec.message_post(body="Discontinued by %s." % self.env.user.name)
            publish(
                self.env,
                "catalogue.item_discontinued",
                "fix.catalogue.item",
                rec.id,
                dict(
                    rec._payload(),
                    successor_id=successor.id or None,
                    end_of_support=fields.Date.to_string(end) if end else None,
                ),
            )
        return True

    def action_revise(self):
        """Active / Restricted / Discontinued -> Draft so the classification
        can change; it is sold again only once re-approved (spec §8:
        reactivation needs approval)."""
        require_role(self.env, (ROLE_OFFICER,), "Revising a catalogue item")
        for rec in self:
            if rec.state not in (*SELLABLE_STATES, "deprecated"):
                raise UserError("Only an Active, Restricted or Discontinued item is revised.")
            rec._guarded().write(
                {
                    "state": "draft",
                    "is_published": False,
                    "approved_by": False,
                    "approved_at": False,
                    "submitted_by": False,
                    "submitted_at": False,
                }
            )
            rec.message_post(body="Revised by %s; back to Draft." % self.env.user.name)
        return True

    @api.model
    def cron_obsolete_discontinued(self):
        """Discontinued -> Obsolete once the end of support has passed
        (spec §8, scheduled evaluation). Idempotent."""
        today = fields.Date.context_today(self)
        due = self.search(
            [
                ("state", "=", "deprecated"),
                ("end_of_support_date", "!=", False),
                ("end_of_support_date", "<", today),
            ]
        )
        for rec in due:
            rec._guarded().write({"state": "obsolete"})
            rec.message_post(body="End of support %s passed: Obsolete." % rec.end_of_support_date)
        return len(due)
