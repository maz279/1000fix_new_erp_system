# cd_contract_core — M08 Contract Lifecycle Management (P07-M01, CD-M08-nn).
#
# All product families on one engine: AMC, RAMC, managed services, rental,
# marketplace. The entitlement model is the heart (T03): what a contract
# BUYS and how consumption draws it down — M01's W1 order-category gate
# (AMC) consumes `entitlement_active()` from here.
#
# T08 (AR-008 §2.2): fix.contract.cost multi-owned by M08/M53/M54 —
# ruling: M08 OWNS it; M53/M54 consume via events, never directly.
#
# A04 build (2026-11-04), C2-C10: the contract `state` could be typed from
# draft to active (no signature, no value approval, no stamp duty), the only
# working activation path died on an OCA AccessError, and a BDT 50M contract
# was activated by its own creator. The lifecycle is now Oracle's status
# model: Draft -> Pending Approval (DOFA on the contract value, routed through
# M63, plus Legal review above a threshold) -> Pending Signature (a completed
# M24 envelope the customer signed) -> Active. Every state, approval and
# evidence field is guarded, and the commercial terms freeze once the
# contract leaves Draft: a value change on a live contract is an amendment.
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

FAMILIES = [
    ("amc", "AMC (Annual Maintenance)"),
    ("ramc", "RAMC (Repair & Maintenance)"),
    ("managed", "Managed Services"),
    ("rental", "Rental"),
    ("marketplace", "Marketplace Agreement"),
]

# A04 ERP audit M08-F8 (20 Nov 2026): the spec names 14 product families and
# the workspace said so, while the engine carries these five. The registry is
# the one place a family's behaviour is read from (cover, order category of
# its work, revenue role, PM interval), so a new family is a selection_add plus
# one row here - and the screens list what the registry holds, nothing more.
#   covers_assets   its work on a covered device is contract work (M01 order
#                   category "amc" = "AMC / Contract"), drawing entitlement
#   revenue_role    cd_billing_engine.account_code.contract_revenue_<role>
CONTRACT_FAMILY_PROFILES = {
    "amc": {"covers_assets": True, "revenue_role": "amc", "pm_interval": 90},
    "ramc": {"covers_assets": True, "revenue_role": "ramc", "pm_interval": 120},
    "managed": {"covers_assets": True, "revenue_role": "managed", "pm_interval": 30},
    "rental": {"covers_assets": True, "revenue_role": "rental", "pm_interval": 180},
    "marketplace": {"covers_assets": False, "revenue_role": "marketplace", "pm_interval": 0},
}
COVER_FAMILIES = tuple(k for k, v in CONTRACT_FAMILY_PROFILES.items() if v["covers_assets"])


def family_profile(family):
    """The registry row of a family (an unknown family covers nothing)."""
    return CONTRACT_FAMILY_PROFILES.get(
        family or "", {"covers_assets": False, "revenue_role": "other", "pm_interval": 0}
    )


CONTRACT_STATES = [
    ("draft", "Draft"),
    ("pending_approval", "Pending Approval"),
    ("pending_signature", "Pending Signature"),
    ("active", "Active"),
    ("expiring", "Expiring Soon"),
    ("expired", "Expired"),
    ("suspended", "Suspended"),
    ("terminated", "Terminated"),
]
# The states in which a contract is in force: it covers devices, consumes
# entitlement and can be amended, suspended or terminated.
IN_FORCE = ("active", "expiring")

# A04 build (2026-11-04): BUSINESS DEFAULTS THE BUSINESS MUST CONFIRM (§7
# decision 2, "contract value thresholds, and which contracts need legal
# review"). Until it rules, the contract-value ladder reuses the closest
# commercial ladder in the estate (the A05 rental damage-waiver ladder:
# Tier 1 to BDT 50k, Tier 2 to 250k, Tier 3 to 1M, Tier 4 above), and Legal
# reviews any contract from BDT 1M and every managed-services, rental and
# marketplace agreement (their terms carry liability and title clauses).
CONTRACT_VALUE_DOFA_THRESHOLDS = [
    (50000.0, "tier_1"),
    (250000.0, "tier_2"),
    (1000000.0, "tier_3"),
    (float("inf"), "tier_4"),
]
LEGAL_REVIEW_THRESHOLD_BDT = 1000000.0
LEGAL_REVIEW_FAMILIES = ("managed", "rental", "marketplace")
# Switch: a contract must be drafted from a Legal-signed template. fix_dev
# holds 6 templates and none is signed off, so requiring it on deploy would
# stop every new contract: the safe-for-deploy default is OFF ("0").
REQUIRE_TEMPLATE_PARAM = "cd_contract_core.require_template"
# AUT-015 escalation ladder (days before the term ends).
EXPIRY_WINDOWS = (90, 60, 30, 15)

OFFICER = "cd_contract_core.group_contract_officer"
MANAGER = "cd_contract_core.group_contract_manager"
LEGAL = "cd_contract_core.group_contract_legal"
# The stamp-duty exemption is a Finance decision (Stamp Act 1899 Schedule I).
FINANCE = "account.group_account_manager"

# The commercial terms of a contract. Editable in Draft only; afterwards they
# change through an approved amendment (A04 build, M08-7).
CONTRACT_TERM_FIELDS = frozenset(
    {
        "name",
        "family",
        "customer_id",
        "company_id",
        "operating_unit_id",
        "currency_id",
        "annual_value",
        "term_value",
        "accepted_total",
        "billing_frequency",
        "billing_timing",
        "retention_pct",
        "ld_rate_pct_per_day",
        "ld_cap_pct",
        "escalation_pct",
        "date_start",
        "date_end",
        "covered_device_ids",
        "entitlement_ids",
        "sla_policy_ids",
        "template_id",
        "stamp_duty_cert_no",
        "stamp_duty_amount",
        "stamp_act_article",
        "stamp_duty_applicable",
        "stamp_duty_exemption_reason",
        "has_signed_contract_doc",
    }
)
# The envelope is attached once the contract is approved, so it stays
# editable until the contract is signed and active.
ENVELOPE_EDITABLE_STATES = ("draft", "pending_approval", "pending_signature")


def require_role(env, xmlid, what):
    """Refuse unless the acting user holds the role (superuser code is
    trusted). UserError, not AccessError: the refusal is a business rule the
    workspace shows, not a crash."""
    if env.su or env.user.has_group(xmlid):
        return
    group = env.ref(xmlid, raise_if_not_found=False)
    raise UserError(
        "%s needs the '%s' role, which you do not hold."
        % (what, group.sudo().name if group else xmlid)
    )


class FixContract(models.Model):
    """A contract across any product family, on the party kernel."""

    _name = "fix.contract"
    _description = "Contract"
    # fix.dofa.mixin brings the M63 approvable mixin and the field guard.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "date_start desc, id desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint("UNIQUE (code)", "Contract code must be unique")

    # A04 build (2026-11-04) C4/C9: the contract value is approved under DOFA,
    # routed through the M63 inbox, never by the record's own button.
    _approval_domain = "contract_value"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    code = fields.Char(string="Contract No.", required=True, readonly=True, index=True, copy=False)
    name = fields.Char(string="Title", required=True, tracking=True)
    family = fields.Selection(FAMILIES, string="Product Family", required=True, tracking=True)
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True, ondelete="restrict"
    )
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True, help="The term end — renewal extends or replaces this")
    state = fields.Selection(
        CONTRACT_STATES, default="draft", required=True, tracking=True, readonly=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # T08: contract cost owned HERE (M53/M54 consume via events)
    annual_value = fields.Monetary(
        string="Annual Value", currency_field="currency_id", required=True
    )
    # A04 ERP audit M36-F3 / M08-F6 (20 Nov 2026): the contract carries the
    # price of its WHOLE term (what the customer accepted, before VAT) and how
    # it is billed. The schedule bills calendar-month periods at
    # annual_value / 12 a month and the last period of the term absorbs the
    # rounding, so the periods total term_value exactly (a 6-month quote of
    # 120,000 bills 120,000, not 119,013.70 on a days/365 basis).
    term_value = fields.Monetary(
        string="Term Value (excl. VAT)",
        currency_field="currency_id",
        copy=False,
        help="The contract's price for its whole term, before VAT. Set from the "
        "accepted quotation or tender; otherwise the annual value over the term.",
    )
    accepted_total = fields.Monetary(
        string="Accepted Total (incl. VAT)",
        currency_field="currency_id",
        copy=False,
        help="What the customer accepted including VAT (quotation / tender award). "
        "The contract's invoices over the term never exceed it.",
    )
    billing_frequency = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("semiannual", "Half-yearly"),
            ("annual", "Annually"),
        ],
        default="monthly",
        required=True,
    )
    billing_timing = fields.Selection(
        [("arrears", "In arrears (period end)"), ("advance", "In advance (period start)")],
        default="arrears",
        required=True,
    )
    escalation_pct = fields.Float(
        string="Annual Escalation (%)",
        default=0.0,
        help="Applied at renewal (T05): next-term value = value * (1 + pct/100)",
    )
    # A04 ERP audit M08-F17: auto-renew defaulted ON, so every contract drafted
    # its next term silently at lead time (and that draft blocked the M36
    # renewal quotation). Renewing is a decision: off unless chosen.
    auto_renew = fields.Boolean(
        default=False, help="AUT-015: the next term is drafted at lead time"
    )
    renewal_lead_days = fields.Integer(
        default=90, help="AUT-015: −90/−60/−30/−15 escalation ladder"
    )
    # copy=True: entitlements carry into a renewal term (T05) — a One2many
    # is not copied by default; quantity_consumed is copy=False, so the
    # renewed term starts with its full included quantity
    entitlement_ids = fields.One2many(
        "fix.contract.entitlement", "contract_id", string="Entitlements", copy=True
    )
    sla_policy_ids = fields.Many2many(
        "fix.sla.policy",
        string="Contract SLAs",
        help="T04: contract SLAs reference the SAME policy model as M01's service "
        "SLAs — one SLA concept, two scopes, not two implementations",
    )
    covered_device_ids = fields.Many2many(
        "fix.device",
        string="Covered Assets",
        help="BRU-SRM-03: an AMC order can only be created if the device is on "
        "an ACTIVE contract's covered-asset list",
    )
    esignature_envelope_id = fields.Many2one(
        "fix.esignature.envelope",
        string="E-Signature",
        copy=False,
        help="T07: through M24's kernel envelope, never a local implementation",
    )
    oca_contract_id = fields.Many2one(
        "contract.contract",
        string="OCA Contract Reference",
        copy=False,
        readonly=True,
        help="T01: Rebuilt on OCA contract (12 modules) for recurring accounting, lines, and billing",
    )
    template_id = fields.Many2one(
        "fix.contract.template",
        string="Contract Template",
        ondelete="restrict",
        help="The Legal-signed wording this contract is issued on. A template "
        "that is not ready to issue blocks submission.",
    )

    # --- approval, legal review and activation evidence (A04 build) -------
    legal_review_required = fields.Boolean(
        compute="_compute_legal_review_required",
        store=True,
        help="Contracts from BDT %s and every managed-services, rental and "
        "marketplace agreement are reviewed by Legal before signature."
        % f"{LEGAL_REVIEW_THRESHOLD_BDT:,.0f}",
    )
    legal_reviewed_by = fields.Many2one(
        "res.users", string="Legal Review By", readonly=True, copy=False, tracking=True
    )
    legal_reviewed_on = fields.Datetime(readonly=True, copy=False)
    legal_review_note = fields.Text(readonly=True, copy=False)
    activated_by = fields.Many2one("res.users", readonly=True, copy=False)
    activated_on = fields.Datetime(readonly=True, copy=False)
    renewed_from_id = fields.Many2one(
        "fix.contract",
        string="Renewal Of",
        readonly=True,
        copy=False,
        index=True,
        ondelete="set null",
        help="The term this contract renews. The earlier term stays in force "
        "until its own end date (A04 build, M08-10).",
    )
    renewal_ids = fields.One2many("fix.contract", "renewed_from_id", string="Renewal Terms")
    amendment_ids = fields.One2many("fix.contract.amendment", "contract_id", string="Amendments")
    amendment_version = fields.Integer(
        string="Amendment Version",
        readonly=True,
        copy=False,
        default=0,
        help="Incremented by every applied amendment: version 0 is the signed contract.",
    )
    billed_through_date = fields.Date(
        string="Billed Through",
        readonly=True,
        copy=False,
        help="The last day already invoiced. An amendment cannot take effect "
        "inside a billed period (the billed-period freeze); set only by the "
        "M20 billing hand-off (mark_billed_through).",
    )
    expiry_notified_window = fields.Integer(
        readonly=True,
        copy=False,
        help="The smallest AUT-015 window (days) already announced, so the "
        "daily job publishes each window once.",
    )

    # Statutory Stamp Duty (Stamp Act 1899) & Legal Documentation (FLAW-08.2)
    stamp_duty_cert_no = fields.Char(
        string="Stamp Duty Certificate No.",
        tracking=True,
        copy=False,
        help="Stamp Act 1899 Schedule I compliance certificate number",
    )
    stamp_duty_amount = fields.Monetary(
        string="Stamp Duty Paid", currency_field="currency_id", tracking=True, copy=False
    )
    stamp_act_article = fields.Selection(
        [
            ("art_5", "Article 5 - Agreement / Memorandum"),
            ("art_15", "Article 15 - Bond / Guarantee"),
            ("art_35", "Article 35 - Lease / Hire"),
        ],
        string="Stamp Act Article",
        default="art_5",
        tracking=True,
    )
    has_signed_contract_doc = fields.Boolean(
        string="Signed Contract PDF Attached",
        default=False,
        tracking=True,
        copy=False,
        help="Set at activation from the completed e-signature envelope's "
        "document. A hand-ticked box opens nothing: activation reads the "
        "envelope itself (A04 build, M08-14).",
    )
    stamp_duty_applicable = fields.Boolean(
        string="Chargeable Under Schedule I",
        default=True,
        tracking=True,
        help="Whether this instrument is chargeable with stamp duty under "
        "Stamp Act 1899 Schedule I. Clearing it requires a recorded reason "
        "and a Finance approver: an exemption is a decision somebody owns, "
        "not a silent skip.",
    )
    stamp_duty_exemption_reason = fields.Char(
        string="Non-Chargeable Reason",
        tracking=True,
        help="Why this instrument is not chargeable (e.g. not an instrument "
        "within Schedule I, or duty discharged on a parent master agreement).",
    )
    stamp_exemption_requested_by = fields.Many2one(
        "res.users", string="Exemption Proposed By", readonly=True, copy=False
    )
    stamp_exemption_approved_by = fields.Many2one(
        "res.users", string="Exemption Approved By", readonly=True, copy=False, tracking=True
    )
    stamp_exemption_approved_on = fields.Datetime(readonly=True, copy=False)

    # Delivery Cost Tracking & True Gross Margin (FLAW-08.1)
    total_delivery_cost = fields.Monetary(
        string="Total Delivery & Service Cost",
        currency_field="currency_id",
        compute="_compute_delivery_cost",
        store=True,
    )
    contract_margin_bdt = fields.Monetary(
        string="Gross Contract Margin",
        currency_field="currency_id",
        compute="_compute_delivery_cost",
        store=True,
    )
    contract_margin_pct = fields.Float(
        string="Gross Margin (%)",
        compute="_compute_delivery_cost",
        store=True,
    )

    service_order_ids = fields.One2many("fix.service.order", "contract_id", string="Work Delivered")
    pm_visit_ids = fields.One2many(
        "fix.contract.pm.visit", "contract_id", string="Preventive Maintenance Visits"
    )
    delivered_order_count = fields.Integer(
        string="Orders Delivered", compute="_compute_delivery_cost", store=True
    )

    # ---- guard -------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "oca_contract_id",
            "legal_reviewed_by",
            "legal_reviewed_on",
            "legal_review_note",
            "activated_by",
            "activated_on",
            "renewed_from_id",
            "amendment_version",
            "billed_through_date",
            "expiry_notified_window",
            "stamp_exemption_requested_by",
            "stamp_exemption_approved_by",
            "stamp_exemption_approved_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= CONTRACT_TERM_FIELDS
            if self.state not in ENVELOPE_EDITABLE_STATES:
                locked.add("esignature_envelope_id")
        return locked

    # ---- DOFA: the contract value -------------------------------------------
    # A04 ERP audit M08-F12: the value approved and reviewed is the TOTAL
    # contract value (the whole term), not one year of it: a 3-year 2.7M
    # contract was tested as 900k and skipped Legal.
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return abs(self._fix_term_value())

    def _dofa_thresholds(self):
        return CONTRACT_VALUE_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (total contract value over the term)" % self._dofa_amount()

    @api.depends("annual_value", "term_value", "date_start", "date_end")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    @api.depends("annual_value", "term_value", "date_start", "date_end", "family")
    def _compute_legal_review_required(self):
        for rec in self:
            rec.legal_review_required = bool(
                rec._fix_term_value() >= LEGAL_REVIEW_THRESHOLD_BDT
                or rec.family in LEGAL_REVIEW_FAMILIES
            )

    def _fix_term_value(self) -> float:
        """The total contract value (excl. VAT): the stored term value, else
        the annual value over the term on the calendar-month basis."""
        self.ensure_one()
        if self.term_value:
            return self.term_value
        if not (self.date_start and self.date_end):
            return self.annual_value or 0.0
        return round(self._fix_fee_between(self.date_start, self.date_end, suspended=False), 2)

    @api.depends(
        "annual_value",
        "term_value",
        "service_order_ids.delivery_cost_bdt",
        "pm_visit_ids.service_order_id.delivery_cost_bdt",
    )
    def _compute_delivery_cost(self):
        """FLAW-08.1: true contract P&L.

        This used to read `delivery_cost = 0.0`, hard-coded, so every contract
        reported its full annual value as margin — a 100% margin on every row
        (A04 audit, 2026-10-31). Cost is now the parts and labour actually
        consumed by the work delivered under the contract, reached two ways:
        orders booked directly against it, and orders raised to service its
        preventive-maintenance visits. The two sets are unioned, because a PM
        visit's order may also carry the contract link.
        """
        for contract in self:
            orders = contract.service_order_ids
            pm_orders = contract.pm_visit_ids.mapped("service_order_id")
            delivered = orders | pm_orders
            delivery_cost = sum(delivered.mapped("delivery_cost_bdt"))
            contract.delivered_order_count = len(delivered)
            contract.total_delivery_cost = delivery_cost
            # A04 ERP audit M08-F13: the cost is every order of the contract's
            # life, so the revenue it is set against is the whole term's value
            # (one year's revenue against lifetime cost understated the margin).
            revenue = contract.term_value or contract.annual_value or 0.0
            net_val = revenue - delivery_cost
            contract.contract_margin_bdt = net_val
            contract.contract_margin_pct = round((net_val / revenue) * 100.0, 2) if revenue else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # The article follows the instrument. The UI gets this from the
            # onchange; records created in code (imports, conversions, tests)
            # would otherwise keep the art_5 default and fail the constraint
            # on a rental.
            if not vals.get("stamp_act_article") and vals.get("family"):
                suggested = self._FAMILY_ARTICLE.get(vals["family"])
                if suggested:
                    vals["stamp_act_article"] = suggested
            if not vals.get("code"):
                vals["code"] = self.env["ir.sequence"].next_by_code("fix.contract") or (
                    "CTR/%s" % fields.Date.context_today(self)
                )
        records = super().create(vals_list)
        if not self.env.su:
            # A04 build (M08-14): who proposed an exemption cannot approve it.
            proposed = records.filtered(lambda r: not r.stamp_duty_applicable)
            if proposed:
                proposed._guarded().write({"stamp_exemption_requested_by": self.env.uid})
        return records

    def _fix_drop_token(self):
        """The records, outside the guard token a transition used to make them."""
        ctx = dict(self.env.context)
        ctx.pop("fix_guarded_transition", None)
        return self.with_context(ctx)

    def write(self, vals):
        """A04 build (2026-11-04) C2: the commercial terms freeze once the
        contract leaves Draft; the envelope once it is signed. A live
        contract's value moves only through an approved amendment."""
        if self and not self._fix_guard_open():
            names = set(vals) & (CONTRACT_TERM_FIELDS | {"esignature_envelope_id"})
            for rec in self:
                frozen = set()
                if rec.state != "draft":
                    frozen |= names & CONTRACT_TERM_FIELDS
                if rec.state not in ENVELOPE_EDITABLE_STATES and "esignature_envelope_id" in names:
                    frozen.add("esignature_envelope_id")
                changed = [n for n in frozen if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed:
                    labels = ", ".join(sorted(rec._fields[n].string or n for n in changed))
                    raise UserError(
                        "%s of contract %s cannot be changed: it is %s. A signed or "
                        "submitted contract changes through an approved amendment "
                        "(or Reset to Draft before it is signed)."
                        % (labels, rec.code, dict(CONTRACT_STATES)[rec.state])
                    )
            exemption = {"stamp_duty_applicable", "stamp_duty_exemption_reason"} & set(vals)
            if exemption:
                moved = self.filtered(
                    lambda r: any(r._fix_guard_differs(n, vals[n], r[n]) for n in exemption)
                )
                result = super().write(vals)
                if moved:
                    # A changed exemption is a new proposal: the old approval
                    # covered other words, and its proposer cannot approve it.
                    moved._guarded().write(
                        {
                            "stamp_exemption_requested_by": self.env.uid,
                            "stamp_exemption_approved_by": False,
                            "stamp_exemption_approved_on": False,
                        }
                    )
                return result
        return super().write(vals)

    @api.constrains("date_start", "date_end")
    def _check_term(self):
        for contract in self:
            if contract.date_end <= contract.date_start:
                raise UserError("The term end must be after the start")

    @api.constrains("annual_value")
    def _check_value(self):
        for contract in self:
            if (contract.annual_value or 0.0) < 0:
                raise ValidationError("A contract value cannot be negative.")

    # ---- helpers -------------------------------------------------------------
    def _contract_require_state(self, allowed, what):
        labels = dict(CONTRACT_STATES)
        for rec in self:
            if rec.state not in allowed:
                raise UserError(
                    "Contract %s cannot %s: it is %s (it must be %s)."
                    % (
                        rec.code,
                        what,
                        labels.get(rec.state, rec.state),
                        " or ".join(labels[s] for s in allowed),
                    )
                )

    def _contract_in_force_on(self, day):
        self.ensure_one()
        return bool(
            self.state in IN_FORCE
            and self.date_start
            and self.date_end
            and self.date_start <= day <= self.date_end
        )

    def _contract_legal_cleared(self) -> bool:
        self.ensure_one()
        return bool(not self.legal_review_required or self.legal_reviewed_by)

    def _contract_template_check(self):
        required = (
            self.env["ir.config_parameter"].sudo().get_param(REQUIRE_TEMPLATE_PARAM, "0") == "1"
        )
        for rec in self:
            if rec.template_id:
                rec.template_id.sudo().assert_publishable()
            elif required:
                raise UserError(
                    "Contract %s must be issued on a Legal-signed contract template." % rec.code
                )

    def action_sync_oca_contract(self):
        """T01: Synchronises with underlying OCA contract.contract record.

        A04 build (M08-2): the OCA record is an accounting side effect of a
        contract that has already passed its checks. It used to be created
        under the user's own ACL, so activation died with an AccessError for
        everyone but an Accounting Administrator. It now runs as a service,
        after the caller's role and the contract's state are checked."""
        require_role(self.env, OFFICER, "Synchronising the OCA contract")
        if not self.env.su:
            self._contract_require_state((*IN_FORCE, "suspended"), "be synchronised to OCA")
        Contract = self.env["contract.contract"].sudo()
        for contract in self:
            vals = {
                "name": contract.name,
                "partner_id": contract.customer_id.id,
                "company_id": contract.company_id.id,
                "date_start": contract.date_start,
                "date_end": contract.date_end,
                "code": contract.code,
            }
            # A04 ERP audit M08-F22: the OCA record is a reference only. M08's
            # own walker bills the contract through M20; an ACTIVE OCA contract
            # sat in the scope of OCA's recurring-invoice cron, so a line added
            # to it would bill the customer a second time. It is kept archived.
            vals["active"] = False
            if contract.oca_contract_id:
                contract.oca_contract_id.sudo().with_context(active_test=False).write(vals)
            else:
                contract.sudo()._guarded().write({"oca_contract_id": Contract.create(vals).id})
        return True

    def action_price_revision(self, new_annual_value: float, revision_reason: str = ""):
        """T01: Mid-term price revision / renegotiation.

        A04 build (M08-7/8): this wrote the new value straight onto an active
        contract (1.2M -> 1, no approval). A revision of a live contract is
        now a pricing AMENDMENT that is approved under DOFA on the change and
        applied by the approval; a draft contract is simply edited. Returns
        the amendment (trusted service code applies it at once)."""
        require_role(self.env, OFFICER, "A price revision")
        Amendment = self.env["fix.contract.amendment"]
        amendments = Amendment.browse()
        for contract in self:
            if contract.state not in ("draft", *IN_FORCE):
                raise UserError(
                    "Price revision can only be applied to active, expiring, or draft contracts"
                )
            if new_annual_value <= 0:
                raise UserError("Revised annual value must be strictly positive")
            if contract.state == "draft":
                # a draft is still being negotiated: its value is simply edited
                old_value = contract.annual_value
                contract.write({"annual_value": new_annual_value})
                contract.message_post(
                    body=f"Annual value revised from {old_value} to {new_annual_value}. "
                    f"Reason: {revision_reason}"
                )
                publish(
                    self.env,
                    "contract.price_revised",
                    "fix.contract",
                    contract.id,
                    {
                        "code": contract.code,
                        "old_annual_value": old_value,
                        "new_annual_value": new_annual_value,
                        "reason": revision_reason,
                    },
                )
                continue
            amendment = Amendment.create(
                {
                    "name": "Price revision %s" % (revision_reason or contract.code),
                    "contract_id": contract.id,
                    "kind": "pricing",
                    "delta_value": round(new_annual_value - contract.annual_value, 2),
                    "effective_from": max(
                        fields.Date.context_today(self),
                        (contract.billed_through_date or contract.date_start)
                        + timedelta(days=1 if contract.billed_through_date else 0),
                    ),
                    "note": revision_reason,
                }
            )
            if self.env.su:
                amendment._amendment_apply()
            amendments |= amendment
        return amendments or True

    def reconcile_service_sla(self, service_order=None) -> dict:
        """T01: Contract-vs-service SLA reconciliation (one concept, two scopes).
        Determines the effective SLA terms for a service order against the
        contract's policies, ensuring contract entitlements take precedence."""
        self.ensure_one()
        # fix.sla.policy's targets are `response_hours`/`resolution_hours`
        # (all required); reading them directly - a getattr() on the old
        # `*_time_hours` names always fell back to 4h/24h, ignoring the
        # contract's actual SLA.
        matched_policies = [
            {
                "policy_id": policy.id,
                "policy_name": policy.name,
                "response_time_hours": policy.response_hours,
                "resolution_time_hours": policy.resolution_hours,
                "priority_override": policy.priority,
            }
            for policy in self.sla_policy_ids
        ]
        return {
            "contract_id": self.id,
            "contract_code": self.code,
            "reconciled": bool(matched_policies),
            "effective_policies": matched_policies,
            "priority": matched_policies[0]["priority_override"]
            if matched_policies
            else "standard",
            "max_response_hours": min(
                (p["response_time_hours"] for p in matched_policies), default=8.0
            ),
            "max_resolution_hours": min(
                (p["resolution_time_hours"] for p in matched_policies), default=48.0
            ),
        }

    # Which Schedule I head a contract falls under follows from what kind of
    # instrument it is. The VALUE thresholds do not: they move with each
    # Finance Act and are not encoded here — an audit is not the place to
    # invent a rate. What this does is stop the article being a silent default
    # that contradicts the contract it sits on.
    _FAMILY_ARTICLE = {
        "amc": "art_5",  # agreement / memorandum
        "ramc": "art_5",
        "managed": "art_5",
        "rental": "art_35",  # lease / hire
        "marketplace": "art_5",
    }

    @api.onchange("family")
    def _onchange_family_sets_article(self):
        for rec in self:
            suggested = rec._FAMILY_ARTICLE.get(rec.family)
            if suggested:
                rec.stamp_act_article = suggested

    @api.constrains("family", "stamp_act_article", "stamp_duty_applicable")
    def _check_article_matches_instrument(self):
        """A rental contract stamped as an Article 5 agreement is a filing
        error waiting to be found by an inspector. The article defaults to
        art_5 for every family, so a rental silently carried the wrong head
        (A04 audit, 2026-11-01)."""
        for rec in self:
            if not rec.stamp_duty_applicable:
                continue
            expected = rec._FAMILY_ARTICLE.get(rec.family)
            if expected and rec.stamp_act_article != expected:
                labels = dict(rec._fields["stamp_act_article"].selection)
                raise ValidationError(
                    "Stamp Act article mismatch on %s: a '%s' contract is "
                    "chargeable under %s, not %s. Correct the article, or "
                    "record why this instrument is classified differently."
                    % (
                        rec.code or "this contract",
                        dict(FAMILIES).get(rec.family, rec.family),
                        labels.get(expected, expected),
                        labels.get(rec.stamp_act_article, rec.stamp_act_article),
                    )
                )

    def _stamp_duty_due(self) -> float:
        """The duty Schedule I charges on this instrument, from the confirmed
        rate in force on the start date; 0.0 when no confirmed rate exists
        (the amount cannot be checked, though the certificate still can)."""
        self.ensure_one()
        row = self.env["fix.stamp.duty.schedule"].rate_for(
            self.stamp_act_article, on_date=self.date_start, company=self.company_id
        )
        if not row:
            return 0.0
        return round(
            (row.duty_fixed_bdt or 0.0)
            + (self.annual_value or 0.0) * (row.duty_rate_pct or 0.0) / 100.0,
            2,
        )

    def _assert_stamp_duty_discharged(self):
        """FLAW-08.2: a chargeable instrument activates only once duty is paid
        and the executed contract is archived.

        The first implementation of this control refused EVERY contract and
        offered a `skip_stamp_duty_check` context key as the way out. Nothing
        in the codebase ever set that key, so in practice it blocked all
        activation while leaving a bypass any caller could pass (A04 audit,
        2026-10-31). Chargeability is now an explicit, tracked decision and
        there is no silent escape. A04 build (2026-11-04) M08-14: the
        exemption is approved by Finance (not the person who proposed it),
        and the duty paid is compared with the confirmed Schedule I rate.
        """
        self.ensure_one()
        if not self.stamp_duty_applicable:
            if not (self.stamp_duty_exemption_reason or "").strip():
                raise UserError(
                    "Contract %s is marked not chargeable under Stamp Act 1899 "
                    "Schedule I but records no reason. State the basis for "
                    "non-chargeability before activating." % self.code
                )
            if not self.stamp_exemption_approved_by and not self.env.su:
                raise UserError(
                    "Contract %s claims a stamp-duty exemption that Finance has not "
                    "approved. Ask a Finance approver who did not propose it to "
                    "Approve Stamp Exemption." % self.code
                )
            return
        # Schedule I charges by value as well as by head. The rate table is
        # effective-dated configuration (fix.stamp.duty.schedule) that Finance
        # maintains; when no row covers the instrument the answer is
        # "chargeable", so an unmaintained table never waives duty.
        Schedule = self.env["fix.stamp.duty.schedule"]
        if not Schedule.is_chargeable(
            self.stamp_act_article,
            self.annual_value,
            on_date=self.date_start,
            company=self.company_id,
        ):
            return
        if not (self.stamp_duty_cert_no or "").strip():
            raise UserError(
                "Contract %s cannot be activated without a Stamp Duty Certificate "
                "Number (Stamp Act 1899 Schedule I, %s). If the instrument is not "
                "chargeable, clear 'Chargeable Under Schedule I' and record why."
                % (
                    self.code,
                    dict(self._fields["stamp_act_article"].selection).get(
                        self.stamp_act_article, "article not set"
                    ),
                )
            )
        if not self.has_signed_contract_doc and not self._contract_signed_document():
            raise UserError(
                "Contract %s cannot be activated without an archived signed "
                "contract PDF document." % self.code
            )
        due = self._stamp_duty_due()
        if due and (self.stamp_duty_amount or 0.0) + 0.005 < due:
            raise UserError(
                "Contract %s records BDT %.2f of stamp duty paid, but Schedule I "
                "charges BDT %.2f on this instrument." % (self.code, self.stamp_duty_amount, due)
            )

    # ---- e-signature evidence (T07, M08-3) ------------------------------------
    def _contract_signed_document(self):
        """The signed document of a verified envelope, or an empty recordset."""
        self.ensure_one()
        envelope = self.esignature_envelope_id.sudo()
        if envelope and envelope.state == "completed" and envelope.document_id.attachment_id:
            return envelope.document_id
        return self.env["fix.document"]

    def _contract_envelope_problems(self):
        """Why this contract's signature is not proven, as a list of reasons.

        A04 build (M08-3): `if envelope and envelope.state != 'completed'`
        meant no envelope, no check; and an envelope with no signers was
        typed 'completed'. The evidence now has to hold together: a completed
        envelope, its signed document on file, every signer signed with the
        provider's signature reference, the customer among the signers, and
        the evidence hash still matching the document and signer list."""
        self.ensure_one()
        envelope = self.esignature_envelope_id.sudo()
        if not envelope:
            return ["no e-signature envelope is attached"]
        problems = []
        if envelope.state != "completed":
            problems.append("the envelope is '%s', not completed" % envelope.state)
        if not envelope.signer_ids:
            problems.append("the envelope has no signers")
        unsigned = envelope.signer_ids.filtered(
            lambda s: not s.signed_at or not (s.signature_provider or "").strip()
        )
        if unsigned:
            problems.append(
                "%d signer(s) carry no provider signature (%s)"
                % (len(unsigned), ", ".join(unsigned.mapped("signer_name")))
            )
        customer = self.customer_id.commercial_partner_id
        signers = envelope.signer_ids.mapped("partner_id").mapped("commercial_partner_id")
        if envelope.signer_ids and customer not in signers:
            problems.append("the customer %s is not among the signers" % self.customer_id.name)
        if not envelope.document_id.attachment_id:
            problems.append("the signed document has no file")
        if not envelope.evidence_hash or envelope.evidence_hash != envelope._compute_evidence():
            problems.append("the evidence hash does not match the document and signers")
        if not envelope.completed_at:
            problems.append("the envelope records no completion time")
        return problems

    # ---- lifecycle: submit, approve, legal review ------------------------------
    def action_request_approval(self, justification=None):
        """Draft -> Pending Approval: route the contract value to the DOFA
        tier holder (M63 inbox). The terms freeze from here."""
        require_role(self.env, OFFICER, "Submitting a contract for approval")
        self._contract_require_state(("draft",), "be submitted for approval")
        for rec in self:
            if (rec.annual_value or 0.0) <= 0:
                raise UserError("Contract %s has no annual value to approve." % rec.code)
            if (
                not rec.stamp_duty_applicable
                and not (rec.stamp_duty_exemption_reason or "").strip()
            ):
                raise UserError(
                    "Contract %s claims a stamp-duty exemption without a reason." % rec.code
                )
        self._contract_template_check()
        result = super().action_request_approval(justification=justification)
        self._guarded().write({"state": "pending_approval"})
        return result

    def action_dofa_approve(self):
        """The value approval, run by the M63 task in the approver's env. The
        approver needs no write right on the contract: the routing check runs
        as the approver, the stamp is written as a service (tier, SoD and
        justification still read the approver)."""
        self._approval_assert_routed()
        self._contract_require_state(("pending_approval",), "be approved")
        result = super(FixContract, self.sudo()).action_dofa_approve()
        self.sudo()._contract_advance_after_review()
        return result

    def _contract_advance_after_review(self):
        for rec in self.filtered(lambda r: r.state == "pending_approval"):
            if rec.dofa_approved and rec._contract_legal_cleared():
                rec._guarded().write({"state": "pending_signature"})
                rec.message_post(body="Approved and reviewed: awaiting the customer's signature.")

    def action_legal_review(self, note=None):
        """Legal clears the contract's terms. A Legal reviewer who neither
        raised the contract nor approved its value (segregation of duties)."""
        require_role(self.env, LEGAL, "Legal review of a contract")
        self._contract_require_state(("pending_approval",), "be reviewed by Legal")
        for rec in self:
            if not rec.legal_review_required:
                raise UserError("Contract %s does not need Legal review." % rec.code)
            if rec.legal_reviewed_by:
                raise UserError("Contract %s is already reviewed by Legal." % rec.code)
            conflicted = rec.create_uid | rec.dofa_approved_by
            if rec.approval_request_id:
                conflicted |= rec.approval_request_id.sudo().requested_by_id
            if self.env.user in conflicted and not self.env.su:
                raise UserError(
                    "Segregation of duties: you raised or approved contract %s, so "
                    "another Legal reviewer must review it." % rec.code
                )
            rec.sudo()._guarded().write(
                {
                    "legal_reviewed_by": self.env.user.id,
                    "legal_reviewed_on": fields.Datetime.now(),
                    "legal_review_note": note or False,
                }
            )
            rec.sudo().message_post(body="Legal review completed by %s." % self.env.user.name)
        self.sudo()._contract_advance_after_review()
        return True

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "pending_approval")._guarded().write({"state": "draft"})
        return result

    def _approval_on_rejected(self, comment):
        for rec in self.sudo().filtered(lambda r: r.state == "pending_approval"):
            rec._guarded().write(
                {"state": "draft", "legal_reviewed_by": False, "legal_reviewed_on": False}
            )
        return super()._approval_on_rejected(comment)

    def action_reset_to_draft(self):
        """Back to Draft before signature (the customer asked for changes).
        The approval and the Legal review covered the old terms: both go."""
        require_role(self.env, OFFICER, "Resetting a contract to draft")
        self._contract_require_state(("pending_approval", "pending_signature"), "be reset to draft")
        for rec in self:
            rec._approval_void("the contract was reset to draft for changes")
            rec.sudo()._approval_clear_stamp("the contract was reset to draft")
            rec.sudo()._guarded().write(
                {
                    "state": "draft",
                    "legal_reviewed_by": False,
                    "legal_reviewed_on": False,
                    "legal_review_note": False,
                    "approval_state": "none",
                }
            )
            rec.message_post(body="Reset to draft by %s." % self.env.user.name)
        return True

    def action_approve_stamp_exemption(self):
        """Finance approves the stamp-duty exemption (M08-14). Not the person
        who proposed it, nor the contract's creator."""
        require_role(self.env, FINANCE, "Approving a stamp-duty exemption")
        self._contract_require_state(
            ("draft", "pending_approval", "pending_signature"), "have its exemption approved"
        )
        for rec in self:
            if rec.stamp_duty_applicable:
                raise UserError("Contract %s claims no stamp-duty exemption." % rec.code)
            if not (rec.stamp_duty_exemption_reason or "").strip():
                raise UserError("Contract %s records no exemption reason." % rec.code)
            if not self.env.su and self.env.user in (
                rec.create_uid | rec.stamp_exemption_requested_by
            ):
                raise UserError(
                    "Segregation of duties: you raised contract %s or proposed its "
                    "exemption, so another Finance approver must approve it." % rec.code
                )
            rec.sudo()._guarded().write(
                {
                    "stamp_exemption_approved_by": self.env.user.id,
                    "stamp_exemption_approved_on": fields.Datetime.now(),
                }
            )
            rec.sudo().message_post(
                body="Stamp-duty exemption approved by %s: %s"
                % (self.env.user.name, rec.stamp_duty_exemption_reason)
            )
        return True

    # ---- activation (T07, FLAW-08.2, M08-1/2/3/4/8) ------------------------------
    def action_activate(self):
        """Pending Signature -> Active: the value approved (and still covering
        the value), Legal cleared, the customer's signature proven, stamp
        duty discharged. Then the PM schedule, the OCA record and the
        contract.activated event. Superuser code (data loads, migrations) is
        trusted with the approval and signature, never with the from-state."""
        today = fields.Date.context_today(self)
        for contract in self:
            trusted = self.env.su
            allowed = ("pending_signature",) + (("draft", "pending_approval") if trusted else ())
            contract._contract_require_state(allowed, "be activated")
            if not trusted:
                require_role(self.env, OFFICER, "Activating a contract")
                if contract.date_end < today:
                    raise UserError(
                        "Contract %s ended on %s: an expired term cannot be activated."
                        % (contract.code, contract.date_end)
                    )
                contract._dofa_assert_approved("Activation of contract %s" % contract.code)
                if not contract._contract_legal_cleared():
                    raise UserError("Contract %s is not yet reviewed by Legal." % contract.code)
                contract._contract_template_check()
                problems = contract._contract_envelope_problems()
                if problems:
                    raise UserError(
                        "Contract %s activates on the customer's completed signature: %s."
                        % (contract.code, "; ".join(problems))
                    )
            else:
                envelope = contract.esignature_envelope_id
                if envelope and envelope.state != "completed":
                    raise UserError(
                        "Contract %s: the e-signature envelope is '%s' — a contract "
                        "activates on a completed signature" % (contract.code, envelope.state)
                    )
            contract._assert_stamp_duty_discharged()
            vals = {
                "state": "active",
                "activated_by": self.env.user.id,
                "activated_on": fields.Datetime.now(),
            }
            if contract._contract_signed_document():
                vals["has_signed_contract_doc"] = True
            contract.sudo()._guarded().write(vals)
            contract.sudo()._generate_pm_schedule()
            contract.sudo().action_sync_oca_contract()
            publish(
                self.env,
                "contract.activated",
                "fix.contract",
                contract.id,
                {
                    "code": contract.code,
                    "family": contract.family,
                    "customer_id": contract.customer_id.id,
                    "annual_value": contract.annual_value,
                },
            )
            previous = contract.renewed_from_id
            if previous:
                publish(
                    self.env,
                    "contract.renewed",
                    "fix.contract",
                    contract.id,
                    {
                        "old_code": previous.code,
                        "new_code": contract.code,
                        "new_value": contract.annual_value,
                    },
                )
        return True

    # ---- suspension / resumption --------------------------------------------------
    def action_resume(self):
        """Suspended -> Active, within the term (Contract Manager)."""
        require_role(self.env, MANAGER, "Resuming a suspended contract")
        self._contract_require_state(("suspended",), "be resumed")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date_end < today:
                raise UserError("Contract %s has ended; it expires, not resumes." % rec.code)
            rec.sudo()._guarded().write({"state": "active"})
            rec.message_post(body="Resumed by %s." % self.env.user.name)
        return True

    # ---- billing hand-off (C7, for the finance bridge) ------------------------------
    # A04 ERP audit M08-F6 / M36-F3 / M08-F1 (20 Nov 2026). The schedule used
    # fixed 30-day steps at days/365 of the annual value: a 12-month AMC got
    # 13 invoices plus a 5-day stub, a 6-month quote billed 986.30 short, a
    # leap year 328.77 long - and a suspended contract was back-billed for
    # its suspension on resume. Now:
    #   * the term is cut into CALENDAR-MONTH slots anchored on the start day
    #     (start + n months, never drifting), and a period is 1/3/6/12 slots;
    #   * a slot is worth annual_value / 12 (the rate in force that day, after
    #     applied pricing amendments); a part-slot is worth its share of the
    #     slot's days;
    #   * a day inside a suspension window is never billed;
    #   * the last period of the term absorbs the rounding so the term bills
    #     exactly term_value, less the value of suspended days that were not
    #     compensated by a term extension.
    FREQUENCY_MONTHS = {"monthly": 1, "quarterly": 3, "semiannual": 6, "annual": 12}

    def _fix_slot_bounds(self, day):
        """(slot start, slot end) of the calendar-month slot holding `day`."""
        self.ensure_one()
        start = self.date_start
        months = (day.year - start.year) * 12 + (day.month - start.month)
        slot = start + relativedelta(months=months)
        if slot > day:
            months -= 1
            slot = start + relativedelta(months=months)
        nxt = start + relativedelta(months=months + 1)
        return slot, nxt - timedelta(days=1)

    def _fix_rate_steps(self):
        """[(effective from, annual value)] of the applied pricing amendments,
        oldest first; empty when the value never changed."""
        self.ensure_one()
        if not self.id:
            return []
        applied = (
            self.env["fix.contract.amendment"]
            .sudo()
            .search(
                [
                    ("contract_id", "=", self.id),
                    ("state", "=", "applied"),
                    ("kind", "in", ("pricing", "scope")),
                ],
                order="effective_from, id",
            )
            .filtered(lambda a: abs((a.value_after or 0.0) - (a.value_before or 0.0)) > 0.005)
        )
        if not applied:
            return []
        steps = [(None, applied[0].value_before or 0.0)]
        steps += [(a.effective_from, a.value_after or 0.0) for a in applied]
        return steps

    def _fix_rate_on(self, day, steps=None):
        """The annual value in force on `day`: the applied pricing amendments
        move it from their effective date."""
        self.ensure_one()
        steps = self._fix_rate_steps() if steps is None else steps
        if not steps:
            return self.annual_value or 0.0
        rate = steps[0][1]
        for since, value in steps[1:]:
            if since <= day:
                rate = value
        return rate

    def _fix_suspension_windows(self):
        self.ensure_one()
        if "fix.contract.suspension" not in self.env or not self.id:
            return []
        rows = self.env["fix.contract.suspension"].sudo().search([("contract_id", "=", self.id)])
        return [
            (row.date_from, row.date_to or self.date_end, row.compensated)
            for row in rows
            if row.date_from
        ]

    def _fix_day_fee(self, day, slot_cache, steps):
        slot = slot_cache.get(day)
        if slot is None:
            slot = self._fix_slot_bounds(day)
            cursor = slot[0]
            while cursor <= slot[1]:
                slot_cache[cursor] = slot
                cursor += timedelta(days=1)
        days_in_slot = (slot[1] - slot[0]).days + 1
        return self._fix_rate_on(day, steps) / 12.0 / days_in_slot

    def _fix_fee_between(self, date_from, date_to, suspended=True, compensated=None):
        """The unrounded fee for the days [date_from, date_to].

        suspended=True    leave out the days inside a suspension window
        suspended='only'  the fee of the suspended days only (compensated:
                          None = all, True/False = only those windows)."""
        self.ensure_one()
        if not (date_from and date_to and self.date_start) or date_to < date_from:
            return 0.0
        windows = self._fix_suspension_windows() if suspended else []
        steps = self._fix_rate_steps()
        cache, total, day = {}, 0.0, date_from
        while day <= date_to:
            inside = [w for w in windows if w[0] <= day <= w[1]]
            if suspended == "only":
                hit = [w for w in inside if compensated is None or w[2] == compensated]
                if hit:
                    total += self._fix_day_fee(day, cache, steps)
            elif not inside:
                total += self._fix_day_fee(day, cache, steps)
            day += timedelta(days=1)
        return total

    def _fix_billing_target(self) -> float:
        """What the whole term bills (excl. VAT): the term value less the
        suspended days no term extension compensated."""
        self.ensure_one()
        lost = self._fix_fee_between(
            self.date_start, self.date_end, suspended="only", compensated=False
        )
        return round(self._fix_term_value() - lost, 2)

    def _fix_billing_periods(self):
        """[(period start, period end)] by the billing frequency."""
        self.ensure_one()
        step = self.FREQUENCY_MONTHS.get(self.billing_frequency or "monthly", 1)
        start, end = self.date_start, self.date_end
        out, n = [], 0
        while True:
            p_start = start + relativedelta(months=n * step)
            if p_start > end:
                break
            p_end = min(start + relativedelta(months=(n + 1) * step) - timedelta(days=1), end)
            out.append((p_start, p_end))
            n += 1
        return out

    def _fix_billing_schedule(self, periods_per_year=None):
        """The contract's billing schedule for the M20 bridge (read-only; no
        invoice is created here). A period already billed (its billing period
        row exists) keeps the amount it was billed; the last period absorbs
        the rounding to the term's billing target, never below zero."""
        self.ensure_one()
        if not (self.date_start and self.date_end):
            return []
        billed = {
            p.period_start: p
            for p in self.env["fix.contract.billing.period"]
            .sudo()
            .search([("contract_id", "=", self.id)])
        }
        rows = []
        for p_start, p_end in self._fix_billing_periods():
            row = billed.get(p_start)
            rows.append(
                {
                    "period_start": p_start,
                    "period_end": row.period_end if row else p_end,
                    "amount": round(
                        row.amount if row else self._fix_fee_between(p_start, p_end), 2
                    ),
                    "billed": bool(row),
                }
            )
        if rows and not rows[-1]["billed"]:
            others = sum(r["amount"] for r in rows[:-1])
            rows[-1]["amount"] = round(max(self._fix_billing_target() - others, 0.0), 2)
        return rows

    def _fix_billed_total(self) -> float:
        """The amount (excl. VAT) of every period billed so far."""
        self.ensure_one()
        periods = (
            self.env["fix.contract.billing.period"].sudo().search([("contract_id", "=", self.id)])
        )
        return round(sum(periods.mapped("amount")), 2)

    def mark_billed_through(self, day):
        """Called by the M20 billing hand-off (as a service) when a period is
        invoiced: amendments cannot take effect inside a billed period."""
        if not self.env.su:
            raise UserError("The billed-through date is set by the billing hand-off only.")
        for rec in self:
            day = fields.Date.to_date(day)
            if rec.billed_through_date and day < rec.billed_through_date:
                raise UserError("A billed-through date cannot move backwards.")
            rec._guarded().write({"billed_through_date": day})
        return True

    # --- T05: renewal engine ------------------------------------------
    def _fix_create_renewal_term(self, date_start=None, date_end=None, value=None, name=None):
        """The next term as a DRAFT contract linked to this one. It is approved,
        signed and activated like any contract; this term stays in force until
        its own end date (A04 build, M08-10)."""
        self.ensure_one()
        if self.renewal_ids.filtered(lambda r: r.state not in ("terminated", "expired")):
            raise UserError("Contract %s already has a renewal term." % self.code)
        factor = 1.0 + (self.escalation_pct or 0.0) / 100.0
        new_value = round(self.annual_value * factor, 2) if value is None else value
        start = date_start or self.date_end + timedelta(days=1)
        end = date_end or self.date_end + timedelta(days=365)
        renewal = self._guarded().copy(
            {
                "code": False,
                "name": name or "%s (renewal)" % self.name,
                "date_start": start,
                "date_end": end,
                "annual_value": new_value,
                "state": "draft",
                "renewed_from_id": self.id,
                # entitlements and covered assets carry into the renewal term
            }
        )
        renewal = renewal._fix_drop_token()
        self.message_post(body="Renewal term %s drafted (BDT %.2f)." % (renewal.code, new_value))
        return renewal

    def action_renew(self):
        """Renew with escalation: the next term is drafted and goes through
        approval and signature; THIS term keeps its cover until it ends.
        Returns the renewal(s) - one per renewed contract."""
        require_role(self.env, OFFICER, "Renewing a contract")
        renewals = self.browse()
        for contract in self:
            if contract.state not in (*IN_FORCE, "expired"):
                raise UserError("Only an active/expiring/expired contract renews")
            # (a `return` here used to end the loop: only the FIRST contract
            # of a multi-record renewal was ever renewed)
            renewals |= contract._fix_create_renewal_term()
        return renewals

    # --- C10: expiry and renewal windows -----------------------------------------
    @api.model
    def cron_expiring_contracts(self):
        """AUT-015, daily and idempotent. A04 build (M08-9): the method had no
        ir.cron and never moved a state, so an 'active' contract that ended a
        month ago still opened AMC orders.

        - a contract past its end date expires (and stops covering);
        - one inside its renewal lead time reads 'Expiring Soon';
        - each −90/−60/−30/−15 window is announced once (contract.expiring);
        - an auto-renew contract gets its next term drafted at lead time.
        Returns the number of window announcements."""
        today = fields.Date.context_today(self)
        Contract = self.sudo()
        expired = Contract.search(
            [("state", "in", (*IN_FORCE, "suspended")), ("date_end", "<", today)]
        )
        for contract in expired:
            contract._guarded().write({"state": "expired"})
            publish(
                self.env,
                "contract.expired",
                "fix.contract",
                contract.id,
                {"code": contract.code, "date_end": str(contract.date_end)},
            )
        live = Contract.search([("state", "in", IN_FORCE), ("date_end", ">=", today)])
        notified = 0
        for contract in live:
            days_left = (contract.date_end - today).days
            lead = max(contract.renewal_lead_days or 0, EXPIRY_WINDOWS[-1])
            if contract.state == "active" and days_left <= lead:
                contract._guarded().write({"state": "expiring"})
            window = (
                min((w for w in EXPIRY_WINDOWS if days_left <= w), default=None)
                if days_left > 0
                else None
            )
            # BRU-CTR-12: a contract in dispute neither escalates nor auto-renews.
            # A04 ERP audit M08-F17: the expiry ladder was announced only for
            # auto-renew contracts, so a contract nobody renews expired with
            # no alert at all. Every in-force contract is announced; only the
            # renewal draft below depends on auto_renew.
            if window is None or contract.in_dispute:
                continue
            if contract.expiry_notified_window and contract.expiry_notified_window <= window:
                continue
            contract._fix_expiry_alert(window)
            publish(
                self.env,
                "contract.expiring",
                "fix.contract",
                contract.id,
                {
                    "code": contract.code,
                    "window_days": window,
                    "date_end": str(contract.date_end),
                },
            )
            contract._guarded().write({"expiry_notified_window": window})
            notified += 1
            if (
                contract.auto_renew
                and days_left <= (contract.renewal_lead_days or 0)
                and not contract.renewal_ids
                and not contract._fix_open_renewal_quote()
            ):
                contract._fix_create_renewal_term()
        return notified

    def _fix_open_renewal_quote(self):
        """A04 ERP audit M08-F17: a renewal being quoted (an M08 renewal quote
        or an M36 quotation still with the customer) is the renewal path; the
        cron does not draft a second term beside it."""
        self.ensure_one()
        quotes = (
            self.env["fix.contract.renewal"]
            .sudo()
            .search_count([("contract_id", "=", self.id), ("state", "in", ("draft", "quoted"))])
        )
        return bool(quotes)

    def _fix_expiry_alert(self, window):
        """A to-do for the contract's owner on each expiry window (AUT-015)."""
        self.ensure_one()
        owner = self.owner_id if "owner_id" in self._fields else self.env["res.users"]
        owner = owner or self.create_uid
        if owner and owner.active and not owner.share:
            self.sudo().activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=self.date_end,
                summary="Contract %s ends in %d days" % (self.code, window),
                note="Renew, re-quote or let it expire on %s (AUT-015)." % self.date_end,
                user_id=owner.id,
            )

    # --- T06: preventive maintenance scheduler -------------------------

    PM_INTERVALS = {  # family -> visit interval days
        "amc": 90,
        "ramc": 120,
        "managed": 30,
        "rental": 180,
        "marketplace": 0,
    }

    def _generate_pm_schedule(self):
        """T06: generate preventive-maintenance visits from the contract
        terms at activation — the schedule feeds M02 dispatch."""
        interval = self.PM_INTERVALS.get(self.family, 0)
        if not interval or not self.covered_device_ids:
            return
        Visit = self.env["fix.contract.pm.visit"].sudo()._guarded()
        start = self.date_start
        while start + timedelta(days=interval) <= self.date_end:
            visit_date = start + timedelta(days=interval)
            for device in self.covered_device_ids:
                Visit.create(
                    {
                        "contract_id": self.id,
                        "device_id": device.id,
                        "scheduled_date": visit_date,
                        "state": "scheduled",
                    }
                )
            start = visit_date


ENTITLEMENT_TERM_FIELDS = frozenset(
    {"contract_id", "entitlement_type", "quantity_included", "device_id"}
)


class FixContractEntitlement(models.Model):
    """What a contract buys and how consumption draws it down (T03).

    Quantity models: visits per term, incidents per term, hours per term —
    drawn down by M01 consumption events; never negative.

    A04 build (2026-11-04) M08-13: a clerk reset a used-up balance 0 -> 500
    through P03. `quantity_consumed` now moves only through consume(), and
    the line's terms freeze with the contract's (a scope change is an
    amendment)."""

    _name = "fix.contract.entitlement"
    _description = "Contract Entitlement"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    entitlement_type = fields.Selection(
        [
            ("visits", "Preventive Visits"),
            ("incidents", "Repair Incidents"),
            ("hours", "Labour Hours"),
            ("loaners", "Loaner Devices"),
        ],
        required=True,
        default="incidents",
    )
    quantity_included = fields.Float(required=True, default=0.0, help="0 = unlimited for that type")
    quantity_consumed = fields.Float(default=0.0, copy=False, readonly=True)
    quantity_remaining = fields.Float(compute="_compute_remaining", store=True)
    device_id = fields.Many2one(
        "fix.device", string="Specific Asset", help="Empty = the whole covered estate"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"quantity_consumed"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.contract_id.state != "draft":
            locked |= ENTITLEMENT_TERM_FIELDS
        return locked

    @api.constrains("quantity_included", "quantity_consumed")
    def _check_quantities(self):
        for ent in self:
            if ent.quantity_included < 0 or ent.quantity_consumed < 0:
                raise ValidationError("Entitlement quantities cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            ids = {v.get("contract_id") for v in vals_list if v.get("contract_id")}
            live = self.env["fix.contract"].browse(list(ids)).filtered(lambda c: c.state != "draft")
            if live:
                raise UserError(
                    "Contract %s is no longer a draft: what it covers changes through an "
                    "approved scope amendment." % ", ".join(live.mapped("code"))
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = set(vals) & ENTITLEMENT_TERM_FIELDS
            for ent in self.filtered(lambda e: e.contract_id.state != "draft"):
                if any(ent._fix_guard_differs(n, vals[n], ent[n]) for n in frozen):
                    raise UserError(
                        "The entitlements of contract %s are fixed once it leaves draft; "
                        "change them through an approved amendment." % ent.contract_id.code
                    )
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open() and self.filtered(lambda e: e.contract_id.state != "draft"):
            raise UserError("An entitlement of a submitted or live contract cannot be deleted.")
        return super().unlink()

    @api.depends("quantity_included", "quantity_consumed")
    def _compute_remaining(self):
        for ent in self:
            if ent.quantity_included == 0:
                ent.quantity_remaining = -1  # sentinel: unlimited
            else:
                ent.quantity_remaining = ent.quantity_included - ent.quantity_consumed

    def consume(self, qty: float, source_ref: str = "") -> bool:
        """Draw down. Returns False when the entitlement is exhausted — the
        caller (M01) then treats the order as standard/paid, not AMC.

        A04 build (M08-5/13): only a contract in force inside its term is
        drawn down, and the draw-down is a service write (M01 calls it as
        the system once its own checks pass; a person needs the Contract
        Officer role)."""
        require_role(self.env, OFFICER, "Drawing down a contract entitlement")
        today = fields.Date.context_today(self)
        for ent in self:
            if not ent.contract_id._contract_in_force_on(today):
                return False
            if ent.quantity_included == 0:  # unlimited
                ent.sudo()._guarded().write({"quantity_consumed": ent.quantity_consumed + qty})
                publish(
                    self.env,
                    "entitlement.consumed",
                    "fix.contract.entitlement",
                    ent.id,
                    {
                        "qty": qty,
                        "source": source_ref,
                        "remaining": -1,
                    },
                )
                return True
            if ent.quantity_remaining < qty:
                return False
            ent.sudo()._guarded().write({"quantity_consumed": ent.quantity_consumed + qty})
            publish(
                self.env,
                "entitlement.consumed",
                "fix.contract.entitlement",
                ent.id,
                {
                    "qty": qty,
                    "source": source_ref,
                    "remaining": ent.quantity_remaining,
                },
            )
            return True
        return False

    # ------------------------------------------------------------------
    # S5 - the Entitlement Lookup Service (A03 gap-plan Part IV)
    #
    # entitlement_active() answers M01's device-and-category question at
    # order time. The contact centre and the complaints desk ask a different
    # one, at INTAKE, before any order exists: "this person is on the phone
    # -- what are we contractually obliged to give them?" That question is
    # about a PARTY, has no device in it, and needs the answer in words an
    # agent can act on rather than a boolean.
    #
    # Before this, neither M27 conversations nor M34 complaints checked
    # entitlements at all, so an AMC customer with a contracted four-hour
    # response was routed exactly like a walk-in.
    # ------------------------------------------------------------------
    @api.model
    def entitlement_summary_for_party(self, partner):
        """What this party is contractually owed, right now.

        Returns:
            has_entitlement  bool  - any active contract covers them
            available        bool  - any covering line still has quantity
            contracts        list  - the covering contracts, with term dates
            lines            list  - per-entitlement remaining quantities
            note             str   - one line an agent can read aloud
            sla_policy_id    int   - the contracted SLA policy, if any, so
                                     the caller can start an S9 clock against
                                     the promise the customer actually bought
        """
        partner_id = getattr(partner, "id", partner) or False
        empty = {
            "has_entitlement": False,
            "available": False,
            "contracts": [],
            "lines": [],
            "sla_policy_id": False,
            "note": "No identified party, so no entitlement could be checked.",
        }
        if not partner_id:
            return empty

        today = fields.Date.context_today(self)
        contracts = (
            self.env["fix.contract"]
            .sudo()
            .search(
                [
                    ("customer_id", "=", partner_id),
                    ("state", "in", IN_FORCE),
                    ("date_start", "<=", today),
                    ("date_end", ">=", today),
                ]
            )
        )
        if not contracts:
            return dict(
                empty,
                note="No active contract covers this customer today, so "
                "standard service terms apply.",
            )

        lines = self.sudo().search([("contract_id", "in", contracts.ids)])
        line_rows = []
        any_available = False
        for line in lines:
            unlimited = line.quantity_included == 0
            remaining = -1 if unlimited else line.quantity_remaining
            if unlimited or remaining > 0:
                any_available = True
            line_rows.append(
                {
                    "contract": line.contract_id.name,
                    "type": line.entitlement_type,
                    "included": line.quantity_included,
                    "consumed": line.quantity_consumed,
                    "remaining": remaining,
                    "unlimited": unlimited,
                    "device_id": line.device_id.id or None,
                }
            )

        # fix.contract carries sla_policy_ids (a contract may buy several
        # targets). The first is handed back as the one to start a clock
        # against; a caller needing a specific KPI reads the contract.
        sla_policy = False
        for contract in contracts:
            policies = contract.sla_policy_ids
            if policies:
                sla_policy = policies[0].id
                break

        if not lines:
            note = (
                "Covered by %d active contract(s), but the contract buys no "
                "entitlement lines - treat as standard/paid service." % len(contracts)
            )
        elif any_available:
            parts = [
                "%s %s"
                % (
                    "unlimited" if r["unlimited"] else ("%g left" % r["remaining"]),
                    r["type"],
                )
                for r in line_rows
                if r["unlimited"] or r["remaining"] > 0
            ]
            note = "Contract customer: %s." % ", ".join(parts)
        else:
            note = (
                "Covered by an active contract, but every entitlement line is "
                "exhausted - this visit is standard/paid."
            )

        return {
            "has_entitlement": True,
            "available": any_available,
            "contracts": [
                {
                    "id": c.id,
                    "name": c.name,
                    "date_end": str(c.date_end),
                }
                for c in contracts
            ],
            "lines": line_rows,
            "sla_policy_id": sla_policy,
            "note": note,
        }

    @api.model
    def consume_for_party(self, partner, entitlement_type, qty=1.0, source_ref=""):
        """Draw down the best-fitting line for a party, or report why not.

        Picks the line that is closest to exhaustion first, so that an
        unlimited line is not burned while a counted one expires unused.
        """
        summary = self.entitlement_summary_for_party(partner)
        if not summary["available"]:
            return {"consumed": False, "reason": summary["note"]}
        today = fields.Date.context_today(self)
        contracts = (
            self.env["fix.contract"]
            .sudo()
            .search(
                [
                    ("customer_id", "=", getattr(partner, "id", partner)),
                    ("state", "in", IN_FORCE),
                    ("date_start", "<=", today),
                    ("date_end", ">=", today),
                ]
            )
        )
        candidates = self.sudo().search(
            [
                ("contract_id", "in", contracts.ids),
                ("entitlement_type", "=", entitlement_type),
            ]
        )
        usable = candidates.filtered(
            lambda line: line.quantity_included == 0 or line.quantity_remaining >= qty
        )
        if not usable:
            return {
                "consumed": False,
                "reason": "No %s entitlement with %g remaining on any active "
                "contract." % (entitlement_type, qty),
            }
        # counted lines before unlimited ones, lowest remaining first
        ordered = usable.sorted(
            key=lambda line: (
                1 if line.quantity_included == 0 else 0,
                line.quantity_remaining if line.quantity_included else 0,
            )
        )
        line = ordered[0]
        ok = line.consume(qty, source_ref=source_ref)
        return {
            "consumed": bool(ok),
            "entitlement_id": line.id,
            "contract": line.contract_id.name,
            "remaining": line.quantity_remaining,
            "reason": ""
            if ok
            else "The selected entitlement was exhausted " "between the check and the draw-down.",
        }

    @api.model
    def entitlement_active(
        self, device_id: int, category: str, customer=None, on_date=None
    ) -> bool:
        """The API M01's order-category gate consumes (BRU-SRM-03): is this
        device covered by an ACTIVE contract of this family with remaining
        entitlement?

        Remaining entitlement = at least one entitlement line of such a
        contract that applies to the device (lines for that specific asset,
        or estate-wide lines with no asset) and is either unlimited
        (quantity_included 0) or still has quantity_remaining > 0 — of any
        type the model defines (visits, incidents, hours, loaners). A
        contract whose applicable lines are all drawn down, or that buys no
        entitlement at all, does not open an AMC order: the caller treats
        it as standard/paid. Every covering contract is considered (one
        exhausted contract does not hide another's balance).

        A04 build (M08-9): the contract must be in force on the day (its
        term covers it), not merely carry an 'active' state; and when the
        caller names the customer, only that customer's contracts count."""
        day = on_date or fields.Date.context_today(self)
        # M08 capture pass 2: a device is covered when it is listed OR caught
        # by a coverage rule (asset type / brand / site, FR-CTR-014), so the
        # device is no longer part of the search
        # A04 ERP audit M08-F10: M01's "AMC / Contract" category is contract
        # work under ANY family that covers assets, not the AMC family alone.
        families = list(COVER_FAMILIES) if category == "amc" else [category]
        domain = [
            ("state", "in", IN_FORCE),
            ("family", "in", families),
            ("date_start", "<=", day),
            ("date_end", ">=", day),
        ]
        if customer:
            partner = (
                customer
                if hasattr(customer, "commercial_partner_id")
                else (self.env["res.partner"].browse(int(customer)))
            )
            domain.append(("customer_id", "child_of", partner.commercial_partner_id.id))
        device = self.env["fix.device"].sudo().browse(device_id)
        contracts = (
            self.env["fix.contract"]
            .sudo()
            .search(domain)
            .filtered(lambda k: k._contract_covers_device(device, day))
        )
        remaining = contracts.entitlement_ids.filtered(
            lambda ent: ent.device_id.id in (False, device_id)
            and (ent.quantity_included == 0 or ent.quantity_remaining > 0)
        )
        return bool(remaining)


class FixContractPmVisit(models.Model):
    """One preventive-maintenance visit on the schedule (T06).

    A04 build (2026-11-04) M08-12/13: a visit was typed 'completed' with no
    order, and the dispatched order was not linked to the contract (so PM
    cost never reached the margin and the order had no AMC basis). The
    state now moves only by its actions: dispatch opens the order linked to
    the contract, and a visit completes when that order is delivered."""

    _name = "fix.contract.pm.visit"
    _description = "Preventive Maintenance Visit"
    _inherit = ["mail.thread", "fix.guarded.mixin"]

    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    device_id = fields.Many2one("fix.device", required=True, ondelete="cascade")
    scheduled_date = fields.Date(required=True)
    service_order_id = fields.Many2one("fix.service.order", string="Service Order", readonly=True)
    skip_reason = fields.Char(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("dispatched", "Dispatched"),
            ("completed", "Completed"),
            ("skipped", "Skipped"),
        ],
        default="scheduled",
        required=True,
        tracking=True,
        readonly=True,
    )

    # The order states in which the visit's work is done.
    _DONE_ORDER_STATES = ("delivered", "closed")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "service_order_id", "skip_reason"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1:
            locked |= {"contract_id", "device_id"}
            if self.state != "scheduled":
                locked.add("scheduled_date")
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for visit in self:
                moved = [
                    n
                    for n in ("contract_id", "device_id")
                    if n in vals and visit._fix_guard_differs(n, vals[n], visit[n])
                ]
                if moved:
                    raise UserError(
                        "A scheduled visit cannot be moved to another contract or device."
                    )
                if (
                    "scheduled_date" in vals
                    and visit.state != "scheduled"
                    and visit._fix_guard_differs(
                        "scheduled_date", vals["scheduled_date"], visit.scheduled_date
                    )
                ):
                    raise UserError("Only a visit that is still scheduled can be rescheduled.")
        return super().write(vals)

    def action_create_service_order(self):
        """Feeds dispatch: the PM visit opens as a service order on the
        covered device, category mapped from the contract family, LINKED to
        the contract (its cost reaches the contract margin; the AMC order's
        zero-charge basis is the contract's visit entitlement). The order is
        created under the dispatcher's own M01 rights; the visit is updated
        as a service."""
        Order = self.env["fix.service.order"]
        today = fields.Date.context_today(self)
        for visit in self:
            if visit.service_order_id:
                continue
            if visit.state != "scheduled":
                raise UserError(
                    "Only a scheduled visit can be dispatched (it is %s)." % visit.state
                )
            contract = visit.contract_id
            if not contract._contract_in_force_on(max(today, contract.date_start)):
                raise UserError(
                    "Contract %s is not in force, so its PM visit cannot be dispatched."
                    % contract.code
                )
            # A04 ERP audit M08-F10: only an AMC visit was contract work; a
            # RAMC, managed-service or rental visit was opened as a standard
            # (paid) order and drew no entitlement. Every family that covers
            # assets opens its visit as contract work ("AMC / Contract").
            category = "amc" if family_profile(contract.family)["covers_assets"] else "standard"
            order = Order.create(
                {
                    "device_id": visit.device_id.id,
                    "customer_id": contract.customer_id.id,
                    # a device registered without a branch is served by the
                    # branch of the contract's unit (A04 ERP audit, B2)
                    "branch_id": visit.device_id.branch_id.id or contract._fix_billing_branch().id,
                    "fault_description": "Preventive maintenance visit (%s)" % contract.code,
                    "order_category": category,
                    "contract_id": contract.id,
                }
            )
            visit.sudo()._guarded().write({"service_order_id": order.id, "state": "dispatched"})
        return True

    def action_complete(self):
        """Dispatched -> Completed, only once its order is delivered."""
        for visit in self:
            if visit.state != "dispatched" or not visit.service_order_id:
                raise UserError("Only a dispatched visit with a service order can complete.")
            if visit.service_order_id.state not in self._DONE_ORDER_STATES:
                raise UserError(
                    "PM visit cannot complete: its service order %s is %s, not delivered."
                    % (visit.service_order_id.name, visit.service_order_id.state)
                )
            visit.sudo()._guarded().write({"state": "completed"})
        return True

    def action_skip(self, reason=None):
        """Scheduled -> Skipped, with a reason (Contract Manager)."""
        require_role(self.env, MANAGER, "Skipping a PM visit")
        if not (reason or "").strip():
            raise UserError("Give the reason this preventive visit is skipped.")
        for visit in self:
            if visit.state != "scheduled":
                raise UserError("Only a scheduled visit can be skipped.")
            visit.sudo()._guarded().write({"state": "skipped", "skip_reason": reason.strip()})
            visit.message_post(body="Visit skipped by %s: %s" % (self.env.user.name, reason))
        return True

    @api.model
    def cron_sync_pm_visits(self):
        """Daily, idempotent: a dispatched visit whose order was delivered or
        closed completes. Returns the number completed."""
        visits = self.sudo().search(
            [
                ("state", "=", "dispatched"),
                ("service_order_id.state", "in", self._DONE_ORDER_STATES),
            ]
        )
        visits._guarded().write({"state": "completed"})
        return len(visits)
