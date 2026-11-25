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
# How the order's money was tendered (A02 ERP audit, 19 Nov 2026). Only cash
# goes into a drawer; a wallet or card payment is matched by its TrxID. The
# keys are the field order's on-site methods and the counter's tenders; the
# finance bridge maps each to an M20 receipt method.
SETTLEMENT_TENDERS = [
    ("cash", "Cash"),
    ("bkash", "bKash"),
    ("nagad", "Nagad"),
    ("rocket", "Rocket"),
    ("upay", "Upay"),
    ("card", "Card (POS)"),
    ("sslcommerz", "SSLCOMMERZ Payment Link"),
    # A02 pass 2 (D1): cash the rider / courier collects on a delivery leg. It
    # never enters a drawer: the M20 receipt debits COD clearing, and the
    # rider's COD settlement (M50) relieves it.
    ("cod", "Cash on Delivery (rider / courier)"),
]
# A02 pass 2 (D1): COD is collected on a delivery leg, never at the counter
COD_TENDER = "cod"
COUNTER_TENDERS = SETTLEMENT_TENDERS  # backward-compatible name
# who, besides a Service Order Cashier, verifies a field collection at the drawer
FD_VERIFIER_GROUPS = ("cd_front_desk.group_fd_cashier", "cd_front_desk.group_fd_branch_manager")


def fd_settlement_tender(env) -> str:
    tender = env.context.get("fd_settlement_tender") or "cash"
    if tender not in dict(SETTLEMENT_TENDERS):
        raise UserError("Unknown tender '%s'." % tender)
    return tender


def fd_require_counter_tender(env, source):
    """X5-01 (A02 pass 2, P0): a counter settlement names its tender. The
    workspace sent none, and the missing tender defaulted to cash, so a bKash
    or card payment went into the drawer as cash (and its GL to drawer cash):
    the count then showed a shortage of exactly that money. Trusted service
    code (superuser) keeps the cash default it always had."""
    if source != "counter":
        return
    tender = env.context.get("fd_settlement_tender")
    if not tender and not env.su:
        raise UserError(
            "Say how the customer paid (cash, bKash, Nagad, Rocket, Upay or card): a counter "
            "payment is never assumed to be cash."
        )
    if tender == COD_TENDER:
        raise UserError(
            "Cash on delivery is collected by the rider on the delivery leg, not at the counter."
        )


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
        return super()._fix_guarded_fields() | {"counter_shift_id", "settlement_tender"}

    settlement_tender = fields.Selection(
        SETTLEMENT_TENDERS,
        string="Settlement Tender",
        readonly=True,
        copy=False,
        help="How the order was paid. Only cash goes into the drawer; a wallet or card "
        "payment is matched by its TrxID (A02 ERP audit: a bKash settlement used to land in "
        "the drawer as cash and show a false shortage at the count).",
    )

    def action_mark_settled(
        self, invoice_ref=None, amount_bdt=None, source="counter", reference=None, tender=None
    ):
        tender = tender or self.env.context.get("fd_settlement_tender")
        if tender and tender not in dict(SETTLEMENT_TENDERS):
            raise UserError("Unknown tender '%s'." % tender)
        # X5-01: no silent "cash" for a counter settlement (checked where the
        # settlement is recorded, _fix_record_settlement, for every caller)
        ctx = {"fd_settlement_tender": tender} if tender else {}
        return super(FixServiceOrderDrawer, self.with_context(**ctx)).action_mark_settled(
            invoice_ref=invoice_ref, amount_bdt=amount_bdt, source=source, reference=reference
        )

    def _fix_record_settlement(self, amount_bdt, reference, source):
        fd_require_counter_tender(self.env, source)
        # interface contract (20 Nov): a COD settlement is source "cod" and
        # its tender is always cod, whatever the caller's context says
        tender = COD_TENDER if source == COD_TENDER else fd_settlement_tender(self.env)
        if tender == COD_TENDER and source != COD_TENDER:
            raise UserError(
                "Cash on delivery is recorded as a COD settlement (source 'cod') on the "
                "delivery leg, not as a %s payment." % source
            )
        # a top-up adds to what was paid (a part payment or a settlement): the
        # drawer takes the difference
        before = (
            self.amount_settled_bdt or 0.0
            if self.payment_settlement_state in ("settled", "partial") and self.settlement_verified
            else 0.0
        )
        result = super()._fix_record_settlement(amount_bdt, reference, source)
        if source in ("counter", "field_collection", COD_TENDER) and not before:
            self._guarded().write({"settlement_tender": tender})
        if source == "counter":
            taken = round((self.amount_settled_bdt or 0.0) - before, 2)
            if tender == "cash":
                self._fd_post_counter_cash(taken)
            else:
                self._fd_post_counter_noncash()
        return result

    def action_verify_settlement(self):
        """A02 ERP audit: the drawer cashier who accepts field cash (M02 Accept
        Field Cash) or a branch manager verifies the collection as a Service
        Order Cashier would. The order's own segregation of duties still
        applies (never the recorder, never the order's technician): it reads
        the acting user, which sudo() keeps."""
        user = self.env.user
        if self.env.su or user.has_group("cd_service_order.group_so_cashier"):
            return super().action_verify_settlement()
        if not any(user.has_group(g) for g in FD_VERIFIER_GROUPS):
            return super().action_verify_settlement()  # refuses with its own message
        # sudo() below lifts record rules, so the scope is checked here first
        # (A02 ERP review, 20 Nov 2026: any front-desk cashier could verify any
        # branch's order, or field cash still in the technician's pocket)
        for order in self:
            order._fd_check_verifier_scope(user)
        return super(FixServiceOrderDrawer, self.sudo()).action_verify_settlement()

    def _fd_check_verifier_scope(self, user):
        """A front-desk verifier acts for the order's own branch, and verifies
        field CASH only once it is counted into a drawer (M02 Accept Field
        Cash, which verifies as part of the acceptance)."""
        self.ensure_one()
        order = self.sudo()
        unit = order.operating_unit_id or order.branch_id.operating_unit_id
        if unit and "operating_unit_ids" in user._fields and unit not in user.operating_unit_ids:
            raise UserError(
                "Order %s belongs to %s, which is not one of your operating units: its "
                "settlement is verified at its own branch." % (order.name, unit.display_name)
            )
        if (
            order.payment_settlement_state in ("settled", "partial")
            and not order.settlement_verified
            and order.settlement_source == "field_collection"
            and (order.settlement_tender or "cash") == "cash"
        ):
            FieldOrder = self.env.get("fix.field.order")
            in_drawer = FieldOrder is not None and FieldOrder.sudo().search_count(
                [("order_id", "=", order.id), ("cash_shift_id", "!=", False)]
            )
            if not in_drawer:
                raise UserError(
                    "The field cash of %s is not in a drawer yet: accept it into the cash shift "
                    "(Accept Field Cash), which verifies the settlement." % order.name
                )

    def _fd_post_counter_noncash(self):
        """A wallet / card payment at the counter: no drawer cash. The
        finance bridge raises its M20 receipt on the channel clearing."""
        self.ensure_one()
        return False

    def _fd_post_counter_cash(self, amount=None):
        """Post the counter settlement (or a top-up) to the branch's open cash shift."""
        self.ensure_one()
        Shift = self.env["fix.cash.shift"]
        shift = Shift._fd_open_shift_for(self.branch_id, self.company_id or self.env.company)
        amount = self.amount_settled_bdt or 0.0 if amount is None else amount
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
