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
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .msp_periods import dhaka_today, month_dates
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
    # A02 ERP pass 2 (M05-S09 / S17 / S18): the scope and metering terms
    "response_hours_major",
    "response_hours_minor",
    "parts_included",
    "remote_hours_monthly",
    "overage_hourly_rate",
)
# the terms whose change moves the monthly fee (M05-S06: published to M39)
MSP_MONEY_TERMS = ("device_count", "per_device_monthly")
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
    # ---- A02 ERP pass 2 (2026-11-20) terms ---------------------------------
    # M05-S18: the response target (first acknowledgement / ticket / fix) per
    # severity. 0 = no response target on this contract.
    response_hours_major = fields.Float(
        string="Major Alert Response Target (h)",
        default=0.0,
        help="Hours to the first response (acknowledged, ticketed or resolved); 0 = none.",
    )
    response_hours_minor = fields.Float(string="Minor Alert Response Target (h)", default=0.0)
    # M05-S09 (owner decision D10): the per-device fee covers labour and remote
    # support. Parts and out-of-scope work are an approved overage estimate
    # unless the contract has a parts entitlement.
    parts_included = fields.Boolean(
        string="Parts Entitlement",
        help="The contract's fee also covers parts. Without it parts and out-of-scope work "
        "on an MSP ticket are priced on an estimate the client approves (overage).",
    )
    # M05-S17 (D11): remote-support hours
    remote_hours_monthly = fields.Float(
        string="Remote Support Hours a Month",
        help="The monthly remote-support entitlement; 0 = not metered against an entitlement.",
    )
    overage_hourly_rate = fields.Monetary(
        string="Overage Rate (BDT / hour)",
        currency_field="currency_id",
        help="Hours above the entitlement are billed at this rate. None = not billed, flagged.",
    )
    terms_amendment_ids = fields.One2many(
        "fix.msp.terms.amendment", "msp_contract_id", string="Terms History"
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

    def action_amend_terms(self, term=None, value=None, reason=None, effective_date=None, **terms):
        """Change the contract's SLA or commercial terms: an SLA credit
        approver (the commercial role), with the reason, recorded on the
        contract. ``term`` / ``value`` take one term from the workspace
        prompt; keyword arguments take several.

        A02 ERP pass 2: every amendment has an effective date (M05-S13, default
        today in Dhaka; never in the future, never inside a month that already
        has its service report) and is kept in the terms history, so a month is
        measured with the terms in force in it. A change of the monthly fee
        (covered devices up or down, or the per-device price) is published to
        the M39 subscription (M05-S06, owner decision D8)."""
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
            effective = msp._msp_amendment_date(effective_date)
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
            old_terms = msp._msp_terms_snapshot()
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
                body="Terms amended by %s, effective %s (%s): %s"
                % (
                    self.env.user.name,
                    effective,
                    reason,
                    "; ".join(
                        "%s %s -> %s" % (msp._fields[n].string, show(before[n]), show(msp[n]))
                        for n in sorted(changed)
                    ),
                )
            )
            amendment = msp._msp_record_amendment(old_terms, effective, reason)
            if set(changed) & set(MSP_MONEY_TERMS):
                msp._msp_publish_commercial_amendment(amendment)
        return True

    def _msp_amendment_date(self, raw):
        """The effective date of an amendment (M05-S13): today in Dhaka by
        default; not in the future (amend on the day it takes effect); not
        inside a month whose service report exists (that month was measured
        with the terms then in force), nor before the M08 term starts."""
        self.ensure_one()
        today = dhaka_today()
        try:
            day = fields.Date.to_date(raw) if raw else today
        except (TypeError, ValueError):
            raise UserError("'%s' is not a date (YYYY-MM-DD)." % raw) from None
        if day > today:
            raise UserError(
                "An amendment takes effect today or on a past date (%s is in the future): "
                "record it on the day it takes effect." % day
            )
        labels = (
            self.env["fix.msp.service.report"]
            .sudo()
            .search([("msp_contract_id", "=", self.id)])
            .mapped("period_label")
        )
        if labels:
            _first, last = month_dates(max(labels))
            if last and day <= last:
                raise UserError(
                    "%s already has its %s service report: an amendment takes effect after "
                    "that month (from %s), never inside a month already measured."
                    % (self.name, max(labels), last + timedelta(days=1))
                )
        start = self.contract_id.sudo().date_start
        if start and day < start:
            raise UserError(
                "An amendment cannot take effect before the M08 term starts (%s)." % start
            )
        return day

    def _msp_terms_snapshot(self) -> dict:
        """The contract's current terms as amendment-row values."""
        self.ensure_one()
        return {
            "device_count": self.device_count,
            "per_device_monthly": self.per_device_monthly,
            "sla_target_pct": self.sla_target_pct,
            "alert_resolve_hours_major": self.alert_resolve_hours_major,
            "alert_resolve_hours_minor": self.alert_resolve_hours_minor,
            "response_hours_major": self.response_hours_major,
            "response_hours_minor": self.response_hours_minor,
            "coverage_window": self.coverage_window,
            "holiday_calendar_id": self.holiday_calendar_id.id or False,
            "parts_included": self.parts_included,
            "remote_hours_monthly": self.remote_hours_monthly,
            "overage_hourly_rate": self.overage_hourly_rate,
            "monthly_value": round((self.per_device_monthly or 0.0) * (self.device_count or 0), 2),
        }

    def _msp_record_amendment(self, old_terms, effective, reason):
        """Write the terms history row of an amendment. A contract with no
        history yet first gets its baseline (the terms before, from the term
        start), so every day has the terms that were in force on it."""
        self.ensure_one()
        Amendment = self.env["fix.msp.terms.amendment"].sudo()._guarded()
        if not Amendment.search_count([("msp_contract_id", "=", self.id)]):
            Amendment.create(
                dict(
                    self._msp_amendment_vals(old_terms),
                    kind="baseline",
                    effective_date=min(self.contract_id.sudo().date_start or effective, effective),
                    reason="Terms before the first recorded amendment",
                    monthly_value_before=old_terms["monthly_value"],
                    device_count_before=old_terms["device_count"],
                    per_device_monthly_before=old_terms["per_device_monthly"],
                    billing_state="none",
                )
            )
        new_terms = self._msp_terms_snapshot()
        delta = round(new_terms["monthly_value"] - old_terms["monthly_value"], 2)
        return Amendment.create(
            dict(
                self._msp_amendment_vals(new_terms),
                kind="amendment",
                effective_date=effective,
                reason=reason,
                amended_by_id=self.env.uid,
                monthly_value_before=old_terms["monthly_value"],
                device_count_before=old_terms["device_count"],
                per_device_monthly_before=old_terms["per_device_monthly"],
                billing_state="pending" if abs(delta) > 0.005 else "none",
            )
        ).with_env(self.env)

    def _msp_amendment_vals(self, terms):
        self.ensure_one()
        vals = {k: v for k, v in terms.items() if k != "monthly_value"}
        vals.update(
            {
                "msp_contract_id": self.id,
                "company_id": self.company_id.id,
                "operating_unit_id": self.operating_unit_id.id or False,
                "monthly_value": terms["monthly_value"],
            }
        )
        return vals

    def _msp_publish_commercial_amendment(self, amendment):
        """BRU-RMS-07 / M05-S05 / S06: the fee change goes to billing as an
        event carrying the amendment and its monthly delta. The M39 consumer
        re-reads the amendment row (the payload is a claim), so the order in
        which amendments are delivered does not matter."""
        self.ensure_one()
        contract = self.contract_id.sudo()
        partner = contract.customer_id.commercial_partner_id or contract.customer_id
        publish(
            self.env,
            "msp.commercial_terms_amended",
            "fix.msp.contract",
            self.id,
            {
                "msp_contract": self.name,
                "msp_contract_id": self.id,
                "amendment_id": amendment.id,
                "contract_id": contract.id,
                "contract_code": contract.code or "",
                "partner_id": partner.id,
                "company_id": self.company_id.id,
                "old_device_count": amendment.device_count_before,
                "new_device_count": amendment.device_count,
                "old_per_device_monthly": amendment.per_device_monthly_before,
                "new_per_device_monthly": amendment.per_device_monthly,
                "monthly_delta": amendment.monthly_delta,
                "currency": self.currency_id.name or "BDT",
                "effective_date": fields.Date.to_string(amendment.effective_date),
                "reason": amendment.reason,
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
