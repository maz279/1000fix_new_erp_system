# fix_bridge_exception — A07 P1 (2026-11-04): a hand-off the bridge could not
# complete on its own, and the shared helpers every consumer uses.
#
# A consumer that fails raises, and the relay retries it and dead-letters it
# after three attempts (fix_event_relay.py). That is right for a defect, and
# wrong for a hand-off that only lacks a fact a person must supply: an injury
# case whose worker nobody named, a lease recorded with no rent. Those land
# here, visible to the target module's role, with the event kept so Retry runs
# the same consumer again once the fact is supplied. Nothing is invented to
# make the hand-off go through.
import json
import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)

PARAM_PREFIX = "cd_asset_finance_hse_bridge."
ACCOUNTANT = "account.group_account_user"
ACCOUNTING_MANAGER = "account.group_account_manager"
HSE_OFFICER = "cd_hse.group_hse_officer"


def has_role(env, *xmlids) -> bool:
    """Superuser code is trusted; a user needs one of the roles."""
    if env.su:
        return True
    return any(env.user.has_group(x) for x in xmlids)


def require_role(env, xmlids, what):
    if has_role(env, *xmlids):
        return
    names = []
    for xmlid in xmlids:
        group = env.ref(xmlid, raise_if_not_found=False)
        names.append(group.sudo().name if group else xmlid)
    raise AccessError("%s needs the %s role." % (what, " or ".join(names)))


def event_source(env, event, model=None):
    """The record an event is about (its aggregate), as superuser; empty when
    the record is gone or the model is not installed."""
    model = model or event.get("aggregate")
    if not model or model not in env:
        return None
    rid = event.get("aggregate_id")
    return env[model].sudo().browse(int(rid)).exists() if rid else env[model].sudo().browse()


def noted(record, text) -> bool:
    """True when `text` is already in the record's chatter: a note posted by
    a consumer is posted once, however often the event is redelivered."""
    return any(text in (body or "") for body in record.sudo().message_ids.mapped("body"))


def source_key(prefix, record):
    return "%s:%s:%s" % (prefix, record._name, record.id)


def param_float(env, key, default=0.0) -> float:
    raw = env["ir.config_parameter"].sudo().get_param(PARAM_PREFIX + key)
    try:
        return float(raw) if raw not in (None, False, "") else default
    except ValueError:
        return default


def run_hook(env, what, fn, *args):
    """Run a bridge side effect from inside another module's write/create.

    The user's own transaction must never fail because a hand-off did: the
    hand-off runs in a savepoint as superuser, and a failure is logged as an
    open bridge exception instead of rolling the user's change back."""
    try:
        with env.cr.savepoint():
            return fn(*args)
    except Exception as exc:  # a hand-off failure must not undo the user's work
        _logger.warning("bridge hook %s failed: %s", what, exc)
        record = args[0][:1] if args and isinstance(args[0], models.BaseModel) else None
        with env.cr.savepoint():
            env["fix.bridge.exception"].sudo().record(
                route="hook",
                key="hook:%s:%s" % (what, source_key("src", record) if record else ""),
                message="%s failed: %s: %s" % (what, type(exc).__name__, exc),
                source=record,
                role=ACCOUNTANT,
            )
        return None


class FixBridgeException(models.Model):
    _name = "fix.bridge.exception"
    _description = "Asset Hand-Off Exception"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "state, create_date desc, id desc"

    _key_unique = models.Constraint("UNIQUE (key)", "One exception row per hand-off.")

    name = fields.Char(required=True, readonly=True)
    key = fields.Char(required=True, readonly=True, index=True, copy=False)
    route = fields.Selection(
        [
            ("m49_asset", "M49 Asset Request"),
            ("m49_lease", "M49 IFRS 16 Lease"),
            ("m52_cost", "M52 Cost Entry"),
            ("m59_case", "M59 HSE Case"),
            ("m59_hazard", "M59 Hazard"),
            ("m60_risk", "M60 Risk Entry"),
            ("m09_claim", "M09 Warranty Claim"),
            ("hook", "Bridge Hook"),
        ],
        required=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    event_type = fields.Char(readonly=True)
    event_json = fields.Text(string="Event", readonly=True)
    consumer_model = fields.Char(readonly=True)
    consumer_method = fields.Char(readonly=True)
    source_model = fields.Char(readonly=True)
    source_res_id = fields.Integer(readonly=True)
    source_ref = fields.Char(string="Source", readonly=True)
    message = fields.Text(string="What Is Needed", readonly=True)
    role_xmlid = fields.Char(string="Resolved By (Role)", readonly=True)
    # the one fact a person supplies for the M59 route: the worker involved
    employee_id = fields.Many2one(
        "hr.employee",
        string="Worker Involved",
        help="M59: the injured worker or the reporter, when the source named neither.",
    )
    state = fields.Selection(
        [("open", "Open"), ("resolved", "Resolved")], default="open", required=True, index=True
    )
    attempts = fields.Integer(readonly=True, default=1)
    resolved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    resolved_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "key",
            "route",
            "event_type",
            "event_json",
            "consumer_model",
            "consumer_method",
            "source_model",
            "source_res_id",
            "source_ref",
            "message",
            "role_xmlid",
            "state",
            "attempts",
            "resolved_by_id",
            "resolved_at",
            "company_id",
        }

    def unlink(self):
        if not self.env.su:
            raise UserError("A hand-off exception is part of the record: resolve it instead.")
        return super().unlink()

    # ---- the consumers' side -------------------------------------------------
    @api.model
    def record(
        self,
        route,
        key,
        message,
        event=None,
        source=None,
        consumer=None,
        role=ACCOUNTANT,
        company=None,
    ):
        """Open (or refresh) the exception for `key`. Idempotent."""
        Exc = self.sudo()._guarded()
        source = source[:1] if source else None
        company = company or (source.company_id if source and "company_id" in source else None)
        vals = {
            "message": message,
            "event_type": (event or {}).get("event_type") or False,
            "event_json": json.dumps(event, default=str) if event else False,
            "consumer_model": consumer[0] if consumer else False,
            "consumer_method": consumer[1] if consumer else False,
            "role_xmlid": role,
        }
        row = Exc.search([("key", "=", key)], limit=1)
        if row:
            vals.update({"state": "open", "attempts": row.attempts + 1})
            row.write(vals)
            return row
        vals.update(
            {
                "name": "%s: %s"
                % (
                    dict(self._fields["route"].selection).get(route, route),
                    source.display_name if source else key,
                ),
                "key": key,
                "route": route,
                "company_id": (company or self.env.company).id,
                "operating_unit_id": source.operating_unit_id.id
                if source and "operating_unit_id" in source and source.operating_unit_id
                else False,
                "source_model": source._name if source else False,
                "source_res_id": source.id if source else 0,
                "source_ref": source.display_name if source else False,
            }
        )
        return Exc.create(vals)

    @api.model
    def resolve(self, key, how):
        rows = self.sudo().search([("key", "=", key), ("state", "=", "open")])
        for row in rows:
            row._guarded().write(
                {
                    "state": "resolved",
                    "resolved_by_id": self.env.uid,
                    "resolved_at": fields.Datetime.now(),
                }
            )
            row.message_post(body="Resolved: %s" % how)
        return rows

    @api.model
    def hint(self, key):
        """The open exception for `key`, read by a consumer on retry."""
        return self.sudo().search([("key", "=", key)], limit=1)

    # ---- the person's side ---------------------------------------------------
    def action_retry(self):
        """Run the consumer again on the kept event, after the missing fact
        was supplied. The target module's role retries; the consumer itself
        decides whether it now goes through."""
        for row in self:
            if row.state != "open":
                raise UserError("%s is already resolved." % row.name)
            require_role(self.env, [row.role_xmlid or ACCOUNTANT], "Retrying %s" % row.name)
            if not (row.consumer_model and row.consumer_method and row.event_json):
                raise UserError("%s has no consumer to retry: resolve it by hand." % row.name)
            method = getattr(self.env[row.consumer_model].sudo(), row.consumer_method, None)
            if not callable(method) or not row.consumer_method.startswith("consume_"):
                raise UserError(
                    "%s.%s cannot be retried." % (row.consumer_model, row.consumer_method)
                )
            method(json.loads(row.event_json))
        return True

    def action_resolve(self, note=None):
        """Close by hand (the hand-off was done another way). Needs a note."""
        for row in self:
            require_role(self.env, [row.role_xmlid or ACCOUNTANT], "Resolving %s" % row.name)
            text = (note or "").strip()
            if not text:
                raise UserError("Say how %s was resolved." % row.name)
            if row.state != "open":
                raise UserError("%s is already resolved." % row.name)
            row.sudo()._guarded().write(
                {
                    "state": "resolved",
                    "resolved_by_id": self.env.uid,
                    "resolved_at": fields.Datetime.now(),
                }
            )
            row.message_post(body="Resolved by hand: %s" % text)
        return True
