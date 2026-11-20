"""A02 ERP audit, pass 2 (20 Nov 2026) - M06 Data Services.

M06-01  the case's customer is frozen once custody is taken; a Data Lab
        Manager corrects it (with a reason, logged in the custody ledger,
        voiding a pending hand-over code); the hand-over goes only to the
        customer the accepted quotation was made to.
M06-02  a case is read by its assigned staff (and the intake queue of
        unassigned cases); lab managers read all. Every read is logged.
M06-03  custody starts only on sealed media, and every custody move
        (intake, transfer, secure-area move, return) is requested by one
        person and confirmed by the receiver: the ledger names both.
M06-04  (D15) a purge is proved by the lab's purge certificate of THIS
        case (its working copy / key destroyed), dated after the hand-over;
        a customer drive certificate never proves a purge, and a purge
        certificate never releases a device (M14 / M18).
M06-05  the wipe-certificate gate can be tied to the consuming record:
        verified after it took the device in, answering its request.
M06-06  media goes back, and a case closes, only once what it bills is
        paid, credited or waived.
M06-07  a waiver cancels the case's unpaid invoice; a credit approval
        issues it.
M06-09  (D16) the sanitisation technique matrix, checked when a
        certificate is recorded and verified; a destruction needs a witness
        and a photo; the certificate prints its standard.
M06-11  (D17) automatic purge is on; a case overdue for purge escalates
        to the lab managers.
M06-12  certified_by is stamped, the device of a decided certificate is
        frozen, and only the data lab records certificates.
"""

import logging
from datetime import timedelta

from odoo import SUPERUSER_ID, api, fields, models
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

from .fix_data_case import GROUP_LAB_MANAGER, GROUP_OPERATOR, _norm_serial, _require_role
from .fix_data_case_ext import _resolve_user

_logger = logging.getLogger(__name__)

CORRECTION_REASON_MIN = 10
READ_LOG_WINDOW_MINUTES = 10
ESCALATE_AFTER_DAYS_PARAM = "cd_data_case.purge_escalate_after_days"
ESCALATE_AFTER_DAYS_DEFAULT = 3
GROUP_QUALITY_MANAGER = "cd_device_registry.group_device_quality_manager"
SECURE_LOCATIONS = ("z4_lab", "cleanroom", "vault")
# the consuming record's wipe-request source (M06-05)
CONSUMER_SOURCES = {
    "fix.tradein.request": ("m14_refurbishment",),
    "fix.ewaste.collection": ("m18_recycling",),
}
STANDARDS = {
    "nist_800_88": "NIST SP 800-88 Rev. 1 - Clear",
    "nist_800_88_purge": "NIST SP 800-88 Rev. 1 - Purge",
    "cryptographic_erase": "NIST SP 800-88 Rev. 1 - Purge (Cryptographic Erase)",
    "physical_destruction": "NIST SP 800-88 Rev. 1 - Destroy (witnessed)",
}


def _internal_receiver(env, value, what):
    """The colleague named to receive a custody move: an active internal
    user, not the requester, holding the operator role."""
    if isinstance(value, list | tuple) and value:
        value = value[0]
    elif isinstance(value, dict):
        value = value.get("id")
    if isinstance(value, int):
        value = str(value)
    user = _resolve_user(env, value)
    if not user:
        raise UserError(
            "%s needs the colleague who receives it (their login): a custody move is "
            "confirmed by the receiver." % what
        )
    if user.id == env.uid:
        raise UserError("%s: the receiver confirms it, so it is another person." % what)
    if not user.active or user.share or not user.has_group(GROUP_OPERATOR):
        raise UserError("%s: %s is not an active data-lab colleague." % (what, user.name))
    return user


class FixDataCaseReadLog(models.Model):
    """M06-02: who opened which case, when (one row per user and case per
    ten minutes). Written by the server only; never edited or deleted."""

    _name = "fix.data.case.read.log"
    _description = "Data Recovery Case Read Log"
    _order = "read_at desc, id desc"

    case_id = fields.Many2one(
        "fix.data.recovery.case", required=True, index=True, ondelete="cascade", readonly=True
    )
    company_id = fields.Many2one(related="case_id.company_id", store=True, readonly=True)
    user_id = fields.Many2one("res.users", required=True, index=True, readonly=True)
    read_at = fields.Datetime(required=True, readonly=True, index=True)
    channel = fields.Char(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("Case read rows are written by the server only.")
        return super().create(vals_list)

    def write(self, vals):
        raise UserError("The case read log is append-only.")

    def unlink(self):
        raise UserError("The case read log is append-only.")


class FixDataRecoveryCaseA02R2(models.Model):
    _inherit = "fix.data.recovery.case"

    customer_id = fields.Many2one(tracking=True)
    # M06-03: the custody hand-off awaiting its receiver
    custody_request_kind = fields.Selection(
        [("intake", "Intake into Custody"), ("transfer", "Custody Transfer")],
        string="Custody Hand-off Awaiting",
        readonly=True,
        copy=False,
    )
    custody_request_by_id = fields.Many2one(
        "res.users", string="Hand-off Requested By", readonly=True, copy=False
    )
    custody_request_to_id = fields.Many2one(
        "res.users", string="Hand-off To (confirms)", readonly=True, copy=False
    )
    custody_request_at = fields.Datetime(readonly=True, copy=False)
    custody_request_note = fields.Char(readonly=True, copy=False)
    # M06-11
    purge_escalated_at = fields.Datetime(string="Purge Escalated At", readonly=True, copy=False)
    read_log_ids = fields.One2many("fix.data.case.read.log", "case_id", string="Reads")

    _A02R2_GUARDED = {
        "custody_request_kind",
        "custody_request_by_id",
        "custody_request_to_id",
        "custody_request_at",
        "custody_request_note",
        "purge_escalated_at",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._A02R2_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self[:1].state not in (False, "new"):
            locked.add("customer_id")
        return locked

    # ------------------------------------------------------------ M06-01
    def write(self, vals):
        if "customer_id" in vals and not self._fix_guard_open():
            for rec in self.filtered("id"):
                if rec.state != "new" and rec._fix_guard_differs(
                    "customer_id", vals["customer_id"], rec.customer_id
                ):
                    raise UserError(
                        "Case %s is in custody: its customer is whom the recovered data is "
                        "handed to. A Data Lab Manager corrects it (Correct Customer), with "
                        "the reason, on the custody ledger." % rec.name
                    )
        return super().write(vals)

    def action_correct_customer(self, partner_id=None, reason=None):
        """A Data Lab Manager corrects the case's customer after intake. The
        correction is on the custody ledger, voids a hand-over code sent to
        the old customer's recipient, and re-binds the live quotation."""
        _require_role(
            self.env, GROUP_LAB_MANAGER, "Data Recovery Lab Manager", "Correcting a case customer"
        )
        reason = (reason or "").strip()
        if len(reason) < CORRECTION_REASON_MIN:
            raise UserError(
                "Say why the customer is corrected (at least %d characters)."
                % CORRECTION_REASON_MIN
            )
        try:
            partner = self.env["res.partner"].sudo().browse(int(partner_id or 0)).exists()
        except (TypeError, ValueError):
            partner = self.env["res.partner"]
        if not partner:
            raise UserError("Choose the correct customer.")
        for rec in self:
            if rec.state in ("handover", "purged", "closed"):
                raise UserError(
                    "Case %s is %s: the data already went to its customer." % (rec.name, rec.state)
                )
            if not self.env.su and self.env.user in rec._z4_staff():
                raise UserError(
                    "Segregation of duties: %s works case %s, so another lab manager corrects "
                    "its customer." % (self.env.user.name, rec.name)
                )
            old = rec.customer_id
            if partner == old:
                raise UserError("Case %s is already %s's." % (rec.name, partner.display_name))
            vals = {
                "customer_id": partner.id,
                "handover_code_hash": False,
                "handover_code_expires_at": False,
            }
            recipient = rec.handover_recipient_id
            if recipient and recipient.commercial_partner_id != partner.commercial_partner_id:
                vals["handover_recipient_id"] = False
            rec._guarded().write(vals)
            live = rec.sudo().quote_ids.filtered(lambda q: q.state in ("draft", "sent", "accepted"))
            if live:
                live._guarded().write({"customer_id": partner.id})
            rec._custody_log(
                "customer_corrected",
                "customer corrected from %s to %s by %s: %s"
                % (old.display_name, partner.display_name, self.env.user.name, reason),
            )
            publish(
                self.env,
                "data_case.customer_corrected",
                "fix.data.recovery.case",
                rec.id,
                {"case": rec.name, "old_customer_id": old.id, "customer_id": partner.id},
            )
        return True

    def _handover_recipient_check(self):
        recipient = super()._handover_recipient_check()
        quote = self.sudo().quote_ids.filtered(lambda q: q.state == "accepted").sorted("id")[-1:]
        if quote:
            bound = quote.customer_id.commercial_partner_id
            if not bound or bound != self.customer_id.commercial_partner_id:
                raise UserError(
                    "Case %s: the accepted quotation %s was made to %s, not to the case's "
                    "customer %s. The data goes to the customer who accepted the price."
                    % (
                        self.name,
                        quote.name,
                        quote.customer_id.display_name or "-",
                        self.customer_id.display_name,
                    )
                )
        return recipient

    # ------------------------------------------------------------ M06-02
    def read(self, fields=None, load="_classic_read"):
        result = super().read(fields=fields, load=load)
        self._m06_log_reads("read")
        return result

    def _m06_log_reads(self, channel):
        if self.env.su or not self.ids or self.env.context.get("m06_no_read_log"):
            return
        uid, ids = self.env.uid, list(self.ids)

        def _write(env):
            Log = env["fix.data.case.read.log"].sudo()
            since = fields.Datetime.now() - timedelta(minutes=READ_LOG_WINDOW_MINUTES)
            recent = set(
                Log.search(
                    [("case_id", "in", ids), ("user_id", "=", uid), ("read_at", ">=", since)]
                )
                .mapped("case_id")
                .ids
            )
            now = fields.Datetime.now()
            rows = [
                {"case_id": cid, "user_id": uid, "read_at": now, "channel": channel}
                for cid in ids
                if cid not in recent
            ]
            if rows:
                Log.create(rows)

        if not self.env.cr.readonly:
            _write(self.env)
            return
        try:
            with self.env.registry.cursor() as cr:
                _write(api.Environment(cr, SUPERUSER_ID, {}))
        except Exception:  # a read is never refused because its log failed
            _logger.exception("M06 case read log failed for %s", ids)

    # ------------------------------------------------------------ M06-03
    def _custody_log(self, action, description, media_unit=None, witness_id=False):
        witness_id = witness_id or self.env.context.get("m06_custody_witness") or False
        return super()._custody_log(
            action, description, media_unit=media_unit, witness_id=witness_id
        )

    def _m06_confirming(self):
        return self.env.su or self.env.context.get("m06_custody_confirming")

    def action_take_custody(self, handler=None):
        """Custody starts on sealed media (M06-03). The person taking the
        device in names the lab colleague who receives it; custody is taken
        when that colleague confirms (action_confirm_custody)."""
        for rec in self if not self.env.su else self.browse():
            if not rec.media_unit_ids.filtered(
                lambda u: (u.seal_number or "").strip() and u.seal_state == "sealed"
            ):
                raise UserError(
                    "Case %s: register the customer's media in a sealed evidence bag (Sealed "
                    "Media, with its seal number) before custody is taken." % rec.name
                )
        if self._m06_confirming():
            return super().action_take_custody(handler=handler)
        _require_role(self.env, GROUP_OPERATOR, "Data Recovery Operator", "Taking custody")
        for rec in self:
            if rec.state != "new":
                raise UserError(
                    "Custody of case %s is taken once, at intake; the case is already '%s'."
                    % (rec.name, rec.state)
                )
        receiver = _internal_receiver(self.env, handler, "Taking custody")
        for rec in self:
            rec._m06_request_handoff("intake", receiver, "intake into custody")
        return True

    def action_log_custody_transfer(self, handler, role="Technician", location="Z4 Lab", notes=""):
        if self._m06_confirming():
            return super().action_log_custody_transfer(
                handler, role=role, location=location, notes=notes
            )
        _require_role(self.env, GROUP_OPERATOR, "Data Recovery Operator", "A custody transfer")
        receiver = _internal_receiver(self.env, handler, "A custody transfer")
        for rec in self:
            if rec.state not in ("custody", "recovering", "recovered", "handover"):
                raise UserError(
                    "A custody transfer is logged while the case is held (case %s is '%s')."
                    % (rec.name, rec.state)
                )
            note = "%s at %s%s" % (role or "", location or "", (" - %s" % notes) if notes else "")
            rec._m06_request_handoff("transfer", receiver, note)
        return True

    def _m06_request_handoff(self, kind, receiver, note):
        self.ensure_one()
        if self.custody_request_kind:
            raise UserError(
                "Case %s already has a hand-off awaiting %s."
                % (self.name, self.custody_request_to_id.name)  # fmt: skip
            )
        self._guarded().write(
            {
                "custody_request_kind": kind,
                "custody_request_by_id": self.env.uid,
                "custody_request_to_id": receiver.id,
                "custody_request_at": fields.Datetime.now(),
                "custody_request_note": note,
            }
        )
        self._custody_log(
            "custody_requested",
            "[%s requested] %s hands the case to %s: %s"
            % (kind, self.env.user.name, receiver.name, note),
        )
        self.sudo().activity_schedule(
            "mail.mail_activity_data_todo",
            summary="Confirm custody of case %s" % self.name,
            note="%s hands case %s to you (%s). Confirm when you hold it."
            % (self.env.user.name, self.name, note),
            user_id=receiver.id,
        )

    def action_confirm_custody(self):
        """The named receiver confirms the hand-off in their own session."""
        for rec in self:
            if not rec.custody_request_kind:
                raise UserError("Case %s has no custody hand-off to confirm." % rec.name)
            if self.env.user != rec.custody_request_to_id and not self.env.su:
                raise AccessError(
                    "Only %s, the named receiver, confirms the hand-off of case %s."
                    % (rec.custody_request_to_id.name, rec.name)
                )
            kind, requester = rec.custody_request_kind, rec.custody_request_by_id
            note = rec.custody_request_note or ""
            rec._guarded().write(
                {
                    "custody_request_kind": False,
                    "custody_request_by_id": False,
                    "custody_request_to_id": False,
                    "custody_request_at": False,
                    "custody_request_note": False,
                }
            )
            # the move is recorded as the receiver (sudo keeps the uid): he
            # need not otherwise see the case he is handed
            ctx = rec.sudo().with_context(
                m06_custody_confirming=True, m06_custody_witness=requester.id
            )
            who = "%s (from %s)" % (self.env.user.name, requester.name)
            if kind == "intake":
                ctx.action_take_custody(handler=who)
            else:
                ctx.action_log_custody_transfer(who, role="Received", location=note)
        return True

    def action_take_custody_me(self):
        """Form button: confirm the hand-off addressed to me (system code
        takes custody directly)."""
        if self.env.su and not self.filtered("custody_request_kind"):
            return self.action_take_custody(self.env.user.name)
        return self.action_confirm_custody()

    def action_transfer_me(self):
        if self.env.su and not self.filtered("custody_request_kind"):
            return self.action_log_custody_transfer(
                self.env.user.name, role="Technician", location="Z4 Lab"
            )
        return self.action_confirm_custody()

    # ------------------------------------------------------------ M06-04
    def _purge_certificate(self, certificate):
        self.ensure_one()
        if certificate or self.purge_certificate_id:
            return super()._purge_certificate(certificate)
        Cert = self.env["fix.data.wipe.certificate"]
        used = self.sudo().search([("purge_certificate_id", "!=", False)]).purge_certificate_id
        matches = (
            Cert.sudo().search(
                [
                    ("purpose", "=", "case_purge"),
                    ("case_id", "=", self.id),
                    ("sanitization_status", "=", "verified"),
                ]
            )
            - used
        )
        if len(matches) != 1:
            raise UserError(
                "Case %s: purge needs the wipe operator's verified purge certificate of this "
                "case (the lab's working copy and key destroyed)%s."
                % (self.name, ": several match, name the one" if matches else "")
            )
        return matches

    def _m06_purge_denial(self, cert) -> str:
        self.ensure_one()
        cert = cert.sudo()
        if not cert:
            return "no purge certificate is attached"
        # verified, its evidence unchanged since (the P0 checks) first
        denial = cert.with_context(m06_case_purge=True)._fix_certify_denial(cert.serial_number)
        if denial:
            return denial
        if cert.purpose != "case_purge":
            return (
                "certificate %s certifies a device's media, not this case's lab copy: a "
                "customer's drive certificate never proves a purge" % cert.name
            )
        if cert.case_id != self:
            return "purge certificate %s belongs to case %s" % (cert.name, cert.case_id.name or "-")
        if not (cert.lab_storage_ref or "").strip():
            return "purge certificate %s names no lab storage / key it destroyed" % cert.name
        handed = self.handover_at
        if handed and (
            (cert.certified_at or handed) < handed or (cert.verified_at or handed) < handed
        ):
            return (
                "purge certificate %s was recorded before the hand-over of %s: the lab copy "
                "is destroyed after the customer has the data" % (cert.name, handed)
            )
        return ""

    # ------------------------------------------------------------ M06-06
    def action_close(self):
        for rec in self:
            denial = rec._handover_settlement_denial()
            if denial:
                raise UserError("Case %s cannot close: %s." % (rec.name, denial))
        return super().action_close()

    # ------------------------------------------------------------ M06-07
    def action_waive_charge(self, note=None):
        result = super().action_waive_charge(note=note)
        for rec in self:
            invoice = rec._data_invoice()
            if not invoice:
                continue
            reason = "Charge waived on data case %s: %s" % (rec.name, note)
            if invoice.state in ("draft", "issued") and (invoice.amount_paid or 0.0) <= 0.005:
                invoice.sudo().action_cancel(reason=reason)
                rec.message_post(body="Invoice AR/%s cancelled: the charge is waived." % invoice.id)
            else:
                rec.message_post(
                    body="Invoice AR/%s is %s with payments on it: finance raises the credit "
                    "note for the waived charge." % (invoice.id, invoice.state)
                )
        return result

    def action_approve_credit(self, note=None):
        result = super().action_approve_credit(note=note)
        for rec in self:
            invoice = rec._data_invoice()
            if invoice and invoice.state == "draft":
                # the receivable goes on the customer's account now
                invoice.sudo().action_issue()
        return result

    # ------------------------------------------------------------ M06-11
    @api.model
    def cron_retention_purge(self):
        purged = super().cron_retention_purge()
        days = int(
            self.env["ir.config_parameter"].sudo().get_param(ESCALATE_AFTER_DAYS_PARAM)
            or ESCALATE_AFTER_DAYS_DEFAULT
        )
        cutoff = fields.Datetime.now() - timedelta(days=max(days, 0))
        overdue = self.sudo().search(
            [
                ("state", "=", "handover"),
                ("retention_flagged_at", "!=", False),
                ("retention_flagged_at", "<=", cutoff),
                ("purge_escalated_at", "=", False),
            ]
        )
        group = self.env.ref(GROUP_LAB_MANAGER, raise_if_not_found=False)
        managers = (
            group.sudo().user_ids.filtered(lambda u: u.active and not u.share) if group else []
        )
        for case in overdue:
            if case._retention_held():
                continue
            case._guarded().write({"purge_escalated_at": fields.Datetime.now()})
            note = (
                "Case %s is overdue for purge since %s (retention ended %s): record the lab's "
                "purge certificate and purge it." % (case.name, case.retention_flagged_at,
                                                    case.retention_until)
            )  # fmt: skip
            case.message_post(body=note)
            for user in managers:
                case.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Purge overdue: %s" % case.name,
                    note=note,
                    user_id=user.id,
                )
        return purged


class FixDataQuoteA02R2(models.Model):
    """M06-01: the customer a quotation was made to."""

    _inherit = "fix.data.quote"

    customer_id = fields.Many2one(
        "res.partner", string="Quoted To", readonly=True, copy=False, index=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"customer_id"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.pop("customer_id", None)
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"customer_id": rec.case_id.customer_id.id})
        return records

    def action_accept(self, acceptance_reference=None, signed_attachment_id=None):
        for quote in self:
            case_customer = quote.case_id.customer_id.commercial_partner_id
            if quote.customer_id.commercial_partner_id != case_customer:
                raise UserError(
                    "Quotation %s was made to %s, not to the case's customer %s: re-quote it."
                    % (quote.name, quote.customer_id.display_name, quote.case_id.customer_id.name)
                )
        return super().action_accept(
            acceptance_reference=acceptance_reference, signed_attachment_id=signed_attachment_id
        )


class FixDataMediaUnitA02R2(models.Model):
    """M06-03: every move of the customer's media is requested by one person
    and confirmed by the receiver; M06-06: it goes back only once paid."""

    _inherit = "fix.data.media.unit"

    pending_kind = fields.Selection(
        [("transfer", "Move"), ("return", "Return to Customer")],
        string="Move Awaiting Confirmation",
        readonly=True,
        copy=False,
    )
    pending_location = fields.Char(readonly=True, copy=False)
    pending_receiver_id = fields.Many2one(
        "res.users", string="Receiver (confirms)", readonly=True, copy=False
    )
    pending_requested_by_id = fields.Many2one(
        "res.users", string="Move Requested By", readonly=True, copy=False
    )
    pending_requested_at = fields.Datetime(readonly=True, copy=False)
    pending_recipient_id = fields.Many2one("res.partner", readonly=True, copy=False)

    _PENDING = (
        "pending_kind",
        "pending_location",
        "pending_receiver_id",
        "pending_requested_by_id",
        "pending_requested_at",
        "pending_recipient_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._PENDING)

    def _log(self, text, action="media_moved", witness_id=False):
        witness_id = witness_id or self.env.context.get("m06_custody_witness") or False
        return super()._log(text, action=action, witness_id=witness_id)

    def _m06_confirming(self):
        return self.env.su or self.env.context.get("m06_custody_confirming")

    def _m06_request(self, kind, receiver, location=False, recipient=False):
        self.ensure_one()
        if self.pending_kind:
            raise UserError(
                "Media %s already has a move awaiting %s."
                % (self.seal_number, self.pending_receiver_id.name)
            )
        self._guarded().write(
            {
                "pending_kind": kind,
                "pending_location": location or False,
                "pending_receiver_id": receiver.id,
                "pending_requested_by_id": self.env.uid,
                "pending_requested_at": fields.Datetime.now(),
                "pending_recipient_id": recipient.id if recipient else False,
            }
        )
        self._log(
            "%s requested by %s, to be confirmed by %s"
            % (kind if kind == "return" else "move to %s" % location, self.env.user.name,
               receiver.name),
            action="custody_requested",
        )  # fmt: skip
        self.sudo().activity_schedule(
            "mail.mail_activity_data_todo",
            summary="Confirm custody of media %s" % self.seal_number,
            user_id=receiver.id,
        )

    def action_transfer(self, location, handler=""):
        if self._m06_confirming():
            return super().action_transfer(location, handler=handler)
        _require_role(self.env, GROUP_OPERATOR, "Data Recovery Operator", "Moving media")
        if not location or location not in dict(type(self).location.selection):
            raise UserError("Pick a valid location.")
        if location in ("destroyed", "returned_to_customer"):
            raise UserError("Destruction and return have their own actions.")
        receiver = _internal_receiver(self.env, handler, "Moving media")
        for unit in self:
            unit._m06_request("transfer", receiver, location=location)
        return True

    def _m06_return_checks(self, recipient):
        self.ensure_one()
        case = self.case_id.sudo()
        if self.location in ("destroyed", "returned_to_customer"):
            raise UserError("Unit %s is %s" % (self.seal_number, self.location))
        denial = case._media_release_denial() or case._handover_settlement_denial()
        if denial:
            raise UserError("Media %s cannot be returned: %s." % (self.seal_number, denial))
        partner = self.env["res.partner"]
        if isinstance(recipient, models.BaseModel):
            partner = recipient
        elif recipient:
            try:
                partner = self.env["res.partner"].sudo().browse(int(recipient)).exists()
            except (TypeError, ValueError):
                partner = self.env["res.partner"]
        partner = partner or case.handover_recipient_id or case.customer_id
        if partner.commercial_partner_id != case.customer_id.commercial_partner_id:
            raise UserError(
                "%s is not the customer %s or one of its contacts."
                % (partner.display_name, case.customer_id.name)
            )
        return partner

    def action_return(self, handler="", recipient=None):
        if self._m06_confirming():
            for unit in self:
                unit._m06_return_checks(recipient)
            return super().action_return(handler=handler, recipient=recipient)
        _require_role(self.env, GROUP_OPERATOR, "Data Recovery Operator", "Returning media")
        receiver = _internal_receiver(self.env, handler, "Returning media")
        for unit in self:
            partner = unit._m06_return_checks(recipient)
            unit._m06_request("return", receiver, recipient=partner)
        return True

    def action_confirm_move(self):
        """The named receiver confirms the move (or the return to the
        customer) in their own session; the ledger names both people."""
        for unit in self:
            if not unit.pending_kind:
                raise UserError("Media %s has no move to confirm." % unit.seal_number)
            if self.env.user != unit.pending_receiver_id and not self.env.su:
                raise AccessError(
                    "Only %s, the named receiver, confirms the move of media %s."
                    % (unit.pending_receiver_id.name, unit.seal_number)
                )
            kind, location = unit.pending_kind, unit.pending_location
            requester, recipient = unit.pending_requested_by_id, unit.pending_recipient_id
            unit._guarded().write(dict.fromkeys(self._PENDING, False))
            ctx = unit.sudo().with_context(
                m06_custody_confirming=True, m06_custody_witness=requester.id
            )
            who = "%s (from %s)" % (self.env.user.name, requester.name)
            if kind == "transfer":
                ctx.action_transfer(location, handler=who)
            else:
                ctx.action_return(handler=who, recipient=recipient.id or None)
        return True


class FixDataSanitisationRule(models.Model):
    """M06-09 (D16): which sanitisation methods a media kind may be given,
    for its confidentiality and final disposition. The Quality Manager keeps
    the matrix; a certificate is checked against it when it is recorded and
    when it is verified."""

    _name = "fix.data.sanitisation.rule"
    _description = "Sanitisation Technique Matrix Rule"
    _order = "media_kind, confidentiality_level, disposition"

    media_kind = fields.Selection(
        [("hdd", "Magnetic (HDD)"), ("flash", "SSD / Flash / Phone")], required=True
    )
    confidentiality_level = fields.Selection(
        [("any", "Any"), ("low", "Low"), ("moderate", "Moderate"), ("high", "High")],
        required=True,
        default="any",
    )
    disposition = fields.Selection(
        [
            ("any", "Any"),
            ("internal_reuse", "Reuse Inside the Company"),
            ("resale", "Resale / Refurbishment"),
            ("recycling", "Recycling"),
            ("return_customer", "Return to the Customer"),
        ],
        required=True,
        default="any",
    )
    allow_clear = fields.Boolean(string="Clear (overwrite)")
    allow_purge = fields.Boolean(string="Purge", default=True)
    allow_crypto = fields.Boolean(string="Cryptographic Erase", default=True)
    allow_destroy = fields.Boolean(string="Physical Destruction", default=True)
    active = fields.Boolean(default=True)

    def _check_editor(self):
        if self.env.su or self.env.user.has_group(GROUP_QUALITY_MANAGER):
            return
        raise AccessError("The sanitisation matrix is kept by the Quality Manager.")

    @api.model_create_multi
    def create(self, vals_list):
        self._check_editor()
        return super().create(vals_list)

    def write(self, vals):
        self._check_editor()
        return super().write(vals)

    def unlink(self):
        self._check_editor()
        return super().unlink()

    def _allows(self, method):
        self.ensure_one()
        return {
            "nist_800_88": self.allow_clear,
            "nist_800_88_purge": self.allow_purge,
            "cryptographic_erase": self.allow_crypto,
            "physical_destruction": self.allow_destroy,
        }.get(method, False)

    @api.model
    def _m06_rule_for(self, media_kind, level, disposition):
        rules = self.sudo().search([("media_kind", "=", media_kind)])

        def score(rule):
            if rule.confidentiality_level not in ("any", level):
                return -1
            if rule.disposition not in ("any", disposition):
                return -1
            return (rule.confidentiality_level != "any") * 2 + (rule.disposition != "any")

        ranked = sorted((r for r in rules if score(r) >= 0), key=score, reverse=True)
        return ranked[0] if ranked else self.browse()


class FixDataWipeCertificateA02R2(models.Model):
    _inherit = "fix.data.wipe.certificate"

    purpose = fields.Selection(
        [
            ("media", "Media Sanitisation / Destruction"),
            ("case_purge", "Data-Case Purge (Lab Copy / Key Destruction)"),
        ],
        string="Certifies",
        required=True,
        default="media",
    )
    case_id = fields.Many2one(
        "fix.data.recovery.case", string="Purged Case", index=True, ondelete="restrict"
    )
    lab_storage_ref = fields.Char(
        string="Lab Working Copy / Key Destroyed",
        help="The lab volume, image or encryption key of the case that was destroyed.",
    )
    media_kind = fields.Selection(
        [("hdd", "Magnetic (HDD)"), ("flash", "SSD / Flash / Phone")], string="Media Kind"
    )
    destruction_witness_id = fields.Many2one(
        "res.users", string="Destruction Witness", readonly=True, copy=False
    )
    destruction_photo_attachment_id = fields.Many2one(
        "ir.attachment", string="Destruction Photo", ondelete="restrict"
    )
    standard_ref = fields.Char(string="Sanitisation Standard", compute="_compute_standard_ref")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "certified_by",
            "certified_at",
            "destruction_witness_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self[:1].sanitization_status not in (False, "pending_verification"):
            locked |= {"purpose", "case_id", "lab_storage_ref", "media_kind", "device_id"}
        return locked

    @api.depends("method")
    def _compute_standard_ref(self):
        for rec in self:
            rec.standard_ref = STANDARDS.get(rec.method, "")

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and not self.env.user.has_group(GROUP_OPERATOR):
            raise AccessError("A data-wipe certificate is recorded by the data lab.")
        for vals in vals_list:
            # M06-12: who certified, and when, are the recording user and the
            # server time, never typed
            for stamp in ("technician_id", "destruction_witness_id", "certified_at"):
                vals.pop(stamp, None)
            vals["certified_by"] = self.env.user.name
            vals["certified_at"] = fields.Datetime.now()
            if vals.get("purpose") == "case_purge":
                if not vals.get("case_id"):
                    raise UserError("A purge certificate names the case it purges.")
                ref = (vals.get("lab_storage_ref") or "").strip()
                if not ref:
                    raise UserError("Name the lab working copy / key destroyed.")
                vals["serial_number"] = ref
                vals.pop("device_id", None)
        records = super(FixDataWipeCertificateA02R2, self._guarded()).create(vals_list)
        records._m06_check_matrix()
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = {"device_id", "purpose", "case_id", "lab_storage_ref", "media_kind"} & set(
                vals
            )
            for rec in self:
                if rec.sanitization_status != "pending_verification" and any(
                    rec._fix_guard_differs(f, vals[f], rec[f]) for f in frozen
                ):
                    raise UserError(
                        "Certificate %s is decided: what it certifies is fixed." % rec.name
                    )
        result = super().write(vals)
        if {"method", "media_kind", "wipe_request_id"} & set(vals):
            self._m06_check_matrix()
        return result

    def _m06_check_matrix(self):
        """D16: the method must be allowed for the media kind, its
        confidentiality and its disposition (from the request)."""
        for cert in self:
            if cert.purpose != "media" or not cert.media_kind:
                continue
            req = cert.wipe_request_id
            level = req.confidentiality_level if req else "high"
            disposition = req.disposition if req else "resale"
            rule = self.env["fix.data.sanitisation.rule"]._m06_rule_for(
                cert.media_kind, level, disposition
            )
            if rule and not rule._allows(cert.method):
                raise UserError(
                    "The sanitisation matrix does not allow %s for %s media of %s "
                    "confidentiality going to %s."
                    % (
                        dict(self._fields["method"].selection).get(cert.method),
                        cert.media_kind,
                        level,
                        disposition,
                    )
                )

    def _evidence_gaps(self) -> list[str]:
        gaps = super()._evidence_gaps()
        if self.purpose == "case_purge":
            if not self.case_id:
                gaps.append("the case it purges")
            if not (self.lab_storage_ref or "").strip():
                gaps.append("the lab working copy / key destroyed")
        elif not self.media_kind and self.wipe_request_id.source in (
            "m14_refurbishment",
            "m18_recycling",
        ):
            # a device leaving for resale or recycling is judged by the matrix
            gaps.append("the media kind (HDD or SSD / flash) the matrix judges")
        if self.method == "physical_destruction" and not self.destruction_photo_attachment_id:
            gaps.append("the photo of the destroyed media")
        return gaps

    def action_witness_destruction(self):
        """D16: a second person witnessed the physical destruction."""
        _require_role(self.env, GROUP_OPERATOR, "Data Recovery Operator", "Witnessing")
        for cert in self:
            if cert.method != "physical_destruction":
                raise UserError("Certificate %s is not a physical destruction." % cert.name)
            if self.env.user in (cert.technician_id | cert.create_uid):
                raise UserError("The witness is not the person who destroyed the media.")
            cert._guarded().write({"destruction_witness_id": self.env.uid})
        return True

    def action_verify(self):
        for cert in self:
            if cert.method == "physical_destruction" and not cert.destruction_witness_id:
                raise UserError(
                    "Certificate %s: a physical destruction is verified only once a second "
                    "person witnessed it (Witness Destruction)." % cert.name
                )
        self._m06_check_matrix()
        return super().action_verify()

    def _fix_certify_denial(self, serial, consumer=None, since=None) -> str:
        """M06-04 / M06-05. Backwards compatible: ``consumer`` (the record
        that consumes the certificate, e.g. a trade-in) and ``since`` (when
        it took the device in) are optional; when given, the certificate
        must have been verified after that intake and answer that record's
        wipe request."""
        denial = super()._fix_certify_denial(serial)
        if denial or not self:
            return denial
        cert = self.sudo()
        if cert.purpose == "case_purge" and not self.env.context.get("m06_case_purge"):
            return (
                "certificate %s records a data-case purge (the lab's own copy): it certifies "
                "no device's media" % cert.name
            )
        if consumer:
            start = since or consumer.create_date
            if start and cert.verified_at and cert.verified_at < start:
                return (
                    "certificate %s was verified on %s, before %s took the device in (%s): it "
                    "certifies an earlier cycle" % (cert.name, cert.verified_at,
                                                    consumer.display_name, start)
                )  # fmt: skip
            req = cert.wipe_request_id
            refs = {_norm_serial(consumer.display_name)}
            if "name" in consumer._fields:
                refs.add(_norm_serial(consumer.name))
            if not req or _norm_serial(req.source_ref) not in refs:
                return "certificate %s answers no wipe request raised for %s" % (
                    cert.name,
                    consumer.display_name,
                )
            sources = CONSUMER_SOURCES.get(consumer._name)
            if sources and req.source not in sources:
                return "certificate %s answers a %s request, not %s" % (
                    cert.name,
                    req.source,
                    consumer._description,
                )
        return ""
