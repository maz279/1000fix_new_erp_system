# ruff: noqa: F821, UP031, S608, E501, S101, SIM105  (odoo-bin shell script: env/cr are injected at runtime; table/column identifiers come from the staging CSVs and information_schema, not user input)
# Loader 2 — 506 real employees from staged_employees.csv (odoo shell, superuser).
# PII note: raw NID/TIN deliberately NOT written to hr.employee — the estate
# routes identity documents to fix.identity.document (cd_hr_core law);
# the staged CSV keeps them for the identity-document take-on follow-up.
import csv

STG = r"C:\software_project\software_project_14\1000fix-2\_migration\staged"


def read_csv(name):
    with open(STG + "\\" + name, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


env.cr.execute("SAVEPOINT emps_l2")
try:
    Emp = env["hr.employee"].sudo()
    Branch = env["fix.branch"].sudo()
    Dept = env["hr.department"].sudo()
    Pos = env["fix.org.position"].sudo()
    company = env["res.company"].sudo().search([("name", "=", "1000Fix Services Limited")], limit=1)

    br = {b.name: b for b in Branch.search([("active", "=", True)])}
    dp = {d.name: d for d in Dept.search([("active", "=", True), ("company_id", "=", company.id)])}
    ps = {p.name: p for p in Pos.search([])}

    rows = read_csv("staged_employees.csv")
    existing = {e.work_email: e for e in Emp.search([("work_email", "!=", False)]) if e.work_email}
    # BRU-HCM-10: a position has sanctioned seats — sanction the real title
    # counts from the file so the whole workforce fits (min 1)
    from collections import Counter

    title_counts = Counter(r["job_title"] for r in rows if r["job_title"])
    for title, n in title_counts.items():
        p = ps.get(title)
        if p and p.headcount < n:
            p.write({"headcount": n})
    created, skipped = 0, 0
    vals = []
    for r in rows:
        if not r["name"].strip():
            skipped += 1
            print("  skip blank-name row:", r["employee_code"] or "(no code)")
            continue
        if r["work_email"] and r["work_email"] in existing:
            skipped += 1
            continue
        v = {
            "name": r["name"],
            "work_email": r["work_email"] or False,
            "employee_code": r["employee_code"] or False,
            "employment_type": r["employment_type"] or False,
            "blood_group": r["blood_group"] or False,
            "company_id": company.id,
            "legacy_branch_name": r["legacy_branch"] or False,
            "legacy_reference": r["legacy_branch"] or False,
        }
        b = br.get(r["new_branch"])
        if b:
            v["branch_id"] = b.id
            v["operating_unit_id"] = b.operating_unit_id.id
        d = dp.get(r["department"])
        if d:
            v["department_id"] = d.id
        p = ps.get(r["job_title"])
        if p:
            v["position_id"] = p.id
        vals.append(v)
    for i in range(0, len(vals), 100):
        Emp.create(vals[i : i + 100])
        created += len(vals[i : i + 100])
    print(
        "employees created:",
        created,
        "| skipped (email existed):",
        skipped,
        "| total:",
        Emp.search_count([]),
    )

    # pass 2: managers by employee code
    by_code = {e.employee_code: e for e in Emp.search([("employee_code", "!=", False)])}
    linked = 0
    for r in rows:
        mc = r["manager_code"]
        if not mc:
            continue
        mgr = by_code.get(mc)
        sub_email = r["work_email"]
        if not mgr or not sub_email:
            continue
        sub = Emp.search([("work_email", "=", sub_email)], limit=1)
        if sub and not sub.parent_id:
            sub.write({"parent_id": mgr.id})
            linked += 1
    print("manager links set:", linked)
    env.cr.execute("COMMIT")
    print("EMPLOYEES COMMIT OK")
except Exception as exc:
    env.cr.execute("ROLLBACK TO SAVEPOINT emps_l2")
    print("EMPLOYEES FAILED:", exc)
    raise
