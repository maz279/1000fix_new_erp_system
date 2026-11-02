# cd_contract_core — M08 Contract Lifecycle Management (P07-M01, CD-M08-nn).
#
# All product families on one engine: AMC, RAMC, managed services, rental,
# marketplace. The entitlement model is the heart (T03): what a contract
# BUYS and how consumption draws it down — M01's W1 order-category gate
# (AMC) consumes `entitlement_active()` from here.
#
# T08 (AR-008 §2.2): fix.contract.cost multi-owned by M08/M53/M54 —
# ruling: M08 OWNS it; M53/M54 consume via events, never directly.
from datetime import date, timedelta

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


class FixContract(models.Model):
    """A contract across any product family, on the party kernel."""

    _name = "fix.contract"
    _description = "Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint("UNIQUE (code)", "Contract code must be unique")

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
        [
            ("draft", "Draft"),
            ("pending_signature", "Pending Signature"),
            ("active", "Active"),
            ("expiring", "Expiring Soon"),
            ("expired", "Expired"),
            ("terminated", "Terminated"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # T08: contract cost owned HERE (M53/M54 consume via events)
    annual_value = fields.Monetary(
        string="Annual Value", currency_field="currency_id", required=True
    )
    escalation_pct = fields.Float(
        string="Annual Escalation (%)",
        default=0.0,
        help="Applied at renewal (T05): next-term value = value * (1 + pct/100)",
    )
    auto_renew = fields.Boolean(default=True, help="AUT-015: renewal opp auto-created at lead time")
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
        help="T07: through M24's kernel envelope, never a local implementation",
    )
    oca_contract_id = fields.Many2one(
        "contract.contract",
        string="OCA Contract Reference",
        copy=False,
        help="T01: Rebuilt on OCA contract (12 modules) for recurring accounting, lines, and billing",
    )

    # Statutory Stamp Duty (Stamp Act 1899) & Legal Documentation (FLAW-08.2)
    stamp_duty_cert_no = fields.Char(
        string="Stamp Duty Certificate No.",
        tracking=True,
        help="Stamp Act 1899 Schedule I compliance certificate number",
    )
    stamp_duty_amount = fields.Monetary(
        string="Stamp Duty Paid", currency_field="currency_id", tracking=True
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
        help="Whether physical/digital signed contract document is archived",
    )
    stamp_duty_applicable = fields.Boolean(
        string="Chargeable Under Schedule I",
        default=True,
        tracking=True,
        help="Whether this instrument is chargeable with stamp duty under "
        "Stamp Act 1899 Schedule I. Clearing it requires a recorded reason: "
        "an exemption is a decision somebody owns, not a silent skip.",
    )
    stamp_duty_exemption_reason = fields.Char(
        string="Non-Chargeable Reason",
        tracking=True,
        help="Why this instrument is not chargeable (e.g. not an instrument "
        "within Schedule I, or duty discharged on a parent master agreement).",
    )

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

    @api.depends(
        "annual_value",
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
            net_val = (contract.annual_value or 0.0) - delivery_cost
            contract.contract_margin_bdt = net_val
            contract.contract_margin_pct = (
                round((net_val / contract.annual_value) * 100.0, 2)
                if contract.annual_value
                else 0.0
            )

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
                    "CTR/%s" % fields.Date.today()
                )
        return super().create(vals_list)

    @api.constrains("date_start", "date_end")
    def _check_term(self):
        for contract in self:
            if contract.date_end <= contract.date_start:
                raise UserError("The term end must be after the start")

    def action_sync_oca_contract(self):
        """T01: Synchronises with underlying OCA contract.contract record.

        OCA `contract` is a manifest dependency, so the model is always
        registered. (The previous guard tested the model's EMPTY recordset
        for truthiness - always False - so the sync silently never ran.)"""
        Contract = self.env["contract.contract"]
        for contract in self:
            vals = {
                "name": contract.name,
                "partner_id": contract.customer_id.id,
                "company_id": contract.company_id.id,
                "date_start": contract.date_start,
                "date_end": contract.date_end,
                "code": contract.code,
            }
            if contract.oca_contract_id:
                contract.oca_contract_id.write(vals)
            else:
                contract.oca_contract_id = Contract.create(vals)
        return True

    def action_price_revision(self, new_annual_value: float, revision_reason: str = ""):
        """T01: Mid-term price revision / renegotiation on active contract terms."""
        for contract in self:
            if contract.state not in ("active", "draft", "expiring"):
                raise UserError(
                    "Price revision can only be applied to active, expiring, or draft contracts"
                )
            if new_annual_value <= 0:
                raise UserError("Revised annual value must be strictly positive")
            old_value = contract.annual_value
            contract.annual_value = new_annual_value
            contract.message_post(
                body=f"Annual value revised from {old_value} to {new_annual_value}. Reason: {revision_reason}"
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
        return True

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

    def _assert_stamp_duty_discharged(self):
        """FLAW-08.2: a chargeable instrument activates only once duty is paid
        and the executed contract is archived.

        The first implementation of this control refused EVERY contract and
        offered a `skip_stamp_duty_check` context key as the way out. Nothing
        in the codebase ever set that key, so in practice it blocked all
        activation while leaving a bypass any caller could pass (A04 audit,
        2026-10-31). Chargeability is now an explicit, tracked decision and
        there is no silent escape.
        """
        self.ensure_one()
        if not self.stamp_duty_applicable:
            if not (self.stamp_duty_exemption_reason or "").strip():
                raise UserError(
                    "Contract %s is marked not chargeable under Stamp Act 1899 "
                    "Schedule I but records no reason. State the basis for "
                    "non-chargeability before activating." % self.code
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
        if not self.has_signed_contract_doc:
            raise UserError(
                "Contract %s cannot be activated without an archived signed "
                "contract PDF document." % self.code
            )

    def action_activate(self):
        """Activation requires the e-signature envelope to be completed
        (T07) and Bangladesh statutory Stamp Duty compliance (Stamp Act 1899)
        with signed contract archival (FLAW-08.2)."""
        for contract in self:
            envelope = contract.esignature_envelope_id
            if envelope and envelope.state != "completed":
                raise UserError(
                    "Contract %s: the e-signature envelope is '%s' — a contract "
                    "activates on a completed signature" % (contract.code, envelope.state)
                )
            contract._assert_stamp_duty_discharged()
            contract.state = "active"
            contract._generate_pm_schedule()
            contract.action_sync_oca_contract()
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

    # --- T05: renewal engine ------------------------------------------

    def action_renew(self):
        """Renew with escalation: a NEW active term replaces this one. The
        original record keeps its history (nothing financial is mutated).
        Returns the renewal(s) - one per renewed contract."""
        renewals = self.browse()
        for contract in self:
            if contract.state not in ("active", "expiring", "expired"):
                raise UserError("Only an active/expiring/expired contract renews")
            factor = 1.0 + (contract.escalation_pct or 0.0) / 100.0
            new_value = round(contract.annual_value * factor, 2)
            renewal = contract.copy(
                {
                    "code": False,
                    "name": "%s (renewal)" % contract.name,
                    "date_start": contract.date_end + timedelta(days=1),
                    "date_end": contract.date_end + timedelta(days=365),
                    "annual_value": new_value,
                    "state": "draft",
                    # entitlements and covered assets carry into the renewal term
                }
            )
            contract.state = "expired"
            publish(
                self.env,
                "contract.renewed",
                "fix.contract",
                renewal.id,
                {
                    "old_code": contract.code,
                    "new_code": renewal.code,
                    "new_value": new_value,
                },
            )
            # (a `return` here used to end the loop: only the FIRST contract
            # of a multi-record renewal was ever renewed)
            renewals |= renewal
        return renewals

    @api.model
    def cron_expiring_contracts(self):
        """AUT-015: the −90/−60/−30/−15 ladder — flags contracts expiring
        within each window and escalates. The Airflow workflow owns the
        schedule; this is the domain action it calls."""
        today = date.today()
        notified = 0
        for window in (90, 60, 30, 15):
            horizon = today + timedelta(days=window)
            contracts = self.search(
                [
                    ("state", "=", "active"),
                    ("auto_renew", "=", True),
                    ("date_end", "<=", horizon),
                    ("date_end", ">", today),
                ]
            )
            for contract in contracts:
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
                notified += 1
        return notified

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
        Visit = self.env["fix.contract.pm.visit"]
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


class FixContractEntitlement(models.Model):
    """What a contract buys and how consumption draws it down (T03).

    Quantity models: visits per term, incidents per term, hours per term —
    drawn down by M01 consumption events; never negative."""

    _name = "fix.contract.entitlement"
    _description = "Contract Entitlement"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
    quantity_consumed = fields.Float(default=0.0, copy=False)
    quantity_remaining = fields.Float(compute="_compute_remaining", store=True)
    device_id = fields.Many2one(
        "fix.device", string="Specific Asset", help="Empty = the whole covered estate"
    )

    @api.depends("quantity_included", "quantity_consumed")
    def _compute_remaining(self):
        for ent in self:
            if ent.quantity_included == 0:
                ent.quantity_remaining = -1  # sentinel: unlimited
            else:
                ent.quantity_remaining = ent.quantity_included - ent.quantity_consumed

    def consume(self, qty: float, source_ref: str = "") -> bool:
        """Draw down. Returns False when the entitlement is exhausted — the
        caller (M01) then treats the order as standard/paid, not AMC."""
        for ent in self:
            if ent.quantity_included == 0:  # unlimited
                ent.quantity_consumed += qty
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
            ent.quantity_consumed += qty
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
                    ("state", "=", "active"),
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
                    ("state", "=", "active"),
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
    def entitlement_active(self, device_id: int, category: str) -> bool:
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
        exhausted contract does not hide another's balance)."""
        contracts = self.env["fix.contract"].search(
            [
                ("state", "=", "active"),
                ("covered_device_ids", "in", [device_id]),
                ("family", "=", category),
            ]
        )
        remaining = contracts.entitlement_ids.filtered(
            lambda ent: ent.device_id.id in (False, device_id)
            and (ent.quantity_included == 0 or ent.quantity_remaining > 0)
        )
        return bool(remaining)


class FixContractPmVisit(models.Model):
    """One preventive-maintenance visit on the schedule (T06)."""

    _name = "fix.contract.pm.visit"
    _description = "Preventive Maintenance Visit"
    _inherit = ["mail.thread"]

    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    device_id = fields.Many2one("fix.device", required=True, ondelete="cascade")
    scheduled_date = fields.Date(required=True)
    service_order_id = fields.Many2one("fix.service.order", string="Service Order", readonly=True)
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
    )

    def action_create_service_order(self):
        """Feeds dispatch: the PM visit opens as a service order on the
        covered device, category mapped from the contract family."""
        Order = self.env["fix.service.order"]
        for visit in self:
            if visit.service_order_id:
                continue
            category = "amc" if visit.contract_id.family == "amc" else "standard"
            order = Order.create(
                {
                    "device_id": visit.device_id.id,
                    "customer_id": visit.contract_id.customer_id.id,
                    "branch_id": visit.device_id.branch_id.id,
                    "fault_description": "Preventive maintenance visit (%s)"
                    % visit.contract_id.code,
                    "order_category": category,
                }
            )
            visit.write({"service_order_id": order.id, "state": "dispatched"})
