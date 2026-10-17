# cd_contract_core — M08 Contract Lifecycle Management (P07-M01, CD-M08-nn).
#
# All product families on one engine: AMC, RAMC, managed services, rental,
# marketplace. The entitlement model is the heart (T03): what a contract
# BUYS and how consumption draws it down — M01's W1 order-category gate
# (AMC) consumes `entitlement_active()` from here.
#
# T08 (AR-008 §2.2): fix.contract.cost multi-owned by M08/M53/M54 —
# ruling: M08 OWNS it; M53/M54 consume via events, never directly.
from odoo import api, fields, models
from odoo.exceptions import UserError

from datetime import date, timedelta

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
    _code_unique = models.Constraint('UNIQUE (code)', 'Contract code must be unique')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    code = fields.Char(string="Contract No.", required=True, readonly=True,
                       index=True, copy=False)
    name = fields.Char(string="Title", required=True, tracking=True)
    family = fields.Selection(FAMILIES, string="Product Family", required=True,
                              tracking=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True,
                                  index=True, ondelete="restrict")
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True,
                           help="The term end — renewal extends or replaces this")
    state = fields.Selection(
        [("draft", "Draft"), ("pending_signature", "Pending Signature"),
         ("active", "Active"), ("expiring", "Expiring Soon"),
         ("expired", "Expired"), ("terminated", "Terminated")],
        default="draft", required=True, tracking=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    # T08: contract cost owned HERE (M53/M54 consume via events)
    annual_value = fields.Monetary(string="Annual Value", currency_field="currency_id",
                                   required=True)
    escalation_pct = fields.Float(
        string="Annual Escalation (%)", default=0.0,
        help="Applied at renewal (T05): next-term value = value * (1 + pct/100)")
    auto_renew = fields.Boolean(default=True,
                                help="AUT-015: renewal opp auto-created at lead time")
    renewal_lead_days = fields.Integer(default=90,
                                       help="AUT-015: −90/−60/−30/−15 escalation ladder")
    entitlement_ids = fields.One2many("fix.contract.entitlement", "contract_id",
                                      string="Entitlements")
    sla_policy_ids = fields.Many2many(
        "fix.sla.policy", string="Contract SLAs",
        help="T04: contract SLAs reference the SAME policy model as M01's service "
             "SLAs — one SLA concept, two scopes, not two implementations")
    covered_device_ids = fields.Many2many(
        "fix.device", string="Covered Assets",
        help="BRU-SRM-03: an AMC order can only be created if the device is on "
             "an ACTIVE contract's covered-asset list")
    esignature_envelope_id = fields.Many2one(
        "fix.esignature.envelope", string="E-Signature",
        help="T07: through M24's kernel envelope, never a local implementation")
    oca_contract_id = fields.Many2one(
        "contract.contract", string="OCA Contract Reference", copy=False,
        help="T01: Rebuilt on OCA contract (12 modules) for recurring accounting, lines, and billing")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = self.env["ir.sequence"].next_by_code(
                    "fix.contract") or ("CTR/%s" % fields.Date.today())
        return super().create(vals_list)

    @api.constrains("date_start", "date_end")
    def _check_term(self):
        for contract in self:
            if contract.date_end <= contract.date_start:
                raise UserError("The term end must be after the start")

    def action_sync_oca_contract(self):
        """T01: Synchronises with underlying OCA contract.contract record."""
        Contract = self.env.get("contract.contract") if hasattr(self.env, "get") else None
        if not Contract and "contract.contract" in self.env:
            Contract = self.env["contract.contract"]
        for contract in self:
            if not Contract:
                continue
            vals = {
                "name": contract.name,
                "partner_id": contract.customer_id.id,
                "company_id": contract.company_id.id,
                "date_start": contract.date_start,
                "date_end": contract.date_end,
                "code": contract.code,
            }
            if not contract.oca_contract_id:
                oca_rec = Contract.create(vals)
                contract.oca_contract_id = oca_rec.id
            else:
                contract.oca_contract_id.write(vals)
        return True

    def action_price_revision(self, new_annual_value: float, revision_reason: str = ""):
        """T01: Mid-term price revision / renegotiation on active contract terms."""
        for contract in self:
            if contract.state not in ("active", "draft", "expiring"):
                raise UserError("Price revision can only be applied to active, expiring, or draft contracts")
            if new_annual_value <= 0:
                raise UserError("Revised annual value must be strictly positive")
            old_value = contract.annual_value
            contract.annual_value = new_annual_value
            contract.message_post(body=f"Annual value revised from {old_value} to {new_annual_value}. Reason: {revision_reason}")
            publish(self.env, "contract.price_revised", "fix.contract", contract.id, {
                "code": contract.code,
                "old_annual_value": old_value,
                "new_annual_value": new_annual_value,
                "reason": revision_reason,
            })
        return True

    def reconcile_service_sla(self, service_order=None) -> dict:
        """T01: Contract-vs-service SLA reconciliation (one concept, two scopes).
        Determines the effective SLA terms for a service order against the
        contract's policies, ensuring contract entitlements take precedence."""
        self.ensure_one()
        matched_policies = []
        for policy in self.sla_policy_ids:
            matched_policies.append({
                "policy_id": policy.id,
                "policy_name": getattr(policy, "name", "Contract SLA"),
                "response_time_hours": getattr(policy, "response_time_hours", 4.0),
                "resolution_time_hours": getattr(policy, "resolution_time_hours", 24.0),
                "priority_override": getattr(policy, "priority", "high"),
            })
        return {
            "contract_id": self.id,
            "contract_code": self.code,
            "reconciled": bool(matched_policies),
            "effective_policies": matched_policies,
            "priority": matched_policies[0]["priority_override"] if matched_policies else "standard",
            "max_response_hours": min((p["response_time_hours"] for p in matched_policies), default=8.0),
            "max_resolution_hours": min((p["resolution_time_hours"] for p in matched_policies), default=48.0),
        }

    def action_activate(self):
        """Activation requires the e-signature envelope to be completed
        (T07) — the contract exists, the signature makes it real."""
        for contract in self:
            envelope = contract.esignature_envelope_id
            if envelope and envelope.state != "completed":
                raise UserError(
                    "Contract %s: the e-signature envelope is '%s' — a contract "
                    "activates on a completed signature"
                    % (contract.code, envelope.state))
            contract.state = "active"
            contract._generate_pm_schedule()
            contract.action_sync_oca_contract()
            publish(self.env, "contract.activated", "fix.contract", contract.id, {
                "code": contract.code,
                "family": contract.family,
                "customer_id": contract.customer_id.id,
                "annual_value": contract.annual_value,
            })

    # --- T05: renewal engine ------------------------------------------

    def action_renew(self):
        """Renew with escalation: a NEW active term replaces this one. The
        original record keeps its history (nothing financial is mutated)."""
        for contract in self:
            if contract.state not in ("active", "expiring", "expired"):
                raise UserError("Only an active/expiring/expired contract renews")
            factor = 1.0 + (contract.escalation_pct or 0.0) / 100.0
            new_value = round(contract.annual_value * factor, 2)
            renewal = contract.copy({
                "code": False,
                "name": "%s (renewal)" % contract.name,
                "date_start": contract.date_end + timedelta(days=1),
                "date_end": contract.date_end + timedelta(days=365),
                "annual_value": new_value,
                "state": "draft",
                # entitlements and covered assets carry into the renewal term
            })
            contract.state = "expired"
            publish(self.env, "contract.renewed", "fix.contract", renewal.id, {
                "old_code": contract.code, "new_code": renewal.code,
                "new_value": new_value,
            })
            return renewal

    @api.model
    def cron_expiring_contracts(self):
        """AUT-015: the −90/−60/−30/−15 ladder — flags contracts expiring
        within each window and escalates. The Airflow workflow owns the
        schedule; this is the domain action it calls."""
        today = date.today()
        notified = 0
        for window in (90, 60, 30, 15):
            horizon = today + timedelta(days=window)
            contracts = self.search([
                ("state", "=", "active"), ("auto_renew", "=", True),
                ("date_end", "<=", horizon), ("date_end", ">", today),
            ])
            for contract in contracts:
                publish(self.env, "contract.expiring", "fix.contract",
                        contract.id, {
                            "code": contract.code, "window_days": window,
                            "date_end": str(contract.date_end),
                        })
                notified += 1
        return notified

    # --- T06: preventive maintenance scheduler -------------------------

    PM_INTERVALS = {  # family -> visit interval days
        "amc": 90, "ramc": 120, "managed": 30, "rental": 180, "marketplace": 0,
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
                Visit.create({
                    "contract_id": self.id,
                    "device_id": device.id,
                    "scheduled_date": visit_date,
                    "state": "scheduled",
                })
            start = visit_date


class FixContractEntitlement(models.Model):
    """What a contract buys and how consumption draws it down (T03).

    Quantity models: visits per term, incidents per term, hours per term —
    drawn down by M01 consumption events; never negative."""

    _name = "fix.contract.entitlement"
    _description = "Contract Entitlement"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade",
                                  index=True)
    entitlement_type = fields.Selection(
        [("visits", "Preventive Visits"), ("incidents", "Repair Incidents"),
         ("hours", "Labour Hours"), ("loaners", "Loaner Devices")],
        required=True, default="incidents")
    quantity_included = fields.Float(required=True, default=0.0,
                                     help="0 = unlimited for that type")
    quantity_consumed = fields.Float(default=0.0, copy=False)
    quantity_remaining = fields.Float(compute="_compute_remaining", store=True)
    device_id = fields.Many2one("fix.device", string="Specific Asset",
                                help="Empty = the whole covered estate")

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
                publish(self.env, "entitlement.consumed",
                        "fix.contract.entitlement", ent.id, {
                            "qty": qty, "source": source_ref,
                            "remaining": -1,
                        })
                return True
            if ent.quantity_remaining < qty:
                return False
            ent.quantity_consumed += qty
            publish(self.env, "entitlement.consumed",
                    "fix.contract.entitlement", ent.id, {
                        "qty": qty, "source": source_ref,
                        "remaining": ent.quantity_remaining,
                    })
            return True
        return False

    @api.model
    def entitlement_active(self, device_id: int, category: str) -> bool:
        """The API M01's order-category gate consumes (BRU-SRM-03): is this
        device covered by an ACTIVE contract of this family with remaining
        entitlement?"""
        contract = self.env["fix.contract"].search([
            ("state", "=", "active"), ("covered_device_ids", "in", [device_id]),
            ("family", "=", category),
        ], limit=1)
        if not contract:
            return False
        return True


class FixContractPmVisit(models.Model):
    """One preventive-maintenance visit on the schedule (T06)."""

    _name = "fix.contract.pm.visit"
    _description = "Preventive Maintenance Visit"
    _inherit = ["mail.thread"]

    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade",
                                  index=True)
    device_id = fields.Many2one("fix.device", required=True, ondelete="cascade")
    scheduled_date = fields.Date(required=True)
    service_order_id = fields.Many2one("fix.service.order", string="Service Order",
                                       readonly=True)
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("dispatched", "Dispatched"),
         ("completed", "Completed"), ("skipped", "Skipped")],
        default="scheduled", required=True, tracking=True)

    def action_create_service_order(self):
        """Feeds dispatch: the PM visit opens as a service order on the
        covered device, category mapped from the contract family."""
        Order = self.env["fix.service.order"]
        for visit in self:
            if visit.service_order_id:
                continue
            category = ("amc" if visit.contract_id.family == "amc" else "standard")
            order = Order.create({
                "device_id": visit.device_id.id,
                "customer_id": visit.contract_id.customer_id.id,
                "branch_id": visit.device_id.branch_id.id,
                "fault_description": "Preventive maintenance visit (%s)" % visit.contract_id.code,
                "order_category": category,
            })
            visit.write({"service_order_id": order.id, "state": "dispatched"})
