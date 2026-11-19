# fix_msp_a02_controls — A02 ERP audit (2026-11-19), builder stream B1, M05.
#
#   M05-F3  the contract's SLA and commercial terms (target, resolution hours,
#           coverage window, holiday calendar, per-device price, covered
#           devices, the M08 contract) and its lifecycle stamps were plain
#           fields an engineer edited, so an engineer could lower the target
#           or the price of a live contract and with it the SLA credit owed.
#           They are now guarded: typed once when the contract is created (the
#           commercial ones by a commercial approver), and changed afterwards
#           only through action_amend_terms by an SLA credit approver, with a
#           reason, on the record's chatter. The lifecycle stamps change only
#           through the offboarding / go-live actions.
#   M05-F4  raising the covered devices publishes msp.device_uplift, the
#           event the recurring billing (M39 subscription) consumes to bill
#           the uplift.
#   M05-F14 an SLA credit names its report: the report must be the credit's
#           own contract and period, and a credit drafted from a report keeps
#           both.
#
# FILE NAME IS LOAD-BEARING: imported last in models/__init__.py.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .msp_roles import GROUP_CREDIT_APPROVER, require_role

# the terms the SLA credit and the bill are computed from
MSP_TERMS = (
    "contract_id",
    "device_count",
    "per_device_monthly",
    "sla_target_pct",
    "alert_resolve_hours_major",
    "alert_resolve_hours_minor",
    "coverage_window",
    "holiday_calendar_id",
    "unattended_access",
    "recording_retention_days",
)
# set at creation by a commercial approver only (the M08 contract is the
# engineer's to name)
MSP_COMMERCIAL_TERMS = tuple(t for t in MSP_TERMS if t != "contract_id")
# written only by the onboarding / offboarding actions
MSP_LIFECYCLE = (
    "lifecycle",
    "offboarding_started_at",
    "access_revoked_at",
    "access_revoked_evidence",
    "offboarded_at",
    "offboarded_by_id",
    "service_live_at",
    "data_returned_at",
    "data_return_evidence",
    "terms_amended_at",
    "terms_amended_by_id",
)
REASON_MIN = 10
_TRUE = ("1", "true", "yes", "y", "on")
_FALSE = ("0", "false", "no", "n", "off", "")


class FixMspContractGuard(models.Model):
    _name = "fix.msp.contract"
    _inherit = ["fix.msp.contract", "fix.guarded.mixin"]

    terms_amended_at = fields.Datetime(string="Terms Last Amended At", readonly=True, copy=False)
    terms_amended_by_id = fields.Many2one(
        "res.users", string="Terms Last Amended By", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(MSP_TERMS) | set(MSP_LIFECYCLE)

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if not self:
            # typed once, on the new contract; a saved contract locks them
            locked -= set(MSP_TERMS)
        return locked

    def _msp_typed(self, vals, names):
        """The names in ``vals`` whose value differs from the field default."""
        empty = self.browse()
        defaults = self.default_get([n for n in names if n in vals])
        typed = []
        for name in names:
            if name not in vals:
                continue
            field = empty._fields[name]
            default = field.convert_to_record(
                field.convert_to_cache(defaults.get(name), empty), empty
            )
            if empty._fix_guard_differs(name, vals[name], default):
                typed.append(name)
        return typed

    @api.model_create_multi
    def create(self, vals_list):
        if self._fix_guard_open():
            return super().create(vals_list)
        for vals in vals_list:
            stamps = self._msp_typed(vals, MSP_LIFECYCLE)
            if stamps:
                self._fix_guard_refuse(stamps)
            commercial = self._msp_typed(vals, MSP_COMMERCIAL_TERMS)
            if commercial:
                require_role(
                    self.env,
                    [GROUP_CREDIT_APPROVER],
                    "Setting an MSP contract's commercial terms (%s)"
                    % ", ".join(self._fields[n].string for n in commercial),
                )
        # the terms are typed once, here: through the guard
        records = super(FixMspContractGuard, self._guarded()).create(vals_list)
        return records.with_env(self.env)

    # ---- the controlled change of terms (M05-F3) ---------------------------
    def _msp_term_value(self, name, raw):
        """``raw`` (typed in a prompt, or sent by a form) as the field's value."""
        field = self._fields[name]
        text = raw.strip() if isinstance(raw, str) else raw
        try:
            if field.type == "integer":
                value = int(float(text))
            elif field.type in ("float", "monetary"):
                value = float(text)
            elif field.type == "boolean":
                if isinstance(text, bool):
                    value = text
                elif str(text).lower() in _TRUE:
                    value = True
                elif str(text).lower() in _FALSE:
                    value = False
                else:
                    raise ValueError(text)
            elif field.type == "selection":
                keys = [k for k, _l in field._description_selection(self.env)]
                if text not in keys:
                    raise UserError("%s is one of: %s." % (field.string, ", ".join(keys)))
                value = text
            elif field.type == "many2one":
                if text in (None, False, "", 0, "0"):
                    value = False
                else:
                    record = self.env[field.comodel_name].sudo().browse(int(text)).exists()
                    if not record:
                        raise UserError("No %s #%s." % (field.string, text))
                    value = record.id
            else:
                value = text
        except (TypeError, ValueError):
            raise UserError("'%s' is not a valid %s." % (raw, field.string)) from None
        if field.type in ("integer", "float", "monetary") and value < 0:
            raise UserError("%s cannot be negative." % field.string)
        if name == "sla_target_pct" and not 0 < value <= 100:
            raise UserError("The SLA target is a percentage above 0 and at most 100.")
        if name in ("alert_resolve_hours_major", "alert_resolve_hours_minor") and value <= 0:
            raise UserError("%s must be more than 0 hours." % field.string)
        return value

    def action_amend_terms(self, term=None, value=None, reason=None, **terms):
        """Change the contract's SLA or commercial terms: an SLA credit
        approver (the commercial role), with the reason, recorded on the
        contract. ``term`` / ``value`` take one term from the workspace
        prompt; keyword arguments take several."""
        require_role(
            self.env, [GROUP_CREDIT_APPROVER], "Amending an MSP contract's SLA or commercial terms"
        )
        reason = (reason or "").strip()
        if len(reason) < REASON_MIN:
            raise UserError(
                "Give the reason for the change (at least %d characters): the contract "
                "amendment or the client's agreement it follows." % REASON_MIN
            )
        terms = dict(terms)
        if term:
            terms[str(term).strip()] = value
        if not terms:
            raise UserError("Name the term to change and its new value.")
        unknown = sorted(set(terms) - set(MSP_TERMS))
        if unknown:
            raise UserError(
                "%s cannot be amended here. The amendable terms are: %s."
                % (", ".join(unknown), ", ".join(MSP_TERMS))
            )
        for msp in self:
            msp._msp_assert_in_service("Amending the contract terms")
            vals = {name: msp._msp_term_value(name, raw) for name, raw in terms.items()}
            changed = {n: v for n, v in vals.items() if msp._fix_guard_differs(n, v, msp[n])}
            if not changed:
                raise UserError("The terms of %s already are what you entered." % msp.name)
            if "contract_id" in changed:
                new = self.env["fix.contract"].sudo().browse(changed["contract_id"])
                old_customer = msp.contract_id.sudo().customer_id.commercial_partner_id
                if not new or new.customer_id.commercial_partner_id != old_customer:
                    raise UserError(
                        "An MSP contract moves only to an M08 contract of the same customer."
                    )
            before = {n: msp[n] for n in changed}
            old_count = msp.device_count
            msp.sudo()._guarded().write(
                dict(
                    changed,
                    terms_amended_at=fields.Datetime.now(),
                    terms_amended_by_id=self.env.uid,
                )
            )

            def show(value):
                if isinstance(value, models.BaseModel):
                    return value.display_name or "-"
                return "-" if value in (False, None) else value

            msp.message_post(
                body="Terms amended by %s (%s): %s"
                % (
                    self.env.user.name,
                    reason,
                    "; ".join(
                        "%s %s -> %s" % (msp._fields[n].string, show(before[n]), show(msp[n]))
                        for n in sorted(changed)
                    ),
                )
            )
            if "device_count" in changed and msp.device_count > old_count:
                msp._msp_publish_uplift(old_count, reason)
        return True

    def _msp_publish_uplift(self, old_count, reason):
        """BRU-RMS-07 / A02 ERP audit M05-F4: devices beyond the contracted
        count are billed, never absorbed. The uplift goes to billing as an
        event: the recurring MSP charge is the M39 subscription's, which
        consumes it (the per-device price and the added devices)."""
        self.ensure_one()
        contract = self.contract_id.sudo()
        partner = contract.customer_id.commercial_partner_id or contract.customer_id
        added = self.device_count - (old_count or 0)
        publish(
            self.env,
            "msp.device_uplift",
            "fix.msp.contract",
            self.id,
            {
                "msp_contract": self.name,
                "msp_contract_id": self.id,
                "contract_id": contract.id,
                "contract_code": contract.code or "",
                "partner_id": partner.id,
                "company_id": self.company_id.id,
                "old_device_count": old_count or 0,
                "new_device_count": self.device_count,
                "added_devices": added,
                "per_device_monthly": self.per_device_monthly,
                "monthly_increase": round(added * (self.per_device_monthly or 0.0), 2),
                "currency": self.currency_id.name or "BDT",
                "effective_date": fields.Date.to_string(fields.Date.context_today(self)),
                "reason": reason,
            },
        )


class FixMspSlaCreditReport(models.Model):
    _inherit = "fix.msp.sla.credit"

    def _msp_frozen_fields(self) -> set:
        frozen = super()._msp_frozen_fields()
        if self.service_report_id:
            # computed from this report: the contract and period are its own
            frozen |= {"msp_contract_id", "period_label"}
        return frozen

    @api.constrains("service_report_id", "msp_contract_id", "period_label")
    def _check_report_of_the_credit(self):
        for credit in self:
            report = credit.service_report_id
            if not report:
                continue
            if report.msp_contract_id != credit.msp_contract_id:
                raise ValidationError(
                    "The SLA credit for %s cannot rest on a service report of another contract "
                    "(%s)." % (credit.msp_contract_id.name, report.msp_contract_id.name)
                )
            if report.period_label != credit.period_label:
                raise ValidationError(
                    "The SLA credit for %s is for %s, but its service report covers %s."
                    % (credit.msp_contract_id.name, credit.period_label, report.period_label)
                )
