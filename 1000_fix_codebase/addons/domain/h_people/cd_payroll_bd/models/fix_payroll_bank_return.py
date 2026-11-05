# fix_payroll_bank_return — M56-4 / FR-PAY-048: the bank's per-item answer to
# a BEFTN batch, the re-issue of the items it failed, and the MFS wallet
# disbursement file (A09 round 2).
#
# BEFTN return file. No bank format exists in the repository (spec Q-02 is
# open), so this module defines the minimal one it accepts and the report
# lists it as a decision:
#
#     account,status[,reason]
#     1501203345001,paid
#     2702150098761,failed,Account closed
#
# a header row naming at least `account` and `status`; one row per credit of
# the batch; `status` is `paid` or `failed` (case-insensitive). Every credit
# of the batch must be answered exactly once and nothing else may appear: a
# partial, unknown or duplicated answer is refused rather than half-applied.
#
# Re-issue. A failed item is re-issued in a NEW BEFTN batch, released by a
# Payroll Disbursement Releaser who neither prepared nor approved the original
# payment (SOD-29), to the account the employee master holds at re-issue
# time. The master must hold a different account from the one the bank
# returned: the fix is an approved master change (cd_hr_core), never a typed
# account here.
#
# MFS. libs/py/payout_rail is the INT-007 seller payout rail: it names bKash
# and Nagad as `rail_preference` values, but it executes only against a
# configured bank payout endpoint (FIX_INT007_BANK_API_URL, refused without
# one: GV-009), knows no Rocket or Upay, and keeps its idempotency store in
# process memory. It is not a payroll MFS rail, so a wallet-paid salary is
# released as a per-provider MFS disbursement file (CSV, below) that treasury
# uploads to the provider's bulk-disbursement portal, and is settled against
# the provider's confirmation like a BEFTN batch.
#
#     provider,wallet,amount,reference,employee_ref,employee_name
import base64
import csv
import hashlib
import io

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_payroll_disbursement import (
    RELEASER,
    check_releaser,
    master_bank_details,
    master_payment_channel,
)

RETURN_STATUSES = ("paid", "failed")


def _batch_conflicts(batch):
    """Who prepared, calculated or approved the payment a batch carried."""
    batch = batch.sudo()
    if batch.reissue_of_id:
        return _batch_conflicts(batch.reissue_of_id)
    if batch.period_id:
        return batch.period_id._release_conflicts()
    doc = batch.offcycle_id or batch.bonus_run_id
    if doc:
        return (
            doc._approval_preparers()
            | doc.approved_by_id
            | doc.approval_request_id.sudo().requested_by_id
        )
    return batch.env["res.users"]


def batch_credits(batch):
    """[(employee, account, routing, amount)] the batch's file credited,
    rebuilt from the frozen document behind it (never re-read from a master)."""
    batch = batch.sudo()
    if batch.reissue_return_id:
        return [
            (ln.employee_id, ln.reissue_account_no, ln.reissue_routing_no, ln.amount)
            for ln in batch.reissue_return_id.line_ids
            if ln.reissue_batch_id == batch
        ]
    if batch.period_id:
        return [
            (s.employee_id, s.bank_account_no, s.routing_no, s.net)
            for s in batch.period_id.payslip_ids
            if s.net > 0 and s.payment_channel != "mfs"
        ]
    if batch.offcycle_id:
        oc = batch.offcycle_id
        return [(oc.employee_id, oc.bank_account_no, oc.routing_no, oc.amount)]
    if batch.bonus_run_id:
        return [
            (ln.employee_id, ln.bank_account_no, ln.routing_no, ln.net_amount)
            for ln in batch.bonus_run_id.line_ids
            if ln.net_amount > 0 and ln.payment_channel != "mfs"
        ]
    return []


class FixBeftnReturn(models.Model):
    _name = "fix.beftn.return"
    _description = "BEFTN Bank Return"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.payroll.state.lock"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", related="batch_id.company_id", store=True, index=True, readonly=True
    )
    operating_unit_id = fields.Many2one("operating.unit", readonly=True)
    batch_id = fields.Many2one(
        "fix.beftn.batch", required=True, index=True, ondelete="restrict", string="BEFTN Batch"
    )
    currency_id = fields.Many2one(related="batch_id.currency_id")
    return_file = fields.Binary(string="Bank Return File (CSV)", attachment=True)
    return_filename = fields.Char()
    file_digest = fields.Char(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("imported", "Imported")], default="draft", required=True
    )
    imported_by_id = fields.Many2one("res.users", readonly=True)
    imported_on = fields.Datetime(readonly=True)
    line_ids = fields.One2many("fix.beftn.return.line", "return_id", readonly=True)
    paid_count = fields.Integer(readonly=True)
    failed_count = fields.Integer(readonly=True)
    failed_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    reissue_batch_ids = fields.One2many(
        "fix.beftn.batch", "reissue_return_id", string="Re-issue Batches", readonly=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "operating_unit_id",
            "file_digest",
            "state",
            "imported_by_id",
            "imported_on",
            "line_ids",
            "paid_count",
            "failed_count",
            "failed_amount",
            "reissue_batch_ids",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {"batch_id", "return_file", "return_filename"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not (self.env.su or self.env.user.has_group(RELEASER)):
            raise AccessError("Only a Payroll Disbursement Releaser records a bank return.")
        records = super().create(vals_list)
        for rec in records:
            seq = (
                self.env["ir.sequence"].sudo().next_by_code("fix.beftn.return") or "BRT/%d" % rec.id
            )
            rec._guarded().write({"name": seq})
        return records

    @staticmethod
    def _parse(content, key="account"):
        """[(account or wallet, status, reason)] from a return CSV (format above)."""
        try:
            text = base64.b64decode(content).decode("utf-8-sig")
        except Exception as exc:
            raise UserError("The bank return file is not a readable UTF-8 CSV.") from exc
        reader = csv.DictReader(io.StringIO(text))
        header = {(h or "").strip().lower(): h for h in (reader.fieldnames or [])}
        if key not in header or "status" not in header:
            raise UserError(
                "The return file needs a header row with the columns %s and status "
                "(and optionally reason)." % key
            )
        rows = []
        for number, row in enumerate(reader, start=2):
            account = (row.get(header[key]) or "").strip()
            status = (row.get(header["status"]) or "").strip().lower()
            reason = (row.get(header["reason"]) or "").strip() if "reason" in header else ""
            if not account and not status:
                continue
            if status not in RETURN_STATUSES:
                raise UserError(
                    "Line %d of the bank return: status %r is neither paid nor failed."
                    % (number, status)
                )
            rows.append((account, status, reason))
        if not rows:
            raise UserError("The bank return file holds no item.")
        return rows

    def action_import(self):
        """Read the bank's per-item answer and mark each credit paid or failed."""
        if not (self.env.su or self.env.user.has_group(RELEASER)):
            raise AccessError("Only a Payroll Disbursement Releaser imports a bank return.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Bank return %s is already imported." % rec.name)
            if not rec.return_file:
                raise UserError("Attach the bank's return file before importing it.")
            batch = rec.batch_id.sudo()
            if not batch.file_content:
                raise UserError("BEFTN batch %s was never sent to the bank." % batch.display_name)
            done = rec.search([("batch_id", "=", batch.id), ("state", "=", "imported")])
            if done:
                raise UserError(
                    "BEFTN batch %s already has its bank return %s."
                    % (batch.file_name or batch.id, done[0].name)
                )
            credits = batch_credits(batch)
            by_account = {}
            for emp, account, routing, amount in credits:
                key = (account or "").strip()
                if key in by_account:
                    raise UserError(
                        "BEFTN batch %s credits account %s twice: a per-account return cannot "
                        "say which credit failed." % (batch.file_name or batch.id, key)
                    )
                by_account[key] = (emp, routing, amount)
            answers = rec._parse(rec.return_file)
            seen = set()
            for account, _status, _reason in answers:
                if account not in by_account:
                    raise UserError(
                        "The bank return names account %s, which BEFTN batch %s did not credit."
                        % (account, batch.file_name or batch.id)
                    )
                if account in seen:
                    raise UserError("The bank return answers account %s twice." % account)
                seen.add(account)
            missing = sorted(set(by_account) - seen)
            if missing:
                raise UserError(
                    "The bank return does not answer every credit of the batch: %s."
                    % ", ".join(missing)
                )
            Line = self.env["fix.beftn.return.line"].sudo()._guarded()
            lines = Line.create(
                [
                    {
                        "return_id": rec.id,
                        "company_id": batch.company_id.id,
                        "employee_id": by_account[account][0].id,
                        "account_no": account,
                        "routing_no": by_account[account][1],
                        "amount": by_account[account][2],
                        "status": status,
                        "reason": reason or False,
                    }
                    for account, status, reason in answers
                ]
            )
            failed = lines.filtered(lambda ln: ln.status == "failed")
            rec._guarded().write(
                {
                    "state": "imported",
                    "imported_by_id": self.env.user.id,
                    "imported_on": fields.Datetime.now(),
                    "file_digest": hashlib.sha256(base64.b64decode(rec.return_file)).hexdigest(),
                    "paid_count": len(lines) - len(failed),
                    "failed_count": len(failed),
                    "failed_amount": sum(failed.mapped("amount")),
                }
            )
            if failed:
                publish(
                    self.env,
                    "payroll.beftn_returned",
                    "fix.beftn.return",
                    rec.id,
                    {
                        "company_id": batch.company_id.id,
                        "channel": "beftn",
                        "batch_id": batch.id,
                        "mfs_disbursement_id": False,
                        "return_id": rec.id,
                        "failed_amount": float(round(sum(failed.mapped("amount")), 2)),
                        "failed_count": len(failed),
                    },
                )
            rec.message_post(
                body="Bank return imported: %d paid, %d failed (%.2f)."
                % (len(lines) - len(failed), len(failed), rec.failed_amount)
            )
        return True

    def _reissue_entries(self, batch):
        from .fix_payroll import beftn_entry

        self.ensure_one()
        return [
            beftn_entry(ln.employee_id, ln.reissue_account_no, ln.reissue_routing_no, ln.amount)
            for ln in self.sudo().line_ids
            if ln.reissue_batch_id == batch
        ]

    def action_reissue(self):
        """The failed items, in a new BEFTN batch, to the account the master
        holds now (it must differ from the one the bank returned)."""
        for rec in self:
            original = rec.batch_id.sudo()
            check_releaser(rec, "a BEFTN re-issue", lambda r: _batch_conflicts(r.batch_id))
            if rec.state != "imported":
                raise UserError("Import the bank return before re-issuing its failed items.")
            todo = rec.sudo().line_ids.filtered(
                lambda ln: ln.status == "failed" and not ln.reissue_batch_id
            )
            if not todo:
                raise UserError("Bank return %s has no failed item left to re-issue." % rec.name)
            problems = []
            pinned = {}
            for ln in todo:
                account, routing, _bank, problem = master_bank_details(ln.employee_id)
                account = (account or "").strip()
                if problem or not account or not routing:
                    problems.append(
                        "%s has no single registered salary account" % ln.employee_id.name
                    )
                elif account == (ln.account_no or "").strip():
                    problems.append(
                        "%s's master still holds the account the bank returned (%s): correct it "
                        "through an approved master change first" % (ln.employee_id.name, account)
                    )
                pinned[ln.id] = (account, routing)
            if problems:
                raise UserError("Nothing is re-issued: %s." % "; ".join(problems))
            submitted = fields.Datetime.now()
            from libs.py.payroll_engine import beftn_settlement_date

            batch = (
                self.env["fix.beftn.batch"]
                .sudo()
                ._guarded()
                .create(
                    {
                        "company_id": original.company_id.id,
                        "reissue_of_id": original.id,
                        "reissue_return_id": rec.id,
                        "submitted_at": submitted,
                        "settlement_date": beftn_settlement_date(submitted),
                        "employee_count": len(todo),
                        "total_amount": sum(todo.mapped("amount")),
                        "company_account_no": original.company_account_no,
                        "company_routing_no": original.company_routing_no,
                        "released_by_id": self.env.user.id,
                    }
                )
            )
            for ln in todo:
                account, routing = pinned[ln.id]
                ln._guarded().write(
                    {
                        "reissue_account_no": account,
                        "reissue_routing_no": routing,
                        "reissue_batch_id": batch.id,
                    }
                )
            batch.action_generate_beftn_file()
            rec.message_post(
                body="%d failed item(s) re-issued in BEFTN batch %s by %s."
                % (len(todo), batch.file_name, self.env.user.name)
            )
        return True


class FixBeftnReturnLine(models.Model):
    _name = "fix.beftn.return.line"
    _description = "BEFTN Bank Return Item"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "return_id, id"

    return_id = fields.Many2one("fix.beftn.return", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one("res.company", required=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    account_no = fields.Char(string="Account Credited")
    routing_no = fields.Char(string="Routing Credited")
    currency_id = fields.Many2one(related="return_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id")
    status = fields.Selection([("paid", "Paid"), ("failed", "Failed")], required=True)
    reason = fields.Char(string="Bank's Reason")
    reissue_account_no = fields.Char(string="Re-issued To Account")
    reissue_routing_no = fields.Char(string="Re-issued To Routing")
    reissue_batch_id = fields.Many2one("fix.beftn.batch", string="Re-issue Batch")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "return_id",
            "company_id",
            "operating_unit_id",
            "employee_id",
            "account_no",
            "routing_no",
            "amount",
            "status",
            "reason",
            "reissue_account_no",
            "reissue_routing_no",
            "reissue_batch_id",
        }


class FixMfsDisbursement(models.Model):
    """One provider's wallet credits of a paid payroll run (see the header)."""

    _name = "fix.mfs.disbursement"
    _description = "MFS Salary Disbursement File"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.payroll.state.lock"]
    _order = "id desc"

    name = fields.Char(readonly=True)
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", readonly=True)
    # the payment it carries: a monthly run, an off-cycle payment, a festival
    # bonus run, or the re-issue of an earlier file's failed wallets
    period_id = fields.Many2one(
        "fix.payroll.period", index=True, ondelete="restrict", readonly=True
    )
    offcycle_id = fields.Many2one(
        "fix.payroll.offcycle", index=True, ondelete="restrict", readonly=True
    )
    bonus_run_id = fields.Many2one(
        "fix.payroll.bonus.run", index=True, ondelete="restrict", readonly=True
    )
    reissue_of_id = fields.Many2one("fix.mfs.disbursement", readonly=True, ondelete="restrict")
    reissue_return_id = fields.Many2one("fix.mfs.return", readonly=True, ondelete="restrict")
    return_ids = fields.One2many("fix.mfs.return", "disbursement_id", string="Provider Returns")
    provider = fields.Selection(
        lambda self: self.env["hr.employee"]._fields["mfs_provider"].selection,
        required=True,
        readonly=True,
    )
    currency_id = fields.Many2one("res.currency", readonly=True)
    line_count = fields.Integer(readonly=True)
    total_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    file_content = fields.Text(string="Disbursement File (CSV)", readonly=True)
    file_name = fields.Char(readonly=True)
    file_digest = fields.Char(readonly=True)
    released_by_id = fields.Many2one("res.users", readonly=True)
    submitted_at = fields.Datetime(readonly=True)
    state = fields.Selection(
        [("submitted", "Submitted"), ("settled", "Settled")], default="submitted", required=True
    )
    confirmation_ref = fields.Char(string="Provider Confirmation Reference")
    confirmation_file = fields.Binary(string="Provider Confirmation File", attachment=True)
    confirmation_filename = fields.Char()
    settled_by_id = fields.Many2one("res.users", readonly=True)
    settled_on = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "company_id",
            "operating_unit_id",
            "period_id",
            "offcycle_id",
            "bonus_run_id",
            "reissue_of_id",
            "reissue_return_id",
            "return_ids",
            "provider",
            "currency_id",
            "line_count",
            "total_amount",
            "file_content",
            "file_name",
            "file_digest",
            "released_by_id",
            "submitted_at",
            "state",
            "settled_by_id",
            "settled_on",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state == "settled":
            locked |= {"confirmation_ref", "confirmation_file", "confirmation_filename"}
        return locked

    @api.model
    def _create_for_period(self, period, slips, submitted):
        """One file per provider for the wallet-paid slips of a released run."""
        rows = [(s.employee_id, s.mfs_provider, s.mfs_wallet, s.net) for s in slips]
        return self._create_rows(
            {"period_id": period.id}, rows, submitted, period.company_id, "SALARY %s" % period.name
        )

    @api.model
    def _create_rows(self, source, rows, submitted, company, reference):
        """One file per provider: rows are (employee, provider, wallet, amount).
        `source` names the document the money comes from."""
        by_provider = {}
        for row in rows:
            by_provider.setdefault(row[1], []).append(row)
        made = self.browse()
        label = (reference or "PAY").replace("/", "-").replace(" ", "_")
        for provider, group in sorted(by_provider.items(), key=lambda kv: kv[0] or ""):
            out = io.StringIO()
            writer = csv.writer(out, lineterminator="\n")
            writer.writerow(
                ["provider", "wallet", "amount", "reference", "employee_ref", "employee_name"]
            )
            for emp, _prov, wallet, amount in sorted(group, key=lambda r: r[0].id):
                writer.writerow(
                    [provider, wallet, "%.2f" % amount, reference, "EMP%05d" % emp.id, emp.name]
                )
            content = out.getvalue()
            rec = (
                self.sudo()
                ._guarded()
                .create(
                    {
                        **source,
                        "name": "MFS %s %s" % (provider, reference),
                        "company_id": company.id,
                        "provider": provider,
                        "currency_id": company.currency_id.id,
                        "line_count": len(group),
                        "total_amount": round(sum(r[3] for r in group), 2),
                        "file_content": content,
                        "released_by_id": self.env.user.id,
                        "submitted_at": submitted,
                    }
                )
            )
            rec._guarded().write(
                {
                    "file_name": "MFS_%s_%s_%d.csv" % (provider, label, rec.id),
                    "file_digest": hashlib.sha256(content.encode()).hexdigest(),
                }
            )
            made |= rec
        return made

    def _credits(self):
        """[(employee, wallet, amount)] this file credited, read back from the
        frozen file itself (its digest is pinned)."""
        self.ensure_one()
        rec = self.sudo()
        if hashlib.sha256((rec.file_content or "").encode()).hexdigest() != rec.file_digest:
            raise UserError("MFS file %s no longer matches its digest." % rec.name)
        rows = []
        for row in csv.DictReader(io.StringIO(rec.file_content or "")):
            emp_id = int((row.get("employee_ref") or "EMP0").replace("EMP", "") or 0)
            rows.append(
                (
                    self.env["hr.employee"].sudo().browse(emp_id),
                    (row.get("wallet") or "").strip(),
                    float(row.get("amount") or 0.0),
                )
            )
        return rows

    def _conflicts(self):
        """Who prepared, calculated or approved the payment this file carried."""
        rec = self.sudo()
        if rec.reissue_of_id:
            return rec.reissue_of_id._conflicts()
        if rec.period_id:
            return rec.period_id._release_conflicts()
        doc = rec.offcycle_id or rec.bonus_run_id
        if doc:
            return (
                doc._approval_preparers()
                | doc.approved_by_id
                | doc.approval_request_id.sudo().requested_by_id
            )
        return self.env["res.users"]

    def action_settle(self):
        """Settled from the provider's confirmation, by a releaser."""
        if not (self.env.su or self.env.user.has_group(RELEASER)):
            raise AccessError("Only a Payroll Disbursement Releaser records a provider settlement.")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("MFS disbursement %s is already settled." % rec.name)
            if not (rec.confirmation_ref or "").strip() or not rec.confirmation_file:
                raise UserError(
                    "Attach the provider's confirmation (reference and file) before settling %s."
                    % rec.name
                )
            rec._guarded().write(
                {
                    "state": "settled",
                    "settled_by_id": self.env.user.id,
                    "settled_on": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "payroll.beftn_settled",
                "fix.mfs.disbursement",
                rec.id,
                {"channel": "mfs", "provider": rec.provider, "amount": float(rec.total_amount)},
            )
        return True


class FixPayrollNomineeAccount(models.Model):
    """A death-in-service nominee's bank account (BLA s.19), for payroll only.

    fix.hr.dependant holds no bank or MFS field, so the account a nominee is
    paid into is recorded here by payroll with its evidence (a cheque leaf or
    the bank's letter) and verified by a SECOND payroll user before any
    payment to the nominee is requested (A09 round 2 decision)."""

    _name = "fix.payroll.nominee.account"
    _description = "Nominee Payout Account (death in service)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.payroll.state.lock"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    employee_id = fields.Many2one(
        "hr.employee", required=True, index=True, string="Deceased Employee"
    )
    dependant_id = fields.Many2one("fix.hr.dependant", string="Nominee Record")
    nominee_name = fields.Char(required=True)
    bank_name = fields.Char()
    bank_account_no = fields.Char(required=True)
    routing_no = fields.Char(required=True, string="Routing No (9 digits)")
    evidence_file = fields.Binary(string="Evidence (cheque leaf / bank letter)", attachment=True)
    evidence_filename = fields.Char()
    state = fields.Selection(
        [("draft", "Recorded"), ("verified", "Verified"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
    )
    recorded_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user, string="Recorded By"
    )
    verified_by_id = fields.Many2one("res.users", readonly=True, string="Verified By")
    verified_on = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "recorded_by_id",
            "verified_by_id",
            "verified_on",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {
                "employee_id",
                "dependant_id",
                "nominee_name",
                "bank_name",
                "bank_account_no",
                "routing_no",
                "evidence_file",
                "evidence_filename",
                "company_id",
            }
        return locked

    @api.constrains("bank_account_no", "routing_no")
    def _check_format(self):
        from libs.py.payroll_engine import validate_routing_number

        for rec in self:
            if not validate_routing_number((rec.routing_no or "").strip()):
                raise ValidationError("A BEFTN routing number is 9 digits.")
            acc = (rec.bank_account_no or "").strip()
            if not acc.isdigit() or len(acc) > 17:
                raise ValidationError("A bank account number is digits, at most 17.")

    def action_verify(self):
        if not (self.env.su or self.env.user.has_group("cd_payroll_bd.group_payroll_officer")):
            raise AccessError("Only payroll verifies a nominee account.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a recorded nominee account is verified.")
            if not rec.evidence_file:
                raise UserError("Attach the cheque leaf or the bank's letter before verifying.")
            if not self.env.su and self.env.user in (rec.recorded_by_id | rec.create_uid):
                raise UserError("A second payroll user verifies the nominee account it recorded.")
            rec._guarded().write(
                {
                    "state": "verified",
                    "verified_by_id": self.env.user.id,
                    "verified_on": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self):
        for rec in self:
            rec._guarded().write({"state": "cancelled"})
        return True

    @api.model
    def _verified_for(self, employee, dependant, name):
        domain = [("employee_id", "=", employee.id), ("state", "=", "verified")]
        if dependant:
            domain.append(("dependant_id", "=", dependant.id))
        else:
            domain.append(("nominee_name", "=ilike", (name or "").strip()))
        return self.sudo().search(domain, order="id desc", limit=1)


class FixMfsReturn(models.Model):
    """The provider's per-wallet answer to an MFS disbursement file, and the
    re-issue of the failed wallets (the BEFTN return pattern, by wallet):

        wallet,status[,reason]
        01712345678,failed,Wallet not KYC-verified
    """

    _name = "fix.mfs.return"
    _description = "MFS Provider Return"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.payroll.state.lock"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", related="disbursement_id.company_id", store=True, index=True
    )
    operating_unit_id = fields.Many2one("operating.unit", readonly=True)
    disbursement_id = fields.Many2one(
        "fix.mfs.disbursement", required=True, index=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(related="disbursement_id.currency_id")
    return_file = fields.Binary(string="Provider Return File (CSV)", attachment=True)
    return_filename = fields.Char()
    file_digest = fields.Char(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("imported", "Imported")], default="draft", required=True
    )
    imported_by_id = fields.Many2one("res.users", readonly=True)
    imported_on = fields.Datetime(readonly=True)
    line_ids = fields.One2many("fix.mfs.return.line", "return_id", readonly=True)
    paid_count = fields.Integer(readonly=True)
    failed_count = fields.Integer(readonly=True)
    failed_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    reissue_ids = fields.One2many(
        "fix.mfs.disbursement", "reissue_return_id", string="Re-issue Files", readonly=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "operating_unit_id",
            "file_digest",
            "state",
            "imported_by_id",
            "imported_on",
            "line_ids",
            "paid_count",
            "failed_count",
            "failed_amount",
            "reissue_ids",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {"disbursement_id", "return_file", "return_filename"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not (self.env.su or self.env.user.has_group(RELEASER)):
            raise AccessError("Only a Payroll Disbursement Releaser records a provider return.")
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"name": "MRT/%d" % rec.id})
        return records

    def action_import(self):
        if not (self.env.su or self.env.user.has_group(RELEASER)):
            raise AccessError("Only a Payroll Disbursement Releaser imports a provider return.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Provider return %s is already imported." % rec.name)
            if not rec.return_file:
                raise UserError("Attach the provider's return file before importing it.")
            disb = rec.disbursement_id.sudo()
            done = rec.search([("disbursement_id", "=", disb.id), ("state", "=", "imported")])
            if done:
                raise UserError(
                    "MFS file %s already has its return %s." % (disb.name, done[0].name)
                )
            by_wallet = {}
            for emp, wallet, amount in disb._credits():
                if wallet in by_wallet:
                    raise UserError(
                        "MFS file %s credits wallet %s twice: a per-wallet return cannot say "
                        "which credit failed." % (disb.name, wallet)
                    )
                by_wallet[wallet] = (emp, amount)
            answers = self.env["fix.beftn.return"]._parse(rec.return_file, key="wallet")
            seen = set()
            for wallet, _status, _reason in answers:
                if wallet not in by_wallet:
                    raise UserError(
                        "The provider return names wallet %s, which MFS file %s did not credit."
                        % (wallet, disb.name)
                    )
                if wallet in seen:
                    raise UserError("The provider return answers wallet %s twice." % wallet)
                seen.add(wallet)
            missing = sorted(set(by_wallet) - seen)
            if missing:
                raise UserError(
                    "The provider return does not answer every credit of the file: %s."
                    % ", ".join(missing)
                )
            lines = (
                self.env["fix.mfs.return.line"]
                .sudo()
                ._guarded()
                .create(
                    [
                        {
                            "return_id": rec.id,
                            "company_id": disb.company_id.id,
                            "employee_id": by_wallet[wallet][0].id,
                            "provider": disb.provider,
                            "wallet": wallet,
                            "amount": by_wallet[wallet][1],
                            "status": status,
                            "reason": reason or False,
                        }
                        for wallet, status, reason in answers
                    ]
                )
            )
            failed = lines.filtered(lambda ln: ln.status == "failed")
            rec._guarded().write(
                {
                    "state": "imported",
                    "imported_by_id": self.env.user.id,
                    "imported_on": fields.Datetime.now(),
                    "file_digest": hashlib.sha256(base64.b64decode(rec.return_file)).hexdigest(),
                    "paid_count": len(lines) - len(failed),
                    "failed_count": len(failed),
                    "failed_amount": sum(failed.mapped("amount")),
                }
            )
            if failed:
                publish(
                    self.env,
                    "payroll.beftn_returned",
                    "fix.mfs.return",
                    rec.id,
                    {
                        "company_id": disb.company_id.id,
                        "channel": "mfs",
                        "batch_id": False,
                        "mfs_disbursement_id": disb.id,
                        "return_id": rec.id,
                        "failed_amount": float(round(sum(failed.mapped("amount")), 2)),
                        "failed_count": len(failed),
                    },
                )
        return True

    def action_reissue(self):
        """The failed wallets, in a new MFS file, to the wallet the master
        holds now (it must differ from the one the provider returned)."""
        for rec in self:
            original = rec.disbursement_id.sudo()
            check_releaser(rec, "an MFS re-issue", lambda r: r.disbursement_id._conflicts())
            if rec.state != "imported":
                raise UserError("Import the provider return before re-issuing its failed items.")
            todo = rec.sudo().line_ids.filtered(
                lambda ln: ln.status == "failed" and not ln.reissue_id
            )
            if not todo:
                raise UserError(
                    "Provider return %s has no failed item left to re-issue." % rec.name
                )
            problems, rows = [], []
            for ln in todo:
                channel, provider, wallet = master_payment_channel(ln.employee_id)
                if channel != "mfs" or not wallet or not provider:
                    problems.append(
                        "%s's master holds no MFS wallet (pay a bank-paid employee off-cycle)"
                        % ln.employee_id.name
                    )
                elif wallet == ln.wallet:
                    problems.append(
                        "%s's master still holds the wallet the provider returned (%s): correct "
                        "it through an approved master change first" % (ln.employee_id.name, wallet)
                    )
                rows.append((ln, provider, wallet))
            if problems:
                raise UserError("Nothing is re-issued: %s." % "; ".join(problems))
            made = self.env["fix.mfs.disbursement"]._create_rows(
                {"reissue_of_id": original.id, "reissue_return_id": rec.id},
                [(ln.employee_id, provider, wallet, ln.amount) for ln, provider, wallet in rows],
                fields.Datetime.now(),
                original.company_id,
                "REISSUE %s" % rec.name,
            )
            for ln, provider, wallet in rows:
                ln._guarded().write(
                    {
                        "reissue_provider": provider,
                        "reissue_wallet": wallet,
                        "reissue_id": made.filtered(lambda d, p=provider: d.provider == p)[:1].id,
                    }
                )
        return True


class FixMfsReturnLine(models.Model):
    _name = "fix.mfs.return.line"
    _description = "MFS Provider Return Item"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "return_id, id"

    return_id = fields.Many2one("fix.mfs.return", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one("res.company", required=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    provider = fields.Selection(
        lambda self: self.env["hr.employee"]._fields["mfs_provider"].selection
    )
    wallet = fields.Char(string="Wallet Credited")
    currency_id = fields.Many2one(related="return_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id")
    status = fields.Selection([("paid", "Paid"), ("failed", "Failed")], required=True)
    reason = fields.Char(string="Provider's Reason")
    reissue_provider = fields.Selection(
        lambda self: self.env["hr.employee"]._fields["mfs_provider"].selection
    )
    reissue_wallet = fields.Char(string="Re-issued To Wallet")
    reissue_id = fields.Many2one("fix.mfs.disbursement", string="Re-issue File")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "return_id",
            "company_id",
            "operating_unit_id",
            "employee_id",
            "provider",
            "wallet",
            "amount",
            "status",
            "reason",
            "reissue_provider",
            "reissue_wallet",
            "reissue_id",
        }
