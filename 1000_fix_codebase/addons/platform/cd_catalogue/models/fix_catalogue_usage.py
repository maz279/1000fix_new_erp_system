# A04 ERP audit round 2 (21 Nov 2026): how the rest of the estate USES a
# catalogue item (M37-F5/F7/F11).
#
# - FR-CAT-046 / AUT-CAT-03: before a lifecycle change (restrict, discontinue,
#   revise) the officer sees which rate cards, contracts, quotations, open
#   orders, listings and subscriptions reference the item. The change is
#   refused until that impact was previewed today and is still what it was.
# - FR-CAT-007: item codes from a configurable, type-aware mask (an ir.sequence
#   with no gaps), never reused; an old code stays searchable as an alias.
# - FR-CAT-015: the skill band and brand certification a technician needs
#   (the M22 competency is cd_competency's required_competency_id); dispatch
#   gating in M02 / M31 reads _fix_technician_requirements / _qualified.
# - FR-CAT-018 (M37-F5): the item's repair warranty reaches M01.
# - FR-CAT-031 / BRU-CAT-08 (M37-F7): a discontinued item offers its live
#   successor at the point of sale.
# - FR-CAT-024 / AUT-PRC-09: an applied SRT re-baseline publishes
#   catalogue.srt_rebaselined, and its effect on a labour price is held until
#   M11 has reviewed it (price_effect).
#
# File name sorts after fix_catalogue_structure and fix_catalogue_spec_records
# (ruff I001), whose models it extends.
import hashlib
import json
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .catalogue_roles import ROLE_OFFICER, ROLE_PUBLISHER, require_role
from .fix_catalogue_item import ITEM_STATES

_logger = logging.getLogger(__name__)

# FR-CAT-015 / FR-PRC-012: the skill band of the technician a service needs,
# and the band an M11 labour rate is priced at. Structural classes the owner
# confirms; no rate or figure lives here.
SKILL_BANDS = [
    ("standard", "Standard technician"),
    ("senior", "Senior technician"),
    ("specialist", "Specialist / brand-certified"),
]
SKILL_ORDER = {key: n for n, (key, _label) in enumerate(SKILL_BANDS)}
LEVEL_ORDER = {"l1": 0, "l2": 1, "l3": 2, "l4": 3}

# FR-CAT-046: the groups the impact preview speaks of, by model name prefix.
IMPACT_GROUPS = (
    ("Rate cards", ("fix.rate.card", "fix.price.")),
    ("Contracts", ("fix.contract",)),
    ("Quotations", ("fix.quotation", "fix.tender")),
    ("Listings", ("fix.marketplace", "fix.storefront.listing")),
    ("Subscriptions", ("fix.subscription",)),
    (
        "Open orders",
        (
            "fix.service.order",
            "fix.estimate",
            "fix.storefront.order",
            "fix.stock.requisition",
            "fix.purchase",
        ),
    ),
)
# Product references are counted only on these document models: a stock
# ledger or a price history is not an open commitment.
IMPACT_PRODUCT_MODELS = (
    "fix.quotation.line",
    "fix.estimate.line",
    "fix.storefront.order.line",
    "fix.marketplace.listing",
    "fix.subscription.line",
)
# A record in one of these states no longer commits the business to the item.
CLOSED_DOC_STATES = frozenset(
    {
        "done",
        "cancel",
        "cancelled",
        "closed",
        "rejected",
        "declined",
        "expired",
        "retired",
        "lost",
        "delivered",
        "invoiced",
        "paid",
        "churned",
        "terminated",
        "superseded",
        "converted",
        "completed",
        "settled",
        "refunded",
        "obsolete",
        "consumed",
    }
)
# The item's own definition (its delivery modes, standard times, fit, its
# own repair BOM, cross-references) and M11's own tasks and what-ifs are
# not documents that commit the business to it.
IMPACT_IGNORED = frozenset(
    {
        ("fix.service.mode.duration", "item_id"),
        ("fix.srt.baseline", "item_id"),
        ("fix.model.compatibility", "item_id"),
        ("fix.part.crossref", "part_item_id"),
        ("fix.rbom.line", "item_id"),
        ("fix.price.review", "catalogue_item_id"),
        ("fix.price.review", "successor_item_id"),
        ("fix.price.simulation", "catalogue_item_id"),
    }
)
PARENT_FIELDS = ("quotation_id", "estimate_id", "order_id", "subscription_id", "contract_id")
IMPACT_FIELDS = frozenset(
    {"impact_summary", "impact_hash", "impact_previewed_at", "impact_previewed_by"}
)


class FixCatalogueItemUsage(models.Model):
    _inherit = "fix.catalogue.item"
    _rec_names_search = ["name", "product_tmpl_id.default_code", "legacy_codes"]

    # ---- FR-CAT-007 ------------------------------------------------------
    legacy_codes = fields.Char(
        string="Legacy Codes (aliases)",
        index=True,
        copy=False,
        help="Earlier codes of this item, comma-separated. Searchable for ever, never "
        "issued to another item (FR-CAT-007).",
    )
    # ---- FR-CAT-015 ------------------------------------------------------
    required_skill_band = fields.Selection(
        SKILL_BANDS,
        string="Required Skill Band",
        tracking=True,
        help="The technician skill band the service needs (dispatch gating, M02 / M31).",
    )
    requires_brand_certification = fields.Boolean(
        string="Needs a Brand-Certified Technician",
        tracking=True,
        help="Only a technician certified by the item's brand performs it.",
    )
    # ---- FR-CAT-046 ------------------------------------------------------
    impact_summary = fields.Text(string="Impact Preview", readonly=True, copy=False)
    impact_hash = fields.Char(readonly=True, copy=False)
    impact_previewed_at = fields.Datetime(readonly=True, copy=False)
    impact_previewed_by = fields.Many2one("res.users", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(IMPACT_FIELDS)

    # ---- FR-CAT-007: numbering --------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        Numbering = self.env["fix.catalogue.numbering"].sudo()
        for rec in records:
            tmpl = rec.product_tmpl_id.sudo()
            if (tmpl.default_code or "").strip():
                continue
            rule = Numbering._rule_for(rec.item_type, rec.company_id)
            if rule:
                tmpl.write({"default_code": rule._next_code()})
        return records

    @api.model
    def _code_taken(self, code, exclude=None):
        """Whether `code` is any other item's code or legacy alias (FR-CAT-007:
        a code is never reused)."""
        code = (code or "").strip()
        if not code:
            return False
        Item = self.sudo().with_context(active_test=False)
        domain = [("product_tmpl_id.default_code", "=ilike", code)]
        if exclude:
            domain.append(("id", "not in", exclude.ids))
        if Item.search_count(domain):
            return True
        for rec in Item.search([("legacy_codes", "ilike", code)]):
            if exclude and rec in exclude:
                continue
            if code.lower() in rec._legacy_list():
                return True
        Product = self.env["product.template"].sudo().with_context(active_test=False)
        others = Product.search_count(
            [("default_code", "=ilike", code), ("catalogue_item_id", "=", False)]
        )
        return bool(others)

    def _legacy_list(self):
        self.ensure_one()
        return [c.strip().lower() for c in (self.legacy_codes or "").split(",") if c.strip()]

    def action_assign_code(self):
        """Give a Draft item its code from the type's numbering mask; the code
        it had becomes a searchable alias. A decided item keeps its code: rate
        cards and documents print it."""
        require_role(self.env, (ROLE_OFFICER,), "Numbering a catalogue item")
        Numbering = self.env["fix.catalogue.numbering"].sudo()
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "%s is %s: its code is on its rate cards and documents and is not "
                    "renumbered." % (rec.display_name, dict(ITEM_STATES)[rec.state])
                )
            rule = Numbering._rule_for(rec.item_type, rec.company_id)
            if not rule:
                raise UserError(
                    "No numbering rule is set for %s items: a Catalogue Publisher defines "
                    "the mask first (FR-CAT-007)." % rec.item_type
                )
            tmpl = rec.product_tmpl_id.sudo()
            old = (tmpl.default_code or "").strip()
            code = rule._next_code()
            legacy = rec._legacy_list()
            if old and old.lower() not in legacy:
                aliases = [c.strip() for c in (rec.legacy_codes or "").split(",") if c.strip()]
                rec.sudo().write({"legacy_codes": ", ".join([*aliases, old])})
            tmpl.write({"default_code": code})
            rec.message_post(body="Code %s issued (was %s)." % (code, old or "none"))
        return True

    def _completeness_problems(self):
        problems = super()._completeness_problems()
        code = (self.product_tmpl_id.default_code or "").strip()
        if code:
            others = (
                self.sudo()
                .with_context(active_test=False)
                .search([("id", "!=", self.id), ("legacy_codes", "ilike", code)])
            )
            if any(code.lower() in o._legacy_list() for o in others):
                problems.append(
                    "a code never used before: '%s' is a legacy code of another item "
                    "(FR-CAT-007)" % code
                )
        return problems

    # ---- FR-CAT-015 -------------------------------------------------------
    def _fix_technician_requirements(self):
        """What a technician needs to perform this item (FR-CAT-015), for the
        dispatch gate of M02 / M31: {repair_level, skill_band, competency_id
        (M22, when cd_competency is installed), certified (a valid
        certification of it), brand_id, brand_certification}."""
        self.ensure_one()
        item = self.sudo()
        competency = (
            item["required_competency_id"] if "required_competency_id" in item._fields else None
        )
        return {
            "repair_level": item.repair_level or False,
            "skill_band": item.required_skill_band or False,
            "competency_id": competency.id if competency else False,
            "certified": bool(item["requires_certification"])
            if "requires_certification" in item._fields
            else False,
            "brand_id": item.brand_id.id or False,
            "brand_certification": bool(item.requires_brand_certification),
        }

    def _fix_technician_qualified(self, employee, on_date=None, skill_band=None):
        """(ok, [reasons]) for `employee` (hr.employee) performing this item:
        a valid, unexpired M22 certification of the required competency (when
        the item asks for a certified technician), of the item's brand (when
        it needs a brand-certified technician), at the item's repair level or
        above; and the skill band when the caller knows the technician's band.
        Without M22 installed no certification is checked here."""
        self.ensure_one()
        req = self._fix_technician_requirements()
        reasons = []
        day = on_date or fields.Date.context_today(self)
        if (
            req["skill_band"]
            and skill_band is not None
            and SKILL_ORDER.get(skill_band or "", -1) < SKILL_ORDER[req["skill_band"]]
        ):
            reasons.append("the %s skill band" % dict(SKILL_BANDS)[req["skill_band"]])
        Cert = self.env.get("fix.certification")
        needs_cert = (req["certified"] and req["competency_id"]) or req["brand_certification"]
        if Cert is None or not needs_cert:
            return (not reasons, reasons)
        certs = Cert.sudo().search([("employee_id", "=", employee.id), ("state", "=", "valid")])
        certs = certs.filtered(
            lambda c: (not c.expires_on or c.expires_on >= day)
            and (not c.issued_on or c.issued_on <= day)
        )
        if req["certified"] and req["competency_id"]:
            certs = certs.filtered(lambda c: c.competency_id.id == req["competency_id"])
            if not certs:
                reasons.append("a valid certification of the required competency")
        if req["brand_certification"]:
            certs = certs.filtered(lambda c: c.brand_id.id == req["brand_id"])
            if not certs:
                reasons.append("a certification of %s" % (self.brand_id.name or "its brand"))
        if req["repair_level"] and certs:
            need = LEVEL_ORDER.get(req["repair_level"], 0)
            if not certs.filtered(
                lambda c: not c.repair_tier or LEVEL_ORDER.get(c.repair_tier, 0) >= need
            ):
                reasons.append("repair level %s" % req["repair_level"].upper())
        return (not reasons, reasons)

    # ---- FR-CAT-018 (M37-F5) ----------------------------------------------
    def _fix_repair_warranty_days(self, policy_days=0):
        """The repair warranty M01 issues for this service: the item's own
        warranty (FR-CAT-018) where it is longer than the company policy,
        else the policy (owner decision 20 Nov 2026: 90 days on every repair
        is the minimum)."""
        days = int(policy_days or 0)
        for item in self.sudo():
            days = max(days, int(item.repair_warranty_days or 0))
        return days

    # ---- FR-CAT-031 (M37-F7) ----------------------------------------------
    def _fix_sale_substitute(self, channel=None):
        """The item to offer in place of this one when this one no longer
        sells: the first sellable item down its successor chain, or empty."""
        self.ensure_one()
        item = self.sudo()
        if not item._sale_refusal(channel) or not item.successor_id:
            return self.browse()
        live = item.successor_id._fix_live_successor()
        if live and not live._sale_refusal(channel):
            return self.browse(live.id)
        return self.browse()

    # ---- FR-CAT-046: impact preview ---------------------------------------
    def _fix_impact_refs(self):
        """[(group label, recordset)] of what references this item and still
        commits the business to it. Extended by cd_rate_card (cards keyed by
        code, the contracts of contract rates)."""
        self.ensure_one()
        out = []
        Fields = self.env["ir.model.fields"].sudo()
        variants = self.sudo().product_tmpl_id.with_context(active_test=False).product_variant_ids
        targets = [
            (self._name, self.id, None),
            ("product.template", self.product_tmpl_id.id, IMPACT_PRODUCT_MODELS),
            ("product.product", variants.ids, IMPACT_PRODUCT_MODELS),
        ]
        for relation, ids, only in targets:
            if not ids:
                continue
            ids = ids if isinstance(ids, list) else [ids]
            domain = [("relation", "=", relation), ("ttype", "=", "many2one"), ("store", "=", True)]
            for field in Fields.search(domain):
                if only and field.model not in only:
                    continue
                if field.model.startswith("fix.catalogue.") or field.model == "product.product":
                    continue
                if (field.model, field.name) in IMPACT_IGNORED:
                    continue
                Model = self.env.get(field.model)
                if Model is None or Model._abstract or not Model._auto:
                    continue
                if field.name not in Model._fields or not Model._fields[field.name].store:
                    continue
                recs = (
                    Model.sudo().with_context(active_test=False).search([(field.name, "in", ids)])
                )
                recs = recs.filtered(self._impact_is_open)
                if recs:
                    out.append((self._impact_group(field.model), recs))
        return out

    @api.model
    def _impact_group(self, model_name):
        for label, prefixes in IMPACT_GROUPS:
            if model_name.startswith(prefixes):
                return label
        return "Other references"

    @api.model
    def _impact_is_open(self, rec):
        """A record that still commits the business: not archived, not in a
        closed state (its own, or its parent document's)."""
        if "active" in rec._fields and not rec.active:
            return False
        if "state" in rec._fields and rec.state:
            return rec.state not in CLOSED_DOC_STATES
        for name in PARENT_FIELDS:
            if name in rec._fields and rec[name] and "state" in rec[name]._fields:
                return rec[name].state not in CLOSED_DOC_STATES
        return True

    def _fix_impact_preview(self):
        """{groups: [{label, count, records: [names]}], total, hash}."""
        self.ensure_one()
        groups, keys = {}, set()
        for label, recs in self._fix_impact_refs():
            bucket = groups.setdefault(label, {})
            for rec in recs:
                key = (rec._name, rec.id)
                if key in keys:
                    continue
                keys.add(key)
                bucket[key] = rec.display_name or "%s #%d" % (rec._name, rec.id)
        rows = [
            {"label": label, "count": len(bucket), "records": sorted(bucket.values())[:10]}
            for label, bucket in sorted(groups.items())
        ]
        digest = hashlib.sha256(json.dumps(sorted(keys)).encode()).hexdigest()
        return {"groups": rows, "total": len(keys), "hash": digest}

    def action_preview_impact(self):
        """Show (and record) what a lifecycle change of the item affects."""
        require_role(self.env, (ROLE_OFFICER, ROLE_PUBLISHER), "Previewing an item's impact")
        for rec in self:
            impact = rec._fix_impact_preview()
            if impact["total"]:
                lines = [
                    "%s: %d (%s%s)"
                    % (
                        g["label"],
                        g["count"],
                        ", ".join(g["records"]),
                        ", …" if g["count"] > len(g["records"]) else "",
                    )
                    for g in impact["groups"]
                ]
                text = "\n".join(lines)
            else:
                text = "Nothing references this item."
            rec._guarded().write(
                {
                    "impact_summary": text,
                    "impact_hash": impact["hash"],
                    "impact_previewed_at": fields.Datetime.now(),
                    "impact_previewed_by": self.env.uid,
                }
            )
            rec.message_post(body="Impact previewed by %s:\n%s" % (self.env.user.name, text))
        return True

    def _assert_impact_previewed(self, what):
        """AUT-CAT-03: a lifecycle change of an item something references is
        committed only after its impact was previewed today and is still the
        same set (block the commit otherwise)."""
        today = fields.Date.context_today(self)
        for rec in self:
            impact = rec._fix_impact_preview()
            if not impact["total"]:
                continue
            seen = rec.impact_previewed_at
            seen_day = fields.Date.context_today(rec, seen) if seen else None
            if not seen or seen_day != today:
                raise UserError(
                    "%s is referenced by %d open record(s). Preview the impact first "
                    "(FR-CAT-046), then %s." % (rec.display_name, impact["total"], what)
                )
            if rec.impact_hash != impact["hash"]:
                raise UserError(
                    "What references %s changed since the impact was previewed. Preview it "
                    "again, then %s." % (rec.display_name, what)
                )

    def _clear_impact(self):
        self._guarded().write(dict.fromkeys(IMPACT_FIELDS, False))

    def action_discontinue(self, reason=None):
        self._assert_impact_previewed("discontinue it")
        result = super().action_discontinue(reason=reason)
        self._clear_impact()
        return result

    def action_restrict(self, reason=None):
        self._assert_impact_previewed("restrict it")
        result = super().action_restrict(reason=reason)
        self._clear_impact()
        return result

    def action_revise(self):
        self._assert_impact_previewed("revise it")
        result = super().action_revise()
        self._clear_impact()
        return result


class FixCatalogueNumbering(models.Model):
    """FR-CAT-007: the code mask of one item type. Codes come from a no-gap
    ir.sequence; the mask is the owner's (no default mask is seeded)."""

    _name = "fix.catalogue.numbering"
    _description = "Catalogue Item Numbering Rule"
    _inherit = ["mail.thread"]
    _order = "item_type"
    _rec_name = "item_type"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    item_type = fields.Selection(
        selection=lambda self: self.env["fix.catalogue.item"]._fields["item_type"].selection,
        required=True,
        tracking=True,
    )
    prefix = fields.Char(
        required=True,
        tracking=True,
        help="The fixed part of the code, e.g. SRV- or PRT-%(year)s- (ir.sequence placeholders "
        "allowed).",
    )
    padding = fields.Integer(required=True, default=6, tracking=True)
    sequence_id = fields.Many2one("ir.sequence", readonly=True, copy=False, ondelete="restrict")
    next_code = fields.Char(string="Next Code", compute="_compute_next_code")
    active = fields.Boolean(default=True, tracking=True)

    _type_unique = models.Constraint(
        "UNIQUE (company_id, item_type)", "One numbering rule per item type and company"
    )

    @api.constrains("padding", "prefix")
    def _check_mask(self):
        for rec in self:
            if not 3 <= rec.padding <= 12:
                raise ValidationError("A code number has 3 to 12 digits.")
            if not (rec.prefix or "").strip():
                raise ValidationError("A numbering mask needs a prefix.")

    @api.depends("sequence_id", "prefix", "padding")
    def _compute_next_code(self):
        for rec in self:
            seq = rec.sudo().sequence_id
            if not seq:
                rec.next_code = False
                continue
            try:
                prefix, suffix = seq._get_prefix_suffix()
            except (KeyError, ValueError, UserError):
                prefix, suffix = seq.prefix or "", seq.suffix or ""
            rec.next_code = "%s%s%s" % (
                prefix,
                str(seq.number_next_actual).zfill(seq.padding),
                suffix,
            )

    def _sequence_vals(self):
        self.ensure_one()
        return {
            "name": "M37 item code: %s (%s)" % (self.item_type, self.company_id.name),
            "code": "fix.catalogue.item.%s.%d" % (self.item_type, self.company_id.id),
            "prefix": self.prefix,
            "padding": self.padding,
            "implementation": "no_gap",
            "company_id": self.company_id.id,
            "number_increment": 1,
        }

    @api.model_create_multi
    def create(self, vals_list):
        require_role(
            self.env,
            (ROLE_PUBLISHER,),
            "Defining an item numbering rule",
            role="Catalogue Publisher",
        )
        records = super().create(vals_list)
        for rec in records:
            seq = self.env["ir.sequence"].sudo().create(rec._sequence_vals())
            rec.sudo().write({"sequence_id": seq.id})
        return records

    def write(self, vals):
        require_role(
            self.env,
            (ROLE_PUBLISHER,),
            "Changing an item numbering rule",
            role="Catalogue Publisher",
        )
        if {"item_type", "company_id"} & set(vals) and not self.env.su:
            raise UserError("A numbering rule keeps its item type; define a new rule instead.")
        res = super().write(vals)
        if {"prefix", "padding"} & set(vals):
            for rec in self.filtered("sequence_id"):
                rec.sequence_id.sudo().write({"prefix": rec.prefix, "padding": rec.padding})
        return res

    def unlink(self):
        raise UserError("A numbering rule is archived, never deleted: its codes were issued.")

    @api.model
    def _rule_for(self, item_type, company=None):
        company = company or self.env.company
        return self.sudo().search(
            [("item_type", "=", item_type), ("company_id", "=", company.id), ("active", "=", True)],
            limit=1,
        )

    def _next_code(self):
        """The next free code of the mask: a number the sequence issues is
        skipped only when that code already belongs to an item or alias
        (a code is never reused)."""
        self.ensure_one()
        Item = self.env["fix.catalogue.item"]
        for _attempt in range(100):
            code = self.sudo().sequence_id.next_by_id()
            if not Item._code_taken(code):
                return code
            _logger.warning("M37 numbering: %s is already used; the next number is taken.", code)
        raise UserError("No free code after 100 attempts: the mask collides with existing codes.")


class FixSrtBaselinePricing(models.Model):
    """AUT-PRC-09: an applied re-baseline moves no labour price until M11 has
    reviewed it. price_effect 'held' = M11 prices at the previous time."""

    _inherit = "fix.srt.baseline"

    price_effect = fields.Selection(
        [
            ("none", "No price effect (first baseline)"),
            ("held", "Held for M11 pricing review"),
            ("released", "Released to pricing"),
        ],
        string="Price Effect",
        default="none",
        readonly=True,
        copy=False,
        index=True,
        help="A re-baselined standard time moves an M11 labour price only after the "
        "pricing review accepts it (AUT-PRC-09).",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"price_effect"}

    def _apply(self):
        pending = self.filtered(lambda r: r.state == "approved" and not r.applied_at)
        result = super()._apply()
        for rec in pending.filtered("applied_at"):
            old = rec._previous_minutes()
            held = bool(old) and abs(old - rec.minutes) > 1e-6
            rec._guarded().write({"price_effect": "held" if held else "none"})
            publish(
                self.env,
                "catalogue.srt_rebaselined",
                "fix.srt.baseline",
                rec.id,
                {
                    "item_id": rec.item_id.id,
                    "device_model_id": rec.device_model_id.id or None,
                    "repair_level": rec.repair_level,
                    "old_minutes": old,
                    "new_minutes": rec.minutes,
                    "effective_from": fields.Date.to_string(rec.effective_from),
                    "price_effect": "held" if held else "none",
                },
            )
        return result

    def _previous_minutes(self):
        """The standard time this baseline replaced: the last applied baseline
        of the same item, model and level, else the time recorded when it was
        proposed."""
        self.ensure_one()
        prior = self.sudo().search(
            [
                ("id", "!=", self.id),
                ("item_id", "=", self.item_id.id),
                ("device_model_id", "=", self.device_model_id.id or False),
                ("repair_level", "=", self.repair_level),
                ("applied_at", "!=", False),
                ("state", "in", ("approved", "superseded")),
            ],
            order="effective_from desc, id desc",
            limit=1,
        )
        return float(prior.minutes if prior else (self.previous_minutes or 0.0))

    def _release_price_effect(self):
        self.filtered(lambda r: r.price_effect == "held")._guarded().write(
            {"price_effect": "released"}
        )
