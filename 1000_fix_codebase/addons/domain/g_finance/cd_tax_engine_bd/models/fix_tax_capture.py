# cd_tax_engine_bd: M51 sub-module capture audit (2026-11-17).
#
# Three spec records the M51 workspace had no way to capture:
#
#   * fix.marketplace.tax.model (FR-TAX-045 P0, BRU-TAX-16/17 H, decision
#     D-03): the single declared principal-or-agent VAT position for
#     marketplace sales. It is a statutory master row: proposed, confirmed by
#     the external tax opinion (the adviser step), activated by the CFO who
#     did neither, and never edited in place. Until one is active the
#     determination service REFUSES (get_declared): the position is absent,
#     never defaulted.
#   * fix.vat.return.amendment (BRU-TAX-15 H, section 8.1 "Filed -> Amended"):
#     a filed Mushak 9.1 is never altered. An error found later, or an NBR
#     query, is corrected by a separately evidenced amendment: the corrected
#     totals, the working papers, CFO approval by someone other than the
#     preparer, and the NBR acknowledgement of the amended return.
#   * fix.tax.notice (AUT-TAX-22, section 3.1 item 22): an NBR query, audit
#     notice, assessment or show-cause with its scope, response deadline and
#     named owner. It generates the audit pack for its scope, reminds the
#     owner before the deadline and escalates when overdue; the response is
#     recorded with its evidence and the notice is closed by an Accounting
#     Administrator who did not write the response.
from __future__ import annotations

from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_tax_master import CFO_GROUP, MANAGER_GROUP, tax_alert
from .fix_tax_returns import FINANCE_USER_GROUPS

LOCK_EXEMPT = {"message_main_attachment_id", "activity_ids", "message_follower_ids"}
NOTICE_REMINDER_PARAM = "cd_tax_engine_bd.notice_reminder_days"
NOTICE_REMINDER_DEFAULT = 5


def _require_finance(env, what):
    if env.su or any(env.user.has_group(g) for g in FINANCE_USER_GROUPS):
        return
    raise UserError("%s needs the Accountant role." % what)


def _require_manager(env, what):
    if env.su or env.user.has_group(MANAGER_GROUP):
        return
    raise UserError("%s needs the Accounting Administrator role." % what)


def _require_cfo(env, what):
    if env.su or env.user.has_group(CFO_GROUP):
        return
    group = env.ref(CFO_GROUP, raise_if_not_found=False)
    raise UserError("%s needs the %s role." % (what, group.name if group else CFO_GROUP))


def _require_other(env, makers, what):
    if not env.su and env.user in makers:
        raise UserError(
            "Segregation of duties: %s is decided by someone other than the person who "
            "prepared it." % what
        )


def _locked_write(records, vals, open_states, what):
    """Refuse a plain write to a record that has left its editable states."""
    if records.env.su or records._fix_guard_has_token():
        return
    if not set(vals) - LOCK_EXEMPT:
        return
    if any(rec.state not in open_states for rec in records):
        raise UserError("%s is a record of what was decided and cannot be edited." % what)


# ------------------------------------------------------------------ marketplace
MARKETPLACE_MODELS = [
    ("principal", "Principal: VAT on the full sale value"),
    ("agent", "Agent: VAT on the commission and platform fees only"),
]
BASIS_OF_CHARGE = {"principal": "gross_sale", "agent": "commission"}


class FixMarketplaceTaxModel(models.Model):
    """The D-03 declared marketplace VAT position, one per company at a time."""

    _name = "fix.marketplace.tax.model"
    _description = "Marketplace VAT Model (D-03 Declared Position)"
    _inherit = ["fix.tax.effective.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "company_id, date_from desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", help="The declared position is company-wide: leave empty"
    )
    model = fields.Selection(
        MARKETPLACE_MODELS, string="Declared Model", required=True, tracking=True
    )
    basis_of_charge = fields.Selection(
        [("gross_sale", "Gross sale value"), ("commission", "Commission and platform fees")],
        string="VAT Charged On",
        compute="_compute_basis",
        store=True,
    )
    rate = fields.Float(string="VAT Rate (%)", required=True, digits=(6, 3), tracking=True)
    external_opinion_ref = fields.Char(
        string="External Tax Opinion",
        required=True,
        tracking=True,
        help="Reference of the external tax opinion that settles decision D-03.",
    )
    opinion_file = fields.Binary(string="Opinion (file)", attachment=True, copy=False)
    opinion_filename = fields.Char(string="Opinion File Name", copy=False)

    @api.depends("model")
    def _compute_basis(self):
        for row in self:
            row.basis_of_charge = BASIS_OF_CHARGE.get(row.model) or False

    @api.depends("model", "rate", "company_id")
    def _compute_display_name(self):
        labels = dict(MARKETPLACE_MODELS)
        for row in self:
            row.display_name = "%s: %s @ %g%%" % (
                row.company_id.name or "",
                (labels.get(row.model) or "").split(":")[0],
                row.rate,
            )

    def _fix_master_key_domain(self):
        return [("company_id", "=", self.company_id.id)]

    @api.constrains("rate", "date_from", "date_to", "company_id", "state", "model")
    def _check_position(self):
        for row in self:
            if not 0 < row.rate <= 100:
                raise ValidationError(
                    "The VAT rate of the declared position is above 0 and at most 100."
                )
            if row._overlaps([("company_id", "=", row.company_id.id)]):
                raise ValidationError(
                    "BRU-TAX-16: %s already has a declared marketplace model in force in an "
                    "overlapping window. The model cannot vary; a change is a new proposal "
                    "whose activation closes the old one." % row.company_id.name
                )

    def action_activate(self):
        for row in self:
            if not row.opinion_file:
                raise UserError(
                    "BRU-TAX-17: attach the external tax opinion that settles D-03 before "
                    "the marketplace model is activated."
                )
        return super().action_activate()

    @api.model
    def get_declared(self, company=None, on_date=None):
        """The position in force, or a refusal: marketplace determination is
        never defaulted (BRU-TAX-17, AUT-TAX-17)."""
        company = company or self.env.company
        on_date = on_date or fields.Date.context_today(self)
        row = self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("state", "=", "active"),
                *self._window_domain(on_date),
            ],
            limit=1,
        )
        if not row:
            raise UserError(
                "BRU-TAX-17: no marketplace VAT model is declared for %s on %s (decision "
                "D-03 is not settled). Marketplace determination is refused, not defaulted."
                % (company.name, on_date)
            )
        if row.signoff_state != "signed":
            raise UserError(
                "BRU-TAX-17: the marketplace VAT model of %s is not signed off by the "
                "adviser and the CFO; marketplace determination is refused." % company.name
            )
        return row

    @api.model
    def determine(self, sale_value, commission_value, company=None, on_date=None):
        """VAT base and VAT under the declared model: the full sale value as
        principal, the commission and fees as agent."""
        row = self.get_declared(company, on_date)
        base = sale_value if row.model == "principal" else commission_value
        base = round(float(base or 0.0), 2)
        return {
            "model": row.model,
            "base": base,
            "rate": row.rate,
            "vat": round(base * row.rate / 100.0, 2),
            "declared_id": row.id,
            "opinion": row.external_opinion_ref,
        }


# ------------------------------------------------------------- VAT return amendment
AMENDMENT_REASONS = [
    ("self_identified", "Error we found ourselves"),
    ("nbr_query", "NBR query"),
    ("nbr_audit", "NBR audit / assessment"),
]


class FixVatReturnAmendment(models.Model):
    """A separately evidenced amendment of a filed Mushak 9.1 (BRU-TAX-15)."""

    _name = "fix.vat.return.amendment"
    _description = "Mushak 9.1 Amendment"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(readonly=True, copy=False, default="New", index=True)
    return_id = fields.Many2one(
        "fix.vat.return",
        string="Filed Return",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("state", "=", "filed")],
    )
    company_id = fields.Many2one(related="return_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="return_id.operating_unit_id", store=True)
    currency_id = fields.Many2one(related="return_id.currency_id")
    period = fields.Char(related="return_id.period", store=True)
    reason_type = fields.Selection(AMENDMENT_REASONS, string="Why", required=True)
    notice_id = fields.Many2one("fix.tax.notice", string="NBR Notice", index=True)
    reason = fields.Text(string="What Was Wrong", required=True)
    amended_output_vat = fields.Monetary(
        string="Corrected Output VAT", currency_field="currency_id", required=True
    )
    amended_input_vat = fields.Monetary(
        string="Corrected Input VAT", currency_field="currency_id", required=True
    )
    amended_net = fields.Monetary(
        string="Corrected Net Payable",
        currency_field="currency_id",
        compute="_compute_amended_net",
        store=True,
    )
    previous_net = fields.Monetary(
        string="Net Payable Before", currency_field="currency_id", readonly=True, copy=False
    )
    difference = fields.Monetary(
        string="Difference (+ payable / - refundable)",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    evidence_file = fields.Binary(string="Working Papers", attachment=True, copy=False)
    evidence_filename = fields.Char(string="Working Papers File Name", copy=False)
    challan_id = fields.Many2one(
        "fix.tax.challan",
        string="Challan for the Additional VAT",
        domain=[("tax_kind", "=", "vat")],
    )
    ack_file = fields.Binary(string="NBR Acknowledgement (file)", attachment=True, copy=False)
    ack_filename = fields.Char(string="Acknowledgement File Name", copy=False)
    nbr_acknowledgement = fields.Char(string="NBR Acknowledgement", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting CFO"),
            ("approved", "Approved (to file)"),
            ("filed", "Filed"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    prepared_by_id = fields.Many2one("res.users", string="Prepared By", readonly=True, copy=False)
    submitted_at = fields.Datetime(readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    filed_by_id = fields.Many2one("res.users", string="Filed By", readonly=True, copy=False)
    filed_at = fields.Datetime(readonly=True, copy=False)
    reject_reason = fields.Char(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "previous_net",
            "difference",
            "nbr_acknowledgement",
            "prepared_by_id",
            "submitted_at",
            "approved_by_id",
            "approved_at",
            "filed_by_id",
            "filed_at",
            "reject_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        typed = {
            "return_id",
            "reason_type",
            "notice_id",
            "reason",
            "amended_output_vat",
            "amended_input_vat",
            "evidence_file",
            "evidence_filename",
        }
        if self and any(a.state != "draft" for a in self):
            locked |= typed
        if self and any(a.state not in ("draft", "approved") for a in self):
            locked |= {"challan_id", "ack_file", "ack_filename"}
        return locked

    @api.depends("amended_output_vat", "amended_input_vat")
    def _compute_amended_net(self):
        for a in self:
            a.amended_net = round((a.amended_output_vat or 0.0) - (a.amended_input_vat or 0.0), 2)

    @api.constrains("amended_output_vat", "amended_input_vat", "return_id", "reason_type")
    def _check_amendment(self):
        for a in self:
            if a.amended_output_vat < 0 or a.amended_input_vat < 0:
                raise ValidationError("Corrected VAT totals cannot be negative.")
            if a.return_id.state != "filed" and a.state == "draft":
                raise ValidationError(
                    "Only a filed return is amended; before filing, re-prepare the return."
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            seq = self.env["ir.sequence"].sudo().next_by_code("fix.vat.return.amendment")
            rec._guarded().write({"name": seq or "VRA/%s" % rec.id})
        return records

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            late = {"challan_id", "ack_file", "ack_filename"}
            moving = set(vals) - LOCK_EXEMPT
            if any(a.state == "approved" for a in self) and moving <= late:
                return super().write(vals)
            _locked_write(self, vals, ("draft",), "A submitted 9.1 amendment")
        return super().write(vals)

    def _previous_net(self):
        """Net payable as last filed for the period: the latest filed
        amendment, else the original return."""
        self.ensure_one()
        last = self.search(
            [("return_id", "=", self.return_id.id), ("state", "=", "filed"), ("id", "!=", self.id)],
            order="filed_at desc, id desc",
            limit=1,
        )
        return last.amended_net if last else self.return_id.net_payable

    def action_submit(self):
        _require_finance(self.env, "Submitting a 9.1 amendment")
        for a in self:
            if a.state != "draft":
                raise UserError("Only a draft amendment is submitted.")
            if a.return_id.state != "filed":
                raise UserError("Only a filed return is amended.")
            if not a.evidence_file:
                raise UserError(
                    "BRU-TAX-15: attach the working papers that show the correction before "
                    "submitting the amendment."
                )
            if a.reason_type != "self_identified" and not a.notice_id:
                raise UserError("Link the NBR notice this amendment answers.")
            if self.search_count(
                [
                    ("return_id", "=", a.return_id.id),
                    ("state", "in", ("submitted", "approved")),
                    ("id", "!=", a.id),
                ]
            ):
                raise UserError(
                    "Return %s already has an amendment in progress: finish it first."
                    % a.return_id.period
                )
            before = a._previous_net()
            a._guarded().write(
                {
                    "state": "submitted",
                    "prepared_by_id": self.env.uid,
                    "submitted_at": fields.Datetime.now(),
                    "previous_net": before,
                    "difference": round(a.amended_net - before, 2),
                }
            )
            tax_alert(
                a,
                a.company_id,
                "Approve 9.1 amendment %s" % a.name,
                "Amendment of the %s return: %s" % (a.period, a.reason),
                (CFO_GROUP,),
            )
        return True

    def action_approve(self):
        _require_cfo(self.env, "Approving a 9.1 amendment")
        for a in self:
            if a.state != "submitted":
                raise UserError("Only a submitted amendment is approved.")
            _require_other(self.env, a.prepared_by_id | a.create_uid, "a 9.1 amendment")
            a.sudo()._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        _require_cfo(self.env, "Rejecting a 9.1 amendment")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the amendment is rejected.")
        for a in self:
            if a.state != "submitted":
                raise UserError("Only a submitted amendment is rejected.")
            _require_other(self.env, a.prepared_by_id | a.create_uid, "a 9.1 amendment")
            a.sudo()._guarded().write({"state": "rejected", "reject_reason": reason})
        return True

    def action_mark_filed(self, reference=None):
        """The amended return was filed through NBR IVAS: record the
        acknowledgement with its file. The original return is not touched."""
        _require_cfo(self.env, "Recording the filing of a 9.1 amendment")
        reference = (reference or "").strip()
        if not reference:
            raise UserError("State the NBR acknowledgement reference of the amended return.")
        for a in self:
            if a.state != "approved":
                raise UserError("Only an approved amendment is filed.")
            _require_other(self.env, a.prepared_by_id | a.create_uid, "filing a 9.1 amendment")
            if not a.ack_file:
                raise UserError("Attach the NBR acknowledgement of the amended return.")
            if a.difference > 0 and not a.challan_id:
                raise UserError(
                    "The amendment adds %.2f of VAT: link the challan that paid it "
                    "(BRU-TAX-14)." % a.difference
                )
            if a.challan_id and a.challan_id.company_id != a.company_id:
                raise UserError("The challan belongs to another company.")
            a.sudo()._guarded().write(
                {
                    "state": "filed",
                    "nbr_acknowledgement": reference,
                    "filed_by_id": self.env.uid,
                    "filed_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "vat_return.amended",
                "fix.vat.return.amendment",
                a.id,
                {
                    "return_id": a.return_id.id,
                    "period": a.period,
                    "reason_type": a.reason_type,
                    "difference": a.difference,
                    "acknowledgement": reference,
                },
            )
        return True


class FixVatReturnAmended(models.Model):
    _inherit = "fix.vat.return"

    amendment_ids = fields.One2many(
        "fix.vat.return.amendment", "return_id", string="Amendments", readonly=True
    )
    amendment_count = fields.Integer(compute="_compute_amendments", string="Amendments Filed")
    amended_net_payable = fields.Monetary(
        compute="_compute_amendments",
        currency_field="currency_id",
        string="Net Payable as Amended",
    )

    @api.depends("amendment_ids.state", "amendment_ids.amended_net", "net_payable")
    def _compute_amendments(self):
        for ret in self:
            filed = ret.amendment_ids.filtered(lambda a: a.state == "filed").sorted(
                lambda a: (a.filed_at or fields.Datetime.now(), a.id)
            )
            ret.amendment_count = len(filed)
            ret.amended_net_payable = filed[-1].amended_net if filed else ret.net_payable


# ---------------------------------------------------------------------- NBR notices
NOTICE_TYPES = [
    ("query", "Query / information request"),
    ("audit", "Audit notice"),
    ("show_cause", "Show-cause notice"),
    ("assessment", "Assessment order"),
    ("appeal", "Appeal / tribunal order"),
]
NOTICE_TAXES = [
    ("vat", "VAT"),
    ("tds", "TDS"),
    ("vds", "VDS"),
    ("income_tax", "Corporate income tax"),
    ("customs", "Customs / import"),
    ("other", "Other"),
]
NOTICE_OUTCOMES = [
    ("no_change", "Closed, no change"),
    ("assessed", "Tax assessed"),
    ("withdrawn", "Withdrawn by NBR"),
    ("appealed", "Appealed"),
]


class FixTaxNotice(models.Model):
    """An NBR query, audit notice or assessment and our response to it."""

    _name = "fix.tax.notice"
    _description = "NBR Notice / Query"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "response_due, id desc"

    name = fields.Char(readonly=True, copy=False, default="New", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", index=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    notice_type = fields.Selection(NOTICE_TYPES, string="Notice Type", required=True)
    tax_kind = fields.Selection(NOTICE_TAXES, string="Tax", required=True)
    authority = fields.Char(
        string="Issuing Office", required=True, help="VAT circle / division, LTU or tax zone"
    )
    notice_ref = fields.Char(string="Notice Reference", required=True, tracking=True)
    received_on = fields.Date(required=True, default=fields.Date.context_today)
    period_from = fields.Date(string="Scope From", required=True)
    period_to = fields.Date(string="Scope To", required=True)
    subject = fields.Text(string="What NBR Asks", required=True)
    response_due = fields.Date(string="Response Due", required=True, tracking=True)
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        index=True,
    )
    disputed_amount = fields.Monetary(
        string="Amount in Dispute", currency_field="currency_id", tracking=True
    )
    notice_file = fields.Binary(string="Notice (file)", attachment=True, copy=False)
    notice_filename = fields.Char(string="Notice File Name", copy=False)
    audit_pack_id = fields.Many2one(
        "fix.tax.audit.pack", string="Audit Pack", readonly=True, copy=False
    )
    response_ref = fields.Char(string="Our Response Reference", tracking=True)
    response_on = fields.Date(string="Responded On")
    response_file = fields.Binary(string="Response (file)", attachment=True, copy=False)
    response_filename = fields.Char(string="Response File Name", copy=False)
    outcome = fields.Selection(NOTICE_OUTCOMES, tracking=True)
    assessed_amount = fields.Monetary(string="Tax Assessed", currency_field="currency_id")
    closure_note = fields.Text(string="Closure Note")
    amendment_ids = fields.One2many("fix.vat.return.amendment", "notice_id", readonly=True)
    state = fields.Selection(
        [("open", "Open"), ("responded", "Responded"), ("closed", "Closed")],
        default="open",
        required=True,
        tracking=True,
        index=True,
    )
    responded_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    responded_at = fields.Datetime(readonly=True, copy=False)
    closed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    closed_at = fields.Datetime(readonly=True, copy=False)
    days_to_due = fields.Integer(compute="_compute_due", string="Days to Due")
    overdue = fields.Boolean(compute="_compute_due")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "audit_pack_id",
            "responded_by_id",
            "responded_at",
            "closed_by_id",
            "closed_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        intake = {
            "company_id",
            "notice_type",
            "tax_kind",
            "authority",
            "notice_ref",
            "received_on",
            "period_from",
            "period_to",
            "subject",
            "notice_file",
            "notice_filename",
        }
        response = {"response_ref", "response_on", "response_file", "response_filename"}
        if self and any(n.state != "open" for n in self):
            locked |= intake | response | {"response_due", "owner_id", "disputed_amount"}
        if self and any(n.state == "closed" for n in self):
            locked |= {"outcome", "assessed_amount", "closure_note"}
        return locked

    @api.depends("response_due", "state")
    def _compute_due(self):
        today = fields.Date.context_today(self)
        for n in self:
            if n.response_due and n.state == "open":
                n.days_to_due = (n.response_due - today).days
                n.overdue = n.response_due < today
            else:
                n.days_to_due = 0
                n.overdue = False

    @api.constrains("period_from", "period_to", "response_due", "received_on", "disputed_amount")
    def _check_notice(self):
        for n in self:
            if n.period_to < n.period_from:
                raise ValidationError("The notice scope ends before it starts.")
            if n.response_due < n.received_on:
                raise ValidationError("The response is due before the notice was received.")
            if n.disputed_amount < 0:
                raise ValidationError("The amount in dispute cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            seq = self.env["ir.sequence"].sudo().next_by_code("fix.tax.notice")
            rec._guarded().write({"name": seq or "TXN/%s" % rec.id})
            # AUT-TAX-22: a response task with the deadline, for the owner
            rec.sudo().activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=rec.response_due,
                summary="Respond to NBR notice %s" % rec.notice_ref,
                note=rec.subject,
                user_id=rec.owner_id.id,
            )
        return records

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            closing = {"outcome", "assessed_amount", "closure_note"}
            moving = set(vals) - LOCK_EXEMPT
            if all(n.state == "responded" for n in self) and moving <= closing:
                return super().write(vals)
            _locked_write(self, vals, ("open",), "A responded notice")
        return super().write(vals)

    def action_generate_pack(self):
        """AUT-TAX-22: the audit pack for the notice's scope, sealed."""
        _require_finance(self.env, "Generating the audit pack for a notice")
        for n in self:
            if n.audit_pack_id:
                raise UserError("Notice %s already has its audit pack." % n.name)
            pack = self.env["fix.tax.audit.pack"].create(
                {
                    "company_id": n.company_id.id,
                    "date_from": n.period_from,
                    "date_to": n.period_to,
                }
            )
            pack.action_generate()
            n._guarded().write({"audit_pack_id": pack.id})
        return True

    def action_record_response(self):
        _require_finance(self.env, "Recording the response to a notice")
        for n in self:
            if n.state != "open":
                raise UserError("Only an open notice is answered.")
            if not (n.response_ref and n.response_on and n.response_file):
                raise UserError(
                    "Record the response reference, its date and the response file first."
                )
            n._guarded().write(
                {
                    "state": "responded",
                    "responded_by_id": self.env.uid,
                    "responded_at": fields.Datetime.now(),
                }
            )
            n.activity_ids.filtered(
                lambda a, ref=n.notice_ref: a.summary == "Respond to NBR notice %s" % ref
            ).sudo().action_done()
        return True

    def action_close(self):
        _require_manager(self.env, "Closing an NBR notice")
        for n in self:
            if n.state != "responded":
                raise UserError("Only a responded notice is closed.")
            _require_other(self.env, n.responded_by_id, "closing an NBR notice")
            if not n.outcome:
                raise UserError("Record the outcome before closing the notice.")
            if n.outcome == "assessed" and n.assessed_amount <= 0:
                raise UserError("State the tax assessed.")
            n._guarded().write(
                {
                    "state": "closed",
                    "closed_by_id": self.env.uid,
                    "closed_at": fields.Datetime.now(),
                }
            )
        return True

    @api.model
    def _cron_notice_deadlines(self):
        """Remind the owner before the response is due; escalate to the
        Accounting Administrators and the CFO once it is overdue."""
        today = fields.Date.context_today(self)
        raw = self.env["ir.config_parameter"].sudo().get_param(NOTICE_REMINDER_PARAM)
        try:
            days = int(raw) if raw else NOTICE_REMINDER_DEFAULT
        except ValueError:
            days = NOTICE_REMINDER_DEFAULT
        for n in self.sudo().search(
            [("state", "=", "open"), ("response_due", "<=", today + timedelta(days=days))]
        ):
            if n.response_due < today:
                tax_alert(
                    n,
                    n.company_id,
                    "NBR notice %s is overdue" % n.notice_ref,
                    "The response to %s (%s) was due on %s; owner %s."
                    % (n.name, n.authority, n.response_due, n.owner_id.name),
                    (MANAGER_GROUP, CFO_GROUP),
                    deadline=today,
                )
            else:
                summary = "NBR notice %s due %s" % (n.notice_ref, n.response_due)
                if not n.activity_ids.filtered(lambda a, s=summary: a.summary == s):
                    n.activity_schedule(
                        "mail.mail_activity_data_todo",
                        date_deadline=n.response_due,
                        summary=summary,
                        note=n.subject,
                        user_id=n.owner_id.id,
                    )
        return True
