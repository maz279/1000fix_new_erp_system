# cd_cash_position — M50 consumer of the payroll disbursement events (A09
# workflow audit M56-17: payroll's events had no consumer in finance).
#
# Payroll releases its own bank files: a BEFTN batch (fix.beftn.batch) or a
# per-provider MFS wallet file (fix.mfs.disbursement), each released by a
# Payroll Disbursement Releaser who neither prepared nor approved the run
# (SOD-29). Treasury therefore NEVER releases or sends them again. It records
# each released file as one fix.payment.execution, already "sent", so that
#   * the cash position counts the outflow until the bank confirms it, and
#   * the bank's confirmation posts the cash leg through treasury's existing
#     execution GL path (_confirm_executed): Dr net salary payable / Cr bank.
#
# Payroll's own entries never touch a bank account (the accrual is Dr salary
# expense / Cr net payable / Cr TDS payable), so the bank is credited once,
# by treasury, and the net payable is cleared once.
#
#   payroll.beftn_submitted   period released: its BEFTN batch + MFS files
#   payroll.offcycle_paid     off-cycle released: its BEFTN batch
#   payroll.bonus_paid        festival bonus released: its BEFTN batch
#   payroll.beftn_settled     a batch / MFS file confirmed by the bank
#   payroll.beftn_returned    the bank / provider failed items of a file
#
# Idempotency key: (source_model, source_id) of the released FILE
# (fix.beftn.batch / fix.mfs.disbursement) - the unit the bank confirms. A
# payroll period paid partly by bank and partly by wallet is two or more files
# settled separately, so it is two or more executions; payroll_document names
# the period, off-cycle or bonus run behind each.
#
# Bank returns (payroll.beftn_returned, idempotent on return_id): before the
# file is confirmed, the failed items are netted out of its execution (the
# settlement also nets any imported return); after it was confirmed gross,
# the returned money is booked back through treasury's posting path (Dr bank
# / Cr net payable). A re-issue batch then posts its own cash leg. Only when a
# return was neither netted nor booked back does a re-issue post nothing -
# the original entry already credited the bank for those items. The bank is
# never credited twice.
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError

from .treasury_common import bank_account_of, post_treasury_move

PAYROLL_FILES = ("fix.beftn.batch", "fix.mfs.disbursement")
# The MFS wallet a provider file is paid from: system parameter
# cd_cash_position.payroll_mfs_journal_code.<provider> = bank journal code.
# Unset (today): the execution is recorded without a paying account and
# treasury picks it on the record before confirming (nothing is guessed).
MFS_JOURNAL_PARAM = "cd_cash_position.payroll_mfs_journal_code."
# Fields of a payroll-released execution only the consumer itself may change.
PAYROLL_PINNED = {
    "source_model",
    "source_id",
    "amount",
    "currency_id",
    "company_id",
    "method",
    "rail",
    "partner_bank_id",
    "debit_account_id",
    "source_posts_gl",
    "sent_at",
    "sent_by_id",
    "instruction_attachment_id",
    "payroll_released",
    "payroll_document",
    "payroll_netted_returns",
    "payroll_booked_returns",
    "payroll_return_move_ids",
}
CTX = "fix_payroll_treasury"


def _ids(text):
    return {i for i in (text or "").split(",") if i}


def _join(ids):
    return ",".join(sorted(ids, key=int))


class FixPaymentExecutionPayroll(models.Model):
    _inherit = "fix.payment.execution"

    payroll_released = fields.Boolean(
        string="Released by Payroll",
        readonly=True,
        copy=False,
        help="The bank file was released by payroll's own releaser (SOD-29). Treasury records "
        "the outflow and the bank's confirmation; it never releases the file again.",
    )
    payroll_document = fields.Char(
        string="Payroll Document",
        readonly=True,
        copy=False,
        help="The payroll period, off-cycle payment or bonus run behind this file (model,id).",
    )
    payroll_netted_returns = fields.Char(
        string="Bank Returns Netted",
        readonly=True,
        copy=False,
        help="Ids of the bank returns whose failed items were left out of this confirmation.",
    )
    payroll_booked_returns = fields.Char(
        string="Bank Returns Booked Back",
        readonly=True,
        copy=False,
        help="Ids of the bank returns that came back after this payment was confirmed and "
        "were booked back to the bank (Dr bank / Cr net payable).",
    )
    payroll_return_move_ids = fields.Many2many(
        "account.move",
        "fix_payment_execution_payroll_return_move_rel",
        "execution_id",
        "move_id",
        string="Bank Return Entries",
        readonly=True,
        copy=False,
    )

    # ------------------------------------------------------------------ guards

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get(CTX):
            for vals in vals_list:
                if vals.get("payroll_released") or vals.get("source_model") in PAYROLL_FILES:
                    raise UserError(
                        "A payroll bank file is recorded by treasury's payroll consumer only, "
                        "from the released file itself."
                    )
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get(CTX) and any(self.mapped("payroll_released")):
            pinned = sorted(PAYROLL_PINNED & set(vals))
            if pinned:
                raise UserError(
                    "Payroll released this payment to the bank: %s cannot be changed here."
                    % ", ".join(pinned)
                )
            if "state" in vals and vals["state"] != "executed":
                raise UserError(
                    "Payroll released this payment to the bank: it only moves to executed, on "
                    "the bank's confirmation (bank failures come back as a payroll bank return)."
                )
        return super().write(vals)

    def _refuse_payroll(self, what):
        released = self.filtered("payroll_released")
        if released:
            raise UserError(
                "%s was released to the bank by payroll's releaser (SOD-29): treasury %s."
                % (", ".join(released.mapped("name")), what)
            )

    def action_release(self):
        self._refuse_payroll("never releases or sends it again")
        return super().action_release()

    def action_mark_failed(self):
        self._refuse_payroll("does not reject it - failed items come back as a payroll bank return")
        return super().action_mark_failed()

    def action_retry(self):
        self._refuse_payroll("never re-queues it")
        return super().action_retry()

    def action_confirm_bank(self):
        """A payroll-released instruction confirms from the bank FILE's
        reference (the BEFTN return or the MFS provider's confirmation
        file), never from a typed reference with no import behind it: the
        disbursement/return document itself is the imported evidence."""
        payroll = self.filtered("payroll_released")
        for pay in payroll:
            if pay.state != "sent":
                raise UserError("%s is not awaiting the bank's confirmation." % pay.name)
            if not pay.journal_id or not pay.debit_account_id:
                raise UserError(
                    "%s: name the paying wallet and the net salary payable account first "
                    "(Confirm Bank completes a configured instruction)." % pay.name
                )
            pay._confirm_executed("payroll_return", reference=pay.bank_reference or pay.name)
        return super(FixPaymentExecutionPayroll, self - payroll).action_confirm_bank()

    def _confirm_executed(self, source, statement_line=None, reference=None, entry_date=None):
        if self.payroll_released and not self.source_posts_gl and not self.debit_account_id:
            raise UserError(
                "%s: the company's net salary payable account is not configured - the payroll "
                "payment is never posted to a guessed account." % self.name
            )
        return super()._confirm_executed(
            source, statement_line=statement_line, reference=reference, entry_date=entry_date
        )

    # ---------------------------------------------------------------- resolve

    def _payroll_net_payable(self, company):
        if "payroll_net_payable_account_id" not in company._fields:
            return self.env["account.account"]
        return company.sudo().payroll_net_payable_account_id

    def _payroll_bank_journal(self, company, account_no):
        """The company bank journal whose account is the file's originating
        account; empty when none or several match (never guessed)."""
        wanted = (account_no or "").replace(" ", "")
        if not wanted:
            return self.env["account.journal"]
        journals = (
            self.env["account.journal"]
            .sudo()
            .search([("type", "=", "bank"), ("company_id", "=", company.id)])
        )
        hits = journals.filtered(
            lambda j: (j.bank_account_id.acc_number or "").replace(" ", "") == wanted
        )
        return hits if len(hits) == 1 else self.env["account.journal"]

    def _payroll_mfs_journal(self, company, provider):
        code = (
            self.env["ir.config_parameter"].sudo().get_param(MFS_JOURNAL_PARAM + (provider or ""))
        )
        if not code:
            return self.env["account.journal"]
        return (
            self.env["account.journal"]
            .sudo()
            .search(
                [("type", "=", "bank"), ("company_id", "=", company.id), ("code", "=", code)],
                limit=1,
            )
        )

    @staticmethod
    def _payroll_batch_document(batch):
        for fname in ("period_id", "offcycle_id", "bonus_run_id", "reissue_return_id"):
            doc = batch[fname]
            if doc:
                return doc
        return batch

    def _payroll_existing(self, model, res_id):
        return self.search([("source_model", "=", model), ("source_id", "=", res_id)], limit=1)

    def _payroll_create(self, vals):
        return self.with_context(**{CTX: True}).create(vals)

    def _payroll_record_batch(self, batch_id):
        """One sent execution for a released BEFTN batch (idempotent)."""
        if "fix.beftn.batch" not in self.env:
            raise UserError("Payroll (cd_payroll_bd) is not installed - no BEFTN batch to record.")
        batch = self.env["fix.beftn.batch"].sudo().browse(int(batch_id or 0)).exists()
        if not batch:
            raise UserError("BEFTN batch %s does not exist." % batch_id)
        existing = self._payroll_existing(batch._name, batch.id)
        if existing:
            return existing
        if not batch.file_content:
            raise UserError(
                "BEFTN batch %s holds no released file - nothing left the bank." % batch.id
            )
        doc = self._payroll_batch_document(batch)
        company = batch.company_id
        ou = batch.operating_unit_id or (
            doc.operating_unit_id if "operating_unit_id" in doc._fields else False
        )
        return self._payroll_create(
            {
                "company_id": company.id,
                "operating_unit_id": ou.id if ou else False,
                "source_model": batch._name,
                "source_id": batch.id,
                "payee": "Payroll BEFTN %s" % (batch.file_name or batch.id),
                "currency_id": batch.currency_id.id,
                "amount": batch.total_amount,
                "method": "bank_transfer",
                "rail": "beftn",
                "journal_id": self._payroll_bank_journal(company, batch.company_account_no).id,
                "debit_account_id": self._payroll_net_payable(company).id,
                "value_date": batch.settlement_date,
                "state": "sent",
                "sent_at": batch.submitted_at,
                "sent_by_id": batch.released_by_id.id,
                "payroll_released": True,
                "payroll_document": "%s,%s" % (doc._name, doc.id),
            }
        )

    def _payroll_record_mfs(self, disb):
        """One sent execution for a released MFS provider file (idempotent)."""
        existing = self._payroll_existing(disb._name, disb.id)
        if existing:
            return existing
        if not disb.file_content:
            raise UserError("MFS disbursement %s holds no released file." % disb.name)
        company = disb.company_id
        ou = disb.operating_unit_id or disb.period_id.operating_unit_id
        return self._payroll_create(
            {
                "company_id": company.id,
                "operating_unit_id": ou.id if ou else False,
                "source_model": disb._name,
                "source_id": disb.id,
                "payee": "Payroll %s" % disb.name,
                "currency_id": (disb.currency_id or company.currency_id).id,
                "amount": disb.total_amount,
                "method": "mobile_fs",
                "journal_id": self._payroll_mfs_journal(company, disb.provider).id,
                "debit_account_id": self._payroll_net_payable(company).id,
                "value_date": fields.Datetime.to_datetime(disb.submitted_at).date()
                if disb.submitted_at
                else fields.Date.context_today(self),
                "state": "sent",
                "sent_at": disb.submitted_at,
                "sent_by_id": disb.released_by_id.id,
                "payroll_released": True,
                "payroll_document": "%s,%s" % (disb.period_id._name, disb.period_id.id),
            }
        )

    @staticmethod
    def _payroll_check_total(what, expected, recorded):
        if round(float(expected or 0.0), 2) != round(float(recorded or 0.0), 2):
            raise UserError(
                "%s: the event states %.2f but the released files total %.2f - nothing recorded."
                % (what, float(expected or 0.0), float(recorded or 0.0))
            )

    # -------------------------------------------------------------- consumers

    @api.model
    def consume_payroll_beftn_submitted(self, event):
        """payroll.beftn_submitted {company_id, amount, mfs_amount, batch_id,
        settlement}: the period's BEFTN batch and its MFS files, each one
        sent execution. The payload's totals must equal the released files."""
        payload = event.get("payload") or {}
        period_id = event.get("aggregate_id")
        made = self.browse()
        if payload.get("batch_id"):
            made |= self._payroll_record_batch(payload["batch_id"])
            self._payroll_check_total(
                "payroll.beftn_submitted (bank)", payload.get("amount"), made.amount
            )
        mfs = self.browse()
        if "fix.mfs.disbursement" in self.env:
            for disb in (
                self.env["fix.mfs.disbursement"]
                .sudo()
                .search([("period_id", "=", period_id)], order="id")
            ):
                mfs |= self._payroll_record_mfs(disb)
        self._payroll_check_total(
            "payroll.beftn_submitted (MFS)", payload.get("mfs_amount"), sum(mfs.mapped("amount"))
        )
        return made | mfs

    @api.model
    def consume_payroll_offcycle_paid(self, event):
        """payroll.offcycle_paid {employee_id, amount, payment_type, batch_id}."""
        payload = event.get("payload") or {}
        pay = self._payroll_record_batch(payload.get("batch_id"))
        self._payroll_check_total("payroll.offcycle_paid", payload.get("amount"), pay.amount)
        return pay

    @api.model
    def consume_payroll_bonus_paid(self, event):
        """payroll.bonus_paid {run, total, batch_id}. `total` is the gross bonus;
        the batch pays the net of any bonus TDS, which is what leaves the bank."""
        payload = event.get("payload") or {}
        return self._payroll_record_batch(payload.get("batch_id"))

    @api.model
    def consume_payroll_beftn_settled(self, event):
        """payroll.beftn_settled on a fix.beftn.batch or fix.mfs.disbursement:
        the bank confirmed the file. Executes its execution with the bank's
        confirmation reference (Dr net payable / Cr bank, treasury's path)."""
        model, res_id = event.get("aggregate"), event.get("aggregate_id")
        if model not in PAYROLL_FILES or model not in self.env:
            raise UserError("payroll.beftn_settled on %s: not a payroll bank file." % model)
        doc = self.env[model].sudo().browse(res_id).exists()
        if not doc:
            raise UserError("%s %s does not exist." % (model, res_id))
        if model == "fix.beftn.batch":
            pay = self._payroll_record_batch(doc.id)
            reference = doc.bank_confirmation_ref
        else:
            pay = self._payroll_record_mfs(doc)
            reference = doc.confirmation_ref
        if pay.state == "executed":
            return pay  # replay, or a bank statement line confirmed it first
        reference = (reference or "").strip()
        if not reference:
            raise UserError("%s %s settled without the bank's reference." % (model, res_id))
        upd = {"bank_reference": reference}
        if not pay.journal_id:
            journal = (
                self._payroll_bank_journal(doc.company_id, doc.company_account_no)
                if model == "fix.beftn.batch"
                else self._payroll_mfs_journal(doc.company_id, doc.provider)
            )
            if journal:
                upd["journal_id"] = journal.id
        if not pay.debit_account_id:
            payable = self._payroll_net_payable(doc.company_id)
            if payable:
                upd["debit_account_id"] = payable.id
        if model == "fix.beftn.batch":
            upd.update(self._payroll_return_netting(pay, doc))
        pay.with_context(**{CTX: True}).write(upd)
        if not pay.journal_id or not pay.debit_account_id:
            missing = [
                label
                for label, ok in (
                    ("the paying bank journal", pay.journal_id),
                    ("the net salary payable account", pay.debit_account_id),
                )
                if not ok
            ]
            pay.message_post(
                body="The bank confirmed %s (reference %s) but %s is not configured: nothing "
                "was posted. Set it and press Confirm Bank."
                % (doc.display_name, reference, " and ".join(missing))
            )
            return pay
        if pay.amount <= 0 and not pay.source_posts_gl:
            # every item failed: nothing left the bank, nothing is posted
            pay.with_context(**{CTX: True}).write({"source_posts_gl": True})
        # the return FILE is the imported bank evidence of the debit (F1's
        # payroll-return exception: relay-side, payroll-released only);
        # the entry date is the return's import date when it carries one
        entry_date = None
        if getattr(doc, "imported_on", None):
            entry_date = fields.Datetime.to_date(doc.imported_on)
        pay._confirm_executed("payroll_return", reference=reference, entry_date=entry_date)
        if pay.source_posts_gl and pay.payroll_released:
            note = (
                "No entry: the bank failed every item of this batch, nothing left the bank."
                if pay.amount <= 0
                else "No entry: the batch this re-issue repays was confirmed in full, so its "
                "entry already credited the bank for these items."
            )
            pay.with_context(**{CTX: True}).write({"gl_note": note})
        return pay

    def _payroll_return_netting(self, pay, batch):
        """Values that net the bank's failed items out of a batch confirmation,
        and keep a re-issue from crediting the bank twice."""
        vals = {}
        if "fix.beftn.return" not in self.env:
            return vals
        Return = self.env["fix.beftn.return"].sudo()
        returns = Return.search([("batch_id", "=", batch.id), ("state", "=", "imported")])
        failed = round(sum(returns.mapped("failed_amount")), 2)
        if failed:
            vals["amount"] = round(batch.total_amount - failed, 2)
            vals["payroll_netted_returns"] = _join(
                _ids(pay.payroll_netted_returns) | {str(i) for i in returns.ids}
            )
            if vals["amount"] <= 0:
                vals["source_posts_gl"] = True  # every item failed: nothing left the bank
            pay.message_post(
                body="Bank return(s) %s failed %.2f of this batch: the confirmation covers the "
                "%.2f the bank paid." % (", ".join(returns.mapped("name")), failed, vals["amount"])
            )
        ret = batch.reissue_return_id
        if ret:
            parent = self._payroll_existing("fix.beftn.batch", ret.batch_id.id)
            seen = _ids(parent.payroll_netted_returns) | _ids(parent.payroll_booked_returns)
            if parent.state == "executed" and str(ret.id) not in seen:
                vals["source_posts_gl"] = True
        return vals

    # ------------------------------------------------------------ bank returns

    @api.model
    def consume_payroll_beftn_returned(self, event):
        """payroll.beftn_returned {company_id, channel ('beftn'|'mfs'), batch_id,
        mfs_disbursement_id, return_id, failed_amount, failed_count}: the bank or
        provider failed items of a released file. Idempotent on return_id."""
        payload = event.get("payload") or {}
        return_id = str(payload.get("return_id") or "")
        if not return_id:
            raise UserError("payroll.beftn_returned names no return.")
        failed = round(float(payload.get("failed_amount") or 0.0), 2)
        if failed <= 0:
            raise UserError("payroll.beftn_returned %s returns no money." % return_id)
        if payload.get("channel") == "mfs":
            if "fix.mfs.disbursement" not in self.env:
                raise UserError("Payroll (cd_payroll_bd) is not installed.")
            doc = (
                self.env["fix.mfs.disbursement"]
                .sudo()
                .browse(int(payload.get("mfs_disbursement_id") or 0))
                .exists()
            )
            if not doc:
                raise UserError("payroll.beftn_returned %s names no MFS file." % return_id)
            pay = self._payroll_record_mfs(doc)
            if "fix.mfs.return" in self.env:
                ret = self.env["fix.mfs.return"].sudo().browse(int(return_id)).exists()
                if not ret or ret.disbursement_id != doc or ret.state != "imported":
                    raise UserError(
                        "payroll.beftn_returned %s: no imported return of MFS file %s."
                        % (return_id, doc.id)
                    )
                if round(ret.failed_amount, 2) != failed:
                    raise UserError(
                        "payroll.beftn_returned %s states %.2f failed; the return holds %.2f."
                        % (return_id, failed, ret.failed_amount)
                    )
        else:
            pay = self._payroll_record_batch(payload.get("batch_id"))
            doc = self.env["fix.beftn.batch"].sudo().browse(pay.source_id)
            if "fix.beftn.return" in self.env:
                ret = self.env["fix.beftn.return"].sudo().browse(int(return_id)).exists()
                if not ret or ret.batch_id != doc or ret.state != "imported":
                    raise UserError(
                        "payroll.beftn_returned %s: no imported return of BEFTN batch %s."
                        % (return_id, doc.id)
                    )
                if round(ret.failed_amount, 2) != failed:
                    raise UserError(
                        "payroll.beftn_returned %s states %.2f failed; the return holds %.2f."
                        % (return_id, failed, ret.failed_amount)
                    )
        if payload.get("company_id") and payload["company_id"] != pay.company_id.id:
            raise UserError("payroll.beftn_returned %s: company mismatch." % return_id)
        if return_id in _ids(pay.payroll_netted_returns) | _ids(pay.payroll_booked_returns):
            return pay  # replay, or the settlement already netted it
        if pay.state == "sent":
            if failed > pay.amount + 0.005:
                raise UserError(
                    "payroll.beftn_returned %s: %.2f failed exceeds the %.2f still awaiting "
                    "the bank." % (return_id, failed, pay.amount)
                )
            return pay._payroll_net_return(return_id, failed)
        if pay.state != "executed":
            raise UserError("%s is %s: a bank return cannot apply." % (pay.name, pay.state))
        return pay._payroll_book_return(return_id, failed, doc)

    def _payroll_net_return(self, return_id, failed):
        """Before confirmation: the failed items never leave the bank."""
        self.ensure_one()
        self.with_context(**{CTX: True}).write(
            {
                "amount": round(self.amount - failed, 2),
                "payroll_netted_returns": _join(_ids(self.payroll_netted_returns) | {return_id}),
            }
        )
        self.message_post(
            body="Bank return %s: %.2f failed - the payment now awaits %.2f."
            % (return_id, failed, self.amount)
        )
        return self

    def _payroll_book_return(self, return_id, failed, doc):
        """After confirmation: the returned money is back in the bank and the
        salary is owed again - Dr bank / Cr net payable, on treasury's path."""
        self.ensure_one()
        booked = _join(_ids(self.payroll_booked_returns) | {return_id})
        if doc._name == "fix.beftn.batch":
            # a re-issue that already settled on the gross confirmation (it
            # posted nothing for these items): booking now would leave the bank
            # credited short
            reissues = doc.search([("reissue_return_id", "=", int(return_id))])
            covered = self.search(
                [
                    ("source_model", "=", "fix.beftn.batch"),
                    ("source_id", "in", reissues.ids or [0]),
                    ("state", "=", "executed"),
                    ("source_posts_gl", "=", True),
                ]
            )
            if covered:
                self.with_context(**{CTX: True}).write({"payroll_booked_returns": booked})
                self.message_post(
                    body="Bank return %s: its re-issue %s already settled on this entry; "
                    "nothing booked." % (return_id, ", ".join(covered.mapped("name")))
                )
                return self
        if not self.debit_account_id:
            raise UserError(
                "%s: the net salary payable account is not configured - the return is not "
                "booked to a guessed account." % self.name
            )
        bank = bank_account_of(self.journal_id)
        move = post_treasury_move(
            self.env,
            self.company_id,
            fields.Date.context_today(self),
            "RETURN %s - %s (bank return %s)" % (self.name, self.payee, return_id),
            [
                (bank, "Returned by the bank: %s" % self.payee, failed, 0.0, self.partner_id),
                (
                    self.debit_account_id,
                    "Salary owed again (bank return %s)" % return_id,
                    0.0,
                    failed,
                    self.partner_id,
                ),
            ],
            source="treasury",
        )
        self.with_context(**{CTX: True}).write(
            {"payroll_booked_returns": booked, "payroll_return_move_ids": [(4, move.id)]}
        )
        self.message_post(
            body="Bank return %s: %.2f came back to the bank - booked in %s."
            % (return_id, failed, move.name)
        )
        return self
