# A04 ERP audit, round 2 (21 Nov 2026), stream R2-2: the deferred M09 items
# that need no owner data.
#
# M09-F13: a brand's rule set declared "certified technician only", a labour
#   allowance, a resubmission window and a fault code scheme, and nothing read
#   any of them. They are enforced at submission (and the resubmission window
#   at appeal / resubmission) while the brand has an ACTIVE rule set:
#     * every technician on the job holds a valid M22 certification for the
#       brand on the job's date (BRU-WTY-10);
#     * the labour recorded on the job's work orders is within the brand's
#       standard allowance, and some labour is recorded (FR-WTY-051,
#       BRU-WTY-09);
#     * each fault code on the job translates to the brand's code through the
#       M37 fault-code brand map (fix.fault.brand.map, FR-WTY-043);
#     * "parts issued" evidence is the M15 issue record of a part issued to
#       THIS job (a document filed on fix.stock.consumption), and parts
#       claimed with nothing issued from stock are refused (BRU-WTY-09). It
#       used to be any document whose name contained "parts_issued".
# M09-F16 (mechanism): every submission and resubmission to the brand is
#   recorded (what was sent, its digest, when, by whom, the brand's codes and
#   the brand's own reference once received).
# M09-F12: approved-but-unpaid OEM receivables age in buckets on the claim
#   and a daily chase escalates by age (cd_warranty_claims.chase_days,
#   default 30,60,90): a to-do for the claims officer, a Finance Manager added
#   from the second level.
# M09-F15 (rest): per-claim limit, claim-count limit and depreciation are plan
#   fields (0 = none) copied onto the policy at sale; protection claims above
#   a value band are routed through M63 at the band's DOFA tier
#   (cd_warranty_claims.protection_claim_dofa_bands, e.g. "50000:tier_1,
#   200000:tier_2"; unset = no extra routing - OWNER fills it in).
import base64
import hashlib
import json

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.addons.cd_workflow_engine.models.fix_approval_engine import TIER_GROUP
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_m09_capture import _today
from .fix_warranty_claims import (
    CLERK_GROUP,
    OFFICER_GROUP,
    OPEN_STATES,
    RECOVERY_STATES,
    _assert_role,
)

PARAM_CHASE_DAYS = "cd_warranty_claims.chase_days"
DEFAULT_CHASE_DAYS = (30, 60, 90)
PARAM_BANDS = "cd_warranty_claims.protection_claim_dofa_bands"
FINANCE_MANAGER_GROUP = "account.group_account_manager"
CTX_BAND_APPROVED = "fix_protection_band_approved"
WORK_DONE_EXCLUDED = ("cancelled", "failed")
AGEING_BUCKETS = [
    ("b0_30", "0-30 days"),
    ("b31_60", "31-60 days"),
    ("b61_90", "61-90 days"),
    ("b90", "Over 90 days"),
]


def _dhaka_date(env, value):
    if not value:
        return None
    user = env["res.users"].with_context(tz="Asia/Dhaka")
    return fields.Datetime.context_timestamp(user, value).date()


def _bucket(age):
    if age <= 30:
        return "b0_30"
    if age <= 60:
        return "b31_60"
    if age <= 90:
        return "b61_90"
    return "b90"


class FixWarrantyClaimBrandRules(models.Model):
    _inherit = "fix.warranty.claim"

    brand_fault_codes = fields.Char(
        string="Brand Fault Codes",
        readonly=True,
        copy=False,
        help="The brand's codes the job's fault codes translated to when the claim was sent.",
    )
    labour_minutes = fields.Integer(
        string="Labour Claimed (min)",
        readonly=True,
        copy=False,
        help="The labour recorded on the job's work orders when the claim was sent.",
    )
    submission_ids = fields.One2many(
        "fix.warranty.claim.submission", "claim_id", string="Submissions to the Brand"
    )
    chase_level = fields.Integer(
        string="Chase Level",
        readonly=True,
        copy=False,
        help="How far the unpaid receivable has been escalated (0 = not chased).",
    )
    last_chased_at = fields.Datetime(string="Last Chased", readonly=True, copy=False)
    receivable_outstanding = fields.Monetary(
        string="Owed by the Brand",
        currency_field="currency_id",
        compute="_compute_receivable",
        help="Approved, not yet received nor written off.",
    )
    receivable_age_days = fields.Integer(
        string="Receivable Age (days)", compute="_compute_receivable"
    )
    ageing_bucket = fields.Selection(
        AGEING_BUCKETS,
        string="Ageing Bucket",
        compute="_compute_receivable",
        search="_search_ageing_bucket",
        help="Age of what the brand owes, from its decision (Asia/Dhaka days).",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "brand_fault_codes",
            "labour_minutes",
            "chase_level",
            "last_chased_at",
        }

    # ---- M09-F12: the receivable's age ----------------------------------------
    def _fix_owed(self):
        self.ensure_one()
        if self.state not in RECOVERY_STATES:
            return 0.0
        written = self.written_off_amount if "written_off_amount" in self._fields else 0.0
        return max(
            (self.approved_amount or 0.0) - (self.remittance_amount or 0.0) - (written or 0.0),
            0.0,
        )

    @api.depends("state", "approved_amount", "remittance_amount", "decided_at")
    def _compute_receivable(self):
        today = _today(self.env)
        for claim in self:
            owed = claim._fix_owed()
            day = _dhaka_date(self.env, claim.decided_at)
            age = (today - day).days if owed > 0.005 and day else 0
            claim.receivable_outstanding = owed
            claim.receivable_age_days = max(age, 0)
            claim.ageing_bucket = _bucket(age) if owed > 0.005 and day else False

    def _search_ageing_bucket(self, operator, value):
        if operator != "in":
            return NotImplemented
        wanted = set(value)
        candidates = self.sudo().search(
            [("state", "in", list(RECOVERY_STATES)), ("approved_amount", ">", 0.0)]
        )
        ids = [c.id for c in candidates if c.ageing_bucket in wanted]
        if False in wanted:
            return ["|", ("id", "in", ids), ("id", "not in", candidates.ids)]
        return [("id", "in", ids)]

    @api.model
    def _fix_chase_days(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(PARAM_CHASE_DAYS) or ""
        try:
            days = sorted({int(x) for x in raw.split(",") if x.strip()})
        except ValueError:
            days = []
        return [d for d in days if d > 0] or list(DEFAULT_CHASE_DAYS)

    def _fix_role_holders(self, xmlid):
        self.ensure_one()
        group = self.env.ref(xmlid, raise_if_not_found=False)
        if not group:
            return self.env["res.users"]
        users = group.sudo().all_user_ids.filtered(
            lambda u: u.active and not u.share and self.company_id in u.company_ids
        )
        local = users.filtered(lambda u: self.operating_unit_id in u.operating_unit_ids)
        return (local or users).sorted("id")

    def _fix_chase_assignees(self, level):
        """The claims officer who recorded the decision (else the first in the
        claim's unit); a Finance Manager joins from the second level."""
        self.ensure_one()
        decider = self.decided_by_id.sudo()
        if decider and decider.active and not decider.share and decider.has_group(OFFICER_GROUP):
            users = decider
        else:
            users = self._fix_role_holders(OFFICER_GROUP)[:1]
        if level >= 2:
            users |= self._fix_role_holders(FINANCE_MANAGER_GROUP)[:1]
        return users

    @api.model
    def cron_chase_oem_receivables(self) -> int:
        """AUT-WTY-10 / FR-WTY-050: each decided-but-unpaid OEM receivable is
        chased once per age level it crosses."""
        levels = self._fix_chase_days()
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        now = fields.Datetime.now()
        claims = self.sudo().search(
            [
                ("state", "in", list(RECOVERY_STATES)),
                ("approved_amount", ">", 0.0),
                ("decided_at", "!=", False),
            ],
            order="decided_at",
            limit=2000,
        )
        chased = 0
        for claim in claims:
            owed = claim.receivable_outstanding
            if owed <= 0.005:
                continue
            age = claim.receivable_age_days
            level = sum(1 for d in levels if age >= d)
            if level <= (claim.chase_level or 0):
                continue
            users = claim._fix_chase_assignees(level)
            what = "Chase %s for %s %.2f on claim %s, %d days after its decision (level %d)" % (
                claim.brand_id.name or "the brand",
                claim.currency_id.name or "BDT",
                owed,
                claim.claim_no,
                age,
                level,
            )
            claim.message_post(
                body="%s. %s"
                % (
                    what,
                    "Escalated to finance." if level >= 2 else "The claims officer chases.",
                )
            )
            if todo:
                for user in users:
                    claim.activity_schedule(
                        activity_type_id=todo.id, summary=what[:250], user_id=user.id
                    )
            claim._guarded().write({"chase_level": level, "last_chased_at": now})
            chased += 1
        return chased

    # ---- M09-F13: the brand's rule flags -----------------------------------------
    def _fix_job_work_orders(self):
        self.ensure_one()
        return self.service_order_id.sudo().work_order_ids.filtered(
            lambda w: w.state not in WORK_DONE_EXCLUDED
        )

    def _fix_job_technicians(self):
        self.ensure_one()
        return self.service_order_id.sudo().technician_id | self._fix_job_work_orders().mapped(
            "technician_id"
        )

    def _fix_job_labour_minutes(self) -> int:
        self.ensure_one()
        return int(round(sum(self._fix_job_work_orders().mapped("duration_hours")) * 60.0))

    def _fix_job_fault_codes(self):
        self.ensure_one()
        order = self.service_order_id.sudo()
        codes = []
        for code in order.fault_line_ids.mapped("fault_code") + self._fix_job_work_orders().mapped(
            "diagnosed_fault_code"
        ):
            code = (code or "").strip()
            if code and code.upper() not in [c.upper() for c in codes]:
                codes.append(code)
        return codes

    def _fix_translate_codes(self, codes):
        """{internal: brand} through the M37 brand map, and the codes it lacks."""
        self.ensure_one()
        Map = self.env.get("fix.fault.brand.map")
        if Map is None or not codes:
            return {}, list(codes)
        rows = Map.sudo().search(
            [
                ("brand_id", "=", self.brand_id.id),
                ("fault_id.code", "in", list(set(codes) | {c.upper() for c in codes})),
            ]
        )
        by_code = {r.fault_id.code.upper(): r.brand_code for r in rows}
        found = {c: by_code[c.upper()] for c in codes if c.upper() in by_code}
        return found, [c for c in codes if c.upper() not in by_code]

    def _fix_certification_defects(self):
        self.ensure_one()
        techs = self._fix_job_technicians()
        if not techs:
            return ["no technician is recorded on the job, so certification cannot be shown"]
        Cert = self.env.get("fix.certification")
        if Cert is None:
            return ["M22 certifications are not installed: certified work cannot be shown"]
        day = _dhaka_date(self.env, self.job_completed_at) or _today(self.env)
        defects = []
        for tech in techs:
            certs = Cert.sudo().search(
                [
                    ("employee_id", "=", tech.id),
                    ("state", "=", "valid"),
                    ("issued_on", "<=", day),
                    "|",
                    ("expires_on", "=", False),
                    ("expires_on", ">=", day),
                ]
            )
            if not certs.filtered(
                lambda c: (c.brand_id or c.competency_id.brand_id) == self.brand_id
            ):
                defects.append(
                    "%s held no valid %s certification on %s (BRU-WTY-10)"
                    % (tech.name, self.brand_id.name, day)
                )
        return defects

    def _fix_parts_issues(self):
        self.ensure_one()
        Issue = self.env.get("fix.stock.consumption")
        order = self.service_order_id.sudo()
        if Issue is None or not order.name:
            return self.env["fix.document"].browse()
        return Issue.sudo().search(
            [("service_order_ref", "=", order.name), ("state", "=", "consumed")]
        )

    def _fix_parts_issue_document(self, exclude=()):
        """The M15 issue note of this job's parts: the document filed on one
        of its issues, else one assembled from them (the evidence is
        assembled, not gathered). Empty when nothing was issued."""
        self.ensure_one()
        issues = self._fix_parts_issues()
        if not issues:
            return self.env["fix.document"]
        Doc = self.env["fix.document"].sudo()
        doc = Doc.search(
            [
                ("res_model", "=", "fix.stock.consumption"),
                ("res_id", "in", issues.ids),
                ("id", "not in", list(exclude)),
            ],
            limit=1,
        )
        if doc:
            return doc
        order = self.service_order_id.sudo()
        lines = ["M15 parts issued to %s" % order.name] + [
            "%s | %s %s | qty %s | serial %s | %s"
            % (
                i.name or i.id,
                i.product_id.part_number or "",
                i.product_id.name or "",
                i.quantity,
                i.serial_number or "-",
                i.consumed_at or "",
            )
            for i in issues
        ]
        return Doc.attach(
            name="Parts issued - %s.txt" % order.name,
            datas=base64.b64encode("\n".join(lines).encode()),
            document_type="evidence_pack",
            res_model="fix.stock.consumption",
            res_id=issues[0].id,
        )

    def _fix_parts_evidence_defects(self):
        self.ensure_one()
        issues = self._fix_parts_issues()
        defects = []
        if (self.parts_value or 0.0) > 0.005 and not issues:
            defects.append(
                "it claims parts of %.2f but no part was issued from stock (M15) to %s "
                "(BRU-WTY-09)" % (self.parts_value, self.service_order_id.name)
            )
        item = self.evidence_ids.filtered(lambda e: e.requirement_key == "parts_issued")[:1]
        doc = item.document_id.sudo()
        if (
            doc
            and (issues or (self.parts_value or 0.0) > 0.005)
            and not (doc.res_model == "fix.stock.consumption" and doc.res_id in issues.ids)
        ):
            defects.append(
                "the Parts Issued evidence (%s) is not the M15 issue record of a part "
                "issued to %s: Assemble Evidence files it" % (doc.name, self.service_order_id.name)
            )
        return defects

    def _fix_brand_rule_check(self, rule):
        """(defects, brand codes, labour minutes) of this claim under `rule`."""
        self.ensure_one()
        defects = []
        if rule.requires_certified_technician:
            defects += self._fix_certification_defects()
        minutes = self._fix_job_labour_minutes()
        if rule.labour_allowance_minutes:
            if minutes <= 0:
                defects.append("no labour time is recorded on the job's work orders (BRU-WTY-09)")
            elif minutes > rule.labour_allowance_minutes:
                defects.append(
                    "%d minutes of labour exceeds %s's standard allowance of %d minutes "
                    "(FR-WTY-051)" % (minutes, self.brand_id.name, rule.labour_allowance_minutes)
                )
        codes = self._fix_job_fault_codes()
        found, missing = self._fix_translate_codes(codes)
        scheme = (rule.code_scheme or "").strip()
        if scheme:
            if not codes:
                defects.append(
                    "%s claims under the %s code scheme and the job carries no fault code"
                    % (self.brand_id.name, scheme)
                )
            elif missing:
                defects.append(
                    "no %s %s code for %s (map it on the fault code's brand claim codes, "
                    "FR-WTY-043)" % (self.brand_id.name, scheme, ", ".join(missing))
                )
        if rule.req_parts_issued:
            defects += self._fix_parts_evidence_defects()
        return defects, found, minutes

    def action_submit(self):
        Rule = self.env["fix.brand.claim.rule"]
        plans = {}
        for claim in self:
            if claim.state not in OPEN_STATES:
                continue  # the base refuses it
            _assert_role(self.env, CLERK_GROUP, "Submitting a warranty claim")
            rule = Rule.active_for(claim.brand_id)
            if rule:
                defects, found, minutes = claim._fix_brand_rule_check(rule)
                if defects:
                    raise UserError(
                        "Claim %s breaks %s: %s." % (claim.claim_no, rule.name, "; ".join(defects))
                    )
            else:
                found = claim._fix_translate_codes(claim._fix_job_fault_codes())[0]
                minutes = claim._fix_job_labour_minutes()
            plans[claim.id] = (found, minutes)
        result = super().action_submit()
        for claim in self.filtered(lambda c: c.state == "submitted" and c.id in plans):
            found, minutes = plans[claim.id]
            claim._guarded().write(
                {
                    "brand_fault_codes": ", ".join("%s=%s" % kv for kv in found.items()) or False,
                    "labour_minutes": minutes,
                }
            )
            claim._fix_record_submission("submission")
        return result

    # ---- M09-F16: what was sent to the brand ------------------------------------
    def _fix_record_submission(self, kind, appeal=None):
        self.ensure_one()
        rule = self.env["fix.brand.claim.rule"].active_for(self.brand_id)
        payload = {
            "claim_no": self.claim_no,
            "brand": self.brand_id.code or self.brand_id.name,
            "service_order": self.service_order_id.sudo().name,
            "amount": round(self.claim_amount or 0.0, 2),
            "currency": self.currency_id.name or "BDT",
            "repair_level": self.repair_level,
            "brand_fault_codes": self.brand_fault_codes or "",
            "labour_minutes": self.labour_minutes or 0,
            "evidence": {e.requirement_key: e.evidence_hash or "" for e in self.evidence_ids},
        }
        body = json.dumps(payload, sort_keys=True)
        return (
            self.env["fix.warranty.claim.submission"]
            .sudo()
            .create(
                {
                    "claim_id": self.id,
                    "attempt": len(self.submission_ids) + 1,
                    "kind": kind,
                    "channel": rule.channel if rule else "portal",
                    "submitted_at": fields.Datetime.now(),
                    "submitted_by_id": self.env.uid,
                    "claim_amount": self.claim_amount,
                    "brand_codes": self.brand_fault_codes or False,
                    "payload": body,
                    "payload_sha256": hashlib.sha256(body.encode()).hexdigest(),
                    "appeal_id": appeal.id if appeal else False,
                }
            )
        )

    def _reopen_for_appeal(self, appeal):
        result = super()._reopen_for_appeal(appeal)
        self.sudo()._fix_record_submission("resubmission", appeal)
        return result

    def action_record_brand_reference(self, reference=None):
        """The brand's own reference for the latest submission (a clerk, once)."""
        for claim in self:
            last = claim.submission_ids.sorted("attempt")[-1:]
            if not last:
                raise UserError("Claim %s has not been sent to the brand." % claim.claim_no)
            last.action_record_brand_reference(reference)
        return True


class FixWarrantyClaimSubmission(models.Model):
    """FR-WTY-044/048: one sending of a claim to the brand. Written by the
    submission and resubmission paths only; the brand's reference is added
    once by a clerk."""

    _name = "fix.warranty.claim.submission"
    _description = "Warranty Claim Submission to the Brand"
    _order = "claim_id, attempt"

    claim_id = fields.Many2one(
        "fix.warranty.claim", required=True, index=True, ondelete="cascade", readonly=True
    )
    company_id = fields.Many2one(related="claim_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="claim_id.operating_unit_id", store=True, index=True
    )
    brand_id = fields.Many2one(related="claim_id.brand_id", store=True, index=True)
    currency_id = fields.Many2one(related="claim_id.currency_id")
    attempt = fields.Integer(readonly=True)
    kind = fields.Selection(
        [("submission", "Submission"), ("resubmission", "Resubmission (appeal)")],
        required=True,
        readonly=True,
    )
    channel = fields.Char(readonly=True)
    submitted_at = fields.Datetime(readonly=True)
    submitted_by_id = fields.Many2one("res.users", string="Sent By", readonly=True)
    claim_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    brand_codes = fields.Char(string="Brand Fault Codes", readonly=True)
    payload = fields.Text(string="What Was Sent", readonly=True)
    payload_sha256 = fields.Char(string="Payload SHA-256", readonly=True)
    appeal_id = fields.Many2one("fix.claim.appeal", string="Appeal", readonly=True)
    brand_reference = fields.Char(string="Brand Reference", readonly=True)
    reference_recorded_at = fields.Datetime(readonly=True)
    reference_recorded_by_id = fields.Many2one("res.users", readonly=True)

    @api.depends("claim_id.claim_no", "attempt", "kind")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s #%d (%s)" % (rec.claim_id.claim_no or "?", rec.attempt, rec.kind)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("A submission is recorded by the claim's submission only.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError("A submission is a record of what was sent; it is not edited.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A submission is a record of what was sent; it is not deleted.")
        return super().unlink()

    def action_record_brand_reference(self, reference=None):
        _assert_role(self.env, CLERK_GROUP, "Recording the brand's claim reference")
        ref = (reference or "").strip()
        if not ref:
            raise UserError("Give the brand's reference for the claim.")
        for rec in self:
            if rec.brand_reference:
                raise UserError(
                    "Submission %s already carries the brand's reference %s."
                    % (rec.display_name, rec.brand_reference)
                )
            rec.sudo().write(
                {
                    "brand_reference": ref[:120],
                    "reference_recorded_at": fields.Datetime.now(),
                    "reference_recorded_by_id": self.env.uid,
                }
            )
            rec.claim_id.sudo().message_post(
                body="Brand reference %s recorded for %s." % (ref, rec.display_name)
            )
        return True


class FixClaimAppealResubmissionWindow(models.Model):
    """BRU-WTY-20: a rejected claim is resubmitted within the brand's
    resubmission window, counted from the brand's decision."""

    _inherit = "fix.claim.appeal"

    def _fix_window_defect(self, claim):
        rule = self.env["fix.brand.claim.rule"].active_for(claim.brand_id)
        decided = claim.sudo().decided_at
        if not rule or not rule.resubmission_window_days or not decided:
            return None
        closes = decided + relativedelta(days=rule.resubmission_window_days)
        if fields.Datetime.now() > closes:
            return (
                "%s takes a resubmission within %d days of its decision; claim %s was decided "
                "on %s, so the window closed on %s"
                % (
                    claim.brand_id.name,
                    rule.resubmission_window_days,
                    claim.claim_no,
                    decided,
                    closes,
                )
            )
        return None

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            claim = self.env["fix.warranty.claim"].browse(vals.get("claim_id")).exists()
            defect = claim and self._fix_window_defect(claim)
            if defect:
                raise ValidationError(defect + ".")
        return super().create(vals_list)

    def action_uphold(self, note=None):
        for rec in self:
            defect = self._fix_window_defect(rec.claim_id)
            if defect:
                raise UserError(defect + ": the claim is not resubmitted.")
        return super().action_uphold(note=note)


# ==========================================================================
# M09-F15: per-claim limit, claim count, depreciation, value-band routing
# ==========================================================================
DEPRECIATION_BASIS = [("replace", "Replacement claims only"), ("all", "Every claim")]
PLAN_LIMIT_FIELDS = (
    "per_claim_limit",
    "max_claim_count",
    "depreciation_pct_per_month",
    "depreciation_cap_pct",
    "depreciation_basis",
)


class FixWarrantyProductLimits(models.Model):
    _inherit = "fix.warranty.product"

    per_claim_limit = fields.Monetary(
        string="Per-Claim Limit",
        currency_field="currency_id",
        help="FR-WTY-020: the most the plan pays on one claim (0 = no limit).",
    )
    max_claim_count = fields.Integer(
        string="Claim-Count Limit",
        help="FR-WTY-020: approved claims a policy takes over its term (0 = no limit).",
    )
    depreciation_pct_per_month = fields.Float(
        string="Depreciation (% per month of cover)",
        help="FR-WTY-020: the assessed value is reduced by this per full month between the "
        "cover start and the incident (0 = no depreciation).",
    )
    depreciation_cap_pct = fields.Float(
        string="Depreciation Cap (%)", help="The most depreciation takes off (0 = up to 100%)."
    )
    depreciation_basis = fields.Selection(
        DEPRECIATION_BASIS, string="Depreciation Applies To", default="replace", required=True
    )
    # M37-F5 (with R2-3): catalogue_item_id points at the product.template;
    # this resolves it to its M37 catalogue definition (one item per template).
    catalogue_def_id = fields.Many2one(
        "fix.catalogue.item",
        string="Catalogue Definition (M37)",
        compute="_compute_catalogue_def",
        store=True,
        index=True,
    )

    @api.depends("catalogue_item_id", "catalogue_item_id.catalogue_item_id")
    def _compute_catalogue_def(self):
        for product in self:
            product.catalogue_def_id = product.catalogue_item_id.catalogue_item_id[:1]

    @api.constrains(*PLAN_LIMIT_FIELDS)
    def _check_plan_limits(self):
        for product in self:
            if product.per_claim_limit < 0 or product.max_claim_count < 0:
                raise ValidationError("Claim limits cannot be negative (0 = no limit).")
            for name in ("depreciation_pct_per_month", "depreciation_cap_pct"):
                if not 0.0 <= (product[name] or 0.0) <= 100.0:
                    raise ValidationError(
                        "%s is a percentage between 0 and 100." % product._fields[name].string
                    )


class FixProtectionPolicyPlanLimits(models.Model):
    _inherit = "fix.protection.policy"

    per_claim_limit = fields.Monetary(
        string="Per-Claim Limit", currency_field="currency_id", readonly=True
    )
    max_claim_count = fields.Integer(string="Claim-Count Limit", readonly=True)
    depreciation_pct_per_month = fields.Float(string="Depreciation (%/month)", readonly=True)
    depreciation_cap_pct = fields.Float(string="Depreciation Cap (%)", readonly=True)
    depreciation_basis = fields.Selection(
        DEPRECIATION_BASIS, string="Depreciation Applies To", readonly=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(PLAN_LIMIT_FIELDS)

    def _terms(self, product, start):
        terms = super()._terms(product, start)
        terms.update({name: product[name] for name in PLAN_LIMIT_FIELDS})
        return terms


class _BandDryRun(Exception):
    pass


class FixProtectionClaimBand(models.Model):
    _name = "fix.protection.claim"
    # the approvable mixin FIRST (it sits in front of the guard mixin; the other
    # order gives Python no consistent method order - see fix.dofa.mixin)
    _inherit = ["fix.approvable.mixin", "fix.protection.claim"]

    # FR-WTY-030: above a value band the decision is routed through M63 at
    # the band's DOFA tier; below every band (and with no band configured)
    # the Claim Decision Officer decides as before.
    _approval_domain = "protection_claim_decision"
    _approval_apply_method = "action_apply_band_approval"
    _approval_group = OFFICER_GROUP
    _approval_routed = True

    depreciation_amount = fields.Monetary(
        string="Depreciation", currency_field="currency_id", readonly=True, copy=False
    )
    payable_note = fields.Char(string="How the Payable Was Reached", readonly=True, copy=False)
    dofa_band_tier = fields.Char(string="Value-Band Tier", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "depreciation_amount",
            "payable_note",
            "dofa_band_tier",
        }

    # ---- the payable --------------------------------------------------------
    def _fix_payable_breakdown(self):
        self.ensure_one()
        policy = self.policy_id.sudo()
        value = self.assessed_value or 0.0
        pct = dep = 0.0
        rate = policy.depreciation_pct_per_month or 0.0
        if (
            rate
            and self.incident_date
            and policy.term_start
            and (policy.depreciation_basis == "all" or self.remedy == "replace")
        ):
            delta = relativedelta(self.incident_date, policy.term_start)
            months = max(delta.years * 12 + delta.months, 0)
            pct = min(rate * months, policy.depreciation_cap_pct or 100.0)
            dep = round(value * pct / 100.0, 2)
        payable = max(round(value - dep - (self.excess_amount or 0.0), 2), 0.0)
        cap = policy.per_claim_limit or 0.0
        capped = bool(cap and payable > cap + 0.005)
        if capped:
            payable = cap
        notes = ["assessed %.2f" % value]
        if dep:
            notes.append("less depreciation %.2f (%.1f%%)" % (dep, pct))
        if self.excess_amount:
            notes.append("less excess %.2f" % self.excess_amount)
        if capped:
            notes.append("capped at the per-claim limit %.2f" % cap)
        return {
            "payable": payable,
            "depreciation": dep,
            "note": "; ".join(notes) + " = %.2f" % payable,
        }

    def _fix_payable(self):
        return self._fix_payable_breakdown()["payable"]

    # ---- value bands (OWNER configures) ------------------------------------
    @api.model
    def _fix_bands(self):
        raw = (self.env["ir.config_parameter"].sudo().get_param(PARAM_BANDS) or "").strip()
        bands = []
        for part in [p.strip() for p in raw.split(",") if p.strip()]:
            try:
                amount, tier = part.split(":")
                amount, tier = float(amount), tier.strip()
            except ValueError:
                amount, tier = -1.0, ""
            if amount < 0 or tier not in TIER_GROUP:
                raise UserError(
                    "%s is malformed (%r): write 'amount:tier_n' pairs, e.g. "
                    "'50000:tier_1,200000:tier_2'." % (PARAM_BANDS, part)
                )
            bands.append((amount, tier))
        return sorted(bands)

    def _fix_band_tier(self, amount):
        tier = False
        for threshold, band_tier in self._fix_bands():
            if amount + 0.005 >= threshold:
                tier = band_tier
        return tier

    def _approval_amount(self) -> float:
        self.ensure_one()
        return self._fix_payable()

    def _approval_tier(self):
        self.ensure_one()
        return self._fix_band_tier(self._fix_payable())

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.state == "assessed" and bool(self._approval_tier())

    def _approval_excluded(self):
        return super()._approval_excluded() | self.assessed_by_id.sudo()

    # ---- the decision -------------------------------------------------------
    def _fix_check_claim_count(self):
        for claim in self:
            policy = claim.policy_id.sudo()
            if not policy.max_claim_count:
                continue
            used = policy.claim_ids.filtered(
                lambda c, me=claim: c.id != me.id and c.state in ("approved", "settled")
            )
            if len(used) >= policy.max_claim_count:
                raise UserError(
                    "Policy %s has paid or approved %d claim(s), its claim-count limit "
                    "(FR-WTY-020): %s is not approved." % (policy.name, len(used), claim.name)
                )

    def _fix_stamp_payable(self):
        for claim in self.filtered(lambda c: c.state == "approved"):
            info = claim._fix_payable_breakdown()
            claim._guarded().write(
                {"depreciation_amount": info["depreciation"], "payable_note": info["note"][:250]}
            )

    def _fix_dry_run_approve(self):
        """Every approval rule, run as the officer and rolled back."""
        try:
            with self.env.cr.savepoint():
                super(
                    FixProtectionClaimBand, self.with_context(**{CTX_BAND_APPROVED: True})
                ).action_approve()
                raise _BandDryRun()
        except _BandDryRun:
            pass
        self.env.invalidate_all()

    def action_approve(self):
        self._fix_check_claim_count()
        if self.env.context.get(CTX_BAND_APPROVED):
            result = super().action_approve()
            self._fix_stamp_payable()
            return result
        routed = self.filtered(
            lambda c: c.state == "assessed" and c._fix_band_tier(c._fix_payable())
        )
        if routed:
            self._decider("Approving a protection claim")
            for claim in routed:
                if claim.approval_state == "pending":
                    raise UserError("%s is already awaiting its value-band approval." % claim.name)
                claim._fix_dry_run_approve()
                payable = claim._fix_payable()
                tier = claim._fix_band_tier(payable)
                claim._guarded().write({"dofa_band_tier": tier})
                claim.action_request_approval(
                    justification="Protection claim %s: the plan would pay %.2f, in the %s value "
                    "band (FR-WTY-030)." % (claim.name, payable, tier)
                )
        rest = self - routed
        if rest:
            super(FixProtectionClaimBand, rest).action_approve()
            rest._fix_stamp_payable()
        return True

    def action_apply_band_approval(self):
        """The M63 apply method: the tier holder's approval completes the
        officer's decision (the officer requested it and does not decide it)."""
        self._approval_assert_routed()
        for claim in self:
            if claim.state != "assessed":
                raise UserError("%s is %s: nothing to approve." % (claim.name, claim.state))
        return self.sudo().with_context(**{CTX_BAND_APPROVED: True}).action_approve()


class FixApprovalMatrixProtectionClaim(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("protection_claim_decision", "Protection Claim (value band)")],
        ondelete={"protection_claim_decision": "cascade"},
    )
