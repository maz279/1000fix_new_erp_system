# cd_hr_core — data clean-up findings for the business to decide (A09 report
# Update 3, "Before any deploy": existing data is not cleaned; the new
# constraints apply when each record is next written).
#
# READ-ONLY decision support. It lists, and changes nothing:
#   * employees with more than one active contract;
#   * overlapping live leave, overlapping attendance, and attendance punched on
#     a day of approved leave;
#   * exited employees still active (record, login or contract);
#   * the decorative flags left from before round 1: documents, qualifications,
#     references and clearance ticks marked verified / done with nobody's stamp
#     (or no file), and the dossier flags they hold up;
#   * NID / e-TIN / birth registration hashes held by more than one employee
#     (moved out of the clear columns as they were found).
# Which record survives, which leave is cancelled and who re-verifies what is
# a person's call; HR Manager runs it.
from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.tools import SQL

from .fix_hr_identity_residency import IDENTITY

LIVE_LEAVE = ("submitted", "approved")
DOSSIER_DOC_TYPES = {
    "doc_nid_verified": "nid_smart",
    "doc_tin_verified": "tin_cert",
    "doc_psr_verified": "tax_psr",
    "doc_appointment_signed": "appointment",
    "doc_nda_signed": "nda",
    "doc_service_book_scanned": "service_book",
    "doc_medical_fit_certified": "medical_fit",
    "doc_police_pcc_cleared": "police_pcc",
}


def _table_exists(cr, table):
    cr.execute("SELECT 1 FROM information_schema.tables WHERE table_name = %s", (table,))
    return bool(cr.fetchone())


class HrEmployeeCleanupReport(models.Model):
    _inherit = "hr.employee"

    @api.model
    def fix_data_cleanup_findings(self):
        """[{category, employee_id, employee, records, detail}], read-only."""
        if not (self.env.su or self.env.user.has_group("hr.group_hr_manager")):
            raise AccessError("The data clean-up findings are for the HR Manager.")
        self.env.flush_all()
        cr = self.env.cr
        rows = []
        names = {}

        def name_of(emp_id):
            if emp_id not in names:
                emp = self.sudo().with_context(active_test=False).browse(emp_id).exists()
                names[emp_id] = emp.name if emp else "#%s" % emp_id
            return names[emp_id]

        def add(category, emp_id, records, detail):
            rows.append(
                {
                    "category": category,
                    "employee_id": emp_id,
                    "employee": name_of(emp_id) if emp_id else "",
                    "records": records,
                    "detail": detail,
                }
            )

        # 1. more than one active contract
        cr.execute(
            """SELECT employee_id, string_agg(name, ', ' ORDER BY id), count(*)
                 FROM fix_employment_contract WHERE state = 'active'
                GROUP BY employee_id HAVING count(*) > 1 ORDER BY employee_id"""
        )
        for emp_id, contracts, count in cr.fetchall():
            add("Multiple active contracts", emp_id, contracts, "%d active contracts" % count)

        # 2. overlapping live leave
        cr.execute(
            """SELECT a.employee_id, a.id, a.date_from, a.date_to, a.state,
                      b.id, b.date_from, b.date_to, b.state
                 FROM fix_leave_request a
                 JOIN fix_leave_request b
                   ON b.employee_id = a.employee_id AND b.id > a.id
                  AND a.date_from <= b.date_to AND b.date_from <= a.date_to
                WHERE a.state IN %s AND b.state IN %s
                ORDER BY a.employee_id, a.id""",
            (LIVE_LEAVE, LIVE_LEAVE),
        )
        for emp_id, a_id, a_from, a_to, a_state, b_id, b_from, b_to, b_state in cr.fetchall():
            add(
                "Overlapping leave",
                emp_id,
                "leave %s / %s" % (a_id, b_id),
                "%s to %s (%s) overlaps %s to %s (%s)"
                % (a_from, a_to, a_state, b_from, b_to, b_state),
            )

        if _table_exists(cr, "fix_attendance_record"):
            # 3. overlapping attendance (the constraint's meaning: intervals
            #    that intersect, or two punches at the same check-in)
            cr.execute(
                """SELECT a.employee_id, a.id, a.check_in, a.check_out, b.id, b.check_in, b.check_out
                     FROM fix_attendance_record a
                     JOIN fix_attendance_record b
                       ON b.employee_id = a.employee_id AND b.id > a.id
                      AND b.check_in BETWEEN a.check_in - interval '2 days'
                                         AND a.check_in + interval '2 days'
                    WHERE (a.check_in < COALESCE(b.check_out, b.check_in)
                           AND b.check_in < COALESCE(a.check_out, a.check_in))
                       OR a.check_in = b.check_in
                    ORDER BY a.employee_id, a.id"""
            )
            for emp_id, a_id, a_in, a_out, b_id, b_in, b_out in cr.fetchall():
                add(
                    "Overlapping attendance",
                    emp_id,
                    "attendance %s / %s" % (a_id, b_id),
                    "%s-%s overlaps %s-%s" % (a_in, a_out or "open", b_in, b_out or "open"),
                )
            # 4. attendance punched on a day of approved leave
            cr.execute(
                """SELECT r.employee_id, r.id, r.check_in, l.id, l.date_from, l.date_to
                     FROM fix_attendance_record r
                     JOIN fix_leave_request l
                       ON l.employee_id = r.employee_id AND l.state = 'approved'
                      AND r.check_in::date BETWEEN l.date_from AND l.date_to
                    ORDER BY r.employee_id, r.id"""
            )
            for emp_id, r_id, r_in, l_id, l_from, l_to in cr.fetchall():
                add(
                    "Attendance on approved leave",
                    emp_id,
                    "attendance %s / leave %s" % (r_id, l_id),
                    "punched %s during leave %s to %s" % (r_in, l_from, l_to),
                )

        # 5. exited employees still active
        today = fields.Date.context_today(self)
        cr.execute(
            """SELECT e.id, e.active, e.left_date, u.active,
                      (SELECT string_agg(x.name, ', ') FROM fix_hr_exit x
                        WHERE x.employee_id = e.id AND x.state = 'settled'),
                      (SELECT string_agg(c.name, ', ') FROM fix_employment_contract c
                        WHERE c.employee_id = e.id AND c.state = 'active')
                 FROM hr_employee e
                 LEFT JOIN res_users u ON u.id = e.user_id
                WHERE (e.left_date IS NOT NULL AND e.left_date <= %s)
                   OR EXISTS (SELECT 1 FROM fix_hr_exit x
                               WHERE x.employee_id = e.id AND x.state = 'settled')
                ORDER BY e.id""",
            (today,),
        )
        for emp_id, emp_active, left, user_active, settled, contracts in cr.fetchall():
            still = []
            if emp_active and not left:
                still.append("record active with no left date")
            if user_active:
                still.append("Odoo login active")
            if contracts:
                still.append("active contract %s" % contracts)
            if still:
                add(
                    "Exited but still active",
                    emp_id,
                    settled or ("left %s" % left),
                    "; ".join(still),
                )

        # 6. decorative flags left from before round 1
        cr.execute(
            """SELECT d.employee_id, d.id, d.doc_type, d.verified_by_id IS NULL,
                      NOT EXISTS (SELECT 1 FROM ir_attachment a
                                   WHERE a.res_model = 'fix.hr.document' AND a.res_id = d.id
                                     AND a.res_field = 'file_data')
                 FROM fix_hr_document d
                WHERE d.verified IS TRUE
                ORDER BY d.employee_id, d.id"""
        )
        legacy_docs = {}
        for emp_id, doc_id, doc_type, nobody, no_file in cr.fetchall():
            if nobody or no_file:
                why = []
                if nobody:
                    why.append("verified by nobody")
                if no_file:
                    why.append("no scanned file")
                add(
                    "Decorative flag: document",
                    emp_id,
                    "document %s (%s)" % (doc_id, doc_type),
                    ", ".join(why),
                )
                legacy_docs.setdefault(emp_id, set()).add(doc_type)
        flags = [f for f in DOSSIER_DOC_TYPES if f in self._fields and self._fields[f].store]
        if flags and legacy_docs:
            for emp in self.sudo().with_context(active_test=False).browse(list(legacy_docs)):
                held = [f for f in flags if emp[f] and DOSSIER_DOC_TYPES[f] in legacy_docs[emp.id]]
                if held:
                    add(
                        "Decorative flag: dossier",
                        emp.id,
                        ", ".join(held),
                        "flag held up only by a document nobody verified",
                    )
        for table, column, stamp, label in (
            ("fix_hr_education", "is_verified", "verified_by_id", "qualification"),
            ("fix_hr_experience", "reference_status", "reference_checked_by_id", "reference"),
        ):
            col = SQL.identifier(column)
            cr.execute(
                SQL(
                    "SELECT employee_id, id, %s FROM %s WHERE %s IS NOT NULL AND %s <> 'pending' "
                    "AND %s IS NULL ORDER BY employee_id, id",
                    col,
                    SQL.identifier(table),
                    col,
                    col,
                    SQL.identifier(stamp),
                )
            )
            for emp_id, rec_id, status in cr.fetchall():
                add(
                    "Decorative flag: %s" % label,
                    emp_id,
                    "%s %s" % (label, rec_id),
                    "'%s' with nobody's stamp" % status,
                )
        cr.execute(
            """SELECT employee_id, id, name,
                      clearance_it AND clearance_it_by_id IS NULL,
                      clearance_finance AND clearance_finance_by_id IS NULL,
                      clearance_hr AND clearance_hr_by_id IS NULL,
                      clearance_assets AND clearance_assets_by_id IS NULL
                 FROM fix_hr_exit ORDER BY employee_id, id"""
        )
        for emp_id, _ex_id, ex_name, *ticks in cr.fetchall():
            unstamped = [
                label
                for label, bad in zip(("IT", "Finance", "HR", "Assets"), ticks, strict=True)
                if bad
            ]
            if unstamped:
                add(
                    "Decorative flag: clearance",
                    emp_id,
                    ex_name,
                    "ticked with no owner's stamp: %s" % ", ".join(unstamped),
                )

        # 7. one identity number on two employees (as moved from the clear columns)
        for name, spec in IDENTITY.items():
            if name == "nominee_nid":
                continue  # two employees may name the same nominee
            hash_field, label = spec[2], spec[6]
            cr.execute(
                SQL(
                    "SELECT string_agg(id::text, ', ' ORDER BY id), min(id) FROM hr_employee "
                    "WHERE %s IS NOT NULL GROUP BY %s HAVING count(*) > 1",
                    SQL.identifier(hash_field),
                    SQL.identifier(hash_field),
                )
            )
            for ids, first in cr.fetchall():
                add(
                    "Duplicate %s" % label,
                    first,
                    "employees %s" % ids,
                    "the same %s is recorded on each (%s)" % (label, name),
                )
        return rows
