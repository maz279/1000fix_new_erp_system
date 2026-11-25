# A04 ERP audit, round 2 (21 Nov 2026), M39-F11: one contract is billed by
# exactly one engine.
#
# The M08 walker (cd_billing_engine) bills every in-force contract with an
# annual value, and an M39 subscription on the same contract bills it again.
# The contract now says who bills it. The default is the walker; a Managed
# Services contract defaults to the M39 subscription, because the owner's
# decision D8 (A02 ERP pass 2) made the MSP fee the subscription on the M08
# contract. Any other contract is moved to the subscription only by a person
# who decides it (the Contract Manager), before either engine has billed it.
#
# This module cannot see fix.subscription (cd_subscription depends on it), so
# the subscription side of the guard is in cd_subscription; the walker's side
# is here: a billing period is never raised on a contract billed by M39.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_contract import MANAGER, require_role

BILLING_ENGINES = [
    ("walker", "M08 contract billing (walker)"),
    ("subscription", "M39 subscription"),
]
LIVE_SUBSCRIPTION_EXCLUDED = ("cancelled", "churned")


class FixContractBillingEngine(models.Model):
    _inherit = "fix.contract"

    billing_engine = fields.Selection(
        BILLING_ENGINES,
        string="Billed By",
        compute="_compute_billing_engine",
        store=True,
        readonly=False,
        precompute=True,
        required=True,
        tracking=True,
        help="Which engine invoices this contract: the M08 contract billing hand-off, or "
        "an M39 subscription. Never both (M39-F11).",
    )

    @api.depends("family")
    def _compute_billing_engine(self):
        for rec in self:
            if not rec.billing_engine:
                rec.billing_engine = "subscription" if rec.family == "managed" else "walker"

    def _fix_billing_engine_problem(self, engine):
        """Why this contract may not move to `engine` now (None when it may)."""
        self.ensure_one()
        if engine == self.billing_engine:
            return None
        if engine == "subscription":
            billed = (
                self.env["fix.contract.billing.period"]
                .sudo()
                .search_count([("contract_id", "=", self.id)])
            )
            if billed or self.billed_through_date:
                return (
                    "%s is already billed by the M08 contract billing (through %s): move it to "
                    "M39 at renewal" % (self.code or self.name, self.billed_through_date or "-")
                )
        else:
            Sub = self.env.get("fix.subscription")
            if Sub is not None and Sub.sudo().search_count(
                [("contract_id", "=", self.id), ("state", "not in", LIVE_SUBSCRIPTION_EXCLUDED)]
            ):
                return (
                    "%s has a live M39 subscription that bills it: cancel the subscription before "
                    "the M08 contract billing takes it over" % (self.code or self.name)
                )
        return None

    def write(self, vals):
        if "billing_engine" in vals:
            changing = self.filtered(lambda c: c.billing_engine != vals["billing_engine"])
            if changing and not self.env.su:
                require_role(self.env, MANAGER, "Changing who bills a contract")
            for rec in changing:
                problem = rec._fix_billing_engine_problem(vals["billing_engine"])
                if problem:
                    raise UserError("%s (M39-F11)." % problem)
        return super().write(vals)


class FixContractBillingPeriodEngine(models.Model):
    _inherit = "fix.contract.billing.period"

    @api.model_create_multi
    def create(self, vals_list):
        ids = [v.get("contract_id") for v in vals_list if v.get("contract_id")]
        m39 = (
            self.env["fix.contract"]
            .sudo()
            .browse(ids)
            .filtered(lambda c: c.billing_engine == "subscription")
        )
        if m39:
            raise UserError(
                "%s is billed by its M39 subscription: the M08 contract billing raises no "
                "period on it (M39-F11)." % ", ".join(m39.mapped(lambda c: c.code or c.name))
            )
        return super().create(vals_list)
