# S10 — the shared step-advance engine (A03 gap-plan Part IV, service S10).
#
# WHY this is a platform mixin and not two implementations. The gap plan
# requires a runtime that walks members through ordered steps for TWO
# features that Microsoft ships separately but builds the same way:
#   * M35 marketing journeys (Customer Insights – Journeys), which walk a
#     res.partner through sends, waits and branches;
#   * M07 sales sequences (Sales acceleration cadences), which walk a
#     crm.lead through calls, e-mails and visits.
# cd_campaign and cd_crm_ext are siblings and cannot import each other, so a
# shared engine has to live in a module they both already depend on. This one
# does (both depend on cd_entity_config), which is also where the DOFA mixin
# lives — the same reasoning.
#
# WHAT IS SHARED is the hard part: finding members that are due, the
# per-member savepoint so one bad member cannot roll back the batch, the
# eligibility re-check before every step, the wait arithmetic, the state
# machine and its terminal transitions, and the loop guard. WHAT IS NOT
# shared is what a step DOES — the concrete flow implements
# _runtime_execute_step(), because sending a WhatsApp template and logging a
# sales call have nothing in common.
#
# The eligibility re-check deserves its own note, because it is the design
# constraint the November 2026 D365 research turned up and it has to be in
# the engine rather than in each flow. Microsoft is shipping edit-and-
# republish of a segment already in use by a LIVE journey, with additions
# applied in real time. If segment membership can change mid-journey then no
# step may trust the launch-time snapshot: membership and consent must be
# re-evaluated at EXECUTION time, every step, or a party who withdrew consent
# after step 1 still receives step 3. Putting the hook here means a flow
# cannot forget it.
from odoo import fields, models

# A member that somehow stops advancing must not be walked forever. Each
# member carries its own step counter and is failed out past this bound,
# which turns a mis-authored flow (a branch that points back at itself) into
# one failed member with a stated reason instead of an infinite cron.
MAX_STEPS_PER_MEMBER = 500

# How many steps one member may execute in a single cron pass. A chain of
# zero-wait steps should run to its next wait in one go — a member should not
# need five cron ticks to get through "branch, tag, send" — but an unbounded
# inner loop would let one member starve the batch.
MAX_STEPS_PER_PASS = 20


class FixStepRuntimeMixin(models.AbstractModel):
    """The step-advance engine. Mixed into a FLOW model (journey, sequence).

    A concrete flow must provide:

        _runtime_member_model     str  — the member/enrolment model name
        _runtime_member_flow_field str — the m2o on the member pointing here

        _runtime_ordered_steps()           -> step recordset, in order
        _runtime_current_step(member)      -> step record or empty
        _runtime_set_step(member, step)    -> None
        _runtime_execute_step(member, step) -> outcome dict

    and may override:

        _runtime_member_still_eligible(member) -> (bool, reason)

    The outcome dict returned by _runtime_execute_step:

        action      'next' | 'goto' | 'wait' | 'exit' | 'complete' | 'fail'
        next_step   step record, for 'goto'
        wait_minutes  int, for 'wait' (stay on this step and retry later)
        reason      str, recorded on the member for terminal actions
    """

    _name = "fix.step.runtime.mixin"
    _description = "Step Advance Runtime"

    # --- contract defaults (concrete flows override) ----------------------
    _runtime_member_model = None
    _runtime_member_flow_field = None

    # ---------------------------------------------------------------------
    # Contract hooks
    # ---------------------------------------------------------------------
    def _runtime_ordered_steps(self):
        raise NotImplementedError("%s must implement _runtime_ordered_steps()" % self._name)

    def _runtime_current_step(self, member):
        raise NotImplementedError("%s must implement _runtime_current_step()" % self._name)

    def _runtime_set_step(self, member, step):
        raise NotImplementedError("%s must implement _runtime_set_step()" % self._name)

    def _runtime_execute_step(self, member, step):
        raise NotImplementedError("%s must implement _runtime_execute_step()" % self._name)

    def _runtime_member_still_eligible(self, member):
        """Is this member still entitled to the NEXT step?

        Default: yes. Flows whose audience can change under a running
        instance — any segment-based journey — must override this, and the
        engine calls it before every single step rather than once at
        enrolment.
        """
        return True, ""

    # ---------------------------------------------------------------------
    # Step navigation
    # ---------------------------------------------------------------------
    def _runtime_first_step(self):
        self.ensure_one()
        steps = self._runtime_ordered_steps()
        return steps[:1]

    def _runtime_next_step(self, step):
        """The step after this one in sequence order, or an empty recordset."""
        self.ensure_one()
        steps = list(self._runtime_ordered_steps())
        if not step or step not in steps:
            return self._runtime_first_step()
        index = steps.index(step)
        if index + 1 >= len(steps):
            return step.browse()
        return steps[index + 1]

    # ---------------------------------------------------------------------
    # The driver
    # ---------------------------------------------------------------------
    def _runtime_due_members(self, limit=500):
        """Active members whose next action is due, oldest first."""
        Member = self.env[self._runtime_member_model].sudo()
        domain = [
            ("state", "=", "active"),
            "|",
            ("next_action_at", "=", False),
            ("next_action_at", "<=", fields.Datetime.now()),
        ]
        if self:
            domain.insert(0, (self._runtime_member_flow_field, "in", self.ids))
        return Member.search(domain, order="next_action_at, id", limit=limit)

    def _runtime_advance_due(self, limit=500):
        """Advance every due member. Returns a counted summary.

        One savepoint per member: a flow step that raises leaves that member
        failed with the exception recorded, and the rest of the batch still
        runs. A single shared transaction here would mean one malformed
        template could stop every journey in the estate, which is exactly the
        failure mode a batch runtime must not have.
        """
        members = self._runtime_due_members(limit=limit)
        summary = {
            "considered": len(members),
            "advanced": 0,
            "completed": 0,
            "exited": 0,
            "failed": 0,
            "waiting": 0,
        }
        for member in members:
            flow = member[self._runtime_member_flow_field]
            try:
                with self.env.cr.savepoint():
                    outcome = flow._runtime_advance_one(member)
                    summary[outcome] = summary.get(outcome, 0) + 1
                    if outcome not in ("completed", "exited", "failed", "waiting"):
                        summary["advanced"] += 1
            except Exception as exc:
                member.sudo().write(
                    {
                        "state": "failed",
                        "exit_reason": "Step execution raised: %s" % exc,
                        "exited_at": fields.Datetime.now(),
                        "next_action_at": False,
                    }
                )
                summary["failed"] += 1
        return summary

    def _runtime_advance_one(self, member):
        """Advance ONE member as far as it will go this pass.

        Returns the last outcome category: 'advanced', 'waiting', 'completed',
        'exited' or 'failed'.
        """
        self.ensure_one()
        last = "waiting"
        for _ in range(MAX_STEPS_PER_PASS):
            if member.state != "active":
                return last

            if member.steps_executed >= MAX_STEPS_PER_MEMBER:
                member.sudo().write(
                    {
                        "state": "failed",
                        "exit_reason": "Loop guard: %d steps executed without "
                        "reaching an end. Check the flow for a branch that "
                        "points backwards." % member.steps_executed,
                        "exited_at": fields.Datetime.now(),
                        "next_action_at": False,
                    }
                )
                return "failed"

            eligible, reason = self._runtime_member_still_eligible(member)
            if not eligible:
                member.sudo().write(
                    {
                        "state": "exited",
                        "exit_reason": reason or "No longer eligible for this flow.",
                        "exited_at": fields.Datetime.now(),
                        "next_action_at": False,
                    }
                )
                return "exited"

            step = self._runtime_current_step(member)
            if not step:
                step = self._runtime_first_step()
                if not step:
                    member.sudo().write(
                        {
                            "state": "completed",
                            "exit_reason": "The flow defines no steps.",
                            "exited_at": fields.Datetime.now(),
                            "next_action_at": False,
                        }
                    )
                    return "completed"
                self._runtime_set_step(member, step)

            outcome = self._runtime_execute_step(member, step) or {}
            member.sudo().write({"steps_executed": member.steps_executed + 1})
            action = outcome.get("action", "next")

            if action == "wait":
                minutes = max(1, int(outcome.get("wait_minutes") or 1))
                member.sudo().write(
                    {"next_action_at": fields.Datetime.add(fields.Datetime.now(), minutes=minutes)}
                )
                return "waiting"

            if action == "exit":
                member.sudo().write(
                    {
                        "state": "exited",
                        "exit_reason": outcome.get("reason") or "Exited by a flow step.",
                        "exited_at": fields.Datetime.now(),
                        "next_action_at": False,
                    }
                )
                return "exited"

            if action == "fail":
                member.sudo().write(
                    {
                        "state": "failed",
                        "exit_reason": outcome.get("reason") or "Step failed.",
                        "exited_at": fields.Datetime.now(),
                        "next_action_at": False,
                    }
                )
                return "failed"

            if action == "complete":
                member.sudo().write(
                    {
                        "state": "completed",
                        "exit_reason": outcome.get("reason") or "Reached the end of the flow.",
                        "exited_at": fields.Datetime.now(),
                        "next_action_at": False,
                    }
                )
                return "completed"

            # 'next' and 'goto' both move on; 'goto' names where.
            target = outcome.get("next_step") if action == "goto" else None
            if target is None:
                target = self._runtime_next_step(step)
            if not target:
                member.sudo().write(
                    {
                        "state": "completed",
                        "exit_reason": "Reached the end of the flow.",
                        "exited_at": fields.Datetime.now(),
                        "next_action_at": False,
                    }
                )
                return "completed"
            self._runtime_set_step(member, target)
            # A step that declares its own delay parks the member there; the
            # delay belongs to the step just entered, not the one just run.
            delay = int(getattr(target, "wait_minutes", 0) or 0)
            if delay > 0:
                member.sudo().write(
                    {"next_action_at": fields.Datetime.add(fields.Datetime.now(), minutes=delay)}
                )
                return "advanced"
            member.sudo().write({"next_action_at": fields.Datetime.now()})
            last = "advanced"
        return last


class FixStepMemberMixin(models.AbstractModel):
    """The member-side state machine, shared by journey members and sequence
    enrolments. Only the genuinely common fields live here; which RECORD is
    being walked (a party, a lead) and which step model is in use are
    concrete, because they differ.
    """

    _name = "fix.step.member.mixin"
    _description = "Step Flow Member"

    state = fields.Selection(
        [
            ("active", "Active"),
            ("completed", "Completed"),
            ("exited", "Exited"),
            ("suppressed", "Suppressed"),
            ("failed", "Failed"),
        ],
        required=True,
        default="active",
        index=True,
        tracking=True,
    )
    entered_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    next_action_at = fields.Datetime(
        index=True, help="When the engine should next look at this member."
    )
    exited_at = fields.Datetime(readonly=True)
    exit_reason = fields.Text(
        readonly=True,
        help="Why this member stopped advancing. Always populated on a "
        "terminal state, so a member that went nowhere says why.",
    )
    steps_executed = fields.Integer(
        default=0,
        readonly=True,
        help="Loop guard and audit: how many steps this member has run.",
    )

    def action_pause_member(self, reason=""):
        """Take a member out of the engine without ending their membership."""
        for rec in self:
            if rec.state != "active":
                continue
            rec.write(
                {
                    "state": "suppressed",
                    "exit_reason": reason or "Paused by %s." % self.env.user.name,
                    "next_action_at": False,
                }
            )
        return True

    def action_resume_member(self):
        for rec in self:
            if rec.state != "suppressed":
                continue
            rec.write(
                {
                    "state": "active",
                    "exit_reason": False,
                    "next_action_at": fields.Datetime.now(),
                }
            )
        return True
