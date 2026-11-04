# fix.workshop.part.line / fix.workshop — A02 P1/P2: extra parts and stock.
#
# A02 workflow audit (2026-11-03), M31 step 6 and B1:
#   - extra parts. The P0 cap refused any part beyond the approved estimate
#     outright, so the only way on was to re-quote the customer even when the
#     business chose to absorb the cost, and it was wrong three ways: it added
#     up EVERY approved estimate version (v2 was inflated by v1), it ignored
#     labour, and a zero-charge order (warranty, goodwill...) had no cap at all.
#     The ceiling is now the governing approved version against parts plus
#     labour (fix.workshop.job._m31_cost_ceiling), a zero-charge order is held
#     to a cap, and a part that does not fit is fitted only after a routed M63
#     approval of that part (DOFA tier on its cost, decided from the approver's
#     inbox) or a revised, re-approved estimate;
#   - stock. reservation_state was a label and consumption a text reference:
#     0 stock moves for BDT 75,000 of parts. Where the workshop names its stock
#     location, Reserve now reserves a stock.move from it and Consume validates
#     that move; without one the reference stays a stub unless
#     cd_workshop.stock_moves_required is on.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_workshop_job import BER_DOFA_THRESHOLDS

# A control switch: "1" refuses to reserve or consume a part at a workshop
# with no stock location. Default "0" (today: workshops have no Odoo stock
# location, and parts are tracked in M15's own ledger).
STOCK_REQUIRED_PARAM = "cd_workshop.stock_moves_required"
# An extra part the customer did not approve is a cost the business absorbs:
# the same write-off ladder as a BER (Tier 2 to BDT 10,000, Tier 3 to 50,000).
EXTRA_PART_DOFA_THRESHOLDS = BER_DOFA_THRESHOLDS
GROUP_TECHNICIAN = "cd_workshop.group_fix_workshop_user"


class FixWorkshopStock(models.Model):
    _inherit = "fix.workshop"

    stock_location_id = fields.Many2one(
        "stock.location",
        string="Parts Store Location",
        domain="[('usage', '=', 'internal')]",
        help="The stock location this workshop's parts are reserved and consumed from.",
    )
    consumption_location_id = fields.Many2one(
        "stock.location",
        string="Consumed Parts Destination",
        help="Where a consumed part goes (default: the Customers location, with the "
        "customer's device).",
    )

    def action_receive_service_order(self, order_ref=""):
        """A02 audit M31 step 1: receive a device from M01 into this workshop.
        The M31 side of the hand-off (the order's own button sits in M01)."""
        self.ensure_one()
        if not self.env.su and not self.env.user.has_group(GROUP_TECHNICIAN):
            raise UserError("Receiving a device into the workshop needs the Workshop role.")
        ref = str(order_ref or "").strip()
        if not ref:
            raise UserError("Give the service order reference to receive.")
        Order = self.env["fix.service.order"]
        order = Order.search([("name", "=", ref)], limit=1)
        if not order and ref.isdigit():
            order = Order.browse(int(ref)).exists()
        if not order:
            raise UserError("Service order %s was not found." % ref)
        job = order.action_create_workshop_job(workshop_id=self.id)
        return {"job_id": job.id, "job_name": job.name}

    def _m31_consumption_location(self):
        self.ensure_one()
        return self.consumption_location_id or self.env.ref(
            "stock.stock_location_customers", raise_if_not_found=False
        )


class FixWorkshopPartLineApproval(models.Model):
    _inherit = "fix.workshop.part.line"

    _approval_domain = "workshop_extra_parts"
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"stock_move_id"}

    stock_move_id = fields.Many2one(
        "stock.move", string="Stock Move", readonly=True, copy=False, ondelete="set null"
    )

    # --- the extra-part approval (DOFA on the part's cost) ---
    def _m31_overrun(self) -> float:
        """The part's cost when the approved amount does not cover it, else 0."""
        self.ensure_one()
        job = self.job_id.sudo()
        if not job or self.reservation_state == "released":
            return 0.0
        _est, ceiling = job._m31_cost_ceiling()
        if ceiling is None:
            return 0.0
        cost = self.subtotal or 0.0
        if self.reservation_state == "consumed":
            # fitted as an approved extra part, it stays outside the ceiling
            return cost if self.dofa_approved else 0.0
        return cost if job._m31_capped_cost(extra=cost) > ceiling + 0.005 else 0.0

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self._m31_overrun()

    def _dofa_thresholds(self):
        return EXTRA_PART_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "the extra part %s of BDT %.2f on %s, beyond its approved estimate" % (
            self.part_number or self.product_id.display_name or "?",
            self._dofa_amount(),
            self.job_id.name,
        )

    @api.depends("subtotal", "reservation_state", "job_id.labour_total")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.reservation_state not in ("draft", "reserved"):
                raise UserError(
                    "Part line %s is %s: an extra-part approval is asked before it is fitted."
                    % (rec.display_name, rec.reservation_state)
                )
            if rec.job_id.sudo().state in ("delivered", "unrepairable", "cancelled"):
                raise UserError("Job %s is closed." % rec.job_id.name)
        return super().action_request_approval(justification=justification)

    def action_dofa_approve(self):
        """The M63 apply method for an extra part: only from the approver's
        inbox. The approver holds the part's DOFA tier, is not the line's
        creator (fix.dofa.mixin) and not the repairing technician."""
        self._approval_assert_routed()
        for rec in self:
            if rec.reservation_state not in ("draft", "reserved"):
                raise UserError(
                    "Part line %s is already %s." % (rec.display_name, rec.reservation_state)
                )
            if rec.job_id._m31_actor_is_technician():
                raise UserError(
                    "Segregation of duties: the repairing technician cannot approve extra "
                    "parts on his own job."
                )
        # The approver usually holds a DOFA tier and no workshop role; the
        # DOFA rules check his tier group and the creator on users, so the
        # stamp is written as the system once the checks above have passed.
        super(FixWorkshopPartLineApproval, self.sudo()).action_dofa_approve()
        return True

    # --- stock (M15 / Odoo stock) ---
    def _m31_stock_required(self) -> bool:
        raw = self.env["ir.config_parameter"].sudo().get_param(STOCK_REQUIRED_PARAM)
        return str(raw or "").strip().lower() in ("1", "true", "yes")

    def _m31_stock_location(self):
        self.ensure_one()
        workshop = self.job_id.sudo().workshop_id
        location = workshop.stock_location_id
        if not location and self._m31_stock_required():
            raise UserError(
                "Workshop %s has no parts store location: name it on the workshop before "
                "parts are reserved or consumed (%s is on)." % (workshop.name, STOCK_REQUIRED_PARAM)
            )
        return location

    def _m31_reserve_move(self):
        """Create and reserve the stock move for this line (as the system:
        the technician has no stock rights). Refuses when a stocked part is
        not fully available at the workshop's location."""
        self.ensure_one()
        if self.stock_move_id and self.stock_move_id.state not in ("cancel", "done"):
            return self.stock_move_id
        location = self._m31_stock_location()
        product = self.product_id.sudo()
        if not location or product.type != "consu":
            return self.env["stock.move"]
        job = self.job_id.sudo()
        dest = job.workshop_id._m31_consumption_location()
        move = (
            self.env["stock.move"]
            .sudo()
            .create(
                {
                    "product_id": product.id,
                    "product_uom_qty": self.quantity,
                    "product_uom": product.uom_id.id,
                    "location_id": location.id,
                    "location_dest_id": dest.id,
                    "origin": "%s / %s" % (job.name, job.order_reference or "-"),
                    "company_id": location.company_id.id or job.company_id.id,
                }
            )
        )
        move._action_confirm()
        move._action_assign()
        if product.is_storable and move.state != "assigned":
            raise UserError(
                "Part %s cannot be reserved: %s of %s %s are available at %s."
                % (
                    product.display_name,
                    move.quantity,
                    self.quantity,
                    product.uom_id.name,
                    location.display_name,
                )
            )
        self._guarded().write({"stock_move_id": move.id})
        return move

    def action_reserve(self):
        """Reserve the part: a reserved stock move from the workshop store."""
        for rec in self:
            if rec.reservation_state != "draft":
                raise UserError("Only a draft part line can be reserved.")
            rec._m31_reserve_move()
        return super().action_reserve()

    def action_release_reservation(self):
        result = super().action_release_reservation()
        for rec in self.sudo():
            move = rec.stock_move_id
            if move and move.state not in ("done", "cancel"):
                move._action_cancel()
        return result

    def action_consume_part(self):
        """HS-05 / BRU-WSR-11: fit the part on the bench.

        Parts are consumed only while the job is in repair (which needs an
        approved order), and within the approved amount: the governing
        approved estimate against parts plus labour, or the zero-charge cap. A
        part that does not fit is fitted only once its extra-part approval is
        granted from the M63 inbox, or after the estimate is revised and
        re-approved in M01. The reserved stock move is validated."""
        for rec in self:
            if rec.reservation_state not in ("draft", "reserved"):
                raise UserError(
                    "Part line %s is already %s." % (rec.display_name, rec.reservation_state)
                )
            job = rec.job_id.sudo()
            if job.state != "in_repair":
                raise UserError(
                    "Parts are consumed on the bench while job %s is in repair (it is %s)."
                    % (job.name, job.state)
                )
            if rec._m31_overrun() > 0:
                if not rec.dofa_approved:
                    _est, ceiling = job._m31_cost_ceiling()
                    raise UserError(
                        "BRU-WSR-11: fitting %s (BDT %.2f) would take job %s to BDT %.2f "
                        "(parts and labour), above the approved amount of BDT %.2f. Revise "
                        "the estimate and have it re-approved in M01, or Request Approval "
                        "for this extra part, before fitting it."
                        % (
                            rec.part_number or rec.product_id.display_name,
                            rec.subtotal or 0.0,
                            job.name,
                            job._m31_capped_cost(extra=rec.subtotal),
                            ceiling,
                        )
                    )
                rec._dofa_assert_approved("The extra part")
            move = rec._m31_reserve_move()
            ref = False
            if move:
                move = move.sudo()
                move.quantity = rec.quantity
                move.picked = True
                move._action_done()
                if move.state != "done":
                    raise UserError(
                        "The stock move for part %s could not be validated." % rec.display_name
                    )
                ref = move.reference or "MOVE/%d" % move.id
            rec._guarded().write(
                {
                    "reservation_state": "consumed",
                    "consumption_ref": ref or rec.consumption_ref or f"M15-CONS-{rec.id}",
                    "consumed_at": fields.Datetime.now(),
                    "consumed_by_id": self.env.user.id,
                }
            )
        return True
