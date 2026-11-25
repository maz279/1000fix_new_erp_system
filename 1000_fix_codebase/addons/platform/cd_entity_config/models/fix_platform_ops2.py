# M30 platform operations (environments, releases), M64 MDM (duplicates, xref),
# M65 localisation (payment gateways). Registered screens in the A12 fragments.
#
# A12 audit (2026-11-04):
#   * P1-4 fix.payment.gateway: activation moved from ANY state to a guarded
#     state machine (draft->active, suspended->active, active/sandbox->live),
#     every transition writes a fix.security.audit row through B1's
#     log_event(), and checkout can assert the gateway is live through
#     assert_live_for_checkout(). The M63 ROUTING lives in
#     cd_multi_entity/models/fix_payment_gateway_approval.py - cd_entity_config
#     cannot depend on the workflow engine (the engine depends on it).
#   * P1-2 fix.mdm.duplicate: a "merge" stamped a survivor reference and moved
#     nothing. For the party master it now delegates to M33's supervised merge
#     (fix.party.merge, itself M63-routed, SOD-15, reversible); other domains
#     refuse clearly instead of pretending.
#   * D8 fix.platform.release: a release with no approved ITSM change ships
#     untracked; action_release now refuses without a linked fix.itsm.change
#     that is approved or implemented (a release ships an approved change;
#     an implemented change - already deployed - also qualifies).
#
# A12 finish audit (2026-11-07):
#   * E5/E12/E13 fix.payment.gateway: a suspended rail reopened through an
#     archive, a rename or a delete, because the identity was pinned only while
#     active. It is now pinned in every state but draft; only a draft is deleted.
#     WHAT READS THE REGISTER: storefront checkout only. credential_ref is a
#     POINTER that no integration dereferences (the storefront's real secret is
#     the cd_storefront.gateway_secret.<rail> parameter), so rotating it records
#     a decision and does not change a live secret. The screen says so.
#   * E7 fix.platform.release: frozen after release, a second person releases,
#     a target environment and one release per change are required, and in_test
#     and rolled_back are reachable.
#   * E8: a credential enters at creation and a live one rotates only through
#     the routed approval, inside its vault namespace.
#   * E14 fix.platform.environment: state moves through audited actions, a new
#     environment is born provisioning, base_url must be https (plain http only
#     for a dev environment on this machine), and non-production goes live only
#     with masking evidence recorded by a second person (BRU-ADM-16).
from urllib.parse import urlsplit

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_entity import audit_event
from .fix_platform_ops import _require_steward_group

GATEWAY_APPROVER_GROUP = "cd_entity_config.group_gateway_activation_approver"
PLATFORM_ADMIN_GROUP = "cd_entity_config.group_platform_admin"
# Comma-separated vault:// prefixes a gateway credential may point into. Unset
# (the default): a rotation of a non-draft gateway stays in its current namespace.
VAULT_NAMESPACES_PARAM = "fix_gateway.vault_namespaces"
# Non-production holds copies of data, so it goes live only with masking evidence.
MASKED_KINDS = ("dev", "staging")
LOCAL_HOSTS = ("localhost", "127.0.0.1", "[::1]")


def _require_gateway_authority(env, what):
    """P1-4 code check: gateway operations need the coded approver group (or
    a platform admin); the ACL grants access, this guards the action."""
    if env.su:
        return
    if not (env.user.has_group(GATEWAY_APPROVER_GROUP) or env.user.has_group(PLATFORM_ADMIN_GROUP)):
        raise UserError(
            "%s requires the 'Payment Gateway Activation Approver' role, "
            "which %s does not hold." % (what, env.user.name)
        )


class FixPlatformEnvironment(models.Model):
    _name = "fix.platform.environment"
    _description = "Platform Environment"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "kind, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    kind = fields.Selection(
        [
            ("dev", "Development"),
            ("staging", "Staging"),
            ("production", "Production"),
            ("dr", "Disaster Recovery"),
        ],
        required=True,
        default="staging",
    )
    base_url = fields.Char(required=True, tracking=True)
    database_name = fields.Char()
    release_channel = fields.Selection(
        [("edge", "Edge"), ("stable", "Stable"), ("lts", "LTS")],
        required=True,
        default="stable",
    )
    state = fields.Selection(
        [
            ("provisioning", "Provisioning"),
            ("live", "Live"),
            ("degraded", "Degraded"),
            ("offline", "Offline"),
        ],
        required=True,
        default="provisioning",
        tracking=True,
    )
    owner_id = fields.Many2one("res.users", string="Owner")
    data_residency = fields.Char(default="BD-Dhaka")
    notes = fields.Char()
    masking_state = fields.Selection(
        [("pending", "Not Evidenced"), ("verified", "Evidence Recorded")],
        string="Data Masking",
        required=True,
        default="pending",
        tracking=True,
        help="BRU-ADM-16: whether a person has recorded evidence that personal "
        "data is masked in this environment. It records that statement; this "
        "system does not inspect the data.",
    )
    masking_evidence = fields.Char(string="Masking Evidence", tracking=True)
    masking_recorded_by_id = fields.Many2one(
        "res.users", string="Evidence Recorded By", readonly=True, copy=False
    )
    masking_recorded_on = fields.Date(string="Evidence Recorded On", readonly=True, copy=False)

    _name_unique = models.Constraint("UNIQUE (name, company_id)", "Environment name is unique")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "masking_state",
            "masking_evidence",
            "masking_recorded_by_id",
            "masking_recorded_on",
        }

    @api.constrains("base_url", "kind")
    def _check_base_url(self):
        for rec in self:
            parts = urlsplit((rec.base_url or "").strip())
            local_dev = (
                rec.kind == "dev"
                and parts.scheme == "http"
                and (parts.netloc.rsplit(":", 1)[0] if parts.port else parts.netloc) in LOCAL_HOSTS
            )
            if not (parts.netloc and (parts.scheme == "https" or local_dev)):
                raise ValidationError(
                    "The base URL of %s must be https:// (plain http only for a dev "
                    "environment on this machine)." % rec.name
                )

    def write(self, vals):
        before = {rec.id: rec.base_url for rec in self} if "base_url" in vals else {}
        result = super().write(vals)
        for rec in self:
            if rec.id in before and before[rec.id] != rec.base_url:
                rec._audit_log("platform.environment_url_changed", "base URL changed")
        return result

    def _audit_log(self, event, detail):
        for rec in self:
            audit_event(
                rec.env,
                event,
                "fix.platform.environment,%d" % rec.id,
                "%s (%s, %s) by %s" % (detail, rec.name, rec.kind, rec.env.user.name),
            )

    def _set_environment_state(self, new_state, from_states, event, reason=None):
        for rec in self:
            if not rec.env.su and not rec.env.user.has_group(PLATFORM_ADMIN_GROUP):
                raise UserError(
                    "Changing an environment's state needs the 'Platform Admin' role, "
                    "which %s does not hold." % rec.env.user.name
                )
            if rec.state not in from_states:
                raise UserError(
                    "%s is %s: it cannot move to %s from there."
                    % (rec.name, dict(rec._fields["state"].selection)[rec.state], new_state)
                )
            rec._guarded().write({"state": new_state})
            rec._audit_log(event, reason or new_state)
            if reason:
                rec.message_post(body="%s: %s" % (new_state, reason))

    def action_go_live(self):
        """Provisioning, degraded or offline to live. A dev or staging copy
        needs the masking evidence first (BRU-ADM-16)."""
        for rec in self:
            if rec.kind in MASKED_KINDS and rec.masking_state != "verified":
                raise UserError(
                    "%s is a non-production environment with no masking evidence: "
                    "record it first (Record Masking Evidence)." % rec.name
                )
        self._set_environment_state(
            "live", ("provisioning", "degraded", "offline"), "platform.environment_live"
        )
        return True

    def action_mark_degraded(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say why this environment is degraded.")
        self._set_environment_state("degraded", ("live",), "platform.environment_degraded", reason)
        return True

    def action_take_offline(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say why this environment is going offline.")
        self._set_environment_state(
            "offline",
            ("provisioning", "live", "degraded"),
            "platform.environment_offline",
            reason,
        )
        return True

    def action_record_masking(self, evidence=None):
        """A person states the evidence; the owner of the environment does not
        vouch for their own copy (BRU-ADM-16)."""
        for rec in self:
            if not rec.env.su:
                if not rec.env.user.has_group(PLATFORM_ADMIN_GROUP):
                    raise UserError(
                        "Recording masking evidence needs the 'Platform Admin' role, "
                        "which %s does not hold." % rec.env.user.name
                    )
                if rec.env.user in (rec.create_uid | rec.owner_id):
                    raise UserError(
                        "A second person records the masking evidence: you created or "
                        "own %s." % rec.name
                    )
            if not (evidence or "").strip():
                raise UserError(
                    "Give the masking evidence: the run, ticket or report that shows it."
                )
            rec._guarded().write(
                {
                    "masking_state": "verified",
                    "masking_evidence": evidence.strip(),
                    "masking_recorded_by_id": rec.env.uid,
                    "masking_recorded_on": fields.Date.context_today(rec),
                }
            )
            rec._audit_log(
                "platform.environment_masking", "masking evidence: %s" % evidence.strip()
            )
        return True


class FixPlatformRelease(models.Model):
    _name = "fix.platform.release"
    _description = "Release Coordination"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "planned_on desc, id desc"

    version = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    environment_id = fields.Many2one("fix.platform.environment", string="Target Environment")
    planned_on = fields.Date(required=True, default=fields.Date.context_today)
    released_on = fields.Date()
    change_summary = fields.Text()
    rollback_plan = fields.Text()
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("in_test", "In Test"),
            ("released", "Released"),
            ("rolled_back", "Rolled Back"),
        ],
        required=True,
        default="planned",
        tracking=True,
    )
    owner_id = fields.Many2one("res.users", string="Release Owner")
    # D8: the ITSM change this release ships. The m2o itself lives in
    # cd_multi_entity (fix_platform_release_itsm.py): its comodel is in
    # cd_itsm, which loads AFTER this module (cd_itsm depends on
    # cd_entity_config), and a m2o here breaks incremental -u setup.
    released_by_id = fields.Many2one("res.users", string="Released By", readonly=True, copy=False)
    rolled_back_reason = fields.Char(string="Rollback Reason", readonly=True, copy=False)

    _version_unique = models.Constraint(
        "UNIQUE (version, company_id)", "A release version is unique per company"
    )

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "state",
            "released_on",
            "released_by_id",
            "rolled_back_reason",
        }
        # A12 finish E7: a shipped release is a record of what shipped. It was
        # rewritten after the fact, its change re-linked, its version renamed.
        if self and any(rec.state in ("released", "rolled_back") for rec in self):
            guarded |= {
                "version",
                "name",
                "company_id",
                "environment_id",
                "planned_on",
                "change_summary",
                "rollback_plan",
                "owner_id",
                "itsm_change_id",
            }
        return guarded

    def action_start_test(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Only a planned release goes into test (%s)." % rec.version)
            if not rec.environment_id:
                raise UserError("Name the target environment of %s first." % rec.version)
            rec._guarded().write({"state": "in_test"})
            rec.message_post(body="In test, by %s." % rec.env.user.name)
        return True

    def action_rollback(self, reason=None):
        for rec in self:
            if rec.state != "released":
                raise UserError("Only a released release can be rolled back (%s)." % rec.version)
            if not (reason or "").strip():
                raise UserError("Say why %s is being rolled back." % rec.version)
            rec._guarded().write(
                {"state": "rolled_back", "rolled_back_reason": reason.strip()[:250]}
            )
            rec.message_post(body="Rolled back by %s: %s" % (rec.env.user.name, reason.strip()))
        return True

    def action_release(self):
        for rec in self:
            if rec.state not in ("planned", "in_test"):
                raise UserError("Only a planned or in-test release can be released")
            if not (rec.rollback_plan or "").strip():
                raise UserError("A release must state its rollback plan before it ships")
            if not rec.environment_id:
                raise UserError("A release must name its target environment before it ships")
            # A12 finish E7: the same person planned it and shipped it. Superuser
            # code stays trusted, as with every guard here.
            if not rec.env.su and rec.env.user in (rec.create_uid | rec.owner_id):
                raise UserError(
                    "A second person releases: you created or own release %s." % rec.version
                )
            # D8: rule chosen - a release ships an approved change. An
            # IMPLEMENTED change (already deployed through ITSM) also
            # qualifies; draft/rolled-back/rejected changes do not. The
            # field ships from cd_multi_entity (module-order requirement),
            # so it is read tolerantly here.
            change = getattr(rec, "itsm_change_id", False)
            if not change:
                raise UserError(
                    "Release %s is not linked to an ITSM change: link the change "
                    "request it ships (D8)." % rec.version
                )
            # N-M66-6: a reviewed change is an implemented one after its PIR, so it
            # still ships. An emergency change the approver rejected afterwards does
            # not. Read tolerantly: the field lives in cd_itsm, which loads after this.
            if change.state not in ("approved", "implemented", "reviewed"):
                raise UserError(
                    "The linked ITSM change %s is %s: a release may only ship an "
                    "approved or implemented change, reviewed or not (D8)."
                    % (change.name, change.state)
                )
            if getattr(change, "retro_approval_state", False) == "rejected":
                raise UserError(
                    "The linked ITSM change %s was rejected at its retrospective "
                    "approval, so a release may not ship it (D8)." % change.name
                )
            if self.sudo().search_count(
                [
                    ("itsm_change_id", "=", change.id),
                    ("state", "=", "released"),
                    ("id", "!=", rec.id),
                ]
            ):
                raise UserError(
                    "ITSM change %s has already shipped in another release: one change "
                    "ships one release (D8). A later release needs its own change." % change.name
                )
            rec._guarded().write(
                {
                    "state": "released",
                    "released_on": fields.Date.context_today(rec),
                    "released_by_id": rec.env.uid,
                }
            )
            rec.message_post(body="Released by %s." % rec.env.user.name)
        return True


class FixMdmDuplicate(models.Model):
    """A duplicate CANDIDATE: the detection engine proposes, a steward decides.

    A merge decision on the party master is delegated to M33's supervised
    merge (fix.party.merge) - it is M63-routed, executor-checked (SOD-15) and
    reversible; this register never fakes the physical merge itself. Domains
    without a supervised merge engine refuse clearly.
    """

    _name = "fix.mdm.duplicate"
    _description = "Duplicate Record Candidate"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "score desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    res_model = fields.Char(string="Master Model", required=True, index=True)
    record_a_ref = fields.Char(required=True)
    record_b_ref = fields.Char(required=True)
    score = fields.Float(help="Match score 0-100 from the detection run.")
    match_factors = fields.Char(help="Which fields matched: name, phone, TIN…")
    decision = fields.Selection(
        [
            ("pending", "Pending"),
            ("merged", "Merged"),
            ("kept_separate", "Kept Separate"),
            ("false_positive", "False Positive"),
        ],
        required=True,
        default="pending",
        tracking=True,
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By")
    decided_on = fields.Datetime()
    survivor_ref = fields.Char(help="For a merge: the record that survived.")
    decision_note = fields.Char(
        help="Why this decision: required to merge a pair below the configured score threshold."
    )
    # The supervised M33 merge this pair was delegated to (fix.party.merge id).
    # A plain Integer, not a Many2one: cd_party_master is loaded with the
    # estate but is not a manifest dependency of this module.
    party_merge_id = fields.Integer(
        string="M33 Merge", readonly=True, copy=False, help="Id of the fix.party.merge transaction."
    )

    def _fix_guarded_fields(self) -> set:
        # E18: the score is what the detection run measured. Typing it would
        # answer the merge threshold's own question.
        return super()._fix_guarded_fields() | {
            "score",
            "decision",
            "decided_by_id",
            "decided_on",
            "survivor_ref",
            "party_merge_id",
        }

    @api.model
    def _merge_score_threshold(self) -> float:
        # Business tunable (M64 md_04): below this score a merge needs a note.
        return float(
            self.env["ir.config_parameter"].sudo().get_param("fix_mdm.merge_score_threshold", "80")
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.mdm.duplicate") or "MDM/DUP/New"
                )
        return super().create(vals_list)

    def _resolve_party(self, ref):
        """Resolve a candidate reference to a res.partner: a database id or the
        partner's own `ref` code."""
        self.ensure_one()
        Partner = self.env["res.partner"]
        value = (ref or "").strip()
        if not value:
            raise UserError("A duplicate candidate needs both record references.")
        if value.isdigit():
            partner = Partner.browse(int(value)).exists()
        else:
            partner = Partner.search([("ref", "=", value)], limit=1)
        if not partner:
            raise UserError("Cannot resolve %r to a partner (duplicate %s)." % (value, self.name))
        return partner

    def _open_merge(self):
        """The M33 merge this pair is committed to: executed, or still awaiting
        its decision. A rejected or recalled one no longer binds the pair."""
        self.ensure_one()
        Merge = self.env.get("fix.party.merge")
        if not self.party_merge_id or Merge is None:
            return None
        merge = Merge.sudo().browse(self.party_merge_id).exists()
        if merge and (
            merge.state == "executed"
            or (merge.state == "draft" and merge.approval_state in ("pending", "approved"))
        ):
            return merge
        return None

    def _assert_no_open_merge(self):
        if self._open_merge():
            raise UserError(
                "%s already has M33 merge %s in progress: decide or reverse that one."
                % (self.name, self.party_merge_id)
            )

    def _merge_survivor_ref(self, survivor):
        """E19: the steward names the survivor, Record A or Record B. Blank
        keeps the pair's stated survivor, or Record A."""
        self.ensure_one()
        wanted = str(survivor).strip() if survivor not in (None, False) else ""
        if not wanted:
            return self.survivor_ref or self.record_a_ref
        candidates = {self.record_a_ref.strip(), self.record_b_ref.strip()}
        if wanted not in candidates:
            raise UserError(
                "The survivor must be Record A (%s) or Record B (%s) of %s, not %r."
                % (self.record_a_ref, self.record_b_ref, self.name, wanted)
            )
        return wanted

    def action_merge(self, justification=None, survivor=None):
        """P1-2: delegate the merge to the supervised engine for the domain.

        res.partner -> M33 fix.party.merge (routed through M63 by M33 itself:
        a steward who is not the creator executes, SOD-15, reversible).
        Any other master -> refused clearly: no supervised merge engine exists
        for it in this build."""
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This candidate pair is already decided")
            _require_steward_group(self.env, "Merging a duplicate candidate")
            rec._assert_no_open_merge()
            if (rec.score or 0.0) < rec._merge_score_threshold() and not (
                justification or rec.decision_note or ""
            ).strip():
                raise UserError(
                    "Merging %s scores %.0f%%, below the configured threshold "
                    "(ir.config_parameter fix_mdm.merge_score_threshold): give a "
                    "justification or a decision note." % (rec.name, rec.score or 0.0)
                )
            if rec.res_model != "res.partner":
                raise UserError(
                    "Duplicate merge for %s has no supervised merge engine in this "
                    "build: only the party master (res.partner) merges, through "
                    "the M33 supervised merge. Record the decision as kept "
                    "separate or false positive, and route %s through its domain "
                    "module." % (rec.res_model, rec.res_model)
                )
            if "fix.party.merge" not in self.env:
                raise UserError(
                    "The party merge engine (cd_party_master) is not installed: "
                    "the duplicate cannot be merged here."
                )
            survivor_party = rec._resolve_party(rec._merge_survivor_ref(survivor))
            parties = rec._resolve_party(rec.record_a_ref) | rec._resolve_party(rec.record_b_ref)
            victim = parties - survivor_party
            if len(victim) != 1:
                raise UserError("The survivor and the victim are the same record.")
            merge = self.env["fix.party.merge"].create(
                {
                    "survivor_id": survivor_party.id,
                    "victim_id": victim.id,
                    "company_id": rec.company_id.id,
                }
            )
            # M33 carries its own M63 routing, SOD-15 and reversal; the
            # physical merge happens when the routed steward executes it.
            merge.action_request_approval(justification=justification)
            rec._guarded().write(
                {"party_merge_id": merge.id, "survivor_ref": str(survivor_party.id)}
            )
            rec.message_post(
                body=(
                    "Merge delegated to M33 supervised merge %s (survivor %s, "
                    "victim %s) by %s: the pair merges when the routed steward "
                    "executes it."
                    % (
                        merge.id,
                        survivor_party.display_name,
                        victim.display_name,
                        self.env.user.name,
                    )
                )
            )

    def action_sync_merge_state(self):
        """Mirror the M33 merge's outcome onto the candidate: merged only when
        the physical merge executed, back to pending when it was reversed."""
        Merge = self.env.get("fix.party.merge")
        for rec in self:
            if not rec.party_merge_id or Merge is None:
                continue
            merge = Merge.browse(rec.party_merge_id).exists()
            if not merge:
                continue
            if merge.state == "executed" and rec.decision == "pending":
                rec._guarded().write(
                    {
                        "decision": "merged",
                        "decided_by_id": merge.executed_by.id,
                        "decided_on": merge.executed_at,
                        "survivor_ref": str(merge.survivor_id.id),
                    }
                )
                rec.message_post(body="M33 merge %s executed: pair merged." % merge.id)
            elif merge.state == "reversed" and rec.decision == "merged":
                rec._guarded().write(
                    {"decision": "pending", "decided_by_id": False, "decided_on": False}
                )
                rec.message_post(body="M33 merge %s was reversed: pair pending again." % merge.id)

    @api.model
    def _sync_from_party_merge(self, merge):
        """E17: M33 calls this when a merge executes or reverses, so the pair
        never reads pending behind a merge that already happened. A pair that
        names the same two parties follows too, however that merge was raised."""
        Duplicate = self.sudo()
        pair = {str(merge.survivor_id.id), str(merge.victim_id.id)}
        linked = Duplicate.search([("party_merge_id", "=", merge.id)])
        same_parties = Duplicate.search(
            [
                ("res_model", "=", "res.partner"),
                ("decision", "=", "pending"),
                ("record_a_ref", "in", list(pair)),
                ("record_b_ref", "in", list(pair)),
                ("party_merge_id", "in", (0, False)),
            ]
        ).filtered(lambda d: {d.record_a_ref.strip(), d.record_b_ref.strip()} == pair)
        for rec in same_parties:
            rec._guarded().write({"party_merge_id": merge.id})
        (linked | same_parties).action_sync_merge_state()

    def _decide(self, decision, note=None):
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This candidate pair is already decided")
            _require_steward_group(self.env, "Deciding a duplicate candidate")
            rec._assert_no_open_merge()
            vals = {
                "decision": decision,
                "decided_by_id": self.env.uid,
                "decided_on": fields.Datetime.now(),
            }
            if (note or "").strip():
                vals["decision_note"] = note.strip()[:250]
            rec._guarded().write(vals)
            rec.message_post(
                body="%s by %s%s."
                % (
                    dict(rec._fields["decision"].selection)[decision],
                    self.env.user.name,
                    ": %s" % note.strip() if (note or "").strip() else "",
                )
            )

    def action_keep_separate(self, note=None):
        self._decide("kept_separate", note)

    def action_false_positive(self, note=None):
        """E22: not a duplicate at all. The pair is recorded, and the detection
        run never raises it again."""
        if not (note or "").strip():
            raise UserError("Say why this pair is not a duplicate.")
        self._decide("false_positive", note)


class FixMdmXref(models.Model):
    """A12 finish audit (E30): a verified mapping is not silently re-pointed,
    and a mapping onto a published code list must name one of its values."""

    _name = "fix.mdm.xref"
    _description = "Cross-Reference Mapping"
    _inherit = ["mail.thread"]
    _order = "code_list, source_value"

    code_list = fields.Char(string="Code List / Domain", required=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    source_system = fields.Char(required=True)
    source_value = fields.Char(required=True)
    canonical_value = fields.Char(required=True, tracking=True)
    canonical_label = fields.Char()
    confidence = fields.Selection(
        [("verified", "Verified"), ("inferred", "Inferred"), ("disputed", "Disputed")],
        required=True,
        default="verified",
        tracking=True,
    )
    active = fields.Boolean(default=True)

    _xref_unique = models.Constraint(
        "UNIQUE (code_list, source_system, source_value, company_id)",
        "A source value maps once per domain and system",
    )

    @api.constrains("code_list", "canonical_value", "company_id")
    def _check_canonical_in_list(self):
        Lists = self.env["fix.mdm.code.list"].sudo()
        for rec in self:
            live = Lists.search(
                [
                    ("code", "=", rec.code_list),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "published"),
                ],
                limit=1,
            )
            if live and rec.canonical_value not in live.entry_ids.mapped("value"):
                raise ValidationError(
                    "%r is not a value of published code list %s: a mapping must point at "
                    "one of its values." % (rec.canonical_value, rec.code_list)
                )

    def write(self, vals):
        # A verified mapping keeps its word: mark it disputed or inferred first,
        # which the thread records, and only then re-point it.
        if "canonical_value" in vals and not self.env.su:
            moving = self.filtered(
                lambda r: r.confidence == "verified"
                and r.canonical_value != vals["canonical_value"]
            )
            if moving and vals.get("confidence", "verified") == "verified":
                raise UserError(
                    "%s -> %s is verified. Mark it disputed before re-pointing it."
                    % (moving[0].source_value, moving[0].canonical_value)
                )
        return super().write(vals)


class FixPaymentGateway(models.Model):
    """A payment gateway configuration.

    P1-4: putting a gateway live (activation, sandbox->live) is a routed M63
    decision by the coded approver group (extension in cd_multi_entity - this
    module cannot depend on the workflow engine). The base here carries the
    guarded state machine, the audit trail and the checkout assertion.

    A12 finish E13: storefront checkout is the only reader of this register.
    Front-desk bKash, cash position, payment links, billing, subscriptions and
    the storefront's payment callback do not consult it; the callback settles an
    order already placed, so a suspension stops new orders and not settlement.
    """

    _name = "fix.payment.gateway"
    _description = "Payment Gateway Configuration"
    _inherit = ["fix.guarded.mixin", "mail.thread"]
    _order = "provider"
    # `name` is a computed label for the grid and its prompts; it is not searchable.
    _rec_name = "provider"

    name = fields.Char(compute="_compute_name", string="Gateway")
    provider = fields.Char(required=True, help="Razorpay, KBZPay, eSewa, bKash, SSLCOMMERZ…")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    country_code = fields.Char(required=True, default="BD")
    mode = fields.Selection(
        [("sandbox", "Sandbox"), ("live", "Live")], required=True, default="sandbox"
    )
    currencies = fields.Char(required=True, default="BDT")
    credential_ref = fields.Char(
        string="Credential Reference",
        required=True,
        groups="cd_entity_config.group_platform_admin,"
        "cd_entity_config.group_gateway_activation_approver",
        help="Pointer into the secret manager (vault://…). API keys are never stored here "
        "(SEC-101). No integration reads it yet, so rotating it records a decision and "
        "does not by itself change a live secret.",
    )
    pending_credential_ref = fields.Char(
        string="Credential Awaiting Approval",
        readonly=True,
        copy=False,
        groups="cd_entity_config.group_platform_admin,"
        "cd_entity_config.group_gateway_activation_approver",
    )
    pending_credential_reason = fields.Char(string="Rotation Reason", readonly=True, copy=False)
    settlement_cycle_days = fields.Integer(default=2)
    supports_refund = fields.Boolean(default=True)
    supports_partial_refund = fields.Boolean(default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("suspended", "Suspended")],
        required=True,
        default="draft",
        tracking=True,
    )
    active = fields.Boolean(default=True)

    _provider_unique = models.Constraint(
        "UNIQUE (provider, country_code, company_id)", "A provider is configured once per country"
    )

    @api.depends("provider", "country_code")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s (%s)" % (rec.provider or "-", rec.country_code or "-")

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "state",
            "mode",
            "credential_ref",
            "pending_credential_ref",
            "pending_credential_reason",
        }
        # P1-4 pinning: the provider identity and its currencies are the contract
        # the approval covered. A12 finish E5: pinned in EVERY state but draft,
        # `active` included. Suspended was the hole: checkout looks the rail up by
        # provider, so renaming or archiving a suspended rail reopened it.
        if self and any(rec.state != "draft" for rec in self):
            guarded |= {"provider", "country_code", "currencies", "active"}
        return guarded

    def _fix_form_locked_fields(self) -> set:
        # A12 finish E8: a NEW gateway must be able to state its vault reference,
        # or + New can never save. It enters at creation; afterwards Rotate.
        locked = super()._fix_form_locked_fields()
        return locked if self else locked - {"credential_ref"}

    def unlink(self):
        # A12 finish E5: deleting a live row left no trace and made checkout treat
        # the rail as unconfigured. Only a draft, which never took money, goes.
        if not self.env.su:
            kept = self.filtered(lambda rec: rec.state != "draft")
            if kept:
                raise UserError(
                    "Only a draft gateway can be deleted: %s has been activated, and its "
                    "record is the audit trail. Suspend it instead."
                    % ", ".join(kept.mapped("provider"))
                )
        self._audit_log("payment.gateway_deleted", "draft gateway deleted")
        return super().unlink()

    @api.model_create_multi
    def create(self, vals_list):
        """Birth configuration, not a forged transition.

        A gateway is born draft and in sandbox mode — those are the only
        state/mode values create accepts (going live is the routed
        activation approval). The initial credential reference is set by
        whoever configures the draft, so it enters here through the
        transition token, the same path the rotation action uses: no code
        path ever writes it outside that path."""
        for vals in vals_list:
            if vals.get("state", "draft") != "draft" or vals.get("mode", "sandbox") != "sandbox":
                raise UserError(
                    "A gateway is created as a draft in sandbox mode; putting one "
                    "live is the routed activation approval from the approver's inbox."
                )
            vals.setdefault("state", "draft")
            vals.setdefault("mode", "sandbox")
        # with_env: hand back records on the CALLER's env — the token used for
        # the birth write must not leak into the returned recordset.
        return super(FixPaymentGateway, self._guarded()).create(vals_list).with_env(self.env)

    @api.model
    def _vault_namespaces(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(VAULT_NAMESPACES_PARAM, "")
        return [part.strip() for part in raw.split(",") if part.strip()]

    def _assert_vault_namespace(self, new_ref):
        """A12 finish E8: the configured allow-list; unset, a non-draft gateway
        stays in the namespace it was approved in, so one person cannot point a
        rail at a path they control."""
        self.ensure_one()
        allowed = self._vault_namespaces()
        if not allowed and self.state == "draft":
            return
        if not allowed:
            current = self.sudo().credential_ref or ""
            allowed = [current.rsplit("/", 1)[0] + "/"]
        if not any(new_ref.startswith(prefix) for prefix in allowed):
            raise UserError(
                "%s is outside the vault namespace allowed for this gateway (%s). "
                "The allow-list is ir.config_parameter %s."
                % (new_ref, ", ".join(allowed), VAULT_NAMESPACES_PARAM)
            )

    @api.constrains("credential_ref")
    def _check_credential_ref(self):
        allowed = self._vault_namespaces()
        for rec in self.sudo():
            ref = (rec.credential_ref or "").strip()
            if not ref.startswith("vault://"):
                raise UserError(
                    "A gateway must reference the secret manager (vault://…); "
                    "keys must never be entered here"
                )
            if allowed and not any(ref.startswith(prefix) for prefix in allowed):
                raise UserError(
                    "%s is outside the allowed vault namespaces (%s)." % (ref, ", ".join(allowed))
                )

    # ---- audit trail (R5, through B1's log_event) --------------------------
    def _audit_log(self, event, detail):
        for rec in self:
            rec.env["fix.security.audit"].sudo().log_event(
                event,
                "fix.payment.gateway,%d" % rec.id,
                "%s (%s/%s, mode=%s) by %s"
                % (detail, rec.provider, rec.country_code, rec.mode, rec.env.user.name),
            )

    # ---- checkout contract (P1-4) ------------------------------------------
    def assert_live_for_checkout(self, purpose="checkout", country_code=None):
        """Refuse unless this gateway may take a REAL payment: state active,
        mode live, and (when given) serving the country of the sale.

        Called by the storefront's checkout (cd_storefront) with a positional
        purpose string, e.g. assert_live_for_checkout("storefront checkout").
        """
        for rec in self:
            if not rec.active or rec.state != "active" or rec.mode != "live":
                raise UserError(
                    "%s refused: gateway %s (%s) is %s in %s mode. Payments need "
                    "an active gateway switched to live through the routed "
                    "activation approval."
                    % (purpose, rec.provider, rec.country_code, rec.state, rec.mode)
                )
            if country_code and (rec.country_code or "").upper() != (country_code or "").upper():
                raise UserError(
                    "%s refused: gateway %s serves %s, not %s."
                    % (purpose, rec.provider, rec.country_code, country_code)
                )
        return True

    # ---- state machine (P1-4; the ROUTING is added in cd_multi_entity) ------
    def action_activate(self):
        """Guarded transitions only: draft->active (first activation),
        suspended->active (reactivation), active/sandbox->live (go-live).
        Everything else is refused. Each transition writes an audit row.
        A rotation of a live credential is applied here too: it is the same
        routed decision, so the approver's inbox applies it (A12 finish E8)."""
        for rec in self:
            if rec.pending_credential_ref:
                new_ref = rec.pending_credential_ref
                reason = rec.pending_credential_reason
                previous = rec.sudo().credential_ref
                rec._guarded().write(
                    {
                        "credential_ref": new_ref,
                        "pending_credential_ref": False,
                        "pending_credential_reason": False,
                    }
                )
                rec._audit_log(
                    "payment.gateway_credential_rotated",
                    "credential rotated %s -> %s: %s" % (previous, new_ref, reason),
                )
                rec.message_post(body="Credential rotated: %s" % reason)
            elif rec.state == "draft":
                rec._guarded().write({"state": "active"})
                rec._audit_log("payment.gateway_activated", "gateway activated")
                rec.message_post(body="Activated by %s (mode=%s)." % (rec.env.user.name, rec.mode))
            elif rec.state == "suspended":
                rec._guarded().write({"state": "active"})
                rec._audit_log("payment.gateway_reactivated", "suspended gateway reactivated")
                rec.message_post(body="Reactivated by %s." % rec.env.user.name)
            elif rec.state == "active" and rec.mode == "sandbox":
                rec._guarded().write({"mode": "live"})
                rec._audit_log("payment.gateway_gone_live", "sandbox switched to live")
                rec.message_post(body="Switched to LIVE by %s." % rec.env.user.name)
            else:
                raise UserError(
                    "Gateway %s is already %s in %s mode: nothing to activate."
                    % (rec.provider, rec.state, rec.mode)
                )

    def action_suspend(self, reason=None):
        for rec in self:
            if rec.state != "active":
                raise UserError(
                    "Only an active gateway can be suspended (%s is %s)."
                    % (rec.provider, rec.state)
                )
            if not (reason or "").strip():
                raise UserError("Suspending a payment gateway needs a reason.")
            _require_gateway_authority(self.env, "Suspending a payment gateway")
            rec._guarded().write({"state": "suspended"})
            rec._audit_log("payment.gateway_suspended", "suspended: %s" % reason)
            rec.message_post(body="Suspended by %s: %s" % (rec.env.user.name, reason))

    def _route_live_rotation(self):
        """The routed approval of a live rotation lives in cd_multi_entity."""
        raise UserError(
            "Rotating the credential of a live gateway needs the routed approval "
            "(cd_multi_entity), which is not installed."
        )

    def action_rotate_credential(self, new_ref=None, reason=None):
        """Point the gateway at a NEW vault entry. The old secret is not
        touched here - it is revoked in the vault by the rotation run.

        A12 finish E8: on a LIVE gateway this only requests the rotation; a
        different person in the approver group applies it from the inbox. A
        draft, sandbox or suspended rail takes no money and its next go-live
        approval covers the new reference, so those rotate directly."""
        for rec in self:
            _require_gateway_authority(self.env, "Rotating gateway credentials")
            new_ref = (new_ref or "").strip()
            reason = (reason or "").strip()
            if not new_ref.startswith("vault://"):
                raise UserError(
                    "The new credential reference must point into the secret "
                    "manager (vault://…); keys are never entered here."
                )
            if not reason:
                raise UserError("Rotating a gateway credential needs a reason.")
            rec._assert_vault_namespace(new_ref)
            if rec.state == "active" and rec.mode == "live":
                rec._guarded().write(
                    {"pending_credential_ref": new_ref, "pending_credential_reason": reason[:250]}
                )
                rec._audit_log(
                    "payment.gateway_credential_rotation_requested",
                    "rotation to %s requested: %s" % (new_ref, reason),
                )
                rec._route_live_rotation()
                continue
            previous = rec.sudo().credential_ref
            rec._guarded().write({"credential_ref": new_ref})
            rec._audit_log(
                "payment.gateway_credential_rotated",
                "credential rotated %s -> %s: %s" % (previous, new_ref, reason),
            )
            rec.message_post(body="Credential rotated by %s: %s" % (rec.env.user.name, reason))
