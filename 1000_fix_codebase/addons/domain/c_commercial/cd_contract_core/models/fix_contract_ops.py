# M08 contract lifecycle operations: amendments, renewals and terminations on
# top of fix.contract / fix.contract.entitlement / fix.contract.pm.visit.
from odoo import fields, models


class FixContractAmendment(models.Model):
    _name = "fix.contract.amendment"
    _description = "Contract Amendment"
    _order = "effective_from desc, id desc"

    name = fields.Char(required=True)
    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    kind = fields.Selection(
        [("pricing", "Pricing change"), ("scope", "Scope change"), ("term", "Term change")],
        required=True,
        default="scope",
    )
    delta_value = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    effective_from = fields.Date(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("applied", "Applied")],
        required=True,
        default="draft",
    )
    note = fields.Char()


class FixContractRenewal(models.Model):
    _name = "fix.contract.renewal"
    _description = "Contract Renewal"
    _order = "proposed_start, id"

    name = fields.Char(required=True)
    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    proposed_start = fields.Date(required=True)
    proposed_end = fields.Date(required=True)
    propo_value = fields.Monetary(currency_field="currency_id", string="Proposed Value")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("quoted", "Quoted"), ("won", "Won"), ("lost", "Lost")],
        required=True,
        default="draft",
    )


class FixContractTermination(models.Model):
    _name = "fix.contract.termination"
    _description = "Contract Suspension / Termination"
    _order = "effective_date desc, id desc"

    name = fields.Char(required=True)
    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    kind = fields.Selection(
        [("suspension", "Suspension"), ("termination", "Termination")],
        required=True,
        default="termination",
    )
    reason = fields.Char(required=True)
    effective_date = fields.Date(required=True)
    notice_ok = fields.Boolean(string="Notice Period Satisfied")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    penalty_amount = fields.Monetary(
        string="Termination Penalty / Break Fee", currency_field="currency_id", default=0.0
    )
    dofa_tier = fields.Selection(
        [
            ("tier1", "Tier 1 - Commercial Director (<500K BDT)"),
            ("tier2", "Tier 2 - Managing Director (<2M BDT)"),
            ("tier3", "Tier 3 - Board of Directors (>=2M BDT)"),
        ],
        string="Required DOFA Tier",
        default="tier1",
        required=True,
    )
    dofa_approver_id = fields.Many2one("res.users", string="DOFA Approver", readonly=True)
    dofa_approved = fields.Boolean(string="DOFA Approved", default=False, readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("effective", "Effective")],
        required=True,
        default="draft",
    )

    def action_dofa_approve(self):
        """DOFA approval gate before contract termination can be enacted."""
        for rec in self:
            rec.write(
                {
                    "dofa_approved": True,
                    "dofa_approver_id": self.env.user.id,
                    "state": "approved",
                }
            )

    def action_execute_termination(self):
        """Enact the termination on the underlying contract."""
        for rec in self:
            if not rec.dofa_approved or rec.state != "approved":
                raise models.UserError(
                    "Termination requires DOFA approval prior to execution (DOFA governance control)."
                )
            rec.state = "effective"
            if rec.kind == "termination":
                rec.contract_id.write({"state": "terminated"})
            elif rec.kind == "suspension":
                rec.contract_id.write({"state": "expired"})
            from libs.py.fix_events import publish

            publish(
                self.env,
                "contract.terminated",
                "fix.contract.termination",
                rec.id,
                {
                    "contract_id": rec.contract_id.id,
                    "kind": rec.kind,
                    "effective_date": str(rec.effective_date),
                    "penalty_amount": float(rec.penalty_amount or 0.0),
                },
            )
