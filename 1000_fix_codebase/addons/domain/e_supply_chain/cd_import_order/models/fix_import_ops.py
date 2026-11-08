# fix_import_ops — M44: proforma invoices, letters of credit (with amendments
# and payments) and LCA, the HS tariff master and HS classification, IRC
# eligibility, shipping documents, arrivals, bills of entry with the duty
# cascade, and landed-cost sheets. The import order lives in fix_import_order.py.
#
# A06 workflow audit (2026-11-03), M44-1..15. Every state, approval, evidence
# and stamp field is guarded (fix.guarded.mixin): it changes only through its
# action, which checks the role and the segregation of duties from env.user.
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.addons.cd_entity_config.models.fix_dofa import TIER_GROUP
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Domain

from libs.py.fix_events import publish

from .fix_import_common import (
    APPROVER,
    FINANCE,
    FORMULA_VERSION,
    OFFICER,
    PARAM_BOE_DOCS,
    PARAM_BOE_REMITTANCE_DAYS,
    PARAM_DUTY_VARIANCE,
    PARAM_IRC_WARNING_DAYS,
    PARAM_LANDING_CHARGE,
    PARAM_LC_LADDER,
    PARAM_LC_REQUIRES_FACILITY,
    PARAM_LC_REQUIRES_LCA,
    PARAM_LC_TOLERANCE,
    PARAM_PROFORMA_TOLERANCE,
    alert_users,
    changes,
    import_account,
    import_journal,
    param,
    param_bool,
    param_float,
    post_import_move,
    refuse_locked,
    require_group,
    require_other_person,
    schedule_alert,
    today,
)

_DUTY_FIELDS = ("cd_amount", "rd_amount", "sd_amount", "vat_amount", "at_amount", "ait_amount")
_RATE_FIELDS = ("cd_pct", "rd_pct", "sd_pct", "vat_pct", "at_pct", "ait_pct")
# An HS heading: 4 digits, then up to three 2-digit groups (8524.11.00), or
# the same digits unpunctuated (85241100).
HS_CODE_RE = re.compile(r"^\d{4}(\.\d{2}){0,3}$|^\d{4}(\d{2}){0,3}$")
RATE_CEILING = 1000.0  # a sanity bound, not a statutory rate


def _hs_digits(code):
    return re.sub(r"\D", "", code or "")


def _check_hs_code(code):
    if not HS_CODE_RE.match((code or "").strip()):
        raise ValidationError(
            "HS code %r is not a tariff heading: use 4 digits and up to three 2-digit "
            "groups, e.g. 8524.11.00." % code
        )


def _typed_date(value, what):
    """A date typed into a prompt: a clear refusal, not a server error."""
    try:
        return fields.Date.to_date(str(value).strip())
    except ValueError as exc:
        raise UserError("%s: %r is not a date (use YYYY-MM-DD)." % (what, value)) from exc


def _seq(env, code, fallback):
    return env["ir.sequence"].sudo().next_by_code(code) or fallback


def _order_rel(string="Import Order"):
    return fields.Many2one(
        "fix.import.order", string=string, required=True, ondelete="cascade", index=True
    )


def _company_rel(path):
    return fields.Many2one(related=path + ".company_id", store=True, index=True, string="Company")


def _ou_rel(path):
    return fields.Many2one(
        related=path + ".operating_unit_id", store=True, index=True, string="Operating Unit"
    )


# =============================================================== proforma
class FixImportProforma(models.Model):
    _name = "fix.import.proforma"
    _rec_name = "proforma_no"
    _description = "Proforma Invoice"
    _order = "issued_on desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    order_id = _order_rel()
    company_id = _company_rel("order_id")
    operating_unit_id = _ou_rel("order_id")
    proforma_no = fields.Char(string="Proforma No", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    issued_on = fields.Date(required=True, default=fields.Date.context_today)
    valid_until = fields.Date()
    state = fields.Selection(
        [("received", "Received"), ("approved", "Approved"), ("rejected", "Rejected")],
        required=True,
        default="received",
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Datetime(string="Decided On", readonly=True, copy=False)
    rejection_reason = fields.Char(readonly=True, copy=False)

    _PINNED = ("order_id", "proforma_no", "currency_id", "amount", "issued_on", "valid_until")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "decided_by_id",
            "decided_on",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state in ("approved", "rejected"):
            locked |= set(self._PINNED)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.proforma", "IPF/New")
        return super().create(vals_list)

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._PINNED) if r.state in ("approved", "rejected") else set(),
            "a decided proforma is final; record a new proforma instead.",
        )
        return super().write(vals)

    def action_approve(self):
        """FR-ITC-002 / BRU-ITC-03: an Import Approver who did not record it
        confirms a proforma that reconciles to the order, under a valid IRC."""
        require_group(self.env, APPROVER, "Approving a proforma invoice")
        tol = param_float(self.env, PARAM_PROFORMA_TOLERANCE, 0.0)
        for rec in self:
            if rec.state != "received":
                raise UserError("Approve a received proforma (this one is %s)." % rec.state)
            require_other_person(rec.env, rec, "Proforma %s" % rec.proforma_no)
            order = rec.order_id
            if not order.line_ids:
                raise UserError(
                    "Import order %s has no lines to reconcile the proforma to." % order.name
                )
            lines_total = sum(order.line_ids.mapped("fob_amount"))
            if abs(lines_total - (order.fob_value or 0.0)) > 0.01:
                raise UserError(
                    "The lines of %s total %.2f but its FOB value is %.2f: correct the order first."
                    % (order.name, lines_total, order.fob_value)
                )
            expected = order._invoice_value()
            got = order._to_order_ccy(rec.amount or 0.0, rec.currency_id)
            if expected <= 0 or abs(got - expected) > expected * tol / 100.0 + 0.01:
                raise UserError(
                    "Proforma %s (%.2f %s) does not reconcile to order %s (%.2f %s under %s, "
                    "tolerance %.2f%%)."
                    % (
                        rec.proforma_no,
                        got,
                        order.currency_id.name,
                        order.name,
                        expected,
                        order.currency_id.name,
                        (order.incoterm or "").upper(),
                        tol,
                    )
                )
            if rec.valid_until and rec.valid_until < today(rec):
                raise UserError("Proforma %s expired on %s." % (rec.proforma_no, rec.valid_until))
            rec.env["fix.import.irc"]._irc_require_valid(order.company_id, "Approving a proforma")
            order._import_check_eligibility("Approving proforma %s" % rec.proforma_no)
            order._import_check_fx("Approving proforma %s" % rec.proforma_no)
            rec._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": rec.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        require_group(self.env, APPROVER, "Rejecting a proforma invoice")
        for rec in self:
            if rec.state != "received":
                raise UserError("Reject a received proforma (this one is %s)." % rec.state)
            if not (reason or "").strip():
                raise UserError("State why the proforma is rejected.")
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": rec.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "rejection_reason": reason.strip(),
                }
            )
        return True


# =============================================================== LC approval
class FixImportLcApprovalMixin(models.AbstractModel):
    """The local defences every routed M44 approval keeps while the M63 rule
    book is writable by every user (A11 audit, fixes E1-E4 pending): the
    approver group is coded here, never taken from the matrix row; the
    approver must also be an Import Approver; the people who raised or
    changed what is approved never decide it."""

    _name = "fix.import.lc.approval.mixin"
    _description = "M44 LC Approval Defences"
    _inherit = ["fix.dofa.mixin"]

    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    def _dofa_thresholds(self):
        raw = (param(self.env, PARAM_LC_LADDER) or "inf:tier_4").strip()
        ladder = []
        try:
            for part in raw.split(","):
                bound, tier = part.split(":")
                bound = bound.strip().lower()
                tier = tier.strip()
                if tier != "tier_0" and tier not in TIER_GROUP:
                    raise ValueError(tier)
                ladder.append((float("inf") if bound == "inf" else float(bound), tier))
        except ValueError as exc:
            raise UserError(
                "System parameter %s is not a valid LC authority ladder (%r). Use "
                "'<upper bound BDT>:<tier>,...,inf:<tier>', e.g. 5000000:tier_3,inf:tier_4."
                % (PARAM_LC_LADDER, raw)
            ) from exc
        ladder.sort(key=lambda x: x[0])
        if ladder[-1][0] != float("inf"):
            ladder.append((float("inf"), ladder[-1][1]))
        return ladder

    def _approval_group_for(self, rule, tier):
        # IGNORE rule.approver_group_id: the matrix is user-writable.
        xmlid = TIER_GROUP.get(tier) if tier else None
        return self.env.ref(xmlid or APPROVER, raise_if_not_found=False)

    def _approval_holders(self, group):
        users = super()._approval_holders(group)
        approvers = self.env.ref(APPROVER).sudo().all_user_ids
        return users & approvers

    def _lc_conflicted(self):
        """Everyone who raised or shaped what is being approved."""
        self.ensure_one()
        users = self.create_uid | self.approval_amount_changed_by_id
        users |= self.approval_request_id.sudo().requested_by_id
        for fname in ("applied_by_id", "terms_changed_by_id"):
            if fname in self._fields:
                users |= self[fname]
        return users.sudo()

    def _approval_excluded(self):
        return super()._approval_excluded() | self._lc_conflicted()

    def action_dofa_approve(self):
        # The routing check comes first, as in the engine: pressed directly,
        # the approval is refused as "use the approver's inbox" before any
        # role check says who else might press it.
        self._dofa_route_guard()
        for rec in self:
            if rec.env.su and not rec._approval_task():
                continue
            if not rec._dofa_authority_user().has_group(APPROVER):
                raise UserError(
                    "%s is approved by an Import Approver who also holds the DOFA tier."
                    % rec.display_name
                )
            if rec._dofa_acting_users() & rec._lc_conflicted():
                raise UserError(
                    "Segregation of duties: you raised, applied for or changed %s and cannot "
                    "approve it." % rec.display_name
                )
        return super().action_dofa_approve()

    def _lc_bdt(self, amount, lc):
        order = lc.order_id
        return order._to_bdt(amount or 0.0, lc.currency_id) if order else (amount or 0.0)


# =============================================================== LC
LC_TERMS = (
    "order_id",
    "lc_no",
    "bank",
    "currency_id",
    "amount",
    "expiry",
    "margin_pct",
    "facility_id",
)


class FixImportLc(models.Model):
    _name = "fix.import.lc"
    _rec_name = "lc_no"
    _description = "Letter of Credit"
    _order = "opened_on desc, id desc"
    _inherit = ["fix.import.lc.approval.mixin", "mail.thread"]

    _approval_domain = "import_lc"

    name = fields.Char(required=True, default="New")
    order_id = _order_rel()
    company_id = _company_rel("order_id")
    operating_unit_id = _ou_rel("order_id")
    lc_no = fields.Char(string="LC No", required=True, tracking=True)
    bank = fields.Char(string="Issuing Bank")
    facility_id = fields.Many2one(
        "fix.bank.facility",
        string="LC Facility (M50)",
        domain=[("facility_type", "=", "lc"), ("state", "=", "active")],
        ondelete="restrict",
        help="The bank's sanctioned LC limit the LC is opened under (BRU-ITC-06).",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="LC Amount", currency_field="currency_id", tracking=True)
    opened_on = fields.Date(default=fields.Date.context_today)
    expiry = fields.Date(tracking=True)
    margin_pct = fields.Float(string="Margin %", default=0.0)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("applied", "Applied"),
            ("opened", "Opened"),
            ("amended", "Amended"),
            ("closed", "Closed"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    applied_by_id = fields.Many2one("res.users", string="Applied By", readonly=True, copy=False)
    opened_by_id = fields.Many2one("res.users", string="Opened By", readonly=True, copy=False)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    closed_on = fields.Date(readonly=True, copy=False)
    terms_changed_by_id = fields.Many2one(
        "res.users", string="Terms Last Changed By", readonly=True, copy=False
    )
    amendment_ids = fields.One2many("fix.import.lc.amendment", "lc_id", string="Amendments")
    payment_ids = fields.One2many("fix.import.lc.payment", "lc_id", string="Payments")
    paid_amount = fields.Monetary(
        string="Paid", currency_field="currency_id", compute="_compute_paid", store=True
    )

    _margin_range = models.Constraint(
        "CHECK (margin_pct >= 0 AND margin_pct <= 100)", "LC margin must be between 0% and 100%"
    )
    _amount_non_negative = models.Constraint(
        "CHECK (amount >= 0)", "An LC amount cannot be negative"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "opened_on",
            "applied_by_id",
            "opened_by_id",
            "closed_by_id",
            "closed_on",
            "terms_changed_by_id",
            "paid_amount",
        }

    def _lc_locked(self) -> set:
        if self.state in ("opened", "amended", "closed"):
            return set(LC_TERMS)
        return set()

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1:
            locked |= self._lc_locked()
        return locked

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return abs(self._lc_bdt(self.amount, self))

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "LC %s for BDT %.2f" % (self.lc_no or "", self._dofa_amount())

    @api.depends("amount", "currency_id", "order_id.fx_rate")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    @api.depends("payment_ids.amount")
    def _compute_paid(self):
        for rec in self:
            rec.paid_amount = round(sum(rec.payment_ids.mapped("amount")), 2)

    @api.constrains("lc_no", "company_id")
    def _check_unique_lc_no(self):
        for rec in self:
            dup = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("lc_no", "=", rec.lc_no),
                    ("company_id", "=", rec.company_id.id),
                ]
            )
            if dup:
                raise ValidationError("LC number %s is already recorded." % rec.lc_no)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.lc", "ILC/New")
        return super().create(vals_list)

    def write(self, vals):
        guard_open = self._fix_guard_open()
        terms = {k: vals[k] for k in LC_TERMS if k in vals}
        changed = self.browse()
        if self and terms and not guard_open:
            for rec in self:
                if rec._lc_locked() and changes(rec, terms):
                    raise UserError(
                        "LC %s is %s: its amount, expiry and terms change only through an LC "
                        "amendment approved at the authority band of the new total (BRU-ITC-20)."
                        % (rec.lc_no, rec.state)
                    )
            changed = self.filtered(lambda r: changes(r, terms))
        voided = changed.filtered(
            lambda r: r.approval_state in ("pending", "approved") or r.dofa_approved
        )
        result = super().write(vals)
        if changed and not self.env.su:
            changed._guarded().write({"terms_changed_by_id": self.env.uid})
        if voided:
            voided._dofa_void_approval("the LC terms changed after approval was requested")
        return result

    # ---- checks ---------------------------------------------------------------
    def _lc_check(self, what):
        """Everything an LC needs before it is applied for and again before it
        is opened (FR-ITC-019/020, BRU-ITC-03/06)."""
        self.ensure_one()
        order = self.order_id
        if (self.amount or 0.0) <= 0:
            raise UserError("%s: the LC amount must be positive." % what)
        if not self.expiry or self.expiry <= today(self):
            raise UserError(
                "%s: the LC expiry (%s) must be in the future." % (what, self.expiry or "not set")
            )
        if (
            not self.env["fix.import.proforma"]
            .sudo()
            .search_count([("order_id", "=", order.id), ("state", "=", "approved")])
        ):
            raise UserError(
                "%s: import order %s has no approved proforma invoice." % (what, order.name)
            )
        self.env["fix.import.irc"]._irc_require_valid(order.company_id, what)
        tol = param_float(self.env, PARAM_LC_TOLERANCE, 0.0)
        cap = order._invoice_value() * (1.0 + tol / 100.0)
        # M44-4: the cap is the order's, not each LC's: this LC plus the others
        # already committed against the order. A closed LC counts what it paid.
        others = self.sudo().search(
            [
                ("order_id", "=", order.id),
                ("id", "!=", self.id),
                ("state", "in", ("applied", "opened", "amended", "closed")),
            ]
        )
        committed = sum(
            order._to_order_ccy(o.paid_amount if o.state == "closed" else o.amount, o.currency_id)
            for o in others
        )
        in_order_ccy = order._to_order_ccy(self.amount, self.currency_id)
        if committed + in_order_ccy > cap + 0.01:
            raise UserError(
                "%s: LC %s is %.2f %s and other LCs already commit %.2f, but order %s is worth "
                "%.2f %s (tolerance %.2f%%). An LC above the order value needs an approved "
                "amendment."
                % (
                    what,
                    self.lc_no,
                    in_order_ccy,
                    order.currency_id.name,
                    committed,
                    order.name,
                    order._invoice_value(),
                    order.currency_id.name,
                    tol,
                )
            )
        self._lc_facility_check(what, self.amount, self.expiry)
        order._import_check_eligibility(what)
        order._import_check_fx(what)
        if param_bool(self.env, PARAM_LC_REQUIRES_LCA, True):
            lca = (
                self.env["fix.import.lca"]
                .sudo()
                .search([("lc_id", "=", self.id), ("state", "=", "approved")])
            )
            if not lca:
                raise UserError("%s: LC %s has no approved LCA." % (what, self.lc_no))
            # M44-4: an LCA approved for a smaller LC does not authorise this one
            covered = sum(
                lca.filtered(lambda a: a.currency_id == self.currency_id).mapped("amount")
            )
            if covered + 0.005 < (self.amount or 0.0):
                raise UserError(
                    "%s: the approved LCA of LC %s covers %.2f %s but the LC is %.2f: lodge an "
                    "LCA for the LC value."
                    % (what, self.lc_no, covered, self.currency_id.name, self.amount)
                )

    def _lc_in_facility_ccy(self, amount, facility):
        self.ensure_one()
        if facility.currency_id == self.currency_id:
            return amount or 0.0
        if facility.currency_id == self.env.ref("base.BDT"):
            return self._lc_bdt(amount, self)
        raise UserError(
            "LC %s is in %s but facility %s is in %s: record the LC in the facility's "
            "currency or BDT."
            % (self.lc_no, self.currency_id.name, facility.name, facility.currency_id.name)
        )

    def _lc_facility_check(self, what, amount, expiry):
        """BRU-ITC-06: the LC's outstanding amount fits the M50 LC facility's
        available limit (sanctioned limit less GL utilisation) after the other
        LCs already applied for or opened under it."""
        self.ensure_one()
        fac = self.facility_id.sudo()
        if not fac:
            if param_bool(self.env, PARAM_LC_REQUIRES_FACILITY, True):
                raise UserError(
                    "%s: choose the bank's LC facility (M50) the LC is opened under." % what
                )
            return
        if fac.facility_type != "lc" or fac.state != "active":
            raise UserError("%s: facility %s is not an active LC facility." % (what, fac.name))
        if fac.company_id != self.company_id:
            raise UserError("%s: facility %s belongs to another company." % (what, fac.name))
        if fac.expiry_date and expiry and expiry > fac.expiry_date:
            raise UserError(
                "%s: the LC expires on %s, after facility %s ends (%s)."
                % (what, expiry, fac.name, fac.expiry_date)
            )
        others = self.sudo().search(
            [
                ("facility_id", "=", fac.id),
                ("state", "in", ("applied", "opened")),
                ("id", "!=", self.id),
            ]
        )
        committed = sum(o._lc_in_facility_ccy(o.amount - o.paid_amount, fac) for o in others)
        need = self._lc_in_facility_ccy((amount or 0.0) - self.paid_amount, fac)
        headroom = (fac.available or 0.0) - committed
        if need > headroom + 0.005:
            raise UserError(
                "%s: %.2f %s exceeds what facility %s has available (%.2f of a %.2f limit, after "
                "%.2f committed to other LCs)."
                % (
                    what,
                    need,
                    fac.currency_id.name,
                    fac.name,
                    max(headroom, 0.0),
                    fac.limit_amount,
                    committed,
                )
            )

    # ---- transitions ------------------------------------------------------------
    def action_apply(self):
        require_group(self.env, OFFICER, "Applying for an LC")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Apply a draft LC")
            rec._lc_check("Applying for LC %s" % rec.lc_no)
            rec._guarded().write({"state": "applied", "applied_by_id": rec.env.user.id})
        return True

    def action_request_approval(self, justification=None):
        require_group(self.env, OFFICER, "Requesting LC approval")
        for rec in self:
            if rec.state != "applied":
                raise UserError("Request approval for an applied LC (this one is %s)." % rec.state)
        return super().action_request_approval(justification=justification)

    def action_open(self):
        """Record the bank's opening: only an LC applied for, approved at its
        authority band through the M63 inbox, and still within its limits."""
        require_group(self.env, OFFICER, "Opening an LC")
        for rec in self:
            if rec.state != "applied":
                raise UserError("Open an applied LC")
            if rec.approval_state != "approved":
                raise UserError(
                    "LC %s is not approved: request approval and have an Import Approver "
                    "with the DOFA tier decide it from the M63 inbox." % rec.lc_no
                )
            rec._dofa_assert_approved("Opening LC %s" % rec.lc_no)
            rec._lc_check("Opening LC %s" % rec.lc_no)
            rec._guarded().write(
                {"state": "opened", "opened_on": today(rec), "opened_by_id": rec.env.user.id}
            )
            publish(
                rec.env,
                "import.lc_opened",
                "fix.import.lc",
                rec.id,
                {"lc": rec.lc_no, "order": rec.order_id.name, "amount_bdt": rec._dofa_amount()},
            )
        return True

    def action_close(self):
        require_group(self.env, OFFICER, "Closing an LC")
        for rec in self:
            if rec.state != "opened":
                raise UserError("Close an opened LC")
            if rec.amendment_ids.filtered(lambda a: a.state == "draft"):
                raise UserError("LC %s has an open amendment." % rec.lc_no)
            bl = (
                rec.env["fix.import.shipdoc"]
                .sudo()
                .search_count(
                    [
                        ("order_id", "=", rec.order_id.id),
                        ("doc_type", "=", "bl"),
                        ("state", "in", ("received", "verified")),
                    ]
                )
            )
            if not bl or rec.paid_amount <= 0:
                raise UserError(
                    "LC %s cannot be closed before the documents are presented (a received B/L) "
                    "and the LC is retired (a recorded payment)." % rec.lc_no
                )
            rec._guarded().write(
                {"state": "closed", "closed_by_id": rec.env.user.id, "closed_on": today(rec)}
            )
        return True


class FixImportLcAmendment(models.Model):
    """BRU-ITC-20: an LC changes only through an amendment record, approved
    at the authority band of the NEW total, then applied. The records are the
    LC's history: who proposed, who approved, the values before and after."""

    _name = "fix.import.lc.amendment"
    _description = "LC Amendment"
    _order = "create_date desc, id desc"
    _inherit = ["fix.import.lc.approval.mixin", "mail.thread"]

    _approval_domain = "import_lc_amendment"

    name = fields.Char(required=True, default="New")
    lc_id = fields.Many2one(
        "fix.import.lc", string="Letter of Credit", required=True, ondelete="cascade", index=True
    )
    order_id = fields.Many2one(related="lc_id.order_id", store=True, index=True)
    company_id = _company_rel("lc_id")
    operating_unit_id = _ou_rel("lc_id")
    currency_id = fields.Many2one(related="lc_id.currency_id")
    new_amount = fields.Monetary(string="New LC Amount", currency_field="currency_id")
    new_expiry = fields.Date(string="New Expiry")
    reason = fields.Char(required=True)
    old_amount = fields.Monetary(
        string="Amount Before", currency_field="currency_id", readonly=True, copy=False
    )
    old_expiry = fields.Date(string="Expiry Before", readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("applied", "Applied"), ("cancelled", "Cancelled")],
        required=True,
        default="draft",
        tracking=True,
    )
    applied_by_id = fields.Many2one("res.users", string="Applied By", readonly=True, copy=False)
    applied_on = fields.Date(readonly=True, copy=False)
    terms_changed_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    _TERMS = ("lc_id", "new_amount", "new_expiry", "reason")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "old_amount",
            "old_expiry",
            "applied_by_id",
            "applied_on",
            "terms_changed_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(self._TERMS)
        return locked

    def _amended_amount(self) -> float:
        """The LC total after the amendment: a blank new amount means the
        amount is unchanged, as applying the amendment reads it."""
        self.ensure_one()
        return self.new_amount if self.new_amount else (self.lc_id.amount or 0.0)

    def _dofa_amount(self) -> float:
        # An expiry-only amendment is approved at the band of the LC total it
        # leaves in force; read as BDT 0 it was "nothing to approve" and then
        # could never be applied.
        self.ensure_one()
        return abs(self._lc_bdt(self._amended_amount(), self.lc_id)) if self.lc_id else 0.0

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "the amended LC total of BDT %.2f" % self._dofa_amount()

    @api.depends("new_amount", "lc_id.amount", "lc_id.currency_id", "lc_id.order_id.fx_rate")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _amendment_refuse_noop(self):
        """An amendment changes the amount, the expiry, or both."""
        for rec in self:
            lc = rec.lc_id
            same_amount = abs(rec._amended_amount() - (lc.amount or 0.0)) <= 0.005
            same_expiry = not rec.new_expiry or rec.new_expiry == lc.expiry
            if same_amount and same_expiry:
                raise UserError(
                    "Amendment %s changes neither the amount nor the expiry of LC %s."
                    % (rec.name, lc.lc_no)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.lc.amendment", "ILCA-AM/New")
        records = super().create(vals_list)
        for rec in records:
            if rec.lc_id.state != "opened":
                raise UserError(
                    "Only an opened LC can be amended (LC %s is %s)."
                    % (rec.lc_id.lc_no, rec.lc_id.state)
                )
            others = rec.lc_id.amendment_ids.filtered(lambda a: a.state == "draft") - rec
            if others:
                raise UserError(
                    "LC %s already has an open amendment (%s)." % (rec.lc_id.lc_no, others[0].name)
                )
        return records

    def write(self, vals):
        terms = {k: vals[k] for k in self._TERMS if k in vals}
        changed = self.browse()
        if self and terms and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft" and changes(rec, terms):
                    raise UserError("Amendment %s is %s and cannot change." % (rec.name, rec.state))
            changed = self.filtered(lambda r: changes(r, terms))
        voided = changed.filtered(
            lambda r: r.approval_state in ("pending", "approved") or r.dofa_approved
        )
        result = super().write(vals)
        if changed and not self.env.su:
            changed._guarded().write({"terms_changed_by_id": self.env.uid})
        if voided:
            voided._dofa_void_approval("the amendment changed after approval was requested")
        return result

    def action_request_approval(self, justification=None):
        require_group(self.env, OFFICER, "Requesting an LC amendment approval")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Request approval for a draft amendment.")
        self._amendment_refuse_noop()
        return super().action_request_approval(justification=justification)

    def action_apply_amendment(self):
        require_group(self.env, OFFICER, "Applying an LC amendment")
        for rec in self:
            lc = rec.lc_id
            if rec.state != "draft":
                raise UserError("Apply a draft amendment.")
            if lc.state != "opened":
                raise UserError("LC %s is %s: only an opened LC is amended." % (lc.lc_no, lc.state))
            if rec.approval_state != "approved":
                raise UserError("Amendment %s is not approved through the M63 inbox." % rec.name)
            rec._amendment_refuse_noop()
            rec._dofa_assert_approved("LC amendment %s" % rec.name)
            new_amount = rec._amended_amount()
            if new_amount < lc.paid_amount - 0.005:
                raise UserError(
                    "The amended LC amount %.2f is below the %.2f already paid under it."
                    % (new_amount, lc.paid_amount)
                )
            new_expiry = rec.new_expiry or lc.expiry
            if not new_expiry or new_expiry <= today(rec):
                raise UserError("The amended expiry must be in the future.")
            lc._lc_facility_check("Amending LC %s" % lc.lc_no, new_amount, new_expiry)
            rec._guarded().write(
                {
                    "old_amount": lc.amount,
                    "old_expiry": lc.expiry,
                    "state": "applied",
                    "applied_by_id": rec.env.user.id,
                    "applied_on": today(rec),
                }
            )
            # the LC's approval now covers the amended total: the amendment's
            # approval, decided at the band of the new total, is carried over
            lc._guarded().write(
                {
                    "amount": new_amount,
                    "expiry": new_expiry,
                    "dofa_approved": True,
                    "dofa_approved_by": rec.dofa_approved_by.id,
                    "dofa_approved_at": rec.dofa_approved_at,
                    "dofa_approved_tier": rec.dofa_approved_tier,
                    "dofa_approved_amount": rec.dofa_approved_amount,
                }
            )
            lc.message_post(
                body="Amendment %s applied: amount %.2f -> %.2f, expiry %s -> %s (%s)."
                % (rec.name, rec.old_amount, new_amount, rec.old_expiry, new_expiry, rec.reason)
            )
        return True

    def action_cancel(self):
        require_group(self.env, OFFICER, "Cancelling an LC amendment")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Cancel a draft amendment.")
            if rec.approval_state == "pending":
                rec.action_recall_approval()
            rec._dofa_void_approval("the amendment was cancelled")
            rec._guarded().write({"state": "cancelled"})
        return True


class FixImportLcPayment(models.Model):
    """A payment (retirement) under an LC. Payments for an import never
    exceed the LC (Bangladesh Bank FE Circular 29/2022). Append-only.

    BRU-ITC-14 / FR-ITC-019: a foreign-currency payment records the settlement
    rate with its source; the commitment rate is the order's, never re-derived.
    The payment posts Dr LC clearing at the commitment rate, the exchange
    difference, Cr bank at the settlement rate. Scorecard 25: a payment names
    the Bill of Entry it remits (now, or later through Link Bill of Entry)."""

    _name = "fix.import.lc.payment"
    _description = "LC Payment"
    _rec_name = "reference"
    _order = "payment_date desc, id desc"

    lc_id = fields.Many2one(
        "fix.import.lc", string="Letter of Credit", required=True, ondelete="restrict", index=True
    )
    company_id = _company_rel("lc_id")
    operating_unit_id = _ou_rel("lc_id")
    currency_id = fields.Many2one(related="lc_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id", required=True)
    payment_date = fields.Date(required=True, default=fields.Date.context_today)
    reference = fields.Char(string="Bank Reference", required=True)
    recorded_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user, copy=False
    )
    settlement_rate = fields.Float(
        string="Settlement Rate (BDT per unit)",
        digits=(16, 6),
        help="The rate the bank settled at. Required when the LC is in a foreign currency.",
    )
    settlement_rate_source = fields.Char(string="Settlement Rate Source")
    commitment_rate = fields.Float(
        string="Commitment Rate", digits=(16, 6), readonly=True, copy=False
    )
    amount_bdt = fields.Float(string="Paid (BDT)", readonly=True, copy=False)
    fx_difference = fields.Float(
        string="FX Difference (BDT)",
        readonly=True,
        copy=False,
        help="Paid at the settlement rate less the same amount at the commitment rate: "
        "positive is a loss.",
    )
    move_id = fields.Many2one("account.move", string="Payment Entry", readonly=True, copy=False)
    boe_id = fields.Many2one(
        "fix.import.boe", string="Bill of Entry", index=True, ondelete="restrict", copy=False
    )
    match_flagged_on = fields.Date(string="Flagged Unmatched On", readonly=True, copy=False)

    _amount_positive = models.Constraint("CHECK (amount > 0)", "An LC payment must be positive")
    _FORGEABLE = (
        "commitment_rate",
        "amount_bdt",
        "fx_difference",
        "move_id",
        "match_flagged_on",
    )

    @api.constrains("boe_id", "lc_id")
    def _check_boe_of_order(self):
        for rec in self.sudo().filtered("boe_id"):
            if rec.boe_id.order_id != rec.lc_id.order_id:
                raise ValidationError(
                    "Bill of Entry %s belongs to import %s, not to this LC's import %s."
                    % (rec.boe_id.boe_no, rec.boe_id.order_id.name, rec.lc_id.order_id.name)
                )

    def _payment_post(self):
        """Accounts and journal are resolved first: an unset one refuses the
        payment with nothing posted."""
        self.ensure_one()
        lc = self.lc_id.sudo()
        order = lc.order_id
        company = lc.company_id
        foreign = lc.currency_id != self.env.ref("base.BDT")
        if foreign:
            if (self.settlement_rate or 0.0) <= 0 or not (
                self.settlement_rate_source or ""
            ).strip():
                raise UserError(
                    "LC %s is in %s: record the settlement rate and its source (BRU-ITC-14)."
                    % (lc.lc_no, lc.currency_id.name)
                )
            order._import_check_fx("Paying under LC %s" % lc.lc_no)
            commitment = order.fx_rate
            settlement = self.settlement_rate
        else:
            commitment = settlement = 1.0
        committed = round(order._to_bdt(self.amount, lc.currency_id), 2)
        paid = round((self.amount or 0.0) * settlement, 2)
        difference = round(paid - committed, 2)
        clearing = import_account(self.env, company, "lc_clearing")
        fx_account = import_account(self.env, company, "fx_difference") if difference else False
        journal = import_journal(self.env, company, "payment")
        ref = "LC %s payment %s" % (lc.lc_no, self.reference)
        move = post_import_move(
            self.env,
            company,
            journal,
            self.payment_date,
            ref,
            [
                (clearing, "LC payment %s" % order.name, committed),
                (fx_account, "Exchange difference %s" % lc.lc_no, difference),
                (journal.default_account_id, ref, -paid),
            ],
            operating_unit=lc.operating_unit_id,
        )
        self.sudo().write(
            {
                "commitment_rate": commitment,
                "amount_bdt": paid,
                "fx_difference": difference,
                "move_id": move.id or False,
            }
        )

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, FINANCE, "Recording an LC payment")
        for vals in vals_list:
            vals["recorded_by_id"] = self.env.uid
            for name in self._FORGEABLE:
                vals.pop(name, None)
        records = super().create(vals_list)
        for rec in records:
            lc = rec.lc_id
            if lc.state != "opened":
                raise UserError(
                    "Payments are recorded against an opened LC (LC %s is %s)."
                    % (lc.lc_no, lc.state)
                )
            total = sum(lc.payment_ids.mapped("amount"))
            if total > lc.amount + 0.005:
                raise UserError(
                    "Payments under LC %s would total %.2f, above the LC amount %.2f."
                    % (lc.lc_no, total, lc.amount)
                )
            rec._payment_post()
        return records

    def write(self, vals):
        if not self.env.su:
            raise UserError("An LC payment is final; record a correcting entry in treasury.")
        return super().write(vals)

    def action_link_boe(self, boe_no=None):
        """Scorecard 25: the Bill of Entry a remittance answers, recorded when
        it exists. Only the link changes on a recorded payment."""
        require_group(self.env, FINANCE, "Linking an LC payment to a Bill of Entry")
        for rec in self:
            if rec.boe_id:
                raise UserError(
                    "This payment is already matched to Bill of Entry %s." % rec.boe_id.boe_no
                )
            number = (boe_no or "").strip()
            if not number:
                raise UserError("State the Bill of Entry number the payment remits.")
            bill = (
                self.env["fix.import.boe"]
                .sudo()
                .search(
                    [
                        ("order_id", "=", rec.lc_id.order_id.id),
                        ("boe_no", "=", number),
                        ("state", "in", ("assessed", "paid")),
                    ],
                    limit=1,
                )
            )
            if not bill:
                raise UserError(
                    "Import %s has no assessed or paid Bill of Entry numbered %s."
                    % (rec.lc_id.order_id.name, number)
                )
            rec.sudo().write({"boe_id": bill.id})
        return True

    def unlink(self):
        if not self.env.su:
            raise UserError("An LC payment cannot be deleted.")
        return super().unlink()


# =============================================================== LCA
class FixImportLca(models.Model):
    _name = "fix.import.lca"
    _rec_name = "lca_no"
    _description = "Letter of Credit Authorisation"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    lc_id = fields.Many2one(
        "fix.import.lc", string="Letter of Credit", required=True, ondelete="cascade", index=True
    )
    company_id = _company_rel("lc_id")
    operating_unit_id = _ou_rel("lc_id")
    lca_no = fields.Char(string="LCA No", required=True)
    bank = fields.Char(string="Dealer Bank")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    state = fields.Selection(
        [("applied", "Applied"), ("approved", "Approved"), ("rejected", "Rejected")],
        required=True,
        default="applied",
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Char(readonly=True, copy=False)

    _PINNED = ("lc_id", "lca_no", "currency_id", "amount", "bank")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "decided_by_id",
            "decided_on",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "applied":
            locked |= set(self._PINNED)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.lca", "ILCA/New")
        return super().create(vals_list)

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._PINNED) if r.state != "applied" else set(),
            "a decided LCA is final.",
        )
        return super().write(vals)

    def action_approve(self):
        require_group(self.env, APPROVER, "Approving an LCA")
        for rec in self:
            if rec.state != "applied":
                raise UserError("Approve an applied LCA")
            require_other_person(rec.env, rec, "LCA %s" % rec.lca_no)
            lc = rec.lc_id
            if (
                rec.currency_id != lc.currency_id
                or abs((rec.amount or 0.0) - (lc.amount or 0.0)) > 0.005
            ):
                raise UserError(
                    "LCA %s authorises %.2f %s but LC %s is %.2f %s: the LCA must cover the LC value."
                    % (
                        rec.lca_no,
                        rec.amount,
                        rec.currency_id.name,
                        lc.lc_no,
                        lc.amount,
                        lc.currency_id.name,
                    )
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": rec.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        require_group(self.env, APPROVER, "Rejecting an LCA")
        for rec in self:
            if rec.state != "applied":
                raise UserError("Reject an applied LCA")
            if not (reason or "").strip():
                raise UserError("State why the LCA is rejected.")
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": rec.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "rejection_reason": reason.strip(),
                }
            )
        return True


# =============================================================== tariff master
class FixImportTariff(models.Model):
    """The NBR operative tariff as reference data (M44-10, BRU-ITC-08): one
    row per heading and effective period. Rates are data the user enters
    from the tariff schedule and SROs; this module asserts none. A row is
    activated by an Import Approver who did not enter it, and is frozen once
    active: a new rate is a new row with its own effective date."""

    _name = "fix.import.tariff"
    _description = "HS Tariff Rate"
    _rec_name = "hs_code"
    _order = "hs_code, date_from desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    hs_code = fields.Char(string="HS Code", required=True, index=True)
    description = fields.Char()
    sro_ref = fields.Char(string="SRO / Tariff Reference", required=True)
    date_from = fields.Date(string="Effective From", required=True)
    date_to = fields.Date(string="Effective To")
    cd_pct = fields.Float(string="Customs Duty %")
    rd_pct = fields.Float(string="Regulatory Duty %")
    sd_pct = fields.Float(string="Supplementary Duty %")
    vat_pct = fields.Float(string="VAT %")
    at_pct = fields.Float(string="Advance Tax %")
    ait_pct = fields.Float(string="AIT %")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    activated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    activated_on = fields.Datetime(readonly=True, copy=False)

    _rates_range = models.Constraint(
        "CHECK (cd_pct >= 0 AND rd_pct >= 0 AND sd_pct >= 0 AND vat_pct >= 0 AND at_pct >= 0 "
        "AND ait_pct >= 0 AND cd_pct <= 1000 AND rd_pct <= 1000 AND sd_pct <= 1000 "
        "AND vat_pct <= 1000 AND at_pct <= 1000 AND ait_pct <= 1000)",
        "Duty and tax rates must be between 0% and 1000%",
    )
    _dates_ordered = models.Constraint(
        "CHECK (date_to IS NULL OR date_to >= date_from)",
        "A tariff row cannot end before it starts",
    )

    _FROZEN = ("company_id", "hs_code", "sro_ref", "date_from", "date_to", *_RATE_FIELDS)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "activated_by_id", "activated_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(self._FROZEN)
        return locked

    @api.constrains("hs_code")
    def _check_code(self):
        for rec in self:
            _check_hs_code(rec.hs_code)

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._FROZEN) if r.state != "draft" else set(),
            "an active tariff row is frozen; enter the new rate as a new row with its own "
            "effective date (BRU-ITC-08).",
        )
        return super().write(vals)

    @api.model
    def _tariff_for(self, company, hs_code, on_date):
        digits = _hs_digits(hs_code)
        if not digits:
            return self.browse()
        rows = self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("state", "in", ("active", "retired")),
                ("date_from", "<=", on_date),
                "|",
                ("date_to", "=", False),
                ("date_to", ">=", on_date),
            ],
            order="date_from desc",
        )
        return rows.filtered(lambda r: _hs_digits(r.hs_code) == digits)[:1]

    def action_activate(self):
        require_group(self.env, APPROVER, "Activating a tariff rate")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Activate a draft tariff row.")
            require_other_person(
                rec.env, rec, "Tariff row %s from %s" % (rec.hs_code, rec.date_from)
            )
            digits = _hs_digits(rec.hs_code)
            live = (
                self.sudo()
                .search(
                    [
                        ("company_id", "=", rec.company_id.id),
                        ("state", "in", ("active", "retired")),
                        ("id", "!=", rec.id),
                    ]
                )
                .filtered(lambda r, d=digits: _hs_digits(r.hs_code) == d)
            )
            for other in live:
                ends = rec.date_to or fields.Date.to_date("9999-12-31")
                other_ends = other.date_to or fields.Date.to_date("9999-12-31")
                if other.date_from < rec.date_from and not other.date_to:
                    # the open-ended predecessor ends the day before this row starts
                    other.sudo()._guarded().write(
                        {"date_to": rec.date_from - timedelta(days=1), "state": "retired"}
                    )
                    continue
                if other.date_from <= ends and rec.date_from <= other_ends:
                    raise UserError(
                        "Tariff %s from %s overlaps the row in force from %s to %s."
                        % (rec.hs_code, rec.date_from, other.date_from, other.date_to or "open")
                    )
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": rec.env.user.id,
                    "activated_on": fields.Datetime.now(),
                }
            )
        return True

    def action_retire(self, date_to=None):
        require_group(self.env, APPROVER, "Retiring a tariff rate")
        for rec in self:
            if rec.state != "active":
                raise UserError("Retire an active tariff row.")
            end = _typed_date(date_to, "Retiring a tariff rate") if date_to else today(rec)
            if end < rec.date_from:
                end = rec.date_from
            rec._guarded().write({"state": "retired", "date_to": end})
        return True


# =============================================================== HS classification
class FixImportHs(models.Model):
    _name = "fix.import.hs"
    _rec_name = "hs_code"
    _description = "HS Classification"
    _order = "hs_code"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="cascade", index=True
    )
    hs_code = fields.Char(string="HS Code", required=True, tracking=True)
    description = fields.Char()
    ruling_ref = fields.Char(string="Ruling Reference", tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("ruled", "Ruled")], required=True, default="draft", tracking=True
    )
    classified_by_id = fields.Many2one(
        "res.users", string="Classified By", readonly=True, copy=False
    )
    ruled_by_id = fields.Many2one("res.users", string="Ruled By", readonly=True, copy=False)
    ruled_on = fields.Datetime(readonly=True, copy=False)
    # The rates are the tariff master's, in force today: shown, never typed.
    tariff_id = fields.Many2one(
        "fix.import.tariff", compute="_compute_rates", string="Tariff in Force"
    )
    cd_pct = fields.Float(string="Customs Duty %", compute="_compute_rates")
    rd_pct = fields.Float(string="Regulatory Duty %", compute="_compute_rates")
    sd_pct = fields.Float(string="Supplementary Duty %", compute="_compute_rates")
    vat_pct = fields.Float(string="VAT %", compute="_compute_rates")
    at_pct = fields.Float(string="Advance Tax %", compute="_compute_rates")
    ait_pct = fields.Float(string="AIT %", compute="_compute_rates")

    _product_unique = models.Constraint("UNIQUE (product_id)", "One HS classification per product")

    _RULED_FROZEN = ("company_id", "product_id", "hs_code", "ruling_ref")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "classified_by_id",
            "ruled_by_id",
            "ruled_on",
            "tariff_id",
            *_RATE_FIELDS,
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state == "ruled":
            locked |= set(self._RULED_FROZEN)
        return locked

    @api.depends("hs_code", "company_id")
    def _compute_rates(self):
        Tariff = self.env["fix.import.tariff"]
        for rec in self:
            row = Tariff._tariff_for(rec.company_id or self.env.company, rec.hs_code, today(rec))
            rec.tariff_id = row
            for fname in _RATE_FIELDS:
                rec[fname] = row[fname] if row else 0.0

    @api.constrains("hs_code")
    def _check_code(self):
        for rec in self:
            _check_hs_code(rec.hs_code)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.hs", "IHS/New")
        records = super().create(vals_list)
        if not self.env.su:
            records._guarded().write({"classified_by_id": self.env.uid})
        return records

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._RULED_FROZEN) if r.state == "ruled" else set(),
            "a ruled classification is reclassified only by reopening it and having it "
            "ruled again (BRU-ITC-04).",
        )
        recoded = self.filtered(
            lambda r: "hs_code" in vals and changes(r, {"hs_code": vals["hs_code"]})
        )
        result = super().write(vals)
        if recoded and not self.env.su:
            recoded._guarded().write({"classified_by_id": self.env.uid})
        return result

    def action_rule(self):
        """An Import Approver who did not classify it rules the line, with
        a ruling reference and a tariff row in force for the heading."""
        require_group(self.env, APPROVER, "Ruling an HS classification")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Rule a draft classification.")
            require_other_person(
                rec.env, rec, "HS classification %s" % rec.hs_code, rec.classified_by_id
            )
            if not (rec.ruling_ref or "").strip():
                raise UserError("Record the ruling reference before ruling %s." % rec.hs_code)
            if not rec.tariff_id:
                raise UserError(
                    "HS %s has no active tariff row in force today: enter and activate it in "
                    "the tariff master first." % rec.hs_code
                )
            rec._guarded().write(
                {
                    "state": "ruled",
                    "ruled_by_id": rec.env.user.id,
                    "ruled_on": fields.Datetime.now(),
                }
            )
        return True

    def action_reopen(self):
        """Reclassification: back to draft, to be ruled again. The chatter
        keeps the code and ruling it had."""
        require_group(self.env, OFFICER, "Reopening an HS classification")
        for rec in self:
            if rec.state != "ruled":
                raise UserError("Only a ruled classification is reopened.")
            rec.message_post(
                body="Reclassification opened by %s; the ruled code was %s (ruling %s, ruled by %s)."
                % (rec.env.user.name, rec.hs_code, rec.ruling_ref, rec.ruled_by_id.name)
            )
            rec._guarded().write({"state": "draft", "ruled_by_id": False, "ruled_on": False})
        return True


# =============================================================== IRC
class FixImportIrc(models.Model):
    _name = "fix.import.irc"
    _rec_name = "irc_no"
    _description = "Import Registration Certificate"
    _order = "valid_to desc, id desc"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company",
        string="Importer",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    irc_no = fields.Char(string="IRC No", required=True)
    issued_on = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    restrictions = fields.Text(string="Restricted Items / Conditions")
    state = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired"), ("suspended", "Suspended")],
        required=True,
        default="valid",
        tracking=True,
    )
    suspended_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    suspension_reason = fields.Char(readonly=True, copy=False)
    expiry_warned_on = fields.Date(string="Expiry Warning Sent", readonly=True, copy=False)
    # Computed on every read from today's date, never stored and forgotten.
    is_valid = fields.Boolean(compute="_compute_is_valid", search="_search_is_valid")

    _FROZEN = ("company_id", "irc_no", "issued_on", "valid_to")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "suspended_by_id",
            "suspension_reason",
            "expiry_warned_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and isinstance(self.id, int):
            locked |= set(self._FROZEN)
        return locked

    @api.depends("state", "valid_to")
    def _compute_is_valid(self):
        day = today(self)
        for rec in self:
            rec.is_valid = bool(rec.state == "valid" and (not rec.valid_to or rec.valid_to >= day))

    def _search_is_valid(self, operator, value):
        day = today(self)
        valid = Domain("state", "=", "valid") & (
            Domain("valid_to", "=", False) | Domain("valid_to", ">=", day)
        )
        if operator in ("=", "!="):
            wanted, negate = {bool(value)}, operator == "!="
        elif operator in ("in", "not in"):
            wanted, negate = {bool(v) for v in value}, operator == "not in"
        else:
            return NotImplemented
        if wanted == {True, False}:
            domain = Domain.TRUE
        elif True in wanted:
            domain = valid
        else:
            domain = ~valid
        return ~domain if negate else domain

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.irc", "IIRC/New")
        return super().create(vals_list)

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._FROZEN),
            "a recorded IRC is evidence; a renewal is recorded as a new certificate.",
        )
        return super().write(vals)

    @api.model
    def _irc_require_valid(self, company, what):
        """BRU-ITC-03: no progression on a lapsed or suspended IRC."""
        if not self.sudo().search_count([("company_id", "=", company.id), ("is_valid", "=", True)]):
            raise UserError(
                "%s: %s holds no valid Import Registration Certificate (expired, suspended or "
                "none recorded)." % (what, company.name)
            )

    def action_suspend(self, reason=None):
        require_group(self.env, APPROVER, "Suspending an IRC")
        for rec in self:
            if rec.state != "valid":
                raise UserError("Suspend a valid IRC.")
            if not (reason or "").strip():
                raise UserError("State why the IRC is suspended.")
            rec._guarded().write(
                {
                    "state": "suspended",
                    "suspended_by_id": rec.env.user.id,
                    "suspension_reason": reason.strip(),
                }
            )
        return True

    def action_reinstate(self):
        require_group(self.env, APPROVER, "Reinstating an IRC")
        for rec in self:
            if rec.state != "suspended":
                raise UserError("Reinstate a suspended IRC.")
            require_other_person(
                rec.env, rec, "Reinstating IRC %s" % rec.irc_no, rec.suspended_by_id
            )
            if rec.valid_to and rec.valid_to < today(rec):
                raise UserError(
                    "IRC %s lapsed on %s; record the renewed certificate."
                    % (rec.irc_no, rec.valid_to)
                )
            rec._guarded().write(
                {"state": "valid", "suspended_by_id": False, "suspension_reason": False}
            )
        return True

    @api.model
    def _cron_expire(self):
        """AUT-ITC-05: a certificate past its date is expired (daily)."""
        lapsed = self.sudo().search([("state", "=", "valid"), ("valid_to", "<", today(self))])
        for rec in lapsed:
            rec._guarded().write({"state": "expired"})
            rec.message_post(body="IRC %s expired on %s." % (rec.irc_no, rec.valid_to))
            publish(self.env, "import.irc_expired", "fix.import.irc", rec.id, {"irc": rec.irc_no})
        self._warn_expiring()
        return len(lapsed)

    @api.model
    def _warn_expiring(self):
        """BRU-ITC-03: the Import Approvers hear before the certificate lapses,
        once per certificate (days in cd_import_order.irc_expiry_warning_days)."""
        days = int(param_float(self.env, PARAM_IRC_WARNING_DAYS, 30.0))
        day = today(self)
        due = self.sudo().search(
            [
                ("state", "=", "valid"),
                ("valid_to", ">=", day),
                ("valid_to", "<=", day + timedelta(days=days)),
                ("expiry_warned_on", "=", False),
            ]
        )
        for rec in due:
            note = "IRC %s expires on %s: record the renewal before it lapses." % (
                rec.irc_no,
                rec.valid_to,
            )
            rec.message_post(body=note)
            schedule_alert(rec, "IRC expiring", note, alert_users(rec, APPROVER, rec.create_uid))
            rec._guarded().write({"expiry_warned_on": day})
        return len(due)


# =============================================================== shipping documents
class FixImportShipdoc(models.Model):
    _name = "fix.import.shipdoc"
    _rec_name = "ref"
    _description = "Shipping Document"
    _order = "received_on desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    order_id = _order_rel()
    company_id = _company_rel("order_id")
    operating_unit_id = _ou_rel("order_id")
    doc_type = fields.Selection(
        [
            ("bl", "Bill of Lading"),
            ("invoice", "Commercial Invoice"),
            ("packing", "Packing List"),
            ("coo", "Certificate of Origin"),
            ("insurance", "Insurance Certificate"),
            ("other", "Other"),
        ],
        required=True,
        default="bl",
    )
    ref = fields.Char(string="Document Reference")
    received_on = fields.Date(required=True, default=fields.Date.context_today)
    document = fields.Binary(string="Document File", attachment=True)
    document_name = fields.Char(string="File Name")
    state = fields.Selection(
        [("pending", "Pending"), ("received", "Received"), ("verified", "Verified")],
        required=True,
        default="pending",
    )
    received_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    verified_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    _FROZEN = ("order_id", "doc_type", "ref", "received_on", "document", "document_name")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "received_by_id", "verified_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "pending":
            locked |= set(self._FROZEN)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.shipdoc", "ISD/New")
        return super().create(vals_list)

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._FROZEN) if r.state != "pending" else set(),
            "a received document is evidence.",
        )
        return super().write(vals)

    def action_receive(self):
        require_group(self.env, OFFICER, "Receiving a shipping document")
        for rec in self:
            if rec.state != "pending":
                raise UserError("Receive a pending document")
            if not (rec.ref or "").strip():
                raise UserError(
                    "Record the document reference (B/L, invoice or certificate number) first."
                )
            if rec.doc_type == "bl":
                what = "Shipping under B/L %s" % rec.ref
                order = rec.order_id
                rec.env["fix.import.irc"]._irc_require_valid(order.company_id, what)
                order._import_check_fx(what)
                order._import_check_instrument(what)
                order._import_check_insurance(what)
            rec._guarded().write({"state": "received", "received_by_id": rec.env.user.id})
            if rec.doc_type == "bl":
                rec.order_id._import_set_state("shipped", ("draft",))
        return True

    def action_verify(self):
        require_group(self.env, OFFICER, "Verifying a shipping document")
        for rec in self:
            if rec.state != "received":
                raise UserError("Verify a received document.")
            if not rec.env.su and rec.received_by_id == rec.env.user:
                raise UserError(
                    "Segregation of duties: the person who received a document does not verify it."
                )
            rec._guarded().write({"state": "verified", "verified_by_id": rec.env.user.id})
        return True


# =============================================================== arrival
class FixImportArrival(models.Model):
    _name = "fix.import.arrival"
    _description = "Shipment Arrival"
    _order = "eta desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    order_id = _order_rel()
    company_id = _company_rel("order_id")
    operating_unit_id = _ou_rel("order_id")
    vessel = fields.Char(string="Vessel / Flight")
    bl_no = fields.Char(string="B/L No")
    port = fields.Char(string="Port", default="Chattogram")
    etd = fields.Date(string="ETD")
    eta = fields.Date(string="ETA")
    arrival_date = fields.Date(string="Arrival")
    free_days = fields.Integer(string="Free Days", default=7)
    # BRU-ITC-17: free time runs from the ACTUAL arrival; demurrage accrues
    # every day the cargo waits at port after it, up to release. Computed.
    demurrage_days = fields.Integer(string="Demurrage Days", compute="_compute_demurrage")
    demurrage_cause = fields.Selection(
        [
            ("documents", "Documents late or incomplete"),
            ("customs", "Customs assessment or query"),
            ("duty_funds", "Duty funds not available"),
            ("agent", "C&F agent delay"),
            ("carrier", "Carrier or port congestion"),
            ("other", "Other (see note)"),
        ],
        string="Demurrage Cause",
    )
    demurrage_note = fields.Char(string="Demurrage Note")
    demurrage_alerted_on = fields.Date(string="Free Days Alert Sent", readonly=True, copy=False)
    release_ref = fields.Char(string="Customs Release Order No")
    cnf_agent_id = fields.Many2one(
        "fix.import.cnf.agent", string="C&F Agent", ondelete="restrict", index=True
    )
    cleared_on = fields.Date(string="Cleared On")
    arrived_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    cleared_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    state = fields.Selection(
        [("in_transit", "In Transit"), ("arrived", "Arrived"), ("cleared", "Cleared")],
        required=True,
        default="in_transit",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "arrival_date",
            "cleared_on",
            "arrived_by_id",
            "cleared_by_id",
            "demurrage_alerted_on",
        }

    def _locked(self) -> set:
        locked = set()
        if self.state != "in_transit":
            locked |= {"order_id", "free_days", "eta", "etd"}
        if self.state == "cleared":
            locked |= {
                "release_ref",
                "bl_no",
                "vessel",
                "port",
                "cnf_agent_id",
                "demurrage_cause",
                "demurrage_note",
            }
        return locked

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1:
            locked |= self._locked()
        return locked

    @api.depends("arrival_date", "cleared_on", "free_days", "state")
    def _compute_demurrage(self):
        day = today(self)
        for rec in self:
            if not rec.arrival_date:
                rec.demurrage_days = 0
                continue
            end = rec.cleared_on or day
            rec.demurrage_days = max((end - rec.arrival_date).days - (rec.free_days or 0), 0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.arrival", "IARR/New")
        return super().create(vals_list)

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: r._locked(),
            "it is fixed once the shipment has arrived or cleared.",
        )
        return super().write(vals)

    def action_arrive(self, arrival_date=None):
        require_group(self.env, OFFICER, "Recording an arrival")
        day = today(self)
        for rec in self:
            if rec.state != "in_transit":
                raise UserError("Mark an in-transit shipment arrived")
            if rec.order_id.state not in ("shipped", "customs"):
                raise UserError(
                    "Import order %s has no received bill of lading: record the B/L before "
                    "the arrival." % rec.order_id.name
                )
            arrival = _typed_date(arrival_date, "Recording an arrival") if arrival_date else day
            if arrival > day or (rec.etd and arrival < rec.etd):
                raise UserError("The arrival date must lie between the departure and today.")
            rec._guarded().write(
                {"state": "arrived", "arrival_date": arrival, "arrived_by_id": rec.env.user.id}
            )
            rec.order_id._import_set_state("customs", ("shipped",))
            publish(
                rec.env,
                "import.arrived",
                "fix.import.arrival",
                rec.id,
                {"order": rec.order_id.name, "arrival": str(arrival)},
            )
        return True

    def action_clear(self):
        """FR-ITC-032: release only against a paid Bill of Entry and the
        customs release order number (M44-7)."""
        require_group(self.env, OFFICER, "Recording customs clearance")
        for rec in self:
            if rec.state != "arrived":
                raise UserError("Clear an arrived shipment")
            rec.cnf_agent_id._cnf_require_usable("Clearing %s" % rec.name)
            if not (rec.release_ref or "").strip():
                raise UserError("Record the customs release order number before clearing.")
            if rec.demurrage_days > 0 and not rec.demurrage_cause:
                raise UserError(
                    "Shipment %s has run %d day(s) past its free time: record the demurrage "
                    "cause before clearing (BRU-ITC-17)." % (rec.name, rec.demurrage_days)
                )
            boes = (
                rec.env["fix.import.boe"]
                .sudo()
                .search([("order_id", "=", rec.order_id.id), ("state", "!=", "reversed")])
            )
            if not boes.filtered(lambda b: b.state == "paid"):
                raise UserError("Shipment %s cannot clear: no Bill of Entry is paid." % rec.name)
            unpaid = boes.filtered(lambda b: b.state != "paid")
            if unpaid:
                raise UserError(
                    "Shipment %s cannot clear: Bill of Entry %s is not paid."
                    % (rec.name, unpaid[0].boe_no)
                )
            rec._guarded().write(
                {"state": "cleared", "cleared_on": today(rec), "cleared_by_id": rec.env.user.id}
            )
            rec.order_id._import_set_state("cleared", ("customs",))
            publish(
                rec.env,
                "import.cleared",
                "fix.import.arrival",
                rec.id,
                {
                    "order": rec.order_id.name,
                    "release_ref": rec.release_ref,
                    "boe": boes.mapped("boe_no"),
                },
            )
        return True

    @api.model
    def _cron_demurrage_alert(self):
        """BRU-ITC-17: a shipment past its free time, still at port, raises a
        to-do on its import order, once per shipment (daily)."""
        waiting = self.sudo().search(
            [("state", "=", "arrived"), ("demurrage_alerted_on", "=", False)]
        )
        late = waiting.filtered(lambda r: r.demurrage_days > 0)
        day = today(self)
        for rec in late:
            order = rec.order_id
            note = (
                "Shipment %s has run %d day(s) past its %d free days at %s. Record the demurrage "
                "cause and clear it." % (rec.name, rec.demurrage_days, rec.free_days, rec.port)
            )
            order.message_post(body=note)
            schedule_alert(
                order,
                "Demurrage running",
                note,
                alert_users(rec, None, rec.arrived_by_id or order.create_uid),
            )
            rec._guarded().write({"demurrage_alerted_on": day})
        return len(late)


# =============================================================== bill of entry
BOE_LOCK_ASSESSED = (
    "order_id",
    "boe_no",
    "boe_date",
    "asycuda_ref",
    "currency_id",
    "line_ids",
    "cnf_agent_id",
)
BOE_LOCK_PAID = ("customs_assessed_total", "payment_ref")


class FixImportBoe(models.Model):
    _name = "fix.import.boe"
    _rec_name = "boe_no"
    _description = "Bill of Entry"
    _order = "assessed_on desc, id desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    name = fields.Char(required=True, default="New")
    order_id = _order_rel()
    company_id = _company_rel("order_id")
    operating_unit_id = _ou_rel("order_id")
    boe_no = fields.Char(string="Bill of Entry No", required=True, tracking=True)
    asycuda_ref = fields.Char(string="ASYCUDA Reference")
    cnf_agent_id = fields.Many2one(
        "fix.import.cnf.agent",
        string="C&F Agent",
        ondelete="restrict",
        index=True,
        help="The licensed agent who lodges the Bill of Entry (BRU-ITC-12).",
    )
    boe_date = fields.Date(
        string="Lodgement Date", required=True, default=fields.Date.context_today
    )
    assessed_on = fields.Date()
    assessed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    line_ids = fields.One2many("fix.import.boe.line", "boe_id", string="Lines")
    cd_amount = fields.Monetary(compute="_compute_totals", store=True, string="CD")
    rd_amount = fields.Monetary(compute="_compute_totals", store=True, string="RD")
    sd_amount = fields.Monetary(compute="_compute_totals", store=True, string="SD")
    vat_amount = fields.Monetary(compute="_compute_totals", store=True, string="VAT")
    at_amount = fields.Monetary(compute="_compute_totals", store=True, string="AT")
    ait_amount = fields.Monetary(compute="_compute_totals", store=True, string="AIT")
    total_tax = fields.Monetary(compute="_compute_totals", store=True, string="Total Duty & Tax")
    assessable_total = fields.Monetary(
        compute="_compute_totals", store=True, string="Assessable Value"
    )
    # BRU-ITC-07: customs' own assessed figure, compared to this computation.
    customs_assessed_total = fields.Monetary(string="Customs Assessed Total", tracking=True)
    duty_variance = fields.Monetary(compute="_compute_variance", string="Variance vs Customs")
    payment_ref = fields.Char(string="Duty Payment Reference", tracking=True)
    paid_on = fields.Date(readonly=True, copy=False)
    paid_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    move_id = fields.Many2one("account.move", string="Payment Entry", readonly=True, copy=False)
    reversal_move_id = fields.Many2one(
        "account.move", string="Reversal Entry", readonly=True, copy=False
    )
    reversal_reason = fields.Char(tracking=True)
    # BRU-ITC-07: a real variance is accepted by an Import Approver who did not
    # assess the Bill of Entry nor type customs' figure, with a reason. The
    # accepted figure is pinned: any later change voids it.
    customs_total_by_id = fields.Many2one(
        "res.users", string="Customs Total Recorded By", readonly=True, copy=False
    )
    variance_accepted_by_id = fields.Many2one(
        "res.users", string="Variance Accepted By", readonly=True, copy=False
    )
    variance_accepted_on = fields.Datetime(string="Variance Accepted On", readonly=True, copy=False)
    variance_accepted_amount = fields.Monetary(
        string="Variance Accepted", readonly=True, copy=False
    )
    variance_reason = fields.Char(string="Variance Acceptance Reason", readonly=True, copy=False)
    cancelled_by_id = fields.Many2one(
        "res.users", string="Assessment Cancelled By", readonly=True, copy=False
    )
    remittance_flagged_on = fields.Date(string="Flagged Unmatched On", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("assessed", "Assessed"),
            ("paid", "Paid"),
            ("reversed", "Reversed / Cancelled"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "assessed_on",
            "assessed_by_id",
            "paid_on",
            "paid_by_id",
            "move_id",
            "reversal_move_id",
            "customs_total_by_id",
            "variance_accepted_by_id",
            "variance_accepted_on",
            "variance_accepted_amount",
            "variance_reason",
            "cancelled_by_id",
            "remittance_flagged_on",
            # computed from the lines; never written directly (M51 reads them)
            *_DUTY_FIELDS,
            "total_tax",
            "assessable_total",
        }

    def _locked(self) -> set:
        locked = set()
        if self.state != "draft":
            locked |= set(BOE_LOCK_ASSESSED)
        if self.state in ("paid", "reversed"):
            locked |= set(BOE_LOCK_PAID)
        if self.state == "reversed":
            locked |= {"reversal_reason"}
        if self.variance_accepted_by_id:
            locked |= {"customs_assessed_total"}
        return locked

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1:
            locked |= self._locked()
        return locked

    @api.depends(
        "line_ids.cd_amount",
        "line_ids.rd_amount",
        "line_ids.sd_amount",
        "line_ids.vat_amount",
        "line_ids.at_amount",
        "line_ids.ait_amount",
        "line_ids.assessable_value",
    )
    def _compute_totals(self):
        for rec in self:
            for fname in _DUTY_FIELDS:
                rec[fname] = round(sum(rec.line_ids.mapped(fname)), 2)
            rec.total_tax = round(sum(rec[f] for f in _DUTY_FIELDS), 2)
            rec.assessable_total = round(sum(rec.line_ids.mapped("assessable_value")), 2)

    @api.depends("customs_assessed_total", "total_tax")
    def _compute_variance(self):
        for rec in self:
            rec.duty_variance = (
                round((rec.customs_assessed_total or 0.0) - rec.total_tax, 2)
                if rec.customs_assessed_total
                else 0.0
            )

    @api.constrains("boe_no", "company_id", "state")
    def _check_unique_boe_no(self):
        for rec in self.filtered(lambda r: r.state != "reversed"):
            dup = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("boe_no", "=", rec.boe_no),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "!=", "reversed"),
                ]
            )
            if dup:
                raise ValidationError("Bill of Entry %s is already lodged." % rec.boe_no)

    @api.constrains("order_id")
    def _check_lines_of_order(self):
        for rec in self.sudo():
            rec.line_ids._check_order_line()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.boe", "IBOE/New")
        return super().create(vals_list)

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: r._locked(),
            "an assessed Bill of Entry is fixed, and a paid one is final: a correction is a "
            "reversal and a new Bill of Entry (BRU-ITC-11).",
        )
        retyped = (
            self.filtered(
                lambda r: changes(r, {"customs_assessed_total": vals["customs_assessed_total"]})
            )
            if self and "customs_assessed_total" in vals
            else self.browse()
        )
        result = super().write(vals)
        if retyped and not self.env.su:
            retyped._guarded().write({"customs_total_by_id": self.env.uid})
        if "boe_date" in vals or "order_id" in vals:
            self.filtered(lambda r: r.state == "draft").line_ids._boe_line_refresh()
        return result

    def action_assess(self):
        """Lodged and assessed: the computation is frozen at the rates in
        force on the lodgement date (BRU-ITC-05/08)."""
        require_group(self.env, OFFICER, "Assessing a Bill of Entry")
        required = [
            d.strip()
            for d in (param(self.env, PARAM_BOE_DOCS) or "bl,invoice,packing").split(",")
            if d.strip()
        ]
        for rec in self:
            if rec.state != "draft":
                raise UserError("Assess a draft bill of entry")
            if not rec.line_ids:
                raise UserError("A bill of entry needs at least one line")
            docs = (
                rec.env["fix.import.shipdoc"]
                .sudo()
                .search(
                    [("order_id", "=", rec.order_id.id), ("state", "in", ("received", "verified"))]
                )
            )
            missing = [d for d in required if d not in docs.mapped("doc_type")]
            if missing:
                labels = dict(rec.env["fix.import.shipdoc"]._fields["doc_type"].selection)
                raise UserError(
                    "Bill of Entry %s cannot be assessed: the document checklist is incomplete "
                    "(missing %s)." % (rec.boe_no, ", ".join(labels.get(d, d) for d in missing))
                )
            rec.cnf_agent_id._cnf_require_usable("Lodging Bill of Entry %s" % rec.boe_no)
            rec.env["fix.import.irc"]._irc_require_valid(
                rec.company_id, "Assessing Bill of Entry %s" % rec.boe_no
            )
            rec.order_id._import_check_eligibility("Assessing Bill of Entry %s" % rec.boe_no)
            rec.line_ids._boe_line_refresh()
            for line in rec.line_ids:
                if not line.order_line_id or line.order_line_id.order_id != rec.order_id:
                    raise UserError(
                        "Every BOE line must be a line of import order %s." % rec.order_id.name
                    )
                if not line.hs_id:
                    raise UserError("Every BOE line needs an HS classification before assessment")
                if line.hs_id.state != "ruled":
                    raise UserError(
                        "HS %s is not ruled: a Bill of Entry is assessed on ruled classifications."
                        % line.hs_id.hs_code
                    )
                if not line.tariff_id:
                    raise UserError(
                        "HS %s has no tariff row in force on %s."
                        % (line.hs_id.hs_code, rec.boe_date)
                    )
                if (line.assessable_value or 0.0) <= 0:
                    raise UserError("Every BOE line needs a positive assessable value")
                declared = sum(
                    rec.env["fix.import.boe.line"]
                    .sudo()
                    .search(
                        [
                            ("order_line_id", "=", line.order_line_id.id),
                            ("boe_id.state", "!=", "reversed"),
                        ]
                    )
                    .mapped("quantity")
                )
                if declared > line.order_line_id.quantity + 1e-6:
                    raise UserError(
                        "%s is declared for %.2f units on Bills of Entry but the order line has %.2f."
                        % (
                            line.order_line_id.part_id.display_name,
                            declared,
                            line.order_line_id.quantity,
                        )
                    )
            rec._guarded().write(
                {"state": "assessed", "assessed_on": today(rec), "assessed_by_id": rec.env.user.id}
            )
        return True

    def action_accept_variance(self, reason=None):
        """BRU-ITC-07: customs assessed a figure other than the computation and
        it stands. An Import Approver who neither assessed the entry nor typed
        customs' figure accepts it with a reason; it is then payable, at
        customs' figure."""
        require_group(self.env, APPROVER, "Accepting a duty variance")
        tol = param_float(self.env, PARAM_DUTY_VARIANCE, 0.0)
        for rec in self:
            if rec.state != "assessed":
                raise UserError("Accept the variance of an assessed Bill of Entry.")
            if not rec.customs_assessed_total:
                raise UserError(
                    "Record the customs-assessed total from the assessment notice first."
                )
            if abs(rec.duty_variance) <= tol + 0.005:
                raise UserError(
                    "Bill of Entry %s has no variance beyond the tolerance to accept." % rec.boe_no
                )
            why = (reason or "").strip()
            if not why:
                raise UserError("State why the variance is accepted.")
            require_other_person(
                rec.env,
                rec,
                "The variance on Bill of Entry %s" % rec.boe_no,
                rec.assessed_by_id,
                rec.customs_total_by_id,
            )
            rec.sudo()._guarded().write(
                {
                    "variance_accepted_by_id": rec.env.user.id,
                    "variance_accepted_on": fields.Datetime.now(),
                    "variance_accepted_amount": rec.duty_variance,
                    "variance_reason": why,
                }
            )
            rec.sudo().message_post(
                body="Variance of %.2f accepted by %s: %s"
                % (rec.duty_variance, rec.env.user.name, why)
            )
        return True

    def action_cancel_assessed(self, reason=None):
        """The other way out of an assessed entry: nothing is paid, so nothing
        posts; the number is free and a corrected Bill of Entry can be lodged.
        Decided by an Import Approver who did not assess it."""
        require_group(self.env, APPROVER, "Cancelling an assessed Bill of Entry")
        for rec in self:
            if rec.state != "assessed":
                raise UserError(
                    "Only an assessed Bill of Entry is cancelled (a paid one is reversed)."
                )
            why = (reason or "").strip()
            if not why:
                raise UserError("State why the assessment is cancelled.")
            require_other_person(
                rec.env, rec, "Cancelling Bill of Entry %s" % rec.boe_no, rec.assessed_by_id
            )
            rec.sudo()._guarded().write(
                {"state": "reversed", "reversal_reason": why, "cancelled_by_id": rec.env.user.id}
            )
        return True

    def action_pay(self):
        """Finance pays the assessed duty: the payment reference is recorded,
        the customs-assessed total must agree with the computation or carry an
        accepted variance, and the payment posts (capitalisable duty to the
        clearing account, import VAT and AT to input tax, AIT to tax advance,
        an accepted variance to the variance account)."""
        require_group(self.env, FINANCE, "Paying a Bill of Entry")
        tol = param_float(self.env, PARAM_DUTY_VARIANCE, 0.0)
        for rec in self:
            if rec.state != "assessed":
                raise UserError("Pay an assessed bill of entry")
            if not (rec.payment_ref or "").strip():
                raise UserError(
                    "Record the duty payment reference (treasury challan / A-challan) first."
                )
            if not rec.customs_assessed_total:
                raise UserError(
                    "Record the customs-assessed total from the assessment notice first."
                )
            accepted = (
                rec.variance_accepted_by_id
                and abs(rec.duty_variance - rec.variance_accepted_amount) <= 0.005
            )
            if abs(rec.duty_variance) > tol + 0.005 and not accepted:
                raise UserError(
                    "Customs assessed %.2f but the computed duty and tax is %.2f (variance %.2f, "
                    "tolerance %.2f): an Import Approver accepts the variance, or the assessment "
                    "is cancelled, before paying (BRU-ITC-07)."
                    % (rec.customs_assessed_total, rec.total_tax, rec.duty_variance, tol)
                )
            company = rec.company_id
            capitalisable = rec.cd_amount + rec.rd_amount + rec.sd_amount
            accounts = {}
            for role, amount in (
                ("duty_clearing", capitalisable),
                ("vat_input", rec.vat_amount),
                ("at_input", rec.at_amount),
                ("ait_advance", rec.ait_amount),
                ("variance", rec.duty_variance if accepted else 0.0),
            ):
                if amount:
                    accounts[role] = import_account(rec.env, company, role)
            journal = import_journal(rec.env, company, "payment")
            paid = rec.customs_assessed_total if accepted else rec.total_tax
            ref = "Bill of Entry %s duty payment %s" % (rec.boe_no, rec.payment_ref)
            lines = [
                (accounts.get("duty_clearing"), "CD + RD + SD %s" % rec.boe_no, capitalisable),
                (accounts.get("vat_input"), "Import VAT %s" % rec.boe_no, rec.vat_amount),
                (accounts.get("at_input"), "Advance tax %s" % rec.boe_no, rec.at_amount),
                (accounts.get("ait_advance"), "AIT %s" % rec.boe_no, rec.ait_amount),
                (
                    accounts.get("variance"),
                    "Accepted duty variance %s" % rec.boe_no,
                    rec.duty_variance,
                ),
                (journal.default_account_id, ref, -paid),
            ]
            move = post_import_move(
                rec.env,
                company,
                journal,
                today(rec),
                ref,
                [line for line in lines if line[0] and line[2]],
                operating_unit=rec.operating_unit_id,
            )
            rec._guarded().write(
                {
                    "state": "paid",
                    "paid_on": today(rec),
                    "paid_by_id": rec.env.user.id,
                    "move_id": move.id or False,
                }
            )
            publish(
                rec.env,
                "import.duty_paid",
                "fix.import.boe",
                rec.id,
                {
                    "boe": rec.boe_no,
                    "order": rec.order_id.name,
                    "vat": rec.vat_amount,
                    "at": rec.at_amount,
                    "ait": rec.ait_amount,
                    "inventoriable": capitalisable,
                },
            )
        return True

    def action_reverse(self, reason=None):
        """A paid Bill of Entry is final; a correction reverses it (the
        payment entry is reversed) and a new one is lodged. M44-7: refused once
        the goods are received, because stock and the landed cost stand on it;
        before that, a cleared shipment goes back to Arrived and its order to
        In Customs, so nothing is received against a reversed entry."""
        require_group(self.env, FINANCE, "Reversing a Bill of Entry")
        for rec in self:
            if rec.state != "paid":
                raise UserError("Only a paid Bill of Entry is reversed.")
            why = (reason or rec.reversal_reason or "").strip()
            if not why:
                raise UserError("State why the Bill of Entry is reversed.")
            final = (
                rec.env["fix.import.landed"]
                .sudo()
                .search_count(
                    [
                        ("order_id", "=", rec.order_id.id),
                        ("sheet_type", "=", "final"),
                        ("state", "=", "finalised"),
                    ]
                )
            )
            if final:
                raise UserError(
                    "The landed cost of %s is final on this Bill of Entry; it cannot be reversed."
                    % rec.order_id.name
                )
            if rec.order_id.state in ("received", "landed", "closed"):
                raise UserError(
                    "Import %s is already received on this Bill of Entry; it cannot be reversed."
                    % rec.order_id.name
                )
            reversal = rec.env["account.move"]
            if rec.move_id:
                reversal = rec.move_id.sudo()._reverse_moves(
                    [{"ref": "Reversal of %s: %s" % (rec.move_id.ref, why), "date": today(rec)}]
                )
                reversal.action_post()
            vals = {"state": "reversed", "reversal_move_id": reversal.id or False}
            if why != (rec.reversal_reason or ""):
                vals["reversal_reason"] = why
            rec._guarded().write(vals)
            for arrival in (
                rec.env["fix.import.arrival"]
                .sudo()
                .search([("order_id", "=", rec.order_id.id), ("state", "=", "cleared")])
            ):
                arrival._guarded().write(
                    {"state": "arrived", "cleared_on": False, "cleared_by_id": False}
                )
            rec.order_id._import_set_state("customs", ("cleared",))
        return True

    # ---- scorecard 25: Bill of Entry to remittance ------------------------------
    @api.model
    def _cron_boe_remittance_match(self):
        """Daily: a paid Bill of Entry with no linked remittance past the window
        (cd_import_order.boe_remittance_match_days, default 120 days for
        Bangladesh Bank's 4-month guideline; Finance confirms) is flagged, and
        so is a remittance with no Bill of Entry. Once each."""
        days = int(param_float(self.env, PARAM_BOE_REMITTANCE_DAYS, 120.0))
        day = today(self)
        cutoff = day - timedelta(days=days)
        Payment = self.env["fix.import.lc.payment"].sudo()
        bills = self.sudo().search(
            [
                ("state", "=", "paid"),
                ("boe_date", "<", cutoff),
                ("remittance_flagged_on", "=", False),
            ]
        )
        flagged = 0
        for bill in bills:
            if Payment.search_count([("boe_id", "=", bill.id)]):
                continue
            order = bill.order_id
            note = (
                "Bill of Entry %s (lodged %s) has no remittance matched %d days on: link the LC "
                "payment or report it to the AD bank." % (bill.boe_no, bill.boe_date, days)
            )
            order.message_post(body=note)
            schedule_alert(
                order,
                "Unmatched Bill of Entry",
                note,
                alert_users(bill, None, bill.paid_by_id or order.create_uid),
            )
            bill._guarded().write({"remittance_flagged_on": day})
            flagged += 1
        payments = Payment.search(
            [
                ("boe_id", "=", False),
                ("payment_date", "<", cutoff),
                ("match_flagged_on", "=", False),
            ]
        )
        for payment in payments:
            order = payment.lc_id.order_id
            note = (
                "LC payment %s (%s) has no Bill of Entry %d days on: link it or report it to the "
                "AD bank." % (payment.reference, payment.payment_date, days)
            )
            order.message_post(body=note)
            schedule_alert(
                order,
                "Remittance without a Bill of Entry",
                note,
                alert_users(payment, None, payment.recorded_by_id),
            )
            payment.write({"match_flagged_on": day})
            flagged += 1
        return flagged


class FixImportBoeLine(models.Model):
    """One declared line. Its assessable value, HS, rates and amounts are a
    SNAPSHOT computed from the import order line and the tariff in force on
    the lodgement date (FR-ITC-033), refreshed while the Bill of Entry is a
    draft and frozen from assessment. None of them is typed."""

    _name = "fix.import.boe.line"
    _description = "Bill of Entry Line"
    _order = "boe_id, id"
    _inherit = ["fix.guarded.mixin"]

    boe_id = fields.Many2one("fix.import.boe", required=True, ondelete="cascade", index=True)
    company_id = _company_rel("boe_id")
    operating_unit_id = _ou_rel("boe_id")
    order_line_id = fields.Many2one(
        "fix.import.order.line", string="Import Order Line", ondelete="restrict"
    )
    quantity = fields.Float(default=0.0)
    description = fields.Char()
    currency_id = fields.Many2one(related="boe_id.currency_id")
    # ---- snapshot (guarded) ----
    hs_id = fields.Many2one("fix.import.hs", string="HS Classification", ondelete="restrict")
    tariff_id = fields.Many2one("fix.import.tariff", string="Tariff Row", ondelete="restrict")
    cif_value_bdt = fields.Float(string="CIF (BDT)")
    landing_charge_pct = fields.Float(string="Landing Charge %")
    assessable_value = fields.Float(string="Assessable Value")
    cd_rate = fields.Float(string="CD %")
    rd_rate = fields.Float(string="RD %")
    sd_rate = fields.Float(string="SD %")
    vat_rate = fields.Float(string="VAT %")
    at_rate = fields.Float(string="AT %")
    ait_rate = fields.Float(string="AIT %")
    formula_version = fields.Char()
    cd_amount = fields.Monetary(string="CD")
    rd_amount = fields.Monetary(string="RD")
    sd_amount = fields.Monetary(string="SD")
    vat_amount = fields.Monetary(string="VAT")
    at_amount = fields.Monetary(string="AT")
    ait_amount = fields.Monetary(string="AIT")

    _SNAPSHOT = (
        "hs_id",
        "tariff_id",
        "cif_value_bdt",
        "landing_charge_pct",
        "assessable_value",
        "cd_rate",
        "rd_rate",
        "sd_rate",
        "vat_rate",
        "at_rate",
        "ait_rate",
        "formula_version",
        *_DUTY_FIELDS,
    )
    _qty_non_negative = models.Constraint(
        "CHECK (quantity >= 0)", "A declared quantity cannot be negative"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._SNAPSHOT)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.boe_id.state != "draft":
            locked |= {"order_line_id", "quantity", "description", "boe_id"}
        return locked

    @api.constrains("order_line_id", "boe_id")
    def _check_order_line(self):
        """The form's domains are static, so the picker cannot be narrowed to
        this Bill of Entry's order: the save refuses another order's line."""
        for rec in self.sudo():
            ol = rec.order_line_id
            if ol and ol.order_id != rec.boe_id.order_id:
                raise ValidationError(
                    "%s is not a line of import order %s."
                    % (ol.display_name, rec.boe_id.order_id.name)
                )

    def _boe_line_values(self):
        """FR-ITC-033: AV = CIF x FX + landing charge; CD = AV x cd; RD = AV x rd;
        SD = (AV + CD + RD) x sd; VAT = (AV + CD + RD + SD) x vat;
        AT = (AV + CD + SD) x at; AIT = AV x ait."""
        self.ensure_one()
        ol = self.order_line_id
        boe = self.boe_id
        order = ol.order_id
        qty = self.quantity or 0.0
        share = (qty / ol.quantity) if ol.quantity else 0.0
        cif = (ol.cif_amount or 0.0) * share * (order.fx_rate or 0.0)
        lc_pct = param_float(self.env, PARAM_LANDING_CHARGE, 1.0)
        av = cif * (1.0 + lc_pct / 100.0)
        hs = ol.hs_id
        tariff = (
            self.env["fix.import.tariff"]._tariff_for(boe.company_id, hs.hs_code, boe.boe_date)
            if hs
            else self.env["fix.import.tariff"]
        )
        r = {f: (tariff[f] if tariff else 0.0) / 100.0 for f in _RATE_FIELDS}
        cd = av * r["cd_pct"]
        rd = av * r["rd_pct"]
        sd = (av + cd + rd) * r["sd_pct"]
        vat = (av + cd + rd + sd) * r["vat_pct"]
        at = (av + cd + sd) * r["at_pct"]
        ait = av * r["ait_pct"]
        return {
            "hs_id": hs.id or False,
            "tariff_id": tariff.id or False,
            "cif_value_bdt": round(cif, 2),
            "landing_charge_pct": lc_pct,
            "assessable_value": round(av, 2),
            "cd_rate": r["cd_pct"] * 100,
            "rd_rate": r["rd_pct"] * 100,
            "sd_rate": r["sd_pct"] * 100,
            "vat_rate": r["vat_pct"] * 100,
            "at_rate": r["at_pct"] * 100,
            "ait_rate": r["ait_pct"] * 100,
            "formula_version": FORMULA_VERSION,
            "cd_amount": round(cd, 2),
            "rd_amount": round(rd, 2),
            "sd_amount": round(sd, 2),
            "vat_amount": round(vat, 2),
            "at_amount": round(at, 2),
            "ait_amount": round(ait, 2),
        }

    def _boe_line_refresh(self):
        for rec in self.sudo():
            if rec.boe_id.state != "draft" or not rec.order_line_id:
                continue
            rec._guarded().write(rec._boe_line_values())

    def _parent_locked(self):
        return not self.env.su and any(rec.boe_id.state != "draft" for rec in self.sudo())

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("order_line_id") and not vals.get("quantity"):
                vals["quantity"] = (
                    self.env["fix.import.order.line"].browse(vals["order_line_id"]).quantity
                )
        records = super().create(vals_list)
        if records._parent_locked():
            raise UserError("Lines are added to a draft Bill of Entry only.")
        records._boe_line_refresh()
        return records

    def write(self, vals):
        if (
            self
            and self._parent_locked()
            and not self._fix_guard_has_token()
            and changes(self, vals)
        ):
            raise UserError(
                "The lines of an assessed or paid Bill of Entry are final: a correction is a "
                "reversal and a new Bill of Entry (BRU-ITC-11)."
            )
        result = super().write(vals)
        if {"order_line_id", "quantity", "boe_id"} & set(vals) and not self._fix_guard_has_token():
            self._boe_line_refresh()
        return result

    def unlink(self):
        if self._parent_locked():
            raise UserError("The lines of an assessed or paid Bill of Entry cannot be deleted.")
        return super().unlink()


# =============================================================== landed cost
LANDED_INPUTS = (
    "order_id",
    "sheet_type",
    "freight",
    "insurance",
    "clearing_charges",
    "bank_charges",
    "other_charges",
    "duty_estimate",
    "allocation_method",
    "currency_id",
)


class FixImportLanded(models.Model):
    """A landed-cost sheet. An ESTIMATE is posted at shipment and applied to
    stock at receipt (the provisional cost, FR-ITC-036). The FINAL sheet
    takes its duty from the paid Bills of Entry (CD + RD + SD only: import
    VAT, AT and AIT are recoverable and never in landed cost, BRU-ITC-02),
    is approved by an Import Approver who did not prepare it, revalues the
    stock still on hand through M15 and posts the true-up to the GL; the part
    already consumed goes to the variance account (cost of sales)."""

    _name = "fix.import.landed"
    _description = "Landed Cost Sheet"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    name = fields.Char(required=True, default="New")
    order_id = _order_rel()
    company_id = _company_rel("order_id")
    operating_unit_id = _ou_rel("order_id")
    sheet_type = fields.Selection(
        [("estimate", "Estimate (at shipment)"), ("final", "Final (from the paid Bills of Entry)")],
        required=True,
        default="final",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    freight = fields.Monetary(currency_field="currency_id")
    insurance = fields.Monetary(currency_field="currency_id")
    clearing_charges = fields.Monetary(currency_field="currency_id", string="Clearing, Port & C&F")
    bank_charges = fields.Monetary(
        currency_field="currency_id",
        string="LC & Bank Charges",
        help="LC opening commission, amendment, acceptance, negotiation, SWIFT and handling "
        "charges of this consignment (FR-ITC-018), capitalised like the clearing charges.",
    )
    other_charges = fields.Monetary(
        currency_field="currency_id",
        string="Other (not capitalised)",
        help="Legacy field. Charges that are not inventoriable are expensed through AP; "
        "a sheet carrying them is not finalised.",
    )
    duty_estimate = fields.Monetary(currency_field="currency_id", string="Estimated CD + RD + SD")
    duty = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_duty",
        store=True,
        string="Duty (CD + RD + SD)",
    )
    vat_amount = fields.Monetary(
        compute="_compute_duty", store=True, string="Import VAT (recoverable)"
    )
    at_amount = fields.Monetary(compute="_compute_duty", store=True, string="AT (recoverable)")
    ait_amount = fields.Monetary(compute="_compute_duty", store=True, string="AIT (tax advance)")
    total_landed = fields.Monetary(compute="_compute_total", store=True, string="Total Landed")
    allocation_method = fields.Selection(
        [("value", "By Value"), ("qty", "By Quantity")],
        required=True,
        default="value",
    )
    line_ids = fields.One2many("fix.import.landed.line", "landed_id", string="Allocation")
    state = fields.Selection(
        [("draft", "Draft"), ("estimated", "Estimate Posted"), ("finalised", "Finalised")],
        required=True,
        default="draft",
        tracking=True,
    )
    amounts_changed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    posted_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    finalised_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    finalised_on = fields.Date(readonly=True, copy=False)
    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True, copy=False)
    estimate_id = fields.Many2one(
        "fix.import.landed", string="Estimate Trued Up", readonly=True, copy=False
    )
    revalued_amount = fields.Monetary(readonly=True, copy=False, string="Stock Revaluation")
    variance_amount = fields.Monetary(readonly=True, copy=False, string="Variance (consumed stock)")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "amounts_changed_by_id",
            "posted_by_id",
            "finalised_by_id",
            "finalised_on",
            "move_id",
            "estimate_id",
            "revalued_amount",
            "variance_amount",
            # computed from the paid Bills of Entry and the sheet's charges
            "duty",
            "vat_amount",
            "at_amount",
            "ait_amount",
            "total_landed",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(LANDED_INPUTS)
        if len(self) == 1 and self.sheet_type == "final":
            locked |= {"duty_estimate"}
        return locked

    @api.depends(
        "sheet_type",
        "duty_estimate",
        "order_id.boe_ids.state",
        "order_id.boe_ids.cd_amount",
        "order_id.boe_ids.rd_amount",
        "order_id.boe_ids.sd_amount",
        "order_id.boe_ids.vat_amount",
        "order_id.boe_ids.at_amount",
        "order_id.boe_ids.ait_amount",
    )
    def _compute_duty(self):
        for rec in self:
            if rec.sheet_type == "estimate":
                rec.duty = rec.duty_estimate or 0.0
                rec.vat_amount = rec.at_amount = rec.ait_amount = 0.0
                continue
            paid = rec.order_id.boe_ids.filtered(lambda b: b.state == "paid")
            rec.duty = round(sum(b.cd_amount + b.rd_amount + b.sd_amount for b in paid), 2)
            rec.vat_amount = round(sum(paid.mapped("vat_amount")), 2)
            rec.at_amount = round(sum(paid.mapped("at_amount")), 2)
            rec.ait_amount = round(sum(paid.mapped("ait_amount")), 2)

    @api.depends("freight", "insurance", "duty", "clearing_charges", "bank_charges")
    def _compute_total(self):
        # BRU-ITC-02 / FR-ITC-034: only inventoriable factors.
        for rec in self:
            rec.total_landed = round(
                (rec.freight or 0.0)
                + (rec.insurance or 0.0)
                + (rec.duty or 0.0)
                + (rec.clearing_charges or 0.0)
                + (rec.bank_charges or 0.0),
                2,
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.landed", "ILND/New")
        records = super().create(vals_list)
        if not self.env.su:
            records._guarded().write({"amounts_changed_by_id": self.env.uid})
        return records

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(LANDED_INPUTS) if r.state != "draft" else set(),
            "a posted or finalised landed-cost sheet is final.",
        )
        inputs = {k: vals[k] for k in LANDED_INPUTS if k in vals}
        changed = self.filtered(lambda r: inputs and changes(r, inputs)) if self else self
        result = super().write(vals)
        if changed and not self.env.su:
            changed._guarded().write({"amounts_changed_by_id": self.env.uid})
        return result

    # ---- allocation -------------------------------------------------------------
    def _landed_allocate(self, total):
        """[(order_line, amount)] across the order lines by the declared basis
        (BRU-ITC-09: the allocation sums to the total exactly)."""
        self.ensure_one()
        lines = self.order_id.line_ids
        if not lines:
            raise UserError(
                "Import order %s has no lines to allocate the landed cost to." % self.order_id.name
            )
        basis = {
            ln.id: (ln.fob_amount if self.allocation_method == "value" else ln.quantity)
            for ln in lines
        }
        whole = sum(basis.values())
        if whole <= 0:
            raise UserError("The allocation basis of %s is zero." % self.order_id.name)
        out, running = [], 0.0
        for idx, ln in enumerate(lines):
            if idx == len(lines) - 1:
                amount = round(total - running, 2)
            else:
                amount = round(total * basis[ln.id] / whole, 2)
                running += amount
            out.append((ln, amount, basis[ln.id]))
        return out

    def _landed_write_lines(self, allocation):
        Line = self.env["fix.import.landed.line"].sudo()
        self.sudo().line_ids.unlink()
        for ln, amount, basis in allocation:
            Line.create(
                {
                    "landed_id": self.id,
                    "order_line_id": ln.id,
                    "basis": basis,
                    "amount": amount,
                    "unit_amount": round(amount / ln.quantity, 4) if ln.quantity else 0.0,
                }
            )

    # ---- estimate -----------------------------------------------------------------
    def action_post_estimate(self):
        """The provisional landed cost, recorded at shipment and applied to
        stock when the consignment is received."""
        require_group(self.env, OFFICER, "Posting a landed-cost estimate")
        for rec in self:
            if rec.sheet_type != "estimate":
                raise UserError(
                    "Only an estimate sheet is posted as an estimate; a final sheet is finalised."
                )
            if rec.state != "draft":
                raise UserError("Post a draft estimate.")
            if rec.order_id.state not in ("shipped", "customs", "cleared"):
                raise UserError(
                    "An estimate is posted between shipment and receipt (order %s is %s)."
                    % (rec.order_id.name, rec.order_id.state)
                )
            other = self.sudo().search_count(
                [
                    ("order_id", "=", rec.order_id.id),
                    ("sheet_type", "=", "estimate"),
                    ("state", "=", "estimated"),
                    ("id", "!=", rec.id),
                ]
            )
            if other:
                raise UserError(
                    "Import order %s already has a posted estimate." % rec.order_id.name
                )
            if rec.total_landed <= 0:
                raise UserError("The estimate is zero.")
            if rec.other_charges:
                raise UserError("Other charges are not capitalised: remove them from the sheet.")
            company = rec.company_id
            import_account(rec.env, company, "inventory")
            import_account(rec.env, company, "landed_accrual")
            import_journal(rec.env, company)
            rec._landed_write_lines(rec._landed_allocate(rec.total_landed))
            rec._guarded().write({"state": "estimated", "posted_by_id": rec.env.user.id})
        return True

    def _landed_post_estimate_entry(self, receipt):
        """At receipt: the estimate enters stock through the receipt's unit
        cost; the GL takes Dr Inventory / Cr Landed-cost accrual."""
        self.ensure_one()
        company = self.company_id
        move = post_import_move(
            self.env,
            company,
            import_journal(self.env, company),
            today(self),
            "Provisional landed cost %s (%s)" % (self.name, receipt.name),
            [
                (
                    import_account(self.env, company, "inventory"),
                    "Provisional landed cost %s" % self.order_id.name,
                    self.total_landed,
                ),
                (
                    import_account(self.env, company, "landed_accrual"),
                    "Landed-cost accrual %s" % self.order_id.name,
                    -self.total_landed,
                ),
            ],
            operating_unit=self.operating_unit_id,
        )
        self.sudo()._guarded().write({"move_id": move.id or False})

    # ---- final ----------------------------------------------------------------------
    def action_finalise(self):
        require_group(self.env, APPROVER, "Finalising a landed cost")
        Onhand = self.env["fix.stock.onhand"].sudo()
        for rec in self:
            order = rec.order_id
            if rec.sheet_type != "final":
                raise UserError("An estimate is posted, not finalised; finalise the final sheet.")
            if rec.state != "draft":
                raise UserError("Finalise a draft landed-cost sheet")
            require_other_person(
                rec.env, rec, "Landed-cost sheet %s" % rec.name, rec.amounts_changed_by_id
            )
            if self.sudo().search_count(
                [
                    ("order_id", "=", order.id),
                    ("sheet_type", "=", "final"),
                    ("state", "=", "finalised"),
                    ("id", "!=", rec.id),
                ]
            ):
                raise UserError("Import order %s already has a final landed cost." % order.name)
            if order.state != "received" or not order.receipt_id:
                raise UserError(
                    "The final landed cost of %s is applied to received stock: receive the "
                    "consignment first (it is %s)." % (order.name, order.state)
                )
            boes = order.boe_ids.filtered(lambda b: b.state != "reversed")
            if not boes.filtered(lambda b: b.state == "paid") or boes.filtered(
                lambda b: b.state != "paid"
            ):
                raise UserError(
                    "Every Bill of Entry of %s must be paid before the final landed cost."
                    % order.name
                )
            if rec.other_charges:
                raise UserError(
                    "Other charges (%.2f) are not inventoriable: expense them through AP (M52), or "
                    "record port and handling charges under Clearing." % rec.other_charges
                )
            if not hasattr(Onhand, "_fix_revalue") or not hasattr(Onhand, "_bucket"):
                raise UserError(
                    "The M15 stock revaluation service (fix.stock.onhand._fix_revalue) is not installed."
                )
            estimate = self.sudo().search(
                [
                    ("order_id", "=", order.id),
                    ("sheet_type", "=", "estimate"),
                    ("state", "=", "estimated"),
                ],
                limit=1,
            )
            est_by_line = {al.order_line_id.id: al.amount for al in estimate.line_ids}
            est_total = round(sum(est_by_line.values()), 2) if estimate.move_id else 0.0
            if not estimate.move_id:
                est_by_line = {}
            allocation = rec._landed_allocate(rec.total_landed)
            svc = round(
                (rec.freight or 0.0)
                + (rec.insurance or 0.0)
                + (rec.clearing_charges or 0.0)
                + (rec.bank_charges or 0.0),
                2,
            )
            plan, stock_total, var_total = [], 0.0, 0.0
            for ln, amount, _basis in allocation:
                diff = round(amount - est_by_line.get(ln.id, 0.0), 2)
                bucket = Onhand._bucket(ln.part_id, order.location_id, "owned")
                on_hand = bucket.qty if bucket else 0.0
                share = min(on_hand, ln.quantity) / ln.quantity if ln.quantity else 0.0
                to_stock = round(diff * share, 2)
                plan.append((ln, to_stock))
                stock_total += to_stock
                var_total += round(diff - to_stock, 2)
            stock_total, var_total = round(stock_total, 2), round(var_total, 2)
            company = rec.company_id
            # every account this entry needs, before anything moves
            acc = {}
            for role, needed in (
                ("inventory", stock_total),
                ("variance", var_total),
                ("duty_clearing", rec.duty),
                ("landed_accrual", svc or est_total),
            ):
                if needed:
                    acc[role] = import_account(rec.env, company, role)
            journal = import_journal(rec.env, company)
            ref = "Final landed cost %s (%s)" % (rec.name, order.name)
            for ln, to_stock in plan:
                if to_stock:
                    Onhand._fix_revalue(ln.part_id, order.location_id, "owned", to_stock, ref)
            lines = [
                (acc.get("landed_accrual"), "Reverse provisional landed cost", est_total),
                (acc.get("duty_clearing"), "CD + RD + SD capitalised", -rec.duty),
                (acc.get("landed_accrual"), "Freight, insurance, clearing and bank charges", -svc),
                (acc.get("inventory"), "Landed-cost revaluation of stock on hand", stock_total),
                (acc.get("variance"), "Landed cost of stock already consumed", var_total),
            ]
            move = post_import_move(
                rec.env,
                company,
                journal,
                today(rec),
                ref,
                [line for line in lines if line[0] and line[2]],
                operating_unit=rec.operating_unit_id,
            )
            rec._landed_write_lines(allocation)
            rec._guarded().write(
                {
                    "state": "finalised",
                    "finalised_by_id": rec.env.user.id,
                    "finalised_on": today(rec),
                    "move_id": move.id or False,
                    "estimate_id": estimate.id or False,
                    "revalued_amount": stock_total,
                    "variance_amount": var_total,
                }
            )
            order._import_set_state("landed", ("received",))
            publish(
                rec.env,
                "landed_cost.finalised",
                "fix.import.landed",
                rec.id,
                {
                    "order": order.name,
                    "total_landed": rec.total_landed,
                    "estimate": est_total,
                    "revalued": stock_total,
                    "variance": var_total,
                    "recoverable": {
                        "vat": rec.vat_amount,
                        "at": rec.at_amount,
                        "ait": rec.ait_amount,
                    },
                },
            )
        return True


class FixImportLandedLine(models.Model):
    """The allocation of a sheet across the order lines (FR-ITC-035).
    Written by the sheet's own actions only."""

    _name = "fix.import.landed.line"
    _description = "Landed Cost Allocation"
    _order = "landed_id, id"

    landed_id = fields.Many2one("fix.import.landed", required=True, ondelete="cascade", index=True)
    company_id = _company_rel("landed_id")
    operating_unit_id = _ou_rel("landed_id")
    order_line_id = fields.Many2one("fix.import.order.line", required=True, ondelete="cascade")
    part_id = fields.Many2one(related="order_line_id.part_id")
    quantity = fields.Float(related="order_line_id.quantity")
    currency_id = fields.Many2one(related="landed_id.currency_id")
    basis = fields.Float()
    amount = fields.Monetary(currency_field="currency_id")
    unit_amount = fields.Float(string="Per Unit")
