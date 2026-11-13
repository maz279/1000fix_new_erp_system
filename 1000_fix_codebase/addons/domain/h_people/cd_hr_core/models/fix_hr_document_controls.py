# cd_hr_core — statutory documents, dependants, qualifications and positions
# (A09 workflow audit M21-10, M21-12, M21-13; BRU-HCM-04/05/10).
#
#   * a document is unverified until a second HR person verifies its file;
#     a generated (system-written, unsigned) document is never verified as
#     such - the signed scan is uploaded and verified instead;
#   * only the employee acknowledges their own document;
#   * the service book is append-only: an entry is never edited or deleted;
#     a correction is a new entry;
#   * nominee shares of an employee total at most 100% (BLA s.19 / s.131);
#   * education and reference checks are verified by a second person against
#     their evidence, never by default;
#   * a position carries its sanctioned headcount and never holds more.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_hr_controls_common import OFFICER

SERVICE_BOOK_FROZEN = (
    "employee_id",
    "doc_type",
    "reference",
    "issued_on",
    "file_data",
    "file_name",
    "notes",
    "company_id",
)


def _second_person(rec, what):
    """HR, and neither the record's creator nor its subject."""
    env = rec.env
    if env.su:
        return
    if not env.user.has_group(OFFICER):
        raise UserError("%s needs the HR Officer role." % what)
    if env.user == rec.sudo().create_uid:
        raise UserError("%s is done by someone other than who recorded it." % what)
    uploader = rec.sudo()["file_uploaded_by_id"] if "file_uploaded_by_id" in rec._fields else None
    if uploader and env.user == uploader:
        raise UserError("%s is done by someone other than who uploaded the file." % what)
    if env.user == rec.employee_id.sudo().user_id:
        raise UserError("You cannot %s on your own record." % what.lower())


class FixHrDocumentControls(models.Model):
    _name = "fix.hr.document"
    _inherit = ["fix.hr.document", "fix.guarded.mixin"]

    verified = fields.Boolean(default=False)
    generated = fields.Boolean(
        string="System Generated (unsigned)",
        readonly=True,
        help="Written by the system (Form 6/7 text, ID card). Upload the signed scan to verify.",
    )
    verified_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    verified_on = fields.Datetime(readonly=True, copy=False)
    acknowledged_on = fields.Datetime(readonly=True, copy=False)
    corrects_id = fields.Many2one(
        "fix.hr.document", string="Corrects Entry", help="A service-book correction is a new entry"
    )
    # The verifier must be neither the creator nor whoever uploaded the file:
    # officer B could upload a file onto A's row and verify it (M21 audit F8).
    file_uploaded_by_id = fields.Many2one(
        "res.users", string="File Uploaded By", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "verified",
            "verified_by_id",
            "verified_on",
            "acknowledged",
            "acknowledged_on",
            "generated",
            "file_uploaded_by_id",
        }

    def write(self, vals):
        if not self._fix_guard_open():
            # the system-generated (unsigned) entry takes its signed scan once:
            # freezing its file made it a dead end (never verifiable, M21 F8)
            books = self.filtered(
                lambda d: d.id
                and d.doc_type == "service_book"
                and not (d.generated and set(vals) <= {"file_data", "file_name"})
            )
            frozen = set(vals) & set(SERVICE_BOOK_FROZEN)
            if (
                books
                and frozen
                and any(d._fix_guard_differs(n, vals[n], d[n]) for d in books for n in frozen)
            ):
                raise UserError(
                    "A service book entry is append-only (BRU-HCM-05): add a correcting "
                    "entry instead of editing it."
                )
            if "file_data" in vals:
                # a new file is new evidence: it must be verified again
                for doc in self.filtered(
                    lambda d: d.id and (d.verified or d.generated or d.acknowledged)
                ):
                    # a new file is a new document: the employee acknowledges it again
                    doc._guarded().write(
                        {
                            "verified": False,
                            "verified_by_id": False,
                            "verified_on": False,
                            "generated": False,
                            "acknowledged": False,
                            "acknowledged_on": False,
                        }
                    )
        result = super().write(vals)
        if "file_data" in vals and vals.get("file_data"):
            self.filtered("id").sudo()._guarded().write({"file_uploaded_by_id": self.env.uid})
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.su:
            records.filtered("file_data").sudo()._guarded().write(
                {"file_uploaded_by_id": self.env.uid}
            )
        return records

    def unlink(self):
        if not self.env.su and self.filtered(lambda d: d.doc_type == "service_book"):
            raise UserError("A service book entry is never deleted (BRU-HCM-05).")
        return super().unlink()

    def action_verify(self):
        for rec in self:
            _second_person(rec, "Verifying a document")
            if not rec.file_data:
                raise UserError("Attach the scanned document before verifying it.")
            if rec.generated:
                raise UserError(
                    "%s was generated by the system and is unsigned: upload the signed scan "
                    "and verify that." % rec.name
                )
            rec._guarded().write(
                {
                    "verified": True,
                    "verified_by_id": self.env.uid,
                    "verified_on": fields.Datetime.now(),
                }
            )
            if rec.doc_type == "service_book":
                # BLR r.21: the service book is endorsed when its signed entry
                # is verified - this, not generating a draft, clears the
                # 15-day clock
                rec.employee_id.sudo()._guarded().write(
                    {"form7_endorsed_on": rec.issued_on or fields.Date.context_today(self)}
                )
        return True

    def action_unverify(self):
        for rec in self:
            _second_person(rec, "Withdrawing a verification")
            rec._guarded().write({"verified": False, "verified_by_id": False, "verified_on": False})
        return True

    def action_acknowledge(self):
        """The employee acknowledges their own document (never HR for them)."""
        for rec in self:
            if not self.env.su and rec.employee_id.sudo().user_id != self.env.user:
                raise UserError("Only %s acknowledges this document." % rec.employee_id.name)
            rec.sudo()._guarded().write(
                {"acknowledged": True, "acknowledged_on": fields.Datetime.now()}
            )
        return True


class FixHrDependantControls(models.Model):
    _inherit = "fix.hr.dependant"

    @api.constrains("nominee_pct", "is_nominee", "employee_id")
    def _check_nominee_total(self):
        for rec in self:
            if rec.nominee_pct and not rec.is_nominee:
                raise ValidationError("Only a nominee carries a share.")
            total = sum(
                self.sudo()
                .search([("employee_id", "=", rec.employee_id.id), ("is_nominee", "=", True)])
                .mapped("nominee_pct")
            )
            if total > 100.0 + 1e-6:
                raise ValidationError(
                    "Nominee shares of %s total %.2f%%: they may not exceed 100%% "
                    "(BLA s.19 / s.131)." % (rec.employee_id.name, total)
                )

    # The dependant's NID format is checked by its inverse, before the value is
    # routed to the resident store (fix_hr_identity_residency.py).


class FixHrEducationControls(models.Model):
    _name = "fix.hr.education"
    _inherit = ["fix.hr.education", "fix.guarded.mixin"]

    is_verified = fields.Selection(default="pending")
    verified_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"is_verified", "verified_by_id"}

    def _fix_set_verification(self, status, need_file=True):
        for rec in self:
            _second_person(rec, "Verifying a qualification")
            if need_file and not rec.certificate_file:
                raise UserError("Attach the certificate before verifying it.")
            rec._guarded().write({"is_verified": status, "verified_by_id": self.env.uid})
        return True

    def action_verify_online(self):
        return self._fix_set_verification("verified_online")

    def action_verify_physical(self):
        return self._fix_set_verification("verified_physical")

    def action_flag_discrepancy(self):
        return self._fix_set_verification("discrepancy", need_file=False)


class FixHrExperienceControls(models.Model):
    _name = "fix.hr.experience"
    _inherit = ["fix.hr.experience", "fix.guarded.mixin"]

    reference_status = fields.Selection(default=False)
    reference_checked_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"reference_status", "reference_checked_by_id"}

    def _fix_reference(self, status):
        for rec in self:
            _second_person(rec, "Recording a reference check")
            if status != "unreachable" and not (rec.experience_letter_file or rec.supervisor_phone):
                raise UserError(
                    "A reference check needs its evidence: the experience letter or the "
                    "supervisor's contact."
                )
            rec._guarded().write(
                {"reference_status": status, "reference_checked_by_id": self.env.uid}
            )
        return True

    def action_reference_positive(self):
        return self._fix_reference("verified_positive")

    def action_reference_neutral(self):
        return self._fix_reference("verified_neutral")

    def action_reference_negative(self):
        return self._fix_reference("negative_flag")

    def action_reference_unreachable(self):
        return self._fix_reference("unreachable")


class FixOrgPositionHeadcount(models.Model):
    _inherit = "fix.org.position"

    headcount = fields.Integer(
        string="Sanctioned Headcount",
        default=1,
        required=True,
        tracking=True,
        help="Seats this position may hold. No dual occupancy beyond it (BRU-HCM-10).",
    )
    filled_count = fields.Integer(compute="_compute_filled", string="Filled")
    vacant_count = fields.Integer(compute="_compute_filled", string="Vacant")

    _headcount_positive = models.Constraint(
        "CHECK (headcount >= 0)", "The sanctioned headcount cannot be negative"
    )

    def _compute_filled(self):
        for rec in self:
            filled = len(rec.sudo().employee_ids)
            rec.filled_count = filled
            rec.vacant_count = max((rec.headcount or 0) - filled, 0)

    @api.constrains("headcount")
    def _check_headcount_covers_holders(self):
        for rec in self:
            if len(rec.sudo().employee_ids) > rec.headcount:
                raise ValidationError(
                    "%s has %d holders: its headcount cannot drop to %d."
                    % (rec.name, len(rec.sudo().employee_ids), rec.headcount)
                )


class HrEmployeePositionSeat(models.Model):
    _inherit = "hr.employee"

    @api.constrains("position_id")
    def _check_position_seat(self):
        for position in self.mapped("position_id").sudo():
            holders = position.employee_ids
            if len(holders) > position.headcount:
                raise ValidationError(
                    "Position %s is full (%d sanctioned): no dual occupancy without a "
                    "sanctioned seat (BRU-HCM-10)." % (position.name, position.headcount)
                )
