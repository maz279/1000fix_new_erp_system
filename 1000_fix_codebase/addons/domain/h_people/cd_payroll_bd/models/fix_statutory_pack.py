# fix_statutory_pack — M56-11 / BRU-PAY-07 / T-01, T-02: the statutory figures
# payroll computes with, as a versioned, effective-dated, approved document.
#
# The A09 audit found the tax table, the overtime divisor, the Para 27
# exemption ceiling and the separation bands hard-coded in the engine or held
# in plain company settings an administrator could change under a posted
# slip (probe M8). They now live in a pack:
#   * version 1 is SEEDED with exactly the figures the code uses today and is
#     marked "as coded, unsourced": nothing is invented, and nothing pretends
#     to be sourced (decisions policy, A09 report §7.3/§7.4);
#   * a new version is prepared by a Payroll Manager and approved through a
#     routed M63 request by a SECOND Payroll Manager (the preparer never
#     decides); once approved its figures never change - a new figure is a
#     new version;
#   * payroll takes the approved pack in force on the period's start date,
#     else the baseline, and every payslip pins the pack it used.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_payroll_statutory import SEPARATION_RULES, TAX_TABLE_RULES, digest_rows

PAYROLL_MANAGER = "cd_payroll_bd.group_payroll_manager"

PACK_FIGURES = ("tax_table_rule", "ot_divisor_hours", "exemption_ceiling", "separation_rule")
PACK_STATES = [
    ("baseline", "As Coded (seeded baseline)"),
    ("draft", "Draft"),
    ("approved", "Approved"),
    ("cancelled", "Cancelled"),
]


class FixApprovalMatrixStatutoryPack(models.Model):
    """The M63 rule book can rule the statutory-pack decision like any other."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("hr_statutory_pack", "HR: Payroll Statutory Pack")],
        ondelete={"hr_statutory_pack": "cascade"},
    )


class FixStatutoryPack(models.Model):
    _name = "fix.statutory.pack"
    _description = "Payroll Statutory Pack"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "fix.people.approval.mixin",
        "fix.payroll.state.lock",
    ]
    _order = "effective_from desc, version desc, id desc"

    _approval_domain = "hr_statutory_pack"
    _approval_apply_method = "action_approve"
    _approval_group = PAYROLL_MANAGER

    name = fields.Char(compute="_compute_name", store=True)
    # Empty only for the seeded baseline, which applies to every company.
    company_id = fields.Many2one("res.company", index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    version = fields.Integer(readonly=True, copy=False)
    effective_from = fields.Date(required=True, tracking=True)
    state = fields.Selection(PACK_STATES, required=True, default="draft", tracking=True)
    basis = fields.Selection(
        [
            ("as_coded", "As coded, unsourced"),
            ("sourced", "Sourced (gazette / adviser evidence attached)"),
        ],
        required=True,
        default="as_coded",
        tracking=True,
    )
    tax_table_rule = fields.Selection(
        TAX_TABLE_RULES, string="Salary Tax Table", required=True, default="engine_fy2026_27"
    )
    ot_divisor_hours = fields.Float(string="Overtime Divisor (hours/month)", required=True)
    exemption_ceiling = fields.Float(string="Para 27 Exemption Ceiling (BDT)", required=True)
    separation_rule = fields.Selection(
        SEPARATION_RULES,
        string="Gratuity & Resignation Bands",
        required=True,
        default="engine_2026_amendment",
    )
    source_note = fields.Text(string="Source / Citation")
    source_file = fields.Binary(string="Source Evidence", attachment=True)
    source_filename = fields.Char()
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", readonly=True, default=lambda self: self.env.user
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(string="Approved On", readonly=True)
    approved_digest = fields.Char(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "version",
            "prepared_by_id",
            "approved_by_id",
            "approved_on",
            "approved_digest",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft" or self.approval_state == "pending":
            locked |= set(PACK_FIGURES) | {"effective_from", "company_id", "basis"}
            locked |= {"source_note", "source_file", "source_filename", "operating_unit_id"}
        return locked

    @api.depends("version", "effective_from", "basis")
    def _compute_name(self):
        for rec in self:
            rec.name = "Statutory Pack v%s from %s%s" % (
                rec.version or "?",
                rec.effective_from or "?",
                " (as coded, unsourced)" if rec.basis == "as_coded" else "",
            )

    @api.constrains("ot_divisor_hours", "exemption_ceiling")
    def _check_figures(self):
        for rec in self:
            if rec.ot_divisor_hours <= 0:
                raise ValidationError("The overtime divisor must be positive.")
            if rec.exemption_ceiling < 0:
                raise ValidationError("The exemption ceiling cannot be negative.")

    @api.constrains("state", "company_id", "effective_from")
    def _check_one_approved_per_date(self):
        for rec in self.filtered(lambda r: r.state == "approved"):
            clash = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("state", "=", "approved"),
                    ("company_id", "=", rec.company_id.id),
                    ("effective_from", "=", rec.effective_from),
                ]
            )
            if clash:
                raise ValidationError(
                    "%s already has an approved statutory pack effective %s."
                    % (rec.company_id.name, rec.effective_from)
                )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            if not self.env.user.has_group(PAYROLL_MANAGER):
                raise AccessError("Only a Payroll Manager prepares a statutory pack.")
            for vals in vals_list:
                if not vals.get("company_id"):
                    vals["company_id"] = self.env.company.id
                if vals.get("state", "draft") != "draft":
                    raise UserError("A statutory pack is created as a draft.")
        records = super().create(vals_list)
        for rec in records.filtered(lambda r: not r.version):
            latest = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    "|",
                    ("company_id", "=", rec.company_id.id),
                    ("company_id", "=", False),
                ],
                order="version desc",
                limit=1,
            )
            rec._guarded().write({"version": (latest.version or 0) + 1})
        return records

    # ---- what payroll uses ---------------------------------------------------
    @api.model
    def _pack_for(self, company, day):
        """The approved pack of `company` in force on `day`, else the baseline."""
        Pack = self.sudo()
        pack = Pack.search(
            [
                ("state", "=", "approved"),
                ("company_id", "=", company.id),
                ("effective_from", "<=", day),
            ],
            order="effective_from desc, version desc",
            limit=1,
        )
        pack = pack or Pack.search(
            [
                ("state", "=", "baseline"),
                ("company_id", "in", [company.id, False]),
                ("effective_from", "<=", day),
            ],
            order="effective_from desc, version desc",
            limit=1,
        )
        if not pack:
            raise UserError(
                "No statutory pack is in force for %s on %s: payroll does not compute without "
                "one." % (company.name, day)
            )
        return pack

    def _figures_digest(self):
        self.ensure_one()
        return digest_rows([(name, str(self[name])) for name in (*PACK_FIGURES, "effective_from")])

    # ---- the routed decision -------------------------------------------------
    def _approval_subject_employees(self):
        return self.env["hr.employee"]

    def _approval_preparers(self):
        return (self.prepared_by_id | self.create_uid).sudo()

    def action_request_approval(self, justification=None):
        if not (self.env.su or self.env.user.has_group(PAYROLL_MANAGER)):
            raise AccessError("Only a Payroll Manager submits a statutory pack.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft statutory pack is sent for approval.")
            if rec.basis == "sourced" and not ((rec.source_note or "").strip() and rec.source_file):
                raise UserError(
                    "A pack marked sourced carries its citation and the evidence file (the "
                    "gazette, Finance Act or adviser's opinion)."
                )
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """The second Payroll Manager's decision, from the inbox only."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        decider = self._people_decider()
        if not (self.env.su or decider.has_group(PAYROLL_MANAGER)):
            raise AccessError("Only a Payroll Manager approves a statutory pack.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft statutory pack is approved.")
            if decider in rec._approval_preparers():
                raise UserError("The Payroll Manager who prepared a pack never approves it.")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": decider.id,
                    "approved_on": fields.Datetime.now(),
                    "approved_digest": rec._figures_digest(),
                }
            )
            rec.message_post(body="Statutory pack approved by %s." % decider.name)

    def action_cancel(self):
        for rec in self:
            if rec.state != "draft" or rec.approval_state == "pending":
                raise UserError("Only a draft pack not awaiting approval is cancelled.")
            rec._guarded().write({"state": "cancelled"})

    def action_new_version(self, effective_from=None):
        """A draft copy of this pack's figures for a new effective date."""
        self.ensure_one()
        new = self.create(
            {
                "company_id": self.company_id.id or self.env.company.id,
                "effective_from": fields.Date.to_date(effective_from)
                if effective_from
                else fields.Date.context_today(self),
                "basis": self.basis,
                **{name: self[name] for name in PACK_FIGURES},
            }
        )
        return {"res_model": self._name, "res_id": new.id}

    def unlink(self):
        if not self.env.su and any(rec.state != "draft" for rec in self):
            raise UserError("A baseline, approved or cancelled statutory pack is never deleted.")
        return super().unlink()
