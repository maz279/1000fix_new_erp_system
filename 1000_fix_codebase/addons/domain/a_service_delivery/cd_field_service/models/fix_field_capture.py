# M02 capture audit (2026-11-18): the records six M02 sub-module pages had no
# way to capture, because the records did not exist.
#
# The 13 Nov pass left pages 7 (Offline Sync), 8 (GPS & ETA) and 9 (Field
# Evidence) with no button on purpose - their streams are written by the
# technician app - and page 11 (On-Site Payment) with list buttons only. The
# spec names person-entered records on each of those pages that the estate
# never had:
#
#   page 1  fix.dispatch.decision      FR-FSM-046/047, BRU-FSM-03/04 (H): every
#                                      dispatcher override of the recommendation
#                                      carries a reason code. The board
#                                      dispatched any technician and kept no
#                                      trace of what the engine had ranked first.
#   page 6  fix.technician.device      FR-FSM-064, T-11: devices are enrolled per
#                                      technician and revoked centrally on loss
#                                      or exit. No register existed; a lost phone
#                                      kept syncing.
#   page 7  fix.offline.conflict.review AUT-FSM-06 / FR-FSM-027: a conflicted or
#                                      rejected replay is flagged for supervisor
#                                      review. The journal listed them; nobody
#                                      could record the review.
#   page 8  fix.tracking.pause         FR-FSM-036, BRU-FSM-05 (H): location
#                                      capture is suspended during breaks and off
#                                      duty. Pings were stored whatever the
#                                      technician was doing.
#   page 9  fix.field.visit.exception  FR-FSM-037/038/072, BRU-FSM-09 (H): a
#                                      failed visit (customer absent, no access,
#                                      cannot complete) needs geotagged evidence.
#                                      The order had no such state or record: a
#                                      technician at a locked door could only
#                                      phone the dispatcher.
#   page 11 fix.field.cash.recon       FR-FSM-056, BRU-FSM-07 (H): field cash is
#                                      reconciled daily per technician against
#                                      jobs and hand-overs. The "Daily Cash
#                                      Reconciliation" screen read the BRANCH
#                                      cash shifts; no technician's day was ever
#                                      reconciled.
import json
import math
from datetime import datetime, time, timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_field_order import DISPATCHER_GROUP

LOCAL_TZ = "Asia/Dhaka"
# a failed-visit photo must be taken at the customer's site (BRU-FSM-09)
EVIDENCE_RADIUS_M = 1000.0
# a pause is a break or the end of a duty day, not a way to go dark for days
MAX_PAUSE_HOURS = 14
FINANCE_GROUP = "account.group_account_manager"


def _is_dispatcher(env):
    return env.su or env.user.has_group(DISPATCHER_GROUP)


def _require_dispatcher(env, what):
    if not _is_dispatcher(env):
        raise AccessError(
            "%s is a dispatcher decision. Ask a member of the Field Service Dispatcher group."
            % what
        )


def _own_employee(env):
    return env["hr.employee"].sudo().search([("user_id", "=", env.uid)], limit=1)


def _require_self_or_dispatcher(env, employee, what):
    """The technician themselves, or a dispatcher acting for them."""
    if env.su or _is_dispatcher(env):
        return
    if not employee or employee.sudo().user_id != env.user:
        raise AccessError("%s: only the technician themselves or a dispatcher may." % what)


def _haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def _local_today(env):
    """Today in the user's frame (Dhaka by default) - the same frame as
    ``_local_day_bounds``, so a day's default and its bounds agree."""
    tz = env.context.get("tz") or env.user.tz or LOCAL_TZ
    return fields.Date.context_today(env["res.users"].with_context(tz=tz))


def _local_day_bounds(env, day):
    """The UTC datetimes that bound ``day`` in the user's frame (Dhaka by
    default): a 03:00 Dhaka completion is the previous UTC day."""
    tz = pytz.timezone(env.context.get("tz") or env.user.tz or LOCAL_TZ)
    start = tz.localize(datetime.combine(day, time.min)).astimezone(pytz.utc)
    end = start + timedelta(days=1)
    return start.replace(tzinfo=None), end.replace(tzinfo=None)


def _changed(records, vals, keys):
    """The keys of ``vals`` among ``keys`` that would change a record: the
    workspace form posts back every field it shows, unchanged ones too."""
    out = set()
    for rec in records:
        for key in set(vals) & set(keys):
            field = rec._fields[key]
            old, new = rec[key], vals[key]
            if field.type == "many2one":
                old, new = old.id or False, new or False
            elif field.type == "datetime":
                new = fields.Datetime.to_datetime(new) if new else False
            elif field.type in ("char", "text", "selection"):
                old, new = old or False, new or False
            if old != new:
                out.add(key)
    return out


def _immutable(records, what):
    if not records.env.su:
        raise UserError("%s is a record of what happened; it cannot be edited." % what)


def _ou_vals(env, employee):
    """Company and operating unit taken from the record's technician, as the
    isolation rules expect."""
    emp = employee.sudo()
    return {
        "company_id": (emp.company_id or env.company).id,
        "operating_unit_id": emp.operating_unit_id.id
        if "operating_unit_id" in emp._fields
        else False,
    }


# --------------------------------------------------------------------------
# page 1: Candidate Scoring & Assignment
# --------------------------------------------------------------------------
class FixDispatchDecision(models.Model):
    """One dispatch: what the suggestion engine ranked first, who the
    dispatcher sent, and - when they differ - why (BRU-FSM-04). Creating the
    decision dispatches the order; the record is never edited afterwards."""

    _name = "fix.dispatch.decision"
    _description = "Dispatch Decision"
    _order = "decided_at desc, id desc"
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    field_order_id = fields.Many2one(
        "fix.field.order", string="Field Order", required=True, index=True, ondelete="restrict"
    )
    technician_id = fields.Many2one(
        "hr.employee", string="Technician Sent", required=True, ondelete="restrict"
    )
    recommended_technician_id = fields.Many2one(
        "hr.employee", string="Recommended Technician", readonly=True
    )
    recommended_score = fields.Integer(string="Recommended Score", readonly=True)
    selected_score = fields.Integer(string="Score Of Technician Sent", readonly=True)
    selected_rank = fields.Integer(
        string="Rank Of Technician Sent",
        readonly=True,
        help="1 = the engine's first choice. 0 = not among the ranked candidates.",
    )
    explanation = fields.Text(string="Why The Engine Recommended", readonly=True)
    candidates_json = fields.Text(string="Ranked Candidates (JSON)", readonly=True)
    is_override = fields.Boolean(string="Overrode The Recommendation", readonly=True)
    override_reason = fields.Selection(
        [
            ("customer_preference", "Customer asked for this technician"),
            ("workload_balance", "Balancing workload"),
            ("skill_detail", "Job needs a skill the score does not see"),
            ("proximity_traffic", "Closer in real traffic"),
            ("parts_on_van", "Has the part on the van"),
            ("continuity", "Continuity with an earlier visit"),
            ("other", "Other (explain)"),
        ],
        string="Override Reason",
    )
    override_notes = fields.Text(string="Override Notes")
    decided_by_id = fields.Many2one(
        "res.users", string="Decided By", readonly=True, default=lambda self: self.env.user
    )
    decided_at = fields.Datetime(string="Decided At", readonly=True, default=fields.Datetime.now)
    # A02 ERP audit M02-F10: a reassignment is logged here too, written only by
    # fix.field.order.action_reassign (never from a form).
    decision_type = fields.Selection(
        [("dispatch", "Dispatch"), ("reassign", "Reassignment")],
        string="Decision",
        required=True,
        default="dispatch",
        readonly=True,
    )
    previous_technician_id = fields.Many2one(
        "hr.employee", string="Taken From", readonly=True, ondelete="restrict"
    )

    @api.model
    def _fix_log_reassignment(self, order, technician, previous, reason):
        """The decision record of action_reassign (which checked the dispatcher
        and the reason). Written as the system on the dispatcher's behalf: the
        decided_by is the dispatcher."""
        return self.sudo().create(
            {
                "field_order_id": order.id,
                "technician_id": technician.id,
                "decision_type": "reassign",
                "previous_technician_id": previous.id or False,
                "override_reason": "other",
                "override_notes": reason,
                "decided_by_id": self.env.uid,
            }
        )

    @api.model_create_multi
    def create(self, vals_list):
        _require_dispatcher(self.env, "Dispatching a field order")
        prepared = []
        for vals in vals_list:
            reassign = vals.get("decision_type") == "reassign"
            if reassign and not self.env.su:
                raise UserError(
                    "A reassignment is recorded by Reassign on the field order, not typed in."
                )
            order = self.env["fix.field.order"].browse(vals.get("field_order_id")).exists()
            if not order:
                raise UserError("Choose the field order to dispatch.")
            if reassign:
                if order.state not in ("dispatched", "accepted", "en_route"):
                    raise UserError(
                        "%s is %s: it cannot be reassigned." % (order.name, order.state)
                    )
            elif order.state not in ("draft", "pending_dispatch", "declined"):
                raise UserError(
                    "%s is %s: only an order waiting for dispatch is dispatched here "
                    "(a dispatched order is moved with Reassign)." % (order.name, order.state)
                )
            tech = self.env["hr.employee"].sudo().browse(vals.get("technician_id")).exists()
            if not tech:
                raise UserError("Choose the technician to send.")
            ranked = order.sudo().action_suggest_technicians(limit=20) or []
            top = ranked[0] if ranked else None
            mine = next((r for r in ranked if r["employee_id"] == tech.id), None)
            rank = (ranked.index(mine) + 1) if mine else 0
            override = bool(top) and (not mine or mine["score"] < top["score"])
            reason = vals.get("override_reason") or False
            notes = (vals.get("override_notes") or "").strip()
            if override:
                if not reason:
                    raise UserError(
                        "BRU-FSM-04: %s is not the recommended technician (%s, score %s). "
                        "Give the override reason." % (tech.name, top["name"], top["score"])
                    )
                if reason == "other" and not notes:
                    raise UserError("BRU-FSM-04: say why the recommendation was overridden.")
            elif not reassign:
                reason, notes = False, ""
            else:
                reason = False  # a reassignment keeps its reason in the notes
            vals.update(
                {
                    "recommended_technician_id": top["employee_id"] if top else False,
                    "recommended_score": top["score"] if top else 0,
                    "selected_score": mine["score"] if mine else 0,
                    "selected_rank": rank,
                    "is_override": override,
                    "override_reason": reason,
                    "override_notes": notes or False,
                    "explanation": (
                        "%s, score %s: %s" % (top["name"], top["score"], ", ".join(top["reasons"]))
                        if top
                        else "The engine had no candidate for this order's zone and day."
                    ),
                    "candidates_json": json.dumps(
                        [
                            {k: r.get(k) for k in ("employee_id", "name", "score", "reasons")}
                            for r in ranked[:5]
                        ]
                    ),
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "name": self.env["ir.sequence"].sudo().next_by_code("fix.dispatch.decision")
                    or "/",
                    "company_id": order.company_id.id,
                    "operating_unit_id": order.operating_unit_id.id,
                }
            )
            prepared.append((vals, order, tech))
        records = super().create([v for v, _o, _t in prepared])
        for rec, (_vals, order, tech) in zip(records, prepared, strict=True):
            # the dispatch itself, as the dispatcher: availability, the M22
            # certification gate and the fleet gate all run as on the board.
            # A reassignment is already being carried out by action_reassign.
            if rec.decision_type != "reassign":
                order.action_dispatch(technician_id=tech.id)
            if rec.is_override:
                publish(
                    self.env,
                    "assignment.overridden",
                    "fix.dispatch.decision",
                    rec.id,
                    {
                        "field_order_id": order.id,
                        "recommended_technician_id": rec.recommended_technician_id.id,
                        "selected_technician_id": tech.id,
                        "reason": rec.override_reason,
                        "decided_by": self.env.uid,
                    },
                )
        return records

    def write(self, vals):
        _immutable(self, "A dispatch decision")
        return super().write(vals)


# --------------------------------------------------------------------------
# page 6: Technician Mobile App - device enrolment
# --------------------------------------------------------------------------
class FixTechnicianDevice(models.Model):
    """A phone enrolled to a technician (FR-FSM-064, T-11). Revoking it
    refuses every sync from that device from then on."""

    _name = "fix.technician.device"
    _description = "Technician Device"
    _order = "state, enrolled_at desc, id desc"
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    _rec_name = "device_uid"

    employee_id = fields.Many2one(
        "hr.employee", string="Technician", required=True, index=True, ondelete="restrict"
    )
    device_uid = fields.Char(
        string="Device ID",
        required=True,
        index=True,
        help="The device identifier the technician app sends with every sync.",
    )
    platform = fields.Selection(
        [("android", "Android"), ("ios", "iOS")],
        string="Platform",
        required=True,
        default="android",
    )
    device_model = fields.Char(string="Handset Model")
    app_version = fields.Char(string="App Version")
    state = fields.Selection(
        [("enrolled", "Enrolled"), ("revoked", "Revoked")],
        string="Status",
        required=True,
        default="enrolled",
        readonly=True,
    )
    enrolled_at = fields.Datetime(string="Enrolled At", readonly=True, default=fields.Datetime.now)
    enrolled_by_id = fields.Many2one(
        "res.users", string="Enrolled By", readonly=True, default=lambda self: self.env.user
    )
    revoke_reason = fields.Selection(
        [
            ("lost", "Lost"),
            ("stolen", "Stolen"),
            ("departed", "Technician left"),
            ("replaced", "Replaced by another device"),
            ("compromised", "Compromised"),
        ],
        string="Revoke Reason",
        readonly=True,
    )
    revoke_notes = fields.Text(string="Revoke Notes", readonly=True)
    revoked_at = fields.Datetime(string="Revoked At", readonly=True)
    revoked_by_id = fields.Many2one("res.users", string="Revoked By", readonly=True)
    last_sync_at = fields.Datetime(string="Last Sync", readonly=True)

    _LOCKED = frozenset(
        {
            "employee_id",
            "device_uid",
            "platform",
            "state",
            "enrolled_at",
            "enrolled_by_id",
            "revoke_reason",
            "revoke_notes",
            "revoked_at",
            "revoked_by_id",
        }
    )

    @api.constrains("device_uid", "state")
    def _check_one_enrolment(self):
        for dev in self.filtered(lambda d: d.state == "enrolled"):
            twin = self.sudo().search_count(
                [
                    ("id", "!=", dev.id),
                    ("state", "=", "enrolled"),
                    ("device_uid", "=", dev.device_uid),
                ]
            )
            if twin:
                raise ValidationError(
                    "Device %s is already enrolled. Revoke that enrolment first." % dev.device_uid
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require_dispatcher(self.env, "Enrolling a technician device")
        for vals in vals_list:
            uid = (vals.get("device_uid") or "").strip()
            if not uid:
                raise UserError("Give the device ID the technician app shows.")
            vals["device_uid"] = uid
            emp = self.env["hr.employee"].browse(vals.get("employee_id")).exists()
            if not emp:
                raise UserError("Choose the technician the device belongs to.")
            vals.update(_ou_vals(self.env, emp))
            vals.update(
                {
                    "state": "enrolled",
                    "enrolled_at": fields.Datetime.now(),
                    "enrolled_by_id": self.env.uid,
                }
            )
            for key in ("revoke_reason", "revoke_notes", "revoked_at", "revoked_by_id"):
                vals.pop(key, None)
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su and _changed(self, vals, self._LOCKED):
            raise UserError(
                "A device's owner, ID and status change only by revoking it (and enrolling "
                "the replacement as a new device)."
            )
        return super().write(vals)

    def action_revoke(self, reason=None, notes=None, revoke=None):
        """``revoke`` is the workspace prompt's one string: '<reason> <notes>'."""
        _require_dispatcher(self.env, "Revoking a technician device")
        if revoke not in (None, "", False):
            head, _sep, tail = str(revoke).strip().partition(" ")
            reason, notes = head, tail
        codes = dict(self._fields["revoke_reason"].selection)
        reason = (reason or "").strip()
        if reason not in codes:
            raise UserError("Revoke reason: one of %s." % ", ".join(codes))
        for dev in self:
            if dev.state != "enrolled":
                raise UserError("Device %s is already revoked." % dev.device_uid)
            dev.sudo().write(
                {
                    "state": "revoked",
                    "revoke_reason": reason,
                    "revoke_notes": (notes or "").strip() or False,
                    "revoked_at": fields.Datetime.now(),
                    "revoked_by_id": self.env.uid,
                }
            )
            publish(
                self.env,
                "technician_device.revoked",
                "fix.technician.device",
                dev.id,
                {"employee_id": dev.employee_id.id, "device_uid": dev.device_uid, "reason": reason},
            )

    @api.model
    def _fix_sync_refusal(self, device_uid, employee):
        """Why a sync from ``device_uid`` by ``employee`` is refused, or None.
        A device revoked and not re-enrolled is refused; so is one enrolled to
        another technician. An unknown device is not refused yet: the register
        is being populated (owner decision, M02 audit 2026-11-18)."""
        uid = (device_uid or "").strip()
        if not uid:
            return None
        rows = self.sudo().search([("device_uid", "=", uid)], order="id desc")
        live = rows.filtered(lambda d: d.state == "enrolled")[:1]
        if live:
            if live.employee_id != employee:
                return "device %s is enrolled to another technician" % uid
            live.write({"last_sync_at": fields.Datetime.now()})
            return None
        if rows:
            return "device %s was revoked (%s); ask dispatch to enrol your device" % (
                uid,
                dict(self._fields["revoke_reason"].selection).get(rows[0].revoke_reason, ""),
            )
        return None


# --------------------------------------------------------------------------
# page 7: Offline Sync & Conflict Resolution
# --------------------------------------------------------------------------
class FixOfflineConflictReview(models.Model):
    """A supervisor's review of a replayed command the server rejected or
    applied with a conflict (AUT-FSM-06). The journal entry itself is audit
    evidence and stays untouched."""

    _name = "fix.offline.conflict.review"
    _description = "Offline Conflict Review"
    _order = "reviewed_at desc, id desc"
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    ledger_id = fields.Many2one(
        "fix.offline.idempotency.ledger",
        string="Journal Entry",
        required=True,
        index=True,
        ondelete="restrict",
    )
    technician_id = fields.Many2one(related="ledger_id.technician_id", store=True)
    operation = fields.Char(related="ledger_id.operation", store=True)
    entry_status = fields.Selection(related="ledger_id.status", string="Replay Result", store=True)
    conflict_reason = fields.Text(related="ledger_id.conflict_reason")
    decision = fields.Selection(
        [
            ("server_kept", "Server version stands, technician told"),
            ("redone_on_server", "Action redone on the server"),
            ("data_corrected", "Record corrected"),
            ("escalated", "Escalated (device or app fault)"),
        ],
        string="Decision",
        required=True,
    )
    notes = fields.Text(string="What Was Done", required=True)
    reviewed_by_id = fields.Many2one(
        "res.users", string="Reviewed By", readonly=True, default=lambda self: self.env.user
    )
    reviewed_at = fields.Datetime(string="Reviewed At", readonly=True, default=fields.Datetime.now)

    _ledger_uniq = models.Constraint(
        "UNIQUE (ledger_id)", "This journal entry has already been reviewed."
    )

    @api.model_create_multi
    def create(self, vals_list):
        _require_dispatcher(self.env, "Reviewing an offline sync conflict")
        for vals in vals_list:
            entry = (
                self.env["fix.offline.idempotency.ledger"]
                .sudo()
                .browse(vals.get("ledger_id"))
                .exists()
            )
            if not entry:
                raise UserError("Choose the journal entry to review.")
            if entry.status not in ("rejected", "conflict_applied"):
                raise UserError(
                    "Only a rejected or conflicted replay is reviewed; %s was applied cleanly."
                    % entry.command_id
                )
            if self.sudo().search_count([("ledger_id", "=", entry.id)]):
                raise UserError("Journal entry %s has already been reviewed." % entry.command_id)
            if entry.technician_id.user_id and entry.technician_id.user_id == self.env.user:
                raise AccessError("A technician does not review their own offline command.")
            if not (vals.get("notes") or "").strip():
                raise UserError("Say what was done about the conflict.")
            vals.update(_ou_vals(self.env, entry.technician_id))
            vals.update(
                {
                    "reviewed_by_id": self.env.uid,
                    "reviewed_at": fields.Datetime.now(),
                    "name": self.env["ir.sequence"]
                    .sudo()
                    .next_by_code("fix.offline.conflict.review")
                    or "/",
                }
            )
        return super().create(vals_list)

    def write(self, vals):
        _immutable(self, "A conflict review")
        return super().write(vals)


class FixOfflineLedgerReview(models.Model):
    _inherit = "fix.offline.idempotency.ledger"

    review_ids = fields.One2many("fix.offline.conflict.review", "ledger_id", string="Review")
    review_state = fields.Selection(
        [("na", "No review needed"), ("pending", "Awaiting review"), ("reviewed", "Reviewed")],
        string="Review",
        compute="_compute_review_state",
    )

    @api.depends("status", "review_ids")
    def _compute_review_state(self):
        for entry in self:
            if entry.status == "applied":
                entry.review_state = "na"
            else:
                entry.review_state = "reviewed" if entry.review_ids else "pending"


# --------------------------------------------------------------------------
# page 8: GPS Tracking & ETA - privacy pause
# --------------------------------------------------------------------------
class FixTrackingPause(models.Model):
    """A break or the end of duty: no position is stored while it runs
    (BRU-FSM-05). The technician can see it; a dispatcher can record it for
    them."""

    _name = "fix.tracking.pause"
    _description = "Location Tracking Pause"
    _order = "started_at desc, id desc"
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    employee_id = fields.Many2one(
        "hr.employee",
        string="Technician",
        required=True,
        index=True,
        ondelete="restrict",
        default=lambda self: _own_employee(self.env),
    )
    reason = fields.Selection(
        [
            ("break", "Rest break"),
            ("meal", "Meal"),
            ("prayer", "Prayer"),
            ("personal", "Personal time"),
            ("off_duty", "Off duty (end of day)"),
        ],
        string="Reason",
        required=True,
        default="break",
    )
    started_at = fields.Datetime(string="From", required=True, default=fields.Datetime.now)
    planned_end = fields.Datetime(string="Until", required=True)
    ended_at = fields.Datetime(string="Ended At", readonly=True)
    state = fields.Selection(
        [("active", "Tracking paused"), ("ended", "Tracking resumed")],
        string="Status",
        compute="_compute_state",
    )

    @api.depends("ended_at", "planned_end")
    def _compute_state(self):
        now = fields.Datetime.now()
        for p in self:
            over = p.ended_at or (p.planned_end and p.planned_end <= now)
            p.state = "ended" if over else "active"

    @api.constrains("started_at", "planned_end")
    def _check_window(self):
        for p in self:
            if p.planned_end <= p.started_at:
                raise ValidationError("A pause ends after it starts.")
            if p.planned_end - p.started_at > timedelta(hours=MAX_PAUSE_HOURS):
                raise ValidationError(
                    "A pause is at most %s hours: tracking stops for a break or the end of "
                    "the day, not for days." % MAX_PAUSE_HOURS
                )
            overlap = self.sudo().search_count(
                [
                    ("id", "!=", p.id),
                    ("employee_id", "=", p.employee_id.id),
                    ("ended_at", "=", False),
                    ("started_at", "<", p.planned_end),
                    ("planned_end", ">", p.started_at),
                ]
            )
            if overlap:
                raise ValidationError("%s already has a pause in that window." % p.employee_id.name)

    @api.model_create_multi
    def create(self, vals_list):
        now = fields.Datetime.now()
        for vals in vals_list:
            emp = self.env["hr.employee"].sudo().browse(vals.get("employee_id")).exists()
            if not emp:
                raise UserError("Choose the technician whose tracking pauses.")
            _require_self_or_dispatcher(self.env, emp, "Pausing location tracking")
            start = fields.Datetime.to_datetime(vals.get("started_at")) or now
            # a pause hides the future, never the past: a ping already stored stays
            if start < now - timedelta(minutes=5):
                raise UserError("A pause starts now or later; it cannot hide past positions.")
            vals["started_at"] = max(start, now)
            vals.pop("ended_at", None)
            vals.update(_ou_vals(self.env, emp))
            vals["name"] = self.env["ir.sequence"].sudo().next_by_code("fix.tracking.pause") or "/"
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            changes = _changed(self, vals, set(vals))
            if changes - {"planned_end"}:
                raise UserError(
                    "A pause is ended with End Pause; only its end time can be changed."
                )
            if changes:
                for p in self:
                    _require_self_or_dispatcher(
                        self.env, p.employee_id, "Changing a tracking pause"
                    )
                    if p.state != "active":
                        raise UserError("Pause %s is over." % p.name)
        return super().write(vals)

    def action_end(self):
        now = fields.Datetime.now()
        for p in self:
            _require_self_or_dispatcher(self.env, p.employee_id, "Ending a tracking pause")
            if p.state != "active":
                raise UserError("Pause %s is already over." % p.name)
            p.sudo().write({"ended_at": max(now, p.started_at)})

    @api.model
    def _fix_paused(self, employee_id, at=None):
        at = at or fields.Datetime.now()
        return bool(
            self.sudo().search_count(
                [
                    ("employee_id", "=", employee_id),
                    ("started_at", "<=", at),
                    ("planned_end", ">", at),
                    ("ended_at", "=", False),
                ]
            )
        )


class FixTechnicianLocationPause(models.Model):
    _inherit = "fix.technician.location"

    @api.model
    def record_ping(self, technician_id, lat, lon, *args, **kwargs):
        """BRU-FSM-05: during a pause the position is not stored at all."""
        if self.env["fix.tracking.pause"]._fix_paused(technician_id):
            return False
        return super().record_ping(technician_id, lat, lon, *args, **kwargs)


# --------------------------------------------------------------------------
# page 9: Field Evidence Capture - failed visit
# --------------------------------------------------------------------------
class FixFieldVisitException(models.Model):
    """A visit that could not be done, with geotagged evidence taken at the
    site (BRU-FSM-09). The order goes back to the dispatch queue."""

    _name = "fix.field.visit.exception"
    _description = "Failed Field Visit"
    _order = "recorded_at desc, id desc"
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    field_order_id = fields.Many2one(
        "fix.field.order", string="Field Order", required=True, index=True, ondelete="restrict"
    )
    technician_id = fields.Many2one("hr.employee", string="Technician", readonly=True)
    exception_type = fields.Selection(
        [
            ("customer_absent", "Customer absent"),
            ("no_access", "Access refused / no access"),
            ("cannot_parts", "Cannot complete: parts"),
            ("cannot_access", "Cannot complete: site access"),
            ("cannot_complexity", "Cannot complete: beyond field repair"),
            ("cannot_safety", "Cannot complete: unsafe"),
            ("scope_change", "Scope change: revised estimate needed"),
        ],
        string="What Happened",
        required=True,
    )
    reason = fields.Text(string="Details", required=True)
    follow_up = fields.Selection(
        [
            ("revisit", "Revisit"),
            ("workshop_transfer", "Transfer to the workshop"),
            ("convert_collection", "Convert to pick-up (M03)"),
            ("revised_estimate", "Revised estimate first"),
        ],
        string="Follow-Up",
        required=True,
        default="revisit",
    )
    evidence_photo = fields.Binary(string="Site Photo", required=True, attachment=True)
    evidence_photo_name = fields.Char(string="Photo File Name")
    latitude = fields.Float(string="Latitude", digits=(10, 7), required=True)
    longitude = fields.Float(string="Longitude", digits=(10, 7), required=True)
    distance_from_site_m = fields.Float(string="Distance From Site (m)", readonly=True)
    recorded_by_id = fields.Many2one(
        "res.users", string="Recorded By", readonly=True, default=lambda self: self.env.user
    )
    recorded_at = fields.Datetime(string="Recorded At", readonly=True, default=fields.Datetime.now)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            order = self.env["fix.field.order"].browse(vals.get("field_order_id")).exists()
            if not order:
                raise UserError("Choose the field order the visit was for.")
            if order.state not in ("en_route", "arrived", "in_progress"):
                raise UserError(
                    "%s is %s: a failed visit is recorded by the technician on the way to or "
                    "at the site." % (order.name, order.state)
                )
            # BRU-FSM-09: the technician who was sent records it, with the
            # evidence from the site; nobody files it on their behalf
            order._fix_require_assigned_technician("record a failed visit on")
            if order.onsite_collection_amount:
                raise UserError(
                    "%s already has a collection recorded: a visit that took payment is not a "
                    "failed visit." % order.name
                )
            if not vals.get("evidence_photo"):
                raise UserError("BRU-FSM-09: a failed visit needs a photo taken at the site.")
            try:
                lat = float(vals.get("latitude"))
                lon = float(vals.get("longitude"))
            except (TypeError, ValueError):
                raise UserError("BRU-FSM-09: give the position the photo was taken at.") from None
            if not (-90 <= lat <= 90 and -180 <= lon <= 180) or (lat == 0 and lon == 0):
                raise UserError("BRU-FSM-09: that is not a real position.")
            distance = 0.0
            if order.latitude or order.longitude:
                distance = _haversine_m(lat, lon, order.latitude, order.longitude)
                if distance > EVIDENCE_RADIUS_M:
                    raise UserError(
                        "BRU-FSM-09: the evidence was taken %.0f m from the customer's site; it "
                        "must be taken there (within %.0f m)." % (distance, EVIDENCE_RADIUS_M)
                    )
            if not (vals.get("reason") or "").strip():
                raise UserError("Say what happened at the site.")
            vals.update(
                {
                    "technician_id": order.technician_id.id,
                    "distance_from_site_m": round(distance, 1),
                    "recorded_by_id": self.env.uid,
                    "recorded_at": fields.Datetime.now(),
                    "company_id": order.company_id.id,
                    "operating_unit_id": order.operating_unit_id.id,
                    "name": self.env["ir.sequence"].sudo().next_by_code("fix.field.visit.exception")
                    or "/",
                }
            )
        records = super().create(vals_list)
        for rec in records:
            order = rec.field_order_id
            # back to the dispatch queue for the follow-up the dispatcher
            # arranges; the visit's own times are kept on this record's chatter
            order._guarded().write(
                {
                    "state": "pending_dispatch",
                    "technician_id": False,
                    "dispatched_at": False,
                    "accepted_at": False,
                    "en_route_at": False,
                    "arrived_at": False,
                    "geofence_waived_by": False,
                    "geofence_waive_reason": False,
                }
            )
            order.message_post(
                body="Failed visit %s by %s: %s (%s). Follow-up: %s."
                % (
                    rec.name,
                    rec.technician_id.name,
                    dict(self._fields["exception_type"].selection)[rec.exception_type],
                    rec.reason,
                    dict(self._fields["follow_up"].selection)[rec.follow_up],
                )
            )
            publish(
                self.env,
                "visit.failed",
                "fix.field.visit.exception",
                rec.id,
                {
                    "field_order_id": order.id,
                    "technician_id": rec.technician_id.id,
                    "exception_type": rec.exception_type,
                    "follow_up": rec.follow_up,
                },
            )
        return records

    def write(self, vals):
        _immutable(self, "A failed visit")
        return super().write(vals)


class FixFieldOrderVisits(models.Model):
    _inherit = "fix.field.order"

    visit_exception_ids = fields.One2many(
        "fix.field.visit.exception", "field_order_id", string="Failed Visits"
    )
    failed_visit_count = fields.Integer(
        string="Failed Visits", compute="_compute_failed_visit_count"
    )

    @api.depends("visit_exception_ids")
    def _compute_failed_visit_count(self):
        for rec in self:
            rec.failed_visit_count = len(rec.visit_exception_ids)


# --------------------------------------------------------------------------
# page 11: On-Site Payment - the technician's daily cash reconciliation
# --------------------------------------------------------------------------
class FixFieldCashRecon(models.Model):
    """One technician's field cash for one day (FR-FSM-056, BRU-FSM-07): the
    cash their completed jobs collected, what went to a branch shift, what
    they say they still hold, and a second person's confirmation."""

    _name = "fix.field.cash.recon"
    _description = "Field Cash Reconciliation"
    _order = "recon_date desc, id desc"
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    employee_id = fields.Many2one(
        "hr.employee",
        string="Technician",
        required=True,
        index=True,
        ondelete="restrict",
        default=lambda self: _own_employee(self.env),
    )
    recon_date = fields.Date(
        string="Day", required=True, default=lambda self: _local_today(self.env)
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    order_count = fields.Integer(string="Cash Jobs", readonly=True)
    cash_collected = fields.Monetary(string="Cash Collected", readonly=True)
    cash_handed_over = fields.Monetary(string="Handed To A Branch Shift", readonly=True)
    cash_outstanding = fields.Monetary(string="Still With The Technician", readonly=True)
    counted_amount = fields.Monetary(string="Cash In Hand (Counted)")
    variance = fields.Monetary(string="Variance", readonly=True)
    variance_reason = fields.Text(string="Variance Explanation")
    order_refs = fields.Text(string="Jobs Counted", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("confirmed", "Confirmed")],
        string="Status",
        required=True,
        default="draft",
        readonly=True,
    )
    submitted_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True)
    submitted_at = fields.Datetime(string="Submitted At", readonly=True)
    confirmed_by_id = fields.Many2one("res.users", string="Confirmed By", readonly=True)
    confirmed_at = fields.Datetime(string="Confirmed At", readonly=True)

    _tech_day_uniq = models.Constraint(
        "UNIQUE (employee_id, recon_date)", "This technician's day is already reconciled."
    )

    _FIGURES = (
        "order_count",
        "cash_collected",
        "cash_handed_over",
        "cash_outstanding",
        "variance",
        "order_refs",
        "state",
        "submitted_by_id",
        "submitted_at",
        "confirmed_by_id",
        "confirmed_at",
    )

    def _fix_measure(self):
        """The day's cash jobs, from the field orders themselves.

        A02 ERP audit M02-F13: "still with the technician" counted only the
        jobs completed THAT day, so cash from yesterday's job that never reached
        a drawer vanished from the next day's count. It is now all the
        technician's field cash collected up to the end of the day and not yet
        accepted into a drawer by then (cash_handed_over_at is the cashier's
        acceptance; a declared but unaccepted hand-over is still outstanding)."""
        self.ensure_one()
        start, end = _local_day_bounds(self.env, self.recon_date)
        FieldOrder = self.env["fix.field.order"].sudo()
        cash = [
            ("technician_id", "=", self.employee_id.id),
            ("onsite_payment_method", "=", "cash"),
            ("onsite_collection_amount", ">", 0),
            ("state", "=", "completed"),
        ]
        today = FieldOrder.search(
            [*cash, ("completed_at", ">=", start), ("completed_at", "<", end)],
            order="completed_at, id",
        )
        outstanding = FieldOrder.search(
            [
                *cash,
                ("completed_at", "<", end),
                "|",
                ("cash_handed_over_at", "=", False),
                ("cash_handed_over_at", ">=", end),
            ],
            order="completed_at, id",
        )
        accepted = FieldOrder.search(
            [*cash, ("cash_handed_over_at", ">=", start), ("cash_handed_over_at", "<", end)]
        )
        carried = outstanding - today
        refs = ", ".join(today.mapped("name"))
        if carried:
            refs = "%s%sstill held from earlier days: %s" % (
                refs,
                "; " if refs else "",
                ", ".join(carried.mapped("name")),
            )
        return {
            "order_count": len(today),
            "cash_collected": sum(today.mapped("onsite_collection_amount")),
            "cash_handed_over": sum(accepted.mapped("onsite_collection_amount")),
            "cash_outstanding": sum(outstanding.mapped("onsite_collection_amount")),
            "order_refs": refs or False,
        }

    @api.model_create_multi
    def create(self, vals_list):
        today = _local_today(self.env)
        for vals in vals_list:
            emp = self.env["hr.employee"].sudo().browse(vals.get("employee_id")).exists()
            if not emp:
                raise UserError("Choose the technician whose cash is reconciled.")
            _require_self_or_dispatcher(self.env, emp, "Reconciling field cash")
            day = fields.Date.to_date(vals.get("recon_date")) or today
            if day > today:
                raise UserError("A day is reconciled once it has happened.")
            if self.sudo().search_count([("employee_id", "=", emp.id), ("recon_date", "=", day)]):
                raise UserError("%s's cash for %s is already reconciled." % (emp.name, day))
            vals["recon_date"] = day
            for key in self._FIGURES:
                vals.pop(key, None)
            vals.update(_ou_vals(self.env, emp))
            vals["name"] = (
                self.env["ir.sequence"].sudo().next_by_code("fix.field.cash.recon") or "/"
            )
        records = super().create(vals_list)
        for rec in records:
            rec.sudo().write(rec._fix_measure())
        return records

    def write(self, vals):
        if not self.env.su:
            if set(self._FIGURES) & set(vals):
                raise UserError("The figures come from the jobs; use Submit and Confirm.")
            for rec in self:
                if rec.state != "draft":
                    raise UserError("%s is %s and can no longer change." % (rec.name, rec.state))
                _require_self_or_dispatcher(self.env, rec.employee_id, "Editing a field cash day")
        return super().write(vals)

    def action_submit(self):
        for rec in self:
            _require_self_or_dispatcher(self.env, rec.employee_id, "Submitting field cash")
            if rec.state != "draft":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            if rec.counted_amount is False or rec.counted_amount is None or rec.counted_amount < 0:
                raise UserError("Count the cash in hand first (zero if none).")
            figures = rec._fix_measure()
            variance = round(rec.counted_amount - figures["cash_outstanding"], 2)
            if variance and not (rec.variance_reason or "").strip():
                raise UserError(
                    "BRU-FSM-07: the count differs from the jobs by BDT %.2f. Explain the "
                    "difference before submitting." % variance
                )
            figures.update(
                {
                    "variance": variance,
                    "state": "submitted",
                    "submitted_by_id": self.env.uid,
                    "submitted_at": fields.Datetime.now(),
                }
            )
            rec.sudo().write(figures)

    def action_confirm(self):
        user = self.env.user
        if not (self.env.su or user.has_group(DISPATCHER_GROUP) or user.has_group(FINANCE_GROUP)):
            raise AccessError("Field cash is confirmed by a dispatcher or a finance manager.")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("%s must be submitted before it is confirmed." % rec.name)
            if not self.env.su and user in (rec.submitted_by_id | rec.employee_id.user_id):
                raise AccessError(
                    "BRU-FSM-07: the technician and whoever submitted the count do not confirm it."
                )
            rec.sudo().write(
                {
                    "state": "confirmed",
                    "confirmed_by_id": user.id,
                    "confirmed_at": fields.Datetime.now(),
                }
            )
