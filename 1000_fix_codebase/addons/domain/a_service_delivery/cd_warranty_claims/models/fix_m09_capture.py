# M09 capture audit, second pass (2026-11-18): the records the M09 sub-module
# pages had no way to capture, because the records did not exist.
#
# The 13 Nov pass gave six of the twelve pages a "+ New" and left the rest as
# workflow steps on existing claims. Read against the specification (§5 FRs,
# §9 rules, §10.1 owned entities) eight pages still could not record what the
# spec says a person records there:
#
#   page 1/4  fix.warranty.void           FR-WTY-010, BRU-WTY-17 (H): a void
#                                         condition is evidenced before it
#                                         refuses cover. "Void Warranty" took a
#                                         typed reason and nothing else.
#   page 5    fix.protection.policy       FR-WTY-015..024, BRU-WTY-11/15: the
#             fix.protection.inspection   sold protection instance, its pre-sale
#             fix.protection.reserve      inspection and its reserve ledger. A
#                                         sold plan existed nowhere: the
#                                         "Protection Policy" chip opened a
#                                         warranty register row.
#   page 6    fix.protection.claim        FR-WTY-027..036, BRU-WTY-12/13/14/21:
#                                         a customer's claim on a protection plan
#                                         (inbound). No record; the page re-listed
#                                         brand claims.
#   page 8    fix.brand.claim.rule        FR-WTY-040, T-03, BRU-WTY-04/19: each
#                                         brand's rule set as data. The evidence
#                                         list was fixed in code and the "Brand
#                                         Rules & Formats" screen listed products.
#   page 9    fix.warranty.claim.info.request  FR-WTY-047: the brand's request
#                                         for information. Appeals gain the
#                                         additional evidence FR-WTY-049 names.
#   page 10   fix.brand.remittance(.line) FR-WTY-053: one brand payment settles
#             fix.brand.reconciliation    many claims; FR-WTY-054 signed period
#             fix.claim.writeoff          statement; FR-WTY-055 / BRU-WTY-07 (H)
#             fix.defective.return        write-off with SoD; FR-WTY-057 /
#                                         BRU-WTY-19 (H) defective-part return.
#   page 12   fix.warranty.fraud.review   FR-WTY-051, BRU-WTY-21 (A): a flagged
#                                         claim is investigated before it is
#                                         settled; a confirmed finding blocks it.
#
# Every money or verdict step is a method that checks its role and keeps the
# person who prepared a record from deciding it (segregation of duties).
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_warranty_claims import (
    CLERK_GROUP,
    EVIDENCE_REQUIREMENTS,
    OFFICER_GROUP,
    OPEN_STATES,
    RECOVERY_STATES,
    _assert_role,
)

WARRANTY_OFFICER_GROUP = "cd_device_registry.group_warranty_officer"
FINANCE_MANAGER_GROUP = "account.group_account_manager"
# A score at or above this needs a cleared fraud review before settlement
# (BRU-WTY-21): advisory, never an automatic rejection (T-13).
FRAUD_REVIEW_THRESHOLD = 50
VOID_CONTEXT = "fix_void_record_id"


def _today(env):
    return fields.Date.context_today(env["res.users"].with_context(tz="Asia/Dhaka"))


def _immutable(records, what):
    if not records.env.su:
        raise UserError("%s is a record of what happened; it cannot be edited." % what)


def _not_same(env, users, what):
    """Segregation of duties: the acting user is none of ``users``."""
    if env.su:
        return
    if env.user in users:
        raise AccessError(
            "Segregation of duties: %s cannot be done by %s, who prepared it."
            % (what, env.user.name)
        )


def _refuse_frozen(records, vals, frozen, message):
    """A record past its working state is a record of what happened: only
    its workflow (the guard token, or superuser code) still writes it."""
    if (
        not records._fix_guard_open()
        and records.filtered(frozen)
        and set(vals) - {"message_main_attachment_id"}
    ):
        raise UserError(message)


def _seq(env, code, prefix):
    return env["ir.sequence"].sudo().next_by_code(code) or "%s/%s" % (prefix, fields.Date.today())


def _upload_document(env, vals, file_field, name_field, fallback, res_model, doc_type="other"):
    """A file a person uploaded on a workspace form becomes a governed
    fix.document (created as the caller, so its ACL applies). Returns the
    document or an empty recordset."""
    data = vals.pop(file_field, None)
    name = (vals.pop(name_field, None) or "").strip() or fallback
    if not data:
        return env["fix.document"]
    return env["fix.document"].create(
        {
            "name": name,
            "upload_file": data,
            "upload_filename": name,
            "document_type": doc_type,
            "company_id": env.company.id,
            "res_model": res_model,
        }
    )


def _bind(doc, record):
    """File an unfiled upload against the record it proves."""
    if doc and not doc.sudo().res_id:
        doc.sudo().write({"res_model": record._name, "res_id": record.id})


# ==========================================================================
# pages 1 and 4: void conditions (FR-WTY-010, BRU-WTY-17)
# ==========================================================================
VOID_CONDITIONS = [
    ("unauthorised_repair", "Unauthorised repair"),
    ("physical_damage", "Physical damage"),
    ("liquid_damage", "Liquid damage"),
    ("tampering", "Tampering"),
    ("seal_breach", "Seal / sticker breached"),
    ("other", "Other (explain)"),
]


class FixWarrantyVoid(models.Model):
    """A void condition found on a device, with its evidence. Declared by
    whoever found it; applied by a Warranty Officer who did not declare it,
    and only then does the warranty become void (BRU-WTY-17)."""

    _name = "fix.warranty.void"
    _description = "Warranty Void Condition"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    company_id = fields.Many2one("res.company", required=True, default=lambda s: s.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    warranty_id = fields.Many2one(
        "fix.warranty", string="Warranty", required=True, index=True, ondelete="restrict"
    )
    device_id = fields.Many2one(related="warranty_id.device_id", string="Device", store=True)
    condition = fields.Selection(VOID_CONDITIONS, required=True)
    description = fields.Text(string="What Was Found", required=True)
    evidence_document_id = fields.Many2one(
        "fix.document", string="Evidence Document", ondelete="restrict"
    )
    evidence_file = fields.Binary(string="Upload Evidence", store=False)
    evidence_filename = fields.Char(string="Evidence File Name", store=False)
    state = fields.Selection(
        [
            ("declared", "Declared"),
            ("applied", "Applied - Warranty Void"),
            ("rejected", "Rejected"),
        ],
        default="declared",
        required=True,
        tracking=True,
    )
    declared_by_id = fields.Many2one(
        "res.users", string="Declared By", readonly=True, default=lambda s: s.env.user
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(string="Decided At", readonly=True)
    decision_note = fields.Text(string="Decision Note", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "declared_by_id",
            "decided_by_id",
            "decided_at",
            "decision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "declared":
            locked |= {"warranty_id", "condition", "description", "evidence_document_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        docs = []
        for vals in vals_list:
            _assert_role(self.env, CLERK_GROUP, "Declaring a void condition")
            warranty = self.env["fix.warranty"].browse(vals.get("warranty_id")).exists()
            if not warranty:
                raise ValidationError("Choose the warranty the condition voids.")
            if warranty.status == "voided":
                raise ValidationError(
                    "Warranty on %s is already void." % warranty.device_id.display_name
                )
            docs.append(
                _upload_document(
                    self.env,
                    vals,
                    "evidence_file",
                    "evidence_filename",
                    "Void evidence",
                    self._name,
                    "custody_photo",
                )
            )
            vals["name"] = _seq(self.env, "fix.warranty.void", "WVD")
            vals.setdefault("operating_unit_id", warranty.operating_unit_id.id or False)
            vals.setdefault("company_id", warranty.company_id.id or self.env.company.id)
        records = super().create(vals_list)
        for rec, doc in zip(records, docs, strict=True):
            if doc:
                rec.sudo().write({"evidence_document_id": doc.id})
            _bind(rec.evidence_document_id, rec)
        return records

    def write(self, vals):
        doc = _upload_document(
            self.env,
            vals,
            "evidence_file",
            "evidence_filename",
            "Void evidence",
            self._name,
            "custody_photo",
        )
        if doc:
            vals["evidence_document_id"] = doc.id
        _refuse_frozen(
            self,
            vals,
            lambda r: r.state != "declared",
            "A decided void condition is closed for edits.",
        )
        res = super().write(vals)
        if doc:
            for rec in self:
                _bind(doc, rec)
        return res

    def _decide(self):
        for rec in self:
            if rec.state != "declared":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            if not self.env.su and not self.env.user.has_group(WARRANTY_OFFICER_GROUP):
                raise AccessError("Applying a void condition needs the Warranty Officer role.")
            _not_same(self.env, rec.declared_by_id | rec.create_uid, "deciding void %s" % rec.name)

    def action_apply(self):
        """Void the warranty, on this evidence (BRU-WTY-17)."""
        self._decide()
        for rec in self:
            if not rec.evidence_document_id:
                raise UserError(
                    "%s has no evidence. A void condition must be evidenced before it "
                    "refuses cover (BRU-WTY-17): upload the photograph or report." % rec.name
                )
            label = dict(VOID_CONDITIONS)[rec.condition]
            rec.warranty_id.with_context(**{VOID_CONTEXT: rec.id}).action_void(
                "%s: %s (void condition %s)" % (label, rec.description.strip(), rec.name)
            )
            rec._guarded().write(
                {
                    "state": "applied",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, note=None):
        self._decide()
        if not (note or "").strip():
            raise UserError("Say why the condition does not void the warranty.")
        for rec in self:
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "decision_note": note.strip(),
                }
            )
        return True


class FixWarrantyVoidGate(models.Model):
    _inherit = "fix.warranty"

    void_record_ids = fields.One2many("fix.warranty.void", "warranty_id", string="Void Conditions")

    def action_void(self, reason: str = ""):
        """BRU-WTY-17 (H): a warranty is voided only through an evidenced void
        condition, applied by a Warranty Officer who did not declare it. A
        typed reason alone used to void cover."""
        if not self.env.su and not self.env.context.get(VOID_CONTEXT):
            raise UserError(
                "A warranty is voided through an evidenced void condition (BRU-WTY-17): "
                "declare it with + Void Condition on the Warranty Register (photograph or "
                "report attached); a Warranty Officer who did not declare it applies it."
            )
        return super().action_void(reason)


# ==========================================================================
# page 5: protection policies, inspections and the reserve ledger
# ==========================================================================
class FixWarrantyProductProtection(models.Model):
    _inherit = "fix.warranty.product"

    inspection_required = fields.Boolean(
        string="Pre-sale Inspection Required",
        help="FR-WTY-017 / BRU-WTY-11: a policy is not activated without a passed inspection.",
    )
    max_device_age_months = fields.Integer(
        string="Max Device Age At Sale (months)",
        help="FR-WTY-016 eligibility: 0 = any age. Measured from the device's purchase date.",
    )
    reserve_rate = fields.Float(
        string="Reserve (% of premium)",
        help="FR-WTY-036 / BRU-WTY-15: the share of the premium held as the policy's reserve "
        "from the day it is issued. A business decision; no policy of a protection plan is "
        "activated until it is set.",
    )

    @api.constrains("max_device_age_months", "reserve_rate")
    def _check_protection_terms(self):
        for product in self:
            if product.max_device_age_months < 0:
                raise ValidationError("The device age limit cannot be negative.")
            if not 0 <= product.reserve_rate <= 100:
                raise ValidationError("The reserve is a percentage of the premium (0-100).")


POLICY_STATES = [
    ("sold", "Sold - Awaiting Activation"),
    ("active", "Active"),
    ("declined", "Declined"),
    ("exhausted", "Exhausted"),
    ("cancelled", "Cancelled"),
    ("expired", "Expired"),
]


class FixProtectionPolicy(models.Model):
    """A protection plan sold on one device (the policy instance of FR-WTY-018).
    Activation checks eligibility and the pre-sale inspection (BRU-WTY-11) and
    establishes the reserve (BRU-WTY-15)."""

    _name = "fix.protection.policy"
    _description = "Protection Policy"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Policy No.", readonly=True, copy=False, default="/")
    company_id = fields.Many2one("res.company", required=True, default=lambda s: s.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    product_id = fields.Many2one(
        "fix.warranty.product", string="Protection Product", required=True, ondelete="restrict"
    )
    partner_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    device_id = fields.Many2one("fix.device", string="Device", required=True, index=True)
    sale_ref = fields.Char(string="Sale Document (M36 / M38 / counter)")
    currency_id = fields.Many2one(related="product_id.currency_id", string="Currency")
    premium = fields.Monetary(string="Premium Paid", currency_field="currency_id", required=True)
    term_start = fields.Date(string="Cover Starts", required=True)
    term_end = fields.Date(string="Cover Ends", readonly=True)
    waiting_until = fields.Date(string="Waiting Period Until", readonly=True)
    excess = fields.Monetary(string="Customer Excess", currency_field="currency_id", readonly=True)
    claim_limit = fields.Monetary(
        string="Aggregate Limit", currency_field="currency_id", readonly=True
    )
    claimed_amount = fields.Monetary(
        string="Settled Claims", currency_field="currency_id", compute="_compute_limits"
    )
    remaining_limit = fields.Monetary(
        string="Remaining Limit", currency_field="currency_id", compute="_compute_limits"
    )
    reserve_balance = fields.Monetary(
        string="Reserve Balance", currency_field="currency_id", compute="_compute_limits"
    )
    inspection_required = fields.Boolean(related="product_id.inspection_required")
    inspection_ids = fields.One2many("fix.protection.inspection", "policy_id", string="Inspections")
    claim_ids = fields.One2many("fix.protection.claim", "policy_id", string="Claims")
    reserve_ids = fields.One2many("fix.protection.reserve", "policy_id", string="Reserve Ledger")
    state = fields.Selection(POLICY_STATES, default="sold", required=True, tracking=True)
    activated_by_id = fields.Many2one("res.users", string="Activated By", readonly=True)
    activated_at = fields.Datetime(string="Activated At", readonly=True)
    cancel_reason = fields.Text(string="Cancellation Reason", readonly=True)
    refund_amount = fields.Monetary(
        string="Refund Due",
        currency_field="currency_id",
        readonly=True,
        help="FR-WTY-022: pro-rata on the unused days; instructed to M20.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "term_end",
            "waiting_until",
            "excess",
            "claim_limit",
            "activated_by_id",
            "activated_at",
            "cancel_reason",
            "refund_amount",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "sold":
            locked |= {"product_id", "partner_id", "device_id", "premium", "term_start", "sale_ref"}
        return locked

    @api.depends(
        "claim_ids.state", "claim_ids.approved_amount", "reserve_ids.amount", "claim_limit"
    )
    def _compute_limits(self):
        for policy in self:
            settled = policy.claim_ids.filtered(lambda c: c.state == "settled")
            used = sum(settled.mapped("approved_amount"))
            policy.claimed_amount = used
            policy.remaining_limit = (
                max(policy.claim_limit - used, 0.0) if policy.claim_limit else 0.0
            )
            policy.reserve_balance = sum(policy.reserve_ids.mapped("amount"))

    def _terms(self, product, start):
        start = fields.Date.to_date(start)
        return {
            "term_end": start + relativedelta(months=product.duration_months) - timedelta(days=1),
            "waiting_until": start + timedelta(days=product.waiting_days or 0),
            "excess": product.excess_amount,
            "claim_limit": product.claim_limit,
        }

    @api.model_create_multi
    def create(self, vals_list):
        terms = []
        for vals in vals_list:
            _assert_role(self.env, CLERK_GROUP, "Selling a protection policy")
            product = self.env["fix.warranty.product"].browse(vals.get("product_id")).exists()
            device = self.env["fix.device"].browse(vals.get("device_id")).exists()
            if not product or not device or not vals.get("term_start"):
                raise ValidationError("A policy needs its product, device and cover start date.")
            if float(vals.get("premium") or 0.0) <= 0:
                raise ValidationError("A sold policy records the premium the customer paid.")
            terms.append(self._terms(product, vals["term_start"]))
            vals["name"] = _seq(self.env, "fix.protection.policy", "PPL")
            vals.setdefault("operating_unit_id", device.operating_unit_id.id or False)
        records = super().create(vals_list)
        for rec, term in zip(records, terms, strict=True):
            rec._guarded().write(term)
        return records

    def write(self, vals):
        res = super().write(vals)
        if {"product_id", "term_start"} & set(vals):
            for rec in self.filtered(lambda r: r.state == "sold"):
                rec._guarded().write(self._terms(rec.product_id, rec.term_start))
        return res

    def _eligibility_defects(self):
        self.ensure_one()
        defects = []
        product, device = self.product_id, self.device_id
        if not product.active:
            defects.append("product %s is no longer sold" % product.name)
        if product.max_device_age_months:
            bought = device.purchase_date
            if not bought:
                defects.append(
                    "%s limits device age to %d months and %s has no purchase date on record"
                    % (product.name, product.max_device_age_months, device.display_name)
                )
            elif bought + relativedelta(months=product.max_device_age_months) < self.term_start:
                defects.append(
                    "%s was bought on %s, older than the %d months %s allows (FR-WTY-016)"
                    % (device.display_name, bought, product.max_device_age_months, product.name)
                )
        if device.owner_id and device.owner_id != self.partner_id:
            defects.append(
                "%s belongs to %s, not to %s"
                % (device.display_name, device.owner_id.name, self.partner_id.name)
            )
        if product.product_type == "protection" and product.reserve_rate <= 0:
            defects.append(
                "%s declares no reserve rate: a protection plan holds a reserve from issue "
                "(BRU-WTY-15); the Warranty Officer sets it on the product" % product.name
            )
        if product.inspection_required:
            passed = self.inspection_ids.filtered(lambda i: i.outcome == "pass")
            if not passed:
                defects.append("%s needs a passed pre-sale inspection (BRU-WTY-11)" % product.name)
        overlap = self.search(
            [
                ("id", "!=", self.id),
                ("device_id", "=", device.id),
                ("product_id", "=", product.id),
                ("state", "=", "active"),
            ],
            limit=1,
        )
        if overlap:
            defects.append(
                "%s already holds active policy %s of this product"
                % (device.display_name, overlap.name)
            )
        return defects

    def action_activate(self):
        """FR-WTY-018: issue the cover. Eligibility and inspection first
        (BRU-WTY-11), then the reserve (BRU-WTY-15)."""
        for policy in self:
            _assert_role(self.env, CLERK_GROUP, "Activating a protection policy")
            if policy.state != "sold":
                raise UserError(
                    "Only a sold policy is activated (%s is %s)." % (policy.name, policy.state)
                )
            defects = policy._eligibility_defects()
            if defects:
                raise UserError("%s cannot be activated: %s." % (policy.name, "; ".join(defects)))
            policy._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                }
            )
            reserve = round(policy.premium * policy.product_id.reserve_rate / 100.0, 2)
            if reserve:
                policy._reserve("establish", reserve, "Reserve established at issue")
        return True

    def _reserve(self, movement, amount, reason, claim=None):
        self.ensure_one()
        return (
            self.env["fix.protection.reserve"]
            .sudo()
            .create(
                {
                    "policy_id": self.id,
                    "movement_type": movement,
                    "amount": amount,
                    "reason": reason,
                    "claim_id": claim.id if claim else False,
                }
            )
        )

    def _release_reserve(self, reason):
        for policy in self:
            balance = policy.reserve_balance
            if balance > 0.005:
                policy._reserve("release", -balance, reason)

    def action_cancel(self, reason=None):
        """FR-WTY-022: cancel on request or breach; the refund is pro-rata on
        the unused days and instructed to M20. A Claim Decision Officer."""
        if not (reason or "").strip():
            raise UserError("Give the reason the policy is cancelled.")
        today = _today(self.env)
        for policy in self:
            _assert_role(self.env, OFFICER_GROUP, "Cancelling a protection policy")
            if policy.state not in ("sold", "active"):
                raise UserError("%s is %s and cannot be cancelled." % (policy.name, policy.state))
            refund = policy.premium
            if policy.state == "active" and policy.term_end and policy.term_start:
                total = (policy.term_end - policy.term_start).days + 1
                unused = max((policy.term_end - max(today, policy.term_start)).days + 1, 0)
                refund = round(policy.premium * unused / total, 2) if total > 0 else 0.0
                if policy.claimed_amount:
                    refund = 0.0  # a policy that paid a claim refunds nothing
            policy._guarded().write(
                {"state": "cancelled", "cancel_reason": reason.strip(), "refund_amount": refund}
            )
            policy._release_reserve("Released on cancellation")
            policy.message_post(
                body="Cancelled: %s. Refund due %.2f (M20)." % (reason.strip(), refund)
            )
        return True

    @api.model
    def cron_expire_policies(self):
        """Policies past their term expire and release their reserve."""
        today = _today(self.env)
        for policy in self.sudo().search([("state", "=", "active"), ("term_end", "<", today)]):
            policy._guarded().write({"state": "expired"})
            policy._release_reserve("Released at expiry")
        return True


class FixProtectionInspection(models.Model):
    """FR-WTY-017: the device as seen before the plan is sold, photographed.
    A failed inspection declines the policy."""

    _name = "fix.protection.inspection"
    _description = "Protection Pre-sale Inspection"
    _inherit = ["mail.thread"]
    _order = "inspected_at desc, id desc"

    policy_id = fields.Many2one(
        "fix.protection.policy", string="Policy", required=True, ondelete="restrict"
    )
    device_id = fields.Many2one(related="policy_id.device_id", string="Device")
    inspected_at = fields.Datetime(
        string="Inspected At", readonly=True, default=fields.Datetime.now
    )
    inspector_id = fields.Many2one(
        "res.users", string="Inspected By", readonly=True, default=lambda s: s.env.user
    )
    condition_grade = fields.Selection(
        [
            ("a", "A - As new"),
            ("b", "B - Light wear"),
            ("c", "C - Visible damage"),
            ("d", "D - Faulty"),
        ],
        string="Condition Grade",
        required=True,
    )
    outcome = fields.Selection([("pass", "Pass"), ("fail", "Fail")], required=True)
    note = fields.Text(string="Findings")
    photo_document_id = fields.Many2one("fix.document", string="Photograph", ondelete="restrict")
    photo_file = fields.Binary(string="Upload Photograph", store=False)
    photo_filename = fields.Char(string="Photograph File Name", store=False)

    @api.model_create_multi
    def create(self, vals_list):
        docs = []
        for vals in vals_list:
            _assert_role(self.env, CLERK_GROUP, "Recording a pre-sale inspection")
            policy = self.env["fix.protection.policy"].browse(vals.get("policy_id")).exists()
            if not policy or policy.state != "sold":
                raise ValidationError(
                    "A pre-sale inspection is recorded on a sold policy awaiting activation."
                )
            if vals.get("outcome") == "fail" and not (vals.get("note") or "").strip():
                raise ValidationError("Write down what failed the inspection.")
            doc = _upload_document(
                self.env,
                vals,
                "photo_file",
                "photo_filename",
                "Inspection photo",
                self._name,
                "custody_photo",
            )
            if not doc and not vals.get("photo_document_id"):
                raise ValidationError("A pre-sale inspection carries its photograph (FR-WTY-017).")
            docs.append(doc)
        records = super().create(vals_list)
        for rec, doc in zip(records, docs, strict=True):
            if doc:
                rec.sudo().write({"photo_document_id": doc.id})
            _bind(rec.photo_document_id, rec)
            if rec.outcome == "fail":
                rec.policy_id._guarded().write({"state": "declined"})
                rec.policy_id.message_post(
                    body="Declined: pre-sale inspection failed (%s)." % rec.note
                )
        return records

    def write(self, vals):
        _immutable(self, "A pre-sale inspection")
        return super().write(vals)

    def unlink(self):
        _immutable(self, "A pre-sale inspection")
        return super().unlink()


class FixProtectionReserve(models.Model):
    """T-09: the reserve is an append-only movement ledger; the balance is
    derived, never edited. Written by the policy and claim transitions only."""

    _name = "fix.protection.reserve"
    _description = "Protection Reserve Movement"
    _order = "id desc"

    policy_id = fields.Many2one(
        "fix.protection.policy", string="Policy", required=True, index=True, ondelete="restrict"
    )
    product_id = fields.Many2one(related="policy_id.product_id", string="Product", store=True)
    currency_id = fields.Many2one(related="policy_id.currency_id")
    movement_type = fields.Selection(
        [("establish", "Establish"), ("adjust", "Adjust"), ("release", "Release")], required=True
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    reason = fields.Char(required=True)
    claim_id = fields.Many2one("fix.protection.claim", string="Claim")
    at = fields.Datetime(string="At", default=fields.Datetime.now, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError(
                "Reserve movements are written by the policy and claim workflow only."
            )
        return super().create(vals_list)

    def write(self, vals):
        raise UserError("The reserve ledger is append-only (T-09).")

    def unlink(self):
        raise UserError("The reserve ledger is append-only (T-09).")


# ==========================================================================
# page 6: protection claims (inbound) - FR-WTY-027..036
# ==========================================================================
PCLAIM_STATES = [
    ("draft", "Received"),
    ("assessed", "Assessed"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("settled", "Settled"),
]


class FixProtectionClaim(models.Model):
    """A customer's claim on a protection policy: intake, assessment, a
    decision by a Claim Decision Officer, the excess, then fulfilment."""

    _name = "fix.protection.claim"
    _description = "Protection Claim"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Claim No.", readonly=True, copy=False, default="/")
    company_id = fields.Many2one("res.company", required=True, default=lambda s: s.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    policy_id = fields.Many2one(
        "fix.protection.policy", string="Policy", required=True, index=True, ondelete="restrict"
    )
    partner_id = fields.Many2one(related="policy_id.partner_id", string="Customer", store=True)
    device_id = fields.Many2one(related="policy_id.device_id", string="Device", store=True)
    currency_id = fields.Many2one(related="policy_id.currency_id")
    channel = fields.Selection(
        [
            ("branch", "Branch"),
            ("portal", "Portal"),
            ("app", "App"),
            ("contact_centre", "Contact Centre"),
            ("field", "Field"),
        ],
        default="branch",
        required=True,
    )
    incident_date = fields.Date(string="Incident Date", required=True)
    cause = fields.Selection(
        [
            ("accidental_drop", "Accidental drop / impact"),
            ("liquid", "Liquid contact"),
            ("screen", "Screen breakage"),
            ("electrical", "Electrical / power surge"),
            ("mechanical", "Mechanical breakdown"),
            ("other", "Other (explain)"),
        ],
        required=True,
    )
    description = fields.Text(string="Circumstances", required=True)
    evidence_document_id = fields.Many2one("fix.document", string="Evidence", ondelete="restrict")
    evidence_file = fields.Binary(string="Upload Evidence", store=False)
    evidence_filename = fields.Char(string="Evidence File Name", store=False)
    # damage assessment (FR-WTY-029)
    assessed_value = fields.Monetary(
        string="Assessed Repair / Replace Value", currency_field="currency_id"
    )
    damage_consistent = fields.Boolean(string="Damage Consistent With Declared Cause", default=True)
    remedy = fields.Selection(
        [("repair", "Repair"), ("replace", "Replace")], string="Repair Or Replace"
    )
    assessment_note = fields.Text(string="Technical Assessment")
    assessed_by_id = fields.Many2one("res.users", string="Assessed By", readonly=True)
    within_waiting_period = fields.Boolean(compute="_compute_cover", string="Within Waiting Period")
    fraud_score = fields.Integer(string="Fraud Score", readonly=True)
    fraud_signals = fields.Char(string="Fraud Signals", readonly=True)
    fraud_review_ids = fields.One2many(
        "fix.warranty.fraud.review", "protection_claim_id", string="Fraud Reviews"
    )
    # decision (FR-WTY-030) and money
    excess_amount = fields.Monetary(string="Excess", currency_field="currency_id", readonly=True)
    approved_amount = fields.Monetary(
        string="Payable By The Plan", currency_field="currency_id", readonly=True
    )
    decision_reason = fields.Text(string="Decision Reason", readonly=True)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(string="Decided At", readonly=True)
    excess_state = fields.Selection(
        [("due", "Due"), ("collected", "Collected"), ("waived", "Waived"), ("none", "No Excess")],
        string="Excess Status",
        readonly=True,
        default="due",
    )
    excess_ref = fields.Char(string="Excess Receipt / Waiver", readonly=True)
    excess_by_id = fields.Many2one("res.users", string="Excess Recorded By", readonly=True)
    # fulfilment (FR-WTY-031)
    fulfilment_type = fields.Selection(
        [
            ("repair", "Repair (M01 order)"),
            ("replacement", "Replacement"),
            ("cash", "Cash settlement"),
            ("refund", "Refund"),
        ],
        string="Fulfilment",
    )
    fulfilment_ref = fields.Char(string="Fulfilment Reference")
    settled_at = fields.Datetime(string="Settled At", readonly=True)
    settled_by_id = fields.Many2one("res.users", string="Settled By", readonly=True)
    state = fields.Selection(PCLAIM_STATES, default="draft", required=True, tracking=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "assessed_by_id",
            "fraud_score",
            "fraud_signals",
            "excess_amount",
            "approved_amount",
            "decision_reason",
            "decided_by_id",
            "decided_at",
            "excess_state",
            "excess_ref",
            "excess_by_id",
            "settled_at",
            "settled_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {"policy_id", "incident_date", "cause", "channel"}
            if self.state != "draft":
                locked |= {
                    "description",
                    "assessed_value",
                    "damage_consistent",
                    "remedy",
                    "assessment_note",
                    "evidence_document_id",
                }
            if self.state in ("rejected", "settled"):
                locked |= {"fulfilment_type", "fulfilment_ref"}
        return locked

    @api.depends("incident_date", "policy_id.waiting_until")
    def _compute_cover(self):
        for claim in self:
            claim.within_waiting_period = bool(
                claim.incident_date
                and claim.policy_id.waiting_until
                and claim.incident_date < claim.policy_id.waiting_until
            )

    @api.model_create_multi
    def create(self, vals_list):
        docs = []
        today = _today(self.env)
        for vals in vals_list:
            _assert_role(self.env, CLERK_GROUP, "Receiving a protection claim")
            policy = self.env["fix.protection.policy"].browse(vals.get("policy_id")).exists()
            if not policy:
                raise ValidationError("Choose the policy the claim is made on.")
            if policy.state != "active":
                raise ValidationError(
                    "Policy %s is %s: only an active policy takes a claim."
                    % (policy.name, policy.state)
                )
            incident = fields.Date.to_date(vals.get("incident_date"))
            if not incident or incident > today:
                raise ValidationError("The incident date is a past date.")
            if incident < policy.term_start or (policy.term_end and incident > policy.term_end):
                raise ValidationError(
                    "The incident (%s) is outside policy %s's cover (%s to %s)."
                    % (incident, policy.name, policy.term_start, policy.term_end)
                )
            docs.append(
                _upload_document(
                    self.env,
                    vals,
                    "evidence_file",
                    "evidence_filename",
                    "Protection claim evidence",
                    self._name,
                    "custody_photo",
                )
            )
            vals["name"] = _seq(self.env, "fix.protection.claim", "PCL")
            vals["operating_unit_id"] = policy.operating_unit_id.id or False
            vals["company_id"] = policy.company_id.id
        records = super().create(vals_list)
        for rec, doc in zip(records, docs, strict=True):
            if doc:
                rec.sudo().write({"evidence_document_id": doc.id})
            _bind(rec.evidence_document_id, rec)
            stamp = {"excess_amount": rec.policy_id.excess}
            if not rec.policy_id.excess:
                stamp["excess_state"] = "none"
            if rec.within_waiting_period:
                # BRU-WTY-12 (H): rejected, and the customer is told why
                stamp.update(
                    state="rejected",
                    decided_at=fields.Datetime.now(),
                    decision_reason="The incident (%s) falls within the waiting period, which ends %s "
                    "(BRU-WTY-12)." % (rec.incident_date, rec.policy_id.waiting_until),
                )
            rec._guarded().write(stamp)
        return records

    def write(self, vals):
        doc = _upload_document(
            self.env,
            vals,
            "evidence_file",
            "evidence_filename",
            "Protection claim evidence",
            self._name,
            "custody_photo",
        )
        if doc:
            vals["evidence_document_id"] = doc.id
        res = super().write(vals)
        if doc:
            for rec in self:
                _bind(doc, rec)
        return res

    def _score(self):
        """FR-WTY-035: explainable indicators, each with its weight (T-13)."""
        self.ensure_one()
        signals, score = [], 0
        policy = self.policy_id
        if policy.activated_at and (self.incident_date - policy.activated_at.date()).days <= 30:
            score += 40
            signals.append("incident within 30 days of activation (+40)")
        since = self.incident_date - timedelta(days=180)
        repeats = self.search_count(
            [
                ("id", "!=", self.id),
                ("device_id", "=", self.device_id.id),
                ("incident_date", ">=", since),
                ("state", "!=", "rejected"),
            ]
        )
        if repeats:
            score += 30
            signals.append("%d other claim(s) on the device in 180 days (+30)" % repeats)
        if not self.damage_consistent:
            score += 30
            signals.append("damage inconsistent with the declared cause (+30)")
        if not self.evidence_document_id:
            score += 20
            signals.append("no evidence uploaded (+20)")
        return min(score, 100), "; ".join(signals)

    def action_assess(self):
        """FR-WTY-028/029: the technical assessment, recorded on the form,
        is confirmed here; coverage is checked and the claim scored."""
        for claim in self:
            _assert_role(self.env, CLERK_GROUP, "Assessing a protection claim")
            if claim.state != "draft":
                raise UserError(
                    "%s is %s; only a received claim is assessed." % (claim.name, claim.state)
                )
            if (
                claim.assessed_value <= 0
                or not claim.remedy
                or not (claim.assessment_note or "").strip()
            ):
                raise UserError(
                    "Fill in the assessed value, repair-or-replace and the technical assessment first."
                )
            score, signals = claim._score()
            claim._guarded().write(
                {
                    "state": "assessed",
                    "assessed_by_id": self.env.uid,
                    "fraud_score": score,
                    "fraud_signals": signals or False,
                }
            )
        return True

    def _decider(self, what):
        _assert_role(self.env, OFFICER_GROUP, what)
        for claim in self:
            _not_same(
                self.env,
                claim.create_uid | claim.assessed_by_id,
                "%s on %s" % (what.lower(), claim.name),
            )

    def action_approve(self):
        """FR-WTY-030/033: an officer who neither received nor assessed it.
        Payable = assessed value less excess, within the remaining limit."""
        self._decider("Approving a protection claim")
        for claim in self:
            if claim.state != "assessed":
                raise UserError(
                    "Only an assessed claim is approved (%s is %s)." % (claim.name, claim.state)
                )
            if claim.within_waiting_period:
                raise UserError("The incident falls within the waiting period (BRU-WTY-12).")
            if claim.policy_id.state != "active":
                raise UserError("Policy %s is %s." % (claim.policy_id.name, claim.policy_id.state))
            reviews = claim.fraud_review_ids
            if reviews.filtered(lambda r: r.finding == "confirmed"):
                raise UserError(
                    "A fraud review confirmed fraud on %s; it cannot be approved." % claim.name
                )
            if claim.fraud_score >= FRAUD_REVIEW_THRESHOLD and not reviews.filtered(
                lambda r: r.finding == "cleared"
            ):
                raise UserError(
                    "%s scores %d for fraud (%s): it is investigated before settlement (BRU-WTY-21). "
                    "Record a Fraud Review first."
                    % (claim.name, claim.fraud_score, claim.fraud_signals)
                )
            payable = max(claim.assessed_value - claim.excess_amount, 0.0)
            limit = claim.policy_id.claim_limit
            if limit:
                remaining = claim.policy_id.remaining_limit
                if payable > remaining + 0.005:
                    raise UserError(
                        "%s would pay %.2f but policy %s has %.2f of its limit left (BRU-WTY-14). "
                        "Reject it, or approve within the limit after re-assessment."
                        % (claim.name, payable, claim.policy_id.name, remaining)
                    )
            if payable <= 0:
                raise UserError(
                    "Nothing is payable: the assessed value does not exceed the excess."
                )
            claim._guarded().write(
                {
                    "state": "approved",
                    "approved_amount": payable,
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
            # FR-WTY-036: on notification the reserve is topped up to cover the
            # incurred claim, never reduced below it
            short = round(payable - claim.policy_id.reserve_balance, 2)
            if short > 0.005:
                claim.policy_id._reserve(
                    "adjust", short, "Claim %s approved for %.2f" % (claim.name, payable), claim
                )
        return True

    def action_reject(self, reason=None):
        """FR-WTY-034: rejected with a reason the customer is given."""
        if not (reason or "").strip():
            raise UserError("Give the reason, in words the customer will read.")
        self._decider("Rejecting a protection claim")
        for claim in self:
            if claim.state not in ("draft", "assessed"):
                raise UserError("%s is %s." % (claim.name, claim.state))
            claim._guarded().write(
                {
                    "state": "rejected",
                    "decision_reason": reason.strip(),
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
        return True

    def action_record_excess(self, receipt_ref=None):
        """FR-WTY-032: the excess is collected before fulfilment."""
        if not (receipt_ref or "").strip():
            raise UserError("Give the receipt number the excess was collected under.")
        for claim in self:
            _assert_role(self.env, CLERK_GROUP, "Recording an excess payment")
            if claim.state != "approved" or claim.excess_state != "due":
                raise UserError("%s has no excess due." % claim.name)
            claim._guarded().write(
                {
                    "excess_state": "collected",
                    "excess_ref": receipt_ref.strip(),
                    "excess_by_id": self.env.uid,
                }
            )
        return True

    def action_waive_excess(self, reason=None):
        """BRU-WTY-13: waived only with a recorded approval by an officer who
        did not receive the claim."""
        if not (reason or "").strip():
            raise UserError("Give the reason the excess is waived.")
        self._decider("Waiving an excess")
        for claim in self:
            if claim.state != "approved" or claim.excess_state != "due":
                raise UserError("%s has no excess due." % claim.name)
            claim._guarded().write(
                {
                    "excess_state": "waived",
                    "excess_ref": reason.strip(),
                    "excess_by_id": self.env.uid,
                }
            )
        return True

    def action_settle(self):
        """FR-WTY-031/033/036: fulfilled; the limit is consumed and the
        reserve released by what the plan paid."""
        for claim in self:
            _assert_role(self.env, CLERK_GROUP, "Settling a protection claim")
            if claim.state != "approved":
                raise UserError(
                    "Only an approved claim is settled (%s is %s)." % (claim.name, claim.state)
                )
            if claim.excess_state == "due":
                raise UserError(
                    "Collect or waive the excess of %.2f before fulfilment (BRU-WTY-13)."
                    % claim.excess_amount
                )
            if not claim.fulfilment_type or not (claim.fulfilment_ref or "").strip():
                raise UserError(
                    "Record how the claim was fulfilled and its reference (order, replacement or M20 payment)."
                )
            claim._guarded().write(
                {
                    "state": "settled",
                    "settled_at": fields.Datetime.now(),
                    "settled_by_id": self.env.uid,
                }
            )
            policy = claim.policy_id
            release = min(claim.approved_amount, max(policy.reserve_balance, 0.0))
            if release > 0.005:
                policy._reserve("release", -release, "Claim %s settled" % claim.name, claim)
            policy.invalidate_recordset(["claimed_amount", "remaining_limit", "reserve_balance"])
            if policy.claim_limit and policy.remaining_limit <= 0.005:
                policy._guarded().write({"state": "exhausted"})
                policy._release_reserve("Released: limit exhausted")
            publish(
                self.env,
                "protection_claim.settled",
                "fix.protection.claim",
                claim.id,
                {
                    "claim_no": claim.name,
                    "policy_no": policy.name,
                    "amount": claim.approved_amount,
                    "fulfilment_type": claim.fulfilment_type,
                    "fulfilment_ref": claim.fulfilment_ref,
                    "company_id": claim.company_id.id,
                },
            )
        return True


# ==========================================================================
# page 8: brand claim rules - FR-WTY-040, T-03
# ==========================================================================
class FixBrandClaimRule(models.Model):
    """One brand's claim rule set, as configuration. The active version
    decides which evidence the pack needs, the submission window and whether
    the defective part goes back before the claim is recoverable."""

    _name = "fix.brand.claim.rule"
    _description = "Brand Claim Rule Set"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "brand_id, version desc"

    name = fields.Char(string="Rule Set", compute="_compute_name", store=True)
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True, index=True)
    version = fields.Integer(readonly=True, default=1)
    valid_from = fields.Date(string="Valid From", required=True, default=fields.Date.context_today)
    channel = fields.Selection(
        [
            ("api", "Brand API"),
            ("portal", "Brand portal (assisted)"),
            ("file", "Structured file"),
            ("email", "E-mail"),
            ("p08", "P08 partner portal"),
        ],
        string="Submission Channel",
        required=True,
        default="portal",
    )
    submission_window_days = fields.Integer(
        string="Submission Window (days from job completion)", required=True, default=3
    )
    resubmission_window_days = fields.Integer(string="Resubmission Window (days)", default=7)
    labour_allowance_minutes = fields.Integer(string="Standard Labour Allowance (min)")
    requires_defective_return = fields.Boolean(
        string="Defective Part Returned Before Recovery",
        help="BRU-WTY-19: the claim is not recoverable until the return is evidenced.",
    )
    requires_certified_technician = fields.Boolean(string="Certified Technician Only")
    req_photo_before = fields.Boolean(string="Before Photograph", default=True)
    req_photo_after = fields.Boolean(string="After Photograph", default=True)
    req_diagnostic = fields.Boolean(string="Diagnostic Record", default=True)
    req_parts_issued = fields.Boolean(string="Parts Issued Evidence", default=True)
    req_device_serial = fields.Boolean(string="Device Serial Capture", default=True)
    req_technician_cert = fields.Boolean(string="Technician Certification", default=True)
    req_purchase_proof = fields.Boolean(string="Purchase Proof", default=True)
    code_scheme = fields.Char(string="Fault Code Scheme")
    note = fields.Text(string="Other Rules")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
    )
    activated_by_id = fields.Many2one("res.users", string="Activated By", readonly=True)
    activated_at = fields.Datetime(string="Activated At", readonly=True)

    @api.depends("brand_id", "version")
    def _compute_name(self):
        for rule in self:
            rule.name = "%s rules v%d" % (rule.brand_id.name or "?", rule.version or 1)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "version",
            "activated_by_id",
            "activated_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "draft":
            locked |= {
                n
                for n, f in self._fields.items()
                if f.store and not n.startswith(("message_", "activity_"))
            }
        return locked

    def required_keys(self):
        self.ensure_one()
        return [key for key, _label in EVIDENCE_REQUIREMENTS if self["req_%s" % key]]

    @api.constrains(
        "submission_window_days", "resubmission_window_days", "labour_allowance_minutes"
    )
    def _check_rule(self):
        for rule in self:
            if rule.submission_window_days <= 0:
                raise ValidationError("The submission window is a positive number of days.")
            if rule.resubmission_window_days < 0 or rule.labour_allowance_minutes < 0:
                raise ValidationError("Windows and allowances cannot be negative.")
            if not rule.required_keys():
                raise ValidationError("A brand rule set requires at least one evidence item.")

    @api.model_create_multi
    def create(self, vals_list):
        if vals_list:
            _assert_role(self.env, OFFICER_GROUP, "Writing a brand's claim rules")
        records = super().create(vals_list)
        for rec in records:
            latest = self.search(
                [("brand_id", "=", rec.brand_id.id), ("id", "!=", rec.id)],
                order="version desc",
                limit=1,
            )
            rec._guarded().write({"version": (latest.version or 0) + 1})
        return records

    def write(self, vals):
        _refuse_frozen(
            self,
            vals,
            lambda r: r.state != "draft",
            "An active or retired rule set is not edited: write a new version.",
        )
        return super().write(vals)

    def action_activate(self):
        """Another Claim Decision Officer activates it; the brand's previous
        version retires and open claims re-read their evidence list."""
        _assert_role(self.env, OFFICER_GROUP, "Activating brand claim rules")
        for rule in self:
            if rule.state != "draft":
                raise UserError("%s is %s." % (rule.name, rule.state))
            _not_same(self.env, rule.create_uid, "activating %s" % rule.name)
            self.search(
                [("brand_id", "=", rule.brand_id.id), ("state", "=", "active")]
            )._guarded().write({"state": "retired"})
            rule._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                }
            )
            claims = (
                self.env["fix.warranty.claim"]
                .sudo()
                .search([("brand_id", "=", rule.brand_id.id), ("state", "in", list(OPEN_STATES))])
            )
            if claims:
                for fname in ("evidence_complete", "missing_evidence"):
                    self.env.add_to_compute(claims._fields[fname], claims)
                self.env.flush_all()
        return True

    def action_retire(self):
        _assert_role(self.env, OFFICER_GROUP, "Retiring brand claim rules")
        for rule in self.filtered(lambda r: r.state == "active"):
            rule._guarded().write({"state": "retired"})
        return True

    @api.model
    def active_for(self, brand):
        if not brand:
            return self.browse()
        return self.sudo().search([("brand_id", "=", brand.id), ("state", "=", "active")], limit=1)


# ==========================================================================
# page 9: the brand's request for information - FR-WTY-047/049
# ==========================================================================
class FixWarrantyClaimInfoRequest(models.Model):
    _name = "fix.warranty.claim.info.request"
    _description = "Brand Request For Information"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    claim_id = fields.Many2one(
        "fix.warranty.claim", string="Claim", required=True, index=True, ondelete="restrict"
    )
    brand_id = fields.Many2one(related="claim_id.brand_id", string="Brand", store=True)
    requested_on = fields.Date(
        string="Brand Asked On", required=True, default=fields.Date.context_today
    )
    request_text = fields.Text(string="What The Brand Asks For", required=True)
    brand_ref = fields.Char(string="Brand's Reference")
    due_date = fields.Date(string="Answer Due By", required=True)
    response = fields.Text(string="Our Answer", readonly=True)
    response_document_id = fields.Many2one(
        "fix.document", string="Document Sent", ondelete="restrict"
    )
    responded_by_id = fields.Many2one("res.users", string="Answered By", readonly=True)
    responded_at = fields.Datetime(string="Answered At", readonly=True)
    overdue = fields.Boolean(compute="_compute_overdue")
    state = fields.Selection(
        [("open", "Open"), ("answered", "Answered")], default="open", required=True, tracking=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "response",
            "responded_by_id",
            "responded_at",
        }

    @api.depends("due_date", "state")
    def _compute_overdue(self):
        today = _today(self.env)
        for rec in self:
            rec.overdue = rec.state == "open" and bool(rec.due_date) and rec.due_date < today

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _assert_role(self.env, CLERK_GROUP, "Recording a brand's request for information")
            claim = self.env["fix.warranty.claim"].browse(vals.get("claim_id")).exists()
            if not claim or claim.state not in ("submitted", "in_review"):
                raise ValidationError(
                    "A brand asks for information on a claim it is deciding (submitted or in review)."
                )
            if (
                vals.get("due_date")
                and vals.get("requested_on")
                and fields.Date.to_date(vals["due_date"])
                < fields.Date.to_date(vals["requested_on"])
            ):
                raise ValidationError("The answer cannot be due before the brand asked.")
            vals["name"] = _seq(self.env, "fix.warranty.claim.info.request", "RFI")
        return super().create(vals_list)

    def write(self, vals):
        _refuse_frozen(
            self,
            vals,
            lambda r: r.state == "answered",
            "An answered request is a record of what was sent.",
        )
        return super().write(vals)

    def action_answer(self, response=None):
        if not (response or "").strip():
            raise UserError("Write what was sent to the brand.")
        for rec in self:
            _assert_role(self.env, CLERK_GROUP, "Answering a brand's request")
            if rec.state != "open":
                raise UserError("%s is already answered." % rec.name)
            rec._guarded().write(
                {
                    "state": "answered",
                    "response": response.strip(),
                    "responded_by_id": self.env.uid,
                    "responded_at": fields.Datetime.now(),
                }
            )
            rec.claim_id.message_post(
                body="Information sent to the brand (%s): %s" % (rec.name, response.strip())
            )
        return True


class FixClaimAppealEvidence(models.Model):
    _inherit = "fix.claim.appeal"

    # FR-WTY-049: an appeal is made WITH additional evidence.
    evidence_document_id = fields.Many2one(
        "fix.document", string="Additional Evidence", ondelete="restrict"
    )


# ==========================================================================
# page 10: remittance, reconciliation, write-off, defective returns
# ==========================================================================
class FixBrandRemittance(models.Model):
    """FR-WTY-053: one brand payment, split across the claims it settles.
    Matching posts each line through the claim's own remittance method; what
    the lines do not cover stays visible as unmatched (T-08)."""

    _name = "fix.brand.remittance"
    _description = "Brand Remittance"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "received_on desc, id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    company_id = fields.Many2one("res.company", required=True, default=lambda s: s.env.company)
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True, index=True)
    bank_ref = fields.Char(string="Bank Reference", required=True)
    received_on = fields.Date(
        string="Received On", required=True, default=fields.Date.context_today
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda s: s.env.ref("base.BDT")
    )
    total_amount = fields.Monetary(
        string="Amount Received", currency_field="currency_id", required=True
    )
    advice_document_id = fields.Many2one(
        "fix.document", string="Brand Remittance Advice", ondelete="restrict"
    )
    line_ids = fields.One2many("fix.brand.remittance.line", "remittance_id", string="Claims Paid")
    allocated_amount = fields.Monetary(
        string="Allocated", currency_field="currency_id", compute="_compute_allocated"
    )
    unmatched_amount = fields.Monetary(
        string="Unmatched", currency_field="currency_id", compute="_compute_allocated"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("matched", "Matched"), ("unmatched", "Matched - Amount Unallocated")],
        default="draft",
        required=True,
        tracking=True,
    )
    matched_by_id = fields.Many2one("res.users", string="Matched By", readonly=True)
    matched_at = fields.Datetime(string="Matched At", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "matched_by_id", "matched_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "draft":
            locked |= {
                "brand_id",
                "bank_ref",
                "received_on",
                "total_amount",
                "line_ids",
                "currency_id",
            }
        return locked

    @api.depends("line_ids.amount", "total_amount")
    def _compute_allocated(self):
        for rec in self:
            rec.allocated_amount = sum(rec.line_ids.mapped("amount"))
            rec.unmatched_amount = rec.total_amount - rec.allocated_amount

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _assert_role(self.env, CLERK_GROUP, "Recording a brand remittance")
            if float(vals.get("total_amount") or 0.0) <= 0:
                raise ValidationError("A remittance is a positive amount received.")
            vals["name"] = _seq(self.env, "fix.brand.remittance", "BRM")
        return super().create(vals_list)

    def write(self, vals):
        _refuse_frozen(
            self,
            vals,
            lambda r: r.state != "draft",
            "A matched remittance is a record of what the bank received.",
        )
        return super().write(vals)

    def action_match(self):
        """A Claim Decision Officer posts every line to its claim."""
        for rec in self:
            _assert_role(self.env, OFFICER_GROUP, "Matching a brand remittance")
            if rec.state != "draft":
                raise UserError("%s is already matched." % rec.name)
            if not rec.line_ids:
                raise UserError("Add the claims this payment settles.")
            if rec.allocated_amount > rec.total_amount + 0.005:
                raise UserError(
                    "The lines allocate %.2f, more than the %.2f received."
                    % (rec.allocated_amount, rec.total_amount)
                )
            for line in rec.line_ids:
                claim = line.claim_id
                if claim.brand_id != rec.brand_id:
                    raise UserError(
                        "%s is %s's claim, not %s's."
                        % (claim.claim_no, claim.brand_id.name, rec.brand_id.name)
                    )
                claim.action_record_remittance(line.amount, "%s (%s)" % (rec.bank_ref, rec.name))
                line.sudo().write(
                    {
                        "variance": round(
                            (claim.approved_amount or 0.0) - (claim.remittance_amount or 0.0), 2
                        )
                    }
                )
            state = "matched" if abs(rec.unmatched_amount) <= 0.005 else "unmatched"
            rec._guarded().write(
                {"state": state, "matched_by_id": self.env.uid, "matched_at": fields.Datetime.now()}
            )
        return True


class FixBrandRemittanceLine(models.Model):
    _name = "fix.brand.remittance.line"
    _description = "Brand Remittance Line"

    remittance_id = fields.Many2one(
        "fix.brand.remittance", required=True, ondelete="cascade", index=True
    )
    claim_id = fields.Many2one(
        "fix.warranty.claim", string="Claim", required=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(related="remittance_id.currency_id")
    approved_amount = fields.Monetary(related="claim_id.approved_amount", string="Approved")
    amount = fields.Monetary(
        string="Paid On This Claim", currency_field="currency_id", required=True
    )
    variance = fields.Monetary(
        string="Still Outstanding", currency_field="currency_id", readonly=True
    )

    @api.constrains("amount", "claim_id")
    def _check_line(self):
        for line in self:
            if line.amount <= 0:
                raise ValidationError("Each line is a positive amount paid on a claim.")
            if line.claim_id.state not in RECOVERY_STATES and line.remittance_id.state == "draft":
                raise ValidationError(
                    "%s is %s: only an approved claim is paid."
                    % (line.claim_id.claim_no, line.claim_id.state)
                )


class FixBrandReconciliation(models.Model):
    """FR-WTY-054: a brand's claims for a period, totalled, then signed by an
    officer who did not prepare it. A signed statement is frozen."""

    _name = "fix.brand.reconciliation"
    _description = "Brand Period Reconciliation"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "date_to desc, id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    company_id = fields.Many2one("res.company", required=True, default=lambda s: s.env.company)
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True, index=True)
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.ref("base.BDT"))
    claim_count = fields.Integer(string="Claims", readonly=True)
    claimed = fields.Monetary(currency_field="currency_id", readonly=True)
    approved = fields.Monetary(currency_field="currency_id", readonly=True)
    rejected = fields.Monetary(currency_field="currency_id", readonly=True)
    paid = fields.Monetary(currency_field="currency_id", readonly=True)
    outstanding = fields.Monetary(currency_field="currency_id", readonly=True)
    written_off = fields.Monetary(string="Written Off", currency_field="currency_id", readonly=True)
    note = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("signed", "Signed")],
        default="draft",
        required=True,
        tracking=True,
    )
    computed_by_id = fields.Many2one("res.users", string="Prepared By", readonly=True)
    computed_at = fields.Datetime(string="Prepared At", readonly=True)
    signed_by_id = fields.Many2one("res.users", string="Signed By", readonly=True)
    signed_at = fields.Datetime(string="Signed At", readonly=True)

    _AMOUNTS = (
        "claim_count",
        "claimed",
        "approved",
        "rejected",
        "paid",
        "outstanding",
        "written_off",
    )

    def _fix_guarded_fields(self) -> set:
        return (
            super()._fix_guarded_fields()
            | set(self._AMOUNTS)
            | {"state", "computed_by_id", "computed_at", "signed_by_id", "signed_at"}
        )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state == "signed":
            locked |= {"brand_id", "date_from", "date_to", "note"}
        return locked

    @api.constrains("date_from", "date_to")
    def _check_period(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError("The period ends before it starts.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _assert_role(self.env, CLERK_GROUP, "Preparing a brand reconciliation")
            vals["name"] = _seq(self.env, "fix.brand.reconciliation", "BRC")
        return super().create(vals_list)

    def write(self, vals):
        _refuse_frozen(
            self, vals, lambda r: r.state == "signed", "A signed reconciliation is frozen."
        )
        res = super().write(vals)
        if not self._fix_guard_open() and {"brand_id", "date_from", "date_to"} & set(vals):
            self.filtered(lambda r: r.state == "computed")._guarded().write({"state": "draft"})
        return res

    def action_compute(self):
        for rec in self:
            _assert_role(self.env, CLERK_GROUP, "Computing a brand reconciliation")
            if rec.state == "signed":
                raise UserError("%s is signed." % rec.name)
            claims = (
                self.env["fix.warranty.claim"]
                .sudo()
                .search(
                    [
                        ("brand_id", "=", rec.brand_id.id),
                        ("company_id", "in", [rec.company_id.id, False]),
                        ("created_at", ">=", fields.Datetime.to_datetime(rec.date_from)),
                        (
                            "created_at",
                            "<",
                            fields.Datetime.to_datetime(rec.date_to + timedelta(days=1)),
                        ),
                    ]
                )
            )
            submitted = claims.filtered(lambda c: c.state not in OPEN_STATES)
            agreed = claims.filtered(
                lambda c: c.state
                in ("approved", "partially_approved", "remitted", "closed", "written_off")
            )
            open_money = claims.filtered(lambda c: c.state in RECOVERY_STATES)
            vals = {
                "claim_count": len(claims),
                "claimed": sum(submitted.mapped("claim_amount")),
                "approved": sum(agreed.mapped("approved_amount")),
                "rejected": sum(
                    claims.filtered(lambda c: c.state == "rejected").mapped("claim_amount")
                ),
                "paid": sum(claims.mapped("remittance_amount")),
                "outstanding": sum(
                    max((c.approved_amount or 0.0) - (c.remittance_amount or 0.0), 0.0)
                    for c in open_money
                ),
                "written_off": sum(claims.mapped("written_off_amount")),
                "state": "computed",
                "computed_by_id": self.env.uid,
                "computed_at": fields.Datetime.now(),
            }
            rec._guarded().write(vals)
        return True

    def action_sign(self):
        _assert_role(self.env, OFFICER_GROUP, "Signing a brand reconciliation")
        for rec in self:
            if rec.state != "computed":
                raise UserError("Compute %s before it is signed." % rec.name)
            _not_same(self.env, rec.computed_by_id | rec.create_uid, "signing %s" % rec.name)
            rec._guarded().write(
                {
                    "state": "signed",
                    "signed_by_id": self.env.uid,
                    "signed_at": fields.Datetime.now(),
                }
            )
        return True


class FixClaimWriteoff(models.Model):
    """FR-WTY-055, BRU-WTY-07 (H): an unrecoverable claim balance is written
    off only with a Finance Manager's approval, never by the person who raised
    or submitted the claim or requested the write-off."""

    _name = "fix.claim.writeoff"
    _description = "Warranty Claim Write-off"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    company_id = fields.Many2one(related="claim_id.company_id", store=True)
    claim_id = fields.Many2one(
        "fix.warranty.claim", string="Claim", required=True, index=True, ondelete="restrict"
    )
    brand_id = fields.Many2one(related="claim_id.brand_id", string="Brand", store=True)
    currency_id = fields.Many2one(related="claim_id.currency_id")
    outstanding = fields.Monetary(
        string="Outstanding On The Claim",
        currency_field="currency_id",
        compute="_compute_outstanding",
    )
    amount = fields.Monetary(
        string="Amount To Write Off", currency_field="currency_id", required=True
    )
    reason = fields.Text(required=True)
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", readonly=True, default=lambda s: s.env.user
    )
    approved_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(string="Decided At", readonly=True)
    decision_note = fields.Text(readonly=True)
    state = fields.Selection(
        [("requested", "Requested"), ("approved", "Approved"), ("refused", "Refused")],
        default="requested",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "approved_by_id",
            "decided_at",
            "decision_note",
        }

    @api.depends("claim_id.approved_amount", "claim_id.remittance_amount")
    def _compute_outstanding(self):
        for rec in self:
            claim = rec.claim_id
            rec.outstanding = max(
                (claim.approved_amount or 0.0) - (claim.remittance_amount or 0.0), 0.0
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _assert_role(self.env, CLERK_GROUP, "Requesting a claim write-off")
            claim = self.env["fix.warranty.claim"].browse(vals.get("claim_id")).exists()
            if not claim or claim.state not in RECOVERY_STATES:
                raise ValidationError(
                    "A write-off is requested on an approved claim the brand has not fully paid."
                )
            outstanding = max(
                (claim.approved_amount or 0.0) - (claim.remittance_amount or 0.0), 0.0
            )
            amount = float(vals.get("amount") or 0.0)
            if amount <= 0 or amount > outstanding + 0.005:
                raise ValidationError(
                    "Write off a positive amount up to the %.2f still outstanding on %s."
                    % (outstanding, claim.claim_no)
                )
            if self.search_count([("claim_id", "=", claim.id), ("state", "=", "requested")]):
                raise ValidationError(
                    "%s already has a write-off awaiting decision." % claim.claim_no
                )
            vals["name"] = _seq(self.env, "fix.claim.writeoff", "CWO")
        return super().create(vals_list)

    def write(self, vals):
        _refuse_frozen(
            self,
            vals,
            lambda r: r.state != "requested",
            "A decided write-off is a record of the decision.",
        )
        return super().write(vals)

    def _decide(self):
        for rec in self:
            if rec.state != "requested":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            _assert_role(self.env, FINANCE_MANAGER_GROUP, "Deciding a claim write-off")
            claim = rec.claim_id
            _not_same(
                self.env,
                rec.requested_by_id | rec.create_uid | claim.create_uid | claim.submitted_by_id,
                "deciding write-off %s (BRU-WTY-07)" % rec.name,
            )

    def action_approve(self):
        self._decide()
        for rec in self:
            claim = rec.claim_id
            outstanding = max(
                (claim.approved_amount or 0.0) - (claim.remittance_amount or 0.0), 0.0
            )
            if rec.amount > outstanding + 0.005:
                raise UserError(
                    "Only %.2f is still outstanding on %s." % (outstanding, claim.claim_no)
                )
            # the decider is a Finance Manager, not a claims clerk: the role and
            # SoD checks above are the gate, the write is the module's
            rec.sudo()._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
            claim.sudo()._guarded().write(
                {
                    "written_off_amount": (claim.written_off_amount or 0.0) + rec.amount,
                    "state": "written_off" if rec.amount + 0.005 >= outstanding else claim.state,
                }
            )
            claim.sudo().message_post(
                body="Written off %.2f (%s): %s" % (rec.amount, rec.name, rec.reason)
            )
            publish(
                self.env,
                "warranty_claim.written_off",
                "fix.warranty.claim",
                claim.id,
                {
                    "claim_no": claim.claim_no,
                    "writeoff_no": rec.name,
                    "amount": rec.amount,
                    "brand_id": claim.brand_id.id,
                    "company_id": claim.company_id.id,
                },
            )
        return True

    def action_refuse(self, note=None):
        if not (note or "").strip():
            raise UserError("Say why the write-off is refused.")
        self._decide()
        for rec in self:
            rec.sudo()._guarded().write(
                {
                    "state": "refused",
                    "approved_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "decision_note": note.strip(),
                }
            )
        return True


class FixDefectiveReturn(models.Model):
    """FR-WTY-057, BRU-WTY-19 (H): the replaced part sent back to the brand,
    with the waybill and proof. Where the brand's rules require it, the claim
    is not closed as recovered until this is shipped."""

    _name = "fix.defective.return"
    _description = "Defective Part Return"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    claim_id = fields.Many2one(
        "fix.warranty.claim", string="Claim", required=True, index=True, ondelete="restrict"
    )
    brand_id = fields.Many2one(related="claim_id.brand_id", string="Brand", store=True)
    part_description = fields.Char(string="Part", required=True)
    part_serial = fields.Char(string="Part Serial")
    waybill_ref = fields.Char(string="Courier / Waybill Reference")
    shipped_on = fields.Date(string="Shipped On")
    proof_document_id = fields.Many2one(
        "fix.document", string="Proof Of Dispatch", ondelete="restrict"
    )
    proof_file = fields.Binary(string="Upload Proof", store=False)
    proof_filename = fields.Char(string="Proof File Name", store=False)
    state = fields.Selection(
        [("pending", "To Ship"), ("shipped", "Shipped"), ("acknowledged", "Brand Acknowledged")],
        default="pending",
        required=True,
        tracking=True,
    )
    shipped_by_id = fields.Many2one("res.users", string="Shipped By", readonly=True)
    acknowledged_by_id = fields.Many2one(
        "res.users", string="Acknowledgement Recorded By", readonly=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "shipped_by_id", "acknowledged_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "pending":
            locked |= {
                "claim_id",
                "part_description",
                "part_serial",
                "waybill_ref",
                "shipped_on",
                "proof_document_id",
                "proof_file",
            }
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        docs = []
        for vals in vals_list:
            _assert_role(self.env, CLERK_GROUP, "Recording a defective part return")
            claim = self.env["fix.warranty.claim"].browse(vals.get("claim_id")).exists()
            if not claim:
                raise ValidationError("Choose the claim the part was replaced under.")
            docs.append(
                _upload_document(
                    self.env, vals, "proof_file", "proof_filename", "Return proof", self._name
                )
            )
            vals["name"] = _seq(self.env, "fix.defective.return", "DPR")
        records = super().create(vals_list)
        for rec, doc in zip(records, docs, strict=True):
            if doc:
                rec.sudo().write({"proof_document_id": doc.id})
            _bind(rec.proof_document_id, rec)
        return records

    def write(self, vals):
        doc = _upload_document(
            self.env, vals, "proof_file", "proof_filename", "Return proof", self._name
        )
        if doc:
            vals["proof_document_id"] = doc.id
        _refuse_frozen(
            self,
            vals,
            lambda r: r.state != "pending",
            "A shipped return is a record of the dispatch.",
        )
        res = super().write(vals)
        if doc:
            for rec in self:
                _bind(doc, rec)
        return res

    def action_ship(self):
        for rec in self:
            _assert_role(self.env, CLERK_GROUP, "Shipping a defective part")
            if rec.state != "pending":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            if (
                not (rec.waybill_ref or "").strip()
                or not rec.shipped_on
                or not rec.proof_document_id
            ):
                raise UserError(
                    "A return is shipped with its waybill reference, date and proof of dispatch (BRU-WTY-19)."
                )
            rec._guarded().write({"state": "shipped", "shipped_by_id": self.env.uid})
        return True

    def action_acknowledge(self):
        _assert_role(self.env, OFFICER_GROUP, "Recording the brand's receipt of a part")
        for rec in self:
            if rec.state != "shipped":
                raise UserError("%s has not been shipped." % rec.name)
            rec._guarded().write({"state": "acknowledged", "acknowledged_by_id": self.env.uid})
        return True


# ==========================================================================
# page 12: fraud reviews - FR-WTY-051, BRU-WTY-21
# ==========================================================================
class FixWarrantyFraudReview(models.Model):
    """An investigation of one flagged claim, by a Claim Decision Officer who
    did not raise it. Cleared lets a high-score claim be settled; confirmed
    blocks it (a brand claim is not submitted, a protection claim not
    approved). Never edited afterwards."""

    _name = "fix.warranty.fraud.review"
    _description = "Warranty Fraud Review"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    claim_id = fields.Many2one(
        "fix.warranty.claim", string="Brand Claim", index=True, ondelete="restrict"
    )
    protection_claim_id = fields.Many2one(
        "fix.protection.claim", string="Protection Claim", index=True, ondelete="restrict"
    )
    signals = fields.Text(string="Signals Reviewed", readonly=True)
    finding = fields.Selection(
        [("cleared", "Cleared - no fraud"), ("confirmed", "Fraud confirmed")], required=True
    )
    note = fields.Text(string="Investigation Notes", required=True)
    reviewer_id = fields.Many2one(
        "res.users", string="Reviewed By", readonly=True, default=lambda s: s.env.user
    )
    reviewed_at = fields.Datetime(string="Reviewed At", readonly=True, default=fields.Datetime.now)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _assert_role(self.env, OFFICER_GROUP, "Recording a fraud review")
            claim = self.env["fix.warranty.claim"].browse(vals.get("claim_id") or []).exists()
            pclaim = (
                self.env["fix.protection.claim"]
                .browse(vals.get("protection_claim_id") or [])
                .exists()
            )
            if bool(claim) == bool(pclaim):
                raise ValidationError(
                    "A fraud review is about one claim: a brand claim or a protection claim."
                )
            if claim:
                _not_same(
                    self.env,
                    claim.create_uid | claim.submitted_by_id,
                    "reviewing %s" % claim.claim_no,
                )
                vals["signals"] = (
                    claim.missing_evidence and "Missing evidence: %s" % claim.missing_evidence
                ) or "Outbound review"
            else:
                _not_same(
                    self.env,
                    pclaim.create_uid | pclaim.assessed_by_id,
                    "reviewing %s" % pclaim.name,
                )
                vals["signals"] = "Score %d: %s" % (
                    pclaim.fraud_score,
                    pclaim.fraud_signals or "no signal",
                )
            if not (vals.get("note") or "").strip():
                raise ValidationError("Record what the investigation found.")
            vals["name"] = _seq(self.env, "fix.warranty.fraud.review", "FRV")
        return super().create(vals_list)

    def write(self, vals):
        _immutable(self, "A fraud review")
        return super().write(vals)

    def unlink(self):
        _immutable(self, "A fraud review")
        return super().unlink()


# ==========================================================================
# the brand claim reads its brand's rules
# ==========================================================================
class FixWarrantyClaimRules(models.Model):
    _inherit = "fix.warranty.claim"

    state = fields.Selection(
        selection_add=[("written_off", "Written Off")], ondelete={"written_off": "set default"}
    )
    written_off_amount = fields.Monetary(
        string="Written Off", currency_field="currency_id", readonly=True, copy=False
    )
    info_request_ids = fields.One2many(
        "fix.warranty.claim.info.request", "claim_id", string="Information Requests"
    )
    fraud_review_ids = fields.One2many(
        "fix.warranty.fraud.review", "claim_id", string="Fraud Reviews"
    )
    defective_return_ids = fields.One2many(
        "fix.defective.return", "claim_id", string="Defective Part Returns"
    )
    writeoff_ids = fields.One2many("fix.claim.writeoff", "claim_id", string="Write-offs")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"written_off_amount"}

    @api.depends(
        "brand_id",
        "evidence_ids.requirement_key",
        "evidence_ids.document_id",
        "evidence_ids.evidence_hash",
    )
    def _compute_evidence(self):
        """FR-WTY-039/040: the pack the BRAND's active rule set requires; all
        seven items when the brand has no rule set yet."""
        Rule = self.env["fix.brand.claim.rule"]
        for claim in self:
            rule = Rule.active_for(claim.brand_id)
            required = rule.required_keys() if rule else [k for k, _l in EVIDENCE_REQUIREMENTS]
            present = {
                e.requirement_key for e in claim.evidence_ids if e.document_id and e.evidence_hash
            }
            labels = dict(EVIDENCE_REQUIREMENTS)
            missing = [labels[k] for k in required if k not in present]
            claim.evidence_complete = not missing
            claim.missing_evidence = ", ".join(missing) if missing else False

    @api.model_create_multi
    def create(self, vals_list):
        claims = super().create(vals_list)
        Rule = self.env["fix.brand.claim.rule"]
        for claim in claims:
            rule = Rule.active_for(claim.brand_id)
            if rule and claim.job_completed_at:
                # FR-WTY-046: the brand's own window, from the service date
                claim._guarded().write(
                    {
                        "submission_deadline": claim.job_completed_at
                        + timedelta(days=rule.submission_window_days)
                    }
                )
        return claims

    def action_submit(self):
        for claim in self:
            if claim.fraud_review_ids.filtered(lambda r: r.finding == "confirmed"):
                raise UserError(
                    "A fraud review confirmed fraud on %s: it is not submitted (FR-WTY-051)."
                    % claim.claim_no
                )
        return super().action_submit()

    def defective_return_pending(self):
        self.ensure_one()
        rule = self.env["fix.brand.claim.rule"].active_for(self.brand_id)
        if not rule or not rule.requires_defective_return or (self.approved_amount or 0.0) <= 0.005:
            return False
        return not self.defective_return_ids.filtered(
            lambda r: r.state in ("shipped", "acknowledged")
        )

    def action_close(self):
        for claim in self:
            if claim.state == "remitted" and claim.defective_return_pending():
                raise UserError(
                    "%s's rules require the defective part back before the claim is recovered "
                    "(BRU-WTY-19): record and ship the return first." % claim.brand_id.name
                )
        return super().action_close()
