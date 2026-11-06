# cd_tax_engine_bd — A08 M51 statutory master data (CD-M51-01).
#
# Every Bangladesh rate, threshold and due day the finance screens use is
# EFFECTIVE-DATED master data here (A08 spec rule 3), never a constant in
# code: the company's VAT/tax adviser corrects a row without a release.
# Rows that could not be confirmed against a primary NBR text are seeded
# with verify_with_adviser=True and say so on every screen that shows them.
import logging
from datetime import date, timedelta
from decimal import Decimal

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from . import return_logic, tax_logic

_logger = logging.getLogger(__name__)

TAX_KINDS = [
    ("vat", "VAT"),
    ("tds", "TDS (income tax at source)"),
    ("vds", "VDS (VAT at source)"),
    # A08 M49-8 / BRU-FXA-13: the ITA 2023 Third Schedule depreciation rates
    # are M51 master data (M49 holds no tax rate of its own).
    ("depreciation", "Tax depreciation (ITA 2023 Third Schedule)"),
]
PAYEE_TYPES = [("any", "Any payee"), ("company", "Company"), ("individual", "Individual")]

PARAMETER_KEYS = [
    ("non_filer_multiplier", "Non-filer withholding multiplier (no proof of return)"),
    ("mushak610_threshold", "Mushak 6.10 high-value invoice threshold (BDT)"),
    ("input_credit_window_periods", "Input VAT claim window (tax periods after the invoice)"),
    ("rtgs_min_amount", "BD-RTGS minimum transfer (BDT)"),
]

OBLIGATIONS = [
    ("vat_91_return", "Mushak 9.1 monthly VAT return and payment"),
    ("tds_deposit", "TDS deposit (income tax withheld)"),
    ("vds_deposit", "VDS deposit (VAT withheld)"),
    ("wht_return", "Quarterly withholding tax return"),
    ("company_itr", "Company income tax return (annual)"),
]
# Obligations whose status the ERP reads from its own returns and deposits.
ERP_TRACKED_OBLIGATIONS = ("vat_91_return", "tds_deposit", "vds_deposit", "wht_return")
FREQUENCIES = [("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual")]

# Account roles shared by the AP sub-ledger (cd_ap_ext) and the challans:
# role -> (system parameter, default code or None). A role without a code
# FAILS CLOSED — a tax liability never lands on a guessed account.
TAX_ACCOUNT_ROLES = {
    "vat_output": ("cd_tax_engine_bd.vat_output_account_code", "210100"),
    # A08 M51-8: the old default 110500 is "Work in Progress" in the loaded
    # chart, so AP input VAT (60,337.50 on fix_dev) landed in WIP. There is
    # no safe default: the input-VAT account is configuration, refused unset.
    "vat_input": ("cd_tax_engine_bd.vat_input_account_code", None),
    # chart loader: 252000 "Tax Payable" -> 2-30-30-010 TDS payable
    "tds_payable": ("cd_tax_engine_bd.account_code.tds_payable", "252000"),
    "vds_payable": ("cd_tax_engine_bd.account_code.vds_payable", None),
}


def tax_account(env, company, role):
    """The company's GL account for a tax role — refused when unconfigured."""
    param, default = TAX_ACCOUNT_ROLES[role]
    code = env["ir.config_parameter"].sudo().get_param(param) or default
    account = env["account.account"]
    if code:
        account = (
            env["account.account"]
            .with_company(company)
            .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        )
    if not account:
        raise UserError(
            "No GL account for the %s role in %s: set system parameter %s to an "
            "account code of this company's chart. Nothing was posted."
            % (role, company.name, param)
        )
    return account


def period_of(day):
    """The YYYY-MM VAT/withholding period of a date."""
    return day.strftime("%Y-%m") if day else False


def add_months(year, month, n):
    """(year, month) shifted by n months."""
    idx = year * 12 + (month - 1) + n
    return idx // 12, idx % 12 + 1


class FixJournalPostingLogTax(models.Model):
    """The tax sub-ledger (challans) as a posting source in M19's posting log."""

    _inherit = "fix.journal.posting.log"

    source = fields.Selection(
        selection_add=[("tax_subledger", "Tax Sub-ledger (M51)")],
        ondelete={"tax_subledger": lambda recs: recs.write({"source": "api"})},
    )


MANAGER_GROUP = "account.group_account_manager"
# BRU-TAX-22 "the CFO approves": the same appointment that files the returns.
CFO_GROUP = "cd_tax_engine_bd.group_tax_filing_approver"
# A08 M51-6: rows in force that are not signed off KEEP WORKING (25 of 26 rates
# and 4 of 4 parameters are flagged today: refusing them would stop every bill
# and invoice). They warn, show on the document and report, and queue on the
# Sign-Off Queue screen. Set this to 1 once the queue is empty: find_rate and
# get_value then refuse an unsigned row.
ENFORCE_SIGNOFF_PARAM = "cd_tax_engine_bd.enforce_rate_signoff"
SIGNOFF_STATES = [
    ("adviser", "Awaiting Adviser"),
    ("cfo", "Awaiting CFO"),
    ("signed", "Signed Off"),
]
DEADLINE_REMINDER_PARAM = "cd_tax_engine_bd.deadline_reminder_days"
DEADLINE_REMINDER_DEFAULT = 7
DEADLINE_ESCALATE_PARAM = "cd_tax_engine_bd.deadline_escalate_days"
DEADLINE_ESCALATE_DEFAULT = 3
DEADLINE_LOOKBACK_PARAM = "cd_tax_engine_bd.deadline_lookback_days"
DEADLINE_LOOKBACK_DEFAULT = 90
MASTER_STATES = [
    ("proposed", "Proposed (awaiting activation)"),
    ("active", "Active"),
    ("retired", "Retired"),
]
# Fields of a statutory master row that never freeze: annotations only.
MASTER_FREE_FIELDS = frozenset(
    {"source_note", "adviser_reference_input", "message_follower_ids", "activity_ids"}
)
NON_FILER_FLOOR_PARAM = "cd_tax_engine_bd.non_filer_multiplier_floor"
# ITA 2023: a payee without proof of return suffers the rate +50% (x1.5).
NON_FILER_FLOOR_DEFAULT = 1.5


def float_param(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    try:
        return float(raw) if raw not in (None, False, "") else float(default)
    except (TypeError, ValueError):
        return float(default)


def signoff_enforced(env):
    raw = env["ir.config_parameter"].sudo().get_param(ENFORCE_SIGNOFF_PARAM)
    return str(raw or "").strip().lower() in ("1", "true", "yes", "on")


def tax_alert(record, company, summary, note, groups, deadline=None):
    """A to-do for each active member of `groups` in `company`, once per
    person while one with the same summary is open. Posts nothing."""
    env = record.env
    record = record.sudo()
    done = record.activity_ids.filtered(lambda a: a.summary == summary).mapped("user_id")
    created = env["mail.activity"]
    for xmlid in groups:
        group = env.ref(xmlid, raise_if_not_found=False)
        if not group:
            continue
        for user in group.sudo().all_user_ids.filtered(
            lambda u: u.active and not u.share and company in u.company_ids
        ):
            if user in done:
                continue
            done |= user
            created |= record.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=deadline,
                summary=summary,
                note=note,
                user_id=user.id,
            )
    return created


class _MasterApproval(models.AbstractModel):
    """Two-step change of a statutory master row (A08 M51-6, BRU-TAX-22/23).

    A user's new row is a PROPOSAL: it is never used (find_rate, get_value,
    the calendar and the VAT determination read ACTIVE rows only), it is
    flagged "verify with adviser", and the CFO (the filing approver), who
    neither proposed it nor recorded the confirmation, activates it only after
    an accounting manager records the adviser's written confirmation on it. An
    active row is never edited in place: a change is a new proposal, whose
    activation closes (or retires) the row it supersedes. Rows written by
    trusted system code (seed data, sudo) are active at once, and a seeded row
    flagged for the adviser goes through the same two steps while in force
    (action_record_adviser_verification, then action_cfo_signoff)."""

    _name = "fix.tax.master.approval.mixin"
    _inherit = ["fix.guarded.mixin"]
    _description = "Statutory master row: two-step activation"

    state = fields.Selection(
        MASTER_STATES, string="Status", required=True, default="active", tracking=True, index=True
    )
    verify_with_adviser = fields.Boolean(
        string="Verify with Adviser",
        default=True,
        help="The company's VAT/tax adviser must confirm (or correct) this row before it is "
        "relied on. A proposal so flagged cannot be activated until the adviser's written "
        "confirmation is recorded on it.",
    )
    proposed_by_id = fields.Many2one("res.users", string="Proposed By", readonly=True, copy=False)
    adviser_reference = fields.Char(
        string="Adviser Confirmation",
        readonly=True,
        copy=False,
        help="Reference of the adviser's written confirmation (letter, e-mail, opinion no.)",
    )
    adviser_reference_input = fields.Char(
        string="Adviser Confirmation (to record)",
        copy=False,
        help="Type the adviser's confirmation reference, then Record Adviser Confirmation",
    )
    adviser_verified_by_id = fields.Many2one(
        "res.users", string="Confirmation Recorded By", readonly=True, copy=False
    )
    adviser_verified_at = fields.Datetime(
        string="Confirmation Recorded On", readonly=True, copy=False
    )
    activated_by_id = fields.Many2one("res.users", string="Activated By", readonly=True, copy=False)
    activated_at = fields.Datetime(string="Activated On", readonly=True, copy=False)
    cfo_signed_by_id = fields.Many2one(
        "res.users", string="CFO Sign-Off By", readonly=True, copy=False
    )
    cfo_signed_at = fields.Datetime(string="CFO Sign-Off On", readonly=True, copy=False)
    signoff_state = fields.Selection(
        SIGNOFF_STATES,
        string="Sign-Off",
        compute="_compute_signoff_state",
        store=True,
        index=True,
        help="BRU-TAX-22: the adviser's written confirmation, then the CFO. A seeded row with "
        "no flag was confirmed before this record existed.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "verify_with_adviser",
            "proposed_by_id",
            "adviser_reference",
            "adviser_verified_by_id",
            "adviser_verified_at",
            "activated_by_id",
            "activated_at",
            "cfo_signed_by_id",
            "cfo_signed_at",
        }

    @api.depends("verify_with_adviser", "adviser_reference", "cfo_signed_by_id")
    def _compute_signoff_state(self):
        for rec in self:
            if rec.verify_with_adviser:
                rec.signoff_state = "adviser"
            elif rec.adviser_reference and not rec.cfo_signed_by_id:
                rec.signoff_state = "cfo"
            else:
                rec.signoff_state = "signed"

    def _fix_signoff_check(self):
        """Called where a row in force is used: warn, or refuse once the company
        has decided to enforce it (see ENFORCE_SIGNOFF_PARAM)."""
        for rec in self.filtered(lambda r: r.signoff_state != "signed"):
            if signoff_enforced(rec.env):
                raise UserError(
                    "%s is not signed off by the adviser and the CFO (%s is set), so it is not "
                    "used. See the Sign-Off Queue." % (rec.display_name, ENFORCE_SIGNOFF_PARAM)
                )
            _logger.warning(
                "%s used before its sign-off (%s): see the M51 Sign-Off Queue",
                rec.display_name,
                dict(SIGNOFF_STATES).get(rec.signoff_state),
            )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "proposed":
            locked |= {n for n, f in self._fields.items() if f.store} - MASTER_FREE_FIELDS
        return locked

    # ---- per-model hooks ----------------------------------------------------
    def _fix_master_key_domain(self):
        """Domain of the rows sharing this row's statutory key (rate code,
        parameter key, obligation, tariff code). Override."""
        raise NotImplementedError

    def _fix_master_supersede(self):
        """Activation of this row: retire the active rows it replaces.
        The effective-dated rows override this to close windows instead."""
        self.ensure_one()
        older = self.search(
            [*self._fix_master_key_domain(), ("state", "=", "active"), ("id", "!=", self.id)]
        )
        older._guarded().write({"state": "retired"})

    # ---- ORM ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        if self._fix_guard_open():
            return super().create(vals_list)
        guarded = self._fix_guarded_fields()
        for vals in vals_list:
            typed = (guarded & set(vals)) - {"verify_with_adviser", "state"}
            if typed:
                self._fix_guard_refuse(typed)
            if vals.get("state") not in (None, False, "proposed"):
                self._fix_guard_refuse({"state"})
            vals["state"] = "proposed"
            vals["proposed_by_id"] = self.env.uid
            # a user's statutory change is always confirmed by the adviser
            vals["verify_with_adviser"] = True
        records = super(_MasterApproval, self._guarded()).create(vals_list)
        return records.with_env(self.env)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = self.filtered(lambda r: r.state != "proposed")
            moving = set(vals) - MASTER_FREE_FIELDS
            if frozen and moving:
                changed = {
                    name
                    for rec in frozen
                    for name in moving
                    if name in rec._fields and rec._fix_guard_differs(name, vals[name], rec[name])
                }
                if changed:
                    raise UserError(
                        "%s is an active statutory master row and is never edited in place "
                        "(BRU-TAX-23). Propose a new row with its own Valid From; activating "
                        "it by a second manager closes this one." % frozen[:1].display_name
                    )
            business = moving - self._fix_guarded_fields()
            verified = (self - frozen).filtered("adviser_verified_by_id")
            if business and verified:
                # an edited proposal loses the adviser's confirmation it was given
                res = super().write(vals)
                verified._guarded().write(
                    {
                        "verify_with_adviser": True,
                        "adviser_reference": False,
                        "adviser_verified_by_id": False,
                        "adviser_verified_at": False,
                    }
                )
                return res
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _fix_unlink_proposals_only(self):
        if self.env.su:
            return
        if any(rec.state != "proposed" for rec in self):
            raise UserError("A statutory master row in force is retired, never deleted.")

    # ---- workflow ---------------------------------------------------------------
    def _fix_require_manager(self, what):
        if not self.env.su and not self.env.user.has_group(MANAGER_GROUP):
            raise UserError("%s needs the Accounting Administrator role." % what)

    def action_record_adviser_verification(self, reference=None):
        """Step one: record the adviser's written confirmation of a proposal,
        or of a seeded row already in force (which clears its verify flag and
        changes nothing else). The row then waits for the CFO."""
        self._fix_require_manager("Recording the adviser's confirmation")
        for rec in self:
            ref = (reference or rec.adviser_reference_input or "").strip()
            if not ref:
                raise UserError("State the reference of the adviser's written confirmation.")
            if rec.state not in ("proposed", "active"):
                raise UserError("A retired row is not confirmed.")
            rec._guarded().write(
                {
                    "verify_with_adviser": False,
                    "adviser_reference": ref,
                    "adviser_reference_input": False,
                    "adviser_verified_by_id": self.env.uid,
                    "adviser_verified_at": fields.Datetime.now(),
                }
            )
        return True

    def _fix_require_cfo(self, what):
        if self.env.su or self.env.user.has_group(CFO_GROUP):
            return
        group = self.env.ref(CFO_GROUP, raise_if_not_found=False)
        raise UserError("%s needs the %s role." % (what, group.name if group else CFO_GROUP))

    def action_activate(self):
        """Second step: the CFO, who neither proposed the row nor recorded the
        confirmation, activates it once the adviser's confirmation is recorded.
        (The CFO need not hold the accounting ACLs: the check is here.)"""
        self._fix_require_cfo("Activating a statutory master row")
        for rec in self:
            if rec.state != "proposed":
                raise UserError("%s is not a proposal." % rec.display_name)
            makers = rec.proposed_by_id | rec.create_uid | rec.adviser_verified_by_id
            if not self.env.su and self.env.user in makers:
                raise UserError(
                    "Segregation of duties: you proposed %s or recorded its confirmation; the "
                    "CFO who did neither activates it." % rec.display_name
                )
            if rec.verify_with_adviser:
                raise UserError(
                    "%s is flagged verify-with-adviser: record the adviser's written "
                    "confirmation before it is activated." % rec.display_name
                )
            row = rec.sudo()
            row._fix_master_supersede()
            row._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                    "cfo_signed_by_id": self.env.uid,
                    "cfo_signed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_cfo_signoff(self):
        """Second step for a row already in force: the CFO accepts the adviser's
        confirmation someone else recorded. Changes nothing but the sign-off."""
        self._fix_require_cfo("Signing off a statutory master row")
        for rec in self:
            if rec.state != "active":
                raise UserError("%s is not in force; a proposal is activated." % rec.display_name)
            if rec.signoff_state != "cfo":
                raise UserError(
                    "%s: %s."
                    % (
                        rec.display_name,
                        "record the adviser's written confirmation first"
                        if rec.signoff_state == "adviser"
                        else "it is already signed off",
                    )
                )
            if not self.env.su and self.env.user == rec.adviser_verified_by_id:
                raise UserError(
                    "Segregation of duties: you recorded the adviser's confirmation of %s; the "
                    "CFO who did not signs it off." % rec.display_name
                )
            rec.sudo()._guarded().write(
                {"cfo_signed_by_id": self.env.uid, "cfo_signed_at": fields.Datetime.now()}
            )
        return True

    def action_reject_proposal(self):
        self._fix_require_manager("Rejecting a statutory proposal")
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Only a proposal is rejected.")
            rec._guarded().write({"state": "retired"})
        return True


class _EffectiveDated(models.AbstractModel):
    """Shared validity window of every effective-dated statutory row."""

    _name = "fix.tax.effective.mixin"
    _inherit = ["fix.tax.master.approval.mixin"]
    _description = "Effective-dated statutory master row"

    date_from = fields.Date(string="Valid From", required=True, default=fields.Date.today)
    date_to = fields.Date(string="Valid To", help="Empty = open-ended")
    source_note = fields.Text(string="Source / Note")

    @api.constrains("date_from", "date_to")
    def _check_window(self):
        for row in self:
            if row.date_to and row.date_to < row.date_from:
                raise ValidationError("Valid To cannot be before Valid From")

    def _overlaps(self, domain):
        """True when another ACTIVE row of the same key overlaps this active
        row's window (a proposal is not in force, so it never collides)."""
        self.ensure_one()
        if self.state != "active":
            return False
        far = date(9999, 12, 31)
        for other in self.search([*domain, ("id", "!=", self.id), ("state", "=", "active")]):
            if self.date_from <= (other.date_to or far) and other.date_from <= (
                self.date_to or far
            ):
                return True
        return False

    def _fix_master_supersede(self):
        """Close the window of the active row this one replaces the day
        before it starts; retire one that would start on or after it."""
        self.ensure_one()
        far = date(9999, 12, 31)
        older = self.search(
            [*self._fix_master_key_domain(), ("state", "=", "active"), ("id", "!=", self.id)]
        )
        for old in older:
            if not (
                old.date_from <= (self.date_to or far) and self.date_from <= (old.date_to or far)
            ):
                continue
            if old.date_from < self.date_from:
                old._guarded().write({"date_to": self.date_from - timedelta(days=1)})
            else:
                old._guarded().write({"state": "retired"})

    @api.model
    def _company_first(self, domain, company, limit=1):
        """ACTIVE rows for the company, else the statutory defaults (no company)."""
        Model = self.sudo()
        domain = [*domain, ("state", "=", "active")]
        rows = Model.search([*domain, ("company_id", "=", company.id)], limit=limit)
        return rows or Model.search([*domain, ("company_id", "=", False)], limit=limit)

    @api.model
    def _window_domain(self, on_date):
        return [
            ("date_from", "<=", on_date),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", on_date),
        ]


class FixTaxRate(models.Model):
    """Tax Rate Master: VAT, TDS (ITA 2023 sections) and VDS (service codes)."""

    _name = "fix.tax.rate"
    _description = "Tax Rate Master"
    _inherit = ["fix.tax.effective.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "tax_kind, code, payee_type, date_from desc"

    company_id = fields.Many2one(
        "res.company",
        index=True,
        default=lambda self: self.env.company,
        help="Empty = the statutory default for every company; a company row overrides it",
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", help="Statutory rates are company-wide: leave empty"
    )
    tax_kind = fields.Selection(TAX_KINDS, required=True, index=True, tracking=True)
    code = fields.Char(
        required=True,
        index=True,
        help="TDS category key (e.g. service_general) or the VAT service code (e.g. S074.00)",
    )
    name = fields.Char(string="Description", required=True)
    section = fields.Char(
        string="Statutory Section",
        help="ITA 2023 section for TDS, VAT Act / service code reference for VAT and VDS",
    )
    payee_type = fields.Selection(PAYEE_TYPES, required=True, default="any")
    rate = fields.Float(string="Rate (%)", required=True, digits=(6, 3), tracking=True)
    non_filer_applies = fields.Boolean(
        string="Non-filer Multiplier Applies",
        default=True,
        help="A payee without proof of return submission suffers this rate times "
        "the non-filer multiplier (statutory parameter)",
    )
    active = fields.Boolean(default=True)

    def _fix_master_key_domain(self):
        return [
            ("company_id", "=", self.company_id.id),
            ("tax_kind", "=", self.tax_kind),
            ("code", "=", self.code),
            ("payee_type", "=", self.payee_type),
        ]

    @api.constrains(
        "rate", "tax_kind", "code", "payee_type", "date_from", "date_to", "company_id", "state"
    )
    def _check_rate(self):
        for row in self:
            if not 0 <= row.rate <= 100:
                raise ValidationError("A rate is a percentage between 0 and 100")
            if row._overlaps(
                [
                    ("company_id", "=", row.company_id.id),
                    ("tax_kind", "=", row.tax_kind),
                    ("code", "=", row.code),
                    ("payee_type", "=", row.payee_type),
                ]
            ):
                raise ValidationError(
                    "Another %s rate for %s (%s) is valid in an overlapping window — "
                    "close the old row (Valid To) first" % (row.tax_kind, row.code, row.payee_type)
                )

    @api.depends("tax_kind", "code", "rate")
    def _compute_display_name(self):
        for row in self:
            row.display_name = "%s %s — %s (%g%%)" % (
                (row.tax_kind or "").upper(),
                row.code or "",
                row.section or row.name or "",
                row.rate,
            )

    @api.model
    def find_rate(self, tax_kind, code, on_date, company=None, payee_type="any"):
        """The effective rate row, or a UserError naming what to maintain.
        A payee-type row wins over the 'any' row."""
        company = company or self.env.company
        on_date = on_date or fields.Date.context_today(self)
        base = [("tax_kind", "=", tax_kind), ("code", "=", code), *self._window_domain(on_date)]
        for ptype in dict.fromkeys([payee_type or "any", "any"]):
            row = self._company_first([*base, ("payee_type", "=", ptype)], company)
            if row:
                row._fix_signoff_check()
                return self.browse(row.id)
        raise UserError(
            "No effective %s rate for %r on %s in %s — maintain it in the Tax Rate Master "
            "(never guessed on statutory money)." % (tax_kind.upper(), code, on_date, company.name)
        )

    @api.model
    def _fix_vat_rates(self, on_date=None, company=None):
        """The VAT rates in force (A08 M51-5): the active standard row and
        every active reduced row (codes reduced_*) on the supply date, the
        company's own first. What the sales determination charges."""
        company = company or self.env.company
        on_date = on_date or fields.Date.context_today(self)
        Rate = self.sudo()
        standard = Rate.find_rate("vat", "standard", on_date, company)
        window = [
            ("tax_kind", "=", "vat"),
            ("code", "=like", "reduced_%"),
            *Rate._window_domain(on_date),
        ]
        reduced = Rate._company_first(window, company, limit=None)
        if signoff_enforced(self.env):
            reduced = reduced.filtered(lambda r: r.signoff_state == "signed")
        return tax_logic.VatRates(
            standard=Decimal(str(standard.rate)),
            reduced=frozenset(Decimal(str(r.rate)) for r in reduced),
            source="master",
        )


class FixTaxParameter(models.Model):
    """Statutory scalar parameters (thresholds, multipliers, windows)."""

    _name = "fix.tax.parameter"
    _description = "Statutory Parameter"
    _inherit = ["fix.tax.effective.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "key, date_from desc"

    company_id = fields.Many2one(
        "res.company",
        index=True,
        default=lambda self: self.env.company,
        help="Empty = the statutory default for every company; a company row overrides it",
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", help="Statutory parameters are company-wide: leave empty"
    )
    key = fields.Selection(PARAMETER_KEYS, required=True, index=True)
    value = fields.Float(required=True, digits=(16, 3), tracking=True)

    @api.depends("key", "value")
    def _compute_display_name(self):
        labels = dict(PARAMETER_KEYS)
        for row in self:
            row.display_name = "%s = %g" % (labels.get(row.key, row.key or ""), row.value)

    def _fix_master_key_domain(self):
        return [("company_id", "=", self.company_id.id), ("key", "=", self.key)]

    @api.constrains("key", "value", "date_from", "date_to", "company_id", "state")
    def _check_parameter(self):
        for row in self:
            if row.value < 0:
                raise ValidationError("A statutory parameter cannot be negative")
            if row.key == "non_filer_multiplier":
                floor = float_param(row.env, NON_FILER_FLOOR_PARAM, NON_FILER_FLOOR_DEFAULT)
                if row.value < floor - 1e-9:
                    raise ValidationError(
                        "The non-filer multiplier cannot be below the statutory %.3g "
                        "(ITA 2023: +50%%; system parameter %s)" % (floor, NON_FILER_FLOOR_PARAM)
                    )
            if row._overlaps([("company_id", "=", row.company_id.id), ("key", "=", row.key)]):
                raise ValidationError(
                    "Parameter %s already has a row valid in an overlapping window" % row.key
                )

    @api.model
    def get_value(self, key, on_date=None, company=None):
        company = company or self.env.company
        on_date = on_date or fields.Date.context_today(self)
        row = self._company_first([("key", "=", key), *self._window_domain(on_date)], company)
        if not row:
            raise UserError(
                "Statutory parameter %r has no row valid on %s for %s — maintain it "
                "under Tax Rate Master > Statutory Parameters." % (key, on_date, company.name)
            )
        row._fix_signoff_check()
        return row.value


class FixStatutoryDueRule(models.Model):
    """Due-day master of the statutory calendar."""

    _name = "fix.statutory.due.rule"
    _description = "Statutory Due-Date Rule"
    _inherit = ["fix.tax.effective.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "obligation, date_from desc"

    company_id = fields.Many2one(
        "res.company",
        index=True,
        default=lambda self: self.env.company,
        help="Empty = the statutory default for every company; a company row overrides it",
    )
    operating_unit_id = fields.Many2one("operating.unit", help="Company-wide: leave empty")
    obligation = fields.Selection(OBLIGATIONS, required=True, index=True)
    name = fields.Char(required=True)
    authority = fields.Char(
        default="NBR",
        help="Collecting authority — configurable (the 2025 NBR split is still being implemented)",
    )
    frequency = fields.Selection(FREQUENCIES, required=True)
    due_day = fields.Integer(string="Due Day of Month", required=True)
    month_offset = fields.Integer(
        string="Months After Period End",
        required=True,
        default=1,
        help="1 = the month after the period (monthly/quarterly); for annual rules the "
        "months after the fiscal year end (30 June)",
    )
    roll_to_working_day = fields.Boolean(
        string="Roll to Next Working Day",
        default=True,
        help="A due date on a Friday/Saturday or fixed public holiday moves forward",
    )
    active = fields.Boolean(default=True)

    def _fix_master_key_domain(self):
        return [("company_id", "=", self.company_id.id), ("obligation", "=", self.obligation)]

    @api.constrains(
        "due_day", "month_offset", "obligation", "date_from", "date_to", "company_id", "state"
    )
    def _check_rule(self):
        for rule in self:
            if not 1 <= rule.due_day <= 31:
                raise ValidationError("The due day is a day of the month (1-31)")
            if rule.month_offset < 0:
                raise ValidationError("Months after period end cannot be negative")
            if rule._overlaps(
                [("company_id", "=", rule.company_id.id), ("obligation", "=", rule.obligation)]
            ):
                raise ValidationError(
                    "Obligation %s already has a rule valid in an overlapping window"
                    % rule.obligation
                )

    # ------------------------------------------------------------ periods --
    @staticmethod
    def _period_ends(frequency, date_from, date_to, lookback_months):
        """Every period END (a date) from lookback_months before date_from up to
        date_to: month ends, quarter ends (Sep/Dec/Mar/Jun) or 30 June."""
        y, m = add_months(date_from.year, date_from.month, -lookback_months)
        ends = []
        while date(y, m, 1) <= date_to:
            ny, nm = add_months(y, m, 1)
            end = date(ny, nm, 1) - timedelta(days=1)
            if (
                frequency == "monthly"
                or (frequency == "quarterly" and m in (3, 6, 9, 12))
                or (frequency == "annual" and m == 6)
            ):
                ends.append(end)
            y, m = ny, nm
        return ends

    def _due_for_period_end(self, period_end):
        self.ensure_one()
        y, m = add_months(period_end.year, period_end.month, self.month_offset)
        ny, nm = add_months(y, m, 1)
        last_day = (date(ny, nm, 1) - timedelta(days=1)).day
        due = date(y, m, min(self.due_day, last_day))
        if self.roll_to_working_day:
            due = return_logic.next_working_day(due, set())
        return due

    @staticmethod
    def period_key(frequency, period_end):
        """The register key of a period: YYYY-MM, the TDS-return quarter label
        (FY-start year, e.g. 2026-Q1 = Jul-Sep 2026) or FY2027."""
        if frequency == "monthly":
            return period_end.strftime("%Y-%m")
        quarter, fiscal_year = return_logic.tds_quarter_for_date(period_end)
        return quarter if frequency == "quarterly" else fiscal_year

    @api.model
    def due_date_for(self, obligation, period_end, company=None):
        """The master-data due date of an obligation for the period ending
        period_end, or None when no rule is maintained."""
        company = company or self.env.company
        rule = self._company_first(
            [("obligation", "=", obligation), *self._window_domain(period_end)], company
        )
        return rule._due_for_period_end(period_end) if rule else None

    @api.model
    def calendar(self, date_from, date_to, company=None):
        """The statutory calendar: one row per obligation whose computed due
        date falls in [date_from, date_to], with its status from the ERP's own
        records (returns, withholding deposits) or recorded filing evidence."""
        company = company or self.env.company
        today = fields.Date.context_today(self)
        rows = []
        own = self.sudo().search([("company_id", "=", company.id), ("state", "=", "active")])
        defaults = self.sudo().search(
            [
                ("company_id", "=", False),
                ("state", "=", "active"),
                ("obligation", "not in", own.mapped("obligation")),
            ]
        )
        for rule in own | defaults:
            lookback = (rule.month_offset or 0) + 13
            for end in self._period_ends(rule.frequency, date_from, date_to, lookback):
                if not (rule.date_from <= end and (not rule.date_to or end <= rule.date_to)):
                    continue
                due = rule._due_for_period_end(end)
                if not date_from <= due <= date_to:
                    continue
                key = self.period_key(rule.frequency, end)
                status, detail = rule._status(key, company)
                if status not in ("done", "nothing_due"):
                    status = "overdue" if due < today else "due"
                rows.append(
                    {
                        "rule": rule,
                        "period": key,
                        "period_end": end,
                        "due_date": due,
                        "status": status,
                        "detail": detail,
                    }
                )
        rows.sort(key=lambda r: (r["due_date"], r["rule"].obligation))
        return rows

    def _status(self, key, company):
        """(status, detail) for one period: done / nothing_due / open."""
        self.ensure_one()
        env = self.env
        # A08 M51-1 (S01): the obligations the ERP files or deposits itself are
        # "done" only from their own records; typed evidence counts for the
        # others (e.g. the annual company return) only.
        if self.obligation not in ERP_TRACKED_OBLIGATIONS:
            evidence = env["fix.statutory.filing"].search(
                [
                    ("rule_id", "=", self.id),
                    ("period_key", "=", key),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )
            if evidence:
                return "done", "Filed %s, ref %s" % (evidence.filed_on, evidence.reference)
        if self.obligation == "vat_91_return":
            ret = env["fix.vat.return"].search(
                [("company_id", "=", company.id), ("period", "=", key)], limit=1
            )
            if ret.state == "filed":
                return "done", "Filed, NBR ref %s" % (ret.nbr_confirmation or "-")
            return "open", ("Return %s" % ret.state) if ret else "No return prepared"
        if self.obligation == "wht_return":
            ret = env["fix.tds.return"].search(
                [("company_id", "=", company.id), ("quarter", "=", key)], limit=1
            )
            if ret.state == "filed":
                return "done", "Filed, NBR ack %s" % (ret.nbr_acknowledgment or "-")
            return "open", ("Return %s" % ret.state) if ret else "No return prepared"
        if self.obligation in ("tds_deposit", "vds_deposit"):
            kind = "tds" if self.obligation == "tds_deposit" else "vds"
            lines = env["fix.withholding.line"].search(
                [
                    ("company_id", "=", company.id),
                    ("tax_kind", "=", kind),
                    ("period", "=", key),
                    ("state", "!=", "cancelled"),
                ]
            )
            if not lines:
                return "nothing_due", "Nothing withheld in the period"
            open_lines = lines.filtered(lambda line: line.state == "withheld")
            if not open_lines:
                return "done", "All %d deduction(s) deposited by challan" % len(lines)
            return "open", "BDT %s withheld, not yet deposited (%d line(s))" % (
                "{:,.2f}".format(sum(open_lines.mapped("amount"))),
                len(open_lines),
            )
        return "open", "Record the filing evidence when done"

    @api.model
    def _cron_deadline_reminders(self):
        """AUT-TAX-07 / BRU-TAX-09 (ir.cron, daily): an open obligation due within
        the reminder window, or overdue, is a to-do for the Accounting
        Administrators; close to the deadline or past it, for the CFO too. One
        to-do per person, obligation and period. Posts nothing, files nothing."""
        today = fields.Date.context_today(self)
        ahead = int(float_param(self.env, DEADLINE_REMINDER_PARAM, DEADLINE_REMINDER_DEFAULT))
        urgent = int(float_param(self.env, DEADLINE_ESCALATE_PARAM, DEADLINE_ESCALATE_DEFAULT))
        back = int(float_param(self.env, DEADLINE_LOOKBACK_PARAM, DEADLINE_LOOKBACK_DEFAULT))
        count = 0
        for company in self.env["res.company"].sudo().search([]):
            rows = self.sudo().calendar(
                today - timedelta(days=back), today + timedelta(days=ahead), company
            )
            for row in rows:
                if row["status"] not in ("due", "overdue"):
                    continue
                late = row["status"] == "overdue"
                groups = [MANAGER_GROUP]
                if late or (row["due_date"] - today).days <= urgent:
                    groups.append(CFO_GROUP)
                summary = "%s: %s %s" % (
                    "OVERDUE" if late else "Statutory deadline",
                    row["rule"].name,
                    row["period"],
                )
                note = "%s for %s is due on %s. %s." % (
                    row["rule"].name,
                    row["period"],
                    row["due_date"],
                    row["detail"],
                )
                count += len(
                    tax_alert(row["rule"], company, summary, note, groups, row["due_date"])
                )
        return count


class FixStatutoryFiling(models.Model):
    """Evidence that a statutory obligation was met (any calendar rule)."""

    _name = "fix.statutory.filing"
    _description = "Statutory Filing Evidence"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "filed_on desc, id desc"
    _rule_period_unique = models.Constraint(
        "UNIQUE (company_id, rule_id, period_key)",
        "Evidence for this obligation and period already exists",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    rule_id = fields.Many2one(
        "fix.statutory.due.rule", string="Obligation", required=True, ondelete="restrict"
    )
    period_key = fields.Char(
        string="Period",
        required=True,
        help="YYYY-MM (monthly), 2026-Q1 (quarter, FY-start year) or FY2027 (annual)",
    )
    filed_on = fields.Date(required=True, default=fields.Date.context_today)
    reference = fields.Char(string="Acknowledgement / Reference", required=True)
    note = fields.Text()
    attachment_ids = fields.Many2many("ir.attachment", string="Evidence Files")

    @api.constrains("rule_id")
    def _check_obligation(self):
        for rec in self:
            if rec.rule_id.obligation in ERP_TRACKED_OBLIGATIONS:
                raise ValidationError(
                    "%s is filed or deposited through the ERP itself (its return or challan "
                    "records it); typed filing evidence is not accepted for it." % rec.rule_id.name
                )
