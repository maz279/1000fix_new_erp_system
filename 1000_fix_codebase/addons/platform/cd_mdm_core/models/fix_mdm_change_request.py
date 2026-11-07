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
#
# A12 finish audit (2026-11-07): the payload checks live in
# fix_mdm_attribute_governance.py and run at entry, at submit and at apply. A plain user
# can edit only their own request (security/fix_mdm_rules.xml); submit records
# the impact of the change (BRU-MDM-07); apply refuses a master that moved
# after the snapshot; a request whose value cannot be written can be cancelled.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import SQL

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
# what the steward read when deciding: frozen with the payload
FROZEN_AFTER_SUBMIT = (*PAYLOAD_FIELDS, "title", "description")
# Impact analysis is bounded: a master like res.partner has hundreds of
# references, and an unindexed one must not stall a submit.
IMPACT_MAX_FIELDS = 400
IMPACT_CAP_PER_FIELD = 1000
IMPACT_SKIPPED_PREFIXES = ("mail.", "ir.", "bus.", "base.", "fix.event.")
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
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "fix.approvable.mixin",
        "fix.mdm.payload.mixin",
    ]
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
        string="Proposed Changes",
        help="One field=value per line, or a JSON object of {field: new_value} pairs",
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
    review_notes = fields.Text(help="A steward's notes while the request is being decided.")
    impact_reference_count = fields.Integer(
        string="Referencing Records",
        readonly=True,
        copy=False,
        help="How many records point at the target, counted at submit.",
    )
    impact_summary = fields.Text(
        string="Impact",
        readonly=True,
        copy=False,
        help="Measured at submit, for the steward to read before deciding (BRU-MDM-07).",
    )
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
            "reference",
            "impact_reference_count",
            "impact_summary",
            "submitted_by",
            "current_values",
            "reviewed_by",
            "reviewed_at",
            "applied_by",
            "applied_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(FROZEN_AFTER_SUBMIT)
        if not self or not self._review_notes_open():
            locked |= {"review_notes"}
        return locked

    def _review_notes_open(self) -> bool:
        """A steward other than the proposer notes a request while deciding it."""
        self.ensure_one()
        user = self.env.user
        return (
            self.state in ("submitted", "under_review")
            and user.has_group(STEWARD_GROUP)
            and user not in (self.submitted_by | self.create_uid)
        )

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
        self.ensure_one()
        return self._mdm_parse_payload(self.proposed_changes, self.model_name, self.reference)

    @api.constrains("model_name", "record_id", "proposed_changes")
    def _check_target_and_payload(self):
        for rec in self:
            target = rec._target_record()
            changes = rec._proposed_values()
            rec._mdm_assert_governed(rec.model_name, changes, rec.reference)
            rec._mdm_assert_route(target, rec.reference)

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
            touched = set(FROZEN_AFTER_SUBMIT) & set(vals)
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
            if "review_notes" in vals:
                for rec in self:
                    if (
                        rec._fix_guard_differs(
                            "review_notes", vals["review_notes"], rec.review_notes
                        )
                        and not rec._review_notes_open()
                    ):
                        raise UserError(
                            "Review notes on %s are the deciding steward's, while the "
                            "request is being decided." % rec.reference
                        )
        return super().write(vals)

    # ---- lifecycle ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            self._emit("mdm.change_requested", rec)
        return records

    def _impact(self, target, changes) -> tuple:
        """BRU-MDM-07: what depends on the target, measured when it is submitted.

        Every stored many2one pointing at the target's model is counted, each
        with a cap, so a heavily referenced master cannot stall the submit."""
        self.ensure_one()
        self.env.flush_all()
        references = []
        relations = (
            self.env["ir.model.fields"]
            .sudo()
            .search(
                [
                    ("ttype", "=", "many2one"),
                    ("relation", "=", target._name),
                    ("store", "=", True),
                ],
                limit=IMPACT_MAX_FIELDS,
            )
        )
        for relation in relations:
            if relation.model.startswith(IMPACT_SKIPPED_PREFIXES) or relation.model not in self.env:
                continue
            model = self.env[relation.model]
            field = model._fields.get(relation.name)
            if (
                model._abstract
                or model._transient
                or not model._auto
                or field is None
                or not field.store
                or field.company_dependent
            ):
                continue
            self.env.cr.execute(
                SQL(
                    "SELECT count(*) FROM (SELECT 1 FROM %s WHERE %s = %s LIMIT %s) AS hit",
                    SQL.identifier(model._table),
                    SQL.identifier(field.name),
                    target.id,
                    IMPACT_CAP_PER_FIELD,
                )
            )
            hits = self.env.cr.fetchone()[0]
            if hits:
                references.append((hits, relation.model, relation.name))
        references.sort(key=lambda row: (-row[0], row[1], row[2]))
        Register = self.env["fix.mdm.governed.attribute"]
        labels = dict(Register._fields["category"].selection)
        attributes = ", ".join(
            "%s (%s)" % (row.field_name, labels.get(row.category))
            for row in Register._rows(target._name, changes)
        )
        total = sum(row[0] for row in references)
        lines = ["Changes: %s." % attributes]
        lines.append(
            "%d record(s) reference %s through %d field(s)."
            % (total, target.display_name, len(references))
        )
        lines += ["%s.%s: %d" % (model, name, hits) for hits, model, name in references[:15]]
        if len(references) > 15:
            lines.append("...and %d more field(s)." % (len(references) - 15))
        return total, "\n".join(lines)

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError("Only draft requests can be submitted.")
            changes = rec._proposed_values()
            target = rec._target_record()
            rec._mdm_check_payload(target, changes, rec.company_id, rec.reference)
            # E4: a value that cannot be written never reaches a steward.
            rec._mdm_dry_run(target, changes, rec.reference)
            impact_count, impact_summary = rec._impact(target, changes)
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by": self.env.uid,
                    "current_values": rec._snapshot_current(target, changes),
                    "impact_reference_count": impact_count,
                    "impact_summary": impact_summary,
                }
            )
            rec.message_post(
                body="Submitted by %s; a domain steward decides it from the M63 "
                "approver's inbox (Request Approval). %s"
                % (self.env.user.name, impact_summary.splitlines()[1])
            )

    def action_request_approval(self, justification=None):
        """BRU-MDM-22: nobody decides a change whose reason is not stated."""
        if not self.env.su:
            for rec in self:
                if not (justification or rec.description or "").strip():
                    raise UserError(
                        "State why %s is needed: give a justification or a description."
                        % rec.reference
                    )
        return super().action_request_approval(justification=justification)

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
            # sudo after the checks: a delegate decides on a steward's authority
            # and need not be able to edit other people's requests.
            rec.sudo()._guarded().write(
                {
                    "state": "approved",
                    "reviewed_by": self.env.uid,
                    "reviewed_at": fields.Datetime.now(),
                }
            )
            rec._emit("mdm.change_approved", rec)
            rec.sudo().message_post(
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

    def _mark_rejected(self, comment):
        self.ensure_one()
        if self.state not in ("submitted", "under_review"):
            raise ValidationError("Only submitted requests can be rejected.")
        self._decision_checks()
        vals = {
            "state": "rejected",
            "reviewed_by": self.env.uid,
            "reviewed_at": fields.Datetime.now(),
        }
        if (comment or "").strip():
            vals["review_notes"] = comment.strip()
        self.sudo()._guarded().write(vals)
        self._emit("mdm.change_rejected", self)

    def _approval_on_rejected(self, comment):
        """A routed rejection lands here: same checks, terminal state."""
        for rec in self:
            rec._mark_rejected(comment)

    def action_reject(self, comment=None):
        """Direct steward rejection of a submitted request (M64-4: never of
        an approved one; terminal afterwards). E7: it also closes the routed
        request, so no steward is left deciding a dead task."""
        for rec in self:
            rec._mark_rejected(comment)
            request = rec.sudo().approval_request_id
            if request and request.state == "pending":
                request._finish(
                    "rejected",
                    "rejected",
                    self.env.user,
                    comment=comment or "Rejected on the request.",
                    record_state="rejected",
                )
            rec.sudo().message_post(
                body="Rejected by %s%s." % (self.env.user.name, ": %s" % comment if comment else "")
            )

    def action_cancel(self):
        """E4: also from approved-not-applied, or a request whose value can no
        longer be written would be stranded for ever."""
        for rec in self:
            if rec.state in TERMINAL_STATES:
                raise ValidationError(
                    "Only an open request can be cancelled (%s is %s)." % (rec.reference, rec.state)
                )
            if rec.approval_state == "pending":
                raise UserError("Recall the approval request before cancelling.")
            if rec.state == "approved":
                rec._approval_void("the approved request was cancelled before it was applied")
            rec._guarded().write({"state": "cancelled"})
            rec.message_post(body="Cancelled by %s." % self.env.user.name)

    def action_apply(self):
        """M64-1: apply the APPROVED proposed values to the target record.

        A separate step after the checks, under sudo, inside a savepoint, and
        re-validated: the approval changed nothing until this runs. Every
        check that ran at submit runs again, against the master as it is now."""
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
            rec._mdm_check_payload(target, changes, rec.company_id, rec.reference)
            rec._mdm_assert_fresh(target, changes, rec.current_values, rec.reference)
            rec._mdm_write(target, changes, rec.reference)
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
        self.ensure_one()
        return self._mdm_snapshot(
            target or self._target_record(), changes or self._proposed_values()
        )

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
