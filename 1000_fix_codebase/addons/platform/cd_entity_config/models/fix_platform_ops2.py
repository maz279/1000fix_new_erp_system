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
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_platform_ops import _require_steward_group

GATEWAY_APPROVER_GROUP = "cd_entity_config.group_gateway_activation_approver"
PLATFORM_ADMIN_GROUP = "cd_entity_config.group_platform_admin"


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
    base_url = fields.Char(required=True)
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
        default="live",
    )
    owner_id = fields.Many2one("res.users", string="Owner")
    data_residency = fields.Char(default="BD-Dhaka")
    notes = fields.Char()

    _name_unique = models.Constraint("UNIQUE (name, company_id)", "Environment name is unique")


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

    _version_unique = models.Constraint(
        "UNIQUE (version, company_id)", "A release version is unique per company"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "released_on"}

    def action_release(self):
        for rec in self:
            if rec.state not in ("planned", "in_test"):
                raise UserError("Only a planned or in-test release can be released")
            if not (rec.rollback_plan or "").strip():
                raise UserError("A release must state its rollback plan before it ships")
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
            if change.state not in ("approved", "implemented"):
                raise UserError(
                    "The linked ITSM change %s is %s: a release may only ship an "
                    "approved or implemented change (D8)." % (change.name, change.state)
                )
            rec._guarded().write(
                {"state": "released", "released_on": fields.Date.context_today(rec)}
            )


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
        return super()._fix_guarded_fields() | {
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

    def action_merge(self, justification=None):
        """P1-2: delegate the merge to the supervised engine for the domain.

        res.partner -> M33 fix.party.merge (routed through M63 by M33 itself:
        a steward who is not the creator executes, SOD-15, reversible).
        Any other master -> refused clearly: no supervised merge engine exists
        for it in this build."""
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This candidate pair is already decided")
            _require_steward_group(self.env, "Merging a duplicate candidate")
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
            survivor = rec._resolve_party(rec.survivor_ref or rec.record_a_ref)
            victim = rec._resolve_party(rec.record_b_ref)
            if survivor == victim:
                raise UserError("The survivor and the victim are the same record.")
            merge = self.env["fix.party.merge"].create(
                {
                    "survivor_id": survivor.id,
                    "victim_id": victim.id,
                    "company_id": rec.company_id.id,
                }
            )
            # M33 carries its own M63 routing, SOD-15 and reversal; the
            # physical merge happens when the routed steward executes it.
            merge.action_request_approval(justification=justification)
            rec._guarded().write({"party_merge_id": merge.id, "survivor_ref": str(survivor.id)})
            rec.message_post(
                body=(
                    "Merge delegated to M33 supervised merge %s (survivor %s, "
                    "victim %s) by %s: the pair merges when the routed steward "
                    "executes it."
                    % (merge.id, survivor.display_name, victim.display_name, self.env.user.name)
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

    def action_keep_separate(self):
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This candidate pair is already decided")
            _require_steward_group(self.env, "Deciding a duplicate candidate")
            rec._guarded().write(
                {
                    "decision": "kept_separate",
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )


class FixMdmXref(models.Model):
    _name = "fix.mdm.xref"
    _description = "Cross-Reference Mapping"
    _order = "code_list, source_value"

    code_list = fields.Char(string="Code List / Domain", required=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    source_system = fields.Char(required=True)
    source_value = fields.Char(required=True)
    canonical_value = fields.Char(required=True)
    canonical_label = fields.Char()
    confidence = fields.Selection(
        [("verified", "Verified"), ("inferred", "Inferred"), ("disputed", "Disputed")],
        required=True,
        default="verified",
    )
    active = fields.Boolean(default=True)

    _xref_unique = models.Constraint(
        "UNIQUE (code_list, source_system, source_value, company_id)",
        "A source value maps once per domain and system",
    )


class FixPaymentGateway(models.Model):
    """A payment gateway configuration.

    P1-4: putting a gateway live (activation, sandbox->live) is a routed M63
    decision by the coded approver group (extension in cd_multi_entity - this
    module cannot depend on the workflow engine). The base here carries the
    guarded state machine, the audit trail and the checkout assertion.
    """

    _name = "fix.payment.gateway"
    _description = "Payment Gateway Configuration"
    _inherit = ["fix.guarded.mixin", "mail.thread"]
    _order = "provider"

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
        help="Pointer into the secret manager (vault://…). API keys are never stored here (SEC-101).",
    )
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

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {"state", "mode", "credential_ref"}
        # P1-4 pinning: once the gateway is live, the provider identity and
        # its currencies are the contract the approval covered.
        if self and any(rec.state == "active" for rec in self):
            guarded |= {"provider", "country_code", "currencies"}
        return guarded

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self[:1].state != "draft":
            locked |= {"credential_ref", "mode"}
        return locked

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

    @api.constrains("credential_ref")
    def _check_credential_ref(self):
        for rec in self:
            if not (rec.credential_ref or "").strip().startswith("vault://"):
                raise UserError(
                    "A gateway must reference the secret manager (vault://…); "
                    "keys must never be entered here"
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
            if rec.state != "active" or rec.mode != "live":
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
        Everything else is refused. Each transition writes an audit row."""
        for rec in self:
            if rec.state == "draft":
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

    def action_rotate_credential(self, new_ref=None, reason=None):
        """Point the gateway at a NEW vault entry. The old secret is not
        touched here - it is revoked in the vault by the rotation run."""
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
            previous = rec.credential_ref
            rec._guarded().write({"credential_ref": new_ref})
            rec._audit_log(
                "payment.gateway_credential_rotated",
                "credential rotated %s -> %s: %s" % (previous, new_ref, reason),
            )
            rec.message_post(body="Credential rotated by %s: %s" % (rec.env.user.name, reason))
