# cd_workflow_engine — M63 Process Automation & Workflow Orchestration
# (P06-M08-T03/T04, CD-M63-01/04).
#
# BRU-MDM-15's shape applied to automation: M63 STORES the automation
# register (data), the engines EXECUTE. Every AUT-001..060 row carries a
# named engine — odoo_automated_action | airflow | domain_service — loaded
# from data/aut_register.yaml (the 05-05 section 12 catalogue).
#
# T03 companion: this closes the M63 -> M27 violation — automations that
# notify do so by PUBLISHING EVENTS the notification dispatcher (W1, live)
# consumes; M63 never calls M27.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

import yaml

from pathlib import Path

from libs.py.fix_events import publish  # FF-28

ENGINES = [
    ("odoo_automated_action", "Odoo Automated Action (event + server action)"),
    ("airflow", "Apache Airflow (scheduled / threshold workflow)"),
    ("domain_service", "Domain Service (named L5 engine)"),
]


class FixAutomation(models.Model):
    """One row of the AUT register with its named execution engine."""

    _name = "fix.automation"
    _description = "Business Automation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint('UNIQUE (code)', 'AUT code must be unique')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    code = fields.Char(string="AUT Code", required=True, size=10, index=True)
    trigger = fields.Char(string="Trigger", required=True)
    action = fields.Text(string="Action", required=True)
    engine = fields.Selection(ENGINES, required=True,
                              help="T04: every automation has a named engine")
    engine_ref = fields.Char(string="Engine Reference",
                             help="Server-action xml id / Airflow dag_id / service route")
    active = fields.Boolean(default=True)
    failure_policy = fields.Selection(
        [("manual_fallback", "Manual Fallback (the catalogue's named fallback)"),
         ("retry", "Retry then alert")],
        default="manual_fallback", required=True,
        help="The catalogue names each automation's fallback; the engine honours it")

    @api.constrains("code")
    def _check_code(self):
        for automation in self:
            if not automation.code.startswith("AUT-"):
                raise ValidationError("AUT codes are AUT-nnn")

    @api.model
    def action_load_register(self) -> int:
        """Load/refresh the register from data/aut_register.yaml (the
        catalogue extract). Idempotent on code."""
        register_path = Path(__file__).parent.parent / "data" / "aut_register.yaml"
        data = yaml.safe_load(register_path.read_text(encoding="utf-8"))
        existing = {a.code for a in self.search([])}
        loaded = 0
        for row in data["automations"]:
            engine_ref = row.get("engine_ref") or self._default_engine_ref(row["engine"])
            if row["id"] in existing:
                rec = self.search([("code", "=", row["id"])], limit=1)
                if rec and (not rec.engine_ref or "created at activation" in str(rec.engine_ref) or "Airflow sync" in str(rec.engine_ref) or "named in the action" in str(rec.engine_ref)):
                    rec.write({"engine_ref": engine_ref})
                continue
            self.create({
                "code": row["id"],
                "trigger": row["trigger"],
                "action": row["action"],
                "engine": row["engine"],
                "engine_ref": engine_ref,
            })
            loaded += 1
        publish(self.env, "automation.register.loaded", "fix.automation", 0,
                {"loaded": loaded, "total": len(data["automations"])})
        return loaded

    @api.model
    def _default_engine_ref(self, engine: str) -> str:
        return {
            "odoo_automated_action": "ir.actions.server (created at activation)",
            "airflow": "dag: fix_< AUT id lowercase > (Airflow sync)",
            "domain_service": "route: services/* engine named in the action",
        }[engine]

    def action_report_engine_gap(self):
        """G3 evidence: any automation without a concrete engine_ref after
        activation is a gap, reported — never assumed done."""
        placeholders = [
            False,
            "",
            self._default_engine_ref("odoo_automated_action"),
            self._default_engine_ref("airflow"),
            self._default_engine_ref("domain_service"),
        ]
        return self.search_read(
            [("engine_ref", "in", placeholders)],
            ["code", "engine", "trigger", "engine_ref"])


class FixApprovalMatrix(models.Model):
    """CD-M63-02 seam: the approval authority matrix one place — reused by
    credit notes, discounts, adjustments and write-offs (each already
    enforces its own threshold; this is the consolidated register)."""

    _name = "fix.approval.matrix"
    _description = "Approval Authority Matrix"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M63",
        "form": "Approval Chain",
        "fields": ["decision_domain", "threshold", "approver_role", "notes"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _domain_threshold_unique = models.Constraint('UNIQUE (decision_domain, currency_id)', 'One threshold per decision domain and currency')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    decision_domain = fields.Selection(
        [("estimate", "Estimate Approval"), ("credit_note", "Credit Note"),
         ("discount", "Discount"), ("adjustment", "Stock Adjustment"),
         ("write_off", "Write-Off"), ("expense", "Expense Claim"),
         ("requisition", "Requisition")], required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    threshold = fields.Monetary(string="Threshold", currency_field="currency_id",
                                required=True,
                                help="At or below: delegated; above: the named role approves")
    approver_role = fields.Char(string="Approver Role (R-nn)", required=True,
                                help="From the reconciled 53-role register")
    notes = fields.Char()
