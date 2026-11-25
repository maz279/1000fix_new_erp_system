# fix_integration_capture — M28 second capture pass (2026-11-19).
#
# The first pass (2026-11-14) gave every M28 sub-module page a "+ New". Read
# against the spec (M28 s5, s9, s10) rather than counted, five pages still could
# not capture the records the spec names for them:
#
#   * Versioning & Portals (FR-IPF-016): a consumer held ONE key reference. There
#     was no credential per environment, no expiry and no revocation.
#     -> fix.api.credential
#   * Subscriptions & DLQ (FR-IPF-026/031): the in-process subscriptions
#     (fix.event.consumer) were on no screen, and the page's "+ New" was the
#     webhook form of the Webhooks page. Replaying a consumer from a point in time
#     had a method (action_backfill) and no screen, approval or audit.
#     -> fix.event.consumer.replay
#   * Webhooks (FR-IPF-037/038, P0): nothing received a third-party webhook.
#     -> fix.webhook.inbound.source + fix.webhook.inbound.event and the
#        receiver at /hooks/v1/inbound/<code> (controllers/inbound_webhook.py)
#   * Connector Framework (FR-IPF-040/043/045/055, BRU-IPF-12/13): a connector
#     declared no pattern, priority or owner; the "fallback" was one Many2one
#     that recorded no type, user message or test, so "a registered, TESTED
#     fallback" could not be shown; batch file exchange had no record at all.
#     -> fix.connector register fields + go-live gate,
#        fix.integration.fallback, fix.integration.fallback.test,
#        fix.integration.batch.run
#
# Every decision is an Integration Admin's, and every privileged act lands in the
# security audit trail, as with the rest of M28. No secrets manager exists (B-8):
# secrets stay vault:// references, resolved from FIX_VAULT_<PATH> at use.
import base64
import hashlib
import re
import secrets
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_integration import (
    INTEGRATION_ADMIN,
    _bump_vault_ref,
    _integration_audit,
    _param_int,
    _require_integration_admin,
    _required_text,
    _route_to_second_admin,
    _vault_ref_problem,
)

# FR-IPF-040 / BRU-IPF-13: the five patterns an integration may declare (IP-03).
INTEGRATION_PATTERNS = [
    ("sync_request", "Synchronous Request / Response"),
    ("async_command", "Asynchronous Command"),
    ("domain_event", "Domain Event"),
    ("webhook", "Webhook"),
    ("batch_file", "Batch File"),
]
INTEGRATION_PRIORITIES = [("p0", "P0 - Critical"), ("p1", "P1"), ("p2", "P2")]
FALLBACK_TYPES = [
    ("alternate", "Alternate Provider"),
    ("cached", "Cached / Last-Known Data"),
    ("queued", "Queue and Replay on Recovery"),
    ("manual", "Manual Procedure"),
]
API_ENVIRONMENTS = [
    ("production", "Production"),
    ("staging", "Staging"),
    ("sandbox", "Sandbox"),
    ("development", "Development"),
]
BATCH_PURPOSES = [
    ("beftn_payroll", "BEFTN Payroll"),
    ("nbr_return", "NBR Return"),
    ("brand_claim", "Brand Claim Batch"),
    ("bank_statement", "Bank Statement Import"),
    ("other", "Other"),
]
# FR-IPF-031: a replay is bounded so one decision cannot flood a consumer.
REPLAY_MAX_EVENTS_KEY = "fix.integration.replay_max_events"
REPLAY_MAX_EVENTS_DEFAULT = 5000
INBOUND_CODE = re.compile(r"^[a-z0-9][a-z0-9-]{2,39}$")
ROUTE_KEY = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")


def _now():
    return fields.Datetime.now()


# --------------------------------------------------------------------------
# Connector Framework: the integration register (FR-IPF-055) and its gate.
# --------------------------------------------------------------------------
class FixConnectorRegister(models.Model):
    _inherit = "fix.connector"

    int_code = fields.Char(
        string="Integration ID",
        copy=False,
        help="The INT-nnn of the 47-integration register (05-03 s2).",
    )
    pattern = fields.Selection(
        INTEGRATION_PATTERNS,
        help="BRU-IPF-13: every integration declares its pattern. A connector "
        "without one cannot go live.",
    )
    priority = fields.Selection(
        INTEGRATION_PRIORITIES,
        help="BRU-IPF-12: a P0 integration cannot go live without a registered "
        "fallback whose latest test passed.",
    )
    owner_id = fields.Many2one("res.users", string="Integration Owner")
    fallback_ids = fields.One2many("fix.integration.fallback", "connector_id", string="Fallbacks")
    fallback_ready = fields.Boolean(
        compute="_compute_fallback_ready",
        string="Tested Fallback",
        help="An active registered fallback whose latest test passed.",
    )

    _int_code_unique = models.UniqueIndex(
        "(company_id, int_code) WHERE int_code IS NOT NULL",
        "This integration ID is already registered.",
    )

    @api.depends("fallback_ids.active", "fallback_ids.last_test_result")
    def _compute_fallback_ready(self):
        for rec in self:
            rec.fallback_ready = any(
                fb.active and fb.last_test_result == "passed" for fb in rec.sudo().fallback_ids
            )

    def _approval_pinned_fields(self) -> set:
        # Lowering a P0 to escape the fallback gate re-opens the go-live decision.
        return super()._approval_pinned_fields() | {"priority"}

    def _fix_register_problems(self):
        """Why this connector may not be put in service, or [] (BRU-IPF-12/13)."""
        self.ensure_one()
        problems = []
        if not self.pattern:
            problems.append("it declares no integration pattern (BRU-IPF-13)")
        if not self.priority:
            problems.append("it declares no priority")
        if self.priority == "p0" and not self.fallback_ready:
            problems.append(
                "it is P0 and has no registered fallback whose latest test passed "
                "(BRU-IPF-12): register one on Fallbacks and record a passed test"
            )
        return problems

    def _fix_assert_register(self):
        for rec in self:
            problems = rec._fix_register_problems()
            if problems:
                raise UserError("%s cannot go live: %s." % (rec.name, "; ".join(problems)))

    def action_request_go_live(self, justification=None):
        self._fix_assert_register()
        return super().action_request_go_live(justification=justification)

    def _fix_apply_go_live(self):
        # The fallback's test may have been superseded by a failed one since the
        # request: the decision is taken on the register as it is now. Who may
        # approve is decided first: pressed outside the approver's inbox, the
        # routing refusal answers before any content check.
        self._approval_assert_routed()
        self._fix_assert_register()
        return super()._fix_apply_go_live()


class FixIntegrationFallback(models.Model):
    """FR-IPF-043 / BRU-IPF-12: the registered fallback of one integration."""

    _name = "fix.integration.fallback"
    _inherit = ["fix.guarded.mixin"]
    _description = "Integration Fallback"
    _order = "connector_id, id"

    connector_id = fields.Many2one(
        "fix.connector", required=True, index=True, ondelete="cascade", string="Integration"
    )
    company_id = fields.Many2one(
        "res.company", related="connector_id.company_id", store=True, index=True
    )
    fallback_type = fields.Selection(FALLBACK_TYPES, required=True)
    fallback_connector_id = fields.Many2one(
        "fix.connector",
        string="Alternate Connector",
        help="For an alternate provider: the connector traffic moves to.",
    )
    procedure = fields.Text(
        required=True, help="What engages the fallback and what staff do while it runs."
    )
    user_message = fields.Char(
        string="User Message (English)",
        required=True,
        help="What affected users are told while the fallback runs (FR-IPF-043).",
    )
    user_message_bn = fields.Char(string="User Message (Bangla)", required=True)
    active = fields.Boolean(default=True)
    test_ids = fields.One2many("fix.integration.fallback.test", "fallback_id", string="Tests")
    last_tested_at = fields.Datetime(compute="_compute_last_test", store=True)
    last_test_result = fields.Selection(
        [("passed", "Passed"), ("failed", "Failed")],
        compute="_compute_last_test",
        store=True,
        string="Latest Test",
    )

    @api.depends("test_ids.tested_at", "test_ids.result")
    def _compute_last_test(self):
        for rec in self:
            latest = rec.test_ids.sorted(lambda t: (t.tested_at, t.id), reverse=True)[:1]
            rec.last_tested_at = latest.tested_at or False
            rec.last_test_result = latest.result or False

    @api.depends("connector_id", "fallback_type")
    def _compute_display_name(self):
        labels = dict(FALLBACK_TYPES)
        for rec in self:
            rec.display_name = "%s: %s" % (
                rec.connector_id.name or "?",
                labels.get(rec.fallback_type, ""),
            )

    @api.constrains("fallback_type", "fallback_connector_id", "connector_id")
    def _check_alternate(self):
        for rec in self:
            alt = rec.fallback_connector_id
            if rec.fallback_type == "alternate" and not alt:
                raise ValidationError(
                    "An alternate-provider fallback names the alternate connector."
                )
            if alt and alt == rec.connector_id:
                raise ValidationError("A connector cannot be its own fallback.")
            if alt and alt.connector_type != rec.connector_id.connector_type:
                raise ValidationError(
                    "The alternate of a %s connector must be a %s connector."
                    % (rec.connector_id.connector_type, rec.connector_id.connector_type)
                )

    def _fix_form_locked_fields(self):
        # A test proves THIS fallback: once one is recorded, what it proved is fixed.
        locked = set(super()._fix_form_locked_fields())
        if any(rec.test_ids for rec in self):
            locked |= {"connector_id", "fallback_type", "fallback_connector_id", "procedure"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        _require_integration_admin(self.env, "register an integration fallback")
        recs = super().create(vals_list)
        for rec in recs:
            _integration_audit(
                self.env,
                "integration.fallback_registered",
                "fix.integration.fallback,%d" % rec.id,
                "integration.fallback_registered: %s by %s"
                % (rec.display_name, self.env.user.name),
            )
        return recs

    def write(self, vals):
        if not self.env.su:
            _require_integration_admin(self.env, "change an integration fallback")
            tested = {"connector_id", "fallback_type", "fallback_connector_id", "procedure"}
            for rec in self.filtered("test_ids"):
                for name in tested & set(vals):
                    if rec._fix_guard_differs(name, vals[name], rec[name]):
                        raise UserError(
                            "This fallback has been tested: what the test proved cannot "
                            "change. Register a new fallback and test it."
                        )
        return super().write(vals)


class FixIntegrationFallbackTest(models.Model):
    """BRU-IPF-12 'tested': one recorded exercise of a fallback. Evidence, so it
    is never edited: a re-test is a new row."""

    _name = "fix.integration.fallback.test"
    _description = "Integration Fallback Test"
    _order = "tested_at desc, id desc"

    fallback_id = fields.Many2one(
        "fix.integration.fallback", required=True, index=True, ondelete="cascade"
    )
    connector_id = fields.Many2one(
        "fix.connector", related="fallback_id.connector_id", store=True, string="Integration"
    )
    company_id = fields.Many2one(
        "res.company", related="fallback_id.company_id", store=True, index=True
    )
    tested_at = fields.Datetime(required=True, default=lambda self: fields.Datetime.now())
    result = fields.Selection([("passed", "Passed"), ("failed", "Failed")], required=True)
    engage_seconds = fields.Integer(
        string="Seconds to Engage", help="How long the switch-over took, when measured."
    )
    evidence = fields.Text(required=True, help="What was done and what was observed.")
    tested_by_id = fields.Many2one(
        "res.users", string="Recorded By", default=lambda self: self.env.user, readonly=True
    )

    @api.constrains("tested_at", "engage_seconds", "evidence")
    def _check_test(self):
        for rec in self:
            if rec.tested_at and rec.tested_at > _now() + timedelta(minutes=5):
                raise ValidationError("A fallback test cannot be dated in the future.")
            if rec.engage_seconds < 0:
                raise ValidationError("Seconds to engage cannot be negative.")
            if len((rec.evidence or "").strip()) < 10:
                raise ValidationError("State what was done and observed in the test.")

    @api.model_create_multi
    def create(self, vals_list):
        _require_integration_admin(self.env, "record a fallback test")
        for vals in vals_list:
            vals["tested_by_id"] = self.env.uid
        recs = super().create(vals_list)
        for rec in recs:
            fallback = rec.fallback_id.sudo()
            if not fallback.active:
                raise UserError("%s is archived: test an active fallback." % fallback.display_name)
            _integration_audit(
                self.env,
                "integration.fallback_tested",
                "fix.integration.fallback,%d" % fallback.id,
                "integration.fallback_tested: %s %s by %s"
                % (fallback.display_name, rec.result, self.env.user.name),
            )
        return recs

    def write(self, vals):
        if not self.env.su:
            raise UserError("A fallback test is evidence and is never edited: record a new test.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A fallback test is evidence and is never deleted.")
        return super().unlink()


class FixIntegrationBatchRun(models.Model):
    """FR-IPF-045 / AUT-IPF-20: one batch file exchanged with a counterparty,
    with its control totals. Verifying is a second person counting the file and
    finding the declared totals."""

    _name = "fix.integration.batch.run"
    _inherit = ["fix.guarded.mixin"]
    _description = "Batch File Exchange Run"
    _order = "id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    connector_id = fields.Many2one("fix.connector", required=True, index=True, string="Integration")
    direction = fields.Selection([("inbound", "Received"), ("outbound", "Sent")], required=True)
    purpose = fields.Selection(BATCH_PURPOSES, required=True)
    reference = fields.Char(required=True, help="Batch or period reference, e.g. PAYROLL-2026-11.")
    file = fields.Binary(required=True, attachment=True)
    file_name = fields.Char()
    file_sha256 = fields.Char(string="File SHA-256", readonly=True, copy=False)
    declared_records = fields.Integer(required=True, string="Declared Records")
    declared_total = fields.Float(required=True, digits=(16, 2), string="Declared Control Total")
    counted_records = fields.Integer(readonly=True, copy=False)
    counted_total = fields.Float(readonly=True, copy=False, digits=(16, 2))
    state = fields.Selection(
        [("recorded", "Recorded"), ("verified", "Verified"), ("rejected", "Rejected")],
        required=True,
        default="recorded",
    )
    verified_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    verified_at = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Char(readonly=True, copy=False)

    def _fix_guarded_fields(self):
        return super()._fix_guarded_fields() | {
            "state",
            "file_sha256",
            "counted_records",
            "counted_total",
            "verified_by_id",
            "verified_at",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self):
        locked = set(super()._fix_form_locked_fields())
        if self.ids:
            # A recorded file and its declared totals are what gets verified.
            locked |= {
                "connector_id",
                "direction",
                "purpose",
                "reference",
                "file",
                "declared_records",
                "declared_total",
                "company_id",
            }
        return locked

    @api.constrains("connector_id", "declared_records")
    def _check_run(self):
        for rec in self:
            if rec.connector_id.pattern != "batch_file":
                raise ValidationError(
                    "%s does not declare the Batch File pattern (BRU-IPF-13): declare it on "
                    "the connector first." % rec.connector_id.name
                )
            if rec.declared_records < 0:
                raise ValidationError("Declared records cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        _require_integration_admin(self.env, "record a batch file exchange")
        Seq = self.env["ir.sequence"].sudo()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = Seq.next_by_code("fix.integration.batch.run") or "New"
        recs = super().create(vals_list)
        for rec in recs:
            raw = rec.with_context(bin_size=False).sudo().file or b""
            digest = hashlib.sha256(base64.b64decode(raw)).hexdigest()
            rec._guarded().write({"file_sha256": digest})
            _integration_audit(
                self.env,
                "integration.batch_recorded",
                "fix.integration.batch.run,%d" % rec.id,
                "integration.batch_recorded: %s %s %s by %s"
                % (rec.name, rec.direction, rec.reference, self.env.user.name),
            )
        return recs

    def write(self, vals):
        if not self.env.su and not self._fix_guard_open():
            fixed = {
                "connector_id",
                "direction",
                "purpose",
                "reference",
                "file",
                "declared_records",
                "declared_total",
                "company_id",
            }
            for rec in self:
                for name in fixed & set(vals):
                    if name == "file":
                        current = rec.with_context(bin_size=False).sudo().file or b""
                        new = vals["file"] or b""
                        differs = (new.encode() if isinstance(new, str) else new) != current
                    else:
                        differs = rec._fix_guard_differs(name, vals[name], rec[name])
                    if differs:
                        raise UserError("%s is recorded: a corrected file is a new run." % rec.name)
        return super().write(vals)

    def action_verify(self, counted_records=None, counted_total=None):
        """AUT-IPF-20: a second person counts the file. Matching totals verify it;
        a mismatch is refused, and the run is then rejected with its reason."""
        _require_integration_admin(self.env, "verify a batch file")
        try:
            records = int(counted_records)
            total = float(counted_total)
        except (TypeError, ValueError) as exc:
            raise UserError("State the records and the control total you counted.") from exc
        for rec in self:
            if rec.state != "recorded":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            if rec.create_uid == self.env.user:
                raise UserError(
                    "You recorded %s: a second Integration Admin counts and verifies it." % rec.name
                )
            if records != rec.declared_records or abs(total - rec.declared_total) > 0.005:
                raise UserError(
                    "%s does not reconcile: declared %d records / %.2f, counted %d / %.2f. "
                    "Reject it with the reason instead."
                    % (rec.name, rec.declared_records, rec.declared_total, records, total)
                )
            rec._guarded().write(
                {
                    "state": "verified",
                    "counted_records": records,
                    "counted_total": total,
                    "verified_by_id": self.env.uid,
                    "verified_at": _now(),
                }
            )
            _integration_audit(
                self.env,
                "integration.batch_verified",
                "fix.integration.batch.run,%d" % rec.id,
                "integration.batch_verified: %s by %s" % (rec.name, self.env.user.name),
            )
        return True

    def action_reject(self, reason=None):
        _require_integration_admin(self.env, "reject a batch file")
        text = _required_text(reason, "why this batch file is rejected")
        for rec in self:
            if rec.state != "recorded":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "rejected", "rejection_reason": text[:250]})
            _integration_audit(
                self.env,
                "integration.batch_rejected",
                "fix.integration.batch.run,%d" % rec.id,
                "integration.batch_rejected: %s by %s; why: %s"
                % (rec.name, self.env.user.name, text),
            )
        return True


# --------------------------------------------------------------------------
# Versioning & Portals: credentials per consumer per environment (FR-IPF-016).
# --------------------------------------------------------------------------
class FixApiCredential(models.Model):
    _name = "fix.api.credential"
    _inherit = ["fix.guarded.mixin"]
    _description = "API Consumer Credential"
    _order = "consumer_id, environment, id desc"
    _rec_name = "client_id"

    consumer_id = fields.Many2one("fix.api.consumer", required=True, index=True, ondelete="cascade")
    company_id = fields.Many2one(
        "res.company", related="consumer_id.company_id", store=True, index=True
    )
    environment = fields.Selection(API_ENVIRONMENTS, required=True)
    client_id = fields.Char(string="Client ID", readonly=True, copy=False, index=True)
    secret_ref = fields.Char(
        string="Secret Reference (vault://)",
        required=True,
        help="The secret value lives in the vault and never in this model (SEC-101).",
    )
    issued_at = fields.Datetime(readonly=True, copy=False)
    issued_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    expires_on = fields.Date()
    revoked_at = fields.Datetime(readonly=True, copy=False)
    revoked_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    revoked_reason = fields.Char(readonly=True, copy=False)
    replaced_by_id = fields.Many2one("fix.api.credential", readonly=True, copy=False)
    state = fields.Selection(
        [("active", "Active"), ("expired", "Expired"), ("revoked", "Revoked")],
        compute="_compute_state",
    )

    _client_id_unique = models.UniqueIndex(
        "(client_id) WHERE client_id IS NOT NULL", "A client id is issued once."
    )

    @api.depends("revoked_at", "expires_on")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.revoked_at:
                rec.state = "revoked"
            elif rec.expires_on and rec.expires_on < today:
                rec.state = "expired"
            else:
                rec.state = "active"

    def _fix_guarded_fields(self):
        return super()._fix_guarded_fields() | {
            "client_id",
            "issued_at",
            "issued_by_id",
            "revoked_at",
            "revoked_by_id",
            "revoked_reason",
            "replaced_by_id",
        }

    def _fix_form_locked_fields(self):
        locked = set(super()._fix_form_locked_fields())
        if self.ids:
            locked |= {"consumer_id", "environment", "secret_ref"}
        return locked

    @api.constrains("secret_ref", "expires_on")
    def _check_credential(self):
        for rec in self:
            problem = _vault_ref_problem(self.env, rec.secret_ref)
            if problem:
                raise ValidationError(problem)

    def _fix_assert_issuable(self):
        for rec in self:
            consumer = rec.consumer_id.sudo()
            if rec.environment == "production" and consumer.registration_state != "registered":
                raise UserError(
                    "%s is not registered: a production credential is issued only to a "
                    "registered consumer (Request Registration). Sandbox and staging "
                    "credentials may come first." % consumer.name
                )
            if rec.expires_on and rec.expires_on < fields.Date.context_today(rec):
                raise UserError("A credential cannot be issued already expired.")
            others = self.sudo().search(
                [
                    ("consumer_id", "=", rec.consumer_id.id),
                    ("environment", "=", rec.environment),
                    ("revoked_at", "=", False),
                    ("id", "!=", rec.id),
                ]
            )
            if others:
                raise UserError(
                    "%s already holds a live %s credential (%s): rotate or revoke it."
                    % (consumer.name, rec.environment, others[0].client_id)
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require_integration_admin(self.env, "issue an API credential")
        recs = super().create(vals_list)
        for rec in recs:
            rec._fix_assert_issuable()
            rec._guarded().write(
                {
                    "client_id": "cid-%s-%s" % (rec.environment[:4], secrets.token_hex(8)),
                    "issued_at": _now(),
                    "issued_by_id": self.env.uid,
                }
            )
            _integration_audit(
                self.env,
                "integration.api_credential_issued",
                "fix.api.credential,%d" % rec.id,
                "integration.api_credential_issued: %s %s for %s by %s"
                % (rec.client_id, rec.environment, rec.consumer_id.name, self.env.user.name),
            )
        return recs

    def write(self, vals):
        if not self.env.su and not self._fix_guard_open():
            for rec in self:
                for name in {"consumer_id", "environment", "secret_ref"} & set(vals):
                    if rec._fix_guard_differs(name, vals[name], rec[name]):
                        raise UserError(
                            "An issued credential keeps its consumer, environment and secret "
                            "reference: rotate it to change the secret."
                        )
        return super().write(vals)

    def _fix_revoke(self, reason):
        self._guarded().write(
            {"revoked_at": _now(), "revoked_by_id": self.env.uid, "revoked_reason": reason[:250]}
        )

    def action_revoke(self, reason=None):
        _require_integration_admin(self.env, "revoke an API credential")
        text = _required_text(reason, "why this credential is revoked")
        for rec in self:
            if rec.revoked_at:
                raise UserError("%s is already revoked." % rec.client_id)
            rec._fix_revoke(text)
            _integration_audit(
                self.env,
                "integration.api_credential_revoked",
                "fix.api.credential,%d" % rec.id,
                "integration.api_credential_revoked: %s by %s; why: %s"
                % (rec.client_id, self.env.user.name, text),
            )
        return True

    def action_rotate(self):
        """Self-service rotation: a new credential on the next vault version, the
        old one revoked in the same transaction. No secrets manager exists (B-8),
        so the operator loads the new value at the new path."""
        _require_integration_admin(self.env, "rotate an API credential")
        for rec in self:
            if rec.revoked_at:
                raise UserError("%s is revoked: issue a new credential." % rec.client_id)
            new_ref = _bump_vault_ref(rec.secret_ref)
            rec._fix_revoke("rotated")
            new = self.create(
                {
                    "consumer_id": rec.consumer_id.id,
                    "environment": rec.environment,
                    "secret_ref": new_ref,
                    "expires_on": rec.expires_on,
                }
            )
            rec._guarded().write({"replaced_by_id": new.id})
        return True


# --------------------------------------------------------------------------
# Subscriptions & DLQ: replay one consumer from a point in time (FR-IPF-031).
# --------------------------------------------------------------------------
class FixEventConsumerReplay(models.Model):
    _name = "fix.event.consumer.replay"
    _inherit = ["fix.approvable.mixin"]
    _description = "Event Consumer Replay"
    _order = "id desc"

    _approval_domain = "other"
    _approval_group = INTEGRATION_ADMIN
    _approval_apply_method = "_fix_apply_replay"
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    consumer_id = fields.Many2one(
        "fix.event.consumer", required=True, index=True, ondelete="restrict", string="Subscription"
    )
    event_type = fields.Char(related="consumer_id.event_type", string="Event Type")
    replay_from = fields.Datetime(required=True)
    replay_to = fields.Datetime(help="Empty: up to the moment the replay runs.")
    reason = fields.Text(required=True)
    event_count = fields.Integer(compute="_compute_event_count", string="Events in Window")
    replayed_at = fields.Datetime(readonly=True, copy=False)
    replayed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    delivered_count = fields.Integer(readonly=True, copy=False)
    failed_count = fields.Integer(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Not Approved"), ("replayed", "Replayed")], compute="_compute_state"
    )

    @api.depends("replayed_at")
    def _compute_state(self):
        for rec in self:
            rec.state = "replayed" if rec.replayed_at else "draft"

    @api.depends("consumer_id", "replay_from")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s since %s" % (
                rec.consumer_id.name or "?",
                str(rec.replay_from or "")[:16],
            )

    def _fix_window_events(self):
        self.ensure_one()
        sub = self.consumer_id.sudo()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("create_date", ">=", self.replay_from),
        ]
        if self.replay_to:
            domain.append(("create_date", "<=", self.replay_to))
        if sub.event_type.endswith(".*"):
            domain.append(("event_type", "=like", sub.event_type[:-1] + "%"))
        else:
            domain.append(("event_type", "=", sub.event_type))
        events = self.env["fix.event.outbox"].sudo().search(domain, order="create_date asc, id asc")
        return events.filtered(lambda e: sub._matches(e.event_type))

    @api.depends("consumer_id", "replay_from", "replay_to", "company_id")
    def _compute_event_count(self):
        for rec in self:
            rec.event_count = (
                len(rec._fix_window_events()) if rec.consumer_id and rec.replay_from else 0
            )

    @api.constrains("replay_from", "replay_to")
    def _check_window(self):
        for rec in self:
            if rec.replay_from > _now():
                raise ValidationError("A replay starts in the past.")
            if rec.replay_to and rec.replay_to <= rec.replay_from:
                raise ValidationError("The window must end after it starts.")

    def _fix_guarded_fields(self):
        return super()._fix_guarded_fields() | {
            "replayed_at",
            "replayed_by_id",
            "delivered_count",
            "failed_count",
        }

    def _fix_form_locked_fields(self):
        locked = set(super()._fix_form_locked_fields())
        if any(rec.replayed_at for rec in self):
            locked |= {"consumer_id", "replay_from", "replay_to", "reason", "company_id"}
        return locked

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return not self.replayed_at

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"consumer_id", "replay_from", "replay_to"}

    @api.model_create_multi
    def create(self, vals_list):
        _require_integration_admin(self.env, "request a consumer replay")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su and not self._fix_guard_open():
            fixed = {"consumer_id", "replay_from", "replay_to", "reason"} & set(vals)
            if fixed and any(rec.replayed_at for rec in self):
                raise UserError("This replay has run: request a new one.")
        return super().write(vals)

    def _fix_assert_bounded(self):
        cap = _param_int(self.env, REPLAY_MAX_EVENTS_KEY, REPLAY_MAX_EVENTS_DEFAULT)
        for rec in self:
            count = len(rec._fix_window_events())
            if not count:
                raise UserError("No %s event falls in this window." % rec.consumer_id.event_type)
            if count > cap:
                raise UserError(
                    "%d events fall in this window, over the limit of %d (%s): narrow it."
                    % (count, cap, REPLAY_MAX_EVENTS_KEY)
                )

    def action_request_replay(self, justification=None):
        _require_integration_admin(self.env, "request a consumer replay")
        for rec in self:
            if rec.replayed_at:
                raise UserError("This replay has already run.")
        self._fix_assert_bounded()
        return _route_to_second_admin(self, justification, "why this consumer must be replayed")

    def _fix_apply_replay(self):
        """Re-deliver the window to THIS consumer only (FR-IPF-031: no side effect
        on any other consumer). Consumers are idempotent (BRU-IPF-07), so an
        event it already processed is processed again harmlessly."""
        self._approval_assert_routed()
        self._fix_assert_bounded()
        Outbox = self.env["fix.event.outbox"].sudo()
        Delivery = self.env["fix.event.consumer.delivery"].sudo()
        for rec in self:
            sub = rec.consumer_id.sudo()
            delivered = failed = 0
            for event in rec._fix_window_events():
                error = Outbox._relay_deliver(sub, event)
                state = "done" if not error else "failed"
                row = Delivery.search(
                    [("subscription_id", "=", sub.id), ("event_id", "=", event.id)], limit=1
                )
                vals = {"state": state, "last_error": error or False, "delivered_at": _now()}
                if row:
                    vals["attempts"] = row.attempts + 1
                    row.write(vals)
                else:
                    Delivery.create(dict(vals, subscription_id=sub.id, event_id=event.id))
                if error:
                    failed += 1
                else:
                    delivered += 1
            rec._guarded().write(
                {
                    "replayed_at": _now(),
                    "replayed_by_id": self.env.uid,
                    "delivered_count": delivered,
                    "failed_count": failed,
                }
            )
            _integration_audit(
                self.env,
                "integration.consumer_replayed",
                "fix.event.consumer.replay,%d" % rec.id,
                "integration.consumer_replayed: %s since %s approved by %s: %d delivered, "
                "%d failed; why: %s"
                % (sub.name, rec.replay_from, self.env.user.name, delivered, failed, rec.reason),
            )
        return True


# --------------------------------------------------------------------------
# Webhooks: inbound (FR-IPF-037/038).
# --------------------------------------------------------------------------
class FixWebhookInboundSource(models.Model):
    """A third party allowed to post to /hooks/v1/inbound/<code>. Data entering
    the Company, so going live is a second Integration Admin's decision."""

    _name = "fix.webhook.inbound.source"
    _inherit = ["fix.approvable.mixin"]
    _description = "Inbound Webhook Source"
    _order = "code"

    _approval_domain = "other"
    _approval_group = INTEGRATION_ADMIN
    _approval_apply_method = "_fix_apply_go_live"
    _approval_routed = True

    name = fields.Char(required=True, help="Who posts here, e.g. bKash payment notifications.")
    code = fields.Char(
        required=True,
        help="The last segment of the receiving URL /hooks/v1/inbound/<code>: "
        "lower-case letters, digits and hyphens.",
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    connector_id = fields.Many2one("fix.connector", string="Integration")
    owning_module = fields.Char(
        required=True, help="The module a verified webhook is routed to (FR-IPF-038), e.g. M20."
    )
    route_key = fields.Char(
        required=True,
        help="What the owning module listens for, e.g. bkash.payment_notified. Carried in "
        "the integration.webhook_received event; the content is not interpreted here.",
    )
    secret_ref = fields.Char(
        string="Signing Secret Reference (vault://)",
        required=True,
        help="The HMAC secret the sender signs with. Its value reaches the receiver as "
        "FIX_VAULT_<PATH>; with no value, every post is refused.",
    )
    replay_window_seconds = fields.Integer(
        default=300,
        required=True,
        help="A post signed longer ago than this is refused as a possible replay.",
    )
    state = fields.Selection(
        [("draft", "Awaiting Go-Live"), ("active", "Receiving"), ("paused", "Paused")],
        required=True,
        default="draft",
    )
    pause_reason = fields.Char(readonly=True, copy=False)
    receipt_ids = fields.One2many("fix.webhook.inbound.event", "source_id")
    receipt_count = fields.Integer(compute="_compute_receipts", string="Received")
    last_received_at = fields.Datetime(compute="_compute_receipts")

    _code_unique = models.Constraint(
        "UNIQUE (code)", "This inbound webhook code is already in use."
    )

    @api.depends("receipt_ids.outcome", "receipt_ids.received_at")
    def _compute_receipts(self):
        for rec in self:
            accepted = rec.sudo().receipt_ids.filtered(lambda r: r.outcome == "accepted")
            rec.receipt_count = len(accepted)
            rec.last_received_at = max(accepted.mapped("received_at")) if accepted else False

    @api.constrains("code", "route_key", "secret_ref", "replay_window_seconds")
    def _check_source(self):
        for rec in self:
            if not INBOUND_CODE.match(rec.code or ""):
                raise ValidationError(
                    "The code becomes the URL: 3-40 lower-case letters, digits and hyphens."
                )
            if not ROUTE_KEY.match(rec.route_key or ""):
                raise ValidationError(
                    "The route key is dotted lower-case, e.g. bkash.payment_notified."
                )
            problem = _vault_ref_problem(self.env, rec.secret_ref)
            if problem:
                raise ValidationError(problem)
            if not 30 <= rec.replay_window_seconds <= 3600:
                raise ValidationError("The replay window is between 30 and 3600 seconds.")

    def _fix_guarded_fields(self):
        return super()._fix_guarded_fields() | {"state", "pause_reason"}

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.state != "active"

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {
            "code",
            "secret_ref",
            "route_key",
            "owning_module",
            "company_id",
        }

    def _approval_clear_stamp(self, reason):
        self.sudo()._guarded().write({"state": "draft"})

    @api.model_create_multi
    def create(self, vals_list):
        _require_integration_admin(self.env, "register an inbound webhook")
        for vals in vals_list:
            # A person's new source receives nothing until a second admin decides.
            if not self.env.su:
                vals.pop("state", None)
        return super().create(vals_list)

    def action_request_go_live(self, justification=None):
        _require_integration_admin(self.env, "request an inbound webhook go-live")
        for rec in self:
            if rec.state == "active":
                raise UserError("%s is already receiving." % rec.code)
            rec._check_source()
        return _route_to_second_admin(self, justification, "why this source may post to us")

    def _fix_apply_go_live(self):
        self._approval_assert_routed()
        self._check_source()
        self._guarded().write({"state": "active", "pause_reason": False})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.inbound_webhook_live",
                "fix.webhook.inbound.source,%d" % rec.id,
                "integration.inbound_webhook_live: %s approved by %s"
                % (rec.code, self.env.user.name),
            )
        return True

    def action_pause(self, reason=None):
        _require_integration_admin(self.env, "pause an inbound webhook")
        text = _required_text(reason, "why this inbound webhook is paused")
        for rec in self:
            rec._guarded().write({"state": "paused", "pause_reason": text[:250]})
            _integration_audit(
                self.env,
                "integration.inbound_webhook_paused",
                "fix.webhook.inbound.source,%d" % rec.id,
                "integration.inbound_webhook_paused: %s by %s; why: %s"
                % (rec.code, self.env.user.name, text),
            )
        return True


class FixWebhookInboundEvent(models.Model):
    """One post the receiver handled: accepted, a duplicate answered from the
    first, or refused with the reason. Written only by the receiver."""

    _name = "fix.webhook.inbound.event"
    _description = "Inbound Webhook Receipt"
    _order = "received_at desc, id desc"
    _rec_name = "message_id"

    source_id = fields.Many2one(
        "fix.webhook.inbound.source", required=True, index=True, ondelete="restrict"
    )
    company_id = fields.Many2one(
        "res.company", related="source_id.company_id", store=True, index=True
    )
    message_id = fields.Char(required=True, index=True, string="Message ID")
    received_at = fields.Datetime(required=True, default=lambda self: fields.Datetime.now())
    signed_at = fields.Datetime()
    outcome = fields.Selection(
        [("accepted", "Accepted"), ("duplicate", "Duplicate"), ("rejected", "Refused")],
        required=True,
    )
    reason = fields.Char()
    body_bytes = fields.Integer()
    payload_sha256 = fields.Char(string="Payload SHA-256")
    outbox_event_id = fields.Many2one("fix.event.outbox", string="Routed Event", readonly=True)

    _accepted_once = models.UniqueIndex(
        "(source_id, message_id) WHERE outcome = 'accepted'",
        "This message was already accepted from this source.",
    )

    def write(self, vals):
        if not self.env.su:
            raise UserError("An inbound webhook receipt is written by the receiver only.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("An inbound webhook receipt is evidence and is never deleted.")
        return super().unlink()
