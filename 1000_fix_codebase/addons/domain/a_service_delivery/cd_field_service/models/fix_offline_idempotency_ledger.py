"""fix_offline_idempotency_ledger — Server-side idempotency ledger (DI-05, AR-010 §4).

Tracks all executed client offline commands keyed by client-generated UUID.
Ensures exactly-once execution semantics across network retries and unstable connections.
"""

import json
from datetime import UTC, datetime

from odoo import api, fields, models


def _client_timestamp(value):
    """The journal's client timestamp as a naive UTC datetime (the Datetime field
    format), or None when absent or unparseable. The client sends ISO 8601
    ("2026-10-17T08:00:00Z"); written as-is it made the ledger write raise - which
    rolled back the command being recorded and REJECTED it. The timestamp is
    informational and never decides a command's fate."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo:
        parsed = parsed.astimezone(UTC).replace(tzinfo=None)
    return parsed


def _record_id(value):
    """A client-supplied record id as an int (0 when absent or not an integer)."""
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


class FixOfflineIdempotencyLedger(models.Model):
    _name = "fix.offline.idempotency.ledger"
    _description = "Offline Command Idempotency Ledger"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )

    command_id = fields.Char(
        string="Command UUID",
        required=True,
        index=True,
        copy=False,
        help="Client-generated unique idempotency key (UUIDv4)",
    )
    technician_id = fields.Many2one(
        "hr.employee",
        string="Technician",
        index=True,
        help="Field technician who issued the command",
    )
    device_id = fields.Char(
        string="Device ID", index=True, help="Device hardware identifier / installation UUID"
    )
    model = fields.Char(
        string="Target Model",
        required=True,
        index=True,
        help="Target Odoo model name, e.g. fix.field.order or fix.work.order",
    )
    record_id = fields.Integer(
        string="Record ID", index=True, help="Target record ID in target model"
    )
    operation = fields.Char(
        string="Operation",
        required=True,
        help="Command operation name (e.g. clock_in, start_order, complete_order, consume_part)",
    )
    payload_hash = fields.Char(
        string="Payload SHA-256",
        index=True,
        help="SHA-256 digest of original command payload for tamper detection",
    )
    status = fields.Selection(
        [
            ("applied", "Applied"),
            ("rejected", "Rejected"),
            ("conflict_applied", "Applied with Conflict Delta"),
        ],
        string="Execution Status",
        required=True,
        default="applied",
    )
    response_payload = fields.Text(
        string="Response Payload (JSON)",
        help="Cached JSON response returned on duplicate / retry execution",
    )
    conflict_reason = fields.Text(string="Conflict / Rejection Reason")
    client_created_at = fields.Datetime(
        string="Client Timestamp",
        help="Timestamp when command was committed to local offline journal",
    )
    applied_at = fields.Datetime(
        string="Server Applied At", default=fields.Datetime.now, required=True
    )

    # Odoo 19 ignores the legacy ``_sql_constraints`` list (it only logs a warning),
    # so the DI-05 invariant was never in the database: two concurrent syncs of the
    # same command could both execute. models.Constraint creates it.
    _command_id_uniq = models.Constraint(
        "UNIQUE (command_id)",
        "Offline command UUID must be unique (DI-05 idempotency invariant).",
    )

    @api.model
    def get_cached_result(self, command_id):
        """Check if command has already been executed.
        Returns dict or None.
        """
        ledger_entry = self.search([("command_id", "=", command_id)], limit=1)
        if not ledger_entry:
            return None

        parsed = {}
        if ledger_entry.response_payload:
            try:
                parsed = json.loads(ledger_entry.response_payload)
            except Exception:
                parsed = {"raw": ledger_entry.response_payload}

        return {
            "status": ledger_entry.status,
            "response": parsed,
            "conflict_reason": ledger_entry.conflict_reason,
            "applied_at": str(ledger_entry.applied_at or ""),
            "idempotent_replay": True,
        }

    @api.model
    def record_execution(
        self,
        command_id,
        technician_id,
        device_id,
        model,
        record_id,
        operation,
        payload_hash,
        status,
        response_dict,
        conflict_reason=None,
        client_created_at=None,
    ):
        """Record command execution in the idempotency ledger."""
        return self.create(
            {
                "command_id": command_id,
                "technician_id": technician_id,
                "device_id": device_id,
                "model": model,
                "record_id": _record_id(record_id),
                "operation": operation,
                "payload_hash": payload_hash,
                "status": status,
                "response_payload": json.dumps(response_dict, default=str),
                "conflict_reason": conflict_reason,
                "client_created_at": _client_timestamp(client_created_at),
                "applied_at": fields.Datetime.now(),
            }
        )
