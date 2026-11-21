# fix_device_erp — A07 ERP audit (2026-11-20), M17 builder stream S1.
#
# What the registry still let through after the capture passes, and the owner
# decisions D12/D13 (audit_analysis/A07_ERP_AUDIT_DECISIONS_2026-11-20.md):
#
# - M17-22 / D12(b): an "ownership disputed" flag beside the lifecycle state,
#   which holds the device as a lost flag does (no hand-over, no transfer, no
#   release); a Branch Manager other than the flagger clears it.
# - M17-13: an identifier conflict quarantines the devices that share it.
# - M17-11: the purchase date is corrected only by a Warranty Officer, with a
#   reason and the purchase proof.
# - M17-09 / M17-10: scrap, recycling and an approved end-of-life route close
#   the device's open PM plans and 1000FiX cover and publish device.end_of_life.
# - M17-14: the device's custody state (with its owner, in 1000FiX custody,
#   under service, awaiting collection, rented out, in refurbishment, disposed)
#   projected from the custody chain and the modules that hold it, and a
#   dormancy flag (daily job).
# - M17-04 / M17-05 / M17-15: event consumers for the circular-economy flows
#   (trade-in, resale, e-waste, workshop BER) and the timeline of the modules
#   that touch the device.
# - M17-24 (small part, D18): entitlement resolution in priority order.
# - M17-08: device.warranty_updated is published from the warranty itself.
# - LEAD-02: a part consumed on a job for the device becomes its installed
#   component (genealogy), and a returned part is removed again.
import logging
from datetime import datetime, time, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_device import (
    BRANCH_MANAGER_GROUP,
    NOT_SCRAPPABLE,
    WARRANTY_PROOF_TYPES,
    bind_evidence,
    document_from_upload,
)
from .fix_warranty import WARRANTY_OFFICER_GROUP

_logger = logging.getLogger(__name__)

# D13 (spec Q-04): the rework window, one value for every device family.
REWORK_WINDOW_PARAM = "cd_device_registry.rework_window_days"
REWORK_WINDOW_DEFAULT = 30
# FR-AST-045 dormancy: no activity for this many days.
DORMANCY_DAYS_PARAM = "cd_device_registry.dormancy_days"
DORMANCY_DAYS_DEFAULT = 365

CUSTODY_STATES = [
    ("with_owner", "With Its Owner"),
    ("in_custody", "In 1000FiX Custody"),
    ("under_service", "Under Service"),
    ("awaiting_collection", "Awaiting Collection"),
    ("rented_out", "Rented Out"),
    ("in_refurb", "In Refurbishment"),
    ("disposed", "Disposed / Recycled"),
]
# FR-AST-033/034: who pays first when several covers apply (lower is first).
ENTITLEMENT_PRIORITY = {
    "contract": 1,
    "protection_plan": 2,
    "extended": 3,
    "manufacturer": 4,
}


def int_param(env, key, default):
    try:
        return max(int(env["ir.config_parameter"].sudo().get_param(key, default)), 1)
    except (TypeError, ValueError):
        return default


def rework_window_days(env):
    """D13: the rework window (default 30 days)."""
    return int_param(env, REWORK_WINDOW_PARAM, REWORK_WINDOW_DEFAULT)


def _event_record(env, event, model):
    """The aggregate record of an event, re-read as superuser (the payload is
    a claim). Empty when the model is not installed or the row is gone."""
    if model not in env or event.get("aggregate") not in (None, model):
        return None
    try:
        res_id = int(event.get("aggregate_id") or 0)
    except (TypeError, ValueError):
        return None
    rec = env[model].sudo().browse(res_id).exists()
    return rec or None


def _device_of(rec):
    """The fix.device a job, order, reservation or collection is about."""
    if not rec:
        return None
    for path in ("device_id", "order_id.device_id", "service_order_id.device_id"):
        head, _, tail = path.partition(".")
        if head not in rec._fields:
            continue
        value = rec[head]
        if tail:
            if not value or tail not in value._fields:
                continue
            value = value[tail]
        if value and value._name == "fix.device":
            return value.sudo()
    return None


class FixDeviceHistoryRef(models.Model):
    _inherit = "fix.device.history"

    # M17-15: the event a projected row came from, so a redelivery adds nothing.
    event_ref = fields.Char(string="Source Event", index=True, readonly=True)


class FixDeviceErp(models.Model):
    _inherit = "fix.device"

    # ---- M17-22 / D12(b): ownership disputed -------------------------------
    ownership_disputed = fields.Boolean(
        string="Ownership Disputed", readonly=True, copy=False, index=True, tracking=True
    )
    dispute_reason = fields.Char(string="Dispute", readonly=True, copy=False)
    dispute_flagged_by_id = fields.Many2one(
        "res.users", string="Dispute Raised By", readonly=True, copy=False
    )
    dispute_flagged_at = fields.Datetime(string="Dispute Raised At", readonly=True, copy=False)
    dispute_cleared_by_id = fields.Many2one(
        "res.users", string="Dispute Cleared By", readonly=True, copy=False
    )
    dispute_cleared_at = fields.Datetime(string="Dispute Cleared At", readonly=True, copy=False)
    # ---- M17-13: identifier conflict quarantine ----------------------------
    identifier_quarantined = fields.Boolean(
        string="Quarantined (Identifier Conflict)", readonly=True, copy=False, index=True
    )
    quarantine_reason = fields.Char(string="Quarantine Reason", readonly=True, copy=False)
    # ---- M17-14: custody state and dormancy --------------------------------
    custody_state = fields.Selection(
        CUSTODY_STATES,
        string="Custody State",
        default="with_owner",
        readonly=True,
        copy=False,
        index=True,
        help="FR-AST-019: where the device is and who holds it, projected from the custody "
        "chain, service orders, rentals, trade-ins and recycling.",
    )
    custody_party_id = fields.Many2one(
        "res.partner", string="Held By (Party)", readonly=True, copy=False
    )
    custody_branch_id = fields.Many2one(
        "fix.branch", string="Held At (Branch)", readonly=True, copy=False
    )
    custody_reference = fields.Char(string="Custody Reference", readonly=True, copy=False)
    custody_changed_at = fields.Datetime(string="Custody Since", readonly=True, copy=False)
    last_activity_at = fields.Datetime(string="Last Activity", readonly=True, copy=False)
    dormant = fields.Boolean(string="Dormant", readonly=True, copy=False, index=True)
    # ---- M17-11: purchase-date correction, staged on the asset form --------
    purchase_date_correction = fields.Date(string="Corrected Purchase Date", copy=False)
    purchase_date_correction_reason = fields.Char(string="Correction Reason", copy=False)
    purchase_date_proof_document_id = fields.Many2one(
        "fix.document", string="Purchase Proof", copy=False
    )
    purchase_date_proof_file = fields.Binary(string="Upload Purchase Proof", store=False)
    purchase_date_proof_filename = fields.Char(string="Proof File Name", store=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "ownership_disputed",
            "dispute_reason",
            "dispute_flagged_by_id",
            "dispute_flagged_at",
            "dispute_cleared_by_id",
            "dispute_cleared_at",
            "identifier_quarantined",
            "quarantine_reason",
            "custody_state",
            "custody_party_id",
            "custody_branch_id",
            "custody_reference",
            "custody_changed_at",
            "last_activity_at",
            "dormant",
        }

    # ============================================================ M17-07
    def assert_population(self, allowed, what):
        """FR-AST-022: only a device of an allowed population (and one that
        could be handed on at all: not lost, stolen, scrapped, provisional,
        disputed, quarantined or NEIR-blocked) is rented, lent or swapped."""
        for rec in self.sudo():
            if rec.population not in allowed:
                labels = dict(rec._fields["population"].selection)
                raise UserError(
                    "%s is %s and cannot %s: only %s units can."
                    % (
                        rec.display_name,
                        rec._population_label(),
                        what,
                        " or ".join(labels[p] for p in allowed),
                    )
                )
            rec._assert_handable(what)
        return True

    # =================================================================== flags
    def action_flag_disputed(self, reason=None):
        """D12(b): anyone may raise an ownership dispute (holding the device is
        the safe side); it blocks hand-over, transfer and release like a lost
        flag, and every open M01 order of the device is put on hold."""
        if not (reason or "").strip():
            raise UserError("Say who disputes the ownership and on what basis.")
        for rec in self:
            rec.check_access("write")
            if rec.state == "scrapped":
                raise UserError("%s is scrapped." % rec.display_name)
            if rec.ownership_disputed:
                raise UserError("%s is already under an ownership dispute." % rec.display_name)
            rec._guarded().write(
                {
                    "ownership_disputed": True,
                    "dispute_reason": reason.strip(),
                    "dispute_flagged_by_id": self.env.uid,
                    "dispute_flagged_at": fields.Datetime.now(),
                    "dispute_cleared_by_id": False,
                    "dispute_cleared_at": False,
                }
            )
            rec.message_post(
                body="Ownership disputed, raised by %s: %s" % (self.env.user.name, reason.strip())
            )
            rec._publish(
                "device.flagged",
                {
                    "device_id": rec.id,
                    "flag": "disputed",
                    "reason": reason.strip(),
                    "source": "registry",
                    "serial_number": rec.serial_number or None,
                    "imei_1": rec.imei_1 or None,
                    "imei_2": rec.imei_2 or None,
                    "flagged_by": self.env.uid,
                },
            )
        return True

    def action_clear_dispute(self, reason=None):
        """A Branch Manager who did not raise the dispute clears it."""
        if not (reason or "").strip():
            raise UserError("Say how the dispute was settled.")
        for rec in self:
            if not rec.ownership_disputed:
                raise UserError("%s has no ownership dispute." % rec.display_name)
            if not self.env.su and rec.dispute_flagged_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you raised the dispute on %s, so another user "
                    "clears it." % rec.display_name
                )
            rec._assert_role(BRANCH_MANAGER_GROUP, "Clearing an ownership dispute")
            rec._guarded().write(
                {
                    "ownership_disputed": False,
                    "dispute_cleared_by_id": self.env.uid,
                    "dispute_cleared_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Ownership dispute cleared by %s: %s" % (self.env.user.name, reason.strip())
            )
            rec._publish(
                "device.flag_cleared",
                {
                    "device_id": rec.id,
                    "flag": "disputed",
                    "reason": reason.strip(),
                    "restored_state": rec.state,
                    "cleared_by": self.env.uid,
                },
            )
        return True

    def _a07_quarantine(self, reason):
        """M17-13: the devices sharing an identifier are held until the
        Quality Manager resolves the conflict."""
        for rec in self:
            rec._guarded().write({"identifier_quarantined": True, "quarantine_reason": reason})
            rec.message_post(body="Quarantined for an identifier conflict: %s" % reason)

    def _a07_release_quarantine(self):
        """Released once no conflict issue of the device is still open."""
        Issue = self.env["fix.device.quality.issue"].sudo()
        for rec in self.filtered("identifier_quarantined"):
            if Issue.search_count(
                [
                    ("device_id", "=", rec.id),
                    ("issue_type", "=", "conflict"),
                    ("state", "!=", "resolved"),
                ]
            ):
                continue
            rec._guarded().write({"identifier_quarantined": False, "quarantine_reason": False})
            rec.message_post(body="Identifier conflict resolved: quarantine released.")

    # ===================================================== M17-11 purchase date
    def action_correct_purchase_date(
        self,
        value=None,
        reason=None,
        evidence_document_id=None,
        evidence_file=None,
        evidence_filename=None,
    ):
        """Correct a recorded purchase date: a Warranty Officer, with a reason
        and the purchase proof (filed on this device). With no arguments it
        takes the correction staged on the asset form."""
        self.ensure_one()
        if not self.env.su and not self.env.user.has_group(WARRANTY_OFFICER_GROUP):
            raise UserError("Only a Warranty Officer corrects a device's purchase date.")
        value = value or self.purchase_date_correction
        reason = (reason or self.purchase_date_correction_reason or "").strip()
        try:
            day = fields.Date.to_date(value)
        except (TypeError, ValueError) as exc:
            raise UserError("Give the corrected purchase date as YYYY-MM-DD.") from exc
        if not day:
            raise UserError("Give the corrected purchase date.")
        if day > self._dhaka_today():
            raise UserError("A purchase date cannot be in the future (%s)." % day)
        if not reason:
            raise UserError("Give the reason the purchase date is corrected.")
        evidence = self.env["fix.document"]
        if evidence_file:
            evidence = document_from_upload(
                self.env,
                self,
                evidence_file,
                (evidence_filename or "").strip(),
                "invoice",
                "Purchase proof - %s" % self.display_name,
                self._name,
                self.id,
            )
        elif evidence_document_id:
            evidence = evidence.browse(int(evidence_document_id))
        else:
            evidence = self.purchase_date_proof_document_id
        if not evidence and not self.env.su:
            raise UserError("Attach the purchase receipt or invoice that shows the date.")
        if evidence:
            bind_evidence(evidence, [self], "purchase proof", WARRANTY_PROOF_TYPES)
        old = self.purchase_date
        self._guarded().write(
            {
                "purchase_date": day,
                "purchase_date_correction": False,
                "purchase_date_correction_reason": False,
                "purchase_date_proof_document_id": False,
            }
        )
        self.message_post(
            body="Purchase date corrected from %s to %s by %s: %s (proof: %s)"
            % (old or "(empty)", day, self.env.user.name, reason, evidence.sudo().name or "-")
        )
        return True

    # ====================================================== M17-09 / M17-10
    def _a07_close_for_end_of_life(self, reason, route, decision=None):
        """AUT-AST-17: the device's open PM plans pause, its open 1000FiX
        cover lapses (a manufacturer warranty is the brand's to honour or not),
        and M08/M09/M14/M18 are told by device.end_of_life."""
        for rec in self.sudo():
            plans = (
                self.env["fix.device.pm"]
                .sudo()
                .search([("device_id", "=", rec.id), ("state", "=", "active")])
            )
            plans._guarded().write({"state": "paused"})
            cover = rec.warranty_id.filtered(lambda w: w.status in ("active", "pending"))
            if route in ("scrapped", "recycled", "dispose"):
                lapsing = cover
            else:
                lapsing = cover.filtered(lambda w: w.warranty_type == "extended")
            lapsing._a07_lapse("Closed at end of life: %s." % reason)
            rec._publish(
                "device.end_of_life",
                {
                    "device_id": rec.id,
                    "route": route,
                    "reason": reason,
                    "decision_id": decision.id if decision else None,
                    "approver_id": decision.decided_by_id.id if decision else self.env.uid,
                    "population": rec.population,
                    "owner_id": rec.owner_id.id or None,
                    "paused_plan_ids": plans.ids,
                    "lapsed_warranty_ids": lapsing.ids,
                },
            )

    # ============================================================ M17-14
    def _a07_set_custody(self, state, party=None, branch=None, reference=None):
        """Project the device's custody state (service code only)."""
        now = fields.Datetime.now()
        for rec in self.sudo():
            vals = {
                "custody_state": state,
                "custody_party_id": party.id if party else False,
                "custody_branch_id": branch.id if branch else False,
                "custody_reference": reference or False,
                "last_activity_at": now,
                "dormant": False,
            }
            if rec.custody_state != state:
                vals["custody_changed_at"] = now
            rec._guarded().write(vals)

    def add_history(
        self,
        event_type: str,
        description: str,
        order_id=None,
        event_ref=None,
        branch_id=None,
        technician_id=None,
    ):
        """M17-15: the projected timeline row, idempotent per source event,
        with its branch and technician; every row is activity (dormancy)."""
        History = self.env["fix.device.history"].sudo()
        if event_ref and History.search_count(
            [("device_id", "=", self.id), ("event_ref", "=", event_ref)]
        ):
            return False
        super().add_history(event_type, description, order_id=order_id)
        row = History.search([("device_id", "=", self.id)], order="id desc", limit=1)
        extra = {
            k: v
            for k, v in (
                ("event_ref", event_ref),
                ("branch_id", branch_id),
                ("technician_id", technician_id),
            )
            if v
        }
        if extra:
            row._guarded().write(extra)
        self.sudo()._guarded().write({"last_activity_at": fields.Datetime.now(), "dormant": False})
        return row

    @api.model
    def cron_dormancy_sweep(self):
        """FR-AST-045 (ir_cron_device_dormancy, daily): a device with no
        activity (history, custody, order) for the dormancy period is marked
        dormant; activity clears the mark. Idempotent; superuser-safe."""
        days = int_param(self.env, DORMANCY_DAYS_PARAM, DORMANCY_DAYS_DEFAULT)
        today = self._dhaka_today()
        cutoff = datetime.combine(today - timedelta(days=days), time.min)
        Device = self.sudo().with_context(active_test=True)
        stale = Device.search(
            [
                ("dormant", "=", False),
                ("state", "not in", ("scrapped",)),
                "|",
                ("last_activity_at", "<", cutoff),
                "&",
                ("last_activity_at", "=", False),
                ("create_date", "<", cutoff),
            ]
        )
        stale._guarded().write({"dormant": True})
        return len(stale)

    # ======================================================= M17-24 (small)
    def resolve_entitlements(self, on_date=None):
        """FR-AST-033/034: every cover that applies on `on_date`, in the order
        it pays: an in-force M08 contract that covers the device, an active M09
        protection plan of the current owner, 1000FiX extended cover, then the
        manufacturer's. A flagged, scrapped, provisional or quarantined device
        has none."""
        self.ensure_one()
        device = self.sudo()
        day = on_date or self._dhaka_today()
        if (
            device.state in NOT_SCRAPPABLE
            or device.state == "provisional"
            or device.identifier_quarantined
        ):
            return []
        found = []
        if "fix.contract" in self.env:
            Contract = self.env["fix.contract"].sudo()
            for contract in Contract.search(
                [
                    ("covered_device_ids", "in", device.ids),
                    ("state", "in", ("active", "expiring")),
                    ("date_start", "<=", day),
                    ("date_end", ">=", day),
                ]
            ):
                found.append(("contract", contract, contract.display_name))
        if "fix.protection.policy" in self.env:
            Policy = self.env["fix.protection.policy"].sudo()
            for policy in Policy.search(
                [("device_id", "=", device.id), ("state", "=", "active")]
            ).filtered(
                lambda p: (not p.term_start or p.term_start <= day)
                and (not p.term_end or p.term_end >= day)
                and (not p.waiting_until or p.waiting_until <= day)
                and p.partner_id.commercial_partner_id == device.owner_id.commercial_partner_id
            ):
                found.append(("protection_plan", policy, policy.display_name))
        for warranty in device.warranty_id.filtered(
            lambda w: w.status == "active"
            and w.start_date
            and w.end_date
            and w.start_date <= day <= w.end_date
        ):
            kind = "extended" if warranty.warranty_type == "extended" else "manufacturer"
            found.append((kind, warranty, warranty.display_name))
        found.sort(key=lambda f: (ENTITLEMENT_PRIORITY[f[0]], f[1].id))
        return [
            {
                "source": kind,
                "priority": ENTITLEMENT_PRIORITY[kind],
                "model": rec._name,
                "id": rec.id,
                "label": label,
            }
            for kind, rec, label in found
        ]

    # ======================================================== event consumers
    def _system_population(self, target, reason_code, notes):
        self.ensure_one()
        if self.population == target or self.state == "scrapped":
            return False
        return (
            self.env["fix.device.population.change"]
            .sudo()
            ._guarded()
            .create(
                {
                    "device_id": self.id,
                    "to_population": target,
                    "reason_code": reason_code,
                    "notes": notes,
                }
            )
        )

    def _stewardship_note(self, description):
        """A consumer that cannot apply its change says so on the worklist."""
        self.ensure_one()
        self.env["fix.device.quality.issue"].sudo()._guarded().create(
            {
                "device_id": self.id,
                "issue_type": "incomplete",
                "severity": "high",
                "description": description,
            }
        )

    @api.model
    def consume_tradein_collected(self, event):
        """M17-04: a trade-in collected is in 1000FiX's hands: trade-in intake
        population (which also ends the seller's portal transfers), custody,
        timeline. Idempotent."""
        tradein = _event_record(self.env, event, "fix.tradein.request")
        device = _device_of(tradein)
        if not device:
            return False
        device._system_population(
            "trade_in_intake", "trade_in", "Trade-in %s collected" % tradein.name
        )
        device._a07_set_custody("in_refurb", reference=tradein.name)
        device.add_history(
            "other",
            "Trade-in %s: device collected by 1000FiX" % tradein.name,
            event_ref=event.get("event_id"),
        )
        return True

    @api.model
    def consume_tradein_paid(self, event):
        """M17-04: the trade-in purchase is complete: the device belongs to the
        company (the seller loses portal control). A device that cannot change
        owner (a flag, a dispute) goes on the stewardship worklist instead of
        failing the relay for ever."""
        tradein = _event_record(self.env, event, "fix.tradein.request")
        device = _device_of(tradein)
        if not device:
            return False
        company_partner = tradein.company_id.partner_id or self.env.company.partner_id
        if device.owner_id == company_partner:
            return False
        try:
            with self.env.cr.savepoint():
                device.action_transfer_ownership(
                    new_owner_id=company_partner.id,
                    transfer_type="sale",
                    reason="Trade-in %s purchased by 1000FiX" % tradein.name,
                    channel="system",
                )
        except UserError as exc:
            device._stewardship_note(
                "Trade-in %s was paid but the device could not pass to 1000FiX: %s"
                % (tradein.name, exc)
            )
            return False
        device._system_population(
            "trade_in_intake", "trade_in", "Trade-in %s purchased" % tradein.name
        )
        return True

    @api.model
    def consume_ewaste_collected(self, event):
        """M17-04: a customer device handed in for recycling is e-waste pending."""
        item = _event_record(self.env, event, "fix.ewaste.collection")
        device = _device_of(item)
        if not device:
            return False
        device._system_population(
            "ewaste_pending", "ewaste_routing", "E-waste collection %s" % item.name
        )
        device._a07_set_custody("in_custody", reference=item.name)
        device.add_history(
            "other", "E-waste collection %s received" % item.name, event_ref=event.get("event_id")
        )
        return True

    @api.model
    def consume_ewaste_certificate_issued(self, event):
        """M17-04 / M17-09: the M18 disposal certificate ends the device:
        scrapped (trusted path), disposed, plans paused, cover closed."""
        item = _event_record(self.env, event, "fix.ewaste.collection")
        device = _device_of(item)
        if not device or device.state == "scrapped":
            return False
        payload = event.get("payload") or {}
        certificate = payload.get("certificate") or item.display_name
        device._system_population(
            "ewaste_pending", "ewaste_routing", "Recycled under certificate %s" % certificate
        )
        device._guarded().write(
            {
                "state": "scrapped",
                "scrapped_by_id": self.env.uid,
                "scrapped_at": fields.Datetime.now(),
            }
        )
        device.message_post(body="Recycled: M18 disposal certificate %s." % certificate)
        device._a07_set_custody("disposed", reference=certificate)
        device._a07_close_for_end_of_life(
            "recycled under M18 certificate %s" % certificate, route="recycled"
        )
        device.add_history(
            "other",
            "Recycled: M18 disposal certificate %s" % certificate,
            event_ref=event.get("event_id"),
        )
        return True

    @api.model
    def consume_workshop_job_transitioned(self, event):
        """M17-15 timeline row for every M31 job transition; M17-04 a job
        closed beyond economic repair (unrepairable) puts the device at end of
        life and raises a draft end-of-life decision for its Branch Manager."""
        job = _event_record(self.env, event, "fix.workshop.job")
        device = _device_of(job)
        if not device:
            return False
        payload = event.get("payload") or {}
        new_state = payload.get("new_state") or job.state
        device.add_history(
            "repair",
            "Workshop job %s: %s -> %s" % (job.name, payload.get("old_state") or "-", new_state),
            order_id=job.order_id.id if "order_id" in job._fields and job.order_id else None,
            event_ref=event.get("event_id"),
            technician_id=job.technician_id.id
            if "technician_id" in job._fields and job.technician_id
            else None,
        )
        if new_state != "unrepairable":
            return True
        basis = "Beyond economic repair on workshop job %s: %s" % (
            job.name,
            (job.ber_reason if "ber_reason" in job._fields else "") or "-",
        )
        if device.lifecycle_stage in ("active", "vintage"):
            device.action_set_lifecycle_stage("end_of_life", basis)
        Decision = self.env["fix.device.eol.decision"].sudo()
        if not Decision.search_count(
            [("device_id", "=", device.id), ("state", "in", ("draft", "requested"))]
        ):
            Decision._guarded().create(
                {"device_id": device.id, "route": "return_to_customer", "basis": basis}
            )
        return True

    # M17-15: what each activity event writes on the timeline, and the custody
    # state it moves the device to (None: unchanged).
    _ACTIVITY_EVENTS = {
        "field_order.completed": (
            "fix.field.order",
            "service_order",
            "Field visit %s completed",
            None,
        ),
        "workshop.qc.completed": ("fix.workshop.job", "qc", "Workshop QC on job %s", None),
        "rental.delivered": ("fix.rental.reservation", "other", "Rented out on %s", "rented_out"),
        "rental.returned": (
            "fix.rental.reservation",
            "return",
            "Returned from rental %s",
            "in_custody",
        ),
        "tradein.refurbished": ("fix.tradein.request", "repair", "Trade-in %s refurbished", None),
        "tradein.graded": ("fix.tradein.request", "qc", "Trade-in %s graded", None),
    }

    @api.model
    def consume_device_activity(self, event):
        """M17-15: the workshop, field, rental and trade-in modules write the
        device's single timeline (idempotent per event)."""
        spec = self._ACTIVITY_EVENTS.get(event.get("event_type"))
        if not spec:
            return False
        model, event_type, text, custody = spec
        rec = _event_record(self.env, event, model)
        device = _device_of(rec)
        if not device:
            return False
        order = None
        if "service_order_id" in rec._fields and rec.service_order_id:
            order = rec.service_order_id.id
        elif (
            "order_id" in rec._fields and rec.order_id and rec.order_id._name == "fix.service.order"
        ):
            order = rec.order_id.id
        technician = (
            rec.technician_id.id
            if "technician_id" in rec._fields and rec.technician_id._name == "hr.employee"
            else None
        )
        device.add_history(
            event_type,
            text % rec.display_name,
            order_id=order,
            event_ref=event.get("event_id"),
            technician_id=technician,
        )
        if custody:
            party = (
                rec.customer_id
                if custody == "rented_out" and "customer_id" in rec._fields
                else None
            )
            device._a07_set_custody(custody, party=party, reference=rec.display_name)
        return True


class FixWarrantyErp(models.Model):
    _inherit = "fix.warranty"

    def _a07_publish_updated(self, what):
        """M17-08: device.warranty_updated, the event M09's open claims re-check
        on (its consumer was registered and could never fire)."""
        for rec in self:
            rec.device_id._publish(
                "device.warranty_updated",
                {
                    "device_id": rec.device_id.id,
                    "serial_number": rec.device_id.serial_number or None,
                    "brand": rec.device_id.brand_id.name or None,
                    "model": rec.device_id.device_model_id.name or None,
                    "owner_id": rec.device_id.owner_id.id or None,
                    "warranty_id": rec.id,
                    "warranty_type": rec.warranty_type,
                    "status": rec.status,
                    "change": what,
                },
            )

    def _a07_lapse(self, reason):
        """Close open cover without a Warranty Officer: the registry's own
        consequence of a transfer (D12) or the end of the device."""
        for rec in self.sudo():
            if rec.status not in ("active", "pending"):
                continue
            rec._guarded().write({"status": "voided", "void_reason": reason})
            rec.message_post(body=reason)
            rec._a07_publish_updated("lapsed")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._a07_publish_updated("registered")
        return records

    def write(self, vals):
        if not self._fix_guard_open() and "device_id" in vals:
            # M17-20: a receipt uploaded for device A verified cover moved to B.
            for rec in self:
                if rec.proof_document_id and rec._fix_guard_differs(
                    "device_id", vals["device_id"], rec.device_id
                ):
                    raise UserError(
                        "The warranty on %s already carries its proof (%s): it is not moved to "
                        "another device. Register a new warranty there."
                        % (rec.device_id.display_name, rec.proof_document_id.sudo().name)
                    )
        terms = {"device_id", "warranty_type", "start_date", "end_date", "deductible"} & set(vals)
        changed = self.browse()
        if terms and not self.env.context.get("fix_no_warranty_event"):
            changed = self.filtered(
                lambda r: any(r._fix_guard_differs(n, vals[n], r[n]) for n in terms)
            )
        result = super().write(vals)
        changed._a07_publish_updated("terms_changed")
        return result

    def _a07_verify_checks(self):
        # M17-21 / BRU-AST-16: cover is verified only with its derivation basis
        # recorded. A basis left blank is the purchase evidence the officer is
        # checking (verification needs the receipt or card), recorded as such.
        for rec in self:
            if rec.warranty_type != "none" and not rec.derivation_basis:
                if not rec.proof_document_id:
                    raise UserError(
                        "Record how the dates of the warranty on %s were derived (purchase "
                        "evidence, brand lookup or contract) before verification."
                        % rec.device_id.display_name
                    )
                rec.with_context(fix_no_warranty_event=True).write(
                    {"derivation_basis": "purchase_evidence"}
                )
        return super()._a07_verify_checks()

    def action_verify(self):
        result = super().action_verify()
        self._a07_publish_updated("verified")
        return result

    def action_void(self, reason: str = ""):
        result = super().action_void(reason)
        self._a07_publish_updated("voided")
        return result

    def _announce_expired(self):
        super()._announce_expired()
        self._a07_publish_updated("expired")

    @api.model
    def consume_graded_stock_sold(self, event):
        """M17-04 / M17-05: a refurbished unit is resold. The 1000FiX resale
        cover M14 issued (born pending, so it covered nothing) is company
        cover backed by the sale itself: it is made active, verified by the
        system with the contract basis. When the storefront order names the
        buyer, the device passes to the buyer (carrying that cover, D12) and
        leaves 1000FiX's stock. Runs after M14's own consumer (relay order:
        event type, model, method); a cover not yet issued is retried."""
        stock = _event_record(self.env, event, "fix.graded.stock")
        device = _device_of(stock)
        if not device:
            return False
        cover = self.browse()
        if stock.tradein_id and "fix.tradein.warranty" in self.env:
            issued = (
                self.env["fix.tradein.warranty"]
                .sudo()
                .search([("graded_stock_ref", "=", stock.name)], limit=1)
            )
            if not issued:
                raise UserError(
                    "The resale warranty of %s is not issued yet; retried." % stock.name
                )
            cover = issued.device_warranty_id.sudo()
        if cover and cover.status == "pending":
            cover._guarded().write(
                {
                    "status": "active",
                    "verified_by": self.env.uid,
                    "verified_at": fields.Datetime.now(),
                    "derivation_basis": "contract",
                }
            )
            cover.message_post(
                body="Company-issued resale cover on the sale of %s: active from the sale "
                "(no customer receipt is needed for 1000FiX's own cover)." % stock.name
            )
            cover._a07_publish_updated("verified")
        buyer = self.env["res.partner"]
        if "fix.storefront.order.line" in self.env:
            line = (
                self.env["fix.storefront.order.line"]
                .sudo()
                .search([("graded_stock_id", "=", stock.id)], order="id desc", limit=1)
            )
            buyer = line.order_id.customer_id if line else buyer
        if buyer and device.owner_id != buyer:
            device.with_context(fix_m09_warranty_ids=cover.ids).action_transfer_ownership(
                new_owner_id=buyer.id,
                transfer_type="sale",
                reason="Resale of refurbished unit %s" % stock.name,
                channel="system",
            )
            device._a07_set_custody("with_owner", party=buyer, reference=stock.name)
        elif not buyer:
            device._stewardship_note(
                "Refurbished unit %s was sold with no buyer on record: record the ownership "
                "transfer to the buyer." % stock.name
            )
        return True


class FixDeviceComponentErp(models.Model):
    _inherit = "fix.device.component"

    # LEAD-02: the M15 issue the installation came from (idempotency key).
    stock_consumption_id = fields.Integer(
        string="M15 Consumption", index=True, readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"stock_consumption_id"}

    _OWNERSHIP_MAP = {
        "owned": "company_stock",
        "van": "company_stock",
        "bench": "company_stock",
        "consignment": "consignment",
        "customer": "customer_supplied",
        "warranty": "brand_supplied",
    }

    @api.model
    def consume_stock_consumed(self, event):
        """LEAD-02 / FR-AST-027: a part issued (M15) to a service order,
        workshop job or field order of a device is installed in that device:
        part, serial/lot, the job, the technician, the part's own warranty and
        its stock class. Idempotent per consumption."""
        if "fix.stock.consumption" not in self.env:
            return False
        cons = _event_record(self.env, event, "fix.stock.consumption")
        if not cons or cons.state != "consumed" or not cons.job_model:
            return False
        if self.sudo().search_count([("stock_consumption_id", "=", cons.id)]):
            return False
        if cons.job_model not in self.env:
            return False
        job = self.env[cons.job_model].sudo().browse(cons.job_res_id).exists()
        device = _device_of(job)
        if not device:
            return False
        part = cons.product_id.sudo()
        lot = cons.lot_id.sudo()
        installed_on = (
            fields.Date.context_today(
                self.with_context(tz="Asia/Dhaka"), timestamp=cons.consumed_at
            )
            if cons.consumed_at
            else device._dhaka_today()
        )
        vals = {
            "device_id": device.id,
            "part_name": part.display_name or part.part_number or cons.name,
            "part_number": part.part_number or False,
            "serial_no": (lot.name if lot else cons.serial_number) or False,
            "installed_on": installed_on,
            "source_ref": "%s / %s" % (cons.name, cons.service_order_ref),
            "lot_model": "fix.stock.lot",
            "lot_id": lot.id or False,
            "service_order_model": cons.job_model,
            "service_order_id": job.id,
            "technician_id": cons.technician_id.id or False,
            "warranty_until": lot.warranty_until if lot and lot.warranty_until else False,
            "ownership_class": self._OWNERSHIP_MAP.get(cons.ownership_class) or False,
            "stock_consumption_id": cons.id,
            "notes": "Fitted from M15 issue %s (qty %s)" % (cons.name, cons.quantity),
        }
        if vals["warranty_until"] and vals["warranty_until"] < installed_on:
            vals["warranty_until"] = False
        component = self.sudo()._guarded().create(vals)
        device.add_history(
            "repair",
            "Part %s fitted on %s (%s)" % (vals["part_name"], job.display_name, cons.name),
            order_id=job.id if cons.job_model == "fix.service.order" else None,
            event_ref=event.get("event_id"),
            technician_id=cons.technician_id.id or None,
        )
        return component.id

    @api.model
    def consume_stock_returned(self, event):
        """A part returned to stock was not left in the device: its installed
        component is removed (disposition returned to stock is the M15 return)."""
        cons = _event_record(self.env, event, "fix.stock.consumption")
        if not cons:
            return False
        rows = self.sudo().search(
            [("stock_consumption_id", "=", cons.id), ("state", "=", "installed")]
        )
        for row in rows:
            row._guarded().write(
                {
                    "state": "removed",
                    "removed_on": max(row.installed_on, row.device_id._dhaka_today()),
                    "notes": "%s; returned to stock (%s)" % (row.notes or "", cons.name),
                }
            )
        return len(rows)


class FixDeviceCustodyErp(models.Model):
    _inherit = "fix.device.custody"

    # M17-14: what each custody event says about where the device now is.
    _CUSTODY_PROJECTION = {
        "issued": "with_owner",
        "transferred": "with_owner",
        "returned": "in_custody",
        "found": "in_custody",
    }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            state = self._CUSTODY_PROJECTION.get(rec.event)
            if state:
                rec.device_id._a07_set_custody(
                    state,
                    party=rec.to_party_id if state == "with_owner" else None,
                    reference=rec.name,
                )
        return records
