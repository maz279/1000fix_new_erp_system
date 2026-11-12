# M01 counter settlements into the M04 cash drawer (A02 audit M04-P2, M04-4).
#
# A Service Order Cashier's counter settlement was recorded on the order and
# verified at once, "accountable in the cash shift", but nothing reached the
# shift: the drawer's expected closing never included order cash, so a
# shortage of exactly that money balanced. The settlement now posts to the
# branch's open shift. cd_front_desk depends on cd_service_order, so the hook
# lives here and the order module needs no knowledge of the drawer.
import re

from odoo import fields, models
from odoo.exceptions import UserError

# What happens to counter cash when the branch has no open shift. The settlement
# is refused, so cash is never taken outside a drawer: that is the default, and
# what an ABSENT parameter means (it was "0", and the parameter is shipped
# nowhere, so the control was off everywhere). An explicit "0" is a branch's
# own choice: the cash is recorded on the order's chatter and posts nothing.
ORDER_CASH_REQUIRES_SHIFT_PARAM = "cd_front_desk.order_cash_requires_open_shift"


def fd_cash_requires_shift(env) -> bool:
    raw = env["ir.config_parameter"].sudo().get_param(ORDER_CASH_REQUIRES_SHIFT_PARAM, "1")
    return str(raw).strip().lower() not in ("0", "false", "no", "off")


class FixServiceOrderDrawer(models.Model):
    _inherit = "fix.service.order"

    counter_shift_id = fields.Many2one(
        "fix.cash.shift",
        string="Counter Cash Shift",
        readonly=True,
        copy=False,
        index=True,
        help="The branch cash shift the counter settlement was posted to.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"counter_shift_id"}

    def _fix_record_settlement(self, amount_bdt, reference, source):
        result = super()._fix_record_settlement(amount_bdt, reference, source)
        if source == "counter":
            self._fd_post_counter_cash()
        return result

    def _fd_post_counter_cash(self):
        """Post the counter settlement to the branch's open cash shift."""
        self.ensure_one()
        Shift = self.env["fix.cash.shift"]
        shift = Shift._fd_open_shift_for(self.branch_id, self.company_id or self.env.company)
        amount = self.amount_settled_bdt or 0.0
        if not shift:
            if fd_cash_requires_shift(self.env):
                raise UserError(
                    "Branch %s has no open cash shift to take the counter payment for %s. "
                    "Open the cash shift first." % (self.branch_id.display_name, self.name)
                )
            self.message_post(
                body="Counter settlement of BDT %.2f taken with no open cash shift at %s: "
                "it is not in any drawer." % (amount, self.branch_id.display_name)
            )
            return False
        shift._post_cash_movement("cash_payments", amount, reference="Service order %s" % self.name)
        self._guarded().write({"counter_shift_id": shift.id})
        shift.message_post(
            body="Counter settlement %s: BDT %.2f for order %s."
            % (self.invoice_ref or "", amount, self.name)
        )
        return shift


# BRU-FRD-05 (M04 build, 13 Nov 2026): a device is handed over only after the
# collector's identity is verified. The M01 release already needs the
# customer's OTP, the recipient's name and the signed report; the OTP proves
# the CUSTOMER, so when somebody else collects (a relative, a driver, an
# office runner) nothing checked who was standing at the counter. A
# third-party collection now needs an identity document seen and recorded by
# the counter. Only the last four digits are kept: the full NID lives in the
# Bangladesh-resident store only (BRU-FRD-14).
COLLECTOR_ID_PARAM = "cd_front_desk.collector_id_required"


class FixServiceOrderCollector(models.Model):
    _inherit = "fix.service.order"

    collector_is_customer = fields.Boolean(
        string="Customer Collects in Person", default=True, copy=False
    )
    collector_relation = fields.Char(string="Collector's Relation to Customer", copy=False)
    collector_id_type = fields.Selection(
        [
            ("nid", "National ID"),
            ("passport", "Passport"),
            ("driving_licence", "Driving Licence"),
            ("birth_certificate", "Birth Certificate"),
            ("company_id", "Company ID Card + Authority Letter"),
        ],
        string="Collector's ID Document",
        copy=False,
    )
    collector_id_last4 = fields.Char(
        string="ID No. (last 4 digits)",
        size=4,
        copy=False,
        help="Only the last four digits are recorded (BRU-FRD-14).",
    )
    collector_authority_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Customer's Authority Letter",
        copy=False,
        help="The customer's written authority for a third party to collect.",
    )
    collector_id_verified_by = fields.Many2one(
        "res.users", string="Collector ID Checked By", readonly=True, copy=False
    )
    collector_id_verified_at = fields.Datetime(
        string="Collector ID Checked At", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "collector_id_verified_by",
            "collector_id_verified_at",
        }

    def write(self, vals):
        # a changed collector voids the check that was made on the previous one
        keys = {
            "collector_is_customer",
            "collector_id_type",
            "collector_id_last4",
            "recipient_name",
        }
        if keys & set(vals) and not self.env.context.get("fd_keep_collector_check"):
            changed = self.filtered("collector_id_verified_by").filtered(
                lambda o: any(o._fix_guard_differs(k, vals[k], o[k]) for k in keys & set(vals))
            )
            res = super().write(vals)
            if changed:
                changed._guarded().with_context(fd_keep_collector_check=True).write(
                    {"collector_id_verified_by": False, "collector_id_verified_at": False}
                )
            return res
        return super().write(vals)

    def action_verify_collector_id(self):
        """The counter has seen the collector's identity document."""
        for order in self:
            if order.state != "ready":
                raise UserError("Order %s is not Ready for collection." % order.name)
            if order.collector_is_customer:
                raise UserError(
                    "The customer collects order %s in person: the delivery OTP from their "
                    "phone is the identity check." % order.name
                )
            missing = []
            if not (order.recipient_name or "").strip():
                missing.append("the collector's name")
            if not (order.collector_relation or "").strip():
                missing.append("their relation to the customer")
            if not order.collector_id_type:
                missing.append("the ID document type")
            if not re.fullmatch(r"[0-9A-Za-z]{4}", (order.collector_id_last4 or "").strip()):
                missing.append("the last 4 characters of the ID number")
            if not order.collector_authority_attachment_id:
                missing.append("the customer's authority letter")
            if missing:
                raise UserError(
                    "Order %s: record %s before checking the collector's ID."
                    % (order.name, ", ".join(missing))
                )
            order._guarded().with_context(fd_keep_collector_check=True).write(
                {
                    "collector_id_verified_by": self.env.uid,
                    "collector_id_verified_at": fields.Datetime.now(),
                }
            )
            order.message_post(
                body="Collector %s (%s) identified by %s ending %s, checked by %s."
                % (
                    order.recipient_name,
                    order.collector_relation,
                    dict(order._fields["collector_id_type"].selection)[order.collector_id_type],
                    order.collector_id_last4,
                    self.env.user.name,
                )
            )
        return True

    def _check_delivery_evidence(self) -> None:
        super()._check_delivery_evidence()
        if self.env.su or self.collector_is_customer:
            return
        raw = self.env["ir.config_parameter"].sudo().get_param(COLLECTOR_ID_PARAM, "1")
        if str(raw).strip().lower() in ("0", "false", "no", "off"):
            return
        if not self.collector_id_verified_by:
            raise UserError(
                "Order %s is collected by someone other than the customer: check the "
                "collector's identity document first (Verify Collector ID, BRU-FRD-05)." % self.name
            )
