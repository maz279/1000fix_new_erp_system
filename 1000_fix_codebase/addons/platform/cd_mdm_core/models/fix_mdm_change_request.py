# fix.mdm.change.request — the master-data change-request model (P03-M07-T01).
# MV-04: MDM governance moved to W1 because it governs the W1 kernels.
#
# A12 audit M64 (2026-11-04) P1-2: this model was a register BESIDE the data —
# approval changed nothing, the proposer approved himself, every workflow
# field was writable, and the target was never validated. It is now the gate
# IN FRONT of the data:
#   draft --action_submit--> submitted --M63 routed--> approved --action_apply-->
#   implemented (the proposed values are written to the target under sudo,
#   inside a savepoint, after re-validation).
# The decision is routed through fix.approvable.mixin to holders of the MDM
# Domain Steward group, never the proposer or the record's creator.
import json
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)

STEWARD_GROUP = "cd_entity_config.group_mdm_domain_steward"

CHANGE_REQUEST_STATES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("under_review", "Under Review"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("implemented", "Implemented"),
    ("cancelled", "Cancelled"),
]
TERMINAL_STATES = ("rejected", "implemented", "cancelled")
# what a submitted (or later) request may never change again (M64-4)
PAYLOAD_FIELDS = ("model_name", "record_id", "proposed_changes")
_CHATTER = frozenset(
    {"message_follower_ids", "message_ids", "activity_ids", "message_main_attachment_id"}
)


class FixMdmChangeRequest(models.Model):
    """A master-data change request.

    Governed changes (identity documents, critical classifications, brand
    authorisations) go through this model before being applied to the master.
    This is M64-core's primary governance mechanism: the request IS the
    change — it holds the proposed values, and only action_apply, after a
    routed steward approval, writes them to the golden record.
    """

    _name = "fix.mdm.change.request"
    _description = "MDM Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "create_date desc"

    # A12 P1-2: the decision is a routed M63 request decided by a domain
    # steward who is neither the proposer nor the record's creator. No DOFA
    # amount: the coded group is the authority.
    _approval_domain = "other"
    _approval_apply_method = "action_approve"
    _approval_group = STEWARD_GROUP
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")

    reference = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code("fix.mdm.change.request")
        or "NEW",
    )
    title = fields.Char(required=True, tracking=True)
    description = fields.Text()
    state = fields.Selection(
        CHANGE_REQUEST_STATES, default="draft", required=True, tracking=True, index=True
    )

    # The governed master record
    model_name = fields.Char(
        string="Target Model",
        required=True,
        help="Odoo model name, e.g. 'res.partner' or 'fix.catalogue.item'",
    )
    record_id = fields.Integer(
        string="Target Record ID",
        required=True,
        help="The database ID of the record this change request governs",
    )

    # The proposed change (JSON diff)
    proposed_changes = fields.Text(
        string="Proposed Changes (JSON)", help="A JSON object of {field: new_value} pairs"
    )
    current_values = fields.Text(
        string="Current Values (JSON)",
        readonly=True,
        help="Snapshot of current values at submission time",
    )

    # Review
    submitted_by = fields.Many2one("res.users", readonly=True, tracking=True)
    reviewed_by = fields.Many2one("res.users", readonly=True, tracking=True)
    reviewed_at = fields.Datetime(readonly=True)
    review_notes = fields.Text()
    applied_by = fields.Many2one("res.users", string="Applied By", readonly=True, copy=False)
    applied_at = fields.Datetime(string="Applied At", readonly=True, copy=False)
    priority = fields.Selection(
        [("low", "Low"), ("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")],
        default="normal",
        required=True,
        tracking=True,
    )

    # ---- guards (M64-3) ----------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_by",
            "current_values",
            "reviewed_by",
            "reviewed_at",
            "applied_by",
            "applied_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields() | set(PAYLOAD_FIELDS)
        if self and self.state != "draft":
            locked |= set(PAYLOAD_FIELDS)
        return locked

    def _approval_pinned_fields(self) -> set:
        # M64-4: an approval covered THIS target and THIS payload; changing
        # either voids the approval like a changed amount would.
        return super()._approval_pinned_fields() | set(PAYLOAD_FIELDS)

    def _approval_needed(self) -> bool:
        return self.state in ("submitted", "under_review")

    def _approval_excluded(self):
        # The proposer never decides their own change (BRU-MDM-06).
        return super()._approval_excluded() | self.submitted_by

    # ---- target validation (M64-12: cr_10, a request for a ghost record) --
    def _target_model(self):
        self.ensure_one()
        if self.model_name not in self.env:
            raise ValidationError(
                "The target model %r does not exist in this database, so change request "
                "%s cannot govern it." % (self.model_name, self.reference)
            )
        return self.env[self.model_name]

    def _target_record(self):
        record = self._target_model().browse(self.record_id).exists()
        if not record:
            raise ValidationError(
                "No %s with id %s exists: change request %s targets a record that is "
                "gone. Re-point it at a live record before submitting."
                % (self.model_name, self.record_id, self.reference)
            )
        return record

    def _proposed_values(self) -> dict:
        try:
            changes = json.loads(self.proposed_changes or "{}")
        except ValueError as exc:
            raise ValidationError(
                "Proposed changes of %s are not valid JSON: %s" % (self.reference, exc)
            ) from exc
        if not isinstance(changes, dict) or not changes:
            raise ValidationError(
                "Change request %s proposes nothing: give a JSON object of "
                "{field: new_value} pairs." % self.reference
            )
        return changes

    @api.constrains("model_name", "record_id", "proposed_changes")
    def _check_target_and_payload(self):
        for rec in self:
            target = rec._target_record()
            changes = rec._proposed_values()
            unknown = sorted(set(changes) - set(target._fields))
            if unknown:
                raise ValidationError(
                    "%s has no field(s) %s, so change request %s cannot propose them."
                    % (rec.model_name, ", ".join(unknown), rec.reference)
                )

    # ---- freeze / terminal immutability (M64-4) ---------------------------
    def write(self, vals):
        if self and not self._fix_guard_open():
            # a closed request is immutable: same-value posts still pass (the
            # P03 form posts every field it shows), any real change is refused
            terminal = self.filtered(lambda r: r.state in TERMINAL_STATES)
            if terminal:
                writable_names = set(vals) & set(self._fields) - _CHATTER
                if any(
                    rec._fix_guard_differs(name, vals[name], rec[name])
                    for rec in terminal
                    for name in writable_names
                    if name in rec._fields
                ):
                    raise UserError(
                        "A %s change request is closed: %s. Raise a new request instead."
                        % (
                            dict(CHANGE_REQUEST_STATES)[terminal[:1].state].lower(),
                            ", ".join(terminal.mapped("reference")[:3]),
                        )
                    )
            moved = self.filtered(lambda r: r.state != "draft")
            touched = set(PAYLOAD_FIELDS) & set(vals)
            if moved and touched:
                changed = {
                    name
                    for rec in moved
                    for name in touched
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                }
                if changed:
                    raise UserError(
                        "The target and payload of %s are frozen once submitted "
                        "(state=%s): cancel and raise a new request."
                        % (moved[:1].reference, moved[:1].state)
                    )
        return super().write(vals)

    # ---- lifecycle ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            self._emit("mdm.change_requested", rec)
        return records

    def _validate_proposed_against_dq(self, changes: dict) -> None:
        """BRU-MDM-05: a blocking (critical) DQ rule stops the change.

        Only rule types that can be checked against a PROPOSED value apply
        here (format/range); the nightly evaluator scores the stored data."""
        self.ensure_one()
        rules = self.env["fix.mdm.dq.rule"].search(
            [
                ("active", "=", True),
                ("severity", "=", "critical"),
                ("res_model", "=", self.model_name),
                ("rule_type", "in", ("format", "range")),
            ]
        )
        import re

        for rule in rules:
            if rule.field_name not in changes:
                continue
            value = changes[rule.field_name]
            if rule.rule_type == "format" and value not in (None, False, ""):
                if not re.fullmatch(rule.expression or "", str(value)):
                    raise ValidationError(
                        "Critical data-quality rule %s (%s on %s.%s) rejects the "
                        "proposed value %r: publication is blocked."
                        % (rule.code, rule.name, rule.res_model, rule.field_name, value)
                    )
            elif rule.rule_type == "range":
                try:
                    low, _, high = (rule.expression or "").partition("..")
                    number = float(value)
                except (TypeError, ValueError):
                    continue  # not a numeric rule/proposal pair; the cron reports it
                if (low.strip() and number < float(low)) or (high.strip() and number > float(high)):
                    raise ValidationError(
                        "Critical data-quality rule %s requires %s.%s in [%s]: "
                        "publication is blocked."
                        % (rule.code, rule.res_model, rule.field_name, rule.expression)
                    )

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError("Only draft requests can be submitted.")
            changes = rec._proposed_values()
            target = rec._target_record()
            rec._validate_proposed_against_dq(changes)
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by": self.env.uid,
                    "current_values": rec._snapshot_current(target, changes),
                }
            )
            rec.message_post(
                body="Submitted by %s; a domain steward decides it from the M63 "
                "approver's inbox (Request Approval)." % self.env.user.name
            )

    def _decision_checks(self) -> None:
        """Everything a steward decision (approve or reject) must satisfy."""
        authority = self._approval_authority_user()
        if not self._mdm_system_trusted() and not authority.has_group(STEWARD_GROUP):
            raise UserError(
                "Deciding an MDM change request needs the 'MDM Domain Steward' group, "
                "which %s does not hold." % authority.name
            )
        # BRU-MDM-06: the proposer cannot approve (or reject) their own change.
        acting = self._approval_acting_users()
        conflicted = self.filtered(lambda r: (r.submitted_by | r.create_uid) & acting)
        if conflicted:
            raise UserError(
                "Segregation of duties: you proposed change request %s, so a "
                "different domain steward must decide it." % conflicted[:1].reference
            )

    def _mdm_system_trusted(self) -> bool:
        # Superuser code with no deciding task (crons, data migration).
        return self.env.su and not self._approval_task()

    def action_approve(self):
        """The M63 apply method: a steward (never the proposer) approves.

        The routing assert fires first — the A03 control suite sweeps every
        routed model this way — so the draft-state refusal only surfaces for
        superuser code (which the assert deliberately lets through)."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state not in ("submitted", "under_review"):
                raise ValidationError("Only submitted requests can be approved.")
            rec._decision_checks()
            rec._guarded().write(
                {
                    "state": "approved",
                    "reviewed_by": self.env.uid,
                    "reviewed_at": fields.Datetime.now(),
                }
            )
            rec._emit("mdm.change_approved", rec)
            rec.message_post(
                body="Approved by %s%s. Apply writes the proposed values to %s/%s."
                % (
                    self.env.user.name,
                    " (on behalf of %s)" % rec._approval_authority_user().name
                    if rec._approval_authority_user() != self.env.user
                    else "",
                    rec.model_name,
                    rec.record_id,
                )
            )

    def _approval_on_rejected(self, comment):
        """A routed rejection lands here: same checks, terminal state."""
        for rec in self:
            if rec.state not in ("submitted", "under_review"):
                raise ValidationError("Only submitted requests can be rejected.")
            rec._decision_checks()
            rec._guarded().write(
                {
                    "state": "rejected",
                    "reviewed_by": self.env.uid,
                    "reviewed_at": fields.Datetime.now(),
                }
            )
            rec._emit("mdm.change_rejected", rec)

    def action_reject(self):
        """Direct steward rejection of a submitted request (M64-4: never of
        an approved one; terminal afterwards)."""
        for rec in self:
            if rec.state not in ("submitted", "under_review"):
                raise ValidationError("Only submitted requests can be rejected.")
            rec._decision_checks()
            rec._guarded().write(
                {
                    "state": "rejected",
                    "reviewed_by": self.env.uid,
                    "reviewed_at": fields.Datetime.now(),
                }
            )
            rec._emit("mdm.change_rejected", rec)
            rec.message_post(body="Rejected by %s." % self.env.user.name)

    def action_cancel(self):
        for rec in self:
            if rec.state in TERMINAL_STATES or rec.state in ("approved",):
                raise ValidationError("Only a draft or submitted request can be cancelled.")
            if rec.state == "submitted" and rec.approval_state == "pending":
                raise UserError("Recall the approval request before cancelling.")
            rec._guarded().write({"state": "cancelled"})

    def action_apply(self):
        """M64-1: apply the APPROVED proposed values to the target record.

        A separate step after the checks, under sudo, inside a savepoint, and
        re-validated: the approval changed nothing until this runs."""
        for rec in self:
            if rec.state != "approved":
                raise ValidationError(
                    "Only an approved change request can be applied (state=%s)." % rec.state
                )
            authority = rec._approval_authority_user()
            if not rec._mdm_system_trusted() and not authority.has_group(STEWARD_GROUP):
                raise UserError(
                    "Applying an MDM change request needs the 'MDM Domain Steward' "
                    "group, which %s does not hold." % authority.name
                )
            changes = rec._proposed_values()
            target = rec._target_record()
            unknown = sorted(set(changes) - set(target._fields))
            if unknown:
                raise ValidationError(
                    "%s no longer carries field(s) %s; the request must be re-raised."
                    % (rec.model_name, ", ".join(unknown))
                )
            with rec.env.cr.savepoint():
                # sudo: the steward holds the decision, not the write access to
                # the governed master (BRU-MDM-01: no direct edits).
                target.sudo().write(changes)
            rec._guarded().write(
                {
                    "state": "implemented",
                    "applied_by": rec.env.uid,
                    "applied_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Applied by %s: %s written to %s/%s."
                % (rec.env.user.name, ", ".join(sorted(changes)), rec.model_name, rec.record_id)
            )
        return True

    def _snapshot_current(self, target=None, changes=None) -> str:
        """Snapshot the current values of the governed record."""
        try:
            target = target or self._target_model().browse(self.record_id)
            changes = changes or (
                json.loads(self.proposed_changes) if self.proposed_changes else {}
            )
            if target.exists() and changes:
                return json.dumps(target.read(list(changes.keys()))[0], default=str)
        except Exception:
            logger.warning(
                "MDM snapshot of %s/%s failed", self.model_name, self.record_id, exc_info=True
            )
        return "{}"

    def _emit(self, event_type: str, rec) -> None:
        from libs.py.fix_events import publish

        publish(
            self.env,
            event_type,
            "fix.mdm.change.request",
            rec.id,
            {
                "reference": rec.reference,
                "model_name": rec.model_name,
                "record_id": rec.record_id,
                "state": rec.state,
            },
        )

    # ---- A12 event consumers (FF-48) --------------------------------------
    # The decision trail is the chatter: whoever holds the record sees what
    # happened to it without opening the outbox.
    @api.model
    def consume_mdm_change_requested(self, event):
        rec = self.browse(event.get("aggregate_id")).exists()
        if rec and hasattr(rec, "message_post"):
            rec.message_post(
                body="Change requested (%s): governs %s/%s."
                % (rec.reference, rec.model_name, rec.record_id)
            )
        return True

    @api.model
    def consume_mdm_change_decided(self, event):
        rec = self.browse(event.get("aggregate_id")).exists()
        if rec and hasattr(rec, "message_post"):
            rec.message_post(
                body="Change %s (%s)." % (event.get("event_type", "").split(".")[-1], rec.reference)
            )
        return True
