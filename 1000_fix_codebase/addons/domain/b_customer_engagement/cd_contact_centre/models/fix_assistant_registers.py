# M32 capture audit (14 Nov 2026): the three registers the spec gives the
# Customer Service Manager, which had no record anywhere.
#
#   fix.assistant.entity            entity definitions (spec 10.1
#                                   fix.entity.definition, FR-CAI-003)
#   fix.assistant.action.authority  the authority matrix (FR-CAI-021/029/030,
#                                   BRU-CAI-03/04/05, spec section 13)
#   fix.assistant.handoff.trigger   the handoff triggers, each independently
#                                   tunable (FR-CAI-036, BRU-CAI-06/07,
#                                   AUT-CAI-04, spec 8.2)
#
# Each register is READ by the running assistant, so a row changes what it
# does: entity definitions drive the entity extraction report, the authority
# matrix is checked before a grounder answers, and the trigger table sets the
# category, priority and supervisor alert of every handoff.
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from libs.py.fix_events import publish  # FF-28

SUPERVISOR_GROUP = "cd_contact_centre.group_cc_supervisor"

# --------------------------------------------------------------------------
# Entity definitions
# --------------------------------------------------------------------------
ENTITY_TYPES = [
    ("order_ref", "Service order reference"),
    ("invoice_ref", "Invoice reference"),
    ("phone", "Phone number"),
    ("imei", "IMEI"),
    ("serial", "Device serial"),
    ("brand", "Brand"),
    ("model", "Model"),
    ("date", "Date"),
    ("time", "Time"),
    ("branch", "Branch name"),
    ("amount", "Amount (BDT)"),
    ("address", "Address"),
    ("other", "Other"),
]
VALIDATIONS = [
    ("none", "None: the pattern is the rule"),
    ("luhn", "Luhn check digit (IMEI)"),
    ("bd_mobile", "Bangladesh mobile number"),
    ("positive_amount", "Positive amount"),
]
# Bengali digits are normalised before matching (FR-CAI-003: "tolerant of
# Bengali numerals"), so one pattern written with [0-9] covers both.
_BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
# A quantified group that is itself quantified - (a+)+, (\d*)* - can take
# exponential time on a crafted message. The pattern runs on every customer
# turn, so it is refused at the point of entry.
_NESTED_QUANTIFIER = re.compile(r"\((?:[^()\\]|\\.)*[+*}]\)\s*[+*{]")
PATTERN_MAX = 300


def _lines(text):
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


def _digits(value):
    return re.sub(r"\D", "", value or "")


def _luhn_ok(value):
    digits = _digits(value)
    if len(digits) != 15:
        return False
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _bd_mobile_ok(value):
    digits = _digits(value)
    if digits.startswith("880"):
        digits = "0" + digits[3:]
    return bool(re.fullmatch(r"01[3-9]\d{8}", digits))


def _positive_amount_ok(value):
    digits = re.sub(r"[^\d.]", "", value or "")
    try:
        return float(digits) > 0
    except ValueError:
        return False


_VALIDATORS = {
    "none": lambda value: True,
    "luhn": _luhn_ok,
    "bd_mobile": _bd_mobile_ok,
    "positive_amount": _positive_amount_ok,
}


class FixAssistantEntity(models.Model):
    """What the assistant extracts from a message, and how.

    A definition is proved before it is saved: every example must extract
    and no counter-example may, so a pattern that silently matches nothing
    (or everything) never reaches the extractor."""

    _name = "fix.assistant.entity"
    _description = "Assistant Entity Definition"
    _inherit = ["mail.thread"]
    _order = "sequence, code"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    sequence = fields.Integer(default=10)
    code = fields.Char(required=True, size=32, tracking=True, help="e.g. imei, order_ref")
    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)")
    entity_type = fields.Selection(ENTITY_TYPES, required=True, default="other", tracking=True)
    pattern = fields.Char(
        required=True,
        tracking=True,
        help="Regular expression, matched case-insensitively after Bengali digits "
        "are normalised to 0-9.",
    )
    validation = fields.Selection(VALIDATIONS, required=True, default="none", tracking=True)
    examples = fields.Text(required=True, help="One message per line; each must extract.")
    counter_examples = fields.Text(help="One message per line; none may extract.")
    example_check = fields.Char(compute="_compute_example_check", string="Examples Proved")
    note = fields.Char()
    active = fields.Boolean(default=True, tracking=True)

    _code_company_unique = models.Constraint(
        "UNIQUE (company_id, code)", "An entity code is defined once per company."
    )

    @api.model
    def _normalise(self, text):
        return (text or "").translate(_BN_DIGITS)

    def _regex(self):
        self.ensure_one()
        return re.compile(self.pattern, re.IGNORECASE)

    def extract(self, text):
        """The validated values this definition finds in a message."""
        self.ensure_one()
        check = _VALIDATORS[self.validation or "none"]
        found = []
        for match in self._regex().finditer(self._normalise(text)):
            value = match.group(0).strip()
            if value and check(value) and value not in found:
                found.append(value)
        return found

    @api.model
    def extract_all(self, text):
        """{code: [values]} for every active definition of the company."""
        out = {}
        for definition in self.search([("company_id", "in", self.env.companies.ids)]):
            values = definition.extract(text)
            if values:
                out[definition.code] = values
        return out

    @api.depends("pattern", "validation", "examples", "counter_examples")
    def _compute_example_check(self):
        for rec in self:
            try:
                rec._regex()
            except (re.error, TypeError):
                rec.example_check = _("The pattern is not a valid regular expression.")
                continue
            ex = _lines(rec.examples)
            cx = _lines(rec.counter_examples)
            hits = sum(1 for line in ex if rec.extract(line))
            false_hits = sum(1 for line in cx if rec.extract(line))
            rec.example_check = _(
                "%(h)s of %(n)s examples extract; %(f)s of %(c)s counter-examples do"
            ) % {
                "h": hits,
                "n": len(ex),
                "f": false_hits,
                "c": len(cx),
            }

    @api.constrains("pattern", "validation", "examples", "counter_examples")
    def _check_definition(self):
        for rec in self:
            pattern = rec.pattern or ""
            if len(pattern) > PATTERN_MAX:
                raise ValidationError(
                    _("A pattern is at most %s characters: it runs on every customer message.")
                    % PATTERN_MAX
                )
            if _NESTED_QUANTIFIER.search(pattern):
                raise ValidationError(
                    _(
                        "The pattern repeats a group that already repeats, e.g. (\\d+)+. "
                        "A crafted message can make that take minutes on every turn. "
                        "Write the repetition once."
                    )
                )
            try:
                regex = rec._regex()
            except re.error as exc:
                raise ValidationError(
                    _("The pattern is not a valid regular expression: %s") % exc
                ) from exc
            if regex.search("") is not None:
                raise ValidationError(
                    _("The pattern matches an empty message, so it would extract nothing real.")
                )
            examples = _lines(rec.examples)
            if not examples:
                raise ValidationError(
                    _("Give at least one example message the pattern must extract.")
                )
            missed = [line for line in examples if not rec.extract(line)]
            if missed:
                raise ValidationError(
                    _("These examples extract nothing with this pattern and validation: %s")
                    % "; ".join(missed[:5])
                )
            wrong = [line for line in _lines(rec.counter_examples) if rec.extract(line)]
            if wrong:
                raise ValidationError(
                    _("These counter-examples extract something, and must not: %s")
                    % "; ".join(wrong[:5])
                )


# --------------------------------------------------------------------------
# Action authority matrix
# --------------------------------------------------------------------------
ACTION_TYPES = [
    ("status_enquiry", "Status enquiry (order, consignment, claim, invoice)"),
    ("service_booking", "Service booking"),
    ("reschedule", "Reschedule an appointment or collection"),
    ("price_quote", "Price quotation (from M11 only)"),
    ("warranty_check", "Warranty check"),
    ("payment_link", "Payment link for an outstanding invoice"),
    ("complaint_capture", "Complaint capture (raised to M34)"),
    ("repair_approval", "Repair approval"),
    ("contract_cancellation", "Contract cancellation"),
    ("refund", "Refund"),
    ("goodwill_credit", "Goodwill credit"),
]
# BRU-CAI-04: these route to a human every time; no row may delegate them.
NEVER_DELEGABLE = frozenset({"contract_cancellation", "refund", "goodwill_credit"})
# BRU-CAI-05 / FR-CAI-030: an action that creates a commitment needs the
# customer's explicit confirmation.
COMMITMENT_ACTIONS = frozenset(
    {"service_booking", "reschedule", "payment_link", "complaint_capture", "repair_approval"}
)
# The transactional intents whose grounder performs or discloses an action.
# branch.locator answers public information and needs no authority.
INTENT_ACTION = {
    "order.status": "status_enquiry",
    "invoice.download": "status_enquiry",
    "repair.price_estimate": "price_quote",
    "appointment.book": "service_booking",
    "complaint.register": "complaint_capture",
}


class FixAssistantActionAuthority(models.Model):
    """What the assistant may do on its own, per action (FR-CAI-029).

    The hard rules are enforced here, not left to whoever fills the matrix:
    cancellations, refunds and goodwill credit are never delegated; nothing
    is done for an unverified customer; a commitment is always confirmed; a
    repair approval needs a limit above which it goes to a person."""

    _name = "fix.assistant.action.authority"
    _description = "Assistant Action Authority Rule"
    _inherit = ["mail.thread"]
    _order = "action_type"
    _rec_name = "action_type"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    action_type = fields.Selection(ACTION_TYPES, required=True, tracking=True)
    assistant_may_perform = fields.Boolean(
        string="Assistant May Perform",
        tracking=True,
        help="Off: the assistant explains the limit and hands the customer to a person.",
    )
    requires_identity = fields.Boolean(
        string="Identity Verification First",
        default=True,
        tracking=True,
        help="BRU-CAI-03: personal data and actions only after the customer is verified.",
    )
    requires_confirmation = fields.Boolean(
        string="Explicit Confirmation First",
        default=True,
        tracking=True,
        help="BRU-CAI-05: restate the action and get a yes before a commitment.",
    )
    approval_limit_bdt = fields.Float(
        string="Approval Limit (BDT)",
        tracking=True,
        help="Repair approval only: above this amount a person approves.",
    )
    never_delegable = fields.Boolean(compute="_compute_kind", store=True)
    commitment = fields.Boolean(compute="_compute_kind", store=True)
    note = fields.Char(string="Why / Owner Note")
    active = fields.Boolean(default=True, tracking=True)

    _action_company_unique = models.Constraint(
        "UNIQUE (company_id, action_type)", "Each action has one authority rule per company."
    )

    @api.depends("action_type")
    def _compute_kind(self):
        for rec in self:
            rec.never_delegable = rec.action_type in NEVER_DELEGABLE
            rec.commitment = rec.action_type in COMMITMENT_ACTIONS

    @api.constrains(
        "action_type",
        "assistant_may_perform",
        "requires_identity",
        "requires_confirmation",
        "approval_limit_bdt",
    )
    def _check_hard_rules(self):
        for rec in self:
            if rec.approval_limit_bdt < 0:
                raise ValidationError(_("An approval limit cannot be negative."))
            if not rec.assistant_may_perform:
                continue
            if rec.action_type in NEVER_DELEGABLE:
                raise ValidationError(
                    _(
                        "BRU-CAI-04: the assistant may never cancel a contract, issue a "
                        "refund or grant goodwill credit. Those always go to a person."
                    )
                )
            if not rec.requires_identity:
                raise ValidationError(
                    _(
                        "BRU-CAI-03: the assistant acts or discloses personal data only "
                        "after the customer's identity is verified."
                    )
                )
            if rec.action_type in COMMITMENT_ACTIONS and not rec.requires_confirmation:
                raise ValidationError(
                    _(
                        "BRU-CAI-05: an action that creates a commitment needs explicit confirmation."
                    )
                )
            if rec.action_type == "repair_approval" and rec.approval_limit_bdt <= 0:
                raise ValidationError(
                    _(
                        "A repair approval the assistant may give needs a limit: above it, "
                        "a person approves (BRU-CAI-04)."
                    )
                )

    @api.model
    def check(self, action_type, identity_verified=False, amount=None):
        """{allowed, reason, rule_id}. No rule recorded keeps today's built-in
        behaviour (allowed=None); a rule always decides."""
        if action_type in NEVER_DELEGABLE:
            return {"allowed": False, "reason": "action_beyond_authority", "rule_id": False}
        rule = self.sudo().search(
            [("action_type", "=", action_type), ("company_id", "in", self.env.companies.ids)],
            limit=1,
        )
        if not rule:
            return {"allowed": None, "reason": "", "rule_id": False}
        if not rule.assistant_may_perform:
            return {"allowed": False, "reason": "action_beyond_authority", "rule_id": rule.id}
        if rule.requires_identity and not identity_verified:
            return {"allowed": False, "reason": "identity_not_verified", "rule_id": rule.id}
        if (
            action_type == "repair_approval"
            and amount is not None
            and amount > rule.approval_limit_bdt
        ):
            return {"allowed": False, "reason": "action_beyond_authority", "rule_id": rule.id}
        return {"allowed": True, "reason": "", "rule_id": rule.id}


# --------------------------------------------------------------------------
# Handoff triggers
# --------------------------------------------------------------------------
SIGNALS = [
    ("frustration", "Frustration detected", "emotional"),
    ("distress", "Distress or vulnerability", "emotional"),
    ("explicit_request", "Customer asked for a human", "emotional"),
    ("abusive", "Abusive or unsafe content", "emotional"),
    ("sla_risk", "SLA at risk", "operational"),
    ("repeat_contact", "Repeat contact", "operational"),
    ("high_value", "High-value customer", "operational"),
    ("contract_entitlement", "Contract entitlement", "operational"),
    ("complaint", "Complaint intent", "operational"),
    ("low_confidence", "Confidence below the intent threshold", "technical"),
    ("guardrail", "Guard rail fired", "technical"),
    ("out_of_scope", "Out of scope", "technical"),
    ("beyond_authority", "Action beyond authority", "technical"),
    ("identity", "Identity not verified", "technical"),
    ("no_retrieval", "Retrieval returned nothing", "technical"),
    ("inference_unavailable", "Inference unavailable", "technical"),
    ("review_required", "Generated answer awaits review", "technical"),
]
SIGNAL_CATEGORY = {code: cat for code, _label, cat in SIGNALS}
CATEGORIES = [
    ("emotional", "Emotional"),
    ("operational", "Operational"),
    ("technical", "Technical"),
]
PRIORITIES = [("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")]
PRIORITY_RANK = {"normal": 0, "high": 50, "urgent": 100}
# BRU-CAI-06 (distress escalates immediately with priority) and BRU-CAI-07
# (an explicit request for a human is honoured immediately): these triggers
# cannot be switched off or lowered below this.
MANDATORY = {"distress": "urgent", "explicit_request": "high"}
# The handoff reasons the assistant writes today, by trigger.
REASON_SIGNAL = {
    "customer_requested_agent": "explicit_request",
    "complaint_escalation": "complaint",
    "low_intent_confidence": "low_confidence",
    "disambiguation_required": "low_confidence",
    "guardrail_blocked": "guardrail",
    "empty_utterance": "out_of_scope",
    "action_beyond_authority": "beyond_authority",
    "identity_not_verified": "identity",
    "grounding_access_denied": "identity",
    "no_grounding_record": "no_retrieval",
    "requires_erp_grounding": "no_retrieval",
    "no_authored_answer": "no_retrieval",
    "no_grounding_source": "no_retrieval",
    "appointment_requires_agent": "beyond_authority",
    "invoice_requires_agent": "beyond_authority",
    "ai_answer_awaiting_review": "review_required",
}


class FixAssistantHandoffTrigger(models.Model):
    """How a handoff of each kind is treated (FR-CAI-036, spec 8.2).

    The category is fixed by the signal (spec 8.2), not typed. A row sets the
    queue priority the conversation gets and whether the supervisors are
    alerted. Distress and an explicit request for a human cannot be weakened.
    """

    _name = "fix.assistant.handoff.trigger"
    _description = "Assistant Handoff Trigger"
    _inherit = ["mail.thread"]
    _order = "category, signal"
    _rec_name = "signal"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    signal = fields.Selection(
        [(c, label) for c, label, _cat in SIGNALS], required=True, tracking=True
    )
    category = fields.Selection(CATEGORIES, compute="_compute_category", store=True)
    mandatory = fields.Boolean(compute="_compute_category", store=True)
    priority = fields.Selection(PRIORITIES, required=True, default="normal", tracking=True)
    notify_supervisor = fields.Boolean(
        string="Alert the Supervisors",
        tracking=True,
        help="Schedules an activity for every Contact Centre Supervisor on the conversation.",
    )
    note = fields.Char(string="Why / Owner Note")
    active = fields.Boolean(default=True, tracking=True)

    _signal_company_unique = models.Constraint(
        "UNIQUE (company_id, signal)", "Each handoff signal has one trigger per company."
    )

    @api.depends("signal")
    def _compute_category(self):
        for rec in self:
            rec.category = SIGNAL_CATEGORY.get(rec.signal) or False
            rec.mandatory = rec.signal in MANDATORY

    @api.constrains("signal", "priority", "active", "notify_supervisor")
    def _check_mandatory(self):
        for rec in self:
            floor = MANDATORY.get(rec.signal)
            if not floor:
                continue
            if not rec.active:
                raise ValidationError(
                    _(
                        "BRU-CAI-06/07: distress and an explicit request for a human always "
                        "hand off. This trigger cannot be switched off."
                    )
                )
            if PRIORITY_RANK[rec.priority] < PRIORITY_RANK[floor]:
                raise ValidationError(
                    _("This trigger escalates with at least %s priority (BRU-CAI-06/07).")
                    % dict(PRIORITIES)[floor]
                )
            if rec.signal == "distress" and not rec.notify_supervisor:
                raise ValidationError(
                    _("AUT-CAI-04: detected distress always alerts the supervisors.")
                )

    def unlink(self):
        if any(rec.signal in MANDATORY for rec in self):
            raise ValidationError(
                _("The distress and explicit-request triggers cannot be deleted (BRU-CAI-06/07).")
            )
        return super().unlink()

    @api.model
    def resolve(self, reason):
        """The trigger behind a handoff reason: signal, category, priority and
        whether to alert. Without a row, the spec's defaults apply."""
        signal = REASON_SIGNAL.get(reason or "") or (reason if reason in SIGNAL_CATEGORY else False)
        out = {
            "signal": signal,
            "category": SIGNAL_CATEGORY.get(signal) or False,
            "priority": MANDATORY.get(signal, "normal"),
            "notify_supervisor": signal == "distress",
            "trigger_id": False,
        }
        if not signal:
            return out
        rule = self.sudo().search(
            [("signal", "=", signal), ("company_id", "in", self.env.companies.ids)], limit=1
        )
        if rule:
            out.update(
                priority=rule.priority,
                notify_supervisor=rule.notify_supervisor,
                trigger_id=rule.id,
            )
        return out


class FixConversationHandoffTrigger(models.Model):
    _inherit = "fix.conversation"

    handoff_signal = fields.Selection(
        [(c, label) for c, label, _cat in SIGNALS], readonly=True, copy=False
    )
    handoff_category = fields.Selection(CATEGORIES, readonly=True, copy=False, index=True)
    handoff_priority = fields.Selection(PRIORITIES, readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        # Set by the handoff from the trigger table, never typed.
        return super()._fix_guarded_fields() | {
            "handoff_signal",
            "handoff_category",
            "handoff_priority",
        }

    def action_handoff_to_agent(self, reason: str = ""):
        res = super().action_handoff_to_agent(reason=reason)
        Trigger = self.env["fix.assistant.handoff.trigger"]
        for conv in self:
            trig = Trigger.with_company(conv.company_id).resolve(reason)
            conv._guarded().write(
                {
                    "handoff_signal": trig["signal"],
                    "handoff_category": trig["category"],
                    "handoff_priority": trig["priority"],
                }
            )
            rank = PRIORITY_RANK.get(trig["priority"], 0)
            item = conv.work_item_id.sudo()
            if item and rank > (item.priority or 0):
                # spec 8.2: "M27 human queue (priority set by trigger)"
                item.write({"priority": rank})
            if trig["notify_supervisor"]:
                conv._alert_supervisors(trig)
            publish(
                self.env,
                "assistant.handoff",
                "fix.conversation",
                conv.id,
                {
                    "reason": reason,
                    "signal": trig["signal"],
                    "category": trig["category"],
                    "priority": trig["priority"],
                    "supervisors_alerted": bool(trig["notify_supervisor"]),
                },
            )
        return res

    def _alert_supervisors(self, trig):
        self.ensure_one()
        group = self.env.ref(SUPERVISOR_GROUP, raise_if_not_found=False)
        users = group.sudo().user_ids.filtered("active")[:20] if group else self.env["res.users"]
        summary = _("Assistant handoff needs a supervisor: %s") % (
            dict(self._fields["handoff_signal"].selection).get(trig["signal"]) or trig["signal"]
        )
        for user in users:
            self.sudo().activity_schedule(
                "mail.mail_activity_data_todo", user_id=user.id, summary=summary
            )
        if not users:
            # nobody holds the role: say so on the record rather than alert no one silently
            self.sudo().message_post(
                body=_("%s. No Contact Centre Supervisor is appointed, so nobody was alerted.")
                % summary
            )

    # FR-CAI-029: the authority matrix is checked before a grounder answers.
    def _ground_intent_response(self, intent, text):
        action = INTENT_ACTION.get(intent or "")
        if action:
            verdict = self.env["fix.assistant.action.authority"].check(
                action, identity_verified=bool(self.customer_id)
            )
            if verdict["allowed"] is False:
                if verdict["reason"] == "identity_not_verified":
                    bn = "আপনার পরিচয় যাচাইয়ের জন্য একজন কাস্টমার কেয়ার প্রতিনিধির সাথে যুক্ত করছি।"
                    en = "Connecting you with a customer care representative to verify your identity."
                else:
                    bn = "এই কাজটি একজন কাস্টমার কেয়ার প্রতিনিধি করবেন। আপনাকে তাঁর সাথে যুক্ত করছি।"
                    en = "A customer care representative handles this. Connecting you now."
                return {"bn": bn, "en": en, "grounded": False, "reason": verdict["reason"]}
        return super()._ground_intent_response(intent, text)


class FixAssistantGuardrailRemoval(models.Model):
    """SOD-20 (spec section 13): the person who authored a guard rail cannot be
    the sole approver of its removal. Switching it off or deleting it is
    done by another supervisor."""

    _inherit = "fix.assistant.guardrail"

    def _check_removal_by_another(self):
        if self.env.su:
            return
        mine = self.filtered(lambda r: r.create_uid == self.env.user)
        if mine:
            raise ValidationError(
                _(
                    "SOD-20: you authored the guard rail '%s', so another supervisor must "
                    "switch it off or delete it."
                )
                % mine[0].name
            )

    def write(self, vals):
        if "active" in vals and not vals["active"]:
            self.filtered("active")._check_removal_by_another()
        return super().write(vals)

    def unlink(self):
        self._check_removal_by_another()
        return super().unlink()


AUTHORITY_REASONS = frozenset({"action_beyond_authority", "identity_not_verified"})


class FixAssistantAuthorityGeneration(models.Model):
    _inherit = "fix.assistant.intent"

    def _generate(self, provider, question, grounded, language):
        # A request the authority matrix refused is not answered some other
        # way: a generated answer would do what the rule just withheld.
        if (grounded or {}).get("reason") in AUTHORITY_REASONS:
            return {
                "ok": False,
                "reason": "The action authority matrix withholds this from the "
                "assistant (%s), so no answer was generated." % grounded["reason"],
                "text": "",
            }
        return super()._generate(provider, question, grounded, language)
