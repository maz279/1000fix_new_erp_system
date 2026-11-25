# fix_import_capture — M44 capture audit (2026-11-16): the spec §10.1 records
# that no sub-module page could capture because they did not exist.
#
#   fix.import.cost            the cost documents of a consignment (forwarder,
#                              C&F agent, port, bank, inland, insurer bills):
#                              FR-ITC-018 / -030 / -031, T-11, BRU-ITC-16 / -18.
#                              Reconciled by an Import Approver who did not
#                              record them; a reconciled document is what the
#                              landed-cost sheet capitalises.
#   fix.import.lc.discrepancy  a presentation defect raised by the negotiating
#                              bank and our decision on it (FR-ITC-016, §8.2).
#                              No payment is recorded under an LC while one is
#                              undecided.
#   fix.import.customs.query   an assessment query or examination raised by
#                              customs on a lodged Bill of Entry (FR-ITC-028,
#                              §8.1 UNDER ASSESSMENT <-> QUERY). The Bill of
#                              Entry is not assessed while one is unresolved.
#   fix.import.arrival         + the freight forwarder, carrier and booking
#                              (FR-ITC-021); the forwarder must be active in
#                              M42 before it is instructed (BRU-ITC-12).
#
# Which charges a forwarder or agent may bill, and at what tariff, are DATA the
# user enters from the documents; nothing here asserts a rate.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_import_common import (
    APPROVER,
    FINANCE,
    OFFICER,
    P,
    param_float,
    refuse_locked,
    require_group,
    require_other_person,
    today,
)
from .fix_import_ops import _seq

PARAM_COST_VARIANCE = P + "cost_variance_tolerance_pct"  # default 0 (BRU-ITC-16)

# cost category -> the landed-cost sheet field it is capitalised into
# (FR-ITC-034: only inventoriable factors; "other" is expensed through M52).
COST_BUCKETS = {
    "freight": "freight",
    "insurance": "insurance",
    "clearing": "clearing_charges",
    "port": "clearing_charges",
    "demurrage": "clearing_charges",
    "inland": "clearing_charges",
    "bank": "bank_charges",
    "other": False,
}
BUCKET_LABELS = {
    "freight": "Freight",
    "insurance": "Insurance",
    "clearing_charges": "Clearing, Port & C&F",
    "bank_charges": "LC & Bank Charges",
}


def _require_any_group(env, xmlids, what):
    if env.su or any(env.user.has_group(x) for x in xmlids):
        return
    names = []
    for xmlid in xmlids:
        group = env.ref(xmlid, raise_if_not_found=False)
        names.append(group.name if group else xmlid)
    raise UserError("%s requires the %s role." % (what, " or ".join(names)))


# =============================================================== cost documents
class FixImportCost(models.Model):
    """One cost document of an import consignment: who billed what, in which
    currency at which rate, against which agreed figure. BRU-ITC-16: the
    document is reconciled, not absorbed - a variance from the agreed figure
    beyond tolerance carries a classified cause."""

    _name = "fix.import.cost"
    _description = "Import Cost Document"
    _order = "incurred_on desc, id desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    name = fields.Char(required=True, default="New", copy=False)
    order_id = fields.Many2one(
        "fix.import.order", string="Import Order", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="order_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="order_id.operating_unit_id", store=True, index=True
    )
    category = fields.Selection(
        [
            ("freight", "Freight (forwarder / shipping line)"),
            ("insurance", "Cargo insurance premium"),
            ("clearing", "C&F agency fee"),
            ("port", "Port, storage, handling & examination"),
            ("demurrage", "Demurrage / detention"),
            ("inland", "Inland transport, port to warehouse"),
            ("bank", "LC & bank charges (opening, amendment, SWIFT, acceptance)"),
            ("other", "Other (not capitalised - expensed through M52)"),
        ],
        required=True,
        tracking=True,
    )
    landed_bucket = fields.Char(compute="_compute_bucket", string="Landed-Cost Line")
    billed_by_id = fields.Many2one(
        "res.partner", string="Billed By", required=True, ondelete="restrict"
    )
    cnf_agent_id = fields.Many2one(
        "fix.import.cnf.agent", string="C&F Agent", ondelete="restrict", index=True
    )
    lc_id = fields.Many2one(
        "fix.import.lc", string="Letter of Credit", ondelete="restrict", index=True
    )
    document_ref = fields.Char(string="Bill / Advice No", required=True)
    incurred_on = fields.Date(string="Document Date", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True, tracking=True)
    rate = fields.Float(
        string="Rate (BDT per unit)",
        digits=(16, 6),
        help="BRU-ITC-14: the rate of a foreign-currency document, with its source.",
    )
    rate_source = fields.Char(string="Rate Source")
    bdt_currency_id = fields.Many2one("res.currency", compute="_compute_bdt_ccy", string="BDT")
    amount_bdt = fields.Monetary(
        currency_field="bdt_currency_id",
        compute="_compute_amount_bdt",
        store=True,
        string="Amount (BDT)",
    )
    expected_amount = fields.Monetary(
        currency_field="currency_id",
        string="Agreed / Quoted Amount",
        help="The agreed tariff or quotation this bill is reconciled against (T-11).",
    )
    variance = fields.Monetary(
        currency_field="currency_id", compute="_compute_variance", store=True
    )
    variance_pct = fields.Float(compute="_compute_variance", store=True, string="Variance %")
    variance_cause = fields.Selection(
        [
            ("rate", "Rate or tariff change"),
            ("quantity", "Weight, volume or quantity differs"),
            ("days", "More storage / demurrage days"),
            ("billing_error", "Billing error by the party"),
            ("scope", "Service not in the agreement"),
            ("other", "Other (see note)"),
        ],
        string="Variance Cause",
    )
    variance_note = fields.Char(string="Variance Note")
    document = fields.Binary(string="Bill / Advice (copy)", attachment=True)
    document_name = fields.Char()
    state = fields.Selection(
        [("draft", "Recorded"), ("reconciled", "Reconciled"), ("rejected", "Rejected")],
        required=True,
        default="draft",
        tracking=True,
    )
    recorded_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    reconciled_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    reconciled_on = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Char(readonly=True, copy=False)

    _FROZEN = (
        "order_id",
        "category",
        "billed_by_id",
        "cnf_agent_id",
        "lc_id",
        "document_ref",
        "incurred_on",
        "currency_id",
        "amount",
        "rate",
        "rate_source",
        "expected_amount",
        "variance_cause",
        "variance_note",
        "document",
        "document_name",
    )
    _amount_positive = models.Constraint("CHECK (amount > 0)", "A cost document is positive")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "recorded_by_id",
            "reconciled_by_id",
            "reconciled_on",
            "rejection_reason",
            "amount_bdt",
            "variance",
            "variance_pct",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(self._FROZEN)
        return locked

    @api.depends("category")
    def _compute_bucket(self):
        for rec in self:
            rec.landed_bucket = BUCKET_LABELS.get(COST_BUCKETS.get(rec.category) or "", "")

    def _compute_bdt_ccy(self):
        bdt = self.env.ref("base.BDT")
        for rec in self:
            rec.bdt_currency_id = bdt

    @api.depends("amount", "rate", "currency_id")
    def _compute_amount_bdt(self):
        bdt = self.env.ref("base.BDT")
        for rec in self:
            if rec.currency_id == bdt or not rec.currency_id:
                rec.amount_bdt = rec.amount or 0.0
            else:
                rec.amount_bdt = round((rec.amount or 0.0) * (rec.rate or 0.0), 2)

    @api.depends("amount", "expected_amount")
    def _compute_variance(self):
        for rec in self:
            if rec.expected_amount:
                rec.variance = round((rec.amount or 0.0) - rec.expected_amount, 2)
                rec.variance_pct = round(rec.variance * 100.0 / rec.expected_amount, 2)
            else:
                rec.variance = 0.0
                rec.variance_pct = 0.0

    @api.constrains(
        "currency_id", "rate", "rate_source", "lc_id", "order_id", "category", "cnf_agent_id"
    )
    def _check_document(self):
        bdt = self.env.ref("base.BDT")
        for rec in self:
            if rec.currency_id != bdt and (rec.rate <= 0 or not (rec.rate_source or "").strip()):
                raise ValidationError(
                    "A %s document needs its rate to BDT and the rate's source (BRU-ITC-14)."
                    % rec.currency_id.name
                )
            if rec.lc_id and rec.lc_id.order_id != rec.order_id:
                raise ValidationError(
                    "LC %s belongs to %s, not %s."
                    % (rec.lc_id.lc_no, rec.lc_id.order_id.name, rec.order_id.name)
                )
            if rec.category == "clearing" and not rec.cnf_agent_id:
                raise ValidationError(
                    "A C&F agency fee names the agent who billed it (FR-ITC-030)."
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require_any_group(self.env, (OFFICER, FINANCE), "Recording an import cost document")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.cost", "ICOST/New")
            for name in (
                "state",
                "recorded_by_id",
                "reconciled_by_id",
                "reconciled_on",
                "rejection_reason",
            ):
                vals.pop(name, None)
        records = super().create(vals_list)
        records._guarded().write({"recorded_by_id": self.env.uid})
        for rec in records:
            rec._cost_check_order_open()
        return records

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._FROZEN) if r.state != "draft" else set(),
            "a reconciled or rejected cost document is evidence; record a new one.",
        )
        result = super().write(vals)
        if "order_id" in vals or "category" in vals:
            for rec in self:
                rec._cost_check_order_open()
        return result

    def _cost_check_order_open(self):
        order = self.order_id.sudo()
        if order.state == "closed":
            raise UserError("Import order %s is closed." % order.name)
        if COST_BUCKETS.get(self.category) and self.env["fix.import.landed"].sudo().search_count(
            [("order_id", "=", order.id), ("sheet_type", "=", "final"), ("state", "=", "finalised")]
        ):
            raise UserError(
                "The final landed cost of %s is already applied: a capitalisable cost "
                "arriving after it is a variance for Finance (M52 / M19), not a landed-cost "
                "document." % order.name
            )

    def action_reconcile(self):
        require_group(self.env, APPROVER, "Reconciling an import cost document")
        tolerance = param_float(self.env, PARAM_COST_VARIANCE, 0.0)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Reconcile a recorded cost document.")
            require_other_person(rec.env, rec, "Cost document %s" % rec.document_ref)
            if not rec.document:
                raise UserError("Attach the bill or advice before it is reconciled.")
            if rec.expected_amount and abs(rec.variance_pct) > tolerance + 1e-9:
                if not rec.variance_cause:
                    raise UserError(
                        "%s differs from the agreed %.2f by %.2f (%.2f%%): classify the "
                        "variance before it is reconciled (BRU-ITC-16)."
                        % (rec.document_ref, rec.expected_amount, rec.variance, rec.variance_pct)
                    )
                if rec.variance_cause == "other" and not (rec.variance_note or "").strip():
                    raise UserError("Explain the variance in the note.")
            rec._guarded().write(
                {
                    "state": "reconciled",
                    "reconciled_by_id": rec.env.user.id,
                    "reconciled_on": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        require_group(self.env, APPROVER, "Rejecting an import cost document")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Reject a recorded cost document.")
            if not (reason or "").strip():
                raise UserError("State why the cost document is rejected.")
            rec._guarded().write(
                {
                    "state": "rejected",
                    "rejection_reason": reason.strip(),
                    "reconciled_by_id": rec.env.user.id,
                    "reconciled_on": fields.Datetime.now(),
                }
            )
        return True

    def _cost_in(self, currency, order):
        """amount_bdt in the sheet's currency (BDT, or the order's at its rate)."""
        self.ensure_one()
        if currency == self.env.ref("base.BDT"):
            return self.amount_bdt
        if currency == order.currency_id and order.fx_rate:
            return self.amount_bdt / order.fx_rate
        raise UserError("A landed-cost sheet in %s cannot read BDT cost documents." % currency.name)


class FixImportOrderCost(models.Model):
    _inherit = "fix.import.order"

    cost_ids = fields.One2many("fix.import.cost", "order_id", string="Cost Documents")

    def _import_cost_buckets(self, currency):
        """{sheet field: total} of the reconciled capitalisable cost documents."""
        self.ensure_one()
        out = {}
        for doc in self.sudo().cost_ids.filtered(lambda d: d.state == "reconciled"):
            bucket = COST_BUCKETS.get(doc.category)
            if bucket:
                out[bucket] = round(out.get(bucket, 0.0) + doc._cost_in(currency, self), 2)
        return out

    def action_close(self):
        """BRU-ITC-18: nothing unreconciled is left against a closing order."""
        for rec in self:
            open_docs = rec.sudo().cost_ids.filtered(lambda d: d.state == "draft")
            if open_docs:
                raise UserError(
                    "Import order %s cannot close: cost document(s) %s are not reconciled "
                    "(BRU-ITC-18)." % (rec.name, ", ".join(open_docs.mapped("document_ref")))
                )
        return super().action_close()


class FixImportLandedCost(models.Model):
    _inherit = "fix.import.landed"

    def action_pull_costs(self):
        """Fill the sheet's charge lines from the reconciled cost documents.
        A line no document evidences keeps the figure typed on it."""
        require_group(self.env, OFFICER, "Filling a landed-cost sheet from its cost documents")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Fill a draft landed-cost sheet.")
            buckets = rec.order_id._import_cost_buckets(rec.currency_id)
            if not buckets:
                raise UserError(
                    "Import order %s has no reconciled cost document yet." % rec.order_id.name
                )
            rec.write(buckets)
        return True

    def action_finalise(self):
        """BRU-ITC-16 / -18: a final sheet is finalised with every cost document
        of the order decided, and every charge line the documents evidence
        equal to them."""
        for rec in self.filtered(lambda r: r.sheet_type == "final" and r.state == "draft"):
            order = rec.order_id.sudo()
            pending = order.cost_ids.filtered(lambda d: d.state == "draft")
            if pending:
                raise UserError(
                    "Reconcile or reject cost document(s) %s of %s before the final landed "
                    "cost (BRU-ITC-16)." % (", ".join(pending.mapped("document_ref")), order.name)
                )
            for bucket, total in order._import_cost_buckets(rec.currency_id).items():
                if abs((rec[bucket] or 0.0) - total) > 0.005:
                    raise UserError(
                        "%s on %s is %.2f but the reconciled cost documents total %.2f: use "
                        "Fill from Cost Documents, or correct the documents (BRU-ITC-16)."
                        % (BUCKET_LABELS[bucket], rec.name, rec[bucket] or 0.0, total)
                    )
        return super().action_finalise()


# =============================================================== LC discrepancy
class FixImportLcDiscrepancy(models.Model):
    """FR-ITC-016 / §8.2: the negotiating bank finds the presented documents
    discrepant; we accept (waive) or refuse, with the cost and delay."""

    _name = "fix.import.lc.discrepancy"
    _description = "LC Discrepancy"
    _order = "raised_on desc, id desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    name = fields.Char(required=True, default="New", copy=False)
    lc_id = fields.Many2one(
        "fix.import.lc", string="Letter of Credit", required=True, ondelete="cascade", index=True
    )
    order_id = fields.Many2one(related="lc_id.order_id", store=True, index=True)
    company_id = fields.Many2one(related="lc_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="lc_id.operating_unit_id", store=True, index=True)
    currency_id = fields.Many2one(related="lc_id.currency_id")
    raised_by_bank = fields.Char(string="Raised By (Bank)", required=True)
    presentation_ref = fields.Char(string="Presentation / Bank Ref")
    raised_on = fields.Date(required=True)
    description = fields.Text(string="Discrepancy", required=True)
    discrepancy_fee = fields.Monetary(
        currency_field="currency_id",
        string="Discrepancy Fee",
        help="Record the fee as an LC & bank charge cost document once billed.",
    )
    delay_days = fields.Integer(string="Delay (days)")
    state = fields.Selection(
        [("open", "Open"), ("accepted", "Accepted (waived)"), ("refused", "Refused")],
        required=True,
        default="open",
        tracking=True,
    )
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    decision_reason = fields.Char(readonly=True, copy=False)

    _FROZEN = (
        "lc_id",
        "raised_by_bank",
        "presentation_ref",
        "raised_on",
        "description",
        "discrepancy_fee",
        "delay_days",
    )
    _fee = models.Constraint(
        "CHECK (discrepancy_fee IS NULL OR discrepancy_fee >= 0)", "A fee is not negative"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "decided_by_id",
            "decided_on",
            "decision_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "open":
            locked |= set(self._FROZEN)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, OFFICER, "Recording an LC discrepancy")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.lc.discrepancy", "ILCD/New")
        records = super().create(vals_list)
        for rec in records:
            if rec.lc_id.state not in ("opened", "amended"):
                raise UserError(
                    "A discrepancy is raised on documents presented under an opened LC "
                    "(LC %s is %s)." % (rec.lc_id.lc_no, rec.lc_id.state)
                )
        return records

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(r._FROZEN) if r.state != "open" else set(),
            "a decided discrepancy is final.",
        )
        return super().write(vals)

    def _decide(self, state, reason, what):
        require_group(self.env, APPROVER, what)
        for rec in self:
            if rec.state != "open":
                raise UserError("Decide an open discrepancy.")
            require_other_person(rec.env, rec, "Discrepancy %s" % rec.name)
            if not (reason or "").strip():
                raise UserError("State the reason for the decision.")
            rec._guarded().write(
                {
                    "state": state,
                    "decided_by_id": rec.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "decision_reason": reason.strip(),
                }
            )
        return True

    def action_accept(self, reason=None):
        return self._decide("accepted", reason, "Accepting an LC discrepancy")

    def action_refuse(self, reason=None):
        return self._decide("refused", reason, "Refusing an LC discrepancy")


class FixImportLcPaymentDiscrepancy(models.Model):
    _inherit = "fix.import.lc.payment"

    @api.model_create_multi
    def create(self, vals_list):
        # §8.2: a discrepant presentation is decided before it is negotiated
        Disc = self.env["fix.import.lc.discrepancy"].sudo()
        for vals in vals_list:
            lc_id = vals.get("lc_id")
            if lc_id and Disc.search_count([("lc_id", "=", lc_id), ("state", "=", "open")]):
                lc = self.env["fix.import.lc"].sudo().browse(lc_id)
                raise UserError(
                    "LC %s has an undecided discrepancy: accept or refuse it before a "
                    "payment is recorded (FR-ITC-016)." % lc.lc_no
                )
            # M44-18: documents we refused are not paid under the LC
            if lc_id and Disc.search_count([("lc_id", "=", lc_id), ("state", "=", "refused")]):
                lc = self.env["fix.import.lc"].sudo().browse(lc_id)
                raise UserError(
                    "LC %s has a refused discrepancy: the discrepant documents are not paid "
                    "under the LC. Amend the LC or settle outside it (M44-18)." % lc.lc_no
                )
        return super().create(vals_list)


class FixImportLcDiscrepancies(models.Model):
    _inherit = "fix.import.lc"

    discrepancy_ids = fields.One2many("fix.import.lc.discrepancy", "lc_id", string="Discrepancies")


# =============================================================== customs query
class FixImportCustomsQuery(models.Model):
    """FR-ITC-028: a classification, valuation or document query, or a
    physical examination, raised by customs on a lodged Bill of Entry."""

    _name = "fix.import.customs.query"
    _description = "Customs Query / Examination"
    _order = "raised_on desc, id desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    name = fields.Char(required=True, default="New", copy=False)
    boe_id = fields.Many2one(
        "fix.import.boe", string="Bill of Entry", required=True, ondelete="cascade", index=True
    )
    order_id = fields.Many2one(related="boe_id.order_id", store=True, index=True)
    company_id = fields.Many2one(related="boe_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="boe_id.operating_unit_id", store=True, index=True)
    query_type = fields.Selection(
        [
            ("classification", "Classification (HS code)"),
            ("valuation", "Valuation"),
            ("documents", "Documents"),
            ("examination", "Physical examination"),
            ("other", "Other"),
        ],
        required=True,
    )
    query_ref = fields.Char(string="Customs Query Ref")
    raised_on = fields.Date(required=True)
    description = fields.Text(string="Query", required=True)
    examination_result = fields.Selection(
        [
            ("matched", "Examined: matches the declaration"),
            ("discrepancy", "Examined: differs from the declaration"),
        ],
        string="Examination Result",
    )
    response = fields.Text(readonly=True, copy=False)
    responded_on = fields.Date(readonly=True, copy=False)
    outcome = fields.Char(readonly=True, copy=False)
    resolved_on = fields.Date(readonly=True, copy=False)
    state = fields.Selection(
        [("open", "Open"), ("answered", "Answered"), ("resolved", "Resolved")],
        required=True,
        default="open",
        tracking=True,
    )
    answered_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    resolved_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    _FROZEN = ("boe_id", "query_type", "query_ref", "raised_on", "description")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "response",
            "responded_on",
            "outcome",
            "resolved_on",
            "answered_by_id",
            "resolved_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "open":
            locked |= set(self._FROZEN)
        if len(self) == 1 and self.state == "resolved":
            locked |= {"examination_result"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, OFFICER, "Recording a customs query")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.import.customs.query", "ICQ/New")
        records = super().create(vals_list)
        for rec in records:
            if rec.boe_id.state != "draft":
                raise UserError(
                    "A query is raised on a lodged Bill of Entry under assessment "
                    "(%s is %s)." % (rec.boe_id.boe_no, rec.boe_id.state)
                )
        return records

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: (set(r._FROZEN) if r.state != "open" else set())
            | ({"examination_result"} if r.state == "resolved" else set()),
            "it is fixed once the query is answered or resolved.",
        )
        return super().write(vals)

    def action_answer(self, response=None):
        require_group(self.env, OFFICER, "Answering a customs query")
        for rec in self:
            if rec.state != "open":
                raise UserError("Answer an open query.")
            if not (response or "").strip():
                raise UserError("Record the response given to customs.")
            rec._guarded().write(
                {
                    "state": "answered",
                    "response": response.strip(),
                    "responded_on": today(rec),
                    "answered_by_id": rec.env.user.id,
                }
            )
        return True

    def action_resolve(self, outcome=None):
        require_group(self.env, OFFICER, "Resolving a customs query")
        for rec in self:
            if rec.state != "answered":
                raise UserError("Resolve an answered query.")
            if not (outcome or "").strip():
                raise UserError("Record what customs decided.")
            if rec.query_type == "examination" and not rec.examination_result:
                raise UserError("Record the examination result first.")
            rec._guarded().write(
                {
                    "state": "resolved",
                    "outcome": outcome.strip(),
                    "resolved_on": today(rec),
                    "resolved_by_id": rec.env.user.id,
                }
            )
        return True


class FixImportBoeQuery(models.Model):
    _inherit = "fix.import.boe"

    query_ids = fields.One2many("fix.import.customs.query", "boe_id", string="Customs Queries")

    def action_assess(self):
        # §8.1: UNDER ASSESSMENT -> DUTY VERIFIED only once every query is resolved
        for rec in self:
            pending = rec.sudo().query_ids.filtered(lambda q: q.state != "resolved")
            if pending:
                raise UserError(
                    "Bill of Entry %s cannot be assessed: customs query %s is not resolved "
                    "(FR-ITC-028)." % (rec.boe_no, ", ".join(pending.mapped("name")))
                )
        return super().action_assess()


# =============================================================== freight booking
class FixImportArrivalBooking(models.Model):
    _inherit = "fix.import.arrival"

    forwarder_id = fields.Many2one(
        "fix.supplier",
        string="Freight Forwarder (M42)",
        ondelete="restrict",
        index=True,
        help="BRU-ITC-12: instructed only while active in M42.",
    )
    carrier = fields.Char(string="Carrier / Shipping Line")
    booking_ref = fields.Char(string="Booking Ref")
    port_of_loading = fields.Char(string="Port of Loading")

    def _locked(self) -> set:
        locked = super()._locked()
        if self.state != "in_transit":
            locked |= {"forwarder_id", "carrier", "booking_ref", "port_of_loading"}
        return locked

    @api.constrains("forwarder_id")
    def _check_forwarder_active(self):
        for rec in self:
            supplier = rec.forwarder_id.sudo()
            if supplier and supplier.status != "active":
                raise ValidationError(
                    "Freight forwarder %s is %s in M42: only an active, qualified forwarder is "
                    "instructed (BRU-ITC-12)." % (supplier.name, supplier.status)
                )
