# M03 class-H business rules (M03 bidirectional audit, 13 Nov 2026; owner
# chose to build them).
#
# BRU-LOG-03 (CFO): a consignment above the declared-value threshold needs
# transit insurance and a second signature before it is dispatched - the
# person who confirms the dispatch is never the one who countersigned it.
# BRU-LOG-05 / BRU-LOG-10 (Quality / Logistics Manager): a restricted item
# (lithium battery, refrigerant, other hazardous goods) is carried only by a
# rider or courier certified for it, and a lapsed certification counts as none.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_consignment import GROUP_HUB, GROUP_MANAGER

HIGH_VALUE_PARAM = "cd_consignment.high_value_threshold_bdt"
# Owner to confirm (OWNER_DECISIONS I3): the spec names the rule, not the figure.
HIGH_VALUE_DEFAULT_BDT = 50000.0

RESTRICTED_CLASSES = [
    ("lithium_battery", "Lithium Battery"),
    ("refrigerant", "Refrigerant Gas"),
    ("other_hazardous", "Other Hazardous Item"),
]


def high_value_threshold(env):
    raw = env["ir.config_parameter"].sudo().get_param(HIGH_VALUE_PARAM)
    try:
        return float(raw) if raw not in (None, False, "") else HIGH_VALUE_DEFAULT_BDT
    except (TypeError, ValueError):
        return HIGH_VALUE_DEFAULT_BDT


class FixRiderCertification(models.Model):
    """A rider's certification to carry one class of restricted item
    (BRU-LOG-05). Recorded by a logistics manager from the certificate the
    rider holds; it covers the dates it is valid for."""

    _name = "fix.rider.certification"
    _description = "Rider Restricted-Item Certification"
    _order = "valid_until desc, id desc"
    _rec_name = "certificate_ref"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", string="Rider", required=True, index=True)
    item_class = fields.Selection(RESTRICTED_CLASSES, string="Restricted Class", required=True)
    certificate_ref = fields.Char(string="Certificate No.", required=True)
    issued_on = fields.Date(string="Issued On")
    valid_until = fields.Date(string="Valid Until", required=True)
    attachment_id = fields.Many2one("ir.attachment", string="Certificate Scan")
    active = fields.Boolean(default=True)

    @api.constrains("issued_on", "valid_until")
    def _check_dates(self):
        for rec in self:
            if rec.issued_on and rec.valid_until < rec.issued_on:
                raise ValidationError("A certification cannot expire before it is issued.")

    @api.model
    def _covers(self, employee, item_class, on_date):
        """Is the rider certified for this class on this date?"""
        if not employee or not item_class:
            return False
        return bool(
            self.sudo().search_count(
                [
                    ("employee_id", "=", employee.id),
                    ("item_class", "=", item_class),
                    ("valid_until", ">=", on_date),
                    "|",
                    ("issued_on", "=", False),
                    ("issued_on", "<=", on_date),
                ],
                limit=1,
            )
        )


class FixCourierPartnerRestricted(models.Model):
    _inherit = "fix.courier.partner"

    restricted_item_certified = fields.Boolean(
        string="Certified for Restricted Items",
        help="BRU-LOG-10: may carry batteries, refrigerant and other restricted items "
        "while the certification is valid.",
    )
    restricted_cert_valid_until = fields.Date(string="Restricted-Item Certification Valid Until")

    def _restricted_ok(self, on_date):
        self.ensure_one()
        return self.restricted_item_certified and (
            not self.restricted_cert_valid_until or self.restricted_cert_valid_until >= on_date
        )


class FixConsignmentControls(models.Model):
    _inherit = "fix.consignment"

    restricted_item = fields.Boolean(
        string="Carries a Restricted Item",
        tracking=True,
        help="Lithium battery, refrigerant or other hazardous goods (BRU-LOG-05).",
    )
    restricted_item_class = fields.Selection(
        RESTRICTED_CLASSES, string="Restricted Class", tracking=True
    )
    insurance_flag = fields.Boolean(
        string="Transit Insurance Taken",
        tracking=True,
        help="Required before a high-value consignment is dispatched (BRU-LOG-03).",
    )
    high_value = fields.Boolean(
        string="High Value",
        compute="_compute_high_value",
        help="Declared value at or above the high-value threshold (setting "
        "cd_consignment.high_value_threshold_bdt).",
    )
    dispatch_countersigned_by_id = fields.Many2one(
        "res.users", string="Dispatch Countersigned By", readonly=True, copy=False
    )
    dispatch_countersigned_at = fields.Datetime(
        string="Dispatch Countersigned At", readonly=True, copy=False
    )
    dispatch_countersigned_value = fields.Float(
        string="Value Countersigned (BDT)", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "dispatch_countersigned_by_id",
            "dispatch_countersigned_at",
            "dispatch_countersigned_value",
        }

    # ------------------------------------------------------------ BRU-LOG-03
    @api.depends("declared_value_bdt")
    def _compute_high_value(self):
        threshold = high_value_threshold(self.env)
        for rec in self:
            rec.high_value = (rec.declared_value_bdt or 0.0) >= threshold

    def _restricted_carrier_problem(self, on_date=None):
        """Why this consignment's carrier may not take its restricted item, or
        None (BRU-LOG-05/10). Checked on the run date when assigned, and again
        on the day it is confirmed and handed over (a certification lapses)."""
        self.ensure_one()
        if not self.restricted_item:
            return None
        if not self.restricted_item_class:
            return "%s carries a restricted item: name its class." % self.name
        day = on_date or (
            self.scheduled_date.date() if self.scheduled_date else fields.Date.today()
        )
        labels = dict(RESTRICTED_CLASSES)
        what = labels.get(self.restricted_item_class, self.restricted_item_class)
        if self.rider_id and not self.env["fix.rider.certification"]._covers(
            self.rider_id, self.restricted_item_class, day
        ):
            return "%s is not certified to carry %s on %s (BRU-LOG-05)." % (
                self.rider_id.name,
                what,
                day,
            )
        if self.courier_partner_id and not self.courier_partner_id._restricted_ok(day):
            return "%s has no valid restricted-item certification on %s (BRU-LOG-10)." % (
                self.courier_partner_id.name,
                day,
            )
        return None

    @api.constrains(
        "restricted_item",
        "restricted_item_class",
        "rider_id",
        "courier_partner_id",
        "scheduled_date",
    )
    def _check_restricted_carrier(self):
        for rec in self:
            if rec.state in ("delivered", "returned", "lost"):
                continue
            problem = rec._restricted_carrier_problem()
            if problem:
                raise ValidationError(problem)

    def action_countersign_dispatch(self):
        """The second signature on a high-value dispatch (BRU-LOG-03): a hub
        operator or logistics manager vouches for the declared value. The
        dispatch is then confirmed by a different person."""
        self._logistics_require(GROUP_HUB, GROUP_MANAGER, what="Countersigning a dispatch")
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft consignment is countersigned (%s is %s)." % (rec.name, rec.state)
                )
            if not rec.high_value:
                raise UserError(
                    "%s is below the high-value threshold (BDT %s); it needs no countersignature."
                    % (rec.name, f"{high_value_threshold(self.env):,.0f}")
                )
            rec._guarded().write(
                {
                    "dispatch_countersigned_by_id": self.env.user.id,
                    "dispatch_countersigned_at": fields.Datetime.now(),
                    "dispatch_countersigned_value": rec.declared_value_bdt,
                }
            )
            rec.message_post(
                body="High-value dispatch countersigned at a declared value of BDT %s."
                % f"{rec.declared_value_bdt:,.2f}"
            )
        return True

    def _check_dispatch_controls(self, confirming=True):
        """Gates of Confirm for Dispatch beyond the declared value itself.
        A02 ERP audit M03-F2: run again at Start Transit (confirming=False),
        where the dual-signature rule (the countersigner does not confirm) is
        not re-applied: the confirmation already happened."""
        for rec in self:
            if rec.high_value:
                if not rec.insurance_flag:
                    raise UserError(
                        "%s is a high-value consignment (BDT %s or more): mark the transit "
                        "insurance before dispatch (BRU-LOG-03)."
                        % (rec.name, f"{high_value_threshold(self.env):,.0f}")
                    )
                if not rec.dispatch_countersigned_by_id or (
                    abs((rec.dispatch_countersigned_value or 0.0) - rec.declared_value_bdt) > 0.005
                ):
                    raise UserError(
                        "%s is a high-value consignment: a second person must countersign its "
                        "declared value before dispatch (BRU-LOG-03)." % rec.name
                    )
                if (
                    confirming
                    and rec.dispatch_countersigned_by_id == self.env.user
                    and not self.env.su
                ):
                    raise UserError(
                        "You countersigned %s; a different person confirms its dispatch "
                        "(dual signature, BRU-LOG-03)." % rec.name
                    )
            problem = rec._restricted_carrier_problem(fields.Date.context_today(rec))
            if problem:
                raise UserError(problem)
