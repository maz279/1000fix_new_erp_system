# cd_entity_config — server-side guard for workflow-controlled fields.
#
# A03 workflow audit (2026-11-03): every approval and lifecycle control in the
# area lived in an action method, while the fields those methods protect —
# state, dofa_approved, concession_approved, points_balance, consent state —
# were writable by any internal user. `readonly=True` is a view attribute, not
# security, so a plain write() through the ORM, the web client's RPC or the
# P03 workspace's own save endpoint forged a Tier-4 approval and closed the
# record it protected.
#
# A model mixes this in and names its guarded fields. Outside a transition, a
# write that CHANGES one of them is refused; writing the value it already has
# is allowed, because the P03 form posts every field it shows on save.
# Transition methods write through `_guarded()`, which carries an in-process
# token in the context. The token is an object, not a flag: a JSON-RPC caller
# can put any key it likes in the context, but it cannot put this object there.
from odoo import api, models
from odoo.exceptions import UserError

GUARD_KEY = "fix_guarded_transition"
_TOKEN = object()


class FixGuardedMixin(models.AbstractModel):
    """Refuses direct changes to fields that only a transition may set."""

    _name = "fix.guarded.mixin"
    _description = "Workflow-Controlled Field Guard"

    def _fix_guarded_fields(self) -> set:
        """Field names only a transition method may change. Extend with super()."""
        return set()

    def _fix_form_locked_fields(self) -> set:
        """Fields a form must show read-only for THIS record (empty set = new).

        The guarded fields, plus whatever a model freezes once a record
        reaches a state: a posted ledger line, a sent message, a captured
        consent. The P03 form endpoint reads this, so the screen offers an
        input only where the server will accept a change. Extend with super()."""
        return self._fix_guarded_fields()

    def _guarded(self):
        """This recordset, allowed to write its guarded fields."""
        return self.with_context(**{GUARD_KEY: _TOKEN})

    def _fix_guard_has_token(self) -> bool:
        """True only inside a transition that obtained the token."""
        return self.env.context.get(GUARD_KEY) is _TOKEN

    def _fix_guard_open(self) -> bool:
        # Superuser code (crons, data loading, seeds, sudo() service calls) is
        # trusted; so is a transition that obtained the token.
        return self.env.su or self._fix_guard_has_token()

    def _fix_guard_refuse(self, names):
        labels = ", ".join(sorted(self._fields[n].string or n for n in names if n in self._fields))
        raise UserError(
            "%s cannot be set directly on %s. It changes only through its workflow "
            "action (approve, launch, post, close…), which applies the approval "
            "and segregation-of-duties checks." % (labels, self._description)
        )

    def _fix_guard_differs(self, name, value, current) -> bool:
        field = self._fields[name]
        try:
            if field.type in ("many2one", "one2many", "many2many"):
                new = field.convert_to_record(field.convert_to_cache(value, self), self)
                return set(new.ids) != set(current.ids if current else [])
            new = field.convert_to_record(field.convert_to_cache(value, self), self)
        except Exception:
            return True
        if field.type in ("float", "monetary"):
            return abs((new or 0.0) - (current or 0.0)) > 1e-6
        return (new or False) != (current or False)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            guarded = self._fix_guarded_fields()
            touched = guarded & {k for vals in vals_list for k in vals}
            if touched:
                defaults = self.default_get(list(touched))
                empty = self.browse()
                for vals in vals_list:
                    changed = [
                        name
                        for name in touched & set(vals)
                        if empty._fix_guard_differs(
                            name,
                            vals[name],
                            empty._fields[name].convert_to_record(
                                empty._fields[name].convert_to_cache(defaults.get(name), empty),
                                empty,
                            ),
                        )
                    ]
                    if changed:
                        self._fix_guard_refuse(changed)
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            touched = self._fix_guarded_fields() & set(vals)
            if touched:
                changed = {
                    name
                    for rec in self
                    for name in touched
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                }
                if changed:
                    self._fix_guard_refuse(changed)
        return super().write(vals)
