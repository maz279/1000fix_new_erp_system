# cd_gl_ext — M19 Financial Accounting & General Ledger core (P06-M01).
#
# Built on Odoo `account` (vendor) + OCA account-financial-tools (T01), this
# module carries the 1000FiX-specific structure:
#   - branch/OU dimensions on every posting (AS-03: cost centre + branch)
#   - the 5-day period-close process (CD-M19-05 close checklist)
#   - the fixed-asset seam M49 extends in Phase 8
#   - the W2 inventory suspense reconciliation stub (AR-006 §5.4)
#   - journal.posted / period.closed events through the outbox (AS-08)
#
# A08 remediation (B3, 4 Nov 2026):
#   - F4  closing a period sets the company lock date in the same transaction;
#         the close is an Accounting Administrator act on a period that has
#         ended; state and stamps are guarded (M19-1, -5, -6).
#   - S2  THE M19 posting API. Every journal entry posts through
#         post_with_dimensions() / post_existing_moves() (or the account.move
#         wrappers _fix_post_via_m19 / _fix_m19_post): the API carries an
#         in-process token that the account.move._post guard
#         (fix_gl_posting_control.py) requires for manual entries. A manual
#         journal is drafted by create_journal_entry_draft() and posted only
#         when its routed fix.journal.approval is approved (M19-2, -8).
#
# AS-10: every amount below is fields.Monetary with an explicit currency_id.
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish  # FF-28: the only event client

from . import coa_logic

_logger = logging.getLogger(__name__)

ACCOUNT_USER = "account.group_account_user"
ACCOUNT_MANAGER = "account.group_account_manager"

# --------------------------------------------------------------------------
# The M19 posting token. An object, never a flag: JSON-RPC can put any key in
# the context, but not this object. post_with_dimensions / post_existing_moves
# are the only code that obtains it.
# --------------------------------------------------------------------------
M19_TOKEN_KEY = "fix_m19_posting"  # noqa: S105 - a context key, not a secret
M19_SOURCE_KEY = "fix_m19_source"
_M19_TOKEN = object()


def m19_context(source):
    """Context that lets account.move._post accept a posting from `source`."""
    return {M19_TOKEN_KEY: _M19_TOKEN, M19_SOURCE_KEY: source or "api"}


def has_m19_token(env) -> bool:
    return env.context.get(M19_TOKEN_KEY) is _M19_TOKEN


def m19_source(env):
    return env.context.get(M19_SOURCE_KEY) if has_m19_token(env) else None


def holds(user, xmlid) -> bool:
    """The user holds the role. The Accounting Administrator does every
    Accountant duty: Odoo 19's manager group does not imply group_account_user,
    so a finance manager could not draft a journal (AR and treasury agree)."""
    if user.has_group(xmlid):
        return True
    return xmlid == ACCOUNT_USER and user.has_group(ACCOUNT_MANAGER)


def holds_group(user, group) -> bool:
    """`holds` for a group record (a close step names its owner as a record)."""
    user = user.sudo()
    if group in user.all_group_ids:
        return True
    accountant = user.env.ref(ACCOUNT_USER, raise_if_not_found=False)
    return bool(accountant and group == accountant and user.has_group(ACCOUNT_MANAGER))


def has_role(env, xmlid) -> bool:
    """Superuser code (crons, seeds, service calls) is trusted."""
    return env.su or holds(env.user, xmlid)


def require_role(env, xmlid, what):
    if not has_role(env, xmlid):
        group = env.ref(xmlid, raise_if_not_found=False)
        raise AccessError(
            "%s needs the %s role, which you do not hold." % (what, group.name if group else xmlid)
        )


def require_takeon_authority(env, what):
    """The one gate of the legacy take-on wizards. A take-on writes the opening
    position to the general ledger (and creates parties as the system) outside
    the manual-journal maker-checker, so it is an Accounting Administrator's
    act. The cut-over loaders run as the superuser and pass."""
    if not has_role(env, ACCOUNT_MANAGER):
        raise AccessError(
            "%s is an Accounting Administrator's act; an accountant stages and validates "
            "the batch, the administrator posts it." % what
        )


def ensure_legacy_account(env, company, name, code, account_type):
    """The take-on wizards' own accounts (contra, unallocated receipts):
    found by CODE first, then by name, created at most once. The wizards
    used to try a create, swallow any exception and create again through a
    fallback that wrote the code as a stringified dict - the first create had
    already inserted its row, so the real chart gained duplicate contra
    accounts and an account coded "{'1': '2-99-99-902'}" (fix_real, Nov 2026).
    The root cause was the code itself: Odoo 19 accepts only alphanumerics and
    dots in an account code, so "2-99-99-901" never validated and every run
    took the fallback. The take-on accounts use the dotted form, 2.99.99.90x.
    A failure now refuses with its cause; it never guesses a second account."""
    Account = env["account.account"].with_company(company)
    existing = Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    if not existing:
        existing = Account.search(
            [("name", "=", name), ("company_ids", "in", company.id)], order="id", limit=1
        )
    if existing:
        return existing
    try:
        with env.cr.savepoint():
            return Account.create(
                {
                    "name": name,
                    "code": code,
                    "account_type": account_type,
                    "company_ids": [(6, 0, [company.id])],
                }
            )
    except Exception as exc:
        raise UserError(
            "Could not create account %s %s on %s (%s). Create it on the chart first."
            % (code, name, company.name, exc)
        ) from exc


def _split_dims(value) -> set:
    """'branch;cost_centre' -> {'branch', 'cost_centre'} (blank items dropped)."""
    return {d.strip() for d in (value or "").split(";") if d.strip()}


class FixJournalDimension(models.Model):
    """The 7-dimension model on every posting (FR-FIN-001..007).

    Every posting carries entity (company), operating unit, branch and cost
    centre plus the business line / project / brand / channel tags — the
    multi-entity, multi-branch ledger requirement (T03). Implementing as a
    model linked to move lines keeps Odoo's account.move untouched at the
    column level while the dimensions ride every entry."""

    _name = "fix.journal.dimension"
    _description = "Journal Posting Dimension"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", required=True, index=True
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    cost_centre = fields.Char(
        string="Cost Centre",
        index=True,
        help="Free-form cost centre code from the MD-* finance set",
    )
    business_line = fields.Char(
        string="Business Line",
        index=True,
        help="One of the 14 business streams (White Goods / Mobile / ICT / AMC...)",
    )
    project_ref = fields.Char(
        string="Project / Contract",
        index=True,
        help="Project or AMC contract reference riding the posting",
    )
    brand = fields.Char(
        string="Brand / OEM",
        index=True,
        help="Brand/OEM dimension (Samsung, HP, Walton...) — warranty economics",
    )
    channel = fields.Char(
        string="Service Channel",
        index=True,
        help="Carry-in depot / field service / mail-in channel tag",
    )
    move_line_id = fields.Many2one(
        "account.move.line", string="Journal Item", required=True, ondelete="cascade", index=True
    )

    @api.constrains("branch_id", "operating_unit_id")
    def _check_branch_ou(self):
        for dim in self:
            if dim.branch_id and dim.branch_id.operating_unit_id != dim.operating_unit_id:
                raise ValidationError(
                    "Branch %s does not belong to operating unit %s"
                    % (dim.branch_id.name, dim.operating_unit_id.name)
                )


# C10 (owner decision 12 Nov 2026, D2-12): the VAT step is done only on a
# PREPARED and RECONCILED Mushak 9.1 return of the period (the evidence used to
# be checked for existence only, and an unreconciled 9.1 closed the step).
VAT_CLOSE_STEP = "VAT Sub-Ledger & Mushak 9.1 Return Preparation"

# The 10 statutory close steps of SOP SP-020: (sequence, step, owner role,
# target day, blocking, owning group xmlid). A step is completed by a holder
# of its owning group (A08 M19-5: one accountant used to clear every owner's
# step, the CFO's included, with the evidence "x").
STANDARD_CLOSE_STEPS = [
    (
        10,
        "Subledger Cut-Off & Physical Inventory Counts",
        "Supply Chain Lead",
        0,
        True,
        "stock.group_stock_manager",
    ),
    (
        20,
        "Bank Statement Feeds Import & Automated Reconciliation",
        "Treasury Lead",
        1,
        True,
        ACCOUNT_USER,
    ),
    (30, "AR Billing & Auto-Invoice Clearance", "Billing Specialist", 2, True, ACCOUNT_USER),
    (40, "AP Three-Way Match & Vendor Invoice Clearance", "AP Accountant", 3, True, ACCOUNT_USER),
    (50, VAT_CLOSE_STEP, "Tax Manager", 3, True, ACCOUNT_USER),
    (
        60,
        "Inventory Suspense Account Zero-Balance Clearance",
        "Inventory Accountant",
        4,
        True,
        ACCOUNT_USER,
    ),
    (70, "Fixed Asset Capitalisation Interface Review", "Asset Accountant", 4, False, ACCOUNT_USER),
    (80, "Inter-Branch & Operating Unit Dimension Balancing", "GL Lead", 5, True, ACCOUNT_USER),
    (
        90,
        "Accruals, Depreciation & Tax Withholding Postings",
        "Senior Accountant",
        5,
        True,
        ACCOUNT_USER,
    ),
    (
        100,
        "General Ledger Lock & Financial Statements Generation",
        "Chief Financial Officer",
        5,
        True,
        ACCOUNT_MANAGER,
    ),
]

STANDARD_STEP_NAMES = frozenset(step[1] for step in STANDARD_CLOSE_STEPS)

# Records a close step's evidence may point at ("model,id"). The record must
# exist: an evidence string that names nothing is not evidence (M19-5).
EVIDENCE_MODELS = (
    "account.move",
    "account.bank.statement",
    "account.bank.statement.line",
    "fix.journal.posting.log",
    "fix.financial.report.bridge",
    "fix.chart.loader",
    "fix.fx.revaluation",
    "fix.allocation.rule",
    "fix.inventory.valuation.suspense",
    "fix.mushak.register",
    "fix.mushak.return",
    "fix.vat.return",
    "fix.depreciation.run",
    "ir.attachment",
)


def dhaka_today(record):
    """Today in the user's (Bangladesh) calendar, not UTC."""
    return fields.Date.context_today(record)


class FixPeriodClose(models.Model):
    """The 5-day month-end close process (T06 / CD-M19-05).

    A close checklist instance per company+period. Each line is a close step
    with an owner and a target day-offset; the close is DONE only when every
    blocking step is cleared. Day 0 = period end. Closing sets the company
    Global Lock Date to the period end in the same transaction: nobody posts
    into a closed period except through an approved, time-boxed reopen
    (fix.period.reopen)."""

    _name = "fix.period.close"
    _description = "Period Close Checklist"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "period_end desc, company_id"
    _company_period_unique = models.Constraint(
        "UNIQUE (company_id, period_end)", "One close checklist per company and period"
    )

    CLOSE_TARGET_DAYS = 5  # G3-04: month-end close within 5 days

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    period_end = fields.Date(string="Period End", required=True)
    started_at = fields.Datetime(string="Started At", default=fields.Datetime.now)
    target_completion_date = fields.Date(
        string="Target Completion Date",
        compute="_compute_target_completion",
        store=True,
    )
    state = fields.Selection(
        [
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("ready_to_close", "Ready to Close"),
            ("closed", "Closed"),
        ],
        default="open",
        required=True,
        tracking=True,
    )
    sla_status = fields.Selection(
        [("within_sla", "Within 5-Day SLA"), ("breached", "Breached Target")],
        string="SLA Performance",
        compute="_compute_duration",
        store=True,
    )
    line_ids = fields.One2many("fix.period.close.line", "close_id", string="Close Steps")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # AS-10: monetary, never float
    suspense_opening = fields.Monetary(
        string="Suspense Opening",
        currency_field="currency_id",
        help="Balance in the W2 inventory suspense account at period start",
    )
    suspense_closing = fields.Monetary(
        string="Suspense Closing",
        currency_field="currency_id",
        readonly=True,
        help="What is still pending after the suspense reconciliation — computed by it, "
        "never typed.",
    )
    suspense_reconciled = fields.Boolean(string="Suspense Reconciled", default=False, readonly=True)
    cutover_voucher_ref = fields.Char(string="Suspense Cutover Voucher Ref", readonly=True)
    cutover_move_id = fields.Many2one(
        "account.move",
        string="Suspense Cutover Journal Entry",
        copy=False,
        help="The POSTED journal entry that brings the W2 inventory suspense into the "
        "general ledger. Required to reconcile the suspense.",
    )
    closed_at = fields.Datetime(readonly=True)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    ready_by_id = fields.Many2one("res.users", string="Ready Check By", readonly=True, copy=False)
    lock_date_set = fields.Date(
        string="Lock Date Set",
        readonly=True,
        copy=False,
        help="The company Global Lock Date this close set (or found already set).",
    )
    reopen_ids = fields.One2many("fix.period.reopen", "close_id", string="Reopen Requests")
    is_locked = fields.Boolean(
        string="Ledger Locked",
        compute="_compute_is_locked",
        help="True when the company Global Lock Date covers this period end — read "
        "from the company, never ticked.",
    )
    close_duration_days = fields.Float(
        compute="_compute_duration", store=True, string="Close Duration (days)"
    )

    @api.depends("period_end", "company_id")
    def _compute_display_name(self):
        # No `name` field: a many2one picker (reopen request, bridge) must not
        # read "fix.period.close,7".
        for close in self:
            close.display_name = "Close %s - %s" % (
                close.period_end or "",
                close.company_id.sudo().name or "",
            )

    def _fix_check_month_end(self, period_end):
        """A close covers a calendar month: the lock it sets and the window a
        reopen admits are measured from it (FR-FIN-019). Now that a person types
        the date on a form, 2026-10-15 is a mistake to refuse, not a period.
        Superuser code (seeds, service calls) is trusted, as the guards trust it,
        which is why this is not an @api.constrains: those run as the superuser."""
        end = fields.Date.to_date(period_end)
        if end and not self.env.su and (end + timedelta(days=1)).day != 1:
            raise ValidationError("Period end %s is not the last day of a month." % end)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._fix_check_month_end(vals.get("period_end"))
        return super().create(vals_list)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "closed_at",
            "closed_by_id",
            "ready_by_id",
            "lock_date_set",
            "suspense_closing",
            "suspense_reconciled",
            "cutover_voucher_ref",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields() | {"is_locked", "target_completion_date"}
        if any(c.state == "closed" for c in self):
            locked |= {"period_end", "company_id", "cutover_move_id", "suspense_opening"}
        return locked

    def write(self, vals):
        frozen = {"period_end", "company_id", "cutover_move_id", "suspense_opening"}
        if (
            frozen & set(vals)
            and not self._fix_guard_open()
            and any(c.state == "closed" for c in self)
        ):
            raise UserError("A closed period's facts are frozen; reopen it through an approval.")
        self._fix_check_month_end(vals.get("period_end"))
        return super().write(vals)

    @api.depends("company_id.fiscalyear_lock_date", "period_end")
    def _compute_is_locked(self):
        for close in self:
            lock = close.company_id.sudo().fiscalyear_lock_date
            close.is_locked = bool(lock and close.period_end and lock >= close.period_end)

    @api.depends("period_end")
    def _compute_target_completion(self):
        for close in self:
            target_days = getattr(close, "CLOSE_TARGET_DAYS", getattr(self, "CLOSE_TARGET_DAYS", 5))
            if close.period_end:
                close.target_completion_date = fields.Date.add(close.period_end, days=target_days)
            else:
                close.target_completion_date = False

    @api.depends("period_end", "closed_at")
    def _compute_duration(self):
        for close in self:
            target_days = getattr(close, "CLOSE_TARGET_DAYS", getattr(self, "CLOSE_TARGET_DAYS", 5))
            if close.closed_at:
                delta = fields.Datetime.from_string(close.closed_at).date() - close.period_end
                duration = max(delta.days, 0.0)
                close.close_duration_days = duration
                close.sla_status = "within_sla" if duration <= target_days else "breached"
            else:
                close.close_duration_days = 0.0
                close.sla_status = "within_sla"

    def action_generate_standard_steps(self):
        """Generate the 10 statutory close steps from SOP SP-020."""
        self.ensure_one()
        require_role(self.env, ACCOUNT_USER, "Starting a period close")
        if self.state != "open":
            raise UserError("The close steps are generated once, on an open close.")
        line_model = self.env["fix.period.close.line"]._guarded()
        for seq, name, role, day, blocking, group_xmlid in STANDARD_CLOSE_STEPS:
            group = self.env.ref(group_xmlid, raise_if_not_found=False) or self.env.ref(
                ACCOUNT_USER
            )
            line_model.create(
                {
                    "close_id": self.id,
                    "sequence": seq,
                    "name": name,
                    "owner_role": role,
                    "owner_group_id": group.id,
                    "target_day": day,
                    "blocking": blocking,
                    "state": "pending",
                }
            )
        self._guarded().write({"state": "in_progress"})
        return True

    @api.model
    def _fix_next_period_end(self, company=None):
        """The month-end after the company's latest close; with no close yet,
        the month that last ended."""
        company = company or self.env.company
        latest = self.sudo().search(
            [("company_id", "=", company.id)], order="period_end desc", limit=1
        )
        if latest:
            first_of_next = fields.Date.add(latest.period_end, days=1)
            return fields.Date.end_of(first_of_next, "month")
        today = dhaka_today(self)
        return fields.Date.subtract(fields.Date.start_of(today, "month"), days=1)

    @api.model
    def action_start_period(self, period_end=None):
        """Open the close checklist of a period with its 10 SOP steps (M19-1):
        the next month-end of the company unless a date is given. Nothing is
        posted, locked or closed by this."""
        require_role(self.env, ACCOUNT_USER, "Starting a period close")
        end = fields.Date.to_date(period_end) if period_end else self._fix_next_period_end()
        company = self.env.company
        if self.sudo().search_count([("company_id", "=", company.id), ("period_end", "=", end)]):
            raise UserError("%s already has a close for %s." % (company.name, end))
        close = self.create({"period_end": end, "company_id": company.id})
        close.action_generate_standard_steps()
        return close

    def action_set_cutover_entry(self, entry=None):
        """Name the posted entry that clears the inventory suspense, by its
        number: the journal the accountant has just had approved."""
        self.ensure_one()
        require_role(self.env, ACCOUNT_USER, "Setting the suspense cutover entry")
        if self.state == "closed":
            raise UserError("The period is closed; the suspense cutover belongs to an open close.")
        number = (entry or "").strip()
        if not number:
            raise UserError("Give the number of the posted cutover journal entry.")
        move = (
            self.env["account.move"]
            .sudo()
            .search(
                [
                    ("name", "=", number),
                    ("state", "=", "posted"),
                    ("company_id", "=", self.company_id.id),
                ],
                limit=1,
            )
        )
        if not move:
            raise UserError(
                "No posted journal entry numbered %s in %s." % (number, self.company_id.name)
            )
        self.write({"cutover_move_id": move.id})
        return True

    def _fix_suspense_pending(self):
        """(entries, value) of the company's inventory suspense still waiting
        for its GL cutover, read from the suspense itself (cd_inventory, which
        depends on this module, is looked up softly)."""
        self.ensure_one()
        if "fix.inventory.valuation.suspense" not in self.env:
            return 0, 0.0
        ((count, value),) = (
            self.env["fix.inventory.valuation.suspense"]
            .sudo()
            ._read_group(
                [("status", "=", "pending_gl_cutover"), ("company_id", "=", self.company_id.id)],
                [],
                ["__count", "total_valuation:sum"],
            )
        )
        return count, round(value or 0.0, 2)

    def _fix_check_suspense_clear(self):
        """AR-006 section 5.4. `suspense_closing` is written only by the
        reconciliation, so a close that never ran it read 0 and passed with the
        suspense pending: the check is against the suspense itself."""
        self.ensure_one()
        count, value = self._fix_suspense_pending()
        if count:
            raise UserError(
                "Period %s cannot close: %d inventory suspense entries (%.2f) are still pending "
                "their GL cutover (AR-006 section 5.4). Post the cutover entry, set it on the "
                "close and reconcile the suspense." % (self.period_end, count, value)
            )

    @staticmethod
    def _fix_clearing_text(clearings) -> str:
        """G1: the price-variance legs the cutover must also carry."""
        if not clearings:
            return ""
        return ", plus the purchase-price variance cleared off the suspense to %s" % ", ".join(
            "%s %.2f (%s)" % (code, value, "debit" if value > 0 else "credit")
            for code, value in sorted(clearings.items())
        )

    def action_reconcile_inventory_suspense(self) -> dict:
        """T04: Reconcile the W2 inventory suspense entries against a REAL,
        balancing cutover journal entry.

        The cutover entry (``cutover_move_id``) must be posted, belong to the
        company, and move the suspense account(s) the entries are booked
        against by exactly the pending suspense valuation. Only then are the
        entries marked reconciled, with the entry's number as voucher. The
        closing suspense is what is STILL pending afterwards — computed, not
        written as 0. (This action used to mark every entry reconciled
        against an invented voucher "GL-CUTOVER-W2-M15-<id>" and force the
        suspense balance to zero without any journal entry.)"""
        self.ensure_one()
        require_role(self.env, ACCOUNT_USER, "Reconciling the inventory suspense")
        if self.state == "closed":
            raise UserError("The period is closed; the suspense cutover belongs to an open close.")
        suspense_model = self.env["fix.inventory.valuation.suspense"]
        domain = [
            ("status", "=", "pending_gl_cutover"),
            ("company_id", "=", self.company_id.id),
        ]
        pending_entries = suspense_model.search(domain)
        # The net stock movement (cd_inventory signs each row by its type: a
        # consumption is value consumed, i.e. stock OUT); the raw sum of the
        # rows counted an issue as stock in. Soft: cd_inventory depends on us.
        stock_effect = (
            pending_entries._fix_stock_effect_total()
            if hasattr(pending_entries, "_fix_stock_effect_total")
            else round(sum(pending_entries.mapped("total_valuation")), 2)
        )
        total_suspense = abs(stock_effect)
        # G1: rows that are not stock (a return to vendor's purchase-price
        # variance) are cleared by the same entry from the suspense account to
        # the account each names: Dr that account / Cr suspense for a positive
        # value. {code: value}; soft, cd_inventory depends on us.
        clearings = (
            pending_entries._fix_cutover_clearings()
            if hasattr(pending_entries, "_fix_cutover_clearings")
            else {}
        )
        cleared = round(sum(clearings.values()), 2)
        voucher_ref = False
        if pending_entries:
            move = self.cutover_move_id
            if not move:
                raise UserError(
                    "Post the suspense cutover journal entry (%.2f%s) and select it on the "
                    "close before reconciling the inventory suspense."
                    % (total_suspense, self._fix_clearing_text(clearings))
                )
            if move.state != "posted" or move.company_id != self.company_id:
                raise UserError(
                    "Cutover entry %s must be a POSTED entry of %s."
                    % (move.display_name, self.company_id.name)
                )
            codes = set(pending_entries.mapped("suspense_account_code"))
            Account = self.env["account.account"].with_company(self.company_id)
            accounts = Account.search(
                [*Account._check_company_domain(self.company_id), ("code", "in", list(codes))]
            )
            missing = codes - set(accounts.mapped("code"))
            if missing:
                raise UserError(
                    "Suspense account(s) %s are not in the chart of %s."
                    % (", ".join(sorted(missing)), self.company_id.name)
                )
            targets = Account.search(
                [*Account._check_company_domain(self.company_id), ("code", "in", list(clearings))]
            )
            missing = set(clearings) - set(targets.mapped("code"))
            if missing:
                raise UserError(
                    "The pending suspense clears a purchase-price variance to account(s) %s, "
                    "which are not in the chart of %s."
                    % (", ".join(sorted(missing)), self.company_id.name)
                )

            def balance(accs):
                return round(
                    sum(
                        move.line_ids.filtered(lambda line: line.account_id in accs).mapped(
                            "balance"
                        )
                    ),
                    2,
                )

            moved = balance(accounts)
            if clearings:
                # signs matter once two legs share the suspense account: stock
                # in credits it, a variance cleared out credits it too
                expected = round(-(stock_effect + cleared), 2)
                clears = round(moved - expected, 2) == 0
            else:
                expected = total_suspense
                clears = round(abs(moved) - abs(total_suspense), 2) == 0
            if not clears:
                raise UserError(
                    "Cutover entry %s moves the suspense account(s) %s by %.2f, but the "
                    "pending suspense valuation is %.2f%s — it does not clear the suspense "
                    "(expected %.2f)."
                    % (
                        move.name,
                        ", ".join(sorted(codes)),
                        moved if clearings else abs(moved),
                        total_suspense,
                        self._fix_clearing_text(clearings),
                        expected,
                    )
                )
            for code, value in sorted(clearings.items()):
                target = targets.filtered(lambda a, c=code: a.code == c)
                got = balance(target)
                if round(got - value, 2) != 0:
                    raise UserError(
                        "Cutover entry %s moves account %s by %.2f, but the pending purchase-price "
                        "variance cleared to it is %.2f (debit a loss, credit a gain) — it does "
                        "not clear the suspense." % (move.name, code, got, value)
                    )
            voucher_ref = move.name
            for entry in pending_entries:
                entry.action_reconcile_to_gl(voucher_ref)

        remaining = round(sum(suspense_model.search(domain).mapped("total_valuation")), 2)
        self._guarded().write(
            {
                "suspense_closing": remaining,
                "suspense_reconciled": remaining == 0,
                "cutover_voucher_ref": voucher_ref or self.cutover_voucher_ref,
            }
        )
        publish(
            self.env,
            "inventory.suspense.reconciled",
            "fix.period.close",
            self.id,
            {
                "company_id": self.company_id.id,
                "period_end": str(self.period_end),
                "reconciled_entries_count": len(pending_entries),
                "total_valuation_cleared": float(total_suspense),
                # G1: purchase-price variance moved off the suspense account
                "price_variance_cleared": float(cleared),
                "voucher_ref": voucher_ref or "",
                "suspense_balance": float(remaining),
            },
        )
        return {
            "reconciled_entries": len(pending_entries),
            "total_valuation": float(total_suspense),
            "voucher_ref": voucher_ref or "",
            "status": "zero_cleared" if remaining == 0 else "residual_pending",
        }

    def _fix_vat_return(self):
        """The period's Mushak 9.1 return (cd_tax_engine_bd's fix.vat.return,
        looked up softly: that module is not a dependency), or None."""
        self.ensure_one()
        if "fix.vat.return" not in self.env:
            return None
        return (
            self.env["fix.vat.return"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("period", "=", self.period_end.strftime("%Y-%m")),
                ],
                limit=1,
            )
        )

    def _fix_check_vat_return_reconciled(self, evidence_model=None, evidence_res_id=0):
        """C10: refuse unless the period's 9.1 is prepared (or filed) and its
        sub-ledger reconciliation says reconciled. A close without the VAT
        step (a hand-made checklist) is not asked. Evidence that names a
        9.1 return must name this period's."""
        self.ensure_one()
        if not self.line_ids.filtered(lambda line: line.name == VAT_CLOSE_STEP):
            return
        period = self.period_end.strftime("%Y-%m")
        company = self.company_id.sudo().name
        if "fix.vat.return" not in self.env:
            raise UserError(
                "The VAT close step of %s needs the Mushak 9.1 return of %s, and the VAT "
                "return module (cd_tax_engine_bd) is not installed (C10)." % (company, period)
            )
        ret = self._fix_vat_return()
        if evidence_model == "fix.vat.return" and evidence_res_id and evidence_res_id != ret.id:
            other = self.env["fix.vat.return"].sudo().browse(evidence_res_id)
            raise UserError(
                "Evidence fix.vat.return,%d is the Mushak 9.1 return for %s, not for %s: the "
                "VAT close step is evidenced by this period's return (C10)."
                % (evidence_res_id, other.period, period)
            )
        if not ret or ret.state == "draft":
            raise UserError(
                "The Mushak 9.1 return for %s of %s is not prepared. Prepare it and reconcile "
                "its VAT sub-ledger before the VAT close step is done (C10)." % (period, company)
            )
        if ret.subledger_status != "reconciled":
            status = dict(ret._fields["subledger_status"].selection).get(
                ret.subledger_status, ret.subledger_status
            )
            raise UserError(
                "The Mushak 9.1 return for %s of %s is not reconciled (sub-ledger status: %s; "
                "output variance %.2f, input variance %.2f). Clear the variance and reconcile "
                "again before the VAT close step is done (C10)."
                % (
                    period,
                    company,
                    status,
                    ret.subledger_output_variance or 0.0,
                    ret.subledger_input_variance or 0.0,
                )
            )

    def action_ready(self):
        require_role(self.env, ACCOUNT_USER, "The close ready check")
        for close in self:
            if close.state not in ("open", "in_progress"):
                raise UserError("Only an open close in progress can be checked ready.")
            if not close.line_ids:
                raise UserError(
                    "Generate the close steps first; a close with no steps is not ready."
                )
            blocking = close.line_ids.filtered(lambda line: line.blocking and line.state != "done")
            if blocking:
                raise UserError("Close steps still open: %s" % ", ".join(blocking.mapped("name")))
            close._fix_check_suspense_clear()
            close._fix_check_vat_return_reconciled()
            if close.suspense_closing:
                raise UserError(
                    "Suspense account must be zero at close (AR-006 §5.4) — "
                    "balance: %.2f" % close.suspense_closing
                )
            close._guarded().write({"state": "ready_to_close", "ready_by_id": self.env.uid})

    def _fix_check_bank_reconciled(self):
        """M50-6 / BRU-TRE-19: no close while imported bank statement lines up
        to the period end are unmatched. The treasury model (cd_cash_position,
        which depends on cd_gl_ext) is looked up softly."""
        self.ensure_one()
        if "fix.bank.statement.line" not in self.env:
            return
        Line = self.env["fix.bank.statement.line"]
        if not hasattr(Line, "_fix_reconciliation_blockers"):
            return
        blockers = Line._fix_reconciliation_blockers(self.company_id, self.period_end)
        if blockers:
            raise UserError(
                "Period %s cannot close: %d imported bank statement line(s) up to the period end "
                "are unmatched (%s). Reconcile them in Treasury first (BRU-TRE-19)."
                % (
                    self.period_end,
                    len(blockers),
                    ", ".join(str(b.display_name) for b in blockers[:5]),
                )
            )

    def _fix_set_company_lock(self):
        """Move the company Global Lock Date forward to this period end. Odoo's
        own lock validation (unreconciled statement lines, unhashed entries)
        refuses it and so blocks the close: the close and the lock are one act."""
        self.ensure_one()
        company = self.company_id.sudo()
        if not company.fiscalyear_lock_date or company.fiscalyear_lock_date < self.period_end:
            company.with_context(**{FISCAL_LOCK_KEY: _FISCAL_LOCK_TOKEN}).write(
                {"fiscalyear_lock_date": self.period_end}
            )
        return company.fiscalyear_lock_date

    def action_close(self):
        """Hard-close the period (FR-FIN-019, BRU-FIN-05/06): an Accounting
        Administrator closes a period that has ENDED, after the ready check;
        the company lock date is set in the same transaction, so a later
        posting dated in the period is refused (manual) or lands in the open
        period (sub-ledger)."""
        require_role(self.env, ACCOUNT_MANAGER, "Closing a period")
        today = dhaka_today(self)
        for close in self:
            if close.state != "ready_to_close":
                raise UserError("Run the ready check before closing")
            close._fix_check_suspense_clear()
            if close.period_end >= today:
                raise UserError(
                    "Period %s has not ended (today is %s): a period closes after its last day."
                    % (close.period_end, today)
                )
            close._fix_check_bank_reconciled()
            close._fix_check_vat_return_reconciled()
            lock = close._fix_set_company_lock()
            close._guarded().write(
                {
                    "state": "closed",
                    "closed_at": fields.Datetime.now(),
                    "closed_by_id": self.env.uid,
                    "lock_date_set": lock,
                }
            )
            close.message_post(
                body="Period %s closed by %s; company Global Lock Date %s."
                % (close.period_end, self.env.user.name, lock)
            )
            publish(
                close.env,
                "period.closed",
                "fix.period.close",
                close.id,
                {
                    "company_id": close.company_id.id,
                    "period_end": str(close.period_end),
                    "duration_days": close.close_duration_days,
                    "sla_status": close.sla_status,
                    "step_count": len(close.line_ids),
                },
            )
            target_days = getattr(close, "CLOSE_TARGET_DAYS", getattr(self, "CLOSE_TARGET_DAYS", 5))
            if close.close_duration_days > target_days:
                _logger.warning(
                    "P06 G3-04 breach: close took %.1f days (target %d)",
                    close.close_duration_days,
                    target_days,
                )

    def action_request_reopen(self, user_id=None, reason=None, end_datetime=None):
        """Raise a time-boxed reopen (lock exception) for one user; an
        Accounting Administrator other than the closer approves it. From the
        workspace row action: for the requester, for the longest window allowed
        (the reopen form names another user or a shorter window)."""
        from .fix_gl_posting_control import (
            DEFAULT_REOPEN_MAX_DAYS,
            PARAM_REOPEN_MAX_DAYS,
            float_param,
        )

        self.ensure_one()
        if not (reason or "").strip():
            raise UserError("A reopen states its reason.")
        if not end_datetime:
            days = float_param(self.env, PARAM_REOPEN_MAX_DAYS, DEFAULT_REOPEN_MAX_DAYS)
            end_datetime = fields.Datetime.now() + timedelta(days=days)
        reopen = self.env["fix.period.reopen"].create(
            {
                "close_id": self.id,
                "user_id": int(user_id) if user_id else self.env.uid,
                "reason": reason,
                "end_datetime": end_datetime,
            }
        )
        reopen.action_submit()
        return reopen

    def action_fail_close_target(self):
        """Report-only helper for the G3 gate: which closes exceeded 5 days."""
        return self.search_read(
            [("state", "=", "closed"), ("close_duration_days", ">", self.CLOSE_TARGET_DAYS)],
            ["period_end", "close_duration_days", "sla_status"],
        )


# Company lock writes made by the close itself (fix_gl_posting_control's
# res.company guard lets these through).
FISCAL_LOCK_KEY = "fix_m19_close_lock"
_FISCAL_LOCK_TOKEN = object()


def has_fiscal_lock_token(env) -> bool:
    return env.context.get(FISCAL_LOCK_KEY) is _FISCAL_LOCK_TOKEN


class FixPeriodCloseLine(models.Model):
    """One step of the close checklist with its owner and day-offset target.

    The step is completed by a holder of its owning group, on evidence that
    points at a real record (``model,id``), a posted entry number, or a file
    attached to the step."""

    _name = "fix.period.close.line"
    _description = "Period Close Step"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "close_id, sequence"

    close_id = fields.Many2one("fix.period.close", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Step", required=True)
    owner_role = fields.Char(string="Owning Role", help="R-nn role accountable for this step")
    owner_group_id = fields.Many2one(
        "res.groups",
        string="Owning Group",
        help="Only a holder of this group completes the step.",
    )
    target_day = fields.Integer(string="Target Day", help="Day offset from period end (0..5)")
    blocking = fields.Boolean(
        default=True, help="A blocking step must clear before the period can close"
    )
    state = fields.Selection(
        [("pending", "Pending"), ("in_progress", "In Progress"), ("done", "Done")],
        default="pending",
        required=True,
    )
    evidence_ref = fields.Char(
        string="Evidence Reference", help="Report ID or reconciliation record proving the step"
    )
    evidence_model = fields.Char(string="Evidence Model", readonly=True)
    evidence_res_id = fields.Integer(string="Evidence Record", readonly=True)
    done_by_id = fields.Many2one("res.users", string="Done By", readonly=True, copy=False)
    done_at = fields.Datetime(string="Done At", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "evidence_ref",
            "evidence_model",
            "evidence_res_id",
            "done_by_id",
            "done_at",
            "owner_group_id",
            "owner_role",
            "blocking",
        }

    @api.constrains("state", "evidence_ref")
    def _check_done_has_evidence(self):
        for line in self:
            if line.state == "done" and not (line.evidence_ref or "").strip():
                raise ValidationError(
                    "Close step '%s' cannot be done without an evidence reference "
                    "(report ID or reconciliation record)." % line.name
                )

    def _check_owner(self):
        """The acting user must hold the step's owning group. Records are read
        as the system: a step owner outside finance (the supply chain lead)
        has no access to the close itself."""
        user = self.env.user
        for line in self.sudo():
            if line.close_id.state == "closed":
                raise UserError("The period is closed; its steps are frozen.")
            if self.env.su:
                continue
            # A step nobody owns is not everybody's: it falls to the
            # Accounting Administrator.
            group = line.owner_group_id or self.env.ref(ACCOUNT_MANAGER).sudo()
            if not holds_group(user, group):
                raise AccessError(
                    "Close step '%s' is owned by %s (%s); you do not hold that role."
                    % (line.name, line.owner_role or "its owner", group.name)
                )

    def _resolve_evidence(self, evidence, trusted=False):
        """(model, res_id) of the record the evidence names, or refuse."""
        self.ensure_one()
        text = (evidence or "").strip()
        for sep in (",", ":"):
            if sep in text:
                model, _sep, rid = text.partition(sep)
                model, rid = model.strip(), rid.strip()
                if model in EVIDENCE_MODELS and model in self.env and rid.isdigit():
                    record = self.env[model].sudo().browse(int(rid)).exists()
                    if record:
                        if (
                            "company_id" in record._fields
                            and record.company_id
                            and (record.company_id != self.close_id.company_id)
                        ):
                            break
                        return model, record.id
                break
        company = self.close_id.company_id
        move = (
            self.env["account.move"]
            .sudo()
            .search(
                [("name", "=", text), ("state", "=", "posted"), ("company_id", "=", company.id)],
                limit=1,
            )
        )
        if move:
            return "account.move", move.id
        attachment = (
            self.env["ir.attachment"]
            .sudo()
            .search(
                [("res_model", "=", self._name), ("res_id", "=", self.id), ("name", "=", text)],
                limit=1,
            )
        )
        if attachment:
            return "ir.attachment", attachment.id
        if trusted:
            # trusted code (seeds, migrations) records a free-text reference
            return False, 0
        raise UserError(
            "Evidence '%s' names no record. Give a posted entry number, a file attached to the "
            "step, or a record reference such as 'account.bank.statement,42'." % text
        )

    def action_mark_done(self, evidence: str = ""):
        """Complete a close step on real evidence, by the step's owner. There
        is no default: the step used to be marked done with the evidence
        "VERIFIED" whenever none was given, and later with any string."""
        evidence = (evidence or "").strip()
        if not evidence:
            raise UserError(
                "Provide the evidence reference (report ID / reconciliation record) "
                "proving the close step before marking it done."
            )
        self._check_owner()
        uid, trusted = self.env.uid, self.env.su
        for line in self.sudo():
            model, res_id = line._resolve_evidence(evidence, trusted=trusted)
            if line.name == VAT_CLOSE_STEP:
                # C10: not on any evidence - on the period's reconciled 9.1
                line.close_id._fix_check_vat_return_reconciled(model, res_id)
            line._guarded().write(
                {
                    "state": "done",
                    "evidence_ref": evidence,
                    "evidence_model": model,
                    "evidence_res_id": res_id,
                    "done_by_id": uid,
                    "done_at": fields.Datetime.now(),
                }
            )
        return True

    def write(self, vals):
        # C10: the VAT rule hangs on the step's name; a standard step keeps it.
        if "name" in vals and not self._fix_guard_open():
            renamed = self.filtered(
                lambda line: line.name in STANDARD_STEP_NAMES and line.name != vals["name"]
            )
            if renamed:
                raise UserError(
                    "'%s' is a standard close step (SOP SP-020); its name is fixed."
                    % renamed[0].name
                )
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open() and self.filtered(
            lambda line: line.name in STANDARD_STEP_NAMES
        ):
            raise UserError("A standard close step (SOP SP-020) is not deleted from a close.")
        return super().unlink()

    def action_set_state(self, new_state: str):
        """Move a step between pending and in progress. Done is reached only
        through action_mark_done (with evidence)."""
        if new_state not in ("pending", "in_progress", "done"):
            raise UserError(f"Invalid state: {new_state}")
        if new_state == "done":
            raise UserError(
                "A step is completed with its evidence (Mark Done), not by a state change."
            )
        self._check_owner()
        self.sudo()._guarded().write(
            {
                "state": new_state,
                "evidence_ref": False,
                "evidence_model": False,
                "evidence_res_id": 0,
                "done_by_id": False,
                "done_at": False,
            }
        )
        return True


class FixFixedAssetSeam(models.Model):
    """The fixed-asset seam M49 extends in Phase 8 (T07).

    Deliberately minimal: the capitalisation interface the asset register
    will plug into. Finance posts capitalisation events; M49 consumes and
    owns depreciation. No depreciation logic here — the seam, not the asset
    module."""

    _name = "fix.fixed.asset.seam"
    _description = "Fixed Asset Seam (M49 interface)"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(string="Capitalisation Reference", required=True)
    move_line_id = fields.Many2one(
        "account.move.line", string="Journal Item", required=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(
        string="Capitalised Amount", currency_field="currency_id", required=True
    )
    asset_category = fields.Char(string="Asset Category", help="From the MD-* finance master data")
    consumed = fields.Boolean(
        default=False, readonly=True, help="True once M49 has created the asset register entry"
    )

    def action_mark_consumed(self):
        """Called by M49 (Phase 8) when the asset record exists. Idempotent."""
        self.write({"consumed": True})


def _chart_map_for_company(env, company_id):
    """statutory accounts of the company linked to Odoo accounts, keyed by
    Odoo account id — the COA unification lookup (FR-FIN-002). Archived
    accounts keep their link: posting to one must still be refused."""
    chart = (
        env["fix.chart.account"]
        .sudo()
        .with_context(active_test=False)
        .search([("company_id", "=", company_id), ("odoo_account_id", "!=", False)])
    )
    return {c.odoo_account_id.id: c for c in chart}


def _default_dimension(env, company, dimension):
    """The configured sub-ledger default for one MD-035 dimension, or False."""
    icp = env["ir.config_parameter"].sudo()
    if dimension == "branch":
        code = icp.get_param("cd_gl_ext.default_branch_code")
        if not code or "fix.branch" not in env:
            return False
        return (
            env["fix.branch"]
            .sudo()
            .search([("code", "=", code), ("company_id", "in", (company.id, False))], limit=1)
            .id
            or False
        )
    return icp.get_param("cd_gl_ext.default_%s" % dimension) or False


def _fill_subledger_dimensions(env, move, dimension_by_line, source):
    """MD-035 requires a branch or cost centre on bank, VAT, TDS and other
    accounts. A person posting a manual journal states them, but the automated
    sub-ledgers (AP, treasury, tax, settlements) have no one to ask: a payment
    from the head-office bank belongs to no service branch. Without this every
    such posting was refused once the chart was linked, so no bill could be paid.

    So a sub-ledger line takes the company default for a dimension the chart
    requires and the caller did not give. Manual and API journals never do, and
    with no default configured the COA-03 refusal stands. Returns the filled map."""
    if source in PERSON_STATES_DIMENSIONS:
        return dimension_by_line
    chart_map = _chart_map_for_company(env, move.company_id.id)
    if not chart_map:
        return dimension_by_line
    filled = dict(dimension_by_line or {})
    for idx, line in enumerate(move.line_ids):
        chart_account = chart_map.get(line.account_id.id)
        if not chart_account:
            continue
        dims = dict(filled.get(idx) or {})
        changed = False
        for dimension in _split_dims(chart_account.requires_dimension):
            key = "branch_id" if dimension == "branch" else dimension
            if dims.get(key) or dims.get(dimension):
                continue
            value = _default_dimension(env, move.company_id, dimension)
            if value:
                dims[key] = value
                changed = True
        if changed:
            filled[idx] = dims
    return filled


def _validate_move_against_chart(env, move, dimension_by_line, source):
    """FR-FIN-011: enforce the MD-035 posting rules on every line whose
    Odoo account is linked to the statutory chart — COA-01 (postable leaf),
    COA-02 (no direct manual posting on control accounts), COA-03 (required
    dimensions present) and the archived-account guard.

    Lines on UNMAPPED accounts get no statutory check: the chart links
    progressively (fix.chart.loader.action_link_odoo_accounts), and the
    platform must post on the generic Odoo chart meanwhile."""
    chart_map = _chart_map_for_company(env, move.company_id.id)
    if not chart_map:
        return
    is_direct_manual = source in MANUAL_POSTING_SOURCES
    for idx, line in enumerate(move.line_ids):
        chart_account = chart_map.get(line.account_id.id)
        if not chart_account:
            continue
        if not chart_account.active:
            raise UserError(
                "Posting refused: %s is archived in the statutory chart (%s)"
                % (line.account_id.display_name, chart_account.account_code)
            )
        dims = dict(dimension_by_line.get(idx) or {})
        dim_vals = {
            "branch": dims.get("branch_id") or dims.get("branch"),
            "cost_centre": dims.get("cost_centre"),
            "business_line": dims.get("business_line"),
            "project": dims.get("project_ref"),
            "brand": dims.get("brand"),
            "channel": dims.get("channel"),
        }
        record = coa_logic.AccountRecord(
            account_code=chart_account.account_code,
            entity_code="EN-01",
            account_name=chart_account.name,
            account_type=chart_account.account_type,
            account_subtype=chart_account.account_subtype or "",
            is_postable=chart_account.is_postable,
            is_control_account=chart_account.is_control_account,
            control_subledger=chart_account.control_subledger or None,
            requires_dimension=_split_dims(chart_account.requires_dimension),
            statutory_group=chart_account.statutory_group or "",
            active=chart_account.active,
        )
        try:
            coa_logic.validate_posting_attempt(
                record, dim_vals, is_direct_manual_post=is_direct_manual
            )
        except coa_logic.CoaValidationError as exc:
            raise UserError(
                "Posting refused on %s (%s): %s"
                % (line.account_id.display_name, chart_account.account_code, exc)
            ) from exc


def _attach_dimensions(env, move, dimension_by_line):
    """Create the fix.journal.dimension rows for every annotated line.
    Returns the dimension recordset (empty when nothing was annotated)."""
    dimension_model = env["fix.journal.dimension"]
    dimensions = dimension_model
    for idx, line in enumerate(move.line_ids):
        dim_vals = dict(dimension_by_line.get(idx) or {})
        # An all-falsy annotation (branch False, cost_centre False...) is no
        # annotation at all — no empty dimension rows ride the entry. A line
        # that names the operating unit key IS annotated even when its value
        # is empty: it gets the company's OU below (AS-03, every posting
        # carries one; e.g. a payroll period without its own unit).
        if not dim_vals or ("operating_unit_id" not in dim_vals and not any(dim_vals.values())):
            continue
        # A missing/empty OU falls back to the MOVE's company OU — never
        # another company's (the dimension is the multi-entity ledger key).
        operating_unit_id = dim_vals.get("operating_unit_id") or (
            env["operating.unit"].search([("company_id", "=", move.company_id.id)], limit=1).id
        )
        if not operating_unit_id:
            raise UserError(
                "Company %s has no operating unit — every posting carries one (AS-03)"
                % move.company_id.name
            )
        dimensions |= dimension_model.create(
            {
                "move_line_id": line.id,
                "company_id": move.company_id.id,
                "operating_unit_id": operating_unit_id,
                "branch_id": dim_vals.get("branch_id", False),
                "cost_centre": dim_vals.get("cost_centre", False),
                "business_line": dim_vals.get("business_line", False),
                "project_ref": dim_vals.get("project_ref", False),
                "brand": dim_vals.get("brand", False),
                "channel": dim_vals.get("channel", False),
            }
        )
    return dimensions


def _log_posting(
    env, move, source, requested_by, template, state="posted", source_ref=None, posted_by=None
):
    """Append the immutable posting-log row (FR-FIN-042). Created sudo: the
    audit trail must never be the reason a posting fails on permissions."""
    poster = posted_by or getattr(env, "uid", None)
    return (
        env["fix.journal.posting.log"]
        .with_context(force_edit=True)
        .sudo()
        .create(
            {
                "company_id": move.company_id.id,
                "move_id": move.id,
                "move_name": move.name or "",
                "source": source,
                "source_ref": source_ref or False,
                "state": state,
                "requested_by": requested_by or getattr(env, "uid", None),
                "posted_by": poster if state == "posted" else False,
                "posted_at": fields.Datetime.now() if state == "posted" else False,
                "template_id": template.id if template else False,
                "currency_id": move.currency_id.id,
                "amount": move.amount_total,
            }
        )
    )


def _publish_posted(env, move, source):
    publish(
        env,
        "journal.posted",
        "account.move",
        move.id,
        {
            "company_id": move.company_id.id,
            "amount": float(move.amount_total),
            "currency": move.currency_id.name,
            "line_count": len(move.line_ids),
            "source": source,
        },
    )


# Sources that count as DIRECT manual postings for the COA-02 control-account
# rule. Engine/subledger sources (settlement, suspense, platform API seams)
# may legitimately post on control accounts.
MANUAL_POSTING_SOURCES = ("manual", "template", "allocation")
# A person states these dimensions: on the journal, or on the template's lines. "api"
# is a caller that must pass its own. An allocation is split by a rule, with no one
# to ask, so it takes the default for a dimension its rule leaves blank.
PERSON_STATES_DIMENSIONS = ("manual", "template", "api")


def _m19_post(env, moves, source):
    """Post `moves` through the guarded account.move._post with the M19
    token. Manual-style sources are refused on a closed period (no silent
    re-date); sub-ledger sources follow Odoo's lock behaviour."""
    moves.with_env(env).with_context(**m19_context(source))._post(soft=False)


def post_with_dimensions(
    env, move_vals, dimension_by_line, source="api", template=None, source_ref=None
):
    """THE M19 posting API (T03/T09, A08 S2). Post an account.move and attach
    the 7-dimension tags to every line in the SAME transaction, append the
    immutable posting-log row and emit journal.posted.

    dimension_by_line: {line_index: {"branch_id": int, "cost_centre": str,
    "business_line": str, "project_ref": str, "brand": str, "channel": str}}.
    FR-FIN-011: lines on accounts linked to the statutory chart are checked
    against the MD-035 posting rules before anything posts. `source` is a
    fix.journal.posting.log source; "manual" is refused here (a manual
    journal is drafted by create_journal_entry_draft and posted by its
    approval). Returns (move, dimensions)."""
    if source == "manual" and not env.su:
        raise UserError(
            "A manual journal entry is drafted for review (create_journal_entry_draft) and "
            "posted by its approver; it cannot be posted directly (BRU-FIN-11)."
        )
    move = env["account.move"].create(move_vals)
    dimension_by_line = _fill_subledger_dimensions(env, move, dimension_by_line or {}, source)
    _validate_move_against_chart(env, move, dimension_by_line, source)
    _m19_post(env, move, source)
    dimensions = _attach_dimensions(env, move, dimension_by_line)
    _publish_posted(env, move, source)
    _log_posting(
        env,
        move,
        source,
        getattr(env, "uid", None),
        template,
        state="posted",
        source_ref=source_ref,
    )
    return move, dimensions


def post_existing_moves(env, moves, source="api", source_ref=None, dimension_by_line=None):
    """The M19 posting API for sub-ledgers that build a DRAFT move first
    (depreciation runs, impairments, lease charges...): validate against the
    chart, post with the token, log and publish each. Returns the moves."""
    if source == "manual" and not env.su:
        raise UserError(
            "A manual journal entry is posted by its approver through the M19 maker-checker."
        )
    for move in moves.with_env(env):
        if move.state != "draft":
            raise UserError("%s is not a draft entry." % move.display_name)
        line_dims = _fill_subledger_dimensions(env, move, dimension_by_line or {}, source)
        _validate_move_against_chart(env, move, line_dims, source)
        _m19_post(env, move, source)
        if line_dims:
            _attach_dimensions(env, move, line_dims)
        _publish_posted(env, move, source)
        _log_posting(env, move, source, getattr(env, "uid", None), None, source_ref=source_ref)
    return moves


def _move_snapshot(move) -> str:
    """What a journal approval covers: date, journal and every line."""
    import json

    move = move.sudo()
    lines = sorted(
        (
            line.account_id.id,
            line.partner_id.id or 0,
            line.currency_id.id or 0,
            round(line.debit, 2),
            round(line.credit, 2),
            round(line.amount_currency, 2),
        )
        for line in move.line_ids
    )
    return json.dumps(
        {
            "date": str(move.date),
            "journal": move.journal_id.id,
            "company": move.company_id.id,
            "lines": lines,
        },
        sort_keys=True,
    )


def create_journal_entry_draft(
    env, move_vals, dimension_by_line, source="manual", template=None, reason=None
):
    """Maker step of the JE review flow (FR-FIN-014/015, AUT-FIN-14): create
    the entry as a DRAFT with its COA rules checked and its dimensions
    attached, queue it in the posting log as awaiting review, and route its
    fix.journal.approval to a DOFA-tier Accounting Administrator who is not
    the preparer. The approver posts it through approve_journal_entry (or
    from the M63 inbox)."""
    require_role(env, ACCOUNT_USER, "Drafting a manual journal entry")
    move_vals = dict(move_vals)
    move_vals.setdefault("move_type", "entry")
    if move_vals.get("move_type") != "entry":
        raise UserError("A manual journal is a journal entry (move_type 'entry').")
    move = env["account.move"].create(move_vals)
    _validate_move_against_chart(env, move, dimension_by_line or {}, source)
    move._fix_check_not_in_closed_period()
    _attach_dimensions(env, move, dimension_by_line or {})
    log = _log_posting(env, move, source, getattr(env, "uid", None), template, state="requested")
    approval = (
        env["fix.journal.approval"]
        ._guarded()
        .create(
            {
                "move_id": move.id,
                "company_id": move.company_id.id,
                "source": source,
                "reason": reason or move.ref or False,
                "log_id": log.id,
            }
        )
    )
    approval.action_request_approval(justification=reason or move.ref or None)
    return move, log


def _dimensions_of_move(env, move) -> dict:
    """The dimension rows already on a draft, as the COA rules read them."""
    rows = env["fix.journal.dimension"].sudo().search([("move_line_id", "in", move.line_ids.ids)])
    by_line = {row.move_line_id.id: row for row in rows}
    out = {}
    for idx, line in enumerate(move.line_ids):
        row = by_line.get(line.id)
        if row:
            out[idx] = {
                "branch_id": row.branch_id.id,
                "cost_centre": row.cost_centre,
                "business_line": row.business_line,
                "project_ref": row.project_ref,
                "brand": row.brand,
                "channel": row.channel,
            }
    return out


def _check_reviewable_draft(env, move, what):
    require_role(env, ACCOUNT_USER, what)
    move.check_access("read")
    if move.state != "draft":
        raise UserError("%s is %s, not a draft entry." % (move.display_name, move.state))
    if not move._fix_is_manual_entry():
        raise UserError(
            "%s is not a manual journal entry; its own sub-ledger posts it." % move.display_name
        )


def _fill_left_behind_dimensions(env, move):
    """A draft raised through the M19 API always has its dimensions: the chart is
    checked as it is created. One with none was left behind by a sub-ledger (the
    live RDEP rental-deposit drafts) and the screen has nowhere to add them, so it
    could never be routed. Such a line takes the sub-ledger default. The entry says
    so, and the approver sees the dimensions on the entry before deciding."""
    dims = _dimensions_of_move(env, move)
    filled = _fill_subledger_dimensions(env, move, dims, "subledger_left_behind")
    new = {idx: vals for idx, vals in filled.items() if vals != dims.get(idx)}
    if not new:
        return
    existing = (
        env["fix.journal.dimension"].sudo().search([("move_line_id", "in", move.line_ids.ids)])
    )
    lines = list(move.line_ids)
    for idx, vals in new.items():
        row = existing.filtered(lambda d, line=lines[idx]: d.move_line_id == line)
        if row:
            row.write(
                {
                    key: vals[key]
                    for key in ("branch_id", "cost_centre", "business_line")
                    if vals.get(key) and not row[key]
                }
            )
    first_time = {
        idx: vals
        for idx, vals in new.items()
        if not existing.filtered(lambda d, line=lines[idx]: d.move_line_id == line)
    }
    if first_time:
        _attach_dimensions(env(su=True), move, first_time)
    move.sudo().message_post(
        body="Dimensions the statutory chart requires were missing on this left-behind draft; "
        "the company defaults were applied when it was routed. Review them before approving."
    )


def route_journal_entry(env, move, reason=None):
    """Send a draft entry for review (M19-2). Three drafts need this: one with
    no approval yet (raised before the maker-checker existed, or by a sub-ledger
    that left it behind), one whose approval was rejected or voided, and one
    edited after it was routed, whose approval no longer covers it. The approval
    is requested again and the usual checks apply; everyone who prepared it or
    requested it in any round stays excluded."""
    move = move.with_env(env)
    move.ensure_one()
    _check_reviewable_draft(env, move, "Routing a manual journal entry")
    reason = (reason or "").strip() or (move.ref or "").strip()
    if not reason:
        raise UserError("State the reason / narrative of the manual journal (BRU-FIN-16).")
    _fill_left_behind_dimensions(env, move)
    _validate_move_against_chart(env, move, _dimensions_of_move(env, move), "manual")
    move._fix_check_not_in_closed_period()
    Approval = env["fix.journal.approval"]
    approval = Approval.sudo().search([("move_id", "=", move.id)], limit=1).with_env(env)
    if approval.state == "posted":
        raise UserError("%s was already approved and posted." % move.display_name)
    if approval.state == "pending":
        if approval.sudo().lines_snapshot == _move_snapshot(move):
            raise UserError("%s is already awaiting approval." % move.display_name)
        approval._fix_void("the entry changed after it was routed for approval")
    log = approval.sudo().log_id
    if not log or log.state != "requested":
        log = _log_posting(env, move, "manual", env.uid, None, state="requested")
    if approval:
        approval._guarded().write({"reason": reason, "log_id": log.id})
    else:
        approval = Approval._guarded().create(
            {
                "move_id": move.id,
                "company_id": move.company_id.id,
                "source": "manual",
                "reason": reason,
                "log_id": log.id,
            }
        )
    approval.action_request_approval(justification=reason)
    return approval


def discard_journal_entry(env, move, reason=None):
    """Withdraw a draft entry that will not be posted: rejected and not worth
    correcting, or left behind by a failed run. It is cancelled, never deleted,
    by its preparer or an Accounting Administrator; its approval and its row in
    the posting log say so."""
    move = move.with_env(env)
    move.ensure_one()
    _check_reviewable_draft(env, move, "Discarding a manual journal entry")
    reason = (reason or "").strip()
    if not reason:
        raise UserError("State why the entry is discarded.")
    approval = env["fix.journal.approval"].sudo().search([("move_id", "=", move.id)], limit=1)
    preparers = move.sudo().create_uid | approval.requested_by_id
    if env.uid not in preparers.ids and not has_role(env, ACCOUNT_MANAGER):
        raise AccessError(
            "%s is discarded by its preparer or an Accounting Administrator." % move.display_name
        )
    if approval:
        approval._fix_void("discarded by %s: %s" % (env.user.name, reason))
        if approval.log_id.state == "requested":
            approval.log_id.with_context(force_edit=True).write(
                {"state": "discarded", "note": reason[:200]}
            )
    move.button_cancel()
    move.sudo().message_post(body="Draft discarded by %s: %s" % (env.user.name, reason))
    return move


def approve_journal_entry(env, move, dimension_by_line=None):
    """Checker step of the JE review flow. The entry must have been drafted
    through create_journal_entry_draft (an entry with no approval cannot be
    approved by anyone — A08 M19-2/J04); the checker decides the routed
    approval task assigned to them, and the approval's own checks apply: the
    Accounting Administrator group, the DOFA tier of the amount, a different
    person from the preparer, and the entry unchanged since it was routed."""
    approval = env["fix.journal.approval"].sudo().search([("move_id", "=", move.id)], limit=1)
    if not approval:
        raise UserError(
            "Entry %s was not drafted through the M19 maker-checker; it has no approval to "
            "decide. Route it for approval first." % (move.display_name,)
        )
    if env.su:
        approval.with_env(env)._fix_post_approved(system=True)
    else:
        if not env.user.has_group(ACCOUNT_MANAGER):
            raise UserError(
                "Only the accounting manager group may approve journal entries (FR-FIN-015)."
            )
        task = (
            env["fix.workflow.task"]
            .sudo()
            .search(
                [
                    ("request_id", "=", approval.approval_request_id.id),
                    ("state", "=", "pending"),
                    ("assigned_user_id", "=", env.uid),
                ],
                limit=1,
            )
            if approval.approval_request_id
            else env["fix.workflow.task"]
        )
        if not task:
            raise UserError(
                "Entry %s is not awaiting your approval: it is routed to the DOFA-tier "
                "Accounting Administrators other than its preparer (segregation of duties, "
                "FR-FIN-015)." % (move.display_name,)
            )
        task.with_env(env).action_approve()
    dimensions = env["fix.journal.dimension"]
    if dimension_by_line:
        existing = env["fix.journal.dimension"].search([("move_line_id", "in", move.line_ids.ids)])
        dimensions = existing | _attach_dimensions(env, move, dimension_by_line)
    return move, dimensions
