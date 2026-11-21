# fix.workshop.job — the A02 P1/P2 lifecycle repairs (CD-M31-01).
#
# A02 workflow audit (2026-11-03), M31 steps 2-3, 5, 11-12 and the comeback
# row, plus B2 (hand-backs):
#   - book-in: the job recorded no condition, no accessories and no receipt,
#     so a device could be booked in with nothing on file to hand back against.
#     Intake now needs both, copied from the M01 order where it has them, and
#     the book-in is frozen afterwards;
#   - the estimate: the job had no link to what the customer approved, so its
#     cost rose with no re-approval (BRU-WSR-11). The job now shows the
#     governing approved estimate and refuses QC while parts plus labour stand
#     above it;
#   - BER / scrap reaches M01 (the order stayed in_repair) and needs evidence;
#   - workshop.job.delivered is published for the M01 consumer;
#   - a comeback is linked to the repair it comes back from.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

# Book-in (M31 step 2): the receipt fields, frozen once the job is booked in.
BOOKIN_FIELDS = frozenset(
    {
        "bookin_condition",
        "bookin_accessories",
        "bookin_no_accessories",
        "bookin_accessory_bag",
        "bookin_lci_tripped",
        "bookin_photo_attachment_id",
    }
)
BOOKIN_STAMPS = frozenset({"bookin_by_id", "bookin_at"})

# BRU-WSR-11: a job on an order with no approved estimate (a warranty, AMC,
# goodwill or rework job that M01 approved on its entitlement) has no money
# the customer approved. Parts and labour above this cap need a routed
# approval. A control, so it fails closed: unset = 0 BDT.
ZERO_CHARGE_CAP_PARAM = "cd_workshop.zero_charge_parts_cap_bdt"

# The order states from which M01 can follow a BER: action_mark_unrepairable
# (diagnosis, repair) or its own cancellation path with reason 'unrepairable'
# (before repair). M01 has no exit from qc_pending / qc_failed.
ORDER_BER_MARK_STATES = ("diagnostic", "in_repair")
ORDER_BER_CANCEL_STATES = (
    "intake",
    "estimate_pending",
    "estimate_sent",
    "awaiting_approval",
    "approved",
)
# A BER is proposed on what the bench has seen: one of these evidence rows,
# filed against this job, must exist (A02 audit M31 steps 11-12).
BER_EVIDENCE_TYPES = ("pre_repair_photo", "diagnostic_report", "during_repair_photo")

# The context key M31 sets while M01 cancels the order of a job it has just
# closed as BER; the order's cascade then leaves that job as it is.
BER_CLOSING_KEY = "m31_ber_closing"  # gitleaks:allow (a context key, not a secret)


class FixWorkshopJobLifecycle(models.Model):
    _inherit = "fix.workshop.job"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | BOOKIN_STAMPS

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= BOOKIN_FIELDS
        return locked

    # --- book-in (M31 step 2) ---
    bookin_condition = fields.Text(
        string="Condition at Book-In",
        help="Cosmetic and physical condition as received: housing, screen, ports, damage.",
    )
    bookin_accessories = fields.Text(
        string="Accessories Received", help="Charger, cable, case, stylus, SIM tray..."
    )
    bookin_no_accessories = fields.Boolean(
        string="Received Without Accessories",
        help="Tick when the device came with nothing else, so 'none' is on record.",
    )
    bookin_accessory_bag = fields.Char(string="Accessory Bag Barcode")
    bookin_lci_tripped = fields.Boolean(string="Liquid Contact Indicator Tripped")
    bookin_photo_attachment_id = fields.Many2one(
        "ir.attachment", string="Book-In Photo", ondelete="set null"
    )
    bookin_by_id = fields.Many2one("res.users", string="Booked In By", readonly=True, copy=False)
    bookin_at = fields.Datetime(string="Booked In At", readonly=True, copy=False)

    # --- the approved estimate (M31 step 5, BRU-WSR-11) ---
    estimate_id = fields.Many2one(
        "fix.estimate",
        string="Approved Estimate",
        compute="_compute_estimate",
        help="The latest approved version of the order's estimate: what the customer "
        "approved, and what the job's cost is held to.",
    )
    estimate_ceiling = fields.Monetary(
        string="Approved Amount",
        compute="_compute_estimate",
        currency_field="currency_id",
        help="The approved estimate total, or the zero-charge cap when the order was "
        "approved on an entitlement without an estimate.",
    )
    cost_over_estimate = fields.Boolean(
        string="Cost Above Approval",
        compute="_compute_estimate",
        help="Parts consumed (other than approved extra parts) plus labour stand above "
        "the approved amount: re-approval is needed before QC.",
    )

    # --- comeback / warranty-on-repair ---
    is_comeback = fields.Boolean(
        string="Comeback", compute="_compute_is_comeback", store=True, index=True
    )
    comeback_technician_id = fields.Many2one(
        "hr.employee",
        string="Technician of the Prior Repair",
        related="rework_of_id.technician_id",
    )

    @api.depends("rework_of_id")
    def _compute_is_comeback(self):
        for rec in self:
            rec.is_comeback = bool(rec.rework_of_id)

    def _compute_estimate(self):
        for rec in self:
            est, ceiling = rec._m31_cost_ceiling()
            rec.estimate_id = est
            rec.estimate_ceiling = ceiling or 0.0
            rec.cost_over_estimate = ceiling is not None and (
                rec._m31_capped_cost() > ceiling + 0.005
            )

    # --- the cost ceiling ---
    def _m31_governing_estimate(self):
        """The latest approved estimate version of the job's order. Earlier
        approved versions are superseded by a revision: summing them (the P0
        cap did) let v1 inflate the ceiling of v2."""
        self.ensure_one()
        order = self.sudo().order_id
        if not order or "estimate_ids" not in order._fields:
            return self.env["fix.estimate"]
        approved = order.estimate_ids.filtered(lambda e: e.state == "approved")
        return approved.sorted(lambda e: (e.version, e.id))[-1:]

    def _m31_zero_charge_cap(self) -> float:
        raw = self.env["ir.config_parameter"].sudo().get_param(ZERO_CHARGE_CAP_PARAM)
        try:
            return max(0.0, float(raw or 0.0))
        except (TypeError, ValueError):
            return 0.0

    def _m31_cost_ceiling(self):
        """(approved estimate, ceiling in BDT). The ceiling is None only for
        a job with no service order (an internal refurbishment job)."""
        self.ensure_one()
        est = self._m31_governing_estimate()
        if not self.sudo().order_id:
            return est, None
        if est:
            return est, self._m31_estimate_price_ex_vat(est)
        return est, self._m31_zero_charge_cap()

    @api.model
    def _m31_estimate_price_ex_vat(self, est) -> float:
        """A02 pass 2 M31-07 (D14): the cost gate is the approved price WITHOUT
        VAT. The VAT-inclusive total let the job's cost run 15% above what the
        customer pays for the work. M01 pins the approved total (VAT
        inclusive); its VAT share is taken off at the estimate's own split."""
        est = est.sudo()
        grand = est.grand_total or 0.0
        net = grand - (est.vat_amount or 0.0)
        pinned = est["approved_total"] if "approved_total" in est._fields else 0.0
        if pinned and grand > 0:
            return round(pinned * net / grand, 2)
        return round(net, 2)

    def _m31_capped_cost(self, extra: float = 0.0) -> float:
        """What the approved amount must cover: consumed parts that are not
        approved extra parts, plus labour (the P0 cap ignored labour)."""
        self.ensure_one()
        job = self.sudo()
        lines = job.part_line_ids.filtered(
            lambda ln: ln.reservation_state == "consumed" and not ln.dofa_approved
        )
        # A02 ERP audit M31-F14: the clocked labour (labour_cost, not the typed
        # figure) and the consumables count against the approved amount
        return (
            sum(lines.mapped("subtotal"))
            + (job.labour_cost or 0.0)
            + job._m31_consumables_cost()
            + (extra or 0.0)
        )

    def _m31_check_cost_within_estimate(self):
        """BRU-WSR-11: when the job's cost rises above what was approved, the
        job does not go on to QC until the estimate is revised and re-approved
        in M01, or the extra parts are approved through M63."""
        for rec in self:
            est, ceiling = rec._m31_cost_ceiling()
            if ceiling is None:
                continue
            cost = rec._m31_capped_cost()
            if cost > ceiling + 0.005:
                raise UserError(
                    "BRU-WSR-11: job %s now costs BDT %.2f (parts and labour) against %s "
                    "of BDT %.2f. The cost rose after approval: revise the estimate in M01 "
                    "and have it re-approved, or route the extra parts for approval, "
                    "before the job goes to QC."
                    % (
                        rec.name,
                        cost,
                        "approved estimate %s v%s" % (est.display_name, est.version)
                        if est
                        else "the zero-charge cap",
                        ceiling,
                    )
                )

    # --- writes ---
    def write(self, vals):
        if self and not self._fix_guard_open() and BOOKIN_FIELDS & set(vals):
            for rec in self:
                if rec.state == "draft":
                    continue
                changed = sorted(
                    n
                    for n in BOOKIN_FIELDS & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                )
                if changed:
                    raise UserError(
                        "%s cannot change on job %s: the book-in is the receipt the device "
                        "is handed back against."
                        % (", ".join(rec._fields[n].string or n for n in changed), rec.name)
                    )
        return super().write(vals)

    # --- book-in gate ---
    def _m31_check_bookin(self):
        self.ensure_one()
        missing = []
        if not (self.bookin_condition or "").strip():
            missing.append("the device's condition at book-in")
        if not ((self.bookin_accessories or "").strip() or self.bookin_no_accessories):
            missing.append("the accessories received (or 'received without accessories')")
        if missing:
            raise UserError(
                "Job %s cannot be booked in without %s." % (self.name, " and ".join(missing))
            )

    def action_intake(self):
        if not self.env.su:
            for rec in self:
                rec._m31_check_bookin()
        result = super().action_intake()
        for rec in self:
            rec._guarded().write(
                {"bookin_by_id": self.env.user.id, "bookin_at": fields.Datetime.now()}
            )
        return result

    # --- transitions ---
    def _transition(self, new_state: str):
        if new_state in ("qc_pending", "ready"):
            self._m31_check_cost_within_estimate()
        result = super()._transition(new_state)
        # A02 pass 2 M31-02: the hand-back is the RELEASE to the front desk
        # (the customer hand-over that closes the job is M01's own)
        if new_state == "released":
            for rec in self:
                # A02 audit B2: the hand-back to M01. Contract with the M01
                # consumer (stream S1): service_order_id (int, or False) and
                # the source record id.
                publish(
                    rec.env,
                    "workshop.job.delivered",
                    "fix.workshop.job",
                    rec.id,
                    {
                        "workshop_job_id": rec.id,
                        "job_name": rec.name,
                        "service_order_id": rec.order_id.id or False,
                        "service_order_ref": rec.order_id.name or "",
                        "workshop_id": rec.workshop_id.id,
                        "technician_id": rec.technician_id.id or False,
                        "repair_level": rec.repair_level,
                        "total_repair_cost": rec.total_repair_cost,
                        "completed_at": rec.completed_at.isoformat() if rec.completed_at else None,
                        "is_comeback": rec.is_comeback,
                    },
                )
        return result

    def action_cancel(self):
        # M01's cancellation cascade cancels every workshop job it finds that
        # is not delivered or cancelled. While M31 itself has M01 close the
        # order of a job it just closed as BER, that job is already closed.
        if self.env.context.get(BER_CLOSING_KEY):
            open_jobs = self.filtered(lambda j: j.state != "unrepairable")
            return super(FixWorkshopJobLifecycle, open_jobs).action_cancel() if open_jobs else True
        return super().action_cancel()

    # --- BER / scrap (A02 audit M31 steps 11-12, B1, B2) ---
    def _m31_check_ber_evidence(self):
        self.ensure_one()
        evidence = self.sudo().evidence_ids.filtered(
            lambda ev: ev.evidence_type in BER_EVIDENCE_TYPES
            and ev.document_id.res_model == self._name
            and ev.document_id.res_id == self.id
        )
        if not evidence:
            raise UserError(
                "A BER / scrap proposal on job %s needs its evidence: attach a pre-repair "
                "photo, a diagnostic report or a during-repair photo to the job first." % self.name
            )

    def _m31_check_ber_order_can_follow(self):
        self.ensure_one()
        order = self.sudo().order_id
        if not order or order.state in (
            "cancelled",
            *ORDER_BER_MARK_STATES,
            *ORDER_BER_CANCEL_STATES,
        ):
            return
        raise UserError(
            "Job %s cannot close as BER while its service order %s is %s: M01 marks an "
            "order unrepairable only from diagnosis or repair, or cancels it before "
            "repair." % (self.name, order.name, order.state)
        )

    def _m31_order_unrepairable(self):
        """B2: a BER reaches M01 through its public methods (the order stayed
        in_repair: 'unrepairable' was not in the sync map)."""
        self.ensure_one()
        order = self.order_id
        if not order or order.state == "cancelled":
            return
        reason = "Workshop job %s beyond economic repair: %s" % (self.name, self.ber_reason or "-")
        order = order.with_context(**{BER_CLOSING_KEY: True})
        if order.state in ORDER_BER_MARK_STATES:
            order.action_mark_unrepairable(reason=reason)
        elif order.state in ORDER_BER_CANCEL_STATES:
            order.action_cancel(reason_code="unrepairable", note=reason)
        else:
            self._m31_check_ber_order_can_follow()

    def _m31_close_ber(self):
        """The BER is approved (or needs no approval): close the job, and the
        order follows."""
        for rec in self:
            rec._transition("unrepairable")
        return True

    def action_request_approval(self, justification=None):
        # The job's one approval is its BER write-off, requested by Confirm BER.
        for rec in self:
            if not (rec.ber_proposed_at and rec.ber_confirmed_at):
                raise UserError(
                    "Job %s has no confirmed BER write-off to approve. Propose the BER, and "
                    "have a second technician confirm it: that routes it for approval." % rec.name
                )
        return super().action_request_approval(justification=justification)

    def _approval_on_rejected(self, comment):
        # a rejected write-off sends the BER back to the bench: it is
        # proposed and confirmed again, or the repair goes on
        for rec in self:
            rec.sudo()._guarded().write({"ber_confirmed_by_id": False, "ber_confirmed_at": False})
            rec.sudo().message_post(body="BER write-off rejected: %s" % (comment or "-"))
        return super()._approval_on_rejected(comment)

    # --- comeback / warranty-on-repair (A02 audit M31) ---
    def _m31_link_comeback(self):
        """rework_of_id was never written, so a comeback could not be raised.
        When M01 flags the order as a rework of an earlier order (same device
        and fault within the window, BRU-SRM-06), the job is linked to the
        last delivered workshop job of that earlier order."""
        for rec in self:
            order = rec.sudo().order_id
            original = order.rework_of_id if order and "rework_of_id" in order._fields else None
            if not original or rec.rework_of_id:
                continue
            prior = (
                self.env["fix.workshop.job"]
                .sudo()
                .search(
                    [("order_id", "=", original.id), ("state", "=", "delivered")],
                    order="completed_at desc, id desc",
                    limit=1,
                )
            )
            if not prior:
                continue
            rec._guarded().write({"rework_of_id": prior.id})
            rec.message_post(
                body="Comeback of %s (order %s, repaired by %s)."
                % (prior.name, original.name, prior.technician_id.name or "-")
            )
        return True

    # --- the certification waiver, routed (B1) ---
    def action_request_certification_waiver(self, reason=""):
        """Ask a Workshop Supervisor, through the M63 inbox, to waive the M22
        certification gate for this job's technician."""
        Request = self.env["fix.workshop.waiver.request"]
        reason = (reason or "").strip()
        for rec in self:
            rec._m31_require_group(
                ("cd_workshop.group_fix_workshop_user",), "Requesting a certification waiver"
            )
            if not reason:
                raise UserError("A certification waiver needs a written justification.")
            if not rec.technician_id:
                raise UserError(f"Job {rec.name} has no technician to waive certification for.")
            if rec.state not in ("draft", "intake", "diagnostic", "waiting_parts", "qc_failed"):
                raise UserError(
                    f"A certification waiver is granted before the repair starts (job {rec.name} "
                    f"is {rec.state})."
                )
            live = Request.sudo().search(
                [("job_id", "=", rec.id), ("state", "=", "pending")], limit=1
            )
            if live:
                raise UserError("Job %s already has a waiver awaiting a supervisor." % rec.name)
            req = Request._guarded().create(
                {
                    "job_id": rec.id,
                    "technician_id": rec.technician_id.id,
                    "reason": reason,
                    "requested_by_id": self.env.user.id,
                }
            )
            req.action_request_approval(justification=reason)
            rec.message_post(
                body="Certification waiver for %s requested by %s: %s"
                % (rec.technician_id.name, self.env.user.name, reason)
            )
        return True
