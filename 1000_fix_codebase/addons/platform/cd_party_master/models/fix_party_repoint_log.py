# fix.party.repoint.log — every reference a party merge moved, so a reversal
# can move it back (A03 audit M33-5, W1).
#
# A supervised merge publishes party.merged and each module re-points its own
# references to the survivor. Before this log, nothing remembered what moved:
# fix.party.merge.action_reverse restored the kernel's own records, but a
# service order, lead or complaint re-pointed downstream stayed on the
# survivor for good, and the reversal unwound nothing.
#
# Every party.merged consumer re-points through `repoint()`, which writes the
# field and appends one row per record. The generic party.merge_reversed
# consumer below walks those rows back: a row whose record still points at
# the survivor is restored to the victim; a row whose record has since been
# moved again by someone else is left alone and noted.
#
# The log is append-only evidence. Only `repoint()` creates rows and only the
# reversal sets the reversal fields, each through an in-process object token
# (a JSON-RPC caller cannot put an object in the context). A forged row would
# otherwise let a reversal move any record onto the victim.
import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)

_LOG_KEY = "fix_party_repoint_log"
_CREATE_TOKEN = object()
_REVERSE_TOKEN = object()
_REVERSAL_FIELDS = frozenset({"reversed", "reversed_at", "reversal_outcome", "reversal_note"})


class FixPartyRepointLog(models.Model):
    """One reference moved victim -> survivor by one merge."""

    _name = "fix.party.repoint.log"
    _description = "Party Merge Re-point Log"
    _order = "id"
    _rec_name = "res_model"

    merge_id = fields.Many2one(
        "fix.party.merge", string="Merge", required=True, index=True, ondelete="cascade"
    )
    res_model = fields.Char(string="Record Model", required=True, index=True, readonly=True)
    res_id = fields.Integer(string="Record ID", required=True, index=True, readonly=True)
    field_name = fields.Char(string="Field", required=True, readonly=True)
    from_partner_id = fields.Many2one(
        "res.partner", string="From (Victim)", required=True, ondelete="cascade", readonly=True
    )
    to_partner_id = fields.Many2one(
        "res.partner", string="To (Survivor)", required=True, ondelete="cascade", readonly=True
    )
    at = fields.Datetime(string="Re-pointed At", required=True, readonly=True)
    reversed = fields.Boolean(string="Reversal Handled", readonly=True, index=True)
    reversed_at = fields.Datetime(readonly=True)
    reversal_outcome = fields.Selection(
        [
            ("restored", "Restored to the victim"),
            ("left", "Left alone: re-pointed elsewhere since"),
            ("gone", "Record no longer exists"),
            ("failed", "Restore failed (will retry)"),
        ],
        readonly=True,
    )
    reversal_note = fields.Char(readonly=True)

    # ---- append-only ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get(_LOG_KEY) is not _CREATE_TOKEN:
            raise UserError("The party merge re-point log is written only by the merge consumers.")
        return super().create(vals_list)

    def write(self, vals):
        if not (self.env.context.get(_LOG_KEY) is _REVERSE_TOKEN and set(vals) <= _REVERSAL_FIELDS):
            raise UserError(
                "The party merge re-point log is append-only evidence; only a merge "
                "reversal marks its rows."
            )
        return super().write(vals)

    def unlink(self):
        raise UserError("The party merge re-point log is append-only evidence.")

    # ---- the event behind a consumer call -----------------------------------
    @api.model
    def _event_merge(self, event):
        """The executed merge a party.merged event is about, or an empty set.

        The merge record is the authority, not the payload: a consumer is a
        public method, and a hand-made event naming a real tombstone and any
        "survivor" would otherwise move the tombstone's records to that party.
        A merge that no longer stands (reversed before delivery) yields
        nothing, so a late delivery never re-points onto a restored party."""
        payload = (event or {}).get("payload") or {}
        Merge = self.env["fix.party.merge"].sudo().with_context(active_test=False)
        survivor_id = int(payload.get("survivor_id") or 0)
        victim_id = int(payload.get("victim_id") or 0)
        merge = Merge.browse(int(payload.get("merge_id") or 0)).exists()
        if not merge and survivor_id and victim_id:
            # Events published before the payload carried merge_id.
            merge = Merge.search(
                [
                    ("survivor_id", "=", survivor_id),
                    ("victim_id", "=", victim_id),
                    ("state", "=", "executed"),
                ],
                order="id desc",
                limit=1,
            )
        if (
            not merge
            or merge.state != "executed"
            or merge.survivor_id.id != survivor_id
            or merge.victim_id.id != victim_id
            or merge.victim_id.party_status != "merged"
        ):
            return Merge.browse()
        return merge

    # ---- the helper every consumer uses -------------------------------------
    @api.private
    @api.model
    def repoint(self, merge, records, field, victim, survivor):
        """Point `field` of `records` from `victim` to `survivor` and log each.

        Only records still on the victim move, so a second delivery is a
        no-op. The write is a system transition (sudo, plus the field guard's
        token where the model has one): the relay runs the consumers as the
        superuser. Returns the records that moved."""
        records = records.sudo().with_context(active_test=False)
        moving = records.filtered(lambda r: r[field].id == victim.id)
        if not moving:
            return moving
        writer = moving._guarded() if hasattr(moving, "_guarded") else moving
        writer.write({field: survivor.id})
        if merge:
            now = fields.Datetime.now()
            self.sudo().with_context(**{_LOG_KEY: _CREATE_TOKEN}).create(
                [
                    {
                        "merge_id": merge.id,
                        "res_model": rec._name,
                        "res_id": rec.id,
                        "field_name": field,
                        "from_partner_id": victim.id,
                        "to_partner_id": survivor.id,
                        "at": now,
                    }
                    for rec in moving
                ]
            )
        _logger.info(
            "party.merged: %d %s.%s re-pointed %s -> %s (merge %s)",
            len(moving),
            moving._name,
            field,
            victim.id,
            survivor.id,
            merge.id if merge else "?",
        )
        return moving

    # ---- party.merge_reversed (R8) -------------------------------------------
    def _reversal_mark(self, outcome, note):
        self.with_context(**{_LOG_KEY: _REVERSE_TOKEN}).write(
            {
                "reversed": outcome != "failed",
                "reversed_at": fields.Datetime.now(),
                "reversal_outcome": outcome,
                "reversal_note": (note or "")[:250] or False,
            }
        )

    @api.model
    def consume_party_merge_reversed(self, event):
        """Restore every logged re-point of the reversed merge.

        A row whose record still points at the survivor goes back to the
        victim. A row whose record now points somewhere else was changed by
        someone after the merge: it is left alone and noted, never
        overwritten. Idempotent: a handled row is never handled again; a row
        whose restore failed stays open so a redelivery retries it."""
        if not self.env.su:
            # A public method: only the relay (superuser) applies an event.
            raise AccessError("Party merge consumers run only from the event relay.")
        payload = (event or {}).get("payload") or {}
        merge = self.env["fix.party.merge"].sudo().browse(int(payload.get("merge_id") or 0))
        merge = merge.exists()
        if not merge or merge.state != "reversed":
            return {"restored": 0, "left": 0, "reason": "no reversed merge"}
        counts = {"restored": 0, "left": 0, "gone": 0, "failed": 0}
        for row in self.sudo().search([("merge_id", "=", merge.id), ("reversed", "=", False)]):
            outcome, note = row._reversal_restore()
            row._reversal_mark(outcome, note)
            counts[outcome] += 1
        if any(counts.values()):
            merge.message_post(
                body="Merge reversal unwound the downstream re-points: %(restored)d "
                "restored, %(left)d left alone (moved since), %(gone)d no longer exist, "
                "%(failed)d failed." % counts
            )
        return counts

    def _reversal_restore(self):
        """(outcome, note) for this row; restores the record when it may."""
        self.ensure_one()
        if self.res_model not in self.env:
            return "gone", "model %s is not installed" % self.res_model
        record = (
            self.env[self.res_model].sudo().with_context(active_test=False).browse(self.res_id)
        ).exists()
        if not record or self.field_name not in record._fields:
            return "gone", "the record no longer exists"
        current = record[self.field_name]
        if current.id != self.to_partner_id.id:
            return "left", "now points at %s (#%s); changed after the merge, left alone" % (
                current.display_name or "nobody",
                current.id or "-",
            )
        try:
            with self.env.cr.savepoint():
                writer = record._guarded() if hasattr(record, "_guarded") else record
                writer.write({self.field_name: self.from_partner_id.id})
        except Exception as exc:  # one record must not stop the rest of the reversal
            _logger.warning(
                "party.merge_reversed: %s#%s not restored: %s", record._name, record.id, exc
            )
            return "failed", "%s: %s" % (type(exc).__name__, exc)
        return "restored", ""
