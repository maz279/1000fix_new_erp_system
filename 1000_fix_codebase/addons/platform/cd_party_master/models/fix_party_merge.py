# fix.party.merge — supervised merge as a first-class transaction (M33,
# FR-CPM-028/029/030, T-05/T-06, BRU-CPM-04/05). Automated merge is
# PROHIBITED: only a data steward executes, the executor must not have
# created either record (SOD-15), everything moves inside the transaction,
# the victim is tombstoned (never deleted), a merge event is published for
# downstream re-pointing, and the merge is reversible inside the window.
import json
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_party_security import STEWARD_GROUP, require_group


class FixPartyMerge(models.Model):
    """One supervised merge: survivor updated, victim tombstoned, party-owned
    records re-pointed, event published, reversible within the window."""

    _name = "fix.party.merge"
    _description = "Supervised Party Merge"
    # fix.approvable.mixin already carries fix.guarded.mixin.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]

    # A03 audit W4 (R7): execution is a routed M63 decision. A steward who
    # did not create either party, and did not request the merge, decides it
    # from the approval inbox; pressing Execute on the record is refused.
    _approval_domain = "party_merge"
    _approval_apply_method = "action_execute"
    _approval_group = STEWARD_GROUP
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        # state='executed' with a forged executor moved nothing (A03 audit).
        return super()._fix_guarded_fields() | {
            "state",
            "executed_by",
            "executed_at",
            "reversible_until",
            "attribute_decisions",
        }

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

    def _fix_form_locked_fields(self) -> set:
        # An executed or reversed merge is FOR one pair (A03 audit W4).
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            return locked | {"survivor_id", "victim_id"}
        return locked

    def write(self, vals):
        # A03 audit W4: the steward approves one pair. Re-pointing a merge
        # after it was requested would have them execute a different one.
        voided = self.browse()
        if {"survivor_id", "victim_id"} & set(vals) and not self._fix_guard_open():
            if any(merge.state != "draft" for merge in self):
                raise UserError(
                    "An executed or reversed merge cannot be moved to other parties. "
                    "Raise a new merge instead."
                )
            voided = self.filtered(lambda m: m.approval_state in ("pending", "approved"))
        result = super().write(vals)
        if voided:
            voided._approval_void("the merge pair changed after approval was requested")
        return result

    # ---- engine hooks (A03 audit W4) -------------------------------------
    def _approval_needed(self) -> bool:
        return self.state == "draft"

    def _approval_excluded(self):
        # SOD-15 at routing time: the creators of either party are never sent
        # the decision (the engine already excludes requester and creator).
        return (
            super()._approval_excluded() | self.survivor_id.create_uid | self.victim_id.create_uid
        ).sudo()

    def _merge_system_trusted(self) -> bool:
        """Superuser code with no deciding task (crons, data loading).

        Not an inbox decision: the engine hands the record to action_execute
        through its sudo request, so env.su is true there too, and the
        steward and SOD-15 checks must still bind the approver."""
        return self.env.su and not self._approval_task()

    def _merge_window_days(self) -> int:
        icp = self.env["ir.config_parameter"].sudo()
        days = int(icp.get_param("fix_party.merge_window_days", "14") or 14)
        return days  # Q-04 (7/14/30) is open with the CTO — 14 is the default

    def action_execute(self):
        """Execute the supervised merge. All activity transfers (BRU-CPM-05):
        nothing is deleted — the victim is tombstoned as 'merged'."""
        # Routed (A03 audit W4): only an inbox task assigned to a steward
        # carries the merge through; a direct press is refused here.
        self._approval_assert_routed()
        for merge in self:
            if merge.state != "draft":
                raise ValidationError("Only a draft merge can be executed")
            # "Only a data steward executes" (module header) had no group
            # behind it: any user with Contact write could merge (A03 audit
            # M33-6). A delegate decides on the absent steward's authority.
            authority = merge._approval_authority_user()
            if not merge._merge_system_trusted() and not authority.has_group(STEWARD_GROUP):
                raise UserError(
                    "Executing a party merge needs the 'Party Data Steward' group, which "
                    "%s does not hold." % authority.name
                )
            survivor, victim = merge.survivor_id, merge.victim_id
            # SOD-15: the steward who executes cannot have created either
            # record (the 24h refinement of the window is an open item).
            # The acting users are the approver and whom they act for.
            acting = merge._approval_acting_users()
            creator_ids = {u.id for u in (victim.create_uid | survivor.create_uid) if u}
            if set(acting.ids) & creator_ids:
                raise ValidationError(
                    "The steward executing the merge cannot be the creator of "
                    "either record (SOD-15)"
                )
            requester = merge.approval_request_id.requested_by_id
            if requester and requester in acting and not merge._merge_system_trusted():
                raise ValidationError(
                    "Segregation of duties: you requested this merge, so another data "
                    "steward must execute it."
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
            victim._guarded().write({"party_status": "merged", "active": False})
            merge._guarded().write(
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
                    # Consumers key on these two; never rename them (the
                    # loyalty and service-order consumers read them).
                    "survivor_id": survivor.id,
                    "victim_id": victim.id,
                    # All subscribers re-point their own references (§12.3)
                    "mandated_consumers": "all",
                    # Added for the R8 consumers: which merge, and when.
                    "merge_id": merge.id,
                    "executed_at": fields.Datetime.to_string(merge.executed_at),
                },
            )
        return True

    def action_reverse(self):
        """Reverse inside the window: restore the victim and move the
        partner-owned records back. Hierarchy edges are NOT auto-restored
        (the UNIQUE parent/child/relation rule makes verbatim restore
        unsafe) — the steward re-links, honestly recorded. Downstream
        re-points unwind on party.merge_reversed."""
        require_group(self.env, STEWARD_GROUP, "Reversing a party merge")
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
            # _guarded(), not a context flag: a JSON-RPC caller can set any
            # context key, so a flag would let anyone un-tombstone a party.
            victim._guarded().write(
                {"party_status": audit.get("victim_prior_status") or "active", "active": True}
            )
            merge._guarded().write({"state": "reversed"})
            from libs.py.fix_events import publish

            publish(
                self.env,
                "party.merge_reversed",
                "res.partner",
                survivor.id,
                {"survivor_id": survivor.id, "restored_id": victim.id, "merge_id": merge.id},
            )
        return True
