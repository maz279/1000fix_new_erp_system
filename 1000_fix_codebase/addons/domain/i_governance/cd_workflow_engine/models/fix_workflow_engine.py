# cd_workflow_engine — M63 Process Automation & Workflow Orchestration
# (P06-M08-T03/T04, CD-M63-01/04).
#
# BRU-MDM-15's shape applied to automation: M63 STORES the automation
# register (data), the engines EXECUTE. Since 19.0.1.2.0 every AUT-001..060
# row names the mechanism that REALLY executes it on this estate and is
# verified at runtime:
#   odoo_cron       an ir.cron scheduled action          cron:<module>.<xmlid>
#   odoo_method     a model method on a document step    method:<model>.<method>
#   event_consumer  an outbox event consumer             consumer:<event_type>
#   manual          no automation executes the row       (no reference)
# `implementation` says how much of the described behaviour the executor
# performs; `executor_note` says where the code lives. The 19.0.1.1.0 values
# (odoo_automated_action / airflow / domain_service) were retired: 0 of the
# 60 references resolved to anything executable (A4-F01).
#
# T03 companion: this closes the M63 -> M27 violation — automations that
# notify do so by PUBLISHING EVENTS the notification dispatcher (W1, live)
# consumes; M63 never calls M27.
import logging
from pathlib import Path

import yaml
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

_logger = logging.getLogger(__name__)

ENGINES = [
    ("odoo_cron", "Odoo scheduled action (ir.cron)"),
    ("odoo_method", "Odoo model method (runs on a document transition)"),
    ("event_consumer", "Event consumer (outbox event → consumer)"),
    ("manual", "Manual step — no automation executes this"),
]

IMPLEMENTATIONS = [
    ("full", "Fully implemented by the named executor"),
    ("partial", "Partially implemented — see the executor note"),
    ("none", "Not implemented — nothing executes this"),
]

# Retired in 19.0.1.2.0 (A4-F01). Kept as data so the migration (and the
# operator reading it) can name what it is deactivating.
RETIRED_ENGINES = ("odoo_automated_action", "airflow", "domain_service")

DOA_ADMIN = "cd_workflow_engine.group_doa_administrator"


class FixAutomation(models.Model):
    """One row of the AUT register with its verified execution engine."""

    _name = "fix.automation"
    _description = "Business Automation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint("UNIQUE (code)", "AUT code must be unique")

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(string="AUT Code", required=True, size=10, index=True)
    trigger = fields.Char(string="Trigger", required=True)
    action = fields.Text(string="Action", required=True)
    engine = fields.Selection(
        ENGINES,
        required=True,
        help="T04: what executes this row. The reference is resolved at "
        "runtime — a row whose engine_ref does not resolve cannot be active.",
    )
    engine_ref = fields.Char(
        string="Engine Reference",
        help="cron:<module>.<xmlid> | method:<model>.<method> | "
        "consumer:<event_type> — empty for engine 'manual'",
    )
    implementation = fields.Selection(
        IMPLEMENTATIONS,
        required=True,
        default="none",
        help="How much of the described behaviour the named executor really "
        "performs. 'partial' rows say what is missing in the executor note.",
    )
    executor_note = fields.Text(
        string="Executor Note",
        help="Where the real code lives (module + file:line), or why nothing does",
    )
    active = fields.Boolean(default=True)
    failure_policy = fields.Selection(
        [
            ("manual_fallback", "Manual Fallback (the catalogue's named fallback)"),
            ("retry", "Retry then alert"),
        ],
        default="manual_fallback",
        required=True,
        help="The catalogue names each automation's fallback; the engine honours it",
    )

    # ------------------------------------------------------------------
    # The honest binding (A4-F01): one resolver for the computed fields,
    # the gap report and the write guard, so they can never disagree.
    # ------------------------------------------------------------------
    binding_state = fields.Selection(
        [("verified", "Verified"), ("unresolved", "Unresolved"), ("manual", "Manual")],
        string="Binding",
        compute="_compute_binding",
        help="Does the engine reference resolve to something executable, right "
        "now, on this database?",
    )
    executor_active = fields.Boolean(
        string="Executor Active",
        compute="_compute_binding",
        help="The cron is active / the method exists / the consumer row is active",
    )
    coverage_state = fields.Selection(
        [
            ("implemented", "Implemented (full + verified)"),
            ("partial", "Partial (verified binding)"),
            ("planned", "Planned (not implemented)"),
            ("broken", "Broken (claims an implementation, reference unresolved)"),
        ],
        string="Coverage",
        compute="_compute_binding",
        help="implemented = full + verified; partial = partial + verified; "
        "planned = nothing implements it; broken = it claims an implementation "
        "its reference cannot back.",
    )

    @api.depends("engine", "engine_ref", "implementation")
    def _compute_binding(self):
        for automation in self:
            state, executor_active, _problem = automation._binding_resolver()
            automation.binding_state = state
            automation.executor_active = executor_active
            if state == "manual" or automation.implementation == "none":
                automation.coverage_state = "planned"
            elif state != "verified":
                automation.coverage_state = "broken"
            else:
                automation.coverage_state = (
                    "implemented" if automation.implementation == "full" else "partial"
                )

    def _binding_resolver(self):
        """Resolve one row's reference against the runtime.

        Returns (binding_state, executor_active, problem):
          binding_state    'verified' | 'unresolved' | 'manual'
          executor_active  cron.active / method callable / consumer.active
          problem          '' or the specific reason a reference did not
                           resolve (the write guard names it to the operator).

        env.ref() honours its own access rules; nothing here needs sudo
        beyond reading the consumer register, which is an integration
        record no internal business user may edit."""
        self.ensure_one()
        ref = (self.engine_ref or "").strip()
        if self.engine == "manual":
            return "manual", False, ""
        if self.engine == "odoo_cron":
            xmlid = ref[len("cron:") :] if ref.startswith("cron:") else ""
            module, _dot, name = xmlid.partition(".")
            # addon names carry no dot; the xmlid name part must not either
            if not module or not name or "." in name:
                return (
                    "unresolved",
                    False,
                    "engine odoo_cron expects cron:<module>.<xmlid>, got %r" % self.engine_ref,
                )
            cron = self.env.ref(xmlid, raise_if_not_found=False)
            if cron is None or cron._name != "ir.cron":
                return "unresolved", False, "ir.cron %s does not exist" % xmlid
            return "verified", bool(cron.active), ""
        if self.engine == "odoo_method":
            target = ref[len("method:") :] if ref.startswith("method:") else ""
            # model names contain dots, method names never do: split on the
            # LAST dot
            model_name, _dot, method = target.rpartition(".")
            if not model_name or not method:
                return (
                    "unresolved",
                    False,
                    "engine odoo_method expects method:<model>.<method>, got %r" % self.engine_ref,
                )
            model = self.env.get(model_name)
            if model is None:
                return "unresolved", False, "model %s is not in the registry" % model_name
            if not callable(getattr(model, method, None)):
                return (
                    "unresolved",
                    False,
                    "%s has no callable method %s" % (model_name, method),
                )
            return "verified", True, ""
        if self.engine == "event_consumer":
            event_type = ref[len("consumer:") :] if ref.startswith("consumer:") else ""
            if not event_type:
                return (
                    "unresolved",
                    False,
                    "engine event_consumer expects consumer:<event_type>, got %r" % self.engine_ref,
                )
            consumers = (
                self.env["fix.event.consumer"].sudo().search([("event_type", "=", event_type)])
            )
            if not consumers:
                return (
                    "unresolved",
                    False,
                    "no fix.event.consumer subscribes to %s" % event_type,
                )
            live = consumers.filtered("active")
            if not live:
                return (
                    "unresolved",
                    False,
                    "every fix.event.consumer of %s is switched off" % event_type,
                )
            for consumer in live:
                model = self.env.get(consumer.model)
                if model is None or not callable(getattr(model, consumer.method, None)):
                    return (
                        "unresolved",
                        False,
                        "consumer %s.%s does not resolve" % (consumer.model, consumer.method),
                    )
            return "verified", True, ""
        # a retired or unknown engine value can never resolve
        return (
            "unresolved",
            False,
            "engine %r is not a value of the honest taxonomy" % self.engine,
        )

    # ------------------------------------------------------------------
    # Fail-closed write guard (BRU-BPA-01): an ACTIVE row must have a
    # binding that resolves — or be an honest manual/not-implemented row.
    # ------------------------------------------------------------------
    def _fix_assert_bindable(self):
        for automation in self:
            if automation.engine == "manual":
                if automation.implementation != "none":
                    raise UserError(
                        "AUT %s: engine 'manual' cannot carry implementation '%s' — "
                        "name the real executor, or mark the row not implemented."
                        % (automation.code, automation.implementation)
                    )
                continue
            state, _active, problem = automation._binding_resolver()
            if automation.active and state != "verified":
                raise UserError(
                    "AUT %s is active but its engine reference does not resolve: %s. "
                    "Fix the reference, or set engine 'manual' with implementation "
                    "'none' and deactivate the row." % (automation.code, problem)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # A manual row with nothing implementing it is not "live": the
            # Active flag would claim an automation nobody runs, and the gap
            # report would flag it on the next read. Only an explicit Active
            # in the values overrides this.
            if (
                vals.get("engine") == "manual"
                and vals.get("implementation", "none") == "none"
                and "active" not in vals
            ):
                vals["active"] = False
        automations = super().create(vals_list)
        automations._fix_assert_bindable()
        return automations

    def write(self, vals):
        result = super().write(vals)
        if {"active", "engine", "engine_ref", "implementation"} & set(vals):
            self._fix_assert_bindable()
        return result

    @api.model
    def _catalogue_create(self, vals_list):
        """Create WITHOUT the write guard — the catalogue loader's own path.

        Why the guard cannot apply here: a migration runs while the registry
        still holds only the modules loaded before this one (Odoo 19 runs a
        module's post-migrate scripts inside the module graph), so a
        `method:` reference to a model of a later-loaded addon would read as
        'not in the registry' and the loader could never load the catalogue.
        The YAML is authored data, not a user edit; the verification net is
        the runtime gap report (action_report_engine_gap) plus the
        automation.register.loaded consumer, which raise a to-do on every
        broken row. Every RPC write still goes through write() -> the guard.
        """
        return super().create(vals_list)

    def _catalogue_write(self, vals):
        return super().write(vals)

    @api.constrains("code")
    def _check_code(self):
        for automation in self:
            if not automation.code.startswith("AUT-"):
                raise ValidationError("AUT codes are AUT-nnn")

    # ------------------------------------------------------------------
    # Loader / gap report / register-loaded consumer
    # ------------------------------------------------------------------
    @api.model
    def action_load_register(self) -> int:
        """Load/refresh the register from data/aut_register.yaml.

        Idempotent on code, and honest: every row is (re)written to exactly
        what the catalogue says about engine, engine_ref, implementation,
        executor_note and failure_policy, and a row the estate does not
        implement is deactivated. `trigger` and `action` are the business's
        own words and are never overwritten.

        The catalogue is authored data, so it is written through
        _catalogue_write / _catalogue_create (no bindability guard): a
        migration runs with a partial registry and could not resolve a
        later-loaded model's method. A row whose reference really does not
        resolve at runtime is reported as 'broken' by
        action_report_engine_gap and given a to-do by the
        automation.register.loaded consumer — that is the verification net,
        not an assumed-good load."""
        register_path = Path(__file__).parent.parent / "data" / "aut_register.yaml"
        data = yaml.safe_load(register_path.read_text(encoding="utf-8"))
        # active_test=False: a DEACTIVATED automation still owns its code; a
        # reload must not try to re-create it against the UNIQUE(code) key.
        automations = self.with_context(active_test=False)
        existing = {a.code: a for a in automations.search([])}
        loaded = refreshed = 0
        for row in data["automations"]:
            vals = {
                "engine": row["engine"],
                "engine_ref": row.get("engine_ref") or "",
                "implementation": row["implementation"],
                "executor_note": row.get("executor_note") or "",
                "failure_policy": row.get("failure_policy") or "manual_fallback",
            }
            if row["implementation"] == "none":
                # an unimplemented automation never counts as live; the reverse
                # is NOT done — an operator may switch a working automation off
                # for a maintenance window, and a reload must not revive it.
                vals["active"] = False
            rec = existing.get(row["id"])
            if rec is not None:
                changed = {}
                for key, value in vals.items():
                    # a Char field reads back False when empty, never ""
                    current = (rec[key] or "") if isinstance(value, str) else rec[key]
                    if current != value:
                        changed[key] = value
                if changed:
                    rec._catalogue_write(changed)
                    refreshed += 1
                continue
            self._catalogue_create(
                [{"code": row["id"], "trigger": row["trigger"], "action": row["action"], **vals}]
            )
            loaded += 1
        codes = [r["id"] for r in data["automations"]]
        rows = automations.search([("code", "in", codes)])
        states = [row._binding_resolver()[0] for row in rows]
        publish(
            self.env,
            "automation.register.loaded",
            "fix.automation",
            0,
            {
                "loaded": loaded,
                "refreshed": refreshed,
                "verified": states.count("verified"),
                "unresolved": states.count("unresolved"),
                "total": len(data["automations"]),
            },
        )
        return loaded

    def action_report_engine_gap(self):
        """G3 evidence: rows whose claimed implementation their reference
        cannot back ('broken'), plus 'planned' rows still switched on.

        References are RESOLVED (xmlid / model registry / consumer register)
        — never string-matched. The 19.0.1.1.0 report matched only its own
        placeholder strings, so it reported 0 gaps over 60 fictional
        references (A4-F01)."""
        rows = self.with_context(active_test=False).search([])
        gapped = rows.filtered(
            lambda r: r.coverage_state == "broken" or (r.coverage_state == "planned" and r.active)
        ).sorted("code")
        return [
            {
                "code": row.code,
                "engine": row.engine,
                "engine_ref": row.engine_ref,
                "implementation": row.implementation,
                "coverage_state": row.coverage_state,
                "trigger": row.trigger,
            }
            for row in gapped
        ]

    @api.model
    def consume_register_loaded(self, event: dict) -> dict:
        """Relay consumer of automation.register.loaded (FF-48: the event
        used to be published with no consumer — a register reload nobody
        reacted to). When the payload reports unresolved bindings, every
        broken row gets a same-day to-do on an active DoA Administrator's
        desk; with no holder the activity is left unassigned and that is
        logged. Idempotent per event: a redelivered event creates nothing."""
        event_id = event.get("event_id") or ""
        marker = "[automation.register.loaded %s]" % event_id
        Activity = self.env["mail.activity"]
        if event_id and Activity.sudo().search_count(
            [("res_model", "=", "fix.automation"), ("note", "like", marker)]
        ):
            return {"created": 0, "reason": "event already consumed"}
        broken = (
            self.with_context(active_test=False)
            .search([])
            .filtered(lambda r: r.coverage_state == "broken")
        )
        payload = event.get("payload") or {}
        if not broken and not payload.get("unresolved"):
            return {"created": 0, "reason": "every binding resolved"}
        group = self.env.ref(DOA_ADMIN, raise_if_not_found=False)
        owner = (
            group.user_ids.filtered(lambda u: u.active and not u.share)[:1]
            if group
            else self.env["res.users"]
        )
        if not owner:
            _logger.warning(
                "automation.register.loaded: broken automations %s but the DoA "
                "Administrator group has no active holder; to-dos left unassigned",
                ", ".join(broken.mapped("code")),
            )
        today = fields.Date.context_today(self)
        for row in broken:
            _state, _active, problem = row._binding_resolver()
            row.activity_schedule(
                act_type_xmlid="mail.mail_activity_data_todo",
                date_deadline=today,
                summary="Automation %s: engine reference does not resolve — fix "
                "the reference or mark it as not implemented" % row.code,
                note="%s\n%s" % (problem or "the reference does not resolve", marker),
                user_id=owner.id or False,
            )
        return {"created": len(broken), "event": event_id or "(no event id)"}


class FixApprovalMatrix(models.Model):
    """CD-M63-02 seam: the approval authority matrix one place — reused by
    credit notes, discounts, adjustments and write-offs (each already
    enforces its own threshold; this is the consolidated register)."""

    _name = "fix.approval.matrix"
    _description = "Approval Authority Matrix"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _domain_threshold_unique = models.Constraint(
        "UNIQUE (decision_domain, currency_id)", "One threshold per decision domain and currency"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    decision_domain = fields.Selection(
        [
            ("estimate", "Estimate Approval"),
            ("credit_note", "Credit Note"),
            ("discount", "Discount"),
            ("adjustment", "Stock Adjustment"),
            ("write_off", "Write-Off"),
            ("expense", "Expense Claim"),
            ("requisition", "Requisition"),
        ],
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    threshold = fields.Monetary(
        string="Threshold",
        currency_field="currency_id",
        required=True,
        help="At or below: delegated; above: the named role approves",
    )
    approver_role = fields.Char(
        string="Approver Role (R-nn)", required=True, help="From the reconciled 53-role register"
    )
    notes = fields.Char()
