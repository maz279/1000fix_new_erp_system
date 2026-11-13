# fix_integration — M28: API gateway catalogue, consumers/quotas, event bus
# (topics, schemas, subscriptions, DLQ, replay), the 47-connector framework,
# connector credentials and offline-sync conflict resolution. The
# transactional outbox lives in cd_event_outbox (fix.event.outbox).
#
# A12 remediation (2026-11-04, report X4 / P1-6 / R4, findings M28-1..M28-13):
# this module was a register anyone could rewrite. Now:
#   - every model inherits fix.guarded.mixin, so state / resolution /
#     replayed_at / health fields change only through a transition action;
#   - every mutating action re-checks cd_itsm.group_integration_admin in
#     code (X4: the ACL alone is not enough);
#   - webhook subscriptions take an https URL on an allow-listed host with a
#     mandatory vault:// signing secret (M28-1; allow-list default EMPTY —
#     refuse everything until the operator lists a host);
#   - fix.event.dlq mirrors the REAL dead letters of the relay
#     (fix.event.consumer.delivery, state='dead') via cron_sync_dead_letters,
#     and replay re-enqueues that delivery (privileged, audited, idempotent);
#   - a published schema is frozen: corrections ship as a new version
#     (BRU-IPF-06 / M28-8);
#   - fix.integration.log is system-written only (M28-5): no user create or
#     write; server code logs through _log_request;
#   - key rotation bumps the version inside the vault reference instead of
#     appending a "#rotated" suffix (M28-2 / E A05), and is audited.
#
# A12 finish build (2026-11-07, working/A12_evidence/finish/m28_m66/FINDINGS.md):
#   - N-M28-1: a sync resolution was an arbitrary sudo write that reached
#     ir.config_parameter. Targets now pass a field-class policy (BRU-IPF-17)
#     and an allow-list; conflicts come from the sync engine, never a form;
#   - M28-1: a connector endpoint obeys the webhook host rule, and a repoint is
#     audited; subscriptions off the list are paused by a cron;
#   - M28-2: raising a quota or making an endpoint public needs a second
#     Integration Admin (M63); key references change only through an action;
#   - M28-3 / M28-5: the webhook dispatcher and API edge write the log (see
#     fix_integration_dispatch.py and libs/py/fix_api_edge); only rows they
#     write count as measured, so a seeded row never reads as traffic;
#   - B-8: no secrets manager exists. References stay vault://; "rotate" versions
#     the reference and records an audit row. It does not touch any secret.
#
# M28 second pass (Y01, Y02, Y05, Y06): an endpoint has a lifecycle and cannot be
# removed while in use or inside its notice (BRU-IPF-05). Registering a consumer,
# taking a webhook or a connector live, discarding a dead letter and publishing a
# breaking schema each go through M63 to a second Integration Admin. A row a person
# creates starts out of service. Rows from before this (default values) stay as they
# are until someone changes what the approval would have covered.
import json
import os
import re
import time
from datetime import timedelta
from urllib.parse import urlsplit

import requests
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request

from libs.py.fix_env_guard import ALLOWED_HOSTS

INTEGRATION_ADMIN = "cd_itsm.group_integration_admin"
# Hosts a webhook endpoint_url may point at (comma or whitespace separated;
# an entry "*.corp.local" allows subdomains). Conservative default: EMPTY —
# every external AND localhost URL is refused until the operator lists it.
WEBHOOK_ALLOWLIST_KEY = "fix.integration.webhook_allowlist"
# Real outbound HTTP is off until a system administrator turns this on (DE-11):
# while off, the dispatcher and the connector probe record a truthful "not sent".
DISPATCH_ENABLED_KEY = "fix.integration.dispatch_enabled"
# Comma-separated first path segments a vault:// reference may use. Unset = any
# (no secrets manager exists to own a namespace yet: decision B-8).
VAULT_NAMESPACES_KEY = "fix.integration.vault_namespaces"
# "enrolled" (default): a user with an authenticator must give a valid code to
# replay a dead letter. "required": a user with none is refused as well.
REPLAY_STEP_UP_KEY = "fix.integration.replay_step_up"
# New quotas above these need the increase route, like any later raise.
QUOTA_CEILING_RPM_KEY = "fix.integration.quota_ceiling_rpm"
QUOTA_CEILING_DAILY_KEY = "fix.integration.quota_ceiling_daily"
QUOTA_CEILING_RPM_DEFAULT = 600
QUOTA_CEILING_DAILY_DEFAULT = 100000
# FR-IPF-041: how long before expiry a credential is flagged.
CREDENTIAL_ALERT_DAYS_KEY = "fix.integration.credential_alert_days"
CREDENTIAL_ALERT_DAYS_DEFAULT = 30
PROBE_TIMEOUT_SECONDS = 5
USAGE_WINDOW_DAYS = 30
# BRU-IPF-05: the notice before a version may go, and how recent a call must be to
# count as "still calling it".
API_NOTICE_MONTHS = 6
API_STILL_CALLING_DAYS = 30

_VAULT_REF = re.compile(r"^vault://[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*/?$")
_VAULT_VERSION = re.compile(r"^(vault://.+/v)(\d+)$")

# BRU-IPF-17: the server is authoritative for assignment, pricing, stock and
# state; the client for field-captured evidence, notes and timestamps. A sync
# resolution reaches ONLY these models: each lists the fields a device may win.
# Every other field on a listed model is server-authoritative, and a model not
# listed here is out of reach. Code, not a parameter: this table decides what a
# resolution may overwrite, so changing it goes through review.
SYNC_TARGET_POLICY = {
    "fix.field.order": {"notes", "work_summary", "decline_notes"},
    "fix.work.order": {"notes"},
    "res.partner": {"phone", "street"},
}
SYNC_NEVER_TARGETS = ("ir.", "res.users", "res.groups", "base.")
SYNC_CLASSES = [
    ("client", "Client authoritative (notes, evidence)"),
    ("server", "Server authoritative (state, price, stock, assignment)"),
    ("denied", "Not on the sync allow-list"),
]
# What a person may decide on a pending conflict ("pending" is not a decision).
SYNC_DECISIONS = ("local_wins", "remote_wins", "merged", "dismissed")


def _require_integration_admin(env, what):
    """X4 code check: the caller must hold the Integration Admin group.

    The ACL already denies plain users; this re-check closes the gap for
    anyone who gains the model ACLs without the role, and states the rule in
    the action itself. Superuser service code (crons, seeds) is trusted.
    """
    if env.su:
        return
    if not env.user.has_group(INTEGRATION_ADMIN):
        raise AccessError(
            "Only an Integration Admin may %s. Ask the platform owner to "
            "appoint one (cd_itsm.group_integration_admin)." % what
        )


def _require_service(env, what):
    """Cron and service bodies are public methods, so JSON-RPC can name them:
    only the superuser's environment may run them."""
    if not env.su:
        raise AccessError("%s is run by the platform's scheduler, not by a user." % what)


def _required_text(value, what):
    text = value.strip() if isinstance(value, str) else ""
    if not text:
        raise UserError("State %s: it goes on the audit record." % what)
    return text


def _integration_audit(env, event, object_ref, detail):
    """P1-6: privileged integration actions land in the append-only security
    audit trail. B1 ships fix.security.audit.log_event(event, object_ref,
    detail); until it lands, write the row directly under the generic
    'privileged' event so the action is still on the record."""
    audit = env["fix.security.audit"].sudo()
    log_event = getattr(audit, "log_event", None)
    if callable(log_event):
        log_event(event=event, object_ref=object_ref, detail=detail)
    else:
        audit.create(
            {
                "event": "privileged",
                "object_ref": object_ref,
                "detail": "[%s] %s" % (event, detail),
            }
        )


def _webhook_host(url):
    try:
        return (urlsplit(url or "").hostname or "").lower()
    except ValueError:
        return ""


def _param_on(env, key):
    value = env["ir.config_parameter"].sudo().get_param(key, "") or ""
    return value.strip().lower() in ("1", "true", "yes", "on")


def _param_int(env, key, default):
    value = env["ir.config_parameter"].sudo().get_param(key, "") or ""
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _allowlist(env):
    raw = env["ir.config_parameter"].sudo().get_param(WEBHOOK_ALLOWLIST_KEY, "") or ""
    return {h.strip().lower() for h in re.split(r"[,\s]+", raw) if h.strip()}


def _host_on_list(host, allowlist):
    if not host:
        return False
    if host in allowlist:
        return True
    return any(entry.startswith("*.") and host.endswith(entry[1:]) for entry in allowlist)


def _outbound_url_problem(env, url):
    """Why `url` may not receive Company data, or '' when it may (M28-1): https,
    no credentials in the URL, host on the operator's allow-list."""
    try:
        parts = urlsplit(url or "")
        host = (parts.hostname or "").lower()
    except ValueError:
        return "%r is not a valid URL." % url
    if parts.scheme.lower() != "https":
        return (
            "Endpoint must be https:// - %r is not accepted (M28-1: payloads must not "
            "leave the Company in clear)." % url
        )
    if parts.username or parts.password:
        return "An endpoint URL may not carry credentials (%s)." % (host or "?")
    if not _host_on_list(host, _allowlist(env)):
        return (
            "Host %r is not on the integration allow-list (M28 > Allowed Hosts, parameter "
            "%s). The list ships EMPTY on purpose: no external or localhost host receives "
            "Company payloads until an Integration Admin lists it."
            % (host or "?", WEBHOOK_ALLOWLIST_KEY)
        )
    return ""


def _de11_refusal(url):
    """DE-11: a local environment never reaches a non-local endpoint. An unset
    FIX_ENV counts as local: every environment in this repository is."""
    if os.environ.get("FIX_ENV", "local") != "local":
        return ""
    host = _webhook_host(url)
    if host in ALLOWED_HOSTS:
        return ""
    return "DE-11: a local environment may not reach %s" % host


def _dispatch_refusal(env, url):
    """Why real HTTP to `url` may not happen now, or ''. The one gate every
    outbound call passes, at send time."""
    if _outbound_url_problem(env, url):
        return "host not on the allow-list"
    if not _param_on(env, DISPATCH_ENABLED_KEY):
        return "dispatch disabled"
    return _de11_refusal(url)


def _http_head(url, timeout):
    """The connector probe's request. Tests replace this: no real network."""
    return requests.head(url, timeout=timeout, allow_redirects=False).status_code


def _vault_ref_problem(env, ref):
    """Why `ref` is not an acceptable vault reference, or '' (SEC-101, B-8)."""
    if not _VAULT_REF.match(ref or "") or ".." in (ref or ""):
        return (
            "A secret is held by reference only: vault://<namespace>/<path>. The value "
            "itself never lands in this model (SEC-101)."
        )
    raw = env["ir.config_parameter"].sudo().get_param(VAULT_NAMESPACES_KEY, "") or ""
    allowed = {n.strip() for n in re.split(r"[,\s]+", raw) if n.strip()}
    namespace = ref[len("vault://") :].split("/", 1)[0]
    if allowed and namespace not in allowed:
        return "Vault namespace %r is not on the list (%s)." % (namespace, VAULT_NAMESPACES_KEY)
    return ""


def _bump_vault_ref(current):
    """vault://keys/x/v2 -> /v3; a reference with no version gains /v2."""
    match = _VAULT_VERSION.match(current or "")
    if match:
        return "%s%d" % (match.group(1), int(match.group(2)) + 1)
    if (current or "").startswith("vault://"):
        return current.rstrip("/") + "/v2"
    return None


def _route_to_second_admin(records, justification, what):
    """The M63 request for a decision a second Integration Admin takes. The engine
    excludes the requester and the record's creator from deciding."""
    text = _required_text(justification, what)
    for rec in records:
        rec.action_request_approval(justification=text)
    return True


def _contract_narrowed(old, new, path="$"):
    """What a consumer built on JSON Schema `old` would break on under `new`.
    Adding an optional property is additive (BRU-IPF-06); the rest is breaking."""
    problems = []
    if old.get("type") != new.get("type"):
        problems.append("%s type %s -> %s" % (path, old.get("type"), new.get("type")))
    for name in sorted(set(new.get("required") or []) - set(old.get("required") or [])):
        problems.append("%s.%s is now required" % (path, name))
    old_props = old.get("properties") or {}
    new_props = new.get("properties") or {}
    for name, sub in old_props.items():
        if name not in new_props:
            problems.append("%s.%s was removed" % (path, name))
        elif isinstance(sub, dict) and isinstance(new_props[name], dict):
            problems += _contract_narrowed(sub, new_props[name], "%s.%s" % (path, name))
    if "enum" in new:
        lost = [v for v in old.get("enum", []) if v not in new["enum"]]
        if "enum" not in old or lost:
            problems.append("%s enum narrowed" % path)
    if new.get("additionalProperties") is False and old.get("additionalProperties") is not False:
        problems.append("%s no longer accepts extra properties" % path)
    if isinstance(old.get("items"), dict) and isinstance(new.get("items"), dict):
        problems += _contract_narrowed(old["items"], new["items"], "%s[]" % path)
    return problems


def _notify_integration_admins(record, summary, note):
    """A to-do for each Integration Admin. Who holds the role is decision B-3;
    an empty role leaves the audit row as the only trace."""
    group = record.env.ref(INTEGRATION_ADMIN).sudo()
    holders = group.all_user_ids.filtered(lambda u: u.active and not u.share)
    for user in holders:
        record.sudo().activity_schedule(
            "mail.mail_activity_data_todo", user_id=user.id, summary=summary, note=note
        )
    return len(holders)


class FixApiEndpoint(models.Model):
    _name = "fix.api.endpoint"
    _inherit = ["fix.approvable.mixin"]
    _description = "API Catalogue Entry"
    _order = "version desc, code"

    # M28-2: a catalogue entry goes public only through a second Integration
    # Admin. Everything else about an entry is configuration.
    _approval_domain = "other"
    _approval_group = INTEGRATION_ADMIN
    _approval_apply_method = "_fix_apply_public"
    _approval_routed = True

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    version = fields.Char(required=True, default="v1")
    path = fields.Char(required=True)
    method = fields.Selection(
        [
            ("GET", "GET"),
            ("POST", "POST"),
            ("PUT", "PUT"),
            ("PATCH", "PATCH"),
            ("DELETE", "DELETE"),
        ],
        required=True,
        default="GET",
    )
    auth_type = fields.Selection(
        [
            ("none", "Public"),
            ("api_key", "API Key"),
            ("oauth2", "OAuth 2.0"),
            ("mtls", "Mutual TLS"),
        ],
        required=True,
        default="api_key",
    )
    description = fields.Char()
    active = fields.Boolean(default=True)
    # Y01. The default is 'published' because every row from before this is already
    # in the catalogue; a row a person registers starts as 'designed'.
    lifecycle = fields.Selection(
        [
            ("designed", "Designed"),
            ("published", "Published"),
            ("deprecated", "Deprecated"),
            ("sunset", "Sunset"),
        ],
        required=True,
        default="published",
        index=True,
    )
    deprecated_on = fields.Date(readonly=True, copy=False)
    sunset_on = fields.Date(
        readonly=True, copy=False, help="The earliest date this version may go (BRU-IPF-05)."
    )

    _code_version_unique = models.Constraint(
        "UNIQUE (code, version, company_id)", "An endpoint code+version is unique per company"
    )

    def _fix_guarded_fields(self):
        return super()._fix_guarded_fields() | {"lifecycle", "deprecated_on", "sunset_on"}

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.auth_type != "none"

    def _approval_pinned_fields(self) -> set:
        # The approval covers this route: moving it voids the approval.
        return super()._approval_pinned_fields() | {"code", "version", "path", "method"}

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            self.check_access("create")
            for vals in vals_list:
                if vals.get("auth_type") == "none":
                    raise UserError(
                        "An endpoint is not registered as public. Register it with an "
                        "authentication type, then use Request Public Access: a second "
                        "Integration Admin decides."
                    )
        records = super().create(vals_list)
        if not self._fix_guard_open():
            records._guarded().write({"lifecycle": "designed"})
        return records

    def _fix_recent_calls(self):
        """Measured calls from a registered consumer inside the still-calling window."""
        self.ensure_one()
        since = fields.Datetime.now() - timedelta(days=API_STILL_CALLING_DAYS)
        return (
            self.env["fix.integration.log"]
            .sudo()
            .search_count(
                [
                    ("kind", "=", "api"),
                    ("endpoint_id", "=", self.id),
                    ("consumer_id", "!=", False),
                    ("measured", "=", True),
                    ("created_at", ">=", since),
                ]
            )
        )

    def _fix_check_removal(self):
        """BRU-IPF-05, for deactivating or deleting by hand."""
        for rec in self:
            if rec.lifecycle in ("published", "deprecated"):
                raise UserError(
                    "%s %s is %s. A version goes only through Deprecate and then Sunset, "
                    "with %d months' notice (BRU-IPF-05)."
                    % (rec.code, rec.version, rec.lifecycle, API_NOTICE_MONTHS)
                )
            quotas = self.env["fix.api.quota"].sudo().search_count([("endpoint_id", "=", rec.id)])
            if quotas or rec._fix_recent_calls():
                raise UserError(
                    "%s %s has a registered consumer: it cannot be removed while in use "
                    "(BRU-IPF-05)." % (rec.code, rec.version)
                )

    def unlink(self):
        if not self._fix_guard_open():
            self.check_access("unlink")
            self._fix_check_removal()
        return super().unlink()

    def action_publish_endpoint(self):
        _require_integration_admin(self.env, "publish an API version")
        for rec in self:
            if rec.lifecycle != "designed":
                raise UserError("Publish a designed version (this one is %s)." % rec.lifecycle)
        self._guarded().write({"lifecycle": "published"})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.endpoint_published",
                "fix.api.endpoint,%d" % rec.id,
                "integration.endpoint_published: %s %s by %s"
                % (rec.code, rec.version, self.env.user.name),
            )
        return True

    def action_deprecate(self, sunset_on=None):
        """FR-IPF-014: start the notice. The sunset date is at least six months away;
        empty takes exactly that. The API edge sends Deprecation and Sunset headers."""
        _require_integration_admin(self.env, "deprecate an API version")
        today = fields.Date.context_today(self)
        earliest = today + relativedelta(months=API_NOTICE_MONTHS)
        chosen = earliest
        if sunset_on:
            try:
                chosen = fields.Date.to_date(str(sunset_on).strip())
            except ValueError as exc:
                raise UserError("Give the sunset date as YYYY-MM-DD.") from exc
        if chosen < earliest:
            raise UserError(
                "A sunset gives %d months' notice: the earliest date is %s (BRU-IPF-05)."
                % (API_NOTICE_MONTHS, earliest)
            )
        for rec in self:
            if rec.lifecycle != "published":
                raise UserError("Deprecate a published version (this one is %s)." % rec.lifecycle)
        self._guarded().write(
            {"lifecycle": "deprecated", "deprecated_on": today, "sunset_on": chosen}
        )
        for rec in self:
            _integration_audit(
                self.env,
                "integration.endpoint_deprecated",
                "fix.api.endpoint,%d" % rec.id,
                "integration.endpoint_deprecated: %s %s sunset %s by %s"
                % (rec.code, rec.version, chosen, self.env.user.name),
            )
        return True

    def action_sunset(self, reason=None):
        """AUT-IPF-09: removal is blocked before the date and while a consumer still
        calls. A sunset version is out of the catalogue, and the API edge answers 410."""
        _require_integration_admin(self.env, "sunset an API version")
        why = _required_text(reason, "why this version can go")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.lifecycle != "deprecated":
                raise UserError("Sunset a deprecated version (this one is %s)." % rec.lifecycle)
            if rec.sunset_on and today < rec.sunset_on:
                raise UserError(
                    "%s %s is inside its notice until %s (BRU-IPF-05)."
                    % (rec.code, rec.version, rec.sunset_on)
                )
            calls = rec._fix_recent_calls()
            if calls:
                raise UserError(
                    "%s %s still has %d call(s) from registered consumers in the last %d "
                    "days: removal is blocked (BRU-IPF-05)."
                    % (rec.code, rec.version, calls, API_STILL_CALLING_DAYS)
                )
        self._guarded().write({"lifecycle": "sunset", "active": False})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.endpoint_sunset",
                "fix.api.endpoint,%d" % rec.id,
                "integration.endpoint_sunset: %s %s by %s; why: %s"
                % (rec.code, rec.version, self.env.user.name, why),
            )
        return True

    def write(self, vals):
        if "active" in vals and not self._fix_guard_open():
            self.check_access("write")
            if vals["active"] and any(rec.lifecycle == "sunset" for rec in self):
                raise UserError("A sunset version does not come back: register a new version.")
            if not vals["active"]:
                self.filtered("active")._fix_check_removal()
        if "auth_type" not in vals:
            return super().write(vals)
        if not self._fix_guard_open():
            self.check_access("write")
        if (
            not self._fix_guard_open()
            and vals["auth_type"] == "none"
            and any(rec.auth_type != "none" for rec in self)
        ):
            raise UserError(
                "An endpoint goes public only through Request Public Access: a second "
                "Integration Admin decides (M28-2)."
            )
        before = {rec.id: rec.auth_type for rec in self}
        result = super().write(vals)
        for rec in self:
            if before[rec.id] != rec.auth_type:
                _integration_audit(
                    self.env,
                    "integration.endpoint_auth_changed",
                    "fix.api.endpoint,%d" % rec.id,
                    "integration.endpoint_auth_changed: %s %s -> %s by %s"
                    % (rec.code, before[rec.id], rec.auth_type, self.env.user.name),
                )
        return result

    def action_request_public(self, justification=None):
        """M28-2: route 'make this endpoint public' to a second Integration Admin."""
        _require_integration_admin(self.env, "request public access to an endpoint")
        text = _required_text(justification, "why this endpoint should be public")
        for rec in self:
            if rec.auth_type == "none":
                raise UserError("%s is already public." % rec.code)
        return self.action_request_approval(justification=text)

    def _fix_apply_public(self):
        """The approved request's effect. Runs from the deciding task only."""
        self._approval_assert_routed()
        self._guarded().write({"auth_type": "none"})
        return True


class FixApiConsumer(models.Model):
    _name = "fix.api.consumer"
    _inherit = ["fix.approvable.mixin"]
    _description = "API Consumer"
    _order = "name"

    # Y05: registration is a second Integration Admin's decision. Until then the
    # consumer gets no issued key, no webhook, and the API edge does not recognise it.
    _approval_domain = "other"
    _approval_group = INTEGRATION_ADMIN
    _approval_apply_method = "_fix_apply_registration"
    _approval_routed = True

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Linked Partner",
        help="The API edge attributes a caller to this consumer through the "
        "authenticated user's partner.",
    )
    key_ref = fields.Char(
        string="Key Reference",
        help="Vault path or key alias - never the key itself (SEC-101). Set when the "
        "consumer is registered; after that it changes only through Rotate Key "
        "Reference, which bumps the version and records an audit row.",
    )
    quota_ids = fields.One2many("fix.api.quota", "consumer_id", string="Quotas")
    request_count = fields.Integer(compute="_compute_usage", string="Requests (30d)")
    active = fields.Boolean(default=True)
    registration_state = fields.Selection(
        [("draft", "Awaiting Approval"), ("registered", "Registered")],
        required=True,
        default="registered",
        index=True,
    )

    def _fix_guarded_fields(self):
        return super()._fix_guarded_fields() | {"registration_state"}

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.registration_state == "draft"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self._fix_guard_open():
            records._guarded().write({"registration_state": "draft"})
        return records

    def action_request_registration(self, justification=None):
        _require_integration_admin(self.env, "request a consumer registration")
        return _route_to_second_admin(self, justification, "why this consumer should be registered")

    def _fix_apply_registration(self):
        self._approval_assert_routed()
        self._guarded().write({"registration_state": "registered"})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.consumer_registered",
                "fix.api.consumer,%d" % rec.id,
                "integration.consumer_registered: %s approved by %s"
                % (rec.name, self.env.user.name),
            )
        return True

    def _approval_clear_stamp(self, reason):
        self.sudo()._guarded().write({"registration_state": "draft"})

    @api.constrains("key_ref")
    def _check_key_ref_vault(self):
        for rec in self:
            problem = rec.key_ref and _vault_ref_problem(self.env, rec.key_ref)
            if problem:
                raise ValidationError(problem)

    def _compute_usage(self):
        Log = self.env["fix.integration.log"].sudo()
        since = fields.Datetime.now() - timedelta(days=USAGE_WINDOW_DAYS)
        for rec in self:
            rec.request_count = Log.search_count(
                [
                    ("kind", "=", "api"),
                    ("consumer_id", "=", rec.id),
                    ("status", "=", "success"),
                    ("measured", "=", True),
                    ("created_at", ">=", since),
                ]
            )

    def _fix_form_locked_fields(self):
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked.add("key_ref")
        return locked

    def write(self, vals):
        if "key_ref" in vals and not self._fix_guard_open():
            for rec in self:
                if rec._fix_guard_differs("key_ref", vals["key_ref"], rec.key_ref):
                    raise UserError(
                        "The key reference changes only through Issue Key or Rotate Key "
                        "Reference, which version it and record an audit row (M28-2)."
                    )
        return super().write(vals)

    def action_issue_key(self):
        """N-M28-3: give a consumer with no key its first reference. Records the
        reference; the operator loads the key at that path in the vault."""
        _require_integration_admin(self.env, "issue an API consumer key")
        for rec in self:
            if rec.registration_state != "registered":
                raise UserError(
                    "%s is not registered yet: use Request Registration, and a second "
                    "Integration Admin decides." % rec.name
                )
            if rec.key_ref:
                raise UserError("%s already has a key reference: rotate it instead." % rec.name)
            new_ref = "vault://keys/consumer-%d/v1" % rec.id
            rec._guarded().write({"key_ref": new_ref})
            _integration_audit(
                self.env,
                "integration.key_issued",
                "fix.api.consumer,%d" % rec.id,
                "integration.key_issued: %s key reference %s by %s"
                % (rec.name, new_ref, self.env.user.name),
            )
        return True

    def action_rotate_key(self):
        """Bump the version inside the vault reference (vault://keys/x/v2 -> /v3)
        and record an audit row. No secrets manager exists (B-8), so this does not
        issue a key: the operator loads the new version in the vault, and the
        previous one stays valid there until it expires."""
        _require_integration_admin(self.env, "rotate an API consumer key")
        for rec in self:
            current = rec.key_ref or ""
            new_ref = _bump_vault_ref(current)
            if not new_ref:
                raise UserError(
                    "%s has no key reference to rotate: use Issue Key first." % rec.name
                )
            rec._guarded().write({"key_ref": new_ref})
            _integration_audit(
                self.env,
                "integration.key_rotated",
                "fix.api.consumer,%d" % rec.id,
                "integration.key_rotated: %s key reference %s -> %s by %s"
                % (rec.name, current, new_ref, self.env.user.name),
            )
        return True


class FixApiQuota(models.Model):
    _name = "fix.api.quota"
    _inherit = ["fix.approvable.mixin"]
    _description = "Rate Limit / Quota"
    _order = "consumer_id, endpoint_id"

    # M28-2: a limit goes down at once; it goes up only through a second
    # Integration Admin, because a raised limit is what an abuser needs.
    _approval_domain = "other"
    _approval_group = INTEGRATION_ADMIN
    _approval_apply_method = "_fix_apply_increase"
    _approval_routed = True

    consumer_id = fields.Many2one("fix.api.consumer", required=True, ondelete="cascade", index=True)
    endpoint_id = fields.Many2one("fix.api.endpoint", string="Endpoint", ondelete="cascade")
    requests_per_min = fields.Integer(string="Requests / minute", default=60, required=True)
    daily_quota = fields.Integer(string="Daily Quota", default=10000, required=True)
    proposed_requests_per_min = fields.Integer(string="Requested Requests / minute", copy=False)
    proposed_daily_quota = fields.Integer(string="Requested Daily Quota", copy=False)
    state = fields.Selection(
        [("active", "Active"), ("throttled", "Throttled")], required=True, default="active"
    )

    _rpm_positive = models.Constraint(
        "CHECK (requests_per_min > 0 AND daily_quota > 0)", "Quota limits must be positive"
    )

    @api.depends("consumer_id", "endpoint_id")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s / %s" % (
                rec.consumer_id.name or "?",
                rec.endpoint_id.code or "all endpoints",
            )

    def _fix_guarded_fields(self):
        # 'throttled' is the gateway's verdict on live traffic: a measured
        # state, not a configuration field. An Integration Admin changes the
        # LIMITS (which take effect on the next request - no pause/resume
        # trick needed); only server code records a throttle.
        return super()._fix_guarded_fields() | {
            "state",
            "proposed_requests_per_min",
            "proposed_daily_quota",
        }

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"consumer_id", "endpoint_id"}

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            self.check_access("create")
            rpm_ceiling = _param_int(self.env, QUOTA_CEILING_RPM_KEY, QUOTA_CEILING_RPM_DEFAULT)
            daily_ceiling = _param_int(
                self.env, QUOTA_CEILING_DAILY_KEY, QUOTA_CEILING_DAILY_DEFAULT
            )
            for vals in vals_list:
                if (
                    vals.get("requests_per_min", 0) > rpm_ceiling
                    or vals.get("daily_quota", 0) > daily_ceiling
                ):
                    raise UserError(
                        "A new quota starts at no more than %d requests/minute and %d/day. "
                        "Register it within that, then Request Limit Increase: a second "
                        "Integration Admin decides (M28-2)." % (rpm_ceiling, daily_ceiling)
                    )
        return super().create(vals_list)

    def write(self, vals):
        limits = {"requests_per_min", "daily_quota"} & set(vals)
        if limits and not self._fix_guard_open():
            self.check_access("write")
            for rec in self:
                if any(vals[name] > rec[name] for name in limits):
                    raise UserError(
                        "Raising a limit needs a second Integration Admin: use Request "
                        "Limit Increase on %s (M28-2). A limit goes down directly."
                        % rec.display_name
                    )
        audited = limits | ({"consumer_id", "endpoint_id"} & set(vals))
        before = {rec.id: {name: rec[name] for name in audited} for rec in self} if audited else {}
        result = super().write(vals)
        for rec in self if audited else ():
            moved = [name for name in audited if before[rec.id][name] != rec[name]]
            if moved:
                _integration_audit(
                    self.env,
                    "integration.quota_changed",
                    "fix.api.quota,%d" % rec.id,
                    "integration.quota_changed: %s %s by %s (now %d/min, %d/day)"
                    % (
                        rec.display_name,
                        ", ".join(sorted(moved)),
                        self.env.user.name,
                        rec.requests_per_min,
                        rec.daily_quota,
                    ),
                )
        return result

    def unlink(self):
        if not self._fix_guard_open():
            raise UserError(
                "Removing a quota lifts the limit altogether, so it is not done by hand. "
                "Lower the limit, or deactivate the consumer."
            )
        return super().unlink()

    def action_request_increase(self, requests_per_min=None, daily_quota=None, justification=None):
        """M28-2: propose higher limits and route them to a second Integration
        Admin. Nothing changes until the request is approved."""
        _require_integration_admin(self.env, "request a quota increase")
        text = _required_text(justification, "why this consumer needs a higher limit")
        for rec in self:
            try:
                rpm = int(requests_per_min or rec.requests_per_min)
                daily = int(daily_quota or rec.daily_quota)
            except (TypeError, ValueError) as exc:
                raise UserError("The requested limits must be whole numbers.") from exc
            if rpm <= 0 or daily <= 0:
                raise UserError("Quota limits must be positive.")
            if rpm <= rec.requests_per_min and daily <= rec.daily_quota:
                raise UserError(
                    "Nothing to approve: %d/min and %d/day are not above the current "
                    "limits on %s. A limit goes down directly." % (rpm, daily, rec.display_name)
                )
            if rec.approval_state == "pending":
                raise UserError("%s is already awaiting approval." % rec.display_name)
            rec._guarded().write({"proposed_requests_per_min": rpm, "proposed_daily_quota": daily})
            rec.action_request_approval(justification=text)
        return True

    def _fix_apply_increase(self):
        """The approved request's effect. Runs from the deciding task only."""
        self._approval_assert_routed()
        for rec in self:
            if not (rec.proposed_requests_per_min and rec.proposed_daily_quota):
                raise UserError("%s has no requested limits to apply." % rec.display_name)
            rec._guarded().write(
                {
                    "requests_per_min": rec.proposed_requests_per_min,
                    "daily_quota": rec.proposed_daily_quota,
                }
            )
        return True

    # ------------------------------------------------------------------
    # P1-6 completion (2026-11-05): the quota ACTS on measured traffic.
    # check_request_allowed is the gate the API edge (libs/py/fix_api_edge)
    # calls before serving; cron_enforce_quotas keeps the register's state
    # honest from the same measured counts.
    # ------------------------------------------------------------------

    def _measured_counts(self, consumer_id, endpoint_id=None, at=None):
        """Requests the consumer actually made (kind='api', every outcome —
        throttled attempts were still requests) in the last rolling minute
        and in the calendar day of `at`. Seeded rows are not traffic."""
        Log = self.env["fix.integration.log"].sudo()
        at = at or fields.Datetime.now()
        minute_start = at - timedelta(seconds=60)
        day_start = at.replace(hour=0, minute=0, second=0, microsecond=0)
        base = [("kind", "=", "api"), ("consumer_id", "=", consumer_id), ("measured", "=", True)]
        if endpoint_id:
            base.append(("endpoint_id", "=", endpoint_id))
        return {
            "minute": Log.search_count([*base, ("created_at", ">=", minute_start)]),
            "day": Log.search_count([*base, ("created_at", ">=", day_start)]),
        }

    @api.model
    def check_request_allowed(self, consumer, endpoint=None, at=None):
        """The server-side rate gate (P1-6). The API edge calls this BEFORE
        serving (and before logging) a request for `consumer`; it refuses when
        the measured window reaches a configured limit. A quota on the endpoint
        and a quota on the whole consumer both apply.

        Returns dict(allowed, reason, quota) so the caller can answer 429
        with the violated limit named. Counts come from the append-only
        integration log — never from a counter the caller could reset.
        """
        consumer = int(consumer) if isinstance(consumer, int) else consumer.id
        endpoint_id = None
        if endpoint:
            endpoint_id = int(endpoint) if isinstance(endpoint, int) else endpoint.id
        domain = [("consumer_id", "=", consumer)]
        if endpoint_id:
            domain.append(("endpoint_id", "in", [endpoint_id, False]))
        quotas = self.search(domain)
        if not quotas:
            return {"allowed": True, "reason": "", "quota": None}
        for quota in quotas:
            counts = self._measured_counts(consumer, quota.endpoint_id.id or None, at=at)
            if counts["minute"] >= quota.requests_per_min:
                return {
                    "allowed": False,
                    "reason": "rate: %d requests in the last minute (limit %d/min)"
                    % (counts["minute"], quota.requests_per_min),
                    "quota": quota,
                }
            if counts["day"] >= quota.daily_quota:
                return {
                    "allowed": False,
                    "reason": "quota: %d requests today (limit %d/day)"
                    % (counts["day"], quota.daily_quota),
                    "quota": quota,
                }
        return {"allowed": True, "reason": "", "quota": quotas[0]}

    @api.model
    def cron_enforce_quotas(self):
        """Keep every quota's state honest from measured traffic (P1-6):
        over either limit in the live window -> 'throttled' (audited); back
        under -> 'active' (audited). Server code only — state is guarded."""
        _require_service(self.env, "Quota enforcement")
        for quota in self.search([]):
            counts = self._measured_counts(quota.consumer_id.id, quota.endpoint_id.id or None)
            over = counts["minute"] >= quota.requests_per_min or counts["day"] >= quota.daily_quota
            if over and quota.state != "throttled":
                quota._guarded().write({"state": "throttled"})
                _integration_audit(
                    self.env,
                    "integration.quota_throttled",
                    "fix.api.quota,%d" % quota.id,
                    "integration.quota_throttled: %s measured %d/min (limit %d) "
                    "and %d/day (limit %d) — state set to throttled"
                    % (
                        quota.display_name,
                        counts["minute"],
                        quota.requests_per_min,
                        counts["day"],
                        quota.daily_quota,
                    ),
                )
            elif not over and quota.state == "throttled":
                quota._guarded().write({"state": "active"})
                _integration_audit(
                    self.env,
                    "integration.quota_released",
                    "fix.api.quota,%d" % quota.id,
                    "integration.quota_released: %s back under its limits "
                    "(%d/min, %d/day) — state set to active"
                    % (
                        quota.display_name,
                        counts["minute"],
                        counts["day"],
                    ),
                )
        return True


class FixEventTopic(models.Model):
    _name = "fix.event.topic"
    _inherit = ["fix.guarded.mixin"]
    _description = "Event Topic"
    _order = "code"

    code = fields.Char(required=True, help="The exact event type, e.g. itsm.ticket_created.")
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    schema_id = fields.Many2one("fix.event.schema", string="Schema")
    retention_days = fields.Integer(default=30, required=True)
    subscription_ids = fields.One2many("fix.event.subscription", "topic_id", string="Subscriptions")
    state = fields.Selection(
        [("active", "Active"), ("paused", "Paused")], required=True, default="active"
    )
    paused_at = fields.Datetime(readonly=True, copy=False)
    pause_reason = fields.Char(readonly=True, copy=False)

    @api.constrains("retention_days")
    def _check_retention_positive(self):
        # M28-8 / E B05: retention -5 was accepted while nothing read it.
        for rec in self:
            if rec.retention_days < 1:
                raise ValidationError(
                    "Topic retention must be at least 1 day (BRU-IPF-22): events "
                    "may not be deleted before retention."
                )

    def _fix_guarded_fields(self):
        return {"state", "paused_at", "pause_reason"}

    def write(self, vals):
        before = {rec.id: rec.retention_days for rec in self} if "retention_days" in vals else {}
        result = super().write(vals)
        for rec in self if before else ():
            if before[rec.id] != rec.retention_days:
                _integration_audit(
                    self.env,
                    "integration.retention_changed",
                    "fix.event.topic,%d" % rec.id,
                    "integration.retention_changed: %s %d -> %d days by %s"
                    % (rec.code, before[rec.id], rec.retention_days, self.env.user.name),
                )
        return result

    def action_pause(self, reason=None):
        """Hold the topic: while paused nothing on it reaches an in-process
        consumer or a webhook. Resume delivers what was held."""
        _require_integration_admin(self.env, "pause an event topic")
        self._guarded().write(
            {
                "state": "paused",
                "paused_at": fields.Datetime.now(),
                "pause_reason": (reason or "").strip() or False,
            }
        )
        self.env.cr.cache.pop("fix_paused_topic_codes", None)
        for rec in self:
            _integration_audit(
                self.env,
                "integration.topic_paused",
                "fix.event.topic,%d" % rec.id,
                "integration.topic_paused: %s by %s (%s)"
                % (rec.code, self.env.user.name, reason or "no reason given"),
            )
        return True

    def action_resume(self):
        _require_integration_admin(self.env, "resume an event topic")
        Outbox = self.env["fix.event.outbox"].sudo()
        for rec in self:
            held_since = rec.paused_at
            rec._guarded().write({"state": "active", "paused_at": False, "pause_reason": False})
            self.env.cr.cache.pop("fix_paused_topic_codes", None)
            # The relay marked what it held as relayed with no delivery: put it
            # back. A consumer that already took an event skips it (DI-05). By the
            # relay's stamp, not the event's date: an event's create_date is the
            # start of its transaction, which can predate the pause.
            if held_since:
                Outbox.search(
                    [("event_type", "=", rec.code), ("relayed_at", ">=", held_since)]
                ).write({"relayed_at": False})
            _integration_audit(
                self.env,
                "integration.topic_resumed",
                "fix.event.topic,%d" % rec.id,
                "integration.topic_resumed: %s by %s" % (rec.code, self.env.user.name),
            )
        return True

    @api.model
    def cron_purge_retention(self, limit=5000):
        """BRU-IPF-22 retention: delete a registered topic's events once they are
        past its retention and settled. An event is kept while a delivery can
        still use it: unrelayed, or with a failed or dead relay delivery, or with
        a webhook delivery not yet finished. Types with no topic are untouched."""
        _require_service(self.env, "Topic retention")
        Outbox = self.env["fix.event.outbox"].sudo()
        Delivery = self.env["fix.event.consumer.delivery"].sudo()
        Webhook = self.env["fix.webhook.delivery"].sudo()
        purged = 0
        for topic in self.sudo().search([("state", "=", "active")]):
            cutoff = fields.Datetime.now() - timedelta(days=topic.retention_days)
            events = Outbox.search(
                [
                    ("event_type", "=", topic.code),
                    ("company_id", "=", topic.company_id.id),
                    ("create_date", "<", cutoff),
                    ("relayed_at", "!=", False),
                ],
                limit=limit,
            )
            if not events:
                continue
            kept = Delivery.search(
                [("event_id", "in", events.ids), ("state", "in", ("failed", "dead"))]
            ).event_id
            kept |= Webhook.search(
                [("event_id", "in", events.ids), ("state", "not in", ("sent",))]
            ).event_id
            doomed = events - kept
            if not doomed:
                continue
            count = len(doomed)
            doomed.unlink()
            purged += count
            _integration_audit(
                self.env,
                "integration.events_purged",
                "fix.event.topic,%d" % topic.id,
                "integration.events_purged: %d %s event(s) older than %d days"
                % (count, topic.code, topic.retention_days),
            )
        return purged


class FixEventSchema(models.Model):
    _name = "fix.event.schema"
    _inherit = ["fix.approvable.mixin"]
    _description = "Event Schema"
    _order = "code, version desc"

    # Y06, spec s13: the engineer who registers a schema cannot approve its
    # breaking-change exception. The engine excludes the creator and the requester.
    _approval_domain = "other"
    _approval_group = INTEGRATION_ADMIN
    _approval_apply_method = "_fix_apply_breaking_publish"
    _approval_routed = True

    code = fields.Char(required=True)
    version = fields.Integer(required=True, default=1)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    schema_text = fields.Text(required=True, help="JSON Schema payload contract for the topic.")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("deprecated", "Deprecated")],
        required=True,
        default="draft",
    )

    _code_version_unique = models.Constraint(
        "UNIQUE (code, version, company_id)",
        "A schema code+version is unique per company: a correction ships as a new version.",
    )

    @api.depends("code", "version", "state")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s v%s (%s)" % (rec.code, rec.version, rec.state)

    @api.constrains("schema_text")
    def _check_schema_json(self):
        # M28-8 / E B06: "not json {{{" was published. A published contract
        # must at least parse; the registry is the source of truth.
        for rec in self:
            try:
                data = json.loads(rec.schema_text or "")
            except ValueError as parse_err:
                raise ValidationError(
                    "Schema text must be valid JSON (a JSON Schema object) - %s v%s "
                    "does not parse." % (rec.code, rec.version)
                ) from parse_err
            if not isinstance(data, dict):
                raise ValidationError(
                    "Schema text must be a JSON object for %s v%s." % (rec.code, rec.version)
                )

    def _fix_guarded_fields(self):
        return super()._fix_guarded_fields() | {"state"}

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.state == "draft" and bool(self._fix_breaking_changes())

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"code", "version", "schema_text"}

    def _fix_breaking_changes(self):
        """How this contract breaks consumers of the latest version in force."""
        self.ensure_one()
        prior = self.sudo().search(
            [
                ("code", "=", self.code),
                ("company_id", "=", self.company_id.id),
                ("state", "in", ("published", "deprecated")),
                ("id", "!=", self.id),
            ],
            order="version desc",
            limit=1,
        )
        if not prior:
            return []
        return _contract_narrowed(
            json.loads(prior.schema_text or "{}"), json.loads(self.schema_text or "{}")
        )

    def _frozen_fields(self):
        """BRU-IPF-06: once published (or deprecated) the contract, code and
        version are immutable - a breaking change ships as a NEW version."""
        return {"code", "version", "schema_text"}

    def _fix_form_locked_fields(self):
        locked = set(super()._fix_form_locked_fields())
        for rec in self:
            if rec.state in ("published", "deprecated"):
                locked |= rec._frozen_fields()
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = self._frozen_fields() & set(vals)
            if frozen:
                for rec in self:
                    if rec.state not in ("published", "deprecated"):
                        continue
                    changed = sorted(
                        n for n in frozen if rec._fix_guard_differs(n, vals[n], rec[n])
                    )
                    if changed:
                        raise UserError(
                            "Schema %s v%s is %s: %s cannot be edited in place. A "
                            "published contract is frozen (BRU-IPF-06) - ship the "
                            "correction as a NEW version record."
                            % (rec.code, rec.version, rec.state, ", ".join(changed))
                        )
        return super().write(vals)

    def action_publish(self):
        _require_integration_admin(self.env, "publish an event schema")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Publish a draft schema (this one is %s)." % rec.state)
        # The JSON contract is validated by _check_schema_json on save; the
        # publish transition re-parses so a draft written before the
        # constraint cannot slip through.
        self._check_schema_json()
        if not self.env.su:
            for rec in self:
                breaking = rec._fix_breaking_changes()
                if breaking:
                    raise UserError(
                        "%s v%s breaks the version in force: %s. Use Request Breaking-Change "
                        "Exception: a second Integration Admin decides, and both versions stay "
                        "live for the dual-publish period (BRU-IPF-06)."
                        % (rec.code, rec.version, "; ".join(breaking[:5]))
                    )
        return self._fix_publish()

    def action_request_breaking_exception(self, justification=None):
        _require_integration_admin(self.env, "request a breaking-change exception")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Request this on a draft schema (this one is %s)." % rec.state)
        return _route_to_second_admin(self, justification, "why this breaking change is needed")

    def _fix_apply_breaking_publish(self):
        self._approval_assert_routed()
        for rec in self:
            _integration_audit(
                self.env,
                "integration.schema_breaking_approved",
                "fix.event.schema,%d" % rec.id,
                "integration.schema_breaking_approved: %s v%s by %s"
                % (rec.code, rec.version, self.env.user.name),
            )
        return self._fix_publish()

    def _fix_publish(self):
        self._guarded().write({"state": "published"})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.schema_published",
                "fix.event.schema,%d" % rec.id,
                "integration.schema_published: %s v%s by %s"
                % (rec.code, rec.version, self.env.user.name),
            )
        return True

    def action_deprecate(self):
        """M28-8: a published contract is retired, not edited. A topic still on it
        keeps validating against it until its schema is changed."""
        _require_integration_admin(self.env, "deprecate an event schema")
        for rec in self:
            if rec.state != "published":
                raise UserError("Deprecate a published schema (this one is %s)." % rec.state)
        self._guarded().write({"state": "deprecated"})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.schema_deprecated",
                "fix.event.schema,%d" % rec.id,
                "integration.schema_deprecated: %s v%s by %s"
                % (rec.code, rec.version, self.env.user.name),
            )
        return True


class FixEventSubscription(models.Model):
    _name = "fix.event.subscription"
    _inherit = ["fix.approvable.mixin", "mail.thread", "mail.activity.mixin"]
    _description = "Event Subscription (webhook)"
    _order = "topic_id, consumer_id"

    # Y05: a webhook is where payloads leave the Company, so going live is a second
    # Integration Admin's decision. The dispatcher sends only for active and failing.
    _approval_domain = "other"
    _approval_group = INTEGRATION_ADMIN
    _approval_apply_method = "_fix_apply_go_live"
    _approval_routed = True

    name = fields.Char(required=True, default="New")
    consumer_id = fields.Many2one("fix.api.consumer", required=True, index=True)
    topic_id = fields.Many2one("fix.event.topic", required=True, ondelete="cascade", index=True)
    endpoint_url = fields.Char(
        required=True, help="The consumer webhook URL the event is delivered to."
    )
    secret_ref = fields.Char(
        string="Signing Secret Reference",
        help="Vault alias of the HMAC secret. Set at registration; after that it "
        "changes only through Rotate Signing Secret.",
    )
    state = fields.Selection(
        [
            ("draft", "Awaiting Go-Live"),
            ("active", "Active"),
            ("paused", "Paused"),
            ("failing", "Failing"),
        ],
        required=True,
        default="active",
    )
    consecutive_failures = fields.Integer(
        readonly=True, copy=False, help="BRU-IPF-18: reaching five disables the endpoint."
    )
    auto_disabled = fields.Boolean(
        readonly=True,
        copy=False,
        help="Disabled by repeated failures: events arriving now are dead-lettered, "
        "not queued, and resuming takes a stated reason.",
    )
    pause_reason = fields.Char(readonly=True, copy=False)

    @api.model
    def _webhook_allowlist(self):
        return _allowlist(self.env)

    @staticmethod
    def _host_allowed(host, allowlist):
        return _host_on_list(host, allowlist)

    @api.constrains("endpoint_url", "secret_ref")
    def _check_webhook_endpoint(self):
        # M28-1 / E B01-B03: a webhook is where payloads leave the Company.
        # https only, host on the operator's allow-list (default: empty =
        # refuse everything, localhost included), HMAC secret referenced in
        # the vault - never inline.
        for rec in self:
            problem = _outbound_url_problem(self.env, rec.endpoint_url)
            if problem:
                raise ValidationError(problem)
            if not rec.secret_ref:
                raise ValidationError(
                    "A webhook subscription needs its signing secret reference: "
                    "deliveries are HMAC-signed, and the secret is held in the vault."
                )
            problem = _vault_ref_problem(self.env, rec.secret_ref)
            if problem:
                raise ValidationError(problem)

    def _fix_guarded_fields(self):
        return super()._fix_guarded_fields() | {
            "state",
            "consecutive_failures",
            "auto_disabled",
            "pause_reason",
        }

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.approval_state != "approved"

    def _approval_pinned_fields(self) -> set:
        # The approval covers this destination: moving it takes the webhook out.
        return super()._approval_pinned_fields() | {"endpoint_url", "topic_id", "consumer_id"}

    def _approval_clear_stamp(self, reason):
        self.sudo()._guarded().write({"state": "draft"})

    def action_request_go_live(self, justification=None):
        _require_integration_admin(self.env, "request a webhook go-live")
        for rec in self:
            rec._check_webhook_endpoint()
            if rec.consumer_id.sudo().registration_state != "registered":
                raise UserError("Consumer %s is not registered yet." % rec.consumer_id.name)
        return _route_to_second_admin(self, justification, "why this webhook should go live")

    def _fix_apply_go_live(self):
        self._approval_assert_routed()
        self._check_webhook_endpoint()
        self._guarded().write(
            {
                "state": "active",
                "consecutive_failures": 0,
                "auto_disabled": False,
                "pause_reason": False,
            }
        )
        for rec in self:
            _integration_audit(
                self.env,
                "integration.webhook_live",
                "fix.event.subscription,%d" % rec.id,
                "integration.webhook_live: %s to %s approved by %s"
                % (rec.name, _webhook_host(rec.endpoint_url), self.env.user.name),
            )
        return True

    def _fix_form_locked_fields(self):
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked.add("secret_ref")
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.event.subscription") or "SUB/New"
                )
        records = super().create(vals_list)
        if not self._fix_guard_open():
            records._guarded().write({"state": "draft"})
        return records

    def write(self, vals):
        if "secret_ref" in vals and not self._fix_guard_open():
            for rec in self:
                if rec._fix_guard_differs("secret_ref", vals["secret_ref"], rec.secret_ref):
                    raise ValidationError(
                        "The signing secret reference changes only through Rotate Signing "
                        "Secret, which versions it and records an audit row (M28-10)."
                    )
        before = {rec.id: rec.endpoint_url for rec in self} if "endpoint_url" in vals else {}
        result = super().write(vals)
        for rec in self if before else ():
            if before[rec.id] != rec.endpoint_url:
                _integration_audit(
                    self.env,
                    "integration.webhook_repointed",
                    "fix.event.subscription,%d" % rec.id,
                    "integration.webhook_repointed: %s %s -> %s by %s"
                    % (
                        rec.name,
                        _webhook_host(before[rec.id]),
                        _webhook_host(rec.endpoint_url),
                        self.env.user.name,
                    ),
                )
                # A row from before the approval route has no approval to void.
                if not self._fix_guard_open() and rec.state in ("active", "failing"):
                    rec._guarded().write({"state": "draft"})
        return result

    def action_pause(self, reason=None):
        _require_integration_admin(self.env, "pause an event subscription")
        self._guarded().write({"state": "paused", "pause_reason": (reason or "").strip() or False})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.webhook_paused",
                "fix.event.subscription,%d" % rec.id,
                "integration.webhook_paused: %s by %s (%s)"
                % (rec.name, self.env.user.name, reason or "no reason given"),
            )
        return True

    def action_resume(self, reason=None):
        """AD-04: re-enabling is deliberate. The URL must pass the allow-list again,
        and missed events are not replayed automatically (AD-05)."""
        _require_integration_admin(self.env, "resume an event subscription")
        for rec in self:
            if rec.approval_state != "approved" and not self.env.su:
                raise UserError(
                    "%s has no go-live approval: use Request Go-Live, and a second "
                    "Integration Admin decides." % rec.name
                )
            if rec.auto_disabled:
                _required_text(reason, "why this failing endpoint can be re-enabled")
            rec._check_webhook_endpoint()
        self._guarded().write(
            {
                "state": "active",
                "consecutive_failures": 0,
                "auto_disabled": False,
                "pause_reason": False,
            }
        )
        for rec in self:
            _integration_audit(
                self.env,
                "integration.webhook_resumed",
                "fix.event.subscription,%d" % rec.id,
                "integration.webhook_resumed: %s by %s (%s)"
                % (rec.name, self.env.user.name, reason or "no reason given"),
            )
        return True

    def action_rotate_secret(self):
        """Bump the version in the signing-secret reference and record an audit
        row. No secrets manager exists (B-8): the operator loads the new value."""
        _require_integration_admin(self.env, "rotate a webhook signing secret")
        for rec in self:
            current = rec.secret_ref or ""
            new_ref = _bump_vault_ref(current)
            if not new_ref:
                raise UserError("%s has no signing secret reference to rotate." % rec.name)
            rec._guarded().write({"secret_ref": new_ref})
            _integration_audit(
                self.env,
                "integration.webhook_secret_rotated",
                "fix.event.subscription,%d" % rec.id,
                "integration.webhook_secret_rotated: %s %s -> %s by %s"
                % (rec.name, current, new_ref, self.env.user.name),
            )
        return True

    def _fix_pause_off_list(self, why):
        """Server path: take a subscription that fails the host rule out of service."""
        for rec in self:
            rec.sudo()._guarded().write({"state": "paused", "pause_reason": why[:200]})
            _integration_audit(
                self.env,
                "integration.webhook_paused",
                "fix.event.subscription,%d" % rec.id,
                "integration.webhook_paused: %s paused by the platform: %s" % (rec.name, why),
            )

    @api.model
    def cron_revalidate_subscriptions(self):
        """M28-1: the rule applied only when a row was saved, so subscriptions
        written earlier stayed active off the list. Pause each one with a note.
        Also lists on screen any host a system administrator set directly."""
        _require_service(self.env, "Webhook re-validation")
        self.env["fix.integration.allowed.host"].sudo()._fix_adopt_parameter_hosts()
        paused = 0
        for rec in self.sudo().search([("state", "in", ("active", "failing"))]):
            problem = _outbound_url_problem(self.env, rec.endpoint_url)
            if not problem and rec.secret_ref:
                problem = _vault_ref_problem(self.env, rec.secret_ref)
            elif not problem:
                problem = "no signing secret reference"
            if problem:
                rec._fix_pause_off_list("Failed re-validation: %s" % problem)
                paused += 1
        return paused


class FixEventDlq(models.Model):
    """The dead-letter register the DLQ screen shows.

    A12 P1-6 / M28-4: this table no longer pretends to be a second queue. It
    MIRRORS the real dead letters of the in-process relay
    (fix.event.consumer.delivery, state='dead') — cron_sync_dead_letters
    copies each one in exactly once — and holds the webhook dispatcher's dead
    letters; Replay re-enqueues the delivery behind the row. Entries with no
    linked delivery (rows seeded before the mirror existed) cannot be replayed:
    nothing could be re-delivered, and the action says so instead of pretending."""

    _name = "fix.event.dlq"
    _inherit = ["fix.approvable.mixin"]
    _description = "Dead-Letter Queue Entry"
    _order = "created_at desc, id desc"
    _rec_name = "display_label"

    # Y05: discarding gives up on an event for good, so a second Integration Admin
    # decides. Replay stays with one person: it loses nothing.
    _approval_domain = "other"
    _approval_group = INTEGRATION_ADMIN
    _approval_apply_method = "_fix_apply_discard"
    _approval_routed = True

    display_label = fields.Char(compute="_compute_label")
    topic_code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    payload = fields.Text(required=True)
    reason = fields.Char(required=True)
    attempts = fields.Integer(default=3, required=True)
    created_at = fields.Datetime(required=True, default=fields.Datetime.now)
    delivery_id = fields.Many2one(
        "fix.event.consumer.delivery",
        string="Relay Delivery",
        index=True,
        ondelete="set null",
        help="The relay delivery this entry mirrors; replay re-enqueues THIS row.",
    )
    webhook_delivery_id = fields.Many2one(
        "fix.webhook.delivery",
        string="Webhook Delivery",
        index=True,
        ondelete="set null",
        help="The webhook delivery that ran out of attempts; replay re-enqueues it.",
    )
    origin = fields.Selection(
        [("relay", "Relay"), ("webhook", "Webhook"), ("none", "No delivery behind it")],
        compute="_compute_origin",
    )
    replayed_at = fields.Datetime()
    replayed_by = fields.Many2one("res.users", string="Replayed By")
    decision_reason = fields.Char(
        string="Decision Reason", help="Why this entry was replayed or discarded."
    )
    state = fields.Selection(
        [("pending", "Pending"), ("replayed", "Replayed"), ("discarded", "Discarded")],
        required=True,
        default="pending",
    )

    _delivery_once = models.Constraint(
        "UNIQUE (delivery_id)", "A dead relay delivery is mirrored into the DLQ once"
    )
    _webhook_delivery_once = models.Constraint(
        "UNIQUE (webhook_delivery_id)", "A dead webhook delivery has one DLQ entry"
    )

    @api.depends("topic_code", "created_at")
    def _compute_label(self):
        for rec in self:
            rec.display_label = "%s @ %s" % (rec.topic_code, str(rec.created_at or "")[:19])

    @api.depends("delivery_id", "webhook_delivery_id")
    def _compute_origin(self):
        for rec in self:
            if rec.webhook_delivery_id:
                rec.origin = "webhook"
            elif rec.delivery_id:
                rec.origin = "relay"
            else:
                rec.origin = "none"

    def _fix_guarded_fields(self):
        # state, replayed_at and replayed_by change only through the
        # privileged replay/discard actions, never through a plain write —
        # so no row can be born 'replayed' or rewritten to 'discarded' (C03).
        # What was dead-lettered is evidence: it does not change either.
        return super()._fix_guarded_fields() | {
            "company_id",
            "state",
            "replayed_at",
            "replayed_by",
            "decision_reason",
            "topic_code",
            "payload",
            "reason",
            "attempts",
            "created_at",
            "delivery_id",
            "webhook_delivery_id",
        }

    @api.model_create_multi
    def create(self, vals_list):
        # M28-6: the table is engine-raised. A person does not add a dead letter.
        if not self.env.su:
            raise AccessError(
                "Dead-letter entries are raised by the relay and the webhook dispatcher, "
                "not typed by hand."
            )
        return super().create(vals_list)

    @api.model
    def cron_sync_dead_letters(self):
        """ir.cron fix.event.dlq (15 min): mirror every relay delivery whose
        state is 'dead' into the DLQ register, once per delivery."""
        _require_service(self.env, "The dead-letter mirror")
        Delivery = self.env["fix.event.consumer.delivery"].sudo()
        dead = Delivery.search([("state", "=", "dead")])
        vals_list = []
        if dead:
            already = set(
                self.sudo().search([("delivery_id", "in", dead.ids)]).mapped("delivery_id").ids
            )
            for delivery in dead:
                if delivery.id in already:
                    continue
                event = delivery.event_id
                vals_list.append(
                    {
                        "topic_code": delivery.event_type or event.event_type,
                        "company_id": event.company_id.id or self.env.company.id,
                        "payload": event.payload or "{}",
                        "reason": (delivery.last_error or "consumer dead-lettered")[:500],
                        "attempts": delivery.attempts,
                        "created_at": delivery.delivered_at or fields.Datetime.now(),
                        "delivery_id": delivery.id,
                    }
                )
            if vals_list:
                self.sudo().create(vals_list)
            # A replay that dead-letters AGAIN must resurface as pending: the
            # unique link stops a second row, so without this the screen would
            # keep showing 'replayed' while the delivery is dead once more
            # (BRU-IPF-14: a dead letter older than an hour is an incident).
            # A discarded entry stays discarded - that decision is final.
            for rec in self.sudo().search(
                [("delivery_id", "in", dead.ids), ("state", "=", "replayed")]
            ):
                delivered = rec.delivery_id.delivered_at
                if rec.replayed_at and delivered and delivered > rec.replayed_at:
                    rec.sudo().write(
                        {"state": "pending", "replayed_at": False, "replayed_by": False}
                    )
        # A dead letter whose relay delivery later succeeded (a consumer fix, then a
        # relay reset outside this screen) must not stay "pending" for ever: close it
        # truthfully, with no person named as the replayer, since nobody replayed it.
        recovered = self.sudo().search(
            [("state", "=", "pending"), ("delivery_id.state", "=", "done")]
        )
        for rec in recovered:
            rec._guarded().write(
                {
                    "state": "replayed",
                    "replayed_at": rec.delivery_id.delivered_at or fields.Datetime.now(),
                    "replayed_by": False,
                    "decision_reason": "Delivered on a later relay attempt, not from this screen",
                }
            )
        return len(vals_list)

    def _fix_step_up(self, otp):
        """M28-6: step-up on replay, as in cd_data_case. Returns a note for the
        audit row, or refuses. An enrolled user must give a valid code; a user
        with no authenticator is let through unless the parameter says required."""
        if self.env.su:
            return "service"
        user = self.env.user
        enrolled = "totp_enabled" in user._fields and user.sudo().totp_enabled
        if not enrolled:
            mode = self.env["ir.config_parameter"].sudo().get_param(REPLAY_STEP_UP_KEY, "enrolled")
            if mode == "required":
                raise UserError(
                    "A replay needs a step-up code, and you have no authenticator enrolled."
                )
            return "no authenticator enrolled"
        code = str(otp or "").strip()
        if not code.isdigit():
            raise UserError("Enter the 6-digit code from your authenticator to replay.")
        if not request:
            raise UserError("Step-up verification needs an interactive session.")
        try:
            user._check_credentials({"type": "totp", "token": int(code)}, {"interactive": True})
        except AccessDenied as exc:
            raise UserError("The authenticator code was not accepted.") from exc
        return "authenticator verified"

    def action_replay(self, reason=None, otp=None):
        """Privileged, audited, idempotent replay (M28-6 / P1-6).

        Re-enqueues the delivery behind the row. A relay delivery goes back to
        'failed' (the relay retries those and skips done/dead) with the event
        marked unrelayed, so the relay cron performs a real redelivery; a webhook
        delivery goes back to pending for the dispatcher. A row already replayed
        is refused; a row with no linked delivery cannot be replayed at all
        (nothing would be re-delivered). The reason is mandatory and step-up
        applies (spec s13)."""
        _require_integration_admin(self.env, "replay a dead-letter entry")
        for rec in self:
            if rec.state != "pending":
                raise UserError(
                    "This dead-letter entry was already %s at %s - replay it once."
                    % (rec.state, str(rec.replayed_at or "")[:19])
                )
            if rec.approval_state == "pending":
                raise UserError(
                    "A discard of this entry is awaiting approval: recall it to replay instead."
                )
            delivery = rec.sudo().delivery_id
            webhook = rec.sudo().webhook_delivery_id
            if not delivery and not webhook:
                raise UserError(
                    "This entry has no relay delivery behind it (a seeded row from "
                    "before the mirror): there is nothing to re-deliver."
                )
            if delivery and delivery.state != "dead":
                raise UserError(
                    "The linked relay delivery is no longer dead (state=%s) - it has "
                    "already been retried." % delivery.state
                )
            why = _required_text(reason, "why this dead letter should be replayed")
            step_up = rec._fix_step_up(otp)
            if delivery:
                # The relay retries 'failed' deliveries and skips done/dead, so a
                # replay = fresh attempt budget + the event back in the relay's
                # queue. Both writes are server-side service writes.
                delivery.write(
                    {
                        "state": "failed",
                        "attempts": 0,
                        "last_error": False,
                        "delivered_at": fields.Datetime.now(),
                    }
                )
                delivery.event_id.write({"relayed_at": False})
                ref = "delivery %d, event %s" % (delivery.id, delivery.event_id.event_id)
            else:
                webhook._fix_requeue()
                ref = "webhook delivery %d, event %s" % (webhook.id, webhook.event_id.event_id)
            rec.sudo()._guarded().write(
                {
                    "state": "replayed",
                    "replayed_at": fields.Datetime.now(),
                    "replayed_by": self.env.user.id,
                    "decision_reason": why[:200],
                }
            )
            _integration_audit(
                self.env,
                "integration.dlq_replayed",
                "fix.event.dlq,%d" % rec.id,
                "integration.dlq_replayed: %s (%s) re-enqueued by %s; step-up: %s; why: %s"
                % (rec.topic_code, ref, self.env.user.name, step_up, why),
            )
        return True

    def action_discard(self, reason=None):
        _require_integration_admin(self.env, "discard a dead-letter entry")
        for rec in self:
            if rec.state != "pending":
                raise UserError("Discard a pending DLQ entry")
        why = _required_text(reason, "why this dead letter can be discarded")
        self.sudo()._guarded().write({"decision_reason": why[:200]})
        if self.env.su:
            return self._fix_discard(why)
        return _route_to_second_admin(self, why, "why this dead letter can be discarded")

    def _fix_apply_discard(self):
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "pending":
                raise UserError("Discard a pending DLQ entry")
        return self._fix_discard(self.sudo().decision_reason)

    def _fix_discard(self, why):
        self.sudo()._guarded().write({"state": "discarded"})
        for rec in self:
            requester = rec.sudo().approval_request_id.requested_by_id.name or "the platform"
            _integration_audit(
                self.env,
                "integration.dlq_discarded",
                "fix.event.dlq,%d" % rec.id,
                "integration.dlq_discarded: %s discarded by %s, requested by %s; why: %s"
                % (rec.topic_code, self.env.user.name, requester, why),
            )
        return True

    def _approval_clear_stamp(self, reason):
        self.sudo()._guarded().write({"decision_reason": False})


class FixConnector(models.Model):
    _name = "fix.connector"
    _inherit = ["fix.approvable.mixin"]
    _description = "External Connector"
    _order = "connector_type, name"

    # Y05: a connector a person registers is not live until a second Integration Admin
    # says so. A probe may degrade it, but evidence alone cannot put it in service.
    _approval_domain = "other"
    _approval_group = INTEGRATION_ADMIN
    _approval_apply_method = "_fix_apply_go_live"
    _approval_routed = True

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    connector_type = fields.Selection(
        [
            ("payment", "Payment"),
            ("logistics", "Logistics"),
            ("government", "Government / NBR"),
            ("messaging", "Messaging"),
            ("cloud", "Cloud / Storage"),
            ("crm", "CRM"),
            ("bi", "Analytics"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    endpoint = fields.Char()
    credential_id = fields.Many2one("fix.connector.credential", string="Credential")
    fallback_connector_id = fields.Many2one(
        "fix.connector",
        string="Fallback Connector",
        help="BRU-IPF-12: the registered fallback of the same type. Traffic does not "
        "flow through the register yet, so this records the fallback; it switches nothing.",
    )
    last_latency_ms = fields.Integer(string="Last Latency (ms)")
    last_success_at = fields.Datetime()
    last_probe_at = fields.Datetime(string="Last Measured At", readonly=True, copy=False)
    last_probe_note = fields.Char(string="Probe Note", readonly=True, copy=False)
    awaiting_go_live = fields.Boolean(string="Awaiting Go-Live", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("registered", "Registered, Not Live"),
            ("live", "Live"),
            ("degraded", "Degraded"),
            ("down", "Down"),
            ("disabled", "Disabled"),
        ],
        required=True,
        default="live",
    )

    @api.constrains("fallback_connector_id", "connector_type")
    def _check_fallback(self):
        for rec in self:
            fallback = rec.fallback_connector_id
            if fallback and fallback == rec:
                raise ValidationError("A connector cannot be its own fallback.")
            if fallback and fallback.connector_type != rec.connector_type:
                raise ValidationError(
                    "The fallback of a %s connector must be a %s connector."
                    % (rec.connector_type, rec.connector_type)
                )

    def _fix_guarded_fields(self):
        # M28-9: health is MEASURED (probe / circuit breaker writes it as
        # server code), never typed by a user. The mark actions below are the
        # operator's manual override of last resort - privileged.
        return super()._fix_guarded_fields() | {
            "state",
            "last_latency_ms",
            "last_success_at",
            "last_probe_at",
            "last_probe_note",
            "awaiting_go_live",
        }

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.awaiting_go_live

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"endpoint", "credential_id"}

    def _approval_clear_stamp(self, reason):
        self.sudo()._guarded().write({"state": "registered", "awaiting_go_live": True})

    def action_request_go_live(self, justification=None):
        _require_integration_admin(self.env, "request a connector go-live")
        for rec in self:
            if not rec.awaiting_go_live:
                raise UserError("%s is not awaiting go-live." % rec.name)
            if not rec.endpoint:
                raise UserError("%s has no endpoint to take live." % rec.name)
            problem = _outbound_url_problem(self.env, rec.endpoint)
            if problem:
                raise UserError(problem)
        return _route_to_second_admin(self, justification, "why this connector should go live")

    def _fix_apply_go_live(self):
        self._approval_assert_routed()
        self._guarded().write({"state": "live", "awaiting_go_live": False})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.connector_live",
                "fix.connector,%d" % rec.id,
                "integration.connector_live: %s approved by %s" % (rec.name, self.env.user.name),
            )
        return True

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            for vals in vals_list:
                problem = vals.get("endpoint") and _outbound_url_problem(self.env, vals["endpoint"])
                if problem:
                    raise ValidationError(problem)
        records = super().create(vals_list)
        if not self._fix_guard_open():
            records._guarded().write({"state": "registered", "awaiting_go_live": True})
        return records

    def write(self, vals):
        # M28-1: the bKash connector, credential attached, was repointed to
        # http://attacker unaudited. The form posts every field, so only a CHANGE
        # is checked: a connector registered earlier can still be renamed.
        watched = {"endpoint", "credential_id"} & set(vals)
        if vals.get("endpoint") and not self._fix_guard_open():
            for rec in self:
                if rec.endpoint != vals["endpoint"]:
                    problem = _outbound_url_problem(self.env, vals["endpoint"])
                    if problem:
                        raise ValidationError(problem)
        before = {rec.id: (rec.endpoint, rec.credential_id.name) for rec in self} if watched else {}
        result = super().write(vals)
        for rec in self if watched else ():
            if before[rec.id] != (rec.endpoint, rec.credential_id.name):
                _integration_audit(
                    self.env,
                    "integration.connector_repointed",
                    "fix.connector,%d" % rec.id,
                    "integration.connector_repointed: %s endpoint %s -> %s, credential %s -> "
                    "%s by %s"
                    % (
                        rec.name,
                        _webhook_host(before[rec.id][0]) or "-",
                        _webhook_host(rec.endpoint) or "-",
                        before[rec.id][1] or "-",
                        rec.credential_id.name or "-",
                        self.env.user.name,
                    ),
                )
                # A new destination is a new go-live, approved before or not.
                if not self._fix_guard_open():
                    rec._guarded().write({"state": "registered", "awaiting_go_live": True})
        return result

    # ------------------------------------------------------------------
    # P1-6 completion (2026-11-05): the health probe exists. It measures
    # credential validity and this connector's recorded traffic, and refuses to
    # fabricate the rest. M28-9 (2026-11-07): with dispatch enabled and the host
    # passing the gate, a silent connector also gets one real HEAD request, and
    # the row carries a note saying what was and was not measured. The probe can
    # only DEGRADE on real evidence and only RECOVER on real evidence. A
    # 'disabled' connector is the operator's decision: the probe never touches it.
    # ------------------------------------------------------------------

    PROBE_WINDOW = timedelta(minutes=30)

    def _fix_window_traffic(self):
        window_start = fields.Datetime.now() - self.PROBE_WINDOW
        return (
            self.env["fix.integration.log"]
            .sudo()
            .search(
                [
                    ("connector_id", "=", self.id),
                    ("created_at", ">=", window_start),
                    ("measured", "=", True),
                ],
                order="created_at desc",
                limit=50,
            )
        )

    def _fix_active_probe(self):
        """One real request when the gate allows it. Returns why none was made."""
        self.ensure_one()
        if not self.endpoint:
            return "no endpoint configured"
        refusal = _dispatch_refusal(self.env, self.endpoint)
        if refusal:
            return refusal
        started = time.monotonic()
        try:
            code = _http_head(self.endpoint, PROBE_TIMEOUT_SECONDS)
        except requests.RequestException:
            code = 0
        self.env["fix.integration.log"].sudo()._log_request(
            "probe",
            status="success" if code and code < 500 else "failed",
            connector=self,
            latency_ms=int((time.monotonic() - started) * 1000),
            status_code=code,
        )
        return ""

    def _probe_health(self):
        """Measure one connector's health. Returns the verdict dict; the
        caller (cron / action_probe) writes it through the guard."""
        self.ensure_one()
        traffic = self._fix_window_traffic()
        not_run = ""
        if not traffic:
            not_run = self._fix_active_probe()
            traffic = self._fix_window_traffic()
        verdict = {"state": None, "last_latency_ms": None, "last_success_at": None}
        successes = traffic.filtered(lambda row: row.status == "success")
        failures = traffic.filtered(lambda row: row.status == "failed")
        credential_expired = bool(
            self.credential_id.expires_on
            and self.credential_id.expires_on < fields.Date.context_today(self)
        )
        if successes:
            verdict["last_success_at"] = successes[0].created_at
            verdict["last_latency_ms"] = int(sum(successes.mapped("latency_ms")) / len(successes))
        if credential_expired:
            # an expired credential is hard evidence the connector cannot
            # authenticate — degrade whatever the traffic says
            verdict["state"] = "degraded"
        elif failures and not successes:
            verdict["state"] = "degraded"
        elif successes:
            verdict["state"] = "live"
        # no traffic + valid credential: no evidence either way — leave the
        # state alone (a silent connector is not a failing connector)
        if verdict["state"]:
            verdict["last_probe_at"] = fields.Datetime.now()
            verdict["last_probe_note"] = "%d log row(s) in the window, credential %s" % (
                len(traffic),
                "expired" if credential_expired else "valid",
            )
        else:
            verdict["last_probe_note"] = (
                "No evidence: no traffic in the window; no probe sent: %s"
                % (not_run or "no response recorded")
            )
        return verdict

    def action_probe(self):
        """On-demand probe (Integration Admin): degrade/recover the
        connector from measured evidence only, audited when it changes."""
        _require_integration_admin(self.env, "probe a connector")
        return self._apply_probe()

    @api.model
    def cron_probe_connectors(self):
        """Every 15 minutes: refresh connector health from measured
        evidence (P1-6 / M28-9). Server code; guarded fields stay closed."""
        _require_service(self.env, "The connector probe")
        return self.search([])._apply_probe()

    def _apply_probe(self):
        for rec in self:
            if rec.state == "disabled":
                continue
            before_state = rec.state
            verdict = rec._probe_health()
            if rec.awaiting_go_live and verdict["state"] == "live":
                verdict["state"] = None
            writes = {k: v for k, v in verdict.items() if v is not None and rec[k] != v}
            if not writes:
                continue
            rec._guarded().write(writes)
            if "state" in writes:
                _integration_audit(
                    self.env,
                    "integration.connector_probed",
                    "fix.connector,%d" % rec.id,
                    "integration.connector_probed: %s state %s -> %s from measured evidence (%s)"
                    % (rec.name, before_state, rec.state, verdict.get("last_probe_note")),
                )
        return True

    def _fix_mark(self, state, reason):
        for rec in self:
            before = rec.state
            rec._guarded().write({"state": state})
            _integration_audit(
                self.env,
                "integration.connector_marked",
                "fix.connector,%d" % rec.id,
                "integration.connector_marked: %s %s -> %s by %s (manual override); why: %s"
                % (rec.name, before, state, self.env.user.name, reason or "not stated"),
            )
        return True

    def action_mark_degraded(self, reason=None):
        _require_integration_admin(self.env, "mark a connector degraded")
        return self._fix_mark("degraded", reason)

    def action_mark_down(self, reason=None):
        _require_integration_admin(self.env, "mark a connector down")
        return self._fix_mark("down", _required_text(reason, "why this connector is down"))

    def action_disable(self, reason=None):
        _require_integration_admin(self.env, "disable a connector")
        return self._fix_mark("disabled", _required_text(reason, "why this connector is disabled"))

    def action_mark_live(self, reason=None):
        """M28-9: down -> live took a button and left no trace. A reason is always
        needed, and a down connector needs a measured success inside the window."""
        _require_integration_admin(self.env, "mark a connector live")
        why = _required_text(reason, "why this connector is live")
        cutoff = fields.Datetime.now() - self.PROBE_WINDOW
        for rec in self:
            if rec.awaiting_go_live:
                raise UserError(
                    "%s has no go-live approval: use Request Go-Live, and a second "
                    "Integration Admin decides." % rec.name
                )
            if rec.state == "down" and not (rec.last_success_at and rec.last_success_at >= cutoff):
                raise UserError(
                    "%s is down and has no measured success in the last 30 minutes: run "
                    "Probe first. A connector does not come back on someone's word." % rec.name
                )
        return self._fix_mark("live", why)


class FixConnectorCredential(models.Model):
    _name = "fix.connector.credential"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _description = "Connector Credential Reference"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    auth_type = fields.Selection(
        [
            ("api_key", "API Key"),
            ("oauth2", "OAuth 2.0"),
            ("basic", "Basic"),
            ("mtls", "Mutual TLS"),
        ],
        required=True,
        default="api_key",
    )
    secret_ref = fields.Char(
        string="Vault Reference",
        required=True,
        help="Vault path or alias. The secret VALUE never lands in this model (SEC-101). "
        "Set at registration; after that it changes only through Rotate Reference.",
    )
    expires_on = fields.Date()
    rotated_at = fields.Datetime(string="Reference Last Rotated", readonly=True, copy=False)
    rotated_by_id = fields.Many2one("res.users", string="Rotated By", readonly=True, copy=False)
    expiry_alerted_on = fields.Date(string="Expiry Alert Raised", readonly=True, copy=False)
    active = fields.Boolean(default=True)

    @api.constrains("secret_ref")
    def _check_secret_ref_vault(self):
        # M28-10 / E D07: a raw key-shaped string was stored in clear.
        for rec in self:
            problem = rec.secret_ref and _vault_ref_problem(self.env, rec.secret_ref)
            if problem:
                raise ValidationError(problem)

    def _fix_guarded_fields(self):
        return {"rotated_at", "rotated_by_id", "expiry_alerted_on"}

    def _fix_form_locked_fields(self):
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked.add("secret_ref")
        return locked

    def write(self, vals):
        if "secret_ref" in vals and not self._fix_guard_open():
            for rec in self:
                if rec._fix_guard_differs("secret_ref", vals["secret_ref"], rec.secret_ref):
                    raise UserError(
                        "The vault reference changes only through Rotate Reference, which "
                        "versions it and records an audit row (M28-10)."
                    )
        before = {rec.id: rec.expires_on for rec in self} if "expires_on" in vals else {}
        result = super().write(vals)
        for rec in self if before else ():
            if before[rec.id] != rec.expires_on:
                # A new date restarts the alert, and pushing it out hides an expiry.
                rec.sudo()._guarded().write({"expiry_alerted_on": False})
                _integration_audit(
                    self.env,
                    "integration.credential_expiry_changed",
                    "fix.connector.credential,%d" % rec.id,
                    "integration.credential_expiry_changed: %s %s -> %s by %s"
                    % (rec.name, before[rec.id], rec.expires_on, self.env.user.name),
                )
        return result

    def action_rotate(self, expires_on=None):
        """M28-10 / B-8: version the reference and record an audit row. No secrets
        manager exists, so this does not change any secret: the operator loads the
        new value at the new path in the vault."""
        _require_integration_admin(self.env, "rotate a connector credential reference")
        new_expiry = False
        if expires_on:
            try:
                new_expiry = fields.Date.to_date(str(expires_on).strip())
            except ValueError as exc:
                raise UserError("Give the new expiry date as YYYY-MM-DD.") from exc
        for rec in self:
            current = rec.secret_ref or ""
            new_ref = _bump_vault_ref(current)
            if not new_ref:
                raise UserError("%s has no vault reference to rotate." % rec.name)
            vals = {
                "secret_ref": new_ref,
                "rotated_at": fields.Datetime.now(),
                "rotated_by_id": self.env.user.id,
            }
            if new_expiry:
                vals["expires_on"] = new_expiry
            rec._guarded().write(vals)
            _integration_audit(
                self.env,
                "integration.credential_rotated",
                "fix.connector.credential,%d" % rec.id,
                "integration.credential_rotated: %s reference %s -> %s by %s (reference only: "
                "no secret was changed)" % (rec.name, current, new_ref, self.env.user.name),
            )
        return True

    @api.model
    def cron_alert_expiring(self):
        """FR-IPF-041: flag each credential once, inside its alert window."""
        _require_service(self.env, "The credential expiry alert")
        days = _param_int(self.env, CREDENTIAL_ALERT_DAYS_KEY, CREDENTIAL_ALERT_DAYS_DEFAULT)
        today = fields.Date.context_today(self)
        due = self.sudo().search(
            [
                ("expires_on", "!=", False),
                ("expires_on", "<=", today + timedelta(days=days)),
                ("expiry_alerted_on", "=", False),
            ]
        )
        for rec in due:
            rec._guarded().write({"expiry_alerted_on": today})
            when = "expired on" if rec.expires_on < today else "expires on"
            told = _notify_integration_admins(
                rec,
                "Credential %s %s %s" % (rec.name, when, rec.expires_on),
                "Rotate the reference and load the new value in the vault.",
            )
            _integration_audit(
                self.env,
                "integration.credential_expiring",
                "fix.connector.credential,%d" % rec.id,
                "integration.credential_expiring: %s %s %s; %d Integration Admin(s) told"
                % (rec.name, when, rec.expires_on, told),
            )
        return len(due)


class FixSyncConflict(models.Model):
    """A conflict the offline sync engine detected. Rows come from the engine's
    ledger (cron_ingest_ledger_conflicts); a person resolves, never raises, one."""

    _name = "fix.sync.conflict"
    _inherit = ["fix.guarded.mixin"]
    _description = "Offline Sync Conflict"
    _order = "detected_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    device_ref = fields.Char(string="Device / Client", required=True, index=True)
    res_model = fields.Char(string="Record Model", required=True)
    res_id = fields.Integer(string="Record ID", required=True)
    field_name = fields.Char(required=True)
    local_value = fields.Char(help="What the device holds.")
    remote_value = fields.Char(help="What the server holds.")
    detected_at = fields.Datetime(required=True, default=fields.Datetime.now)
    source_command_id = fields.Char(
        string="Offline Command",
        index=True,
        copy=False,
        help="The offline command in the idempotency ledger that collided.",
    )
    engine_note = fields.Char(string="Engine Note", copy=False)
    policy_class = fields.Selection(
        SYNC_CLASSES, string="Field Class (BRU-IPF-17)", compute="_compute_policy_class"
    )
    resolution = fields.Selection(
        [
            ("pending", "Pending"),
            ("local_wins", "Local Wins"),
            ("remote_wins", "Remote Wins"),
            ("merged", "Manually Merged"),
            ("dismissed", "Closed, Nothing Applied"),
        ],
        required=True,
        default="pending",
    )
    resolution_note = fields.Char(copy=False)
    resolved_by_id = fields.Many2one("res.users", string="Resolved By", copy=False)
    resolved_at = fields.Datetime(copy=False)

    _source_command_once = models.Constraint(
        "UNIQUE (source_command_id)", "An offline command raises one conflict"
    )

    @api.depends("res_model", "field_name")
    def _compute_policy_class(self):
        for rec in self:
            rec.policy_class = rec._fix_sync_class()

    def _fix_sync_class(self):
        """client / server / denied for this conflict's target (BRU-IPF-17)."""
        self.ensure_one()
        model = self.res_model or ""
        if model.startswith(SYNC_NEVER_TARGETS) or model not in SYNC_TARGET_POLICY:
            return "denied"
        return "client" if self.field_name in SYNC_TARGET_POLICY[model] else "server"

    def _fix_guarded_fields(self):
        # M28-7 / N-M28-1: the target and the collided values are the engine's
        # evidence. Re-pointing a pending conflict is how an Integration Admin
        # reached ir.config_parameter.
        return {
            "name",
            "company_id",
            "device_ref",
            "res_model",
            "res_id",
            "field_name",
            "local_value",
            "remote_value",
            "detected_at",
            "source_command_id",
            "engine_note",
            "resolution",
            "resolution_note",
            "resolved_by_id",
            "resolved_at",
        }

    @api.model_create_multi
    def create(self, vals_list):
        # N-M28-2: a person cannot raise a conflict: a screen-made row carried
        # empty values, and Local Wins then blanked the target field.
        if not self.env.su:
            raise AccessError(
                "Sync conflicts are raised by the offline sync engine, not typed by hand."
            )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.sync.conflict") or "SYC/New"
                )
        return super().create(vals_list)

    @api.model
    def cron_ingest_ledger_conflicts(self, limit=500):
        """M28-7: feed the register from the engine. offline_sync_api records every
        command it applied over a server change as conflict_applied in the ledger;
        each becomes one row here. The server's state stood, so the row is
        server-authoritative and the screen can only confirm that."""
        _require_service(self.env, "The sync conflict feed")
        if "fix.offline.idempotency.ledger" not in self.env:
            return 0
        Ledger = self.env["fix.offline.idempotency.ledger"].sudo()
        rows = Ledger.search([("status", "=", "conflict_applied")], order="id", limit=limit)
        if not rows:
            return 0
        seen = set(
            self.sudo()
            .search([("source_command_id", "in", rows.mapped("command_id"))])
            .mapped("source_command_id")
        )
        vals_list = []
        for row in rows:
            if row.command_id in seen:
                continue
            try:
                response = json.loads(row.response_payload or "{}")
            except ValueError:
                response = {}
            vals_list.append(
                {
                    "company_id": row.company_id.id,
                    "device_ref": row.device_id or "DEV-UNKNOWN",
                    "res_model": row.model,
                    "res_id": row.record_id,
                    "field_name": "state",
                    "local_value": row.operation,
                    "remote_value": str(response.get("state") or "")[:200] or False,
                    "detected_at": row.applied_at,
                    "source_command_id": row.command_id,
                    "engine_note": (row.conflict_reason or "")[:200] or False,
                }
            )
        if vals_list:
            self.sudo().create(vals_list)
        return len(vals_list)

    def _resolve(self, resolution, note=None):
        _require_integration_admin(self.env, "resolve an offline sync conflict")
        for rec in self:
            if rec.resolution != "pending":
                raise UserError("Resolve a pending conflict (this one is %s)" % rec.resolution)
            rec._fix_check_policy(resolution, note)
            if resolution in ("local_wins", "remote_wins"):
                rec._apply_resolution_value(resolution)
        self._guarded().sudo().write(
            {
                "resolution": resolution,
                "resolution_note": (note or "").strip()[:200] or False,
                "resolved_by_id": self.env.user.id,
                "resolved_at": fields.Datetime.now(),
            }
        )
        for rec in self:
            if resolution == "local_wins" or (
                resolution == "remote_wins" and rec._fix_sync_class() == "client"
            ):
                effect = " — value applied to %s#%s" % (rec.res_model, rec.res_id)
            elif resolution == "remote_wins":
                effect = " — the server's value stands, nothing written"
            else:
                effect = " (nothing auto-applied: %s)" % (note or "").strip()
            _integration_audit(
                self.env,
                "integration.sync_conflict_resolved",
                "fix.sync.conflict,%d" % rec.id,
                "integration.sync_conflict_resolved: %s %s on %s.%s by %s%s"
                % (
                    rec.name,
                    resolution,
                    rec.res_model,
                    rec.field_name,
                    self.env.user.name,
                    effect,
                ),
            )
        return True

    def _fix_check_policy(self, resolution, note):
        """BRU-IPF-17, before anything is written."""
        self.ensure_one()
        klass = self._fix_sync_class()
        if resolution == "dismissed":
            _required_text(note, "why this conflict is closed with nothing applied")
            return
        if klass == "denied":
            raise UserError(
                "%s.%s is not a sync target (allowed: %s). Nothing can be applied there, and "
                "%s is never reachable. Close the row with nothing applied."
                % (
                    self.res_model,
                    self.field_name,
                    ", ".join(sorted(SYNC_TARGET_POLICY)),
                    ", ".join(SYNC_NEVER_TARGETS),
                )
            )
        if klass == "server" and resolution != "remote_wins":
            raise UserError(
                "%s.%s is server-authoritative (BRU-IPF-17: assignment, pricing, stock and "
                "state): the server's value stands. Use Remote Wins."
                % (self.res_model, self.field_name)
            )
        if resolution == "merged":
            _required_text(note, "how this conflict was reconciled by hand")

    def _apply_resolution_value(self, resolution):
        """P1-6 completion (M28-7): a resolution is not a label — the chosen
        value is WRITTEN to the collided record, when the field is
        client-authoritative. Remote Wins on a server-authoritative field writes
        nothing: the server's value already stands, and a state changes only
        through its own workflow.

        The write runs as the caller when the caller may write the record, so the
        owner's ACL, rules and guards apply. An Integration Admin normally holds no
        role on the target, so otherwise it is a service write: narrow, because
        _fix_check_policy has already limited it to the table above.

        Refuses (nothing resolved) when the record, the field or the model
        is gone, the value is empty, or the field is not text-like.
        """
        self.ensure_one()
        if self._fix_sync_class() == "server":
            return False
        if self.res_model not in self.env:
            raise UserError(
                "Cannot apply %s on %s: model %r no longer exists — resolve "
                "as 'merged' once handled." % (resolution, self.name, self.res_model)
            )
        target = self.env[self.res_model].browse(self.res_id)
        if not target.sudo().exists():
            raise UserError(
                "Cannot apply %s on %s: record %s#%d no longer exists — resolve "
                "as 'merged' once handled." % (resolution, self.name, self.res_model, self.res_id)
            )
        field_def = target._fields.get(self.field_name)
        if field_def is None:
            raise UserError(
                "Cannot apply %s on %s: field %r no longer exists on %s — "
                "resolve as 'merged' once handled."
                % (resolution, self.name, self.field_name, self.res_model)
            )
        if field_def.type not in ("char", "text", "html"):
            raise UserError(
                "Cannot auto-apply %s on %s.%s: the field is %s and the stored "
                "collision values are text — reconcile by hand and use 'merged'."
                % (resolution, self.res_model, self.field_name, field_def.type)
            )
        value = self.local_value if resolution == "local_wins" else self.remote_value
        if not (value or "").strip():
            # N-M28-2: Local Wins on an empty value blanked the target field.
            raise UserError(
                "%s has no %s value to apply: applying it would blank %s.%s."
                % (
                    self.name,
                    "device" if resolution == "local_wins" else "server",
                    self.res_model,
                    self.field_name,
                )
            )
        if self.res_model == "res.partner" and target.sudo().user_ids:
            raise UserError(
                "Partner %d is linked to a login: its contact details are not a sync target."
                % self.res_id
            )
        company = target.sudo()["company_id"] if "company_id" in target._fields else None
        if company and not self.env.su and company not in self.env.user.company_ids:
            raise UserError("%s#%d belongs to another company." % (self.res_model, self.res_id))
        writer = target if target.has_access("write") else target.sudo()
        writer.write({self.field_name: value})
        return True

    def action_local_wins(self):
        return self._resolve("local_wins")

    def action_remote_wins(self):
        return self._resolve("remote_wins")

    def action_merged(self, note=None):
        """The operator states how they reconciled it. Applies nothing."""
        return self._resolve("merged", note)

    def action_dismiss(self, note=None):
        """Close a row whose target cannot take a value: gone, or off the list."""
        return self._resolve("dismissed", note)

    def action_resolve_decision(self, decision=None, note=None):
        """The Offline Sync page's capture (M28 capture audit, 2026-11-14): pick a
        pending conflict, choose the decision, write the note. The same _resolve
        as the four buttons above, so the group, the BRU-IPF-17 policy, the note
        rules and the audit row all still decide."""
        if decision not in SYNC_DECISIONS:
            raise UserError(
                "Choose the decision: Local Wins, Remote Wins, Manually Merged or "
                "Closed, Nothing Applied."
            )
        return self._resolve(decision, note)


class FixIntegrationLog(models.Model):
    """The measured traffic log: API requests, event deliveries, webhook
    attempts and connector probes — the data the five reports compute from.

    A12 P1-6 / M28-5: system-written only. No group holds create or write on
    this model, and the model itself refuses a user-driven create/write as a
    second lock: measured figures must not be typeable (50 forged 'success'
    rows lifted the SLO to 100%). Server code logs through _log_request, and
    only those rows carry measured=True: anything else is seed data, and the
    reports leave it out."""

    _name = "fix.integration.log"
    _description = "Integration Log Entry"
    _order = "created_at desc, id desc"

    kind = fields.Selection(
        [
            ("api", "API Request"),
            ("delivery", "Event Delivery"),
            ("webhook", "Webhook Attempt"),
            ("probe", "Connector Probe"),
        ],
        required=True,
        index=True,
    )
    company_id = fields.Many2one("res.company", index=True, default=lambda self: self.env.company)
    measured = fields.Boolean(
        readonly=True,
        index=True,
        help="Written by the platform for a real request. A row without this is seed data.",
    )
    consumer_id = fields.Many2one("fix.api.consumer", string="Consumer", index=True)
    endpoint_id = fields.Many2one("fix.api.endpoint", string="Endpoint", index=True)
    route = fields.Char(help="The route served, when no catalogue entry matches it.")
    topic_code = fields.Char(index=True)
    connector_id = fields.Many2one(
        "fix.connector",
        string="Connector",
        index=True,
        help="The connector the attempt ran through — the probe derives "
        "health (state/latency) from these rows (P1-6).",
    )
    subscription_id = fields.Many2one(
        "fix.event.subscription",
        string="Subscription",
        index=True,
        help="The webhook attempt's subscription — the success-rate report "
        "matches on THIS, not on the consumer (M28-12).",
    )
    status = fields.Selection(
        [
            ("success", "Success"),
            ("throttled", "Throttled"),
            ("failed", "Failed"),
            ("not_sent", "Not Sent"),
        ],
        required=True,
        default="success",
        index=True,
    )
    outcome = fields.Char(help="Why it was not sent, or what came back.")
    latency_ms = fields.Integer()
    status_code = fields.Integer()
    created_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        # P1-6: only server code logs. The old context key was a value any
        # JSON-RPC caller can send, so only the superuser environment counts.
        if not self.env.su:
            raise AccessError(
                "The integration log is written by the platform (measured "
                "requests, deliveries and webhook attempts only) — it cannot be "
                "created by hand."
            )
        return super().create(vals_list)

    def write(self, vals):
        raise AccessError(
            "The integration log is append-only: a measured request cannot be "
            "edited afterwards (flip a failure to success and the SLO lies)."
        )

    def unlink(self):
        raise AccessError("The integration log is append-only: entries cannot be deleted.")

    @api.private
    @api.model
    def _log_request(
        self,
        kind,
        status="success",
        consumer=None,
        endpoint=None,
        topic_code=None,
        subscription=None,
        connector=None,
        latency_ms=None,
        status_code=None,
        created_at=None,
        outcome=None,
        route=None,
    ):
        """The one path server code logs a request/delivery/webhook attempt
        through (P1-6). @api.private: never callable over RPC."""
        vals = {
            "kind": kind,
            "status": status,
            "measured": True,
            "latency_ms": latency_ms,
            "status_code": status_code,
            "created_at": created_at or fields.Datetime.now(),
        }
        Self = self.sudo()
        company = None
        if consumer:
            vals["consumer_id"] = consumer if isinstance(consumer, int) else consumer.id
            company = Self.env["fix.api.consumer"].browse(vals["consumer_id"]).company_id
        if endpoint:
            vals["endpoint_id"] = endpoint if isinstance(endpoint, int) else endpoint.id
            company = company or Self.env["fix.api.endpoint"].browse(vals["endpoint_id"]).company_id
        if subscription:
            vals["subscription_id"] = (
                subscription if isinstance(subscription, int) else subscription.id
            )
            company = (
                company
                or Self.env["fix.event.subscription"]
                .browse(vals["subscription_id"])
                .topic_id.company_id
            )
        if connector:
            vals["connector_id"] = connector if isinstance(connector, int) else connector.id
            company = company or Self.env["fix.connector"].browse(vals["connector_id"]).company_id
        if topic_code:
            vals["topic_code"] = topic_code
        if outcome:
            vals["outcome"] = outcome[:200]
        if route:
            vals["route"] = route[:200]
        if company:
            vals["company_id"] = company.id
        return Self.create(vals)
