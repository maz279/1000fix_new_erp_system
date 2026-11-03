# fix.party.duplicate — duplicate-detection candidates for stewardship
# (M33, FR-CPM-026/027, BRU-CPM-03/04). Detection (entry-time + batch) is
# scored deterministically + probabilistically by the engine that consumes
# fix.dedup.rule; this model is the QUEUE a data steward works — a
# confirmed candidate opens a supervised merge; nothing merges by itself.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .fix_party_security import STEWARD_GROUP, require_group

_OPEN_STATES = ("new", "reviewed", "confirmed")


class FixPartyDuplicate(models.Model):
    """A scored candidate pair awaiting data-steward review."""

    _name = "fix.party.duplicate"
    _description = "Duplicate Candidate"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "score desc, id desc"

    def _fix_guarded_fields(self) -> set:
        # The steward decision is the actions' to record (A03 audit M33-6).
        return super()._fix_guarded_fields() | {"state", "reviewed_by"}

    party_a = fields.Many2one(
        "res.partner", string="Party A", required=True, ondelete="cascade", index=True
    )
    party_b = fields.Many2one(
        "res.partner", string="Party B", required=True, ondelete="cascade", index=True
    )
    score = fields.Float(
        string="Match Score", help="0–100; explainable score (T-03) — the factors below say why"
    )
    factors = fields.Text(
        string="Match Factors",
        help="JSON of factor contributions — an unexplainable score is not actionable",
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("reviewed", "Under Review"),
            ("confirmed", "Confirmed Duplicate"),
            ("dismissed", "Dismissed (not a duplicate)"),
            ("merged", "Merged"),
        ],
        string="State",
        default="new",
        required=True,
        tracking=True,
    )
    reviewed_by = fields.Many2one("res.users", string="Reviewed By", readonly=True)
    decision = fields.Char(string="Decision Note")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.constrains("party_a", "party_b")
    def _check_distinct(self):
        for cand in self:
            if cand.party_a == cand.party_b:
                raise ValidationError("A party cannot be a duplicate of itself")

    def action_review(self):
        require_group(self.env, STEWARD_GROUP, "Reviewing a duplicate candidate")
        for cand in self:
            if cand.state != "new":
                raise ValidationError("Only a new candidate can be put under review")
            cand._guarded().write({"state": "reviewed", "reviewed_by": self.env.user.id})
        return True

    def action_confirm(self):
        """Confirm the duplicate and open the supervised merge draft — the
        merge itself is a SEPARATE steward action (BRU-CPM-04)."""
        require_group(self.env, STEWARD_GROUP, "Confirming a duplicate")
        Merge = self.env["fix.party.merge"]
        for cand in self:
            if cand.state not in ("reviewed", "new"):
                raise ValidationError("Only a reviewed candidate can be confirmed")
            cand._guarded().write({"state": "confirmed", "reviewed_by": self.env.user.id})
            existing = Merge.search(
                [
                    ("victim_id", "in", (cand.party_a | cand.party_b).ids),
                    ("state", "!=", "reversed"),
                ],
                limit=1,
            )
            if not existing:
                # Older/lower-quality record becomes the victim by default;
                # the steward can swap before executing the merge.
                victim, survivor = cand.party_a, cand.party_b
                if cand.party_a.create_date and cand.party_b.create_date:
                    victim, survivor = (
                        (cand.party_a, cand.party_b)
                        if cand.party_a.create_date <= cand.party_b.create_date
                        else (cand.party_b, cand.party_a)
                    )
                Merge.create(
                    {
                        "survivor_id": survivor.id,
                        "victim_id": victim.id,
                        "company_id": cand.company_id.id,
                    }
                )
        return True

    def action_dismiss(self, reason=None):
        """Dismiss with a reason — a dismissed pair is recorded and never
        silently re-raised (spec §8.3)."""
        if not reason:
            raise ValidationError("A dismissal needs its reason (BRU-CPM-03)")
        require_group(self.env, STEWARD_GROUP, "Dismissing a duplicate")
        for cand in self:
            if cand.state not in _OPEN_STATES:
                raise ValidationError("Only an open candidate can be dismissed")
            cand._guarded().write(
                {"state": "dismissed", "reviewed_by": self.env.user.id, "decision": reason}
            )
        return True

    @api.model
    def consume_party_merged(self, event):
        """R8 consumer: close the queue behind a merge (A03 audit M33-8).

        The merged pair becomes 'merged' (it stayed 'confirmed' forever).
        Other open candidates naming the victim are re-pointed at the
        survivor, or closed when that would pair the survivor with itself or
        repeat a pair already queued. Idempotent: a second delivery finds no
        open candidate naming the victim. Re-points are logged so a merge
        reversal moves them back (A03 audit W1)."""
        Log = self.env["fix.party.repoint.log"]
        merge = Log._event_merge(event)
        if not merge:
            return 0
        survivor, victim = merge.survivor_id, merge.victim_id
        Cand = self.sudo()._guarded()
        touched = 0
        for cand in Cand.search(
            [
                ("state", "in", _OPEN_STATES),
                "|",
                ("party_a", "=", victim.id),
                ("party_b", "=", victim.id),
            ]
        ):
            other = cand.party_b if cand.party_a == victim else cand.party_a
            note = "Closed by merge #%s into %s" % (
                (event.get("payload") or {}).get("merge_id") or "?",
                survivor.display_name,
            )
            duplicate_pair = Cand.search_count(
                [
                    ("id", "!=", cand.id),
                    ("state", "in", _OPEN_STATES),
                    "|",
                    "&",
                    ("party_a", "=", survivor.id),
                    ("party_b", "=", other.id),
                    "&",
                    ("party_a", "=", other.id),
                    ("party_b", "=", survivor.id),
                ]
            )
            if other == survivor or duplicate_pair:
                cand.write({"state": "merged", "decision": note})
            elif cand.party_a == victim:
                Log.repoint(merge, cand, "party_a", victim, survivor)
            else:
                Log.repoint(merge, cand, "party_b", victim, survivor)
            touched += 1
        return touched
