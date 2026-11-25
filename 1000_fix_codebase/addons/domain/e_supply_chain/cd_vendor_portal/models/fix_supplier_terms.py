# fix_supplier_terms - M42 records the sub-module pages could not capture
# (capture audit 2026-11-15).
#
# Before: page 2 Segmentation captured nothing and the segment was typed on
# the profile by anyone with write rights - although it sets the review
# cadence and the authority a qualification needs (PARAM_QUAL_TIERS), so a
# steward could lower it to escape a CFO approval. Page 5 "Contracts & Price
# Lists" captured a contract DOCUMENT: no agreement (FR-SRM2-021), no agreed
# price (FR-SRM2-022), no price-change approval (FR-SRM2-023, BRU-SRM2-14) and
# no consignment terms (FR-SRM2-024, BRU-SRM2-15) existed anywhere. The
# profile had no classification (FR-SRM2-002) or risk tier (FR-SRM2-004),
# there were no role-based contacts (§10.1 fix.supplier.contact), no
# questionnaire template (FR-SRM2-008) and no authorisation evidence
# (FR-SRM2-015, BRU-SRM2-05).
#
# The file sorts after fix_supplier.py and fix_supplier_controls.py, so the
# models it extends are registered first (ruff I001 orders models/__init__).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_supplier import GROUP_APPROVER, GROUP_STEWARD, _not_by, _require

CLASSIFICATIONS = [
    ("oem", "OEM (manufacturer)"),
    ("authorised_distributor", "Authorised Distributor"),
    ("local_distributor", "Local Distributor"),
    ("local_trader", "Local Trader"),
    ("importer", "Importer"),
    ("service_provider", "Service Provider"),
    ("courier_partner", "Courier Partner"),
    ("recycling_partner", "Recycling Partner"),
    ("freight_forwarder", "Freight Forwarder"),
    ("cnf_agent", "C&F (Clearing & Forwarding) Agent"),
    ("cargo_insurer", "Cargo Insurer"),
    ("brand_partner", "Brand Partner"),
]
RISK_TIERS = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")]
# BRU-SRM2-05: a supplier selling genuine parts it does not make must evidence
# its authorisation; the manufacturer itself (OEM) and a brand partner do not.
AUTHORISED_CLASSES = ("authorised_distributor",)
PRICE_TOLERANCE = 0.005


def _today(rec):
    return fields.Date.context_today(rec)


class FixSupplierClassified(models.Model):
    """FR-SRM2-002/004 on the profile, and the segment governed (FR-SRM2-003)."""

    _inherit = "fix.supplier"

    classification = fields.Selection(
        CLASSIFICATIONS,
        tracking=True,
        help="What kind of supplier this is (BR-SCM-001). An authorised distributor needs "
        "current brand-authorisation evidence before its qualification is approved.",
    )
    risk_tier = fields.Selection(
        RISK_TIERS,
        tracking=True,
        help="Sets qualification depth, review frequency and documentation (FR-SRM2-004).",
    )
    contact_ids = fields.One2many("fix.supplier.contact", "supplier_id", string="Contacts")
    agreement_ids = fields.One2many("fix.supplier.agreement", "supplier_id", string="Agreements")

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(s.status != "prospect" for s in self):
            locked |= {"segment"}
        return locked

    def _a06_order_problems(self):
        """A06 P19: an authorised distributor is ordered from only while its
        brand authorisation is valid (its expiry used to change nothing once
        the qualification had passed)."""
        problems = super()._a06_order_problems()
        if self.classification in AUTHORISED_CLASSES:
            valid = (
                self.env["fix.supplier.document"]
                .sudo()
                .search_count(
                    [
                        ("supplier_id", "=", self.id),
                        ("doc_type", "=", "brand_authorisation"),
                        ("is_valid", "=", True),
                    ]
                )
            )
            if not valid:
                problems.append("its brand authorisation is missing or expired")
        return problems

    def write(self, vals):
        # A06 P19: what kind of supplier it is decides the evidence it owes;
        # it is fixed once the supplier has left prospect
        if "classification" in vals and not self._fix_guard_has_token() and not self.env.su:
            for rec in self:
                if rec.status != "prospect" and rec._fix_guard_differs(
                    "classification", vals["classification"], rec.classification
                ):
                    raise UserError(
                        "Supplier %s is %s: its classification decides its evidence and changes "
                        "only through a new qualification." % (rec.supplier_code, rec.status)
                    )
        if "segment" in vals and not self._fix_guard_has_token() and not self.env.su:
            for rec in self:
                if rec.status != "prospect" and rec._fix_guard_differs(
                    "segment", vals["segment"], rec.segment
                ):
                    raise UserError(
                        "Supplier %s is %s: its segment sets the review cadence and the "
                        "qualification authority, so it changes only through an approved "
                        "segment review (Segmentation)." % (rec.supplier_code, rec.status)
                    )
        return super().write(vals)


class FixSupplierContact(models.Model):
    """Role-based supplier contacts (§10.1 fix.supplier.contact)."""

    _name = "fix.supplier.contact"
    _description = "Supplier Contact"
    _inherit = ["fix.guarded.mixin"]  # every M42 register carries the guard (test W01)
    _order = "supplier_id, role, name"

    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    name = fields.Char(string="Contact Person", required=True)
    role = fields.Selection(
        [
            ("commercial", "Commercial"),
            ("logistics", "Logistics"),
            ("quality", "Quality"),
            ("finance", "Finance"),
            ("escalation", "Escalation"),
        ],
        required=True,
        default="commercial",
    )
    phone = fields.Char()
    email = fields.Char()
    partner_id = fields.Many2one(
        "res.partner", string="Contact Record (M33)", ondelete="set null", index=True
    )
    active = fields.Boolean(default=True)

    # "name" is always written on create, so the check also runs when both are left out
    @api.constrains("name", "phone", "email")
    def _check_reachable(self):
        for rec in self:
            if not (rec.phone or "").strip() and not (rec.email or "").strip():
                raise ValidationError("Contact %s needs a phone number or an e-mail." % rec.name)


class FixSupplierSegmentReview(models.Model):
    """A re-segmentation decision (FR-SRM2-003, Procurement Manager right,
    §13): a steward proposes the new segment with its basis, a Supplier
    Approver who did not propose it applies it."""

    _name = "fix.supplier.segment.review"
    _description = "Supplier Segment Review"
    _inherit = ["fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    from_segment = fields.Selection(
        lambda self: self.env["fix.supplier"]._fields["segment"].selection,
        string="Current Segment",
        readonly=True,
        copy=False,
    )
    to_segment = fields.Selection(
        lambda self: self.env["fix.supplier"]._fields["segment"].selection,
        string="Proposed Segment",
        required=True,
    )
    annual_spend = fields.Float(string="Annual Spend (BDT)")
    criticality = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        required=True,
        default="medium",
    )
    risk_tier = fields.Selection(RISK_TIERS, string="Risk Tier")
    reason = fields.Text(string="Basis / Reason", required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("proposed", "Proposed"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
    )
    proposed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Date(readonly=True, copy=False)
    reject_reason = fields.Char(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "from_segment",
            "proposed_by_id",
            "decided_by_id",
            "decided_on",
            "reject_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= {"supplier_id", "to_segment", "annual_spend", "criticality", "risk_tier"}
            locked |= {"reason"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.segment.review")
                    or "SSEG/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        frozen = {"supplier_id", "to_segment", "annual_spend", "criticality", "risk_tier"}
        frozen = (frozen | {"reason"}) & set(vals)
        if frozen and not self._fix_guard_has_token():
            for rec in self:
                if rec.state != "draft" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen
                ):
                    raise UserError(
                        "Segment review %s is %s: reject it and propose again."
                        % (rec.name, rec.state)
                    )
        return super().write(vals)

    def action_propose(self):
        _require(self.env, "Proposing a segment change", GROUP_STEWARD)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Segment review %s is %s." % (rec.name, rec.state))
            if rec.to_segment == rec.supplier_id.segment:
                raise UserError(
                    "Supplier %s is already %s." % (rec.supplier_id.supplier_code, rec.to_segment)
                )
            if not (rec.reason or "").strip():
                raise UserError("State the basis for re-segmenting %s." % rec.supplier_id.name)
            rec._guarded().write(
                {
                    "state": "proposed",
                    "from_segment": rec.supplier_id.segment,
                    "proposed_by_id": self.env.uid,
                }
            )
        return True

    def action_approve(self):
        _require(self.env, "Approving a segment change", GROUP_APPROVER)
        for rec in self:
            if rec.state != "proposed":
                raise UserError(
                    "Approve a proposed segment review (%s is %s)." % (rec.name, rec.state)
                )
            _not_by(self.env, rec.create_uid | rec.proposed_by_id, "proposed this segment change")
            supplier = rec.supplier_id
            if supplier.segment != rec.from_segment:
                raise UserError(
                    "Supplier %s changed segment since this review was proposed; propose again."
                    % supplier.supplier_code
                )
            supplier._guarded().write({"segment": rec.to_segment})
            supplier.message_post(
                body="Segment %s → %s (review %s): %s"
                % (rec.from_segment, rec.to_segment, rec.name, rec.reason)
            )
            rec._guarded().write(
                {"state": "approved", "decided_by_id": self.env.uid, "decided_on": _today(self)}
            )
            publish(
                self.env,
                "supplier.segment_changed",
                "fix.supplier",
                supplier.id,
                {
                    "supplier": supplier.supplier_code,
                    "from": rec.from_segment,
                    "to": rec.to_segment,
                },
            )
        return True

    def action_reject(self, reason=None):
        _require(self.env, "Rejecting a segment change", GROUP_APPROVER)
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Segment review %s is %s." % (rec.name, rec.state))
            if not (reason or "").strip():
                raise UserError("State why segment review %s is rejected." % rec.name)
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": self.env.uid,
                    "decided_on": _today(self),
                    "reject_reason": reason.strip(),
                }
            )
        return True


class FixQualificationQuestionnaire(models.Model):
    """A qualification template per category and risk tier (FR-SRM2-008): its
    questions, the evidence it makes mandatory and its pass threshold."""

    _name = "fix.qualification.questionnaire"
    _description = "Qualification Questionnaire Template"
    _inherit = ["fix.guarded.mixin"]
    _order = "name, version desc"

    name = fields.Char(required=True)
    spend_category = fields.Char(string="Spend Category")
    category_id = fields.Many2one("product.category", string="Product Category")
    risk_tier = fields.Selection(RISK_TIERS)
    questions = fields.Text(required=True, help="One question per line, with its weight.")
    required_doc_types = fields.Char(
        string="Mandatory Evidence",
        help="Comma-separated document types the supplier must hold verified before the "
        "qualification is approved, e.g. iso,brand_authorisation.",
    )
    pass_threshold = fields.Float(
        default=70.0, help="Never lowers the estate-wide qualification threshold."
    )
    version = fields.Integer(default=1, required=True)
    active = fields.Boolean(default=True)

    _threshold_range = models.Constraint(
        "CHECK (pass_threshold >= 0 AND pass_threshold <= 100)", "The threshold is 0–100"
    )

    @api.constrains("required_doc_types")
    def _check_doc_types(self):
        known = dict(self.env["fix.supplier.document"]._fields["doc_type"].selection)
        for rec in self:
            bad = [t for t in rec._doc_types() if t not in known]
            if bad:
                raise ValidationError(
                    "Unknown document type(s) %s; use %s." % (", ".join(bad), ", ".join(known))
                )

    def _doc_types(self):
        self.ensure_one()
        return [t.strip() for t in (self.required_doc_types or "").split(",") if t.strip()]


class FixSupplierDocumentAuthorisation(models.Model):
    _inherit = "fix.supplier.document"

    doc_type = fields.Selection(
        selection_add=[("brand_authorisation", "Brand / OEM Authorisation")],
        ondelete={"brand_authorisation": "set default"},
    )


class FixSupplierQualificationTemplate(models.Model):
    _inherit = "fix.supplier.qualification"

    questionnaire_id = fields.Many2one(
        "fix.qualification.questionnaire", string="Questionnaire", index=True
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state in ("approved", "rejected") for r in self):
            locked |= {"questionnaire_id"}
        return locked

    def write(self, vals):
        if "questionnaire_id" in vals and not self._fix_guard_has_token():
            for rec in self:
                if rec.state in ("approved", "rejected") and rec._fix_guard_differs(
                    "questionnaire_id", vals["questionnaire_id"], rec.questionnaire_id
                ):
                    raise UserError(
                        "Qualification %s is %s: its questionnaire is final."
                        % (rec.name, rec.state)
                    )
        return super().write(vals)

    def _a06_template_problems(self):
        """BRU-SRM2-05 and the template's own evidence and threshold."""
        self.ensure_one()
        supplier = self.supplier_id.sudo()
        Doc = self.env["fix.supplier.document"].sudo()
        labels = dict(Doc._fields["doc_type"].selection)
        wanted = list(self.questionnaire_id._doc_types()) if self.questionnaire_id else []
        if supplier.classification in AUTHORISED_CLASSES and "brand_authorisation" not in wanted:
            wanted.append("brand_authorisation")
        problems = []
        for doc_type in wanted:
            if not Doc.search_count(
                [
                    ("supplier_id", "=", supplier.id),
                    ("doc_type", "=", doc_type),
                    ("is_valid", "=", True),
                ]
            ):
                problems.append("no verified, unexpired %s" % labels.get(doc_type, doc_type))
        threshold = self.questionnaire_id.pass_threshold if self.questionnaire_id else 0.0
        if threshold and (self.score or 0.0) < threshold:
            problems.append(
                "score %.1f is below the questionnaire's threshold %.1f"
                % (self.score or 0.0, threshold)
            )
        return problems

    def action_approve(self):
        for rec in self:
            if rec.state != "in_review":
                continue  # the base method refuses it with its own message
            problems = rec._a06_template_problems()
            if problems:
                raise UserError(
                    "Qualification %s cannot be approved: %s." % (rec.name, "; ".join(problems))
                )
        return super().action_approve()


AGREEMENT_TERMS = (
    "supplier_id",
    "agreement_type",
    "reference",
    "term_from",
    "term_to",
    "currency_id",
    "committed_value",
    "committed_volume",
    "service_levels",
    "penalties",
    "rebate_terms",
    "notice_days",
    "renewal_mode",
    "parts_scope",
    "valuation_basis",
    "settlement_trigger",
    "settlement_cadence",
    "return_rights",
    "reconciliation_frequency",
    "loss_liability",
)
CONSIGNMENT_TERMS = (
    "parts_scope",
    "valuation_basis",
    "settlement_trigger",
    "settlement_cadence",
    "return_rights",
    "reconciliation_frequency",
    "loss_liability",
)


class FixSupplierAgreement(models.Model):
    """A framework, supply, consignment, service or courier agreement
    (FR-SRM2-021/024/026). A steward drafts it with the signed copy; a
    Supplier Approver who did not draft it puts it in force. Its terms are
    then fixed: a change is a new agreement. Consignment terms recorded here
    are the authority M15 enforces (BRU-SRM2-15)."""

    _name = "fix.supplier.agreement"
    _description = "Supplier Agreement"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "term_to desc, id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(related="supplier_id.company_id", store=True, readonly=True)
    agreement_type = fields.Selection(
        [
            ("framework", "Framework Agreement"),
            ("supply", "Supply Agreement"),
            ("consignment", "Consignment Agreement"),
            ("service", "Service Agreement"),
            ("courier", "Courier Agreement"),
        ],
        string="Type",
        required=True,
        default="framework",
    )
    reference = fields.Char(string="Agreement Reference", required=True)
    term_from = fields.Date(required=True, default=fields.Date.context_today)
    term_to = fields.Date(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    committed_value = fields.Monetary(currency_field="currency_id")
    committed_volume = fields.Char()
    service_levels = fields.Text()
    penalties = fields.Text()
    rebate_terms = fields.Text()
    notice_days = fields.Integer(string="Notice Period (days)", default=30)
    renewal_mode = fields.Selection(
        [("manual", "Renew by decision"), ("auto", "Auto-renew"), ("retender", "Re-tender")],
        required=True,
        default="manual",
    )
    # consignment terms (FR-SRM2-024)
    parts_scope = fields.Text(string="Parts in Scope")
    valuation_basis = fields.Selection(
        [
            ("supplier_price", "Supplier's list price"),
            ("agreed_price", "Agreed price list"),
            ("cost", "Landed cost"),
        ],
    )
    settlement_trigger = fields.Selection(
        [
            ("consumption", "On consumption / sale"),
            ("period", "Per period"),
            ("withdrawal", "On withdrawal from stock"),
        ],
    )
    settlement_cadence = fields.Selection(
        [("weekly", "Weekly"), ("monthly", "Monthly"), ("quarterly", "Quarterly")]
    )
    return_rights = fields.Text()
    reconciliation_frequency = fields.Selection(
        [("monthly", "Monthly"), ("quarterly", "Quarterly"), ("half_yearly", "Half-yearly")]
    )
    loss_liability = fields.Selection(
        [("supplier", "Supplier"), ("fix", "1000FiX"), ("shared", "Shared")],
        string="Liability for Loss or Damage",
    )
    file = fields.Binary(string="Signed Agreement", attachment=True, copy=False)
    file_filename = fields.Char(string="File Name", copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "In Force"),
            ("expired", "Expired"),
            ("terminated", "Terminated"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_on = fields.Date(readonly=True, copy=False)
    terminated_reason = fields.Char(readonly=True, copy=False)
    days_to_expiry = fields.Integer(compute="_compute_days_to_expiry")
    price_ids = fields.One2many("fix.supplier.price.list", "agreement_id", string="Agreed Prices")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_on",
            "terminated_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(AGREEMENT_TERMS) | {"file", "file_filename"}
        return locked

    @api.depends("term_to")
    def _compute_days_to_expiry(self):
        today = _today(self)
        for rec in self:
            rec.days_to_expiry = (rec.term_to - today).days if rec.term_to else 0

    @api.constrains("term_from", "term_to")
    def _check_term(self):
        for rec in self:
            if rec.term_from and rec.term_to and rec.term_to < rec.term_from:
                raise ValidationError("Agreement %s ends before it starts." % rec.reference)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.agreement") or "SAGR/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        terms = (set(AGREEMENT_TERMS) | {"file"}) & set(vals)
        if terms and not self._fix_guard_has_token():
            for rec in self:
                if rec.state == "draft":
                    continue
                changed = [
                    n for n in terms if n != "file" and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if "file" in vals:
                    new = vals["file"]
                    new = new.encode() if isinstance(new, str) else (new or b"")
                    if new != (rec.file or b""):
                        changed.append("file")
                if changed:
                    raise UserError(
                        "Agreement %s is %s: its terms are fixed. Record the change as a new "
                        "agreement." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def action_activate(self):
        """A Supplier Approver who did not draft it puts it in force."""
        _require(self.env, "Putting a supplier agreement in force", GROUP_APPROVER)
        today = _today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Agreement %s is %s." % (rec.name, rec.state))
            _not_by(
                self.env, rec.create_uid | rec.write_uid, "drafted or last edited this agreement"
            )
            if rec.supplier_id.status in ("suspended", "deactivated"):
                raise UserError(
                    "Supplier %s is %s: no agreement is put in force."
                    % (rec.supplier_id.supplier_code, rec.supplier_id.status)
                )
            if not rec.file:
                raise UserError("Agreement %s needs the uploaded signed copy." % rec.name)
            if rec.term_to < today:
                raise UserError("Agreement %s ended on %s." % (rec.name, rec.term_to))
            if rec.agreement_type == "consignment":
                missing = [rec._fields[n].string for n in CONSIGNMENT_TERMS if not rec[n]]
                if missing:
                    raise UserError(
                        "Consignment agreement %s needs its terms (BRU-SRM2-15): %s."
                        % (rec.name, ", ".join(missing))
                    )
            rec._guarded().write(
                {"state": "active", "approved_by_id": self.env.uid, "approved_on": today}
            )
            rec.message_post(body="Put in force by %s." % self.env.user.name)
            publish(
                self.env,
                "supplier.agreement_activated",
                "fix.supplier.agreement",
                rec.id,
                {
                    "agreement": rec.name,
                    "supplier_id": rec.supplier_id.id,
                    "type": rec.agreement_type,
                    "term_to": str(rec.term_to),
                },
            )
        return True

    def action_terminate(self, reason=None):
        _require(self.env, "Terminating a supplier agreement", GROUP_APPROVER)
        for rec in self:
            if rec.state != "active":
                raise UserError(
                    "Only an agreement in force is terminated (%s is %s)." % (rec.name, rec.state)
                )
            if not (reason or "").strip():
                raise UserError("State why agreement %s is terminated." % rec.name)
            rec._guarded().write({"state": "terminated", "terminated_reason": reason.strip()})
            rec.message_post(body="Terminated: %s" % reason.strip())
        return True

    @api.model
    def _cron_agreement_expiry(self):
        """BRU-SRM2-19: warn at 90/60/30 days (a to-do on the supplier, once
        each) and expire an agreement past its end date."""
        today = _today(self)
        Agreement = self.sudo()
        expired = Agreement.search([("state", "=", "active"), ("term_to", "<", today)])
        expired._guarded().write({"state": "expired"})
        Activity = self.env["mail.activity"].sudo()
        made = Activity
        for days in (90, 60, 30):
            for rec in Agreement.search(
                [("state", "=", "active"), ("term_to", "=", today + timedelta(days=days))]
            ):
                summary = "M42 agreement %s ends in %d days" % (rec.name, days)
                supplier = rec.supplier_id.sudo()
                if Activity.search_count(
                    [
                        ("res_model", "=", "fix.supplier"),
                        ("res_id", "=", supplier.id),
                        ("summary", "=", summary),
                    ]
                ):
                    continue
                made |= supplier.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=rec.term_to,
                    summary=summary,
                    note="Decide renewal or re-tender: after %s its spend is uncontracted."
                    % rec.term_to,
                    user_id=supplier._a06_reminder_user().id,
                )
        return {"expired": expired.ids, "reminders": made.ids}


class FixSupplierPriceList(models.Model):
    """An agreed price per part under an agreement in force (FR-SRM2-022). A
    Supplier Approver other than its preparer approves it; the price is then
    fixed and moves only through an approved price change (FR-SRM2-023). M16
    may not send a PO above it (BRU-SRM2-14)."""

    _name = "fix.supplier.price.list"
    _description = "Agreed Supplier Price"
    _inherit = ["fix.guarded.mixin"]
    _order = "supplier_id, product_id, valid_from desc, id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    agreement_id = fields.Many2one(
        "fix.supplier.agreement", string="Agreement", required=True, ondelete="restrict", index=True
    )
    supplier_id = fields.Many2one(
        related="agreement_id.supplier_id", store=True, readonly=True, index=True
    )
    company_id = fields.Many2one(related="agreement_id.company_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="agreement_id.currency_id", store=True, readonly=True)
    product_id = fields.Many2one("product.product", string="Part", required=True, index=True)
    price = fields.Monetary(string="Agreed Unit Price", currency_field="currency_id", required=True)
    moq = fields.Float(string="Minimum Order Qty", default=1.0)
    lead_time_days = fields.Integer(string="Lead Time (days)")
    volume_breaks = fields.Char(help="e.g. 100+: 950; 500+: 900")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("withdrawn", "Withdrawn")],
        required=True,
        default="draft",
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_on = fields.Date(readonly=True, copy=False)
    source_change_id = fields.Many2one("fix.supplier.price.change", readonly=True, copy=False)

    PRICE_TERMS = ("agreement_id", "product_id", "price", "valid_from", "valid_to")

    _price_positive = models.Constraint("CHECK (price > 0)", "An agreed price is positive")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_on",
            "source_change_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.PRICE_TERMS)
        return locked

    @api.constrains("valid_from", "valid_to")
    def _check_validity(self):
        for rec in self:
            if rec.valid_to and rec.valid_from and rec.valid_to < rec.valid_from:
                raise ValidationError("Price %s ends before it starts." % rec.name)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.price.list") or "SPRC/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        terms = set(self.PRICE_TERMS) & set(vals)
        if terms and not self._fix_guard_has_token():
            for rec in self:
                if rec.state != "draft" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in terms
                ):
                    raise UserError(
                        "Agreed price %s is %s: it changes only through an approved price "
                        "change." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def _overlaps(self):
        self.ensure_one()
        domain = [
            ("id", "!=", self.id),
            ("state", "=", "approved"),
            ("supplier_id", "=", self.supplier_id.id),
            ("product_id", "=", self.product_id.id),
            ("currency_id", "=", self.currency_id.id),
            "|",
            ("valid_to", "=", False),
            ("valid_to", ">=", self.valid_from),
        ]
        if self.valid_to:
            domain.append(("valid_from", "<=", self.valid_to))
        return self.sudo().search(domain)

    def action_approve(self):
        _require(self.env, "Approving an agreed price", GROUP_APPROVER)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Agreed price %s is %s." % (rec.name, rec.state))
            _not_by(self.env, rec.create_uid | rec.write_uid, "prepared this price")
            if rec.agreement_id.state != "active":
                raise UserError(
                    "Agreement %s is not in force: its prices cannot be approved."
                    % rec.agreement_id.name
                )
            clash = rec._overlaps()
            if clash:
                raise UserError(
                    "%s already has an approved price for %s in that period (%s). Change it "
                    "through a price change."
                    % (
                        rec.supplier_id.name,
                        rec.product_id.display_name,
                        ", ".join(clash.mapped("name")),
                    )
                )
            rec._guarded().write(
                {"state": "approved", "approved_by_id": self.env.uid, "approved_on": _today(self)}
            )
        return True

    def action_withdraw(self):
        _require(self.env, "Withdrawing an agreed price", GROUP_APPROVER)
        for rec in self:
            if rec.state != "approved":
                raise UserError("Agreed price %s is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "withdrawn"})
        return True

    @api.model
    def _a06_agreed(self, partner, product, currency, on_date):
        """The approved price in force for this supplier and part: the one in
        `currency` when there is one, else (A06 P04) the latest in any other
        currency - an order in another currency no longer escapes the list."""
        supplier = self.env["fix.supplier"]._for_partner(partner)
        if not supplier or not product:
            return self.browse()
        found = self.sudo().search(
            [
                ("state", "=", "approved"),
                ("agreement_id.state", "=", "active"),
                ("supplier_id", "=", supplier.id),
                ("product_id", "=", product.id),
                ("valid_from", "<=", on_date),
                "|",
                ("valid_to", "=", False),
                ("valid_to", ">=", on_date),
            ],
            order="valid_from desc, id desc",
        )
        same = found.filtered(lambda p: p.currency_id == currency)
        return (same or found)[:1]

    def _a06_price_in(self, currency, company, on_date):
        """This agreed price in `currency` (converted through BDT at the
        day's rate when it is agreed in another one)."""
        self.ensure_one()
        if self.currency_id == currency:
            return self.price
        from odoo.addons.cd_requisition.models.fix_requisition import bdt_rate

        bdt = self.price * bdt_rate(self.env, self.currency_id, company, on_date)
        rate = bdt_rate(self.env, currency, company, on_date)
        return round(bdt / rate, 6) if rate else self.price


class FixSupplierPriceChange(models.Model):
    """A supplier's price movement, submitted with its justification and
    decided by a Supplier Approver who did not request it (FR-SRM2-023). An
    approved change closes the old price the day before it takes effect and
    opens the new one."""

    _name = "fix.supplier.price.change"
    _description = "Supplier Price Change"
    _inherit = ["fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    price_list_id = fields.Many2one(
        "fix.supplier.price.list",
        string="Agreed Price",
        required=True,
        ondelete="restrict",
        index=True,
        domain=[("state", "=", "approved")],
    )
    supplier_id = fields.Many2one(related="price_list_id.supplier_id", store=True, readonly=True)
    product_id = fields.Many2one(related="price_list_id.product_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="price_list_id.currency_id", store=True, readonly=True)
    old_price = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    proposed_price = fields.Monetary(currency_field="currency_id", required=True)
    variance_pct = fields.Float(string="Variance %", compute="_compute_variance", store=True)
    justification = fields.Text(required=True)
    effective_from = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
    )
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Date(readonly=True, copy=False)
    decision_note = fields.Char(readonly=True, copy=False)
    new_price_id = fields.Many2one("fix.supplier.price.list", readonly=True, copy=False)

    CHANGE_TERMS = ("price_list_id", "proposed_price", "justification", "effective_from")

    _proposed_positive = models.Constraint(
        "CHECK (proposed_price > 0)", "A proposed price is positive"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "old_price",
            "requested_by_id",
            "decided_by_id",
            "decided_on",
            "decision_note",
            "new_price_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.CHANGE_TERMS)
        return locked

    @api.depends("old_price", "proposed_price", "price_list_id.price")
    def _compute_variance(self):
        for rec in self:
            base = rec.old_price or rec.price_list_id.price
            rec.variance_pct = round((rec.proposed_price - base) / base * 100.0, 2) if base else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.price.change") or "SPCH/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        terms = set(self.CHANGE_TERMS) & set(vals)
        if terms and not self._fix_guard_has_token():
            for rec in self:
                if rec.state != "draft" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in terms
                ):
                    raise UserError("Price change %s is %s." % (rec.name, rec.state))
        return super().write(vals)

    def action_submit(self):
        _require(self.env, "Submitting a price change", GROUP_STEWARD)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Price change %s is %s." % (rec.name, rec.state))
            line = rec.price_list_id
            if line.state != "approved":
                raise UserError("Price %s is not an approved price." % line.name)
            if abs(rec.proposed_price - line.price) <= PRICE_TOLERANCE:
                raise UserError("Price change %s proposes the current price." % rec.name)
            if rec.effective_from <= line.valid_from:
                raise UserError(
                    "Price change %s must take effect after %s, when the current price started."
                    % (rec.name, line.valid_from)
                )
            if not (rec.justification or "").strip():
                raise UserError("Justify price change %s." % rec.name)
            rec._guarded().write(
                {"state": "submitted", "old_price": line.price, "requested_by_id": self.env.uid}
            )
        return True

    def action_approve(self):
        _require(self.env, "Approving a price change", GROUP_APPROVER)
        for rec in self:
            if rec.state != "submitted":
                raise UserError(
                    "Approve a submitted price change (%s is %s)." % (rec.name, rec.state)
                )
            _not_by(self.env, rec.create_uid | rec.requested_by_id, "requested this price change")
            line = rec.price_list_id.sudo()
            if line.state != "approved" or abs(line.price - rec.old_price) > PRICE_TOLERANCE:
                raise UserError(
                    "Price %s changed since %s was submitted; submit again." % (line.name, rec.name)
                )
            if line.valid_to and rec.effective_from > line.valid_to:
                raise UserError(
                    "Price %s ends on %s, before this change would take effect."
                    % (line.name, line.valid_to)
                )
            end = line.valid_to
            line._guarded().write({"valid_to": rec.effective_from - timedelta(days=1)})
            new = (
                self.env["fix.supplier.price.list"]
                .sudo()
                .create(
                    {
                        "agreement_id": line.agreement_id.id,
                        "product_id": line.product_id.id,
                        "price": rec.proposed_price,
                        "moq": line.moq,
                        "lead_time_days": line.lead_time_days,
                        "volume_breaks": line.volume_breaks,
                        "valid_from": rec.effective_from,
                        "valid_to": end,
                    }
                )
            )
            new._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_on": _today(self),
                    "source_change_id": rec.id,
                }
            )
            rec._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": self.env.uid,
                    "decided_on": _today(self),
                    "new_price_id": new.id,
                }
            )
            publish(
                self.env,
                "supplier.price_changed",
                "fix.supplier.price.change",
                rec.id,
                {
                    "supplier_id": line.supplier_id.id,
                    "product_id": line.product_id.id,
                    "old": rec.old_price,
                    "new": rec.proposed_price,
                    "effective_from": str(rec.effective_from),
                },
            )
        return True

    def action_reject(self, reason=None):
        _require(self.env, "Rejecting a price change", GROUP_APPROVER)
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Price change %s is %s." % (rec.name, rec.state))
            if not (reason or "").strip():
                raise UserError("State why price change %s is rejected." % rec.name)
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": self.env.uid,
                    "decided_on": _today(self),
                    "decision_note": reason.strip(),
                }
            )
        return True


class FixPurchaseOrderAgreedPrice(models.Model):
    """BRU-SRM2-14: a PO line above the agreed price in force for its supplier,
    part and currency is refused at approval request and at send. A part with
    no agreed price is not checked (no list = no authority yet)."""

    _inherit = "fix.purchase.order"

    def _a06_check_categories(self):
        result = super()._a06_check_categories()
        self._a06_check_agreed_prices()
        return result

    def _a06_check_agreed_prices(self):
        Price = self.env["fix.supplier.price.list"]
        on_date = _today(self)
        for order in self:
            for line in order.sudo().line_ids:
                agreed = Price._a06_agreed(
                    order.vendor_id, line.product_id, order.currency_id, on_date
                )
                if not agreed:
                    continue
                ceiling = agreed._a06_price_in(order.currency_id, order.company_id, on_date)
                if line.unit_price > ceiling + PRICE_TOLERANCE:
                    raise UserError(
                        "BRU-SRM2-14: PO %s orders %s at %s %.2f, above the agreed price %s %.2f "
                        "(%s%s). Submit a price change in M42 and have it approved first."
                        % (
                            order.name,
                            line.product_id.display_name,
                            order.currency_id.name,
                            line.unit_price,
                            order.currency_id.name,
                            ceiling,
                            agreed.name,
                            ""
                            if agreed.currency_id == order.currency_id
                            else ", agreed as %s %.2f" % (agreed.currency_id.name, agreed.price),
                        )
                    )
        return True


class FixPurchaseOrderReferencePrice(models.Model):
    """A06 P27: the M42 agreed price list is the first reference price of a
    converted requisition's order line (before the M16 approved source)."""

    _inherit = "fix.purchase.order"

    def _a06_reference_price(self, line):
        self.ensure_one()
        on_date = _today(self)
        agreed = self.env["fix.supplier.price.list"]._a06_agreed(
            self.vendor_id, line.product_id, self.currency_id, on_date
        )
        if agreed:
            return (
                agreed._a06_price_in(self.currency_id, self.company_id, on_date),
                "agreed price %s" % agreed.name,
            )
        return super()._a06_reference_price(line)


class FixProcurementBlanketAgreement(models.Model):
    """A06 P27: an M16 blanket is a call-off vehicle UNDER the supplier's M42
    agreement, never a second, competing contract: where the supplier has an
    agreement in force the blanket names it and stays inside its term and
    currency, and one agreement has one active blanket."""

    _inherit = "fix.procurement.blanket"

    agreement_id = fields.Many2one(
        "fix.supplier.agreement",
        string="Supplier Agreement (M42)",
        index=True,
        ondelete="restrict",
        help="The M42 agreement this blanket calls off under.",
    )

    BLANKET_TERMS = (
        "vendor_id",
        "cap_amount",
        "valid_from",
        "valid_to",
        "currency_id",
        "agreement_id",
    )

    def _a06_agreement_problems(self):
        self.ensure_one()
        Agreement = self.env["fix.supplier.agreement"].sudo()
        supplier = self.env["fix.supplier"]._for_partner(self.vendor_id, self.company_id)
        in_force = Agreement.browse()
        if supplier:
            in_force = Agreement.search(
                [
                    ("supplier_id", "=", supplier.id),
                    ("state", "=", "active"),
                    ("term_from", "<=", self.valid_to),
                    ("term_to", ">=", self.valid_from),
                ]
            )
        agreement = self.agreement_id.sudo()
        if in_force and not agreement:
            return "%s has agreement %s in force: blanket %s calls off under it" % (
                self.vendor_id.display_name,
                ", ".join(in_force.mapped("name")),
                self.name,
            )
        if not agreement:
            return None
        if agreement.supplier_id != supplier or agreement.state != "active":
            return "agreement %s is not an active agreement of %s" % (
                agreement.name,
                self.vendor_id.display_name,
            )
        if self.valid_from < agreement.term_from or self.valid_to > agreement.term_to:
            return "blanket %s runs %s to %s, outside agreement %s (%s to %s)" % (
                self.name,
                self.valid_from,
                self.valid_to,
                agreement.name,
                agreement.term_from,
                agreement.term_to,
            )
        if agreement.currency_id != self.currency_id:
            return "blanket %s is in %s but agreement %s is in %s" % (
                self.name,
                self.currency_id.name,
                agreement.name,
                agreement.currency_id.name,
            )
        twin = self.sudo().search(
            [
                ("id", "!=", self.id),
                ("agreement_id", "=", agreement.id),
                ("state", "=", "active"),
            ],
            limit=1,
        )
        if twin:
            return "agreement %s already has active blanket %s" % (agreement.name, twin.name)
        return None

    def action_activate(self):
        for rec in self:
            problem = rec._a06_agreement_problems()
            if problem:
                raise UserError("Blanket %s: %s." % (rec.name, problem))
        return super().action_activate()
