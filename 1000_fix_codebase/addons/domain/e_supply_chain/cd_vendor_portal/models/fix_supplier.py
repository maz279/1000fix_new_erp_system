# fix_supplier — M42: the supplier register and its governance records. The
# vendor portal module owns the supplier subject (it already depends on the
# requisition module), so the models live here and M16 reads the activation
# state through the supplier record (fix_supplier_controls.py: the PO gate).
#
# A06 workflow audit (2026-11-03), M42-1..10: a supplier was created already
# active, its status typed (ORM and the P03 form), its qualification approved
# with a score of 0 by its own buyer, activated with another supplier's
# qualification and with three self-typed "valid" documents with no number or
# file, re-activated after being blacklisted, kept active with a flagged
# sanctions hit and a critical risk; a hit was erased by writing "clear";
# scorecards were typed (100s for a supplier with no POs) and rewritten after
# publication. Now every state, status and evidence field changes only through
# its action (fix.guarded.mixin) and:
#   - status moves only by qualification approval, the activation gate,
#     suspension / block, and an approved reinstatement;
#   - activation needs an approved qualification of THAT supplier, verified and
#     unexpired mandatory documents, no unresolved screening hit and no
#     critical open risk, decided by a Supplier Approver who did not prepare it;
#   - a document is valid only once a second user verified it with its number
#     and file; a change to it returns it to pending; expiry suspends;
#   - a screening hit is cleared only by an approver's clearance action;
#   - scorecards are computed from M16 purchase-order and receipt facts and
#     frozen once published; two D grades in a row raise a CAR.
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

MANDATORY_DOCS = ("trade_licence", "tin", "vat")

GROUP_STEWARD = "cd_vendor_portal.group_fix_supplier_steward"
GROUP_APPROVER = "cd_vendor_portal.group_fix_supplier_approver"
# BRU-SRM2-16: a blocked (deactivated) supplier is reinstated only by the CFO
# or CEO; the DOFA Tier 4 group is the CFO authority in this estate.
GROUP_CFO = "cd_entity_config.group_dofa_tier_4"

# Business decisions (A06 report §7 B4), kept as configuration:
PARAM_MIN_SCORE = "cd_vendor_portal.qualification_min_score"  # default 70 (grade B floor)
DEFAULT_MIN_SCORE = 70.0
PARAM_REQUAL_GRACE = "cd_vendor_portal.requalification_grace_days"  # default 0
PARAM_ACK_SLA = "cd_vendor_portal.ack_sla_days"  # scorecard responsiveness, default 2
PARAM_CAR_DAYS = "cd_vendor_portal.auto_car_due_days"  # default 30
# Reminder lead time before a document or re-qualification falls due (M42-7).
PARAM_REMINDER_DAYS = "cd_vendor_portal.expiry_reminder_days"  # default 30
REMINDER_PREFIX = "M42 reminder: "


def _param(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    try:
        return float(raw) if raw not in (None, False, "") else float(default)
    except (TypeError, ValueError):
        return float(default)


def _has(env, *xmlids):
    return env.su or any(env.user.has_group(x) for x in xmlids)


def _require(env, what, *xmlids):
    if not _has(env, *xmlids):
        names = [
            (env.ref(x, raise_if_not_found=False) or env["res.groups"]).name or x for x in xmlids
        ]
        raise UserError("%s needs the %s role." % (what, " or ".join(names)))


def _bool_positive(operator, value):
    """Whether a search on a boolean compute asks for True (Odoo 19 normalises
    `= True` to `in [True]`)."""
    if operator in ("in", "not in"):
        hit = any(bool(v) for v in (value or []))
        return hit if operator == "in" else not hit
    return bool(value) if operator in ("=", "==") else not bool(value)


def _not_by(env, users, what):
    """Two-person rule: the acting user is none of `users`."""
    if env.su:
        return
    if env.user in users:
        raise UserError("Segregation of duties: you %s; another person must do this." % what)


class FixSupplier(models.Model):
    _name = "fix.supplier"
    _description = "Supplier"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one(
        "res.partner", string="Contact", required=True, ondelete="restrict", index=True
    )
    supplier_code = fields.Char(required=True, default="New", copy=False)
    segment = fields.Selection(
        [
            ("strategic", "Strategic"),
            ("preferred", "Preferred"),
            ("transactional", "Transactional"),
            ("probationary", "Probationary"),
        ],
        required=True,
        default="transactional",
    )
    category = fields.Char(string="Spend Category")
    buyer_id = fields.Many2one("hr.employee", string="Buyer")
    onboarded_on = fields.Date()
    status = fields.Selection(
        [
            ("prospect", "Prospect"),
            ("qualified", "Qualified"),
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("deactivated", "Deactivated (Blocked)"),
        ],
        required=True,
        default="prospect",
        index=True,
        tracking=True,
    )
    status_reason = fields.Char(readonly=True, copy=False)
    status_changed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    status_changed_at = fields.Datetime(readonly=True, copy=False)
    reinstatement_reason = fields.Char(readonly=True, copy=False)
    reinstatement_requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    reinstatement_requested_at = fields.Datetime(readonly=True, copy=False)
    payment_block = fields.Boolean(
        readonly=True,
        copy=False,
        tracking=True,
        help="Set while a bank-detail change awaits confirmation: no payment is released.",
    )
    bank_account_id = fields.Many2one(
        "res.partner.bank",
        string="Approved Payee Account",
        readonly=True,
        copy=False,
        help="The account a confirmed bank-detail change approved. Payment runs pay to it.",
    )
    notes = fields.Text()

    SUPPLIER_GUARDED = {
        "status",
        "status_reason",
        "status_changed_by_id",
        "status_changed_at",
        "reinstatement_reason",
        "reinstatement_requested_by_id",
        "reinstatement_requested_at",
        "payment_block",
        "bank_account_id",
    }

    _partner_unique = models.Constraint("UNIQUE (partner_id)", "One supplier record per partner")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.SUPPLIER_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(s.status != "prospect" for s in self):
            locked |= {"partner_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("supplier_code", "New") == "New":
                vals["supplier_code"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier") or "SUP/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if "partner_id" in vals and not self._fix_guard_has_token():
            for rec in self:
                if rec.status != "prospect" and rec._fix_guard_differs(
                    "partner_id", vals["partner_id"], rec.partner_id
                ):
                    raise UserError(
                        "Supplier %s is %s: its partner (the payee) is fixed."
                        % (rec.supplier_code, rec.status)
                    )
        return super().write(vals)

    @api.model
    def _for_partner(self, partner):
        if not partner:
            return self.browse()
        ids = list({partner.id, partner.commercial_partner_id.id})
        return self.sudo().search([("partner_id", "in", ids)], limit=1)

    # ---- compliance -------------------------------------------------------
    def _a06_document_problems(self):
        self.ensure_one()
        docs = self.env["fix.supplier.document"].sudo().search([("supplier_id", "=", self.id)])
        labels = dict(docs._fields["doc_type"].selection)
        problems = []
        for doc_type in MANDATORY_DOCS:
            if not docs.filtered(lambda d, t=doc_type: d.doc_type == t and d.is_valid):
                problems.append("no verified, unexpired %s" % labels.get(doc_type, doc_type))
        return problems

    def _a06_screening_problems(self):
        self.ensure_one()
        hits = (
            self.env["fix.supplier.screening"]
            .sudo()
            .search(
                [("supplier_id", "=", self.id), ("result", "=", "hit"), ("state", "!=", "cleared")]
            )
        )
        labels = dict(hits._fields["screening_type"].selection)
        return [
            "unresolved %s screening hit (%s)" % (labels.get(h.screening_type), h.name)
            for h in hits
        ]

    def _a06_risk_problems(self):
        self.ensure_one()
        risks = (
            self.env["fix.supplier.risk"]
            .sudo()
            .search(
                [("supplier_id", "=", self.id), ("band", "=", "critical"), ("state", "=", "open")]
            )
        )
        return ["critical open risk %s" % r.name for r in risks]

    def _a06_order_problems(self):
        """Why an active supplier may still not be ordered from today (the
        PO gate re-checks, fail closed, before the cron has suspended it)."""
        self.ensure_one()
        return self._a06_document_problems() + self._a06_screening_problems()

    def _a06_activation_problems(self):
        self.ensure_one()
        return (
            self._a06_document_problems()
            + self._a06_screening_problems()
            + self._a06_risk_problems()
        )

    # ---- status transitions ---------------------------------------------
    def _a06_set_status(self, status, reason):
        for rec in self:
            before = rec.status
            rec._guarded().write(
                {
                    "status": status,
                    "status_reason": reason,
                    "status_changed_by_id": self.env.uid,
                    "status_changed_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Status %s → %s: %s" % (before, status, reason))
            publish(
                self.env,
                "supplier.status_changed",
                "fix.supplier",
                rec.id,
                {
                    "supplier": rec.supplier_code,
                    "partner_id": rec.partner_id.id,
                    "from": before,
                    "to": status,
                    "reason": reason,
                },
            )

    def _a06_auto_suspend(self, reason):
        """Automatic suspension (BRU-SRM2-04/10): document expiry, a flagged
        hit, a failed re-qualification."""
        active = self.filtered(lambda s: s.status == "active")
        active.sudo()._a06_set_status("suspended", reason)
        return active

    def action_suspend(self, reason=None):
        _require(self.env, "Suspending a supplier", GROUP_STEWARD, GROUP_APPROVER)
        for rec in self:
            if rec.status not in ("active", "qualified"):
                raise UserError(
                    "Only an active or qualified supplier is suspended (%s is %s)."
                    % (rec.supplier_code, rec.status)
                )
            if not (reason or "").strip():
                raise UserError("State why supplier %s is suspended." % rec.supplier_code)
            rec._a06_set_status("suspended", reason.strip())
        return True

    def action_block(self, reason=None):
        """Permanent block (blacklist: sanctions, counterfeit, fraud)."""
        _require(self.env, "Blocking a supplier", GROUP_STEWARD, GROUP_APPROVER)
        for rec in self:
            if rec.status == "deactivated":
                raise UserError("Supplier %s is already blocked." % rec.supplier_code)
            if not (reason or "").strip():
                raise UserError("State why supplier %s is blocked." % rec.supplier_code)
            rec._a06_set_status("deactivated", reason.strip())
        return True

    def action_request_reinstatement(self, reason=None):
        _require(self.env, "Requesting a reinstatement", GROUP_STEWARD)
        for rec in self:
            if rec.status not in ("suspended", "deactivated"):
                raise UserError(
                    "Only a suspended or blocked supplier is reinstated (%s is %s)."
                    % (rec.supplier_code, rec.status)
                )
            if not (reason or "").strip():
                raise UserError("State why supplier %s should be reinstated." % rec.supplier_code)
            rec._guarded().write(
                {
                    "reinstatement_reason": reason.strip(),
                    "reinstatement_requested_by_id": self.env.uid,
                    "reinstatement_requested_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Reinstatement requested: %s" % reason.strip())
        return True

    def action_approve_reinstatement(self):
        """A Supplier Approver other than the requester reinstates; a blocked
        supplier also needs the CFO authority (BRU-SRM2-16). The gate's
        compliance checks apply again."""
        _require(self.env, "Approving a reinstatement", GROUP_APPROVER)
        for rec in self:
            if rec.status not in ("suspended", "deactivated"):
                raise UserError("Supplier %s is %s." % (rec.supplier_code, rec.status))
            if not rec.reinstatement_requested_by_id:
                raise UserError("No reinstatement was requested for %s." % rec.supplier_code)
            _not_by(
                self.env,
                rec.reinstatement_requested_by_id,
                "requested this reinstatement",
            )
            if rec.status == "deactivated" and not _has(self.env, GROUP_CFO):
                raise UserError(
                    "Supplier %s is blocked: only the CFO authority (DOFA Tier 4) reinstates "
                    "it." % rec.supplier_code
                )
            qualified = (
                self.env["fix.supplier.qualification"]
                .sudo()
                .search_count([("supplier_id", "=", rec.id), ("state", "=", "approved")])
            )
            problems = rec._a06_activation_problems()
            if not qualified:
                problems.insert(0, "no approved qualification")
            if problems:
                raise UserError(
                    "Reinstatement of %s refused: %s." % (rec.supplier_code, "; ".join(problems))
                )
            reason = "reinstated: %s" % rec.reinstatement_reason
            rec._a06_set_status("active", reason)
            rec._guarded().write(
                {
                    "reinstatement_reason": False,
                    "reinstatement_requested_by_id": False,
                    "reinstatement_requested_at": False,
                }
            )
        return True

    # ---- cron ---------------------------------------------------------------
    @api.model
    def _cron_lifecycle_sweep(self):
        """Daily (BRU-SRM2-04/11): expire documents past their end date,
        suspend active suppliers whose mandatory documents are no longer
        valid or whose re-qualification is overdue, and escalate overdue
        CARs once."""
        today = fields.Date.context_today(self)
        Doc = self.env["fix.supplier.document"].sudo()
        expired = Doc.search([("state", "=", "valid"), ("valid_to", "<", today)])
        expired._guarded().write({"state": "expired"})
        suspended = self.browse()
        for supplier in self.sudo().search([("status", "=", "active")]):
            problems = supplier._a06_document_problems()
            if problems:
                suspended |= supplier._a06_auto_suspend("documents: %s" % "; ".join(problems))
        grace = int(_param(self.env, PARAM_REQUAL_GRACE, 0))
        overdue = (
            self.env["fix.supplier.requalification"]
            .sudo()
            .search([("state", "!=", "done"), ("due_on", "<", today - timedelta(days=grace))])
        )
        for requal in overdue:
            suspended |= requal.supplier_id._a06_auto_suspend(
                "re-qualification %s overdue since %s" % (requal.name, requal.due_on)
            )
        cars = (
            self.env["fix.supplier.car"]
            .sudo()
            .search(
                [("state", "!=", "closed"), ("due_date", "<", today), ("escalated_on", "=", False)]
            )
        )
        for car in cars:
            car._guarded().write({"escalated_on": today})
            publish(
                self.env,
                "supplier.car.overdue",
                "fix.supplier.car",
                car.id,
                {"car": car.name, "supplier_id": car.supplier_id.id, "due": str(car.due_date)},
            )
        reminders = self._a06_schedule_reminders(today)
        return {
            "expired_documents": expired.ids,
            "suspended": suspended.ids,
            "escalated_cars": cars.ids,
            "reminders": reminders.ids,
        }

    def _a06_reminder_user(self):
        """Who is reminded: the supplier's buyer, else the steward who
        registered it."""
        self.ensure_one()
        return self.buyer_id.user_id or self.create_uid

    @api.model
    def _a06_schedule_reminders(self, today):
        """Before suspension, a reminder (M42-7): a to-do activity on the
        supplier for every mandatory document and re-qualification falling due
        within the lead time. One open reminder per item; it is not repeated."""
        days = int(_param(self.env, PARAM_REMINDER_DAYS, 30))
        horizon = today + timedelta(days=days)
        Activity = self.env["mail.activity"].sudo()
        made = Activity
        items = []
        docs = (
            self.env["fix.supplier.document"]
            .sudo()
            .search(
                [
                    ("state", "=", "valid"),
                    ("doc_type", "in", MANDATORY_DOCS),
                    ("valid_to", ">=", today),
                    ("valid_to", "<=", horizon),
                    ("supplier_id.status", "=", "active"),
                ]
            )
        )
        for doc in docs:
            items.append(
                (doc.supplier_id, "document %s expires %s" % (doc.name, doc.valid_to), doc.valid_to)
            )
        requals = (
            self.env["fix.supplier.requalification"]
            .sudo()
            .search(
                [
                    ("state", "!=", "done"),
                    ("due_on", ">=", today),
                    ("due_on", "<=", horizon),
                    ("supplier_id.status", "=", "active"),
                ]
            )
        )
        for requal in requals:
            items.append(
                (
                    requal.supplier_id,
                    "re-qualification %s due %s" % (requal.name, requal.due_on),
                    requal.due_on,
                )
            )
        for supplier, what, due in items:
            summary = REMINDER_PREFIX + what
            if Activity.search_count(
                [
                    ("res_model", "=", "fix.supplier"),
                    ("res_id", "=", supplier.id),
                    ("summary", "=", summary),
                ]
            ):
                continue
            made |= supplier.sudo().activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=due,
                summary=summary,
                note="Renew it before it lapses: on that date the supplier is suspended and no "
                "purchase order can be sent to it.",
                user_id=supplier._a06_reminder_user().id,
            )
        return made


class FixSupplierDocument(models.Model):
    _name = "fix.supplier.document"
    _description = "Supplier Document"
    _inherit = ["fix.guarded.mixin"]
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    doc_type = fields.Selection(
        [
            ("trade_licence", "Trade Licence"),
            ("tin", "TIN Certificate"),
            ("vat", "VAT Registration"),
            ("iso", "ISO Certificate"),
            ("insurance", "Insurance"),
            ("bank", "Bank Details"),
            ("contract", "Signed Contract"),
            ("other", "Other"),
        ],
        required=True,
        default="trade_licence",
    )
    number = fields.Char(string="Document Number")
    valid_from = fields.Date()
    valid_to = fields.Date()
    file_ref = fields.Char(string="File Reference")
    state = fields.Selection(
        [("valid", "Valid"), ("pending", "Pending"), ("expired", "Expired")],
        required=True,
        default="pending",
    )
    verified_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    verified_on = fields.Date(readonly=True, copy=False)
    is_valid = fields.Boolean(
        compute="_compute_is_valid",
        search="_search_is_valid",
        help="Verified and not past its end date, today.",
    )

    DOC_EVIDENCE = ("supplier_id", "doc_type", "number", "valid_from", "valid_to", "file_ref")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "verified_by_id", "verified_on"}

    @api.depends("state", "valid_to")
    def _compute_is_valid(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_valid = bool(
                rec.state == "valid" and (not rec.valid_to or rec.valid_to >= today)
            )

    def _search_is_valid(self, operator, value):
        today = fields.Date.context_today(self)
        valid = [
            "&",
            ("state", "=", "valid"),
            "|",
            ("valid_to", "=", False),
            ("valid_to", ">=", today),
        ]
        return valid if _bool_positive(operator, value) else ["!", *valid]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.document") or "SDOC/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        evidence = set(self.DOC_EVIDENCE) & set(vals)
        reverify = self.browse()
        if evidence and not self._fix_guard_has_token():
            reverify = self.filtered(
                lambda d: (
                    d.state == "valid"
                    and any(d._fix_guard_differs(n, vals[n], d[n]) for n in evidence)
                )
            )
        suppliers = reverify.mapped("supplier_id")
        result = super().write(vals)
        if reverify:
            reverify._guarded().write(
                {"state": "pending", "verified_by_id": False, "verified_on": False}
            )
            for supplier in suppliers.sudo():
                problems = supplier._a06_document_problems()
                if problems:
                    supplier._a06_auto_suspend(
                        "a mandatory document changed and awaits re-verification: %s"
                        % "; ".join(problems)
                    )
        return result

    def action_verify(self):
        """A second user verifies the document against its file."""
        _require(self.env, "Verifying a supplier document", GROUP_STEWARD, GROUP_APPROVER)
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state == "valid":
                raise UserError("Document %s is already verified." % rec.name)
            _not_by(
                self.env, rec.create_uid | rec.write_uid, "recorded or last edited this document"
            )
            if not (rec.number or "").strip() or not (rec.file_ref or "").strip():
                raise UserError(
                    "Document %s needs its number and the file reference of the evidence "
                    "before it can be verified." % rec.name
                )
            if rec.valid_to and rec.valid_to < today:
                raise UserError("Document %s expired on %s." % (rec.name, rec.valid_to))
            rec._guarded().write(
                {"state": "valid", "verified_by_id": self.env.uid, "verified_on": today}
            )
        return True


class FixSupplierQualification(models.Model):
    _name = "fix.supplier.qualification"
    _description = "Supplier Qualification"
    _inherit = ["fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    stage = fields.Selection(
        [
            ("documents", "Documents"),
            ("site_audit", "Site Audit"),
            ("sample_approval", "Sample Approval"),
            ("finance", "Finance Review"),
            ("activation", "Activation"),
        ],
        required=True,
        default="documents",
    )
    submitted_on = fields.Date(required=True, default=fields.Date.context_today)
    auditor_id = fields.Many2one("hr.employee", string="Auditor")
    score = fields.Float(string="Score (0–100)")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_review", "In Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
    )
    approved_on = fields.Date(readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    notes = fields.Text()

    _score_range = models.Constraint(
        "CHECK (score >= 0 AND score <= 100)", "The score is a 0–100 value"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_on", "approved_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state in ("approved", "rejected") for r in self):
            locked |= {"supplier_id", "score", "stage", "auditor_id", "submitted_on"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.qualification")
                    or "SQUAL/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        fixed = {"supplier_id", "score", "stage", "auditor_id", "submitted_on"} & set(vals)
        if fixed and not self._fix_guard_has_token():
            for rec in self:
                if rec.state in ("approved", "rejected") and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in fixed
                ):
                    raise UserError(
                        "Qualification %s is %s: its score and supplier are final."
                        % (rec.name, rec.state)
                    )
        return super().write(vals)

    def action_start(self):
        _require(self.env, "Starting a qualification review", GROUP_STEWARD)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Start a draft qualification")
            rec._guarded().write({"state": "in_review"})

    def action_approve(self):
        """A Supplier Approver who neither scored nor audited the supplier,
        and is not its buyer, approves a score at or above the threshold."""
        _require(self.env, "Approving a qualification", GROUP_APPROVER)
        min_score = _param(self.env, PARAM_MIN_SCORE, DEFAULT_MIN_SCORE)
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Approve a qualification in review")
            _not_by(
                self.env,
                rec.create_uid | rec.auditor_id.user_id | rec.supplier_id.buyer_id.user_id,
                "scored, audited or buy from this supplier",
            )
            if (rec.score or 0.0) < min_score:
                raise UserError(
                    "Qualification %s scored %.1f; the approval threshold is %.1f."
                    % (rec.name, rec.score or 0.0, min_score)
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_on": fields.Date.context_today(self),
                    "approved_by_id": self.env.uid,
                }
            )
            if rec.supplier_id.status == "prospect":
                rec.supplier_id.sudo()._a06_set_status(
                    "qualified", "qualification %s approved" % rec.name
                )

    def action_reject(self):
        _require(self.env, "Rejecting a qualification", GROUP_APPROVER, GROUP_STEWARD)
        for rec in self:
            if rec.state not in ("draft", "in_review"):
                raise UserError("Qualification %s is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "rejected"})


class FixSupplierActivation(models.Model):
    """The activation gate: a supplier goes active only when its own
    qualification is approved, its mandatory documents are verified and
    unexpired, no screening hit is unresolved and no critical risk is open —
    decided by a Supplier Approver who did not prepare the activation."""

    _name = "fix.supplier.activation"
    _description = "Supplier Activation Gate"
    _inherit = ["fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    qualification_id = fields.Many2one(
        "fix.supplier.qualification", string="Qualification", ondelete="set null"
    )
    activated_on = fields.Date(readonly=True, copy=False)
    activated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("activated", "Activated"), ("blocked", "Blocked")],
        required=True,
        default="draft",
    )
    blocker = fields.Char(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "activated_on",
            "activated_by_id",
            "blocker",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= {"supplier_id", "qualification_id"}
        return locked

    def write(self, vals):
        if (
            {"supplier_id", "qualification_id"} & set(vals)
            and not self._fix_guard_has_token()
            and any(r.state == "activated" for r in self)
        ):
            raise UserError("A completed activation is a record; raise a new one.")
        return super().write(vals)

    def _blockers(self):
        self.ensure_one()
        problems = []
        supplier = self.supplier_id.sudo()
        qual = self.qualification_id.sudo()
        if supplier.status in ("suspended", "deactivated"):
            problems.append(
                "supplier is %s: it returns only through an approved reinstatement"
                % supplier.status
            )
        elif supplier.status == "active":
            problems.append("supplier is already active")
        if not qual or qual.state != "approved":
            problems.append("no approved qualification")
        elif qual.supplier_id != supplier:
            problems.append("qualification %s belongs to another supplier" % qual.name)
        return problems + supplier._a06_activation_problems()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.activation") or "SACT/New"
                )
        records = super().create(vals_list)
        records._a06_check_one_live()
        return records

    def _a06_check_one_live(self):
        """M42-10: no activation of an already-active supplier, and one pending
        activation request per supplier (live: supplier 9 activated 4 times)."""
        for rec in self:
            supplier = rec.supplier_id.sudo()
            if supplier.status == "active":
                raise UserError(
                    "Supplier %s is already active; it needs no activation."
                    % supplier.supplier_code
                )
            if self.sudo().search_count(
                [("supplier_id", "=", supplier.id), ("state", "=", "draft"), ("id", "!=", rec.id)]
            ):
                raise UserError(
                    "Supplier %s already has a pending activation request." % supplier.supplier_code
                )

    def action_activate(self):
        _require(self.env, "Activating a supplier", GROUP_APPROVER)
        for rec in self:
            if rec.state == "activated":
                raise UserError("Activation %s is already done." % rec.name)
            _not_by(
                self.env,
                rec.create_uid | rec.supplier_id.buyer_id.user_id,
                "prepared this activation or buy from this supplier",
            )
            problems = rec._blockers()
            if problems:
                raise UserError("Activation blocked: %s" % ", ".join(problems))
            rec._guarded().write(
                {
                    "state": "activated",
                    "activated_on": fields.Date.context_today(self),
                    "activated_by_id": self.env.uid,
                    "blocker": False,
                }
            )
            supplier = rec.supplier_id.sudo()
            supplier._a06_set_status("active", "activation %s" % rec.name)
            if not supplier.onboarded_on:
                supplier.write({"onboarded_on": fields.Date.context_today(self)})


class FixSupplierRequalification(models.Model):
    _name = "fix.supplier.requalification"
    _description = "Supplier Re-Qualification"
    _inherit = ["fix.guarded.mixin"]
    _order = "due_on desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    due_on = fields.Date(required=True)
    completed_on = fields.Date(readonly=True, copy=False)
    outcome = fields.Selection([("pass", "Pass"), ("conditional", "Conditional"), ("fail", "Fail")])
    state = fields.Selection(
        [("due", "Due"), ("scheduled", "Scheduled"), ("done", "Done")],
        required=True,
        default="due",
    )
    notes = fields.Char()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "completed_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state == "done" for r in self):
            locked |= {"outcome", "supplier_id", "due_on"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.requalification")
                    or "SREQ/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if (
            {"outcome", "supplier_id", "due_on"} & set(vals)
            and not self._fix_guard_has_token()
            and any(r.state == "done" for r in self)
        ):
            raise UserError("A completed re-qualification is final.")
        return super().write(vals)

    def action_complete(self):
        _require(self.env, "Completing a re-qualification", GROUP_STEWARD, GROUP_APPROVER)
        for rec in self:
            if rec.state == "done":
                raise UserError("This re-qualification is already complete")
            if not rec.outcome:
                raise UserError("Record the outcome before completing the re-qualification")
            rec._guarded().write({"state": "done", "completed_on": fields.Date.context_today(self)})
            if rec.outcome == "fail":
                rec.supplier_id.sudo()._a06_auto_suspend("re-qualification %s failed" % rec.name)


class FixSupplierScorecard(models.Model):
    """The supplier scorecard, computed from M16 purchase-order and receipt
    facts for one month and frozen once published (BRU-SRM2-08/09)."""

    _name = "fix.supplier.performance"
    _description = "Supplier Scorecard"
    _inherit = ["fix.guarded.mixin"]
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    period = fields.Char(required=True, help="YYYY-MM")
    quality_score = fields.Float(string="Quality (0–100)", default=0.0, readonly=True)
    delivery_score = fields.Float(string="Delivery (0–100)", default=0.0, readonly=True)
    cost_score = fields.Float(string="Cost (0–100)", default=0.0, readonly=True)
    responsiveness_score = fields.Float(string="Responsiveness (0–100)", default=0.0, readonly=True)
    quality_measured = fields.Boolean(default=True, readonly=True)
    delivery_measured = fields.Boolean(default=True, readonly=True)
    cost_measured = fields.Boolean(default=True, readonly=True)
    responsiveness_measured = fields.Boolean(default=True, readonly=True)
    total_score = fields.Float(compute="_compute_total", store=True, string="Total")
    grade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")],
        compute="_compute_total",
        store=True,
        string="Grade",
    )
    basis_note = fields.Text(string="Basis", readonly=True, copy=False)
    computed_at = fields.Datetime(readonly=True, copy=False)
    computed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    published_at = fields.Datetime(readonly=True, copy=False)
    published_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    reviewed_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published")], required=True, default="draft"
    )

    CARD_GUARDED = {
        "quality_score",
        "delivery_score",
        "cost_score",
        "responsiveness_score",
        "quality_measured",
        "delivery_measured",
        "cost_measured",
        "responsiveness_measured",
        "total_score",
        "grade",
        "basis_note",
        "computed_at",
        "computed_by_id",
        "published_at",
        "published_by_id",
        "state",
    }

    _scores_range = models.Constraint(
        "CHECK (quality_score >= 0 AND quality_score <= 100 AND delivery_score >= 0 "
        "AND delivery_score <= 100 AND cost_score >= 0 AND cost_score <= 100 "
        "AND responsiveness_score >= 0 AND responsiveness_score <= 100)",
        "Scorecard components are 0–100 values",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.CARD_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state == "published" or r.computed_at for r in self):
            locked |= {"supplier_id", "period", "reviewed_on"}
        return locked

    WEIGHTS = (
        ("quality", 0.35),
        ("delivery", 0.30),
        ("cost", 0.20),
        ("responsiveness", 0.15),
    )

    @api.depends(
        "quality_score",
        "delivery_score",
        "cost_score",
        "responsiveness_score",
        "quality_measured",
        "delivery_measured",
        "cost_measured",
        "responsiveness_measured",
    )
    def _compute_total(self):
        for rec in self:
            weight = sum(w for key, w in self.WEIGHTS if rec["%s_measured" % key])
            total = (
                sum(
                    rec["%s_score" % key] * w for key, w in self.WEIGHTS if rec["%s_measured" % key]
                )
                / weight
                if weight
                else 0.0
            )
            rec.total_score = round(total, 1)
            rec.grade = (
                "a" if total >= 85 else ("b" if total >= 70 else ("c" if total >= 55 else "d"))
            )

    @api.constrains("supplier_id", "period")
    def _check_one_per_period(self):
        for rec in self:
            if (
                not self.env["fix.supplier.performance"]
                .sudo()
                .search_count(
                    [
                        ("supplier_id", "=", rec.supplier_id.id),
                        ("period", "=", rec.period),
                        ("id", "!=", rec.id),
                    ]
                )
            ):
                continue
            raise ValidationError(
                "Supplier %s already has a scorecard for %s."
                % (rec.supplier_id.supplier_code, rec.period)
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.performance") or "SPERF/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_has_token():
            if any(r.state == "published" for r in self) and vals:
                raise UserError("A published scorecard is final (BRU-SRM2-09).")
            fixed = {"supplier_id", "period"} & set(vals)
            if fixed and any(r.computed_at for r in self):
                raise UserError("Recompute rather than re-point a computed scorecard.")
        return super().write(vals)

    def unlink(self):
        if any(r.state == "published" for r in self):
            raise UserError("A published scorecard is final and cannot be deleted.")
        return super().unlink()

    # ---- computation from M16 facts ---------------------------------------
    def _a06_period_bounds(self):
        self.ensure_one()
        try:
            year, month = (int(x) for x in (self.period or "").split("-"))
            start = date(year, month, 1)
        except (TypeError, ValueError) as exc:
            raise UserError("Period %r is not YYYY-MM." % self.period) from exc
        return start, start + relativedelta(months=1) - timedelta(days=1)

    def _a06_measure(self):
        """{component: (score or None, basis text)} for this supplier/month."""
        self.ensure_one()
        start, end = self._a06_period_bounds()
        partner = self.supplier_id.partner_id.commercial_partner_id
        Order = self.env["fix.purchase.order"].sudo()
        orders = Order.search(
            [
                ("vendor_id", "child_of", partner.id),
                ("company_id", "=", self.supplier_id.company_id.id),
            ]
        )
        RLine = self.env["fix.purchase.receipt.line"].sudo()
        rlines = RLine.search(
            [
                ("receipt_id.purchase_order_id", "in", orders.ids),
                ("receipt_id.state", "=", "posted"),
                ("receipt_id.received_on", ">=", start),
                ("receipt_id.received_on", "<=", end),
            ]
        )
        out = {}
        judged = rlines.filtered(
            lambda r: r.inspection_state in ("passed", "partial", "failed", "not_required")
        )
        received = sum(judged.mapped("qty_received"))
        if received:
            accepted = sum(judged.mapped("qty_accepted"))
            out["quality"] = (
                round(100.0 * accepted / received, 1),
                "%.2f accepted of %.2f received (%d receipt lines)"
                % (accepted, received, len(judged)),
            )
        receipts = rlines.mapped("receipt_id")
        dated = [
            (r, r.purchase_order_id.vendor_confirmed_date or r.purchase_order_id.promised_date)
            for r in receipts
        ]
        dated = [(r, d) for r, d in dated if d]
        if dated:
            on_time = sum(1 for r, d in dated if r.received_on <= d)
            out["delivery"] = (
                round(100.0 * on_time / len(dated), 1),
                "%d of %d receipts on or before the confirmed date" % (on_time, len(dated)),
            )
        sla = _param(self.env, PARAM_ACK_SLA, 2)
        start_dt = fields.Datetime.to_datetime(start)
        end_dt = fields.Datetime.to_datetime(end) + timedelta(days=1)
        sent = orders.filtered(lambda o: o.sent_at and start_dt <= o.sent_at < end_dt)
        if sent:
            quick = sent.filtered(
                lambda o: o.acknowledged_at and o.acknowledged_at - o.sent_at <= timedelta(days=sla)
            )
            out["responsiveness"] = (
                round(100.0 * len(quick) / len(sent), 1),
                "%d of %d POs acknowledged within %g day(s)" % (len(quick), len(sent), sla),
            )
        issued = orders.filtered(
            lambda o: (
                o.state in ("sent", "acknowledged", "partially_received", "received", "closed")
            )
        )
        compared = held = 0
        for line in issued.mapped("line_ids"):
            when = line.order_id.date_order
            if not when or not (start_dt <= when < end_dt):
                continue
            prev = (
                self.env["fix.purchase.order.line"]
                .sudo()
                .search(
                    [
                        ("id", "!=", line.id),
                        ("product_id", "=", line.product_id.id),
                        ("order_id", "in", issued.ids),
                        ("order_id.date_order", "<", when),
                    ],
                    order="id desc",
                    limit=1,
                )
            )
            if prev:
                compared += 1
                held += 1 if line.unit_price <= prev.unit_price + 0.005 else 0
        if compared:
            out["cost"] = (
                round(100.0 * held / compared, 1),
                "%d of %d PO lines at or below the previous price" % (held, compared),
            )
        return out

    def action_compute(self):
        _require(self.env, "Computing a scorecard", GROUP_STEWARD)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Scorecard %s is published." % rec.name)
            measured = rec._a06_measure()
            if not measured:
                raise UserError(
                    "No purchase-order or receipt facts for %s in %s: a scorecard is computed "
                    "from them, never typed." % (rec.supplier_id.display_name, rec.period)
                )
            vals = {
                "computed_at": fields.Datetime.now(),
                "computed_by_id": self.env.uid,
                "basis_note": "\n".join(
                    "%s: %s" % (key, measured[key][1])
                    if key in measured
                    else "%s: no data (excluded)" % key
                    for key, _w in self.WEIGHTS
                ),
            }
            for key, _w in self.WEIGHTS:
                vals["%s_score" % key] = measured[key][0] if key in measured else 0.0
                vals["%s_measured" % key] = key in measured
            rec._guarded().write(vals)
        return True

    @api.model
    def consume_supplier_fact(self, event):
        """Event consumer (M16-12, registered in data/fix_supplier_consumers.xml):
        a goods receipt or a PO acknowledgement refreshes the vendor's draft
        scorecard for that month, creating it if needed. Idempotent: the card
        is recomputed from the period's facts, never incremented, and a
        published card is never touched."""
        payload = event.get("payload") or {}
        partner = self.env["res.partner"].browse(int(payload.get("vendor_id") or 0)).exists()
        supplier = self.env["fix.supplier"]._for_partner(partner)
        if not supplier:
            return False
        day = None
        if payload.get("received_on"):
            day = fields.Date.to_date(payload["received_on"])
        elif event.get("aggregate") == "fix.purchase.order":
            order = self.env["fix.purchase.order"].sudo().browse(event.get("aggregate_id") or 0)
            order = order.exists()
            if order and order.sent_at:
                day = order.sent_at.date()
        day = day or fields.Date.context_today(self)
        period = day.strftime("%Y-%m")
        Card = self.sudo()
        card = Card.search([("supplier_id", "=", supplier.id), ("period", "=", period)], limit=1)
        if card.state == "published":
            return False
        if not card:
            card = Card.create({"supplier_id": supplier.id, "period": period})
        if card._a06_measure():
            card.action_compute()
        return card

    def action_publish(self):
        _require(self.env, "Publishing a scorecard", GROUP_STEWARD)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Scorecard %s is already published." % rec.name)
            if not rec.computed_at:
                raise UserError(
                    "Compute scorecard %s from the period's PO and receipt facts before "
                    "publishing it." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "published",
                    "published_at": fields.Datetime.now(),
                    "published_by_id": self.env.uid,
                }
            )
            rec._a06_auto_car()
        return True

    def _a06_auto_car(self):
        """BRU-SRM2-10: the lowest band two periods running opens a CAR."""
        self.ensure_one()
        if self.grade != "d":
            return False
        previous = self.sudo().search(
            [
                ("supplier_id", "=", self.supplier_id.id),
                ("state", "=", "published"),
                ("period", "<", self.period),
            ],
            order="period desc",
            limit=1,
        )
        if previous.grade != "d":
            return False
        days = int(_param(self.env, PARAM_CAR_DAYS, 30))
        car = (
            self.env["fix.supplier.car"]
            .sudo()
            .create(
                {
                    "supplier_id": self.supplier_id.id,
                    "issue": "Two consecutive D-grade scorecards (%s, %s)"
                    % (previous.period, self.period),
                    "severity": "major",
                    "due_date": fields.Date.context_today(self) + timedelta(days=days),
                }
            )
        )
        # supplier.car.raised is published by the CAR's own create (A10 S6):
        # one event per CAR, whatever raised it.
        return car


class FixSupplierCar(models.Model):
    _name = "fix.supplier.car"
    _description = "Corrective Action Request"
    _inherit = ["fix.guarded.mixin"]
    _order = "due_date desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    issue = fields.Char(required=True)
    root_cause = fields.Text()
    action_plan = fields.Text()
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")],
        required=True,
        default="major",
    )
    raised_on = fields.Date(required=True, default=fields.Date.context_today)
    due_date = fields.Date(required=True)
    closed_on = fields.Date(readonly=True, copy=False)
    closed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    escalated_on = fields.Date(readonly=True, copy=False)
    state = fields.Selection(
        [("open", "Open"), ("actioned", "Actioned"), ("closed", "Closed")],
        required=True,
        default="open",
    )
    is_overdue = fields.Boolean(compute="_compute_overdue", search="_search_overdue")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "closed_on",
            "closed_by_id",
            "escalated_on",
        }

    @api.depends("due_date", "state")
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_overdue = bool(rec.due_date and rec.state != "closed" and rec.due_date < today)

    def _search_overdue(self, operator, value):
        today = fields.Date.context_today(self)
        overdue = ["&", ("state", "!=", "closed"), ("due_date", "<", today)]
        return overdue if _bool_positive(operator, value) else ["!", *overdue]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.car") or "SCAR/New"
                )
        recs = super().create(vals_list)
        # A10 S6 (M23-12, the M42 hand-off): every CAR announces itself with
        # what it is — the QMS consumer in cd_qms_process raises the NCR for
        # the majors. The vendor portal does not depend on the governance
        # stack; the hand-off is this event, nothing else.
        for rec in recs:
            publish(
                self.env,
                "supplier.car.raised",
                "fix.supplier.car",
                rec.id,
                {
                    "car": rec.name,
                    "supplier_id": rec.supplier_id.id,
                    "supplier": rec.supplier_id.name or "",
                    "issue": rec.issue or "",
                    "severity": rec.severity or "",
                    "due": str(rec.due_date or ""),
                },
                metadata={"module": "cd_vendor_portal", "reason": "A10 S6 CAR -> NCR hand-off"},
            )
        return recs

    def action_action(self):
        _require(self.env, "Marking a CAR actioned", GROUP_STEWARD)
        for rec in self:
            if rec.state != "open":
                raise UserError("Mark an open CAR actioned")
            if not rec.action_plan:
                raise UserError("Record the action plan before marking it actioned")
            rec._guarded().write({"state": "actioned"})

    def action_close(self):
        """Verification and closure by someone other than the raiser.

        A10 S6 (M23-12): a MAJOR/CRITICAL CAR closes on its root cause —
        the audit closed a CRITICAL CAR with neither a root cause nor an
        NCR anywhere in the QMS."""
        _require(self.env, "Closing a CAR", GROUP_STEWARD, GROUP_APPROVER)
        for rec in self:
            if rec.state != "actioned":
                raise UserError("Close an actioned CAR")
            _not_by(self.env, rec.create_uid, "raised this CAR")
            if rec.severity in ("major", "critical") and not (rec.root_cause or "").strip():
                raise UserError(
                    "A %s CAR closes on its root cause — state what went wrong "
                    "before closing %s (A10 S6)." % (rec.severity.upper(), rec.name)
                )
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_on": fields.Date.context_today(self),
                    "closed_by_id": self.env.uid,
                }
            )


class FixSupplierReview(models.Model):
    _name = "fix.supplier.review"
    _description = "Supplier Review"
    _inherit = ["fix.guarded.mixin"]
    _order = "review_date desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    review_type = fields.Selection(
        [("quarterly", "Quarterly"), ("annual", "Annual")],
        required=True,
        default="quarterly",
    )
    review_date = fields.Date(required=True, default=fields.Date.context_today)
    attendees = fields.Char()
    outcomes = fields.Text()
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("done", "Done")], required=True, default="scheduled"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.review") or "SRVW/New"
                )
        return super().create(vals_list)

    def action_complete(self):
        _require(self.env, "Completing a supplier review", GROUP_STEWARD)
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("Complete a scheduled review")
            rec._guarded().write({"state": "done"})


class FixSupplierRisk(models.Model):
    _name = "fix.supplier.risk"
    _description = "Supplier Risk Assessment"
    _inherit = ["fix.guarded.mixin"]
    _order = "assessed_on desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    risk_type = fields.Selection(
        [
            ("financial", "Financial"),
            ("operational", "Operational"),
            ("geographic", "Geographic"),
            ("compliance", "Compliance"),
            ("quality", "Quality"),
        ],
        required=True,
        default="quality",
    )
    likelihood = fields.Integer(default=3)
    impact = fields.Integer(default=3)
    risk_score = fields.Integer(compute="_compute_score", store=True)
    band = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        compute="_compute_score",
        store=True,
    )
    mitigation = fields.Text()
    assessed_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("open", "Open"), ("mitigated", "Mitigated")], required=True, default="open"
    )

    _factors_range = models.Constraint(
        "CHECK (likelihood >= 1 AND likelihood <= 5 AND impact >= 1 AND impact <= 5)",
        "Likelihood and impact are 1–5",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "risk_score", "band"}

    @api.depends("likelihood", "impact")
    def _compute_score(self):
        for rec in self:
            score = (rec.likelihood or 0) * (rec.impact or 0)
            rec.risk_score = score
            rec.band = (
                "critical"
                if score >= 20
                else ("high" if score >= 12 else ("medium" if score >= 6 else "low"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.risk") or "SRISK/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if (
            {"likelihood", "impact", "supplier_id"} & set(vals)
            and not self._fix_guard_has_token()
            and any(r.state == "mitigated" for r in self)
        ):
            raise UserError("A mitigated risk is closed; assess a new one.")
        return super().write(vals)

    def action_mitigate(self):
        _require(self.env, "Closing a supplier risk", GROUP_STEWARD, GROUP_APPROVER)
        for rec in self:
            if rec.state != "open":
                raise UserError("Risk %s is already mitigated." % rec.name)
            if not rec.mitigation:
                raise UserError("Record the mitigation before closing the risk")
            rec._guarded().write({"state": "mitigated"})


class FixSupplierScreening(models.Model):
    _name = "fix.supplier.screening"
    _description = "Supplier Compliance Screening"
    _inherit = ["fix.guarded.mixin"]
    _order = "screened_on desc, id desc"

    name = fields.Char(required=True, default="New")
    supplier_id = fields.Many2one(
        "fix.supplier", string="Supplier", required=True, ondelete="cascade", index=True
    )
    screening_type = fields.Selection(
        [
            ("sanctions", "Sanctions List"),
            ("coi", "Conflict of Interest"),
            ("abac", "Anti-Bribery / ABAC"),
            ("pep", "PEP Check"),
        ],
        required=True,
        default="sanctions",
    )
    result = fields.Selection(
        [("clear", "Clear"), ("hit", "Hit"), ("pending", "Pending")],
        required=True,
        default="pending",
    )
    screened_on = fields.Date(required=True, default=fields.Date.context_today)
    reference = fields.Char()
    state = fields.Selection(
        [("pending", "Pending"), ("cleared", "Cleared"), ("flagged", "Flagged")],
        required=True,
        default="pending",
    )
    cleared_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    cleared_on = fields.Date(readonly=True, copy=False)
    clearance_reason = fields.Char(readonly=True, copy=False)
    notes = fields.Char()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "cleared_by_id",
            "cleared_on",
            "clearance_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.result == "hit" or r.state != "pending" for r in self):
            locked |= {"result", "screening_type", "supplier_id", "screened_on"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.supplier.screening") or "SSCRN/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        fixed = {"result", "screening_type", "supplier_id", "screened_on"} & set(vals)
        if fixed and not self._fix_guard_has_token():
            for rec in self:
                if (rec.result == "hit" or rec.state != "pending") and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in fixed
                ):
                    raise UserError(
                        "Screening %s is a recorded %s: it is cleared only by an approver's "
                        "clearance, never by rewriting it." % (rec.name, rec.result)
                    )
        return super().write(vals)

    def action_clear(self):
        _require(self.env, "Clearing a screening", GROUP_STEWARD, GROUP_APPROVER)
        for rec in self:
            if rec.result == "hit":
                raise UserError("A screening hit cannot be cleared")
            if rec.result != "clear":
                raise UserError("Record a clear result before clearing the screening")
            if rec.state != "pending":
                raise UserError("Screening %s is %s." % (rec.name, rec.state))
            rec._guarded().write(
                {
                    "state": "cleared",
                    "cleared_by_id": self.env.uid,
                    "cleared_on": fields.Date.context_today(self),
                }
            )

    def action_flag(self):
        _require(self.env, "Flagging a screening", GROUP_STEWARD, GROUP_APPROVER)
        for rec in self:
            if rec.state != "pending":
                raise UserError("Screening %s is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "flagged"})
            if rec.result == "hit":
                rec.supplier_id.sudo()._a06_auto_suspend(
                    "%s screening hit %s flagged" % (rec.screening_type, rec.name)
                )

    def action_clear_hit(self, reason=None):
        """A false-positive hit is cleared by a Supplier Approver other than the
        person who recorded it, with the reason; the result stays 'hit'."""
        _require(self.env, "Clearing a screening hit", GROUP_APPROVER)
        for rec in self:
            if rec.result != "hit" or rec.state == "cleared":
                raise UserError("Screening %s carries no open hit." % rec.name)
            _not_by(self.env, rec.create_uid, "recorded this screening")
            if len((reason or "").strip()) < 10:
                raise UserError(
                    "State why hit %s is a false positive (evidence reference)." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "cleared",
                    "cleared_by_id": self.env.uid,
                    "cleared_on": fields.Date.context_today(self),
                    "clearance_reason": reason.strip(),
                }
            )
            publish(
                self.env,
                "supplier.screening.cleared",
                "fix.supplier.screening",
                rec.id,
                {"supplier_id": rec.supplier_id.id, "type": rec.screening_type, "by": self.env.uid},
            )
