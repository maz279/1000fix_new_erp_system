# fix_mdm_attribute_governance — what MDM may change, and how a payload is checked.
#
# A12 finish audit (2026-11-07):
#   E2/B4: action_apply wrote ANY model and field under sudo: a plain proposer's
#   approved request made a user a Settings admin and took a BDT 5M project
#   active with no DOFA. fix.mdm.governed.attribute is now the register of what
#   a request may touch. Anything off it, any target's _fix_guarded_fields(),
#   and res.users / res.groups / ir.* are refused at entry, submit and apply.
#   E10: bank and tax attributes cannot be edited directly (BRU-MDM-01). The
#   switch is the ir.config_parameter fix.mdm.enforce_direct_edit_block.
#   E3/E4/E8: a payload is `field=value` lines or a JSON object, strictly
#   parsed, dry-run before a steward sees it, gated by every critical DQ rule,
#   and refused when the master moved after the snapshot.
import json
import logging
import re

import psycopg2
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)

DIRECT_EDIT_PARAM = "fix.mdm.enforce_direct_edit_block"
# Never governable, whatever the register says: access control and the
# technical layer are not master data.
FORBIDDEN_MODELS = frozenset({"res.users", "res.groups"})
FORBIDDEN_PREFIXES = ("ir.",)
UNGOVERNABLE_TYPES = frozenset({"one2many", "many2many", "binary", "properties", "json"})
# Lifecycle, not data: the party's status and the archive flag have their own paths.
UNGOVERNABLE_FIELDS = frozenset({"party_status", "active"})
_LINE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
_TRUE = frozenset({"1", "true", "yes", "y"})
_FALSE = frozenset({"0", "false", "no", "n"})


class _DryRun(Exception):
    """Raised to roll a dry-run write back; never leaves this module."""


def forbidden_reason(model_name):
    if model_name in FORBIDDEN_MODELS or (model_name or "").startswith(FORBIDDEN_PREFIXES):
        return (
            "%s is access control or technical configuration, not master data: "
            "a change request can never write it." % model_name
        )
    return None


class FixMdmGovernedAttribute(models.Model):
    """One master attribute that change requests may write (BRU-MDM-01)."""

    _name = "fix.mdm.governed.attribute"
    _description = "Governed Master Attribute"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "model_name, category, field_name"
    _rec_name = "name"

    _model_field_unique = models.Constraint(
        "UNIQUE (model_name, field_name)", "An attribute is registered once per model and field"
    )

    name = fields.Char(compute="_compute_name", store=True)
    model_name = fields.Char(string="Master Model", required=True, index=True, tracking=True)
    field_name = fields.Char(string="Attribute", required=True, index=True, tracking=True)
    category = fields.Selection(
        [
            ("bank", "Bank Details"),
            ("tax", "Tax Identity"),
            ("credit", "Credit Terms"),
            ("contact", "Contact"),
            ("product", "Product Master"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
        tracking=True,
    )
    block_direct_edit = fields.Boolean(
        string="Block Direct Edits",
        tracking=True,
        help="A user changing a stored value outside a change request is refused, while the "
        "parameter %s is on. Capturing a first value is still allowed." % DIRECT_EDIT_PARAM,
    )
    note = fields.Char()
    active = fields.Boolean(default=True, tracking=True)

    @api.depends("model_name", "field_name")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s.%s" % (rec.model_name, rec.field_name)

    @api.constrains("model_name", "field_name")
    def _check_attribute(self):
        for rec in self:
            reason = forbidden_reason(rec.model_name)
            if reason:
                raise ValidationError(reason)
            # Data files load before optional modules (account adds the payment
            # terms): shipped rows wait for their field, a person must be right.
            # Not env.su: the ORM runs every constraint as sudo.
            shipped = self.env.context.get("install_mode") or self.env.context.get("install_module")
            if rec.model_name not in self.env:
                if shipped:
                    continue
                raise ValidationError("Model %r does not exist." % rec.model_name)
            model = self.env[rec.model_name]
            field = model._fields.get(rec.field_name)
            if field is None:
                if shipped:
                    continue
                raise ValidationError("%s has no field %r." % (rec.model_name, rec.field_name))
            if field.type in UNGOVERNABLE_TYPES:
                raise ValidationError(
                    "%s is a %s field: only a single value can be governed."
                    % (rec.name, field.type)
                )
            if rec.field_name in UNGOVERNABLE_FIELDS | _guarded_fields(model):
                raise ValidationError(
                    "%s changes only through its workflow action: it cannot be governed "
                    "as master data." % rec.name
                )

    # ---- the register, read as the system ---------------------------------
    @api.model
    def _direct_edit_mode(self) -> str:
        """off = nothing blocked; on (default) = rows flagged Block Direct Edits,
        shipped for bank and tax; all = every governed attribute."""
        raw = self.env["ir.config_parameter"].sudo().get_param(DIRECT_EDIT_PARAM) or "on"
        value = str(raw).strip().lower()
        if value in ("0", "off", "false", "no"):
            return "off"
        return "all" if value == "all" else "on"

    @api.model
    def _rows(self, model_name, names=None):
        domain = [("model_name", "=", model_name)]
        if names is not None:
            domain.append(("field_name", "in", list(names)))
        return self.sudo().search(domain)

    @api.model
    def _assert_direct_edit_allowed(self, records, vals) -> None:
        """BRU-MDM-01. Called for non-superuser writes only: a change request
        applies under sudo, after its approval."""
        mode = self._direct_edit_mode()
        if mode == "off":
            return
        rows = self._rows(records._name, vals)
        if mode != "all":
            rows = rows.filtered("block_direct_edit")
        if not rows:
            return
        for rec in records._mdm_direct_edit_scope().sudo():
            for row in rows:
                name = row.field_name
                current = rec[name]
                # A first value is ordinary data entry, not a change of the golden one.
                if not current or not _differs(rec, name, vals[name]):
                    continue
                raise UserError(
                    "%s on %s is a governed master attribute (%s): it changes only through "
                    "an approved MDM Change Request%s."
                    % (
                        rec._fields[name].string or name,
                        rec.display_name,
                        dict(self._fields["category"].selection).get(row.category),
                        " or a bank-detail change request" if row.category == "bank" else "",
                    )
                )


def _guarded_fields(model) -> set:
    hook = getattr(model, "_fix_guarded_fields", None)
    return set(hook()) if hook else set()


def _differs(rec, name, value) -> bool:
    field = rec._fields[name]
    try:
        new = field.convert_to_record(field.convert_to_cache(value, rec), rec)
    except (ValueError, TypeError):
        return True  # unreadable: let the write say why, after the block
    if field.type == "many2one":
        return new.id != rec[name].id
    if field.type in ("float", "monetary"):
        return abs((new or 0.0) - (rec[name] or 0.0)) > 1e-6
    return (new or False) != (rec[name] or False)


class FixMdmDirectEditGuard(models.AbstractModel):
    """Mixed into each governed master that needs a direct-edit block."""

    _name = "fix.mdm.edit.guard"
    _description = "Governed Attribute Direct-Edit Block"

    def _mdm_direct_edit_scope(self):
        return self

    def write(self, vals):
        if self and not self.env.su:
            self.env["fix.mdm.governed.attribute"]._assert_direct_edit_allowed(self, vals)
        return super().write(vals)


class ResPartnerGoverned(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "fix.mdm.edit.guard"]

    def _mdm_direct_edit_scope(self):
        # A child contact's tax identity is synced from its company by Odoo:
        # the commercial entity holds the attribute.
        return self.sudo().filtered(lambda p: p.commercial_partner_id == p).with_env(self.env)


class ResPartnerBankGoverned(models.Model):
    _name = "res.partner.bank"
    _inherit = ["res.partner.bank", "fix.mdm.edit.guard"]

    def _mdm_direct_edit_scope(self):
        # A supplier's and an employee's account answer to their own guards, whose
        # refusal names the route that applies to them.
        return self.filtered(lambda bank: not bank._mdm_governed_elsewhere())

    def _mdm_governed_elsewhere(self):
        """Why a change request may not touch this account, or None. Suppliers
        and employees on the payroll have their own approved routes, whose
        guards trust the sudo an apply step runs under."""
        self.ensure_one()
        bank = self.sudo()
        if "fix.supplier" in self.env:
            partner = bank.partner_id
            if (
                self.env["fix.supplier"]
                .sudo()
                .search_count([("partner_id", "in", (partner | partner.commercial_partner_id).ids)])
            ):
                return "It belongs to a supplier: use a supplier bank-detail change request."
        employee_model = self.env["hr.employee"].sudo().with_context(active_test=False)
        if "bank_account_ids" in employee_model._fields and employee_model.search_count(
            [("bank_account_ids", "in", bank.ids)]
        ):
            return "It belongs to an employee: use an Employee Master Change."
        return None


class ProductTemplateGoverned(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "fix.mdm.edit.guard"]


class FixMdmPayloadMixin(models.AbstractModel):
    """What a change request and a steward request both do with a payload."""

    _name = "fix.mdm.payload.mixin"
    _description = "Governed Master-Data Payload"

    # ---- parsing (E3) ------------------------------------------------------
    @api.model
    def _mdm_coerce_line(self, model_name, name, raw, label):
        """A `field=value` line carries text; give the field the type it holds."""
        model = self.env.get(model_name)
        field = model._fields.get(name) if model is not None else None
        if field is None:
            return raw or False
        if raw == "":
            return False
        try:
            if field.type == "boolean":
                lowered = raw.lower()
                if lowered not in _TRUE | _FALSE:
                    raise ValueError(raw)
                return lowered in _TRUE
            if field.type in ("integer", "many2one"):
                return int(raw)
            if field.type in ("float", "monetary"):
                return float(raw)
        except ValueError as exc:
            raise ValidationError(
                "%s: %r is not a valid %s value for %s." % (label, raw, field.type, name)
            ) from exc
        if field.type in UNGOVERNABLE_TYPES:
            raise ValidationError(
                "%s: %s is a %s field and cannot take a field=value line."
                % (label, name, field.type)
            )
        return raw

    @api.model
    def _mdm_parse_payload(self, raw, model_name, label) -> dict:
        """`field=value` per line, or one JSON object. Nothing else parses."""
        text = (raw or "").strip()
        if not text:
            raise ValidationError(
                "%s proposes nothing: give one field=value per line, or a JSON object." % label
            )
        if text[0] in "{[":
            try:
                changes = json.loads(text)
            except ValueError as exc:
                raise ValidationError(
                    "Proposed changes of %s are not valid JSON: %s" % (label, exc)
                ) from exc
            if not isinstance(changes, dict) or not changes:
                raise ValidationError(
                    "%s proposes nothing: a JSON payload must be an object of "
                    "{field: new_value} pairs." % label
                )
            return changes
        changes = {}
        for number, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            match = _LINE.match(line)
            if not match:
                raise ValidationError(
                    "%s: line %d (%r) is neither field=value nor part of a JSON object."
                    % (label, number, line.strip()[:60])
                )
            name, value = match.groups()
            if name in changes:
                raise ValidationError("%s: %s is proposed twice." % (label, name))
            changes[name] = self._mdm_coerce_line(model_name, name, value, label)
        return changes

    # ---- the register (E2) -------------------------------------------------
    @api.model
    def _mdm_assert_governed(self, model_name, names, label) -> None:
        """Refuse everything off the register. An empty `names` asks whether
        the model is governed at all (a deactivation)."""
        reason = forbidden_reason(model_name)
        if reason:
            raise ValidationError("%s: %s" % (label, reason))
        if model_name not in self.env:
            raise ValidationError(
                "The target model %r does not exist in this database, so %s cannot govern it."
                % (model_name, label)
            )
        model = self.env[model_name]
        names = set(names or ())
        unknown = sorted(names - set(model._fields))
        if unknown:
            raise ValidationError(
                "%s has no field(s) %s, so %s cannot propose them."
                % (model_name, ", ".join(unknown), label)
            )
        guarded = sorted(names & _guarded_fields(model))
        if guarded:
            raise ValidationError(
                "%s changes only through its workflow action on %s: %s cannot propose it."
                % (", ".join(guarded), model_name, label)
            )
        Register = self.env["fix.mdm.governed.attribute"]
        known = set(Register._rows(model_name).mapped("field_name"))
        if not known:
            raise ValidationError(
                "%s is not on the governed-attribute register, so %s cannot change it. "
                "Change it in its own module, or have a Platform Admin register it."
                % (model_name, label)
            )
        off = sorted(names - known)
        if off:
            raise ValidationError(
                "%s on %s is not on the governed-attribute register, so %s cannot change "
                "it. Governed: %s." % (", ".join(off), model_name, label, ", ".join(sorted(known)))
            )

    @api.model
    def _mdm_assert_route(self, target, label) -> None:
        hook = getattr(target, "_mdm_governed_elsewhere", None)
        reason = hook() if hook else None
        if reason:
            raise ValidationError("%s cannot change %s. %s" % (label, target.display_name, reason))

    # ---- writing (E4) ------------------------------------------------------
    @api.model
    def _mdm_write(self, target, changes, label) -> None:
        """The sudo write, with what it can raise turned into words a steward
        can act on (a bare ValueError reads as 'contact Finance support')."""
        try:
            with self.env.cr.savepoint():
                # sudo: the steward holds the decision, not write access to the
                # governed master (BRU-MDM-01).
                target.sudo().write(changes)
                self.env.flush_all()
        except UserError:
            raise
        except (psycopg2.Error, ValueError, TypeError, KeyError) as exc:
            logger.info("MDM write refused for %s: %s", label, exc)
            diag = getattr(exc, "diag", None)
            detail = str((diag and diag.message_primary) or exc)
            raise ValidationError(
                "%s cannot be written to %s: %s" % (label, target.display_name, detail[:200])
            ) from exc

    @api.model
    def _mdm_dry_run(self, target, changes, label) -> None:
        """Would this payload write? Nothing stays, and a bad value is caught
        before a steward approves what can never apply."""
        try:
            with self.env.cr.savepoint():
                self._mdm_write(target, changes, label)
                raise _DryRun()
        except _DryRun:
            pass

    # ---- snapshot and staleness (E8) ---------------------------------------
    @api.model
    def _mdm_snapshot(self, target, names) -> str:
        target = target.sudo()
        values = {"id": target.id}
        for name in sorted(names):
            field = target._fields.get(name)
            if field is None:
                continue
            value = target[name]
            if field.type == "many2one":
                value = value.id or False
            elif field.type in ("one2many", "many2many"):
                value = sorted(value.ids)
            values[name] = value
        return json.dumps(values, default=str, sort_keys=True)

    @api.model
    def _mdm_assert_fresh(self, target, names, snapshot, label) -> None:
        """The approval covered a change FROM these values. A master that moved
        since then is not silently overwritten."""
        try:
            before = json.loads(snapshot or "{}")
        except ValueError:
            before = {}
        now = json.loads(self._mdm_snapshot(target, names))
        moved = sorted(name for name in names if name in now and before.get(name) != now[name])
        if moved:
            raise ValidationError(
                "%s on %s changed after %s was raised, or no snapshot of it was taken: "
                "applying would overwrite a value nobody reviewed. Cancel it and raise a new "
                "request." % (", ".join(moved), target.display_name, label)
            )

    # ---- the blocking DQ gate (BRU-MDM-05, E8) -----------------------------
    @api.model
    def _mdm_dq_gate(self, target, changes, company, label) -> None:
        """Every critical rule on a proposed field, for the proposed value."""
        rules = (
            self.env["fix.mdm.dq.rule"]
            .sudo()
            .search(
                [
                    ("active", "=", True),
                    ("severity", "=", "critical"),
                    ("res_model", "=", target._name),
                    ("field_name", "in", list(changes)),
                    ("company_id", "=", company.id),
                ]
            )
        )
        for rule in rules:
            value = changes[rule.field_name]
            empty = value in (None, False, "")
            refused = None
            if rule.rule_type == "completeness" and empty:
                refused = "requires a value"
            elif rule.rule_type == "format" and not empty:
                try:
                    if not re.fullmatch(rule.expression or "", str(value)):
                        refused = "rejects the proposed value %r" % (value,)
                except re.error:
                    logger.warning("DQ rule %s has an invalid expression", rule.code)
            elif rule.rule_type == "uniqueness" and not empty:
                domain = [(rule.field_name, "=", value), ("id", "!=", target.id)]
                if target.sudo().with_context(active_test=False).search_count(domain):
                    refused = "finds the proposed value %r on another record" % (value,)
            elif rule.rule_type == "range" and not empty:
                low, _, high = (rule.expression or "").partition("..")
                try:
                    number = float(value)
                    if (low.strip() and number < float(low)) or (
                        high.strip() and number > float(high)
                    ):
                        refused = "requires a value in [%s]" % rule.expression
                except (TypeError, ValueError):
                    logger.info("DQ rule %s: %r is not numeric", rule.code, value)
            if refused:
                raise ValidationError(
                    "Critical data-quality rule %s (%s on %s.%s) %s: publication is blocked (%s)."
                    % (rule.code, rule.name, rule.res_model, rule.field_name, refused, label)
                )

    # ---- every check a payload meets, before the steward and before the write
    @api.model
    def _mdm_check_payload(self, target, changes, company, label) -> None:
        self._mdm_assert_governed(target._name, changes, label)
        self._mdm_assert_route(target, label)
        self._mdm_dq_gate(target, changes, company, label)
