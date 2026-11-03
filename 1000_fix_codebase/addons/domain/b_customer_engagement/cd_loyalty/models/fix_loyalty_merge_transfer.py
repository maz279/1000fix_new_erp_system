# fix.loyalty.merge.transfer — what a party merge moved between two loyalty
# accounts, so a merge reversal can move it back (A03 audit W1).
#
# When both merged parties hold an account in the same programme, the
# party.merged consumer moves the victim's balance to the survivor as posted
# merge_transfer lines and closes the victim's account. A reversal of the
# merge left all of that in place: the restored party came back with a closed
# wallet and no points. This row remembers the transfer; the
# party.merge_reversed consumer reverses it with posted counter-lines (a
# posted line is never edited) and re-opens the account the merge closed.
#
# Append-only: rows are written only by the consumers, through an in-process
# object token, so a forged row cannot make a reversal pay out points.
import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

_logger = logging.getLogger(__name__)

_KEY = "fix_loyalty_merge_transfer"
_CREATE_TOKEN = object()
_REVERSE_TOKEN = object()
_REVERSAL_FIELDS = frozenset(
    {"reversed", "reversed_at", "reversal_ledger_ids", "points_returned", "reversal_note"}
)


class FixLoyaltyMergeTransfer(models.Model):
    """One victim account merged into one survivor account by one merge."""

    _name = "fix.loyalty.merge.transfer"
    _description = "Loyalty Party-Merge Transfer"
    _order = "id desc"
    _rec_name = "victim_account_id"

    merge_id = fields.Many2one(
        "fix.party.merge", string="Party Merge", required=True, index=True, ondelete="cascade"
    )
    victim_account_id = fields.Many2one(
        "fix.loyalty.account", string="Merged-Away Account", required=True, ondelete="cascade"
    )
    target_account_id = fields.Many2one(
        "fix.loyalty.account", string="Surviving Account", required=True, ondelete="cascade"
    )
    points = fields.Integer(string="Points Moved", readonly=True)
    qualifying_points = fields.Integer(string="Qualifying Points Moved", readonly=True)
    closed_victim = fields.Boolean(string="Closed the Merged-Away Account", readonly=True)
    ledger_ids = fields.Many2many(
        "fix.loyalty.ledger",
        "fix_loyalty_merge_transfer_ledger_rel",
        "transfer_id",
        "ledger_id",
        string="Transfer Lines",
        readonly=True,
    )
    reversed = fields.Boolean(string="Reversal Handled", readonly=True, index=True)
    reversed_at = fields.Datetime(readonly=True)
    points_returned = fields.Integer(readonly=True)
    reversal_ledger_ids = fields.Many2many(
        "fix.loyalty.ledger",
        "fix_loyalty_merge_transfer_reversal_rel",
        "transfer_id",
        "ledger_id",
        string="Counter-Lines",
        readonly=True,
    )
    reversal_note = fields.Char(readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get(_KEY) is not _CREATE_TOKEN:
            raise UserError("Loyalty merge transfers are recorded only by the party merge itself.")
        return super().create(vals_list)

    def write(self, vals):
        if not (self.env.context.get(_KEY) is _REVERSE_TOKEN and set(vals) <= _REVERSAL_FIELDS):
            raise UserError("A loyalty merge transfer is evidence; only its reversal marks it.")
        return super().write(vals)

    def unlink(self):
        raise UserError("A loyalty merge transfer is evidence and cannot be deleted.")

    @api.model
    def _record(self, merge, victim_account, target_account, points, qualifying, lines):
        return (
            self.sudo()
            .with_context(**{_KEY: _CREATE_TOKEN})
            .create(
                {
                    "merge_id": merge.id,
                    "victim_account_id": victim_account.id,
                    "target_account_id": target_account.id,
                    "points": points,
                    "qualifying_points": qualifying,
                    "closed_victim": True,
                    "ledger_ids": [(6, 0, lines.ids)],
                    "company_id": victim_account.company_id.id,
                }
            )
        )

    def _mark(self, note, returned=0, lines=None):
        self.with_context(**{_KEY: _REVERSE_TOKEN}).write(
            {
                "reversed": True,
                "reversed_at": fields.Datetime.now(),
                "points_returned": returned,
                "reversal_ledger_ids": [(6, 0, lines.ids)] if lines else False,
                "reversal_note": note[:250],
            }
        )

    def _reverse(self) -> str:
        """Undo this transfer. Returns what happened, in plain words."""
        self.ensure_one()
        victim, target = self.victim_account_id.sudo(), self.target_account_id.sudo()
        reason = "Party merge #%s reversed" % self.merge_id.id
        notes = []
        if self.closed_victim and victim.state == "closed":
            victim._guarded().write({"state": "active"})
            victim.message_post(body="%s: account re-opened (the merge had closed it)." % reason)
            notes.append("%s re-opened." % victim.name)
        returned, counter = 0, self.env["fix.loyalty.ledger"].sudo()
        if self.points > 0:
            if victim.state != "active" or target.state != "active":
                # A frozen wallet's points are under fraud review; moving them
                # would make them spendable. A steward settles it by adjustment.
                notes.append(
                    "%d points NOT returned: %s is %s and %s is %s. Settle by a "
                    "DOFA-approved adjustment."
                    % (self.points, target.name, target.state, victim.name, victim.state)
                )
                publish(
                    self.env,
                    "loyalty.merge_reversal_blocked",
                    "fix.loyalty.account",
                    victim.id,
                    {"victim_account": victim.name, "survivor_account": target.name},
                )
            else:
                returned, counter = self._return_points(victim, target, reason)
                if returned < self.points:
                    notes.append(
                        "Only %d of %d points returned: the surviving account had spent the "
                        "rest. Settle the shortfall by a DOFA-approved adjustment."
                        % (returned, self.points)
                    )
                    publish(
                        self.env,
                        "loyalty.merge_reversal_shortfall",
                        "fix.loyalty.account",
                        victim.id,
                        {
                            "victim_account": victim.name,
                            "survivor_account": target.name,
                            "points": self.points,
                            "returned": returned,
                        },
                    )
                else:
                    notes.append("%d points returned to %s." % (returned, victim.name))
        if self.qualifying_points:
            back = min(self.qualifying_points, target.qualifying_points_balance or 0)
            if back > 0:
                target.write({"qualifying_points_balance": target.qualifying_points_balance - back})
                victim.award_qualifying_points(back, reason=reason)
                notes.append("%d qualifying points returned." % back)
        outcome = " ".join(notes) or "Nothing to return."
        for account in victim | target:
            account.message_post(body="%s: %s" % (reason, outcome))
        self._mark(outcome, returned, counter)
        return outcome

    def _return_points(self, victim, target, reason):
        """Post the counter-lines: a debit on the survivor and credits on the
        victim that keep the expiry dates the points had. Returns
        (points returned, the posted lines)."""
        take = min(self.points, max(target.points_balance, 0))
        Ledger = self.env["fix.loyalty.ledger"].sudo()
        if take <= 0:
            return 0, Ledger
        allocations, left = [], take
        credits = self.ledger_ids.filtered(
            lambda line: line.account_id == target and line.points > 0
        )
        for line in credits.sorted("id"):
            if left <= 0:
                break
            part = min(line.points, left)
            allocations.append((part, line.expiry_date))
            left -= part
        if left > 0:
            allocations.append((left, False))
        debit = Ledger.create(
            {
                "account_id": target.id,
                "transaction_type": "merge_transfer",
                "points": -take,
                "company_id": target.company_id.id,
                "notes": "%s: balance returned to account %s." % (reason, victim.name),
            }
        )
        debit.action_post()
        lines = debit
        for points, expiry in allocations:
            credit = Ledger.create(
                {
                    "account_id": victim.id,
                    "transaction_type": "merge_transfer",
                    "points": points,
                    "expiry_date": expiry,
                    "company_id": victim.company_id.id,
                    "notes": "%s: balance returned from account %s." % (reason, target.name),
                }
            )
            credit.action_post()
            lines |= credit
        return take, lines


class FixLoyaltyAccountMergeReversal(models.Model):
    _inherit = "fix.loyalty.account"

    @api.model
    def consume_party_merge_reversed(self, event: dict) -> dict:
        """R8 consumer of party.merge_reversed: undo the loyalty side of the
        merge (A03 audit W1).

        A re-pointed account is restored by cd_party_master's generic
        re-point log consumer. A balance transfer is reversed here: posted
        counter-lines and the victim's account re-opened. Idempotent: a
        handled transfer is marked and never handled again."""
        if not self.env.su:
            raise AccessError("Loyalty event consumers run only from the event relay.")
        payload = (event or {}).get("payload") or {}
        merge = self.env["fix.party.merge"].sudo().browse(int(payload.get("merge_id") or 0))
        merge = merge.exists()
        if not merge or merge.state != "reversed":
            return {"skipped": "no reversed merge"}
        transfers = (
            self.env["fix.loyalty.merge.transfer"]
            .sudo()
            .search([("merge_id", "=", merge.id), ("reversed", "=", False)])
        )
        return {"outcomes": [transfer._reverse() for transfer in transfers]}
