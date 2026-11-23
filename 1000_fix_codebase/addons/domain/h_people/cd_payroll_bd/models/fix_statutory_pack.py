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
import base64

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_payroll_statutory import (
    SEPARATION_RULES,
    TAX_TABLE_RULES,
    TAX_TABLES_BY_RULE,
    digest_rows,
    fiscal_year_of,
)

PAYROLL_MANAGER = "cd_payroll_bd.group_payroll_manager"

# A09 ERP B1b (M56-F3/F4/F5, F16/F17/F18): the pack carries the real figures.
# Every figure field defaults to TODAY'S value (the engine's constants): a new
# pack changes nothing until a Payroll Manager prepares the ruled figures and a
# second one approves them. The tax-table fields are filled from the selected
# enacted table (see figures_for_rule) so nobody types thresholds by hand.
DEFAULT_THRESHOLDS = {
    "general": 375000.0,
    "female_senior": 400000.0,
    "disabled_third_gender": 475000.0,
    "freedom_fighter": 500000.0,
}
DEFAULT_SLABS = [
    [300000.0, 0.10],
    [400000.0, 0.15],
    [500000.0, 0.20],
    [2000000.0, 0.25],
    [None, 0.30],
]
DEFAULT_RESIGNATION_BANDS = [[0, 7], [5, 15], [10, 30]]
DEFAULT_GRATUITY_BANDS = {"min_years": 5, "days_upto_12": 30, "days_above_12": 45}
DEFAULT_OT_BASE = ["basic", "dearness", "ad_hoc"]
OT_BASE_CHOICES = ("basic", "dearness", "ad_hoc", "house_rent", "conveyance", "medical")

TAX_FIGURE_FIELDS = (
    "tax_free_thresholds",
    "guardian_extra_threshold",
    "tax_slabs",
    "minimum_tax",
)
RULE_OPTION_FIELDS = (
    "rebate_rate_percent",
    "rebate_cap",
    "resignation_bands",
    "gratuity_bands",
    "ot_base_components",
    "festival_bonus_proportionate",
)
PACK_FIGURES = (
    "tax_table_rule",
    "ot_divisor_hours",
    "exemption_ceiling",
    "separation_rule",
    *TAX_FIGURE_FIELDS,
    *RULE_OPTION_FIELDS,
)
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
    effective_to = fields.Date(
        string="Effective To",
        tracking=True,
        help="Last day this pack is in force (default: the June 30 that ends the "
        "Bangladesh fiscal year its effective_from starts). A run whose period "
        "starts after every pack's effective_to is refused (AUT-PAY-12).",
    )
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
        TAX_TABLE_RULES, string="Salary Tax Table", required=True, default="fa2025_26_2026_27"
    )
    # ---- M56-F3/F5: the enacted tax figures, effective-dated by fiscal year.
    # Defaults are the LEGACY engine table (what the code did); selecting an
    # enacted rule fills them (create/onchange) from the sourced table.
    tax_free_thresholds = fields.Json(
        string="Tax-Free Thresholds",
        default=dict(DEFAULT_THRESHOLDS),
        help="Tax-free ceiling per taxpayer category (BDT), as enacted for this "
        "pack's fiscal years. The categories are the hr.employee taxpayer "
        "slab categories; the guardian add-on below is the extra ceiling for "
        "the parent / legal guardian of a physically challenged person.",
    )
    guardian_extra_threshold = fields.Float(
        string="Guardian / Disabled-Dependant Add-On (BDT)", default=50000.0
    )
    tax_slabs = fields.Json(
        string="Tax Bands",
        default=lambda self: [list(row) for row in DEFAULT_SLABS],
        help="[[band width (BDT) or null for the balance, rate as a fraction]] "
        "applied above the threshold, in order.",
    )
    minimum_tax = fields.Float(
        string="Minimum Tax (BDT)",
        default=0.0,
        help="Flat minimum annual tax where income exceeds the threshold, as "
        "enacted. 0 keeps the legacy location-based minimum (5,000/4,000/3,000).",
    )
    # ---- M56-F4: the s.78 investment-rebate parameters (OWNER: adviser to
    # confirm the Finance Act 2026 reading of 10% / 750,000; today's 15% /
    # 1,000,000 is the default and the alternative is set on the pack).
    rebate_rate_percent = fields.Float(string="Investment Rebate Rate (%)", default=15.0)
    rebate_cap = fields.Float(string="Investment Rebate Cap (BDT)", default=1000000.0)
    # ---- M56-F16/F17/F18: rule options, mechanism only. Each default is
    # today's behaviour; nothing changes until labour counsel rules.
    resignation_bands = fields.Json(
        string="Resignation Bands",
        default=lambda self: [list(row) for row in DEFAULT_RESIGNATION_BANDS],
        help="[[min completed years, days of wages per year]]. Default: the "
        "engine's bands paying 7 days/year from day 1. Reports on the Labour "
        "(Amendment) Act 2026 read eligibility only from 3 years (7d under 3y, "
        "15d 3-10y, 30d 10y+) - labour counsel to confirm (A09 §7.4).",
    )
    gratuity_bands = fields.Json(
        string="Gratuity Bands",
        default=lambda self: dict(DEFAULT_GRATUITY_BANDS),
        help="{'min_years', 'days_upto_12', 'days_above_12'}: the vesting cliff "
        "and days of basic per completed year. Default: 5 years, 30/45 days "
        "(engine bands, not verified by labour counsel).",
    )
    ot_base_components = fields.Json(
        string="Overtime Base Components",
        default=lambda self: list(DEFAULT_OT_BASE),
        help="Which monthly components the overtime hourly rate is built on. "
        "Default: basic + dearness + ad-hoc (engine reading); many practitioners "
        "read BLR 2015 r.239(1) as basic + house rent + conveyance + medical - "
        "adviser to rule (A09 §7.4).",
    )
    festival_bonus_proportionate = fields.Boolean(
        string="Festival Bonus Proportionate Under One Year",
        default=False,
        help="BLR 2015 r.111(5) reading (OWNER, labour counsel): whether a "
        "joiner with less than a year of service receives a festival bonus "
        "proportionate to days worked. Default No: under-one-year joiners are "
        "skipped, as the code does today.",
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
            locked |= set(PACK_FIGURES) | {"effective_from", "effective_to", "company_id", "basis"}
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

    @api.constrains(
        "tax_free_thresholds",
        "tax_slabs",
        "minimum_tax",
        "rebate_rate_percent",
        "rebate_cap",
        "resignation_bands",
        "gratuity_bands",
        "ot_base_components",
        "effective_from",
        "effective_to",
    )
    def _check_rule_figures(self):
        for rec in self:
            thresholds = rec.tax_free_thresholds or {}
            if not thresholds or any((v or 0) <= 0 for v in thresholds.values()):
                raise ValidationError(
                    "A statutory pack carries a positive tax-free threshold for every "
                    "taxpayer category."
                )
            slabs = rec.tax_slabs or []
            if not slabs:
                raise ValidationError("A statutory pack carries at least one tax band.")
            last_rate = 0.0
            for row in slabs:
                width, rate = row[0], row[1]
                if rate is None or not 0.0 < float(rate) <= 1.0:
                    raise ValidationError("Every tax band rate is a fraction between 0 and 1.")
                if float(rate) < last_rate:
                    raise ValidationError("Tax band rates do not decrease down the schedule.")
                last_rate = float(rate)
                if width is not None and float(width) <= 0:
                    raise ValidationError(
                        "A tax band width is a positive amount or empty " "(the balance band)."
                    )
            if rec.minimum_tax < 0:
                raise ValidationError("The minimum tax cannot be negative.")
            if not 0.0 <= rec.rebate_rate_percent <= 100.0:
                raise ValidationError("The investment rebate rate is a percentage.")
            if rec.rebate_cap < 0:
                raise ValidationError("The investment rebate cap cannot be negative.")
            bands = rec.resignation_bands or []
            if not bands or any(int(b[0]) < 0 or int(b[1]) <= 0 for b in bands):
                raise ValidationError(
                    "Resignation bands are [minimum completed years, positive days per year]."
                )
            grat = rec.gratuity_bands or {}
            if any(int(grat.get(k, 0)) < 0 for k in ("min_years", "days_upto_12", "days_above_12")):
                raise ValidationError("The gratuity band figures cannot be negative.")
            base = rec.ot_base_components or []
            if not base or any(c not in OT_BASE_CHOICES for c in base):
                raise ValidationError(
                    "Overtime base components are chosen from: %s." % ", ".join(OT_BASE_CHOICES)
                )
            if rec.effective_to and rec.effective_from and rec.effective_to < rec.effective_from:
                raise ValidationError("A pack's effective-to day never precedes its first day.")

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

    @api.model
    def figures_for_rule(self, rule):
        """The tax figures of a tax-table rule, as field values. Selecting an
        enacted table fills the pack from the sourced figures - nobody types
        thresholds by hand; a draft table different from every ruled one is a
        deliberate edit on top."""
        table = TAX_TABLES_BY_RULE.get(rule) or {}
        thresholds = {
            k: float(v) for k, v in (table.get("thresholds") or DEFAULT_THRESHOLDS).items()
        }
        slabs = [
            [None if w is None else float(w), float(r)]
            for w, r in (table.get("slabs") or DEFAULT_SLABS)
        ]
        minimum = table.get("minimum_tax")
        return {
            "tax_free_thresholds": thresholds,
            "guardian_extra_threshold": float(table.get("guardian_extra") or 50000),
            "tax_slabs": slabs,
            "minimum_tax": float(minimum) if minimum is not None else 0.0,
        }

    @api.onchange("tax_table_rule")
    def _onchange_tax_table_rule(self):
        if self.tax_table_rule:
            self.update(self.figures_for_rule(self.tax_table_rule))

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
        for vals in vals_list:
            # A pack that names a ruled table but passes no tax figures takes
            # the table's figures (the UI onchange does the same).
            rule = vals.get("tax_table_rule") or "fa2025_26_2026_27"
            if rule in TAX_TABLES_BY_RULE and not any(
                vals.get(f) is not None for f in TAX_FIGURE_FIELDS
            ):
                vals.update(self.figures_for_rule(rule))
            if not vals.get("effective_to") and vals.get("effective_from"):
                # the June 30 that ends the fiscal year the pack starts in
                vals["effective_to"] = fiscal_year_of(fields.Date.to_date(vals["effective_from"]))[
                    1
                ]
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
        """The approved pack of `company` in force on `day`, else the baseline.

        AUT-PAY-12 (A09 M56-F5): a pack in force only within its effective
        range. A day no pack covers - a new fiscal year nobody has approved a
        pack for - is REFUSED, naming the fiscal year: payroll never computes
        on a table nobody signed."""
        Pack = self.sudo()
        in_force = [
            ("effective_from", "<=", day),
            "|",
            ("effective_to", "=", False),
            ("effective_to", ">=", day),
        ]
        pack = Pack.search(
            [
                ("state", "=", "approved"),
                ("company_id", "=", company.id),
                *in_force,
            ],
            order="effective_from desc, version desc",
            limit=1,
        )
        pack = pack or Pack.search(
            [
                ("state", "=", "baseline"),
                ("company_id", "in", [company.id, False]),
                *in_force,
            ],
            order="effective_from desc, version desc",
            limit=1,
        )
        if not pack:
            start = fields.Date.to_date(day)
            fy_start, fy_end = fiscal_year_of(start)
            label = "%d-%02d" % (fy_start.year, fy_end.year % 100)
            raise UserError(
                "No statutory pack is in force for %s in fiscal year %s (%s to %s): payroll "
                "does not compute until a Payroll Manager prepares and a second one approves "
                "the year's pack." % (company.name, label, fy_start, fy_end)
            )
        return pack

    @api.model
    def _fix_tax_table_note(self, company, period):
        """A short warning for the payroll preflight (stream B1a) when the pack
        in force for `period`'s fiscal year is not a signed, sourced one, or a
        newer sourced pack for that year is still awaiting sign-off. None when
        the year's figures are ruled and signed."""
        day = period and getattr(period, "period_start", None)
        if not day:
            return None
        try:
            pack = self._pack_for(company or period.company_id, day)
        except UserError as exc:
            return str(exc)
        notes = []
        if pack.basis == "as_coded":
            notes.append(
                "The statutory pack in force for this period is the unsourced baseline "
                "(pack v%s): its tax table is the superseded pre-enactment draft, which "
                "over-withholds against the enacted Finance Act figures." % (pack.version or 0)
            )
        fy_start, fy_end = fiscal_year_of(fields.Date.to_date(day))
        pending = self.sudo().search(
            [
                ("state", "=", "draft"),
                ("basis", "=", "sourced"),
                ("company_id", "in", [company.id, False] if company else [False]),
                ("effective_from", "<=", fy_end),
                "|",
                ("effective_to", "=", False),
                ("effective_to", ">=", fy_start),
            ],
            order="effective_from desc",
            limit=1,
        )
        if pending:
            notes.append(
                "An enacted, sourced statutory pack (v%s, effective %s) is prepared but not "
                "yet approved: approve it through the routed request before paying the "
                "period on its figures." % (pending.version or 0, pending.effective_from)
            )
        return " ".join(notes) if notes else None

    # ---- the figures, as the engine takes them (M56-F3/F4/F16/F17) ----------
    def _engine_tax_table(self):
        """This pack's tax figures as a libs/py/payroll_engine table dict; the
        slip passes it to compute_payslip so the engine withholds by the pack
        in force for the slip's fiscal year, never by a code constant."""
        self.ensure_one()
        table = dict(self.figures_for_rule(self.tax_table_rule))
        table.update(
            {
                "thresholds": dict(self.tax_free_thresholds or {}),
                "guardian_extra": self.guardian_extra_threshold or 0.0,
                "slabs": [list(row) for row in (self.tax_slabs or [])],
                "minimum_tax": self.minimum_tax or None,
                "rebate_rate": (self.rebate_rate_percent or 0.0) / 100.0,
                "rebate_cap": self.rebate_cap or 0.0,
            }
        )
        return table

    def _engine_separation_kwargs(self):
        """The pack's separation figures as gratuity()/resignation_compensation()
        keyword arguments (M56-F16)."""
        self.ensure_one()
        grat = self.gratuity_bands or {}
        return {
            "bands": [list(row) for row in (self.resignation_bands or DEFAULT_RESIGNATION_BANDS)],
            "min_years": int(grat.get("min_years", 5)),
            "days_upto_12": int(grat.get("days_upto_12", 30)),
            "days_above_12": int(grat.get("days_above_12", 45)),
        }

    def _engine_ot_base(self):
        """The pack's overtime base components (M56-F17)."""
        self.ensure_one()
        return list(self.ot_base_components or DEFAULT_OT_BASE)

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

    # ---- M24 archival of what payroll issues (A09 X-F10) --------------------
    # fix.payroll.period lives in fix_payroll.py and the certificate in
    # fix_payroll_ops.py (stream B1a's files); the consumer methods therefore
    # live here, on this module's own model, and are registered as
    # fix.event.consumer rows in data/fix_payroll_a09_erp_b1b.xml. The relay
    # calls them as superuser; both are idempotent (a redelivered event
    # re-archives nothing).
    def _archive_document(
        self,
        name,
        name_bn,
        filename,
        content_b64,
        mimetype,
        employee,
        slip_model,
        slip_id,
        description,
    ):
        Attachment = self.env["ir.attachment"].sudo()
        if Attachment.search_count(
            [("res_model", "=", slip_model), ("res_id", "=", slip_id), ("name", "=", filename)],
            limit=1,
        ):
            return self.env["fix.document"]
        attachment = Attachment.create(
            {
                "name": filename,
                "type": "binary",
                "datas": content_b64,
                "res_model": slip_model,
                "res_id": slip_id,
                "mimetype": mimetype,
            }
        )
        return (
            self.env["fix.document"]
            .sudo()
            .create(
                {
                    "name": name,
                    "name_bn": name_bn,
                    "document_type": "other",
                    "attachment_id": attachment.id,
                    # linked to the employee: M24's employee dossier
                    "res_model": "hr.employee",
                    "res_id": employee.id,
                    "company_id": employee.company_id.id or self.env.company.id,
                    "isolation_tier": "T3",
                    "description": description,
                }
            )
        )

    @api.model
    def consume_payslips_published(self, event):
        """payroll.payslips_published -> every published payslip's Bengali PDF
        is archived as a fix.document linked to the employee (spec 12.2: the
        M24 retention 'Command')."""
        period = self.env["fix.payroll.period"].sudo().browse(int(event.get("aggregate_id") or 0))
        if not period.exists():
            return True
        for slip in period.payslip_ids.filtered(lambda s: s.published):
            filename = "Payslip_%s_%s.pdf" % (slip.employee_id.name, slip.period_id.name)
            pdf = slip._render_payslip_pdf()
            self._archive_document(
                "Payslip - %s (%s)" % (slip.employee_id.name, slip.period_id.name),
                "বেতন বিবরণী - %s (%s)" % (slip.employee_id.name, slip.period_id.name),
                filename,
                base64.b64encode(pdf).decode(),
                "application/pdf",
                slip.employee_id,
                "fix.payslip",
                slip.id,
                "Archived payslip PDF of %s for period %s (payroll.payslips_published)."
                % (slip.employee_id.name, slip.period_id.name),
            )
        return True

    @api.model
    def consume_certificate_issued(self, event):
        """payroll.certificate_issued -> the issued salary / tax certificate is
        archived as a fix.document linked to the employee, as a signed text
        statement of the certificate's own stored figures (the certificate has
        no PDF report yet - A09 M56-F25)."""
        cert = (
            self.env["fix.payroll.certificate"].sudo().browse(int(event.get("aggregate_id") or 0))
        )
        if not cert.exists() or cert.state != "issued":
            return True
        lines = [
            "1000 FiX Services Ltd. - %s" % (cert.name or "certificate"),
            "Employee: %s" % cert.employee_id.name,
            "Type: %s    Fiscal year: %s" % (cert.certificate_type or "", cert.fiscal_year or ""),
            "Issued on: %s" % (cert.issued_on or ""),
            "Gross: %.2f    Basic: %.2f" % (cert.total_gross or 0.0, cert.total_basic or 0.0),
            "Tax withheld: %.2f    PF deducted: %.2f"
            % (cert.total_tax_withheld or 0.0, cert.total_pf_deducted or 0.0),
            "Statement of the certificate's stored figures under the Income Tax Act 2023.",
        ]
        content = ("\n".join(lines) + "\n").encode("utf-8")
        filename = "Certificate_%s_%s.txt" % (cert.name or "CERT", cert.fiscal_year or "")
        self._archive_document(
            "Salary/Tax Certificate - %s (%s)" % (cert.employee_id.name, cert.fiscal_year or ""),
            "কর ও বেতন সনদ - %s" % cert.employee_id.name,
            filename,
            base64.b64encode(content).decode(),
            "text/plain",
            cert.employee_id,
            "fix.payroll.certificate",
            cert.id,
            "Archived issued certificate %s of %s (payroll.certificate_issued)."
            % (cert.name, cert.employee_id.name),
        )
        return True

    def unlink(self):
        if not self.env.su and any(rec.state != "draft" for rec in self):
            raise UserError("A baseline, approved or cancelled statutory pack is never deleted.")
        return super().unlink()
