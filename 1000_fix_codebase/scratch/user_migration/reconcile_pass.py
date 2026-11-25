# ruff: noqa: F821, UP031, S608, E501, S101, SIM105  (odoo-bin shell script: env/cr are injected at runtime)
# Reconciliation pass — cross-session duplicate cleanup (odoo shell, superuser).
# The parallel employee wave (2026-11-09 18:16-18:46) archived my linked
# 'Rayan Zaman Nabil' and created an unlinked duplicate; and the source file
# itself carries 3 shared-email rows (two different people, one email).
# Rule: first occurrence in staged_employees.csv keeps the email and the
# employee record; second occurrences are archived (printed as a WORKLIST
# line for HR adjudication - two people cannot share one work email).
import csv

STG = r"C:\software_project\software_project_14\1000fix-2\_migration\staged"


def read_staged():
    # read-only staging input
    with open(STG + "\\" + "staged_employees.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


env.cr.execute("SAVEPOINT recon_l6")
try:
    Emp = env["hr.employee"].sudo()
    staged = read_staged()

    first_code = {}
    for r in staged:
        em = r["work_email"]
        if em and em not in first_code:
            first_code[em] = r["employee_code"].strip().lower()

    rayan = Emp.search(
        [("work_email", "=", "rayan.zaman@1000fix.com"), ("employee_code", "=", "cs-4718")], limit=1
    )
    if rayan and not rayan.active:
        rayan.write({"active": True})
        print("reactivated linked original:", rayan.name, rayan.id)

    active = Emp.search([("active", "=", True), ("work_email", "!=", False)])
    to_archive = Emp.browse([])
    for e in active:
        keep_code = first_code.get(e.work_email)
        if keep_code is None:
            continue
        if (e.employee_code or "").strip().lower() != keep_code:
            to_archive |= e
    if to_archive:
        to_archive.write({"active": False})
    print("second-occurrence duplicates archived:", len(to_archive))
    for e in to_archive:
        keep_code = first_code.get(e.work_email)
        first_emp = Emp.search(
            [("work_email", "=", e.work_email), ("employee_code", "=", keep_code)], limit=1
        )
        print(
            "WORKLIST_DUP | %s | kept: %s (%s) | archived: %s (%s) | HR: assign distinct emails, then re-activate"
            % (
                e.work_email,
                first_emp.name if first_emp else "?",
                keep_code,
                e.name,
                e.employee_code,
            )
        )

    print("active employees:", Emp.search_count([("active", "=", True)]))
    print("linked (active):", Emp.search_count([("active", "=", True), ("user_id", "!=", False)]))
    env.cr.execute(
        "SELECT work_email, count(*) FROM hr_employee WHERE active AND work_email IS NOT NULL "
        "GROUP BY work_email HAVING count(*) > 1"
    )
    print("remaining active duplicate emails:", env.cr.fetchall())
    env.cr.execute("COMMIT")
    print("RECONCILE COMMIT OK")
except Exception as exc:
    env.cr.execute("ROLLBACK TO SAVEPOINT recon_l6")
    print("RECONCILE FAILED:", exc)
    raise
