# fix.party.merge — supervised merge as a first-class transaction (M33,
# FR-CPM-028/029/030, T-05/T-06, BRU-CPM-04/05). Automated merge is
# PROHIBITED: only a data steward executes, the executor must not have
# created either record (SOD-15), everything moves inside the transaction,
# the victim is tombstoned (never deleted), a merge event is published for
# downstream re-pointing, and the merge is reversible inside the window.
import json
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixPartyMerge(models.Model):
    """One supervised merge: survivor updated, victim tombstoned, party-owned
    records re-pointed, event published, reversible within the window."""

    _name = "fix.party.merge"
    _description = "Supervised Party Merge"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "requested_at desc, id desc"

    survivor_id = fields.Many2one(
        "res.partner", string="Survivor", required=True, ondelete="cascade", index=True
    )
    victim_id = fields.Many2one(
        "res.partner", string="Victim (tombstoned)", required=True, ondelete="cascade", index=True
    )
    state = fields.Selection(
        [("draft", "Draft"), ("executed", "Executed"), ("reversed", "Reversed")],
        string="State",
        default="draft",
        required=True,
        tracking=True,
    )
    requested_at = fields.Datetime(
        string="Requested At", default=fields.Datetime.now, readonly=True
    )
    executed_by = fields.Many2one("res.users", string="Executed By", readonly=True)
    executed_at = fields.Datetime(string="Executed At", readonly=True)
    reversible_until = fields.Datetime(string="Reversible Until", readonly=True)
    # The audit of what was moved and what was skipped — the reversal map.
    attribute_decisions = fields.Text(
        string="Move Audit (JSON)",
        readonly=True,
        help="Per-model record ids moved victim→survivor and skipped (kept on "
        "survivor already); the reversal walks this map back",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.constrains("survivor_id", "victim_id")
    def _check_distinct(self):
        for merge in self:
            if merge.survivor_id == merge.victim_id:
                raise ValidationError("A party cannot merge into itself")

    def _merge_window_days(self) -> int:
        icp = self.env["ir.config_parameter"].sudo()
        days = int(icp.get_param("fix_party.merge_window_days", "14") or 14)
        return days  # Q-04 (7/14/30) is open with the CTO — 14 is the default

    def action_execute(self):
        """Execute the supervised merge. All activity transfers (BRU-CPM-05):
        nothing is deleted — the victim is tombstoned as 'merged'."""
        for merge in self:
            if merge.state != "draft":
                raise ValidationError("Only a draft merge can be executed")
            survivor, victim = merge.survivor_id, merge.victim_id
            # SOD-15: the steward who executes cannot have created either
            # record (the 24h refinement of the window is an open item).
            creator_ids = {u.id for u in (victim.create_uid | survivor.create_uid) if u}
            if self.env.user.id in creator_ids:
                raise ValidationError(
                    "The steward executing the merge cannot be the creator of "
                    "either record (SOD-15)"
                )
            moves, skips = {}, {}

            # Roles: move to the survivor; a role_type the survivor already
            # holds is dropped on the victim (it is the same role by design).
            victim_roles = victim.role_ids
            keep = victim_roles.filtered(
                lambda r, s=survivor: r.role_type not in s.role_ids.mapped("role_type")
            )
            skips["fix.party.role"] = (victim_roles - keep).ids
            keep.write({"partner_id": survivor.id})
            moves["fix.party.role"] = keep.ids

            # Consent: append-only records move with the party.
            victim_consents = victim.consent_ids
            victim_consents.write({"partner_id": survivor.id})
            moves["fix.consent"] = victim_consents.ids

            # Identity documents: move (the residency references move with them).
            docs = victim.identity_document_ids
            docs.write({"partner_id": survivor.id})
            moves["fix.identity.document"] = docs.ids

            # Hierarchy edges: re-point edges touching the victim, dropping
            # edges that would duplicate the survivor's own (UNIQUE
            # parent/child/relation) or self-loop.
            Hierarchy = self.env["fix.party.hierarchy"]
            edges = Hierarchy.search(
                ["|", ("parent_id", "=", victim.id), ("child_id", "=", victim.id)]
            )
            kept_edges = edges
            for edge in edges:
                new_parent = survivor if edge.parent_id == victim else edge.parent_id
                new_child = survivor if edge.child_id == victim else edge.child_id
                if new_parent == new_child or Hierarchy.search_count(
                    [
                        ("parent_id", "=", new_parent.id),
                        ("child_id", "=", new_child.id),
                        ("relation_type", "=", edge.relation_type),
                        ("id", "!=", edge.id),
                    ]
                ):
                    edges = edges - edge
                    continue
                edge.write({"parent_id": new_parent.id, "child_id": new_child.id})
            skips["fix.party.hierarchy"] = (kept_edges - edges).ids
            moves["fix.party.hierarchy"] = edges.ids

            audit = {
                "moved": moves,
                "skipped": skips,
                "victim_prior_status": victim.party_status,
            }
            victim.write({"party_status": "merged", "active": False})
            merge.write(
                {
                    "state": "executed",
                    "executed_by": self.env.user.id,
                    "executed_at": fields.Datetime.now(),
                    "reversible_until": fields.Datetime.now()
                    + timedelta(days=merge._merge_window_days()),
                    "attribute_decisions": json.dumps(audit),
                }
            )
            from libs.py.fix_events import publish

            publish(
                self.env,
                "party.merged",
                "res.partner",
                survivor.id,
                {
                    "survivor_id": survivor.id,
                    "victim_id": victim.id,
                    # All subscribers re-point their own references (§12.3)
                    "mandated_consumers": "all",
                },
            )
        return True

    def action_reverse(self):
        """Reverse inside the window: restore the victim and move the
        partner-owned records back. Hierarchy edges are NOT auto-restored
        (the UNIQUE parent/child/relation rule makes verbatim restore
        unsafe) — the steward re-links, honestly recorded. Downstream
        re-points unwind on party.merge_reversed."""
        for merge in self:
            if merge.state != "executed":
                raise ValidationError("Only an executed merge can be reversed")
            if merge.reversible_until and fields.Datetime.now() > merge.reversible_until:
                raise ValidationError("The reversal window closed on %s" % merge.reversible_until)
            audit = json.loads(merge.attribute_decisions or "{}")
            survivor, victim = merge.survivor_id, merge.victim_id
            for model_name, ids in (audit.get("moved") or {}).items():
                if not ids or model_name == "fix.party.hierarchy":
                    continue  # hierarchy has no partner_id — steward re-links
                self.env[model_name].browse(ids).exists().write({"partner_id": victim.id})
            victim.with_context(skip_party_status_guard=True).write(
                {"party_status": audit.get("victim_prior_status") or "active", "active": True}
            )
            merge.state = "reversed"
            from libs.py.fix_events import publish

            publish(
                self.env,
                "party.merge_reversed",
                "res.partner",
                survivor.id,
                {"survivor_id": survivor.id, "restored_id": victim.id},
            )
        return True
